# Phase 0-C: Backend Models & DTO Strict Purge

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 4 "Synchronous Backend Model & DTO Purge" (L305-L317) and 6-Step Pipeline Step 2 (L245-L247)
**Scope:** Backend Python only

**Overview:** Remove `include_diagnostic_scorecard` from domain models and DTOs, migrate `display_scale` from `Literal[...]` to `DisplayScale` enum, migrate `target_block_order` from `list[str]` to `list[TargetBlockType]`, enforce non-nullable `max_extension_items` with `Field(ge=1, le=100)`, and enforce `ConfigDict(strict=True, extra="forbid")` on all models.

**Target Files:**
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L1313-L1398]` — OutputProfile class
- `[MODIFY]` `@[backend_v2/models/dtos/output_profile.py]` — OutputProfileCreateDTO, OutputProfileUpdateDTO, OutputProfileResponseDTO

**Context Files (Read-Only):**
- `@[backend_v2/models/enums.py]` — DisplayScale, TargetBlockType (from Plan 01)
- `@[backend_v2/seed/seed_data.json]` — Already sanitized (Plan 02)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 02 (Seed Sanitization) is complete — grep_search for "include_diagnostic_scorecard" in seed_data.json returns zero results. Verify local database was reseeded.</action>
    <action>Look forward: Verify that @[backend_v2/models/v2_core.py] still contains `include_diagnostic_scorecard: bool` at L1355 and `display_scale: Literal[...]` at L1351 and `target_block_order: list[str]` at L1375.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/seed/seed_data.json — Already sanitized in Plan 02, do NOT modify</file>
    <file>backend_v2/settings.py — Already done in Plan 01</file>
    <file>backend_v2/models/enums.py — Already done in Plan 01</file>
    <file>backend_v2/services/ — Do NOT modify service layer yet (Phase 3)</file>
    <file>backend_v2/tests/ — Do NOT update test fixtures yet (Plans 04-05)</file>
    <file>client_app_v2/ — Do NOT touch any Flutter files</file>
  </anti_targets>

  <dod_checklist>
    <item>`include_diagnostic_scorecard` completely removed from OutputProfile, OutputProfileCreateDTO, OutputProfileUpdateDTO, OutputProfileResponseDTO.</item>
    <item>`display_scale` type changed from `Literal["original", "custom", "normalized_100"]` to `DisplayScale` in OutputProfile and all DTOs.</item>
    <item>`target_block_order` type changed from `list[str]` to `list[TargetBlockType]` in OutputProfile and all DTOs (using `LaxTargetBlockType` where strict=False needed for database deserialization).</item>
    <item>`max_extension_items` is non-nullable `Annotated[int, Field(default=3, ge=1, le=100)]` on OutputProfileCreateDTO and OutputProfileResponseDTO, and `Annotated[int | None, Field(default=None, ge=1, le=100)]` on OutputProfileUpdateDTO.</item>
    <item>`model_config = ConfigDict(strict=True, extra="forbid")` enforced on OutputProfile, OutputLayoutBlock, SynthesisConfigDTO, and all DTOs.</item>
  </dod_checklist>

  <step id="1" name="MODIFY OutputProfile IN v2_core.py">
    <action>In @[backend_v2/models/v2_core.py], modify the OutputProfile class (near L1340-L1380):
1. DELETE: `include_diagnostic_scorecard: bool = Field(...)` (L1355).
2. CHANGE: `display_scale: Literal["original", "custom", "normalized_100"]` (L1351) → `display_scale: DisplayScale = Field(default=DisplayScale.ORIGINAL, description="...")`.
3. CHANGE: `target_block_order: list[str]` (L1375) → `target_block_order: list[LaxTargetBlockType] = Field(...)`. Use `LaxTargetBlockType` (which is `Annotated[TargetBlockType, Field(strict=False)]` already defined at L626 of enums.py) to allow Pydantic to coerce string values from the database into enum members.
4. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` is present on `OutputProfile`.
5. Ensure the import at the top of v2_core.py includes `DisplayScale` from enums.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard: bool = Field(...)` at @[backend_v2/models/v2_core.py#L1355]. REPLACE `display_scale: Literal[...]` with `display_scale: DisplayScale`. REPLACE `target_block_order: list[str]` with `target_block_order: list[LaxTargetBlockType]`.</demolish>
    <contract_freeze>
      OutputProfile.display_scale: DisplayScale = Field(default=DisplayScale.ORIGINAL, ...)
      OutputProfile.target_block_order: list[LaxTargetBlockType] = Field(...)
    </contract_freeze>
    <constraint invariant="strict_pydantic_v2_extra_forbid">ConfigDict(strict=True, extra="forbid") is MANDATORY. Relaxing to extra="ignore" is BANNED.</constraint>
  </step>

  <step id="2" name="MODIFY OutputProfileCreateDTO">
    <action>In @[backend_v2/models/dtos/output_profile.py], modify `OutputProfileCreateDTO`:
1. DELETE: `include_diagnostic_scorecard` field.
2. CHANGE: `display_scale` type to `DisplayScale`.
3. CHANGE: `target_block_order` type to `list[TargetBlockType]` (strict — DTOs receive validated API input).
4. ENFORCE: `max_extension_items: Annotated[int, Field(default=3, ge=1, le=100, description="Maximum extension items per category")]`.
5. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` present.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard` field from OutputProfileCreateDTO. REPLACE: `display_scale: Annotated[Literal[...], ...]` with `display_scale: DisplayScale`. REPLACE: nullable `max_extension_items: int | None` (if present) with non-nullable `int` with `Field(default=3, ge=1, le=100)`.</demolish>
    <contract_freeze>
      OutputProfileCreateDTO.display_scale: DisplayScale
      OutputProfileCreateDTO.target_block_order: list[TargetBlockType]
      OutputProfileCreateDTO.max_extension_items: Annotated[int, Field(default=3, ge=1, le=100)]
    </contract_freeze>
  </step>

  <step id="3" name="MODIFY OutputProfileUpdateDTO">
    <action>In @[backend_v2/models/dtos/output_profile.py], modify `OutputProfileUpdateDTO`:
1. DELETE: `include_diagnostic_scorecard` field.
2. CHANGE: `display_scale` type to `DisplayScale | None`.
3. CHANGE: `target_block_order` type to `list[TargetBlockType] | None`.
4. ENFORCE: `max_extension_items: Annotated[int | None, Field(default=None, ge=1, le=100)]`.
5. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` present.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard` field from OutputProfileUpdateDTO.</demolish>
    <contract_freeze>
      OutputProfileUpdateDTO.display_scale: DisplayScale | None = None
      OutputProfileUpdateDTO.target_block_order: list[TargetBlockType] | None = None
      OutputProfileUpdateDTO.max_extension_items: Annotated[int | None, Field(default=None, ge=1, le=100)]
    </contract_freeze>
  </step>

  <step id="4" name="MODIFY OutputProfileResponseDTO">
    <action>In @[backend_v2/models/dtos/output_profile.py], modify `OutputProfileResponseDTO`:
1. DELETE: `include_diagnostic_scorecard` field.
2. CHANGE: `display_scale` type to `DisplayScale`.
3. CHANGE: `target_block_order` type to `list[TargetBlockType]`.
4. ENFORCE: `max_extension_items: Annotated[int, Field(default=3, ge=1, le=100)]` (non-nullable).
5. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` present.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard` field from OutputProfileResponseDTO.</demolish>
    <contract_freeze>
      OutputProfileResponseDTO.display_scale: DisplayScale
      OutputProfileResponseDTO.target_block_order: list[TargetBlockType]
      OutputProfileResponseDTO.max_extension_items: Annotated[int, Field(default=3, ge=1, le=100)]
    </contract_freeze>
  </step>

  <validation_gate>
    <check>grep_search for "include_diagnostic_scorecard" in @[backend_v2/models/v2_core.py] — MUST return zero results</check>
    <check>grep_search for "include_diagnostic_scorecard" in @[backend_v2/models/dtos/output_profile.py] — MUST return zero results</check>
    <check>grep_search for "DisplayScale" in @[backend_v2/models/v2_core.py] — MUST find the field definition</check>
    <check>grep_search for "list[LaxTargetBlockType]" in @[backend_v2/models/v2_core.py] — MUST find target_block_order</check>
    <check>grep_search for 'Literal\["original"' in @[backend_v2/models/v2_core.py] — MUST return zero results (no more raw Literal)</check>
    <check>grep_search for 'Literal\["original"' in @[backend_v2/models/dtos/output_profile.py] — MUST return zero results</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test (Ruff + MyPy only, tests will be fixed in Plan 04-05)</check>
  </validation_gate>
</execution_protocol>
```
