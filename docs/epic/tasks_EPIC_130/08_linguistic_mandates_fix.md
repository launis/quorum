# Phase 8: Linguistic Mandates Fix

**Overview:** Ensure all dynamically generated synthesis strings (like `cited_sources` and `row_explanation`) are strictly translated into the user's `target_locale`. Fix the loophole where the LLM defaults to English for deep JSON structures.

**Source:** User feedback regarding untranslated outputs in the synthesis phase.

**Target Files:**
- `c:\src\quorum\backend_v2\models\prompts\field_prompts.py` [MODIFY]
- `c:\src\quorum\backend_v2\models\dtos\synthesis.py` [MODIFY]
- `C:\Users\risto\.gemini\antigravity-ide\knowledge\domain_model_prompt_separation\artifacts\ki_domain_model_prompt_separation.md` [MODIFY]

```xml
<execution_protocol>
  <dod_checklist>
    <item>Create `DESC_TRANSLATION_MANDATE` in `field_prompts.py`.</item>
    <item>Apply `DESC_TRANSLATION_MANDATE` to user-facing fields in `SynthesisOutputDTO` (and sub-DTOs) inside `synthesis.py`.</item>
    <item>Update `ki_domain_model_prompt_separation.md` to enforce the Pydantic field translation mandate using `linguistic_directives.py` and `field_prompts.py`.</item>
    <item>Run tests to verify Pydantic schemas are intact.</item>
  </dod_checklist>

  <step id="1" name="Global Field Mandate">
    <action>Modify `field_prompts.py` to add `DESC_TRANSLATION_MANDATE = "MUST BE TRANSLATED TO <required_output_language>!"`.</action>
  </step>

  <step id="2" name="Enforce Mandate in Synthesis Schema">
    <action>Modify `synthesis.py` to interpolate `DESC_TRANSLATION_MANDATE` into the `Field(description=...)` of `cited_sources`, `user_role`, `user_role_justification`, `XaiHighlightItem.content`, and `SynthesisRowExplanationDTO.row_explanation`.</action>
  </step>

  <step id="3" name="Update Knowledge Item">
    <action>Modify `ki_domain_model_prompt_separation.md` to add `pydantic_field_translation_mandate`.</action>
  </step>
</execution_protocol>
```
