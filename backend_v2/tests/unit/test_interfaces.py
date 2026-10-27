"""Unit tests for backend_v2.database.interfaces."""

from __future__ import annotations

import inspect

import pytest

from backend_v2.database import interfaces
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7_opaque_id
from backend_v2.models.domain.proposition_graph import EdgeDraft, NodeDraft, PropositionPayloadDTO
from backend_v2.models.enums import DependencyRelationType, EntityPrefix, PropositionNodeType
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


def test_interfaces_are_protocols() -> None:
    """Verify that all 22 repository interfaces and Hexagonal CQRS ports are defined as Protocols."""
    protocol_classes = [
        interfaces.CausalReasoningPort,
        interfaces.EntityPersistencePort,
        interfaces.GraphMutationPort,
        interfaces.IAgentRepository,
        interfaces.IAuditRepository,
        interfaces.IComponentRepository,
        interfaces.IEntityPersistenceAdapter,
        interfaces.IExecutionPersonaRepository,
        interfaces.IExecutionRepository,
        interfaces.IExtractionProtocolRepository,
        interfaces.IIdentityRepository,
        interfaces.IKnowledgeRepository,
        interfaces.IMatrixRepository,
        interfaces.IOutputProfileRepository,
        interfaces.IPromptBlockRepository,
        interfaces.IReportArtifactRepository,
        interfaces.IRoleRepository,
        interfaces.ISystemRepository,
        interfaces.ITaskBlueprintRepository,
        interfaces.IUnifiedWorkflowRepository,
        interfaces.IWorkflowRepository,
        interfaces.QuorumUnitOfWork,
        interfaces.TopologyResolutionPort,
    ]

    assert len(protocol_classes) == len(interfaces.__all__)
    for protocol_class in protocol_classes:
        assert inspect.isclass(protocol_class)
        assert any(base.__name__ == "Protocol" for base in protocol_class.__mro__)


@pytest.mark.asyncio
async def test_runtime_checkable_ports_conformance_and_roundtrip() -> None:
    """Verify runtime_checkable CQRS ports and stateful wave materialization roundtrip."""
    uow = InMemoryUnitOfWork()
    assert isinstance(uow, interfaces.QuorumUnitOfWork)
    assert isinstance(uow.graph, interfaces.GraphMutationPort)
    assert isinstance(uow.topology, interfaces.TopologyResolutionPort)
    assert isinstance(uow.reasoning, interfaces.CausalReasoningPort)
    assert isinstance(uow.entities, interfaces.EntityPersistencePort)

    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    draft = NodeDraft(
        local_key="claim_1",
        node_type=PropositionNodeType.CLAIM,
        confidence=0.85,
        payload=PropositionPayloadDTO(statement="Primary analytical claim.", metadata={}),
    )
    async with uow as active_uow:
        materialized = await active_uow.graph.materialize_wave(run_id, [draft], [])
        assert len(materialized) == 1
        ready_wave = await active_uow.topology.fetch_next_kahn_wave(run_id)
        assert len(ready_wave) == 1
        assert ready_wave[0].node_id == materialized[0].node_id


def test_protocol_direct_instantiation_and_structural_mismatch_fail() -> None:
    """Verify direct Protocol instantiation raises TypeError and non-conforming objects fail isinstance."""
    protocol_types: list[type[object]] = [
        interfaces.QuorumUnitOfWork,
        interfaces.IExecutionRepository,
    ]
    for protocol_type in protocol_types:
        with pytest.raises(TypeError):
            protocol_type()

    assert not isinstance(object(), interfaces.QuorumUnitOfWork)
    assert not isinstance(object(), interfaces.GraphMutationPort)


@pytest.mark.asyncio
async def test_graph_mutation_port_rejects_malformed_run_id() -> None:
    """Verify GraphMutationPort implementation raises AppException on malformed run_id."""
    uow = InMemoryUnitOfWork()
    async with uow as active_uow:
        with pytest.raises(AppException) as exc_info:
            await active_uow.graph.materialize_wave("invalid_run_id", [], [])
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_graph_mutation_port_rejects_dangling_edge_draft() -> None:
    """Verify GraphMutationPort implementation raises AppException on dangling EdgeDraft reference."""
    uow = InMemoryUnitOfWork()
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    dangling_edge = EdgeDraft(
        source_key="missing_source",
        target_key="missing_target",
        relation_type=DependencyRelationType.SUPPORTS,
    )
    async with uow as active_uow:
        with pytest.raises(AppException) as exc_info:
            await active_uow.graph.materialize_wave(run_id, [], [dangling_edge])
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
