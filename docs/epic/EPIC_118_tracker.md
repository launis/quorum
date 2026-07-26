# EPIC 118: TDA Context-Enriched Decompose-Verify Pipeline - Tracker

**Epic Reference**: @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]
**Task Directory**: @[c:\src\quorum\docs\epic\tasks_EPIC_118\]

---

## Phase Execution Status

### Phase 0: Seed Data & Database Prerequisite / Migration
- [ ] **[NOK]** Red-Teaming (`/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\00_seed_data_plan.md]`)
- [ ] **[NOK]** Execution (`/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\00_seed_data_plan.md]`)
  - [ ] `1` (SKIP PHASE 0)

### Phase 1: Backend Domain Models & Service Engine Hardening
- [ ] **[NOK]** Red-Teaming (`/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_domain_models_plan.md]`)
- [ ] **[NOK]** Execution (`/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_domain_models_plan.md]`)
  - [ ] `1` (FlattenedAtom DTO Migration)
  - [ ] `2` (FlattenedAtom Hook Refactor)
  - [ ] `3` (Testing & Quality Gate Plan)

### Phase 2: Orchestration, Registry & Prompt Compiler Updates
- [ ] **[NOK]** Red-Teaming (`/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_orchestration_updates_plan.md]`)
- [ ] **[NOK]** Execution (`/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_orchestration_updates_plan.md]`)
  - [ ] `1` (LLM Strategy Hydration)
  - [ ] `2` (Context-Enriched Decompose-Verify Pipeline)
  - [ ] `3` (Testing & Quality Gate Plan)
  - [ ] `4` (Integration Checkpoint)

---

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK]** Backend and Frontend full-stack integration test gates.

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Atomic Commits**: You MUST perform an atomic `git commit` after ANY successful run of the `universal_quality_gate` audit script that passes, before proceeding to the next file or logic block. Git commit messages MUST ALWAYS be written in English.
2. **Seeding Environment**: If you need to re-seed the database, run: `uv run python backend_v2/seed/run_seed.py local`.
3. **Reference Syntax**: Use `@-reference` syntax (e.g., `@[c:\src\quorum\path\to\file.py]`) when referring to files in commands or prompts.
4. **Resume Command Update**: You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.

---

## Requirements Traceability Matrix

| Req ID | Description | Step ID (XML) |
|:---|:---|:---|
| R1 | `FlattenedAtom` model definition is moved to the DTO layer (`engine.py`). | Phase 1, Step 1 |
| R2 | `FlattenedAtom` uses `ConfigDict(strict=True, frozen=True, extra="ignore")`. | Phase 1, Step 1 |
| R3 | All fields in `FlattenedAtom` use PEP 593 `Annotated` syntax. | Phase 1, Step 1 |
| R4 | `EngineExecutionRequest` extends to include `shuffled_atoms: Annotated[list[FlattenedAtom] \| None, Field(default=None)]`. | Phase 1, Step 1 |
| R5 | `atom_flattening.py` hook is modified to import `FlattenedAtom` from the DTO layer. | Phase 1, Step 2 |
| R6 | Backend audit loop passes for `engine.py` and `atom_flattening.py`. | Phase 1, Step 3 |
| R7 | `llm.py` strategy replaces `if` check with unconditional direct key access `state_data["shuffled_atoms"]` when `is_matrix_step` is True. | Phase 2, Step 1 |
| R8 | `llm.py` hydrates the raw array using `TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False)`. | Phase 2, Step 1 |
| R9 | `llm.py` passes `shuffled_atoms=hydrated_shuffled_atoms` into the `EngineExecutionRequest` constructor. | Phase 2, Step 1 |
| R10 | `tda_engine.py` Matrix path executes Phase 0+1 to generate enriched context. | Phase 2, Step 2 |
| R11 | `tda_engine.py` Matrix path constructs `evaluation_context` with `<context>`, `<enriched_facts>`, and `<source_text>` XML wrappers. | Phase 2, Step 2 |
| R12 | `tda_engine.py` Matrix path maps predefined matrix atoms into `LinkedAtomGraph` nodes, explicitly preserving the predefined `tda_id`. | Phase 2, Step 2 |
| R13 | `tda_engine.py` uses module-level constant `_MATRIX_SOURCE_SENTINEL = "MATRIX"`. | Phase 2, Step 2 |
| R14 | `tda_engine.py` Matrix path sets `ExtractedAtom` nodes with `is_logical_deduction=True` and `source_quote=None`. | Phase 2, Step 2 |
| R15 | `tda_engine.py` Matrix path skips `SlidingWindowLinker` and passes `evaluation_context` to `EnrichedDagExecutor.execute_graph()`. | Phase 2, Step 2 |
| R16 | `tda_engine.py` Regular path preserves existing behavior using `SlidingWindowLinker` and `global_source_text`. | Phase 2, Step 2 |
| R17 | Progress callback ranges in `tda_engine.py` are adjusted to skip linker allocation for the Matrix path. | Phase 2, Step 2 |
| R18 | Explicit negative (`test_llm_strategy_missing_atoms_crash`, `test_tda_engine_invalid_shuffled_atoms_type`) and positive tests are added. | Phase 2, Step 3 |
| R19 | Full E2E REST API verification gate (`test_integration_real_llm.py`) is run and passes. | Phase 2, Step 4 |

---

# Session Handover Context
## Achieved
- Successfully generated the comprehensive EPIC 118 Tracker document from the drafted implementation plans.
- Established the Requirements Traceability Matrix linking specific implementation instructions to distinct requirements.

## Learned
- **Baseline State Snapshot**:
  - The bug currently causes matrix evaluation steps to produce empty matrix results because `TDAEngine` generates new UUIDs instead of using predefined `tda_id` values from the PromptBlock criteria.
  - `FlattenedAtom` is currently located in `atom_flattening.py`, violating the dependency rules and causing duck-typing upstream.
  - `llm.py` uses defensive `dict.get` style access rather than enforcing the Fail-Fast Hydration mandate.
  - `tda_engine.py` evaluates newly extracted atoms and discards matrix atoms.

## Remaining
- Proceed with Phase 1 Execution: migrating `FlattenedAtom` to the DTO layer in `engine.py` and updating the `atom_flattening.py` hook.

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\EPIC_118_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_domain_models_plan.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
