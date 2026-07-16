"""
Pydantic 请求模型
"""

from pydantic import BaseModel, Field
from typing import Optional


class OptimizeRequest(BaseModel):
    resume_text: str = Field(..., description="完整简历文本", min_length=1, max_length=10000)
    section_type: str = Field(..., description="要优化的模块类型：综合优势 / 工作经历 / 项目经验 / 技能")
    section_content: str = Field(..., description="该模块的当前内容")
    user_answers: Optional[str] = Field(None, description="用户对追问问题的补充回答", max_length=5000)


class ConfigUpdateRequest(BaseModel):
    llm_api_key: Optional[str] = Field(None, description="LLM API Key")
    llm_base_url: Optional[str] = Field(None, description="LLM API 地址")
    llm_model: Optional[str] = Field(None, description="模型名称")