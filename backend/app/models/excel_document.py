from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ChunkMode(str, Enum):
    ROW_LEVEL = "row_level"
    TOPIC_SEMANTIC = "topic_semantic"


class SheetInfo(BaseModel):
    name: str
    row_count: int
    col_count: int
    merged_cells: int


class ExcelDocumentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Excel 文件名称")
    sheet_count: int = Field(default=0, description="Sheet 数量")


class ExcelDocumentCreate(BaseModel):
    knowledge_base_id: str = Field(..., description="所属知识库 ID")


class ExcelDocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    chunk_mode: Optional[ChunkMode] = None


class ExcelDocument(ExcelDocumentBase):
    id: str = Field(..., description="文档唯一标识")
    knowledge_base_id: str = Field(..., description="所属知识库 ID")
    file_path: Optional[str] = Field(None, description="文件路径")
    size: int = Field(default=0, description="文件大小（字节）")
    sheets: List[SheetInfo] = Field(default_factory=list, description="Sheet 信息列表")
    chunk_mode: ChunkMode = Field(default=ChunkMode.ROW_LEVEL, description="分块模式")
    chunk_count: int = Field(default=0, description="分块数量")
    vector_count: int = Field(default=0, description="向量数量")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ChunkPreview(BaseModel):
    chunk_index: int
    content: str
    row_range: Optional[str] = None
    topic: Optional[str] = None


class ParsePreview(BaseModel):
    sheet_name: str
    headers: List[str]
    rows: List[List[str]]
    total_rows: int
    total_cols: int


class ChunkConfig(BaseModel):
    chunk_mode: ChunkMode = Field(default=ChunkMode.ROW_LEVEL, description="分块模式")
    semantic_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="语义分块阈值")
    include_headers: bool = Field(default=True, description="行级分块是否包含表头")
    max_chunk_tokens: Optional[int] = Field(default=None, description="最大分块 token 数")


class ExcelDocumentResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[ExcelDocument] = None


class ExcelDocumentListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[ExcelDocument] = []
    total: int = 0


class ChunkPreviewResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[ChunkPreview] = []
    total: int = 0


class ParsePreviewResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[ParsePreview] = []
