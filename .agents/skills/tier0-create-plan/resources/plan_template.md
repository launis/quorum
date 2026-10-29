<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: [Descriptive Title]

## 1. Objective & Architectural Background

[Detailed technical objective, root cause analysis, and architectural context.]

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[path/to/context_file.py]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[NEW] @[path/to/new_file.py]` | [Banned anti-pattern] | [Approved Pydantic V2 / Freezed / SSOT invariant] | [Pruned unnecessary abstraction] | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py path/to/new_file.py --test --ast-strict` |

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

1. **[Debt Item 1]:** [Description of existing anti-pattern in touched scope to be resolved before feature logic.]

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1: [Step Title]">
    <constraint invariant="strict_pydantic_v2_rust">[Specific architectural invariant constraint]</constraint>
    <constraint invariant="anti_happy_path_mandate">[Specific ISTQB negative testing constraint]</constraint>
    <action>[Actionable, deterministic instruction referencing exact target files]</action>
  </step>
</execution_protocol>
```

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path):** [Concrete input -> expected output]
- **Scenario 2 (Negative Path 1 - Missing/Invalid Input):** [Concrete invalid input -> expected AppException / ValidationError]
- **Scenario 3 (Negative Path 2 - Boundary Value Violation):** [Boundary min-1 / max+1 input -> expected rejection]

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Global Backend Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

