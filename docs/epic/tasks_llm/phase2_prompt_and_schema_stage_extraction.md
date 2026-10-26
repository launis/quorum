<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 2: Context Building, Prompt Compilation & Dynamic Schema Stage Extraction (`phase2_prompt_and_schema_stage_extraction.md`)

## 1. Objective
Execute Phase 2 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]`:
1. Extract Stage 2 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`: `schema_map` & `blueprint_labels` resolution from `workflow_obj.steps`, `ContextBuilder.build`, matrix `shuffled_atoms` validation and `StepExecutionMetadataDTO` tagging, `PromptFactory.build`, `<execution_parameters>` appending from `OutputProfile`, `ChunkingService.chunk_payload`, `ExecutionRecord` lookup for `SourceDocumentContext` validation, and `dynamic_schema` resolution via `compiler.compile_schema` / `SchemaBuilderRegistry.get`) into `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]` (`< 310` lines) returning an immutable `@dataclass(frozen=True) class PromptAndSchemaStageResult`.
2. Update `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` to delegate Stage 2 of `execute` to `execute_prompt_and_schema_stage` with explicit redundant re-exports.
3. Create dedicated unit tests in `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]` | `PromptAndSchemaStageResult` and `execute_prompt_and_schema_stage` encapsulating context building, prompt compilation, atom chunking, `SourceDocumentContext` validation, and dynamic schema resolution (`< 310` lines) |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` | Delegate Stage 2 of `execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`) to `execute_prompt_and_schema_stage` with explicit redundant re-exports |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py]` | Register `backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py` in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` during Epoch 1 pure structural lift-and-shift |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]` | Unit tests for `execute_prompt_and_schema_stage` covering matrix shuffled atoms validation, output profile `<execution_parameters>`, chunking, `SourceDocumentContext` fail-fast validation, and dynamic schema compilation |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Prompt & Schema Stage Sub-Module">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py during Phase 2 while backend_v2/services/orchestrator/strategies/llm.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">prompt_and_schema_stage.py MUST NOT import from backend_v2.services.orchestrator.strategies.llm and MUST remain under 350 lines with all lines <= 120 characters.</constraint>
    <action>
      1. Add `"backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py"` to `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` for the verbatim Epoch 1 lift-and-shift of `ExecutionRecord` reconstitution.
      2. Create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]` (`< 310` lines, all lines `<= 120` chars) with `__all__ = ["PromptAndSchemaStageResult", "execute_prompt_and_schema_stage"]`:
         - Import `BlueprintStageResult`, `_SCHEMA_BLOCK_EXTENSION`, `_SCHEMA_BLOCK_MATRIX`, `_SCHEMA_BLOCK_SYSTEM`, and `_SCHEMA_BLOCK_TEXT` from `backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage`.
         - Define `@dataclass(frozen=True) class PromptAndSchemaStageResult` encapsulating: `hook_state: HookState`, `prompt_payload: PromptPayload`, `matrix_block: PromptBlock | None`, `target_chunks: list[list[PromptAtom]] | None`, `dynamic_schema: type[BaseModel] | None`, `is_synthesis_step: bool`, `source_doc_ctx: SourceDocumentContext`, `schema_map: dict[str, dict[str, str]]`, and `blueprint_labels: dict[str, str]`.
         - Implement `async def execute_prompt_and_schema_stage(...) -> PromptAndSchemaStageResult` encapsulating Stage 2 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`), preserving 100% identical runtime behavior, immutable `frozen_ctx.generated_schemas` handling, and structured `step_logger.error(...)` logging.
    </action>
  </step>

  <step id="2" name="Delegate Prompt & Schema Stage in LLMNodeStrategy and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in llm.py.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` to import `PromptAndSchemaStageResult` and `execute_prompt_and_schema_stage` from `backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage` using explicit redundant aliases.
      2. Replace Stage 2 inside `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`) with a call to `await execute_prompt_and_schema_stage(...)` unpacking `PromptAndSchemaStageResult` for Stage 3.
      3. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]` testing `execute_prompt_and_schema_stage` across matrix atom chunking, missing `shuffled_atoms` fail-fast errors, `<execution_parameters>` synthesis injection, `SourceDocumentContext` validation, and `dynamic_schema` resolution.
    </action>
  </step>

  <step id="3" name="Run Phase 2 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both prompt_and_schema_stage.py and llm.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test --ast-strict` to verify all 45 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_output_profile_directives_relocated_to_user_payload_and_system_prompt_invariant_neg09">
      Verifies that execute_prompt_and_schema_stage appends execution_parameters to user_payload while keeping system_prompt 100% static.
    </contract>
    <contract type="positive" name="test_matrix_step_succeeds_when_shuffled_atoms_only_in_dynamic_inputs">
      Verifies that execute_prompt_and_schema_stage resolves shuffled_atoms from inputs_payload.dynamic_inputs and chunks matrix atoms via ChunkingService.
    </contract>
    <contract type="negative" name="test_llm_strategy_missing_atoms_crash">
      Verifies that execute_prompt_and_schema_stage raises ConfigurationError when a matrix step has neither shuffled_atoms nor PromptBlock atoms.
    </contract>
  </test_contracts>
</execution_protocol>
```
