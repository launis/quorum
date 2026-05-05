# Epic 46: Soft Scoring Engines - Phase 1: Backend Math & Engines

## Objective
Refactor the backend mathematical scoring logic to implement "Soft Scaling" (Benefit of the Doubt - BoD) rather than the rigid Guttman "Hard Threshold" model. Ensure that the `strictness_level` from the UI dynamically directs the severity of the penalty instead of always crashing the score to the minimum.

## Architectural Invariants
- **Rule 1 (No Naked Dicts):** Pydantic models and explicit typings must be used.
- **Rule 2 (No Hardcoded Strings):** Configuration values must not rely on magic strings.
- **Rule 3 (The Zero-Compromise Pledge):** No backward compatibility hacks, duck-typing, or `try/except` silent passes.
- **Rule 4 (No Silent Failures):** Let exceptions bubble up.

## Target Files
**TARGET (Modify):**
- `backend_v2/utils/math_utils.py`
- `backend_v2/utils/scoring/waterfall_engine.py`
- `backend_v2/utils/scoring/dampening_engine.py`
- `backend_v2/utils/scoring/average_engine.py`

**CONTEXT (Read-Only):**
- `backend_v2/hooks/scoring.py`
- `backend_v2/models/enums.py`

## Milestones

### [COMPLETE] Milestone 1: Math Utilities Refactoring (`math_utils.py`)
1. **Implement Strictness Converter (`convert_strictness_to_forgiveness`):** 
   - Add a utility function to convert `strictness_level: int` to a `base_forgiveness` float multiplier:
     - 0 (Täysi joustavuus): `1.0`
     - 15 (Salliva): `0.60`
     - 50 (Tasapainoinen): `0.30`
     - 85 (Tiukka): `0.10`
     - 100 (Ehdottomuus): `0.00`
2. **Update `calculate_progressive_dampening_score`:**
   - Update function signature to accept `base_forgiveness: float`.
   - Update the progressive dampening math loop to calculate `effective_hit_rate = max(hit_rate, base_forgiveness)`.
   - Modify the multiplier application: `modifier = modifier * math.sqrt(effective_hit_rate)`.
3. **Implement `calculate_soft_waterfall_score`:**
   - Replace or modify the rigid `calculate_waterfall_floor` to use a weighted sum approach.
   - For any level that falls below the `target_threshold` (e.g. 0.75), apply a `penalty_multiplier` to all higher levels.
   - `penalty_multiplier` should be directly derived from the strictness level (e.g. `base_forgiveness`, where 100=0.0 meaning zero higher points pass, 50=0.3 meaning 30% of higher points pass).

### [COMPLETE] Milestone 2: Engine Integrations (`backend_v2/utils/scoring/*.py`)
1. **`dampening_engine.py`:**
   - Fetch the `base_forgiveness` via the new math utility using `strictness_level`.
   - Pass it to the math function.
   - Update the `calculation_log` generation to clearly explain: *"Tasolta X saatiin 0 osumaa. Käytetään Strictness Y:n mukaista joustokerrointa (Z.ZZ), joten pisteitä vaimennettiin pehmeästi."*
2. **`waterfall_engine.py`:**
   - Integrate the `calculate_soft_waterfall_score`.
   - Update the `calculation_log` to reflect the penalty multipliers applied, instead of outputting "(SKIPPED - Blocked by failure)".
3. **`average_engine.py`:**
   - `PureAverageScoringEngine` and `WeightedAverageScoringEngine` are naturally soft. Connect the `strictness_level` to curve scaling so that a high strictness requires a higher hit rate to map proportionally to higher scores. (e.g., applying a non-linear exponent or adjusting the ratio based on strictness).

### Verification & Quality Gate Plan
- **Tools to Run:** 
  - `uv run python scripts/backend_audit_loop.py backend_v2/utils/math_utils.py`
  - `uv run python scripts/backend_audit_loop.py backend_v2/utils/scoring/waterfall_engine.py backend_v2/utils/scoring/dampening_engine.py backend_v2/utils/scoring/average_engine.py`
- **Tests:** Write/update unit tests for the math utilities and scoring engines to mathematically prove that `strictness_level=15` yields a higher score than `strictness_level=85` for the identical 0-hit rate stats, ensuring the Soft Scaling feature works deterministically.
