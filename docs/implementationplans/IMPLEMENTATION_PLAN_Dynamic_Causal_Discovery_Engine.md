```xml
<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>
```

# Implementation Plan - Dynamic Causal Discovery Engine (Exploratory Text DAG & Argument Mapping)

> [!CAUTION]
> **KAUKAISEN TULEVAISUUDEN TIEKARTTA (DISTANT FUTURE ROADMAP ONLY)**
> Tämä toteutussuunnitelma on laadittu varastoon tulevaisuuden laajennusta varten eikä se kuulu nykyiseen aktiiviseen kehityssykliin. Suunnitelma kuvaa valinnaisen ja kokeellisen avoimen tekstin kausaalianalyysin (*Exploratory Causal Discovery Engine*), joka analysoi vapaamuotoisia dokumentteja ilman ennalta määriteltyä arviointimatriisia. Tätä **EI** tule aktivoida osana nykyistä normatiivista arviointiydintä, eikä se saa heikentää `TDAEngine`-moottorin nykyistä determinismiä tai tiukkaa `shuffled_atoms`-vaatimusta.

---

## User Review Required

> [!IMPORTANT]
> **Single Pipeline Invariant & Zero-Fallback Compliance:**
> `CausalDiscoveryEngine` toteutetaan täysin itsenäisenä `ExecutionEngine`-moottorina omalla reititystunnisteellaan (`EngineOverrideStrategy.CAUSAL_DISCOVERY`). Se **EI** saa olla minkäänlainen fallback-haara `TDAEngine`n sisällä. `TDAEngine` säilyttää 100 % tiukan Fail-Fast-sopimuksensa (`request.shuffled_atoms` pakollinen).
>
> **SSOT ja Pydantic V2 -sopimukset:**
> Kaikki graafin solmut (`LinkedAtomGraph`), reunat (`CausalEdge`), uutetut väitteet (`ExtractedAtom`) ja SDUI-lohkot (`CausalGraphBlock`) noudattavat tiukkaa `ConfigDict(strict=True, extra='forbid', frozen=True)` -mallia ilman paljaita sanakirjoja (`dict[str, Any]`).
>
> **Resurssien hallinta ja tausta-ajo (Arq Worker):**
> Koska dynaaminen uutto ja liukuva linkitys vaativat useita peräkkäisiä ja rinnakkaisia LLM-kutsuja (Phase 0 ontologia -> Phase 1 lohkot -> Sliding Window linkitys -> Topologinen evaluointi), moottori ajetaan aina asynkronisessa taustaprosessissa (`worker.py`), raportoiden edistymistä reaaliaikaisesti SSE-virtaan.

---

## Scope & Boundaries

### Target Files:
- `[NEW]` @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- `[NEW]` @[backend_v2/models/dtos/causal_discovery.py]
- `[NEW]` @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/models/enums.py]
- `[MODIFY]` @[backend_v2/models/view/sdui.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]
- `[NEW]` @[client_app_v2/lib/features/execution/presentation/causal_graph_view.dart]

### Context / Read-Only Files:
- `@[backend_v2/services/orchestrator/engines/base.py]`
- `@[backend_v2/services/orchestrator/engines/tda_engine.py]`
- `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`
- `@[backend_v2/services/orchestrator/sliding_window_linker.py]`
- `@[backend_v2/services/orchestrator/topological_evaluator.py]`
- `@[backend_v2/services/orchestrator/result_projector.py]`
- `@[backend_v2/models/dtos/dag_models.py]`

---

## Proposed Changes

### Phase 1: Configuration, DTOs & Pre-requisite Foundation

#### [MODIFY] @[backend_v2/settings.py]
- Lisätään keskitetyt asetukset liukuvan ikkunan ja dynaamisen uuton rajoille:
  - `causal_discovery_window_size: int = 4`
  - `causal_discovery_overlap: int = 2`
  - `causal_discovery_max_atoms_per_window: int = 25`
  - `causal_discovery_max_total_atoms: int = 100`

#### [MODIFY] @[backend_v2/models/enums.py]
- Lisätään `EngineOverrideStrategy.CAUSAL_DISCOVERY = "CAUSAL_DISCOVERY"`.
- Lisätään `SduiBlockType.CAUSAL_GRAPH = "CAUSAL_GRAPH"`.

#### [NEW] @[backend_v2/models/dtos/causal_discovery.py]
- Määritellään tyypitetyt DTOt dynaamiselle kausaaligraafille:
  - `CausalNodeDTO(BaseModel)`: `node_id: str`, `claim: str`, `source_quote: str | None`, `status: ExecutionStatus`, `blame_parent_ids: list[str]`.
  - `CausalEdgeDTO(BaseModel)`: `source_id: str`, `target_id: str`, `reasoning: str`.
  - `CausalGraphPayloadDTO(BaseModel)`: `nodes: list[CausalNodeDTO]`, `edges: list[CausalEdgeDTO]`, `root_cause_node_ids: list[str]`, `cycle_detected: bool`.

---

### Phase 2: Engine Implementation & Orchestrator Wiring

#### [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- Toteutetaan `CausalDiscoveryEngine(ExecutionEngine)`:
  - Konstruktorissa injektoidaan `prompt_compiler: PromptCompiler`.
  - `execute(request: EngineExecutionRequest) -> EngineExecutionResult`:
    1. **Pre-flight Ingress & Hydration**: Alustaa `AliasEngine`, numeroi kappaleet (`[B0]...[Bn]`).
    2. **Phase 0 (Global Ontology)**: Kutsuu `TwoPassAtomizer.execute_phase_0` rakentaen `GlobalOntologyMap` -olion.
    3. **Phase 1 (Chunked Claim Extraction)**: Kutsuu `TwoPassAtomizer.execute_phase_1` muodostaen itsenäiset `ExtractedAtom`-oliot anaforat korvattuna.
    4. **Sliding Window Linking**: Kutsuu `SlidingWindowLinker.link_graph` kytkien atomit suunnatuksi `LinkedAtomGraph`-verkoksi (`CausalEdge`).
    5. **Topological Wave Execution**: Ajaa verkon `EnrichedDagExecutor`/`TopologicalEvaluator`-läpi short-circuit -kaskadeineen ja blame-attribuutioineen.
    6. **Result Projection**: Projisoi tilat `ResultProjector.project()`:lla palauttaen `EngineExecutionResult`.

#### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py]
- Lisätään `NodeExecutor.execute()`:n reititykseen tuki `EngineOverrideStrategy.CAUSAL_DISCOVERY`:lle:
  - Injektoi puhtaasti `CausalDiscoveryEngine(self.deps.prompt_compiler)`.
  - Ei koske `TDAEngine`-haaraan (säilyttää SSOT-invarianssin).

---

### Phase 3: SDUI Presentation & Client Visualization

#### [MODIFY] @[backend_v2/models/view/sdui.py]
- Lisätään `CausalGraphBlock(AnySduiBlock)` polymorfiseen SDUI-blokkijoukkoon.
- Sisältää interaktiivisen graafin renderöintitiedot (`nodes`, `edges`, `blame_attributions`, `summary`).

#### [NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
- Toteutetaan adapteri, joka muuntaa `EngineExecutionResult`:n `CausalGraphBlock`-lohkoiksi raportointinäkymään.

#### [NEW] @[client_app_v2/lib/features/execution/presentation/causal_graph_view.dart]
- Toteutetaan Flutter-komponentti interaktiivisen suunnatun graafin visualisointiin (solmut, kaaret, syyllisyyskaskadit, sitaattitarkastelu).

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="SETTINGS_AND_DTO_FOUNDATION">
    <action>Add causal discovery configuration parameters to `settings.py`.</action>
    <action>Add `CAUSAL_DISCOVERY` engine override and `CAUSAL_GRAPH` block type to `models/enums.py`.</action>
    <action>Create strictly typed immutable DTOs in `models/dtos/causal_discovery.py`.</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce ConfigDict(strict=True, extra='forbid', frozen=True) on all DTOs with zero naked dicts.</constraint>
    <constraint invariant="dry_composition_mandate">Reuse existing CausalEdge and ExtractedAtom types rather than inventing duplicate models.</constraint>
  </step>

  <step id="2" name="ENGINE_IMPLEMENTATION">
    <action>Implement `CausalDiscoveryEngine` in `services/orchestrator/engines/causal_discovery_engine.py`.</action>
    <action>Wire `TwoPassAtomizer` (Phase 0 &amp; Phase 1) and `SlidingWindowLinker` sequentially with progress reporting callbacks.</action>
    <action>Pass generated LinkedAtomGraph to `EnrichedDagExecutor` for wave-based topological evaluation.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Keep CausalDiscoveryEngine completely separate from TDAEngine with zero shared fallback branches.</constraint>
    <constraint invariant="anti_god_file_dumping">Isolate engine logic strictly in its own file under 200 lines.</constraint>
  </step>

  <step id="3" name="DAG_ROUTER_INTEGRATION">
    <action>Mount `CausalDiscoveryEngine` in `dag_executor.py` under `EngineOverrideStrategy.CAUSAL_DISCOVERY`.</action>
    <constraint invariant="engine_override_ban">Ensure routing resolves deterministically from step blueprint metadata or explicit typed override.</constraint>
  </step>

  <step id="4" name="SDUI_MODEL_AND_ADAPTER">
    <action>Add `CausalGraphBlock` to `models/view/sdui.py`.</action>
    <action>Implement `CausalGraphAdapter` in `services/sdui/adapters/causal_graph_adapter.py`.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Ensure 100% semantic parity between Python SDUI model and Flutter Freezed representation.</constraint>
  </step>

  <step id="5" name="CLIENT_APP_VISUALIZATION">
    <action>Implement interactive Flutter DAG visualizer widget in `client_app_v2`.</action>
    <constraint invariant="flutter_audit_execution">Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build` to compile Freezed models.</constraint>
  </step>

  <step id="6" name="UNIT_TESTING_AND_VERIFICATION">
    <action>Create comprehensive ISTQB unit tests in `test_causal_discovery_engine.py` covering Happy Path, Cyclic graph handling, Data starvation, and Blame cascading.</action>
    <constraint invariant="backend_audit_execution">Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py --test`.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Engine Unit & Equivalence Tests**:
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py --test`
   - Testaa vapaamuotoisen tekstin 2-vaiheisen uuton ja linkityksen läpiviennin.
   - Testaa short-circuit -kaskadin ja syyllisyysattribuution, kun juuriväite hylätään.
   - Testaa kehäriippuvuuksien eristyksen (`CYCLIC_DEPENDENCY_DETECTED`).
2. **Frontend UI Parity Gate**:
   - `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`
   - Varmistaa Freezed-mallien ja SDUI-lohkojen 1:1 vastaavuuden.
3. **Markdown Boundary Audit**:
   - `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Engine.md`

### Manual Verification
1. Syötetään Studio-testityökalussa monimutkainen monisivuinen teksti, jossa on syy-seuraussuhteita.
2. Tarkastetaan, että Flutter-käyttöliittymässä avautuu interaktiivinen kausaaliverkko.
3. Klikataan solmua ja tarkistetaan, että sen sitaatti ja vanhempien tilat visualisoituvat oikein ilman kaatumisia.
