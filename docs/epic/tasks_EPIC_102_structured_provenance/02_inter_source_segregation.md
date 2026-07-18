# Phase 2: Inter-Source Segregation & Global Directives

This plan implements Epic 102 Phase 2b and Phase 3. It dynamically wraps source texts in `<user_payload>` or `<ai_draft_context>` based on their origin (`$inputs.*` vs `$steps.*`), and injects the semantic directives instructing the LLM to obey these tags.

## Architectural Rules Injected
- **01-python-backend.md**: `prompt_fragmentation_ban`
- **05_llm_architecture.md**: `xml_structural_sovereignty_mandate`, `high_fidelity_prompting_and_caching`

## User Review Required
> [!WARNING]
> Modifying `prompt_compiler.py` violates the `prompt_compiler_immutability` rule. The executing agent MUST explicitly ask the user for permission before modifying this file.

## Proposed Changes

### Backend Core
#### [MODIFY] [global_mandates.py](file:///c:/src/quorum/backend_v2/models/prompts/global_mandates.py)
**Changes:**
1. Define a new constant `CONTEXT_SEGREGATION_MANDATE`:
```python
CONTEXT_SEGREGATION_MANDATE = (
    "<context_segregation_mandate>\n"
    "You are evaluating the HUMAN USER's intent. Text enclosed in <ai_draft_context> is for "
    "background reference ONLY (Read-Only). You MUST NOT extract quotes or derive user intent "
    "from the AI context. You MUST ONLY extract evidence and evaluate intent from the <user_payload> "
    "(Write-Intent).\n"
    "</context_segregation_mandate>"
)
```

#### [MODIFY] [localization_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/localization_compiler.py)
**Changes:**
1. Import `CONTEXT_SEGREGATION_MANDATE` from `backend_v2.models.prompts.global_mandates`.
2. In `compile_static_instructions()`, explicitly append `CONTEXT_SEGREGATION_MANDATE.strip()` to the final compiled string list so it is included as a static directive.

#### [MODIFY] [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py)
**Changes:**
1. In `build_xml_context`, populate `input_meta_map` with a new key `is_chat_history: bool` derived from `ei.is_chat_history`.
2. When iterating over `input_mappings` and extracting `value`:
   - Identify if `source_path` originated from `$inputs` or `$steps`.
   - **CRITICAL**: To prevent the Nested Provenance Trap for deep paths (e.g., `$inputs.chat_log.turns`), extract the base key (e.g., `$inputs.chat_log`) from `source_path` to correctly resolve `is_chat_history` from `input_meta_map`.
   - If from `$inputs` and `is_chat_history` is False: wrap `value` in `<user_payload>...</user_payload>`.
   - If from `$inputs` and `is_chat_history` is True: do NOT wrap `value` (it already contains intra-chat tags).
   - If from `$steps`: wrap `value` in `<ai_draft_context>...</ai_draft_context>`.
   - Ensure these wrapped values are placed cleanly inside the encapsulating `<matrix_input>` block.

## Destructive Operation Inventory
N/A

## Documentation & Knowledge Item Mandate
- No structural directory changes made.

## Testing & Quality Gate Plan
- Unit tests: Add/modify tests to verify `$inputs` vs `$steps` origin tagging in the compiler.
- Verify `CONTEXT_SEGREGATION_MANDATE` static injection.
- Run Universal Quality Gate (Backend Audit Loop) on `backend_v2/services/orchestrator/` and `backend_v2/models/prompts/`.

## Session Handover Context
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
