# Epic 91.5 Phase C — Frontend Pipeline Unification Tracker

> **Origin:** Red-Teamed `implementation_plan.md` from conversation `662c356b`
> **Architecture:** Unify the dual Scorecard+SDUI rendering pipelines into a single `ReportDataDto` pipeline.
> **Root Cause:** Flutter `ReportDataDto` was a broken 6-field placeholder; backend `ReportDataDTO` already contained all data.

---

## Phase C Execution Tasks

- `[x]` **C0 — Backend Schema Fix:** Add `execution_id` to `ReportDataDTO` → [C0_backend_schema_fix.md](file:///c:/src/quorum/docs/epic/tasks_epic_91_5_phase_c/C0_backend_schema_fix.md) *(Backend only, 2 files)*
- `[x]` **C1 — Flutter DTO Rewrite:** Rewrite `ReportDataDto` + create `ReportLayoutDto`, `SynthesisConfigDto` → [C1_flutter_dto_rewrite.md](file:///c:/src/quorum/docs/epic/tasks_epic_91_5_phase_c/C1_flutter_dto_rewrite.md) *(Frontend only, 3 files)*
- `[NOK]` **C2 — DTO Relocation:** Move scorecard classes to `matrix_scorecard_dto.dart` → [C2_dto_relocation.md](file:///c:/src/quorum/docs/epic/tasks_epic_91_5_phase_c/C2_dto_relocation.md)
- `[NOK]` **C3 — Scorecard Pipeline Delete:** Remove `/scorecard` endpoint + frontend consumers → [C3_scorecard_pipeline_delete.md](file:///c:/src/quorum/docs/epic/tasks_epic_91_5_phase_c/C3_scorecard_pipeline_delete.md)
- `[NOK]` **C4 — UI Rewiring:** Connect widgets to unified `ReportDataDto` → [C4_ui_rewiring.md](file:///c:/src/quorum/docs/epic/tasks_epic_91_5_phase_c/C4_ui_rewiring.md)
- `[NOK]` **C5 — Controller Updates:** Fix `_performHeavyFetch` and `ReportController` → [C5_controller_updates.md](file:///c:/src/quorum/docs/epic/tasks_epic_91_5_phase_c/C5_controller_updates.md)

---

## Structural Quality Gates

- `[x]` **Proxy Sunset & Consumer Migration:** Codebase-wide search/replace old `scorecard_dto.dart` import paths. Verify no orphaned imports remain.
- `[NOK]` **Tier 2 Hardening (Backend):** Run `/tier2-hardening-backend` on `backend_v2/models/` and `backend_v2/services/blueprint.py` after C0 is committed.
- `[NOK]` **Tier 2 Hardening (Frontend):** Run `/tier2-hardening-frontend` on `client_app_v2/lib/features/execution/models/` after C1+C2 are committed.
- `[NOK]` **Pre-Delete Audit:** Verify `scorecard_dto.dart`, `scorecard_provider.dart`, `async_scorecard_widget.dart` have zero consumers before deletion. Verify `ScorecardResponseDTO` and `get_scorecard_dto` have zero external callers.
- `[x]` **Baseline Parity & Zero-Loss Audit:** Verify that the final test count and coverage match or exceed the `[BASELINE]` recorded at start.

---

## Instructions for the Execution Agent

1. Execute tasks in strict sequential order (C0 → C1 → Re-invoke Tier 1 → C2 → C3 → C4 → C5).
2. After completing each task, run the corresponding Quality Gate command from the plan.
3. Perform an atomic `git commit` after each passing Quality Gate.
4. **BEFORE handing over the session**, update the `/tier5-resume` command below with your progress.
5. Execute tasks C2-C5 sequentially.

---

## Documentation Updates

- `[NOK]` Update `.agents/rules/04_directory_reference.md` with new model files (`report_layout_dto.dart`, `synthesis_config_dto.dart`, `matrix_scorecard_dto.dart`).
- `[NOK]` Update `docs/architecture/` if any architecture docs reference the dual scorecard pipeline.

---

# Session Handover Context

## Achieved
- Red-teamed the original `implementation_plan.md` and discovered 4 critical weaknesses.
- Generated Tier 1 micro-chunked plans for Phase C0 (backend, detailed) and C1 (Flutter, detailed).
- Re-invoked Tier 1 Planner and generated detailed plans for C2-C5.

## Learned
- Backend `ReportDataDTO` does NOT have `execution_id` — must be added (C0).
- Flutter `ReportDataDto` is a broken 6-field placeholder that silently crashes `_performHeavyFetch`.
- The `/scorecard` endpoint is a pure re-wrap of `build_report_dto()` — completely redundant.
- `SynthesisConfigDTO` has 15+ fields; use `disallowUnrecognizedKeys: false` for Flutter model.
- Backend has no `global_synthesis` field — uses `content_blocks` instead.
- `TDAState` Freezed union MUST be preserved (O(1) pattern matching).
- Dart `export` can act as a proxy to prevent immediate import breakages during C2 relocation.

## Remaining
- Execute C2-C5 (relocation, deletion, rewiring, controllers)
- Quality gates: Proxy sunset, Tier 2 hardening, pre-delete audit, baseline parity

---

```
/tier5-resume --workflow=/tier2-execute --target="c:\src\quorum\docs\epic\epic_91_5_phase_c_tracker.md, c:\src\quorum\docs\epic\EPIC_91_5_DTO_Bridge.md" --rules="00-antigravity-core.md, 01-python-backend.md, 02_flutter_desktop.md"
```
