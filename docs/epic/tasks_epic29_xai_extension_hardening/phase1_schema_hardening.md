# Phase 1: Schema Level Hardening & Enum Parity

## Goal
Anchor Pydantic schemas in `backend_v2/llm/schema_builder.py` to be stricter and eliminate "cheerleader" (Sycophancy) language from XAI output extensions. Enforce strict Enum Parity using `XaiExtensionType` to resolve No-String Mandate violations.

## Target Files (Modify)
- `backend_v2/llm/schema_builder.py`

## Context Files (Read-Only)
- `backend_v2/models/enums.py`

## Implementation Steps
1. **Import `XaiExtensionType`**: In `backend_v2/llm/schema_builder.py`, import `XaiExtensionType` from `backend_v2.models.enums`.
2. **Remove Hardcoded Strings**: Replace all hardcoded string checks in `extensions` (e.g., `if "coaching" in extensions:`) with the corresponding Enum value (e.g., `if XaiExtensionType.COACHING.value in extensions:`).
3. **Coaching & Remediation Hardening**: Update the description for `XaiExtensionType.COACHING.value`:
   - *Old*: "Concrete coaching tip/remediation advice to the subject."
   - *New*: "STRICT MANDATE: Provide one concrete, actionable step to patch the observed data or logic gap. DO NOT give general tips or encouraging advice."
4. **Falsification Hardening**: Update the description for `XaiExtensionType.FALSIFICATION.value`:
   - *Old*: "Devil's advocate argument rejecting the primary justification."
   - *New*: "STRICT MANDATE: List the exact business scenario where the user's model or claim crashes 100%. No mitigating words allowed."
5. **Risk Flag & Missing Context Hardening**: Update the descriptions for `XaiExtensionType.RISK_FLAG.value` and `XaiExtensionType.MISSING_CONTEXT.value` to reflect a stricter tone, removing any theoretical jargon.

## Verification & Quality Gate Plan
- **Linting & Formatting**: Run `uv run python scripts/backend_audit_loop.py backend_v2/llm/schema_builder.py backend_v2/models/enums.py`
- **Unit Testing**: Run `uv run python scripts/backend_audit_loop.py backend_v2/llm/schema_builder.py --test`
