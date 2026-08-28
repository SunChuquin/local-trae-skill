"""
问答记忆服务（持久化记忆 - MVP）
================================
让 RAG 从"无状态、用完即弃"走向"记住成功交互"：把已验证的问答存入一个独立的
内部向量集合（__memory__），后续检索时若命中高相似度问题，则直接返回缓存答案，
避免每次重新跑完整检索-生成流程。

设计要点：
- 内部集合名以 __ 前缀标识，检索全库时会被排除，不污染普通文档检索。
- 保存：把问题向量化存入集合，metadata 携带答案与时间。
- 检索：在记忆集合按问题语义查最近邻，相似度高于阈值视为"已验证问题"命中。
- 记忆命中属于"锦上添花"：未命中时完全走原检索流程，不影响现有功能。
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
import re
from loguru import logger
from app.services.chroma_service import chroma_service

# 内部集合名：以字母开头（chroma 要求字母数字开头结尾），检索全库时据此排除
INTERNAL_PREFIX = "mem_"


class MemoryService:
    MEMORY_COLLECTION = "mem_qa"
    # 记忆命中的相似度阈值：只有高度相似才算"已验证问题"，避免误命中
    DEFAULT_HIT_THRESHOLD = 0.85

    def _ensure_collection(self):
        """确保记忆集合存在（首次保存时自动创建）。"""
        return chroma_service.get_or_create_collection(self.MEMORY_COLLECTION)

    def save_qa(self, question: str, answer: str, source_note: Optional[str] = None) -> bool:
        """保存一条已验证的问答到长期记忆。

        以问题文本为内容做向量，metadata 携带答案与元信息，便于命中后直接回答。
        """
        q = (question or "").strip()
        a = (answer or "").strip()
        if not q or not a:
            logger.warning("保存问答记忆失败：问题或答案为空")
            return False

        self._ensure_collection()

        mem_id = "mem_" + hashlib.sha1(q.encode("utf-8")).hexdigest()[:16]
        metadata: Dict[str, Any] = {
            "question": q,
            "answer": a,
            "created_at": datetime.now().isoformat(),
            "type": "qa",
        }
        if source_note:
            metadata["source_note"] = source_note

        ok = chroma_service.add_vectors(
            collection_name=self.MEMORY_COLLECTION,
            documents=[q],
            metadatas=[metadata],
            ids=[mem_id],
        )
        logger.info(f"保存问答记忆: {q[:50]}... -> {ok}")
        return ok

    @staticmethod
    def _normalize(text: str) -> str:
        """归一化用于"一字不差"判断：去全部空白并转小写（保留标点与字序）。"""
        return re.sub(r"\s+", "", (text or "")).lower()

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """在记忆集合中检索与问题最相似的历史问答。

        返回按相似度降序的命中列表（含 answer），未命中返回空列表。
        每条命中带 exact 字段：True 表示归一化后与查询一字不差（可安全直接复用答案），
        False 表示仅语义近似（是否真是用户所问需上层确认）。
        """
        threshold = self.DEFAULT_HIT_THRESHOLD if threshold is None else threshold
        if not query or not query.strip():
            return []

        collection = chroma_service.get_collection(self.MEMORY_COLLECTION)
        if collection is None:
            return []

        results = chroma_service.query_vectors(
            collection_name=self.MEMORY_COLLECTION,
            query_texts=[query],
            n_results=top_k,
        )
        if not results or not results.get("documents"):
            return []

        documents = results["documents"][0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        norm_query = self._normalize(query)
        hits: List[Dict[str, Any]] = []
        for i, doc in enumerate(documents):
            l2 = max(0.0, distances[i] if i < len(distances) else 1.0)
            similarity = max(0.0, min(1.0, 1.0 - (l2 * l2) / 2.0))
            meta = metadatas[i] if i < len(metadatas) else {}
            if meta.get("type") == "qa" and similarity >= threshold:
                hits.append({
                    "question": meta.get("question", doc),
                    "answer": meta.get("answer", ""),
                    "similarity": round(similarity, 4),
                    "created_at": meta.get("created_at"),
                    "exact": self._normalize(meta.get("question", doc)) == norm_query,
                })
        hits.sort(key=lambda h: (h["exact"], h["similarity"]), reverse=True)
        return hits

    def count(self) -> int:
        """当前记忆集合中的条数。"""
        try:
            return chroma_service.get_collection_count(self.MEMORY_COLLECTION)
        except Exception as e:
            logger.error(f"获取记忆条数失败: {e}")
            return 0


memory_service = MemoryService()
