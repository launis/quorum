# Implementation Plan: EPIC 90 Phase 1 - Pydantic "Suojamuuri" ja DTO:n rakentaminen

Source: Epic Phase 1, Step 1.1 & 1.2

## Goal
Establish a robust Pydantic barrier for LLM outputs, defining allowed visual intents and formatting text at the domain level to protect UI graphics.

## Target Files (Modify)
- `backend_v2/models/v2_core.py` (and/or `lightweight_matrix.py` where `AtomEvaluationItemDTO` lives)

## Context Files (Read-Only)
- `backend_v2/models/dtos/lightweight_matrix.py`

## Implementation Steps
1. Add `VisualIntent = Literal["success", "warning", "critical_override", "info"]` enum.
2. Update `AtomEvaluationItemDTO` (or relevant DTO) with `chart_display_label: str`, `visual_intent: VisualIntent`, and `semantic_reasoning: str`.
3. Create `@field_validator(mode="after")` for `chart_display_label` to split by whitespace and truncate to max 3 words, and cut string at max 25 characters. Append "..." if truncated.

## Hardening Rules & Architectural Invariants (from hardening.xml & .agents/rules)
- **Rule 2 (Strict Pydantic V2 Rust):** Ensure `model_config = ConfigDict(strict=True, extra="forbid")` is respected. No legacy fallback hacks.
- **Rule 10 (Pydantic Pure Hydration Boundary):** Strict validation at the API boundary.
- **Rule 11 (Pydantic Native Field Priority):** Use `Field(max_length=25)` alongside the `@field_validator` for word-count truncation.
- **Rule 1 & 22 (The Zero Compromise Pledge / Zero Legacy Fallbacks):** DO NOT use `.get("key", "info")` or silent defaults for `visual_intent`. If invalid, `ValidationError` must crash it.

## Testing & Quality Gate Plan
- **Unit Tests:** Add tests to verify truncation logic in `chart_display_label` and that invalid `visual_intent` triggers `ValidationError`.
- **Quality Gate:** Run `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`
- Update `docs/architecture/` with the new schema constraints.

---
<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_90_Output_renewal_tracker.md`
