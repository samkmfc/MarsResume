"""
Agent base class — all agents must inherit from BaseAgent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from services.llm_client import LLMClient


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, llm: LLMClient, name: Optional[str] = None):
        self.llm = llm
        self.name = name or self.__class__.__name__

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent task.

        Args:
            context: Task context with input_data, config, etc.

        Returns:
            Dict with task_id, success, output_data, error, metrics
        """
        pass

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        user_data: Optional[str] = None,
        temperature: float = 0.3,
        response_format: Optional[str] = None,
    ) -> str:
        return self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            user_data=user_data,
            temperature=temperature,
            response_format=response_format,
        )