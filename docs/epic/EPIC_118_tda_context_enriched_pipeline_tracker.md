# EPIC 118 Tracker: TDA Context-Enriched Decompose-Verify Pipeline

## Phase Execution Status

### Phase 0: Seed Data & Database Prerequisite / Migration
- `[ ]` /tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\00_phase_0_seed_data.md]
- `[x]` /tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\00_phase_0_seed_data.md]
  - `[x]` `phase_0.1` (N/A - no seed changes needed)

### Phase 1: Backend Domain Models & Service Engine Hardening
- `[ ]` /tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_phase_1_backend_domain_models.md]
- `[x]` /tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_phase_1_backend_domain_models.md]
  - `[x]` `phase_1.1`
  - `[x]` `phase_1.2`

### Phase 2: Orchestration, Registry & Prompt Compiler Updates
- `[x]` /tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_phase_2_orchestration_registry.md]
- `[ ]` /tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_phase_2_orchestration_registry.md]
  - `[x] (85af2832)` `phase_2.1`
  - `[x] (85af2832)` `phase_2.2`

### Phase 3: Frontend Flutter UI & Freezed DTO Synchronization
- `[ ]` /tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\03_phase_3_frontend.md]
- `[ ]` /tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\03_phase_3_frontend.md]
  - `[ ]` `phase_3.1`

### Phase 4: Verification & E2E Integration Gate
- `[ ]` /tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\04_phase_4_verification.md]
- `[ ]` /tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\04_phase_4_verification.md]
  - `[ ]` `phase_4.1`

### Phase 5: Dual-Axis Documentation Update (EPIC 115 Compliance)
- `[ ]` /tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\05_phase_5_documentation.md]
- `[ ]` /tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\05_phase_5_documentation.md]
  - `[ ]` `phase_5.1`

### Integration Checkpoint: Full-Stack Validation
- `[ ]` **[NOK] Backend and Frontend full-stack integration test gates.**

### Post-Implementation Gates
- `[ ]` **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- `[ ]` **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- `[ ]` **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- `[ ]` **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- `[ ]` **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- `[ ]` **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

### Documentation & Knowledge Item Update
- `[ ]` **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- `[ ]` **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- `[ ]` **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Requirements Traceability Matrix

| Req ID | Requirement Description | XML Step ID | Target File | Status |
| :--- | :--- | :--- | :--- | :--- |
| R1 | Move `FlattenedAtom` model definition into the DTO layer to enforce No Naked Dicts rule | `phase_1.1` | `@[c:\src\quorum\backend_v2\models\dtos\engine.py]` | Complete |
| R2 | FlattenedAtom MUST use PEP 593 Annotated syntax for all fields | `phase_1.1` | `@[c:\src\quorum\backend_v2\models\dtos\engine.py]` | Complete |
| R3 | Update `test_engine.py` for new `FlattenedAtom` model with positive/negative tests | `phase_1.1` | `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_engine.py]` | Complete |
| R4 | Remove the `FlattenedAtom` definition from `atom_flattening.py` and import from DTO layer | `phase_1.2` | `@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]` | Complete |
| R5 | Update imports in `test_atom_flattening.py` to use new DTO location | `phase_1.2` | `@[c:\src\quorum\backend_v2\tests\unit\hooks\test_atom_flattening.py]` | Complete |
| R6 | Safely parse `state_data["shuffled_atoms"]` when `is_matrix_step` is True via KeyError catch | `phase_2.1` | `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]` | Complete |
| R7 | Raise explicit AppException on KeyError for `state_data["shuffled_atoms"]` | `phase_2.1` | `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]` | Complete |
| R8 | Validate `raw_atoms` with `TypeAdapter(list[FlattenedAtom]).validate_python(..., strict=False)` | `phase_2.1` | `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]` | Complete |
| R9 | Pass hydrated `shuffled_atoms` to BOTH `EngineExecutionRequest` constructors | `phase_2.1` | `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]` | Complete |
| R10 | Implement Context-Enriched Decompose-Verify Pipeline in `TDAEngine.execute()` Matrix path | `phase_2.2` | `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]` | Complete |
| R11 | Construct `evaluation_context` using strict XML boundaries for enriched facts and source_text | `phase_2.2` | `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]` | Complete |
| R12 | Map `FlattenedAtom` objects to `ExtractedAtom` models with empty `depends_on` | `phase_2.2` | `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]` | Complete |
| R13 | Bypass `SlidingWindowLinker` for Matrix path (due to independent matrix assertions) | `phase_2.2` | `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]` | Complete |
| R14 | Use `_MATRIX_SOURCE_SENTINEL` constant instead of hardcoded strings | `phase_2.2` | `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]` | Complete |
| R15 | Update `test_tda_engine.py` with matrix and regular execution paths tests | `phase_2.2` | `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\engines\test_tda_engine.py]` | Complete |

## Instructions for the Execution Agent
- Atomic commit mandates: You MUST perform an atomic `git commit` after ANY successful run of the `universal_quality_gate` audit script that passes. NEVER propose `git add .`.
- Seeding environment command: Execute `uv run python backend_v2/seed/run_seed.py local` to reset database if required.
- `@-reference` syntax rule: Always explicitly wrap all target file paths in `@-reference` syntax.
- You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue.

# Session Handover Context
## Achieved
- Executed Phase 2.1: `llm.py` safely parses `shuffled_atoms` via TypeAdapter with explicit AppException error boundaries.
- Executed Phase 2.2: `TDAEngine.execute()` properly bypasses the Atomizer Phase 1 and `SlidingWindowLinker` for matrix execution paths, mapping `FlattenedAtom` instances to synthetic, independent `ExtractedAtom` schemas. Evaluation context is constructed dynamically with static-first tag boundaries.
- Test suites (`test_llm.py`, `test_tda_engine.py`) have been rewritten to cover both matrix execution paths and exception branches.
- Code has been fully verified using the `backend_audit_loop.py` and committed.

## Learned
- **Architectural Checkpoint**: `EngineExecutionRequest` requires `shuffled_atoms` as a fully hydrated Pydantic list (no naked dicts).
- **Testing Mocks**: `ExtractedAtom` schemas enforce rigorous regex constraints on `tda_id` (e.g. `^tda_[a-fA-F0-9]{8,32}$`); mocking must ensure proper prefixes to satisfy Pydantic validations during Matrix testing.

## Remaining
- Execute Phase 3 (`tasks_EPIC_118/03_phase_3_frontend.md`): Frontend Flutter UI & Freezed DTO Synchronization.
- The next executing agent should follow `/tier2-execute` for `03_phase_3_frontend.md`.

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_118\03_phase_3_frontend.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
