"""Panel Task (Critique).

Functional task for 'Panel' role.
Performs multi-perspective critique (Logic, Ethics, Causal, Performativity).
"""

import logging

from backend.core.registry import TaskRegistry

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
from backend.models.domain import (
    CausalAnalysis,
    FalsifierData,
    OverseerData,
    PerformativityAnalysis,
)

TaskRegistry.register_agent(task_keys=["falsifier"], agent_cls=LogicalFalsifierAgent, output_model=FalsifierData)

TaskRegistry.register_agent(task_keys=["overseer"], agent_cls=FactualOverseerAgent, output_model=OverseerData)

TaskRegistry.register_agent(task_keys=["causal"], agent_cls=CausalAnalystAgent, output_model=CausalAnalysis)

TaskRegistry.register_agent(
    task_keys=["detector"], agent_cls=PerformativityDetectorAgent, output_model=PerformativityAnalysis
)
