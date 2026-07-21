# Phase 1: Foundation (Settings & DTOs)

Source: Epic Phase 1, Step 4

## Proposed Changes

### Configuration
#### [MODIFY] @[c:\src\quorum\backend_v2\settings.py]
- Update `max_concurrent_llm_steps` to default to `3` and change description to `"Max parallel LLM extractions within a TaskGroup"`.

### Domain Models
#### [MODIFY] @[c:\src\quorum\backend_v2\models\domain\blackboard.py]
- Update `DraftExtractedAtom` to include `source_sequence_index: Annotated[int, Field(description="Injected programmatically by the Python worker for chronological sorting.")]` (Must NOT have a default value to enforce Fail-Fast).

#### [MODIFY] @[c:\src\quorum\backend_v2\models\dtos\dag_models.py]
- Update `ExtractedAtom` to include `source_sequence_index: Annotated[int, Field(description="The chronological sequence index indicating extraction order.")]` (Must NOT have a default value).

### Unit Tests
#### [MODIFY] @[c:\src\quorum\backend_v2\tests\]
- Update all test mocks and factories instantiating `ExtractedAtom` and `DraftExtractedAtom` (e.g., in `test_dag_models.py`, `test_two_pass_atomizer.py`, `test_extractive_sensor_service.py`, `test_topological_evaluator.py`, `test_sliding_window_linker.py`, `test_dag_executor_atom_ceiling.py`) to explicitly pass `source_sequence_index=0` to satisfy the new strict Pydantic requirements.

## Verification Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/settings.py`
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models/`

## Session Handover
Run the Tier 2 execution command provided in the tracker.
