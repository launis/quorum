from backend.agents.panel import PanelAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import PanelAudit

# Register
TaskRegistry.register_agent(task_keys=["panel"], agent_cls=PanelAgent, output_model=PanelAudit)
