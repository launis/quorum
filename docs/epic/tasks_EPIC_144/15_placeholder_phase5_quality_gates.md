# Phase 5: Quality Gates & Anti-Happy-Path Falsification

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Tracker:** `@[docs\epic\EPIC_144_tracker.md]`
**Source:** Epic Phase 5 "Quality Gates & Anti-Happy-Path Falsification" (L631-L672), Step 6 (L261-L264), Definition of Done (L674-L731), Requirements `R73`–`R75`, and Modernity Violations `V1`–`V15`.

---

## 1. Objective & Scope

Execute the comprehensive final Quality Gate sweep and Anti-Happy-Path Falsification for Epic 144 across Backend Python (Pydantic V2 strict schemas, Enum parity, Settings boundary limits, and SDUI Adapter dual-logging) and Frontend Flutter (Dart 3 Freezed strict deserialization, `CheckedFromJsonException` firewall, `SystemUiConstraints` slider clamping, and widget boundary tests), concluding with global audit loops and the mandatory Final Live E2E REST API Verification Gate.

### Target Files (Test & Verification Targets):
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_settings.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_output_profile_models.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_blueprint.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_scoring.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_v2_core_models.py]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/models/output_profile_test.dart]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/models/blueprint_config_test.dart]`
- `[MODIFY]` `@[client_app_v2/test/shared/models/sdui_block_dto_test.dart]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/widgets/profile/blocks/block_card_registry_test.dart]`

---

## 2. Architectural Protocol & Invariants

```xml
<execution_protocol>
  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <rule>@[.agents\rules\03_seed_vault.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <rule>@[.agents\rules\05_llm_architecture.md]</rule>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/services/orchestrator/prompt_compiler.py — Frozen architectural cornerstone, do NOT modify</file>
    <file>backend_v2/seed/seed_data.json — Prompt text and seed definitions are immutable; modify tests/validators instead</file>
    <file>backend_v2/settings.py — Configured in Phase 0 &amp; 3; do NOT alter thresholds without user authorization</file>
  </anti_targets>

  <step id="0" name="Strategic Alignment &amp; Pre-Flight Baseline Audit">
    <action>Verify that Phase 4 is signed off in tracker (`@[docs\epic\EPIC_144_tracker.md]`), git workspace is clean, and the existing test suites pass cleanly.</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2 --test</command>
    <command>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --test</command>
  </step>

  <step id="1" name="Backend Pydantic Strictness &amp; Domain Negative Tests">
    <constraint invariant="the_zero_compromise_pledge">
      Enforce strict Pydantic V2 schemas with ConfigDict(strict=True, extra='forbid'). If an unexpected key is passed or boundary is breached, raise ValidationError and crash Fail-Fast without silent fallbacks.
    </constraint>
    <action>In `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]`, verify and add comprehensive negative boundary tests:
      1. Out-of-bounds `max_extension_items` in `OutputProfileCreateDTO` and `OutputProfileUpdateDTO`: assert `ValidationError` for boundary failure inputs `0`, `-1`, and `101` (`Field(ge=1, le=100)`).
      2. Invalid string for `display_scale`: assert `ValidationError`.
      3. Invalid `target_block_order` block identifiers: assert `ValidationError`.
      4. Legacy field injection (`include_diagnostic_scorecard`): assert `ValidationError` (`extra='forbid'`).
      5. Extra/unrecognized keys inside nested sub-DTOs (`SynthesisConfigDTO`, `OutputLayoutBlock`, `I18nText`): assert `ValidationError`.
    </action>
    <action>In `@[backend_v2/tests/unit/test_output_profile_models.py]`, verify that `OutputProfile` domain model rejects invalid IDs, empty slugs, unmapped `TargetBlockType` values, and unexpected extra attributes under `extra="forbid"`.</action>
    <action>In `@[backend_v2/tests/unit/test_settings.py]`, verify and assert negative boundary tests:
      1. `authenticity_threshold_high` below `0.0` (`-0.1`) and above `100.0` (`100.1`): assert `ValidationError`.
      2. `authenticity_threshold_low` below `0.0` (`-0.1`) and above `100.0` (`100.1`): assert `ValidationError`.
      3. Inversion `high < low` (specifically `high=40.0, low=70.0`): assert `ValidationError` with cross-field validator message.
    </action>
    <action>In `@[backend_v2/tests/unit/test_v2_core_models.py]`, verify that `SynthesisConfigDTO` rejects dead-weight fields (`model_strategy`, `historical_context_mode`, `enable_pii_masking`, `allowed_exports`, `omit_empty_sections`, `allowed_mcp_tools`) with `ValidationError`.</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/dtos/test_output_profile.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_settings.py --test`.</validation>
  </step>

  <step id="2" name="SDUI Adapter Dual-Logging &amp; Fail-Fast Exception Audit">
    <constraint invariant="rfc7807_dual_reporting_mandate">
      Every AppException raised in SDUI presentation adapters MUST be preceded by a structured logger.error call with exc_info=True.
    </constraint>
    <action>In `@[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]`:
      1. Verify negative test `test_metadata_adapter_missing_metric_mapping_raises_app_exception`: assert `AppException(VALIDATION_FAILED)` when `metric_mappings` lacks required keys (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`) or when a translation is missing for the active locale.
      2. Add dual-logging verification using `unittest.mock.patch` on `backend_v2.services.sdui.adapters.metadata_adapter.logger.error`: assert `logger.error` is invoked with `exc_info=True` before `AppException` is raised.
    </action>
    <action>In `@[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]`:
      1. Verify exact classification threshold boundaries configured in `settings.py`: `80.0` -> `level_high`, `79.99` -> `level_medium`, `50.0` -> `level_medium`, `49.99` -> `level_low`.
      2. Verify dynamic settings override via `monkeypatch` targeting `backend_v2.services.sdui.adapters.authenticity_adapter.get_settings` (overriding `high=90.0, low=60.0` causing `85.0` to classify as `level_medium`) operates without singleton pollution.
      3. Add dual-logging verification asserting `logger.error` is called with `exc_info=True` upon invalid context or unmapped evaluation status.
    </action>
    <action>In `@[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]` and `@[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]`:
      1. Verify dual-logging exception handling and strict mapping resolution.
      2. Verify that `ExecutiveSummaryAdapter` properly merges `section_syntheses` dynamic paragraphs alongside the user role badge.
    </action>
    <action>In `@[backend_v2/tests/unit/services/test_blueprint.py]`:
      1. Verify that `BlueprintTransformer.build_report_dto()` raises `AppException(VALIDATION_FAILED)` when `target_block_order` contains an unmapped or un-hydrated `TargetBlockType` key without fallback.
      2. Verify graph adapter graceful degradation: when `preset_view == '3d_matrix'` but `len(axes) < 3`, the adapter returns downgraded 2D/1D blocks and emits `logger.warning` instead of crashing.
    </action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py --test`.</validation>
  </step>

  <step id="3" name="Prompt Directives SSOT &amp; Cross-Language Enum Parity Gate">
    <constraint invariant="prompt_asset_ssot_mandate">
      All prompt directives MUST reside in backend_v2/models/prompts/ as static XML strings. Seed data Prompts MUST NOT contain raw XML tags.
    </constraint>
    <action>In `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]`, expand test coverage to verify:
      1. `test_synthesis_directives_xml_validity`: All mandate constants (`SDUI_SYNTHESIS_MANDATE_BLOCK`, `SECTION_SYNTHESIS_DIRECTIVE_BLOCK`, `STATE_ISOLATION_BLOCK`) parse cleanly via `xml.etree.ElementTree.fromstring()`.
      2. `test_synthesis_directives_exports`: `backend_v2.models.prompts.__all__` contains all synthesis directives constants (`SDUI_SYNTHESIS_MANDATE_BLOCK`, `SECTION_SYNTHESIS_DIRECTIVE_BLOCK`, `STATE_ISOLATION_BLOCK`).
      3. `test_prompt_preservation_qualitative_integrity`: Core qualitative coaching concepts (Toulmin, Goodhart, Kahneman, Popper, Pearl, Humility, Traceability, Coherence) remain fully intact in `seed_data.json` PromptBlock `ai_description` strings per `prompt_preservation_mandate`.
    </action>
    <action>In `@[backend_v2/tests/unit/test_enum_parity.py]`:
      1. Verify 1:1 cross-language enum parity between Python `enums.py` and Dart `enums.dart` across all shared enums (`DisplayScale`, `TargetBlockType`, `PresetView`, `TextDeliveryMode`, `HistoricalContextMode`, `XaiExtensionType`, `RoleClassification`, `ScoringStrategy`).
      2. Verify `test_enum_l10n_keys()` ensuring all UI-driving enums define valid camelCase `l10n_key` properties matching ARB translation keys.
    </action>
    <action>In `@[backend_v2/tests/unit/test_worker_synthesis.py]`, verify that `worker.py` injects `SDUI_SYNTHESIS_MANDATE_BLOCK` into `<dynamic_context>` in the user payload during graph synthesis while keeping `sys_prompt` 100% static for Prompt Caching (`ephemeral_caching_topology`).</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/prompts/test_synthesis_directives.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test`.</validation>
  </step>

  <step id="4" name="Frontend Freezed Deserialization &amp; CheckedFromJsonException Firewall">
    <constraint invariant="silent_json_fallbacks">
      Frontend Freezed models MUST enforce disallowUnrecognizedKeys: true without unknownEnumValue fallbacks. Unmapped enum strings and unexpected JSON keys MUST throw CheckedFromJsonException.
    </constraint>
    <action>In `@[client_app_v2/test/features/studio/models/output_profile_test.dart]`:
      1. Verify `CheckedFromJsonException` is thrown when unmapped enum values (for `PresetView`, `TextDeliveryMode`, `HistoricalContextMode`, `DisplayScale`, or `TargetBlockType` in `targetBlockOrder`) are encountered.
      2. Verify `CheckedFromJsonException` is thrown when unrecognized extra keys (both at root `OutputProfile` level and inside nested `SynthesisConfigDTO` / `OutputLayoutBlock` objects) are present.
      3. Verify that `include_diagnostic_scorecard` and other purged legacy attributes trigger immediate deserialization failure.
    </action>
    <action>In `@[client_app_v2/test/features/studio/models/blueprint_config_test.dart]`:
      1. Verify that unknown `preset_view` strings throw `CheckedFromJsonException`.
      2. Verify that extra JSON keys throw `CheckedFromJsonException`.
    </action>
    <action>In `@[client_app_v2/test/shared/models/sdui_block_dto_test.dart]`:
      1. Verify that unknown SDUI block types (`block_type: 'unknown_type'`), missing required fields, and unrecognized extra keys across polymorphic block types throw exceptions (`CheckedFromJsonException` / `FormatException`) to prevent silent UI fallback degradation.
    </action>
    <validation>Run `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models/output_profile_test.dart --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/shared/models/sdui_block_dto_test.dart --test`.</validation>
  </step>

  <step id="5" name="Studio UI Widget Boundaries &amp; Slider Clamping Verification">
    <constraint invariant="desktop_pro_tool_interaction">
      Interactive widgets MUST support boundary resilience. Out-of-bounds database values MUST safely clamp on the visual Slider while displaying accurately in companion fields without framework assertion crashes.
    </constraint>
    <action>In `@[client_app_v2/test/features/studio/views/widgets/profile/blocks/block_card_registry_test.dart]`:
      1. Verify that out-of-bounds database values (specifically testing boundary scenario `max_extension_items = 50`) safely clamp on the visual Slider (`currentVal.clamp(minVal, sliderMax)`) while displaying `50` in the companion text field without Flutter assertion crashes.
      2. Verify that `MatrixGraphsBlockCard` and `MatrixSummaryTableCard` correctly partition layouts by `PresetView` without cross-card state pollution.
      3. Verify that all 13 `TargetBlockType` members are mapped in `BlockCardRegistry`.
    </action>
    <action>In `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`:
      1. Verify 3-tab navigation (`ProfileGeneralTab`, `ProfileScoringTab`, `ProfileLayoutsTab`) with mock provider overrides.
      2. Verify that saving output profile dispatches valid payloads to `OutputProfilesController` without schema violations.
    </action>
    <validation>Run `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/ --test`.</validation>
  </step>

  <step id="6" name="Global Quality Gate Audit Loops">
    <constraint invariant="zero_tolerance_audit_loop">
      Run global backend and frontend audit scripts enforcing Ruff linting, MyPy strict typing, Pytest coverage (>=90%), Freezed codegen, and Flutter analyzer checks.
    </constraint>
    <action>Execute Backend Global Audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Execute Frontend Freezed &amp; Analyzer Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`.</action>
    <action>Execute Frontend Full Test Suite: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`.</action>
    <validation>All backend tests (1,480+) and frontend tests (138+) pass with 0 errors, 0 warnings, and 0 skipped tests.</validation>
  </step>

  <step id="7" name="Final Live E2E REST API Verification Gate">
    <constraint invariant="mocking_mandate_for_llm">
      The Final E2E REST API Verification Gate validates the fully integrated FastAPI and worker pipeline against real LLM or local mock integration.
    </constraint>
    <action>Execute live integration test verifying PDF ingestion, eager extraction, DAG execution, SDUI synthesis, and report layout rendering:
      - Windows/PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
      - Unix/Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
    </action>
    <validation>Verify exit code 0 on `test_integration_real_llm.py`.</validation>
  </step>

  <step id="8" name="Post-Execution Architecture Sync &amp; Epic Completion Sign-Off">
    <action>Verify all 22 Definition of Done (DoD) criteria from Epic 144.</action>
    <action>Update `@[docs\epic\EPIC_144_tracker.md]` marking Phase 5 complete (`[OK]`), document learned invariants, and update summary statistics.</action>
    <action>Instruct the user to run `/tier7-describe-architecture` and `/tier8-audit-epic` to synchronize architecture manifestos and close out Epic 144.</action>
  </step>

  <dod_checklist>
    - [ ] `DisplayScale` Enum parity is mathematically enforced: `DisplayScale(StrEnum)` in Python and `@JsonEnum() DisplayScale` with `@JsonValue('normalized_100')` in Dart.
    - [ ] `TargetBlockType` Enum parity is mathematically enforced: `TargetBlockType(StrEnum)` in Python (13 members) and `@JsonEnum() TargetBlockType` in Dart with all 13 `@JsonValue` mappings.
    - [ ] `OutputProfile` and all OutputProfile DTOs strictly type `target_block_order` as `list[TargetBlockType]` (Python) and `List<TargetBlockType>` (Dart).
    - [ ] `blueprint.py` `_target_block_hydrators` is strictly typed as `dict[TargetBlockType, Callable]` without `str()` casting, and registry lookup is protected by `try...except KeyError:` raising `AppException(VALIDATION_FAILED)` on unmapped blocks.
    - [ ] `matrix_domain_parser.py` compares native `DisplayScale` enum members (`NORMALIZED_100`, `CUSTOM`) directly without magic string literals.
    - [ ] All backend test fixtures across `test_matrix_domain_parser.py`, `test_blueprint.py`, `test_scoring.py`, `test_worker_synthesis.py`, and `test_v2_core_models.py` pass with `DisplayScale` enums.
    - [ ] `SystemUiConstraints` enum is defined in `@[client_app_v2/lib/core/models/enums.dart]` for centralized UI slider and boundary limits (`maxExtensionItemsSliderMin: 1`, `maxExtensionItemsSliderMax: 20`, `maxExtensionItemsAbsoluteMax: 100`, `maxExtensionItemsDefault: 3`).
    - [ ] `OutputProfileCreateDTO` and `OutputProfileUpdateDTO` strictly validate `max_extension_items` with `Field(ge=1, le=100)`.
    - [ ] Flutter `xai_extensions_block_card.dart` implements Dual-Input Hybrid Pattern, safely clamping slider display values (`currentVal.clamp(minVal, sliderMax)`) and validating companion `TextFormField` (`1 <= val <= 100`) to prevent framework assertion crashes on out-of-bounds database values.
    - [ ] `layout_editor_card.dart` provides visual card selection for `PresetView` with adaptive form fields.
    - [ ] No manual comma-separated `steps` text fields remain in the UI.
    - [ ] All UI strings exist in both English (`app_en.arb`) and Finnish (`app_fi.arb`).
    - [ ] `MetadataAdapter` contains ZERO hardcoded Finnish strings (V7), ZERO duck-typing `getattr` calls or latent attribute name mismatches (`custom_preface` strictly resolved) (V7a), ZERO hardcoded title fallbacks (strictly resolved `name` + Fail-Fast) (V7b), and ZERO runtime `isinstance` guards on `created_at` (V7c) while safely guarding existence via `if context.execution.created_at:` prior to `.strftime()`. All labels (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`) are resolved bilingually.
    - [ ] `AuthenticityAdapter` contains ZERO hardcoded business logic thresholds (V13). Thresholds are resolved dynamically from `Settings.authenticity_threshold_high` and `Settings.authenticity_threshold_low` via top-level `get_settings()` import per `@[ki_global_config_sovereignty.md]`.
    - [ ] `seed_data.json` and backend test fixtures in `test_blueprint.py` and `test_metadata_adapter.py` explicitly seed all required `metric_mappings` metadata keys in both English and Finnish.
    - [ ] `OutputProfileResponseDTO` and `OutputProfileUpdateDTO` maintain the DTO firewall (`metric_mappings` excluded) to prevent Studio UI CRUD operations from clobbering system metric mappings.
    - [ ] `SynthesisTextAdapter` reads both `content_blocks` (static) and `section_syntheses` (dynamic Pipeline synthesis).
    - [ ] All adapter exception handling follows `adapter_dual_logging_process`: catch → `logger.error("[AdapterName] ...", exc_info=True)` → `raise AppException(...) from e`. Zero silent swallows exist in any modified adapter.
    - [ ] Matrix graph adapters emit SDUI blocks in the strict `adapter_flat_element_sequencing` order: `MarkdownBlock(### {title})` → `ParagraphBlock(synthesis)` → `GraphBlock(title=None)`. For `text_only` matrices, the graph block is omitted entirely.
    - [ ] Graph adapters implement `adapter_strict_fail_fast_routing` Graceful Degradation: if `len(axes) < 3` for a 3D graph request, the adapter downgrades to `2d_compare` or `1d_metrics` and logs `logger.warning` instead of crashing.
    - [ ] Block visibility is controlled exclusively via `target_block_order` manipulation (no `include_X: bool` fields).
    - [ ] Redundant legacy field `include_diagnostic_scorecard: bool` is completely removed from Backend models/DTOs and Frontend Freezed models.
    - [ ] Dedicated unit tests in `@[backend_v2/tests/unit/test_settings.py]` verify `authenticity_threshold_high` and `authenticity_threshold_low` boundary limits (`ge=0.0, le=100.0`), cross-field validation (`high >= low`), and environment variable overrides.
    - [ ] Dedicated unit tests in `@[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]` verify boundary classifications (`80.0`, `79.99`, `50.0`, `49.99`), `monkeypatch` settings isolation, and dual-logging exception handling.
    - [ ] `OutputProfile`, all OutputProfile DTOs, and all nested sub-DTOs (`SynthesisConfigDTO`, `OutputLayoutBlock`, `I18nText`, and all `AnySduiBlock` / SduiBlockDTO polymorphic subtypes) maintain `model_config = ConfigDict(strict=True, extra="forbid")` in Python and `@JsonSerializable(disallowUnrecognizedKeys: true)` without `unknownEnumValue` in Dart Freezed, with zero relaxed serialization flags (`extra="ignore"` strictly banned).
    - [ ] Backend OpenAPI generation and Frontend Freezed generation are synchronized in lockstep to guarantee zero HTTP 422 Unprocessable Entity or 500 Validation Failed deserialization crashes.
    - [ ] `RenderedSynthesisCache.xai_highlights` is strictly typed as `list[XaiHighlightItem]` and defensive try-catch loops in `XaiHighlightsAdapter` are removed.
    - [ ] All dynamic UI block arrays (`OutputProfile.content_blocks`, `ReportDataDTO.inner_sdui_blocks`) are strictly typed as polymorphic Dart SduiBlockDTO models and Python `list[AnySduiBlock]` with zero occurrences of `List<dynamic>` or `list[dict[str, Any]]`.
    - [ ] In Flutter, the polymorphic block DTO (SduiBlockDTO) enforces `@Freezed(unionKey: 'block_type')` without `fallbackUnion` and with `@JsonSerializable(disallowUnrecognizedKeys: true)`.
    - [ ] Unified Synthesis Prompt SSOT: `@[backend_v2/models/prompts/synthesis_directives.py]` defines structural mandate constants re-exported via `@[backend_v2/models/prompts/__init__.py]`, layout synthesis objects contain only block IDs, and `worker.py` injects `SDUI_SYNTHESIS_MANDATE_BLOCK` into `<dynamic_context>` maintaining static system prompt prefix.
    - [ ] Violation V3 (`AsyncValue<List<dynamic>>`) is completely eradicated in `output_profile_crud_view.dart` in favor of typed `AsyncValue<List<PromptBlock>>`, `AsyncValue<List<Workflow>>`, and `AsyncValue<List<NodeStrategy>>`.
    - [ ] All `.arb` keys for block titles, tab labels, and preset views are registered in both `app_en.arb` and `app_fi.arb`.
    - [ ] Anti-Happy-Path Negative Tests: All 7 explicit negative test suites pass green (unmapped target block types, missing metric mappings, out-of-bounds threshold settings, out-of-bounds `max_extension_items`, 1:1 cross-language enum parity, `CheckedFromJsonException` on unmapped Freezed enums / extra keys, and SDUI polymorphic block exceptions).
    - [ ] All automated tests pass without warnings or deprecations.
  </dod_checklist>

  <validation_gate>
    <command>uv run python scripts/backend_audit_loop.py backend_v2 --test</command>
    <command>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build</command>
    <command>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test</command>
    <command>$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py</command>
  </validation_gate>
</execution_protocol>
```

---

## 3. Verification Plan

### Automated Tests
- Backend Unit Tests: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- Frontend Freezed & Analyzer: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`
- Frontend Widget & Unit Tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`
- Final E2E REST API Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Manual Verification
1. Open Quorum Studio -> Output Profiles -> Edit Profile.
2. Verify all tabs and cards load without rendering errors.
3. Save modified profile and verify database state matches strict Pydantic V2 schema.

