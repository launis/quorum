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

- [x] **[OK] (1af36b166) Execution:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md --gate backend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [x] **[OK] (1af36b166) Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`
  - [x] @[backend_v2/models/domain/base.py]
  - [x] @[backend_v2/models/domain/metadata.py]
  - [x] @[backend_v2/models/domain/usage.py]
  - [x] @[backend_v2/models/domain/references.py]
  - [x] @[backend_v2/models/domain/retrieval.py]
  - [x] @[backend_v2/models/domain/hydration.py]
  - [x] @[backend_v2/models/domain/interaction.py]
  - [x] @[backend_v2/models/domain/integrity.py]
  - [x] @[backend_v2/models/domain/archivist.py]
  - [x] @[backend_v2/models/domain/causal.py]
  - [x] @[backend_v2/models/domain/coach.py]
  - [x] @[backend_v2/models/domain/evaluation.py]
  - [x] @[backend_v2/models/domain/falsifier.py]
  - [x] @[backend_v2/models/domain/judge.py]
  - [x] @[backend_v2/models/domain/knowledge.py]
  - [x] @[backend_v2/models/domain/logician.py]
  - [x] @[backend_v2/models/domain/overseer.py]
  - [x] @[backend_v2/models/domain/performativity.py]
  - [x] @[backend_v2/models/domain/profiler.py]
  - [x] @[backend_v2/models/domain/scoring.py]
  - [x] @[backend_v2/models/domain/source_verification.py]
  - [x] @[backend_v2/models/domain/synthesis.py]
  - [x] @[backend_v2/models/domain/workflow.py]
  - [x] @[backend_v2/models/prompt.py]
  - [x] @[backend_v2/models/dtos/system.py]
  - [x] @[backend_v2/models/dtos/inputs.py]
  - [x] @[backend_v2/models/dtos/prompt.py]
  - [x] @[backend_v2/models/dtos/prompt_context.py]
  - [x] @[backend_v2/models/dtos/retrieval.py]
  - [x] @[backend_v2/models/dtos/evaluation_steps.py]
  - [x] @[backend_v2/models/dtos/schema_manifest.py]
  - [x] @[backend_v2/models/dtos/state.py]
  - [x] @[backend_v2/models/dtos/variance.py]
  - [x] @[backend_v2/models/dtos/workflow_schema.py]

- [x] **[SKIPPED] (1af36b166) Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]" --gate frontend --model gemini-4-argon-medium` (Zero frontend targets in backend targeted hardening).
- [x] **[OK] (1af36b166) Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] (1af36b166) Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Final Verification Quality Gate
- [x] **[OK] (1af36b166)** Universal Backend Quality Gate:
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  ```

---

# Session Handover Context

## Achieved
* Completed **Targeted Backend Hardening Wave 4 (`34/34` targets)** across 23 Domain Models (`backend_v2/models/domain/*`) and 11 DTO/Prompt Schemas (`backend_v2/models/dtos/*` + `@[backend_v2/models/prompt.py]`) with 100% first-attempt pass rate (`12,983.2s` total, commit `1af36b166`) and passed the Final Macro-Audit Completion Gate.
* Synchronized `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md#L648-L696]` and `@[docs/arkkitehtuurin_parannuskohteet.md#L9-L49]` (`53ec8063b`) with 0 markdown boundary violations verified via `@[scripts/audit_markdown_boundaries.py]`.

## Learned
* When referencing planned future files or DTO classes in roadmap and tracker documents, `@[scripts/audit_markdown_boundaries.py]` enforces explicit `[NEW]` markers (`MBD003` and `MBD005`) and exact AST span bounds (`MBD004`, verified on `@[backend_v2/settings.py#L47-L1087]:Settings`).
* In `@[backend_v2/models/domain/workflow.py#L25-L217]:Workflow`, both `mcp_gateway_id` (`pattern=r"^sys_[a-fA-F0-9]{16,32}$"`, lines 42–46) and `model_registry_id` (`pattern=r"^(sys_[a-fA-F0-9]{16,32}|cfg_model_registry_\d{2})$"`, lines 47–50) must be tightened to `r"^sys_[a-fA-F0-9]{32}$"` during Askel 3.3 (Model A `PrefixedUUID7` cutover).

## Resume Command
```text
/tier5-resume --target="@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md#L698-L723]" --workflow="/tier0-create-plan" --rules="00-antigravity-core.md,01-python-backend.md,02_flutter_desktop.md,03_seed_vault.md,04_directory_reference.md"
```

## Remaining
### Hardening State Snapshot
* **Wave 4 (`TRACKER_Backend_Targeted_Hardening_Wave4.md`):** `TARGETS = 34`, `DONE = 34`, `REMAINING = 0` (`100.0%` complete).
* **Cumulative Backend Waves 1–4:** `TARGETS = 133`, `DONE = 133`, `REMAINING = 0` (`391/403` = `97.0%` of `backend_v2/` production files hardened; `12` remaining files isolated to Askel 4 IAM [`9` files] and Askel 5 Storage [`3` files]).
* **Next Action in New Session:** Generate the implementation plans and trackers for **Askel 3.3** (`[NEW]` `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]` & `[NEW]` `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]`) and **Askel 3.4** (`[NEW]` `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` & `[NEW]` `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`) and update their execution command links directly into `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md#L698-L723]`.
