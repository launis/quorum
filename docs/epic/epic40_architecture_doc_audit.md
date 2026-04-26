# Epic 40: Arkkitehtuuridokumentaation Auditointi (Doc Sync Audit)

## Tausta

Tämä epic kattaa `docs/architecture/` -dokumenttien systemaattisen auditoinnin ja päivityksen vastaamaan nykyistä koodipohjaa (`backend_v2/` + `client_app_v2/`). Auditointi on jaettu 7 milestoneen, joista kukin käsittelee yhtä arkkitehtuurilohkoa.

**Periaate: Koodi on totuus. Dokumentaatio seuraa koodia, ei toisinpäin.**

Aiemmin päivitetyt (sessio 2026-04-26):
- ✅ `04_hooks_and_llm.md` — synthesis.py + reporting.py detail
- ✅ `08_dynamic_rendering_engine.md` — Token Shield fix + SDUI §6

---

## Milestone-järjestys (Prioriteettijärjestys)

| # | Milestone | Kohde-doc | Prioriteetti |
|---|---|---|---|
| M2 | Orchestrator Strategiat | uusi `03b` tai `03`-laajennus | 🔴 Kriittinen |
| M1 | Backend Services Layer | `03_business_services_and_dag.md` | 🔴 Kriittinen |
| M3 | Domain Models | `02_domain_models.md` | 🟠 Korkea |
| M4 | Hooks & LLM täydennys | `04_hooks_and_llm.md` | 🟠 Korkea |
| M5 | Flutter Client | `06_desktop_first_flutter_client.md` | 🟡 Keskitaso |
| M6 | Persistointi & Infra | `05_` + `07_` | 🟡 Keskitaso |
| M7 | API & Core Registry | `01_backend_api_and_core.md` | 🟢 Matala |

---

## M2: Orchestrator Strategiat (KRIITTINEN — Ei dokumentaatiota)

**Kohde:** Uusi dokumenttilohko tai `03_business_services_and_dag.md` laajennusosio  
**Koodipolku:** `backend_v2/services/orchestrator/strategies/`

### Tarkistettavat tiedostot:
- `strategies/base.py` — `BaseNodeStrategy`, pre/post-hook loop, `HookState` injektio
- `strategies/llm.py` — `LLMNodeStrategy`: Map-Reduce, schema_map, PromptBlock validointi
- `strategies/logic.py` — `LogicNodeStrategy`: hook name lookup, `$inputs`/`$steps`
- `strategies/llm_execution/context_builder.py` — schema_map-pohjainen suodatus, reasoning_trace passthrough
- `strategies/llm_execution/prompt_factory.py` — olemassaolo ja rooli

### Vaiheet:
1. Lue kaikki tiedostot
2. Tunnista puuttuvat dokumentointikohdat
3. Kirjoita uusi osio tai tiedosto

---

## M1: Backend Services Layer

**Kohde:** `03_business_services_and_dag.md`  
**Koodipolku:** `backend_v2/services/`

### Kokonaan puuttuvat palvelut:
- `chat_parser.py`, `localization.py`, `flattener.py`, `progress.py`
- `pii_analyzer.py`, `usage_service.py`, `drivers/`
- `orchestrator/atomizer.py`, `orchestrator/chunk_accumulator.py`, `orchestrator/context_router.py`

### Puutteelliset kuvaukset:
- `dag_compiler.py` — ShiftLeft pre-flight details
- `prompt_compiler.py` (38 KB) — Two-Tier schema, Self-Healing citation

---

## M3: Domain Models

**Kohde:** `02_domain_models.md`  
**Koodipolku:** `backend_v2/models/domain/` (31 tiedostoa)

### Tarkistettavat uudet DTOt (Phase 9):
- `models/domain/synthesis.py` — SynthesisStepDataDTO, SynthesisMetadataDTO
- `models/domain/scoring.py` — StrictMatrixPayload, LightweightMatrixOutput
- `models/domain/xai.py` — Discriminated Union XAIExtensionPayload

---

## M4: Hooks & LLM Täydennys

**Kohde:** `04_hooks_and_llm.md`  
**Koodipolku:** `backend_v2/hooks/`, `backend_v2/llm/`

### Puutteelliset hookit:
- `atom_flattening.py` — MD5 content-addressable ID, sokkoarviointi
- `context_mapper.py` — build_ordinal_mapping API
- `references.py` — onko edelleen stub?
- `llm/provider.py` (44 KB) — retry-jäähylogiikka, streaming modet

---

## M5: Flutter Client

**Kohde:** `06_desktop_first_flutter_client.md`  
**Koodipolku:** `client_app_v2/lib/`

### Puuttuvat:
- `features/execution/views/` — 6 näkymätiedostoa
- `features/studio/` — DAG editor, PromptBlock editori
- `shared/widgets/` — AppExceptionBoundary, MatrixObservabilityAccordion

---

## M6: Persistointi & Infra

**Kohde:** `05_data_persistence_and_seeding.md`, `07_infrastructure_and_observability.md`  
**Koodipolku:** `backend_v2/database/`, `backend_v2/seed/`

---

## M7: API & Core Registry

**Kohde:** `01_backend_api_and_core.md`  
**Koodipolku:** `backend_v2/api/`, `backend_v2/core/`

### Puuttuvat:
- `core/registry.py` TaskRegistry detail
- `api/v2/` vs `api/routers/` ero
- Middleware-ketjun toimintalogiikka
