# Cognitive Quorum Documentation Hub (2026 SOTA)

**Structured, Auditable, and Deterministic AI Orchestration.**

## 📚 Overview

Cognitive Quorum (2026 Enterprise Edition) is a **Modular Async Monolith** designed for high-fidelity cognitive labor. It orchestrates a pipeline of specialized agents to perform rigorous analysis, enforcing a **"Zero-Compromise"** philosophy where every step is strictly typed via **Rust-Core Pydantic V2 DTOs** and auditable via Event Sourcing traces.

---

## 🏛️ The 2026 System Architecture

The system is built on an unbreakable, strictly typed distributed execution model, replacing legacy agent concepts with explicit Directed Acyclic Graphs (DAG).

*   **[AI-orkestraattori V2.5 Määrittely](Arkkitehtuurimäärittely_%20AI-orkestraattori%20V2.md)**
    The master reference for the backend engine: Polymorphic DAGs, Model Context Protocol (MCP), and the Anti-Mirror protocol.
*   **[B2B SaaS IAM-arkkitehtuuri 2026](epic/B2B%20SaaS%20IAM-arkkitehtuuri%202026.md)**
    Control Plane documentation detailing Zero-Trust, Passkey-First Auth, Step-Up MFA, and the absolute Stripe Pattern (`org_[a-zA-Z0-9]{8}`).
*   **[Client UI - Flutter Prompt Ohje](flutterpromptohje.md)**
    The authoritative standard for the front-end Display Tier. It mandates Desktop-First development, Stale-While-Revalidate (SWR) UI, and the crucial `Isolate` data parsing rules to ensure 0ms main-thread blockage.

---

## 🧠 Cognitive Orchestration

How the AI reasons, grounds itself, and maintains continuity without hallucination.

*   **Anti-Hallucination Schemas**: All outputs are extracted directly from LLMs using `Structured Outputs` bounded by Pydantic's `extra="forbid"`.
*   **Model Context Protocol (MCP)**: Grounded Explainable AI (XAI) achieved through serverless Tool Loops, producing immutable `FrozenContext` traces in the database.
*   **Semantic Data Flow ($inputs)**: Pure structural mapping across DAG nodes, empowering strict separation between `LogicStrategies` and `LLMStrategies`.

---

## 🛠️ Implementation Mandaatit

Technical references for developers and AI agents working on the codebase:

*   **[Antigravity Prompt Mandaatit](antigravity_prompting.md)**
    The core rules system for coding changes (The Zero-Compromise Pledge, The Banned Patterns).
*   **[Backend Hardening & Tier Checklists](hardeningback.md)**
    Strict checklists for enforcing API router anemia and preventing try-except pass leakage.
*   **[Reference & Structures](reference.md)**
    Documentation of core configurations, Seed Data models, and CLI tools.

---

## ⚡ Quick Start (Windows)

 1.  **Initialize Packages**: `uv sync`
 2.  **Start Services**: `.\run_local.bat`
     *   Bootstraps FastAPI, the Arq Background Worker, and the Flutter Client.
     *   Access the live system API at `http://localhost:8000`.
 3.  **Docs Server**: `uv run mkdocs serve` (http://localhost:8001)

 ### Alternative (Docker)
 *   `.\run_full_docker.bat` - Full stack in containers (Redis, Firestore, App).

---

*(C) 2026 Risto Launis / Cognitive Quorum Team*
