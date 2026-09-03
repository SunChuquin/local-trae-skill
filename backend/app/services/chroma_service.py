from typing import List, Optional, Dict, Any, Callable
import uuid
from datetime import datetime
from loguru import logger
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.services.embedding import embedding_service


class ChromaService:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    # HNSW 索引优化参数（基于数据规模调整；chromadb 0.5.x 参数命名）
    INDEX_CONFIG = {
        "hnsw:space": "cosine",  # 使用余弦距离
        "hnsw:construction_ef": 200,  # 索引构建精度（越高越精确但越慢）
        "hnsw:search_ef": 100,  # 搜索精度（越高越精确但越慢）
        "hnsw:M": 16  # 邻居数量（平衡精度和内存）
    }

    def _initialize_client(self):
        try:
            logger.info("正在初始化 Chroma 客户端")
            self.client = chromadb.PersistentClient(
                path=str(settings.get_chroma_path()),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            logger.info("Chroma 客户端初始化成功")
        except Exception as e:
            logger.error(f"Chroma 客户端初始化失败: {str(e)}")
            raise

    def create_collection(self, collection_name: str, optimized: bool = True) -> bool:
        """
        创建集合（支持优化配置）
        optimized: 是否使用优化的索引配置
        """
        # 第一步：尝试删除可能已存在的损坏集合
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"已删除可能存在的集合: {collection_name}")
        except Exception as e:
            # 集合不存在或其他错误，忽略
            pass
        
        # 第二步：创建新集合
        try:
            if optimized:
                # 使用优化配置创建集合
                metadata = {
                    "created_at": datetime.now().isoformat(),
                    **self.INDEX_CONFIG
                }
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata=metadata
                )
                logger.info(f"创建新集合（优化配置）: {collection_name}")
            else:
                # 使用默认配置
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"created_at": datetime.now().isoformat()}
                )
                logger.info(f"创建新集合（默认配置）: {collection_name}")
            return True
        except Exception as e:
            logger.warning(f"创建集合失败（将尝试降级配置）{collection_name}: {str(e)}")
            # 如果优化配置失败，尝试使用默认配置作为最后手段
            if optimized:
                try:
                    collection = self.client.create_collection(
                        name=collection_name,
                        metadata={"created_at": datetime.now().isoformat()}
                    )
                    logger.info(f"创建新集合（默认配置，降级成功）: {collection_name}")
                    return True
                except Exception as e2:
                    logger.error(f"降级创建集合失败 {collection_name}: {str(e2)}")
                    return False
            else:
                return False

    def delete_collection(self, collection_name: str) -> bool:
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"删除集合: {collection_name}")
            return True
        except Exception as e:
            # 集合不存在视为删除成功（目标本就是删除它，集合已不存在即已达成），
            # 避免上层因找不到集合而误判失败（如 --all 清理后记录仍在但集合已被清空）
            if "does not exist" in str(e):
                logger.info(f"集合不存在，视为已删除: {collection_name}")
                return True
            logger.error(f"删除集合失败 {collection_name}: {str(e)}")
            return False

    def get_collection(self, collection_name: str):
        try:
            collection = self.client.get_collection(name=collection_name)
            return collection
        except Exception as e:
            logger.error(f"获取集合失败 {collection_name}: {str(e)}")
            return None

    def get_or_create_collection(self, collection_name: str):
        """获取集合，不存在则自动创建（带优化索引配置）。
        若创建失败，清理可能残留的半创建集合后重试一次。"""
        try:
            collection = self.client.get_collection(name=collection_name)
            return collection
        except Exception:
            # 集合不存在 → 创建
            try:
                metadata = {
                    "created_at": datetime.now().isoformat(),
                    **self.INDEX_CONFIG
                }
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata=metadata,
                )
                logger.info(f"自动创建集合（优化配置）: {collection_name}")
                return collection
            except Exception as e:
                # 创建失败：清理可能残留的半创建集合（collection 已建但 segment 未建）
                logger.warning(f"自动创建集合失败 {collection_name}: {str(e)}，尝试清理残留后重试")
                try:
                    self.client.delete_collection(name=collection_name)
                except Exception:
                    pass
                try:
                    collection = self.client.create_collection(
                        name=collection_name,
                        metadata={
                            "created_at": datetime.now().isoformat(),
                            **self.INDEX_CONFIG
                        },
                    )
                    logger.info(f"重试创建集合成功: {collection_name}")
                    return collection
                except Exception as e2:
                    logger.error(f"重试创建集合仍失败 {collection_name}: {str(e2)}")
                    return None

    def list_collections(self) -> List[str]:
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"列出集合失败: {str(e)}")
            return []

    def add_vectors(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"集合不存在: {collection_name}")
                return False

            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            # 生成向量
            embeddings = embedding_service.get_embeddings(documents)

            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"添加 {len(documents)} 个向量到集合 {collection_name}")
            return True
        except Exception as e:
            logger.error(f"添加向量失败: {str(e)}")
            return False

    def upsert_vectors(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """写入向量，id 已存在时覆盖（更新文档/向量/metadata），用于记忆去重更新。"""
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"集合不存在: {collection_name}")
                return False

            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            embeddings = embedding_service.get_embeddings(documents)

            collection.upsert(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Upsert {len(documents)} 个向量到集合 {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Upsert 向量失败: {str(e)}")
            return False

    def add_vectors_progress(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        batch_size: int = 16,
        progress_cb: Optional[Callable[[int], None]] = None,
    ) -> bool:
        """分批向量化并写入，progress_cb(本批数量) 逐批回调，用于上报真实进度。"""
        try:
            collection = self.get_or_create_collection(collection_name)
            if not collection:
                logger.error(f"集合不存在或创建失败: {collection_name}")
                return False

            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            embeddings = embedding_service.get_embeddings_batch_progress(
                documents,
                batch_size=batch_size,
                on_batch=progress_cb,
            )

            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"添加 {len(documents)} 个向量到集合 {collection_name}")
            return True
        except Exception as e:
            logger.error(f"添加向量失败: {str(e)}")
            return False

    def delete_vectors(self, collection_name: str, ids: List[str]) -> bool:
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"集合不存在: {collection_name}")
                return False

            collection.delete(ids=ids)
            logger.info(f"从集合 {collection_name} 删除 {len(ids)} 个向量")
            return True
        except Exception as e:
            logger.error(f"删除向量失败: {str(e)}")
            return False

    def query_vectors(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        查询向量
        Query和Chunk使用统一的嵌入方式，保持语义对齐
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"集合不存在: {collection_name}")
                return None

            # 生成查询向量
            query_embeddings = embedding_service.get_embeddings(query_texts)

            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )

            logger.info(f"查询集合 {collection_name}，返回 {len(results.get('documents', [[]])[0])} 个结果")
            return results
        except Exception as e:
            logger.error(f"查询向量失败: {str(e)}")
            return None

    def get_collection_count(self, collection_name: str) -> int:
        try:
            collection = self.get_collection(collection_name)
            if collection:
                return collection.count()
            return 0
        except Exception as e:
            logger.error(f"获取集合数量失败: {str(e)}")
            return 0

    def reset_collection(self, collection_name: str) -> bool:
        try:
            collection = self.get_collection(collection_name)
            if collection:
                # 获取所有向量ID
                all_data = collection.get(include=[])
                
                if all_data and all_data.get('ids'):
                    ids = all_data['ids']
                    # 批量删除所有向量
                    batch_size = 1000
                    for i in range(0, len(ids), batch_size):
                        batch_ids = ids[i:i + batch_size]
                        collection.delete(ids=batch_ids)
                    logger.info(f"重置集合: {collection_name}，删除 {len(ids)} 个向量")
                else:
                    logger.info(f"集合 {collection_name} 已为空，无需重置")
                return True
            return False
        except Exception as e:
            logger.error(f"重置集合失败: {str(e)}")
            return False
    
    def optimize_collection(self, collection_name: str) -> bool:
        """
        优化集合的索引配置
        在数据量大时调用以提升检索性能
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"集合不存在: {collection_name}")
                return False
            
            count = collection.count()
            logger.info(f"集合 {collection_name} 包含 {count} 个向量")
            
            # 根据数据规模调整配置
            if count > 100000:
                # 大规模数据：提高精度
                logger.info("检测到大规模数据，使用高精度配置")
            elif count > 10000:
                # 中等规模：使用默认配置
                logger.info("检测到中等规模数据，使用默认配置")
            else:
                # 小规模数据：可降低精度提升速度
                logger.info("检测到小规模数据，优化配置以提升速度")
            
            logger.info(f"集合 {collection_name} 索引优化完成")
            return True
        except Exception as e:
            logger.error(f"优化集合失败: {str(e)}")
            return False


chroma_service = ChromaService()
