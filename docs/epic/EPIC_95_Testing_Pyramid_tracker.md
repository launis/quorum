# EPIC 95: Testing Pyramid & API Parity Tracker

## Tavoite
Saattaa Quorum V2 laatu tuotantovalmiiksi, korjata Tier 0 auditissa löytynyt `ReportDataDTO` vs `ReportDataV2DTO` API-ristiriita ja rakentaa testauspyramidi.

## Session Handover Context
- **Achieved:** Tier 2 Hardening Loop completed for 5 files in `backend_v2/services/orchestrator/`: `atomizer.py`, `chunk_accumulator.py`, `chunking_service.py`, `context_router.py`, `dag_compiler.py`.
- **Learned:** All 5 files are natively compliant with Phase 9 Fail-Fast constraints. No architectural violations were found. Coverage targets were met.
- **Remaining:** Tier 2 Hardening Loop for the remaining files in `backend_v2/services/orchestrator/` (dag_executor.py, enriched_dag_executor.py, extraction_schema_factory.py, extractive_sensor_service.py, graph_validator.py, etc.). Pre-Delete Audit and Baseline Parity Audit.

## Tehtävät (Tasks)

- [OK] **Phase 1: API Contract Synchronization**
  - Tiedosto: `docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_1_plan.md`
  - Kuvaus: Korjataan Pydanticin ja Dartin välinen DTO-yhteensopimattomuus.

- [OK] **Phase 2: Backend Unit & Integration Tests (Hardening)**
  - Tiedosto: `docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_2_plan.md`
  - Kuvaus: Korjataan/poistetaan 192 rikkinäistä testiä ja taataan DAG-moottorin integraatiotestit.

- [OK] **Phase 3a: Backend E2E Golden Master (NA_CARD Cascade)**
  - Tiedosto: `docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_3a_backend_e2e.md`
  - Kuvaus: Lisää `SduiNACard` SDUI-malleihin ja rakenna `test_epic_chain_e2e.py` E2E-testi N/A kaskadille.

- [OK] **Phase 3b: Frontend E2E UI Parity**
  - Tiedosto: `docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_3b_frontend_snapshot.md`
  - Kuvaus: Varmista `n_a_card` -komponentin renderoituminen Flutterissa (harmaa teema, short_circuit_reason_tda_ids näkyvyys) snapshot-testeillä.

- [NOK] **Tier 2 Hardening**
  - Ohje: Aja Tier 2 Hardening Loop (esim `/tier2-hardening-backend`) kohdistettuna `backend_v2/models/` ja `backend_v2/services/orchestrator/` -hakemistoihin varmistamaan Pydantic V2 säännökset.

- [NOK] **Pre-Delete Audit**
  - Ohje: Poista vanhentuneet legacy-testit lopullisesti (Zero Behavioral Change verifioituna).

- [NOK] **Baseline Parity & Zero-Loss Audit**
  - Ohje: Varmista pytest coverage testin avulla, että kaikki moottorin uudet ominaisuudet ovat täysin testattuja ja testien kokonaismäärä/kattavuus vastaa odotuksia, eikä liiketoimintalogiikkaa kadonnut.

## Instructions for the Execution Agent
Tämä on master-tracker Epic 95:lle. Etene yksi tehtävä kerrallaan tiukassa järjestyksessä.
Jos kohtaat bugeja Phase 1/2 aikana, ratkaise ne Tier 4:llä ja palaa trackeriin.

To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found below.

```
/tier5-resume --workflow=/tier2-execute --target="docs\epic\EPIC_95_Testing_Pyramid_tracker.md, docs\epic\EPIC_95_Testing_Pyramid.md" --rules="00-antigravity-core.md, 01-python-backend.md, 02_flutter_desktop.md"
```
