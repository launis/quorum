# Architectural Assessment & Improvement Proposal (Feb 2026)

**Auditor:** Antigravity (Google Deepmind)
**Target:** `docs/flutterpromptohje.md` (System Architecture Manifesto)

## 1. Executive Summary

The "System Architecture Manifesto" (V2026) establishes a robust, discipline-first culture ("Zero-Magic", "Fail Fast"). The "Dual Sovereign" localization and "SDUI" patterns are forward-thinking. However, the **Dual Backend Parity** requirement and the **Fuzzy Matching** pattern for LLM localization present significant scalability and reliability risks.

This proposal recommends three high-impact architectural refactors to align with the project's "Standardization" phase.

---

## 2. Key Findings & Critique

### 2.1 ⚠️ Risk: LLM Localization via Fuzzy Matching
*   **Current State:** The "Backend Localization Pattern" (Part 12) relies on `_map_l10n_values` to fuzzy-match LLM string outputs (e.g., "Korkea Riski") back to logic values (e.g., `3.0`).
*   **Critique:** This violates the "Zero-Magic" philosophy. It assumes the LLM will output a string that *fuzzy matches* one of the localized keys. If the LLM produces a synonym or a slightly different inflection (e.g., "Erittäin Korkea Riski"), the logic fails or falls back unpredictably. It entangles *Presentation* (Localized String) with *Logic* (The actual value).
*   **Severity:** High (Reliability & Determinism).

### 2.2 ⚠️ Risk: Dual Repository Implementation Burden
*   **Current State:** The "Repository Parity Mandate" requires *any* database modification to be implemented manually in both `repository.py` (TinyDB) and `firestore_repo.py`.
*   **Critique:** This is a violation of the DRY (Don't Repeat Yourself) principle at the architectural level. It doubles the surface area for bugs and guarantees that the two implementations will eventually diverge in subtle behavioral ways (e.g., how they handle sorting, filtering, or partial updates), breaking the "Worker Environment Parity" goal.
*   **Severity:** Medium (Maintenance Debt).

### 2.3 ⚠️ Risk: Testing Gaps for Parity
*   **Current State:** The manifesto emphasizes "Routine Quality Gates" (Linting/Types) but lacks a specific mandate for *Behavioral Parity Testing*. "Sitra Integration Test" is mentioned, but not a systematic matrix.
*   **Critique:** Without automated enforcement, the "Dual Backend" rule relies entirely on developer discipline, which is prone to error under pressure.

---

## 3. Improvement Proposals

### 3.1 ✅ Solution: Schema-Enforced Canonical Codes (Replace Fuzzy Matching)
**Pattern:** "Logic First, Presentation Second".
Instead of asking the LLM for "Low Risk" (String) and trying to parse it, force the LLM to output a **Canonical Enum Code** (e.g., `RISK_LOW`).

**Implementation:**
1.  **Define Pydantic Enum:**
    ```python
    class RiskLevel(str, Enum):
        LOW = "RISK_LOW"
        MEDIUM = "RISK_MEDIUM"
        HIGH = "RISK_HIGH"
    ```
2.  **Enforce Structure:** Use LiteLLM's `response_format` or Pydantic validation to ensure the LLM *only* returns these codes, regardless of the prompt language.
3.  **Localize on Read:** The Backend or Frontend maps `RISK_LOW` -> `LocalizationService.translate("risk.low")`.

**Benefit:**
*   **Determinism:** 100% guarantee of valid logic values.
*   **Simplicity:** Removes `_map_l10n_values` and fuzzy logic entirely.
*   **Separation:** The LLM "thinks" in concepts (Codes), the UI shows language (Strings).

### 3.2 ✅ Solution: The "Storage Driver" Pattern (Abstract the Parity)
**Pattern:** "Write Logic Once, Swap the Driver".
Refactor the repositories to separate *Business Logic* (Queries, Aggregation) from *Storage Mechanics* (Read/Write JSON vs API).

**Implementation:**
1.  **Create `StorageDriver` Protocol:**
    ```python
    class StorageDriver(Protocol):
        async def get(self, collection: str, id: str) -> dict: ...
        async def query(self, collection: str, filters: list[Filter]) -> list[dict]: ...
        async def upsert(self, collection: str, data: dict) -> None: ...
    ```
2.  **Implement Drivers:** `TinyDBDriver` and `FirestoreDriver`.
3.  **Unified Repository:**
    ```python
    class WorkflowRepository:
        def __init__(self, driver: StorageDriver):
            self.driver = driver
        
        async def get_active_workflows(self):
            # Logic written ONCE. Works on both DBs.
            return await self.driver.query("workflows", [Filter("status", "==", "active")])
    ```

**Benefit:**
*   **Parity:** Guaranteed. The business logic is identical because it's the same code.
*   **Efficiency:** Developers write the query once.
*   **Maintenance:** Adding a 3rd backend (e.g., PostgreSQL) only requires writing a new Driver, not rewriting every single repository method.

### 3.3 ✅ Solution: The "Parity Matrix" CI Pipeline
**Pattern:** "Trust but Verify".
Automate the verification of dual-backend support.

**Implementation:**
1.  **Parametrized Tests:** Update `pytest` fixtures to accept a `db_driver` param.
2.  **CI Job:**
    *   Job 1: `Pytest (TinyDB)` -> Runs all tests using TinyDB.
    *   Job 2: `Pytest (Firestore Emulator)` -> Runs all valid tests using Firestore Emulator.
3.  **Rule:** CI fails if *either* job fails.

**Benefit:**
*   Catches "TinyDB-only" features immediately.
*   Validates that the `FirestoreDriver` implementation correctly mimics the expected behavior.

---

## 4. Immediate Action Plan

1.  **Refactor `docs/flutterpromptohje.md`**: Update "Part 12" to recommend the **Enum Code** pattern instead of Fuzzy Matching.
2.  **Prototype Driver:** Create a proof-of-concept `StorageDriver` interface in `backend/database/driver.py`.
3.  **Update Roadmap:** Add "Migration to Storage Driver Pattern" to Phase 2 (Hardening).
