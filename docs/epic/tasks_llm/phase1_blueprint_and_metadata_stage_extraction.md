<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 1: Blueprint Resolution, Pre-Hook & Step Context Metadata Stage Extraction (`phase1_blueprint_and_metadata_stage_extraction.md`)

## 1. Objective
Execute Phase 1 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]`:
1. Create the test package marker `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/__init__.py]` (`strangler_fig_mandate` rule 2: test subpackages require `__init__.py` from Step 1 to prevent Pytest flat-namespace collisions, while the source domain sub-directory `backend_v2/services/orchestrator/strategies/llm_strategy/` MUST NOT contain `__init__.py` while `llm.py` exists).
2. Extract leaf constants (`_SCHEMA_BLOCK_MATRIX`, `_SCHEMA_BLOCK_TEXT`, `_SCHEMA_BLOCK_EXTENSION`, `_SCHEMA_BLOCK_SYSTEM`), PEP 695 type alias `NodeStatePayload`, `dlq_handle_debug_log_error` (`@[backend_v2/services/orchestrator/strategies/llm.py#L107-L114]`), `extract_step_context_metadata` (`@[backend_v2/services/orchestrator/strategies/llm.py#L116-L218]`), and Stage 1 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`, lines 241–470: concurrency kwargs rejection, `SourceDocumentPacker` packing, `V2Step` blueprint resolution, `HookState` initialization, `run_pre_hooks`, `PromptBlockAdapter` hydration, `output_profile_id` & `target_locale` validation, and `OutputProfile` loading) into `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` (`< 380` lines) returning an immutable `@dataclass(frozen=True) class BlueprintStageResult`.
3. Update `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` to delegate `_dlq_handle_debug_log_error`, `_extract_step_context_metadata`, and Stage 1 of `execute` to `blueprint_and_metadata_stage.py` with explicit redundant re-exports, and create unit tests in `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` | Leaf constants, `NodeStatePayload`, `dlq_handle_debug_log_error`, `extract_step_context_metadata`, `BlueprintStageResult`, and `execute_blueprint_and_pre_hooks_stage` (`< 380` lines, without `__init__.py` in `llm_strategy/`) |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` | Delegate `_dlq_handle_debug_log_error` (`#L107-L114`), `_extract_step_context_metadata` (`#L116-L218`), and Stage 1 of `execute` (`#L220-L1091`) to `blueprint_and_metadata_stage.py` with explicit redundant re-exports |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py]` | Register `backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py` in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` during Epoch 1 pure structural lift-and-shift |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/__init__.py]` | Mandatory Pytest test package marker |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]` | Dedicated unit tests for `dlq_handle_debug_log_error`, `extract_step_context_metadata`, and `execute_blueprint_and_pre_hooks_stage` |

### Multi-Phase Decomposition Context (Epoch 1 Surviving Targets)
Across Phases 1–4 of the `llm.py` decomposition, the complete set of surviving production `.py` files (`[NEW]` sub-modules, package facade, and `[MODIFY]` 1-hop production callers) registered for Epoch 2 Tier 2 Hardening is:
- `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` (Phase 1)
- `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/registry.py#L42-L60]` (Phase 4)

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Test Package Marker and Blueprint & Metadata Stage Module">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py during Phase 1 while backend_v2/services/orchestrator/strategies/llm.py exists on disk. Create backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/__init__.py immediately.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">blueprint_and_metadata_stage.py MUST NOT import from backend_v2.services.orchestrator.strategies.llm and MUST remain under 400 lines with all lines <= 120 characters.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/__init__.py]` containing a module docstring.
      2. Add `"backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py"` to `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` so the verbatim Epoch 1 lift-and-shift of `OutputProfile` reconstitution passes `QGR028` prior to Epoch 2 hardening.
      3. Create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` (`< 380` lines, all lines `<= 120` chars) with `__all__ = ["BlueprintStageResult", "NodeStatePayload", "_SCHEMA_BLOCK_EXTENSION", "_SCHEMA_BLOCK_MATRIX", "_SCHEMA_BLOCK_SYSTEM", "_SCHEMA_BLOCK_TEXT", "dlq_handle_debug_log_error", "execute_blueprint_and_pre_hooks_stage", "extract_step_context_metadata"]`:
         - Relocate `_SCHEMA_BLOCK_MATRIX`, `_SCHEMA_BLOCK_TEXT`, `_SCHEMA_BLOCK_EXTENSION`, `_SCHEMA_BLOCK_SYSTEM`, and `type NodeStatePayload` from `llm.py` lines 77–82.
         - Relocate `dlq_handle_debug_log_error` verbatim from `LLMNodeStrategy._dlq_handle_debug_log_error` (`@[backend_v2/services/orchestrator/strategies/llm.py#L107-L114]`).
         - Relocate `extract_step_context_metadata(hook_state: HookState, context: StrategyContext | None = None) -> StepContextMetadataDTO` verbatim from `LLMNodeStrategy._extract_step_context_metadata` (`@[backend_v2/services/orchestrator/strategies/llm.py#L116-L218]`).
         - Define `@dataclass(frozen=True) class BlueprintStageResult` encapsulating: `step_obj: V2Step`, `workflow_obj: Workflow`, `hook_state: HookState`, `hook_deps: HookDependencies`, `pre_events: list[TraceEvent]`, `block_map: dict[str, PromptBlock]`, `role_block: PromptBlock | None`, `protocol_block: PromptBlock | None`, `execution_persona_block: PromptBlock | None`, `criteria_blocks_models: list[PromptBlock]`, `output_profile_id: str`, `output_profile: OutputProfile`, `target_locale: str`, `global_source_text: str`, `state_data: dict[str, NodeStatePayload]`, and `inputs_payload: ExecutionInputsDTO`.
         - Implement `async def execute_blueprint_and_pre_hooks_stage(...) -> BlueprintStageResult` encapsulating lines 241–470 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`), accepting `step_logger: logging.Logger` so structured `step_logger.error(...)` emissions preserve logger name parity for existing `caplog` tests.
    </action>
  </step>

  <step id="2" name="Delegate Blueprint & Metadata Stage in LLMNodeStrategy and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in llm.py.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` to import `BlueprintStageResult`, `NodeStatePayload`, `_SCHEMA_BLOCK_EXTENSION`, `_SCHEMA_BLOCK_MATRIX`, `_SCHEMA_BLOCK_SYSTEM`, `_SCHEMA_BLOCK_TEXT`, `dlq_handle_debug_log_error`, `execute_blueprint_and_pre_hooks_stage`, and `extract_step_context_metadata` from `backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage` using explicit redundant aliases.
      2. Replace the bodies of `LLMNodeStrategy._dlq_handle_debug_log_error` (`@[backend_v2/services/orchestrator/strategies/llm.py#L107-L114]`) and `LLMNodeStrategy._extract_step_context_metadata` (`@[backend_v2/services/orchestrator/strategies/llm.py#L116-L218]`) with 1-line delegations to `dlq_handle_debug_log_error(exc)` and `extract_step_context_metadata(hook_state, context)`.
      3. Replace lines 241–470 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`) with a call to `await execute_blueprint_and_pre_hooks_stage(...)` unpacking the returned `BlueprintStageResult` attributes for downstream stages.
      4. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]` testing `dlq_handle_debug_log_error`, `extract_step_context_metadata` (DTO, atom, mapping, and results branches), and `execute_blueprint_and_pre_hooks_stage` (blueprint validation, prompt block resolution, output profile validation, and concurrency kwargs rejection).
    </action>
  </step>

  <step id="3" name="Run Phase 1 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both the new stage module and llm.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test --ast-strict` to verify all 45 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_extract_step_context_metadata_dto_and_atom_branches">
      Verifies that extract_step_context_metadata extracts gvars, doc_aliases, and AtomResultDTO dag_results identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_execute_with_role_and_persona_and_protocol">
      Verifies that execute_blueprint_and_pre_hooks_stage resolves role, protocol, persona, and criteria prompt blocks and loads the OutputProfile.
    </contract>
    <contract type="negative" name="test_execute_fails_fast_on_missing_prompt_block">
      Verifies that execute_blueprint_and_pre_hooks_stage logs an RFC 7807 error and raises ConfigurationError when a referenced prompt block ID is missing from block_map.
    </contract>
  </test_contracts>
</execution_protocol>
```
