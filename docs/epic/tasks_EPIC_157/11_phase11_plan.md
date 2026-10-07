# Phase 11: Extended Dict Eradication & Hardening (Re-Planning & True Pydantic DTO Enclosure)

**Overview:** Close all dict-audit blind spots and systematically eradicate the 12 AI evasion anti-patterns discovered in @[docs/epic/tasks_EPIC_157/11_phase11_audit_findings.md]: expand `_is_naked_dict_subscript` in `scripts/audit_dict_eradication.py` to match `dict`, `Dict`, `Mapping`, and `MutableMapping` when value type is `Any` or `object`; expand `_is_dict_type_node` in `scripts/_ast_guardrails.py` (QGR018) to match `Mapping` and `MutableMapping`; expand `_find_nested_dict_subscript` in `scripts/audit_dict_eradication.py` and `scripts/_ast_guardrails.py` to match `Mapping` and `MutableMapping` in both outer and inner positions; extend Metric 11 (`unauthorized_open_json_annotations`) to inspect `FunctionDef.returns` and `AsyncFunctionDef.returns` across `tests/`, banning `def _get_base_*() -> dict[..., JsonValue]`; fix test file path classification in `scripts/_ast_guardrails.py` and `scripts/audit_dict_eradication.py` to inspect `backend_v2/tests/` (ensuring `backend_v2/core/test_settings.py` is scanned as a production module); extend Stage 10 in `scripts/backend_audit_loop.py` to run `audit_dict_eradication.py backend_v2 scripts --strict`; eradicate `_MAPPING_ADAPTER: TypeAdapter[Mapping[...]]` type laundering from `matrix_explanation_service.py` and `source_document_packer.py`; narrow `DomainInputValue` in `backend_v2/models/domain/inputs.py` to purge open dictionary unions; eradicate chameleon `__getitem__` on `MatrixSetupDTO` in `test_matrix_hook.py`; replace `_get_base_*_dict` open JSON fixtures with concrete Pydantic V2 models (`Workflow`, `OutputProfile`, `SystemConfigModelRegistry`); replace `ctx = {}` unannotated dictionaries in `test_worker.py` with typed containers or in-memory fakes; replace `Sequence[Mapping[str, JsonValue]]` in scripts and tests with concrete DTOs; eradicate raw `Any` assigned dict literals (`: Any = {`) in `backend_v2/llm/client.py` and `backend_v2/tests/unit/services/test_blueprint.py`; eliminate anonymous state tuples in favor of immutable Pydantic V2 DTOs; eliminate dynamic `json.loads` bypassing Pydantic deserialization in `backend_v2/llm/ingress_pipeline.py` and purge dead `UniversalIngress` import from `backend_v2/llm/client.py`; eradicate `SimpleNamespace` chameleon container mocks across all 10 sites in `backend_v2/tests/unit/services/test_blueprint.py` in favor of concrete validated models (`Workflow`, `StepRule`, `StepOutputDTO`, `MCPAuditTrace`); ensure baseline test fixtures construct valid domain models through `model_validate` rather than bypassing validation via `model_construct`; and enforce 100% mathematical zero open-JSON fixture camouflage via Metric 11 (`unauthorized_open_json_annotations`) in `scripts/audit_dict_eradication.py` in automated Stage 10 quality gates while monotonically ratcheting `CURRENT_RESIDUAL_CEILINGS.p = 0` and `CURRENT_RESIDUAL_CEILINGS.m = 0` in `scripts/audit_warning_baseline.py`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] Phase 11: Extended Dict Eradication (Tests, scripts/, Mapping) (Epic baseline lines: #L602-L621, #L228-L229, #L259, #L105-L106); @[docs/epic/tasks_EPIC_157/11_phase11_audit_findings.md].

**Execution Pre-Conditions:** User statement "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" (Section 2.4 item 5) for `backend_v2/services/orchestrator/strategies/llm.py`, `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py`, `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`, and `backend_v2/services/orchestrator/matrix_explanation_service.py`.

**Target Files (101 files):**
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]
- `[MODIFY]` @[scripts/backend_audit_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]
- `[MODIFY]` @[scripts/audit_warning_baseline.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- `[MODIFY]` @[backend_v2/models/domain/inputs.py]
- `[MODIFY]` @[backend_v2/core/test_settings.py]
- `[MODIFY]` @[backend_v2/hooks/input_processing.py]
- `[MODIFY]` @[backend_v2/services/ingress/pdf_chat_extractor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_matrix_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py]
- `[MODIFY]` @[backend_v2/llm/client.py]
- `[MODIFY]` @[backend_v2/llm/ingress_pipeline.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py]
- `[MODIFY]` @[scripts/diff_executions.py]
- `[MODIFY]` @[scripts/sanitize_seed_vault.py]
- `[MODIFY]` @[scripts/audit_database_atoms.py]
- `[MODIFY]` @[scripts/matrix_slice_engine.py]
- `[MODIFY]` @[scripts/reconcile_storage.py]
- `[MODIFY]` @[scripts/matrix_hardening_generator.py]
- `[MODIFY]` @[scripts/migrate_seed_contrastive_pairs.py]
- `[MODIFY]` Residual Active Test Files (72 files, 253 lines) enumerated in @[docs/epic/EPIC_157_residual_ledger.md]:
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
   - In @[scripts/audit_dict_eradication.py], `_is_naked_dict_subscript` (lines 237-271) only inspected AST nodes with identifier `"dict"` or `"Dict"`. Permissive annotations using `Mapping[str, Any]`, `Mapping[str, object]`, `MutableMapping[str, Any]`, and `MutableMapping[str, object]` evaded static detection. Expanding the pattern match to include `"Mapping"` and `"MutableMapping"` closed this typing hole permanently.
2. **Test File Path Classification Heuristic (`test_` Name Prefix vs `backend_v2/tests/` Path)**:
   - In @[scripts/audit_dict_eradication.py] and @[scripts/_ast_guardrails.py], test files were classified using `Path(filepath).name.startswith("test_")`. This heuristic misclassified the production module `backend_v2/core/test_settings.py` as a test file, exempting it from strict production AST guardrails and dict eradication checks. Updating both classification predicates to evaluate whether the normalized POSIX file path contains `backend_v2/tests/` restored production enforcement over `backend_v2/core/test_settings.py`.
3. **Disabled Annotation Checks for Test Suites in `audit_dict_eradication.py`**:
   - In @[scripts/audit_dict_eradication.py], `visit_AnnAssign`, `visit_FunctionDef`, and `visit_AsyncFunctionDef` guarded naked dict annotation checks behind `not self.is_test`. Removing `not self.is_test` from the naked dict subscript check allows `audit_dict_eradication.py` to enforce typed test fixtures repo-wide.
4. **Outdated Stage 10 Argument Scope in `backend_audit_loop.py`**:
   - In @[scripts/backend_audit_loop.py], Stage 10 previously invoked `audit_dict_eradication.py` with argument `backend_v2` only. Updating Stage 10 to supply arguments `backend_v2 scripts` ensures continuous static verification across all Python infrastructure.
5. **Untyped Dynamic Fallback Duck-Typing Branches in `llm.py` and `context_builder.py`**:
   - In @[backend_v2/services/orchestrator/strategies/llm.py] and @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py], methods accepted `HookState | Mapping[str, Any]` and attempted dictionary unpacking. Restricting parameter to `state_data: HookState`, constructing the composite lookup dictionary, and deleting legacy fallback branches removed Census M sites 6, 7, and 8.
6. **PyMuPDF Vector Drawing Parameter in `pdf_chat_extractor.py`**:
   - In @[backend_v2/services/ingress/pdf_chat_extractor.py], method `_is_user_bubble_drawing` annotated parameter `d` as `Mapping[str, object]`. Defining dedicated type alias `DrawingItemValue = fitz.Rect | tuple[float, ...] | list[float] | float | int | str | bool | None` and annotating `d: Mapping[str, DrawingItemValue]` resolved Census M site 5.
7. **Unmonitored Naked Dicts across 9 Maintenance and Audit Scripts**:
   - In 9 maintenance and audit scripts (`run_e2e_variance_test.py`, `diff_executions.py`, `sanitize_seed_vault.py`, `audit_database_atoms.py`, `audit_dict_eradication.py`, `matrix_slice_engine.py`, `reconcile_storage.py`, `matrix_hardening_generator.py`, `migrate_seed_contrastive_pairs.py`), 96 lines utilized `dict[str, Any]` or `dict[str, object]`. Retyping domain payloads to concrete Pydantic DTOs eradicates Census P in `scripts/`.
8. **Residual `dict[str, Any]` and `dict[str, object]` Test Fixture Payloads across 73 Test Files**:
   - Across 73 active test files, 255 lines annotated test fixtures, mock responses, and intermediate variables as `dict[str, Any]` or `dict[str, object]`. Retyping them to concrete domain DTOs (specifically: `ExecutionRecord`, `StepOutputDTO`, `AtomResultDTO`, `LevelStatsDTO`, `Workflow`, `OutputProfile`) eradicates Census P in test suites.
9. **Anti-Pattern 1: Open-JSON Camouflage (`dict[str, Any]` -> `dict[str, JsonValue]`)**:
   - In ~150 test fixture annotations and scripts, `Any` was substituted with `JsonValue` to bypass Census P while evading Metric 11 (`unauthorized_open_json_annotations`), which was previously restricted by `if self.is_domain_or_service:`. Extending Metric 11 to inspect `FunctionDef.returns` in `tests/` and replacing fixtures with concrete Pydantic V2 models (`Workflow`, `OutputProfile`, `StepOutputDTO`) eliminates open-JSON camouflage.
10. **Anti-Pattern 2: Primitive Obsession Bypass (`list[dict]` -> `Sequence[Mapping[str, JsonValue]]`)**:
    - In scripts and tests (specifically `test_ast_prompt_xml_sovereignty.py`, `test_scoring.py`, `test_overfit_token_sanitization.py`, `audit_database_atoms.py`, `diff_executions.py`, `run_e2e_variance_test.py`, `sanitize_seed_vault.py`), `list[dict[str, Any]]` was converted to `Sequence[Mapping[str, JsonValue]]` to bypass primitive obsession checks. Expanding `_find_nested_dict_subscript` in @[scripts/audit_dict_eradication.py] to match `Mapping` and `MutableMapping` in both outer and inner positions closes this hole.
11. **Anti-Pattern 3: Inner Dict Disguise (`dict[str, dict]` -> `dict[str, Mapping[str, JsonValue]]`)**:
    - In `test_matrix_anchoring_rules.py`, `diff_executions.py`, and `run_e2e_variance_test.py`, nested dictionaries were retyped to `dict[str, Mapping[str, JsonValue]]`. Expanding AST nested dict inspection to flag `Mapping` and `MutableMapping` mandates genuine DTO encapsulation.
12. **Anti-Pattern 4: QGR018 Type Laundering in Production Services (`TypeAdapter(Mapping[...])`)**:
    - In @[backend_v2/services/orchestrator/matrix_explanation_service.py] (`_MAPPING_ADAPTER: TypeAdapter[Mapping[str, JsonValue]]` at line 34) and @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py] (`_MAPPING_ADAPTER: TypeAdapter[Mapping[str, DomainInputValue]]` at line 23), wrapping dictionaries in `Mapping` bypassed QGR018 because `_is_dict_type_node` only matched `dict`/`Dict`. Expanding `_is_dict_type_node` in @[scripts/_ast_guardrails.py] to match `Mapping` and `MutableMapping`, and deleting the `_MAPPING_ADAPTER` instances along with their fallback parsing branches, restores single-pipeline determinism.
13. **Anti-Pattern 5: Stripping Type Annotations (`ctx = {...}`)**:
    - In @[backend_v2/tests/unit/test_worker.py] (12 test functions), removing `: dict[str, Any]` annotations left unannotated mutable dictionary variables (`ctx = {...}`) to evade Census P. Replacing raw dictionary contexts with typed containers or in-memory repositories restores type transparency.
14. **Anti-Pattern 6: Chameleon Dictionary Dataclasses (`def __getitem__`)**:
    - In @[backend_v2/tests/unit/hooks/test_matrix_hook.py], wrapping mock containers in `MatrixSetupDTO` with `def __getitem__(self, key: str)` preserved legacy dictionary indexing. Deleting `__getitem__` and updating callers to dot notation (`matrix_setup.pb_id`) eradicates dictionary emulation.
15. **Anti-Pattern 7: Mega-Union Ingress Dicts (`DomainInputValue`)**:
    - In @[backend_v2/models/domain/inputs.py], `DomainInputValue` included `dict[str, str]`, `dict[str, float]`, and `dict[str, HydratedAtomDTO]`. Purging open dictionary unions from `DomainInputValue` ensures all domain payloads conform to concrete Pydantic V2 DTOs or primitive scalars.
16. **Anti-Pattern 8: Raw `object` or `Any` Assigned Dict Literals (`: Any = {` / `: object = {`)**:
    - In @[backend_v2/llm/client.py] (`adapter_schema: Any = {"type": "json_schema"}` at line 102), @[backend_v2/tests/unit/services/test_blueprint.py] (`workflow_steps: Any = {` at line 1807, and `mcp_audit_map: Any = {...}` at line 1815), variables were typed as `Any` while assigned dictionary literals directly, evading `_is_naked_dict_subscript` because the AST annotation node lacked a subscript. Retyping `adapter_schema` to `dict[str, JsonValue]` in `client.py` and replacing test mock dictionaries with validated Pydantic models (`dict[str, StepRule]`, `dict[str, MCPAuditTrace]`) in `test_blueprint.py` eradicates these untyped dictionary assignments.
17. **Anti-Pattern 9: Anonymous Tuple State Packing ("Tuple Hell")**:
    - Packing multi-value states or key-value structures into anonymous tuples (specifically `tuple[dict, dict]` or `list[tuple[str, object]]`) evades dictionary audits while retaining loose associative access. Enforcing rule `ban_anonymous_state_tuples` repo-wide mandates that all multi-field return states and pipeline payloads are encapsulated in dedicated immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`).
18. **Anti-Pattern 10: Dynamic `json.loads` Deserialization Bypassing Schemas**:
    - In @[backend_v2/llm/ingress_pipeline.py] (`cast(dict[str, JsonValue], json.loads(raw_stripped))` at line 394) and dead `UniversalIngress` import in @[backend_v2/llm/client.py], dynamic text deserialization bypassed Pydantic schemas. Purging the dead `UniversalIngress` import from `client.py` and enforcing native Pydantic V2 Structured Outputs (`run_structured_task`) without manual syntactic repair fallbacks eliminates ad-hoc dictionary casting.
19. **Anti-Pattern 11: `SimpleNamespace` Chameleon Container Mocks**:
    - Across 10 sites exclusively in @[backend_v2/tests/unit/services/test_blueprint.py] (lines 1713, 1724, 1735, 1808, 1815, 1919, 1926, 1948, 2366, 2892), `types.SimpleNamespace` was imported and used to construct unvalidated mock objects with arbitrary attributes, evading Pydantic DTO contracts while mimicking object attribute access (`obj.attr`). Eradicating all `SimpleNamespace` imports and usages across `test_blueprint.py` by instantiating genuine validated Pydantic models (`Workflow`, `StepRule`, `StepOutputDTO`, `MCPAuditTrace`) completely purges `SimpleNamespace` repo-wide.
20. **Anti-Pattern 12: `model_construct()` Validation Bypassing in Fixtures**:
    - Using `Model.model_construct(...)` in test fixtures instead of `Model(...)` or `Model.model_validate(...)` bypasses schema validation and allows malformed dictionaries or mismatched types to bypass testing gates (specifically in @[backend_v2/tests/unit/test_worker.py] and @[backend_v2/tests/unit/services/test_blueprint.py]). Mandating that test fixture factories construct valid domain models through full Pydantic validation (`model_validate`) ensures test suites exercise real validation invariants.
21. **Zero Drive-By Schema Mutation Invariant**:
    - Purging unapproved shadow fields (specifically `j` on `ResidualDebtCeilingsDTO` defined in `scripts/audit_warning_baseline.py`) ensures permanent schema stability. Metric 11 (`unauthorized_open_json_annotations`) in `scripts/audit_dict_eradication.py` is the sovereign AST engine for zero open-JSON fixture returns in automated Stage 10 quality gates without mutating `ResidualDebtCeilingsDTO`.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/audit_dict_eradication.py]` and `@[scripts/_ast_guardrails.py]` | Banned name-prefix test classification (`Path(filepath).name.startswith("test_")`); banned `Mapping` and `MutableMapping` blind spot in `_is_naked_dict_subscript`, `_is_dict_type_node` (QGR018), and `_find_nested_dict_subscript`; banned exempting test files from open-JSON return type checks (`def _get_base_*() -> dict[..., JsonValue]`). | Inspect normalized POSIX path for `backend_v2/tests/` to classify test files; match `dict`, `Dict`, `Mapping`, and `MutableMapping` with `Any` or `object` values; expand QGR018 to flag `TypeAdapter` on `Mapping`/`MutableMapping`; extend Metric 11 to check `FunctionDef.returns` and `AsyncFunctionDef.returns` across `tests/`. | Clean AST matching via standard library `ast.walk`; zero regex or heuristics on annotations. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py backend_v2/tests/unit/scripts/test_ast_guardrails.py` passes 100%. |
| `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` | Banned missing unit test coverage for `Mapping`/`MutableMapping` naked dict detection, QGR018 `TypeAdapter(Mapping)` detection, nested `Sequence[Mapping]` detection, test path classification, and Metric 11 test return checks. | Add unit tests asserting: (1) `Mapping[str, Any]` and `MutableMapping[str, object]` produce `naked_dict_annotations` violations; (2) `TypeAdapter(Mapping[str, JsonValue])` produces QGR018 violation; (3) `Sequence[Mapping[str, JsonValue]]` produces nested dict violation; (4) `def _get_base_workflow() -> dict[str, JsonValue]` in a test file produces Metric 11 violation; (5) `backend_v2/core/test_settings.py` is scanned as production. | Hermetic in-memory AST visitor tests with synthetic code snippets. | Unit tests fail before audit engine update, pass cleanly after. |
| `@[scripts/backend_audit_loop.py]` and `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]` | Banned Stage 10 scanning only `backend_v2`, leaving `scripts/` unmonitored. | Configure Stage 10 command to `["uv", "run", "python", "scripts/audit_dict_eradication.py", "backend_v2", "scripts", "--strict"]`; update unit test assertion to match both target directories. | Single unified audit call covering both root modules. | `backend_v2/tests/unit/scripts/test_backend_audit_loop.py` verifies Stage 10 target invocation. |
| `@[backend_v2/core/test_settings.py]` | Banned `TEST_SETTINGS_OVERRIDES: dict[str, Any]` and `merged: dict[str, Any]`. | Retype `TEST_SETTINGS_OVERRIDES: dict[str, int | str]`; eliminate intermediate `merged` variable by returning `Settings(**TEST_SETTINGS_OVERRIDES, **custom_overrides)` directly. | Direct dictionary unpacking into Pydantic Settings constructor; zero intermediary variables. | Census M regex finds 0 occurrences in `test_settings.py`; `get_test_settings()` succeeds. |
| `@[backend_v2/hooks/input_processing.py]` | Banned `Mapping[str, object]` annotations on `raw_inputs` and `dynamic_inputs` in `_extract_raw_value`. | Retype `raw_inputs: Mapping[str, DomainInputValue] = state.inputs.raw_inputs` and `dynamic_inputs: Mapping[str, DomainInputValue] = state.inputs.dynamic_inputs`. | Native reuse of `DomainInputValue` from `ExecutionInputsDTO`. | Census M regex finds 0 occurrences in `input_processing.py`; hook tests pass. |
| `@[backend_v2/services/ingress/pdf_chat_extractor.py]` | Banned `d: Mapping[str, object]` on `_is_user_bubble_drawing`. | Define `type DrawingItemValue = fitz.Rect | tuple[float, ...] | list[float] | float | int | str | bool | None`; annotate `d: Mapping[str, DrawingItemValue]`. | Pure type alias without heavyweight wrapper classes; zero runtime translation. | Census M regex finds 0 occurrences in `pdf_chat_extractor.py`; unit tests pass. |
| `@[backend_v2/services/orchestrator/strategies/llm.py]` | Banned legacy duck-typing fallback branch attempting dictionary conversion on `hook_state.inputs`; banned passing loose state dict to `ContextBuilder.build`. | Direct dot-notation access: `raw_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.raw_inputs` and `dynamic_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.dynamic_inputs`; pass `state_data=hook_state` at line 517; delete lines 160-164. | Zero fallback branching; relies strictly on `HookState` and `ExecutionInputsDTO` domain contracts. | Census M regex finds 0 occurrences in `llm.py`; orchestrator tests pass. |
| `@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]` | Banned `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, DomainInputValue]]`, `dict_payload: Mapping[str, IngressInputValue | object]`, and `step_dict_payload: Mapping[str, object] | None = None`. | Delete `_MAPPING_ADAPTER` and eradicate fallback parsing branch; retype `dict_payload: Mapping[str, DomainInputValue]` and `step_dict_payload: Mapping[str, DomainInputValue] | None = None`. | Direct Pydantic validation via `ExecutionInputsDTO`; zero wrapper adapters. | Census M regex finds 0 occurrences in `source_document_packer.py`; QGR018 passes; packer tests pass. |
| `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]` | Banned `state_data: HookState | Mapping[str, Any]` union and lines 275-285, 343-346, 379-382 dictionary unpacking logic. | Restrict parameter to `state_data: HookState`; delete lines 275-285, 343-346, 379-382; construct lookup state `lookup_state = {"inputs": state_data.inputs.raw_inputs, "raw_inputs": state_data.inputs.raw_inputs, **state_data.inputs.dynamic_inputs, **state_data.inputs.raw_inputs}` to resolve dot notation. | Eradicates bifurcated dictionary-vs-DTO handling; single sovereign pipeline. | Census M regex finds 0 occurrences in `context_builder.py`; context builder tests pass. |
| `@[backend_v2/services/orchestrator/matrix_explanation_service.py]` | Banned `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, JsonValue]]` (line 34) and fallback dictionary parsing branch (lines 180-196). | Delete `_MAPPING_ADAPTER`; enforce deterministic type branching on `ExecutionInputsDTO | str`; purge dictionary fallback branch. | Native direct DTO extraction without intermediate Mapping adapter. | QGR018 flags zero violations; `backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py` passes 100%. |
| `@[backend_v2/models/domain/inputs.py]` | Banned open dictionary types (`dict[str, str]`, `dict[str, float]`, and `dict[str, HydratedAtomDTO]`) inside `DomainInputValue` union. | Narrow `DomainInputValue` union to exclude open dictionaries, restricting ingress inputs to scalar primitives, validated DTOs, and homogeneous scalar sequences. | Strict union type definition without open-ended catch-alls. | AST guardrail Metric 11 and QGR001 pass; domain input serialization tests pass. |
| `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]` and `@[backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py]` | Banned passing raw dictionaries `state_data = {"document_text": ...}` to `ContextBuilder.build`. | Update unit tests to construct and pass typed `HookState(inputs=ExecutionInputsDTO(...))` instances. | Typed domain fixtures; zero loose dictionaries. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py` passes 100%. |
| `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]` | Banned chameleon dictionary dataclass (`def __getitem__` on `MatrixSetupDTO`) enabling bracket indexing emulation. | Eradicate `__getitem__`; refactor test callers to access attributes via dot notation (`matrix_setup.mock_repo`). | Standard dataclass without custom container emulation. | `uv run pytest backend_v2/tests/unit/hooks/test_matrix_hook.py` passes 100%. |
| `@[backend_v2/tests/unit/test_worker.py]` | Banned stripping type annotations (`ctx = {}`) on mutable context dictionaries to bypass Census P; banned open-JSON camouflage returns (`def _get_base_*_dict() -> dict[str, JsonValue]`). | Modernize test fixtures to instantiate typed Pydantic V2 state models (`SystemConfigModelRegistry`, `Workflow`, `OutputProfile`) or in-memory repository doubles. | Direct reuse of existing domain fixtures; zero ad-hoc dictionary state bags. | `uv run pytest backend_v2/tests/unit/test_worker.py` passes 100%. |
| `@[backend_v2/llm/client.py]` and `@[backend_v2/llm/ingress_pipeline.py]` | Banned `adapter_schema: Any = {"type": "json_schema"}` (line 102); banned dead import `from backend_v2.llm.ingress_pipeline import UniversalIngress` (line 23); banned `cast(dict[str, JsonValue], json.loads(raw_stripped))` (line 394 in `ingress_pipeline.py`). | Retype `adapter_schema: dict[str, JsonValue]`; purge dead `UniversalIngress` import from `client.py`; enforce Pydantic V2 schema validation on incoming text payloads in `ingress_pipeline.py`. | Zero dead imports; direct Pydantic validation instead of dynamic json.loads type casting. | `uv run pytest backend_v2/tests/unit/llm/test_llm_client_tiers.py backend_v2/tests/unit/services/execution/test_ingress_service.py` passes 100%. |
| `@[backend_v2/tests/unit/services/test_blueprint.py]` | Banned `types.SimpleNamespace` across 10 mock sites (lines 1713, 1724, 1735, 1808, 1815, 1919, 1926, 1948, 2366, 2892); banned `workflow_steps: Any = {` (line 1807) and `mcp_audit_map: Any = {...}` (line 1815); banned `model_construct()` validation bypassing (line 1937). | Replace all 10 `SimpleNamespace` mock sites with concrete Pydantic V2 models (`Workflow`, `StepRule`, `StepOutputDTO`, `MCPAuditTrace`); retype lines 1807 and 1815 to typed collections of domain models; enforce `model_validate`. | Zero `SimpleNamespace` chameleon objects; test fixtures instantiate real domain entities. | Python search for SimpleNamespace across `backend_v2` returns 0 results; `uv run pytest backend_v2/tests/unit/services/test_blueprint.py` passes 100%. |
| 8 Scripts Files: `@[scripts/run_e2e_variance_test.py]`, `@[scripts/diff_executions.py]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/audit_database_atoms.py]`, `@[scripts/matrix_slice_engine.py]`, `@[scripts/reconcile_storage.py]`, `@[scripts/matrix_hardening_generator.py]`, `@[scripts/migrate_seed_contrastive_pairs.py]` | Banned `Sequence[Mapping[str, JsonValue]]`, `dict[str, Mapping[str, JsonValue]]`, `dict[str, Any]`, and `dict[str, object]`. | Retype domain payloads to concrete Pydantic V2 DTOs (`ExecutionRecord`, `StepOutputDTO`, `AtomResultDTO`); retype raw JSON serialization blobs to typed models. | Standard Pydantic V2 DTOs; zero ad-hoc type laundering. | `audit_dict_eradication.py scripts --strict` reports 0 violations; Census P returns 0 matches across `scripts/`. |
| 21 Representative Test Files (from 72 active test files): `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/seed/test_overfit_token_sanitization.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]`, `@[backend_v2/tests/unit/llm/test_provider.py]`, `@[backend_v2/tests/unit/test_matrix_data_integrity.py]`, `@[backend_v2/tests/unit/api/routers/test_server_id_authority.py]`, `@[backend_v2/tests/unit/seed/test_inverse_atoms_clarity_criteria.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py]`, `@[backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py]`, `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]`, `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`, `@[backend_v2/tests/unit/hooks/test_input_processing.py]`, `@[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py]`, `@[backend_v2/tests/unit/llm/test_transient_error_detection.py]`, `@[backend_v2/tests/unit/models/test_trace_envelope.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`, `@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]`, `@[backend_v2/tests/unit/test_model_registry_discovery.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]` | Banned open-JSON camouflage (`def _get_base_*() -> dict[str, JsonValue]`), `Sequence[Mapping[str, JsonValue]]`, and `dict[str, Mapping[str, JsonValue]]`. | Retype fixture helper functions to return concrete validated Pydantic V2 models (`Workflow`, `OutputProfile`, `StepOutputDTO`); pass unannotated dictionary literals in negative tests asserting parsing failure. | Direct instantiation of existing domain models; zero loose dictionary plumbing. | Metric 11 returns 0 violations; `uv run pytest backend_v2/tests/` passes 100%. |
| `@[scripts/audit_warning_baseline.py]` | Banned residual debt ceilings `p > 0` and `m > 0`. | Monotonically ratchet `CURRENT_RESIDUAL_CEILINGS.p = 0` and `CURRENT_RESIDUAL_CEILINGS.m = 0`. | Hardcoded exact integer equality ratchet. | `uv run python scripts/audit_warning_baseline.py --verify-zero` passes with exit code 0. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; CENSUS P/M BASELINE AUDIT [COMPLETED]">
    <action>Look backward: Verify Phase 10 eradicated all # type: ignore comments (Census T=0) and enforced strict mypy ignore accounting with global warn_unused_ignores = true.</action>
    <action>Verify current baseline: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and confirm current ceilings (p=0, m=0, f=51, r=186, d=0, k=0, x=0, n=0, t=0, s=0).</action>
    <action>Verify live Census M: Run Census M search across `backend_v2` and confirm 0 active occurrences across production files.</action>
    <action>Verify live Census P: Run Census P search across `backend_v2/tests` and `scripts` and confirm exact count of active occurrences is 0.</action>
    <action>Look forward: Verify extended dict eradication across tests, scripts, and Mapping constructs completely eliminates loose dictionary typing from backend Python before Phase 12 client-side Dart permissive map eradication.</action>
    <constraint invariant="universal_fail_fast">If unexpected violations exist outside the residual ledger boundaries, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/11_phase11_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="AUDIT ENGINE MODERNIZATION &amp; AST GUARDRAIL HARDENING [COMPLETED]">
    <action>In @[scripts/audit_dict_eradication.py]: In `_is_naked_dict_subscript`, expand matching logic so that target subscript values matching `ast.Name(id="dict" | "Dict" | "Mapping" | "MutableMapping") | ast.Attribute(attr="dict" | "Dict" | "Mapping" | "MutableMapping")` with value type `Any` or `object` return True.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `self.is_test`, fix evaluation to inspect whether the normalized POSIX file path contains `"backend_v2/tests/"`, replacing `name.startswith("test_")` so `backend_v2/core/test_settings.py` is scanned as production.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `visit_AnnAssign`, `visit_FunctionDef`, and `visit_AsyncFunctionDef`, remove `not self.is_test` from the naked dict annotation check so `self._is_naked_dict_subscript` is checked on all non-exempt files including test files.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `self._is_test_file`, fix evaluation to inspect whether the normalized POSIX file path contains `"backend_v2/tests/"`, replacing `name.startswith("test_")` so `backend_v2/core/test_settings.py` is evaluated under production domain guardrails.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that `Mapping[str, Any]` and `Mapping[str, object]` annotations produce `naked_dict_annotations` violations.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that `MutableMapping[str, Any]` and `MutableMapping[str, object]` annotations produce `naked_dict_annotations` violations.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that a module located at `backend_v2/core/test_settings.py` is classified as `is_test = False` and `is_domain_or_service = True`.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting that a test file under `backend_v2/tests/` with `dict[str, Any]` annotation produces a `naked_dict_annotations` violation.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` asserting all unit tests pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Dict eradication audit must detect Mapping and MutableMapping with Any/object and enforce annotation checks across tests.</constraint>
  </step>

  <step id="2" name="AUDIT LOOP STAGE 10 EXTENSION [COMPLETED]">
    <action>In @[scripts/backend_audit_loop.py]: In Stage 10, update subprocess call to `["uv", "run", "python", "scripts/audit_dict_eradication.py", "backend_v2", "scripts", "--strict"]` to include `scripts/` directory in automated quality gate.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]: Update test expectations asserting that Stage 10 executes `audit_dict_eradication.py` over both `backend_v2` and `scripts` targets.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_backend_audit_loop.py` asserting all unit tests pass 100%.</action>
    <constraint invariant="universal_quality_gates">Stage 10 must audit both backend_v2 and scripts directories in strict mode.</constraint>
  </step>

  <step id="3" name="CENSUS M PRODUCTION FILES ERADICATION &amp; 1-HOP CALLER SYNCHRONIZATION [COMPLETED]">
    <action>In @[backend_v2/core/test_settings.py]: Retype `TEST_SETTINGS_OVERRIDES: dict[str, int | str] = {...}` eliminating `Any`. In `get_test_settings(**custom_overrides: Any)`, eliminate the intermediate `merged: dict[str, Any]` variable by returning `Settings(**TEST_SETTINGS_OVERRIDES, **custom_overrides)` directly.</action>
    <action>In @[backend_v2/hooks/input_processing.py]: In `_extract_raw_value`, retype `raw_inputs: Mapping[str, DomainInputValue] = state.inputs.raw_inputs` and `dynamic_inputs: Mapping[str, DomainInputValue] = state.inputs.dynamic_inputs`, using the SSOT `DomainInputValue` from `state.inputs`.</action>
    <action>In @[backend_v2/services/ingress/pdf_chat_extractor.py]: Define type alias `type DrawingItemValue = fitz.Rect | tuple[float, ...] | list[float] | float | int | str | bool | None`. In `_is_user_bubble_drawing`, retype parameter `d: Mapping[str, DrawingItemValue]`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py]: In `execute`, retype `raw_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.raw_inputs` and `dynamic_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.dynamic_inputs`. Delete legacy fallback duck-typing logic. At line 517, update invocation to `ContextBuilder.build(input_mappings=input_mappings, state_data=hook_state, output_profile=output_profile, schema_map=schema_map, criteria_blocks=criteria_blocks, blueprint_labels=blueprint_labels)`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]: Retype `dict_payload: Mapping[str, DomainInputValue]` and `step_dict_payload: Mapping[str, DomainInputValue] | None = None`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]: In `build`, restrict parameter `state_data: HookState` (purging `| Mapping[str, Any]`). Extract `extracted_metadata = state_data.metadata` and `extracted_raw_inputs = dict(state_data.inputs.raw_inputs)`. Construct `lookup_state = {"inputs": state_data.inputs.raw_inputs, "raw_inputs": state_data.inputs.raw_inputs, **state_data.inputs.dynamic_inputs, **state_data.inputs.raw_inputs}` to resolve dot notation. Delete legacy duck-typing fallback lines.</action>
    <action>In 1-hop test callers @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py] and @[backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py]: Modernize test fixtures to instantiate and pass typed `HookState(inputs=ExecutionInputsDTO(...))` instances rather than raw dictionaries.</action>
    <action>Execute localized verification: Run Census M search across `backend_v2` and assert exactly 0 matches.</action>
    <action>Execute localized tests: Run `uv run pytest backend_v2/tests/unit/core/test_test_settings.py backend_v2/tests/unit/hooks/test_input_processing.py backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py backend_v2/tests/unit/services/orchestrator/strategies/test_fail_fast_inputs_resolution.py` asserting all pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Census M must be reduced to exactly 0 matches across all production files.</constraint>
  </step>

  <step id="4" name="CENSUS P SCRIPTS ERADICATION (INITIAL) [COMPLETED]">
    <action>In @[scripts/run_e2e_variance_test.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/diff_executions.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/sanitize_seed_vault.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/audit_database_atoms.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/matrix_slice_engine.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/reconcile_storage.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/matrix_hardening_generator.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>In @[scripts/migrate_seed_contrastive_pairs.py]: Eradicate occurrences of `dict[str, Any]` and `dict[str, object]`.</action>
    <action>Execute localized verification: Run Census P search across `scripts/` and assert exactly 0 matches.</action>
    <constraint invariant="the_zero_compromise_pledge">Census P must be reduced to exactly 0 matches across all scripts files.</constraint>
  </step>

  <step id="5" name="CENSUS P TEST SUITES ERADICATION (INITIAL) [COMPLETED]">
    <action>In test suites Batch A through Batch E across 73 test files: Initial mechanical eradication of `dict[str, Any]` and `dict[str, object]` achieved Census P=0.</action>
    <constraint invariant="the_zero_compromise_pledge">Initial mechanical eradication completed; discovered evasion anti-patterns require hardening in Steps 5-H through 8-H.</constraint>
  </step>

  <step id="5-H" name="AST GUARDRAIL HARDENING &amp; METRIC 11 RETURN EXTENSION">
    <action>In @[scripts/audit_dict_eradication.py]: Expand `_find_nested_dict_subscript` to match `Mapping` and `MutableMapping` in both outer and inner positions (specifically banning `Sequence[Mapping[...]]` and `dict[str, Mapping[...]]`).</action>
    <action>In @[scripts/audit_dict_eradication.py]: Extend Metric 11 (`unauthorized_open_json_annotations`) to inspect `visit_FunctionDef` and `visit_AsyncFunctionDef` returns annotations across test files, banning return types matching `dict[str, JsonValue]` or `Mapping[str, JsonValue]` in fixture helper methods.</action>
    <action>In @[scripts/_ast_guardrails.py]: Expand `_is_dict_type_node` (QGR018) to match `Mapping` and `MutableMapping` in addition to `dict`/`Dict`, preventing `TypeAdapter(Mapping[...])` type laundering.</action>
    <action>In @[scripts/_ast_guardrails.py]: Expand `_find_nested_dict_subscript` to match `Mapping` and `MutableMapping` in both outer and inner positions.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting `def _get_base_workflow() -> dict[str, JsonValue]` in a test module produces Metric 11 violation.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test asserting `Sequence[Mapping[str, JsonValue]]` produces `primitive_obsession_nested_dicts` violation.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]: Add unit test asserting `TypeAdapter(Mapping[str, JsonValue])` produces QGR018 violation.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py backend_v2/tests/unit/scripts/test_ast_guardrails.py` asserting all pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Audit engines must detect and block all 12 evasion anti-patterns.</constraint>
  </step>

  <step id="6-H" name="PRODUCTION SERVICE LAUNDERING ERADICATION &amp; INGRESS PURGE">
    <action>In @[backend_v2/services/orchestrator/matrix_explanation_service.py]: Eradicate `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, JsonValue]]` (line 34) and purge the legacy fallback dictionary parsing branch (lines 180-196), enforcing deterministic extraction strictly on `ExecutionInputsDTO | str`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]: Eradicate `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, DomainInputValue]]` (line 23) and purge the fallback dictionary parsing branch (lines 228-241), validating step inputs directly against `ExecutionInputsDTO`.</action>
    <action>In @[backend_v2/models/domain/inputs.py]: Narrow `DomainInputValue` union by purging open dictionary members (`dict[str, str]`, `dict[str, float]`, and `dict[str, HydratedAtomDTO]`), ensuring ingress payloads conform to concrete Pydantic DTOs or primitive scalars.</action>
    <action>In @[backend_v2/llm/client.py]: Retype line 102 `adapter_schema: dict[str, JsonValue] = {"type": "json_schema"}` eliminating raw `Any` dict assignment (Anti-Pattern 8), and purge dead import line 23 `from backend_v2.llm.ingress_pipeline import UniversalIngress`.</action>
    <action>In @[backend_v2/llm/ingress_pipeline.py]: Enforce Pydantic V2 validation on deserialized payloads, eliminating `cast(dict[str, JsonValue], json.loads(raw_stripped))` (Anti-Pattern 10).</action>
    <action>Execute localized tests: Run `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py backend_v2/tests/unit/models/domain/test_inputs.py backend_v2/tests/unit/llm/test_llm_client_tiers.py backend_v2/tests/unit/services/execution/test_ingress_service.py` asserting all pass 100%.</action>
    <constraint invariant="zero_service_layer_fallbacks">Production services must never launder dictionaries through TypeAdapter or fallback parsing branches.</constraint>
  </step>

  <step id="7-H" name="TRUE PYDANTIC DTO ENCLOSURE IN TEST FIXTURES &amp; SCRIPTS">
    <action>In @[backend_v2/tests/unit/hooks/test_matrix_hook.py]: Eradicate `__getitem__` on `MatrixSetupDTO`; refactor test callers to access attributes via dot notation (`matrix_setup.mock_repo`).</action>
    <action>In @[backend_v2/tests/unit/test_worker.py]: Replace stripped unannotated mutable dictionary contexts (`ctx = {}`) with typed Pydantic models or in-memory fakes.</action>
    <action>In @[backend_v2/tests/unit/services/test_blueprint.py]: Eradicate all 10 `SimpleNamespace` mock sites (lines 1713, 1724, 1735, 1808, 1815, 1919, 1926, 1948, 2366, 2892) (Anti-Pattern 11), retyping lines 1807 and 1815 from `: Any = {` (Anti-Pattern 8) to concrete validated Pydantic V2 models (`dict[str, StepRule]`, `dict[str, MCPAuditTrace]`).</action>
    <action>In test fixture factories across target test files: Verify test fixtures construct domain models through full Pydantic validation (`model_validate`) rather than bypassing validation via `model_construct()` (Anti-Pattern 12).</action>
    <action>Across all target files: Enforce immutable Pydantic V2 DTOs for multi-field state transit, eliminating anonymous tuple state packing (Anti-Pattern 9).</action>
    <action>In @[scripts/run_e2e_variance_test.py]: Replace `Sequence[Mapping[str, JsonValue]]` with concrete DTOs (`list[StepOutputDTO]`, `list[ScaleDTO]`).</action>
    <action>In @[scripts/diff_executions.py]: Replace `Sequence[Mapping[str, JsonValue]]` and `dict[str, Mapping[str, JsonValue]]` with concrete DTOs.</action>
    <action>In @[scripts/sanitize_seed_vault.py]: Replace `Sequence[Mapping[str, JsonValue]]` with concrete DTOs.</action>
    <action>In @[scripts/audit_database_atoms.py]: Replace `Sequence[Mapping[str, JsonValue]]` with concrete DTOs.</action>
    <action>In @[scripts/matrix_slice_engine.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[scripts/reconcile_storage.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[scripts/matrix_hardening_generator.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[scripts/migrate_seed_contrastive_pairs.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_scoring.py]: Replace open JSON camouflage returns (`dict[str, JsonValue]`) and `Sequence[Mapping]` with concrete DTOs (`Workflow`, `OutputProfile`, `StepOutputDTO`).</action>
    <action>In @[backend_v2/tests/unit/seed/test_overfit_token_sanitization.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/test_worker_synthesis.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/llm/test_provider.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/test_matrix_data_integrity.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/api/routers/test_server_id_authority.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/seed/test_inverse_atoms_clarity_criteria.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/test_seed_architectural_guardrails.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_input_processing.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/llm/test_transient_error_detection.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/models/test_trace_envelope.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/test_model_registry_discovery.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>In @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]: Replace open JSON fixtures with concrete DTOs.</action>
    <action>Execute localized verification: Run `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` asserting 0 violations.</action>
    <constraint invariant="the_zero_compromise_pledge">All test fixtures and scripts must enclose data in genuine validated Pydantic V2 DTOs.</constraint>
  </step>

  <step id="8-H" name="MONOTONIC RATCHET UPDATE &amp; UNIVERSAL TWO-STAGE VERIFICATION GATE">
    <action>In @[scripts/audit_warning_baseline.py]: Verify `CURRENT_RESIDUAL_CEILINGS` enforces `p=0` and `m=0` with zero regressions.</action>
    <action>Run localized baseline ledger check: `uv run python scripts/audit_warning_baseline.py --verify-zero` and assert returncode 0.</action>
    <action>Run strict dict eradication audit over both scopes: `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` and assert `TOTAL VIOLATIONS: 0`.</action>
    <action>Run global two-stage verification gate: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` and assert all 10 stages pass with exit code 0.</action>
    <constraint invariant="universal_quality_gates">All 10 stages of backend_audit_loop.py must pass with 0 warnings, 0 AST violations, Census P=0, and Census M=0.</constraint>
  </step>

  <dod_checklist>
    <item>_is_naked_dict_subscript in scripts/audit_dict_eradication.py matches dict, Dict, Mapping, and MutableMapping with Any or object values.</item>
    <item>_is_test_file in scripts/_ast_guardrails.py and is_test in scripts/audit_dict_eradication.py evaluate normalized path for backend_v2/tests/ ensuring backend_v2/core/test_settings.py is scanned as production.</item>
    <item>_is_dict_type_node in scripts/_ast_guardrails.py matches Mapping and MutableMapping in addition to dict/Dict (QGR018).</item>
    <item>_find_nested_dict_subscript in scripts/audit_dict_eradication.py and scripts/_ast_guardrails.py flags Mapping and MutableMapping in inner and outer positions.</item>
    <item>Metric 11 in scripts/audit_dict_eradication.py inspects FunctionDef and AsyncFunctionDef returns in tests, banning dict[str, JsonValue] fixture returns.</item>
    <item>Stage 10 in scripts/backend_audit_loop.py executes audit_dict_eradication.py over backend_v2 and scripts.</item>
    <item>_MAPPING_ADAPTER and fallback dictionary parsing branches are eradicated from matrix_explanation_service.py and source_document_packer.py.</item>
    <item>DomainInputValue in backend_v2/models/domain/inputs.py excludes open dictionary unions.</item>
    <item>Chameleon __getitem__ is eradicated from MatrixSetupDTO in test_matrix_hook.py.</item>
    <item>Stripped unannotated mutable dictionary contexts (ctx = {}) in test_worker.py are replaced with typed models or fakes.</item>
    <item>Raw Any assigned dict literals (: Any = {) in backend_v2/llm/client.py and backend_v2/tests/unit/services/test_blueprint.py are eradicated.</item>
    <item>Dead UniversalIngress import in backend_v2/llm/client.py is purged, and dynamic json.loads bypassing in backend_v2/llm/ingress_pipeline.py is eliminated.</item>
    <item>All 10 SimpleNamespace mock sites in backend_v2/tests/unit/services/test_blueprint.py are eradicated in favor of concrete validated Pydantic V2 models, ensuring zero SimpleNamespace occurrences repo-wide.</item>
    <item>Anonymous state tuples are eradicated in favor of immutable Pydantic V2 DTOs.</item>
    <item>Baseline test fixtures construct valid domain models through model_validate rather than bypassing validation via model_construct.</item>
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

