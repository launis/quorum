# Phase 2: Frontend (Epic 82 Admin Studio UI)

Tämä suunnitelma kattaa Flutter-frontendin muutokset, jotka mahdollistavat System Audit Trail -asetuksen hallinnan Admin Studiossa, vastaten Backendin uutta schemaa.

## 1. Dart DTO-mallien Päivitys
**Tiedosto:** `client_app_v2/lib/core/models/dtos.dart` (tai vastaava tiedosto, jossa Workflow/WorkflowDTO on määritelty)
- Lisätään `system_audit_trail` (tyyppiä `bool`, oletuksena `false`) vastaaviin Dart-malleihin. Varmistetaan, että annotaatiot ovat oikein, jotta Freezed-serialisointi toimii.
- Tämä varmistaa arkkitehtuurisen pariteetin backendin Pydantic-mallien kanssa ja estää Fail-Fast -kaatumisen.

## 2. Admin Studio UI: Globaalit laajennokset
**Tiedosto:** Työnkulun muokkausnäkymä, tyypillisesti esim. `client_app_v2/lib/features/studio/views/...`
- Lisätään "Globaalit työnkulun laajennokset" -osioon uusi Checkbox (tai kytkin).
- **Label / Nimi:** "Järjestelmän Faktantarkistusloki".
- Kytketään valinta Riverpod-tilaan (optimistic mutation), joka päivittää valitun työnkulun `system_audit_trail`-asetuksen reaaliaikaisesti ja kutsuu repository-tason päivitysfunktiota asettamaan uuden arvon tietokantaan.

## 3. Verifiointisuunnitelma (Frontend Audit Loop)
1. **Mallien generointi:** Generoidaan uudet Freezed-mallit ajamalla `dart run build_runner build -d` (suositus tehdä scriptin kautta, esim. `flutter_audit_loop.py ... --build`).
2. **Käännöksen tarkistus:** Suoritetaan `uv run python scripts/flutter_audit_loop.py client_app_v2` sen varmistamiseksi, ettei tyyppi- tai tyylivirheitä ole.
3. **Visuaalinen vahvistus:** Käynnistetään Flutter-sovellus lokaalisti, navigoidaan Admin Studioon, muokataan työnkulkua, ja varmistetaan uuden asetuksen tallentuminen ja säilyminen laitteen päivityksen jälkeen.
