# Phase 0-C: Backend Models & DTO Strict Purge

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 4 "Synchronous Backend Model & DTO Purge" (L305-L317) and 6-Step Pipeline Step 2 (L245-L247)
**Scope:** Backend Python only

**Overview:** Remove `include_diagnostic_scorecard` from domain models and DTOs, migrate `display_scale` from `Literal[...]` to `DisplayScale` enum, migrate `target_block_order` from `list[str]` to `list[TargetBlockType]`, enforce non-nullable `max_extension_items` with `Field(ge=1, le=100)`, and enforce `ConfigDict(strict=True, extra="forbid")` on all models.

**Target Files:**
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L1317-L1410]` — OutputProfile class
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
    <item>`include_diagnostic_scorecard` completely removed from OutputProfile, OutputProfileCreateDTO, OutputProfileUpdateDTO, OutputProfileResponseDTO (including class docstrings).</item>
    <item>`display_scale` type changed from `Literal["original", "custom", "normalized_100"]` to `Annotated[LaxDisplayScale, ...]` in OutputProfile and `Annotated[DisplayScale, ...]` in all DTOs using PEP 593 Annotated syntax.</item>
    <item>`target_block_order` type changed from `list[str]` to `Annotated[list[LaxTargetBlockType], ...]` in OutputProfile and `Annotated[list[TargetBlockType], ...]` in OutputProfileResponseDTO (with enum default factories), and `Annotated[list[TargetBlockType] | None, ...]` in OutputProfileCreateDTO and OutputProfileUpdateDTO.</item>
    <item>`max_extension_items` is non-nullable `Annotated[int, Field(default=3, ge=1, le=100)] = 3` on OutputProfileCreateDTO and OutputProfileResponseDTO, and `Annotated[int | None, Field(default=None, ge=1, le=100)] = None` on OutputProfileUpdateDTO.</item>
    <item>`model_config = ConfigDict(strict=True, extra="forbid")` verified on OutputProfile, OutputLayoutBlock, SynthesisConfigDTO, and all DTOs.</item>
    <item>All imports in `v2_core.py` and `output_profile.py` cleanly updated with no unused `Literal` or missing enum symbols.</item>
  </dod_checklist>

  <step id="1" name="MODIFY OutputProfile IN v2_core.py">
    <action>In @[backend_v2/models/v2_core.py], modify the `OutputProfile` class (L1313-L1398):
1. DELETE: `include_diagnostic_scorecard: bool = Field(...)` (L1355-L1357).
2. CHANGE: `display_scale: Literal[...]` (L1351) → `display_scale: Annotated[LaxDisplayScale, Field(default=DisplayScale.ORIGINAL, description="Selects the source scaling for the scores printed by Blueprint.")] = DisplayScale.ORIGINAL`.
3. CHANGE: `target_block_order: list[str]` (L1375-L1391) → `target_block_order: Annotated[list[LaxTargetBlockType], Field(default_factory=lambda: [TargetBlockType.METADATA_BLOCK, TargetBlockType.EXECUTIVE_SUMMARY_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK, TargetBlockType.MATRIX_GRAPHS_BLOCK, TargetBlockType.GROUPED_EXTENSIONS_BLOCK, TargetBlockType.PENALTIES_BLOCK, TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK, TargetBlockType.VARIANCE_VALIDATION_BLOCK, TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK, TargetBlockType.PRINTABLE_SOURCES_BLOCK, TargetBlockType.GLOBAL_SCORE_BLOCK, TargetBlockType.AUDIT_TRAIL_BLOCK], description="The exact dynamic block sequence for the SDUI output. Drives the dispatch loop in blueprint.py.")]`.
4. CHANGE: `max_extension_items: int = Field(...)` (L1344) → `max_extension_items: Annotated[int, Field(default=3, ge=1, le=100, description="Max number of items to show per grouped XAI extension.")] = 3`.
5. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` is present on `OutputProfile`.
6. VERIFY: Imports at top of `v2_core.py` include `DisplayScale`, `LaxDisplayScale`, `TargetBlockType`, `LaxTargetBlockType` from `backend_v2.models.enums`.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard: bool = Field(...)` at @[backend_v2/models/v2_core.py#L1355]. REPLACE `display_scale: Literal[...]` with `display_scale: Annotated[LaxDisplayScale, ...]`. REPLACE `target_block_order: list[str]` with `target_block_order: Annotated[list[LaxTargetBlockType], ...]`.</demolish>
    <contract_freeze>
      OutputProfile.display_scale: Annotated[LaxDisplayScale, Field(default=DisplayScale.ORIGINAL, description="Selects the source scaling for the scores printed by Blueprint.")] = DisplayScale.ORIGINAL
      OutputProfile.target_block_order: Annotated[list[LaxTargetBlockType], Field(default_factory=lambda: [TargetBlockType.METADATA_BLOCK, TargetBlockType.EXECUTIVE_SUMMARY_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK, TargetBlockType.MATRIX_GRAPHS_BLOCK, TargetBlockType.GROUPED_EXTENSIONS_BLOCK, TargetBlockType.PENALTIES_BLOCK, TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK, TargetBlockType.VARIANCE_VALIDATION_BLOCK, TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK, TargetBlockType.PRINTABLE_SOURCES_BLOCK, TargetBlockType.GLOBAL_SCORE_BLOCK, TargetBlockType.AUDIT_TRAIL_BLOCK], description="The exact dynamic block sequence for the SDUI output. Drives the dispatch loop in blueprint.py.")]
      OutputProfile.max_extension_items: Annotated[int, Field(default=3, ge=1, le=100, description="Max number of items to show per grouped XAI extension.")] = 3
    </contract_freeze>
    <constraint invariant="strict_pydantic_v2_extra_forbid">ConfigDict(strict=True, extra="forbid") is MANDATORY. Relaxing to extra="ignore" is BANNED.</constraint>
  </step>

  <step id="2" name="MODIFY OutputProfileCreateDTO">
    <action>In @[backend_v2/models/dtos/output_profile.py], modify `OutputProfileCreateDTO`:
1. UPDATE DOCSTRING: Remove `include_diagnostic_scorecard` from class docstring attributes.
2. DELETE: `include_diagnostic_scorecard` field definition (L126-L128).
3. CHANGE: `display_scale` (L101-L104) → `display_scale: Annotated[DisplayScale, Field(default=DisplayScale.ORIGINAL, description="UI rendering scale instruction.")] = DisplayScale.ORIGINAL`.
4. CHANGE: `target_block_order` (L143-L146) → `target_block_order: Annotated[list[TargetBlockType] | None, Field(default=None, description="Optional block order override.")] = None`.
5. ENFORCE: `max_extension_items` (L93-L100) → `max_extension_items: Annotated[int, Field(default=3, ge=1, le=100, description="Max number of items to show per grouped XAI extension. Sorted by severity.")] = 3`.
6. VERIFY: Imports include `DisplayScale`, `TargetBlockType` from `backend_v2.models.enums`.
7. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` present.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard` field and docstring reference from OutputProfileCreateDTO. REPLACE: `display_scale: Annotated[Literal[...], ...]` with `display_scale: Annotated[DisplayScale, ...]`. REPLACE: nullable `max_extension_items: int | None` with non-nullable `Annotated[int, Field(default=3, ge=1, le=100)] = 3`.</demolish>
    <contract_freeze>
      OutputProfileCreateDTO.display_scale: Annotated[DisplayScale, Field(default=DisplayScale.ORIGINAL, description="UI rendering scale instruction.")] = DisplayScale.ORIGINAL
      OutputProfileCreateDTO.target_block_order: Annotated[list[TargetBlockType] | None, Field(default=None, description="Optional block order override.")] = None
      OutputProfileCreateDTO.max_extension_items: Annotated[int, Field(default=3, ge=1, le=100, description="Max number of items to show per grouped XAI extension. Sorted by severity.")] = 3
    </contract_freeze>
  </step>

  <step id="3" name="MODIFY OutputProfileUpdateDTO">
    <action>In @[backend_v2/models/dtos/output_profile.py], modify `OutputProfileUpdateDTO`:
1. UPDATE DOCSTRING: Remove `include_diagnostic_scorecard` from class docstring attributes.
2. DELETE: `include_diagnostic_scorecard` field definition (L231-L233).
3. CHANGE: `display_scale` (L227-L230) → `display_scale: Annotated[DisplayScale | None, Field(default=None, description="UI rendering scale instruction.")] = None`.
4. CHANGE: `target_block_order` (L248-L251) → `target_block_order: Annotated[list[TargetBlockType] | None, Field(default=None, description="Optional block order override.")] = None`.
5. ENFORCE: `max_extension_items` (L219-L226) → `max_extension_items: Annotated[int | None, Field(default=None, ge=1, le=100, description="Max number of items to show per grouped XAI extension. Sorted by severity.")] = None`.
6. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` present.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard` field and docstring reference from OutputProfileUpdateDTO.</demolish>
    <contract_freeze>
      OutputProfileUpdateDTO.display_scale: Annotated[DisplayScale | None, Field(default=None, description="UI rendering scale instruction.")] = None
      OutputProfileUpdateDTO.target_block_order: Annotated[list[TargetBlockType] | None, Field(default=None, description="Optional block order override.")] = None
      OutputProfileUpdateDTO.max_extension_items: Annotated[int | None, Field(default=None, ge=1, le=100, description="Max number of items to show per grouped XAI extension. Sorted by severity.")] = None
    </contract_freeze>
  </step>

  <step id="4" name="MODIFY OutputProfileResponseDTO">
    <action>In @[backend_v2/models/dtos/output_profile.py], modify `OutputProfileResponseDTO`:
1. UPDATE DOCSTRING: Remove `include_diagnostic_scorecard` from class docstring attributes.
2. DELETE: `include_diagnostic_scorecard` field definition (L321-L323).
3. CHANGE: `display_scale` (L320) → `display_scale: Annotated[DisplayScale, Field(default=DisplayScale.ORIGINAL, description="Exact enumeration of UI rendering modes ('normalized_100').")] = DisplayScale.ORIGINAL`.
4. CHANGE: `target_block_order` (L294-L312) → `target_block_order: Annotated[list[TargetBlockType], Field(default_factory=lambda: [TargetBlockType.METADATA_BLOCK, TargetBlockType.EXECUTIVE_SUMMARY_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK, TargetBlockType.MATRIX_GRAPHS_BLOCK, TargetBlockType.GROUPED_EXTENSIONS_BLOCK, TargetBlockType.PENALTIES_BLOCK, TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK, TargetBlockType.VARIANCE_VALIDATION_BLOCK, TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK, TargetBlockType.PRINTABLE_SOURCES_BLOCK, TargetBlockType.GLOBAL_SCORE_BLOCK, TargetBlockType.AUDIT_TRAIL_BLOCK])]`.
5. ENFORCE: `max_extension_items` (L319) → `max_extension_items: Annotated[int, Field(default=3, ge=1, le=100, description="Top limit cap applying constraints to presentation loops.")] = 3`.
6. VERIFY: `model_config = ConfigDict(strict=True, extra="forbid")` present.</action>
    <demolish>REMOVE: `include_diagnostic_scorecard` field and docstring reference from OutputProfileResponseDTO.</demolish>
    <contract_freeze>
      OutputProfileResponseDTO.display_scale: Annotated[DisplayScale, Field(default=DisplayScale.ORIGINAL, description="Exact enumeration of UI rendering modes ('normalized_100').")] = DisplayScale.ORIGINAL
      OutputProfileResponseDTO.target_block_order: Annotated[list[TargetBlockType], Field(default_factory=lambda: [TargetBlockType.METADATA_BLOCK, TargetBlockType.EXECUTIVE_SUMMARY_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK, TargetBlockType.MATRIX_GRAPHS_BLOCK, TargetBlockType.GROUPED_EXTENSIONS_BLOCK, TargetBlockType.PENALTIES_BLOCK, TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK, TargetBlockType.VARIANCE_VALIDATION_BLOCK, TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK, TargetBlockType.PRINTABLE_SOURCES_BLOCK, TargetBlockType.GLOBAL_SCORE_BLOCK, TargetBlockType.AUDIT_TRAIL_BLOCK])]
      OutputProfileResponseDTO.max_extension_items: Annotated[int, Field(default=3, ge=1, le=100, description="Top limit cap applying constraints to presentation loops.")] = 3
    </contract_freeze>
  </step>

  <validation_gate>
    <check>grep_search for "include_diagnostic_scorecard" in @[backend_v2/models/v2_core.py] — MUST return zero results</check>
    <check>grep_search for "include_diagnostic_scorecard" in @[backend_v2/models/dtos/output_profile.py] — MUST return zero results</check>
    <check>grep_search for "DisplayScale" in @[backend_v2/models/v2_core.py] — MUST find the field definition</check>
    <check>grep_search for "LaxTargetBlockType" in @[backend_v2/models/v2_core.py] — MUST find target_block_order</check>
    <check>grep_search for 'Literal\["original"' in @[backend_v2/models/v2_core.py] — MUST return zero results (no more raw Literal)</check>
    <check>grep_search for 'Literal\["original"' in @[backend_v2/models/dtos/output_profile.py] — MUST return zero results</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py backend_v2/models/dtos/output_profile.py --test</check>
  </validation_gate>
</execution_protocol>
```
