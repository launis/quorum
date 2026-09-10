# Implementation Plan: Studio TDA Editor Input Modernization & ContrastivePairDTO Migration

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
</required_context_rules>

## Executive Summary

The current Studio TDA (Test-Driven Assertion) Editor in `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]` suffers from severe **"Stringification Debt"** and unconstrained user input formatting:
1. **Contrastive Example Ambiguity:** `contrastive_example` is stored as an untyped string (`str | None`) in `@[backend_v2/models/v2_core.py#L155-L264]`, forcing authors in the UI to manually type arbitrary prefixes specifically `ACCEPTABLE: "..."` and `UNACCEPTABLE: "..."` inside an unvalidated single multiline `TextFormField`. Omission of either side corrupts the prompt compiler's few-shot grounding boundary.
2. **Brittle String Delimiter Splitting:** The frontend splits acceptance criteria and anti-patterns on newline characters (`.split('\n')`), and syntactic anchors on commas (`.split(',')`). Accidental linebreaks in a sentence fracture criteria into nonsensical tokens, while commas inside quotation marks produce corrupted anchor queries.
3. **Cognitive Overload & Visual Clutter:** All 12 TDA parameters are presented as a monolithic, unformatted vertical column of text inputs without visual hierarchy, semantic grouping, or active guidance on reversed hypothesis polarity (`inverse_evidence`).
4. **Hardcoded Strings & Design Token Violations:** Multiple helper labels and warning messages are hardcoded in Finnish with static colors (`Colors.amber`), violating the Dual-Axis Localization architecture.

This plan systematically eliminates stringification debt by:
1. Hardening `contrastive_example` into an immutable `ContrastivePairDTO` in `@[backend_v2/models/v2_core.py#L155-L264]` and `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`.
2. Migrating all existing occurrences in `@[backend_v2/seed/seed_data.json]` via an automated migration script `[NEW] @[scripts/migrate_seed_contrastive_pairs.py]`.
3. De-stringifying the Studio UI into three dedicated modular widgets: `[NEW] @[client_app_v2/lib/features/studio/views/widgets/tag_chip_input.dart]`, `[NEW] @[client_app_v2/lib/features/studio/views/widgets/dynamic_item_list_editor.dart]`, and `[NEW] @[client_app_v2/lib/features/studio/views/widgets/contrastive_pair_editor.dart]`.
4. Reorganizing the TDA editor into 5 visually distinct cards with clear typography, contextual badges, an explicit Virhetutka polarity warning banner, and 100% bilingual `.arb` localization coverage.

---

## User Review Required

> [!IMPORTANT]
> **Database Seed Schema Migration:** `contrastive_example` in `seed_data.json` transitions from a raw multiline string (`"ACCEPTABLE: ...\nUNACCEPTABLE: ..."`) to a structured JSON dictionary: `{"acceptable": "...", "rejected": "..."}`. A dedicated migration script (`[NEW] @[scripts/migrate_seed_contrastive_pairs.py]`) will perform this transformation deterministically and verify seed integrity before any schema change is committed.

> [!WARNING]
> **Pydantic V2 Fail-Fast Strictness:** In `@[backend_v2/models/v2_core.py#L155-L264]`, `ContrastivePairDTO` enforces `min_length=10`, `strip_whitespace=True`, and a `@model_validator` requiring `acceptable != rejected`. Any assertion attempting to persist identical strings, whitespace-only entries, or strings shorter than 10 characters will trigger a hard `ValidationError`.

> [!IMPORTANT]
> **Desktop-Class Pro Tool Input Resilience (Uncommitted State Loss Prevention):** `TagChipInput` implements the Dual-Shield FormField Architecture (per audit `AUDIT-STUDIO-TAGCHIP-STATE-LOSS-001`). When an author types a lexical anchor (e.g. `"kausaalisuus"`) and directly clicks "Tallenna" on the dialog AppBar or presses `Ctrl+S` without pressing Enter first, `TagChipInput` synchronously flushes and validates the uncommitted text buffer during form validation and save, preventing silent data loss.

---

## Target Scope & Affected Boundaries

### Target Files (Read-Write)
- `[MODIFY] @[backend_v2/models/v2_core.py#L155-L265]` - Define `ContrastivePairDTO`, update `TDAAssertion.contrastive_example` to `ContrastivePairDTO | None`, enforce cross-field validators.
- `[MODIFY] @[backend_v2/models/dtos/engine.py#L38-L66]` - Extend `FlattenedAtom` with typed `contrastive_example: ContrastivePairDTO | None`, `acceptance_criteria`, `anti_patterns`, and `syntactic_anchors`.
- `[MODIFY] @[backend_v2/hooks/atom_flattening.py#L124-L208]` - Eradicate anonymous state tuple, instantiate `FlattenedAtom` directly, and map structured assertion fields.
- `[MODIFY] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L168-L215]` - Compile structured `<contrastive_grounding>`, `<acceptance_criteria>`, `<anti_patterns>`, and `<syntactic_anchors>` with CDATA encapsulation.
- `[NEW] @[scripts/migrate_seed_contrastive_pairs.py]` - Deterministic migration script converting all 305 legacy string `contrastive_example` fields in `seed_data.json` to structured dictionaries.
- `[MODIFY] @[backend_v2/seed/seed_data.json]` - Converted seed data atoms (all 305 occurrences).
- `[MODIFY] @[scripts/matrix_slice_engine.py#L121-L153]` - Update slice validation rules for `ContrastivePairDTO` (auditing `acceptable` and `rejected` fields without `TypeError`).
- `[MODIFY] @[scripts/matrix_hardening_generator.py#L83-L125]` - Emit structured `ContrastivePairDTO` dictionary during atom expansion with length >= 10.
- `[MODIFY] @[scripts/diff_executions.py#L780-L805]` and `@[scripts/diff_executions.py#L1790-L1805]` - Update contrastive example extraction and formatting for structured dictionaries without `AttributeError`.
- `[MODIFY] @[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py#L92-L102]` - Validate `ContrastivePairDTO` instances across target atoms.
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py#L51-L76]` - Update unit tests for structured contrastive examples.
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py#L51-L76]` - Update unit tests for structured contrastive examples.
- `[NEW] @[backend_v2/tests/unit/models/test_contrastive_pair_dto.py]` - Unit tests for `ContrastivePairDTO` and `TDAAssertion` validation constraints.
- `[NEW] @[tests/guardrails/test_ast_tda_editor_guardrails.py]` - AST guardrail preventing string delimiter parsing (`.split('\n')`, `.split(',')`) or unvalidated contrastive strings.
- `[MODIFY] @[client_app_v2/lib/features/studio/models/prompt_block.dart#L108-L143]` - Add `@Freezed ContrastivePairDTO` and update `TDAAssertion.contrastiveExample`.
- `[NEW] @[client_app_v2/lib/features/studio/views/widgets/tag_chip_input.dart]` - Tag chip collection widget with trimming, duplicate prevention, and backspace deletion.
- `[NEW] @[client_app_v2/lib/features/studio/views/widgets/dynamic_item_list_editor.dart]` - Structured dynamic list editor for criteria and anti-patterns.
- `[NEW] @[client_app_v2/lib/features/studio/views/widgets/contrastive_pair_editor.dart]` - Two-field contrastive pair editor with character counters and semantic labels.
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L28-L1085]` - Reorganize editor into 5 visual cards, implement pre-save focus unfocus + form validate/save, remove hardcoded strings/colors, embed modular widgets.
- `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb]` - Finnish localization strings.
- `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb]` - English localization strings.
- `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart#L24-L60]` - Update widget test fixtures for `ContrastivePairDTO`.
- `[NEW] @[client_app_v2/test/features/studio/views/widgets/tag_chip_input_test.dart]` - Unit test for tag chip input.
- `[NEW] @[client_app_v2/test/features/studio/views/widgets/contrastive_pair_editor_test.dart]` - Unit test for contrastive pair editor.

### Context Files (Read-Only)
- `@[backend_v2/models/core_base.py]` - `V2CoreBase` model base class.
- `@[backend_v2/core/template_processor.py]` - CDATA encapsulation and safe interpolation engine.
- `@[client_app_v2/lib/core/theme/app_spacing.dart]` - App spacing and theme tokens.

---

## Detailed UI Simplification & Categorization Architecture

To eliminate author cognitive fatigue, prevent scroll disorientation, and guarantee desktop-class authoring speed, `scale_editor_modal.dart` is redesigned around **Master-Detail Navigation**, **Progressive Disclosure**, and **5 Distinct Visual Cards**:

```
+-----------------------------------------------------------------------------------------------+
| Dialog Header: Muokkaa arviointitasoa (Score 5: Exemplary Mastery)      [ Peruuta ] [ Tallenna ] |
+-----------------------------------------------------------------------------------------------+
| MASTER PANE: Claims Sidebar (240px) | DETAIL PANE: Active Claim Canvas (Scrollable)           |
|                                     |                                                         |
| [ Claim 1: Causal Depth ] [● OK]    | Active Assertion: tda_08c5a8eca0bb41a49d60b849503da2bb  |
| [ Claim 2: Evidence Ground ] [! Err]| +-----------------------------------------------------+ |
|                                     | | CARD 1: Ydinmääritelmä & Kohdistus                  | |
| [+ Lisää uusi väite]                | | - Päättelyraita: SegmentedButton (Laadullinen/Sensor)| |
|                                     | | - Pääväite: TextFormField (live laskuri: 14/10 char)| |
|                                     | | - Kohdistusalue & Erotussääntö (Rinnakkain Row)     | |
|                                     | +-----------------------------------------------------+ |
|                                     | | CARD 2: Päättelyketju & Hylkäysperusteet            | |
|                                     | | - DynamicItemListEditor: Step 1, Step 2 (+ Lisää)   | |
|                                     | | - DynamicItemListEditor: Antimalli 1 (+ Lisää)      | |
|                                     | +-----------------------------------------------------+ |
|                                     | | CARD 3: Rajanveto & Kalibrointi (Contrastive Pairs) | |
|                                     | | - ContrastivePairEditor (Rinnakkain/Päällekkäin)    | |
|                                     | |   [+] Hyväksytty (Vihreä reuna, min 10 char)        | |
|                                     | |   [-] Hylätty (Punainen reuna, min 10 char)         | |
|                                     | +-----------------------------------------------------+ |
|                                     | | CARD 4: Täsmähaku & Pikakarsinta (Lexical Anchors)  | |
|                                     | | - TagChipInput (Enter/Pilkku lisää, Backspace poistaa)|
|                                     | | - Progressive Switch: enforce_pre_flight            | |
|                                     | +-----------------------------------------------------+ |
|                                     | | CARD 5: Aggregaatio & Virhetutka                    | |
|                                     | | - Käänteinen tulkinta (Virhetutka Switch)           | |
|                                     | |   >>> [VIRHETUTKA ERROR CONTAINER BANNER]           | |
|                                     | |       ⚠️ Virhetutka aktiivinen: Varmista, että      | |
|                                     | |       pääväite kuvaa virhettä tai puutetta.         | |
|                                     | | - Osumien laajuus (Lukittuu tilaan EXISTS)          | |
|                                     | +-----------------------------------------------------+ |
+-----------------------------------------------------------------------------------------------+
```

### 1. Zone Breakdown & Desktop Ergonomics (Per KI ki_desktop_pro_tool_studio_ux)
- **Master-Detail Claims Navigation:** On desktop viewports (width $\ge$ 900px), a sticky 240px left sidebar lists all claims for the scale with live status badges (`OK` green badge vs `Missing inputs` error badge). Switching claims instantly swaps the detail pane without page-level scroll resets.
- **Zone 1: Core Hypothesis & Progressive Scope:** Uses a `SegmentedButton` for `evaluation_track` (`COGNITIVE_JUDGEMENT` vs `EXTRACTIVE_SENSOR`). The concept description textfield enforces `minLines: 2`, `maxLines: 4`, with a live character count badge (`N/10 chars`) turning green upon reaching threshold. Non-English detection (`[äöåÄÖÅ]`) renders a soft inline linguistic notice badge (`Theme.of(context).colorScheme.tertiaryContainer`). When `EXTRACTIVE_SENSOR` is selected, `facts_to_find` and `logical_expression` query builders are dynamically progressively revealed.
- **Zone 2: Reasoning Chain & Anti-Patterns:** Eradicates `.split('\n')`. Replaced by `DynamicItemListEditor`. Authors add discrete numbered cards with an explicit `+ Lisää kriteeri` button, order badges, and a trashcan deletion icon per row. Empty submissions are blocked.
- **Zone 3: Contrastive Calibration:** Eradicates the single textarea. Replaced by `ContrastivePairEditor`. Contains two dedicated `TextFormField` fields with colored semantic indicator accents (green checkmark accent for `acceptable`, red ban accent for `rejected`), character length indicators, and an active inline error if acceptable and rejected texts match.
- **Zone 4: Lexical Anchors & Keyboard-First Input (Dual-Shield FormField):** Eradicates `.split(',')`. Replaced by `TagChipInput` implementing `FormField<List<String>>`:
  1. *Keystroke Tokenization:* Typing a keyword and pressing `Enter`, `,`, or `Tab` immediately commits a distinct `InputChip`. Trailing whitespace is automatically stripped, duplicate keywords trigger an inline error indicator, and chips can be deleted via tap on `(X)` or `Backspace` in an empty input field.
  2. *Focus-Loss Auto-Commit:* When the input field loses focus (e.g., author presses `Tab` to navigate to another section or clicks another card), any non-empty trimmed text in the controller is automatically committed to `List<String> tags`.
  3. *Pre-Save Flush Protocol:* When clicking "Tallenna" on the AppBar or pressing `Ctrl+S`, `scale_editor_modal.dart` invokes `FocusScope.of(context).unfocus()` and `_formKey.currentState!.validate()`. `TagChipInput` synchronously flushes and validates the pending text buffer during validation, preventing silent data loss when saving without pressing Enter.
- **Zone 5: Aggregation & Virhetutka Metamorphosis:** When `inverse_evidence` is toggled to `True`:
  1. `aggregation_mode` is automatically coerced to `AggregationMode.exists` and `AggregationMode.allMustComply` is disabled in the dropdown with an explanatory helper.
  2. The Card container adopts a subtle `colorScheme.errorContainer` border accent.
  3. An eye-catching warning container (`colorScheme.errorContainer`) is dynamically mounted directly beneath the switch:
     *"⚠️ Huomio: Virhetutka etsii tekstistä virheitä ja riskikäyttäytymistä. Väitteen löytyminen hylkää tämän tason. Varmista, että arvioitava väite on muotoiltu virheeksi (esim. 'Kausaalisuhde puuttuu täysin'), jotta oikeat suoritukset eivät saa nollatulosta."*
- **Global Desktop Shortcuts:** `Ctrl + S` / `Cmd + S` invokes atomic modal save; `Esc` prompts clean dismissal with dirty-form state verification.

---

## Multilingual Localization Specification (.arb)

All UI strings adhere to the Dual-Axis Localization architecture. No user-facing text or prompt instructions are hardcoded in widget code.

### Required Keys in `@[client_app_v2/lib/l10n/app_fi.arb]`
```json
  "scaleSectionCoreHypothesis": "1. Ydinmääritelmä & Kohdistus",
  "scaleSectionReasoning": "2. Päättelyketju & Hylkäysperusteet",
  "scaleSectionContrastive": "3. Rajanveto & Kalibrointi",
  "scaleSectionAnchors": "4. Täsmähaku & Pikakarsinta",
  "scaleSectionAggregation": "5. Aggregaatio & Virhetutka",
  "scaleAcceptableExampleLabel": "Hyväksytty esimerkki (Acceptable)",
  "scaleAcceptableExampleHelper": "Esimerkki lauseesta tai ilmaisusta, joka täyttää tämän tason vaatimuksen (EN, vähintään 10 merkkiä).",
  "scaleRejectedExampleLabel": "Hylätty vastine (Rejected)",
  "scaleRejectedExampleHelper": "Esimerkki lauseesta, joka hylätään tältä tasolta (EN, vähintään 10 merkkiä).",
  "scaleContrastiveIdenticalError": "Hyväksytty ja hylätty esimerkki eivät voi olla identtisiä.",
  "scaleContrastiveMinLengthError": "Esimerkin tulee olla vähintään {count} merkkiä pitkä.",
  "scaleAddCriterionBtn": "Lisää päättelyvaihe",
  "scaleAddAntiPatternBtn": "Lisää hylkäysperuste",
  "scaleCriterionPlaceholder": "Kirjoita looginen tarkistusvaihe englanniksi...",
  "scaleAntiPatternPlaceholder": "Kirjoita hylkäävä antimalli englanniksi...",
  "scaleAnchorChipPlaceholder": "Kirjoita sana ja paina Enter...",
  "scaleAnchorDuplicateError": "Tunnistussana on jo lisätty.",
  "scaleInverseEvidenceWarningTitle": "Virhetutka aktivoitu",
  "scaleInverseEvidenceWarningDesc": "Tämä väite etsii virheitä tai laadun puutteita. Löytyminen aiheuttaa hylkäyksen. Varmista, että yllä oleva pääväite kuvaa virheellistä toimintaa, jotta laadukas teksti ei saa virheellistä hylkäystä.",
  "scaleSystemLanguageNotice": "Ohje: Tekoälyn arviointiväitteiden, kriteerien ja esimerkkien tulee olla englanniksi (System Language) parhaan päättelytarkkuuden takaamiseksi."
```

### Required Keys in `@[client_app_v2/lib/l10n/app_en.arb]`
```json
  "scaleSectionCoreHypothesis": "1. Core Hypothesis & Scope",
  "scaleSectionReasoning": "2. Reasoning Chain & Anti-Patterns",
  "scaleSectionContrastive": "3. Contrastive Calibration",
  "scaleSectionAnchors": "4. Lexical Anchors & Fast Falsification",
  "scaleSectionAggregation": "5. Aggregation & Reverse Polarity",
  "scaleAcceptableExampleLabel": "Approved Example (Acceptable)",
  "scaleAcceptableExampleHelper": "Example of a sentence or expression that satisfies this level's requirement (EN, at least 10 characters).",
  "scaleRejectedExampleLabel": "Rejected Counterpart (Rejected)",
  "scaleRejectedExampleHelper": "Example of a sentence that is rejected from this level (EN, at least 10 characters).",
  "scaleContrastiveIdenticalError": "Approved and rejected examples cannot be identical.",
  "scaleContrastiveMinLengthError": "Example must be at least {count} characters long.",
  "scaleAddCriterionBtn": "Add Reasoning Step",
  "scaleAddAntiPatternBtn": "Add Anti-Pattern",
  "scaleCriterionPlaceholder": "Enter logical verification step in English...",
  "scaleAntiPatternPlaceholder": "Enter disqualifying anti-pattern in English...",
  "scaleAnchorChipPlaceholder": "Type word and press Enter...",
  "scaleAnchorDuplicateError": "Keyword has already been added.",
  "scaleInverseEvidenceWarningTitle": "Defect Sensor Activated",
  "scaleInverseEvidenceWarningDesc": "This assertion detects defects or omissions. A match triggers disqualification. Ensure the core hypothesis describes a defect so that high-quality text is not erroneously rejected.",
  "scaleSystemLanguageNotice": "Note: AI evaluation assertions, criteria, and examples must be written in English (System Language) to ensure optimal reasoning accuracy."
```

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`ContrastivePairDTO` & `TDAAssertion`**<br>`@[backend_v2/models/v2_core.py#L155-L265]` | Banned untyped string `contrastive_example: str \| None`, unvalidated `ACCEPTABLE:` prefix conventions, loose whitespace strings, and permissive dictionary fallbacks. | Immutable Pydantic V2 DTO (`ConfigDict(strict=True, extra="forbid", frozen=True)`). `StringConstraints(strip_whitespace=True, min_length=10)`. `@model_validator` enforcing `acceptable.lower() != rejected.lower()`. | Pruned speculative multi-exemplar lists (`list[ContrastiveExample]`), fuzzy cosine similarity validators, or LLM-based rubric evaluators inside Pydantic models. Simple two-field pair. | `uv run pytest backend_v2/tests/unit/models/test_contrastive_pair_dto.py -v`. Hard `ValueError` / `AppException` with `ErrorCodes.VALIDATION_FAILED` on identical or short strings. |
| **Seed Data Migration**<br>`[NEW] @[scripts/migrate_seed_contrastive_pairs.py]`<br>`@[backend_v2/seed/seed_data.json]` | Banned ad-hoc terminal regex scripts (`sed`), in-place dirty overwrites without backups, and silent dropping of unparseable contrastive text across all 305 seed atoms. | Deterministic Python migration script creating timestamped backup in `backend_v2/seed/backups/`. Parses `ACCEPTABLE:` / `UNACCEPTABLE:` / `REJECTED:` prefixes, trims quotes, asserts `ContrastivePairDTO` validity across all 305 atoms. | Pruned dynamic online schema conversion in API endpoints or lazy runtime migration hooks in the repository layer. One-time offline migration. | `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`. 100% in-memory validation before database sync. |
| **Engine Transit & FlattenedAtom**<br>`@[backend_v2/models/dtos/engine.py#L38-L66]`<br>`@[backend_v2/hooks/atom_flattening.py#L124-L208]` | Banned anonymous state tuples (`tuple[str, str, str, str, bool, ...]`), positional index access (`atom[5]`, `val[0]`), naked dictionary unpacks (`**tda_dict`), and dropping structured assertion fields during DAG flattening. | Strict direct instantiation of `FlattenedAtom` instances in `scale_atoms`, `matrix_collected_atoms`, and `unique_atoms`. Direct dot-notation propagation of `tda.contrastive_example`, `tda.acceptance_criteria`, `tda.anti_patterns`, and `tda.syntactic_anchors`. | Pruned creating a secondary shadow atom model or wrapping `FlattenedAtom` in an extra intermediate container layer. Direct typed extension. | `uv run pytest backend_v2/tests/unit/hooks/ -v` and `backend_audit_loop.py`. Assertion fields verified in serialized DAG state. Zero anonymous tuples in hook. |
| **Matrix Sensor Prompt Builder**<br>`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L168-L215]` | Banned raw Python f-string XML interpolation (`f"<acceptable>{ex}</acceptable>"`), unshielded prompt injection, and scattering prompt instructions in service methods. | Dynamic user message compilation via `TemplateProcessor.encapsulate_payload()` with CDATA breakout protection (`]]]]><![CDATA[>`) for `<contrastive_grounding>`, `<acceptable>`, `<rejected>`, `<acceptance_criteria>`, `<anti_patterns>`, and `<syntactic_anchors>`. | Pruned multi-pass XML formatting pipelines or custom template engines. Uses existing `TemplateProcessor` SSOT. | Unit tests in `backend_v2/tests/unit/orchestrator/` asserting valid CDATA wrapping and unescaped XML shield survival. |
| **Slice Engine & Hardening Generator**<br>`@[scripts/matrix_slice_engine.py#L121-L153]`<br>`@[scripts/matrix_hardening_generator.py#L83-L125]` | Banned `TypeError` from checking `"ACCEPTABLE:" in ex` on `ContrastivePairDTO` objects, and banned short fixture strings (`<10` chars) triggering `ValidationError`. | Audit `ContrastivePairDTO` attributes (`ex.acceptable`, `ex.rejected`) in `audit_atom_coherence`. Update `create_template_atom` to emit structured dictionary with exemplars length >= 10. | Pruned complex AST validators inside generator scripts. Pure attribute and length validation. | `uv run pytest backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py -v` and `test_matrix_hardening_loop.py`. |
| **Execution Diff Reporting**<br>`@[scripts/diff_executions.py#L780-L805]`<br>`@[scripts/diff_executions.py#L1790-L1805]` | Banned `AttributeError: 'dict' object has no attribute 'strip'` on `(tda.get("contrastive_example") or "").strip()` when contrastive example becomes a structured dictionary, and raw dict dump in markdown. | Extract typed `acceptable` and `rejected` sub-fields from dictionary/DTO and format in Markdown audit trail. | Pruned creating complex report view models for diff script. Direct clean formatting. | Mental dry-run and script execution check on local trace files. |
| **Dart Freezed DTO & Parity**<br>`@[client_app_v2/lib/features/studio/models/prompt_block.dart#L108-L143]` | Banned untyped string `contrastiveExample: String?`, permissive JSON deserialization (`disallowUnrecognizedKeys: false`), and default empty string fallbacks (`?? ""`). | `@Freezed(equal: false)` immutable `ContrastivePairDTO` with `@JsonSerializable(disallowUnrecognizedKeys: true)`. Required `acceptable` and `rejected` fields. | Pruned client-side validation business logic or dynamic JSON transformation layers in Dart. Pure data carrier. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`. Freezed codegen verified. |
| **Studio UI De-Stringification & Input Resilience**<br>`[NEW] @[client_app_v2/lib/features/studio/views/widgets/tag_chip_input.dart]`<br>`[NEW] @[client_app_v2/lib/features/studio/views/widgets/dynamic_item_list_editor.dart]`<br>`[NEW] @[client_app_v2/lib/features/studio/views/widgets/contrastive_pair_editor.dart]` | Banned `.split('\n')` on textarea inputs, `.split(',')` on keywords, raw string parsing, hardcoded Finnish labels, `Colors.amber`, and **Frontend Uncommitted State Loss** (dropping text in `_textController.text` when saving via mouse or `Ctrl+S` without pressing Enter). | Modular UI widgets under 150 lines: `TagChipInput` implementing **Dual-Shield FormField Architecture** (`FormField<List<String>>` with synchronous `_commitPendingText()` on focus loss, Tab, Comma, Enter, and during `validator`/`onSaved`), `DynamicItemListEditor` (numbered step cards), `ContrastivePairEditor` (two validated `TextFormField`s). 100% `AppSpacing` tokens and `AppLocalizations`. | Pruned third-party chip libraries (`flutter_tags`) and redundant custom EventBus/Stream messaging between parent and child widgets. Native Flutter `FormField` composition. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart --build`. ISTQB tests asserting buffer commit on mouse save, save on `Ctrl+S`, and duplicate buffer error feedback. |
| **5-Card Studio Layout & Virhetutka**<br>`@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L330-L1085]` | Banned monolithic 12-input vertical column, unguided reverse polarity toggles, and hiding broken fields with `SizedBox.shrink()`. | 5 semantic `Card` widgets with borderRadius 12, elevation 1, and `AppSpacing.p16`. Dynamic `errorContainer` warning banner when `inverse_evidence == true` explaining defect detection polarity. Dropdown coercing `AggregationMode.exists`. | Pruned collapsible accordion animations, multi-step wizards, or multi-tab subviews that would hide context from the author. Flat scrollable 5-card layout. | Flutter widget test asserting 5 distinct card containers and error container banner rendering upon `inverseEvidence = true`. |

---

```xml
<execution_protocol>
  <step id="1" name="PHASE 1: PRE-IMPLEMENTATION CLEANUPS & BACKEND SSOT DTO">
    <action>In `@[backend_v2/models/v2_core.py#L155-L264]`, declare the canonical `ContrastivePairDTO`:</action>
    <content>
class ContrastivePairDTO(V2CoreBase):
    """Structured contrastive calibration pair for TDA assertion boundary grounding.

    Attributes:
        acceptable: Textual exemplar satisfying the evaluation assertion.
        rejected: Textual counterpart demonstrating disqualification or boundary failure.
    """

    acceptable: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10),
        Field(description="Textual exemplar satisfying the evaluation assertion."),
    ]
    rejected: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10),
        Field(description="Textual counterpart demonstrating disqualification or boundary failure."),
    ]

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    @model_validator(mode="after")
    def validate_contrastive_diversity(self) -> Self:
        """Enforces that acceptable and rejected exemplars are distinct and non-empty.

        Raises:
            ValueError: If acceptable equals rejected or either exemplar is blank.
        """
        if self.acceptable.strip().lower() == self.rejected.strip().lower():
            msg = "Contrastive acceptable and rejected exemplars cannot be identical."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self
    </content>
    <action>In `@[backend_v2/models/v2_core.py#L155-L264]`, update `TDAAssertion.contrastive_example`:</action>
    <content>
    contrastive_example: ContrastivePairDTO | None = Field(
        default=None,
        description="Structured contrastive pair showing acceptable vs rejected exemplars.",
    )
    </content>
    <action>In `@[backend_v2/models/v2_core.py#L234-L264]`, update `validate_math_logic` to enforce that when `enforce_pre_flight=True`, `syntactic_anchors` must not be empty, and all string list elements in `acceptance_criteria` and `anti_patterns` must have stripped length >= 5. Ensure all validation failures log with `ErrorCodes.VALIDATION_FAILED.name` and raise `ValueError`.</action>
    <action>Export `ContrastivePairDTO` in `__all__` of `@[backend_v2/models/v2_core.py]`.</action>
    <action>Eradicate Anonymous Tuple Hell in `@[backend_v2/hooks/atom_flattening.py#L124-L208]`:
      1. Refactor `all_matrix_atoms` and `unique_atoms` from `dict[str, tuple[...]]` to store typed `FlattenedAtom` instances directly.
      2. Eliminate the 6-element tuple `(aid, text, rule, anchor, is_inv, deps)` and positional indexing (`current_atom[5]`, `current_atom[0]`, `val[0]...val[4]`), instantiating `FlattenedAtom` directly in `scale_atoms`.
    </action>
    <action>Fix technical debt in `@[scripts/diff_executions.py#L780-L805]` and `@[scripts/diff_executions.py#L1790-L1805]`:
      1. Safely parse `contrastive_example` when structured as a dictionary: replace `(tda.get("contrastive_example") or "").strip()` with safe dictionary key extraction (`c_ex.get("acceptable")` / `c_ex.get("rejected")`), preventing `AttributeError: 'dict' object has no attribute 'strip'`.
      2. Format structured contrastive pairs cleanly in markdown report lines 1794-1798.
    </action>
    <action>Fix technical debt in `@[scripts/matrix_slice_engine.py#L121-L153]`:
      Update `audit_atom_coherence` line 146 to check `ContrastivePairDTO` attributes (`ex.acceptable`, `ex.rejected`) instead of raw substring search `"ACCEPTABLE:" not in ex` which raises `TypeError` on DTO objects.
    </action>
    <action>Fix technical debt in `@[scripts/matrix_hardening_generator.py#L83-L125]` and tests:
      Upgrade template fixtures in `create_template_atom` and unit tests (`test_matrix_hardening_generator.py`, `test_matrix_hardening_loop.py`) so `acceptable_example` and `unacceptable_example` have length >= 10 (e.g. `"Acceptable exemplar text"` / `"Unacceptable counter text"`), preventing `ValidationError` against `ContrastivePairDTO`.
    </action>
    <action>Clean up technical debt in `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L28-L920]`:
      1. In `_save()` (lines 28-56): call `FocusScope.of(context).unfocus()` as the very first operation, call `_formKey.currentState!.validate()`, call `_formKey.currentState!.save()`, and route snackbar messages through `AppLocalizations.of(context)!`.
      2. Eliminate hardcoded Finnish strings (lines 37, 47, 572, 673, 835, 873, 910), routing all display text through `AppLocalizations.of(context)!`.
      3. Eliminate hardcoded `Colors.amber` (lines 574, 675), replacing with `Theme.of(context).colorScheme.tertiaryContainer`.
      4. Eliminate `.split('\n')` delimiter parsing (lines 598, 700) and `.split(',')` (lines 750, 1018).
    </action>
    <constraint invariant="the_zero_compromise_pledge">Zero permissive typing: ConfigDict(strict=True, extra="forbid", frozen=True). No loose string fallback or Union with raw str.</constraint>
    <constraint invariant="ban_anonymous_state_tuples">Eradicate all anonymous tuples in DAG state transit and atom flattening.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">Precede all validation failures with structured logger.error containing ErrorCodes.VALIDATION_FAILED.name.</constraint>
  </step>

  <step id="2" name="SEED DATA VAULT MIGRATION SCRIPT & ATOMIC RE-SEEDING">
    <action>Create `[NEW] @[scripts/migrate_seed_contrastive_pairs.py]` to migrate all 305 existing atoms in `@[backend_v2/seed/seed_data.json]`. The script parses legacy strings containing `ACCEPTABLE:` and `UNACCEPTABLE:` (or `REJECTED:`) into `{"acceptable": acceptable_text, "rejected": rejected_text}`.</action>
    <action>The script creates a backup copy at `backend_v2/seed/backups/seed_data_backup_contrastive_pre.json` before writing.</action>
    <action>Execute migration: `uv run python scripts/migrate_seed_contrastive_pairs.py`.</action>
    <action>Update `@[scripts/diff_executions.py#L780-L805]` and `@[scripts/diff_executions.py#L1790-L1805]` to safely read structured `contrastive_example` dictionaries and format them as `det['contrastive_example']['acceptable']` / `det['contrastive_example']['rejected']`.</action>
    <action>Execute dry-run pre-flight validation: `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`.</action>
    <action>Execute atomic re-seed: `uv run python backend_v2/seed/run_seed.py local`.</action>
    <constraint invariant="vault_mutation_protocol">Must execute two-phase pre-flight in-memory validation before database sync. If validation fails, restore backup immediately.</constraint>
    <constraint invariant="database_persistence_git_ban">Never rollback runtime database state with git checkout. Preserve updated seed_data.json and db_v2.json atomically.</constraint>
  </step>

  <step id="3" name="ENGINE DTO PROPAGATION & SENSOR PROMPT BUILDER INTEGRATION">
    <action>In `@[backend_v2/models/dtos/engine.py#L38-L64]`, update `FlattenedAtom` to carry structured assertion parameters:</action>
    <content>
class FlattenedAtom(BaseModel):
    atom_id: Annotated[str, Field(description="Opaque hashed ID for the extracted atom.")]
    question: Annotated[str, Field(description="The text content evaluated blindly.")]
    extraction_rule: Annotated[str, Field(default="", description="The specific validation rule.")]
    anchor_target: Annotated[str, Field(default="", description="Semantic bounding box target.")]
    is_inverse: Annotated[bool, Field(default=False, description="True if this is an inverse assertion.")]
    depends_on: Annotated[
        tuple[CausalEdge, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(
            default_factory=tuple,
            description="Causal dependencies attached to this atom.",
        ),
    ]
    contrastive_example: Annotated[
        ContrastivePairDTO | None,
        Field(default=None, description="Structured contrastive pair."),
    ] = None
    acceptance_criteria: Annotated[
        tuple[AcceptanceCriterion, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(default_factory=tuple, description="Deductive verification sequence."),
    ]
    anti_patterns: Annotated[
        tuple[AntiPattern, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(default_factory=tuple, description="Disqualifying patterns."),
    ]
    syntactic_anchors: Annotated[
        tuple[str, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(default_factory=tuple, description="Exact syntactic markers."),
    ]

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    </content>
    <action>In `@[backend_v2/hooks/atom_flattening.py#L124-L208]`, eradicate anonymous state tuple construction and instantiate typed `FlattenedAtom` directly, propagating `tda.contrastive_example`, `tda.acceptance_criteria`, `tda.anti_patterns`, and `tda.syntactic_anchors`.</action>
    <action>In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L83-L233]`, compile structured XML tags using `TemplateProcessor` with CDATA shielding:</action>
    <content>
            if assertion:
                # ... existing question, extraction_rule, anchor_target compilation ...
                if assertion.contrastive_example:
                    acc_cdata = TemplateProcessor.encapsulate_payload(assertion.contrastive_example.acceptable)
                    rej_cdata = TemplateProcessor.encapsulate_payload(assertion.contrastive_example.rejected)
                    content += (
                        f"<contrastive_grounding>\n"
                        f"<acceptable>\n{acc_cdata}\n</acceptable>\n"
                        f"<rejected>\n{rej_cdata}\n</rejected>\n"
                        f"</contrastive_grounding>\n"
                    )

                if assertion.acceptance_criteria:
                    crit_blocks = [
                        f'<criterion index="{idx + 1}">\n{TemplateProcessor.encapsulate_payload(c.instruction)}\n</criterion>'
                        for idx, c in enumerate(assertion.acceptance_criteria)
                    ]
                    content += f"<acceptance_criteria>\n" + "\n".join(crit_blocks) + "\n</acceptance_criteria>\n"

                if assertion.anti_patterns:
                    anti_blocks = [
                        f'<anti_pattern index="{idx + 1}">\n{TemplateProcessor.encapsulate_payload(a.pattern)}\n</anti_pattern>'
                        for idx, a in enumerate(assertion.anti_patterns)
                    ]
                    content += f"<anti_patterns>\n" + "\n".join(anti_blocks) + "\n</anti_patterns>\n"

                if assertion.syntactic_anchors:
                    anchor_blocks = [
                        f"<anchor>\n{TemplateProcessor.encapsulate_payload(a)}\n</anchor>"
                        for a in assertion.syntactic_anchors
                    ]
                    content += f"<syntactic_anchors>\n" + "\n".join(anchor_blocks) + "\n</syntactic_anchors>\n"
    </content>
    <action>Update `@[scripts/matrix_slice_engine.py#L121-L152]` to validate `tda.contrastive_example` using `acceptable` and `rejected` length checks instead of raw string substring searches.</action>
    <action>Update `@[scripts/matrix_hardening_generator.py#L83-L124]` to output `contrastive_example: {"acceptable": acceptable_example, "rejected": unacceptable_example}`.</action>
    <constraint invariant="static_first_caching_topology">All static instructions remain static in the system message. Dynamic claim parameters are isolated in dynamic user messages.</constraint>
  </step>

  <step id="4" name="FLUTTER FREEZED DTO & CODEGEN SYNC">
    <action>In `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, define `ContrastivePairDTO`:</action>
    <content>
@Freezed(equal: false)
abstract class ContrastivePairDTO with _$ContrastivePairDTO {
  const ContrastivePairDTO._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ContrastivePairDTO({
    required String acceptable,
    required String rejected,
  }) = _ContrastivePairDTO;

  factory ContrastivePairDTO.fromJson(Map<String, dynamic> json) =>
      _$ContrastivePairDTOFromJson(json);
}
    </content>
    <action>Update `TDAAssertion` in `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`:
      `@JsonKey(name: 'contrastive_example') ContrastivePairDTO? contrastiveExample,`
    </action>
    <action>Run Freezed code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`.</action>
    <constraint invariant="automated_code_generation_mandate">Never manually edit .freezed.dart or .g.dart files. Autonomously execute the flutter audit loop with --build.</constraint>
  </step>

  <step id="5" name="MULTILINGUAL LOCALIZATION ARB SYNCHRONIZATION">
    <action>In `@[client_app_v2/lib/l10n/app_fi.arb]`, insert the required Finnish keys for section headers, contrastive editors, dynamic list buttons, and the Virhetutka alert banner.</action>
    <action>In `@[client_app_v2/lib/l10n/app_en.arb]`, insert the identical English keys with 1:1 parity.</action>
    <action>Run Flutter l10n compilation: `cd client_app_v2; flutter gen-l10n`.</action>
    <constraint invariant="no_magic_strings_l10n">Zero hardcoded string literals in UI widgets. All display text must resolve through AppLocalizations.of(context)!.</constraint>
    <constraint invariant="dual_axis_localization_mandate">Static UI chrome in .arb; English system language rules for prompt evaluations.</constraint>
  </step>

  <step id="6" name="MODULAR FLUTTER COMPONENT EXTRACTION">
    <action>Create `[NEW] @[client_app_v2/lib/features/studio/views/widgets/tag_chip_input.dart]`:
      - Implements Dual-Shield FormField Architecture: extends or wraps `FormField<List<String>>`.
      - Encapsulates `List<String> tags` and internal `TextEditingController` with `FocusNode`.
      - Implements `_commitPendingText()`:
        * Triggers on `Enter`, `,`, or `Tab`.
        * Triggers on Focus Loss (`!focusNode.hasFocus`) when tabbing out or clicking another field.
        * Triggers synchronously during `FormField.validator` and `FormField.onSaved` to eliminate uncommitted state loss when clicking "Tallenna" on the AppBar or pressing `Ctrl+S`.
        * Trims whitespace; ignores empty strings; surfaces inline duplicate error if token already exists.
      - Renders an `InputChip` wrapping list inside a `Wrap` widget with `spacing: AppSpacing.p8`.
      - Pressing `Backspace` in an empty input field deletes the trailing chip.
      - Each chip has an `onDeleted` callback and an explicit semantic tooltip.
    </action>
    <action>Create `[NEW] @[client_app_v2/lib/features/studio/views/widgets/dynamic_item_list_editor.dart]`:
      - Reusable component for `acceptance_criteria` and `anti_patterns`.
      - Renders a vertical list of item rows. Each item row contains a numbered step badge (`Container` with `colorScheme.surfaceContainerHighest`), an expanded `TextFormField`, and an `IconButton` (trashcan) with `colorScheme.error`.
      - Includes an `OutlinedButton.icon` at the bottom (`+ Lisää vaihe` / `+ Lisää kriteeri`).
    </action>
    <action>Create `[NEW] @[client_app_v2/lib/features/studio/views/widgets/contrastive_pair_editor.dart]`:
      - Renders two distinct `TextFormField` inputs: `Hyväksytty esimerkki (Acceptable)` and `Hylätty vastine (Rejected)`.
      - Features colored border accents (green for acceptable, red for rejected), live character counters (`N/10 chars`), helper texts, and real-time duplicate rejection banner.
    </action>
    <constraint invariant="monolithic_god_widgets">Decompose UI outwards into discrete, testable sub-widgets under 150 lines each. Prevent bloating scale_editor_modal.dart.</constraint>
    <constraint invariant="design_token_absolute_rule">Exclusively use AppSpacing tokens and Theme.of(context).colorScheme. No hardcoded numeric paddings or Color(0x...) literals.</constraint>
  </step>

  <step id="7" name="STUDIO TDA EDITOR REFACTORING & MASTER-DETAIL 5-CARD LAYOUT">
    <action>In `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`:
      1. Implement Master-Detail split pane navigation (left 240px Claim sidebar with error badges, right detail pane with active Claim cards).
      2. Replace the unformatted vertical input block with 5 `Card` widgets as designed in the UI Architecture section.
      3. Implement Progressive Disclosure: collapse sensor parameters (`facts_to_find`, `logical_expression`) when `evaluation_track == COGNITIVE_JUDGEMENT`.
      4. Embed `DynamicItemListEditor` for `acceptance_criteria` and `anti_patterns`.
      5. Embed `ContrastivePairEditor` for `contrastive_example`.
      6. Embed `TagChipInput` for `syntactic_anchors` adhering to `FormField<List<String>>` with pre-save flush and focus-loss auto-commit.
      7. In `_save()`:
        * Call `FocusScope.of(context).unfocus()` as the very first operation to trigger desktop focus listeners.
        * Call `_formKey.currentState!.validate()` (which flushes and validates pending text in `TagChipInput`).
        * Call `_formKey.currentState!.save()` to synchronously bind FormField state before inspecting domain constraints and popping.
      8. Eradicate all hardcoded Finnish strings in snackbars (`"Virhetutka vaatii..."`, `"Pikahylkäys vaatii..."`), replacing them with `l10n` calls.
      9. Eradicate `Colors.amber` and replace with `Theme.of(context).colorScheme.tertiaryContainer`.
      10. In Card 5, when `tda.inverseEvidence == true`, mount the prominent `Virhetutka` warning container with `colorScheme.errorContainer` and `Icons.warning_amber_rounded`.
      11. Bind `Ctrl+S` / `Cmd+S` keyboard shortcuts for saving (invoking `_save()`), and ensure dirty-state detection (`Esc` / Cancel) evaluates both model differences and uncommitted pending text in `TagChipInput`.
    </action>
    <constraint invariant="studio_unified_visual_design_system">Card containers with borderRadius 12, padding 16, margin 16, semantic typography, and 100% Theme.of(context) color adherence.</constraint>
  </step>

  <step id="8" name="TESTING, AST GUARDRAILS & QUALITY GATE VERIFICATION">
    <action>Create `[NEW] @[backend_v2/tests/unit/models/test_contrastive_pair_dto.py]` covering:
      - Positive: Valid pairs with lengths >= 10 instantiate cleanly.
      - Negative 1: `acceptable == rejected` raises `ValidationError` / `AppException`.
      - Negative 2: `len(acceptable) < 10` raises `ValidationError`.
      - Negative 3: Whitespace-only string raises `ValidationError`.
      - Negative 4: Missing `acceptable` or `rejected` key raises `ValidationError`.
    </action>
    <action>Update `@[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py#L92-L100]` to assert that all target atoms have `isinstance(assertion.contrastive_example, ContrastivePairDTO)`.</action>
    <action>Update `@[backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py#L51-L74]` and `@[backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py#L51-L74]` for structured contrastive example dictionaries.</action>
    <action>Create `[NEW] @[tests/guardrails/test_ast_tda_editor_guardrails.py]` utilizing Python `ast` module:
      - Asserts that `scale_editor_modal.dart` contains zero occurrences of `.split('\n')` or `.split(',')`.
      - Asserts that `TDAAssertion` in `v2_core.py` defines `contrastive_example` strictly as `ContrastivePairDTO | None`.
    </action>
    <action>Update `@[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart]` with valid `ContrastivePairDTO` instances and assert rendering of the 5 cards.</action>
    <action>Create `[NEW] @[client_app_v2/test/features/studio/views/widgets/tag_chip_input_test.dart]` covering ISTQB boundary partitions:
      - Happy Path: Enter/Comma/Tab commits trimmed chip.
      - Backspace: Deletes trailing chip when input is empty.
      - Uncommitted Buffer (Mouse Click): Entering text without Enter -> triggering `FormField.save()` commits the token.
      - Uncommitted Buffer (Focus Loss): Entering text -> unfocusing field auto-commits the chip.
      - Duplicate Buffer on Save: Entering duplicate text -> triggering validation flags duplicate error and halts save.
    </action>
    <action>Create `[NEW] @[client_app_v2/test/features/studio/views/widgets/contrastive_pair_editor_test.dart]`.</action>
    <action>In `@[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart]`:
      - Test that typing anchor in `TagChipInput` without Enter and clicking "Tallenna" button retains the anchor in the returned `MatrixScale`.
      - Test that typing anchor without Enter and pressing `Ctrl+S` retains the anchor in the returned `MatrixScale`.
    </action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`.</action>
    <action>Run flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart --build`.</action>
    <constraint invariant="anti_happy_path_mandate">Every component must have at least 2 negative test cases covering boundary values, empty inputs, and validation errors.</constraint>
    <constraint invariant="ast_guardrail_mandate">Build AST guardrail test to structurally prevent regression of loose string contrastive examples or .split() anti-patterns.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Pydantic Validation & Negative Boundaries:**
   `uv run pytest backend_v2/tests/unit/models/test_contrastive_pair_dto.py -v`
2. **Seed Vault Integrity & Anchoring Rules:**
   `uv run pytest backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py -v`
3. **AST Architectural Guardrails:**
   `uv run pytest tests/guardrails/test_ast_tda_editor_guardrails.py -v`
4. **Backend Global Quality Gate:**
   `uv run python scripts/backend_audit_loop.py backend_v2 --test`
5. **Flutter Widget & Unit Tests:**
   `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart --build`
6. **Frontend Global Quality Gate:**
   `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart --build`

### Manual Verification
1. Launch the Flutter desktop app: `cd client_app_v2; flutter run -d windows`.
2. Navigate to Quorum Studio -> Evaluation Matrices -> Open any rubric scale editor modal.
3. Verify that the 5 distinct visual cards are rendered with clear boundaries, spacing, and subtitles.
4. Test `TagChipInput`: Enter a word with trailing spaces and press `Enter`. Confirm a clean trimmed chip is created. Attempt to enter the same word again and verify duplicate rejection. Test Uncommitted State Loss prevention: Type a new anchor (e.g. 'kausaalisuus') without pressing Enter, and directly click the 'Tallenna' button on the AppBar; re-open the modal and verify that 'kausaalisuus' was committed and saved. Test the same flow with `Ctrl+S`.
5. Test `DynamicItemListEditor`: Add a new acceptance criterion with `+ Lisää päättelyvaihe`. Confirm numbered badge indexing. Delete a row using the trashcan icon.
6. Test `ContrastivePairEditor`: Verify that entering fewer than 10 characters or identical text triggers active inline validation error messages.
7. Test `Virhetutka`: Toggle `Käänteinen tulkinta` on and verify that the red alert banner appears, explaining the reverse polarity hypothesis clearly.
