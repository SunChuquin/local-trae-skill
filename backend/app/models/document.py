from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    MARKDOWN = "md"
    TEXT = "txt"
    PDF = "pdf"
    DOCX = "docx"


class DocumentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="文档名称")
    content: Optional[str] = Field(None, description="文档内容")
    document_type: DocumentType = Field(default=DocumentType.MARKDOWN, description="文档类型")


class DocumentCreate(DocumentBase):
    knowledge_base_id: str = Field(..., description="所属知识库ID")
    content: str = Field(..., description="文档内容")


class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None


class Document(DocumentBase):
    id: str = Field(..., description="文档唯一标识")
    knowledge_base_id: str = Field(..., description="所属知识库ID")
    file_path: Optional[str] = Field(None, description="文件路径")
    size: int = Field(default=0, description="文件大小（字节）")
    chunk_count: int = Field(default=0, description="分块数量")
    vector_count: int = Field(default=0, description="向量数量")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class DocumentContent(BaseModel):
    id: str
    name: str
    content: str
    document_type: DocumentType
    created_at: datetime


class DocumentResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Document] = None


class DocumentListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[Document] = []
    total: int = 0
