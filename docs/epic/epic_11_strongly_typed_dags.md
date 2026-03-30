# EPIC 11: Strongly Typed DAGs & Zero-Typo Workflows

Tämä Epic määrittelee siirtymän Cognitive Quorum -alustan V2-arkkitehtuurista ("Vapaan Tekstin Työnkulut") V3-tason "Vahvasti Tyypitettyihin Työnkulkuihin" (Strongly Typed DAGs). Tavoitteena on saavuttaa 100% Fail-Fast -yhteensopivuus ja rakentaa markkinoiden johtava Visual Node Editor, jossa käyttäjä ei voi koskaan reitittää muuttujia väärin.

Tämä on luonnollinen jatkumo Epicille 10 (Slug Eradication) ja Epic 9 (Fail-Fast Remediation), varmistaen "De-Generator"-arkkitehtuurin asettaman tavoitteen Dataohjatusta Käyttöliittymästä (Data-Driven UI), jossa Client ei koskaan arvaile backendin tietorakenteita ja kaikki tila on vahvasti tyypitetty Freezed-malleilla.

## 🎯 1. Ongelma / The Problem
Nykyisessä Flutter-pohjaisessa V2-toteutuksessa `Step` (Tehtävän Blueprint) ei kerro graafiselle editorille (`WorkflowStepCard`), mitä tarkkoja syötteitä se vaatii toimiakseen, eikä mitä rakenteita se tulostaa (`output_schema`). Tämä jättää vastuun täydellisyydestä loppukäyttäjälle:
- Frontend joutuu luottamaan vapaavalintaisiin tekstikenttiin (Target Argument & Source Token), joissa kirjoitusvirheet `$stteeps.xyz` tuhoavat LLM-ajon ja hukkaavat kallista API-kutsuaikaa (rikkoen FinOps-suojausta).
- Reititys tapahtuu osittain vanhojen arvausten varassa. Koska Epic 10 poisti slugit, reitityksen on nojattava yksinomaan Opaque Stripe -ideihin (`$steps.stp_xxxx.output`), mikä on ihmiselle mahdotonta kirjoittaa manuaalisesti oikein ilman virheitä.

## 💡 2. Ratkaisu / The Solution
Siirrämme reititystiedon nollatason avoimista stringeistä Vahvasti Tyypitetyiksi rajapinnoiksi, pakottaen sekä Backendin (Pydantic V2) että UI:n (Freezed Domain Models) kommunikoimaan ennaltasovittujen muuttujien varassa.

### Vaihe 1: Backend Domain Modelin Rikastus (`v2_core.py`)
Lisätään `Step`-tietomalliin uudet kentät, jotka tekevät siitä "itsetietoisen" solmun. Näiden on läpäistävä `--strict` Mypy -validointi ja noudatettava Pydantic V2 tiukkaa skeemaa.
- **`expected_inputs`**: `list[str]` -> Kertoo UI:lle lennossa, mitkä ovat ohjeistetut muuttujat, joita tämä AI-solmu ottaa vastaan (esim. `["context", "document"]`).
- **`output_schema`**: `dict | None` -> Määrittelee tulosteen json-skeeman ohjatusti, jotta seuraavat solmut voivat kytkeytyä suoraan sen palauttamiin ali-avaimiin.

### Vaihe 2: DB Parity & Siemenen Migraatio (`seed_data.json`)
Lisätään yllä mainitut uudet attribuutit JSON-tietokantaan operatiivisille askelille taaksepäin yhteensopivuuden ja heti-valmiin turvallisuuden takaamiseksi. Varmistetaan `run_seed.py`:n validaation läpäisy.

### Vaihe 3: Älykäs Frontend (`workflow_step_card.dart` & Freezed)
Rakennetaan Flutteriin V2-tason Autocomplete / Dropdown-patteristo hyödyntäen uusia Freezed-malleja ja Riverpodin `AsyncNotifier` -tiloja. Vapaa teksti tuhotaan "Syötekartoitukset" (Input Mappings) -välilehdeltä lähes kokonaan.
- **Kohdemuuttuja:** Lataa lennossa `step.expectedInputs` -listan (Isolate-käännettynä) ja pakottaa kytkökset näihin avaimiin.
- **Lähdetieto (Opaque ID Routing):** Selaa lennossa työnkulun aikaisemmat solmut ja rakentaa selväkieliset ehdotukset ("Vaiheen X Tuloste"), kääntäen valinnan konepellin alla tiukasti Opaque ID -pohjaiseksi viittaukseksi (`$steps.stp_xyz.output`).

## 📈 3. Arkkitehtuuriesimerkki (Investointimuistio)
Tämän Epicin toteuttamisen jälkeen mahdollistamme automaattireitityksen ja "Magic Connectin":
- **Skanneri (Solmu A / stp_111):** Lukee PDF:n (`$inputs.document`) ja tuottaa vain raakatekstin (`output`).
- **Faktantarkistaja (Solmu B / stp_222):** Koska UI tietää analyysin vaativan *molemmat*, pudotusvalikko pakottaa kytkemään *Skannerin* (`stp_111.output`) -> *Faktantarkistajan* `contextiin` ja kohdedokumentin (`$inputs.document`) -> *Faktantarkistajan* `documentiin`.

## 🛠️ 4. Hyväksymiskriteerit (Acceptance Criteria)
- [ ] `Step` luokka `models/v2_core.py`:ssa tukee uusia metakenttiä (100% rust-core strict Pydantic).
- [ ] Flutterin Freezed-mallit (`step.dart`/`step.freezed.dart`) osaavat parsia `expectedInputs` ja `outputSchema` kentät virheettömästi Isolate-threadissa.
- [ ] Admin Studion UI estää kirjoitusvirheet poistamalla Raw String -injektiot työnkulkujen syöterakenteissa ja priorisoi alasvetovalikkoja Opaque ID -viitteillä.
- [ ] Lokituksesta katoavat työnkulkujen ajoaikaiset KeyErrorit ja Fail-Fast viestintä ohjaa API-virheet suoraan Flutter-käyttäjälle RFC 7807 mukaan.
- [ ] Kaikki `mypy --strict` ja `dart analyze` -tarkistukset menevät läpi nollalla virheellä.
