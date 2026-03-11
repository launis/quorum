# Courtroom 2.0 (Full Audit) - Askeleittainen Korjaussuunnitelma (Dynaamiset Syötteet)

Tämä raportti erittelee yksityiskohtaisesti kaikki `workflow_courtroom_20_full_audit` -työnkulun kohdat, jotka vaativat muutoksia [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) -tiedostossa, jotta järjestelmä tukee täydellisesti rajoittamatonta määrää mielivaltaisesti nimettyjä syötetiedostoja. **Yhtäkään tiedostoa ei ole vielä muutettu; tämä on toimintasuunnitelma.**

## 1. Ongelma: Staattinen `input_mappings` jokaisessa askeleessa (15 kpl)

**Nykyinen tilanne:**
Jokainen työnkulun 15 Node-askeleesta (esim. `step_node_1` -> `step_node_15`) on määritelty [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) -tiedostossa seuraavasti:
```json
"input_mappings": {
  "context": "$inputs.chat_log",
  "document": "$inputs.document_text"
}
```

**Syy miksi tämä rikkoo dynaamisuuden:**
Vaikka Pydantic-mallit ja hookit on nyt refaktoroitu ottamaan vastaan rajattomasti eri avaimia, tämä yllä oleva DAG-määritys *suodattaa* syötteen niin, että Node saa datakseen VAIN "chat_log" ja "document_text" (jota ei edes ole olemassa, koska UI lähettää "product_text"). Jos käyttäjä lataa esimerkiksi 5 tiedostoa avaimilla `liite_1`, `liite_2`, `lasku_a`, tämä injektori ohittaa ne kaikki.

**EHDOTETTU KORJAUS:**
Jokaisen 15 askeleen kohdalla [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) -tiedostossa vaihdetaan mappaamaan suoraan koko `$inputs` -olio:
```json
"input_mappings": {
  "inputs": "$inputs"
}
```
Näin jokainen tekoälyagentti ja -koodi näkee kaikki käyttäjän lähettämät tiedostot täysin as-is.

---

## 2. Ongelma: Tekoälyn Järjestelmäkehotteet (PromptBlocks) olettavat tiettyjä tiedostoja

**Nykyinen tilanne:**
Quorum V2 rakentaa promptit yhdistelemällä [PromptBlock](file:///c:/src/quorum/backend_v2/models/v2_core.py#67-149) -elementtejä (esim. `block_agent_analyst`, `block_agent_falsifier`). Näissä blokeissa lukee tällä hetkellä usein rakenteellisia kehotteita, kuten:
*   *"Tässä on keskusteluhistoria (Chat History) ja tässä on lopputuote (Product)."*
*   *"Analysoi historia ja vertaa sitä tuotteeseen."*

**Syy miksi tämä rikkoo dynaamisuuden:**
Jos käyttäjä ajaakin työnkulun 15 tiedostolla "Talousraportit Kuukausittain", Chat Parser jäsentelee ne dynaamisina tiedostoina JSON-muotoon, mutta LLM hämmentyy, koska sille on kerrottu sen tutkivan "Keskusteluhistoriaa".

**EHDOTETTU KORJAUS:**
Käymme läpi Courtroom 2.0:n tarvitsemat ydin-PromptBlockit [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) -tiedostosta ja muutamme "keskusteluhistoria"-sanan dynaamista ympäristöä tukevaksi:
*   **Aiemmin:** `"Analysoi oheinen keskusteluhistoria ja vertaa sitä lopputuotteeseen."`
*   **Korjaus:** `"Analysoi oheinen aineisto (Inputs). Aineisto voi sisältää mitä tahansa dokumentteja, lokeja tai tehtävänantoja. Käsittele kaikkea saatavilla olevaa tietoa kokonaisuutena."`

### Konkreettiset muokattavat Prompt Blockit:
1.  **Analyst (`block_agent_analyst`):** Prompti päivitettävä tutkimaan "kaikkea toimitettua aineistoa".
2.  **Profiler (`block_agent_profiler`):** Prompti päivitettävä muotoon "Luo profiili aineistossa esiintyvästä toimijasta."
3.  **Logician / Falsifier (`block_agent_logician`, `block_agent_falsifier`):** Korvataan oletus historia/tuote -vastakkainasettelusta puhtaaseen Toulmin/Popper -analyysiin *suhteessa kaikkeen toimitettuun aineistoon*.
4.  **Coach / Judge (`block_agent_coach`, `block_agent_judge`):** Palaute annetaan "koko käytettävissä olevan aineiston ja muiden asiantuntijoiden raporttien perusteella."

---

## 3. Ongelma: PromptBlockien Ristiriitaisuuksien Järjestelmällinen Tutkiminen (`description` -kentät)

**Nykyinen tilanne:**
Kuten yllä havaittiin, jotkin pääblokkien (kuten Analystin ohjeistukset) promptit sisältävät oletuksia. Järjestelmässä on kuitenkin kymmeniä muitakin PromptBlockeja (kuten `block_instruction1`, `block_heuristic1`, `block_protocol2`), joita ketjutetaan agenttien ohjeistuksiin. 

**Riski:**
Jos tutkitussa yhdistelmässä on yksikin ristiriitainen kehotus (esim. yksittäisessä Heuristiikka-blokissa lukee "Vertaa AINA tulosta Chat Historyyn"), se voi kaataa tekoälyn suorituksen täysin, koska se menee sekaisin dynaamisesta JSON-syöterakenteesta. Käytännössä yksikin väärä `description.translations.fi` -määräys sabotoi "yhden totuuden" mallin (Pydantic SSOT), jos tekoälylle annetaan ohjeita dataan liittyvistä rajoitteista, joita ei enää ole.

**EHDOTETTU KORJAUS (Auditoinnin aikana toteutettava):**
Auditoinnissa minun on luettava ja analysoitava JOKAISEN `workflow_courtroom_20_full_audit` -työnkulussa käytettävän lokaalin PromptBlockin (`description.translations.fi`) sisältö. Varmistan systemaattisesti seuraavat asiat:
1.  **Vapaamuotoiset viittaukset:** Etsin sanastoa kuten "chat history", "tuote", "lokitieto" (ja niiden englanninkieliset vastineet) ja varmistan, että ne on kirjoitettu dynaamisen inklusiivisiksi (esim. "käytettävissä oleva aineisto", "dokumentit", "liitteet").
2.  **Rooliristiriidat:** Varmistan, ettei mikään yksittäinen heuristiikka tai protokolla anna määräyksiä *spesifin* tiedoston etsimisestä, kun tiedoston nimi tai olemassaolo voi olla dynaamista. Analyysin tulee ohjeistaa tutkimaan *esitettyä todistusaineistoa ja annettua syötettä*, mitä ikinä käyttäjä onkaan lähettänyt analytiikan kohteeksi.
3.  **Rakenneoletukset:** Varmistan, ettei mikään blokki kehota tekoälyä "lukemaan JSON:n alkuosaa" tai oleta rakenteelta mitään tiettyä järjestystä, vaan että tiedot voivat uida dynaamisina kokonaisuuksina.

*Toimenpide suunnitelmassa:* Raportti edellyttää, että käyn "suurentamislasilla" läpi kaikki blokit (Metodit, Protokollat, Ohjeistukset) ennen koodin/JSON:n päivittämistä, jotta `courtroom_audit_plan` kattaa koko logiikkapuun 100% kattavuudella eikä sisällä ristiriitaisia ohjeita LLM:lle.

---

## 4. Ongelma: Workflow Päättelyn Ketjutus (Step Dependency)

**Nykyinen tilanne:**
Myös välivaiheiden tuotokset (esim. Analystin vastaus) ohjataan eteenpäin seuraavalle nodelle:
```json
"input_mappings": {
  "step_node_3": "$step_node_3.output"
}
```

**Syy miksi tämä on oikein:**
Tämä osa on V2 arkkitehtuurissa mallinnettu **täydellisesti**. Koska muutin jo Pydantic-mallit hyväksymään `extra="allow"`, edellisten agenttien tuotokset valuvat siististi seuraavalle LLM:lle osana isoa [Inputs](file:///c:/src/quorum/backend_v2/models/domain/inputs.py#8-60)-JSON-kokonaisuutta.

**EHDOTETTU KORJAUS:**
Näihin riippuvuuksiin (Depends On ja step_node_X) ei kosketa. Ainoastaan perus inputs-mäppäys korjataan.

---

## 5. Ongelma: Dynaamisten Syötteiden Roolit ja Selitteet (`ai_description`)

**Nykyinen tilanne:**
Käyttäjä huomautti, että [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) -tiedostossa on määritelty `expected_inputs` -osiossa kenttiä kuten `ai_description`. Nämä kentät kertovat tekoälylle, mikä kunkin tiedoston *funktio* on (esim. "Tämä on käyttäjän vapaamuotoinen reflektio"). Tällä hetkellä tätä metatietoa ei kuitenkaan koskaan syötetä LLM:lle asti osaksi analyysiä.

**Syy miksi tämä on ongelmallista:**
Jos promptissa vain lukee "käsittele oheinen aineisto", LLM joutuu itse arvailemaan, onko teksti `Talousraportti` vai `Käyttäjän reflektio`, vaikka meillä on tuo tieto UI:sta saatavilla. Tämä voi johtaa hallusinaatioihin tai väärintulkintoihin. 

**EHDOTETTU KORJAUS:**
Kun korjaamme agenttien promptit (kohta 2), meidän on varmistettava, että järjestelmä ketjuttaa automaattisesti tiedostojen roolit aineiston yhteyteen. Korjaamme siis promptin rakenteen (eli PromptBlockien ja LLM-runkorakenteen) ottamaan tämän huomioon:

**Toimenpide (Backendin Python-koodin puolella, ei suoraan pelkässä JSONissa):**
Kun kokoamme syötteen tekoälylle (esim. `InputsProcessor` tai LLM-ajon rakentaja `engine/llm_router`), meidän tulee huolehtia siitä, että [inputs](file:///c:/src/quorum/backend_v2/hooks/input_processing.py#56-142) JSON-rakenteeseen injektoidaan itse tekstin lisäksi kyseisen avaimen `ai_description`, joka on määritelty työnkulussa.
LLM:lle menevä rakenne ei saa olla vain:
```json
{"liite_1": "Lorem ipsum"}
```
Vaan sen tulisi näyttää tältä:
```json
{
  "liite_1": {
    "role_description": "Tämä on käyttäjän vapaamuotoinen reflektio.",
    "content": "Lorem ipsum"
  }
}
```
*Toteutustapa suunnitelmassa:* Raportti suosittaa tarkistamaan, miten backend kokoaa `$inputs` objektin suoritusaikana, ja tarvittaessa joko a) injektoimaan `ai_description` suoraan LLM:n saamaan datasanakirjaan, tai b) lisäämällä PromptBlockeihin eksplisiittisen kehotteen: *"Huomioi aineiston ohessa toimitetut roolikuvaukset (role_description) ymmärtääksesi kunkin tiedoston kontekstin."*

---

## Yhteenveto Seuraavista Toimenpiteistä ja Vaiheistus (Miten vältämme "Lost in the Middle" -virheet)

Koska [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) on yli 4000 riviä pitkä ja prompt\_blockeja on kymmeniä, ison massamuokkauksen tekeminen kerralla (Big Bang) voi aiheuttaa minulle (tekoälylle) "Lost in the Middle" -ilmiön tai rikkoa JSON-syntaksin vahingossa. Siksi suunnitelman *toteutus* tehdään ehdottomasti erittäin pienissä, eristetyissä vaiheissa. 

**Toteutuksen Vaiheistus:**

**Vaihe 1: Backend-integraation (Python) varmistaminen (Pieni riski)**
Tässä vaiheessa emme vielä koske JSON:iin. Päivitämme vain Python-koodin puolella, että kun agentit lukevat `$inputs`, ne myös näkevät kentän tyyliin `{"asiakirja_1": {"role": "ai_description", "content": "..."}}`.
1.  **Toimenpide:** Etsitään ja päivitetään tiedosto/hook, joka rakentaa tekoälyn näkemän lopullisen payloadin (esim. [hydration.py](file:///c:/src/quorum/backend_v2/hooks/hydration.py) tai `llm_router.py`). Varmistetaan pytestillä tai yksinkertaisella CLI-ajolla, että kentät menevät oikein läpi.

**Vaihe 2: Olemassa olevien 15 DAG-askeleen Input Mappausten korjaus (Mekaaninen)**
Käyn läpi ainoastaan työnkulkujen `input_mappings` -lohkot. 
1.  **Toimenpide:** Kirjoitan pienen ohjelmallisen Python-skriptin (`refactor_mappings.py`), joka lukee [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) tiedoston, muuttaa "context" ja "document" -viittaukset puhtaaksi `"inputs": "$inputs"` -mäppäykseksi juuri ja vain työnkuluille `workflow_courtroom_20_full_audit` ja `workflow_courtroom_30_fused_critics`.
2.  **Toimenpide:** Ajan skriptin ja tarkastan rakenteen. Tämä eliminoi tekoälyn manuaalisen luku/kirjoitus -hallusinaation riskin tyystin.

**Vaihe 3: PromptBlockien Yksittäinen Auditointi ja Ristiriitojen Ratkaisu (Eräkäsittely)**
Promptblokit ovat suurin riski "Lost in the Middle" -ongelmalle.
1.  **Toimenpide:** Teen erillisen haun, jolla lataan muistiini *kerrallaan* vain kourallisen yksittäisiä [PromptBlock](file:///c:/src/quorum/backend_v2/models/v2_core.py#67-149)-objekteja (esim. 5 agentin pääpromptia).
2.  **Toimenpide:** Muokkaan ainoastaan näitä viittä, siivoan pois "Chat History" -viittaukset tehden teksteistä yleismaailmallisia.
3.  **Toimenpide:** Tallennan tiedoston ja *pyydän sinulta hyväksynnän/käynnin läpi*.
4.  **Toimenpide:** Toistan haun metodeille ja protokollille (esim. 10 kerrallaan), päivitän, testaan. Jätän kokonaan rauhaan ne, jotka tukevat jo valmiiksi dynaamisuutta (kuten "Tarkista lainsäädäntö").

**Vaihe 4: End-to-End Testaus**
Kun kaikki kolme vaihetta on tehty, kokeilemme ajaa live-version käyttöliittymästä usealla oudolla liitetiedostolla ja katsomme, ymmärtääkö LLM tiedostojen roolit ja säilyykö streami auki loppuun saakka.
