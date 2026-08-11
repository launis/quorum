# Tracker: EPIC 136 Comprehensive Test Expansion & AST Guardrails

@[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion.md]
@[c:\src\quorum\docs\epic\tasks_EPIC_136/]

<required_context_rules>
  @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\ai_testing_standards\artifacts\ki_ai_testing_standards.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\agent_context_quarantine\artifacts\ki_agent_context_quarantine.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\neuro_symbolic_agentic_workflow\artifacts\ki_neuro_symbolic_agentic_workflow.md]
  @[c:\src\quorum\.agents\rules\01-python-backend.md]
  @[c:\src\quorum\.agents\rules\05_llm_architecture.md]
</required_context_rules>

## Phase Execution Status

### Phase 1: AST Guardrails (Concurrency & Domain Security)
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_136\01_phase_1.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_136\01_phase_1.md] @[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion_tracker.md]`
- [x] (04109e3a) **[OK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_136\01_phase_1.md] @[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion_tracker.md]`
  - [x] (04109e3a) Step 1: Create deterministic AST inspection guardrails ensuring critical concurrency and pacing constructs are never removed. (Assert Semaphore, TaskGroup, enqueue_job)
  - [x] (04109e3a) Step 1: Implement concurrency negative tests: 1. Missing Construct Detection (no `asyncio.Semaphore`). 2. False Positive Prevention (`Semaphore` as string literal).
  - [x] (04109e3a) Step 1: AST scanner constraint: MUST NOT use naive string matching (`str.find`). It must recursively parse `ast.ImportFrom` nodes.
  - [x] (04109e3a) Step 1: Create deterministic AST inspection guardrails for domain security. Assert LLMClient.from_strategy, _safe_commit, StreamingResponse, ConfigDict(strict=True, extra="forbid"), ban run_chat.
  - [x] (04109e3a) Step 1: Implement domain security negative tests: 1. Banned Node Detection. 2. False Positive Prevention.
  - [x] (04109e3a) Step 1: Constraint: The `hasattr` ban is strictly scoped to `backend_v2/api/` (Controller/Router layer) only.
  - [x] (04109e3a) Step 1: Execute local verification: backend_audit_loop.py on both new tests.
  - [x] (04109e3a) Step 1: Execute `/tier5-session-handover` to start a new session for Phase 2.
- [x] (04109e3a) **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_136\01_phase_1.md] @[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion_tracker.md]`

### Phase 2: Concurrency Fuzzer & Context Boundary Tests
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_136\02_phase_2.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_136\02_phase_2.md] @[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_136\02_phase_2.md] @[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion_tracker.md]`
  - [x] Step 2: Start the new session by executing `/tier5-resume` using the payload provided at the end of Phase 1.
  - [x] Step 2: Create `backend_v2/tests/unit/test_concurrency_fuzzer.py` to prove Two-Tier Semaphore Architecture. Monkeypatch, explicitly instantiate fresh `DAGExecutor`, clear caches.
  - [x] Step 2: Patch `provider.router.acompletion` with mock atomic counter, fire 10 concurrent tasks, assert peak.
  - [x] Step 2: Implement fuzzer negative tests: Zero Concurrency, Exceeding Physical Limit.
  - [x] Step 2: Create `backend_v2/tests/unit/test_llm_context_bounds.py` to prove mapping to `AGENT_EXECUTION_CRITICAL`. Patch to raise `ContextWindowExceededError`.
  - [x] Step 2: Implement context bounds negative tests: Non-Context 400 Error, Transient 503 Error Path.
  - [x] Step 2: Execute local verification: backend_audit_loop.py on new tests.
  - [x] Step 2: Execute global completion gates.
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_136\02_phase_2.md] @[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] Backend and Frontend full-stack integration test gates (N/A - backend unit test epic)

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains. (Aspirational test skipped explicitly per plan).
- [x] **[N/A] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories. (Passed local and global audit).
- [x] **[N/A] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [x] **[N/A] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [x] **[N/A] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [x] **[OK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [x] **[OK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/. (`ki_ast_guardrail_testing.md` created)
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_136_Test_Expansion.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- Atomic commit mandates, seeding environment commands (`uv run python backend_v2/seed/run_seed.py local`), `@-reference` syntax rule.
- You MUST update the `/tier5-resume` or `/tier0-research-plan` command at the bottom of this tracker before handing over the session. 
- Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. 
- The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). 
- You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands (specifically: `/tier0-research-plan`, `/tier2-execute`, `/tier8-audit-plan`). 
- Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. 
- Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

## Requirements Traceability Matrix
| Req ID | Description | Phase/Step | Status |
|--------|-------------|------------|--------|
| R1 | Create AST guardrails asserting `asyncio.Semaphore` node in `provider.py` and `dag_executor.py` | Phase 1 (Step 1) | [x] |
| R2 | Create AST guardrails asserting `asyncio.TaskGroup` node in `dag_executor.py`, `worker.py`, `execution.py` | Phase 1 (Step 1) | [x] |
| R3 | Create AST guardrails asserting `enqueue_job` attribute call in `worker.py` and `execution.py` | Phase 1 (Step 1) | [x] |
| R4 | Implement concurrency negative test: Missing Construct Detection | Phase 1 (Step 1) | [x] |
| R5 | Implement concurrency negative test: False Positive Prevention (`Semaphore` as string) | Phase 1 (Step 1) | [x] |
| R6 | AST scanner must recursively parse `ast.ImportFrom` nodes to build alias map, rejecting naive `str.find` | Phase 1 (Step 1) | [x] |
| R7 | Create AST guardrails asserting `LLMClient.from_strategy` initialization | Phase 1 (Step 1) | [x] |
| R8 | Create AST guardrails asserting `_safe_commit` (AsyncFunctionDef) in workflow loops | Phase 1 (Step 1) | [x] |
| R9 | Create AST guardrails asserting `StreamingResponse` in streaming endpoints | Phase 1 (Step 1) | [x] |
| R10 | Create AST guardrails asserting Pydantic `ConfigDict(strict=True, extra="forbid")` in all `backend_v2/models/` | Phase 1 (Step 1) | [x] |
| R11 | Create AST guardrails banning unstructured `run_chat()` inside all files in `backend_v2/services/orchestrator/` | Phase 1 (Step 1) | [x] |
| R12 | Implement domain security negative test: Banned Node Detection (`hasattr` in `backend_v2/api/`) | Phase 1 (Step 1) | [x] |
| R13 | Implement domain security negative test: False Positive Prevention (`hasattr` in `backend_v2/services/execution.py`) | Phase 1 (Step 1) | [x] |
| R14 | Ensure `hasattr` ban is strictly scoped ONLY to `backend_v2/api/` (Controller/Router layer) | Phase 1 (Step 1) | [x] |
| R15 | Execute local verification for Phase 1 AST guardrails tests | Phase 1 (Step 1) | [x] |
| R16 | Start Phase 2 session using `/tier5-resume` | Phase 2 (Step 2) | [x] |
| R17 | Create `test_concurrency_fuzzer.py` testing Two-Tier Semaphore Architecture | Phase 2 (Step 2) | [x] |
| R18 | Monkeypatch `max_concurrent_llm_steps` to 2 and instantiate fresh `DAGExecutor` inside the fuzzer test | Phase 2 (Step 2) | [x] |
| R19 | Clear caches in fuzzer test setup/teardown (`_semaphores`, `_router_cache`, `_httpx_clients`) | Phase 2 (Step 2) | [x] |
| R20 | Patch `provider.router.acompletion` with mock atomic counter (`asyncio.Event()`) | Phase 2 (Step 2) | [x] |
| R21 | Fire 10 concurrent tasks via `asyncio.TaskGroup` and assert `peak_concurrent <= max_concurrent_llm_steps` | Phase 2 (Step 2) | [x] |
| R22 | Implement fuzzer negative tests: Zero Concurrency and Exceeding Physical Limit | Phase 2 (Step 2) | [x] |
| R23 | Create `test_llm_context_bounds.py` to prove `ContextWindowExceededError` maps to `AGENT_EXECUTION_CRITICAL` | Phase 2 (Step 2) | [x] |
| R24 | Patch `provider.router.acompletion` to raise `litellm.ContextWindowExceededError` with strict args to prevent logger crash | Phase 2 (Step 2) | [x] |
| R25 | Implement context bounds negative tests: Non-Context 400 Error and Transient 503 Error Path | Phase 2 (Step 2) | [x] |
| R26 | Execute local verification for fuzzer and context bounds tests | Phase 2 (Step 2) | [x] |
| R27 | Execute global completion gates (`uv run python scripts/backend_audit_loop.py backend_v2/ --test`) | Phase 2 (Step 2) | [x] |

# Session Handover Context
## Achieved
- Formally scoped Epic 136 into discrete implementation phases.
- Verified test mock targets, file paths, and existing semantic constructs.
- Resolved domain rule conflicts (`hasattr` ban scope, `html.escape` assertion viability).
- Generated execution plans (`01_phase_1.md`, `02_phase_2.md`) and the master Tracker.
- Completed Tier 0 Research & Analysis (Red-Teaming) for Phase 1 & Phase 2.
- Successfully executed Phase 1 AST guardrails tests via `/tier2-execute` and passed Phase 1 Audit (`red_team_audit_phase_1.md`).
- Implemented and passed all unit tests for domain security and concurrency AST constraints.
- Enforced strict Pydantic V2 configuration (`model_config = ConfigDict(strict=True, extra="forbid")`) globally across the `backend_v2/models` directory, including TypeAdapter payloads.
- Verified all code via `backend_audit_loop.py`, passing 100% of formatting, typing, UI validation, and test coverage assertions.
- Successfully executed Phase 2 Concurrency Fuzzer & Context Boundary Tests via `/tier2-execute`.
- Passed Phase 2 Audit (`red_team_audit_phase_2.md`).
- Fixed MyPy type hints (`dict` -> `dict[str, Any]`) during final audit verification.

## Learned
- **Baseline State Snapshot**: 
  - The AST guardrails and new tests for concurrency fuzzing and context bounds do not currently exist. 
  - `semaphore_max_concurrency` does not exist; the SSOT is `max_concurrent_llm_steps`. 
  - `hasattr` is extensively used in the services layer; banning it globally would break the backend, hence the explicit constraint to limit the ban to `backend_v2/api/`. 
  - `html.escape` does not exist in the source codebase yet, meaning tests asserting its existence must use `@pytest.mark.skip`.
  - The correct mock target for acompletion is `provider.router.acompletion`.
- **Phase 1 Red-Teaming Learnings**:
  - The initial planner dropped the `html.escape` assertion and required XML boundary blocks (`<anti_targets>`, `<dod_checklist>`). These were manually restored.
  - AST scanning logic for Pydantic strictness and `run_chat` ban requires explicit negative tests to prevent false positives and bypasses, which were added to the plan.
- **Phase 1 Execution Learnings**:
  - Global `ConfigDict` injection requires manual verification for manually implemented DTOs (like `MetricsPayloadDTO`) that use `TypeAdapter` and don't inherit from `BaseModel`.
  - Automated regex-based replacement scripts must be carefully audited to prevent indentation errors within classes.
  - AST guardrail tests inherently check logic structure by returning boolean dicts instead of raising business logic exceptions. Thus, `pytest.raises(AppException)` is not applicable there, but the architectural intent of the `anti_happy_path_mandate` is satisfied through structural false positive/negative validation logic.
- **Post-Implementation E2E Learnings**:
  - The E2E REST API gate failed with `INVALID_OUTPUT_SCHEMA` because `MetadataHookPayloadDTO` enforced `extra="forbid"`, which caused a crash when it received the full `global_context_vars` (which includes API ingress data like `language`, `simulation_mode`).
  - To respect both the `extra="forbid"` mandate from Epic 136 and the "Duct Tape Ban" (no `.get()` fallbacks), `MetadataHookPayloadDTO` was refactored to inherit from `WorkflowInputsIngress`. This allowed it to strictly validate known API inputs while continuing to safely forbid unknown fields.

## Remaining
- Epic 136 code implementation is fully completed.
- As-Built Architectural Sync (`/tier7-describe-architecture`).
- Final Epic Audit (`/tier8-audit-epic`).

## Resume Command
`/tier7-describe-architecture`
