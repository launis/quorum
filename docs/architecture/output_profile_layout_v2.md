# OutputProfile Layout Architecture (V2 Baseline)

*Tämä on dynaaminen ja ensimmäinen lähtötasomalli (baseline) V2 OutputProfile -arkkitehtuurille.*
*Kaikki säännöt on todennettu tietokannan malleista (`backend_v2/models/v2_core.py`) ja Blueprint-syntetisaattorin logiikasta (`backend_v2/services/blueprint.py`).*

## Rakenteen Hierarkia (Dumb Painter SDUI)
Koko raportin tulostus (Frontend ja PDF) perustuu `blueprint.py`:n luomaan `ReportLayoutDTO`-putkeen, joka saa ohjeistuksensa suoraan tietokannan `OutputProfile`-taulusta. 

Raportin tulostuksen looginen 7-portainen järjestys ja sen arkkitehtuurisäännöt ovat seuraavat:

### 1. Metadata-laatikko
- **Tietokannan kenttä:** `OutputProfile.visible_metadata` (esim. lista `["date", "organization", "user"]`).
- **Koodin ilmentymä:** `ReportMetadataDTO`.
- **Flutter/PDF:** Piirtää standardoidun infolaatikon raportin alkuun tai ylätunnisteeseen profiilin valitsemilla kentillä.

### 2. Executive Summary (Käyttäjän rooli)
- **Tietokannan kenttä:** `OutputProfile.synthesis` (`SynthesisConfigDTO`) ja `OutputProfile.custom_preface` / `user_role_label`.
- **Koodin ilmentymä:** `ReportLayoutDTO.synthesis_blocks`. Käännetään Server-Driven UI (SDUI) muotoon (yleensä `HeroInsightBlock` tai `MarkdownBlock`).
- **Flutter/PDF:** Piirtää tekstin sokeasti sellaisenaan. Käyttäjän valitsema rooli on injektoitu tekoälyn promptiin ja se ohjaa tiivistelmän asennetta ja sävyä.

### 3. Matriisien Tekstitulostus (Perustelut ja Graafit)
- **Koodin ilmentymä:** `MatrixScorecardRowDTO`, josta frontendille renderöidään `inner_sdui_blocks`.
- **Logiikka (`blueprint.py`):**
  - **Tekoälyn rooli:** Graafeilla on täysin omat LLM-sääntönsä ja promptinsa. Tekoäly kirjoittaa nimenomaan kyseistä graafia ja valittua dimensiota tukevat selitekappaleet.
  - **Arkkitehtuurisääntö:** Pisteitä (`score`) **ei näytetä** tässä osiossa. 
  - Yhdistetään 1D, 2D tai 3D -rakenteen mukaiset tekstit ja graafit.
- **Flutter/PDF:** Generoi graafit ja niihin liitetyt SDUI-tekstiblokit (`ParagraphBlock` ja `MarkdownBlock`) sokeasti sijoituskordinaattien mukaan. Taulukoita tai raakaa matematiikkaa ei tulosteta.

### 4. Extensiot (Tekstiblokkeja)
- **Tietokannan kenttä:** `OutputProfile.visible_block_extensions` (Lista, esim. `COACHING`, `KEY_TAKEAWAY`).
- **Koodin ilmentymä:** Metodi `_hydrate_grouped_extensions_block()` paketoi extensiot.
- **Logiikka:**
  - **Arkkitehtuurisääntö:** Nämä ovat **täysin itsenäinen oma blokkinsa**. Niitä *ei ikinä* sijoiteta matriisitekstien väliin tai perään.
  - Käännetään ryhmitellyiksi haitarivalikoiksi (`AccordionBlock`) tai varoituslaatikoiksi (`AlertBlock`).
- **Flutter/PDF:** Renderöi puhtaan, eristetyn osion, josta lukija voi lukea valmennusvinkit sotkematta muuta analyysia.

### 5. Matriisin Pistetaulukko
- **Koodin ilmentymä:** `ReportLayoutDTO` (jossa `preset_view: "3d_matrix"` tai vastaava) ja `MatrixScorecardRowDTO` (matemaattiset kentät).
- **Logiikka:**
  - **Arkkitehtuurisääntö:** Tässä on pelkästään numeerinen taulukko. Graafeja ei näytetä tässä lohkossa.
  - Yhtenä taulukon sarakkeena (selitesarake) esitetään alkuperäinen tekoälyn antama perustelu suoraan `row_explanation`-kentästä.
- **Flutter/PDF:** Älykäs taulukko-widget sivuuttaa tekstitulostuksen SDUI-blokit ja rakentaa visuaalisen taulukon puhtaan matematiikan (`score`, `scale_max`) varaan.

### 6-7. Variaatiot ja Aitous (1D Blokkina)
- **Tietokannan kenttä:** `OutputProfile.visible_workflow_extensions` (lista, esim. `VARIANCE_VALIDATION`, `AUTHENTICITY_EVALUATION`).
- **Koodin ilmentymä:** Erillinen `ReportLayoutDTO`, jossa `preset_view: "1d_metrics"`.
- **Logiikka (`blueprint.py`):**
  - **Arkkitehtuurisääntö:** 1D-blokin muodostamiseen käytetään täsmälleen samaa periaatetta kuin kohdassa 3 (Dumb Painter SDUI).
  - Koska näillä ei ole omaa monimutkaista taulukkoa (kuten kohta 5), näiden numeerinen tulos ja tekoälyn perustelu piirretään poikkeuksellisesti näkyviin tähän samaan 1D-laatikkoon.
- **Flutter/PDF:** Piirtää numeerisen tuloksen ja tekoälyn perustelun sokeasti allekkain 1D-listana.
