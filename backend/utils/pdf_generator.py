"""
PDF 导出工具 — 使用 ReportLab 生成中文简历 PDF
"""

import os
import tempfile
from pathlib import Path
from io import BytesIO
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib import colors

# ── 查找并注册系统中文 TrueType 字体（模块加载时注册） ──

def _register_font_global():
    """在模块加载时注册中文字体到 ReportLab"""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # 候选字体列表（按优先级）
    candidates = [
        "C:/Windows/Fonts/simkai.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsunb.ttf",
    ]
    for font_path in candidates:
        if os.path.exists(font_path):
            try:
                # TTC 文件需要 subfontIndex
                if font_path.endswith(".ttc"):
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                return True
            except Exception:
                continue
    return False


_FONT_OK = _register_font_global()


def get_font_name() -> str:
    """获取已注册的中文字体名称"""
    _register_font()
    return "ChineseFont"


# ── PDF 生成 ──

def generate_resume_pdf(
    title: str,
    sections: list[dict],
    output_path: Optional[str] = None,
) -> BytesIO:
    """
    生成简历 PDF。

    Args:
        title: 简历标题（姓名等）
        sections: [{"heading": "...", "content": "..."}]
        output_path: 如果提供，保存到文件路径

    Returns:
        BytesIO 对象（或文件路径字符串）
    """
    global _FONT_OK
    if not _FONT_OK:
        _FONT_OK = _register_font_global()
        if not _FONT_OK:
            raise RuntimeError("未找到系统中文字体，请安装中文字体后重试")

    font_name = "ChineseFont"

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    # ── 样式定义 ──
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "ResumeTitle", parent=styles["Title"],
        fontName=font_name, fontSize=22, leading=30,
        alignment=TA_CENTER, spaceAfter=4 * mm,
    )
    style_heading = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"],
        fontName=font_name, fontSize=14, leading=20,
        spaceBefore=6 * mm, spaceAfter=3 * mm,
        textColor=colors.HexColor("#1d4ed8"),
        borderPadding=(0, 0, 2, 0),
    )
    style_body = ParagraphStyle(
        "ResumeBody", parent=styles["Normal"],
        fontName=font_name, fontSize=10.5, leading=16,
        alignment=TA_JUSTIFY, spaceAfter=2 * mm,
    )
    style_bullet = ParagraphStyle(
        "ResumeBullet", parent=style_body,
        leftIndent=8 * mm, bulletIndent=2 * mm,
        spaceBefore=1 * mm, spaceAfter=1 * mm,
    )

    # ── 构建文档 ──
    elements = []

    # 标题
    elements.append(Paragraph(title, style_title))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=colors.HexColor("#1d4ed8"),
        spaceAfter=4 * mm,
    ))

    # 各模块
    for section in sections:
        heading = section.get("heading", "")
        content = section.get("content", "")

        if heading:
            elements.append(Paragraph(heading, style_heading))

        # 将内容按行分割，bullet 行用 bullet 样式
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 2 * mm))
                continue

            # 转义 HTML 特殊字符
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            if line.startswith("●") or line.startswith("-") or line.startswith("•"):
                elements.append(Paragraph(f"&bull; {safe_line[1:].strip()}", style_bullet))
            elif line.startswith("→") or line.startswith(">"):
                elements.append(Paragraph(f"&rarr; {safe_line[1:].strip()}", style_bullet))
            else:
                elements.append(Paragraph(safe_line, style_body))

        elements.append(Spacer(1, 2 * mm))

    # 生成
    doc.build(elements)

    if output_path:
        with open(output_path, "wb") as f:
            f.write(buf.getvalue())
        return output_path

    buf.seek(0)
    return buf