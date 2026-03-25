# Architectural Proposal: Flutter Global Error Handling (RFC 7807 Parity)

**Status:** Proposed (Phase 3 / V3 Candidate)
**Context:** Quorum V2 Flutter Client
**Author:** AI Orchestrator
**Reference:** `docs/flutterpromptohje.md` (Sections 2 and 6)
**Date:** March 14, 2026

## 1. Problem Statement
The Quorum V2 Python Backend has a highly resilient, RFC 7807 compliant error handling mechanism with strict Dual-Reporting (`logger.error` + `raise AppException`).
However, the Flutter client currently lacks a unified, global strategy for catching these backend exceptions, localizing them into multi-language formats (Finnish/English), and presenting them in a standardized, user-friendly UI component. Errors are often handled locally within widgets or result in generic "Something went wrong" messages.

## 2. Goals (The Zero-Compromise Pledge)
1. **Backend Parity:** The Flutter client must natively understand and parse the `AppException` JSON structure (RFC 7807) sent by the backend.
2. **Centralized Error State:** A global Riverpod state must catch unhandled exceptions and route them to a standardized `ErrorView`.
3. **The No-String Mandate (I18N):** Error codes (e.g., `VALIDATION_FAILED`) must be intercepted and translated using Flutter's `intl` (.arb files) with Actionable Hints, never hardcoded in the UI.
4. **Dual-Reporting in Dart:** Frontend must also log structured errors (`logger.error`) before showing the UI fallback.

## 3. Implementation Blueprint

### Phase A: Telemetry & Logfire Integration (The Dual-Reporting Pipeline)
* **Strategy 1: Local Catch-All (client_debug.log)**
  * Implement global error handlers in `main.dart` (`FlutterError.onError` and `PlatformDispatcher.instance.onError`) to catch all native UI and Async exceptions that bypass HTTP interceptors.
  * Route all caught errors (HTTP & Native) through a centralized `LoggerService.error()` that writes synchronously to the local `client_debug.log` file. This guarantees a local forensic trail even if the network is dead.
* **Strategy 2: Backend Forwarding (Logfire Parity)**
  * The `LoggerService` silently queues and forwards the structured error payloads via an HTTP POST to a new backend endpoint (e.g., `POST /api/v2/telemetry/client-error`).
  * The Python backend receives this payload and natively logs it using its existing `logfire` connection, tagging it with `source="flutter_client"`. This ensures all telemetry (frontend + backend) converges into a single, chronological Logfire trace.

### Phase B: Architecture & Interceptors (Data Layer)
* **`AppException` Dart Model:** Create a Freezed data class (`AppException`) in Flutter that perfectly mirrors the backend's RFC 7807 response schema (`title`, `status`, `error_code`, `instance`).
* **Dio Interceptor:** Implement a global Dio interceptor (`ErrorInterceptor`). 
  * When an HTTP 4xx/5xx occurs, the interceptor attempts to parse the payload into the `AppException` model.
  * If parsing succeeds, it throws a strongly-typed Dart `AppException`.
  * If parsing fails (e.g., a 502 Bad Gateway from a proxy), it wraps it in a fallback `AppException(error_code: "NETWORK_FATAL")`.

### Phase C: State Management & Formatting (Domain Layer)
* **Error Localization Extension:** Create an extension `AppExceptionX` on `AppException` (e.g., in `client_app/lib/core/error/app_error_ext.dart`).
  * This extension contains a single method: `String toLocalizedHint(BuildContext context)`.
  * It acts as a switch statement, mapping `error_code` enums to `AppLocalizations.of(context)` getters (e.g., `case 'VALIDATION_FAILED': return loc.errorValidationFailedHint;`).
* **Riverpod AsyncValue Handling:** All AsyncNotifier build methods must use `.when(data: ..., loading: ..., error: (e, st) => ...)` to catch these typed exceptions.

### Phase C: Presentation (UI Layer - Desktop First)
* **Floating Error Topologies (No Red Screens):** Per Epic 7 and the 2026 System Architecture Manifesto, full-screen blocking modals ("Red Screen of Death") and global error views are strictly forbidden in PC/Desktop usage.
  * Errors must be presented as non-blocking, floating `Toast` or `Snackbar` notifications anchored to the bottom corner of the workspace, ensuring they never steal active focus from the user.
* **Graceful Degradation (Infinite Canvas):** Local component failures within the display matrix or DAG canvas must be caught dynamically via `AppErrorBoundary`.
  * Broken components must silently degrade and hide themselves using `SizedBox.shrink()` instead of crashing the parent view or forcing a fallback UI.
* **GoRouter Integration:** The `errorBuilder` must gracefully redirect the user to a safe ambient state (e.g., the root dashboard) while pushing a floating transient error notification, completely avoiding dead-end full-screen error routes.

## 4. Execution Plan (Next Steps for Developer)
1. Define the `AppException` Freezed model in Dart.
2. Update the `app_en.arb` and `app_fi.arb` dictionaries with translated actionable hints for all known backend `ErrorCodes`.
3. Build the `ErrorInterceptor` for the Dio network client.
4. Construct the `AppErrorBoundary` and `Toast/Snackbar` presentation logic, verifying that artificially triggered `VALIDATION_FAILED` errors degrade gracefully via `SizedBox.shrink()` without causing full-screen UI crashes.
