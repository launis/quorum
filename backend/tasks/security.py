"""Security Tasks.

Functional tasks for security operations, registered for workflow execution.
"""

import logging

from pydantic import BaseModel, ConfigDict, Field

from backend.core.registry import TaskRegistry
from backend.core.security import sanitize_text

logger = logging.getLogger(__name__)


# --- Class-Based Agent Registration ---

from backend.agents.guard import GuardAgent
from backend.models.domain import TaintedData

# Register the GuardAgent class for the "guard" task key.
# This ensures it runs as a BaseAgent subclass, inheriting metadata injection logic.
TaskRegistry.register_agent(
    task_keys=["guard"],
    agent_cls=GuardAgent,
    output_model=TaintedData
)

