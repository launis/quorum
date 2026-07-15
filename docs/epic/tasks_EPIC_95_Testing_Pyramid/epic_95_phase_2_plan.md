# EPIC 95 Phase 2: Backend Unit & Integration Tests (Hardening)

## 1. Tavoite (Objective)
Varmistetaan 100% testikattavuus DAG-moottorille (Epic 92) ja korjataan/poistetaan 192 rikkoutunutta backend-testiä.

## 2. Arkkitehtuurin Invariantit
- **Fail-Fast**: Kaikki Pydantic-mallit räjähtävät heti datavirheissä.
- **TaskGroup over Gather**: Varmistetaan, että testit generoivat kaskadit ja syklinmurtajat oikein.

## 3. Toteutettavat muutokset

### TARGET (Modify)
- `backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py`
  - **Muutos:** Kattavat yksikkötestit `TopologicalEvaluator`ille. Varmistetaan `N_A`, `BLOCKED`, `SYSTEM_ERROR` kaskadien oikea toiminta ja syklin tunnistaminen.
- `backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`
  - **Muutos:** Kattavat yksikkötestit TaskGroup-moottorille, DLQ-reititykselle ja semaforille.
- `backend_v2/tests/` (Laajempi puhdistus)
  - **Muutos:** Deletoidaan orvot testit (esim. vanhoja `scoring.py` tai legacy pipeline B testejä), jotka ovat arkkitehtuurisesti vanhentuneita eikö niitä kuulu enää tekohengittää.

### CONTEXT (Read-Only)
- `backend_v2/services/orchestrator/topological_evaluator.py`
- `backend_v2/services/orchestrator/dag_executor.py`

## 4. Testaussuunnitelma (Quality Gate)
- Suorita `uv run pytest backend_v2/tests/unit/services/orchestrator/` -varmista 100% pass rate näissä moottoritesteissä.
- Base-level metric: 192 errors pitää saada laskemaan nollaan (poistamalla orvot, korjaamalla elävät).

## 5. Session Handover
Tämä suunnitelma suoritetaan Tier 2:n kautta. Kun olet valmis, etene Phase 3:een.
