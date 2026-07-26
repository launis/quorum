# Phase 2: Orchestration & TDA Engine Context-Enriched Pipeline

> Source: Epic 118, Phase 2 (Steps 2.1 + 2.2)

## Objective

Wire `shuffled_atoms` through `LLMNodeStrategy` into `EngineExecutionRequest`, and implement the **Context-Enriched Decompose-Verify Pipeline** in `TDAEngine.execute()` — the core fix that preserves original `tda_id` values for `matrix_scoring_hook` correlation.

## PERMISSION GRANTED to mutate DAG Orchestrator ecosystem

Per `orchestrator_god_object_fragility`, this Epic explicitly grants permission to mutate the DAG Orchestrator ecosystem.

---

## Baseline Verification (MANDATORY FIRST STEP)

Before modifying any files, record the current test state:

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/tda_engine.py --test
```

Record the passing test count and coverage as `[BASELINE]`.

---

## Step 2.1: Wire `shuffled_atoms` through `LLMNodeStrategy`

### Scope
- **TARGET (Modify):** @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]
- **CONTEXT (Read-Only):** @[c:\src\quorum\backend_v2\models\dtos\engine.py], @[c:\src\quorum\backend_v2\hooks\atom_flattening.py]

### Actions

1. Add import at top of file:
   ```python
   from pydantic import TypeAdapter
   from backend_v2.models.dtos.engine import FlattenedAtom
   ```

2. **Fail-Fast Hydration**: Locate the section where `is_matrix_step` is determined (around line 403-408). Replace the existing defensive `"shuffled_atoms" in state_data` check with **unconditional direct key access** when `is_matrix_step` is True:
   ```python
   # Fail-Fast Hydration Mandate: If is_matrix_step, shuffled_atoms MUST exist.
   # KeyError → 500 if atom_flattening_hook failed to inject.
   if is_matrix_step:
       raw_atoms = state_data["shuffled_atoms"]
       # python_314_root_model_ban: Always use TypeAdapter for array validation
       hydrated_shuffled_atoms = TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False)
   else:
       hydrated_shuffled_atoms = None
   ```

3. **Pass into BOTH `EngineExecutionRequest` constructor calls**: The file has TWO instantiations of `EngineExecutionRequest` — one for `is_synthesis_step` (around line 625) and one for the regular path (around line 641). Add `shuffled_atoms=hydrated_shuffled_atoms` to **both** constructors.

4. Update the existing `has_shuffled_atoms` variable to derive from the hydrated result:
   ```python
   has_shuffled_atoms = hydrated_shuffled_atoms is not None and len(hydrated_shuffled_atoms) > 0
   ```

### Invariants
- `fail_fast_hydration_mandate`: Unconditional `state_data["shuffled_atoms"]` key access (no `.get()` or `in` checks).
- `python_314_root_model_ban`: Use `TypeAdapter(list[FlattenedAtom]).validate_python()` for array validation.
- `pydantic_pure_hydration_boundary`: Use `strict=False` since `state_data` contains raw dicts from TinyDB serialization.
- Both `EngineExecutionRequest` constructor calls must include `shuffled_atoms`.

### FORBIDDEN
- `dict.get()` defensive access for `shuffled_atoms` during the initial schema compilation.
- Modifying the chunking logic later in the file (around line 469). It correctly chunks the raw `state_data["shuffled_atoms"]` dicts. Leave it unchanged.
- `asyncio.gather`
- `isinstance()` duck-typing checks for atom validation
- Any changes to the prompt compilation logic

---

## Step 2.2: Implement Context-Enriched Decompose-Verify Pipeline in `TDAEngine`

### Scope
- **TARGET (Modify):** @[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]
- **CONTEXT (Read-Only):** @[c:\src\quorum\backend_v2\models\dtos\dag_models.py#L46-L100], @[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py], @[c:\src\quorum\backend_v2\services\orchestrator\two_pass_atomizer.py], @[c:\src\quorum\backend_v2\services\orchestrator\sliding_window_linker.py], @[c:\src\quorum\backend_v2\services\orchestrator\result_projector.py]

### Actions

1. Add import for `Final` from `typing`:
   ```python
   from typing import TYPE_CHECKING, Any, Final
   ```

2. Add import for DAG models:
   ```python
   from backend_v2.models.dtos.dag_models import LinkedAtomGraph, ExtractedAtom
   ```

3. Add module-level sentinel constant (`zero_db_hardcoding_mandate`):
   ```python
   _MATRIX_SOURCE_SENTINEL: Final[str] = "MATRIX"
   ```

4. **Modify `TDAEngine.execute()`** to implement the dual-path architecture. After Phase 0 + Phase 1 complete (ontology + atoms extraction), add the branching logic:

   **If `request.shuffled_atoms` is present (Matrix path):**
   - Construct `evaluation_context` by combining:
     - Enriched facts from Phase 1 atoms (wrapped in `<context><enriched_facts><fact>...</fact></enriched_facts>`)
     - Original `hydrated_text` with `[B0]`, `[B1]` AliasEngine block tags (wrapped in `<source_text>`)
   - Map predefined matrix atoms from `request.shuffled_atoms` into `LinkedAtomGraph` nodes:
     - `ExtractedAtom` uses `is_logical_deduction=True` (allows `source_quote=None` for matrix assertions)
     - `tda_id=flat_atom.atom_id` (preserves original predefined UUID)
     - `source_id=_MATRIX_SOURCE_SENTINEL` (module-level constant)
     - `source_sequence_index=i` (Python-injected index)
   - Skip `SlidingWindowLinker` (matrix assertions are independent — no inter-atom dependencies)
   - Pass `evaluation_context` as `source_text` to `EnrichedDagExecutor.execute_graph()`

   **If `request.shuffled_atoms` is None (Regular path):**
   - Preserve existing behavior: `SlidingWindowLinker` + `global_source_text`

5. **Adjust progress callback ranges for Matrix path:**
   - Skip linker allocation (35-60%) → redistribute to DAG execution:
     - Phase 0: 0-15%
     - Phase 1: 15-35%
     - DAG execution: 35-100% (Matrix path) vs 60-100% (Regular path)

6. Update docstring to document the dual-path architecture.

### Key Pseudocode Reference

```python
_MATRIX_SOURCE_SENTINEL: Final[str] = "MATRIX"

# Inside execute(), AFTER Phase 0+1 complete:
if request.shuffled_atoms:
    # MATRIX PATH: Evaluate predefined matrix atoms against enriched context.
    # xml_structural_sovereignty_mandate: Use rigid XML tags.
    # atom_aliasing_hydration_mandate: Exclude raw tda_id from LLM prompt text.
    enriched_claims = "\n".join(f"<fact>{a.resolved_claim}</fact>" for a in atoms)
    evaluation_context = (
        "<context>\n"
        "<enriched_facts>\n"
        f"{enriched_claims}\n"
        "</enriched_facts>\n"
        "<source_text>\n"
        f"{hydrated_text}\n"
        "</source_text>\n"
        "</context>"
    )
    
    nodes: list[LinkedAtomGraph] = []
    for i, flat_atom in enumerate(request.shuffled_atoms):
        ext_atom = ExtractedAtom(
            reasoning="Predefined matrix assertion",
            resolved_claim=flat_atom.question,
            is_logical_deduction=True,
            source_quote=None,
            tda_id=flat_atom.atom_id,
            source_id=_MATRIX_SOURCE_SENTINEL,
            source_sequence_index=i,
        )
        nodes.append(LinkedAtomGraph(atom=ext_atom, depends_on=[]))
    
    # Adjusted progress for matrix path (skip linker)
    async def dag_progress_matrix(completed: int, total: int) -> None:
        if request.progress_callback:
            prog = 35 + int((completed / total) * 65)
            await request.progress_callback(prog, 100)
    
    states = await dag_executor.execute_graph(
        nodes, evaluation_context, request.target_locale,
        progress_callback=dag_progress_matrix, semaphore=request.semaphore,
    )
else:
    # REGULAR TDA PATH: Uses SlidingWindowLinker + global_source_text.
    nodes = await linker.link_graph(...)
    states = await dag_executor.execute_graph(
        nodes, global_source_text, request.target_locale,
        progress_callback=dag_progress, semaphore=request.semaphore,
    )
```

### Invariants
- `atom_aliasing_hydration_mandate`: Raw `tda_id` UUIDs are NOT exposed in the LLM prompt text — only the `flat_atom.question` is passed to `resolved_claim`.
- `high_fidelity_prompting`: `evaluation_context` with `<context>` at the top of the prompt for O(1) Cache Survival.
- `xml_structural_sovereignty_mandate`: Use rigid XML tags (`<context>`, `<enriched_facts>`, `<fact>`, `<source_text>`).
- `zero_db_hardcoding_mandate`: Use `_MATRIX_SOURCE_SENTINEL` module-level constant instead of hardcoded strings.
- `frozen_state_mutability`: `ExtractedAtom` and `LinkedAtomGraph` remain frozen.
- `python_314_modern_syntax`: Use `asyncio.TaskGroup` (already used by `EnrichedDagExecutor`).

### FORBIDDEN
- Raw dict state passing
- `asyncio.gather`
- Exposing raw `tda_id` UUIDs to the LLM prompt
- Modifying `EnrichedDagExecutor`, `ResultProjector`, or `prompt_compiler.py`
- Any changes to the Regular TDA path behavior

---

## Testing & Quality Gate Plan

### Unit Tests (Location: @[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\engines\test_tda_engine.py])

### Positive Scenarios
1. **`test_tda_engine_matrix_path`:**
   - **Input**: `EngineExecutionRequest` with `shuffled_atoms` populated with predefined matrix assertions (list of `FlattenedAtom`).
   - **Expected Output**: `EnrichedDagExecutor.execute_graph()` is called with the original matrix atoms and the concatenated `evaluation_context` (containing extracted facts and original `[B0]` tags). `SlidingWindowLinker.link_graph()` is NOT called.

2. **`test_tda_engine_no_shuffled_atoms_unchanged`:**
   - **Input**: `EngineExecutionRequest` where `shuffled_atoms` is `None`.
   - **Expected Output**: `SlidingWindowLinker.link_graph()` IS called. The existing pipeline operates identically.

### Negative Scenarios (Minimum 2)
1. **`test_llm_strategy_missing_atoms_crash`:**
   - **Input**: `is_matrix_step` is True, but `"shuffled_atoms"` is completely missing from `state_data`.
   - **Expected Output**: Native `KeyError` is raised in `llm.py`, fulfilling the Fail-Fast Hydration mandate.

2. **`test_tda_engine_invalid_shuffled_atoms_type`:**
   - **Input**: `is_matrix_step` is True, `state_data["shuffled_atoms"]` contains invalid data (e.g., list of plain strings instead of dicts).
   - **Expected Output**: Pydantic `ValidationError` is raised during `TypeAdapter(list[FlattenedAtom]).validate_python()`.

### Audit Commands

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/tda_engine.py --test
```

### Atomic Commit

After passing audit, commit:
```powershell
git add backend_v2/services/orchestrator/strategies/llm.py backend_v2/services/orchestrator/engines/tda_engine.py
git add backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py
git commit -m "feat: implement context-enriched decompose-verify pipeline for matrix TDA evaluation"
```

### MANDATORY Final E2E REST API Verification Gate

```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```
