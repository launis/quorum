# Epic 11 - Absolute Data Purity (Strict Nirvana)

## 🎯 Goal
Saavuttaa Pydantic V2 "Strict Nirvana" poistamalla kaikki ajonaikaiset `@model_validator(mode="before")` -validaattorit. Dataputki linjataan täydellisesti alusta loppuun noudattaen V2 sekvenssiä, varmistaen että Desktop-First IDE -käyttöliittymä tuottaa vain validia, käsin tyypitettyä dataa ilman automaattisesti generoituja DTO-malleja tai raakoja sanakirjoja.

## 📁 File Scoping

**TARGET (Modify):**
* `backend_v2/models/v2_core.py` (Before-hacks poisto)
* `backend_v2/seed/seed_data.json` (Datan täydellinen siivous)
* `backend_v2/tests/test_data/*.json` (Testidatan korjaus)
* `client_app_v2/lib/l10n/app_en.arb` & `app_fi.arb` (Enum-käännökset)
* `client_app_v2/lib/features/studio/models/*.dart` (Käsin koodatut tiukat Dart-mallit)
* `client_app_v2/lib/features/studio/views/widgets/inspector_pane.dart` (Vapaan tekstin korvaaminen Dropdowneilla)
* `client_app_v2/lib/features/studio/views/workflow_builder_view.dart` (Strict DTO integraatio)

**CONTEXT (Read-Only):**
* `epic_11_absolute_data_purity.md` (Mandaatti)
* `backend_v2/models/enums.py` (SSOT tyyppiviitteille)
* `client_app_v2/lib/core/network/api_client.dart` (RFC 7807)

---

## 🗺️ Sequence & Milestones (V2 Architecture Pipeline)

### Milestone 1: Pydantic Models & Seed Data (The Foundation)
* **Toimenpiteet:**
  1. Kirjoitetaan lokaaliin ympäristöön Python-skripti (`backend_v2/seed/clean_seed_types.py`), joka käy ohjelmallisesti läpi ja putsaa `seed_data.json` -tiedoston. Skriptin on automaattisesti purettava JSON-stringit aidoiksi objekteiksi (eliminoi `ast.literal_eval`), korjattava Enumit täsmälliseen pienkirjainmuotoon, ja muutetava aikaleimat natiiveiksi ISO 8601 Z -muodoiksi.
  2. Poistetaan `v2_core.py`:stä KAIKKI `pre_validate_type_enums` ja vastaavat `mode="before"` validaattorit.
  3. Tuhotaan lokaali tietokanta (`wipe_user_data.py`) ja iteroidaan `uv run python backend_v2/seed/run_seed.py local`, kunnes Pydantic nielee datan 100% ilman 422-virheitä.

### Milestone 2: L10n (Localization)
* **Toimenpiteet:**
  1. Lisätään `.arb` -tiedostoihin tismalleen uusia Enum-arvoja vastaavat käännökset (esim. `enum_status_completed`, `enum_type_string`), jotta käyttöliittymä osaa esittää tekniset avaimet käyttäjälle ymmärrettävästi.

### Milestone 3: Repo & API (Testing & Contract Validation)
* **Toimenpiteet:**
  1. Koska Repo ja API perivät Pydantic-tiukkuuden automaattisesti, keskitytään testeihin.
  2. Haravoidaan `backend_v2/tests/` läpi ja korjataan kaikki mockatut JSON-payloadit vastaamaan uutta absoluuttista tyyppiturvallisuutta. Varmistetaan, että API palauttaa RFC 7807 `ValidationError` -vastauksen, jos väärää dataa yritetään uittaa sisään.

### Milestone 4: Frontend Controller & Domain Models (No Gen-Code)
* **Toimenpiteet:**
  1. Hylätään raakojen `Map<String, dynamic>` -sanakirjojen käyttö Frontendin kontrollereissa (`studio_controller.dart`).
  2. Luodaan käsin tiukat Dart-mallit (`PromptBlock`, `ExecutionRecord`, `Workflow`) kansioon `features/studio/models/`. Ei OpenAPI-generointia. 
  3. Kirjoitetaan tismalliset `fromJson` / `toJson` -metodit, jotka pakottavat Dartin `DateTime` -oliot lähettämään ISO8601-Z -muotoa ja Enumit pienellä kirjoitettuna backendille.

### Milestone 5: Desktop-Class UI/UX (Information Density & Constraints)
* **Toimenpiteet:**
  1. Päivitetään 3-Pane layouteissa sijaitseva `inspector_pane.dart` ja `workflow_builder_view.dart`.
  2. Vaihdetaan kaikki aiemmin vapaina tekstikenttinä (viallista dataa sallineet) kentät tiukoiksi alasvetovalikoiksi (Cascading Dropdowns), jotka sitoutuvat Milestone 4:n Dart-malleihin. 
  3. Estetään käyttöliittymätasolla asiantuntijaa syöttämästä "Stringifioitua JSONia" – käytetään erillisiä avain-arvo -lomakerivejä, jotka ohjelmallisesti rakentavat puhtaan JSON-objektin API:lle.
