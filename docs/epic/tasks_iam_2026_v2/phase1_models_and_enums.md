# Phase 1: Pydantic Models & Enums (IAM Foundation)

**Source:** Epic EPIC-IAM-003, Sections 1 & 2
**Objective:** Establish the strictly typed Pydantic V2 models and Enums for the new IAM architecture, enforcing Opaque IDs and Fail-Fast validation.

## 🛑 Architectural Invariants (From .agents/rules)
* **Rule 1 (Pydantic Strict Protocol):** All models MUST use `model_config = ConfigDict(strict=True, extra="forbid")`. No silent coercion or legacy dictionaries.
* **Rule 2 (Opaque Stripe ID Mandate):** Organization IDs must follow `org_[a-zA-Z0-9]{8,}`. Do not use auto-increment or slugs for relations.
* **Rule 3 (Data Leak Prevention):** DTOs returning data to the client MUST explicitly drop database internal properties to prevent cross-tenant trace leaks.

## 🎯 Target Scope
* **TARGET (Modify):** `backend_v2/models/iam.py` (Create/Update)
* **TARGET (Modify):** `backend_v2/models/enums.py` (Create/Update)

## 🛠️ Implementation Steps

### 1. Define strict `UserRole` Enum
In `backend_v2/models/enums.py`:
```python
class UserRole(str, Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"
```

### 2. Define `QuorumTokenData` Pydantic Model
In `backend_v2/models/iam.py`:
* Define `QuorumTokenData(BaseModel)`.
* Include `sub` (str, Firebase UID), `org` (str, Opaque ID regex: `^org_[a-zA-Z0-9]{8,}$`), `role` (UserRole), and `exp` (int).
* Enforce `ConfigDict(strict=True, extra="forbid")`.

### 3. Define `UserDTO` and Authentication DTOs
In `backend_v2/models/iam.py`:
* Define `TokenExchangeRequest(BaseModel)` containing `firebase_id_token` (str).
* Define `TokenExchangeResponse(BaseModel)` containing `quorum_token` (str) and `expires_in` (int).
* Define `UserDTO(BaseModel)` representing the flat 1:1 user object for API responses.

## 🧪 Testing & Quality Gate Plan
* **Unit Tests (`tests/unit/test_iam_models.py`):**
  * Instantiate `QuorumTokenData` with invalid `org` (e.g. `org_123` instead of length 8) and assert `ValidationError`.
  * Instantiate models with extra fields and assert `ValidationError` (`extra=forbid`).
* **Verification:** `uv run python scripts/backend_audit_loop.py backend_v2/models/iam.py --test`

---
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/iam_2026_v2_tracker.md`
