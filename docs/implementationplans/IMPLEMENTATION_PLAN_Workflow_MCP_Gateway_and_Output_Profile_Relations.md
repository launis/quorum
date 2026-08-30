> **STATUS: PENDING / ODOTTAA TOTEUTUSTA**

# Implementation Plan: Workflow MCP-Gateway & Output Profile Relational Architecture (Clean Pydantic V2)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_e2e_sdui_parity_architecture.md]</knowledge_item>
</required_context_rules>

<anti_targets>
- Do NOT use naked dictionaries (`dict[str, Any]`) for state transit inside Service or Adapter layers.
- Do NOT break `polymorphic_parsing_mandate` / `service_layer_hydration_firewall` before the Clean Pydantic DAL transition is globally scheduled (Repositories return `dict[str, Any]` with `id` filtering; Service/Transformer layers hydrate).
- Do NOT use defensive `isinstance(..., dict)` or `.get(...)` fallback branching in new service or adapter code.
- Do NOT use legacy `workflow_id == "*"` wildcards in `OutputProfile` resolution.
- Do NOT allow deleting active default output profiles (`Workflow.default_profile_id`).
- Do NOT execute generic `limit=1` unindexed queries when fetching MCP Gateways by ID.
- Do NOT hardcode localized tool names in Python constants.
- Do NOT couple MCP Gateway documents to specific workflows (Gateways are standalone; Workflows reference Gateways `N : 1`).
</anti_targets>

## Problem Statement & Architectural Context

In Quorum 2026, the relationship between Workflows, Output Profiles, and MCP Gateways must adhere strictly to the **Tripartite Pipeline Architecture** (`ki_tripartite_pipeline_architecture.md`) and the **Clean Pydantic Transition Catalog** (`docs/CLEAN_PYDANTIC_TRANSITION_CATALOG.md`):

1. **Phase 1 (Heavy LLM Execution Phase — Pre-bound MCP Gateways & Reusability):**
   - **Täysi riippumattomuus työnkulusta (Standalone System Entity):** `SystemConfigMCPGateways` -määrittelyt (`system_config`-kokoelmassa) ovat täysin riippumattomia ja itsenäisiä järjestelmätason entiteettejä. Ne eivät sisällä mitään viittauksia työnkulkuihin. Useat eri työnkulut voivat käyttää samaa MCP-yhdyskäytäväkonfiguraatiota (`N : 1` uudelleenkäytettävyys).
   - **Yksikäsitteinen sidonta työnkulun puolelta:** Kukin `Workflow` sidotaan yhteen ja vain yhteen MCP-yhdyskäytävään suoralla viittauksella: `Workflow.mcp_gateway_id: str | None = Field(default="sys_8172bda70c8641c5")` (tai `None`, jos työnkulku ei käytä ulkoista tiedonhakua).
   - MCP-työkalut (Tavily, Wikipedia, PubMed jne.) suorittavat reaaliaikaisen ulkoisen tiedonhaun DAG-ajon aikana (vaiheet 7 & 14). Kaikki noudettu todistusaineisto ja `MCPAuditTrace`-jäljet jäädytetään immutaabelisti suoritustietueeseen `ExecutionRecord.frozen_context`.

2. **Phase 2 & 3 (Synthesis & SDUI Presentation — Post-Hoc Output Profiles):**
   - Output Profiles ovat puhtaita "Dumb Painter" -esitysmalleja (`target_block_order`, `matrix_visible_columns`, `tone_instruction`).
   - Jokainen `OutputProfile` kuuluu täsmälleen yhteen työnkulkuun (`1 : N` relaatio `OutputProfile.workflow_id` -kentän kautta).
   - Työnkulku ilmoittaa oletusprofiilinsa `Workflow.default_profile_id` -kentässä.
   - **Tripartite Decoupling:** Koska Vaiheen 1 suoritusdata on täysin eriytetty Vaiheiden 2 & 3 esityslogiikasta, käyttäjä voi **jälkikäteen (post-hoc)** renderöidä minkä tahansa aiemman ajon minkä tahansa samaan työnkulkuun kuuluvan `OutputProfile`-profiilin läpi ilman, että raskasta LLM-graafia tarvitsee suorittaa uudestaan!

3. **Pydantic Transition State (Repository Hydration Firewall):**
   - Noudattaen `polymorphic_parsing_mandate` ja `service_layer_hydration_firewall` -sääntöjä, `ISystemRepository` palauttaa `dict[str, Any]` täsmällisellä `id`-suodatuksella (`[Filter("id", "==", id)]`).
   - Service-kerros (`SystemConfigService`) ja esitysmuuntaja (`BlueprintTransformer`) toimivat *Hydration Firewallina*, validoiden raakadatan Pydantic V2 -malliksi (`SystemConfigMCPGateways.model_validate(raw, strict=False)`).
   - Kaikki sisäiset domain-operaatiot ja adapterikontekstit toimivat 100 % tiukoilla Pydantic V2 -malleilla (`ConfigDict(strict=True, extra="forbid")`) puhtaalla pistenotaatiolla.

---

## Five-Column Architectural Directive Table

| 1. Kohdealue & Skoopit (Target Scope) | 2. 🚫 KIELLETTY PURKKA (Eradicated Duct-Tape) | 3. 🎯 TEE NÄIN (Approved Best Practice) | 4. ✂️ KARSITTU YLISUUNNITTELU (Pruned Over-Engineering) | 5. 🔒 VERIFIOINTI & FAIL-FAST (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`Workflow.mcp_gateway_id`** (`models/v2_core.py#L1096-L1224`) | Epämääräinen `limit=1` -haku kannasta ilman relaatiota; singleton-oletus. | Eksplisiittinen `mcp_gateway_id: str \| None = Field(default="sys_8172bda70c8641c5", pattern=r"^sys_[a-fA-F0-9]{16,32}$", description="The system_config ID of the MCP gateways configuration attached to this workflow.")` sitoen työnkulun täsmälleen yhteen itsenäiseen MCP-yhdyskäytävään (useat työnkulut voivat jakaa saman yhdyskäytävän). | Suora N:1 skalaarirelaatio; ei monimutkaisia väli-mapping-tauluja. | Pydantic regex-validointi ja yksikkötestit (`test_workflow_model.py`). |
| **`OutputProfile.workflow_id`** (`models/v2_core.py#L943-L1093`) | Villikortit `workflow_id == "*"` ja tyypittömät sanakirjat profiilin haussa. | Tiukka `workflow_id: str = Field(pattern=r"^wf_[a-fA-F0-9]{16,32}$", description="ID of the associated Workflow")` sitoen jokaisen profiilin täsmälleen yhteen työnkulkuun. Mahdollistaa post-hoc raportoinnin eri profiileilla. | Suora 1:N FK; ei monesta-moneen ristiliitoksia tai dynaamisia profiili-injectoreita. | Pydantic regex-validointi ja `test_output_profile_repo.py`. |
| **`ISystemRepository.get_mcp_gateways`** (`database/interfaces.py#L1233-L1246` & `repositories/system.py#L56-L74`) | Unindexed `limit=1` haku ilman id-suodatusta; ennenaikainen Pydantic DAL -rajapintamuutos kesken siirtymän. | `async def get_mcp_gateways(self, id: str \| None = None) -> dict[str, Any]:` suodattaa `[Filter("id", "==", id)]` ja nostaa `ResourceNotFoundError` jos dokumenttia ei löydy. | Repositorio palauttaa `dict[str, Any]` noudattaen `service_layer_hydration_firewall` -sääntöä. | `test_system_repository.py` testaa id-suodatuksen ja `ResourceNotFoundError`-käsittelyn. |
| **`AdapterContext.mcp_tools_map`** (`services/sdui/adapters/base_adapter.py#L20-L47`) | Tyypittömät sanakirjat tai ad-hoc tietokantakyselyt adapterin sisällä (Dumb Painter -rikkomus). | `mcp_tools_map: dict[str, AllowedMCPTool] = Field(default_factory=dict)` suoraan Pydantic DTO -kontekstissa. `AllowedMCPTool` lisätään `model_rebuild()` -kutsuun. | Ei dynaamisia tietokantakutsuja tai asynkronisia hookeja adapterin sisällä. | `test_base_adapter.py` ja `test_printable_sources_adapter.py`. |
| **`BlueprintTransformer` Gateway Resolution** (`services/blueprint.py#L58-L671`) | Kovakoodatut oletustyökalunimet tai MCP-gatewayn lataamatta jättäminen. | Eager Fetching: `raw = await self.system_repo.get_mcp_gateways(id=workflow_obj.mcp_gateway_id)`, hydratointi `gateway_obj = SystemConfigMCPGateways.model_validate(raw, strict=False)`, `mcp_tools_map = {t.tool_id: t for t in gateway_obj.tools}` ja injektio `AdapterContext`-olioon. | Ei rinnakkaista gateway-resoluutiopalvelua; suora kulutus repositoriosta. | `test_blueprint_transformer.py` varmentaa `mcp_tools_map`-injektion. |
| **`PrintableSourcesAdapter.build`** (`services/sdui/adapters/printable_sources_adapter.py#L35-L200`) | Kovakoodattu `PRINTABLE_SOURCES_RULES["mcp_tools"]` -sanakirja ja olematon `name.resolve()` -metodi. | Puhdas pistenotaatio: `tool.name.translations.get(locale, tool.name.translations["en"])` hyödyntäen tietokannasta ladattua `AllowedMCPTool`-mallia. Fallback tuntemattomille työkaluille `clean_name = t_id.removeprefix("mcp_").replace("_", " ").title()`. | `mcp_tools` -sanakirjan poisto Python-koodista; nojataan tietokannan SSOT-malliin. | `test_printable_sources_adapter.py` todistaa kannasta tulevan lokalosoidun nimen tulostumisen raporttiin. |
| **Flutter Studio UI** (`client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart#L140-L240`) | Kovakoodattu yhdyskäytävän nimi tai puuttuva valitsin työnkulun yleisasetuksissa. | Reaktiivinen pudotusvalikko `mcpGatewaysControllerProvider` -ohjaimesta sidottuna `workflow.mcpGatewayId` -kenttään. | Suora valitsin General-välilehdellä olemassa olevan profiilivalitsimen rinnalle. | Flutter-laatuportti (`flutter_audit_loop.py`). |

---

## Proposed Changes

### Phase 1: Pre-Implementation Technical Debt Cleanups & Schema Alignment

#### [CLEANUP] [printable_sources_adapter.py](file:///c:/src/quorum/backend_v2/services/sdui/adapters/printable_sources_adapter.py)
- **Target Span:** `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L35-L84]`
- Remove hardcoded `"mcp_tools"` dictionary inside `PRINTABLE_SOURCES_RULES` in favor of dynamic `AdapterContext.mcp_tools_map` resolution.
- Keep `literature_source`, `theory_evidence_map`, and `default_tool` fallback rules intact.

#### [NOTE: KNOWN TECH DEBT BOUNDARY] [blueprint.py](file:///c:/src/quorum/backend_v2/services/blueprint.py)
- **Target Span:** `@[backend_v2/services/blueprint.py#L346-L352]`
- `isinstance(execution.metadata, dict)` represents Catalog Archetype 1 debt. Do NOT refactor this execution metadata block in this task (reserved for Clean Pydantic Transition Phase 3).

#### [MODIFY] [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)
- **Target Span:** `@[backend_v2/models/v2_core.py#L1096-L1224]`
- Add `mcp_gateway_id: str | None = Field(default="sys_8172bda70c8641c5", pattern=r"^sys_[a-fA-F0-9]{16,32}$", description="The system_config ID of the MCP gateways configuration attached to this workflow.")` to `Workflow`.

#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)
- **Target Span:** `@[backend_v2/seed/seed_data.json#L8335-L8480]`
- Add `"mcp_gateway_id": "sys_8172bda70c8641c5"` to workflow `wf_9d68c573802341db` in `workflows`.

---

### Phase 2: Database Repository & Service Layer Integration

#### [MODIFY] [interfaces.py](file:///c:/src/quorum/backend_v2/database/interfaces.py)
- **Target Span:** `@[backend_v2/database/interfaces.py#L1233-L1246]`
- Update signature with ID filter parameter while preserving `dict[str, Any]` return:
  `async def get_mcp_gateways(self, id: str | None = None) -> dict[str, Any]:`

#### [MODIFY] [system.py](file:///c:/src/quorum/backend_v2/database/repositories/system.py)
- **Target Span:** `@[backend_v2/database/repositories/system.py#L56-L74]`
- Update `get_mcp_gateways(self, id: str | None = None) -> dict[str, Any]`:
  - Filter by `id` when provided (`[Filter("id", "==", id)]`), falling back to `[Filter("type", "==", "mcp_gateways")]` if `id` is None.
  - Raise `ResourceNotFoundError(resource_type="system_config", resource_id=id or "mcp_gateways")` if not found.
  - Return raw document `dict[str, Any]`.

#### [MODIFY] [system_config_service.py](file:///c:/src/quorum/backend_v2/services/studio/system_config_service.py)
- **Target Span:** `@[backend_v2/services/studio/system_config_service.py#L318-L367]`
- Clean up `.get("type")` checks: consume `raw = await self.system_repo.get_mcp_gateways(id=id)` and hydrate `SystemConfigMCPGateways.model_validate(raw, strict=False)`.

#### [MODIFY] [base_adapter.py](file:///c:/src/quorum/backend_v2/services/sdui/adapters/base_adapter.py)
- **Target Span:** `@[backend_v2/services/sdui/adapters/base_adapter.py#L20-L80]`
- Import `AllowedMCPTool` from `backend_v2.models.v2_core`.
- Add `mcp_tools_map: dict[str, AllowedMCPTool] = Field(default_factory=dict)` to `AdapterContext`.
- Add `"AllowedMCPTool": AllowedMCPTool` to `AdapterContext.model_rebuild(_types_namespace=...)`.

#### [MODIFY] [blueprint.py](file:///c:/src/quorum/backend_v2/services/blueprint.py)
- **Target Span:** `@[backend_v2/services/blueprint.py#L365-L385]` & `@[backend_v2/services/blueprint.py#L585-L605]`
- When `workflow_obj.mcp_gateway_id` is set:
  - Load raw dict `raw = await self.system_repo.get_mcp_gateways(id=workflow_obj.mcp_gateway_id)`.
  - Hydrate `gateway_obj = SystemConfigMCPGateways.model_validate(raw, strict=False)`.
  - Build `mcp_tools_map = {tool.tool_id: tool for tool in gateway_obj.tools}`.
  - Pass `mcp_tools_map=mcp_tools_map` into `AdapterContext` at both construction sites.
- When `workflow_obj.mcp_gateway_id` is None, pass `mcp_tools_map={}`.

#### [MODIFY] [printable_sources_adapter.py](file:///c:/src/quorum/backend_v2/services/sdui/adapters/printable_sources_adapter.py)
- **Target Span:** `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L150-L175]`
- Resolve tool names dynamically from `context.mcp_tools_map`:
  - If `t_id in context.mcp_tools_map`: `tool = context.mcp_tools_map[t_id]; t_name = tool.name.translations.get(locale, tool.name.translations["en"])`.
  - Fallback cleanly for unknown IDs: `clean_name = t_id.removeprefix("mcp_").replace("_", " ").title(); t_name = f"{clean_name} Gateway"`.

---

### Phase 3: Client App Model & UI Support

#### [MODIFY] [workflow.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/workflow.dart)
- **Target Span:** `@[client_app_v2/lib/features/studio/models/workflow.dart#L127-L180]`
- Add `@JsonKey(name: 'mcp_gateway_id') @Default("sys_8172bda70c8641c5") String? mcpGatewayId` to `Workflow` Freezed model.

#### [MODIFY] [workflow_general_tab.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart)
- **Target Span:** `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart#L140-L240]`
- Add a dropdown for selecting the MCP Gateway configuration from `mcpGatewaysControllerProvider` in the Global Settings Card.

---

## Post-Implementation Evolution: Cross-Workflow Profile Cloning (Sanitizing Cloner Pattern)

> [!NOTE]
> **TULEVAISUUDEN LAATIKKO / FUTURE CAPABILITY (Ei toteuteta tässä tehtävässä, mutta arkkitehtuuri on valmisteltu tätä varten):**
> 
> Vaikka tulostusprofiili on aina alisteinen yhdelle työnkululle (`OutputProfile.workflow_id`), järjestelmään voidaan tulevassa vaiheessa lisätä Studio-tason **"Kopioi toiseen työnkulkuun"** -toiminto (`clone_output_profile_to_workflow(source_profile_id, target_workflow_id)`):
> 
> 1. **85 % profiilista on työnkuluista riippumatonta esityskonfiguraatiota:** Sävyohjeet (`tone_instruction`), mukautettu esipuhe (`custom_preface`), esitysasteikot (`display_scale`, `custom_scale_min/max`), näkyvät sarakkeet (`matrix_visible_columns`), lohkojärjestys (`target_block_order`) ja lähdemoodit (`sources_display_mode`). Nämä kopioituvat 1:1 sellaisenaan uuteen työnkulkuun.
> 2. **15 % (työnkulkukohtaiset viittaukset) sanitoidaan:**
>    - `cloned.workflow_id = target_workflow_id`
>    - `performativity_detector_step_id`: Nollataan arvoon `None`, jos askelta ei löydy uudesta työnkulusta.
>    - `matrix_synthesis_groups`: Tarkistetaan kohdetyönkulun matriiseja vasten ja poistetaan tai alustetaan puuttuvat vertailuryhmät.
> 3. **Dumb Painter -turvaverkko (`ki_dumb_painter_sdui.md`):** Koska `BlueprintTransformer` piirtää raportin vain suoritetusta datasta, työnkulun muuttuminen tai erot eivät koskaan kaada raportin muodostusta.

---

## Verification Plan

### Automated Tests
1. **Backend Quality Gates & Unit Tests:**
   - `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py backend_v2/database/repositories/system.py backend_v2/services/blueprint.py backend_v2/services/sdui/adapters/printable_sources_adapter.py --test`
   - `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py`
2. **ISTQB Boundary & Equivalence Partitions:**
   - Positive: Workflow with `mcp_gateway_id` successfully resolves localized tool name (`Tavily AI -haku` for `fi`, `Tavily AI Search` for `en`).
   - Boundary/Negative 1: Unknown tool ID in trace not present in `mcp_tools_map` triggers graceful fallback badge formatting without crashing.
   - Boundary/Negative 2: Missing MCP gateway document (invalid `mcp_gateway_id`) triggers explicit `ResourceNotFoundError(resource_type="system_config", resource_id=id)`.
   - Boundary/Negative 3: Workflow with `mcp_gateway_id = None` passes empty `mcp_tools_map` without attempting database lookups.
   - Boundary/Negative 4: `AllowedMCPTool.name.translations` missing target locale falls back cleanly to English translation (`"en"`).
3. **E2E Semantic Parity:**
   - `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
   - `uv run pytest backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py`
4. **Flutter Quality Gates:**
   - `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build`
   - `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart`
