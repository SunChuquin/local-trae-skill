#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务终端 - 本地知识库文档处理进度监控 CLI
========================================
简洁风格：每个文件一行，处理完打勾，最后总结"任务已完成"。

显示效果（demo）：
    ═══ 演示模式（纯模拟）═══
      共 5 个文件，串行处理

      → ISO7816-1.pdf（模拟）[pass]
    → ISO7816-2.pdf（模拟）[pass]
    → ISO7816-3.pdf（模拟）[pass]    ← 处理中会在这行显示进度
      → ISO7816-4.pdf（模拟）      ← 还没开始
      → ISO7816-5.pdf（模拟）      ← 还没开始

      任务已完成

Windows cmd 兼容：
    1. UTF-8 reconfigure（tdx_parser2 同款，防 GBK 炸 Unicode 块字符）
    2. ctypes 显式开启 ENABLE_VIRTUAL_TERMINAL_PROCESSING
    3. ANSI \\033[2K\\r 清行 + 回车，无残影

用法:
    python task_terminal.py                    # dashboard（启动即全屏最大化）
    python task_terminal.py demo
    python task_terminal.py list
    python task_terminal.py watch <task_id>
    python task_terminal.py --no-max dashboard # 不最大化控制台
"""
import argparse
import json
import os
import re
import shutil
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

# ═══════════════════════════════════════════════════════════
# 第 1 重保险：UTF-8 reconfigure（tdx_parser2 同款）
# ═══════════════════════════════════════════════════════════
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')

# ═══════════════════════════════════════════════════════════
# 第 2 重保险：ctypes 显式开启 ENABLE_VIRTUAL_TERMINAL_PROCESSING
# ═══════════════════════════════════════════════════════════
if os.name == "nt":
    try:
        import ctypes
        _kernel32 = ctypes.windll.kernel32
        _hStdout = _kernel32.GetStdHandle(-11)
        _mode = ctypes.c_ulong()
        if _kernel32.GetConsoleMode(_hStdout, ctypes.byref(_mode)):
            _kernel32.SetConsoleMode(_hStdout, _mode.value | 0x0001 | 0x0004)
    except Exception:
        pass


def maximize_console() -> None:
    """启动时把控制台窗口最大化，并把缓冲区宽度同步为可视宽度，
    保证 shutil.get_terminal_size() 返回正确的列数（行宽计算才准确）。
    可用 --no-max 关闭。"""
    if os.name != "nt":
        return
    try:
        import ctypes
        import ctypes.wintypes
        _kernel32 = ctypes.windll.kernel32
        _user32 = ctypes.windll.user32
        _hwnd = _kernel32.GetConsoleWindow()  # GetConsoleWindow 属于 kernel32
        if not _hwnd:
            return
        _user32.ShowWindow(_hwnd, 3)  # SW_MAXIMIZE

        class _CSBI(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.wintypes.COORD),
                ("dwCursorPosition", ctypes.wintypes.COORD),
                ("wAttributes", ctypes.wintypes.WORD),
                ("srWindow", ctypes.wintypes.SMALL_RECT),
                ("dwMaximumWindowSize", ctypes.wintypes.COORD),
            ]

        _h_out = _kernel32.GetStdHandle(-11)
        _info = _CSBI()
        if _kernel32.GetConsoleScreenBufferInfo(_h_out, ctypes.byref(_info)):
            cols = _info.srWindow.Right - _info.srWindow.Left + 1
            rows = _info.srWindow.Bottom - _info.srWindow.Top + 1
            if _info.dwSize.X < cols:
                _kernel32.SetConsoleScreenBufferSize(
                    _h_out,
                    ctypes.wintypes.COORD(cols, max(_info.dwSize.Y, rows)),
                )
    except Exception:
        pass

DEFAULT_API = "http://127.0.0.1:8000"
DEFAULT_INTERVAL = 1.5
TERMINAL_STATUS = ("done", "error")

PHASE_LABEL = {
    "queued": "排队",
    "parsing": "解析",
    "chunking": "分块",
    "embedding": "向量化",
    "saving": "保存",
    "done": "完成",
    "error": "失败",
}

# 有进度条的阶段（后端会上报 done/total）
PROGRESS_PHASES = {"chunking", "embedding", "saving"}

# ANSI 颜色（仅点缀）
_GREEN = "\033[92m"
_RED = "\033[91m"
_CYAN = "\033[96m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

# 第 3 重保险：清行 + 回车 前缀（写每行前先清掉旧内容，防残影）
_CLEAR = "\033[2K\r"


def _http_get_json(url: str, timeout: float = 5.0):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_tasks(api: str):
    return _http_get_json(api.rstrip("/") + "/api/documents/upload-tasks")


def fetch_task(api: str, task_id: str):
    return _http_get_json(api.rstrip("/") + f"/api/documents/upload-progress/{urllib.parse.quote(task_id)}")


def fmt_eta(seconds) -> str:
    if seconds is None:
        return ""
    seconds = int(seconds)
    if seconds < 60:
        return f" 剩{seconds}s"
    return f" 剩{seconds // 60}m{seconds % 60}s"


def draw_bar(percent: float, width: int = 15) -> str:
    """tdx_parser2 同款：█ 实心 + ░ 空心。"""
    pct = max(0.0, min(100.0, percent or 0.0))
    filled = int(width * pct // 100)
    return "█" * filled + "░" * (width - filled)


# ═══════════════════════════════════════════════════════════
# 终端宽度安全：文件名按显示宽度截断，防止整行超宽自动换行
# ═══════════════════════════════════════════════════════════
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    """去掉 ANSI 颜色码，用于计算真实显示宽度。"""
    return _ANSI_RE.sub("", s)


def disp_width(s: str) -> int:
    """计算字符串的终端显示宽度（中文/全角字符占 2 列）。"""
    w = 0
    for ch in strip_ansi(s):
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def truncate_wide(s: str, max_w: int) -> str:
    """按显示宽度截断，超出部分以 … 结尾（省略号本身占 2 列）。"""
    if disp_width(s) <= max_w:
        return s
    out = ""
    w = 0
    for ch in s:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if w + cw > max_w - 2:  # 预留省略号 2 列
            break
        out += ch
        w += cw
    return out + "…"


def safe_line(filename: str, suffix: str = "") -> str:
    """拼装一行：文件名动态截断，保证整行不超终端宽度。"""
    cols = shutil.get_terminal_size().columns
    if cols < 30:  # 极窄终端兜底
        cols = 30
    prefix = "  → "
    # suffix 前面自动补一个空格（如果不是以空格开头）
    if suffix and not suffix.startswith(" "):
        suffix = " " + suffix
    max_name = max(2, cols - disp_width(prefix) - disp_width(suffix) - 2)
    return prefix + truncate_wide(filename, max_name) + suffix


def build_progress(label: str, percent: float, done: int, total: int, eta) -> str:
    """拼进度字符串，进度条宽度按终端宽度动态压缩，保证不超宽。"""
    cols = shutil.get_terminal_size().columns
    if cols < 30:
        cols = 30
    bar_w = 15
    while bar_w >= 2:
        bar = draw_bar(percent, bar_w)
        prog = f"  {label} [{bar}] {int(percent)}% ({done}/{total}){fmt_eta(eta)}"
        if disp_width(prog) <= cols - 6:  # 留出 "  → " 与余量
            return prog
        bar_w -= 2
    # 极端兜底：去掉进度条，只留文字百分比
    return f"  {label} {int(percent)}% ({done}/{total})"


# ═══════════════════════════════════════════════════════════
# 任务看板：区块式渲染（带编号，整块重绘）
# ═══════════════════════════════════════════════════════════

SEP_CHARS = 35


def _bar(ch: str) -> str:
    """分隔线：固定 35 字符，窄终端自适应压缩。"""
    cols = shutil.get_terminal_size().columns
    return ch * max(10, min(SEP_CHARS, cols - 2))


def print_dashboard_title() -> None:
    """打印看板标题（固定一次，不参与重绘）。"""
    bar = _bar("#")
    print(f"{_CYAN}{_BOLD}{bar}{_RESET}")
    print(f"{_BOLD}  文档处理任务看板，串行处理（一次一个）{_RESET}")
    print(f"{_CYAN}{_BOLD}{bar}{_RESET}")
    print()


def task_line(idx: int, filename: str, suffix: str = "") -> str:
    """【N】 → 文件名 + 状态，文件名按终端宽度截断。"""
    cols = shutil.get_terminal_size().columns
    if cols < 40:
        cols = 40
    prefix = f"  【{idx}】 → "
    if suffix and not suffix.startswith(" "):
        suffix = " " + suffix
    max_name = max(2, cols - disp_width(prefix) - disp_width(suffix) - 2)
    return prefix + truncate_wide(filename, max_name) + suffix


def build_block_rows(all_tasks: list) -> list:
    """生成看板区块的所有文本行。"""
    total = len(all_tasks)
    done_count = sum(1 for t in all_tasks if t.get("status") == "done")
    fail_count = sum(1 for t in all_tasks if t.get("status") == "error")
    queued_count = sum(1 for t in all_tasks if t.get("status") == "queued")

    rows = [_bar("=")]
    if total == 0:
        rows.append(f"  {_DIM}暂无任务，上传文档后自动开始处理...{_RESET}")
    else:
        stats = f"完成 {done_count}"
        if fail_count:
            stats += f" / 失败 {fail_count}"
        if queued_count:
            stats += f" / 排队 {queued_count}"
        rows.append(f"当前共 {total} 个任务（{stats}）：")
        for idx, t in enumerate(all_tasks, 1):
            status = t.get("status", "unknown")
            if status == "queued":
                continue  # 排队任务折叠成底部汇总行
            fname = t.get("filename") or "未知"
            if status == "done":
                rows.append(task_line(idx, fname, f"{_GREEN}[pass]{_RESET}"))
            elif status == "error":
                rows.append(task_line(idx, fname, f"{_RED}[fail]{_RESET}"))
            else:
                phase = t.get("phase") or status
                label = PHASE_LABEL.get(phase, phase)
                if phase in PROGRESS_PHASES and t.get("total", 0) > 0:
                    prog = build_progress(
                        label,
                        t.get("percent", 0) or 0,
                        t.get("done", 0) or 0,
                        t.get("total", 0) or 0,
                        t.get("estimate_seconds"),
                    )
                else:
                    prog = f"  {label}"
                rows.append(task_line(idx, fname, prog))
        if queued_count > 0:
            rows.append(f"  {_DIM}... 其余 {queued_count} 个文件排队中{_RESET}")
    rows.append(_bar("="))
    return rows


def redraw_block(rows: list, old_rows: int) -> None:
    """整块重绘：光标回到区块顶部，逐行清空重写，防止滚动/残影。
    注意：光标停在区块最后一行（非其后），故上移 old_rows-1 行即可回到区块顶。"""
    n = max(len(rows), old_rows)
    if old_rows > 1:
        sys.stdout.write(f"\033[{old_rows - 1}A")
    for i in range(n):
        sys.stdout.write(_CLEAR)
        if i < len(rows):
            sys.stdout.write(rows[i])
        if i < n - 1:
            sys.stdout.write("\n")
    sys.stdout.flush()


# ═══════════════════════════════════════════════════════════
# 命令实现
# ═══════════════════════════════════════════════════════════


def cmd_dashboard(api: str, interval: float) -> None:
    """实时看板：区块式整块重绘，带编号，任务总数动态更新。
    渲染策略：
      - 标题固定打印一次（# 框）
      - 任务区块（==== 上下框）整块重绘，不滚动不闪烁
      - 已完成 [pass] / 失败 [fail] / 处理中进度 / 排队折叠汇总
    """
    print_dashboard_title()
    block_rows = 0
    total = 0
    done_fail = 0
    try:
        while True:
            try:
                all_tasks = fetch_tasks(api).get("data", [])
            except Exception:
                redraw_block([f"{_RED}连接中断：{api}，请检查后端是否运行{_RESET}"], block_rows)
                sys.exit(1)
            rows = build_block_rows(all_tasks)
            redraw_block(rows, block_rows)
            block_rows = len(rows)
            total = len(all_tasks)
            done_fail = sum(1 for t in all_tasks if t.get("status") in TERMINAL_STATUS)
            if total > 0 and done_fail >= total:
                break
            try:
                time.sleep(interval)
            except KeyboardInterrupt:
                break
    except KeyboardInterrupt:
        pass
    redraw_block([], block_rows)
    print(f"{_GREEN}{_BOLD}任务已完成：{done_fail}/{total} 个文件{_RESET}")
    print(f"{_DIM}可到前端 http://localhost:3000 或检索接口查询文档。{_RESET}")


def cmd_list(api: str) -> None:
    try:
        tasks = fetch_tasks(api).get("data", [])
    except Exception:
        print(f"{_RED}无法连接后端。{_RESET}")
        sys.exit(1)
    if not tasks:
        print("暂无任务。")
        return
    for t in tasks:
        fname = t.get("filename") or "未知"
        status = t.get("status", "unknown")
        total = t.get("total") or 0
        done = t.get("done") or 0
        pct = t.get("percent") or 0.0
        phase = PHASE_LABEL.get(t.get("phase") or "?", "?")
        print(f"▌ {fname}  [{status.upper()}/{phase}]  {done}/{total}  {pct:.0f}%")


def cmd_watch(api: str, task_id: str, interval: float) -> None:
    print(f"跟踪任务 {task_id}，Ctrl+C 退出...")
    first = True
    while True:
        try:
            t = fetch_task(api, task_id).get("data") or {}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"{_RED}任务不存在。{_RESET}")
                sys.exit(1)
            sys.exit(1)
        except Exception:
            print(f"{_RED}无法连接后端。{_RESET}")
            sys.exit(1)

        fname = t.get("filename", "未知")
        phase = t.get("phase") or t.get("status") or "unknown"
        pct = t.get("percent") or 0.0
        done = t.get("done") or 0
        total = t.get("total") or 0
        eta = t.get("estimate_seconds")

        if first:
            sys.stdout.write(safe_line(fname))
            sys.stdout.flush()
            first = False

        label = PHASE_LABEL.get(phase, phase)
        if phase in ("chunking", "embedding", "saving") and total:
            prog = build_progress(label, pct, done, total, eta)
            sys.stdout.write(_CLEAR + safe_line(fname, prog))
            sys.stdout.flush()
        else:
            sys.stdout.write(_CLEAR + safe_line(fname, f"  {label}"))
            sys.stdout.flush()

        if t.get("status") in TERMINAL_STATUS:
            ok = t.get("status") == "done"
            mark = f"{_GREEN}[pass]{_RESET}" if ok else f"{_RED}[fail]{_RESET}"
            sys.stdout.write(_CLEAR + safe_line(fname, mark) + "\n")
            sys.stdout.flush()
            print(f"\n{_GREEN if ok else _RED}任务{'完成' if ok else '失败'}{_RESET}")
            break
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            break
    sys.stdout.write("\n")
    sys.stdout.flush()


# ═══════════════════════════════════════════════════════════
# Demo：模拟 3 个文件逐个处理（区块式看板）
# ═══════════════════════════════════════════════════════════

def cmd_demo() -> None:
    files = [
        "ISO_IEC 7816-3-2006 Identification cards Integrated circuit cards.pdf",
        "Java Card Platform Runtime Environment Specification Classic Edition 3.1.pdf",
        "Java Card Protection Profile v3.1.0 Closed Configuration 智能卡安全评估.pdf",
    ]
    print_dashboard_title()
    block_rows = 0
    tasks = [
        {"task_id": f"demo-{i+1}", "filename": f,
         "status": "queued", "phase": "queued",
         "done": 0, "total": 0, "percent": 0, "estimate_seconds": None}
        for i, f in enumerate(files)
    ]

    def _render():
        nonlocal block_rows
        rows = build_block_rows(tasks)
        redraw_block(rows, block_rows)
        block_rows = len(rows)

    try:
        # 初始全排队
        _render()
        time.sleep(0.6)
        for i in range(len(tasks)):
            # 进入处理中
            tasks[i]["status"] = "processing"
            tasks[i]["phase"] = "parsing"
            _render()
            time.sleep(0.4)
            # 分块 → 向量化 → 保存
            for phase, steps in (("chunking", 20), ("embedding", 30), ("saving", 5)):
                tasks[i]["phase"] = phase
                tasks[i]["total"] = steps
                tasks[i]["done"] = 0
                tasks[i]["percent"] = 0
                tasks[i]["estimate_seconds"] = None
                for step in range(1, steps + 1):
                    tasks[i]["done"] = step
                    tasks[i]["percent"] = round(step / steps * 100, 1)
                    if phase == "embedding":
                        tasks[i]["estimate_seconds"] = (steps - step) // 3
                    _render()
                    time.sleep(0.03)
            # 完成
            tasks[i]["status"] = "done"
            tasks[i]["phase"] = "done"
            tasks[i]["percent"] = 100
            _render()
            time.sleep(0.4)

        # 所有文件已完成
        redraw_block([], block_rows)
        print(f"{_GREEN}{_BOLD}任务已完成：{len(files)}/{len(files)} 个文件{_RESET}")
        print(f"{_DIM}确认没问题后，对我说 '开始'，我启动真正的文档向量化。{_RESET}")
    except KeyboardInterrupt:
        redraw_block([], block_rows)
        sys.stdout.write(_CLEAR + f"{_DIM}演示已停止。{_RESET}\n")
        sys.stdout.flush()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="task_terminal",
        description="文档处理进度监控（每文件一行，完成打勾）",
    )
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    parser.add_argument("--no-max", action="store_true",
                        help="不最大化控制台窗口（默认启动即全屏最大化）")
    parser.add_argument("command", nargs="?", default="dashboard",
                        choices=["dashboard", "list", "watch", "demo"])
    parser.add_argument("task_id", nargs="?", default=None)
    args = parser.parse_args()

    if not args.no_max:
        maximize_console()

    if args.command == "list":
        cmd_list(args.api)
    elif args.command == "watch":
        if not args.task_id:
            print("用法: python task_terminal.py watch <task_id>")
            sys.exit(1)
        cmd_watch(args.api, args.task_id, args.interval)
    elif args.command == "demo":
        cmd_demo()
    else:
        cmd_dashboard(args.api, args.interval)


if __name__ == "__main__":
    main()
