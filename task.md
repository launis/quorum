# Task Tracker: Output Profile Clone 404 Route Fix & Router Hardening

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

Bug Fix Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\73f27b73-80fb-4396-b14b-b559e2242c3c\bug_fix_plan.md]

## Execution Tasks

- [x] **Step 1: Router Hardening & Output Profile Clone Implementation (`output_profiles.py`)**
  - [x] Import `Path` and `OPAQUE_STRIPE_ID_REGEX` in `@[backend_v2/api/routers/output_profiles.py]`
  - [x] Enforce `profile_id: str = Path(..., pattern=OPAQUE_STRIPE_ID_REGEX)` on all path endpoints
  - [x] Add explicit `status_code=status.HTTP_201_CREATED` on `create_output_profile`
  - [x] Clean up dict mutation anti-pattern and add `ID_MISMATCH` check in `upsert_output_profile`
  - [x] Implement `@router.post("/{profile_id}/clone")` with `OutputProfileResponseDTO` and `status.HTTP_201_CREATED`

- [x] **Step 2: Elimination of the Phantom Router (`backend_v2/api/routers/studio/output_profiles.py`)**
  - [x] Remove `output_profiles` router import and mount from `@[backend_v2/api/routers/studio/__init__.py]`
  - [x] Delete phantom router file `@[backend_v2/api/routers/studio/output_profiles.py]`
  - [x] Delete phantom router tests `@[backend_v2/tests/unit/api/routers/studio/test_output_profiles.py]`

- [x] **Step 3: Rules & Knowledge Base Lockdown (Never Duplicate Routers)**
  - [x] Add `single_router_ssot_mandate` to `@[.agents/rules/01-python-backend.md]`
  - [x] Update `@[.agents/rules/04_directory_reference.md]` router laws
  - [x] Create Knowledge Item `@[ki_api_router_ssot_governance.md]` in `<appDataDir>\knowledge\api_router_ssot_governance\`

- [x] **Step 4: Router SSOT AST Guardrail & Comprehensive Unit Testing**
  - [x] Create `@[backend_v2/tests/unit/api/test_router_ssot_guardrails.py]` asserting no duplicate entity routers or shadow prefixes in OpenAPI schema
  - [x] Update `@[backend_v2/tests/unit/test_api_clone_endpoints.py]` to assert `/api/v2/output-profiles/{id}/clone`
  - [x] Create `@[backend_v2/tests/unit/api/routers/test_output_profiles.py]` with 13 ISTQB test cases (CRUD + clone, 200, 201, 204, 400, 404, 422)

- [x] **Step 5: Quality Gate Verification**
  - [x] Run `uv run pytest backend_v2/tests/unit/test_api_clone_endpoints.py` (7 passed)
  - [x] Run `uv run pytest backend_v2/tests/unit/api/routers/test_output_profiles.py` (13 passed, 100% coverage, 0 deprecation warnings)
  - [x] Run `uv run pytest backend_v2/tests/unit/api/test_router_ssot_guardrails.py` (3 passed, clean AST guardrail check)
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/output_profiles.py --test` (100% PASS, exit code 0)
  - [x] Run full pytest suite across all 3 test files (23 passed, exit code 0)

## # Session Handover Context
- **Achieved:**
  1. Implemented deep cloning `POST /{profile_id}/clone`, `Path(..., pattern=OPAQUE_STRIPE_ID_REGEX)` validation, and typed `ID_MISMATCH` validation in SSOT router `@[backend_v2/api/routers/output_profiles.py]`.
  2. Eliminated phantom router `backend_v2/api/routers/studio/output_profiles.py` and unmounted it from `backend_v2/api/routers/studio/__init__.py`.
  3. Hardcoded `single_router_ssot_mandate` in `@[.agents/rules/01-python-backend.md]` and directory reference in `@[.agents/rules/04_directory_reference.md]`.
  4. Established Knowledge Item `api_router_ssot_governance` with `metadata.json` and `artifacts/ki_api_router_ssot_governance.md`.
  5. Implemented automated route guardrail `@[backend_v2/tests/unit/api/test_router_ssot_guardrails.py]` and 13 comprehensive unit tests in `@[backend_v2/tests/unit/api/routers/test_output_profiles.py]`.
  6. Verified 100% passing Universal Quality Gate with exit code 0 (100% coverage on router, zero ruff/mypy/AST warnings).
- **Learned:**
  - Parallel routers directly cause "Ghost Endpoints" where tests pass on phantom paths while frontend fails on production paths.
  - An automated OpenAPI route registry guardrail test prevents router and route duplication statically and dynamically.
- **Remaining:**
  - Execute atomic git commit and route to `/tier8-audit-plan`.

