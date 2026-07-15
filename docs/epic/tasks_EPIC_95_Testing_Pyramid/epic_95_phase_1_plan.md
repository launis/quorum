# EPIC 95 Phase 1: API Contract Synchronization & Model Parity

## 1. Tavoite (Objective)
Ratkaistaan Tier 0 Auditissa havaittu API-ristiriita Pydantic V2:n (`ReportDataDTO`) ja Dart 3 Freezed -mallien (`ReportDataV2DTO`) välillä. Varmistetaan, että Flutter Frontend saa odottamansa `results` (topologinen lista) ja `hydrated_references` (O(1) välimuisti) rakenteet Backendiltä.

## 2. Arkkitehtuurin Invariantit (Architecture Invariants)
- **00-antigravity-core.md**: Zero Behavioral Change for non-target components.
- **01-python-backend.md**: Strict Pydantic (`strict=True, extra='forbid'`).
- **02_flutter_desktop.md**: `disallowUnrecognizedKeys: true` Freezed-malleissa.

## 3. Toteutettavat muutokset

### TARGET (Modify)
- `backend_v2/models/v2_core.py`
  - **Muutos:** Refaktoroi `ReportDataDTO` vastaamaan Epic 91.5 / Epic 94:n spesifikaatiota:
    - Lisää `results: list[AtomResultDTO]` (Tulee vaatimaan `AtomResultDTO` luonnin Pydanticiin Epic 91.5 mukaisesti).
    - Lisää `hydrated_references: dict[str, HydratedAtomDTO]`.
    - Poista / Siirrä vanhat `evaluative_matrices` ja `layouts` -kentät, jos ne eivät kuulu uuteen rajapintaan (tai pidä väliaikaisesti UI-migraatiota varten deprekoituina, mutta uudet kentät on saatava).
- `backend_v2/services/execution.py` & `backend_v2/services/sdui_mapper_service.py`
  - **Muutos:** Varmista, että nämä palvelut tuottavat tai kuluttavat uutta DTO-rakennetta oikein, jotta FastAPI rajapinta vastaa Frontendin huutoihin.
- `backend_v2/tests/unit/models/test_contract_parity.py` [NEW]
  - **Muutos:** Staattinen Python-testi, joka lukee kovakoodatun Dart-skeeman tai suorittaa rakenteellisen varmistuksen siitä, että Pythonin `ReportDataDTO` ja Dartin `ReportDataV2DTO` ovat kenttätasolla identtiset.

### CONTEXT (Read-Only)
- `client_app_v2/lib/features/execution/models/report_data_v2_dto.dart`
- `docs/epic/EPIC_91_5_DTO_Bridge.md`

## 4. Testaussuunnitelma (Quality Gate)
- Aja uusi `test_contract_parity.py`.
- Aja backend-testit varmistaen, että DTO-muutokset on heijastettu `SduiMapperService`en.

## 5. Session Handover
Tämä suunnitelma suoritetaan Tier 2:n kautta. Kun olet valmis, etene Phase 2:een Trackerin mukaisesti.
