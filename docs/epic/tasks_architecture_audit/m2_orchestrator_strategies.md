# Epic 40 — M2: Orchestraattoristrategioiden Dokumentointi

## Goal
Auditoida `backend_v2/services/orchestrator/strategies/` koko kerros ja kirjoittaa puuttuva dokumentaatio `docs/architecture/`-hakemistoon. Strategiakerros on **täysin dokumentoimaton** tällä hetkellä. Koodi on totuus.

## Scope
- **TARGET (Modify/Create):** `docs/architecture/03_business_services_and_dag.md` (uusi osio) TAI uusi tiedosto `docs/architecture/03b_orchestrator_strategies.md`
- **CONTEXT (Read-Only):**
  - `backend_v2/services/orchestrator/strategies/base.py`
  - `backend_v2/services/orchestrator/strategies/llm.py`
  - `backend_v2/services/orchestrator/strategies/logic.py`
  - `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`
  - `backend_v2/services/orchestrator/dag_executor.py` (viitekonteksti)
  - `backend_v2/services/orchestrator/prompt_compiler.py` (viitekonteksti)

## Tunnetut puutteet (löydetty audit-sessiossa 2026-04-26)

### `base.py` — `BaseNodeStrategy`
- Pre/post-hook execution loop (`run_pre_hooks`, `run_post_hooks`)
- `HookState` injektio ja `HookDependencies` rakenne
- Fail-Fast: `logger.warning` ennen poikkeusten heittoa

### `llm.py` — `LLMNodeStrategy`
- Map-Reduce orkestraatio ChunkingServicen kautta
- `schema_map` rakentaminen (`category_id == "matrix"` lookup)
- PromptBlock validointi — Fail-Fast, ei duck-typing
- `build_schema_map_loop` logiikka

### `logic.py` — `LogicNodeStrategy`
- Hook name lookup hook_registrystä
- `$inputs` / `$steps` evaluointi
- Fail-Fast: `logger.error` + `AppException`

### `context_builder.py`
- Uusi `schema_map`-pohjainen suodatusmalli (ei enää OPAQUE_BLOCK_ID_RE regex)
- `reasoning_trace` passthrough -logiikka (metadata ei validoida)
- `_process_trace_event` arkkitehtuuri

## Implementation Steps
1. Lue kaikki scope-tiedostot `view_file`-työkalulla
2. Dokumentoi löydökset — mitä kukin tiedosto tekee, mitkä design-päätökset
3. Kirjoita uusi dokumentaatio-osio (uusi §5 `03_business_services_and_dag.md`:aan TAI uusi `03b_`-tiedosto)
4. Esitä diff käyttäjälle hyväksyttäväksi

## Verification
- Ei Python-koodimuutoksia
- Dokumentaatio on teknisesti täsmällinen koodiin nähden
- Jokainen design-päätös (Fail-Fast, schema_map, reasoning_trace passthrough) perustellaan
