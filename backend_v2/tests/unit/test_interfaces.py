"""Unit tests for backend_v2.database.interfaces."""

from __future__ import annotations

import inspect

import pytest

from backend_v2.database import interfaces
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7_opaque_id
from backend_v2.models.domain.proposition_graph import EdgeDraft, NodeDraft, PropositionPayloadDTO
from backend_v2.models.enums import DependencyRelationType, EntityPrefix, PropositionNodeType
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


def test_interfaces_are_protocols() -> None:
    """Verify that all 9 active V2 repository protocols and Hexagonal CQRS ports are defined as Protocols."""
    protocol_classes = [
        interfaces.CausalReasoningPort,
        interfaces.EntityPersistencePort,
        interfaces.GraphMutationPort,
        interfaces.IAuditRepository,
        interfaces.IEntityPersistenceAdapter,
        interfaces.IExecutionRepository,
        interfaces.IIdentityRepository,
        interfaces.IOutputProfileRepository,
        interfaces.IPromptBlockRepository,
        interfaces.IReportArtifactRepository,
        interfaces.ISystemRepository,
        interfaces.ITaskBriefRepository,
        interfaces.IUnifiedWorkflowRepository,
        interfaces.IWorkflowRepository,
        interfaces.QuorumUnitOfWork,
        interfaces.TopologyResolutionPort,
    ]

    helper_exports = [
        interfaces.UnitOfWorkFactory,
        interfaces.get_active_uow,
        interfaces.get_registered_uow_factory,
        interfaces.open_uow_session,
        interfaces.register_default_uow_factory,
    ]
    assert len(protocol_classes) + len(helper_exports) == len(interfaces.__all__)
    assert callable(interfaces.register_default_uow_factory)
    assert callable(interfaces.get_registered_uow_factory)
    assert interfaces.get_registered_uow_factory() is not None
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


@pytest.mark.asyncio
async def test_in_memory_entity_adapter_delete_tenant_secret_positive_and_invalid() -> None:
    """Verify InMemoryEntityAdapter.delete_tenant_secret deletes records and rejects invalid prefixes."""
    uow = InMemoryUnitOfWork()
    sec_id = generate_uuid7_opaque_id(EntityPrefix.TENANT_SECRET)
    uow.store.seed_tables["tenant_secrets"][sec_id] = (sec_id,)

    assert await uow.entities.delete_tenant_secret(sec_id) is True
    assert await uow.entities.delete_tenant_secret(sec_id) is False

    with pytest.raises(AppException) as bad_prefix_exc:
        await uow.entities.delete_tenant_secret("usr_0195f3a0000070008000000000000001")
    assert bad_prefix_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_open_uow_session_propagates_and_reuses_active_uow_and_handles_none_factory() -> None:
    """Verify open_uow_session binds get_active_uow, reuses outer session re-entrantly, and handles None factory."""
    assert interfaces.get_active_uow() is None

    async with interfaces.open_uow_session(None) as none_uow:
        assert none_uow is None
        assert interfaces.get_active_uow() is None

    root_uow = InMemoryUnitOfWork()
    opened: list[InMemoryUnitOfWork] = []

    def factory() -> InMemoryUnitOfWork:
        inst = InMemoryUnitOfWork(root_uow.store)
        opened.append(inst)
        return inst

    committed_execution = ExecutionRecordFactory.build()
    async with interfaces.open_uow_session(factory) as outer_uow:
        assert outer_uow is not None
        assert interfaces.get_active_uow() is outer_uow
        await outer_uow.entities.save_execution(committed_execution)
        async with interfaces.open_uow_session(factory) as inner_uow:
            assert inner_uow is outer_uow
            assert len(opened) == 1
        assert interfaces.get_active_uow() is outer_uow

    assert interfaces.get_active_uow() is None
    assert opened[0]._finalized is True
    assert root_uow.store.current_org_reset_count == 1
    assert await root_uow.entities.get_execution(committed_execution.id) is not None

    aborted_execution = ExecutionRecordFactory.build()
    with pytest.raises(AppException):
        async with interfaces.open_uow_session(factory) as failing_uow:
            assert failing_uow is not None
            await failing_uow.entities.save_execution(aborted_execution)
            raise AppException(
                message="Simulated transactional failure",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
    assert interfaces.get_active_uow() is None
    assert opened[1]._finalized is True
    assert root_uow.store.current_org_reset_count == 2
    assert await root_uow.entities.get_execution(aborted_execution.id) is None
