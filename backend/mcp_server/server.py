"""
MCP Server — expose MarsResume capabilities via Model Context Protocol.
Supports both stdio (Claude Desktop) and SSE (HTTP) transports.
Uses mcp SDK v2 API with callback handlers.
"""

import json
import os
import sys
from typing import Any

# Add backend root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server import Server
from mcp.types import (
    CallToolResult,
    GetPromptResult,
    ListPromptsResult,
    ListResourcesResult,
    ListToolsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    ReadResourceResult,
    Resource,
    TextContent,
    TextResourceContents,
    Tool,
)

# ═══════════════════════════════════════════════════════════════
# Tool implementations
# ═══════════════════════════════════════════════════════════════


def _parse_resume(args: dict) -> str:
    from services.file_parser import extract_text

    file_path = args["file_path"]
    ext = os.path.splitext(file_path)[1].lower()
    text = extract_text(file_path, ext)
    return json.dumps({
        "file_path": file_path,
        "ext": ext,
        "text": text,
        "text_length": len(text),
    }, ensure_ascii=False)


def _analyze_resume_jd(args: dict) -> str:
    from services.llm_client import LLMClient
    from services.jd_analyzer import JDAnalyzer

    llm = LLMClient()
    analyzer = JDAnalyzer(llm)
    result = analyzer.analyze(args["resume_text"], args["jd_text"])
    return json.dumps(result, ensure_ascii=False)


def _optimize_resume_section(args: dict) -> str:
    from services.llm_client import LLMClient
    from services.skill_engine import SkillEngine

    llm = LLMClient()
    engine = SkillEngine(llm)
    result = engine.optimize(
        args["resume_text"],
        args["section_type"],
        args["section_content"],
        args.get("user_answers"),
    )
    return json.dumps(result, ensure_ascii=False)


def _export_resume_pdf(args: dict) -> str:
    from pathlib import Path

    from services.docx_editor import apply_replacements, convert_to_pdf
    from services.file_parser import UPLOAD_DIR, cleanup_file
    from utils.pdf_generator import generate_resume_pdf

    file_id = args["file_id"]
    ext = args["ext"]
    replacements = args["replacements"]
    title = args.get("title", "简历")

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


def _get_optimization_history(args: dict) -> str:
    from data.db import storage

    limit = min(args.get("limit", 20), 100)
    records = storage.get_history(limit=limit)
    return json.dumps({"records": records}, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# Tool definitions
# ═══════════════════════════════════════════════════════════════

TOOLS: dict[str, tuple[Tool, callable]] = {
    "parse_resume": (
        Tool(
            name="parse_resume",
            description="Parse a resume file and extract text content",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the resume file (.pdf, .docx, .png, .jpg)",
                    }
                },
                "required": ["file_path"],
            },
        ),
        _parse_resume,
    ),
    "analyze_resume_jd": (
        Tool(
            name="analyze_resume_jd",
            description="Analyze resume against a job description and return suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "resume_text": {"type": "string", "description": "Full resume text"},
                    "jd_text": {"type": "string", "description": "Job description text"},
                },
                "required": ["resume_text", "jd_text"],
            },
        ),
        _analyze_resume_jd,
    ),
    "optimize_resume_section": (
        Tool(
            name="optimize_resume_section",
            description="Optimize a specific section of the resume",
            inputSchema={
                "type": "object",
                "properties": {
                    "resume_text": {"type": "string", "description": "Full resume text"},
                    "section_type": {
                        "type": "string",
                        "description": "Section type (综合优势/工作经历/项目经验/技能)",
                    },
                    "section_content": {
                        "type": "string",
                        "description": "Current content of the section",
                    },
                    "user_answers": {
                        "type": "string",
                        "description": "User's supplementary answers (optional)",
                    },
                },
                "required": ["resume_text", "section_type", "section_content"],
            },
        ),
        _optimize_resume_section,
    ),
    "export_resume_pdf": (
        Tool(
            name="export_resume_pdf",
            description="Export optimized resume as PDF",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID from upload"},
                    "ext": {
                        "type": "string",
                        "description": "File extension (.docx, .pdf, .png, .jpg)",
                    },
                    "replacements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "original": {"type": "string"},
                                "suggested": {"type": "string"},
                            },
                        },
                        "description": "List of {original, suggested} replacements",
                    },
                    "title": {"type": "string", "description": "PDF title"},
                },
                "required": ["file_id", "ext", "replacements"],
            },
        ),
        _export_resume_pdf,
    ),
    "get_optimization_history": (
        Tool(
            name="get_optimization_history",
            description="Get optimization history",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max number of records (default 20, max 100)",
                    }
                },
            },
        ),
        _get_optimization_history,
    ),
}


# ═══════════════════════════════════════════════════════════════
# Resource handlers
# ═══════════════════════════════════════════════════════════════

RESOURCES: dict[str, tuple[Resource, callable]] = {
    "resume://history": (
        Resource(
            name="resume://history",
            uri="resume://history",
            description="Get optimization history as a JSON resource",
            mimeType="application/json",
        ),
        lambda: json.dumps(
            {"records": _get_optimization_history({"limit": 20})}, ensure_ascii=False
        ),
    ),
    "resume://status": (
        Resource(
            name="resume://status",
            uri="resume://status",
            description="Get service status",
            mimeType="application/json",
        ),
        lambda: json.dumps(
            {
                "status": "ok",
                "version": "3.0.0",
            },
            ensure_ascii=False,
        ),
    ),
}


# ═══════════════════════════════════════════════════════════════
# Prompt definitions
# ═══════════════════════════════════════════════════════════════

PROMPTS: dict[str, Prompt] = {
    "resume_optimization": Prompt(
        name="resume_optimization",
        description="Standard prompt for resume optimization workflow",
        arguments=[
            PromptArgument(
                name="resume_text",
                description="Optional resume text to pre-fill",
                required=False,
            )
        ],
    ),
}


# ═══════════════════════════════════════════════════════════════
# Server factory
# ═══════════════════════════════════════════════════════════════


def create_server() -> Server:
    """Create and configure the MCP server with all handlers."""

    # mcp SDK v2: list handlers receive (ctx, params) where params is a
    # PaginatedRequestParams, and must return a *Result BaseModel (a bare list
    # is rejected by the runner's _dump_result).
    async def handle_list_tools(_ctx, _params) -> ListToolsResult:
        return ListToolsResult(tools=[t[0] for t in TOOLS.values()])

    async def handle_call_tool(ctx, params) -> CallToolResult:
        name = params.name
        args = params.arguments or {}

        if name not in TOOLS:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                isError=True,
            )

        try:
            _, handler = TOOLS[name]
            result = handler(args)
            return CallToolResult(content=[TextContent(type="text", text=result)])
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {e}")],
                isError=True,
            )

    async def handle_list_resources(_ctx, _params) -> ListResourcesResult:
        return ListResourcesResult(resources=[r[0] for r in RESOURCES.values()])

    async def handle_read_resource(_ctx, params) -> ReadResourceResult:
        uri = params.uri
        if uri not in RESOURCES:
            return ReadResourceResult(
                contents=[TextResourceContents(uri=uri, text=f"Unknown resource: {uri}")]
            )
        _, handler = RESOURCES[uri]
        text = handler()
        return ReadResourceResult(
            contents=[TextResourceContents(uri=uri, text=text, mimeType="application/json")]
        )

    async def handle_list_prompts(_ctx, _params) -> ListPromptsResult:
        return ListPromptsResult(prompts=list(PROMPTS.values()))

    async def handle_get_prompt(_ctx, params) -> GetPromptResult:
        name = params.name
        if name not in PROMPTS:
            return GetPromptResult(messages=[])
        prompt_text = """You are a resume optimization assistant. Follow these steps:

1. Ask the user to upload their resume (PDF, DOCX, or image) and paste the job description.
2. Use `parse_resume` to extract text from the uploaded file.
3. Use `analyze_resume_jd` to get gap analysis between resume and JD.
4. For each section, use `optimize_resume_section` to generate improvements.
5. Let the user review and accept/reject each suggestion.
6. Use `export_resume_pdf` to generate the final PDF.

Always explain your reasoning for each suggestion."""
        return GetPromptResult(
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ]
        )

    server = Server(
        "MarsResume",
        version="3.0.0",
        description="AI 简历优化工具 — 上传简历、分析 JD、优化内容、导出 PDF",
        instructions="简历优化助手 — 支持解析简历、JD对齐分析、逐段优化、PDF导出",
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
        on_list_resources=handle_list_resources,
        on_read_resource=handle_read_resource,
        on_list_prompts=handle_list_prompts,
        on_get_prompt=handle_get_prompt,
    )
    return server