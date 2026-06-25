# Phase 3: Kognitiivinen purkutila ja tuplainversio-ansan eliminointi (Cognitive Unlock)

Source: Epic System 2 Variance Analysis Report (Liite 3.3 & 3.4)
Goal: Remove conflicting V1 legacy instructions from the prompt compiler and expand the `reasoning_steps` schema to explicitly demand a mechanical 3-stage audit trace, resolving CoT deprivation.

## Architectural Invariants (from .agents/rules & hardening.xml)
- **Strict Pydantic V2 Rust (Rule 2)**: All models must be strictly validated.
- **Fail-Fast Hydration (Rule 3)**: Prevent raw dictionary states.
- **Prompt Compiler Immutability Exception**: The Epic analysis explicitly mandates removing the V1 double-inversion from `localization_compiler.py`.

## Proposed Changes

### Orchestrator & Models

#### [MODIFY] backend_v2/services/orchestrator/localization_compiler.py (CONTEXT: None)
- **Requirement**: Eliminate the double-inversion trap.
- **Details**: In `compile_xml_rubrics`, find and remove/comment out the legacy V1 instruction that tells the LLM "This is an inverse rule (Vice). If rule_satisfied = True...". The LLM must act purely as an objective sensor without knowing the scoring inversion logic.

#### [MODIFY] backend_v2/models/dtos/evaluation_steps.py (CONTEXT: None)
- **Requirement**: Fix CoT deprivation by modifying the `reasoning_steps` description.
- **Details**: Update the `Field(description=...)` for `reasoning_steps` in `StepDTOStrict` (and `StepDTOSemantic` if applicable) to demand a 3-stage trace: "Step-by-step mechanical audit trace BEFORE making a decision. Format: '1) Rule requires X. 2) Text provides Y. 3) Y meets/fails X.' Max 3 sentences." Remove the old "Max 1 short sentence" limitation.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/localization_compiler.py backend_v2/models/dtos/evaluation_steps.py --test`
- Verify prompt generation output in tests does not contain the "Vice" string.

---
**Session Handover**
To execute this phase, please start a NEW chat session and run:
`/tier5-resume --target docs/epic/system2_variance_analysis_report_tracker.md`
