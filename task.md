# Task Tracker: Studio Workflow Step Simulation & Prompt Preview Architecture

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_matrix_sensor_prompt_builder.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\e09a5c6c-95b7-4e8f-ba14-3fca4d7cc65b\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Step 1 Constraint (`the_zero_compromise_pledge`): Eliminate naked dictionaries in StepSimulationResponse and duplicate preview dialogs across Studio editors.
- [x] Step 1 Constraint (`ssot_reuse_mandate`): Extract shared UI dialog to prevent parallel duplicate preview implementations.
- [x] Step 2 Constraint (`static_first_caching_topology`): Isolate static instructions in static_messages prefix and dynamic claims in dynamic_messages.
- [x] Step 2 Constraint (`zero_service_layer_fallbacks`): Forward explicit parameters without lazy fallback operators.
- [x] Step 3 Constraint (`the_zero_compromise_pledge`): Eliminate naked Map<String, dynamic> transit in Flutter Studio.
- [x] Step 3 Constraint (`silent_json_fallbacks`): Enforce disallowUnrecognizedKeys: true in JSON serialization.
- [x] Step 4 Constraint (`rigid_macro_breakpoint_standard`): Enforce responsive layout via LayoutBuilder (Two-Pane >= 900px vs Single Column < 900px).
- [x] Step 4 Constraint (`desktop_pro_tool_interaction`): Support mouse hover, keyboard focus, and Escape key dismissal.
- [x] Step 5 Constraint (`universal_quality_gate`): Enforce automated audit loop on all touched files with >90% coverage and zero warnings.
- [x] Step 6 Constraint (`metadata_json_ssot_mandate`): Every Knowledge Item MUST maintain strict 5-field schema with workspace-relative references that physically exist on disk.
- [x] Step 7 Constraint (`timeless_as_built_mandate`): Describe purely and exclusively what the system currently has and how it operates right now ("kerro ainoastaan ja puhtaasti se mitä meillä on nyt").

## Execution Tasks

- [x] **Step 1: Technical Debt Remediation & SSOT UI Extraction (Debts 1-14)**
  - [x] Export `StepSimulationTraceDTO` in `backend_v2/models/dtos/studio.py`.
  - [x] Add `StepSimulationTraceDTO` and update `StepSimulationResponse.trace`.
  - [x] Enhance `StepSimulationRequest` with `target_locale`, `context_text`, and comment on `mock_inputs`.
  - [x] Extract `PromptPreviewDialog` and `PromptPreviewFormatter` to `client_app_v2/lib/features/studio/views/widgets/prompt_preview_dialog.dart`.
  - [x] Refactor `scale_editor_modal.dart` to use `PromptPreviewDialog` and replace `showSnackBar` with in-modal error alert.

- [x] **Step 2: Backend Simulation Engine & Router Upgrade**
  - [x] Upgrade `simulate_step` in `backend_v2/services/studio/simulation_service.py` to accept `target_locale`, `context_text`.
  - [x] Resolve blocks in DAG order: `role_block_id`, `extraction_protocol_block_id`, `execution_persona_block_id`, `criteria_block_ids`.
  - [x] Aggregate `static_messages` and `dynamic_messages` into `PromptContextDTO`.
  - [x] Calculate BPE token estimation and return `StepSimulationTraceDTO`.
  - [x] Update router in `backend_v2/api/routers/studio/steps.py`.

- [x] **Step 3: Frontend Freezed DTOs and Client Layer**
  - [x] Create `@Freezed(equal: false)` models in `client_app_v2/lib/features/studio/models/step_simulation.dart`.
  - [x] Generate Freezed code via audit loop (`--build`).
  - [x] Strongly type `simulateStep` in `studio_client.dart` and `studio_controller.dart`.

- [x] **Step 4: Frontend Step Simulation Modal & UI Wiring**
  - [x] Add localized strings to `app_en.arb` and `app_fi.arb`, compile with `flutter gen-l10n`.
  - [x] Create `StepSimulationDialog` in `client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart`.
  - [x] Wire bug icon button in `step_builder_view.dart` to open `StepSimulationDialog`.

- [x] **Step 5: Quality Gates & Test Verification**
  - [x] Fix MyPy strictness in `backend_v2/tests/unit/services/studio/test_simulation_service.py` and `backend_v2/tests/unit/api/routers/studio/test_steps.py`.
  - [x] Pass backend audit loop on `simulation_service.py` (97% coverage), `test_simulation_service.py` (17/17 passed), `test_steps.py` (8/8 passed, 100% coverage), and `test_studio.py` (14/14 passed, 99% coverage).
  - [x] Pass Flutter audit loop on `client_app_v2/lib/features/studio/views/widgets/` (0 issues).
  - [x] Pass widget tests on `step_simulation_dialog_test.dart` (6/6 passed) and `scale_editor_modal_test.dart` (17/17 passed).
  - [x] Pass SDUI semantic parity test (`test_sdui_semantic_parity.py`).

- [x] **Step 6: Knowledge Base Hardening & Metadata Synchronization**
  - [x] Update `ki_matrix_sensor_prompt_builder.md` and `metadata.json` (added `step_level_simulation_prompt_parity` rule).
  - [x] Update `ki_desktop_pro_tool_studio_ux.md` and `metadata.json` (added `prompt_preview_dialog_ssot_standard`, `step_simulation_dialog_standard`, and catalog updates).
  - [x] Update `ki_workflow_context_governance.md` and `metadata.json` (added `step_authoring_simulation_validation` rule).

- [x] **Step 7: As-Built Architectural Documentation**
  - [x] Update Section 2.11 in `docs/architecture/04_server_driven_ui_and_presentation.md`.
  - [x] Update Sections 9.1 and 9.2 in `docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md`.
  - [x] Pass automated regex scan for banned historical/meta markers.

---

# Session Handover Context

### 1. Achieved
- **Full Backend Simulation Modernization**: `simulate_step()` now resolves prompt blocks in exact DAG execution order (`role_block_id`, `extraction_protocol_block_id`, `execution_persona_block_id`, `criteria_block_ids`), aggregates both `static_messages` (prefix caching) and `dynamic_messages` (CDATA-shielded runtime parameters), calculates BPE token estimates (`len(m.content) // 4`), forwards `target_locale` and `context_text`, and returns strongly typed `StepSimulationTraceDTO`.
- **Zero Permissive Typing Across Full Stack**: Eradicated naked `dict[str, Any]` and `Map<String, dynamic>` transit across boundaries. Defined `@Freezed(equal: false)` models `StepSimulationRequest`, `StepSimulationResponse`, `StepSimulationTraceDto`, `PromptContextDto`, and `LlmMessageDto` with `disallowUnrecognizedKeys: true`.
- **SSOT UI Dialog Extraction**: Extracted `PromptPreviewDialog` and `PromptPreviewFormatter` to a public reusable Studio widget, refactored `ScaleEditorModal` to use it, and eliminated modal-external `SnackBar` in favor of an ergonomic `AlertDialog`.
- **Desktop Step Simulation Modal**: Built `StepSimulationDialog` with two-pane responsive desktop layout, dynamic input generation for each key declared in `step.expectedInputs`, context text editor, target locale dropdown, execution time / token count telemetry chips, and tabbed prompt preview.
- **Universal Quality Gates 100% PASS**: Pytest unit tests, Ruff, MyPy strict mode, Flutter analyze, widget tests, and SDUI semantic parity verified with 0 warnings and >95% coverage.
- **Knowledge Base & As-Built Architecture**: Hardened 3 Knowledge Items (`ki_matrix_sensor_prompt_builder.md`, `ki_desktop_pro_tool_studio_ux.md`, `ki_workflow_context_governance.md`) and synchronized architectural pillars `04_` and `09_` under the Timeless As-Built Mandate.

### 2. Learned
- **Pydantic V2 / MyPy Strict Constructor Semantics**: `Annotated[T, Field(default=...)]` does not declare a Python class-level default unless an assignment `= ...` or `= Field(default_factory=...)` is physically present on the class attribute. Adding class-level default assignments resolves MyPy `call-arg` errors while preserving PEP 593 strictness.
- **In-Modal Alert Dialogs**: In Flutter desktop modals, replacing `ScaffoldMessenger.showSnackBar` with `showDialog(builder: (_) => AlertDialog(...))` ensures that error messages display inside the active modal viewport and do not bleed outside to the parent Scaffold.

### 3. Remaining Work
- None. All 7 steps in the implementation plan are 100% complete and verified.

### 4. Mandatory Red-Team Audit Gate
- To perform an independent System 2 Red-Team audit of this implementation, invoke:
  `/tier8-audit-plan @[c:\Users\risto\.gemini\antigravity-ide\brain\e09a5c6c-95b7-4e8f-ba14-3fca4d7cc65b\implementation_plan.md]`
