# Implementation Plan: EPIC 90 Phase 4 - LLM-moottorin purkaminen (The Dumb Pipe)

Source: Epic Phase 4, Step 4.1, 4.2, 4.3

## Goal
Connect the LLM to the new OutputProfile-driven architecture, implement the Fast-Track XML Parsing pipeline (Universal Ingress), and delete all legacy hardcoded logic.

## Target Files (Modify)
- `backend_v2/services/orchestrator/strategies/llm_execution.py`
- `backend_v2/services/llm/ingress_pipeline.py` (NEW)
- `backend_v2/services/orchestrator/prompt_builder.py`
- `backend_v2/llm/directives.py` (DELETE)
- `backend_v2/llm/linguistic.py` (DELETE)

## Context Files (Read-Only)
- `backend_v2/models/domain/output_profile.py`

## Implementation Steps
1. Update `llm_execution.py` to inject `OutputProfile` attributes into the prompt inside a `<execution_parameters>` tag.
2. Build `ingress_pipeline.py` to regex-extract `<reasoning>` and `<json_payload>` tags in O(1) time before Pydantic hydration. Prevent AST JSON/GIL blockages.
3. Remove old natural language rules from `prompt_builder.py`.
4. Delete `directives.py` and `linguistic.py`.

## Hardening Rules & Architectural Invariants (from hardening.xml & .agents/rules)
- **Rule 29 & 52 (High Fidelity Prompting / Ephemeral Caching):** Keep core system prompts 100% static; dynamic rules go to `<execution_parameters>`. Avoid f-strings for core instructions.
- **Rule 51 (Hybrid Prompting Mandate):** Use XML for structural layout and Markdown for semantic/nested content (`<reasoning>`).
- **Rule 28 (LLM Structured Execution Mandate):** No direct anemic `LLMClient` calls. Let Universal Ingress handle the Fast-Track XML parsing before hydrating into Pydantic models.
- **Rule 50 (Feature Sovereignty Mandate):** Ensure no undocumented business logic is lost during the deletion of legacy files.

## Testing & Quality Gate Plan
- **Unit Tests:** Verify `ingress_pipeline.py` correctly parses XML tags with regex without blocking. Test that missing tags raise `AppException`.
- **Quality Gate:** Run `uv run python scripts/backend_audit_loop.py backend_v2/services/llm/ingress_pipeline.py backend_v2/services/orchestrator/prompt_builder.py --test`

---
<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_90_Output_renewal_tracker.md`
