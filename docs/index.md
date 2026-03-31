# Cognitive Quorum Documentation Hub (2026 SOTA)

**Structured, Auditable, and Deterministic AI Orchestration.**

## 📚 Overview

Cognitive Quorum (2026 Enterprise Edition) is a **Modular Async Monolith** designed for high-fidelity cognitive labor. It orchestrates a pipeline of specialized agents to perform rigorous analysis, enforcing a **"Zero-Compromise"** philosophy where every step is strictly typed via **Rust-Core Pydantic V2 DTOs** and auditable via Event Sourcing traces.

---

## 🏛️ The 2026 System Architecture

The system is built on an unbreakable, strictly typed distributed execution model, mapped 1:1 to the codebase layer conventions.

*   **[00. Executive Summary & Core Mandates](architecture/00_executive_summary.md)**
*   **[01. API-kerros ja Asynkroninen tapahtumahallinta (Core)](architecture/01_backend_api_and_core.md)**
*   **[02. Pydantic-tietomalli ja Fail-Fast (Domain Models)](architecture/02_domain_models.md)**
*   **[03. Työnkulkujen Orkestraatio (DAG) & Suoritusmoottori](architecture/03_business_services_and_dag.md)**
*   **[04. Tekoälyn Hooks, Polyglot Context & LLM Päätepisteet](architecture/04_hooks_and_llm.md)**
*   **[05. Datan Pysyvyys, CQRS ja The Seed Vault](architecture/05_data_persistence_and_seeding.md)**
*   **[06. Esityskerros (Desktop-First Flutter) ja L10n](architecture/06_desktop_first_flutter_client.md)**
*   **[07. Infrastruktuuri, Observability ja FinOps](architecture/07_infrastructure_and_observability.md)**

---

## 🧠 Cognitive Orchestration (Theory)

How the AI reasons, grounds itself, and maintains continuity without hallucination.

*   **[Holistinen Mestaruus](Holistinen%20Mestaruus.md)**: Järjestelmän filosofinen perusta asiantuntijoiden osaamisen skaalaamiseksi yli rutiinien.
*   **[Agent Workflows Opas](Agent_Workflows_Opas.md)**: Alkuperäinen työnkulkujen ja orkestraation asiantuntijaopas.
*   **[B2B SaaS IAM-arkkitehtuuri 2026](epic/B2B%20SaaS%20IAM-arkkitehtuuri%202026.md)**: Control Plane documentation detailing Zero-Trust, Passkey-First Auth, Step-Up MFA, and the absolute Stripe Pattern (`org_[a-zA-Z0-9]{8}`).

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
