# EPIC: Vertex Search Re-Integration & Architecture Alignment (V2)

> [!IMPORTANT]
> **TÄRKEÄÄ: HAKUARKKITEHTUURIN TOTEUTUSTAPA (VÄLIAIKAINEN "VANHA TAPA")** 
> Tämä Epic keskittyy ns. **vanhan tavan** (Output Extensions + Pydantic Post-Hook) palauttamiseen. Vaikka ylätason tavoite on siirtyä arkkitehtuurimäärittelyn (V2.6) asettamaan moderniin agenttiseen MCP Tool Loop -malliin tulevaisuudessa, teemme tämän ominaisuuden tässä dokumentissa peräkkäisyyttä ja Output Extensionseja käyttämällä (Pipeline).
> Tässä mallissa **Search** toimii tiukasti ulkoistettuna osana:
> 1. LLM tekee työnsä askeleen puitteissa ja muodostaa JSON-tulosteeseen oman `search_query` -hakusanan, päättäen samalla suorituksensa.
> 2. Kognition ulkopuolinen **Search Hook** (`search.py`) aktivoituu fyysisen askeleen jälkeen, poimii the sanan ajonaikaisesta datasta (`state.inputs`), hakee Internetistä dataa ajon *ulkopuolella* ja sementoi löydetyt faktat.
> 3. Nämä tulokset siirretään verkon (DAG) the **seuraavalle** agentille viestikapulana. Alkuperäinen kysyjä ei tässä vanhassa mallissa asetu jatkokeskusteluun tai lue hakutuloksia omassa solmussaan.

## 1. Tausta ja Yleinen Informaatio (Background & Context)
**Vertex Search (Google Grounding)** on kriittinen mekanismi Quorum-alustan luotettavuuden ja *Empiirisen XAI (Explainable AI)* -arkkitehtuurin takaamiseksi. Se on Enterprise-tason ominaisuus, jonka avulla (Post-hook putken muodossa) voidaan hakea reaaliaikaisesti faktoja ja lähteitä avoimesta internetistä (Google Search) ja maadoittaa the tulokset todellisiin URL-lähteisiin. Ilman Vertex-maadoitusta kielimalli nojaa puhtaasti staattiseen koulutusdataansa, jolloin se on altis tuottamaan hallusinaatioita tutkiessaan käyttäjien aineistoja. Grounding varmistaa, että järjestelmän vastaukset ovat objektiivisesti todennettavissa.

### 1.1. Miten "Output Extensions" ja Search Hook toimivat yhdessä (Peräkkäinen Vanha Malli)?
Quorum V2 -arkkitehtuurissa tekoälyn analyysitehtävät eristetään suorista reaktiivisista työkalukutsuista käyttämällä tässä väliaikaisessa Tapa 1 -protokollassa dynaamisia **Output Extensions** -laajennoksia ja peräkkäisiä **Post-Hookeja**. Kuten varoituksessa on mainittu, haku on tiukasti peräkkäinen ja katkaistu:
1. **Dynaaminen Schema Inject (Output Extension):** Kun työnkulkustrategia (esim. aktiivinen *Kokonaisvaltainen Auditointi*) määrittelee `steprule`-solmulle laajennoksen (`output_extensions: ["search_query"]`), V2:n Pydantic-moottori rakentaa tekoälymallille lennossa käskyn (Structured Outputs JSON Schema) tuottaa varsinaisen analyysinsa lisäksi oma, erillinen JSON-avain `"search_query"` (esim. *"KHO ennakkopäätös 2026 sähköverkko"*).
2. **Search Hookin Sieppaus ja Suorite:** Askeleen elinkaareen asennettu ohjelmistotason suodatin, asynkroninen **Search Hook** (`search.py`), aktivoituu suorituksen jälkeisenä hetkenä (The Tool Loop). Se etsii (`state.inputs` -dataobjektista) LLM:n generoimaa `search_query` -avainta.
3. **Faktamaadoitus (Grounding):** Jos hakusana löytyy, Hook tekee pyynnön Google Vertex AI -rajapintaan, noutaa ajantasaiset internet-linkit ja tekstikatkelmat (snippets), ja injektoi nämä lähteet laadulliseksi näytöksi eteenpäin työnkulun verkon seuraavalle tekoälysolmulle ("Grounded XAI") ja maadoittaa ne lisäksi muuttumattomaan `FrozenContext` -muistiin.

Tämä suunnittelumalli tekee hausta täysin dynaamisen ominaisuuden, jonka voi asentaa työnkulun mille tahansa yksittäiselle askeleelle puhtaalla tietokanta-ajolla (*Semantic Data Flow*) ilman backend-koodin muutoksia (Zero-Deploy).

## 2. Ongelman Yhteenveto (Problem Summary)
Vertex Search ei tällä hetkellä aktivoidu "De-Generator" (V2) -työnkuluissa (kuten aktiivisessa "Kokonaisvaltainen Auditointi" -työnkulussa), vaikka ympäristömuuttujat (`ENABLE_VERTEX_SEARCH`, `GOOGLE_CLOUD_PROJECT`) ovat kunnossa. Tämä johtuu kahdesta juurisyystä:
1. **Arkkitehtuurikuilu:** Haun koodi (`search.py`) on riippuvainen `step_analyst`-koneen tuottamista hakusanoista, mutta modernit asiantuntijaverkostot (esim. `steprule_falsifier`) eivät työnkuluissa tuota näitä. Hooksien kytkentä ei siksi tuota hakusanoja haettavaksi, ohittaen haun äänettömästi ("Fail-Fast").
2. **Kieliristiriita (Schema Mismatch):** Vanhat dokumentaatiot ja vanhat kehotteet vaativat LLM:ää tuottamaan suomenkieliset JSON-Pydantic-avaimet ("hypoteesit", "hakusana_ehdotus"), kun taas Python-koodin skanneri etsii englanniksi "hypotheses" ja "search_query".

## 3. Tavoitteet (Objectives)
- Palauttaa Vertex Search -faktantarkistus saumattomaksi ja varmatoimiseksi (100% On-Target) osaksi Quorumin V2-työnkulkuja.
- Yhtenäistää JSON/Pydantic-skeemat (suomi vs englanti) siten, että koodi ja LLM-säännöt puhuvat samaa Output Extensions -kieltä.

## 4. Vaiheet (Milestones & Execution Plan)

### Vaihe 1: Pydantic-skeemojen ja Sääntöjen Yhtenäistäminen
- **Kuvaus:** Koodin ja LLM:n välinen kommunikaatio on standardoitava. V2-arkkitehtuurin (De-Generator) mukaisesti kaikessa sisäisessä tietorakenteessa tulee käyttää englanninkielistä "Output Extension" -avainta `search_query` tai `hypotheses`. 
- **Toimenpide:** Varmistetaan `analyst.py` -skeeman Pydantic-avaimet ja korjataan mahdolliset virheelliset `seed_data.json` Prompt-lohkot, jotta kielimalli ohjeistetaan tuottamaan englanninkieliset avaimet suomen sijaan.

### Vaihe 2: Search Hookin (`execute_google_search`) refaktorointi & Tietoturva
- **Kuvaus:** Hook eristetään `step_analyst` -kovakoodauksesta ja integroidaan dynaamisempaan V2-arkkitehtuuriin.
- **Toimenpide:** Muutetaan `search.py` iteroiduksi. Sen ei tulisi etsiä hakusanoja vain `step_analyst` -nimisestä paikasta, vaan laajemmin `state.inputs` -dataobjektista dynaamisesti niistä askeleista, joissa haku suoritetaan.
  - **Sanitisaatio ja Tietoturva:** Ennen Vertex-rajapintaa kaikki generoidut hakusanat sanitoidaan (esim. pituusrajoitukset, prompt injection -yritysten suodatus) tietoturvariskien ja turhien API-kulujen hallitsemiseksi.
  - **Välimuisti (Caching) ja Suorituskyky:** Harkitaan välimuistimekanismin (esim. Redis tai in-memory cache) lisäämistä. Jos sama `search_query` esiintyy työnkulussa uudelleen, tulos palautetaan suoraan välimuistista.

### Vaihe 3: Ajokohtainen Hakuloki, Virheenkäsittely ja Telemetria
- **Kuvaus:** Vianetsinnän ja läpinäkyvyyden parantamiseksi jokaisen ajon haut dokumentoidaan pysyvästi (XAI - Empiirinen maadoitus / `FrozenContext`) standardia tallennusrajapintaa käyttäen. Myös työnkulun käyttäytyminen poikkeustilanteissa määritellään tarkasti.
- **Toimenpide:** `search.py` -hookkia laajennetaan tallentamaan ajokohtainen hakuloki kohdekansioon `executions/<execution_id>/` hyödyntäen standardia tallennusrajapintaa (`backend_v2.services.storage` / `FileDriver`). Lokiin kirjataan tarkasti luodut hakusanat, Vertex-rajapinnan palauttamat virheet ja varoitukset. Standardin tapahtumalokin ohella kehitetään seuraavat lisäominaisuudet:
  - **Virheenkäsittely & Fallback-mekanismit:** Määritellään eksplisiittisesti, miten työnkulku reagoi API-katkoihin tai kiintiöiden ylityksiin (esim. sovelletaanko Fail-Fast -mandaattia työnkulun keskeyttämiseksi, vai jatketaanko suoritusta varoituksen kera).
  - **Telemetria ja Metriikat:** Hookin tulee rakenteellisen lokituksen lisäksi kerätä metriikkaa hakujen kestosta (latenssi) ja onnistumisprosentista `backend_debug.log` -tietueeseen pidemmän aikavälin järjestelmäseurantaa varten.

### Vaihe 4: Työnkulkujen Seed-datan Päivitys
- **Kuvaus:** Päivitetään ainoa tällä hetkellä aktiivinen työnkulku, **"Kokonaisvaltainen Auditointi"** (`wf_d653170e174847559e08af42b938d826`), siten, että se pakottaa LLM:n oikeasti generoimaan hakusanoja tarvittaessa joko lisäämällä erillinen Fact-Checking -välivaihe tai liittämällä tiettyihin `steprule`-koneisiin oikeat `output_extensions` ("search_query").
- **Toimenpide:** Edelliset muutokset tallennetaan puhtaana JSON-datana `seed_data.json` puitteissa ja luodaan validi V2 tietokantaseed. Päivityksessä noudatetaan tiukkaa *Configuration Backup Protocol* -käytäntöä: varmistetaan datan versiointi siten, että mahdollisessa vikatilanteessa kanta voidaan asettaa aiempaan työtilaan vaivattomasti (Rollback).

### Vaihe 5: Laadunvarmistus (QA) ja Automaatiotestaus
- **Kuvaus:** Estetään jatkossa hiljaiset virheet ajamalla korjattu **"Kokonaisvaltainen Auditointi"** -työnkulku, sekä tuetaan koodimuutoksia vahvalla automaatiotestauksella.
- **Toimenpide:**
  - **Automaattitestaus:** Kirjoitetaan yksikkö- ja integraatiotestit (esim. `pytest`) refaktoroidulle Search Hookille, telemetria/välimuistimekanismille ja dynaamisesti luoduille Pydantic-skeemoille regressioiden estämiseksi tulevaisuudessa.
  - **Manuaalinen QA:** Todennetaan `backend_debug.log`:sta, että `[SearchHook]`-kutsut menevät läpi Vertex AI:lle (ja että telemetria kirjautuu) ilman hiljaista "No queries" -ohitusta. Koskien API:n palauttamaa XAI-dataa (Grounded Explainable AI), UI:sta varmistetaan, että asiantuntija-agentit todella näkevät löydetyt google-linkit ja hyödyntävät niitä osana kognitiivista päättelyään ("Ei hakutuloksia" -tekstin sijaan).

---
*Tämä Epic noudattaa Quorumin V2.33 Zero-Compromise Pledgesiä.*
