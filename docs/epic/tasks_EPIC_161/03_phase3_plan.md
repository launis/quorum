<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 3: Frontend Flutter UI, Jinja PDF & Freezed SDUI DTO Synchronization

**Overview:** Bind topological short-circuit lineage (`short_circuited_by_claims`) and Toulmin falsification lineage (`falsified_warrant_claims`) directly onto matrix row items and causal graph nodes across `@[backend_v2/models/dtos/report_data.py]`, `@[backend_v2/models/view/sdui.py]`, `@[backend_v2/services/blueprint.py#L127-L698]`, `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`, and `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L32-L185]`. Refactor `@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]` so short-circuit (`N_A`) lineage is anchored contextually within its parent matrix summary table and causal graph block rather than orphaned at the bottom of the report. Synchronize Jinja2 PDF templates (`@[backend_v2/templates/report_template.jinja2]`), `@[backend_v2/services/pdf_generator.py]`, Flutter Freezed models (`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]` and `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`), and Flutter SDUI widgets (`@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` and `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`) with 100% Tripartite Cross-Domain Parity.

**Source:** @[docs/epic/EPIC_161_topological_synthesis_cohesion.md#L198-L204] Phase 3: Frontend Flutter UI, Jinja PDF & Freezed SDUI DTO Synchronization

**Target Files:**
- `[MODIFY] @[backend_v2/models/dtos/report_data.py]`
- `[MODIFY] @[backend_v2/models/view/sdui.py]`
- `[MODIFY] @[backend_v2/services/blueprint.py#L127-L698]`
- `[MODIFY] @[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]`
- `[MODIFY] @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`
- `[MODIFY] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L32-L185]`
- `[MODIFY] @[backend_v2/templates/report_template.jinja2]`
- `[MODIFY] @[backend_v2/services/pdf_generator.py]`
- `[MODIFY] @[client_app_v2/lib/shared/models/sdui_block_dto.dart]`
- `[MODIFY] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`
- `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`
- `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`
- `[MODIFY] @[backend_v2/tests/unit/services/sdui/test_sdui_mapper_service.py]`
- `[MODIFY] @[client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/services/blueprint.py#L127-L698]`**<br>**`@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]`**<br>**`@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`**<br>**`@[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L32-L185]`**<br>**`@[backend_v2/models/dtos/report_data.py]`**<br>**`@[backend_v2/models/view/sdui.py]`** | Eradicate dumping disconnected `SduiNACard` blocks at the bottom of the report (lines `146–160` of `@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]`) severed from the matrix row and causal graph node where the dependency chain broke. | Bind topological short-circuit lineage (`short_circuited_by_claims`) and Toulmin falsification lineage (`falsified_warrant_claims`) directly into matrix row items and `CausalGraphAdapter` node metadata across `report_data.py`, `models/view/sdui.py`, `matrix_summary_table_adapter.py`, and `causal_graph_adapter.py`. | Do NOT invent new bespoke SDUI widget primitives; enrich existing `SduiMatrixSummaryTableBlock`, `SduiCausalGraphBlock`, and `SduiXaiHighlightsBlock` schemas to display the linked causal argument cleanly. | `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/ --test --ast-strict` + unit tests in `@[backend_v2/tests/unit/services/sdui/test_sdui_mapper_service.py]`. |
| **`@[backend_v2/templates/report_template.jinja2]`**<br>**`@[backend_v2/services/pdf_generator.py]`** | Eradicate omitting topological short-circuit blocker badges and Toulmin rebuttal links from static PDF exports. | Update `@[backend_v2/templates/report_template.jinja2]` and `@[backend_v2/services/pdf_generator.py]` to render inline `short_circuited_by_claims` blocker badges and `falsified_warrant_claims` Toulmin rebuttal links in 1:1 parity with SDUI blocks. | Do NOT add LLM calls or dynamic computations inside Jinja2 templates; keep PDF rendering 100% deterministic over `ReportDataDTO`. | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`. |
| **`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]`**<br>**`@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`**<br>**`@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`**<br>**`@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`** | Eradicate schema drift between Backend Python SDUI DTOs and Frontend Dart Freezed models or hardcoded typography/spacing in SDUI widgets. | Synchronize `@JsonKey(name: 'snake_case')` fields on Freezed models in `sdui_block_dto.dart` and `causal_discovery_dto.dart`, render inline topological short-circuit badges and Toulmin rebuttal indicators in `sdui_matrix_table_widget.dart` and `sdui_causal_graph_widget.dart` using `Theme.of(context).textTheme` and `AppSpacing` tokens, and run Freezed code generation. | Do NOT introduce client-side graph traversal or heuristic string matching in Flutter widgets; render strictly what Backend SDUI DTOs provide (`strict_sdui_rendering_mandate`). | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` + widget tests in `@[client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart]`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 2 completion of [NEW] `MatrixFailureDeficitDTO` and [NEW] `CausalSynthesisBriefDTO` defined in @[backend_v2/models/dtos/synthesis.py], @[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311], and @[backend_v2/workers/synthesis_worker.py#L92-L664].</action>
    <action>Look forward: Read @[backend_v2/models/dtos/report_data.py], @[backend_v2/models/view/sdui.py], @[backend_v2/services/blueprint.py#L127-L698], @[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167], @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py], @[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L32-L185], @[backend_v2/templates/report_template.jinja2], @[backend_v2/services/pdf_generator.py], @[client_app_v2/lib/shared/models/sdui_block_dto.dart], @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart], @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart], and @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart].</action>
    <constraint invariant="sdui_contract_fracture_prevention">Maintain 1:1 field and semantic parity across Backend Python DTOs, Jinja2 PDF templates, and Frontend Dart Freezed models.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_161_topological_synthesis_cohesion.md] and @[docs/epic/EPIC_161_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/03_phase3_plan.md] @[docs/epic/EPIC_161_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/dtos/report_data.py]</backend>
    <backend>@[backend_v2/models/view/sdui.py]</backend>
    <backend>@[backend_v2/services/blueprint.py]</backend>
    <backend>@[backend_v2/services/sdui/sdui_mapper_service.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]</backend>
    <backend>@[backend_v2/templates/report_template.jinja2]</backend>
    <backend>@[backend_v2/services/pdf_generator.py]</backend>
    <backend>@[backend_v2/tests/unit/services/sdui/test_sdui_mapper_service.py]</backend>
    <frontend>@[client_app_v2/lib/shared/models/sdui_block_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]</frontend>
    <frontend>@[client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`@[backend_v2/models/dtos/report_data.py]`, `@[backend_v2/models/view/sdui.py]`, `@[backend_v2/services/blueprint.py#L127-L698]`, `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`, and `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L32-L185]` bind `short_circuited_by_claims: list[str]` and `falsified_warrant_claims: list[str]` directly onto matrix row items and causal graph nodes.</item>
    <item>`SduiMapperService.map_report_to_sdui` (`@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]`, lines 110-165 and 146-160) anchors short-circuit (`N_A`) lineage contextually within its parent matrix summary table and causal graph block rather than dumping disconnected `SduiNACard` entries at the bottom of the report.</item>
    <item>Jinja2 PDF template (`@[backend_v2/templates/report_template.jinja2]`) and `@[backend_v2/services/pdf_generator.py]` render inline short-circuit blocker badges and Toulmin rebuttal links in 1:1 parity with SDUI blocks.</item>
    <item>Flutter Freezed models (`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]` and `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`) and SDUI widgets (`@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` and `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`) synchronized with 1:1 `@JsonKey(name: 'snake_case')` parity and verified via `flutter_audit_loop.py --build`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT invent new bespoke SDUI widget primitives; enrich existing `SduiMatrixSummaryTableBlock`, `SduiCausalGraphBlock`, and `SduiXaiHighlightsBlock` schemas.</anti_target>
    <anti_target>Do NOT use `SizedBox.shrink()`, hardcoded `TextStyle(...)`, or hardcoded pixel spacing in Flutter widgets; strictly enforce `Theme.of(context).textTheme` and `AppSpacing` design tokens.</anti_target>
    <anti_target>Do NOT introduce LLM calls into SDUI adapters (`@[backend_v2/services/sdui/adapters/]`); SDUI adapters must remain 100% pure deterministic mappers.</anti_target>
  </anti_targets>

  <demolish>
    <item target="@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]">Eradicate appending disembodied `SduiNACard` entries at the bottom of `inner_sdui_blocks` at lines 146-160 when already bound inline to matrix summary rows and causal graph nodes.</item>
  </demolish>

  <step id="3.1" name="Inline Topological &amp; Short-Circuit Lineage in SDUI Blocks &amp; Report DTOs">
    <action>In @[backend_v2/models/dtos/report_data.py] and @[backend_v2/models/view/sdui.py], add `short_circuited_by_claims: list[str]` and `falsified_warrant_claims: list[str]` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) onto the matrix row item and causal graph node DTOs.</action>
    <action>In @[backend_v2/services/blueprint.py#L127-L698] (lines 574-658), @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py], and @[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L32-L185], populate `short_circuited_by_claims` and `falsified_warrant_claims` directly from the topological evaluation lineage and `CausalTdaFusionResultDTO`.</action>
    <action>In @[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167] (lines 110-165 and 146-160), refactor `map_report_to_sdui` so short-circuit (`N_A`) lineage is anchored contextually within its parent matrix summary table and causal graph block rather than orphaned at the bottom of the report.</action>
    <action>In @[backend_v2/tests/unit/services/sdui/test_sdui_mapper_service.py], add positive, boundary, and negative unit tests verifying contextual short-circuit lineage and Toulmin rebuttal mapping in `SduiMatrixSummaryTableBlock` and `SduiCausalGraphBlock`.</action>
    <constraint invariant="tripartite_rendering_boundary">SDUI adapters must remain pure synchronous data mappers returning strictly typed Pydantic V2 DTOs.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/report_data.py backend_v2/models/view/sdui.py backend_v2/services/blueprint.py backend_v2/services/sdui/ --test --ast-strict</audit_command>
  </step>

  <step id="3.2" name="Jinja2 PDF Template &amp; PDF Generator Parity">
    <action>In @[backend_v2/templates/report_template.jinja2] and @[backend_v2/services/pdf_generator.py], render inline short-circuit blocker badges (`short_circuited_by_claims`) on matrix summary table rows and Toulmin rebuttal links (`falsified_warrant_claims`) on causal graph sections.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Ensure every SDUI field added in Step 3.1 is rendered deterministically in `report_template.jinja2`.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/pdf_generator.py --test --ast-strict</audit_command>
  </step>

  <step id="3.3" name="Flutter Freezed SDUI DTO &amp; Widget Synchronization">
    <action>In @[client_app_v2/lib/shared/models/sdui_block_dto.dart] and @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart], add `@JsonKey(name: 'short_circuited_by_claims') @Default(&lt;String&gt;[]) List&lt;String&gt; shortCircuitedByClaims` and `@JsonKey(name: 'falsified_warrant_claims') @Default(&lt;String&gt;[]) List&lt;String&gt; falsifiedWarrantClaims` to the corresponding Freezed models with 1:1 Backend DTO parity.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart] and @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart], render inline short-circuit blocker chips and Toulmin falsification badges using `Theme.of(context).textTheme`, `Theme.of(context).colorScheme`, and `AppSpacing` tokens, wrapped in `Flexible` / `Expanded` with `TextOverflow.ellipsis`.</action>
    <action>In @[client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart], add widget tests verifying rendering of `shortCircuitedByClaims` and `falsifiedWarrantClaims` badges and strict JSON deserialization.</action>
    <constraint invariant="design_token_absolute_rule">Zero hardcoded `TextStyle`, `Colors.*`, or numeric `SizedBox` dimensions in Flutter widgets; verify with `scripts/audit_flutter_theme_sovereignty.py`.</constraint>
    <audit_command>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</audit_command>
    <audit_command>uv run python scripts/audit_flutter_theme_sovereignty.py</audit_command>
  </step>

  <test_contracts>
    <test name="test_matrix_summary_table_adapter_populates_short_circuited_by_claims" category="positive">
      <input>ReportDataDTO containing matrix row with short_circuited_by_claims=["Prerequisite Claim A: Failed verification"]</input>
      <expected>SduiMatrixSummaryTableBlock row item contains short_circuited_by_claims=["Prerequisite Claim A: Failed verification"]</expected>
    </test>
    <test name="test_causal_graph_adapter_populates_falsified_warrant_claims" category="positive">
      <input>CausalTdaFusionResultDTO containing FalsifiedClaimMatch(rebuttal_claim="Rebuttal R1", invalidated_warrant="Warrant W1", falsified_claim="Claim C1")</input>
      <expected>SduiCausalGraphBlock node metadata contains formatted falsified_warrant_claims entry linking R1 -> W1 -> C1</expected>
    </test>
    <test name="test_sdui_mapper_service_empty_short_circuits_produces_empty_list" category="boundary">
      <input>ReportDataDTO with zero N_A atoms and zero falsified claims</input>
      <expected>short_circuited_by_claims=[] and falsified_warrant_claims=[] on SDUI blocks without bottom-of-report SduiNACard orphans</expected>
    </test>
    <test name="test_sdui_matrix_row_extra_field_raises_validation_error" category="negative">
      <input>SduiMatrixSummaryTableBlock row instantiated with unrecognized field key</input>
      <expected>Raises pydantic.ValidationError (extra="forbid")</expected>
    </test>
    <test name="test_flutter_sdui_matrix_table_widget_renders_short_circuit_badge" category="positive">
      <input>SduiMatrixSummaryTableBlock fixture with shortCircuitedByClaims=["Blocked by Parent Claim"]</input>
      <expected>Widget tree displays "Blocked by Parent Claim" badge with zero layout overflow</expected>
    </test>
    <test name="test_flutter_sdui_block_dto_rejects_invalid_type_on_short_circuited_by_claims" category="error_path">
      <input>JSON payload with short_circuited_by_claims: 12345 (integer instead of List&lt;String&gt;)</input>
      <expected>Throws TypeError / CheckedFromJsonException during Freezed deserialization</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run backend SDUI and PDF unit tests: `uv run pytest backend_v2/tests/unit/services/sdui/test_sdui_mapper_service.py backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <action>Run Phase 3 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/report_data.py backend_v2/models/view/sdui.py backend_v2/services/blueprint.py backend_v2/services/pdf_generator.py backend_v2/services/sdui/ --test --ast-strict`.</action>
    <action>Run Phase 3 Flutter quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_flutter_theme_sovereignty.py`.</action>
  </validation_gate>
</execution_protocol>

