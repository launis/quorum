# Tracker: Canonical `id` Relational Sovereignty, Universal Entity Naming, `slug` Identification Ban, Zero-Default & Zero-Fallback Static Guardrails

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md] @[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]`
  - [x] Step 1: Phase 1: Enforce PEP 593 Annotated Fields & Expand Canonical ID / Slug / Zero-Default / Zero-Fallback AST Guardrails in _ast_guardrails.py
  - [x] Step 2: Phase 2: Enforce Canonical id Primary Keys, Universal Entity Display Names (name/label/title), Foreign Key REFERENCES (id), SQL Default Bans, and SQL slug Filter Bans in audit_zero_orm_strictness.py
  - [x] Step 3: Phase 3: Enforce 7-Collection Canonical id, Required Human-Readable Display Name (name/label), & Cross-Collection id Referential Integrity in audit_database_atoms.py
  - [x] Step 4: Phase 4: Codify Canonical ID Relations, Universal Entity Naming, Zero-Default & Zero-Fallback Inspection Mandate in tier2-hardening-backend SKILL.md
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md] @[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[scripts/_ast_guardrails.py]
  - [x] @[scripts/audit_zero_orm_strictness.py]
  - [x] @[scripts/audit_database_atoms.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"` (NA — zero frontend `.dart` targets in plan).
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the expanded `QGR016`, `QGR020`, `QGR030`, and `QGR031` AST guardrails in `@[scripts/_ast_guardrails.py]` (banning non-`None` defaults on identity/relational/naming/mode fields, `if x is None: x = <default>` service fallbacks, `Filter("slug", ...)` / `QueryCondition("slug", ...)`, `{x.slug: ...}` dict keys, `.slug` literal/ID comparisons, `.slug` in `logger.*`/`AppException`, `"PYTEST_CURRENT_TEST"` branching, and `self._local_*`/`self._deleted_*`/`self._memory_*` shadow state attributes), the `ZORM004` and `ZORM007` DDL/SQL checks in `@[scripts/audit_zero_orm_strictness.py]` (`CANONICAL_ENTITY_PK_TABLES`, `CANONICAL_NAMED_ENTITY_TABLES`, `REFERENCES <table>(id)`, SQL `DEFAULT` bans, and SQL `slug` `UNIQUE`/`WHERE`/`JOIN` bans), and the 7-collection `audit_canonical_entity_ids` verification in `@[scripts/audit_database_atoms.py]`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register the expanded canonical `id`, universal entity naming, zero-default, and zero-`slug` verification contracts in `scripts/_ast_guardrails.py`, `scripts/audit_zero_orm_strictness.py`, and `scripts/audit_database_atoms.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the canonical `id` primary key and foreign key sovereignty, universal human-readable entity naming (`name`, `label`, `title`), informational-only `slug` boundaries, and zero-default / zero-fallback static guardrails in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md] @[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[scripts/_ast_guardrails.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Migrate `AuditIssue` and `FullDatabaseAuditReport` in `@[scripts/audit_database_atoms.py#L116-L136]` and `@[scripts/audit_database_atoms.py#L139-L161]` to PEP 593 `Annotated[T, Field(...)]` and remove `"scripts/audit_database_atoms.py"` from `RESIDUAL_BARE_FIELD_FILES` in `@[scripts/_ast_guardrails.py#L897-L3929]`. | Step 1 | [x] Completed |
| REQ-002 | Define and export `RESIDUAL_LOCAL_SHADOW_STATE_FILES` and `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` in `@[scripts/_ast_guardrails.py#L897-L3929]`, sanitize default-value remediation strings in `QGR002` (`#L1375`), `QGR016` (`#L2284`, `#L3399`), and `QGR020` (`#L2618`), and enforce `FATAL` AST bans for non-`None` defaults on identity/relational/naming/mode fields (`QGR020`), `if x is None: x = <default>` service/router fallbacks (`QGR016`), `Filter("slug", ...)` / `QueryCondition("slug", ...)` (`QGR031`), `.slug` in `logger.*`/`AppException` (`QGR031`), `.slug` literal/ID comparisons (`QGR031`), `{x.slug: ...}` dictionary keys (`QGR031`), `"PYTEST_CURRENT_TEST"` branching (`QGR030`), and `self._local_*`/`self._deleted_*`/`self._memory_*` shadow state attributes (`QGR030`). | Step 1 | [x] Completed |
| REQ-003 | Add ISTQB positive and negative unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L3006-L3023]` verifying `QGR016`, `QGR020`, `QGR030`, and `QGR031` AST violations and compliant `.id` / `.slug == .slug` metadata checks. | Step 1 | [x] Completed |
| REQ-004 | Enforce `name TEXT NOT NULL` (without SQL `DEFAULT`) on `system_configs` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L82-L98]`. | Step 2 | [x] Completed (VERIFIED_EXISTING) |
| REQ-005 | Define and export `CANONICAL_ENTITY_PK_TABLES` and `CANONICAL_NAMED_ENTITY_TABLES` in `@[scripts/audit_zero_orm_strictness.py#L805-L825]` and enforce `id UUID PRIMARY KEY DEFAULT uuidv7()`, `CHECK (uuid_extract_version(id) = 7)`, required human-readable display column (`name`, `label`, `title`), `REFERENCES <table>(id)` foreign key targeting, SQL `DEFAULT` bans on `*_id`/`name`/`label`/`title`/`slug`/`storage_mode` columns (`ZORM004`), and `slug` bans in SQL `UNIQUE`, `WHERE`, and `JOIN ... ON` clauses (`ZORM007`). | Step 2 | [x] Completed |
| REQ-006 | Add ISTQB positive and negative unit tests in `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py#L203-L244]` covering `ZORM004` and `ZORM007` DDL and SQL AST checks. | Step 2 | [x] Completed |
| REQ-007 | Ensure `"name": "Tavily MCP Gateway"` is present on `sys_0195f3a00000700080008172bda70c86` in `@[backend_v2/seed/seed_data.json#L209-L218]`. | Step 3 | [x] Completed (VERIFIED_EXISTING) |
| REQ-008 | Define and export `SEED_COLLECTION_ALLOWED_PREFIXES`, `SEED_COLLECTION_REQUIRED_DISPLAY_FIELD`, `BANNED_ALTERNATIVE_PK_KEYS`, and `audit_canonical_entity_ids(data)` in `@[scripts/audit_database_atoms.py#L1119-L1312]`, wiring `audit_canonical_entity_ids` into `run_full_database_audit` to verify 7-collection `OPAQUE_STRIPE_ID_REGEX` primary keys, non-empty `name`/`label` display fields, absence of banned alternative PK keys, and cross-collection `id` referential integrity. | Step 3 | [x] Completed |
| REQ-009 | Add ISTQB positive and negative unit tests in `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py#L702-L714]` covering `audit_canonical_entity_ids`, `MISSING_CANONICAL_NAME`, `INVALID_CANONICAL_ID`, `DUPLICATE_CANONICAL_ID`, `BANNED_ALTERNATIVE_PK_FIELD`, and orphan foreign key detection. | Step 3 | [x] Completed |
| REQ-010 | Expand Invariant 2 under `EVIDENCE_BASED_INSPECTION_MANDATE` in `@[.agents/skills/tier2-hardening-backend/SKILL.md#L64-L74]` to `2. CANONICAL ID RELATIONS, UNIVERSAL ENTITY NAMING, ZERO-SLUG, ZERO-DEFAULT & ZERO-FALLBACK BAN` with zero ambiguous terms. | Step 4 | [x] Completed |

# Session Handover Context

## Achieved
- Executed all 4 steps (`REQ-001` through `REQ-010`) of `@[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]` and verified 100% physical compliance via `/tier8-audit-plan` (`red_team_audit_canonical_id_relations_and_zero_fallback_guardrails.md`, Commit `a808cf475`) with 100% Universal Quality Gate pass and line coverage >90% (`scripts/_ast_guardrails.py`: 95%, `scripts/audit_zero_orm_strictness.py`: 99%, `scripts/audit_database_atoms.py`: 98%).
- Executed `Tier 2 Hardening (Backend)` via `scripts/auto_hardening_runner.py` across all 3 target scripts:
  - `@[scripts/_ast_guardrails.py]` (Commit `9d9936fb8`): Verified 7-invariant hardening compliance and 95% line coverage.
  - `@[scripts/audit_zero_orm_strictness.py]` (Commit `aa1112ab6`): Hardened PEP 257 docstrings (`visit_Constant`), cleaned phase markers, updated CLI parser documentation to `ZORM001-ZORM007`, and verified 99% line coverage in `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`.
  - `@[scripts/audit_database_atoms.py]` (Commit `7372acbd1`): Removed redundant `Field(default="ERROR")` in `AuditIssue`, replaced `or` fallback operators with explicit ternary checks, added RFC 7807 Dual-Reporting (`logger.error(..., exc_info=True)` + `AppException` with `ErrorCodes.VALIDATION_FAILED`) on corrupt/non-object seed files in `run_full_database_audit`, and added ISTQB negative boundary tests in `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`.
- Executed `/tier7-describe-architecture` (Commit `da0b2b62d`), synchronizing `@[ki_god_code_prevention.md]` and its `metadata.json`, `@[.agents/rules/04_directory_reference.md]`, `@[docs/architecture/01_system_context_and_invariants.md]`, and `@[docs/architecture/02_data_seeding_and_ontology.md]`.
- **Step 1 (`REQ-001`, `REQ-002`, `REQ-003` — Commit `298865116`):** Migrated `AuditIssue` (`#L116-L136`) and `FullDatabaseAuditReport` (`#L139-L161`) in `@[scripts/audit_database_atoms.py]` to PEP 593 `Annotated[T, Field(...)]`, removed `"scripts/audit_database_atoms.py"` from `RESIDUAL_BARE_FIELD_FILES`, sanitized remediation strings in `QGR002`/`QGR016`/`QGR020`, and enforced `QGR016`, `QGR020`, `QGR030`, and `QGR031` in `@[scripts/_ast_guardrails.py]` with ISTQB tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`.
- **Step 2 (`REQ-004`, `REQ-005`, `REQ-006` — Commit `784d2a6dd`):** Verified `name TEXT NOT NULL` on `system_configs` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L82-L98]` and enforced `CANONICAL_ENTITY_PK_TABLES`, `CANONICAL_NAMED_ENTITY_TABLES`, `ZORM004`, and `ZORM007` in `@[scripts/audit_zero_orm_strictness.py]` with ISTQB tests in `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`.
- **Step 3 (`REQ-007`, `REQ-008`, `REQ-009` — Commit `6ab29042e`):** Verified `"name": "Tavily MCP Gateway"` in `@[backend_v2/seed/seed_data.json#L209-L218]` and implemented `SEED_COLLECTION_ALLOWED_PREFIXES`, `SEED_COLLECTION_REQUIRED_DISPLAY_FIELD`, `BANNED_ALTERNATIVE_PK_KEYS`, and `audit_canonical_entity_ids` in `@[scripts/audit_database_atoms.py#L1119-L1312]` with ISTQB tests in `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`.
- **Step 4 (`REQ-010` — Commit `d6a8762f6`):** Updated Invariant 2 under `EVIDENCE_BASED_INSPECTION_MANDATE` in `@[.agents/skills/tier2-hardening-backend/SKILL.md#L64-L74]`, synchronized `@[ki_god_code_prevention.md]`, and updated `@[.agents/rules/04_directory_reference.md#L120]`.

## Learned
- `scripts/audit_warning_baseline.py` Census `P` scans all `.py` files in `backend_v2/tests/` and `scripts/` for raw regex `\b[Dd]ict\[\s*str\s*,\s*(?:Any|object)\s*\]` (including inside multiline string literals in test files).
- `test_audit_zero_reflection` in `backend_v2/tests/unit/scripts/test_audit_database_atoms.py` and `scripts/audit_dict_eradication.py` enforce zero `getattr`/`hasattr`/`setattr`, zero `.get()`, and zero `isinstance(..., dict)` across `scripts/audit_database_atoms.py`; using `collections.abc.Mapping` and `collections.abc.Sequence` indexing satisfies all guardrails cleanly.
- `scripts/audit_markdown_boundaries.py --fix` writes Windows CRLF (`\r\n`) line endings via `Path.write_text()`; using `write_file(Overwrite=True)` avoids `edit_file` LF/CRLF target mismatches on tracker updates.

## Remaining
- None — all implementation steps (`REQ-001` through `REQ-010`), Tier 2 Backend Hardening passes, Tier 7 As-Built Architectural Sync, and Tier 8 Final Plan Audit are 100% complete.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md] @[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]
```
