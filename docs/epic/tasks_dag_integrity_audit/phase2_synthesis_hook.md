# Phase 2: SynthesisHookin Todisteketju

## Tavoite
Varmistaa, että `SynthesisHook` rakentaa lopullisen Executive Summaryn lukemalla *kaikkien* suoritettujen askeleiden tulokset (`state.metadata.step_results`) ja injektoimalla ne Chief Editor -mallin kontekstiin, jotta yksikään askel ei valu hukkaan.

## Arkkitehtuurin Invariantit
- Rule 1: **English-Only Mandate**: Synthesis output must be forced in English natively before TranslationHook.
- Rule 2: **LLM Structured Execution Mandate**: Use `LLMClient.from_strategy()` and explicit XML blocks for fencing user inputs/step results.
- Rule 3: **Fail-Fast**: If `step_results` is empty or corrupted, raise AppException, do not return empty report.

## Tiedostot (Scoping)
- **TARGET**: `backend_v2/hooks/synthesis.py`
- **CONTEXT**: `backend_v2/models/dto/execution.py`

## Työkalut & Verify Plan
- `uv run python scripts/backend_audit_loop.py backend_v2/hooks/synthesis.py --test`
