from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SkillConfig(BaseModel):
    name: str = Field(default="retrieve_personal_private_docs", description="Skill 名称")
    description: str = Field(
        default="仅在提问涉及我的个人私有文档、本地知识库、私人沉淀内容时调用，禁止使用公共知识回答私有内容问题，无关问题禁止调用此工具。",
        description="Skill 描述"
    )
    top_k: int = Field(default=5, ge=1, le=20, description="检索返回的最大结果数")
    similarity_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="相似度阈值")


class SkillMetadata(BaseModel):
    type: str = "function"
    function: Dict[str, Any] = Field(..., description="Function Calling 结构")


class RetrievalResult(BaseModel):
    document_id: str = Field(..., description="文档ID")
    document_name: str = Field(..., description="文档名称")
    content: str = Field(..., description="匹配内容片段")
    similarity: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class RetrievalRequest(BaseModel):
    query: str = Field(..., description="用户查询问题")
    knowledge_base_name: Optional[str] = Field(None, description="指定知识库名称，为空则全库检索")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")


class RetrievalResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[RetrievalResult] = []
    total: int = 0


class SkillConfigResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: SkillConfig = Field(default_factory=SkillConfig)


class SystemHealth(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    chroma_status: str = "connected"
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    knowledge_base_count: int = 0
    total_documents: int = 0
    total_vectors: int = 0
