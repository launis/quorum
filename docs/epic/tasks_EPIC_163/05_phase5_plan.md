<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# EPIC 163 - Phase 5: Frontend Flutter `DGR005` Open-JSON DTO & UI Consumer Eradication

## 1. Executive Summary & Architectural Directives

This phase replaces all `Map<String, Object?>` fields and consumers across the 13 Freezed DTO files (Group 2) and 23 UI/controller/widget files (Group 3) in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`, shrinking `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]` from 45 files to exclusively the 9 pure HTTP/SSE/Dio transport boundary files.

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]`, `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]`, `@[client_app_v2/lib/features/execution/models/execution_metadata.dart]`, `@[client_app_v2/lib/features/execution/models/execution_record.dart]`, `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]`, `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]`, `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]`, `@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`, `@[client_app_v2/lib/features/studio/models/step_simulation.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]`, `@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]`, `@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]` | Declaring `Map<String, Object?>` fields on 13 Group 2 Freezed DTO model files (`DGR005`). | Replace all `Map<String, Object?>` fields across the 13 Freezed DTO models with closed Freezed classes enforcing `@JsonSerializable(disallowUnrecognizedKeys: true)` in 1:1 parity with backend Pydantic V2 DTOs. | Zero untyped map properties on Execution or Studio Freezed models. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build` |
| `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`, `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`, `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]`, `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`, `@[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]`, `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]`, `@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]`, `@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]`, `@[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]` | Passing, cloning, or indexing `Map<String, Object?>` in Execution and Studio controllers, utilities, and views (`DGR005`). | Refactor Execution and Studio controllers, cloner utilities, and views to construct and read strongly typed Freezed DTO instances directly. | Zero manual dictionary cloning or raw key lookup in Studio and Execution views. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build` |
| `@[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]`, `@[client_app_v2/lib/shared/widgets/comparison_matrix.dart]`, `@[client_app_v2/lib/shared/widgets/dynamic_form.dart]`, `@[client_app_v2/lib/shared/widgets/generic_grid.dart]`, `@[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]`, `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`, `@[client_app_v2/lib/shared/widgets/schema_mapper.dart]`, `@[client_app_v2/lib/shared/widgets/score_card_radar.dart]`, `@[client_app_v2/lib/shared/widgets/specialist_section.dart]`, `@[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]`, `@[client_app_v2/lib/shared/widgets/workflow_selector.dart]`, `@[scripts/_dart_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]` | Consuming `Map<String, Object?>` widget parameters across 11 shared widgets and exempting 36 DTO/UI files in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`. | Bind all 11 shared widgets to strongly typed Freezed models and remove all 36 Group 2 and Group 3 paths from `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]`. | Retain exclusively the 9 Group 1 HTTP/SSE/Dio transport boundary files in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_dart_guardrails.py --test --ast-strict` |

---

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify 1:1 Cross-Domain DTO &amp; SDUI Semantic Parity (`sdui_contract_fracture_prevention` and `anti_semantic_drift_renaming`) between backend Pydantic V2 DTOs and the 13 Group 2 Flutter Freezed models before running `build_runner`.</action>
  </step>

  <dod_checklist>
    <item>All 13 Group 2 Freezed DTO model files replace `Map<String, Object?>` fields with typed Freezed models (`@JsonSerializable(disallowUnrecognizedKeys: true)`).</item>
    <item>All 23 Group 3 Flutter controller, view, and widget files consume typed Freezed DTO properties with zero `Map<String, Object?>` references.</item>
    <item>`DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]` contains exclusively the 9 Group 1 transport boundary files.</item>
  </dod_checklist>

  <anti_targets>
    <file>@[backend_v2/seed/seed_data.json]</file>
    <file>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]</file>
  </anti_targets>

  <touched_artifacts>
    <file>@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]</file>
    <file>@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]</file>
    <file>@[client_app_v2/lib/features/execution/models/execution_metadata.dart]</file>
    <file>@[client_app_v2/lib/features/execution/models/execution_record.dart]</file>
    <file>@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]</file>
    <file>@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]</file>
    <file>@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]</file>
    <file>@[client_app_v2/lib/features/studio/models/model_config.dart]</file>
    <file>@[client_app_v2/lib/features/studio/models/prompt_block.dart]</file>
    <file>@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]</file>
    <file>@[client_app_v2/lib/features/studio/models/step_simulation.dart]</file>
    <file>@[client_app_v2/lib/features/studio/models/workflow.dart]</file>
    <file>@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]</file>
    <file>@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]</file>
    <file>@[client_app_v2/lib/features/execution/views/dashboard_view.dart]</file>
    <file>@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]</file>
    <file>@[client_app_v2/lib/features/execution/views/new_execution_view.dart]</file>
    <file>@[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]</file>
    <file>@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]</file>
    <file>@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]</file>
    <file>@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]</file>
    <file>@[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]</file>
    <file>@[client_app_v2/lib/features/studio/views/model_registry_view.dart]</file>
    <file>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</file>
    <file>@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/comparison_matrix.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/dynamic_form.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/generic_grid.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/result_dashboard.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/schema_mapper.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/score_card_radar.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/specialist_section.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]</file>
    <file>@[client_app_v2/lib/shared/widgets/workflow_selector.dart]</file>
    <file>@[scripts/_dart_guardrails.py]</file>
    <file>@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]</file>
    <file>@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]</file>
    <file>@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]</file>
  </touched_artifacts>

  <step id="5.1" name="Migrate Group 2 Execution &amp; Studio Freezed DTO Models">
    <context>
      13 Freezed DTO model files in `client_app_v2/lib/features/execution/models/` and `client_app_v2/lib/features/studio/models/` contain `Map<String, Object?>` fields exempted in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`.
    </context>
    <demolish>
      Remove `Map<String, Object?>` fields from all 13 Group 2 Freezed model files.
    </demolish>
    <action>
      1. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]`: Replace `Map<String, Object?>` fields with strongly typed Freezed DTOs.
      2. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]`: Replace `Map<String, Object?>` fields with typed input DTOs.
      3. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_metadata.dart]`: Replace `Map<String, Object?>` fields with typed metadata Freezed classes.
      4. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_record.dart]`: Replace `Map<String, Object?>` fields with typed Freezed step state and synthesis models.
      5. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]`: Replace `Map<String, Object?>` fields with typed snapshot Freezed models.
      6. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]`: Replace `Map<String, Object?>` fields with typed report data Freezed models.
      7. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]`: Replace `Map<String, Object?>` fields with typed workflow input Freezed classes.
      8. `[MODIFY]` `@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`, `@[client_app_v2/lib/features/studio/models/step_simulation.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, and `@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]`: Replace `Map<String, Object?>` fields with strongly typed Studio Freezed DTOs.
      9. `[MODIFY]` `@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]` and `@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]`: Update and expand unit tests for the strongly typed Freezed models.
    </action>
    <constraint>
      Never manually edit `.freezed.dart` or `.g.dart` files (`ignore_generated`); run code generation via `flutter_audit_loop.py --build`.
    </constraint>
    <test_contracts>
      <contract name="test_execution_record_and_report_dto_deserialize_typed_models" category="positive">
        <input>Canonical JSON payload matching backend `ExecutionRecord` and `ReportDataV2` schemas.</input>
        <expected>Deserializes into strongly typed Freezed instances with zero `Map&lt;String, Object?&gt;` fields.</expected>
      </contract>
      <contract name="test_freezed_models_reject_unrecognized_json_keys" category="negative">
        <input>JSON payload containing an unrecognized key on `ExecutionRecord` or `FrozenContextSnapshot`.</input>
        <expected>Throws `UnrecognizedKeysException` (`disallowUnrecognizedKeys: true`).</expected>
      </contract>
      <contract name="test_workflow_and_prompt_block_simulation_empty_and_populated_states" category="boundary">
        <input>Simulation response payloads with 0 items and multiple items.</input>
        <expected>Roundtrips cleanly through `fromJson` and `toJson`.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/unit/features/execution/models/ --build`
    </validation_gate>
  </step>

  <step id="5.2" name="Migrate Group 3 Execution &amp; Studio Controllers, Utilities &amp; Views">
    <context>
      12 Execution and Studio controller, utility, and view files in `client_app_v2/lib/features/` consume or pass `Map<String, Object?>`.
    </context>
    <demolish>
      Remove all `Map<String, Object?>` type annotations, parameters, and map indexing across the 12 Execution and Studio feature files.
    </demolish>
    <action>
      1. `[MODIFY]` `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`, `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`, `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]`, and `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`: Consume typed Execution Freezed DTOs directly.
      2. `[MODIFY]` `@[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]`, `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]`, `@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]`, and `@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]`: Operate exclusively on typed Studio Freezed models (`copyWith`) without `Map<String, Object?>`.
      3. `[MODIFY]` `@[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]`, and `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]`: Render typed Studio Freezed DTO properties directly.
    </action>
    <constraint>
      Enforce Dart 3 `switch` pattern matching (`freezed_when_ban`) and preserve `context.mounted` guards after every `await` (`async_build_context_mounted_ban`).
    </constraint>
    <test_contracts>
      <contract name="test_workflow_cloner_preserves_typed_freezed_structure" category="positive">
        <input>Valid `Workflow` Freezed instance passed to `WorkflowCloner`.</input>
        <expected>Produces a cloned `Workflow` with a fresh 32-hex UUIDv7 ID and preserved typed step configurations without map conversion.</expected>
      </contract>
      <contract name="test_mcp_tool_params_panel_handles_missing_optional_schema_properties" category="negative">
        <input>`MCPToolInputSchemaDTO` with empty required list and null optional descriptions.</input>
        <expected>Renders typed parameter rows cleanly without fallback string literals.</expected>
      </contract>
      <contract name="test_dynamic_start_screen_validates_required_workflow_inputs" category="boundary">
        <input>`Workflow` with 0 required inputs and 5 required typed `ExpectedInput` definitions.</input>
        <expected>Constructs typed `ExecutionCreateRequestDto` payload matching input constraints.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
    </validation_gate>
  </step>

  <step id="5.3" name="Migrate Group 3 Shared Widgets &amp; Shrink DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES to 9 Transport Files">
    <context>
      11 shared widgets in `client_app_v2/lib/shared/widgets/` accept `Map<String, Object?>` parameters, and `@[scripts/_dart_guardrails.py]` lists 45 files in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`.
    </context>
    <demolish>
      Remove `Map<String, Object?>` from all 11 shared widgets and delete all 36 Group 2 and Group 3 entries from `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]`, `@[client_app_v2/lib/shared/widgets/comparison_matrix.dart]`, `@[client_app_v2/lib/shared/widgets/dynamic_form.dart]`, `@[client_app_v2/lib/shared/widgets/generic_grid.dart]`, `@[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]`, `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`, `@[client_app_v2/lib/shared/widgets/schema_mapper.dart]`, `@[client_app_v2/lib/shared/widgets/score_card_radar.dart]`, `@[client_app_v2/lib/shared/widgets/specialist_section.dart]`, `@[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]`, and `@[client_app_v2/lib/shared/widgets/workflow_selector.dart]`: Replace `Map<String, Object?>` widget fields and parameters with strongly typed Freezed models.
      2. `[MODIFY]` `@[scripts/_dart_guardrails.py]`: Remove all 36 Group 2 and Group 3 paths from `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`, retaining only the 9 Group 1 transport boundary files (`execution_client.dart`, `reports_client.dart`, `sse_client.dart`, `studio_client.dart`, `workflow_client.dart`, `app_exception.dart`, `error_interceptor.dart`, `auth_repository.dart`, `user_repository.dart`).
      3. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]`: Assert that `len(DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES) == 9` and that `DGR005` passes with 0 violations across `client_app_v2/lib/`.
    </action>
    <constraint>
      Never use `SizedBox.shrink()` (`sized_box_shrink_ban`) or hardcoded layout numbers (`design_token_absolute_rule`) when updating shared widgets.
    </constraint>
    <test_contracts>
      <contract name="test_dgr005_exempt_set_contains_only_nine_transport_boundary_files" category="positive">
        <input>Inspect `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]` and run `check_dart_files` across `client_app_v2/lib/`.</input>
        <expected>`len(DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES) == 9` and `DGR005` reports 0 violations.</expected>
      </contract>
      <contract name="test_dgr005_rejects_map_string_object_in_dto_or_widget_file" category="negative">
        <input>Synthetic Dart source containing `final Map&lt;String, Object?&gt; payload;` in `lib/features/execution/models/execution_record.dart` or `lib/shared/widgets/result_dashboard.dart`.</input>
        <expected>`DGR005` reports a fatal violation.</expected>
      </contract>
      <contract name="test_dgr005_permits_json_decode_map_at_transport_client_boundary" category="boundary">
        <input>Transport client file in the 9-file Group 1 boundary set deserializing Dio response JSON into a Freezed `fromJson` factory.</input>
        <expected>Passes `DGR005` without violation.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_dart_guardrails.py --test --ast-strict; uv run --no-sync --offline python scripts/audit_dto_parity.py; uv run --no-sync --offline pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
    </validation_gate>
  </step>
</execution_protocol>
```
