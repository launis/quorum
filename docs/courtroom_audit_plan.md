# Courtroom 2.0 (Full Audit) - Askeleittainen Korjaussuunnitelma (Dynaamiset Syötteet ja BARS-matriisit)

Tämä raportti erittelee yksityiskohtaisesti kaikki `workflow_courtroom_20_full_audit` -työnkulun kohdat, jotka vaativat muutoksia `seed_data.json` -tiedostossa, jotta järjestelmä tukee täydellisesti rajoittamatonta määrää mielivaltaisesti nimettyjä syötetiedostoja, ja jotta epämääräiset tekstikentät korvataan Pydantic-turvallisilla BARS-matriiseilla.

## 1. Ongelma: Staattinen `input_mappings` jokaisessa askeleessa (15 kpl)

**Nykyinen tilanne:**
Jokainen työnkulun 15 Node-askeleesta (esim. `step_node_1` -> `step_node_15`) on määritelty `seed_data.json` -tiedostossa seuraavasti:
```json
"input_mappings": {
  "context": "$inputs.chat_log",
  "document": "$inputs.document_text"
}
```

**Syy miksi tämä rikkoo dynaamisuuden:**
Vaikka Pydantic-mallit ja hookit on nyt refaktoroitu ottamaan vastaan rajattomasti eri avaimia, tämä yllä oleva DAG-määritys *suodattaa* syötteen niin, että Node saa datakseen VAIN "chat_log" ja "document_text". 

**EHDOTETTU KORJAUS:**
Jokaisen 15 askeleen kohdalla `seed_data.json` -tiedostossa vaihdetaan mappaamaan suoraan koko `$inputs` -olio:
```json
"input_mappings": {
  "inputs": "$inputs"
}
```

---

## 2. Ongelma: Tekoälyn Järjestelmäkehotteet (PromptBlocks) olettavat tiettyjä tiedostoja

**Nykyinen tilanne:**
Quorum V2 rakentaa promptit yhdistelemällä `PromptBlock` -elementtejä, jotka tällä hetkellä olettavat syötteeksi "keskusteluhistoriaa" ja "lopputuotetta".

**EHDOTETTU KORJAUS:**
Käyttäjä on jo laatinut valtaosan PromptBlockeista V2-dynaamisuuteen sopiviksi. Korvaamme nämä (esim. `block_globalcontext`) täsmällisesti yksi kerrallaan käyttäjän toimittamiin, dynaamisiin versioihin, jotka lukevat "kaikkea toimitettua aineistoa".

---

## 3. Ongelma: Dynaamisten Syötteiden Roolit ja Selitteet (`ai_description`)

**Nykyinen tilanne:**
`seed_data.json` -tiedostossa on määritelty `expected_inputs` -osiossa kenttiä kuten `ai_description`. Nämä kentät kertovat tekoälylle, mikä kunkin tiedoston *funktio* on, mutta niitä ei injektoida LLM:lle asti.

**EHDOTETTU KORJAUS:**
Päivitämme `input_processing.py` -hookin käärimään jokaisen dynaamisen syötteen arvon JSON-objektiin:
```json
{
  "liite_1": {
    "role_description": "Tämä on käyttäjän vapaamuotoinen reflektio.",
    "content": "Lorem ipsum"
  }
}
```

---

## 4. UUSI VAIHE: Epämääräisten tekstuaalisten luokitteluiden muuttaminen BARS-matriiseiksi

Yksi V2-arkkitehtuurin kulmakivistä on "Universaali Mittausarkkitehtuuri ('PromptBlocks')". Olemme tunnistaneet työnkuluista useita tekstipohjaisia enum-kenttiä, jotka on syytä muuttaa vahvasti tyypitetyiksi BARS (Behaviorally Anchored Rating Scale) -matriiseiksi "numeric"-tyypillä (ilman desimaaleja).

Tämä pakottaa Pydanticin ja LLM:n tuottamaan tarkan numeron, jonka UI voi lokalisoida haluamastaan `.arb` tiedostosta.

### 4.1. `block_taskarchivist` (Compliance Score & Analysis)
**Tavoite:** Yhdistää vapaamuotoinen 'compliance_analysis' (esim. "Critically Misaligned") ja numero 1-5 samaksi BARS-matriisiksi.
**Käytännön toteutus (seed_data.json muutos):**
- **Tyyppi:** `"type": "numeric"`
- **Desimaalit:** `"allow_decimals": false`
- **Scales:**
  - `1`: "Täysin satunnainen prosessi ilman linjakkuutta. Vastaa 'Critically Misaligned'."
  - `2`: "Hajanaista prosessin noudattamista. Vastaa 'Misaligned'."
  - `3`: "Jonkinlainen prosessi näkyvissä, mutta ei noudata alan standardeja täysin. Vastaa 'Neutral'."
  - `4`: "Noudattaa alan standardeja ja best practiceja hyvin. Vastaa 'Aligned'."
  - `5`: "Täydellinen State-of-the-Art (esim. OpenAI Cookbook) käytäntöjen noudattaminen. Vastaa 'Strongly Aligned'."

### 4.2. `block_taskinteraction` (Role Classification / Arkkityyppi)
**Tavoite:** Muuttaa sanallinen arkkityyppi ("Passenger", "Navigator", "Driver", "Architect") skaalaksi 1-4.
**Käytännön toteutus:**
- **Tyyppi:** `"type": "numeric"`
- **Scales:**
  - `1`: "Passenger (Matkustaja): Passiivinen tilaaja. Antaa vain 1-2 sanan komentoja ja odottaa tekoälyn tekevän työn."
  - `2`: "Navigator (Suunnistaja): Suunnistaa olemassa olevan aineiston varassa, pyytää korjauksia mutta ei ohjaa logiikkaa."
  - `3`: "Driver (Kuljettaja): Aktiivinen ohjaaja. Antaa kontekstia, määrittää tavoitteen ja hallitsee prosessia."
  - `4`: "Architect (Arkkitehti): Suunnittelija. Strateginen tason johtaja, hyödyntää tekoälyä omien ajatusmalliensa skaalaamiseen."

### 4.3. `block_taskinteraction` (Strategy)
**Tavoite:** Muuttaa promptausstrategia ("Zero-shot", "Few-shot", "Chain-of-Thought") skaalaksi 1-3.
**Käytännön toteutus:**
- **Tyyppi:** `"type": "numeric"`
- **Scales:**
  - `1`: "Zero-shot: Suora käsky ilman ohjeistusta askeleista tai esimerkkejä."
  - `2`: "Few-shot: Antaa esimerkkejä tai rakennemalleja, joiden pohjalta tekoälyn tulisi toimia."
  - `3`: "Chain-of-Thought: Pakottaa järjestelmällisen askel-askeleelta etenemisen tai loogisen ketjun."

### 4.4. `block_taskcausal` (Simulation Result / Counterfactual Test)
**Tavoite:** Muuttaa vastafaktuaalisen testin tulos ("IMPOSSIBLE", "PLAUSIBLE", "HIGH") skaalaksi 1-3.
**Käytännön toteutus:**
- **Tyyppi:** `"type": "numeric"`
- **Scales:**
  - `1`: "Mahdoton (Aito riippuvuus): Jos käyttäjä ei olisi esittänyt väitettä, tekoäly ei koskaan olisi päätynyt tähän tulokseen."
  - `2`: "Mahdollinen: Vaikka käyttäjä poistettaisiin, tekoäly saattaisi satunnaisesti päätyä samaan tulokseen."
  - `3`: "Todennäköinen (Riippumaton): Käyttäjän väitteellä ei ole vaikutusta; tekoäly olisi joka tapauksessa tuottanut tämän aineiston pohjalta."

### 4.5. `block_taskxai` (Confidence Score)
**Tavoite:** Estää lennokkaat desimaalit (.8754) ja sitoa epävarmuus selkeisiin neliportaisiin tai viisiportaisiin prosentteihin, jotka UI voi renderöidä kauniisti.
**Käytännön toteutus:**
- **Tyyppi:** `"type": "numeric"`
- **Desimaalit:** `"allow_decimals": false`
- **Scales:**
  - `0`: "Täysin epävarma (0%). Data on erittäin ristiriitaista eikä luotettavaa johtopäätöstä voida vetää."
  - `25`: "Epävarma (25%). Huomattavasti tulkinnanvaraista tai puutteellista dataa."
  - `50`: "Neutraali (50%). Data on osittain ristiriitaista mutta suuntaa antavaa."
  - `75`: "Melko varma (75%). Vahvaa näyttöä, pienillä epävarmuuksilla."
  - `100`: "Ehdottoman varma (100%). Raskas ja kiistaton todistusaineisto lokissa."

### 4.6. `block_taskguard` (Risk Level Oikaisu)
**Tavoite:** Guardilla oli päällekkäinen `simulation_result` (joka kuuluu Arkkityypille). Poistetaan se Guardista, ja muutetaan risk_level (High/Low) BARS-skaalaksi.
**Käytännön toteutus:**
- **Tyyppi:** `"type": "numeric"`
- **Scales:**
  - `1`: "Matala riski: Strukturoitua, turvallista ja asiallista dataa sisältävä ohjeistus."
  - `2`: "Keskisuuri riski: Epämääräinen tai heikosti strukturoitu pyyntö, muttei suora kyberuhka."
  - `3`: "Korkea riski: 'Lazy Prompting' (alle 5 sanaa, ei kontekstia) tai täysin roskadataa."
  - *(Huomio: Poistetaan Guardin PromptBlockista maininnat `simulation_result`:in täyttämisestä)*

---

## Toteutuksen Vaiheistus ja Milestonet (Lost in the Middle -esto)

Koska `seed_data.json` on massiivinen, kaikki muutokset toteutetaan vahvasti eristettyinä milestoneina:

1. **VAIHE 1: Backend-integraatio (`input_processing.py`).**
2. **VAIHE 2: Ohjelmallinen DAG-Mappaus-korjaus (Python Skriptillä).** 
3. **VAIHE 3: PromptBlockien korvaaminen sanasta sanaan (käyttäjän toimittamilla aineistoilla), yksi block kerrallaan.**
4. **VAIHE 4: BARS-Matriisien Asennus (Kohdat 4.1 - 4.6 yllä), jokainen matriisi täysin omana erillisenä JSON-muokkauksenaan.**
