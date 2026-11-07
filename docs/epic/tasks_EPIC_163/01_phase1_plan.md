<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# Phase 1: Pre-Implementation Guardrail Hygiene (`QGR001`, `QGR002`), Audit Script `C901` Decomposition & `QGR030` Local Shadow-State Eradication

**Overview:** Eliminate `RESIDUAL_MISSING_DOCSTRING_FILES` (`QGR001`), `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` (`QGR002`), and `RESIDUAL_LOCAL_SHADOW_STATE_FILES` (`QGR030`) from `@[scripts/_ast_guardrails.py]`, and eliminate `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` and `[tool.ruff.lint.per-file-ignores]` from `@[scripts/audit_dict_eradication.py]` and `@[pyproject.toml]`. Specifically: (1) restore PEP 257 module, class, and function docstrings across `@[backend_v2/models/dtos/variance.py#L17-L38]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L27-L80]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L83-L168]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238]`, `@[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305]`, and `@[backend_v2/services/orchestrator/schema_factory.py#L39-L411]`; (2) add structured `logger.error` calls immediately preceding both `raise AppException(...)` statements in `setup_logging` (`@[backend_v2/logging_config.py#L138-L269]`); (3) decompose high-branching functions in `@[scripts/backend_audit_loop.py#run_audit_loop]` and `@[scripts/flutter_audit_loop.py#L107-L313]` so McCabe cyclomatic complexity is $\le 15$ with zero `per-file-ignores`; and (4) eradicate process-local dictionary shadow states (`self._local_invitations`, `self._local_assignments`, `self._memory_entries`) in `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`, and `@[backend_v2/services/cache/typed_cache.py#L111-L187]`, routing all persistence through `QuorumUnitOfWork` (`@[backend_v2/database/interfaces.py#L437-L477]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L1960-L2034]`, and `@[backend_v2/tests/fakes/in_memory_repositories.py#L1461-L2106]`) and `TypedCacheService`.

**Source:** `@[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]`

**Target Files:**
- `[MODIFY] @[backend_v2/models/dtos/variance.py#L17-L38]`
- `[MODIFY] @[backend_v2/services/orchestrator/extraction_schema_factory.py#L27-L80]`
- `[MODIFY] @[backend_v2/services/orchestrator/extraction_schema_factory.py#L83-L168]`
- `[MODIFY] @[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238]`
- `[MODIFY] @[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305]`
- `[MODIFY] @[backend_v2/services/orchestrator/schema_factory.py#L39-L411]`
- `[MODIFY] @[backend_v2/logging_config.py#L138-L269]`
- `[MODIFY] @[scripts/backend_audit_loop.py#run_audit_loop]`
- `[MODIFY] @[scripts/flutter_audit_loop.py#L107-L313]`
- `[MODIFY] @[pyproject.toml]`
- `[MODIFY] @[scripts/audit_dict_eradication.py]`
- `[MODIFY] @[backend_v2/services/auth/organization_service.py#L61-L1271]`
- `[MODIFY] @[backend_v2/services/execution/assignment_service.py#L123-L1610]`
- `[MODIFY] @[backend_v2/services/cache/typed_cache.py#L111-L187]`
- `[MODIFY] @[scripts/_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/dtos/variance.py#L17-L38]`**<br>**`@[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238]`**<br>**`@[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305]`**<br>**`@[backend_v2/services/orchestrator/schema_factory.py#L39-L411]`**<br>**`@[backend_v2/logging_config.py#L138-L269]`**<br>**`@[scripts/_ast_guardrails.py]`** | Exempting missing PEP 257 docstrings via `RESIDUAL_MISSING_DOCSTRING_FILES` (`QGR001`) and unlogged `AppException` raises in `setup_logging` via `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` (`QGR002`). | Place module docstrings at line 1 before `from __future__ import annotations`, complete all class and method Google-style docstrings, log `logger.error` with `ErrorCodes.CONFIGURATION_ERROR.name` before raising `AppException` in `setup_logging`, and delete `RESIDUAL_MISSING_DOCSTRING_FILES` and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` from `@[scripts/_ast_guardrails.py]`. | Zero transitional docstring or exception-logging exemption sets in `@[scripts/_ast_guardrails.py]`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/variance.py backend_v2/services/orchestrator/extraction_schema_factory.py backend_v2/services/orchestrator/rag_preflight_service.py backend_v2/services/orchestrator/schema_factory.py backend_v2/logging_config.py scripts/_ast_guardrails.py --test --ast-strict` |
| **`@[scripts/backend_audit_loop.py#run_audit_loop]`**<br>**`@[scripts/flutter_audit_loop.py#L107-L313]`**<br>**`@[scripts/audit_dict_eradication.py]`**<br>**`@[pyproject.toml]`** | Exempting `@[scripts/backend_audit_loop.py]` and `@[scripts/flutter_audit_loop.py]` from Ruff `C901` McCabe cyclomatic complexity via `[tool.ruff.lint.per-file-ignores]` and `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS`. | Extract single-responsibility stage and CLI helper functions so every function in `@[scripts/backend_audit_loop.py]` and `@[scripts/flutter_audit_loop.py]` achieves McCabe complexity $\le 15$, remove `[tool.ruff.lint.per-file-ignores]` from `@[pyproject.toml]`, and set `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS = frozenset()` in `@[scripts/audit_dict_eradication.py]`. | Zero per-file lint suppression overrides across the entire repository. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/backend_audit_loop.py scripts/flutter_audit_loop.py scripts/audit_dict_eradication.py --test --ast-strict` |
| **`@[backend_v2/services/auth/organization_service.py#L61-L1271]`**<br>**`@[backend_v2/services/execution/assignment_service.py#L123-L1610]`**<br>**`@[backend_v2/services/cache/typed_cache.py#L111-L187]`**<br>**`@[scripts/_ast_guardrails.py]`** | Process-local in-memory dictionary fallbacks (`self._local_invitations`, `self._local_assignments`, `self._memory_entries`) exempted under `RESIDUAL_LOCAL_SHADOW_STATE_FILES` (`QGR030`). | Route all invitation and assignment persistence exclusively through `entity_adapter` or `uow_factory` (`get_registered_uow_factory()` from `@[backend_v2/database/interfaces.py#L437-L477]`), route `MCPGatewayCache` exclusively through `TypedCacheService`, and delete `RESIDUAL_LOCAL_SHADOW_STATE_FILES` from `@[scripts/_ast_guardrails.py]`. | Zero dual-mode local dictionary fallback branches in `OrganizationService`, `ExecutionAssignmentService`, or `MCPGatewayCache`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/organization_service.py backend_v2/services/execution/assignment_service.py backend_v2/services/cache/typed_cache.py scripts/_ast_guardrails.py --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]`, `@[docs/epic/EPIC_163_audit_report.md]`, `@[scripts/_ast_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, `@[backend_v2/database/interfaces.py#L437-L477]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L1960-L2034]`, and `@[backend_v2/tests/fakes/in_memory_repositories.py#L1461-L2106]`.</action>
    <action>Look forward: Verify Step 1.1 eliminates `RESIDUAL_MISSING_DOCSTRING_FILES` (`QGR001`) and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` (`QGR002`), Step 1.2 decomposes `C901` complexity in `scripts/backend_audit_loop.py` and `scripts/flutter_audit_loop.py` and removes `[tool.ruff.lint.per-file-ignores]`, and Step 1.3 eliminates `self._local_invitations`, `self._local_assignments`, `self._memory_entries`, and `RESIDUAL_LOCAL_SHADOW_STATE_FILES` (`QGR030`).</action>
    <constraint invariant="zero_compromise_cutover_mandate">Services and caches MUST NOT maintain transitional process-local dictionary shadow states (`_local_*` or `_memory_*`).</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md] and @[docs/epic/EPIC_163_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/dtos/variance.py]</backend>
    <backend>@[backend_v2/services/orchestrator/extraction_schema_factory.py]</backend>
    <backend>@[backend_v2/services/orchestrator/rag_preflight_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/schema_factory.py]</backend>
    <backend>@[backend_v2/logging_config.py]</backend>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <backend>@[scripts/flutter_audit_loop.py]</backend>
    <backend>@[pyproject.toml]</backend>
    <backend>@[scripts/audit_dict_eradication.py]</backend>
    <backend>@[backend_v2/services/auth/organization_service.py]</backend>
    <backend>@[backend_v2/services/execution/assignment_service.py]</backend>
    <backend>@[backend_v2/services/cache/typed_cache.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py]</backend>
    <backend>@[backend_v2/tests/unit/test_organization_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_assignment_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`RESIDUAL_MISSING_DOCSTRING_FILES` and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` are deleted from `@[scripts/_ast_guardrails.py]`, with `@[backend_v2/models/dtos/variance.py#L17-L38]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238]`, `@[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305]`, `@[backend_v2/services/orchestrator/schema_factory.py#L39-L411]`, and `@[backend_v2/logging_config.py#L138-L269]` passing `QGR001` and `QGR002` with zero exemptions.</item>
    <item>`[tool.ruff.lint.per-file-ignores]` is removed from `@[pyproject.toml]`, `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` in `@[scripts/audit_dict_eradication.py]` is `frozenset()`, and `uv run ruff check scripts/ backend_v2/` passes with zero `C901` warnings.</item>
    <item>`RESIDUAL_LOCAL_SHADOW_STATE_FILES` is deleted from `@[scripts/_ast_guardrails.py]`, and `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`, and `@[backend_v2/services/cache/typed_cache.py#L111-L187]` contain zero `_local_*` or `_memory_*` shadow state dictionaries.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT add `# noqa: C901` or `# noqa: QGR` inline suppression comments to bypass complexity or AST guardrails (`the_zero_compromise_pledge`).</anti_target>
    <anti_target>Do NOT retain in-memory fallback dicts (`_local_invitations`, `_local_assignments`, `_memory_entries`) under any conditional flag (`zero_compromise_cutover_mandate`).</anti_target>
    <anti_target>Do NOT modify Flutter `.dart` files in Phase 1 (reserved for Phase 5).</anti_target>
  </anti_targets>

  <step id="1.1" name="PEP 257 Module/Class/Function Docstrings (QGR001) &amp; Dual-Reported AppException Logging (QGR002)">
    <action>In @[backend_v2/models/dtos/variance.py#L17-L38], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L27-L80], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L83-L168], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238], @[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305], and @[backend_v2/services/orchestrator/schema_factory.py#L39-L411], place the module docstring at line 1 prior to `from __future__ import annotations` so `ast.get_docstring(module_node)` resolves it, and ensure all classes and functions possess complete PEP 257 Google-style docstrings (`Attributes:`, `Args:`, `Returns:`, `Raises:` without `Raises: None`).</action>
    <action>In @[backend_v2/logging_config.py#L138-L269], add a structured `logging.getLogger(__name__).error(...)` call with `extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name}` immediately preceding the `raise AppException(...)` statement when `log_dir.mkdir(parents=True, exist_ok=True)` raises `OSError`, and ensure the `litellm` configuration `except` block logs `extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name}` before raising `AppException`.</action>
    <action>In @[scripts/_ast_guardrails.py] and @[backend_v2/tests/unit/scripts/test_ast_guardrails.py], delete `RESIDUAL_MISSING_DOCSTRING_FILES` and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` from `__all__`, module constants, and `QuorumGuardrailVisitor`, and update unit test assertions accordingly.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every `AppException` raised in `setup_logging` MUST be preceded by a structured `logger.error` call.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/variance.py backend_v2/services/orchestrator/extraction_schema_factory.py backend_v2/services/orchestrator/rag_preflight_service.py backend_v2/services/orchestrator/schema_factory.py backend_v2/logging_config.py scripts/_ast_guardrails.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict</audit_command>
  </step>

  <step id="1.2" name="Audit Script C901 McCabe Complexity Decomposition &amp; Per-File-Ignore Eradication">
    <action>In @[scripts/backend_audit_loop.py#run_audit_loop] and @[scripts/flutter_audit_loop.py#L107-L313], decompose high-branching stage orchestration and CLI entrypoint functions into focused single-responsibility helper functions so that every function in `@[scripts/backend_audit_loop.py]` and `@[scripts/flutter_audit_loop.py]` has a McCabe cyclomatic complexity $\le 15$.</action>
    <action>In @[pyproject.toml] and @[scripts/audit_dict_eradication.py], remove the `[tool.ruff.lint.per-file-ignores]` section from `@[pyproject.toml]` and set `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS: frozenset[str] = frozenset()` in `@[scripts/audit_dict_eradication.py]`.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py], @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py], and @[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py], synchronize unit tests with the decomposed helpers and empty `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` ledger.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero `[tool.ruff.lint.per-file-ignores]` entries are permitted in `pyproject.toml`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/backend_audit_loop.py scripts/flutter_audit_loop.py scripts/audit_dict_eradication.py backend_v2/tests/unit/scripts/test_audit_dict_eradication.py backend_v2/tests/unit/scripts/test_backend_audit_loop.py backend_v2/tests/unit/scripts/test_flutter_audit_loop.py --test --ast-strict</audit_command>
  </step>

  <step id="1.3" name="QGR030 Process-Local Shadow State Eradication in OrganizationService, ExecutionAssignmentService &amp; MCPGatewayCache">
    <action>In @[backend_v2/services/auth/organization_service.py#L61-L1271], add `uow_factory: UnitOfWorkFactory | None = None` to `OrganizationService.__init__` (importing `UnitOfWorkFactory` and `get_registered_uow_factory` from `@[backend_v2/database/interfaces.py#L437-L477]`), delete `self._local_invitations: dict[str, Invitation] = {}`, and update `_save_invitation`, `_get_invitation_by_id`, `_list_org_invitations`, and `_find_invitation_by_token_hash` to route exclusively through `self._entity_adapter` or `self._uow_factory` / `get_registered_uow_factory()`, raising `ConfigurationError` (`ErrorCodes.CONFIGURATION_ERROR`) Fail-Fast if neither is configured.</action>
    <action>In @[backend_v2/services/execution/assignment_service.py#L123-L1610], add `uow_factory: UnitOfWorkFactory | None = None` to `ExecutionAssignmentService.__init__` (importing `UnitOfWorkFactory` and `get_registered_uow_factory` from `@[backend_v2/database/interfaces.py#L437-L477]`), delete `self._local_assignments: dict[str, ExecutionAssignment] = {}`, and update `get_assignment_by_execution_id`, `_get_assignment_or_raise`, `_save_assignment`, `_list_all_assignments`, and `_find_assignment_by_token_hash` to route exclusively through `self._entity_adapter` or `self._uow_factory` / `get_registered_uow_factory()`, raising `ConfigurationError` (`ErrorCodes.CONFIGURATION_ERROR`) Fail-Fast if neither is configured.</action>
    <action>In @[backend_v2/services/cache/typed_cache.py#L111-L187], delete `self._memory_entries: dict[str, str] = {}` from `MCPGatewayCache.__init__`, `get_gateway`, `set_gateway`, and `invalidate`, routing all caching operations exclusively through `self.cache_service` (`TypedCacheService` backed by `RedisClientProtocol`).</action>
    <action>In @[scripts/_ast_guardrails.py], delete `RESIDUAL_LOCAL_SHADOW_STATE_FILES` from `__all__`, module constants, and `QuorumGuardrailVisitor`. In @[backend_v2/tests/unit/test_organization_service.py], @[backend_v2/tests/unit/services/execution/test_assignment_service.py], and @[backend_v2/tests/unit/scripts/test_ast_guardrails.py], wire `InMemoryUnitOfWork` (`@[backend_v2/tests/fakes/in_memory_uow.py#L1960-L2034]`) / `InMemoryEntityAdapter` fixtures and add negative tests verifying Fail-Fast `ConfigurationError` when persistence is unconfigured.</action>
    <constraint invariant="hermetic_test_fixtures_mandate">Unit tests for `OrganizationService` and `ExecutionAssignmentService` MUST verify stateful roundtrip persistence via `InMemoryUnitOfWork` / `InMemoryEntityAdapter`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/organization_service.py backend_v2/services/execution/assignment_service.py backend_v2/services/cache/typed_cache.py scripts/_ast_guardrails.py backend_v2/tests/unit/test_organization_service.py backend_v2/tests/unit/services/execution/test_assignment_service.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_qgr001_and_qgr002_pass_with_zero_residual_exemptions" category="positive">
      <input>Scan `variance.py`, `extraction_schema_factory.py`, `rag_preflight_service.py`, `schema_factory.py`, and `logging_config.py` with `scan_file_for_guardrails` after removing `RESIDUAL_MISSING_DOCSTRING_FILES` and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`</input>
      <expected>Returns 0 GuardrailViolation instances for QGR001 and QGR002</expected>
    </test>
    <test name="test_setup_logging_logs_error_before_raising_app_exception_on_mkdir_failure" category="negative">
      <input>`setup_logging` invoked when `Path.mkdir` raises `OSError("Permission denied")`</input>
      <expected>Logs structured `logger.error` with `ErrorCodes.CONFIGURATION_ERROR.name` and raises `AppException` with status_code=500</expected>
    </test>
    <test name="test_audit_dict_eradication_rejects_any_per_file_ignore_in_pyproject" category="negative">
      <input>`check_config_suppression_ratchet` evaluated when `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` is `frozenset()` and a `per-file-ignores` entry is injected</input>
      <expected>Flags unauthorized per-file-ignore violation immediately</expected>
    </test>
    <test name="test_organization_and_assignment_services_persist_roundtrip_via_uow" category="positive">
      <input>`OrganizationService.create_invitation` and `ExecutionAssignmentService.create_assignment` invoked with `InMemoryUnitOfWork`</input>
      <expected>Invitation and assignment records are persisted in `uow.entities` and retrieved via subsequent `list_invitations` and `get_execution_assignment` calls with zero `_local_*` attributes on the service instances</expected>
    </test>
    <test name="test_organization_and_assignment_services_fail_fast_when_uow_unconfigured" category="negative">
      <input>`OrganizationService` or `ExecutionAssignmentService` invoked with `entity_adapter=None` and `uow_factory=None` (and no registered default UoW factory)</input>
      <expected>Logs `ErrorCodes.CONFIGURATION_ERROR.name` and raises `ConfigurationError`</expected>
    </test>
    <test name="test_qgr030_flags_local_shadow_state_dict_on_service_as_fatal" category="boundary">
      <input>Service class assigning `self._local_invitations = {}` or `self._memory_entries = {}` scanned by `scan_source_code_for_guardrails`</input>
      <expected>Emits `GuardrailSeverity.FATAL` `QGR030` violation</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 1 quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/variance.py backend_v2/services/orchestrator/extraction_schema_factory.py backend_v2/services/orchestrator/rag_preflight_service.py backend_v2/services/orchestrator/schema_factory.py backend_v2/logging_config.py backend_v2/services/auth/organization_service.py backend_v2/services/execution/assignment_service.py backend_v2/services/cache/typed_cache.py scripts/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```

