# Task Execution Tracker: Output Profile Studio Parity, Save Fix, Graph Modernization & Prompt Architecture Segregation

## [x] Pre-Flight Codebase Scan & Baseline Analysis

## Phase 1: PROMPT ARCHITECTURE SEGREGATION & BACKEND PARITY
- [x] Step 1.1: Clean 3-Way Prompt Module Segregation (`sdui_directives.py`, `style_directives.py`, `synthesis_directives.py`, `hook_prompts.py`, `__init__.py`)
- [x] Step 1.2: Declare PresetView Enum & Test Pre-hydration (`enums.py`, test files)
- [x] Step 1.3: Update Domain Models & DTOs for PresetView and Matrix Columns (`v2_core.py`, `output_profile.py`)
- [x] Step 1.4: Update OutputProfile Router & Background Worker Synthesis Pipeline Integration (`output_profiles.py`, `worker.py`)
- [x] Step 1.5: Update SDUI Presentation Adapters (`matrix_graphs_adapter.py`, `matrix_summary_table_adapter.py`)

## Phase 2: FLUTTER CLEANUP, SYNTHESIS CARD REMOVAL & EXACT MATRIX VIEWTYPE GUIDANCE
- [x] Step 2.1: Update Flutter Freezed Models & Run Code Generation (`output_profile.dart`, flutter_audit_loop)
- [x] Step 2.2: Demolish SynthesisTextBlockCard and Clean BlockCardRegistry (`synthesis_text_block_card.dart`, `block_card_registry.dart`, `profile_layouts_tab.dart`)
- [x] Step 2.3: Refactor MatrixGraphItemEditor with Exact Slot Constraints (`matrix_graph_item_editor.dart`)
- [x] Step 2.4: Refactor MatrixSummaryTableCard for Column Selection (`matrix_summary_table_card.dart`)

## Phase 3: VERIFICATION & QUALITY GATES
- [x] Step 3.1: Backend Unit Tests & Quality Gate (`test_output_profile_studio_parity.py`, `backend_audit_loop.py`)
- [x] Step 3.2: Flutter Widget Tests & Quality Gate (`matrix_graph_editor_test.dart`, `flutter_audit_loop.py`)

## Learnings & Deviations
- `AdapterContext` requires `import backend_v2.models.state` in unit test files to fully resolve `ErrorTraceEvent` before model initialization.
- AST Guardrail QGR011 enforces that `OutputProfileCreateDTO` must strictly NOT have an `id` field, while `OutputProfileUpdateDTO` accepts `id: str | None = None` for client `PUT` requests without causing `extra_forbidden` errors.
