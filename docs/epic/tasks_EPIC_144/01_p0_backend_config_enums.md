# Phase 0-A: Backend Config, Enums & Settings

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 1 "Backend Config & Enums" (L273-L288)
**Scope:** Backend Python only

**Overview:** Centralize authenticity thresholds in `settings.py`, define `DisplayScale(StrEnum)` in `enums.py`, and establish cross-language enum parity testing.

**Target Files:**
- `[MODIFY]` `@[backend_v2/settings.py]`
- `[MODIFY]` `@[backend_v2/models/enums.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_settings.py]`
- `[NEW]` `@[backend_v2/tests/unit/test_enum_parity.py]`

**Context Files (Read-Only):**
- `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]` — contains `AUTHENTICITY_THRESHOLDS = {"high": 80.0, "low": 50.0}` at L51 (to be migrated in Phase 3)
- `@[client_app_v2/lib/core/models/enums.dart]` — Dart enum file for parity verification

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: This is the first phase. Verify the Epic SSOT at @[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md] is unchanged.</action>
    <action>Look forward: Verify that @[backend_v2/settings.py] does NOT already contain `authenticity_threshold_high` and that @[backend_v2/models/enums.py] does NOT already contain `DisplayScale`.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/models/v2_core.py — Do NOT modify domain models yet (Plan 03)</file>
    <file>backend_v2/models/dtos/output_profile.py — Do NOT modify DTOs yet (Plan 03)</file>
    <file>backend_v2/seed/seed_data.json — Do NOT touch seed data yet (Plan 02)</file>
    <file>backend_v2/services/sdui/adapters/authenticity_adapter.py — Do NOT migrate thresholds yet (Phase 3)</file>
    <file>client_app_v2/ — Do NOT touch any Flutter files (Plans 07-08)</file>
  </anti_targets>

  <dod_checklist>
    <item>DisplayScale(StrEnum) defined in @[backend_v2/models/enums.py] with values ORIGINAL, CUSTOM, NORMALIZED_100 and @property l10n_key.</item>
    <item>settings.py contains authenticity_threshold_high (default=80.0, ge=0.0, le=100.0) and authenticity_threshold_low (default=50.0, ge=0.0, le=100.0) with @model_validator(mode="after") enforcing high >= low.</item>
    <item>test_settings.py has boundary tests for thresholds: ge=0.0 (testing -0.1 fails), le=100.0 (testing 100.1 fails), inversion failure (high=40.0, low=70.0 fails), and env var overrides.</item>
    <item>test_enum_parity.py mathematically verifies 1:1 cross-language parity between Python enums.py and Dart enums.dart for all shared enums.</item>
  </dod_checklist>

  <step id="1" name="ADD DisplayScale ENUM TO enums.py">
    <action>In @[backend_v2/models/enums.py], define:
```python
class DisplayScale(StrEnum):
    """Display scale configuration for matrix score rendering."""

    ORIGINAL = "original"
    CUSTOM = "custom"
    NORMALIZED_100 = "normalized_100"

    @property
    def l10n_key(self) -> str:
        """Localization key for UI label resolution."""
        return f"display_scale_{self.value}"
```
Place it after the existing `PresetView` enum class (near L60-80 area).</action>
    <constraint invariant="strict_enum_hydration_and_validation">DisplayScale MUST be a StrEnum, NOT a plain string Literal. This enables strict Pydantic V2 enum validation.</constraint>
    <constraint invariant="strict_enum_l10n_adapter">The l10n_key property MUST use the f"display_scale_{self.value}" pattern. NO magic string manipulation (.lower(), .split('_')) permitted.</constraint>
  </step>

  <step id="2" name="ADD AUTHENTICITY THRESHOLDS TO settings.py">
    <action>In @[backend_v2/settings.py], add two new fields to the Settings class:
```python
authenticity_threshold_high: Annotated[float, Field(
    default=80.0, ge=0.0, le=100.0,
    description="Minimum score required for HIGH authenticity level classification",
)] = 80.0

authenticity_threshold_low: Annotated[float, Field(
    default=50.0, ge=0.0, le=100.0,
    description="Minimum score required for MEDIUM authenticity level classification",
)] = 50.0
```
Add a `@model_validator(mode="after")` to enforce `authenticity_threshold_high >= authenticity_threshold_low`:
```python
@model_validator(mode="after")
def validate_authenticity_thresholds(self) -> "Settings":
    """Enforce cross-field consistency: high threshold must be >= low threshold."""
    if self.authenticity_threshold_high < self.authenticity_threshold_low:
        msg = (
            f"authenticity_threshold_high ({self.authenticity_threshold_high}) "
            f"must be >= authenticity_threshold_low ({self.authenticity_threshold_low})"
        )
        raise ValueError(msg)
    return self
```</action>
    <constraint invariant="global_config_sovereignty_mandate">All backend evaluation thresholds MUST be centralized in settings.py. Zero hardcoded thresholds in adapters.</constraint>
    <constraint invariant="settings_fail_fast_validation_gate">Cross-field consistency MUST be enforced via @model_validator.</constraint>
  </step>

  <step id="3" name="ADD BOUNDARY TESTS TO test_settings.py">
    <action>In @[backend_v2/tests/unit/test_settings.py], add the following tests for authenticity thresholds.</action>
    <test_contracts>
      <test name="test_authenticity_threshold_high_below_minimum_raises" category="boundary">
        <input>Settings(authenticity_threshold_high=-0.1)</input>
        <expected>raises pydantic.ValidationError (ge=0.0 violated)</expected>
      </test>
      <test name="test_authenticity_threshold_high_above_maximum_raises" category="boundary">
        <input>Settings(authenticity_threshold_high=100.1)</input>
        <expected>raises pydantic.ValidationError (le=100.0 violated)</expected>
      </test>
      <test name="test_authenticity_threshold_low_below_minimum_raises" category="boundary">
        <input>Settings(authenticity_threshold_low=-0.1)</input>
        <expected>raises pydantic.ValidationError (ge=0.0 violated)</expected>
      </test>
      <test name="test_authenticity_threshold_low_above_maximum_raises" category="boundary">
        <input>Settings(authenticity_threshold_low=100.1)</input>
        <expected>raises pydantic.ValidationError (le=100.0 violated)</expected>
      </test>
      <test name="test_authenticity_threshold_inversion_raises" category="negative">
        <input>Settings(authenticity_threshold_high=40.0, authenticity_threshold_low=70.0)</input>
        <expected>raises ValueError via @model_validator ("must be >= ")</expected>
      </test>
      <test name="test_authenticity_threshold_equal_values_valid" category="boundary">
        <input>Settings(authenticity_threshold_high=60.0, authenticity_threshold_low=60.0)</input>
        <expected>passes validation (high == low is allowed)</expected>
      </test>
      <test name="test_authenticity_threshold_env_override" category="positive">
        <input>monkeypatch env AUTHENTICITY_THRESHOLD_HIGH=90.0, AUTHENTICITY_THRESHOLD_LOW=60.0</input>
        <expected>Settings resolves with overridden values 90.0 and 60.0</expected>
      </test>
    </test_contracts>
  </step>

  <step id="4" name="CREATE CROSS-LANGUAGE ENUM PARITY TEST">
    <action>Create [NEW] @[backend_v2/tests/unit/test_enum_parity.py]. This test MUST automatically verify 1:1 cross-language enum parity via AST/regex parsing between Python @[backend_v2/models/enums.py] and Dart @[client_app_v2/lib/core/models/enums.dart] for all shared enums.

The test MUST:
1. Parse Python enums using `ast.parse()` to extract StrEnum class names and member values.
2. Parse Dart enums using regex to extract `@JsonValue('...')` annotations from matching enum definitions.
3. Assert that for each shared enum (specifically and exhaustively: `DisplayScale`, `TargetBlockType`, `PresetView`, `TextDeliveryMode`, `ScoringStrategy`, `HistoricalContextMode`, `XaiExtensionType`), the set of Python member values equals the set of Dart @JsonValue strings.

NOTE: This test will initially FAIL for `DisplayScale` (not yet in Dart) and `TargetBlockType` (Dart has 9 vs Python's 13). Mark these specific assertions as `pytest.mark.skip(reason="Awaiting Plan 07: Frontend Enum Sync")` until Plan 07 is executed. All other shared enums MUST pass immediately.</action>
    <constraint invariant="cross_language_enum_parity_gate">Enum parity between Python and Dart MUST be mathematically verified via automated testing.</constraint>
    <test_contracts>
      <test name="test_preset_view_parity" category="positive">
        <input>Python PresetView members vs Dart PresetView @JsonValue members</input>
        <expected>Sets are equal</expected>
      </test>
      <test name="test_scoring_strategy_parity" category="positive">
        <input>Python ScoringStrategy members vs Dart ScoringStrategy @JsonValue members</input>
        <expected>Sets are equal</expected>
      </test>
      <test name="test_display_scale_parity" category="positive">
        <input>Python DisplayScale members vs Dart DisplayScale @JsonValue members</input>
        <expected>pytest.mark.skip — Dart enum not yet created (Plan 07)</expected>
      </test>
      <test name="test_target_block_type_parity" category="positive">
        <input>Python TargetBlockType (13 members) vs Dart TargetBlockType (9 members)</input>
        <expected>pytest.mark.skip — Dart missing 4 members (Plan 07)</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_settings.py --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test</check>
    <check>grep_search for "class DisplayScale" in @[backend_v2/models/enums.py] — MUST find exactly 1 match</check>
    <check>grep_search for "authenticity_threshold_high" in @[backend_v2/settings.py] — MUST find exactly 1 field definition</check>
    <check>grep_search for "authenticity_threshold_low" in @[backend_v2/settings.py] — MUST find exactly 1 field definition</check>
    <check>grep_search for "model_validator" in @[backend_v2/settings.py] — MUST find the cross-field validator</check>
  </validation_gate>
</execution_protocol>
```
