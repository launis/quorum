# Tracker: Targeted Backend Hardening Wave 4 (Domain Models & DTO Schemas)

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

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 3.2d: Vaihe 2c-4)

- [ ] **[NOK] Execution:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md --gate backend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure`
  - [x] @[backend_v2/models/domain/base.py]
  - [x] @[backend_v2/models/domain/metadata.py]
  - [x] @[backend_v2/models/domain/usage.py]
  - [x] @[backend_v2/models/domain/references.py]
  - [ ] @[backend_v2/models/domain/retrieval.py]
  - [ ] @[backend_v2/models/domain/hydration.py]
  - [ ] @[backend_v2/models/domain/interaction.py]
  - [ ] @[backend_v2/models/domain/integrity.py]
  - [ ] @[backend_v2/models/domain/archivist.py]
  - [ ] @[backend_v2/models/domain/causal.py]
  - [ ] @[backend_v2/models/domain/coach.py]
  - [ ] @[backend_v2/models/domain/evaluation.py]
  - [ ] @[backend_v2/models/domain/falsifier.py]
  - [ ] @[backend_v2/models/domain/judge.py]
  - [ ] @[backend_v2/models/domain/knowledge.py]
  - [ ] @[backend_v2/models/domain/logician.py]
  - [ ] @[backend_v2/models/domain/overseer.py]
  - [ ] @[backend_v2/models/domain/performativity.py]
  - [ ] @[backend_v2/models/domain/profiler.py]
  - [ ] @[backend_v2/models/domain/scoring.py]
  - [ ] @[backend_v2/models/domain/source_verification.py]
  - [ ] @[backend_v2/models/domain/synthesis.py]
  - [ ] @[backend_v2/models/domain/workflow.py]
  - [ ] @[backend_v2/models/prompt.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/models/dtos/inputs.py]
  - [ ] @[backend_v2/models/dtos/prompt.py]
  - [ ] @[backend_v2/models/dtos/prompt_context.py]
  - [ ] @[backend_v2/models/dtos/retrieval.py]
  - [ ] @[backend_v2/models/dtos/evaluation_steps.py]
  - [ ] @[backend_v2/models/dtos/schema_manifest.py]
  - [ ] @[backend_v2/models/dtos/state.py]
  - [ ] @[backend_v2/models/dtos/variance.py]
  - [ ] @[backend_v2/models/dtos/workflow_schema.py]

- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]" --gate frontend --model gemini-4-argon-medium` (Zero frontend targets in backend targeted hardening).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Backend Quality Gate:
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  ```

