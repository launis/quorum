# REPOSITORY DIRECTORY & ARCHITECTURE REFERENCE (V2.5)

Tämä dokumentti on tekninen viiteopas (The Map) **Cognitive Quorum V2026** -arkkitehtuurille. Se kuvaa järjestelmän hakemistorakenteen, hakemistojen roolit Pydantic Fail-Fast/BFF-arkkitehtuurissa, tietokannan mallin sekä skriptien suoritusreitit.

---

## 1. Directory Structure (V2) - The Modular Async Monolith

Quorum V2 on jaettu tiukasti erillisiin kerroksiin. Backendissä noudatetaan vankkaa kansio-ohjattua sääntöä, jossa kognitio ei vuoda rajapintoihin, ja reititysliberaalit rakenteet on sidottu Pydantic V2 -malleihin.

### 1.1 `backend_v2/` - The Core Engine (Python 3.14)

```text
quorum/backend_v2/
├── api/                        # FastAPI Control Plane
│   └── routers/                # Eriytetyt HTTP REST V2 -ruuterit
│       ├── execution/          # DAG-ajojen hallinta ja /report BFF-päätepiste
│       ├── iam/                # Identiteetin ja roolien hallinta
│       └── studio/             # CRUD-rajapinnat säännöstölle (Output Profiles, Workflows)
│
├── core/                       # Keskitetyt konfiguraatiot ja luokat (BaseException, Dependency Injection)
│
├── database/                   # The Unified Repository (Storage Engine)
│   ├── firestore_repo.py       # Tuotannon (Google Cloud) repo-implementaatio
│   ├── repository.py           # Abstrakti base-luokka (AbstractWorkflowRepository)
│   ├── db_v2.json              # Local-kehityksen tietokantatiedosto (TinyDB dokumenttikanta)
│   └── wrapper.py              # Turvamuuri abstraktion ja konkreettisten ajurien välillä
│
├── hooks/                      # Puhdas ja deterministinen CPU-logiikka
│   ├── integrity.py            # Hallusinaatioiden paljastaja (Citation Integrity)
│   ├── reporting.py            # PDF ja Markdown BFF -generointi
│   ├── scoring.py              # LLM-vastausten numeerinen override ja puhdistus
│   ├── search.py               # Vertex AI haku-integraatiot
│   └── security.py             # Estettyjen lausekkeiden (Banned Phrases) valvonta
│
├── llm/                        # Integroidut AI-mallien soittimet (LiteLLM, GenAI)
│
├── models/                     # Single Source of Truth (SSOT) Datamallit (Pydantic V2 Strict Mode)
│   ├── auth.py                 # TokenData ja User/Organization Skeemat
│   ├── domain/                 # Vahvat liiketoimintamallit
│   ├── dtos/                   # DTO-mallit (LLM-päätepisteiden sisään/ulostulo)
│   ├── enums.py                # Status-, Rooli-, ja Moodi-Enumeraatiot
│   ├── state.py                # DAG Moottorin ajonaikainen tila
│   ├── v2_core.py              # Arkkitehtuurimallit (Workflow, PromptBlock, OutputProfile jne.)
│   │                           # Status, tyyppi ja versiot on pakotettu eksplisiittisiksi ilman oletusarvoja.
│   └── workflow.py             # Työnkulkujen rakennemallit
│
├── scripts/                    # Työkalut, migraatiot ja API-dokumentaatio (esim. generate_openapi.py)
│
├── seed/                       # Järjestelmän konfiguraation koti (Zero-Deploy DNA)
│   ├── run_seed.py             # Alustustyökalu: Lataa säännöstön ja rakentaa DB:n
│   ├── seed_registry.py        # Kytkee JSON-avaimet Pydantic-kokoelmiin
│   └── seed_data.json          # Itse The DNA: Kaikki järjestelmän säännöt, matriisit ja Tulostusprofiilit (Output Profiles)
│
├── services/                   # Järjestelmän aivot: Liiketoimintalogiikka (Business Services)
│   ├── auth.py                 # Kirjautumis-, Organisaatio- ja JWT-logiikka
│   ├── blueprint.py            # Yhdistää Tulostusprofiilit DAG-tuloksiin. (BFF Compiler)
│   ├── execution.py            # Suorittaa / Alustaa DAG-ajot
│   ├── orchestrator/           # Autonominen Ydinsuoritin (Askelten reititys ja validointi)
│   │   ├── dag_executor.py     # Yhdistää DAG Async-verkot 
│   │   └── strategies/         # Strategy Pattern: Eristetyt LLMNodeStrategy & LogicNodeStrategy
│   ├── pdf_generator.py        # Renderöi PDF-dokumentit ajamalla BFF Kääntäjää palvelussa
│   └── usage_service.py        # Token-telemetrian, kustannusten ja Logfiren keskitetty käsittely
│
├── tests/                      # Yksikkö/Integraatiotestit (Pytest) joiden kattavuus varmistaa luotettavuuden
│
├── utils/                      # Pienet hajautetut apufunktiot (Fail-Fast)
│   ├── dict_utils.py           # Sanakirjojen syväyhdistämiset
│   ├── math_utils.py           # Numeeriset normalisoinnit ja skaalaukset
│   ├── pydantic_utils.py       # Pydantic-mallien dynaaminen konvertointi (inflate)
│   ├── redis_patcher.py        # Fakeredis fixit asynkroniseen ajoon
│   └── static_charts.py        # PDF-raporttien staattiset kuvaajat (Radar/Scatter)
│
├── main.py                     # FastAPI ohjelman käynnistystiedosto ja reititysten aktivointi
├── worker.py                   # ARQ (Asynchronous Redis Queue) Worker. Ajaa DAG-jonot ja PDF-luonnit taustalla
└── settings.py                 # Pydantic BaseSettings: HALLITSEE ENV-muttujat ja polut.
```

### 1.2 `client_app_v2/` - The Cognitive Studio (Flutter / Dart)

Järjestelmän käyttöliittymä, joka noudattaa vahvasti Riverpod (State Management) ja GoRouter (Navigaatio) konsepteja. Näyttökerros lukee puhtaasti JSON-dataa, eikä sisällä AI-kognition vaatimaa tilatietoa.

```text
quorum/client_app_v2/
├── lib/
│   ├── core/                   # Ydinjärjestelmät (Verkkoasiakas, Riverpod-loggeri, Error Boundaries)
│   ├── features/               # Ominaisuuksiin jaetut sovellusalueet (Feature-First Architecture)
│   │   ├── auth/               # IAM Kirjautumisnäkymät ja Logiikka
│   │   ├── execution/          # DAG Ajojen seurantanäkymä. Riippuvainen BFF ViewModelista.
│   │   └── bff/                # Backend-For-Frontend: WidgetFactory lukemaan ViewModel Nodeja
│   │
│   ├── l10n/                   # Lokalisointi (app_en.arb, app_fi.arb) No-String -säännön mukaisesti
│   ├── router/                 # GoRouter URL-reitittimet ja Guardit
│   ├── shared/                 # Jaetut widgetit, DTO-purkajat ja SafeCast (Defensive Parsing) mallit
│   └── theme/                  # Material 3 Design System - Värit ja muotokieli (Ei koskaan Blueprinteissä)
│
├── main.dart                   # Flutter App Entry point
└── app.dart                    # App Shell (AppErrorBoundary wrapper)
```

### 1.3 `.agents/` - Agentic Configuration Center
Sisältää ohjauslogiikan ja säännöt automatisoidulle Antigravity-kehitykselle. AI:n on luettava nämä dynaamisesti ennen koodausta.
*   **`.agents/rules/`:** Arkkitehtuurin master-dokumentit (`00-antigravity-core.md`, `01-python-backend.md`, jne.).
*   **`.agents/workflows/`:** AI-kehityksen pakotetut askeleet ja roolit (`/tier1-planner`, `/tier2-execute`, tietokannan nollaukset).

### 1.4 `docs/` - Documentation & Assets
Kehittäjien ja projektin dokumentaatio, mallinnukset ja prosessikuvaukset.
*   **`docs/Agent_Workflows_Opas.md`:** Opas AI-agenttien työnkulkujen hyödyntämiseen.
*   **`docs/Holistinen Mestaruus.md`:** Kattava strateginen visio- ja arkkitehtuuridokumentti.
*   **`docs/architecture/`:** Järjestelmän tekniset erittelyt ja kaaviot.
*   **`docs/swagger/` / `docs/epic/`:** API-dokumentaatio (Swagger/OpenAPI) ja ominaisuuskokonaisuuksien (epic) vaatimukset.
*   **`docs/datat/`:** Data-asetuksia.

### 1.5 Juurihakemiston tiedostot (Root-Level Files)
Järjestelmän tärkeimmät aloitustiedostot, konfiguraatiot ja lokit on keskitetty juureen.

**Agentin Ohjaus (Sources of Truth):**
*   **`AGENTS.md`:** Globaali perussääntö (esim. Windows 11 rajoitteet, lokien luku, tietokannan turvallisuus). Agentin tärkein dokumentti.
*   **`GEMINI.md`:** AI-ohjaus, joka ohjaa käyttämään `AGENTS.md` tiedostoa.
*   **`README.md`:** Projektin yleiskuvaus.

**Reaaliaikaiset Lokit (Runtime Logs for AI Diagnostics):**
Pakollinen lukurutiini (MCP Tools) ennen vianmääritystä, välttääkseen ajonaikaiset sokeat pisteet:
*   **`backend_debug.log`:** Backendin virheet, Pydantic-validaatiot, FastAPI-reititys, asynkroniset jonot.
*   **`client_debug.log`:** Frontendin (Flutter) logiikka, tilamuutokset, navigaatio, verkkopyyntöjen datavirheet.

**Käynnistys ja Orkestrointi (Runner Scripts):**
Tuetussa Windows 11 PowerShell -ympäristössä suoritettavat skriptit:
*   **`run_all.py` / `run_local.bat`:** Lokaalin kehitysympäristön kokonaisvaltainen käynnistys.
*   **`run_client_web.bat`:** Flutter Web -version lokaali ajo (ui-testaukseen).
*   **`run_firestore.bat`:** Lokaalin Firestore OS-emulaattorin käynnistäjä.
*   **`run_full_docker.bat` / `docker-compose.yml`:** Kontitettu infra (Redis, tietokannat jne.).
*   **`kill_services.bat`:** Skripti taustapalveluiden sammuttamiseen.

**Konfiguraatiot (Configuration & Meta):**
*   **`pyproject.toml`:** Python-riippuvuudet (uv), linter-säännöt (Ruff, Mypy) ja projektin meta.
*   **`pytest.ini`:** Automaattisen testauksen (Pytest) juurikonfiguraatiot.
*   **`mkdocs.yml`:** Dokumentaatiosivuston (MkDocs) rakennemäärittely.
*   **`openapitools.json`:** DTO-mallien ja rajapintojen asiakaskoodin konfiguraatio (OpenAPI Generator).
*   **`service-account.json`:** Google Cloudin IAM-valtuutusavain (Firebase Admin SDK).
*   **`LICENSE`:** Projektin lisenssi.

---

## 2. Järjestelmän Tärkeimmät Ohjelmat ja Skriptit

### 2.1 The Seed CLI Tool (Konfiguraatioiden siirto kannaksi)
Kaikki Quorum V2 joustavuus piilee `backend_v2/seed/seed_data.json` -tiedostossa.
*   **Lokaali Alustus:** `uv run python backend_v2/seed/run_seed.py local`
*   **Pilvi Alustus (Firestore):** `uv run python backend_v2/seed/run_seed.py firestore`

### 2.2 Taustaprosessointi (The ARQ Worker)
Quorum käyttää asynkroniseen työhön Redis-pohjaista `arq` -kirjastoa.
*   Ohjelmisto: `backend_v2/worker.py`
*   *Worker on itsenäinen aivo.* Sillä on suora yhteys `repository.py` rajapintaan mutta se asuu irtaallaan HTTP API:sta.

### 2.3 Lokaali Kehitys / Caching
*   `USE_MOCK_DB=true` purkaa Firestore-riippuvuudet lokaaliin `db_v2.json` kantaan.
*   CORS ja asynkroninen ympäristö käynnistyvät automaattisesti lokaaleilla `.env` -asetuksilla kehityksessä.
