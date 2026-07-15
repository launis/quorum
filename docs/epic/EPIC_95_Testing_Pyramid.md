# Epic 95: Quorum V2 Testing Pyramid & API Parity Verification

> [!CAUTION]
> **TIER 0 AUDIT CATASTROPHIC FINDING:** Ennen testauspyramidin rakentamista on korjattava koodikannasta löytynyt massiivinen API-ristiriita. 
> - **Python Backend (`v2_core.py`):** `ReportDataDTO` käyttää edelleen vanhaa rakennetta (`evaluative_matrices`, `layouts`, `MatrixScorecardRowDTO`). Se ei palauta Epic 91.5:n vaatimaa litteää `results` + `hydrated_references` -rakennetta. `AtomResultDTO` ja `HydratedAtomDTO` puuttuvat täysin backendistä.
> - **Flutter Frontend (`client_app_v2`):** Epic 94:n mukaisesti UI käyttää `ReportDataV2DTO`:ta, joka odottaa Pydantic V2 -mukaista litteää listaa (`AtomResultDTO`, `HydratedAtomDTO`).
> - **Tulos:** Frontin ja Backin välinen Data Contract on rikki. Backendin e2e-testit (192 virhettä) kaatuvat tähän epäjohdonmukaisuuteen.

## 1. Yhteenveto ja Tavoite (Objective)
Tämän Epicin tavoitteena on saattaa Quorum V2:n laatu ja testikattavuus tuotantovalmiiksi. Epic 95 ei tuota uusia ominaisuuksia, vaan rakentaa **Testauspyramidin (Testing Pyramid)**, joka matemaattisesti todistaa, että Epic 91.5 (DTO Bridge), 92 (DAG Moottori), 93 (SDUI) ja 94 (Flutter) toimivat virheettömästi yhteen Single Source of Truth -arkkitehtuurissa.

## 2. Testauspyramidin Tasot (Testing Pyramid)

### 2.1 Taso 1: API Contract & Domain Model Parity (Unit Tests)
Koska havaitsimme Tier 0 -auditissa API-ristiriidan, järjestelmään on rakennettava staattinen varmistus sille, että Pydantic V2 -mallit ja Dart 3 Freezed -mallit pysyvät 100% synkronissa.
- **Fail-Fast -pakotus:** `backend_v2/tests/unit/models/test_contract_parity.py` -testin on ladattava Dart-koodin json-skeemat (tai vast.) ja verrattava niitä Pydantic-malleihin (`ReportDataDTO`, `ReportDataV2DTO`).
- Korjataan `v2_core.py` ja frontendin DTO:t vastaamaan samaa yhtenäistä datamallia.

### 2.2 Taso 2: DAG Moottorin Eristetty Testaus (Integration Tests)
TopologicalEvaluatorin ja TaskGroupin on toimittava deterministisesti riippumatta LLM:n vastauksista.
- **Kattavuus:** `test_topological_evaluator.py` ja `test_dag_executor.py` on saatava täysin vihreiksi.
- Syklinmurtajan (Cycle Breaker), Oikosulkukaskadin (N/A Propagation) ja `SYSTEM_ERROR` -tilojen propagointi on todennettava ilman mockattuja API-verkkoja.

### 2.3 Taso 3: Golden Master End-to-End (E2E Tests)
Varmistetaan kokonaisvaltainen putki: `seed_data.json -> DAG Run -> ReportDataDTO -> SDUI Mapper -> ReportView / Flutter Widget Tree`.
- Olemassa olevien 192 kaatuvan testin puhdistus. Orvot testit deletoidaan säälimättä (Zero-Tolerance legacy-koodille), ja niiden tilalle tuodaan uusi `test_epic_chain_e2e.py`.
- **UI/UX Näkökulma:** Tämän E2E-testin on todistettava, että jos `AtomResultDTO` menee tilaan `N_A`, se näkyy Flutterissa harmaana `N_A_CARD` -komponenttina, ja sen `short_circuit_reason_tda_ids` esitetään käyttäjälle ymmärrettävässä muodossa.

## 3. Toimeenpanosuunnitelma (Phases)

### Phase 1: API Contract Synchronization
- **Tavoite:** Ratkaistaan Tier 0 -auditin löydös. Python-backendin ja Flutterin DTO-mallien yhtenäistäminen.
- **UX/UI:** Tämä on näkymätön infratason muutos, mutta se estää UI:n Null-Pointer -kaatumiset kokonaan (`disallowUnrecognizedKeys: true`).

### Phase 2: Backend Unit & Integration Tests (Hardening)
- **Tavoite:** 100% testikattavuus DAG-moottorille ja kognitiivisen tilan validaattoreille. Kaikki 192 kaatuvaa testiä korjataan tai poistetaan.
- **Fail-Fast:** Varmistetaan, että `strict=True` ja `extra='forbid'` ovat päällä kaikkialla ja testit räjähtävät heti, jos väärää dataa syötetään.

### Phase 3: Golden Master E2E & UI Parity
- **Tavoite:** Kokonaisputken automaatiotestaus. `seed_data.json` syötetään järjestelmään, ja ulos täytyy tulla täsmälleen odotettu SDUI-puu.
- **UX/UI:** Testi generoi lokaalin HTML/PDF-raportin tai SDUI-snapshotin, josta voidaan todentaa, että käännökset (I18nText), XAI-korostukset ja N/A -ohitukset näkyvät oikein.

## 4. Ohjeistus Tier 1 Plannerille
Aja komento `/tier1-planner` tälle tiedostolle. Luo sen perusteella `epic_95_phase_1_tracker.md` ja tarkat tiedostotason `implementation_plan.md` -dokumentit, joissa korjataan ensin Tier 0 -auditissa löytynyt API-ristiriita.
