# Epic 27 Phase 1: Context Isolation and Concurrency Optimization

## Objective
Implement Phase 1, Phase 2, and Phase 3 of Epic 27 to strictly filter input variables, dynamically generate chunk-specific rubrics, and open concurrency limits for high-speed Map-Reduce execution. The goal is to achieve significant payload size reductions without losing analytical fidelity, while pushing the concurrent API calls to safe mathematical optimums.

## Target Architecture
- **TARGET (Modify):** 
  - `backend_v2/services/orchestrator/prompt_compiler.py`
  - `backend_v2/services/orchestrator/strategies/llm.py`
  - `backend_v2/models/enums.py`
- **CONTEXT (Read-Only):**
  - `backend_v2/services/orchestrator/chunking_service.py`
  - `backend_v2/models/v2_core.py`

## Implementation Steps

### 1. Context Filtering (Phase 1: Input Pruning)
Modify `PromptCompiler.build_xml_context` in `backend_v2/services/orchestrator/prompt_compiler.py`:
- Identify where `llm_context_data` receives full `state_data` and restrict the extraction logic to ONLY surface data keys that are explicitly declared in the `step.input_mappings` dictionary.
- Prevent implicit or full background state (such as full text fields from previous non-related steps) from bleeding into the `<inputs>` XML.

### 2. Dynamic Chunk Rubrics (Phase 2: Surgical Rubrics)
Modify `LLMNodeStrategy.execute` in `backend_v2/services/orchestrator/strategies/llm.py`:
- Shift the generation of `dynamic_schema` and `xml_rubrics` out of the global scope and dynamically build them **inside** the `process_chunk(chunk)` loop.
- When generating schemas and rubrics for a specific chunk, filter the `criteria_blocks` to only include the specific matrices/blocks that correspond to the `atom_id`s or items present in that chunk.
- This effectively prevents the LLM from processing the "entire rubric instruction manual" for irrelevant criteria.

### 3. SystemConcurrency Updates (Phase 3)
Modify `SystemConcurrency` in `backend_v2/models/enums.py` to match the mathematically validated optimums:
- `MAX_CONCURRENT_LLM_STEPS` from 1 to 3
- `LLM_MAX_CHUNK_SIZE` from 15 to 40
- Ensure limits align strictly with the Epic's FinOps rate-limit survival numbers.

## Verification & Quality Gate Plan
- Verify Pydantic architectures via the unified script: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py backend_v2/services/orchestrator/strategies/llm.py backend_v2/models/enums.py`
- Run core tests to ensure no regressions occur in prompt compiling: `uv run python scripts/backend_audit_loop.py backend_v2/ -v --test`
