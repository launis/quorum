# Phase 2: Syvä-atomisointi ja Obfuskointi (Kerta-ajo / Design-Time)

## Objective
Toteutetaan Kääntäjä-AI -logiikka, joka ajetaan vain kerran tallennusvaiheessa (Design-Time). Tekoäly lukee asiantuntijan promptin (1-2 lausetta per BARS-taso) ja räjäyttää sen 15 erilaiseksi mikro-atomiksi (yhteensä 75 per matriisi) poistaen domain-spesifin sanaston (Obfuskointi) ja luoden "Scaffolded" poikkeusmekanismit erikoissanoille.

## TARGET (Modify)
- `backend_v2/services/studio.py` (Tallennuslogiikka ohjaa Kääntäjä-AI tilaan ennen DB-commitia)
- `backend_v2/llm/client.py` tai uusi arkkitehtoninen kääntäjä-työkalu
- `backend_v2/seed/seed_data.json` (Seed-tietokannan rakenne matriisien tallennukseen kera `micro_atoms` kenttien)

## CONTEXT (Read-Only)
- `backend_v2/models/v2_core.py` (Rakenne)
- `backend_v2/services/orchestrator/prompt_compiler.py`

## Architectural Constraints (V2 Sequence)
1. **Dependencies:** Hyödynnetään yksinomaan keskitettyä `LLMClient.from_strategy()` reititystä Kääntäjä-AI:lle. 
2. **Pydantic Models:** Uudet JSON Object / Boolean listat Pydantic V2 läpi. `extra="forbid"`.
3. **Repo -> API:** Tämä tapahtuu kertaalleen arviointikriteerin tallennus/rakennusvaiheessa omana async työnkeruuna tai lukittuna tallennusprosessina ennen Seed Vault hyväksyntää.

## Design / Implementation specifics
* Järjestelmä hakee Matrixin (`PromptBlock`) alkuperäiset kriteerit, kutsuu Kääntäjä-AI:ta (`run_structured_task`) ja vaatii Pydantic Strict V2 muodossa arrayn atomeita.
* Atomien generoinnissa käytetään *Rubric-CoT* -teemallista vaatimusta (AI kirjoittaa auki miten atomi perustuu alkuperäiseen rubricsiin torjuakseen Context Driftiä).
* Lopulliset Atomit tallennetaan tietokantaan osaksi arviointiprofiilia eikä niitä koskaan muuteta runtimessa.

## Verification & Quality Gate Plan
* Unit testi Kääntäjä-AI hookille/servicelle: `backend_v2/tests/unit/test_atomization.py`.
* LLM testaamiseen: Täydellinen `mock_data.py` json-fixtuuria hyödyntäen estämään ulkoiset kutsut (`Rule: mocking_mandate_for_llm`).
* Komento: `uv run python scripts/backend_audit_loop.py backend_v2/services/studio.py --test`
