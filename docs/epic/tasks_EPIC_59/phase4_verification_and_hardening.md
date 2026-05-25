# Phase 4: Zero-Variance Verification and Architecture Hardening

## 1. Yhteenveto
Tässä vaiheessa suoritetaan täydellinen arkkitehtuurin kovettaminen, tilastollinen todistelu ja visuaalinen verifiointi. Kirjoitetaan aukottomat pytest-totuustaulutestit, vihamielinen "Lazy LLM" -simulaatiotesti, Kronomnesian negatiivisen tilan testi ja suoritetaan oskilloinnin poistumisen stressitesti (Shannonin entropiatemp=0.3). Lopuksi luodaan Flutter XAI UI -testit ja päivitetään arkkitehtuuridokumentit.

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [technical_architecture_summary.md](file:///c:/src/quorum/docs/architecture/technical_architecture_summary.md) - Päivitetään arkkitehtuuridokumentti.
* [06_evaluation_and_scoring.md](file:///c:/src/quorum/docs/architecture/06_evaluation_and_scoring.md) - Päivitetään pisteytysdokumentaatio.

### B. Lukuoikeus (Context - Read-Only)
* [00-antigravity-core.md](file:///c:/src/quorum/.agents/rules/00-antigravity-core.md) - Yleiset arkkitehtuurilait.
* [01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md) - Python-arkkitehtuurisäännöt.
* [02_flutter_desktop.md](file:///c:/src/quorum/.agents/rules/02_flutter_desktop.md) - Flutter-arkkitehtuurisäännöt.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: Totuustaulun yksikkötestaus (Dual-Lock Logic Gate)
* **Tiedosto**: `backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py`
* **Tehtävä**: Kirjoita kattava `pytest.mark.parametrize`-yksikkötesti, joka käy läpi kaikki 32 loogisen totuustaulun kombinaatiota:
  * `Workflow Switch` (enable_contextual_overrides) `True/False`
  * `Assertion Switch` (allow_contextual_override) `True/False`
  * `LLM Override` (contextual_override) `True/False`
  * `LLM Evidence` (evidence_found) `True/False`
  * `Inverse Evidence` (inverse_evidence) `True/False`
  Testin on deterministisesti varmennettava System 2 -tason ehdoton ylivalta: Jos LLM palauttaa `override=True`, mutta työnkorjuun master-kytkin tai väitekytkin on `False`, ohituksen on heti kaaduttava `FAILED`-tilaan.
* **Source**: Epic 59, Phase 4, Tehtävä 4.

### Milestone 2: Vihamielinen "Lazy LLM" -simulaatio (Red Teaming)
* **Tiedosto**: `backend_v2/tests/integration/test_lazy_llm_simulation.py` (Luo uusi)
* **Tehtävä**: Rakenna integrointitesti, joka hyödyntää Mock-LLM:ää simuloimaan laiskaa tekoälyä. Simuloitu LLM yrittää oikaista ja palauttaa kaikille arvioitaville atomeille `contextual_override = True` sekä keksii lyhyitä, tyhjiä perusteluja. Testin on todennettava, että:
  1. Kaikki luvattomat ohitukset (joissa `allow_contextual_override` on `False`) reititetään deterministisesti `FAILED/DLQ` -tilaan.
  2. Spatiaalisen ankkuroinnin rikkovat ohitukset (alle 50 merkkiä tai ilman sijaintiviitettä) reititetään `FAILED/DLQ` -tilaan tai laukaisevat korjaavan `HardeningRetryDirectiveDTO`-uudelleenyrityksen.
  Varmista, ettei mikään laiska tai luvaton LLM-ohitus pääse koskaan suodattimen läpi `PASSED`-tilaan.
* **Source**: Epic 59, Phase 4, Tehtävä 5.

### Milestone 3: Kronomnesian negatiivisen tilan (Negative State) testi
* **Tehtävä**: Kirjoita integrointitesti, joka mittaa *Spatial Slicing* -tekniikkaa aikajanaan sidotulla säännöllä (esim. *"Tapahtumaa X ei tapahtunut ennen vaihetta Y"*). Syötä testiputkeen dokumentti, jossa tapahtuma X tapahtuu vasta vaiheen Y jälkeen (eli leikatun alueen ulkopuolella). Testin on todennettava, että:
  1. `context_builder.py` leikkaa fyysisi irti kaiken tekstin vaiheen Y jälkeen ennen LLM-syötettä.
  2. LLM ei näe tapahtumaa X lainkaan, jolloin se raportoi siitä nollahavainnon.
  3. Python-kerroksen Boolean-inversio (`inverse_evidence`) kääntää tämän oikein ja antaa deterministiseksi lopputuomioksi `PASSED` (vahvistaen, että säännön rikkomusta ei tapahtunut sallitulla aikajanalla), todistaen kronomnesian eston ja kaksiportaisen falsifioinnin aukottoman integraation.
* **Source**: Epic 59, Phase 4, Tehtävä 6.

### Milestone 4: Oskilloinnin poistumisen stressitesti (Shannonin Entropia Benchmark)
* **Tehtävä**: Suorita tilastollinen oskilloinnin eliminointitesti:
  1. Määritä testiajolle (tai muokkaa dynaamisesti `seed_data.json`-malliin) korkeampi tekoälyn lämpötila `temperature = 0.3` provosoidaksesi luonnollisen kielen luovaa varianssia.
  2. Aja E2E-simulaatiotesti 10–20 kertaa peräkkäin vaikeilla testisiemenillä (Toulmin, Bloom, Goodhart).
  3. **Quality Gate -vaatimus**: Vaikka tekoälyn luovuutta on nostettu (temp=0.3), System 2:n ja kognitiivisen ohitusventtiilin deterministic-suodattimien läpi ajettuna lopputuomion (PASS/FAIL) **Shannonin entropian on oltava tasan 0.000** ja **Fleissin Kappan tasan 1.0**. Tuloksen on oltava absoluuttisesti sama jokaisessa ajossa.
* **Source**: Epic 59, Phase 4, Tehtävä 7.

### Milestone 5: XAI-läpinäkyvyyden visuaalinen varmistaminen (Audit Trail UI Test)
* **Tiedosto**: `client_app_v2/test/features/studio/widgets/test_xai_audit_trail.dart` (Luo uusi)
* **Tehtävä**: Kirjoita Flutter-integraatio/widget-testi, joka todentaa, että:
  1. Kun atomilaskenta sisältää `contextual_override == true`, käyttöliittymä korvaa perinteisen *"Lainaus/Quote"* -näyttölohkon selkeällä, erivärisellä *"Tekoälyn semanttinen perustelu / Semantic Explanation"* -laatikolla.
  2. Komponentti renderöi ja visualisoi semanttisen ankkuriperusteen (esim. sivun ja kappaleen viitteet) loppukäyttäjälle yksiselitteisenä ja korostettuna audit-trailina.
* **Source**: Epic 59, Phase 4, Tehtävä 8.

### Milestone 6: Arkkitehtuuridokumentaation päivitys
* **Tiedostot**: `docs/architecture/technical_architecture_summary.md` ja `06_evaluation_and_scoring.md`
* **Tehtävä**: Lisää lyhyt, korkean laadun arkkitehtuurikuvaus Claim-Level Contextual Override -ohitusventtiilistä, System 2 Zero-Variance suojamuureista, Spatial Slicingista, Decoupled Falsificationista sekä näiden visuaalisesta XAI- visualisoinnista front-endissä.
* **Source**: Epic 59, Section 6.

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattiset testit (Pytest & Flutter Test)
```powershell
uv run pytest backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py -v
uv run pytest backend_v2/tests/integration/test_lazy_llm_simulation.py -v
uv run flutter test client_app_v2/test/features/studio/widgets/test_xai_audit_trail.dart
```

### B. Staattinen laatuportti (Quality Gates)
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py
uv run python scripts/flutter_audit_loop.py client_app_v2
```

---

## 5. Istunnon Handover (Session Handover)

> [IMPORTANT]
> Aina onnistuneen työvaiheen ja auditointisilmukan jälkeen suorita kansion tarkka commit:
> `git add docs/architecture/technical_architecture_summary.md docs/architecture/06_evaluation_and_scoring.md`
> `git commit -m "docs(epic-59): updated technical architecture docs for zero-variance system"`

Kun tämä vaihe on täysin valmis ja laatuportit ovat vihreänä, merkitse tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` täytetyksi askeleeksi (`[x]`).

Tämä Epic on nyt valmis ja täydellisesti verifioitu! Raportoi onnistuneesta sulkemisesta käyttäjälle.
