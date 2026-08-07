<system_prompt>
  <objective>Generate Implementation Plan for Phase 3: Service Logic Extraction & Duck-Typing Eradication</objective>
  <context>
    Epic: @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]
  </context>
  
  <execution_protocol level="1_planner">
    <step id="3.0" name="STRATEGIC ALIGNMENT CHECK">
      <action>Verify Phase 2 completed successfully. Ensure `atom_evaluation.py` exists and tests pass.</action>
    </step>
    <step id="3.1" name="STRIP VALIDATION SERVICE IMPORTS">
      <action>In `@[c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py]`, completely remove usage of `AnchorValidationService` and `AliasEngine` from `AtomEvaluationItemDTO._enforce_null_hypothesis_before` and `_enforce_zero_variance_protocols`.</action>
      <demolish>REMOVE: `AnchorValidationService` and `AliasEngine` imports. REMOVE: Execution of heavy service logic from within the `@model_validator` methods.</demolish>
    </step>
    <step id="3.1b" name="REDUCE CONTEXT CONTRACT">
      <action>Reduce the `ValidationInfo.context` contract in `AtomEvaluationItemDTO` to only expect `{"null_hypothesis_blacklist": set[str]}`.</action>
    </step>
    <step id="3.2" name="ERADICATE HASATTR DUCK-TYPING">
      <action>Replace `hasattr(quote, "text")` checks in `evidence_found` properties and validators with strict `quote.text` access.</action>
      <demolish>REMOVE: `hasattr(quote, "text")` patterns at lines 238, 507, 688 of the original file.</demolish>
    </step>
    <step id="3.3" name="ERADICATE DICT AND GET FALLBACKS">
      <action>Replace `isinstance(quote, dict)` and `.get()` fallbacks inside properties and validators with Pydantic typed access.</action>
      <demolish>REMOVE: `isinstance(quote, dict)` and `.get()` patterns. EXCEPTION: keep `isinstance(data, dict)` in `@model_validator(mode="before")`.</demolish>
    </step>
    <step id="3.3b" name="FIX DUPLICATE VALIDATOR BUG">
      <action>Investigate duplicate `@field_validator("chart_display_label", mode="before")` methods on `AtomEvaluationItemDTO` (`truncate_chart_label` vs `_truncate_chart_label`). Delete the redundant one.</action>
    </step>
    <step id="3.4" name="MOVE INLINE IMPORTS">
      <action>Move `import re` statements from inline methods to the global import section of `atom_evaluation.py`.</action>
    </step>
    <step id="3.5" name="REPLACE HARDCODED FINNISH BLACKLISTS">
      <action>Replace hardcoded Finnish arrays (e.g., "ei löydy") in `evidence_found` properties with the injected `_null_hypothesis_blacklist` `PrivateAttr`. Add an `@model_validator(mode="after")` to populate this private attribute from `info.context`.</action>
    </step>
    <step id="3.6" name="CLEANUP MODULE IMPORTS">
      <action>Remove unused module-level imports in `atom_evaluation.py` (e.g., `get_lexical_fuzz_threshold`) if no remaining code references them.</action>
    </step>
    <step id="3.7" name="ATOMIC TEST FIXTURE MIGRATION">
      <action>Update test fixtures in `test_lightweight_matrix.py`, `test_lightweight_matrix_schema.py`, and `test_lazy_llm_simulation.py` to inject `null_hypothesis_blacklist` via `context=` and use instantiated objects instead of raw dictionaries for `exact_quotes`.</action>
    </step>
    <validation_gate>
      Run: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
      Assert: All tests pass with the new strict types and injected context.
    </validation_gate>
  </execution_protocol>
</system_prompt>
