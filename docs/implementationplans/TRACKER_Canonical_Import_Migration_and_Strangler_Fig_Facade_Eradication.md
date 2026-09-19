# Tracker: Canonical Import Migration & Strangler Fig Facade Eradication

@[docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md]

- [ ] **[NOK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md] @[docs/implementationplans/TRACKER_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md]`
  - [x] Step 1: PRE_IMPLEMENTATION_CLEANUPS_AND_DTO_CREATION
  - [x] Step 2: CANONICAL_SYMBOL_MAPPING_AND_MIGRATION_SCRIPT
  - [ ] Step 3: MIGRATE_PRODUCTION_CALLERS_BATCH_A
  - [ ] Step 4: MIGRATE_TEST_CALLERS_BATCH_B
  - [ ] Step 5: PERMANENTLY_PURGE_V2_CORE
  - [ ] Step 6: STREAMLINE_EXECUTION_INIT_FACADE
  - [ ] Step 7: STREAMLINE_WORKER_ENTRYPOINT_FACADE
  - [ ] Step 8: AST_GUARDRAIL_LOCKDOWN_AND_AUDIT
  - [ ] Step 9: KNOWLEDGE_BASE_AND_KI_SYNCHRONIZATION
  - [ ] Step 10: AS_BUILT_ARCHITECTURE_AND_DIRECTORY_REFERENCE_SYNC

- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md] @[docs/implementationplans/TRACKER_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md]`

---

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files.
  - [ ] @[backend_v2/models/dtos/workflow_schema.py]
  - [ ] @[scripts/migrate_v2_core_imports.py]
  - [ ] @[backend_v2/models/domain/synthesis.py]
  - [ ] @[backend_v2/models/dtos/report_data.py]
  - [ ] @[backend_v2/models/domain/matrix.py]
  - [ ] @[backend_v2/models/domain/execution.py]
  - [ ] @[backend_v2/models/view/sdui.py]
  - [ ] @[backend_v2/services/execution/__init__.py]
  - [ ] @[backend_v2/services/execution/ingress_service.py]
  - [ ] @[backend_v2/services/execution/resumption_service.py]
  - [ ] @[backend_v2/services/execution/override_service.py]
  - [ ] @[backend_v2/services/execution/legacy_render_service.py]
  - [ ] @[backend_v2/services/execution/lifecycle_service.py]
  - [ ] @[backend_v2/services/execution/context_service.py]
  - [ ] @[backend_v2/worker.py]
  - [ ] @[backend_v2/api/routers/execution/workflows.py]
  - [ ] @[backend_v2/services/execution/facade.py]
  - [ ] @[scripts/_ast_guardrails.py]

- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files.

- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain after v2_core.py permanent deletion.

- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic via `uv run pytest backend_v2/tests/ --cov=backend_v2.models --cov=backend_v2.services.execution --cov-report=term-missing`.

---

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (specifically: @[docs/architecture/00_README_META_ARCHITECTURE.md], @[docs/architecture/01_system_context_and_invariants.md], @[docs/architecture/03_cognitive_orchestration_engine.md], @[docs/architecture/04_server_driven_ui_and_presentation.md]), update Knowledge Items (@[ki_god_code_prevention.md], @[ki_tripartite_pipeline_architecture.md], @[ki_zero_permissive_typing.md]), and synchronize @[.agents/rules/04_directory_reference.md].

---

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md] @[docs/implementationplans/TRACKER_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

---

## Instructions for the Execution Agent

### Pre-Flight Mandatory Actions
1. **Context Rules Governance**: Load `<required_context_rules>` from both the plan and this tracker on every session start.
2. **KI Pre-Read**: Before modifying models or services, physically `view_file` @[ki_god_code_prevention.md], @[ki_tripartite_pipeline_architecture.md], and @[ki_zero_permissive_typing.md].
3. **AST Guardrail Check**: Ensure `scripts/_ast_guardrails.py` is executable and run baseline audit before modifying imports.

### Execution Governance
- **Atomic Commits**: After EVERY successful step or `backend_audit_loop.py` run, perform `git add <specific_files>; git commit -m "<conventional commit>"`.
- **Quality Gates**: `uv run python scripts/backend_audit_loop.py backend_v2 --test` after Python edits.
- **Session Handovers**: Execute `/tier5-session-handover` if modifying >5 distinct complex files or processing >8 prompts.
- **Execution Mode**: Step-by-Step by default. Invoke `/tier2-execute --full-auto` for continuous execution across all steps.
- **Tracker Updates**: Mark steps `[x]` in this tracker after each successful step completion.

### Resume Command Format
```
/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md] @[docs/implementationplans/TRACKER_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md]
```

---

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
|---|---|---|---|
| REQ-001 | Eradicate `WorkflowSchemaResponse = dict[str, Any]` in favor of `WorkflowSchemaResponseDTO` | Step 1 | [ ] Pending |
| REQ-002 | Purge dead circular import `ScorecardAtomDTO` in `execution.py#L23` and unused TYPE_CHECKING imports | Step 1 | [ ] Pending |
| REQ-003 | Preserve mandatory `AnySduiBlock` under `if TYPE_CHECKING:` in `matrix_scorecard.py#L19-L21` | Step 1 | [ ] Pending |
| REQ-004 | Co-locate Pydantic `model_rebuild()` forward-reference resolutions in home modules | Step 1 | [ ] Pending |
| REQ-005 | Build deterministic AST codemod script `scripts/migrate_v2_core_imports.py` with multi-scope traversal | Step 2 | [ ] Pending |
| REQ-006 | Migrate 80 production callers from `backend_v2.models.v2_core` to canonical domain modules | Step 3 | [ ] Pending |
| REQ-007 | Migrate 170 test callers from `backend_v2.models.v2_core` to canonical domain modules and delete proxy test | Step 4 | [ ] Pending |
| REQ-008 | Permanently delete `backend_v2/models/v2_core.py` (`git rm`) | Step 5 | [ ] Pending |
| REQ-009 | Streamline `services/execution/__init__.py`, purge 12 borrowed re-exports, decouple subservices and mock patches | Step 6 | [ ] Pending |
| REQ-010 | Streamline `worker.py` entrypoint, purge coroutine re-exports from `__all__`, update test callers | Step 7 | [ ] Pending |
| REQ-011 | Implement AST Guardrail QGR017 with FATAL severity banning `v2_core` imports | Step 8 | [ ] Pending |
| REQ-012 | Delete temporary migration script `scripts/migrate_v2_core_imports.py` after audit | Step 8 | [ ] Pending |
| REQ-013 | Synchronize Knowledge Items (`ki_god_code_prevention.md`, `ki_tripartite_pipeline_architecture.md`, `ki_zero_permissive_typing.md`) | Step 9 | [ ] Pending |
| REQ-014 | Synchronize Architecture Pillars (`docs/architecture/`) and `04_directory_reference.md` in timeless present tense | Step 10 | [ ] Pending |

---

# Session Handover Context

## Achieved
- Tier 0 Research Plan completed with 100% zero-shortening and zero-deferral invariants enforced.
- Created canonical implementation plan at `docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md`.
- Generated double-entry bookkeeping tracker at `docs/implementationplans/TRACKER_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md`.
- Mapped 14 granular requirements to all 10 plan steps in the Requirements Traceability Matrix.

## Learned
- `matrix_scorecard.py#L19-L21` requires `AnySduiBlock` under `if TYPE_CHECKING:` for MyPy strict compliance on line 297 (`inner_sdui_blocks`).
- `execution.py#L23` contains an unreferenced `ScorecardAtomDTO` import that induces circular imports when `matrix_scorecard.py` imports `system_config.py`.
- `ingress_service.py` returns naked dict `WorkflowSchemaResponse = dict[str, Any]` at `/workflows/{workflow_id}/ui_schema`, which must be converted to `WorkflowSchemaResponseDTO`.
- `services/execution/__init__.py` borrows 12 external symbols that must be cleaned to isolate the execution package.
- `worker.py` re-exports coroutines in `__all__` which duplicates `backend_v2.workers.*`.

## Remaining
- Step 1: PRE_IMPLEMENTATION_CLEANUPS_AND_DTO_CREATION
- Step 2: CANONICAL_SYMBOL_MAPPING_AND_MIGRATION_SCRIPT
- Step 3: MIGRATE_PRODUCTION_CALLERS_BATCH_A
- Step 4: MIGRATE_TEST_CALLERS_BATCH_B
- Step 5: PERMANENTLY_PURGE_V2_CORE
- Step 6: STREAMLINE_EXECUTION_INIT_FACADE
- Step 7: STREAMLINE_WORKER_ENTRYPOINT_FACADE
- Step 8: AST_GUARDRAIL_LOCKDOWN_AND_AUDIT
- Step 9: KNOWLEDGE_BASE_AND_KI_SYNCHRONIZATION
- Step 10: AS_BUILT_ARCHITECTURE_AND_DIRECTORY_REFERENCE_SYNC

## Resume Command
```
/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md] @[docs/implementationplans/TRACKER_Canonical_Import_Migration_and_Strangler_Fig_Facade_Eradication.md]
```
