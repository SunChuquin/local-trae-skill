"""剔除预览 API：查看上传文档"剔除前/后"文本，供用户检查页眉页脚剔除是否正确。"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from app.utils.logger import logger

router = APIRouter(prefix="/api/clean-preview", tags=["clean-preview"])

# 与 document.py 中 CLEAN_PREVIEW_DIR 保持一致（相对 backend 目录）
CLEAN_PREVIEW_DIR = Path("./data/temp_clean")


def _safe_name(name: str) -> str:
    """去掉路径分隔符，防止路径穿越。"""
    return Path(name).name


@router.get("/list")
async def list_clean_previews():
    """列出所有可对比的 PDF 剔除预览（按更新时间倒序）。"""
    if not CLEAN_PREVIEW_DIR.exists():
        return {"code": 200, "message": "success", "data": [], "total": 0}
    items = []
    for f in sorted(CLEAN_PREVIEW_DIR.glob("*.cleaned.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        name = f.name[: -len(".cleaned.md")]
        items.append({
            "name": name,
            "size": f.stat().st_size,
            "updated_at": f.stat().st_mtime,
        })
    logger.info(f"列出剔除预览: {len(items)} 个")
    return {"code": 200, "message": "success", "data": items, "total": len(items)}


@router.get("/content")
async def get_clean_preview(
    name: str = Query(..., description="文件名（不含后缀）"),
    kind: str = Query("cleaned", description="cleaned=剔除后 / original=剔除前"),
):
    """返回单个文件的剔除前或剔除后文本。"""
    if kind not in ("original", "cleaned"):
        raise HTTPException(status_code=400, detail="kind 只能为 original 或 cleaned")
    safe = _safe_name(name)
    suffix = ".original.md" if kind == "original" else ".cleaned.md"
    target = CLEAN_PREVIEW_DIR / (safe + suffix)
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"预览文件不存在: {name}（{kind}）")
    content = target.read_text(encoding="utf-8", errors="replace")
    return {
        "code": 200,
        "message": "success",
        "data": {"name": safe, "kind": kind, "content": content},
    }
