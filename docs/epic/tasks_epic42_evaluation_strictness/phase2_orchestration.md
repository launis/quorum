# Epic 42: Phase 2 - Backend Orchestration & Fail-Fast Pipeline

## Tavoite
Update the DAGExecutor and LLMTaskExecutor to pass the runtime `strictness_level` through the execution pipeline, enabling context-aware Pydantic validation and dynamic prompt injection.

## Architectural Laws (Must Follow)
- **Rule 1: LLM Structured Execution Mandate.** Rely ONLY on `LLMTaskExecutor.execute_structured_task()` to force execution via API native Structural Constraining.
- **Rule 2: Ephemeral Caching Topology.** The System Prompt MUST be 100% static. ALL dynamic data MUST be injected exclusively into the user message.
- **Rule 3: No Naked Dicts.** Do not read configuration from raw dictionaries in logic layer.

## Proposed Changes

### 1. `backend_v2/services/orchestrator/dag_executor.py`
**TARGET (Modify)**
- `DAGExecutor` must read the `strictness_level` from the typed `ExecutionRecord` / `ExecutionCreate` DTO.
- Pass `strictness_level` into the `LLMTaskExecutor.execute_structured_task()` calls.

### 2. `backend_v2/services/llm_task_executor.py`
**TARGET (Modify)**
- Update `execute_structured_task` signature to accept `validation_context: dict[str, Any] | None = None`.
- Pass this `validation_context` to the Pydantic `.model_validate_json()` or to the client's `run_structured_task` (which needs to pass it to Pydantic).
- Note: `backend_v2/llm/client.py` might need modification if it does the parsing. Let's explicitly say: Locate the `model_validate_json` or `model_validate` call for the LLM output and inject `context=validation_context`. 

### 3. Prompt Injection (PromptCompiler & Orchestrator)
**TARGET (Modify)**
- In the orchestration flow (e.g., in `chunk_worker.py`, `atomizer.py`, or `dag_executor.py`), generate the strictness instruction by calling `prompt_compiler.calibrate_strictness(level)`.
- Inject this dynamically at the **very end** of the `user` message, strictly inside XML tags:
```xml
<execution_parameters>
<STRICTNESS_CALIBRATION>
...ohje...
</STRICTNESS_CALIBRATION>
</execution_parameters>
```
- Wait, the `prompt_compiler.calibrate_strictness` is already implemented. We just need to make sure it's called and appended to the user message.

### 4. `backend_v2/llm/client.py` (If applicable)
**TARGET (Modify)**
- Ensure `run_structured_task` accepts `validation_context` and passes it to `response_model.model_validate_json(llm_output, context=validation_context)`.

## Verification & Quality Gate Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/[TARGET_FILES]`
- Ensure tests run with mocked `validation_context`.
