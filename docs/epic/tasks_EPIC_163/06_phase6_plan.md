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

# EPIC 163 - Phase 6: Stateful `InMemoryUnitOfWork` Migration for Worker Test Suites (`Census F = 0`) & Final E2E Verification Gate

## 1. Executive Summary & Architectural Directives

This phase replaces all 44 `patch("...UnifiedWorkflowRepository")` mocks across the 6 worker unit test files with stateful `InMemoryUnitOfWork` and `InMemoryUnifiedWorkflowRepository` fixtures (`deceptive_persistence_mocking_ban` and `hermetic_test_fixtures_mandate`), lowers `CURRENT_RESIDUAL_CEILINGS["f"]` from `44` to `0` in `@[scripts/audit_warning_baseline.py]`, and executes the full backend, frontend, parity, and live E2E verification gates.

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]` | Mocking `UnifiedWorkflowRepository` via 35 string-based `patch("...UnifiedWorkflowRepository")` calls across `test_worker.py` (18), `test_worker_synthesis.py` (16), and `test_worker_synthesis_accumulation.py` (1) (`Census F`). | Seed stateful `InMemoryUnitOfWork` and `InMemoryUnifiedWorkflowRepository` instances with Polyfactory domain models and assert persisted state transitions via subsequent `get_execution` / `get_workflow` roundtrip queries. | Zero `AsyncMock` repository return-value theater in `test_worker*.py`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_accumulation.py --test --ast-strict` |
| `@[backend_v2/tests/unit/workers/test_report_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`, `@[scripts/audit_warning_baseline.py]` | Mocking `UnifiedWorkflowRepository` via 9 string-based `patch("...UnifiedWorkflowRepository")` calls across `test_report_worker.py` (2), `test_synthesis_reducers.py` (3), and `test_synthesis_worker.py` (4) (`Census F = 44`). | Migrate `test_report_worker.py`, `test_synthesis_reducers.py`, and `test_synthesis_worker.py` to stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures and lock `CURRENT_RESIDUAL_CEILINGS["f"] = 0` in `@[scripts/audit_warning_baseline.py]`. | All 10 categories in `CURRENT_RESIDUAL_CEILINGS` equal `0` (`d=0, f=0, k=0, x=0, n=0, t=0, p=0, m=0, r=0, s=0`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_warning_baseline.py --verify-ceilings` |

---

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that all 44 `UnifiedWorkflowRepository` patches across the 6 worker test files are accounted for and that `InMemoryUnifiedWorkflowRepository.clear_faults()` is called in `try...finally` blocks whenever fault injection is tested (`scoped_mock_and_fault_isolation_mandate`).</action>
  </step>

  <dod_checklist>
    <item>Zero `patch("...UnifiedWorkflowRepository")` calls remain across `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`, `@[backend_v2/tests/unit/workers/test_report_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, and `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`.</item>
    <item>`CURRENT_RESIDUAL_CEILINGS["f"]` is updated from `44` to `0` in `@[scripts/audit_warning_baseline.py]` and `--verify-ceilings` passes with exit code 0.</item>
    <item>All global Backend, Frontend, Dict Eradication, Warning Baseline, DTO Parity, SDUI Parity, and Live E2E verification gates pass 100%.</item>
  </dod_checklist>

  <anti_targets>
    <file>@[backend_v2/seed/seed_data.json]</file>
    <file>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]</file>
  </anti_targets>

  <touched_artifacts>
    <file>@[backend_v2/tests/unit/test_worker.py]</file>
    <file>@[backend_v2/tests/unit/test_worker_synthesis.py]</file>
    <file>@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]</file>
    <file>@[backend_v2/tests/unit/workers/test_report_worker.py]</file>
    <file>@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]</file>
    <file>@[backend_v2/tests/unit/workers/test_synthesis_worker.py]</file>
    <file>@[scripts/audit_warning_baseline.py]</file>
  </touched_artifacts>

  <step id="6.1" name="Migrate test_worker.py, test_worker_synthesis.py &amp; test_worker_synthesis_accumulation.py to Stateful InMemoryUnifiedWorkflowRepository">
    <context>
      `@[backend_v2/tests/unit/test_worker.py]` (18 patches), `@[backend_v2/tests/unit/test_worker_synthesis.py]` (16 patches), and `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]` (1 patch) mock `UnifiedWorkflowRepository` via `unittest.mock.patch`.
    </context>
    <demolish>
      Delete all 35 `patch("...UnifiedWorkflowRepository")` calls and `AsyncMock` repository stubs across `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, and `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/tests/unit/test_worker.py]`: Replace 18 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures and verify persisted state via roundtrip `get_execution` / `get_workflow` calls.
      2. `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis.py]`: Replace 16 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures.
      3. `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`: Replace 1 `UnifiedWorkflowRepository` patch with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixture.
    </action>
    <constraint>
      Every persistence test must assert that stored and reconstituted records pass root Pydantic V2 validation (`preflight_schema_assertion_mandate`) and clean up any injected faults via `repo.clear_faults()` in `try...finally`.
    </constraint>
    <test_contracts>
      <contract name="test_worker_execution_persists_completed_record_in_memory_roundtrip" category="positive">
        <input>Seeded `Workflow`, `V2Step`, and `ExecutionRecord` in `InMemoryUnifiedWorkflowRepository` executed through worker entrypoint.</input>
        <expected>Subsequent `await repo.get_execution(execution_id)` returns the updated `ExecutionRecord` with `ExecutionStatus.COMPLETED`.</expected>
      </contract>
      <contract name="test_worker_handles_injected_repository_fault_and_clears_faults" category="negative">
        <input>Fault injected into `InMemoryUnifiedWorkflowRepository` during worker execution.</input>
        <expected>Worker routes failure deterministically and `repo.clear_faults()` restores clean state in `finally`.</expected>
      </contract>
      <contract name="test_worker_synthesis_accumulation_preserves_multi_profile_caches" category="boundary">
        <input>Sequential and parallel synthesis accumulation across 2 distinct `OutputProfile` IDs.</input>
        <expected>Roundtrip `get_execution` contains both `RenderedSynthesisCache` entries without overwrite loss.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_accumulation.py --test --ast-strict`
    </validation_gate>
  </step>

  <step id="6.2" name="Migrate test_report_worker.py, test_synthesis_reducers.py &amp; test_synthesis_worker.py and Lock Census F = 0">
    <context>
      `@[backend_v2/tests/unit/workers/test_report_worker.py]` (2 patches), `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]` (3 patches), and `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` (4 patches) contain the remaining 9 `UnifiedWorkflowRepository` patches tracked by `CURRENT_RESIDUAL_CEILINGS["f"]` in `@[scripts/audit_warning_baseline.py]`.
    </context>
    <demolish>
      Delete all 9 `patch("...UnifiedWorkflowRepository")` calls across the 3 `tests/unit/workers/` files and lower `CURRENT_RESIDUAL_CEILINGS["f"]` from `44` to `0` in `@[scripts/audit_warning_baseline.py]`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/tests/unit/workers/test_report_worker.py]`: Replace 2 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures.
      2. `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`: Replace 3 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures.
      3. `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`: Replace 4 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures.
      4. `[MODIFY]` `@[scripts/audit_warning_baseline.py]`: Update `CURRENT_RESIDUAL_CEILINGS["f"]` from `44` to `0` so all 10 categories (`d`, `f`, `k`, `x`, `n`, `t`, `p`, `m`, `r`, `s`) equal `0`.
    </action>
    <constraint>
      Verify `audit_warning_baseline.py --verify-ceilings` passes with `f = 0` and `CURRENT_WARNING_CEILING = 0`.
    </constraint>
    <test_contracts>
      <contract name="test_audit_warning_baseline_verify_ceilings_all_zero" category="positive">
        <input>Run `audit_warning_baseline.py --verify-ceilings` across the repository.</input>
        <expected>All 10 residual categories (`d`, `f`, `k`, `x`, `n`, `t`, `p`, `m`, `r`, `s`) equal `0` and exit code is `0`.</expected>
      </contract>
      <contract name="test_report_worker_fails_fast_when_execution_record_missing_in_memory" category="negative">
        <input>`InMemoryUnifiedWorkflowRepository` without the requested `execution_id`.</input>
        <expected>Raises or logs deterministic `ResourceNotFoundError` / `AppException` without `AsyncMock` stubs.</expected>
      </contract>
      <contract name="test_synthesis_reducers_atomic_persistence_roundtrip" category="boundary">
        <input>Concurrent profile synthesis updates persisted via `persist_profile_synthesis_atomic` against `InMemoryUnifiedWorkflowRepository`.</input>
        <expected>Roundtrip `get_execution` reflects all committed profile syntheses and step states accurately.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/workers/ scripts/audit_warning_baseline.py --test --ast-strict; uv run --no-sync --offline python scripts/audit_warning_baseline.py --verify-ceilings`
    </validation_gate>
  </step>

  <step id="6.3" name="Full-Stack Global Quality Gates &amp; Live E2E Verification">
    <context>
      Final completion gate verifying all 6 phases of EPIC 163 across Backend, Frontend, AST Guardrails, Dict Eradication, Warning Baseline, DTO Parity, SDUI Semantic Parity, and Live E2E LLM integration.
    </context>
    <action>
      Execute the complete suite of global verification commands and confirm 100% pass across `@[scripts/_ast_guardrails.py]`, `@[scripts/_dart_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, `@[scripts/audit_warning_baseline.py]`, `backend_v2/`, and `client_app_v2/`.
    </action>
    <constraint>
      Do not close EPIC 163 until every single command in `<validation_gate>` exits with code 0.
    </constraint>
    <test_contracts>
      <contract name="test_full_stack_epic_163_verification_gates_pass" category="positive">
        <input>Global backend audit loop, global Flutter audit loop, dict eradication audit, warning baseline audit, DTO parity audit, SDUI semantic parity suite, and live E2E integration suite.</input>
        <expected>100% pass with 0 errors and 0 warnings.</expected>
      </contract>
      <contract name="test_guardrail_unit_suites_reject_regressed_exemptions" category="negative">
        <input>Run `test_ast_guardrails.py`, `test_dart_guardrails.py`, and `test_audit_dict_eradication.py`.</input>
        <expected>Asserts zero `RESIDUAL_*` sets in `_ast_guardrails.py`, zero `per-file-ignores` in `pyproject.toml`, and exactly 9 transport files in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`.</expected>
      </contract>
      <contract name="test_sdui_and_dto_parity_across_python_and_flutter" category="boundary">
        <input>Run `audit_dto_parity.py` and `test_sdui_semantic_parity.py`.</input>
        <expected>1:1 field and type parity across all backend Pydantic V2 DTOs, Jinja PDF templates, and Flutter Freezed models.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/ --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dict_eradication.py; uv run --no-sync --offline python scripts/audit_warning_baseline.py --verify-ceilings; uv run --no-sync --offline python scripts/audit_dto_parity.py; uv run --no-sync --offline pytest backend_v2/tests/integration/test_sdui_semantic_parity.py; $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
    </validation_gate>
  </step>
</execution_protocol>
```
