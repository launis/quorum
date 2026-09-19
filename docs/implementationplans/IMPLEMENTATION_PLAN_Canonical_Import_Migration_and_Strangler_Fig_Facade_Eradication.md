<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Plan: Canonical Import Migration & Strangler Fig Facade Eradication

## Executive Summary & Architectural Rationale

The Tripartite Pipeline Isolation refactoring successfully decomposed the monolithic `v2_core.py` (1,920L), `execution.py` (1,511L), and `worker.py` (2,037L) into bounded single-responsibility modules under `backend_v2/models/domain/`, `backend_v2/models/dtos/`, `backend_v2/services/execution/`, and `backend_v2/workers/`.
To prevent system-wide import breakages during decomposition, temporary Strangler Fig Facades with PEP 484 explicit re-exports were deployed in `backend_v2/models/v2_core.py`, `backend_v2/services/execution/__init__.py`, and `backend_v2/worker.py`.

Now that the Tripartite architecture is 100% hardened, tested (130/130 passing), and audited, this plan executes the final phase of the Strangler Fig Lifecycle mandated by `@[ki_god_code_prevention.md#L81-L89]` (`remedial_strangler_fig_proxy`):
1. **Migrate all callers** of `backend_v2.models.v2_core` (80 production files + 170 test files = 250 files total) to their authoritative canonical domain paths (`models/domain/*`, `models/dtos/*`, `models/core_base.py`, `models/enums.py`).
2. **Relocate model forward-reference rebuilds** (`model_rebuild`) directly into their respective canonical model files.
3. **Eradicate naked dict `WorkflowSchemaResponse = dict[str, Any]`** in favor of strict `WorkflowSchemaResponseDTO`.
4. **Permanently delete** `backend_v2/models/v2_core.py` and its temporary proxy test `test_v2_core_proxy.py`.
5. **Clean up `backend_v2/services/execution/__init__.py`**: Eradicate external borrowed re-exports (specifically and exhaustively: `BlueprintTransformer`, `DocumentExtractionService`, `ExportService`, `FlatFileService`, `OutputProfile`, `PdfReportService`, `SduiMapperService`, `TokenData`, `Workflow`, `asyncio`, `get_storage_driver`, `recalculate`), retaining strictly the `ExecutionService` unified facade and execution lifecycle subservices. Simultaneously decouple internal subservices (`ingress_service.py`, `resumption_service.py`, `override_service.py`, `legacy_render_service.py`, `lifecycle_service.py`, `context_service.py`) from borrowed symbols and update mock patch paths in `test_execution.py`.
6. **Clean up `backend_v2/worker.py`**: Eradicate legacy worker coroutine re-exports (specifically and exhaustively: `VarianceExplanationResult`, `execute_workflow_job`, `generate_pdf_job`, `generate_pdf_task`, `generate_profile_synthesis_and_pdf_task`, `generate_report_artifact_job`, `render_profile_job`), leaving `worker.py` strictly as the Arq daemon runtime entrypoint (`WorkerSettings`, `startup`, `shutdown`, `health_check`).
7. **Enforce AST Guardrail (QGR017)**: Lock in `scripts/_ast_guardrails.py` to structurally prevent any future imports from `v2_core`.
8. **Knowledge Item Synchronization**: Update `ki_god_code_prevention.md`, `ki_tripartite_pipeline_architecture.md`, and `ki_zero_permissive_typing.md` to reflect complete eradication of `v2_core.py` and adoption of canonical imports.
9. **As-Built Architecture & Directory Reference Sync**: Execute `/tier7-describe-architecture` for relevant documents in `docs/architecture/` (`00_README_META_ARCHITECTURE.md`, `01_system_context_and_invariants.md`, `03_cognitive_orchestration_engine.md`, `04_server_driven_ui_and_presentation.md`) and update `.agents/rules/04_directory_reference.md`.

---

## User Review Required

> [!IMPORTANT]
> - `backend_v2/models/v2_core.py` will be permanently deleted (`git rm`).
> - All imports across 80 production backend files and 170 test files (250 files total) will be updated to point to canonical paths.
> - `scripts/migrate_v2_core_imports.py` will be created as a verified deterministic AST codemod tool to execute the bulk import transformations safely across both module and function scopes without lossy manual text edits.
> - Knowledge Items, Architecture Pillars (`docs/architecture/`), and `.agents/rules/04_directory_reference.md` will be synchronized with physical codebase state.
> - Zero changes are made to runtime business logic, database seeds, or Flutter frontend contracts.
> - Per user instruction, no section of this plan is shortened and no part of the software implementation is deferred.

---

## Scope & Target Boundaries

### TARGET Files
- `[NEW] @[backend_v2/models/dtos/workflow_schema.py]` — Pure Pydantic V2 `WorkflowSchemaResponseDTO` eradicating naked dict `WorkflowSchemaResponse = dict[str, Any]`.
- `[NEW] @[scripts/migrate_v2_core_imports.py]` — Deterministic AST codemod tool to migrate imports across all module and function scopes.
- `[DELETE] @[backend_v2/models/v2_core.py#L1-L395]` — Hollow Shell proxy to be permanently eradicated.
- `[DELETE] @[backend_v2/tests/unit/test_v2_core_proxy.py#L1-L32]` — Temporary proxy test to be removed.
- `[MODIFY] @[backend_v2/models/domain/synthesis.py#L14-L17]`, `@[backend_v2/models/domain/synthesis.py#L170-L238]` — Mount `RenderedSynthesisCache.model_rebuild()` in home module.
- `[MODIFY] @[backend_v2/models/dtos/report_data.py#L11-L13]`, `@[backend_v2/models/dtos/report_data.py#L88-L105]` — Mount `ReportDataDTO.model_rebuild()` in home module.
- `[CONTEXT] @[backend_v2/models/dtos/matrix_scorecard.py#L19-L21]` — Preserve mandatory TYPE_CHECKING import (`AnySduiBlock`) required by `inner_sdui_blocks` (L297) under MyPy strict.
- `[MODIFY] @[backend_v2/models/domain/matrix.py#L13-L15]`, `@[backend_v2/models/domain/matrix.py#L260-L296]` — Mount `TDAAssertion.model_rebuild()` with `CausalEdge` in home module.
- `[MODIFY] @[backend_v2/models/domain/execution.py#L14-L17]`, `@[backend_v2/models/domain/execution.py#L23]`, `@[backend_v2/models/domain/execution.py#L63-L105]` — Purge dead TYPE_CHECKING imports (`RenderedSynthesisCache`, `TraceEvent`, `ErrorTraceEvent`, `TombstoneEvent`), purge dead circular import `ScorecardAtomDTO` at L23 (preserving L22 `DataDictionaryField` and `MCPAuditTrace` used in `FrozenContext`), and mount `ExecutionCreate.model_rebuild()` in home module.
- `[MODIFY] @[backend_v2/models/view/sdui.py#L713-L734]` — Mount SDUI block `model_rebuild()` calls and `MatrixScorecardRowDTO.model_rebuild()` after `AnySduiBlock` definition.
- `[MODIFY] @[backend_v2/tests/unit/models/view/test_sdui.py#L6-L8]` — Remove obsolete side-effect import of `v2_core`.
- `[MODIFY] @[backend_v2/services/execution/__init__.py#L1-L73]` — Purge non-execution re-exports (specifically and exhaustively: `BlueprintTransformer`, `DocumentExtractionService`, `ExportService`, `FlatFileService`, `OutputProfile`, `PdfReportService`, `SduiMapperService`, `TokenData`, `Workflow`, `asyncio`, `get_storage_driver`, `recalculate`).
- `[MODIFY] @[backend_v2/services/execution/ingress_service.py#L10]`, `@[backend_v2/services/execution/ingress_service.py#L33]`, `@[backend_v2/services/execution/ingress_service.py#L182-L203]` — Decouple borrowed `execution.Workflow` at L187 and L202; return `WorkflowSchemaResponseDTO`.
- `[MODIFY] @[backend_v2/services/execution/resumption_service.py#L9]`, `@[backend_v2/services/execution/resumption_service.py#L74]` — Decouple borrowed `execution.Workflow` at L74.
- `[MODIFY] @[backend_v2/services/execution/override_service.py#L11]`, `@[backend_v2/services/execution/override_service.py#L82]`, `@[backend_v2/services/execution/override_service.py#L88]`, `@[backend_v2/services/execution/override_service.py#L200]` — Decouple borrowed `execution.Workflow`, `get_storage_driver`, and `recalculate`.
- `[MODIFY] @[backend_v2/services/execution/legacy_render_service.py#L12]`, `@[backend_v2/services/execution/legacy_render_service.py#L59]`, `@[backend_v2/services/execution/legacy_render_service.py#L78]`, `@[backend_v2/services/execution/legacy_render_service.py#L144]`, `@[backend_v2/services/execution/legacy_render_service.py#L221-L227]`, `@[backend_v2/services/execution/legacy_render_service.py#L269]`, `@[backend_v2/services/execution/legacy_render_service.py#L287]` — Decouple borrowed `execution.*` symbols.
- `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L129]`, `@[backend_v2/services/execution/context_service.py#L48]` — Decouple `execution.get_storage_driver` in favor of canonical `backend_v2.services.storage`.
- `[MODIFY] @[backend_v2/tests/unit/services/test_execution.py#L502]`, `@[backend_v2/tests/unit/services/test_execution.py#L573]`, `@[backend_v2/tests/unit/services/test_execution.py#L1580]`, `@[backend_v2/tests/unit/services/test_execution.py#L1640]`, `@[backend_v2/tests/unit/services/test_execution.py#L1709]`, `@[backend_v2/tests/unit/services/test_execution.py#L2104-L2345]` — Update mock patch paths targeting decoupled symbols.
- `[MODIFY] @[backend_v2/worker.py#L30-L53]` — Purge worker coroutine re-exports from `__all__` (specifically and exhaustively: `VarianceExplanationResult`, `execute_workflow_job`, `generate_pdf_job`, `generate_pdf_task`, `generate_profile_synthesis_and_pdf_task`, `generate_report_artifact_job`, `render_profile_job`), preserve pure Arq daemon runtime entrypoint (`WorkerSettings`, `startup`, `shutdown`, `health_check`).
- `[MODIFY] @[backend_v2/tests/unit/test_worker_proxy.py#L7-L28]` — Update expected symbols in proxy test to match pure Arq daemon entrypoint.
- `[MODIFY] @[backend_v2/api/routers/execution/workflows.py#L12-L39]` — Adopt `WorkflowSchemaResponseDTO` in place of naked dict.
- `[MODIFY] @[backend_v2/services/execution/facade.py#L136-L138]` — Return `WorkflowSchemaResponseDTO` from `get_workflow_ui_schema`.
- `[MODIFY] @[scripts/_ast_guardrails.py#L30-L65]`, `@[scripts/_ast_guardrails.py#L480-L520]` — Add AST guardrail QGR017 banning `backend_v2.models.v2_core` imports.
- `[MODIFY] Production Callers (80 files)` in `api/` (6), `core/` (1), `database/` (5), `hooks/` (8), `llm/` (6), `models/dtos/` (5), `seed/` (1), `services/` (29), `utils/` (1), `workers/` (5).
- `[MODIFY] Test Callers (170 files)` in `tests/unit/`, `tests/integration/` (including 5 worker test files importing coroutines from `backend_v2.workers.*`).
- `[MODIFY] @[.agents/rules/04_directory_reference.md]` — Eradicate `v2_core.py` references and update `worker.py` definition.
- `[MODIFY] @[docs/architecture/00_README_META_ARCHITECTURE.md]` — Synchronize as-built meta-architecture.
- `[MODIFY] @[docs/architecture/01_system_context_and_invariants.md]` — Synchronize system invariants and remove legacy facades.
- `[MODIFY] @[docs/architecture/03_cognitive_orchestration_engine.md]` — Synchronize orchestration models and execution facade.
- `[MODIFY] @[docs/architecture/04_server_driven_ui_and_presentation.md]` — Synchronize SDUI block rebuilds and ReportDataDTO.
- `[MODIFY] Knowledge Items` — `@[ki_god_code_prevention.md]`, `@[ki_tripartite_pipeline_architecture.md]`, `@[ki_zero_permissive_typing.md]`.

### CONTEXT Files (Read-Only)
- `@[backend_v2/models/core_base.py#L1-L80]`
- `@[backend_v2/models/domain/workflow.py#L1-L150]`
- `@[backend_v2/models/domain/step.py#L1-L120]`
- `@[backend_v2/models/domain/output_profile.py#L1-L120]`
- `@[backend_v2/models/domain/report_artifact.py#L1-L100]`
- `@[backend_v2/models/dtos/atom_result.py#L1-L100]`
- `@[backend_v2/models/enums.py#L1-L150]`
- `@[scripts/backend_audit_loop.py#L1-L120]`

---

## Technical Debt & Anti-Pattern Sweep (Pre-Implementation Cleanups)

The target files and their immediate 1-hop dependencies were thoroughly inspected for the standard technical debt items:
1. **Naked Dict Anti-Pattern (`WorkflowSchemaResponse`)**: `backend_v2/models/v2_core.py#L353` declares `WorkflowSchemaResponse = dict[str, Any]`, imported by `backend_v2/api/routers/execution/workflows.py#L12-L39` and returned by `ingress_service.py#L182-L189` and `facade.py#L136-L138`. This violates `no_naked_dicts_in_state` and `data_leak_prevention_firewall`. **Cleanup**: Create `WorkflowSchemaResponseDTO(BaseModel)` with `model_config = ConfigDict(strict=True, extra="forbid")` and `expected_inputs: list[ExpectedInput]`.
2. **Monolithic Module-Level Rebuild Coupling**: `v2_core.py#L356-L393` hosts `model_rebuild()` calls for `RenderedSynthesisCache`, `ReportDataDTO`, `MatrixScorecardRowDTO`, `ExecutionCreate`, `TDAAssertion`, and SDUI blocks, creating an artificial runtime dependency on `v2_core`. **Cleanup**: Relocate rebuilds directly into home modules (`synthesis.py#L170-L238`, `report_data.py#L88-L105`, `matrix.py#L260-L296`, `execution.py#L63-L105`), and place the SDUI block and scorecard rebuilds at the end of `sdui.py#L713-L734` after `AnySduiBlock` definition.
3. **Leaked External Service Re-exports in Execution Subpackage & Callers**: `backend_v2/services/execution/__init__.py#L1-L73` re-exports external services (specifically and exhaustively: `BlueprintTransformer`, `DocumentExtractionService`, `ExportService`, `FlatFileService`, `OutputProfile`, `PdfReportService`, `SduiMapperService`, `TokenData`, `Workflow`, `asyncio`, `get_storage_driver`, `recalculate`). Inspection revealed internal subservices borrowed these re-exports:
   - `ingress_service.py#L187, #L202`: `execution.Workflow.model_validate()` borrows `Workflow` (canonical is `backend_v2.models.domain.workflow.Workflow`).
   - `resumption_service.py#L74`: `execution.Workflow.model_validate()` borrows `Workflow`.
   - `override_service.py#L82, #L88, #L200`: borrows `Workflow`, `get_storage_driver`, and `recalculate`.
   - `legacy_render_service.py#L59, #L78, #L144, #L221, #L227, #L269, #L287`: borrows `get_storage_driver`, `BlueprintTransformer`, `SduiMapperService`, `FlatFileService`, `Workflow`, and `PdfReportService`.
   - `lifecycle_service.py#L129` and `context_service.py#L48`: borrow `get_storage_driver`.
   - `test_execution.py#L502, #L573, #L1580, #L1640, #L1709, #L2104-L2345`: patches `backend_v2.services.execution.get_storage_driver`, `BlueprintTransformer`, and `PdfReportService.generate_execution_pdf`.
   **Cleanup**: Purge all borrowed re-exports from `backend_v2/services/execution/__init__.py`, update all 6 subservices to import canonical symbols directly, decouple `import backend_v2.services.execution as execution`, and synchronously update `test_execution.py` mock patch paths.
4. **Duplicated Worker Coroutine Re-exports in Arq Entrypoint**: `backend_v2/worker.py#L30-L53` re-exports worker coroutines (specifically and exhaustively: `VarianceExplanationResult`, `execute_workflow_job`, `generate_pdf_job`, `generate_pdf_task`, `generate_profile_synthesis_and_pdf_task`, `generate_report_artifact_job`, `render_profile_job`) in `__all__`, which duplicates `backend_v2.workers.*`. Five test files (`test_worker_synthesis_accumulation.py`, `test_worker_synthesis.py`, `test_worker_dlq_fallback.py`, `test_worker_models_used.py`, `test_worker.py`) import from `worker.py`. **Cleanup**: Purge coroutine re-exports from `__all__`, redirect test callers to `backend_v2.workers.*`, and retain `worker.py` strictly as the Arq daemon runtime entrypoint (`WorkerSettings`, `startup`, `shutdown`, `health_check`).
5. **Obsolete Side-Effect Import in SDUI Test**: `backend_v2/tests/unit/models/view/test_sdui.py#L6-L8` contains `import backend_v2.models.v2_core  # noqa: F401` solely to trigger model rebuilds. **Cleanup**: Remove line 7 once SDUI rebuilds are co-located in `sdui.py`.
6. **Dead TYPE_CHECKING Imports in Execution Domain Model**: `backend_v2/models/domain/execution.py#L14-L17` imports `RenderedSynthesisCache`, `TraceEvent`, `ErrorTraceEvent`, and `TombstoneEvent` under `if TYPE_CHECKING:`, but none of these types are referenced in the module. **Cleanup**: Purge unused TYPE_CHECKING imports.
7. **Dead Imports in Execution Domain Model Inducing Circular Imports**: `backend_v2/models/domain/execution.py#L23` imports `ScorecardAtomDTO` from `matrix_scorecard.py`, which is completely unused in `execution.py`. Line 22 imports `DataDictionaryField` and `MCPAuditTrace`, which are actively used in `FrozenContext` (L55, L58) and must be preserved. When `matrix_scorecard.py` is initialized, it imports `system_config.py`, triggering `domain/__init__.py`, which imports `execution.py`, which attempts to import `ScorecardAtomDTO` from the still-initializing `matrix_scorecard.py`, crashing with `ImportError: cannot import name 'ScorecardAtomDTO' from partially initialized module 'backend_v2.models.dtos.matrix_scorecard'`. **Cleanup**: Purge line 23 (`from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO`) from `execution.py` completely while preserving line 22, breaking the circular dependency at module root without breaking `FrozenContext`.
8. **Preservation of Mandatory TYPE_CHECKING Import in Matrix Scorecard DTO (False-Positive Trap Avoidance)**: Initial inspection suggested `backend_v2/models/dtos/matrix_scorecard.py#L19-L21` was an unused `TYPE_CHECKING` import. However, rigorous AST analysis revealed that `inner_sdui_blocks: Annotated[list[AnySduiBlock], Field(...)]` on line 297 depends directly on `AnySduiBlock`. Purging lines 19-21 causes MyPy strict mode to crash with `[name-defined]`. **Preservation Invariant**: Retain lines 19-21 under `if TYPE_CHECKING:` to guarantee zero runtime circularity while preserving 100% static typing integrity.
9. **Obsolete Proxy Test Fixture**: `test_v2_core_proxy.py#L1-L32` asserts that `v2_core.__all__` contains >40 symbols. Once `v2_core.py` is eradicated, this test becomes an obsolete ghost test. **Cleanup**: Permanently delete `test_v2_core_proxy.py`.
10. **Stale Directory References**: `.agents/rules/04_directory_reference.md` still lists `v2_core.py` in `models/` and documents `worker.py` as a re-export facade. **Cleanup**: Update directory reference to reflect canonical structure and pure entrypoint.
11. **Function-Level Import Traversal in Codemod**: Test files (specifically: `test_v2_core_models.py#L137`, `test_executions.py#L77`, `test_document_extraction.py#L153`) contain inline `from backend_v2.models.v2_core import ...` inside test functions. **Cleanup**: Ensure `scripts/migrate_v2_core_imports.py` traverses all scopes (`ast.walk`) to rewrite function-level imports as well as top-level imports.

---

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`backend_v2/models/v2_core.py` & Caller Base (250 files)** | Banned: Leaving `v2_core.py` alive as a permanent "Hollow Shell" facade; banned manual regex text replacements that leave unformatted or dangling imports; banned top-level-only AST parsers that miss function-level test imports. | Canonical SSOT domain imports (`models/domain/*`, `models/dtos/*`, `models/core_base.py`, `models/enums.py`). Full deletion of `v2_core.py`. | Pruned: No runtime import hooks (`sys.meta_path`) or intermediate migration bridge packages. Complete physical removal. Migration tool deleted after audit. | `uv run python scripts/_ast_guardrails.py` (QGR017); `python -c "import backend_v2.models.v2_core"` raises `ModuleNotFoundError`. |
| **`workflows.py` & Ingress Service** | Banned: `WorkflowSchemaResponse = dict[str, Any]` naked dict in router and service return signatures; banned `execution.Workflow` borrowed re-export lookup. | Typed `WorkflowSchemaResponseDTO(BaseModel)` with `ConfigDict(strict=True, extra="forbid")` in `backend_v2/models/dtos/workflow_schema.py`. Direct import of canonical `Workflow`. | Pruned: No generic dictionary wrappers or untyped schema responses. Pure Pydantic V2 DTO. | Router `response_model=WorkflowSchemaResponseDTO` verified via `uv run python scripts/backend_audit_loop.py backend_v2/api --test`. |
| **Model Rebuilds (`sdui.py`, `report_data.py`, `matrix.py`, `synthesis.py`, `execution.py`)** | Banned: Relying on `v2_core.py` side-effects at startup to resolve forward references; banned eager circular imports between `matrix_scorecard.py` and `sdui.py`; banned dead cross-module imports in `execution.py#L23` (`ScorecardAtomDTO`); banned side-effect imports (`import v2_core # noqa: F401` in `test_sdui.py`). | Co-located Pydantic `model_rebuild()` calls at module level in home files. SDUI/Scorecard circularity resolved at bottom of `sdui.py` after `AnySduiBlock` definition. Clean dead import `ScorecardAtomDTO` in `execution.py#L23` while preserving L22. | Pruned: No external startup rebuild manager script. Direct module-load evaluation. | `uv run python -c "import backend_v2.models.view.sdui; import backend_v2.models.dtos.report_data; print('REBUILDS OK')"` verifies zero forward-ref crashes. |
| **`backend_v2/services/execution/__init__.py` & Subservices** | Banned: Re-exporting non-execution domain services (specifically and exhaustively: `BlueprintTransformer`, `DocumentExtractionService`, `ExportService`, `FlatFileService`, `OutputProfile`, `PdfReportService`, `SduiMapperService`, `TokenData`, `Workflow`, `asyncio`, `get_storage_driver`, `recalculate`) to serve as an ad-hoc dumping ground; banned internal subservices borrowing foreign exports from their own package root. | Pure execution package facade re-exporting strictly `ExecutionService`, `create_execution_record`, and the 6 lifecycle subservices. Direct canonical imports in subservices. | Pruned: 12 borrowed service, model, and utility re-exports removed from `__all__` and module imports. | `uv run pytest backend_v2/tests/unit/services/test_execution_proxy.py` passes with strictly execution symbols; `test_execution.py` passes with canonical patch paths. |
| **`backend_v2/worker.py`** | Banned: Re-exporting worker job coroutines (specifically and exhaustively: `VarianceExplanationResult`, `execute_workflow_job`, `generate_pdf_job`, `generate_pdf_task`, `generate_profile_synthesis_and_pdf_task`, `generate_report_artifact_job`, `render_profile_job`) in Arq configuration entrypoint. | Pure Arq daemon runtime configuration (`WorkerSettings`, `startup`, `shutdown`, `health_check`). Worker callers import directly from `backend_v2.workers.*`. | Pruned: Coroutines removed from `__all__`. Test files re-pointed directly to authoritative `backend_v2.workers.*`. | `uv run pytest backend_v2/tests/unit/test_worker_proxy.py` and `backend_v2/tests/unit/test_worker*.py` pass 100%. |
| **`scripts/_ast_guardrails.py` (QGR017)** | Banned: Unenforced architectural agreements that rely on developer memory or code review alone; banned soft WARNING severity on forbidden facade imports. | AST Guardrail QGR017: FATAL violation on any `ast.Import` or `ast.ImportFrom` targeting `backend_v2.models.v2_core`. | Pruned: Integrated directly into existing `QuorumGuardrailVisitor` without creating a separate linter CLI. | `uv run python scripts/_ast_guardrails.py` runs and verifies codebase is 100% clean of `v2_core` imports. |
| **Knowledge Items & As-Built Architecture Sync** | Banned: Leaving outdated references to `v2_core.py` or temporary facades in KIs, directory references, and architecture pillars. | Timeless as-built architectural synchronization describing purely current state without historical narratives or phase labels. | Pruned: No changelogs or phase history appended to architecture pillars. Pure present-tense operational description. | Physical code paths verified via `/tier7-describe-architecture` and cross-referenced with `04_directory_reference.md`. |

---

```xml
<execution_protocol level="0_create_plan">
  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS_AND_DTO_CREATION">
    <action>1. Create `backend_v2/models/dtos/workflow_schema.py` defining `WorkflowSchemaResponseDTO` with `expected_inputs: list[ExpectedInput]` to eradicate naked dict `WorkflowSchemaResponse = dict[str, Any]`.</action>
    <action>2. Update `backend_v2/services/execution/ingress_service.py#L182-L189` and `facade.py#L136-L138` to return `WorkflowSchemaResponseDTO`.</action>
    <action>3. Update `backend_v2/services/execution/ingress_service.py#L187` and `#L202` to use canonical `Workflow.model_validate(...)` directly instead of borrowed `execution.Workflow`, and remove `import backend_v2.services.execution as execution` at line 10.</action>
    <action>4. Update `backend_v2/api/routers/execution/workflows.py#L12-L39` to import and annotate `WorkflowSchemaResponseDTO` as `response_model`.</action>
    <action>5. Clean unused `TYPE_CHECKING` imports in `backend_v2/models/domain/execution.py#L14-L17` (`RenderedSynthesisCache`, `TraceEvent`, `ErrorTraceEvent`, `TombstoneEvent`).</action>
    <action>6. Clean dead import in `backend_v2/models/domain/execution.py#L23` (`ScorecardAtomDTO`) to break artificial circular import dependency with `matrix_scorecard.py` while preserving line 22 (`DataDictionaryField`, `MCPAuditTrace`) required by `FrozenContext`.</action>
    <action>7. Explicitly preserve mandatory `TYPE_CHECKING` import in `backend_v2/models/dtos/matrix_scorecard.py#L19-L21` (`from backend_v2.models.view.sdui import AnySduiBlock`) required by `inner_sdui_blocks` (L297) to ensure zero MyPy `[name-defined]` regressions.</action>
    <action>8. Remove obsolete side-effect import in `backend_v2/tests/unit/models/view/test_sdui.py#L6-L8` (`import backend_v2.models.v2_core  # noqa: F401`).</action>
    <action>9. Relocate forward-reference Pydantic model rebuilds directly into home modules:
      - In `backend_v2/models/domain/synthesis.py#L170-L238`: mount local rebuild for `RenderedSynthesisCache` with `DataStarvationEvent` (from `backend_v2.models.dtos.base`) and `AnySduiBlock` (from `backend_v2.models.view.sdui`).
      - In `backend_v2/models/dtos/report_data.py#L88-L105`: mount local rebuild for `ReportDataDTO` with `AnySduiBlock`.
      - In `backend_v2/models/domain/matrix.py#L260-L296`: mount local rebuild for `TDAAssertion` with `CausalEdge` (from `backend_v2.models.dtos.dag_models`).
      - In `backend_v2/models/domain/execution.py#L63-L105`: mount local rebuild for `ExecutionCreate`.
      - In `backend_v2/models/view/sdui.py#L713-L734`: mount rebuilds for `MatrixScorecardRowDTO`, `SduiRadarChartBlock`, `SduiScatterPlotBlock`, `SduiQuadrantMatrixBlock`, `SduiMatrixTableBlock`, `SduiMetrics1DBlock`, and `SduiGridBlock` immediately after `AnySduiBlock` definition.
    </action>
    <constraint invariant="fail_fast_hydration">All forward references must resolve deterministically at module load time without requiring v2_core to be imported.</constraint>
  </step>

  <step id="2" name="CANONICAL_SYMBOL_MAPPING_AND_MIGRATION_SCRIPT">
    <action>Create deterministic migration script `scripts/migrate_v2_core_imports.py` to map all 56 distinct imported symbols from `backend_v2.models.v2_core` directly to their canonical modules.</action>
    <action>The script AST visitor MUST recursively traverse all scopes (`ast.walk` or recursive `ast.NodeVisitor`) to catch both top-level imports and function-level / block-level imports inside test methods.</action>
    <action>Exhaustive mapping table:
      - `OPAQUE_STRIPE_ID_REGEX`, `I18nText`, `V2CoreBase` -> `backend_v2.models.core_base`
      - `EvaluatedMatrixContextDTO`, `EvidenceRejectionRequest`, `ExecutionCreate`, `ExecutionRecord`, `ExecutionStep`, `ExecutionStepState`, `ExecutionSummarySnapshot`, `FrozenContext`, `JobAcceptedDTO` -> `backend_v2.models.domain.execution`
      - `WorkflowInputs`, `WorkflowInputsIngress` -> `backend_v2.models.domain.inputs`
      - `AcceptanceCriterion`, `AntiPattern`, `ContrastivePairDTO`, `MatrixClaim`, `MatrixRow`, `MatrixScale`, `TDAAssertion`, `TheoryGrounding`, `_coerce_to_tuple` -> `backend_v2.models.domain.matrix`
      - `OutputProfile` -> `backend_v2.models.domain.output_profile`
      - `ReportArtifact` -> `backend_v2.models.domain.report_artifact`
      - `ALLOWED_INPUT_MODES`, `ExpectedInput`, `QuestionnaireItem`, `Role`, `Step`, `StepRule` -> `backend_v2.models.domain.step`
      - `BaseMatrixXAI`, `BaseTDAExtraction`, `DistilledEvaluation`, `MatrixSynthesisGroup`, `RenderedSynthesisCache`, `SynthesisMetadataDTO`, `SynthesisStepDataDTO` -> `backend_v2.models.domain.synthesis`
      - `AllowedMCPTool`, `ChatHistoryDTO`, `ChatMessageDTO`, `DataDictionaryField`, `MCPAuditTrace`, `ModelProfile`, `ProviderExtraParamsDTO`, `SystemConfigMCPGateways`, `SystemConfigModelRegistry` -> `backend_v2.models.domain.system_config`
      - `Workflow` -> `backend_v2.models.domain.workflow`
      - `AtomResultDTO`, `ErrorDetailsDTO`, `ExecutionMetricsDTO`, `ExtensionMetricsDTO`, `ExtractedValueDTO`, `HydratedAtomDTO` -> `backend_v2.models.dtos.atom_result`
      - `DataStarvationEvent` -> `backend_v2.models.dtos.base`
      - `HumanOverrideDTO`, `HumanOverrideRequest`, `MatrixScorecardRowDTO`, `ScorecardAtomDTO`, `TDADlq`, `TDAEvaluated`, `TDAPending`, `TDAStateUnion` -> `backend_v2.models.dtos.matrix_scorecard`
      - `LLMExtractedQuote` -> `backend_v2.models.dtos.quote_evidence`
      - `ReportDataDTO` -> `backend_v2.models.dtos.report_data`
      - `XaiHighlightItem` -> `backend_v2.models.dtos.synthesis`
      - `BlockDataType`, `CognitiveTier`, `ComponentType`, `DisplayScale`, `ExecutionStatus`, `Lax*`, `LLMProvider`, `PresetView`, `SourcesDisplayMode`, `StepType`, `TargetBlockType`, `TargetSpeaker`, `XaiExtensionType` -> `backend_v2.models.enums`
      - `ExecutionCoreFields`, `ExecutionMetadata` -> `backend_v2.models.execution_core`
      - `WorkflowSchemaResponseDTO` -> `backend_v2.models.dtos.workflow_schema`
    </action>
    <action>The script must run `ruff check --fix` and `ruff format` on each modified file to guarantee zero syntax or formatting defects.</action>
    <constraint invariant="zero_duct_tape">The script must parse multi-line and single-line imports using AST / LibCST and emit cleanly formatted, alphabetically sorted PEP 8 imports with zero duplicate lines.</constraint>
  </step>

  <step id="3" name="MIGRATE_PRODUCTION_CALLERS_BATCH_A">
    <action>Execute migration script on 80 production files in: `backend_v2/services/`, `backend_v2/api/`, `backend_v2/workers/`, `backend_v2/database/`, `backend_v2/hooks/`, `backend_v2/llm/`, `backend_v2/models/`, `backend_v2/utils/`, `backend_v2/core/`, `backend_v2/seed/`.</action>
    <action>Verify zero references to `backend_v2.models.v2_core` remain in production code via `grep_search`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services --test`.</action>
    <action>Atomic git commit: `refactor(models): migrate 80 production callers from v2_core to canonical domain modules`.</action>
    <constraint invariant="atomic_checkpoint_mandate">Verify all production files pass Ruff formatting and MyPy strict typecheck before proceeding to test migration.</constraint>
  </step>

  <step id="4" name="MIGRATE_TEST_CALLERS_BATCH_B">
    <action>Execute migration script on 170 test files in: `backend_v2/tests/unit/`, `backend_v2/tests/integration/`.</action>
    <action>Delete `backend_v2/tests/unit/test_v2_core_proxy.py` (obsolete proxy test).</action>
    <action>Update `test_v2_core_strictness.py` and `test_v2_core_models.py` imports to reference canonical domain modules directly.</action>
    <action>Verify zero references to `backend_v2.models.v2_core` remain in test code via `grep_search`.</action>
    <action>Run unit test suite: `uv run pytest backend_v2/tests/unit/`.</action>
    <action>Atomic git commit: `refactor(tests): migrate 170 test callers from v2_core to canonical domain modules`.</action>
  </step>

  <step id="5" name="PERMANENTLY_PURGE_V2_CORE">
    <action>Physically delete `backend_v2/models/v2_core.py` using `git rm backend_v2/models/v2_core.py`.</action>
    <action>Run `grep_search` across entire workspace to mathematically verify 0 remaining references to `v2_core`.</action>
    <action>Atomic git commit: `refactor(models): eradicate v2_core.py strangler fig facade`.</action>
    <constraint invariant="remedial_strangler_fig_proxy">Once all downstream consumers are migrated, the temporary Hollow Shell proxy MUST be completely deleted.</constraint>
  </step>

  <step id="6" name="STREAMLINE_EXECUTION_INIT_FACADE">
    <action>Clean `backend_v2/services/execution/__init__.py`:
      - Remove borrowed re-exports (specifically and exhaustively: `BlueprintTransformer`, `DocumentExtractionService`, `ExportService`, `FlatFileService`, `OutputProfile`, `PdfReportService`, `SduiMapperService`, `TokenData`, `Workflow`, `asyncio`, `get_storage_driver`, `recalculate`).
      - Preserve strictly: `ExecutionService`, `create_execution_record`, `ExecutionLifecycleService`, `ExecutionIngressService`, `ExecutionResumptionService`, `ExecutionOverrideService`, `ExecutionStreamService`, `ExecutionContextService`, `ExecutionRecord`, `ExecutionStep`, `FrozenContext`, `ExecutionCreate`.
      - Update `__all__` list accordingly.
    </action>
    <action>Decouple execution subservices from borrowed re-exports:
      - In `backend_v2/services/execution/resumption_service.py#L9, #L74`: import canonical `Workflow` from `backend_v2.models.domain.workflow`; remove `import backend_v2.services.execution as execution`.
      - In `backend_v2/services/execution/override_service.py#L11, #L82, #L88, #L200`: import `Workflow` from `backend_v2.models.domain.workflow`, `get_storage_driver` from `backend_v2.services.storage`, and `recalculate` from `backend_v2.hooks.scoring`; remove `import backend_v2.services.execution as execution`.
      - In `backend_v2/services/execution/legacy_render_service.py#L12, #L59, #L78, #L144, #L221, #L227, #L269, #L287`: import canonical `get_storage_driver` from `backend_v2.services.storage`, `BlueprintTransformer` from `backend_v2.services.blueprint`, `SduiMapperService` from `backend_v2.services.sdui_mapper_service`, `FlatFileService` from `backend_v2.services.flattener`, `Workflow` from `backend_v2.models.domain.workflow`, and `PdfReportService` from `backend_v2.services.pdf_generator`; remove `import backend_v2.services.execution as execution`.
      - In `backend_v2/services/execution/lifecycle_service.py#L129` and `context_service.py#L48`: import canonical `get_storage_driver` from `backend_v2.services.storage`.
      - In `backend_v2/tests/unit/services/test_execution.py#L502, #L573, #L1580, #L1640, #L1709, #L2104-L2345`: update mock patch targets from `backend_v2.services.execution.*` to canonical modules (`backend_v2.services.storage.get_storage_driver`, `backend_v2.services.blueprint.BlueprintTransformer`, `backend_v2.services.pdf_generator.PdfReportService.generate_execution_pdf`).
    </action>
    <action>Run tests: `uv run pytest backend_v2/tests/unit/services/test_execution_proxy.py` and `uv run pytest backend_v2/tests/unit/services/test_execution.py`.</action>
    <action>Atomic git commit: `refactor(execution): streamline execution package exports and purge external service bridges`.</action>
  </step>

  <step id="7" name="STREAMLINE_WORKER_ENTRYPOINT_FACADE">
    <action>Clean `backend_v2/worker.py`:
      - Remove redundant re-exports of worker coroutines from `__all__` (specifically and exhaustively: `VarianceExplanationResult`, `execute_workflow_job`, `generate_pdf_job`, `generate_pdf_task`, `generate_profile_synthesis_and_pdf_task`, `generate_report_artifact_job`, `render_profile_job`).
      - Update 5 test files (`test_worker_synthesis_accumulation.py`, `test_worker_synthesis.py`, `test_worker_dlq_fallback.py`, `test_worker_models_used.py`, `test_worker.py`) to import coroutines directly from `backend_v2.workers.*`.
      - Preserve `WorkerSettings`, `startup`, `shutdown`, `health_check` as the pure Arq daemon runtime entrypoint.
      - Update `test_worker_proxy.py` to assert Arq daemon settings without expecting coroutine re-exports in `__all__`.
    </action>
    <action>Run test: `uv run pytest backend_v2/tests/unit/test_worker*.py`.</action>
    <action>Atomic git commit: `refactor(worker): streamline worker entrypoint and direct callers to backend_v2.workers`.</action>
  </step>

  <step id="8" name="AST_GUARDRAIL_LOCKDOWN_AND_AUDIT">
    <action>Add AST Guardrail QGR017 in `scripts/_ast_guardrails.py`:
      - Add `visit_Import` and `visit_ImportFrom` methods to `QuorumGuardrailVisitor`.
      - Rule: Flag any import where `module == "backend_v2.models.v2_core"` or alias ends with `"v2_core"` with a fatal `ASTGuardrailError` (Rule code: `QGR017`, Severity: `FATAL`).
    </action>
    <action>Run AST guardrail suite: `uv run python scripts/_ast_guardrails.py`.</action>
    <action>Run global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Run SDUI semantic parity test: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <action>Delete temporary migration script: `git rm scripts/migrate_v2_core_imports.py`.</action>
    <action>Atomic git commit: `chore(guardrails): add QGR017 AST guardrail banning v2_core imports and complete audit`.</action>
    <constraint invariant="ast_guardrail_mandate">Structural testing of new architectural constraints must prevent regression permanently.</constraint>
  </step>

  <step id="9" name="KNOWLEDGE_BASE_AND_KI_SYNCHRONIZATION">
    <action>Update Knowledge Items to reflect canonical module SSOT and complete eradication of `v2_core.py`:
      - Update `ki_god_code_prevention.md`: Document completion of Step 4 of the Strangler Fig Lifecycle: eradication of the `v2_core.py` Hollow Shell proxy, pruning of execution/worker borrowed re-exports, and enforcement of AST guardrail QGR017.
      - Update `ki_tripartite_pipeline_architecture.md`: Document canonical domain import paths and complete decoupling from `v2_core.py`.
      - Update `ki_zero_permissive_typing.md`: Document `WorkflowSchemaResponseDTO` eradicating `WorkflowSchemaResponse = dict[str, Any]` naked dict in `/workflows/{workflow_id}/ui_schema`.
    </action>
    <action>Verify all KI artifact references are synchronized.</action>
    <action>Atomic git commit: `docs(knowledge): update KIs for v2_core eradication and canonical domain imports`.</action>
  </step>

  <step id="10" name="AS_BUILT_ARCHITECTURE_AND_DIRECTORY_REFERENCE_SYNC">
    <action>Execute `/tier7-describe-architecture` synchronization on architectural pillars in `docs/architecture/`:
      - Update `docs/architecture/00_README_META_ARCHITECTURE.md`: Reflect fully decomposed domain module structure and pure Arq worker entrypoint.
      - Update `docs/architecture/01_system_context_and_invariants.md`: Document invariant QGR017 banning legacy facade imports and confirming canonical SSOT import rule.
      - Update `docs/architecture/03_cognitive_orchestration_engine.md`: Synchronize execution subpackage boundaries and worker entrypoint architecture.
      - Update `docs/architecture/04_server_driven_ui_and_presentation.md`: Synchronize SDUI model rebuilds co-located in `sdui.py` and ReportDataDTO.
    </action>
    <action>Update `.agents/rules/04_directory_reference.md`:
      - Remove `v2_core.py` from `backend_v2/models/` schema list.
      - Update `backend_v2/worker.py` definition from "Strangler Fig re-export facade" to "Arq 2026 worker daemon runtime entrypoint (`WorkerSettings`, `startup`, `shutdown`)".
      - Update rule `strict_model_location` to ban re-creating monolithic `v2_core.py`.
    </action>
    <action>Atomic git commit: `docs(architecture): synchronize architecture pillars and directory reference rules`.</action>
    <constraint invariant="timeless_as_built_mandate">All updates to docs/architecture/ must be strictly timeless, present-tense, code-derived, and free of historical changelogs or phase labels.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan & Red-Team Attack Falsification

### Red-Team Attack Points (Falsification Analysis)
1. **Failure Point 1: Circular Import Deadlock during Module Initialization**:
   - *Attack*: If `backend_v2/models/dtos/matrix_scorecard.py` is imported first, its import of `MCPAuditTrace` from `backend_v2.models.domain.system_config` triggers `domain/__init__.py`, which imports `execution.py`. If `execution.py` still contains dead imports (`from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO`), Python encounters a circular import deadlock because `matrix_scorecard.py` is partially initialized.
   - *Falsification / Proof*: Running `uv run python -c "from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO"` fails with `ImportError: cannot import name 'ScorecardAtomDTO' from partially initialized module 'backend_v2.models.dtos.matrix_scorecard'`.
   - *Mitigation*: Pre-implementation step 1 purges the dead circular import `ScorecardAtomDTO` from `execution.py#L23` (while preserving L22 `DataDictionaryField` and `MCPAuditTrace` required by `FrozenContext`) and preserves `AnySduiBlock` under `if TYPE_CHECKING:` in `matrix_scorecard.py#L19-L21` (required by MyPy strict on L297). Furthermore, co-locate the `MatrixScorecardRowDTO.model_rebuild()` call inside `sdui.py#L713-L734` at the bottom of the file (after `AnySduiBlock` definition), passing both `AnySduiBlock` and `MCPAuditTrace` into `_types_namespace`. This completely decouples `matrix_scorecard.py` from importing `sdui.py` at runtime while resolving all types natively.
2. **Failure Point 2: Function-Level and Inline Test Imports Missed by Codemod**:
   - *Attack*: In test files (specifically: `test_v2_core_models.py#L137`, `test_executions.py#L77`, `test_document_extraction.py#L153`), `from backend_v2.models.v2_core import ...` occurs inside test functions. If the codemod script only inspects top-level module AST statements (`ast.Module.body`), function-level imports are missed, causing subsequent `ModuleNotFoundError` once `v2_core.py` is eradicated.
   - *Falsification / Proof*: Running `uv run pytest backend_v2/tests/unit/test_executions.py` fails with `ModuleNotFoundError: No module named 'backend_v2.models.v2_core'` inside test functions.
   - *Mitigation*: The codemod script uses recursive AST traversal (`ast.walk` or recursive `ast.NodeVisitor`) to locate all `ast.ImportFrom` nodes regardless of nesting depth, rewriting them in-place and invoking `ruff check --fix` and `ruff format` on each modified file.
3. **Failure Point 3: Codemod Mangling Comments, Decorators, or Multi-Line Formats**:
   - *Attack*: Naive regex string replacement on 250 files risks corrupting inline `# noqa` comments, multi-line parentheses, or trailing commas, causing syntax errors.
   - *Falsification / Proof*: AST parsing of unformatted modified files fails with `SyntaxError` or `IndentationError`.
   - *Mitigation*: The codemod script parses the AST to pinpoint exact start and end line ranges of `ImportFrom` nodes for `backend_v2.models.v2_core`, splits the imported symbols by their target canonical modules, synthesizes clean grouped imports, and automatically executes `ruff check --fix` and `ruff format` on each modified file.
4. **Failure Point 4: Breaking `/workflows/{workflow_id}/ui_schema` Endpoint**:
   - *Attack*: `backend_v2/api/routers/execution/workflows.py` imports `WorkflowSchemaResponse = dict[str, Any]` from `v2_core.py`. If `v2_core.py` is eradicated without a replacement DTO, the endpoint fails with `ImportError`.
   - *Falsification / Proof*: Running `uv run pytest backend_v2/tests/unit/test_api_clone_endpoints.py` or calling `/ui_schema` fails with 500 error.
   - *Mitigation*: Pre-implementation step 1 creates `WorkflowSchemaResponseDTO(BaseModel)` with `expected_inputs: list[ExpectedInput]` in `backend_v2/models/dtos/workflow_schema.py` and updates `ingress_service.py` and `workflows.py` before any caller migration begins.
5. **Failure Point 5: Execution Subservices and Mock Patches Broken by Purging Borrowed Re-exports in `execution/__init__.py`**:
   - *Attack*: If `BlueprintTransformer`, `get_storage_driver`, and `Workflow` are purged from `services/execution/__init__.py` without updating internal subservices and test patch targets, `override_service.py`, `legacy_render_service.py`, `resumption_service.py`, and `lifecycle_service.py` crash with `AttributeError: module 'backend_v2.services.execution' has no attribute 'get_storage_driver'/'Workflow'`, and 15 mock patches in `test_execution.py` fail.
   - *Falsification / Proof*: Running `uv run pytest backend_v2/tests/unit/services/test_execution.py` fails with `AttributeError` on `get_storage_driver`.
   - *Mitigation*: Step 6 explicitly updates all 6 subservices to import canonical symbols from `models.domain.workflow`, `services.storage`, `hooks.scoring`, `services.blueprint`, `services.sdui_mapper_service`, and `services.pdf_generator`, while simultaneously synchronizing patch paths in `test_execution.py`.
6. **Failure Point 6: False-Positive Dead Import Purge in Matrix Scorecard DTO**:
   - *Attack*: Purging `from backend_v2.models.view.sdui import AnySduiBlock` under `if TYPE_CHECKING:` in `backend_v2/models/dtos/matrix_scorecard.py#L19-L21` assuming it is unused.
   - *Falsification / Proof*: Running `mypy --strict backend_v2/models/dtos/matrix_scorecard.py` fails immediately with `error: Name "AnySduiBlock" is not defined  [name-defined]` on `inner_sdui_blocks` at line 297.
   - *Mitigation*: The `if TYPE_CHECKING:` block in `matrix_scorecard.py#L19-L21` is explicitly preserved. Runtime circularity is prevented because `AnySduiBlock` is only imported during static typechecking, while runtime hydration is resolved when `MatrixScorecardRowDTO.model_rebuild()` is called in `sdui.py#L734` where `AnySduiBlock` is natively in scope.

### Automated Tests
1. **Import Migration Validation**:
   - `uv run python -c "import backend_v2.models.domain.execution; import backend_v2.models.domain.workflow; import backend_v2.models.dtos.atom_result; print('ALL CANONICAL IMPORTS OK')"`
2. **Proxy Tests**:
   - `uv run pytest backend_v2/tests/unit/services/test_execution_proxy.py`
   - `uv run pytest backend_v2/tests/unit/test_worker_proxy.py`
3. **AST Guardrail QGR017**:
   - `uv run python scripts/_ast_guardrails.py`
4. **SDUI Semantic Parity**:
   - `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
5. **Global Quality Gates**:
   - `uv run python scripts/backend_audit_loop.py backend_v2 --test`
   - `uv run pytest backend_v2/tests/`

### Negative Scenarios & Fail-Fast Boundaries (ISTQB)
1. **Importing from deleted `v2_core` raises `ModuleNotFoundError`**:
   - `python -c "from backend_v2.models.v2_core import ExecutionRecord"` fails loudly with `ModuleNotFoundError: No module named 'backend_v2.models.v2_core'`.
2. **AST Guardrail catches resurrected import**:
   - Introducing `from backend_v2.models.v2_core import Step` triggers `ASTGuardrailError: [QGR017] Banned import from eradicated facade backend_v2.models.v2_core`.
3. **Forward-Reference Hydration Failure**:
   - Validating a `MatrixScorecardRowDTO` with nested `inner_sdui_blocks` containing `SduiRadarChartBlock` fails-fast with `ValidationError` if types are un-rebuilt or mismatched, proving mathematical validation integrity without silent dictionary fallback.
4. **Schema Violation on `/workflows/{workflow_id}/ui_schema`**:
   - Providing malformed `expected_inputs` payload (specifically: non-list structure or invalid schema item) triggers `ValidationError` and HTTP 422 Unprocessable Entity instead of permissive dictionary acceptance.
5. **Execution Subservice Borrowed Symbol Immunity**:
   - Attempting to access `execution.Workflow` or `execution.get_storage_driver` from `backend_v2.services.execution` raises `AttributeError`, proving that execution subservices no longer leak foreign domain capabilities.
