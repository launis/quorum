
from backend.core.registry import TaskRegistry
from backend.agents.interaction import InteractionAnalystAgent
from backend.models.domain import InteractionAnalysis

# Register
TaskRegistry.register_agent(
    task_keys=["interaction"],
    agent_cls=InteractionAnalystAgent,
    output_model=InteractionAnalysis
)
