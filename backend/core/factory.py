from typing import Dict
from backend.agents.base import BaseAgent
from backend.agents.guard import GuardAgent
from backend.agents.analyst import AnalystAgent
from backend.agents.interaction import InteractionAnalystAgent
from backend.agents.profiler import ProfilerAgent
from backend.agents.logician import LogicianAgent
from backend.agents.critics import (
    LogicalFalsifierAgent,
    FactualOverseerAgent,
    CausalAnalystAgent,
    PerformativityDetectorAgent
)
from backend.agents.archivist import ArchivistAgent
from backend.agents.judge import JudgeAgent
from backend.agents.coach import CoachAgent
from backend.agents.xai import XAIReporterAgent
from backend.agents.panel import PanelAgent

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
        # Explicitly map ClassName -> Instance
        # This ensures that if a class is renamed or deleted, this file breaks immediately (good).
        return {
            "GuardAgent": GuardAgent(model=initial_model),
            "AnalystAgent": AnalystAgent(model=initial_model),
            "InteractionAnalystAgent": InteractionAnalystAgent(model=initial_model),
            "ProfilerAgent": ProfilerAgent(model=initial_model),
            "LogicianAgent": LogicianAgent(model=initial_model),
            "LogicalFalsifierAgent": LogicalFalsifierAgent(model=initial_model),
            "FactualOverseerAgent": FactualOverseerAgent(model=initial_model),
            "CausalAnalystAgent": CausalAnalystAgent(model=initial_model),
            "PerformativityDetectorAgent": PerformativityDetectorAgent(model=initial_model),
            "ArchivistAgent": ArchivistAgent(model=initial_model),
            "JudgeAgent": JudgeAgent(model=initial_model),
            "CoachAgent": CoachAgent(model=initial_model),
            "XAIReporterAgent": XAIReporterAgent(model=initial_model),
            "PanelAgent": PanelAgent(model=initial_model)
        }
