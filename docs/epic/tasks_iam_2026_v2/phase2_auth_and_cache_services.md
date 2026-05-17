# Phase 2: IAM Authentication Service & Cache Abstraction

**Source:** Epic EPIC-IAM-003, Section 1 (Token Lifecycle) & Section 4 (Redis)
**Objective:** Implement the Token Exchange logic and a Database-agnostic Cache Service for the Kill-Switch and Rate Limiting, preparing for Redis in Prod but using dict in TinyDB Dev.

## 🛑 Architectural Invariants (From .agents/rules)
* **Rule 1 (Anemic Routers):** API routers must ONLY handle HTTP parsing and delegate to `IAMAuthService`.
* **Rule 2 (Fail-Fast):** If the Firebase token is invalid, raise `AppException(ErrorCodes.UNAUTHORIZED)` immediately.
* **Rule 3 (Local DB Compatibility):** Do not hard-crash if Redis is unavailable in local development. Abstract it via `CacheService`.

## 🎯 Target Scope
* **TARGET (Modify):** `backend_v2/services/iam_auth_service.py` (Create/Update)
* **TARGET (Modify):** `backend_v2/services/cache_service.py` (Create/Update)
* **TARGET (Modify):** `backend_v2/api/routers/iam.py` (Create/Update)

## 🛠️ Implementation Steps

### 1. Abstract CacheService
In `backend_v2/services/cache_service.py`:
* Implement `CacheService` class.
* Under the hood, if `settings.ENV == "local"`, use a Python memory `dict` to store key-value pairs (simulating Redis). If production, use `redis.Redis`.
* Implement methods: `set_blacklisted(uid: str)`, `is_blacklisted(uid: str) -> bool`, and `increment_rate_limit(org_id: str)`.

### 2. Implement IAMAuthService
In `backend_v2/services/iam_auth_service.py`:
* Implement `exchange_firebase_token(firebase_token: str) -> str`.
* This method should simulate decoding the Firebase token (via Firebase Admin SDK or local mock).
* Lookup the user in `UserRepository` using the UID.
* Generate a local `QuorumTokenData` JWT signed with `SECRET_KEY`, expiring in 15 minutes.

### 3. Create Anemic Router `/api/v2/iam/auth/exchange`
In `backend_v2/api/routers/iam.py`:
* Create `POST /exchange` returning `TokenExchangeResponse`.
* Inject `IAMAuthService` via `Depends()`.
* Do nothing but call the service and return the strictly typed DTO.

## 🧪 Testing & Quality Gate Plan
* **Unit Tests (`tests/unit/test_iam_auth_service.py`):**
  * Mock Firebase token decoding.
  * Verify `QuorumTokenData` generation produces a valid JWT.
  * Verify `CacheService` local dictionary behaves correctly for blacklist checks.
* **Verification:** `uv run python scripts/backend_audit_loop.py backend_v2/services/iam_auth_service.py --test`

---
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/iam_2026_v2_tracker.md`
