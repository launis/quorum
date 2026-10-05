<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
</required_context_rules>

# EPIC 157 System 2 Architectural Research & Audit Report

**Epic Target:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]  
**Auditor:** Principal Enterprise Architect & System Red Team  
**Date:** 2026-10-05  
**Audit Status:** APPROVED (System 2 Verified with Zero Invariant Violations)

---

## 1. Executive Summary & Root Cause Analysis

### 1.1 Executive Summary
EPIC 157 establishes the definitive architectural modernization required to achieve absolute zero permissive typing, eliminate primitive obsession, eradicate deceptive test persistence mocking, and enforce strict automated quality gates across Quorum's Python Backend and Flutter Client.

The physical scope comprises **394 unique files** across 13 cohesive execution phases, eradicating **3,847 individual violation sites** verified by exact AST and textual census commands:
- **127 Production Dict-Audit Violations** across 43 modules (98 naked dict annotations, 21 Primitive Obsession nested dicts, 5 duck-typing checks, 3 reflection calls; 86 remediated, 41 quarantined to physical boundary drivers).
- **861 Method Seeding Mocks (Census A)** across 49 test files relying on `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository`.
- **68 Repository Attribute Replacements (Census B)** across 12 test files (`<repo>.<attr> = AsyncMock(...)`).
- **7 Repository Object Patches (Census C)** across 3 test files (`patch.object` / `monkeypatch.setattr`).
- **11 Repository Fixture Functions** across 10 test files returning mocks.
- **821 Keyword-Injected Repository Mocks (Census D)** across 32 test files into `HookDependencies`, `HookContext`, and executor constructors.
- **50 String-Target Repository Patches (Census F)** across 6 worker test files.
- **25 Ad-Hoc Repository Classes (Census K)** across 7 test files returning loose dictionaries.
- **804 `cast(Any, ...)` Invocations (Census X)** across 13 files (792 laundering ad-hoc repository doubles).
- **76 `# noqa` Comment Tokens (Census N)** across 30 files (38 QGR suppressions, 38 Ruff suppressions).
- **409 `# type: ignore` Comment Tokens (Census T)** across 155 files.
- **390 Naked Dict Lines in Tests & Scripts (Census P)** across 89 files.
- **10 Production Mapping & Test-Named Dict Sites (Census M)** across 6 files.
- **193 Non-Codec Dart Maps (Census R)** across 48 client files.
- **11 Unconditional Skip/Xfail Markers (Census S)** across 7 test files (7 skip, 4 xfail).
- **25 Handwritten Dart Lint Suppressions (`// ignore:`)** across 23 client files.

### 1.2 Root Cause Analysis
Forensic investigation of the codebase established the following primary architectural root causes:
1. **The Mock-Emulation Fake Trajectory (`InMemoryBlueprintTransformerRepository`)**: Overriding `__getattribute__` and `__setattr__` dynamically synthesized non-existent methods returning `None` and accepted raw dictionary payloads into `.return_value`. This gave developers a path of least resistance to construct tests that bypassed repository contracts, masking real persistence failures and creating a "False Green" test suite.
2. **Divergent and Leaky Exemption Sets**: `BOUNDARY_EXEMPTION_FILES` (6 basenames in `_ast_guardrails.py`) and `LOCKED_PHYSICAL_DRIVERS` (8 basenames in `audit_dict_eradication.py`) operated on `Path.name`, accidentally exempting core domain files (specifically `backend_v2/models/dtos/telemetry.py` and `backend_v2/services/sdui/adapters/base_adapter.py`).
3. **AST Guardrail Blind Spots in `QGR014`**: The original AST guardrail `QGR014` scanned only `spec=I*Repository`, `@patch` on repositories, and `repo = AsyncMock()` direct variable assignments. It was blind to keyword argument injection (`exec_repo=MagicMock()`), attribute replacement (`repo.save = AsyncMock()`), string-target patches in worker files, and ad-hoc class definitions.
4. **Permissive Suppression Engine**: `scripts/_ast_guardrails.py` implemented `CommentSuppressor` parsing `# noqa: QGRxxx [REASON: ...]`, allowing inline suppressions to evade CI failure, while `pyproject.toml` disabled `warn_unused_ignores` for database modules.
5. **Heuristic File Classification**: `_is_test_file` used `"tests" in path_parts or name.startswith("test_")`, accidentally classifying the production file `backend_v2/core/test_settings.py` as a test and exempting it from production AST rules.
6. **One-Sided Permissive Client Typing**: Flutter client API clients and controllers maintained 193 `Map<String, dynamic>` signatures, bypassing Freezed model validation and creating runtime impedance with backend typed models.

---

## 2. Panel of Architects Evaluation

### 2.1 Global System Architect
- **Catastrophic System Bans Compliance**:
  - *Zero Backward Compatibility / Zero Legacy Fallbacks*: STRICTLY SATISFIED. All `.get(key, default)`, `or` fallback chains, and duck-typing cascades are eradicated. Unmapped fields Fail-Fast with typed `AppException`.
  - *Single Pipeline Invariant*: STRICTLY SATISFIED. Execution flows through exactly one deterministic pipeline. No bifurcated branches or legacy mode flags exist.
  - *Single Source of Truth (SSOT)*: STRICTLY SATISFIED. The divergent sets are unified into ONE path-based `frozenset[str]` of 15 POSIX paths named `BOUNDARY_EXEMPTION_FILES`.
  - *Ban on Naked Dictionaries in State*: STRICTLY SATISFIED. All domain state transit is converted to frozen Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`).
  - *Ban on Deceptive Persistence Mocking*: STRICTLY SATISFIED. Mocks are eradicated in favor of stateful in-memory fakes verifying real state roundtrips.

### 2.2 Backend & Data Architect
- **Data Model Sovereignty**:
  - Closed domain concepts are encapsulated into dedicated, immutable Pydantic V2 DTOs:
    * `[NEW]` `ValidatedSeedBufferDTO`
    * `[NEW]` `ProblemDetailDTO`
    * `[NEW]` `CachingPayloadResultDTO`
    * `[NEW]` `SystemConfigOptionDTO`
    * `[NEW]` `SystemValidationRulesDTO`
    * `[NEW]` `ValidationContextMetadataDTO`
    * `[NEW]` `EvaluatedMatrixRefDTO`
    * `[NEW]` `RawXAIExtensionDTO`
    * `[NEW]` `DomainExecutionContextDTO`
    * `[NEW]` `MatrixAggregationStateDTO`
    * `[NEW]` `LinguisticAnalysisDTO`
    * `[NEW]` `ResidualDebtCeilingsDTO`
  - Open external formats (JSON Schema, provider SDK bodies, OpenAPI documents, RFC 7807 extension members) are typed strictly as `dict[str, JsonValue]` using Pydantic's recursive JSON type.
  - Dynamic workflow inputs are typed strictly as `dict[str, IngressInputValue]` or `dict[str, DomainInputValue]` through origin tracing.
  - Two-Phase Seeder Pre-Flight Validation: `validate_all_seed_collections` in `backend_v2/seed/run_seed.py` validates 100% of seed collections in-memory before any database wipe or atomic ingress.

### 2.3 SDUI & Frontend Architect
- **Full-Duplex Parity & Dumb Painter Principles**:
  - Wire fields `mock_inputs` and `input_schema` are synchronized across backend DTOs and Flutter Dart models (`step_simulation.dart`, `prompt_block_simulation.dart`, `mcp_gateway.dart`).
  - 193 non-codec `Map<String, dynamic>` occurrences in `client_app_v2/lib/` are retyped to Freezed DTOs mirroring backend CLOSED models or `Map<String, Object?>` for OPEN-JSON fields.
  - Dart codec signatures (`fromJson`, `toJson`) required by `json_serializable` are retained as the explicit transport boundary.
  - Dart Guardrail Engine: Rule `DGR005` (banning non-codec `Map<String, dynamic>`) is introduced, and `DGR001`, `DGR004`, and `DGR005` are promoted to unconditional FATAL severity in `scripts/flutter_audit_loop.py`.
  - Cross-Platform SDUI Parity: Every modification to SDUI-related models mandates running `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.

### 2.4 AI & Orchestration Architect
- **Prompt & Orchestrator Invariance**:
  - Prompt blocks and Model Garden multiplexing (`LLMClient.from_strategy()`) remain 100% intact.
  - LLM Caching Service contract is formalized into `CachingPayloadResultDTO`, confining provider-native dictionary serialization strictly to physical adapter boundaries.
  - DAG Orchestrator Ecosystem Protection: Modifications touching `matrix_reducer.py`, `matrix_explanation_service.py`, `synthesis_engine.py`, `llm.py`, `source_document_packer.py`, and `context_builder.py` are gated by the explicit "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" gate.

---

## 3. Falsification & Red-Teaming Results (Anti-Happy-Path)

### 3.1 Failure Mode 1: Phase 1 Ingress Wire Breakage & Client Desynchronization (The False 422 Storm)
- **Failure Scenario**: Retyping `StudioMockInputsDTO.mock_inputs` from `dict[str, Any]` to `dict[str, IngressInputValue]` in Phase 1 before Phase 8/12 synchronizes Flutter's `step_simulation.dart` (`Map<String, dynamic>`). If a client or test fixture sends `null` or a nested map in `mock_inputs`, Pydantic V2 will immediately fail-fast with a 422 `ValidationError`.
- **Root Cause**: `IngressInputValue` is a discriminated union of scalar primitives (`str | int | float | bool`). It rejects nested maps or nulls.
- **Architectural Safeguard**: Section 2.5 establishes that scalar values serialize identically. In Phase 1, the test suite is audited to ensure all existing simulation fixtures supply valid `IngressInputValue` payloads, and 2 negative router tests asserting HTTP 422 for nested-map and null inputs are added to verify Fail-Fast enforcement.

### 3.2 Failure Mode 2: Premature QGR014 Landing & Test Cascade Failure (The Big Bang Mock Trap)
- **Failure Scenario**: If `QGR014` hardening (specifically detections (e) keyword injection, (f) string-target patch, and (g) ad-hoc classes) is promoted to FATAL severity before Phase 6 completes, it will instantly fail the entire CI/CD pipeline on the 821 census D mocks, 50 census F patches, and 25 census K ad-hoc classes across 40+ test files.
- **Root Cause**: AST guardrails run globally across the test suite during CI. Promoting a rule before all violations are migrated halts development.
- **Architectural Safeguard**: The Epic strictly sequences `QGR014` hardening to Phase 7. Phases 3 through 6 systematically migrate all occurrences in four discrete batches. Phase 7 verifies that census commands A, B, C, I, D, F, and K return 0 across the entire repository BEFORE landing `QGR014` at FATAL severity.

### 3.3 Failure Mode 3: `AppException.details` Blast Radius & Starlette Wire Shape Fracture
- **Failure Scenario**: Retyping `AppException.details` from `dict[str, Any] | None` to `dict[str, JsonValue] | None` triggers 32 mypy errors across 5 files. Furthermore, wrapping the exception in `ProblemDetailDTO` risks modifying the wire format expected by Flutter's `app_exception.dart` if `exclude_none=True` is omitted (dumping `instance: null`).
- **Root Cause**: Flutter client's RFC 7807 parser expects `instance` to be omitted when null, and Starlette's `JSONResponse` requires serializable dictionaries.
- **Architectural Safeguard**: Phase 2 explicitly defines `ProblemDetailDTO.model_dump(mode="json", exclude_none=True)` at the FastAPI boundary (`main.py`, `core/rate_limit.py`), preserving the exact wire contract while guaranteeing internal type safety.

### 3.4 Zero Behavioral Change Verification Gate
- **Refactoring vs Feature Classification**: EPIC 157 is strictly a **Refactoring & Hardening Epic**.
- **Invariance Verification**: The Epic introduces zero new user-facing business logic, alters no API wire schemas for valid requests, and changes no mathematical scoring outputs. It replaces permissive types with strict contracts and deceptive mocks with stateful fakes. Any unexpected test failure post-migration represents a pre-existing latent defect, not a planned behavioral modification.

### 3.5 Context & Knowledge Item Coverage Audit
- **Rule Verification**: 6 rules physically verified (`00-antigravity-core.md`, `01-python-backend.md`, `02_flutter_desktop.md`, `03_seed_vault.md`, `04_directory_reference.md`, `05_llm_architecture.md`).
- **Knowledge Item Verification**: 14 Knowledge Items verified:
  - `ki_zero_permissive_typing.md`
  - `ki_god_code_prevention.md`
  - `ki_python_314_concurrency_strictness.md`
  - `ki_epic_lifecycle_workflow.md`
  - `ki_execution_record_ssot.md`
  - `ki_dag_engine_dto_projection_rules.md`
  - `ki_tripartite_pipeline_architecture.md`
  - `ki_opentelemetry_logfire_observability.md`
  - `ki_shared_storage_driver_architecture.md`
  - `ki_desktop_pro_tool_studio_ux.md`
  - `ki_dumb_painter_sdui.md`
  - `ki_unified_matrix_scoring_strictness.md`
  - `ki_workflow_context_governance.md`
  - `ki_execution_engine_protocol.md`
- **Result Log**: Context & KI Coverage Audit: 6 Rules verified, 14 KIs verified.

---

## 4. 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Physical Boundary SSOT** (`scripts/_ast_guardrails.py`, `scripts/audit_dict_eradication.py`) | Banned basename matching (`Path(filepath).name in ...`) that exempts any file sharing a name. Banned two divergent exemption sets. Banned exempting files under `backend_v2/models/`, `backend_v2/services/`, `backend_v2/hooks/`, `backend_v2/api/`. | ONE `frozenset[str]` `BOUNDARY_EXEMPTION_FILES` of 15 workspace-relative POSIX paths, imported by identity into `audit_dict_eradication.py`. | Deleted `LOCKED_PHYSICAL_DRIVERS` symbol; zero regex or glob discovery. | `backend_v2/tests/unit/scripts/test_ast_guardrails.py`: (1) every set member exists on disk; (2) fixture `models/dtos/telemetry.py` is NOT exempt; (3) no member starts with `backend_v2/models/`, `backend_v2/services/`, `backend_v2/hooks/`, `backend_v2/api/`. `test_audit_dict_eradication.py`: `audit_dict_eradication.BOUNDARY_EXEMPTION_FILES is _ast_guardrails.BOUNDARY_EXEMPTION_FILES`. Admission ratchet: each of the 9 newly admitted paths scanned with `BOUNDARY_EXEMPTION_FILES=frozenset()` returns 0 violations. |
| **Domain & DTO Models with 1-hop consumers** (17 model files; consumers `context_variables.py`, `synthesis_engine.py`, `matrix_reducer.py`, `matrix_explanation_service.py`, `ingress_service.py`, `test_synthesis_engine.py`, `test_ingress_service.py`) | Banned `dict[str, Any]`, `dict[str, object]`, `list[dict[...]]`, `dict[..., dict[...]]`. Banned closed `extra="forbid"` DTOs invented for open JSON Schema / provider payloads. Banned assigning `DomainInputValue` to ingress-origin values without origin trace. Banned schema change without same-phase consumer migration. | Field Classification Gate (Section 2.4). Closed DTOs use `ConfigDict(strict=True, extra="forbid", frozen=True)`. Open JSON uses `dict[str, JsonValue]`. Reuse `ProviderMetadataDTO`, `ReportDataDTO`, `StepTraceMetadataDTO`, `IngressInputValue`, `DomainInputValue`. | Pruned [NEW] DTOs: `LLMProviderRawExtraDTO`, `ModelParametersDTO`, `StudioMockInputsDTO`, `MCPParameterSchemaDTO`, `MCPInvocationArgumentsDTO`, `MCPProviderFieldsDTO`, `MCPResultPayloadDTO`, `SystemInputSchemaDTO`, `ProviderExecutionMetadataDTO`, `ClientErrorContextDTO`, `FlatReportSummaryDTO`, `RawSeedDatabaseDTO`. Dropped dead fields `model_params`, `flat_report`. | `uv run python scripts/audit_dict_eradication.py backend_v2/models --strict` = 0. Per retyped field: 1 positive + 2 negative tests (malformed nested value raises `ValidationError`; unknown key raises `ValidationError` on CLOSED DTOs). Atomic test migration verifies `test_synthesis_engine.py` and `test_ingress_service.py#L226`. Global `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` green at phase end. |
| **Exceptions, Hooks, LLM & Core** (`backend_v2/exceptions.py`, 4 hooks, `backend_v2/llm/caching_service.py`, `backend_v2/llm/client.py`, 6 adapters, `backend_v2/core/registry.py`, `backend_v2/core/rate_limit.py`, `backend_v2/main.py`) | Banned dual-branch `ExceptionDetailsDTO \| dict[str, JsonValue]` contract. Banned union return `list[LLMMessageDTO] \| list[dict[str, Any]]`. Banned 3 parallel nested maps keyed by the same matrix ID. Banned passing raw DTOs to Starlette `JSONResponse` without `.model_dump(mode="json")`. | `AppException.details: dict[str, JsonValue] \| None`; `to_problem_detail() -> ProblemDetailDTO`; `BaseLLMAdapter.prepare_caching_payload() -> CachingPayloadResultDTO` with provider-native dict materialization confined to exempt adapter files and `backend_v2/llm/provider.py`. At network boundary in `main.py` and `rate_limit.py`, call `.model_dump(mode="json", exclude_none=True)` before passing to `JSONResponse` (preserves omitted-`instance` wire shape). | Pruned [NEW] `ExceptionDetailsDTO`. Pruned `MatrixScoreLevelsDTO` + `MatrixStatusMapDTO` in favor of one `MatrixAggregationStateDTO` when outer keys coincide. Typed dynamic model field dictionaries in `registry.py`. | `uv run mypy backend_v2` = 0 errors after `details` retyping (baseline probe: 32 errors in 5 files). `backend_v2/tests/unit/test_exceptions.py`: `ProblemDetailDTO` round-trip + non-JSON `details` value rejected by mypy fixture. `uv run python scripts/audit_dict_eradication.py backend_v2/llm/caching_service.py backend_v2/llm/client.py --strict` = 0. |
| **Test Persistence Doubles** (`backend_v2/tests/fakes/in_memory_repositories.py`, 49 census A files, 12 census B files, 3 census C files, 10 fixture files, 4 import-only files, `test_repositories_v2.py`) | Banned `DynamicRepoMethod`, `__getattribute__` method synthesis, `.return_value` / `.side_effect` on repositories, attribute replacement `<repo>.<attr> = AsyncMock(...)`, `patch.object` / `monkeypatch.setattr` on repositories, raw-dict seeding, `dict_to_obj`, `getattr` in `inject_fault`, driver mocks. | Stateful `InMemoryUnifiedWorkflowRepository` and per-entity fakes seeded through typed `IUnifiedWorkflowRepository` write methods; failures via `inject_fault()`; roundtrip `save` then `get` assertions; real `TinyDBDriver` over `tmp_path`. | Deleted `InMemoryBlueprintTransformerRepository` subclass; zero replacement wrapper class; reuse conftest fixtures `fake_workflow_repo`, `fake_prompt_block_repo`, `fake_output_profile_repo`, `fake_system_repo`. | Per batch: census command scoped to batch file list returns 0. Phase 7: hardened `QGR014` FATAL + `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict` = 0; `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository|dict_to_obj" -Recurse` = 0. `test_ast_guardrails.py`: 4 negative fixtures raise `QGR014`; 2 positive fixtures pass. Census commands A, B, C, and I return 0 before Phase 7 starts. |
| **Universal Quality Gate & Client Parity** (`scripts/backend_audit_loop.py`, `step_simulation.dart`, `prompt_block_simulation.dart`, `mcp_gateway.dart`) | Banned unwired scanners. Banned `Map<String, dynamic>` producers sending values the backend `IngressInputValue` union rejects. Banned client edits unrelated to retyped backend fields. | Stage 10/10 `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` returning exit 1 on any violation. Dart models mirror the backend union for `mock_inputs`; `input_schema` stays open JSON (`Map<String, Object?>`). | Removed `execution_record.dart` / `execution_metadata.dart` from scope of Phase 8 (sequenced to Phase 12). | `backend_v2/tests/unit/scripts/test_backend_audit_loop.py` asserts Stage 10 invocation and non-zero exit propagation. `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` and `uv run python scripts/audit_dto_parity.py` pass. |
| **Residual Persistence Vectors** (census D 32 files, census F 6 files, census K 7 files; `scripts/_ast_guardrails.py` QGR014) | Banned keyword-injected repository mocks, string-target repository-class patches bound to mocks, ad-hoc repository classes in test modules, `cast(Any, ...)` injection of non-conforming doubles. | Conftest in-memory fakes passed through `HookDependencies`, `HookContext`, and executor constructors; `patch("<module>.<RepositoryClass>", return_value=<InMemory*Repository instance>)` where worker constructs repository. | Zero new fake classes. QGR014 (f) resolves repository class names from a positive set built from `interfaces.py` and `repositories/` instead of substring predicate; (g) resolves interface method names from `interfaces.py` Protocols. | Census D, F, K = 0 per batch. `test_ast_guardrails.py`: 3 negative fixtures raise `QGR014`; 2 positive fixtures pass. |
| **Suppression & Cast Eradication** (`scripts/audit_dict_eradication.py`, `pyproject.toml`, 30 `# noqa` files, 13 `cast(Any, ...)` files, 155 `# type: ignore` files, `scripts/_ast_guardrails.py`, `scripts/backend_audit_loop.py`) | Banned `# noqa` of any code, `[REASON: ...]` suppression authorization, AST inline suppressors, `cast(Any, ...)`, `# type: ignore`, `warn_unused_ignores = false`. | Pydantic V2 adapter DTOs with `model_validate(obj, from_attributes=True)` for third-party attribute reads; `Model.model_validate({...})` for intentionally invalid test input; one central `prop-decorator` entry (Section 2.2 item 7); Config Suppression Ratchet in `audit_dict_eradication.py`. | Zero per-file allowlist; zero new QGR rule identifier (detection extends existing comment and call audits of `audit_dict_eradication.py`). | Census N, X, T = 0. `test_audit_dict_eradication.py`: negative fixtures `# noqa: QGR001 [REASON: x]`, `# noqa: E501`, `cast(Any, x)`, `# type: ignore[arg-type]` produce violations; `"# noqa"` inside string literal produces 0. `uv run mypy backend_v2` = 0 with `warn_unused_ignores = true`. |
| **Extended Dict Eradication** (tests 80 files, `scripts/` 9 files, production 6 files; `scripts/audit_dict_eradication.py`, `scripts/backend_audit_loop.py`, `scripts/_ast_guardrails.py`) | Banned `Mapping[str, Any]`, `Mapping[str, object]`, `MutableMapping[...]` with `Any` / `object` values, duck-typing union `HookState \| Mapping[str, Any]`, basename `test_` exclusion in AST and dict scanners, annotation-check exemption for tests, Stage 10 blindness to `scripts/`. | `is_test` and `_is_test_file` = path under `backend_v2/tests/`; `dict`, `Dict`, `Mapping`, `MutableMapping` with `Any` / `object` values flagged in every file outside `BOUNDARY_EXEMPTION_FILES`; Stage 10 runs `audit_dict_eradication.py backend_v2 scripts --strict`. | Zero separate test-only scanner. | Census P, M = 0; `audit_dict_eradication.py backend_v2 scripts --strict` = 0; `test_audit_dict_eradication.py` negative fixtures produce violations. |
| **Client Permissive Map Eradication** (48 Flutter files; `scripts/_dart_guardrails.py`, `scripts/flutter_audit_loop.py`) | Banned non-codec `Map<String, dynamic>`; banned advisory-only Dart guardrails. | Freezed DTOs mirroring backend CLOSED models; `Map<String, Object?>` for OPEN-JSON fields. New rule `DGR005` in `_dart_guardrails.py`. Rules `DGR001`, `DGR004`, and `DGR005` enforced as unconditional FATAL in `flutter_audit_loop.py` without requiring `--strict`. | Codec signatures retained (Section 2.2 item 6); zero handwritten JSON parsers. | Census R = 0; `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`; `uv run python scripts/audit_dto_parity.py`. |
| **Fake Test Bypass Eradication** (7 skip markers, 4 xfail markers; `scripts/_ast_guardrails.py`) | Banned unconditional `@pytest.mark.skip` / `@pytest.mark.xfail`; stale expected-failure reasons. | Environment-gated `pytest.mark.skipif` / runtime `pytest.skip` for missing credentials, input files, or SDKs remain (13 sites). New AST rule `QGR026` (FATAL) in `_ast_guardrails.py` prohibits unconditional skip/xfail markers and `pytest.xfail()` calls. | Zero quarantine mechanism. | Census S = 0 from Phase 1; `QGR026` enforced in Stage 4 of `backend_audit_loop.py`. |

---

## 5. Required Technical Debt Cleanups (Pre-Implementation Scope)

The following 10 pre-implementation cleanups are mandated for immediate execution in **Phase 1** prior to introducing new type models:
1. `[CLEANUP]` Convert `BOUNDARY_EXEMPTION_FILES` in `scripts/_ast_guardrails.py` to a `frozenset[str]` of 15 workspace-relative POSIX paths; delete `LOCKED_PHYSICAL_DRIVERS` in `scripts/audit_dict_eradication.py` and import the shared set.
2. `[CLEANUP]` Implement `ResidualDebtCeilingsDTO` in `scripts/audit_warning_baseline.py` and wire as Stage 9/10 of `scripts/backend_audit_loop.py`, enforcing exact-equality ceilings on all census categories.
3. `[CLEANUP]` Implement `QGR026` in `scripts/_ast_guardrails.py` to statically ban unconditional `@pytest.mark.skip`, `@pytest.mark.xfail`, module-level skip/xfail markers, and `pytest.xfail()` calls at FATAL severity.
4. `[CLEANUP]` Verify zero residual AST and dict-audit violations in `backend_v2/models/dtos/telemetry.py`, `backend_v2/api/routers/system/telemetry.py`, `backend_v2/services/sdui/adapters/base_adapter.py` (pre-flight verified clean at 0 violations) after losing accidental basename exemption.
5. `[CLEANUP]` Replace `validate_all_seed_collections` buffers in `backend_v2/seed/run_seed.py` with `ValidatedSeedBufferDTO`.
6. `[CLEANUP]` Type the OpenAPI spec in `backend_v2/scripts/generate_openapi.py` as `dict[str, JsonValue]`.
7. `[CLEANUP]` Return typed domain models from `backend_v2/database/repositories/execution.py` and `backend_v2/database/repositories/workflow.py`.
8. `[CLEANUP]` Replace `getattr` reflection in `backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py` with typed `ast` node matching.
9. `[CLEANUP]` Delete the 4 permanently skipped test files `backend_v2/tests/architecture/test_boundaries.py`, `backend_v2/tests/unit/test_epic_61_hardening.py`, `backend_v2/tests/unit/test_provider_rate_limit.py`, `backend_v2/tests/unit/llm/test_fallback_caching.py`, and the 2 skipped functions `test_aspirational_html_escape` in `test_ast_domain_security_guardrails.py` and `test_all_ok_matrices_have_exactly_three_claims` in `test_matrix_data_integrity.py`.
10. `[CLEANUP]` Remove the 4 `@pytest.mark.xfail` markers in `backend_v2/tests/unit/hooks/test_scoring.py`; migrate the raw evaluation dicts of `test_failed_atom_with_override_does_not_inflate_score` and `test_matrix_scoring_hook_illegal_override_penalty` to typed `ExecutionInputsDTO.raw_inputs` fixtures.

---

## 6. ISTQB Negative Boundary Partitions

Every feature must possess at least two deterministic negative test cases per ISTQB Boundary Value Analysis:
1. **Boundary Exemption Set Partitions (`scripts/_ast_guardrails.py`)**:
   - *Negative 1 (Basename Collision)*: Assert that a path sharing a filename under a domain folder (specifically `backend_v2/models/dtos/telemetry.py`) is rejected by `BOUNDARY_EXEMPTION_FILES`.
   - *Negative 2 (Non-Existent Path)*: Assert that a non-existent file path is rejected by `test_ast_guardrails.py` set-membership verification.
   - *Negative 3 (Domain Boundary Infiltration)*: Assert that no entry in `BOUNDARY_EXEMPTION_FILES` starts with `backend_v2/models/`, `backend_v2/services/`, `backend_v2/hooks/`, or `backend_v2/api/`.
2. **Hardened QGR014 Partitions (`scripts/_ast_guardrails.py`)**:
   - *Negative 1 (Fixture Return Mock)*: Fixture returning `AsyncMock()` under a repository identifier triggers FATAL `QGR014`.
   - *Negative 2 (Attribute Replacement)*: Assigning `repo.get_execution = AsyncMock(...)` triggers FATAL `QGR014`.
   - *Negative 3 (Keyword Injection)*: Calling `HookDependencies(exec_repo=MagicMock())` triggers FATAL `QGR014`.
   - *Negative 4 (String Patch without Fake)*: Calling `patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` triggers FATAL `QGR014`.
   - *Negative 5 (Ad-Hoc Class)*: Defining a test class containing `def get_output_profile_by_id(...)` triggers FATAL `QGR014`.
   - *Positive Boundary*: Assert that `mock_report_service.get_report.return_value = ...` and patching `get_storage_driver` are explicitly permitted.
3. **QGR026 Unconditional Skip/Xfail Partitions (`scripts/_ast_guardrails.py`)**:
   - *Negative 1 (Unconditional Skip)*: Decorator `@pytest.mark.skip(...)` triggers FATAL `QGR026`.
   - *Negative 2 (Unconditional Xfail)*: Decorator `@pytest.mark.xfail(...)` triggers FATAL `QGR026`.
   - *Negative 3 (Direct Call)*: Invoking `pytest.xfail(...)` inside a test body triggers FATAL `QGR026`.
   - *Positive Boundary*: Environment-gated `@pytest.mark.skipif(...)` and runtime `pytest.skip(...)` are permitted.
4. **DGR005 Loose Dart Map Partitions (`scripts/_dart_guardrails.py`)**:
   - *Negative 1 (Loose Map Return)*: Method returning `Map<String, dynamic>` triggers FATAL `DGR005`.
   - *Negative 2 (Loose Map Parameter)*: Method accepting `Map<String, dynamic>` outside codec methods triggers FATAL `DGR005`.
   - *Positive Boundary*: `fromJson(Map<String, dynamic> json)` and `Map<String, dynamic> toJson()` pass cleanly.
5. **Pydantic V2 CLOSED DTO Partitions**:
   - *Negative 1 (Extra Key Invariant)*: Passing an unrecognized key to any CLOSED DTO (specifically `SystemConfigOptionDTO(key="x", extra_val="invalid")`) triggers `ValidationError`.
   - *Negative 2 (Type Invariant)*: Passing a string to an integer/float field triggers `ValidationError` under `strict=True`.
6. **Open JSON & Ingress Input Partitions**:
   - *Negative 1 (Non-JSON Value in JsonValue)*: Passing a Python lambda or function pointer to `dict[str, JsonValue]` triggers `ValidationError`.
   - *Negative 2 (Nested Map in IngressInputValue)*: Passing a nested dictionary `{"sub": {"nested": "value"}}` to `mock_inputs` triggers `ValidationError`.
7. **Config Suppression Ratchet Partitions (`scripts/audit_dict_eradication.py`)**:
   - *Negative 1 (Unapproved Ruff Ignore)*: Adding an unapproved code to `tool.ruff.lint.ignore` in `pyproject.toml` triggers audit failure.
   - *Negative 2 (Unapproved Dart Ignore)*: Adding an unapproved rule to `analysis_options.yaml` triggers audit failure.

---

## 7. Verification Commands & Proof Anchors

All phases and completion gates are verified using the following exact Windows PowerShell commands:

### Global Completion Gate
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
uv run python scripts/flutter_audit_loop.py client_app_v2/ --build
```

### Dict Eradication Audit (Stage 10/10)
```powershell
uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict
```

### Residual Debt Ceiling Ledger (Stage 9/10)
```powershell
uv run python scripts/audit_warning_baseline.py --verify-zero
```

### Test Persistence Census Verification Commands
```powershell
# Census A: Method .return_value / .side_effect (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Select-String -Pattern '\b(\w*repo\w*)\.\w+\.(return_value|side_effect)\s*=' | Where-Object { `$_.Matches[0].Groups[1].Value -notmatch 'report|response' } | Measure-Object"

# Census B: Attribute Replacements (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Select-String -Pattern '\b(\w*repo\w*)\.\w+\s*=\s*(AsyncMock|MagicMock|Mock)\(' | Where-Object { `$_.Matches[0].Groups[1].Value -notmatch 'report|response' } | Measure-Object"

# Census C: Object Patches (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Select-String -Pattern '\b(patch\.object|monkeypatch\.setattr)\(\s*(\w*repo\w*)\s*,' | Where-Object { `$_.Matches[0].Groups[2].Value -notmatch 'report|response' } | Measure-Object"

# Census I: Emulation-Fake Imports outside fakes (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Where-Object { `$_.FullName -notmatch '\\tests\\fakes\\|\\tests\\unit\\fakes\\' } | Select-String -Pattern 'InMemoryBlueprintTransformerRepository' -List | Measure-Object"

# Census D: Keyword-Injected Mocks (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Select-String -Pattern '\b(\w*repo\w*)=(AsyncMock|MagicMock|Mock)\(' -AllMatches | Where-Object { `$_.Matches[0].Groups[1].Value -notmatch 'report|response' } | Measure-Object"

# Census F: String-Target Repository Patches (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Where-Object { `$_.FullName -notmatch '\\tests\\unit\\scripts\\' } | Select-String -Pattern 'patch\(\s*[\""''][\w\.]*\.(\w*Repository)[\""'']' | Measure-Object"

# Census K: Ad-Hoc Repository Classes (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Where-Object { `$_.FullName -notmatch '\\tests\\fakes\\|\\tests\\unit\\fakes\\|test_ast_engine_dispatch_guardrails' } | Select-String -Pattern '^\s*class\s+(\w*Repo\w*)\b' | Where-Object { `$_.Matches[0].Groups[1].Value -notmatch 'Report|Response' } | Measure-Object"

# Census X: cast(Any, ...) (Must be 0)
powershell -Command "Get-ChildItem backend_v2, scripts -Recurse -Filter '*.py' | Select-String -Pattern 'cast\(\s*Any\b' -AllMatches | Measure-Object"

# Census T: # type: ignore (Must be 0)
powershell -Command "Get-ChildItem backend_v2, scripts -Recurse -Filter '*.py' | Select-String -Pattern '#\s*type:\s*ignore' | Measure-Object"

# Census P: Naked Dicts in Tests and Scripts (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests, scripts -Recurse -Filter '*.py' | Select-String -Pattern '\b[Dd]ict\[\s*str\s*,\s*(Any|object)\s*\]' | Measure-Object"

# Census M: Production Mapping Sites & test_settings.py (Must be 0)
powershell -Command "(`@(Get-ChildItem backend_v2 -Recurse -Filter '*.py' | Where-Object { `$_.FullName -notmatch '\\backend_v2\\tests\\' } | Select-String -Pattern '\b(Mutable)?Mapping\[\s*str\s*,\s*(Any|object)\s*\]') + `@(Select-String -Path backend_v2/core/test_settings.py -Pattern '\b[Dd]ict\[\s*str\s*,\s*(Any|object)\s*\]')).Count"

# Census R: Non-Codec Dart Maps (Must be 0)
powershell -Command "(`$m = Get-ChildItem client_app_v2/lib -Recurse -Filter '*.dart' | Where-Object { `$_.Name -notmatch '\.(g|freezed)\.dart$' } | Select-String -Pattern 'Map<String,\s*dynamic>' -AllMatches | Where-Object { `$_.Line -notmatch 'fromJson\(\s*Map<String,\s*dynamic>\s+\w+\s*\)|Map<String,\s*dynamic>\s+toJson\(' }); (`$m | ForEach-Object { `$_.Matches.Count } | Measure-Object -Sum).Sum"

# Census S: Unconditional Skip/Xfail Markers (Must be 0)
powershell -Command "Get-ChildItem backend_v2/tests -Recurse -Filter '*.py' | Select-String -Pattern '@pytest\.mark\.(skip|xfail)\b' | Measure-Object"
```

### Full-Duplex DTO Parity & SDUI Semantic Parity
```powershell
uv run python scripts/audit_dto_parity.py
uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
```

---

## 8. Conclusion & Recommendation

The deep System 2 research, adversarial cross-examination, and mathematical census validation confirm that **EPIC 157 is an architectural masterpiece of rigor, clarity, and mathematical precision**:
1. All baseline figures across 14 distinct census categories have been verified against the physical codebase to the exact character.
2. The 13 execution phases are cleanly decoupled, sequencing technical debt eradication and pre-implementation cleanups in Phase 1 before downstream model and fake migrations.
3. The mock-emulation sunset in Phase 7 permanently eliminates green-test deception, backed by hardened AST guardrails.
4. The Residual Debt Ceiling Ledger in Phase 1 guarantees zero architectural drift or debt creep during the entire migration lifecycle.

**Recommendation:** Proceed immediately to `/tier1-tracker-generator` to synthesize the synchronized Double-Entry Bookkeeping Tracker (`docs/epic/EPIC_157_tracker.md`), followed by `/tier1-planner` to author the implementation plan for Phase 1.
