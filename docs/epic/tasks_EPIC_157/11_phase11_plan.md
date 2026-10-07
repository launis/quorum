# Phase 11: Extended Dict Eradication (Tests, scripts/, Mapping)

**Overview:** Close the dict-audit blind spots: expand `_is_naked_dict_subscript` in `scripts/audit_dict_eradication.py` to match `dict`, `Dict`, `Mapping`, and `MutableMapping` when value type is `Any` or `object`; fix `_is_test_file` in `scripts/_ast_guardrails.py` and `is_test` in `scripts/audit_dict_eradication.py` to use path check `backend_v2/tests/` (ensuring `backend_v2/core/test_settings.py` is scanned as a production module); enforce annotation checks across test files; and extend Stage 10 in `scripts/backend_audit_loop.py` to run `audit_dict_eradication.py backend_v2 scripts --strict`. Eradicate Census M (9 active production sites across 6 files) and Census P (351 active residual lines across 9 `scripts/` files [96 lines] and 73 test files [255 lines] enumerated in @[docs/epic/EPIC_157_residual_ledger.md]). Monotonically ratchet `CURRENT_RESIDUAL_CEILINGS.p = 0` and `CURRENT_RESIDUAL_CEILINGS.m = 0` in `scripts/audit_warning_baseline.py`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] Phase 11: Extended Dict Eradication (Tests, scripts/, Mapping) (Epic baseline lines: #L602-L621, #L228-L229, #L259, #L105-L106).

**Execution Pre-Conditions:** User statement "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" (Section 2.4 item 5) for `backend_v2/services/orchestrator/strategies/llm.py`, `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py`, and `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`.

**Target Files (96 files):**
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[scripts/backend_audit_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]
- `[MODIFY]` @[scripts/audit_warning_baseline.py]
- `[MODIFY]` @[backend_v2/core/test_settings.py]
- `[MODIFY]` @[backend_v2/hooks/input_processing.py]
- `[MODIFY]` @[backend_v2/services/ingress/pdf_chat_extractor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py]
- `[MODIFY]` @[scripts/diff_executions.py]
- `[MODIFY]` @[scripts/sanitize_seed_vault.py]
- `[MODIFY]` @[scripts/audit_database_atoms.py]
- `[MODIFY]` @[scripts/matrix_slice_engine.py]
- `[MODIFY]` @[scripts/reconcile_storage.py]
- `[MODIFY]` @[scripts/matrix_hardening_generator.py]
- `[MODIFY]` @[scripts/migrate_seed_contrastive_pairs.py]
- `[MODIFY]` Residual Active Test Files (73 files, 255 lines) enumerated in @[docs/epic/EPIC_157_residual_ledger.md]:
  - `@[backend_v2/tests/unit/hooks/test_scoring.py]` (46 lines)
  - `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]` (29 lines)
  - `@[backend_v2/tests/unit/test_worker.py]` (16 lines)
  - `@[backend_v2/tests/unit/seed/test_overfit_token_sanitization.py]` (12 lines)
  - `@[backend_v2/tests/unit/test_worker_synthesis.py]` (9 lines)
  - `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]` (8 lines)
  - `@[backend_v2/tests/unit/llm/test_provider.py]` (8 lines)
  - `@[backend_v2/tests/unit/test_matrix_data_integrity.py]` (7 lines)
  - `@[backend_v2/tests/unit/api/routers/test_server_id_authority.py]` (6 lines)
  - `@[backend_v2/tests/unit/seed/test_inverse_atoms_clarity_criteria.py]` (6 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py]` (6 lines)
  - `@[backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py]` (5 lines)
  - `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]` (5 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]` (5 lines)
  - `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]` (5 lines)
  - `@[backend_v2/tests/unit/hooks/test_input_processing.py]` (4 lines)
  - `@[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py]` (4 lines)
  - `@[backend_v2/tests/unit/llm/test_transient_error_detection.py]` (4 lines)
  - `@[backend_v2/tests/unit/models/test_trace_envelope.py]` (4 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]` (4 lines)
  - `@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]` (4 lines)
  - `@[backend_v2/tests/unit/test_model_registry_discovery.py]` (4 lines)
  - `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]` (3 lines)
  - `@[backend_v2/tests/unit/database/test_tinydb_resilience.py]` (3 lines)
  - `@[backend_v2/tests/unit/llm/adapters/test_base_adapter.py]` (3 lines)
  - `@[backend_v2/tests/unit/llm/test_sdui_schema_discriminator_regression.py]` (3 lines)
  - `@[backend_v2/tests/unit/scripts/test_diff_executions.py]` (3 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]` (3 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]` (3 lines)
  - `@[backend_v2/tests/unit/services/test_competency_workflows_seed.py]` (3 lines)
  - `@[backend_v2/tests/unit/test_input_processing.py]` (3 lines)
  - `@[backend_v2/tests/unit/test_main.py]` (3 lines)
  - `@[backend_v2/tests/unit/database/repositories/test_execution.py]` (2 lines)
  - `@[backend_v2/tests/unit/hooks/test_passivity_hook.py]` (2 lines)
  - `@[backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py]` (2 lines)
  - `@[backend_v2/tests/unit/llm/test_adaptive_retry.py]` (2 lines)
  - `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]` (2 lines)
  - `@[backend_v2/tests/unit/llm/test_provider_toolcalls.py]` (2 lines)
  - `@[backend_v2/tests/unit/models/domain/test_output_profile.py]` (2 lines)
  - `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]` (2 lines)
  - `@[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py]` (2 lines)
  - `@[backend_v2/tests/unit/seed/test_run_seed.py]` (2 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py]` (2 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]` (2 lines)
  - `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]` (2 lines)
  - `@[backend_v2/tests/unit/services/test_blueprint.py]` (2 lines)
  - `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` (2 lines)
  - `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]` (2 lines)
  - `@[backend_v2/tests/unit/test_epic93_contract_verification.py]` (2 lines)
  - `@[backend_v2/tests/unit/test_v2_core_models.py]` (2 lines)
  - `@[backend_v2/tests/conftest.py]` (1 line)
  - `@[backend_v2/tests/fakes/in_memory_repositories.py]` (1 line)
  - `@[backend_v2/tests/test_worker_models_used.py]` (1 line)
  - `@[backend_v2/tests/unit/api/routers/test_output_profile_metric_mappings_retention.py]` (1 line)
  - `@[backend_v2/tests/unit/database/test_tinydb_driver.py]` (1 line)
  - `@[backend_v2/tests/unit/llm/test_provider_penalties.py]` (1 line)
  - `@[backend_v2/tests/unit/llm/test_provider_retry_after.py]` (1 line)
  - `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]` (1 line)
  - `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` (1 line)
  - `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]` (1 line)
  - `@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]` (1 line)
  - `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]` (1 line)
  - `@[backend_v2/tests/unit/services/mcp/test_dispatcher.py]` (1 line)
  - `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]` (1 line)
  - `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]` (1 line)
  - `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]` (1 line)
  - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` (1 line)
  - `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py]` (1 line)
  - `@[backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py]` (1 line)
  - `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]` (1 line)
  - `@[backend_v2/tests/unit/test_backend_l10n_internal_parity.py]` (1 line)
  - `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]` (1 line)
  - `@[backend_v2/tests/unit/test_tier4_metric_mappings_bug.py]` (1 line)
  - `@[backend_v2/tests/unit/test_tier4_profile_dto_bug.py]` (1 line)
  - `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]` (1 line)
  - `@[backend_v2/tests/unit/utils/test_math_utils.py]` (1 line)
  - `@[backend_v2/tests/unit/workers/test_variance_synthesis.py]` (1 line)

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Blind Spot in `_is_naked_dict_subscript` for `Mapping` and `MutableMapping`**:
   - In @[scripts/audit_dict_eradication.py], `_is_naked_dict_subscript` (lines 236-267) only inspects AST nodes with identifier `"dict"` or `"Dict"`. Permissive annotations using `Mapping[str, Any]`, `Mapping[str, object]`, `MutableMapping[str, Any]`, and `MutableMapping[str, object]` evade static detection. Expanding the pattern match to include `"Mapping"` and `"MutableMapping"` closes this typing hole permanently.
2. **Test File Path Classification Heuristic (`test_` Name Prefix vs `backend_v2/tests/` Path)**:
   - In @[scripts/audit_dict_eradication.py] (lines 206-208) and @[scripts/_ast_guardrails.py] (lines 396-400), test files are classified using `Path(filepath).name.startswith("test_")`. This heuristic misclassifies the production module `backend_v2/core/test_settings.py` as a test file, exempting it from strict production AST guardrails and dict eradication checks. Updating both classification predicates to evaluate whether the normalized POSIX file path contains `backend_v2/tests/` restores production enforcement over `backend_v2/core/test_settings.py`.
3. **Disabled Annotation Checks for Test Suites in `audit_dict_eradication.py`**:
   - In @[scripts/audit_dict_eradication.py] (lines 384-585), `visit_AnnAssign`, `visit_FunctionDef`, and `visit_AsyncFunctionDef` guard naked dict annotation checks behind `not self.is_test`. This permits loose `dict[str, Any]` and `dict[str, object]` annotations to proliferate in test suites. Removing `not self.is_test` from the naked dict subscript check allows `audit_dict_eradication.py` to enforce typed test fixtures repo-wide.
4. **Outdated Stage 10 Argument Scope in `backend_audit_loop.py`**:
   - In @[scripts/backend_audit_loop.py] (lines 476-482), Stage 10 invokes `audit_dict_eradication.py` with argument `backend_v2` only. As a result, maintenance and audit scripts in `scripts/` escape the automated quality gate. Updating Stage 10 to supply arguments `backend_v2 scripts` ensures continuous static verification across all Python infrastructure.
5. **Untyped Dynamic Fallback Duck-Typing Branches in `llm.py` and `context_builder.py`**:
   - In @[backend_v2/services/orchestrator/strategies/llm.py] (lines 154-164), lines 159-164 contain legacy fallback duck typing attempting to unpack `hook_state.inputs` as a dictionary if not an `ExecutionInputsDTO`. `HookState.inputs` is natively typed as an immutable `ExecutionInputsDTO`. In @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py] (lines 236-483), the method accepts `HookState | Mapping[str, Any]`, with lines 275-285, 343-346, and 379-382 attempting dictionary unpacking. Eliminating the union in favor of strict `HookState`, constructing the lookup dictionary `lookup_state = {"inputs": state_data.inputs.raw_inputs, "raw_inputs": state_data.inputs.raw_inputs, **state_data.inputs.dynamic_inputs, **state_data.inputs.raw_inputs}`, and deleting the fallback branches removes Census M sites 6, 7, and 8. Callers @[backend_v2/services/orchestrator/strategies/llm.py] (lines 510-525), @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py], and @[backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py] are updated to pass `HookState`.
6. **PyMuPDF Vector Drawing Parameter in `pdf_chat_extractor.py`**:
   - In @[backend_v2/services/ingress/pdf_chat_extractor.py] (lines 113-230), method `_is_user_bubble_drawing` annotates parameter `d` as `Mapping[str, object]`. Defining a dedicated typed type alias `DrawingItemValue = fitz.Rect | tuple[float, ...] | list[float] | float | int | str | bool | None` and annotating `d: Mapping[str, DrawingItemValue]` resolves Census M site 5 without runtime overhead or loose duck typing.
7. **Unmonitored Naked Dicts across 9 Maintenance and Audit Scripts**:
   - In `scripts/run_e2e_variance_test.py` (35 lines), `scripts/diff_executions.py` (27 lines), `scripts/sanitize_seed_vault.py` (16 lines), `scripts/audit_database_atoms.py` (4 lines), `scripts/audit_dict_eradication.py` (5 lines), `scripts/matrix_slice_engine.py` (3 lines), `scripts/reconcile_storage.py` (3 lines), `scripts/matrix_hardening_generator.py` (2 lines), and `scripts/migrate_seed_contrastive_pairs.py` (1 line), 96 lines utilize `dict[str, Any]` or `dict[str, object]`. Retyping these to `dict[str, JsonValue]` for JSON payloads or typed domain DTOs eradicates Census P in `scripts/`.
8. **Residual `dict[str, Any]` and `dict[str, object]` Test Fixture Payloads across 73 Test Files**:
   - Across 73 active test files, 255 lines annotate test fixtures, mock responses, and intermediate variables as `dict[str, Any]` or `dict[str, object]`. Retyping them to `dict[str, JsonValue]` for open JSON payload fixtures and dedicated domain DTOs (specifically: `ExecutionRecord`, `StepOutputDTO`, `AtomResultDTO`, `LevelStatsDTO`) eradicates Census P in test suites.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/audit_dict_eradication.py]` and `@[scripts/_ast_guardrails.py]` | Banned name-prefix test classification (`Path(filepath).name.startswith("test_")`); banned `Mapping` and `MutableMapping` blind spot in `_is_naked_dict_subscript`; banned exempting test files from annotation audit. | Inspect normalized POSIX path for `backend_v2/tests/` to classify test files; match `dict`, `Dict`, `Mapping`, and `MutableMapping` with `Any` or `object` values; enforce naked dict annotation checks across all non-exempt files including test files. | Clean AST matching via standard library `ast.walk`; zero regex or heuristics on annotations. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` passes 100%. |
| `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]` | Banned missing unit test coverage for `Mapping`/`MutableMapping` naked dict detection, test path classification, and test annotation enforcement. | Add unit tests asserting: (1) `Mapping[str, Any]` produces `naked_dict_annotations` violation; (2) `MutableMapping[str, object]` produces violation; (3) `backend_v2/core/test_settings.py` is scanned as production; (4) test file annotations trigger violations. | Hermetic in-memory AST visitor tests with synthetic code snippets. | Unit tests fail before audit engine update, pass cleanly after. |
| `@[scripts/backend_audit_loop.py]` and `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]` | Banned Stage 10 scanning only `backend_v2`, leaving `scripts/` unmonitored. | Configure Stage 10 command to `["uv", "run", "python", "scripts/audit_dict_eradication.py", "backend_v2", "scripts", "--strict"]`; update unit test assertion to match both target directories. | Single unified audit call covering both root modules. | `backend_v2/tests/unit/scripts/test_backend_audit_loop.py` verifies Stage 10 target invocation. |
| `@[backend_v2/core/test_settings.py]` | Banned `TEST_SETTINGS_OVERRIDES: dict[str, Any]` and `merged: dict[str, Any]`. | Retype `TEST_SETTINGS_OVERRIDES: dict[str, int | str]`; eliminate intermediate `merged` variable by returning `Settings(**TEST_SETTINGS_OVERRIDES, **custom_overrides)` directly. | Direct dictionary unpacking into Pydantic Settings constructor; zero intermediary variables. | Census M regex finds 0 occurrences in `test_settings.py`; `get_test_settings()` succeeds. |
| `@[backend_v2/hooks/input_processing.py]` | Banned `Mapping[str, object]` annotations on `raw_inputs` and `dynamic_inputs` in `_extract_raw_value`. | Retype `raw_inputs: Mapping[str, DomainInputValue] = state.inputs.raw_inputs` and `dynamic_inputs: Mapping[str, DomainInputValue] = state.inputs.dynamic_inputs`. | Native reuse of `DomainInputValue` from `ExecutionInputsDTO`. | Census M regex finds 0 occurrences in `input_processing.py`; hook tests pass. |
| `@[backend_v2/services/ingress/pdf_chat_extractor.py]` | Banned `d: Mapping[str, object]` on `_is_user_bubble_drawing`. | Define `type DrawingItemValue = fitz.Rect | tuple[float, ...] | list[float] | float | int | str | bool | None`; annotate `d: Mapping[str, DrawingItemValue]`. | Pure type alias without heavyweight wrapper classes; zero runtime translation. | Census M regex finds 0 occurrences in `pdf_chat_extractor.py`; unit tests pass. |
| `@[backend_v2/services/orchestrator/strategies/llm.py]` | Banned legacy duck-typing fallback branch attempting dictionary conversion on `hook_state.inputs`; banned passing loose state dict to `ContextBuilder.build`. | Direct dot-notation access: `raw_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.raw_inputs` and `dynamic_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.dynamic_inputs`; pass `state_data=hook_state` at line 517; delete lines 160-164. | Zero fallback branching; relies strictly on `HookState` and `ExecutionInputsDTO` domain contracts. | Census M regex finds 0 occurrences in `llm.py`; orchestrator tests pass. |
| `@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]` | Banned `dict_payload: Mapping[str, IngressInputValue | object]` and `step_dict_payload: Mapping[str, object] | None = None`. | Retype `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, DomainInputValue]] = TypeAdapter(Mapping[str, DomainInputValue])`; retype `dict_payload: Mapping[str, DomainInputValue]` and `step_dict_payload: Mapping[str, DomainInputValue] | None = None`. | Strict domain typing via `DomainInputValue`. | Census M regex finds 0 occurrences in `source_document_packer.py`; packer tests pass. |
| `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]` | Banned `state_data: HookState | Mapping[str, Any]` union and lines 275-285, 343-346, 379-382 dictionary unpacking logic. | Restrict parameter to `state_data: HookState`; delete lines 275-285, 343-346, 379-382; construct lookup state `lookup_state = {"inputs": state_data.inputs.raw_inputs, "raw_inputs": state_data.inputs.raw_inputs, **state_data.inputs.dynamic_inputs, **state_data.inputs.raw_inputs}` to resolve dot notation. | Eradicates bifurcated dictionary-vs-DTO handling; single sovereign pipeline. | Census M regex finds 0 occurrences in `context_builder.py`; context builder tests pass. |
| `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]` and `@[backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py]` | Banned passing raw dictionaries `state_data = {"document_text": ...}` to `ContextBuilder.build`. | Update unit tests to construct and pass typed `HookState(inputs=ExecutionInputsDTO(...))` instances. | Typed domain fixtures; zero loose dictionaries. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py` passes 100%. |
| 9 Scripts Files: `@[scripts/run_e2e_variance_test.py]`, `@[scripts/diff_executions.py]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/audit_database_atoms.py]`, `@[scripts/matrix_slice_engine.py]`, `@[scripts/reconcile_storage.py]`, `@[scripts/matrix_hardening_generator.py]`, `@[scripts/migrate_seed_contrastive_pairs.py]`, `@[scripts/audit_dict_eradication.py]` | Banned 96 lines of `dict[str, Any]` and `dict[str, object]` in maintenance and audit scripts. | Retype JSON payloads to `dict[str, JsonValue]` (using `from pydantic import JsonValue`) and domain parameters to concrete Pydantic DTOs. | Native standard library and Pydantic V2 types; zero ad-hoc type laundering. | Census P returns 0 matches across `scripts/`; scripts execute cleanly. |
| 73 Test Files enumerated in `Target Files` | Banned 255 lines of `dict[str, Any]` and `dict[str, object]` in unit, integration, and e2e test suites. | Retype JSON fixtures to `dict[str, JsonValue]`; use typed domain DTOs (`ExecutionRecord`, `StepOutputDTO`, `AtomResultDTO`, `LevelStatsDTO`) for domain fixtures. | Standard typed test patterns; zero suppressions. | Census P returns 0 matches across `backend_v2/tests/`; test suite passes 100%. |
| `@[scripts/audit_warning_baseline.py]` | Banned residual debt ceilings `p=351` and `m=9`. | Monotonically ratchet `CURRENT_RESIDUAL_CEILINGS.p = 0` and `CURRENT_RESIDUAL_CEILINGS.m = 0`. | Hardcoded exact integer equality ratchet. | `uv run python scripts/audit_warning_baseline.py --verify-zero` passes with exit code 0. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; CENSUS P/M BASELINE AUDIT">
    <action>Look backward: Verify Phase 10 eradicated all # type: ignore comments (Census T=0) and enforced strict mypy ignore accounting with global warn_unused_ignores = true.</action>
    <action>Verify current baseline: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and confirm current ceilings (p=351, m=9, f=51, r=186, d=0, k=0, x=0, n=0, t=0, s=0).</action>
    <action>Verify live Census M: Run Census M search across `backend_v2` and confirm 9 active occurrences across 6 production files (`test_settings.py` 2, `input_processing.py` 2, `pdf_chat_extractor.py` 1, `llm.py` 2, `source_document_packer.py` 1, `context_builder.py` 1).</action>
    <action>Verify live Census P: Run Census P search across `backend_v2/tests` and `scripts` and confirm exact count of active occurrences across 9 scripts files (96 lines) and 73 test files (255 lines).</action>
    <action>Look forward: Verify extended dict eradication across tests, scripts, and Mapping constructs completely eliminates loose dictionary typing from backend Python before Phase 12 client-side Dart permissive map eradication.</action>
    <constraint invariant="universal_fail_fast">If unexpected violations exist outside the residual ledger boundaries, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/11_phase11_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="AUDIT ENGINE MODERNIZATION &amp; AST GUARDRAIL HARDENING (scripts/audit_dict_eradication.py, scripts/_ast_guardrails.py, test_audit_dict_eradication.py)">
    <action>In @[scripts/audit_dict_eradication.py]: In `_is_naked_dict_subscript` (lines 236-267), expand matching logic so that target subscript values matching `ast.Name(id="dict" | "Dict" | "Mapping" | "MutableMapping") | ast.Attribute(attr="dict" | "Dict" | "Mapping" | "MutableMapping")` with value type `Any` or `object` return True.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `self.is_test` (lines 206-208), fix evaluation to inspect whether the normalized POSIX file path contains `"backend_v2/tests/"`, replacing `name.startswith("test_")` so `backend_v2/core/test_settings.py` is scanned as production.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `visit_AnnAssign`, `visit_FunctionDef`, and `visit_AsyncFunctionDef` (lines 384-585), remove `not self.is_test` from the naked dict annotation check so `self._is_naked_dict_subscript` is checked on all non-exempt files including test files.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `self._is_test_file` (lines 396-400), fix evaluation to inspect whether the normalized POSIX file path contains `"backend_v2/tests/"`, replacing `name.startswith("test_")` so `backend_v2/core/test_settings.py` is evaluated under production domain guardrails.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that `Mapping[str, Any]` and `Mapping[str, object]` annotations produce `naked_dict_annotations` violations.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that `MutableMapping[str, Any]` and `MutableMapping[str, object]` annotations produce `naked_dict_annotations` violations.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that a module located at `backend_v2/core/test_settings.py` is classified as `is_test = False` and `is_domain_or_service = True`.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that a test file under `backend_v2/tests/` with `dict[str, Any]` annotation produces a `naked_dict_annotations` violation.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` asserting all unit tests pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Dict eradication audit must detect Mapping and MutableMapping with Any/object and enforce annotation checks across tests.</constraint>
  </step>

  <step id="2" name="AUDIT LOOP STAGE 10 EXTENSION (scripts/backend_audit_loop.py &amp; test_backend_audit_loop.py)">
    <action>In @[scripts/backend_audit_loop.py]: In Stage 10 (lines 476-482), update subprocess call to `["uv", "run", "python", "scripts/audit_dict_eradication.py", "backend_v2", "scripts", "--strict"]` to include `scripts/` directory in automated quality gate.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]: (lines 596-634) Update test expectations asserting that Stage 10 executes `audit_dict_eradication.py` over both `backend_v2` and `scripts` targets.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_backend_audit_loop.py` asserting all unit tests pass 100%.</action>
    <constraint invariant="universal_quality_gates">Stage 10 must audit both backend_v2 and scripts directories in strict mode.</constraint>
  </step>

  <step id="3" name="CENSUS M PRODUCTION FILES ERADICATION (6 FILES, 9 SITES) &amp; 1-HOP CALLER SYNCHRONIZATION">
    <action>In @[backend_v2/core/test_settings.py]: (lines 1-67) Retype `TEST_SETTINGS_OVERRIDES: dict[str, int | str] = {...}` eliminating `Any`. In `get_test_settings(**custom_overrides: Any)`, eliminate the intermediate `merged: dict[str, Any]` variable by returning `Settings(**TEST_SETTINGS_OVERRIDES, **custom_overrides)` directly.</action>
    <action>In @[backend_v2/hooks/input_processing.py]: In `_extract_raw_value` (lines 55-85), retype `raw_inputs: Mapping[str, DomainInputValue] = state.inputs.raw_inputs` and `dynamic_inputs: Mapping[str, DomainInputValue] = state.inputs.dynamic_inputs`, using the SSOT `DomainInputValue` from `state.inputs`.</action>
    <action>In @[backend_v2/services/ingress/pdf_chat_extractor.py]: Define type alias `type DrawingItemValue = fitz.Rect | tuple[float, ...] | list[float] | float | int | str | bool | None`. In `_is_user_bubble_drawing` (lines 113-230), retype parameter `d: Mapping[str, DrawingItemValue]`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py]: In `execute` (lines 154-164), retype `raw_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.raw_inputs` and `dynamic_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.dynamic_inputs`. Delete the legacy fallback lines 159-164 (`else: if not isinstance(hook_state.inputs, ...): dynamic_inputs_dict = dict(hook_state.inputs)`). At line 517, update invocation to `ContextBuilder.build(input_mappings=input_mappings, state_data=hook_state, output_profile=output_profile, schema_map=schema_map, criteria_blocks=criteria_blocks, blueprint_labels=blueprint_labels)`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]: Retype `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, DomainInputValue]] = TypeAdapter(Mapping[str, DomainInputValue])` (lines 23-25).</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]: Retype `dict_payload: Mapping[str, DomainInputValue]` (lines 225-240).</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]: Retype `step_dict_payload: Mapping[str, DomainInputValue] | None = None` (lines 305-320).</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]: In `build` (lines 236-483), restrict parameter `state_data: HookState` (purging `| Mapping[str, Any]`). Extract `extracted_metadata = state_data.metadata` and `extracted_raw_inputs = dict(state_data.inputs.raw_inputs)`. Construct `lookup_state = {"inputs": state_data.inputs.raw_inputs, "raw_inputs": state_data.inputs.raw_inputs, **state_data.inputs.dynamic_inputs, **state_data.inputs.raw_inputs}` to resolve dot notation. Delete legacy duck-typing fallback lines 275-285, 343-346, and 379-382.</action>
    <action>In 1-hop test callers @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py] and @[backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py]: Modernize test fixtures to instantiate and pass typed `HookState(inputs=ExecutionInputsDTO(...))` instances rather than raw dictionaries.</action>
    <action>Execute localized verification: Run Census M search across `backend_v2` and assert exactly 0 matches.</action>
    <action>Execute localized tests: Run `uv run pytest backend_v2/tests/unit/core/test_test_settings.py backend_v2/tests/unit/hooks/test_input_processing.py backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py` asserting all pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Census M must be reduced to exactly 0 matches across all production files.</constraint>
  </step>

  <step id="4" name="CENSUS P SCRIPTS ERADICATION (9 SCRIPTS FILES, 96 LINES)">
    <action>In @[scripts/run_e2e_variance_test.py]: Retype all 35 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]` (using `from pydantic import JsonValue`) or typed DTOs.</action>
    <action>In @[scripts/diff_executions.py]: Retype all 27 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]`.</action>
    <action>In @[scripts/sanitize_seed_vault.py]: Retype all 16 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]`.</action>
    <action>In @[scripts/audit_database_atoms.py]: Retype all 4 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: Retype all 5 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]` or typed DTO structures.</action>
    <action>In @[scripts/matrix_slice_engine.py]: Retype all 3 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]`.</action>
    <action>In @[scripts/reconcile_storage.py]: Retype all 3 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]`.</action>
    <action>In @[scripts/matrix_hardening_generator.py]: Retype both 2 occurrences of `dict[str, Any]` and `dict[str, object]` to `dict[str, JsonValue]`.</action>
    <action>In @[scripts/migrate_seed_contrastive_pairs.py]: Retype the 1 occurrence of `dict[str, Any]` to `dict[str, JsonValue]`.</action>
    <action>Execute localized verification: Run Census P search across `scripts/` and assert exactly 0 matches.</action>
    <constraint invariant="the_zero_compromise_pledge">Census P must be reduced to exactly 0 matches across all scripts files.</constraint>
  </step>

  <step id="5" name="CENSUS P TEST SUITES ERADICATION (73 TEST FILES, 255 LINES)">
    <action>In test suites Batch A (Hooks &amp; Workers - 4 files, 100 lines): Retype `dict[str, Any]` / `dict[str, object]` in `backend_v2/tests/unit/hooks/test_scoring.py` (46 lines), `backend_v2/tests/unit/hooks/test_matrix_hook.py` (29 lines), `backend_v2/tests/unit/test_worker.py` (16 lines), and `backend_v2/tests/unit/test_worker_synthesis.py` (9 lines) to `dict[str, JsonValue]` or concrete domain DTOs.</action>
    <action>In test suites Batch B (LLM, Adapters &amp; Models - 15 files, 60 lines): Retype `dict[str, Any]` / `dict[str, object]` in `backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py` (8), `backend_v2/tests/unit/llm/test_provider.py` (8), `backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py` (5), `backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py` (5), `backend_v2/tests/unit/llm/adapters/test_openai_adapter.py` (4), `backend_v2/tests/unit/llm/test_transient_error_detection.py` (4), `backend_v2/tests/unit/models/test_trace_envelope.py` (4), `backend_v2/tests/unit/llm/adapters/test_base_adapter.py` (3), `backend_v2/tests/unit/llm/test_sdui_schema_discriminator_regression.py` (3), `backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py` (2), `backend_v2/tests/unit/llm/test_adaptive_retry.py` (2), `backend_v2/tests/unit/llm/test_llm_client_tiers.py` (2), `backend_v2/tests/unit/llm/test_provider_toolcalls.py` (2), `backend_v2/tests/unit/models/domain/test_output_profile.py` (2), and `backend_v2/tests/unit/test_v2_core_models.py` (2) to `dict[str, JsonValue]` or concrete DTOs.</action>
    <action>In test suites Batch C (Seed &amp; Integrity - 8 files, 40 lines): Retype `dict[str, Any]` / `dict[str, object]` in `backend_v2/tests/unit/seed/test_overfit_token_sanitization.py` (12), `backend_v2/tests/unit/test_matrix_data_integrity.py` (7), `backend_v2/tests/unit/seed/test_inverse_atoms_clarity_criteria.py` (6), `backend_v2/tests/unit/test_seed_architectural_guardrails.py` (5), `backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py` (2), `backend_v2/tests/unit/seed/test_run_seed.py` (2), `backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py` (4), and `backend_v2/tests/unit/test_epic93_contract_verification.py` (2) to `dict[str, JsonValue]`.</action>
    <action>In test suites Batch D (Services &amp; Orchestrator - 13 files, 38 lines): Retype `dict[str, Any]` / `dict[str, object]` in `backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py` (6), `backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py` (5), `backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py` (4), `backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py` (3), `backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py` (3), `backend_v2/tests/unit/services/test_competency_workflows_seed.py` (3), `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py` (2), `backend_v2/tests/unit/services/orchestrator/test_dag_executor.py` (2), `backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py` (2), `backend_v2/tests/unit/services/test_blueprint.py` (2), `backend_v2/tests/unit/services/test_matrix_domain_parser.py` (2), `backend_v2/tests/unit/services/mcp/test_dispatcher.py` (1), and `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py` (1) to `dict[str, JsonValue]` or concrete DTOs.</action>
    <action>In test suites Batch E (Residual Test Files - 33 files, 46 lines): Retype `dict[str, Any]` / `dict[str, object]` in `api/routers/test_server_id_authority.py` (6), `test_model_registry_discovery.py` (4), `database/test_tinydb_resilience.py` (3), `scripts/test_diff_executions.py` (3), `test_main.py` (3), `database/repositories/test_execution.py` (2), `hooks/test_passivity_hook.py` (2), `scripts/test_run_e2e_variance_test.py` (2), `test_ast_domain_security_guardrails.py` (2), `tests/conftest.py` (1), `fakes/in_memory_repositories.py` (1), `test_worker_models_used.py` (1), `api/routers/test_output_profile_metric_mappings_retention.py` (1), `database/test_tinydb_driver.py` (1), `llm/test_provider_penalties.py` (1), `llm/test_provider_retry_after.py` (1), `models/dtos/test_output_profile.py` (1), `scripts/test_ast_guardrails.py` (1), `scripts/test_audit_database_atoms.py` (1), `scripts/test_sanitize_seed_vault.py` (1), `services/orchestrator/engines/test_synthesis_engine.py` (1), `services/orchestrator/engines/test_tda_engine.py` (1), `services/orchestrator/strategies/test_llm.py` (1), `services/orchestrator/test_anchor_validation_atom_result.py` (1), `services/orchestrator/test_matrix_reducer.py` (1), `services/orchestrator/test_synthesis_distiller_wiring.py` (1), `test_backend_l10n_internal_parity.py` (1), `test_concurrency_fuzzer.py` (1), `test_tier4_metric_mappings_bug.py` (1), `test_tier4_profile_dto_bug.py` (1), `utils/test_math_utils.py` (1), `workers/test_variance_synthesis.py` (1), and `scripts/test_audit_dict_eradication.py` (5) to `dict[str, JsonValue]` or typed DTOs.</action>
    <action>Execute localized verification: Run Census P search across `backend_v2/tests` and assert exactly 0 matches.</action>
    <constraint invariant="the_zero_compromise_pledge">Census P must be reduced to exactly 0 matches across all test files.</constraint>
  </step>

  <step id="6" name="MONOTONIC RATCHET UPDATE (p=0, m=0 in audit_warning_baseline.py) &amp; UNIVERSAL TWO-STAGE VERIFICATION GATE">
    <action>In @[scripts/audit_warning_baseline.py]: In `CURRENT_RESIDUAL_CEILINGS` (lines 68-80), update with monotonic ratchet: set `p=0` and `m=0`.</action>
    <action>Run localized baseline ledger check: `uv run python scripts/audit_warning_baseline.py --verify-zero` and assert returncode 0.</action>
    <action>Run strict dict eradication audit over both scopes: `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` and assert `TOTAL VIOLATIONS: 0`.</action>
    <action>Run global two-stage verification gate: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` and assert all 10 stages pass with exit code 0.</action>
    <constraint invariant="universal_quality_gates">All 10 stages of backend_audit_loop.py must pass with 0 warnings, 0 AST violations, Census P=0, and Census M=0.</constraint>
  </step>

  <dod_checklist>
    <item>_is_naked_dict_subscript in scripts/audit_dict_eradication.py matches dict, Dict, Mapping, and MutableMapping with Any or object values.</item>
    <item>_is_test_file in scripts/_ast_guardrails.py and is_test in scripts/audit_dict_eradication.py evaluate normalized path for backend_v2/tests/ ensuring backend_v2/core/test_settings.py is scanned as production.</item>
    <item>Naked dict annotation checks in scripts/audit_dict_eradication.py run across all non-exempt files including test files.</item>
    <item>Stage 10 in scripts/backend_audit_loop.py executes audit_dict_eradication.py over backend_v2 and scripts.</item>
    <item>All 9 Census M production sites across the 6 target files are eradicated with Census M returning 0 matches.</item>
    <item>All 96 lines of Census P across the 9 target scripts files are eradicated.</item>
    <item>All 255 lines of Census P across the 73 target test files are eradicated with Census P returning 0 matches.</item>
    <item>CURRENT_RESIDUAL_CEILINGS in scripts/audit_warning_baseline.py is ratcheted to p=0 and m=0.</item>
    <item>uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict reports TOTAL VIOLATIONS: 0.</item>
    <item>uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes all 10 stages with exit code 0.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT modify Dart files during Phase 11 (quarantined strictly for Phase 12 client permissive map eradication).</anti_target>
    <anti_target>Do NOT introduce unapproved JsonValue annotations into internal domain models outside OPEN_JSON_EXEMPTION_FILES (strictly banned by QGR027).</anti_target>
    <anti_target>Do NOT reintroduce legacy mock persistence fixtures in tests (strictly banned by QGR014).</anti_target>
    <anti_target>Do NOT add new fields or optional attributes to existing Pydantic DTOs without full-duplex schema parity audit.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census Verification: Verify Census P returns 0 matches (`Get-ChildItem backend_v2/tests, scripts -Recurse -Filter "*.py" | Select-String -Pattern "\b[Dd]ict\[\s*str\s*,\s*(?:Any|object)\s*\]"`).</action>
    <action>Execute Census Verification: Verify Census M returns 0 matches (`Get-ChildItem backend_v2 -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "\\backend_v2\\tests\\" } | Select-String -Pattern "\b(?:Mutable)?Mapping\[\s*str\s*,\s*(?:Any|object)\s*\]"`).</action>
    <action>Execute Baseline Ledger Gate: `uv run python scripts/audit_warning_baseline.py --verify-zero` reports all residual debt categories strictly conform to ratchet ceilings.</action>
    <action>Execute Extended Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Global Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes with all 10 stages clean.</action>
  </validation_gate>
</execution_protocol>
```
