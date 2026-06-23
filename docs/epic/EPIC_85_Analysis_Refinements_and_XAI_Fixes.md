# Epic 85: Analysis Refinements, XAI Fixes, and Synthesis Brevity

## 1. Background
Several interconnected issues were discovered during execution monitoring regarding the Explainable AI (XAI) output, system audit trails, and the length of generated synthesis texts.

## 2. Objective
Implement minor but critical architectural refinements to ensure external tools can run when requested, all audit traces are collected, text synthesis is kept strictly concise, and the remaining EPIC 82 items are completed.

## 2.5 Architectural & Hardening Directives
**CRITICAL:** Kun näitä Epic 85:n korjauksia toteutetaan koodiin (Tier 2 -vaiheessa), toteutuksen **TÄYTYY** noudattaa tiukasti `c:\src\quorum\scripts\hardening.xml` -tiedostossa määriteltyjä arkkitehtuurisääntöjä. 

Erityisesti nämä kohdat on pidettävä mielessä koodia muutettaessa:
- **Ei `.get("key", default)` -hakkerointeja:** Kaikki uusi logiikka on vietävä tiukasti Pydanticin ja Fail-Fast -protokollan (RFC 7807) kautta (Säännöt 1, 3, 22).
- **Poikkeusten hallinta:** Ei `except Exception: pass` tai regex-hätäkorjauksia (Säännöt 17, 20). Hallusinaatiot ratkaistaan itsekorjautuvalla silmukalla tai arkkitehtuurin säännöillä.
- **Strict-tyypitykset ja Pydantic:** Koodissa ei saa heikentää olemassa olevia Pydantic-skenaarioita (Säännöt 84, 91).
- **Jumalakoodin välttäminen (SRP & Pienet tiedostot):** Koodin paisuminen "God-metodeiksi" tai satojen rivien tiedostoiksi on ehdottomasti kielletty. Monimutkainen logiikka (esim. uusi itsekorjautuva silmukka) **täytyy** jakaa pieniin, erillisiin ja testattaviin apufunktioihin Single Responsibility -periaatteen mukaisesti (Sääntö 88).
*(Huom. Hardening.xml sisältää sääntöjä, jotka kieltävät tiettyjen rakenteiden tai tiedostojen editoinnin, kuten "Architecture Lock" tai "Schema Freeze". Nämä "älä editoi" -säännöt EIVÄT ole nyt voimassa, sillä Epic 85 nimenomaan vaatii näiden rakenteiden muuttamista ja parantamista. Pelkät koodin laatusäännöt ja fail-fast -periaatteet sen sijaan pysyvät ehdottomina).*

## 3. Implementation Plan

### Fix 1: Source Sufficiency Gate Bypass
**File:** `backend_v2/services/mcp/mcp_tool_loop.py`
**Status:** ✅ Tehty
**Problem:** `is_source_sufficient()` (rivi 94-108) blokkaa kaikki ulkoiset työkalut, jos lähdetekstin pituus ylittää 200 merkkiä (`SourceSufficiencyThreshold.MIN_CHARS`). Tämä estää Tavily-haut kokonaan pitkillä dokumenteilla.
**Change:** Muutetaan `execute_tool_loop`-funktiota (rivi 276-299) siten, että `is_source_sufficient`-tarkistus ohitetaan, kun `allowed_tools`-listassa on nimenomaisesti `mcp_tavily_search`. Näin Faktantarkistaja saa tehdä hakuja vaikka dokumentti olisi kuinka pitkä.

### Fix 2: Falsifier-stepin Tavily-oikeudet (seed_data.json)
**File:** `backend_v2/seed/seed_data.json`
**Status:** ✅ Tehty
**Problem:** Tietokannassa Falsifier-step (`sp_6f40b964895c426b`, rivi 8127) on konfiguroitu `"allowed_mcp_tools": []` — se ei saa koskaan käyttää Tavily-hakua. Ainoa step, jolla on Tavily-oikeus, on Faktantarkistaja (`sp_76eedbc020274f66`, rivi 8515). Falsifier ei siis koskaan pääse tekemään vastaväitehakuja verkosta, vaikka se olisi arkkitehtuurin kannalta oleellista.
**Change:** Lisätään `"mcp_tavily_search"` Falsifier-stepin `allowed_mcp_tools`-listaan.

### Fix 3: Global Audit Trail Consolidation
**File:** `backend_v2/hooks/synthesis.py`
**Status:** ✅ Tehty
**Problem:** Synthesis-hookin "Järjestelmän Tarkastusloki" -osio (rivit 756-780) kerää vain `audit_traces`-muuttujasta, joka sisältää ainoastaan loppusynteesin aikana tehdyt haut. Se ei poimi kaikkia aiemmissa Map-Reduce-vaiheissa (Faktantarkistaja, Falsifier) kerättyjä `MCPAuditTrace`-tietueita, jotka on tallennettu `FrozenContext.mcp_tool_audit`-listaan.
**Change:** Laajennetaan logiikkaa hakemaan myös execution-tason `frozen_context.mcp_tool_audit`-tiedot ja yhdistämään ne synteesin omien audit-jälkien kanssa ennen Alert-blokin generointia.

### Fix 4: Section-Level Brevity Mandate
**File:** `backend_v2/hooks/synthesis.py`
**Status:** ✅ Tehty
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
| F | XAI-laajennusten mielivaltainen leikkaus | `synthesis.py` leikkaa yli `max_items` menevät XAI-havainnot pois täysin sokeasti → Fix 5 |

## 5. Future Additions

### Fix 5: Intelligent XAI Extension Curation (LLM Curation & Reduction)
**File:** `backend_v2/hooks/synthesis.py`
**Status:** ❌ Pending
**Problem:** Currently, `synthesis.py` collects the XAI highlights produced in the Map phase and blindly slices them in Python using `items[:max_items]`. This causes critical/actionable insights to be lost randomly, and duplicate highlights to leak to the UI.
**Change (LLM Arch Compliant):**
1. Collect all raw XAI highlights *before* the main LLM synthesis call.
2. Inject the gathered highlights as a `<raw_extensions>` XML tag inside the `user` message to respect the `ephemeral_caching_topology` prompt caching guidelines.
3. Add a static rule in the system prompt instructing the model to curate, deduplicate, and select highlights up to the `<max_extension_items>` limit.
4. Place the dynamic limit variable `<max_extension_items>{max_items}</max_extension_items>` inside the `<execution_parameters>` block in the system prompt.
5. The LLM returns curated highlights directly in `result.xai_highlights` (which is a list of `XaiHighlightItem` in `SynthesisOutputDTO`), and the blind Python slicing is completely removed.

### Fix 6: Unified Dynamic Tone & Language Maintenance (Kielihuoltopesula)
**File:** `backend_v2/hooks/synthesis.py`
**Status:** ❌ Pending
**Problem:** Currently, Matrix Summary uses a hardcoded "Human-Centric Focus" rule in `row_exp_prompt` while XAI highlights lack consistent tone alignment. Furthermore, database models lack a field to configure this dynamic tone instruction, presenting a schema and data seeding discrepancy.
**Change:**
1. **Schema Extension:** Add `tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")` to `SynthesisConfigDTO`, `EmbeddedOutputProfile`, and `OutputProfile` in `backend_v2/models/v2_core.py`, as well as `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO` in `backend_v2/models/dtos/output_profile.py`.
2. **DB Seed Updates:** Add `"tone_instruction"` fields to profiles in `backend_v2/seed/seed_data.json` to allow local re-seeding.
3. **Unification:** Remove the hardcoded "Human-Centric" rules. Resolve the dynamic tone configuration `tone_text = synthesis_cfg.tone_instruction.resolve(language)` and inject it dynamically into the system instructions for both the global synthesis (`sys_prompt`) and the row explanations (`row_exp_prompt`).

### Fix 7: Tavily Hallucination Remediation (Physical Anchoring & Contextual Override)
**File:** `backend_v2/services/mcp/mcp_tool_loop.py`
**Status:** ❌ Pending
**Problem:** The current physical anchoring check in `mcp_tool_loop.py` uses a raw `claim not in source_context` substring check. This check is highly brittle, failing on minor casing, spacing, or unicode accent differences. Furthermore, physical verification is enforced even when `strictness_level < 100` (which allows indirect quotes/contextual override).
**Change:**
1. Replace `claim not in source_context` with a call to the normalized `AnchorValidationService.strict_match(source_context, [claim])` which handles normalization, casing, and accent differences robustly.
2. Read the strictness level from `validation_context.get("strictness_level")`. If it is less than 100, bypass the physical substring verification entirely for Phase 0 citation extraction, enabling indirect/paraphrased queries.

### Fix 8: Deterministic Ensemble Extraction (Kappa Score Maximization)
**File:** `backend_v2/services/mcp/mcp_tool_loop.py`
**Status:** ❌ Pending
**Problem:** A single LLM call is executed to perform citation extraction in Phase 0. Natural LLM variance causes low Kappa score consistency. Furthermore, token usage of Phase 0 is discarded, violating the FinOps token tracking mandate.
**Change:**
1. Wrap the Phase 0 citation extraction in an `asyncio.TaskGroup` to run **3 times in parallel** (Best-of-3 ensemble).
2. Protect each call with `try-except` blocks to survive single-call transient errors.
3. Perform a majority vote: keep claims whose normalized forms appear in >= 2/3 of successful runs (or >= 2/2 if one fails, or >= 1/1 if two fail).
4. Accumulate and track token usage of all ensemble calls in Phase 0 plus Phase 2, ensuring complete FinOps audit trails.

### Fix 9: Agentic Self-Reflection Loop (SOTA RAG Architecture)
**File:** `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py` / `mcp_tool_loop.py`
**Status:** ❌ Pending
**Problem:** Minor mechanical errors or formatting differences in LLM citations trigger `SemanticEvidenceError` in physical anchoring, discarding valid evidence.
**Change:**
1. Define the `CitationCorrectionResult` Pydantic model in `backend_v2/models/domain/mcp.py` to capture corrected claim text.
2. Catch `SemanticEvidenceError` in `execute_tool_loop` for strictness=100.
3. Invoke a fast self-correction LLM task using a static system instruction (`_SELF_CORRECTION_SYSTEM_INSTRUCTION`) to locate and return the exact physical substring from the source context.
4. If corrected successfully, update the citation with the corrected string. If correction fails, raise `SemanticEvidenceError`.

## 6. Verification and Seeding Plan

### Database Seeding
To persist the new `tone_instruction` dynamic fields in the output profiles, run the local seeding script:
```powershell
uv run python backend_v2/seed/run_seed.py local
```

### Automated Testing Strategy
1. **Unit Tests:**
   - Add new tests in `backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py` to verify the ensemble vote consensus logic, contextual override (skipping physical check when strictness < 100), and the agentic self-reflection loop.
   - Add new tests in `backend_v2/tests/unit/hooks/test_synthesis.py` to verify the dynamic tone injection into `sys_prompt` and `row_exp_prompt`, and the LLM curation of raw XAI highlights.
2. **Quality Gates:**
   - Enforce the Universal Quality Gate using the backend audit loop tool:
     ```powershell
     uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test
     uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/mcp_tool_loop.py --test
     uv run python scripts/backend_audit_loop.py backend_v2/hooks/synthesis.py --test
     ```

