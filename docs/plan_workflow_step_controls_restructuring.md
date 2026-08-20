# Implementation Plan: Workflow Step Controls & Terminology Restructuring

Refactor the Workflow Step Card UI in Flutter Studio to replace technical developer jargon (*"Syötekartoitukset (Tilan injektointi)"*) with clear, human-understandable categorization:
1. **Suoritusjärjestys (Edeltävät vaiheet)** (*Execution Flow / Dependencies*)
2. **Analysoitava lähdeaineisto (Dokumentit)** (*Analyzed Source Material / Documents*)
3. **Edeltävien vaiheiden raportit (Valinnainen konteksti)** (*Prior Step Reports / Optional Text Context*)

This UI and localization update preserves 100% of the underlying backend database contracts (`StepRule.input_mappings`, `StepRule.depends_on`) and execution engine logic while making the interaction intuitive and transparent to the user.

---

## User Review Required

> [!IMPORTANT]
> **No Backend or Database Schema Changes:**
> The underlying data structure (`StepRule.input_mappings: dict[str, str]` and `StepRule.depends_on: list[str]`) remains strictly identical.
> This change is purely an **SDUI / UI presentation and localization refactoring** in Flutter that visually groups `$inputs.` and `$steps.` into distinct, self-explanatory sections with helpful inline guidance.

---

## Proposed Changes

### Frontend (Flutter Client & Localization)

#### [MODIFY] @[client_app_v2/lib/l10n/app_fi.arb#L1040-L1095]
- Add localized strings for the new categorized sections:
  - `studioWorkflowSourceDocsTitle`: `"Analysoitava lähdeaineisto (Dokumentit)"`
  - `studioWorkflowSourceDocsSubtitle`: `"Dokumentit toimivat tekoälyn analyysin ja sanantarkkojen sitaattien lähteenä (Context Cache)."`
  - `studioWorkflowPriorStepsTitle`: `"Edeltävien vaiheiden raportit (Valinnainen tekstikonteksti)"`
  - `studioWorkflowPriorStepsSubtitle`: `"Ruksaa vain, jos askeleen pitää lukea edellisen vaiheen tekstiraportti. Puretut atomit ja kausaalirakenne siirtyvät aina automaattisesti taustalla."`
  - `studioWorkflowNoSourceDocs`: `"Ei odotettuja lähdedokumentteja määritettynä."`
  - `studioWorkflowNoPriorStepsSelected`: `"Ei edeltäviä vaiheita valittuna riippuvuuksista."`

#### [MODIFY] @[client_app_v2/lib/l10n/app_en.arb#L1615-L1650]
- Add corresponding English localized strings:
  - `studioWorkflowSourceDocsTitle`: `"Analyzed Source Material (Documents)"`
  - `studioWorkflowSourceDocsSubtitle`: `"Documents serve as evidence for analysis and exact quote citations (Context Cache)."`
  - `studioWorkflowPriorStepsTitle`: `"Prior Step Reports (Optional Text Context)"`
  - `studioWorkflowPriorStepsSubtitle`: `"Select only if this step needs to read the full text summary. Decomposed atoms and causal structure are forwarded automatically."`
  - `studioWorkflowNoSourceDocs`: `"No expected source documents configured."`
  - `studioWorkflowNoPriorStepsSelected`: `"No prior steps selected in dependencies."`

#### [MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L200-L330]
- Restructure the UI layout into two distinct, styled visual containers:
  - **Section A (Source Documents):** Displays `globalWorkflowInputs` with checkboxes for `$inputs.<key>`.
  - **Section B (Prior Step Reports):** Displays previous steps selected in `dependsOn` with checkboxes for `$steps.<id>`.
  - Add descriptive helper text under each section header explaining the purpose and automatic background atom graph forwarding.

#### [NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart]
- Comprehensive Widget test verifying:
  - Categorized rendering of source documents vs prior step reports.
  - Toggling `$inputs` mappings updates `stepDef.inputMappings` correctly.
  - Toggling `$steps` mappings updates `stepDef.inputMappings` correctly.
  - Empty states display informative helper messages.

---

## Canonical XML Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="LOCALIZATION_EXPANSION">
    <description>Add categorized title and subtitle keys to Finnish and English arb files.</description>
    <target_files>
      <file>@[client_app_v2/lib/l10n/app_fi.arb#L1040-L1095]</file>
      <file>@[client_app_v2/lib/l10n/app_en.arb#L1615-L1650]</file>
    </target_files>
    <constraint invariant="dual_axis_localization_architecture">
      All UI labels and descriptive tooltips MUST be defined in .arb files; never hardcode Finnish or English strings directly in Flutter widget code.
    </constraint>
    <action>
      Update app_fi.arb and app_en.arb with the new localization keys and run flutter gen-l10n via audit loop.
    </action>
  </step>

  <step id="2" name="WORKFLOW_STEP_CARD_REFACTORING">
    <description>Refactor WorkflowStepCard into distinct Source Material and Prior Steps sections with inline guidance.</description>
    <target_files>
      <file>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L200-L330]</file>
    </target_files>
    <constraint invariant="frontend_feature_isolation">
      Widget MUST remain stateless and dumb, delegating state changes via the onChanged(StepRule) callback without direct store mutation.
    </constraint>
    <action>
      Replace the unified checkbox block with two distinct sections:
      1. 'Analysoitava lähdeaineisto (Dokumentit)' with helper text and globalWorkflowInputs checkboxes.
      2. 'Edeltävien vaiheiden raportit (Valinnainen tekstikonteksti)' with helper text and dependsOn step checkboxes.
    </action>
  </step>

  <step id="3" name="WIDGET_TEST_SUITE_CREATION">
    <description>Create comprehensive unit and widget tests for WorkflowStepCard rendering and interaction.</description>
    <target_files>
      <file>[NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart]</file>
    </target_files>
    <constraint invariant="anti_happy_path_mandate">
      Test suite MUST cover both populated inputs/steps and empty state handling when no dependencies or inputs exist.
    </constraint>
    <action>
      Write tests asserting that toggling checkboxes produces exact $inputs.<key> and $steps.<id> string mappings in StepRule.inputMappings.
    </action>
  </step>

  <step id="4" name="GLOBAL_QUALITY_GATE_VERIFICATION">
    <description>Run the flutter audit loop to compile Freezed models, verify localization generation, and execute test suites.</description>
    <target_files>
      <file>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]</file>
    </target_files>
    <action>
      Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test`
    </action>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
- Flutter Quality Loop & Widget Testing:
  ```powershell
  uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test
  ```

### Manual Verification
1. Launch Studio view in client app: `.\run_local.bat`
2. Navigate to *Admin Studio* -> *Workflows* -> *Kokonaisvaltainen Auditointi* -> *Stepit & Riippuvuudet*.
3. Verify that each step displays:
   - **Suoritusjärjestys (Edeltävät vaiheet)** with interactive chips.
   - **Analysoitava lähdeaineisto (Dokumentit)** with clearly labeled document checkboxes and Context Cache helper text.
   - **Edeltävien vaiheiden raportit** with step checkboxes and automatic atom graph forwarding note.
