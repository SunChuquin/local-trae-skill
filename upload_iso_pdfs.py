# -*- coding: utf-8 -*-
"""批量上传 iso_7816 目录下尚未入库的 PDF 到 ISO7816标准库，并逐批采集每个文件的任务 ID。"""
import json
import os
import re
import urllib.request
import urllib.parse

BASE = "http://127.0.0.1:8000"
KB_ID = "d1e29ca9-1d31-482c-b26e-2dfe660c112b"
SRC_DIR = r"c:\Users\sunck\home\projects\doc\iso_7816"


def multipart_form(fields: dict, files: dict) -> bytes:
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


def upload(filename: str) -> dict:
    path = os.path.join(SRC_DIR, filename)
    with open(path, "rb") as f:
        content = f.read()
    boundary, body = multipart_form(
        {"knowledge_base_id": KB_ID},
        {"file": (filename, content, "application/pdf")},
    )
    req = urllib.request.Request(
        BASE + "/api/documents/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    files = sorted(
        f for f in os.listdir(SRC_DIR)
        if f.lower().endswith(".pdf") and f.lower() != "iso_iec 7816-3-2006.pdf"
    )
    results = {}
    for i, f in enumerate(files, 1):
        try:
            resp = upload(f)
            results[f] = resp
            tid = resp.get("data", {}).get("task_id")
            print(f"[{i}/{len(files)}] 已提交 {f} -> task_id={tid}", flush=True)
        except Exception as e:
            results[f] = {"error": str(e)}
            print(f"[{i}/{len(files)}] 失败 {f}: {e}", flush=True)
    with open(r"c:\Users\sunck\home\projects\doc\local-trae-skill\temp_upload_tasks.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print("完成，任务记录已写入 temp_upload_tasks.json", flush=True)


if __name__ == "__main__":
    main()