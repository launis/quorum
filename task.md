# Task Tracker: Restore Executive Summary & User Role Badge Rendering (Zero Fallbacks)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\a623781c-2dc9-4c51-af2d-26cb77ed2063\bug_fix_plan.md]

## 11 Tulostuslohkon auditointitulos (Audit Summary)
- [x] Kaikki 11 `TargetBlockType`-lohkoa tarkistettu tietokannasta ja raportista.
- [x] Vahvistettu: Mitään muita lohkoja ei ole poistettu profiileista.
- [x] Raportissa tulostui 31 SDUI-lohkoa (8 eri aktiivista lohkotyyppiä).
- [x] Eristetty: Vain Johdon tiivistelmä (`executive_summary_block`) ei tulostunut, johtuen kahdesta teknisestä bugista.

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint 1 (zero_service_layer_fallbacks): Eradicate `elif profile_cache and profile_cache.user_role:` fallback branch entirely. Zero fallback chains.
- [x] Constraint 2 (dumb_painter_ui): Adapter outputs pure SDUI `ParagraphBlock` instances; Flutter client remains an un-opinionated Dumb Painter.
- [x] Constraint 3 (zero_permissive_typing): `ExecutiveSummarySectionResult.executive_summary` must strictly enforce non-empty list validation (`min_length=1`).
- [x] Constraint 4 (prompt_asset_ssot_mandate): Centralize executive summary section rules in `backend_v2/models/prompts/synthesis/synthesis_directives.py`.
- [x] Constraint 5 (sdui_contract_fracture_prevention): Synchronously run `test_sdui_semantic_parity.py` upon adapter/model updates.

## Execution Tasks
- [x] **Step 1: SDUI ADAPTER DETERMINISTIC TARGET MATRIX KEY RESOLUTION (ZERO FALLBACKS)**
  - [x] 1.1: In `backend_v2/services/sdui/adapters/executive_summary_adapter.py`, iterate over `context.parsed_matrices.values()` to match `axis.block_id == profile.user_role_target_block`.
  - [x] 1.2: Completely eradicate the legacy `elif profile_cache and profile_cache.user_role:` fallback branch.
  - [x] 1.3: Verify regression tests in `test_executive_summary_adapter.py` (`test_build_matrix_target_block_with_composite_step_block_id_key` and `test_build_matrix_target_block_absent_omits_badge_without_fallback`) turn GREEN.
- [x] **Step 2: SYNTHESIS DTO SCHEMA ENFORCEMENT**
  - [x] 2.1: In `backend_v2/models/dtos/synthesis.py`, mandate `executive_summary: Annotated[list[LlmSduiBlock], Field(..., min_length=1)]`.
  - [x] 2.2: Update mock fixtures and unit tests in `backend_v2/tests/unit/models/dtos/test_synthesis.py` to supply at least one content block.
  - [x] 2.3: Verify regression test `test_executive_summary_section_result_requires_executive_summary` turns GREEN.
- [x] **Step 3: PROMPT DIRECTIVE SSOT ALIGNMENT IN WORKER**
  - [x] 3.1: In `backend_v2/models/prompts/synthesis/synthesis_directives.py`, define `EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX` aligning instructions with `executive_summary`.
  - [x] 3.2: In `backend_v2/worker.py`, replace `SYNTHESIS_SECTION_RULES_PREFIX` with `EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX` in `exec_section_rule`.
  - [x] 3.3: Update worker synthesis tests in `backend_v2/tests/unit/test_worker_synthesis.py`.
- [x] **Step 4: GLOBAL QUALITY GATE & SEMANTIC PARITY VERIFICATION**
  - [x] 4.1: Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py --test`.
  - [x] 4.2: Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/dtos/test_synthesis.py --test`.
  - [x] 4.3: Run `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
  - [x] 4.4: Verify with `scratch/test_bp.py` that `exe_708fbe4b51ca4e65` outputs role badge and report renders with 32 SDUI blocks.

# Session Handover Context
- **Status**: Complete (All 4 steps implemented and verified with 100% green tests).
- **Decision**: Zero fallback chains. Legacy `profile_cache.user_role` fallback branch eradicated. `ExecutiveSummaryAdapter` deterministically resolves user role from target matrix via `axis.block_id == profile.user_role_target_block`. Prompt directives centralized in SSOT `synthesis_directives.py` and aligned with strict `executive_summary` DTO schema (`min_length=1`).
- **Achieved**:
  - Deterministic target matrix resolution in `ExecutiveSummaryAdapter`
  - Strict Pydantic V2 schema for `ExecutiveSummarySectionResult.executive_summary` (min_length=1)
  - New SSOT constant `EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX` in `synthesis_directives.py` wired to `worker.py`
  - All unit and integration tests (adapter, synthesis DTOs, worker synthesis, SDUI semantic parity) pass 100%
  - Real execution blueprint `exe_708fbe4b51ca4e65` verified: role badge rendered, total blocks 32
- **Remaining**: User confirmation / atomic git commit.
