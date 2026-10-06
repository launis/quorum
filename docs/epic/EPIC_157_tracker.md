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
| Domain Exception Extraction to AppException Hierarchy | models/domain/base.py, core/exceptions.py, core/error_codes.py, services/orchestrator/dag_executor.py | Phase 2, Step 1 | test_domain_exceptions.py, test_dag_executor.py | [OK] |
| Hook System Permissive Type Eradication & Strict Contracts | hooks/base.py, hooks/context.py, hooks/input_processing.py, hooks/scoring.py, hooks/registry.py | Phase 2, Step 2 | test_hooks.py, audit_dict_eradication.py | [OK] |
| Provider Adapter Type Parity & Caching Contract | llm/provider.py, llm/adapters/base_adapter.py, llm/adapters/vertex_adapter.py, llm/adapters/ai_studio_adapter.py | Phase 2, Step 3 | test_vertex_adapter.py, test_ai_studio_adapter.py | [OK] |
| Core Engine Context Refactoring (No-Dict Invariant) | services/orchestrator/dag_executor.py, services/orchestrator/context_router.py, services/orchestrator/two_pass_atomizer.py | Phase 2, Step 4 | test_context_router.py, test_two_pass_atomizer.py | [OK] |
| Ingress Service & Strategy Typings | services/execution/ingress_service.py, services/execution/lifecycle_service.py, services/mcp/tavily_search_client.py | Phase 2, Step 5 | test_ingress_service.py, test_tavily_search_client.py | [OK] |
| Phase 2 Unit & Integration Test Coverage | backend_v2/tests/unit/core/, tests/unit/hooks/, tests/unit/llm/, tests/integration/ | Phase 2, Step 6 | Global backend audit loop passes | [OK] |
| Hook Persistence Emulation-Fake Migration | backend_v2/tests/unit/hooks/test_archival.py, test_atom_flattening.py, test_atom_sampling_determinism.py, test_integrity.py, test_matrix_hook.py, test_passivity_hook.py | Phase 3, Step 3 | Census A=0, B=0, localized pytest passes | [OK] |
| LLM Client & Handler Persistence Migration | backend_v2/tests/unit/llm/test_client.py, test_llm_client_tiers.py, test_handler.py, test_llm_context_bounds.py | Phase 3, Step 4 | Census A=0, I=0, localized pytest passes | [OK] |
| Ad-Hoc Repository Classes & Cast(Any) Eradication | backend_v2/tests/unit/hooks/test_scoring.py, test_input_processing.py, test_dlq_guard.py, test_metadata.py, test_references.py, test_security.py | Phase 3, Step 2 | Census K=0, X=0, localized pytest passes | [OK] |
| Keyword-Injected Repository Mocks Eradication | backend_v2/tests/unit/hooks/test_validation.py, test_source_verification_hook.py, test_linguistics.py, test_metadata.py, test_metrics.py, test_references.py, test_synthesis_distiller_hook.py, test_hook_registry.py, test_google_providers_separation.py | Phase 3, Step 5 | Census D=0, localized pytest passes | [OK] |
| Phase 3 Test Persistence Migration Quality Gates | 30 Hook and LLM test files across backend_v2/tests/unit/ | Phase 3, Step 6 | Global backend audit loop & SDUI parity pass | [OK] |

---

# Session Handover Context

## Achieved
- Formally drafted `EPIC 157: Zero Permissive Typing & Test Persistence Modernization` at `@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]`.
- Created detailed, fully verified implementation plans for Phase 1 (`@[docs/epic/tasks_EPIC_157/01_phase1_plan.md]`), Phase 2 (`@[docs/epic/tasks_EPIC_157/02_phase2_plan.md]`), and Phase 3 (`@[docs/epic/tasks_EPIC_157/03_phase3_plan.md]`).
- Successfully created `implementation_plan.md` and `task.md` system artifacts for Phase 3.
- Verified 100% boundary pass rates on `docs/epic/tasks_EPIC_157/03_phase3_plan.md` via `scripts/audit_markdown_boundaries.py`.
- Successfully implemented and verified Phase 1: established `BOUNDARY_EXEMPTION_FILES` SSOT, created `ResidualDebtCeilingsDTO`, implemented `QGR026`, retyped 30 model violations, and signed off Tier 8 audit (`red_team_audit_01_phase1_plan.md`).
- Successfully implemented and verified Phase 2:
  - Retyped `AppException.details` to `dict[str, JsonValue] | None` and implemented RFC 7807 `ProblemDetailDTO` with `.model_dump(mode="json", exclude_none=True)` serialization at FastAPI boundaries (`main.py`, `core/rate_limit.py`).
  - Sanitized exception caller details (sanitizing `ValidationError.errors()` in `input_processing.py` to JSON primitives).
  - Refactored `prepare_caching_payload` across `BaseLLMAdapter`, `LLMCachingService`, and all 6 adapters (`vertex_adapter.py`, `ai_studio_adapter.py`, `anthropic_adapter.py`, `openai_adapter.py`, `mock_adapter.py`) to return `CachingPayloadResultDTO`, eliminating anonymous tuples.
  - Consolidated parallel matrix hook accumulator maps into `MatrixAggregationStateDTO` and eliminated `judge_model: dict[str, Any]` in `passivity_hook.py`.
  - Defined `LinguisticAnalysisDTO` in `hooks/linguistics.py` and retyped source verification payloads.
  - Strongly typed dynamic Pydantic model fields in `core/registry.py` and `schema_builder.py` via `DynamicFieldDefinition`, retyped `MOCK_REGISTRY` to `dict[type[BaseModel], BaseModel]`, and retyped `get_fallback_data` / `parse_llm_output` to `dict[str, JsonValue]`.
- Successfully implemented and verified Phase 3:
  - Step 3.0: Baseline census probe completed (A=87, B=13, C=0, I=12, D=379, K=25, X=792).
  - Step 3.1: Modernized AsyncMock fixtures and repository fakes across `test_epic66_multi_provider.py`, `test_handler.py`, `hooks/test_interaction_hook.py`, `test_structured_retry.py`, and `test_cdata_hardening_comprehensive.py`.
  - Step 3.2: Completely eradicated all 25 ad-hoc repository classes (Census K) and all 792 `cast(Any, ...)` bypasses (Census X) across `test_scoring.py`, `hooks/test_input_processing.py`, `test_input_processing.py`, `hooks/test_dlq_guard.py`, `hooks/test_metadata.py`, `hooks/test_references.py`, and `hooks/test_security.py`.
  - Step 3.3: Migrated hook persistence emulation fakes (Census A & B) across `test_archival.py`, `test_atom_flattening.py`, `test_atom_sampling_determinism.py`, `test_integrity.py`, `test_matrix_hook.py`, and `test_passivity_hook.py`.
  - Step 3.4: Migrated LLM client and handler persistence (Census A & I) across `test_client.py`, `test_llm_client_tiers.py`, `test_handler.py`, and `test_llm_context_bounds.py`.
  - Step 3.5: Completely eradicated all 379 keyword-injected repository mocks (Census D) across `test_hook_registry.py`, `test_synthesis_distiller_hook.py`, `test_metadata.py`, `test_validation.py`, `test_google_providers_separation.py`, `test_references.py`, `test_metrics.py`, `test_linguistics.py`, and `test_source_verification_hook.py`.
  - Step 3.6: Verified zero residual census matches on all 30 target files: A=0, B=0, C=0, I=0, D=0, K=0, X=0 (100% eradicated). Verified 10/10 stages in global backend audit loop (`uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`) passing with 5,091 passing tests, 97.75% coverage, zero AST violations, and clean SDUI semantic parity (`test_sdui_semantic_parity.py`). Ratcheted residual debt ceilings down to new repo-wide lows (d=442, k=0, x=14, t=406, p=362).

## Learned
- Strict adherence to the 13-phase architecture requires zero permissive typing, absolute eradication of loose dicts, eradication of inline `# noqa` and `# type: ignore` suppressions, and full-duplex DTO parity with Flutter.
- In `BaseInMemoryRepository`, `self._clone(item)` provides Rust-accelerated validation/dumping for Pydantic models while safely handling `dict` instances via deep copy for negative configuration error test fixtures.
- When Census D, K, and X are eradicated from test suites, `CURRENT_RESIDUAL_CEILINGS` in `scripts/audit_warning_baseline.py` must be ratcheted down monotonically to lock in quality gains permanently.
- Never add `# type: ignore` comments in test files (specifically: `test_source_verification_hook.py`); instead construct valid typed inputs (specifically: `ExecutionInputsDTO(raw_inputs={...}, target_locale="fi")`) to protect the Census T ceiling.

## Remaining
- Audit Phase 3: `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- Plan, Research, Execute & Audit Phases 4 through 13.

## Resume Command
/tier8-audit-plan @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md]
