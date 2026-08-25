<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
</required_context_rules>

# EPIC 147: Engine Dispatch, Cognitive Grounding Resilience & DAG Concurrency Hardening

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
EPIC 147 establishes a robust, fail-fast, and decoupled execution and prompt architecture across the Quorum backend engine. The epic consolidates execution engine dispatch, extracts dedicated non-matrix execution pipelines into `PromptEngine`, eliminates prompt duplication and token bloat from dual theory grounding injections, hardens `DAGExecutor` against multi-task race conditions and in-place `FrozenContext` mutations, eliminates ghost tool executions in source verification hooks, enforces polymorphic static node strategy routing via `NODE_STRATEGY_REGISTRY`, implements fail-fast prompt block batch resolution with mathematical set parity, and encapsulates multi-dependency groupings into `StrategyDependencies`.

### 1.2 Problem Statement & Root Cause Analysis
1. **Theory Grounding Dual Injection & Prompt Bloat**: In `@[backend_v2/seed/seed_data.json]`, epistemic and academic grounding anchors are duplicated across both `PromptBlock.ai_description` (as freeform `EPISTEMIC ANCHOR:` text blocks) and `PromptBlock.theory_grounding` (as structured `TheoryGrounding` DTOs). When `MatrixSensorPromptBuilder` compiles the prompt, it injects both the raw text description and the structured object with raw URLs (`source_url`), triggering prompt duplication, URL token bloat, XML syntax corruption risks, and Single Source of Truth (SSOT) drift.
2. **Strategy Constructor Bloat & Parameter Anti-Pattern**: In `@[backend_v2/services/orchestrator/strategies/base.py]`, `@[backend_v2/services/orchestrator/strategies/llm.py]`, and `@[backend_v2/services/orchestrator/strategies/logic.py]`, strategy constructors accept 10–11 decoupled dependencies directly, creating brittle parameter coupling and violating typed dependency injection standards.
3. **Execution Engine Monolith & Lack of Dedicated Prompt Engine**: `LLMNodeStrategy` historically contained branching logic for non-matrix prompt tasks (specifically `step_input_processing`), lacking an isolated `ExecutionEngine` protocol implementation comparable to `TDAEngine` and `SynthesisEngine`. Furthermore, `LLMNodeStrategy` executes full-table repository scans (`get_all_prompt_blocks()`) during node execution instead of receiving targeted prompt blocks resolved once by `NodeExecutor`.
4. **DAG Executor Concurrency Race Conditions & FrozenContext Mutation**: In `@[backend_v2/services/orchestrator/dag_executor.py]`, parallel node execution tasks in `asyncio.TaskGroup` overwrite `mcp_tool_audit` metadata during non-synchronized `model_copy` operations. Concurrently, `LLMNodeStrategy` directly mutates `frozen_ctx.generated_schemas` in place, violating the immutability contract of Pydantic V2 `FrozenContext` (`frozen=True`) and creating transient race conditions during serialization (`_safe_commit()`). Trace events in the for-loop at L693-L703 are also appended to `exec_record.execution_trace` outside `_update_lock`.
5. **Ghost Execution in Source Verification Hook**: `@[backend_v2/hooks/source_verification_hook.py]` and `@[backend_v2/services/source_verification_service.py]` execute expensive external Tavily searches and LLM evaluation tasks even when `prior_analysis` or payload text inputs are empty, whitespace-only, or malformed non-string structures. The hook lacks registry registration (`@hook_registry.register("source_verification")`), export in `hooks/__init__.py`, input/output DTO encapsulation, and contains hardcoded mock LLM credentials (`api_key="mock"`).
6. **Procedural Strategy Branching & Dangling Batch References**: Node strategy dispatch in `NodeExecutor` relies on procedural `if step_def.type == "logic"` branching and string literals instead of a canonical `StepType` enum and static registry routing. In `@[backend_v2/database/repositories/components/prompt_block.py]`, batch resolution lacks a targeted, fail-fast lookup with mathematical set validation, risking silent partial returns and dangling references.

---

## 2. Scope & File Modification Boundary

### 2.1 TARGET Files (Editable)
- `[MODIFY]` `@[backend_v2/models/enums.py]` (Declare canonical `StepType(StrEnum)`: `LLM = "llm"`, `LOGIC = "logic"` and export in `__all__`)
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L540-L585]` (Update `Step.type: StepType = Field(default=StepType.LLM)`)
- `[MODIFY]` `@[backend_v2/database/interfaces.py#L677-L740]` (Add `get_prompt_blocks_by_ids(block_ids: list[str], strict: bool = True) -> list[dict[str, Any]]` to `IPromptBlockRepository`)
- `[MODIFY]` `@[backend_v2/database/repositories/components/prompt_block.py#L50-L115]` (Implement `get_prompt_blocks_by_ids` with strict mathematical set parity `unique_requested - found_ids` raising `AppException(RESOURCE_NOT_FOUND, missing_ids=...)`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L88]` (Format `<theory_context>\n{citation}\n</theory_context>` in ephemeral system rule block, omitting raw URLs)
- `[NEW]` `@[backend_v2/services/orchestrator/engines/prompt_engine.py]` (Extract `PromptEngine` implementing `ExecutionEngine` protocol for structured non-matrix LLM tasks)
- `[MODIFY]` `@[backend_v2/services/orchestrator/engines/__init__.py#L1-L15]` (Re-export `PromptEngine` in `__all__ = ["ExecutionEngine", "TDAEngine", "SynthesisEngine", "PromptEngine"]`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/base.py#L50-L105]` (Add `prompt_blocks: list[PromptBlock]` to `StrategyContext`, define `StrategyDependencies` dataclass, update `NodeStrategy.__init__`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/logic.py#L19-L50]` (Update `LogicNodeStrategy.__init__(self, deps: StrategyDependencies)`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]` (Update `LLMNodeStrategy.__init__(self, deps: StrategyDependencies, engine: ExecutionEngine)`, consume injected `context.prompt_blocks`, eliminate `get_all_prompt_blocks()`, eliminate in-place `frozen_ctx.generated_schemas` mutation, clean scoped technical debt)
- `[NEW]` `@[backend_v2/services/orchestrator/strategies/registry.py]` (Declare `StrategyBuilder` Protocol, static `NODE_STRATEGY_REGISTRY`, and `NodeStrategyFactory.create_strategy`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py#L115-L375]` (Update `NodeExecutor.__init__(self, deps: StrategyDependencies)`, implement `_resolve_execution_engine`, single-fetch & hydrate prompt blocks, delegate to `NodeStrategyFactory.create_strategy`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py#L690-L730]` (Atomic deduplicating accumulator for `mcp_tool_audit` and `generated_schemas` under `_update_lock`, move trace append loop inside `_update_lock`)
- `[MODIFY]` `@[backend_v2/models/state.py#L110-L135]` (Verify/add `mcp_audit_traces: list[MCPAuditTrace]` to `TraceEvent`)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]` (Sanitize all 13 matrices: remove `EPISTEMIC ANCHOR:` tails while preserving qualitative prompt definitions)
- `[MODIFY]` `@[backend_v2/hooks/source_verification_hook.py#L1-L47]` (Attach `@hook_registry.register("source_verification")`, parse `SourceVerificationInputsDTO`, short-circuit on empty/whitespace inputs returning complete zero-claims envelope)
- `[MODIFY]` `@[backend_v2/services/source_verification_service.py#L1-L257]` (Add `MIN_VERIFIABLE_TEXT_LENGTH = 15`, static module constants `_EXTRACTION_SYSTEM_PROMPT` and `_VERIFICATION_SYSTEM_PROMPT`, dynamic `LLMClient.from_strategy`, `html.escape()` for XML injection defense)
- `[MODIFY]` `@[backend_v2/models/dtos/source_extraction_schema.py#L1-L25]` (Declare `SourceVerificationInputsDTO` with `strict=True`, `extra="forbid"`, strictly no `@property`)
- `[MODIFY]` `@[backend_v2/hooks/__init__.py#L7-L42]` (Import and export `source_verification_hook` in `__all__`)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L266]` (Remove stale mock `@patch("...tda_engine.get_settings")`, update to `StrategyDependencies` and typed models)
- `[NEW]` `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]` (Comprehensive ISTQB unit test suite for `PromptEngine`)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py#L12-L38]` (Update test assertions to verify pure `<theory_context>` XML formatting and raw URL omission)
- `[MODIFY]` `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py#L32-L50]` (Update root prompt builder tests to match pure `<theory_context>` structure)
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_source_verification_service.py#L1-L137]` (Add tests for empty, whitespace, sub-threshold, and escaped XML inputs)
- `[MODIFY]` `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]` (Add unit tests for `get_prompt_blocks_by_ids` success, empty, duplicate, strict missing single/all, and non-strict)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L287-L347]` (Update fixtures to `StrategyDependencies`, migrate mocks to typed Pydantic models, test engine injection)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L1-L564]` (Update fixtures to `StrategyDependencies`, migrate mocks to typed Pydantic models, test `PromptEngine` payload compilation)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L1-L100]` (Update fixtures to `StrategyDependencies`, migrate mocks to typed Pydantic models)
- `[MODIFY]` `@[backend_v2/tests/unit/test_logic.py#L1-L177]` (Update fixtures to `StrategyDependencies`, migrate mocks to typed Pydantic models)
- `[NEW]` `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]` (Unit tests for hook registration, empty/whitespace short-circuits, zero-claims envelope parity)
- `[NEW]` `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]` (Comprehensive AST guardrail suite locking all 8 architectural invariants)
- `[NEW]` `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]` (Concurrency tests for `mcp_tool_audit` and `generated_schemas` atomic accumulation)
- `[NEW]` `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]` (Unit tests for static strategy registry and factory dispatch)

### 2.2 CONTEXT Files (Read-Only)
- `@[backend_v2/models/v2_core.py#L194-L208]` (`TheoryGrounding` schema SSOT)
- `@[backend_v2/models/v2_core.py#L635-L657]` (`MCPAuditTrace` schema SSOT)
- `@[backend_v2/models/v2_core.py#L1563-L1700]` (`FrozenContext`, `ExecutionRecord` schemas)
- `@[backend_v2/models/domain/source_verification.py#L1-L79]` (`SourceClaimDTO`, `VerifiedSourceDTO`, `SourceVerificationResultDTO`)
- `@[backend_v2/models/dtos/engine.py#L41-L63]` (`MatrixEvaluationContext` DTO)
- `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L10-L140]` (`PromptCompilerAdapter`)
- `@[backend_v2/core/hook_registry.py#L1-L216]` (`HookRegistry`, `HookState`, `HookDependencies`, `HookResult`)
- `@[backend_v2/services/mcp/tavily_search_client.py#L1-L333]` (`tavily_search`, `batch_tavily_search`)
- `@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L219]` (`TDAEngine`)
- `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L25-L220]` (`SynthesisEngine`)

---

## 3. Technical Debt Itemization & Pre-Implementation Remediation

Specifically and exhaustively, the following 18 technical debt items and pre-flight architectural violations are identified for remediation across the execution phases:
1. **Stale Mock Patch in `test_llm_cost_tracking.py`**: Line 60 contains `@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")`. `tda_engine` does not import `get_settings`, causing immediate `AttributeError` during test collection.
2. **Raw JSON in System Prompt**: `MatrixSensorPromptBuilder.build_caching_prefix` calls `matrix_context.theory_grounding.model_dump_json()`, injecting unformatted JSON strings into static LLM system directives.
3. **DAG Executor Concurrency Race Condition (`mcp_tool_audit`)**: `dag_executor.py` lacks atomic merging for `mcp_tool_audit` on `FrozenContext`. Concurrent steps in `TaskGroup` overwrite each other's traces during non-synchronized `model_copy`.
4. **Strategy In-Place Mutation Race Condition (`generated_schemas`)**: `llm.py` line 575 mutates `frozen_ctx.generated_schemas[step.id] = ...` directly across concurrent `asyncio.TaskGroup` tasks. During concurrent execution, active commits (`_safe_commit()`) serializing `exec_record` encounter `RuntimeError: dictionary changed size during iteration`.
5. **Silent Exception Swallowing in `llm.py`**: Lines 516-517 and 539-540 contain silent `except Exception: pass` duct-tapes on execution record retrieval and source document context serialization.
6. **Banned `getattr`/`hasattr` Duck-Typing in `llm.py`**: Lines 505/546 use `getattr(step, "input_mappings", None)` and lines 553/560 use `getattr(step, "mcp_tools", None)` / `hasattr(tool, "function")`.
7. **Banned Magic Defaults in `llm.py`**: Lines 573 and 644 use `getattr(step, "expected_sdui_type", "grid")`.
8. **Raw String Comparison in `llm.py`**: Lines 361 and 393 use raw string comparison `b.category_id == "matrix"` instead of canonical `PromptBlockCategory.MATRIX`.
9. **Parameter Bloat & Missing `StrategyDependencies`**: `base.py`, `logic.py`, `llm.py`, and `dag_executor.py` copy-paste 10 individual repository and compiler parameters across constructors rather than using a typed container.
10. **Missing `PromptEngine`**: No dedicated execution engine exists for structured non-matrix prompt steps, leaving `step_input_processing` steps without an isolated engine execution path.
11. **Full Table Scans on Prompt Blocks**: `LLMNodeStrategy.execute()` calls `await self.prompt_block_repo.get_all_prompt_blocks()`, performing a full database scan on every single LLM step.
12. **Unsynchronized Trace Event Appends**: Line 694 in `dag_executor.py` appends to `exec_record.execution_trace` inside the for-loop at L693-L703 outside `_update_lock`.
13. **Procedural String Routing Anti-Pattern in `NodeExecutor`**: `dag_executor.py` lines 237-243 use procedural raw string branching `if step_def.type == "logic": ...` instead of declarative Enum lookup in a static registry, violating `@[ki_polymorphic_rule_routing.md]`.
14. **Missing Canonical `StepType` Enum**: `backend_v2/models/enums.py` lacks `StepType(StrEnum)` and `Step.type` in `v2_core.py` is typed with loose `Literal["llm", "logic"]`.
15. **Ghost Executions on Empty/Whitespace Inputs**: `source_verification_hook.py` does loose `isinstance(val, str)` iteration and returns `state_delta={}` on empty input, dropping the `verified_sources` key.
16. **Hardcoded Mock LLM Configuration in Production Path**: `SourceVerificationService._ensure_initialized()` constructs a hardcoded `LLMProviderConfig(api_key="mock", model_name="gemini/gemini-2.5-flash")` violating the Model Registry and crashing in live environments.
17. **Missing Hook Registration & Export**: `source_verification_hook.py` lacks `@hook_registry.register("source_verification")` and is omitted from `backend_v2/hooks/__init__.py`.
18. **XML Injection Vulnerability & In-Method System Prompts**: `SourceVerificationService` interpolates unescaped text into `<source_data>` and `<claim>` blocks without `html.escape()`, and constructs system directives dynamically inside methods rather than using static module constants.
19. **Dangling References in PromptBlock Batch Resolution**: SQL/NoSQL `IN` queries in `PromptBlockRepository` return partial lists when prompt block IDs are missing or deleted, silently corrupting downstream engine dispatch (`is_matrix_step`) and prompt compilation.
20. **Testing Drift with Raw Dictionaries**: Test fixtures across `test_dag_executor.py`, `test_llm.py`, `test_logic.py`, and `test_llm_cost_tracking.py` use legacy raw dictionaries for repository mock return values rather than typed Pydantic V2 models (`Step`, `PromptBlock`, `Workflow`, `OutputProfile`).

---

## 4. Architectural Impact & Compliance Matrix

### 4.1 Deprecations & Sunset List (`What We Will REMOVE`)
| Deprecated Symbol / Pattern | Location | Replacement / Disposition |
| :--- | :--- | :--- |
| `EPISTEMIC ANCHOR:` prompt tails | `@[backend_v2/seed/seed_data.json]` | **PURGED**. Retained exclusively in structured `theory_grounding` field. |
| Raw `source_url` in LLM prompts | `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]` | **OMITTED** from LLM prompt payload; retained in DTOs for UI/PDF rendering. |
| 10-argument constructors in strategies | `@[backend_v2/services/orchestrator/strategies/base.py]`, `@[backend_v2/services/orchestrator/strategies/llm.py]`, `@[backend_v2/services/orchestrator/strategies/logic.py]` | Replaced by `@dataclass(frozen=True) class StrategyDependencies`. |
| `get_all_prompt_blocks()` table scan in strategy | `@[backend_v2/services/orchestrator/strategies/llm.py]` | Replaced by `StrategyContext.prompt_blocks` single-fetch injection from `NodeExecutor`. |
| Procedural `if step_def.type == "logic"` branching | `@[backend_v2/services/orchestrator/dag_executor.py]` | Replaced by declarative `NodeStrategyFactory.create_strategy` and `NODE_STRATEGY_REGISTRY[step_def.type]`. |
| In-place `frozen_ctx.generated_schemas` mutation | `@[backend_v2/services/orchestrator/strategies/llm.py]` | Replaced by schema propagation via `TraceEvent.metadata["generated_schema"]` and atomic merge under `_update_lock`. |
| Unsynchronized `mcp_tool_audit` updates | `@[backend_v2/services/orchestrator/dag_executor.py]` | Wrapped inside `async with _update_lock:` with atomic deduplication. |
| Unsynchronized trace event appends | `@[backend_v2/services/orchestrator/dag_executor.py#L693-L703]` | Moved inside `async with _update_lock:`. |
| Unregistered Source Verification Hook | `@[backend_v2/hooks/source_verification_hook.py]` | Registered via `@hook_registry.register("source_verification")` and exported in `hooks/__init__.py`. |
| Hardcoded mock LLM in production path | `@[backend_v2/services/source_verification_service.py]` | Replaced with `await LLMClient.from_strategy("fast", repository=self.system_repo)`. |
| Stale `@patch("...tda_engine.get_settings")` | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]` | **REMOVED**; updated to mock settings SSOT directly. |
| Raw dictionary repository mocks | Test suites (`test_dag_executor.py`, `test_llm.py`, `test_logic.py`, `test_llm_cost_tracking.py`) | Migrated to strictly typed Pydantic V2 model instances (`Step`, `PromptBlock`, `Workflow`, `OutputProfile`). |

### 4.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **Qualitative Coaching Philosophy (`prompt_preservation_mandate`)**: Prompt texts in `@[backend_v2/seed/seed_data.json]` (specifically `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections) are strictly preserved. Only duplicate `EPISTEMIC ANCHOR:` tails are pruned.
2. **Deterministic UI/PDF Provenance**: `PromptBlock.theory_grounding` retains full metadata (`theoretical_framework`, `academic_citation`, `grounding_type`, `source_url`) for Server-Driven UI (SDUI) and PDF report generation.
3. **Pydantic V2 Strictness (`strict_pydantic_v2_rust`)**: All DTOs and models enforce `ConfigDict(strict=True, extra='forbid')`. `@property` methods on DTOs are strictly prohibited.
4. **Python 3.14 Concurrency (`python_314_concurrency_strictness`)**: All parallel executions utilize `asyncio.TaskGroup` with non-blocking concurrency limiters and `contextlib.nullcontext` wrapping.
5. **Executor Taxonomy & Decoupling Invariant (`DAGExecutor` vs `NodeExecutor` vs `EnrichedDagExecutor`)**:
   - `DAGExecutor` (`@[backend_v2/services/orchestrator/dag_executor.py]`): The workflow macro-orchestrator executing the top-level `StepRule` DAG pipeline. It instantiates `NodeExecutor(deps=self.deps)`.
   - `NodeExecutor` (`@[backend_v2/services/orchestrator/dag_executor.py]`): The step-level dispatcher executing a single `StepRule` via `NodeStrategyFactory` and `StrategyDependencies`.
   - `EnrichedDagExecutor` (`@[backend_v2/services/orchestrator/enriched_dag_executor.py]`): Downstream leaf atom-graph evaluator inside `TDAEngine` evaluating `LinkedAtomGraph` cognitive atom waves. It is instantiated solely by `TDAEngine(llm_executor, client)` and is completely decoupled from `StrategyDependencies` refactoring.

### 4.3 Producer-Consumer Integration Architecture
```
┌──────────────────────────────────────────────────────────────────────────┐
│                             PRODUCER-CONSUMER FLOW                      │
└──────────────────────────────────────────────────────────────────────────┘

 [PromptBlockRepositoryImpl] (get_prompt_blocks_by_ids)
          │  (Returns list[dict[str, Any]] with strict set parity check)
          ▼
   [NodeExecutor] (dag_executor.py)
          ├─► Hydrates: PromptBlockAdapter.validate_python(b, strict=False)
          ├─► Resolves Engine: _resolve_execution_engine(step_def, loaded_blocks)
          │       ├─► step.model_strategy == "synthesis" ──► SynthesisEngine
          │       ├─► criteria has PromptBlockCategory.MATRIX ──► TDAEngine
          │       └─► non-matrix structured step ──► PromptEngine
          ├─► Resolves Strategy: NodeStrategyFactory.create_strategy(step.type, deps, engine)
          └─► Injects: StrategyContext(..., prompt_blocks=loaded_blocks)
                   │
                   ▼
          [LLMNodeStrategy.execute()] (llm.py)
                   ├─► Consumes: context.prompt_blocks (0 redundant DB queries)
                   ├─► Compiles: dynamic schema & 4-layer cacheable envelope
                   ├─► Emits: TraceEvent.metadata["generated_schema"]
                   └─► Delegates: engine.execute(request) ──► PromptEngine / TDAEngine / SynthesisEngine
                            │
                            ▼
          [DAGExecutor.run_step_wrapper] (dag_executor.py)
                   └─► async with _update_lock:
                            ├─► Append TraceEvents to exec_record.execution_trace
                            ├─► Deduplicate & Accumulate MCPAuditTrace ──► exec_record.frozen_context.mcp_tool_audit
                            ├─► Accumulate generated_schemas ──► exec_record.frozen_context.generated_schemas
                            └─► Immutable Reassignment: exec_record = exec_record.model_copy(...)
```

---

## 5. Phased Implementation Plan

### Phase 1: Pre-Implementation Technical Debt Cleanups & Seed Vault Sanitization

#### Step 1.1: Backup Seed Vault (`vault_mutation_protocol`)
Ensure directory `backend_v2/seed/backups/` exists and execute backup command:
`New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_theory_grounding_cleanup.json`

#### Step 1.2: Deterministic Seed Vault Sanitization across all 13 Matrix Blocks
Surgically sanitize the `ai_description` field across specifically and exhaustively all 13 matrices in `@[backend_v2/seed/seed_data.json]`:
1. `blk_440a5fef9331451b` (matrix_toulmin): Remove `EPISTEMIC ANCHOR:\nToulmin, S. E. (2003)...`
2. `blk_f921c7c0989b47e8` (matrix_bloom): Remove `EPISTEMIC ANCHOR:\nAnderson, L. W., & Krathwohl...`
3. `blk_109dab5b6b3f403a` (matrix_kahneman): Remove `EPISTEMIC ANCHOR:\nKahneman, D. (2011)...`
4. `blk_53f32679aa514fcb` (matrix_goodhart): Remove `EPISTEMIC ANCHOR:\nStumborg, M. F., et al...`
5. `blk_fb15f8dcf23f4865` (matrix_archivist): Remove `EPISTEMIC ANCHOR:\nARMA International...`
6. `blk_c5804a9143c34cb1` (matrix_causal_analyst): Remove `EPISTEMIC ANCHOR:\nPearl, J. 'The Book of Why...`
7. `blk_b476f89fb732448c` (matrix_falsifier): Remove `EPISTEMIC ANCHOR:\nKarl Popper's Theory of Falsification...`
8. `blk_ff72c2d79edb4ebf` (matrix_judge): Remove `EPISTEMIC ANCHOR:\nW. Edwards Deming...`
9. `blk_6b8c766185294f7e` (matrix_xai_reporter): Remove `EPISTEMIC ANCHOR:\nDARPA XAI Program (2017)...`
10. `blk_80732a33fe1947ee` (matrix_taskguard): Remove `EPISTEMIC ANCHOR:\nAnchored in the OWASP Top 10...`
11. `blk_c3bc5f3eb8e74110` (matrix_causal_abductive): Remove `EPISTEMIC ANCHOR:\nAnchored in Judea Pearl's 'The Book of Why'...`
12. `blk_f6e286f050c94d60` (matrix_taskxai_clarity): Remove `EPISTEMIC ANCHOR:\nAnchored in Zachary C. Lipton's 'The Mythos of Model Interpretability'...`
13. `blk_22e3598e06414409` (matrix_epistemic_humility): Remove `EPISTEMIC ANCHOR:\nGrounded in Kahneman's Dual Process Theory...`

Preserve all `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections intact per `prompt_preservation_mandate`.

#### Step 1.3: Re-seed Database
Verify JSON syntax and re-seed the local test database:
Run: `uv run python backend_v2/seed/run_seed.py local`

#### Step 1.4: Scoped Technical Debt Cleanup in `test_llm_cost_tracking.py` & `llm.py`
1. In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148]`: Remove outdated mock `@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")` at line 60.
2. In `@[backend_v2/services/orchestrator/strategies/llm.py#L361-L644]`:
   - Replace raw string comparison `b.category_id == "matrix"` with `b.category_id == PromptBlockCategory.MATRIX` and `any(b.category_id == PromptBlockCategory.MATRIX for b in criteria_blocks_models)`.
   - Replace silent `except Exception: pass` blocks (L516-517, L539-540) with explicit RFC 7807 `logger.warning` structured logging on `exec_repo.get_execution()` and `SourceDocumentContext` serialization.
   - Eliminate `getattr(step, "input_mappings", None)` duck-typing (L505, L546). Resolve allowed dynamic keys directly from `input_mappings` argument combined with `context.expected_inputs`.
   - Eliminate `getattr(step, "mcp_tools", None)` and `hasattr(tool, "function")` (L553-L560). Iterate directly over `step.allowed_mcp_tools` (`list[str]`) from the `Step` model.
   - Eliminate `getattr(step, "expected_sdui_type", "grid")` (L573, L644).

---

### Phase 2: DTOs, Repository Interfaces, StrategyDependencies Container & Polymorphic Strategy Registry

#### Step 2.1: Canonical `StepType` Enum & Schema Update
1. In `@[backend_v2/models/enums.py]`, declare canonical `StepType(StrEnum)` and export in `__all__`:
   ```python
   class StepType(StrEnum):
       """Execution taxonomy for workflow steps."""
       LLM = "llm"
       LOGIC = "logic"
   ```
2. In `@[backend_v2/models/v2_core.py#L540-L585]`, update `Step.type`:
   ```python
   type: StepType = Field(default=StepType.LLM, description="Step execution type (llm or native logic)")
   ```

#### Step 2.2: Fail-Fast PromptBlock Batch Resolution in Repository
1. In `@[backend_v2/database/interfaces.py#L677-L740]`: Add `get_prompt_blocks_by_ids` to `IPromptBlockRepository`:
   ```python
   async def get_prompt_blocks_by_ids(
       self,
       block_ids: list[str],
       strict: bool = True,
   ) -> list[dict[str, Any]]: ...
   ```
2. In `@[backend_v2/database/repositories/components/prompt_block.py#L50-L115]`: Implement `get_prompt_blocks_by_ids` with strict mathematical set parity:
   ```python
   async def get_prompt_blocks_by_ids(
       self,
       block_ids: list[str],
       strict: bool = True,
   ) -> list[dict[str, Any]]:
       if not block_ids:
           return []

       unique_requested: set[str] = set(block_ids)
       filters = [Filter("id", "in", list(unique_requested))]
       results = await self.driver.query("prompt_blocks", filters=filters)

       if strict:
           found_ids: set[str] = {r["id"] for r in results if isinstance(r, dict) and "id" in r}
           missing_ids = unique_requested - found_ids
           if missing_ids:
               sorted_missing = sorted(list(missing_ids))
               msg = f"PromptBlock(s) not found for IDs: {sorted_missing}"
               logger.error(
                   "[PromptBlockRepository] %s: %s",
                   ErrorCodes.RESOURCE_NOT_FOUND.name,
                   msg,
                   extra={
                       "error_code": ErrorCodes.RESOURCE_NOT_FOUND.name,
                       "missing_ids": sorted_missing,
                       "requested_ids": sorted(list(unique_requested)),
                   },
               )
               raise AppException(
                   message=msg,
                   status_code=404,
                   details={
                       "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                       "missing_ids": sorted_missing,
                   },
               )

       return results
   ```

#### Step 2.3: Declare `StrategyDependencies` Container & Context Injection
1. In `@[backend_v2/services/orchestrator/strategies/base.py#L50-L105]`:
   - Add `prompt_blocks: list[PromptBlock] = Field(default_factory=list)` to `StrategyContext`.
   - Define `@dataclass(frozen=True) class StrategyDependencies`:
     ```python
     @dataclass(frozen=True)
     class StrategyDependencies:
         """Immutable container encapsulating all repositories and compiler dependencies for strategies."""
         exec_repo: IExecutionRepository
         workflow_repo: IWorkflowRepository
         comp_repo: IComponentRepository
         prompt_block_repo: IPromptBlockRepository
         output_profile_repo: IOutputProfileRepository
         identity_repo: IIdentityRepository
         audit_repo: IAuditRepository
         system_repo: ISystemRepository
         prompt_compiler: Any
         arq_pool: Any | None = None
     ```
   - Update `NodeStrategy.__init__(self, deps: StrategyDependencies)` to unpack `self.deps = deps` and assign attributes cleanly.
2. In `@[backend_v2/services/orchestrator/strategies/logic.py#L19-L50]`: Update constructor to accept `deps: StrategyDependencies`.
3. In `@[backend_v2/services/orchestrator/strategies/llm.py#L56-L110]`: Update constructor to accept `deps: StrategyDependencies` and `engine: ExecutionEngine`.

#### Step 2.4: Extract `PromptEngine` for Structured Tasks
Create [NEW] `@[backend_v2/services/orchestrator/engines/prompt_engine.py]` implementing `ExecutionEngine`:
1. Signal `running_event.set()` if `request.running_event` is provided.
2. Enforce Fail-Fast validation:
   - If `request.compiled_schema is None`: raise `AppException(status_code=500, message="PromptEngine requires a valid 'compiled_schema'.", details={"error_code": "PROMPT_ENGINE_ERROR"})`.
   - If `request.hydrated_messages is None` or empty: raise `AppException(status_code=500, message="PromptEngine requires non-empty 'hydrated_messages'.", details={"error_code": "PROMPT_ENGINE_ERROR"})`.
3. Wrap execution inside `async with request.semaphore:` (or `nullcontext` if None) and call `await self._llm_executor.execute_structured_task(client=request.bound_client, messages=request.hydrated_messages, response_model=request.compiled_schema)`.
4. Extract validated Pydantic model dump: `validated_output = validated_dto.model_dump(mode="json")`.
5. Return `EngineExecutionResult(results=[], hydrated_references={}, synthesis_output=validated_output, trace_events=[], usage=usage)`. Token metadata injection (`_step_metadata.token_usage`) is handled centrally by `LLMNodeStrategy.execute()`.
6. Export `PromptEngine` in `@[backend_v2/services/orchestrator/engines/__init__.py]`.

#### Step 2.5: Implement Polymorphic Strategy Factory & Static Registry
Create [NEW] `@[backend_v2/services/orchestrator/strategies/registry.py]`:
```python
from collections.abc import Callable
from typing import Protocol

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import StepType
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy


class StrategyBuilder(Protocol):
    """Protocol for building node strategy instances."""
    def __call__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy: ...


def _build_logic_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    return LogicNodeStrategy(deps=deps)


def _build_llm_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    if engine is None:
        raise AppException(
            message="LLMNodeStrategy requires a non-null ExecutionEngine instance.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
        )
    return LLMNodeStrategy(deps=deps, engine=engine)


NODE_STRATEGY_REGISTRY: dict[StepType, StrategyBuilder] = {
    StepType.LOGIC: _build_logic_strategy,
    StepType.LLM: _build_llm_strategy,
}


class NodeStrategyFactory:
    """Factory resolving node strategies via strict static registry mapping."""

    @staticmethod
    def create_strategy(
        step_type: StepType,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy:
        builder = NODE_STRATEGY_REGISTRY.get(step_type)
        if builder is None:
            raise AppException(
                message=f"Unsupported step type '{step_type}'. Must be registered in NODE_STRATEGY_REGISTRY.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )
        return builder(deps=deps, engine=engine)
```

---

### Phase 3: Engine Architecture, NodeExecutor Decomposition, Single-Fetch DI & DAG Concurrency Hardening

#### Step 3.1: Decompose `NodeExecutor` & Single-Fetch DI in `dag_executor.py`
In `@[backend_v2/services/orchestrator/dag_executor.py#L115-L375]`:
1. Update `NodeExecutor.__init__(self, deps: StrategyDependencies) -> None: self.deps = deps`.
2. Update `DAGExecutor.__init__` to instantiate `self.deps = StrategyDependencies(...)` and pass `self.node_executor = NodeExecutor(deps=self.deps)`.
3. Add helper method `def _resolve_execution_engine(self, step_def: Step, prompt_blocks: list[PromptBlock]) -> ExecutionEngine`:
   - If `step_def.model_strategy == "synthesis"` (or step contains synthesis prompt blocks): return `SynthesisEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
   - Filter criteria blocks from already-injected `prompt_blocks`: `criteria_blocks = [b for b in prompt_blocks if b.id in step_def.criteria_block_ids]`.
   - Check block categories using strict enum comparisons: `is_matrix_step = any(b.category_id == PromptBlockCategory.MATRIX or isinstance(b, MatrixPromptBlock) for b in criteria_blocks)`.
   - If `is_matrix_step`: return `TDAEngine(self.deps.prompt_compiler)`.
   - Else (non-matrix structured prompt step): return `PromptEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
4. In `NodeExecutor.execute()`:
   - Collect all required prompt block IDs: `all_required_block_ids = list(dict.fromkeys([b_id for b_id in (step_def.role_block_id, step_def.extraction_protocol_block_id, step_def.execution_persona_block_id, *step_def.criteria_block_ids) if b_id]))`.
   - Fetch with strict set parity: `raw_blocks = await self.deps.prompt_block_repo.get_prompt_blocks_by_ids(all_required_block_ids, strict=True)`.
   - Hydrate in service layer: `loaded_prompt_blocks = [PromptBlockAdapter.validate_python(b, strict=False) for b in raw_blocks]`.
   - Resolve engine: `engine = self._resolve_execution_engine(step_def, loaded_prompt_blocks) if step_def.type == StepType.LLM else None`.
   - Create strategy via factory: `strategy_impl = NodeStrategyFactory.create_strategy(step_type=step_def.type, deps=dataclasses.replace(self.deps, arq_pool=arq_pool) if arq_pool else self.deps, engine=engine)`.
   - Inject `loaded_prompt_blocks` into `StrategyContext(..., prompt_blocks=loaded_prompt_blocks)`.
   - Execute quota and strategy: `await strategy_impl.assert_quota(org_id=org_id); return await strategy_impl.execute(...)`.

#### Step 3.2: Atomic Deduplicating State Accumulation under `_update_lock` in `DAGExecutor`
In `@[backend_v2/services/orchestrator/dag_executor.py#L690-L730]`:
Move unsynchronized trace append for-loop at L693-L703 inside `_update_lock`, and implement atomic deduplicating accumulation of both `MCPAuditTrace` into `exec_record.frozen_context.mcp_tool_audit` AND `generated_schemas` into `exec_record.frozen_context.generated_schemas` under `_update_lock`:
```python
has_error_evt = any(isinstance(evt, ErrorTraceEvent) for evt in events)
async with _update_lock:
    step_mcp_traces: list[MCPAuditTrace] = []
    new_cv = dict(exec_record.context_variables)
    new_schemas = dict(exec_record.frozen_context.generated_schemas)
    has_cv_updates = False
    has_schema_updates = False

    for evt in events:
        exec_record.execution_trace.append(evt)
        projector.apply_delta(evt)
        if (
            evt.event_type == "decision"
            and evt.metadata
            and "is_context_update" in evt.metadata
            and evt.metadata["is_context_update"]
        ):
            new_cv.update(evt.content)
            has_cv_updates = True

        if evt.metadata and "generated_schema" in evt.metadata:
            new_schemas[step_id] = evt.metadata["generated_schema"]
            has_schema_updates = True

        match evt:
            case TraceEvent() if evt.mcp_audit_traces:
                step_mcp_traces.extend(evt.mcp_audit_traces)

    updates: dict[str, Any] = {}
    if has_cv_updates:
        updates["context_variables"] = new_cv

    frozen_updates: dict[str, Any] = {}
    if step_mcp_traces:
        current_traces: list[MCPAuditTrace] = list(exec_record.frozen_context.mcp_tool_audit)
        seen_ids: set[str] = {t.id for t in current_traces if t.id}
        new_unique_traces: list[MCPAuditTrace] = [
            t for t in step_mcp_traces if t.id is None or t.id not in seen_ids
        ]
        frozen_updates["mcp_tool_audit"] = current_traces + new_unique_traces

    if has_schema_updates:
        frozen_updates["generated_schemas"] = new_schemas

    if frozen_updates:
        updates["frozen_context"] = exec_record.frozen_context.model_copy(update=frozen_updates)

    step_status = ExecutionStatus.FAILED if has_error_evt else ExecutionStatus.PASSED
    new_state = exec_record.step_states[step_id].model_copy(update={"status": step_status})
    updates["step_states"] = {**exec_record.step_states, step_id: new_state}

    exec_record = exec_record.model_copy(update=updates)

if has_error_evt:
    err_msg = [evt.error_message for evt in events if isinstance(evt, ErrorTraceEvent)][0]
    msg = f"Step {step_id} emitted ErrorTraceEvent: {err_msg}"
    logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
    raise AppException(
        message=msg,
        status_code=500,
        details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
    )

await _safe_commit()
```

#### Step 3.3: Consume Injected Prompt Blocks & Schema Propagation in `LLMNodeStrategy`
In `@[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]`:
1. Eliminate duplicate DB fetch: Replace `all_prompt_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()` with direct consumption of injected prompt blocks:
   `block_map = {b.id: b for b in context.prompt_blocks if b.id}`.
2. Validate that all required step prompt blocks (`role_block_id`, `extraction_protocol_block_id`, `execution_persona_block_id`, `criteria_block_ids`) exist in `block_map`; raise Fail-Fast `ConfigurationError` / `AppException(VALIDATION_FAILED)` if any are missing.
3. Eliminate in-place `FrozenContext` mutation: Remove `frozen_ctx.generated_schemas[step.id] = global_schema.model_json_schema()`. Attach the compiled JSON schema to `TraceEvent.metadata["generated_schema"] = global_schema.model_json_schema()` to avoid in-place shared dictionary mutation across concurrent tasks; `DAGExecutor` will merge it atomically under `_update_lock`.
4. When preparing `EngineExecutionRequest`:
   - For `is_synthesis_step`: pass `compiled_schema=dynamic_schema`, `hydrated_messages=[static_msg]`, `system_prompt=""`.
   - For `is_matrix_step`: pass `compiled_schema=None`, `hydrated_messages=None`, `system_prompt=user_payload`, `shuffled_atoms=hydrated_shuffled_atoms`.
   - For non-matrix structured prompt step (`PromptEngine` target):
     - Compile static instructions from non-matrix prompt blocks via `self.compiler.compile_static_instructions(criteria_blocks, target_locale)`.
     - Assemble 4-layer cacheable envelope: `hydrated_messages=[{"role": "system", "content": static_instructions}, {"role": "user", "content": user_payload}]`.
     - Pass `compiled_schema=global_schema`, `hydrated_messages=hydrated_messages`, `system_prompt=user_payload`.
5. When processing `engine_result`:
   - If `engine_result.synthesis_output is not None`: assign `final_dict = engine_result.synthesis_output`.
   - Else: assign `final_dict = {"results": [r.model_dump(mode="json") for r in engine_result.results], "hydrated_references": {k: v.model_dump(mode="json") for k, v in engine_result.hydrated_references.items()}}`.

#### Step 3.4: Format Pure `<theory_context>` in `MatrixSensorPromptBuilder`
In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L88]`:
Refactor theory_grounding injection in `MatrixSensorPromptBuilder.build_caching_prefix`:
Replace `ai_desc=matrix_context.theory_grounding.model_dump_json()` with pure citation XML formatting (excluding URL token bloat and preventing unclosed XML tags):
```python
if matrix_context and matrix_context.theory_grounding and matrix_context.theory_grounding.citation_reference:
    citation = matrix_context.theory_grounding.citation_reference.strip()
    if citation:
        theory_desc = f"<theory_context>\n{citation}\n</theory_context>"
        blocks.append(
            MatrixSensorPromptBuilder._create_ephemeral_block(
                block_id="blk_3333333333333333",
                category_id=PromptBlockCategory.SYSTEM_RULE,
                ai_desc=theory_desc,
            )
        )
```

---

### Phase 4: Ghost Execution Elimination & Source Verification Hook Hardening

#### Step 4.1: Source Extraction Schema & Service Hardening
1. In `@[backend_v2/models/dtos/source_extraction_schema.py#L1-L25]`, declare `SourceVerificationInputsDTO`:
   ```python
   class SourceVerificationInputsDTO(V2CoreBase):
       """Strict inputs schema for source verification hook."""
       model_config = ConfigDict(strict=True, extra="forbid")

       prior_analysis: str | None = None
       text: str | None = None
       document: str | None = None
   ```
   **ARCHITECTURAL CONSTRAINT — NO @property ON DTOs**: Per `context_envelope_ssot_predicates`, `@property` methods are STRICTLY FORBIDDEN on API/Persistence DTOs in `models/dtos/`. Text consolidation logic MUST be computed as a local variable in `source_verification_hook.py` immediately after DTO parsing:
   ```python
   inputs = SourceVerificationInputsDTO.model_validate(state.inputs)
   text_parts = [p.strip() for p in (inputs.prior_analysis, inputs.text, inputs.document) if isinstance(p, str) and p.strip()]
   text_content = "\n\n".join(text_parts)
   ```
2. In `@[backend_v2/services/source_verification_service.py#L1-L257]`:
   - Add `system_repo: ISystemRepository | None = None` and `llm_task_executor: LLMTaskExecutor | None = None` parameters to `SourceVerificationService.__init__(self, system_repo: ISystemRepository | None = None, llm_task_executor: LLMTaskExecutor | None = None) -> None`.
   - Define `MIN_VERIFIABLE_TEXT_LENGTH: int = 15` as an explicit SSOT module-level constant.
   - Define static module-level system directives `_EXTRACTION_SYSTEM_PROMPT` and `_VERIFICATION_SYSTEM_PROMPT` to enable 100% Google Gemini Context Caching.
   - Replace hardcoded `LLMProviderConfig(api_key="mock", ...)` with `await LLMClient.from_strategy("fast", repository=self.system_repo)` and `LLMTaskExecutor(PromptCompiler(), client=self.llm_client)` in `_ensure_initialized()`.
   - In `_extract_source_claims` and `_verify_single_claim`, wrap untrusted content inside `<source_data>` and `<claim>` with `html.escape()` to eliminate XML injection vulnerabilities.
   - Enforce minimum character threshold `len(text.strip()) < MIN_VERIFIABLE_TEXT_LENGTH` in `run_full_verification` to short-circuit ghost executions before initializing the LLM client.

#### Step 4.2: Hook Defensive Guard & Registry Export
1. In `@[backend_v2/hooks/source_verification_hook.py#L1-L47]`:
   - Decorate hook with `@hook_registry.register(name="source_verification")`.
   - Parse inputs through `SourceVerificationInputsDTO.model_validate(state.inputs)`.
   - Compute consolidated text as a local variable.
   - If inputs are missing, empty, whitespace-only, or `len(text_content) < MIN_VERIFIABLE_TEXT_LENGTH`, return a fully initialized `SourceVerificationResultDTO` with zero claims in `state_delta={"verified_sources": empty_result.model_dump(mode="json")}` to preserve state schema parity.
   - Pass `system_repo=deps.system_repo` to `SourceVerificationService(system_repo=deps.system_repo)`.
   - Wrap errors in RFC 7807 `AppException` with `ErrorCodes.AGENT_EXECUTION_CRITICAL`.
2. In `@[backend_v2/hooks/__init__.py#L7-L42]`:
   - Import `source_verification_hook` and add `"source_verification_hook"` to `__all__`.

---

### Phase 5: AST Guardrails, Unit Test Suites, Mock Migrations & E2E Integration Gate

#### Step 5.1: Create AST Guardrail Suite (`test_ast_theory_grounding_guardrails.py`)
Create [NEW] `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]` locking all 8 architectural invariants:
1. `test_seed_matrices_have_no_epistemic_anchor_in_ai_description`: Parses `backend_v2/seed/seed_data.json` and asserts that 0 matrix blocks contain `"EPISTEMIC ANCHOR:"` in `ai_description`.
2. `test_seed_matrices_have_valid_theory_grounding`: Asserts that all 13 matrix blocks have non-null `theory_grounding` with non-empty `source_url` and `citation_reference`.
3. `test_matrix_sensor_prompt_builder_ast_uses_pure_theory_citation`: Inspects the AST of `MatrixSensorPromptBuilder.build_caching_prefix` to verify that `<theory_context>` is constructed with pure `citation_reference` and `model_dump_json` is not called on `theory_grounding`.
4. `test_matrix_sensor_prompt_builder_ast_has_no_xml_string_slicing`: Inspects the AST of `MatrixSensorPromptBuilder` to verify that no raw string slicing `[:` is performed on assembled XML prompt messages.
5. `test_source_verification_hook_registered_and_safe`: Inspects AST of `source_verification_hook.py` to verify `@hook_registry.register` is attached and no hardcoded mock API keys exist.
6. `test_node_strategy_registry_ast_has_no_procedural_string_routing`: Inspects AST of `dag_executor.py` and `registry.py` to assert that no raw string comparisons `step_def.type == "logic"` exist and routing strictly utilizes `StepType` enum keys in `NODE_STRATEGY_REGISTRY`.
7. `test_llm_strategy_ast_has_no_frozen_ctx_generated_schemas_mutation`: Inspects AST of `backend_v2/services/orchestrator/strategies/llm.py` to assert that zero in-place mutations of `frozen_ctx.generated_schemas` exist.
8. `test_prompt_block_repo_ast_strict_missing_parity`: Inspects AST of `backend_v2/database/repositories/components/prompt_block.py` to verify that `get_prompt_blocks_by_ids` performs mathematical set difference validation (`unique_requested - found_ids`) and raises `AppException(RESOURCE_NOT_FOUND)` when `missing_ids` is non-empty.

#### Step 5.2: Unit Test Suites & Typed Mock Migration
1. In [NEW] `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`: Positive structured task verification, Fail-Fast missing schema, missing messages, empty messages, exception re-raising, semaphore acquisition and `running_event.set()`.
2. In [NEW] `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]`: Logic strategy resolution, LLM strategy resolution with engine, LLM missing engine Fail-Fast (`CONFIGURATION_ERROR`), unregistered step type Fail-Fast (`CONFIGURATION_ERROR`).
3. In [NEW] `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`: Parallel steps `MCPAuditTrace` accumulation, schema accumulation, trace ID deduplication, and immutable `_safe_commit()`.
4. In `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`: Batch query success, empty input fast-path, duplicate ID deduplication, strict single missing Fail-Fast, strict all missing Fail-Fast, and non-strict partial return.
5. In `@[backend_v2/tests/unit/services/test_source_verification_service.py]` and [NEW] `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`: Empty prior analysis zero-claims envelope, whitespace prior analysis, sub-threshold text length, non-string payload safety, XML injection escaping, and hook registry discovery.
6. Across `test_dag_executor.py`, `test_llm.py`, `test_logic.py`, and `test_llm_cost_tracking.py`: Migrate all `AsyncMock` return values from raw dictionaries to typed Pydantic V2 models (`Step`, `PromptBlock`, `Workflow`, `OutputProfile`), and update fixtures to pass `StrategyDependencies`.

---

## 6. ISTQB Equivalence Partitions & Boundary Scenarios Matrix

| Scenario ID | Test Name | Input State | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **TC-TG-01** (Happy Path: Pure Citation) | `test_build_caching_prefix_with_context` | `TheoryGrounding(source_url="https://arma.org", citation_reference="ARMA Principles")` | Static prompt contains `<theory_context>\nARMA Principles\n</theory_context>` (no raw URL in prompt) |
| **TC-TG-02** (Boundary: Null Citation) | `test_build_caching_prefix_theory_grounding_none_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference=None)` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-03** (Boundary: Empty Citation) | `test_build_caching_prefix_theory_grounding_empty_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference="")` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-04** (Boundary: Whitespace-only) | `test_build_caching_prefix_theory_grounding_whitespace_only` | `TheoryGrounding(source_url="https://arma.org", citation_reference="   \n\t")` | Ephemeral block is not appended, avoiding whitespace-only tags |
| **TC-TG-05** (Boundary: URL Exclusion) | `test_build_caching_prefix_theory_grounding_omits_raw_urls` | `TheoryGrounding(source_url="https://secret-domain.org/doc", citation_reference="Valid Citation")` | Static prompt does NOT contain `"https://secret-domain.org"` (zero token bloat / URL leakage) |
| **TC-TG-06** (AST Guardrail: Epistemic Anchor) | `test_seed_matrices_have_no_epistemic_anchor_in_ai_description` | `seed_data.json` | 0 occurrences of `EPISTEMIC ANCHOR:` across all 13 matrices |
| **TC-TG-07** (AST Guardrail: Valid DTOs & No Slicing) | `test_matrix_sensor_prompt_builder_ast_has_no_xml_string_slicing` | `matrix_sensor_prompt_builder.py` | AST confirms no string slicing `[:` on XML strings and no `model_dump_json()` on `theory_grounding` |
| **TC-PE-01** (PromptEngine: Success Structured Task) | `test_prompt_engine_success_structured_task` | Valid `compiled_schema` and `hydrated_messages` | Validated Pydantic dictionary output returned in `EngineExecutionResult.synthesis_output` |
| **TC-PE-02** (PromptEngine Fail-Fast: Missing Schema) | `test_prompt_engine_fail_fast_missing_schema` | `compiled_schema=None` | Raises `AppException(PROMPT_ENGINE_ERROR)` immediately |
| **TC-PE-03** (PromptEngine Fail-Fast: Empty Messages) | `test_prompt_engine_fail_fast_empty_messages` | `hydrated_messages=[]` | Raises `AppException(PROMPT_ENGINE_ERROR)` immediately |
| **TC-MCP-01** (Concurrency: Multi-step Accumulation) | `test_dag_executor_concurrent_steps_accumulate_mcp_traces` | 4 concurrent steps generating 2 `MCPAuditTrace` each | All 8 unique traces preserved in `exec_record.frozen_context.mcp_tool_audit` |
| **TC-MCP-02** (Boundary: Trace Deduplication) | `test_dag_executor_mcp_trace_deduplication` | Concurrent steps emitting duplicate `MCPAuditTrace(id="mcp_001")` | `mcp_tool_audit` contains exactly 1 instance of `mcp_001` |
| **TC-MCP-03** (Immutability: State Persistence) | `test_dag_executor_frozen_context_immutability_and_commit` | Parallel steps mutating state | `_safe_commit()` commits complete merged `FrozenContext` to repository without corruption |
| **TC-FC-01** (Concurrency: Schema Accumulation) | `test_dag_executor_concurrent_steps_accumulate_generated_schemas` | 4 concurrent steps generating dynamic JSON schemas | All 4 step schemas safely accumulated into `exec_record.frozen_context.generated_schemas` under `_update_lock` |
| **TC-AST-08** (AST Guardrail: FrozenContext Schema Immutability) | `test_llm_strategy_ast_has_no_frozen_ctx_generated_schemas_mutation` | `llm.py` | AST confirms zero in-place mutations on `frozen_ctx.generated_schemas` |
| **TC-REG-01** (Registry: Logic Node Resolution) | `test_node_strategy_registry_resolves_logic_strategy` | `StepType.LOGIC` | `NODE_STRATEGY_REGISTRY` returns `LogicNodeStrategy` instance |
| **TC-REG-02** (Registry: LLM Node Resolution) | `test_node_strategy_registry_resolves_llm_strategy` | `StepType.LLM` + non-null `ExecutionEngine` | `NODE_STRATEGY_REGISTRY` returns `LLMNodeStrategy` instance |
| **TC-REG-03** (Boundary: LLM Missing Engine) | `test_node_strategy_registry_llm_without_engine_raises_app_exception` | `StepType.LLM` + `engine=None` | Raises `AppException(ErrorCodes.CONFIGURATION_ERROR)` at factory boundary |
| **TC-REG-04** (Boundary: Unregistered StepType) | `test_node_strategy_registry_unregistered_type_raises_app_exception` | Unregistered / invalid StepType | Raises `AppException(ErrorCodes.CONFIGURATION_ERROR)` immediately |
| **TC-PB-01** (Repo: Batch Resolution Success) | `test_get_prompt_blocks_by_ids_success` | `["blk_1", "blk_2"]` in DB | Returns `list[dict]` containing all requested block records |
| **TC-PB-02** (Boundary: Empty Input List) | `test_get_prompt_blocks_by_ids_empty_list` | `[]` | Fast-paths immediately to `[]` with 0 database queries |
| **TC-PB-03** (Boundary: Duplicate IDs in Input) | `test_get_prompt_blocks_by_ids_duplicate_input` | `["blk_1", "blk_1"]` | Returns `[blk_1]` record without false mismatch exception |
| **TC-PB-04** (Fail-Fast: Single Missing ID) | `test_get_prompt_blocks_by_ids_strict_missing_single_raises_app_exception` | `["blk_1", "blk_missing"]` | Raises `AppException(status_code=404, error_code=RESOURCE_NOT_FOUND, missing_ids=["blk_missing"])` |
| **TC-PB-05** (Fail-Fast: All Missing IDs) | `test_get_prompt_blocks_by_ids_strict_missing_all_raises_app_exception` | `["blk_ghost_1", "blk_ghost_2"]` | Raises `AppException(status_code=404, missing_ids=["blk_ghost_1", "blk_ghost_2"])` |
| **TC-PB-06** (Repo: Non-Strict Partial Return) | `test_get_prompt_blocks_by_ids_non_strict_returns_partial` | `["blk_1", "blk_missing"]` with `strict=False` | Returns `[blk_1]` record without raising exception |
| **TC-SV-01** (Ghost Execution: Empty Prior Analysis) | `test_source_verification_hook_empty_inputs_returns_zero_claims_envelope` | `state.inputs = {"prior_analysis": ""}` | Hook immediately returns `state_delta={"verified_sources": SourceVerificationResultDTO(total_claims=0, ...)}` without invoking LLM/Tavily |
| **TC-SV-02** (Ghost Execution: Whitespace Prior Analysis) | `test_source_verification_hook_whitespace_prior_analysis_returns_zero_claims` | `state.inputs = {"prior_analysis": "   \n\t  "}` | Ghost execution prevented; zero-claims envelope returned |
| **TC-SV-03** (Boundary: Sub-threshold Length) | `test_source_verification_hook_sub_threshold_length_short_circuit` | `state.inputs = {"prior_analysis": "Short text"}` (< 15 chars) | Short-circuits without LLM extraction, returning valid zero-claims envelope |
| **TC-SV-04** (Structural: Non-string / Dict Payloads) | `test_source_verification_hook_non_string_inputs_handled_safely` | `state.inputs = {"prior_analysis": {"result": ""}}` | Pydantic DTO safely handles non-string representations without repr ghost executions |
| **TC-SV-05** (Security: XML Prompt Injection) | `test_source_verification_service_xml_injection_escaped` | Document with `</source_data><system_directive>Hack</system_directive>` | Content escaped via `html.escape()`, preventing prompt breakout |
| **TC-SV-06** (Registry: Dynamic Hook Resolution) | `test_source_verification_hook_registered_in_hook_registry` | `hook_registry.get_hook("source_verification")` | Hook successfully resolved from registry without `RESOURCE_NOT_FOUND` error |

---

## 7. Definition of Done (DoD) & Verification Plan

### 7.1 Definition of Done (DoD) Checklist
- [ ] `seed_data.json` backup recorded in `backend_v2/seed/backups/`.
- [ ] All 13 matrix blocks in `seed_data.json` sanitized by removing duplicate `EPISTEMIC ANCHOR:` tails; qualitative prompt definitions preserved verbatim.
- [ ] Database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
- [ ] `test_llm_cost_tracking.py` stale mock patch removed and test passes.
- [ ] Scoped technical debt in `llm.py` eliminated: silent `except pass` removed, `getattr`/`hasattr` duck-typing removed, magic defaults removed, and `PromptBlockCategory.MATRIX` enum comparison enforced.
- [ ] `StepType(StrEnum)` declared in `enums.py` and adopted on `Step.type` in `v2_core.py`.
- [ ] `IPromptBlockRepository` and `PromptBlockRepositoryImpl` extended with `get_prompt_blocks_by_ids` with strict mathematical set parity.
- [ ] `StrategyDependencies` container defined in `base.py` and adopted across `NodeStrategy`, `LogicNodeStrategy`, and `LLMNodeStrategy`.
- [ ] `PromptEngine` extracted in `prompt_engine.py`, exported in `engines/__init__.py`, and implementing `ExecutionEngine` protocol with Fail-Fast validations.
- [ ] Static `NODE_STRATEGY_REGISTRY` and `NodeStrategyFactory.create_strategy` implemented in `registry.py`.
- [ ] `NodeExecutor` decomposed into `_resolve_execution_engine` and `NodeStrategyFactory` dispatch; prompt blocks single-fetched and injected via `StrategyContext(..., prompt_blocks=...)`.
- [ ] Full-table scan `get_all_prompt_blocks()` completely eliminated from `NodeExecutor` and `LLMNodeStrategy`.
- [ ] `DAGExecutor.run_step_wrapper` executes all state mutations, trace appends, `mcp_tool_audit` merging, and `generated_schemas` merging inside `async with _update_lock:`.
- [ ] In-place mutation of `frozen_ctx.generated_schemas` in `LLMNodeStrategy` completely eliminated; schemas propagated via `TraceEvent.metadata["generated_schema"]`.
- [ ] `MatrixSensorPromptBuilder.build_caching_prefix` formats pure `<theory_context>\n{citation}\n</theory_context>` XML block, omitting raw URLs from the LLM prompt.
- [ ] `SourceVerificationInputsDTO` created (with `strict=True`, `extra="forbid"`, strictly no `@property`); consolidated text computed locally in hook.
- [ ] `source_verification_hook.py` short-circuits on empty/whitespace inputs, returning full zero-claims `SourceVerificationResultDTO` envelope.
- [ ] `source_verification_hook.py` registered with `@hook_registry.register("source_verification")` and exported in `hooks/__init__.py`.
- [ ] `SourceVerificationService` uses `MIN_VERIFIABLE_TEXT_LENGTH = 15`, static module prompt constants, `LLMClient.from_strategy("fast", repository=self.system_repo)`, and `html.escape()` XML sanitization.
- [ ] All 8 AST guardrails implemented and passing in `test_ast_theory_grounding_guardrails.py`.
- [ ] Comprehensive unit test suites created/updated for `PromptEngine`, `NodeStrategyFactory`, `test_dag_executor_mcp_concurrency.py`, `test_prompt_block.py`, and `test_source_verification_hook.py`.
- [ ] All repository mock return values across unit test suites migrated from legacy raw dictionaries to strict Pydantic V2 model instances (`Step`, `PromptBlock`, `Workflow`, `OutputProfile`).
- [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- [ ] Live E2E verification passes: `RUN_LIVE_E2E=true uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

### 7.2 Verification Execution Commands
```powershell
# 1. Run Repository & Strategy Unit Tests
uv run pytest backend_v2/tests/unit/database/repositories/components/test_prompt_block.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py

# 2. Run Hook & Service Tests
uv run pytest backend_v2/tests/unit/hooks/test_source_verification_hook.py backend_v2/tests/unit/services/test_source_verification_service.py backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py

# 3. Run AST Guardrail Suite
uv run pytest backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py

# 4. Run Global Backend Quality Loop
uv run python scripts/backend_audit_loop.py backend_v2 --test

# 5. Live E2E Integration Gate
$env:RUN_LIVE_E2E="true"
uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```
