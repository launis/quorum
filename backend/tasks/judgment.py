from backend.agents.judge import JudgeAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import EvaluationResult

# Register
TaskRegistry.register_agent(task_keys=["judge"], agent_cls=JudgeAgent, output_model=EvaluationResult)
