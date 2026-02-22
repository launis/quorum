import logging

from backend.agents.judge import JudgeAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import EvaluationResult

logger = logging.getLogger(__name__)


def register_judgment_tasks():
    """Registers judgment-related agents with the TaskRegistry."""
    logger.info("Registering judgment tasks...")

    TaskRegistry.register_agent(task_keys=["judge"], agent_cls=JudgeAgent, output_model=EvaluationResult)


# Execute registration on import
register_judgment_tasks()
