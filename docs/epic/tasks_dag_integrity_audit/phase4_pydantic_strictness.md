# Phase 4: De-Generator ja Fail-Fast Pydantic Suojaus

## Tavoite
Varmistaa, että malleissa käytetään Pydantic V2 `extra='forbid'` -suojausta, jotta LLM:n mahdolliset hallusinaatiot uusista matriisiakseleista tai kentistä kaatavat suorituksen hallitusti (Token Shield), eivätkä vuoda tietokantaan.

## Arkkitehtuurin Invariantit
- Rule 1: **Strict Pydantic V2 Rust**: `model_config = ConfigDict(extra='forbid', strict=True)`
- Rule 2: **Zero Legacy Fallback Hacks**: No silent scrubbing of unknown fields to appease extra='forbid'.
- Rule 3: **No Naked Dicts in State**: Data crossing boundaries must be `.model_validate()` checked.

## Tiedostot (Scoping)
- **TARGET**: 
  - `backend_v2/models/dto/execution.py`
  - `backend_v2/llm/client.py` (if structural outputs configured here)
- **CONTEXT**: `backend_v2/llm/parsers.py` (if exists)

## Työkalut & Verify Plan
- `uv run python scripts/backend_audit_loop.py backend_v2/models/ --openapi`
