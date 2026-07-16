"""
文件解析服务 — 支持 PDF / Word / PNG 格式的文本提取
- PDF: PyMuPDF 提取文字层，无文字层时自动 OCR
- Word: python-docx 提取段落
- 图片: 使用 EasyOCR / Pillow 进行 OCR
"""

import os
import uuid
from pathlib import Path
from typing import Optional

# PDF
import fitz  # PyMuPDF

# Word
from docx import Document

# 图片
from PIL import Image

from config import settings

# ── 支持的文件类型 ──

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"


def _ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file_bytes: bytes, filename: str) -> dict:
    """
    保存上传文件到本地，返回文件信息。
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}，支持: {', '.join(ALLOWED_EXTENSIONS.keys())}")

    _ensure_upload_dir()
    file_id = uuid.uuid4().hex[:12]
    safe_name = f"{file_id}{ext}"
    save_path = UPLOAD_DIR / safe_name

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    return {
        "file_id": file_id,
        "filename": filename,
        "path": str(save_path),
        "size": len(file_bytes),
        "ext": ext,
    }


def extract_text(file_path: str, ext: str) -> str:
    """
    根据文件类型提取文本。
    """
    ext = ext.lower()
    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_path)
    elif ext in (".png", ".jpg", ".jpeg"):
        return _extract_image(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


def _extract_pdf(file_path: str) -> str:
    """从 PDF 提取文本，无文字层时尝试 OCR"""
    doc = fitz.open(file_path)
    text_parts = []
    need_ocr_pages = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text().strip()
        if page_text and len(page_text) > 20:
            text_parts.append(f"--- 第 {page_num + 1} 页 ---\n{page_text}")
        else:
            need_ocr_pages.append(page_num)

    # 如果有页面需要 OCR，尝试用 EasyOCR
    if need_ocr_pages:
        ocr_text = _ocr_pdf_pages(doc, need_ocr_pages)
        if ocr_text:
            text_parts.append(ocr_text)

    doc.close()
    return "\n\n".join(text_parts) if text_parts else ""


def _ocr_pdf_pages(doc: fitz.Document, page_nums: list[int]) -> str:
    """对 PDF 指定页面进行 OCR"""
    try:
        from easyocr import Reader
        reader = Reader(["ch_sim", "en"], gpu=False)
        texts = []
        for pn in page_nums:
            page = doc[pn]
            # 渲染为图片
            pix = page.get_pixmap(dpi=200)
            img_path = UPLOAD_DIR / f"_ocr_temp_{pn}.png"
            pix.save(str(img_path))
            # OCR
            result = reader.readtext(str(img_path), detail=0)
            img_path.unlink(missing_ok=True)
            if result:
                texts.append(f"--- 第 {pn + 1} 页（OCR）---\n" + "\n".join(result))
        return "\n\n".join(texts)
    except ImportError:
        return f"\n[OCR 引擎未安装，跳过第 {', '.join(str(p+1) for p in page_nums)} 页 OCR]\n"
    except Exception as e:
        return f"\n[OCR 处理失败: {e}]\n"


def _extract_docx(file_path: str) -> str:
    """从 Word 文档提取文本"""
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def _extract_image(file_path: str) -> str:
    """从图片提取文本（OCR）"""
    try:
        from easyocr import Reader
        reader = Reader(["ch_sim", "en"], gpu=False)
        result = reader.readtext(file_path, detail=0)
        return "\n".join(result) if result else ""
    except ImportError:
        # 回退：尝试使用 pytesseract
        try:
            import pytesseract
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="chi_sim+eng")
            return text.strip()
        except ImportError:
            return "[OCR 引擎未安装，无法提取图片文字]\n"


def cleanup_file(file_path: str):
    """删除临时文件"""
    try:
        Path(file_path).unlink(missing_ok=True)
    except Exception:
        pass