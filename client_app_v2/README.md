# Cognitive Quorum — Client Application

**Desktop-First Server-Driven UI Client for Cognitive Quorum.**

> **Architecture:** Server-Driven UI (SDUI), Dumb Painter Presentation, Isolate-Backed Deserialization
> **Philosophy:** Zero-Math UI, Fail-Fast Freezed Contracts, No-String Localization

The Flutter desktop client communicates asynchronously with the FastAPI backend and background worker pipeline, rendering Server-Driven UI payloads with zero client-side business or scoring logic.

---

## 📚 Architecture Documentation

All system and client architectural specifications, Server-Driven UI contracts, state management invariants, and presentation rules are maintained exclusively in [`../docs/architecture/`](../docs/architecture/):

* **[Meta-Architecture & Verification Runbook](../docs/architecture/00_README_META_ARCHITECTURE.md)**
* **[System Context & Invariants](../docs/architecture/01_system_context_and_invariants.md)**
* **[Data Seeding & Ontology](../docs/architecture/02_data_seeding_and_ontology.md)**
* **[Cognitive Orchestration Engine](../docs/architecture/03_cognitive_orchestration_engine.md)**
* **[Server-Driven UI & Presentation](../docs/architecture/04_server_driven_ui_and_presentation.md)**
* **[Resilience & Observability](../docs/architecture/05_resilience_and_observability.md)**
* **[Enriched Atom Graph Engine](../docs/architecture/06_enriched_atom_graph_engine.md)**
* **[EU AI Act Compliance & Governance](../docs/architecture/07_eu_ai_act_compliance_architecture.md)**
* **[Matrix Theory Explanations Compendium](../docs/architecture/08_matrix_explanations.md)**
* **[LLM Prompt Orchestration & Matrix Evaluation](../docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md)**

---

## 🛠️ Technology Stack

* **UI Framework**: Flutter (Desktop-First)
* **State Management**: Riverpod (`@riverpod` code generation)
* **Data Modeling**: Freezed (`disallow_unrecognized_keys: true`)
* **Routing**: GoRouter (`GoRouteData` typed routes)

---

## 📂 Directory Structure

* `lib/core/`: Core models (`models/`), network client (`network/`), error boundaries (`error/`), configuration (`config/`), and application constants.
* `lib/features/`: Feature modules (`auth/`, `execution/`, `reports/`, `settings/`, `shell/`, `studio/`).
* `lib/l10n/`: Localization `.arb` catalogs and generated localization delegates.
* `lib/router/`: Typed `GoRouter` route definitions.
* `lib/shared/`: Reusable passive UI widgets and layout components.
* `lib/theme/`: Design tokens, typography, and theme definitions.
* `lib/utils/`: Formatting and helper utilities.

---

## 📦 Getting Started

1. **Full-Stack Startup (from Workspace Root)**:
   ```powershell
   cd ..
   ./run_local.bat
   ```
2. **Standalone Client Development**:
   ```powershell
   flutter pub get
   dart run build_runner build -d
   flutter run
   ```

---

## 🛡️ License

**Proprietary and Closed-Source.**
Copyright (c) Risto Launis. All Rights Reserved.
No permission is granted to use, copy, modify, or distribute this software under any circumstances.
