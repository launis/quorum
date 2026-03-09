# **ARKKITEHTUURIMÄÄRITTELY: Komponenttipohjainen AI-orkestraattori (Enterprise V2)**

Tämä dokumentti määrittelee dynaamisen, palvelinohjatun (SDUI) ja sataprosenttisesti auditoitavan tekoälyorkestraattorin arkkitehtuurin. Järjestelmä siirtää kaiken kognitiivisen liiketoimintalogiikan, datareitityksen, arvioinnin kalibroinnin ja käyttöliittymän piirtosäännöt tietokantaan, mikä mahdollistaa ominaisuuksien globaalin skaalaamisen välittömästi ilman koodipäivityksiä (Zero-Deploy).

## **1\. Arkkitehtuurin Ydinfilosofiat**

1. **Zero-Deploy, SDUI & Responsiivisuus:** Käyttöliittymä ja tulostemoottorit ovat liiketoimintalogiikasta tietämättömiä renderöijiä. Kaikki syötevaatimukset, arviointikriteerit, tekoälymallit ja käyttöliittymäkomponentit konfiguroidaan tietokannassa. Käyttöliittymä on täysin dynaaminen, responsiivinen ja mukautuu automaattisesti kaikille laitteille (mobiili, tabletti, desktop).  
2. **Reaktiivinen Tilanhallinta (Riverpod):** Koko käyttöliittymän tilanhallinta ja asynkroniset datavirrat rakennetaan Riverpodilla uusimpien best practice \-mallien mukaisesti (Notifier / AsyncNotifier).  
3. **Schema-Driven AI (Dynaaminen Pydantic):** Tekoälyltä ei koskaan pyydetä tulosteen muotoa vapaassa tekstissä. Tulostevaatimukset käännetään lennosta validointiluokiksi, joista generoituu OpenAPI JSON Schema. LLM pakotetaan vastaamaan tähän tiukkaan rakenteeseen API-tasolla.  
4. **Universaali Mittausarkkitehtuuri ("Kaikki on Matriiseja"):** Vapaamuotoiset laadulliset analyysit ja numeeriset/desimaaliset mittaristot yhdistetään yhdeksi "Universaali Matriisi" \-tietokantamalliksi. Tämä poistaa siilot ja automatisoi LLM-ohjeistuksen sekä API-skeemojen luonnin.  
5. **Arvioinnin Dynaaminen Kalibrointi (Tiukkuus 0–100):** Jokaiseen arviointimatriisiin on sisäänrakennettu matemaattinen tiukkuus/armollisuus-parametri (0–100). Arvo 0 pakottaa tekoälyn antamaan aina maksimiarvosanan (esim. 6), kun taas 100 pakottaa antamaan aina minimiarvosanan (esim. 1). Järjestelmä muuntaa tämän arvon dynaamisesti semanttiseksi prompt-injektioksi, joka kalibroi tekoälyn kognitiivisen asenteen lennosta.  
6. **Teoriamaadoitettu XAI (Grounded Explainable AI):** Arviointimatriiseihin tallennetaan aina teorialähde (URL) sekä virallinen lähdeviite. Järjestelmä hakee lähteen ja syöttää sen tekoälylle *ennen* arviointia. Tekoäly pakotetaan antamaan numeerinen arvo/desimaali sekä monikielinen perustelu nimenomaisesti kyseiseen lähteeseen tukeutuen.  
7. **Dynaaminen Datan Reititys (Semantic Data Flow):** Työnkulkuun tulevan datan määrä ja rooli ovat täysin dynaamisia. Järjestelmä reitittää alkuperäiset tiedostot ja aiempien agenttien tuotokset seuraaville agenteille XML-eristettyinä, semanttisina rooleina.  
8. **Kognitiivinen Monikielisyys (I18n Fallback):** Järjestelmä on natiivisti monikielinen ja tukee dynaamista käännösten hakua automaattisella varakieleen putoamisella, yhdistettynä LLM-tason tiukkaan kohdekielen pakotukseen.  
9. **Ikuinen Auditoitavuus (Append-Only & Snapshotting):** Mitään kognitiivista palikkaa ei koskaan ylikirjoiteta. Historialliset ajot jäädyttävät suoritushetken absoluuttisen tilan fyysisenä syväkopiona (frozen\_context).  
10. **Viivästetty Esityseristys (Late-Binding Omni-Channel):** Datan prosessointi pidetään yhtenäisenä, alustariippumattomana JSON-rakenteena prosessin loppuun asti. Vasta aivan viimeisessä adapterikerroksessa data purkautuu kolmeen formaattiin: interaktiiviseksi näyttöliittymäksi (Flutter), visuaaliseksi PDF-dokumentiksi tai yksiriviseksi litteäksi vientitiedostoksi (Flat File).
11. **Single Source of Truth (Domain Service Layer):** API-reitittimet ovat rakenteellisesti aneemisia ja vastaavat vain HTTP-pyyntöjen (Pydantic) parsinnasta. Kaikki tietokantaintegraatiot, luvitus, roolisuojaukset (RBAC) ja Tenant-eristys tapahtuvat pakotetusti eristetyssä Service-kerroksessa (esim. `AuthService`, `ExecutionService`). Tämä estää turvallisuusvuodot, kun tausta-ajoja tai agentteja suoritetaan ohjelmallisesti ilman selainta.

## ---

**2\. Kognitiivinen Monikielisyys (I18n Fallback)**

Järjestelmä tukee globaalia monikielisyyttä joustavasti ilman, että kääntäminen on käyttäjälle pakollista. Yleiset "Best Practice" \-työnkulut voivat sisältää asiantuntijoiden käännökset, mutta käyttäjän omat, lokaalit työnkulut voivat olla täysin yksikielisiä.

## **2.1. Datan rakenne**

Kaikki tietokannan tekstit (ohjeet, säännöt, ankkurit, UI-otsikot) tallennetaan I18n JSON-objekteina:

JSON

"instruction": {  
  "default\_locale": "fi",  
  "translations": {  
    "fi": "Arvioi innovaatiotaso teoriaan tukeutuen.",  
    "en": "Evaluate the innovation level based on the theory."  
  }  
}

## **2.2. Kääntäjän Fallback-logiikka ja LLM Pakotus**

1. **Fallback-haku:** Ajoa käynnistettäessä API vastaanottaa parametrin target\_locale (UI:n kieli). Prompt Compiler etsii komponentista tätä käännöstä. Jos sitä ei löydy, algoritmi putoaa turvallisesti komponentin default\_locale \-kieleen.  
2. **Kielen yliajo (Critical Mandate):** Koska promptissa voi tämän myötä olla sekaisin eri kieliä, kääntäjä injektoi System Promptin loppuun ehdottoman systeemimandaatin:  
   *"CRITICAL MANDATE: You must process the input and generate all your output text, reasoning, and source justifications exclusively in the {target\_locale} language, regardless of the language used in the instructions or source materials."*

## ---

**3\. Tietokantamalli (NoSQL Document DB)**

Tietokanta on jaettu kolmeen loogiseen kerrokseen. Kokoelmat hyödyntävät Append-Only \-mallia: jokaisella dokumentilla on looginen perhe (slug) ja muuttumaton fyysinen versio (\_id muodossa \_vX).

## **KERROS 1: KIRJASTOT (Peruspalikat)**

* **data_dictionary (Sanakirja):** Määrittelee datatyypit, semanttiset roolit ja UI-vihjeet asioille, jotka EIVÄT ole matriiseja (esim. syötetiedostot, vapaat tekstitulosteet).  
* **dimensions (Käsitteet)::** Luettelo asioista, joita ylipäätään mitataan (esim. dim_bloom).  
* **system_configs (Globaali rekisteri):** Singleton-kokoelma, joka mapittaa kognitiiviset strategiat (fast, deep, strict jne.) fyysisiin LLM-malleihin erillään agenteista.

## **KERROS 2: ORKESTRAATIO (Äly ja Työnkulut)**

* **matrices (PromptBlocks / Yhdistetty Rakennepalikkataulu):**  
  Sisältää KAIKKI kognitiiviset ohjeet, säännöt, otsikot ja numeeriset arvioinnit. Puhtaat tekstiohjeet merkitään arvolla `type: "instruction"`, jolloin Pydantic-kääntäjä ei odota tekoälyltä niihin tulostetta. Yhdistää numeeriset ja laadulliset arvioinnit, kireysindeksin sekä teorian.  
  JSON  
  {  
    "dimension\_slug": "bloom\_score",   
    "type": "float",   
    "allow\_decimals": true,  
    "strictness\_level": 85, // 0 \= Maksimi armollisuus, 100 \= Maksimi kireys  
    "require\_justification": true,  
    "theory\_grounding": {  
      "source\_url": "https://esimerkki.fi/bloom-teoria",  
      "citation\_reference": "Bloom, B. S. (1956). Taxonomy of Educational Objectives."  
    },  
    "scale": { "min": 1.0, "max": 6.0 },  
    "instruction": { "default\_locale": "fi", "translations": {"fi": "Arvioi taso peilaten teoriaan."} },  
    "ui_hints": { "widget": "slider" }  
  }

* **output_schemas (Tulostepohjat):** Lista viittauksia Sanakirjaan asioista, joita LLM:ltä halutaan matriisin lisäksi.  
* **output_configs (Esitysmallit):** Määrittelee dynaamisesti (SDUI), miten tuloksista kootaan loppukäyttäjän Dashboard/PDF. Poistaa koodattujen ReportTransformerien tarpeen.
* **workflows (DAG-Työnkulut):** Määrittelee dynaamiset syötteet (expected_inputs), askeleet (steps), niiden välisen riippuvuustaulukon (depends_on) ja datareitityksen (input_mappings). *Kognitiivisia agentteja ei tunneta askeleiden ulkopuolella; askel "on Tuomari", jos sille on kytketty Tuomarin matriisit (slugit).*

## **KERROS 3: HISTORIA JA AUDITOINTI**

* **executions (Ikuinen Jäädytys):**  
  * raw\_inputs: Käyttäjän lataamat syötteet rooleittain.  
  * **frozen\_context**: Täydellinen, muuttumaton syväkopio käännetyistä ohjeista, noudetuista teorioista, kireysindekseistä ja JSON-skeemoista ajon hetkellä.  
  * results: Backendin Pydantic-validoima, askeleittain jaoteltu tulos-JSON.

## ---

**4\. Syötteet, Roolit ja Datan Reititys (Semantic Data Flow)**

Järjestelmä ei sisällä kovakoodattua vaatimusta pelkästä "keskusteluhistoriasta". Työnkulku itse määrittelee dynaamisesti, mitä dataa tarvitaan ja mikä sen kognitiivinen rooli on.

## **4.1. Odotetut syötteet (Expected Inputs)**

workflows-dokumentissa on expected\_inputs \-taulukko. Käyttöliittymä lukee tämän lennosta ja piirtää sen perusteella automaattisesti responsiiviset tiedostonlataus- ja tekstikentät.

## **4.2. Askeleiden välinen datareititys (Step-to-Step Routing)**

DAG-verkossa (Suunnattu asyklinen verkko) jokaisella askeleella (step) on input\_mappings-määritys. Se kertoo Kääntäjälle, mistä agentti saa datansa:

1. **Globaalit syötteet ($inputs):** Käyttäjän antamat alkuperäiset tiedostot.  
2. **Aiempien askeleiden tulokset ($steps.step_n.output.x):** Ketjutus, jossa aiemman askeleen JSON-tulos syötetään suoraan seuraavalle työnkulun askeleelle, luoden aidon vuovaikutteisen arviointiketjun vapaasti konfiguroitavissa rooleissa.

## **4.3. Y-Funnel: Deterministiset Hookit vs. Kognitiiviset Askeleet**

Järjestelmä jakaa viestinnän kahteen kategoriaan Worker-tasolla:
1. **Pre-Hooks (PrepService):** Säännöpohjaiset konversiot (esim. Base64 PDF de-koodaus V1-rakenteesta tai Markdown-sanitointi). Nämä tallennetaan suoraan `$inputs.historia`-muotoon.
2. **Kognitiivinen Työnkulku:** LLM-operaatiot, joilla aiemmin siistittiin chat-lokeja, tehdään nyt normaaleina `DAG Nodeina` työnkulun alussa (esim. askel `step_chat_parsing`), joista seuraavat askeleet hakevat datansa dynaamisesti. Koodattuja Pre-Processoreita agenttiluokissa ei enää sallita.

## **4.4. Roolien vaikutus kääntäjässä (XML-injektio)**

Datan semanttisella roolilla on valtava merkitys LLM:n ohjauksessa. Prompt Compiler lukee input\_mappings \-avaimet ja käärii datan automaattisesti roolia vastaaviin XML-tageihin (esim. \<target\_conversation\>, \<analyst\_insights\>). Tämä estää prompt-injektiot ja auttaa tekoälyä erottamaan arvioitavan tekstin muilta agenteilta saadusta tukimateriaalista.

## ---

**5\. Kääntäjä ja Suoritusmoottori (FastAPI Backend)**

Backend on dynaaminen Compiler-moottori, joka ratkaisee DAG-graafin (depends\_on), ajaa askeleet rinnakkain (asyncio.gather) ja suorittaa turvalliset Python Hookit muistista.

## **5.1. Teoriamaadoitus ja RAG (System Prompt)**

Jos kriteerissä on theory\_grounding.source\_url, Web Fetcher hakee lähteen asynkronisesti. Teksti injektoidaan System Promptiin XML-tageilla:

\<theory\_context dimension="bloom\_score" citation="Bloom (1956)..."\> \[TEKSTI LÄHTEESTÄ\] \</theory\_context\>.

## **5.2. Arvioinnin Kalibrointi (Tiukkuus/Armollisuus)**

Kääntäjä lukee matriisin kriteeristä arvon strictness\_level (0-100) ja muuntaa sen dynaamisesti kognitiiviseksi matemaattiseksi ohjeeksi System Promptiin.

* *Algoritmiesimerkki Prompt Compilerin muodostamasta säännöstä (Skaalalla 1-6):*  
  * 0: *"CRITICAL MANDATE: Absolute Leniency (0/100). You must be extremely forgiving. Assign the maximum possible score (6) to every evaluation, unless the input is entirely missing or completely irrelevant."*  
  * 50: *"EVALUATION MANDATE: Neutral and objective evaluation (50/100). Use the full scale fairly based on the criteria."*  
  * 100: *"CRITICAL MANDATE: Absolute Strictness (100/100). You must be extremely strict and highly critical. Assign the minimum possible score (1) to every evaluation, penalizing even the smallest flaws. Only indisputable absolute perfection can score higher."*

## **5.3. Dynaaminen Pydantic & Pakotettu Perustelu**

Tekoälyn muoto pakotetaan luomalla lennosta pydantic.create\_model \-funktiolla OpenAPI JSON Schema.

* Jos kriteerissä on require\_justification: true, malliin generoidaan arvo-kentän lisäksi kaksi tekstikenttää: {dimension\_slug}\_justification ja {dimension\_slug}\_citation.  
* LLM ohjeistetaan: *"Anna arvo (sallien desimaalit). Perustele arvo yksityiskohtaisesti \<theory\_context\> \-lähteeseen tukeutuen ja aseta tarkka lähdeviite citation-kenttään."*

## **5.4. Jäädytys ja Suoritus**

Generoitu kokonaisuus kopioidaan frozen\_context \-kenttään, API-kutsu suoritetaan Structured Outputs \-pakotuksella ja vastaus tallennetaan results-kenttään.

## **5.5. Hook-Riippuvuuksien Ruiskutus (Dependency Injection)**

Kaikki Python-suoritushookit askeleissa (esim. `SearchHook`, `ArchivalHook`) noudattavat tiukkaa I/O-sopimusta: ne ottavat vastaan vain yhden `dict`-rakenteen ja palauttavat `dict`-rakenteen. Jotta tietokanta- tai LLM-yhteyksiä ei tarvitse avata ja sulkea lukuisia kertoja, työnkulkumoottori (`DAG Executor`) ruiskuttaa automaattisesti aktiivisen tietokantayhteytensä (`Repository`) datarungon sisälle piiloavaimen `_sys_repository` alle ennen hookin suoritusta. 

Tämä "Dependency Injection via Payload" -malli mahdollistaa raskaiden riippuvuuksien jakamisen turvallisesti useiden hookien kesken asynkronisesti, pitäen hookit samalla "puhtaina" (Pure Functions) ja täysin yksikkötestattavina valesisällöllä (Mock Repository) ilman globaaleja sivuvaikutuksia.

## **5.6. SSOT Reititys & Dual-Reporting (RFC 7807)**

Backend on rakennettu ehdottomalle "Single Source of Truth" -arkkitehtuurille (Domain Service Layer).

* **Anemic Routers:** Kaikki API-reitittimet (`users.py`, `studio.py` jne.) ovat ohutta logiikkaa ("anemic"), jotka tekevät vain Pydantic-validoinnin. Ne **eivät koskaan** ota suoraa yhteyttä tietokantaan (`repository.get()`) tai toteuta käyttöoikeustarkistuksia omassa tiedostossaan.
* **Service Layer:** Kaikki pyynnöt reititetään suoraan kyseisen domainin Service-injektiolle (Esim. `AuthServiceDep`, `StudioServiceDep`), joka varmentaa Tenant-Eristyksen, roolitarkistukset sekä mahdollisen "Last Admin Protection" suojan.
* **Dual-Reporting & Enums:** Virheet hoidetaan aina **RFC 7807** hengessä: 
  1. Exception napataan
  2. Tulostetaan `logger.error` taulukkolokeihin kehittäjille *teknisen* poikkeuksen kera
  3. Nostetaan ulospäin `AppException`, joka piilottaa tekniset tiedot, mutta sisältää ehdottomasti **koneluettavan ErrorCodes-enumin** (Esim. `VALIDATION_FAILED`). Tämän pohjalta mobiiliclient päättelee oikean i18n-kielen ("No-String Mandate") ja renderöi asiakkaalle joko dialogin tai virheilmoituksen. Tällä taataan, ettei backend vuoda salaisuuksia ulos, eikä se koskaan joudu arvailemaan frontendin asettamaa kieltä.

## ---

**6\. Viivästetty Esityseristys (Omni-Channel Rendering)**

Tekoälyn tuotos on vain yksi koneluettava tila: results (puhdas data) ja frozen\_context.ui\_hints\_snapshot (semanttinen piirto-ohje). Tämä datarakenne purkautuu vasta aivan prosessin lopussa (Late-Binding) kolmeen tulostusformaattiin.

## **Esityskerros 1: Adaptiivinen ja Responsiivinen SDUI (Flutter & Riverpod)**

Frontend on "tyhmä" renderöintimoottori, joka on suunniteltu äärimmäisen mukautuvaksi, dynaamiseksi ja reaktiiviseksi.

1. **Riverpod ja Reaktiivisuus (Best Practices):**  
   * Sovelluksen tilanhallinta, datavirtojen (SSE) kuuntelu ja UI:n päivitykset rakentuvat puhtaasti **Riverpod 3.0** (Notifier, AsyncNotifier) varaan koodigeneroinnilla.  
   * **ChangeNotifier on ehdottomasti kielletty** arkkitehtuurissa, jotta vältetään tarpeeton boilerplate ja hallintabugit.
2. **Tyyppiturvallinen Koodigenerointi (Codegen Pienellä Datanhallinnalla):**  
   * Käytämme `@TypedGoRoute` / `@TypedStatefulShellRoute` ja `go_router_builder` -työkaluja täysin tyyppiturvallisen navigoinnin (GoRouter 17) pakottamiseen. Tällä vältetään ICU-sääntöjen vastaiset vapaat string-polut (No-String Mandate).
   * Koodigeneroijien (`build_runner`, `freezed`, `json_serializable`, `@riverpod`) käyttö on keskeinen V2-standardi. Silti vältämme raskaita Frontend API DTO-malleja: luottamattomissa taulukoissa luotamme defensiiviseen `SafeCast`-luokkaan parsinnassa dynaamisesti luotavan SDUI:n ehtojen mukaan.
3. **Responsiivisuus (Fluid Layouts):**  
   * Kaikki näkymät (DynamicStartScreen, LiveExecutionScreen) on rakennettu joustavilla Flutter-layouteilla (LayoutBuilder, Wrap, Flex, SliverGrid).  
   * Järjestelmä asettelee SDUI-komponentit saumattomasti isolla työpöytäruudulla rinnakkaisiksi paneeleiksi, tabletilla joustavaksi gridiksi ja mobiilissa pystysuoraksi listaksi, täysin automaattisesti yhdestä koodikannasta.  
4. **Widget Factory & Yhdistelmäkomponentit (Grounded UI):**  
   * UI iteroi sokeasti ui\_hints\_snapshot \-objektia.  
   * Jos vihje käskee piirtää desimaali-liukusäätimen (slider), ja datasta löytyy {slug}\_justification ja {slug}\_citation \-avaimet, tehdas käärii liukusäätimen automaattisesti moderniin **yhdistelmäkomponenttiin (Compound Widget)**.  
   * Tämä komponentti piirtää säätimen alle avattavan Markdown-laatikon, joka esittää LLM:n teoriaan pohjautuvan monikielisen perustelun ja klikattavan virallisen lähdeviitteen.  
5. **Live SSE & Version Drift:** UI kuuntelee Riverpodin kautta Server-Sent Events (SSE) \-striimiä ja päivittyy livenä. Järjestelmä vertaa ajon \_vX ID:tä kannan aktiiviseen versioon ja piirtää Audit-varoituksen, jos teoria, tiukkuus tai sääntö on päivittynyt ajon jälkeen.

## **Esityskerros 2: Taitettu PDF (Backend Jinja2)**

* **API:** GET /api/v2/executions/{id}/render?format=pdf  
* **Block Builder:** PDF-generointi on riisuttu staattisista domain-muuttujista. Se iteroi ui\_hints\_snapshotia samalla logiikalla kuin Flutter-frontend, latoen PDF-sivun HTML/CSS-palikka kerrallaan dynaamisesti luoden näyttävän, teoria-perusteluilla rikastetun asiakirjan historiasta riippumatta.

## **Esityskerros 3: Litteä Datatiedosto (Flat File / CSV Export)**

* **Tarkoitus:** Koneellinen vienti massaanalytiikkaa ja BI-järjestelmiä varten.  
* **API:** GET /api/v2/executions/{id}/render?format=flat  
* **Flattening Engine:** Palvelu purkaa koko syvän JSON-puun **yhdeksi litteäksi datariviksi** (One-Liner).  
* **Sarakkeiden Yhdenmukaistaminen:** Kenttien otsikot standardoidaan deterministisesti yhdistämällä askeleen ID ja kentän Slug (esim. step\_analyst\_bloom\_score, step\_analyst\_bloom\_score\_justification, step\_analyst\_bloom\_score\_citation). Näin monimutkaisinkin teoriamaadoitettu ajo tiivistyy aina eksaktiksi, tasalevyiseksi CSV/JSONL-riviksi.