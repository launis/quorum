"""Panel Task (Critique).

Functional task for 'Panel' role.
Performs multi-perspective critique (Logic, Ethics, Causal, Performativity).
"""

import logging

from pydantic import BaseModel

from backend.core.registry import TaskRegistry
from backend.dependencies import get_async_repository
from backend.llm.client import LLMClient
from backend.models.domain import PanelAudit, TodistusKartta
from backend.services.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)

# Legacy functional 'panel' task removed. 
# The 'panel' task is now exclusively handled by PanelAgent in backend/tasks/panel.py.


# --- Class-Based Critic Registration ---

from backend.agents.critics import (
    CausalAnalystAgent,
    FactualOverseerAgent,
    LogicalFalsifierAgent,
    PerformativityDetectorAgent,
)
from backend.models.domain import EtiikkaJaFakta, KausaalinenAuditointi, LogiikkaAuditointi, PerformatiivisuusAuditointi

TaskRegistry.register_agent(task_keys=["falsifier"], agent_cls=LogicalFalsifierAgent, output_model=LogiikkaAuditointi)

TaskRegistry.register_agent(task_keys=["overseer"], agent_cls=FactualOverseerAgent, output_model=EtiikkaJaFakta)

TaskRegistry.register_agent(task_keys=["causal"], agent_cls=CausalAnalystAgent, output_model=KausaalinenAuditointi)

TaskRegistry.register_agent(
    task_keys=["detector"], agent_cls=PerformativityDetectorAgent, output_model=PerformatiivisuusAuditointi
)
