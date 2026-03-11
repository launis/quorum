# **ARKKITEHTUURIMÄÄRITTELY: Komponenttipohjainen AI-orkestraattori (Enterprise V2.5)**

Tämä dokumentti määrittelee dynaamisen, palvelinohjatun (SDUI) ja sataprosenttisesti auditoitavan tekoälyorkestraattorin arkkitehtuurin. Järjestelmä siirtää kaiken kognitiivisen liiketoimintalogiikan, datareitityksen, arvioinnin kalibroinnin ja käyttöliittymän piirtosäännöt tietokantaan, mikä mahdollistaa ominaisuuksien globaalin skaalaamisen välittömästi ilman koodipäivityksiä (Zero-Deploy).

## **1\. Arkkitehtuurin Ydinfilosofiat**

1. **Zero-Deploy, SDUI & Responsiivisuus:** Käyttöliittymä ja tulostemoottorit ovat liiketoimintalogiikasta tietämättömiä renderöijiä. Kaikki syötevaatimukset, arviointikriteerit, tekoälymallit ja käyttöliittymäkomponentit konfiguroidaan tietokannassa. Käyttöliittymä on täysin dynaaminen, responsiivinen ja mukautuu automaattisesti kaikille laitteille (mobiili, tabletti, desktop).  
2. **Reaktiivinen Tilanhallinta (Riverpod):** Koko käyttöliittymän tilanhallinta ja asynkroniset datavirrat rakennetaan Riverpodilla uusimpien best practice \-mallien mukaisesti (Notifier / AsyncNotifier).  
3. **Schema-Driven AI (Dynaaminen Pydantic):** Tekoälyltä ei koskaan pyydetä tulosteen muotoa vapaassa tekstissä. Tulostevaatimukset käännetään lennosta validointiluokiksi, joista generoituu OpenAPI JSON Schema. LLM pakotetaan vastaamaan tähän tiukkaan rakenteeseen API-tasolla (`Structured Outputs`).  
4. **Universaali Mittausarkkitehtuuri ("PromptBlocks"):** Vapaamuotoiset laadulliset analyysit, numeeriset/desimaaliset mittaristot ja ohjeistukset yhdistetään yhdeksi "PromptBlock" \-tietokantamalliksi. Tämä poistaa siilot ja automatisoi LLM-ohjeistuksen erillisten taulujen välillä.  
5. **Arvioinnin Dynaaminen Kalibrointi (Model Strategy):** Järjestelmä erottaa kognitiiviset intentiot (`fast`, `deep`, `precise`) fyysisistä malleista (`gemini-2.5-pro`). Tämä tapahtuu globaalissa `system_config` rekisterissä.
6. **Teoriamaadoitettu XAI (Grounded Explainable AI):** Arviointimatriiseihin tallennetaan aina teorialähde (URL) sekä virallinen lähdeviite. Järjestelmä hakee lähteen ja syöttää sen tekoälylle *ennen* arviointia.
7. **Dynaaminen Datan Reititys (Semantic Data Flow):** Työnkulkuun tulevan datan määrä ja rooli ovat täysin dynaamisia. Askeleet muodostavat suunnatun syklittömän verkon (DAG), jossa data reititetään nimenomaisilla `$inputs.` tai `$steps.` muuttujilla.
8. **Kognitiivinen Monikielisyys (I18n Fallback):** Järjestelmä on natiivisti monikielinen ja tukee dynaamista käännösten hakua automaattisella varakieleen putoamisella.
9. **Ikuinen Auditoitavuus (Append-Only & Snapshotting):** Mitään kognitiivista palikkaa ei koskaan ylikirjoiteta ajon aikana. Historialliset ajot jäädyttävät suoritushetken absoluuttisen tilan fyysisenä syväkopiona (`frozen_context`).  
10. **Single Source of Truth (Domain Service Layer):** API-reitittimet ovat rakenteellisesti aneemisia ja vastaavat vain HTTP-pyyntöjen (Pydantic) parsinnasta. Kaikki tietokantaintegraatiot ja Tenant-eristys tapahtuvat pakotetusti eristetyssä Service-kerroksessa (esim. `StudioService`, `ExecutionService`).

## ---

## **2\. Kognitiivinen Monikielisyys (I18n Fallback)**

Järjestelmä tukee globaalia monikielisyyttä joustavasti ilman, että kääntäminen on käyttäjälle pakollista. Kaikki tietokannan tekstit tallennetaan I18n JSON-objekteina:

```json
"instruction": {  
  "default_locale": "fi",  
  "translations": {  
    "fi": "Arvioi innovaatiotaso teoriaan tukeutuen.",  
    "en": "Evaluate the innovation level based on the theory."  
  }  
}
```

UI päättelee target_localen ja poimii joko käännöksen tai oletuksen dynaamisesti (SafeCast).

## ---

## **3\. Tietokantamalli (NoSQL Document DB)**

Tietokanta on suunniteltu Firestoren varaan tuotannossa ja lokaalin `db_v2.json` varaan kehityksessä. 

## **KERROS 1: KIRJASTOT (Peruspalikat)**

* **system_configs (Globaali rekisteri):** Singleton-kokoelma, joka mapittaa kognitiiviset strategiat (fast, deep, strict) fyysisiin LLM-malleihin erillään agenteista.

## **KERROS 2: ORKESTRAATIO (Äly ja Työnkulut)**

* **prompt_blocks (Ohjeet ja Kriteerit):**  
  Sisältää KAIKKI kognitiiviset ohjeet, säännöt, otsikot ja numeeriset arvioinnit (`type`: `instruction`, `matrix`, `hook`, `generator`).
* **steps (Task Blueprints):** Sitovat tietyn abstraktin ohjeen (`prompt_block`) tiettyyn kognitiiviseen strategiaan (`model_strategy`) tehden niistä uudelleenkäytettäviä palikoita verkolle.
* **workflows (DAG-Työnkulut):** Määrittelee dynaamiset syötteet (`expected_inputs`) ja luovat askeleiden välisen riippuvuustaulukon (`depends_on`) sekä datareitityksen (`input_mappings`).

## **KERROS 3: HISTORIA JA AUDITOINTI**

* **executions (Ikuinen Jäädytys):**  
  * `raw_inputs`: Käyttäjän lataamat syötteet.  
  * `frozen_context`: Täydellinen, muuttumaton syväkopio käännetyistä ohjeista askelepohjaisesti ajon hetkellä.  
  * `results`: Backendin Pydantic-validoima, askeleittain jaoteltu tulos-JSON.

## ---

## **4\. Syötteet, Roolit ja Datan Reititys (Semantic Data Flow)**

Järjestelmä ei sisällä kovakoodattua vaatimusta pelkästä "keskusteluhistoriasta". Työnkulku itse määrittelee dynaamisesti, mitä dataa tarvitaan ja mikä sen kognitiivinen rooli on.

## **4.1. Odotetut syötteet (Expected Inputs) ja Universaali Reititys**
`workflows`-dokumentissa on `expected_inputs`-taulukko (Esim. `{"chat_log": "file", "reflection_text": "file"}`). Käyttöliittymä lukee tämän lennosta ja piirtää vaadittujen kenttien Upload/Text-alueet. Mukaansa jokainen syöte ottaa `ai_description`-kentän (esim. "Tämä on Sitran raportti"). `input_processing.py`-hook injektoi tämän kuvauksen suoraan raakadatan yläpuolelle (Universal Routing), jolloin jokainen Pydantic-agentti ymmärtää datan kontekstin ilman, että ohjeita tarvitsee kovakoodata agenteille!

## **4.2. Routing Variables ($)**
DAG-verkossa jokaisella askeleella (`step_node_1`) on `input_mappings`-määritys:
1. **Globaalit syötteet (`$inputs.chat_log`):** Käyttäjän antamat tiedostot/tekstit.  
2. **Aiempien askeleiden tulokset (`$steps.step_node_1.output.risk_score`):** Yksittäiseen Pydantic-tulosavun alikenttään viittaava osoitin.

Tällä taataan, että jokainen Node suoritetaan turvallisessa Pydantic eristyksessä (Fail-Fast), eikä data lipsu vahingossa väärien LLM-kutsujen kontekstiin.

## ---

## **5\. FastAPI Backend ja Suoritusmoottori**

Backend (`backend_v2`) on dynaaminen Compiler-moottori, joka ratkaisee DAG-graafin, ajaa askeleet rinnakkain ja suorittaa Pydantic-validoinnin raskaasti tiukalla `extra="ignore"` säännöllä estääkseen LLM hallusinaatiot.

## **5.1. Pydantic SSOT (Strict-DTO Protocol)**
Aivan jokainen työnkulku kulkee tiukan Pydantic `v2_core.py` (Määritelmät) ja `execution.py` (Suoritus) suodattimen läpi. Jos databaseen tallennettu tietue riitelee skeeman kanssa, kutsu katkeaa välittömästi HTTP 422 tai 500 virheeseen poikkeuksetta (Fail Fast).

## **5.2. Teoriamaadoitus ja RAG (System Prompt)**
Jos `prompt_block` kriteerissä on `theory_grounding.source_url`, Web Fetcher tai dokumentin lukija (RAG) hakee lähteen. Teksti injektoidaan Promptiin tiukkoihin XML-tageihin `<theory_context>`, ja malli pakotetaan reitittämään vastauksensa Pydantic json schemaan niin, että vastaus sisältää numeerisen arvon ja tarkan lainauksen kirjasta.

## **5.3. Hook-Riippuvuuksien Ruiskutus (Dependency Injection)**
Kaikki tietokanta- ja LLM-yhteydet ruiskutetaan suoraan FastAPIn `Depends` injektiosta Service-kerrokselle. Reititin (Controller) on aneeminen, mikä mahdollistaa äärimmäisen kattavan ja turvallisen Unit-Testauksen MockDB:llä ilman HTTP mokkauksia.

## **5.4. Dual-Reporting (RFC 7807)**
Frontend API rajapinnoissa virheet hoidetaan aina **RFC 7807** hengessä: 
1. Exception napataan
2. Tulostetaan `logger.error` backend lokeihin kehittäjille teknisen poikkeuksen kera.
3. Nostetaan ulospäin asiallinen JSON, joka sisältää koneluettavan enumin (Esim. `VALIDATION_FAILED`), estäen koodin pinojen ja salaisuuksien vuotamisen asiakkaalle.

## ---

## **6\. Esityskerros (Adaptive SDUI - Flutter)**

Frontend (`client_app_v2`) on "tyhmä" renderöintimoottori, joka on suunniteltu äärimmäisen mukautuvaksi, dynaamiseksi ja reaktiiviseksi.

1. **Riverpod ja Koodigeneroitu Reaktiivisuus:** Sovelluksen tilanhallinta ja datavirrat rakentuvat **Riverpod 3.0** (Notifier, AsyncNotifier) varaan hyödyntäen vahvasti koodigenerointia (`@riverpod`). Tämä turvaa tilojen luonnollisen päivityssyklin ilman manuaalista boilerplatea ja kieltää `ChangeNotifier` -käytöt kokonaan.  
2. **Hybridiparillinen Datanhallinta (Freezed vs. SafeCast):** 
   * Kaikki ydintila, navigointireitit (`go_router_builder`) ja staattiset rajapintavastaukset parsitaan ehdottoman tyyppiturvallisesti käyttäen `freezed` ja `json_serializable` koodigeneraattoreita. Tämä ylläpitää Pydantic-tason tyyppiturvallisuutta API-rajapinnassa.
   * Kuitenkin, kun käsitellään taaksepäin yhteensopimattomia tai erittäin dynaamisia SDUI-määrityksiä (kuten tietokannan vanhoja `prompt_blocks` tai renderöintivihjeitä), järjestelmä nojaa **defensiiviseen parsintaan** (`SafeCast`-luokka). Tämä estää Flutter-sovelluksen täydellisen kaatumisen (Red Screen of Death) yhden väärintypitetyn avaimen takia luottamattomassa datassa.
3. **Compound Widgets (Grounded UI):** Koska ohjeet ja arvioinnit on yhdistetty `PromptBlock` muotoon, UI rakentaa lennosta komponentteja, joissa arviointislaideri, LLM-perustelu, teoria-citaatio ja ohjetekstit sidotaan visuaalisesti jäännöksettömäksi kokonaisuudeksi, yhden renderöintisyklin sisällä.