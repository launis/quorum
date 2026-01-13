SYSTEM CONTEXT & ARCHITECTURE MANDATE (2026 Edition)

PROJECT: Cognitive Quorum (Monorepo: Python Backend + Flutter Client)
CURRENT DATE: 2026-01-01
STATUS: Phase 2 (Hardening Architecture & Error Handling)

--------------------------------------------------------------------------------
⚠️ STRICT DEPENDENCY & PATTERN PROTOCOL
The dependencies listed below are ALREADY DEFINED in the project's `pubspec.yaml`.
DO NOT ask to install them again unless they are missing.

YOUR CORE TASK:
Use the **LATEST FEATURES** and **MODERN BEST PRACTICES** associated with these specific versions.
Legacy patterns (e.g., `ChangeNotifier`, manual providers, `setState` for complex logic) are STRICTLY FORBIDDEN.
--------------------------------------------------------------------------------

TECHNOLOGY STACK & VERIFIED DOCUMENTATION LINKS:

1.  **Framework & Core**:
    * **Flutter 3.38+** (Stable): [https://docs.flutter.dev/]
        * *Requirement*: Use latest Material 3 widgets, Adaptive Scaffold, and `dart:ui` features.
        * *Requirement*: **STRICT ADHERENCE TO BREAKING CHANGES**. Consult [https://docs.flutter.dev/release/breaking-changes] regulary.
        * *Requirement*: Immediate migration of deprecated APIs (e.g., `RadioListTile` -> `RadioGroup`).

2.  **State Management (The Brain)**:
    * **Riverpod ^3.0.0** (with `riverpod_annotation`): [https://riverpod.dev/] & [https://riverpod.dev/docs/whats_new]
        * *Requirement*: **STRICT GENERATOR ONLY (Class-Based & Functional)**.
            *   Manually defined defaults (`Provider`, `FutureProvider`, `StreamProvider`, `StateNotifierProvider`) are **BANNED**.
            *   **Reasoning**: Prevents "provider desync", ensures correct overrides, eliminates boilerplate.
        * *Requirement*: **Declarative vs Imperative** (The "What's New" Philosophy).
            *   **DO NOT** manually `.listen()` to streams inside a Notifier to set state (Imperative).
            *   **DO**: Create a dependency provider (`@riverpod Stream<T>`) and `ref.watch()` it in the UI or another provider (Declarative).
        * *Requirement*: **AsyncValue Everywhere**.
            *   All async state must use `AsyncValue<T>`. Never use custom `isLoading` booleans.
            *   Use `.when()` or `.value` for UI rendering.
        * *Requirement*: **Side Effects via Mutation**.
            *   Controllers (`@riverpod class`) are for **Actions** (void methods modifying backend/state).
            *   Providers (`@riverpod function`) are for **Data** (fetching/computing).

3.  **Routing (The Navigation)**:
    * **GoRouter ^17.0.1**: [https://pub.dev/packages/go_router]
        * *Requirement*: Use `StatefulShellRoute` for persistent bottom navigation.
        * *Requirement*: Implement Type-safe routes (`GoRouteData`) if possible.
        * *Requirement*: Auth Guard must use `ref.watch` (Reactive Redirection).

4.  **Authentication & Backend**:
    * **Firebase Auth ^6.1.3**: [https://firebase.google.com/docs/auth/flutter/start]
    * **Firebase UI Auth**: [https://pub.dev/packages/firebase_ui_auth]
        * *Requirement*: Use generic `AuthInterceptor` to inject tokens into Python Backend calls.

5.  **UI & Localization**:
    * **FlexColorScheme**: [https://docs.flexcolorscheme.com/]
        * *Requirement*: Use distinct themes for Light/Dark modes using this package.
    * **Visual Identity (Brand DNA)**:
        * *Primary Color*: **Deep Purple** (Seed: #673AB7). Represents Intelligence & AI.
        * *Typography*: **Inter** (via `google_fonts`). Clean, legible sans-serif for high-density data.
        * *Style*: Material 3 with professional SaaS aesthetics (rounded corners, high contrast).
    * **Intl & Flutter Localizations**: [https://docs.flutter.dev/ui/internationalization]
        * *Requirement*: **Multi-language Support (FI/EN)**. The app must support Finnish and English immediately.
        * *Requirement*: All strings must be in `.arb` files. No hardcoded strings allowed.
    * **Error Message Hygiene**: NEVER pass hardcoded string literals to `AppError.validation()` or any error constructor.
        * *Requirement*: Client-side validation errors must use `AppLocalizations` getters (e.g., `l10n.fieldRequired`).
        * *Requirement*: Backend errors must be mapped from `error_code` to `.arb` keys. Do not rely on backend `message` strings unless they are guaranteed to be user-facing and localized.

6.  **Documentation & Code Quality**:
    * **DartDoc Standard**: [https://dart.dev/effective-dart/documentation]
        * *Requirement*: "Code-to-Doc" ready. All public Classes, Providers, and Repositories MUST have `///` documentation comments.
        * *Requirement*: Comments must explain the **WHY** and the **BUSINESS LOGIC**, not just restate the function name.
        * *Requirement*: Use markdown in comments (e.g., `[MyClass]`, code blocks) to ensure generated HTML docs are navigable.

7.  **Adaptive & Responsive Design (Strict Mandate)**:
    * **Philosophy**: "Write once, adapt everywhere." The app must look professional on Mobile, Tablet, and Desktop/Web.
    * **Navigation Architecture**:
        * *Requirement*: Implement a responsive shell. Use `NavigationBar` (Bottom) for width < 600dp and `NavigationRail` (Left) for width > 600dp.
    * **Content Layout**:
        * *Requirement*: **Content Constraint**. NEVER allow text or forms to stretch full-width on large screens. Wrap body content in `Center` > `ConstrainedBox(maxWidth: ~1000)`.
    * **Grids**:
        * *Requirement*: Use `SliverGridDelegateWithMaxCrossAxisExtent` to automatically add columns on wider screens.

8.  **Logging & Observability Mandate (Backend)**:
    * **No Manual Printing**: `print()` usage is FORBIDDEN in production code. Use the standard `logging` module.
    * **Standard Logger**: Always instantiate `logger = logging.getLogger(__name__)`.
    * **Routing Policy**:
        * **INFO/DEBUG/WARNING**: Routed to `logging_config.py` handlers (File: `backend_debug.log` / Stream).
        * **ERROR/CRITICAL**: Must include `exc_info=True` for stack traces.
    *   "Environment Config": Log file location is controlled via `LOG_FILE_NAME` env var.
    *   "Cloud-Native": Assume logs are scraped from `stdout`. File writing is secondary/local-only.

9.  **Backend Code Quality & Standards (Python)**:
    *   **Linter**: Code MUST pass `ruff check` with zero errors. No exceptions.
    *   **Formatter**: Code MUST be formatted via `ruff format`.
    *   **Pre-Commit**: Always run `uv run ruff check .` and `uv run pytest` before submitting changes.
    *   **Mypy Type Checking**: Code MUST pass `uv run mypy backend` with zero errors.

10. **Database Strategy (Hybrid Mandate)**:
    *   **Source of Truth**: Treat Firestore as the primary design target for data models.
    *   **Async-First**: All repository methods MUST be designed for Firestore's async nature first.
    *   **Dual Support**: However, you MUST maintain functional TinyDB support for local development and testing alongside Firestore. Both databases are used for everything.
    
11. **Cloud-Native & Hosting Strategy (Long-Term Mandate)**:
    *   **Metric**: "Design for the Cloud, Run Locally."
    *   **Goal**: The long-term objective is to deploy a fully hosted Cloud SaaS solution for both the Flutter Client and the Backend.
    *   **Requirement**: The software MUST implement this readiness *immediately*.
    *   **Implication**: Strict Statelessness. Do not rely on local filesystem for shared state (use Storage/DB). Do not hardcode `localhost` references in production logic. Ensure containerization compatibility.

ARCHITECTURAL RULES (ENFORCED):
1.  **Monorepo Context**: You are working in `client_app/`. The backend is in `backend/`.
2.  **API Strategy**: The Flutter app DOES NOT touch the database directly. It talks to the Python API (`http://localhost:8000`).
3.  **Code Style**:
    * Use `fpdart` for functional error handling. **Repositories MUST return `Future<Either<AppError, T>>` instead of throwing exceptions.**
    * Prioritize Composition over Inheritance.
    * Always verify imports (no relative imports for different feature modules).

5.  **Testing Strategy (Strict Mandate)**:
    *   **Library**: **Mocktail (^1.0.4+)** is the ONLY permitted mocking library for new tests.
    *   **Legacy**: `mockito` is DEPRECATED. Do not add new `mockito` dependencies or generatable mocks. Refactor to `mocktail` when touching legacy tests.
    *   **Why**: No code generation (`build_runner`) required for tests, type-safe `any()`, and cleaner API.
    *   **Pattern**: Register fallbacks in `setUpAll` or `setUp` if needed. Use `registerFallbackValue`.

12. **API & Error Handling Mandate (Strict Protocol)**:
    *   **Backend Implementation Rules**:
        *   **BANNED**: NEVER raise raw Python exceptions (`ValueError`, `RuntimeError`, `FileNotFoundError`) for business logic or domain failures.
            *   *Why*: They produce generic `500 Internal Server Error` responses with `INTERNAL_SERVER_ERROR` codes, hiding the true cause from the client.
        *   **REQUIRED**: Always raise distinct classes from `backend.exceptions`:
            *   `ResourceNotFoundError` (404): When an ID is not found.
            *   `ConfigurationError` (500): When settings/env/secrets are missing (Stop immediately).
            *   `FatalInterruption` (500): When a workflow step fails critically.
            *   `AppException` (Custom): For all other logical failures.
        *   **Logging vs. Raising**:
            *   **Raising**: Is for *Control Flow* (Stopping execution).
            *   **Logging**: Is for *Observability* (Debugging).
            *   *Rule*: If you `raise`, the Global Exception Handler (`backend/main.py`) will automatically log the error. You do NOT need to manually log before raising, unless adding specific context variables.
    *   **The Contract (JSON Schema)**:
        *   All errors return: `{ "error_code": "SCREAMING_SNAKE_CASE", "message": "Human readable", "details": {...} }`.
        *   `error_code` is derived automatically from the Exception Class Name (e.g. `BudgetExceededError` -> `BUDGET_EXCEEDED_ERROR`).
    *   **Frontend Consumption Rules**:
        *   **BANNED**: Detecting errors by regex-matching the `message` string (e.g. `if (e.message.contains("Not Found"))`).
        *   **REQUIRED**: Switch on the standardized `error_code` (e.g. `if (e.code == 'RESOURCE_NOT_FOUND_ERROR')`).
        *   **REQUIRED**: All API calls must be wrapped in a Repository handler that maps Dio `Response` to `AppError` domain objects.

GOAL:
Build a production-grade, multi-tenant SaaS client. If a solution implies technical debt or "the old way of doing things", REJECT IT and propose the scalable, modern solution based on the documentation links above.

IMPORTANT:
Do not implement or plan to implement any functions or features based on SYSTEM CONTEXT & ARCHITECTURE MANDATE (2026 Edition) at this stage. This document is provided for CONTEXT and GUIDANCE ONLY to ensure future code aligns with the architecture.


# 🛑 STOP! READ THIS CAREFULLY 🛑

**THIS DOCUMENT IS A CONTEXT REFERENCE ONLY.**

**DO NOT START ANY IMPLEMENTATION OR GENERATE CODE BASED ON THIS FILE YET.**

**STORE THIS CONTEXT IN YOUR MEMORY AND AWAIT FURTHER INSTRUCTIONS.**
