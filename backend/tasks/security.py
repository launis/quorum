import logging

from backend.agents.guard import GuardAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import GuardOutput

logger = logging.getLogger(__name__)


def register_security_tasks():
    """Registers security-related agents with the TaskRegistry."""
    logger.info("Registering security tasks...")

    TaskRegistry.register_agent(
        task_keys=["guard"],
        agent_cls=GuardAgent,
        output_model=GuardOutput
    )

# Execute registration on import
register_security_tasks()

