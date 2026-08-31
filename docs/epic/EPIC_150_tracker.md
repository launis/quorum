# Epic 150 Tracker: Zero Permissive Typing Lockdown

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

## Phase Execution Status

### Phase 1: LLM Message DTO & Prompt Infrastructure
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1_llm_message_dto_and_prompt_infrastructure.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1_llm_message_dto_and_prompt_infrastructure.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1_llm_message_dto_and_prompt_infrastructure.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1_llm_message_dto_and_prompt_infrastructure.md] @[docs/epic/EPIC_150_tracker.md]`

### Phase 2: Service & Studio Layer DTO Elimination
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase2_service_studio_layer_dto_elimination.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase2_service_studio_layer_dto_elimination.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase2_service_studio_layer_dto_elimination.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase2_service_studio_layer_dto_elimination.md] @[docs/epic/EPIC_150_tracker.md]`

### Phase 3: Hooks, Orchestrator & Repository Suppression Eradication
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase3_hooks_orchestrator_suppression_eradication.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase3_hooks_orchestrator_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase3_hooks_orchestrator_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase3_hooks_orchestrator_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`

### Phase 4: AST Hardening & Governance Lockdown
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase4_ast_hardening_and_governance_lockdown.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase4_ast_hardening_and_governance_lockdown.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase4_ast_hardening_and_governance_lockdown.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase4_ast_hardening_and_governance_lockdown.md] @[docs/epic/EPIC_150_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend Parity & Quality Loop**: Full execution of `uv run python scripts/backend_audit_loop.py backend_v2/ --test` passing Ruff, MyPy, and Pytest coverage gates (>90%).
- [ ] **[NOK] AST Guardrails FATAL Verification**: Full AST Guardrail audit passing `uv run python scripts/_ast_guardrails.py backend_v2/ --strict` with zero violations and zero suppressions.
- [ ] **[NOK] Cross-Platform SDUI Semantic Parity**: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
- [ ] **[NOK] Zero Suppressions Deterministic Check**: Zero `# noqa: QGR` across all non-test production files.
- [ ] **[NOK] Zero isinstance(dict) Deterministic Check**: Zero `isinstance(..., dict)` in non-exempt production files.

---

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]` to verify all requirements were physically implemented.
- [ ] Full backend test suite passes: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- [ ] Live E2E verification: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

## Baseline Violation Census (2026-08-31, Pre-Epic)

| Violation Type | Count | Target |
| :--- | :--- | :--- |
| `dict[str, Any]` annotations (total) | 516 | ~401 after exemptions |
| `isinstance(..., dict)` checks | 152 | All in non-exempt files |
| `# noqa: QGR` suppressions | 130 | Zero remaining |
| Unsuppressed `hasattr`/`getattr` | 77 | All in non-exempt files |
| `match/case dict` patterns | 0 | Already eliminated |

---

## Instructions for the Execution Agent
1. **Atomic Commit Mandate**: After ANY successful run of the `universal_quality_gate` audit script that passes, you MUST explicitly instruct the user to perform an atomic `git commit` BEFORE proceeding to the next file or logic block. Git commit messages MUST ALWAYS be written in English.
2. **Workspace Relative Syntax**: All file references MUST use `@-reference` syntax.
3. **Producer-Before-Consumer Ordering**: Follow the strict dependency ordering: Phase 1 -> Phase 2 -> Phase 3 -> Phase 4.
4. **Zero-Compromise Invariants**: Enforce `the_no_legacy_mandate`, `the_duct_tape_ban`, `zero_service_layer_fallbacks`, and `feature_sovereignty_mandate`.
5. **Boundary Exemptions**: NEVER modify `dict[str, Any]` annotations in EXEMPT files (database interfaces, drivers, wrapper, logging_config, exceptions).
6. **Workflow Execution Pipeline**: The mandatory workflow loop is: `/tier0-create-plan` -> `/tier0-research-plan` -> `/tier2-execute` -> `/tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.

---

# Session Handover Context

## Achieved
- **Epic 150 Created**: Drafted and validated `@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]` with 4 phases, boundary exemption register, and deterministic verification gates.
- **Boundary Audit Passed**: `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md` passed cleanly (0 findings).
- **Baseline Census**: Deterministic codebase scan established exact violation counts: 516 dict[str, Any], 152 isinstance(dict), 130 noqa:QGR, 77 hasattr/getattr.

## Learned
- Epic 149's "130+" count only captured service/hook layer annotations visible to `_ast_guardrails.py` in advisory mode, missing 386 additional annotations across models, LLM, database, core, utils, and worker layers.
- `dict[str, Any]` at absolute persistence boundaries (database drivers, Protocol interfaces) and stdlib infrastructure (LogRecord) is architecturally correct. Blanket eradication would break stdlib compatibility.
- New DTOs MUST be co-located with their primary consumer to prevent God Code accumulation in `system.py`.

## Remaining
- Phase 1 plan creation and execution (LLM Message DTO & Prompt Infrastructure).
- Phase 2 plan creation and execution (Service & Studio Layer DTO Elimination).
- Phase 3 plan creation and execution (Hooks, Orchestrator & Repository Suppression Eradication).
- Phase 4 plan creation and execution (AST Hardening & Governance Lockdown).

## Resume Command
```
/tier1-planner @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]
```
