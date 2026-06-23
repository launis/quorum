# Epic 85: Analysis Refinements, XAI Fixes, and Synthesis Brevity

## 1. Background
Several interconnected issues were discovered during execution monitoring regarding the Explainable AI (XAI) output, system audit trails, and the length of generated synthesis texts.

## 2. Objective
Implement minor but critical architectural refinements to ensure external tools can run when requested, all audit traces are collected, text synthesis is kept strictly concise, and the remaining EPIC 82 items are completed.

## 3. Implementation Plan

### Fix 1: Source Sufficiency Gate Bypass
**File:** `backend_v2/services/mcp/mcp_tool_loop.py`
**Status:** ❌ Tekemättä
**Problem:** `is_source_sufficient()` (rivi 94-108) blokkaa kaikki ulkoiset työkalut, jos lähdetekstin pituus ylittää 200 merkkiä (`SourceSufficiencyThreshold.MIN_CHARS`). Tämä estää Tavily-haut kokonaan pitkillä dokumenteilla.
**Change:** Muutetaan `execute_tool_loop`-funktiota (rivi 276-299) siten, että `is_source_sufficient`-tarkistus ohitetaan, kun `allowed_tools`-listassa on nimenomaisesti `mcp_tavily_search`. Näin Faktantarkistaja saa tehdä hakuja vaikka dokumentti olisi kuinka pitkä.

### Fix 2: Falsifier-stepin Tavily-oikeudet (seed_data.json)
**File:** `backend_v2/seed/seed_data.json`
**Status:** ❌ Tekemättä
**Problem:** Tietokannassa Falsifier-step (`sp_6f40b964895c426b`, rivi 8127) on konfiguroitu `"allowed_mcp_tools": []` — se ei saa koskaan käyttää Tavily-hakua. Ainoa step, jolla on Tavily-oikeus, on Faktantarkistaja (`sp_76eedbc020274f66`, rivi 8515). Falsifier ei siis koskaan pääse tekemään vastaväitehakuja verkosta, vaikka se olisi arkkitehtuurin kannalta oleellista.
**Change:** Lisätään `"mcp_tavily_search"` Falsifier-stepin `allowed_mcp_tools`-listaan.

### Fix 3: Global Audit Trail Consolidation
**File:** `backend_v2/hooks/synthesis.py`
**Status:** ❌ Tekemättä (osittain toteutettu)
**Problem:** Synthesis-hookin "Järjestelmän Tarkastusloki" -osio (rivit 756-780) kerää vain `audit_traces`-muuttujasta, joka sisältää ainoastaan loppusynteesin aikana tehdyt haut. Se ei poimi kaikkia aiemmissa Map-Reduce-vaiheissa (Faktantarkistaja, Falsifier) kerättyjä `MCPAuditTrace`-tietueita, jotka on tallennettu `FrozenContext.mcp_tool_audit`-listaan.
**Change:** Laajennetaan logiikkaa hakemaan myös execution-tason `frozen_context.mcp_tool_audit`-tiedot ja yhdistämään ne synteesin omien audit-jälkien kanssa ennen Alert-blokin generointia.

### Fix 4: Section-Level Brevity Mandate
**File:** `backend_v2/hooks/synthesis.py`
**Status:** ❌ Tekemättä
**Problem:** Taulukon riviselitteillä on tiukka 1 virkkeen sääntö (`EXACTLY ONE short, punchy sentence`, rivi 807), mutta päälaatikoiden (Kognitiivinen syvyys, Yhteenveto jne.) synteesipromptissa (SECTION-LEVEL SYNTHESIS, rivit 647-654) ei ole ehdotonta pituusrajoitusta. Tämä johtaa 4-5 virkkeen lörpöttelyyn.
**Change:** Lisätään promptiin tiukka `CRITICAL BREVITY MANDATE`: "Limit every section summary to an absolute maximum of 2-3 short sentences."

## 4. EPIC 82 Audit: Mitä on jo toteutettu ja mitä ei

### ✅ Toteutettu (EPIC 82):
| # | Kohta | Tiedosto | Todiste |
|---|-------|----------|---------|
| 1 | `MCPAuditTrace` Pydantic-malli | `v2_core.py:581` | Täysi malli: `tool_id`, `query`, `source_urls`, `response_summary`, `timestamp`, `duration_ms` |
| 2 | `FrozenContext.mcp_tool_audit` kenttä | `v2_core.py:1225` | Kerää kaikki ajon aikana tehdyt MCP-kutsut |
| 3 | `ExecutionRecord.mcp_tool_audit` kenttä | `v2_core.py:990` | XAI Evidence Box -renderöintiä varten |
| 4 | Map-Reduce Audit Deduplication | `llm.py:504-546` | Kaikki chunk_workerien audit-tracerit deduplikoidaan `tool_id::query` hashilla ja liitetään `frozen_ctx.mcp_tool_audit`-listaan |
| 5 | `BlueprintTransformer` audit paketointi | `blueprint.py:926-934` | Kerää `frozen_context.mcp_tool_audit`, deduplikoi ja syöttää `ReportDataDTO.mcp_tool_audit`-kenttään |
| 6 | `Workflow.system_audit_trail` boolean | `v2_core.py:1153` + `seed_data.json:7777` | Lippu on päälle kytkettynä tietokannassa (`true`) |
| 7 | Synthesis Audit Trail Alert Block | `synthesis.py:756-780` | Generoi "Järjestelmän Tarkastusloki" -AlertBlockin PDF:ään, **mutta vain loppusynteesin audit-traceista** |
| 8 | Flutter `MCPToolAuditDTO` model | `report_data_dto.dart:102` | Freezed+JsonSerializable malli: `toolId`, `query`, `sourceUrls`, `responseSummary` |
| 9 | Flutter `XAIEvidenceBox` widget | `xai_evidence_box.dart` | Renderöi audit-tracet UI:ssa, kun `mcpToolAudit.isNotEmpty` |
| 10 | Flutter `ReportRendererWidget` integraatio | `report_renderer_widget.dart:65-66` | Kutsuu `XAIEvidenceBox` automaattisesti |
| 11 | Faktantarkistaja (`sp_76eedbc020274f66`) Tavily-oikeus | `seed_data.json:8515` | `"allowed_mcp_tools": ["mcp_tavily_search"]` |

### ❌ Tekemättä (EPIC 82 → siirretty EPIC 85:een):
| # | Kohta | Ongelma |
|---|-------|---------|
| A | Source Sufficiency Gate blokkaa Tavily-haut | `is_source_sufficient()` estää kaikki haut yli 200 merkin dokumenteilla → Fix 1 |
| B | Falsifier ei saa käyttää Tavily-hakua | `allowed_mcp_tools: []` → Fix 2 |
| C | Audit Trail kerää vain synteesin omat haut | Ei hae aiempien vaiheiden auditeja → Fix 3 |
| D | Section-tason synteesit liian pitkiä | Ei tiukkaa pituusrajoitusta → Fix 4 |
| E | Toteutustapa B (Flutter): Falsification-linkitys | `FALSIFICATION`-laajennuksen yhteyteen ei vielä renderöidä "Faktantarkistettu lähteistä:" -tägiä `source_urls`-datalla (EPIC 82 §3 Toteutustapa B). Tämä on **matalan prioriteetin** UI-tehtävä, koska XAIEvidenceBox renderöi jo globaalin audit-lokin. |

## 5. Future Additions
*(This Epic serves as a rolling container for similar small execution refinements and prompt hardening tasks.)*
