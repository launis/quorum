# Task Checklist: Decouple Inverse Evidence Null-Quotes, Fix Step 5 Ingestion Scoping, Calibrate Workflow Population Telemetry, Fix Matrix Reducer & Reseed Database

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
</required_context_rules>

- [x] Step 1: Phase 1: Pre-Implementation Technical Debt Cleanups
  - [x] In `backend_v2/hooks/scoring/matrix_hook.py`, eradicate 6-element anonymous state tuple `(pb_id, s_val, tda.concept_description, str(tda.aggregation_mode), tda.inverse_evidence, pb_model.allow_contextual_override)` and define `AtomScoringRuleDTO(BaseModel)` with typed fields
  - [x] Replace positional index access (`atom_mapping[aid][5]`) with typed property dot-notation (`rule.allow_contextual_override`)
  - [x] Eradicate silent `except ValidationError: pass` blocks in `matrix_hook.py` (lines 250, 322) and replace with structured logging
  - [x] Eradicate silent `except ValidationError: return ""` in `source_document_packer.py` and replace with `logger.error` and `AppException(ErrorCodes.VALIDATION_FAILED)`
  - [x] Eradicate hardcoded string `"0 (Kaikki 305 atomia, Tuotanto)"` in `diff_executions.py` line 1534
- [x] Step 2: Model Extension in `v2_core.py`
  - [x] Add `is_inverse_evidence: Annotated[bool, Field(default=False)]` to `AtomResultDTO`
  - [x] Update `validate_cognitive_vs_system_state` on `AtomResultDTO` to allow `PASSED` with null quote when `is_inverse_evidence is True`
- [x] Step 2b: Cross-Domain Freezed Parity in `atom_result_dto.dart`
  - [x] Add `@JsonKey(name: 'is_inverse_evidence') @Default(false) bool isInverseEvidence` to `AtomResultDTO` in `client_app_v2/lib/features/execution/models/atom_result_dto.dart`
  - [x] Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/atom_result_dto.dart --build`
- [x] Step 3: Decouple Quote-Less Inverse Passing in `result_projector.py`
  - [x] Check `node.atom.is_inverse` in `ResultProjector.project`
  - [x] Set `source_quote=None`, `contextual_override=False`, `is_inverse_evidence=True` for inverse passed claims
- [x] Step 4: Sovereign Inverse Evidence Preservation in `matrix_hook.py`
  - [x] Update `matrix_scoring_hook` evaluation resolution loop
  - [x] Prevent `enable_contextual_overrides: false` from demoting verified inverse evidence passes to `FALSE`
- [x] Step 5: Prior Step Output Ingestion & Scoping in `source_document_packer.py` and `llm.py`
  - [x] Support `$steps` references in `SourceDocumentPacker.resolve_allowed_keys`
  - [x] Pack prior step outputs into `global_source_text` for downstream sensor evaluations
- [x] Step 6: Self-Contained Differential Reporting & Population Calibration in `diff_executions.py`
  - [x] Replace static "305 atomia" label with dynamic workflow atom population resolution
  - [x] Output Workflow Provenance & Invariants Snapshot: workflow ID, localized name, version, governance switches (`enable_contextual_overrides`, `scoring_strategy`, `strictness_level`)
  - [x] Annotate blocks with human-readable titles, categories, and scale extrema from `prompt_blocks` in `seed_data.json`
  - [x] Render full scoring breakdown: raw scores vs normalized scores, level-by-level breakdown, and exact waterfall break point
  - [x] Render Evidence Class & Override Distribution (empirical quotes, inverse passes, overrides, policy demotions, failures)
  - [x] Resolve and display concrete physical model bindings (actual model strings, temperature, token budgets)
  - [x] Implement two-tier ontology: candidate deliverables (`chat_log_user_only`, `product_text`, `reflection_text`) vs external frameworks (`assignment_context`, `compliance_framework`, `source_evidence`, `chat_log_ai_only`)
  - [x] Append aggregated summary row for total User Documentation Volume
- [x] Step 7: Harmonize Workflow Invariants in `seed_data.json` & Reseed Database
  - [x] Set `enable_contextual_overrides: true` across all workflows (`wf_01`, `wf_03`, `wf_04`, `wf_05`) in `seed_data.json`
  - [x] Harmonize external framework `input_modes` to declare `assignment` mode (`is_assignment: true`) for `source_evidence` and `compliance_framework`
  - [x] Add `assignment_context: $inputs.assignment_context` to `sr_02c1d71000000008` in `wf_02`
  - [x] Run pre-flight validation: `run_seed.py local --dry-run` and `audit_database_atoms.py --strict`
  - [x] Update `test_competency_workflows_seed.py` assertions and run unit test
  - [x] Execute `uv run python backend_v2/seed/run_seed.py local`
- [x] Step 8: Fix Ghost Matrix Reducer & LLM Telemetry Attribution
  - [x] In `MatrixReducer.reduce_matrix`, iterate over `record.step_states.values()` instead of `record.steps`
  - [x] Forward `execution_id` and `step_id` from `TDAEngine` through `EnrichedDagExecutor.execute_graph` to `ExtractiveSensorService.evaluate_atom_boolean_batch`
  - [x] Propagate `execution_id` and `step_id` to `validation_context` in `evaluate_atom_boolean_batch`
  - [x] Update unit tests in `test_matrix_reducer.py` and `test_extractive_sensor_service.py`
- [x] Step 9: Unit & Regression Test Verification (ISTQB Negative Partitions)
  - [x] Run `uv run pytest backend_v2/tests/unit/test_report_data_dto.py`
  - [x] Run `uv run pytest backend_v2/tests/unit/services/orchestrator/test_result_projector.py`
  - [x] Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/atom_result_dto.dart --build`
  - [x] Run `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -k "inverse"`
  - [x] Run `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py`
  - [x] Run `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py`
  - [x] Run `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py`
  - [x] Run `uv run pytest backend_v2/tests/unit/test_diff_executions.py`
  - [x] Run `uv run pytest backend_v2/tests/unit -q` (3,318 tests passed)
  - [x] Run `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`

- [x] Step 10: Post-Audit Quality Gate Remediation
  - [x] Import `Any` from `typing` in `test_source_document_packer.py` and `test_diff_executions.py` (resolving fatal `F821 Undefined name Any`)
  - [x] Wrap lines exceeding 120 chars across `matrix_hook.py`, `source_document_packer.py`, `diff_executions.py`, and `test_diff_executions.py`
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` and confirm 100% PASS with exit code 0 (94.64% test coverage, 3,318 tests passed)
  - [x] Perform atomic git commit `b7683c11`

---

# Session Handover Context

## Achieved
- **Step 1 (`8bedb17a`):** Pre-Implementation Technical Debt Cleanups: eradicated anonymous 6-tuple with `AtomScoringRuleDTO`, removed silent validation swallows in `matrix_hook.py` and `source_document_packer.py`, replaced hardcoded "305" label in `diff_executions.py`.
- **Step 2 & 2b (`d7efd7b5`):** Added `is_inverse_evidence: bool = False` to Python `AtomResultDTO` (`backend_v2/models/v2_core.py`) and Flutter `AtomResultDTO` (`client_app_v2/lib/features/execution/models/atom_result_dto.dart`) with `@JsonKey(name: 'is_inverse_evidence') @Default(false) bool isInverseEvidence`, verified via `flutter_audit_loop.py --build`.
- **Step 3 (`53a10b9d`):** Decoupled quote-less inverse passing in `ResultProjector.project` (`backend_v2/services/orchestrator/result_projector.py`), setting `source_quote=None`, `contextual_override=False`, and `is_inverse_evidence=True`.
- **Step 4 (`5677f7d8`):** Sovereign inverse evidence preservation in `matrix_scoring_hook` (`backend_v2/hooks/scoring/matrix_hook.py`), resolving verified inverse passes unconditionally to `final_state = "TRUE"`.
- **Step 5 (`5240d3e0`):** Prior step output packing in `SourceDocumentPacker` (`source_document_packer.py` and `llm.py`) with fail-fast validation.
- **Step 6 (`9ceda040`):** Calibrated dynamic workflow population and self-contained differential reporting in `scripts/diff_executions.py` and unit tests in `test_diff_executions.py` (46 tests passed).
- **Step 7 (`c02390bc`):** Harmonized workflow invariants in `seed_data.json` (`enable_contextual_overrides: true`, `assignment` input modes for external frameworks), updated seed assertions, and re-seeded database.
- **Step 8 (`5a02fda6`):** Resolved ghost matrix reduction by iterating `record.step_states.values()` instead of `record.steps`, forwarded `execution_id` and `step_id` from `TDAEngine` through `EnrichedDagExecutor` to `ExtractiveSensorService.evaluate_atom_boolean_batch` in `validation_context`.
- **Step 9 (`092a4016`):** Verified ISTQB negative partitions, updated model regex error assertions, confirmed 3,318/3,318 unit tests passed and SDUI semantic parity verified.
- **Step 10 (`b7683c11`):** Post-Audit Quality Gate Remediation: fixed `F821` missing `Any` imports in `test_source_document_packer.py` and `test_diff_executions.py`, wrapped lines exceeding 120 chars, and verified 100% exit code 0 across all 6 stages of `backend_audit_loop.py backend_v2 --test` with 94.64% coverage.

## Learned
- Iterating `record.steps` in `MatrixReducer.reduce_matrix` starved Phase 2 synthesis of all 85 evaluated atoms because `scorecard_atoms` is populated on `record.step_states.values()`.
- Error messages in Pydantic validators must be kept strictly synchronized with ISTQB test assertions when adding new domain invariants like `is_inverse_evidence`.
- Static analysis via `ruff check` catches deferred-evaluation type annotation scope leaks (such as `dict[str, Any]` missing `from typing import Any`) that Python 3.14 deferred evaluation allows during localized runtime test execution.

## Remaining
- All implementation plan and remediation steps (1-10) are 100% COMPLETE.
- Mandatory Red-Team Audit sign-off via `/tier8-audit-plan`.

## Resume Command
```powershell
/tier5-resume --target="@[task.md]" --workflow=/tier8-audit-plan
```
