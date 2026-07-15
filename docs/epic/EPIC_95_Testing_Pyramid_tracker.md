# EPIC 95: Testing Pyramid & API Parity Tracker

## Tavoite
Saattaa Quorum V2 laatu tuotantovalmiiksi, korjata Tier 0 auditissa löytynyt `ReportDataDTO` vs `ReportDataV2DTO` API-ristiriita ja rakentaa testauspyramidi.

## Session Handover Context
- **Achieved:** Tier 0 Audit paljasti API-ristiriidan, jossa Python Backendin `ReportDataDTO` käyttää vanhaa rakennetta, ja Flutter Frontend odottaa Epic 91.5:n mukaista litteää `results` + `hydrated_references` -rakennetta. Testaus-Epic 95 luotiin.
- **Learned:** Vanhojen testien mockit ovat vanhentuneita ja aiheuttavat massiivisesti virheitä (192 kpl). SSOT DTO-malli on yhdenmukaistettava Backendin ja Frontendin välillä ennen E2E-testejä.
- **Remaining:** Epic 95 implementointi alla olevien suunnitelmien mukaisesti.

## Tehtävät (Tasks)

- [OK] **Phase 1: API Contract Synchronization**
  - Tiedosto: `docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_1_plan.md`
  - Kuvaus: Korjataan Pydanticin ja Dartin välinen DTO-yhteensopimattomuus.

- [NOK] **Phase 2: Backend Unit & Integration Tests (Hardening)**
  - Tiedosto: `docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_2_plan.md`
  - Kuvaus: Korjataan/poistetaan 192 rikkinäistä testiä ja taataan DAG-moottorin integraatiotestit.

- [NOK] **Invoke Tier 1 Planner for Phase 3**
  - Ohje: "Invoke the Tier 1 Planner again to generate detailed plans for Phase 3 (Golden Master E2E) based on the updated codebase state."

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
