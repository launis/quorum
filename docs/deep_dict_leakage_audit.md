# Syvyysauditointi: Dict-Vuotovektorit Nykyisen Suunnitelman Ohitse

> [!CAUTION]
> Nykyinen suunnitelma kattaa `isinstance(dict)`, `match/case dict`, `cast(Any)`, ja `# noqa: QGR` — mutta **6 muuta vuotovektoria** sallii dict-tyyppien valumisen toteutukseen tahattomasti.

## Yhteenveto: 6 Vuotovektoria

| # | Vektori | Instanssit | Tiedostot | Kriittisyys | Nykyisen suunnitelman kattavuus |
|---|---|---|---|---|---|
| V1 | `dict[str, Any]` tyyppi-annotaatiot | **130+** | **35+** | **KRIITTINEN** | ❌ Ei katettu |
| V2 | `list[dict[str, Any]]` tyyppi-annotaatiot | **40+** | **20+** | **KRIITTINEN** | ⚠️ Osittain katettu (Phase 3 `LLMMessageDTO`) |
| V3 | `model_dump()` → dict-muuttuja → dict-operaatiot (laundering) | **56** | **25+** | **KORKEA** | ❌ Ei katettu |
| V4 | `hasattr()` ilman noqa (reflektio) | **46** | **10** | **KRIITTINEN** | ⚠️ Vain 4 QGR001-suppressoitua katettu |
| V5 | `json.loads()` ilman `model_validate()` | **7** | **3** | **KORKEA** | ❌ Ei katettu |
| V6 | `{**spread}` dict merge -patternit | **16** | **5** | **KESKITASO** | ❌ Ei katettu |

---

## V1: `dict[str, Any]` Tyyppi-Annotaatiot (130+ instanssia)

> [!IMPORTANT]
> Tämä on **suurin yksittäinen vuotovektori**. Kun funktio hyväksyy `data: dict[str, Any]`, se on eksplisiittinen lupaus käsitellä raakoja sanakirjoja. Tekoäly näkee nämä annotaatiot ja pitää dict-käyttöä sallittuna.

### Kriittisimmät tiedostot (Service/Hook-kerrokset):

| Tiedosto | Instanssit | Esimerkki |
|---|---|---|
| `@[backend_v2/services/progress.py]` | **21** | `payload: dict[str, Any]`, `details: dict[str, Any] \| None` |
| `@[backend_v2/services/orchestrator/dag_executor.py]` | **12** | `global_vars: dict[str, Any]`, `updates: dict[str, Any]` |
| `@[backend_v2/services/orchestrator/strategies/llm.py]` | **8** | `current_state: dict[str, Any]`, `metadata: dict[str, Any]` |
| `@[backend_v2/services/studio/workflow_service.py]` | **6** | `draft_dict: dict[str, Any]`, `new_mappings: dict[str, Any]` |
| `@[backend_v2/services/studio/simulation_service.py]` | **4** | `mock_inputs: dict[str, Any]`, `-> dict[str, Any]` |
| `@[backend_v2/services/studio/output_profile_service.py]` | **3** | `data: dict[str, Any] \| OutputProfile` |
| `@[backend_v2/services/orchestrator/extraction_schema_factory.py]` | **3** | `facts_fields: dict[str, Any]` |
| `@[backend_v2/services/orchestrator/strategies/logic.py]` | **2** | `safe_context: dict[str, Any]` |

**Miksi vaarallista**: Nämä eivät ole pelkkiä annotaatioita — ne ovat **funktioiden julkisia allekirjoituksia** jotka kertovat koodipohjalle ja tekoälylle: "tämä funktio hyväksyy raakoja dictejä". Jokainen uusi koodinkirjoittaja (ihminen tai AI) käyttää näitä annotaatioita ohjenuoranaan.

---

## V2: `list[dict[str, Any]]` Annotaatiot (40+ instanssia)

### Kriittisimmät (jo suunnitelmassa osittain katetut):

| Tiedosto | Instanssit | Status |
|---|---|---|
| `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]` | 3 | ✅ Katettu Phase 3 (`LLMMessageDTO`) |
| `@[backend_v2/services/llm_task_executor.py]` | 2 | ✅ Katettu Phase 3 |
| `@[backend_v2/worker.py]` | 5 | ❌ **Puuttuu** — `exec_messages: list[dict[str, Any]]` etc. |
| `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]` | 4 | ❌ **Puuttuu** |
| `@[backend_v2/services/orchestrator/matrix_explanation_service.py]` | 1 | ❌ **Puuttuu** |
| `@[backend_v2/services/execution.py]` | 2 | ❌ **Puuttuu** |
| `@[backend_v2/hooks/interaction_hook.py]` | 1 | ❌ **Puuttuu** |

---

## V3: `model_dump()` Laundering (56 instanssia)

**Mekanismi**: `model_dump()` muuntaa Pydantic-mallin raakaksi dictiksi. Kun tulos tallennetaan muuttujaan ja sitä käytetään dict-operaatioilla (`[key]`, `.get()`, `.update()`, `.pop()`), tämä kiertää kaikki tyypitystarkistukset:

```python
# VAARALLINEN PATTERTI:
dumped = model.model_dump(mode="json")    # → dict[str, Any]
dumped["new_key"] = "anything"             # → ei tyyppitarkistusta
dumped.update({"rogue_field": True})       # → ei validointia
```

### Kriittisimmät esimerkit:
- `@[backend_v2/hooks/scoring/matrix_hook.py]`: `ev_dump = ev.model_dump(mode="json")` → `ev_dump["key"]` (4 tapausta)
- `@[backend_v2/services/orchestrator/prompt_compiler.py]`: `current = current.model_dump()[part]` (dict traversal)
- `@[backend_v2/llm/provider.py]`: `provider_meta = response.model_dump() if hasattr(response, "model_dump") else {}` (hasattr + model_dump combo)
- `@[backend_v2/services/studio/output_profile_service.py]`: `existing_dict = existing.model_dump()` → `{**existing_dict, **data_dict}` (merge)

---

## V4: `hasattr()` Reflektio (46 unsuppressed instanssia)

> [!CAUTION]
> **21 pelkästään `provider.py`:ssä!** Nykyinen suunnitelma kattaa vain 4 `QGR001`-suppressoitua `hasattr()`-kutsua. **42 lisäinstanssia** on täysin suunnitelman ulkopuolella.

| Tiedosto | Instanssit | Esimerkki |
|---|---|---|
| `@[backend_v2/llm/provider.py]` | **21** | `hasattr(response, "choices")`, `hasattr(tc, "function")`, `hasattr(response, "_hidden_params")` |
| `@[backend_v2/logging_config.py]` | **7** | `hasattr(record, "error_code")`, `hasattr(exc, "details")` |
| `@[backend_v2/utils/redis_patcher.py]` | **7** | `hasattr(fake_redis, "get_connection")` |
| `@[backend_v2/database/firestore_driver.py]` | **1** | `hasattr(data, "model_dump")` |
| `@[backend_v2/database/tinydb_driver.py]` | **1** | `hasattr(data, "model_dump")` |
| `@[backend_v2/database/repositories/audit.py]` | **1** | `hasattr(record, "model_dump")` |
| `@[backend_v2/llm/client.py]` | **1** | `hasattr(response, "choices")` |
| `@[backend_v2/llm/mock.py]` | **1** | `hasattr(obj, "isoformat")` |
| `@[backend_v2/core/registry.py]` | **1** | `hasattr(status, "name")` |

---

## V5: `json.loads()` Ilman `model_validate()` (7 instanssia)

| Tiedosto | Rivinumero | Koodi |
|---|---|---|
| `@[backend_v2/llm/ingress_pipeline.py]` | L364 | `parsed_data = cast(dict[str, Any], json.loads(raw_stripped))` |
| `@[backend_v2/llm/provider.py]` | L1160 | `parsed_result = json.loads(content_str)` |
| `@[backend_v2/utils/finops_trace_analyzer.py]` | L24, L40, L86, L131, L162 | Useita `json.loads()` → raaka dict |

---

## V6: `{**spread}` Dict Merge (16 instanssia palvelukerroksessa)

Erityisesti `dag_executor.py` sisältää **11 {**spread}** -patternia:
```python
new_states = {**exec_record.step_states, step_id: new_state}
```

Nämä ovat `model_copy(update=...)` -käytännön sijasta suoria dict-yhdistämisiä, jotka ohittavat Pydanticin validoinnin.

---

## Analyysi: Mikä on akuutti riski vs. hyväksyttävä rajakerrosoperaatio?

### Hyväksyttävät (rajakerros-poikkeukset per `no_naked_dicts_in_state`):

1. **Database driver/repository -kerrokset** (`firestore_driver.py`, `tinydb_driver.py`): `hasattr(data, "model_dump")` on legitimiimia rajakerrosinspektiota ennen hydraatiota — mutta pitäisi korvata `isinstance(data, BaseModel)` -tarkistuksella.
2. **`model_dump(mode="json")` + heti DB-tallennus**: Esim. `@[backend_v2/database/repositories/audit.py]` L81 — tämä on rajakerrosoperaatio ja sallittu per sääntö.
3. **`finops_trace_analyzer.py`**: Apuohjelma lokien lukemiseen, ei domain-koodi.
4. **`redis_patcher.py`**: Test utility monkeypatching.

### Kriittiset (EIVÄT ole rajakerrosoperaatioita):

1. **`provider.py` 21 hasattr()**: LiteLLM-responsejen käsittely on KRIITTINEN — tämä on Quorumin LLM-rajapinnan ydin.
2. **Service-kerroksen `dict[str, Any]` -annotaatiot** (130+): Nämä ovat arkkitehtuurisia lupauksia raaka-dict-käytöstä.
3. **`model_dump()` → dict-manipulaatio** palvelukerroksessa: Kiertää tyypitystarkistukset.
4. **`json.loads()` → `cast(dict[str, Any], ...)`** ingress_pipeline.py: Tulisi olla `TypeAdapter.validate_json()`.

---

## Korjausehdotus: Suunnitelman Laajennukset

### Välitön (lisää olemassaoleviin vaiheihin):

| Vektori | Toimenpide | Vaiheen laajennus |
|---|---|---|
| V4 hasattr() (42 uutta) | `provider.py` 21 kpl korvattava tyypitettyinä | Phase 8A laajennus |
| V4 hasattr() | `logging_config.py` 7 kpl: OK (stdlib LogRecord) | Ei tarvita |
| V4 hasattr() | `redis_patcher.py` 7 kpl: OK (test utility) | Ei tarvita |
| V4 hasattr() | `firestore_driver.py`, `tinydb_driver.py`, `audit.py`: korvaa `isinstance(data, BaseModel)` | Phase 8C laajennus |
| V5 json.loads() | `ingress_pipeline.py` L364: korvaa `TypeAdapter.validate_json()` | Phase 8A laajennus |
| V5 json.loads() | `provider.py` L1160: korvaa tyypitetyllä parserilla | Phase 8A laajennus |

### Pitkän aikavälin (erillinen Epic):

> [!WARNING]
> V1 (130+ `dict[str, Any]` annotaatiota) ja V3 (56 `model_dump()` laundering) ovat **rakenteellisesti eri ongelma** kuin isinstance/noqa-remontti. Niiden korjaus vaatii **uuden DTO-hierarkian suunnittelua** jokaiselle palvelulle erikseen (esim. `ProgressEventDTO`, `DAGUpdateDTO`, `SimulationResultDTO`).

| Vektori | Laajuus | Suositus |
|---|---|---|
| V1 dict[str, Any] annotaatiot (130+) | 35+ tiedostoa | **Erillinen Epic** (massiivinen DTO-refaktorointi) |
| V2 list[dict] annotaatiot (40+) | 20+ tiedostoa | **Yhdistä V1 Epiciin** |
| V3 model_dump() laundering (56) | 25+ tiedostoa | **Erillinen Epic** (vaatii jokaisen model_dump()-polun analyysin) |
| V6 {**spread} dict merge (16) | 5 tiedostoa | **Yhdistä V3 Epiciin** |

---

## Päätökset tarvitaan

1. **Lisätäänkö V4 (hasattr 42 uutta) ja V5 (json.loads 7) nykyiseen suunnitelmaan?** → Suosittelen: Kyllä, laajenna Phase 8A ja 8C.
2. **Tehdäänkö V1/V2/V3/V6 erillisenä Epicinä?** → Suosittelen: Kyllä, uusi Epic koska laajuus on 200+ instanssia ja vaatii DTO-suunnittelua per palvelu.
3. **Pitäisikö AST guardrailsiin lisätä QGR013 (`dict[str, Any]` annotaatio) ja QGR014 (`hasattr()` ilman noqa)?** → Suosittelen: Kyllä, estää uusien vuotojen syntyminen.
