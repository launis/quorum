"""Security Tasks.

Functional tasks for security operations, registered for workflow execution.
"""

import logging

from backend.core.registry import TaskRegistry

logger = logging.getLogger(__name__)


# --- Class-Based Agent Registration ---

from backend.agents.guard import GuardAgent
from backend.models.domain import TaintedDataContent

# Register the GuardAgent class for the "guard" task key.
# This ensures it runs as a BaseAgent subclass, inheriting metadata injection logic.
TaskRegistry.register_agent(
    task_keys=["guard"],
    agent_cls=GuardAgent,
    output_model=TaintedDataContent
)

