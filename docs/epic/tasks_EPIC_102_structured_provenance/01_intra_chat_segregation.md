# Phase 1: Intra-Chat Role Segregation

This plan implements Epic 102 Phase 2a. The goal is to wrap AI turns in `<ai_draft_context>` and User turns in `<user_payload>` inside `input_processing.py`.

## Architectural Rules Injected
- **00-antigravity-core.md**: `surgical_precision_edits`
- **01-python-backend.md**: `no_naked_dicts_in_state`

## User Review Required
No major architectural shifts; modifying an existing hook.

## Proposed Changes

### Backend Core
#### [MODIFY] [input_processing.py](file:///c:/src/quorum/backend_v2/hooks/input_processing.py)
**Changes:**
1. In `process_inputs()`, remove the JSON check `and not resolved_text.strip().startswith("{")` for chat history.
2. Remove the global `smooth_text` and `mask_pii` step calls for chat inputs inside `process_inputs()`. 
3. Modify the signature of `_process_chat_history()` to accept `enable_semantic_smoothing: bool`, `enable_eager_anonymization: bool`, and `language: str`. Pass these from `process_inputs()`.
4. In `_process_chat_history()`:
   - If `resolved_text` starts with `{` or `[`, attempt to parse it directly using `ChatHistoryDTO.model_validate_json(resolved_text)`. Do NOT run NLP in this success path.
   - Catch both `ValidationError` and `ValueError` to ensure any malformed JSON strings safely fall back to treating it as raw text.
   - For raw text (or fallback), run the NLP steps (`pii_service.smooth_text` and `pii_service.mask_pii` if enabled) on the entire string FIRST. **CRITICAL**: You MUST use `await asyncio.to_thread()` for these NLP calls to prevent blocking the async event loop (SpaCy is CPU-bound). Then pass it to `ChatParserService.parse_pasted_chat()`.
   - In the `combined` output, wrap AI turns in `<ai_draft_context>...</ai_draft_context>` and User turns in `<user_payload>...</user_payload>`, completely removing the `**role**: ` prefix.
   - For the `user_only` and `ai_only` return strings, do NOT wrap them in XML tags. Keep them as pure text (they are only used internally by Python metrics hooks, not the LLM).

## Destructive Operation Inventory
N/A

## Documentation & Knowledge Item Mandate
- No structural directory changes made. 

## Testing & Quality Gate Plan
- Unit tests: Add/modify tests in `tests/unit/hooks/test_input_processing.py` to verify XML tagging and the NLP bypass for JSON.
- Run Universal Quality Gate (Backend Audit Loop) on `backend_v2/hooks/`.
- Ensure baseline metrics are recorded before modification.

## Session Handover Context
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
