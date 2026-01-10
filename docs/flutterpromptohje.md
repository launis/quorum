SYSTEM CONTEXT & ARCHITECTURE MANDATE (2026 Edition)

PROJECT: Cognitive Quorum (Monorepo: Python Backend + Flutter Client)
CURRENT DATE: 2026-01-01
STATUS: Phase 2 (Building the Scalable Flutter Client)

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

2.  **State Management (The Brain)**:
    * **Riverpod ^3.0.0** (with `riverpod_annotation`): [https://riverpod.dev/] & [https://riverpod.dev/docs/whats_new]
        * *Requirement*: STRICT Generator Mode (`@riverpod`).
        * *Requirement*: Use `Ref` instead of `WidgetRef` in logic classes.
        * *Requirement*: All async operations must return `AsyncValue<T>`.

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

ARCHITECTURAL RULES (ENFORCED):
1.  **Monorepo Context**: You are working in `client_app/`. The backend is in `backend/`.
2.  **API Strategy**: The Flutter app DOES NOT touch the database directly. It talks to the Python API (`http://localhost:8000`).
3.  **Code Style**:
    * Use `fpdart` for functional error handling where appropriate.
    * Prioritize Composition over Inheritance.
    * Always verify imports (no relative imports for different feature modules).

GOAL:
Build a production-grade, multi-tenant SaaS client. If a solution implies technical debt or "the old way of doing things", REJECT IT and propose the scalable, modern solution based on the documentation links above.

IMPORTANT:
Do not implement or plan to implement any functions or features based on SYSTEM CONTEXT & ARCHITECTURE MANDATE (2026 Edition) at this stage. This document is provided for CONTEXT and GUIDANCE ONLY to ensure future code aligns with the architecture.


# 🛑 STOP! READ THIS CAREFULLY 🛑

**THIS DOCUMENT IS A CONTEXT REFERENCE ONLY.**

**DO NOT START ANY IMPLEMENTATION OR GENERATE CODE BASED ON THIS FILE YET.**

**STORE THIS CONTEXT IN YOUR MEMORY AND AWAIT FURTHER INSTRUCTIONS.**
