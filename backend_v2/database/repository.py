"""Unified composite repository facade over the 9 active V2 domain repositories."""

from __future__ import annotations

from backend_v2.database.interfaces import IUnifiedWorkflowRepository, UnitOfWorkFactory
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.components.task_brief import TaskBriefRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.report_artifact import ReportArtifactRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl

__all__ = ["UnifiedWorkflowRepository"]


class UnifiedWorkflowRepository(
    WorkflowRepositoryImpl,
    ExecutionRepositoryImpl,
    ReportArtifactRepositoryImpl,
    PromptBlockRepositoryImpl,
    TaskBriefRepositoryImpl,
    OutputProfileRepositoryImpl,
    IdentityRepositoryImpl,
    AuditRepositoryImpl,
    SystemRepositoryImpl,
    IUnifiedWorkflowRepository,
):
    """Zero-storage-logic V2 composite protocol facade over the 9 EntityPersistencePort repositories."""

    def __init__(self, uow_factory: UnitOfWorkFactory | None = None) -> None:
        """Initialize the composite facade bound to a UnitOfWorkFactory."""
        super().__init__(uow_factory)
