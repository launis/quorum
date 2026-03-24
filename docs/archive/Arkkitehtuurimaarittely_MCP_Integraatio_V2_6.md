# ARKKITEHTUURIMÄÄRITTELY: Model Context Protocol (MCP) Integraatio - Cloud Native V2.6

Tämä on ohjelmiston suunnitteludokumentti Model Context Protocol (MCP) -standardin integroimisesta Quorum V2 -kognitiiviseen orkestraattoriin. Quorumin The Absolute Zero-Compromise V2 -arkkitehtuurin mukaisesti integraatio on suunniteltu puhtaasti serverless-pilviympäristöön (Firebase/Cloud Run) hyödyntäen asynkronisia SSE (Server-Sent Events) HTTP-rajapintoja kognition hakemiseksi.

---

## OSA I: TAVOITTEET (Mitä tällä MCP-uudistuksella saavutetaan?)

1. **Hallusinaatioiden Täydellinen Kuolema (Determinismin Paluu):** Pakottaa "Todellisuusherätys" (Reality Check). MCP-työkalu hakee netistä faktan, ja matriisin arvosana `score` pakotetaan heijastamaan empiiristä todellisuutta.
2. **The Authority Leap (Perustelujen Uskominen):** Perustelu (`reasoning_trace`) muuttuu subjektiivisesta keksinnöstä tarkkaan, luettuun ja dokumentoituun verkkolähteeseen.
3. **Ikuinen Forensisuus ja Läpinäkyvyys (The XAI Audit):** MCP:n hakema raakateksti tallennetaan millisekuntien tarkkuudella osaksi muuttumatonta `FrozenContext` -tietokantaa.
4. **Zero Vendor Lock-in:** Vapautuminen Google Vertex -sidonnaisuudesta. Kuka tahansa LLM voi käyttää The Tool Loopin tarjoamaa pilvihakua.

---

## OSA II: TEKEMINEN KÄYTÄNNÖSSÄ (Arkkitehtuurin Uudet Mallit)

Admin rakentaa Studio-työkalulla uusia "kognitiivisia topologioita" ohjaamalla MCP-oikeuksia yksittäisiin `StepRule`-solmuihin:
* **Topologia A (Integroitu Faktantarkistaja):** Yksi LLM googlaa itseään epäillen faktat ennen matriisin Pydantic-arviota (Suora korvaus lukitulle Vertex Search Groundingille).
* **Topologia B (The Prep-Step / Etsivä):** Halvempi agentti kerää uutiset puhtaaksi listaksi, ja vasta toinen, verkkoyhteydetön "Tuomari" -malli tekee kalliin o1-tasoisen matriisiarvion nettidatan pohjalta.
* **Topologia C (The Prosecutor / Haastaja):** Koneet tuomitsevat itsensä. Ensimmäinen tekee Sokko-arvion Pydanticin sisällä. Toinen lukee Sokko-arvion, saa The MCP Toolit, ja yrittää kumota netistä löytyvillä faktoilla ensimmäisen mallin luottamuksen.

---

## OSA III: KÄYTÄNNÖN SUORITUSPROSESSI (The Execution Pipeline)

Integraatio toteutetaan Quorumin serverless-arkkitehtuuriin seuraavissa vaiheissa:

1. **"The Core Foundation" (Pydantic & Firestore Parity):** `backend_v2/models/v2_core.py` päivitetään tukemaan `SystemConfigMCPGateways`, `AllowedMCPTool` ja `MCPAuditTrace` (extra='forbid' turvaten). Firestore-tietokannan `system_config`-kokoelmaan injektoidaan valtuutetut The Gateways.
2. **"The Engine & The Bridge" (Python MCP SDK ja The Tool Loop):** Rakennetaan `mcp_client_manager.py`. Muokataan Cloud Runissa pyörivä `dag_executor.execute_step` rutiinia siten, että se kykenee hylkäämään osittaisen LLM-vastauksen, tekemään asynkronisen työkalukutsun (nettiin) itsenäisenä SSE-pyyntönä toiseen mikropalveluun, päivittämään viestihistorian ja jatkamaan, kunnes LLM suostuu tulostamaan matriisin. Tallennetaan hakuloki The Firestore `executions` -kokoelmaan.
3. **"The Client Foundation" (Dart DTO Parity):** Quorumin Pydantic-turvallinen Dart-kerros (Riverpod/Freezed) päivitetään tunnistamaan uudet MCP DTO:t Firestoressa, jotta sovellus pysyy vakaana.
4. **"The Administrative SDUI" (Visualisointi):** Quorum Backendiin luodaan rajapinta luvanvaraisten työkalujen noutoon. Quorum Studio UI:n asetusvalikkoon koodataan MCP-pudotusvalikko (dropdown), ja Loppuraportin näkymään `execution_results_view` ohjelmoidaan "The AI Fact-Checking Audit" -laatikko.

---

## OSA IV: KÄYTTÖSKENAARIO ("The Dual-User Reality Check")

Tämä esimerkki demonstroi Quorum V2 -agentin voiman ratkoa ristiriitoja **Adminin staattisen datan** ja **Käyttäjän väitteen** välillä objektiiivisena tuomarina serverless-ympäristössä.

### 1. Pohjan Rakennusvaihe (Admin / Kouluttaja)
* Nimetön Pääkäyttäjä luo Quorum Studiossa työnkulun: "Sertifikaattikoe C++".
* **Staattinen Totuus:** Hän liittää askeleeseen "Tenttikirjan" faktan. Esim: *"Sääntö: Kaikki pointterit on vapautettava manuaalisesti."*
* **The Tools:** Admin sallii avoimen haun ulkoisesta ohjelmointirajapinnasta (C++ Library MCP Container).

### 2. Analyysin Aloitus (Loppukäyttäjä / Opiskelija)
* Opiskelija syöttää vastauksensa väittäen C++14:n mahdollistavan automaattisen vapautuksen.
* Hän painaa **Execute** tietämättä, että Quorum asettuu tutkijan rooliin.

### 3. Autonominen Työskentely (Quorum Backend Cloud Run)
1. **Staattinen Peilaus:** Tekoäly lukee Adminin säännön (Score 1 uhkaa).
2. **The MCP Reality Check:** Koska opiskelija nojasi uuteen tietoon ja MCP on sallittu, Agentti hakee Tool Loopissa itsenäisesti HTTP-yhteyden yli ulkoisesta SSE-kontista asiantuntijatiedon oppikirjan ohi (`search_web`).
3. **The Data Intake:** API-dokumentaatio palautuu tekoälylle, ja kysely tallentuu välittömästi Firestore`mcp_tool_audit`iin.

### 4. The Final Forensic Report (UI)
* **Arvosana:** 5/5
* **Perustelu (`reasoning_trace`):** *"Tarkistin opiskelijan väitteen MCP-haulla API-dokumentaatiosta. Sääntö on todella muuttunut C++14 päivityksessä. Opiskelija ansaitsee täydet pisteet tiedon modernista soveltamisesta vanhentuneen kurssimateriaalin ohi."*
* **XAI Todistusaineisto:** Raportin alareunassa Quorum-asiakas lataa Firestoresta The Auditin, joka näyttää tarkan API-URLin The Evidence Boxissa.

### 5. Custom Knowledge MCP (Esim. Sisäinen PDF tai The RAG)
Avoimen netin lisäksi organisaatioilla on usein suljettua tietoa (esim. yrityksen oma PDF-opas), joka edustaa absoluuttista totuutta.
* **The Custom Gateway:** Tälle datalle pystytetään täysin oma The MCP Gateway -kontti (esim. `internal_knowledge_mcp`), johon ladataan sisäinen PDF-materiaali tai yhteys vektorikantaan (Pinecone, yms.).
* **The StepRule:** Pääkäyttäjä voi ohittaa avoimen the Netin kytkemällä askeleelle päälle VAIN `internal_knowledge_mcp` -oikeuden.
* **The Tool Loop Parity:** Kooditasolla backend (`dag_executor.py` / `mcp_tool_loop.py`) ei edes tiedä, että nyt etsitään yksityisestä PDF-tiedostosta. Se lähettää LLM:n tool-pyynnön the Internal Gatewaylle, injectoi The ToolMessagen (PDF-katkelman) takaisin LLM:n työmuistiin, ja pakottaa Pydantic-matriisin The Evidenceen nojaten, rangaisten syötettä Pydantic-Enumissa (BARS) armottomasti, jos se on sisäisen ohjesäännön vastainen.

---

## OSA V: KOODI- JA TIETOKANTATASON IMPLEMENTOINTIOPAS

### 1. The Tool Choice Logiikka (`tool_choice="auto"`)
Jotta MCP-integraatio toimii THE TOOL LOOPissa, tekoälyn on kyettävä itse arpomaan, antaako se Pydantic-matriisin vai hakeeko se uutta dataa verkosta. Tästä syystä `dag_executor.py` ja `LLMClient` on päivitettävä tukemaan tilaa, jossa LLM:lle annetaan Pydantic-skeeman rinnalla **valinnanvapaus**.
* **Epistemic Uncertainty (Epoksivarmuus):** Kun "Zero-Trust"-rooli on päällä ja LLM kohtaa väitteen jota se ei tunnista, sen päättelyalgoritmi estää hallusinaation ja valitsee vapaaehtoisesti THE TOOLIN the matriisin sijaan.
* Määrittele säännöt niin, että vasta The Tool Loopin täytettyä viestihistorian faktoilla (ToolMessage), tekoälyn epävarmuus katoaa ja algoritmi suostuu tulostamaan matriisin the loopin lopussa.

### 2. Pydantic-Tietokantamallit (`v2_core.py`)
Tietokannan (Firestore/JSON) on pysyttävä 100% strict-tyyppiturvallisena Quorumin linjan mukaisesti. Seuraavat lisäykset on koodattava kantaan:

```python
# 1. Määritellään MCP-palvelimet (V2_Core)
class MCPGatewayDefinition(V2CoreBase):
    gateway_slug: str = Field(description="Esim. brave_search_mcp")
    transport: Literal["sse"] = Field(description="Strict enforcement of remote SSE serverless connections.")
    sse_url: str = Field(description="External HTTPS endpoint for the remote MCP container")
    env_vars: dict[str, str] = Field(default_factory=dict, description="Esim. Firebase Secret Manager keys")

class SystemConfigMCPGateways(V2CoreBase):
    id: str = Field(pattern=r"^([a-z]+)_[a-zA-Z0-9]{8,}$")
    type: str = Field(default="mcp_gateways")
    gateways: dict[str, MCPGatewayDefinition]

# 2. Askeleiden oikeudet (StepRule)
class AllowedMCPTool(V2CoreBase):
    gateway_slug: str = Field(description="Viittaus SystemConfigMCPGateways -rekisteriin")
    tool_name: str = Field(description="Tarkka MCP-työkalun nimi (esim. search_web)")

class StepRule(V2CoreBase):
    allowed_mcp_tools: list[AllowedMCPTool] = Field(default_factory=list)

# 3. Raportoinnin jäädytys (The XAI Audit Trail)
# Kun verkko on tutkittu, on ehdotonta tallettaa askeleen FrozenContext-tietueeseen tarkka
# kopio tiedoista XAI (Explainable AI) todisteiksi tulevaisuuden raportointia varten.
class MCPAuditTrace(V2CoreBase):
    timestamp_utc: datetime
    gateway_slug: str
    tool_name: str
    arguments_passed: dict[str, Any]
    result_raw: str | dict[str, Any]
    is_error: bool = False

class FrozenContext(V2CoreBase):
    mcp_tool_audit: list[MCPAuditTrace] = Field(default_factory=list)
```

The Tool Loop Pseudo-arkkitehtuuri (`dag_executor.py` suoritettavana Cloud Runissa):
```python
async def _execute_step(self, step: StepRule, ...):
    # Hydrate Tools
    mcp_tools = await self.mcp_manager.list_tools_for_step(step.allowed_mcp_tools)
    messages = [SystemMessage(...), HumanMessage(...)]
    mcp_audit_log = []

    # HUOM: Tämä "Tool Loop" -suoritus on refaktoroitava erilliseen 'mcp_tool_loop.py' -tiedostoon,
    # jotta 'dag_executor.py' ei muutu massiiviseksi The God Object -monoliitiksi (kts. OSA VI).
    
    # 1. The Conductor delegating to The Engine
    tool_loop = MCPToolLoop(llm_client, self.mcp_manager)
    
    # 2. THE SERVERLESS TOOL LOOP is processed securely inside the new modular class
    final_pydantic_dict, mcp_audit_log = await tool_loop.execute_until_matrix(
        messages=messages,
        allowed_tools=step.allowed_mcp_tools,
        dynamic_schema=MatrixSchema,
        max_loops=3  # Strictly limited to prevent Cloud Run 504 timeouts
    )
    
    # 3. Pydantic valmis -> Hyväksy tulos XAI audit trailin kera
    record.frozen_context.mcp_tool_audit.extend(mcp_audit_log)
    return final_pydantic_dict
```

---

## OSA VI: CLOUD DEPLOYMENT ARKKITEHTUURI (Firebase)

Koska Quorum operoi Firebase/Firestore -ympäristössä, järjestelmän luonne on Serverless (palvelimetta toimiva mikropalveluarkkitehtuuri). Tämä Cloud Native -lähtökohta ohjaa koko the MCP-ratkaisun rakentumaan HTTP-pohjaisten The Gatewaysien ympärille eristäen sovellukset fyysisesti toisistaan.

### 1. Quorumin Puhdas jako (The Decoupled Microservices)
Firestore-yhteensopiva MCP-toteutus eristetään arkkitehtuurisesti näin:

* **Päätösmoottori (Quorum Backend):** Järjestelmän aivot, pyörii omassa Cloud Run / Cloud Functions -instanssissaan. Kirjoittaa ja lukee Firestorea tehokkaasti. Täällä ajetaan yllä koodattu The Tool Loop. Backendillä ei ole mitään varsinaisia selaimia tai web-skreippereitä asennettuna itseensä.
* **The MCP Gateways (Etsivät):** Nämä The Toolit pyöritetään täysin erillisissä, keveissä The Cloud Run -mikropalvelukonteissa (Taikka ostetaan avaimet käteen -palveluna kaupallisilta tahoilta, jotka tarjoavat MCP SSE-rajapintoja). Nämä the etäpalvelimet kuuntelevat asynkronisia HTTP/SSE -pyyntöjä. Quorumin Backend ja Gateway keskustelevat turvallisesti keskenään internetin yli pelkällä tekstillä.

### 2. Oikea Koodirakenne ("No God Objects" -periaate)
`dag_executor.py` on tällä hetkellä 500 riviä pitkä. Emme saa sijoittaa The Tool Loopin satoja rivejä koodia The Executorin sisälle (God Object -antipattern). Quorumin Domain Driven Design -arkkitehtuurin mukaisesti `backend_v2/services/orchestrator/` -kansio pilkotaan ylläpitämällä SRP (Single Responsibility Principle) seuraavasti:

1. **`dag_executor.py` (The Conductor):** Vastaa pelkästään verkoston DAG-reitityksestä, The Hookkien ajamisesta ja kokonaisvaltaisen askeleen tilan hallinnasta. Kutsuu `mcp_tool_loop.py`:tä.
2. **`mcp_tool_loop.py` (The Engine / UUSI):** Ottaa sisäänsä `while max_loops > 0` -rakenteen, asynkronisen the LLMClient -hallinnan `tool_choice="auto"` moodilla ja Pydantic JSON-purkamisen. Ottaa sisään pelkän puhtaan the messages -listan ja palauttaa the valmiin the Pydantic Enum-tuloksen the Executorille. Tämä on Se Paikka, jossa The ToolMessage Injection The ruiske tapahtuu.
3. **`mcp_client_manager.py` (The Bridge / UUSI):** Piilottaa the raa'an asynkronisen HTTP/SSE-viestinnän the Internet-konteille the Orchestratorilta kokonaan. Tuntee vain the ToolCall argumentit ja the sse_urlit.

### 3. The BARS Matrix Forcing (Sanallisten Gaugien Ratkaisu)
Erityisohjeistus the BARS (Behaviorally Anchored Rating Scales) -matriiseille (Esim. "matrix_epistemic_humility"): BARS-matriisit ovat Pydantic-skeemassa Enum-listoja the pakotetuista väittämistä. 
* Ennen MCP:tä LLM arpoi väittämän sokeana The Context Windowssa vain The User Inputin pohjalta.
* Uudessa V2.6 Arkkitehtuurissa, kun The Tool Loop (`mcp_tool_loop.py`) iskee netin raa'an vastauksen The ToolMessage-objektilla suoraan LLM:n työmuistiin Pydantic-pakotuksen THE TOISELLA kierroksella, The LLM:n The Attention Mechanism pakotetaan matemaattisesti valitsemaan se The BARS Anchor-Enum, joka on linjassa The Evidence:n (ToolMessage) kanssa silloinkin kun alkuperäisessä inputissa valehdeltiin ummet ja lammet oppikirjasta. The XAI (Explainable AI) Audit trail kytketään näihin arvoihin ja viedään UI:ssa tuomarille selitteeksi the valinnan pätevyydestä.

### 4. Turvallisuuden ja Aikakatkaisun ratkaisu 
Kun otat yhteyden rinnakkaisten The Serverless-konttien välillä:
1. **SSOT Firestore Config:** `SystemConfigMCPGateways` -tiedot ja the Gateway URL:it tallentuvat suoraan Firestore-kokoelmaan `system_config`.
2. **Aikakatkaisut (Timeout constraints):** Serverless ympäristöissä the Request-vastine ei saa ylittää API-rajojen kellotusta. Koska "Topologia A: Integrated Fact-Checker" -mallissa LLM voi tuhlata pitkiä aikoja itsenäiseen verkkosurffailuun The Tool Loopin sisällä, se altistaa Quorumin `504 Gateway Timeout` -viiveille.
3. **Miksi Topologia B dominoi Pilvessä:** Tästä syystä asiantuntijuuden rinnakkaistaminen (Topologia B) istuu the Firebaseen täydellisesti. Ensimmäinen The Cloud Task ("Etsivä") tekee itsenäisesti The Tool Loopin, hakee datan The Ulkoisista Konteista, ja tallentaa tuloksen nopeasti Firestoreen. Tämän jälkeen ohjelma irrottaa the resurssit ja The DAG-moottori herättää erillisen the "Tuomarin", joka vain silmänräpäyksessä lukee The Firestoren valmiin datan ja the alkuperäisen syötteen antaen finaalisen analyysin. Jaettu työnkulku eliminoi the timeoutit kokonaan ja maksimoi the skaalautuvuuden.

### 5. The MCP Server -konttien Hostaus (Konkreettinen Ehdotus)
Koska Google Firebasella ei ole (vielä) sisäänrakennettua, valmista "The MCP Backend API:a", Quorum V2 joutuu hakemaan itse datan netistä erillisen The Gatewayn kautta. Quorum Backendiin ohjelmoidaan yllä kuvattu The MCP Client -protokolla, mutta **The MCP Serverit** (jotka tekevät varsinaisen työn) on hankittava ulkopuolelta. Tähän on kolme vaihtoehtoa:

**Vaihtoehto 1: Valmis kaupallinen "Agentic Search" SaaS (VIRALLINEN SUOSITUS: TAVILY AI)**
* **Mitä:** Ostetaan API-avaimella pääsy valmiiseen tekoälyille suunniteltuun The Web Search API -palveluun (esim. Tavily AI). Tämä korvaa tarpeen hostata itse monimutkaisia hakukone-kontteja.
* **Miksi Quorum V2 valitsee Tavilyn (The XAI Fit):**
  1. **Tarkka The Audit Trail:** Tavily palauttaa HTTP-vastauksessa raa'at URL-osoitteet ja the the uutistekstit suoraan Backendiin. Nämä tallennetaan Quorumin `MCPAuditTrace`:iin absoluuttisina the XAI (Explainable AI) todisteina UI:n the tuomarille. (Toisin kuin natiivit LLM:ien omat "Black Box" haut, jotka the piilottavat the prosessin).
  2. **Optimoitu Token-kulutus:** Tavily siivoaa The the HTML-mainosroskat the sivustoilta ennen palautusta. The Pydantic The Tool Loopin the työmuisti (Context Window) the ei räjähdä the 100 000 the tokenin hintaiseksi.
  3. **Zero DevOps:** Ei the ylläpitokustannuksia omasta Docker-mikropalvelusta. Admin vain liittää `https://api.tavily.com/search` URlin (tai MCP SSE-endpointin) the `seed_data.json`iin the `SystemConfigMCPGateways`-lohkossa.

**Vaihtoehto 2: Oma Open-Source Cloud Run -kontti (V2.1 Riippumattomuus)**
* **Mitä:** Ladataan avoimen lähdekoodin MCP Server (Kuten Anthropicin virallinen `mcp-server-brave-search`), asennetaan se Docker Imagena yrityksen omaan **Google Cloud Run** -tiliin. The Cloud Run antaa sille The URLin `https://mcp-brave.a.run.app/sse`. 
* **Miksi:** Täydellinen kontrolli liikenteestä ja The Zero Vendor Lock-in the Search enginestä (Käytetään Brave Search API -avainta itse halvimpaan hintaan). The Cloud Run API-kutsut turvataan The Firebase IAM The Service Account -varmenteilla.

**Vaihtoehto 3: Koodataan Oma "The Internal Knowledge MCP Server" (RAG)**
* **Mitä:** Organisaation PDF:t ja sisäinen the Pinecone Vektoritietokanta eivät itsessään ymmärrä MCP-puhetta. Quorum the backend-tiimi ohjelmoi "Tyhmän The Wrapper" -mikropalvelun Pythonilla tai TypeScriptillä. Se kontitetaan the Cloud Runiin (`the_internal_knowledge_mcp`), ja kaikki mitä se tekee on: Ottaa the SSE Eventtejä vastaan the Quorum the Backendiltä -> Tekee the tavanomaisen haun Pineconessa/Drive:ssä -> Puskee the tuloksen takaisin the MCP The Formatissa the Quorum Backendille the ToolMessagena.
* **Miksi:** The Absolute Privacy. Yrityksen salaista dataa the PDF dokumenteista tuodaan the Tool Loopin ruiskeena the LLM:n työmuistiin täydellisellä the XAI-audit The läpinäkyvyydellä. (Korvaa Vertex AI:n rajoitetun V1 the Groundingin).

### Jatkotoimenpiteet (Execution Phase)
Siirrytään implementoimaan **Vaihtoehto 1 (SaaS / Tavily) kooditason The Tool Loop** -integraatio valmiiksi the `backend_v2` -ydinmoottoriin. Tämä varmistaa the arkkitehtuurijutut:

**Konkreettinen Töiden Järjestys (TIER 2):**
1. **The Database The Engine:** Päivitetään `backend_v2/models/v2_core.py` Pydantic-mallit tukemaan The Gateway -rekisteriä (`SystemConfigMCPGateways`) ja The Audit Trailia (`FrozenContext.mcp_tool_audit`).
2. **The Seeding:** Injektoidaan uudet the rakenteet `backend_v2/seed/seed_data.json` the tiedostoon ja the validoidaan the strict-pakotus the The Pydantic the Pledgen mukaisesti.
3. **The Orchestrator Refactor:** Eristetään the `dag_executor.py` the LLM the HTTP-kutsut the omaan modulaariseen the `mcp_tool_loop.py` the luokkaansa the (Single Responsibility Principle). Säädetään the Anthropic/OpenAI The API-kutsu tukemaan `tool_choice="auto"` the The BARS the Enum-pakotusta varten the kakkoskierroksella.
