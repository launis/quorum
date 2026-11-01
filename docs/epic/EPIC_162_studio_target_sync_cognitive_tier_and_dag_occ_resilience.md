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

# EPIC 162: Studio Target Block Synchronization, CognitiveTier SSOT Enforcement & DAG Optimistic Concurrency Resilience

## 1. Goal Description & Background (Objective & Problem Statement)

This Epic resolves Chapters 6, 7, and 8 of `@[docs/arkkitehtuurin_parannuskohteet.md#L232-329]` as Step 3.6 (`Askel 3.6`) in the production architecture roadmap (`@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]`). Before transitioning to Step 4 (`EPIC 158: Monolithic File Decomposition & SRP`), the system requires deterministic cross-entity synchronization between Studio `Workflow` and `OutputProfile` models, complete eradication of the legacy string-based `LLMClient.from_strategy` bridge in favor of `CognitiveTier` Enum Single Source of Truth (SSOT), and multi-worker DAG execution resilience via semantic oscillation detection, per-run execution budgets, node-level Merkle input hashing, MCP XML boundary sanitization, and PostgreSQL 19 optimistic concurrency control (`state_version` OCC).

### Core Architectural Problems Addressed

1. **Chapter 7 — Legacy `LLMClient.from_strategy` String Bridge & Untyped `PipelineConfig.default_strategy` (`@[docs/arkkitehtuurin_parannuskohteet.md#L261-283]`):**
   - `PipelineConfig.default_strategy` in `@[backend_v2/models/enums.py#L1051-L1065]` is typed as `str | None = None` instead of `CognitiveTier | None = None`, and `PIPELINE_REGISTRY` (`@[backend_v2/models/enums.py#L1051-L1065]`) passes raw `"fast"` string literals.
   - `LLMClient.from_strategy` (`@[backend_v2/llm/client.py#L44-L863]`) remains active as a string-coercion shim and is invoked by 5 production and operational script modules (`@[backend_v2/services/chat_parser.py#L136-L346]`, `@[backend_v2/hooks/interaction_hook.py#L44-L185]`, `@[backend_v2/hooks/linguistics.py#L78-L231]`, `@[backend_v2/hooks/source_verification_hook.py#L156-L282]`, `@[scripts/ablation_live_executor.py#L651-L691]`) and 14 test suites, violating `direct_sdk_calls` and `internal_utility_llm_execution` in `@[.agents/rules/05_llm_architecture.md#L18-20]`.
   - Pre-flight technical debt scanning (`scripts/audit_technical_debt.py`) identified 2 `TD_DICT_GET` warnings in `@[scripts/ablation_live_executor.py#L353]` and `@[scripts/ablation_live_executor.py#L522]` and 2 `TD_MODEL_FACTORY` raw dictionary validation warnings in `@[backend_v2/tests/fakes/in_memory_uow.py#L1040]` and `@[backend_v2/tests/fakes/in_memory_uow.py#L1154]`.

2. **Chapter 6 — Studio `OutputProfile` & `Workflow` `target_blocks` Desynchronization on Step Deletion (`@[docs/arkkitehtuurin_parannuskohteet.md#L232-259]`):**
   - Deleting a step from a `Workflow` in `WorkflowStepsTab._deleteStep` (`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L91-124]`) and persisting the workflow via `StudioWorkflowService.save_workflow` (`@[backend_v2/services/studio/workflow_service.py#L283-321]`) leaves orphaned `blk_...` matrix references inside linked `OutputProfile` entities (`matrix_synthesis_groups[*].target_blocks`, `variance_target_block`, and `user_role_target_block`).
   - In `MatrixGraphItemEditor` (`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L47-53]`), `matrixBlocks` filters out any block ID not in `allowedBlockIds`, hiding stale block IDs in `group.targetBlocks` from the UI while still submitting them on save and triggering HTTP 400 `VALIDATION_FAILED` in `StudioOutputProfileService.save_output_profile` (`@[backend_v2/services/studio/output_profile_service.py#L26-L295]`).

3. **Chapters 8.1 & 8.3 — Anomaly Retry Token Reset, Semantic Oscillation, Missing Per-Run `ExecutionBudget`, Node-Level `input_merkle_hash` & MCP XML Control-Tag Injection (`@[docs/arkkitehtuurin_parannuskohteet.md#L285-305]`, `@[docs/arkkitehtuurin_parannuskohteet.md#L319-329]`):**
   - In `execute_engine_retry_stage` (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py#L411-L588]`), `usage_agg = retrieval_usage + engine_usage` (`#L538`) overwrites previous retry token usage on each anomaly retry iteration instead of accumulating `usage_agg`, and identical failing LLM outputs retry up to `max_retries` before swallowing the anomaly (`#L555-561`).
   - `Settings` (`@[backend_v2/settings.py#L47-L1199]`) and `execute_topological_waves_stage` (`@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L280-369]`) lack a workflow-level cumulative `ExecutionBudget` circuit breaker (`max_tokens_per_run`, `max_cost_usd_per_run`, `max_total_steps_per_run`).
   - `ExecutionStep` (`@[backend_v2/models/domain/execution.py#L135-L170]`) and `ExecutionResumptionService` (`@[backend_v2/services/execution/resumption_service.py#L23-L192]`) verify workflow-level `workflow_version` but lack a node-level `input_merkle_hash` to deterministically preserve unchanged `PASSED` upstream steps while invalidating steps whose upstream inputs or prompt blocks drifted.
   - `_assemble_evidence_payload` in `@[backend_v2/services/mcp/mcp_tool_loop.py#L412-L448]` interpolates external MCP `audit.query`, `audit.response_summary`, and `audit.source_urls` into `<source ID="...">...</source>` inside `<external_evidence>...</external_evidence>` without stripping reserved structural XML boundary tags.

4. **Chapter 8.2 — Cross-Process Lost Update Race in `ExecutionRecord` Persistence (`@[docs/arkkitehtuurin_parannuskohteet.md#L307-317]`):**
   - While in-process coroutines in `DAGExecutor` coordinate via `WorkflowExecutionState.update_lock` and `commit_lock` (`@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L55-L94]`), cross-process mutations between the FastAPI API process (`ExecutionOverrideService` in `@[backend_v2/services/execution/override_service.py#L35-L425]`) and the Arq background worker process (`ExecutionCommitter` in `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L59-107]`) overwrite the entire `executions` row in `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366]` without optimistic concurrency control (`state_version` OCC).

### Quantitative Scope Summary

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Production Backend & Script Files** | 28 | `@[backend_v2/models/enums.py]`, `@[backend_v2/llm/client.py]`, `@[backend_v2/services/chat_parser.py]`, `@[backend_v2/hooks/interaction_hook.py]`, `@[backend_v2/hooks/linguistics.py]`, `@[backend_v2/hooks/source_verification_hook.py]`, `@[scripts/ablation_live_executor.py]`, `@[scripts/run_ablation_benchmark.py]`, `@[scripts/_ast_guardrails.py]`, `@[scripts/audit_zero_orm_strictness.py]`, `@[backend_v2/services/studio/workflow_service.py]`, `@[backend_v2/services/studio/output_profile_service.py]`, `@[backend_v2/settings.py]`, `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]`, `@[backend_v2/services/execution/resumption_service.py]`, `@[backend_v2/services/mcp/mcp_tool_loop.py]`, `@[backend_v2/models/domain/execution.py]`, `@[backend_v2/models/dtos/trace.py]`, `@[backend_v2/models/dtos/node_execution.py]`, `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]`, `@[backend_v2/database/postgres/storage_driver.py]`, `@[backend_v2/database/repositories/execution.py]`, `@[backend_v2/services/execution/override_service.py]`, `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` (28 backend/script/SQL targets) |
| **Production Frontend Flutter & ARB Files** | 6 | `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]`, `@[client_app_v2/lib/features/execution/models/execution_record.dart]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart]`, `@[client_app_v2/lib/l10n/app_en.arb]`, `@[client_app_v2/lib/l10n/app_fi.arb]` |
| **Test & Fake Files** | 26 | 24 Python unit test and fake files + 2 Flutter widget/model unit test files |
| **Execution Phases** | 4 | Phase 1: Tech Debt & `CognitiveTier` SSOT; Phase 2: Studio `target_blocks` Sync & UI; Phase 3: DAG Retry Resilience, `ExecutionBudget`, `input_merkle_hash` & MCP XML Sanitization; Phase 4: PostgreSQL 19 `state_version` OCC & Full-Duplex DTO Parity |

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

| Symbol / File / Field | Current Location | Target Destination / Disposition |
| :--- | :--- | :--- |
| Legacy string-based strategy bridge on `LLMClient` | `@[backend_v2/llm/client.py#L44-L863]` | INTENTIONALLY DROPPED — Replaced 100% by `LLMClient.from_tier(CognitiveTier.<TIER>, ...)` in `@[backend_v2/llm/client.py#L129-312]` |
| Untyped `str | None` annotation on `PipelineConfig.default_strategy` | `@[backend_v2/models/enums.py#L1051-L1065]` | Replaced in-place by `CognitiveTier | None = None` and `CognitiveTier.FAST` in `PIPELINE_REGISTRY` |
| Untyped `tuple[str, str]` on `AblationLiveExecutionConfigDTO.compare_strategies` | `@[scripts/ablation_live_executor.py#L153-L180]` | Replaced in-place by `tuple[LaxCognitiveTier, LaxCognitiveTier]` and `LLMClient.from_tier` at `@[scripts/ablation_live_executor.py#L153-L180]` |
| Legacy `test_from_strategy_compatibility_bridge` and `test_from_strategy_invalid_tier_raises_configuration_error` unit tests | `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L193-L208]` | INTENTIONALLY DROPPED — Replaced by `LLMClient.from_tier` negative type/tier validation tests and AST guardrail tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` |
| Silent anomaly swallowing and token usage overwrite in `execute_engine_retry_stage` | `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py#L411-L588]` | Replaced by cumulative `usage_agg` summation and canonical SHA-256 semantic oscillation short-circuit |

### Retained SSOT Invariants (`What We Will RETAIN`)

- `LLMClient.from_tier` (`@[backend_v2/llm/client.py#L129-312]`) as the sole factory entrypoint for initializing `LLMClient` instances from `SystemConfigModelRegistry`.
- `Workflow.get_allowed_prompt_block_targets` (`@[backend_v2/models/domain/workflow.py#L174-193]`) and `Workflow.get_allowed_layout_targets` (`@[backend_v2/models/domain/workflow.py#L195-213]`) as the authoritative positive-ID-set resolvers for workflow block membership (`positive_id_set_filtering_mandate`).
- `OutputProfile.validate_variance_target_block_coherence` (`@[backend_v2/models/domain/output_profile.py#L225-253]`), `OutputProfile.validate_matrix_graphs_coherence` (`@[backend_v2/models/domain/output_profile.py#L255-269]`), and `MatrixSynthesisGroup.validate_dimensional_cardinality` (`@[backend_v2/models/domain/synthesis.py#L237-280]`).
- Two-Lock coroutine synchronization (`WorkflowExecutionState.update_lock` and `commit_lock` in `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L55-L94]`) for intra-process coroutine safety, augmented with `state_version` OCC for cross-process persistence safety.

### 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/enums.py#L1051-L1065]` & `@[backend_v2/llm/client.py#L44-L863]` | Passing raw `"fast"` strings via `LLMClient.from_strategy` and typing `PipelineConfig.default_strategy` as `str \| None`. | Enforce `default_strategy: CognitiveTier \| None = None`, delete `LLMClient.from_strategy`, and ban `from_strategy` via `scripts/_ast_guardrails.py`. | Zero string-to-enum fallback wrappers or deprecated transition aliases on `LLMClient`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/llm/client.py backend_v2/models/enums.py --test --ast-strict` |
| `@[backend_v2/services/studio/workflow_service.py#StudioWorkflowService.save_workflow]` & `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]` | Leaving orphaned `blk_...` IDs in `OutputProfile` when workflow steps are deleted and hiding stale IDs in `MatrixGraphItemEditor`. | Auto-prune stale block IDs from linked `OutputProfile` models on `save_workflow` and render removable error-styled `FilterChip` items in `MatrixGraphItemEditor`. | Zero background cron jobs or cross-feature Riverpod listeners; synchronize deterministically on save and render. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/ --test --ast-strict` |
| `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py#L411-L588]` & `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L280-L369]` | Overwriting `usage_agg` on retry, retrying identical oscillating payloads, and running DAG waves without a per-run token/cost ceiling. | Accumulate `usage_agg` across retries, abort retry loop on duplicate SHA-256 output digest, and enforce `max_tokens_per_run`, `max_cost_usd_per_run`, and `max_total_steps_per_run` via `ErrorCodes.QUOTA_EXCEEDED`. | Zero external Redis token-bucket daemons; evaluate budget directly from `ExecutionRecord` telemetry between waves. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test --ast-strict` |
| `@[backend_v2/models/domain/execution.py#L135-L170]` & `@[backend_v2/services/mcp/mcp_tool_loop.py#L412-L448]` | Resuming DAG runs without checking step-level input/block hash drift, and interpolating raw MCP tool strings into `<source>` XML blocks. | Compute canonical SHA-256 `input_merkle_hash` per `ExecutionStep` and strip reserved structural XML boundary tags in `_assemble_evidence_payload`. | Zero heavy AST/DOM XML parsers; use deterministic tuple-based tag scrubbing before `<source>` framing. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/mcp/mcp_tool_loop.py backend_v2/services/execution/resumption_service.py --test --ast-strict` |
| `@[backend_v2/models/domain/execution.py#L189-L356]` & `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366]` | Blindly overwriting `executions` rows across API and worker processes without version checking. | Add `state_version: int = 1` to `ExecutionRecord` (`001_pg19_uuidv7_schema.sql`, Python, and Flutter) and enforce conditional OCC check + increment raising `AppException(ErrorCodes.CONFLICT, status_code=409)`. | Zero distributed Redis locks (`Redlock`); rely 100% on native PostgreSQL 19 atomic `state_version` OCC. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py --test --ast-strict` |

### Producer-Consumer Integration Check

- **Producer 1 (`StudioWorkflowService.save_workflow` in `@[backend_v2/services/studio/workflow_service.py#L283-321]`):** Computes `allowed_prompt_blocks = saved.get_allowed_prompt_block_targets(all_steps)` and `allowed_layout_targets = saved.get_allowed_layout_targets(all_steps)`, prunes stale block IDs from linked `OutputProfile` models, and persists updated profiles via `self.output_profile_repo.save_output_profile`.
- **Consumer 1 (`StudioOutputProfileService.save_output_profile` in `@[backend_v2/services/studio/output_profile_service.py#L96-155]` & `MatrixGraphItemEditor` in `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]`):** Consumes synchronized `OutputProfile` models without triggering stale block HTTP 400 errors, and surfaces any unsaved client-side stale block IDs as removable error `FilterChip` items.
- **Producer 2 (`ExecutionCommitter` in `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L59-107]`, `ExecutionOverrideService` in `@[backend_v2/services/execution/override_service.py#L35-L425]`, & `save_execution_row` in `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-366]`):** Persists `ExecutionRecord` with `state_version: int` and `ExecutionStep.input_merkle_hash: str | None`.
- **Consumer 2 (Flutter `ExecutionRecord` in `@[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]` & `ExecutionStep` in `@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-39]`):** Deserializes `state_version` (`@JsonKey(name: 'state_version')`) and `input_merkle_hash` (`@JsonKey(name: 'input_merkle_hash')`) under `@JsonSerializable(disallowUnrecognizedKeys: true)` with 100% Full-Duplex Serialization Parity.

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Pre-Implementation Technical Debt Cleanups, 100% `CognitiveTier` Enum Enforcement & `LLMClient.from_strategy` Eradication

- **Objective:** Resolve all pre-existing technical debt warnings in the touched scope (`scripts/ablation_live_executor.py` and `backend_v2/tests/fakes/in_memory_uow.py`), enforce `CognitiveTier` Enum typing in `PipelineConfig` and `PIPELINE_REGISTRY`, migrate all 5 production/script callers and 14 test files from `LLMClient.from_strategy` to `LLMClient.from_tier`, delete `LLMClient.from_strategy`, and enforce static AST guardrail protection.
- **Target Files:**
  - `@[scripts/ablation_live_executor.py#L153-L180]` (`AblationLiveExecutionConfigDTO.compare_strategies` typed as `tuple[LaxCognitiveTier, LaxCognitiveTier] | None = None`), `@[scripts/ablation_live_executor.py#load_seed_data]` (replace `data.get("system_config", [])` with explicit key check `"system_config" in data`), `@[scripts/ablation_live_executor.py#L153-L180]` (replace `telemetry.get(strat)` with `telemetry[strat] if strat in telemetry else None` and replace `LLMClient.from_strategy(strat_1, repository=repo)` with `LLMClient.from_tier(CognitiveTier(strat_1), repository=repo)`), and `@[scripts/run_ablation_benchmark.py#L490-L1148]` (coerce `compare_strategies` to `tuple[CognitiveTier, CognitiveTier] | None` when instantiating `AblationLiveExecutionConfigDTO`).
  - `@[backend_v2/tests/fakes/in_memory_uow.py#L217-L299]` and `@[backend_v2/tests/fakes/in_memory_uow.py#L217-L299]` (extract module-level typed hydration mapping helpers `_hydrate_in_memory_execution_record` and `_hydrate_in_memory_proposition_node` so `TD_MODEL_FACTORY` warnings on inline dict literals in `model_validate` are eliminated cleanly).
  - `@[backend_v2/models/enums.py#L1051-L1065]` (`PipelineConfig.default_strategy: CognitiveTier | None = None` and `PIPELINE_REGISTRY` entries `"chat_parser"`, `"studio_generation"`, and `"interaction_hook"` using `default_strategy=CognitiveTier.FAST`).
  - `@[backend_v2/services/chat_parser.py#L72-L346]` (`ChatParserService.parse_pasted_chat` calling `await LLMClient.from_tier(CognitiveTier.FAST, repository=system_repo, pipeline_name="chat_parser", registry_id=registry_id, provider=provider_override)`).
  - `@[backend_v2/hooks/interaction_hook.py#L44-L185]` (`analyze_interaction_role` calling `await LLMClient.from_tier(CognitiveTier.FAST, repository=system_repo, pipeline_name="interaction_hook", registry_id=registry_id, provider=provider_override)`).
  - `@[backend_v2/hooks/linguistics.py#L78-L231]` (`detect_performative_patterns` calling `await LLMClient.from_tier(CognitiveTier.FAST, repository=deps.system_repo, pipeline_name="linguistics_hook", registry_id=registry_id, provider=provider_override)`).
  - `@[backend_v2/hooks/source_verification_hook.py#L155-L282]` (`source_verification_hook` calling `await LLMClient.from_tier(CognitiveTier.FAST, repository=deps.system_repo, pipeline_name="source_verification", registry_id=registry_id, provider=provider_override)`).
  - `@[backend_v2/llm/client.py#L44-L863]` (delete `LLMClient.from_strategy` classmethod completely).
  - `@[scripts/_ast_guardrails.py#L781-L3519]` (enforce static AST guardrail in `QuorumGuardrailVisitor.visit_Call` banning any `.from_strategy(...)` invocation and any `LLMClient.from_tier(...)` call where the first positional argument or `tier=` keyword argument is an `ast.Constant` string literal).
  - **Synchronized Unit Test Targets:**
    - `@[backend_v2/tests/unit/models/test_enums.py#L240-L245]`
    - `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L193-L208]`
    - `@[backend_v2/tests/unit/llm/test_provider_retry_after.py#L131-L133]`
    - `@[backend_v2/tests/unit/services/test_chat_parser.py#L37-L87]`
    - `@[backend_v2/tests/unit/hooks/test_interaction_hook.py#L120-L186]`
    - `@[backend_v2/tests/unit/hooks/test_linguistics.py#L487-L543]`
    - `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py#L178-L250]`
    - `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py#L135-L184]`
    - `@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py#L519-L553]`
    - `@[backend_v2/tests/unit/scripts/test_run_ablation_benchmark.py#L904-L918]`
    - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L154-L286]`
    - `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py#L311-L420]` and `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py#L477-L550]`
    - `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py#L42-L135]`
    - `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py#L139-L288]`
    - `@[backend_v2/tests/test_fastdev_frozen.py#L13-L48]`
    - `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py#L19-L31]` and `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py#L214-L232]`
    - `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2935-L2987]`

### Phase 2: Studio `Workflow` & `OutputProfile` Stale `target_blocks` Synchronization & Error FilterChip UI

- **Objective:** Implement defense-in-depth synchronization between `Workflow` and `OutputProfile` so deleting a step from a workflow automatically prunes orphaned block IDs from linked `OutputProfile` records on save, `StudioOutputProfileService.save_output_profile` validates `variance_target_block` and `user_role_target_block` against `allowed_prompt_blocks`, and `MatrixGraphItemEditor` displays any unsaved stale block ID in `group.targetBlocks` as a removable error-styled `FilterChip`.
- **Target Files:**
  - `@[backend_v2/services/studio/workflow_service.py#L283-321]` (`StudioWorkflowService.save_workflow` and helper `_sync_output_profiles_for_workflow(self, workflow: Workflow) -> None`):
    - Fetch `all_steps = await self.workflow_repo.get_all_steps()` and `all_profiles = await self.output_profile_repo.get_all_output_profiles()`.
    - Resolve `allowed_prompt_blocks = workflow.get_allowed_prompt_block_targets(all_steps)` and `allowed_layout_targets = workflow.get_allowed_layout_targets(all_steps)`.
    - For each `profile` where `profile.workflow_id == workflow.id`:
      - Prune any block ID not in `allowed_layout_targets` from each `group.target_blocks` in `profile.matrix_synthesis_groups`. If a group has remaining `target_blocks` whose count is incompatible with `group.view_type` (`COMPARE_2D` requiring 2 or `MATRIX_3D` requiring >= 3), coerce `view_type` deterministically (`COMPARE_2D` if `len == 2`, `METRICS_1D` if `len == 1`); if `target_blocks` becomes empty, drop the empty `MatrixSynthesisGroup`. If `profile.matrix_synthesis_groups` becomes empty while `TargetBlockType.MATRIX_GRAPHS_BLOCK` is in `profile.target_block_order`, remove `TargetBlockType.MATRIX_GRAPHS_BLOCK` from `target_block_order` so `validate_matrix_graphs_coherence` succeeds.
      - If `profile.variance_target_block is not None` and `profile.variance_target_block not in allowed_prompt_blocks`, set `variance_target_block = None`, remove `TargetBlockType.VARIANCE_VALIDATION_BLOCK` from `target_block_order`, and remove `XaiExtensionType.VARIANCE_VALIDATION` from `visible_workflow_extensions` so `validate_variance_target_block_coherence` succeeds.
      - If `profile.user_role_target_block is not None` and `profile.user_role_target_block not in allowed_prompt_blocks`, set `user_role_target_block = None`.
      - Persist updated profile via `await self.output_profile_repo.save_output_profile(updated_profile)`.
  - `@[backend_v2/services/studio/output_profile_service.py#L96-155]` (`StudioOutputProfileService.save_output_profile`):
    - In addition to verifying `group.target_blocks` against `allowed_blocks = workflow.get_allowed_layout_targets(all_steps)`, verify `profile.variance_target_block` and `profile.user_role_target_block` (when not `None`) against `allowed_prompt_blocks = workflow.get_allowed_prompt_block_targets(all_steps)`, raising `AppException(ErrorCodes.VALIDATION_FAILED, status_code=400)` with RFC 7807 `logger.error` if either references a block outside `allowed_prompt_blocks`.
  - `@[client_app_v2/lib/l10n/app_en.arb#L2963-2983]` & `@[client_app_v2/lib/l10n/app_fi.arb#L2213-2233]`:
    - Add `staleTargetBlockChipLabel` (`"Removed from workflow: {blockId}"` / `"Poistettu työnkulusta: {blockId}"` with `blockId` placeholder of type `String`).
  - `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]` & `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L41-72]`:
    - In `MatrixGraphItemEditor`, identify stale block IDs via `final staleBlockIds = allowedBlockIds.isEmpty ? const <String>[] : group.targetBlocks.where((id) => !allowedBlockIds.contains(id)).toList();`.
    - Render a selected, removable error `FilterChip` for each `staleId` in `staleBlockIds` Inside the `Wrap` widget using `Theme.of(context).colorScheme.errorContainer`, `Theme.of(context).colorScheme.onErrorContainer`, `avatar: Icon(Icons.warning_amber_rounded, size: 16, color: Theme.of(context).colorScheme.onErrorContainer)`, and `label: Text(l10n.staleTargetBlockChipLabel(staleId))`, where tapping the chip removes `staleId` from `group.targetBlocks` via `onUpdate(group.copyWith(targetBlocks: newTargets))`.
  - **Synchronized Unit Test Targets:**
    - `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L267-L278]`
    - `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L501-L587]`
    - `@[client_app_v2/test/unit/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor_test.dart#L209-291]`

### Phase 3: DAG Execution Resilience — Semantic Oscillation Detector, Per-Run `ExecutionBudget` Cap, Node-Level `input_merkle_hash` & MCP XML Control-Tag Sanitization

- **Objective:** Prevent runaway token/cost consumption and retry oscillation in `execute_engine_retry_stage` and `execute_topological_waves_stage`, enforce deterministic node-level `input_merkle_hash` validation during DAG execution and resumption, and sanitize external MCP tool outputs against XML boundary breakout.
- **Target Files:**
  - `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py#L411-L588]` (`execute_engine_retry_stage`):
    - Fix cumulative token accounting across anomaly retries: initialize `usage_agg = retrieval_usage` before the `while retry_count <= max_retries:` loop and accumulate `usage_agg = usage_agg + engine_usage` on every attempt.
    - Compute a deterministic SHA-256 payload digest `_compute_retry_output_digest(final_dict: dict[str, JsonValue]) -> str` using `hashlib.sha256(json.dumps({k: v for k, v in final_dict.items() if k != "llm_anomaly_retry_requested"}, sort_keys=True, default=str).encode("utf-8")).hexdigest()`.
    - Track `seen_anomaly_digests: set[str] = set()`. If `llm_anomaly_retry_requested` is truthy and `current_digest in seen_anomaly_digests`, log an RFC 7807 warning/error for semantic oscillation, set `final_dict["anomaly_unresolved"] = True`, delete `final_dict["llm_anomaly_retry_requested"]`, and `break` immediately without issuing another redundant LLM call.
  - `@[backend_v2/settings.py#L47-L1199]` (`Settings`):
    - Add `max_tokens_per_run: Annotated[int, Field(ge=0, default=5_000_000, description="Maximum cumulative tokens permitted per workflow execution run (0 disables limit)")] = 5_000_000`, `max_cost_usd_per_run: Annotated[float, Field(default=25.0, description="Maximum cumulative USD cost permitted per workflow execution run (0.0 disables limit)")] = 25.0` (validated `>= 0.0` via `@field_validator` per `vertex_serving_grammar_fix`), and `max_total_steps_per_run: Annotated[int, Field(ge=0, default=50, description="Maximum executed DAG steps permitted per workflow execution run (0 disables limit)")] = 50`.
  - `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L280-369]` (`execute_topological_waves_stage` & helper `_enforce_execution_budget(state: WorkflowExecutionState) -> None`):
    - Before dispatching each topological wave (and after wave completion), evaluate total run tokens (`record.prompt_tokens + record.completion_tokens + record.reasoning_tokens`), total run cost (`record.dag_cost_usd`), and total executed steps against the configured `max_tokens_per_run`, `max_cost_usd_per_run`, and `max_total_steps_per_run` ceilings on `Settings`.
    - When any positive ceiling is exceeded, log structured `logger.error` with `ErrorCodes.QUOTA_EXCEEDED.name`, transition remaining `PENDING` steps to `BLOCKED`, commit failed execution state, and raise `AppException(message=..., status_code=429, details={"error_code": ErrorCodes.QUOTA_EXCEEDED})`.
  - `@[backend_v2/models/domain/execution.py#L135-L170]` (`ExecutionStep`) & `@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-39]`:
    - Add `input_merkle_hash: Annotated[str | None, Field(default=None, description="Canonical SHA-256 Merkle hash of step inputs, prompt blocks, and tier configuration")] = None` to `ExecutionStep` in Python (`@[backend_v2/models/domain/execution.py#L135-L170]`) and `@JsonKey(name: 'input_merkle_hash') String? inputMerkleHash` to Flutter `ExecutionStep` (`@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-39]`).
  - `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py#L238-L403]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L148-L326]`, & `@[backend_v2/services/execution/resumption_service.py#L128-L192]`:
    - Implement deterministic `compute_step_input_merkle_hash(step_rule: StepRule, step_def: Step | None, raw_inputs: WorkflowInputs, upstream_hashes: dict[str, str | None]) -> str` using `hashlib.sha256(json.dumps(..., sort_keys=True).encode("utf-8")).hexdigest()`.
    - Persist `input_merkle_hash` onto `ExecutionStep` when a step transitions to `PASSED`.
    - During `bootstrap_workflow_execution_state` (`@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L148-L326]`) and `ExecutionResumptionService.check_resumability` (`@[backend_v2/services/execution/resumption_service.py#L91-126]`), if a previously `PASSED` step has a stored `input_merkle_hash` that mismatches the newly computed `input_merkle_hash` (or depends on an invalidated upstream step), transition that step (and its downstream dependents) from `PASSED` to `PENDING` so it re-executes cleanly on resume.
  - `@[backend_v2/services/mcp/mcp_tool_loop.py#L412-L448]` (`_assemble_evidence_payload` & helper `_sanitize_mcp_xml_control_tags(raw_text: str) -> str`):
    - Strip or neutralize reserved structural XML boundary tags (specifically and exhaustively: `<source_data>`, `</source_data>`, `<user_payload>`, `</user_payload>`, `<system_directive>`, `</system_directive>`, `<external_evidence>`, `</external_evidence>`, `<source`, `</source>`) from `audit.query`, `audit.response_summary`, and `audit.source_urls` before constructing `<source ID="...">` blocks in `_assemble_evidence_payload` and tool outputs in `_build_tool_evidence_message`.
  - **Synchronized Unit Test Targets:**
    - `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py#L426-L636]`
    - `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py#L220-L415]`
    - `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py#L129-L237]`
    - `@[backend_v2/tests/unit/services/test_execution_resumability.py#L40-L64]`
    - `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py#L1210-L1304]`

### Phase 4: Cross-Process Optimistic Concurrency Control (`state_version` OCC) on PostgreSQL 19 `executions`, Full-Duplex Flutter DTO Parity & Verification Gate

- **Objective:** Enforce atomic optimistic concurrency control (`state_version` OCC) on `ExecutionRecord` across PostgreSQL 19 DDL, Zero-ORM entity adapter, storage driver, in-memory fakes, `ExecutionCommitter`, `ExecutionOverrideService`, and Flutter Freezed models, followed by the global backend and frontend quality gates.
- **Target Files:**
  - `@[backend_v2/models/domain/execution.py#L189-L356]` (`ExecutionRecord`):
    - Add `state_version: Annotated[int, Field(ge=1, default=1, description="Monotonically increasing optimistic concurrency control version")] = 1`.
  - `@[backend_v2/models/dtos/trace.py#L65-L118]` (`ExecutionUpdateDTO`) & `@[backend_v2/models/dtos/node_execution.py#L30-L72]` (`NodeExecutionUpdateDTO`):
    - Add `expected_state_version: Annotated[int | None, Field(ge=1, default=None, description="Expected OCC state_version for conditional update")] = None` and `state_version: Annotated[int | None, Field(ge=1, default=None, description="Updated OCC state_version")] = None`.
  - `@[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]`:
    - Add `@JsonKey(name: 'state_version') @Default(1) int stateVersion` to `ExecutionRecord` and run Freezed code generation so `@JsonSerializable(disallowUnrecognizedKeys: true)` maintains 1:1 Full-Duplex Serialization Parity.
  - `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279]`:
    - Add `state_version INTEGER NOT NULL DEFAULT 1` to `CREATE TABLE IF NOT EXISTS executions`.
  - `@[scripts/audit_zero_orm_strictness.py]`:
    - Add `"state_version"` to `APPROVED_ADAPTER_RECORD_COLUMNS`.
  - `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366]`:
    - Add `state_version` as column `$41` in `_EXECUTION_COLS` and `_SAVE_EXECUTION_SQL`, hydrate `state_version=int(row["state_version"])` in `hydrate_execution_row`, and enforce OCC check in `save_execution_row` / `PostgresStorageDriver.update` (`@[backend_v2/database/postgres/storage_driver.py#L326-353]`) and `ExecutionRepositoryImpl.update_execution` (`@[backend_v2/database/repositories/execution.py#L28-L442]`): when `expected_state_version` is provided and does not match the stored `state_version`, log structured `logger.error` with `ErrorCodes.CONFLICT.name` and raise `AppException(message=..., status_code=409, details={"error_code": ErrorCodes.CONFLICT})`, otherwise increment `state_version = existing_state_version + 1`.
  - `@[backend_v2/tests/fakes/in_memory_uow.py#L941-L996]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L1356-L1412]`, & `@[backend_v2/tests/fakes/in_memory_repositories.py#L206-226]`:
    - Synchronize `state_version` column handling and `expected_state_version` OCC conflict detection (`ErrorCodes.CONFLICT`, HTTP 409) in `InMemoryAsyncPgConnection` and `InMemoryExecutionRepository.update_execution`.
  - `@[backend_v2/services/execution/override_service.py#L35-L425]` (`ExecutionOverrideService`) & `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L107]` (`ExecutionCommitter`):
    - Pass `expected_state_version=record.state_version` in `ExecutionOverrideService` (`clear_profile_synthesis`, `override_atom`, `reject_evidence_quote`) so concurrent worker mutations trigger deterministic HTTP 409 `ErrorCodes.CONFLICT` instead of silent lost updates, and preserve concurrent human overrides/syntheses during `ExecutionCommitter.commit_trace`.
  - **Synchronized Unit Test Targets:**
    - `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py#L153-L225]`
    - `@[backend_v2/tests/unit/services/execution/test_override_service.py#L267-L295]`
    - `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py#L26-L89]`
    - `@[client_app_v2/test/unit/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor_test.dart#L1-291]`

---

## 4. Definition of Done (DoD) & Verification Plan

- **Definition of Done (DoD):**
  1. Zero occurrences of `from_strategy` across `backend_v2/` and `scripts/` (enforced statically by `scripts/_ast_guardrails.py` and `scripts/audit_zero_orm_strictness.py`).
  2. `PipelineConfig.default_strategy` in `@[backend_v2/models/enums.py#L1051-L1065]` is strictly typed as `CognitiveTier | None = None`.
  3. Deleting a step from a `Workflow` and saving via `StudioWorkflowService.save_workflow` automatically prunes stale block IDs from linked `OutputProfile` records (`matrix_synthesis_groups[*].target_blocks`, `variance_target_block`, `user_role_target_block`), and `MatrixGraphItemEditor` renders any unsaved stale block IDs as removable error-styled `FilterChip` items.
  4. `execute_engine_retry_stage` accumulates `usage_agg` across all anomaly retries and aborts immediately when consecutive retries emit identical canonical SHA-256 output digests.
  5. `execute_topological_waves_stage` enforces `max_tokens_per_run`, `max_cost_usd_per_run`, and `max_total_steps_per_run` from `settings.py`, raising `AppException(ErrorCodes.QUOTA_EXCEEDED, status_code=429)` on breach.
  6. `ExecutionStep` computes and persists `input_merkle_hash`, and `ExecutionResumptionService` / `bootstrap_workflow_execution_state` preserves `PASSED` steps with matching `input_merkle_hash` while invalidating drifted steps to `PENDING`.
  7. `_assemble_evidence_payload` in `@[backend_v2/services/mcp/mcp_tool_loop.py#L412-L448]` strips reserved structural XML boundary tags from external MCP tool outputs.
  8. `ExecutionRecord` enforces `state_version` OCC across PostgreSQL 19 (`001_pg19_uuidv7_schema.sql`), `execution_and_report_stage.py`, `InMemoryUnitOfWork`, `ExecutionOverrideService`, `ExecutionCommitter`, and Flutter Freezed models (`execution_record.dart`, `execution_step.dart`).
- **Automated Unit & Quality Gate Tests:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
- **AST Guardrails & Structural Tests:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/test_ast_domain_security_guardrails.py`
- **MANDATORY Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
