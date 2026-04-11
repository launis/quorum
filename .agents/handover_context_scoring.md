# EPIC 20: Hybrid Waterfall Math, UI Plotting & Strictness (Handover Context)

Tämä dokumentti on tilannekatsaus uuden konteksti-ikkunan tekoälylle. Se sisältää "viimeistä yksityiskohtaa myöten" tiedot siitä, miten pisteiden laskenta, normalisointi ja graafien piirtäminen tapahtuu yhdessä tekoälyn asettamien kynnysarvojen kanssa.

## 1. Miten matemaattiset tasot muodostuvat (Guttman Waterfall)?
**Tiedosto:** `c:\src\quorum\backend_v2\utils\math_utils.py`
Tässä tiedostossa tapahtuu mikrotason totuusarvojen (atoms) yhteenlasku, joka määrittää matriisien alimman Floor-lattia-arvon.
* **`calculate_waterfall_floor(level_stats, scale_min, threshold=0.75)`**: Käy LLM:n palauttamat arvot läpi porras portaalta "alhaalta ylös". Jos vähintään `75 %` kyseisen portaan kriteereistä on arvioitu `True`, lattia (floor) nousee seuraavalle laatalle.
* **Miksi arvosanat ovat usein tasalukuja (3.0, 5.0) ilman desimaaleja?** Koska jos alin kriteeristö täyttyy maksimiin asti kynnyksen (0.75) ylittämisen vuoksi, ylijäävälle "painotetulle" jatkolaskennalle ei enää riitä matemaattista kattoa, jolloin ohjelma lukittaa tuloksen kiinteäksi indeksiksi. Esim. `5.0`.
* **Miten saada "kireyttä lisää"?** Kynnys (threshold) tulee korottaa arvoon `1.0`. Tällöin tason saavuttamiseen vaaditaan 100 % suoritus.

## 2. Pisteiden skaalautuminen keskiarvoistamista varten
**Tiedosto:** `c:\src\quorum\backend_v2\utils\math_utils.py` ja `backend_v2\hooks\scoring.py`
Jotta kaikki eri asteikot (1–3, 1–5, 1–6) voidaan laittaa samalle viivalle "Total Score" laskennassa, niiden painoarvot tasataan lineaarisella siirrolla.
* **`normalize_score_to_100`**: Kaava `(score - math_min) / (math_max - math_min) * 100.0`. Aiempien virheellisten skaalauksien (Inflation Bug) korjaaja. Esimerkiksi arvosana `3.0` skaalalla `1.0-5.0` tuottaa puhtaan `50 %` suorituksen vertailulaskentaan.

## 3. UI-Graafien Piirtokoordinaatit (SDUI - Server Driven UI)
**Tiedosto:** `c:\src\quorum\backend_v2\services\blueprint.py`
Toisin kuin tutkakartta (ScoreCardRadar), **LogicMatrixChart (3D)** hakee koordinaattinsa backendistä täydellisen Zero-Math arkkitehtuurin mukaisesti offsetteina väliltä `0.0 - 1.0`.
* Backend laskee `ui_plot_ratio`:
  ```python
  ratio = (score_float - scale_min) / (scale_max - scale_min)
  ui_plot_ratio = float(max(0.0, min(1.0, ratio)))
  ```
* Siksi esim. Toulminin mallin `3.0 / 5.0` asettaa `ui_plot_ratio` arvon prikulleen `0.5`, minkä takia Flutter renderöi pallon täydellisesti X-akselinsa keskelle.
* Siksi Kahnemanin pallo (`2.2 / 3.0`) laskee säteeksi `0.6` (eli 60 % pallo).

## 4. Flutter UI (Renderöinti)
**Tiedostot:** `c:\src\quorum\client_app_v2\lib\shared\widgets\logic_matrix_chart.dart` ja `score_card_radar.dart`
* Front-end toimii puhtaana "tyhmänä" renderöintimoottorina. `logic_matrix_chart.dart` lukee suoraan backendin tarjoamat koordinaatit (mm. `zAxis!.uiPlotRatio ?? 0.5;`) ja piirtää ne ilman ylimääräistä oletuslaskentaa.

## Säännöt ja tehtävät seuraavalle tekoäly-ikkunalle (NEXT STEPS)
Seuraavan agentin on aloitettava tehtävä asiakkaan ohjeella "Kiristetään kriteerejä".
1. Siirry heti tutkimaan tiedostoa `c:\src\quorum\backend_v2\hooks\scoring.py`. Rivityksillä noin 460 etsi kutsu `floor_score = calculate_waterfall_floor(stats, scale_min, threshold=0.75)`. Muuta arvo `0.75` arvoon `1.0`. (100% kireys).
2. Päivitä testitiedosto `c:\src\quorum\backend_v2\tests\unit\test_scoring.py` jos tarpeellista kynnykselle, tai tarkista meneekö se suoraan läpi.
3. Päivitä LLM Prompt-kierre (`backend_v2\seed\seed_data.json`), jotta kielimalli lopettaa armollisen `True`-vastausten jakamisen.
