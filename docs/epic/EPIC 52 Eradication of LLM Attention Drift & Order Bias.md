# EPIC 52: Eradication of LLM Attention Drift & Order Bias

## 1. Executive Summary
The system currently suffers from "Lost in the Middle" syndrome and Order Bias (Attention Drift) due to massive context evaluation limits (e.g., 60 TDA atoms per chunk) and global random shuffling. To ensure absolute B2B SaaS deterministic reliability, we will refactor the orchestration pipeline to use Semantic Micro-Batching (max 10 atoms), modern `asyncio.TaskGroup` concurrency, Context Caching, and Exhaustive Chain-of-Thought (CoT) enforcing `reasoning_trace` articulation for *every* evaluated atom natively via Pydantic schema ordering.

## 2. Architectural Invariants to Enforce (Antigravity Constraints 00-05)
This Epic MUST be planned and executed strictly adhering to the following Zero-Trust principles:
- **Universal Fail-Fast (`00-antigravity-core` / `01-python-backend`)**: Pydantic models must use `extra='forbid', strict=True, frozen=True`. If an LLM micro-batch evaluates 10 atoms, the parsed array MUST contain exactly 10 evaluated DTOs. Mismatches must raise an `AppException` instantly. No `.get()` fallback hacks.
- **Python 3.14 Modern Syntax (`01-python-backend`)**: Enforce `async with asyncio.TaskGroup() as tg:` for parallel chunk execution. Legacy `asyncio.gather()` is strictly BANNED.
- **System Concurrency SSOT (`05_llm_architecture`)**: Parallel execution of micro-batches MUST be throttled using an `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)`. Hardcoded limits are banned.
- **High-Fidelity Caching (`05_llm_architecture`)**: System prompts must remain 100% static. Dynamic contextual inputs (`product_text`, `chat_log`) must be positioned securely in `<source_data>` tags to utilize Provider-Agnostic Context Caching efficiently across all concurrent micro-batch calls. Dynamic micro-chunks must be injected exclusively at the end of the `user` message.
- **LLM Structured Execution Mandate (`05_llm_architecture`)**: Execution MUST route through `LLMTaskExecutor.execute_structured_task()` to guarantee Fail-Fast Pydantic validation.
- **Seed Vault Mutations (`03_seed_vault`)**: Modifying evaluation prompts requires precise `seed_data.json` modifications via scripted migrations (`modify_seed.py`).

## 3. Implementation Phases

### Phase 1: Exhaustive CoT in Pydantic Schemas (Backend Models & Seed Vault)
**Objective:** Eliminate LLM lazy scanning by forcing the evaluation of every single rule before arriving at a conclusion via Pydantic ordering.
**Execution Mandates:**
1. Locate the output schema for TDA Assertion results (e.g., `backend_v2/models/dtos/` or equivalent). The system already utilizes the so-called "Alphabetical Keys Hack" method (`step_1_...`, `step_4_reasoning`, `step_5_boolean`).
2. **CRITICAL ORDERING & REFINEMENT (Alphabetical Sorting Trap & Pydantic Aliases):** Although Pydantic V2 preserves field ordering, the LLM still needs to generate raw JSON text. Because the letter 'i' (`is_true`) comes before 'r' (`reasoning_trace`) alphabetically, the model might optimize by pushing the boolean value first. You must strictly adhere to numerical prefixes so that the generation order is mechanically guaranteed. Since the LLM generates JSON from top to bottom, this physically forces the model into a System 2 state (Chain-of-Thought) prior to decision making. To maintain clean Python backend code while strictly enforcing the JSON schema order, use Pydantic's alias feature. Define properties intuitively (e.g., `reasoning_trace`) but alias them for the LLM. Ensure the dynamically compiled prompt schema sent to the LLM enforces these specific aliased keys.
3. Enhance the `reasoning_trace` validation: `reasoning_trace: str = Field(..., alias='step_1_reasoning_trace', min_length=15, description="MANDATORY: Document causal logic BEFORE yielding boolean.")`.
4. **Seed Update:** Create a `modify_seed.py` script to update `backend_v2/seed/seed_data.json`. Remove lazy instructions (e.g., "Find ONE occurrence"). Inject the mandate: *"EXHAUSTIVE EVALUATION MANDATE: You MUST sequentially provide a `step_1_reasoning_trace` for EVERY claim provided in this batch. If evidence is found, quote it. If not found, explicitly explain why the document passed."*

### Phase 2: Semantic Grouping & Deterministic Batching (Orchestrator)
**Objective:** Replace global random shuffle with semantic batching to prevent Context Switching fatigue and ensure testing reproducibility.
**Execution Mandates:**
1. Target the atomization logic (e.g., `backend_v2/services/orchestrator/atomizer.py` or `chunking_service.py`).
2. Remove all global `random.shuffle()` operations across the atom arrays.
3. **Semantic Grouping:** Group TDA atoms by their parent `PromptBlock` (`category_id` or `matrix_id`). The LLM must evaluate conceptually identical rules in the same micro-batch.
4. **100% Deterministic Sorting (No Sacrificial Atoms):** Sort groups and atoms deterministically using a **purely static key**, e.g., alphabetical order `sorted(atoms, key=lambda x: x.id)`. NEVER use `execution_id` as a sorting key, as this would break SSOT reproducibility across runs. Because we are using Micro-Batching (Chunk=10), static sorting is safe: the LLM's "Lost in the Middle" blind spot is eradicated, and the list will not produce "Sacrificial Atoms", ensuring CI/CD testability and audit objectivity meet without compromise.
5. Slice these groups into strict micro-batches setting `LLM_MAX_CHUNK_SIZE = 10` (update in settings/enums).
6. **Mitigate Pattern Matching Bias:** Because semantic grouping places highly similar rules in the same micro-batch, the LLM might suffer from "Pattern Matching Bias" (e.g., if it evaluates the first 4 claims as false, it might lazily assume the 5th is also false). Update the prompt definitions in `seed_data.json` to inject the following strict isolation directive: *"EVALUATION MANDATE: Treat every claim in this batch as a completely isolated audit. Do not let the outcome of Claim N influence Claim N+1."*

### Phase 3: Micro-Batch TaskGroup Concurrency (Orchestrator)
**Objective:** Process micro-batches concurrently to neutralize the latency impact of chunk reduction.
**Execution Mandates:**
1. Target the LLM execution worker (e.g., `chunk_worker.py` or equivalent in `backend_v2/services/orchestrator/strategies/llm_execution/`).
2. Refactor the execution loop using modern syntax: `async with asyncio.TaskGroup() as tg:`.
3. **RPM Rate Limiting & Concurrency:** A simple `asyncio.Semaphore` is insufficient because it only limits concurrent calls. If 5 calls finish in 10 seconds, the `TaskGroup` will immediately fire 5 more, triggering a 429 Resource Exhausted error (e.g., Gemini's 5 RPM limit). Implement a Token Bucket RPM limiter (e.g., using `aiolimiter.AsyncLimiter`) in conjunction with the Semaphore to throttle requests effectively. The AsyncLimiter and Semaphore MUST be instantiated as global/class-level singletons (e.g., injected from the Orchestrator) and passed down to the task level. Do NOT instantiate them locally inside the execution worker, as they must pool and throttle concurrency globally across all micro-batches.
4. **Provider-Agnostic Context Caching (Model Independence):** In strict accordance with `05_llm_architecture.md` (the `direct_sdk_calls` ban), the caching strategy MUST be model-independent. Do not hardcode "Vertex Prompt Caching" SDK calls or dependencies. Instead, rely on the `LLMClient.from_strategy()` abstraction. Prompt caching is achieved inherently by standardizing the prompt structure so that any underlying provider (Vertex, OpenAI, Anthropic) can utilize its native prefix caching automatically.
5. **Strict Static Prefix & High-Fidelity Prompting:** To preserve Context Caching across all micro-batches, the `PromptCompiler` (`backend_v2/services/orchestrator/prompt_compiler.py`) MUST enforce the `high_fidelity_prompting_and_caching` and `ephemeral_caching_topology` rules. *(Note: Per `prompt_compiler_immutability` rule in `01-python-backend.md`, modifying `prompt_compiler.py` requires explicit USER CONFIRMATION before execution.)*
   - The System Prompt MUST be 100% static.
   - Massive data payloads MUST be rigidly wrapped in `<source_data>` tags within the static prefix.
   - All dynamic execution variables MUST be isolated into an `<execution_parameters>` XML tag.
   - Absolutely NO dynamic variables (e.g., `execution_id`, timestamps, or indices) may be injected into the cached system instruction.
   - The semantic chunk of 10 atoms MUST be injected strictly into a `<current_evaluation_batch>` XML block at the *absolute end* of the `user` message.
   This strict byte-for-byte identical prefix makes the transition from 60-atom to 10-atom chunks economically and latentially viable, regardless of the underlying LLM provider.

### Phase 4: Map-Reduce Strict Coverage Verification (Reducer)
**Objective:** Merge the concurrent micro-batch outputs back into the global trace flawlessly and verify total coverage.
**Execution Mandates:**
1. Target the reducer (e.g., `backend_v2/services/orchestrator/matrix_reducer.py`).
2. The Reducer MUST process a list of strongly typed Pydantic DTOs, NOT naked dictionaries.
3. **Strict Set-Based Verification & Deterministic Sorting:** Because `asyncio.TaskGroup` completes tasks non-deterministically based on latency, the Reducer MUST explicitly re-sort the combined DTO array back into the original static input order (e.g., `sorted(processed_dtos, key=lambda x: x.tda_id)`) BEFORE mathematically verifying the sets or finalizing the state delta. This guarantees byte-for-byte reproducibility. Then, the Reducer MUST mathematically verify coverage using Set operations on the unique IDs, NOT just simple length checks. An LLM might duplicate an ID and drop another, passing a length check but corrupting data. Execute `input_ids == processed_ids`. If they do not match, raise an `AppException` (Fail-Fast) for hallucinated or missing IDs.
4. **Localized Micro-Retry Resilience:** Because the batches are strictly limited to 10 atoms, a failure in one micro-batch should NOT globally crash the entire execution run. Implement a localized Fail-Fast retry mechanism (e.g., using the `tenacity` library) directly at the internal task level within the `TaskGroup`. If Micro-Batch 3 fails validation or coverage checks, only retry Micro-Batch 3, drastically improving system resilience. When applying tenacity for localized micro-retries, explicitly enforce Exponential Backoff with Jitter (e.g., `wait=wait_random_exponential(...)`). This prevents the 'Thundering Herd' problem if multiple concurrent micro-batches hit rate limits simultaneously. Only catch explicit API/Validation errors, never broad Exceptions.
5. **Strict Retries & DLP Logging (`05_llm_architecture.md` compliance):** In accordance with the `infinite_retry_loops` ban, the tenacity retry MUST be strictly capped using `stop=stop_after_attempt(SystemConcurrency.LLM_MAX_RETRIES)`. Furthermore, adhering to `data_leak_logging`, if the micro-batch ultimately fails, you MUST NOT log the raw LLM payload, PII, or the full Pydantic exception text block. Log ONLY the mathematical/enumerated error code and Trace ID before raising the `AppException`.

## 4. Testing & Universal Quality Gate
- **Unit Tests (`tests/backend_v2/services/orchestrator/`)**: 
  - Write tests verifying the deterministic sorting mechanism and semantic grouping.
  - Verify that `TaskGroup` properly bubbles up exceptions (Fail-Fast) when an LLM hallucination occurs inside a micro-batch using `polyfactory` and `mock_data.py`. Live LLM calls are strictly forbidden.
- **Documentation Update**: Update the relevant `docs/architecture/` documents (specifically `04_workflow_and_dag.md` and `06_evaluation_and_scoring.md`) and `.agents/rules/04_directory_reference.md` to reflect the new Semantic Micro-Batching, Exhaustive CoT mechanisms, and any structural changes.
- **Audit Requirement**: After all phases are coded, execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test` before declaring completion.