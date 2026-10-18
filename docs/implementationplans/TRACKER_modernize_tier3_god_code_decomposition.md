# Tracker: Modernize Tier 3 God Code Decomposition Workflow
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md]
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md] @[docs/implementationplans/TRACKER_modernize_tier3_god_code_decomposition.md]`
  - [x] Step 1: PRE_FLIGHT_TECH_DEBT_AND_CORE_RULES_ROUTING_OVERHAUL
  - [x] Step 2: TOPOLOGICAL_LEAF_FIRST_EXTRACTION_MANDATE
  - [x] Step 3: SHARED_CONCURRENCY_STATE_AND_TRANSACTION_AUDIT
  - [x] Step 4: SECURITY_DLP_TELEMETRY_AND_RFC7807_PARITY
  - [x] Step 5: AST_BOUNDARY_CALCULATION_AND_PYTHON_314_TECH_DEBT_INVENTORY
  - [x] Step 6: EXTRACTION_PIPELINE_BATCH_MIGRATION_AND_QUALITY_GATES
  - [x] Step 7: MARKDOWN_BOUNDARY_VERIFICATION_AND_SELF_HEALING
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md] @[docs/implementationplans/TRACKER_modernize_tier3_god_code_decomposition.md]`

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Verified no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Workflow documentation modernization; verified via `scripts/audit_markdown_boundaries.py` and `scripts/_ast_guardrails.py`.
- [x] **[OK] Tier 2 Hardening (Frontend)**: No production Dart files modified in this plan; workflow infrastructure.
- [x] **[OK] Pre-Delete Audit**: Verified no orphaned symbols or broken references remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Verified 93% line coverage on auth.py baseline, 100% on QGR017 unit tests.
- [x] **[OK] End-to-End Dry-Run Verification**: Verified AST symbol extraction on 993-line `backend_v2/services/auth.py` (30 symbol definitions extracted) and test baseline (30/30 passed, 93% coverage).

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_modernize_tier3_god_code_decomposition.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document modernized Tier 3 decomposition pipeline: AST boundary calculation, leaf-first topological sorting order, shared concurrency primitive state containers (`@dataclass(frozen=True)`), 5-file consumer migration batches, monolithic test suite preservation and modular decomposition, and permanent QGR017 facade lockdown.
     - `@[ki_deterministic_hardening_state.md]`: Document eradication of legacy `tmp/` persistence paths in favor of conversations sandbox and in-flight hardening before consumer migration.
     - `@[ki_zero_permissive_typing.md]`: Document authoritative 10-item Tech Debt Inventory covering PEP 695 type aliases, PEP 742 `TypeIs`, PEP 750 template strings, and strict Pydantic V2 configuration.
  2. **Directory Reference Sync:**
     - Verify registration of `scripts/_ast_boundary_utils.py`, `scripts/audit_mutation_coverage.py`, and updated workflow `@[.agents/workflows/tier3-god-code-decomposition.md]` in `@[.agents/rules/04_directory_reference.md]`.
  3. **Pillar Documentation Sync:**
     - Update `docs/architecture/01_system_context_and_invariants.md` and `docs/architecture/05_resilience_and_observability.md` describing modernized decomposition invariants, mathematical mutant kill gates, and test suite preservation.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md] @[docs/implementationplans/TRACKER_modernize_tier3_god_code_decomposition.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After completing each logical step, run verification commands and perform an atomic commit using Conventional Commits (`feat(workflows): ...` or `fix(workflows): ...`).
- **Markdown Boundary Verification**: At each step affecting `@[.agents/workflows/tier3-god-code-decomposition.md]`, execute `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md` to mathematically prove 0 fatal findings and 0 warnings.
- **Single Source of Truth**: All paths across workflow instructions and trackers must use POSIX forward slashes.
- **Execution Mode**: Continuous Full-Auto Mode is authorized via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md] @[docs/implementationplans/TRACKER_modernize_tier3_god_code_decomposition.md]`.
- **Session Handover Interval**: Trigger `/tier5-session-handover` after completing major milestones or before context budget limits are reached.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-01 | Pre-flight tech debt and core rules routing overhaul with physical rules loading and forward slash path normalization | Step 1 | [x] |
| REQ-02 | DAG Orchestrator & Architecture Lock Gate requiring explicit permission for `backend_v2/services/orchestrator/` targets | Step 1 | [x] |
| REQ-03 | Deterministic terminology replacement and XML protocol escaping in workflow descriptions | Step 1 | [x] |
| REQ-04 | Topological leaf-first extraction mandate enforcing call-graph DAG construction and depth-0 pre-extraction | Step 2 | [x] |
| REQ-05 | Elimination of circular dependency deadlocks and total ban on inline function-level import shims | Step 2 | [x] |
| REQ-06 | Shared concurrency state container (`@dataclass(frozen=True)`) for `asyncio.Lock`, `asyncio.Semaphore`, and circuit breakers | Step 3 | [x] |
| REQ-07 | Execution-scoped immutable Pydantic V2 context envelopes updated strictly inside shared lock | Step 3 | [x] |
| REQ-08 | Verification of authorization hook survival (`_enforce_tenant_isolation`) and RFC 7807 dual-logging | Step 4 | [x] |
| REQ-09 | Data Leak Prevention (DLP) telemetry audit banning raw payloads in spans | Step 4 | [x] |
| REQ-10 | Test suite invariance and modular test decomposition rewiring monolithic tests into domain-aligned test files | Step 4 | [x] |
| REQ-11 | Mathematical AST boundary calculation via `_ast_boundary_utils.py` replacing text-based line guessing | Step 5 | [x] |
| REQ-12 | Authoritative 10-item Tech Debt Inventory covering PEP 695, PEP 742, PEP 750, and strict Pydantic V2 | Step 5 | [x] |
| REQ-13 | In-flight module hardening prior to consumer migration preventing double-migration trap | Step 6 | [x] |
| REQ-14 | Bounded consumer migration batches (maximum 5 files per batch) with atomic commits and handover checkpoints | Step 6 | [x] |
| REQ-15 | Conditional mathematical core mutation testing gate requiring 100% mutant kill rate | Step 6 | [x] |
| REQ-16 | Conditional SDUI/PDF semantic parity verification gate | Step 6 | [x] |
| REQ-17 | Permanent proxy deletion backed by AST Guardrail QGR017 lockdown | Step 6 | [x] |
| REQ-18 | Modernized continuous session handover syntax `/tier2-execute --full-auto plan_path tracker_path` | Step 6 | [x] |
| REQ-19 | Automated markdown boundary audit self-healing gate verifying 0 fatal findings and 0 warnings | Step 7 | [x] |
| REQ-20 | End-to-end dry-run verification protocol on real 993-line monolith (auth.py) and orchestrator lock gate (dag_executor.py) | Verification Plan | [x] |

# Session Handover Context
## Achieved
- Hardened and modernized `.agents/workflows/tier3-god-code-decomposition.md` across all 7 steps.
- Implemented AST boundary extraction (`_ast_boundary_utils.py`), bottom-up leaf-first topological sorting order, shared concurrency containers (`@dataclass(frozen=True)`), DLP parity, RFC 7807 dual-logging, authoritative 10-item Tech Debt Inventory, in-flight hardening, bounded 5-file consumer migration batches, monolithic test suite preservation and modular decomposition, and QGR017 facade lockdown.
- Eliminated all legacy Windows backslashes in workflow file paths, escaped XML protocol tag literals, and replaced ambiguous phrasing.
- Verified 100% clean markdown boundaries via `audit_markdown_boundaries.py` with 0 fatal findings and 0 warnings on `.agents/workflows/tier3-god-code-decomposition.md`, `IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md`, and `TRACKER_modernize_tier3_god_code_decomposition.md`.
- Verified AST Guardrails `_ast_guardrails.py` and QGR017 unit tests (5/5 passed).
- Verified AST symbol extraction on real 993-line monolith `backend_v2/services/auth.py` (30 symbol definitions extracted) and unit test baseline (30/30 passed, 93% coverage).

## Learned
- Pre-existing markdown boundary checker strictly checks that all `@-reference` syntax paths physically exist on disk; formatting rules must use physical workspace reference paths.
- Concurrency primitives (`asyncio.Lock`, `asyncio.Semaphore`) must be grouped into frozen containers to avoid split-brain execution across subservices.

## Remaining
- Route through mandatory System 2 Red-Team Audit via `/tier8-audit-plan`.
- Run As-Built Architectural Sync via `/tier7-describe-architecture`.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_modernize_tier3_god_code_decomposition.md] @[docs/implementationplans/TRACKER_modernize_tier3_god_code_decomposition.md]
```
