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
- [ ] **Phase 0 Task 0.1:** Delete the rogue `__pycache__/` directory inside `docs/architecture/` using a native powershell command via `run_command` (e.g. `Remove-Item -Recurse -Force docs\architecture\__pycache__`).

### docs/architecture/04_server_driven_ui_and_presentation.md
- [ ] Synthesize any exclusive conceptual knowledge from the "Physical Implementation Map" into the theoretical sections.
- [ ] Remove the "Physical Implementation Map" section entirely.
- [ ] Remove all historical references.
- [ ] Ensure no inline physical file paths remain in theoretical text.

### docs/architecture/05_resilience_and_observability.md
- [ ] Synthesize any exclusive conceptual knowledge from the "Physical Implementation Map" into the theoretical sections.
- [ ] Remove the "Physical Implementation Map" section entirely.
- [ ] Remove all historical references.
- [ ] Ensure no inline physical file paths remain in theoretical text.

### docs/architecture/06_enriched_atom_graph_engine.md
- [ ] Synthesize any exclusive conceptual knowledge from the "Physical Implementation Map" into the theoretical sections.
- [ ] Remove the "Physical Implementation Map" section entirely (Note: inconsistent numbering `## 3. Physical Implementation Map`).
- [ ] Remove inline paths (`**Path:** backend_v2/...`) from components (Extractive Sensor Service, Topological Evaluator, Result Projector, Sliding Window Linker).
- [ ] Remove historical references.
- [ ] Line 29 (or matching sentence): Remove "Following the Universal DTO Bridge (Epic 91.5)" and replace with: "The engine strictly decouples logical graph execution from server-driven UI elements."

## Testing & Quality Gate Plan
- Verify zero matches for `Epic`, `V1`, `legacy` etc. using `grep_search`.
