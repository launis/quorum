# Implementation Plan: Phase 4 - Frontend SDUI & PDF Report Parity

This task implements the premium visuaalinen "Variance Gauge" card in the Flutter Client and Jinja2 PDF templates, and adds the required localization keys.

## Scoping

### Target (Modify)
- [ ] [xai_extensions_box.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/views/widgets/xai_extensions_box.dart) - Render the new `VarianceValidationExtension` dynamically using design tokens.
- [ ] [app_fi.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb) - English and Finnish translations.
- [ ] [app_en.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_en.arb)
- [ ] [report_template.jinja2](file:///c:/src/quorum/backend_v2/templates/report_template.jinja2) - Mirror the visual balance card in the static A4 PDF.

### Context (Read-Only)
- [x] [pdf_generator.py](file:///c:/src/quorum/backend_v2/services/pdf_generator.py)

---

## Technical Specifications & Architectural Invariants

> [!IMPORTANT]
> **No Hardcoded Strings & Design Token absolute adherence**:
> - All new UI labels, tooltips, and strings must be strictly read from `AppLocalizations` (`no_magic_strings_l10n` & `no_string_l10n`).
> - Use exclusively global spacing tokens and context-aware styling instead of hardcoded hex values (`design_token_absolute_rule`).
> - Both PDF and Flutter implementations must share identical semantic coloring (e.g. Amber/Orange for mismatch, Green for aligned) to respect PDF-first layout rules (`tripartite_rendering_boundary`).

### Visual Variance Gauge Design
The gauge represents the comparison:
$$\text{Variance} = | \text{LLM Authenticity Score} - (3.0 - \text{Normalized Performative Count}) |$$
- Scale: $0.0$ (perfect alignment) to $2.0$ (complete mismatch/sycophancy).
- Gauge Visual: A horizontal segment bar with:
  - Aligned Segment ($0.0 - 0.5$): Pure Green (Success/Safe color scheme).
  - Mild Mismatch ($0.5 - 1.0$): Yellow/Amber (Warning).
  - Severe Mismatch ($1.0 - 2.0$): Orange/Red (Error).
- Position Marker: An indicator triangle/line floating dynamically over the segment representing the calculated `variance_score`.
- Alignment Verdict Display: Display text (read via l10n) based on the `alignment_verdict` enum value.

---

## Detailed Milestones

### Milestone 1: Localizations Update
- **Goal**: Register the translation keys in arb files.
- **Source**: Epic Phase 4, Toimenpide 1.
- **Actions**:
  1. Add translations in `client_app_v2/lib/l10n/app_en.arb` and `app_fi.arb`:
     - `xaiVarianceValidationTitle`: Finnish: "Mekaaninen vs Kognitiivinen Tasapaino", English: "Mechanical vs Cognitive Balance".
     - `xaiVerdictAligned`: Finnish: "Tasapainossa (ALIGNED)", English: "Aligned (ALIGNED)".
     - `xaiVerdictSycophancy`: Finnish: "Kognitiivinen Mielistely (MISALIGNED_SYCOPHANCY)", English: "Cognitive Sycophancy (MISALIGNED_SYCOPHANCY)".
     - `xaiVerdictMisaligned`: Finnish: "Poikkeama (MISALIGNED)", English: "Misaligned (MISALIGNED)".
  2. Regenerate Dart localizations:
     ```powershell
     cd client_app_v2 ; flutter gen-l10n
     ```

### Milestone 2: Flutter Variance Gauge Widget Integration
- **Goal**: Implement the responsive Gauge inside `xai_extensions_box.dart`.
- **Source**: Epic Phase 4, Toimenpide 1.
- **Actions**:
  1. Update `XAIExtensionsBox` switch block to handle the `variance_validation` extension type.
  2. Build a beautiful Card featuring a linear/circular slider gauge showing where the marker sits between perfect Aligned and Sycophancy.
  3. Hook tooltips explaining that it compares the linguistic performative phrase count against the LLM's authenticity rating.

### Milestone 3: Jinja2 PDF Template Parity
- **Goal**: Mirror the visual card layout in the static A4 template.
- **Source**: Epic Phase 4, Toimenpide 2.
- **Actions**:
  1. Modify `backend_v2/templates/report_template.jinja2` to scan and render the `variance_validation` extension.
  2. Implement a styled HTML/CSS progress bar replicating the segments and dynamic marker positioning matching the A4 spatial constraints.

---

## Testing & Quality Gate Plan

### Manual Verification
- In local dev mode, trigger report generation, open the execution details page in Admin Studio, and check that the "Mechanical vs Cognitive Balance" card is rendered beautifully.
- Trigger PDF export and verify that the exported A4 PDF report matches perfectly without overflow or page breaks.

---

## Session Handover
To execute this step iteratively in a new session, run:
```powershell
/tier2-execute --plan="docs/epic/tasks_EPIC_57/phase4_frontend_pdf.md"
```
