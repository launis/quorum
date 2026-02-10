"""Analyst Task.

Functional task for 'Analyst' role.
Generates Hypotheses and RAG evidence needs.
"""

import logging

from backend.core.registry import TaskRegistry
from backend.models.domain import AnalystOutput

logger = logging.getLogger(__name__)


# --- Class-Based Agent Registration ---

from backend.agents.analyst import AnalystAgent

# Register the AnalystAgent class for the "analyst" task key.
# This ensures it runs as a BaseAgent subclass, inheriting metadata injection logic.
TaskRegistry.register_agent(
    task_keys=["analyst"],
    agent_cls=AnalystAgent,
    output_model=AnalystOutput
)


# --- Class-Based Agent Registration ---

from backend.agents.logician import LogicianAgent
from backend.models.domain import LogicianData

TaskRegistry.register_agent(task_keys=["logician"], agent_cls=LogicianAgent, output_model=LogicianData)

from backend.agents.profiler import ProfilerAgent
from backend.models.domain import ProfilerAnalysis

TaskRegistry.register_agent(task_keys=["profiler"], agent_cls=ProfilerAgent, output_model=ProfilerAnalysis)
