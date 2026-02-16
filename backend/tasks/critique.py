"""Panel Task (Critique).

Functional task for 'Panel' role.
Performs multi-perspective critique (Logic, Ethics, Causal, Performativity).
"""

import logging

from backend.agents.critics import (
    CausalAnalystAgent,
    FactualOverseerAgent,
    LogicalFalsifierAgent,
    PerformativityDetectorAgent,
)
from backend.core.registry import TaskRegistry
from backend.models.domain import (
    CausalOutput,
    FalsifierOutput,
    OverseerOutput,
    PerformativityOutput,
)

logger = logging.getLogger(__name__)


def register_critique_tasks():
    """Registers critique-related agents with the TaskRegistry."""
    logger.info("Registering critique tasks...")

    # 1. Falsifier (Logic)
    TaskRegistry.register_agent(
        task_keys=["falsifier"],
        agent_cls=LogicalFalsifierAgent,
        output_model=FalsifierOutput
    )

    # 2. Overseer (Fact)
    TaskRegistry.register_agent(
        task_keys=["overseer"],
        agent_cls=FactualOverseerAgent,
        output_model=OverseerOutput
    )

    # 3. Causal (Cause-Effect)
    TaskRegistry.register_agent(
        task_keys=["causal"],
        agent_cls=CausalAnalystAgent,
        output_model=CausalOutput
    )

    # 4. Detector (Performativity)
    TaskRegistry.register_agent(
        task_keys=["detector"],
        agent_cls=PerformativityDetectorAgent,
        output_model=PerformativityOutput
    )

# Execute registration on import
register_critique_tasks()
