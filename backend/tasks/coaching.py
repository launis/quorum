import logging

from backend.agents.coach import CoachAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import CoachingPlan

logger = logging.getLogger(__name__)


def register_coaching_tasks():
    """Registers coaching-related agents with the TaskRegistry."""
    logger.info("Registering coaching tasks...")

    TaskRegistry.register_agent(task_keys=["coach"], agent_cls=CoachAgent, output_model=CoachingPlan)


# Execute registration on import
register_coaching_tasks()
