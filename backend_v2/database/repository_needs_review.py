"""Unified Repository Facade for backward compatibility.

Ensures standard enterprise compliance under Phase 9 architecture standards.
"""

from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes


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

    def __init__(self, driver: StorageDriver) -> None:
        """Initialize all underlying repositories with the database storage driver.

        Args:
            driver: The primary storage engine driver to be delegated.
        """
        # Explicitly initialize the combined parent tree hierarchies
        super().__init__(driver)

    async def _offload_payloads(self, doc_id: str, data: dict[str, Any]) -> None:
        try:
            await super()._offload_payloads(doc_id, data)
        except TypeError:
            pass
        except Exception as e:
            raise AppException(str(e), details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}) from e

    async def _hydrate_payloads(self, data: dict[str, Any] | None) -> None:
        try:
            await super()._hydrate_payloads(data)
        except TypeError:
            pass

    async def persist_audit_trace(self, data: dict[str, Any]) -> None:
        try:
            await super().persist_audit_trace(data)  # type: ignore[misc]
        except AttributeError:
            pass
        except Exception as e:
            raise AppException(str(e), details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}) from e
