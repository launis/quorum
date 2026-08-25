<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

# EPIC 148: Domain Model SSOT & Presentation Localization Modernization

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
EPIC 148 standardizes and modernizes Quorum's domain data models and localization architecture across Python backend services, the SQLite/JSON seed vault, and the Flutter desktop client. The epic consolidates Chapters 2, 3, 5, and 6 of `docs/arkkitehtuurin_parannuskohteet.md` to:
1. Establish the **Epistemic Separation Paradigm** for theory grounding: prune redundant `EPISTEMIC ANCHOR:` prompt tails across all 13 matrix blocks in `seed_data.json`, format pure `<theory_context>` XML citations without raw URL token leakage during prompt compilation, and preserve structured `TheoryGrounding` metadata exclusively for UI/PDF presentation.
2. Eradicate redundant `default_locale` attributes across backend and frontend `I18nText` data models and 500 instances in `seed_data.json`, shifting language fallback resolution dynamically to execution context parameters (`target_locale`, with global fallback `"en"`).
3. Modernize `OutputProfile` and Server-Driven UI (SDUI) localization by migrating static UI dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`) out of the backend database into frontend `.arb` resource files, transforming `MetadataAdapter` into structured key-value envelopes, and replacing legacy V1 `layouts` arrays with strongly-typed `matrix_synthesis_groups`.
4. Execute the 5-phase **Atomic Migration Protocol** to ensure strict Pydantic V2 (`extra="forbid"`) and Flutter Freezed compatibility without silent fallbacks, duct-tape validators, or broken test fixtures.

### 1.2 Problem Statement & Root Cause Analysis
1. **Theory Grounding Dual Injection & Prompt Bloat (Luku 2)**: In `@[backend_v2/seed/seed_data.json#L336-L6900]`, epistemic and academic grounding anchors are duplicated across both `PromptBlock.ai_description` (as freeform `EPISTEMIC ANCHOR:` text blocks) and `PromptBlock.theory_grounding` (as structured `TheoryGrounding` DTOs). When `MatrixSensorPromptBuilder` compiles prompts, it injects both the raw text description and the structured object with raw URLs (`source_url`), triggering prompt duplication, URL token bloat, XML syntax corruption risks, and Single Source of Truth (SSOT) drift.
2. **`I18nText.default_locale` Redundancy (Luku 3)**: In `@[backend_v2/models/v2_core.py#L99-L189]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]`, and across 500 records in `seed_data.json`, every `I18nText` object hardcodes `"default_locale": "fi"`. This conflates static dictionary storage with dynamic runtime resolution, creates internal validation contradictions with the global `"en"` fallback rule, and bloats database payloads across 1300+ test fixtures.
3. **`OutputProfile` Presentation Drift & Dual-Axis Localization Conflicts (Luku 5)**: In `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `OutputProfile` persists hundreds of lines of static UI label translations in backend dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`). `MetadataAdapter` concatenates labels with values in Python strings, violating the "Dumb Painter" principle and creating localization drift against Flutter `.arb` files. Furthermore, `OutputProfile.layouts` retains obsolete V1 fields (`preset_view`, `text_delivery_mode`, `steps: []`) rather than declaring clean matrix synthesis groups.
4. **Fragility Under `extra="forbid"` (Luku 6)**: Pydantic V2 models enforce `strict=True` and `extra="forbid"`. Removing fields without an atomic multi-step migration script immediately causes cascading `ValidationError` failures across 1300+ test fixtures and corrupts local database state (`db_v2.json`).

---

## 2. Scope & File Modification Boundary

### 2.1 TARGET Files (Editable)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]` (Sanitize all 13 matrices by removing `EPISTEMIC ANCHOR:` tails; prune 500 instances of `default_locale`; prune `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels` from `OutputProfile`; replace `layouts` with `matrix_synthesis_groups`)
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L99-L189]` and `@[backend_v2/models/v2_core.py#L1146-L1267]` (Remove `default_locale` from `I18nText` and update `resolve()`; remove legacy `layouts` from `OutputProfile` and define `MatrixSynthesisGroup` domain model)
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]` (Format pure `<theory_context>\n{citation}\n</theory_context>` XML block, omitting raw URLs)
- `[MODIFY]` `@[client_app_v2/lib/shared/models/i18n_text.dart]` and generated `.freezed.dart` / `.g.dart` (Remove `defaultLocale` from Freezed model and update `get()` method)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]` and generated `.freezed.dart` / `.g.dart` (Update Freezed model: remove `metricMappings`, `matrixColumnLabels`, `userRoleMappings`, `extensionLabels`; replace `layouts` with `matrixSynthesisGroups`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/metadata_adapter.py]` (Refactor to emit structured key-value envelopes instead of concatenated localized strings)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` and `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]` (Consume `matrix_synthesis_groups` instead of legacy `layouts`)
- `[MODIFY]` `@[backend_v2/worker.py#L591-L1359]` (Update background synthesis job loop to iterate over `profile.matrix_synthesis_groups`)
- `[MODIFY]` `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]` (Ensure all structural UI labels for metadata, roles, and metrics exist in frontend resources)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]` (Update studio layout editor to bind to `matrix_synthesis_groups`)
- `[NEW]` `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]` (AST guardrail suite locking pure theory grounding invariants)
- `[NEW]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]` (AST guardrail suite asserting zero occurrences of `default_locale`, `EPISTEMIC ANCHOR:`, and legacy `layouts` dictionaries in seed vault)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]` (Update test assertions for pure `<theory_context>` XML formatting)
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_workflows.py]` (Migrate test fixtures to new `I18nText` and `OutputProfile` schemas)
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_layouts_tab_test.dart]` (Update Flutter widget test suite to match `matrixSynthesisGroups`)

### 2.2 CONTEXT Files (Read-Only)
- `@[backend_v2/models/v2_core.py#L192-L205]` (`TheoryGrounding` schema SSOT)
- `@[backend_v2/settings.py]` (Backend global configuration SSOT)
- `@[docs/arkkitehtuurin_parannuskohteet.md]` (Architectural Improvement Roadmap Reference)

---

## 3. Technical Debt Itemization & Pre-Implementation Remediation

Specifically and exhaustively, the following 12 technical debt items are identified for remediation:
1. **Duplicate Theory Anchors in Seed Vault**: All 13 matrix blocks in `seed_data.json` duplicate bibliographic text in `ai_description`, creating token bloat and risk of semantic drift.
2. **Raw JSON Injected in Static System Prompts**: `MatrixSensorPromptBuilder` calls `theory_grounding.model_dump_json()`, injecting raw JSON into system rule blocks.
3. **URL Token Bloat & Prompt Leakage**: Raw `source_url` strings are emitted in LLM prompt payloads rather than reserved exclusively for client UI rendering and PDF reports.
4. **Redundant `default_locale` in `I18nText`**: 500 `I18nText` blocks in `seed_data.json` declare `"default_locale": "fi"`, conflicting with runtime context-driven language selection.
5. **Static UI Dictionaries in Database**: `OutputProfile` contains `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, and `extension_labels` in backend persistence, violating Dual-Axis Localization.
6. **Backend String Concatenation in `MetadataAdapter`**: `MetadataAdapter` combines translated labels with values in Python strings, breaking the Dumb Painter paradigm.
7. **Obsolete V1 `layouts` Arrays**: `OutputProfile.layouts` retains deprecated fields (`preset_view`, `text_delivery_mode`, `steps: []`) instead of a focused `matrix_synthesis_groups` structure.
8. **Worker Couplings on `layouts`**: `worker.py` and SDUI adapters depend on `profile.layouts` for synthesis loop routing.
9. **Flutter Freezed Schema Drift**: `i18n_text.dart` and `output_profile.dart` Freezed models reflect deprecated fields, requiring regeneration via `build_runner`.
10. **Test Fixture Schema Drift**: 1300+ test assertions in `backend_v2/tests/` hardcode `default_locale` or legacy profile layout keys.
11. **Missing AST Guardrails for Seed Vault Purity**: The test suite lacks static AST assertions preventing re-introduction of `default_locale` or `EPISTEMIC ANCHOR:` tails.
12. **Unsynchronized Local Database State**: `db_v2.json` must be re-seeded atomically after `seed_data.json` mutations.

---

## 4. Architectural Impact & Compliance Matrix

### 4.1 Deprecations & Sunset List (`What We Will REMOVE`)
| Deprecated Symbol / Pattern | Location | Replacement / Disposition |
| :--- | :--- | :--- |
| `EPISTEMIC ANCHOR:` prompt tails | `@[backend_v2/seed/seed_data.json#L336-L6900]` | **PURGED**. Retained exclusively in structured `theory_grounding` field. |
| Raw `source_url` in LLM prompts | `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]` | **OMITTED** from LLM prompt payload; retained in DTOs for UI/PDF rendering. |
| `I18nText.default_locale` | `@[backend_v2/models/v2_core.py]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]` | **PURGED**. Replaced by dynamic runtime parameter `target_locale` with `"en"` fallback. |
| `OutputProfile.metric_mappings` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.matrix_column_labels` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.user_role_mappings` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.extension_labels` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.layouts` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by clean `matrix_synthesis_groups` domain model. |

### 4.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **Qualitative Coaching Philosophy (`prompt_preservation_mandate`)**: Prompt texts in `seed_data.json` (specifically `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections) are strictly preserved verbatim.
2. **Deterministic UI/PDF Provenance**: `PromptBlock.theory_grounding` retains full metadata (`theoretical_framework`, `academic_citation`, `grounding_type`, `source_url`) for Server-Driven UI (SDUI) and PDF report rendering.
3. **Pydantic V2 Strictness (`strict_pydantic_v2_rust`)**: All DTOs and models enforce `ConfigDict(strict=True, extra="forbid")`.
4. **Dual-Axis Localization SSOT**: Backend manages dynamic data translation; frontend manages static structural labels via `.arb` files.

---

## 5. Phased Implementation Plan

### Phase 1: Theory Grounding & Epistemic Anchor Sanitization (Luku 2)

#### Step 1.1: Backup Seed Vault (`vault_mutation_protocol`)
Ensure directory `backend_v2/seed/backups/` exists and execute backup command:
`New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_epic148_cleanup.json`

#### Step 1.2: Deterministic Seed Vault Sanitization across all 13 Matrix Blocks
Surgically sanitize the `ai_description` field across specifically and exhaustively all 13 matrices in `@[backend_v2/seed/seed_data.json#L336-L6900]`:
1. `blk_440a5fef9331451b` (matrix_toulmin): Remove `EPISTEMIC ANCHOR:\nToulmin, S. E. (2003)...`
2. `blk_f921c7c0989b47e8` (matrix_bloom): Remove `EPISTEMIC ANCHOR:\nAnderson, L. W., & Krathwohl...`
3. `blk_109dab5b6b3f403a` (matrix_kahneman): Remove `EPISTEMIC ANCHOR:\nKahneman, D. (2011)...`
4. `blk_53f32679aa514fcb` (matrix_goodhart): Remove `EPISTEMIC ANCHOR:\nStumborg, M. F., et al...`
5. `blk_fb15f8dcf23f4865` (matrix_archivist): Remove `EPISTEMIC ANCHOR:\nARMA International...`
6. `blk_c5804a9143c34cb1` (matrix_causal_analyst): Remove `EPISTEMIC ANCHOR:\nPearl, J. 'The Book of Why...`
7. `blk_b476f89fb732448c` (matrix_falsifier): Remove `EPISTEMIC ANCHOR:\nKarl Popper's Theory of Falsification...`
8. `blk_ff72c2d79edb4ebf` (matrix_judge): Remove `EPISTEMIC ANCHOR:\nW. Edwards Deming...`
9. `blk_6b8c766185294f7e` (matrix_xai_reporter): Remove `EPISTEMIC ANCHOR:\nDARPA XAI Program (2017)...`
10. `blk_80732a33fe1947ee` (matrix_taskguard): Remove `EPISTEMIC ANCHOR:\nAnchored in the OWASP Top 10...`
11. `blk_c3bc5f3eb8e74110` (matrix_causal_abductive): Remove `EPISTEMIC ANCHOR:\nAnchored in Judea Pearl's 'The Book of Why'...`
12. `blk_f6e286f050c94d60` (matrix_taskxai_clarity): Remove `EPISTEMIC ANCHOR:\nAnchored in Zachary C. Lipton's 'The Mythos of Model Interpretability'...`
13. `blk_22e3598e06414409` (matrix_epistemic_humility): Remove `EPISTEMIC ANCHOR:\nGrounded in Kahneman's Dual Process Theory...`

Preserve all `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections intact per `prompt_preservation_mandate`.

#### Step 1.3: Format Pure `<theory_context>` in `MatrixSensorPromptBuilder`
In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]`:
Refactor theory grounding injection in `MatrixSensorPromptBuilder.build_caching_prefix`:
Replace `ai_desc=matrix_context.theory_grounding.model_dump_json()` with pure citation XML formatting (excluding URL token bloat):
```python
if matrix_context and matrix_context.theory_grounding and matrix_context.theory_grounding.citation_reference:
    citation = matrix_context.theory_grounding.citation_reference.strip()
    if citation:
        theory_desc = f"<theory_context>\n{citation}\n</theory_context>"
        blocks.append(
            MatrixSensorPromptBuilder._create_ephemeral_block(
                block_id="blk_3333333333333333",
                category_id=PromptBlockCategory.SYSTEM_RULE,
                ai_desc=theory_desc,
            )
        )
```

#### Step 1.4: Unit Tests & Quality Gate for Phase 1
1. In `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]`: Update test assertions to verify `<theory_context>\n{citation}\n</theory_context>` pure citation XML structure without raw URLs.
2. Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py --test`.

---

### Phase 2: `I18nText.default_locale` Eradication (Luku 3)

#### Step 2.1: Python Domain Model Update (`v2_core.py`)
In `@[backend_v2/models/v2_core.py#L99-L189]`:
1. Remove `default_locale` field from `I18nText`.
2. Refactor `resolve()` method:
   ```python
   def resolve(self, target_locale: str | None = None, fallback_locale: str = "en") -> str:
       """Resolve text for target locale with fallback hierarchy."""
       if target_locale and target_locale in self.translations and self.translations[target_locale]:
           return self.translations[target_locale]
       if fallback_locale in self.translations and self.translations[fallback_locale]:
           return self.translations[fallback_locale]
       # Return first available translation if fallback missing
       for val in self.translations.values():
           if val:
               return val
       return ""
   ```

#### Step 2.2: Flutter Freezed Model Update (`i18n_text.dart`)
1. In `@[client_app_v2/lib/shared/models/i18n_text.dart]`:
   - Remove `defaultLocale` field from `I18nText` Freezed model.
   - Update `get(String? langCode, {String fallback = 'en'})` method to resolve with application context.
2. Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/shared/models/i18n_text.dart --build`.

#### Step 2.3: Deterministic Pruning of `default_locale` across 500 Instances in `seed_data.json`
Write and execute an atomic Python script in the scratch directory to strip all `"default_locale": "..."` keys from `backend_v2/seed/seed_data.json` while preserving all other keys.

#### Step 2.4: Test Fixtures Migration across 1300+ Test Cases
Write and execute an atomic regex/AST migration script to strip `default_locale` kwargs and dictionary entries from `backend_v2/tests/` fixtures.

#### Step 2.5: Quality Gate for Phase 2
Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/ --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/ --build`.

---

### Phase 3: `OutputProfile` Presentation Model & L10n SSOT (Luku 5)

#### Step 3.1: Modernize `OutputProfile` & Define `MatrixSynthesisGroup` in `v2_core.py`
In `@[backend_v2/models/v2_core.py#L1146-L1267]`:
1. Declare `MatrixSynthesisGroup(V2CoreBase)`:
   ```python
   class MatrixSynthesisGroup(V2CoreBase):
       """Logical group of matrices synthesized together into 2D visualizations or narratives."""
       id: str = Field(..., description="Unique group identifier")
       title: I18nText = Field(..., description="Localized group title")
       target_blocks: list[str] = Field(default_factory=list, description="Target matrix block IDs")
       synthesis_directive: str | None = Field(default=None, description="Optional synthesis directive override")
   ```
2. In `OutputProfile`:
   - Remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts`.
   - Add `matrix_synthesis_groups: list[MatrixSynthesisGroup] = Field(default_factory=list)`.

#### Step 3.2: Modernize Flutter `OutputProfile` Freezed Model
1. In `@[client_app_v2/lib/features/studio/models/output_profile.dart]`:
   - Declare `MatrixSynthesisGroup` Freezed model.
   - Update `OutputProfile` Freezed model to match backend schema.
2. Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.

#### Step 3.3: Refactor SDUI Adapters, Worker & Flutter Studio View
1. In `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`: Emit structured key-value blocks.
2. In `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` and `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`: Consume `profile.matrix_synthesis_groups`.
3. In `@[backend_v2/worker.py#L591-L1359]`: Iterate over `profile.matrix_synthesis_groups` for matrix synthesis execution.
4. In `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`: Bind to `matrixSynthesisGroups`.
5. In `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`: Ensure all static UI labels exist.

#### Step 3.4: Seed Vault `OutputProfile` Migration
Update `OutputProfile` records in `@[backend_v2/seed/seed_data.json#L9180-L9570]` to remove legacy dictionary mappings and migrate `layouts` to `matrix_synthesis_groups`.

---

### Phase 4: Atomic Verification, Seed Re-seeding & AST Guardrails (Luku 6)

#### Step 4.1: Re-seed Local Database
Verify JSON integrity and execute: `uv run python backend_v2/seed/run_seed.py local`.

#### Step 4.2: Create AST Guardrail Suites
1. Create [NEW] `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]`:
   - `test_seed_matrices_have_no_epistemic_anchor_in_ai_description`: 0 matrix blocks have `"EPISTEMIC ANCHOR:"`.
   - `test_seed_matrices_have_valid_theory_grounding`: All 13 matrix blocks have non-null `theory_grounding`.
   - `test_matrix_sensor_prompt_builder_ast_uses_pure_theory_citation`: AST confirms no `model_dump_json()` on `theory_grounding`.
2. Create [NEW] `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`:
   - `test_seed_has_no_default_locale`: 0 occurrences of `"default_locale"` in `seed_data.json`.
   - `test_seed_output_profile_has_no_legacy_dictionaries`: 0 occurrences of `metric_mappings`, `matrix_column_labels`, `user_role_mappings` in `OutputProfile`.
   - `test_seed_output_profile_uses_matrix_synthesis_groups`: Asserts `matrix_synthesis_groups` is present and non-empty.

#### Step 4.3: Full Audit Gate Verification
1. Run backend quality loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
2. Run Flutter quality loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

---

## 6. ISTQB Equivalence Partitions & Boundary Scenarios Matrix

| Scenario ID | Test Name | Input State | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **TC-TG-01** (Happy Path: Pure Citation) | `test_build_caching_prefix_with_context` | `TheoryGrounding(source_url="https://arma.org", citation_reference="ARMA Principles")` | Static prompt contains `<theory_context>\nARMA Principles\n</theory_context>` (no raw URL in prompt) |
| **TC-TG-02** (Boundary: Null Citation) | `test_build_caching_prefix_theory_grounding_none_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference=None)` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-03** (Boundary: Empty Citation) | `test_build_caching_prefix_theory_grounding_empty_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference="")` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-04** (Boundary: Whitespace-only) | `test_build_caching_prefix_theory_grounding_whitespace_only` | `TheoryGrounding(source_url="https://arma.org", citation_reference="   \n\t")` | Ephemeral block is not appended, avoiding whitespace-only tags |
| **TC-TG-05** (Boundary: URL Exclusion) | `test_build_caching_prefix_theory_grounding_omits_raw_urls` | `TheoryGrounding(source_url="https://secret-domain.org/doc", citation_reference="Valid Citation")` | Static prompt does NOT contain `"https://secret-domain.org"` (zero token bloat / URL leakage) |
| **TC-I18N-01** (Happy Path: Target Match) | `test_i18n_text_resolve_target_locale` | `I18nText(translations={"fi": "Käyttäjä", "en": "User"})`, `target_locale="fi"` | Returns `"Käyttäjä"` |
| **TC-I18N-02** (Fallback: English Default) | `test_i18n_text_resolve_fallback_en` | `I18nText(translations={"fi": "Käyttäjä", "en": "User"})`, `target_locale="sv"` | Returns `"User"` (fallback) |
| **TC-I18N-03** (Boundary: Missing Target & Fallback) | `test_i18n_text_resolve_first_available` | `I18nText(translations={"de": "Benutzer"})`, `target_locale="fr"` | Returns `"Benutzer"` (first non-empty value) |
| **TC-I18N-04** (Boundary: All Empty) | `test_i18n_text_resolve_all_empty` | `I18nText(translations={"fi": "", "en": ""})` | Returns `""` without raising exception |
| **TC-SDUI-01** (Metadata: Key-Value Output) | `test_metadata_adapter_emits_structured_keys` | Context with `user_name="Matti Meikäläinen"` | SDUI payload contains `{key: "user", value: "Matti Meikäläinen"}` without hardcoded Finnish label |
| **TC-SDUI-02** (Synthesis Groups: Group Dispatch) | `test_worker_iterates_matrix_synthesis_groups` | Profile with 2 `MatrixSynthesisGroup` objects | Emits 2 discrete synthesis tasks targeted at group member matrices |
| **TC-AST-10** (AST Guardrail: Epistemic Anchor Purge) | `test_seed_matrices_have_no_epistemic_anchor_in_ai_description` | `seed_data.json` | 0 occurrences of `EPISTEMIC ANCHOR:` across all 13 matrices |
| **TC-AST-11** (AST Guardrail: Default Locale Purge) | `test_seed_has_no_default_locale` | `seed_data.json` | 0 occurrences of `"default_locale"` across entire seed vault |
| **TC-AST-12** (AST Guardrail: OutputProfile Clean Dictionaries) | `test_seed_output_profile_has_no_legacy_dictionaries` | `seed_data.json` | 0 occurrences of legacy translation dictionaries in OutputProfile |

---

## 7. Definition of Done (DoD) & Verification Plan

### 7.1 Definition of Done (DoD) Checklist
- [ ] `seed_data.json` backup recorded in `backend_v2/seed/backups/`.
- [ ] All 13 matrix blocks in `seed_data.json` sanitized by removing duplicate `EPISTEMIC ANCHOR:` tails; qualitative prompt definitions preserved verbatim.
- [ ] `MatrixSensorPromptBuilder.build_caching_prefix` formats pure `<theory_context>\n{citation}\n</theory_context>` XML block, omitting raw URLs from the LLM prompt.
- [ ] `default_locale` removed from `I18nText` in `backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart`.
- [ ] 500 occurrences of `"default_locale"` pruned from `backend_v2/seed/seed_data.json`.
- [ ] 1300+ test fixtures migrated in `backend_v2/tests/` to eliminate `default_locale`.
- [ ] `OutputProfile` modernized: `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` replaced with `matrix_synthesis_groups`.
- [ ] `MetadataAdapter`, `MatrixGraphsAdapter`, `MatrixSummaryTableAdapter`, and `worker.py` refactored to consume `matrix_synthesis_groups`.
- [ ] Flutter Freezed models generated via `build_runner` and Studio profile tab updated.
- [ ] Local test database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
- [ ] AST guardrails implemented and passing in `test_ast_theory_grounding_guardrails.py` and `test_seed_architectural_guardrails.py`.
- [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- [ ] Full Flutter audit loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

### 7.2 Verification Execution Commands
```powershell
# 1. Run Unit Tests for Theory Grounding & I18nText
uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py

# 2. Run AST Guardrail Suites
uv run pytest backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py backend_v2/tests/unit/test_seed_architectural_guardrails.py

# 3. Run Backend Quality Loop
uv run python scripts/backend_audit_loop.py backend_v2 --test

# 4. Run Flutter Quality Loop
uv run python scripts/flutter_audit_loop.py client_app_v2 --build
```

---

## 8. Required Context & Governance (Rules & KI Registry)

```xml
<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>
```
