# EPIC 134: v2_core.py God Code Decomposition - Tracker

**Original Epic:** @[c:\src\quorum\docs\epic\EPIC_134_v2_core_god_code_decomposition.md]
**Task Directory:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\]

<required_context_rules>
- @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
- @[c:\src\quorum\.agents\rules\01-python-backend.md]
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]
- @[C:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
</required_context_rules>

## Phase Execution Status

### Phase 1: Golden Master & Coverage Verification
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\01_golden_master_and_coverage_plan.md]
- [ ] **Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\01_golden_master_and_coverage_plan.md]`
- [ ] **Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\01_golden_master_and_coverage_plan.md]`
  - [ ] Step 1.1: VERIFY COVERAGE
  - [ ] Step 1.2: CATALOG IMPORT CONSUMERS
- [ ] **Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\01_golden_master_and_coverage_plan.md]`

### Phase 2: Enum Centralization
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\02_enum_centralization_plan.md]
- [ ] **Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\02_enum_centralization_plan.md]`
- [ ] **Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\02_enum_centralization_plan.md]`
  - [ ] Step 2.1: Create 10 new Enum classes in enums.py
  - [ ] Step 2.2: Update Literal annotations in v2_core.py to Enum references
  - [ ] Step 2.3: Global audit loop verification
- [ ] **Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\02_enum_centralization_plan.md]`

### Phase 3: Finnish String Eradication & Duck-Typing Cleanup
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\03_finnish_eradication_plan.md]
- [ ] **Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\03_finnish_eradication_plan.md]`
- [ ] **Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\03_finnish_eradication_plan.md]`
  - [ ] Step 3.1: Translate ALL Finnish strings to English
  - [ ] Step 3.2: Replace hasattr/getattr duck-typing with typed access
  - [ ] Step 3.3: Global audit loop verification
- [ ] **Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\03_finnish_eradication_plan.md]`

### Phase 4: Domain Extraction & Strangler Fig Proxy
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\04_domain_extraction_plan.md]
- [ ] **Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\04_domain_extraction_plan.md]`
- [ ] **Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\04_domain_extraction_plan.md]`
  - [ ] Step 4.1: Extract I18nText → domain/i18n.py
  - [ ] Step 4.2: Extract PromptBlock group → domain/prompt_blocks.py
  - [ ] Step 4.3: Extract ModelProfile, SystemConfigModelRegistry → domain/llm_config.py
  - [ ] Step 4.4: Merge AllowedMCPTool, MCPAuditTrace, SystemConfigMCPGateways → domain/mcp.py
  - [ ] Step 4.5: Extract Lexicons → domain/lexicons.py
  - [ ] Step 4.6: Extract ChatMessageDTO, ChatHistoryDTO → domain/chat.py
  - [ ] Step 4.7: Extract Step, StepRule, Role → domain/workflow_steps.py
  - [ ] Step 4.8: Extract Workflow, QuestionnaireItem, ExpectedInput → domain/workflow.py
  - [ ] Step 4.9: Extract BaseMatrixXAI, BaseTDAExtraction → domain/llm_extraction.py
  - [ ] Step 4.10: Extract Report/Scorecard DTOs → dtos/report_data.py
  - [ ] Step 4.11: Extract Execution Lifecycle → domain/execution_lifecycle.py
  - [ ] Step 4.12: Global audit loop verification
- [ ] **Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\04_domain_extraction_plan.md]`

### Phase 5: Import Migration (Batched Strangler Fig Sunset)
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\05_import_migration_plan.md]
- [ ] **Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\05_import_migration_plan.md]`
- [ ] **Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\05_import_migration_plan.md]`
  - [ ] Step 5.1: Migrate import consumers in batches of 5 (22+ batches)
  - [ ] Step 5.2: Remove Strangler Fig re-exports from v2_core.py
  - [ ] Step 5.3: Final global audit loop
- [ ] **Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\05_import_migration_plan.md]`

### Phase 6: Frontend Flutter UI Enum Synchronization
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\06_frontend_enum_sync_plan.md]
- [ ] **Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\06_frontend_enum_sync_plan.md]`
- [ ] **Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\06_frontend_enum_sync_plan.md]`
  - [ ] Step 6.1: Run flutter_audit_loop.py and ensure Enum parity
- [ ] **Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\06_frontend_enum_sync_plan.md]`

### Phase 7: Verification & E2E Integration Gate
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\07_verification_and_e2e_gate_plan.md]
- [ ] **Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\07_verification_and_e2e_gate_plan.md]`
- [ ] **Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\07_verification_and_e2e_gate_plan.md]`
  - [ ] Step 7.1: Global Python backend audit loop
  - [ ] Step 7.2: Global Flutter audit loop
  - [ ] Step 7.3: Database re-seed verification
- [ ] **Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_134_v2_core\07_verification_and_e2e_gate_plan.md]`

### Post-Implementation Gates
- [ ] **Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **Describe Architecture**: Run `/tier7-describe-architecture`. Sync KI findings into documentation pillars.
- [ ] **Epic 134 Complete**: Transition Epic status to `IMPLEMENTED`.

### Final Epic Audit
- [ ] **System 2 Reverse Epic Analysis:** Verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- **Atomic Commits:** You MUST perform atomic Git commits after every successful milestone or batch of import migrations.
- **Seeding:** Run `uv run python backend_v2/seed/run_seed.py local` for verifying backend response models.
- **Reference Syntax:** Always use the strict `@-reference` syntax for file paths.
- **Workflow Loop:** You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

## Requirements Traceability Matrix

| Req ID | Description | Source File / Section | Phase / Step Mapping |
|---|---|---|---|
| R1 | Verify test coverage for `v2_core.py` > 80% or write Golden Master tests. | Epic 134 Section 3 Phase 1 | Phase 1 (Step 1.1) |
| R2 | Catalog all 107+ import consumers. | Epic 134 Section 3 Phase 1 | Phase 1 (Step 1.2) |
| R3 | Create 10 new Enum classes (AggregationMode, EvaluationTrack, BoundingBoxScope, StepExecutionType, StepSafety, ExpectedSduiType, PresetView, TextDeliveryMode, DisplayScale, ExportFormat). | Epic 134 Section 3 Phase 2 | Phase 2 (Step 2.1) |
| R4 | Replace all `Literal[...]` annotations with Enum references. | Epic 134 Section 3 Phase 2 | Phase 2 (Step 2.2) |
| R5 | Translate 12+ Finnish string literals to English. | Epic 134 Section 3 Phase 3 | Phase 3 (Step 3.1) |
| R6 | Eradicate `hasattr()` and `getattr()` duck-typing in PromptBlock validator. | Epic 134 Section 3 Phase 3 | Phase 3 (Step 3.2) |
| R7 | Extract I18nText to `domain/i18n.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.1) |
| R8 | Extract PromptBlock + 7 sub-models to `domain/prompt_blocks.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.2) |
| R9 | Extract ModelProfile, SystemConfigModelRegistry to `domain/llm_config.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.3) |
| R10 | Merge MCP config models into existing `domain/mcp.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.4) |
| R11 | Extract Lexicon models to `domain/lexicons.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.5) |
| R12 | Extract Chat DTOs to `domain/chat.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.6) |
| R13 | Extract Step, StepRule, Role to `domain/workflow_steps.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.7) |
| R14 | Extract Workflow, QuestionnaireItem, ExpectedInput to `domain/workflow.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.8) |
| R15 | Extract BaseMatrixXAI, BaseTDAExtraction to `domain/llm_extraction.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.9) |
| R16 | Extract 13 Report/Scorecard DTOs to `dtos/report_data.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.10) |
| R17 | Extract 6 Execution Lifecycle models to `domain/execution_lifecycle.py`. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.11) |
| R18 | Relocate `model_rebuild()` calls to correct target modules. | Epic 134 Section 3 Phase 4 | Phase 4 (Step 4.11-4.12) |
| R19 | Migrate 107+ import consumers to canonical new locations in batches of 5. | Epic 134 Section 3 Phase 5 | Phase 5 (Step 5.1) |
| R20 | Remove ALL Strangler Fig re-exports from v2_core.py. | Epic 134 Section 3 Phase 5 | Phase 5 (Step 5.2) |
| R21 | Verify Enum parity in Flutter UI. | Epic 134 Section 3 Phase 6 | Phase 6 (Step 6.1) |
| R22 | Final global backend, frontend audit, and DB re-seed verification. | Epic 134 Section 3 Phase 7 | Phase 7 (Step 7.1-7.3) |

# Session Handover Context
## Achieved
- Created EPIC 134 document: `@[c:\src\quorum\docs\epic\EPIC_134_v2_core_god_code_decomposition.md]`
- Created EPIC 134 Tracker document: `@[c:\src\quorum\docs\epic\EPIC_134_v2_core_god_code_decomposition_tracker.md]`
- Fully inventoried v2_core.py: 1702 lines, 50+ classes, 107+ import consumers.
- Defined 11 extraction targets across `models/domain/` and `models/dtos/`.
- Identified 10 `Literal` → Enum migrations, 12+ Finnish strings, 3 duck-typing violations.
- Noted `domain/mcp.py` collision hazard and `model_rebuild()` relocation strategy.

## Learned
- **Audit Script Limitations**: `audit_markdown_boundaries.py` flags [NEW] file paths as "does not exist" (false positive for Epic planning documents) and cannot detect type aliases (`WorkflowSchemaResponse = dict[str, Any]`) as valid symbols.
- **Circular Dependency Hazard**: v2_core.py uses bottom-of-file deferred imports and `model_rebuild()` to resolve circular refs with `state.py` and `view/sdui.py`. This MUST be handled carefully during extraction.
- **Massive Consumer Count**: 107+ files import from v2_core.py — significantly more than lightweight_matrix.py (23 consumers). Phase 5 will require 22+ batches with session handovers.
- **Residual Classes**: 8 classes STAY in v2_core.py (HumanOverrideRequest, HumanOverrideDTO, SynthesisConfigDTO, OutputLayoutBlock, OutputProfile, JobAcceptedDTO, EvidenceRejectionRequest, WorkflowSchemaResponse) totaling ~250 lines — well under the 400-line limit.

## Remaining
- User review and approval of EPIC 134.
- Proceed to `/tier1-planner` for Phase 1 implementation plan generation.

## Resume Command
`/tier1-planner @[c:\src\quorum\docs\epic\EPIC_134_v2_core_god_code_decomposition.md]`
