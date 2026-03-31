# Arkkitehtuurimäärittely: The Modular 2026 Engine

**Strukturoitu, Auditoitava ja Deterministinen Tekoälyorkestraatio.**

## 📚 Yleiskatsaus

Cognitive Quorum (2026 Enterprise Edition) on huipputason kognitiiviseen työhön suunniteltu **modulaarinen, asynkroninen monoliitti**. Se orkestroi erikoistuneiden tekoälyagenttien putkea ankaran "Zero-Compromise" -filosofian alaisuudessa: jokainen askel on tiukasti tyypitetty **Rust-pohjaisen Pydantic V2 DTO:n** avulla ja jäljitettävissä tapahtumapohjaisten (Event Sourcing) lokien kautta.

---

## 🏛️ Järjestelmäarkkitehtuuri ja Säännökset (Phase 9)

Järjestelmä rakentuu särkymättömän ydinarkkitehtuurin (The Strict Execution Model) varaan. Alla olevat modulaariset säännökset peilaavat 1:1 koodikannan fyysistä hakemistorakennetta.

*   **[00. Executive Summary & Core Mandates](architecture/00_executive_summary.md)**
*   **[01. API-kerros ja Asynkroninen tapahtumahallinta (Core)](architecture/01_backend_api_and_core.md)**
*   **[02. Pydantic-tietomalli ja Fail-Fast (Domain Models)](architecture/02_domain_models.md)**
*   **[03. Työnkulkujen Orkestraatio (DAG) & Suoritusmoottori](architecture/03_business_services_and_dag.md)**
*   **[04. Tekoälyn Hooks, Polyglot Context & LLM Päätepisteet](architecture/04_hooks_and_llm.md)**
*   **[05. Datan Pysyvyys, CQRS ja The Seed Vault](architecture/05_data_persistence_and_seeding.md)**
*   **[06. Esityskerros (Desktop-First Flutter) ja L10n](architecture/06_desktop_first_flutter_client.md)**
*   **[07. Infrastruktuuri, Observability ja FinOps](architecture/07_infrastructure_and_observability.md)**

---

## 🧠 Kognitiivinen Orkestraatio (Teoria ja Käytäntö)

Asiantuntijadokumentaatio siitä, kuinka tekoäly kytketään todellisuuteen, perustelee päätöksensä ja välttää hallusinaatiot.

*   **[Holistinen Mestaruus](Holistinen%20Mestaruus.md)**: Järjestelmän filosofinen perusta asiantuntijoiden osaamisen skaalaamiseksi yli rutiinien.
*   **[Agent Workflows Opas](Agent_Workflows_Opas.md)**: Alkuperäinen työnkulkujen ja orkestraation asiantuntijaopas.
*   **[B2B SaaS IAM-arkkitehtuuri 2026](epic/B2B%20SaaS%20IAM-arkkitehtuuri%202026.md)**: Control Plane documentation detailing Zero-Trust, Passkey-First Auth, Step-Up MFA, and the absolute Stripe Pattern (`org_[a-zA-Z0-9]{8}`).

---

## 🛠️ Ylläpitäjän Mandaatit

Tekniset referenssit kehittäjille ja AI-agenteille, jotka operoivat koodikannassa:

*   **[Antigravity Prompting](antigravity_prompting.md)**
    Ydinsäännöstö tekoälyn lähdekoodimuutoksille (The Zero-Compromise Pledge, Blokatut rakenteet).
*   **[Backend Hardening & Tier Checklists](hardeningback.md)**
    Tiukat tarkistuslistat API-reitittimien puhtauden valvontaan.
*   **[Reference & Structures](reference.md)**
    Ydinkonfiguraatioiden, siemendatan ja CLI-työkalujen referenssit.

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
