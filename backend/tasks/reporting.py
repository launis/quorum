from backend.agents.xai import XAIReporterAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import XAIOutput

# Register
TaskRegistry.register_agent(task_keys=["xai"], agent_cls=XAIReporterAgent, output_model=XAIOutput)
