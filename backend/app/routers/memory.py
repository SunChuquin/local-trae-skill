"""问答记忆 API（持久化记忆 - MVP）"""
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.memory_service import memory_service
from app.utils.logger import logger

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemorySaveRequest(BaseModel):
    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="已验证的回答")
    source_note: Optional[str] = Field(None, description="来源备注（可选）")


class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="查询问题")
    top_k: int = Field(default=3, ge=1, le=20)
    threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)


@router.post("/save")
async def save_memory(req: MemorySaveRequest):
    ok = memory_service.save_qa(req.question, req.answer, req.source_note)
    logger.info(f"保存问答记忆: {req.question[:50]} -> {ok}")
    return {
        "code": 200 if ok else 500,
        "message": "保存成功" if ok else "保存失败",
        "data": {"saved": ok},
    }


@router.get("/search")
async def search_memory(query: str, top_k: int = 3, threshold: Optional[float] = None):
    hits = memory_service.search(query, top_k=top_k, threshold=threshold)
    return {
        "code": 200,
        "message": "success",
        "data": hits,
        "total": len(hits),
    }


@router.post("/search")
async def search_memory_post(req: MemorySearchRequest):
    hits = memory_service.search(req.query, top_k=req.top_k, threshold=req.threshold)
    return {
        "code": 200,
        "message": "success",
        "data": hits,
        "total": len(hits),
    }


@router.get("/count")
async def count_memory():
    return {
        "code": 200,
        "message": "success",
        "data": {"count": memory_service.count()},
    }


@router.get("/list")
async def list_memory(limit: int = 100, offset: int = 0):
    records = memory_service.list_all(limit=limit, offset=offset)
    return {
        "code": 200,
        "message": "success",
        "data": records,
        "total": len(records),
    }


@router.delete("/{mem_id}")
async def delete_memory(mem_id: str):
    ok = memory_service.delete(mem_id)
    return {
        "code": 200 if ok else 404,
        "message": "删除成功" if ok else "记忆不存在或删除失败",
        "data": {"deleted": ok},
    }
