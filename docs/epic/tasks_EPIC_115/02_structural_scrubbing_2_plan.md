# EPIC 115 Phase 0 & 1: Structural Scrubbing (Pillars 4-6)

Phase 1 MUST be purely structural.
Source: Epic Phase 0 (Task 0.1) & Phase 1 (Tasks 1.1 & 1.2)

## TARGET Files (Modify)
- @[c:\src\quorum\docs\architecture\04_server_driven_ui_and_presentation.md]
- @[c:\src\quorum\docs\architecture\05_resilience_and_observability.md]
- @[c:\src\quorum\docs\architecture\06_enriched_atom_graph_engine.md]

## CONTEXT Files (Read-Only)
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]
- @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md]

## Proposed Changes

### docs/architecture/__pycache__/
- [x] **Phase 0 Task 0.1:** Delete the rogue `__pycache__/` directory using a native powershell command via `run_command` (e.g. `Remove-Item -Recurse -Force docs\architecture\__pycache__ -ErrorAction SilentlyContinue`).

### docs/architecture/04_server_driven_ui_and_presentation.md
- [x] Synthesize the conceptual knowledge of "BFF SDUI Translation" (`sdui_mapper_service.py`) and the "3-Part UI Layout Block Editor" (`layout_editor_card.dart`) into the theoretical sections.
- [x] Remove the "Physical Implementation Map" section entirely.
- [x] Search for and remove any of these historical terms: `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d`.
- [x] Ensure no inline physical file paths remain in theoretical text (e.g., Line 4 references `` `client_app_v2` / Flutter `` -> change to `Flutter frontend`).

### docs/architecture/05_resilience_and_observability.md
- [x] Synthesize the conceptual roles of "Compliance Guardrail" (PII Analyzer) and "Observability/Usage Tracking" (`progress.py`/`usage_service.py`) into the theoretical sections.
- [x] Remove the "Physical Implementation Map" section entirely.
- [x] Search for and remove any of these historical terms: `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d`.
- [x] Ensure no inline physical file paths remain in theoretical text.

### docs/architecture/06_enriched_atom_graph_engine.md
- [x] Synthesize the conceptual roles of "Chat Parser" and "Source Verification Service" into the theoretical sections.
- [x] Remove the "Physical Implementation Map" section entirely (Note: inconsistent numbering `## 3. Physical Implementation Map`).
- [x] Remove inline paths (`**Path:** backend_v2/...`) from components (Extractive Sensor Service, Topological Evaluator, Result Projector, Sliding Window Linker).
- [x] Search for and remove any of these historical terms: `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d`.
- [x] Line 29 (or matching sentence): Remove "Following the Universal DTO Bridge (Epic 91.5)" and replace with: "The engine strictly decouples logical graph execution from server-driven UI elements."

## Testing & Quality Gate Plan
- Verify zero matches for `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d` using `grep_search`.
- Verify zero matches for `backend_v2` or `client_app_v2` in the remaining text.
