# Epic: System 2 Reliability Fixes - Phase 1B: Deterministic Anchor Validation

**Source:** Epic Phase 1, Step 2 & 3

## Goal
Replace the rigid 100% exact match requirement with a Deterministic Discrete Tiers (Porraskaava) approach and an Entropy Gate to prevent hallucinations on short strings, effectively curing DLQ errors caused by overly strict validation.

## Target Files
- `[MODIFY] c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py`
- `[MODIFY] c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py`

## Context Files
- `c:\src\quorum\backend_v2\models\enums.py`

## Architectural Invariants & Hardening Mandates
- **No Overengineering (from Context Handover):** Stick to deterministic Discrete Tiers (Porraskaava) that map directly to existing Enum states (`StrictnessAnchor`). Do not use complex fuzzy match lerp math.
- **Entropy Gate (Hallucination Protection):** Fuzzy search (`fuzz.partial_ratio`) is lethal for words under 20 chars due to "100% match" hallucinations. Length Gate implementation is critical.
- **Rule 17 (hardening.xml):** "The Duct Tape Ban". All errors MUST be caught, logged, and re-raised via `AppException`. No `except Exception: pass`.
- **Rule 20 (hardening.xml):** "The Self-Healing Ban". Data validation belongs 100% to Pydantic/Service, no dynamic patching of AI outputs using Regex.
- **Rule 87 (hardening.xml):** "Architecture Lock Mandate". Do not break protected algorithms unless explicitly required. Preserve existing file I/O and extraction logic structure where possible.

## Implementation Steps

### 1. Update `AnchorValidationService`
Modify `validate_evidence` in `anchor_validation_service.py`.
- **Signature Change:** Add `strictness_level: int = 50` to the method signature.
- **Entropy Gate:** If the `quote` is less than 20 characters long, Fuzzy Match is FORBIDDEN. It must fall back to 100.0% strict match.
- **Deterministic Tiers (Discrete Tiers):** Map the `strictness_level` to explicit thresholds:
  - `ABSOLUTE (100)`: 100.0% (Fuzzy off)
  - `STRICT (85)`: 95.0% (Allows minor typo)
  - `STANDARD (50)`: `base_threshold` (e.g., 80.0%) (Normal OCR tolerance)
  - `RELAXED (30)`: 65.0% (Heavy OCR noise tolerance)
- **Fuzzy Fallback Execution:** Implement `fuzz.partial_ratio(quote, text) >= tier_threshold` to accept the match if it doesn't meet the 100% `strict_match`, provided it clears the Entropy Gate.

### 2. Update `ChunkWorker` Orchestrator
Modify `evaluate_extraction` in `chunk_worker.py`.
- Ensure `strictness_level` is explicitly passed down to the `AnchorValidationService.validate_evidence` call.

### 3. Update Documentation
- **Target:** `c:\src\quorum\docs\architecture\system_quality_standards.md`
- Document the Entropy Gate and Discrete Tiers approach for evidence validation.

## Testing & Quality Gate Plan
- **Unit Tests:** Update/Create tests for `AnchorValidationService` to prove the Entropy Gate (short strings fail if not 100%) and Discrete Tiers function correctly.
- **Quality Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_system2_reliability_fixes_tracker.md`
