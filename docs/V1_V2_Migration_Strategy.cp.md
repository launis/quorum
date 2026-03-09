# V1 -> V2 Migraatiostrategia (Komponenttien yhdistäminen Matriiseiksi)

## Johdanto
Käyttäjä on ehdottanut ratkaisua V2-arkkitehtuurin yksinkertaistamiseksi: **Poistetaan täysin dedikoitu legacy-tyylinen `Component`-kokoelma ja siirretään kaikki V1-komponentit osaksi V2:n `UniversalMatrix`-mallia.** 

Tämä tarkoittaa, että jopa puhtaat ohjetekstit ("INSTRUCTION", "MANDATE", "RULE", "HEADER"), jotka eivät odota tekoälyltä dynaamista JSON-palautetta, kohdellaan jatkossa *matriiseina* (tai pikemminkin "Prompt-komponentteina"), joilla on vain ohjeellinen tekstisisältö.

Täydennettynä ehdotuksella **Slug-perustaisesta linkityksestä**, V2:n työnkuluista (Workflow) poistettaisiin kokonaan riippuvuus kryptisiin UUID-tunnisteisiin, mikä edistää "No-String Mandate" sekä "De-Generator" -periaatteita äärimmilleen.

---

## 1. Miten tämä toteutettaisiin (Toteutusperiaate)

### A) Tietomallin rikastaminen (V2 UniversalMatrix)
Jotta puhdas tekstikomponentti voi toimia osana `UniversalMatrix`-kokoelmaa, datatyypin valinnan on tuettava "ei palautettavaa arvoa" -tyyppiä.
*   **Lisäys uusi tyyppi:** `backend_v2/models/enums.py` -tiedostoon `MatrixDataType` saa arvon `INSTRUCTION` tai `NONE`.
*   **Sisällön migraatio:** V1:n `content`-kenttä pakataan V2:n `description`-kenttään, joka hyödyntää `I18nText`-käännösrakennetta. (Tai vaihtoehtoisesti `UniversalMatrix`:iin lisätään oma `content: I18nText` -kenttä juuri Prompt-injektiota varten).
*   **Slug Ensisijaiseksi:** Matriisin `id`-kenttään voidaan varastointia varten säilyttää UUID, mutta työnkulkujen askeleet osoittavat matriiseihin pelkän selkeän `slug`-kentän (esim. `TASK_JUDGE`) avulla.

### B) Työnkulkujen rakentaminen (Workflow DAG ilman UUID:tä)
V1:ssä workflow-taulu sisälsi pelkkiä kryptisiä UUID-listaohjeita.
V2:ssa `Workflow.steps`-lista sisältää viittauksia irrallisiin askeliin (`TaskBlueprint`). UUID-linkityksen sijaan voisimme siirtyä selkokieliseen viittaukseen. Se muuttuisi visuaalisesti ja ohjelmallisesti tähän suuntaan:
```json
// V2 Työnkulku (Workflow)
{
  "slug": "workflow_courtroom_30",
  "name": {"default_locale": "fi", "translations": {"fi": "Courtroom 3.0"}},
  "steps": [
    {"task_blueprint": "task_mandates"},
    {"task_blueprint": "task_judge"}
  ]
}
```
Tämä tekee JSON-tiedostosta aidosti ihmisen luettavan.

### C) Dynaaminen Pydantic Schema Generation (Prompt Compiler)
Kun tuleva `PromptCompiler` rakentaa tekoälyn kyselyn, se hakee työnkulun perusteella kaikki matriisit slugien mukaan ennalta määrätyssä järjestyksessä.
1.  **Tekstin kasaus (System Prompt):** Se poimii jokaisen matriisin kääntödatan (esim. `description.translations["fi"]`) ja liimaa ne peräkkäin yhdeksi "System Promptiksi".
2.  **JSON-Skeeman kasaus (Structured Output):** Se tarkistaa jokaisen matriisin datatyypin (`type`):
    *   Jos `type == MatrixDataType.INSTRUCTION`, se **ei tee mitään** dynaamiselle skeemalle.
    *   Jos `type == MatrixDataType.FLOAT` tai `STRING`, se **generoi dynaamiseen Pydantic-skeemaan vaaditut ohjeet** (esim. asettaen odotusarvoksi tietyn kentän `TASK_JUDGE_score`).

---

## 2. Näkökulmat, pohdinta ja vaihtoehdot

**Onko kaikki otettu huomioon?**
* **V2 Semantic Routing / Caching:** Koska sekä säännöt, otsikot että arviointikriteerit asuvat samassa `matrices` (tai prompt-kokoelma) taulussa, välimuistin hajauttaminen on menneisyydestä. Yhden tiedotteen päivittäminen invalidisoi välimuistin oikein.
* **UI Studion helppous:** Admin Studiossa ei tarvita kahta UI-näkymää (Legacy "Components" ja "Matrices"). On vain yksi lista rakennuspalikoita, joita käyttäjä voi raahata DAG-byggäimeen.
* **Validointi:** Joillakin komponenteilla V1:ssä (kuten säännöilla tai otsikolla) ei ollut `slug`:ia tai `name`:a vaan niissä luki vain `null`. Migraatiossa täytyy ajaa automaattinen generatori sellaisille objekteille.

**Vaihtoehdot (Alternatives):**

1.  **Täydellinen Sulautuminen (Ehdotettu Yhtymispiste):** 
    Kaikki yhdistetään V2 Matrix -luokkaan. `MatrixDataType.INSTRUCTION` on uusi normi pelkille tekstiblokeille.
    *   *Plussat:* 1 taulu, erittäin modulaarinen rakennusrakenne ("everything is a block"), täydellinen Zero-Compromise Pledgen toteutus.
    *   *Miinukset:* "Matriisi" sana viittaa arviointiin (Bars Matrix), joten terminologia voi hämätä, jos sana tarkoittaa nyt myös "perus system promtin sääntö 1:tä".

2.  **Rinnakkainen V2 'PromptBlock' -malli (Käsitteellinen Eriytys):** 
    Pidetään matriisi (arvioinnit) ja PromptBlock (ohjeet) taulut erillään, mutta pakotetaan molemmat taulut toimimaan samalla V2 I18N-periaatteella. Slugin avulla.
    *   *Plussat:* Käsitteellinen selkeys säilyy. Käyttäjä tietää, mikä on kriteeristö, mikä ohjeistus.
    *   *Miinukset:* Prompt Compilerin koodista tulee monimutkaista, kun pitää noutaa kahdesta eri tietokantataulusta luovien slugien välityksellä oikeassa järjestyksessä asioita.

**Johtopäätös:** Täydellinen sulautuminen (Vaihtoehto 1) on teknisesti kaikkein loogisin. Terminologisen hämmennyksen (Matriisi vs Komponentti) voi välttää kutsumalla koko tietomallia frontendin UI:ssa nimellä "Rakennuspalikat (Blocks)", mutta säilyttää backendissa nimen `matrices` (tai päivittää uuden luokan nimeksi `UniversalBlock`).

---

## 3. Kuinka Migrate-skripti pitäisi kirjoittaa uusiksi

Tällä hetkellä `backend_v2/scripts/migrate_v1_to_v2.py` tekee ns. "raaka-kopion" ja kopioi kaikki V1 `components` sellaiseen vanhakantaiseen formaattiin `core_routeriin`.

**Uusi skripti (`migrate_v1_to_v2.py` V2 täysversio):**
1.  **Drop V1 Components entirely:** Skripti ei enää luo 'components'-kokoelmaa V2-kantaan.
2.  **Transform to V2 UniversalMatrix (The Fusion):** 
    Tehdään for-looppi V1 komponentteille. Ne luodaan uusiksi Pydantic `UniversalMatrix` -olioiksi ja pumpataan yhdessä AI-matriisien kanssa `matrices`-tauluun.
    Miten mappaus toimii tekstin kohdalla:
    *   `id`: UUID
    *   `slug`: V1 slug tai autogeneroitu slug
    *   `label`: V1 slugista muotoiltu `I18nText`, jos nimi puuttuu.
    *   `description`: V1 `content` paketoituna `I18nText`:iin.
    *   `type`: `MatrixDataType.INSTRUCTION` (uusi enum-arvo)
    *   `allow_decimals` / `require_justification`: `False` (Koska ei datatyyppiä)
3.  **TaskBlueprints Rakennus:** V1:n irralliset askeleet (joissa oli pitkiä UUID-listoja ohjeita, esim `step_guard`) muutetaan `TaskBlueprint`-dokumenteiksi, joissa nämä UUID:t on korvattu uudelleen nimetyillä slugeilla (`prompt_blocks: ["rule_mandate_1", "criteria_judge_score"]`).
4.  **Workflows Rebuilding:** V1 UUID -listan sijaan skripti generoi askeleet viittaamaan suoraan yllä luotuihin TaskBlueprinteihin. Nyt työnkulun `steps` = `[ { "task_blueprint": "task_fused_audit_chain_dual" }, ... ]` JSON-tiedostossa.

---

## 4. Promptin Vertaileva Esimerkki (V1 vs V2 - Ei koodausta vielä)

### V1 Prompt (Staattiset DTO-luokat + Kovat Listat)
V1 kasasi promptin Python-koodissa ja ohjasi JSON:in tuloksen takaisin ohjelmoojan tekemiin DTO-luokkiin (esim. `LogicianOutputDTO`).

```text
SYSTEM PROMPT (Compiled from text loop):
### 1. PERUUTTAMATTOMAT MÄÄRÄYKSET (IRREVOCABLE MANDATES)
Mandaatti 1 (System 2 -Pakko): MÄÄRÄYS: Sinun ON käytettävä hidasta...

VAIHE 9: TUOMARI (JUDGE) - GRAND UNIFICATION
Toimit Järjestelmän Tuomarina. Tehtäväsi EI ole arvioida syötetekstin laatua...

KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN seuraavan JSON-skeeman mukaisesti:

STATIC JSON SCHEMA (Generated manually by Python Pydantic classes out-of-band):
{
  "type": "object",
  "properties": {
    "reasoning_trace": { "type": "string" },
    "score_card": { "type": "number" }
  }
}
```

### V2 Prompt (Dynaamisten Slug-Matriisien "De-Generator")
V2 Compiler ei tarvitse yhtään DTO-luokkaa (Kukaan ei osaa sanoa ennalta "Tuomari" tai "Logician"). Se vain poimii Slugin mukaisen tekstin, tulostaa "FI"-käännöksen, tyhjentää kentän, *ja rakentaa dynaamisen Schema-rungon täysin lennosta niille askeleille, joiden `type` ei ole 'instruction'*.

```text
SYSTEM PROMPT (Compiled fully dynamically from 'slugs'):
[Instruction FI]: ### 1. PERUUTTAMATTOMAT MÄÄRÄYKSET
[Instruction FI]: Mandaatti 1: Sinun ON käytettävä hidasta...
[Instruction FI]: VAIHE 9: TUOMARI (JUDGE) - GRAND UNIFICATION...

Ohje LLM:lle: Palauta mallioppilas-objekti tämän JSON-määrityksen periaatteella.

DYNAMIC Pydantic Schema (Generated at runtime based implicitly on the Matrix configs!):
{
  "type": "object",
  "properties": {
    "dynamic_TASK_JUDGE_reasoning": {
      "type": "string",
      "description": "VAIHE 9: TUOMARI (JUDGE) - GRAND UNIFICATION..."
    },
    ... (kaikki muut matriisit rakennetaan lennosta, paitsi ne joissa type="instruction")
  }
}
```
*Merkittävin ero*: V1-promptissa JSON-skeema ja säännöt ovat jumissa Python-koodeissa. V2-promptissa JSON-skeeman rakentaa lennolla `PromptCompiler` täysin ennalta-arvaamattomasti sen perusteella, mitä 'UniversalMatrix' malleja se lukee tietokannasta askeleen `TaskBlueprint` -profiilista! Järjestelmään voidaan keksiä uusi vaihe `TASK_NINDJA_COACH`, ja koko V2 järjestelmä mukautuu ilman ensimmäistäkään python-koodin muutosta.

---

## 5. Y-Funnelin ja Input Processorin Migraatio (Pre-Hooks & Worker)

V1-arkkitehtuurissa ensimmäinen askel (`step_input_processor`) oli "jumbo-agentti", johon oli kovakoodattu sekä determinististä Python-logiikkaa (Base64-tiedostojen purku, Reflection-muotoilut) että LLM-logiikkaa (`ChatParser`, `ChatLogParser`).

V2-arkkitehtuurissa ja uudessa matriisi-mallissa "No-String Mandate" purkaa tämän yksittäisen tiedoston kahdeksi erilliseksi kerrokseksi. **Tärkeä huomio: kaikki tämä prosessoidaan edelleen täysin turvallisesti turva-aidan sisällä raskaana taustatyönä (Worker), täsmälleen samassa moottorissa (WorkflowEngine) kuin V1:ssä, kaukana kevyestä API-rajapinnasta.** Mutta vastuunjako moottorin *sisällä* on uusi:

### 1. Deterministinen kerros (Pre-Hooks / PrepService)
Kaikki raskaat, mekanistiset datakonversiot, joihin *ei* tarvita tekoälyä, siirretään ns. Pre-Hookeiksi, jotka valmistellaan Workerissa ennen askeleiden alkamista:
*   `ExecutionPrepService` hoitaa Base64-pakkausten purkamisen asynkronisesti Workerissa.
*   `ReflectionService` muokkaa SDUI-Guided Reflectionin markdowniksi.
*   Nämä tungetaan suoraan Globaaliin Execution Contextiin, sijoitukseen `$inputs.historia`, `$inputs.reflektio` jne.

### 2. Kognitiivinen kerros (Aito Workflow Askel LLM:llä)
Kaikki LLM-siistiminen (kuten V1 `chat_parser.py`:n chat-logien uudelleenjärjestely ihmisen/tekoälyn vuorosanoiksi) muuttuu pelkäksi **täysin tavalliseksi työnkulun askeleeksi (DAG Node)**. Tämä poistaa täysin entisen `input_processor.py` agenttiluokan olemassaolon.

V2 Työnkulussa tämä näyttää orkestraattorille tältä:
```json
{
  "id": "step_chat_parsing",
  "task_blueprint": "task_chat_parsing",
  "input_mappings": {
    "raw_chat": "$inputs.history_text"
  }
}
```

Kun Workerin suoritinmoottori tulee tähän askeleeseen:
1.  Se lukee askeleen `TaskBlueprintin` ja hakee sieltä slugien mukaiset matriisit, eli ne promptit jotka V1:ssä makasivat syvällä Python-koodeissa.
2.  LLM suorittaa parsing-työn ja asettaa tulokset Workerin väliaikaisvarastoon dynaamisin avaimin.
3.  Tuomari (Judge) poimii myöhemmin tämän siistityn datan suoraam `$steps.step_chat_parsing.output.xxx` osoitteella.

**Hyöty Worker-tason migraatiossa:**
Raskas työ on edelleen suojassa katkeamisilta Celery-Workerissä. Mutta jatkossa, kun järjestelmään pitää tuoda täysin uusi Y-Funnel parseri (esimerkiksi "Kokouspöytäkirjan siistijä"), emme tee uutta python-moduulia emmekä käynnistä kontteja uudelleen. Me yksinkertaisesti luomme graafisessa Admin Studiossa uuden ohjematriisin (Slug: `INSTRUCTION_MINUTE_CLEANER`) ja kytkemme sen graafilla Workflowhun. Workerin ohjausmoottori poimii sen lennosta.

---

## 6. Muiden askelten Input/Output - V1 vs V2 Vertailu

Miten kaikki "normaalit" askeleet (Tuomari, Analyytikko, Synteesi) käyttäytyvät verrattuna V1-tapaan?

### V1-Tapa (Staattinen Putki - The Pipeline)
V1:ssä askeleet (esim. `step_judge`) olivat sidottu toisiinsa kovan koodin putkessa. Askel *A* oletti aina saavansa Inputin tietyssä `WorkflowInputs` -muodossa ja palautti ulos koodiin kovakoodatun `JudgeOutputDTO` -luokan.
*   **Input:** Perustui siihen, mitä `execution_prep_service.py` oli globaaliin objektiin puskenut.
*   **Output:** Määräytyi täysin Python-luokan `DTO` (Data Transfer Object) perusteella.
*   **Ongelma:** Jos halusit, että Tuomari huomioi Analyytikon tulokset, jouduit avaamaan Pythonin ja koodaamaan Tuomarin promptiin "Tässä on analyytikon tulos: {tulos}".

### V2-Tapa (Dynaaminen Graafi - The DAG)
V2:ssa askeleet ovat itsenäisiä solmuja graafissa (Directed Acyclic Graph). Niillä **ei ole ennalta määriteltyä Python-tason DTO:ta** inputille tai outputille. Ne sitovat syötteensä (inputs) ja luovat tulosteensa (outputs) lennosta matriisien perusteella.

**Input (Syöte) V2:ssa:**
Määritellään Admin Studiosta (tallennettu tietokannan workflow-JSON:iin) `input_mappings`-kentässä. Askel voi poimia vapaasti mitä tahansa aiemmista askeleista tai globaalista inputista.
```json
// Tuomari-solmu hakee datansa dynaamisesti muilta!
"input_mappings": {
  "syote_teksti": "$inputs.history_text", // Inputista
  "asiantuntijan_analyysi": "$steps.step_analyst.output.dynamic_ANALYSIS_score" // Aiemmalta V2 askeleelta!
}
```

**Output (Tuloste) V2:ssa:**
Generoidaan lennosta sen mukaan, mitä Matriiseja (`slug`) askeleelle kytketty `TaskBlueprint` sisältää.
Jos blueprintissä on kaksi matriisia (joista `type` on esim. STRING ja FLOAT): `["CRITERIA_CLARITY", "CRITERIA_LOGIC"]`,
Askelta suorittava moottori lukee ne ja pakottaa LLM:n palauttamaan dynaamisen JSONin:
`{"dynamic_CRITERIA_CLARITY_value": "Teksti on selkeää...", "dynamic_CRITERIA_LOGIC_value": 7.5}`.

Tämä jatketaan sellaisenaan graafin seuraaville solmuille. Kaikki askeleet ovat arkkitehtuuriltaan 100% identtisiä. Vain niihin osoitetun `TaskBlueprint`:in sisältämät Matriisit tekevät askeleesta Tuomarin tai Analyytikon.

---

## 7. Viimeinen Vaihe: Raportointi (Output ja Transformer)

Entä aivan lopussa? Miten datasta tulee visuaalinen raportti käyttäjille (kuten V1 ReportTransformer)?

### V1-Tapa (Python ReportTransformer)
V1:ssä oli raskas tiedosto `backend/transformers/report_core.py`. Kun kaikki askeleet olivat valmiita, tämä transformer keräsi `JudgeOutputDTO`:n ja `SynthesizerOutputDTO`:n kentät ja "käänsi" ne pitkän if-else-logiikan kautta `SemanticBlock` -raportti-elementeiksi.
Tämä oli "Violent Transformation" – uuden arviointikriteerin lisääminen UI-raporttiin vaati poikkeuksetta Python-koodausta kääntäjään!

### V2-Tapa (OutputConfigs & Semantic Router)
V2 ottaa käyttöön täysin tietokantaohjatun `output_configs` -kokoelman ("De-Generator" SDUI-raportointi).
Emme kirjoita enää Pythoniin raporttimuuntimia (Transformereita) kriteereille! Sen sijaan käyttäjä/admin määrittelee mallirekisterissä (Admin Studiossa), miltä loppuraportin tulisi näyttää.

**Migraatio (`migrate_v1_to_v2.py` laajennus):**
Kun siirrämme V1:stä komponentteja V2:een, me siirrämme luodut Matriisit myös osaksi raporttipohjaa.

Raportin luonti V2:ssa:
1. Kun DAG-työnkulku valmistuu, moottori istuu valtavan dynaamisen JSON-pinon päällä, joka sisältää kaikki `$steps.step_id.output...` arvot.
2. V2-Raporttigeneraattori hakee tietokannasta kyseisen työnkulun `OutputConfig` -dokumentin.
3. Se on visuaalinen sabluuna, joka on täynnä muuttujia. Se lukee esim:
   *  "Tee PDF:n ylälaitaan `hero_banner` komponentti, jonka arvo on `$steps.step_judge.output.dynamic_CRITERIA_CLARITY_value`".
4. Tämä generoituu automaattisesti SemanticBlock-listaksi (SDUI) rajapintaan, jonka Flutter ja PDF-generaattori renderöivät 100% samalla tavalla.

**Mitä tämä tarkoittaa koko V1 -> V2 migraation osalta:**
Kun luovutamme staattiset komponentit asettamalla ne matriiseiksi (`UniversalMatrix`), poistamme tarpeen ohjelmoida "agentteja" (Kuten InputProcessor tai Tuomari) sekä poistamme tarpeen ohjelmoida "Transformereita" (Kuten ReportTransformer). Järjestelmä on pelkkä tyhjä moottori (Engine), joka reitittää bittejä komponenttien slugien ja OutputConfigin sabluunoiden mukaan. Jopa raportti rakennetaan täysin dynaamisesti ilman koodimuutoksia.

---

## 8. V2-Nimistö (Nomenclature) - Käsitteiden Uudelleenristiminen

Koska muutamme koko arkkitehtuurin logiikkaa (sulautamme Komponentit ja Matriisit, ja poistamme kovat Agentti-luokat), meidän on erittäin suositeltavaa **uudelleennimetä** V1-perintöä olevat sekavat käsitteet koko ohjelmiston tasolla (Koodistossa, API:ssa ja UI:ssa) enemmän kuvaaviksi. 

Tässä on ehdotus ehdottomasta "V2 Sanakirjasta":

#### A) Ohjaus- ja Arviointidata (The Directives)
*   **V1 Nimi:** `Component` (Säännöt, ohjeet) ja `Matrix` (Arviointikriteerit)
*   **V2 Nimi:** `PromptBlock` (tai `KnowledgeBlock` / `CognitiveBlock`)
*   *Miksi:* Sana "Matriisi" on liian matemaattinen tai arviointiin viittaava, jos se sisältääkin tekstin "Olet Tuomari, puhut suomea". "Block" (Palikka) kuvaa täydellisesti sitä De-Generator-mentaliteettia, että rakennamme UI:ssa työnkulun palikoista.

#### B) Tekoälyn Tuottama Data (The Outputs)
*   **V1 Nimi:** `Dimension` (Arvioinnin yksittäinen vastaus askeleelta)
*   **V2 Nimi:** `Observation` (tai `ExtractedValue` / `DataPoint`)
*   *Miksi:* Sana Dimension (Ulottuvuus) oli aina todella sekava. Se oli vain LLM:n generoima dynaaminen avain-arvo-pari (esim. `{"score": 8.0, "reasoning": "Hyvä teksti"}`). "Observation" (Havainto) kuvaa paremmin sitä mitä tekoäly tuotti.

#### C) Orkestrointi (The Routing)
*   **V1 Nimi:** `Workflow` ja sen sisällä oleva kova lista `Steps` (esim. Tuomari, Synteesi).
*   **V2 Nimi:** `Workflow` on pelkkä reititin (Router). Sen sisällä olevat DAG Nodet viittaavat **uudelleenkäytettäviin askeliin (`TaskBlueprint`)**. Kuten PromptBlocks, myös Blueprintit ovat täysin riippumattomia yksittäisestä työnkulusta ja siksi globaalisti hyödynnettävissä.

#### D) Älykkyysosamäärät (The Intelligence)
*   **V1 Nimi:** `Agentit` (esim. `JudgeAgent`, `AnalystAgent`, joilla omat `.py` tiedostot)
*   **V2 Nimi:** `Roles` (Roolit) tai pelkkä `Step`. Ei ole enää Tuomari-Agenttia. On olemassa työnkulun askel nimeltä "Arviointi", joka on *omaksunut Tuomarin Roolin* lukemalla Tuomarin `PromptBlockit` tietokannasta.

Tämä nimistömuutos puhdistaa täysin sen sekasotkun, joka meillä V1:ssä oli "Matriisien" ja "Komponenttien" ja "Dimensioiden" kesken!

---

## 9. Mallirekisterin (Model Registry) Litteyttäminen

Käyttäjä huomautti kriittisestä ongelmasta V1-perintöä olevassa `system_config` -taulussa. Koska V2 on "Polymorphic" ja sallii kenen tahansa AI-tarjoajan, emme voi sitoa malleja "google"-hierarkian alle, tai jättää agenttien nimiä globaaliin asetukseen (Sillä kuten edellä mainittiin, Pythonissa ei ole enää agentteja, on vain dynaamisia Askeleita).

**Ongelma V1-rakenteessa:**
*   Liian syvä puurakenne (`models -> google -> fast -> max_tokens`).
*   Global Configurationissa on kovakoodattuja V1 agenttien nimiä (`JudgeAgent: precise`). 

**Ratkaisu V2-rakenteessa (Flattening & Decoupling):**
1. Erotetaan fyysiset mallit (LLM API:t). Jokainen malliprofiili (`fast`, `deep`, `strict`) tietää **itse** kuka on sen palveluntarjoaja (`provider: "google"` tai `provider: "openai"`).
2. Poistetaan Agentti-mäppäykset (`JudgeAgent: precise`) täydellisesti! Kuten edellä Strategia luvussa 6 & 7 sovittiin, me siirrämme älykkyystason suoraan osaksi Työnkulkujen (Workflow) askeleen graafimäärittelyä. Työnkulussa päätetään: "Tässä askeleessa ladataan Tuomari-palikat ja ajetaan 'precise' -mallistrategialla".

Tämä kruunaa järjestelmän modulaarisuuden. Globals ei rajoita Workflow:ta, eikä Google rajoita muita tarjoajia.

---

## 10. Migraation Aikainen Tietojen Siivous (Sanitation & Renaming)

Käyttäjä huomasi oikein, että vanha V1 data (esim. `seed_data.json`) sisältää paljon sekavia arvoja (esim. ID `matrix_input_processing`) ja täysin vanhentuneita avaimia (kuten `agent_type: "EvaluatorAgent"` sisällä matriisissa, vaikka moista ei V2:ssa ole).

Migraatioskriptin (`migrate_v1_to_v2.py`) olennaisin tehtävä ei olekaan pelkkä datan siirto putkessa, vaan sen **kääntäminen, puhdistaminen ja vakiointi (Sanitation)**.

Kun skripti pumppaa tietoa V1-kannasta V2-malleihin (osana `UniversalMatrix` tai V2 `Workflow` rakenteita), se tekee automaattisesti seuraavaa:
1.  **Roska-avainten karsinta (Pruning):** V2:n tiukat Pydantic-mallit (ja skripti) pudottavat armotta pois sellaiset V1-jäänteet kuin `agent_type`, `is_active`, tai `component_class`. Ne eivät siirry V2-kantaan lainkaan.
2.  **ID- ja Slug-standardointi:** Vanhat arviointikriteerit (esim. `matrix_judge`) nimetään skriptissä uudelleen loogisemmiksi, esim. ID:ksi generoidaan uusi UUID, tai sen nimeksi muutetaan `block_eval_judge`. Vastaavasti vanhat komponentit (esim. slug `MANDATE_1`) saavat johdonmukaisemman liitteen `RULE_MANDATE_1` tai `INSTRUCT_MANDATE_1`.
3.  **Kategoriat ja Tyypit (Roles vs Evaluations):** Migraatioskripti toteuttaa tiukan kahtiajaon. Kaikille askeleille ei enää pakoteta numeerisia arviointiasteikkoja. Jos kyseessä on vain tekoälylle suunnattu rooliohje (esim "Olet Analyst" tai "Input Processing"), se saa kategorian `agent_role` tai `system_rule` ja asettuu JSON:in `type: "instruction"`. Vasta aidot arvioivat mitat saavat `category_id: "cognitive_evaluation"` sekä numeeriset `scales`.
4.  **Työnkulkujen Askelten Ketjutus (Sequential Workflows):** Työnkulkujen JSON-askeleille generoidaan automaattisesti `depends_on`-riippuvuudet (esim. askel 2 odottaa etukäteen askelta 1) sekä asiaankuuluvat `input_mappings`-määritykset edellisestä askeleesta (`$step_id.output`), jotta rinnakkainen ajo estetään tarvittaessa.

**Lopputulos:** Kun `migrate_v1_to_v2.py` -skripti on ajettu, V2 tietokannassa ei ole *bittiäkään* sellaista tietoa joka muistuttaisi V1:n Python-agenttilyhenteistä (kuten EvaluatorAgent), ja kaikki nimet viittaavat siististi universaaleihin "Palikoihin" (tai Matriiseihin). UI asettaa sitten näille nätit käännökset (I18nText).

---

## 11. Empiirisen Prompt-Vertailun Tulokset ja Vaatimukset Migraatiolle

V1:n (staattinen DTO) ja V2:n (dynaaminen De-Generator) promptauslogiikan vertailu paljasti merkittäviä eroja, jotka ohjaavat **miten `migrate_v1_to_v2.py` -skripti on rakennettava**. 

Kun LLM-kyselyt muuttuvat Python-koodiin sidotuista luokista täysin tietokantaohjatuiksi dynaamisiksi JSON-skeemoiksi, asetamme skriptille kolme keskeistä vaatimusta:

### 1. DTO-Riippuvuuksien Katkaiseminen (Jäykkyys -> Skalautuvuus)
* **Analyysi:** V1:ssä agenttien tiedot (kuten kenttien nimet, tulostustyypit) makasivat syvällä Pydantic-malleissa. V2:ssa uusi `UniversalMatrix` (Palikka/Block) luo itselleen dynaamisen JSON-avaimen (esim. `dynamic_BLOCK_EVAL_POLITENESS_value`) täysin itsenäisesti.
* **Vaatimus migraatioskriptille:** Skriptin on varmistettava, että *mikään* V1-kannan vanha "agentti-lataus" -logiikka tai kovakoodattu kenttänimi ei siirry V2-kantaan. Kaikki datasta tehtävät ohjeet on irrotettava agentti-kontekstistaan ja purettava pelkiksi modulaarisiksi `UniversalMatrix` -riveiksi (`PromptBlockeiksi`).

### 2. Säännöt Osaksi Skeemaa (Hallusinaatioiden Väheneminen)
* **Analyysi:** Koska V2 injektoi arviointisäännöt ja ohjetekstit suoraan lennosta luodun JSON-skeeman `description` -kenttiin (eikä erilliseen kyselytekstiin kuten V1:ssä), LLM:n kognitiivinen keskittyminen kasvaa ja hallusinaatiot vähenevät. 
* **Vaatimus migraatioskriptille:** V1:n irralliset arviointikriteerit ja ohjetekstit (`content`) on yhdistettävä skriptissä oikeaoppisesti V2:n `UniversalMatrix.description` -kenttiin (I18nText-muodoissa). Skriptin huolellisuus tässä ratkaisee, pystyykö tuleva `PromptCompiler` nostamaan säännöt tekoälyn huomiopisteeseen.

### 3. Yhtenäistäminen (Pakkolaatoitettu Auditoitavuus)
* **Analyysi:** V1:ssä perustelukenttien nimet ja vaatimukset vaihtelivat satunnaisesti koodaajan muistin mukaan (`reasoning`, `justification`, `thought_process`). V2 lukitsee tämän järjestelmätasolla (Fail-Fast), pakottaen jokaiseen kriteeriin tarvittaessa yhtenäisen `dynamic_{slug}_justification` avaimen.
* **Vaatimus migraatioskriptille:** Kun skripti lukee V1:n komponentteja tai matriiseja, sen on älykkäästi pääteltävä, odottivatko ne tekoälyltä arvoa ja perustelua. Skriptin pitää asettaa V2-kannassa selkeä lippu `require_justification = True` tarpeen vaatiessa. Samalla voimme skriptissä siivota pois kaiken V1:n "Muista antaa perustelut" -roskatekstin, sillä V2-moottori hoitaa tuon validointirakenteen täysin automaattisesti kenttätasolla.

**Yhteenveto:** Uusi `migrate_v1_to_v2.py` ei saa olla pelkkä datan kopioija. Sen on oltava rakenteellinen kääntäjä, joka ymmärtää että data irrotetaan staattisesta V1 Python-muotista ja valmistellaan sataprosenttisesti dynaamista V2 De-Generator -moottoria ja Prompt Compilering lennosta luotavia käskyjä varten.

---

## 12. BARS Matriisien Arkkitehtuuri & Tieteellinen Tausta (AD1048729)

V2 PromptBlocks/Dimensions rakennetaan tiukasti klassisen **Behaviorally Anchored Rating Scales (BARS)** -viitekehyksen mukaisesti. BARS-asteikot noudattavat **tarkasti** taustalla olevan teorian kognitiivisia tasoja, ja ne sidotaan sekä numeroon että tasoa kuvaavaan nimeen jatkuvilla, eheillä skaaloilla ilman välihyppyjä.

### Toteutetut Tieteelliset BARS-Matriisit (category: `scientific_theory`)

Kovaa koodattua tekstiä ei jätetä UI-tasoon. Kaikki rakenteet, "Nimet" (Rivi/Sarakkeen nimi) ja "Väitteet" (Claims), viedään kantaan `I18nText` -muotissa (`default_locale` ja `translations`).

#### 1. Bloomin Taksonomia (Kognitiivinen Oppiminen)
*Tieteellinen tausta: Benjamin Bloom. Tieto- ja ymmärrystasojen syvyys.*
* **Asteikko: 1-6**
* **Tasot:** 1: Muistaminen, 2: Ymmärtäminen, 3: Soveltaminen, 4: Analysointi, 5: Arviointi, 6: Luominen. (Jokaisella vähintään kaksi yksilöllistä I18n väitettä).

#### 2. Kahnemanin Ajattelumallit (Kognitiivinen Kuormitus)
*Tieteellinen tausta: Daniel Kahneman (Thinking, Fast and Slow).*
* **Asteikko: 1-3**
* **Tasot:** 1: Systeemi 1 (Nopea/Intuitiivinen), 2: Siirtymä, 3: Systeemi 2 (Hidas/Analyyttinen ajattelu).

#### 3. Toulminin Argumentaatiomalli (Logiikka ja Perustelu)
*Tieteellinen tausta: Stephen Toulmin. Väitteiden rakenteellinen kestävyys.*
* **Asteikko: 1-5** (Heikko -> Välttävä -> Kohtalainen -> Hyvä -> Vahva)
* **Kriteeristö:** Arvioi väitteen, perusteen (data), oikeutuksen (warrant) ja vasta-argumenttien huomioinnin astetta.

#### 4. Performatiivisuus (Goodhartin Laki)
*Tieteellinen tausta: Charles Goodhart. Mittarin heikentyminen kun siitä tulee itse tavoite.*
* **Asteikko: 1-5** 
* **Tasot:** 1: Sokea usko mittariin, 2: Reaktiivinen huomioija, 3: Pintapuolinen optimoija, 4: Kriittinen ohjaaja, 5: Aktiivinen haastaja ohjaten takaisin alkuperäiseen tavoitteeseen.

#### 5. Tehtävävuorovaikutus (Task Interaction & Agency)
*Tieteellinen tausta: Moderni työnjako perustuen Sengeen (Systems Thinking), Fowleriin (Pair Programming) ja Coveyyn (Proaktiivisuus).*
* **Asteikko: 1-4**
* **Tasot:** 
  1: Matkustaja (Passenger - Passiivinen suorittaja, vaatii johtamista)
  2: Kuljettaja (Driver - Keskittyy toimeenpanoon ja maaliin viemiseen yksityiskohdissa)
  3: Navigaattori (Navigator - Taktinen ohjaaja ison kuvan näköalalla)
  4: Arkkitehti (Architect - Strateginen visionääri, suunnittelee olosuhteet/systeemin)
*Tieteellinen tausta: Karl Popper (Falsifiointiperiaate) - Pyrkimys kumota olemassa olevia väitteitä. Tasot 1-4.*
Esimerkki tietorakenteesta (Scale 4):
* **Piste (Score):** 4
* **Nimi (Name):** `{"fi": "Aito Falsifiointi", "en": "True Falsification"}`
* **Väitteet (Claims):**
  * `{"fi": "Käyttäjä yrittää ohjeistetusti murtaa...", "en": "The user attempts to break..."}`
  * `{"fi": "Käyttäjä pakottaa tekoälyn leikkimään Paholaisen asianajajaa...", "en": "The user forces the AI to play Devil's Advocate..."}`

---

## 13. Input Scope - Arvioinnin Kohdistaminen (Mihin dataan BARS osuu?)

Käyttäjä nosti esiin kriittisen kysymyksen: **"Mihin dataan BARS-matriisin arviointi kohdistuu? Eivätkö ne kohdistu kaikkiin input-tiedostoihin?"**

### Nykytilanteen ongelma (Globaali Konteksti)
Tällä hetkellä V2-arkkitehtuuri jakaa syötteet `raw_inputs` sisällä rooleittain (esim. `{"document": "tiedosto.pdf", "history": "chat_loki"}`). Jos BARS-arvioijalle (esim. `step_eval`) sanotaan vain: "Lue data ja arvioi BARS:lla", tekoäly lukee kaiken yhdessä köntässä (PDF:t, järjestelmäohjeet, käyttäjän chat-historian) ja tulos on sekava kompromissi analyysiä "käyttäjästä" ja tyhjästä "dokumentista".

Esimerkkejä BARS:sta:
* **Synteesi / Luovuus** arvioi *käyttäjän asennetta* ja iterointikykyä. Sen päädata on **Chat-historia**.
* **Laadullinen sisällönanalyysi** saattaa arvioida *tiedoston asiatekstiä*. Sen päädata on **Lähetetty Dokumentti**.

### Vaihtoehdot kohdistamisen (Scope) ratkaisemiseksi:

#### Vaihtoehto A: Globaali Työnkulun Mäppäys (The Workflow DAG approach) - Nykyisen Arkkitehtuurin Mukainen
V2:ssa jokaisella `Workflow.StepRule`:lla on `input_mappings`. Voimme määritellä Admin Studiossa solmun kytkennät tarkasti.
* **Toteutus:** Askeleelle, joka käyttää `Falsification` matriisia, liitetään input-mäppäykseen **vain** `$inputs.chat_history` (jättäen isot ref-dokumentit pois). Solmu, joka tekee asiatekstin laatutarkistusta, lukee vain `$inputs.document`.
* **Plussat:** Pysyy 100% V2 "De-Gererator" arkkitehtuurissa, jossa äly on kytkennöissä (Workflows), eikä matriiseissa. 
* **Miinukset:** Työkalurivien vetäminen (SDUI) voi tulla sekavaksi, kun askeleita on paljon ja eri matriisit vaatisivat teknisesti omat arviointisolmunsa. Samassa Askeleessa (solmussa) voi olla useita arviointikriteereitä, joten tekoälyn huomio jakautuu, jos kaadoimme koko laarin samaan kontekstiin.

#### Vaihtoehto B: Matriisikohtainen Kohdistus-suodatin (Target Scope in Matrix)
Lisätään `UniversalMatrix` tietomalliin uusi kenttä `target_scope: str | None`. Tämä on ohje LLM:lle: *"Kun lasket pisteen tähän matriisiin, painota yksinomaan kenttää X"*.
* **Toteutus:** `UniversalMatrix(target_scope="conversation_history")`. Prompt Compiler rakentaisi ohjeen: *"Huom: Arvioitaessa kriteeriä 'Kriittinen iteraatio', lue AINOASTAAN käyttäjän lähettämiä chat-viestejä"*.
* **Plussat:** Antaa täydellisen teoretisoidun tarkkuuden LLM:n Semantic Validatorille. Estää saastumisen muiden PDF-dokumenttien ohjeilla.
* **Miinukset:** Rikoimme "Palapeli"-konseptin hieman, jos Matriisi sisältää odotusarvoja siita, mitä dataa tulevaisuudessa joku Workflow ylipäätään sille tarjoaa.

#### Vaihtoehto C: Täydellinen Isolointi (Multi-Pass Validation)
Jokainen BARS-kriteeri (Matrix) ajetaan täytenä omana LLM-kutsunaan eristetyssä putkessa omalla kontekstillaan, jo ennen kuin mikään jatkolaskenta alkaa.
* **Toteutus:** Taustalla Worker pirstaloi työn 3LLM kutsuun.
* **Plussat:** Ehdottomasti parhaimmat BARS-arvosanat, 0 hallusinaatiota.
* **Miinukset:** Räjäyttää LLM token kustannukset x 3 ja moninkertaistaa odotusajan. Tähän järjestelmällä ei ole vielä suoraan kyvykkyyttä työnkulkujen kautta, ilman rankkaa rinnakkaista ajo-tukea.

### VAATIVA SUOSITUS: Yhdistelmä (Vaihtoehto A + Prompt-injektio)
Koska olemme V2-arkkitehtuurissa, **Työnkulun kytkennät (input_mappings) päättävät MITÄ dataa solmu ylipäätään näkee**. Mutta voimme rikastuttaa BARS-taulukon sisältöä *teoriakentällä*, joka auttaa mallia ymmärtämään sen kohteen. 
Esimerkki: `$inputs.chat_history` ohjautuu Bloomin synteesille ja `$inputs.document` asiakirjan tyyliarviointiin. Emme koodaa tätä matriiseihin, vaan työnkulun rakennuspalikkaan (JSON). Lisäämme kuitenkin matriisiin kuvaustekstin, jossa selviää *"Tämä mittari arvioi KÄYTTÄJÄN TOIMINTAA"*.

---

## 14. BARS-matriisien Deduplikointi ja Keskittäminen (Deduplication)

Vanhojen `steps`-pohjaisten migraatioiden ongelmana oli tiedon valtava toistuvuus: jokainen sub-task sisälsi oman versionsa Bloomin tai Toulminin arviointilogiikasta, johtaen sekaviin kopioihin, joissa `category_id` oli typistetysti vain "migrated_v1".

**Uusi Strategia (Deduplikointi):**
1. **Globaalit Singleton-Matriisit:** Tieteellisesti perustellut arviointimatriisit (esim. `matrix_bloom`, `matrix_toulmin`, `matrix_kahneman`, `matrix_goodhart`) luodaan tietokantaan vain **kerran** itsenäisinä V2 `PromptBlock` -entiteetteinä.
2. **Kategorisointi:** Niille asetetaan tarkat ja kuvaavat `category_id` -arvot (esim. `"scientific_theory"`, `"cognitive_evaluation"`) pelkän `"migrated_v1"` -jäänteen sijaan.
3. **Erilaistetut Kriteerit (Claims):** Jokaisen teorian BARS-skaalalle (MatrixScale) määritellään selkeästi yksilölliset, teoriaan nojaavat `claims`-lauseet eri pisteille (1-6 tai 1-5).
4. **Työnkulkujen Viittaukset:** Kun `migrate_v1_to_v2.py` rakentaa työnkulkuja (Workflows) GitHubin `seed_data.json` lähtödatasta, se tarkastelee askelten historiaa heuristisesti. Jos askel liittyy Toulminiin, skripti kytkee askeleen suoraan globaalin `matrix_toulmin` -matriisin `slug_id`:hen sen sijaan, että se kopioisi kriteerit työnkulun sisälle.

Tämä linjaa backendin täydellisesti *De-Generator* arkkitehtuurimandaatin tavoitteisiin (täydellinen uudelleenkäytettävyys, puhdas kanta).
