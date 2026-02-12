# Cognitive Quorum V2.9 Documentation

**Structured, Auditable, and Deterministic AI Orchestration.**

## 📚 Overview

Cognitive Quorum V2.9 (2026) is a **Modular Async Monolith** designed for high-fidelity cognitive labor. It orchestrates a pipeline of 12 specialized agents to perform rigorous analysis, from logical mapping to causal inference, enforcing a **"Zero-Magic"** philosophy where every step is strictly typed and auditable.

---

## 🏛️ Architecture (The "Spine")

The system is built on a strictly typed, distributed execution model.

*   **[System Architecture](architecture.md)**
    The authoritative master reference for the V2.9 Modular Async Monolith.
*   **[Architecture Analysis](architecture_analysis.md)**
    Deep dive into the Async Worker pattern, Timeout Decoupling, and Scalability.
*   **[Management Architecture](management_architecture.md)**
    Admin Panel, Tenant Isolation, and RBAC strategies.
*   **[Data Management](data_management.md)**
    Database schemas, Optimistic Locking, Storage Drivers (`Local`/`Firebase`), and Dual-Database persistence.

---

## 🧠 Cognitive System (The "Mind")

How the AI reasons, grounds itself, and maintains continuity.

*   **[Structured Cognitive Architecture](structured_cognitive_architecture.md)**
    The core philosophy: "Separation of Mind and Spine", BARS Scoring, and the 12-Agent Pipeline.
*   **[Prompt Engineering](prompt_engineering.md)**
    The "Sandwich" Strategy, Jinja2 Templates, and "Thinking Token" extraction.
*   **[Workflow Data Architecture](workflow_data_architecture.md)**
    Data contracts between agents (`TodistusKartta`, `ArgumentaatioAnalyysi`).

---

## 🛠️ Implementation (The "Hand")

Technical references for the code that powers the system.

*   **[API Models & Schemas](api_models.md)**
    Strict Pydantic V2 definitions for `WorkflowState` and Agent Input/Output.
*   **[Components Registry](components.md)**
    Reference for all 12 Agents, Deterministic Hooks, and Tools.
*   **[Hooks & Tools](hooks.md)**
    Documentation for the deterministic Python functions (Search, Math, PII).
*   **[Seed Data & Sync](seed_data.md)**
    The "Unidirectional Data Flow" strategy for configuration management.
*   **[API Reference](reference.md)**
    Endpoints, Directory Structure, and Swagger documentation.

---

## ✅ Quality & Verification

Strategies for ensuring the system works as expected without "Magic".

*   **[Simplified Verification Strategy](simplified_verification_strategy.md)**
    The "Zero-Magic" testing philosophy: `pytest`, `unittest.mock`, and `mocktail`.
*   **[Test Strategy](test_strategy.md)**
    Detailed commands for running Backend (Unit/Integration) and Frontend tests.

---

## 🚀 Development Guides

*   **[Product Roadmap](product_roadmap.md)**
    Current status (V2.9), active tasks, and future milestones.
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
