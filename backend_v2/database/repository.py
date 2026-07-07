"""Unified Repository Facade for backward compatibility."""

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.database.repositories.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.agent import AgentRepositoryImpl
from backend_v2.database.repositories.task_blueprint import TaskBlueprintRepositoryImpl
from backend_v2.database.repositories.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl


class UnifiedWorkflowRepository(
    WorkflowRepositoryImpl,
    ExecutionRepositoryImpl,
    ComponentRepositoryImpl,
    PromptBlockRepositoryImpl,
    AgentRepositoryImpl,
    TaskBlueprintRepositoryImpl,
    OutputProfileRepositoryImpl,
    IdentityRepositoryImpl,
    AuditRepositoryImpl,
    SystemRepositoryImpl,
    KnowledgeRepositoryImpl,
):
    """Facade combining all granular repository implementations."""

    def __init__(self, driver: StorageDriver):
        """Initialize the unified repository facade.

        Args:
            driver: The storage driver instance to use for operations.
        """
        super().__init__(driver)
