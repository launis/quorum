import logging

from backend.agents.xai import XAIReporterAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import XAIOutput

logger = logging.getLogger(__name__)


def register_reporting_tasks():
    """Registers reporting-related agents with the TaskRegistry."""
    logger.info("Registering reporting tasks...")

    TaskRegistry.register_agent(task_keys=["xai"], agent_cls=XAIReporterAgent, output_model=XAIOutput)


# Execute registration on import
register_reporting_tasks()
