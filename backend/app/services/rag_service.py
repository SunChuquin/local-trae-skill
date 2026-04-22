from typing import List, Optional, Dict, Any
from loguru import logger
from app.config import settings
from app.services.chroma_service import chroma_service
from app.services.storage import skill_config_storage, knowledge_base_storage
from app.models.skill import RetrievalResult, RetrievalRequest
from app.services.vector_utils import vector_utils


class RAGService:
    def __init__(self):
        self.default_top_k = settings.default_top_k
        self._cached_threshold: float = settings.default_similarity_threshold
        self.enable_parent_child = True  # 启用父子块增强
        self.parent_chunk_ratio = 2  # 额外检索父块的数量比例

    def _get_kb_id_by_name(self, kb_name: str) -> Optional[str]:
        """根据知识库名称获取对应的知识库ID"""
        try:
            all_kbs = knowledge_base_storage.get_all()
            for kb_id, kb_data in all_kbs.items():
                if kb_data.get('name') == kb_name:
                    return kb_id
            logger.warning(f"未找到名称 '{kb_name}' 对应的知识库")
            return None
        except Exception as e:
            logger.error(f"根据名称查找知识库失败: {e}")
            return None

    def _get_threshold(self) -> float:
        try:
            config_data = skill_config_storage.get("default")
            if config_data and "similarity_threshold" in config_data:
                threshold = float(config_data["similarity_threshold"])
                if threshold != self._cached_threshold:
                    self._cached_threshold = threshold
                    logger.info(f"从配置读取新阈值: {threshold}")
                return threshold
        except Exception as e:
            logger.warning(f"读取阈值配置失败，使用默认值: {e}")
        return self._cached_threshold

    def _get_top_k(self, top_k: int) -> int:
        try:
            config_data = skill_config_storage.get("default")
            if config_data and "top_k" in config_data and top_k is None:
                return int(config_data["top_k"])
        except Exception:
            pass
        return top_k or self.default_top_k

    def _get_parent_chunks(
        self,
        child_ids: List[str],
        collection_name: str
    ) -> List[Dict[str, Any]]:
        """
        获取子块对应的父块内容
        增强上下文完整性
        """
        if not child_ids or not self.enable_parent_child:
            return []
        
        try:
            collection = chroma_service.get_collection(collection_name)
            if not collection:
                return []
            
            # 获取所有父块
            all_data = collection.get(
                include=["documents", "metadatas"],
                where={"is_parent": True}
            )
            
            parent_chunks = []
            for i, metadata in enumerate(all_data.get("metadatas", [])):
                if metadata.get("is_parent"):
                    parent_ids = metadata.get("child_ids", [])
                    # 检查是否与检索到的子块相关
                    if any(child_id in parent_ids for child_id in child_ids):
                        parent_chunks.append({
                            "content": all_data["documents"][i],
                            "metadata": metadata,
                            "child_ids": parent_ids
                        })
            
            return parent_chunks
            
        except Exception as e:
            logger.error(f"获取父块失败: {str(e)}")
            return []

    def retrieve(
        self,
        query: str,
        knowledge_base_name: Optional[str] = None,
        top_k: int = None
    ) -> List[RetrievalResult]:
        top_k = self._get_top_k(top_k)
        threshold = self._get_threshold()

        logger.info('========== 检索开始 ==========');
        logger.info(f'原始查询: {query}');
        logger.info(f'top_k: {top_k}, threshold: {threshold}');

        try:
            processed_query = vector_utils.preprocess_for_chunk(query)
            logger.info(f'预处理后查询: {processed_query}');
            
            if knowledge_base_name:
                kb_id = self._get_kb_id_by_name(knowledge_base_name)
                if kb_id:
                    collection_names = [kb_id]
                    logger.info(f"将知识库名称 '{knowledge_base_name}' 映射到ID: {kb_id}")
                else:
                    collection_names = [knowledge_base_name]
                    logger.warning(f"未找到知识库 '{knowledge_base_name}' 的ID，直接使用名称作为集合名")
            else:
                collection_names = chroma_service.list_collections()

            if not collection_names:
                logger.warning("没有找到任何知识库")
                return []

            all_results = []
            retrieved_child_ids = []  # 记录检索到的子块ID

            for collection_name in collection_names:
                results = chroma_service.query_vectors(
                    collection_name=collection_name,
                    query_texts=[query],
                    n_results=top_k
                )

                if results and results.get('documents'):
                    documents = results['documents'][0]
                    metadatas = results.get('metadatas', [[]])[0]
                    distances = results.get('distances', [[]])[0]

                    logger.info(f"集合 {collection_name}: 原始距离值={distances}")

                    for i, doc_content in enumerate(documents):
                        raw_distance = distances[i] if i < len(distances) else 1.0
                        l2_distance = max(0.0, raw_distance)
                        cosine_similarity = 1.0 - (l2_distance * l2_distance) / 2.0
                        similarity = max(0.0, min(1.0, cosine_similarity))

                        logger.info(f"结果{i}: l2_dist={l2_distance:.4f}, cos_sim={similarity:.4f}, threshold={threshold}")

                        metadata = metadatas[i] if i < len(metadatas) else {}
                        
                        # 记录子块ID
                        chunk_id = metadata.get("id", "")
                        if chunk_id:
                            retrieved_child_ids.append(chunk_id)

                        result = RetrievalResult(
                            document_id=metadata.get("document_id", ""),
                            document_name=metadata.get("document_name", "未知文档"),
                            content=doc_content,
                            similarity=round(similarity, 4),
                            metadata=metadata
                        )
                        all_results.append(result)
            
            # 增强：获取父块上下文
            if self.enable_parent_child and retrieved_child_ids:
                for collection_name in collection_names:
                    parent_chunks = self._get_parent_chunks(
                        retrieved_child_ids,
                        collection_name
                    )
                    
                    # 添加父块到结果
                    for parent in parent_chunks:
                        metadata = parent.get("metadata", {})
                        
                        # 检查是否已添加
                        parent_id = metadata.get("id", "")
                        if any(r.metadata.get("id") == parent_id for r in all_results):
                            continue
                        
                        parent_result = RetrievalResult(
                            document_id=metadata.get("document_id", ""),
                            document_name=metadata.get("document_name", "未知文档"),
                            content=parent["content"],
                            similarity=0.85,  # 父块相似度略低
                            metadata={
                                **metadata,
                                "is_parent": True,
                                "is_context_enhanced": True
                            }
                        )
                        all_results.append(parent_result)
                        
                        logger.info(f"添加父块上下文: {parent_id}")

            all_results.sort(key=lambda x: x.similarity, reverse=True)
            
            filtered_results = [r for r in all_results if r.similarity >= threshold]
            final_results = filtered_results[:top_k]

            logger.info(f"检索完成: 共{len(all_results)}条原始结果, 阈值{threshold}过滤后{len(filtered_results)}条, 返回{len(final_results)}条")
            logger.info('========== 检索结束 ==========');
            
            for i, result in enumerate(final_results[:3]):
                logger.info(f"Top{i+1}: {result.document_name} - 相似度={result.similarity:.4f} - 内容预览: {result.content[:100]}...");
            
            return final_results

        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            logger.info('========== 检索结束 ==========');
            return []

    def hybrid_retrieve(
        self,
        query: str,
        knowledge_base_name: Optional[str] = None,
        top_k: int = None
    ) -> List[RetrievalResult]:
        return self.retrieve(query, knowledge_base_name, top_k)


rag_service = RAGService()
