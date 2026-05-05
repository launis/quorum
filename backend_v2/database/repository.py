"""Unified Repository Facade for backward compatibility."""

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl


class UnifiedWorkflowRepository(
    WorkflowRepositoryImpl,
    ExecutionRepositoryImpl,
    ComponentRepositoryImpl,
    IdentityRepositoryImpl,
    AuditRepositoryImpl,
    SystemRepositoryImpl,
    KnowledgeRepositoryImpl,
):
    """Facade combining all granular repository implementations."""

    def __init__(self, driver: StorageDriver):
        super().__init__(driver)
