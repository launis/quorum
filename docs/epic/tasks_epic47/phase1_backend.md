# Epic 47 - Phase 1: Backend Math & Soft Scoring Engines

## Objective
Implement Soft Scoring V3 by transitioning from hard mathematical thresholds to soft scoring logic (Lerp, Sigmoid, MAD).

## TARGET (Modify)
- `backend_v2/utils/scoring/dampening_engine.py`
- `backend_v2/utils/scoring/waterfall_engine.py`
- `backend_v2/utils/scoring/average_engine.py`
- `backend_v2/utils/math_utils.py`
- `backend_v2/models/enums.py`
- `tests/backend_v2/utils/scoring/test_*.py`

## CONTEXT (Read-Only)
- `backend_v2/models/v2_core.py`

## Architectural Invariants (From .agents/rules/)
- **Rule 1: Pydantic V2 Strictness:** Enforce `c:\src\quorum\.agents\rules\01-python-backend.md` (Strict Pydantic V2 & Mutability). New domain models (e.g., for strictness config) must use `ConfigDict(frozen=True)` and strict validations. Enum conversion must use `Annotated[Enum, Field(strict=False)]`.
- **Rule 2: The Duct Tape Ban:** Do not use generic `except Exception: pass` to catch floating point errors; handle them explicitly. Let the system crash loudly if data is malformed.
- **Rule 3: No Magic Strings:** Do not hardcode strings for enums without parity.
- **Rule 4: Opaque Stripe ID Mandate:** No sequential IDs or slugs.
- **Rule 5: Tripartite Rendering Boundary:** Backend returns pure data payloads.

## [x] Task 1: DINA-moottori (Syväarvostelu) - Lerp ja matemaattinen turvallisuus
Target files: `backend_v2/utils/scoring/dampening_engine.py`, `backend_v2/utils/math_utils.py`

Refactor the `DampeningScoringEngine` (Now called: "Syväarvostelu") and related functions to use Linear Interpolation (Lerp) and dynamic exponential dampening instead of a flat `max()` threshold.

New logic requirements:
1. Replace `max(hit_rate, base_forgiveness)` with Lerp: 
   `effective_hit_rate = base_forgiveness + (hit_rate * (1.0 - base_forgiveness))`.
2. Calculate a dynamic exponent based on `strictness_level` (50 -> 0.5, >50 -> higher, <50 -> lower). Note: Strictness 50 is the optimal baseline for cognitive matrices.
3. Math Safety: Safely handle edge cases like `0.0 ** exponent` to avoid `FloatingPointError`. Ensure `dynamic_exponent` is explicitly clamped within reasonable bounds (e.g., 0.2 to 3.0) to prevent overflow/underflow.
4. Apply the exponent: `modifier = modifier * (effective_hit_rate ** dynamic_exponent)`.
5. Ensure strict monotonicity: a higher raw hit rate must ALWAYS result in a higher or equal effective modifier.
6. **Agent Rule Compliance**: Strictly adhere to `c:\src\quorum\.agents\rules\01-python-backend.md` (Math Safety & The Duct Tape Ban). Do not use generic `except Exception: pass` to catch floating point errors; handle them explicitly.

## [x] Task 2: Vesiputousmoottori (Koearvostelu) - Liukuva rangaistuskerroin ja kaskadointi
Target file: `backend_v2/utils/scoring/waterfall_engine.py`

Refactor `WaterfallScoringEngine.calculate` (Now called: "Koearvostelu") to use a proportional/sliding penalty multiplier instead of a fixed binary penalty. This engine is strictly for compliance pass/fail audits.

New logic requirements:
1. Optimal baseline: Must be configured to use Strictness 85 (Tiukka, threshold 0.70) when evaluating absolute pass/fail audits.
2. When `hit_rate < target_threshold`, calculate the shortfall distance: 
   `shortfall = (target_threshold - hit_rate) / target_threshold`.
3. Edge Case: If `target_threshold == 0.0`, fallback shortfall to 0.0 (ZeroDivisionError prevention).
4. Calculate sliding penalty: `sliding_penalty = 1.0 - (shortfall * (1.0 - base_forgiveness))`.
5. Cascade Rule: The `sliding_penalty` MUST be cumulatively multiplied to ALL SUBSEQUENT (higher) levels ONLY, not the current level where the threshold was initially missed: `next_multiplier = current_multiplier * sliding_penalty`.

## [x] Task 3: Painotettu Keskiarvo (Sigmoid-skaalaus ilman ulkoisia riippuvuuksia)
Target files: `backend_v2/utils/scoring/average_engine.py`, `backend_v2/utils/math_utils.py`

Refactor `WeightedAverageScoringEngine` to utilize a Sigmoid (logistic) scaling curve.

New logic requirements:
1. Replace linear scaling with a Sigmoid curve using standard Python `math.exp()`. DO NOT introduce external libraries like NumPy or SciPy.
2. Formula: `raw_sigmoid = 1 / (1 + math.exp(-steepness * (hit_rate - midpoint)))`.
3. Shift the `midpoint` dynamically based on `strictness_level`. Higher strictness = higher midpoint.
4. Normalization: Normalize the output mathematically so that a raw hit_rate of 0.0 yields EXACTLY the mathematical minimum (e.g., 1.0), and 1.0 yields EXACTLY the maximum (e.g., 5.0).

## [x] Task 4: Lineaarinen Keskiarvo (Konkreettinen Outlier Rejection)
Target file: `backend_v2/utils/scoring/average_engine.py`

Refactor `PureAverageScoringEngine` (Now called: "Lineaarinen Keskiarvo") to implement a statistically sound 'Outlier Rejection' mechanism utilizing the robust MAD (Median Absolute Deviation) method.

New logic requirements:
1. Before flattening stats, calculate the `hit_rate` for each level.
2. Calculate the Median of the hit rates. Then calculate the absolute deviations from this median, and find the median of those deviations (this is the MAD). Use standard Python `statistics.median`.
3. Edge case: If MAD is 0.0, fallback to a minimum MAD of `0.05` to prevent overly aggressive rejection in nearly uniform datasets.
4. Define a concrete heuristic for an anomaly: `hit_rate < (median - 3.0 * MAD) AND hit_rate < 0.30`.
5. If an anomaly is found, mitigate it by multiplying that specific outlier level's total weight by `0.25` before calculating the final pure average.

## [x] Task 5: Backend - Keskitetty Strictness-konfiguraatio (Score Clamping)
Target files: `backend_v2/utils/math_utils.py`, `backend_v2/models/enums.py`

Create a centralized strictness mapping and ensure absolute mathematical boundary safety.

New logic requirements:
1. Clean up unused enums (e.g., `SelfHealingThresholdRatio`) from `enums.py`.
2. Implement a pure function `get_strictness_config(level: int)` returning an object/dict with `base_forgiveness`, `sigmoid_midpoint`, and `dynamic_exponent`.
3. Replace all hardcoded strictness logic inside engines with calls to this centralized mapper.
4. Implement `clamp_score(score: float, math_min: float, math_max: float) -> float`. Every single scoring engine MUST pass its final numerical result through this clamp before returning it.
5. **Agent Rule Compliance**: Enforce `c:\src\quorum\.agents\rules\01-python-backend.md` (Strict Pydantic V2 & Mutability). New domain models (e.g., for strictness config) must use `ConfigDict(frozen=True)` and strict validations. Enum conversion must use `Annotated[Enum, Field(strict=False)]`.

## [x] Task 10: Laadunvarmistus - Matemaattisen Monotonisuuden Testiautomaatio
Target files: `tests/backend_v2/utils/scoring/test_*.py`

Implement rigorous Pytest coverage for the refactored 'Soft Scoring' engines.

New logic requirements:
1. Boundary Tests: Test absolute 0.0 and 1.0 hit rates across all strictness levels. Assert values strictly clamp between `math_min` and `math_max`.
2. Monotonicity Tests: Programmatically loop through hit rates from 0.0 to 1.0 in 0.01 increments. Assert that `f(x) <= f(x + 0.01)` is ALWAYS true for all engines. The score must never flatline or decrease when the raw hit rate increases.
3. Outlier Mitigation Tests: Pass an array `[1.0, 1.0, 0.0, 1.0]` to the Lineaarinen Keskiarvo Engine and assert the `0.0` value's weight is significantly reduced compared to a standard mean calculation.
4. **Hardening Verification**: The implementing agent MUST execute the `[/tier2-hardening-backend]` workflow rules upon completion. Explicitly run `ruff check .`, `ruff format .`, `mypy .`, and `pytest tests/backend_v2/utils/scoring/` to ensure zero errors. If any error occurs, fix it immediately before concluding the task.

## [x] Documentation Update
Update `c:\src\quorum\docs\architecture\` documentation with the new Lerp, Sigmoid, and MAD mathematical definitions after tests pass.
Täydennä myös `c:\src\quorum\.agents\rules\04_directory_reference.md` tiedostoa tehtyjen muutosten osalta.

## Testing & Quality Gate Plan
1. **UNIT TESTS**: Create/update `tests/backend_v2/utils/scoring/test_dampening_engine.py`, `test_waterfall_engine.py`, `test_average_engine.py`, `test_math_utils.py` covering all new math boundaries and assertions.
2. Run `uv run python scripts/backend_audit_loop.py backend_v2/utils/scoring/ --test` to verify 100% test passing and >90% coverage. 
3. Run `ruff` and `mypy` via audit script.
