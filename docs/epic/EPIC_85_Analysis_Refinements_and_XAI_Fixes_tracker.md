# Epic 85: Analysis Refinements, XAI Fixes, and Synthesis Brevity Tracker

This master tracker coordinates the phased execution of the Epic 85 refinements.

## Taustatietoa (Background)

Epic 85 korjaa suoritusseurannassa (execution monitoring) havaittuja ongelmia, jotka liittyvät Explainable AI (XAI) -havaintojen kuratoimiseen, tarkastuslokien (audit trail) kattavuuteen ja synteesitekstien pituuksiin, sekä viimeistelee aiemman EPIC 82:n avoimia asioita.

Lead Architect on arvioinut ja hyväksynyt seuraavat tekniset ja arkkitehtoniset valinnat, joita on noudatettava kaikissa toteutusvaiheissa:
1. **Skeeman laajennus (Fix 6):** Output-profiileihin ja kantaan lisätään dynaaminen sävynohjaus (`tone_instruction`).
2. **Fyysinen ankkurointi (Fix 7):** Korvataan hauraat merkkijonotarkistukset `AnchorValidationService.strict_match` -kutsulla. Jos `strictness_level < 100`, fyysinen substring-ankkurointi ohitetaan Tavily-hauissa, jotta semanttiset haut sallitaan.
3. **Best-of-3 Ensemble & FinOps (Fix 8):** Sitaattien erottaminen (Phase 0) suoritetaan rinnakkain 3 kertaa `asyncio.TaskGroup`-kontekstissa. Lopulliset claims-tiedot valitaan enemmistöäänestyksellä, ja tokenien käyttö summataan FinOps-auditointia varten.
4. **Itsekorjaava silmukka (Fix 9):** Jos ankkurointi pettää strictness-tasolla 100, ajetaan nopea itsekorjaava LLM-tehtävä (`CitationCorrectionResult`) korjaamaan claim-teksti.

## Tarpeellinen taustamateriaali (Reference Material)

Kehittäjäagentin on luettava ja sisäistettävä seuraavat taustatiedot ennen suoritusta:
- **Epic-määrittely:** [EPIC_85_Analysis_Refinements_and_XAI_Fixes.md](file:///c:/src/quorum/docs/epic/EPIC_85_Analysis_Refinements_and_XAI_Fixes.md) (Requirements SSOT)
- **Arkkitehtuurisäännöt:**
  - [AGENTS.md](file:///c:/src/quorum/AGENTS.md) – Pääarkkitehtuurin reunaehdot ja kiellot
  - [.agents/rules/01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md) – Python & Pydantic V2 säännöt (kuten PEP 695 syntaksi, model copy, strict-asetukset)
  - [.agents/rules/05_llm_architecture.md](file:///c:/src/quorum/.agents/rules/05_llm_architecture.md) – LLM-kutsut, ankkurointikoodi, ja ensemble-ohjeet
  - [scripts/hardening.xml](file:///c:/src/quorum/scripts/hardening.xml) – Koodin laatusäännöt (mukaan lukien God-metodien kielto ja SRP)

## Execution Progress

- [OK] [phase1_schema_seeding.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_85_Analysis_Refinements_and_XAI_Fixes/phase1_schema_seeding.md) - Output Profile Schema Extension & Database Seeding (Fix 6 Part 1)
- [OK] [phase2_mcp_tool_loop.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_85_Analysis_Refinements_and_XAI_Fixes/phase2_mcp_tool_loop.md) - MCP Tool Loop Concurrency Ensemble, Overrides, & Self-Correction (Fix 7, 8, 9)
- [OK] [phase3_synthesis_hooks.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_85_Analysis_Refinements_and_XAI_Fixes/phase3_synthesis_hooks.md) - Synthesis Consolidation, Dynamic Tone & XAI Curation (Fix 5, Fix 6 Part 2)


---

## Handover Instructions

To execute this Epic iteratively, start a NEW chat session and run:
```powershell
/tier5-resume --target docs/epic/EPIC_85_Analysis_Refinements_and_XAI_Fixes_tracker.md
```

