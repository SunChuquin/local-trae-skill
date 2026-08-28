import threading
import time
from typing import Any, Dict, Optional


class UploadTracker:
    """记录上传/索引任务的实时进度（内存版，适合单进程使用）。"""

    def __init__(self):
        self._lock = threading.Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create(self, task_id: str, filename: str) -> None:
        now = time.time()
        with self._lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "filename": filename,
                "status": "queued",
                "phase": "queued",
                "done": 0,
                "total": 0,
                "message": "等待处理",
                "error": "",
                "started_at": now,
                "phase_started_at": now,
                "updated_at": now,
            }

    def update(self, task_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            task.update(fields)
            task["updated_at"] = time.time()
            return dict(task)

    def bump(self, task_id: str, increment: int) -> Optional[Dict[str, Any]]:
        """原子地推进已完成数量（用于向量化的分批进度）。"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            task["done"] = task.get("done", 0) + increment
            task["updated_at"] = time.time()
            return dict(task)

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task else None

    def list_tasks(self, limit: int = 0) -> list:
        """列出全部任务（按开始时间倒序），供任务列表接口轮询。
        limit=0 表示不限制（返回全部）。"""
        with self._lock:
            states = [dict(t) for t in self._tasks.values()]
        states.sort(key=lambda s: s.get("started_at") or 0, reverse=True)
        if limit and limit > 0:
            states = states[:limit]
        return [_enrich_public_state(s) for s in states]

    def public_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """对外返回的进度快照，附带 percent 与剩余时间估算。"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            state = dict(task)
        return _enrich_public_state(state)


def _enrich_public_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """为任务快照补充 percent 与剩余时间估算（调用方需已持有副本，避免锁重入）。"""
    total = state.get("total") or 0
    done = state.get("done") or 0
    state["percent"] = round(done / total * 100, 1) if total else 0.0

    # 仅对可量化的进度阶段（向量化/写入）做剩余时间估算
    estimate = None
    if total and done > 0 and done < total:
        anchor = state.get("phase_started_at") or state.get("started_at") or time.time()
        elapsed = max(time.time() - anchor, 0.1)
        speed = done / elapsed  # 个/秒
        if speed > 0:
            estimate = int(round((total - done) / speed))
    state["estimate_seconds"] = estimate
    return state


upload_tracker = UploadTracker()