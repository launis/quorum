# Phase 5: Vikasietoinen Vesiputouslaskenta (Python-moottori)

## Objective
Rakennetaan täysin mekaaninen, 100 % deterministinen Python-laskentahook (`scoring.py`), joka remappaa Sokean-LLM:n antamat 75 Boolean tulosta takaisin alkuperäiseen 5-portaiseen BARS ruudukkoonsa, laskee "Hit Raten" ja käyttää matemaattista vesiputouslogiikkaa (>= 75 % kynnysarvo) lopullisen tason tuomitsemiseksi turvallisesti.

## TARGET (Modify)
- `backend_v2/hooks/scoring.py` (Vesiputouslaskenta ja kynnysarvojen tarkistus HookResults muodossa)
- Mahdolliset laajennukset `backend_v2/utils/math_utils.py` uusia Hit Rate -laskureita varten.

## CONTEXT (Read-Only)
- `backend_v2/models/v2_core.py` 

## Architectural Constraints (V2 Sequence)
1. **Dependencies:** Ei ulkoisia LLM-kutsuja! Vain pelkkää nopeaa Python "CPU-bound algorithmic logicia".
2. **Pydantic V2:** Palautus noudattaa tarkasti `ReportDataDTO` / `ReportAxisDTO` vaatimuksia ja tallentaa tuloksen sellaiseen muotoon, joka istuu nykyisen "Zero-Math UI" sääntöjen mukaiseen esitykseen etusivulla.

## Design / Implementation specifics
* Järjestelmä kulkee matriisin tasoja ylöspäin (1, 2, 3..). Jos tasolta löytyvistä atomeista (esim 15kpl) >= 75% on osumia (True), jatketaan. Heti kun hit rate alittaa 75%, taso katkaistaan ja edellinen taso lukitaan lopulliseksi arvosanaksi.
* Tuloksesta muodostetaan numeerinen Score-arvo (esim 3.0), sekä kerätään puuttuvat atomit (False-osumat) myöhempää Valmentavaa Synteesiä varten.

## Verification & Quality Gate Plan
* Kirjoitetaan yksikkötestit Waterfall-laskennalle eri reuna-arvoilla (False Negative tilanteet joissa LLM hallusinoi satunnaisia virheitä).
* Komento: `uv run pytest backend_v2/tests/unit/test_scoring.py -v` (Kattavuus yli 90%).

## 🏆 Validation & Outcome (Status: COMPLETED)
Systemaattinen arkkitehtuuriauditointi (Huhtikuu 2026) ja tietokannan "Zero-Trust" -mittarien verifiointi todisti:
1. **Pydantic Scoring Logic on aktiivinen**: The Hook ajaa numeerisen arvioinnin onnistuneesti LLM:n palautteelle (`scoring.py`), laskee matriisien pisteet (`blk_[id]_normalized`) ja asettaa lopullisen Score-arvon oikein muuttujaan `final_score`.
2. Moottori erottelee kylmästi sallitut ja sanktioidut väitteet ja ohjaa nämä ulkoiseen XAI audit-tiedostoon, täyttäen `Zero-Math UI` -velvoitteet. Valmiiksi käsitelty data ladataan käyttöliittymälle puhtaana numeerisena esityksenä (Final Score + Numeeriset dimensiokohtaiset pisteet).
