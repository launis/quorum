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
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
  - [x] Step 3.0: Strategic Alignment & Persistence Census Probe
  - [x] Step 3.1: AsyncMock Fixtures & Import-Only Target Modernization
  - [ ] Step 3.2: Ad-Hoc Repository Classes & Cast(Any) Eradication (Census K & X)
  - [ ] Step 3.3: Hook Persistence Emulation-Fake Migration (Census A & B)
  - [ ] Step 3.4: LLM Client & Handler Persistence Migration (Census A)
  - [ ] Step 3.5: Keyword-Injected Repository Mocks Eradication (Census D)
  - [ ] Step 3.6: Two-Stage Testing Pipeline & Zero-Bypass Verification Gate
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
| Domain Exception Extraction to AppException Hierarchy | models/domain/base.py, core/exceptions.py, core/error_codes.py, services/orchestrator/dag_executor.py | Phase 2, Step 1 | test_domain_exceptions.py, test_dag_executor.py | [OK] |
| Hook System Permissive Type Eradication & Strict Contracts | hooks/base.py, hooks/context.py, hooks/input_processing.py, hooks/scoring.py, hooks/registry.py | Phase 2, Step 2 | test_hooks.py, audit_dict_eradication.py | [OK] |
| Provider Adapter Type Parity & Caching Contract | llm/provider.py, llm/adapters/base_adapter.py, llm/adapters/vertex_adapter.py, llm/adapters/ai_studio_adapter.py | Phase 2, Step 3 | test_vertex_adapter.py, test_ai_studio_adapter.py | [OK] |
| Core Engine Context Refactoring (No-Dict Invariant) | services/orchestrator/dag_executor.py, services/orchestrator/context_router.py, services/orchestrator/two_pass_atomizer.py | Phase 2, Step 4 | test_context_router.py, test_two_pass_atomizer.py | [OK] |
| Ingress Service & Strategy Typings | services/execution/ingress_service.py, services/execution/lifecycle_service.py, services/mcp/tavily_search_client.py | Phase 2, Step 5 | test_ingress_service.py, test_tavily_search_client.py | [OK] |
| Phase 2 Unit & Integration Test Coverage | backend_v2/tests/unit/core/, tests/unit/hooks/, tests/unit/llm/, tests/integration/ | Phase 2, Step 6 | Global backend audit loop passes | [OK] |

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
- Completed Tier 8 System 2 Post-Implementation Red Team Audit (`red_team_audit_02_phase2_plan.md`):
  - Verified 100% contract adherence across all 6 execution steps and 9 DoD checklist items.
  - Verified 10/10 Universal Quality Gate stages passed cleanly with 5,087 passing tests, 97.75% coverage, 0 AST violations, and 0 MyPy issues across 354 source files.
  - Verified SDUI semantic parity (`test_sdui_semantic_parity.py`) passed cleanly in 44.56s.
  - Phase 2 is formally signed off.
- Completed Tier 0 System 2 Research & Red-Teaming for Phase 3 (`@[docs/epic/tasks_EPIC_157/03_phase3_plan.md]`):
  - Verified baseline census probe counts mathematically across the 30 target files: A=87, B=13, C=0, I=12, D=379, K=25, X=792.
  - Discovered critical active fake instantiation in `test_structured_retry.py#L35-L37` and `test_cdata_hardening_comprehensive.py#L171`, correcting the plan from "unused import deletion" to typed replacement with `InMemoryUnifiedWorkflowRepository`.
  - Verified exact line bounds for AsyncMock repository fixtures in `test_epic66_multi_provider.py#L12-L14`, `test_handler.py#L31-L34`, and `hooks/test_interaction_hook.py#L24-L26`.
  - Confirmed `InMemoryUnifiedWorkflowRepository` implements all 15 database protocols natively and satisfies all 8 slots in `HookDependencies`.
  - Enriched fault injection protocol for `test_matrix_hook.py` using `BaseInMemoryRepository.inject_fault()` and `async with repo.fault_context():`.
  - Verified 100% pass on `scripts/audit_markdown_boundaries.py` with zero MBD001-MBD009 violations.

## Learned
- Strict adherence to the 13-phase architecture requires zero permissive typing, absolute eradication of loose dicts, eradication of inline `# noqa` and `# type: ignore` suppressions, and full-duplex DTO parity with Flutter.
- Phase 1 and Phase 2 establish the physical boundary SSOT, domain model field typings, system exception contracts, and hook/LLM typing covenants.
- Retyping `AppException.details` to `dict[str, JsonValue] | None` locks RFC 7807 serialization at the network boundary, preventing arbitrary non-serializable objects from entering Starlette response serialization.
- In `input_processing.py`, raw `ValidationError.errors()` contains non-JSON context objects; sanitizing them into primitive string dictionaries (`loc`, `msg`, `type`) guarantees JSON safety.
- Establishing `CachingPayloadResultDTO` as an immutable Pydantic V2 contract owned by `BaseLLMAdapter.prepare_caching_payload` completely eradicates anonymous tuple state transit and positional type blindness across caching workflows.
- Unifying parallel block-level nested dictionary accumulators into a single `MatrixAggregationStateDTO` eliminates Primitive Obsession while preserving strict `extra="forbid"` integrity.
- In `backend_v2/models/llm.py`, `LLMMessageDTO.content: str | list[dict[str, JsonValue]]` was introduced for Anthropic structured caching blocks; while `models/llm.py` is exempt for Metric 11 (Open-JSON), Metric 2 flags `list[dict[...]]`. A dedicated `StructuredContentBlockDTO` should be defined in a future phase to achieve zero nested dict annotations.
- Phase 3 persistence census probe verified exact occurrence counts across the 30 hook and LLM test files: 87 Census A assignments, 13 Census B attribute replacements, 0 Census C object patches, 12 Census I fake imports, 379 Census D keyword-injected mocks, 25 Census K ad-hoc classes, and 792 Census X dynamic casts.
- Replacing ad-hoc repository classes in `test_scoring.py`, `test_input_processing.py`, `test_dlq_guard.py`, `test_metadata.py`, `test_references.py`, and `test_security.py` with typed `InMemoryUnifiedWorkflowRepository` / `InMemorySystemRepository` fakes naturally eliminates all 792 `cast(Any, ...)` bypasses.
- Red-team analysis revealed that `test_structured_retry.py` and `test_cdata_hardening_comprehensive.py` actively instantiate `InMemoryBlueprintTransformerRepository` rather than merely importing it; treating them as "unused import removal" would have broken tests with `NameError`. They must be migrated to `InMemoryUnifiedWorkflowRepository`.
- `BaseInMemoryRepository` natively provides `inject_fault(method_name, exception, trigger_count)` and `async with fault_context(...)`, which provides a 100% typed, deterministic alternative to monkeypatching `.side_effect` or overwriting methods with `AsyncMock`.

## Remaining
- Execute Phase 3: `/tier2-execute @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`
- Audit Phase 3: `/tier8-audit-plan @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md]`
- Plan, Research, Execute & Audit Phases 4 through 13.

## Resume Command
/tier2-execute @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto
