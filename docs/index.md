# Cognitive Quorum V3.2 Documentation

**Structured, Auditable, and Deterministic AI Orchestration.**

## 📚 Overview

Cognitive Quorum V3.2 (2026) is a **Modular Async Monolith** designed for high-fidelity cognitive labor. It orchestrates a pipeline of specialized agents (Panel, Judge, Analyst) to perform rigorous analysis, enforcing a **"Zero-Magic"** philosophy where every step is strictly typed via **Pydantic V2 DTOs** and auditable.

---

## 🏛️ Architecture (The "Spine")

The system is built on a strictly typed, distributed execution model.

*   **[System Architecture](architecture.md)**
    The authoritative master reference for the V3.2 Modular Async Monolith.
*   **[Management Architecture](management_architecture.md)**
    Control Plane for System Config, Tenant Isolation, and RBAC strategies.
*   **[Data Management](data_management.md)**
    Database schemas, Optimistic Locking, Storage Drivers (`Local`/`Firebase`), and "Zero-Fallback" Configuration.

---

## 🧠 Cognitive System (The "Mind")

How the AI reasons, grounds itself, and maintains continuity.

*   **[Structured Cognitive Architecture](structured_cognitive_architecture.md)**
    The core philosophy: "Separation of Mind (Strategy) and Spine (Execution)". Features the **Fused Panel Agent**.
*   **[Workflow Data Architecture](workflow_data_architecture.md)**
    Data contracts between agents (`PanelOutputDTO` -> `PanelOutput`). Explains the **Fan-Out Pattern**.
*   **[Prompt Engineering](prompt_engineering.md)**
    The "Sandwich" Strategy, Jinja2 Templates, and "Thinking Token" extraction.

---

## 🛠️ Implementation (The "Hand")

Technical references for the code that powers the system.

*   **[API Models & Schemas](api_models.md)**
    Strict Pydantic V2 definitions for `WorkflowState` and Agent Input/Output DTOs.
*   **[Components Registry](components.md)**
    Reference for Agents, Prompts, and Matrices.
*   **[Hooks & Tools](hooks.md)**
    Documentation for deterministic functions (Security, Reporting) and Fail-Fast protocols.
*   **[Seed Data & Sync](seed_data.md)**
    The "Unidirectional Data Flow" strategy for **System Config** and **Registry**.
*   **[API Reference](reference.md)**
    Endpoints, Error Codes (RFC 7807), and Directory Structure.

---

## ✅ Quality & Verification

Strategies for ensuring the system works as expected without "Magic".

*   **[Simplified Verification Strategy](simplified_verification_strategy.md)**
    The "Zero-Magic" testing philosophy: `pytest`, `verify_sync.py`, and `strict mode`.
*   **[Test Strategy](test_strategy.md)**
    Detailed commands for running Backend (DTO/Config Testing) and Frontend tests.
*   **[JSON Flattening Hazard](json_flattening_hazard.md)**
    Analysis of LLM "Level Skipping" and the DTO mitigation strategy.

---

## 🚀 Development Guides

*   **[Product Roadmap](product_roadmap.md)**
    Current status (V3.2 - Phase 8 Complete), active tasks (Phase 9 Migration), and future milestones.
*   **[Flutter Development Guide](flutterpromptohje.md)**
    Standards for the Frontend "Thick Client" (Riverpod, Localization, Widgets).

---

## ⚡ Quick Start (Windows)

 1.  **Initialize**: `uv sync`
 2.  **Start Everything**: `.\run_local.bat`
     *   Starts Backend (Uvicorn), Worker (Arq), and Flutter Client.
     *   Access API at `http://localhost:8000`.
 3.  **Read the Docs**: `uv run mkdocs serve` (http://localhost:8001)

 ### Alternative (Docker)
 *   `.\run_full_docker.bat` - Full stack in containers (Redis, Firestore, App).

---

*(C) 2024-2026 Risto Launis / Cognitive Quorum Team*
