# Symbol Migration Map: `backend_v2/services/report_service.py`

This artifact maps every symbol in `backend_v2/services/report_service.py` to its target domain sub-module under `backend_v2/services/report/`.

## 1. Domain Bounded Contexts

| Bounded Context | Target File | Responsibility |
| :--- | :--- | :--- |
| **Lifecycle** | `@[backend_v2/services/report/lifecycle_service.py]` | Report artifact CRUD, draft creation, public report generation, and deletion. |
| **Compilation** | `@[backend_v2/services/report/compilation_service.py]` | Multi-format artifact generation (SDUI, PDF, XLSX, CSV), background synthesis dispatch, and DLQ handling. |
| **Format Reader** | `@[backend_v2/services/report/format_reader_service.py]` | Storage reading, artifact deserialization, format byte streams, and tabular row projections. |
| **Package Entrypoint** | `@[backend_v2/services/report/__init__.py]` | Canonical package root and typed facade re-exporting `ReportService`. |

## 2. Exhaustive Symbol-to-Target Mapping

| Original Symbol | Source Bounds | Target Module | Future Symbol Name |
| :--- | :--- | :--- | :--- |
| `get_report` | `@[backend_v2/services/report_service.py#L70-L91]` | `@[backend_v2/services/report/lifecycle_service.py]` | `ReportLifecycleService.get_report` |
| `list_reports_for_execution` | `@[backend_v2/services/report_service.py#L93-L115]` | `@[backend_v2/services/report/lifecycle_service.py]` | `ReportLifecycleService.list_reports_for_execution` |
| `create_report_artifact` | `@[backend_v2/services/report_service.py#L117-L191]` | `@[backend_v2/services/report/lifecycle_service.py]` | `ReportLifecycleService.create_report_artifact` |
| `get_or_create_default_artifact` | `@[backend_v2/services/report_service.py#L193-L270]` | `@[backend_v2/services/report/lifecycle_service.py]` | `ReportLifecycleService.get_or_create_default_artifact` |
| `delete_report_artifact` | `@[backend_v2/services/report_service.py#L653-L690]` | `@[backend_v2/services/report/lifecycle_service.py]` | `ReportLifecycleService.delete_report_artifact` |
| `regenerate_report_artifact` | `@[backend_v2/services/report_service.py#L692-L699]` | `@[backend_v2/services/report/lifecycle_service.py]` | `ReportLifecycleService.regenerate_report_artifact` |
| `get_public_report` | `@[backend_v2/services/report_service.py#L701-L749]` | `@[backend_v2/services/report/lifecycle_service.py]` | `ReportLifecycleService.get_public_report` |
| `compile_and_persist_artifact` | `@[backend_v2/services/report_service.py#L272-L298]` | `@[backend_v2/services/report/compilation_service.py]` | `ReportCompilationService.compile_and_persist_artifact` |
| `process_artifact_compilation` | `@[backend_v2/services/report_service.py#L300-L473]` | `@[backend_v2/services/report/compilation_service.py]` | `ReportCompilationService.process_artifact_compilation` |
| `_dispatch_report_compilation_dlq` | `@[backend_v2/services/report_service.py#L475-L493]` | `@[backend_v2/services/report/compilation_service.py]` | `ReportCompilationService._dispatch_report_compilation_dlq` |
| `_read_artifact` | `@[backend_v2/services/report_service.py#L495-L534]` | `@[backend_v2/services/report/format_reader_service.py]` | `ReportFormatReaderService._read_artifact` |
| `get_report_sdui` | `@[backend_v2/services/report_service.py#L536-L551]` | `@[backend_v2/services/report/format_reader_service.py]` | `ReportFormatReaderService.get_report_sdui` |
| `get_report_pdf_bytes` | `@[backend_v2/services/report_service.py#L553-L567]` | `@[backend_v2/services/report/format_reader_service.py]` | `ReportFormatReaderService.get_report_pdf_bytes` |
| `get_report_excel_bytes` | `@[backend_v2/services/report_service.py#L569-L583]` | `@[backend_v2/services/report/format_reader_service.py]` | `ReportFormatReaderService.get_report_excel_bytes` |
| `get_report_csv_bytes` | `@[backend_v2/services/report_service.py#L585-L599]` | `@[backend_v2/services/report/format_reader_service.py]` | `ReportFormatReaderService.get_report_csv_bytes` |
| `get_report_rows` | `@[backend_v2/services/report_service.py#L601-L643]` | `@[backend_v2/services/report/format_reader_service.py]` | `ReportFormatReaderService.get_report_rows` |
| `_dlq_log_absent_storage_artifact` | `@[backend_v2/services/report_service.py#L645-L651]` | `@[backend_v2/services/report/format_reader_service.py]` | `ReportFormatReaderService._dlq_log_absent_storage_artifact` |
| `ReportService` (Facade) | `@[backend_v2/services/report_service.py#L42-L68]` | `@[backend_v2/services/report/__init__.py]` | `ReportService` (Aggregator Facade) |

## 3. External 1-Hop Consumer Blast Radius

| Consumer File | Current Import | Target Import (Mechanical Rewiring) |
| :--- | :--- | :--- |
| `backend_v2/api/routers/execution/reports.py` | `from backend_v2.services.report_service import ReportService` | `from backend_v2.services.report import ReportService` |
| `backend_v2/workers/report_worker.py` | `import backend_v2.services.report_service as report_service_mod` | `import backend_v2.services.report as report_service_mod` |
| `backend_v2/workers/synthesis_worker.py` | `from backend_v2.services.report_service import ReportService` | `from backend_v2.services.report import ReportService` |
| `backend_v2/workers/synthesis_reducers.py` | `from backend_v2.services.report_service import ReportService` | `from backend_v2.services.report import ReportService` |
