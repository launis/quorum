# EPIC 142 Phase 5: Pydantic Schema CoT Ordering Audit & Fix

## Objective
To restore analytical rigor by reordering Pydantic schema fields in `StepDTOStrict` and `StepDTOSemantic` so that logical reasoning fields explicitly precede final decision boolean flags (Chain-of-Thought ordering). This forces the autoregressive LLM to generate analytical tokens before committing to a final outcome.

## Scope
### TARGET FILES
- @[backend_v2/models/dtos/evaluation_steps.py]

### [MODIFY] `backend_v2/models/dtos/evaluation_steps.py`
- Swap the positions of `decision` and `semantic_reasoning` in `StepDTOStrict`.
- Swap the positions of `contextual_override` and `override_reason` in `StepDTOSemantic`.

```xml
<execution_protocol level="2_execute">
  <step id="1" name="REORDER STEPDTOSTRICT CoT FIELDS">
    <action>In @[backend_v2/models/dtos/evaluation_steps.py], move the `decision` field to be defined explicitly AFTER the `semantic_reasoning` field within the `StepDTOStrict` class.</action>
    <constraint invariant="zero_duct_tape">Ensure no other structural changes are made. Only reorder the two fields.</constraint>
  </step>
  
  <step id="2" name="REORDER STEPDTOSEMANTIC CoT FIELDS">
    <action>In @[backend_v2/models/dtos/evaluation_steps.py], move the `contextual_override` field to be defined explicitly AFTER the `override_reason` field within the `StepDTOSemantic` class.</action>
    <constraint invariant="zero_duct_tape">Ensure no other structural changes are made to the class attributes or defaults.</constraint>
  </step>

  <step id="3" name="QUALITY GATE &amp; VERIFICATION">
    <action>Run the backend audit loop on the modified file: `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/evaluation_steps.py --test`</action>
    <action>Ensure full test suite coverage is maintained, specifically verifying `test_epic93_contract_verification.py` and downstream synthesis tests.</action>
    <constraint invariant="quality_gate_execution">Ensure all tests pass.</constraint>
  </step>
</execution_protocol>
```
