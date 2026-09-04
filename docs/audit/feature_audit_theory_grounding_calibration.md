# Feature Audit Report: Theory-Grounding Matrix Calibration & Diagnostic Engine

**Execution Target:** `exe_88267cb7b3cf4718ae76b7dbce04a92e`  
**Associated Logs & Artifacts:** @[backend_debug.log], @[data/files/executions/exe_88267cb7b3cf4718ae76b7dbce04a92e/execution_trace.json]  
**Calibrated Roadmap Context:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Theory_Grounding_Matrix_Calibration_and_Micro_Slice_Engine.md]  
**Workflow Tier:** `/tier8-audit-feature` (System 2 First Principles Analysis & Red Team Audit)

---

## 1. Executive Summary & Forensic Findings

During post-implementation verification of the **Theory-Grounding Matrix Calibration and Micro-Slice Engine** (committed in `4b950256`), a live analysis run (`exe_88267cb7b3cf4718ae76b7dbce04a92e`) yielded severe scoring anomalies across the user UI:
1. **The 0.0% Collapse:** 8 out of 13 evaluation matrices scored **0.0% (1.0 / 5.0 or 1.0 / 6.0)** across all scale levels (e.g. *Syy-seuraussuhteet*, *Ohjeiden noudattaminen*, *Vastuullisuus*, *Oman tiedon rajat*, *Avoimuus*, *Prosessiomistajuus*, *Itsensä haastaminen*, *Luottamusarvio*), with *Päättelyn rehellisyys* scoring **0.8%**, while *Harkintakyky (Kahneman)* scored **100.0%**, and *Toulmin* scored **71.8%**.
2. **The Visual Asterisks:** Row titles in the UI exhibited trailing asterisks (e.g. `*` or `* **`).

Forensic analysis of @[data/files/executions/exe_88267cb7b3cf4718ae76b7dbce04a92e/execution_trace.json] and backend code paths isolated the exact mechanical root causes:

### Finding A: The Double-Inversion Bug in `matrix_hook.py`
In @[backend_v2/services/orchestrator/extractive_sensor_service.py#L403-L406], the extractive sensor evaluates each micro-atom assertion and assigns an `ExecutionStatus`:
```python
# extractive_sensor_service.py (Lines 403-406)
if is_inverse:
    status = ExecutionStatus.FAILED if eval_result.is_true else ExecutionStatus.PASSED
else:
    status = ExecutionStatus.PASSED if eval_result.is_true else ExecutionStatus.FAILED
```
Here, `ExecutionStatus.PASSED` is an absolute semantic contract: **the analyzed text passed the test** (i.e. for inverse evidence atoms, no defect was found; for positive atoms, the required quality was present).

However, downstream in @[backend_v2/hooks/scoring/matrix_hook.py#L361-L366], the hook re-evaluated `tda.inverse_evidence`:
```python
# matrix_hook.py (Lines 361-366) - THE DEFECTIVE INVERSION:
if status_str == "PASSED":
    is_satisfied = not tda.inverse_evidence  # When inverse_evidence is True, this evaluates to FALSE!
elif status_str == "FAILED":
    is_satisfied = bool(tda.inverse_evidence)
else:
    is_satisfied = False
```
Because `status_str == "PASSED"` was already inverted by the sensor, checking `not tda.inverse_evidence` inverted it a **second time**. Consequently, **every single inverse evidence atom that successfully passed (where the user committed zero errors) was marked as `FAILED` in the matrix scorecard!**

### Finding B: The Guttman Waterfall Cascade Collapse
In the calibrated matrices (@[backend_v2/seed/seed_data.json]), Level 1 and Level 2 are structured with **fatal-flaw / negative defect detectors** (`inverse_evidence: True`):
- For `matrix_taskguard`, `matrix_causal_abductive`, and `matrix_epistemic_humility`, Level 1 and Level 2 have **5 out of 5** atoms with `inverse_evidence: True`.
- Due to the double-inversion bug, all 5 Level 1 atoms were marked `FAILED`, resulting in **0 / 5 hits (0.0%) on Level 1**.
- Under the Guttman Waterfall scoring algorithm in @[backend_v2/utils/math_utils.py#L227-L280], if Level 1 fails to meet the strict threshold, the waterfall sliding penalty drops to `0.0`, locking `achieved_score` to `math_min = 1.0`. When normalized to `[0, 100]`:
  $$\text{Normalized Score} = \frac{1.0 - 1.0}{5.0 - 1.0} \times 100 = 0.0\%$$
- Conversely, `matrix_kahneman` contains positive assertions on Levels 1, 2, and 3 which passed and did not suffer from the double inversion, allowing Kahneman to cascade cleanly to 100.0%.

### Finding C: Asterisks in UI Row Titles
In @[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart#L51-L56], row titles append asterisks based on boolean DTO flags:
```dart
Text(
  matrix.labelI18n.get(Localizations.localeOf(context).languageCode) +
      (isEval ? ' *' : '') +
      (matrix.allowContextualOverride ? ' **' : ''),
  ...
)
```
- `*` denotes `isEvaluative = true` (an evaluative target matrix).
- `**` denotes `allowContextualOverride = true` (the matrix permits contextual AI override).
While technically intentional metadata markers, appending raw asterisks `*` and `**` directly into text strings degrades aesthetic polish and confuses end-users.

---

## 2. Root Cause Analysis & First Principles

| Component | First Principle Invariant | Violation / Breakdown |
| :--- | :--- | :--- |
| **`extractive_sensor_service.py`** | Single Source of Semantic Status (`ExecutionStatus`). `PASSED` means the entity satisfied the operational test. | Correctly inverts `is_true` for inverse evidence atoms, yielding `PASSED` when no defect is detected. |
| **`matrix_hook.py`** | Consumer of DTO status. Must trust upstream `ExecutionStatus` contracts without semantic mutations. | Violated the SSOT contract by re-interpreting `inverse_evidence`, flipping `PASSED` into `is_satisfied = False`. |
| **`math_utils.py` (Waterfall)** | Monotonic progression. Level $N$ depends strictly on passing threshold at Level $N-1$. | Operating mathematically as designed: zero hits at Level 1 immediately choked the entire progression pipeline. |
| **`matrix_row_item_widget.dart`** | Zero-Math Dumb Painter. Visual badges and semantic indicators must use UI widgets, not string concatenation. | Concatenated raw ASCII asterisks `*` and `**` to title text rather than rendering dedicated badges or tooltips. |

---

## 3. Panel of Experts Audit

### A. Backend & Typing Architect
- **Invariant:** Strict Pydantic V2 DTOs (`AtomResultDTO`, `ExecutionStatus`).
- **Audit:** Downstream consumers like `matrix_hook.py` must never inspect private atom configurations (`tda.inverse_evidence`) to question or re-invert an explicit enum state (`ev_dto.status == ExecutionStatus.PASSED`). `ExecutionStatus.PASSED` is sovereign.
- **AST Guardrail Need:** Any check of `tda.inverse_evidence` inside a scoring reduction hook that already receives `ExecutionStatus` represents a semantic anti-pattern and must be purged.

### B. LLM & Context Architect
- **Invariant:** Prompt caching efficiency and epistemic purity.
- **Audit:** In @[backend_v2/services/orchestrator/extractive_sensor_service.py] and @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py], the LLM prompt and Bo3 voting functioned properly. The LLM accurately identified that the user's memo did not commit post-hoc fallacies, teleological fallacies, or uncalibrated causal extrapolation, correctly outputting `is_true = False`. The LLM inference was 100% faithful; the bug was purely in downstream reduction logic.

### C. SDUI & Frontend Architect
- **Invariant:** Dumb Painter SDUI & Polish Mandate.
- **Audit:** The Flutter UI in `matrix_row_item_widget.dart` appended ` *` and ` **` directly to the localized title string. Instead of unadorned typography or subtle status badges (e.g. `AppSpacing`, `Theme.of(context).colorScheme`), raw characters clutter the layout.

---

## 4. Falsification & Anti-Happy-Path Analysis

### Failure Mode 1: Pure Inverse Scale Failure
- **Hypothesis:** When an entire scale level consists solely of negative assertions (`inverse_evidence: True`), any document that is completely clean and defect-free will be marked as completely failed ($0\%$ hits).
- **Proof:** Proven in `exe_88267cb7b3cf4718ae76b7dbce04a92e` where `matrix_taskguard` (Level 1: 5 inverse assertions) and `matrix_causal_abductive` (Level 1: 5 inverse assertions) were evaluated as `0 / 5` despite all 10 LLM evaluations returning `PASSED` with zero flaws detected.

### Failure Mode 2: Override Interaction Corruption
- **Hypothesis:** When `status_str == "PASSED"` and `ev_dto.contextual_override == True`, line 355 bypasses the standard inversion logic, leading to asymmetric state handling where non-overridden inverse atoms fail but overridden inverse atoms pass.
- **Remediation:** Centralize atom satisfaction: an atom is satisfied if and only if `ev_dto.status == ExecutionStatus.PASSED` (or when valid contextual override promotes it to `PASSED`).

---

## 5. Quorum Modernity Gate & Technical Debt Sweep

Checking @[backend_v2/hooks/scoring/matrix_hook.py]:
1. **Duck-typing & Raw Dicts:** `ev_dict_tmp` and `ev_dict_check` fallbacks are present around lines 312-320 to handle DLQ dictionaries. These should be modernized to strict `AtomResultDTO` or typed DLQ envelopes.
2. **Banned Lazy Fallbacks (`QGR016`):**
   - Line 259: `content_payload['extracted_facts'] if 'extracted_facts' in content_payload else {}`
   - Line 274: `pb_model.scales or []`
   - Line 301: `total_evals or 1`
   - Line 327: `state.global_context_vars or {}`
   - Line 454: `matrix_extensions_by_block[pb_id] if pb_id in matrix_extensions_by_block else {}`
   All of these trigger AST Guardrail advisory warnings and must be cleaned up in Phase 1 of the implementation plan.

---

## 6. Five-Axis System 2 Deconstruction & Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`backend_v2/hooks/scoring/matrix_hook.py`** (Lines 350-378) | Eradicate double inversion: delete `is_satisfied = not tda.inverse_evidence`. Delete ternary dictionary fallbacks flagged by `QGR016`. | Respect `ev_dto.status == ExecutionStatus.PASSED` as the single source of truth. If status is `PASSED`, `is_satisfied = True`. | Eliminate redundant state branching. A single resolution block evaluates `status` and `effective_override`. | Unit test asserting 100% hits when `inverse_evidence: True` atoms report `ExecutionStatus.PASSED`. |
| **`backend_v2/tests/unit/hooks/test_scoring.py`** | Eradicate test gaps: existing tests only tested happy path with `inverse_evidence: False`. | Add explicit ISTQB partition tests covering: 1) Scale with 100% inverse atoms passing, 2) Mixed positive/inverse scales, 3) DLQ handling. | No mock duplication; reuse `MockRepoWaterfall`. | `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -k "test_matrix_scoring_hook"` passing 100%. |
| **`client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart`** | Eradicate string concatenation of ` *` and ` **` into localized title strings. | Render clean, accessible UI badges or icons using `Tooltip` and `Theme.of(context).colorScheme`. | Do not build complex custom chip hierarchies; a simple, subtle badge or clean tooltip preserves layout stability. | Flutter analyzer clean; visual test confirming clean titles. |

---

## 7. Recommended Remediation & Next Steps

### Surgical Fix Details
In @[backend_v2/hooks/scoring/matrix_hook.py], replace lines 351–376 with:
```python
status_str = ev_dto.status.name

if status_str == "DLQ":
    final_state = "DLQ"
elif status_str == "PASSED":
    # ExtractiveSensorService already inverted status for inverse_evidence atoms.
    # PASSED strictly means the requirement was satisfied.
    if ev_dto.contextual_override:
        final_state = "TRUE" if effective_override else "FALSE"
    else:
        final_state = "TRUE"
elif status_str == "FAILED":
    if effective_override and ev_dto.contextual_override:
        final_state = "TRUE"
    else:
        final_state = "FALSE"
else:
    final_state = "FALSE"
```

### Immediate Action Items:
1. **Approve Implementation Plan:** Transition to `/tier0-create-plan` to formulate a formal, phased remediation plan covering:
   - Phase 1: Pre-requisite `QGR016` AST guardrail debt cleanups in `matrix_hook.py`.
   - Phase 2: Elimination of the double-inversion bug in `matrix_hook.py`.
   - Phase 3: Flutter title asterisk cleanup in `matrix_row_item_widget.dart`.
   - Phase 4: Full automated test suite expansion and local verification rerun against `exe_88267cb7b3cf4718ae76b7dbce04a92e`.
