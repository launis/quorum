from typing import Dict

from backend.agents.analyst import AnalystAgent
from backend.agents.archivist import ArchivistAgent
from backend.agents.base import BaseAgent
from backend.agents.coach import CoachAgent
from backend.agents.critics import (
    CausalAnalystAgent,
    FactualOverseerAgent,
    LogicalFalsifierAgent,
    PerformativityDetectorAgent,
)
from backend.agents.guard import GuardAgent
from backend.agents.interaction import InteractionAnalystAgent
from backend.agents.judge import JudgeAgent
from backend.agents.logician import LogicianAgent
from backend.agents.panel import PanelAgent
from backend.agents.profiler import ProfilerAgent
from backend.agents.xai import XAIReporterAgent


class AgentFactory:
    """
    Static Factory to explicitly instantiate all available Agents.
    Replaces dynamic discovery to ensure compile-time safety and explicit dependencies.
    """

    @staticmethod
    def create_agents_map(initial_model: str = None) -> Dict[str, BaseAgent]:
        """
        Returns a dictionary of {ClassName: AgentInstance}.
        """
        # Explicitly pass provider="vertex_ai" to ensure robust initialization
        default_provider = "vertex_ai"

        return {
            "GuardAgent": GuardAgent(model=initial_model, provider=default_provider),
            "AnalystAgent": AnalystAgent(model=initial_model, provider=default_provider),
            "InteractionAnalystAgent": InteractionAnalystAgent(model=initial_model, provider=default_provider),
            "ProfilerAgent": ProfilerAgent(model=initial_model, provider=default_provider),
            "LogicianAgent": LogicianAgent(model=initial_model, provider=default_provider),
            "LogicalFalsifierAgent": LogicalFalsifierAgent(model=initial_model, provider=default_provider),
            "FactualOverseerAgent": FactualOverseerAgent(model=initial_model, provider=default_provider),
            "CausalAnalystAgent": CausalAnalystAgent(model=initial_model, provider=default_provider),
            "PerformativityDetectorAgent": PerformativityDetectorAgent(model=initial_model, provider=default_provider),
            "ArchivistAgent": ArchivistAgent(model=initial_model, provider=default_provider),
            "JudgeAgent": JudgeAgent(model=initial_model, provider=default_provider),
            "CoachAgent": CoachAgent(model=initial_model, provider=default_provider),
            "XAIReporterAgent": XAIReporterAgent(model=initial_model, provider=default_provider),
            "PanelAgent": PanelAgent(model=initial_model, provider=default_provider),
        }
