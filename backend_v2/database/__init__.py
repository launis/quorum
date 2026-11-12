"""Database persistence ports, unit-of-work factories, and repository facades."""

from __future__ import annotations

from backend_v2.database.factory import (
    close_shared_pool_manager,
    create_unit_of_work,
    get_shared_pool_manager,
)
from backend_v2.database.interfaces import (
    CausalReasoningPort,
    EntityPersistencePort,
    GraphMutationPort,
    IAuditRepository,
    IEntityPersistenceAdapter,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    IReportArtifactRepository,
    ISystemRepository,
    ITaskBriefRepository,
    IUnifiedWorkflowRepository,
    IWorkflowRepository,
    QuorumUnitOfWork,
    TopologyResolutionPort,
    UnitOfWorkFactory,
    get_active_uow,
    get_registered_uow_factory,
    open_uow_session,
    register_default_uow_factory,
)
from backend_v2.database.repository import UnifiedWorkflowRepository

__all__ = [
    "CausalReasoningPort",
    "EntityPersistencePort",
    "GraphMutationPort",
    "IAuditRepository",
    "IEntityPersistenceAdapter",
    "IExecutionRepository",
    "IIdentityRepository",
    "IOutputProfileRepository",
    "IPromptBlockRepository",
    "IReportArtifactRepository",
    "ISystemRepository",
    "ITaskBriefRepository",
    "IUnifiedWorkflowRepository",
    "IWorkflowRepository",
    "QuorumUnitOfWork",
    "TopologyResolutionPort",
    "UnifiedWorkflowRepository",
    "UnitOfWorkFactory",
    "close_shared_pool_manager",
    "create_unit_of_work",
    "get_active_uow",
    "get_registered_uow_factory",
    "get_shared_pool_manager",
    "open_uow_session",
    "register_default_uow_factory",
]
