---
trigger: always_on
description: Desktop-First Flutter and Strict Freezed Mandates
globs: **/*.dart, docs/flutterpromptohje.md
---
# FRONTEND ARCHITECTURE CONSTRAINTS (V5.2 - FLUTTER)

## 1. TOOLING, SCOPING & QUALITY GATES

### 1.1 Primary Audit Loop
Test changes using `uv run python docs\koodit\flutter_audit_loop.py [tiedosto]`. Add `--build` flag ONLY if `@riverpod` or `@freezed` models changed. Alternatively, run `dart run custom_lint` and `dart run build_runner build -d`.

### 1.2 Ignored Files
Never audit or manually edit `.g.dart`, `.freezed.dart`, or `build/` directories.

### 1.3 Environment Logging
Always check `client_debug.log` first when debugging UI or Network failures.

### 1.4 Dependencies
Strictly `flutter_riverpod ^3.1.0`, `go_router ^17.0.1+`, `freezed ^3.2.3`.

### 1.5 Frontend Bans (Non-Negotiable)
<architecture_bans>
  <rule>NO empty catch blocks (`try {} catch (e) {}`). You MUST display an ErrorView, log, and rethrow.</rule>
  <rule>NO `SizedBox.shrink()` to swallow errors or hide broken UI components. Crash audibly using AppErrorBoundary.</rule>
  <rule>NO silent JSON fallbacks (`text ?? "Unknown"`). Missing API data MUST crash the Freezed parser immediately.</rule>
  <rule>NO monolithic "God Widgets". Enforce SRP across Widgets, Notifiers, and Repositories.</rule>
  <rule>NO GoRouter `$extra` object passing. Pass ONLY strings/IDs.</rule>
  <rule>NO manual Riverpod providers. Code Gen `@riverpod` is MANDATORY.</rule>
  <rule>NO Freezed `.when()` or `.map()`. You MUST use native Dart 3 switch matching.</rule>
  <rule>NO full-screen loading spinners. Use Optimistic Updates and mutation states.</rule>
</architecture_bans>

## 2. DESKTOP-FIRST & LAYOUT ARCHITECTURE

### 2.1 PC Breakpoints
1. **>1200dp (PC/Ultrawide):** Three-Pane Layout (Sidebar -> Master List -> Canvas) + Resizable Splitters.
2. **600dp - 1199dp (Tablet/Laptop):** TwoPane Split-Screen.
3. **<600dp (Mobile):** NavigationBar + Stack Navigation.

### 2.2 Information Density
For >600dp, enforce `VisualDensity.compact`. Prefer DataGrids over loose lists. Do not waste space.

### 2.3 Power-User Modalities
Native support for Context Menus, Hover tips, shortcuts (`Ctrl+S`, `Del`), Shift/Ctrl multiselect. Provide touch fallbacks (e.g., Up/Down arrows) for complex drag-and-drop actions.

### 2.4 Keyboard Navigation
Complex layouts MUST use `FocusTraversalGroup` and `FocusNode` for flawless Tab navigation.

### 2.5 Infinite Canvas & Inspector
Do not use static lists for DAG/Workflows. Use `InteractiveViewer` for an Infinite 2D Canvas. Node settings open via a right-side "Inspector" panel.

## 3. RIVERPOD 3.0 & STATE MANAGEMENT

### 3.1 Code Gen Mandate
Only `@riverpod` annotations. Manually written `ChangeNotifier`, `StateProvider`, or old `Provider` logic is BANNED. Use `@riverpod(keepAlive: true)` explicitly when defining standard read-only controllers instead of relying solely on manual state preservation.

### 3.2 Loading Spinners Banned
Full-screen loading spinners are forbidden. Use **Optimistic Updates**.

### 3.3 Mutations & UI Listeners
Use Riverpod 3.0 `Mutation<T>` for side effects (save/delete). Manual UI loading flags (like `bool _isLoading`) are heavily BANNED. Read `.isLoading` from the mutation state. To show SnackBars on error, NEVER embed logic in the `build()` thread. You MUST use hooks or `ref.listen` to intercept error states cleanly without clogging the render tree.

### 3.4 Hybrid Caching
- **SWR (Stale-While-Revalidate):** Use `@riverpod(keepAlive: true)` for Read/Dashboard views to ensure 0ms latency navigation.
- **TTL (Time-To-Live):** Use manual `ref.keepAlive()` with timers for Form inputs to preserve partial states against accidental navigation (e.g., 3 mins).

### 3.5 Flat MVC List
Deliver Master-views as `AsyncNotifier<List<FreezedModel>>`. Detail views fetch data via isolated `IdProvider`s (e.g., `modelRegistryByIdProvider(id)`) to support deep linking perfectly, not by filtering the master list.

### 3.6 Transient Form State
Use `flutter_hooks` (`useTextEditingController`) for typing state. Do NOT dispatch keystrokes to Riverpod directly (prevents Main Thread Jank). Only `submit()` to the Riverpod Mutation.

### 3.7 Frontend Zero Leaks & State Isolation
Riverpod memory must be guarded against State Leaks. Upon Organization or User change (Tenant Isolation), the old cache MUST be safely invalidated (`ref.invalidate()`) to prevent exposing previous tenant data to a new context.

### 3.8 Single Responsibility Principle (The Three Riverpod Boundaries)
The system strictly enforces SRP across three layers:
1. **Widgets (UI ONLY):** Render the screen. No HTTP, no business logic, no heavy parsing.
2. **Notifiers (STATE ONLY):** Coordinate actions and mutate state. Never interact with `BuildContext`.
3. **Repositories (NETWORK ONLY):** Handle HTTP and external APIs.
Monolithic "God Widgets" executing heavy parsing, network calls, and UI building simultaneously are strictly BANNED.

## 4. ROUTER, NAVIGATION & DEEP LINKING

### 4.1 Strongly Typed Routing
Use `GoRouteData`. Native string routing (`context.push('/home')`) is a bug.

### 4.2 Hybrid URL Pattern (Opaque ID)
URLs capture the Stripe Pattern Opaque ID (e.g., `blk_abc123`). Name slugs in URLs are purely cosmetic and ignored by parsing to prevent Link Rot.

### 4.3 $extra Ban
NEVER inject object states through GoRouter `$extra`. Routing must pass ONLY strings/IDs. Target views pull states via Riverpod using the ID.

### 4.4 Guard Clauses
Route protection lives exclusively in GoRouter `redirect`, never in widget `build()`.

### 4.5 Stateful Nested Navigation
For persistent IDE sidebar environments, use `StatefulShellRoute` (or `StatefulShellBranch`) so ongoing tasks don't get destroyed when switching tabs.

## 5. CONCURRENCY & ISOLATE MANDATE (ZERO-LATENCY)

### 5.1 Main Thread Jank Prevention
Heavy JSON parsing, DTO deserialization, and large API payloads MUST be isolated.

### 5.2 Isolate.run()
Always wrap heavy parsing using `final payload = await Isolate.run(() => jsonDecode(chunk));` inside Riverpod asynchronous providers. Do NOT leak or use `Isolate.run()` inside Widget `build()` or UI hooks.

## 6. STRICT FREEZED & DART 3 PATTERN MATCHING

### 6.1 DTO Schema Parity (Fail-Fast Client Firewall & Fallback Ban)
Ensure 100% strict JSON conformity (`disallow_unrecognized_keys: true`). No fallback defaults or empty states for missing server data (e.g., `String text = ""` or `text ?? "Unknown"`) are allowed. This acts as a Client-Side Firewall: if the backend leaks undocumented extra data to the UI, the JSON parser MUST crash immediately to protect client memory. Silent fallbacks are strictly banned.

### 6.2 O(1) Lists
Use native Dart `List<T>` with `@Freezed(equal: false)` to bypass deep equality performance hits on massive lists. Do not inject external immutable collection packages.

### 6.3 Exhaustive Switch (Riverpod Widget Rendering)
Freezed `.when()` or `.map()` are BANNED. Define polymorphic structures as `@Freezed(unionKey: 'type') sealed class`. In Widget `build()` methods handling Riverpod `AsyncValue`, `if-else` chains are BANNED. You MUST always use native Dart 3 `switch` expressions (pattern matching destructuring): `return switch(state) { AsyncData(:final value) => Text(value.id), AsyncLoading() => Spinner(), _ => ErrorBox() };`.

### 6.4 Dart 3 Records (Multiple Returns)
NEVER create arbitrary DTO classes or return `List<dynamic>` just to output multiple values from a repository or service. You MUST use native Dart 3 Records: `(String, int) fetch()` and destructure them synchronously: `final (id, count) = await repo.fetch();`.

## 7. FIREBASE CQRS & ZERO-MATH UI

### 7.1 Read-Only Firebase
The Flutter client is STRICTLY READ-ONLY against Firestore, using `snapshots()` for the zero-latency illusion. All mutations Must be routed through Python FastAPI.

### 7.2 Zero-Math UI
Flutter widgets NEVER calculate complex algorithms. Display states (like gauge indicators and colors) are derived from the `"ui_hints_snapshot"`. Let the Backend `BlueprintTransformer` calculate the math.

### 7.3 Event Rehydration
UI is rendered entirely from the `TraceEvent` log. Client supports seamless rehydration of failed runs by resuming the trace ID instead of discarding it.

## 8. ERROR HANDLING (RFC 7807 & EXCEPTION BOUNDARY)

### 8.1 The No-Pass Rule
Empty `try { ... } catch (e) {}` blocks are BANNED. You must display an ErrorView, log the error, and rethrow it.

### 8.2 Exception Unwrapping
Always catch `CheckedFromJsonException` and unwrap the real issue via `.innerError` before escalating to Telemetry.

### 8.3 Absolute Death / Diagnostic Node (SizedBox.shrink Ban)
Invalid components must CRASH immediately. A higher-level `AppErrorBoundary` traps the crash and displays a localized "Error Box" (red dashed border, ErrorCode) in place of the widget. It is STRICTLY BANNED to hide corrupted UI elements or swallowed errors using `SizedBox.shrink()`.

### 8.4 Dual-Reporting
On HTTP/Network faults, log to `LoggerServiceProvider` (which relays to Backend Telemetry) and `rethrow` to trigger the local UI boundary.

## 9. ZERO-HARDCODING & THE 5-LAYER I18N

### 9.1 No Magic Strings/Numbers
Do not hardcode padding (use Theme tokens).

### 9.2 No Hardcoded Keys/Forms
Do not fake dictionary keys. Do not ask users to manually type Opaque IDs in text fields. Backend orchestrates IDs.

### 9.3 Enum Settings
Detached duration rules (e.g., `Duration(seconds: 15)`) must be centralized into private Enums (e.g., `class ApiTimeouts`).

### 9.4 5-Layer I18N
Backend returns Enum Codes (e.g., `AUTH_ORGANIC`). Raw UI language strings are banned in APIs. The UI resolves language dynamically. Use `.arb` files for compile-time strings. "Edit values, never keys."

### 9.5 Actionable Hints
Map backend errors to Toast/Snackbars containing actionable text natively inside the Desktop canvas.

## 10. IAM & SECURITY

### 10.1 Passkey-First Reauth
If token is stale (`REAUTH_REQUIRED`), do NOT route to a full-screen login. Inject an overlay dialog to intercept, ask for Passkey, and retry the request silently. Step-Up MFA works the same way.

### 10.2 O(1) Authorization (Flat Claims)
UI authorization relies on JWT token custom claims (`org_xyz: MEMBER`). UI actively hides elements (`SizedBox.shrink()`) based on memory without re-fetching server roles constantly.

### 10.3 Zero-Latency IAM
Settings views are cached via SWR. They are integrated via TwoPane layout, not a separate page, preserving workflow context.

## 11. DOCUMENTATION & HYGIENE

### 11.1 Effective Dart Documentation
All public APIs, classes, and methods MUST be documented strictly adhering to the "Effective Dart: Documentation" guidelines. Use `///` for doc comments, start with a brief one-sentence summary, and write in the third-person or imperative mood (e.g., "Returns the...", "Calculates the...").

### 11.2 Language Strategy
All source code (variables, classes, files) MUST be named in English. Explanations and conversational context MUST be in Finnish.

### 11.3 "Why" Mandate
Inline comments (`//`) should explain WHY a non-obvious business logic decision was made, never WHAT the code mechanically does.