import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Dict, Any, Optional, TypeVar, Generic
from datetime import datetime
from loguru import logger
from app.config import settings

T = TypeVar('T')


class JSONStorage:
    def __init__(self, filename: str):
        self.filepath: Path = settings.get_data_path() / filename
        self._data: Dict[str, Any] = {}
        # 写锁：多个后台线程可能同时 set/delete，必须串行化且原子落盘，
        # 否则并发写或进程被中断会导致 JSON 文件损坏、全量数据丢失。
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                logger.info(f"从 {self.filepath} 加载数据成功，共 {len(self._data)} 条记录")
            except Exception as e:
                logger.error(f"加载数据失败: {str(e)}")
                self._data = {}
        else:
            self._data = {}
            logger.info(f"数据文件 {self.filepath} 不存在，创建新存储")

    def _save(self) -> bool:
        """原子写盘：先写临时文件再 os.replace，避免写一半被中断导致整个文件损坏。"""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(
                dir=str(self.filepath.parent), suffix='.tmp'
            )
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2,
                              default=self._json_serializer)
                os.replace(tmp_path, self.filepath)
            except Exception:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise
            return True
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return False

    def _json_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> bool:
        with self._lock:
            self._data[key] = value
            return self._save()

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._data:
                del self._data[key]
                return self._save()
            return True

    def get_all(self) -> Dict[str, Any]:
        return self._data.copy()

    def count(self) -> int:
        return len(self._data)

    def clear(self) -> bool:
        with self._lock:
            self._data = {}
            return self._save()


knowledge_base_storage = JSONStorage("knowledge_bases.json")
document_storage = JSONStorage("documents.json")
skill_config_storage = JSONStorage("skill_config.json")
excel_doc_storage = JSONStorage("excel_documents.json")


class GenericStorage:
    """
    通用键值存储，用于存储任意 JSON 可序列化数据
    """
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._dirty = False

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> bool:
        self._cache[key] = value
        self._dirty = True
        self._save_all()
        return True

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            self._dirty = True
            self._save_all()
        return True

    def get_all(self) -> Dict[str, Any]:
        return self._cache.copy()

    def _save_all(self) -> bool:
        if not self._dirty:
            return True
        try:
            excel_path = settings.get_data_path() / "excel_documents.json"
            with open(excel_path, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2, default=self._json_serializer)
            self._dirty = False
            return True
        except Exception as e:
            logger.error(f"保存 Excel 文档索引失败: {str(e)}")
            return False

    def _json_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def load_from_file(self):
        """从文件加载已有数据"""
        excel_path = settings.get_data_path() / "excel_documents.json"
        if excel_path.exists():
            try:
                with open(excel_path, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                logger.info(f"从 {excel_path} 加载 Excel 文档索引成功，共 {len(self._cache)} 条")
            except Exception as e:
                logger.error(f"加载 Excel 文档索引失败: {str(e)}")
                self._cache = {}


storage = GenericStorage()
storage.load_from_file()
