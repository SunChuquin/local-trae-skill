#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传任务进度轮询：直到全部 done/error 后汇总退出。
配合 upload_docs.py 生成的 JSON 使用。

用法:
    python monitor_upload.py                            # 读默认 temp_upload_tasks.json
    python monitor_upload.py --tasks temp_gp_tasks.json
    python monitor_upload.py --tasks temp_gp_tasks.json --api http://127.0.0.1:8000
"""
import argparse
import json
import sys
import time
import urllib.request

DEFAULT_API = "http://127.0.0.1:8000"
DEFAULT_TASKS = "temp_upload_tasks.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def fetch_progress(api: str, task_id: str) -> dict:
    with urllib.request.urlopen(
        f"{api.rstrip('/')}/api/documents/upload-progress/{task_id}", timeout=10
    ) as resp:
        return json.loads(resp.read().decode("utf-8"))["data"]


def main() -> None:
    parser = argparse.ArgumentParser(prog="monitor_upload.py", description="上传任务进度轮询")
    parser.add_argument("--tasks", default=DEFAULT_TASKS,
                        help=f"任务 JSON 路径（upload_docs.py 输出，默认 {DEFAULT_TASKS}）")
    parser.add_argument("--api", default=DEFAULT_API, help=f"后端地址（默认 {DEFAULT_API}）")
    args = parser.parse_args()

    try:
        with open(args.tasks, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"错误：任务文件不存在: {args.tasks}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：任务文件不是合法 JSON: {e}")
        sys.exit(1)

    tasks = {
        name: d["data"]["task_id"]
        for name, d in data.items()
        if d and d.get("data") and d["data"].get("task_id")
    }
    if not tasks:
        print("任务文件中没有可轮询的 task_id（可能全部上传失败，见 JSON 里的 error）。")
        sys.exit(1)

    last_print = {}
    while tasks:
        all_done = True
        for name, tid in list(tasks.items()):
            try:
                state = fetch_progress(args.api, tid)
            except Exception as e:
                print(f"{name}: 查询失败 {e}", flush=True)
                all_done = False
                continue
            status = state.get("status")
            done = state.get("done")
            total = state.get("total")
            message = state.get("message", "")
            key = (status, done, total)
            if key != last_print.get(name):
                last_print[name] = key
                print(f"{name}: {status} | {done}/{total} | {message}", flush=True)
            if status in ("done", "error"):
                tasks.pop(name)
            else:
                all_done = False
        if not all_done and tasks:
            time.sleep(10)

    print("=== 全部结束 ===", flush=True)


if __name__ == "__main__":
    main()
