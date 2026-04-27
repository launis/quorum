# Phase 3: PromptBlock-fuusion ja Matriisin Kompilointi

## Tavoite
Varmistaa, että matriisin säännöt, akselit ja kriteerit eivät ylikirjaudu, vaan fuusioituvat onnistuneesti askeleen oman promptin kanssa (PromptBlock Fusion Strategy).

## Arkkitehtuurin Invariantit
- Rule 1: **Prompt Compiler Immutability**: The Prompt Compiler (`prompt_compiler.py`) is frozen. Do NOT touch this file unless explicitly flagged and authorized by the USER via "PERMISSION GRANTED".
- Rule 2: **Mathematical Extrema Anchoring**: Check that the axes dynamically resolve their min/max values (math_min, math_max) based on the scales array, not hardcoded defaults.
- Rule 3: **Hybrid Prompting Mandate**: Ensure XML tags are used for semantic boundaries in the compiler.

## Tiedostot (Scoping)
- **TARGET**: None (Context Only by default, requires permission to edit).
- **CONTEXT**: `backend_v2/services/orchestrator/prompt_compiler.py`

## Työkalut & Verify Plan
- Analyze logic visually.
- `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test`

## Tila
- [x] COMPLETE: Analysoitu ja testit läpäisty. Arkkitehtuurin invariantit toteutuvat.
