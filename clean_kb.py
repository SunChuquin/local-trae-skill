#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库清理脚本（停任务 + 清理向量化数据）
==========================================
复用"停止任务 + 清理数据"的整套机制，避免每次重新摸清存储与清理流程。

两种模式（通过 --all 区分）：

默认模式（不传 --all）——只清理"未完成"的文档：
    1. 停止后端进程（内存态任务队列随之清空，正在向量化的任务被中断）
    2. 找出 documents.json 中"未完成"的文档：
       - 完整向量化 = vector_count >= chunk_count 且 chunk_count > 0
       - 未完成 = 其余（向量化到一半 / 失败 / 空记录）
    3. 删除这些未完成文档在 chroma 中的向量 + documents.json 中的记录
    4. 重算各知识库的 document_count / vector_count
    已经完整向量化的文档及其向量不受影响。

--all 模式——完整清理：
    停后端 + 清空全部文档记录 + 重置全部计数 + 清空全部向量。

用法:
    python clean_kb.py                 # 默认：停后端 + 只清未完成文档（保留已完整向量化的）
    python clean_kb.py --all           # 完整清理：停后端 + 清全部记录/计数/向量
    python clean_kb.py --dry-run       # 只预览将删除/重置的内容，不实际执行
    python clean_kb.py --no-stop-backend  # 不停止后端进程
    python clean_kb.py --keep-chroma   # 不删向量，只清理文档记录并重算计数
    python clean_kb.py --data-dir <路径> # 指定 backend/data 目录（默认自动定位）

说明:
    - 默认模式删除向量需 chromadb（请用 .venv310 python 运行）；若不可用会跳过向量删除
    - 数据目录默认定位到脚本同级的 backend/data；脚本放在 backend 下也兼容
    - 停止后端依赖 Windows 的 netstat/taskkill（按 127.0.0.1:8000 监听 PID 定位）

依赖: Python 标准库 + 默认模式可选 chromadb。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BACKEND_PORT = 8000
HOST = "127.0.0.1"


def _find_backend_data_dir() -> Path:
    """定位 backend/data 目录：脚本在根目录 -> backend/data；脚本在 backend 下 -> ./data。"""
    here = Path(__file__).resolve().parent
    candidates = [here / "backend" / "data", here / "data"]
    for c in candidates:
        if (c / "knowledge_bases.json").exists() or (c / "chroma").exists():
            return c
    return here / "backend" / "data"


def _find_backend_pid() -> int | None:
    """通过 netstat 找 127.0.0.1:8000 的监听 PID，没有则返回 None。"""
    try:
        out = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        ).stdout
    except Exception:
        return None
    for line in out.splitlines():
        if f"{HOST}:{BACKEND_PORT}" in line and "LISTENING" in line:
            m = re.search(r"(\d+)\s*$", line.strip())
            if m:
                return int(m.group(1))
    return None


def stop_backend() -> tuple:
    """停止占用端口的后端进程。返回 (ok, 描述)。"""
    pid = _find_backend_pid()
    if pid is None:
        return True, f"未检测到 {HOST}:{BACKEND_PORT} 监听（后端未运行）"
    try:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                       capture_output=True, text=True, check=True)
        return True, f"已停止后端进程 PID={pid}"
    except Exception as e:
        return False, f"停止后端进程 PID={pid} 失败: {e}"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _is_complete(doc: dict) -> bool:
    vc = doc.get("vector_count", 0) or 0
    cc = doc.get("chunk_count", 0) or 0
    return cc > 0 and vc >= cc


def classify_docs(data_dir: Path) -> tuple:
    """按"完整/未完成"分类文档，返回 (complete_by_kb, incomplete_by_kb)。
    每组为 {knowledge_base_id: [(doc_id, doc), ...]}。"""
    docs = load_json(data_dir / "documents.json")
    complete, incomplete = {}, {}
    for did, d in docs.items():
        kb = d.get("knowledge_base_id")
        target = complete if _is_complete(d) else incomplete
        target.setdefault(kb, []).append((did, d))
    return complete, incomplete


def delete_incomplete_vectors(chroma_dir: Path, incomplete_by_kb: dict) -> tuple:
    """按 document_id 删除未完成文档在 chroma 中的向量。"""
    if not incomplete_by_kb:
        return True, "没有未完成文档，无需删除向量"
    try:
        import chromadb
    except ImportError:
        return False, "chromadb 不可用（请用 .venv310 python 运行），已跳过向量删除"
    client = chromadb.PersistentClient(path=str(chroma_dir))
    total = 0
    for kb, docs in incomplete_by_kb.items():
        if not kb:
            continue
        try:
            collection = client.get_collection(name=kb)
        except Exception:
            continue
        ids = []
        for did, _d in docs:
            try:
                got = collection.get(where={"document_id": did}, include=[])
                ids.extend(got.get("ids", []))
            except Exception:
                continue
        if ids:
            collection.delete(ids=ids)
            total += len(ids)
    return True, f"已删除未完成文档的 {total} 个向量"


def remove_incomplete_docs(data_dir: Path, incomplete_by_kb: dict) -> tuple:
    """删除未完成文档记录，并重算各知识库计数（保留完整文档）。"""
    path = data_dir / "documents.json"
    docs = load_json(path)
    remove_ids = {did for docs_in_kb in incomplete_by_kb.values() for did, _d in docs_in_kb}
    for did in remove_ids:
        docs.pop(did, None)
    save_json(path, docs)

    kb_path = data_dir / "knowledge_bases.json"
    kbs = load_json(kb_path)
    for kb_id, kb in kbs.items():
        kb_docs = [d for d in docs.values() if d.get("knowledge_base_id") == kb_id]
        kb["document_count"] = len(kb_docs)
        kb["vector_count"] = sum(d.get("vector_count", 0) or 0 for d in kb_docs)
    save_json(kb_path, kbs)
    return True, f"已删除 {len(remove_ids)} 条未完成文档记录并重算计数"


def full_clear(data_dir: Path) -> list:
    """--all 完整清理：清空文档记录 + 重置计数 + 清空向量。"""
    steps = []
    for f in ("documents.json", "excel_documents.json"):
        p = data_dir / f
        if p.exists():
            save_json(p, {})
            steps.append((True, f"{f} 已清空"))
        else:
            steps.append((True, f"{f} 不存在，跳过"))
    kb_path = data_dir / "knowledge_bases.json"
    kbs = load_json(kb_path)
    changed = sum(1 for kb in kbs.values()
                  if isinstance(kb, dict) and kb.get("document_count") is not None)
    for kb in kbs.values():
        if isinstance(kb, dict):
            kb["document_count"] = 0
            kb["vector_count"] = 0
    save_json(kb_path, kbs)
    steps.append((True, f"knowledge_bases.json 已重置 {changed} 个条目的计数"))
    chroma_dir = data_dir / "chroma"
    if chroma_dir.exists():
        removed = 0
        for p in chroma_dir.iterdir():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            removed += 1
        steps.append((True, f"chroma 已清空 {removed} 个条目（全部向量删除）"))
    else:
        steps.append((True, "chroma 目录不存在，跳过"))
    return steps


def main() -> None:
    parser = argparse.ArgumentParser(description="清理知识库：默认清未完成，--all 完整清")
    parser.add_argument("--all", action="store_true", help="完整清理：停后端 + 清全部记录/计数/向量")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不实际执行")
    parser.add_argument("--no-stop-backend", action="store_true", help="不停止后端进程")
    parser.add_argument("--keep-chroma", action="store_true", help="不删向量，只清理文档记录并重算计数")
    parser.add_argument("--data-dir", help="指定 backend/data 目录（默认自动定位）")
    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else _find_backend_data_dir()
    chroma_dir = data_dir / "chroma"

    print(f"数据目录: {data_dir}")
    print(f"后端端口: {HOST}:{BACKEND_PORT}")
    if args.all:
        print("模式: --all 完整清理（清全部记录/计数/向量）")
    else:
        complete, incomplete = classify_docs(data_dir)
        n_inc = sum(len(v) for v in incomplete.values())
        n_cmp = sum(len(v) for v in complete.values())
        print(f"模式: 默认（只清未完成） | 完整文档 {n_cmp} 个 | 未完成文档 {n_inc} 个")
        if not args.dry_run and n_inc:
            print("以下未完成文档将被清理:")
            for kb, docs in incomplete.items():
                for did, d in docs:
                    vc = d.get("vector_count", 0) or 0
                    cc = d.get("chunk_count", 0) or 0
                    print(f"  - {d.get('name', did)} (chunk={cc}, vector={vc})")
    if args.dry_run:
        print("[dry-run] 以下仅预览，不实际执行\n")

    steps = []

    # 1. 停止后端
    if args.no_stop_backend:
        steps.append((True, "跳过停止后端（--no-stop-backend）"))
    elif args.dry_run:
        pid = _find_backend_pid()
        steps.append((True, f"将停止后端进程 PID={pid}" if pid else "未检测到后端监听"))
    else:
        steps.append(stop_backend())

    # 2. 数据清理
    if args.all:
        if args.dry_run:
            steps.append((True, "将清空全部文档记录"))
            steps.append((True, "将重置全部知识库计数"))
            steps.append((True, "将清空 chroma（全部向量）" if not args.keep_chroma
                          else "将保留 chroma（--keep-chroma）"))
        else:
            if args.keep_chroma:
                for f in ("documents.json", "excel_documents.json"):
                    p = data_dir / f
                    if p.exists():
                        save_json(p, {})
                        steps.append((True, f"{f} 已清空"))
                    else:
                        steps.append((True, f"{f} 不存在，跳过"))
                kb_path = data_dir / "knowledge_bases.json"
                kbs = load_json(kb_path)
                for kb in kbs.values():
                    if isinstance(kb, dict):
                        kb["document_count"] = 0
                        kb["vector_count"] = 0
                save_json(kb_path, kbs)
                steps.append((True, "知识库计数已重置（--keep-chroma 保留向量）"))
            else:
                steps.extend(full_clear(data_dir))
    else:
        # 默认模式：只清未完成
        if args.dry_run:
            steps.append((True, f"将删除 {n_inc} 条未完成文档记录并重算计数"))
            if not args.keep_chroma and n_inc:
                steps.append((True, "将删除未完成文档在 chroma 中的向量"))
            elif args.keep_chroma:
                steps.append((True, "将保留向量（--keep-chroma）"))
        else:
            if n_inc:
                if not args.keep_chroma:
                    ok, desc = delete_incomplete_vectors(chroma_dir, incomplete)
                    steps.append((ok, desc))
                ok, desc = remove_incomplete_docs(data_dir, incomplete)
                steps.append((ok, desc))
            else:
                steps.append((True, "没有未完成文档，记录/计数/向量无需清理"))

    # 汇总输出
    print(f"\n共 {len(steps)} 步：")
    for i, (ok, desc) in enumerate(steps, 1):
        tag = "[pass]" if ok else "[fail]"
        print(f"  {i}. {tag} {desc}")

    failed = [i for i, (ok, _) in enumerate(steps, 1) if not ok]
    if failed:
        print(f"\n有 {len(failed)} 步失败: {failed}")
        sys.exit(1)
    if args.dry_run:
        print("\n[dry-run] 预览结束，未做任何改动。移除 --dry-run 即可实际执行。")
    else:
        print("\n清理完成。后端如需继续使用，请重新启动。")


if __name__ == "__main__":
    main()
