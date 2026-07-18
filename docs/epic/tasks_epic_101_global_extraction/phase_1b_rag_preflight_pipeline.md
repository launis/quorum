# Phase 1B: RAG Pre-Flight Pipeline & Virtual Step Injection

> **Source:** Epic 101, Phase 1 (Steps 1-7), Section 4 (TaskGroup Cascade Isolation, Blackboard Anti-Corruption, Payload Bloat, Virtual Injection Risk)

## Goal

Implement the RAG Pre-Flight hook inside `DAGExecutor.execute_workflow()` that runs BEFORE the UI step iteration loop. This phase creates the invisible extraction pipeline that atomizes all input documents ONCE and stores the result into the `context_variables["global_atoms"]` blackboard.

## Architectural Invariants (Injected)

- `taskgroup_exceptiongroup_mandate`: `asyncio.TaskGroup` + `asyncio.Semaphore`, NO `asyncio.gather`
- `dlq_arq_fallback_routing`: Worker errors → DLQ sentinel, NOT naked exceptions
- `llm_structured_execution_mandate`: All LLM calls → `LLMTaskExecutor.execute_structured_task()`
- `no_naked_dicts_in_state`: Blackboard projection via `.model_dump(mode="json")`
- `frozen_state_mutability`: `workflow.model_copy(update={...})` for virtual step injection
- `global_config_sovereignty` (KI): Semaphore from `settings.max_concurrent_llm_steps`
- `unified_model_multiplexing` (KI): `LLMClient.from_strategy("fast", repo)`
- `transient_error_resilience` (KI): Retry transient 503/429 before DLQ routing

## Dependencies

- **Phase 1A MUST be completed first** (models, enums, settings exist).

---

## Milestone 1B.1: Virtual Step Injection in `DAGExecutor`

**Source: Epic Phase 1, Steps 1-2**

### TARGET (Modify): [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py)

Inside `execute_workflow()`, BEFORE the step iteration loop (line ~608), implement:

1. **Pre-Condition Scan**: Scan `workflow.steps` to check if ANY step has `engine_override == EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS`. If none, skip the entire Pre-Flight phase.

2. **Virtual Step Identity Generation**:
   ```python
   import uuid
   
   virtual_step_id = f"stp_{uuid.uuid4().hex[:16]}"
   ```
   > **CRITICAL ARCHITECTURE RULE:** Do NOT inject this step into the `workflow.steps` list! The `workflow` is an immutable database record and modifying it will contaminate the main `asyncio.TaskGroup` executor loop causing a fatal `ConfigurationError` when it tries to run `sys_rag_preflight`.

3. **Virtual StepState Injection & Pre-Commit**: Add `ExecutionStepState` with `RUNNING` status for the virtual step into `exec_record.step_states`. This is the ONLY injection needed for the UI to organically discover and render the step.
   > **CRITICAL DB COMMIT:** You MUST explicitly call `await _safe_commit()` immediately AFTER injecting this `RUNNING` state and BEFORE launching the heavy `_execute_rag_preflight()`. If you fail to commit here, the frontend SSE will freeze and never show the virtual step until the extraction is entirely finished.

4. **Emit Progress TraceEvent**: Create helper method `_emit_preflight_progress()` that emits `TraceEvent(step_name=virtual_step_id, event_type="progress", content={"message": "...", "progress_pct": N})` and commits via `_safe_commit()`.

### CONTEXT (Read-Only):
- `backend_v2/models/v2_core.py` — `StepRule`, `ExecutionStepState`, `Workflow`
- `backend_v2/models/state.py` — `TraceEvent`
- `backend_v2/models/enums.py` — `EngineOverrideStrategy`, `ExecutionStatus`

---

## Milestone 1B.2: RAG Extraction Pipeline (Map-Reduce Atomization)

**Source: Epic Phase 1, Steps 3-6**

### TARGET (Modify): [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py)

Implement a private method `_execute_rag_preflight()` on `DAGExecutor`:

```python
async def _execute_rag_preflight(
    self,
    workflow: Workflow,
    exec_record: ExecutionRecord,
    projector: StateProjector,
    virtual_step_id: str,
    _update_lock: asyncio.Lock,
    _safe_commit: Callable,
) -> dict[str, Any]:
```

Logic flow:

1. **Resolve LLM Task Executor & Client**: 
   ```python
   executor = LLMTaskExecutor(prompt_compiler=self.compiler)
   client = await LLMClient.from_strategy("fast", self.system_repo)
   ```

2. **Collect Input Files & Sequential File Orchestration**: Inspect `workflow.expected_inputs` (if accessible through the workflow object) or inspect `exec_record.raw_inputs` to enumerate all input file keys (e.g., `product_text`, `chat_log`). For EACH input file:
   - Extract the text payload from the execution trace projector (`projector.snapshot`)
   - Chunk it via `ChunkingService.chunk_payload()`
   - Run `TwoPassAtomizer(executor).execute_phase_0()` + `TwoPassAtomizer(executor).execute_phase_1_drafts()` per file sequentially.
   > **CONCURRENCY CLARIFICATION:** Do NOT implement `asyncio.TaskGroup` or `Semaphore` inside `DAGExecutor`. The `TwoPassAtomizer` ALREADY implements `TaskGroup` and `Semaphore(settings.max_concurrent_llm_steps)` internally to process all chunks of a single file concurrently. `DAGExecutor` only loops over the files sequentially.
   > **LINKER OMISSION CLARIFICATION:** Although Epic 101 Chapter 3 mentions running `SlidingWindowLinker`, this is a legacy architectural artifact. Because `GlobalAtomBlackboard` explicitly requires `DraftAtomList`, the topological causal edges from the linker are discarded. Do NOT run `SlidingWindowLinker` in the RAG Pre-Flight to save tokens and latency.

3. **TwoPassAtomizer Modifications (DLQ, Anti-Corruption, and Draft Methods)**: 
   - **New Blackboard Methods**: Do NOT modify the return type of `execute_phase_1`. Instead, create `execute_phase_1_drafts()` and `_extract_drafts_from_chunk()` which return `DraftAtomList` (preserving `DraftExtractedAtom` models without mapping them to `ExtractedAtom`). This prevents breaking the legacy consumer in `llm.py` while natively supporting the `GlobalAtomBlackboard` which strictly requires `DraftAtomList`.
   - Update `_extract_drafts_from_chunk()` to handle both Retry and Physical Anchoring:
     - **Tenacity Retry**: Add a Tenacity retry decorator (`@retry(stop=stop_after_attempt(3), wait=wait_exponential())`) to handle transient 503/429 errors.
     - **DLQ Wrapper**: Wrap the internal execution in a `try-except Exception` block. If retries are exhausted and an exception is caught, return the fallback sentinel: `DraftAtomList(atoms=[], dlq_status="FAILED/DLQ")`. 
     - **Anti-Corruption Layer & Quote Normalization**: Inside the `for draft in draft_result.atoms:` loop, BEFORE appending to the final validated drafts list, validate each atom individually against the `chunk` text. 
       - Apply `AnchorValidationService.normalize_text_with_mapping()` to BOTH the `chunk` text and the `draft.source_quote` BEFORE executing `str.find`.
       - If `draft.is_logical_deduction` is `True`, bypass the `str.find` check entirely and force `source_quote = None`.
       - If the quote is not found, drop the atom and log: `logger.warning("corrupted_atom_dropped", extra={"raw_payload": ...})` — **Dual-Reporting Mandate**. Silent drops are banned.
   - **TaskGroup Collector (execute_phase_1_drafts)**: Inside the TaskGroup result collector loop, check `if result.dlq_status:` on the returned draft lists. If any chunk failed, set `has_dlq = True` and emit `logger.warning("dlq_chunk_detected", ...)`. Finally, return a merged `DraftAtomList(atoms=all_atoms, dlq_status="FAILED/DLQ" if has_dlq else None)`.

4. **Atom Ceiling Enforcement (Inside DAGExecutor)**: After retrieving the `DraftAtomList` for a file, check `len(atoms.atoms) > settings.max_extracted_atoms_per_document`. If exceeded, Fail-Fast with `AppException(..., details={"error_code": ErrorCodes.VALIDATION_FAILED})`. Do NOT attempt to do the `str.find` Try-Except block inside `DAGExecutor`.

6. **Construct Blackboard**:
   ```python
   blackboard = GlobalAtomBlackboard(atoms_by_input=atoms_by_input_dict)
   ```

7. **Project to context_variables**: 
   ```python
   new_cv = dict(exec_record.context_variables)
   new_cv["global_atoms"] = blackboard.model_dump(mode="json")
   exec_record = exec_record.model_copy(update={"context_variables": new_cv})
   ```

8. **Emit Progress Events**: Throughout the loop, emit periodic `progress` TraceEvents to keep SSE alive.

### CONTEXT (Read-Only):
- `backend_v2/services/orchestrator/two_pass_atomizer.py` — `TwoPassAtomizer`
- `backend_v2/services/orchestrator/chunking_service.py` — `ChunkingService`
- `backend_v2/llm/client.py` — `LLMClient.from_strategy()`
- `backend_v2/models/domain/blackboard.py` — `GlobalAtomBlackboard`, `DraftAtomList`
- `backend_v2/settings.py` — `max_extracted_atoms_per_document`

---

## Milestone 1B.3: Mark Virtual Step Passed & Commit

**Source: Epic Phase 1, Step 7**

### TARGET (Modify): [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py)

After `_execute_rag_preflight()` returns successfully:

1. Mark virtual step as `ExecutionStatus.PASSED` in `exec_record.step_states`.
2. Commit the full state via `_safe_commit()`
3. **Exclude Check**: Since we strictly obeyed Milestone 1B.1 and did NOT add the virtual step to `workflow.steps`, no messy exclusion logic is required. The main step iteration loop will naturally ignore it.

Error handling: If the preflight crashes, mark virtual step as `FAILED`, commit error state, and re-raise as `WorkflowExecutionError`.

### CONTEXT (Read-Only):
- Same as Milestone 1B.1

---

## Bidirectional Integration Check

| Consumer | Producer | Verified? |
|---|---|---|
| `PreHydratedSynthesisStrategy` reads `context_variables["global_atoms"]` | `_execute_rag_preflight()` writes it | ✅ (Phase 2 plan) |
| Flutter SSE renders `progress` TraceEvents | `_emit_preflight_progress()` emits them | ✅ (Cross-Boundary Note: existing SSE projection handles new event_type) |
| `GlobalAtomBlackboard.model_validate()` | `_execute_rag_preflight()` constructs it | ✅ (Phase 1A models) |

---

## Testing & Quality Gate Plan

### Baseline:
```
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test
```
Record passing test count as `[BASELINE]`.

### Unit Tests:
1. **`test_dag_executor_preflight_skip.py`** — Verify pre-flight is skipped when no step has `engine_override == PRE_HYDRATED_SYNTHESIS`.
2. **`test_dag_executor_preflight_execution.py`** — Mock `TwoPassAtomizer` and verify blackboard is projected into `context_variables["global_atoms"]`.
3. **`test_dag_executor_virtual_step.py`** — Verify virtual step injection, status transitions (RUNNING → PASSED), and progress events.
4. **`test_dag_executor_dlq_routing.py`** — Verify DLQ sentinel handling when a chunk worker fails.
5. **`test_dag_executor_atom_ceiling.py`** — Verify `AppException` is raised when atom count exceeds `settings.max_extracted_atoms_per_document`.

### Quality Gate:
```
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test
```

---

## Session Handover
```
Achieved: RAG Pre-Flight pipeline with virtual step injection, DLQ routing, and blackboard projection.
Remaining: Phase 2 (PreHydratedSynthesisStrategy), Phase 3 (SDUI routing + seed_data.json).
```
