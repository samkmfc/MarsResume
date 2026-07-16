"""
文件上传 & JD 分析相关 Pydantic 模型
"""

from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="简历文本", min_length=1)
    jd_text: str = Field(..., description="职位描述文本", min_length=1)


class SuggestionItem(BaseModel):
    id: str = Field(..., description="建议唯一标识")
    section: str = Field(..., description="所属模块")
    original: str = Field(..., description="原文片段")
    suggested: str = Field(..., description="建议修改文本")
    reason: str = Field(..., description="修改原因")
    severity: str = Field("medium", description="重要程度: high/medium/low")


class AcceptRejectRequest(BaseModel):
    """采纳/拒绝建议的请求"""
    suggestion_id: str = Field(..., description="建议ID")
    accepted: bool = Field(..., description="是否采纳")


class ExportPdfRequest(BaseModel):
    title: str = Field("个人简历", description="简历标题/姓名")
    sections: list[dict] = Field(..., description="简历模块列表")
    accepted_suggestions: list[SuggestionItem] = Field(default_factory=list, description="已采纳的建议列表")