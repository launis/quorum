# Cognitive Quorum — Client Application

Desktop-first Flutter user interface for the **Cognitive Quorum** platform. The client communicates asynchronously with the FastAPI backend and background worker pipeline while enforcing a passive, Server-Driven UI (Dumb Painter / Zero-Math UI) architecture.

---

## 📚 Architecture Documentation

All architectural specifications, Server-Driven UI contracts, state management invariants, and presentation rules are maintained exclusively in the architecture documentation directory:

* **[Architecture Documentation (`docs/architecture/`)](../docs/architecture/)**: The Single Source of Truth for the system and client architecture, including **[Server-Driven UI & Presentation](../docs/architecture/04_server_driven_ui_and_presentation.md)**.

---

## 🛠️ Technology Stack

* **UI Framework**: Flutter (Desktop-First)
* **State Management**: Riverpod (`@riverpod` code generation)
* **Data Modeling**: Freezed (`disallow_unrecognized_keys: true`)
* **Routing**: GoRouter (`GoRouteData` typed routes)

---

## 📂 Directory Structure

* `lib/core/`: Application shell, error boundaries, routing, theme, localization, and network infrastructure.
* `lib/features/`: Feature modules including `auth/`, `dashboard/`, `execution/`, `organization/`, and `studio/`.
* `lib/shared/` & `lib/models/`: Shared UI components and Freezed data models synchronized with backend DTO schemas.
* `lib/l10n/`: Localization `.arb` catalogs.

---

## 📦 Development Environment

To start the full stack locally from the workspace root:
```powershell
cd ..
./run_local.bat
```

To run and develop the Flutter client independently when the backend is already running:
```powershell
flutter pub get
dart run build_runner build -d
flutter run
```
