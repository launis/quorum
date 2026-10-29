# Tracker: Targeted Backend Hardening Wave 3 (Repositories, Orchestrator Services & FastAPI Routers)

@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 3.2c: Vaihe 2c-3)

- [ ] **[NOK] Execution:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md --gate backend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure`
  - [x] @[backend_v2/database/repository.py]
  - [x] @[backend_v2/database/repositories/component.py]
  - [x] @[backend_v2/database/repositories/report_artifact.py]
  - [x] @[backend_v2/database/repositories/components/agent.py]
  - [x] @[backend_v2/database/repositories/components/execution_persona.py]
  - [x] @[backend_v2/database/repositories/components/extraction_protocol.py]
  - [x] @[backend_v2/database/repositories/components/matrix.py]
  - [x] @[backend_v2/database/repositories/components/output_profile.py]
  - [x] @[backend_v2/database/repositories/components/prompt_block.py]
  - [x] @[backend_v2/database/repositories/components/role.py]
  - [x] @[backend_v2/database/repositories/components/task_blueprint.py]
  - [x] @[backend_v2/services/orchestrator/schema_factory.py]
  - [x] @[backend_v2/services/orchestrator/chunking_service.py]
  - [x] @[backend_v2/services/orchestrator/atomizer.py]
  - [x] @[backend_v2/services/orchestrator/dag_compiler.py]
  - [x] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
  - [x] @[backend_v2/services/orchestrator/enriched_dag_executor.py]
  - [x] @[backend_v2/api/routers/system/health.py]
  - [x] @[backend_v2/api/routers/system/telemetry.py]
  - [x] @[backend_v2/api/routers/system/configs.py]
  - [x] @[backend_v2/api/routers/output_profiles.py]
  - [x] @[backend_v2/api/routers/studio/model_registry.py]
  - [x] @[backend_v2/api/routers/studio/prompt_blocks.py]
  - [x] @[backend_v2/api/routers/studio/system_configs.py]
  - [x] @[backend_v2/api/routers/studio/workflows.py]
  - [x] @[backend_v2/api/routers/execution/workflows.py]
  - [ ] @[backend_v2/api/routers/execution/reports.py]

- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]" --gate frontend --model gemini-4-argon-medium` (Zero frontend targets in backend targeted hardening).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Backend Quality Gate:
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  ```

