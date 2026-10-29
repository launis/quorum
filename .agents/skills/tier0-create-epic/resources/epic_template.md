<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# EPIC [NUM]: [Descriptive Title]

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> [Include when introducing major architectural shifts or external integrations; omit for internal refactors.]

## 1. Goal Description & Background (Objective & Problem Statement)

[High-level business objectives, problem statement, quantitative scope summary table, and strategic scope.]

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

| Symbol / File / Field | Current Location | Target Destination / Disposition |
| :--- | :--- | :--- |
| `[Symbol]` | `@[path/to/file.py#Lnn-mm]` | `[Moved to X / INTENTIONALLY DROPPED — Reason]` |

### Retained SSOT Invariants (`What We Will RETAIN`)

- [Preserved models, APIs, and interfaces validated by Red-Teaming.]

### 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[path/to/target.py]` | [Banned anti-pattern] | [Approved Pydantic V2 / Freezed / SSOT invariant] | [Pruned unnecessary abstraction] | [Exact unit test / quality gate command] |

### Producer-Consumer Integration Check

- **Producer:** [Service/Model producing the data]
- **Consumer:** [Service/UI/PDF consuming the data]

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Pre-Implementation Technical Debt Cleanups
- [Scoped Boy Scout cleanup of existing anti-patterns in touched target files before new logic.]

### Phase 2: Orchestration, Registry & Prompt Compiler Updates
- [Core backend domain and service implementation.]

### Phase 3: Frontend Flutter UI & Freezed DTO Synchronization
- [Cross-domain DTO parity and Flutter UI updates.]

### Phase 4: Verification & E2E Integration Gate
- [Unit, integration, and live E2E verification.]

## 4. Definition of Done (DoD) & Verification Plan

- **Definition of Done (DoD):** Explicit quality requirements.
- **Automated Unit Tests:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **AST Guardrails & Structural Tests:** Static AST tests enforcing new architectural rules.
- **MANDATORY Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.

