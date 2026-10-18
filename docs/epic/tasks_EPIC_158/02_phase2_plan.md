# Phase 2: Domain Model, DTO, Client Freezed Contract & Test Fixture Multi-Segment Schema Refactoring (WP1)

**Overview:** Refactor proposition and DAG models to represent evidence quotes as ordered tuples ($1 \le m \le 3$), enforcing Full-Duplex Parity across backend models, blackboard schemas, execution engines, projection pipelines, 1-hop caller services, Flutter Freezed consumer models, test factories, unit test suites, and golden master fixtures.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L232-L294] Phase 2: Domain Model, DTO, Client Freezed Contract & Test Fixture Multi-Segment Schema Refactoring (WP1)

**Target Files:**
- `[MODIFY]` @[backend_v2/models/core_base.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/extractive_sensor_service.py]
- `[MODIFY]` @[backend_v2/models/domain/blackboard.py]
- `[MODIFY]` @[backend_v2/models/dtos/dag_models.py]
- `[MODIFY]` @[backend_v2/models/dtos/causal_discovery.py]
- `[MODIFY]` @[backend_v2/models/dtos/atom_result.py]
- `[MODIFY]` @[backend_v2/models/dtos/atom_evaluation.py]
- `[MODIFY]` @[backend_v2/models/dtos/quote_evidence.py]
- `[MODIFY]` @[backend_v2/models/dtos/matrix_scorecard.py]
- `[MODIFY]` @[backend_v2/models/dtos/report_artifact.py]
- `[MODIFY]` @[backend_v2/services/sdui/sdui_mapper_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/topological_evaluator.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/matrix_hook.py]
- `[MODIFY]` @[backend_v2/services/matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/services/report_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/result_projector.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/state_reducer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_reducer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py]
- `[MODIFY]` @[backend_v2/services/studio/simulation_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/atom_extraction.py]
- `[MODIFY]` @[backend_v2/models/prompts/execution/field_prompts.py]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/atom_result_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L264-L295]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L697-L749]
- `[MODIFY]` @[backend_v2/tests/factories/model_factories.py]
- `[MODIFY]` @[backend_v2/llm/mock_data.py]
- `[MODIFY]` @[backend_v2/tests/fixtures/sdui_golden_master.json]
- `[MODIFY]` @[backend_v2/tests/test_data/report_data_dto_fixture.json]
- `[MODIFY]` @[backend_v2/tests/unit/models/domain/test_blackboard.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_atom_result.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_dag_models.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_quote_evidence.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_matrix_scorecard.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/test_atom_result_override_guard.py]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/core_base.py]`, `@[backend_v2/services/orchestrator/extractive_sensor_service.py]`, `@[backend_v2/models/domain/blackboard.py]`, `@[backend_v2/models/dtos/dag_models.py]`, `@[backend_v2/models/dtos/causal_discovery.py]`, `@[backend_v2/models/dtos/atom_result.py]`, `@[backend_v2/models/dtos/atom_evaluation.py]`, `@[backend_v2/models/dtos/quote_evidence.py]`, `@[backend_v2/models/dtos/matrix_scorecard.py]`, `@[backend_v2/models/dtos/report_artifact.py]` | Banned scalar `source_quote: str \| None`, bare `quote: str`, and strict Pydantic V2 list rejections. | Refactor models to `source_quotes: tuple[str, ...] \| None = None` ($1 \le m \le 3$, each $\ge 30$ chars when $m > 1$) with `BeforeValidator(coerce_source_quotes_tuple)` and Null Hypothesis invariants (`source_quotes is None` on `is_inverse_evidence=True`). | Pruned parallel single vs multi quote DTOs; single quotes represented as 1-tuples. | `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`. |
| `@[backend_v2/services/sdui/sdui_mapper_service.py]`, `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`, `@[backend_v2/services/orchestrator/topological_evaluator.py]`, `@[backend_v2/services/orchestrator/dag_executor.py]`, `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`, `@[backend_v2/hooks/scoring/matrix_hook.py]`, `@[backend_v2/services/matrix_domain_parser.py]`, `@[backend_v2/services/report_service.py]` | Banned retired `"source_quote"` keyword in `model_copy(update=...)`, scalar `atom.source_quote` in paragraph search, scalar `quote=ev_dto.source_quote`, and direct scalar access in report rows. | Update wave copy to `"source_quotes": res.source_quotes`, paragraph search to anchor on `atom.source_quotes[0]`, matrix hook/parser to `source_quotes=...`, and project `quote=" [...] ".join(atom.source_quotes) if atom.source_quotes else None` in `ReportRowItemDTO`. | Pruned manual string sanitizers; format deterministically from tuple. | `pytest backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| `@[backend_v2/services/orchestrator/synthesis_distiller.py]`, `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`, `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`, `@[backend_v2/services/orchestrator/result_projector.py]`, `@[backend_v2/services/orchestrator/state_reducer.py]`, `@[backend_v2/services/orchestrator/matrix_reducer.py]`, `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`, `@[backend_v2/services/orchestrator/engines/tda_engine.py]`, `@[backend_v2/services/studio/simulation_service.py]`, `@[backend_v2/services/orchestrator/prompts/atom_extraction.py]`, `@[backend_v2/models/prompts/execution/field_prompts.py]` | Banned dropping quote segments during distillation, state reduction, or atom extraction prompt compilation. | Preserve multi-segment `source_quotes` throughout distillation and reduction pipelines; update `DESC_SOURCE_QUOTE` and extraction prompts to instruct ordered non-contiguous multi-segment tuples. | Pruned custom serialization shims; transit immutable tuple directly. | `pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py`. |
| `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`, `@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]`, `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`, `@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]`, `@[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L264-L295]`, `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L697-L749]` | Banned legacy scalar `quote: String` and `sourceQuote: String?` in Freezed models enforcing `disallowUnrecognizedKeys: true`. Banned scalar quote string interpolation. | Refactor client models to `final List<String>? sourceQuotes` and `defaultLexicalStrictnessLevel: int`; update display to `q.sourceQuotes?.join(' [...] ') ?? ''` and pass `sourceQuotes: [l10n.humanOverrideExpertNote]`. | Pruned custom client-side JSON converters; rely on Freezed/JsonSerializable codegen. | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`. |
| `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/llm/mock_data.py]`, `@[backend_v2/tests/fixtures/sdui_golden_master.json]`, `@[backend_v2/tests/test_data/report_data_dto_fixture.json]`, `@[backend_v2/tests/unit/models/domain/test_blackboard.py]`, `@[backend_v2/tests/unit/models/dtos/test_atom_result.py]`, `@[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py]`, `@[backend_v2/tests/unit/models/dtos/test_dag_models.py]`, `@[backend_v2/tests/unit/models/dtos/test_quote_evidence.py]`, `@[backend_v2/tests/unit/models/dtos/test_matrix_scorecard.py]`, `@[backend_v2/tests/unit/models/test_atom_result_override_guard.py]` | Banned outdated scalar quote fixtures causing false test failures or masking schema breaking changes. | Atomically update model factories, mock responses, golden master fixtures, and unit test assertions to `source_quotes: tuple[str, ...] \| None`. | Pruned legacy string fixtures; align with modernized DTO contracts. | `uv run pytest backend_v2/tests/unit/models/`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify `coerce_source_quotes_tuple` and defined `GateMatchResultDTO` are established in @[backend_v2/models/core_base.py] and @[backend_v2/models/dtos/quote_evidence.py].</action>
    <action>Look forward: Verify all downstream DAG models, 1-hop caller services, and Flutter Freezed consumer contracts before refactoring `source_quote` to `source_quotes`.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/02_phase2_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/core_base.py]</backend>
    <backend>@[backend_v2/services/orchestrator/extractive_sensor_service.py]</backend>
    <backend>@[backend_v2/models/domain/blackboard.py]</backend>
    <backend>@[backend_v2/models/dtos/dag_models.py]</backend>
    <backend>@[backend_v2/models/dtos/causal_discovery.py]</backend>
    <backend>@[backend_v2/models/dtos/atom_result.py]</backend>
    <backend>@[backend_v2/models/dtos/atom_evaluation.py]</backend>
    <backend>@[backend_v2/models/dtos/quote_evidence.py]</backend>
    <backend>@[backend_v2/models/dtos/matrix_scorecard.py]</backend>
    <backend>@[backend_v2/models/dtos/report_artifact.py]</backend>
    <backend>@[backend_v2/services/sdui/sdui_mapper_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]</backend>
    <backend>@[backend_v2/services/orchestrator/topological_evaluator.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend>@[backend_v2/services/matrix_domain_parser.py]</backend>
    <backend>@[backend_v2/services/report_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/result_projector.py]</backend>
    <backend>@[backend_v2/services/orchestrator/state_reducer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_reducer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py]</backend>
    <backend>@[backend_v2/services/studio/simulation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompts/atom_extraction.py]</backend>
    <backend>@[backend_v2/models/prompts/execution/field_prompts.py]</backend>
    <frontend>@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/workflow.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`BooleanEvaluationResult` and `PreFlightResult` in @[backend_v2/services/orchestrator/extractive_sensor_service.py] refactored to `source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple` pre-validator.</item>
    <item>`DraftExtractedAtom` in @[backend_v2/models/domain/blackboard.py] refactored to `source_quotes: tuple[str, ...] | None`.</item>
    <item>`ExtractedAtom`, `AtomEvaluationResultDTO`, and `AtomExecutionState` in @[backend_v2/models/dtos/dag_models.py] refactored to `source_quotes: tuple[str, ...] | None`.</item>
    <item>`CausalNodeDTO` in @[backend_v2/models/dtos/causal_discovery.py] refactored to `source_quotes: tuple[str, ...] | None`.</item>
    <item>`AtomResultDTO`, `HydratedAtomDTO`, and `EvaluatedAtomDTO` in @[backend_v2/models/dtos/atom_result.py] refactored to `source_quotes: tuple[str, ...] | None`.</item>
    <item>`ReducedAtomDTO` in @[backend_v2/models/dtos/atom_evaluation.py] refactored to `source_quotes: tuple[str, ...] | None`.</item>
    <item>`QuoteEvidenceDTO` in @[backend_v2/models/dtos/quote_evidence.py] refactored from `quote: str` to `source_quotes: tuple[str, ...] | None`.</item>
    <item>`ScorecardAtomDTO` in @[backend_v2/models/dtos/matrix_scorecard.py] updated to transit `QuoteEvidenceDTO` with `source_quotes`.</item>
    <item>`ReportRowItemDTO` in @[backend_v2/models/dtos/report_artifact.py] and @[backend_v2/services/report_service.py] aligned to project multi-segment quotes with delimiter `" [...] "`.</item>
    <item>1-hop caller services (@[backend_v2/services/sdui/sdui_mapper_service.py], @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py], @[backend_v2/services/orchestrator/topological_evaluator.py], @[backend_v2/services/orchestrator/dag_executor.py], @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py], @[backend_v2/hooks/scoring/matrix_hook.py], @[backend_v2/services/matrix_domain_parser.py], @[backend_v2/services/orchestrator/synthesis_distiller.py], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py], @[backend_v2/services/orchestrator/matrix_explanation_service.py], @[backend_v2/services/orchestrator/result_projector.py], @[backend_v2/services/orchestrator/state_reducer.py], @[backend_v2/services/orchestrator/matrix_reducer.py], @[backend_v2/services/orchestrator/two_pass_atomizer.py], @[backend_v2/services/orchestrator/engines/tda_engine.py], @[backend_v2/services/studio/simulation_service.py]) migrated cleanly.</item>
    <item>Extraction prompt documentation in @[backend_v2/services/orchestrator/prompts/atom_extraction.py] and @[backend_v2/models/prompts/execution/field_prompts.py] updated for multi-segment tuples.</item>
    <item>Flutter Freezed DTOs (@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart], @[client_app_v2/lib/features/execution/models/atom_result_dto.dart], @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart], @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart], @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart], @[client_app_v2/lib/features/studio/models/workflow.dart]) and widgets (@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L264-L295], @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L697-L749]) updated and compiled with `build_runner`.</item>
    <item>Model factories, mock data, and test fixtures in @[backend_v2/tests/factories/model_factories.py], @[backend_v2/llm/mock_data.py], @[backend_v2/tests/fixtures/sdui_golden_master.json], @[backend_v2/tests/test_data/report_data_dto_fixture.json], and unit test suites (@[backend_v2/tests/unit/models/domain/test_blackboard.py], @[backend_v2/tests/unit/models/dtos/test_atom_result.py], @[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py], @[backend_v2/tests/unit/models/dtos/test_dag_models.py], @[backend_v2/tests/unit/models/dtos/test_quote_evidence.py], @[backend_v2/tests/unit/models/dtos/test_matrix_scorecard.py], @[backend_v2/tests/unit/models/test_atom_result_override_guard.py]) updated atomically.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_opaque_id_hydration.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT retain scalar `source_quote` fallback accessors in modernized DTOs.</anti_target>
    <anti_target>Do NOT relax Freezed `disallowUnrecognizedKeys: true` on the Flutter client.</anti_target>
    <anti_target>Do NOT alter database seed data or prompt matrices in Phase 2.</anti_target>
  </anti_targets>

  <contract_freeze>
    <contract id="source_quotes_transit_contract">
      <signature>source_quotes: tuple[str, ...] | None = None</signature>
      <invariants>1 to 3 ordered string segments; segment floor &gt;= 30 chars when m &gt; 1; None on absence under Null Hypothesis.</invariants>
    </contract>
    <contract id="QuoteEvidenceDto_freeze">
      <signature>final List&lt;String&gt;? sourceQuotes</signature>
      <invariants>Flutter Freezed model matching backend QuoteEvidenceDTO with disallowUnrecognizedKeys: true.</invariants>
    </contract>
  </contract_freeze>

  <step id="1" name="REFACTOR BACKEND DOMAIN MODELS &amp; DAG DTOS">
    <action>In @[backend_v2/models/core_base.py]: Re-export `coerce_source_quotes_tuple` SSOT for domain DTO pre-validation.</action>
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py]: Update `BooleanEvaluationResult` and `PreFlightResult` to `source_quotes: tuple[str, ...] | None = None` with `BeforeValidator(coerce_source_quotes_tuple)` and Null Hypothesis invariants (`source_quotes is None` on `is_inverse_evidence=True`).</action>
    <action>In @[backend_v2/models/domain/blackboard.py]: Update `DraftExtractedAtom.source_quotes: tuple[str, ...] | None = None` with `coerce_source_quotes_tuple`.</action>
    <action>In @[backend_v2/models/dtos/dag_models.py]: Update `ExtractedAtom`, `AtomEvaluationResultDTO`, and `AtomExecutionState` to replace `source_quote` with `source_quotes: tuple[str, ...] | None = None`.</action>
    <action>In @[backend_v2/models/dtos/causal_discovery.py]: Update `CausalNodeDTO.source_quotes: tuple[str, ...] | None = None`.</action>
    <action>In @[backend_v2/models/dtos/atom_result.py]: Update `AtomResultDTO`, `HydratedAtomDTO`, and `EvaluatedAtomDTO` to `source_quotes: tuple[str, ...] | None = None`.</action>
    <action>In @[backend_v2/models/dtos/atom_evaluation.py]: Update `ReducedAtomDTO.source_quotes: tuple[str, ...] | None = None`.</action>
    <action>In @[backend_v2/models/dtos/quote_evidence.py]: Update `QuoteEvidenceDTO` to replace `quote: str` with `source_quotes: tuple[str, ...] | None = None`.</action>
    <action>In @[backend_v2/models/dtos/matrix_scorecard.py]: Update `ScorecardAtomDTO.exact_quotes` holding modernized `QuoteEvidenceDTO`.</action>
    <action>In @[backend_v2/models/dtos/report_artifact.py]: Align `ReportRowItemDTO` quote documentation and validation.</action>
    <constraint invariant="the_zero_compromise_pledge">All models must enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`.</constraint>
  </step>

  <step id="2" name="REFACTOR 1-HOP CALLER ORCHESTRATION &amp; HOOK SERVICES">
    <action>In @[backend_v2/services/sdui/sdui_mapper_service.py]: Project `evidence.source_quotes` joined with `" [...] "` into `SduiQuoteCard` and `SduiWarningCard`.</action>
    <action>In @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]: Update line 266 `hydrated_references` construction to pass `source_quotes=None` instead of `source_quote=None`.</action>
    <action>In @[backend_v2/services/orchestrator/topological_evaluator.py]: Update line 163 state copy from `"source_quote": res.source_quote` to `"source_quotes": res.source_quotes`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py]: Update lines 110-112 to format `node.source_quotes` and line 224 to check `if not n.source_quotes`.</action>
    <action>In @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]: Update lines 182-198 to anchor on `atom.source_quotes[0]` across paragraphs and document directives, and lines 250 &amp; 333 for graph node compilation.</action>
    <action>In @[backend_v2/hooks/scoring/matrix_hook.py]: Update lines 421-426 to construct `QuoteEvidenceDTO(source_quotes=ev_dto.source_quotes, ...)`.</action>
    <action>In @[backend_v2/services/matrix_domain_parser.py]: Update lines 479-484 to construct `QuoteEvidenceDTO(source_quotes=val_data.source_quotes, ...)`.</action>
    <action>In @[backend_v2/services/report_service.py]: Update line 636 to project `quote=" [...] ".join(atom.source_quotes) if atom.source_quotes else None` in `ReportRowItemDTO`.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_distiller.py]: Update synthesis distillation to preserve `source_quotes`.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]: Update payload compression to handle multi-segment `source_quotes`.</action>
    <action>In @[backend_v2/services/orchestrator/matrix_explanation_service.py]: Update explanation service to format multi-segment quotes.</action>
    <action>In @[backend_v2/services/orchestrator/result_projector.py]: Project multi-segment `source_quotes` into `AtomResultDTO` and `HydratedAtomDTO`.</action>
    <action>In @[backend_v2/services/orchestrator/state_reducer.py]: Reduce multi-segment `source_quotes` in state reducer.</action>
    <action>In @[backend_v2/services/orchestrator/matrix_reducer.py]: Pass `source_quotes=atom.source_quotes` when compiling `ReducedAtomDTO` instances.</action>
    <action>In @[backend_v2/services/orchestrator/two_pass_atomizer.py]: Pass multi-segment quote extraction in two-pass atomizer for `ExtractedAtom` and `DraftExtractedAtom`.</action>
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py]: Update `ExtractedAtom` instantiations to pass `source_quotes=None`.</action>
    <action>In @[backend_v2/services/studio/simulation_service.py]: Update `ExtractedAtom` instantiations to pass `source_quotes=None`.</action>
    <constraint invariant="zero_service_layer_fallbacks">Zero silent fallbacks or `.get("source_quote")`; transit typed `source_quotes` directly.</constraint>
  </step>

  <step id="3" name="UPDATE ATOM EXTRACTION PROMPTS &amp; DESCRIPTIONS">
    <action>In @[backend_v2/services/orchestrator/prompts/atom_extraction.py]: Update atom extraction prompts to guide models to emit 1 to 3 ordered sentence quotes without ellipses.</action>
    <action>In @[backend_v2/models/prompts/execution/field_prompts.py]: Update `DESC_SOURCE_QUOTE` to reflect ordered multi-segment JSON array schema requirements.</action>
    <constraint invariant="two_tier_prompting">Prompts SSOT must reside strictly within `backend_v2/models/prompts`.</constraint>
  </step>

  <step id="4" name="SYNCHRONIZE FLUTTER FREEZED CONTRACTS &amp; CITATION WIDGETS">
    <action>In @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]: Update `QuoteEvidenceDto` from `quote: String` to `sourceQuotes: List<String>?`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/atom_result_dto.dart]: Update `AtomResultDTO` from `sourceQuote: String?` to `sourceQuotes: List<String>?`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]: Update `CausalNodeDto` from `sourceQuote: String?` to `sourceQuotes: List<String>?`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]: Update `HydratedAtomDto` from `sourceQuote: String?` to `sourceQuotes: List<String>?`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]: Update Freezed model for multi-segment quote parity.</action>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart]: Add `defaultLexicalStrictnessLevel: int` with `@Default(50)`.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L264-L295]: Update line 264 display to `q.sourceQuotes?.join(' [...] ') ?? ''` and lines 291-295 to pass `sourceQuotes: [l10n.humanOverrideExpertNote]`.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L697-L749]: Update line 697 uniqueKey and line 749 text to `q.sourceQuotes?.join(' [...] ') ?? ''`.</action>
    <action>Execute Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <constraint invariant="anti_semantic_drift_renaming">Maintain 1:1 serialization naming between backend `source_quotes` and frontend `sourceQuotes`.</constraint>
  </step>

  <step id="5" name="SYNCHRONIZE TEST FIXTURES, FACTORIES &amp; UNIT TESTS">
    <action>In @[backend_v2/tests/factories/model_factories.py]: Update model factories to generate `source_quotes: tuple[str, ...] | None`.</action>
    <action>In @[backend_v2/llm/mock_data.py]: Update mock LLM payloads with `source_quotes` segment arrays.</action>
    <action>In @[backend_v2/tests/fixtures/sdui_golden_master.json]: Update golden master fixture quote representation.</action>
    <action>In @[backend_v2/tests/test_data/report_data_dto_fixture.json]: Update report data DTO fixtures.</action>
    <action>In @[backend_v2/tests/unit/models/domain/test_blackboard.py]: Update blackboard model assertions to `source_quotes`.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_atom_result.py]: Update atom result DTO assertions to `source_quotes`.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py]: Update atom evaluation DTO assertions to `source_quotes`.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_dag_models.py]: Update DAG model assertions to `source_quotes`.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_quote_evidence.py]: Update quote evidence DTO assertions from `quote` to `source_quotes`.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_matrix_scorecard.py]: Update matrix scorecard assertions to `source_quotes`.</action>
    <action>In @[backend_v2/tests/unit/models/test_atom_result_override_guard.py]: Update override guard assertions to `source_quotes`.</action>
    <constraint invariant="anti_tdd_trap">Rewrite unit test assertions to match modern multi-segment contracts rather than reverting to loose types.</constraint>
  </step>

  <test_contracts>
    <test name="test_draft_extracted_atom_multi_segment_quotes_valid" category="positive">
      <input>DraftExtractedAtom(..., source_quotes=("Premise quote.", "Conclusion quote."))</input>
      <expected>Valid model instance with source_quotes as 2-tuple</expected>
    </test>
    <test name="test_atom_evaluation_result_dto_coerces_list_to_tuple" category="positive">
      <input>AtomEvaluationResultDTO(..., source_quotes=["Segment 1.", "Segment 2."])</input>
      <expected>source_quotes coerced to ("Segment 1.", "Segment 2.")</expected>
    </test>
    <test name="test_extracted_atom_segment_under_30_chars_when_m_greater_than_1_raises_error" category="boundary">
      <input>ExtractedAtom(..., source_quotes=("Valid premise sentence here.", "Short."))</input>
      <expected>raises ValidationError (segment floor &gt;= 30 chars for m &gt; 1)</expected>
    </test>
    <test name="test_quote_evidence_dto_empty_string_resolves_none" category="boundary">
      <input>QuoteEvidenceDTO(..., source_quotes="")</input>
      <expected>source_quotes resolves to None</expected>
    </test>
    <test name="test_atom_result_dto_null_hypothesis_absence_enforces_none_quotes" category="negative">
      <input>AtomResultDTO(..., is_true=False, is_inverse_evidence=True, source_quotes=("Phantom quote.",))</input>
      <expected>raises ValidationError (Null Hypothesis invariant)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute causal discovery DTO tests: `uv run pytest backend_v2/tests/unit/models/dtos/test_causal_discovery_dtos.py`.</action>
    <action>Execute extractive sensor tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py`.</action>
    <action>Execute blackboard tests: `uv run pytest backend_v2/tests/unit/models/domain/test_blackboard.py`.</action>
    <action>Execute modernized model DTO unit test suites: `uv run pytest backend_v2/tests/unit/models/dtos/test_atom_result.py backend_v2/tests/unit/models/dtos/test_atom_evaluation.py backend_v2/tests/unit/models/dtos/test_dag_models.py backend_v2/tests/unit/models/dtos/test_quote_evidence.py backend_v2/tests/unit/models/dtos/test_matrix_scorecard.py backend_v2/tests/unit/models/test_atom_result_override_guard.py`.</action>
    <action>Execute backend models audit: `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`.</action>
    <action>Execute Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
  </validation_gate>
</execution_protocol>
```
