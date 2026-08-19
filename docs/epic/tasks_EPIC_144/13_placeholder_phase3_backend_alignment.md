# Phase 3: Backend Execution, Synthesis Alignment & Prompt DRY Simplification

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 3 "Backend Execution Alignment" (L512-L604)
**Scope:** Backend Python adapters, DTOs, prompt directives SSOT, seed sanitization, and Flutter DTO alignment.

## 1. Executive Summary & Problem Statement

Phase 3 aligns Quorum's backend pipeline with the modernized `OutputProfile` schema developed in Phases 0–2. Currently:
1. `AuthenticityAdapter` hardcodes `AUTHENTICITY_THRESHOLDS = {"high": 80.0, "low": 50.0}` instead of referencing `backend_v2/settings.py` (violating `@[ki_global_config_sovereignty.md]`).
2. `MetadataAdapter` contains hardcoded Finnish strings (`"Käyttäjä:"`, `"Organisaatio:"`), uses `getattr(context.profile, "custom_preamble", None)` (a bug: the domain model attribute is `custom_preface`), falls back to `"Raportti"`, and uses `isinstance(dt, datetime)` duck-typing (violating `@[ki_dual_axis_localization_architecture.md]` and `@[ki_python_314_concurrency_strictness.md]`).
3. `SynthesisTextAdapter` only reads static `content_blocks`, ignoring dynamic `section_syntheses` computed during pipeline execution (violating `@[ki_tripartite_pipeline_architecture.md]`).
4. `ExecutiveSummaryAdapter` only outputs the user role badge, omitting synthesized executive summary paragraphs.
5. `blueprint.py` target block hydrator dispatch loop uses string keys `str(target_k)` instead of strict enum keys `TargetBlockType` and lacks explicit `try...except KeyError:` fail-fast handling.
6. `matrix_domain_parser.py` compares raw string literals (`display_scale == "normalized_100"`) instead of native `DisplayScale` enum members.
7. Graph synthesis PromptBlocks in `seed_data.json` duplicate mathematical scale validation, two-paragraph structuring, and XML wrapper tags instead of referencing a centralized Python SSOT `synthesis_directives.py` (`@[ki_global_config_sovereignty.md]`).
8. `SynthesisConfigDTO` retains 6 dead-weight fields (`model_strategy`, `historical_context_mode`, `enable_pii_masking`, `allowed_exports`, `omit_empty_sections`, `allowed_mcp_tools`) across backend and frontend models, causing bloat and schema confusion.
9. `RenderedSynthesisCache.xai_highlights` is typed as `list[Any]`, forcing `XaiHighlightsAdapter` to perform defensive runtime try-catch validation loops.

This plan executes a rigorous 9-step atomic sequence to eliminate all these anti-patterns, keeping domain models strictly typed and 100% compliant with Quorum 2026 invariants.

---

## 2. Target Files & Action Catalog

### Modified Files:
1. `[MODIFY]` `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`
   - Delete module-level `AUTHENTICITY_THRESHOLDS` dict.
   - Import `get_settings` at module level and read `authenticity_threshold_high` and `authenticity_threshold_low` dynamically.
2. `[MODIFY]` `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`
   - Eradicate hardcoded Finnish strings: resolve labels dynamically from `context.profile.metric_mappings` with Fail-Fast `KeyError` -> `AppException(VALIDATION_FAILED)`.
   - Fix `custom_preamble` bug: access `context.profile.custom_preface.resolve(context.locale) if context.profile.custom_preface else None`.
   - Remove `"Raportti"` fallback: enforce `context.profile.name.resolve(context.locale)`.
   - Eliminate `isinstance(dt, datetime)`: check `if context.execution.created_at:` directly.
3. `[MODIFY]` `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]`
   - Read and append both static `context.profile.content_blocks` AND dynamic `context.profile_cache.section_syntheses` as a pure Dumb Painter.
4. `[MODIFY]` `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`
   - Append synthesized narrative paragraphs from `context.profile_cache.section_syntheses` (or `user_role_justification`) alongside the localized user role badge.
5. `[MODIFY]` `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
   - Clean up source formatting and ensure deterministic deduplication.
6. `[MODIFY]` `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`
   - Remove runtime `model_validate` try-catch loop; consume typed `XaiHighlightItem` instances directly from `context.profile_cache.xai_highlights`.
7. `[MODIFY]` `@[backend_v2/services/blueprint.py]`
   - Type `_target_block_hydrators` strictly as `dict[TargetBlockType, Callable[[AdapterContext], list[AnySduiBlock]]]`.
   - Index `_target_block_hydrators[target_k]` directly with native `TargetBlockType` keys.
   - Wrap lookup in localized `try...except KeyError:` logging RFC 7807 error and raising `AppException(VALIDATION_FAILED)`.
8. `[MODIFY]` `@[backend_v2/services/matrix_domain_parser.py]`
   - Replace raw string comparisons `display_scale == "normalized_100"` / `"custom"` with native `DisplayScale` enum members (`DisplayScale.NORMALIZED_100`, `DisplayScale.CUSTOM`).
9. `[NEW]` `@[backend_v2/models/prompts/synthesis_directives.py]`
   - Create SSOT module exporting `SYNTHESIS_MATHEMATICAL_ANCHORING_MANDATE`, `SYNTHESIS_VISUAL_STORYTELLING_MANDATE`, `SYNTHESIS_GRAPH_DIRECTIVES_XML`, and `ROW_EXPLANATION_MANDATE`.
10. `[MODIFY]` `@[backend_v2/models/prompts/__init__.py]`
    - Re-export all 4 prompt directive constants in `__all__`.
11. `[MODIFY]` `@[backend_v2/worker.py]`
    - Inject `SYNTHESIS_GRAPH_DIRECTIVES_XML` into `dynamic_ctx_parts` for graph section synthesis and `ROW_EXPLANATION_MANDATE` for row explanations.
12. `[MODIFY]` `@[backend_v2/seed/seed_data.json]`
    - Strip 6 dead-weight fields from all 12 layout synthesis objects and root synthesis.
    - Cleanse prompt blocks `blk_111122223333444a/b/c`, `blk_34def5d628ba4ed4`, and `blk_ad303690b26b413d` to pure Markdown headers preserving coaching philosophies without XML tags.
13. `[MODIFY]` `@[backend_v2/models/v2_core.py]`
    - Purge 6 dead-weight fields from `SynthesisConfigDTO` under `ConfigDict(strict=True, extra="forbid")`.
    - Type `RenderedSynthesisCache.xai_highlights: list[XaiHighlightItem]`.
14. `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]`
    - Purge 6 dead-weight fields from Dart `SynthesisConfigDTO` Freezed model.
15. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]`
    - Purge 6 dead-weight fields from Dart `SynthesisConfigDto` Freezed model.
16. `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]`
    - Add positive tests with bilingual `metric_mappings` (en/fi) and negative tests for missing metric mapping keys, missing name, and custom preface rendering.
17. `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]`
    - Add threshold boundary classification tests (80.0, 79.99, 50.0, 49.99) with dynamic `get_settings()` verification.
18. `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]`
    - Add tests for synthesized narrative append alongside user role badge.
19. `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]`
    - Update fixtures to instantiate typed `XaiHighlightItem` objects.
20. `[NEW]` `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]`
    - Create unit tests verifying prompt directive XML structure, immutability, and presence in `__all__`.
21. `[MODIFY]` `@[backend_v2/tests/unit/services/test_blueprint.py]`
    - Update test fixtures for `_target_block_hydrators` enum indexing and unmapped `TargetBlockType` KeyError negative test.

---

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; PRE-FLIGHT CHECK">
    <action>Verify workspace status. Check that Phase 2 is complete, test suites pass, and seed data backups are in place.</action>
    <validation>Run `uv run pytest backend_v2/tests/unit/test_settings.py` to verify baseline stability.</validation>
  </step>

  <step id="1" name="GLOBAL CONFIG SOVEREIGNTY: AUTHENTICITY ADAPTER">
    <action>Refactor `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]` to remove `AUTHENTICITY_THRESHOLDS`. Import `get_settings` at module level and dynamically resolve `get_settings().authenticity_threshold_high` and `get_settings().authenticity_threshold_low`.</action>
    <action>Update `@[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]` to test classification boundaries (80.0, 79.99, 50.0, 49.99) and negative cases.</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py --test`.</validation>
  </step>

  <step id="2" name="METADATA ADAPTER LOCALIZATION &amp; DUCK-TYPING ERADICATION">
    <action>Refactor `@[backend_v2/services/sdui/adapters/metadata_adapter.py]` to eradicate hardcoded Finnish strings, resolve dynamic labels via `context.profile.metric_mappings` with Fail-Fast key lookup, resolve title strictly from `context.profile.name`, access `context.profile.custom_preface`, and format `context.execution.created_at` without `isinstance` checks.</action>
    <action>Update `@[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]` with positive bilingual tests and negative tests for missing metric mapping keys.</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py --test`.</validation>
  </step>

  <step id="3" name="SDUI SYNTHESIS TEXT &amp; EXECUTIVE SUMMARY ADAPTER ENHANCEMENTS">
    <action>Refactor `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]` to render both static `context.profile.content_blocks` and dynamic `context.profile_cache.section_syntheses` as a pure Dumb Painter.</action>
    <action>Refactor `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]` to append synthesized narrative paragraphs from `context.profile_cache.section_syntheses` alongside the user role badge.</action>
    <action>Clean up `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` deterministic source deduplication.</action>
    <action>Update unit tests in `@[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]`.</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py --test`.</validation>
  </step>

  <step id="4" name="TARGET BLOCK DISPATCHER STRICTNESS &amp; DOMAIN PARSER ENUM ALIGNMENT">
    <action>Refactor `@[backend_v2/services/blueprint.py]`: type `_target_block_hydrators` strictly as `dict[TargetBlockType, Callable]`, index with native `TargetBlockType` keys, and wrap in `try...except KeyError:` logging RFC 7807 error and raising `AppException(VALIDATION_FAILED)`.</action>
    <action>Refactor `@[backend_v2/services/matrix_domain_parser.py]` to compare native `DisplayScale` enum members (`DisplayScale.NORMALIZED_100`, `DisplayScale.CUSTOM`) instead of raw string literals.</action>
    <action>Update unit test fixtures and negative KeyError tests in `@[backend_v2/tests/unit/services/test_blueprint.py]` and `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`.</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/test_blueprint.py --test`.</validation>
  </step>

  <step id="5" name="PROMPT DIRECTIVES SSOT &amp; WORKER DYNAMIC CONTEXT INJECTION">
    <action>Create [NEW] `@[backend_v2/models/prompts/synthesis_directives.py]` exporting `SYNTHESIS_MATHEMATICAL_ANCHORING_MANDATE`, `SYNTHESIS_VISUAL_STORYTELLING_MANDATE`, `SYNTHESIS_GRAPH_DIRECTIVES_XML`, and `ROW_EXPLANATION_MANDATE`.</action>
    <action>Re-export all 4 prompt directive constants in `@[backend_v2/models/prompts/__init__.py]`.</action>
    <action>Update `@[backend_v2/worker.py]` to inject `SYNTHESIS_GRAPH_DIRECTIVES_XML` into `dynamic_ctx_parts` for graph section synthesis and `ROW_EXPLANATION_MANDATE` for row explanations.</action>
    <action>Create [NEW] `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]` verifying XML structures and re-exports.</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/prompts/test_synthesis_directives.py --test`.</validation>
  </step>

  <step id="6" name="SEED DATA SANITIZATION &amp; LOCAL DATABASE RESEED GATE">
    <action>Create pre-mutation backup `backend_v2/seed/backups/seed_data_backup_p3.json`.</action>
    <action>Strip 6 dead-weight fields (`model_strategy`, `historical_context_mode`, `enable_pii_masking`, `allowed_exports`, `omit_empty_sections`, `allowed_mcp_tools`) from all 12 layout synthesis objects in `@[backend_v2/seed/seed_data.json]`.</action>
    <action>Cleanse prompt blocks `blk_111122223333444a`, `blk_111122223333444b`, `blk_111122223333444c`, `blk_34def5d628ba4ed4`, and `blk_ad303690b26b413d` in `seed_data.json` to Markdown headers preserving coaching philosophy without XML tags.</action>
    <action>Execute local database reseed: `uv run python backend_v2/seed/run_seed.py local` to sanitize TinyDB persistence before modifying Pydantic models in Step 7.</action>
    <validation>Verify exit code 0 on `uv run python backend_v2/seed/run_seed.py local`.</validation>
  </step>

  <step id="7" name="SYNTHESIS CONFIG DTO PURGE &amp; XAI HIGHLIGHTS STRICT TYPING">
    <action>Purge 6 dead-weight fields from `SynthesisConfigDTO` in `@[backend_v2/models/v2_core.py]` under `ConfigDict(strict=True, extra="forbid")`.</action>
    <action>Type `RenderedSynthesisCache.xai_highlights: list[XaiHighlightItem]` in `@[backend_v2/models/v2_core.py]`.</action>
    <action>Refactor `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]` to remove defensive runtime try-catch parsing.</action>
    <action>Purge 6 dead-weight fields from Dart Freezed models `@[client_app_v2/lib/features/studio/models/output_profile.dart]` and `@[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]`.</action>
    <action>Update test fixtures in `@[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]` and `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]`.</action>
    <validation>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/dtos/test_output_profile.py --test`.</validation>
  </step>

  <step id="8" name="CROSS-STACK COMPILATION &amp; FREEZED CODEGEN GATE">
    <action>Execute Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`.</action>
    <action>Run Flutter Studio tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`.</action>
    <validation>Verify 0 Dart analyzer errors and 100% Flutter tests pass green.</validation>
  </step>

  <step id="9" name="FULL BACKEND REGRESSION &amp; QUALITY GATE AUDIT">
    <action>Run global backend test suite: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Verify zero skipped tests in modified test modules and >=90% test coverage across target files.</action>
    <validation>All backend tests pass green (1450+ tests).</validation>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <rule>@[.agents\rules\03_seed_vault.md]</rule>
    <rule>@[.agents\rules\05_llm_architecture.md]</rule>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>client_app_v2/lib/features/studio/views/ — Do NOT modify decomposed view components in Phase 3</file>
    <file>backend_v2/services/orchestrator/prompt_compiler.py — FROZEN architectural cornerstone</file>
  </anti_targets>

  <dod_checklist>
    <item>`AUTHENTICITY_THRESHOLDS` deleted from `authenticity_adapter.py` and read dynamically from `get_settings()`.</item>
    <item>`MetadataAdapter` localized via `context.profile.metric_mappings` with zero hardcoded Finnish strings and zero duck-typing.</item>
    <item>`SynthesisTextAdapter` renders both `content_blocks` and `section_syntheses`.</item>
    <item>`ExecutiveSummaryAdapter` appends synthesized narrative paragraphs alongside user role badge.</item>
    <item>`blueprint.py` `_target_block_hydrators` strictly typed and indexed with native `TargetBlockType` keys.</item>
    <item>`matrix_domain_parser.py` compares native `DisplayScale` enum members.</item>
    <item>`synthesis_directives.py` SSOT created and re-exported in `prompts/__init__.py`.</item>
    <item>PromptBlocks `blk_111122223333444a/b/c`, `blk_34def5d628ba4ed4`, `blk_ad303690b26b413d` cleansed to Markdown headers in `seed_data.json`.</item>
    <item>6 dead-weight fields purged from `SynthesisConfigDTO` across Python and Dart models.</item>
    <item>`RenderedSynthesisCache.xai_highlights` typed as `list[XaiHighlightItem]`.</item>
    <item>Local database reseeded via `uv run python backend_v2/seed/run_seed.py local`.</item>
    <item>Freezed codegen executed and verified clean via `flutter_audit_loop.py`.</item>
    <item>Backend audit loop passes 100% green with >=90% coverage across modified files.</item>
  </dod_checklist>

  <validation_gate>
    <check>`uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py --test`</check>
    <check>`uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py --test`</check>
    <check>`uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py --test`</check>
    <check>`uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/prompts/test_synthesis_directives.py --test`</check>
    <check>`uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`</check>
    <check>`uv run python scripts/backend_audit_loop.py backend_v2 --test`</check>
  </validation_gate>
</execution_protocol>
```

