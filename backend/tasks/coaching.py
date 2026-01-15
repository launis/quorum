
from backend.core.registry import TaskRegistry
from backend.agents.coach import CoachAgent
from backend.models.domain import CoachingPlan

# Register
TaskRegistry.register_agent(
    task_keys=["coach"],
    agent_cls=CoachAgent,
    output_model=CoachingPlan
)
