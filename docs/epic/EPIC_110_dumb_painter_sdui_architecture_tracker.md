# EPIC 110: Dumb Painter SDUI Architecture Tracker

**Epic Document:** @[c:\src\quorum\docs\epic\EPIC_110_dumb_painter_sdui_architecture.md]
**Task Directory:** @[c:\src\quorum\docs\epic\tasks_EPIC_110/]

## Phase Execution Status

### Phase 1 & 2: Backend Architecture & Seed Data Migration
- `[x]` **[OK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_110\01_backend_architecture_and_seed_plan.md]`
- `[x]` **[OK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_110\01_backend_architecture_and_seed_plan.md]`

### Phase 3: Backend Blueprint
- `[x]` **[OK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_110\02_backend_blueprint_plan.md]`
- `[x]` **[OK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_110\02_backend_blueprint_plan.md]`

### Phase 1 & 2: Frontend Models & Renderer
- `[x]` **[OK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_110\03_frontend_models_and_renderer_plan.md]`
- `[x]` **[OK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_110\03_frontend_models_and_renderer_plan.md]`

### Phase 4: Frontend UI Editor
- `[ ]` **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_110\04_frontend_ui_editor_plan.md]`
- `[ ]` **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_110\04_frontend_ui_editor_plan.md]`

### Integration Checkpoint: Full-Stack Validation
- `[ ]` **[NOK]** Run End-to-End backend evaluation and verify payload outputs match the newly updated strictly-typed schemas.

### Post-Implementation Gates
- `[ ]` **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- `[ ]` **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created or modified `@-referenced` backend files. NEVER specify whole directories to avoid auditing untouched files.
- `[ ]` **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created or modified `@-referenced` Flutter files. NEVER specify whole directories to avoid auditing untouched files.
- `[ ]` **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- `[ ]` **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- `[ ]` **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- `[ ]` **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.
- `[ ]` **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- `[ ]` **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_110_dumb_painter_sdui_architecture.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- Enforce Atomic Commits for all functional blocks.
- Run DB seeding via explicit environment command: `uv run python backend_v2/seed/run_seed.py local`
- You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.
- Always use bounded `@-reference` links for large files (e.g. `@[c:\src\quorum\backend_v2\seed\seed_data.json#L1-L800]`) to prevent context amnesia crashes.
- Do NOT mix Backend (Python) and Frontend (Flutter) changes in the same plan.

## Requirements Traceability Matrix

| Requirement | Epic Phase | Mapped Plan | Status |
| ----------- | ---------- | ----------- | ------ |
| Jinja PDF Deduplication | Phase 1 | `01_backend_architecture_and_seed_plan.md` | Done |
| Add `matrix_column_labels` and `extension_labels` | Phase 2 | `01_backend_architecture_and_seed_plan.md` | Done |
| Migrate `seed_data.json` layout blocks | Phase 2 | `01_backend_architecture_and_seed_plan.md` | Done |
| Delegate title resolution in `blueprint.py` | Phase 3 | `02_backend_blueprint_plan.md` | Done |
| Remove Flutter duct-tape | Phase 1 | `03_frontend_models_and_renderer_plan.md` | Done |
| Flutter Models Sync | Phase 2 | `03_frontend_models_and_renderer_plan.md` | Done |
| 3-Part UI Refactor | Phase 4 | `04_frontend_ui_editor_plan.md` | Pending |

# Session Handover Context
## Achieved
- Conducted Epic 110 research (Tier 1).
- Inspected the current architectural state of `report_template.jinja2`, `report_renderer_v2_widget.dart`, `v2_core.py`, `output_profile.dart`, `layout_editor_card.dart`, and `blueprint.py`.
- Identified that `matrix_column_labels` and `extension_labels` are completely missing from the existing `OutputLayoutBlock` models.
- Split the Epic execution into isolated Micro-Chunks (Plans).
- Generated implementation plans for Phase 1 & 2 (Backend Models/Jinja/Seed) and Phase 3 (Blueprint Delegation).
- Generated placeholder files for Frontend Plans to avoid context oversaturation, which will require a subsequent Tier 1 pass later.
- Executed Phase 1 & 2 Backend Architecture updates.
  - Added `matrix_column_labels` and `extension_labels` to `OutputLayoutBlock` (`v2_core.py`).
  - Migrated `seed_data.json` successfully with new label fields.
  - Refactored `report_template.jinja2` to remove hardcoded Finnish strings and use `l10n` placeholders.
  - Passed strict backend and seed data audit loops.
- Executed Phase 3 Backend Blueprint mapping updates:
  - Resolved `matrix_column_labels` and `extension_labels` from `OutputLayoutBlock` and mapped them directly into `ReportLayoutDTO`.
  - Fixed the Amnesia Bug by preventing raw_score overwrite when an AI score already exists.
  - Passed strict backend audit loop (MyPy strict and Pytest).
- Executed Phase 1 & 2 Frontend Models & Renderer updates:
  - Added `matrixColumnLabels` and `extensionLabels` nullable map fields to `OutputLayoutBlock` in `output_profile.dart`.
  - Stripped out "2.5 Global Synthesis" logic from `report_renderer_v2_widget.dart` to match Dumb Painter rules.
  - Dynamically injected `resolvedTitle` from `payload.contentBlocks` without using localized defaults.
  - Generated Freezed `build_runner` files and passed flutter audit gate.

## Learned
- Seed data size is ~533KB, requiring careful parsing and bounded reading via grep or line limits to prevent truncation.
- The `OutputLayoutBlock` model resides in `backend_v2/models/v2_core.py` (Python) and `client_app_v2/lib/features/studio/models/output_profile.dart` (Flutter).
- `blueprint.py` handles the main ReportDataDTO mapping, and now correctly cascades UI label configurations down to the layout payloads.
- SDUI enforces no layout assumptions on frontend, strict reliance on `block['resolved_title']`.

## Remaining
- Execute Phase 4 Frontend UI Editor implementation plan to support term authoring in `layout_editor_card.dart`.

## Resume Command
/tier5-resume --workflow=/tier0-research-plan --target="@[c:\src\quorum\docs\epic\EPIC_110_dumb_painter_sdui_architecture_tracker.md] @[c:\src\quorum\docs\epic\EPIC_110_dumb_painter_sdui_architecture.md] @[c:\src\quorum\docs\epic\tasks_EPIC_110\04_frontend_ui_editor_plan.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\02_flutter_desktop.md]"
