# Implementation Plan: Phase 1 - Domain Models & Variance Calculation Engine

This task implements the backend schemas, enum mappings, and core numerical cross-comparison engine for EPIC 57.

## Scoping

### Target (Modify)
- [x] [enums.py](file:///c:/src/quorum/backend_v2/models/enums.py) - Add enum `XaiExtensionType.VARIANCE_VALIDATION` (ja tarvittava `contextual_override`).
- [x] [xai.py](file:///c:/src/quorum/backend_v2/models/domain/xai.py) - Add `VarianceValidationExtension` ja päivitä `XAIReporterInput`.
- [x] [enums.dart](file:///c:/src/quorum/client_app_v2/lib/core/models/enums.dart) - Lisää Dart enum-arvot `contextualOverride` ja `varianceValidation` pariteetin saavuttamiseksi.

### New (Create)
- [x] [variance_engine.py](file:///c:/src/quorum/backend_v2/utils/scoring/variance_engine.py) - Central math engine.

### Context (Read-Only)
- [x] [metrics.py](file:///c:/src/quorum/backend_v2/models/domain/metrics.py)
- [x] [linguistics.py](file:///c:/src/quorum/backend_v2/models/domain/linguistics.py)
- [x] [test_enum_parity.py](file:///c:/src/quorum/tests/test_enum_parity.py)

---

## Technical Specifications & Architectural Invariants

> [!IMPORTANT]
> **Strict Pydantic V2 & Zero-Compromise Invariants**:
> - Enforce `ConfigDict(extra='forbid', strict=True)` on the new extension type (`strict_pydantic_v2_rust`).
> - Do not introduce any silent default fallback hacks (`zero_legacy_fallback_hacks`).
> - Scoring calculation bounds must be mathematically pure and separate from UI presentation (`strict_math_display_isolation`).
> - Ensure 1:1 parity between Backend and Frontend enums (`cross_language_enum_parity`).

### Mathematical Variance Engine Specification
The `variance_engine.py` will implement the cross-comparison algorithm:
- Inputs:
  - `llm_authenticity_score` (float, expected range 1.0 - 3.0).
  - `performative_phrases_count` (int, >= 0).
- Normalization:
  - `normalized_performative_count` = `min(performative_phrases_count / 10.0 * 2.0, 2.0)` (maps count from 0-10+ to 0.0-2.0 scale).
  - `target_cognitive_dampener` = `3.0 - normalized_performative_count`
- Absolute Variance Formula:
  $$\text{Variance} = | \text{LLM Authenticity Score} - \text{target\_cognitive\_dampener} |$$
- Alignment Verdict:
  - If `Variance < 0.5`: `ALIGNED`
  - If `Variance >= 0.5` and `llm_authenticity_score > target_cognitive_dampener`: `MISALIGNED_SYCOPHANCY`
  - Else: `MISALIGNED`

---

## Detailed Milestones

### Milestone 1: Centralized Enums Update
- **Goal**: Register the new enum values in Python and Dart.
- **Source**: Epic Phase 1, Toimenpide 1 & enums.dart parity.
- **Actions**:
  1. Add `VARIANCE_VALIDATION = "variance_validation"` to `XaiExtensionType` in `backend_v2/models/enums.py`.
  2. Add `@JsonValue('variance_validation') varianceValidation` to `XaiExtensionType` in `client_app_v2/lib/core/models/enums.dart`.

### Milestone 2: Domain Schema Evolution
- **Goal**: Implement `VarianceValidationExtension` and update input/output envelopes.
- **Source**: Epic Phase 1, Toimenpide 1 & 3.
- **Actions**:
  1. Create `VarianceValidationExtension` class inheriting from `V2CoreBase` in `backend_v2/models/domain/xai.py`.
  2. Register `VarianceValidationExtension` in `XAIExtension` union type (`Annotated`).
  3. Modify `XAIReporterInput` to explicitly declare `step_metrics` and `step_linguistics`.

### Milestone 3: Variance Engine Core Implementation
- **Goal**: Create the numerical verification helper.
- **Source**: Epic Phase 1, Toimenpide 2.
- **Actions**:
  1. Create `backend_v2/utils/scoring/variance_engine.py`.
  2. Implement `calculate_mechanical_cognitive_variance` with pure mathematical isolation.

### Milestone 4: Cross-Language Verification
- **Goal**: Validate that all model constraints are perfectly synchronized.
- **Source**: Epic Phase 1, Toimenpide 1 (Parity loop).
- **Actions**:
  1. Run `test_enum_parity.py` to assert backend/frontend mapping is identical.

---

## Testing & Quality Gate Plan

### Unit Tests
- Create `tests/unit/test_variance_engine.py` verifying multiple mathematical edge-cases:
  - Zero performative phrases, Authenticity 3.0 -> Aligned (Variance 0.0).
  - 10 performative phrases, Authenticity 3.0 -> Sycophancy (Variance 2.0).
  - 5 performative phrases, Authenticity 2.0 -> Aligned (Variance 0.0).

### Execution Command
```powershell
uv run pytest tests/unit/test_variance_engine.py
uv run python scripts/backend_audit_loop.py backend_v2/models/domain/xai.py --test
```

---

## Session Handover
To execute this step iteratively in a new session, run:
```powershell
/tier2-execute --plan="docs/epic/tasks_EPIC_57/phase1_domain_models.md"
```
