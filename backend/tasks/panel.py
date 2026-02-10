from backend.agents.panel import PanelAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import PanelOutput

# Register
TaskRegistry.register_agent(task_keys=["panel"], agent_cls=PanelAgent, output_model=PanelOutput)
