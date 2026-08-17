"""
RAG management routes.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from auth.deps import require_admin, require_user
from services.rag_service import rag_service

router = APIRouter(prefix="/api/rag", tags=["rag"])


class AddExampleRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None


class AddJDRequest(BaseModel):
    jd_text: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None


@router.post("/add-example")
async def add_example(req: AddExampleRequest, _admin=Depends(require_admin)):
    """Add a resume example to the knowledge base (admin only)."""
    if not rag_service.enabled:
        return {"success": False, "data": None, "error": {"code": "RAG_ERROR", "message": "RAG 服务未启用"}, "meta": {}}
    ok = rag_service.add_resume_example(req.text, req.metadata)
    return {"success": ok, "data": {"added": ok}, "error": None, "meta": {}}


@router.post("/add-jd-template")
async def add_jd_template(req: AddJDRequest, _admin=Depends(require_admin)):
    """Add a JD template to the knowledge base (admin only)."""
    if not rag_service.enabled:
        return {"success": False, "data": None, "error": {"code": "RAG_ERROR", "message": "RAG 服务未启用"}, "meta": {}}
    ok = rag_service.add_jd_template(req.jd_text, req.metadata)
    return {"success": ok, "data": {"added": ok}, "error": None, "meta": {}}


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    type: str = Query("resume_examples", alias="type"),
    top_k: int = Query(5, ge=1, le=20),
    _user=Depends(require_user),
):
    """Search the knowledge base (authenticated)."""
    results = rag_service.search_similar(q, type, top_k=top_k)
    return {"success": True, "data": {"results": results}, "error": None, "meta": {}}


@router.get("/stats")
async def stats(_user=Depends(require_user)):
    """Get knowledge base statistics (authenticated)."""
    return {"success": True, "data": rag_service.get_stats(), "error": None, "meta": {}}