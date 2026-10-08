# Phase 3: Sub-Executor Concurrency Decoupling

**Overview:** Decouple Quorum's DAG sub-executors (`TwoPassAtomizer`, `EnrichedDagExecutor`, `SlidingWindowLinker`) from in-memory concurrency primitives by purging redundant `semaphore` parameters, removing lazy `or` fallback expressions and phantom semaphores, eliminating `sem` parameter drilling and `async with sem:` wrapping across all private chunk extraction helpers, and delegating micro-concurrency throttling to the `LiteLLMProvider` dynamic semaphore pool.

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L110-L127] Phase 3: Sub-Executor Concurrency Decoupling

**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L596]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L79-L148]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L150-L178]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L180-L255]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L257-L356]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L358-L437]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L439-L548]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L550-L581]
- `[MODIFY]` @[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]
- `[MODIFY]` @[backend_v2/services/orchestrator/enriched_dag_executor.py#L50-L218]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L9]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L195-L353]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_dlq_routing.py#L24-L57]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L596]` (`TwoPassAtomizer`) | `semaphore: asyncio.Semaphore \| None` parameter, lazy `or` fallback expressions (`sem = semaphore or asyncio.Semaphore(...)` at L121, L225, L404), `sem: asyncio.Semaphore` plumbing, docstring drift, and `async with sem:` blocks across all four private helpers (`_extract_ontology_from_chunk`, `_extract_atoms_from_chunk`, `_extract_drafts_from_chunk_with_retry`, `_extract_drafts_from_chunk`). | Autonomous `TaskGroup` chunk scheduling relying on `LiteLLMProvider` dynamic semaphore pool for rate-limiting across `execute_phase_0`, `execute_phase_1`, and `execute_phase_1_drafts`. | Pruned redundant internal semaphore instantiation and parameter passing across chunks. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py backend_v2/tests/unit/services/orchestrator/test_dag_executor_dlq_routing.py -v`. Helper fixtures migrated in the same commit as the helper signatures. |
| `@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]` (`SlidingWindowLinker`) | `semaphore: asyncio.Semaphore \| None` parameter, docstring drift, dead `import asyncio` at L9, fallback `if sem is None: sem = asyncio.Semaphore(...)` at L278-L279, and local `async with sem:` chunk lock around sequential window processing. | Pure sequential graph linking relying on `LiteLLMProvider` for micro-concurrency throttling. | Pruned redundant semaphore parameter, fallback checks, dead `import asyncio`, and local chunk locking. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py -v`. |
| `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]` (`EnrichedDagExecutor`) | `semaphore: asyncio.Semaphore \| None` parameter, docstring drift, ternary fallback `sem = semaphore if semaphore is not None else ...` at L115, and local `async with sem:` lock around `ExtractiveSensorService.evaluate_atom_boolean_batch`. | Direct batch evaluation relying on `LiteLLMProvider` for micro-concurrency throttling. | Pruned chunk-level semaphore lock, ternary fallbacks, and plumbing parameter. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py -v`. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Ensure Phase 2 protocol harmonization and Stage A fuzzer rebase are committed and passing.
2. `[CLEANUP]` Migrate unit test calls in `test_two_pass_atomizer.py` (L162/L172, L257/L267, L290/L299, L344/L353) and `test_dag_executor_dlq_routing.py` (L48-L53) in the exact same atomic commit as the atomizer signature changes.
3. `[CLEANUP]` Eliminate phantom semaphores and fallbacks in `enriched_dag_executor.py` (L115) and `sliding_window_linker.py` (L277-L279).
4. `[CLEANUP]` Remove dead `import asyncio` at `sliding_window_linker.py#L9` to prevent Ruff F401 once local semaphore instantiation is purged.
5. `[CLEANUP]` Remove eradicated `semaphore:` and `sem:` entries from docstrings across `two_pass_atomizer.py` (L92, L160, L195, L278, L373, L468, L571), `enriched_dag_executor.py` (L70), and `sliding_window_linker.py` (L212) to prevent docstring parameter drift.
6. `[CLEANUP]` Harmonize `<contract_freeze>` interface signatures and `<test_contracts>` with physical codebase SSOT types (`GlobalOntologyMap`, `ExtractedAtom`, `DraftAtomList`, `AtomExecutionState`, `LinkedAtomGraph`) instead of deprecated speculative abstractions.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify `PromptEngine`, `SynthesisEngine`, and `TDAEngine` execute without top-level semaphore locks.</action>
    <action>Look forward: Verify that removing semaphore parameters from `TwoPassAtomizer`, `EnrichedDagExecutor`, and `SlidingWindowLinker` aligns chunk fan-out with `LiteLLMProvider` rate limiting.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]) and the Tracker document (@[docs/epic/EPIC_155_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_155/03_phase3_plan.md] @[docs/epic/EPIC_155_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>TwoPassAtomizer.execute_phase_0, execute_phase_1, and execute_phase_1_drafts signatures have zero semaphore parameters.</item>
    <item>All four TwoPassAtomizer private helpers (_extract_ontology_from_chunk, _extract_atoms_from_chunk, _extract_drafts_from_chunk_with_retry, _extract_drafts_from_chunk) have zero sem parameters and zero async with sem: blocks.</item>
    <item>EnrichedDagExecutor.execute_graph signature has zero semaphore parameter and zero local async with sem: locks.</item>
    <item>SlidingWindowLinker.link_graph signature has zero semaphore parameter and zero local chunk sem locks.</item>
    <item>Unit tests in test_two_pass_atomizer.py and test_dag_executor_dlq_routing.py pass without passing semaphore fixtures.</item>
    <item>Unit tests in test_enriched_dag_executor.py and test_sliding_window_linker.py pass without concurrency arguments.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT modify NodeStrategy.execute signatures during Phase 3 (quarantined strictly for Phase 4).</anti_target>
    <anti_target>Do NOT remove semaphore or running_event from EngineExecutionRequest during Phase 3 (quarantined strictly for Phase 5).</anti_target>
    <anti_target>Do NOT modify DAGExecutor.run_step_wrapper during Phase 3 (quarantined strictly for Phase 5).</anti_target>
    <anti_target>Do NOT modify RAGPreflightService source code at @[backend_v2/services/orchestrator/rag_preflight_service.py#L134-L301] (1-hop read-only caller verification).</anti_target>
    <anti_target>Do NOT modify ExtractiveSensorService internal semaphore at @[backend_v2/services/orchestrator/extractive_sensor_service.py#L455-L718] (retained concurrency boundary remains out of scope).</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/enriched_dag_executor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/sliding_window_linker.py]</backend>
  </touched_artifacts>

  <contract_freeze>
    <interface name="TwoPassAtomizer Phase Methods">
      <signature>async def execute_phase_0(self, client: LLMClient, hydrated_text: str, progress_callback: Callable[[int, int], Awaitable[None]] | None = None) -> tuple[GlobalOntologyMap, TokenUsage]:</signature>
      <signature>async def execute_phase_1(self, client: LLMClient, hydrated_text: str, ontology: GlobalOntologyMap, progress_callback: Callable[[int, int], Awaitable[None]] | None = None) -> tuple[list[ExtractedAtom], TokenUsage]:</signature>
      <signature>async def execute_phase_1_drafts(self, client: LLMClient, hydrated_text: str, ontology: GlobalOntologyMap, progress_callback: Callable[[int, int], Awaitable[None]] | None = None) -> tuple[DraftAtomList, TokenUsage]:</signature>
      <constraint>Signatures are frozen without semaphore parameters.</constraint>
    </interface>
    <interface name="EnrichedDagExecutor.execute_graph">
      <signature>async def execute_graph(self, nodes: list[LinkedAtomGraph], source_text: str, locale: str | None = None, progress_callback: Callable[[int, int], Awaitable[None]] | None = None, execution_id: str = "default_run", step_id: str | None = None, matrix_context: MatrixEvaluationContext | None = None) -> tuple[dict[str, AtomExecutionState], TokenUsage]:</signature>
      <constraint>Signature is frozen without semaphore parameter.</constraint>
    </interface>
    <interface name="SlidingWindowLinker.link_graph">
      <signature>async def link_graph(self, executor: LLMTaskExecutor, client: LLMClient, atoms: list[ExtractedAtom], ontology_map: GlobalOntologyMap, progress_callback: Callable[[int, int], Awaitable[None]] | None = None) -> tuple[list[LinkedAtomGraph], TokenUsage]:</signature>
      <constraint>Signature is frozen without semaphore parameter.</constraint>
    </interface>
  </contract_freeze>

  <test_contracts>
    <test name="test_two_pass_atomizer_execute_phase_0_without_semaphore" category="positive">
      <input>valid client, hydrated_text</input>
      <expected>returns tuple[GlobalOntologyMap, TokenUsage] with autonomous TaskGroup scheduling</expected>
    </test>
    <test name="test_two_pass_atomizer_execute_phase_1_without_semaphore" category="positive">
      <input>valid client, hydrated_text, ontology</input>
      <expected>returns tuple[list[ExtractedAtom], TokenUsage] with autonomous TaskGroup scheduling</expected>
    </test>
    <test name="test_two_pass_atomizer_helpers_reject_unexpected_semaphore_kwarg" category="error_path">
      <input>call _extract_ontology_from_chunk with sem=asyncio.Semaphore(1)</input>
      <expected>raises TypeError (unexpected keyword argument 'sem')</expected>
    </test>
    <test name="test_enriched_dag_executor_execute_graph_without_semaphore" category="positive">
      <input>valid nodes, source_text, locale</input>
      <expected>returns tuple[dict[str, AtomExecutionState], TokenUsage] relying on provider rate limiting</expected>
    </test>
    <test name="test_enriched_dag_executor_execute_graph_rejects_unexpected_semaphore_kwarg" category="error_path">
      <input>call execute_graph with semaphore=asyncio.Semaphore(1)</input>
      <expected>raises TypeError (unexpected keyword argument 'semaphore')</expected>
    </test>
    <test name="test_sliding_window_linker_link_graph_without_semaphore" category="positive">
      <input>valid executor, client, atoms, ontology_map</input>
      <expected>returns tuple[list[LinkedAtomGraph], TokenUsage] without local chunk sem locks</expected>
    </test>
    <test name="test_sliding_window_linker_link_graph_rejects_unexpected_semaphore_kwarg" category="error_path">
      <input>call link_graph with semaphore=asyncio.Semaphore(1)</input>
      <expected>raises TypeError (unexpected keyword argument 'semaphore')</expected>
    </test>
  </test_contracts>

  <step id="3.1" name="DECOUPLE_TWO_PASS_ATOMIZER">
    <action>In `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L79-L148]`, remove `semaphore: asyncio.Semaphore | None = None` parameter from `execute_phase_0` signature at L84 and delete the corresponding docstring parameter line at L92.</action>
    <action>In `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L79-L148]`, remove lazy `or` fallback expressions `sem = semaphore or asyncio.Semaphore(...)` (specifically at L121, L225, and L404), and remove the `sem` parameter, docstring parameter lines, and `async with sem:` wrapping from ALL four private helpers (specifically and exhaustively: `_extract_ontology_from_chunk` L150 with parameter L151, docstring L160, and wrapping L165; `_extract_atoms_from_chunk` L257 with parameter L266, docstring L278, and wrapping L286; `_extract_drafts_from_chunk_with_retry` L447 with parameter L456, docstring L468, and wrapping L473; `_extract_drafts_from_chunk` L550 with parameter L559, docstring L571, and wrapping L578).</action>
    <action>In `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L180-L255]`, remove `semaphore: asyncio.Semaphore | None = None` parameter from `execute_phase_1` signature at L186, delete docstring parameter line at L195, and remove internal `sem` initialization.</action>
    <action>In `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L358-L437]`, remove `semaphore: asyncio.Semaphore | None = None` parameter from `execute_phase_1_drafts` signature at L364, delete docstring parameter line at L373, and remove internal `sem` initialization.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]`, remove `sem`/`semaphore` arguments from all direct helper and phase calls (L162/L172, L257/L267, L290/L299, L344/L353) in the SAME commit as the atomizer signature change.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_dlq_routing.py#L24-L57]`, remove the `sem = asyncio.Semaphore(1)` fixture and the `sem` argument from the helper call at L48-L53 in the SAME commit as the atomizer signature change.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]`, add positive and negative tests: verify `_extract_ontology_from_chunk` executes without `sem` and verify that passing `sem=asyncio.Semaphore(1)` raises `TypeError`.</action>
  </step>

  <step id="3.2" name="DECOUPLE_ENRICHED_DAG_EXECUTOR">
    <action>In `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]`, remove `semaphore: asyncio.Semaphore | None = None` parameter from `execute_graph` signature at L58 and delete the corresponding docstring parameter line at L70.</action>
    <action>In `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]`, remove ternary fallback `sem = semaphore if semaphore is not None else ...` (L115) and remove `async with sem:` block around `ExtractiveSensorService.evaluate_atom_boolean_batch` at L115-L117.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py]`, add negative test asserting `execute_graph` raises `TypeError` if caller attempts to pass `semaphore=asyncio.Semaphore(1)`.</action>
  </step>

  <step id="3.3" name="DECOUPLE_SLIDING_WINDOW_LINKER">
    <action>In `@[backend_v2/services/orchestrator/sliding_window_linker.py#L9]`, remove unused `import asyncio` (Ruff F401) once concurrency locks are purged.</action>
    <action>In `@[backend_v2/services/orchestrator/sliding_window_linker.py#L195-L353]`, remove `semaphore: asyncio.Semaphore | None = None` parameter from `link_graph` signature at L202 and delete the corresponding docstring parameter line at L212.</action>
    <action>In `@[backend_v2/services/orchestrator/sliding_window_linker.py#L195-L353]`, remove `if semaphore is None: semaphore = ...` fallback (L277-L279) and `sem = semaphore` local chunk lock and internal semaphore wrapping.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]`, add negative test asserting `link_graph` raises `TypeError` if caller attempts to pass `semaphore=asyncio.Semaphore(1)`.</action>
  </step>

  <validation_gate>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/two_pass_atomizer.py backend_v2/services/orchestrator/enriched_dag_executor.py backend_v2/services/orchestrator/sliding_window_linker.py --test --ast-strict`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py backend_v2/tests/unit/services/orchestrator/test_dag_executor_dlq_routing.py backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py -v`</action>
    <action>Assert zero occurrences of "async with sem:" and "async with semaphore:" across two_pass_atomizer.py, enriched_dag_executor.py, and sliding_window_linker.py</action>
  </validation_gate>
</execution_protocol>
```
