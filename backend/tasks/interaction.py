import logging

from backend.agents.interaction import InteractionAnalystAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import InteractionAnalysis

logger = logging.getLogger(__name__)


def register_interaction_tasks():
    """Registers interaction-related agents with the TaskRegistry."""
    logger.info("Registering interaction tasks...")

    TaskRegistry.register_agent(
        task_keys=["interaction"],
        agent_cls=InteractionAnalystAgent,
        output_model=InteractionAnalysis
    )

# Execute registration on import
register_interaction_tasks()
