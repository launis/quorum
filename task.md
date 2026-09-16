# Task Checklist: Endorsed Deliverable Provenance Toggle & Universal Matrix Calibration

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

## Phase 1: Pre-Implementation Cleanups & Backend Model Enhancement
- [x] Step 1.1: Extend `ExpectedInput` Model with `is_endorsed_deliverable` in `@[backend_v2/models/v2_core.py#L681-L770]` and add mutual exclusivity validation against `is_chat_history`, `assignment`, and `questionnaire`
- [x] Step 1.2: Update Prompt Compiler Metadata & Capsule Emission in `@[backend_v2/services/orchestrator/prompt_compiler.py#L37-L64]` and `@[backend_v2/services/orchestrator/prompt_compiler.py#L193-L295]`
- [x] Step 1.3: Inject Anti-Ellipsis and Endorsed Deliverable Directives in System Prompt in `@[backend_v2/models/prompts/execution/matrix_evaluation.py#L12-L127]` (mandating substance over stylistic jargon on deliverables; zero banned ambiguities)
- [x] Step 1.4: Implement Tier 2 Unicode NFKC & Zero-Width Space Normalization in `@[backend_v2/services/orchestrator/anchor_validation_service.py#L60-L135]` and `@[scripts/diff_executions.py#L930-L962]` (normalizing Unicode spaces `\u2002`, `\u00a0` and zero-width format chars `\u200b-\u200d\ufeff` so that quote verification passes robustly under both `--no-noise` and default watermark noise-injection modes)
- [x] Step 1.5: Backend Unit Test Suite Expansion in `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py#L34-L60]`, `@[backend_v2/tests/unit/models/test_v2_core.py#L537-L600]`, and `@[backend_v2/tests/unit/services/test_anchor_validation_service.py]`

## Phase 2: Seed Vault Ontological Calibration & Re-Seeding
- [x] Step 2.1: Backup and Update `@[backend_v2/seed/seed_data.json]` (Set `"is_endorsed_deliverable": true` on all `product_text` inputs, enable candidate jargon scanning across workflows `wf_01`-`wf_03`, refine Bloom 3 anti-patterns in `tda_6a779cd5e9714994b83168dd0fef0ef7` lines 2100-2144, and calibrate Bloom 1 dogmatism anti-pattern in `tda_216cc3fd45284deb8d51ea4cf2b2fd93` lines 1726-1766)
- [x] Step 2.2: Pre-Flight In-Memory Validation & Seed Vault Synchronization (`run_seed.py local --dry-run` and `audit_database_atoms.py --strict` passing 100% before live seeding)
- [x] Step 2.3: Architecture Documentation & Knowledge Item Sync (`08_matrix_explanations.md#L61-L82` and `#L614-L618`, `09_llm_prompt_orchestration_and_matrix_evaluation.md`, `01_system_context_and_invariants.md`, `03_cognitive_orchestration_engine.md`, `06_enriched_atom_graph_engine.md`, `00_README_META_ARCHITECTURE.md`, and KIs `ki_prompt_orchestration_and_matrix_evaluation.md`, `ki_structured_forensic_quotes.md`, and `ki_workflow_context_governance.md` synchronized under `/tier7-describe-architecture` timeless as-built mandate)

## Phase 3: Frontend Studio UI & Localization Parity
- [x] Step 3.1: Update Flutter Freezed Workflow Model in `@[client_app_v2/lib/features/studio/models/workflow.dart#L28-L47]` and run build runner
- [x] Step 3.2: Add Localization Strings in `@[client_app_v2/lib/l10n/app_en.arb#L1850-L1860]` and `@[client_app_v2/lib/l10n/app_fi.arb#L1180-L1190]`
- [x] Step 3.3: Extend `ExpectedInputEditorBox` in `@[client_app_v2/lib/features/studio/views/widgets/expected_input_editor_box.dart#L126-L224]` with `FilterChip` and mutual exclusivity logic

## Phase 4: Global Verification & Quality Gates
- [x] Step 4.1: Execute Backend Audit Loop (`uv run python scripts/backend_audit_loop.py backend_v2 --test`)
- [x] Step 4.2: Execute Flutter Audit Loop (`uv run python scripts/flutter_audit_loop.py client_app_v2 --build`)
- [x] Step 4.3: SDUI Parity Verification (`uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`)
- [x] Step 4.4: Mandatory Live E2E REST API Verification (`$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -k test_real_llm_pdf_execution`)

---

# Session Handover Context
- **Achieved**: Fully implemented and verified Endorsed Deliverable Provenance Toggle & Universal Matrix Calibration across Phase 1 (Backend Pydantic models, prompt compiler capsule emission, anti-ellipsis & substance-over-jargon directives, Tier 2 Unicode NFKC and zero-width format stripping), Phase 2 (Seed Vault ontological calibration, dry-run & atom audit, live db_v2.json re-seeding, and timeless architecture/KI synchronization), Phase 3 (Flutter Freezed models, code generation, en/fi localizations, and Studio UI FilterChip with mutual exclusivity), and Phase 4 (Backend Audit Loop with 3405 tests passing and 94.82% coverage, Flutter Audit Loop with 0 analyzer issues, SDUI Semantic Parity passing, and Live E2E real LLM execution passing).
- **Learned**: Zero-width format characters (\u200b-\u200d\ufeff) in watermarks require regex stripping to preserve lexical anchor validation. Bloom Level 3 anti-pattern calibration requires retaining "abstract governing rule" anchor for domain neutrality test compliance. Live E2E test function name is `test_real_llm_pdf_execution`.
- **Remaining**: Execute mandatory post-implementation Red-Team audit via `/tier8-audit-plan`.
- **Resume Command**: `/tier8-audit-plan @[C:\Users\risto\.gemini\antigravity-ide\brain\186c222d-a46d-4e61-a7ec-3e8c7f29bc4e\implementation_plan.md] @[c:\src\quorum\task.md]`
