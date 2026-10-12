# Phase 5: Atomic SDUI Presentation Parity & Theme Sovereignty

**Overview:** Implement the server-driven presentation layer for causal discovery adhering strictly to the Dumb Painter architecture and Flutter Theme Sovereignty. Define `SduiCausalGraphBlock` in `backend_v2/models/view/sdui.py` and its Dart Freezed counterpart in `client_app_v2/lib/shared/models/sdui_block_dto.dart` with reference equality optimization (`@Freezed(equal: false)`). Extend `AdapterContext` with in-memory `causal_result` in `backend_v2/services/sdui/adapters/base_adapter.py`. Implement `CausalGraphAdapter` in `backend_v2/services/sdui/adapters/causal_graph_adapter.py` and integrate with `ExecutiveSummaryAdapter` in `backend_v2/services/sdui/adapters/executive_summary_adapter.py` and `backend_v2/services/blueprint.py` to project the Unified Causal Action Card into `TargetBlockType.EXECUTIVE_SUMMARY_BLOCK` (Zero New Output Profiles Invariant). Inject `<causal_diagnosis>` into synthesis tasks in `backend_v2/workers/synthesis_tasks.py` and `backend_v2/workers/synthesis_worker.py`. Implement the A4 PDF Jinja2 macro in `backend_v2/templates/report_template.jinja2`, build `SduiCausalGraphWidget` and `CausalInspectorModal` in Flutter wrapped with `AppErrorBoundary` and verified by `scripts/audit_flutter_theme_sovereignty.py`, register the block in `sdui_blocks_renderer.dart`, and update Golden Master fixtures and SDUI parity test suites to assert 19 SDUI block types.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 5: Presentation Parity, Studio Dispatch & Export Symmetry

**Target Files:**
- `[MODIFY] @[backend_v2/models/view/sdui.py#L778-L784]`
- `[NEW] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`
- `[MODIFY] @[client_app_v2/lib/shared/models/sdui_block_dto.dart#L9-L170]`
- `[NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`
- `[MODIFY] @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`
- `[MODIFY] @[backend_v2/services/sdui/adapters/executive_summary_adapter.py#L20-L96]`
- `[MODIFY] @[backend_v2/services/blueprint.py#L63-L618]`
- `[MODIFY] @[backend_v2/workers/synthesis_tasks.py#L61-L133]`
- `[MODIFY] @[backend_v2/workers/synthesis_worker.py#L86-L571]`
- `[MODIFY] @[backend_v2/templates/report_template.jinja2#L85-L570]`
- `[NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`
- `[NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`
- `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L19-L112]`
- `[MODIFY] @[backend_v2/tests/fixtures/sdui_golden_master.json#L50-L480]`
- `[MODIFY] @[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]`
- `[MODIFY] @[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]`
- `[MODIFY] @[scripts/audit_flutter_theme_sovereignty.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/view/sdui.py#L778-L784]`, `@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L9-L170]`, [NEW] `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]` | Client-side graph semantic calculation, client inferring root causes, generic raw JSON passing, loose block discriminators, missing Freezed Dart models. Deep equality checks on large collections causing UI rebuild performance degradation. | `SduiCausalGraphBlock(SduiBlockBase)` added to `AnySduiBlock` discriminated union with strict `block_type: Literal["causal_graph"] = "causal_graph"` and `ConfigDict(title="causal_graph", strict=True, extra="forbid")`. 1:1 Freezed `@Freezed(equal: false, unionKey: 'block_type')` Dart model with `@FreezedUnionValue('causal_graph')`. Dedicated Freezed DTOs in `causal_discovery_dto.dart` for causal nodes, edges, diagnoses, remediations, and fair scoring. | Dynamic client-side layout calculators, SVG graph vector serialization over HTTP, multi-pass SDUI transformers, separate disjoint report blocks, and speculative `CausalDisplayMode` enums. | `test_sdui_template_parity.py` asserting 19 SDUI block types; `backend_audit_loop.py`; `flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`. |
| `@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`, [NEW] `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`, `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py#L20-L96]`, `@[backend_v2/services/blueprint.py#L63-L618]` | Raw dictionary passing in `AdapterContext`, loose fallback defaults (`.get("causal_result")`), new output profile clutter (`TargetBlockType.CAUSAL_GRAPH_BLOCK`). | `AdapterContext` extended with strictly typed in-memory field `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None`. `CausalGraphAdapter` implements `SduiAdapterProtocol` returning `[SduiCausalGraphBlock]`. `ExecutiveSummaryAdapter` unifies top fold inside `TargetBlockType.EXECUTIVE_SUMMARY_BLOCK` (Zero New Output Profiles Invariant). | Standalone dedicated causal report tab; multi-pass SDUI transformers; secondary output profile schemas. | `test_executive_summary_adapter_injects_causal_block_when_present`, `test_executive_summary_adapter_omits_causal_block_when_absent`, `test_causal_graph_adapter_data_starvation_omits_block`. |
| `@[backend_v2/workers/synthesis_tasks.py#L61-L133]`, `@[backend_v2/workers/synthesis_worker.py#L86-L571]` | Disconnected LLM synthesis generating generic prose contradicting the empirical causal action card. | In Phase 2 synthesis, inject `<causal_diagnosis>` containing root causes and fault chains into `create_executive_summary_task` prompt dynamic tail, ensuring high-level prose and action card speak with 100% mutual coherence. | Dedicated parallel synthesis worker daemons or speculative secondary causal synthesis pipelines. | Synthesis worker unit tests in `backend_audit_loop.py`. |
| `@[backend_v2/templates/report_template.jinja2#L85-L570]`, [NEW] `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`, [NEW] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L19-L112]`, `@[scripts/audit_flutter_theme_sovereignty.py]` | Hardcoded hex colors (`Color(0x...)`), `Colors.*`, naked `TextStyle(...)`, visual drift between PDF and screen, full graph clutter on printed report. | Jinja2 macro `render_causal_graph_block` and Flutter `SduiCausalGraphWidget` render the identical compact Unified Causal Action Card (max half A4 page). Full interactive exploration decoupled into `CausalInspectorModal`. All Flutter styling derives from `Theme.of(context).colorScheme`, `AppSemanticColors`, and `textTheme`. Both wrapped in `AppErrorBoundary`. Registered in `scripts/audit_flutter_theme_sovereignty.py`. | Monolithic spaghetti graph rendering on printed page; client-side graph simulation algorithms. | `scripts/audit_flutter_theme_sovereignty.py` passing with 0 violations; `flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`. |
| `@[backend_v2/tests/fixtures/sdui_golden_master.json#L50-L480]`, `@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]`, `@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]` | Stale Golden Master fixtures, unverified block models, missing template parity checks, broken contextual override test setups omitting quotes column. | Synchronously register `SduiCausalGraphBlock` in `PYDANTIC_BLOCK_MODELS` and `DART_UNION_TYPE_MAP` asserting 19 SDUI block types. Golden Master fixture contains valid populated block. Fix `parity_matrix_block` in `test_sdui_semantic_parity.py` to include `"quotes"` in `matrix_visible_columns` and `matrix_column_labels`. | Ad-hoc template snapshot bypasses. | `test_sdui_template_parity.py` and `test_sdui_semantic_parity.py` passing 100%. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 4. Verify fusion chaining and defined `CausalTdaFusionResultDTO` are implemented and tested.</action>
    <action>Look forward: Verify if `SduiCausalGraphBlock` integrates seamlessly into `TargetBlockType.EXECUTIVE_SUMMARY_BLOCK`, preserving the Zero New Output Profiles Invariant without requiring new layout profiles.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_154/05_phase5_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>In @[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380], restore "quotes" to matrix_visible_columns and matrix_column_labels in parity_matrix_block to resolve existing technical debt where contextual override test asserted on missing quotes column.</action>
    <action>Create [NEW] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart] defining Freezed models CausalNodeDto, CausalEdgeDto, CausalRootCauseDiagnosisDto, AntiFluffAuditDto, PrescriptiveRemediationDto, and FairScoringBreakdownDto with @Freezed(equal: false) and @JsonSerializable(disallowUnrecognizedKeys: true) to eliminate compilation gaps before sdui_block_dto.dart modification.</action>
    <action>In @[scripts/audit_flutter_theme_sovereignty.py], register client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart and client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart in DEFAULT_TARGET_FILES.</action>
    <constraint invariant="zero_duct_tape">Eliminate pre-existing test fixture fractures and missing model gaps before domain implementation.</constraint>
  </step>

  <dod_checklist>
    <item>SduiCausalGraphBlock added to backend_v2/models/view/sdui.py with sealed discriminator block_type="causal_graph" and ConfigDict(strict=True, extra="forbid"), appended to AnySduiBlock union, registered in _sdui_localns, and model_rebuild called.</item>
    <item>Dart Freezed CausalNodeDto, CausalEdgeDto, CausalRootCauseDiagnosisDto, AntiFluffAuditDto, PrescriptiveRemediationDto, FairScoringBreakdownDto created in causal_discovery_dto.dart and SduiCausalGraphBlock added to client_app_v2/lib/shared/models/sdui_block_dto.dart with @Freezed(equal: false, unionKey: 'block_type') and @FreezedUnionValue('causal_graph').</item>
    <item>AdapterContext in base_adapter.py extended with typed in-memory causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None.</item>
    <item>CausalGraphAdapter implemented in backend_v2/services/sdui/adapters/causal_graph_adapter.py transforming causal_result into SduiCausalGraphBlock.</item>
    <item>ExecutiveSummaryAdapter in executive_summary_adapter.py and blueprint.py updated to assemble SduiCausalGraphBlock within TargetBlockType.EXECUTIVE_SUMMARY_BLOCK (Zero New Output Profiles Invariant).</item>
    <item>Synthesis task in workers/synthesis_tasks.py injects &lt;causal_diagnosis&gt; into prompt dynamic tail whenever causal results exist.</item>
    <item>Jinja2 macro render_causal_graph_block implemented in backend_v2/templates/report_template.jinja2 rendering half-page A4 Unified Causal Action Card.</item>
    <item>SduiCausalGraphWidget implemented in Flutter wrapped with AppErrorBoundary and strictly obeying Flutter Theme Sovereignty.</item>
    <item>CausalInspectorModal implemented in Flutter for pro-tool pan/zoom inspection wrapped with AppErrorBoundary and obeying Theme Sovereignty.</item>
    <item>SduiCausalGraphBlock registered in sdui_blocks_renderer.dart dispatch.</item>
    <item>Valid populated SduiCausalGraphBlock instance added to backend_v2/tests/fixtures/sdui_golden_master.json.</item>
    <item>test_sdui_template_parity.py updated asserting 19 SDUI block types across PYDANTIC_BLOCK_MODELS and DART_UNION_TYPE_MAP.</item>
    <item>test_sdui_semantic_parity.py passes 100% verifying 1:1 cross-platform token and layout parity.</item>
    <item>scripts/audit_flutter_theme_sovereignty.py passes 100% with zero raw colors or naked TextStyles.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do not create separate TargetBlockType.CAUSAL_GRAPH_BLOCK in target_block_order.</forbidden>
    <forbidden>Do not instantiate raw Color(0x...) or Colors.* in SduiCausalGraphWidget or CausalInspectorModal.</forbidden>
    <forbidden>Do not use naked TextStyle(...) instantiations; derive strictly from Theme.of(context).textTheme.</forbidden>
    <forbidden>Do not perform semantic graph calculations or root cause inference on the Flutter client.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/models/view/sdui.py#L778-L784]</backend>
    <backend>[NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]</backend>
    <backend>@[backend_v2/services/sdui/adapters/executive_summary_adapter.py#L20-L96]</backend>
    <backend>@[backend_v2/services/blueprint.py#L63-L618]</backend>
    <backend>@[backend_v2/workers/synthesis_tasks.py#L61-L133]</backend>
    <backend>@[backend_v2/workers/synthesis_worker.py#L86-L571]</backend>
    <backend>@[backend_v2/templates/report_template.jinja2#L85-L570]</backend>
    <frontend>[NEW] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L9-L170]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L19-L112]</frontend>
    <support>@[backend_v2/tests/fixtures/sdui_golden_master.json#L50-L480]</support>
    <support>@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]</support>
    <support>@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]</support>
    <support>@[scripts/audit_flutter_theme_sovereignty.py]</support>
  </touched_artifacts>

  <step id="5.1" name="SDUI_MODEL_DEFINITION_AND_DART_PARITY">
    <action>In @[backend_v2/models/view/sdui.py#L778-L784], define SduiCausalGraphBlock(SduiBlockBase) with block_type: Literal["causal_graph"] = "causal_graph", ConfigDict(title="causal_graph", strict=True, extra="forbid"), critical_path_nodes: list[CausalNodeDTO], critical_edges: list[CausalEdgeDTO], root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO], anti_fluff_audit: AntiFluffAuditDTO, prescriptive_remediations: list[PrescriptiveRemediationDTO], fair_scoring: FairScoringBreakdownDTO | None = None, intact_claims_count: int, total_claims_count: int, summary: I18nText. Append to AnySduiBlock union, register in _sdui_localns, and invoke SduiCausalGraphBlock.model_rebuild(_types_namespace=_sdui_localns).</action>
    <action>In [NEW] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart], define Freezed models CausalNodeDto, CausalEdgeDto, CausalRootCauseDiagnosisDto, AntiFluffAuditDto, PrescriptiveRemediationDto, and FairScoringBreakdownDto with @Freezed(equal: false) and @JsonSerializable(disallowUnrecognizedKeys: true).</action>
    <action>In @[client_app_v2/lib/shared/models/sdui_block_dto.dart#L9-L170], define Freezed SduiCausalGraphBlock variant with @Freezed(equal: false, unionKey: 'block_type') and @FreezedUnionValue('causal_graph') matching 1:1 fields.</action>
    <constraint invariant="anti_semantic_drift_renaming">1:1 field nomenclature between Python snake_case and Dart camelCase.</constraint>
  </step>

  <step id="5.2" name="ADAPTER_CONTEXT_EXTENSION_AND_CAUSAL_GRAPH_ADAPTER">
    <action>In @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47], extend AdapterContext with typed in-memory field causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None and register in AdapterContext.model_rebuild. Document backend_v2/services/blueprint.py as the single production construction site for hydration.</action>
    <action>Create [NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py] implementing CausalGraphAdapter conforming to SduiAdapterProtocol providing build(context: AdapterContext) -> list[AnySduiBlock] and build_action_card(ctx: AdapterContext) -> SduiCausalGraphBlock, populating card blocks directly based on profile.visible_block_extensions.</action>
    <constraint invariant="zero_service_layer_fallbacks">AdapterContext envelope remains strictly typed with zero raw dictionaries.</constraint>
  </step>

  <step id="5.3" name="EXECUTIVE_SUMMARY_INTEGRATION_AND_BLUEPRINT_WIRING">
    <action>In @[backend_v2/services/sdui/adapters/executive_summary_adapter.py#L20-L96] and @[backend_v2/services/blueprint.py#L63-L618], assemble SduiCausalGraphBlock directly within TargetBlockType.EXECUTIVE_SUMMARY_BLOCK whenever context.causal_result is present: 1. Status pill, 2. Holistic narrative ParagraphBlock, 3. Unified Causal Action Card SduiCausalGraphBlock, 4. Strategic recommendations BulletListBlock (Zero New Output Profiles Invariant).</action>
    <action>In @[backend_v2/workers/synthesis_worker.py#L86-L571] and @[backend_v2/workers/synthesis_tasks.py#L61-L133], inject &lt;causal_diagnosis&gt; into create_executive_summary_task dynamic context tail whenever causal payload exists in execution step_states or execution_trace.</action>
    <constraint invariant="single_presentation_point">Project causal results into exactly one presentation point in EXECUTIVE_SUMMARY_BLOCK.</constraint>
  </step>

  <step id="5.4" name="JINJA2_PDF_MACRO_IMPLEMENTATION">
    <action>In @[backend_v2/templates/report_template.jinja2#L85-L570], implement macro render_causal_graph_block: render compact linear critical causal path ([Root Cause] -&gt; [Cascading Fault] -&gt; [Score Loss]), lexical quote card with paragraph_ref, prescriptive remediation card, and intact claims count chip (occupying at most half an A4 page in PDF).</action>
    <constraint invariant="dumb_painter_sdui">PDF macro performs zero calculation; renders pre-computed DTO blocks purely.</constraint>
  </step>

  <step id="5.5" name="FLUTTER_WIDGET_AND_INSPECTOR_MODAL_IMPLEMENTATION">
    <action>In [NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart], implement SduiCausalGraphWidget rendering the identical layout matching Jinja2 PDF macro, wrapped with AppErrorBoundary and strictly obeying Flutter Theme Sovereignty: all colors resolve via Theme.of(context).colorScheme or AppSemanticColors, and typography via Theme.of(context).textTheme.</action>
    <action>In [NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart], implement CausalInspectorModal providing interactive pan/zoom navigation, citation exploration, and remediation simulation, decoupled from primary layout, wrapped with AppErrorBoundary, and obeying Theme Sovereignty.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L19-L112], register SduiCausalGraphBlock handler dispatching to SduiCausalGraphWidget.</action>
    <action>In @[scripts/audit_flutter_theme_sovereignty.py], register new widgets in DEFAULT_TARGET_FILES.</action>
    <constraint invariant="theme_sovereignty">Zero raw Color(0x...), Colors.*, or naked TextStyle(...).</constraint>
  </step>

  <step id="5.6" name="GOLDEN_MASTER_AND_PARITY_TEST_SYNCHRONIZATION">
    <action>In @[backend_v2/tests/fixtures/sdui_golden_master.json#L50-L480], add a valid populated SduiCausalGraphBlock instance.</action>
    <action>In @[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148], register SduiCausalGraphBlock in PYDANTIC_BLOCK_MODELS and DART_UNION_TYPE_MAP, and assert 19 SDUI block types.</action>
    <action>In @[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380], verify 1:1 cross-platform SDUI parity between Flutter widget and Jinja2 PDF output.</action>
    <action>Execute scripts/audit_flutter_theme_sovereignty.py client_app_v2/ verifying zero theme sovereignty violations.</action>
    <constraint invariant="sdui_contract_fracture_prevention">100% semantic and structural parity across Python, Jinja2, and Flutter representations.</constraint>
  </step>

  <test_contracts>
    <test name="test_sdui_causal_graph_block_serialization_roundtrip" category="positive">
      <input>SduiCausalGraphBlock with valid critical path nodes, edges, diagnoses, remediations</input>
      <expected>serializes to JSON with block_type="causal_graph" and re-validates via SduiBlockBase</expected>
    </test>
    <test name="test_sdui_causal_graph_block_extra_field_forbid" category="negative">
      <input>Payload containing unrecognized extra field passed to SduiCausalGraphBlock</input>
      <expected>raises pydantic.ValidationError due to extra="forbid"</expected>
    </test>
    <test name="test_executive_summary_adapter_injects_causal_block_when_present" category="positive">
      <input>AdapterContext with non-null causal_result</input>
      <expected>returns list of blocks containing SduiCausalGraphBlock inside EXECUTIVE_SUMMARY_BLOCK sequence</expected>
    </test>
    <test name="test_executive_summary_adapter_omits_causal_block_when_absent" category="boundary">
      <input>AdapterContext with causal_result=None</input>
      <expected>returns standard executive summary blocks without SduiCausalGraphBlock and zero exceptions</expected>
    </test>
    <test name="test_causal_graph_adapter_data_starvation_omits_block" category="boundary">
      <input>AdapterContext with is_data_starved=True</input>
      <expected>returns empty list, preventing broken card emission during data starvation</expected>
    </test>
    <test name="test_sdui_template_parity_asserts_19_block_types" category="positive">
      <input>PYDANTIC_BLOCK_MODELS and DART_UNION_TYPE_MAP</input>
      <expected>len == 19 including SduiCausalGraphBlock</expected>
    </test>
    <test name="test_sdui_semantic_parity_contextual_override_roundtrip" category="positive">
      <input>SduiMatrixTableBlock with visible columns label, raw_score, quotes and contextual override atom</input>
      <expected>1:1 typographical and token parity between Flutter widget and Jinja2 PDF output</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run pytest backend_v2/tests/unit/test_sdui_template_parity.py</action>
    <action>Execute: uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py</action>
    <action>Execute: uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/</action>
    <action>Execute: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/models/view/sdui.py --test</action>
  </validation_gate>
</execution_protocol>
