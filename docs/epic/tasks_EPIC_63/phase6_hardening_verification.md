# Phase 6: Quality Gates, Hardening & Full Verification

> **Source**: Epic 63 – Phase 6 (Laadunvarmistus, Hardening ja Auditoinnit / Hardening Verification)

---

## Objective

Execute the full backend audit loop with testing, Ruff linting, Ruff formatting, and strict MyPy type checking across ALL modified files. This is the final verification gate ensuring the entire Epic passes architectural compliance.

---

## Architectural Invariants (Injected from `.agents/rules/`)

| Rule ID | Rule | Enforcement |
|---|---|---|
| R2 (`strict_pydantic_v2_rust`) | `ExecutionCoreFields` uses `V2CoreBase`'s `ConfigDict(strict=True, extra="forbid")` | Verified by MyPy + tests |
| R18 (`rfc7807_dual_reporting_strict`) | Factory method errors → `AppException(error_code=ErrorCodes.XYZ)`, not `ValueError` | Verified by Ruff + tests |
| R24 (`python_314_modern_syntax`) | `X \| None`, not `Optional[X]`. PEP 695 generics. | Verified by Ruff |
| R55-59 (`pep257_google_style`) | All new classes, methods and functions have proper docstrings | Verified by Ruff D-rules |
| R73 (`no_inline_imports_unless_ml`) | All imports global except ML SDKs | Verified by Ruff |
| R80 (`pydantic_validation_bypass_ban`) | `.model_validate()`, not `dict(model)` | Verified by tests |
| R92 (`pydantic_mutation_optimization`) | `.model_copy(update={...})`, not dump-then-reconstruct | Verified by Ruff |

---

## Scoping

### TARGET Files (Audit)
All files modified or created across Phases 1-4:

1. **[NEW]** `backend_v2/models/execution_core.py`
2. **[MODIFY]** `backend_v2/models/v2_core.py`
3. **[MODIFY]** `backend_v2/models/state.py`
4. **[MODIFY]** `backend_v2/services/execution.py`
5. **[MODIFY]** `backend_v2/services/orchestrator/dag_executor.py`
6. **[MODIFY]** `backend_v2/tests/unit/test_v2_core_models.py`

### CONTEXT Files (Read-Only)
- `scripts/backend_audit_loop.py` — Unified audit script
- All existing test files that reference `ExecutionRecord` or `WorkflowState`

---

## Milestones

### Milestone 6.1: Full Backend Audit Loop (Source: Epic Phase 6, Toimenpide 1)

Execute the unified backend audit loop with testing enabled against ALL modified files:

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/execution_core.py backend_v2/models/v2_core.py backend_v2/models/state.py backend_v2/services/execution.py backend_v2/services/orchestrator/dag_executor.py --test
```

This command runs:
1. **Ruff lint** — Checks for code quality, import ordering, docstring compliance
2. **Ruff format** — Ensures consistent code formatting
3. **MyPy strict** — Type-checks all modified files for type safety
4. **Pytest** — Runs the full test suite with coverage

### Milestone 6.2: Hardening Compliance Verification (Source: Epic Phase 6, Toimenpide 2)

The executing agent MUST manually verify each hardening rule against the modified files:

| Rule | ID | File | Verification |
|---|---|---|---|
| Strict Pydantic V2 | R2 | `execution_core.py` | Inherits `V2CoreBase` → `ConfigDict(strict=True, extra="forbid")` |
| RFC 7807 Dual Reporting | R18 | `execution.py` | Factory's `ValidationError` → `AppException(VALIDATION_FAILED)` |
| Python 3.14 Syntax | R24 | All files | `X \| None` (not `Optional[X]`), no `TypeVar` |
| PEP 257 Docstrings | R55-59 | All new classes/functions | Google-style: Summary + Attributes/Args/Returns/Raises |
| No Inline Imports | R73 | All files | All imports at module top level |
| Pydantic Bypass Ban | R80 | All files | `.model_validate()`, not `dict(model)` |
| Mutation Optimization | R92 | All files | `.model_copy(update={...})` |

### Milestone 6.3: Existing Test Suite Regression Check (Source: Epic DoD §5)

Verify that ALL existing tests still pass, particularly tests that construct `ExecutionRecord` directly:

```powershell
uv run pytest backend_v2/tests/ -v --tb=short
```

Key test files to watch for regressions:
- `test_executions.py` — Direct `ExecutionRecord(...)` construction
- `test_pdf_generator.py` — Direct `ExecutionRecord(...)` construction
- `test_flattener.py` — Direct `ExecutionRecord(...)` construction
- `test_worker_synthesis.py` — Direct `ExecutionRecord(...)` construction
- `test_worker.py` — Direct `ExecutionRecord(...)` construction
- `test_execution_resumability.py` — `Mock(spec=ExecutionRecord)` usage
- `test_execution.py` — `Mock(spec=ExecutionRecord)` usage

---

## Documentation Update

### Final Documentation Tasks
Update `docs/architecture/02_domain_models.md` with:
1. The `ExecutionCoreFields` SSOT pattern and mermaid inheritance diagram
2. The `create_execution_record` factory pattern
3. The CI-level structural parity meta-test description
4. Updated field ownership table showing which fields live in `ExecutionCoreFields` vs child classes

---

## Testing & Quality Gate Plan

### Definition of Done Checklist (Source: Epic §5)

- [ ] **Zero Schema Redundancy**: All 5 core fields (`status`, `execution_trace`, `execution_trace_storage_path`, `context_variables`, `context_variables_storage_path`) are defined ONLY in `ExecutionCoreFields` (except `status` override in `ExecutionRecord`)
- [ ] **Automated CI Parity Check**: `test_strict_schema_parity_for_core_execution_fields` passes
- [ ] **Decoupled Architecture**: `WorkflowState` has no PDF/presentation dependencies. `ExecutionRecord` has no domain-logic methods
- [ ] **Clean-Slate Database**: `run_seed.py` completes without errors
- [ ] **Quality Gates Passed**: Full audit loop passes cleanly:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/ --test
  ```

---

## Session Handover

```
To execute this plan, start a NEW chat session and run:
/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_63\phase6_hardening_verification.md]
```
