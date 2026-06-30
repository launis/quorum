# EPIC 92: Phase 2 - Scoring Engine & Inline Conditional Evaluation

## Goal
Modify the scoring engine (`scoring.py`) to evaluate the `conditions` field before processing the `resolved_claim`. Introduce the `N/A - Condition Not Met` state and populate short-circuit metadata.

**Source**: [EPIC_92_Enriched_Atom_Graph_Architecture.md](file:///c:/src/quorum/docs/epic/EPIC_92_Enriched_Atom_Graph_Architecture.md) Phase 2

## Scoping
**TARGET (Modify)**
- `c:\src\quorum\backend_v2\hooks\scoring.py` (Pre-evaluate conditions before mapping)
- `c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py` (Update `calculate_rule_satisfied` to accept `conditions_met`)

**CONTEXT (Read-Only)**
- `c:\src\quorum\backend_v2\api\routers\execution\executions.py`

## Architectural Invariants (Hardening Mandates)
You MUST strictly adhere to these rules during execution:
- **Rule 3 (Fail-Fast Hydration)**: Do not use naked dict access `.get()` in business logic.
- **Rule 17 (Duct Tape Ban)**: "God Blocks" are forbidden. Catch, log, and raise specific exceptions if condition validation crashes.
- **Rule 18 (RFC7807)**: All exceptions must be translated into Quorum's `AppException`.
- **Epic-Specific Short-Circuit Metadata**: You must explicitly return `short_circuit_reason_tda_id` and `short_circuit_evaluation` when bypassing an atom.

## Implementation Steps

### Step 1: Inline Condition Evaluation Logic
- In `scoring.py` (around L653 `atom_mapping`), the LLM evaluation now returns `conditions`.
- **Deterministic-First Strategy (Huang et al., ICLR 2024):** Ehtojen totuusarviointi suoritetaan kahdessa tasossa:
  1. **Ensisijainen (deterministinen):** Käytä `AnchorValidationService`-tyylistä merkkijonohakua. Jos `ClaimCondition.condition_text` löytyy fyysisesti lähdetekstistä, ehto on TOSI. Tämä on 100% deterministinen, ei LLM-riippuvainen.
  2. **Toissijainen (ensemble):** Jos ehdon arviointi vaatii semanttista päättelyä (ei suoraa tekstiosumaa), se arvioidaan `high_entropy = True` -ensemble-moodissa sycophancy-riskin torjumiseksi.
- Update `atom_mapping` to store this result as a boolean (or string if DLQ'd).

### Step 2: calculate_rule_satisfied Update
- In `lightweight_matrix.py`, update `calculate_rule_satisfied(..., conditions_met: bool | None = None)` to accept the pre-evaluated condition state.
- Implement the short-circuit:
  ```python
  if conditions_met is False:
      return "N/A"
  ```

### Step 3: Short-Circuit Metadata Tracking
- Ensure that when `"N/A"` is returned, `scoring.py` creates an explicit payload containing the `short_circuit_reason_tda_id` (the ID of the condition atom that failed) and `short_circuit_evaluation` ("FALSE" or "DLQ").

### Step 4: Documentation Update
- Document the new N/A state and metadata tracking in `c:\src\quorum\docs\architecture\architecture\tripartite_calculation_boundary.md`.

## Testing & Quality Gate Plan
- **UNIT TESTS**: Create/update `tests/unit/hooks/test_scoring.py` to assert that:
  - If a condition fails, the atom's state is strictly `"N/A"`.
  - The `short_circuit_reason_tda_id` is populated in the resulting evaluation dict.
- **QUALITY GATE**: You MUST run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py --test` to verify code quality. Naked execution of `pytest` is forbidden.

---
## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_92_tracker.md`
