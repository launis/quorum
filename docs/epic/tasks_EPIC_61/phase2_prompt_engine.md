# Implementation Plan - Phase 2: Prompt Engine Hardening

This sub-plan focuses on the global prompt level directives. It updates both the `GLOBAL_HARDENING_FRAMEWORK` inside `system_directives.py` (which governs matrix and claim evaluations) and the blind system instruction inside `prompt_compiler.py` (which governs blind TDA evaluations) by appending the zero-trust negative condition matching rule.

## Architectural Rules Applied
- **Rule 1 (Prompt Compiler Immutability)**: The Prompt Compiler is a frozen architectural cornerstone. Do not edit unless strictly necessary. In this plan, we modify it to append a critical system directive to `compile_blind_system_instruction` with strict bounds.
- **Rule 2 (No Naked Dicts / Type Ignores)**: Maintain absolute type-safety when passing data.

## Proposed Changes

### Component: Prompt Compiler & Global Directives

#### [MODIFY] [system_directives.py](file:///c:/src/quorum/backend_v2/core/system_directives.py)

##### Milestone 2.1: Harden `GLOBAL_HARDENING_FRAMEWORK`
- **Source**: Epic Phase 2, Step 1
- **File Range**: `backend_v2/core/system_directives.py` lines 8 to 14
- **Change**: Append a new rule to `GLOBAL_HARDENING_FRAMEWORK` to enforce zero-trust matching for negative conditions and flaws:
  ```xml
  <rule>ZERO-TRUST NEGATIVE CONDITION MATCHING: When evaluating negative conditions or presence of flaws (vice rules), you must look ONLY for physical semantic matches. If the text does not contain the exact physical anchors defined in the rule, you MUST return JSON null. Speculation, extrapolation, or rationalizing away missing evidence is strictly banned.</rule>
  ```

---

### Component: Orchestrator Service

#### [MODIFY] [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py)

##### Milestone 2.2: Harden `compile_blind_system_instruction`
- **Source**: Epic Phase 2, Step 1
- **File Range**: `backend_v2/services/orchestrator/prompt_compiler.py` lines 862 to 880
- **Change**: Append a new rule to the `<rules>` list in the `compile_blind_system_instruction` prompt:
  ```xml
    <rule>When evaluating negative conditions or presence of flaws (vice rules), you must look ONLY for physical semantic matches. If the text does not contain the exact physical anchors defined in the rule, you MUST return JSON null. Speculation, extrapolation, or rationalizing away missing evidence is strictly banned.</rule>
  ```

---

## Verification Plan

### Automated Verification
1. We will verify the compilation behavior of prompts and system directives using a dynamic prompt test:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test
   ```

---

## Session Handover
To execute this sub-plan after approval:
1. Open a fresh context window.
2. Run command: `/tier2-execute --target docs/epic/tasks_EPIC_61/phase2_prompt_engine.md`
