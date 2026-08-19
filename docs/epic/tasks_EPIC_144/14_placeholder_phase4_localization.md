# Phase 4: Localization Synchronization & Freezed Validation

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Tracker:** `@[docs\epic\EPIC_144_tracker.md]`
**Source:** Epic Phase 4 "Localization & Accessibility" (L609-L630), Requirements R73, R74, R75, and Modernity Violations V1, V15.

---

## 1. Objective & Scope

Complete bilingual (English + Finnish) localization using `.arb` compile-time dictionaries for all Studio Output Profile UI elements, eradicate all magic strings and hardcoded labels across the modernized 3-tab views and 10 block card builders, enforce strict Backend Enum `@property l10n_key` adapter mapping in Python, and execute the final dead-weight field purge for `SynthesisConfigDTO` across both Python Pydantic and Dart Freezed models with full code generation and parity verification.

### Target Files:
- `[MODIFY]` `@[backend_v2/models/enums.py#L69-L79]`
- `[MODIFY]` `@[backend_v2/models/enums.py#L602-L608]`
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L1071-L1108]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py#L276]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY]` `@[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]`
- `[MODIFY]` `@[client_app_v2/lib/l10n/app_en.arb]`
- `[MODIFY]` `@[client_app_v2/lib/l10n/app_fi.arb]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/models/output_profile_test.dart]`

---

## 2. Architectural Protocol & Invariants

```xml
<execution_protocol>
  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/services/orchestrator/prompt_compiler.py — Frozen architectural cornerstone</file>
    <file>backend_v2/seed/seed_data.json — Sanitized in Phase 0 &amp; 3, do NOT mutate in Phase 4</file>
    <file>backend_v2/settings.py — Configured in Phase 0 &amp; 3</file>
  </anti_targets>

  <step id="0" name="Strategic Alignment Check &amp; Baseline Verification">
    <action>Verify that Phase 3 is signed off in tracker, git workspace is clean, and test baseline is green.</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2 --test</command>
    <command>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --test</command>
  </step>

  <step id="1" name="Backend Enum l10n_key Adapters &amp; Parity Alignment">
    <constraint invariant="strict_enum_l10n_mapping">
      Define `@property def l10n_key(self) -> str:` inside all backend Enum classes that map to UI presentation using explicit static dictionary mapping.
      Do NOT use string manipulation methods (specifically `.lower()` or `.split('_')` or `f"..."`).
    </constraint>
    <action>In `@[backend_v2/models/enums.py#L602-L608]`, add `@property def l10n_key(self) -> str:` to `ScoringStrategy`:
      ```python
      @property
      def l10n_key(self) -> str:
          """Explicit mapping to Frontend ARB camelCase translation keys."""
          mapping = {
              ScoringStrategy.WATERFALL: "strategyKoearvostelu",
              ScoringStrategy.AVERAGE: "strategyLineaarinenKeskiarvo",
              ScoringStrategy.WEIGHTED_AVERAGE: "strategyPainotettuKeskiarvo",
              ScoringStrategy.PURE_MATH: "strategyPuhdasMatematiikka",
          }
          return mapping.get(self, "")
      ```
    </action>
    <action>In `@[backend_v2/models/enums.py#L69-L79]`, refactor `DisplayScale.l10n_key` to use explicit dictionary mapping:
      ```python
      @property
      def l10n_key(self) -> str:
          """Explicit mapping to Frontend ARB camelCase translation keys."""
          mapping = {
              DisplayScale.ORIGINAL: "displayScaleOriginal",
              DisplayScale.CUSTOM: "displayScaleCustom",
              DisplayScale.NORMALIZED_100: "displayScaleNormalized100",
          }
          return mapping.get(self, "")
      ```
    </action>
    <action>In `@[backend_v2/tests/unit/test_enum_parity.py]`, add unit test `test_enum_l10n_keys()` verifying that every member of `DisplayScale`, `ScoringStrategy`, and `XaiExtensionType` resolves to a non-empty string and matches the corresponding ARB key.</action>
  </step>

  <step id="2" name="SynthesisConfigDTO Dead-Weight Purge in Python &amp; Dart Freezed Models">
    <constraint invariant="the_no_legacy_mandate">
      Purge all 6 dead-weight layout-level fields from both Python Pydantic and Dart Freezed models: `model_strategy`, `historical_context_mode`, `enable_pii_masking`, `allowed_exports`, `omit_empty_sections`, `allowed_mcp_tools`.
    </constraint>
    <action>In `@[backend_v2/models/v2_core.py#L1071-L1108]`, refactor `SynthesisConfigDTO` to retain specifically and exhaustively:
      - `system_prompt: str | None = Field(default=None, description="Optional system prompt overriding default synthesis.")`
      - `synthesis_block_id: str | None = Field(default=None, description="Optional explicit reference to the extraction block UUID that generates the global synthesis.")`
      - `row_explanations_block_id: str | None = Field(default=None, description="Optional explicit reference to the extraction block UUID that generates row explanations.")`
      - `length_constraint: int | None = Field(default=None, description="Length constraint for the synthesized text.")`
      - `preamble_text: I18nText | None = Field(default=None, description="Multilingual preamble text added before synthesis.")`
      - `tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")`
    </action>
    <action>In `@[backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py#L276]`, update test fixture from `SynthesisConfigDTO(enable_pii_masking=False)` to `SynthesisConfigDTO()`.</action>
    <action>In `@[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]`, refactor `SynthesisConfigDto` to retain specifically and exhaustively:
      - `systemPrompt: String?`
      - `synthesisBlockId: String?`
      - `rowExplanationsBlockId: String?`
      - `lengthConstraint: int?`
      - `preambleText: I18nText?`
      - `toneInstruction: I18nText?`
      Eradicate `@Default` parameters and imports of dead fields (`HistoricalContextMode`).
    </action>
    <action>In `@[client_app_v2/lib/features/studio/models/output_profile.dart]`, refactor `SynthesisConfigDTO` to match the exact same 6 functional fields with `@JsonSerializable(disallowUnrecognizedKeys: true)`.</action>
  </step>

  <step id="3" name="Bilingual .arb Key Additions">
    <constraint invariant="structural_localization_axis">
      All UI text, tab labels, card headers, helper tooltips, and static buttons MUST be registered in `app_en.arb` and `app_fi.arb`. Parameterized keys MUST include `@key` metadata blocks with type definitions.
    </constraint>
    <action>In `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`, add the following complete key catalog:
      - Tab Titles:
        - `profileTabGeneral`: "General" / "Yleiset"
        - `profileTabScoring`: "Scoring & XAI" / "Pisteytys & XAI"
        - `profileTabReportStructure`: "Report Structure" / "Raportin rakenne"
      - Block Card Titles:
        - `blockMetadataTitle`: "Report Metadata" / "Raportin metatiedot"
        - `blockExecutiveSummaryTitle`: "Executive Summary" / "Johdon tiivistelmä"
        - `blockSynthesisTextTitle`: "Synthesis & Narrative Text" / "Synteesi ja narratiiviteksti"
        - `blockMatrixGraphsTitle`: "Matrix Visualizations & Graphs" / "Matriisivisualisoinnit ja kaaviot"
        - `blockAiExtensionsTitle`: "XAI Highlights & Extensions" / "XAI-korostukset ja laajennukset"
        - `blockPenaltiesTitle`: "Penalties & Deductions" / "Rangaistukset ja vähennykset"
        - `blockMatrixSummaryTitle`: "Matrix Summary Table" / "Matriisiyhteenvetotaulukko"
        - `blockVarianceTitle`: "Variance Validation" / "Varianssivalidointi"
        - `blockAuthenticityTitle`: "Authenticity Evaluation" / "Autenttisuuden arviointi"
        - `blockBibliographyTitle`: "Bibliography & Sources" / "Lähdeluettelo ja viitteet"
        - `blockGlobalScoreTitle`: "Global Score" / "Kokonaistulos"
        - `blockAuditTrailTitle`: "Audit Trail" / "Auditointijälki"
        - `blockJargonRatioTitle`: "Jargon & Clarity Ratio" / "Ammattikieli- ja selkeyssuhde"
      - Block Card Subtitles:
        - `blockMetadataSubtitle`: "Execution timestamps, organization info, and engine parameters" / "Suoritusleimat, organisaatiotiedot ja moottorin parametrit"
        - `blockExecutiveSummarySubtitle`: "Global multi-step synthesis and management summary" / "Koko työnkulun laajuinen synteesi ja johdon yhteenveto"
        - `blockSynthesisTextSubtitle`: "Executive synthesis narratives, LLM summaries, and section preambles" / "Synteesikertomukset, tekoäly-yhteenvedot ja osiojohdannot"
        - `blockMatrixGraphsSubtitle`: "1D Metrics, 2D Comparisons, 3D Matrices, and Text-Only matrix presentations" / "1D-mittarit, 2D-vertailut, 3D-matriisit ja tekstiesitykset"
        - `blockAiExtensionsSubtitle`: "Explainable AI callouts, justifications, tips, and citations" / "Selitettävän tekoälyn nostot, perustelut, vinkit ja viitteet"
        - `blockPenaltiesSubtitle`: "Automated scoring deductions and compliance penalties" / "Automaattiset pistevähennykset ja sääntöjenmukaisuusrangaistukset"
        - `blockMatrixSummarySubtitle`: "Tabular overview of matrix evaluations, atomic breakdown, and scores" / "Taulukkomuotoinen katsaus matriisiarviointeihin, atomijakaumaan ja pisteisiin"
        - `blockVarianceSubtitle`: "Inter-rater variance and statistical confidence bounds" / "Arvioijien välinen varianssi ja tilastolliset luottamusvälit"
        - `blockAuthenticitySubtitle`: "Source document authenticity and cognitive manipulation checks" / "Lähdeaineiston aitous ja kognitiivisen manipulaation tarkistukset"
        - `blockBibliographySubtitle`: "Printable citations, sources, and verified references section" / "Tulostettavat viittaukset, lähteet ja todennetut viitteet"
        - `blockGlobalScoreSubtitle`: "Aggregated final scoring card and benchmark metrics" / "Yhdistetty loppupistekortti ja vertailulukuarvot"
        - `blockAuditTrailSubtitle`: "Forensic event logs and chronological execution trace" / "Oikeudelliset tapahtumalokit ja aikajärjestyksessä oleva suoritusjälki"
        - `blockJargonRatioSubtitle`: "Linguistic clarity metrics and domain jargon density" / "Kielellisen selkeyden mittarit ja toimialajargonin tiheys"
      - Builder &amp; Layout UI:
        - `reportVisualBlocksHeader`: "Report Visual Blocks" / "Raportin visuaaliset lohkot"
        - `activeBlocksCount`: "{count} active" / "{count} aktiivisena" (with `@activeBlocksCount` metadata defining `int count`)
        - `availableBlocksHeader`: "Available Blocks (Click to enable)" / "Käytettävissä olevat lohkot (Klikkaa ottaaksesi käyttöön)"
        - `noGraphLayoutsDefined`: "No graph layouts defined yet. Click \"+ Add Graph\" below to add a 1D, 2D, or 3D visualization." / "Kaaviolohkoja ei ole vielä määritetty. Klikkaa alta \"+ Lisää kaavio\" luodaksesi 1D-, 2D- tai 3D-visualisoinnin."
        - `addGraphButton`: "Add Graph" / "Lisää kaavio"
        - `graphTitleDefault`: "Graph #{index} ({preset})" / "Kaavio #{index} ({preset})" (with `@graphTitleDefault` metadata defining `int index`, `String preset`)
        - `graphTitleLabel`: "Graph Title" / "Kaavion otsikko"
        - `axisXPrimary`: "X-Axis (Primary)" / "X-akseli (Ensisijainen)"
        - `axisYComparison`: "Y-Axis (Comparison)" / "Y-akseli (Vertailu)"
        - `axisZDepth`: "Z-Axis (Depth)" / "Z-akseli (Syvyys)"
        - `selectBlockHint`: "Select block..." / "Valitse lohko..."
        - `alreadySelectedOnOtherAxis`: "{label} (Already selected on other axis)" / "{label} (Valittu jo toiselle akselille)" (with `@alreadySelectedOnOtherAxis` metadata defining `String label`)
      - Preset View Labels:
        - `presetView1d`: "1D Table" / "1D-taulukko"
        - `presetView2d`: "2D Grid" / "2D-ruudukko"
        - `presetView3d`: "3D Matrix" / "3D-matriisi"
        - `presetViewTextOnly`: "Text Only" / "Vain teksti"
        - `presetViewSummaryTable`: "Summary Table" / "Yhteenvetotaulukko"
      - Card Field Labels:
        - `visibleMetadataFieldsLabel`: "Visible Metadata Fields" / "Näkyvät metatietokentät"
        - `pipelineSynthesisBindingLabel`: "Pipeline Synthesis Block Binding" / "Työnkulun synteesilohkon sidonta"
        - `synthesisPromptBlockLabel`: "Synthesis Prompt Block (Pipeline Way)" / "Synteesin kehotelohko (Työnkulku)"
        - `synthesisPromptBlockHelper`: "Select an existing prompt block configured in the workflow" / "Valitse työnkulkuun määritetty olemassa oleva kehotelohko"
        - `synthesisNoneOption`: "None (Use On-the-Fly configuration below)" / "Ei mitään (Käytä alla olevaa suoraa määritystä)"
        - `toneInstructionLabel`: "Tone Instruction (Voice & Audience)" / "Äänensävy ja kohdeyleisö"
        - `sectionPreambleTextLabel`: "Section Preamble Text" / "Osion johdantoteksti"
        - `visibleTableColumnsLabel`: "Visible Table Columns" / "Näkyvät taulukon sarakkeet"
        - `columnLabelOverridesLabel`: "Column Label Overrides" / "Sarakkeiden otsikoiden mukautukset"
        - `columnLabelField`: "Column Label: {column}" / "Sarakkeen otsikko: {column}" (with `@columnLabelField` metadata defining `String column`)
        - `maxExtensionItemsCount`: "Max Extension Items: {count}" / "Laajennusten enimmäismäärä: {count}" (with `@maxExtensionItemsCount` metadata defining `int count`)
        - `maxFieldLabel`: "Max" / "Enintään"
        - `bibliographyCardHint`: "Formatted source document list and exact quote citations will be rendered at the end of the report." / "Muotoiltu lähdeluettelo ja tarkat lainaukset esitetään raportin lopussa."
      - Display Scales:
        - `displayScaleOriginal`: "Original Scale (Unmodified)" / "Alkuperäinen asteikko (Muuttamaton)"
        - `displayScaleCustom`: "Custom Domain Scale" / "Mukautettu toimiala-asteikko"
        - `displayScaleNormalized100`: "Normalized 0-100% Scale" / "Normalisoitu 0-100 % asteikko"
    </action>
    <action>Execute `flutter gen-l10n` from `client_app_v2` directory to compile synthetic localizations.</action>
  </step>

  <step id="4" name="UI Chrome &amp; Block Card Localization Refactor">
    <constraint invariant="no_magic_strings_l10n">
      Eradicate all hardcoded English/Finnish strings across all Profile Studio tabs and block cards.
      Replace `b.name` in `ProfileLayoutsTab` with localized block title helper function.
    </constraint>
    <action>In `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`:
      - Bind tab titles to `l10n.profileTabGeneral`, `l10n.profileTabScoring`, `l10n.profileTabReportStructure`.
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]`:
      - Verify all field labels, dropdown hints, and section titles use `l10n`.
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]`:
      - Localize DisplayScale dropdown items using `l10n.displayScaleOriginal`, `l10n.displayScaleCustom`, `l10n.displayScaleNormalized100`.
      - Localize ScoringStrategy and Strictness dropdown items.
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`:
      - Replace hardcoded `'Report Visual Blocks'` with `l10n.reportVisualBlocksHeader`.
      - Replace hardcoded `'${payload.targetBlockOrder.length} active'` with `l10n.activeBlocksCount(payload.targetBlockOrder.length)`.
      - Replace hardcoded `'Available Blocks (Click to enable)'` with `l10n.availableBlocksHeader`.
      - Replace `b.name` ActionChip labels with localized block title helper `BlockCardRegistry.getBlockTitle(b, l10n)`.
      - Replace raw padding `EdgeInsets.all(4.0)` with `AppSpacing.p4`.
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]`:
      - Add static `getBlockTitle(TargetBlockType type, AppLocalizations l10n) -> String` and `getBlockSubtitle(TargetBlockType type, AppLocalizations l10n) -> String`.
      - Refactor `SimpleToggleBlockCard` invocations to pass localized `title` and `subtitle` resolved from `l10n`.
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]`:
      - Pass localized title/subtitle to `BaseBlockCard` via `l10n.blockMetadataTitle` / `l10n.blockMetadataSubtitle`.
      - Localize section title: `l10n.visibleMetadataFieldsLabel`.
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart]`:
      - Localize title/subtitle (`l10n.blockSynthesisTextTitle`, `l10n.blockSynthesisTextSubtitle`), section header (`l10n.pipelineSynthesisBindingLabel`), dropdown label (`l10n.synthesisPromptBlockLabel`), helper text (`l10n.synthesisPromptBlockHelper`), none option (`l10n.synthesisNoneOption`), and I18nTextField labels (`l10n.toneInstructionLabel`, `l10n.sectionPreambleTextLabel`).
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]`:
      - Localize title/subtitle (`l10n.blockMatrixGraphsTitle`, `l10n.blockMatrixGraphsSubtitle`), empty state prompt (`l10n.noGraphLayoutsDefined`), and add graph button (`l10n.addGraphButton`).
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`:
      - Localize fallback title (`l10n.graphTitleDefault(index + 1, layout.presetView.name)`), SegmentedButton presets (`l10n.presetView1d`, `l10n.presetView2d`, `l10n.presetView3d`, `l10n.presetViewTextOnly`), graph title label (`l10n.graphTitleLabel`), axis dropdown labels (`l10n.axisXPrimary`, `l10n.axisYComparison`, `l10n.axisZDepth`), placeholder item (`l10n.selectBlockHint`), and duplicate item disabled label (`l10n.alreadySelectedOnOtherAxis(label)`).
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]`:
      - Localize title/subtitle (`l10n.blockMatrixSummaryTitle`, `l10n.blockMatrixSummarySubtitle`), visible columns section header (`l10n.visibleTableColumnsLabel`), column label overrides header (`l10n.columnLabelOverridesLabel`), and field label (`l10n.columnLabelField(col)`).
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]`:
      - Localize title/subtitle (`l10n.blockAiExtensionsTitle`, `l10n.blockAiExtensionsSubtitle`), max extension items count (`l10n.maxExtensionItemsCount(payload.maxExtensionItems)`), and text field label (`l10n.maxFieldLabel`).
    </action>
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]`:
      - Localize title/subtitle (`l10n.blockBibliographyTitle`, `l10n.blockBibliographySubtitle`) and hint text (`l10n.bibliographyCardHint`).
    </action>
  </step>

  <step id="5" name="Dart Freezed Code Generation &amp; Validation Gate">
    <constraint invariant="automated_code_generation_mandate">
      Run build runner automatically after Freezed model and ARB modifications.
    </constraint>
    <action>Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build` to re-generate `output_profile.freezed.dart` and `output_profile.g.dart`.</action>
    <action>Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/synthesis_config_dto.dart --build` to re-generate `synthesis_config_dto.freezed.dart` and `synthesis_config_dto.g.dart`.</action>
  </step>

  <step id="6" name="Frontend Unit &amp; Widget Test Suite Updates">
    <constraint invariant="anti_happy_path_mandate">
      Update test fixtures to cover positive and negative parsing for purged SynthesisConfigDTO, DisplayScale, and localized blocks.
    </constraint>
    <action>In `@[client_app_v2/test/features/studio/models/output_profile_test.dart]`:
      - Update positive test for `SynthesisConfigDTO` verifying valid fields (`synthesis_block_id`, `row_explanations_block_id`, `system_prompt`, `length_constraint`, `preamble_text`, `tone_instruction`).
      - Add negative test asserting `CheckedFromJsonException` when legacy purged keys (`historical_context_mode`, `enable_pii_masking`, `allowed_exports`, `omit_empty_sections`, `allowed_mcp_tools`, `model_strategy`) are present under `disallowUnrecognizedKeys: true`.
    </action>
    <action>Run full Studio test suite to verify zero regressions:
      `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`
    </action>
  </step>

  <step id="7" name="Cross-Stack Quality Gate &amp; Parity Verification">
    <constraint invariant="fragmented_quality_gates_prevention">
      Run both global audit loops to guarantee 100% full-stack integrity.
    </constraint>
    <action>Run Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <action>Run Frontend Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --test`</action>
    <action>Run Enum Parity Test: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test`</action>
  </step>

  <dod_checklist>
    <item>Bilingual ARB dictionaries (`app_en.arb`, `app_fi.arb`) updated with all tab, block title, subtitle, preset, and field keys.</item>
    <item>`flutter gen-l10n` successfully compiled without errors.</item>
    <item>Zero hardcoded UI strings in `output_profile_crud_view.dart`, all 3 tabs, and all 10 block cards.</item>
    <item>`BlockCardRegistry` provides localized block titles and subtitles for all `TargetBlockType` enums.</item>
    <item>`b.name` replaced with localized block titles in `ProfileLayoutsTab`.</item>
    <item>`SynthesisConfigDTO` dead-weight fields purged from Python and Dart Freezed models with `disallowUnrecognizedKeys: true`.</item>
    <item>`backend_v2/models/enums.py` provides `@property def l10n_key` for `ScoringStrategy` and `DisplayScale` via static dictionary mapping.</item>
    <item>`test_enum_parity.py` passes 100% green across all shared enums and asserts l10n_key validity.</item>
    <item>Frontend Freezed code generation passes cleanly with zero warnings.</item>
    <item>Backend and Flutter audit loops pass with 100% test pass rate.</item>
  </dod_checklist>

  <validation_gate>
    <check>uv run python scripts/backend_audit_loop.py backend_v2 --test</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test</check>
  </validation_gate>
</execution_protocol>
```
