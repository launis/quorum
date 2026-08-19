# Phase 0-B: Master Seed Sanitization & Local Reseed

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 3 "Master Seed Sanitization" (L297-L303) and 6-Step Pipeline Step 1 (L240-L242)
**Scope:** Database/Seed Data only

**Overview:** Sanitize `seed_data.json` to remove legacy `include_diagnostic_scorecard` fields, ensure all `output_profiles` have valid enum-compatible values for `display_scale`, `preset_view`, `text_delivery_mode`, and ensure bilingual `metric_mappings` are complete. Then execute local database reseed. This step MUST complete BEFORE any Pydantic model modifications (Plan 03).

**Target Files:**
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]`

**Context Files (Read-Only):**
- `@[backend_v2/models/enums.py]` — TargetBlockType, PresetView, ScoringStrategy enum values
- `@[backend_v2/models/v2_core.py]` — OutputProfile current schema (still has include_diagnostic_scorecard at L1355)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 01 (Backend Config & Enums) is complete — DisplayScale enum exists in @[backend_v2/models/enums.py] and authenticity thresholds exist in @[backend_v2/settings.py].</action>
    <action>Look forward: Verify that @[backend_v2/seed/seed_data.json] still contains `include_diagnostic_scorecard` fields that need removal. Use grep_search to confirm.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\03_seed_vault.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/models/v2_core.py — Do NOT modify domain models yet (Plan 03)</file>
    <file>backend_v2/models/dtos/output_profile.py — Do NOT modify DTOs yet (Plan 03)</file>
    <file>backend_v2/settings.py — Already done in Plan 01</file>
    <file>backend_v2/models/enums.py — Already done in Plan 01</file>
    <file>client_app_v2/ — Do NOT touch any Flutter files</file>
    <file>PromptBlock ai_description fields — Do NOT touch prompt texts (prompt_preservation_mandate). PromptBlock cleanup is Phase 3 scope.</file>
  </anti_targets>

  <dod_checklist>
    <item>All `output_profiles` in seed_data.json have valid enum keys for display_scale ("original", "custom", "normalized_100"), preset_view, text_delivery_mode.</item>
    <item>All `metric_mappings` in output_profiles are complete with bilingual entries for metadata_user, metadata_organization, metadata_scoring_engine, metadata_strictness.</item>
    <item>Zero occurrences of `include_diagnostic_scorecard` remain in seed_data.json.</item>
    <item>Local database re-seeded successfully via `uv run python backend_v2/seed/run_seed.py local`.</item>
  </dod_checklist>

  <step id="1" name="AUDIT CURRENT SEED DATA STATE">
    <action>Use grep_search on @[backend_v2/seed/seed_data.json] to locate:
1. All occurrences of `"include_diagnostic_scorecard"` — document exact line numbers for removal.
2. All occurrences of `"display_scale"` — verify each is one of "original", "custom", "normalized_100".
3. All occurrences of `"metric_mappings"` — verify completeness.
4. All `output_profiles` entries — verify `preset_view` and `text_delivery_mode` keys are valid enum strings.</action>
    <constraint>Do NOT modify the file yet. Document the exact locations first.</constraint>
  </step>

  <step id="2" name="REMOVE include_diagnostic_scorecard FROM ALL OUTPUT PROFILES">
    <action>Delete ALL occurrences of `"include_diagnostic_scorecard": true` and `"include_diagnostic_scorecard": false` from the `output_profiles` array in @[backend_v2/seed/seed_data.json]. Use multi_replace_file_content or surgical edits to remove each key-value pair entirely (including the trailing comma if necessary to maintain valid JSON).</action>
    <demolish>REMOVE: every `"include_diagnostic_scorecard": ...` key-value pair across all output_profile entries in seed_data.json. This legacy field is replaced by the presence/absence of `matrix_summary_table_block` and `matrix_graphs_block` in `target_block_order`.</demolish>
    <constraint invariant="seed_data_sanitization_mandate">Master seed data MUST be sanitized to purge legacy keys BEFORE removing the field from Python models (Plan 03). Failure to do this causes `pydantic.ValidationError(extra_forbidden)` on next database read.</constraint>
  </step>

  <step id="3" name="VERIFY AND COMPLETE metric_mappings METADATA KEYS">
    <action>For EACH output_profile in @[backend_v2/seed/seed_data.json], verify that `metric_mappings` contains bilingual I18nText entries for all 4 required metadata label keys (specifically and exhaustively: `metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`). If ANY key is missing, add it with the following exact bilingual entries:
```json
"metadata_user": {"default_locale": "fi", "translations": {"fi": "Käyttäjä:", "en": "User:"}},
"metadata_organization": {"default_locale": "fi", "translations": {"fi": "Organisaatio:", "en": "Organization:"}},
"metadata_scoring_engine": {"default_locale": "fi", "translations": {"fi": "Arviointimoottori:", "en": "Scoring Engine:"}},
"metadata_strictness": {"default_locale": "fi", "translations": {"fi": "Ankaruustaso:", "en": "Strictness Level:"}}
```</action>
    <constraint invariant="seed_metadata_contract">All profiles MUST define bilingual (en + fi) I18nText entries for all 4 metadata label keys. This enables MetadataAdapter (Phase 3) to strictly resolve labels via I18nText.resolve(locale) instead of hardcoded Finnish strings.</constraint>
  </step>

  <step id="4" name="VERIFY ENUM-COMPATIBLE VALUES">
    <action>Verify that ALL `display_scale` values in seed_data.json are exactly one of: "original", "custom", "normalized_100".
Verify that ALL `preset_view` values are exactly one of: "1d_metrics", "2d_compare", "3d_matrix", "text_only", "matrix_summary".
Verify that ALL `text_delivery_mode` values are exactly one of: "full", "summary", "bullets".
Verify that ALL `scoring_strategy` values (if present) are exactly one of: "waterfall", "average", "weighted_average", "pure_math".
If any value is invalid or missing, correct it to the appropriate default.</action>
  </step>

  <step id="5" name="EXECUTE LOCAL DATABASE RESEED">
    <action>Execute: `uv run python backend_v2/seed/run_seed.py local`</action>
    <constraint invariant="local_database_reseed_mandate">The local TinyDB MUST be refreshed to eliminate stale keys before executing backend model modifications in Plan 03.</constraint>
    <constraint>The command MUST complete without errors. If it fails, diagnose the JSON formatting issue in seed_data.json and fix it before retrying.</constraint>
  </step>

  <validation_gate>
    <check>grep_search for "include_diagnostic_scorecard" in @[backend_v2/seed/seed_data.json] — MUST return zero results</check>
    <check>grep_search for "metadata_user" in @[backend_v2/seed/seed_data.json] — MUST find entries in every output_profile</check>
    <check>grep_search for "metadata_organization" in @[backend_v2/seed/seed_data.json] — MUST find entries in every output_profile</check>
    <check>grep_search for "metadata_scoring_engine" in @[backend_v2/seed/seed_data.json] — MUST find entries in every output_profile</check>
    <check>grep_search for "metadata_strictness" in @[backend_v2/seed/seed_data.json] — MUST find entries in every output_profile</check>
    <check>uv run python backend_v2/seed/run_seed.py local — MUST exit 0</check>
  </validation_gate>
</execution_protocol>
```
