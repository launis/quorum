<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
</required_context_rules>

# Master Decomposition Tracker: Anchor Validation Service (`backend_v2/services/orchestrator/anchor_validation_service.py` -> `backend_v2/services/orchestrator/anchor_validation/`)

## Overview & Decomposition Architecture
- **Target God File**: `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (replaced by `@[backend_v2/services/orchestrator/anchor_validation/__init__.py#L51-L147]`)
- **Monolith Archetype**: Archetype A — Algorithmic / Pure Compute Engine (`AnchorValidationService`: zero semaphores, zero network I/O, pure deterministic lexical and semantic evidence validation functions)
- **Symbol & Blast-Radius Map**: `@[docs/epic/tasks_anchor_validation_service/symbol_migration_map.md]`
- **Baseline Audit (`[BASELINE]`)**: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test` -> **53 passed**, **93% coverage** (443 statements, 30 missed). Since baseline coverage `>= 75%`, `Phase 0: Coverage Bootstrap` is bypassed.

## Phase Execution Status

### Phase 1: Leaf Constants, Normalizer, Strict Match & Fuzzy Score Extraction (Epoch 1)
- **Plan:** @[docs/epic/tasks_anchor_validation_service/phase1_normalizer_and_strict_match_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_anchor_validation_service/phase1_normalizer_and_strict_match_extraction.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]` (`274e88291`)
  - [x] Step 1: Create `@[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]` containing `MAX_CITATION_SPAN_CHARS`, `MIN_MULTI_SEGMENT_FLOOR_CHARS`, `MIN_ENTROPY_GATE_CHARS`, `normalize_text_with_mapping`, `strict_match`, and `calculate_fuzzy_score` relocated from `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]`.
  - [x] Step 2: Wire proxy delegations and explicit redundant re-exports in `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` without creating `backend_v2/services/orchestrator/anchor_validation/__init__.py`.
  - [x] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_anchor_validation_service/phase1_normalizer_and_strict_match_extraction.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]`

### Phase 2: Multi-Tier Lexical Matcher Extraction (Epoch 1)
- **Plan:** @[docs/epic/tasks_anchor_validation_service/phase2_lexical_matcher_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_anchor_validation_service/phase2_lexical_matcher_extraction.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]` (`a7900163c`)
  - [x] Step 1: Create `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py]` containing `is_lexically_valid` relocated from `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]`.
  - [x] Step 2: Update `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` to delegate `AnchorValidationService._is_lexically_valid` to `is_lexically_valid`.
  - [x] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_anchor_validation_service/phase2_lexical_matcher_extraction.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]`

### Phase 3: Evidence Validator & Atom Evaluation Processor Extraction (Epoch 1)
- **Plan:** @[docs/epic/tasks_anchor_validation_service/phase3_evidence_and_atom_validator_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_anchor_validation_service/phase3_evidence_and_atom_validator_extraction.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]` (`27f74c0e2`)
  - [x] Step 1: Create `@[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py#L25-L337]` (`validate_evidence`) and `@[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py#L18-L125]` (`process_atom_evaluation` with top-level `AliasEngine` import).
  - [x] Step 2: Update `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` to delegate `validate_evidence` and `process_atom_evaluation` to the extracted sub-modules.
  - [x] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/evidence_validator.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_anchor_validation_service/phase3_evidence_and_atom_validator_extraction.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]`

### Phase 4: Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown (Epoch 1 Cutover)
- **Plan:** @[docs/epic/tasks_anchor_validation_service/phase4_package_cutover_and_guardrails.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_anchor_validation_service/phase4_package_cutover_and_guardrails.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]` (`e7cfff52e`)
  - [x] Step 1: Split `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` and `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py]` into 5 modular unit test suites under `backend_v2/tests/unit/services/orchestrator/anchor_validation/`.
  - [x] Step 2: Atomically create `@[backend_v2/services/orchestrator/anchor_validation/__init__.py#L51-L147]` (`< 150` lines), delete `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]`, and rewire all 1-hop consumer imports (`extractive_sensor_service.py`, `mcp_tool_loop.py`, `integrity.py`, `ablation_live_executor.py`, `audit_manifest_generator.py`, `run_ablation_benchmark.py`, `run_e2e_variance_test.py`, `test_multi_segment_quote_foundation.py`, `test_integrity.py`, `test_multi_segment_causal_e2e.py`).
  - [x] Step 3: Lock retired module `backend_v2.services.orchestrator.anchor_validation_service` in `@[scripts/_ast_guardrails.py#L1865-L1936]` and `@[scripts/_ast_guardrails.py#L1938-L2084]` (`QGR017`) and synchronize `@[.agents/rules/04_directory_reference.md]`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_anchor_validation_service/phase4_package_cutover_and_guardrails.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker docs/epic/anchor_validation_service_decomposition_tracker.md --gate backend`
  - [x] `@[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py#L27-L76]`
  - [x] `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]`
  - [x] `@[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py#L25-L337]`
  - [ ] `@[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py#L18-L125]`
  - [ ] `@[backend_v2/services/orchestrator/anchor_validation/__init__.py#L51-L147]`
  - [ ] `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L176-L761]`
  - [ ] `@[backend_v2/services/mcp/mcp_tool_loop.py#L150-L476]`
  - [ ] `@[backend_v2/hooks/integrity.py#L118-L138]`
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Pure backend Python decomposition with zero `.dart` changes.
- [ ] **[NOK] Pre-Delete Audit**: Verify `git status` and `grep_search` confirm 0 remaining references to `backend_v2.services.orchestrator.anchor_validation_service` and physical removal of `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]`.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify all 59 baseline unit tests pass across the modularized test suites (`@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_normalizer.py]`, `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]`, `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_evidence_validator.py]`, `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_atom_evaluation_processor.py]`, `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_anchor_validation_facade.py]`) with `>= 93%` line coverage.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Verify 100% symbol parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$) and execute `uv run pytest backend_v2/tests/integration/test_multi_segment_causal_e2e.py`, `uv run python scripts/audit_dict_eradication.py`, and `uv run python scripts/audit_clean_imports.py`.

#### Conditional Mutation Coverage Gate (Archetype A Proof Anchor)
- [ ] **[NOK] AST Mutation Coverage Gate**: Run `uv run python scripts/audit_mutation_coverage.py --strict` to verify 100% mutant kill rate across mathematical and algorithmic cores.

#### Epoch 2: 12-Item Technical Debt Inventory (Target Scope for Tier 2 Hardening)
1. **Item 6 (`inline_imports_ban` / `QGR009`)**: Ensure `from backend_v2.utils.alias_engine import AliasEngine` (previously inline at line 770 of `anchor_validation_service.py`) is declared at module top-level in `@[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py#L18-L125]`.
2. **Item 7 (`strict_configuration_segregation` — Magic Numbers)**: Audit module-level citation constants (`MAX_CITATION_SPAN_CHARS = 1000`, `MIN_MULTI_SEGMENT_FLOOR_CHARS = 30`, `MIN_ENTROPY_GATE_CHARS = 10`), the `0.80` stem coverage cap in `is_lexically_valid`, and default `strictness_level: int = 50` against `@[backend_v2/settings.py]`.
3. **Item 1 (`the_zero_compromise_pledge` & `idiomatic_pattern_matching`)**: Replace multi-branch `isinstance(quote, (list, tuple, Sequence)) and not isinstance(quote, str)` checks in `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]` and `@[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py#L25-L337]` with clean Python 3.14 `match/case` structural pattern matching or `typing.TypeIs` narrowing.
4. **Item 8 (`docstring_fail_fast_ban` & `pep257_google_style_docstrings`)**: Ensure all functions across all 4 sub-modules and `@[backend_v2/services/orchestrator/anchor_validation/__init__.py#L51-L147]` include complete PEP 257 Google-style docstrings (`Args:`, `Returns:`, and explicit `Raises: SemanticEvidenceError` in `validate_evidence`).
5. **Item 4 (`data_leak_logging` / DLP Audit)**: Verify zero raw user text payloads or PII strings are serialized into logger or OpenTelemetry attributes across all extracted sub-modules.
6. **Item 10 (`anti_happy_path_mandate` — ISTQB Negative & Boundary Partitions)**: Add negative and boundary tests covering the 30 missed statements from baseline (`lines 250, 304, 341-342, 377-384, 393-412, 521-522, 686-687, 711, 738, 848-849` of `anchor_validation_service.py`) across the 5 modular test files to achieve `>= 98%` line coverage.

#### Architectural Documentation Synchronization
- [ ] **[NOK] As-Built Architectural Sync**: Run `/tier7-describe-architecture @[docs/epic/anchor_validation_service_decomposition_tracker.md] @[ki_god_code_prevention.md] @[ki_structured_forensic_quotes.md]`
  - **Target KIs to Synchronize**: `@[ki_god_code_prevention.md]`, `@[ki_structured_forensic_quotes.md]`
  - **Directory Reference Sync**: Verify `@[.agents/rules/04_directory_reference.md]` reflects `backend_v2/services/orchestrator/anchor_validation/`
  - **Pillar Documentation Sync**: Update Pillar 6 (`docs/architecture/06_ATOM_GRAPH_ENGINE.md`) to reflect the modular `backend_v2/services/orchestrator/anchor_validation/` package

### Final Epic Audit
- [ ] **[NOK] Final Decomposition Audit**: Run `/tier8-audit-plan @[docs/epic/tasks_anchor_validation_service/phase4_package_cutover_and_guardrails.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]` and verify 100% completion across all phases and gates.

## Instructions for the Execution Agent
1. **Strict Two-Epoch Firewall**: During Epoch 1 (Phases 1–4), perform ONLY pure structural lift-and-shift extraction, consumer import rewiring, test suite modularization, and atomic package cutover with **zero behavioral changes**. Do NOT mix Epoch 2 tech debt fixes into Epoch 1.
2. **Two-Phase Package Strangler Protocol**: Do NOT create `backend_v2/services/orchestrator/anchor_validation/__init__.py` during Phases 1, 2, or 3 while `backend_v2/services/orchestrator/anchor_validation_service.py` exists on disk. Create `__init__.py` and delete `anchor_validation_service.py` atomically in Phase 4 Step 2.
3. **Quality Gate Enforcement**: Run `uv run python scripts/backend_audit_loop.py <target> --test --ast-strict` after every phase step and create an atomic Conventional Commit before advancing to the next phase.

## Requirements Traceability Matrix

| Requirement ID | Architectural Requirement | Phase & Step Mapping | Verification Target |
| :--- | :--- | :--- | :--- |
| `REQ-AVS-01` | Extract leaf constants (`MAX_CITATION_SPAN_CHARS`, `MIN_MULTI_SEGMENT_FLOOR_CHARS`, `MIN_ENTROPY_GATE_CHARS`), `normalize_text_with_mapping`, `strict_match`, and `calculate_fuzzy_score` into `lexical_normalizer.py` | Phase 1, Step 1 | `@[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py#L27-L76]` |
| `REQ-AVS-02` | Delegate `normalize_text_with_mapping`, `strict_match`, and `calculate_fuzzy_score` in `AnchorValidationService` with explicit redundant re-exports | Phase 1, Step 2 | `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` |
| `REQ-AVS-03` | Verify Phase 1 leaf extraction passes 10/10 backend audit gates and all 59 unit tests | Phase 1, Step 3 | `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_normalizer.py#L18-L26]` |
| `REQ-AVS-04` | Extract multi-tier lexical matcher `is_lexically_valid` (Gates 0–3) into `lexical_matcher.py` | Phase 2, Step 1 | `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]` |
| `REQ-AVS-05` | Wire proxy delegation for `AnchorValidationService._is_lexically_valid` | Phase 2, Step 2 | `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` |
| `REQ-AVS-06` | Verify Phase 2 lexical matcher extraction passes 10/10 backend audit gates and multi-segment foundation tests | Phase 2, Step 3 | `@[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py#L129-L142]` |
| `REQ-AVS-07` | Extract `validate_evidence` into `evidence_validator.py` and `process_atom_evaluation` into `atom_evaluation_processor.py` | Phase 3, Step 1 | `@[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py#L25-L337]`, `@[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py#L18-L125]` |
| `REQ-AVS-08` | Wire proxy delegations for `validate_evidence` and `process_atom_evaluation` in `AnchorValidationService` | Phase 3, Step 2 | `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` |
| `REQ-AVS-09` | Verify Phase 3 extraction passes 10/10 backend audit gates and causal E2E integration tests | Phase 3, Step 3 | `@[backend_v2/tests/integration/test_multi_segment_causal_e2e.py#L52-L76]` |
| `REQ-AVS-10` | Split `test_anchor_validation_service.py` and `test_anchor_validation_atom_result.py` into 5 modular unit test suites under `backend_v2/tests/unit/services/orchestrator/anchor_validation/` | Phase 4, Step 1 | `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_anchor_validation_facade.py#L21-L123]` |
| `REQ-AVS-11` | Atomically replace `anchor_validation_service.py` with `anchor_validation/__init__.py` (`< 150` lines) and rewire all 1-hop callers | Phase 4, Step 2 | `@[backend_v2/services/orchestrator/anchor_validation/__init__.py#L51-L147]` |
| `REQ-AVS-12` | Lock retired `backend_v2.services.orchestrator.anchor_validation_service` in `QGR017` AST guardrails and update `04_directory_reference.md` | Phase 4, Step 3 | `@[scripts/_ast_guardrails.py#L1865-L1936]`, `@[scripts/_ast_guardrails.py#L1938-L2084]` |

# Session Handover Context

## Achieved
- Completed Phase 1 (`@[docs/epic/tasks_anchor_validation_service/phase1_normalizer_and_strict_match_extraction.md]`):
  - Extracted `MAX_CITATION_SPAN_CHARS`, `MIN_MULTI_SEGMENT_FLOOR_CHARS`, `MIN_ENTROPY_GATE_CHARS`, `normalize_text_with_mapping`, `strict_match`, and `calculate_fuzzy_score` into `@[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py#L27-L76]` without creating `__init__.py` (`strangler_fig_mandate`).
- Completed Phase 2 (`@[docs/epic/tasks_anchor_validation_service/phase2_lexical_matcher_extraction.md]`):
  - Extracted `is_lexically_valid` into `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]` importing leaf functions exclusively from `lexical_normalizer.py`.
- Completed Phase 3 (`@[docs/epic/tasks_anchor_validation_service/phase3_evidence_and_atom_validator_extraction.md]`):
  - Extracted `validate_evidence` into `@[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py#L25-L337]` (337 lines) and `process_atom_evaluation` into `@[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py#L18-L125]` (125 lines, with `AliasEngine` promoted to a top-level import per `inline_imports_ban`).
- Completed Phase 4 (`@[docs/epic/tasks_anchor_validation_service/phase4_package_cutover_and_guardrails.md]`):
  - Split `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` (998 lines, 53 tests) and `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py]` (145 lines, 6 tests) into 5 modular unit test suites (`< 450` lines each, 61 tests total) under `backend_v2/tests/unit/services/orchestrator/anchor_validation/`: `test_lexical_normalizer.py` (175 lines), `test_lexical_matcher.py` (362 lines), `test_evidence_validator.py` (355 lines), `test_atom_evaluation_processor.py` (258 lines), and `test_anchor_validation_facade.py` (140 lines).
  - Atomically replaced `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` with `@[backend_v2/services/orchestrator/anchor_validation/__init__.py#L51-L147]` (147 lines, `< 150` lines) with explicit `__all__` and redundant import aliases (`from module import Symbol as Symbol`), and rewired all 10 1-hop consumer files (`extractive_sensor_service.py`, `mcp_tool_loop.py`, `integrity.py`, `ablation_live_executor.py`, `audit_manifest_generator.py`, `run_ablation_benchmark.py`, `run_e2e_variance_test.py`, `test_multi_segment_quote_foundation.py`, `test_integrity.py`, `test_multi_segment_causal_e2e.py`).
  - Registered retired module `backend_v2.services.orchestrator.anchor_validation_service` in `@[scripts/_ast_guardrails.py#L1865-L1936]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1938-L2084]` (`visit_ImportFrom`) under `QGR017` (FATAL severity) and synchronized `@[.agents/rules/04_directory_reference.md]`.
  - Passed 10/10 Universal Quality Gate checks (`96.94%` coverage across `anchor_validation/`, `>= 93%` per sub-module, 61/61 unit tests, 7/7 E2E causal tests, and local database seeding).

## Learned
- Running multiple `backend_audit_loop.py --test` processes concurrently in the same workspace directory causes `.coverage` SQLite file contention; always run coverage-enabled quality gates sequentially.

## Resume Command
`/tier8-audit-plan @[docs/epic/tasks_anchor_validation_service/phase4_package_cutover_and_guardrails.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]`

## Remaining
- Execute Phase 4 Audit (`/tier8-audit-plan @[docs/epic/tasks_anchor_validation_service/phase4_package_cutover_and_guardrails.md] @[docs/epic/anchor_validation_service_decomposition_tracker.md]`).
- Execute Epoch 2 Post-Implementation Gates (`Tier 2 Hardening (Backend)`, `Pre-Delete Audit`, `audit_mutation_coverage.py --strict`, `/tier7-describe-architecture`, and `/tier8-audit-plan`).
