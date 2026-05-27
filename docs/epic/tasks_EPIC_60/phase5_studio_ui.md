# Phase 5: Admin Studio Form UI (Käyttöliittymämuutokset)

This sub-plan addresses **Phase 5: Käyttöliittymä (Flutter Client & Admin Studio)** from Epic 60. It updates the Admin Studio dynamic step builder visual layout in Flutter to handle decoupled parameters via dropdown controls and multi-selection criteria editors.

## System Invariants & Rules
* **Rule 1: No Hardcoded Strings (client_application_development.md)**: All newly introduced labels, dropdown tooltips, and validation error messages must reside exclusively in Flutter `.arb` language assets. Hardcoded Finnish or English strings in the Dart widget code are completely banned.
* **Rule 2: Responsive PC-Class Layouts (client_application_development.md)**: Admin Studio forms must respect premium, desktop-grade information densities and layouts (>1200dp), using visual dividers and clear grouping cards.

---

## Proposed Changes

### [Component: Admin Studio UI]
We will replace the single unstructured PromptBlock list card inside `step_builder_view.dart` with dedicated fields for Role, Extraction Protocol, and Criteria.

#### [MODIFY] [step_builder_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/step_builder_view.dart)
* **Step 1 (Source: Epic Phase 4, Toimenpide 1)**: Modify the UI layout to replace the old `prompt_blocks` visual list with separate selectors:
  * **Role Selection**: A dropdown displaying all prompt blocks belonging to the role category, mapped to `payload.roleBlockId`.
  * **Extraction Protocol Selection**: A dropdown showing instructions blocks, mapped to `payload.extractionProtocolBlockId` (defaulting to zero-trust extraction block `blk_573802341db9d68c`).
  * **Criteria Blocks List**: Reorderable card list of matrix and text criteria blocks, mapped to `payload.criteriaBlockIds`.
* **Step 2**: Rebuild `_buildPromptBlockCard` to manage elements of `payload.criteriaBlockIds` as `_buildCriteriaBlockCard`.

#### [MODIFY] [app_en.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_en.arb)
* **Step 3 (Source: Epic Phase 4, Toimenpide 1)**: Add English translations for the newly introduced selectors.
  ```json
  "roleBlockLabel": "AI Persona Role Override",
  "roleBlockDescription": "Select standard LLM persona (e.g. blk_role_critic).",
  "protocolBlockLabel": "Evidence Extraction Protocol",
  "protocolBlockDescription": "Standard mecanic rules for blind mathematical verification.",
  "criteriaBlocksTitle": "Evaluation Criteria Matrices",
  "criteriaBlocksDescription": "Specific domain semantic claims to evaluate."
  ```

#### [MODIFY] [app_fi.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb)
* **Step 4 (Source: Epic Phase 4, Toimenpide 1)**: Add Finnish translations for the newly introduced selectors.
  ```json
  "roleBlockLabel": "Tekoälyn roolipersoona",
  "roleBlockDescription": "Valitse tekoälyn asenne (esim. blk_role_critic).",
  "protocolBlockLabel": "Evidenssin poimintaprotokolla",
  "protocolBlockDescription": "Mekaaniset säännöt sokeaan matemaattiseen poimintaan.",
  "criteriaBlocksTitle": "Arvioitavat kriteerilohkot",
  "criteriaBlocksDescription": "Spesifit domain-tason arviointikriteerit."
  ```

---

## Testing & Quality Gate Plan

### Automated Verification
1. **L10n Arb Alignment**:
   Ensure all new localization strings are compiled and synchronized natively:
   ```powershell
   # USER EXECUTION DELEGATION
   flutter gen-l10n
   ```
2. **Flutter Compilation & Test Suite**:
   Run the Flutter audit loop to build generated assets and execute existing widgets and unit tests:
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2 --build
   ```

---

## Session Handover
To proceed, start a new chat session and run the following command to load the tracking context:
```powershell
/tier5-resume --target="docs/epic/EPIC_60_tracker.md"
```
