# Phase 1: DAG-Riippuvuuksien ja Muuttujien Auditointi

## Tavoite
Varmistaa, että Workflow Engine (`dag_executor.py` & `context_router.py`) purkaa dynaamiset muuttujat (`$steps.X.output`) oikein ja syöttää edellisten askelten raakadatan seuraavien askelten LLM-kontekstiin. Estetään "Orphaned Steps" -ongelma.

## Arkkitehtuurin Invariantit (00-antigravity-core & 01-python-backend)
- Rule 1: **Strict Pydantic V2 Rust**: No naked dicts or legacy fallback hacks. 
- Rule 2: **No Duck Typing / Schema Driven Routing**: Types must be derived from database UI config, not guessed from payload.
- Rule 3: **Fail-Fast**: If an input variable `$steps.step_1.output` cannot be resolved, crash loudly, don't fallback to empty strings.

## Tiedostot (Scoping)
- **TARGET (Modify/Fix if bugs found)**: 
  - `backend_v2/services/orchestrator/dag_executor.py`
  - `backend_v2/services/orchestrator/context_router.py` 
- **CONTEXT (Read-Only)**: 
  - `backend_v2/services/orchestrator/dag_compiler.py`

## Työkalut & Verify Plan
- Run Pytest for orchestrator: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`
- Verify OpenAPI integrity if modifying models.
