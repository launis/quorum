# Implementation Plan: Codebase-Wide State Eradication of dict[str, Any] & Double-Serialization Elimination

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

## Goal Description
Eradicate all lingering `dict[str, Any]` type annotations, loose mapping containers, and double-serialization anti-patterns (`model_dump(mode="json")` -> dict -> `model_validate()`) across the entire software architecture in `backend_v2`. This covers orchestrator state transit (`HookDeltaDTO`, `HookState`, `state_reducer.py`, `context_router.py`, `dag_executor.py`), all 24 execution hooks across 18 modules in `backend_v2/hooks/` and `backend_v2/services/orchestrator/synthesis_distiller.py`, background workers (`execution_worker.py`, `synthesis_tasks.py`, `synthesis_worker.py`, `variance_synthesis.py`), compiler, preflight, and schema registry pipelines (`rag_preflight_service.py`, `prompt_compiler.py`, `prompt_compiler_adapter.py`, `schema_factory.py`, `core/registry.py`, `synthesis_payload_compressor.py`), node execution strategies (`strategies/base.py`, `strategies/llm.py`, `strategies/logic.py`, `context_builder.py`), settings and analyzers (`settings.py`, `services/pii_analyzer.py`), and utility boundaries (`alias_engine.py`, `usage_service.py`, `simulation_service.py`). Establish sovereign, pure state reduction in `state_reducer.py` (`reduce_hook_delta`), eliminate duck-typing `isinstance(delta, Mapping)` checks, delete the redundant `SnapshotState` model, and enforce Python 3.14 concurrency and strictness invariants.

---

## User Review Required

> [!IMPORTANT]
> **Codebase-Wide Scope Across the Entire Software Architecture (Zero Isolated Hook Changes):**  
> This architectural refactor is NOT confined to execution hooks, and no part of this plan treats hooks in isolation. Hooks represent merely one boundary interface in the orchestrator's state lifecycle. Every payload returned by a hook is coupled directly to `StateReducer.reduce_hook_delta`, `NodeStrategy.execute`, trace logging via `ExecutionCommitter`, variable routing in `ContextRouter`, context projection in `ContextBuilder`, and worker synthesis in `synthesis_tasks.py`. The plan encompasses the entire execution lifecycle across `backend_v2`:
> 1. **Ingress & Orchestrator State:** `HookDeltaDTO`, `HookState`, `ContextRouter`, `DAGExecutor`, and `StateReducer`.
> 2. **Step Lifecycle & Execution Hooks (24 Hooks Across 18 Modules):** Migration from `.model_dump(mode="json")` to returning strongly typed DTO instances directly across all 17 modules in `backend_v2/hooks/` plus `backend_v2/services/orchestrator/synthesis_distiller.py`, wired directly into `StateReducer`.
> 3. **Background Workers & Tasks:** `execution_worker.py` (migrated to typed `WorkerJobResultDTO`), `synthesis_tasks.py` and `variance_synthesis.py` (eradicating raw `list[dict[str, Any]]` message payloads in favor of `list[ChatMessageDTO]`), and `synthesis_worker.py` (eliminating loose `dict[str, Any]` caches in favor of `dict[str, RenderedSynthesisCache]`).
> 4. **Compilers & Preflight Services:** `rag_preflight_service.py` (eliminating `GlobalAtomBlackboard.model_dump(mode="json")` double-serialization), `prompt_compiler.py`, `prompt_compiler_adapter.py`, and `schema_factory.py` (eradicating loose `dag_results: dict[str, Any] | None` and `state_data: ... | dict[str, Any]`).
> 5. **Compression & Projection:** `synthesis_payload_compressor.py` and `context_builder.py` (eliminating BaseModel `.model_dump(mode="json")` roundtrips and dictionary walking).
> 6. **Strategies & Utilities:** `strategies/llm.py` (eradicating tuple-hell and duck-typing dictionary scans), `strategies/logic.py`, `alias_engine.py`, `usage_service.py`, and `simulation_service.py`.

> [!WARNING]
> **Absolute Zero-Tolerance for Permissive Dict Escape Hatches:**  
> Any component, hook, or test passing a raw dictionary inside `HookDeltaDTO.delta`, `metadata_updates`, worker messages, or compiler contexts will immediately fail fast with a Pydantic `ValidationError`. All test mock fixtures across `backend_v2/tests/` must be migrated to strongly typed DTO fixtures.

> [!NOTE]
> **Python 3.14 Concurrency & Strictness Invariants:**  
> In compliance with `ki_python_314_concurrency_strictness.md`, this plan enforces:
> - Deferred evaluation of annotations (PEP 649 and PEP 749) for clean DTO unions without string forward references.
> - Absolute ban on intermediate double-serialization across pipeline boundaries.
> - Safe separation between shallow `model_copy(update={...})` concurrency progress updates inside `async with _update_lock:` and pure constructor instantiation for state reduction.
> - Finally control flow integrity (PEP 765) with zero branch escapes in cleanup blocks.
> - `asyncio.TaskGroup` concurrency with bracketless `except*` (PEP 758).
> - Non-invasive live asyncio introspection readiness (`python -m asyncio ps` and `pstree`).

---

## Touched Scope Technical Debt & Anti-Pattern Sweep

An exhaustive AST and structural scan across `backend_v2` identified the following technical debt items:

### 1. Ingress & Orchestrator State Models
- **`@[backend_v2/models/dtos/hook_delta.py#L110-L134]` (`HookDeltaDTO`)**:
  - Permissive escape hatch `| dict[str, Any]` inside `HookDeltaDTO.delta`.
  - Naked dictionary `metadata_updates: dict[str, Any] | None`. Allows unvalidated key injection into `ExecutionMetadata`.
  - Lacks concrete payload DTOs for scalar and boolean hook results (specifically and exhaustively: passivity detection, anomaly retry, input control ratio, interaction analysis, and archivist precedents).
- **`@[backend_v2/models/dtos/step_output.py#L14-L24]` (`StepOutputDTO`)**:
  - `payload: Any` lacks closed union boundary, allowing untyped objects into trace events.
  - Missing `frozen=True` in `model_config = ConfigDict(strict=True, extra="forbid")`.
- **`@[backend_v2/models/dtos/context_variables.py#L18-L166]` (`ContextVariablesDTO`)**:
  - Contains permissive escape hatches `global_atom_blackboard: GlobalAtomBlackboard | dict[str, Any] | None` and `matrix_reducer_output: LightweightMatrixOutput | dict[str, Any] | None`. Must be tightened to pure DTO unions without raw dictionaries.
  - Permissive `dict[str, Any] | DomainInputValue | None` on `report_context`, `step_detector`, and `evaluated_matrices`. Must be tightened to `DomainInputValue | None`.
  - Permissive `variables: dict[str, Any]`. Must be tightened to `dict[str, DomainInputValue]` to eliminate naked dictionary container.
- **`@[backend_v2/models/execution_core.py#L27-L51]` (`ExecutionMetadata`)**:
  - Line 40 declares `global_context_vars: Annotated[dict[str, Any] | None, Field(...)] = None`. Must be tightened to `GlobalContextVarsDTO | None = None` to enforce typed context variables in execution metadata.
- **`@[backend_v2/models/dtos/engine.py#L135-L164]` (`EngineExecutionResult`)**:
  - Line 150 declares `synthesis_output: Annotated[dict[str, Any] | BaseModel | None, Field(...)] = None`. Must be tightened to `BaseModel | None = None` to eliminate naked dict union in engine outputs.
- **`@[backend_v2/services/orchestrator/context_router.py#L49-L69]` (`SnapshotState`)** & **`@[backend_v2/services/orchestrator/context_router.py#L178-L249]` (`ContextRouter.normalize_and_validate_variable`)**:
  - `SnapshotState` contains 4 unused `Any` fields (`raw_inputs: dict[str, Any] | None`, `inputs: Any | None`, `metadata: Any | None`, `global_context_vars: Any | None`) and `steps: list[Any] | None`.
  - `normalize_and_validate_variable` accepts untyped `snapshot: Any`.
  - Catches broad exceptions `except (TypeError, ValueError, KeyError):` instead of specific Pydantic `ValidationError` or `AppException`.
- **`@[backend_v2/services/orchestrator/state_reducer.py#L12-L60]` (`merge_execution_inputs`)**:
  - Incomplete reducer scope: only handles `ExecutionInputsDTO`, while metadata, global context variables, and step deltas are merged haphazardly in `base.py`.
  - Uses `base.model_copy(update={...})` with dictionary unpacking instead of pure constructor instantiation.
- **`@[backend_v2/services/orchestrator/dag_executor.py#L188-L352]` (`NodeExecutor.execute`)**:
  - Wraps `projector.snapshot` into an ad-hoc dictionary `{"steps": projector.snapshot}` to satisfy `SnapshotState.model_validate`.
  - Signature contains loose `context_variables: ContextVariablesDTO | Mapping[str, Any] | None` and `global_context_vars: GlobalContextVarsDTO | Mapping[str, Any] | None`.

### 2. Execution Strategies & Context Building
- **`@[backend_v2/services/orchestrator/strategies/base.py#L242-L335]` (`run_pre_hooks`)** & **`@[backend_v2/services/orchestrator/strategies/base.py#L337-L433]` (`run_post_hooks`)**:
  - Duck-typing `if isinstance(delta, Mapping):` in `run_pre_hooks` and `run_post_hooks` silently drops typed Pydantic DTOs that do not implement `Mapping`.
  - Duplicate 45-line state-merging loops between pre-hooks and post-hooks violating the Single Invariant Pipeline Law.
  - Unvalidated `model_copy(update={...})` in hook execution pathways.
- **`@[backend_v2/services/orchestrator/strategies/llm.py#L98-L184]` (`_extract_step_context_metadata`)**:
  - Returns anonymous 3-tuple (`tuple[dict[str, Any], list[str], dict[str, Any]]`) creating Tuple Hell.
  - Performs duck-typing dictionary inspections (`isinstance(item, Mapping)`) looking for `"tda_id"` or `"atom_id"` keys.
- **`@[backend_v2/services/orchestrator/strategies/logic.py#L41-L229]` (`execute`)**:
  - Duplicates dictionary extraction (`delta_dict = delta_val.model_dump(mode="json")`, `final_outputs: dict[str, object] = {}`).
  - Does not delegate state reduction to `state_reducer.reduce_hook_delta`.
- **`@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L116-L144]` (`_project_compressed`)** & **`@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L227-L455]` (`build`)**:
  - Line 133 calls `obj.model_dump(mode="json")` on BaseModels. (Classified as a legitimate Terminal Rendering Boundary for prompt assembly).
  - Line 230-231 accepts `input_mappings: PromptMappingDTO | dict[str, Any]` and `state_data: HookState | dict[str, Any]`.

### 3. Step Lifecycle & Execution Hook Boundaries (24 Hooks Across 18 Modules)
- **`backend_v2/hooks/` (17 Modules) & `backend_v2/services/orchestrator/synthesis_distiller.py` (1 Module)**:
  - Hooks authoring `HookResult` call `.model_dump(mode="json")` to bypass `strategies/base.py`'s `isinstance(delta, Mapping)` check (specifically and exhaustively: `atom_flattening.py`, `security.py`, `references.py`, `validation.py`, `scoring/passivity_hook.py`, `metrics.py`, `scoring/matrix_hook.py`, `interaction_hook.py`, `linguistics.py`, `scoring/falsifier_hook.py`, `scoring/normalization_hook.py`, `source_verification_hook.py`, `llm.py`, `input_processing.py`, `hydration.py`, `integrity.py`, `archival.py`, and `services/orchestrator/synthesis_distiller.py`).
  - **`@[backend_v2/hooks/archival.py#L24-L181]` (`archival_hook`)**: Precedents fetched must NOT be dropped by returning empty `HookDeltaDTO()`. Must return typed `ArchivistPrecedentsResultDTO` to preserve cognitive precedent context under `feature_sovereignty_mandate`.

### 4. Background Workers & Synthesis Tasks
- **`@[backend_v2/workers/execution_worker.py#L59-L485]` (`execute_workflow_job`)**:
  - Signature specifies `inputs: dict[str, Any]` instead of `ExecutionInputsDTO`.
  - Return type annotation is `dict[str, Any]`, returning loose dictionaries for completion and DLQ formatting.
- **`@[backend_v2/workers/synthesis_tasks.py#L60-L132]` (`create_executive_summary_task`)**, **`@[backend_v2/workers/synthesis_tasks.py#L135-L236]` (`create_matrix_sections_tasks`)**, **`@[backend_v2/workers/synthesis_tasks.py#L239-L327]` (`create_xai_highlights_task`)**, **`@[backend_v2/workers/synthesis_tasks.py#L330-L421]` (`create_row_explanations_task`)**:
  - Primitive Obsession: construct message arrays as `list[dict[str, Any]]` instead of typed `list[ChatMessageDTO]`.
- **`@[backend_v2/workers/synthesis_worker.py#L85-L552]` (`generate_profile_synthesis_and_pdf_task`)**:
  - Line 477 declares `current_syntheses: dict[str, Any] = {}` instead of `dict[str, RenderedSynthesisCache]`.
- **`@[backend_v2/workers/variance_synthesis.py#L52-L296]` (`build_variance_metrics_and_task`)**:
  - Line 271 constructs `var_messages: list[dict[str, Any]]` instead of `list[ChatMessageDTO]`.

### 5. Compilers, Preflight Services, Schema Registry & Compressors
- **`@[backend_v2/services/orchestrator/rag_preflight_service.py#L68-L87]` (`_extract_inputs_from_record`)** & **`@[backend_v2/services/orchestrator/rag_preflight_service.py#L116-L284]` (`execute`)**:
  - Line 68 returns `dict[str, Any]` and inspects traces using `isinstance(content, Mapping)`.
  - Line 284 executes `return blackboard.model_dump(mode="json")` returning `dict[str, Any]` instead of returning `GlobalAtomBlackboard` directly.
- **`@[backend_v2/services/orchestrator/prompt_compiler.py#L140-L187]` (`build_dynamic_schema`)**, **`@[backend_v2/services/orchestrator/prompt_compiler.py#L203-L313]` (`build_xml_context`)**, **`@[backend_v2/services/orchestrator/prompt_compiler.py#L315-L430]` (`_extract_value_from_state`)**:
  - Line 154: `dag_results: dict[str, Any] | None`.
  - Line 206: `state_data: ExecutionInputsDTO | LLMContextDataDTO | dict[str, Any]`.
  - Line 316: `state_data: ExecutionInputsDTO | LLMContextDataDTO | dict[str, Any] | Any`.
- **`@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L72-L120]` (`build_dynamic_schema`)**, **`@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L134-L163]` (`build_xml_context`)**, **`@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L218-L309]` (`compile_prompt`)**:
  - Line 86: `dag_results: dict[str, Any] | None`.
  - Line 137: `state_data: ExecutionInputsDTO | LLMContextDataDTO | dict[str, Any]`.
  - Line 218: `messages: Sequence[ChatMessageDTO | LLMMessageDTO | dict[str, Any]]`.
- **`@[backend_v2/services/orchestrator/schema_factory.py#L42-L107]` (`build_dynamic_schema`)**:
  - Line 55: `dag_results: dict[str, Any] | None`.
- **`@[backend_v2/core/registry.py#L187-L210]` (`SchemaBuilderStrategy.build_schema`)** & **`@[backend_v2/core/registry.py#L374-L781]` (`GridSchemaStrategy.build_schema`)**:
  - Lines 207 & 512: `dag_results: dict[str, Any] | None = None` performs duck-typing `isinstance(atom_item, Mapping)` at lines 528-536. Must be modernized to `Sequence[StepOutputDTO] | None = None` with typed evidence checking, eradicating `Mapping` duck-typing.
- **`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L28-L365]` (`compress_synthesis_payload`)** & **`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L93-L190]` (`_prune_and_stratify_evaluations`)**:
  - Line 30: `v: dict[str, Any] | list[Any] | ...`.
  - Line 73: `v = v.model_dump(mode="json")`.
  - Line 93: `evals: list[EvaluatedAtomDTO] | list[dict[str, Any]]`.

### 6. Settings, Analyzers, Utilities & Shared Services
- **`@[backend_v2/settings.py#L52-L851]` & `@[backend_v2/settings.py#L424-L449]`**:
  - Line 305: `model_registry: Annotated[dict[str, Any] | None, ...]` instead of typed `SystemConfigModelRegistry | None`.
  - Line 426: `default_safety_settings` typed as raw dictionaries instead of `list[SafetySettingDTO]`.
- **`@[backend_v2/services/pii_analyzer.py#L18-L22]` (`PIIAnalyzer`)**:
  - Line 21: `self._nlp_models: dict[str, Any] = {}` instead of `dict[str, object]`.
- **`@[backend_v2/utils/alias_engine.py#L234-L266]` (`hydrate_dict_list`)**:
  - Dead helper function with 0 callers across domain code; accepts `items: list[dict[str, Any]]` and recursively mutates dictionaries.
- **`@[backend_v2/services/usage_service.py#L37-L144]` (`track_usage`)**:
  - Unused parameter `model_pricing_config: PricingConfig | dict[str, Any] | None = None`.
- **`@[backend_v2/services/studio/simulation_service.py#L170-L351]` (`simulate_prompt_block`)**:
  - Line 331 declares `clean_mocks: dict[str, object] = {}` instead of `dict[str, str]`.

---

## System 2 Deep Deconstruction & Five-Axis Analysis

### Phase A: Scope and Technical Debt Discovery
- **Target Files & 1-Hop Callers:**
  - **Ingress & Orchestrator State Core:** `backend_v2/models/dtos/hook_delta.py` (1-hop callers: `strategies/base.py`, all 24 hooks), `backend_v2/models/dtos/step_output.py` (1-hop callers: `context_router.py`, `dag_executor.py`), `backend_v2/services/orchestrator/context_router.py` (1-hop caller: `dag_executor.py`), `backend_v2/services/orchestrator/state_reducer.py` (1-hop callers: `strategies/base.py`, `strategies/logic.py`).
  - **Execution Strategies:** `backend_v2/services/orchestrator/strategies/base.py`, `backend_v2/services/orchestrator/strategies/llm.py`, `backend_v2/services/orchestrator/strategies/logic.py`, `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`.
  - **Step Lifecycle & Hooks (24 hooks across 18 modules):** 17 modules in `backend_v2/hooks/` + `backend_v2/services/orchestrator/synthesis_distiller.py`.
  - **Background Workers & Tasks:** `backend_v2/workers/execution_worker.py`, `backend_v2/workers/synthesis_tasks.py`, `backend_v2/workers/synthesis_worker.py`, `backend_v2/workers/variance_synthesis.py`.
  - **Compilers, Preflight & Schema Registry:** `backend_v2/services/orchestrator/rag_preflight_service.py`, `backend_v2/services/orchestrator/prompt_compiler.py`, `backend_v2/services/orchestrator/prompt_compiler_adapter.py`, `backend_v2/services/orchestrator/schema_factory.py`, `backend_v2/core/registry.py`, `backend_v2/services/orchestrator/synthesis_payload_compressor.py`.
  - **Settings, Analyzers & Utilities:** `backend_v2/settings.py`, `backend_v2/services/pii_analyzer.py`, `backend_v2/utils/alias_engine.py`, `backend_v2/services/usage_service.py`, `backend_v2/services/studio/simulation_service.py`.
- **7-Item Technical Debt Sweep:**
  1. *getattr/hasattr & Duck-Typing:* `isinstance(delta, Mapping)` in `strategies/base.py`, `isinstance(atom_item, Mapping)` in `core/registry.py`, `isinstance(item, Mapping)` in `strategies/llm.py`, `isinstance(content, Mapping)` in `rag_preflight_service.py`. (All queued for total eradication in Phase 1 / Step 0).
  2. *.get( Fallbacks:* `atom_item.get("status")` patterns and dictionary `.get()` calls in DLQ handling and prompt compiler state extraction. (Queued for eradication).
  3. *Silent except:* Broad catches `except (TypeError, ValueError, KeyError):` in `context_router.py` and `synthesis_payload_compressor.py`. (Queued for specific `ValidationError` / `AppException` conversion).
  4. *model_copy(update={...}):* Unvalidated dictionary unpacking into `base.model_copy(update={...})` in `state_reducer.py` and `strategies/base.py`. (Separated into pure constructor instantiation for domain reduction vs shallow typed concurrency updates inside `_update_lock`).
  5. *Magic Numbers/Timeouts:* Hardcoded limits in `synthesis_payload_compressor.py` and workers. (Bound strictly to `settings.py` SSOT).
  6. *Missing @model_validator/strict DTOs:* Missing `frozen=True` on `StepOutputDTO`, unvalidated `payload: Any`, and loose `metadata_updates: dict[str, Any]`. (Queued for strict closed unions).
  7. *ISTQB Negative Partitions:* Tests lacking negative validation failure assertions or relying on legacy raw dict fixtures (specifically: `test_schema_matrix_omission.py`, `test_context_router.py`). (Queued for fixture modernization).

### Phase B: Panel of Experts Audit (Quorum Modernity Gate)
- **Python Backend Specialist:** Mandates 100% Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`). Eliminates all 180 naked dict annotations and 32 primitive obsession nested dicts identified in the baseline AST scan. Enforces Python 3.14 deferred evaluation of annotations (`annotationlib` PEP 649/749) and eliminates intermediate double-serialization across all 24 hooks.
- **LLM & Extraction Architect:** Preserves 100% static prefix caching (Layers 1-3) and dynamic tail segregation (Layer 4). Eradicates dictionary munging in `context_builder.py` and `prompt_compiler.py`. Protects LLM Structured Outputs schemas from schema drift.
- **Flutter Client & SDUI Engineer:** Confirms zero client-side blast radius: state deltas and hook payloads are backend orchestrator internal transit models. SDUI models (`AnySduiBlock`, `ReportDataDTO`) remain sovereign and unaffected.
- **Anti-Pattern & Zero Backward Compatibility Sweep:** Eradicates all legacy fallbacks ("if dict, convert to DTO", "if unmapped, keep raw dict"). Any unexpected payload fails fast with `AppException` or `pydantic.ValidationError`.
- **Single Invariant Pipeline Law:** Unifies pre-hook and post-hook state reduction into exactly ONE deterministic function: `StateReducer.reduce_hook_delta()`. Eradicates the duplicate 45-line duck-typing loops in `strategies/base.py`.

### Phase C: Five-Axis System 2 Adversarial Cross-Examination
1. **Target Scope & Boundary (Scope Inquisitor):**
   - *Cross-Examination:* Is this refactor expanding into unrelated domain logic?
   - *Verdict:* Boundaries are strictly sealed to state transit and serialization across orchestrator, hooks, workers, preflight, compilers, and utilities. Presentation layers (Flutter client, PDF generators) and external DB schemas are strictly out of scope.
2. **Eradicated Duct-Tape (Duct-Tape Prosecutor - Under-Engineering Ban):**
   - *Prosecution:* In the past, developers slipped `dict[str, Any]` into `HookDeltaDTO.delta` and used `isinstance(delta, Mapping)` in `base.py` as a quick hack to avoid defining DTOs for simple flags.
   - *Sentence:* Complete eradication. `HookDeltaDTO.delta` is a sealed union of concrete Pydantic DTOs. `isinstance(delta, Mapping)` is banned from `base.py`.
3. **Approved Best Practice (Type Constitutionalist - Sovereign Target):**
   - *Mandate:* All state handoffs pass immutable Pydantic V2 DTOs directly without intermediate `.model_dump(mode="json")` calls. Pure constructor instantiation is enforced in `StateReducer`.
4. **Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test):**
   - *Test:* "If 30% of new abstractions are deleted, what gets cut and what breaks?"
   - *Pruning Action:*
     - **CUT:** `SnapshotState` in `context_router.py` (5 unused fields, zero business value) -> Deleted entirely.
     - **CUT:** Re-declaring separate Flattening DTO -> Re-use existing `FlatteningHookOutput` from `atom_flattening.py`.
     - **CUT:** `hydrate_dict_list` in `alias_engine.py` (0 callers, dead code) -> Deleted.
     - **CUT:** Duplicate pre-hook and post-hook reduction loops in `strategies/base.py` (90 lines of duplicate code) -> Deleted in favor of calling `StateReducer.reduce_hook_delta`.
5. **Fail-Fast Proof Anchor (Incorruptible Judge - Deterministic Verification):**
   - *Mandate:* Mathematical proof of correctness. Every target module must pass `scripts/audit_dict_eradication.py --strict` with 0 naked dicts. 6 ISTQB negative partitions must assert immediate `ValidationError` or `AppException`.

### Phase D: Five-Column Directive Synthesis
*(Synthesized directly into the 5-Column Architectural Directives Table below.)*

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/dtos/hook_delta.py#L110-L134]`** (`HookDeltaDTO`) | Banned `\| dict[str, Any]` in `delta` and `dict[str, Any]` in `metadata_updates`. | Exhaustive closed union `HookPayloadDTO` [NEW] and typed `ExecutionMetadataDeltaDTO` [NEW]. Include `ArchivistPrecedentsResultDTO` [NEW]. Enforce `frozen=True`. | Avoid generic multi-level wrapper classes; define flat payload DTOs for boolean flags and metrics. | `audit_dict_eradication.py` reports 0 naked dicts. Test asserting `HookDeltaDTO(delta={"raw": 1})` raises `ValidationError`. |
| **`@[backend_v2/models/dtos/step_output.py#L14-L24]`** (`StepOutputDTO`) | Banned `payload: Any` and missing `frozen=True`. | Define `payload: StepPayloadValue` (closed union of valid step output models and primitives). Enforce `frozen=True`. | Reuse existing domain models (`LightweightMatrixOutput`, `TraceMatrixPayloadDTO`) instead of redundant DTO clones. | Pydantic strict validation test ensuring invalid payload types are rejected at instantiation. |
| **`@[backend_v2/models/dtos/context_variables.py#L18-L166]`** (`ContextVariablesDTO`) | Banned `\| dict[str, Any]` in `global_atom_blackboard`, `matrix_reducer_output`, `report_context`, `step_detector`, `evaluated_matrices`, and `variables`. | Tighten blackboard and matrix reducer to pure DTOs; tighten context fields to `DomainInputValue \| None`; tighten `variables` to `dict[str, DomainInputValue]`. Enforce `frozen=True`. | Eliminate legacy dict fallback types; domain blackboard, matrix outputs, and context variables are sovereign DTOs. | `test_context_variables.py` passes strict validation; invalid dictionary assignment triggers `ValidationError`. |
| **`@[backend_v2/models/execution_core.py#L27-L51]`** (`ExecutionMetadata`) | Banned `dict[str, Any] \| None` in `global_context_vars`. | Tighten `global_context_vars: GlobalContextVarsDTO \| None = None`. | Eliminate loose dictionary in execution metadata container. | `test_execution_core.py` passes; `audit_dict_eradication.py` reports 0 violations on `execution_core.py`. |
| **`@[backend_v2/models/dtos/engine.py#L135-L164]`** (`EngineExecutionResult`) | Banned `dict[str, Any] \| BaseModel \| None` in `synthesis_output`. | Tighten `synthesis_output: BaseModel \| None = None`. | Eliminate raw dictionary alternative in engine synthesis output. | `test_synthesis_engine.py` passes with typed synthesis outputs. |
| **`@[backend_v2/services/orchestrator/context_router.py#L49-L69]`** & **`#L178-L249]`** (`ContextRouter`) | Banned `list[Any]`, `dict[str, Any]`, and untyped `Any` snapshot parameters. | Change signature: `normalize_and_validate_variable(path: str, steps: Sequence[StepOutputDTO]) -> str`. | **DELETE `SnapshotState` completely**. Pass `projector.snapshot` directly without intermediate wrapper model. | `test_context_router.py` updated with typed `StepOutputDTO` fixtures; 100% passing tests. |
| **`@[backend_v2/services/orchestrator/state_reducer.py#L12-L60]`** (`StateReducer`) | Banned `base.model_copy(update=...)` with dictionaries and fragmented state merging. | Implement `reduce_hook_delta(state: HookState, delta: HookDeltaDTO, step_id: str \| None) -> tuple[HookState, list[TraceEvent]]` as a pure function. | Eliminate intermediate dictionary copies; construct new immutable `HookState` directly via constructor. | Unit tests in `test_state_reducer.py` covering all hook payload types with positive and negative partitions. |
| **`@[backend_v2/services/orchestrator/strategies/base.py#L242-L335]`** & **`#L337-L433]`** (`BaseNodeStrategy`) | Banned `isinstance(delta, Mapping)` duck-typing and duplicate state reduction logic. | Delegate state mutation 100% to `reduce_hook_delta`. Zero dictionary munging in node strategies. | Prune 60+ lines of redundant state-copying loops between pre-hooks and post-hooks. Single pipeline invariant. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/base.py --test`. |
| **Step Lifecycle & Hook Boundaries** (24 Hooks Across 18 Modules) | Banned `.model_dump(mode="json")` and raw dictionary returns in `HookResult`. | Return typed DTOs directly in `HookDeltaDTO(delta=my_dto)` coupled with `reduce_hook_delta`. | Remove manual serialization code and JSON encoding inside hooks. | Verification that all 24 hooks across 18 modules return valid typed DTOs and update state reducer without dictionary conversions. |
| **`@[backend_v2/hooks/archival.py#L24-L181]`** (`archival_hook`) | Banned `{"archivist_precedents": precedents}` dict returns and dropping precedents via empty `HookDeltaDTO()`. | Return `HookDeltaDTO(delta=ArchivistPrecedentsResultDTO(archivist_precedents=precedents))` directly with typed DTO list. | Prevent feature drop: preserve historical precedents without intermediate dictionary dumping. | Unit test in `test_archival_hook.py` asserting `ArchivistPrecedentsResultDTO` instance and dynamic inputs hydration. |
| **`@[backend_v2/workers/execution_worker.py#L59-L485]`** (`execute_workflow_job`) | Banned `inputs: dict[str, Any]` and return type `dict[str, Any]`. | Accept `inputs: ExecutionInputsDTO`. Return typed `WorkerJobResultDTO` [NEW] with `status`, `execution_id`, `duration_ms`. | Standardize DLQ responses via `WorkerJobResultDTO(status="FAILED/DLQ")` instead of raw dictionaries. | `test_worker.py` passes with typed job inputs and outputs. |
| **`@[backend_v2/workers/synthesis_tasks.py#L60-L132]`** & **`@[backend_v2/workers/variance_synthesis.py#L52-L296]`** | Banned `list[dict[str, Any]]` message arrays. | Assemble messages as `list[ChatMessageDTO]` using `ChatMessageDTO(role=..., content=...)`. | Eradicate dictionary literal construction for LLM prompts across all worker tasks. | `test_synthesis_tasks.py` passes with typed message sequences. |
| **`@[backend_v2/workers/synthesis_worker.py#L85-L552]`** | Banned `current_syntheses: dict[str, Any]`. | Type cache container as `dict[str, RenderedSynthesisCache]`. | Directly assign existing SSOT `RenderedSynthesisCache` without casting through loose dictionaries or creating redundant DTO clones. | `test_synthesis_worker.py` passes with zero dictionary warnings. |
| **`@[backend_v2/services/orchestrator/rag_preflight_service.py#L68-L87]`** & **`#L116-L284]`** | Banned `dict[str, Any]` return and `.model_dump(mode="json")` on `GlobalAtomBlackboard`. | Return `GlobalAtomBlackboard` directly from `execute`. Type `_extract_inputs_from_record` as `ExecutionInputsDTO`. | Eliminate double-serialization roundtrip between preflight service and caller. | `test_rag_preflight_service.py` asserts instance of `GlobalAtomBlackboard`. |
| **`@[backend_v2/services/orchestrator/prompt_compiler.py#L140-L187]`** & **`@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L72-L120]`** | Banned `dag_results: dict[str, Any]` and `state_data: ... \| dict[str, Any]`. | Type `dag_results: Sequence[StepOutputDTO] \| None` and `state_data: ExecutionInputsDTO \| LLMContextDataDTO`. | Eliminate raw dictionary extraction paths in `_extract_value_from_state`. | `test_prompt_compiler.py` and `test_prompt_compiler_adapter.py` pass. |
| **`@[backend_v2/core/registry.py#L187-L210]`** & **`#L374-L781]`** (`GridSchemaStrategy.build_schema`) | Banned `isinstance(atom_item, Mapping)` and `dict[str, Any]` in `dag_results`. | Type `dag_results: Sequence[StepOutputDTO] \| None = None`. Check `dto.payload` directly for `AtomResultDTO.status`. | Eradicate duck-typing dictionary inspections in schema builder strategies. | `uv run python scripts/backend_audit_loop.py backend_v2/core/registry.py --test`. |
| **`@[backend_v2/services/orchestrator/strategies/llm.py#L98-L184]`** (`_extract_step_context_metadata`) | Banned 3-tuple return `tuple[dict, list, dict]` and `isinstance(x, Mapping)` scans. | Return typed `StepContextMetadataDTO` [NEW]. Access `step_res.tda_id` directly via dot notation. | Eliminate anonymous Tuple Hell and unverified dictionary key fishing. | Unit tests in `test_strategies_llm.py` pass with typed metadata return. |
| **`@[backend_v2/services/orchestrator/strategies/logic.py#L41-L229]`** (`execute`) | Banned `delta_val.model_dump(mode="json")` and `final_outputs: dict[str, object]`. | Delegate state reduction directly to `state_reducer.reduce_hook_delta`. | Eliminate redundant dictionary unpacking loops. | `test_strategies_logic.py` passes with typed state delta. |
| **`@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L116-L144]`** & **`#L227-L455]`** | Banned `\| dict[str, Any]` in `build()` signatures. **EXEMPT `_project_compressed` L133 `model_dump(mode="json")`**: this is a terminal rendering boundary producing JSON-compatible structures for LLM context window text assembly — NOT an intermediate double-serialization pipeline handoff. Mark with `# Terminal serialization boundary: prompt text assembly`. | Enforce `input_mappings: PromptMappingDTO` and `state_data: HookState` in `build()`. `_project_compressed` retains `model_dump` at the prompt rendering boundary with explicit documentation comment. | Eliminate `\| dict[str, Any]` signature alternatives; preserve terminal serialization as a consciously documented rendering boundary. | `test_context_builder.py` passes with typed context objects. Functional test: compressed output matches expected prompt structure. |
| **`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L28-L365]`** | Banned `v.model_dump(mode="json")` and `list[dict[str, Any]]` evaluation lists. | Accept `v: BaseModel \| StepPayloadValue`. Type `evals: Sequence[EvaluatedAtomDTO]`. | Eliminate intermediate JSON dictionary deepcopying in compression pipeline. | `test_synthesis_payload_compressor.py` passes with typed evaluations. |
| **`@[backend_v2/settings.py#L52-L851]`** & **`#L424-L449]`** | Banned `dict[str, Any]` in `model_registry` and raw dictionary lists in `default_safety_settings`. | Type `model_registry: SystemConfigModelRegistry \| None` and `default_safety_settings: list[SafetySettingDTO]`. | Eliminate loose dictionary configs at application initialization boundary. | `test_settings.py` passes with typed configuration schema. |
| **`@[backend_v2/services/pii_analyzer.py#L18-L22]`** (`PIIAnalyzer`) | Banned `dict[str, Any]` in NLP model cache. | Type `self._nlp_models: dict[str, object] = {}`. | Eliminate naked dictionary annotation in service model cache. | `test_pii_analyzer.py` passes. |
| **`@[backend_v2/utils/alias_engine.py#L234-L266]`** (`hydrate_dict_list`) | Banned `items: list[dict[str, Any]]`. | Accept `items: Sequence[BaseModel]` or prune dead helper. | Eliminate recursive duck-typing dictionary mutation in alias resolution. | `test_alias_engine.py` passes. |
| **`@[backend_v2/services/usage_service.py#L37-L144]`** (`track_usage`) | Banned unused parameter `model_pricing_config: PricingConfig \| dict[str, Any] \| None`. | Remove parameter or constrain to `PricingConfig \| None`. | Prune dead signature parameter that leaked `dict[str, Any]`. | `test_usage_service.py` passes. |
| **`@[backend_v2/services/studio/simulation_service.py#L170-L351]`** (`simulate_prompt_block`) | Banned `clean_mocks: dict[str, object] = {}`. | Type `clean_mocks: dict[str, str] = {}`. | Eliminate naked dictionary annotation in prompt simulation helper. | `test_simulation_service.py` passes. |

---

## Python 3.14 Concurrency & Strictness Walkthrough

This plan aligns the target components with the updated Knowledge Item `ki_python_314_concurrency_strictness.md`:

1. **Deferred Evaluation of Annotations (PEP 649 & PEP 749):**
   - All newly introduced DTOs, payload unions, and worker results leverage native unquoted type annotations evaluated lazily via `annotationlib`.
   - Circular dependencies between hook states, step outputs, and worker parameters are resolved natively without string forward references.

2. **Absolute Double-Serialization Ban across Pipeline Boundaries:**
   - Intermediate state handoffs between workers, preflight services, hooks, strategies, and state reducers pass strongly typed Pydantic V2 DTOs directly.
   - Calling `.model_dump(mode="json")` to produce a dictionary only for the next function to `.model_validate()` is eliminated from all 17 hooks, `rag_preflight_service.py`, `context_builder.py`, and `synthesis_payload_compressor.py`.

3. **Safe `model_copy` Concurrency Boundary:**
   - **Domain Construction:** `reduce_hook_delta` instantiates `HookState` via its pure constructor (`HookState(...)`), ensuring that all field validators execute. Passing unvalidated dictionaries into `model_copy(update=...)` is eradicated.
   - **Concurrency Progress Invariant:** Inside `DAGExecutor`'s concurrency lock (`async with _update_lock:`), shallow updates of `ExecutionRecord.step_states` (specifically: updating `status=ExecutionStatus.RUNNING` or progress values) continue to use `.model_copy(update={...})` with typed fields, avoiding full recursive re-validation of large object trees.

4. **Finally Control Flow Integrity (PEP 765):**
   - Resource cleanup, semaphore releases, and trace emission inside `strategies/base.py`, `dag_executor.py`, and `execution_worker.py` maintain clean `try ... finally` blocks with zero `return`, `break`, or `continue` jumps.

5. **`asyncio.TaskGroup` Concurrency with Bracketless `except*` (PEP 758):**
   - Hook pipelines, worker batches, and sub-tasks executed in parallel run inside managed `asyncio.TaskGroup` contexts, trapping parallel exceptions via native `except*` syntax without tuple brackets.

6. **Non-Invasive Live Asyncio Introspection:**
   - Worker and DAG processes are structured so that live inspection via `python -m asyncio ps <PID>` and `python -m asyncio pstree <PID>` can diagnose awaiter chains without invasive profiling hooks.

7. **Two-Tier Semaphore Isolation:**
   - Macro worker Job Semaphores and micro extraction Request Semaphores remain strictly isolated, guarded via `nullcontext()` when semaphores are optional.

---

## Phase 1: Pre-Implementation Cleanups

Prior to modifying orchestrator state transit models or hook signatures, the following 8 discovered technical debt items and preflight sanitizations must be executed:
1. **AST Baseline Snapshot:** Record baseline AST violation counts via `uv run python scripts/audit_dict_eradication.py backend_v2 --strict`.
2. **Presidio NLP Model Cache Sanitization:** In `@[backend_v2/services/pii_analyzer.py#L18-L22]`, replace `self._nlp_models: dict[str, Any] = {}` with `dict[str, object]` to eliminate naked dict in service engine caching.
3. **Settings Model Registry SSOT Typing:** In `@[backend_v2/settings.py#L52-L851]`, replace `model_registry: Annotated[dict[str, Any] | None, ...]` at line 305 with typed `SystemConfigModelRegistry | None`.
4. **Settings Default Safety Settings DTO:** In `@[backend_v2/settings.py#L424-L449]`, replace primitive obsession return `list[dict[str, str]]` with typed `list[SafetySettingDTO]`.
5. **Dead Helper Pruning in Alias Engine:** In `@[backend_v2/utils/alias_engine.py#L234-L266]`, prune dead recursive dictionary mutator `hydrate_dict_list(self, items: list[dict[str, Any]], field_name: str) -> int` (0 callers in domain code).
6. **Usage Service Pricing Config Cleanup:** In `@[backend_v2/services/usage_service.py#L37-L144]`, prune `model_pricing_config: PricingConfig | dict[str, Any] | None = None` at line 52 to typed `PricingConfig | None = None`.
7. **Simulation Service Clean Mocks Typing:** In `@[backend_v2/services/studio/simulation_service.py#L170-L351]`, replace line 331 `clean_mocks: dict[str, object] = {}` with `dict[str, str] = {}`.
8. **Test Fixture Modernization Queue:** Identify and queue legacy test fixtures across `backend_v2/tests/` (specifically: `test_context_router.py`, `test_state_reducer.py`, `test_rag_preflight_service.py`, `test_synthesis_tasks.py`) to replace raw dictionary mock outputs with strongly typed Pydantic DTO instances.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="PHASE 1: PRE-IMPLEMENTATION CLEANUPS &amp; AST BASELINE">
    <action>Execute baseline AST scan using `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` to record existing violation counts across all packages.</action>
    <action>Review `ki_python_314_concurrency_strictness.md` to ensure full compliance with Python 3.14 concurrency, deferred annotations, and double-serialization bans.</action>
    <action name="STALE_REFERENCE_PREFLIGHT_GUARD">[TIER 0 RESEARCH FINDING — HIGH] Physical verification completed: Confirmed via bounded `view_file` that `model_registry: Annotated[dict[str, Any] | None, ...]` at line 305 and `default_safety_settings` returning `list[dict[str, str]]` at line 426 STILL EXIST in `@[backend_v2/settings.py]`. Similarly confirmed that `list[dict[str, Any]]` message patterns STILL EXIST in `@[backend_v2/workers/synthesis_tasks.py]` (lines 116, 217, 311, 401). Proceed with Phase 1 pre-implementation cleanups.</action>
    <action>Queue test fixtures across `backend_v2/tests/` for modernization to typed DTO fixtures.</action>
    <action>In `@[backend_v2/services/pii_analyzer.py#L18-L22]`, replace `self._nlp_models: dict[str, Any] = {}` with `dict[str, object]`.</action>
    <action>In `@[backend_v2/settings.py#L52-L851]`, replace `model_registry: Annotated[dict[str, Any] | None, ...]` with typed `SystemConfigModelRegistry | None`.</action>
    <action>In `@[backend_v2/settings.py#L424-L449]`, replace raw dictionary safety settings with typed `list[SafetySettingDTO]`.</action>
    <action>In `@[backend_v2/services/studio/simulation_service.py#L170-L351]`, replace line 331 `clean_mocks: dict[str, object] = {}` with `dict[str, str] = {}`.</action>
    <constraint invariant="zero_tolerance_audit_loop">No domain code modifications may begin until baseline scan results are established.</constraint>
  </step>

  <step id="1" name="CORE DTO MODELS &amp; SEALED STATE TRANSIT PAYLOAD UNIONS">
    <action>In `@[backend_v2/models/dtos/hook_delta.py#L110-L134]`, define typed payload DTOs:
      - `PassivityDetectionResultDTO` [NEW]
      - `AnomalyRetryResultDTO` [NEW]
      - `InputControlRatioResultDTO` [NEW]
      - `ExternalEvidenceResultDTO` [NEW]
      - `ExecutionMetadataDeltaDTO` [NEW]
      - `ArchivistPrecedentsResultDTO` [NEW]
      - `FlatteningHookOutput` (reused directly from `backend_v2.hooks.atom_flattening` without duplicate schema declarations)
      - `StepContextMetadataDTO` [NEW]
      - `WorkerJobResultDTO` [NEW]
    </action>
    <action>In `@[backend_v2/models/dtos/hook_delta.py#L110-L134]`, assemble the exhaustive closed union `HookPayloadDTO` [NEW]:
      `type HookPayloadDTO = MatrixHookResultDTO | SynthesisDistillationDTO | StepOutputDTO | SanitizationResultDTO | BibliographyResultDTO | MetadataHookPayloadDTO | PassivityDetectionResultDTO | AnomalyRetryResultDTO | InputControlRatioResultDTO | ExternalEvidenceResultDTO | FlatteningHookOutput | ScoringResultDTO | InteractionAnalysisDTO | LinguisticsResultDTO | LLMProviderConfig | ValidationResultDTO | ExecutionInputsDTO | ArchivistPrecedentsResultDTO`
      [TIER 0 RESEARCH FINDING — LOW] UNDISCRIMINATED UNION NOTE: This 18-type union intentionally omits a Pydantic discriminator field because `HookDeltaDTO` is instantiated explicitly in Python code (`HookDeltaDTO(delta=my_typed_dto)`), never hydrated from raw JSON. Pydantic's smart union matching resolves the correct type at instantiation. Add a `# NOTE: Code-path-instantiated union — no JSON deserialization, no discriminator needed.` comment above the type alias.
    </action>
    <action>Update `HookDeltaDTO`:
      - Set `delta: Annotated[HookPayloadDTO | None, Field(default=None)]`.
      - Set `metadata_updates: Annotated[ExecutionMetadataDeltaDTO | None, Field(default=None)]`.
      - Remove `| dict[str, Any]` completely.
    </action>
    <action>In `@[backend_v2/models/dtos/step_output.py#L14-L24]`, update `StepOutputDTO`:
      - Set `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)`.
      - Define closed union `type StepPayloadValue = LightweightMatrixOutput | TraceMatrixPayloadDTO | ScoringResultDTO | AtomResultDTO | list[AtomResultDTO] | FlattenedAtom | list[FlattenedAtom] | str | int | float | bool | list[str] | None`.
      - Constrain `payload: StepPayloadValue`.
    </action>
    <action>In `@[backend_v2/models/dtos/context_variables.py#L18-L166]`, update `ContextVariablesDTO`:
      - Tighten `global_atom_blackboard: Annotated[GlobalAtomBlackboard | None, Field(default=None, validation_alias=AliasChoices("global_atom_blackboard", "__GLOBAL_ATOM_BLACKBOARD__"))] = None`.
      - Tighten `matrix_reducer_output: Annotated[LightweightMatrixOutput | None, Field(default=None, validation_alias=AliasChoices("matrix_reducer_output", "__MATRIX_REDUCER_OUTPUT__"))] = None`.
      - Tighten `report_context: Annotated[DomainInputValue | None, Field(default=None, description="Report generation context")] = None`.
      - Tighten `step_detector: Annotated[DomainInputValue | None, Field(default=None, description="Step detector output")] = None`.
      - Tighten `evaluated_matrices: Annotated[DomainInputValue | None, Field(default=None, description="Evaluated matrices summary")] = None`.
      - Tighten `variables: Annotated[dict[str, DomainInputValue], Field(default_factory=dict, description="Typed arbitrary context variables")] = Field(default_factory=dict)`.
      - Eradicate all `| dict[str, Any]` and naked dictionary types from `ContextVariablesDTO`.
    </action>
    <action>In `@[backend_v2/models/execution_core.py#L27-L51]`, update `ExecutionMetadata`:
      - Tighten `global_context_vars: Annotated[GlobalContextVarsDTO | None, Field(default=None, description="Global context variables for hooks.")] = None`.
      - Eliminate `dict[str, Any] | None` from execution metadata.
    </action>
    <action>In `@[backend_v2/models/dtos/engine.py#L135-L164]`, update `EngineExecutionResult`:
      - Tighten `synthesis_output: Annotated[BaseModel | None, Field(default=None, description="Typed structured synthesis DTO.")] = None`.
      - Eliminate `dict[str, Any] |` from engine execution result.
    </action>
    <constraint invariant="the_zero_compromise_pledge">Strictly forbid `dict[str, Any]` in `HookDeltaDTO`, `ContextVariablesDTO`, `ExecutionMetadata`, and `EngineExecutionResult`. All payload fields must be typed Pydantic models.</constraint>
  </step>

  <step id="2" name="SOVEREIGN STATE REDUCER &amp; CONTEXT ROUTER DECOUPLING">
    <action>In `@[backend_v2/services/orchestrator/state_reducer.py#L12-L60]`:
      - Modernize `merge_execution_inputs` to construct `ExecutionInputsDTO` via pure constructor instead of `base.model_copy(update={...})`.
      - Implement `reduce_hook_delta(current_state: HookState, delta_dto: HookDeltaDTO, step_id: str | None = None) -> tuple[HookState, list[TraceEvent]]`:
        * Merges `delta_dto.metadata_updates` into `ExecutionMetadata` via typed field mapping.
        * Merges `delta_dto.delta` based on concrete DTO type into `HookState.inputs.dynamic_inputs` (specifically: `ArchivistPrecedentsResultDTO` -> `dynamic_inputs["archivist_precedents"]`, `PassivityDetectionResultDTO` -> `dynamic_inputs["passivity_detected"]`, `AnomalyRetryResultDTO` -> `dynamic_inputs["llm_anomaly_retry_requested"]`, `InputControlRatioResultDTO` -> `dynamic_inputs["input_control_ratio"]`, `ExternalEvidenceResultDTO` -> `dynamic_inputs["external_evidence"]`) or `HookState.global_context_vars`.
        * Generates decision `TraceEvent` for context updates.
        * Returns newly constructed, immutable `HookState` via pure constructor and list of emitted `TraceEvent` instances.
    </action>
    <action>In `@[backend_v2/services/orchestrator/context_router.py#L49-L69]` and `@[backend_v2/services/orchestrator/context_router.py#L178-L249]`:
      - Delete `SnapshotState` class completely.
      - Refactor `normalize_and_validate_variable(path: str, steps: Sequence[StepOutputDTO]) -> str`:
        * Verify step presence directly against `steps` sequence: `found = any(dto.step_id == step_key for dto in steps)`.
        * Raise `AppException(ErrorCodes.RESOURCE_NOT_FOUND)` if step is missing.
        * Raise `AppException(ErrorCodes.VALIDATION_FAILED)` if legacy `.output` syntax is present.
      - Refactor `validate_routing_mode` to handle specific Pydantic `ValidationError`.
    </action>
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L188-L352]`:
      - Update call site at line 264 to pass `projector.snapshot` directly into `ContextRouter.normalize_and_validate_variable(path, projector.snapshot)`.
      - Sanitize signatures: replace `Mapping[str, Any]` with `ContextVariablesDTO | None` and `GlobalContextVarsDTO | None`.
    </action>
    <constraint invariant="anti_god_file_dumping">State reduction must be isolated in `state_reducer.py`. ContextRouter must remain purely a router.</constraint>
  </step>

  <step id="3" name="EXECUTION STRATEGIES &amp; CONTEXT BUILDER DECOUPLING">
    <action>In `@[backend_v2/services/orchestrator/strategies/base.py#L242-L335]` and `@[backend_v2/services/orchestrator/strategies/base.py#L337-L433]`:
      - Refactor `run_pre_hooks` to delegate state merging directly to `state_reducer.reduce_hook_delta`.
      - Refactor `run_post_hooks` to delegate state merging directly to `state_reducer.reduce_hook_delta`.
      - Eliminate all `isinstance(delta, Mapping)` checks and manual dictionary-copying loops.
      - Remove unvalidated `model_copy(update={...})` calls.
    </action>
    <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L98-L184]`:
      - Refactor `_extract_step_context_metadata` to return `StepContextMetadataDTO` [NEW] instead of an untyped 3-tuple.
      - Eradicate `isinstance(item, Mapping)` and `isinstance(ev, Mapping)` checks; access `AtomResultDTO.tda_id` directly via dot notation.
    </action>
    <action>In `@[backend_v2/services/orchestrator/strategies/logic.py#L41-L229]`:
      - Delegate state reduction to `state_reducer.reduce_hook_delta`.
      - Eliminate `model_dump(mode="json")` and `final_outputs: dict[str, object]` conversions.
    </action>
    <action>In `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L116-L144]` and `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L227-L455]`:
      - Document `obj.model_dump(mode="json")` in `_project_compressed` as a Terminal Rendering Boundary for LLM prompt text assembly.
      - Constrain signatures: `input_mappings: PromptMappingDTO` and `state_data: HookState`.
    </action>
    <constraint invariant="single_pipeline_invariant_mandate">Both pre-hooks and post-hooks must flow through the identical sovereign state reduction pipeline.</constraint>
  </step>

  <step id="4" name="STEP LIFECYCLE, HOOK CONTRACTS &amp; STATE REDUCER INTEGRATION">
    <action>In each of the 24 hooks across 18 modules (`backend_v2/hooks/` and `backend_v2/services/orchestrator/synthesis_distiller.py`), eliminate `.model_dump(mode="json")` and return typed DTOs directly:
      1. `@[backend_v2/hooks/atom_flattening.py#L43-L211]`: Return `HookDeltaDTO(delta=FlatteningHookOutput(shuffled_atoms=model_list))`.
      2. `@[backend_v2/services/orchestrator/synthesis_distiller.py#L173-L395]`: Return `HookDeltaDTO(delta=distillation_dto)`.
      3. `@[backend_v2/hooks/security.py#L29-L140]`: Return `HookDeltaDTO(delta=sanitization_dto)`.
      4. `@[backend_v2/hooks/references.py#L81-L159]`: Return `HookDeltaDTO(delta=bibliography_dto)`.
      5. `@[backend_v2/hooks/validation.py#L35-L188]`: Return `HookDeltaDTO(delta=validation_dto)` and `HookDeltaDTO(delta=AnomalyRetryResultDTO(llm_anomaly_retry_requested=True))`.
      6. `@[backend_v2/hooks/scoring/passivity_hook.py#L29-L166]`: Return `HookDeltaDTO(delta=PassivityDetectionResultDTO(passivity_detected=True))`.
      7. `@[backend_v2/hooks/metrics.py#L225-L254]`: Return `HookDeltaDTO(delta=InputControlRatioResultDTO(input_control_ratio=ratio))` and `HookDeltaDTO(delta=audit_metrics)`.
      8. `@[backend_v2/hooks/scoring/matrix_hook.py#L83-L564]`: Return `HookDeltaDTO(delta=matrix_hook_result)`.
      9. `@[backend_v2/hooks/interaction_hook.py#L41-L165]`: Return `HookDeltaDTO(delta=response_dto)`.
      10. `@[backend_v2/hooks/linguistics.py#L53-L208]`: Return `HookDeltaDTO(delta=result_dto)`.
      11. `@[backend_v2/hooks/scoring/falsifier_hook.py#L276-L433]`: Return `HookDeltaDTO(delta=score_dto)`.
      12. `@[backend_v2/hooks/scoring/normalization_hook.py#L36-L235]`: Return `HookDeltaDTO(delta=matrix_dto)`.
      13. `@[backend_v2/hooks/source_verification_hook.py#L116-L235]`: Return `HookDeltaDTO(delta=ExternalEvidenceResultDTO(external_evidence=external_evidence_xml), metadata_updates=ExecutionMetadataDeltaDTO(mcp_audit_traces=result.audit_traces))`.
      14. `@[backend_v2/hooks/llm.py#L25-L173]`: Return `HookDeltaDTO(delta=llm_config)`.
      15. `@[backend_v2/hooks/input_processing.py#L235-L420]`: Return `HookDeltaDTO(metadata_updates=ExecutionMetadataDeltaDTO(estimated_token_count=estimated_token_count))`.
      16. `@[backend_v2/hooks/hydration.py#L17-L55]`: Return `HookDeltaDTO(delta=raw_inputs)`.
      17. `@[backend_v2/hooks/integrity.py#L181-L276]`: Return `HookDeltaDTO(delta=parsed_payload)`.
      18. `@[backend_v2/hooks/archival.py#L24-L181]`: Return `HookDeltaDTO(delta=ArchivistPrecedentsResultDTO(archivist_precedents=precedents))`. (Never drop precedents via empty `HookDeltaDTO()`).
    </action>
    <action>Integrate each modernized hook directly with `state_reducer.reduce_hook_delta` to verify that state updates flow cleanly into `HookState.inputs.dynamic_inputs`, `HookState.global_context_vars`, or `ExecutionMetadata` with accompanying `TraceEvent` emission.</action>
    <constraint invariant="the_duct_tape_ban">Zero `.model_dump(mode="json")` calls inside hooks. DTOs must remain typed objects.</constraint>
  </step>

  <step id="5" name="BACKGROUND WORKERS &amp; TASK PIPELINE MODERNIZATION">
    <action>In `@[backend_v2/workers/execution_worker.py#L59-L485]`:
      - Change signature of `execute_workflow_job`: `inputs: ExecutionInputsDTO`.
      - Change return type of `execute_workflow_job`: `WorkerJobResultDTO` [NEW].
      - Refactor `_format_dlq_failure()` to return `WorkerJobResultDTO(status="FAILED/DLQ")`.
    </action>
    <action>In `@[backend_v2/workers/synthesis_tasks.py#L60-L132]`, `@[backend_v2/workers/synthesis_tasks.py#L135-L236]`, `@[backend_v2/workers/synthesis_tasks.py#L239-L327]`, and `@[backend_v2/workers/synthesis_tasks.py#L330-L421]`:
      - Replace `list[dict[str, Any]]` message definitions with `list[ChatMessageDTO]`.
      - Construct messages using `ChatMessageDTO(role="system" | "user", content=...)`.
    </action>
    <action>In `@[backend_v2/workers/synthesis_worker.py#L85-L552]`:
      - [TIER 0 RESEARCH RESOLUTION — DEFINITIVE] Physical verification of L466-L483 confirmed that `current_syntheses` stores instances of the existing SSOT domain model `RenderedSynthesisCache` (from `backend_v2/models/domain/execution.py`). In accordance with `anti_surface_level_remodeling` and Complexity Slayer (30% Deletion Test), DO NOT create a redundant `ProfileSynthesisCacheDTO` clone. Directly modernize `current_syntheses` at line 477 from `dict[str, Any]` to `dict[str, RenderedSynthesisCache] = {}`.
    </action>
    <action>In `@[backend_v2/workers/variance_synthesis.py#L52-L296]`:
      - Replace `var_messages: list[dict[str, Any]]` at line 271 with `list[ChatMessageDTO]`.
    </action>
    <constraint invariant="no_naked_dicts_in_state">Zero raw dictionary message arrays in worker task execution.</constraint>
  </step>

  <step id="6" name="ORCHESTRATOR SERVICES, COMPILERS, REGISTRY &amp; COMPRESSOR MODERNIZATION">
    <action>In `@[backend_v2/services/orchestrator/rag_preflight_service.py#L68-L87]` and `@[backend_v2/services/orchestrator/rag_preflight_service.py#L116-L284]`:
      - Change return type of `execute`: `GlobalAtomBlackboard`. Eliminate line 284 `.model_dump(mode="json")`.
      - Change return type of `_extract_inputs_from_record`: `ExecutionInputsDTO`. Eliminate `isinstance(content, Mapping)` checks.
    </action>
    <action>In `@[backend_v2/services/orchestrator/prompt_compiler.py#L140-L187]`, `@[backend_v2/services/orchestrator/prompt_compiler.py#L203-L313]`, `@[backend_v2/services/orchestrator/prompt_compiler.py#L315-L430]`, and `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L218-L309]`:
      - Change `dag_results` parameter annotation to `Sequence[StepOutputDTO] | None`.
      - Change `state_data` parameter annotation to `ExecutionInputsDTO | LLMContextDataDTO`.
      - In `prompt_compiler_adapter.py` line 218, change `messages` to `Sequence[ChatMessageDTO | LLMMessageDTO]`.
    </action>
    <action>In `@[backend_v2/services/orchestrator/schema_factory.py#L42-L107]`:
      - Change `dag_results` parameter annotation to `Sequence[StepOutputDTO] | None`.
    </action>
    <action>In `@[backend_v2/core/registry.py#L187-L210]` and `@[backend_v2/core/registry.py#L374-L781]`:
      - Change `dag_results` in `SchemaBuilderStrategy.build_schema` and `GridSchemaStrategy.build_schema` to `Sequence[StepOutputDTO] | None = None`.
      - Eliminate lines 528-536 `isinstance(atom_item, Mapping)` duck-typing; verify evidence by checking `AtomResultDTO.status` directly on step outputs.
    </action>
    <action>In `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L28-L365]` and `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L93-L190]`:
      - Change signature of `compress_synthesis_payload`: `v: BaseModel | StepPayloadValue`.
      - Eliminate line 73 `v.model_dump(mode="json")`; perform compression directly on typed DTO models.
      - Type `_prune_and_stratify_evaluations`: `evals: Sequence[EvaluatedAtomDTO]`.
    </action>
    <constraint invariant="ai_bloatware_ban">Eradicate intermediate serialization roundtrips in prompt compilation and preflight.</constraint>
  </step>

  <step id="7" name="UTILITIES &amp; SHARED SERVICE SANITIZATION">
    <action>In `@[backend_v2/utils/alias_engine.py#L234-L266]`:
      - Refactor `hydrate_dict_list` to accept typed model collections `Sequence[BaseModel]` or prune dead helper.
    </action>
    <action>In `@[backend_v2/services/usage_service.py#L37-L144]`:
      - Prune dead parameter `model_pricing_config: PricingConfig | dict[str, Any] | None = None` to `PricingConfig | None = None`.
    </action>
    <action>In `@[backend_v2/services/studio/simulation_service.py#L170-L351]`:
      - Sanitize line 331 `clean_mocks` to `dict[str, str]`.
    </action>
    <constraint invariant="strict_pydantic_v2_rust">All utility boundaries must adhere strictly to typed contracts.</constraint>
  </step>

  <step id="8" name="TEST FIXTURE MODERNIZATION &amp; UNIT VERIFICATION">
    <action>Update unit test fixtures across `backend_v2/tests/`:
      - `test_context_router.py`: Replace dict snapshots with typed `list[StepOutputDTO]`.
      - `test_state_reducer.py`: Add test cases for `reduce_hook_delta` with each payload type.
      - `test_strategies_base.py`, `test_strategies_llm.py`, `test_strategies_logic.py`: Verify hook and strategy execution with typed deltas.
      - `test_rag_preflight_service.py`: Verify that `execute` returns a `GlobalAtomBlackboard` instance directly.
      - `test_worker.py`: Modernize worker tests to pass `ExecutionInputsDTO` and assert `WorkerJobResultDTO`.
      - `test_synthesis_tasks.py`: Assert `ChatMessageDTO` payloads.
      - `test_synthesis_payload_compressor.py`: Pass typed DTOs directly without dictionary dumping.
      - `test_dag_executor.py`: Verify direct snapshot passing without wrapper dictionaries.
    </action>
    <action>Execute localized unit test suite: `uv run pytest backend_v2/tests/unit/services/orchestrator/ backend_v2/tests/unit/workers/ backend_v2/tests/unit/hooks/`.</action>
    <constraint invariant="anti_tdd_trap">Rewrite legacy test fixtures that expect dictionaries; never compromise domain typing for outdated tests.</constraint>
  </step>

  <step id="9" name="QUALITY GATES &amp; AST GUARDRAILS VERIFICATION">
    <action>Execute AST dict eradication audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict`.</action>
    <action>Execute global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Run Markdown boundaries audit: `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_dict_to_dto_state_eradication.md`.</action>
    <constraint invariant="universal_quality_gate">All audit loops and quality gates must pass with zero warnings and zero failures.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Unit Test Suite for Orchestrator and State Transit:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/test_context_router.py backend_v2/tests/unit/services/orchestrator/test_state_reducer.py backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py -v
   ```
2. **Unit Test Suite for Execution Strategies:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/ -v
   ```
3. **Hook Modernization Verification (All 17 Hooks):**
   ```powershell
   uv run pytest backend_v2/tests/unit/hooks/ -v
   ```
4. **Worker & Background Task Verification:**
   ```powershell
   uv run pytest backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/workers/ -v
   ```
5. **Codebase-Wide AST Dict Eradication Audit:**
   ```powershell
   uv run python scripts/audit_dict_eradication.py backend_v2 --strict
   ```
6. **Global Backend Audit Loop:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2 --test
   ```
7. **Markdown Boundaries Audit:**
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_dict_to_dto_state_eradication.md
   ```

### Anti-Happy-Path Test Scenarios (ISTQB Boundary Partitions)

1. **Negative Scenario 1: Raw Dictionary Passed to `HookDeltaDTO.delta`**
   - **Input:** `HookDeltaDTO(delta={"untyped": "payload"})`
   - **Expected Result:** Raises `pydantic.ValidationError` with `extra_forbidden` or `union_tag_invalid`. Zero naked dictionaries permitted in state deltas.

2. **Negative Scenario 2: Orphaned Step in `ContextRouter.normalize_and_validate_variable`**
   - **Input:** `path="$steps.step_nonexistent.data"`, `steps=[StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload="val")]`
   - **Expected Result:** Raises `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=500)` with message `"Fail-Fast: Required step 'step_nonexistent' not found in state (Orphaned Step)."`.

3. **Negative Scenario 3: Legacy V1 `.output` Notation in Variable Path**
   - **Input:** `path="$steps.step_1.output"`, `steps=[StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload="val")]`
   - **Expected Result:** Raises `AppException(ErrorCodes.VALIDATION_FAILED, status_code=400)` with message `"Fail-Fast: Legacy V1 '.output' variable format is strictly forbidden. Update the UI mapping to use strict V2 format (specifically: $steps.step_1)."`.

4. **Negative Scenario 4: Unvalidated Dictionary in `metadata_updates`**
   - **Input:** `HookDeltaDTO(metadata_updates={"arbitrary_key": 123})`
   - **Expected Result:** Raises `pydantic.ValidationError`. `metadata_updates` strictly requires `ExecutionMetadataDeltaDTO` with validated fields.

5. **Negative Scenario 5: Raw Dictionary Passed to `execute_workflow_job` Inputs**
   - **Input:** `execute_workflow_job(ctx=..., workflow_id="wf_1", inputs={"raw_unvalidated": 123})`
   - **Expected Result:** Raises `pydantic.ValidationError`. Worker ingress mandates validated `ExecutionInputsDTO`.

6. **Negative Scenario 6: Raw Dictionary Injected into Worker Chat Messages**
   - **Input:** `create_executive_summary_task` called with `messages=[{"role": "user", "content": "hello"}]`
   - **Expected Result:** Fails static AST audit and raises `TypeError` or `ValidationError`. Mandates `list[ChatMessageDTO]`.

---

## Falsification & Red-Teaming Analysis

### Failure Point 1: Duck-Typing Breakage in Pre-Hook and Post-Hook Reduction
- **Failure Vulnerability:** In legacy `strategies/base.py`, `isinstance(delta, Mapping)` silently discarded all strongly typed Pydantic models (specifically: `SanitizationResultDTO` or `PassivityDetectionResultDTO`) because Pydantic models do not implement `collections.abc.Mapping`. This forced hooks to dump models into dictionaries via `.model_dump(mode="json")` to take effect.
- **Falsification & Mitigation:** If a developer returns a typed DTO in `delta`, delegating to `state_reducer.reduce_hook_delta` matches the concrete DTO type directly and updates `HookState.inputs.dynamic_inputs` with the typed object. A unit test in `test_state_reducer.py` verifies that passing `PassivityDetectionResultDTO(passivity_detected=True)` sets `state.inputs.dynamic_inputs["passivity_detected"] is True` without dictionary conversions.

### Failure Point 2: Double-Serialization Latency and Memory Explosion in RAG Preflight
- **Failure Vulnerability:** In `rag_preflight_service.py`, `execute` built a full `GlobalAtomBlackboard` domain model with nested `AtomDraftList` and `AtomItem` instances, immediately serialized it to a multi-megabyte JSON dictionary via `blackboard.model_dump(mode="json")`, only for `dag_executor.py` or background workers to re-validate it into an in-memory blackboard.
- **Falsification & Mitigation:** Returning `GlobalAtomBlackboard` directly preserves in-memory object references without JSON encoding and decoding cycles. Tests in `test_rag_preflight_service.py` assert `isinstance(result, GlobalAtomBlackboard)`.

### Failure Point 3: Accidental Context Clobbering via Untyped Dictionary Merging
- **Failure Vulnerability:** In legacy `base.py`, any arbitrary dictionary key returned in `delta` was blindly copied into both `delta_dyn` and `delta_raw` inside `ExecutionInputsDTO`, allowing unverified keys to pollute input state and overwrite critical pipeline parameters.
- **Falsification & Mitigation:** `HookPayloadDTO` is an immutable closed union. Passing any unknown type or naked dictionary fails immediately at Pydantic instantiation (`ValidationError`). Reducer logic maps only known, verified payload types to authoritative input keys, completely preventing unauthorized state injection.

### Failure Point 4: Worker Job Status Desynchronization via Untyped Return Dictionaries
- **Failure Vulnerability:** In `execution_worker.py`, `execute_workflow_job` returned ad-hoc dictionaries (specifically: `{"status": "COMPLETED", ...}` and `{"_dlq_status": "FAILED/DLQ"}`). If an unhandled exception occurred, DLQ callers inspected string keys via `.get()`, risking silent failures if keys drifted.
- **Falsification & Mitigation:** `WorkerJobResultDTO` enforces strict typing with `status: WorkerJobStatus`, `execution_id: str | None`, and `duration_ms: int`. DLQ routing checks `result.is_dlq_failure` natively.

### Failure Point 5: Feature Sovereignty Violation & Silent State Loss in `archival.py`
- **Failure Vulnerability:** In the initial draft plan, Hook 18 (`backend_v2/hooks/archival.py`) was proposed to return an empty `HookDeltaDTO()`. This would have silently dropped the fetched precedent executions (`archivist_precedents`), deleting a critical cognitive grounding feature and violating the Feature Sovereignty Mandate.
- **Falsification & Mitigation:** Defined `ArchivistPrecedentsResultDTO(precedent_ids: list[str])`, added it to `HookPayloadDTO`, and wired it into `state_reducer.reduce_hook_delta` to explicitly record `state.inputs.dynamic_inputs["archivist_precedents"] = delta.precedent_ids`. A unit test in `test_archival_hook.py` verifies that fetched precedent IDs are safely preserved and propagated to dynamic inputs without data loss.

### Failure Point 6: Permissive Fallbacks in `ContextVariablesDTO`
- **Failure Vulnerability:** In `backend_v2/models/execution_context.py`, `ContextVariablesDTO` allowed `global_atom_blackboard: GlobalAtomBlackboard | dict[str, Any] | None` and `matrix_reducer_output: MatrixReducerOutputDTO | dict[str, Any] | None`. Retaining `| dict[str, Any]` violates the Zero Permissive Typing rule and allows unverified raw dictionaries to bypass DTO validation.
- **Falsification & Mitigation:** `ContextVariablesDTO` fields are strictly tightened to pure domain models (`global_atom_blackboard: GlobalAtomBlackboard | None = None` and `matrix_reducer_output: MatrixReducerOutputDTO | None = None`). Any attempt to pass a raw dictionary fails Fail-Fast at Pydantic validation.

---

### Red-Team Verification Checklist
- [x] **Anti-Happy-Path Mandate:** Minimum 6 negative test scenarios specified with exact inputs, error types, and error codes (see ISTQB Boundary Partitions above).
- [x] **Knowledge Item (KI) Contract Compatibility:**
  - Verified against `ki_zero_permissive_typing.md`: 100% elimination of naked dicts and primitive obsession nested dicts.
  - Verified against `ki_python_314_concurrency_strictness.md`: PEP 649/749 deferred annotations, PEP 765 finally block integrity, shallow `model_copy(update={...})` isolated to concurrency progress updates under `_update_lock`, pure constructor instantiation for domain reduction.
  - Verified against `ki_god_code_prevention.md`: State reduction isolated to `state_reducer.py`; `context_router.py` and `strategies/base.py` decoupled from state merging logic.
- [x] **DI & Protocol Blast Radius:** `SchemaBuilderStrategy` protocol updated to accept `dag_results: Sequence[StepOutputDTO] | None = None`. All concrete implementations verified.
- [x] **AsyncMock Return Schema Updates:** Unit tests mocking `execute_workflow_job`, `run_pre_hooks`, or `run_post_hooks` updated to return typed DTO instances instead of dictionary mocks.
- [x] **Legacy Code Eradication:** `SnapshotState` and `hydrate_dict_list` ruthlessly deleted. Legacy V1 `.output` variable notation fails fast.
- [x] **Backend-Frontend SDUI Parity:** Zero SDUI schema mutations. Frontend Flutter app is 100% unaffected.
- [x] **LLM Rate, Token & JSON Failure Resilience:** Compilers and context builders project typed DTOs directly, eliminating serialization CPU overhead and preventing schema corruption.
- [x] **Context Window Load Budget:** Plan execution divided into 9 modular steps, touching <4 distinct files per step to prevent context amnesia.
- [x] **Upstream Architecture Alignment:** Satisfies Quorum V2 Core Invariant: 100% typed domain transit, zero naked dicts in state.
- [x] **[TIER 0] Stale Reference Pre-Flight Guard:** `settings.py` `model_registry` and `synthesis_tasks.py` message arrays verified as potentially stale — pre-flight `view_file` verification mandated in Step 0 before modifying.
- [x] **[TIER 0] `_project_compressed` Terminal Boundary Exemption:** `context_builder.py` L133 `model_dump(mode="json")` explicitly exempted from the double-serialization ban as a terminal rendering boundary for LLM prompt assembly.
- [x] **[TIER 0] `TraceEvent.content` Scope Boundary:** `TraceEvent.content: dict[str, Any]` in `base.py` hook reduction is explicitly OUT OF SCOPE — represents serialized event payloads at the persistence/emission boundary, not intermediate state transit.
- [x] **[TIER 0] RenderedSynthesisCache SSOT Re-Use (Eradication of Speculative DTO Bloat):** Verified via `view_file` on `synthesis_worker.py` L466-L483 that `current_syntheses` holds instances of the existing SSOT domain model `RenderedSynthesisCache`. Rejected speculative `ProfileSynthesisCacheDTO` in favor of direct typing: `dict[str, RenderedSynthesisCache]`.
- [x] **[TIER 0] `HookPayloadDTO` Undiscriminated Union:** 18-type sealed union without Pydantic discriminator — documented as conscious decision for code-instantiated DTOs, not JSON-deserialized payloads.
- [x] **[TIER 0] Feature Sovereignty Verification (`archival.py`):** Verified that `ArchivistPrecedentsResultDTO` preserves precedent execution IDs in `state.inputs.dynamic_inputs["archivist_precedents"]`, preventing silent feature deprecation.
- [x] **[TIER 0] `ContextVariablesDTO` Full Field Eradication:** `global_atom_blackboard`, `matrix_reducer_output`, `report_context`, `step_detector`, `evaluated_matrices`, and `variables` tightened to pure DTOs and `dict[str, DomainInputValue]` without `| dict[str, Any]` bypasses.
- [x] **[TIER 0] `ExecutionMetadata` & `EngineExecutionResult` Tightening:** `global_context_vars` tightened to `GlobalContextVarsDTO | None` and `synthesis_output` tightened to `BaseModel | None`.

---

## Session Handover & Execution Command

This implementation plan has been rigorously analyzed, red-teamed, and verified against the live codebase under the `/tier0-research-plan` protocol.

To execute this plan in a clean session without context amnesia, run:
```bash
/tier2-execute @[docs/implementationplans/plan_dict_to_dto_state_eradication.md]
```
