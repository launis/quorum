# Phase 1: Backend (Phase 0 Citation Extraction + Epic 82 Audit Trail)

Tämä suunnitelma kattaa backend-muutokset, joiden avulla siirrytään deterministiseen faktantarkistukseen (Phase 0) ja mahdollistetaan järjestelmän auditointijäljen (System Audit Trail) renderöinti loppuraporttiin (Epic 82).

## 1. Uusi Pydantic-malli: CitationExtractionResult
**Tiedosto:** `backend_v2/models/domain/mcp.py`
- Luodaan Pydantic-malli `CitationExtractionResult`, joka sisältää listan objekteja. Näissä objekteissa on `claim_text` (alkuperäinen väite, suora lainaus tekstistä) ja `search_query` (haettava termi).
- Seurataan tiukkaa Pydantic V2 -standardia (esim. `model_config = ConfigDict(frozen=True)`).

## 2. Phase 0 Logiikka mcp_tool_loop.py:ssä
**Tiedosto:** `backend_v2/services/mcp/mcp_tool_loop.py`
- Korvataan vanha stokastinen `tool_choice="auto"` -lähestymistapa (Phase 1) deterministisellä koodiohjatulla rakenteella.
- **Vaihe 0:** Kutsutaan `LLMTaskExecutor.execute_structured_task()` `fast`-strategialla (eli `LLMClient.from_strategy("fast")`). LLM tuottaa `CitationExtractionResult`-rakenteen pelkästään lähdetekstin perusteella.
- **Physical Anchoring Mandate:** Validoidaan LLM:n poimimat `claim_text`-arvot käyttämällä tiukkaa `str.find()` -hakua alkuperäistä lähdettä vasten. Jos eksaktia osumaa ei löydy, laukaistaan välitön `SemanticEvidenceError` (Fail-Fast) hallusinaation torjumiseksi.
- Vain ne haut (`search_query`), joiden `claim_text` on onnistuneesti validoitu lähdetekstistä, suoritetaan koodin puolelta deterministisesti MCP-työkaluilla.

## 3. WorkflowDTO:n Laajennus (System Audit Trail)
**Tiedostot:** `backend_v2/models/v2_core.py` (tai missä WorkflowDTO sijaitsee) ja `backend_v2/seed/seed_data.json`
- Lisätään `WorkflowDTO`-malliin boolean-kenttä `system_audit_trail: bool = False`. Tämä ohjaa, näytetäänkö faktantarkistusloki asiakkaalle.
- Päivitetään olemassa olevat työnkulut SSOT:iin (`seed_data.json`) pitäen huolta validista datasta.

## 4. XAI Injektio Context Routerissa
**Tiedosto:** `backend_v2/services/orchestrator/context_router.py`
- Päivitetään keräilologiikkaa. Jos `workflow.system_audit_trail == True`:
  - Kerätään työnkulun ajon ajalta tuotetut `MCPAuditTrace`-objektit.
  - Tiivistetään trace-tiedot token-rajan suojelemiseksi (vain Työkalu, Hakusana, URL ja Tiivistelmä).
  - Injektoidaan tiivistelmä dynaamisesti synteesi-ohjeistukseen (`synthesis_instructions`): *"Jos kontekstissa on MCPAuditTrace-dataa faktantarkistuksista, lisää raportin aivan loppuun osio 'Järjestelmän Faktantarkistusloki', johon listaat tehdyt haut ja paljastuneet ristiriidat."*

## 5. Verifiointisuunnitelma (Backend Audit Loop)
Suoritetaan `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/mcp_tool_loop.py backend_v2/models/domain/mcp.py --test` ja lisätään uudet yksikkötestit:
- `test_citation_extraction_empty_document`: Tyhjä dokumentti palauttaa tyhjän listan.
- `test_citation_extraction_hallucinated_claim_rejected`: Phase 0 hallusinoi väitteen, jolloin `str.find` hylkää sen ja laukaisee `SemanticEvidenceError`:in.
- `test_execute_tool_loop_deterministic_search`: Varmistetaan koodin deterministinen hakukontrolli ilman stokastista työkalun valintaa.
