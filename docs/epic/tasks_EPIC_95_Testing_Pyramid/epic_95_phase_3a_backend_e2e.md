# Epic 95 Phase 3a: Backend E2E Golden Master (NA_CARD Cascade)

## Context
**Source:** Epic 95 Phase 3
**Goal:** Verify the full E2E pipeline for N_A conditions (seed_data.json -> DAG Run -> ReportDataDTO -> SDUI Mapper -> ReportView). Solve the missing `n_a_card` block in backend SDUI models.

## Rules Injected
- `01-python-backend.md`: Fail-Fast, Pydantic V2 Strictness (`strict=True, extra='forbid'`).
- `ki_strict_icu_markdown_parity.md`: Backend only serves semantic markdown and SDUI.
- Tier 1 Mandates: Do not mix Backend and Frontend changes.

## Target Files (Modify)
- `backend_v2/models/view/sdui.py`
  - [NEW] Add `class SduiNACard(SduiBlockBase):` with `block_type: Literal["n_a_card"] = "n_a_card"`.
  - Add properties: `short_circuit_reason_tda_ids: list[str]` and `message: str`.
  - Append `SduiNACard` to `AnySduiBlock`.

- `backend_v2/tests/integration/test_epic_chain_e2e.py`
  - [NEW] Add `test_epic_95_na_cascade_e2e()`
  - Mock an `ExecutionRecord` where `ExecutionStatus.N_A` is reached.
  - Verify that `SduiMapperService` maps the `N_A` trace to an SDUI component of type `n_a_card`.
  - Assert that `short_circuit_reason_tda_ids` is mapped correctly to the SDUI card data.

## Target Files (Context / Read-Only)
- `backend_v2/services/sdui_mapper_service.py` (To see how `ReportDataDTO` handles `N_A`)

## Testing & Quality Gate Plan
- Run `uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`
- Run global tests to ensure no regressions `uv run pytest backend_v2/tests/`
- [BASELINE] Current pass count is 1116. Ensure it is >= 1117.

## Session Handover
To execute this phase, run the following command in a new session:
`/tier5-resume --workflow=/tier2-execute --target="docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_3a_backend_e2e.md" --rules="00-antigravity-core.md, 01-python-backend.md"`
