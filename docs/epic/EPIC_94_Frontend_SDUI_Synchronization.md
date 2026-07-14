# Epic 94: Frontend SDUI Synchronization (Flutter V2)

## Context & Objective
In Epics 91.5, 92, and 93, the Quorum Backend was completely modernized to a strict, Single Source of Truth (SSOT) architecture using Pydantic V2. The legacy Pipeline B ("God Code") was erased, and the backend now serves a highly optimized, flat adjacency list payload for the Server-Driven UI (SDUI). 

The Flutter Frontend (`client_app_v2`), however, still uses the obsolete `ReportDataDTO` (which expects massive nested `layouts`, `evaluative_matrices`, and `grouped_extensions`). If the frontend attempts to parse the new V2 payload, the `disallowUnrecognizedKeys: true` firewall will trigger an immediate crash.

**Objective**: Synchronize the Flutter Frontend's Dart 3 Freezed models, Riverpod state managers, and Widget rendering components with the new Backend `ReportDataDto` contract.

## Architectural Safeguards & Red-Teaming
1. **Producer/Consumer:** The Backend is the pure Producer (serves `results` and `hydrated_references`). The Flutter application is the pure Consumer. The frontend MUST NOT re-compute DAG dependencies or perform topological sorts; it only renders the data based on the `SDUIComponentType` hints.
2. **Performance Constraints:** The new payload uses a flat adjacency list. The frontend MUST utilize `ref.watch` intelligently to bind individual `AtomResultDTO` nodes to their respective widgets via O(1) dictionary lookups (`hydrated_references`), avoiding O(N^2) list parsing during 60fps renders.
3. **Fail-Fast Boundary:** All new Freezed models MUST enforce `@JsonSerializable(disallowUnrecognizedKeys: true)`. Missing required fields must crash the parsing natively so `AppErrorBoundary` can intercept it. No silent fallbacks or `SizedBox.shrink()` are allowed.
4. **Knowledge Base:** This Epic will rely heavily on `ki_app_error_boundary.md` and `ki_strict_icu_markdown_parity.md`.

## Execution Phases

### Phase 0: Backend SDUI Output Rendering Unification & Hardening (Completed)
**Goal:** Enforce Single Source of Truth (SSOT), Fail-Fast, and No Fallback mandates on the backend before the frontend consumes the new API.
- [x] Wire `row_explanations_block_id` and `formatting_directives` into the Database Seed Data (`OutputProfile` → `SynthesisConfigDTO`).
- [x] Enforce single-source synthesis prompt in `worker.py` (removing dual-source fallback chains).
- [x] Implement deterministic Python enforcement (Sandwich Architecture) in `BlueprintTransformer` (e.g., PII masking, truncation, layout filtering).
- [x] Eradicate legacy string fallbacks (`justification`) and dead code from `hook_prompts.py`.
- [x] Re-align all backend unit tests (`test_execution.py`, `test_chat_parser.py`, `test_llm_task_executor.py`) with Pydantic V2 and the new `ReportDataDto` contract.
- [x] Pass the `/tier2-hardening-backend` audit loop ensuring strict 30% TDD coverage.

### Phase 1: Freezed Models Synchronization
**Goal:** Create the new Dart Freezed schemas to mirror `backend_v2/models/dtos/report/`.
- [x] Create `atom_result_dto.dart` mapped to backend `AtomResultDTO` (including `ExtractedValueDTO` and `ErrorDetailsDTO`).
- [x] Create `hydrated_atom_dto.dart` mapped to backend `HydratedAtomDTO` (including `SDUIComponentType` enum mappings in `enums.dart`).
- [x] Create `global_synthesis_dto.dart` mapped to backend `GlobalSynthesisDTO`.
- [x] Create `report_data_v2_dto.dart` representing the new root payload structure (`execution_id`, `global_metrics`, `global_synthesis`, `results`, `hydrated_references`).

### Phase 2: Riverpod State Providers (O(1) Data Binding)
**Goal:** Abstract the `report_data_v2_dto` payload into granular Riverpod Notifiers to prevent full-screen re-renders.
- [x] Implement `HydratedReferenceProvider` to serve O(1) lookups for static `HydratedAtomDTO` ontology.
- [x] Implement `AtomResultListProvider` to expose the topologically sorted `results` array.
- [ ] Ensure tenant/organization boundary caches are flushed on execution load (`ref.invalidate`).

### Phase 3: SDUI Widget Rendering Components
**Goal:** Build responsive, Macro-Breakpoint compliant UI widgets that react exclusively to the new V2 models.
- [x] Implement a unified `SduiNodeRenderer` widget that uses Dart 3 `switch` expressions on `SDUIComponentType` to determine the layout (e.g., `hero_insight`, `bullet_list`, `alert_box`).
- [x] Ensure all dynamic strings utilize exact matching without fallback generic strings (`ki_strict_translation_fallback_mandate`).
- [ ] Implement `MatrixReducer` compatibility on the frontend to render compressed Token Matrices.
- [x] Incorporate **Polymorphic Rule Routing & Synthesis Mapping** by ensuring the frontend correctly parses dynamically mapped `global_synthesis` blocks (driven by the backend's `OutputProfile.synthesis_block_id` injection).

### Phase 4: Erase Legacy Models & Views
**Goal:** Clean up the codebase to enforce SSOT.
- [ ] Safely sunset the old monolithic `report_data_dto.dart` and `scorecard_dto.dart`.
- [ ] Delete deprecated UI widgets that relied on the nested `layouts` arrays.
- [ ] Perform a full UI End-to-End audit to verify Baseline Parity for report rendering.

---

## Instructions for the Execution Agent
To begin the execution of this Epic, start a NEW chat session and run the Tier 1 Planner command to generate the specific file-by-file `implementation_plan.md` for Phase 1:

`/tier1-planner --target="c:\src\quorum\docs\epic\EPIC_94_Frontend_SDUI_Synchronization.md"`
