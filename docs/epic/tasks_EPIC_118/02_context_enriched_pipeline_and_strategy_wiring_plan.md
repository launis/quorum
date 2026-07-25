# Phase 2: Context-Enriched Pipeline & Strategy Wiring

> **Source**: EPIC 118 — Phase 2 (Orchestration) + Phase 4 (TDA Engine Implementation) + Phase 5 (Documentation)
> **Scope**: Implement the Context-Enriched Decompose-Verify pipeline in `TDAEngine`, wire `shuffled_atoms` via Fail-Fast hydration in `llm.py`, and write all 4 TDD test cases.

---

## Objective

Fix the root cause production bug: `matrix_scoring_hook` finds zero atom matches because `TDAEngine` generates new UUIDs instead of using predefined `tda_id` values. The fix:

1. `llm.py` passes `shuffled_atoms` to `EngineExecutionRequest` via Fail-Fast unconditional key access.
2. `TDAEngine` uses Phase 0+1 (ontology + anaphora resolution) to generate enriched context, then evaluates the **original predefined matrix atoms** against that context (preserving `tda_id`).
3. `matrix_scoring_hook` then successfully correlates results via `tda_id` matching.

---

## Architectural Invariants Applied

| Rule ID | Enforcement |
|:--------|:------------|
| `orchestrator_god_object_fragility` | PERMISSION GRANTED required — EPIC 118 explicitly grants this per §2.1. |
| `fail_fast_hydration_mandate` | `state_data["shuffled_atoms"]` — unconditional key access, no `.get()`. |
| `python_314_root_model_ban` | `TypeAdapter(list[FlattenedAtom]).validate_python()` instead of `RootModel`. |
| `zero_db_hardcoding_mandate` | `_MATRIX_SOURCE_SENTINEL: Final[str] = "MATRIX"` as module-level constant. |
| `xml_structural_sovereignty_mandate` | Enriched context uses `<context>`, `<enriched_facts>`, `<fact>`, `<source_text>` XML tags. |
| `atom_aliasing_hydration_mandate` | `tda_id` is NOT exposed to LLM — only the `resolved_claim` text is passed in `<fact>` tags. |
| `high_fidelity_prompting_and_caching` | `full_context` placed at absolute top of prompt (`<context>`) for O(1) Cache Survival. |
| `topological_evaluator_ssot` | `EnrichedDagExecutor.execute_graph()` remains the SSOT for DAG evaluation. |
| `engine_dto_strictness` | Input/output strictly via `EngineExecutionRequest` / `EngineExecutionResult`. |
| `engine_exception_acl` | All exceptions wrapped in `AppException` before re-raising. |

---

## Target Files (Modify)

### [MODIFY] [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py)

**Current State** (verified at @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py#L403-L409]):
- Lines 403-408: Uses `"shuffled_atoms" in state_data` check with `isinstance` guard.
- Lines 469-488: Second check for chunking — also uses `"shuffled_atoms" in state_data`.
- Lines 602-655: `EngineExecutionRequest` construction — does NOT pass `shuffled_atoms`.

**Changes**:

1. **Import `FlattenedAtom` and `TypeAdapter`** at file top:
   ```python
   from pydantic import TypeAdapter
   from backend_v2.models.dtos.engine import FlattenedAtom
   ```

2. **Replace the EngineExecutionRequest construction** (both `is_synthesis_step` and regular paths, lines 625-655) to include `shuffled_atoms`:
   - For the regular (non-synthesis) path:
     ```python
     # Fail-Fast Hydration Mandate: If is_matrix_step, shuffled_atoms MUST exist.
     # KeyError → 500 if atom_flattening_hook failed upstream.
     if is_matrix_step:
         raw_atoms = state_data["shuffled_atoms"]
         # python_314_root_model_ban: Always use TypeAdapter for array validation.
         hydrated_shuffled_atoms = TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False)
     else:
         hydrated_shuffled_atoms = None

     engine_request = EngineExecutionRequest(
         ...,
         shuffled_atoms=hydrated_shuffled_atoms,
         ...
     )
     ```
   - For the synthesis path: pass `shuffled_atoms=None` (synthesis steps never have matrix atoms).

**CRITICAL**: The existing `has_shuffled_atoms` boolean logic (line 403-408) and the chunking logic (lines 469-488) MUST be preserved as-is — they control prompt compilation and chunking, not engine routing. The ONLY change is adding `shuffled_atoms` to `EngineExecutionRequest` construction.

---

### [MODIFY] [tda_engine.py](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py)

**Current State** (verified at @[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py#L40-L149]):
- `execute()` always runs: Phase 0 → Phase 1 → `SlidingWindowLinker.link_graph()` → `EnrichedDagExecutor.execute_graph(global_source_text)` → `ResultProjector.project()`.
- No conditional path for predefined matrix atoms.
- `execute_graph()` receives `global_source_text` as the `source_text` parameter.

**Changes**:

1. **Add imports** at file top:
   ```python
   from typing import Final
   from backend_v2.models.dtos.dag_models import LinkedAtomGraph, ExtractedAtom
   ```

2. **Add module-level sentinel constant**:
   ```python
   _MATRIX_SOURCE_SENTINEL: Final[str] = "MATRIX"
   ```

3. **Implement bifurcation AFTER Phase 0+1** (after `atoms.sort(...)`, line 112):
   ```python
   # Context-Enriched Decompose-Verify Pipeline
   if request.shuffled_atoms:
       # MATRIX PATH: Use enriched context from Phase 0+1 to evaluate predefined matrix atoms.
       # The enriched context resolves anaphora (S2A) while preserving original tda_id UUIDs.

       # xml_structural_sovereignty_mandate: Use rigid XML tags instead of markdown.
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

       states = await dag_executor.execute_graph(
           nodes,
           evaluation_context,  # Enriched context replaces raw source text
           request.target_locale,
           progress_callback=dag_progress,
           semaphore=request.semaphore,
       )
   else:
       # REGULAR TDA PATH: Use global_source_text for standard extraction.
       nodes = await linker.link_graph(
           llm_executor,
           request.bound_client,
           atoms,
           ontology,
           progress_callback=linker_progress,
           semaphore=request.semaphore,
       )
       states = await dag_executor.execute_graph(
           nodes,
           global_source_text,
           request.target_locale,
           progress_callback=dag_progress,
           semaphore=request.semaphore,
       )
   ```
4. `ResultProjector.project(nodes, states)` remains identical for both paths.

**Producer-Consumer Verification**:
| Producer | Data | Consumer |
|:---------|:-----|:---------| 
| `atom_flattening.py` hook | `shuffled_atoms` list in `state_data` | `llm.py` → `EngineExecutionRequest.shuffled_atoms` |
| `TwoPassAtomizer` Phase 0+1 | `ontology` + `atoms` (enriched context) | `TDAEngine` → constructs `evaluation_context` string |
| `TDAEngine` | `LinkedAtomGraph` nodes with original `tda_id` | `EnrichedDagExecutor.execute_graph()` |
| `ResultProjector` | Results with preserved `tda_id` | `matrix_scoring_hook` |

---

## Context Files (Read-Only)

| File | Purpose |
|:-----|:--------|
| @[c:\src\quorum\backend_v2\models\dtos\engine.py] | `FlattenedAtom` + `EngineExecutionRequest` (Phase 1 modified). |
| @[c:\src\quorum\backend_v2\models\dtos\dag_models.py] | `ExtractedAtom`, `LinkedAtomGraph` — DAG graph construction. |
| @[c:\src\quorum\backend_v2\services\orchestrator\engines\base.py] | `ExecutionEngine` protocol. |
| @[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py] | `execute_graph(nodes, source_text, ...)` — verify signature. |
| @[c:\src\quorum\backend_v2\services\orchestrator\result_projector.py] | `ResultProjector.project()` — verify node/state contract. |
| @[c:\src\quorum\backend_v2\services\orchestrator\two_pass_atomizer.py] | Phase 0 + Phase 1 interface — verify return types. |
| @[c:\src\quorum\backend_v2\hooks\scoring.py#L514-L560] | `matrix_scoring_hook` — verify `tda_id` correlation logic. |
| @[c:\src\quorum\backend_v2\hooks\atom_flattening.py] | `FlatteningHookOutput` — verify `state_delta` structure. |
| @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\prompt_factory.py] | Verify `has_shuffled_atoms` consumption. |

---

## Testing & Quality Gate Plan

### Baseline Capture (MANDATORY FIRST STEP)
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines --test
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies --test
```
Record the passing test count and coverage as `[BASELINE]`.

### Unit Tests (4 TDD Scenarios — EPIC 114 Shift-Left)

All tests go in @[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\engines\test_tda_engine.py].

#### ✅ Success Scenario 1: `test_tda_engine_matrix_path`
- **Input**: `EngineExecutionRequest` with `shuffled_atoms` populated with predefined matrix assertions.
- **Expected**: `EnrichedDagExecutor.execute_graph()` is called with `LinkedAtomGraph` nodes containing original `tda_id` values and concatenated `evaluation_context` (containing `<enriched_facts>` and original `[B0]` tags).
- **Verification**: `SlidingWindowLinker.link_graph()` is NOT called. `ResultProjector.project()` receives the nodes with preserved `tda_id`.

#### ✅ Success Scenario 2: `test_tda_engine_no_shuffled_atoms_unchanged`
- **Input**: `EngineExecutionRequest` where `shuffled_atoms` is `None` (Regular TDA Path).
- **Expected**: `SlidingWindowLinker.link_graph()` IS called. Pipeline operates identically to pre-fix behavior.

#### ❌ Failure Scenario 1: `test_llm_strategy_missing_atoms_crash`
- **Location**: New test in @[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\strategies\test_llm_strategy.py] (or existing test file for LLM strategy).
- **Input**: `is_matrix_step` is True, but `"shuffled_atoms"` is completely missing from `state_data`.
- **Expected**: Native `KeyError` is raised in `llm.py`, fulfilling the Fail-Fast Hydration mandate.

#### ❌ Failure Scenario 2: `test_tda_engine_invalid_shuffled_atoms_type`
- **Input**: `is_matrix_step` is True, `state_data["shuffled_atoms"]` contains invalid data (list of strings instead of dicts).
- **Expected**: Pydantic `ValidationError` is raised during `TypeAdapter(list[FlattenedAtom]).validate_python()` coercion.

### Quality Gate Commands
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py --test
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines --test
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies --test
```

### MANDATORY Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## Documentation Mandate (EPIC 115 Compliance)

After implementation and test verification:

1. **Create KI**: `ki_context_enriched_decompose_verify.md` in `<appDataDir>\knowledge\context_enriched_pipeline\artifacts\`.
   - Document the Context-Enriched Decompose-Verify pattern.
   - Reference: Phase 0/1 for enriched context → preserving original `tda_id` → `EnrichedDagExecutor` evaluation.
2. **Do NOT manually edit** `docs/architecture/` pillars.
3. Instruct the user to run `/tier7-describe-architecture` after KI creation.
