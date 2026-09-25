<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_global_document_cache.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: LLM Adapter Strict Typing & Periphery Dict Eradication

> **STATUS: DRAFT / ODOTTAA VAIHEITA 1 JA 2**  
> **ARKKITEHTUURINEN ASEMONTINTI: VAIHE 3/3 (Koodikannan 100 % Tyyppiturvallisuuden Viimeistely)**

---

## 1. Riippuvuudet ja Suoritusjärjestys (The Tripartite Roadmap)

Tämä suunnitelma on kolmas ja viimeinen osa Quorumin kolmivaiheisessa arkkitehtonisessa tyyppiturvallisuus- ja modernisointitiekartassa:

```
┌────────────────────────────────────────────────────────────────────────┐
│ VAIHE 1: IN-MEMORY SUORITUSPUTKEN TILASIIRTYMÄ (Toteutetaan ensin)    │
│ @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] │
│ • Ydin: DAGExecutor, StateProjector, ContextRouter, SynthesisEngine    │
│ • 100 % DTO: TraceEvent, StepOutputContentDTO, ContextVariablesDTO     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ VAIHE 2: PYSYVYYSKERROS & POSTGRESQL 17+ (Toteutetaan toisena)         │
│ @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]          │
│ • Vaihe 1.5: Pysyvyysentiteettien esisiivous (system_config, xai, mcp) │
│ • Vaihe 2+: All-in-PostgreSQL 17+, SQLAlchemy 2.0 ORM, PydanticJSONB   │
│ • driver.py poisto, seederin modernisointi, QGR003-poikkeusten siivous │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ VAIHE 3: LLM-ADAPTERIT & OHEISRAJAPINNAT (TÄMÄ SUUNNITELMA)            │
│ @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_Adapter_Strict_Typing.md] │
│ • LLM-adapterien Anti-Corruption Layer -tyypitys (adapters/)           │
│ • JSON-skeemanrakentajat ja ingress-korjausputki (ingress_pipeline.py) │
│ • Oheisalueiden jäännössanakirjojen siivous (hooks/, registry.py)      │
│ • TAVOITE: audit_dict_eradication.py backend_v2 -> TASAN 0 RIKKOMUSTA │
└────────────────────────────────────────────────────────────────────────┘
```

- **Esiehto 1 (Kriittinen)**: @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] on suoritettu ja validoitu 100 % hyväksytysti. Suoritusputki operoi puhtailla DTO-olioilla.
- **Esiehto 2 (Suositeltu)**: @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] on toteutettu tai sen Vaihe 1.5 (Pysyvyysentiteettien esisiivous) on ajettu, jolloin tietokantakoodi ja poistuva TinyDB eivät aiheuta varjo-ongelmia.

---

## 2. Ongelman Kuvaus & Nykyinen AST-tilanne

Kun Vaihe 1 (Suoritusputki) ja Vaihe 2 (PostgreSQL + Vaihe 1.5) on toteutettu, koodikantaan jää n. 74 kpl `audit_dict_eradication.py` -rikkomusta, jotka jakautuvat kahteen ryhmään:

### A. Ulkoisten LLM-palveluntarjoajien adapterit & skeemanrakentajat (~50 kpl)
- `backend_v2/llm/adapters/anthropic_adapter.py` (12 kpl)
- `backend_v2/llm/adapters/base_adapter.py` (10 kpl, sis. 4 duck-typingia `isinstance(schema_dict, dict)`)
- `backend_v2/llm/adapters/openai_adapter.py` (8 kpl, sis. 2 duck-typingia `isinstance(node, dict)`)
- `backend_v2/llm/ingress_pipeline.py` (6 kpl, sis. 4 duck-typingia `isinstance(data, dict)`)
- `backend_v2/llm/adapters/mock_adapter.py` (4 kpl)
- `backend_v2/llm/schema_builder.py` (3 kpl)
- `backend_v2/llm/adapters/deepseek_adapter.py` (2 kpl)
- `backend_v2/llm/caching_service.py` (2 kpl)
- `backend_v2/llm/mock_data.py` & `mock.py` (3 kpl)

**Syy**: Ulkoiset SDK:t (LiteLLM, OpenAI SDK, Anthropic SDK) ottavat vastaan ja palauttavat natiivisti raakoja sanakirjoja (`tools: [{"type": "function", ...}]`). Adapterien tehtävä on toimia palomuurina (*Anti-Corruption Layer*). Tässä suunnitelmassa nämä sisäiset sanakirjat tyypitetään joko virallisilla Pydantic-malleilla tai `JsonValue`-tyypeillä ilman, että ulkoisten APIen yhteensopivuutta rikotaan.

### B. Oheismoduulien ja koukkujen jäännössanakirjat (~24 kpl)
- `backend_v2/core/registry.py` (4 kpl)
- `backend_v2/hooks/scoring/matrix_hook.py` (3 kpl)
- `backend_v2/models/domain/base.py` (2 kpl)
- `backend_v2/models/llm.py` (2 kpl)
- `backend_v2/core/rate_limit.py` (1 kpl)
- `backend_v2/hooks/linguistics.py` & `llm.py` (2 kpl)
- `backend_v2/hooks/scoring/passivity_hook.py` (1 kpl)
- `backend_v2/models/domain/analyst.py`, `archivist.py`, `integrity.py`, `metrics.py`, `security.py` (5 kpl)
- `backend_v2/models/dtos/mcp.py`, `prompt_context.py`, `system.py` (3 kpl)
- `backend_v2/scripts/generate_openapi.py` (1 kpl)

---

## 3. Toteutussuunnitelma & Työpaketit

### Työpaketti 1: BaseLLMAdapter & SchemaBuilder Tyyppiturvallisuus
- Tiedostot: @[backend_v2/llm/adapters/base_adapter.py], @[backend_v2/llm/schema_builder.py]
- **Toimenpiteet**:
  1. Korvataan `isinstance(schema_dict, dict)`- ja `isinstance(properties, dict)` -duck-typingit Pydantic V2 `TypeAdapter`-tarkistuksilla tai tyypitetyllä `JSONSchemaNodeDTO` -mallilla.
  2. Korvataan `schema: dict[str, Any]` tyypitetyllä `dict[str, JsonValue]` tai `PydanticJsonSchemaDTO` -mallilla.
  3. Säilytetään adapterin `build_schema`-metodin julkinen DTO-rajapinta.

### Työpaketti 2: Palveluntarjoajaspesifit Adapterit (OpenAI, Anthropic, DeepSeek)
- Tiedostot: @[backend_v2/llm/adapters/openai_adapter.py], @[backend_v2/llm/adapters/anthropic_adapter.py], @[backend_v2/llm/adapters/deepseek_adapter.py]
- **Toimenpiteet**:
  1. Tyypitetään OpenAI- ja Anthropic-työkalumäärittelyt (`tools`, `tool_choice`) käyttäen joko palveluntarjoajan virallisia tyyppejä tai `dict[str, JsonValue]`.
  2. Poistetaan `openai_adapter.py`:n 2 kpl `isinstance(node, dict)` duck-typingia.
  3. Eristetään LiteLLM:n palauttama raaka JSON-vastaus välittömästi `LLMStepResponse`- ja `EngineExecutionResult`-malleihin ilman sanakirjojen vuotamista adapterin ulkopuolelle.

### Työpaketti 3: IngressPipeline & Mock-Infrastruktuuri
- Tiedostot: @[backend_v2/llm/ingress_pipeline.py], @[backend_v2/llm/mock.py], @[backend_v2/llm/mock_data.py], @[backend_v2/llm/caching_service.py]
- **Toimenpiteet**:
  1. Korvataan `ingress_pipeline.py`:n 4 kpl `isinstance(data, dict)` duck-typingia puhtaalla `TypeAdapter.validate_python()` Fail-Fast -käsittelyllä.
  2. Korvataan mock-adapterien ja välimuistin raakasanakirjat vahvoilla DTO-malleilla.

### Työpaketti 4: Oheismoduulien & Koukkujen Siivous (Periphery Zero Dicts)
- Tiedostot: @[backend_v2/core/registry.py], @[backend_v2/hooks/scoring/matrix_hook.py], @[backend_v2/hooks/scoring/passivity_hook.py], @[backend_v2/hooks/linguistics.py], @[backend_v2/hooks/llm.py]
- **Toimenpiteet**:
  1. Korvataan pisteytyskoukkujen tilapäiset sanakirjamerkinnät `dict[str, JsonValue]`- tai `LevelStatsDTO`-tyypeillä.
  2. Korvataan `registry.py`:n ja `rate_limit.py`:n sanakirjatyypit `dict[str, JsonValue]` -rakenteilla.
  3. Siivotaan yksittäiset domain-tiedostot (`analyst.py`, `archivist.py`, `integrity.py`, `metrics.py`, `security.py`).

---

## 4. Matemaattinen Laatuportti (Proof Anchor)

Tämän suunnitelman valmistuttua koko Quorum Backend saavuttaa täydellisen matemaattisen tyyppipuhtauden:

```powershell
# Lopullinen järjestelmätason AST-verifiointi:
uv run python scripts/audit_dict_eradication.py backend_v2 --strict
```

**HYVÄKSYNTÄKRITEERI**:
- `Total Violations`: **Tasan 0**
- `Naked Dict Annotations`: **0**
- `Service Duck-Typing`: **0**
- `Banned .get()`: **0**
- `Reflection`: **0**
- `Primitive Obsession`: **0**
- `Unauthorized Suppressions`: **0**
- Pytest-yksikkötestit ja integraatiotestit: **100 % pass**.
