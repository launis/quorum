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
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/02_phase2_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 3: Test Persistence Migration — Hooks & LLM
**Plan:** @[docs/epic/tasks_EPIC_157/03_phase3_plan.md]
- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=3`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
  - [x] Step 3.0: Strategic Alignment & Persistence Census Probe
  - [x] Step 3.1: AsyncMock Fixtures & Import-Only Target Modernization
  - [x] Step 3.2: Ad-Hoc Repository Classes & Cast(Any) Eradication (Census K & X)
  - [x] Step 3.3: Hook Persistence Emulation-Fake Migration (Census A & B)
  - [x] Step 3.4: LLM Client & Handler Persistence Migration (Census A)
  - [x] Step 3.5: Keyword-Injected Repository Mocks Eradication (Census D)
  - [x] Step 3.6: Two-Stage Testing Pipeline & Zero-Bypass Verification Gate
- [x] **[OK] Test Coverage Assertions:** Verified 100% of Phase 3 test contracts across 30 Hook and LLM test files, strict >=90% TDD unit test coverage (global 97.75%, 5,091 passed), zero AST violations, Census A=0, B=0, C=0, I=0, D=0, K=0, X=0, and 10/10 backend audit stages with exit code 0.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 4: Test Persistence Migration — Services, Studio, Execution & Database
**Plan:** @[docs/epic/tasks_EPIC_157/04_phase4_plan.md]
- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=4`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
  - [x] Step 4.0: Strategic Alignment & Persistence Census Probe
  - [x] Step 4.1: Repository Fixtures Modernization & dict_to_obj Deletion
  - [x] Step 4.2: Database Repositories & Real TinyDB Driver Migration
  - [x] Step 4.3: Census B Attribute Replacements & Census C Object Patches
  - [x] Step 4.4: Service & Studio Persistence Emulation-Fake Migration (Census A & I)
  - [x] Step 4.5: Keyword-Injected Repository Mocks Eradication (Census D)
  - [x] Step 4.6: Two-Stage Testing Pipeline & Zero-Bypass Verification Gate
- [x] **[OK] Test Coverage Assertions:** Verified 100% of Phase 4 test contracts, unit tests (5,091 passed in backend_v2, 97.67% total line coverage exceeding 90% threshold), SDUI semantic parity, 0 AST violations, and 10/10 backend audit stages.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md]`

### Phase 5: Test Persistence Migration — Orchestrator & DAG
**Plan:** @[docs/epic/tasks_EPIC_157/05_phase5_plan.md]
- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --phase=5`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
  - [x] Step 5.0: Strategic Alignment & Persistence Census Probe
  - [x] Step 5.1: Repository Fixtures Modernization & MCP Concurrency Fakes
  - [x] Step 5.2: Census B Attribute Replacements & Deterministic Fault Injection
  - [x] Step 5.3: Keyword-Injected Repository Mocks Eradication (Census D)
  - [x] Step 5.4: Orchestrator & Strategy Persistence Emulation-Fake Migration (Census A & I)
  - [ ] Step 5.5: Concurrency, Fuzzer & Logic Suites Persistence Migration (Census A & I)
  - [ ] Step 5.6: Two-Stage Testing Pipeline & Zero-Bypass Verification Gate
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
| Open-JSON Whitelist & Unauthorized JsonValue Ban (QGR027) | scripts/_ast_guardrails.py, scripts/audit_dict_eradication.py, backend_v2/models/ | Phase 1, Step 1 | test_ast_guardrails.py, test_audit_dict_eradication.py, Metric 11 | [OK] |
| 1-hop Consumer Migration & Ingress Service Alignment | models/dtos/context_variables.py, synthesis_engine.py, matrix_reducer.py, matrix_explanation_service.py, ingress_service.py | Phase 1, Step 5 | pytest test_synthesis_engine.py test_ingress_service.py | [OK] |
| Unconditional Skip & Xfail Test Eradication (QGR026) | test_boundaries.py, test_epic_61_hardening.py, test_provider_rate_limit.py, test_fallback_caching.py, test_scoring.py | Phase 1, Step 6 | Census S command returns 0 matches | [OK] |
| Domain Exception Extraction to AppException Hierarchy | models/domain/base.py, core/exceptions.py, core/error_codes.py, services/orchestrator/dag_executor.py | Phase 2, Step 1 | test_domain_exceptions.py, test_dag_executor.py | [OK] |
| Hook System Permissive Type Eradication & Strict Contracts | hooks/base.py, hooks/context.py, hooks/input_processing.py, hooks/scoring.py, hooks/registry.py | Phase 2, Step 2 | test_hooks.py, audit_dict_eradication.py | [OK] |
| Provider Adapter Type Parity & Caching Contract | llm/provider.py, llm/adapters/base_adapter.py, llm/adapters/vertex_adapter.py, llm/adapters/ai_studio_adapter.py | Phase 2, Step 3 | test_vertex_adapter.py, test_ai_studio_adapter.py | [OK] |
| Core Engine Context Refactoring (No-Dict Invariant) | services/orchestrator/dag_executor.py, services/orchestrator/context_router.py, services/orchestrator/two_pass_atomizer.py | Phase 2, Step 4 | test_context_router.py, test_two_pass_atomizer.py | [OK] |
| Ingress Service & Strategy Typings | services/execution/ingress_service.py, services/execution/lifecycle_service.py, services/mcp/tavily_search_client.py | Phase 2, Step 5 | test_ingress_service.py, test_tavily_search_client.py | [OK] |
| Phase 2 Unit & Integration Test Coverage | backend_v2/tests/unit/core/, tests/unit/hooks/, tests/unit/llm/, tests/integration/ | Phase 2, Step 6 | Global backend audit loop passes | [OK] |
| Async Mock Fixtures & Repository Fake Replacement | test_epic66_multi_provider.py, test_handler.py, hooks/test_interaction_hook.py, test_structured_retry.py, test_cdata_hardening_comprehensive.py | Phase 3, Step 1 | Localized pytest passes, Census I=0 | [OK] |
| Ad-Hoc Repository Classes & Cast(Any) Eradication | backend_v2/tests/unit/hooks/test_scoring.py, test_input_processing.py, test_dlq_guard.py, test_metadata.py, test_references.py, test_security.py | Phase 3, Step 2 | Census K=0, X=0, localized pytest passes | [OK] |
| Hook Persistence Emulation-Fake Migration | backend_v2/tests/unit/hooks/test_archival.py, test_atom_flattening.py, test_atom_sampling_determinism.py, test_integrity.py, test_matrix_hook.py, test_passivity_hook.py | Phase 3, Step 3 | Census A=0, B=0, localized pytest passes | [OK] |
| LLM Client & Handler Persistence Migration | backend_v2/tests/unit/llm/test_client.py, test_llm_client_tiers.py, test_handler.py, test_llm_context_bounds.py | Phase 3, Step 4 | Census A=0, I=0, localized pytest passes | [OK] |
| Keyword-Injected Repository Mocks Eradication | backend_v2/tests/unit/hooks/test_validation.py, test_source_verification_hook.py, test_linguistics.py, test_metadata.py, test_metrics.py, test_references.py, test_synthesis_distiller_hook.py, test_hook_registry.py, test_google_providers_separation.py | Phase 3, Step 5 | Census D=0, localized pytest passes | [OK] |
| Phase 3 Test Persistence Migration Quality Gates | 30 Hook and LLM test files across backend_v2/tests/unit/ | Phase 3, Step 6 | Global backend audit loop & SDUI parity pass | [OK] |
| Repository Fixtures Modernization & dict_to_obj Deletion | test_chat_parser.py, test_output_profile_service.py, test_workflow_service.py, test_security.py, test_blueprint.py, test_dependencies.py | Phase 4, Step 1 | dict_to_obj deleted (0 matches repo-wide), typed fixtures | [OK] |
| Database Repositories & Real TinyDB Driver Migration | test_repositories_v2.py, database/repositories/components/test_agent.py, test_prompt_block.py, test_task_blueprint.py | Phase 4, Step 2 | Real TinyDB on tmp_path, version increments verified | [OK] |
| Census B Attribute Replacements & Census C Patches | test_lifecycle_service.py, test_override_service.py, test_stream_service.py, test_repo_deletion.py, test_system_config_service.py, test_prompt_block_service.py | Phase 4, Step 3 | Census B=0, Census C=0 across target files | [OK] |
| Service & Studio Persistence Emulation-Fake Migration | test_blueprint.py, test_execution.py, test_execution_resumability.py, test_report_service.py, test_ingress_service.py, test_output_profile_service.py, test_workflow_service.py, test_auth.py, test_usage_service.py | Phase 4, Step 4 | Census A=0, Census I=0 across target files | [OK] |
| Keyword-Injected Repository Mocks Eradication | test_execution.py, test_security.py, test_legacy_render_service.py | Phase 4, Step 5 | Census D=0 across target files | [OK] |
| Phase 4 Quality Gates, Baseline Ratchet & SDUI Parity | 23 target files across services, studio, execution & database suites | Phase 4, Step 6 | Global backend audit loop & SDUI parity pass, D ratcheted to 173 | [OK] |
| Orchestrator Fixtures Modernization & cast(Any) Eradication | test_dag_executor_atom_ceiling.py, test_dag_executor_mcp_concurrency.py, test_rag_preflight_service.py | Phase 5, Step 1 | Typed fixtures, Census X=0 | [OK] |
| Census B Attribute Replacements & Fault Injection | test_dag_executor.py, test_dag_executor_atom_ceiling.py, test_dag_executor_preflight.py, strategies/test_llm.py, test_dag_taskgroup.py | Phase 5, Step 2 | Census B=0, localized pytest passes | [OK] |
| Keyword-Injected Repository Mocks Eradication (Census D) | 14 orchestrator and strategy test files | Phase 5, Step 3 | Census D=0 across target files | [OK] |
| Orchestrator & Strategy Persistence Emulation-Fake Migration | test_dag_executor.py, test_dag_executor_atom_ceiling.py, test_dag_executor_mcp_audit.py, test_dag_executor_preflight.py, strategies/test_llm.py, strategies/test_llm_cost_tracking.py, strategies/test_logic.py, test_synthesis_distiller.py | Phase 5, Step 4 | Census A=0, Census I=0 across target files | [NOK] |
| Concurrency, Fuzzer & Logic Suites Persistence Migration | test_dag_executor_prompt_blocks.py, test_dag_taskgroup.py, test_concurrency_fuzzer.py, test_logic.py | Phase 5, Step 5 | Census A=0, Census I=0 across target files | [NOK] |
| Phase 5 Quality Gates, Baseline Ratchet & SDUI Parity | 20 target files across orchestrator, strategy, and concurrency suites | Phase 5, Step 6 | Global backend audit loop & SDUI parity pass, D ratcheted to 21 | [NOK] |

---

# Session Handover Context

## Achieved
- Formally drafted `EPIC 157: Zero Permissive Typing & Test Persistence Modernization` at `@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]`.
- Created detailed, fully verified implementation plans for Phase 1 (`@[docs/epic/tasks_EPIC_157/01_phase1_plan.md]`), Phase 2 (`@[docs/epic/tasks_EPIC_157/02_phase2_plan.md]`), Phase 3 (`@[docs/epic/tasks_EPIC_157/03_phase3_plan.md]`), Phase 4 (`@[docs/epic/tasks_EPIC_157/04_phase4_plan.md]`), and Phase 5 (`@[docs/epic/tasks_EPIC_157/05_phase5_plan.md]`).
- Successfully created `implementation_plan.md` and `task.md` system artifacts for Phase 3, Phase 4, and Phase 5.
- Successfully implemented and verified Phase 1, Phase 2, and Phase 3 (all with PASSED Tier 8 Red Team audits).
- Successfully implemented and verified Phase 4:
  - Step 4.0: Baseline persistence census probe completed (A=419, B=45, C=7, I=9 files, D=269, Fixtures=6 returning AsyncMock, Driver Mocks=1 file, Increment Version Mocks=3 files, dict_to_obj=8 occurrences).
  - Step 4.1: Modernized 6 repository fixtures returning `AsyncMock` to typed fakes (`InMemoryUnifiedWorkflowRepository`, `InMemoryWorkflowRepository`, `InMemoryOutputProfileRepository`, `InMemoryPromptBlockRepository`). Completely deleted duck-typing helper `dict_to_obj` (0 matches repo-wide via recursive regex probe). Replaced legacy fake import in `test_dependencies.py`.
  - Step 4.2: Migrated `test_repositories_v2.py` from unverified `AsyncMock(spec=StorageDriver)` to real `TinyDBDriver` on `tmp_path`, verifying stateful disk roundtrips. Migrated component repository tests (`test_agent.py`, `test_prompt_block.py`, `test_task_blueprint.py`) from `_increment_version` mock overrides to real TinyDB persistence.
  - Step 4.3: Eradicated 45 Census B attribute replacements (`<repo>.<attr> = AsyncMock(...)`) and 7 Census C object patches (`patch.object(<repo>, ...)`) across 6 target files (`test_lifecycle_service.py`, `test_override_service.py`, `test_stream_service.py`, `test_repo_deletion.py`, `test_system_config_service.py`, `test_prompt_block_service.py`), replacing them with typed in-memory stores and deterministic `repo.inject_fault()`.
  - Step 4.4: Eradicated 419 Census A assignments and Census I imports across 9 target files (`test_blueprint.py`, `test_execution.py`, `test_execution_resumability.py`, `test_report_service.py`, `test_ingress_service.py`, `test_output_profile_service.py`, `test_workflow_service.py`, `test_auth.py`, `test_usage_service.py`), seeding real domain models and snapshot fakes.
  - Step 4.5: Eradicated all 269 Census D keyword-injected repository mocks across `test_execution.py` (182), `test_security.py` (80), and `test_legacy_render_service.py` (7).
  - Step 4.6: Verified zero residual census matches on all 23 Phase 4 target files: A=0, B=0, C=0, I=0, D=0, dict_to_obj=0 (100% eradicated). Verified SDUI semantic parity (`test_sdui_semantic_parity.py`) passing in 16.50s. Ratcheted repo-wide residual debt ceilings in `scripts/audit_warning_baseline.py` monotonically: D lowered from 362 to 173 (-189, cumulative -269 from baseline), T lowered from 403 to 397 (-6), P lowered from 359 to 358 (-1). Verified 10/10 stages in global backend audit loop (`uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`) passing with 5,091 passing tests, 97.67% total test coverage, zero AST violations, and clean MyPy strict validation.
- Successfully completed Tier 0 Research & Red-Teaming for Phase 5 (`@[docs/epic/tasks_EPIC_157/05_phase5_plan.md]`):
  - Verified exact live census counts across all 20 target files: Census A=161, Census B=10, Census C=0, Census D=152, Census I=11, Census X=1, Fixtures=2.
  - Falsified potential fault injection and in-memory execution update failure modes, proving `BaseInMemoryRepository.inject_fault` decrements trigger counts cleanly and executes deterministic failure branches.
  - Aligned exact AST line bounds for all target files (specifically `test_rag_preflight_service.py#L111-L136`) and verified 100% compliance with `scripts/audit_markdown_boundaries.py` (passing with exit code 0).
  - Validated that eradicating 152 Census D mocks in Phase 5 reduces repo-wide Census D ceiling from 173 to 21, preparing the exact baseline for Phase 6.

## Learned
- Strict adherence to the 13-phase architecture requires zero permissive typing, absolute eradication of loose dicts, eradication of inline `# noqa` and `# type: ignore` suppressions, and full-duplex DTO parity with Flutter.
- In `BaseInMemoryRepository`, `self._clone(item)` provides Rust-accelerated validation/dumping for Pydantic models while safely handling `dict` instances via deep copy for negative configuration error test fixtures.
- When Census D, K, and X are eradicated from test suites, `CURRENT_RESIDUAL_CEILINGS` in `scripts/audit_warning_baseline.py` must be ratcheted down monotonically to lock in quality gains permanently (Census D ceiling lowered by 269 from 442 to 173, and Phase 5 will lower it by 152 from 173 to 21).
- In `BaseInMemoryRepository.inject_fault`, `self._check_fault(method_name)` executes at the start of each repository method before database or in-memory collection lookups, guaranteeing deterministic error injection even when entities are not pre-seeded.
- In `scripts/audit_markdown_boundaries.py`, MBD004 computes `node_start` as `min(d.lineno for d in node.decorator_list)` when decorators exist; line spans must encompass `@pytest.mark.asyncio` through the function end line.
- `InMemoryUnifiedWorkflowRepository` delegates all step methods (`get_step_by_id`, `get_step`, `save_step`, `create_step`, `seed_raw_step`) to `self._workflows` and all execution methods (`get_execution`, `update_execution`, `create_execution`) to `self._executions`, enabling single-instance injection for all 8 `StrategyDependencies` and `DAGExecutor` dependencies.

## Remaining
- Execute & Audit Phase 5 (`/tier2-execute @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`).
- Plan, Research, Execute & Audit Phases 6 through 13.

## Resume Command
/tier2-execute @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto


