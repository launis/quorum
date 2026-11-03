# Tracker: Topological Causal Synthesis Projection, SDUI Quiescent Summary Refinement & Scientific Formalization

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Topological_Causal_Synthesis_Projection.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Topological_Causal_Synthesis_Projection.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Topological_Causal_Synthesis_Projection.md] @[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md]`
  - [x] Step 1: Phase 1: Enrich CausalSynthesisBriefDTO and Synthesis Prompt Mandate with Topological Projection
  - [x] Step 2: Phase 2: Enforce PostgreSQL Trace Hydration Parity in synthesis_worker.py
  - [x] Step 3: Phase 3: Enrich Quiescent Summary in CausalGraphAdapter for SDUI & PDF Parity
  - [x] Step 4: Phase 4: Synchronize Scientific Paper docs/tiede.md with Topological Synthesis Projection & Replication Telemetry
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Topological_Causal_Synthesis_Projection.md] @[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/models/dtos/synthesis.py]
  - [x] @[backend_v2/models/prompts/synthesis/synthesis_directives.py]
  - [ ] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
  - [ ] @[backend_v2/workers/synthesis_worker.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Topological_Causal_Synthesis_Projection.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document `CausalSynthesisBriefDTO` topological projection (`largest_component_ratio`, `branch_convergence_ratio`, `isolated_deliverable_claims`, `established_causal_chains`), PostgreSQL JSONB `final_inputs` hydration parity in `synthesis_worker.py`, and bilingual quiescent summary rendering in `CausalGraphAdapter`.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` reflects `CausalSynthesisBriefDTO` in `backend_v2/models/dtos/synthesis.py` and `CausalGraphAdapter` in `backend_v2/services/sdui/adapters/causal_graph_adapter.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing Phase 2 topological synthesis projection and SDUI quiescent summary rendering in present tense.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Topological_Causal_Synthesis_Projection.md] @[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

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
| REQ-001 | Enrich `CausalSynthesisBriefDTO` in `@[backend_v2/models/dtos/synthesis.py#L133-L473]` with `largest_component_ratio`, `branch_convergence_ratio`, `isolated_deliverable_claims` (cap 16), `established_causal_chains` (cap 12), and `_extract_graph_topology`. | Step 1 | [x] Completed |
| REQ-002 | Expand `CAUSAL_TDA_DIAGNOSIS_MANDATE` in `@[backend_v2/models/prompts/synthesis/synthesis_directives.py]` with static `TOPOLOGICAL COHESION & ISOLATED CLAIM GROUNDING` rule and verify with unit tests in `@[backend_v2/tests/unit/models/dtos/test_synthesis.py#L471-L571]` and `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py#L48-L61]`. | Step 1 | [x] Completed |
| REQ-003 | Hydrate `causal_payload` from `reversed(final_inputs)` (`block_id in ("fusion", "graph")`) via `TypeAdapter(CausalTdaFusionResultDTO \| CausalGraphPayloadDTO)` in `@[backend_v2/workers/synthesis_worker.py#L95-L661]` with Fail-Fast `AppException` and verify in `@[backend_v2/tests/unit/workers/test_synthesis_worker.py#L794-L964]` and `@[backend_v2/tests/unit/workers/test_synthesis_worker.py#L967-L1026]`. | Step 2 | [x] Completed |
| REQ-004 | Enrich `CausalGraphAdapter._build_summary_text` in `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L34-L353]` to surface bilingual (`en`/`fi`) causal link count, isolated claim count, and cohesion percentage when `diagnoses_count == 0`, verified in `@[backend_v2/tests/unit/services/sdui/adapters/test_causal_graph_adapter.py#L464-L535]`. | Step 3 | [x] Completed |
| REQ-005 | Formalize Point 6 (`Topological Synthesis Projection Under Quiescent ATMS Baseline`) in Section 4.2.1, update Barrier 4 in Section 7.2, and document the confirmatory Trial Pair A replication in Section 8.1 of `@[docs/tiede.md]`. | Step 4 | [x] Completed |

# Session Handover Context

## Achieved
- **Step 1 (`98fe1898b`)**: Enriched `CausalSynthesisBriefDTO` in `@[backend_v2/models/dtos/synthesis.py#L133-L473]` with `largest_component_ratio`, `branch_convergence_ratio`, `isolated_deliverable_claims` (bounded to 16), and `established_causal_chains` (bounded to 12, filtering self-loops) via `_extract_graph_topology`. Added `TOPOLOGICAL COHESION & ISOLATED CLAIM GROUNDING` to `CAUSAL_TDA_DIAGNOSIS_MANDATE` in `@[backend_v2/models/prompts/synthesis/synthesis_directives.py]`. Verified with unit tests in `@[backend_v2/tests/unit/models/dtos/test_synthesis.py#L471-L571]` and `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py#L48-L61]`.
- **Step 2 (`593a80a02`)**: Enforced PostgreSQL JSONB trace hydration parity in `@[backend_v2/workers/synthesis_worker.py#L95-L661]` by inspecting `reversed(final_inputs)` and validating `step_dto.block_id in ("fusion", "graph")` via `TypeAdapter(CausalTdaFusionResultDTO | CausalGraphPayloadDTO).validate_python(step_dto.payload, strict=False)` with Fail-Fast `AppException(ErrorCodes.VALIDATION_FAILED, status_code=500)`. Verified with unit tests in `@[backend_v2/tests/unit/workers/test_synthesis_worker.py#L794-L964]` and `@[backend_v2/tests/unit/workers/test_synthesis_worker.py#L967-L1026]`.
- **Step 3 (`db4f09349`)**: Updated `CausalGraphAdapter.build_action_card` and `CausalGraphAdapter._build_summary_text` in `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L34-L353]` to surface causal link count, isolated claim count, and cohesion percentage when `diagnoses_count == 0`. Verified with unit tests in `@[backend_v2/tests/unit/services/sdui/adapters/test_causal_graph_adapter.py#L464-L535]`.
- **Step 4 (`1292534e6`)**: Formalized Point 6 (`Topological Synthesis Projection Under Quiescent ATMS Baseline`) in Section 4.2.1, updated Barrier 4 in Section 7.2, and documented the confirmatory Trial Pair A production replication telemetry in Section 8.1 of `@[docs/tiede.md]`.
- **Synchronized Plan & Tracker**: Materialized canonical workspace plan `@[docs/implementationplans/IMPLEMENTATION_PLAN_Topological_Causal_Synthesis_Projection.md]` and tracker `@[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md]` with the 4 `Tier 2 Hardening (Backend)` targets ready for `auto_hardening_runner.py`.

## Learned
- `scripts/auto_hardening_runner.py` parses unchecked `- [ ] @[backend_v2/...]` items specifically under the `Tier 2 Hardening (Backend)` section header and stages the tracker via `git add`; therefore, the tracker must reside inside `docs/implementationplans/` and contain the standardized `Tier 2 Hardening (Backend)` section.

## Remaining
- Execute `scripts/auto_hardening_runner.py` across the 4 backend production targets in `Tier 2 Hardening (Backend)`.
- Run `/tier7-describe-architecture` and final `/tier8-audit-plan`.

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Topological_Causal_Synthesis_Projection.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
```

