# Tracker: Cross-Model Variance Harmonization, Global Sensor Directives, Matrix Seed Vault Hardening, and Input Ingress Determinism
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md]

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md] @[docs/implementationplans/TRACKER_Cross_Model_Variance_Harmonization.md]`
  - [x] Step 1: Pre-Implementation Cleanups (`global_mandates.py`, `field_prompts.py`, `evaluation_steps.py`, `anchor_validation_service.py`, `extractive_sensor_service.py`)
  - [x] Step 2: Static System Prompt Hardening (`matrix_evaluation.py`)
  - [x] Step 3: Test Harness & Ingress Invariance (`diff_executions.py`, `pdf_chat_extractor.py`, `run_e2e_variance_test.py`)
  - [ ] Step 4: Seed Data Hardening (`seed_data.json` - 19 high-entropy atoms)
  - [ ] Step 5: Automated Test Suite & Audit Gates
  - [ ] Step 6: Knowledge Base Synchronization & KI Documentation Updates
  - [ ] Step 7: As-Built Architectural Pillar Synchronization via `/tier7-describe-architecture`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md] @[docs/implementationplans/TRACKER_Cross_Model_Variance_Harmonization.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [ ] @[backend_v2/models/prompts/execution/matrix_evaluation.py]
  - [ ] @[backend_v2/models/prompts/execution/global_mandates.py]
  - [ ] @[backend_v2/models/prompts/execution/field_prompts.py]
  - [ ] @[backend_v2/models/dtos/evaluation_steps.py]
  - [ ] @[backend_v2/services/ingress/pdf_chat_extractor.py]
  - [ ] @[backend_v2/services/orchestrator/anchor_validation_service.py]
  - [ ] @[backend_v2/services/orchestrator/extractive_sensor_service.py]
  - [ ] @[backend_v2/seed/seed_data.json]
  - [ ] @[scripts/run_e2e_variance_test.py]
  - [ ] @[scripts/diff_executions.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` (Scope: N/A - Zero production Flutter files modified in this plan).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.
  - [ ] Knowledge Item Updated: @[ki_prompt_orchestration_and_matrix_evaluation.md] (Layer 1 procedural prompt and document metadata disqualification protocols, Metacognitive Safe Harbor, hardened contextual override invariants, schema term purity)
  - [ ] Knowledge Item Updated: @[ki_seed_vault_verification_and_sanitization.md] (19 hardened atom definitions across Groups A-D, deterministic anti-pattern standards, multi-step acceptance criteria disambiguation)
  - [ ] Knowledge Item Updated: @[ki_ai_testing_standards.md] (Test harness ingress hoisting in `run_e2e_variance_test.py`, table extraction regex boundary normalization in `pdf_chat_extractor.py`, NFKC normalization in `diff_executions.py`, cross-model consensus bounds)
  - [ ] Knowledge Item Updated: @[ki_unified_matrix_scoring_strictness.md] (Statistical agreement baselines and target invariants for cross-model calibration)
  - [ ] Knowledge Item Updated: @[ki_structured_forensic_quotes.md] (Four-Layer Forensic Defense Architecture, empty normalized quote guard in `AnchorValidationService`, `min_length=10` and non-whitespace enforcement on `BooleanEvaluationResult`)
  - [ ] Architecture Document Updated: @[docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md] (Four-Layer Clean Stack updates, Layer 1 static prompt protocols, hardened contextual override mechanics, schema term purity)
  - [ ] Architecture Document Updated: @[docs/architecture/02_data_seeding_and_ontology.md] (Matrix Seed Vault Hardening, deterministic anti-patterns, multi-step acceptance criteria standards)
  - [ ] Architecture Document Updated: @[docs/architecture/01_system_context_and_invariants.md] (Cryptographic Input Ingress Determinism, test harness hoisting invariants, statistical cross-model consensus bounds)
  - [ ] Architecture Rule Synchronized: @[.agents/rules/04_directory_reference.md]

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md] @[docs/implementationplans/TRACKER_Cross_Model_Variance_Harmonization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After each successful quality gate verification, commit changes atomically with strict Conventional Commits syntax (`<type>(<scope>): <summary>`). List all staged files explicitly in `git add`.
- **Seeding Environment**: If database re-seeding is required, execute `uv run python backend_v2/seed/run_seed.py local`.
- **Quality Gates**:
  - For Python changes: `uv run python scripts/backend_audit_loop.py <target_path> --test`
  - For database atom validation: `uv run python scripts/audit_database_atoms.py --strict`
  - For in-memory seed verification: `uv run python backend_v2/seed/run_seed.py local --dry-run`
- **Execution Mode**: Supports Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`).
- **Context Budget Watchdog**: In Continuous Mode, proactively trigger `/tier5-session-handover` when the context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified complex files.
- **Workflow Loop**: `/tier2-execute @[plan] @[tracker]` -> `/tier8-audit-plan @[plan] @[tracker]` -> Post-Implementation Hardening Gates (`/tier2-hardening-backend`) -> `/tier7-describe-architecture`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-01 | Purge contradictory `atom_id`, V1 `exact_quotes`/`decision` terms, and open-ended `e.g.` ambiguity tokens from `global_mandates.py` | Step 1 | [x] |
| REQ-02 | Replace open-ended `e.g.` token in `DESC_ALIAS` with deterministic closed list `(specifically: 'a0', 'a1')` in `field_prompts.py` | Step 1 | [x] |
| REQ-03 | Replace silent auto-mutation `model_copy(update=)` with Fail-Fast `ValueError` in `StepDTOSemantic._enforce_override_exclusivity` | Step 1 | [x] |
| REQ-04 | Eradicate empty normalized quote bypass bug in `AnchorValidationService._is_lexically_valid` with `if not norm_quote: return False` | Step 1 | [x] |
| REQ-05 | Harden `BooleanEvaluationResult` schema with `min_length=10`, `strip()`, and non-whitespace character assertions on `source_quote` | Step 1 | [x] |
| REQ-06 | Inject `<procedural_prompt_disqualification_protocol>` and `<document_metadata_disqualification_protocol>` into `matrix_evaluation.py` | Step 2 | [x] |
| REQ-07 | Harden `CONTEXTUAL_OVERRIDE_DIRECTIVE` in `matrix_evaluation.py` requiring concrete alternative mechanisms and Null Hypothesis on inverse rules | Step 2 | [x] |
| REQ-08 | Apply Unicode NFKC normalization and uniform whitespace standardization before SHA-256 computation in `diff_executions.py` | Step 3 | [x] |
| REQ-09 | Enforce camelCase word-boundary regex spacing and space collapsing for table cells in `pdf_chat_extractor.py` | Step 3 | [x] |
| REQ-10 | Hoist `expected_inputs` resolution and `load_inputs_from_path` outside the execution loop in `run_e2e_variance_test.py` under `--no-noise` | Step 3 | [x] |
| REQ-11 | Add Pre-Flight Ingress Hash Assertion in `run_e2e_variance_test.py` verifying byte-identical SHA-256 hashes across comparison runs | Step 3 | [x] |
| REQ-12 | Harden Group A structural atoms (Toulmin, Goodhart, XAI: 6 atoms) in `seed_data.json` with anti-patterns and acceptance criteria | Step 4 | [ ] |
| REQ-13 | Harden Group B Kahneman Dual-Process atoms (3 atoms) in `seed_data.json` to disqualify task briefings and scenario parameters | Step 4 | [ ] |
| REQ-14 | Harden Group C Bloom Taxonomy, Falsification & Clarity atoms (7 atoms) in `seed_data.json` against prompt commands and headcounts | Step 4 | [ ] |
| REQ-15 | Harden Group D high-entropy triage atoms (3 atoms: Goodhart proxy, Avoimuus, Causal mechanisms) in `seed_data.json` | Step 4 | [ ] |
| REQ-16 | Expand unit test suite in `test_matrix_evaluation.py` and add negative partition tests in `test_global_mandates.py` | Step 5 | [ ] |
| REQ-17 | Expand ISTQB negative partition and boundary tests in `test_anchor_validation_service.py` and `test_extractive_sensor_service.py` | Step 5 | [ ] |
| REQ-18 | Execute quality gate loops (`backend_audit_loop.py`), `run_seed.py local --dry-run`, and `audit_database_atoms.py --strict` | Step 5 | [ ] |
| REQ-19 | Update 5 Knowledge Items (`prompt_orchestration`, `seed_vault`, `ai_testing`, `scoring_strictness`, `forensic_quotes`) | Step 6 | [ ] |
| REQ-20 | Synchronize architectural pillars (`09`, `02`, `01`) via `/tier7-describe-architecture` and update `.agents/rules/04_directory_reference.md` | Step 7 | [ ] |

# Session Handover Context
## Achieved
- Standalone single-phase implementation plan `docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md` reconciled across all audits (0110 vs 0218 diff reports, input data asymmetry forensics, Tier 0 research, Tier 8 audit).
- Plan tracker `docs/implementationplans/TRACKER_Cross_Model_Variance_Harmonization.md` generated with complete 1:1 step tracking, granular file-level hardening checklists, and 20-requirement traceability matrix.
- Step 1 completed: Legacy terms purged, quote validation hardened, and fail-fast enforced (`global_mandates.py`, `field_prompts.py`, `evaluation_steps.py`, `anchor_validation_service.py`, `extractive_sensor_service.py`).
- Step 2 completed: Static system prompt hardened with procedural prompt and document metadata disqualification protocols, English Metacognitive Safe Harbor, and inverse rule Null Hypothesis directive (`matrix_evaluation.py`).
- Step 3 completed: Test harness ingress hoisting, table cell regex spacing, and canonical hash normalization implemented (`diff_executions.py`, `pdf_chat_extractor.py`, `run_e2e_variance_test.py`). 138 unit tests passing with 100% Quality Gate.
## Learned
- Cross-model variance between Gemini 3.8 Flash and OpenAI GPT-5.4 was driven by extractive sensitivity/prompt mining (76.7%), contextual override asymmetry on inverse rules (23.3%), and Kahneman System 1/2 concept drift (+21.98 pp), NOT input text divergence.
- Naive `len(quote) > 0` checks fail against compliance evasion whitespace/punctuation tokens; four-layer defense architecture (`min_length=10`, `strip()`, `if not norm_quote: return False`, Null Hypothesis) guarantees strict grounding.
- PyMuPDF in-memory table layout artifacts can cause minor whitespace differences; hoisting inputs outside the variance test loop in `--no-noise` mode cryptographically guarantees byte-identical inputs (`KOLLISIO`).
## Remaining
- Execute Step 4: Seed Data Hardening (`seed_data.json` - 19 high-entropy atoms).
- Execute Step 5: Automated Test Suite & Audit Gates.
- Execute Step 6: Knowledge Base Synchronization & KI Documentation Updates.
- Execute Step 7: As-Built Architectural Pillar Synchronization via `/tier7-describe-architecture`.
- Execute Final Plan Audit via `/tier8-audit-plan`.
## Resume Command
`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md] @[docs/implementationplans/TRACKER_Cross_Model_Variance_Harmonization.md]`
