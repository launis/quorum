# Epic 62 Master Tracker: LLM Concurrency Hardening & Universal Provider Decoupling

Tämä seurantadokumentti (Tracker) valvoo **Epic 62** -suunnitelman vaiheittaista suoritusta. Epicin tavoitteena on poistaa kovakoodatut konesalisidokset, toteuttaa dynaaminen ympäristömuuttujien interpolointi `additional_params` -kenttien kautta, parantaa rate-limit -sietokykyä eksponentiaalisella jitter-perääntymisellä, ottaa käyttöön universaali välimuistin hallinta ja integroida nämä täydellisesti Admin Studio Model Registry UI -näkymään.

## Jatkuva Suorituskierto (Continuous Execution Loop)

Suorita jokainen vaihe järjestyksessä. Kun olet suorittanut vaiheen loppuun, päivitä sen tila muotoon `[OK]` ja siirry seuraavaan.

- [OK] phase1_database.md - Tietokannan ja Seeding-rakenteen Päivitys (Database & Seed Refactoring)
- [OK] phase2_resolver.md - Dynaamisen Ympäristöresoluution Toteutus (Dynamic Env Resolution & Decoupling)
- [OK] phase3_retry.md - Eksponentiaalinen Jitter-Perääntyminen & Caching Strategiat (Resilient Retry & Cache Control)
- [OK] phase4_frontend.md - Käyttöliittymän & Riverpod-tilojen Integrointi (Model Registry UI & Json Form Fields)
- [OK] phase5_hardening.md - Laadunvarmistus & Arkkitehtuuridokumentaation Päivitys (E2E Hardening & Architecture Docs)

---

## Vaihekohtaiset Yksityiskohdat ja Vaatimukset

### Phase 1: Tietokannan ja Seeding-rakenteen Päivitys
* **Dokumentti**: [phase1_database.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_62/phase1_database.md)
* **Päätavoitteet**:
  - Lisää `additional_params` -kenttä backendin `ModelProfile` -malliin.
  - Korvaa `backend_v2/seed/seed_data.json` -tiedoston Vertex AI -sijaintien kovakoodaukset dynaamisella `"${VERTEX_LOCATION}"` -ympäristömuuttujamerkinnällä.
  - Aja seederi päivittämään lokaali TinyDB.

### Phase 2: Dynaamisen Ympäristöresoluution Toteutus
* **Dokumentti**: [phase2_resolver.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_62/phase2_resolver.md)
* **Päätavoitteet**:
  - Toteuta `resolve_env_variables` -metodi `provider.py` -tiedostoon.
  - Pura `additional_params` ja ratkaise ympäristömuuttujat dynaamisesti (strict error handling jos muuttuja puuttuu).
  - Poista suorat `VERTEX_LOCATION` -ympäristötarkistukset ja sijaintikaatumiset `provider.py` -tiedostosta.

### Phase 3: Eksponentiaalinen Jitter-Perääntyminen & Caching Strategiat
* **Dokumentti**: [phase3_retry.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_62/phase3_retry.md)
* **Päätavoitteet**:
  - Korvaa tenacityn kiinteä 30s odotus dynaamisella eksponentiaalisella perääntymisellä (`multiplier=2, min=2, max=30`) ja satunnaisella jitterillä (`1-5s`).
  - Päivitä `client.py` dynaamisesti soveltamaan cache_control-tageja `caching_strategy` -asetuksen perusteella.

### Phase 4: Käyttöliittymän & Riverpod-tilojen Integrointi
* **Dokumentti**: [phase4_frontend.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_62/phase4_frontend.md)
* **Päätavoitteet**:
  - Lisää `additionalParams` ja `cachingStrategy` asiakasohjelman `LlmModelConfig` Freezed-malliin.
  - Lisää tarvittavat käännökset englannin- ja suomenkielisiin `.arb` tiedostoihin.
  - Rakenna `_buildJsonField` ja kytke se Formin `onSaved`-latauskulkuun sekä optimisesti päivittyvään Riverpodiin, estäen kohdistuksen menetykset ja kursorihypyt tekstikentissä.

### Phase 5: Laadunvarmistus & Arkkitehtuuridokumentaation Päivitys
* **Dokumentti**: [phase5_hardening.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_62/phase5_hardening.md)
* **Päätavoitteet**:
  - Luo yksikkötesti `test_adaptive_retry.py` testaamaan backoffin toimintaa.
  - Päivitä arkkitehtuuridokumentit `02_domain_models.md`, `05_llm_and_hooks.md`, `07_desktop_first_flutter.md` ja `09_data_persistence.md`.
  - Aja backend- ja frontend-laatuporttisilmukat.

---

## Universal Hardening Loop Mandate
Ennen kuin merkitset Epicin kokonaan valmiiksi, aja testaus- ja laadunvarmistuskierros:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

---

## Handover-ohjeet (Handover Instructions)
Aloittaaksesi suorituksen fresh-ikkunassa:
1. Avaa uusi puhtaan tilan keskusteluikkuna.
2. Aja käynnistyskomento: `/tier5-resume --target docs/epic/EPIC_62_tracker.md`
