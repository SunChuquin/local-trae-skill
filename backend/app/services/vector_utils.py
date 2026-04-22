"""
向量处理工具箱 v2.0
优化特性：
1. 非对称嵌入（Query和Chunk使用不同prompt模板）
2. 统一文本清洗规则
3. 向量稳定性校验
4. 批量处理优化
5. 增量更新支持
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import hashlib
import numpy as np
from loguru import logger


def _get_embedding_service():
    """延迟导入embedding_service，避免循环依赖"""
    from app.services.embedding import embedding_service
    return embedding_service


class VectorUtils:
    """
    向量处理工具类
    提供文本预处理、非对称嵌入、效果校验等功能
    """
    
    # BAAI/bge-large-zh-v1.5 官方推荐的 prompt 模板
    QUERY_PROMPT_TEMPLATE = "为这个片段生成表示用于检索相关文章：{query}"
    CHUNK_PROMPT_TEMPLATE = "{chunk}"  # Chunk 直接使用原始文本
    
    def __init__(self):
        self.vector_cache: Dict[str, List[float]] = {}
        self.max_cache_size = 10000
    
    def preprocess_for_query(self, query: str) -> str:
        """
        Query 预处理（用于检索）
        1. 统一文本清洗
        2. 添加检索 prompt
        """
        cleaned = self._clean_text(query)
        enhanced = self.QUERY_PROMPT_TEMPLATE.format(query=cleaned)
        return enhanced
    
    def preprocess_for_chunk(self, chunk: str) -> str:
        """
        Chunk 预处理（用于编码）
        1. 统一文本清洗
        2. 保持原始语义
        """
        return self._clean_text(chunk)
    
    def _clean_text(self, text: str) -> str:
        """
        统一文本清洗规则
        解决格式、符号、大小写导致的匹配偏差
        """
        if not text:
            return ""
        
        # 1. 规范化空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 2. 去除特殊控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # 3. 规范化标点符号
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('《', '<').replace('》', '>')
        
        # 4. 规范化数字格式
        text = re.sub(r'(\d),(\d)', r'\1\2', text)  # 去除千位分隔符
        
        # 5. 去除首尾空白
        text = text.strip()
        
        # 6. 限制最大长度（嵌入模型通常有 512 token 限制）
        max_chars = 2000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        return text
    
    def get_embedding_with_prompt(
        self,
        text: str,
        text_type: str = "chunk"
    ) -> Optional[List[float]]:
        """
        使用 prompt 模板生成嵌入向量
        text_type: "query" 或 "chunk"
        """
        try:
            if text_type == "query":
                processed_text = self.preprocess_for_query(text)
            else:
                processed_text = self.preprocess_for_chunk(text)
            
            # 使用缓存
            cache_key = self._get_cache_key(processed_text)
            if cache_key in self.vector_cache:
                return self.vector_cache[cache_key]
            
            # 生成向量
            embedding_service = _get_embedding_service()
            embedding = embedding_service.get_embedding(processed_text)
            
            # 更新缓存
            self._update_cache(cache_key, embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {str(e)}")
            return None
    
    def get_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Optional[List[float]]]:
        """
        批量生成嵌入向量
        带进度追踪和异常处理
        """
        results = []
        total = len(texts)
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for text in batch:
                try:
                    # 统一的文本预处理
                    processed = self.preprocess_for_chunk(text)
                    
                    # 检查缓存
                    cache_key = self._get_cache_key(processed)
                    if cache_key in self.vector_cache:
                        batch_results.append(self.vector_cache[cache_key])
                    else:
                        embedding_service = _get_embedding_service()
                        embedding = embedding_service.get_embedding(processed)
                        self._update_cache(cache_key, embedding)
                        batch_results.append(embedding)
                        
                except Exception as e:
                    logger.warning(f"处理文本失败: {str(e)}, text={text[:50]}")
                    batch_results.append(None)
            
            results.extend(batch_results)
            logger.info(f"批量嵌入进度: {min(i + batch_size, total)}/{total}")
        
        return results
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _update_cache(self, key: str, vector: List[float]):
        """更新缓存，保持固定大小"""
        if len(self.vector_cache) >= self.max_cache_size:
            # 清除最老的 20%
            keys_to_remove = list(self.vector_cache.keys())[:int(self.max_cache_size * 0.2)]
            for k in keys_to_remove:
                del self.vector_cache[k]
        
        self.vector_cache[key] = vector
    
    def verify_vector_stability(
        self,
        text: str,
        text_type: str = "chunk",
        iterations: int = 3
    ) -> Dict[str, Any]:
        """
        验证向量生成稳定性
        同一段文本多次生成的向量相似度应 >= 0.99
        """
        if text_type == "query":
            processed = self.preprocess_for_query(text)
        else:
            processed = self.preprocess_for_chunk(text)
        
        embeddings = []
        for _ in range(iterations):
            try:
                embedding_service = _get_embedding_service()
                emb = embedding_service.get_embedding(processed)
                embeddings.append(emb)
            except Exception as e:
                logger.error(f"验证失败: {str(e)}")
                return {
                    "stable": False,
                    "error": str(e),
                    "iterations": iterations,
                    "successful": 0
                }
        
        # 计算相似度
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self._cosine_similarity(embeddings[i], embeddings[j])
                similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        min_similarity = min(similarities) if similarities else 0
        
        return {
            "stable": min_similarity >= 0.99,
            "avg_similarity": avg_similarity,
            "min_similarity": min_similarity,
            "iterations": iterations,
            "similarities": similarities
        }
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(v1, v2) / (norm1 * norm2))
    
    def detect_duplicates(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Tuple[int, int, float]]:
        """
        检测重复或高度相似的分块
        返回: [(index1, index2, similarity), ...]
        """
        duplicates = []
        threshold = 0.95
        
        contents = [c.get('content', '') for c in chunks]
        embeddings = self.get_embeddings_batch(contents)
        
        for i in range(len(embeddings)):
            if embeddings[i] is None:
                continue
            
            for j in range(i + 1, len(embeddings)):
                if embeddings[j] is None:
                    continue
                
                sim = self._cosine_similarity(embeddings[i], embeddings[j])
                if sim >= threshold:
                    duplicates.append((i, j, sim))
        
        return duplicates
    
    def compute_chunk_quality_score(
        self,
        chunk: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估分块质量
        - 长度合理性
        - 语义完整性
        - 上下文相关性
        """
        content = chunk.get('content', '')
        length = len(content)
        
        scores = {}
        
        # 1. 长度评分
        ideal_min = 200
        ideal_max = 1000
        if ideal_min <= length <= ideal_max:
            scores['length'] = 1.0
        elif length < ideal_min:
            scores['length'] = length / ideal_min
        else:
            scores['length'] = max(0.5, 1.0 - (length - ideal_max) / ideal_max)
        
        # 2. 语义完整性评分（是否有完整句子）
        sentence_count = len(re.findall(r'[。！？.!?]+', content))
        expected_sentences = length / 50  # 假设每50字符一个句子
        if sentence_count > 0 and expected_sentences > 0:
            ratio = min(1.0, sentence_count / expected_sentences)
            scores['completeness'] = ratio
        else:
            scores['completeness'] = 0.5
        
        # 3. 上下文评分（是否有文档标题等前缀）
        has_context = '【文档】' in content or '【段落' in content
        scores['context'] = 1.0 if has_context else 0.5
        
        # 综合评分
        overall = sum(scores.values()) / len(scores)
        
        return {
            "overall_score": overall,
            "scores": scores,
            "length": length,
            "recommendations": self._get_quality_recommendations(scores)
        }
    
    def _get_quality_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """根据评分给出改进建议"""
        recommendations = []
        
        if scores.get('length', 1) < 0.7:
            recommendations.append("分块长度不合理，建议调整")
        if scores.get('completeness', 1) < 0.6:
            recommendations.append("语义可能被截断，建议检查分割点")
        if scores.get('context', 1) < 0.7:
            recommendations.append("缺少上下文信息，建议添加文档标题")
        
        if not recommendations:
            recommendations.append("分块质量良好")
        
        return recommendations


vector_utils = VectorUtils()
