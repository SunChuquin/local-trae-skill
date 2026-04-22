from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeBaseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, max_length=500, description="知识库描述")


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class KnowledgeBase(KnowledgeBaseBase):
    id: str = Field(..., description="知识库唯一标识")
    document_count: int = Field(default=0, description="文档数量")
    vector_count: int = Field(default=0, description="向量数量")
    summary: Optional[str] = Field(None, description="知识库摘要，由AI自动生成")
    summary_updated_at: Optional[datetime] = Field(None, description="摘要更新时间")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        from_attributes = True


class KnowledgeBaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[KnowledgeBase] = None
