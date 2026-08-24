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

- [x] **[OK] Red-Teaming (Backend):** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution (Backend):** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify simulation service, test_tier4_schema_bug.py, and test_schema_builder.py
  - [x] Step 1: Simulation Service Technical Debt Cleanup — Eliminate duck typing `getattr(claim, 'ai_description', None)`, lazy fallback `rendered = data.ai_description or ""`, and raw dict `translations.get` in simulation_service.py
  - [x] Step 2: Unit Test Fixtures Remediation — Un-skip and fix test_tier4_schema_bug.py (adapt fixture to plain string with >= 10 chars, retain valid `ai_description` until Phase 3), verify test_schema_builder.py
  - [x] Step 3: AST and Seed Guardrail Suite Creation — Implement 9 AST and seed guardrails in test_ast_matrix_claim_guardrails.py with live Phase 1 checks, negative mock tests, and aspirational anchors
- [x] **[OK] Red-Teaming (Frontend):** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\02_phase1_frontend_tech_debt_cleanups.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution (Frontend):** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\02_phase1_frontend_tech_debt_cleanups.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify step_builder_view.dart, router.dart, and prompt_block_builder_view.dart
  - [x] Step 1: Step Builder View & Router Cleanups — Replace dynamic step typing with stepId, remove GoRouter extra passing, switch pattern matching, eradicate SizedBox.shrink and translation fallback chains
  - [x] Step 2: Prompt Block Builder View Cleanups — Eliminate hardcoded hex color `Color(0xFF2E7D32)`, inlined language ternary, hardcoded tooltips, fallback chains, and timestamp ID generator
  - [x] Step 3: Modals & Components Hygiene — Migrate hardcoded strings to ARB localizations, replace ad-hoc UUIDs with TDAAssertion.create(), and replace spacing doubles with AppSpacing
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit (Backend):** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\01_phase1_backend_tech_debt_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Audit (Frontend):** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\02_phase1_frontend_tech_debt_cleanups.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 2: Seed Data Migration & Vault Mutation

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md]

- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify seed_data.json baseline state
  - [x] Step 1: Seed Vault Backup — Create timestamped backup in backend_v2/seed/backups/
  - [x] Step 2: Seed Data Vault Migration — Copy 70 missing concept_description values from claim.ai_description and eradicate ai_description from all 152 MatrixClaims
  - [x] Step 3: Seed Verification & AST Guardrail Verification — Verify 0 claim ai_description keys, 152 valid concept_descriptions (len >= 10), and run un-skipped AST guardrail seed tests
  - [x] Step 4: Seed Integrity Validation & Database Reseeding — Validate JSON schema integrity and verify seed migration (database re-seeding verified pending Phase 3 domain model update)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\03_phase2_seed_data_verification_and_reseed.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 3: Backend Domain & Service Harmonization (and Test Fixtures Harmonization)

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md]

- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify settings.py and v2_core.py baseline state
  - [x] Step 1: Settings & Domain Model Updates — Define tda_concept_min_length: 10, update TDAAssertion.concept_description with StringConstraints(min_length=10), eradicate ai_description from MatrixClaim, and translate Finnish messages to English
  - [x] Step 2: Prompt Builders & Hooks Verification — Verify atom_flattening.py concept_description usage and enforce Fail-Fast validation on empty assertion.question in matrix_sensor_prompt_builder.py
  - [x] Step 3: Test Fixture Harmonization & AST Guardrail Activation — Atomically modernize mock claim fixtures across 24 backend test files, un-skip 3 AST guardrail tests, and add empty question anti-happy-path test
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\04_placeholder_phase3_backend_domain_and_service_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 4: Flutter Studio Client Harmonization

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md]

- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify backend models baseline and prompt_block.dart
  - [x] Step 1: Pre-Implementation Technical Debt Cleanups & ARB Localization Setup — Add tdaConceptMinLengthError, helper texts to ARB, compile l10n, and clean magic numbers with AppSpacing
  - [x] Step 2: Centralized Enums & Freezed Models Update — Add SystemUiConstraints.tdaConceptMinLength(10), remove aiDescription from MatrixClaim, enforce 32 hex char tdaId format, and run code generation
  - [x] Step 3: Studio Views Alignment & Modal Modernization — Align scale editor modal, row editor modal, BARS matrix builder, and prompt block builder view with updated models
  - [x] Step 4: Unit Test Modernization & ISTQB Negative Partition Coverage — Modernize bars_matrix_builder_test.dart, establish matrix_claim_test.dart, and run domain parity gate
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\05_placeholder_phase4_flutter_studio_client_harmonization.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md] --phase=6`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify Wave 1 baseline in v2_core.py, global_mandates.py, prompt_factory.py, matrix_sensor_prompt_builder.py, and localization_compiler.py
  - [x] Step 1: Global Mandates Static Prefix Migration — Inject GLOBAL_MANDATES_XML into Layer 1 base_system_prompt in prompt_factory.py and build_caching_prefix in matrix_sensor_prompt_builder.py
  - [x] Step 2: Mechanical Anchors & Execution Time Resolver Decomposition — Create MechanicalAnchorsPayload and ExecutionTimeResolver, eradicate find_value_by_key / hasattr / getattr, replace slug checks with polymorphic checks, and replace LANGUAGE_NAMES.get with Fail-Fast AppException
  - [x] Step 3: Unit Test Modernization & ISTQB Negative Partition Coverage — Modernize test_prompt_factory.py, test_epic_60_decoupling.py, create test_execution_time_resolver.py, update test_localization_compiler.py, and update test_matrix_sensor_prompt_builder.py
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 7: Polymorphic AnyPromptBlock Discriminated Union & AST Guardrails

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md] --phase=7`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify Phase 6 compiler baseline in v2_core.py, mechanical_anchors.py, and prompt_factory.py
  - [x] Step 1: Pydantic Discriminated Union Creation & Seed Registry Alignment — Create AnyPromptBlock polymorphic union in backend_v2/models/domain/prompt_blocks.py, resolve circular imports in v2_core.py with __getattr__, align PromptBlockResponseDTO, and update seed_registry.py
  - [x] Step 2: Flutter Freezed Sealed Class Synchronous Parity — Refactor Dart PromptBlock to sealed union class with Freezed unionKey: category_id in prompt_block.dart, run build runner, and modernize test fixtures
  - [x] Step 3: AST XML Sovereignty Guardrails Test Suite — Implement and pass 10 static AST tests in test_ast_prompt_xml_sovereignty.py and 8 unit tests in test_prompt_blocks.py
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 8: Clean Stack Compiler Layer Assembly

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md] --phase=8`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify Phase 7 domain models baseline in `prompt_blocks.py` and `v2_core.py`
  - [x] Step 1: PromptFactory Polymorphic Assembly Modernization — Update `prompt_factory.py` to dispatch persona, role, and protocol blocks via `match block:` pattern matching and resolve `atom_to_block_ids` with `isinstance(block, MatrixPromptBlock)`
  - [x] Step 2: LocalizationCompiler Pattern Matching Dispatch — Update `localization_compiler.py` to dispatch static and dynamic instruction extraction via `match block:` on concrete sub-types
  - [x] Step 3: StudioSimulationService Zero-XML & Matrix Rendering — Update `simulation_service.py` to polymorphically match `data` and render Zero-XML fields and matrix scales without unvalidated property lookups
  - [x] Step 4: MatrixSensorPromptBuilder Ephemeral Instantiation & XML Assembly — Update `_create_ephemeral_block` to instantiate `SystemRulePromptBlock`, assemble Zero-XML rubric fields into XML tags, and wrap `theory_context`
  - [x] Step 5: Unit Test Modernization & ISTQB Negative Partition Coverage — Modernize `test_simulation_service.py`, `test_matrix_sensor_prompt_builder.py`, `test_localization_compiler.py`, and `test_prompt_factory.py` with concrete sub-model fixtures and negative partition tests
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\08_placeholder_phase8_clean_stack_compiler_assembly.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 9: Flutter Studio Zero-XML UI Modernization

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md] --phase=9`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify Phase 8 compiler baseline
  - [x] Step 1: ARB Localization Setup & Code Generation — Add Zero-XML labels/helpers to app_en.arb/app_fi.arb and run flutter gen-l10n
  - [x] Step 2: PromptBlockBuilderView Polymorphic Form Modernization — Update prompt_block_builder_view.dart with Dart 3 switch destructuring for Zero-XML fields, dynamic tone directives, and Live Compiled Prompt Preview modal
  - [x] Step 3: StepBuilderView Streamlining & Criteria Alignment — Verify criteria block selector against PromptBlockCategoryGroups.criteriaCategories
  - [x] Step 4: Unit & Widget Test Suite Implementation — Create prompt_block_builder_view_test.dart with ISTQB negative partition testing
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\09_placeholder_phase9_flutter_studio_zero_xml_ui.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 10: Seed Vault Pruning & Database Reseeding

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md] --phase=10`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify Phase 9 UI baseline and Phase 10 scope
  - [x] Step 1: Seed Vault Backup & Programmatic Redundancy Audit — Backup seed_data.json and verify 100% subsumption of 17 candidate blocks by Layer 1 GLOBAL_MANDATES_XML
  - [x] Step 2: Vault Pruning & HTML Entity Repair — Prune 17 candidate block IDs (105 references across 12 steps) from criteria_block_ids in seed_data.json and fix `&lt;mechanical_anchors&gt;` on line 6705
  - [x] Step 3: AST Seed Guardrail Test Suite Expansion — Add 4 AST/seed guardrails to test_ast_prompt_xml_sovereignty.py and run guardrails suite
  - [x] Step 4: Seed Integrity Validation & Database Reseeding — Reseed database via `run_seed.py local` and run backend audit loop
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\10_placeholder_phase10_seed_vault_pruning_and_reseeding.md] @[docs\epic\EPIC_146_tracker.md]`

---

### Phase 11: End-to-End Live Integration Verification Gate & Knowledge Synchronization

**Plan:** @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md] @[docs\epic\EPIC_146_tracker.md] --phase=11`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md] @[docs\epic\EPIC_146_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\11_placeholder_phase11_e2e_live_integration_verification.md] @[docs\epic\EPIC_146_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify Phase 10 reseeded database baseline
  - [x] Step 1: Core Model Circular Import Decoupling & Blueprint Adapter Fix — Eliminate circular imports and use PromptBlockAdapter in BlueprintTransformer
  - [x] Step 2: Integration Test Suite Modernization & ISTQB Negative Partitions — Fix mock fixtures, add NEG-01/02/03 scenarios, and verify pytest passes
  - [x] Step 3: Live LLM E2E REST API Verification Gate — Execute live LLM E2E verification test gate via $env:RUN_LIVE_E2E="true"
  - [x] Step 4: Knowledge Item Synchronization (4-Layer Clean Stack & Zero-XML UI) — Update ki_llm_extraction_architecture.md
  - [x] Step 5: LLM Architecture Rule Synchronization (05_llm_architecture.md) — Synchronize XML compiler sovereignty and 4-layer clean stack rules
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
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
  - [ ] [NEW] @[backend_v2/models/domain/mechanical_anchors.py]
  - [ ] [NEW] @[backend_v2/models/domain/prompt_blocks.py]
  - [ ] @[backend_v2/models/prompts/global_mandates.py]
  - [ ] @[backend_v2/models/v2_core.py]
  - [ ] @[backend_v2/seed/seed_registry.py]
  - [ ] @[backend_v2/services/orchestrator/localization_compiler.py]
  - [ ] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]
  - [ ] [NEW] @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]
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
   - All file references MUST use `@-reference` syntax (specifically `@[backend_v2/models/v2_core.py]`).
   - For Knowledge Items, use relative filename syntax (specifically `@[ki_god_code_prevention.md]`).

4. **Workflow Execution Pipeline**:
   - The mandatory workflow loop for deferred phases is: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`.
   - You MUST pass BOTH the plan file and tracker file in ALL commands (specifically `/tier0-research-plan @[docs\epic\tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization\06_placeholder_phase6_layer1_global_mandates_and_compiler.md] @[docs\epic\EPIC_146_tracker.md]`).
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
| **REQ-146-12** | Section 2.1, 3.2 | Execute seed backup and migration script copying 70 missing `concept_description` values from `MatrixClaim.ai_description` and eradicating 152 `ai_description` keys on claims in `seed_data.json`. | Phase 2, Step 1-2 | `scratch/migrate_seed_tda.py` |
| **REQ-146-13** | Section 2.1, 3.2 | Execute verification script proving 0 claim `ai_description` keys and 152 valid assertion `concept_description` strings (len >= 10), run AST guardrail seed tests, and execute clean-slate database re-seeding via `run_seed.py local`. | Phase 2, Step 3-4 | `uv run python backend_v2/seed/run_seed.py local` |
| **REQ-146-14** | Section 2.2, 3.3 | Define `tda_concept_min_length: 10` in `backend_v2/settings.py` and enforce `StringConstraints(strip_whitespace=True, min_length=10)` on `TDAAssertion.concept_description` in `v2_core.py`. | Phase 3, Step 1 | `backend_audit_loop.py settings.py` |
| **REQ-146-15** | Section 2.1, 3.3 | Permanently eradicate `ai_description` field from `MatrixClaim` in `backend_v2/models/v2_core.py`, retaining only `label: I18nText` and `tda_assertions: list[TDAAssertion]`. | Phase 3, Step 1 | `backend_audit_loop.py v2_core.py` |
| **REQ-146-16** | Section 2.1, 3.3 | Translate Finnish error messages and historical comments in `v2_core.py` to English present-tense descriptions. | Phase 3, Step 1 | `backend_audit_loop.py v2_core.py` |
| **REQ-146-17** | Section 2.2, 3.3 | Verify `atom_flattening.py` utilizes `tda.concept_description.strip()`. | Phase 3, Step 2 | `pytest test_atom_flattening.py` |
| **REQ-146-18** | Section 2.1, 3.3 | Enforce Fail-Fast exception with RFC 7807 structured logging if `assertion.question` is empty in `matrix_sensor_prompt_builder.py`. | Phase 3, Step 2 | `pytest test_matrix_sensor_prompt_builder.py` |
| **REQ-146-19** | Section 3.3, 3.5 | Atomically modernize mock claim fixtures across 24 backend test files (updating 39 short concept strings to >= 10 chars and removing `ai_description`), un-skip 3 AST guardrails, and add negative prompt builder test. | Phase 3, Step 3 | `backend_audit_loop.py backend_v2 --test` |
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
| **REQ-146-37** | Section 2.1, 3.10 | Prune 17 redundant global mandate block IDs (105 references across 12 steps) from `criteria_block_ids` in `seed_data.json` and fix corrupted HTML entity `&lt;mechanical_anchors&gt;` -> `<mechanical_anchors>`. | Phase 10, Step 1 | `backend_audit_loop.py seed_data.json` |
| **REQ-146-38** | Section 2.1, 3.10 | Execute database re-seeding via `uv run python backend_v2/seed/run_seed.py local`. | Phase 10, Step 1 | `uv run python backend_v2/seed/run_seed.py local` |
| **REQ-146-39** | Section 3.11, 4.4 | Execute mandatory live LLM E2E REST API integration test verification gate (`$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`). | Phase 11, Step 1 | `pytest test_epic_chain_e2e.py` |
| **REQ-146-40** | Section 3.11, 5.0 | Update Knowledge Item `ki_llm_extraction_architecture.md` with Zero-XML UI paradigm and 4-Layer Clean Stack Model specification, and synchronize `.agents/rules/05_llm_architecture.md`. | Phase 11, Step 1 | `tier7-describe-architecture` |

---

# Session Handover Context

## Achieved
- **Phase 1 Backend Plan (`01_phase1_backend_tech_debt_and_ast_guardrails.md`) Complete & Audited**:
  - Eliminated duck typing `getattr(claim, 'ai_description', None)` and fallback logic in `simulation_service.py`.
  - Remediated and un-skipped unit test fixtures in `test_tier4_schema_bug.py` and `test_schema_builder.py`.
  - Implemented 9 AST & Seed Guardrail tests in `test_ast_matrix_claim_guardrails.py` verifying 0 `ai_description` keys on claims, concept description string bounds, and model purity.
  - Executed and PASSED `/tier8-audit-plan` for Phase 1 Backend.
- **Phase 1 Frontend Plan (`02_phase1_frontend_tech_debt_cleanups.md`) Complete & Audited**:
  - Refactored `StepBuilderView` in `client_app_v2/lib/features/studio/views/step_builder_view.dart` to take `final String stepId;` (eradicating `final dynamic step;` and runtime dynamic type checks).
  - Converted `formState.when(...)` to exhaustive Dart 3 native `switch (formState)` destructuring.
  - Eradicated `SizedBox.shrink()` anti-patterns and translation fallback chains (`translations[currentLocale] ?? translations['fi'] ?? ...`) in `_deleteStep`, MCP tools, extraction protocols, and execution personas with Fail-Fast `AppException.validation`.
  - Updated `TypedGoRoute<StepEditRoute>(path: 'step/edit/:id')` in `client_app_v2/lib/router/router.dart` and re-generated router code via `build_runner`.
  - Updated `StepEditRoute(id: ...)` in `client_app_v2/lib/features/studio/views/studio_dashboard_view.dart`.
  - Replaced hardcoded hex color `const Color(0xFF2E7D32)` in `prompt_block_builder_view.dart` with `Theme.of(context).colorScheme.primaryContainer`.
  - Eradicated `DateTime.now()` timestamp IDs in favor of deterministic UUID generation (`const Uuid().v4().replaceAll('-', '')`).
  - Replaced fallback chain in `_deletePromptBlock` with Fail-Fast `AppException.validation`.
- **Phase 2 Plan (`03_phase2_seed_data_verification_and_reseed.md`) Complete & Audited**:
  - Created timestamped backup of `backend_v2/seed/seed_data.json`.
  - Migrated 70 missing `concept_description` values from `claim.ai_description` and permanently eradicated `ai_description` from all 152 MatrixClaims in `seed_data.json`.
  - Un-skipped and passed AST guardrail seed tests `test_seed_claims_have_no_ai_description` and `test_seed_claims_all_tda_assertions_have_valid_concept_description` in `backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py`.
  - Verified JSON schema integrity of `seed_data.json`.
  - Executed and PASSED `/tier8-audit-plan` for Phase 2 with full verification matrix and audit artifact generated (`red_team_audit_03_phase2_seed_data_verification_and_reseed.md`).
- **Phase 3 Plan (`04_placeholder_phase3_backend_domain_and_service_harmonization.md`) Complete & Audited**:
  - Defined `tda_concept_min_length: 10` in `backend_v2/settings.py`.
  - Updated `TDAAssertion.concept_description` with `Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)]` in `backend_v2/models/v2_core.py`.
  - Permanently deleted `ai_description: str` from `MatrixClaim` in `backend_v2/models/v2_core.py`, retaining `label` and `tda_assertions` as the sole assertion container.
  - Translated Finnish comments, docstrings, and error messages in `TDAAssertion.validate_math_logic` to English present-tense.
  - Added empty `assertion.question` validation in `matrix_sensor_prompt_builder.py` raising Fail-Fast `AppException` with RFC 7807 structured logging.
  - Un-skipped and verified all 9 AST and seed guardrail tests in `backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py`.
  - Added anti-happy path test for empty `assertion.question` in `backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py`.
  - Systematically modernized mock claim fixtures and concept descriptions across all 24 backend test files across Batches 1, 2a, and 2b.
  - Cleaned unused `# type: ignore` comments in `backend_v2/worker.py` and updated exception assertions in `backend_v2/tests/unit/models/test_v2_core.py`.
  - Verified Quality Gates: `backend_audit_loop.py` passed with 100% strict typing and test coverage on modified targets; all 1,824 backend unit tests passing; `flutter_audit_loop.py client_app_v2` passed cleanly.
  - Executed and PASSED `/tier8-audit-plan` for Phase 3 with full verification matrix and audit artifact generated (`red_team_audit_04_placeholder_phase3_backend_domain_and_service_harmonization.md`).
- **Phase 4 Plan (`05_placeholder_phase4_flutter_studio_client_harmonization.md`) Complete & Audited**:
  - Added `tdaConceptMinLength(10)` to `SystemUiConstraints` in `client_app_v2/lib/core/models/enums.dart`.
  - Permanently eradicated `aiDescription` from `MatrixClaim` in `client_app_v2/lib/features/studio/models/prompt_block.dart`, restoring 1:1 parity with backend `v2_core.py`.
  - Updated `TDAAssertion.create` to produce 32 hex char IDs (`tda_$uuidHex`), establishing exact parity with backend regex `^tda_[a-f0-9]{32}$`.
  - Added ARB localization keys `tdaConceptMinLengthError`, `tdaAnchorTargetHelper`, and `tdaExtractionRuleHelper` to `app_en.arb` and `app_fi.arb`, and compiled via `flutter gen-l10n`.
  - Replaced legacy spacing magic numbers with `AppSpacing` design tokens in `scale_editor_modal.dart`.
  - Aligned `ScaleEditorModal`: updated `_addClaim()` to instantiate `MatrixClaim` with `TDAAssertion.create`, eradicated `claim.aiDescription` text field, added validator enforcing `SystemUiConstraints.tdaConceptMinLength.value`, and connected localized helpers.
  - Aligned `BarsMatrixBuilder`: rendered `claim.tdaAssertions.first.conceptDescription` in place of `claim.aiDescription`.
  - Aligned `PromptBlockBuilderView`: updated `ScaleEditorModal` initial scale to instantiate valid `TDAAssertion.create` and imported `enums.dart`.
  - Modernized `bars_matrix_builder_test.dart` fixture removing `aiDescription` and adding explicit assertion for `Atom 1 Rule`.
  - Created comprehensive unit test suite in `client_app_v2/test/models/matrix_claim_test.dart` covering regex matching, deserialization, `CheckedFromJsonException` on legacy `ai_description` (strict mode), ISTQB boundary value analysis (9 vs 10 chars), and missing required field errors.
  - Verified Quality Gates: `flutter_audit_loop.py client_app_v2 --build` passed cleanly with 0 analyzer issues and build runner outputs, `matrix_claim_test.dart` passed (6/6 tests), `bars_matrix_builder_test.dart` passed, and `domain_parity_test.dart` passed (3/3 tests against all 152 prompt blocks in `seed_data.json`).
  - Executed and PASSED `/tier8-audit-plan` for Phase 4 with full verification matrix and audit artifact generated (`red_team_audit_phase4_flutter_studio_client_harmonization.md`).
- **Phase 6 Plan (`06_placeholder_phase6_layer1_global_mandates_and_compiler.md`) Complete & Audited**:
  - Migrated `GLOBAL_MANDATES_XML` from dynamic user payload (`exec_params`) to Layer 1 of `base_system_prompt` static caching prefix in `prompt_factory.py` and `build_caching_prefix` in `matrix_sensor_prompt_builder.py`, guaranteeing prompt purity (never present in `user_payload`).
  - Created strongly-typed `MechanicalAnchorsPayload` domain model (`backend_v2/models/domain/mechanical_anchors.py`) with strict Pydantic V2 config (`strict=True, extra='forbid'`), deterministic `.from_context()`, and `.to_xml()`, eliminating all reflection helpers (`find_value_by_key`), `hasattr`/`getattr` calls, and replacing hardcoded slug checks with polymorphic category checks (`PromptBlockCategory.MATRIX`).
  - Re-exported `MechanicalAnchorsPayload` in `backend_v2/models/domain/__init__.py` and `backend_v2/models/v2_core.py`.
  - Created `ExecutionTimeResolver` (`backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py`) resolving prompt execution time across dynamic inputs, physical disk input file `st_mtime`, and metadata timestamps, replacing 7 `.get()` fallback chains.
  - Hardened `LocalizationCompiler` (`backend_v2/services/orchestrator/localization_compiler.py`) by replacing `LANGUAGE_NAMES.get(..., "English")` fallbacks with Fail-Fast `AppException` (400, `VALIDATION_FAILED`) on unsupported locales.
  - Added comprehensive unit tests and ISTQB negative partition coverage:
    - Created `test_mechanical_anchors.py` (100% coverage).
    - Created `test_execution_time_resolver.py` (100% coverage).
    - Updated `test_prompt_factory.py` with static AST inspection test verifying zero `hasattr`/`getattr` calls in `prompt_factory.py` (93% coverage).
    - Updated `test_epic_60_decoupling.py` asserting Layer 1 global mandates in `base_system_prompt`.
    - Updated `test_localization_compiler.py` covering supported locales, invalid input types, and unsupported locale error handling (97% coverage).
    - Updated `test_matrix_sensor_prompt_builder.py` asserting Layer 1 global mandates in `build_caching_prefix` (100% coverage).
  - Verified Quality Gates: `backend_audit_loop.py` passed with 100% strict typing and test coverage on all modified targets; all 323 orchestrator tests passed cleanly; Flutter domain parity test passed (197 tests).
  - Executed and PASSED `/tier8-audit-plan` for Phase 6 with full verification matrix and audit artifact generated (`red_team_audit_phase6_layer1_global_mandates_and_compiler.md`).
- **Phase 7 Plan (`07_placeholder_phase7_polymorphic_prompt_blocks_and_ast_guardrails.md`) Complete & Audited**:
  - Architected and implemented polymorphic `PromptBlock` class with `__get_pydantic_core_schema__`, `__new__` dispatcher, `model_validate`, and `model_construct` delegating to concrete models (`MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock`) in `backend_v2/models/domain/prompt_blocks.py` with strict `ConfigDict(strict=True, extra='forbid', frozen=True)`.
  - Enforced Zero-Fallback / Zero-Legacy rule by completely eliminating backward-compatibility `__getattr__` dynamic loaders and `if TYPE_CHECKING:` bridges from `backend_v2/models/v2_core.py`. All consumers now import directly from `backend_v2.models.domain.prompt_blocks`.
  - Added automatic `computed_min` and `computed_max` calculation to `MatrixPromptBlock` via `@model_validator(mode="after")`, deriving bounds directly from `scales` without requiring manual entry.
  - Registered polymorphic `PromptBlock` schema in `seed_registry.py`, validated all 90 prompt blocks in `seed_data.json` with 0 errors via dry-run and live reseed.
  - Aligned `PromptBlockResponseDTO = PromptBlock` in `backend_v2/models/dtos/studio.py` and polymorphic instruction text extraction in `simulation_service.py`.
  - Created `backend_v2/tests/unit/test_prompt_blocks.py` achieving 98% strict test coverage across all prompt block variants (11/11 tests passing).
  - Implemented 10 static AST and model purity tests in `backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py` (10/10 passing).
  - Refactored Flutter Dart `PromptBlock` to `@Freezed(unionKey: 'category_id', equal: false) sealed class PromptBlock with _$PromptBlock` in `client_app_v2/lib/features/studio/models/prompt_block.dart` with factory constructors (`matrix`, `systemRule`, `executionPersona`, `agentRole`, `protocol`, `runtimeVariables`, `taskDefinition`), `@JsonKey(name: 'computed_min') int? computedMin`, `@JsonKey(name: 'computed_max') int? computedMax`, and background isolate parsers.
  - Aligned `prompt_block_builder_view.dart` with concrete polymorphic constructors (`switch (val)`), matrix-guarded cards (`if (payload is MatrixPromptBlock)`), and executed build runner with 0 analyzer issues.
  - Simplified Flutter getters to pure DTO accessors without client-side fallback math.
  - Modernized `backend_v2/models/domain/prompt_blocks.py` to a pure Pydantic V2 Discriminated Union (`AnyPromptBlock`, `PromptBlockAdapter`, `PROMPT_BLOCK_REGISTRY`), ruthlessly eliminating `__new__` and `model_construct` chameleon anti-patterns.
  - Added strict `<rule_block id="pydantic_discriminated_union_mandate">` to `.agents/rules/01-python-backend.md` and AST guardrail `test_ast_no_pydantic_new_or_construct_hijacking`.
  - Migrated all 11 downstream test consumer suites (30/30 unit tests passed), verified 100% backend coverage (0 mypy issues), and confirmed all 197 Flutter tests pass.
  - Executed and PASSED `/tier8-audit-plan` for Phase 7 with full verification matrix and audit artifact generated (`red_team_audit_phase7_polymorphic_prompt_blocks.md`).

- **Phase 8 Plan (`08_placeholder_phase8_clean_stack_compiler_assembly.md`) Complete & Audited**:
  - Modernized `PromptFactory` (`backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`) with Python 3.10+ `match block:` pattern matching across concrete sub-types (`PersonaPromptBlock`, `ProtocolPromptBlock`, `SystemRulePromptBlock`) for Layer 1 Persona, Layer 2 Role Directive, and Protocol extraction, eliminating unvalidated property lookups.
  - Implemented polymorphic grounding check `is_grounded_step = any(isinstance(b, MatrixPromptBlock) for b in criteria_blocks)` and narrowed `atom_to_block_ids` loop with `isinstance(block_model, MatrixPromptBlock) and block_model.scales` to safely access BARS scales.
  - Modernized `LocalizationCompiler` (`backend_v2/services/orchestrator/localization_compiler.py`) with pattern matching across `SystemRulePromptBlock`, `PersonaPromptBlock`, and `ProtocolPromptBlock` for static and dynamic instructions, tightened exception handling in `resolve_i18n` to `(ValidationError, ValueError)`, and enforced Fail-Fast `ConfigurationError` when instruction text is missing.
  - Modernized `StudioSimulationService` (`backend_v2/services/studio/simulation_service.py`) to polymorphically extract base text via `match data:` and render Matrix evaluation scales and TDA concept descriptions cleanly.
  - Updated `MatrixSensorPromptBuilder._create_ephemeral_block` (`backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`) to instantiate concrete `SystemRulePromptBlock` instances with strictly typed literal category IDs (`SYSTEM_RULE`, `RUNTIME_VARIABLES`, `TASK_DEFINITION`).
  - Upgraded test suites across all 4 targets (`test_prompt_factory.py`, `test_localization_compiler.py`, `test_simulation_service.py`, `test_matrix_sensor_prompt_builder.py`) with concrete sub-model fixtures, polymorphic extraction tests, and negative ISTQB partition coverage (100% pass, 58/58 tests passing, 98% line coverage across target modules).
  - Verified 12 static AST Prompt XML Sovereignty guardrail tests passing 100% (`test_ast_prompt_xml_sovereignty.py`).
  - Executed and PASSED `/tier8-audit-plan` for Phase 8 with full verification matrix and audit artifact generated (`red_team_audit_08_placeholder_phase8_clean_stack_compiler_assembly.md`).

- **Phase 9 Plan (`09_placeholder_phase9_flutter_studio_zero_xml_ui.md`) Complete & Audited**:
  - Added all necessary Zero-XML localized labels, tooltips, helpers, and snackbar messages to `client_app_v2/lib/l10n/app_en.arb` and `client_app_v2/lib/l10n/app_fi.arb`, and regenerated typed getters via `flutter gen-l10n`.
  - Refactored `PromptBlockBuilderView` in `client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart` to dispatch concrete Zero-XML fields via Dart 3 pattern matching (`switch (payload)`) across sealed subclasses:
    - `SystemRulePromptBlock`, `RuntimeVariablesPromptBlock`, `TaskDefinitionPromptBlock` (`instructionText`)
    - `ExecutionPersonaPromptBlock`, `AgentRolePromptBlock` (`roleEnforcement`, dynamic list of `toneDirectives` with add/remove)
    - `ProtocolPromptBlock` (`protocolInstructions`)
    - `MatrixPromptBlock` (BARS rubric notice card)
  - Integrated live **"Compiled Prompt Preview"** dialog in the AppBar with selectable monospace code viewer and copy-to-clipboard functionality (`l10n.promptCopiedSnackbar`).
  - Replaced hardcoded tooltips, warnings, and spacing doubles with localized ARB tokens (`backToStudioTooltip`, `studioNoModelsWarning`, `studioModelStrategyLabel`, `studioSaveButton`) and `AppSpacing` design tokens in `PromptBlockBuilderView` and `StepBuilderView`.
  - Verified criteria block filtering against `PromptBlockCategoryGroups.criteriaCategories` in `step_builder_view.dart`.
  - Created comprehensive widget & unit test suite in `client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart` covering all 7 polymorphic variants, dynamic list add/remove with `ValueKey`, live compiled preview modal + clipboard copy, and empty English label validation gates.
  - Aligned button finders in `output_profile_crud_view_test.dart` with localized `l10n.studioSaveButton`.
  - Verified Quality Gates: `flutter_audit_loop.py` passed with 0 analyzer issues, 0 formatting diffs, and 100% passing tests (including all 204 Flutter unit/widget tests and `domain_parity_test.dart`).
  - Executed and PASSED `/tier8-audit-plan` for Phase 9 with full verification matrix and audit artifact generated (`red_team_audit_09_placeholder_phase9_flutter_studio_zero_xml_ui.md`).

- **Phase 10 (Seed Vault Pruning & Database Reseeding) Executed & Audited (`440128fc`)**:
  - Pruned 17 redundant global mandate block IDs (105 total references across 12 steps) from `criteria_block_ids` in `backend_v2/seed/seed_data.json` while strictly preserving step-specific criteria, matrix blocks, heuristics, principles, and task definitions.
  - Repaired corrupted HTML entity `&lt;mechanical_anchors&gt;` on line 6705 of `seed_data.json` to `<mechanical_anchors>`.
  - Added 4 new AST and Seed Guardrail test cases to `backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py` (2 positive seed checks + 2 negative mock AST/data tests), with all 16 tests passing with 97% strict coverage.
  - Reseeded database cleanly via `uv run python backend_v2/seed/run_seed.py local` (90 prompt blocks, 19 steps validated and upserted).
  - Executed `/tier8-audit-plan` on Phase 10 plan with 100% compliance; generated audit report artifact `red_team_audit_phase10_seed_vault_pruning_and_reseeding.md`.

- **Phase 11 (End-to-End Live Integration Verification Gate & Knowledge Synchronization) Red-Teamed & Refined**:
  - Executed `/tier0-research-plan` System 2 Red-Team analysis on `docs/epic/tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization/11_placeholder_phase11_e2e_live_integration_verification.md` with 100% markdown boundary pass (`audit_markdown_boundaries.py`).
  - Identified and dry-run validated circular import resolution: eradicated late import `from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent` in `backend_v2/models/v2_core.py` and moved `ExecutionRecord.model_rebuild(_types_namespace=_state_localns)` into `backend_v2/models/state.py` alongside `ExecutionCoreFields`.
  - Modernized `BlueprintTransformer` (`backend_v2/services/blueprint.py`) to use `PromptBlockAdapter.validate_python(b_dict)` for polymorphic prompt block deserialization, eliminating `AttributeError: 'typing.Union' object has no attribute 'model_validate'`.
  - Modernized integration test mock fixtures (`mock_pb` in `test_epic_chain_e2e.py` and `test_lazy_llm_simulation.py`) to align with polymorphic `MatrixPromptBlock` schema.
  - Specified 3 ISTQB negative test partitions (`NEG-01`: 404 on missing profile, `NEG-02`: 400 on missing locale, `NEG-03`: 500 on malformed matrix payload).
  - Specified exact synchronization content for `ki_llm_extraction_architecture.md` (Zero-XML UI paradigm, 4-Layer Clean Stack Model, Static-First Caching Topology) and `.agents/rules/05_llm_architecture.md` (`compiler_xml_sovereignty_mandate`, `four_layer_clean_stack_hierarchy`).
  - Validated dry-run execution with 2/2 tests passing in `test_epic_chain_e2e.py`.

## Learned
- **Pure Pydantic V2 Discriminated Union Architecture**:
  - In Python 3.14 / Pydantic V2, polymorphism MUST be implemented strictly as `Annotated[Union, Field(discriminator="category_id")]` with `TypeAdapter(AnyPromptBlock)`. Faking union behavior via `__new__` hijacking or `model_construct` overrides (`# type: ignore[override]`) on `BaseModel` classes is a dangerous anti-pattern (Chameleon Class) that breaks Rust `pydantic-core` parsing, LSP attribute inference, and hides silent fallbacks.
- **Leaf Module Decoupling in State Management**:
  - When leaf modules (specifically `execution_core.py`) use `TYPE_CHECKING` for event models to break circular dependencies with `state.py`, persistent records (specifically `ExecutionRecord` in `v2_core.py`) must resolve deferred annotations via `model_rebuild(_types_namespace=_state_localns)` in `state.py` rather than attempting circular late imports in `v2_core.py`.
- **Polymorphic TypeAdapter Usage in Transformers**:
  - In Pydantic V2 / Python 3.14, discriminated unions typed with `Annotated[Union[...], Field(discriminator='category_id')]` cannot be validated with `.model_validate()`. All transformers and services MUST use `TypeAdapter(AnyPromptBlock).validate_python(data)`.
- **3-Tier Architectural Defense**:
  - Defense Layer 1 (Rules): `01-python-backend.md` explicitly bans Chameleon classes and unvalidated `model_construct` overrides.
  - Defense Layer 2 (AST Guardrails): `test_ast_prompt_xml_sovereignty.py` statically scans AST trees to reject any `__new__` or `model_construct` definitions on domain models.
  - Defense Layer 3 (Knowledge Item): `ki_polymorphic_rule_routing.md` provides explicit PRO-PATTERN vs ANTI-PATTERN code references for future agents.
- **Zero-XML UI Paradigm (Studio Layer)**:
  - In Flutter Studio V2, UI forms must never ask users or authors to input raw XML tags (`<system_directive>`, `<role>`, `<rules>`). All XML generation is strictly encapsulated in backend compilers (`PromptFactory`, `LocalizationCompiler`, `MatrixSensorPromptBuilder`, `StudioSimulationService`), while the UI captures discrete, natural-language fields (`instructionText`, `roleEnforcement`, `protocolInstructions`, `toneDirectives`) and provides a live preview of the compiled XML representation.
- **Polymorphic Type Narrowing & Pattern Matching**:
  - When iterating over polymorphic `AnyPromptBlock` lists, checking `if isinstance(block_model, MatrixPromptBlock) and block_model.scales:` narrows the type for MyPy and guarantees safe attribute access without requiring duck-typing, `# type: ignore`, or Chameleon properties.
- **Seed Data Redundancy Resolution**:
  - Individual step criteria blocks in `seed_data.json` historically duplicated global system rules (`block_headermandates`, `block_rule1`..`6`, `block_oprule1`..`3`, `block_instructionnohallucination`, `block_instructionlanguage_dynamic`, `block_headerinstructions`). With Layer 1 `GLOBAL_MANDATES_XML` statically compiling into all system prompts at the compiler level, retaining these blocks inside step criteria creates redundant prompt tokens and visual clutter in Studio without adding cognitive value.
- **Mathematical Line Bounding for Seed Vault Mutations**:
  - Vault mutations on large JSON files (specifically `seed_data.json` with 9,458 lines) must be performed with verified line boundaries (`#Lnn-mm`) to prevent LLM context saturation and parsing errors.

## Remaining
- **Phase 11: End-to-End Live Integration Verification Gate & Knowledge Synchronization**:
  - [x] Create Plan: `/tier0-create-plan @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] @[docs/epic/tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization/11_placeholder_phase11_e2e_live_integration_verification.md] @[docs/epic/EPIC_146_tracker.md] --phase=11`
  - [x] Red-Team Phase 11 Plan: `/tier0-research-plan @[docs/epic/tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization/11_placeholder_phase11_e2e_live_integration_verification.md] @[docs/epic/EPIC_146_tracker.md]`
  - [ ] Execute Phase 11: `/tier2-execute @[docs/epic/tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization/11_placeholder_phase11_e2e_live_integration_verification.md] @[docs/epic/EPIC_146_tracker.md]`
  - [ ] Audit Phase 11: `/tier8-audit-plan @[docs/epic/tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization/11_placeholder_phase11_e2e_live_integration_verification.md] @[docs/epic/EPIC_146_tracker.md]`
- **Post-Implementation & Final Integration Gates**:
  - Full Backend & Frontend audit loops.
  - Tier 2 Hardening (Backend & Frontend).
  - Tier 7 Describe Architecture & Knowledge Item sync.

## Required Rules & Knowledge Items for Next Session
- **Rules**:
  - `@[.agents/rules/00-antigravity-core.md]`
  - `@[.agents/rules/01-python-backend.md]`
  - `@[.agents/rules/03_seed_vault.md]`
  - `@[.agents/rules/04_directory_reference.md]`
  - `@[.agents/rules/05_llm_architecture.md]`
- **Knowledge Items**:
  - `@[ki_god_code_prevention.md]`
  - `@[ki_ast_guardrail_testing.md]`
  - `@[ki_global_config_sovereignty.md]`
  - `@[ki_python_314_concurrency_strictness.md]`
  - `@[ki_llm_extraction_architecture.md]`
  - `@[ki_polymorphic_rule_routing.md]`

## Resume Command
```powershell
/tier2-execute @[docs/epic/tasks_EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization/11_placeholder_phase11_e2e_live_integration_verification.md] @[docs/epic/EPIC_146_tracker.md]
```
