#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库检索 CLI - 本地私有知识库向量检索命令行工具
====================================================
封装后端的 GET /api/vectors/retrieve 接口，供命令行/脚本直接调用，
避免每次手写临时脚本。中文参数自动 UTF-8 编码，无乱码。

用法:
    python retrieve.py query "问题" [--kb 库名] [--top-k N] [--length N] [--json]
    python retrieve.py kbs
    python retrieve.py health

示例:
    python retrieve.py query "在ISO7816-3中什么情况下PPS会被停用" --kb ISO7816标准库 --top-k 5
    python retrieve.py query "JCRE 3.1 相比 3.0.5 新增特性" --kb JavaCard标准库 --top-k 8 --length 0
    python retrieve.py kbs

依赖: 仅 Python 标准库（urllib/json）。后端须运行在 127.0.0.1:8000。
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

# ═══════════════════════════════════════════════════════════
# UTF-8 reconfigure（防 Windows GBK 中文乱码，与 task_terminal 同款）
# ═══════════════════════════════════════════════════════════
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_API = "http://127.0.0.1:8000"
RETRIEVE_PATH = "/api/vectors/retrieve"
HEALTH_PATH = "/api/system/health"
KBS_PATH = "/api/knowledge-bases"

_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_CYAN = "\033[96m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _http_get(url: str) -> dict:
    """GET 请求并解析 JSON，超时 15 秒。"""
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def health(api: str) -> bool:
    """检查后端健康状态，失败给出启动引导。"""
    try:
        r = _http_get(api + HEALTH_PATH)
        ok = r.get("status") == "healthy" or r.get("code") == 200
        if ok:
            print(f"{_GREEN}✓ 后端健康{_RESET} ({api})")
            return True
        print(f"{_YELLOW}! 后端响应异常: {r}{_RESET}")
        return False
    except Exception as e:
        print(f"{_RED}✗ 无法连接后端 {api}{_RESET}")
        print(f"  原因: {e}")
        print("  请先启动后端（AI 自行启动或手动执行 .\\启动后端.bat）：")
        print("    cd backend")
        print("    ..\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
        return False


def list_kbs(api: str) -> None:
    """列出所有知识库。"""
    if not health(api):
        sys.exit(1)
    r = _http_get(api + KBS_PATH)
    kbs = r.get("data", [])
    print(f"{_BOLD}知识库列表（共 {len(kbs)} 个）:{_RESET}")
    for kb in kbs:
        print(f"  {_CYAN}{kb['name']}{_RESET}")
        print(f"    文档 {kb.get('document_count', 0)} 个 | 向量 {kb.get('vector_count', 0)} 块 | id={kb['id']}")


def query(api: str, text: str, kb: str, top_k: int, length: int, as_json: bool) -> None:
    """执行向量检索。"""
    if not health(api):
        sys.exit(1)

    params = {"query": text, "top_k": top_k, "content_length": length}
    if kb:
        params["knowledge_base_name"] = kb
    url = api + RETRIEVE_PATH + "?" + urllib.parse.urlencode(params)

    try:
        r = _http_get(url)
    except Exception as e:
        print(f"{_RED}✗ 检索请求失败: {e}{_RESET}")
        sys.exit(1)

    data = r.get("data", [])
    total = r.get("total", len(data))

    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return

    print(f"{_BOLD}检索: {text}{_RESET}")
    kb_s = f" 知识库: {kb}" if kb else " 全库"
    print(f"命中 {_GREEN}{total}{_RESET} 条{_DIM}{kb_s}{_RESET}\n")

    if total == 0:
        print(f"{_YELLOW}知识库中没有找到相关内容（可能不在库内，或相似度低于阈值 0.5）。{_RESET}")
        return

    for i, item in enumerate(data, 1):
        sim = item.get("similarity", 0)
        meta = item.get("metadata", {})
        doc = item.get("document_name", "?")
        chunk = meta.get("chunk_index", "?")
        content = item.get("content", "")
        print(f"{_BOLD}[{i}] 根据《{doc}》{_RESET}{_GREEN}(相似度 {sim * 100:.1f}%){_RESET} {_DIM}chunk={chunk}{_RESET}")
        print(content)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="retrieve.py",
        description="本地知识库向量检索 CLI",
    )
    parser.add_argument("--api", default=DEFAULT_API, help=f"后端地址，默认 {DEFAULT_API}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_health = sub.add_parser("health", help="检查后端健康")
    p_health.add_argument("--api", default=DEFAULT_API, help="后端地址")

    p_kbs = sub.add_parser("kbs", help="列出知识库")
    p_kbs.add_argument("--api", default=DEFAULT_API, help="后端地址")

    p_query = sub.add_parser("query", help="执行向量检索")
    p_query.add_argument("text", help="检索问题（原话）")
    p_query.add_argument("--kb", default=None, help="指定知识库名；缺省检索全部")
    p_query.add_argument("--top-k", type=int, default=5, help="返回结果数，默认 5")
    p_query.add_argument("--length", type=int, default=500, help="每条内容最大字符数，0 表示不截断")
    p_query.add_argument("--json", action="store_true", help="输出原始 JSON")
    p_query.add_argument("--api", default=DEFAULT_API, help="后端地址")

    args = parser.parse_args()

    if args.cmd == "health":
        sys.exit(0 if health(args.api) else 1)
    elif args.cmd == "kbs":
        list_kbs(args.api)
    elif args.cmd == "query":
        query(args.api, args.text, args.kb, args.top_k, args.length, args.json)


if __name__ == "__main__":
    main()
