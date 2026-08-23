# Phase 4: Flutter Studio Client Harmonization

**Overview:** Update frontend enums with `SystemUiConstraints.tdaConceptMinLength(10)`, update Freezed model `MatrixClaim` by removing `aiDescription`, enforce 32 hex char `tdaId` format in `TDAAssertion.create`, align modal dialogs and BARS matrix builder, add ARB localizations, perform Scoped Boy Scout cleanups, establish comprehensive unit tests with ISTQB negative boundary value coverage, and run Freezed code generation.
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/core/models/enums.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/prompt_block.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart]
- `[NEW]` @[client_app_v2/test/models/matrix_claim_test.dart]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L229-L242] Phase 4: Flutter Studio Client Harmonization

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3 in @[backend_v2/models/v2_core.py#L330-L360] and @[backend_v2/settings.py]. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[client_app_v2/lib/core/models/enums.dart] and @[client_app_v2/lib/features/studio/models/prompt_block.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] `tdaConceptMinLength(10)` added to `SystemUiConstraints` enum in @[client_app_v2/lib/core/models/enums.dart].
    - [x] `required String aiDescription` removed from `MatrixClaim` in @[client_app_v2/lib/features/studio/models/prompt_block.dart].
    - [x] `TDAAssertion.create` factory updated to produce 32 hex chars (`tda_$uuidHex`).
    - [x] ARB localization keys `tdaConceptMinLengthError`, `tdaAnchorTargetHelper`, and `tdaExtractionRuleHelper` added to @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb], and compiled via `flutter gen-l10n`.
    - [x] Freezed code generation executed via `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`.
    - [x] Scale editor modal, row editor modal, BARS matrix builder, and prompt block builder view aligned with new models.
    - [x] Scale editor modal `conceptDescription` field enforces min length validator checking `SystemUiConstraints.tdaConceptMinLength.value`.
    - [x] Unit test fixture in @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart] updated to omit `aiDescription` and assert rendering of `claim.tdaAssertions.first.conceptDescription`.
    - [x] Comprehensive unit test suite in @[client_app_v2/test/models/matrix_claim_test.dart] established with positive assertions and ISTQB negative boundary value test coverage.
    - [x] Quality gate `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test` passes against migrated `seed_data.json`.
    - [x] Global Quality Gate `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` passes.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_pipeline.md]</knowledge_item>
    <knowledge_item>@[ki_strict_sdui_serialization.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/prompt_block.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <test>@[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart]</test>
    <test>@[client_app_v2/test/models/matrix_claim_test.dart]</test>
  </touched_artifacts>

  <anti_targets>
    - Do NOT re-introduce `aiDescription` in Dart `MatrixClaim` models.
    - Do NOT mix Python backend edits in this plan.
    - Do NOT create ad-hoc UUID strings without `TDAAssertion.create()`.
    - Do NOT hardcode validation error strings in widget files without `.arb` localizations.
    - Do NOT use hardcoded numeric doubles for spacing or padding instead of `AppSpacing` tokens.
  </anti_targets>

  <step id="1" name="Pre-Implementation Technical Debt Cleanups &amp; ARB Localization Setup">
    <action>Modify @[client_app_v2/lib/l10n/app_en.arb]: Add `tdaConceptMinLengthError` ("Concept description must be at least {min} characters long."), `tdaAnchorTargetHelper` ("Specific entity, keyword, or sentence to anchor on"), and `tdaExtractionRuleHelper` ("Condition that must hold true within the bounding box").</action>
    <action>Modify @[client_app_v2/lib/l10n/app_fi.arb]: Add `tdaConceptMinLengthError` ("Käsitekuvauksen on oltava vähintään {min} merkkiä pitkä."), `tdaAnchorTargetHelper` ("Tietty entiteetti, avainsana tai lause, johon kiinnitytään"), and `tdaExtractionRuleHelper` ("Ehto, jonka on pädettävä rajausalueella").</action>
    <action>Run localization compilation: `cd client_app_v2; flutter gen-l10n`.</action>
    <action>Modify @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]: Replace remaining magic numbers (`SizedBox(height: 10)`, `padding: EdgeInsets.all(10.0)`, `margin: EdgeInsets.only(bottom: 12)`) with standard `AppSpacing` design tokens.</action>
    <action>Modify @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]: Ensure all layout spacing uses `AppSpacing` design tokens.</action>
  </step>

  <step id="2" name="Centralized Enums &amp; Freezed Models Update">
    <action>Modify @[client_app_v2/lib/core/models/enums.dart]: Add `tdaConceptMinLength(10)` to `SystemUiConstraints` enum.</action>
    <action>Modify @[client_app_v2/lib/features/studio/models/prompt_block.dart]: Replace `tdaId: 'tda_${uuidHex.substring(0, 16)}'` with `tdaId: 'tda_$uuidHex'` in `TDAAssertion.create`, and remove `required String aiDescription` from `MatrixClaim` Freezed model.</action>
    <demolish>REMOVE: `aiDescription` from `MatrixClaim` Freezed model at @[client_app_v2/lib/features/studio/models/prompt_block.dart]. REPLACE WITH: 1:1 parity with backend `MatrixClaim`.</demolish>
    <action>Run Freezed code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`.</action>
  </step>

  <step id="3" name="Studio Views Alignment &amp; Modal Modernization">
    <action>Modify @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]:
      1. In `_addClaim()`, instantiate `MatrixClaim` with `label: const I18nText(defaultLocale: 'en', translations: {'en': ''})` and `tdaAssertions: [TDAAssertion.create(conceptDescription: 'CRITICAL MANDATE: ', inverseEvidence: false, aggregationMode: AggregationMode.exists)]`.
      2. Eradicate legacy `TextFormField` for `claim.aiDescription`.
      3. In `TextFormField` for `tda.conceptDescription`, add `validator` enforcing `if (val == null || val.trim().length < SystemUiConstraints.tdaConceptMinLength.value) return l10n.tdaConceptMinLengthError(SystemUiConstraints.tdaConceptMinLength.value); return null;`.
      4. Migrate helper texts to `l10n.tdaAnchorTargetHelper` and `l10n.tdaExtractionRuleHelper`.</action>
    <action>Modify @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]: Replace display of `claim.aiDescription` with `claim.tdaAssertions.first.conceptDescription`.</action>
    <action>Modify @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]: Update default `MatrixClaim` instantiation in `ScaleEditorModal` dialog (at line 1188) to omit `aiDescription` and supply valid `tdaAssertions` via `TDAAssertion.create`.</action>
  </step>

  <step id="4" name="Unit Test Modernization &amp; ISTQB Negative Partition Coverage">
    <action>Modify @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart]: Remove `aiDescription: 'AI Rule 1'` from `MatrixClaim` test fixture and assert that `claim.tdaAssertions.first.conceptDescription` (`'Atom 1 Rule'`) is rendered in the UI.</action>
    <action>Create [NEW] @[client_app_v2/test/models/matrix_claim_test.dart]:
      1. Positive Test: `TDAAssertion.create` generates 32 hex char ID matching regex `^tda_[a-f0-9]{32}$`.
      2. Positive Test: `MatrixClaim` deserializes from JSON without `ai_description` and preserves `label` and `tda_assertions`.
      3. Positive Test: `SystemUiConstraints.tdaConceptMinLength.value` equals 10.
      4. Negative Test 1: `MatrixClaim.fromJson` with legacy `ai_description` throws `CheckedFromJsonException` (`disallowUnrecognizedKeys: true`).
      5. Negative Test 2: Boundary Value Analysis on concept length validator (9 characters fails validation, 10 characters succeeds).
      6. Negative Test 3: `TDAAssertion` JSON deserialization with missing required fields throws `CheckedFromJsonException`.</action>
    <action>Execute Domain Parity Gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test` proving all 152 prompt blocks from `seed_data.json` parse via background isolate.</action>
  </step>

  <validation_gate>
    <action>Execute Frontend Model Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`</action>
    <action>Execute Matrix Claim Unit Tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/matrix_claim_test.dart --test`</action>
    <action>Execute Bars Matrix Builder Unit Tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart --test`</action>
    <action>Execute Domain Parity Gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test`</action>
    <action>Execute Global Frontend Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`</action>
  </validation_gate>
</execution_protocol>
```
