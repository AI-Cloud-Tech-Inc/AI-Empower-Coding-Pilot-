"""Multi-agent system: 9 specialised agents for autonomous coding."""

from backend.agents.accessibility import AccessibilityAgent
from backend.agents.architect import ArchitectAgent
from backend.agents.base import AgentRole, BaseAgent
from backend.agents.coder import CoderAgent
from backend.agents.devops import DevOpsAgent
from backend.agents.docs import DocsAgent
from backend.agents.performance import PerformanceAgent
from backend.agents.reviewer import ReviewerAgent
from backend.agents.security import SecurityAgent
from backend.agents.tester import TesterAgent

__all__ = [
    "AgentRole",
    "BaseAgent",
    "ArchitectAgent",
    "CoderAgent",
    "TesterAgent",
    "SecurityAgent",
    "DocsAgent",
    "ReviewerAgent",
    "DevOpsAgent",
    "PerformanceAgent",
    "AccessibilityAgent",
]
