
from backend.core.registry import TaskRegistry
from backend.agents.judge import JudgeAgent
from backend.models.domain import TuomioJaPisteet

# Register
TaskRegistry.register_agent(
    task_keys=["judge"],
    agent_cls=JudgeAgent,
    output_model=TuomioJaPisteet
)
