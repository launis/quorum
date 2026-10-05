# Phase 1: Physical Boundary SSOT, Pre-Implementation Cleanups & Model Typing with 1-hop Consumers

**Overview:** Replace basename exemptions with the path-based `BOUNDARY_EXEMPTION_FILES` SSOT, wire `scripts/audit_warning_baseline.py` (Residual Debt Ceiling Ledger) as Stage 9/10 of `scripts/backend_audit_loop.py`, introduce `QGR026` (FATAL skip/xfail ban) in `scripts/_ast_guardrails.py`, resolve seed, OpenAPI, repository, and guardrail-test debt, and retype all 30 model violations together with their 1-hop consumers and test fixtures in the same phase.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L295-L368] Phase 1: Physical Boundary SSOT, Pre-Implementation Cleanups & Model Typing with 1-hop Consumers

**Target Files:**
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/audit_warning_baseline.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]
- `[MODIFY]` @[scripts/backend_audit_loop.py#L282-L477]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[backend_v2/models/dtos/telemetry.py]
- `[MODIFY]` @[backend_v2/api/routers/system/telemetry.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/base_adapter.py]
- `[MODIFY]` @[backend_v2/scripts/generate_openapi.py]
- `[MODIFY]` @[backend_v2/seed/run_seed.py]
- `[MODIFY]` @[backend_v2/database/repositories/execution.py]
- `[MODIFY]` @[backend_v2/database/repositories/workflow.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L311-L353]
- `[MODIFY]` @[backend_v2/models/domain/base.py#L40-L128]
- `[MODIFY]` @[backend_v2/models/domain/analyst.py]
- `[MODIFY]` @[backend_v2/models/domain/archivist.py]
- `[MODIFY]` @[backend_v2/models/domain/integrity.py#L92-L118]
- `[MODIFY]` @[backend_v2/models/domain/mcp.py]
- `[MODIFY]` @[backend_v2/models/domain/metrics.py]
- `[MODIFY]` @[backend_v2/models/domain/security.py]
- `[MODIFY]` @[backend_v2/models/domain/system_config.py]
- `[MODIFY]` @[backend_v2/models/domain/validation.py]
- `[MODIFY]` @[backend_v2/models/domain/xai.py#L439-L465]
- `[MODIFY]` @[backend_v2/models/domain/xai.py#L468-L490]
- `[MODIFY]` @[backend_v2/models/dtos/atom_evaluation.py]
- `[MODIFY]` @[backend_v2/models/dtos/mcp.py]
- `[MODIFY]` @[backend_v2/models/dtos/prompt_context.py#L11-L33]
- `[MODIFY]` @[backend_v2/models/dtos/studio.py]
- `[MODIFY]` @[backend_v2/models/dtos/system.py]
- `[MODIFY]` @[backend_v2/models/dtos/trace.py#L157-L194]
- `[MODIFY]` @[backend_v2/models/llm.py#L63-L76]
- `[MODIFY]` @[backend_v2/models/llm.py#L426-L447]
- `[MODIFY]` @[backend_v2/models/dtos/context_variables.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_reducer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- `[MODIFY]` @[backend_v2/services/execution/ingress_service.py#L146-L250]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_ingress_service.py#L152-L227]
- `[MODIFY]` @[backend_v2/tests/unit/models/test_trace_envelope.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_trace.py]
- `[MODIFY]` @[backend_v2/tests/unit/seed/test_run_seed.py#L472-L496]
- `[DELETE]` @[backend_v2/tests/architecture/test_boundaries.py]
- `[DELETE]` @[backend_v2/tests/unit/test_epic_61_hardening.py]
- `[DELETE]` @[backend_v2/tests/unit/test_provider_rate_limit.py]
- `[DELETE]` @[backend_v2/tests/unit/llm/test_fallback_caching.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_matrix_data_integrity.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/_ast_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, `@[scripts/audit_warning_baseline.py]`, `@[scripts/backend_audit_loop.py#L282-L477]` | Banned basename matching that exempts any file sharing a name. Banned two divergent exemption sets. Banned exempting files under models, services, hooks, api. Banned unmonitored residual debt ceilings. Banned unconditional skip and xfail markers. | ONE `frozenset[str]` `BOUNDARY_EXEMPTION_FILES` of 15 workspace-relative POSIX paths, imported by identity into `audit_dict_eradication.py`. Define [NEW] `ResidualDebtCeilingsDTO` in `audit_warning_baseline.py` wired as Stage 9/10 in `backend_audit_loop.py`. Implement `QGR026` in `_ast_guardrails.py` banning unconditional skip and xfail. | Deleted `LOCKED_PHYSICAL_DRIVERS` symbol; no regex or glob discovery. Single shared SSOT set imported directly. | `backend_v2/tests/unit/scripts/test_ast_guardrails.py`: (1) every set member exists on disk; (2) a fixture file `models/dtos/telemetry.py` is NOT exempt; (3) no member starts with models, services, hooks, api. `backend_v2/tests/unit/scripts/test_audit_dict_eradication.py`: `audit_dict_eradication.BOUNDARY_EXEMPTION_FILES is _ast_guardrails.BOUNDARY_EXEMPTION_FILES`. Admission ratchet in `test_ast_guardrails.py`: each of the 9 newly admitted paths scanned with empty exemption set returns 0 violations. |
| `@[backend_v2/models/dtos/telemetry.py]`, `@[backend_v2/api/routers/system/telemetry.py]`, `@[backend_v2/services/sdui/adapters/base_adapter.py]`, `@[backend_v2/scripts/generate_openapi.py]`, `@[backend_v2/seed/run_seed.py]`, `@[backend_v2/database/repositories/execution.py]`, `@[backend_v2/database/repositories/workflow.py]`, `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L311-L353]` | Banned accidental basename exemption leakage. Banned loose dict validation buffers in seed data loading. Banned untyped OpenAPI specifications. Banned naked dictionary returns from repositories. Banned reflection `getattr` in guardrail test assertions. | Remediate accidental exemption loss files to 0 AST and dict violations. Define [NEW] `ValidatedSeedBufferDTO` for collection parsing in `run_seed.py`. Retype OpenAPI spec to `dict[str, JsonValue]`. Return strongly typed domain models from execution and workflow repositories. Replace reflection in `test_ast_engine_dispatch_guardrails.py` with typed AST node matching. | Pruned ad-hoc schema validators; reuse Pydantic V2 native collection hydration. Pruned untyped reflection wrappers. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos/telemetry.py backend_v2/api/routers/system/telemetry.py backend_v2/services/sdui/adapters/base_adapter.py backend_v2/seed/run_seed.py backend_v2/database/repositories --strict` = 0. `uv run python backend_v2/seed/run_seed.py local`. |
| `@[backend_v2/models/domain/base.py#L40-L128]`, `@[backend_v2/models/domain/analyst.py]`, `@[backend_v2/models/domain/archivist.py]`, `@[backend_v2/models/domain/integrity.py#L92-L118]`, `@[backend_v2/models/domain/mcp.py]`, `@[backend_v2/models/domain/metrics.py]`, `@[backend_v2/models/domain/security.py]`, `@[backend_v2/models/domain/system_config.py]`, `@[backend_v2/models/domain/validation.py]` | Banned permissive typing `dict[str, Any]`, `dict[str, object]`, `list[dict]`. Banned assigning `DomainInputValue` to ingress values without origin verification. Banned invented fallback keys. | Field Classification Gate (Section 2.4). Retype `context` to [NEW] `DomainExecutionContextDTO | None` or `dict[str, JsonValue] | None`; retype `provider_metadata` to `ProviderMetadataDTO | None`; retype `dynamic_inputs` to `dict[str, DomainInputValue]`; retype `raw_inputs` and `root` to `dict[str, IngressInputValue] | None`; retype MCP parameters, arguments, result_data to `dict[str, JsonValue]`; retype `options` to `list[SystemConfigOptionDTO] | None` and `validation_rules` to `SystemValidationRulesDTO | None`. | Pruned speculative open DTOs for open JSON Schema; map open schemas strictly to `dict[str, JsonValue]`. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/domain --strict` = 0. Per retyped field: 1 positive plus 2 negative validation tests. |
| `@[backend_v2/models/domain/xai.py#L439-L465]`, `@[backend_v2/models/domain/xai.py#L468-L490]`, `@[backend_v2/models/dtos/atom_evaluation.py]`, `@[backend_v2/models/dtos/mcp.py]`, `@[backend_v2/models/dtos/prompt_context.py#L11-L33]`, `@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/models/dtos/trace.py#L157-L194]`, `@[backend_v2/models/llm.py#L63-L76]`, `@[backend_v2/models/llm.py#L426-L447]` | Banned dead legacy fields `model_params` and `flat_report`. Banned nested dicts in atom evaluation DTOs. Banned loose Studio mock inputs and traces. Banned dual-key `_step_metadata` fallback in `trace.py`. | Drop dead fields `model_params` and `flat_report`. Retype `ReportResult.data` to `ReportDataDTO | None`. Define [NEW] `list[EvaluatedMatrixRefDTO]` and [NEW] `list[RawXAIExtensionDTO]`. Retype `mock_inputs` to `dict[str, IngressInputValue]`. Remove `model_validate` override in `trace.py` in favor of single canonical key. Retype `raw_extra` to `dict[str, JsonValue] | None`. | Pruned obsolete fallback extraction paths and dead model configurations. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos backend_v2/models/llm.py --strict` = 0. `backend_v2/tests/unit/models/test_trace_envelope.py` and `backend_v2/tests/unit/models/dtos/test_trace.py` pass. |
| `@[backend_v2/models/dtos/context_variables.py]`, `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`, `@[backend_v2/services/orchestrator/matrix_reducer.py]`, `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`, `@[backend_v2/services/execution/ingress_service.py#L146-L250]`, `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, `@[backend_v2/tests/unit/services/execution/test_ingress_service.py#L152-L227]` | Banned untyped consumer extraction of matrix evaluations in reducers and explainers. Banned loose ingress validation rule writes. Banned desynchronized test fixtures. | Migrate 1-hop consumers to consume the new `EvaluatedMatrixRefDTO` and `RawXAIExtensionDTO` DTOs. Update `ingress_service.py` to write typed `SystemValidationRulesDTO`. Migrate unit tests to typed assertions. | Pruned raw dictionary comprehension loops; access typed DTO fields via static dot-notation. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py backend_v2/tests/unit/services/execution/test_ingress_service.py`. Global audit loop passes. |
| `@[backend_v2/tests/architecture/test_boundaries.py]`, `@[backend_v2/tests/unit/test_epic_61_hardening.py]`, `@[backend_v2/tests/unit/test_provider_rate_limit.py]`, `@[backend_v2/tests/unit/llm/test_fallback_caching.py]`, `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]`, `@[backend_v2/tests/unit/test_matrix_data_integrity.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]` | Banned unconditional skip and xfail markers that hide broken assertions or obsolete tests. Banned raw dict evaluation fixtures in scoring tests. | Delete 4 permanently skipped test files. Delete skipped functions in `test_ast_domain_security_guardrails.py` and `test_matrix_data_integrity.py`. Remove 4 xfail markers in `test_scoring.py` and migrate fixtures to typed `ExecutionInputsDTO.raw_inputs`. | Pruned dead legacy tests that execute no assertions and mask coverage holes. | Census S command returns 0 matches. `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -rxX` reports 0 xfailed and 0 xpassed. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Convert `BOUNDARY_EXEMPTION_FILES` in `scripts/_ast_guardrails.py` to a `frozenset[str]` of 15 workspace-relative POSIX paths; delete `LOCKED_PHYSICAL_DRIVERS` and import the shared set in `scripts/audit_dict_eradication.py`.
2. `[CLEANUP]` Define [NEW] `ResidualDebtCeilingsDTO` in `scripts/audit_warning_baseline.py` and wire as Stage 9/10 of `scripts/backend_audit_loop.py`, enforcing exact-equality ceilings on all census categories.
3. `[CLEANUP]` Implement `QGR026` in `scripts/_ast_guardrails.py` to statically ban unconditional `@pytest.mark.skip`, `@pytest.mark.xfail`, module-level skip/xfail markers, and `pytest.xfail()` calls at FATAL severity.
4. `[CLEANUP]` Verify zero residual AST and dict-audit violations in `backend_v2/models/dtos/telemetry.py`, `backend_v2/api/routers/system/telemetry.py`, `backend_v2/services/sdui/adapters/base_adapter.py` after losing accidental basename exemption.
5. `[CLEANUP]` Replace `validate_all_seed_collections` buffers in `backend_v2/seed/run_seed.py` with `ValidatedSeedBufferDTO`.
6. `[CLEANUP]` Type the OpenAPI spec in `backend_v2/scripts/generate_openapi.py` as `dict[str, JsonValue]`.
7. `[CLEANUP]` Return typed domain models from `backend_v2/database/repositories/execution.py` and `backend_v2/database/repositories/workflow.py`.
8. `[CLEANUP]` Replace `getattr` reflection in `backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py` with typed `ast` node matching.
9. `[CLEANUP]` Delete the 4 permanently skipped test files `backend_v2/tests/architecture/test_boundaries.py`, `backend_v2/tests/unit/test_epic_61_hardening.py`, `backend_v2/tests/unit/test_provider_rate_limit.py`, `backend_v2/tests/unit/llm/test_fallback_caching.py`.
10. `[CLEANUP]` Delete the skipped functions `test_aspirational_html_escape` in `backend_v2/tests/unit/test_ast_domain_security_guardrails.py` and `test_all_ok_matrices_have_exactly_three_claims` in `backend_v2/tests/unit/test_matrix_data_integrity.py`.
11. `[CLEANUP]` Remove the 4 `@pytest.mark.xfail` markers in `backend_v2/tests/unit/hooks/test_scoring.py`; migrate the raw evaluation dicts of `test_failed_atom_with_override_does_not_inflate_score` and `test_matrix_scoring_hook_illegal_override_penalty` to typed `ExecutionInputsDTO.raw_inputs` values.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state. Verify baseline violation count across 896 backend files (127 dict-audit violations, 11 unconditional skip/xfail markers, 0 QGR026 rules).</action>
    <action>Look forward: Verify that establishing the path-based BOUNDARY_EXEMPTION_FILES SSOT, QGR026, Stage 9/10 Residual Debt Baseline, and model retyping provides the clean Foundation for Phase 2 exception and caching lockdowns.</action>
    <constraint>If baseline diverges unexpectedly or pre-conditions fail, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/01_phase1_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>BOUNDARY_EXEMPTION_FILES in scripts/_ast_guardrails.py is a frozenset[str] of exactly the 15 workspace-relative POSIX paths.</item>
    <item>LOCKED_PHYSICAL_DRIVERS symbol is completely deleted from scripts/audit_dict_eradication.py and replaced with an import from scripts._ast_guardrails.</item>
    <item>QGR026 implemented in scripts/_ast_guardrails.py banning unconditional @pytest.mark.skip, @pytest.mark.xfail, module-level skip/xfail markers, and pytest.xfail() calls at FATAL severity.</item>
    <item>scripts/audit_warning_baseline.py implements ResidualDebtCeilingsDTO and is wired as Stage 9/10 in scripts/backend_audit_loop.py.</item>
    <item>The 4 permanently skipped test files are deleted and skipped functions in test_ast_domain_security_guardrails.py and test_matrix_data_integrity.py are removed.</item>
    <item>The 4 @pytest.mark.xfail markers in test_scoring.py are removed and their fixtures migrated to typed ExecutionInputsDTO.raw_inputs values.</item>
    <item>All 30 model violations across 17 files in backend_v2/models/ are retyped according to the Field Classification Gate.</item>
    <item>1-hop consumers in orchestrator and execution services are migrated to consume the new typed DTOs.</item>
    <item>Global quality gate uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes with 9 stages clean.</item>
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
    <anti_target>Do NOT modify backend_v2/exceptions.py details typing during Phase 1 (quarantined strictly for Phase 2).</anti_target>
    <anti_target>Do NOT modify hooks or LLM adapters during Phase 1 (quarantined strictly for Phase 2).</anti_target>
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 1 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT modify client_app_v2 Flutter code during Phase 1 (quarantined strictly for Phase 8 and Phase 12).</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/audit_dict_eradication.py]</backend>
    <backend>@[scripts/audit_warning_baseline.py]</backend>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <backend>@[backend_v2/models/dtos/telemetry.py]</backend>
    <backend>@[backend_v2/api/routers/system/telemetry.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/base_adapter.py]</backend>
    <backend>@[backend_v2/scripts/generate_openapi.py]</backend>
    <backend>@[backend_v2/seed/run_seed.py]</backend>
    <backend>@[backend_v2/database/repositories/execution.py]</backend>
    <backend>@[backend_v2/database/repositories/workflow.py]</backend>
    <backend>@[backend_v2/models/domain/base.py]</backend>
    <backend>@[backend_v2/models/domain/analyst.py]</backend>
    <backend>@[backend_v2/models/domain/archivist.py]</backend>
    <backend>@[backend_v2/models/domain/integrity.py]</backend>
    <backend>@[backend_v2/models/domain/mcp.py]</backend>
    <backend>@[backend_v2/models/domain/metrics.py]</backend>
    <backend>@[backend_v2/models/domain/security.py]</backend>
    <backend>@[backend_v2/models/domain/system_config.py]</backend>
    <backend>@[backend_v2/models/domain/validation.py]</backend>
    <backend>@[backend_v2/models/domain/xai.py]</backend>
    <backend>@[backend_v2/models/dtos/atom_evaluation.py]</backend>
    <backend>@[backend_v2/models/dtos/mcp.py]</backend>
    <backend>@[backend_v2/models/dtos/prompt_context.py]</backend>
    <backend>@[backend_v2/models/dtos/studio.py]</backend>
    <backend>@[backend_v2/models/dtos/system.py]</backend>
    <backend>@[backend_v2/models/dtos/trace.py]</backend>
    <backend>@[backend_v2/models/llm.py]</backend>
    <backend>@[backend_v2/models/dtos/context_variables.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_reducer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/services/execution/ingress_service.py]</backend>
  </touched_artifacts>

  <contract_freeze>
    <contract name="BOUNDARY_EXEMPTION_FILES">
      frozenset[str] of exactly 15 workspace-relative POSIX paths:
      backend_v2/database/tinydb_driver.py, backend_v2/database/firestore_driver.py,
      backend_v2/database/driver.py, backend_v2/database/wrapper.py,
      backend_v2/llm/provider.py, backend_v2/llm/handler.py,
      backend_v2/logging_config.py, backend_v2/core/telemetry.py,
      backend_v2/llm/adapters/base_adapter.py, backend_v2/llm/adapters/vertex_adapter.py,
      backend_v2/llm/adapters/ai_studio_adapter.py, backend_v2/llm/adapters/openai_adapter.py,
      backend_v2/llm/adapters/anthropic_adapter.py, backend_v2/llm/adapters/deepseek_adapter.py,
      backend_v2/llm/adapters/mock_adapter.py.
    </contract>
    <contract name="ResidualDebtCeilingsDTO">
      ConfigDict(strict=True, extra="forbid", frozen=True) specifying exact integer ceilings for census categories D, F, K, X, N, T, P, M, R, S.
    </contract>
  </contract_freeze>

  <step id="1" name="Physical Boundary SSOT, QGR026 &amp; Residual Debt Ceiling Ledger Tooling">
    <action>In `@[scripts/_ast_guardrails.py]`, replace basename-matching BOUNDARY_EXEMPTION_FILES with the canonical frozenset[str] of 15 workspace-relative POSIX paths. Enforce OS-independent path normalization via `Path(filepath).resolve().relative_to(repo_root).as_posix()` to eliminate Windows backslash matching bugs.</action>
    <action>In `@[scripts/audit_dict_eradication.py]`, delete the LOCKED_PHYSICAL_DRIVERS symbol and import BOUNDARY_EXEMPTION_FILES from scripts._ast_guardrails directly.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, implement AST rule QGR026 at FATAL severity banning unconditional @pytest.mark.skip, @pytest.mark.xfail, module-level pytestmark skip/xfail markers, and pytest.xfail() calls.</action>
    <action>In `@[scripts/audit_warning_baseline.py]`, implement ResidualDebtCeilingsDTO asserting exact-equality ceilings across all census categories.</action>
    <action>In `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]`, add unit tests asserting ResidualDebtCeilingsDTO validation and fail-fast threshold mechanics.</action>
    <action>In `@[scripts/backend_audit_loop.py#L282-L477]`, wire audit_warning_baseline.py as Stage 9/10 of the universal audit pipeline.</action>
    <action>In `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`, update audit loop stage assertions to verify Stage 9/10 execution.</action>
    <action>In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, add unit tests for BOUNDARY_EXEMPTION_FILES path matching, QGR026 skip/xfail detection, and the 9-path admission ratchet.</action>
    <action>In `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`, assert identity parity between audit_dict_eradication.BOUNDARY_EXEMPTION_FILES and _ast_guardrails.BOUNDARY_EXEMPTION_FILES.</action>
    <constraint invariant="the_zero_compromise_pledge">No basename matching or divergent exemption lists permitted.</constraint>
  </step>

  <step id="2" name="Boundary Exemption Loss Remediation &amp; OpenAPI Typings">
    <action>In `@[backend_v2/models/dtos/telemetry.py]`, verify 0 residual AST and dict violations and enforce strict typing on all fields.</action>
    <action>In `@[backend_v2/api/routers/system/telemetry.py]`, verify 0 residual AST and dict violations across telemetry endpoints.</action>
    <action>In `@[backend_v2/services/sdui/adapters/base_adapter.py]`, verify 0 residual AST and dict violations across SDUI layout adapters.</action>
    <action>In `@[backend_v2/scripts/generate_openapi.py]`, retype the openapi_spec dictionary from dict[str, Any] to dict[str, JsonValue].</action>
    <constraint invariant="universal_fail_fast">Files losing accidental basename exemption must report 0 violations without exemptions.</constraint>
  </step>

  <step id="3" name="Seeder, DAL Repositories, Guardrail Reflection &amp; Test Deletions">
    <action>In `@[backend_v2/seed/run_seed.py]`, define ValidatedSeedBufferDTO with typed list fields per collection and replace loose dict buffers in validate_all_seed_collections.</action>
    <action>In `@[backend_v2/database/repositories/execution.py]`, replace 3 naked dict return sites with strongly typed ExecutionRecord domain models.</action>
    <action>In `@[backend_v2/database/repositories/workflow.py]`, replace naked dict return with strongly typed Workflow domain model.</action>
    <action>In `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L311-L353]`, replace reflection getattr(val.value, 'id', '') calls with typed match on AST node classes.</action>
    <action>In `@[backend_v2/tests/unit/seed/test_run_seed.py#L472-L496]`, update seeder unit test assertions for ValidatedSeedBufferDTO.</action>
    <action>Delete permanently skipped test file `@[backend_v2/tests/architecture/test_boundaries.py]`.</action>
    <action>Delete permanently skipped test file `@[backend_v2/tests/unit/test_epic_61_hardening.py]`.</action>
    <action>Delete permanently skipped test file `@[backend_v2/tests/unit/test_provider_rate_limit.py]`.</action>
    <action>Delete permanently skipped test file `@[backend_v2/tests/unit/llm/test_fallback_caching.py]`.</action>
    <action>In `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]`, delete the skipped function test_aspirational_html_escape.</action>
    <action>In `@[backend_v2/tests/unit/test_matrix_data_integrity.py]`, delete the skipped function test_all_ok_matrices_have_exactly_three_claims.</action>
    <action>In `@[backend_v2/tests/unit/hooks/test_scoring.py]`, remove the 4 @pytest.mark.xfail markers (unblocking 2 already-passing tests) and migrate test_failed_atom_with_override_does_not_inflate_score and test_matrix_scoring_hook_illegal_override_penalty fixtures to typed AtomResultDTO instances in ExecutionInputsDTO.raw_inputs respecting cognitive invariants (contextual_override=False on FAILED, source_quote=None on override=True).</action>
    <constraint invariant="the_no_legacy_mandate">Permanently skipped and fake-failing tests must be eradicated.</constraint>
  </step>

  <step id="4" name="Domain &amp; DTO Model Retyping (Base, Analyst, Archivist, Integrity, MCP, Metrics, Security, System Config, Validation)">
    <action>In `@[backend_v2/models/domain/base.py#L40-L128]`, retype context to DomainExecutionContextDTO | None (or dict[str, JsonValue] | None) and provider_metadata to ProviderMetadataDTO | None.</action>
    <action>In `@[backend_v2/models/domain/analyst.py]`, retype dynamic_inputs to dict[str, DomainInputValue].</action>
    <action>In `@[backend_v2/models/domain/archivist.py]`, retype dynamic_inputs to dict[str, DomainInputValue].</action>
    <action>In `@[backend_v2/models/domain/integrity.py#L92-L118]`, retype raw_inputs to dict[str, IngressInputValue] | None.</action>
    <action>In `@[backend_v2/models/domain/mcp.py]`, retype arguments to dict[str, JsonValue], provider_specific_fields to dict[str, JsonValue] | None, and result_data to dict[str, JsonValue].</action>
    <action>In `@[backend_v2/models/domain/metrics.py]`, retype root in MetricsInputPayload to dict[str, IngressInputValue | DomainInputValue].</action>
    <action>In `@[backend_v2/models/domain/security.py]`, retype root in SanitizationInput to dict[str, IngressInputValue].</action>
    <action>In `@[backend_v2/models/domain/system_config.py]`, retype options to list[SystemConfigOptionDTO] | None, validation_rules to SystemValidationRulesDTO | None, and input_schema to dict[str, JsonValue].</action>
    <action>In `@[backend_v2/models/domain/validation.py]`, retype root to dict[str, IngressInputValue | DomainInputValue] and meta to ValidationContextMetadataDTO | dict[str, JsonValue].</action>
    <constraint invariant="the_zero_compromise_pledge">Naked dict[str, Any] and Primitive Obsession strictly prohibited.</constraint>
  </step>

  <step id="5" name="Domain &amp; DTO Model Retyping (XAI, Atom Evaluation, Prompt Context, Studio, System, Trace, LLM)">
    <action>In `@[backend_v2/models/domain/xai.py#L439-L465]` and `@[backend_v2/models/domain/xai.py#L468-L490]`, drop dead field flat_report and retype ReportResult.data to ReportDataDTO | None.</action>
    <action>In `@[backend_v2/models/dtos/atom_evaluation.py]`, retype evaluated_matrices to list[EvaluatedMatrixRefDTO] and raw_extensions to list[RawXAIExtensionDTO].</action>
    <action>In `@[backend_v2/models/dtos/mcp.py]`, retype parameters to dict[str, JsonValue].</action>
    <action>In `@[backend_v2/models/dtos/prompt_context.py#L11-L33]`, retype metadata to typed metadata DTO or dict[str, JsonValue].</action>
    <action>In `@[backend_v2/models/dtos/studio.py]`, retype trace to StepTraceMetadataDTO and mock_inputs to dict[str, IngressInputValue].</action>
    <action>In `@[backend_v2/models/dtos/system.py]`, retype context_data to dict[str, JsonValue].</action>
    <action>In `@[backend_v2/models/dtos/trace.py#L157-L194]`, delete the model_validate override and eliminate the _step_metadata fallback key.</action>
    <action>In `@[backend_v2/models/llm.py#L63-L76]` and `@[backend_v2/models/llm.py#L426-L447]`, retype raw_extra to dict[str, JsonValue] | None and drop dead field model_params.</action>
    <action>In `@[backend_v2/tests/unit/models/test_trace_envelope.py]`, update trace envelope assertions for canonical step_metadata.</action>
    <action>In `@[backend_v2/tests/unit/models/dtos/test_trace.py]`, update trace DTO assertions for single canonical metadata key.</action>
    <action>In `@[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py]`, add unit tests asserting EvaluatedMatrixRefDTO and RawXAIExtensionDTO validation.</action>
    <constraint invariant="zero_backward_compatibility_planning_ban">No fallback keys or defensive dict unpacking.</constraint>
  </step>

  <step id="6" name="1-Hop Orchestrator &amp; Ingress Consumers and Coupled Unit Tests">
    <action>In `@[backend_v2/models/dtos/context_variables.py]`, align matrix references with EvaluatedMatrixRefDTO.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`, update synthesis consumer to process EvaluatedMatrixRefDTO and RawXAIExtensionDTO.</action>
    <action>In `@[backend_v2/services/orchestrator/matrix_reducer.py]`, update matrix reducer reduction loop to consume list[EvaluatedMatrixRefDTO].</action>
    <action>In `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`, update matrix explanation consumer to process EvaluatedMatrixRefDTO.</action>
    <action>In `@[backend_v2/services/execution/ingress_service.py#L146-L250]`, update validation rule writes to produce SystemValidationRulesDTO.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, update synthesis engine unit test fixtures to supply EvaluatedMatrixRefDTO.</action>
    <action>In `@[backend_v2/tests/unit/services/execution/test_ingress_service.py#L152-L227]`, update ingress service test fixtures to validate SystemValidationRulesDTO.</action>
    <constraint invariant="universal_quality_gates">1-hop consumers and tests must be migrated atomically in the same phase as model changes.</constraint>
  </step>

  <test_contracts>
    <test name="test_boundary_exemption_files_contains_only_relative_paths" category="positive">
      <input>scripts._ast_guardrails.BOUNDARY_EXEMPTION_FILES</input>
      <expected>All 15 members are workspace-relative POSIX paths matching existing physical files</expected>
    </test>
    <test name="test_boundary_exemption_files_rejects_models_services_hooks_api" category="negative">
      <input>Paths starting with backend_v2/models, backend_v2/services, backend_v2/hooks, backend_v2/api</input>
      <expected>Zero members belong to core domain directories</expected>
    </test>
    <test name="test_admission_ratchet_asserts_clean_baseline_for_new_members" category="boundary">
      <input>9 newly admitted boundary files scanned with empty exemption set</input>
      <expected>Returns 0 AST guardrail violations</expected>
    </test>
    <test name="test_qgr026_unconditional_skip_marker_raises_fatal" category="positive">
      <input>Function decorated with @pytest.mark.skip</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR026</expected>
    </test>
    <test name="test_qgr026_unconditional_xfail_marker_raises_fatal" category="positive">
      <input>Function decorated with @pytest.mark.xfail</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR026</expected>
    </test>
    <test name="test_qgr026_environment_skipif_permitted" category="boundary">
      <input>Function decorated with @pytest.mark.skipif(not os.getenv('FLAG'), reason='env')</input>
      <expected>QuorumGuardrailVisitor emits zero violations for QGR026</expected>
    </test>
    <test name="test_residual_debt_ceilings_dto_asserts_exact_equality" category="positive">
      <input>ResidualDebtCeilingsDTO instantiated with census counts</input>
      <expected>Validates successfully with extra='forbid' and frozen=True</expected>
    </test>
    <test name="test_validated_seed_buffer_dto_rejects_unknown_collection" category="negative">
      <input>JSON payload with unmapped collection key</input>
      <expected>ValidatedSeedBufferDTO.model_validate raises ValidationError</expected>
    </test>
    <test name="test_system_validation_rules_dto_rejects_unknown_attribute" category="negative">
      <input>SystemValidationRulesDTO(unknown_rule='bad')</input>
      <expected>Raises ValidationError under extra='forbid'</expected>
    </test>
    <test name="test_evaluated_matrix_ref_dto_roundtrip" category="positive">
      <input>EvaluatedMatrixRefDTO with matrix_id and evaluation attributes</input>
      <expected>Serializes and deserializes with 100% field fidelity</expected>
    </test>
  </test_contracts>

  <demolish>
    `test_aspirational_html_escape`
    `test_all_ok_matrices_have_exactly_three_claims`
  </demolish>

  <validation_gate>
    <action>Execute Census S: `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Select-String -Pattern "@pytest\.mark\.(skip|xfail)\b"` returns 0 matches.</action>
    <action>Execute QGR026 check: `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict` reports 0 QGR026 violations.</action>
    <action>Execute Scoring Test Suite: `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -rxX` reports 0 xfailed and 0 xpassed.</action>
    <action>Execute Model Dict Eradication Audit: `uv run python scripts/audit_dict_eradication.py backend_v2/models backend_v2/seed backend_v2/scripts backend_v2/database/repositories --strict` reports 0 violations.</action>
    <action>Execute Local Seed: `uv run python backend_v2/seed/run_seed.py local` verifies clean-slate seed validation.</action>
    <action>Execute SDUI Parity Test: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` passes.</action>
    <action>Execute Global Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes with 9 stages clean.</action>
  </validation_gate>
</execution_protocol>
```
