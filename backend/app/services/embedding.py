import os

# 在导入任何 Hugging Face 库之前设置镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from typing import Callable, List, Optional, Union
import threading
import numpy as np
from loguru import logger
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.config import settings
from app.services.vector_utils import vector_utils


class EmbeddingService:
    def __init__(self):
        self.model: Optional[HuggingFaceEmbedding] = None
        # 全局推理锁：任何时刻只允许一个向量化计算运行。
        # CPU 环境下若多个文档并发向量化，PyTorch 线程过度订阅会把整机卡死。
        self._infer_lock = threading.Lock()
        self._initialize_model()
    
    # BAAI/bge-large-zh-v1.5 官方推荐的 prompt 模板
    QUERY_PROMPT = "为这个片段生成表示用于检索相关文章：{query}"
    LEGACY_PROMPT = "represent the document for retrieval:"

    def _initialize_model(self):
        try:
            logger.info(f"正在加载嵌入模型: {settings.embedding_model}")
            logger.info("使用国内镜像: https://hf-mirror.com")

            self.model = HuggingFaceEmbedding(
                model_name=settings.embedding_model,
                device=settings.embedding_device,
            )
            logger.info("嵌入模型加载成功")
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {str(e)}")
            logger.warning("如果下载失败，请检查网络连接或配置代理")
            raise

    def get_embedding(self, text: str, text_type: str = "chunk") -> List[float]:
        """
        生成嵌入向量
        text_type: "query" 或 "chunk"
        注意：BGE模型本身已针对检索优化，不建议添加额外prompt
        Query和Chunk使用统一的文本预处理，保持语义对齐
        """
        if not self.model:
            raise RuntimeError("嵌入模型未初始化")

        try:
            # 预处理文本（Query和Chunk使用相同的处理方式）
            processed_text = vector_utils.preprocess_for_chunk(text)
            
            with self._infer_lock:  # 串行推理，避免并发打满 CPU
                embedding = self.model.get_text_embedding(processed_text)
            return self._normalize(embedding)
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {str(e)}")
            raise

    def get_embeddings(self, texts: List[str], text_type: str = "chunk") -> List[List[float]]:
        """
        批量生成嵌入向量
        Query和Chunk使用统一的文本预处理
        """
        if not self.model:
            raise RuntimeError("嵌入模型未初始化")

        try:
            # 批量预处理（Query和Chunk使用相同的处理方式）
            processed_texts = [vector_utils.preprocess_for_chunk(text) for text in texts]
            
            with self._infer_lock:  # 串行推理，避免并发打满 CPU
                embeddings = self.model.get_text_embedding_batch(processed_texts)
            return [self._normalize(emb) for emb in embeddings]
        except Exception as e:
            logger.error(f"批量生成嵌入向量失败: {str(e)}")
            raise

    def get_embeddings_batch_progress(
        self,
        texts: List[str],
        batch_size: int = 16,
        on_batch: Optional[Callable[[int], None]] = None,
    ) -> List[List[float]]:
        """分批向量化，并在每批完成后回调 on_batch(本批数量)，用于上报进度。"""
        if not texts:
            return []
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            all_embeddings.extend(self.get_embeddings(batch))
            if on_batch:
                on_batch(len(batch))
        return all_embeddings
    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        arr = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr.tolist()

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(cosine_sim)


embedding_service = EmbeddingService()
