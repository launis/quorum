# Reference Manual & Directory Structure (V2.5)

Tämä dokumentti on tekninen viiteopas (Reference Manual) **Cognitive Quorum V2026** -arkkitehtuurille. Se kuvaa poikkeuksellisen tarkasti järjestelmän hakemistorakenteen, hakemistojen roolit Pydantic Fail-Fast/BFF-arkkitehtuurissa, tietokannan mallin sekä ohjelmien suoritusreitit.

---

## 1. Directory Structure (V2) - The Modular Async Monolith

Quorum V2 on jaettu tiukasti erillisiin kerroksiin (Backend "Aivot / The Spine" ja Frontend "Näyttö / Display Tier"). Backendissä noudatetaan vankkaa kansio-ohjattua sääntöä, jossa mikään kognitio ei saa vuotaa rajapintoihin, ja reititysliberaalit rakenteet on sidottu Pydantic V2 -malleihin.

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
├── models/                     # Single Source of Truth (SSOT) Datamallit (Pydantic V2)
│   ├── auth.py                 # TokenData ja User/Organization Skeemat
│   ├── domain/                 # Vahvat liiketoimintamallit
│   ├── dtos/                   # DTO-mallit (LLM-päätepisteiden sisään/ulostulo)
│   ├── enums.py                # Status-, Rooli-, ja Moodi-Enumeraatiot
│   ├── state.py                # DAG Moottorin ajonaikainen tila
│   ├── v2_core.py              # Arkkitehtuurimallit (Workflow, PromptBlock, OutputProfile jne.)
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
│   ├── orchestrator/           # Laaja kansio: DAGExecutor - Rengastaa askeleet graphina
│   ├── pdf_generator.py        # Renderöi PDF-dokumentit ajamalla BFF Kääntäjää palvelussa
│   └── usage_service.py        # Token-telemetrian, kustannusten ja Logfiren keskitetty käsittely
│
├── tests/                      # Yksikkö/Integraatiotestit (Pytest) joiden kattavuus varmistaa luotettavuuden
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

---

## 2. Järjestelmän Tärkeimmät Ohjelmat ja Skriptit

Näitä työkaluja ja moottoreita järjestelmä käyttää toimintansa varmentamiseen.

### 2.1 The Seed CLI Tool (Konfiguraatioiden siirto kannaksi)
Kaikki Quorum V2 joustavuus piilee `backend_v2/seed/seed_data.json` -tiedostossa. Sitä mukaa kun `seed_data.json`:ia päivitetään (esim. lisätään uusi PromptBlock tai uusi Output Profile), järjestelmä täytyy "Alustaa" (Seed).

*   **Lokaali Alustus:** `uv run python backend_v2/seed/run_seed.py local`
    Tämä tyhjentää paikallisen `db_v2.json` kantaan liitetyt komponentit ja kirjoittaa SSOT tiedon `seed_data.json`:ista suoraan kantaan.
*   **Pilvi Alustus (Firestore):** `uv run python backend_v2/seed/run_seed.py firestore`
    **(Kriittinen operaatio)**. Tuhoaa ja korvaa tuotannon matriisit.

### 2.2 Taustaprosessointi (The ARQ Worker)
Quorum käyttää asynkroniseen työhön Redis-pohjaista `arq` -kirjastoa (joka tukee myös paikallista simulointia ilman Redistä testiajoissa).
*   Ohjelmisto: `backend_v2/worker.py`
*   Sisältää Taskit: `execute_workflow_job` (Ajaa raskaat LLM Graph -kutsut reitittimellä) ja `generate_pdf_job` (Rakentaa PDF-raportit lokaalisti asynkronisena taustatehtävänä estämättä FastAPI/Uvicorn -ruutereita).
*   *Worker on itsenäinen aivo.* Sillä on suora yhteys `repository.py` rajapintaan mutta se asuu irtaallaan HTTP API:sta.

### 2.3 Paikallinen Kehitys (run_local.bat)
*   **Ohjelma:** `./run_local.bat`
*   Ajaa rinnakkain kehitysympäristön Python Uvicorn-palvelinta portissa `8000` sekä asynkronista Dart Flutter pavelinta portissa `8001`. Se latautuu automaattisesti `.env` tiedoston arvoilla kytkemällä `USE_MOCK_DB=true`.

### 2.4 OpenAPI-skeeman Generointi
*   **Ohjelma:** `uv run backend_v2/scripts/generate_openapi.py`
*   **Käyttö:** Kun rajapintoihin (API/Pydantic) tehdään muutoksia, Github CI/CD (`api-sync.yml`) vaatii ajantasaisen tiedoston `docs/swagger/openapi.json`. Tämä skripti käynnistää FastAPI-instanssin väliaikaisesti, uuttaa uuden API-spesifikaation ulos JSON-muotoon, ja estää asynkronisten Client-kirjastojen rikkoutumisen.

---

## 3. Tietokanta ja Ympäristöt

Quorum V2 käyttää modulaarista **Unified Repository** -mallia, jossa abstraktio sallii saumattoman kytkennän joko offline-kehityskantaan (TinyDB) tai pilveen (Firestore).

### 3.1 Pydantic Model -Rakenne (SSOT)
Kaiken tietokantaan menevän datan ja rakenteen on kuljettava `v2_core.py` (tai muiden Domain mallien) läpi. Kun esimerkiksi luodaan työnkulku, data on validoitu `Workflow` Pydantic-objektina. Olennaisia malleja ovat:
1.  **SystemConfig**: Määrittelee The Model Registryn (mikä mallipari toimii tagilla `fast` tai `deep`).
2.  **PromptBlock**: Yhtenäinen tekoälyn ohjeistuskomponentti (yhdistää V1-aikaiset komponentit ja matriisit).
3.  **TaskBlueprint**: Opettaa askeleen siitä kuinka Input ($inputs) käännetään roolille.
4.  **Workflow**: Solmii askeleet ($steps) yhteen DAG:iksi (Directed Acyclic Graph). Määrittelee datareitityksen. Kytkeytyy erillisiin Tulostusprofiileihin 1:N suhteella.
5.  **ExecutionRecord**: Tallentaa joka ainoan suoritetun työn ja kognitiivisen `$results` luupin puhtaana datana loogiseksi, peruuttamattomaksi pöytäkirjaksi.

### 3.2 Lokaali vs. Tuotantokanta
Polussa `backend_v2/database/wrapper.py` alustetaan joko Firestore- tai TinyDB-ajuri riippuen ympäristömuuttujasta.

*   **`USE_MOCK_DB=true`** -> Lukee/Kirjoittaa tiedostoon `backend_v2/database/db_v2.json`. Kaikki suoritettu data, tiimit, luvat (IAM) ovet vapaasti modifioitavissa. Suosittu ohjelmistokehittäjien lokaalissa ympäristössä.
*   **`USE_MOCK_DB=false`** -> Yhdistyy Google Cloud Firestoreen osoittaen `GOOGLE_APPLICATION_CREDENTIALS` polun kautta valtakirjoihin. Toimii tiukoilla Security Ruleseilla ja Tenant-eristelyllä.

### 3.3 Fail-Fast ja Error Codes (RFC 7807)
Koko järjestelmä (Tietokannasta Frontend-renderöitiin) on sidottu yhteen deterministiseen Error Code -avaruuteen. Mallit kuten `AppException(ErrorCodes.VALIDATION_FAILED)` varmistavat, että datavirheet pysäyttävät suorituksen sekunnin murto-osassa ja palauttavat yhtenäisen viestin rajapinnasta, jonka asiakasohjelma (Flutter) parsii Pydantic-standardien mukaisesti, estäen hallusinoinnit järjestelmän omiin sisäänrakennettuihin luuppeihin.