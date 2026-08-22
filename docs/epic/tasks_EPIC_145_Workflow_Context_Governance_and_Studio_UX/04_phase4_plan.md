# Phase 4: Studio Workflow & Step Blueprint UX Restructuring (3-Zone Management & Core Protection)

**Overview:** Restructures Studio Workflow Builder step view into 3 distinct zones (Zone A Input Anchor, Zone B Dynamic Specialists, Zone C Pipeline Funnel Anchors), enforces system core protection in Step Blueprint Library, adds dual-axis localized ARB strings, and eliminates hardcoded Finnish text, manual substring clippings, and magic numbers.
**Source:** @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L193-L251] Phase 4: Studio Workflow & Step Blueprint UX Restructuring (3-Zone Management & Core Protection)
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb#L1075-L1125]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb#L1620-L1670]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L1-L335]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L108-L140]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L219-L295]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L940-L1195]
- [NEW] `@[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify that backend services, models, seed data, and APIs are fully functional and pass all quality gates.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true for Flutter studio workflow views and step builder views.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Localized ARB strings (specifically and exhaustively 18 keys) added to `app_fi.arb` and `app_en.arb` for 3-zone workflow management and core badges.
    - [ ] Flutter localization regenerated cleanly via `flutter gen-l10n`.
    - [ ] `WorkflowStepCard` displays 3 distinct zones with categorized sections ($inputs.* source materials vs $steps.* prior step reports), localized explanatory text, and zero hardcoded Finnish strings.
    - [ ] Blueprint dropdown in `WorkflowStepCard` filters out system core blueprints (`is_system_core == false`) for Zone B specialist steps, and is disabled/locked for Zone A (Step 1) and Zone C (Steps N+1..N+3) system anchors.
    - [ ] Step deletion is hidden/disabled for protected system core steps in `WorkflowStepCard` and `StepBuilderView`.
    - [ ] `WorkflowStepCard` modernizes `getBlueprintLabel` with `bp.name.get(locale)` and replaces manual `substring(0, 15)` clippings with `TextOverflow.ellipsis`.
    - [ ] `step_builder_view.dart` removes hardcoded hex colors (success snackbar `Color(0xFF2E7D32)`, delete icon `Color(0xFFD32F2F)`, drag indicator `Color(0xFF9E9E9E)`), uses localized snackbar error message `l10n.studioStepBuilderModelStrategyRequired`, and displays `studioSystemCoreBadge` with locked execution type and hook for system core steps.
    - [ ] Mandatory quality gates enforced in `StepBuilderView` for saving LLM specialist blueprints: requires at least one Role Block and a valid Model Strategy.
    - [ ] Comprehensive unit tests created in `client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart` (5 positive + 2 negative ISTQB partitions covering 3-zone rendering, blueprint filtering, delete lock, and localized labels).
    - [ ] Flutter audit loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/step_builder_view.dart --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
  </required_context_rules>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT hardcode user-facing strings or hex colors in Flutter widgets per `no_magic_strings_l10n` and `design_token_absolute_rule`.
    - Do NOT bypass Riverpod provider patterns or use `ref.read` inside `build()`.
    - Do NOT mutate domain models in-place or introduce fallback chains on missing translations.
    - Do NOT modify backend Python domain code in Phase 4.
  </anti_targets>

  <step id="1" name="Dual-Axis ARB Localization Expansion">
    <action>In @[client_app_v2/lib/l10n/app_fi.arb#L1075-L1125] and @[client_app_v2/lib/l10n/app_en.arb#L1620-L1670], add the 18 localized ARB keys specified in the Epic:
      1. `studioWorkflowTaskProfileTitle`: `"Tehtäväprofiili (Kognitiivinen rooli)"` / `"Task Profile (Cognitive Role)"`
      2. `studioWorkflowExecutionOrderTitle`: `"Suoritusjärjestys & Riippuvuudet"` / `"Execution Order & Dependencies"`
      3. `studioWorkflowExecutionOrderSubtitle`: `"Käynnistyy vasta kun valitut edeltävät vaiheet ovat valmistuneet:"` / `"Runs only after the following prior steps complete:"`
      4. `studioWorkflowStep1IngestionTitle`: `"Syötenäytöllä määritetyt raakatiedostot (PDF, DOCX)"` / `"Raw Source Documents from Input Screen (PDF, DOCX)"`
      5. `studioWorkflowStep1IngestionSubtitle`: `"Tämä vaihe lukee annetut raakadokumentit ja pilkkoo ne strukturoiduiksi todisteiksi ja atomeiksi."` / `"This step ingests raw documents and decomposes them into structured evidence and atoms."`
      6. `studioWorkflowStep1OutputBadge`: `"✨ Muuntaa tiedostot puretuiksi atomeiksi loppuketjulle."` / `"✨ Deconstructs files into atoms and citations for the pipeline."`
      7. `studioWorkflowAtomicScopeTitle`: `"Atomisoidut aineistot (Valitse analysoitavat sisällöt)"` / `"Atomized Materials (Select Analyzed Contents)"`
      8. `studioWorkflowAtomicScopeSubtitle`: `"Syötenäytöllä määritettyjen dokumenttien puretut atomit ja sitaatit (raakatiedostoja ei raahata mukana):"` / `"Decomposed atoms and citations from input screen documents (raw files are excluded):"`
      9. `studioWorkflowPriorStepsTitle`: `"Edeltävien askeleiden tekstiyhteenvedot (Valinnainen)"` / `"Prior Step Text Summaries (Optional)"`
      10. `studioWorkflowPriorStepsSubtitle`: `"Valitse vain jos agentin pitää lukea laaja sanallinen analyysi. Strukturoitu data ja havainnot siirtyvät aina automaattisesti."` / `"Enable only if this agent needs to read the narrative analysis. Structured findings are forwarded automatically."`
      11. `studioWorkflowZoneCAutoTitle`: `"Automaattinen järjestelmäankkuri (Suojattu)"` / `"Automated System Anchor (Protected)"`
      12. `studioWorkflowXaiReporterAggregateBadge`: `"⚡ Automaattinen koonti: Kokoaa automaattisesti kaikki yllä määritellyt työnkulun asiantuntijat."` / `"⚡ Automatic Aggregation: Automatically collects all active workflow specialists above."`
      13. `studioWorkflowXaiReporterPayloadDesc`: `"📑 Yhdistetty tilasyöte ($steps): Tämä askel lukee ja ristiinanalysoi kaikkien aktiivisten asiantuntijoiden havainnot ja todisteet. Raakatiedostoja ei tarvita."` / `"📑 Consolidated State Stream ($steps): This step ingests and cross-analyzes all active specialist findings. Raw files are excluded."`
      14. `studioSystemCoreBadge`: `"🔒 Järjestelmän perusaskel (Suojattu)"` / `"🔒 System Core Step (Protected)"`
      15. `studioStepBuilderModelStrategyRequired`: `"Tekoälymalli (Model Strategy) on pakollinen LLM-askelille."` / `"Model Strategy is required for LLM steps."`
      16. `studioWorkflowInputPrefix`: `"Syöte: {name}"` with `@studioWorkflowInputPrefix` placeholders `{ "name": { "type": "String" } }` / `"Input: {name}"`
      17. `studioWorkflowStepPrefix`: `"Askel: {name}"` with `@studioWorkflowStepPrefix` placeholders `{ "name": { "type": "String" } }` / `"Step: {name}"`
      18. `studioWorkflowNoSelectableInputs`: `"Ei valittavia syötteitä tai riippuvuuksia."` / `"No selectable inputs or dependencies available."`</action>
    <action>Execute Flutter localization build: `cd client_app_v2; flutter gen-l10n` to regenerate `AppLocalizations` classes.</action>
  </step>

  <step id="2" name="WorkflowStepCard 3-Zone Restructuring & Tech Debt Elimination">
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L1-L335], refactor `WorkflowStepCard` to implement the 3-Zone Architecture:
      1. Eliminate hardcoded Finnish strings:
         - Replace `'Syöte: $labelText'` at line 225 with `l10n.studioWorkflowInputPrefix(labelText)`.
         - Replace `'Askel: $labelStr'` at line 279 with `l10n.studioWorkflowStepPrefix(labelStr)`.
         - Replace `'Ei valittavia syötteitä tai riippuvuuksia.'` at line 308 with `l10n.studioWorkflowNoSelectableInputs`.
      2. Modernize `getBlueprintLabel(String stepId)`:
         - Replace manual fallback chain `bp.name.translations['fi'] ?? bp.name.translations['en'] ?? ''` at lines 59-61 with `bp.name.get(Localizations.localeOf(context).languageCode)` on `I18nText`.
      3. Eliminate manual string truncation `substring(0, 15)`:
         - Replace `prevId.length > 15 ? '${prevId.substring(0, 15)}...' : prevId` at lines 180-182 and 272-274 with `Text(displayLabel, overflow: TextOverflow.ellipsis)` and `Text(labelStr, overflow: TextOverflow.ellipsis)` per `horizontal_overflow_prevention`.
      4. Implement Zone-based Rendering Logic:
         - Determine the active zone for the step card:
           - **Zone A**: `index == 0` (Input Processing `sp_db849f9790984585`).
           - **Zone C**: Any step where the selected blueprint has `isSystemCore == true` AND `index > 0` (specifically and exhaustively: XAI Reporter `sp_192910b5f5a34c79`, Scoring Engine `sp_d245365e4a274b9e`, Synteesin Generointi `sp_7a8b9c0d1e2f3a4b`).
           - **Zone B**: All remaining steps (Cognitive Specialists, `index > 0` and `isSystemCore == false`).
         - **Zone A (Input Processing - Step 1)**:
           - Header: Delete button 🗑 is HIDDEN/DISABLED.
           - Blueprint Selector: Locked displaying `studioSystemCoreBadge` (`🔒 Järjestelmän perusaskel (Suojattu)`).
           - Body: Source documents container ($inputs.*) with `studioWorkflowStep1IngestionTitle` and `studioWorkflowStep1IngestionSubtitle`, plus `studioWorkflowStep1OutputBadge`.
         - **Zone B (Cognitive Specialists - Steps 2..N)**:
           - Header: Delete button 🗑 enabled.
           - Blueprint Selector: Filtered dropdown displaying EXCLUSIVELY non-core blueprints (`blueprints.where((bp) => !bp.isSystemCore)`).
           - Body:
             - Execution Order & Dependencies with `FilterChip` selection and cycle prevention.
             - Categorized Section 1: Atomized Materials ($inputs.*) with `studioWorkflowAtomicScopeTitle` and `studioWorkflowAtomicScopeSubtitle`.
             - Categorized Section 2: Prior Step Reports ($steps.*) with `studioWorkflowPriorStepsTitle` and `studioWorkflowPriorStepsSubtitle`.
         - **Zone C (Pipeline Funnel Anchors - Steps N+1..N+3)**:
           - Header: Delete button 🗑 is HIDDEN/DISABLED.
           - Blueprint Selector: Locked displaying `studioSystemCoreBadge` and `studioWorkflowZoneCAutoTitle`.
           - Body: **Zero manual input mutations**.
             - For XAI Reporter (`sp_192910b5f5a34c79`): Render `studioWorkflowXaiReporterAggregateBadge` and `studioWorkflowXaiReporterPayloadDesc` along with the dynamically collected list of active Zone B specialists ($steps).
             - For Scoring Engine (`sp_d245365e4a274b9e`): Render automated CDM calculation badge.
             - For Synteesin Generointi (`sp_7a8b9c0d1e2f3a4b`): Render headless state sealing badge into Tripartite Phase 2.</action>
    <demolish>REMOVE: Monolithic input mappings container and hardcoded Finnish strings in `workflow_step_card.dart#L204-L328`. REPLACE WITH: 3-Zone categorized containers.</demolish>
  </step>

  <step id="3" name="StepBuilderView System Core Protection &amp; Quality Gates">
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L108-L140], @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L219-L295], and @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L940-L1195]:
      1. Design Token Absolute Rule (Hex Color Elimination):
         - In `saveStep()` at line 252, remove hardcoded `backgroundColor: const Color(0xFF2E7D32)` from the success `SnackBar`, allowing it to inherit themed styling from `Theme.of(context).snackBarTheme` per `design_token_absolute_rule`.
         - In `_buildPreHookCard`, `_buildPostHookCard`, and `_buildCriteriaBlockCard` at lines 944, 986, 1031, 1091, 1126, 1186:
           - Replace hardcoded `color: Color(0xFFD32F2F)` on delete `IconButton` with `color: Theme.of(context).colorScheme.error`.
           - Replace hardcoded `color: Color(0xFF9E9E9E)` on drag indicator `Icon` with `color: Theme.of(context).colorScheme.onSurfaceVariant`.
      2. Localized Validation Error:
         - At line 237, replace hardcoded snackbar error text `'Model Strategy (Tekoälymalli) on pakollinen LLM-askelille.'` with `l10n.studioStepBuilderModelStrategyRequired`.
      3. System Core Protection (`payload.isSystemCore == true`):
         - In the AppBar actions at lines 285-294: Hide/disable the Delete action 🗑 when `payload.isSystemCore` is true.
         - Display the `studioSystemCoreBadge` (`🔒 Järjestelmän perusaskel (Suojattu)`) in the configuration header.
         - Lock the execution type (`logic` vs `llm`), hook name (specifically `apply_scoring_logic` for Scoring Engine), and expected input signatures to prevent engine disruption.
      4. Mandatory Quality Gates for Specialist Blueprints:
         - In `saveStep()`: When saving an LLM step (`payload is NodeStrategyLlm`), if `payload.isSystemCore == false`, require that `payload.roleBlockId` is not null/empty (or at least one criteria block / persona is configured) and `payload.modelStrategy` is not empty. If missing, show a localized validation error via SnackBar and abort save.</action>
    <demolish>REMOVE: `backgroundColor: const Color(0xFF2E7D32)` at @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L252] and hardcoded hex colors `Color(0xFFD32F2F)` / `Color(0xFF9E9E9E)` at @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L940-L1195]. REPLACE WITH: Themed SnackBar and `Theme.of(context).colorScheme` tokens.</demolish>
  </step>

  <step id="4" name="Flutter Quality Gate &amp; Unit/Widget Verification">
    <action>In [NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart], implement comprehensive widget unit tests (5 positive + 2 negative ISTQB partitions):
      1. Positive: Zone A rendering for Step 1 (`index == 0`) hides delete button, locks blueprint selector with `studioSystemCoreBadge`, and renders `$inputs.*` raw documents deconstruction badge.
      2. Positive: Zone B rendering for Step 2+ specialist steps renders delete button, filtered blueprint dropdown (excluding system core blueprints), dependency chips, and dual categorized input sections.
      3. Positive: Zone C rendering for Step N+1..N+3 system anchors hides delete button, locks blueprint selector, and displays automated aggregation badges with zero manual inputs.
      4. Positive: `getBlueprintLabel` correctly resolves localized name from `I18nText` via `bp.name.get(locale)` without manual fallback chains.
      5. Positive: Long step and blueprint identifiers render with `TextOverflow.ellipsis` without triggering horizontal layout overflow assertion errors.
      6. Negative ISTQB: Zone B blueprint dropdown assertion verifies that system core blueprints (`isSystemCore == true`) are never selectable for specialist steps.
      7. Negative ISTQB: Delete callback is disabled/untriggered when attempting deletion on Step 1 (Zone A) or System Core Step (Zone C).</action>
    <action>Execute Flutter Audit Loop on modified files:
      `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test`
      `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/step_builder_view.dart --test`</action>
    <action>Run existing Studio Widget tests:
      `uv run flutter test client_app_v2/test/features/studio/views/step_builder_view_dropdown_test.dart`
      `uv run flutter test client_app_v2/test/features/studio/models/workflow_test.dart`
      `uv run flutter test client_app_v2/test/models/domain_parity_test.dart`
      (and run [NEW] `uv run flutter test client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart`)</action>
  </step>

  <validation_gate>
    <action>Execute Flutter Audit Loop on all modified studio files: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test`</action>
    <action>Verify zero warnings, 0 type errors, 0 l10n missing keys, and 100% green widget tests.</action>
  </validation_gate>
</execution_protocol>
```

