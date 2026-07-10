# Cognitive Quorum - Client Application (Flutter V2.9)

This is the new **Desktop-First** user interface for the **Cognitive Quorum** platform, specialized for heavy cognitive expert work (Thick Client). It communicates seamlessly and asynchronously with the Backend's (`FastAPI`) APIs and background workers (`Arq / Redis`), bypassing typical device latency (Main Thread Jank).

You can read the main guidelines, architectures, and technological background of the broader software from the **[Root README](../README.md)**. A more detailed technical breakdown of the Frontend resides in the `docs/architecture/06_desktop_first_flutter_client.md` directory.

## 🚀 The Core of the Architecture (The Client Manifesto)

The Flutter application is not just a visual layer, but a strict extension of the system's **Fail-Fast** philosophy:

*   **Zero-Math UI (BFF):** The UI device (Flutter / CPU) *must never* calculate AI performance scores, mathematical averages of x/y axes, or compare numerical color thresholds from AI data. All this complexity is brought in as pre-chewed `ReportLayoutDTO` "Backend-for-Frontend" data from the `BlueprintService`.
*   **AppErrorBoundary (RFC 7807):** We do not desperately try to hide broken architecture (`SizedBox.shrink()` is banned for patching validation errors). If the backend serves data missing from or outside the Freezed model, a single component (e.g., an AI node) "crashes gracefully" into a red **Error Card** box. The rest of the graphical IDE runs smoothly, and the developer sees the source of the fault (`Exception` / `CheckedFromJsonException`) on the screen without a black box. The Opaque Stripe IDs system protects routes from link rot.
*   **Riverpod 3.0 & SWR:** Screen-freezing massive loading animations (Full View Loading Spinners) have been replaced with a **Stale-While-Revalidate** (SWR) cache architecture. State changes are accelerated with "Optimistic UI" mutations, allowing controls to function in milliseconds through latency delays.
*   **The De-Generator Mandate & Snapshot Revert:** The Admin Studio on the maintenance side is built to tolerate massive mutations (editing workflows and matrices) with dynamic "SafeCast" validation layers. If the Pydantic V2 backend rejects a mutation in the spirit of "Fail-Fast", the **Snapshot Revert** protocol undoes the cache changes on the fly without breaking the user experience.
*   **The Isolate Mandate:** (Main Thread Jank Prevention). Even if the server sends a 10 MB JSON report full of complex quotes from dozens of LLM network parts, the deserialization of massive data is locked safely into its own Dart Isolate processor core, guaranteeing an intact 60/120Hz scrolling experience: `await Isolate.run(() => jsonDecode(chunk));`

## 🏗️ Technology Stack

*   **UI Framework**: Flutter (3.27+) -> Optimized for Desktop (Win/Mac) / Ultrawide routing (Three-Pane Layout).
*   **State Management**: Riverpod 3.0+ (`@riverpod` code generation is strictly mandatory).
*   **Code Safety**: Freezed (`disallow_unrecognized_keys: true` -> Strict mode Fail-Fast for the API).
*   **Routing**: GoRouter (Native `GoRouteData` classes; string/path routes are banned for type safety).

## 📂 Directory Structure

*   `lib/core/`: IDE shell (workspaces, AppErrorBoundary, navigation layer) and Dio / Riverpod network infrastructure with asynchronous SWR subscriptions.
*   `lib/features/`: Grouped business modules. Includes `studio/` (Canvas-based DAG editor) and `execution/` expert system workflow monitor.
*   `lib/shared/` & `lib/models/`: Global safely `@freezed`-generated Data Models that sync 1:1 with the Backend Pydantic API.
*   `lib/l10n/`: **No-String Mandate!** The system's I18N localization is handled entirely through `.arb` files to prevent hardcoding the UI and is safeguarded by Enum practices.

## 📦 Development Environment

The easiest way to run the code (FastAPI + Arq + Flutter) at once and ready to go is to start everything from the root level of the project with the installed dependencies (Redis) using the `run_local.bat` script:
```bash
cd ..
./run_local.bat
```

If you edit the Client application independently (the Backend is already up):
```bash
flutter pub get
# Always regenerate routes and models!
dart run build_runner build -d
flutter run
```

---
*(The Client's own technical architecture resides entirely at `docs/architecture/06_desktop_first_flutter_client.md`)*
