# Task Tracker: Studio TDA Editor Input Modernization & ContrastivePairDTO Migration

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_matrix_sensor_prompt_builder.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_TDA_Editor_Input_Modernization_and_ContrastivePairDTO_Migration.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint Step 1 (`the_zero_compromise_pledge`): Zero permissive typing: `ConfigDict(strict=True, extra="forbid", frozen=True)`. No loose string fallback or Union with raw str.
- [x] Constraint Step 1 (`ban_anonymous_state_tuples`): Eradicate all anonymous tuples in DAG state transit and atom flattening.
- [x] Constraint Step 1 (`rfc7807_dual_reporting_mandate`): Precede all validation failures with structured `logger.error` containing `ErrorCodes.VALIDATION_FAILED.name`.
- [x] Constraint Step 2 (`vault_mutation_protocol`): Must execute two-phase pre-flight in-memory validation before database sync. If validation fails, restore backup immediately.
- [x] Constraint Step 2 (`database_persistence_git_ban`): Never rollback runtime database state with git checkout. Preserve updated `seed_data.json` and `db_v2.json` atomically.
- [x] Constraint Step 3 (`static_first_caching_topology`): All static instructions remain static in the system message. Dynamic claim parameters are isolated in dynamic user messages.
- [x] Constraint Step 4 (`atomic_checkpoint_mandate`): Halt execution after Phase A completion and commit atomically before opening Phase B files.
- [x] Constraint Step 5 (`automated_code_generation_mandate`): Never manually edit `.freezed.dart` or `.g.dart` files. Autonomously execute the flutter audit loop with `--build`.
- [x] Constraint Step 6 (`no_magic_strings_l10n`): Zero hardcoded string literals in UI widgets. All display text must resolve through `AppLocalizations.of(context)!`.
- [x] Constraint Step 6 (`dual_axis_localization_mandate`): Static UI chrome in `.arb`; English system language rules for prompt evaluations.
- [x] Constraint Step 7 (`monolithic_god_widgets`): Decompose UI outwards into discrete, testable sub-widgets under 150 lines each. Prevent bloating `scale_editor_modal.dart`.
- [x] Constraint Step 7 (`design_token_absolute_rule`): Exclusively use `AppSpacing` tokens and `Theme.of(context).colorScheme`. No hardcoded numeric paddings or Color literals.
- [x] Constraint Step 8 (`studio_unified_visual_design_system`): Card containers with borderRadius 12, elevation 2, margin 16, semantic typography, and 100% `Theme.of(context)` color adherence.
- [x] Constraint Step 9 (`anti_happy_path_mandate`): Every component must have at least 2 negative test cases covering boundary values, empty inputs, and validation errors.
- [x] Constraint Step 9 (`ast_guardrail_mandate`): Build AST guardrail test to structurally prevent regression of loose string contrastive examples, `.split()` anti-patterns, or SnackBar invocations in dialogs.
- [x] Constraint Step 10 (`dual_axis_documentation_mandate`): KIs are the theoretical source of truth for AI agents; update KIs before generating architectural pillar documentation.
- [x] Constraint Step 11 (`timeless_as_built_mandate`): Describe purely and timelessly what the system currently has and how it operates right now.
- [x] Constraint Step 11 (`documentation_present_tense_mandate`): Never describe project phases, historical progressions, or Law/Enforcement labels in `docs/architecture/`.

## Execution Tasks

### PHASE A: BACKEND SCHEMA, SEED MIGRATION, DAG TRANSIT & SENSOR PROMPTS
- [x] **Step 1: PHASE A.1: PRE-IMPLEMENTATION CLEANUPS & BACKEND SSOT DTO**
  - [x] Declare `ContrastivePairDTO` in `backend_v2/models/v2_core.py` with `acceptable`, `rejected`, `min_length=10`, `strip_whitespace=True`, and diversity validator.
  - [x] Update `TDAAssertion.contrastive_example` to `ContrastivePairDTO | None = Field(default=None)`.
  - [x] Update `validate_math_logic` on `TDAAssertion`.
  - [x] Export `ContrastivePairDTO` in `backend_v2/models/v2_core.py` and `backend_v2/models/dtos/engine.py`.
  - [x] Refactor `backend_v2/hooks/atom_flattening.py`: eradicate anonymous tuple containers (`unique_atoms`, `all_matrix_atoms`, `matrix_collected_atoms`, `scale_atoms`), instantiate `FlattenedAtom` directly, preserve transitive causal closure.
  - [x] Update `scripts/diff_executions.py` to unpack structured dict fields and fail-fast on legacy traces.
  - [x] Update `scripts/matrix_slice_engine.py` line 146 to check `ContrastivePairDTO` attributes.
  - [x] Update `scripts/matrix_hardening_generator.py` line 106 and test fixtures to >=10 char exemplars.
- [x] **Step 2: PHASE A.2: SEED DATA VAULT MIGRATION SCRIPT & ATOMIC RE-SEEDING**
  - [x] Create `scripts/migrate_seed_contrastive_pairs.py` with backup, regex parsing, UTF-8 normalization, and summary logging.
  - [x] Execute migration on all 305 atoms in `backend_v2/seed/seed_data.json`.
  - [x] Run dry-run validation (`run_seed.py local --dry-run` and `audit_database_atoms.py --strict`).
  - [x] Execute atomic re-seed (`run_seed.py local`).
- [x] **Step 3: PHASE A.3: ENGINE DTO PROPAGATION & SENSOR PROMPT BUILDER INTEGRATION**
  - [x] Extend `FlattenedAtom` in `backend_v2/models/dtos/engine.py` with structured fields (`contrastive_example`, `acceptance_criteria`, `anti_patterns`, `syntactic_anchors`).
  - [x] Update `backend_v2/hooks/atom_flattening.py` to propagate structured assertion fields.
  - [x] Update `backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py` with CDATA-shielded tags (`<contrastive_grounding>`, `<acceptance_criteria>`, `<anti_patterns>`, `<syntactic_anchors>`).
  - [x] Run 432 orchestrator tests to verify zero regressions.
- [x] **Step 4: PHASE A.4: PHASE A VERIFICATION & ATOMIC COMMIT CHECKPOINT**
  - [x] Create `backend_v2/tests/unit/models/test_contrastive_pair_dto.py` with 4 negative partitions.
  - [x] Create `backend_v2/tests/unit/guardrails/test_ast_tda_editor_guardrails.py` (backend AST assertions).
  - [x] Update `test_matrix_anchoring_rules.py`, `test_matrix_hardening_loop.py`, `test_matrix_hardening_generator.py`.
  - [x] Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`.
  - [x] Atomic git commit checkpoint for Phase A (Commit `0cdc8b41`).

### PHASE B: FRONTEND FREEZED DTO, LOCALIZATION, MODULAR WIDGETS & STUDIO UI
- [x] **Step 5: PHASE B.1: FLUTTER FREEZED DTO & CODEGEN SYNC**
  - [x] Define `@Freezed ContrastivePairDTO` in `client_app_v2/lib/features/studio/models/prompt_block.dart`.
  - [x] Update `TDAAssertion.contrastiveExample` to `ContrastivePairDTO?`.
  - [x] Run `flutter_audit_loop.py ... --build`.
- [x] **Step 6: PHASE B.2: MULTILINGUAL LOCALIZATION ARB SYNCHRONIZATION**
  - [x] Add Finnish keys in `client_app_v2/lib/l10n/app_fi.arb`.
  - [x] Add English keys in `client_app_v2/lib/l10n/app_en.arb`.
  - [x] Run `flutter gen-l10n`.
- [x] **Step 7: PHASE B.3: MODULAR FLUTTER COMPONENT EXTRACTION (4 SSOT SUB-WIDGETS)**
  - [x] Create `TagChipInput` with Dual-Shield FormField auto-flush, bounded chip width (`maxWidth: 240px`), hover tooltip, `hasPendingBuffer`.
  - [x] Create `DynamicItemListEditor` with numbered badges, `OutlinedButton.icon`, and `IconButton` delete.
  - [x] Create `ContrastivePairEditor` with live counters, color accents, and <520px responsive stacking.
  - [x] Create `LinguisticShieldBanner` with two-phase `LinguisticShieldDetector` (Unicode + stopwords).
- [x] **Step 8: PHASE B.4: STUDIO TDA EDITOR REFACTORING & MASTER-DETAIL 5-CARD LAYOUT**
  - [x] Reorganize `scale_editor_modal.dart` into Adaptive Master Selector + 5 visual cards (`elevation: 2`, `borderRadius: 12`).
  - [x] Embed 4 modular sub-widgets.
  - [x] Implement save debouncing (`_isSaving`), auto-scroll to invalid field, cross-claim error navigation.
  - [x] Implement `PopScope` dismissal protocol with composite dirty check (`_isModelDirty() || _hasPendingInputBuffers()`).
  - [x] Mount prominent `Virhetutka` warning container when `inverseEvidence == true`.
  - [x] Eradicate all snackbars, hardcoded Finnish strings, and `Colors.amber`.
- [x] **Step 9: PHASE B.5: TESTING, AST GUARDRAILS & QUALITY GATE VERIFICATION**
  - [x] Add frontend AST guardrails in `test_ast_tda_editor_guardrails.py`.
  - [x] Create widget tests for `TagChipInput`, `ContrastivePairEditor`, `LinguisticShieldBanner`.
  - [x] Update `scale_editor_modal_test.dart` for 5 cards, save debouncing, and PopScope dismissal.
  - [x] Run flutter audit loop with `--build`.
  - [x] Atomic git commit for Phase B (Commit `e7f086b1`).

### PHASE C: KNOWLEDGE BASE (KI) & TIER 7 AS-BUILT ARCHITECTURE SYNCHRONIZATION
- [x] **Step 10: PHASE C.1: KNOWLEDGE INFORMATION (KI) DOCUMENTATION SYNCHRONIZATION**
  - [x] Synchronize `ki_desktop_pro_tool_studio_ux.md`.
  - [x] Synchronize `ki_zero_permissive_typing.md`.
  - [x] Synchronize `ki_seed_vault_verification_and_sanitization.md`.
  - [x] Synchronize `ki_matrix_sensor_prompt_builder.md`.
  - [x] Update `.agents/rules/04_directory_reference.md`.
- [x] **Step 11: PHASE C.2: TIER 7 INDIVIDUAL AS-BUILT ARCHITECTURAL AUDIT & PILLAR SYNCHRONIZATION**
  - [x] Synchronize `docs/architecture/02_data_seeding_and_ontology.md` (Section 2.12).
  - [x] Synchronize `docs/architecture/03_cognitive_orchestration_engine.md` (Section 2.16).
  - [x] Synchronize `docs/architecture/04_server_driven_ui_and_presentation.md` (Section 2.11).
  - [x] Synchronize `docs/architecture/06_enriched_atom_graph_engine.md` (Section 2.13).
  - [x] Synchronize `docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md` (Sections 2.7, 2.8, 2.9).
  - [x] Atomic git commit for Phase C.

## Session Handover Context
- **Achieved**: 100% implementation and verification across Phase A, Phase B, and Phase C. All 45 backend/guardrail tests and all 25 Flutter widget tests passing with exit code 0. Zero compiler, lint, or format issues. All 4 KIs and 5 architecture pillars synchronized.
- **Learned**: In Flutter Master-Detail forms, detail subforms bound to dynamic selection indices require distinct `ValueKey`s across all input fields to avoid stale `TextEditingController` state retention across selection changes.
- **Remaining**: Route through mandatory Tier 8 System 2 Red-Team Audit (`/tier8-audit-plan`).
