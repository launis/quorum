<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# God Code Decomposition Tracker: `backend_v2/services/matrix_domain_parser.py`

## 1. Executive Summary & Baseline Telemetry
- **Target Monolith**: `@[backend_v2/services/matrix_domain_parser.py#L35-L206]` (originally 732 lines; `MatrixDomainParser.parse_matrices` currently spans lines `#L65-L206`)
- **Monolith Archetype**: Archetype C — Ingress / Parser / Anti-Corruption Layer (ACL) with Sequential Pipeline Staging (`MatrixDomainParser.parse_matrices`)
- **Planning Mode**: Single-File Fast-Track Mode (732 lines, 3 domain sub-modules + 1 package facade `< 150` lines, non-orchestrator)
- **Baseline Test Suite (`[BASELINE]`)**: `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test` -> **34 passed**, 10/10 audit stages passed, **91% line coverage** (384 statements, 33 missed; `>= 75%` prerequisite satisfied, no `Phase 0: Coverage Bootstrap` required)
- **Symbol & Blast-Radius Map**: `@[docs/epic/tasks_matrix_domain_parser/symbol_migration_map.md]`

---

## Phase Execution Status

### Phase 1: Stage DTOs & Distribution Formatter Extraction (Epoch 1 — Phase 1A)
- **Plan:** @[docs/epic/tasks_matrix_domain_parser/phase1_leaf_and_formatter_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_matrix_domain_parser/phase1_leaf_and_formatter_extraction.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]` (`73a147c3d`)
  - [x] Step 1: Define Immutable Stage DTOs in `backend_v2/models/dtos/matrix_parser.py` (`@[backend_v2/models/dtos/matrix_parser.py#L106-L145]` `MatrixScaleProjectionDTO`, `@[backend_v2/models/dtos/matrix_parser.py#L148-L165]` `MatrixAtomHydrationResultDTO`, `@[backend_v2/models/dtos/matrix_parser.py#L168-L183]` `MatrixContextTargetResultDTO`)
  - [x] Step 2: Create Leaf Formatter Module `@[backend_v2/services/matrix_parser/distribution_formatter.py#L26-L75]`
  - [x] Step 3: Wire Proxy Delegations in `@[backend_v2/services/matrix_domain_parser.py#L38-L50]`, `@[backend_v2/services/matrix_domain_parser.py#L52-L63]`, and `@[backend_v2/services/matrix_domain_parser.py#L65-L206]`
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_matrix_domain_parser/phase1_leaf_and_formatter_extraction.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]` (`red_team_audit_phase1_leaf_and_formatter_extraction.md`)

### Phase 2: Scale Projection & Atom Hydration Stage Extraction (Epoch 1 — Phase 1B)
- **Plan:** @[docs/epic/tasks_matrix_domain_parser/phase2_scale_and_atom_stage_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_matrix_domain_parser/phase2_scale_and_atom_stage_extraction.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]. PERMISSION GRANTED for continuous full-auto execution across all steps without intermediate confirmations.` (`45510b6c1`)
  - [x] Step 1: Create Scale and Atom Stage Module (`@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L32-L55]` `unpack_matrix_payload`, `@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L58-L191]` `compute_scale_and_score_projection`, `@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L194-L311]` `hydrate_step_scorecard_atoms`)
  - [x] Step 2: Delegate Scale and Atom Stages in `@[backend_v2/services/matrix_domain_parser.py#L65-L206]`
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_matrix_domain_parser/phase2_scale_and_atom_stage_extraction.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]` (`red_team_audit_phase2_scale_and_atom_stage_extraction.md`)

### Phase 3: Context Target Resolution & Row Builder Stage Extraction (Epoch 1 — Phase 1C)
- **Plan:** @[docs/epic/tasks_matrix_domain_parser/phase3_row_builder_stage_extraction.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_matrix_domain_parser/phase3_row_builder_stage_extraction.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]. PERMISSION GRANTED for continuous full-auto execution across all steps without intermediate confirmations.`
  - [x] Step 1: Create Row Builder Stage Module (`@[backend_v2/services/matrix_parser/row_builder_stage.py#L35-L75]` `resolve_unique_axis_name`, `@[backend_v2/services/matrix_parser/row_builder_stage.py#L78-L90]` `resolve_axis_description`, `@[backend_v2/services/matrix_parser/row_builder_stage.py#L93-L153]` `resolve_context_target`, `@[backend_v2/services/matrix_parser/row_builder_stage.py#L156-L248]` `build_matrix_scorecard_row`)
  - [x] Step 2: Delegate Context Target and Row Builder Stages in `@[backend_v2/services/matrix_domain_parser.py#L65-L206]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_matrix_domain_parser/phase3_row_builder_stage_extraction.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]`

### Phase 4: Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown (Epoch 1 — Cutover)
- **Plan:** @[docs/epic/tasks_matrix_domain_parser/phase4_package_cutover_and_guardrails.md]
- [x] **[SKIPPED] Research:** Single-File Fast-Track Mode (bypassed per Archetype C fast-track)
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_matrix_domain_parser/phase4_package_cutover_and_guardrails.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]. PERMISSION GRANTED for continuous full-auto execution across all steps without intermediate confirmations.`
  - [ ] Step 1: Modularize Unit Test Suite (`[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_distribution_formatter.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_scale_and_atom_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_row_builder_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_matrix_parser_facade.py]`) and delete `[DELETE] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`
  - [ ] Step 2: Execute Atomic Package Cutover (`[DELETE] @[backend_v2/services/matrix_domain_parser.py]` -> `[NEW] @[backend_v2/services/matrix_parser/__init__.py]`) and Rewire 1-Hop Callers (`@[backend_v2/services/blueprint.py#L65-L669]`, `@[backend_v2/tests/unit/services/test_blueprint.py#L3302-L3397]`, `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py#L81-L160]`)
  - [ ] Step 3: Lock Retired Path in `QGR017` AST Guardrails (`@[scripts/_ast_guardrails.py#L1865-L1897]` and `@[scripts/_ast_guardrails.py#L1899-L1977]`) and Synchronize `@[.agents/rules/04_directory_reference.md]`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_matrix_domain_parser/phase4_package_cutover_and_guardrails.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]`

---

### Post-Implementation Gates

#### Tier 2 Hardening (Backend)
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/epic/matrix_domain_parser_decomposition_tracker.md] --gate backend`
  - [ ] @[backend_v2/models/dtos/matrix_parser.py#L106-L145]
  - [ ] @[backend_v2/services/matrix_parser/distribution_formatter.py#L26-L75]
  - [ ] @[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L58-L191]
  - [ ] @[backend_v2/services/matrix_parser/row_builder_stage.py#L35-L75]
  - [ ] [NEW] @[backend_v2/services/matrix_parser/__init__.py]
  - [ ] [DELETE] @[backend_v2/services/matrix_domain_parser.py]
  - [ ] @[backend_v2/services/blueprint.py#L65-L669]
  - [ ] @[scripts/_ast_guardrails.py#L1865-L1897]

#### Tier 2 Hardening (Frontend)
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: N/A — Pure Python Backend Service Decomposition (zero `.dart` files in target scope).

#### Quality & Safety Gates
- [ ] **[NOK] Pre-Delete Audit**: Verify 0 remaining imports from `backend_v2.services.matrix_domain_parser` and 100% green `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_parser/ --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test --ast-strict`.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify all 34 baseline unit tests pass across the modularized test suites (`[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_distribution_formatter.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_scale_and_atom_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_row_builder_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_matrix_parser_facade.py]`) with `>= 91%` line coverage.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Verify 100% symbol parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$) and execute `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`, `uv run python scripts/audit_dict_eradication.py`, and `uv run python scripts/audit_clean_imports.py`.
- [ ] **[NOK] As-Built Architectural Sync**:
  `/tier7-describe-architecture @[docs/epic/matrix_domain_parser_decomposition_tracker.md] @[ki_sdui_matrix_synthesis.md] @[ki_god_code_prevention.md]`
  - **Target KIs to Synchronize**: `@[ki_sdui_matrix_synthesis.md]`, `@[ki_god_code_prevention.md]`
  - **Directory Reference Sync**: Verify `@[.agents/rules/04_directory_reference.md]` reflects `backend_v2/services/matrix_parser/` (`distribution_formatter.py`, `scale_and_atom_stage.py`, `row_builder_stage.py`, `__init__.py` facade).
  - **Pillar Documentation Sync**: Synchronize Pillar 4 & Pillar 6 architectural documentation to reflect the modular `backend_v2/services/matrix_parser/` stage pipeline.

#### Epoch 2: 12-Item Technical Debt Inventory (To Resolve During Tier 2 Hardening ONLY After Epoch 1 Cutover Completes)
1. **Item 1 (`Any` Annotations & Permissive Signatures)**:
    - Replace `results: list[Any]` and `execution: Any = None` in `[NEW] @[backend_v2/services/matrix_parser/__init__.py]`, `@[backend_v2/services/matrix_parser/distribution_formatter.py#L151-L199]`, and `@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L194-L311]` with strictly typed `Sequence[StepOutputDTO]` (or a structural `typing.Protocol` for folded step output envelopes) and `ExecutionRecord | None = None`.
    - Replace `clustered_row_sources: list[Any] = []` with `list[MCPAuditTrace]`.
    - Synchronize 1-hop caller `BlueprintTransformer.build_report_dto` (`@[backend_v2/services/blueprint.py#L126-L669]`) in the same atomic commit if parameter types or unused legacy parameters (`workflow_ext_values`, `row_curated_quotes_cache`, `rejected_evq_ids`, `mcp_audit_map`, `source_identity_manifest`) are tightened.
2. **Item 4 (Structured Exception Logging Parity)**:
    - Add `exc_info=True` to `logger.error` in `unpack_matrix_payload` and `hydrate_step_scorecard_atoms` inside `@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L32-L55]` and `@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L194-L311]` (originally in `@[backend_v2/services/matrix_domain_parser.py#L65-L206]`), and audit all OpenTelemetry / Logfire `set_attribute` calls to ensure zero raw user prompt or PII serialization.
3. **Item 6 (Modern Python 3.14 Pattern Matching & Enum Typing)**:
    - Convert inline `Literal["EXPLICIT_QUOTE", "IMPLIED_INTENT", "NO_EVIDENCE"]` and its `if/elif` chain in `@[backend_v2/services/matrix_parser/row_builder_stage.py#L156-L248]` (originally in `@[backend_v2/services/matrix_domain_parser.py#L65-L206]`) to a centralized `StrEnum` in `backend_v2/models/enums.py` or structural `match/case` validation.
4. **Item 8 (Dead Assignment Cleanup & Docstring Completeness)**:
    - Remove the redundant dead assignment `final_explanation = row_explanations_cache[block_id]` before `final_explanation = ""` in `resolve_row_explanation` inside `@[backend_v2/services/matrix_parser/distribution_formatter.py#L151-L199]`.
5. **Item 9 (Backend Localization SSOT)**:
    - Route hardcoded bilingual vocabulary in `format_level_distribution` (`"skills"` / `"taitoa"`, `"purity"` / `"puhtaus"`, `"defect"` / `"virhe"`, `"defects"` / `"virhettä"`) and the `"Kriteeri"` fallback in `hydrate_step_scorecard_atoms` through `LocalizationService.translate` while keeping all existing regression assertions green.
6. **Item 10 (ISTQB Negative Partition Expansion & Polyfactory Migration)**:
    - Replace manual `MockDTO` test helpers in `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_distribution_formatter.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_scale_and_atom_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_row_builder_stage.py]`, and `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_matrix_parser_facade.py]` with typed `StepOutputDTO` / `Polyfactory` factories, and add negative/boundary tests covering the 33 previously missed lines (achieving `>= 95%` coverage across `backend_v2/services/matrix_parser/`).

---

### Final Epic Audit
- [ ] **[NOK] System 2 Red-Team Audit:** `/tier8-audit-plan @[docs/epic/tasks_matrix_domain_parser/phase4_package_cutover_and_guardrails.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]`
- [ ] **[NOK] Global Backend Completion Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/ --test`

---

## Instructions for the Execution Agent
1. **Two-Epoch Firewall (`two_epoch_separation_mandate`)**: Execute Phases 1 through 4 (Epoch 1) as a **100% pure structural lift-and-shift** with zero behavioral mutations. Do NOT resolve the Epoch 2 12-Item Tech Debt Inventory until Phase 4 (Atomic Package Cutover and `QGR017` lockdown) is 100% complete and committed.
2. **Two-Phase Package Strangler Protocol (`strangler_fig_mandate`)**: Do NOT create `[NEW] @[backend_v2/services/matrix_parser/__init__.py]` during Phases 1, 2, or 3 while `@[backend_v2/services/matrix_domain_parser.py#L35-L206]` exists on disk (`Duplicate module named matrix_parser` / shadow package hazard). Create `[NEW] @[backend_v2/services/matrix_parser/__init__.py]` and delete `[DELETE] @[backend_v2/services/matrix_domain_parser.py]` atomically in Phase 4 Step 2.
3. **500-Line Partitioning Gate**: Every extracted sub-module (`@[backend_v2/services/matrix_parser/distribution_formatter.py#L26-L75]`, `@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L58-L191]`, `@[backend_v2/services/matrix_parser/row_builder_stage.py#L35-L75]`) and the package facade (`[NEW] @[backend_v2/services/matrix_parser/__init__.py]`) MUST remain strictly below 350 lines (and `< 150` lines for `__init__.py`).
4. **Atomic Checkpoints**: Run `uv run python scripts/backend_audit_loop.py <target> --test --ast-strict` after every phase and perform an atomic `git commit` before advancing to the next phase.

---

## Requirements Traceability Matrix

| Requirement ID | Architectural Requirement Description | Phase & Step Mapping | Verification Gate |
| :--- | :--- | :--- | :--- |
| `REQ-MDP-01` | Encapsulate intermediate stage outputs in immutable Pydantic V2 DTOs (`MatrixScaleProjectionDTO`, `MatrixAtomHydrationResultDTO`, `MatrixContextTargetResultDTO`) inside `@[backend_v2/models/dtos/matrix_parser.py#L106-L145]` | Phase 1, Step 1 | `backend_audit_loop.py backend_v2/models/dtos/matrix_parser.py --test --ast-strict` |
| `REQ-MDP-02` | Extract Model B level distribution, hallucinated number cleaning, level breakdown, and row explanation resolution into `@[backend_v2/services/matrix_parser/distribution_formatter.py#L26-L75]` | Phase 1, Step 2 | `backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test --ast-strict` |
| `REQ-MDP-03` | Delegate `_format_level_distribution`, `_clean_hallucinated_numbers`, and breakdown/explanation formatting in `@[backend_v2/services/matrix_domain_parser.py#L35-L206]` | Phase 1, Step 3 | `pytest backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py` |
| `REQ-MDP-04` | Extract matrix payload unpacking, scale/score projection, and TDA atom hydration into `@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L58-L191]` | Phase 2, Step 1 | `backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test --ast-strict` |
| `REQ-MDP-05` | Delegate payload unpacking, scale projection, and atom hydration in `@[backend_v2/services/matrix_domain_parser.py#L65-L206]` | Phase 2, Step 2 | `pytest backend_v2/tests/unit/services/test_blueprint.py -k "matrix"` |
| `REQ-MDP-06` | Extract axis label collision resolution, description resolution, three-tier context target resolution, and `MatrixScorecardRowDTO` construction into `@[backend_v2/services/matrix_parser/row_builder_stage.py#L35-L75]` | Phase 3, Step 1 | `backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test --ast-strict` |
| `REQ-MDP-07` | Delegate axis label, context target, and row building stages in `@[backend_v2/services/matrix_domain_parser.py#L65-L206]` | Phase 3, Step 2 | `backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test --ast-strict` |
| `REQ-MDP-08` | Split `[DELETE] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` into 4 modular test files under `backend_v2/tests/unit/services/matrix_parser/` | Phase 4, Step 1 | `pytest backend_v2/tests/unit/services/matrix_parser/` |
| `REQ-MDP-09` | Atomically cut over `[DELETE] @[backend_v2/services/matrix_domain_parser.py]` to `[NEW] @[backend_v2/services/matrix_parser/__init__.py]` and rewire all 1-hop consumer imports | Phase 4, Step 2 | `backend_audit_loop.py backend_v2/services/matrix_parser/ --test --ast-strict` |
| `REQ-MDP-10` | Ban `backend_v2.services.matrix_domain_parser` in `@[scripts/_ast_guardrails.py#L1865-L1897]` and `@[scripts/_ast_guardrails.py#L1899-L1977]` under `QGR017` and update `@[.agents/rules/04_directory_reference.md]` | Phase 4, Step 3 | `backend_audit_loop.py backend_v2/services/matrix_parser/ --test --ast-strict` |

---

# Session Handover Context

## Achieved
- Completed Phase 1 (`@[docs/epic/tasks_matrix_domain_parser/phase1_leaf_and_formatter_extraction.md]`):
  - Step 1: Defined immutable Pydantic V2 stage DTOs (`MatrixScaleProjectionDTO` `@[backend_v2/models/dtos/matrix_parser.py#L106-L145]`, `MatrixAtomHydrationResultDTO` `@[backend_v2/models/dtos/matrix_parser.py#L148-L165]`, and `MatrixContextTargetResultDTO` `@[backend_v2/models/dtos/matrix_parser.py#L168-L183]`) with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields.
  - Step 2: Extracted leaf formatter functions (`format_level_distribution` `@[backend_v2/services/matrix_parser/distribution_formatter.py#L26-L75]`, `clean_hallucinated_numbers` `@[backend_v2/services/matrix_parser/distribution_formatter.py#L78-L101]`, `format_level_breakdown` `@[backend_v2/services/matrix_parser/distribution_formatter.py#L104-L148]`, `resolve_row_explanation` `@[backend_v2/services/matrix_parser/distribution_formatter.py#L151-L199]`) without creating `backend_v2/services/matrix_parser/__init__.py`.
  - Step 3: Delegated `MatrixDomainParser._format_level_distribution` (`@[backend_v2/services/matrix_domain_parser.py#L38-L50]`), `MatrixDomainParser._clean_hallucinated_numbers` (`@[backend_v2/services/matrix_domain_parser.py#L52-L63]`), and level breakdown / row explanation resolution in `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L65-L206]`) to `backend_v2.services.matrix_parser.distribution_formatter`.
  - Completed and passed Tier 8 post-implementation audit (100% compliance, `red_team_audit_phase1_leaf_and_formatter_extraction.md`).
- Completed Phase 2 (`@[docs/epic/tasks_matrix_domain_parser/phase2_scale_and_atom_stage_extraction.md]`):
  - Step 1: Created `backend_v2/services/matrix_parser/scale_and_atom_stage.py` (310 lines, `< 320` lines) containing `unpack_matrix_payload` (`@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L32-L55]`), `compute_scale_and_score_projection` (`@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L58-L191]`), and `hydrate_step_scorecard_atoms` (`@[backend_v2/services/matrix_parser/scale_and_atom_stage.py#L194-L311]`).
  - Step 2: Delegated matrix payload unpacking, scale boundary and UI display score projection, and step scorecard TDA atom hydration in `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L65-L206]`) while preserving Fail-Fast exception ordering (`pb_meta.label` check prior to scale projection).
  - Completed and passed Tier 8 post-implementation audit (100% compliance, `red_team_audit_phase2_scale_and_atom_stage_extraction.md`).
- Completed Phase 3 (`@[docs/epic/tasks_matrix_domain_parser/phase3_row_builder_stage_extraction.md]`):
  - Step 1: Created `backend_v2/services/matrix_parser/row_builder_stage.py` (248 lines, `< 250` lines) containing `resolve_unique_axis_name` (`@[backend_v2/services/matrix_parser/row_builder_stage.py#L35-L75]`), `resolve_axis_description` (`@[backend_v2/services/matrix_parser/row_builder_stage.py#L78-L90]`), `resolve_context_target` (`@[backend_v2/services/matrix_parser/row_builder_stage.py#L93-L153]`), and `build_matrix_scorecard_row` (`@[backend_v2/services/matrix_parser/row_builder_stage.py#L156-L248]`).
  - Step 2: Delegated axis name/collision resolution, axis description resolution, three-tier deterministic context target resolution, and `MatrixScorecardRowDTO` construction in `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L65-L206]`), reducing `backend_v2/services/matrix_domain_parser.py` to a 206-line orchestrator facade.
  - Passed 10/10 Universal Quality Gate stages, 34/34 unit tests (`test_matrix_domain_parser.py`, 98% coverage on `matrix_domain_parser.py` and 91% coverage on `row_builder_stage.py`), 6/6 Blueprint matrix tests (`test_blueprint.py -k "matrix"`), 7/7 Tier 4 regression tests (`test_tier4_matrix_distribution_regression.py`), and `test_sdui_semantic_parity.py`.

## Learned
- Extracting `row_builder_stage.py` reduced `@[backend_v2/services/matrix_domain_parser.py#L35-L206]` from 352 lines to 206 lines (`parse_matrices` spans `#L65-L206`).
- Initializing `ext = TraceMatrixExtensionsDTO()` when `matrix_payload.extensions is None` in `build_matrix_scorecard_row` (`@[backend_v2/services/matrix_parser/row_builder_stage.py#L156-L248]`) eliminates 18 lines of repetitive `= None` assignments while keeping `row_builder_stage.py` at 248 lines (`< 250` lines) and maintaining 100% identical runtime values.
- `QGR016` flags inline ternary fallback expressions (`target_key if target_key in ("chat_log", "product_text") else "all"`); preserving the explicit `if/else` block passes `_ast_guardrails.py --strict` cleanly.

## Resume Command
`/tier8-audit-plan @[docs/epic/tasks_matrix_domain_parser/phase3_row_builder_stage_extraction.md] @[docs/epic/matrix_domain_parser_decomposition_tracker.md]`

## Remaining
- Execute Tier 8 Audit for Phase 3 (`@[docs/epic/tasks_matrix_domain_parser/phase3_row_builder_stage_extraction.md]`).
- Execute Phase 4 (`@[docs/epic/tasks_matrix_domain_parser/phase4_package_cutover_and_guardrails.md]`): Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown.
- Execute Epoch 2 Post-Cutover Tier 2 Hardening on the extracted `backend_v2/services/matrix_parser/` package and synchronize 1-hop caller `@[backend_v2/services/blueprint.py#L65-L669]`.
