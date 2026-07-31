# Goal: SDUI Matrix Synthesis & Prefix Text Fixes (Suunnitelma v4)

Tämä suunnitelma korjaa aiemman `implementation_plan.md` (Suunnitelma v3) epäonnistumiset, jotka jättivät SDUI-profiilin (Kokonaisvaltainen Auditointi) puutteelliseksi. 

## Proposed Changes

### 1. Alkutekstin (Custom Preface) Palauttaminen
- **Tiedosto:** `backend_v2/seed/seed_data.json`
- **Kohde:** `OutputProfile` id:llä `prf_5d6e7f8091a2b3c4` ("Kokonaisvaltainen Auditointi")
- **Ongelma:** Aiempi suunnitelma unohti päivittää `custom_preface` -kentän, jolloin PDF:n ensimmäiseltä sivulta puuttui EPIC_123:n vaatima pitkä staattinen teksti.
- **Toimenpide:** Korvataan nykyinen lyhyt otsikko täydellisellä Markdown-tekstillä.

### 2. Flutterin report_renderer_v2_widget.dart korjaus (Akselien piilotuksen poisto `text_only`-layouteilta)
- **Tiedosto:** `client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart`
- **Ongelma:** Käyttäjän mainitsemat irralliset lohkot ("Best Practices", "Kausaalinen", "Turvallisuus") ON määritetty täysin oikein erillisiksi `text_only` -layouteiksi `seed_data.json`:ssa. Ongelma on Flutterissa: `report_renderer_v2_widget.dart` piilottaa tällä hetkellä kaikki akselit ehdolla `presetView == PresetView.textOnly`.
- **Toimenpide:** Poistetaan `presetView == PresetView.textOnly ||` ehto `hideAxes` -muuttujan laskennasta.

### 3. Ylimääräisten tuplalayoutien poistaminen
- **Tiedosto:** `backend_v2/seed/seed_data.json`
- **Ongelma:** Edellinen tekoäly loi vahingossa tuplalayoutit matriisissa jo oleville lohkoille `blk_109dab5b6b3f403a` ja `blk_c5804a9143c34cb1`.
- **Toimenpide:** Poistetaan nämä kaksi ylimääräistä tuplalayoutia.

### 4. `pdf_vs_plan_analysis.md`:n Paljastamien Virheiden ja Hallusinaatioiden Korjaus (Tier 0 Tarkkuus)
- **Tiedosto:** `backend_v2/seed/seed_data.json`
- **Ongelma:** Edellinen tekoäly oli **sekoittanut `text_only` -layouttien target_block -ID:t täysin** ja hallusinoinut olemattomia layouteja.
- **Korjaukset:**
  1. **Scrambled Target Blocks:**
     - *Lopullinen Tuomioasteikko* osoitti väärään blockiin. Korjataan oikeaan: `blk_ff72c2d79edb4ebf`.
     - *Kausaalinen ja Abduktiivinen Integriteetti* osoitti vahingossa `blk_c5804a9143c34cb1`:een. Korjataan oikeaan: `blk_c3bc5f3eb8e74110`.
     - *Episteeminen Nöyryys* osoitti vahingossa `blk_109dab5b6b3f403a`:een. Korjataan oikeaan: `blk_22e3598e06414409`.
  2. **Hallusinoidut Layoutit, jotka POISTETAAN KOKONAAN:**
     - `grouped_extensions_block` ja `Kognitiivinen syvyys (Mekaaninen variaatio)` poistetaan kokonaan.
  3. **Ylimääräisiksi Luullut Telemetrialohkot (Lähteet, Rangaistukset, Jargon):**
     - Nämä pidetään Epic 123 (Phase 4: Telemetry Hydration) mukaisesti.
  4. **`matrix_summary` Pidetään Omalla Paikallaan:**
     - EMME siirrä `matrix_summary` -layoutia ylös, vaan palautamme sen indeksin 9/10 paikalle. Asetamme `target_blocks: ["*"]` jotta se nappaa kaikki 13 `category_id == 'matrix'` -lohkoa.

### 5. SDUI:n salliminen `allowed_exports` -kentässä
- **Toimenpide:** Lisätään `"sdui"` jokaiseen layout-olioon `allowed_exports`-kenttään.

### 6. Admin Studion Layout-Editorin (Flutter) Korjaus
- **Tiedosto:** `client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart`
- **Ongelma:** Admin Studio kaatuu (`AssertionError`), jos profiilissa on aktiivisena `PresetView.matrixSummary`. Vika johtuu siitä, että kyseinen legacy-UI-komponentti on kovakoodattu, eikä pudotusvalikosta (`DropdownButtonFormField`) löydy juuri lisättyä `matrixSummary` Enumia.
- **Juurisyy (Dynaamisuus):** Koska Admin Studio sallii layouttien vapaan lisäämisen ja poistamisen, `matrix_summary`:n sijoitus listalla on täysin dynaaminen (eli se voi liukua ykköseksi tai mihin tahansa). Backend ja tietokanta tukevat dynaamista järjestystä 100%, mutta UI kaatui lukiessaan uuden järjestyksen, koska siltä puuttui tämä yksi pudotusvalikon arvo.
- **Toimenpide:** Lisätään `PresetView.matrixSummary` vaihtoehto `DropdownButtonFormField` -komponentin kovakoodattuun `items` -listaan `layout_editor_card.dart` -tiedostossa (rivin 246 tienoille). Tämän pienen korjauksen myötä Admin Studio muuttuu täysin kestäväksi graafien dynaamiselle poistolle ja uudelleenjärjestelylle.
