# Task Tracking: Modern Python Typing, 100% Protocol Reconstitution, Dict Eradication & Strict Boundary Lockdown

- [x] **Step 0: Strategic Alignment Check & Baseline Verification**
  - [x] Run AST guardrails baseline on `backend_v2/database/` (0 fatal errors)
  - [x] Run repository unit test baseline in `backend_v2/tests/unit/database/repositories/` (89/89 passed)

- [x] **Step 1: Implement Ingress & Update DTOs across All Domains with ISTQB Negative Tests**
  - [x] Add `WorkflowUpdateDTO` and `StepUpdateDTO` to `backend_v2/models/dtos/studio.py`
  - [x] Add `ExecutionCreateDTO` and `ExecutionUpdateDTO` to `backend_v2/models/dtos/trace.py`
  - [x] Update `TraceMatrixPayloadDTO` and `TraceScoringPayloadDTO` in `backend_v2/models/dtos/trace.py`
  - [x] Add `OrganizationUpdateDTO` and verify `UserUpdate` in `backend_v2/models/auth.py`
  - [x] Add `ConceptCreateDTO`, `ReferenceCreateDTO`, `ClaimCreateDTO` to `backend_v2/models/domain/knowledge.py`
  - [x] Add `SystemSettingsDTO`, `AnySystemConfig`, `SystemConfigUpdateDTO`, `SystemConfigCreateDTO`, `SystemConfigUpsertDTO` to `backend_v2/models/dtos/system.py`
  - [x] Add strict schema titles to `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `SystemConfigPerformativeLexicons` in `backend_v2/models/v2_core.py`
  - [x] Add `AuditLogCreateDTO`, `UsageAggregateUpdateDTO`, `UsageAggregateDTO`, `DetailedUsageDTO` to `backend_v2/models/domain/base.py`
  - [x] Add ISTQB negative test cases verifying `extra="forbid"` rejection and boundary constraints in `backend_v2/tests/unit/models/`
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test`

- [x] **Step 1b: Eradicate Naked Dicts in Domain Models, Synthesis Payloads & Strategy Inputs**
  - [x] Update `backend_v2/models/execution_core.py` (scalar dicts for `context_variables`, preserving `execution_trace`)
  - [x] Update `backend_v2/models/domain/synthesis.py` (scalar mappings in `SynthesisMetadataDTO`, `DistilledEvaluation.extensions`)
  - [x] Update Strategy Ingress inputs across `interaction.py`, `judge.py`, `logician.py`, `linguistics.py`, `xai.py`
  - [x] Update `backend_v2/models/domain/references.py`
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test`

- [x] **Step 2: Modernize Core Hook Registry (PEP 695 Generics & ISearchClient Typing)**
  - [x] Refactor `backend_v2/core/hook_registry.py` to `def register[F: HookFunction]`
  - [x] Reconstitute `ISearchClient.search()` return to `TavilySearchResultDTO`
  - [x] Modernize header docstrings in `hook_registry.py`
  - [x] Run `uv run pytest backend_v2/tests/unit/core/test_hook_registry.py -v`

- [x] **Step 3: Reconstitute All 15 Database Interfaces (100% Protocol Typing preserving ALL methods)**
  - [x] Add `from __future__ import annotations` and top-level model imports to `backend_v2/database/interfaces.py`
  - [x] Reconstitute all 15 protocol signatures with typed Pydantic models & DTOs
  - [x] Verify import graph and runtime stability with FastAPI
  - [x] Run `uv run mypy --strict backend_v2/database/interfaces.py`

- [x] **Step 4a: Modernize Core Execution & Workflow Repositories & Migrate 12+ Service Callers**
  - [x] Update `backend_v2/database/repositories/workflow.py`
  - [x] Update `backend_v2/database/repositories/execution.py`
  - [x] Migrate `update_execution` callers in `progress.py`, `execution.py`, `blueprint.py`, `dag_executor.py`, `llm.py`, `worker.py`
  - [x] Run backend audit loop on core repositories

- [x] **Step 4b: Modernize Component Repositories & Execution Service QGR012 Cleanup**
  - [x] Update `backend_v2/database/repositories/components/matrix.py`
  - [x] Update `agent.py`, `execution_persona.py`, `extraction_protocol.py`
  - [x] Update `backend_v2/database/repositories/component.py`
  - [x] Clean up downstream `backend_v2/services/execution.py`
  - [x] Run backend audit loop on component repositories

- [x] **Step 4c: Eradicate Service Layer Duck-Typing & isinstance(dict) Checks across Services**
  - [x] Refactor `backend_v2/services/blueprint.py` (eradicate 9 `isinstance(dict)`)
  - [x] Refactor `backend_v2/services/execution.py` (eradicate 6 `isinstance(dict)`)
  - [x] Refactor `backend_v2/services/matrix_domain_parser.py` (eradicate 3 `isinstance(dict)`)
  - [x] Refactor `backend_v2/services/document_extraction.py`
  - [x] Run backend audit loop on services

- [x] **Step 5: Modernize Identity, Knowledge, System, Audit & Authoring Repositories**
  - [x] Update `identity.py`, `knowledge.py`, `system.py`, `audit.py`
  - [x] Update `output_profile.py`, `task_blueprint.py`, `role.py`
  - [x] Update callers in `backend_v2/services/auth.py`
  - [x] Run backend audit loop on repositories

- [x] **Step 6: Delete dict_utils.py, Eliminate Suppressions & Service Duck-Typing**
  - [x] Create `backend_v2/services/orchestrator/state_reducer.py` with `merge_dynamic_inputs()` and tests
  - [x] Relocate `resolve_dot_notation()` to `backend_v2/utils/math_utils.py` and update `context_builder.py`
  - [x] Migrate `logic.py` and `base.py` to `merge_dynamic_inputs()`
  - [x] Delete `backend_v2/utils/dict_utils.py` and `test_dict_utils.py`
  - [x] Eradicate `# noqa: QGR001` in `backend_v2/main.py`
  - [x] Eradicate `# noqa: QGR003` in `llm_task_executor.py` and `typed_cache.py`
  - [x] Modernize `backend_v2/exceptions.py`
  - [x] Modernize `backend_v2/utils/finops_trace_analyzer.py`
  - [x] Modernize `backend_v2/utils/alias_engine.py`
  - [x] Run backend audit loop on utils

- [x] **Step 7: Build In-Memory Protocol Fakes Infrastructure for ALL 15 Protocols with Snapshot Isolation & Native Fault Injection**
  - [x] Create `backend_v2/tests/fakes/in_memory_repositories.py`
  - [x] Implement all 15 protocol fakes and composite facade
  - [x] Create `backend_v2/tests/unit/fakes/test_in_memory_repositories.py`
  - [x] Run pytest on in-memory repositories

- [x] **Step 8: Migrate Database Repository & Service Unit Tests with InMemory Fakes and Typed DTOs**
  - [x] Update repository unit tests
  - [x] Refactor service unit tests to replace `AsyncMock()` with `InMemoryRepositories`
  - [x] Migrate fault and resilience tests to `inject_fault` / `fault_context`
  - [x] Add `HookRegistrationScanResultDTO` helper
  - [x] Add ISTQB negative test partitions
  - [x] Run full test suite on database and service tests

- [x] **Step 9: AST Guardrails Strict 4-Driver Lockdown & Rule Expansion (QGR013-QGR015)**
  - [x] Purge 7 non-driver files from `BOUNDARY_EXEMPTION_FILES` in `scripts/_ast_guardrails.py`
  - [x] Implement `QGR013` (TypeVar), `QGR014` (AsyncMock repo ban, FATAL), `QGR015` (TypeGuard ban)
  - [x] Update `test_ast_guardrails.py` fixtures and add unit tests
  - [x] Run `uv run python scripts/_ast_guardrails.py backend_v2/`

- [x] **Step 9b: Implement Deterministic AST Multi-Layer Audit Script (audit_dict_eradication.py)**
  - [x] Create `scripts/audit_dict_eradication.py`
  - [x] Run `uv run python scripts/audit_dict_eradication.py` (verify 0 dict leaks)

- [x] **Step 10: Global Backend Quality Gate & Verification**
  - [x] Run `audit_dict_eradication.py`
  - [x] Run `backend_audit_loop.py backend_v2/ --test` (100% 2,726 tests passed, 93.54% coverage)
  - [x] Run `_ast_guardrails.py backend_v2/` (0 fatal errors)
