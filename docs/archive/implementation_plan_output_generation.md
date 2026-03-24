# Implementation Plan: Output Generation Pipeline (V6.0 / Dynamic SDUI Blueprints)

Tämä epic toteuttaa Quorum V2:n täysin irrotetun esitysarkkitehtuurin (Zero-Deploy UI) sekä 5-kerroksisen monikielisyysstrategian (The Translation Schema Doctrine).

## User Review Required
> [!IMPORTANT]
> - Hyväksy tiedostojen "Read-Only" vs "Modify" -rajaukset.
> - Suunnitelma lykkää "Admin GUI Drag-and-Drop Editor" -käyttöliittymän teon myöhemmäksi (Vaihe 7), jotta ydinmoottori ja E2E-skripti saadaan ensin luotettavasti tuotantoon.
> - E2E API-testi (Vaihe 5) on ehdoton portinvartija Frontend-toteutukseen siirtymiselle.
> - Käännösarkkitehtuuri (Kerrokset 1-5) on integroitu suunnitelmaan.

## Proposed Changes

### Milestone 1: Blueprint Schema & Data Decoupling (Backend Core)
Extending the Pydantic domain models to support the new `render_blueprint` structure inside `ExecutionRecord`, separating layout instructions from the generated intelligence.

#### [TARGET] `c:\src\quorum\backend_v2\models\execution.py`
- Define Pydantic V2 models for `RenderBlueprint` and its components (`1d_gauge`, `2d_matrix`, jne.).
- Lisää `render_blueprint: dict | None` -kenttä `ExecutionRecord` -skeemaan.

#### [TARGET] `c:\src\quorum\backend_v2\services\execution.py`
- Päivitä `DAGExecutor` tallentamaan raaka `$results` data ja liittämään kovakoodattu "MVP Blueprint" ajon tallennusvaiheessa (frozen_context).

---

### Milestone 2: Shared Core - BlueprintTransformer, Multilingual Resolution & UI Render API
Building the universal data transformation hub that merges execution data with the blueprint layouts and safely resolves translations based on the client's locale.

#### [TARGET] `c:\src\quorum\backend_v2\services\blueprint.py` (NEW)
- Toteuta `BlueprintTransformer` yhdistämään Blueprint-asettelu ja `$results` data.
- **Multilingual Resolution (The Translation Schema Doctrine):** Rakenna logiikka, joka lukee käyttäjän kielen (esim. HTTP `Accept-Language` otsakkeesta tai sisäisestä metadatasta) ja poimii dynaamisten matriisien `translations` -oliosta oikeankielisen termin (esim. `fi`) asennuskuormaan (Payload). Tämä toteuttaa Kerroksen 5 käännösvastuun backendissä (Late-Binding).
- Toteuta Graceful Degradation: Jos kognitiivinen tulosdata puuttuu askeleelta, lokita rakenteellisesti `VALIDATION_FAILED` (Dual-Reporting), mutta jatka renderöintiä antaen kentälle null-arvon. Jos itse Blueprint-ohjeisto on viallinen/korruptoitunut, kaadu välittömästi RFC 7807 -virheellä (AppException).

#### [TARGET] `c:\src\quorum\backend_v2\api\routers\execution\executions.py`
- Lisää `GET /executions/{id}/render?format=json` päätepiste palauttamaan koottu ja lokalisoitu SDUI Blueprint JSON synkronisesti.

---

### Milestone 3: Asynchronous PDF-Worker & E2E Validation
Yhdistetään asynkroninen PDF-moottori hyödyntämään tismalleen samaa `BlueprintTransformer` -ydintä kuin Flutter (Parity).

#### [TARGET] `c:\src\quorum\backend_v2\api\routers\execution\executions.py`
- Lisää `POST /executions/{id}/render_pdf` API palauttamaan `202 Accepted` ja ohjaamaan lokalisoidun pdf-tulosteen rakentaminen tausta-Workerille.

#### [TARGET] `c:\src\quorum\backend_v2\worker.py`
- Rakenna taustatehtävä (Task), joka kutsuu `BlueprintTransformer.build_render_payload()` funktiota (ja välittää PDF:n vaatiman kielilokaalin) ja siirtää kootun JSONin PDF-generaattorille.

#### [TARGET] `c:\src\quorum\backend_v2\services\pdf_generator.py`
- Uudelleenkirjoita PDF-moottori ottamaan vastaan abstrakti SDUI Blueprint JSON kovakoodattujen asettelujen sijaan.

---

### Milestone 4: Complex Components Extension (2D, 3D, Notes & Bibliography)
Laajennetaan Blueprint tukemaan syväanalyysejä ja kootaan lähdeluettelo (Bibliography).

#### [TARGET] `c:\src\quorum\backend_v2\models\execution.py`
- Laajenna Blueprint-skeemat tukemaan erikoisosioita: `2d_matrix`, `3d_scatter`, `evaluation_notes_panel` ja globaali `metadata_header`.

#### [TARGET] `c:\src\quorum\backend_v2\services\blueprint.py`
- Rakenna `post_hook` -tyylinen Dictionary-skanneri keräämään kaikki `citation_reference` viittaukset koko `$results` ruumiista yhdistetyksi, deduplikoiduksi Global Bibliography -listaksi dokumentin alaosaan.

---

### Milestone 5: The Final Proof - End-to-End API Test (Automated)
Backendin arkkitehtuuri todistetaan täysin ennen minkään Frontend-ohjelmoinnin aloittamista. Tästä ei edetä ennen kuin testi menee fyysisesti ja puhtaasti läpi.

#### [TARGET] `c:\src\quorum\backend_v2\scripts\test_api_execution.py` (NEW)
- Automatisoitu Python-skripti: Ajaa koko tietyn LLM-työnkulun manuaalisesti, generoi fyysisen asynkronisen PDF:n ja noutaa/tallentaa sen `/scripts/` kansioon. Tuottaa fyysisen todisteen siitä, että asettelut ja dynaamiset käännökset toimivat.

---

### Milestone 6: Flutter SDUI Widget Factory & L10n Validation (Frontend)
Dynaamisen Zero-Deploy -käyttöliittymärenderöijän ohjelmointi Flutteriin ja lokaalien resurssien kytkeminen säännöstön mukaan.

#### [TARGET] `c:\src\quorum\client_app_v2\lib\features\reports\presentation\sdui\widget_factory.dart` (NEW)
- Toteuta Dart 3 Pattern Matching (`switch` expression) parsimaan asettelu JSON `type` -komponenttien perusteella (1D/2D graafit, otsakkeet jne.).
- Rakenna `SafeCast`-pohjaiset suojamuurit (Graceful Degradation): UI piirtää `SizedBox.shrink()`, jos widgetin data on tuntematon / rikki estäen Red Screen kaatumiset.
- **Täydentävä Monikielisyys (Kerros 1 & 4):** Ohjaa renderöinnin ympäröivät staattiset tittelit ja aikaleimat Dartin `intl`-kirjaston (ICU) ja `app_fi.arb` tai `app_en.arb` kautta. Reititä backendin dynaamiset SDUI-arvot natiivilla Riverpod `Locale` tarpeistolla pyytäen backendiä tulostamaan data jo valmiiksi oikealla kielellä.

#### [TARGET] `c:\src\quorum\client_app_v2\lib\features\reports\presentation\report_screen.dart`
- Refaktoroi raportin "tulostus" näkymä ohjaamaan data pelkästään uuden `WidgetFactory` tulostimen läpi poistaen kovakoodatut näkymät.

---

### Milestone 7: Unit Testing & Integrity Pipelines
Koko monikielisen ja dynaamisen reitityksen turvaaminen regression varalta CI/CD-putkessa.

#### [TARGET] `c:\src\quorum\backend_v2\tests\test_blueprint_transformer.py` (NEW)
- Assertoi `AppException 7807` virheellisten JSON-Blueprint tyyppikenttien osalta.
- Assertoi, että puuttuvalla datalla suoritus lokittaa `VALIDATION_FAILED`, mutta palauttaa null arvot estämättä puskua UI:lle.
- Assertoi Kerros 5 käännösten oikea kieliversiointi mockatulla kieli-pyynnöllä dynaamisista `translations` solmuista.

## Verification Plan
1. **Linting & Typing:** `ruff check . --fix` & `mypy .`
2. **Backend Unit Tests:** `pytest backend_v2/tests/test_blueprint_transformer.py`
3. **E2E Integration:** `python backend_v2/scripts/test_api_execution.py`
4. **Frontend Architecture:** `dart build_runner` luonnin tarkistus sekä UI:n visuaalinen vahvistus emulaattorissa asettelulle lokalisointineen.
