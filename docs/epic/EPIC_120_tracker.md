# EPIC 120 Tracker: SDUI Strictness Hardening

**Original Epic**: @[c:\src\quorum\docs\epic\EPIC_120_database_driven_sdui_templates.md]
**Task Directory**: @[c:\src\quorum\docs\epic\tasks_EPIC_120\]

## Phase Execution Status

- [ ] **Phase 2: Frontend Freezed Sealed Class Synchronization**
  - [ ] `<step id="1">` Extract SduiBlockDTO to Shared Layer
  - [ ] `<step id="2">` Rewire Studio Imports
  - [ ] `<step id="3">` Rewire Execution Imports
  - [ ] `<step id="4">` Strict Deserialization Testing
- [ ] **Phase 1 & 4: Backend Model Strictness Hardening & Test Fixture Migration**
  - [ ] `<step id="1">` Update V2 Core Models
  - [ ] `<step id="2">` Update Output Profile DTOs
  - [ ] `<step id="3">` Test Fixture Migration
  - [ ] `<step id="4">` Seed Data Verification
- [ ] **Phase 3: Blueprint Generator & Worker Strictness Hardening**
  - [ ] `<step id="1">` Blueprint Generator Refactor
  - [ ] `<step id="2">` Synthesis Distiller Refactor
  - [ ] `<step id="3">` Worker Double-Serialization Removal

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK]** Backend Audit Loop Passes (`uv run python scripts/backend_audit_loop.py backend_v2/ --test`)
- [ ] **[NOK]** Frontend Audit Loop Passes (`uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`)

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_120_database_driven_sdui_templates.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- **Atomic commit mandates**: After ANY successful run of the `universal_quality_gate` audit script that passes, you MUST explicitly instruct the user to perform an atomic `git commit` BEFORE proceeding to the next file or logic block. Specify exact relative file paths.
- **Seeding environment commands**: `uv run python backend_v2/seed/run_seed.py local`
- **Reference syntax**: You MUST use `@-reference` syntax for all file paths.
- **Resume Command Update**: You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue.
- **Mandatory workflow loop**: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.

## Requirements Traceability Matrix
| Req ID | Requirement Description | Phase & Step Mapping |
|---|---|---|
| R1 | `OutputProfile.content_blocks` replaces `List<dynamic>` with `AnySduiBlock` (Backend) | Phase 1, Step 1 & 2 |
| R2 | `EmbeddedOutputProfile.content_blocks` replaces `List<dynamic>` with `AnySduiBlock` (Backend) | Phase 1, Step 1 |
| R3 | `OutputLayoutBlock.synthesis_blocks` typed to `list[AnySduiBlock] \| None` | Phase 1, Step 1 |
| R4 | `ReportLayoutDTO.synthesis_blocks` typed to `list[AnySduiBlock] \| None` | Phase 1, Step 1 |
| R5 | `RenderedSynthesisCache.content_blocks` typed to `list[AnySduiBlock]` | Phase 1, Step 1 |
| R6 | `RenderedSynthesisCache.section_syntheses` typed to `dict[str, list[AnySduiBlock]]` | Phase 1, Step 1 |
| R7 | `OutputProfile` DTOs updated to use `list[AnySduiBlock]` for `content_blocks` | Phase 1, Step 2 |
| R8 | Test fixtures mocked as dicts updated to models or discriminators | Phase 1, Step 3 |
| R9 | Seed data verification for `AnySduiBlock` | Phase 1, Step 4 |
| R10 | Flutter `SduiBlockDTO` extracted to `shared/models/sdui_block_dto.dart` | Phase 2, Step 1 |
| R11 | Flutter `SduiBlockDTO` adds 4 missing types: `quote_card`, `warning_card`, `n_a_card`, `grid` | Phase 2, Step 1 |
| R12 | Flutter `OutputProfile` and `EmbeddedOutputProfile` replace `List<dynamic>` with `List<SduiBlockDTO>` | Phase 2, Step 2 |
| R13 | Flutter `ReportLayoutDto` replaces `List<Map<String, dynamic>>?` with `List<SduiBlockDTO>?` | Phase 2, Step 3 |
| R14 | Strict Deserialization Testing for `SduiBlockDTO.fromJson` | Phase 2, Step 4 |
| R15 | Blueprint Generator removes duck-typing (`isinstance`, `hasattr`, `.get()`) and uses Pydantic methods | Phase 3, Step 1 |
| R16 | Synthesis Distiller serialization handles typed `AnySduiBlock` via `model_dump` | Phase 3, Step 2 |
| R17 | Worker removes double-serialization `model_dump()` + cast when saving cache | Phase 3, Step 3 |
| R18 | Worker catches `ValidationError` on LLM parsing and raises `AppException` | Phase 3, Step 3 |

# Session Handover Context
## Achieved
- Generated `EPIC_120_tracker.md` from implementation plans for EPIC 120.
- Extracted every technical requirement into a granular Requirements Traceability Matrix.

## Learned
- **MANDATORY Order of Execution**: Phase 2 (Frontend) MUST be executed BEFORE Phase 1 (Backend). The Python backend emits 9 AnySduiBlock types while Flutter only has 5. Deploying the backend first will crash the client via `disallowUnrecognizedKeys`.
- **Baseline State Snapshot**: `content_blocks` and `synthesis_blocks` currently use `list[dict[str, Any]]` and `List<dynamic>`. The blueprint generator (`c:\src\quorum\backend_v2\services\blueprint.py`) uses `isinstance(cb, dict)` and `c_block.get("id")`. Because `SduiBlockBase` lacks an `id` field, the `.get("id")` lookup logic MUST be redesigned during execution. Worker (`c:\src\quorum\backend_v2\worker.py`) does a double-serialization `model_dump()` cast on lines ~877-896.

## Remaining
- Begin execution with `/tier0-research-plan` on Phase 2 (Frontend Freezed Sealed Class Synchronization).

## Resume Command
`/tier5-resume --workflow=/tier0-research-plan --target="@[c:\src\quorum\docs\epic\EPIC_120_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_120\00_phase2_frontend_sealed_class_sync.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
