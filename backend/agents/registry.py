"""
Agent registry — central registry for all agents.
"""

from typing import Any, Dict, Optional

from services.llm_client import LLMClient
from agents.base import BaseAgent
from agents.deep_dive_agent import DeepDiveAgent
from agents.highlight_agent import HighlightAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent


class AgentRegistry:
    """Registry that manages all agent instances."""

    def __init__(self, llm: LLMClient):
        self._agents: Dict[str, BaseAgent] = {}
        self._register_defaults(llm)

    def _register_defaults(self, llm: LLMClient):
        self.register("deep_dive", DeepDiveAgent(llm))
        self.register("highlight", HighlightAgent(llm))
        self.register("writer", WriterAgent(llm))
        self.register("reviewer", ReviewerAgent(llm))

    def register(self, name: str, agent: BaseAgent):
        self._agents[name] = agent

    def get(self, name: str) -> BaseAgent:
        agent = self._agents.get(name)
        if not agent:
            raise KeyError(f"Agent not found: {name}")
        return agent

    def list(self) -> Dict[str, str]:
        return {name: agent.name for name, agent in self._agents.items()}