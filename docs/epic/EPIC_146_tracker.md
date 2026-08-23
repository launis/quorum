# EPIC 146 Tracker: Unified Prompt Orchestration and Cognitive Harmonization

**Epic:** @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]
**Task Directory:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization]

```xml
<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <ki>@[ki_god_code_prevention.md]</ki>
  <ki>@[ki_ast_guardrail_testing.md]</ki>
  <ki>@[ki_global_config_sovereignty.md]</ki>
  <ki>@[ki_python_314_concurrency_strictness.md]</ki>
  <ki>@[ki_llm_extraction_architecture.md]</ki>
  <ki>@[ki_workflow_context_governance.md]</ki>
  <ki>@[ki_sdui_matrix_synthesis.md]</ki>
  <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
  <ki>@[ki_dual_axis_localization_architecture.md]</ki>
  <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  <ki>@[ki_epic_lifecycle_workflow.md]</ki>
  <ki>@[ki_synthesis_payload_compression.md]</ki>
  <ki>@[ki_context_enriched_pipeline.md]</ki>
  <ki>@[ki_strict_sdui_serialization.md]</ki>
  <ki>@[ki_polymorphic_rule_routing.md]</ki>
  <ki>@[ki_sdui_adapter_pattern.md]</ki>
  <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
  <ki>@[ki_deterministic_hardening_state.md]</ki>
  <ki>@[ki_ai_testing_standards.md]</ki>
</required_context_rules>
```

---

## Phase Execution Status

### Phase 1: Pre-Requisite Technical Debt Cleanups & AST Guardrails (Backend & Frontend)

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md]
**Plan (Frontend):** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\02_phase1_frontend_tech_debt_cleanups.md]

- [ ] **[NOK] Red-Teaming (Backend):** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution (Backend):** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify simulation service, test_tier4_schema_bug.py, and test_schema_builder.py
  - [ ] Step 1: Simulation Service Technical Debt Cleanup — Eliminate duck typing `getattr(claim, 'ai_description', None)` and lazy fallback `rendered = data.ai_description or ""` in simulation_service.py
  - [ ] Step 2: Unit Test Fixtures Remediation — Un-skip and fix test_tier4_schema_bug.py (adapt fixture to plain string with >= 10 chars, remove `ai_description`), verify test_schema_builder.py
  - [ ] Step 3: AST and Seed Guardrail Suite Creation — Implement 9 AST and seed guardrails in test_ast_matrix_claim_guardrails.py
- [ ] **[NOK] Red-Teaming (Frontend):** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\02_phase1_frontend_tech_debt_cleanups.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution (Frontend):** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\02_phase1_frontend_tech_debt_cleanups.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify step_builder_view.dart, router.dart, and prompt_block_builder_view.dart
  - [ ] Step 1: Step Builder View & Router Cleanups — Replace dynamic step typing with stepId, remove GoRouter extra passing, switch pattern matching, eradicate SizedBox.shrink and translation fallback chains
  - [ ] Step 2: Prompt Block Builder View Cleanups — Eliminate hardcoded hex color `Color(0xFF2E7D32)`, inlined language ternary, hardcoded tooltips, fallback chains, and timestamp ID generator
  - [ ] Step 3: Modals & Components Hygiene — Migrate hardcoded strings to ARB localizations, replace ad-hoc UUIDs with TDAAssertion.create(), and replace spacing doubles with AppSpacing
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit (Backend):** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Audit (Frontend):** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\02_phase1_frontend_tech_debt_cleanups.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 2: Seed Data Migration & Vault Mutation (Verification-Only)

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify seed_data.json baseline state
  - [ ] Step 1: Seed Verification Script Execution — Execute read-only Python script verifying 0 claim ai_description keys and 152 valid assertion concept_description strings
  - [ ] Step 2: Seed Integrity Validation & Database Reseeding — Validate JSON schema integrity and execute database re-seeding via `uv run python backend_v2/seed/run_seed.py local`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 3: Backend Domain & Service Harmonization (and Test Fixtures Harmonization)

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify settings.py and v2_core.py baseline state
  - [ ] Step 1: Settings & Domain Model Updates — Define tda_concept_min_length: 10, update TDAAssertion.concept_description with StringConstraints(min_length=10), eradicate ai_description from MatrixClaim, and translate Finnish messages to English
  - [ ] Step 2: Prompt Builders & Hooks Verification — Verify atom_flattening.py concept_description usage and enforce Fail-Fast validation on empty assertion.question in matrix_sensor_prompt_builder.py
  - [ ] Step 3: Test Fixture Harmonization — Atomically modernize mock claim fixtures across 23 backend test files and 1 frontend test file
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 4: Flutter Studio Client Harmonization

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify enums.dart and prompt_block.dart baseline state
  - [ ] Step 1: Centralized Enums & Freezed Models Update — Add SystemUiConstraints.tdaConceptMinLength(10), remove aiDescription from MatrixClaim Freezed model, enforce 32 hex char tdaId format, and run code generation
  - [ ] Step 2: Studio Views Alignment & Modal Hygiene — Align scale editor modal, row editor modal, BARS matrix builder, and prompt block builder view with updated models
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md]

- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md] --phase=6`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify Wave 1 baseline in prompt_factory.py, matrix_sensor_prompt_builder.py, and localization_compiler.py
  - [ ] Step 1: Global Mandates Static Prefix Migration — Inject GLOBAL_MANDATES_XML into Layer 1 base_system_prompt static prefix in prompt_factory.py and matrix_sensor_prompt_builder.py
  - [ ] Step 2: Compiler Refactoring & Anti-Pattern Demolition — Replace find_value_by_key and hasattr/getattr with MechanicalAnchorsPayload DTO, eradicate 7 get fallback chains via ExecutionTimeResolver, and replace localization compiler fallback with Fail-Fast validation
  - [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 7: Polymorphic AnyPromptBlock Discriminated Union & AST Guardrails

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md]

- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md] --phase=7`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify Phase 6 compiler baseline
  - [ ] Step 1: Pydantic Discriminated Union Creation — Create AnyPromptBlock polymorphic union in backend_v2/models/domain/prompt_blocks.py, eradicate monolithic PromptBlock and pre_validate_block_consistency in v2_core.py, and update seed_registry.py
  - [ ] Step 2: Flutter Freezed Sealed Class Synchronous Parity — Refactor Dart PromptBlock to sealed union class with Freezed unionKey: categoryId and run build runner
  - [ ] Step 3: AST XML Sovereignty Guardrails — Implement 10 static AST tests in test_ast_prompt_xml_sovereignty.py
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 8: Clean Stack Compiler Layer Assembly

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md]

- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md] --phase=8`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify Phase 7 domain models baseline
  - [ ] Step 1: Polymorphic Compiler Dispatch Implementation — Update prompt_factory.py, localization_compiler.py, simulation_service.py, and matrix_sensor_prompt_builder.py to dispatch via pattern matching and assemble Zero-XML fields into XML tags
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 9: Flutter Studio Zero-XML UI Modernization

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md]

- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md] --phase=9`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify Phase 8 compiler baseline
  - [ ] Step 1: Zero-XML UI Forms & View Alignment — Update prompt_block_builder_view.dart with Dart 3 switch destructuring for Zero-XML fields, streamline step criteria block selection, and add ARB localizations
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 10: Seed Vault Pruning & Database Reseeding

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md]

- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md] --phase=10`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify Phase 9 UI baseline
  - [ ] Step 1: Vault Pruning & Reseeding — Run Python audit in scratch, prune redundant global mandate block IDs from criteria_block_ids in seed_data.json, fix corrupted HTML entity, and reseed database
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 11: End-to-End Live Integration Verification Gate & Knowledge Synchronization

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md]

- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md] @[docs\epic\EPIC_146_tracker.md] --phase=11`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md] @[docs\epic\EPIC_146_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md] @[docs\epic\EPIC_146_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check — Verify Phase 10 reseeded database baseline
  - [ ] Step 1: Live LLM Verification & Knowledge Synchronization — Execute live LLM E2E integration test gate, update ki_llm_extraction_architecture.md, and synchronize 05_llm_architecture.md rules
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation

- [ ] **[NOK]** Backend full audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **[NOK]** Frontend full audit: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
- [ ] **[NOK]** Domain Parity Gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test`
- [ ] **[NOK]** Seed Integrity Gate: `uv run python backend_v2/seed/run_seed.py local`

---

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths and delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified backend production files:
  - [ ] @[backend_v2/hooks/atom_flattening.py]
  - [ ] @[backend_v2/models/domain/prompt_blocks.py]
  - [ ] @[backend_v2/models/prompts/global_mandates.py]
  - [ ] @[backend_v2/models/v2_core.py]
  - [ ] @[backend_v2/seed/seed_registry.py]
  - [ ] @[backend_v2/services/orchestrator/localization_compiler.py]
  - [ ] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]
  - [ ] @[backend_v2/services/studio/simulation_service.py]
  - [ ] @[backend_v2/settings.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified frontend production files:
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
  - [ ] @[client_app_v2/lib/router/router.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain across backend and frontend codebases.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

---

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, create/update relevant Knowledge Items (KIs), and update `.agents/rules/04_directory_reference.md`.

---

### Final Epic Audit

- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Atomic Commits & Quality Gates**:
   - You MUST strictly follow the Zero-Tolerance Audit Loop.
   - After completing each step in a plan, run the localized quality loop:
     - Python: `uv run python scripts/backend_audit_loop.py <target_path> --test`
     - Flutter: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
   - Instruct the user to make an atomic git commit after every passing audit.

2. **Seeding Environment Mandate**:
   - When running seed scripts, ALWAYS pass the explicit `local` environment parameter: `uv run python backend_v2/seed/run_seed.py local`.
   - Never run raw seed execution without the environment argument.

3. **Workspace Relative References**:
   - All file references MUST use `@-reference` syntax (e.g. `@[backend_v2/models/v2_core.py]`).
   - For Knowledge Items, use relative filename syntax (e.g. `@[ki_god_code_prevention.md]`).

4. **Workflow Execution Pipeline**:
   - The mandatory workflow loop for deferred phases is: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`.
   - You MUST pass BOTH the plan file and tracker file in ALL commands (e.g. `/tier0-research-plan @[path_to_plan.md] @[docs\epic\EPIC_146_tracker.md]`).
   - Once all phases are executed and audited, proceed through the Post-Implementation Gates:
     `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.
   - Whenever completing a session or handing over, automatically output the next resume command in your chat response. Note that context rules are self-hydrating from `<required_context_rules>` blocks; `--rules` flag is not needed.

---

## Requirements Traceability Matrix

| Requirement ID | Epic Section | Technical Specification & Scope | Mapped Plan & Step | Verification & Gate |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-146-01** | Section 1.1, 2.1 | Eliminate duck typing `getattr(claim, 'ai_description', None)` and lazy fallback `rendered = data.ai_description or ""` in simulation service. | Phase 1, Step 1 | `backend_audit_loop.py simulation_service.py` |
| **REQ-146-02** | Section 2.1, 3.1 | Eradicate `final dynamic step;` and GoRouter `$extra` object passing in `StepBuilderView`, routing purely by `stepId`. | Phase 1, Step 1 | `flutter_audit_loop.py step_builder_view.dart` |
| **REQ-146-03** | Section 2.1, 3.1 | Replace `formState.when(...)` with Dart 3 native `switch (formState)` pattern matching and eradicate `SizedBox.shrink()` in `StepBuilderView`. | Phase 1, Step 1 | `flutter_audit_loop.py step_builder_view.dart` |
| **REQ-146-04** | Section 2.1, 3.1 | Replace translation fallback chains `translations[currentLocale] ?? translations['fi'] ?? ...` with Fail-Fast `AppException.validation`. | Phase 1, Step 1 | `flutter_audit_loop.py step_builder_view.dart` |
| **REQ-146-05** | Section 2.1, 3.1 | Un-skip and fix broken test fixture in `test_tier4_schema_bug.py` (adapt fixture to plain string with >= 10 chars, remove `ai_description`) and verify `test_schema_builder.py`. | Phase 1, Step 2 | `pytest test_tier4_schema_bug.py` |
| **REQ-146-06** | Section 2.1, 3.1 | Eradicate hardcoded hex color `const Color(0xFF2E7D32)` in `PromptBlockBuilderView`, replacing with `Theme.of(context).colorScheme.primaryContainer`. | Phase 1, Step 2 | `flutter_audit_loop.py prompt_block_builder_view.dart` |
| **REQ-146-07** | Section 2.1, 3.1 | Migrate inlined language ternaries and hardcoded tooltips in `PromptBlockBuilderView` to `.arb` localizations (`l10n.matrixCategoryLockedHelper`). | Phase 1, Step 2 | `flutter gen-l10n` |
| **REQ-146-08** | Section 2.1, 3.1 | Eradicate timestamp ID generation (`blk_${DateTime.now()...}`) in `PromptBlockBuilderView`, replacing with standard UUID generator. | Phase 1, Step 2 | `flutter_audit_loop.py prompt_block_builder_view.dart` |
| **REQ-146-09** | Section 2.1, 3.1 | Establish 9 AST and seed guardrail tests in `test_ast_matrix_claim_guardrails.py` enforcing 0 `ai_description` on claims, `len >= 10` on assertions, AST model purity, and negative AST scans. | Phase 1, Step 3 | `pytest test_ast_matrix_claim_guardrails.py` |
| **REQ-146-10** | Section 2.1, 3.1 | Migrate hardcoded strings in `scale_editor_modal.dart` and `row_editor_modal.dart` to ARB, replace ad-hoc UUIDs with `TDAAssertion.create()`, and replace spacing doubles with `AppSpacing`. | Phase 1, Step 3 | `flutter_audit_loop.py scale_editor_modal.dart` |
| **REQ-146-11** | Section 2.1, 3.1 | Replace magic spacing doubles in `bars_matrix_builder.dart` with `AppSpacing` design tokens. | Phase 1, Step 3 | `flutter_audit_loop.py bars_matrix_builder.dart` |
| **REQ-146-12** | Section 2.1, 3.2 | Execute read-only verification script in `scratch/` proving 0 claim `ai_description` keys and 152 valid assertion `concept_description` strings in `seed_data.json`. | Phase 2, Step 1 | `scratch/verify_seed.py` |
| **REQ-146-13** | Section 2.1, 3.2 | Validate schema integrity of `seed_data.json` and execute clean-slate database re-seeding via `run_seed.py local`. | Phase 2, Step 2 | `uv run python backend_v2/seed/run_seed.py local` |
| **REQ-146-14** | Section 2.2, 3.3 | Define `tda_concept_min_length: 10` in `backend_v2/settings.py` and enforce `StringConstraints(strip_whitespace=True, min_length=10)` on `TDAAssertion.concept_description` in `v2_core.py`. | Phase 3, Step 1 | `backend_audit_loop.py settings.py` |
| **REQ-146-15** | Section 2.1, 3.3 | Permanently eradicate `ai_description` field from `MatrixClaim` in `backend_v2/models/v2_core.py`, retaining only `label: I18nText` and `tda_assertions: list[TDAAssertion]`. | Phase 3, Step 1 | `backend_audit_loop.py v2_core.py` |
| **REQ-146-16** | Section 2.1, 3.3 | Translate Finnish error messages and historical comments in `v2_core.py` to English present-tense descriptions. | Phase 3, Step 1 | `backend_audit_loop.py v2_core.py` |
| **REQ-146-17** | Section 2.2, 3.3 | Verify `atom_flattening.py` utilizes `tda.concept_description.strip()`. | Phase 3, Step 2 | `pytest test_atom_flattening.py` |
| **REQ-146-18** | Section 2.1, 3.3 | Enforce Fail-Fast exception with RFC 7807 structured logging if `assertion.question` is empty in `matrix_sensor_prompt_builder.py`. | Phase 3, Step 2 | `pytest test_matrix_sensor_prompt_builder.py` |
| **REQ-146-19** | Section 3.3, 3.5 | Atomically modernize mock claim fixtures across 23 backend test files (updating 39 short concept strings to >= 10 chars and removing `ai_description`) and 1 frontend test file. | Phase 3, Step 3 | `backend_audit_loop.py backend_v2 --test` |
| **REQ-146-20** | Section 2.3, 3.4 | Add `tdaConceptMinLength(10)` to `SystemUiConstraints` in `enums.dart` and remove `aiDescription` from `MatrixClaim` Freezed model in `prompt_block.dart`. | Phase 4, Step 1 | `flutter_audit_loop.py enums.dart` |
| **REQ-146-21** | Section 2.3, 3.4 | Update `TDAAssertion.create` factory in `prompt_block.dart` to generate 32 hex chars (`tda_$uuidHex`), matching backend regex `^tda_[a-f0-9]{32}$`. | Phase 4, Step 1 | `flutter_audit_loop.py prompt_block.dart --build` |
| **REQ-146-22** | Section 2.1, 3.4 | Update `scale_editor_modal.dart`, `row_editor_modal.dart`, `bars_matrix_builder.dart`, and `prompt_block_builder_view.dart` to route editing to `conceptDescription` and enforce min length validator. | Phase 4, Step 2 | `flutter_audit_loop.py bars_matrix_builder.dart` |
| **REQ-146-23** | Section 2.3, 3.6 | Remove `GLOBAL_MANDATES_XML` from user payload and inject into Layer 1 of `base_system_prompt` static caching prefix in `prompt_factory.py` and `matrix_sensor_prompt_builder.py`. | Phase 6, Step 1 | `backend_audit_loop.py prompt_factory.py` |
| **REQ-146-24** | Section 2.1, 3.6 | Eradicate `find_value_by_key` reflection loop and all `hasattr`/`getattr` calls in `prompt_factory.py`, replacing with typed `MechanicalAnchorsPayload` Pydantic model. | Phase 6, Step 2 | `backend_audit_loop.py prompt_factory.py` |
| **REQ-146-25** | Section 2.1, 3.6 | Eliminate hardcoded slug checks in `prompt_factory.py` (replace with polymorphic `isinstance(block, MatrixPromptBlock)`). | Phase 6, Step 2 | `backend_audit_loop.py prompt_factory.py` |
| **REQ-146-26** | Section 2.1, 3.6 | Eradicate 7 `.get()` fallback chains for `execution_time` via `ExecutionTimeResolver` pure function in `prompt_factory.py`. | Phase 6, Step 2 | `backend_audit_loop.py prompt_factory.py` |
| **REQ-146-27** | Section 2.1, 3.6 | Replace `LANGUAGE_NAMES.get(..., "English")` lazy fallback in `localization_compiler.py` with Fail-Fast `AppException(VALIDATION_FAILED)`. | Phase 6, Step 2 | `backend_audit_loop.py localization_compiler.py` |
| **REQ-146-28** | Section 2.1, 3.7 | Create polymorphic Discriminated Union `AnyPromptBlock` in `backend_v2/models/domain/prompt_blocks.py` with `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock`. | Phase 7, Step 1 | `backend_audit_loop.py prompt_blocks.py` |
| **REQ-146-29** | Section 2.1, 3.7 | Eradicate monolithic `PromptBlock` and runtime duck-typing validator `pre_validate_block_consistency` from `v2_core.py`, and map `"prompt_blocks"` to `TypeAdapter(AnyPromptBlock)` in `seed_registry.py`. | Phase 7, Step 1 | `backend_audit_loop.py v2_core.py` |
| **REQ-146-30** | Section 2.3, 3.7 | Refactor Dart `PromptBlock` to sealed union class with `@Freezed(unionKey: 'categoryId', equal: false)` and run Freezed code generation. | Phase 7, Step 2 | `flutter_audit_loop.py prompt_block.dart --build` |
| **REQ-146-31** | Section 2.3, 3.7 | Establish 10 static AST guardrail tests in `test_ast_prompt_xml_sovereignty.py` verifying strict models, discriminator usage, zero reflection, zero slug checks, and XML ordering. | Phase 7, Step 3 | `pytest test_ast_prompt_xml_sovereignty.py` |
| **REQ-146-32** | Section 2.1, 3.8 | Update `prompt_factory.py`, `localization_compiler.py`, and `simulation_service.py` to use polymorphic `match block:` dispatching to extract discrete instruction fields. | Phase 8, Step 1 | `backend_audit_loop.py prompt_factory.py` |
| **REQ-146-33** | Section 2.1, 3.8 | Update `matrix_sensor_prompt_builder.py` to compile Zero-XML fields (`objective`, `evaluation_rules`, `banned_concepts`) into XML tags and wrap theory citation into `<theory_context>` without `source_url`. | Phase 8, Step 1 | `backend_audit_loop.py matrix_sensor_prompt_builder.py` |
| **REQ-146-34** | Section 2.1, 3.9 | Update `prompt_block_builder_view.dart` using Dart 3 pattern matching to render Zero-XML structured form inputs (Objective, Evaluation Rules list, Banned Concepts list, Role Enforcement, Compiled Preview). | Phase 9, Step 1 | `flutter_audit_loop.py prompt_block_builder_view.dart` |
| **REQ-146-35** | Section 2.1, 3.9 | Streamline step criteria block selection in `step_builder_view.dart` and add localization keys in `app_en.arb` and `app_fi.arb`. | Phase 9, Step 1 | `flutter_audit_loop.py step_builder_view.dart --build` |
| **REQ-146-36** | Section 2.1, 3.10 | Execute Python redundancy verification script in `scratch/` proving candidate blocks are covered by `GLOBAL_MANDATES_XML`. | Phase 10, Step 1 | `scratch/verify_redundancy.py` |
| **REQ-146-37** | Section 2.1, 3.10 | Prune 27 redundant global mandate block IDs from `criteria_block_ids` in `seed_data.json` and fix corrupted HTML entity `&lt;mechanical_anchors&gt;` -> `<mechanical_anchors>`. | Phase 10, Step 1 | `backend_audit_loop.py seed_data.json` |
| **REQ-146-38** | Section 2.1, 3.10 | Execute database re-seeding via `uv run python backend_v2/seed/run_seed.py local`. | Phase 10, Step 1 | `uv run python backend_v2/seed/run_seed.py local` |
| **REQ-146-39** | Section 3.11, 4.4 | Execute mandatory live LLM E2E REST API integration test verification gate (`$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`). | Phase 11, Step 1 | `pytest test_epic_chain_e2e.py` |
| **REQ-146-40** | Section 3.11, 5.0 | Update Knowledge Item `ki_llm_extraction_architecture.md` with Zero-XML UI paradigm and 4-Layer Clean Stack Model specification, and synchronize `.agents/rules/05_llm_architecture.md`. | Phase 11, Step 1 | `tier7-describe-architecture` |

---

# Session Handover Context

## Achieved
- Completed Tier 1 Planning and Tracker Generation for Epic 146: Unified Prompt Orchestration and Cognitive Harmonization.
- Generated comprehensive implementation sub-plans for all 11 phases across Wave 1 (TDA Assertion SSOT) and Wave 2 (Zero-XML UI & Clean Stack Prompt Engine) in `docs/epic/tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization/`.
- Verified and aligned `audit_tracker_output.py` structural auditor to ensure bidirectional mapping between Requirements Traceability Matrix and sub-plan step IDs.
- Generated the official `EPIC_146_tracker.md` document containing full phase execution statuses, granular file-level hardening checklists, instructions for execution agents, and 40-row Requirements Traceability Matrix.

## Learned
- **Baseline Codebase State Snapshot**:
  - `seed_data.json` already has 0 `ai_description` keys on claims and 0 redundant global mandate block IDs in persistence, making Phase 2 verification-only.
  - `MatrixClaim.ai_description` in `backend_v2/models/v2_core.py` and `MatrixClaim.aiDescription` in `client_app_v2/lib/features/studio/models/prompt_block.dart` are still physically present in domain code and must be cleanly eradicated in Phases 3 and 4.
  - `GLOBAL_MANDATES_XML` is already centralized in `backend_v2/models/prompts/global_mandates.py` with 11 system mandates, but is currently injected into the dynamic user payload (`exec_params`) in `prompt_factory.py`; Wave 2 will migrate it into the Layer 1 static caching prefix.
  - `PromptBlock` is currently a monolithic class with optional catch-all fields and runtime duck-typing validation (`pre_validate_block_consistency`) in `v2_core.py`; Phase 7 will decompose it into a clean `AnyPromptBlock` discriminated union with `Field(discriminator='category_id')`.

## Remaining
- Execute Phase 1: Pre-Requisite Technical Debt Cleanups & AST Guardrails (Backend & Frontend) via `/tier0-research-plan`.

## Resume Command
`/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
