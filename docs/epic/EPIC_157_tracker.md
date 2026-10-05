<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
</required_context_rules>

# EPIC 157 Tracker: Zero Permissive Typing & Test Persistence Modernization

**Epic:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]  
**Task Directory:** @[docs/epic/tasks_EPIC_157/]  

---

## Phase Execution Status

### Phase 1: Physical Boundary SSOT, Pre-Implementation Cleanups & Model Typing with 1-hop Consumers
**Plan:** @[docs/epic/tasks_EPIC_157/01_phase1_plan.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/01_phase1_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
  - [x] Step 1.1: Physical Boundary Exemption SSOT & Universal Ceilings
  - [x] Step 1.2: Accidental Boundary Exemption Loss Remediations
  - [x] Step 1.3: Domain Model Field Typing & Ingress Segregation
  - [x] Step 1.4: DTO Model Typing, StepSimulationTraceDTO Promotion & Dead Field Pruning
  - [x] Step 1.5: 1-hop Consumer Migration & Ingress Service Alignment
  - [x] Step 1.6: Unconditional Skip & Xfail Test Eradication (QGR026)
  - [x] Step 1.7: Open-JSON Whitelist SSOT (QGR027 FATAL AST Guardrail & Metric 11 Dict Eradication Audit)
- [x] **[OK] Test Coverage Assertions:** Verified 100% of Phase 1 test contracts, unit tests (212 passed in scripts, 44 passed in models/services, 88 passed in hooks/scoring), SDUI semantic parity, and 10/10 backend audit stages.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/01_phase1_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 2: System Exceptions, Hooks, LLM Caching Contract & Core Lockdown
**Plan:** @[docs/epic/tasks_EPIC_157/02_phase2_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/02_phase2_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/02_phase2_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
  - [x] Step 2.1: Domain Exception Extraction to AppException Hierarchy
  - [x] Step 2.2: Hook System Permissive Type Eradication & Strict Contracts
  - [x] Step 2.3: Provider Adapter Type Parity & Caching Contract
  - [x] Step 2.4: Core Engine Context Refactoring (No-Dict Invariant)
  - [x] Step 2.5: Ingress Service & Strategy Typings
  - [x] Step 2.6: Phase 2 Unit & Integration Test Coverage
- [x] **[OK] Test Coverage Assertions:** Verified 100% of Phase 2 test contracts, strict >=90% TDD unit test coverage across all 24 modified target files, zero AST violations, Census P=401 ratchet floor, and 10/10 backend audit stages.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/02_phase2_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 3: Test Persistence Migration — Hooks & LLM
**Plan:** @[docs/epic/tasks_EPIC_157/03_phase3_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=3`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 4: Test Persistence Migration — Services, Studio, Execution & Database
**Plan:** @[docs/epic/tasks_EPIC_157/04_phase4_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=4`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 5: Test Persistence Migration — Orchestrator & DAG
**Plan:** @[docs/epic/tasks_EPIC_157/05_phase5_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=5`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 6: Test Persistence Migration — Workers, API & Integration
**Plan:** @[docs/epic/tasks_EPIC_157/06_phase6_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/06_phase6_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=6`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/06_phase6_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/06_phase6_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/06_phase6_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 7: Mock-Emulation Sunset & QGR014 FATAL Hardening
**Plan:** @[docs/epic/tasks_EPIC_157/07_phase7_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/07_phase7_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=7`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/07_phase7_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/07_phase7_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/07_phase7_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 8: Universal Quality Gate Stage 10 Integration & Full-Duplex Client Parity
**Plan:** @[docs/epic/tasks_EPIC_157/08_phase8_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/08_phase8_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=8`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/08_phase8_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/08_phase8_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/08_phase8_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 9: Suppression & Cast Eradication (# noqa, cast(Any, ...))
**Plan:** @[docs/epic/tasks_EPIC_157/09_phase9_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/09_phase9_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=9`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/09_phase9_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/09_phase9_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/09_phase9_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 10: # type: ignore Eradication & Strict mypy Ignore Accounting
**Plan:** @[docs/epic/tasks_EPIC_157/10_phase10_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/10_phase10_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=10`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/10_phase10_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/10_phase10_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/10_phase10_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 11: Extended Dict Eradication (Tests, scripts/, Mapping)
**Plan:** @[docs/epic/tasks_EPIC_157/11_phase11_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/11_phase11_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=11`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/11_phase11_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/11_phase11_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/11_phase11_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 12: Client Permissive Map Eradication (Dart)
**Plan:** @[docs/epic/tasks_EPIC_157/12_phase12_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/12_phase12_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=12`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/12_phase12_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/12_phase12_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/12_phase12_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 13: Zero-Bypass Final Gate & Knowledge Synchronization
**Plan:** @[docs/epic/tasks_EPIC_157/13_phase13_plan.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/13_phase13_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=13`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/13_phase13_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/13_phase13_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/13_phase13_plan.md] @[docs/epic/EPIC_157_tracker.md]`

---

### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying all created or modified Python files.
  - [ ] @[backend_v2/models/domain/base.py]
  - [ ] @[backend_v2/models/domain/analyst.py]
  - [ ] @[backend_v2/models/domain/archivist.py]
  - [ ] @[backend_v2/models/domain/integrity.py]
  - [ ] @[backend_v2/models/domain/mcp.py]
  - [ ] @[backend_v2/models/domain/metrics.py]
  - [ ] @[backend_v2/models/domain/security.py]
  - [ ] @[backend_v2/models/domain/system_config.py]
  - [ ] @[backend_v2/models/domain/validation.py]
  - [ ] @[backend_v2/models/domain/xai.py]
  - [ ] @[backend_v2/models/domain/overseer.py]
  - [ ] @[backend_v2/models/dtos/atom_evaluation.py]
  - [ ] @[backend_v2/models/dtos/context_variables.py]
  - [ ] @[backend_v2/models/dtos/mcp.py]
  - [ ] @[backend_v2/models/dtos/prompt_context.py]
  - [ ] @[backend_v2/models/dtos/studio.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/models/dtos/telemetry.py]
  - [ ] @[backend_v2/models/dtos/trace.py]
  - [ ] @[backend_v2/models/llm.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/core/test_settings.py]
  - [ ] @[backend_v2/exceptions.py]
  - [ ] @[backend_v2/core/registry.py]
  - [ ] @[backend_v2/core/rate_limit.py]
  - [ ] @[backend_v2/hooks/validation.py]
  - [ ] @[backend_v2/hooks/input_processing.py]
  - [ ] @[backend_v2/hooks/scoring/matrix_hook.py]
  - [ ] @[backend_v2/hooks/scoring/passivity_hook.py]
  - [ ] @[backend_v2/llm/provider.py]
  - [ ] @[backend_v2/llm/adapters/base_adapter.py]
  - [ ] @[backend_v2/llm/adapters/vertex_adapter.py]
  - [ ] @[backend_v2/llm/adapters/ai_studio_adapter.py]
  - [ ] @[backend_v2/database/firestore_driver.py]
  - [ ] @[backend_v2/database/tinydb_driver.py]
  - [ ] @[backend_v2/database/repositories/execution.py]
  - [ ] @[backend_v2/database/repositories/workflow.py]
  - [ ] @[backend_v2/logging_config.py]
  - [ ] @[backend_v2/api/routers/system/telemetry.py]
  - [ ] @[backend_v2/services/execution/lifecycle_service.py]
  - [ ] @[backend_v2/services/execution/ingress_service.py]
  - [ ] @[backend_v2/services/ingress/pdf_chat_extractor.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/context_router.py]
  - [ ] @[backend_v2/services/orchestrator/two_pass_atomizer.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_explanation_service.py]
  - [ ] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]
  - [ ] @[backend_v2/services/mcp/tavily_search_client.py]
  - [ ] @[backend_v2/services/sdui/adapters/base_adapter.py]
  - [ ] @[backend_v2/scripts/generate_openapi.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/_dart_guardrails.py]
  - [ ] @[scripts/backend_audit_loop.py]
  - [ ] @[scripts/flutter_audit_loop.py]
  - [ ] @[scripts/audit_dict_eradication.py]
  - [ ] @[scripts/audit_warning_baseline.py]
  - [ ] @[scripts/audit_dto_parity.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying created or modified Flutter files.
  - [ ] @[client_app_v2/lib/features/studio/models/step_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_record.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_metadata.dart]
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Pre-Delete Audit**: Verify zero dangling consumers before proxy removal.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify test coverage exceeds 90% across modified domains.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Assert zero skipped, fake-failing, or gutted unit tests across all test suites.

---

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_157_tracker.md] @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_zero_permissive_typing.md]`: Path-based `BOUNDARY_EXEMPTION_FILES` replacing item 27 together with the 9-path Admission Ratchet test; 10-stage audit loop with Stage 9 Residual Debt Ceiling Ledger and Stage 10 Dict Eradication Audit over `backend_v2 scripts` replacing item 30; hardened `QGR014` covering 7 mock detection vectors; `QGR026` skip/xfail ban; `QGR027` unauthorized Open-JSON ban with `OPEN_JSON_EXEMPTION_FILES` SSOT whitelist; `DGR005` loose map ban and unconditional FATAL Dart guardrails; Zero Suppression Gate rejecting every `# noqa`, `cast(Any, ...)`, `# type: ignore`, and unapproved config ignores; extended dict audit covering `Mapping` / `MutableMapping`, test files, and `scripts/`; Dart codec signature boundary; `ExecutionInputsDTO.raw_inputs: Mapping[str, DomainInputValue]`; Field Classification Gate.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register removal of `InMemoryBlueprintTransformerRepository` and addition of new audit scripts and DTOs.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (specifically `01_system_context_and_invariants.md`, `05_resilience_and_observability.md`) describing newly established invariants in present tense without historical language or Epic IDs.

---

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Strict Execution Sequencing:** Execute phases strictly in order (`01_phase1_plan.md` -> `02_phase2_plan.md` -> `03_phase3_plan.md` through `13_phase13_plan.md`).
2. **Two-Stage Testing Pipeline:** During step execution, run localized tests (`uv run pytest <test_file>`). Before completing any phase, execute the full global completion gate: `uv run python scripts/backend_audit_loop.py backend_v2 --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.
3. **Strict Quality Gates:** All audit loop executions MUST run in strict mode (`--ast-strict`). Zero tolerance for unsuppressed AST warnings or bypass flags in production gates.
4. **Atomic Git Commits:** Perform an atomic git commit after completing each verified logical step with an English conventional commit message.
5. **Database Seeding Specifier:** Always execute seeding commands with the explicit environment specifier: `uv run python backend_v2/seed/run_seed.py local`.
6. **Zero Permissive Typing:** Never introduce raw dictionaries, duck-typing, dynamic casts, or unvalidated fallbacks.
7. **Workflow Loop & Session Handovers:** You MUST update the `/tier5-resume` or `/tier0-research-plan` (or `/tier0-create-plan` if the plan is missing) command at the bottom of this tracker before handing over the session. Execution Mode: Supports both Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto` or explicit continuous mandate; progresses autonomously across steps as long as quality gates pass 100%, and triggers clean session handover when the context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified files). Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands. Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

---

## Requirements Traceability Matrix

| Requirement / Directive | Target Scope | Plan Step | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- |
| Physical Boundary Exemption SSOT & Ceilings | scripts/_ast_guardrails.py, scripts/audit_dict_eradication.py, scripts/audit_warning_baseline.py, scripts/backend_audit_loop.py | Phase 1, Step 1 | test_ast_guardrails.py, Stage 9 audit gate | [OK] |
| Accidental Boundary Exemption Loss Remediations | models/dtos/telemetry.py, api/routers/system/telemetry.py, services/sdui/adapters/base_adapter.py, run_seed.py, repositories | Phase 1, Step 2 | audit_dict_eradication.py on target paths | [OK] |
| Domain Model Field Typing & Ingress Segregation | backend_v2/models/domain/base.py, analyst.py, archivist.py, integrity.py, mcp.py, metrics.py, security.py, system_config.py, validation.py | Phase 1, Step 3 | audit_dict_eradication.py models/domain | [OK] |
| DTO Model Typing & Dead Field Pruning | backend_v2/models/domain/xai.py, models/dtos/atom_evaluation.py, mcp.py, prompt_context.py, studio.py, trace.py, models/llm.py | Phase 1, Step 4 | audit_dict_eradication.py models/dtos | [OK] |
| StepSimulationTraceDTO Promotion & Simulation Service Typing | backend_v2/models/dtos/studio.py, backend_v2/services/studio/simulation_service.py | Phase 1, Step 4 | test_studio.py, test_simulation_service.py | [OK] |
| Open-JSON Whitelist & Unauthorized JsonValue Ban (QGR027) | scripts/_ast_guardrails.py, scripts/audit_dict_eradication.py, backend_v2/models/ | Phase 1, Step 7 | test_ast_guardrails.py, test_audit_dict_eradication.py, Metric 11 | [OK] |
| 1-hop Consumer Migration & Ingress Service Alignment | models/dtos/context_variables.py, synthesis_engine.py, matrix_reducer.py, matrix_explanation_service.py, ingress_service.py | Phase 1, Step 5 | pytest test_synthesis_engine.py test_ingress_service.py | [OK] |
| Unconditional Skip & Xfail Test Eradication (QGR026) | test_boundaries.py, test_epic_61_hardening.py, test_provider_rate_limit.py, test_fallback_caching.py, test_scoring.py | Phase 1, Step 6 | Census S command returns 0 matches | [OK] |
| Domain Exception Extraction to AppException Hierarchy | models/domain/base.py, core/exceptions.py, core/error_codes.py, services/orchestrator/dag_executor.py | Phase 2, Step 1 | test_domain_exceptions.py, test_dag_executor.py | [NOK] |
| Hook System Permissive Type Eradication & Strict Contracts | hooks/base.py, hooks/context.py, hooks/input_processing.py, hooks/scoring.py, hooks/registry.py | Phase 2, Step 2 | test_hooks.py, audit_dict_eradication.py | [NOK] |
| Provider Adapter Type Parity & Caching Contract | llm/provider.py, llm/adapters/base_adapter.py, llm/adapters/vertex_adapter.py, llm/adapters/ai_studio_adapter.py | Phase 2, Step 3 | test_vertex_adapter.py, test_ai_studio_adapter.py | [NOK] |
| Core Engine Context Refactoring (No-Dict Invariant) | services/orchestrator/dag_executor.py, services/orchestrator/context_router.py, services/orchestrator/two_pass_atomizer.py | Phase 2, Step 4 | test_context_router.py, test_two_pass_atomizer.py | [NOK] |
| Ingress Service & Strategy Typings | services/execution/ingress_service.py, services/execution/lifecycle_service.py, services/mcp/tavily_search_client.py | Phase 2, Step 5 | test_ingress_service.py, test_tavily_search_client.py | [NOK] |
| Phase 2 Unit & Integration Test Coverage | backend_v2/tests/unit/core/, tests/unit/hooks/, tests/unit/llm/, tests/integration/ | Phase 2, Step 6 | Global backend audit loop passes | [NOK] |

---

# Session Handover Context

## Achieved
- Formally drafted `EPIC 157: Zero Permissive Typing & Test Persistence Modernization` at `@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]`.
- Created detailed, fully verified implementation plans for Phase 1 (`@[docs/epic/tasks_EPIC_157/01_phase1_plan.md]`) and Phase 2 (`@[docs/epic/tasks_EPIC_157/02_phase2_plan.md]`).
- Created placeholder plans with complete boundary preservation for Phases 3 through 13 (`03_phase3_plan.md` to `13_phase13_plan.md`).
- Verified 100% boundary pass rates via `scripts/audit_planner_output.py` and `scripts/audit_markdown_boundaries.py`.
- Established `docs/epic/EPIC_157_tracker.md` governing all 13 phases, Traceability Matrix, and Post-Implementation quality gates.
- Completed Tier 0 deep System 2 research, falsification, and red-teaming for Phase 1 (`@[docs/epic/tasks_EPIC_157/01_phase1_plan.md]`).
- Mathematically verified all 30 model violations across 17 files with `audit_dict_eradication.py`.
- Formulated OS-independent POSIX path normalization for `BOUNDARY_EXEMPTION_FILES` to eliminate Windows backslash matching bugs.
- Uncovered root cause for `test_scoring.py` xfail markers: 2 tests were already XPASSing, and 2 were failing `ExecutionInputsDTO` hydration due to cognitive state invariant violations in test fixtures.
- Successfully implemented 100% of Phase 1: established `BOUNDARY_EXEMPTION_FILES` SSOT, created `ResidualDebtCeilingsDTO` wired into Stage 9/10 audit loop, implemented `QGR026`, retyped all 30 model violations, migrated 1-hop consumers, and eradicated unconditional test skip/xfail markers.
- Promoted `PromptBlockSimulationResponse.trace` and `WorkflowSimulationResponse.trace` in `@[backend_v2/models/dtos/studio.py]` to strictly typed `StepSimulationTraceDTO` and eliminated loose `trace={}` instantiation in `@[backend_v2/services/studio/simulation_service.py]`.
- Eliminated permissive `dict[str, JsonValue]` in `@[backend_v2/models/domain/archivist.py]` and `@[backend_v2/models/domain/analyst.py]`, retyping `dynamic_inputs` to `dict[str, IngressInputValue]` while decoupling circular dependency cycles.
- Implemented static AST rule `QGR027` (FATAL) in `@[scripts/_ast_guardrails.py]` with `OPEN_JSON_EXEMPTION_FILES` SSOT whitelist and monotonic phase ratchet `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`.
- Wired Metric 11 (`unauthorized_open_json_annotations`) into `@[scripts/audit_dict_eradication.py]` to fail fast if any non-whitelisted model introduces `dict[..., JsonValue]`.
- Added unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` (Partition 27) and `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`, achieving 100% green tests.
- Completed Tier 8 System 2 Post-Implementation Red Team Audit (`red_team_audit_01_phase1_plan.md`): Verified 100% adherence to model retyping, boundary SSOT, and destructive cleanups; identified 12 failing legacy test fixtures requiring alignment before phase sign-off.
- Remediated all 12 legacy test fixture, hook envelope, and logging format regressions identified in the Tier 8 Red Team Audit.
- Updated trace metadata fixtures to canonical `step_metadata` across test suites (`test_blueprint_combined_costs.py`, `test_worker.py`, `test_execution_worker.py`, `test_blueprint.py`).
- Retyped `MetricsPayloadDTO.root` to `dict[str, IngressInputValue | None]` and aligned `test_security.py`.
- Formulated `type NestedValidationInputs = dict[str, IngressInputValue]` PEP 695 type alias for `ValidationHookPayloadDTO` and guarded empty raw inputs unpacking in `backend_v2/hooks/validation.py`.
- Fixed logging format string placeholder parity in `backend_v2/services/auth.py`.
- Completed Tier 8 System 2 Post-Implementation Red Team Audit (`red_team_audit_01_phase1_plan.md`): Verified 100% adherence to model retyping, boundary SSOT, and destructive cleanups; confirmed 10/10 Universal Quality Gate stages clean with 5,067 passing tests, 97.74% coverage, 0 AST violations, and 0 skipped/xfailed tests. Phase 1 is formally signed off.
- Completed Tier 0 deep System 2 research, falsification, and red-teaming for Phase 2 (`@[docs/epic/tasks_EPIC_157/02_phase2_plan.md]`).
- Audited all 12 line-bounded files from the Epic against the physical codebase AST, verifying 100% boundary preservation.
- Executed `scripts/audit_dict_eradication.py` across Phase 2 targets, identifying exactly 35 AST violations across 10 files and codifying them into `Pre-Implementation Cleanups`.
- Synthesized the 5-Column Architectural Directives Table with 1:1 table-protocol reconciliation (rule `MBD008`) and zero markdown boundary errors (`scripts/audit_markdown_boundaries.py`).
- Uncovered and resolved critical failure points: retyping `LLMMessageDTO` content blocks for Anthropic caching parity, sanitizing `ValidationError.errors()` context to JSON-safe primitives for `AppException(details=...)`, adding `test_caching_service.py` to target boundaries for defined `CachingPayloadResultDTO` 2-tuple mock modernization, and consolidating parallel matrix hook nested maps into defined `MatrixAggregationStateDTO`.

## Learned
- Strict adherence to the 13-phase architecture requires zero permissive typing, absolute eradication of loose dicts, eradication of inline `# noqa` and `# type: ignore` suppressions, and full-duplex DTO parity with Flutter.
- Phase 1 and Phase 2 establish the physical boundary SSOT, domain model field typings, system exception contracts, and hook/LLM typing covenants.
- `BOUNDARY_EXEMPTION_FILES` must enforce OS-independent path normalization (`Path(filepath).resolve().relative_to(repo_root).as_posix()`) across `_ast_guardrails.py` and `audit_dict_eradication.py` to prevent false positive violations on Windows environments.
- Permissive `dict[str, JsonValue]` is a duct-tape shortcut for internal models and execution traces; Open-JSON must be restricted exclusively to 7 approved external specification boundaries (`mcp.py`, `system_config.py`, `validation.py`, `base.py`, `llm.py`, `generate_openapi.py`).
- Internal simulation traces must be strictly typed to `StepSimulationTraceDTO` with typed attributes rather than open-ended JSON dictionaries.
- Using `IngressInputValue` for dynamic input schemas resolves values while cleanly decoupling domain import cycles (`inputs.py` -> `coach.py` -> `judge.py` -> `archivist.py`).
- Static AST guardrails (`QGR027`) and `audit_dict_eradication.py` Metric 11 mathematically prevent future regressions of unauthorized `JsonValue` dictionaries.
- Phases 3 through 7 systematically migrate unit, integration, and mock persistence tests to stateful in-memory repository fakes, completely eliminating deceptive mocks.
- Phases 8 through 13 integrate universal audit loops (Stages 9 and 10), eradicate all suppression comments and loose Dart maps, and lock residual debt baselines to zero.
- Eliminating legacy fallback keys (specifically `_step_metadata`) from trace models requires simultaneously updating test fixtures in `test_blueprint_combined_costs.py`, `test_worker.py`, and `test_execution_worker.py` to supply the canonical `step_metadata` key.
- Defining a PEP 695 type alias `type NestedValidationInputs = dict[str, IngressInputValue]` cleanly models dynamic nested dictionaries under Pydantic V2 while maintaining 0 AST violations and zero permissive typing.
- Guarding against falsy `{}` in validation hook payload extraction (`state.inputs.raw_inputs is not None`) prevents unintended fallback to dumping unflattened model attributes.
- In `anthropic_adapter.py`, block-level caching injects structured dictionary blocks into message content; retyping `LLMMessageDTO.content` to accommodate structured content blocks preserves strict DTO contracts across provider boundaries without fallback dicts.
- Passing raw `ValidationError.errors()` to `AppException.details` violates JSON serialization contracts because `ErrorDetails.ctx` can contain non-JSON Python objects; extracting location, message, and type into JSON-safe dictionaries resolves RFC 7807 compliance.
- Mock specifications in `test_caching_service.py` expecting 2-tuples must be updated synchronously when modernizing `prepare_caching_payload` to return defined `CachingPayloadResultDTO`.
- In `matrix_hook.py`, parallel block-level accumulator maps (`block_scale_stats`, `evaluated_atoms_by_block`, `matrix_extensions_by_block`) create primitive obsession violations that are eliminated by grouping them into a single defined `MatrixAggregationStateDTO`.

## Remaining
- Execute Phase 2: `/tier2-execute @[docs/epic/tasks_EPIC_157/02_phase2_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- Plan, Research & Execute Phases 3 through 13.

## Resume Command
/tier2-execute @[docs/epic/tasks_EPIC_157/02_phase2_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto
