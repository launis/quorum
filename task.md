# Task Tracker: Pruning Datatype & XAI Output Extensions from Non-Matrix Prompt Block Views

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\0c442112-1f4a-4fd4-9d4a-27dd11c71e43\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Phase 1, Step 1.1 Constraint (`the_zero_compromise_pledge`): Reset non-matrix models to canonical defaults (`isEvaluative: false`, `type: BlockDataType.instruction`, `allowDecimals: false`, `outputExtensions: const []`) and Matrix models to valid sensor types (`type: floatType/intType`, `isEvaluative: true`).
- [x] Phase 1, Step 1.2 Constraint (`zero_service_layer_fallbacks`): Add in-flight submission lock using `useState(false)` in `savePromptBlock()` and guarantee non-matrix payload fields are clean before submission.
- [x] Phase 2, Step 2.1 Constraint (`progressive_disclosure_mandate`): Encapsulate XAI and Contextual Override containers inside unified `if (payload is MatrixPromptBlock) ...[...]` guard and consolidate `AppSpacing.h16` dividers to eliminate 32px double gap.
- [x] Phase 3, Step 3.1 Constraint (`anti_happy_path_mandate`): Add Matrix positive test asserting presence of `dataTypeExecutionConstraints` and `xaiOutputExtensionsTitle`.
- [x] Phase 3, Step 3.2 Constraint (`anti_happy_path_mandate`): Add 3 non-matrix negative partition tests (SystemRule, Protocol, ExecutionPersona) asserting absence of `dataTypeExecutionConstraints` and `xaiOutputExtensionsTitle`.
- [x] Phase 3, Step 3.3 Constraint (`the_zero_compromise_pledge`): Add category switch test from Matrix to System Rule asserting clean state without residual matrix attributes.
- [x] Phase 4, Step 4.1 Constraint (`quality_gate_execution`): Execute Flutter audit loop with 0 errors, 0 warnings, and 0 deprecations.

## Execution Tasks

- [x] **Phase 1: Pre-Implementation Technical Debt Cleanups**
  - [x] Step 1.1: Category Switch State Sanitization (`client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L410-L634`)
  - [x] Step 1.2: Save Payload Normalization & In-Flight Guard (`client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L223-L258`)

- [x] **Phase 2: UI Discriminator Guard Implementation**
  - [x] Step 2.1: Encapsulate XAI & Constraints Container in Matrix Discriminator (`client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L675-L909`)

- [x] **Phase 3: ISTQB Negative & Positive Test Verification**
  - [x] Step 3.1: Add Matrix Positive Test (`client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart`)
  - [x] Step 3.2: Add Non-Matrix Negative Partition Tests
  - [x] Step 3.3: Add Category Switch Sanitization Test

- [x] **Phase 4: Universal Quality Gate & Verification**
  - [x] Step 4.1: Execute Flutter Audit Loop (`uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart`)

---

# Session Handover Context

### 1. Achieved
- **Bidirectional Category Switch Sanitization**: Enforced explicit normalization in `PromptBlockBuilderView` category dropdown switch statement so non-matrix blocks reset to `type: BlockDataType.instruction`, `allowDecimals: false`, `isEvaluative: false`, `outputExtensions: const []`, and Matrix blocks reset to `isEvaluative: true` and valid sensor type (`floatType`/`intType`).
- **In-Flight Submission Lock & Save Normalization**: Added `isSaving = useState(false)` submission lock to `savePromptBlock()` with try/finally protection and normalized `savingPayload` before calling `submit()` to ensure non-matrix blocks do not leak dirty evaluative attributes to backend validators.
- **UI Progressive Disclosure Discriminator Guard**: Encapsulated both the XAI & Constraints container and the Contextual Override container within `if (payload is MatrixPromptBlock) ...[...]`, moving internal `AppSpacing.h16` divider inside to eliminate the 32px double gap.
- **ISTQB Test Suite Expansion**: Added 1 positive test (`MatrixPromptBlock`), 3 negative partition tests (`SystemRulePromptBlock`, `ProtocolPromptBlock`, `ExecutionPersonaPromptBlock`), and 1 category switch test in `prompt_block_builder_view_test.dart`. All 18 tests pass with 0 errors and 0 warnings.

### 2. Learned
- **Category Lock vs Initial Block Creation**: Checking `payload.scales?.isNotEmpty == true || payload.rows?.isNotEmpty == true || payload.columns?.isNotEmpty == true` on new blocks (`blockId == 'new'`) ensures that brand new matrix blocks with empty collections can still switch categories freely without being prematurely locked.

### 3. Remaining Work
- None. All phases and steps in the implementation plan are completed and verified.

### 4. Mandatory Red-Team Audit Gate
- To perform an independent System 2 Red-Team audit of this implementation plan in a fresh context window, invoke:
  `/tier8-audit-plan @[C:\Users\risto\.gemini\antigravity-ide\brain\0c442112-1f4a-4fd4-9d4a-27dd11c71e43\implementation_plan.md]`
