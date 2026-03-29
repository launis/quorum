# EPIC 11: Strongly Typed DAGs & Zero-Typo Workflows

Tämä Epic määrittelee siirtymän Cognitive Quorum -alustan V2-arkkitehtuurista ("Vapaan Tekstin Työnkulut") V3-tason "Vahvasti Tyypitettyihin Työnkulkuihin" (Strongly Typed DAGs). Tavoitteena on saavuttaa 100% Fail-Fast -yhteensopivuus ja rakentaa markkinoiden johtava Visual Node Editor, jossa käyttäjä ei voi koskaan reitittää muuttujia väärin.

Tämä on luonnollinen jatkumo Epicille 10 (Slug Eradication) ja Epic 9 (Fail-Fast Remediation), varmistaen "De-Generator"-arkkitehtuurin asettaman tavoitteen Dataohjatusta Käyttöliittymästä (Data-Driven UI), jossa Client ei koskaan arvaile backendin tietorakenteita.

## 🎯 1. Ongelma / The Problem
Nykyisessä V2-toteutuksessa `Step` (Tehtävän Blueprint) ei kerro graafiselle editorille (`WorkflowStepCard`), mitä syötteitä se vaatii toimiakseen, eikä mitä rakenteita se tulostaa (`output_schema`). Tämä jättää vastuun täydellisyydestä loppukäyttäjälle:
- Frontend joutuu luottamaan vapaavalintaisiin tekstikenttiin (Target Argument & Source Token), joissa kirjoitusvirheet `$stteeps.xyz` tuhoavat LLM-ajon ja hukkaavat kallista API-kutsuaikaa.
- Puuttuu kyvykkyys rakentaa visuaalisia, toisistaan tietoisia solmuja (kuten n8n.io, Zapier, Make.com).

## 💡 2. Ratkaisu / The Solution
Siirrämme reititystiedon nollatason avoimista stringeistä Vahvasti Tyypitetyiksi rajapinnoiksi, pakottaen sekä Backendin että UI:n kommunikoimaan ennaltasovittujen muuttujien varassa.

### Vaihe 1: Backend Domain Modelin Rikastus (`v2_core.py`)
Lisätään `Step`-tietomalliin uudet kentät, jotka tekevät siitä "itsetietoisen" solmun.
- **`expected_inputs`**: `list[str]` -> Kertoo UI:lle lennossa, mitkä ovat ohjeistetut muuttujat, joita tämä AI-solmu ottaa vastaan (esim. `["context", "document"]`).
- **`output_schema`**: `dict | None` -> Määrittelee tulosteen json-skeeman, jotta seuraavat solmut voivat kytkeytyä suoraan sen palauttamiin ali-avaimiin (esim. `$steps.id.output.sentiment`).

### Vaihe 2: DB Parity & Siemenen Migraatio (`seed_data.json`)
Lisätään yllä mainitut uudet attribuutit JSON-tietokantaan kaikille operatiivisille askelille taaksepäin yhteensopivuuden ja heti-valmiin turvallisuuden takaamiseksi.

### Vaihe 3: Älykäs Frontend (`workflow_step_card.dart`)
Rakennetaan Flutteriin V2-tason Autocomplete / Dropdown-patteristo. Vapaa teksti tuhotaan "Syötekartoitukset" (Input Mappings) -välilehdeltä lähes kokonaan.
- **Kohdemuuttuja:** Lataa lennossa `step_def['expected_inputs']` -taulukon ja pakottaa kytkökset näihin avaimiin.
- **Lähdetieto:** Selaa lennossa työnkulun aikaisemmat solmut ja rakentaa selväkieliset ehdotukset ("Vaiheen X Tuloste").

## 📈 3. Arkkitehtuuriesimerkki (Investointimuistio)
Tämän Epicin toteuttamisen jälkeen mahdollistamme automaattireitityksen ja "Magic Connectin".
- **Skanneri (Solmu A):** Lukee PDF:n (`$inputs.document`) ja tuottaa vain raakatekstin (`output`).
- **Faktantarkistaja (Solmu B):** Koska UI tietää analyysin vaativan *molemmat*, pudotusvalikko pakottaa kytkemään *Skannerin* `outputin` -> *Faktantarkistajan* `contextiin` ja *PDF*:n -> *Faktantarkistajan* `documentiin`.

## 🛠️ 4. Hyväksymiskriteerit (Acceptance Criteria)
- [ ] `Step` luokka `models/v2_core.py`:ssa tukee uusia metakenttiä.
- [ ] Vanhat työnkulut tietokannassa / Seedissä eivät rikkoonnu uuden tarkan pydanticin alla.
- [ ] Admin Studion UI estää kirjoitusvirheet estämällä Raw String -injektiot lähde/kohde reitityksissä ja priorisoimalla alasvetovalikkojen (Introspection) käyttöä.
- [ ] Lokituksesta katoavat työnkulkujen KeyErrorit ja Fail-Fast on entistä älykkäämpi jo UI-tasolla.
