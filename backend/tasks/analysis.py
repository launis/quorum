"""Analyst Task.

Functional task for 'Analyst' role.
Generates Hypotheses and RAG evidence needs.
"""

import logging

from backend.agents.analyst import AnalystAgent
from backend.agents.logician import LogicianAgent
from backend.agents.profiler import ProfilerAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import AnalystOutput, LogicianOutput, ProfilerOutput

logger = logging.getLogger(__name__)


def register_analysis_tasks():
    """Registers analysis-related agents with the TaskRegistry."""
    logger.info("Registering analysis tasks...")

    # 1. Analyst
    TaskRegistry.register_agent(
        task_keys=["analyst"],
        agent_cls=AnalystAgent,
        output_model=AnalystOutput
    )

    # 2. Logician
    TaskRegistry.register_agent(
        task_keys=["logician"],
        agent_cls=LogicianAgent,
        output_model=LogicianOutput
    )

    # 3. Profiler
    TaskRegistry.register_agent(
        task_keys=["profiler"],
        agent_cls=ProfilerAgent,
        output_model=ProfilerOutput
    )

# Execute registration on import
register_analysis_tasks()
