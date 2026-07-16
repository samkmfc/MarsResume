"""
LLM 客户端（增强版）
- 支持 OpenAI 兼容接口
- 支持结构化 JSON 输出 (response_format)
- 支持流式输出
- 支持 Prompt 注入防护（fence markers 自动注入）
"""

from openai import OpenAI
from typing import Optional, Generator

from config import settings
from utils.ai_utils import fence_user_data, INJECTION_GUARD


class LLMClient:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_BASE_URL
        self.model = model or settings.LLM_MODEL

        if not self.api_key:
            raise ValueError("未配置 LLM_API_KEY，请在 .env 文件中设置或通过 API 配置")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        user_data: Optional[str] = None,
        temperature: float = 0.3,
        response_format: Optional[str] = None,
    ) -> str:
        """
        调用 LLM 进行对话。

        Args:
            system_prompt: 系统指令（受信任）
            user_prompt: 用户提示词框架（受信任的指令模板）
            user_data: 用户提供的原始数据（不受信任，将被 fence 包裹）
            temperature: 温度参数
            response_format: 响应格式，如 "json_object" 表示 JSON 结构化输出

        Returns:
            LLM 响应的文本内容
        """
        # 构建 messages
        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\n{INJECTION_GUARD}",
            },
        ]

        # 如果提供 user_data，用 fence markers 包裹；否则直接用 user_prompt
        if user_data:
            fenced_data = fence_user_data(user_data)
            messages.append({
                "role": "user",
                "content": f"{user_prompt}\n\n## 用户数据\n{fenced_data}",
            })
        else:
            messages.append({"role": "user", "content": user_prompt})

        # 构建 API 参数
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        # OpenAI 兼容的结构化输出
        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def chat_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        user_data: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Generator[str, None, None]:
        """流式调用 LLM"""
        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\n{INJECTION_GUARD}",
            },
        ]

        if user_data:
            fenced_data = fence_user_data(user_data)
            messages.append({
                "role": "user",
                "content": f"{user_prompt}\n\n## 用户数据\n{fenced_data}",
            })
        else:
            messages.append({"role": "user", "content": user_prompt})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content