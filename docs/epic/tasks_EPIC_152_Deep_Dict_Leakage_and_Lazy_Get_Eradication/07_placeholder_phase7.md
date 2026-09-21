<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

# Phase 7: Full-Spectrum Verification, AST Guardrails & Live E2E Gate

**Overview:** Full-spectrum mathematical integrity verification and final quality gating for EPIC 152. Eradicates all Primitive Obsession nested dictionaries (`dict[..., dict[...]]`) codebase-wide (specifically and exhaustively: `LightweightMatrixOutput.level_breakdown` and `ScoringResultDTO.breakdown` migrated to strongly typed `dict[str, LevelStatsDTO]` with pure static dot-notation `.hits`, `.total` across all consumers; `AESTHETICS_RULES` across all remaining SDUI adapters migrated to typed frozen DTOs in `sdui_rules.py`; background worker `step_telemetry` encapsulated in `StepTelemetryEntryDTO`; causal linker graph dependencies encapsulated in `WindowCausalEdgesDTO`; and matrix parser outputs unified in `ParsedMatricesResultDTO`). Enforces 100% mathematical zero violations across `audit_dict_eradication.py` (0 naked dict annotations, 0 Primitive Obsession nested dicts, 0 unauthorized `# noqa` suppressions, 0 reflection calls) and `_ast_guardrails.py` (0 fatal violations in non-exempt files), mathematically confirms 1:1 SDUI semantic parity between Flutter UI and PDF templates (`test_sdui_semantic_parity.py`), validates clean database re-seeding via the two-phase seeder (`run_seed.py local`), and executes the live Real-LLM E2E execution verification gate (`test_integration_real_llm.py` and `run_e2e_variance_test.py`).
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 7: Full-Spectrum Verification, AST Guardrails & Live E2E Gate

## Phase 1: Pre-Implementation Cleanups

Prior to implementing the core primitive obsession eradication tasks, resolve all discovered 1-hop caller coupling and uncataloged technical debt:
1. **`@[backend_v2/services/blueprint.py#L321-L342]`**: Unpacks anonymous 4-tuple from `MatrixDomainParser.parse_matrices(...)`. Update caller to receive `ParsedMatricesResultDTO` and access attributes directly (`result.evaluative_matrices`, `result.informational_matrices`, `result.all_parsed_matrices`) with zero tuple destructuring. Also clean up legacy `.get()` on line 219 and `TypeAdapter(dict)` on line 305.
2. **`@[backend_v2/services/pdf_generator.py#L183-L205]`**: Private attribute access and banned `.get()` on `LocalizationService._translations.get(lang_simple)`. Update caller to use public `LocalizationService.get_translations(lang_simple)` returning typed `LocaleTranslationsDTO`.
3. **`@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`**: Multiple unit test functions unpack the 4-tuple from `MatrixDomainParser.parse_matrices`. Update test assertions to validate `ParsedMatricesResultDTO` attributes.
4. **`@[backend_v2/tests/unit/services/test_blueprint.py#L1774-L2100]`**: Unpacks 4-tuple from `MatrixDomainParser.parse_matrices`. Update assertions to validate `ParsedMatricesResultDTO` attributes.
5. **`@[backend_v2/models/dtos/engine.py#L119-L168]`**: Migrate `EngineExecutionRequest.hydrated_messages` from `list[dict[str, str]] | None` to strongly typed `list[LLMMessageDTO] | None`, eradicating primitive dictionary lists in engine payloads. Update callers in `strategies/llm.py`, `synthesis_engine.py`, `prompt_engine.py`, and test suites.

## Five-Axis Architectural Directives Table

| Target Scope & Boundaries | Eradicated Duct-Tape | Approved Best Practice | Pruned Over-Engineering (30% Deletion Test) | Verification & Fail-Fast (Proof Anchor) |
|---|---|---|---|---|
| `backend_v2/models/dtos/lightweight_matrix.py#L37-L111` | `level_breakdown: dict[str, dict[str, int]] \| None = None` in `LightweightMatrixOutput` and `breakdown: dict[str, dict[str, int]]` in `ScoringResultDTO`. | Move `LevelStatsDTO` definition before `LightweightMatrixOutput`. Migrate both models to strongly typed `dict[str, LevelStatsDTO]`. Lock `LevelStatsDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`. | Demolish inner primitive dictionary subscripting and manual type laundering. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py --test`. |
| `backend_v2/models/dtos/engine.py#L119-L168` | `hydrated_messages: list[dict[str, str]] \| None` in `EngineExecutionRequest`. | Migrate to strongly typed `list[LLMMessageDTO] \| None`, accessing attributes strictly via dot-notation (`msg.role`, `msg.content`). | Demolish primitive dictionary lists in engine execution requests. | `uv run pytest backend_v2/tests/unit/models/dtos/test_engine.py backend_v2/tests/unit/services/orchestrator/engines/`. |
| `backend_v2/utils/scoring/unified_engine.py#L41-L124` | Ad-hoc conversion of `LevelStatsDTO` to primitive nested dict `{"hits": int(v.hits), "total": int(v.total), "dlqs": int(v.dlqs)}`. | Pass `LevelStatsDTO` directly into `ScoringResultDTO(breakdown=level_breakdown)`: `{str(k): LevelStatsDTO(hits=v.hits, total=v.total, dlqs=v.dlqs) for k, v in stats.items()}`. | Demolish redundant primitive dictionary mapping step. | `uv run pytest backend_v2/tests/unit/utils/scoring/test_unified_engine.py`. |
| `backend_v2/services/orchestrator/matrix_explanation_service.py#L29-L276` | Popping `raw_level_breakdown` from payload and manual validation loop with `LevelStatsDTO.model_validate(raw_stats, strict=False)`. | Direct access to `lw_matrix.level_breakdown` with static dot-notation (`stats_dto.hits`, `stats_dto.total`). | Demolish dictionary popping, type checking, and ad-hoc validation loops. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py`. |
| `backend_v2/hooks/scoring/matrix_hook.py#L56-L528` & `passivity_hook.py#L26-L157` | Nested dictionary annotations: `blocks_meta: dict[str, dict[str, Any]]`, `block_scale_stats: dict[str, dict[float, dict[str, int]]]`, and `matrix_blocks_meta: dict[str, dict[str, float]]`. | Define typed `BlockMetaDTO(scales=..., math_min=..., math_max=...)`; type `block_scale_stats: dict[str, dict[float, LevelStatsDTO]]`; flatten `matrix_blocks_min: dict[str, float]`. | Demolish untyped dictionary wrappers and nested primitive mappings. | `uv run pytest backend_v2/tests/unit/hooks/test_matrix_hook.py`. |
| `backend_v2/models/dtos/sdui_rules.py#L65-L229` & SDUI Adapters (`global_score_adapter.py#L20-L57`, `matrix_graphs_adapter.py#L26-L106`, `matrix_summary_table_adapter.py#L25-L96`, `mcp_audit_adapter.py#L20-L59`, `metadata_adapter.py#L23-L103`, `synthesis_text_adapter.py#L22-L63`, `warning_card_adapter.py#L29-L100`, `xai_highlights_adapter.py#L26-L177`) | Untyped naked dictionary `AESTHETICS_RULES: dict[str, dict[str, Any]]` across 8 SDUI adapters. | Define frozen Pydantic V2 schemas (`GlobalScoreAestheticsDTO`, `MatrixGraphsAestheticsDTO`, `MatrixSummaryAestheticsDTO`, `McpAuditAestheticsDTO`, `MetadataAestheticsDTO`, `SynthesisTextAestheticsDTO`, `WarningCardAestheticsDTO`) in `sdui_rules.py`; bind adapters to immutable DTO instances. | Demolish loose dictionary subscripting in SDUI visual block transformation. | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` and `test_blueprint.py`. |
| `backend_v2/workers/execution_worker.py#L50-L443` | `step_telemetry: dict[str, dict[str, Any]] = {}` and in-place raw dictionary mutation. | Encapsulate in frozen Pydantic V2 `StepTelemetryEntryDTO` in `backend_v2/models/dtos/step_telemetry.py` with typed `.model_copy(update=...)` transitions. | Demolish untyped dictionary bags in high-frequency background worker loops. | `uv run pytest backend_v2/tests/unit/test_worker.py`. |
| `backend_v2/services/orchestrator/sliding_window_linker.py#L71-L282`, `localization.py#L40-L283`, `matrix_domain_parser.py#L32-L631` | `master_deps: dict[str, dict[str, CausalEdge]]`, `_translations: dict[str, dict[str, str]]`, and anonymous 4-tuple with `step_scorecard_atoms: dict[str, dict[str, ScorecardAtomDTO]]`. | Define `WindowCausalEdgesDTO`, `LocaleTranslationsDTO`, and `ParsedMatricesResultDTO` encapsulating matrix parsing outputs with typed collections. | Demolish anonymous state tuples and nested primitive dictionaries. | `uv run pytest backend_v2/tests/unit/services/test_matrix_domain_parser.py`. |
| `backend_v2/services/blueprint.py#L321-L342` & `backend_v2/services/pdf_generator.py#L183-L205` | 4-tuple unpacking from `parse_matrices` in `blueprint.py` and private `_translations.get()` in `pdf_generator.py`. | Consume `ParsedMatricesResultDTO` with static dot-notation; invoke `LocalizationService.get_translations(lang_simple)`. | Demolish anonymous tuple unpacking and private dictionary access. | `uv run pytest backend_v2/tests/unit/services/test_blueprint.py` and `test_pdf_generator.py`. |
| `scripts/audit_dict_eradication.py` & `scripts/_ast_guardrails.py` | Outdated violation exemptions, unchecked reflection occurrences, and loose AST rule bounds. | Statically audit codebase for 100% mathematical zero violations (0 naked dict annotations, 0 Primitive Obsession nested dicts, 0 unauthorized suppressions, 0 reflection instances). | Demolish legacy dictionary tolerance in automated quality gates. | `uv run python scripts/audit_dict_eradication.py` and `uv run python scripts/_ast_guardrails.py backend_v2 scripts`. |
| `scripts/run_e2e_variance_test.py` & `test_integration_real_llm.py` | Potential runtime regression in multi-provider LLM pipelines or FinOps telemetry serialization. | Execute live Real-LLM E2E workflow test and multi-model variance verification suite. | Demolish test-skipping shortcuts and verify true end-to-end integration pass. | `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`. |

**Target Files:**
- `[NEW]` @[backend_v2/models/dtos/step_telemetry.py]
- `[NEW]` @[backend_v2/models/dtos/matrix_parser.py]
- `[NEW]` Defined Schemas: `StepTelemetryEntryDTO`, `ParsedMatricesResultDTO`, `ScorecardAtomCollectionDTO`, `WindowCausalEdgesDTO`, `LocaleTranslationsDTO`, `BlockMetaDTO`, `GlobalScoreAestheticsDTO`, `MatrixGraphsAestheticsDTO`, `MatrixSummaryAestheticsDTO`, `McpAuditAestheticsDTO`, `MetadataAestheticsDTO`, `SynthesisTextAestheticsDTO`, `WarningCardAestheticsDTO`.
- `[MODIFY]` @[backend_v2/models/dtos/lightweight_matrix.py#L37-L111]
- `[MODIFY]` @[backend_v2/models/dtos/engine.py#L119-L168]
- `[MODIFY]` @[backend_v2/utils/scoring/unified_engine.py#L41-L124]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L29-L276]
- `[MODIFY]` @[backend_v2/hooks/scoring/matrix_hook.py#L56-L528]
- `[MODIFY]` @[backend_v2/hooks/scoring/passivity_hook.py#L26-L157]
- `[MODIFY]` @[backend_v2/models/dtos/sdui_rules.py#L65-L229]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/global_score_adapter.py#L20-L57]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py#L26-L106]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py#L25-L96]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/mcp_audit_adapter.py#L20-L59]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/metadata_adapter.py#L23-L103]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/synthesis_text_adapter.py#L22-L63]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/warning_card_adapter.py#L29-L100]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L26-L177]
- `[MODIFY]` @[backend_v2/workers/execution_worker.py#L50-L443]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L740-L815]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L246]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L75]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L71-L282]
- `[MODIFY]` @[backend_v2/services/localization.py#L40-L283]
- `[MODIFY]` @[backend_v2/services/matrix_domain_parser.py#L32-L631]
- `[MODIFY]` @[backend_v2/services/blueprint.py#L321-L342]
- `[MODIFY]` @[backend_v2/services/pdf_generator.py#L183-L205]
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/utils/scoring/test_unified_engine.py#L44-L61]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L906-L953]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py#L64-L81]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phases 1 through 6 completed all structural refactoring, DTO hardening, SDUI modernization, and BaseDTO/BaseResponseDTO immutability lockdown.</action>
    <action>Look forward: Mathematically verify that zero dictionary leakages, lazy .get() calls, Primitive Obsession nested dictionaries, or reflection anti-patterns remain anywhere in the production execution pipeline.</action>
    <constraint invariant="the_no_legacy_mandate">Legacy state, backward compatibility shims, and permissive fallback chains are strictly forbidden.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/07_placeholder_phase7.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>AST audit script @[scripts/audit_dict_eradication.py] reports exactly 0 violations across all production packages, including 0 naked dict annotations, 0 Primitive Obsession nested dictionary annotations, 0 unauthorized suppressions, and 0 dynamic reflection calls.</item>
    <item>AST guardrails engine @[scripts/_ast_guardrails.py] passes with 0 fatal violations in non-exempt files across backend_v2 and scripts.</item>
    <item>LightweightMatrixOutput.level_breakdown and ScoringResultDTO.breakdown in @[backend_v2/models/dtos/lightweight_matrix.py#L37-L111] are migrated from dict[str, dict[str, int]] to strongly typed dict[str, LevelStatsDTO], with LevelStatsDTO relocated before LightweightMatrixOutput and dot-notation access (.hits, .total) across all consumers with exactly 0 dictionary subscripting.</item>
    <item>LevelStatsDTO is locked with ConfigDict(strict=True, extra="forbid", frozen=True).</item>
    <item>EngineExecutionRequest in @[backend_v2/models/dtos/engine.py#L119-L168] migrates hydrated_messages from list[dict[str, str]] | None to strongly typed list[LLMMessageDTO] | None, eliminating primitive dictionary lists in engine payloads.</item>
    <item>UnifiedScoringEngine in @[backend_v2/utils/scoring/unified_engine.py#L41-L124] constructs ScoringResultDTO with typed dict[str, LevelStatsDTO] breakdown without primitive dict conversion.</item>
    <item>MatrixExplanationService in @[backend_v2/services/orchestrator/matrix_explanation_service.py#L29-L276] directly consumes lw_matrix.level_breakdown via dot-notation with zero popping or ad-hoc validation loops.</item>
    <item>MatrixScoringHook in @[backend_v2/hooks/scoring/matrix_hook.py#L56-L528] encapsulates blocks_meta in BlockMetaDTO and block_scale_stats in dict[str, dict[float, LevelStatsDTO]], eradicating nested dicts on lines 203, 246, 248, 250.</item>
    <item>PassivityHook in @[backend_v2/hooks/scoring/passivity_hook.py#L26-L157] flattens matrix_blocks_meta to matrix_blocks_min: dict[str, float].</item>
    <item>SDUI presentation adapters in @[backend_v2/services/sdui/adapters/] bind module-level AESTHETICS_RULES to frozen Pydantic V2 DTOs defined in @[backend_v2/models/dtos/sdui_rules.py#L65-L229], eliminating all nested primitive dict annotations.</item>
    <item>Background worker in @[backend_v2/workers/execution_worker.py#L50-L443] encapsulates step_telemetry in strongly typed StepTelemetryEntryDTO.</item>
    <item>SlidingWindowLinker in @[backend_v2/services/orchestrator/sliding_window_linker.py#L71-L282] encapsulates master_deps in WindowCausalEdgesDTO.</item>
    <item>LocalizationService in @[backend_v2/services/localization.py#L40-L283] encapsulates _translations in LocaleTranslationsDTO.</item>
    <item>MatrixDomainParser in @[backend_v2/services/matrix_domain_parser.py#L32-L631] returns strongly typed ParsedMatricesResultDTO, eliminating anonymous 4-tuples and nested dict returns.</item>
    <item>Blueprint service in @[backend_v2/services/blueprint.py#L321-L342] consumes ParsedMatricesResultDTO via dot-notation, eliminating 4-tuple unpacking, legacy .get(), and TypeAdapter(dict).</item>
    <item>PDF generator in @[backend_v2/services/pdf_generator.py#L183-L205] consumes LocalizationService.get_translations(lang_simple) without private attribute access or .get().</item>
    <item>Unit test suites in @[backend_v2/tests/unit/services/test_matrix_domain_parser.py] and @[backend_v2/tests/unit/services/test_blueprint.py] assert against ParsedMatricesResultDTO with zero tuple unpacking.</item>
    <item>Two-phase database seeder passes 100% in-memory validation and atomic ingress via uv run python backend_v2/seed/run_seed.py local.</item>
    <item>SDUI semantic parity test passes 100% via uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py.</item>
    <item>Global backend audit loop passes with 100% test pass rate, clean Ruff formatting, and MyPy strict typing via uv run python scripts/backend_audit_loop.py backend_v2 --test.</item>
    <item>Flutter client analyzer passes cleanly via uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/api/reports_client.dart.</item>
    <item>Live Real-LLM E2E integration test gate passes 100% via $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py.</item>
    <item>End-to-end variance verification suite @[scripts/run_e2e_variance_test.py] executes cleanly and confirms telemetry contracts.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT skip any failing tests in the full test suite via @pytest.mark.skip or comment-outs.</forbidden>
    <forbidden>Do NOT introduce fallback dictionaries or loose Any fields to appease type checkers.</forbidden>
    <forbidden>Do NOT use getattr, hasattr, or object.__setattr__ dynamic reflection.</forbidden>
    <forbidden>Do NOT use anonymous tuples for state transit or service returns (Tuple Hell).</forbidden>
    <forbidden>Do NOT use negative prefix exclusions or string matching for entity resolution.</forbidden>
    <forbidden>Do NOT re-introduce emojis into templates, adapters, or log outputs.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/models/dtos/step_telemetry.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/matrix_parser.py]</backend>
    <backend>@[backend_v2/models/dtos/lightweight_matrix.py#L37-L111]</backend>
    <backend>@[backend_v2/models/dtos/engine.py#L119-L168]</backend>
    <backend>@[backend_v2/utils/scoring/unified_engine.py#L41-L124]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py#L29-L276]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py#L56-L528]</backend>
    <backend>@[backend_v2/hooks/scoring/passivity_hook.py#L26-L157]</backend>
    <backend>@[backend_v2/models/dtos/sdui_rules.py#L65-L229]</backend>
    <backend>@[backend_v2/services/sdui/adapters/global_score_adapter.py#L20-L57]</backend>
    <backend>@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py#L26-L106]</backend>
    <backend>@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py#L25-L96]</backend>
    <backend>@[backend_v2/services/sdui/adapters/mcp_audit_adapter.py#L20-L59]</backend>
    <backend>@[backend_v2/services/sdui/adapters/metadata_adapter.py#L23-L103]</backend>
    <backend>@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py#L22-L63]</backend>
    <backend>@[backend_v2/services/sdui/adapters/warning_card_adapter.py#L29-L100]</backend>
    <backend>@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L26-L177]</backend>
    <backend>@[backend_v2/workers/execution_worker.py#L50-L443]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py#L740-L815]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L246]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L75]</backend>
    <backend>@[backend_v2/services/orchestrator/sliding_window_linker.py#L71-L282]</backend>
    <backend>@[backend_v2/services/localization.py#L40-L283]</backend>
    <backend>@[backend_v2/services/matrix_domain_parser.py#L32-L631]</backend>
    <backend>@[backend_v2/services/blueprint.py#L321-L342]</backend>
    <backend>@[backend_v2/services/pdf_generator.py#L183-L205]</backend>
    <backend>@[scripts/audit_dict_eradication.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_engine.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]</backend>
    <backend>@[backend_v2/tests/unit/utils/scoring/test_unified_engine.py#L44-L61]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L906-L953]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py#L64-L81]</backend>
    <backend>@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint.py]</backend>
  </touched_artifacts>

  <step id="7.1" name="LightweightMatrixOutput &amp; ScoringResultDTO Primitive Obsession Eradication">
    <action>Modify @[backend_v2/models/dtos/lightweight_matrix.py#L37-L111]:</action>
    <action>- Relocate LevelStatsDTO definition (currently lines 71-85) before LightweightMatrixOutput (lines 37-69) to resolve class ordering invariants.</action>
    <action>- Migrate LightweightMatrixOutput.level_breakdown from dict[str, dict[str, int]] | None = None to dict[str, LevelStatsDTO] | None = None.</action>
    <action>- Migrate ScoringResultDTO.breakdown from dict[str, dict[str, int]] to dict[str, LevelStatsDTO].</action>
    <action>- Update LevelStatsDTO.model_config to ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>Modify @[backend_v2/utils/scoring/unified_engine.py#L41-L124]:</action>
    <action>- Update level_breakdown construction to pass LevelStatsDTO instances directly: {str(k): LevelStatsDTO(hits=v.hits, total=v.total, dlqs=v.dlqs) for k, v in stats.items()}.</action>
    <action>Modify @[backend_v2/services/orchestrator/matrix_explanation_service.py#L29-L276]:</action>
    <action>- Delete raw_level_breakdown popping and ad-hoc validation loop.</action>
    <action>- Directly iterate lw_matrix.level_breakdown: for lvl, stats_dto in lw_matrix.level_breakdown.items(): breakdowns.append(f"Level {lvl}: {stats_dto.hits}/{stats_dto.total} hits").</action>
    <action>Modify @[backend_v2/hooks/scoring/matrix_hook.py#L56-L528]:</action>
    <action>- Define BlockMetaDTO with scales: list[float], math_min: float, math_max: float under ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>- Type blocks_meta as dict[str, BlockMetaDTO].</action>
    <action>- Type block_scale_stats as dict[str, dict[float, LevelStatsDTO]].</action>
    <action>- Encapsulate evaluated_atoms_by_block and matrix_extensions_by_block in dedicated typed DTOs.</action>
    <action>Modify @[backend_v2/hooks/scoring/passivity_hook.py#L26-L157]:</action>
    <action>- Flatten matrix_blocks_meta: dict[str, dict[str, float]] into matrix_blocks_min: dict[str, float] = {pb_id: min(scale_values)}.</action>
    <action>Update unit tests:</action>
    <action>- Update @[backend_v2/tests/unit/utils/scoring/test_unified_engine.py#L44-L61] to assert dto.breakdown contains LevelStatsDTO instances with .hits and .total access.</action>
    <action>- Update @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L906-L953] to pass typed LevelStatsDTO instances in mock payloads.</action>
    <action>- Update @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py#L64-L81] asserting clean detection.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero permissive typing: all matrix metrics must flow via LevelStatsDTO with zero dictionary subscripting.</constraint>
  </step>

  <step id="7.2" name="SDUI Adapter AESTHETICS_RULES Primitive Obsession Eradication">
    <action>Modify @[backend_v2/models/dtos/sdui_rules.py#L65-L229]:</action>
    <action>- Define typed visual styling schemas for all remaining SDUI adapters:</action>
    <action>  * GlobalScoreAestheticsDTO with visual_intent: VisualIntent = VisualIntent.PRIMARY.</action>
    <action>  * MatrixGraphsAestheticsDTO with chart styling properties.</action>
    <action>  * MatrixSummaryAestheticsDTO with column width and alignment properties.</action>
    <action>  * McpAuditAestheticsDTO with tool badge visual intents.</action>
    <action>  * MetadataAestheticsDTO with metadata badge visual intents.</action>
    <action>  * SynthesisTextAestheticsDTO with prose intent styling.</action>
    <action>  * WarningCardAestheticsDTO with warning level to VisualIntent mapping.</action>
    <action>Modify SDUI adapters to bind module-level AESTHETICS_RULES to these frozen DTOs:</action>
    <action>- @[backend_v2/services/sdui/adapters/global_score_adapter.py#L20-L57]</action>
    <action>- @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py#L26-L106]</action>
    <action>- @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py#L25-L96]</action>
    <action>- @[backend_v2/services/sdui/adapters/mcp_audit_adapter.py#L20-L59]</action>
    <action>- @[backend_v2/services/sdui/adapters/metadata_adapter.py#L23-L103]</action>
    <action>- @[backend_v2/services/sdui/adapters/synthesis_text_adapter.py#L22-L63]</action>
    <action>- @[backend_v2/services/sdui/adapters/warning_card_adapter.py#L29-L100]</action>
    <action>- @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L26-L177] (bind to XaiAestheticsRulesDTO).</action>
    <constraint invariant="tripartite_rendering_boundary">Adapters must return pure SDUI block structures referencing typed styling tokens with zero naked dictionaries.</constraint>
  </step>

  <step id="7.3" name="Worker, Linker &amp; Core Parser Primitive Obsession Eradication">
    <action>Create [NEW] @[backend_v2/models/dtos/step_telemetry.py]:</action>
    <action>- Define StepTelemetryEntryDTO with model_strategy: str, physical_model: str | None, system_fingerprint: str | None, prompt_tokens: int, completion_tokens: int, cached_tokens: int, reasoning_tokens: int, cost_usd: float, chunk_count: int under ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>Modify @[backend_v2/workers/execution_worker.py#L50-L443]:</action>
    <action>- Replace step_telemetry: dict[str, dict[str, Any]] on Line 183 with step_telemetry: dict[str, StepTelemetryEntryDTO].</action>
    <action>- Update accumulation logic to use StepTelemetryEntryDTO with typed immutable updates.</action>
    <action>Create [NEW] @[backend_v2/models/dtos/matrix_parser.py]:</action>
    <action>- Define ParsedMatricesResultDTO with evaluative_matrices: list[MatrixScorecardRowDTO], informational_matrices: list[MatrixScorecardRowDTO], all_parsed_matrices: dict[str, MatrixScorecardRowDTO], and step_scorecard_atoms: dict[str, ScorecardAtomCollectionDTO].</action>
    <action>Modify @[backend_v2/services/matrix_domain_parser.py#L32-L631]:</action>
    <action>- Replace anonymous 4-tuple return with ParsedMatricesResultDTO.</action>
    <action>- Replace step_scorecard_atoms nested dictionary with typed collection.</action>
    <action>Modify 1-hop callers of parse_matrices:</action>
    <action>- @[backend_v2/services/blueprint.py#L321-L342]: Consume ParsedMatricesResultDTO via dot-notation, eliminating 4-tuple destructuring. Clean up line 219 .get() and line 305 TypeAdapter(dict).</action>
    <action>- @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]: Update all 4-tuple unpacking tests to assert against ParsedMatricesResultDTO attributes.</action>
    <action>- @[backend_v2/tests/unit/services/test_blueprint.py]: Update lines 1914-2055 to assert against ParsedMatricesResultDTO.</action>
    <action>Modify @[backend_v2/services/orchestrator/sliding_window_linker.py#L71-L282]:</action>
    <action>- Define WindowCausalEdgesDTO encapsulating edges: dict[str, CausalEdge].</action>
    <action>- Replace master_deps nested dict on Line 175 with dict[str, WindowCausalEdgesDTO].</action>
    <action>Modify @[backend_v2/services/localization.py#L40-L283]:</action>
    <action>- Define LocaleTranslationsDTO with translations: dict[str, str] and typed lookup method.</action>
    <action>- Replace _translations: dict[str, dict[str, str]] on Line 43 with dict[str, LocaleTranslationsDTO].</action>
    <action>Modify 1-hop callers of LocalizationService._translations:</action>
    <action>- @[backend_v2/services/pdf_generator.py#L183-L205]: Replace private attribute access LocalizationService._translations.get(lang_simple) with public LocalizationService.get_translations(lang_simple).</action>
    <action>Modify @[backend_v2/models/dtos/engine.py#L119-L168]:</action>
    <action>- Replace hydrated_messages: list[dict[str, str]] | None on Line 144 with hydrated_messages: list[LLMMessageDTO] | None.</action>
    <action>Modify @[backend_v2/services/orchestrator/strategies/llm.py#L740-L815]:</action>
    <action>- Construct static_msg = LLMMessageDTO(role=LLMRole.SYSTEM, content=static_instructions) on Line 744 and hydrated_messages with LLMMessageDTO instances on Lines 783-786.</action>
    <action>Modify @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L246]:</action>
    <action>- Update Line 142 local_messages copying from dict(msg) to list of LLMMessageDTO instances.</action>
    <action>Modify @[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L75]:</action>
    <action>- Forward strongly typed request.hydrated_messages directly to task_executor.execute_structured_task.</action>
    <action>Update unit tests for EngineExecutionRequest and engine callers:</action>
    <action>- Update @[backend_v2/tests/unit/models/dtos/test_engine.py] to test EngineExecutionRequest with list[LLMMessageDTO].</action>
    <action>- Update @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py] and @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py] to construct and pass LLMMessageDTO instances in test payloads.</action>
    <constraint invariant="ban_anonymous_state_tuples">Positional tuple destructuring and anonymous multi-value return tuples are strictly prohibited.</constraint>
  </step>

  <step id="7.4" name="Codebase-Wide AST Guardrails Sweep &amp; Full Reflection Lockdown">
    <action>Modify and enhance @[scripts/audit_dict_eradication.py]:</action>
    <action>- Expand AST visitor (_find_nested_dict_subscript) to detect all primitive collection obsession patterns, specifically list[dict[...]] and dict[..., dict[...]].</action>
    <action>- Update report aggregation to track primitive collection violations and verify 0 violations codebase-wide.</action>
    <action>- Verify 0 naked dict annotations in non-exempt files.</action>
    <action>- Verify 0 unauthorized/unjustified # noqa comment suppressions.</action>
    <action>- Verify 0 legacy dict_utils imports.</action>
    <action>- Verify 0 dynamic reflection calls (getattr, hasattr, object.__setattr__) in domain code.</action>
    <action>Modify and enhance @[scripts/_ast_guardrails.py]:</action>
    <action>- Synchronize QGR018 rule with primitive collection detection.</action>
    <action>- Verify 0 fatal violations (QGR000, QGR001, QGR002, QGR003, QGR012, QGR016, QGR018) across backend_v2 and scripts.</action>
    <action>- Verify all 156 previously identified test reflection instances remain completely eradicated.</action>
    <action>Update AST audit unit tests:</action>
    <action>- Update @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py#L64-L81] to assert positive detection and failure for list[dict[...]] patterns.</action>
    <constraint invariant="ast_guardrail_fatal_severity_mandate">AST guardrail violations in domain code are strictly FATAL with zero exemptions outside physical storage drivers.</constraint>
  </step>

  <step id="7.5" name="Two-Phase Database Seeder &amp; SDUI Semantic Parity Quality Gate">
    <action>Execute two-phase database seeder: uv run python backend_v2/seed/run_seed.py local.</action>
    <action>- Verify Phase 1: In-Memory Validation passes 100% with extra="forbid".</action>
    <action>- Verify Phase 2: Atomic Ingress commits cleanly.</action>
    <action>Execute SDUI semantic parity test: uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py.</action>
    <action>- Verify 1:1 semantic and visual parity between Flutter UI and PDF templates.</action>
    <action>Execute backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2 --test.</action>
    <action>- Verify Ruff formatting, MyPy strict typing, and >90% test coverage across all modified targets.</action>
    <action>Execute Flutter audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/api/reports_client.dart.</action>
    <action>- Verify clean Dart compilation with zero analyzer warnings.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Backend DTOs, PDF templates, and Flutter Freezed models must maintain 1:1 semantic parity.</constraint>
  </step>

  <step id="7.6" name="Live End-to-End Variance Test Run (E2E Gate)">
    <action>Execute live Real-LLM E2E integration test gate:</action>
    <action>- Windows PowerShell: $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py.</action>
    <action>- Unix/Bash: RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py.</action>
    <action>Execute live multi-provider variance runner: uv run python scripts/run_e2e_variance_test.py.</action>
    <action>- Verify FinOpsMonitorSummaryDTO and FinOpsFinalizeSummaryDTO telemetry contracts.</action>
    <action>- Verify that all provider responses hydrate cleanly without KeyError or AttributeError regressions.</action>
    <constraint invariant="quality_gate_execution">Completion gate requires passing the full end-to-end execution pipeline with live model verification.</constraint>
  </step>

  <validation_gate>
    <action>uv run python scripts/audit_dict_eradication.py</action>
    <action>uv run python scripts/_ast_guardrails.py backend_v2 scripts</action>
    <action>uv run python backend_v2/seed/run_seed.py local</action>
    <action>uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py</action>
    <action>uv run python scripts/backend_audit_loop.py backend_v2 --test</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/api/reports_client.dart</action>
  </validation_gate>
</execution_protocol>
```
