# EPIC 89: Dynamic Tool Registry & Pluggable MCP Architecture

## 1. Yhteenveto (Executive Summary)
Quorumin nykyinen työkalukerros (`mcp_tool_loop.py`) on MVP-hengessä kytketty tiukasti yhteen työkaluun (Tavily AI Search). Jotta järjestelmä voi palvella laajempaa työnkulkuautomaatiota ja organisaatiokohtaisia tarpeita (esim. Confluence-haut, sisäiset RAG-tietokannat, API-integraatiot), työkalujen injektion ja suorituksen on oltava täysin dynaamista.

Tämä Epic irrottaa LLM:n työkalusilmukan hardkoodatusta Tavilystä ja esittelee **Dynamic Tool Registry** -arkkitehtuurin. Muutos mahdollistaa minkä tahansa uuden tietolähteen kytkemisen Quorumiin siten, että Epic 88:n asettamat tiukat forensiikka- ja laatuvaatimukset (Quality Gates, Soft Delete, Alias Registry) toteutuvat automaattisesti ilman lisätyötä.

---

## 2. Nykytilan Ongelmat
1. **Hardkoodattu julistus:** `TAVILY_TOOL_DECLARATION` ja siihen liittyvä suorituslogiikka elävät suoraan orkestraattorin ytimessä (`mcp_tool_loop.py`).
2. **Joustamattomuus:** Jos organisaatio haluaa käyttää sisäistä dokumentaatiota (esim. Archivist RAG), koko työkalusilmukka pitäisi kirjoittaa uusiksi.
3. **Data-Sovereignty:** Tällä hetkellä järjestelmä ei tue konfiguraatio-ohjattua (Workflow/SystemConfig) työkalujen rajoittamista, vaan Tavily on aina aktiivinen ulkoisilla hauilla.

---

## 3. Tavoitetila (Arkkitehtuuri)

### 3.1 Sisäinen Tool Registry (Vaihtoehto B)
Arkkitehtuuri siirtyy malliin, jossa työkalut on rekisteröity abstraktien rajapintojen kautta. Tämä pohjustaa myöhempää integraatiota virallisen Model Context Protocol (MCP) -standardin mukaisten ulkoisten palvelinten kanssa.

*   **`BaseTool` -abstraktio:** Kaikki työkalut (Tavily, Jira, Confluence, Sisäinen RAG) toteuttavat yhteisen rajapinnan:
    *   `get_declaration()`: Palauttaa OpenAI/LiteLLM-yhteensopivan JSON-skeeman työkalulle.
    *   `execute(**kwargs)`: Suorittaa työkalun ja palauttaa standardoidun tuloksen.

*   **`ToolDispatcher`:** Uusi komponentti, joka lukee sallitut työkalut ajon konfiguraatiosta (esim. `["web_search", "company_wiki"]`). Se injektoi näiden työkalujen julistukset LLM:lle, sieppaa `tool_call` -pyynnöt ja reitittää ne oikealle työkalulle dynaamisesti.

### 3.2 Konfiguraatio-ohjattu Injektio (Sovereignty)
Datalähteet eivät saa olla globaalisti päällä. Joissakin työnkuluissa LLM:n ei pidä hakea tietoa ulkoapäin. Työkalujen injektio määritellään `SystemConfig` tai `WorkflowConfig` (DAG) tasolla, jolloin eri ajoissa on eri työkalut käytössä organisaation tarpeiden mukaan.

### 3.3 Yhtenäinen Forensinen Jälki (Forensic Parity)
Jotta dynaamiset työkalut eivät riko Epic 88:n jäljitettävyyttä, niiden on tuotettava standardoitu Audit-jälki:
*   Nykyinen `MCPAuditTrace` abstrahoidaan yleiseksi `ToolExecutionTrace`:ksi (tai laajennetaan).
*   Sillä ei ole väliä, tuleeko tulos Tavilystä (URL) vai sisäisestä HR-dokumentista (Dokumentti-ID); tuloksen on aina purkauduttava yhtenäiseen `<<QRM-SRC-X>>` alias-muotoon.
*   Tämä takaa sen, että **Fuzzy Match (RapidFuzz)**, **Soft Delete** ja **UI-pariteetti** toimivat automaattisesti mille tahansa uudelle työkalulle.

---

## 4. Onnistumisen Kriteerit (Quality Gates)

- [ ] **Työkalujen Eristys (SRP):** `mcp_tool_loop.py` ei sisällä viittauksia Tavilyyn tai muihin yksittäisiin työkaluihin. Se operoi vain `ToolDispatcherin` ja `BaseTool`-rajapinnan kautta.
- [ ] **Dynaaminen Rekisteri:** Järjestelmään on mahdollista lisätä uusi työkalu (esim. Mock-työkalu testiä varten) vain luomalla uusi `BaseTool`-toteutus ja rekisteröimällä se `ToolDispatcherille`.
- [ ] **Konfiguraatio-ohjaus:** Työkalut voidaan kytkeä päälle ja pois `SystemConfig` tai Workflow-parametrien kautta per ajo.
- [ ] **Forensinen Jatkuvuus:** Tavilyn siirto abstraktin työkalun taakse ei riko Epic 88:n raportointia. Tulokset linkittyvät `EvidenceQuoteDTO`-rakenteisiin tismalleen kuten ennenkin.

---

## 5. Siirtymästrategia
1.  **Refaktorointi:** Eristetään olemassa oleva Tavily-logiikka uuteen `TavilyTool`-luokkaan, joka toteuttaa `BaseTool`-rajapinnan.
2.  **ToolDispatcherin luonti:** Korvataan `mcp_tool_loop.py`:n hardkoodatut osat dispatcher-kutsuilla.
3.  **Audit Tracen päivitys:** Varmistetaan, että `MCPAuditTrace` pystyy tallentamaan geneerisempiä metadata-arvoja (kuten Document ID:tä URLs-listan sijaan).
4.  **Integraatiotestaus:** Varmistetaan E2E-testeillä, että nykyinen työnkulku toimii täsmälleen samalla tavalla uuden rekisterin läpi.

---

## 6. Testiskenaario: Wikipedia MCP & Paikallinen dokumentti

Jotta voimme varmistaa Dynamic Tool Registryn toimivuuden ja samalla taata **Epic 88:n mukaisen 100 % forensisen jäljitettävyyden**, käytämme konkreettista testiä yhdistämällä organisaation sisäisen dokumentin ja ulkoisen avoimen datan (Wikipedia).

### 6.1 Skenaarion asetus (Setup)
*   **Sisäinen lähde (Local Context):** LLM:lle syötetään paikallinen PDF-tiedosto `c:\src\quorum\docs\jwdatat\lopputuote.pdf`, joka käsittelee "Etä- ja hybridityöpolitiikan uudistamista" (mm. tavoitejohtamista ja läsnäolon seurantaa).
*   **Ulkoinen työkalu (Dynamic MCP):** `ToolDispatcher` injektoi ajoon avoimen lähdekoodin **Wikipedia MCP Serverin** (`@modelcontextprotocol/server-wikipedia`), joka antaa LLM:lle pääsyn työkaluihin `search_wikipedia` ja `get_wikipedia_article`.
*   **Prompti (Arviointimatriisi):** *"Arvioi dokumentin ehdottamaa hybridityömallia. Etsi akateemista tai yleistä vahvistusta tavoitejohtamisen (Management by objectives) ja etätyön (Hybrid work) teemoista käyttämällä Wikipedia-hakua. Palauta todisteet molemmista lähteistä."*

### 6.2 Odotettu Forensinen Jälki (Matrix Summary UI)

Kriittisin vaatimus on, että uusi dynaaminen arkkitehtuuri ei riko Epic 88:n lupausta "Sovereign Traceabilitystä". Kun Quorum renderöi loppuraportin (Flutter tai PDF Matrix Summary), käyttöliittymän on **aina** näytettävä selkeästi jokaisen sitaatin lähde.

Renderöitävän käyttöliittymän tulee näyttää tältä:

> **Arviointi: Hyväksytty (4/5)**
>
> **Lainaukset (quotes):**
> *   *"Esihenkilöiden työtä tuetaan siirtymällä läsnäolon seurannasta selkeisiin tavoitemittareihin."*
>     🔗 **Lähde:** `lopputuote.pdf` (Sisäinen dokumentti)
> *   *"Management by objectives is a strategic management model that aims to improve the performance of an organization by clearly defining objectives..."*
>     🔗 **Lähde:** `Wikipedia: Management by objectives` (MCP-työkalu) ✅ MCP-Varmennettu
> *   *"Koko oppilaitoksen yhteisestä ankkuripäivästä luovutaan..."*
>     🔗 **Lähde:** `lopputuote.pdf` (Sisäinen dokumentti)

### 6.3 Verifioitavat järjestelmävaatimukset (Epic 88 x Epic 89)
Tämä testitapaus todistaa arkkitehtuurin eheyden kolmella tasolla:
1.  **Dynaaminen Routing:** LLM ymmärtää hakea määritelmät Wikipediasta MCP-työkalun läpi, samalla kun se lukee paikallista PDF:ää.
2.  **Alias Registry Integrity:** `BlueprintTransformer` kykenee luomaan `<<QRM-SRC-X>>` aliakset sekaisin sisäisestä PDF-tekstistä ja MCP:n palauttamasta dynaamisesta tekstistä, purkaen ne yhdenmukaiseen `EvidenceQuoteDTO` -muotoon.
3.  **UI Traceability:** Käyttöliittymä ei koskaan piilota lähdettä. Jokaisen sitaatin yhteydessä näkyy, onko kyseessä paikallinen vai ulkoinen lähde, mahdollistaen asiantuntijalle turvallisen hylkäämisen (Soft Delete), jos Wikipedia-sitaatti on irrotettu kontekstista.
