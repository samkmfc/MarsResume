"""
MCP Server — expose MarsResume capabilities via Model Context Protocol.
Supports both stdio (Claude Desktop) and SSE (HTTP) transports.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add backend root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP(
    "MarsResume",
    description="AI 简历优化工具 — 上传简历、分析 JD、优化内容、导出 PDF",
)


# ═══════════════════════════════════════════════════════════════
# Tools
# ═══════════════════════════════════════════════════════════════


@mcp.tool()
def parse_resume(file_path: str) -> str:
    """
    Parse a resume file and extract text content.

    Args:
        file_path: Path to the resume file (.pdf, .docx, .png, .jpg)
    """
    from services.file_parser import extract_text

    ext = os.path.splitext(file_path)[1].lower()
    text = extract_text(file_path, ext)
    return json.dumps({
        "file_path": file_path,
        "ext": ext,
        "text": text,
        "text_length": len(text),
    }, ensure_ascii=False)


@mcp.tool()
def analyze_resume_jd(resume_text: str, jd_text: str) -> str:
    """
    Analyze resume against a job description and return suggestions.

    Args:
        resume_text: Full resume text
        jd_text: Job description text
    """
    from services.llm_client import LLMClient
    from services.jd_analyzer import JDAnalyzer

    llm = LLMClient()
    analyzer = JDAnalyzer(llm)
    result = analyzer.analyze(resume_text, jd_text)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def optimize_resume_section(
    resume_text: str,
    section_type: str,
    section_content: str,
    user_answers: Optional[str] = None,
) -> str:
    """
    Optimize a specific section of the resume.

    Args:
        resume_text: Full resume text
        section_type: Section type (综合优势/工作经历/项目经验/技能)
        section_content: Current content of the section
        user_answers: User's supplementary answers (optional)
    """
    from services.llm_client import LLMClient
    from services.skill_engine import SkillEngine

    llm = LLMClient()
    engine = SkillEngine(llm)
    result = engine.optimize(resume_text, section_type, section_content, user_answers)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def export_resume_pdf(
    file_id: str,
    ext: str,
    replacements: List[Dict[str, str]],
    title: str = "简历",
) -> str:
    """
    Export optimized resume as PDF.

    Args:
        file_id: File ID from upload
        ext: File extension (.docx, .pdf, .png, .jpg)
        replacements: List of {original, suggested} replacements
        title: PDF title
    """
    from pathlib import Path
    from services.docx_editor import apply_replacements, convert_to_pdf
    from services.file_parser import UPLOAD_DIR, cleanup_file
    from utils.pdf_generator import generate_resume_pdf

    orig_path = UPLOAD_DIR / f"{file_id}{ext}"

    if ext == ".docx" and orig_path.exists():
        out_docx = UPLOAD_DIR / f"{file_id}_modified.docx"
        out_pdf = UPLOAD_DIR / f"{file_id}_export.pdf"
        apply_replacements(str(orig_path), replacements, str(out_docx))
        convert_to_pdf(str(out_docx), str(out_pdf))
        with open(out_pdf, "rb") as f:
            pdf_bytes = f.read()
        cleanup_file(str(out_docx))
        cleanup_file(str(out_pdf))
        result = {"success": True, "size": len(pdf_bytes), "path": str(out_pdf)}
    else:
        from services.file_parser import extract_text
        text = extract_text(str(orig_path), ext) if orig_path.exists() else ""
        for r in replacements:
            text = text.replace(r.get("original", ""), r.get("suggested", ""))
        sections = [{"heading": title, "content": text}]
        pdf_buf = generate_resume_pdf(title=title, sections=sections)
        result = {"success": True, "size": len(pdf_buf.getvalue()), "format": "reportlab"}

    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def get_optimization_history(limit: int = 20) -> str:
    """
    Get optimization history.

    Args:
        limit: Max number of records (default 20, max 100)
    """
    from data.db import storage
    records = storage.get_history(limit=min(limit, 100))
    return json.dumps({"records": records}, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# Resources
# ═══════════════════════════════════════════════════════════════


@mcp.resource("resume://history")
def history_resource() -> str:
    """Get optimization history as a JSON resource."""
    from data.db import storage
    records = storage.get_history(limit=20)
    return json.dumps({"records": records}, ensure_ascii=False)


@mcp.resource("resume://status")
def status_resource() -> str:
    """Get service status."""
    from config import settings
    return json.dumps({
        "status": "ok",
        "api_configured": bool(settings.LLM_API_KEY),
        "model": settings.LLM_MODEL,
        "version": "3.0.0",
    }, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# Prompts
# ═══════════════════════════════════════════════════════════════


@mcp.prompt()
def resume_optimization_prompt() -> str:
    """Standard prompt for resume optimization workflow."""
    return """You are a resume optimization assistant. Follow these steps:

1. Ask the user to upload their resume (PDF, DOCX, or image) and paste the job description.
2. Use `parse_resume` to extract text from the uploaded file.
3. Use `analyze_resume_jd` to get gap analysis between resume and JD.
4. For each section, use `optimize_resume_section` to generate improvements.
5. Let the user review and accept/reject each suggestion.
6. Use `export_resume_pdf` to generate the final PDF.

Always explain your reasoning for each suggestion."""