import logging

from backend.agents.panel import PanelAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import PanelOutput

logger = logging.getLogger(__name__)


def register_panel_tasks():
    """Registers panel-related agents with the TaskRegistry."""
    logger.info("Registering panel tasks...")

    TaskRegistry.register_agent(
        task_keys=["panel"],
        agent_cls=PanelAgent,
        output_model=PanelOutput
    )

# Execute registration on import
register_panel_tasks()
