# EPIC: Model Context Protocol (MCP) Integraatio & The Tool Loop (V2.6)

## 1. Yhteenveto (Summary)
Tämä Epic määrittelee Quorum V2:n siirtymisen perinteisistä peräkkäisistä Post-Hook -ratkaisuista (kuten vanhasta `search.py`:stä) moderniin agenttiseen **Model Context Protocol (MCP)** -malliin. Siirtymän myötä tekoälymallit eivät enää ainoastaan palauta hakusanoja kognitionsa sivutuotteena. Sen sijaan ne **keskeyttävät asynkronisesti oman suorituksensa** ("The Tool Loop"), hakevat kriittisen datan ulkoisista palvelimista (esim. Tavily AI SaaS tai organisaation sisäinen RAG/PDF-kontti) kesken arvioinnin ja maadoittavat BARS-matriisien tuloksensa näihin palautettuihin XAI-faktoihin (The Evidence) reaaliajassa, saman askeleen (Node) sisällä.

Tämä uudistus on ratkaiseva ohjelmallinen muutos "Zero-Trust" -mallin soveltamisessa ja arvioinnin tarkkuuden kalibroinnissa ("Hallusinaatioiden Täydellinen Kuolema").

## 2. Tavoitteet (Objectives)
- **Determinismin Paluu (The Reality Check):** Pakottaa tekoäly lukemaan MCP:n tuottama raakafakta (The Evidence) ennen Pydantic BARS-matriisin täyttöä työkalukierroksen jälkeen.
- **Infrastruktuurin Serverless-Eristys (No God Objects):** Koodikanta puhdistetaan irrottamalla Quorumin ydinmoottorista kaikki web-skraappaus- ja hakulogiikat. Haut suoritetaan asynkronisina HTTP/SSE-rajapintapyyntöinä itsenäisiin the mikropalveluihin (The Gateways).
- **Core Orchestrator Refaktorointi:** Suuren `dag_executor.py`:n pilkkominen erillisiksi the Single Responsibility -objekteiksi (`mcp_tool_loop.py` & `mcp_client_manager.py`). Järjestelmä alkaa tukemaan LLM-palveluntuottajien natiiveja `tool_choice="auto"` -ohjauksia.
- **Ikuinen Forensisuus ja Läpinäkyvyys (The XAI Audit Trail):** Kaikki järjestelmän the MCP-kyselyt kirjautuvat absoluuttisella tarkkuudella muuttumattomaan `FrozenContext.mcp_tool_audit` -tietueeseen tietokantaan UI-näkyvyyttä varten.

## 3. Vaiheet (Milestones & Execution Plan)

### Vaihe 1: Pydantic & Firestore Parity (The Database Engine)
- **Kuvaus:** Rakennetaan luotettavat Pydantic-mallit MCP Gateway-rekistereille, käyttöoikeuksille (`allowed_mcp_tools`) ja XAI-auditoinnille.
- **Toimenpide:** Päivitetään `backend_v2/models/v2_core.py` sisältämään `SystemConfigMCPGateways`, `AllowedMCPTool` ja laajennetaan `FrozenContext` -mallia listaamaan `MCPAuditTrace`. Varmistetaan `extra='forbid'` turvallisuus.
- **Datan Injektointi:** Lisätään ohjelmoidut oikeusrakenteet ja Gatewayn the API-osoitteet (kuten Tavily) dev-kantaan päivittämällä `backend_v2/seed/seed_data.json`.

### Vaihe 2: Koodikannan Refaktorointi ja Silmukka (The Engine & The Bridge)
- **Kuvaus:** Rakennetaan Quorum-moottoriin silmukkamekaniikka (Tool Loop), joka tauottaa LLM-ajon the rajapinnan ohjauksessa.
- **Toimenpide 2A:** Eristetään `dag_executor.py`:stä (`_execute_step`) the HTTP-kutsut uuteen the modulaariseen `mcp_tool_loop.py` -luokkaan.
- **Toimenpide 2B:** Rakennetaan the `mcp_client_manager.py` (The Bridge) vastaamaan raa'asta asynkronisesta the SSE / HTTP -viestinnästä the Gateway-kontteihin suojattuna erillisasiana. Ohjelmoinnin on tultava tukemaan askeleen (Node) toisella "kierroksella" tapahtuvaa BARS Pydantic-matriisin pakottavaa "puristusta" MCP-Evidencen the ympärille.

### Vaihe 3: Serverless Agentic Search Gateway (esim. Tavily AI)
- **Kuvaus:** Toteutetaan avoimen datan (The Open Web) tuonti erikoistuneen hakumoottorirajapinnan kautta ilman oman the search engine docker-mikropalvelun koodaamista.
- **Toimenpide:** Kytketään Vaiheen 2 rakentama Bridge (Tool Loop in `mcp_client_manager.py`) osoittamaan suoraan the Tavily AI:n avaimeen the (System Config Vaultissa). Moottori hakee ja suodattaa dataa, jättäen LLM:n työmuistiin pelkän konemaisen the HTML-siivotun tekstin the Token-kulutuksen estämiseksi. Varmistetaan The Timeout protection the Firebase-ympäristön asettamissa rajoissa käyttämällä *The Prep-Step / Etsivä* -hakutopologiaa raskaiden Nodejen edellä.

### Vaihe 4: Esityskerros ja Auditoinnin UI (The Administrative SDUI)
- **Kuvaus:** Tuodaan auditoinnin tulokset visuaalisesti the selväkieliseen the Loppuraporttiin Frontendiin.
- **Toimenpide:** Päivitetään Flutter-käyttöliittymä the Riverpod/Freezed -kerroksessa sietämään the uusia `MCPAuditTrace` DTO-malleja the kanta-latauksissa. Koodataan `execution_results_view` -raporttiin The Evidence Box, joka näyttää XAI-tuomarille tarkan Pydantic the Pledgen the mukaisen the API-URLin (FrozenContextista). Tämän avulla loppukäyttäjä näkee "Mistä tämä fakta löytyi" ilman LLM-kuplaa.

---
*Tämä Epic hyödyntää Quorum V2.6 Cloud Native The Tool Loop -paradigmaa jättäen vanhat pre/post -hookit ehdollisesti väliaikaisiin tai datamuunnos -käyttöihin the the kognition analyysissä.*
