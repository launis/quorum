"""Pre-processing tasks (Y-Funnel Extract)."""

from backend.agents.input_processor import InputProcessorAgent
from backend.core.registry import TaskRegistry
from backend.models.domain.input_processor import InputProcessorOutput


def register_tasks() -> None:
    """Registers pre-processing functional tasks."""
    # V5.1 Refactor: Move logic from API to Agent
    TaskRegistry.register_agent(
        task_keys=["input_processor"],
        agent_cls=InputProcessorAgent,
        output_model=InputProcessorOutput
    )

# Automatically register when imported
register_tasks()
