# Phase 2A: Pre-Hydrated Synthesis Strategy (Backend)

> **Source:** Epic 101, Phase 2 (Steps 1-4), Section 4 (Alias Hallucination Resilience, Fail-Fast Hydration, Single-Call Mandate, Rogue SDK Ban, Cache-Busting Prevention, Quote Normalization, FinOps)

## Goal

Implement `PreHydratedSynthesisStrategy` — the fast-path strategy that replaces heavy per-step Map-Reduce with a single LLM call fed from the pre-computed RAG Blackboard.

## Architectural Invariants (Injected)

- `llm_structured_execution_mandate`: All calls → `LLMTaskExecutor.execute_structured_task()` or `.execute_chat_task()`
- `alias_engine_llm_isolation_mandate` (+ KI): Convert UUIDs → short aliases before LLM, hydrate back after
- `prompt_compiler_immutability`: Do NOT modify `prompt_compiler.py`. Use its existing interface.
- `provider_agnostic_caching` (KI): Static system prompt, dynamic atoms at the end
- `high_fidelity_prompting`: XML structural sovereignty for prompt boundaries
- `rogue_sdk_ban` (Epic §4): No direct SDK imports — `LLMClient.from_strategy()` only
- `single_call_mandate` (Epic §4): Exactly 1 LLM call per step, no hidden loops
- `tda_best_of_three_flash` (KI): **OVERRIDDEN** — Synthesis uses Cascading, NOT Bo3

## Dependencies

- **Phase 1A AND Phase 1B MUST be completed first** (blackboard model exists, context_variables populated).

---

## Milestone 2A.1: Create `PreHydratedSynthesisStrategy` Class

**Source: Epic Phase 2, Steps 1-4**

### TARGET (New): [pre_hydrated_synthesis.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py)

Create a new strategy file implementing `NodeStrategy` (base class from `strategies/base.py`).

**Class structure:**

```python
class PreHydratedSynthesisStrategy(NodeStrategy):
    """Single-call synthesis strategy hydrated from the RAG Blackboard.
    
    Replaces per-step Map-Reduce with a single LLM call by reading
    pre-extracted atoms from the GlobalAtomBlackboard in context_variables.
    Enforces the Single-Call Mandate: exactly ONE LLM request per step.
    """
```

**`execute()` method logic:**

1. **Fail-Fast Hydration & Context Wiring** (Epic §4):
   > **CRITICAL ARCHITECTURE RULE:** `DAGExecutor` does not currently pass `context_variables` down to `NodeExecutor`. You MUST first modify `StrategyContext` in `base.py` to add `context_variables: dict[str, Any] = Field(default_factory=dict)`. Then, modify `NodeExecutor.execute()` and `DAGExecutor` (line ~543) to pass `exec_record.context_variables` into it.
   
   Once wired, read the blackboard safely:
   ```python
   raw_blackboard = context.context_variables.get("global_atoms")
   if raw_blackboard is None:
       logger.error("preflight_blackboard_missing", extra={"execution_id": context.execution_id})
       # Note: You MUST add DEPENDENCY_ERROR to ErrorCodes in exceptions.py
       raise AppException(
           status_code=500,
           message="global_atoms missing from context_variables",
           details={"error_code": "DEPENDENCY_ERROR"}
       )
   blackboard = GlobalAtomBlackboard.model_validate(raw_blackboard)
   ```

2. **Hydrate Facts & Alias Isolation** (Epic Phase 2, Step 1):
   - Read `step.input_mappings` to determine which input keys this step maps (e.g., only `$inputs.product_text` → key `product_text`)
   - Extract ONLY the corresponding `DraftAtomList`s from `blackboard.atoms_by_input[key]`
   - Pass atoms through `AliasEngine` to convert `draft_id` values into short semantic aliases (`a0`, `a1`...)
   - This prevents Attention Drift from long UUIDs

3. **Preserve Prompt Logic** (Epic Phase 2, Step 2):
   - Use the existing `PromptCompiler` instance (injected via constructor, same as LLMNodeStrategy) to compile the step's Matrix Block rules
   - The compiled prompt preserves BARS scales, Toulmin models, XAI requirements exactly as defined in the UI
   - **BANNED**: Raw f-string injection of prompt content

4. **Dual-Input Context / Ephemeral Caching Topology** (Epic Phase 2, Step 3):
   - System prompt: 100% static (compiled Matrix rules from PromptCompiler)
   - User payload: Dynamic atoms injected at the absolute END inside `<user_payload>` XML fence
   - Raw source documents are passed as context cache entries via the LLM client's native caching mechanism

5. **Single-Call Synthesis & Cascading Escalation** (Epic Phase 2, Step 4 & Epic §4 FinOps):
   - Use `LLMClient.from_strategy(step_def.model_strategy, repo)` — the strategy is the step's native model_strategy from `seed_data.json` (e.g., `"fast"`, `"synthesis"`).
   - Execute the call exclusively via `executor.execute_structured_task()`. (`execute_chat_task()` is STRICTLY BANNED because synthesis must produce strict SDUI DTOs).
   - **Cascading Routing**: Wrap the execution in a `try-except ValidationError` block. If Pydantic validation fails with the initial strategy, you MUST catch the error, log a warning, and dynamically escalate by making exactly ONE retry using `LLMClient.from_strategy("reasoning", repo)`. 
   - **NO HIDDEN LOOPS**: Other than the single reasoning escalation fallback, there are NO LOOPS. Do not use Best-of-Three. If the reasoning fallback also fails, let it Fail-Fast.

6. **Alias Reverse Hydration & Safe Dropping** (Epic §4 — Alias Hallucination Resilience):
   > **CRITICAL ARCHITECTURE RULE:** `AliasEngine.hydrate_dict_list()` is broken for both arrays and scalars: it does NOT drop invalid aliases, which causes Pydantic to crash the step.
   - You MUST add a new method to `AliasEngine` called `hydrate_and_filter_aliases(data: Any, field_names: set[str])` that recursively traverses dicts/lists.
   - **List Handling**: If it encounters a list under a `field_name` (e.g. `depends_on: ["a0", "a99"]`), it must map valid aliases and strictly DROP invalid aliases from the list.
   - **Scalar Handling**: If it encounters a single scalar string under a `field_name` (e.g. `primary_source: "a99"`), and the alias is invalid, it MUST set the field to `None`.
   - In both cases, emit `logger.warning("hallucinated_alias_dropped", extra={"alias": "a99"})` for each dropped alias.
   - Call this new method on the raw JSON dict returned by `LLMClient` BEFORE instantiating the final Pydantic response model to prevent validation crashes.

### CONTEXT (Read-Only):
- `backend_v2/services/orchestrator/strategies/base.py` — `NodeStrategy`, `StrategyContext`
- `backend_v2/services/orchestrator/dag_executor.py` — `DAGExecutor` context variable passing
- `backend_v2/services/orchestrator/strategies/llm.py` — Reference for constructor pattern
- `backend_v2/services/orchestrator/prompt_compiler.py` — Existing `PromptCompiler` interface
- `backend_v2/utils/alias_engine.py` — `AliasEngine`
- `backend_v2/models/domain/blackboard.py` — `GlobalAtomBlackboard`
- `backend_v2/llm/client.py` — `LLMClient.from_strategy()`
- `backend_v2/services/llm_task_executor.py` — `LLMTaskExecutor`

---

## Milestone 2A.2: Strategy Routing in `NodeExecutor.execute()`

**Source: Epic Phase 3, Step 2 — "implement a routing priority cascade"**

### TARGET (Modify): [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py)

In `NodeExecutor.execute()` (line ~221), BEFORE the existing `if step_def.type == "logic"` check, add:

```python
# Engine override routing priority cascade
match step.engine_override:
    case EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS:
        strategy_impl = PreHydratedSynthesisStrategy(
            self.exec_repo, self.workflow_repo, self.comp_repo,
            self.prompt_block_repo, self.output_profile_repo,
            self.identity_repo, self.audit_repo, self.system_repo,
            self.compiler, arq_pool=arq_pool,
        )
    case EngineOverrideStrategy.DYNAMIC_TOOL_AGENT:
        # Falls through to default LLM strategy with tool access
        strategy_impl = LLMNodeStrategy(...)
    case None:
        # Default fallback to existing step_def.type routing
        if step_def.type == "logic":
            strategy_impl = LogicNodeStrategy(...)
        else:
            strategy_impl = LLMNodeStrategy(...)
```

Add imports for `PreHydratedSynthesisStrategy` and `EngineOverrideStrategy`.

### CONTEXT (Read-Only):
- `backend_v2/models/enums.py` — `EngineOverrideStrategy`

---

## Milestone 2A.3: Register Strategy in `__init__.py`

**Source: Standard module registration**

### TARGET (Modify): [strategies/__init__.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/__init__.py)

Add the new strategy to the module exports.

### CONTEXT (Read-Only): None.

---

## Milestone 2A.4: Structural Test for Ephemeral Caching Topology

**Source: Epic Section 4 — Cache-Busting Prevention (Topology Verification)**

### TARGET (New): [test_cache_busting_prevention.py](file:///c:/src/quorum/backend_v2/tests/unit/services/orchestrator/test_cache_busting_prevention.py)

Create a structural unit test to verify that the `PromptCompiler` outputs an identical `System Message` when compiling the exact same Matrix Block across two different executions (different dynamic context variables). 

This is an architectural requirement to enforce the Ephemeral Caching Topology. If the hash differs, it means dynamic data has leaked into the static block, preventing Vertex AI from reusing the context cache. 

1. Setup two dummy `GlobalAtomBlackboard` payloads with completely different atoms.
2. Compile a mock `StepRule` with a `PromptBlock` using `PromptCompiler` with the first payload, extract the System Message, and hash it.
3. Compile the same `StepRule` with the second payload, extract the System Message, and hash it.
4. `assert hash1 == hash2`, "Dynamic data leaked into the static system prompt!"
5. Assert that the dynamic atoms were injected exclusively into the trailing User Message.

---

## Bidirectional Integration Check

| Consumer | Producer | Verified? |
|---|---|---|
| `PreHydratedSynthesisStrategy` reads `context_variables["global_atoms"]` | `_execute_rag_preflight()` (Phase 1B) writes it | ✅ |
| `PreHydratedSynthesisStrategy` uses `PromptCompiler` output | `PromptCompiler` exists (READ-ONLY) | ✅ |
| `AliasEngine` hydration maps aliases to UUIDs | `AliasEngine` already exists in `utils/` | ✅ |
| `NodeExecutor` routes via `engine_override` | `StepRule.engine_override` field (Phase 1A) | ✅ |

---

## Testing & Quality Gate Plan

### Unit Tests:
1. **`test_pre_hydrated_synthesis.py`** — Test the full execute() flow with mocked LLM executor, verify single-call mandate (exactly 1 LLM invocation).
2. **`test_pre_hydrated_fail_fast.py`** — Verify `DependencyError` when `global_atoms` is missing.
3. **`test_pre_hydrated_alias_hydration.py`** — Mock AliasEngine, verify alias injection before LLM call and reverse hydration after.
4. **`test_pre_hydrated_hallucination_drop.py`** — Verify hallucinated aliases are dropped with logger.warning, not crashed.
5. **`test_node_executor_routing.py`** — Verify `engine_override` priority cascade in `NodeExecutor.execute()`.
6. **`test_cache_busting_prevention.py`** — Structural test: compile same prompt twice, compare system message hash. Must match (no dynamic data leaked into static block).

### Quality Gate:
```
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/ --test
```

---

## Session Handover
```
Achieved: PreHydratedSynthesisStrategy with AliasEngine, single-call mandate, and routing cascade.
Remaining: Phase 2B (Flutter StepRule + seed_data), Phase 3 (Reasoning strategy + Vertex adapter).
```
