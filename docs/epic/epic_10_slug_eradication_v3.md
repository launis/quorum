# Epic 10: The Definitive V3 Slug Eradication & Opaque ID Hardening

> [!IMPORTANT]
> **AI AGENT DIRECTIVE (ANTIGRAVITY V1.21.6+ PROTOCOL)**
> This is a Tier 2 Execution Epic. You must execute this document directory by directory according to the `docs/reference.md` structure. Do not proceed to the next phase without confirming the current one via the "PERMISSION GRANTED" loop from the user.
> 
> **MANDATORY HARDENING SYNERGY (Double-Purge):** Every directory and file touched during this Epic *MUST* mathematically comply with the strict architectural constraints defined in `docs/hardeningback.md` (e.g., No Naked Dicts, Strict Pydantic, No Raw Exceptions, TaskGroups, @override) and `docs/hardeningfront.md` (e.g., Isolate.run, No Empty Catches, UI .arb Strings). Do not consider a file refactored for "Slug Eradication" until it also passes its respective Hardening Audit.

**Context:** Quorum V2/V3 Backend (FastAPI, Python, Arq/Redis) & Frontend (Flutter Riverpod, GoRouter)
**Core Mandate:** The "Zero-Compromise Fail-Fast Pledge" (RFC 7807), The Opaque Stripe ID Pattern & Distributed Observability Hardening.

## 1. Tactical Objective
The database is already seeded correctly with Opaque Stripe IDs (`blk_...`, `syscfg_...`). The "slug" property must remain in models for URLs and SEO, but it is **strictly forbidden** to use `slug` as a database lookup key, API identifier, internal relational link, telemetry index, or external Webhook payload key.
Your objective is to globally decouple the system from `slug`-based logic and enforce ID-based lookup and data transmission across the database, routing, background workers, enterprise observability layer, and Flutter client storage.

## 2. Directory-by-Directory Execution Phases

> [!WARNING]
> DO NOT BATCH THESE PHASES. Request explicit permission to proceed after completing each phase.

### Phase 1: The Seed Data Relational Audit
**Target Directory:** `backend_v2/seed/`
**Directive:** The IDs in `seed_data.json` are already Opaque Stripe IDs. Your task is to audit internal cross-references.
*   **Action:** If task blueprints or related links (e.g., `task_blueprint: "matrix_risk"`) still point to slugs, replace them with the corresponding Stripe ID (`task_blueprint: "blk_371c..."`).

### Phase 2: Domain Modeling & Pydantic Hardening
**Target Directory:** `backend_v2/models/`
**Directive:** Make the Pydantic schemas enforce the Opaque ID format intrinsically.
*   **Action:** Ensure relations (`task_blueprint`, `profile_id`) operate solely on IDs.
*   **Fail-Fast Mandate:** Impose strict Regex matching on the main `id` field within Pydantic V2 models. Submissions with a simple slug in the `id` field must immediately trigger an HTTP 422 Fail-Fast response. Allowed format examples: `org_[...], blk_[...], syscfg_[...]`.

### Phase 3: The Unified Repository & Environment Data Strategy
**Target Directory:** `backend_v2/database/`
**Directive:** Realign CRUD operations away from slug lookups and define environment-specific DB handling.
*   **Action:** Ensure DB repositories offer `get_by_id` logic. If `by_slug` exists, verify it is *exclusively* for resolving human-readable aliasing, never for internal Orchestrator mapping.
*   **Local State Reset:** Instruct the user to Wipe the local databases (`data/db_v2.json`, Firestore Dev) and run the Reseed command. This guarantees corrupted local cache states do not interfere with tests.
*   **Staging & Production Strategy:** Document whether Staging/Production databases will be fully wiped (permitted at this lifecycle stage) OR if a one-off Migration Script must be written to convert live slug relations into Stripe IDs. Do not proceed to higher environments without resolving this decision.

### Phase 4: Business Logic, Orchestrator & Background Workers
**Target Directory:** `backend_v2/services/` & `backend_v2/workers/`
**Directive:** Decouple Orchestrator graph generation, resolution, and Arq/Redis asynchronous background job payloads from slugs.
*   **Action (Synchronous):** Ensure logic in `orchestrator/strategies/` does not fetch nodes via variables like `blueprint_slug`. Refactor internal calls to extract the ID (`getattr(step, "task_blueprint_id")`).
*   **Action (Asynchronous Workers):** Audit the AI-DAG payloads sent to Arq/Redis background workers. Worker serialization schemas (Pydantic/dicts) must explicitly drop slug references and ONLY transmit Opaque IDs. Background workers must fetch DB context solely by Stripe ID.

### Phase 5: FastAPI Control Plane & Path Validators
**Target Directory:** `backend_v2/api/routers/`
**Directive:** Shield the endpoints from incorrect URL parameter formats.
*   **Action:** Ensure `/{slug}` is completely eradicated from state-mutating or core GET paths; upgrade them to `/{id}`.
*   **Fail-Fast Mandate:** Attach Path validators to FastAPI `/{id}` variables. If the shape does not match an Opaque Stripe ID, DO NOT pass the error down into a `try-except` block. Raise an `AppException` (RFC 7807) immediately.

### Phase 6: Core Engine Defensiveness & Negative Testing
**Target Directory:** `backend_v2/tests/`
**Directive:** Validate the Epic so far using rigorous regression testing.
*   **Action 1:** Refactor existing tests simulating API payloads to pass Stripe IDs (`id="pb_test_123"`) instead of slugs (`slug="test"`).
*   **Action 2:** Create purposeful negative tests. Write asserts that intentionally attempt to alter state or fetch entities using `id="holistic_audit"`. Ensure these crash explicitly with 422 or RFC 7807 (Fail-Fast validated).

### Phase 7: Flutter Client - Core API
**Target Directory:** `client_app_v2/lib/core/`
**Directive:** Re-align client REST connections.
*   **Action:** Update `studio_client.dart` endpoint definitions to correctly utilize the new `by-id` parameter paradigm targeting the refactored FastAPI backend routes.

### Phase 8: Flutter GoRouter & Hybrid URLs
**Target Directory:** `client_app_v2/lib/router/`
**Directive:** Keep the URLs SEO-friendly while relying on IDs under the hood.
*   **Action:** Implement the Hybrid URL Pattern (`path: 'workflow/edit/:id/:slug'`). 
*   **Durability Check:** Program the Router/Controller to extract ONLY the `:id` parameter for API requests. Treat `:slug` strictly as unbreakable cosmetics. Verify that mutating `:slug` via the browser's address bar does not trigger re-renders, 404s, or state losses.

### Phase 9: Riverpod State, Caching & Local Storage Invalidation
**Target Directory:** `client_app_v2/lib/features/` & `l10n`
**Directive:** Enforce ID-driven UI cache and Red-Screen mitigation across both in-memory and persistent storage.
*   **Caching Hardening:** Audit all Riverpod Providers (`family` modifiers). Crucially ensure `family` cache keys inject the Opaque Stripe ID. Disobeying this breaks the Optimistic UI Stale-While-Revalidate (SWR) architectural mandate.
*   **Persistent Storage Invalidation:** SharedPreferences, Hive, or SecureStorage keys relying on legacy slugs (e.g., `last_workspace_slug`) must be programmatically invalidated/migrated on startup to prevent Red Screens upon app launch.

### Phase 10: Telemetry, Observability & B2B Webhooks (System Edge)
**Target Directory:** `backend_v2/telemetry/` & `backend_v2/webhooks/`
**Directive:** Ensure data leaving the primary execution loop (logs, traces, external payloads) respects strict ID rules.
*   **Distributed Tracing:** Ensure that centralized telemetry engines (Pydantic Logfire, OpenTelemetry) utilize ONLY Opaque Stripe IDs (e.g., `execution_id`) as `ContextVars` and distributed tracing identifiers. Slugs must never be indexed in analytics, as they fragment error tracking.
*   **B2B Webhooks:** Outbound API calls to Client CRM/ERP systems (e.g., lifecycle events like `COMPLETED` or `FAILED`) must transmit Opaque IDs exclusively as reference keys, training client integrations to adapt instantly to the new primary key architecture.

---

## 3. The Definition of Done (Final Audit)

> [!TIP]
> **Agent Execution Checklist**
> Before marking this Epic complete and requesting the final sign-off, run the following verification checks using the workspace terminal or your `grep_search` capabilities.

1.  **Global Regex Audit:** Execute `grep -rn "by_slug"` across `backend_v2/database/`, `backend_v2/services/`, and `backend_v2/workers/`. Confirm output is strictly empty or highly scrutinized.
2.  **Eq-Check Audit:** Verify that no queries containing `== slug` or `== blueprint_slug` exist in database repositories. These must use the `_id` suffix.
3.  **Observability Audit:** Verify that log formatting injects Stripe IDs and actively redacts indexable slugs from core metadata.
4.  **Hardening Synergy Audit:** The Agent must explicitly state that the affected subdirectories successfully passed the strict checks dictated in `hardeningback.md` and `hardeningfront.md` by replicating the required validation checkboxes from those documents.
5.  **UI State Stability:** Once all 10 Phases pass with the "PERMISSION GRANTED" loop, the application is effectively immune to slug-pollution internally and across B2B integrations.
