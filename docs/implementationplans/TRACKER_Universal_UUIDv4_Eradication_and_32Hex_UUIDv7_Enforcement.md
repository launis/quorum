# Tracker: Universal Eradication of Legacy UUIDv4 Generators & Full 32-Hex RFC 9562 UUIDv7 Enforcement

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md] @[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]`
  - [x] Step 1: Phase 1: Flutter Client UUIDv7 SSOT, StrictOpaqueIdConverter Lock & DGR003/DGR008 Technical Debt Cleanup
  - [x] Step 2: Phase 2: Backend Core UUIDv7 Primitive & Domain Model Default Factories
  - [x] Step 3: Phase 3: Backend Services, Repositories, Hooks, LLM & Test Doubles UUIDv4 Eradication
  - [x] Step 4: Phase 4: Static AST (QGR030) & Dart (DGR008) Guardrail Enforcement
  - [x] Step 5: Phase 5: Rules, Knowledge Items & Tier 2 Hardening Skills Synchronization
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md] @[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/database/repositories/audit.py]
  - [x] @[backend_v2/database/repositories/execution.py]
  - [x] @[backend_v2/database/repositories/knowledge.py]
  - [x] @[backend_v2/hooks/linguistics.py]
  - [x] @[backend_v2/hooks/llm.py]
  - [x] @[backend_v2/hooks/references.py]
  - [x] @[backend_v2/llm/client.py]
  - [x] @[backend_v2/llm/mock_data.py]
  - [x] @[backend_v2/llm/provider/litellm_response_stage.py]
  - [x] @[backend_v2/models/auth.py]
  - [x] @[backend_v2/models/chunking.py]
  - [x] @[backend_v2/models/core_base.py]
  - [ ] @[backend_v2/models/domain/base.py]
  - [ ] @[backend_v2/models/domain/matrix.py]
  - [ ] @[backend_v2/models/state.py]
  - [ ] @[backend_v2/services/auth/organization_service.py]
  - [ ] @[backend_v2/services/auth/user_service.py]
  - [ ] @[backend_v2/services/drivers/local_file_driver.py]
  - [ ] @[backend_v2/services/mcp/dispatcher.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]
  - [ ] @[backend_v2/services/orchestrator/two_pass_atomizer.py]
  - [ ] @[backend_v2/services/usage_service.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/_dart_guardrails.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block.dart]
  - [ ] @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]
  - [ ] @[client_app_v2/lib/utils/json_converters.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the universal eradication of `uuid.uuid4()` and `Uuid().v4()`, the canonical `generate_uuid7()` helper in `backend_v2/models/core_base.py`, `generateOpaqueUuid7(prefix)` in `client_app_v2/lib/utils/json_converters.dart`, and the `QGR030` / `DGR008` static guardrails banning version-4 UUID generation.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register `client_app_v2/test/unit/utils/json_converters_test.dart` and the `generate_uuid7()` / `generateOpaqueUuid7()` SSOT primitives.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing 32-hex RFC 9562 UUIDv7 identifier generation across Backend and Frontend in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md] @[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/settings.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Tighten `StrictOpaqueIdConverter` to 32-hex `r'^[a-z]{2,5}_[a-f0-9]{32}$'`, add `generateOpaqueUuid7(String prefix)` in `@[client_app_v2/lib/utils/json_converters.dart]`, migrate Flutter Studio widgets/cloner/models (`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]`, `@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`), and update Flutter test fixtures and `@[client_app_v2/test/unit/utils/json_converters_test.dart]`. | Step 1 | [x] Completed |
| REQ-002 | Extract `generate_uuid7(timestamp_ms: int \| None = None) -> uuid.UUID` in `@[backend_v2/models/core_base.py]`, migrate domain model default factories in `@[backend_v2/models/auth.py]`, `@[backend_v2/models/domain/base.py]`, `@[backend_v2/models/domain/matrix.py]`, `@[backend_v2/models/chunking.py]`, and `@[backend_v2/models/state.py]`, and add unit tests in `@[backend_v2/tests/unit/models/test_core_base.py]`. | Step 2 | [x] Completed |
| REQ-003 | Replace `uuid.uuid4()` with `generate_opaque_id(EntityPrefix.<TYPE>)` and `generate_uuid7()` across backend services, repositories, hooks, LLM providers, model factories, and repository fakes, and scope test patches in `@[backend_v2/tests/unit/hooks/test_references.py]` and `@[backend_v2/tests/unit/test_references.py]`. | Step 3 | [x] Completed |
| REQ-004 | Enforce `QGR030` in `@[scripts/_ast_guardrails.py]` blocking `uuid.uuid4` / `uuid4` in domain code and `DGR008` in `@[scripts/_dart_guardrails.py]` blocking `.v4(` in handwritten Dart files, with unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` and `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]`. | Step 4 | [x] Completed |
| REQ-005 | Synchronize `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/02_flutter_desktop.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[.agents/skills/tier2-hardening-backend/SKILL.md]`, `@[.agents/skills/tier2-hardening-frontend/SKILL.md]`, `@[.agents/skills/tier2-hardening-knowledge/SKILL.md]`, `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]`, and Knowledge Items to enforce 32-hex RFC 9562 UUIDv7 parity. | Step 5 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Steps 1 through 5 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` with 4 atomic commits (`8ee9bce02`, `8e618981d`, `0e534720a`, `265eeaaef`) plus the Step 5 rules/skills/KI synchronization commit.
- Tightened `StrictOpaqueIdConverter` to 32-hex and added `generateOpaqueUuid7(String prefix)` in `@[client_app_v2/lib/utils/json_converters.dart]`, migrating all Flutter Studio widgets, cloners, models, and test fixtures.
- Extracted `generate_uuid7(timestamp_ms: int | None = None) -> uuid.UUID` in `@[backend_v2/models/core_base.py]`, and eradicated `uuid.uuid4()` across all domain models, services, repositories, hooks, LLM modules, model factories, and repository fakes.
- Added static AST guardrail `QGR030` in `@[scripts/_ast_guardrails.py]` banning `uuid.uuid4` / `uuid4` in domain code and Dart guardrail `DGR008` in `@[scripts/_dart_guardrails.py]` banning `.v4(` in handwritten Dart files.
- Synchronized `.agents/rules/`, Tier 2 hardening skills, and `<appDataDir>/knowledge/` artifacts, and passed both global completion gates (`flutter_audit_loop.py client_app_v2/ --build` and `backend_audit_loop.py backend_v2/ --test` with 6566 passed tests and 97.34% coverage).
- Completed `/tier8-audit-plan` (`d27fc6fc2`) and `/tier7-describe-architecture`, synchronizing `docs/architecture/01_system_context_and_invariants.md`, `docs/architecture/02_data_seeding_and_ontology.md`, `docs/architecture/05_resilience_and_observability.md`, `docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md`, `@[.agents/rules/04_directory_reference.md]`, and Knowledge Base metadata.

## Learned
- Both `StrictOpaqueIdConverter` on the Flutter client and `OPAQUE_STRIPE_ID_REGEX` / `PostgresEntityAdapter` on the Python backend enforce 32-hex RFC 9562 UUIDv7 identifiers (`^[a-z]{2,5}_[a-f0-9]{32}$` with version nibble `7`).
- Updating `two_pass_atomizer.py` to generate 32-hex `tda_` IDs via `generate_opaque_id(EntityPrefix.TDA)` required updating the length assertion in `@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]` from `12` (`tda_` + 8-hex) to `36` (`tda_` + 32-hex).

## Remaining
- Execute genuine AI-driven Tier 2 Hardening (`scripts/auto_hardening_runner.py` evaluating all ~180 `<rule_block>` requirements + Subsystem KIs per file) across all 24 Backend targets and 7 Frontend targets.

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]" --gate all --model gemini-4-argon-medium --continue-on-failure
```
