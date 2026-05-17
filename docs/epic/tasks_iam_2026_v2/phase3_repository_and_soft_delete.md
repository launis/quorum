# Phase 3: Repository, Tenant Isolation & Soft Delete

**Source:** Epic EPIC-IAM-003, Sections 5 & 6
**Objective:** Implement the TinyDB repository layer ensuring 100% Python-level Tenant Isolation (as prep for Prod RLS) and GDPR Soft Delete.

## 🛑 Architectural Invariants (From .agents/rules)
* **Rule 1 (Zero ORM Bleed):** The Repository layer is an absolute firewall. Raw records MUST be mapped into strict Pydantic Domain Models (`ConfigDict(frozen=True)`).
* **Rule 2 (Flat 1:1 Identity):** Do not create N:M tables. User -> org_xxx mapping is flat.
* **Rule 3 (Local vs Prod Awareness):** TinyDB does not have RLS. Isolation must be explicitly coded in `.search()` queries.

## 🎯 Target Scope
* **TARGET (Modify):** `backend_v2/repositories/user_repository.py` (Create/Update)
* **TARGET (Modify):** `backend_v2/api/routers/system_webhooks.py` (Create/Update)

## 🛠️ Implementation Steps

### 1. Create UserRepository with Strict Isolation
In `backend_v2/repositories/user_repository.py`:
* Create method `get_user_by_uid_and_org(uid: str, org_id: str) -> UserDTO`.
* For TinyDB, implement explicit filtering: `User.search((where('id') == uid) & (where('organization_id') == org_id))`.
* Add a Python comment `TODO(PROD): PostgreSQL RLS will handle this via SET LOCAL quorum.current_org = org_id. Keep Python filter for defense-in-depth.`
* Return frozen `UserDTO` strictly validated.

### 2. Implement Soft Delete Logic
In `backend_v2/repositories/user_repository.py`:
* Implement `soft_delete_user(uid: str)`.
* It MUST NOT execute physical delete. It must update `deleted_at = NOW()` and anonymize `email = f"deleted_{uid}@quorum.local"`.

### 3. Firebase Webhook Endpoint
In `backend_v2/api/routers/system_webhooks.py`:
* Create `POST /api/v2/system/webhooks/firebase-delete`.
* Extract `uid` and call `user_repo.soft_delete_user(uid)`.

## 🧪 Testing & Quality Gate Plan
* **Integration Tests (`tests/integration/test_user_repo_tinydb.py`):**
  * Insert user, verify `get_user_by_uid_and_org` returns the user.
  * Verify querying with WRONG org_id returns `None` (Validating TinyDB isolation).
  * Call soft delete, verify email is anonymized and `deleted_at` is set.
* **Verification:** `uv run python scripts/backend_audit_loop.py backend_v2/repositories/user_repository.py --test`

---
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/iam_2026_v2_tracker.md`
