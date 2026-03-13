# Cognitive Quorum - Client Application (Flutter)

This is the front-end client for the **Cognitive Quorum** platform, built with Flutter. It serves as a "Thick Client" explicitly designed for high-stakes cognitive orchestration, interacting seamlessly with the Modular Async Monolith backend.

For the overarching platform documentation, architecture, and backend details, please refer to the **[Main Project README](../README.md)** at the root level.

## 🚀 Overview

The Cognitive Quorum Client is designed with the same **"Zero-Magic"** philosophy as the backend:
- **Strict DTOs**: UI state is driven by explicit data contracts from the backend. 
- **Fail-Fast UI & Graceful Degradation**: Errors are not swallowed. The UI gracefully degrades into Error Cards utilizing the RFC 7807 problem details standard. Additionally, missing properties (e.g. `null` citations) are rendered away using `SizedBox.shrink()` without hardcoded textual fallbacks ("No String Mandate").
- **Real-Time Polling**: Leverages Server-Sent Events (SSE) and Riverpod async streams to track deep reasoning execution in real-time.

## 🏗️ Architecture

- **Framework**: Flutter (3.27+)
- **State Management**: Riverpod 3.0+
- **Routing**: go_router with typed routes (`GoRouteData`).
- **Networking**: Dio (with automatic token injection and RFC 7807 error interception).
- **Localization**: Standard Flutter `flutter_localizations` with strict mapping of backend `ErrorCodes`.

### Key Directories

- `lib/core/`: Application shell, routing (`router.dart`), themed components, and networking infrastructure.
- `lib/features/`: Domain-specific UI modules (e.g., Dashboard, Studio, Execution Monitor).
- `lib/models/`: Strongly typed Dart data classes (often generated via `freezed` and `json_serializable`) matching the backend Pydantic models.
- `lib/l10n/`: Localization files (`.arb`) containing translated strings and error code mappings.

## 📦 Getting Started

### Prerequisites
- Flutter SDK 3.27 or higher
- Android Studio / Xcode (for mobile builds) or a supported Web/Desktop target setup.

### Running the App

The easiest way to launch the entire Cognitive Quorum stack (including this client) is to use the launcher script in the project root:

```bash
cd ..
./run_local.bat
```

To run just the Flutter client manually (assuming the backend is already running on `localhost:8000`):

```bash
# From inside the client_app folder:
flutter pub get

# Generate necessary code (Freezed models, GoRouter routes, JSON Serialization)
dart run build_runner build -d

# Run the app
flutter run
```

### Code Generation
Whenever you modify models or routes, you must run the build runner to generate the `.freezed.dart` or `.g.dart` files:
```bash
dart run build_runner build -d
```

---

*For detailed Flutter development standards, see the `docs/flutterpromptohje.md` in the root repository.*
