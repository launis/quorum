# EPIC 11: Strongly Typed DAGs & Zero-Typo Workflows

Tämä Epic määrittelee siirtymän Cognitive Quorum -alustan V2-arkkitehtuurista ("Vapaan Tekstin Työnkulut") V3-tason "Vahvasti Tyypitettyihin Työnkulkuihin" (Strongly Typed DAGs). Tavoitteena on saavuttaa 100% Fail-Fast -yhteensopivuus ja rakentaa markkinoiden johtava Visual Node Editor, jossa käyttäjä ei voi koskaan reitittää muuttujia väärin.

Tämä on luonnollinen jatkumo Epicille 10 (Slug Eradication) ja Epic 9 (Fail-Fast Remediation), varmistaen "De-Generator"-arkkitehtuurin asettaman tavoitteen Dataohjatusta Käyttöliittymästä (Data-Driven UI), jossa Client ei koskaan arvaile backendin tietorakenteita ja kaikki tila on vahvasti tyypitetty Freezed-malleilla.

## 🎯 1. Nykytila ja Analysoidut Ongelmat (Phase 9 Audit)

Nykyisessä Flutter-pohjaisessa V2-toteutuksessa `Step` (Tehtävän Blueprint) ei kerro graafiselle editorille (`WorkflowStepCard`), mitä tarkkoja syötteitä se vaatii toimiakseen, eikä mitä rakenteita se tulostaa (`output_schema`).

Tarkka koodianalyysi on paljastanut seuraavat kriittiset arkkitehtuuriviat:

1. **Backend Domain Model (`backend_v2/models/v2_core.py`)**
   - **Havainto:** Pydanticin `Step`-luokasta puuttuvat täysin `expected_inputs` ja `output_schema` -kentät.
   - **Seuraus:** Backend ei pysty viestimään UI:lle solmujen vaatimuksia, mikä rikkoo "Schema-First" doktriinin.

2. **Flutter Freezed -mallit (`client_app_v2/lib/features/studio/models/workflow.dart`)**
   - **Havainto:** Polymorfinen `NodeStrategy` ei sisällä kenttiä `expectedInputs` eikä `outputSchema`.
   - **Seuraus:** Vaikka backend palauttaisi nämä tiedot, Dartin turvallinen Isolate-lanka jättää ne parsintavaiheessa pois.

3. **Graafinen Editori (`workflow_step_card.dart`)**
   - **Havainto:** Työnkulun `inputMappings` toteutetaan täysin vapaavalintaisilla `TextFormField`-komponenteilla (Target ja Source).
   - **Seuraus:** Katastrofaalinen "Zero-Typo" säännön rikkomus. Käyttäjät tekevät helposti typoja Opaque ID -reitityksissä (`$steps.stp_xxxx.output`), mikä johtaa LLM-ajon kaatumiseen ja kalliiden AI-kutsujen hukkaan (FinOps-vuoto).

4. **Siemendata (`backend_v2/seed/seed_data.json`)**
   - **Havainto:** JSON-siemendatassa määritellyt validit työnkulkujen `steps` eivät sisällä näitä uusia metakenttiä.
   - **Seuraus:** Ilman taaksepäin yhteensopivaa migraatiota järjestelmän `run_seed.py` Pydantic `extra="forbid"` -tilassa kaatuisi välittömästi.

## 💡 2. Ratkaisu ja Kehitysehdotukset

Siirrämme reititystiedon nollatason avoimista stringeistä Vahvasti Tyypitetyiksi rajapinnoiksi, pakottaen sekä Backendin (Pydantic V2) että UI:n (Freezed Domain Models) kommunikoimaan ennaltasovittujen muuttujien varassa.

### Askel 1: Backend Domain Modelin Rikastus (`v2_core.py`)
Lisätään `Step`-tietomalliin uudet kentät, jotka tekevät siitä "itsetietoisen" solmun. Näiden on läpäistävä `--strict` Mypy -validointi.
- **`expected_inputs`**: `list[str] = Field(default_factory=list)` -> Kertoo UI:lle lennossa sallitut avaimet (esim. `["context", "document"]`).
- **`output_schema`**: `dict[str, Any] | None = Field(default=None)` -> Määrittelee tulosteen JSON-skeeman myöhempää validointia varten.

### Askel 2: Siemendatan (DB Parity) Migraatio (`seed_data.json`)
Päivitetään `seed_data.json` siten, että `steps`-taulukon jokaisella oliolla on `"expected_inputs": []` ja `"output_schema": null`. Tämä takaa, että `run_seed.py` menee läpi puhtaasti.

### Askel 3: Frontendin Freezed-mallien päivitys
Lisätään uudet kentät `workflow.dart`-tiedoston `NodeStrategy`-sealeadin alle (`llm` ja `logic` -unioneihin). Koodigeneroijan ajaminen pakotetaan turva-askeleena.

### Askel 4: "Magic Connect" UI:n toteutus (`workflow_step_card.dart`)
Poistetaan vapaavalintaiset teksti-injektiot ja luodaan "Zero-Typo" rajapinta.
- **Target Argument (Avain):** Luetaan `step.expectedInputs`. Korvataan `TextFormField` turvallisella `DropdownButtonFormField<String>` -komponentilla.
- **Source Token (Arvo):** Selaa työnkulun aiemmat solmut (jotka on merkitty `dependsOn`) ja esittää ne selkokielisinä vaihtoehtoina (esim. "Skanneri Tuloste"). Kun käyttäjä valitsee nimen, UI kääntää sen konepellin alla Opaque ID -reitiksi (`$steps.stp_xyz.output`).

## 📈 3. Arkkitehtuuriesimerkki (Investointimuistio)
Tämän Epicin toteuttamisen jälkeen mahdollistamme automaattireitityksen:
- **Skanneri (Solmu A / stp_111):** Lukee PDF:n (`$inputs.document`) ja tuottaa raakatekstin.
- **Faktantarkistaja (Solmu B / stp_222):** Koska UI tietää analyysin vaativan *molemmat*, pudotusvalikko pakottaa kytkemään *Skannerin* (`stp_111.output`) suoraan *Faktantarkistajan* `context` -kenttään ilman, että käyttäjä tarvitsee muistaa ID-koodeja.

## 🛠️ 4. Hyväksymiskriteerit (Definition of Done)
1. **Pydantic V2 Strict:** `Step`-luokka tukee uusia kenttiä Rust-Core strict -tasolla poikkeuksetta.
2. **Backend Seed Validointi:** Paikallinen `uv run python backend_v2/seed/run_seed.py local` menee läpi ilman kaatumisia.
3. **Isolate Freezed Parity:** Flutter osaa parsia `expectedInputs` taustasäikeessä virheittä.
4. **Zero-Typo UI:** Vapaan tekstin syöttö (`TextFormField`) `inputMappings`-matriisiin on tehty täysin mahdottomaksi Admin Studiossa.
5. **No Errors:** Koko 14-kerroksinen järjestelmä läpäisee `mypy --strict` ja `dart analyze` käännökset nollalla virheellä.
