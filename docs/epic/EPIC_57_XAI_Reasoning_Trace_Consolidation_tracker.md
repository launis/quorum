# Epic 57 Master Tracker: XAI Reasoning Trace Consolidation

Tämä seurantadokumentti (Tracker) valvoo **Epic 57** -suunnitelman vaiheittaista suoritusta. Epicin tavoitteena on yhdistää deterministiset mekaaniset esikoukut ja laadulliset semanttiset asiantuntija-agentit yhdeksi yhtenäiseksi Explainable AI (XAI) -päättelyketjuksi, laskea ristiinvertailulla mekaanisen todellisuuden ja kognitiivisen arvion välinen varianssi (Mechanical-Cognitive Variance) ja esittää se tyylikkäästi käyttöliittymässä sekä PDF-raporteissa.

## Jatkuva Suorituskierto (Continuous Execution Loop)

Suorita jokainen vaihe järjestyksessä. Kun olet suorittanut vaiheen loppuun, päivitä sen tila muotoon `[OK]` ja siirry seuraavaan.

- [NOK] docs/epic/tasks_EPIC_57/phase1_domain_models.md - Domain Models & Variance Calculation Engine
- [NOK] docs/epic/tasks_EPIC_57/phase2_prompt_grounding.md - Context Compiler & Prompt XML Grounding
- [NOK] docs/epic/tasks_EPIC_57/phase3_xai_reporter_synthesis.md - XAI Reporter Agent Integration
- [NOK] docs/epic/tasks_EPIC_57/phase4_frontend_pdf.md - Frontend SDUI & PDF Report Parity

---

## Universal Hardening Loop Mandate
Ennen kuin merkitset Epicin kokonaan valmiiksi, aja testaus- ja laadunvarmistuskierros:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

---

## Handover-ohjeet (Handover Instructions)
Aloittaaksesi suorituksen fresh-ikkunassa:
1. Avaa uusi puhtaan tilan keskusteluikkuna.
2. Aja käynnistyskomento: `/tier5-resume --target docs/epic/EPIC_57_XAI_Reasoning_Trace_Consolidation_tracker.md`
