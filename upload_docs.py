#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用批量文档上传工具（upload_iso_pdfs.py 的参数化通用版）
============================================================
扫描目录下指定扩展名的文档，逐个 POST 到后端 /api/documents/upload，
把每个文件的响应（含 task_id）写入一个 JSON，供 monitor_upload.py 轮询。

用法:
    python upload_docs.py --src <目录> --kb-id <知识库ID>
                          [--out <json路径>] [--ext pdf docx] [--skip <子串>] [--api <地址>]
                          [--no-dashboard]          # 不自动启动进度看板
                          [--force]                 # 跳过"已入库检测"，强制全部上传

示例:
    # globalplatform（含 docx）→ 新知识库
    python upload_docs.py --src "c:\\Users\\sunck\\home\\projects\\doc\\globalplatform" --kb-id <GP知识库ID> --out temp_gp_tasks.json --ext pdf docx
    # iso_7816 → 现有 ISO 库
    python upload_docs.py --src "c:\\Users\\sunck\\home\\projects\\doc\\iso_7816" --kb-id e70ef4bc-c3f1-4600-ae8c-727605754896 --out temp_iso_tasks.json

说明:
    - 默认会先查询知识库内已有文档名，自动跳过已入库的文件，防止重复向量化
    - 上传前会自动弹出一个独立 cmd 窗口运行 task_terminal.py dashboard（自动最大化），
      实时显示处理进度；不需要可加 --no-dashboard 关闭
    - --ext 可多值（默认 pdf）；MIME 按扩展名自动选择（含 docx/doc/md/txt）
    - --skip 可重复传入，跳过文件名含该子串的文件（如已入库文件）
    - 结果 JSON 格式: {文件名: 上传响应}，与 monitor_upload.py 兼容

依赖: 仅 Python 标准库。后端须运行在 127.0.0.1:8000（或 --api 指定）。
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_API = "http://127.0.0.1:8000"
DEFAULT_OUT = "temp_upload_tasks.json"

MIME = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".md": "text/markdown",
    ".txt": "text/plain",
}


def multipart_form(fields: dict, files: dict) -> tuple:
    """构造 multipart/form-data 报文，返回 (boundary, body)。"""
    boundary = "----TraeBoundary" + os.urandom(8).hex()
    buf = b""
    for k, v in fields.items():
        buf += f"--{boundary}\r\n".encode()
        buf += f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode()
        buf += str(v).encode("utf-8") + b"\r\n"
    for k, (filename, content, mime) in files.items():
        buf += f"--{boundary}\r\n".encode()
        buf += f'Content-Disposition: form-data; name="{k}"; filename="{filename}"\r\n'.encode()
        buf += f"Content-Type: {mime}\r\n\r\n".encode()
        buf += content + b"\r\n"
    buf += f"--{boundary}--\r\n".encode()
    return boundary, buf


def upload(api: str, kb_id: str, src_dir: str, filename: str) -> dict:
    """上传单个文件，返回后端 JSON 响应。"""
    path = os.path.join(src_dir, filename)
    ext = os.path.splitext(filename)[1].lower()
    mime = MIME.get(ext, "application/octet-stream")
    with open(path, "rb") as f:
        content = f.read()
    boundary, body = multipart_form(
        {"knowledge_base_id": kb_id},
        {"file": (filename, content, mime)},
    )
    req = urllib.request.Request(
        api.rstrip("/") + "/api/documents/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_existing_names(api: str, kb_id: str) -> set:
    """获取知识库内已有文档名集合，用于跳过已入库文件，防止重复向量化。"""
    with urllib.request.urlopen(
        f"{api.rstrip('/')}/api/documents/knowledge-base/{urllib.parse.quote(kb_id)}",
        timeout=15,
    ) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return {d.get("name") for d in data.get("data", []) if d.get("name")}


def launch_dashboard() -> None:
    """上传前自动弹出独立 cmd 窗口运行 task_terminal.py dashboard（自动最大化），
    让用户实时看到处理进度，避免忘记启动看板。"""
    if os.name != "nt":
        return
    try:
        import subprocess
        script_dir = os.path.dirname(os.path.abspath(__file__))
        terminal = os.path.join(script_dir, "task_terminal.py")
        py = sys.executable
        # 直接 Popen 启动 Python 进程，用 cwd 代替 cd /d（避免 cmd.exe 引号解析错乱）；
        # CREATE_NEW_CONSOLE 会弹出独立 cmd 窗口，窗口随 Python 进程存活而保持打开。
        subprocess.Popen(
            [py, terminal, "dashboard"],
            cwd=script_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        print("已自动启动进度看板（task_terminal.py dashboard，最大化窗口）")
    except Exception as e:
        print(f"（自动启动进度看板失败，可手动运行 task_terminal.py dashboard）{e}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="upload_docs.py", description="通用批量文档上传工具")
    parser.add_argument("--src", required=True, help="源目录（必填）")
    parser.add_argument("--kb-id", required=True, help="目标知识库 ID（必填）")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"任务结果 JSON 路径（默认 {DEFAULT_OUT}）")
    parser.add_argument("--ext", nargs="+", default=["pdf"],
                        help="要上传的扩展名（默认 pdf，可多值如 pdf docx）")
    parser.add_argument("--skip", action="append", default=[],
                        help="跳过文件名含该子串的文件（可重复传入）")
    parser.add_argument("--no-dashboard", action="store_true",
                        help="不自动启动 task_terminal.py dashboard 进度看板")
    parser.add_argument("--force", action="store_true",
                        help="不检查已入库文件，强制全部上传")
    parser.add_argument("--api", default=DEFAULT_API, help=f"后端地址（默认 {DEFAULT_API}）")
    args = parser.parse_args()

    if not args.no_dashboard:
        launch_dashboard()

    src = args.src
    if not os.path.isdir(src):
        print(f"错误：目录不存在: {src}")
        sys.exit(1)

    exts = tuple(e.lower() if e.startswith(".") else "." + e.lower() for e in args.ext)
    all_files = sorted(
        f for f in os.listdir(src)
        if f.lower().endswith(exts) and not any(s in f for s in args.skip)
    )
    if not all_files:
        print("目录下没有匹配的文件（检查 --src / --ext / --skip）。")
        sys.exit(1)

    # 已入库检测：查询库内已有文档名，跳过已入库文件（--force 可关闭）
    existing = set()
    if not args.force:
        try:
            existing = fetch_existing_names(args.api, args.kb_id)
            print(f"知识库已入库文档数: {len(existing)}")
        except Exception as e:
            print(f"错误：无法获取知识库已有文档列表（{e}）")
            print("请确认后端运行、知识库 ID 正确；或加 --force 强制全量上传。")
            sys.exit(1)

    files = [f for f in all_files if f not in existing]
    skipped = [f for f in all_files if f in existing]
    print(f"目录共 {len(all_files)} 个文件")
    if skipped:
        print(f"  已入库跳过 {len(skipped)} 个")
        for f in skipped:
            print(f"    ⊘ {f}")
    print(f"  待上传 {len(files)} 个\n")

    if not files:
        print("全部文件都已在知识库中，无需上传。")
        sys.exit(0)

    results = {}
    for i, f in enumerate(files, 1):
        try:
            resp = upload(args.api, args.kb_id, src, f)
            results[f] = resp
            tid = resp.get("data", {}).get("task_id")
            print(f"[{i}/{len(files)}] 已提交 {f} -> task_id={tid}", flush=True)
        except Exception as e:
            results[f] = {"error": str(e)}
            print(f"[{i}/{len(files)}] 失败 {f}: {e}", flush=True)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"\n完成，任务记录已写入 {args.out}")
    print(f"下一步: python monitor_upload.py --tasks {args.out}")


if __name__ == "__main__":
    main()
