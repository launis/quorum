# EPIC 140: Matrix Scoring Reliability & Protocol Harmonization

## 1. Goal Description & Background (Objective & Problem Statement)

**Objective**: Resolve the "Cognitive Collapse" failure in Matrix Scoring where matrices evaluate to a 0 score and empty distribution, ensuring that soft matrices correctly utilize the Soft Extraction Protocol and illegal `contextual_override` bypasses are strictly penalized.

**Problem Statement**:
The user reported that matrix evaluations are scoring 0 and the distribution values are empty (not even showing `0/5`). A deep system trace revealed that the matrices are evaluating, but the `cognitive_collapse` safety lock is being triggered in `backend_v2/hooks/scoring.py` due to a high number of `CONTESTED` atoms. 

This is caused by two compounding issues:
1. **Illegal Bypass in `scoring.py`:** When the LLM evaluates an atom as `PASSED` but uses `contextual_override=True` (meaning it couldn't find a physical exact quote), `scoring.py` forces it into a `CONTESTED` state, even if the matrix explicitly forbids contextual overrides (`allow_contextual_override=False`).
2. **Protocol Mismatch (Epic 92 Violation):** Epic 92 mandated that "Soft" matrices MUST use a **Soft Extraction Protocol** at the Step level to encourage the LLM to extract the *best implying sentence* rather than using contextual overrides. However, `seed_data.json` was never updated. The execution step processing these matrices (specifically `sp_48974af1fc584407`) is still using the `blk_573802341db9d68c` "Zero-Trust Hard Extraction Protocol".

Because the LLM is forced to use a Hard Protocol for a Soft concept, it fails to find exact syntactic markers, hallucinating `contextual_override=True` to bypass Pydantic validation. `scoring.py` blindly accepts this, marks them all as `CONTESTED`, and rapidly breaches the `cognitive_collapse` threshold (`n_contested > 3`), destroying the matrix output.

## 2. Architectural Impact & Compliance Matrix

- **Deprecations & Sunset List (`What We Will REMOVE`)**
  - The behavior in `scoring.py` that maps illegal `contextual_override=True` to `CONTESTED` when `allow_contextual_override` is False.

- **Retained SSOT Invariants (`What We Will RETAIN`)**
  - The `cognitive_collapse` safety lock threshold (`n_contested > 3`) remains intact to protect against genuine hallucinations.
  - The Matrix Domain Parser and LLM Extraction structures remain unchanged.

- **Compliance & Modernity Gates**
  - Pydantic Strictness: `ConfigDict(strict=True, extra='forbid')` remains enforced.
  - Zero Legacy State Support: We will update the raw `seed_data.json` instead of writing migration scripts.

- **Producer-Consumer Integration Check**
  - Backend modifications directly affect the scoring hooks. The Flutter UI will correctly receive the valid `level_breakdown` arrays instead of `null` once the backend prevents the `cognitive_collapse`.

## 3. Phased Execution Plan (Implementation Strategy)

**Phase 1: Seed Data Protocol Harmonization**
- **Action**: Modify `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- **Details**: Update the `extraction_protocol_block_id` for Execution Steps that process Matrices (specifically `sp_48974af1fc584407` and `sp_6f40b964895c426b`) from the Hard Protocol (`blk_573802341db9d68c`) to the Soft Protocol (`blk_f23a9b1c7d4e5082`). This will instruct the LLM to extract semantic quotes instead of bypassing.

**Phase 2: Hook Validation Strengthening (The Safety Lock)**
- **Action**: Modify `@[c:\src\quorum\backend_v2\hooks\scoring.py]`
- **Details**: Update `matrix_scoring_hook` to validate `effective_override`. If `allow_contextual_override` is False for the matrix, an atom returning `PASSED` with `contextual_override=True` must be mapped to `FALSE` (penalty), NOT `CONTESTED`. This enforces the matrix's bypass rules.

**Phase 3: Verification & E2E Integration Gate**
- Ensure Python formatting and strict typing passes via `backend_audit_loop.py`.

## 4. Definition of Done (DoD) & Verification Plan

- **Definition of Done (DoD)**:
  - `scoring.py` no longer allows illegal `contextual_override` bypassing.
  - `seed_data.json` step blocks correctly reference the Soft Extraction Protocol.

- **Automated Unit Tests**:
  - Run `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py` to ensure `scoring.py` modifications pass unit tests.

- **AST Guardrails & Structural Tests**:
  - N/A for this specific logic flow adjustment, as it modifies conditional logic inside an existing hook rather than introducing a new architectural construct.

- **Manual Verification Steps**:
  - Re-run `uv run python backend_v2/seed/run_seed.py local` to apply the JSON changes.
  - Perform a full matrix execution via the UI or API and verify that `level_breakdown` values populate correctly without triggering `cognitive_collapse`.

- **MANDATORY Final E2E REST API Verification Gate**:
  - Set environment variable `RUN_LIVE_E2E=true` and run `uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

## 5. Required Knowledge Items (KI Registry)

<required_knowledge_items>
- `@[C:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]` <!-- LLM Extraction Architecture (Steps, Protocols, Matrices, Overrides) -->
</required_knowledge_items>
