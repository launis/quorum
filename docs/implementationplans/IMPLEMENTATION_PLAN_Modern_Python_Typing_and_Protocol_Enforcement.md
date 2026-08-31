# Unified Implementation Plan: Modern Python Typing, 100% Protocol Reconstitution, Dict Eradication & Strict Boundary Lockdown

This comprehensive implementation plan combines Python 3.12–3.14+ typing modernization, 100% typing reconstitution of ALL 15 database protocols and repositories (Ingress DTOs & Egress Domain Models), eradication of permissive dictionary utility anti-patterns (`dict_utils.py`), new stateful In-Memory Protocol Fake testing infrastructure, static AST Guardrail engine expansion alongside **Permanent Lockdown of `BOUNDARY_EXEMPTION_FILES` to ONLY 5 physical SDK/storage & pre-validation drivers (`interfaces.py`, `driver.py`, `wrapper.py`, `exceptions.py`, `finops_trace_analyzer.py`, and `dict_utils.py` removed/deleted; `alias_engine.py` retained as pre-validation boundary)**.

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

## User Review Required

> [!IMPORTANT]
> - **Grand Unified Protocol & Zero-Permissive Lockdown (15/15 Protocols Typed + Dict Eradication)**:
>   - **Part A: Core Pipeline, Execution Ingress/Mutation & Generics Modernization**
>     - Reconstitute `IExecutionRepository`, `IWorkflowRepository`, `IComponentRepository`, `IMatrixRepository`, `IAgentRepository`, `IExecutionPersonaRepository`, `IExtractionProtocolRepository` in `@[backend_v2/database/interfaces.py]`.
>     - Introduce `ExecutionUpdateDTO` as the SSOT for partial execution state updates and migrate all 12+ callers across `progress.py`, `execution.py`, `blueprint.py`, `dag_executor.py`, and `llm.py` to construct strongly typed DTOs.
>     - Refactor `@[backend_v2/core/hook_registry.py]` to PEP 695 generic method syntax (`def register[F: HookFunction]`) and type `ISearchClient.search()` return to `TavilySearchResultDTO`.
>     - Build `@[backend_v2/tests/fakes/in_memory_repositories.py]` (`InMemoryWorkflowRepository`, `InMemoryExecutionRepository`, `InMemoryComponentRepository`).
>   - **Part B: Domain Identity, Knowledge, System, Audit & Utility Modernization**
>     - Reconstitute ALL remaining 8 protocols in `@[backend_v2/database/interfaces.py]` (including all 8 methods of `ISystemRepository` and all 7 methods of `IAuditRepository`): `IIdentityRepository`, `IKnowledgeRepository`, `ISystemRepository`, `IAuditRepository`, `IPromptBlockRepository`, `IOutputProfileRepository`, `ITaskBlueprintRepository`, `IRoleRepository`.
>     - **DELETE `dict_utils.py` & `test_dict_utils.py`**: Relocate pure `resolve_dot_notation()` utility into `@[backend_v2/utils/math_utils.py]` and update `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`. Relocate `deep_merge_dicts` as a private `_deep_merge()` helper in `@[backend_v2/services/orchestrator/strategies/base.py]` for dynamic input blackboard reduction, while all domain-level updates enforce canonical Pydantic V2 `.model_copy(update=...)` and typed DTOs.
>     - **Modernize `exceptions.py`**: Refactor `AppException` and validation error formatting to use typed `ErrorDetails` (Pydantic V2) with 0 `.get()` / `getattr()` calls.
>     - **Modernize `finops_trace_analyzer.py`**: Introduce `MonitorState` and `TelemetryRecord` DTOs, replacing raw `.get()` calls with dot-notation.
>     - **Alias Engine Pre-Validation Boundary**: `alias_engine.py` is preserved as a legitimate pre-validation boundary driver in `BOUNDARY_EXEMPTION_FILES` per `atom_aliasing_hydration_mandate`.
>   - **Part C: Permanent Boundary Exemption Lockdown (Strict 5-Driver Firewall)**
>     - **6 Files Removed/Deleted from `BOUNDARY_EXEMPTION_FILES`**: `interfaces.py`, `driver.py`, `wrapper.py`, `exceptions.py`, `finops_trace_analyzer.py`, `dict_utils.py`.
>     - **ONLY 5 Legitimate Physical & Pre-Validation Drivers Retained**: `tinydb_driver.py` (disk JSON driver), `firestore_driver.py` (GCP Firestore SDK), `provider.py` (LiteLLM / AI Provider network boundary), `logging_config.py` (Python stdlib logging formatter), `alias_engine.py` (LLM pre-validation hydration boundary).
>     - Expand AST Guardrail engine with `QGR013` (ban `TypeVar`), `QGR014` (warn on `AsyncMock` in services), and `QGR015` (ban `TypeGuard` per PEP 742 `pep742_typeis_over_typeguard`).
>     - Synchronize existing test in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L827-L835]` (`test_ast_guardrails_allows_exempt_driver_annotations`) from `interfaces.py` to `tinydb_driver.py`.

> [!WARNING]
> - **QGR014 Severity is `WARNING`**:
>   - The codebase contains test files that legitimately utilize `AsyncMock`/`MagicMock` for non-database dependencies (`LLMClient`, `PromptCompiler`, `Settings`). The rule is maintained at `WARNING` level for progressive, non-breaking test migration.

---

## Deterministic Verification & Inventory: Dictionaries & `# noqa` Suppressions

### 1. Complete Protocol Typing Scope Inventory (15/15 Protocols)

| Entity / Protocol | Current Permissive Pattern | Target 100% Reconstitution | Status | Rationale / Boundary |
| :--- | :--- | :--- | :--- | :--- |
| `IExecutionRepository` (all methods) | `execution_data: dict`, `updates: dict`, `event_data: dict` | `ExecutionCreateDTO \| ExecutionRecord`, `ExecutionUpdateDTO \| ExecutionRecord`, `TraceEvent \| ErrorTraceEvent \| TombstoneEvent` | `[x]` | Strongly typed execution ingress/mutation DTOs |
| `IWorkflowRepository` (all methods) | `workflow_data: dict`, `updates: dict`, `step_data: dict` | `WorkflowCreateDTO \| Workflow`, `WorkflowUpdateDTO \| Workflow`, `StepCreateDTO \| Step`, `StepUpdateDTO \| Step` | `[x]` | Strongly typed workflow & step DTOs |
| `IComponentRepository` (all methods) | `-> list[dict]`, `comp_data: dict` | `-> list[PromptBlock]`, `comp: PromptBlock` | `[x]` | Reconstituted PromptBlock Domain models |
| `IMatrixRepository` (all 4 methods) | `dict[str, Any]` params/returns | `PromptBlock` / `list[PromptBlock]` | `[x]` | Reconstituted PromptBlock Domain models |
| `IAgentRepository` (all 4 methods) | `dict[str, Any]` params/returns | `PromptBlock` / `list[PromptBlock]` | `[x]` | Reconstituted PromptBlock Domain models |
| `IExecutionPersonaRepository` (all 4 methods) | `dict[str, Any]` params/returns | `PromptBlock` / `list[PromptBlock]` | `[x]` | Reconstituted PromptBlock Domain models |
| `IExtractionProtocolRepository` (all 4 methods) | `dict[str, Any]` params/returns | `PromptBlock` / `list[PromptBlock]` | `[x]` | Reconstituted PromptBlock Domain models |
| `IIdentityRepository` (all 14 methods) | `org_data: dict`, `updates: dict`, `user_data: dict` | `OrganizationCreate \| Organization`, `OrganizationUpdateDTO`, `UserCreate \| User`, `UserUpdateDTO` | `[x]` | Reconstituted Auth & RBAC Domain DTOs |
| `IKnowledgeRepository` (all 10 methods) | `add_concept(dict)`, `add_claim(dict)`, `add_reference(dict)` | `ConceptCreateDTO \| Concept`, `ClaimCreateDTO \| Claim`, `ReferenceCreateDTO \| Reference`, `BannedPhrase` | `[x]` | Reconstituted Knowledge Domain DTOs |
| `ISystemRepository` (all 8 methods) | `update_model_registry(dict)`, `update_mcp_gateways(dict)`, `update_system_settings(dict)`, `create_system_config(dict)` | `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `SystemConfig`, `SystemConfigUpdateDTO`, `SystemConfigCreateDTO` | `[x]` | 100% Reconstituted System Config DTOs across all 8 methods |
| `IAuditRepository` (all 7 methods) | `log_audit_event(dict)`, `upsert_usage_aggregate(dict)`, `get_usage_aggregate() -> dict`, `get_detailed_usage() -> dict`, `log_usage(Any)` | `AuditLogCreateDTO \| AuditLogEntry`, `UsageAggregateUpdateDTO`, `UsageAggregateDTO`, `DetailedUsageDTO`, `UsageRecord` | `[x]` | 100% Reconstituted Audit & Usage DTOs across all 7 methods |
| `IPromptBlockRepository` (all 8 methods) | `create_prompt_block(dict)`, `update_prompt_block(dict)` | `PromptBlockCreateDTO \| PromptBlock`, `PromptBlockUpdateDTO \| PromptBlock` | `[x]` | Reconstituted PromptBlock DTOs |
| `IOutputProfileRepository` (all 6 methods) | `create_output_profile(dict)`, `update_output_profile(dict)` | `OutputProfileCreateDTO \| OutputProfile`, `OutputProfileUpdateDTO \| OutputProfile` | `[x]` | Reconstituted OutputProfile DTOs |
| `ITaskBlueprintRepository` (all 5 methods) | `create_task_blueprint(dict)`, `update_task_blueprint(dict)` | `StepCreateDTO \| Step`, `StepUpdateDTO \| Step` | `[x]` | Reconstituted Step/Blueprint DTOs |
| `IRoleRepository` (all 5 methods) | `create_role(dict)`, `update_role(dict)` | `RoleCreateDTO \| Role`, `RoleUpdateDTO \| Role` | `[x]` | Reconstituted Role DTOs |
| `dict_utils.py` | `deep_merge_dicts()` and loose helper functions | **PERMANENTLY DELETED**; `_deep_merge` in `base.py` | `[x]` | Banned dict module completely removed |
| `finops_trace_analyzer.py` | 9x `.get()` calls on raw dicts | `MonitorState` & `TelemetryRecord` Pydantic DTOs | `[x]` | Strongly typed telemetria DTOs |
| `exceptions.py` | `.get("error_code")` & `.get("loc")` | Typed `ErrorDetails` (Pydantic V2) | `[x]` | Typed RFC 7807 problem details |
| `alias_engine.py` | `isinstance(node, dict)` recursion | Retained in `BOUNDARY_EXEMPTION_FILES` | `[x]` | Pre-validation LLM hydration boundary |
| `ISearchClient.search()` (`hook_registry.py`) | `-> list[dict[str, Any]]` | `-> TavilySearchResultDTO` | `[x]` | Reconstituted retrieval DTO |
| `ComponentRepositoryImpl.get_all_components` | `c["type"] not in exclude_types` | `c.type not in exclude_types` | `[x]` | Dot-notation attribute filtering |
| `ComponentRepositoryImpl.get_components_using_dimension` | `c.get("content").get("criteria")` + `try/except` | Dot-notation on `PromptBlock.content.criteria` | `[x]` | Typed dot-notation, zero fallback dicts |
| `MatrixRepositoryImpl.get_matrices_using_dimension` | `m.get("content").get("criteria")` + `try/except` | Dot-notation on `PromptBlock.content.criteria` | `[x]` | Typed dot-notation, zero fallback dicts |
| `ExecutionRepositoryImpl.get_execution_status` | `data["status"]` | `ExecutionRecord.status` | `[x]` | Typed model attribute access |
| `ExecutionRepositoryImpl.create_execution` | `if "id" in execution_data` | `execution_data.id` | `[x]` | Typed DTO attribute access |
| 12+ `update_execution` Callers across 5 services | Raw dict literals `{"status": ...}` | `ExecutionUpdateDTO(...)` | `[x]` | Migrated callers to typed DTO |
| `HookRegistry._hooks` (`hook_registry.py`) | `_hooks: dict[str, HookFunction]` | Retained `dict[str, HookFunction]` | `[ ]` | Permissible in-memory registry map |
| Repository Persistence Drivers (`tinydb_driver.py`) | `doc: dict[str, Any]` | Internal JSON serialization boundary | `[ ]` | Permissible driver storage boundary |
| `ExecutionUpdateDTO.step_states` (`trace.py`) | `dict[str, Any] \| None` | Validated via `TypeAdapter` on consumer | `[ ]` | Permissible polymorphic DAG payload |
| `BOUNDARY_EXEMPTION_FILES` Lockdown | 11 files exempt | **LOCKED TO 5 PHYSICAL & PRE-VAL DRIVERS** | `[x]` | 6 non-driver files purged from exemption |

---

### 2. `# noqa` Suppression Remediation Inventory

| File & Location | Suppression Rule & Reason | Target Remediation | Status |
| :--- | :--- | :--- | :--- |
| `backend_v2/services/execution.py#L863` | `# noqa: QGR012 [REASON: Polymorphic DAG payload validation]` | **ERADICATE**: Remove dict check & suppression; iterate typed `PromptBlock` directly | `[x]` |
| `backend_v2/models/dtos/system.py#L50` | `# noqa: QGR001 [REASON: Client error telemetry payload]` | **RETAIN**: Raw HTTP ingress payload at external ACL | `[ ]` |
| `backend_v2/worker.py#L402,L423,L475,L590,L619,L840,L1377` | `# noqa: QGR003 [REASON: Background worker DLQ catch-all]` | **RETAIN**: Top-level background worker crash boundaries | `[ ]` |
| `backend_v2/main.py#L154,L161` | `# noqa: QGR001 [REASON: FastAPI dynamic app.state lookup]` | **RETAIN**: Framework lifespan dependency lookup | `[ ]` |
| `backend_v2/services/llm_task_executor.py#L208` | `# noqa: QGR003 [REASON: Telemetry logging errors]` | **RETAIN**: Non-blocking telemetry isolation | `[ ]` |
| `backend_v2/services/cache/typed_cache.py#L57` | `# noqa: QGR003 [REASON: Best-effort cache auto-eviction]` | **RETAIN**: Non-blocking cache cleanup | `[ ]` |

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **All 15 Database Protocols** (`@[backend_v2/database/interfaces.py]`) | Banned `dict[str, Any]` and `list[dict[str, Any]]` return types and input parameters across ALL 15 protocol definitions. Eradicated exemption status. | 100% strongly typed Protocol methods accepting strict Pydantic DTOs and returning frozen Domain models. | Pruned: Zero intermediate raw mapping dicts or parallel loose interfaces. Single cohesive protocol per domain. | `uv run python scripts/_ast_guardrails.py backend_v2/database/interfaces.py` passes with 0 violations without exemption. |
| **Ingress & Update DTOs** (`@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/models/dtos/trace.py]`, `@[backend_v2/models/auth.py]`, `@[backend_v2/models/domain/knowledge.py]`, `@[backend_v2/models/domain/base.py]`) | Banned unvalidated `dict[str, Any]` updates in workflow, step, execution, identity, knowledge, system, and audit mutation pathways. | Explicit `WorkflowUpdateDTO`, `StepUpdateDTO`, `ExecutionCreateDTO`, `ExecutionUpdateDTO`, `OrganizationUpdateDTO`, `UserUpdateDTO`, `ConceptCreateDTO`, `ClaimCreateDTO`, `ReferenceCreateDTO`, `AuditLogCreateDTO`, `UsageAggregateUpdateDTO` with `ConfigDict(strict=True, extra="forbid")`. | Pruned: No dynamic untyped kwargs unpacking; structured Pydantic payload models only. Migrates all callers across services to typed DTOs. | Unit test validation in `test_studio_dtos.py`, `test_execution.py`, `test_auth.py` with ISTQB negative validation partitions. |
| **Repository Implementations** (`@[backend_v2/database/repositories/...]`) | Banned returning raw driver dictionaries and accepting loose dictionaries in repository write/update methods across all 11 repository modules. | Automatic ingress model dumping to JSON-safe driver records via `.model_dump(mode="json", exclude_unset=True)`, and instant reconstitution into domain models on retrieval (`Model.model_validate(raw, strict=False)`). Pure dot-notation in dimension filters. | Persistence drivers (`driver.py`, `tinydb_driver.py`) handle low-level serialization; repository enforces strict domain boundaries. | `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test`. |
| **Dictionary Utilities Deletion & Relocation** (`@[backend_v2/utils/dict_utils.py]`) | Banned `deep_merge_dicts()` and dictionary mutation helper functions in domain services. | Delete `dict_utils.py` entirely. Relocate `deep_merge_dicts()` as a private `_deep_merge()` helper in `@[backend_v2/services/orchestrator/strategies/base.py]` for dynamic inputs blackboard reduction, while all domain-level updates enforce canonical Pydantic V2 `.model_copy(update=...)` and typed DTOs. Relocate pure utility `resolve_dot_notation()` to `@[backend_v2/utils/math_utils.py]` and update `context_builder.py`. | Pruned: Eliminate psychological anti-pattern magnet entirely from repository. | `grep_search` verifies 0 imports of `dict_utils` across entire codebase. |
| **Modern Generics & Registry** (`@[backend_v2/core/hook_registry.py]`) | Banned legacy `TypeVar("F", bound=HookFunction)` instantiation, `list[dict]` search return, and outdated docstrings referencing `Dict -> Dict`. | PEP 695 generic method syntax: `def register[F: HookFunction](self, name: str) -> Callable[[F], F]:`, and `ISearchClient.search()` returning `TavilySearchResultDTO`. | Pruned: Eradicate module-level `TypeVar` boilerplate, naked search result dicts, and legacy dictionary docstrings. | `uv run mypy --strict backend_v2/core/hook_registry.py` and `uv run pytest backend_v2/tests/unit/core/test_hook_registry.py -v`. |
| **In-Memory Protocol Fakes** (`@[backend_v2/tests/fakes/in_memory_repositories.py]`) | Banned brittle mock fixtures with manual dict configurations for database repositories. | State-backed `InMemoryWorkflowRepository`, `InMemoryExecutionRepository`, `InMemoryComponentRepository`, `InMemoryIdentityRepository`, `InMemoryKnowledgeRepository` adhering 100% to typed Protocols. | Pruned: No ad-hoc mock patches in service tests; deterministic in-memory dict state engine. | `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py -v`. |
| **AST Guardrail 5-Driver Lockdown** (`@[scripts/_ast_guardrails.py]`) | Banned unchecked legacy typing patterns (`TypeVar`, `TypeGuard`, `AsyncMock` in service tests) and **PURGED 6 non-driver files from `BOUNDARY_EXEMPTION_FILES`**. | Add `QGR013` (`TypeVar`), `QGR014` (`AsyncMock`), and `QGR015` (`TypeGuard` ban per PEP 742 `pep742_typeis_over_typeguard`). Enforce FATAL AST scan across all domain files. Synchronize test fixture in `test_ast_guardrails.py#L830`. | Pruned: No complex runtime reflection; pure static AST visitor pattern. | `uv run python scripts/_ast_guardrails.py backend_v2/` passes with 0 fatal violations. |

---

## Phase 1: Pre-Implementation Cleanups & Touched Scope Debt Sweep

1. **AST Guardrail Baseline Check**: Run `uv run python scripts/_ast_guardrails.py backend_v2/` to verify initial AST state (0 fatal violations).
2. **MyPy PEP 695 Support Check**: Verified `mypy 2.1.0` supports modern Python generic syntax (`def func[T](...)`).
3. **Execution Service Downstream Debt Cleanup**: In `@[backend_v2/services/execution.py#L856-L869]`, remove manual dictionary validation loop and `# noqa: QGR012 [REASON: Polymorphic DAG payload validation]` suppression once `ComponentRepositoryImpl.get_all_components()` returns strictly typed `list[PromptBlock]`.
4. **Hook Registry Header Docstring Modernization**: In `@[backend_v2/core/hook_registry.py#L1-L7]`, clean up docstring to reflect immutable Pydantic V2 state deltas instead of legacy `Dict -> Dict`.
5. **[DISCOVERED DEBT RESOLVED] `ComponentRepositoryImpl` Reconstitution & Typed Filtering**: In `@[backend_v2/database/repositories/component.py#L16-L158]`, `get_all_components()` must reconstitute all raw documents to `PromptBlock` via `PromptBlockAdapter`, refactor filtering logic (`c.type not in exclude_types`) from raw dict keys to typed model attributes, and eliminate cascading `.get()` chains and duct-tape `try...except` in `get_components_using_dimension()` in favor of 100% typed dot-notation.
6. **[DISCOVERED DEBT RESOLVED] `MatrixRepositoryImpl.get_matrices_using_dimension()`**: In `@[backend_v2/database/repositories/components/matrix.py#L82-L106]`, replace identical legacy `.get()` chains and duct-tape `try...except` copy-paste with 100% typed dot-notation on reconstituted `PromptBlock` models.
7. **[DISCOVERED DEBT] `ExecutionRepositoryImpl.get_execution_status()`**: In `@[backend_v2/database/repositories/execution.py#L207-L217]`, raw dict key access `data["status"]` must be accessed via typed `ExecutionRecord.status` after typed return.
8. **[DISCOVERED DEBT] `ExecutionRepositoryImpl.create_execution()`**: In `@[backend_v2/database/repositories/execution.py#L228]`, raw dict key check `if "id" in execution_data` must be replaced with typed DTO attribute access.
9. **[DISCOVERED DEBT RESOLVED] `ISearchClient.search()` Return Typing**: In `@[backend_v2/core/hook_registry.py#L49-L55]`, replace `list[dict[str, Any]]` return in `ISearchClient.search()` with `TavilySearchResultDTO` (from `backend_v2.models.dtos.retrieval`), eliminating naked dictionary returns from `HookDependencies`.
10. **[DISCOVERED DEBT RESOLVED] `resolve_dot_notation` Relocation & Import Cleanup**: Relocate pure utility function `resolve_dot_notation()` from `dict_utils.py` to `@[backend_v2/utils/math_utils.py]`, update callers in `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L15]`, and update its unit tests in `@[backend_v2/tests/unit/utils/test_math_utils.py]`.
11. **[DISCOVERED DEBT RESOLVED] Test Fixture Boundary Exemption Sync**: Update `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L830]` where `test_ast_guardrails_allows_exempt_driver_annotations` passes `backend_v2/database/interfaces.py` (which is being purged from exemption) to use `backend_v2/database/tinydb_driver.py` instead.

---

## Proposed Changes

### Domain & Ingress DTOs (`backend_v2/models/`)

#### [MODIFY] [`backend_v2/models/dtos/studio.py`](file:///c:/src/quorum/backend_v2/models/dtos/studio.py#L436-L446)
- Add `WorkflowUpdateDTO` and `StepUpdateDTO` with `ConfigDict(strict=True, extra="forbid")`:
  ```python
  class WorkflowUpdateDTO(BaseDTO):
      """DTO for updating an existing Workflow definition."""

      model_config = ConfigDict(strict=True, extra="forbid")

      name: Annotated[I18nText | str | None, Field(default=None, description="Updated localized workflow name")]
      description: Annotated[I18nText | str | None, Field(default=None, description="Updated description")]
      slug: Annotated[str | None, Field(default=None, pattern=r"^[a-zA-Z0-9_\-]+$", description="Updated routing slug")]
      expected_inputs: Annotated[list[ExpectedInput] | None, Field(default=None, description="Updated expected inputs")]
      steps: Annotated[list[StepRule] | None, Field(default=None, description="Updated step rules")]
      allowed_exports: Annotated[list[Literal["pdf", "docx", "raw_json", "xlsx"]] | None, Field(default=None)]
      historical_context_mode: Annotated[LaxHistoricalContextMode | None, Field(default=None)]
      default_profile_id: Annotated[str | None, Field(default=None)]
      status: Annotated[str | None, Field(default=None)]


  class StepUpdateDTO(BaseDTO):
      """DTO for updating an existing Step blueprint."""

      model_config = ConfigDict(strict=True, extra="forbid")

      name: Annotated[I18nText | None, Field(default=None)]
      description: Annotated[I18nText | None, Field(default=None)]
      slug: Annotated[str | None, Field(default=None)]
      type: Annotated[LaxStepType | None, Field(default=None)]
      hook: Annotated[str | None, Field(default=None)]
      role_block_id: Annotated[str | None, Field(default=None)]
      extraction_protocol_block_id: Annotated[str | None, Field(default=None)]
      execution_persona_block_id: Annotated[str | None, Field(default=None)]
      criteria_block_ids: Annotated[list[str] | None, Field(default=None)]
      pre_hooks: Annotated[list[str] | None, Field(default=None)]
      post_hooks: Annotated[list[str] | None, Field(default=None)]
      safety: Annotated[Literal["safe", "unsafe"] | None, Field(default=None)]
      allowed_mcp_tools: Annotated[list[str] | None, Field(default=None)]
      model_strategy: Annotated[str | None, Field(default=None)]
      expected_inputs: Annotated[list[str] | None, Field(default=None)]
  ```

#### [MODIFY] [`backend_v2/models/dtos/trace.py`](file:///c:/src/quorum/backend_v2/models/dtos/trace.py#L106-L116)
- Add `ExecutionCreateDTO` and `ExecutionUpdateDTO` for typed execution ingress and mutation (using `ExecutionMetadata` SSOT):
  ```python
  from datetime import datetime
  from backend_v2.models.enums import LaxExecutionStatus
  from backend_v2.models.execution_core import ExecutionMetadata


  class ExecutionCreateDTO(BaseDTO):
      """DTO for creating a new execution record at ingress boundary."""

      model_config = ConfigDict(strict=True, extra="forbid")

      workflow_id: Annotated[str, Field(min_length=1, description="Target workflow ID")]
      target_locale: Annotated[str, Field(default="fi", description="Target locale code")]
      status: Annotated[str, Field(default="PENDING", description="Initial lifecycle status")]
      metadata: Annotated[ExecutionMetadata | None, Field(default=None, description="Typed metadata SSOT")]


  class ExecutionUpdateDTO(BaseDTO):
      """Single Source of Truth (SSOT) DTO for partial execution updates."""

      model_config = ConfigDict(strict=True, extra="forbid")

      status: Annotated[LaxExecutionStatus | str | None, Field(default=None, description="Lifecycle status")] = None
      current_step: Annotated[str | None, Field(default=None, description="Current progress activity description")] = None
      current_step_name: Annotated[str | None, Field(default=None, description="Current step name")] = None
      progress: Annotated[int | None, Field(default=None, ge=0, le=100, description="Completion percentage 0-100")] = None
      error: Annotated[str | None, Field(default=None, description="Failure error message")] = None
      step_states: Annotated[dict[str, Any] | None, Field(default=None, description="DAG step states mapping")] = None
      profile_syntheses: Annotated[dict[str, Any] | None, Field(default=None, description="Rendered synthesis cache")] = None
      pdf_report_path: Annotated[str | None, Field(default=None, description="Generated PDF report path")] = None
      active_profile_id: Annotated[str | None, Field(default=None, description="Active profile ID")] = None
      output_profile_id: Annotated[str | None, Field(default=None, description="Target profile ID")] = None
      metadata: Annotated[ExecutionMetadata | None, Field(default=None, description="Execution metadata SSOT")] = None
      context_variables: Annotated[dict[str, Any] | None, Field(default=None, description="Dynamic blackboard")] = None
      is_resumable: Annotated[bool | None, Field(default=None, description="Resumable execution flag")] = None
      duration_ms: Annotated[int | None, Field(default=None, ge=0, description="Duration in milliseconds")] = None
      cost_estimate: Annotated[float | None, Field(default=None, ge=0.0, description="Estimated cost in USD")] = None
      models_used: Annotated[dict[str, int] | None, Field(default=None, description="Models token usage summary")] = None
      created_at: Annotated[datetime | str | None, Field(default=None, description="Creation timestamp")] = None
      updated_at: Annotated[datetime | str | None, Field(default=None, description="Update timestamp")] = None
      completed_at: Annotated[datetime | str | None, Field(default=None, description="Completion timestamp")] = None
  ```

#### [MODIFY] [`backend_v2/models/auth.py`](file:///c:/src/quorum/backend_v2/models/auth.py#L360-L382)
- Add `OrganizationUpdateDTO` and ensure `OrganizationCreate` & `UserUpdate` adhere to strict DTO standards:
  ```python
  class OrganizationUpdateDTO(BaseDTO):
      """Payload for updating an existing organization."""

      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

      name: Annotated[str | None, Field(default=None, description="Updated display name")] = None
      tier: Annotated[str | None, Field(default=None, description="Updated service tier")] = None
      is_active: Annotated[bool | None, Field(default=None, description="Updated active status")] = None
      contact_email: Annotated[str | None, Field(default=None, description="Updated contact email")] = None
      billing_id: Annotated[str | None, Field(default=None, description="Updated billing ID")] = None
      subscription_status: Annotated[LaxSubscriptionStatus | None, Field(default=None)] = None
      quota_limit: Annotated[float | None, Field(default=None, ge=0.0)] = None
      tpm_limit: Annotated[int | None, Field(default=None, ge=1000)] = None
      rpm_limit: Annotated[int | None, Field(default=None, ge=1)] = None
  ```

#### [MODIFY] [`backend_v2/models/domain/knowledge.py`](file:///c:/src/quorum/backend_v2/models/domain/knowledge.py#L25-L54)
- Add `ConceptCreateDTO`, `ReferenceCreateDTO`, and `ClaimCreateDTO`:
  ```python
  class ConceptCreateDTO(BaseDTO):
      """DTO for adding a concept to the knowledge base."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      id: Annotated[str | None, Field(default=None, description="Optional concept ID")] = None
      name: Annotated[str, Field(min_length=1, description="Concept name")]


  class ReferenceCreateDTO(BaseDTO):
      """DTO for adding a reference to the knowledge base."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      id: Annotated[str | None, Field(default=None, description="Optional reference ID")] = None
      name: Annotated[str, Field(min_length=1, description="Reference name")]


  class ClaimCreateDTO(BaseDTO):
      """DTO for adding a claim to the knowledge base."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      id: Annotated[str | None, Field(default=None, description="Optional claim ID")] = None
      name: Annotated[str, Field(min_length=1, description="Claim name")]
  ```

#### [MODIFY] [`backend_v2/models/dtos/system.py`](file:///c:/src/quorum/backend_v2/models/dtos/system.py#L1-L79)
- Add `SystemConfigUpdateDTO` and `SystemConfigCreateDTO`:
  ```python
  class SystemConfigUpdateDTO(BaseDTO):
      """DTO for updating system configuration entries."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      model_registry: Annotated[dict[str, Any] | None, Field(default=None)] = None
      mcp_gateways: Annotated[dict[str, Any] | None, Field(default=None)] = None
      performative_lexicons: Annotated[dict[str, Any] | None, Field(default=None)] = None
      system_settings: Annotated[dict[str, Any] | None, Field(default=None)] = None


  class SystemConfigCreateDTO(BaseDTO):
      """DTO for creating a new system configuration record."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      id: Annotated[str, Field(min_length=1)]
      category: Annotated[str, Field(min_length=1)]
      content: Annotated[dict[str, Any], Field(default_factory=dict)]
  ```

#### [MODIFY] [`backend_v2/models/domain/base.py`](file:///c:/src/quorum/backend_v2/models/domain/base.py#L1-L60)
- Add `AuditLogCreateDTO`, `UsageAggregateUpdateDTO`, `UsageAggregateDTO`, and `DetailedUsageDTO`:
  ```python
  class AuditLogCreateDTO(BaseDTO):
      """DTO for creating an audit log entry."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      id: Annotated[str | None, Field(default=None)] = None
      organization_id: Annotated[str | None, Field(default=None)] = None
      actor_id: Annotated[str, Field(min_length=1)]
      action: Annotated[str, Field(min_length=1)]
      resource_type: Annotated[str, Field(min_length=1)]
      resource_id: Annotated[str | None, Field(default=None)] = None
      details: Annotated[dict[str, Any] | None, Field(default=None)] = None
      timestamp: Annotated[datetime | str | None, Field(default=None)] = None


  class UsageAggregateUpdateDTO(BaseDTO):
      """DTO for upserting usage aggregations."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      total_tokens: Annotated[int, Field(ge=0)]
      total_cost_usd: Annotated[float, Field(ge=0.0)]
      execution_count: Annotated[int, Field(ge=0)]


  class UsageAggregateDTO(BaseDTO):
      """DTO representing aggregated usage statistics."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      scope: Annotated[str, Field(min_length=1)]
      entity_id: Annotated[str | None, Field(default=None)]
      period: Annotated[str, Field(min_length=1)]
      total_tokens: Annotated[int, Field(ge=0)]
      total_cost_usd: Annotated[float, Field(ge=0.0)]
      execution_count: Annotated[int, Field(ge=0)]


  class DetailedUsageDTO(BaseDTO):
      """DTO representing detailed usage reporting."""
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      records: Annotated[list[UsageRecord], Field(default_factory=list)]
      aggregate: Annotated[UsageAggregateDTO | None, Field(default=None)]
  ```

---

### Core Registry & Generics Modernization (`backend_v2/core/`)

#### [MODIFY] [`backend_v2/core/hook_registry.py`](file:///c:/src/quorum/backend_v2/core/hook_registry.py#L1-L141)
- Reconstitute `ISearchClient.search` signature to return `TavilySearchResultDTO` (from `backend_v2.models.dtos.retrieval`) instead of `list[dict[str, Any]]`.
- Replace legacy `F = TypeVar("F", bound=HookFunction)` with PEP 695 generic method syntax:
  ```python
  def register[F: HookFunction](self, name: str) -> Callable[[F], F]:
      """Decorator to register a function in the hook registry."""
  ```
- Remove `TypeVar` from `from typing import ...` imports.
- Update header docstring to present-tense Pydantic V2 state delta terminology.

---

### Database Protocols & Interfaces (`backend_v2/database/`)

#### [MODIFY] [`backend_v2/database/interfaces.py`](file:///c:/src/quorum/backend_v2/database/interfaces.py#L1-L261)
- **ALL 15 Protocols reconstituted to 100% Pydantic V2 Domain Models & DTOs (0 `dict[str, Any]` remaining)**:
  1. `IExecutionRepository`:
     - `create_execution(self, execution_data: ExecutionCreateDTO | ExecutionRecord) -> str`
     - `update_execution(self, execution_id: str, updates: ExecutionUpdateDTO | ExecutionRecord) -> bool`
     - `append_trace_event(self, execution_id: str, event_data: TraceEvent | ErrorTraceEvent | TombstoneEvent) -> bool`
     - `get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None`
     - `get_all_executions(self, organization_id: str | None = None, user_id: str | None = None) -> list[ExecutionRecord]`
     - `get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]`
  2. `IWorkflowRepository`:
     - `create_workflow(self, workflow_data: WorkflowCreateDTO | Workflow) -> str`
     - `update_workflow(self, workflow_id: str, updates: WorkflowUpdateDTO | Workflow) -> str`
     - `update_workflow_definition(self, workflow_id: str, definition_data: WorkflowUpdateDTO | Workflow) -> str`
     - `create_step(self, step_data: StepCreateDTO | Step) -> str`
     - `update_step(self, step_id: str, updates: StepUpdateDTO | Step) -> str`
     - `get_workflow_definition(self, workflow_id: str) -> Workflow | None`
     - `get_workflow(self, workflow_id: str) -> Workflow | None`
     - `get_all_workflows(self, organization_id: str | None = None, role: str | None = None) -> list[Workflow]`
     - `get_all_steps(self) -> list[Step]`
     - `get_step_by_id(self, step_id: str) -> Step | None`
  3. `IIdentityRepository`:
     - `list_organizations(self) -> list[Organization]`
     - `get_organization(self, org_id: str) -> Organization | None`
     - `create_organization(self, org_data: OrganizationCreate | Organization) -> str`
     - `update_organization(self, org_id: str, updates: OrganizationUpdateDTO | Organization) -> bool`
     - `list_users(self, org_id: str | None = None) -> list[User]`
     - `get_user(self, user_id: str) -> User | None`
     - `get_user_by_email(self, email: str) -> User | None`
     - `create_user(self, user_data: UserCreate | User) -> str`
     - `update_user(self, user_id: str, updates: UserUpdate | User) -> bool`
  4. `IComponentRepository`:
     - `get_all_components(self, type: str | None = None, exclude_types: list[str] | None = None) -> list[PromptBlock]`
     - `get_component_by_id(self, component_id: str) -> PromptBlock | None`
     - `get_component_by_name(self, name: str) -> PromptBlock | None`
     - `register_component(self, component_data: PromptBlock) -> str`
     - `create_component(self, component_data: PromptBlock) -> str`
     - `update_component(self, component_id: str, updates: PromptBlock) -> str`
     - `get_components_using_dimension(self, dimension_id: str) -> list[str]`
  5. `IPromptBlockRepository`:
     - `get_prompt_block_by_id(self, block_id: str) -> PromptBlock | None`
     - `get_all_prompt_blocks(self) -> list[PromptBlock]`
     - `get_prompt_blocks_by_ids(self, block_ids: list[str], strict: bool = True) -> list[PromptBlock]`
     - `create_prompt_block(self, block_data: PromptBlock) -> str`
     - `update_prompt_block(self, block_id: str, updates: PromptBlock) -> bool`
  6. `IAgentRepository`:
     - `get_agent_by_id(self, agent_id: str) -> PromptBlock | None`
     - `get_all_agents(self) -> list[PromptBlock]`
     - `create_agent(self, agent_data: PromptBlock) -> str`
     - `update_agent(self, agent_id: str, updates: PromptBlock) -> bool`
  7. `ITaskBlueprintRepository`:
     - `get_task_blueprint_by_id(self, blueprint_id: str) -> Step | None`
     - `get_all_task_blueprints(self) -> list[Step]`
     - `create_task_blueprint(self, blueprint_data: Step) -> str`
     - `update_task_blueprint(self, blueprint_id: str, updates: StepUpdateDTO | Step) -> bool`
  8. `IOutputProfileRepository`:
     - `get_all_output_profiles(self) -> list[OutputProfile]`
     - `get_output_profile_by_id(self, profile_id: str) -> OutputProfile | None`
     - `create_output_profile(self, profile_data: OutputProfile) -> str`
     - `update_output_profile(self, profile_id: str, updates: OutputProfile) -> bool`
  9. `IKnowledgeRepository`:
     - `get_banned_phrases(self) -> list[BannedPhrase]`
     - `add_banned_phrase(self, phrase: str, language: str = "en") -> None`
     - `get_prompt_template(self, template_id: str) -> PromptTemplateDTO | None`
     - `get_concepts(self) -> list[Concept]`
     - `get_references(self) -> list[Reference]`
     - `get_claims(self) -> list[Claim]`
     - `add_concept(self, item: ConceptCreateDTO | Concept) -> str`
     - `add_reference(self, item: ReferenceCreateDTO | Reference) -> str`
     - `add_claim(self, item: ClaimCreateDTO | Claim) -> str`
  10. `ISystemRepository`:
      - `get_model_registry(self) -> SystemConfigModelRegistry`
      - `update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool`
      - `get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways`
      - `update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool`
      - `get_system_settings(self) -> SystemConfig | None`
      - `update_system_settings(self, updates: SystemConfigUpdateDTO) -> bool`
      - `get_system_config(self, config_id: str) -> SystemConfig | None`
      - `create_system_config(self, config_data: SystemConfigCreateDTO | SystemConfig) -> str`
  11. `IAuditRepository`:
      - `log_audit_event(self, event_data: AuditLogCreateDTO | AuditLogEntry) -> None`
      - `get_audit_logs(self, organization_id: str | None = None, actor_id: str | None = None, action: str | None = None, limit: int = 100) -> list[AuditLogEntry]`
      - `log_usage(self, record: UsageRecord) -> None`
      - `get_usage_records(self, scope: str, entity_id: str | None = None, since: str | None = None) -> list[UsageRecord]`
      - `get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> UsageAggregateDTO | None`
      - `upsert_usage_aggregate(self, scope: str, entity_id: str | None, period: str, update_data: UsageAggregateUpdateDTO) -> None`
      - `get_detailed_usage(self, scope: str, target_id: str | None = None, since: str | None = None) -> DetailedUsageDTO`
  12. `IMatrixRepository`: All 4 methods accept & return `PromptBlock`.
  13. `IRoleRepository`: All methods accept & return `Role`.
  14. `IExecutionPersonaRepository`: All methods accept & return `PromptBlock`.
  15. `IExtractionProtocolRepository`: All methods accept & return `PromptBlock`.
  16. `IUnifiedWorkflowRepository`: Composite protocol inheriting from all 15 reconstituted protocols.

---

### Repository Implementations (`backend_v2/database/repositories/`)

#### [MODIFY] [`backend_v2/database/repositories/workflow.py`](file:///c:/src/quorum/backend_v2/database/repositories/workflow.py#L116-L255)
- Accept `WorkflowCreateDTO | Workflow` in `create_workflow` and `WorkflowUpdateDTO | Workflow` in `update_workflow`.
- Serialize input DTOs safely using `.model_dump(mode="json", exclude_unset=True)` before passing to storage driver.
- Accept `StepCreateDTO | Step` in `create_step` and `StepUpdateDTO | Step` in `update_step`.

#### [MODIFY] [`backend_v2/database/repositories/execution.py`](file:///c:/src/quorum/backend_v2/database/repositories/execution.py#L75-L155)
- Accept `TraceEvent | ErrorTraceEvent | TombstoneEvent` in `append_trace_event`.
- Reconstitute and offload trace events via `.model_dump(mode="json")`.
- Accept `ExecutionCreateDTO | ExecutionRecord` in `create_execution` and `ExecutionUpdateDTO | ExecutionRecord` in `update_execution`.
- Serialize input DTOs via `.model_dump(mode="json", exclude_unset=True)` before driver calls.

#### [MODIFY] [`backend_v2/database/repositories/identity.py`](file:///c:/src/quorum/backend_v2/database/repositories/identity.py#L1-L150)
- Accept `OrganizationCreate | Organization` in `create_organization` and `OrganizationUpdateDTO` in `update_organization`.
- Accept `UserCreate | User` in `create_user` and `UserUpdate | User` in `update_user`.
- Serialize input DTOs safely via `.model_dump(mode="json", exclude_unset=True)` before passing to storage driver.

#### [MODIFY] [`backend_v2/database/repositories/knowledge.py`](file:///c:/src/quorum/backend_v2/database/repositories/knowledge.py#L1-L150)
- Accept `ConceptCreateDTO | Concept` in `add_concept`, `ReferenceCreateDTO | Reference` in `add_reference`, `ClaimCreateDTO | Claim` in `add_claim`.
- Serialize input DTOs safely via `.model_dump(mode="json", exclude_unset=True)` before storage driver calls.

#### [MODIFY] [`backend_v2/database/repositories/system.py`](file:///c:/src/quorum/backend_v2/database/repositories/system.py#L1-L120)
- Accept `SystemConfigModelRegistry` in `update_model_registry` and `SystemConfigMCPGateways` in `update_mcp_gateways`.
- Serialize input models via `.model_dump(mode="json", exclude_unset=True)` before storage driver calls.

#### [MODIFY] [`backend_v2/database/repositories/audit.py`](file:///c:/src/quorum/backend_v2/database/repositories/audit.py#L1-L150)
- Accept `AuditLogCreateDTO | AuditLogEntry` in `log_audit_event` and `UsageAggregateUpdateDTO` in `upsert_usage_aggregate`.
- Accept `UsageRecord` in `log_usage`.

#### [MODIFY] [`backend_v2/database/repositories/component.py`](file:///c:/src/quorum/backend_v2/database/repositories/component.py#L16-L159)
- Reconstitute all component queries (`get_all_components`, `get_component_by_id`, `get_component_by_name`) into strictly typed `PromptBlock` models using `PromptBlockAdapter.validate_python(doc, strict=False)`.
- Reconstitute filtering logic in `get_all_components()`: `[c for c in validated_blocks if c.type not in exclude_types and c.type.value not in exclude_types]`.
- Reconstitute `get_components_using_dimension()`: iterate typed `PromptBlock.content.criteria` using dot-notation (`if crit.dimension_id == dimension_id`), eradicating all cascading `.get()` chains and duct-tape `try-except` blocks.
- Accept typed `PromptBlock` in `register_component()`, `create_component()`, and `update_component()`.

#### [MODIFY] [`backend_v2/database/repositories/components/matrix.py`](file:///c:/src/quorum/backend_v2/database/repositories/components/matrix.py#L16-L107)
- Reconstitute queries in `get_all_matrices()` and `get_matrix_by_id()` into validated `PromptBlock` models.
- Reconstitute `get_matrices_using_dimension()`: iterate typed `PromptBlock.content.criteria` using dot-notation, eradicating all `.get()` chains and `try-except` blocks.
- Accept typed `PromptBlock` in `create_matrix()` and `update_matrix()`.

#### [MODIFY] [`backend_v2/database/repositories/components/output_profile.py`](file:///c:/src/quorum/backend_v2/database/repositories/components/output_profile.py#L1-L100)
- Accept typed `OutputProfile` in `create_output_profile()` and `update_output_profile()`.

#### [MODIFY] [`backend_v2/database/repositories/components/task_blueprint.py`](file:///c:/src/quorum/backend_v2/database/repositories/components/task_blueprint.py#L1-L80)
- Accept typed `Step` in `create_task_blueprint()` and `StepUpdateDTO | Step` in `update_task_blueprint()`.

#### [MODIFY] [`backend_v2/database/repositories/components/role.py`](file:///c:/src/quorum/backend_v2/database/repositories/components/role.py#L1-L80)
- Accept typed `Role` in `create_role()` and `update_role()`.

---

### Utility Cleanups & Eradication (`backend_v2/utils/` & `backend_v2/`)

#### [DELETE] [`backend_v2/utils/dict_utils.py`](file:///c:/src/quorum/backend_v2/utils/dict_utils.py) & [`backend_v2/tests/unit/test_dict_utils.py`](file:///c:/src/quorum/backend_v2/tests/unit/test_dict_utils.py)
- Eradicate `dict_utils.py` entirely from the repository.
- Move pure `resolve_dot_notation()` utility into `@[backend_v2/utils/math_utils.py]` and update `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`.
- Relocate `deep_merge_dicts()` as a private `_deep_merge()` function inside `@[backend_v2/services/orchestrator/strategies/base.py]` for dynamic inputs blackboard reduction, while all domain-level state mutations enforce canonical Pydantic V2 `.model_copy(update=...)` and typed DTOs.

#### [MODIFY] [`backend_v2/exceptions.py`](file:///c:/src/quorum/backend_v2/exceptions.py#L365-L585)
- Reconstitute `error_code` property: eliminate `self.details.get("error_code")` fallback.
- Reconstitute validation error formatting: use typed `pydantic_core.ErrorDetails` direct key lookups (`err["loc"]`, `err["msg"]`) instead of `.get()`.
- Eliminate `getattr(exc, "title")` in favor of explicit `isinstance(exc, ValidationError)` handling.

#### [MODIFY] [`backend_v2/utils/finops_trace_analyzer.py`](file:///c:/src/quorum/backend_v2/utils/finops_trace_analyzer.py#L1-L178)
- Reconstitute state and telemetry records into strict Pydantic V2 `MonitorState` and `TelemetryRecord` models with `ConfigDict(strict=True, extra="forbid")`.
- Replace all 9 `.get()` calls with typed dot-notation.

#### [MODIFY] [`backend_v2/utils/alias_engine.py`](file:///c:/src/quorum/backend_v2/utils/alias_engine.py#L1-L338)
- **Pre-Validation Boundary Exemption**: Retain `alias_engine.py` in `BOUNDARY_EXEMPTION_FILES` as a legitimate LLM pre-validation hydration boundary per `atom_aliasing_hydration_mandate`.
- **Model Hardening (`AliasManifest`)**: Add `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` to `AliasManifest` DTO for type-safe cross-boundary transport.
- **Type Signature Tightening**: Replace untyped `Any` in traversal methods (`hydrate_and_filter_aliases`) with typed `JsonNode` recursive type alias (`type JsonScalar = str | int | float | bool | None; type JsonNode = dict[str, Any] | list[Any] | JsonScalar`).
- **Two-Phase Parsing Target Architecture**: Document the roadmap pattern: (1) LLM produces `AliasedExtractionDTO` with short semantic aliases (`a0`, `doc1`), (2) `alias_engine` translates aliases to real opaque UUIDs (`tda_...`), (3) validated into domain `AtomResultDTO`/`PromptBlock` with zero ad-hoc dictionary manipulation.

---

### Service Layer Callers Migration (`backend_v2/services/`)

#### [MODIFY] [`backend_v2/services/progress.py`](file:///c:/src/quorum/backend_v2/services/progress.py#L120-L228)
- Replace raw dictionary payloads in `start()`, `update()`, `complete()`, and `fail()` with `ExecutionUpdateDTO(...)`:
  - `start()`: `ExecutionUpdateDTO(status=STATUS_STARTED, created_at=now_iso, updated_at=now_iso)`
  - `update()`: `ExecutionUpdateDTO(status=STATUS_RUNNING, current_step=current_step, current_step_name=current_step, progress=progress, updated_at=now_iso)`
  - `complete()`: `ExecutionUpdateDTO(status=STATUS_COMPLETED, completed_at=now_iso, updated_at=now_iso)`
  - `fail()`: `ExecutionUpdateDTO(status=STATUS_FAILED, error=error, completed_at=now_iso, updated_at=now_iso)`

#### [MODIFY] [`backend_v2/services/execution.py`](file:///c:/src/quorum/backend_v2/services/execution.py#L690-L1400)
- Migrate raw dictionary update calls to `ExecutionUpdateDTO(...)`:
  - L693: `ExecutionUpdateDTO(status=ExecutionStatus.RUNNING.value)`
  - L985, L1069: `ExecutionUpdateDTO(step_states=...)`
  - L1297: `ExecutionUpdateDTO(pdf_report_path=saved_path)`
  - L1397: `ExecutionUpdateDTO(...)`

#### [MODIFY] [`backend_v2/services/blueprint.py`](file:///c:/src/quorum/backend_v2/services/blueprint.py#L370)
- Migrate `update_execution` payload to `ExecutionUpdateDTO(profile_syntheses=...)`.

#### [MODIFY] [`backend_v2/services/orchestrator/dag_executor.py`](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py#L118)
- Migrate `update_execution` payload to `ExecutionUpdateDTO(...)`.

#### [MODIFY] [`backend_v2/services/orchestrator/strategies/llm.py`](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py#L912)
- Migrate `update_execution` payload to `ExecutionUpdateDTO(step_states=new_states_raw)`.

#### [MODIFY] [`backend_v2/services/auth.py`](file:///c:/src/quorum/backend_v2/services/auth.py#L85-L105)
- Pass typed `Organization` and `User` models to `IdentityRepository` methods instead of raw dict dumps.

---

### In-Memory Test Fakes Infrastructure (`backend_v2/tests/fakes/`)

#### [NEW] `backend_v2/tests/fakes/in_memory_repositories.py`
- Create in-memory protocol implementations storing models in stateful memory dictionaries:
  - `InMemoryWorkflowRepository(IWorkflowRepository)`: Stores `Workflow` and `Step` domain models; validates `WorkflowCreateDTO`/`WorkflowUpdateDTO`.
  - `InMemoryExecutionRepository(IExecutionRepository)`: Stores `ExecutionRecord` models and appends `TraceEvent` instances.
  - `InMemoryComponentRepository(IComponentRepository)`: Stores `PromptBlock` components and filters by type.
  - `InMemoryIdentityRepository(IIdentityRepository)`: Stores `Organization` and `User` models.
  - `InMemoryKnowledgeRepository(IKnowledgeRepository)`: Stores `Concept`, `Reference`, `Claim`, and `BannedPhrase` models.

#### [NEW] `backend_v2/tests/unit/fakes/test_in_memory_repositories.py`
- Comprehensive contract unit tests verifying that all in-memory fakes strictly adhere to `interfaces.py` protocols.

---

### AST Guardrails Lockdown & Rule Expansion (`scripts/`)

#### [MODIFY] [`scripts/_ast_guardrails.py`](file:///c:/src/quorum/scripts/_ast_guardrails.py#L82-L665)
- **`BOUNDARY_EXEMPTION_FILES` STRICT 5-DRIVER LOCKDOWN**:
  - Purge 6 non-driver files from `BOUNDARY_EXEMPTION_FILES`: `interfaces.py`, `driver.py`, `wrapper.py`, `exceptions.py`, `finops_trace_analyzer.py`, `dict_utils.py`.
  - Lock exemption set to ONLY 5 legitimate drivers: `tinydb_driver.py`, `firestore_driver.py`, `provider.py`, `logging_config.py`, `alias_engine.py` (LLM pre-validation hydration boundary).
  - Add `QGR013`: Ban `TypeVar()` instantiation (Severity: `WARNING`). Preventative rule — single current instance fixed in Step 2.
  - Add `QGR014`: Ban `AsyncMock` / `MagicMock` in `backend_v2/tests/unit/services/` (Severity: `WARNING`).
  - Add `QGR015`: Ban `TypeGuard` import / type annotation (Severity: `WARNING`). Preventative rule enforcing PEP 742 `TypeIs` (`pep742_typeis_over_typeguard`).

#### [MODIFY] [`backend_v2/tests/unit/scripts/test_ast_guardrails.py`](file:///c:/src/quorum/backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1-L100)
- Append unit tests for `QGR013`, `QGR014`, and `QGR015`. Verify purged files are no longer in `BOUNDARY_EXEMPTION_FILES`.

---

### Execution Protocol

<execution_protocol>
  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  </required_context_rules>

  <step id="0" name="Strategic Alignment Check & Baseline Verification">
    <action>Run `uv run python scripts/_ast_guardrails.py backend_v2/database/` to verify initial AST state.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/database/repositories/ -v` to ensure clean initial test baseline.</action>
    <constraint invariant="universal_quality_gate">Test baseline and quality gate must be 100% green.</constraint>
  </step>

  <step id="1" name="Implement Ingress & Update DTOs across All Domains with ISTQB Negative Tests">
    <action>Add `WorkflowUpdateDTO` and `StepUpdateDTO` to @[backend_v2/models/dtos/studio.py] with `ConfigDict(strict=True, extra="forbid")`.</action>
    <action>Add `ExecutionCreateDTO` and `ExecutionUpdateDTO` (with typed `metadata: ExecutionMetadata | None` SSOT) to @[backend_v2/models/dtos/trace.py].</action>
    <action>Add `OrganizationUpdateDTO` to @[backend_v2/models/auth.py].</action>
    <action>Add `ConceptCreateDTO`, `ReferenceCreateDTO`, `ClaimCreateDTO` to @[backend_v2/models/domain/knowledge.py].</action>
    <action>Add `SystemConfigUpdateDTO`, `SystemConfigCreateDTO` to @[backend_v2/models/dtos/system.py].</action>
    <action>Add `AuditLogCreateDTO`, `UsageAggregateUpdateDTO`, `UsageAggregateDTO`, `DetailedUsageDTO` to @[backend_v2/models/domain/base.py].</action>
    <action>Add ISTQB negative test cases verifying extra="forbid" rejection and boundary constraints across all new DTOs in @[backend_v2/tests/unit/models/].</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test`.</action>
    <constraint invariant="no_naked_dicts_in_state">Strict Pydantic V2 DTOs with extra='forbid'.</constraint>
  </step>

  <step id="2" name="Modernize Core Hook Registry (PEP 695 Generics & ISearchClient Typing)">
    <action>Refactor @[backend_v2/core/hook_registry.py] to use `def register[F: HookFunction](...)` and remove `TypeVar`.</action>
    <action>Reconstitute `ISearchClient.search()` in @[backend_v2/core/hook_registry.py] to return `TavilySearchResultDTO` instead of `list[dict[str, Any]]`.</action>
    <action>Update header docstring in `hook_registry.py` to modern present-tense Pydantic V2 state delta terminology.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/core/test_hook_registry.py -v`.</action>
    <constraint invariant="english_language_mandate">100% English docstrings in present tense.</constraint>
  </step>

  <step id="3" name="Reconstitute All 15 Database Interfaces (100% Protocol Typing across all methods)">
    <action>Update method signatures in @[backend_v2/database/interfaces.py] across ALL 15 protocols (`IExecutionRepository`, `IWorkflowRepository`, `IIdentityRepository`, `IComponentRepository`, `IPromptBlockRepository`, `IAgentRepository`, `ITaskBlueprintRepository`, `IOutputProfileRepository`, `IKnowledgeRepository`, `ISystemRepository`, `IAuditRepository`, `IMatrixRepository`, `IRoleRepository`, `IExecutionPersonaRepository`, `IExtractionProtocolRepository`), replacing all `dict[str, Any]` and `list[dict]` with typed Pydantic models & DTOs.</action>
    <action>Import required domain models (`PromptBlock`, `Role`, `Step`, `Workflow`, `ExecutionRecord`, `TraceEvent`, `Organization`, `User`, `AuditLogEntry`, `UsageRecord`, `OutputProfile`, `BannedPhrase`, `Concept`, `Reference`, `Claim`, `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `SystemConfig`) in `interfaces.py`.</action>
    <action>Run `uv run mypy --strict backend_v2/database/interfaces.py`.</action>
    <constraint invariant="repository_reconstitution_mandate">All 15 interfaces must declare typed domain models and DTOs.</constraint>
  </step>

  <step id="4a" name="Modernize Core Execution & Workflow Repositories & Migrate 12+ Service Callers">
    <action>Update @[backend_v2/database/repositories/workflow.py] to accept and validate `WorkflowCreateDTO`, `WorkflowUpdateDTO`, `StepCreateDTO`, `StepUpdateDTO`.</action>
    <action>Update @[backend_v2/database/repositories/execution.py] to accept typed `TraceEvent` models, `ExecutionCreateDTO`, and `ExecutionUpdateDTO`.</action>
    <action>Migrate update_execution callers across @[backend_v2/services/progress.py], @[backend_v2/services/execution.py], @[backend_v2/services/blueprint.py], @[backend_v2/services/orchestrator/dag_executor.py], and @[backend_v2/services/orchestrator/strategies/llm.py] to construct `ExecutionUpdateDTO`.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/execution.py backend_v2/database/repositories/workflow.py --test`.</action>
    <constraint invariant="service_layer_hydration_firewall">Zero dictionary leakage across core repository and service layers.</constraint>
  </step>

  <step id="4b" name="Modernize Component Repositories & Execution Service QGR012 Cleanup">
    <action>Update @[backend_v2/database/repositories/components/matrix.py] to reconstitute queries into `list[PromptBlock]`, accept typed `PromptBlock` in create/update, and refactor `get_matrices_using_dimension()` to 100% typed dot-notation (deleting `.get()` chains and `try-except` blocks).</action>
    <action>Update @[backend_v2/database/repositories/components/agent.py], @[backend_v2/database/repositories/components/execution_persona.py], and @[backend_v2/database/repositories/components/extraction_protocol.py] to return typed domain models.</action>
    <action>Update @[backend_v2/database/repositories/component.py] to reconstitute all component queries to typed `PromptBlock` models via `PromptBlockAdapter`, refactor filtering logic (`c.type not in exclude_types`) to typed model attributes, and refactor `get_components_using_dimension()` to 100% typed dot-notation.</action>
    <action>Clean up downstream @[backend_v2/services/execution.py#L856-L869] to consume already-reconstituted `list[PromptBlock]` without manual dict parsing.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/components/ --test`.</action>
    <constraint invariant="service_layer_hydration_firewall">Component repositories return strictly typed PromptBlock models.</constraint>
  </step>

  <step id="5" name="Modernize Identity, Knowledge, System, Audit & Authoring Repositories">
    <action>Update @[backend_v2/database/repositories/identity.py] to accept and return typed `Organization`, `User`, `OrganizationCreate`, `OrganizationUpdateDTO`, `UserCreate`, `UserUpdate`.</action>
    <action>Update @[backend_v2/database/repositories/knowledge.py] to accept and return typed `ConceptCreateDTO`, `ReferenceCreateDTO`, `ClaimCreateDTO`, `BannedPhrase`.</action>
    <action>Update @[backend_v2/database/repositories/system.py] to accept and return typed `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `SystemConfig`, `SystemConfigUpdateDTO`, `SystemConfigCreateDTO` across all 8 methods.</action>
    <action>Update @[backend_v2/database/repositories/audit.py] to accept and return typed `AuditLogCreateDTO`, `UsageAggregateUpdateDTO`, `UsageAggregateDTO`, `DetailedUsageDTO`, `UsageRecord` across all 7 methods.</action>
    <action>Update @[backend_v2/database/repositories/components/output_profile.py], @[backend_v2/database/repositories/components/task_blueprint.py], @[backend_v2/database/repositories/components/role.py] to accept and return typed models.</action>
    <action>Update service callers in @[backend_v2/services/auth.py] to pass typed models.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test`.</action>
    <constraint invariant="repository_reconstitution_mandate">All repositories accept and return strictly typed models.</constraint>
  </step>

  <step id="6" name="Delete dict_utils.py, Relocate resolve_dot_notation & Modernize exceptions, finops Utilities">
    <action>Move `resolve_dot_notation()` from `dict_utils.py` into `@[backend_v2/utils/math_utils.py]` and update `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]` imports.</action>
    <action>Relocate `deep_merge_dicts()` as a private `_deep_merge()` helper in `@[backend_v2/services/orchestrator/strategies/base.py]` for dynamic inputs blackboard reduction, while all domain-level state mutations enforce canonical Pydantic V2 `.model_copy(update=...)` and typed DTOs.</action>
    <action>Delete `@[backend_v2/utils/dict_utils.py]` and `@[backend_v2/tests/unit/test_dict_utils.py]`, and clean up `@[backend_v2/tests/unit/utils/test_dict_utils.py]` into `@[backend_v2/tests/unit/utils/test_math_utils.py]`.</action>
    <action>Refactor @[backend_v2/exceptions.py] to eliminate `.get()` and `getattr()` using typed `pydantic_core.ErrorDetails`.</action>
    <action>Refactor @[backend_v2/utils/finops_trace_analyzer.py] to use typed `MonitorState` and `TelemetryRecord` models with dot-notation.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/utils/ --test`.</action>
    <constraint invariant="no_naked_dicts_in_state">dict_utils completely purged from codebase.</constraint>
  </step>

  <step id="7" name="Build In-Memory Protocol Fakes Infrastructure">
    <action>Create `@[backend_v2/tests/fakes/in_memory_repositories.py]` implementing `IWorkflowRepository`, `IExecutionRepository`, `IComponentRepository`, `IIdentityRepository`, and `IKnowledgeRepository` with typed models.</action>
    <action>Create `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]` to verify protocol conformance with both positive and ISTQB negative partition tests.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py -v`.</action>
    <constraint invariant="deterministic_testing_delegation">Stateful in-memory fakes replacing AsyncMock stubs.</constraint>
  </step>

  <step id="8" name="Migrate Database Repository Unit Tests with ISTQB Negative Partitions">
    <action>Update unit tests in `backend_v2/tests/unit/database/repositories/` to assert typed return models and pass typed DTO parameters.</action>
    <action>Add ISTQB negative test partitions for repository invalid inputs and constraint violations.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/database/repositories/ -v`.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test`.</action>
    <constraint invariant="deterministic_testing_delegation">Test suite must achieve >90% coverage with zero failures.</constraint>
  </step>

  <step id="9" name="AST Guardrails Strict 5-Driver Lockdown & Rule Expansion (QGR013-QGR015)">
    <action>PURGE 6 non-driver files from `BOUNDARY_EXEMPTION_FILES` in @[scripts/_ast_guardrails.py#L82-L94], locking it strictly to `tinydb_driver.py`, `firestore_driver.py`, `provider.py`, `logging_config.py`, and `alias_engine.py`.</action>
    <action>Add `QGR013` (TypeVar ban), `QGR014` (AsyncMock ban), and `QGR015` (TypeGuard ban per PEP 742 `pep742_typeis_over_typeguard`) visitor rules to @[scripts/_ast_guardrails.py#L200-L665].</action>
    <action>Update @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L830] `test_ast_guardrails_allows_exempt_driver_annotations` to test `tinydb_driver.py` instead of purged `interfaces.py`.</action>
    <action>Append unit tests in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py] verifying QGR013, QGR014, and QGR015, and verifying purged files are no longer exempt.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v`.</action>
    <action>Run `uv run python scripts/_ast_guardrails.py backend_v2/` to mathematically verify 0 fatal violations.</action>
    <constraint invariant="ast_guardrail_mandate">All domain files pass 100% FATAL AST inspection without exemption.</constraint>
  </step>

  <step id="10" name="Global Backend Quality Gate & Verification">
    <action>Run full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.</action>
    <action>Run full AST codebase scan: `uv run python scripts/_ast_guardrails.py backend_v2/`.</action>
    <constraint invariant="universal_quality_gate">100% green tests, 0 Ruff errors, 0 MyPy strict errors, >90% coverage.</constraint>
  </step>
</execution_protocol>

---

## Verification Plan & Mathematical Immunity Safeguards

### 1. Mathematical AST Guardrails & Zero-Regression Verification
To mathematically guarantee that no permissive dictionaries, unchecked reflection, or unapproved exemptions can EVER exist in domain code or protocol definitions:

1. **AST Protocol & Domain Zero-Permissive Scan (`QGR012` FATAL)**:
   - **Mathematical Proof Anchor**: Verifies that `interfaces.py`, `exceptions.py`, `finops_trace_analyzer.py`, `driver.py`, `wrapper.py`, and `dict_utils.py` are purged from `BOUNDARY_EXEMPTION_FILES` and contain **EXACTLY 0** FATAL violations, while `alias_engine.py` is locked as the sole LLM pre-validation hydration boundary driver alongside the 4 physical SDK/storage drivers. Any unauthorized exemption or fatal violation triggers immediate exit code 1.

2. **AST Suppression Tamper-Proof Audit (`QGR000` FATAL Immunity Check)**:
   - Target: Entire `backend_v2/` codebase
   - Command: `uv run python scripts/_ast_guardrails.py backend_v2/`
   - **Mathematical Proof Anchor**: Ensures that no `# noqa` comment can suppress `QGR012` or `QGR001` without an explicit, validated `[REASON: ...]` explanation (minimum 10 characters, banned placeholder firewall). QGR000 itself is mathematically immune to suppression.

3. **Static MyPy Strict Invariant Gate**:
   - Target: `backend_v2/database/interfaces.py`, `backend_v2/core/hook_registry.py`, `backend_v2/database/repositories/`, `backend_v2/utils/`
   - Command: `uv run mypy --strict backend_v2/`
   - **Mathematical Proof Anchor**: Zero untyped definitions, zero dynamic `Any` propagation, 100% adherence to generic PEP 695 method types and Pydantic V2 signatures.

4. **In-Memory Protocol Fakes Full Contract Coverage**:
   - Target: `backend_v2/tests/unit/fakes/test_in_memory_repositories.py`
   - Command: `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py -v`
   - **Mathematical Proof Anchor**: Direct runtime verification that every single method of all 15 protocols can be executed using purely Pydantic V2 DTOs and Domain Models with zero dictionary conversions.

5. **Global Multi-Tool Quality Audit Gate**:
   - Command: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
   - **Mathematical Proof Anchor**: Concurrently runs Ruff (formatting/linter), MyPy Strict (type checking), AST Guardrails (architectural invariants), and Pytest (>90% statement coverage).

---

### 2. Safeguards Against Circumvention ("Why Circumvention Is Mathematically Impossible")

| Bypass Vector / Risk | Prevention & Mathematical Lock | Enforcing Mechanism |
| :--- | :--- | :--- |
| **Silent Exemption Addition** | Adding files back to `BOUNDARY_EXEMPTION_FILES` | AST unit test `test_ast_guardrails.py` explicitly asserts purged files are NOT in `BOUNDARY_EXEMPTION_FILES`. |
| **Lazy `# noqa` Suppression** | Inserting `# noqa` comments to bypass type checks | `QGR000` enforces non-empty substantive `[REASON: ...]` blocks and fails CI build if reason is trivial/placeholder. |
| **Implicit `Any` / Untyped Dictionaries** | Omitting type hints or using `dict` without types | `QGR012` scans AST nodes for `ast.Dict`, `ast.Subscript` with `dict`, and `mypy --strict` fails on missing annotations. |
| **Dynamic `getattr`/`hasattr` Fallbacks** | Using reflection to read missing dictionary keys | `QGR001` bans `getattr`, `hasattr`, `setattr`, and `object.__setattr__` with FATAL severity in all non-exempt files. |
| **Runtime Dict Leaks in Repositories** | Drivers returning raw dictionaries to services | Service layer tests and in-memory fakes reject raw dicts and crash loudly (`ValidationError` / `AppException`). |
| **Legacy `TypeVar` Boilerplate** | Re-introducing old generic syntax | `QGR013` statically scans for `TypeVar()` calls and flags them for PEP 695 generic syntax replacement. |
| **Legacy `TypeGuard` Narrowing** | Using `TypeGuard` instead of PEP 742 `TypeIs` | `QGR015` bans `TypeGuard` imports and type hints across the entire codebase. |
| **Resurrection of `dict_utils`** | Re-creating `deep_merge_dicts` or dict helpers | `QGR012` bans dict pattern matching and `isinstance(..., dict)`; PR gates fail AST scan. |
