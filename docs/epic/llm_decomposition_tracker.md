<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Master Decomposition Tracker: `backend_v2/services/orchestrator/strategies/llm.py` (`LLMNodeStrategy`)

- **Target Monolith**: `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` (1,091 lines)
- **Target Domain Package**: `backend_v2/services/orchestrator/strategies/llm_strategy/` (`< 380` lines per sub-module, `< 220` lines for `__init__.py` facade)
- **Symbol & Blast-Radius Map**: `@[docs/epic/tasks_llm/symbol_migration_map.md]`
- **Monolith Archetype**: **Archetype D — Macro Orchestrator & Concurrency Core** (Sequential Pipeline Staging, Two-Tier Concurrency Guard, Stateless Stage Modules, RFC 7807 Dual-Reporting & OpenTelemetry Span Parity)
- **Pre-Flight Test Baseline (`[BASELINE]`)**: **45 passed unit tests, 94% line coverage** (`511` statements, `33` missed across `test_llm.py`, `test_llm_cost_tracking.py`, and `test_llm_strategy.py`). Exceeds the `75%` minimum coverage gate (`Phase 0` skipped).

---

## Phase Execution Status

### Phase 1: Blueprint Resolution, Pre-Hook & Step Context Metadata Stage Extraction (Epoch 1 Leaf & Stage 1)
- **Plan:** @[docs/epic/tasks_llm/phase1_blueprint_and_metadata_stage_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_llm/phase1_blueprint_and_metadata_stage_extraction.md] @[docs/epic/llm_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/__init__.py]` and `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` (`_SCHEMA_BLOCK_*` constants, `NodeStatePayload`, `dlq_handle_debug_log_error`, `extract_step_context_metadata`, `BlueprintStageResult`, and `execute_blueprint_and_pre_hooks_stage`) without creating `llm_strategy/__init__.py`.
  - [ ] Step 2: Update `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` to delegate `_dlq_handle_debug_log_error`, `_extract_step_context_metadata`, and Stage 1 of `execute` to `blueprint_and_metadata_stage.py` with explicit redundant re-exports, and create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`.
  - [ ] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_llm/phase1_blueprint_and_metadata_stage_extraction.md] @[docs/epic/llm_decomposition_tracker.md]`

### Phase 2: Context Building, Prompt Compilation & Dynamic Schema Stage Extraction (Epoch 1 Stage 2)
- **Plan:** @[docs/epic/tasks_llm/phase2_prompt_and_schema_stage_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_llm/phase2_prompt_and_schema_stage_extraction.md] @[docs/epic/llm_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]` (`PromptAndSchemaStageResult` and `execute_prompt_and_schema_stage`).
  - [ ] Step 2: Update `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` to delegate Stage 2 of `execute` to `execute_prompt_and_schema_stage` with explicit redundant re-exports, and create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`.
  - [ ] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_llm/phase2_prompt_and_schema_stage_extraction.md] @[docs/epic/llm_decomposition_tracker.md]`

### Phase 3: Engine Retry Loop, MCP Tool Retrieval & TraceEvent Stage Extraction (Epoch 1 Stages 3 & 4)
- **Plan:** @[docs/epic/tasks_llm/phase3_engine_retry_and_trace_stage_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_llm/phase3_engine_retry_and_trace_stage_extraction.md] @[docs/epic/llm_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` (`EngineRetryStageResult` and `execute_engine_retry_stage`) and `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` (`build_llm_step_trace_events`).
  - [ ] Step 2: Update `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` to delegate Stage 3 and Stage 4 of `execute` to `execute_engine_retry_stage` and `build_llm_step_trace_events`, and create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]` and `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]`.
  - [ ] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_llm/phase3_engine_retry_and_trace_stage_extraction.md] @[docs/epic/llm_decomposition_tracker.md]`

### Phase 4: Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown (Epoch 1 Cutover)
- **Plan:** @[docs/epic/tasks_llm/phase4_package_cutover_and_guardrails.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_llm/phase4_package_cutover_and_guardrails.md] @[docs/epic/llm_decomposition_tracker.md]`
  - [ ] Step 1: Migrate all 42 unit tests from `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` into `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]` and the modular stage test suites under `backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/`, and delete `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`.
  - [ ] Step 2: Atomically create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` (`< 220` lines), physically delete `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]`, and rewire all 1-hop consumer imports (`strategies/__init__.py`, `strategies/registry.py`, `test_ast_engine_dispatch_guardrails.py`, `test_dag_executor.py`, `test_node_strategy_registry.py`, `test_registry.py`, `test_tier4_matrix_shuffled_atoms_regression.py`, `test_llm_cost_tracking.py`, `test_llm_strategy.py`).
  - [ ] Step 3: Lock retired module `backend_v2.services.orchestrator.strategies.llm` in `@[scripts/_ast_guardrails.py#L1892-L1992]` and `@[scripts/_ast_guardrails.py#L1994-L2212]` (`QGR017`), remove `"backend_v2/services/orchestrator/strategies/llm.py"` from `RESIDUAL_FUTURE_PHASE_QGR028_FILES` and `@[pyproject.toml]`, and synchronize `@[.agents/rules/04_directory_reference.md]`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_llm/phase4_package_cutover_and_guardrails.md] @[docs/epic/llm_decomposition_tracker.md]`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker docs/epic/llm_decomposition_tracker.md --gate backend`
  - [ ] `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]`
  - [ ] `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]`
  - [ ] `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`
  - [ ] `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]`
  - [ ] `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]`
  - [ ] `@[backend_v2/services/orchestrator/strategies/__init__.py]`
  - [ ] `@[backend_v2/services/orchestrator/strategies/registry.py#L42-L60]`
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Pure backend Python decomposition with zero `.dart` changes.
- [ ] **[NOK] Pre-Delete Audit**: Verify `git status` and `grep_search` confirm 0 remaining references to `backend_v2.services.orchestrator.strategies.llm` and physical removal of `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]`.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify all 45 baseline unit tests pass across the modularized test suites (`[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L144-L276]`, and `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py#L147-L303]`) with `>= 94%` line coverage.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Verify 100% symbol parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$) and execute `uv run pytest backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py`, `uv run python scripts/audit_dict_eradication.py`, and `uv run python scripts/audit_clean_imports.py`.

#### Epoch 2: 12-Item Technical Debt Inventory (Target Scope for Tier 2 Hardening)
1. **Item 2 (`service_layer_hydration_firewall` / `QGR028`)**: Eliminate redundant repository model reconstitution (`OutputProfile.model_validate(raw_profile)` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]`, `ExecutionRecord.model_validate(raw_exec)` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]`, and `ExecutionRecord.model_validate(exec_dict)` + `dict(exec_obj.step_states)` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`) and remove the `llm_strategy` entries from `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]`.
2. **Item 1 (`no_naked_dicts_in_state` & `polymorphic_dag_payload_handling`)**: Audit `NodeStatePayload` (`list[Any]` union member) and `isinstance` checks in `extract_step_context_metadata` inside `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` and `final_dict` normalization in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` to enforce strict typed unions and `match/case` structural pattern matching.
3. **Item 4 (`data_leak_logging` / DLP Audit)**: Audit all `logger.error`, `logger.warning`, `logger.info`, and OpenTelemetry `span.set_attribute` calls across all 4 stage modules and `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` to verify zero raw user prompt, input payload, or PII serialization.
4. **Item 5 (`frozen_state_mutability` & `trace_serialization_hygiene_mandate`)**: Verify all `model_dump(mode="json", exclude_none=True)` and `model_copy(update={...})` calls across `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` and `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` enforce immutable state transitions and `exclude_none=True`.
5. **Item 8 (`docstring_fail_fast_ban` & `pep257_google_style_docstrings`)**: Ensure all stage functions, dataclasses, and facade methods across `backend_v2/services/orchestrator/strategies/llm_strategy/` include complete PEP 257 Google-style docstrings (`Args:`, `Returns:`, and explicit `Raises:` error codes).
6. **Item 10 (`anti_happy_path_mandate` — ISTQB Negative & Boundary Partitions)**: Add negative and boundary tests covering the 33 missed statements from baseline (`lines 169, 175, 181, 191, 203, 209, 343, 605-612, 636, 645, 673, 676-683, 702, 763, 766, 925-929, 976, 1019, 1027, 1034-1035, 1045-1046` of `llm.py`) across the 5 modular test suites under `backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/` to achieve `>= 98%` line coverage.

#### Architectural Documentation Synchronization
- [ ] **[NOK] As-Built Architectural Sync**: Run `/tier7-describe-architecture @[docs/epic/llm_decomposition_tracker.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md]`
  - **Target KIs to Synchronize**: `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`
  - **Directory Reference Sync**: Verify `@[.agents/rules/04_directory_reference.md]` reflects `backend_v2/services/orchestrator/strategies/llm_strategy/`
  - **Pillar Documentation Sync**: Update Pillar 3 (`docs/architecture/03_orchestration_and_execution.md`) to reflect the modular `backend_v2/services/orchestrator/strategies/llm_strategy/` package

### Final Epic Audit
- [ ] **[NOK] Final Decomposition Audit**: Run `/tier8-audit-plan @[docs/epic/tasks_llm/phase4_package_cutover_and_guardrails.md] @[docs/epic/llm_decomposition_tracker.md]` and verify 100% completion across all phases and gates.

## Instructions for the Execution Agent
1. **Strict Two-Epoch Firewall**: During Epoch 1 (Phases 1–4), perform ONLY pure structural lift-and-shift extraction, consumer import rewiring, test suite modularization, and atomic package cutover with **zero behavioral changes**. Do NOT mix Epoch 2 tech debt fixes into Epoch 1.
2. **Two-Phase Package Strangler Protocol**: Do NOT create `backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py` during Phases 1, 2, or 3 while `backend_v2/services/orchestrator/strategies/llm.py` exists on disk. Create `__init__.py` and delete `llm.py` atomically in Phase 4 Step 2.
3. **Quality Gate Enforcement**: Run `uv run python scripts/backend_audit_loop.py <target> --test --ast-strict` after every phase step and create an atomic Conventional Commit before advancing to the next phase.

## Requirements Traceability Matrix

| Requirement ID | Architectural Requirement | Phase & Step Mapping | Verification Target |
| :--- | :--- | :--- | :--- |
| `REQ-LLM-01` | Extract leaf constants (`_SCHEMA_BLOCK_*`), `NodeStatePayload`, `dlq_handle_debug_log_error`, `extract_step_context_metadata`, `BlueprintStageResult`, and `execute_blueprint_and_pre_hooks_stage` into `blueprint_and_metadata_stage.py` | Phase 1, Step 1 | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` |
| `REQ-LLM-02` | Delegate `_dlq_handle_debug_log_error`, `_extract_step_context_metadata`, and Stage 1 of `execute` in `LLMNodeStrategy` with explicit redundant re-exports | Phase 1, Step 2 | `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` |
| `REQ-LLM-03` | Verify Phase 1 extraction passes 10/10 backend audit gates and all 45 baseline unit tests | Phase 1, Step 3 | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]` |
| `REQ-LLM-04` | Extract `PromptAndSchemaStageResult` and `execute_prompt_and_schema_stage` into `prompt_and_schema_stage.py` | Phase 2, Step 1 | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]` |
| `REQ-LLM-05` | Wire proxy delegation for Stage 2 of `LLMNodeStrategy.execute` with explicit redundant re-exports | Phase 2, Step 2 | `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` |
| `REQ-LLM-06` | Verify Phase 2 extraction passes 10/10 backend audit gates and all 45 baseline unit tests | Phase 2, Step 3 | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]` |
| `REQ-LLM-07` | Extract `execute_engine_retry_stage` into `engine_retry_stage.py` and `build_llm_step_trace_events` into `trace_event_stage.py` | Phase 3, Step 1 | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` |
| `REQ-LLM-08` | Wire proxy delegations for Stage 3 and Stage 4 of `LLMNodeStrategy.execute` | Phase 3, Step 2 | `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` |
| `REQ-LLM-09` | Verify Phase 3 extraction passes 10/10 backend audit gates and all 45 baseline unit tests | Phase 3, Step 3 | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]` |
| `REQ-LLM-10` | Split `test_llm.py` (3,597 lines, 42 tests) into 5 modular unit test suites under `backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/` | Phase 4, Step 1 | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]` |
| `REQ-LLM-11` | Atomically replace `llm.py` with `llm_strategy/__init__.py` (`< 220` lines) and rewire all 1-hop callers | Phase 4, Step 2 | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `REQ-LLM-12` | Lock retired `backend_v2.services.orchestrator.strategies.llm` in `QGR017` AST guardrails and update `04_directory_reference.md` | Phase 4, Step 3 | `@[scripts/_ast_guardrails.py#L1892-L1992]`, `@[scripts/_ast_guardrails.py#L1994-L2212]` |

# Session Handover Context

## Achieved
- Completed Tier 3 God Code Decomposition pre-flight AST analysis, test baseline verification (`45 passed, 94% coverage`), 1-hop caller blast-radius mapping (`@[docs/epic/tasks_llm/symbol_migration_map.md]`), 4-Phase Strangler Fig implementation plan generation (`@[docs/epic/tasks_llm/phase1_blueprint_and_metadata_stage_extraction.md]`, `@[docs/epic/tasks_llm/phase2_prompt_and_schema_stage_extraction.md]`, `@[docs/epic/tasks_llm/phase3_engine_retry_and_trace_stage_extraction.md]`, `@[docs/epic/tasks_llm/phase4_package_cutover_and_guardrails.md]`), and Two-Epoch master decomposition tracker generation (`@[docs/epic/llm_decomposition_tracker.md]`).

## Learned
- `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` (1,091 lines) is an Archetype D Macro Orchestrator whose `execute` method (`#L220-L1091`, 872 lines) operates as a 4-stage sequential pipeline: Stage 1 (Blueprint, Pre-Hooks & OutputProfile resolution), Stage 2 (ContextBuilder, PromptFactory, Chunking & Dynamic Schema), Stage 3 (LLMClient binding, MCP tool loop & Engine retry loop), and Stage 4 (Telemetry & TraceEvent assembly).
- Existing unit tests in `test_llm.py` patch `EngineExecutionRequest`, `execute_mcp_retrieval`, and `get_settings` on `backend_v2.services.orchestrator.strategies.llm` and assert `caplog` on `logger="backend_v2.services.orchestrator.strategies.llm"`, so Stage 1–3 functions accept defaulted injectable hooks/logger from `LLMNodeStrategy` during Phases 1–3 to preserve 100% green tests without modifying `test_llm.py` prior to Phase 4.
- `llm.py` is listed in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]`; during Epoch 1 (Phases 1–3), the extracted stage modules are registered in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` for pure lift-and-shift parity, and Epoch 2 Tier 2 Hardening resolves all redundant `.model_validate()` calls and removes those entries.

## Resume Command
`/tier2-execute @[docs/epic/tasks_llm/phase1_blueprint_and_metadata_stage_extraction.md] @[docs/epic/llm_decomposition_tracker.md]`

## Remaining
- Execute Phase 1 (`@[docs/epic/tasks_llm/phase1_blueprint_and_metadata_stage_extraction.md]`).
- Execute Phase 2 (`@[docs/epic/tasks_llm/phase2_prompt_and_schema_stage_extraction.md]`).
- Execute Phase 3 (`@[docs/epic/tasks_llm/phase3_engine_retry_and_trace_stage_extraction.md]`).
- Execute Phase 4 (`@[docs/epic/tasks_llm/phase4_package_cutover_and_guardrails.md]`).
- Execute Post-Implementation Gates (Epoch 2 Tier 2 Hardening, Pre-Delete Audit, Golden Master & Test Restoration Audit, Semantic Coverage & Zero-Loss Audit, As-Built Architectural Sync) and Final Epic Audit.
