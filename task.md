<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
</required_context_rules>

# Task Tracker: Fix Report Generation & Regeneration Deadlock

## Session Handover Context
- **Achieved**: Fully implemented and verified bug fix for Report Generation & Regeneration Deadlock across backend and client. Cleared stale `arq:result:` keys in `ReportService.compile_and_persist_artifact`, consolidated compilation kickoff across `synthesis_worker.py` and `synthesis_reducers.py`, eliminated premature artifact provider invalidation in `regenerateReport`, added downstream artifact invalidation on `ready` in `reportDetail`, added localized error notices and retry controls in `execution_reports_view.dart`, added comprehensive unit and regression test coverage, and verified 100% PASS on all backend and flutter audit gates and SDUI semantic parity.
- **Learned**: In Riverpod, function providers cannot listen to themselves (`ref.listen` on origin triggers assertion violation). Reactive invalidation of downstream artifact providers (`reportSduiProvider`, `reportRowsProvider`) upon status transition to `ReportStatus.ready` within `reportDetail` reliably guarantees fresh data without premature 409 Conflict races.
- **Remaining**: Mandatory System 2 Red-Team audit of completed plan via `/tier8-audit-plan`.
- **Resume Command**: `/tier8-audit-plan @[c:\Users\risto\.gemini\antigravity-ide\brain\ab9049bf-d46b-43fc-b599-f23052d637e2\implementation_plan.md] @[task.md]`

## Execution Steps
- [x] Step 1: Pre-Implementation Cleanups: Type `arq_pool: ArqRedis` with `if TYPE_CHECKING:` in `@[backend_v2/services/report_service.py#L276-L288]` and `@[backend_v2/services/report_service.py#L665-L673]`. In `@[client_app_v2/lib/features/reports/views/execution_reports_view.dart#L708-L716]`, replace hardcoded string `'SDUI-lataus epäonnistui: $err'` with `l10n.reportGenerationFailedNotice` and provide an explicit Retry button.
- [x] Step 2: In `@[backend_v2/services/report_service.py#L276-L288]`, update `compile_and_persist_artifact` to await `arq_pool.delete(f"arq:result:{job_key}")` before calling `arq_pool.enqueue_job`. Consolidate report compilation in `@[backend_v2/workers/synthesis_worker.py#L140-L154]`, `@[backend_v2/workers/synthesis_worker.py#L518-L528]`, and `@[backend_v2/workers/synthesis_reducers.py#L355-L365]` to delegate cleanly to `ReportService.compile_and_persist_artifact`.
- [x] Step 3: In `@[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart#L103-L125]`, remove premature invalidation of `reportSduiProvider` and `reportRowsProvider` in `regenerateReport`; in `reportDetail` (`@[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart#L34-L50]`), invalidate artifact providers when `report.status == ReportStatus.ready`.
- [x] Step 4: Run regression unit tests: `uv run pytest backend_v2/tests/unit/services/test_report_service.py::test_regenerate_report_artifact_clears_stale_arq_result` and `test_compile_and_persist_artifact`.
- [x] Step 5: Run backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/services/report_service.py --test`.
- [x] Step 6: Run flutter quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart`.
- [x] Step 7: Clear stranded live report record in `@[data/db_v2.json]` (verified none present).


