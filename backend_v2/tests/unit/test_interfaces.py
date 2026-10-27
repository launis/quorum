"""Unit tests for backend_v2.database.interfaces."""

from __future__ import annotations

import inspect
from typing import Protocol

from backend_v2.database import interfaces


def test_interfaces_are_protocols() -> None:
    """Verify that all repository interfaces and Hexagonal CQRS ports are defined as Protocols."""
    protocol_classes = [
        interfaces.IExecutionRepository,
        interfaces.IWorkflowRepository,
        interfaces.IIdentityRepository,
        interfaces.IComponentRepository,
        interfaces.IKnowledgeRepository,
        interfaces.ISystemRepository,
        interfaces.IAuditRepository,
        interfaces.GraphMutationPort,
        interfaces.TopologyResolutionPort,
        interfaces.CausalReasoningPort,
        interfaces.EntityPersistencePort,
        interfaces.QuorumUnitOfWork,
    ]

    for protocol_class in protocol_classes:
        assert inspect.isclass(protocol_class)
        assert Protocol in protocol_class.__mro__


def test_interfaces_can_be_imported() -> None:
    """Verify that the module loads without circular dependencies."""
    assert interfaces is not None
