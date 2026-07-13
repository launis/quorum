# Phase 1.2: Legacy Migration & KI Registration

## Goal
Integrate the newly built `TopologicalEvaluator` SSOT engine with the existing evaluation pipeline (e.g., `dag_executor.py` or node strategy) so that the current legacy logic leverages the new deterministic engine. Create a Knowledge Item for the new DAG engine.

## Context (Read-Only)
- `backend_v2/services/orchestrator/dag_executor.py`
- `backend_v2/models/dtos/dag_models.py`
- `backend_v2/services/orchestrator/topological_evaluator.py`

## Target (Modify)
- `[MODIFY] backend_v2/services/orchestrator/strategies/llm_node_strategy.py` (or equivalent file delegating evaluation logic, e.g., `chunk_worker.py`)
- `[NEW] <appDataDir>\knowledge\topological_engine\ki_topological_engine.md`
- `[NEW] <appDataDir>\knowledge\topological_engine\metadata.json`

## Destructive Operation Inventory
- Intentionally modifying the evaluation delegation inside the existing Node Strategy to use `TopologicalEvaluator` instead of inline iteration/gather. No symbols are completely dropped, only execution internals routed through the new SSOT.

## Architectural Rules Injected
- **00-antigravity-core.md**: SSOT UI Validation Mandate (Legacy Migration First). You must validate UI tests pass after refactoring.
- **01-python-backend.md**: TaskGroup ExceptionGroup Mandate. Zero-Trust Dependency Environment.

## Implementation Steps
1. **Analyze Current Evaluator**:
   - Locate the current execution loops handling chunk atomization or matrix processing where nodes are evaluated.
   - Refactor these loops to construct `LinkedAtomGraph` representations of the legacy elements.
2. **Refactor & Wire up**:
   - Pass the mapped graphs into `TopologicalEvaluator.evaluate()`.
   - Map the returned `AtomExecutionState` items back to the legacy state models (`ExecutionStepState` or `AtomResultDTO`) so that downstream pipeline stages and clients don't break.
3. **KI Creation**:
   - Create `ki_topological_engine.md` in `<appDataDir>\knowledge\topological_engine\`. Detail usage rules: All future DAG dependency evaluations MUST use this SSOT. NEVER use `asyncio.gather` or manual locking for acyclic evaluation.
   - Create `metadata.json` for the KI with references to Epic 92.
4. **Documentation**:
   - Update `.agents/rules/04_directory_reference.md` to formally document `TopologicalEvaluator` as the SSOT graph engine.

## Testing & Quality Gate Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`
- Run the full suite `uv run pytest` to ensure UI-Validointi (Legacy Migration First) passes perfectly. The Baseline Parity must remain at 100% relative to Phase 1.1.

---
**Session Handover**
To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
