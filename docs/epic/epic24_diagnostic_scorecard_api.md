# Epic 24: Diagnostic Scorecard & Independent Presentation API

## 1. Executive Summary
Tavoitteena on tuottaa raakadataan perustuva, läpinäkyvä "Executive Scorecard" tekoälyn suorittamasta arvioinnista (CDA / DINA -mallin tasokohtainen läpivalaisu). Tämä mahdollistaa arvioinnin tarkastelun kognitiivisilla tasoilla (esim. Bloomin taksonomian tasot 1-6) tuottaen ymmärryksen siitä, miksi suoritus riitti tiettyyn pisteeseen ja mihin se kaatui. Epic rakennetaan puhtaasti V2-arkkitehtuurin (Zero-Math UI, Fail-Fast) sääntöjen mukaisesti erillisenä, riippumattomana rajapintana (API), jonka päälle käyttöliittymä ja PDF-raportit nojaavat sokeasti.

## 2. Arkkitehtoniset Reunaehdot
*   **Zero-Math UI (00-antigravity-core):** Kaikki atomien tasokohtaisen suorituksen summeeraus, lopputuloksen laskenta ja normalisointi suoritetaan yksinomaan Backendissä. Frontend ja PDF-moottori tekevät vain ehdollisen renderöinnin (vihreä/punainen porras) Pydantic-skeemojen perusteella.
*   **Structural Sovereignty:** Raportin tulostusmääreisiin (esim. `Output Profiles` / järjestelmäkonfiguraatio) lisätään dynaaminen lippu `include_diagnostic_scorecard` (boolean). Käyttäjä ei ohjelmoi UI:tä, vaan tietokannan asetus piilottaa tai näyttää sivun.
*   **API Isolation:** Kokonaisuus rakennetaan itsenäiseksi API-reitiksi. V2-palvelin ei sekoita tätä raskaan PDF-luonnin tai ydinreittien sekaan, vaan tuloskojelaudan voi ladata UI:ssa itsenäisesti asynkronisesti tyyliin `HTTP GET /api/v2/executions/{exe_id}/scorecard`.

## 3. Toteutusvaiheet (Implementation Execution)

### Phase 1: Backend Scoring & DTO Enhancements
*   Päivitetään `backend_v2/hooks/scoring.py` `waterfall_scoring_hook` ja Map-Reduce -yhdistäjä.
*   Globaalien osumien (`_true_atoms` / `_total_atoms`) lisäksi hook rakentaa lennosta JSON-objektin: `_level_breakdown`.
*   Sanakirja tallentaa kunkin matriisin portaan osumat ja kokonaismäärät suhteuttaen ne DINA-teorian portaisiin Pydantic-validoituna rakenteena.
*   Päivitetään järjestelmäkonfiguraation Pydantic DTO (esim. raportin asetus `show_scorecard: bool` / `include_diagnostic_scorecard: bool`) System Configuration db_v2 -malliin.

### Phase 2: Independent Presentation API
*   Luodaan FastAPI-sovellukseen uusi eristetty lukurajapinta (esim. `router_scorecard.py`).
*   Reitti noutaa `execution_trace.json` -tiedoston Blob/Storage -osiosta ja hydratoi sen uuteen `ScorecardResponseDTO` -skeemaan.
*   Rajapinta siivoaa raakadatan ja palauttaa frontendille / UI:lle valmiiksi suodatetun vasteen, joka jakaa asiat suoraan listoihin: `global_average`, `evaluative_matrices` ja `informational_matrices` (matkien täysin valmista kokeellista skriptiä).

### Phase 3: Unit Testing (Pytests API Audit)
*   **TDD/Fail-Fast Vaatimus:** Kehitetään `test_scorecard_api.py`.
*   Mokataan tyypillinen Map-Reduce -ajon tulos (Trace), jossa on monitasoisia dynaamisia pudotuksia (esim. Taso 1: 5/5, Taso 2: 1/5).
*   Testataan assertioilla, että `Scorecard API` tuottaa matemaattisesti tasan tarkat ja katkeamattomat Breakdownt.
*   Testataan, että API-reitti kaatuu asiallisella HTTP 400 -luokan Pydantic-virheellä (RFC 7807), jos yritetään noutaa scorecard korruptoituneesta tracesta.

### Phase 4: Flutter Käyttöliittymä (Dart V2 Client)
*   Luodaan erillinen Riverpod Provider noutamaan uuden API:n datat (`ScorecardRepository`).
*   Rakennetaan `DiagnosticScorecardWidget` komponentti.
*   Jos konfiguraatio (`is_scorecard_active`) antaa luvan, visualisoidaan kunkin matriisin kohdalla skaalan mukainen palkkidiagrammi ja asiantuntijan perusteluvirke (first sentence).
*   Noudatetaan "No-String Mandatea": Kovat otsakekirjoitukset (esim. "Informaatiomatriisit") haetaan `.arb` lokalisaatiotiedostoista, ei koodista.

### Phase 5: PDF Engine Parity
*   Päivitetään raportoinnin PDF-moottorin mallit tukemaan valinnaista viimeistä "Diagnostic Summary" -sivua.
*   Jos ajo on pyydetty tulostettavaksi PDF-liitteellä (`show_scorecard=True`), luodaan tiukka ja visuaalisesti dynaaminen laatikosto/taulukko, joka heijastaa 1:1 Flutter UI:n esittämää pariteettia (Yhdistetty "Zero-Math Layout" rutiini).
*   Varmistetaan teknisesti vakaa taulukkotulostus, valuma-reunasuojat ja pitkien `justification`-tekstien virheettömät rivitykset paperi/pdf-kirjoittimelle.
