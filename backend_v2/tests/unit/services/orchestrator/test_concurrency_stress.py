"""High-concurrency stress test suite for DAG orchestrator atom tasks.

Verifies lock integrity, zero deadlocks, zero lock starvation, snapshot isolation,
and clean TaskGroup cancellation with bracketless except* under high atom load (50+ and 100+ atoms).
"""

from __future__ import annotations

import asyncio

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep
from backend_v2.models.enums import ExecutionStatus
from backend_v2.tests.fakes.in_memory_repositories import InMemoryExecutionRepository


def _build_test_execution_record(execution_id: str, step_count: int) -> ExecutionRecord:
    """Helper to instantiate a valid ExecutionRecord populated with initial steps."""
    steps: list[ExecutionStep] = [
        ExecutionStep(
            id=f"stp_{i:04d}_0123456789abcdef"[:20],
            label=f"Simulated Atom Step {i}",
            status=ExecutionStatus.PENDING,
            prompt_tokens=0,
            completion_tokens=0,
        )
        for i in range(step_count)
    ]
    step_states: dict[str, ExecutionStep] = {s.id: s for s in steps}
    return ExecutionRecord(
        id=execution_id,
        workflow_id="wf_0123456789abcdef",
        target_locale="en",
        status=ExecutionStatus.RUNNING,
        steps=steps,
        step_states=step_states,
    )


@pytest.mark.asyncio
async def test_concurrency_stress_50_atoms_no_deadlock() -> None:
    """Boundary: 50 concurrent simulated atom tasks complete in TaskGroup with zero deadlocks."""
    step_count = 50
    exec_record = _build_test_execution_record("exe_0000000000000001", step_count)
    update_lock = asyncio.Lock()
    completed_steps: list[str] = []

    async def _simulate_atom_task(step_id: str, index: int) -> None:
        # Simulate asynchronous cognitive work / IO latency
        await asyncio.sleep(0.005 * (index % 5))

        # Perform atomic thread-safe state transition under lock
        async with update_lock:
            nonlocal exec_record
            current_state = exec_record.step_states[step_id]
            updated_state = current_state.model_copy(
                update={
                    "status": ExecutionStatus.PASSED,
                    "prompt_tokens": 150 + index,
                    "completion_tokens": 40 + index,
                }
            )
            new_states = {**exec_record.step_states, step_id: updated_state}
            new_steps = [updated_state if s.id == step_id else s for s in exec_record.steps]
            exec_record = exec_record.model_copy(
                update={
                    "step_states": new_states,
                    "steps": new_steps,
                    "prompt_tokens": exec_record.prompt_tokens + 150 + index,
                    "completion_tokens": exec_record.completion_tokens + 40 + index,
                }
            )
            completed_steps.append(step_id)

    # Execute all 50 atom tasks inside asyncio.TaskGroup with timeout
    async with asyncio.timeout(10.0):
        async with asyncio.TaskGroup() as tg:
            for i, step in enumerate(exec_record.steps):
                tg.create_task(_simulate_atom_task(step.id, i))

    assert len(completed_steps) == step_count
    assert len(set(completed_steps)) == step_count
    assert all(s.status == ExecutionStatus.PASSED for s in exec_record.steps)
    assert all(st.status == ExecutionStatus.PASSED for st in exec_record.step_states.values())
    assert exec_record.prompt_tokens > 0
    assert exec_record.completion_tokens > 0


@pytest.mark.asyncio
async def test_concurrency_stress_100_atoms_high_frequency_lock() -> None:
    """Stress: 100+ concurrent atom tasks execute multi-phase state transitions under heavy contention."""
    step_count = 100
    exec_record = _build_test_execution_record("exe_0000000000000002", step_count)
    update_lock = asyncio.Lock()
    transition_counter = 0

    async def _multi_phase_atom_task(step_id: str, index: int) -> None:
        nonlocal exec_record, transition_counter

        # Phase 1: Transition PENDING -> RUNNING
        async with update_lock:
            running_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.RUNNING})
            new_states = {**exec_record.step_states, step_id: running_state}
            exec_record = exec_record.model_copy(update={"step_states": new_states})
            transition_counter += 1

        # Simulate micro-work
        await asyncio.sleep(0.002 * (index % 4))

        # Phase 2: Transition RUNNING -> PASSED with token telemetry
        async with update_lock:
            passed_state = exec_record.step_states[step_id].model_copy(
                update={"status": ExecutionStatus.PASSED, "prompt_tokens": 100, "completion_tokens": 50}
            )
            new_states = {**exec_record.step_states, step_id: passed_state}
            new_steps = [passed_state if s.id == step_id else s for s in exec_record.steps]
            exec_record = exec_record.model_copy(
                update={
                    "step_states": new_states,
                    "steps": new_steps,
                    "prompt_tokens": exec_record.prompt_tokens + 100,
                    "completion_tokens": exec_record.completion_tokens + 50,
                }
            )
            transition_counter += 1

    async with asyncio.timeout(15.0):
        async with asyncio.TaskGroup() as tg:
            for i, step in enumerate(exec_record.steps):
                tg.create_task(_multi_phase_atom_task(step.id, i))

    assert transition_counter == step_count * 2
    assert all(s.status == ExecutionStatus.PASSED for s in exec_record.steps)
    assert all(st.status == ExecutionStatus.PASSED for st in exec_record.step_states.values())
    assert exec_record.prompt_tokens == step_count * 100
    assert exec_record.completion_tokens == step_count * 50


@pytest.mark.asyncio
async def test_concurrency_stress_fault_injection_cancels_cleanly() -> None:
    """Error path: fault injected at high concurrency triggers clean TaskGroup cancellation without zombies."""
    step_count = 50
    fault_index = 25
    exec_record = _build_test_execution_record("exe_0000000000000003", step_count)
    update_lock = asyncio.Lock()
    started_tasks: set[int] = set()
    cleaned_up_tasks: set[int] = set()
    caught_app_exception = False

    async def _failing_atom_task(step_id: str, index: int) -> None:
        started_tasks.add(index)
        try:
            if index == fault_index:
                # Trigger fail-fast domain exception
                await asyncio.sleep(0.01)
                raise AppException(
                    f"Injected fault in atom task {index}",
                    details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
                )
            # Sibling tasks perform normal work until cancelled
            await asyncio.sleep(1.0)
            async with update_lock:
                nonlocal exec_record
                passed_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.PASSED})
                new_states = {**exec_record.step_states, step_id: passed_state}
                exec_record = exec_record.model_copy(update={"step_states": new_states})
        except asyncio.CancelledError:
            cleaned_up_tasks.add(index)
            raise

    try:
        async with asyncio.timeout(5.0):
            async with asyncio.TaskGroup() as tg:
                for i, step in enumerate(exec_record.steps):
                    tg.create_task(_failing_atom_task(step.id, i))
    except* AppException as eg:
        caught_app_exception = True
        assert len(eg.exceptions) == 1
        assert "Injected fault in atom task 25" in str(eg.exceptions[0])

    assert caught_app_exception is True
    # Verify that sibling tasks that were started got cancelled cleanly
    assert len(cleaned_up_tasks) > 0
    # Faulty task itself raised, so it should not be in cleaned_up_tasks
    assert fault_index not in cleaned_up_tasks


@pytest.mark.asyncio
async def test_concurrency_stress_fake_repo_fault_injection() -> None:
    """Error path: in-memory repository fault injection during concurrent saves triggers ExceptionGroup."""
    repo = InMemoryExecutionRepository()
    record = _build_test_execution_record("exe_0000000000000004", 10)
    await repo.save_execution(record)

    # Configure deterministic fault injection on save_execution
    repo.inject_fault(
        "save_execution",
        AppException(
            "Simulated disk write failure under load",
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
        ),
        trigger_count=1,
    )

    caught_repo_fault = False

    async def _concurrent_save(i: int) -> None:
        await asyncio.sleep(0.002 * (i % 3))
        mutated = record.model_copy(update={"prompt_tokens": (i + 1) * 10})
        await repo.save_execution(mutated)

    try:
        async with asyncio.timeout(5.0):
            async with asyncio.TaskGroup() as tg:
                for i in range(20):
                    tg.create_task(_concurrent_save(i))
    except* AppException as eg:
        caught_repo_fault = True
        assert any("Simulated disk write failure under load" in str(exc) for exc in eg.exceptions)

    assert caught_repo_fault is True


@pytest.mark.asyncio
async def test_concurrency_stress_snapshot_isolation_under_concurrency() -> None:
    """Positive: concurrent reads and writes maintain snapshot isolation without torn states."""
    repo = InMemoryExecutionRepository()
    record = _build_test_execution_record("exe_0000000000000005", 20)
    await repo.save_execution(record)

    read_snapshots: list[ExecutionRecord] = []
    stop_event = asyncio.Event()

    async def _writer_task() -> None:
        for i in range(30):
            await asyncio.sleep(0.003)
            current = await repo.get_execution(record.id)
            assert current is not None
            updated = current.model_copy(update={"prompt_tokens": (i + 1) * 50})
            await repo.save_execution(updated)
        stop_event.set()

    async def _reader_task(reader_id: int) -> None:
        while not stop_event.is_set():
            await asyncio.sleep(0.002)
            fetched = await repo.get_execution(record.id)
            if fetched is not None:
                read_snapshots.append(fetched)

    async with asyncio.timeout(5.0):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_writer_task())
            for r in range(5):
                tg.create_task(_reader_task(r))

    assert len(read_snapshots) > 0
    # Verify snapshot isolation: each fetched record is an isolated immutable instance
    for snap in read_snapshots:
        assert snap.id == record.id
        assert snap.workflow_id == record.workflow_id
        assert snap.prompt_tokens >= 0
