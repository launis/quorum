"""Retrieval Tasks.

Functional tasks for fetching context and precedents.
"""

import logging

from pydantic import BaseModel, ConfigDict, Field

from backend.core.registry import TaskRegistry
from backend.database.factory import get_repository
from backend.database.wrapper import get_db_client
from backend.settings import get_settings

logger = logging.getLogger(__name__)


# --- Class-Based Agent Registration ---

from backend.agents.retrieval import RetrievalAgent
from backend.models.domain import ContextData

# Register RetrievalAgent for "retrieve_context"
# Replaces the functional task, ensuring uniform BaseAgent metadata injection.
TaskRegistry.register_agent(
    task_keys=["retrieve_context"],
    agent_cls=RetrievalAgent,
    output_model=ContextData
)


# --- Class-Based Agent Registration (Archivist) ---

from backend.agents.archivist import ArchivistAgent
from backend.models.domain import ArchivistOutput

TaskRegistry.register_agent(task_keys=["archivist"], agent_cls=ArchivistAgent, output_model=ArchivistOutput)
