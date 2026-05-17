# Phase 4: API Security Guards & Throttling

**Source:** Epic EPIC-IAM-003, Sections 2 & 4
**Objective:** Implement the bulletproof `require_role` FastAPI Dependency to act as the ultimate zero-latency API firewall, integrating the CacheService Kill-Switch.

## 🛑 Architectural Invariants (From .agents/rules)
* **Rule 1 (Fail-Fast):** If the Redis Kill-Switch triggers or Tenant IDs don't match, raise `AppException(ErrorCodes.FORBIDDEN)` or `UNAUTHORIZED` immediately.
* **Rule 2 (Strict Dependency Injection):** Dependencies MUST be injected exclusively via FastAPI's `Depends()`.

## 🎯 Target Scope
* **TARGET (Modify):** `backend_v2/core/security.py` (Create/Update)
* **CONTEXT (Read-Only):** `backend_v2/services/cache_service.py`

## 🛠️ Implementation Steps

### 1. Implement `get_quorum_jwt`
In `backend_v2/core/security.py`:
* Extract `Bearer` token from HTTP Header.
* Decode local JWT. If expired or invalid, raise `AppException(ErrorCodes.UNAUTHORIZED)`.
* Parse into strictly validated `QuorumTokenData`.

### 2. Implement `require_role` Guard
In `backend_v2/core/security.py`:
* Implement `def require_role(allowed_roles: list[UserRole]):` returning a dependency function.
* Step 1: Check `CacheService.is_blacklisted(token.sub)`. If true -> 401.
* Step 2: Root bypass (`token.role == ROOT`).
* Step 3: Role check (`token.role in allowed_roles`).
* Step 4: Tenant Isolation (`token.org == x_org_id` header). If false -> 403.

### 3. Implement Rate Limiter Guard
In `backend_v2/core/security.py`:
* Implement `def rate_limit_ai(max_requests: int):` returning a dependency.
* Check `CacheService.increment_rate_limit(token.org)`. If > max_requests -> 429.

## 🧪 Testing & Quality Gate Plan
* **Unit Tests (`tests/unit/test_security_guards.py`):**
  * Mock `CacheService` to return `True` for blacklist, assert `require_role` raises 401.
  * Provide mismatched `x_org_id`, assert 403.
  * Trigger rate limit > max, assert 429.
* **Verification:** `uv run python scripts/backend_audit_loop.py backend_v2/core/security.py --test`

---
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/iam_2026_v2_tracker.md`
