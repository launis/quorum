# Tracker: Router SSOT Consolidation & Universal CRUD+Clone Enforcement (`reports.py`, `workflows.py`, `system_configs.py`)

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md] @[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]`
  - [x] Step 1: Remediate DGR008 and DGR009 Technical Debt in ReportsClient and MatricesMasterView, Fix System Health Prefix, and Demolish Dead System Configs Router
  - [x] Step 2: Consolidate Workflow Router SSOT, Upgrade All 5 Studio Blueprint Routers to Gold-Standard Parity, and Enforce Dynamic Matrix/Step Creation with 3-Layer Delete Protection
  - [x] Step 3: Consolidate ReportArtifact Router SSOT into Single APIRouter and Lock Universal CRUD+Clone Guardrails
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md] @[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] [DELETE] @[backend_v2/api/routers/studio/system_configs.py]
  - [x] @[backend_v2/api/routers/studio/__init__.py]
  - [x] @[backend_v2/api/routers/system/health.py]
  - [x] [DELETE] @[backend_v2/api/routers/execution/workflows.py]
  - [ ] @[backend_v2/api/routers/studio/workflows.py]
  - [ ] @[backend_v2/api/routers/studio/steps.py]
  - [ ] @[backend_v2/api/routers/studio/prompt_blocks.py]
  - [ ] @[backend_v2/database/repositories/components/prompt_block.py]
  - [ ] @[backend_v2/services/studio/prompt_block_service.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[backend_v2/services/studio/output_profile_service.py]
  - [ ] @[backend_v2/services/studio/system_config_service.py]
  - [ ] @[backend_v2/api/routers/studio/model_registry.py]
  - [ ] @[backend_v2/api/routers/studio/mcp_gateways.py]
  - [ ] @[backend_v2/api/routers/execution/reports.py]
  - [ ] @[backend_v2/api/routers/execution/executions.py]
  - [ ] @[backend_v2/api/routers/execution/__init__.py]
  - [ ] @[backend_v2/main.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/core/api/reports_client.dart]
  - [ ] @[client_app_v2/lib/core/api/workflow_client.dart]
  - [ ] @[client_app_v2/lib/core/api/studio_client.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/matrices_master_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md] @[ki_router_ssot_and_crud_clone_lifecycle.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_router_ssot_and_crud_clone_lifecycle.md]`: Synchronize router topology, 3-layer delete protection rules, dynamic matrix draft creation, and OPAQUE_STRIPE_ID_REGEX path bindings.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect single-entity router SSOT topology and deleted execution/workflows.py, studio/system_configs.py.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing consolidated router architecture in present tense.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md] @[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/target.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Remediate DGR008 substring slicing in `reports_client.dart` using RegExp replacement | Step 1 | [x] Completed |
| REQ-002 | Remediate DGR009 missing AppErrorBoundary in `matrices_master_view.dart` | Step 1 | [x] Completed |
| REQ-003 | Delete dead `studio/system_configs.py` router and obsolete unit tests | Step 1 | [x] Completed |
| REQ-004 | Remove duplicate `/system` prefix in `health.py` to fix `/hooks` route | Step 1 | [x] Completed |
| REQ-005 | Consolidate `Workflow` entity router SSOT: move `GET /{id}/ui_schema` to `studio/workflows.py`, delete `execution/workflows.py`, and update `workflow_client.dart` | Step 2 | [x] Completed |
| REQ-006 | Enforce `OPAQUE_STRIPE_ID_REGEX` path parameter validation and `ID_MISMATCH` check on `PUT /{id}` across all 5 older Studio blueprint routers | Step 2 | [x] Completed |
| REQ-007 | Support dynamic matrix draft creation via `category_id` query parameter in `prompt_blocks.py`, `prompt_block_service.py`, and Flutter Studio client | Step 2 | [x] Completed |
| REQ-008 | Unlock specialist steps on clone (`is_system_core=False`) in `workflow_service.py` while preserving informational `slug` | Step 2 | [x] Completed |
| REQ-009 | Enforce 3-layer delete protection across `prompt_block.py` repository, `prompt_block_service.py`, `workflow_service.py`, `output_profile_service.py`, and `system_config_service.py` | Step 2 | [x] Completed |
| REQ-010 | Consolidate `ReportArtifact` routes into single `APIRouter` in `reports.py` mounted once at `/api/v2`, eradicating `/api/v1` and shadow decorators | Step 3 | [x] Completed |
| REQ-011 | Expand `test_router_ssot_guardrails.py` to enforce universal CRUD + Clone parity across all 6 blueprint routers and reject shadow routes | Step 3 | [x] Completed |
| REQ-012 | Synchronize `04_directory_reference.md` with consolidated router topology | Step 3 | [x] Completed |

# Session Handover Context

## Achieved
- Step 1: Remediated DGR008 and DGR009 technical debt, fixed health router prefix, demolished dead system_configs router.
- Step 2: Consolidated Workflow router SSOT (`GET /{id}/ui_schema`), deleted `execution/workflows.py`, upgraded all 5 Studio routers with `OPAQUE_STRIPE_ID_REGEX` and `ID_MISMATCH` Fail-Fast validation, added dynamic matrix draft creation (`category_id=matrix`), unlocked specialist steps on clone (`is_system_core=False`), and enforced 3-layer delete protection across repositories and services.
- Step 3: Consolidated ReportArtifact routes onto a single `router = APIRouter(tags=["Reports"])` mounted once under `/api/v2` in `main.py`, eradicated `external_reports_router` and legacy `/api/v1` mounts, deleted all 10 shadow decorators and duplicate direct subrouter methods, expanded `test_router_ssot_guardrails.py` to verify universal CRUD + Clone lifecycle parity across all 6 blueprint routers (`workflows`, `steps`, `prompt-blocks`, `output-profiles`, `model-registry`, `mcp-gateways`) with strict `OPAQUE_STRIPE_ID_REGEX` parameter pattern validation, and synchronized `04_directory_reference.md`. All backend audit loops and AST guardrails pass 100%.

## Learned
- Single APIRouter mounting in `main.py` directly under `/api/v2` avoids duplicate subrouter mappings and guarantees predictable OpenAPI path generation.
- FastAPI OpenAPI schema generation includes parameter `schema.pattern` reflecting `Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)]`, providing a deterministic AST/OpenAPI gate.

## Remaining
- Post-Implementation Gates: Tier 2 Hardening (Backend/Frontend), Semantic Coverage Audit, and Tier 8 Plan Audit.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md] @[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]
```
