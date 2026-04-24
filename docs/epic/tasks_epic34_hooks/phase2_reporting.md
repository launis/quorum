# Phase 2: Cleansing `reporting.py` (Schema-First Templating)

## 1. Description and Objective
**Epic 34: Global Hooks Zero-Compromise Hardening.**
The `generate_report_hook` currently scavenges through `global_context_vars` using `isinstance(out, dict)` and `.get()` chains to guess if an agent was present. This silent fallback behavior violates the Zero-Compromise pledge. The goal is to enforce strict Pydantic parsing using a `ReportSynthesisDTO`.

## 2. File Scoping
- **TARGET (Modify):** 
  - `backend_v2/hooks/reporting.py`
- **CONTEXT (Read-Only):** 
  - `backend_v2/models/dtos/report.py` (or similar new DTO model if necessary)

## 3. Implementation Steps
1. **Define DTO:** Introduce a `ReportSynthesisDTO` that requires strict typed classes for every supported specialist report (e.g. `PerformativityReport`, `LogicianReport`). 
2. **Remove Dictionary Hunting:** Delete `_get_agent_output`, `isinstance(overseer_out, dict)`, and arbitrary `dict.get()` chaining inside `generate_report_hook`.
3. **Enforce Parsing:** The hook must do a single `ReportSynthesisDTO.model_validate(global_context_vars)` sweep.
4. **Jinja Integration:** If validation succeeds, pass the validated DTO directly into Jinja2 templates, ensuring deterministic template rendering.

## 4. Verification & Quality Gate Plan
- **Unit Testing:** 
  - *Fail-Fast Safety Tests:* Write specific tests that feed missing or corrupted Pydantic metadata/specialists to the orchestrator to verify it immediately crashes with a validation error (`AppException` or `ValidationError`) instead of a silent KeyError or null fallback.
  - *Pure Function Isolation:* Test DTO instantiation directly.
- **Audit Loop Execution:** `uv run python scripts/backend_audit_loop.py backend_v2/hooks/reporting.py --test` (Make sure to specifically test missing specialists trigger DTO validation failures).
