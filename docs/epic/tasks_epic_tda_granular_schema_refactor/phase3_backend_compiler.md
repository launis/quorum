# Phase 3: Backend Logic & Prompt Compiler

**Source:** Epic Phase 3 (Backend Logic & Compiler)

## Objective
Update the `localization_compiler.py` to stop sending raw text and start sending strict XML structures to the LLM based on the new granular fields.

## Scope
- **TARGET (Modify):**
  - `backend_v2/services/orchestrator/localization_compiler.py`
  - `backend_v2/tests/integration/test_prompt_compiler.py`
- **CONTEXT (Read-Only):**
  - `backend_v2/models/v2_core.py`

## Architectural Mandates
- **<rule num="51" id="hybrid_prompting_mandate">**: System prompts MUST use a hybrid of XML for structural control and Markdown for nested content formatting.
- **<rule num="29" id="high_fidelity_prompting">**: Prompt core instructions MUST remain completely static to enable Prompt Caching. Dynamic execution variables MUST be isolated within an `<execution_parameters>` tag at the tail of the message. Avoid f-strings when formatting foundational core rules.
- **<rule num="65" id="pep750_t_strings_only">**: Construct dynamic LLM prompts and SQL statements exclusively utilizing Python 3.14 t-strings (Template Strings - PEP 750). The use of standard f-strings within critical data ingestion pathways is categorically forbidden due to inherent injection vulnerability vectors.
- **<rule num="47" id="prompt_compiler_immutability">**: The core logic within `prompt_compiler.py` is locked and static. DO NOT mutate it with ad-hoc patches. *(Exception granted by Epic. Ensure the logic is cleanly replaced, not patched with duct-tape).*

## Implementation Steps
1. Open `backend_v2/services/orchestrator/localization_compiler.py`.
2. Locate the TDA compilation logic (around line 113).
3. Remove the fallback logic that parses `assertion.concept_description` directly into the instructions.
4. Construct the new XML structure using t-strings:
```xml
<tda_validation>
    <anchor_target>{assertion.anchor_target}</anchor_target>
    <search_scope>{assertion.bounding_box_scope}</search_scope>
    <validation_rule>{assertion.extraction_rule}</validation_rule>
</tda_validation>
```
5. Append this XML block cleanly to the prompt context.
6. Open `test_prompt_compiler.py` and update the assertions to expect the new `<tda_validation>` XML structure instead of the old raw string format.

## Testing & Quality Gate Plan
- **Unit/Integration Tests:** `test_prompt_compiler.py` must pass, proving the prompt output matches the new XML standard.
- **Universal Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`. Naked execution of pytest is forbidden.

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_tda_granular_schema_refactor_tracker.md`
