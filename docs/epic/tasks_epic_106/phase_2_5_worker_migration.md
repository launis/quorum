# Phase 2.5: Worker Rendering Pipeline Migration

Provide a brief description of the problem, any background context, and what the change accomplishes.
**Goal**: Refactor the synthesis pipeline in the worker to source cognitive instructions from the DAG's `PromptBlock` instead of relying on the legacy `SynthesisConfigDTO.system_prompt`. This enforces the `execution_synthesis_tier_decoupling` invariant.

## Proposed Changes

### `backend_v2/worker.py`
#### [MODIFY] [worker.py](file:///c:/src/quorum/backend_v2/worker.py)
- **Refactor `generate_profile_synthesis_and_pdf_task`**: 
  - Locate the synthesis prompt construction block (lines 766-802).
  - Remove reliance on `synthesis_cfg.system_prompt`.
  - Instead, use the `synthesis_block_id` to fetch the actual `PromptBlock` via `await repo.get_prompt_block(synthesis_block_id)`.
  - Instantiate the `PromptBlock` Pydantic model (`PromptBlock.model_validate(pb_dict, strict=False)` - enforcing the `pydantic_pure_hydration_boundary` rule) and use its `ai_description` (or let the `PromptCompiler` format it) as the base system prompt.
  - Retain the injection of `length_constraint`, `tone_instruction`, and `omit_empty_sections` from `synthesis_cfg` (which comes from `OutputLayoutBlock.synthesis`).
  - **Fail-Fast**: Ensure the block triggers `if synthesis_cfg:` (rather than just `if synthesis_block_id:`). If `synthesis_block_id` is missing from `synthesis_cfg` or the block cannot be found in the DB, raise an explicit `AppException(ErrorCodes.CONFIGURATION_ERROR)`.
- **Double Check `formatting_directives`**: Verify that no residual `formatting_directives` or profile-level `synthesis` config accesses remain in `worker.py` or `llm.py`. (Note: Phase 1/2 already scrubbed these from `llm.py` and the DTOs, but we must guarantee `worker.py` is clean).

## Verification Plan

### Automated Tests
- **Update Mocks**: Update `tests/unit/test_worker_synthesis.py` so that the `repo.get_prompt_block` `AsyncMock` returns a valid `PromptBlock` dictionary when queried for `synthesis_block_id`, preventing the new Fail-Fast logic from crashing existing tests.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` to verify that `worker.py` compiles, passes MyPy, and doesn't break existing synthesis tests.
- Verify coverage remains >90%.

### Manual Verification
- None required before Integration Checkpoint.
