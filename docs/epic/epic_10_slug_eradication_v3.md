# Epic 10: Demoting "Slug" – Enforcing Opaque IDs (Stripe Pattern)

**Status:** Proposed (Tier 1 & Tier 2 Execution)
**Context:** Quorum V2/V3 Backend & Frontend
**Author:** AI Orchestrator / Principal Solutions Architect
**Reference:** `docs/reference.md`
**Date:** March 25, 2026

## 1. Problem Statement
Sanaa "slug" on käytetty ristiin ja väärin koko koodikannassa. Sitä on alkanut siirtyä vahingossa API-rajapintojen avaimeksi (API Key), tietokantahakujen pääparametriksi, reitityksen polkumuuttujaksi ja jopa orkestraattorin relaatiolinkiksi (`get_step_by_id(blueprint_slug)`).

**TÄRKEÄÄ:** `slug` (esim. `holistic_audit`) ei ole poistumassa järjestelmästä. Sillä on oma funktionsa (hybridi-URL / hakusana), ja se pysyy Pydantic-malleissa ominaisuutena. Ohjelmiston siemen (Seed Data) **ON JO** oikeassa muodossa ja kantaa täydellisiä Stripe Pattern ID -koodeja (`blk_...`, `syscfg_...`). Ongelma piilee laiskassa Python-koodissa ja Flutterissa, jotka yhä käyttävät `slug`-kenttiä tietokantahakuihin ohi varsinaisen ID-kentän!

Tämän Epicin tehtävä on **riisua slugilta API-avaimen, ensisijaisen tunnisteen (Primary Key) ja ulkoisen avaimen (Foreign Key) vastuut**, ja pakottaa Python- ja Flutter-ohjelmakoodi käyttämään taustalle jo valmiiksi generoituja **Opaque Stripe ID** -koodeja tiedon noutamiseen.

## 2. Execution Strategy (Directory by Directory)
Korjaus etenee kerroksittain `reference.md` -hakemistorakenteen mukaan. Teemme "massiivisia tuplatarkistuksia" (Grep Searches) jokaisen vaiheen jälkeen varmistaaksemme, ettei slugia käytetä kytköksenä tai API-avaimena.

---

### Phase 1: The Seed (Kytkösten / Foreign Keys Tarkistus)
**Target:** `backend_v2/seed/`
* **Task:** HYVÄ UUTINEN: `seed_data.json` sisältää JO TÄYDELLISET Opaque Stripe ID:t (`"id": "blk_...", "id": "syscfg_..."`). ID-tunnisteita EI TARVITSE generoida! Ainoa tehtäväsi on etsiä ja korjata **relaatiot** (esim. Workflown työvaiheiden `task_blueprint` -viittaukset The Prompt Blockeihin). Jos ne osoittavat vielä laiskasti slugeihin (`"task_blueprint": "matrix_risk"`), muuta viittaukset osoittamaan The Stripe ID -koodeja (`"task_blueprint": "blk_371c..."`). Muutoin tiedosto on jo täydellinen.

### Phase 2: Domain Models (Single Source of Truth)
**Target:** `backend_v2/models/`
* **Task:** Käy läpi kaikki Pydantic-mallit. Varmista, että mikään malli ei aseta `slug`:ia ensikertaisesti (Primary Key) tunnistavaksi kentäksi ID:n ohi. Relaatiot (`task_blueprint`, `profile_id`) voivat kantaa vain `id`-tyyppisiä arvoja.

### Phase 3: The Unified Repository & Storage
**Target:** `backend_v2/database/`
* **Task:** Tarkista tietokanta-CRUD -metodit. API-reitittimille ja ajoympäristölle on pääasiassa tarjottava `get_by_id` -tyyppiset haut. Jos `by_slug` jää koodiin, varmista, että sitä käytetään VARTEN VASTEN slugin omaan tarkoitukseen (esim. UI:n asettaman ihmisluettavan aliaksen haku) eikä sisäisen Moottorin datanlinkitykseen.

### Phase 4: Business Logic & The Orchestrator
**Target:** `backend_v2/services/`
* **Task:** Analysoi ja korjaa orkestraattorin ja DAG:in ydinlogiikka. Esim. `orchestrator/strategies/` ei saa KOSKAAN hakea askeleita muuttujanimellä kuten `blueprint_slug`. Ne on muutettava: `blueprint_id = getattr(step, "task_blueprint_id") -> get_step_by_id(blueprint_id)`. Pysäytä massiivisella tarkistuksella, ettei slug-muuttujia käytetä id-hakuun.

### Phase 5: FastAPI Control Plane & Core
**Target:** `backend_v2/api/routers/`
* **Task:** Siivoa API-rajapinnat. Sisäiset "muokkaa / hae / aja" API-kutsut eivät saa käyttää muotoa `/{slug}` API-avaimena, vaan niiden TÄYTYY käyttää `/{id}` -reititystä. 

### Phase 6: Core Engine Tests
**Target:** `backend_v2/tests/`
* **Task:** Korjaa kaikki rikkoutuneet yksikkö- ja integraatiotestit, joissa API:lle huijattiin syötteeksi slug (`slug="test"`). Vaihda testien syötteiksi Stripe ID:t (`id="pb_test_123"`). Testit **on mentävä läpi** ennen siirtymistä Flutterin pariin.

---

### Phase 7: Flutter Client - Core API 
**Target:** `client_app_v2/lib/core/` 
* **Task:** Päivitä `studio_client.dart` endpoint-kutsut vastaamaan Backendin uutta API-rajapintaa (`by-id`).

### Phase 8: Flutter GoRouter
**Target:** `client_app_v2/lib/router/`
* **Task:** Vaihda työtilojen ja editoreiden Deep Linking -reitit uuteen hybridi-malliin (Hybrid URL Pattern) SEO:n ja selkokielisyyden vuoksi. Reitti on muotoa `path: 'workflow/edit/:id/:slug'`. Reitittimen tai Controllerin logiikka POIMII talteen AINOASTAAN `:id` parametrin tietokannan avaimeksi ja ohittaa `:slug` osuuden kokonaan pelkkänä rikkoutumattomana kosmetiikkana. 

### Phase 9: Flutter Features & Dashboard
**Target:** `client_app_v2/lib/features/` & `l10n`
* **Task:** Päivitä Riverpod-tilojen sisäinen logiikka (kuten tallennusmutaatiot) välittämään taaksepäin `id` eikä arvailemaan sitä `slug`in perusteella. Varmista `dart run custom_lint` -validointi koko hakemistolle.

## 3. The Definition of Done
Kun kaikki 9 vaihetta on tehty hakemisto kerrallaan "PERMISSION GRANTED"-silmukalla (katso `reference.md`).
Epic on valmis, kun mikään backendin tai frontendin ydinkomponentti ei ota sisään eikä lähetä ulos slugia `id`-avaimen korvikkeena (Primary Identifer).
