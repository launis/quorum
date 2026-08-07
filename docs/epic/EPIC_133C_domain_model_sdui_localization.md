# EPIC 133C: Domain Model & SDUI Localization (Enums & "N/A" Eradication)

## 1. Goal Description & Background (Objective & Problem Statement)
Following EPIC 133B, this Epic eradicates the final layer of hardcoding: Enum Literals and hardcoded UI fallback text. Currently, states (specifically "PASS" or "FAIL") are typed as Pydantic `Literal` strings, and missing data falls back to hardcoded strings (specifically `"N/A (Lightweight extraction)"`). This violates the Domain Driven Design mandate (which requires strict `Enum` classes) and the Server-Driven UI (SDUI) localization mandate (which dictates the backend must never hardcode UI translations).

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **INTENTIONALLY DROPPED**: `Literal["PASS", "FAIL", "CONTESTED", "DLQ"]` from `backend_v2/models/dtos/atom_evaluation.py`.
- **INTENTIONALLY DROPPED**: Hardcoded fallback strings (specifically `"N/A (Lightweight extraction)"` and `"N/A"`) from backend properties.

### Retained SSOT Invariants (What We Will RETAIN)
- The logical flow of the matrix synthesis remains unchanged.

### Compliance & Modernity Gates
- **Enum Sovereignty**: All states MUST be defined in `@[backend_v2/models/enums.py]`.
- **Strict SDUI Polymorphic Serialization**: The backend MUST output `null`/`None` for missing data. Flutter `.arb` handles display fallbacks.
- **Cross-Domain DTO Parity**: Flutter Freezed models MUST be updated synchronously to expect the new Enums instead of strings.

### Producer-Consumer Integration Check
- **Producer**: Backend Python DTOs.
- **Consumer**: Flutter UI (`@[client_app_v2/lib/core/models/enums.dart]` and affected models).

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Golden Master & Coverage Verification (MANDATORY PREREQUISITE)
- **Step 1.1**: Run global test coverage.

### Phase 2: Enum Migration
- **Step 2.1**: Define `AtomEvaluationStatus(StrEnum)` in `@[backend_v2/models/enums.py]`.
- **Step 2.2**: Update all DTOs in `@[backend_v2/models/dtos/atom_evaluation.py]` to use the new Enum.

### Phase 3: SDUI Localization ("N/A" Eradication)
- **Step 3.1**: Remove `"N/A (Lightweight extraction)"` default texts. Return `None` if data is missing.
- **Step 3.2**: Verify that Flutter `.arb` configurations correctly handle `None` values to provide localized fallbacks. `localization_compiler.py` MUST NOT inject fallbacks.

### Phase 4: Frontend Synchronization
- **Step 4.1**: Update Flutter models in `@[client_app_v2/lib/core/models/enums.dart]` to reflect the new Enums.
- **Step 4.2**: Run Flutter build runner.

### Phase 5: Verification & E2E Integration Gate
- **Step 5.1**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- **Step 5.2**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

## 4. Definition of Done (DoD) & Verification Plan
- No `Literal` string states in `backend_v2/models/dtos/atom_evaluation.py`.
- No `"N/A"` hardcoded strings in backend DTOs.
- `flutter_audit_loop.py` compiles successfully with the new Enums.
- E2E Tests pass.
