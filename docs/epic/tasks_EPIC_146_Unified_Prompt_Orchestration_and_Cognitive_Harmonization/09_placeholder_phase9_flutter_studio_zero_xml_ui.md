# Phase 9: Flutter Studio Zero-XML UI Modernization

**Overview:** Modernize `PromptBlockBuilderView` using Dart 3 pattern matching to render Zero-XML structured form sections per polymorphic variant (`SystemRulePromptBlock`, `ExecutionPersonaPromptBlock`, `AgentRolePromptBlock`, `ProtocolPromptBlock`, `RuntimeVariablesPromptBlock`, `TaskDefinitionPromptBlock`, and `MatrixPromptBlock`), integrate live "Compiled Prompt Preview" modal/sheet with copy-to-clipboard, streamline Step criteria selection and clean hardcoded strings in `StepBuilderView`, add all required localization keys to `app_en.arb` and `app_fi.arb`, and implement comprehensive unit/widget tests for the zero-XML form dispatcher.

**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[NEW]` @[client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L379-L385] Phase 9: Flutter Studio Zero-XML UI Modernization

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify baseline state left by Phase 8 in @[client_app_v2/lib/features/studio/models/prompt_block.dart] and @[backend_v2/models/domain/prompt_blocks.py]. Confirm that PromptBlock sealed hierarchy possesses: MatrixPromptBlock, SystemRulePromptBlock, ExecutionPersonaPromptBlock, AgentRolePromptBlock, ProtocolPromptBlock, RuntimeVariablesPromptBlock, and TaskDefinitionPromptBlock.</action>
    <action>Look forward: Verify requirements for Phase 9 in @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L379-L385] and ensure PromptBlockBuilderView and StepBuilderView adhere strictly to Dart 3 pattern matching, Zero-XML input paradigms, AppSpacing tokens, and ARB localization.</action>
    <constraint invariant="zero_legacy_state_support">Zero tolerance for asking users to input raw XML tags in UI forms, hardcoded magic double spacing, hardcoded hex colors, or missing ARB localizations.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `app_en.arb` and `app_fi.arb` updated with all required localization keys for Zero-XML fields (`instructionTextLabel`, `instructionTextHelper`, `roleEnforcementLabel`, `roleEnforcementHelper`, `protocolInstructionsLabel`, `protocolInstructionsHelper`, `toneDirectivesTitle`, `toneDirectiveItemLabel`, `addToneDirectiveBtn`, `compiledPromptPreviewTitle`, `compiledPromptPreviewTooltip`, `copyToClipboardBtn`, `promptCopiedSnackbar`, `noInstructionsDefined`, `matrixPromptNotice`, `studioModelStrategyLabel`, `studioNoModelsWarning`).
    - [ ] `flutter gen-l10n` successfully compiled in `client_app_v2`.
    - [ ] `prompt_block_builder_view.dart` updated with Dart 3 switch expression pattern matching on `payload` to render specialized form sections per polymorphic variant without asking users to type raw XML tags.
    - [ ] Dynamic lists (specifically `toneDirectives` for Persona/Role) rendered with add/remove controls adhering to `_addListItem` and `_removeListItem` patterns.
    - [ ] Live "Compiled Prompt Preview" modal/sheet integrated in `prompt_block_builder_view.dart` showing simulated compiled prompt with syntax styling and copy-to-clipboard button.
    - [ ] `step_builder_view.dart` criteria block dropdown verified and aligned with `PromptBlockCategoryGroups.criteriaCategories`, and hardcoded tooltips/warnings migrated to ARB.
    - [ ] Spacing doubles and padding constants across both views migrated to `AppSpacing` design tokens.
    - [ ] Comprehensive unit and widget tests established in `client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart` testing form rendering across all 7 polymorphic variants, category switching, validation error states, and negative ISTQB partitions.
    - [ ] Quality gates pass: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart --build` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
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
    <frontend>@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT ask users to input raw XML tags (specifically `<system_directive>`, `<role>`, `<rules>`) manually into form fields.
    - Do NOT hardcode colors (specifically `Color(0xFF...)`) or numeric layout spacing doubles (`SizedBox(height: 16)`); use Theme and `AppSpacing` design tokens strictly.
    - Do NOT use string concatenation or fallback chains for localized texts (`trans['fi'] ?? trans['en'] ?? ...`).
    - Do NOT suppress errors with empty catch blocks or `SizedBox.shrink()`.
    - Do NOT leave unlocalized hardcoded strings in Studio views (e.g. `'Back to Studio'`, `'Warning: No models found.'`).
  </anti_targets>

  <step id="1" name="ARB Localization Setup &amp; Code Generation">
    <action>In @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb], add comprehensive localization entries:
      1. Zero-XML Form Headers &amp; Labels:
         - `instructionTextLabel` (EN: "System Instruction Text", FI: "Järjestelmän ohjeteksti")
         - `instructionTextHelper` (EN: "English natural text instruction without XML tags. Tag wrapping is applied automatically by the prompt compiler.", FI: "Englanninkielinen luonnollinen ohjeteksti ilman XML-tageja. Kehote-kääntäjä lisää tagit automaattisesti.")
         - `roleEnforcementLabel` (EN: "Role Enforcement Directive", FI: "Rooliohjeistus (Role Enforcement)")
         - `roleEnforcementHelper` (EN: "Defines persona constraints, background expertise, and behavioral posture.", FI: "Määrittelee persoonan rajat, asiantuntijuustaustan ja toimintamallin.")
         - `protocolInstructionsLabel` (EN: "Protocol Execution Instructions", FI: "Protokollan suoritusohjeet")
         - `protocolInstructionsHelper` (EN: "Operational protocol steps and algorithmic directives for the model.", FI: "Toiminnalliset protokolla-askeleet ja algoritmiset ohjeet mallille.")
         - `toneDirectivesTitle` (EN: "Tone Directives", FI: "Sävyohjeet (Tone Directives)")
         - `toneDirectiveItemLabel` (EN: "Tone Directive {index}", FI: "Sävyohje {index}", placeholders: index (int))
         - `addToneDirectiveBtn` (EN: "Add Tone Directive", FI: "Lisää sävyohje")
      2. Compiled Prompt Preview:
         - `compiledPromptPreviewTitle` (EN: "Live Compiled Prompt Preview", FI: "Koostetun kehotteen esikatselu")
         - `compiledPromptPreviewTooltip` (EN: "Preview the exact compiled XML prompt output sent to the foundational model", FI: "Esikatsele mallille lähetettävä valmis XML-muotoiltu kehote")
         - `copyToClipboardBtn` (EN: "Copy to Clipboard", FI: "Kopioi leikepöydälle")
         - `promptCopiedSnackbar` (EN: "Compiled prompt copied to clipboard!", FI: "Koostettu kehote kopioitu leikepöydälle!")
         - `noInstructionsDefined` (EN: "No instructions defined for this block yet.", FI: "Tälle lohkolle ei ole vielä määritelty ohjeita.")
         - `matrixPromptNotice` (EN: "Evaluation matrix guidelines and criteria are configured in the BARS Matrix scales below.", FI: "Arviointimatriisin ohjeet ja kriteerit määritellään alla olevissa BARS-matriisin asteikoissa.")
      3. Step Builder &amp; Model Strategy Localizations:
         - `studioModelStrategyLabel` (EN: "Model Strategy (Cost/Cognition Override)", FI: "Mallistrategia (Hinta/Kognitio-ohitus)")
         - `studioNoModelsWarning` (EN: "Warning: No models found in registry.", FI: "Varoitus: Mallirekisteristä ei löytynyt malleja.")
    </action>
    <action>Execute `cd client_app_v2; flutter gen-l10n` using `run_command`.</action>
  </step>

  <step id="2" name="PromptBlockBuilderView Polymorphic Form Modernization">
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]:
      1. Pre-requisite Technical Debt Cleanup:
         - Replace all legacy magic spacing doubles (`SizedBox(height: 16)`, `SizedBox(height: 24)`, `EdgeInsets.all(16.0)`) with `AppSpacing` tokens (`AppSpacing.h16`, `AppSpacing.h24`, `AppSpacing.p16`, `AppSpacing.w8`).
      2. Replace legacy single `aiDescription` textarea with a polymorphic form dispatcher using Dart 3 pattern matching on `payload`:
         ```dart
         Widget _buildPolymorphicInstructionSection(
           BuildContext context,
           WidgetRef ref,
           AppLocalizations l10n,
           PromptBlock payload,
           String blockId,
         ) {
           return switch (payload) {
             SystemRulePromptBlock(:final instructionText) => _buildSystemRuleSection(
                 context, ref, l10n, payload, blockId, instructionText,
               ),
             RuntimeVariablesPromptBlock(:final instructionText) => _buildSystemRuleSection(
                 context, ref, l10n, payload, blockId, instructionText,
               ),
             TaskDefinitionPromptBlock(:final instructionText) => _buildSystemRuleSection(
                 context, ref, l10n, payload, blockId, instructionText,
               ),
             ExecutionPersonaPromptBlock(:final roleEnforcement, :final toneDirectives) =>
               _buildPersonaSection(
                 context, ref, l10n, payload, blockId, roleEnforcement, toneDirectives,
               ),
             AgentRolePromptBlock(:final roleEnforcement, :final toneDirectives) =>
               _buildPersonaSection(
                 context, ref, l10n, payload, blockId, roleEnforcement, toneDirectives,
               ),
             ProtocolPromptBlock(:final protocolInstructions) => _buildProtocolSection(
                 context, ref, l10n, payload, blockId, protocolInstructions,
               ),
             MatrixPromptBlock() => _buildMatrixNoticeSection(
                 context, l10n,
               ),
           };
         }
         ```
      3. Implement specialized Zero-XML sub-section builders:
         - `_buildSystemRuleSection`: renders `TextFormField` bound to `instructionText` with `l10n.instructionTextLabel` and `l10n.instructionTextHelper`, updating `ref.read(promptBlockFormProvider(blockId).notifier).forceRebuild(...)` with updated `instructionText`.
         - `_buildPersonaSection`: renders `TextFormField` bound to `roleEnforcement` with `l10n.roleEnforcementLabel` and `l10n.roleEnforcementHelper`, plus a dynamic list of `toneDirectives` with add/remove buttons using `_addListItem<String>` and `_removeListItem<String>`.
         - `_buildProtocolSection`: renders `TextFormField` bound to `protocolInstructions` with `l10n.protocolInstructionsLabel` and `l10n.protocolInstructionsHelper`, updating `protocolInstructions`.
         - `_buildMatrixNoticeSection`: renders a stylized notice card with `l10n.matrixPromptNotice` indicating that rubric criteria are configured in the BARS scales below.
      4. Enhance live "Compiled Prompt Preview" action button in AppBar:
         - Connect `l10n.compiledPromptPreviewTooltip` to the IconButton tooltip.
         - In `validateMutation.onSuccess`, display `AlertDialog` with `l10n.compiledPromptPreviewTitle`, monospace code viewer, "Copy to Clipboard" button (`Clipboard.setData(ClipboardData(text: rendered))` with `l10n.promptCopiedSnackbar`), and close button.
    </action>
  </step>

  <step id="3" name="StepBuilderView Streamlining &amp; Criteria Categories Alignment">
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart]:
      1. Pre-requisite Technical Debt Cleanup:
         - Replace hardcoded `'Back to Studio'` tooltip with `l10n.backToStudioTooltip`.
         - Replace hardcoded `'Warning: No models found.'` with `l10n.studioNoModelsWarning`.
         - Replace hardcoded `'Model Strategy (Cost/Cognition Override)'` with `l10n.studioModelStrategyLabel`.
         - Replace magic spacing doubles (`SizedBox(height: 16)`, `SizedBox(height: 24)`) with `AppSpacing` tokens (`AppSpacing.h16`, `AppSpacing.h24`).
      2. Verify that `PromptBlockCategoryGroups.criteriaCategories` in `enums.dart` includes `['matrix', 'system_rule', 'runtime_variables', 'task_definition', 'protocol', 'criteria', 'text']`.
      3. Verify that criteria block dropdown filtering cleanly filters prompt blocks without assertion crashes.
    </action>
  </step>

  <step id="4" name="Unit &amp; Widget Test Suite Implementation">
    <action>In @[client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart]:
      Implement comprehensive widget tests covering:
      1. **SystemRulePromptBlock**: Renders `instructionText` field and text updates emit updated `PromptBlock.systemRule`.
      2. **ExecutionPersonaPromptBlock**: Renders `roleEnforcement` and `toneDirectives` dynamic list; verifies adding and removing tone directive items.
      3. **AgentRolePromptBlock**: Renders `roleEnforcement` and `toneDirectives` dynamic list for agent role variant.
      4. **ProtocolPromptBlock**: Renders `protocolInstructions` field and emits updated `PromptBlock.protocol`.
      5. **RuntimeVariablesPromptBlock &amp; TaskDefinitionPromptBlock**: Renders `instructionText` field for runtime/task variants.
      6. **MatrixPromptBlock**: Renders BARS matrix scales card, row list, column list, and matrix notice.
      7. **Category Switching**: Switching category in dropdown resets/preserves common metadata and switches to appropriate sub-type.
      8. **Validation Gate**: Empty English label displays `l10n.promptBlockMandatoryEnglishError` snackbar.
      9. **Live Prompt Simulation**: Renders preview modal dialog and copy-to-clipboard action.
      10. **Negative ISTQB Partition**: Malformed or missing translation handles fail-fast gracefully without crashing Flutter widget tree.
    </action>
  </step>

  <validation_gate>
    <action>Run Localization Generation: `cd client_app_v2; flutter gen-l10n`</action>
    <action>Run Quality Gate for PromptBlockBuilderView: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart --build`</action>
    <action>Run Quality Gate for StepBuilderView: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/step_builder_view.dart --build`</action>
    <action>Run Unit Tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart --test`</action>
    <action>Run Domain Parity Gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test`</action>
  </validation_gate>
</execution_protocol>
```

