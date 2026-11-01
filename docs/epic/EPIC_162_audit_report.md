<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# EPIC 162 Tier 0 Architectural Research & Red-Team Audit Report

- **Target Epic:** `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]`
- **Roadmap Step:** Step 3.6 (`Askel 3.6` — Chapters 6, 7, and 8 of `@[docs/arkkitehtuurin_parannuskohteet.md#L232-329]`)
- **Audit Status:** `CONVERGENCE ACHIEVED: 0 architectural defects found` (Idempotent Zero-Mutation Pass)

---

## 1. Automated Pre-Flight & Boundary Gate Verification

1. **Markdown AST Boundary Audit (`scripts/audit_markdown_boundaries.py`):**
   - Command: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md`
   - Result: `SUCCESS: Audit passed` (`0` boundary errors, `0` anti-ambiguity violations, `0` absolute path leaks).
2. **Touched-Scope Technical Debt Scan (`scripts/audit_technical_debt.py`):**
   - Scanned all 28 direct Python production, operational script, and fake target files (`--targets ...`).
   - Discovered 4 pre-existing technical debt items in the direct target scope:
     - `@[backend_v2/tests/fakes/in_memory_uow.py#L951-1123]` (`TD_MODEL_FACTORY` at line 1040)
     - `@[backend_v2/tests/fakes/in_memory_uow.py#L1125-1200]` (`TD_MODEL_FACTORY` at line 1154)
     - `@[scripts/ablation_live_executor.py#load_seed_data]` (`TD_DICT_GET` at line 353)
     - `@[scripts/ablation_live_executor.py#L649-687]` (`TD_DICT_GET` at line 522)
   - All 4 items are already explicitly cataloged in Section 1.1 and scheduled for resolution in `Phase 1: Pre-Implementation Technical Debt Cleanups, 100% CognitiveTier Enum Enforcement & LLMClient.from_strategy Eradication`.
3. **Flutter Theme Sovereignty Audit (`scripts/audit_flutter_theme_sovereignty.py`):**
   - Scanned all 4 Flutter target files (`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]`, `@[client_app_v2/lib/features/execution/models/execution_record.dart]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart]`).
   - Result: `0 violations found`.
4. **Epic Coverage & Sunset Audit (`scripts/audit_epic_coverage.py`):**
   - Command: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_epic_coverage.py --epic docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md`
   - Result: `[PASSED] AUDIT PASSED`.

---

## 2. Five-Axis System 2 Deconstruction & Falsification Audit

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/enums.py#L1051-1061]` & `@[backend_v2/llm/client.py#L44-911]` | Passing raw `"fast"` strings via `LLMClient.from_strategy` and typing `PipelineConfig.default_strategy` as `str \| None`. | Enforce `default_strategy: CognitiveTier \| None = None`, delete `LLMClient.from_strategy`, and ban `from_strategy` via `@[scripts/_ast_guardrails.py#L781-3490]`. | Zero string-to-enum fallback wrappers or deprecated transition aliases on `LLMClient`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/llm/client.py backend_v2/models/enums.py --test --ast-strict` |
| `@[backend_v2/services/studio/workflow_service.py#StudioWorkflowService.save_workflow]` & `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]` | Leaving orphaned `blk_...` IDs in `OutputProfile` when workflow steps are deleted and hiding stale IDs in `MatrixGraphItemEditor`. | Auto-prune stale block IDs from linked `OutputProfile` models on `save_workflow` and render removable error-styled `FilterChip` items in `MatrixGraphItemEditor`. | Zero background cron jobs or cross-feature Riverpod listeners; synchronize deterministically on save and render. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/ --test --ast-strict` |
| `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py#L411-588]` & `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L280-369]` | Overwriting `usage_agg` on retry, retrying identical oscillating payloads, and running DAG waves without a per-run token/cost ceiling. | Accumulate `usage_agg` across retries, abort retry loop on duplicate SHA-256 output digest, and enforce `max_tokens_per_run`, `max_cost_usd_per_run`, and `max_total_steps_per_run` via `ErrorCodes.QUOTA_EXCEEDED`. | Zero external Redis token-bucket daemons; evaluate budget directly from `ExecutionRecord` telemetry between waves. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test --ast-strict` |
| `@[backend_v2/models/domain/execution.py#L135-170]` & `@[backend_v2/services/mcp/mcp_tool_loop.py#L412-448]` | Resuming DAG runs without checking step-level input/block hash drift, and interpolating raw MCP tool strings into `<source>` XML blocks. | Compute canonical SHA-256 `input_merkle_hash` per `ExecutionStep` and strip reserved structural XML boundary tags in `_assemble_evidence_payload`. | Zero heavy AST/DOM XML parsers; use deterministic tuple-based tag scrubbing before `<source>` framing. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/mcp/mcp_tool_loop.py backend_v2/services/execution/resumption_service.py --test --ast-strict` |
| `@[backend_v2/models/domain/execution.py#L189-356]` & `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-366]` | Blindly overwriting `executions` rows across API and worker processes without version checking. | Add `state_version: int = 1` to `ExecutionRecord` (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279]`, Python, and Flutter) and enforce conditional OCC check + increment raising `AppException(ErrorCodes.CONFLICT, status_code=409)`. | Zero distributed Redis locks (`Redlock`); rely 100% on native PostgreSQL 19 atomic `state_version` OCC. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py --test --ast-strict` |

---

## 3. Red-Team Falsification Verdict

1. **Fail-Fast & RFC 7807 Dual-Reporting:** Verified. `StudioOutputProfileService.save_output_profile` raises `AppException(ErrorCodes.VALIDATION_FAILED, status_code=400)` with `logger.error`; `execute_topological_waves_stage` raises `AppException(ErrorCodes.QUOTA_EXCEEDED, status_code=429)` with `logger.error`; `save_execution_row` / `PostgresStorageDriver.update` raises `AppException(ErrorCodes.CONFLICT, status_code=409)` with `logger.error`.
2. **Full-Duplex Serialization Parity:** Verified. Adding `input_merkle_hash: str | None = None` to `ExecutionStep` (`@[backend_v2/models/domain/execution.py#L135-170]`) and `state_version: int = 1` to `ExecutionRecord` (`@[backend_v2/models/domain/execution.py#L189-356]`) is paired 1:1 with `@JsonKey(name: 'input_merkle_hash') String? inputMerkleHash` in `@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-39]` and `@JsonKey(name: 'state_version') @Default(1) int stateVersion` in `@[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]`, plus `APPROVED_ADAPTER_RECORD_COLUMNS` in `@[scripts/audit_zero_orm_strictness.py]`.
3. **Vertex Serving Grammar Compliance:** Verified. `max_cost_usd_per_run` in `@[backend_v2/settings.py#L47-1199]` uses a `@field_validator` for float `>= 0.0` validation rather than `Field(ge=0.0)` (`vertex_serving_grammar_fix`).
4. **Zero-Defect Convergence Gate:** Satisfied with `0` mutations required on `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]`.
