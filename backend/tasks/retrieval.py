"""Retrieval Tasks.

Functional tasks for fetching context and precedents.
"""

import logging

from backend.agents.archivist import ArchivistAgent
from backend.agents.retrieval import RetrievalAgent
from backend.core.registry import TaskRegistry
from backend.models.domain import ArchivistOutput, ContextData

logger = logging.getLogger(__name__)


def register_retrieval_tasks():
    """Registers retrieval-related agents with the TaskRegistry."""
    logger.info("Registering retrieval tasks...")

    # 1. Retrieval (Context)
    TaskRegistry.register_agent(task_keys=["retrieve_context"], agent_cls=RetrievalAgent, output_model=ContextData)

    # 2. Archivist (Precedents)
    TaskRegistry.register_agent(task_keys=["archivist"], agent_cls=ArchivistAgent, output_model=ArchivistOutput)


# Execute registration on import
register_retrieval_tasks()
