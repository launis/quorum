# Phase 0: Atomic Data, Mock Fixture & Code Generation Gate (Pre-requisite)

**Overview:** Establish the structural data and contract foundation before any Studio UI refactoring begins. Enforce `extra="forbid"` JSON deserialization, 1:1 cross-language enum parity, centralized settings thresholds, and complete eradication of legacy fallback mechanisms.
**Target Files:**
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_settings.py]
- `[MODIFY]` @[backend_v2/models/enums.py]
- `[NEW]` @[backend_v2/tests/unit/test_enum_parity.py]
- `[MODIFY]` @[client_app_v2/lib/core/models/enums.dart]
- `[MODIFY]` @[backend_v2/seed/seed_data.json]
- `[MODIFY]` @[backend_v2/models/v2_core.py]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/output_profile.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/blueprint_config.dart]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_output_profile.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_v2_core_models.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]
- `[MODIFY]` @[client_app_v2/test/features/studio/models/output_profile_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart]
- `[NEW]` @[client_app_v2/test/features/studio/models/blueprint_config_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics (EPIC 141, EPIC 142, EPIC 143). Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/models/v2_core.py], @[backend_v2/models/dtos/output_profile.py], @[client_app_v2/lib/core/models/enums.dart], and @[client_app_v2/lib/features/studio/models/output_profile.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_144_Output_Profile_Studio_UI_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Master seed data in @[backend_v2/seed/seed_data.json] sanitized (valid enum keys, bilingual metric_mappings, zero include_diagnostic_scorecard keys) and local database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
    - [ ] Authenticity thresholds centralized in @[backend_v2/settings.py] (`authenticity_threshold_high: float = 80.0`, `authenticity_threshold_low: float = 50.0`) with `@model_validator(mode="after")` enforcing `high >= low`.
    - [ ] DisplayScale(StrEnum) defined in @[backend_v2/models/enums.py] (`ORIGINAL = "original"`, `CUSTOM = "custom"`, `NORMALIZED_100 = "normalized_100"`) and @JsonEnum() DisplayScale in @[client_app_v2/lib/core/models/enums.dart] (`@JsonValue('normalized_100')`).
    - [ ] Missing 4 TargetBlockType enum members added to @[client_app_v2/lib/core/models/enums.dart] (`matrixGraphsBlock: 'matrix_graphs_block'`, `matrixSummaryTableBlock: 'matrix_summary_table_block'`, `varianceValidationBlock: 'variance_validation_block'`, `authenticityEvaluationBlock: 'authenticity_evaluation_block'`).
    - [ ] SystemUiConstraints enum defined in @[client_app_v2/lib/core/models/enums.dart] (`maxExtensionItemsSliderMin: 1`, `maxExtensionItemsSliderMax: 20`, `maxExtensionItemsAbsoluteMax: 100`, `maxExtensionItemsDefault: 3`).
    - [ ] Automated enum parity tests implemented in `[NEW]` @[backend_v2/tests/unit/test_enum_parity.py] verifying 1:1 parity between Python `enums.py` and Dart `enums.dart`.
    - [ ] `include_diagnostic_scorecard` completely removed from @[backend_v2/models/v2_core.py], @[backend_v2/models/dtos/output_profile.py], and @[client_app_v2/lib/features/studio/models/output_profile.dart].
    - [ ] `target_block_order` strictly typed as `list[TargetBlockType]` (Python) and `List<TargetBlockType>` (Dart) across domain models and DTOs.
    - [ ] `max_extension_items` non-nullable `Annotated[int, Field(default=3, ge=1, le=100)]` in OutputProfileCreateDTO / OutputProfileResponseDTO and `@Default(3) int maxExtensionItems` in Dart Freezed model.
    - [ ] ALL `unknownEnumValue` fallback parameters removed from @[client_app_v2/lib/features/studio/models/output_profile.dart] and @[client_app_v2/lib/features/studio/models/blueprint_config.dart].
    - [ ] OpenAPI specification synchronized via `uv run python backend_v2/scripts/generate_openapi.py` and Freezed models generated via `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.
    - [ ] All mock fixtures and unit tests updated across backend and frontend test suites.
  </dod_checklist>

  <required_context_rules>
    - @[.agents/rules/00-antigravity-core.md]
    - @[.agents/rules/01-python-backend.md]
    - @[.agents/rules/02_flutter_desktop.md]
    - @[.agents/rules/03_seed_vault.md]
    - @[.agents/rules/04_directory_reference.md]
    - @[.agents/rules/05_llm_architecture.md]
    - @[ki_god_code_prevention.md]
    - @[ki_sdui_adapter_pattern.md]
    - @[ki_tripartite_pipeline_architecture.md]
    - @[ki_dual_axis_localization_architecture.md]
    - @[ki_strict_sdui_serialization.md]
    - @[ki_flat_polymorphic_pipeline.md]
    - @[ki_sdui_matrix_synthesis.md]
    - @[ki_global_config_sovereignty.md]
    - @[ki_ai_testing_standards.md]
    - @[ki_ast_guardrail_testing.md]
    - @[ki_python_314_concurrency_strictness.md]
    - @[ki_epic_lifecycle_workflow.md]
    - @[ki_synthesis_payload_compression.md]
    - @[ki_dag_engine_dto_projection_rules.md]
    - @[ki_matrix_boolean_evaluation_strictness.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT modify Flutter view widgets or tab components in Phase 0.
    - Do NOT relax Pydantic validation to `extra="ignore"` or inject `.pop()` duct-tape in repository layers.
    - Do NOT leave `unknownEnumValue` fallback parameters in Freezed models.
    - Do NOT keep raw strings for `target_block_order` or `display_scale`.
  </anti_targets>

  <step id="1" name="Master Seed Sanitization & Local Database Reseed">
    <action>In @[backend_v2/seed/seed_data.json], sanitize the `output_profiles` collection:
1. Ensure all profiles (specifically `prf_5d6e7f8091a2b3c4`) have `display_scale` set to valid enum strings (`normalized_100`, `custom`, `original`).
2. Ensure `target_block_order` contains exclusively valid `TargetBlockType` string values.
3. Ensure all `metric_mappings` are complete and bilingual (specifically: `metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`).
4. Completely eliminate all occurrences of `include_diagnostic_scorecard`.
    </action>
    <action>Execute local environment database re-seeding via `uv run python backend_v2/seed/run_seed.py local` to establish a clean, validated local TinyDB state prior to modifying backend Pydantic models.</action>
    <constraint invariant="seed_data_vault_protocol">Follow vault mutation protocol: backup seed data before modifying, run json integrity check, verify via audit script, and execute reseed.</constraint>
  </step>

  <step id="2" name="Backend Config & Settings Centralization">
    <action>In @[backend_v2/settings.py], add centralized authenticity threshold settings:
```python
authenticity_threshold_high: Annotated[
    float,
    Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="Minimum score required for HIGH authenticity level classification",
    ),
] = 80.0
authenticity_threshold_low: Annotated[
    float,
    Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Minimum score required for MEDIUM authenticity level classification",
    ),
] = 50.0

@model_validator(mode="after")
def validate_authenticity_thresholds(self) -> Self:
    """Validate that high threshold is greater than or equal to low threshold."""
    if self.authenticity_threshold_high < self.authenticity_threshold_low:
        raise ValueError(
            f"authenticity_threshold_high ({self.authenticity_threshold_high}) "
            f"must be >= authenticity_threshold_low ({self.authenticity_threshold_low})"
        )
    return self
```
    </action>
    <action>In @[backend_v2/tests/unit/test_settings.py], add boundary and validation tests for the new thresholds.</action>
    <test_contracts>
      <test name="test_settings_authenticity_thresholds_valid_defaults" category="positive">
        <input>Settings() default instantiation</input>
        <expected>authenticity_threshold_high == 80.0, authenticity_threshold_low == 50.0</expected>
      </test>
      <test name="test_settings_authenticity_thresholds_out_of_bounds_high" category="boundary">
        <input>Settings(authenticity_threshold_high=100.1)</input>
        <expected>raises pydantic.ValidationError</expected>
      </test>
      <test name="test_settings_authenticity_thresholds_out_of_bounds_low" category="boundary">
        <input>Settings(authenticity_threshold_low=-0.1)</input>
        <expected>raises pydantic.ValidationError</expected>
      </test>
      <test name="test_settings_authenticity_thresholds_inverted_raises_validation_error" category="error_path">
        <input>Settings(authenticity_threshold_high=40.0, authenticity_threshold_low=70.0)</input>
        <expected>raises pydantic.ValidationError</expected>
      </test>
    </test_contracts>
  </step>

  <step id="3" name="Backend Enums & Parity Test">
    <action>In @[backend_v2/models/enums.py], define `DisplayScale(StrEnum)`:
```python
class DisplayScale(StrEnum):
    """UI rendering display scale modes."""

    ORIGINAL = "original"
    CUSTOM = "custom"
    NORMALIZED_100 = "normalized_100"

    @property
    def l10n_key(self) -> str:
        """Get the localized ARB key for this display scale."""
        match self:
            case DisplayScale.ORIGINAL:
                return "displayScaleOriginal"
            case DisplayScale.CUSTOM:
                return "displayScaleCustom"
            case DisplayScale.NORMALIZED_100:
                return "displayScaleNormalized100"
```
    </action>
    <action>In `[NEW]` @[backend_v2/tests/unit/test_enum_parity.py], implement automated cross-language enum parity verification asserting that Python `enums.py` and Dart `enums.dart` share 1:1 identical enum members and `@JsonValue` mappings for `DisplayScale`, `TargetBlockType`, `PresetView`, `TextDeliveryMode`, `ScoringStrategy`, `HistoricalContextMode`, and `XaiExtensionType`.</action>
    <test_contracts>
      <test name="test_display_scale_enum_parity" category="positive">
        <input>Python DisplayScale vs Dart DisplayScale</input>
        <expected>All values (original, custom, normalized_100) match 1:1 with correct @JsonValue</expected>
      </test>
      <test name="test_target_block_type_enum_parity" category="positive">
        <input>Python TargetBlockType (13 members) vs Dart TargetBlockType</input>
        <expected>All 13 values match 1:1 with correct @JsonValue</expected>
      </test>
    </test_contracts>
  </step>

  <step id="4" name="Frontend Enums Synchronization">
    <action>In @[client_app_v2/lib/core/models/enums.dart]:
1. Define `@JsonEnum() enum DisplayScale`:
```dart
enum DisplayScale {
  @JsonValue('original')
  original,
  @JsonValue('custom')
  custom,
  @JsonValue('normalized_100')
  normalized100,
}
```
2. Add missing 4 `TargetBlockType` members:
```dart
  @JsonValue('matrix_graphs_block')
  matrixGraphsBlock,
  @JsonValue('matrix_summary_table_block')
  matrixSummaryTableBlock,
  @JsonValue('variance_validation_block')
  varianceValidationBlock,
  @JsonValue('authenticity_evaluation_block')
  authenticityEvaluationBlock,
```
3. Define `SystemUiConstraints` enum:
```dart
enum SystemUiConstraints {
  maxExtensionItemsSliderMin(1),
  maxExtensionItemsSliderMax(20),
  maxExtensionItemsAbsoluteMax(100),
  maxExtensionItemsDefault(3);

  final int value;
  const SystemUiConstraints(this.value);
}
```
    </action>
    <constraint invariant="centralized_frontend_enums">All systemic client constraints and enums must be centralized in enums.dart.</constraint>
  </step>

  <step id="5" name="Backend Domain Model & DTO Purge">
    <action>In @[backend_v2/models/v2_core.py]:
<demolish>
REMOVE: `include_diagnostic_scorecard: bool = Field(...)` at @[backend_v2/models/v2_core.py].
REPLACE WITH: Exclusively `target_block_order: list[TargetBlockType]` SSOT.
</demolish>
1. Remove `include_diagnostic_scorecard` from `OutputProfile`.
2. Change `display_scale` type from `str` to `DisplayScale = DisplayScale.ORIGINAL`.
3. Change `target_block_order` type from `list[str]` to `list[TargetBlockType]`.
4. Ensure `model_config = ConfigDict(strict=True, extra="forbid")` is enforced on `OutputProfile`, `OutputLayoutBlock`, and `SynthesisConfigDTO`.
    </action>
    <action>In @[backend_v2/models/dtos/output_profile.py]:
<demolish>
REMOVE: `include_diagnostic_scorecard` fields from `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.
REPLACE WITH: Direct `target_block_order: list[TargetBlockType]` validation.
</demolish>
1. Remove `include_diagnostic_scorecard` across all DTOs.
2. Enforce non-nullable `max_extension_items: Annotated[int, Field(default=3, ge=1, le=100)]` on `OutputProfileCreateDTO` and `OutputProfileResponseDTO`.
3. Enforce `max_extension_items: Annotated[int | None, Field(default=None, ge=1, le=100)]` on `OutputProfileUpdateDTO`.
4. Migrate `target_block_order` to `list[TargetBlockType]`.
5. Ensure `model_config = ConfigDict(strict=True, extra="forbid")` is enforced on all DTOs.
    </action>
    <action>Run backend unit models audit: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_v2_core_models.py --test`.</action>
    <test_contracts>
      <test name="test_output_profile_dto_max_extension_items_bounds_validation" category="boundary">
        <input>OutputProfileCreateDTO with max_extension_items=0 or max_extension_items=101</input>
        <expected>raises pydantic.ValidationError</expected>
      </test>
      <test name="test_output_profile_dto_extra_forbidden_fails_fast" category="negative">
        <input>OutputProfileCreateDTO with extra key "include_diagnostic_scorecard"</input>
        <expected>raises pydantic.ValidationError (extra_forbidden)</expected>
      </test>
      <test name="test_output_profile_dto_target_block_order_invalid_type" category="negative">
        <input>OutputProfileCreateDTO with target_block_order=["invalid_block_type"]</input>
        <expected>raises pydantic.ValidationError</expected>
      </test>
    </test_contracts>
  </step>

  <step id="6" name="OpenAPI Specification Synchronization Gate">
    <action>Execute OpenAPI generator: `uv run python backend_v2/scripts/generate_openapi.py`.</action>
    <action>Verify OpenAPI parity test: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test`.</action>
    <constraint invariant="pydantic_namespace_collisions">OpenAPI must match updated DTO schemas before Frontend code generation.</constraint>
  </step>

  <step id="7" name="Frontend Freezed Model Synchronization & Code Generation">
    <action>In @[client_app_v2/lib/features/studio/models/output_profile.dart]:
<demolish>
REMOVE: `@JsonKey(name: 'include_diagnostic_scorecard') bool includeDiagnosticScorecard` from `OutputProfile`.
REMOVE: `unknownEnumValue` fallback parameters from all `@JsonKey` annotations in `OutputProfile` and `OutputLayoutBlock`.
</demolish>
1. Remove `includeDiagnosticScorecard`.
2. Change `displayScale` to `DisplayScale displayScale` with `@Default(DisplayScale.original)`.
3. Change `targetBlockOrder` to `List<TargetBlockType> targetBlockOrder` with `@Default([TargetBlockType.metadataBlock, ...])`.
4. Strictly type `@Default(3) @JsonKey(name: 'max_extension_items') int maxExtensionItems` (eradicating `int? maxExtensionItems`).
5. Remove ALL `unknownEnumValue` fallback parameters across `OutputProfile`, `OutputLayoutBlock`, and `SynthesisConfigDTO`.
    </action>
    <action>In @[client_app_v2/lib/features/studio/models/blueprint_config.dart], eradicate its `unknownEnumValue: PresetView.metrics1d` fallback parameter.</action>
    <action>Execute code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.</action>
    <action>In `[NEW]` @[client_app_v2/test/features/studio/models/blueprint_config_test.dart] and @[client_app_v2/test/features/studio/models/output_profile_test.dart], add negative tests asserting that `CheckedFromJsonException` is thrown on unmapped enum strings or unexpected keys.</action>
  </step>

  <step id="8" name="Mock & Unit Test Fixtures Update Across Blast Radius">
    <action>Synchronously update all mock fixtures across backend and frontend test suites to use the updated typed DTOs and Enums:
- Backend:
  - @[backend_v2/tests/unit/models/dtos/test_output_profile.py]
  - @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
  - @[backend_v2/tests/unit/services/test_blueprint.py]
  - @[backend_v2/tests/unit/hooks/test_scoring.py]
  - @[backend_v2/tests/unit/test_worker_synthesis.py]
  - @[backend_v2/tests/unit/test_v2_core_models.py]
  - @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]
- Frontend:
  - @[client_app_v2/test/features/studio/models/output_profile_test.dart]
  - @[client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart]
  - @[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart]
    </action>
  </step>

  <validation_gate>
    <action>uv run python backend_v2/scripts/generate_openapi.py</action>
    <action>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_settings.py --test</action>
    <action>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test</action>
    <action>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_v2_core_models.py --test</action>
    <action>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/dtos/test_output_profile.py --test</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models/output_profile_test.dart --test</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models/blueprint_config_test.dart --test</action>
  </validation_gate>
</execution_protocol>
```
