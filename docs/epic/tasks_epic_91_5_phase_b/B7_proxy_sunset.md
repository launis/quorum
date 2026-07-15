# Epic 91.5 Phase B7: Proxy Sunset & Consumer Migration

## Objective
Finalize the "No Proxies" and "Delete, don't Deprecate" mandate by ensuring all temporary adapters, proxy methods, or deprecated structures introduced during the refactoring process are fully removed. Ensure all consumers use the direct SSOT endpoints.

## Context & Architectural Mandates
- **No Legacy Mandate:** Preserve zero backwards compatibility with old V1 structures. No fallback chains.
- **Strangler Fig Abandonment:** Codebase must not contain legacy proxies or adapters routing between V1 and V2.

## Target Files (Modify)
- Any files containing `@deprecated` proxies or adapter imports related to the DTO bridge.

## Proposed Changes
### 1. Codebase Search
- Execute a codebase-wide search for `@deprecated` annotations or mentions of legacy adapters mapping to the new `v2_core.ReportDataDTO`.
- Search for any lingering imports of old models that should have been deleted.

### 2. Consumer Refactoring & Proxy Sunset
- If any active code (consumers, routers, services) is found using a proxy or adapter, refactor it to directly use the SSOT Pydantic models.
- After updating consumers, DELETE the proxy functions or adapter classes entirely.

## Testing & Quality Gate Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to ensure the removal of proxies does not break the dependency graph or failing tests.

---

# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the following command:
`/tier5-resume --workflow=/tier2-execute --target="docs/epic/epic_91_5_phase_b_tracker.md, docs/epic/tasks_epic_91_5_phase_b/B7_proxy_sunset.md" --rules=".agents/rules/00-antigravity-core.md, .agents/rules/01-python-backend.md"`
