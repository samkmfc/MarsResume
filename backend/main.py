"""
简历优化器 — FastAPI 后端入口

架构说明：
  main.py 仅为应用入口，不包含业务逻辑。
  所有功能通过模块化目录组织：
    schemas/       — Pydantic 请求/响应模型
    services/      — 核心业务逻辑（LLM 客户端、Skill Engine）
    middleware/     — 全局异常处理中间件
    utils/         — 工具函数（注入防护、速率限制）
    data/          — 数据持久化
    config.py      — 统一配置管理
"""

import json
import asyncio
import os
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from config import settings
from schemas.request import OptimizeRequest
from schemas.response import ApiResponse
from middleware.exception_handler import GlobalExceptionMiddleware
from services.llm_client import LLMClient
from services.skill_engine import SkillEngine, _build_step3_prompt
from services.file_parser import save_upload, extract_text, cleanup_file, ALLOWED_EXTENSIONS, UPLOAD_DIR
from services.jd_analyzer import JDAnalyzer
from services.docx_editor import apply_replacements, convert_to_pdf
from utils.pdf_generator import generate_resume_pdf
from data.db import storage
from utils.rate_limit import ai_rate_limiter
from utils.ai_utils import sanitize_input

# ── 应用初始化 ────────────────────────────────────────────

app = FastAPI(
    title="简历模块优化器",
    description="基于 Skill 方法论的简历优化 API — 结构化、安全、可扩展",
    version="2.0.0",
)

# ── 中间件 ────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GlobalExceptionMiddleware)

# ── 引擎实例（懒加载） ────────────────────────────────────

_engine = None


def get_engine() -> SkillEngine:
    global _engine
    if _engine is None:
        llm = LLMClient()
        _engine = SkillEngine(llm)
    return _engine

# ── 健康检查 ──────────────────────────────────────────────

@app.get("/api/status")
def get_status():
    """检查服务状态和 API 配置"""
    return ApiResponse.ok({
        "status": "ok",
        "message": "服务运行正常",
        "api_configured": bool(settings.LLM_API_KEY),
        "version": "2.0.0",
    })

# ── 优化核心接口 ──────────────────────────────────────────

@app.post("/api/optimize")
def optimize_resume(req: OptimizeRequest):
    """执行简历优化（支持追问流程）"""

    # 速率限制 — 基于来源 IP
    client_ip = "unknown"
    allowed, remaining = ai_rate_limiter.check(client_ip)
    if not allowed:
        return ApiResponse.fail(
            error=f"请求过于频繁，请 {remaining} 秒后再试",
            meta={"retry_after": remaining},
        )

    eng = get_engine()
    result = eng.optimize(
        resume_text=req.resume_text,
        section_type=req.section_type,
        section_content=req.section_content,
        user_answers=req.user_answers,
    )

    # 如果有最终结果，存到历史
    if not result.get("need_answers") and result.get("final_text"):
        storage.save_optimization(
            section_type=req.section_type,
            original_text=req.section_content,
            optimized_text=result["final_text"],
            changes_summary=result.get("changes_summary", []),
        )

    return ApiResponse.ok(data=result, meta={"rate_limit_remaining": remaining})


# ── 流式优化接口（SSE） ──────────────────────────────────

@app.post("/api/optimize/stream")
async def optimize_resume_stream(req: OptimizeRequest):
    """
    流式简历优化 — 通过 SSE 逐步推送各步骤结果
    Event 类型：
      - step1: 深挖分析完成（含追问问题）
      - step2: 亮点识别完成
      - step3: 生成阶段（逐 token 流式推送）
      - step4: 指标检查完成
      - step5: 自检完成
      - done:  全部完成
      - error: 错误
    """

    async def event_stream():
        client_ip = "unknown"
        allowed, remaining = ai_rate_limiter.check(client_ip)
        if not allowed:
            yield f"event: error\ndata: {json.dumps({'error': f'请求过于频繁，请 {remaining} 秒后再试'})}\n\n"
            return

        eng = get_engine()

        # Step 1: 深挖
        try:
            deep_dive = eng.step1_deep_dive(
                req.resume_text, req.section_type, req.section_content,
            )
            yield f"event: step1\ndata: {json.dumps(deep_dive, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': f'深挖分析失败: {str(e)}'})}\n\n"
            return

        # 追问阶段
        if not req.user_answers:
            yield f"event: done\ndata: {json.dumps({'need_answers': True, 'questions': deep_dive.get('questions', []), 'known_info': deep_dive.get('known_info', '')}, ensure_ascii=False)}\n\n"
            return

        # Step 2: 识别亮点
        try:
            highlights = eng.step2_identify_highlights(
                req.resume_text, req.section_type, req.user_answers,
            )
            yield f"event: step2\ndata: {json.dumps(highlights, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': f'亮点识别失败: {str(e)}'})}\n\n"
            return

        # Step 3: 流式生成
        yield "event: step3_start\ndata: {}\n\n"
        prompt_builder = _build_step3_prompt(
            req.resume_text, req.section_type, req.section_content,
            req.user_answers, highlights.get("highlights", []),
        )
        try:
            full_text = ""
            for chunk in eng.llm.chat_stream(
                system_prompt=prompt_builder["system_prompt"],
                user_prompt=prompt_builder["user_prompt"],
                user_data=prompt_builder.get("user_data"),
                temperature=0.4,
            ):
                full_text += chunk
                yield f"event: step3_chunk\ndata: {json.dumps({'chunk': chunk, 'full': full_text}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': f'生成失败: {str(e)}'})}\n\n"
            return

        # Step 4: 指标检查
        try:
            metrics_check = eng.step4_check_metrics(full_text)
            yield f"event: step4\ndata: {json.dumps(metrics_check, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': f'指标检查失败: {str(e)}'})}\n\n"
            return

        final_text = metrics_check.get("fixed_text") or full_text

        # Step 5: 自检
        try:
            self_check = eng.step5_self_check(final_text)
            yield f"event: step5\ndata: {json.dumps(self_check, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': f'自检失败: {str(e)}'})}\n\n"
            return

        if self_check.get("final_version"):
            final_text = self_check["final_version"]

        # 变更摘要
        changes = eng._generate_summary(req.section_content, final_text)

        # 保存历史
        storage.save_optimization(
            section_type=req.section_type,
            original_text=req.section_content,
            optimized_text=final_text,
            changes_summary=changes,
        )

        # 完成
        yield f"event: done\ndata: {json.dumps({'final_text': final_text, 'changes_summary': changes, 'rate_limit_remaining': remaining}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

# ── 模块类型 ──────────────────────────────────────────────

_SUPPORTED_SECTIONS = [
    {"id": "comprehensive_advantage", "name": "综合优势", "description": "个人简介/综合优势/核心能力模块"},
    {"id": "work_experience", "name": "工作经历", "description": "工作经历/职业经历模块"},
    {"id": "project_experience", "name": "项目经验", "description": "项目经验/项目案例模块"},
    {"id": "skills", "name": "技能", "description": "专业技能/技术栈模块"},
]


@app.get("/api/section-types")
def get_section_types():
    """获取支持的模块类型列表"""
    return ApiResponse.ok(data={"sections": _SUPPORTED_SECTIONS})

# ── 历史记录 ──────────────────────────────────────────────

@app.get("/api/history")
def get_history(limit: int = 20):
    """获取优化历史"""
    records = storage.get_history(limit=min(limit, 100))
    return ApiResponse.ok(data={"records": records})

@app.get("/api/history/{opt_id}")
def get_history_item(opt_id: str):
    """获取单条优化记录"""
    record = storage.get_optimization(opt_id)
    if not record:
        return ApiResponse.fail(error="记录未找到")
    return ApiResponse.ok(data=record)

# ── 配置 ──────────────────────────────────────────────────

@app.get("/api/config")
def get_config():
    """获取当前配置状态（不含敏感信息）"""
    return ApiResponse.ok(data={
        "api_configured": bool(settings.LLM_API_KEY),
        "model": settings.LLM_MODEL,
        "base_url": settings.LLM_BASE_URL,
        "rate_limit": settings.AI_RATE_LIMIT,
    })


# ═══════════════════════════════════════════════════════════════
# 文件上传 + JD 对齐 + PDF 导出
# ═══════════════════════════════════════════════════════════════

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """上传简历文件，保留原件用于后续导出"""
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return ApiResponse.fail(error=f"不支持的文件格式: {ext}")
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        return ApiResponse.fail(error="文件过大")
    file_info = save_upload(file_bytes, filename)
    try:
        text = extract_text(file_info["path"], ext)
    except Exception as e:
        cleanup_file(file_info["path"])
        return ApiResponse.fail(error=f"文本提取失败: {str(e)}")
    if not text.strip():
        cleanup_file(file_info["path"])
        return ApiResponse.fail(error="未能从文件中提取到任何文本")
    return ApiResponse.ok(data={
        "file_id": file_info["file_id"],
        "filename": filename,
        "ext": ext,
        "text": text,
        "text_length": len(text),
    })


@app.post("/api/resume/analyze")
def analyze_resume(resume_text: str = Form(...), jd_text: str = Form(...)):
    """简历与 JD 对齐分析，返回逐条修改建议"""
    if not resume_text.strip() or not jd_text.strip():
        return ApiResponse.fail(error="简历文本和职位描述不能为空")
    allowed, remaining = ai_rate_limiter.check("unknown")
    if not allowed:
        return ApiResponse.fail(error=f"请求过于频繁", meta={"retry_after": remaining})
    llm = LLMClient()
    analyzer = JDAnalyzer(llm)
    result = analyzer.analyze(resume_text, jd_text)
    return ApiResponse.ok(data=result, meta={"rate_limit_remaining": remaining})


@app.post("/api/resume/export-pdf")
def export_resume_pdf(
    file_id: str = Form(...),
    ext: str = Form(...),
    replacements_json: str = Form("[]"),
    title: str = Form("简历"),
):
    """
    导出修改后的简历为 PDF。
    - .docx 格式：在原始 Word 文档上精确替换文本，然后通过 Word COM 转 PDF（保留原始排版）
    - 其他格式：用 ReportLab 生成 PDF（文字保留，排版简化）
    """
    import json as _json

    try:
        replacements = _json.loads(replacements_json)
    except _json.JSONDecodeError:
        replacements = []

    # 查找原始文件
    orig_path = UPLOAD_DIR / f"{file_id}{ext}"

    if ext == ".docx" and orig_path.exists():
        # ── Word 原件流程：替换文本 → COM 转 PDF ──
        try:
            out_docx = UPLOAD_DIR / f"{file_id}_modified.docx"
            out_pdf = UPLOAD_DIR / f"{file_id}_export.pdf"

            # 执行替换
            apply_replacements(str(orig_path), replacements, str(out_docx))

            # 转 PDF
            convert_to_pdf(str(out_docx), str(out_pdf))

            with open(out_pdf, "rb") as f:
                pdf_bytes = f.read()

            # 清理临时文件
            cleanup_file(str(out_docx))
            cleanup_file(str(out_pdf))

            return StreamingResponse(
                iter([pdf_bytes]), media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=resume.pdf",
                    "Content-Type": "application/pdf",
                },
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse.fail(error=f"PDF 导出失败: {str(e)}")
    else:
        # ── 降级流程：ReportLab 生成（保留文字，排版简化） ──
        # 将 replacements 应用到文本，再生成 PDF
        text = ""
        p = UPLOAD_DIR / f"{file_id}{ext}"
        if p.exists():
            from services.file_parser import extract_text as _extract
            text = _extract(str(p), ext)

        # 应用替换
        for r in replacements:
            text = text.replace(r.get("original", ""), r.get("suggested", ""))

        sections = _json.loads(_json.dumps([{"heading": "简历内容", "content": text}]))

        try:
            pdf_buf = generate_resume_pdf(title=title, sections=sections)
            return StreamingResponse(
                pdf_buf, media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=resume.pdf",
                    "Content-Type": "application/pdf",
                },
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ApiResponse.fail(error=f"PDF 生成失败: {str(e)}")

# ── 启动 ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 简历优化服务 v2.0 启动于 http://localhost:{settings.SERVER_PORT}")
    print(f"📄 API 文档: http://localhost:{settings.SERVER_PORT}/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVER_PORT, reload=True)