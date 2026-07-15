# Tasks

- [x] Create checklist from Phase 3a plan.
- [x] Modify `backend_v2/models/view/sdui.py`
  - [x] Add `class SduiNACard(SduiBlockBase):` with `block_type: Literal["n_a_card"] = "n_a_card"`.
  - [x] Add properties: `short_circuit_reason_tda_ids: list[str]` and `message: str`.
  - [x] Append `SduiNACard` to `AnySduiBlock`.
- [x] Modify `backend_v2/tests/integration/test_epic_chain_e2e.py`
  - [x] Add `test_epic_95_na_cascade_e2e()`
  - [x] Mock an `ExecutionRecord` where `ExecutionStatus.N_A` is reached.
  - [x] Verify that `SduiMapperService` maps the `N_A` trace to an SDUI component of type `n_a_card`.
  - [x] Assert that `short_circuit_reason_tda_ids` is mapped correctly to the SDUI card data.
- [x] Run `uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`
- [x] Run global tests `uv run pytest backend_v2/tests/` (Verify pass count >= 1117)
- [x] Update Epic 95 tracker (mark Phase 3a as `[x]`)
- [x] Issue Handover command for Phase 3b.

## Tier 2 Hardening (In Progress)
### backend_v2/models/dtos/
- [x] base.py
- [x] dag_models.py
- [x] evaluation_steps.py
- [x] inputs.py
- [x] prompt_context.py
- [x] quote_evidence.py
- [x] source_extraction_schema.py
- [x] state.py
- [ ] lightweight_matrix.py
- [ ] output_profile.py
- [ ] studio.py
- [ ] synthesis.py
- [ ] system.py
- [ ] trace.py

### backend_v2/services/orchestrator/
- [ ] (Pending)
