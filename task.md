<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
</required_context_rules>

# Task Tracker: Fix Report Generation & Regeneration Deadlock

## Session Handover Context
- **Achieved**: Completed Tier 0 deep System 2 research, 5-axis architectural deconstruction, Redis key lifecycle analysis, touched scope tech debt sweep, and Red-Team falsification. Identified exact root causes: Arq `arq:result:` key caching causing silent job drop on regeneration, and premature client invalidation causing 409 DioExceptions.
- **Learned**: Arq caches completed job results under `arq:result:{_job_id}` for `result_ttl` (3600s), silently returning `None` on subsequent `enqueue_job` calls with the same `_job_id`. Calling `await arq_pool.delete(f"arq:result:{job_key}")` clears the completed cache while preserving `arq:job:{job_key}` in-flight deduplication.
- **Remaining**: Execute Steps 1-7 via `/tier2-execute`.
- **Resume Command**: `/tier2-execute @[c:\Users\risto\.gemini\antigravity-ide\brain\ab9049bf-d46b-43fc-b599-f23052d637e2\implementation_plan.md] @[task.md]`

## Execution Steps
- [x] Step 1: Pre-Implementation Cleanups: Type `arq_pool: ArqRedis` with `if TYPE_CHECKING:` in `@[backend_v2/services/report_service.py#L276-L288]` and `@[backend_v2/services/report_service.py#L665-L673]`. In `@[client_app_v2/lib/features/reports/views/execution_reports_view.dart#L708-L716]`, replace hardcoded string `'SDUI-lataus epäonnistui: $err'` with `l10n.reportGenerationFailedNotice` and provide an explicit Retry button.
- [x] Step 2: In `@[backend_v2/services/report_service.py#L276-L288]`, update `compile_and_persist_artifact` to await `arq_pool.delete(f"arq:result:{job_key}")` before calling `arq_pool.enqueue_job`. Consolidate report compilation in `@[backend_v2/workers/synthesis_worker.py#L140-L154]`, `@[backend_v2/workers/synthesis_worker.py#L518-L528]`, and `@[backend_v2/workers/synthesis_reducers.py#L355-L365]` to delegate cleanly to `ReportService.compile_and_persist_artifact`.
- [ ] Step 3: In `@[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart#L103-L125]`, remove premature invalidation of `reportSduiProvider` and `reportRowsProvider` in `regenerateReport`; in `reportDetail` (`@[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart#L34-L50]`), add `ref.listenSelf` to trigger invalidation of both providers when `previous.status != ready && next.status == ready`.
- [ ] Step 4: Run regression unit tests: `uv run pytest backend_v2/tests/unit/services/test_report_service.py::test_regenerate_report_artifact_clears_stale_arq_result` and `test_compile_and_persist_artifact`.
- [ ] Step 5: Run backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/services/report_service.py --test`.
- [ ] Step 6: Run flutter quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart`.
- [ ] Step 7: Clear stranded live report record in `@[data/db_v2.json]` (specifically `rep_bf56b0aebceb46e3`) if present.


