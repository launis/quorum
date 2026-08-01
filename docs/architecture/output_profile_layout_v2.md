# OutputProfile Layout Architecture (V2 Baseline)

> [!CAUTION]
> **TAVOITETILA-DOKUMENTTI.** Tämä dokumentti kuvaa arkkitehtuurin tavoitetilaa. Nykyinen koodi käyttää vielä `ReportLayoutDTO` ja `preset_view` -rakenteita. Migraatiosuunnitelma: katso `implementation_plan.md`.

*Tämä on dynaaminen ja ensimmäinen lähtötasomalli (baseline) V2 OutputProfile -arkkitehtuurille.*
*Kaikki säännöt tullaan todentamaan tietokannan malleista (`backend_v2/models/v2_core.py`) ja Blueprint-syntetisaattorin logiikasta (`backend_v2/services/blueprint.py`) migraation jälkeen.*

## Esitystavat (SDUI Polymorphic Blocks)
Raportin renderöinti ja asettelu (Server-Driven UI) on täysin litteä (flat) ja perustuu kokonaisuudessaan litteään `inner_sdui_blocks` -rakenteeseen. Makrotason `preset_view` ja `ReportLayoutDTO` on poistettu "Dumb Painter" -arkkitehtuurin mukaisesti.

Jokainen visuaalinen komponentti, mukaan lukien monimutkaiset graafit, käännetään Pydanticissa `AnySduiBlock`-luokiksi (ja Flutterissa `SduiBlockDTO`-liittoumaksi):
- **Tekstitulostus**: `ParagraphBlock`, `MarkdownBlock`.
- **`1d_metrics` -> `SduiMetrics1DBlock`**: Yksittäisten metrikoiden tasaiseen listaukseen.
- **`2d_compare` -> `SduiScatterPlotBlock`**: Kahden akselin vertailuun.
- **`3d_matrix` -> `SduiRadarChartBlock`**: Sisältää tarkalleen kolme arvoa (akselia), jotka tulostetaan tutkakuvaajana.
- **`matrix_summary` -> `SduiMatrixTableBlock`**: Taulukkonäkymä, missä on sarakkeita (esim. varsinainen Matriisin Pistetaulukko).

> [!NOTE]
> Kaikki graafit ja taulukot ovat täten puhtaita SDUI-blokkeja, aivan kuten tekstikappaleetkin. Tekoälyn generoimat selitteet (esim. graafia tukevat perustelut) liitetään graafiblokin perään litteässä `inner_sdui_blocks`-putkessa normaaleina `ParagraphBlock`-komponentteina.

## Rakenteen Hierarkia (Dumb Painter SDUI)
Koko raportin tulostus (Frontend ja PDF) perustuu `blueprint.py`:n luomaan litteään `ReportDataDTO.inner_sdui_blocks` -putkeen, joka generoidaan tietokannan `OutputProfile`-taulun ohjeistuksista.

Raportin tulostuksen looginen järjestys ja sen arkkitehtuurisäännöt ovat seuraavat:

### 1. Metadata-laatikko
- **Tietokannan kenttä:** `OutputProfile.visible_metadata` (esim. lista `["date", "organization", "user"]`).
- **Koodin ilmentymä:** `HeaderBlock` (SDUI-komponentti).
- **Flutter/PDF:** Piirtää standardoidun infolaatikon raportin alkuun tai ylätunnisteeseen.

### 2. Executive Summary (Käyttäjän rooli)
- **Tietokannan kenttä:** `OutputProfile.synthesis` (`SynthesisConfigDTO`) ja `OutputProfile.custom_preface` / `user_role_label`.
- **Koodin ilmentymä:** Käännetään Server-Driven UI (SDUI) muotoon (yleensä `HeroInsightBlock` tai `MarkdownBlock`) `inner_sdui_blocks`-taulukkoon.
- **Flutter/PDF:** Piirtää tekstin sokeasti sellaisenaan.

### 3. Matriisien Tekstitulostus (Perustelut ja Graafit)
- **Koodin ilmentymä:** `SduiRadarChartBlock`, `SduiScatterPlotBlock` ja näitä seuraavat `ParagraphBlock`-komponentit.
- **Logiikka (`blueprint.py`):**
  - **Tekoälyn rooli:** Graafeilla on täysin omat LLM-sääntönsä ja promptinsa. Tekoäly kirjoittaa nimenomaan kyseistä graafia ja valittua dimensiota tukevat selitekappaleet.
  - **Arkkitehtuurisääntö:** Pisteitä (`score`) **ei näytetä** tekstiosiossa. 
- **Flutter/PDF:** Generoi graafit (esim. `SduiRadarChartBlock`) ja niihin liitetyt SDUI-tekstiblokit sokeasti järjestyksessä.

### 4. Extensiot (Tekstiblokkeja)
- **Tietokannan kenttä:** `OutputProfile.visible_block_extensions` (Lista, esim. `COACHING`, `KEY_TAKEAWAY`).
- **Koodin ilmentymä:** Metodi `_hydrate_grouped_extensions_block()` paketoi extensiot osaksi `inner_sdui_blocks`-taulukkoa.
- **Logiikka:**
  - Käännetään ryhmitellyiksi haitarivalikoiksi (`AccordionBlock`) tai varoituslaatikoiksi (`AlertBlock`).
- **Flutter/PDF:** Renderöi puhtaan, eristetyn osion.

### 5. Matriisin Pistetaulukko
- **Koodin ilmentymä:** `SduiMatrixTableBlock`.
- **Logiikka:**
  - **Arkkitehtuurisääntö:** Tässä on pelkästään numeerinen taulukko. Graafeja ei näytetä tässä lohkossa.
  - Yhtenä taulukon sarakkeena (selitesarake) esitetään alkuperäinen tekoälyn antama perustelu.
- **Flutter/PDF:** Älykäs SDUI taulukko-widget rakentaa visuaalisen taulukon puhtaan tiedon varaan ilman, että sen tarvitsee tietää makrotason profiileista mitään.

### 6-7. Variaatiot ja Aitous
- **Tietokannan kenttä:** `OutputProfile.visible_workflow_extensions` (lista, esim. `VARIANCE_VALIDATION`, `AUTHENTICITY_EVALUATION`).
- **Koodin ilmentymä:** `SduiMetrics1DBlock` yhdistettynä normaaliin tekstiin.
- **Logiikka (`blueprint.py`):**
  - 1D-blokin muodostamiseen käytetään täsmälleen samaa periaatetta kuin kohdassa 3 (Dumb Painter SDUI).
- **Flutter/PDF:** Piirtää numeerisen tuloksen ja tekoälyn perustelun sokeasti allekkain.
