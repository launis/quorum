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
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
</required_context_rules>
```

# Implementation Plan - Dynamic Causal Discovery Engine (Exploratory Text DAG & Argument Mapping)

> [!CAUTION]
> **KAUKAISEN TULEVAISUUDEN TIEKARTTA (DISTANT FUTURE ROADMAP ONLY)**
> Tämä toteutussuunnitelma on laadittu varastoon tulevaisuuden laajennusta varten eikä se kuulu nykyiseen aktiiviseen kehityssykliin. Suunnitelma kuvaa valinnaisen ja kokeellisen avoimen tekstin kausaalianalyysin (*Exploratory Causal Discovery Engine*), joka analysoi vapaamuotoisia dokumentteja ilman ennalta määriteltyä arviointimatriisia. Tätä **EI** tule aktivoida osana nykyistä normatiivista arviointiydintä, eikä se saa heikentää `TDAEngine`-moottorin nykyistä determinismiä tai tiukkaa `shuffled_atoms`-vaatimusta.

---

## User Review Required

> [!IMPORTANT]
> **Täysi Itsenäinen ja Irrallinen Käyttötila (Standalone Engine Mandate):**
> `CausalDiscoveryEngine` toteutetaan ja pidetään ensisijaisesti **100 % itsenäisenä ja irrallisena analyysimoottorina**.
> - Moottoria voidaan ajaa täysin erillisenä ilman `TDAEngine`-riippuvuutta, ilman ennalta määriteltyä arviointimatriisia ja ilman kriteerilohkoja.
> - Se ei edellytä `request.shuffled_atoms` -syötettä, vaan louhii vapaamuotoisesta tekstistä itsenäisesti argumenttirakenteen, muodostaa suunnatun argumenttiverkon (`LinkedAtomGraph`), suorittaa topologisen arvioinnin ja tuottaa valmiin visualisoitavan raportin (`SduiCausalGraphBlock`).
> - Itsenäisessä tilassa solmujen värit ja tilat heijastavat suoraan argumenttien topologista validiteettia (määriteltyinä: Vihreä = validoitu väite, Punainen = hylätty/kumottu väite, Oranssi = kaskadoitunut virhe, Harmaa = orpo käsite).
>
> **Single Pipeline Invariant & Zero-Fallback Compliance:**
> `CausalDiscoveryEngine` ja `TDAEngine` pidetään toisistaan täysin erillisinä `ExecutionEngine`-moottoreina. `CausalDiscoveryEngine` kytketään askeleelle `step_def.model_strategy == "causal_discovery"` -tunnisteella. Se **EI** saa olla minkäänlainen fallback-haara `TDAEngine`n sisällä, eikä moottoreita yhdistetä yhdeksi monoliittiseksi luokaksi. `TDAEngine` säilyttää 100 % tiukan Fail-Fast-sopimuksensa (`request.shuffled_atoms` pakollinen).
>
> **Valinnainen Kausaaligraafin ja TDA-matriisin Fuusio (Kaksi erillistä moottoria $\rightarrow$ Yksi tulos):**
> Kun työnkulussa halutaan yhdistää normatiivinen kriteeriarviointi ja vapaa kausaaliverkko, niitä ei ajeta erillisinä toisistaan irrallisina raportteina, vaan ne kytketään yhdeksi kaksivaiheiseksi analyysiputkeksi:
> 1. **Putkikytkentä (Discovery louhii $\rightarrow$ TDA evaluoi):**
>    Työnkulussa ei valita jompaakumpaa moottoria satunnaisesti, vaan ne ketjutetaan DAG-tasolla kahdeksi deterministiseksi vaiheeksi:
>    - **Vaihe 1A (`CausalDiscoveryEngine`):** Moottori analysoi vapaan tekstin ja rakentaa siitä suunnatun argumenttiverkon (`LinkedAtomGraph`), eristäen premissit, väitteet ja johtopäätökset erillisiksi atomisolmuiksi.
>    - **Vaihe 1B (`TDAEngine`):** TDA-moottori ei arvioi koko tekstimassaa satunnaisesti, vaan se ottaa syötteekseen juuri nämä löydetyt kausaalisolmut (`ExtractedAtom` $\rightarrow$ `shuffled_atoms`) ja testaa niitä normatiivisen matriisin kriteereillä (tarkastukset: Warrant-kytkentä, Backing-taustatuki, dogmaattiset kvanttorit ja matriisiasteikot).
>    - **Lopputulos:** Yksi ainoa analyysiprosessi, jossa kausaalianalyysi toimii rakenteen jäsentäjänä ja TDA toimii sen laadullisena tuomarina.
> 2. **Semanttinen päällekkäisasettelu käyttöliittymässä (Semantic Overlay):**
>    Käyttöliittymään ei luoda kahta eri välilehteä tai rinnakkaista erillisraporttia, vaan Flutterin SDUI-kerrokseen tuotetaan yksi interaktiivinen graafi (`SduiCausalGraphBlock`):
>    - Solmujen väliset nuolet näyttävät tekstin loogisen etenemisen ja syy-seuraussuhteet (Discovery-moottorin tuottama topologia).
>    - Solmujen värit ja tasot tulevat fuusiotilassa suoraan TDA-matriisista (määriteltyinä: Vihreä = perusteltu väite, Punainen = dogmaattinen oletus ilman taustatukea).
>    - **Lopputulos:** Arvioija näkee yhdellä silmäyksellä tekstin loogisen rakenteen ja kunkin argumentin laadun suoraan solmun visuaalisesta tilasta.
> 3. **Kausaalinen juurisyydiagnoosi osana pisteytystä:**
>    Yhdistetään Causal Discoveryn syyllisyysattribuutio (`blame_parent_ids`) suoraan TDA-pisteiden vähennyksiin ja sanalliseen perusteluun:
>    - Jos kirjoittaja menettää pisteitä arviointikohdassa "Väitteiden perustelu", järjestelmä ei anna vain yleistä palautetta, vaan raportoi kausaalisen polun: *"Johtopäätös B hylättiin, koska se nojaa solmun A virheelliseen oletukseen kappaleessa [B2]"*.
>    - **Lopputulos:** Kokonaispistemäärä ja sen sanallinen perustelu muodostavat yhden riidattoman ja läpinäkyvän kokonaisuuden.
>
> **Loppukäyttäjän ja Arvioijan Viisi Konkreettista Hyötyä (Five Core Stakeholder Benefits):**
> Riippumatta siitä, ajetaanko moottoria itsenäisenä vai yhdessä TDA-matriisin kanssa, järjestelmä tuottaa viisi konkreettista hyötyä:
> 1. **Korttitaloefektin ja juurisyyn paljastaminen (Root Cause Attribution):**
>    - *Ongelma ilman graafia:* Perinteinen rubriikki sakottaa kirjoittajaa erikseen jokaisesta ontuvasta väitteestä, vaikka kaikki virheet johtuisivat yhdestä ainoasta väärästä pohjaoletuksesta.
>    - *Hyöty lopputuotteessa:* Järjestelmä suorittaa topologisen syyllisyyskaskadin (`blame_parent_ids`). Loppuraportti ei vain totea johtopäätöksen hylkäystä, vaan osoittaa suoraan: *"Johtopäätös C hylättiin, koska se nojaa kappaleessa [B2] esitettyyn virheelliseen premissiin A"*. Arvioitava ja arvioija ymmärtävät välittömästi, mistä virhe kumpusi.
> 2. **Suoja tekoälyn tuottamaa "avainsanahöttöä" vastaan (Anti-Fluff Shield):**
>    - *Ongelma ilman graafia:* Generatiivisella tekoälyllä laadittu teksti osaa usein mainita kaikki rubriikin vaatimat termit ja teoriat (käsitteet: Data, Claim, Warrant, Backing, Qualifier, Rebuttal), jolloin se läpäisee laadullisen matriisitarkistuksen ilman aitoa päättelyketjua.
>    - *Hyöty lopputuotteessa:* Kausaaliverkko testaa, muodostavatko käsitteet todellisen loogisen ketjun vai leijuvatko ne irrallaan. Jos premissit eivät johda väitteeseen tai päättely on kehämäistä (`cycle_detected`), järjestelmä pudottaa arvosanaa riippumatta siitä, kuinka sujuvaa kieli on.
> 3. **Arvosanasta täsmäkorjaukseen (Prescriptive Feedback):**
>    - *Ongelma ilman graafia:* Palaute jää usein yleiselle tasolle: *"Perustele väitteesi paremmin ja syvennä teoreettista taustatukea."*
>    - *Hyöty lopputuotteessa:* Lopputuote antaa kirjoittajalle kirurgisen tarkan toimenpidesuosituksen: *"Korjaamalla solmun 3 taustatuki (Backing), validoidaan samalla siitä riippuvat jatkoväitteet 5 ja 8."* Tämä tekee palautteesta aidosti kehittävää ja toiminnallista.
> 4. **Interaktiivinen "kognitiivinen röntgenkuva" käyttöliittymässä (Visual XAI):**
>    - *Ongelma ilman graafia:* Tuloste on vain pitkä taulukko tai staattinen tekstiraportti.
>    - *Hyöty lopputuotteessa:* Lopputuotteena syntyy yksi yhtenäinen Flutter SDUI -näkymä (`SduiCausalGraphBlock`), jossa tekstin looginen eteneminen näkyy suorana argumenttikarttana. Solmun väri kertoo kriteeritoteutuksen tai loogisen tilan (määriteltyinä: Vihreä = perusteltu väite, Punainen = dogmaattinen oletus tai virheellinen premissi), ja klikkaamalla solmua näytölle aukeaa suora leksikaalinen sitaatti alkuperäisestä tekstistä sekä sen vanhempien tila.
> 5. **Kohtuullinen ja oikeudenmukainen osapisteytys (Fair & Deduplicated Scoring):**
>    - *Ongelma ilman graafia:* Opiskelijaa rangaistaan moninkertaisesti, jos hän toistaa saman yhden loogisen lipsahduksen työn eri osioissa, tai arviointi ei erota yhtä juurisyytä useista toisistaan riippumattomista virheistä.
>    - *Hyöty lopputuotteessa:* Graafi mahdollistaa älykkään pisteytyslogiikan: opiskelijaa ei rangaista viittä kertaa, jos hän toistaa saman yhden loogisen lipsahduksen työn eri osioissa. Järjestelmä tunnistaa saman virheen heijastumat ja erottaa sen tilanteesta, jossa opiskelijalla on viisi toisistaan riippumatonta asiavirhettä.
>
> **SSOT ja Pydantic V2 -sopimukset:**
> Kaikki graafin solmut (`LinkedAtomGraph`), reunat (`CausalEdge`), uutetut väitteet (`ExtractedAtom`), fuusiodiagnoosit (`CausalRootCauseDiagnosisDTO`), anti-fluff -tarkastusraportit (`AntiFluffAuditDTO`), korjaussuositukset (`PrescriptiveRemediationDTO`), osapisteytyksen erittelyt (`FairScoringBreakdownDTO`) ja SDUI-lohkot (`SduiCausalGraphBlock`) noudattavat tiukkaa `ConfigDict(strict=True, extra='forbid', frozen=True)` -mallia ilman paljaita sanakirjoja (`dict[str, Any]`).
>
> **Resurssien hallinta ja tausta-ajo (Arq Worker):**
> Koska dynaaminen uutto ja liukuva linkitys vaativat useita peräkkäisiä ja rinnakkaisia LLM-kutsuja (Phase 0 ontologia $\rightarrow$ Phase 1 lohkot $\rightarrow$ Sliding Window linkitys $\rightarrow$ Topologinen evaluointi), moottori ajetaan aina asynkronisessa taustaprosessissa (`worker.py`), raportoiden edistymistä reaaliaikaisesti SSE-virtaan.

---

## Scope & Boundaries

### Target Files:
- `[NEW]` @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- `[NEW]` @[backend_v2/models/dtos/causal_discovery.py]
- `[NEW]` @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/models/view/sdui.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]
- `[NEW]` @[client_app_v2/lib/features/execution/presentation/causal_graph_view.dart]

### Context / Read-Only Files:
- `@[backend_v2/services/orchestrator/engines/base.py]`
- `@[backend_v2/services/orchestrator/engines/tda_engine.py]`
- `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`
- `@[backend_v2/services/orchestrator/sliding_window_linker.py]`
- `@[backend_v2/services/orchestrator/topological_evaluator.py]`
- `@[backend_v2/services/orchestrator/result_projector.py]`
- `@[backend_v2/services/blueprint.py]`
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
  - `causal_secondary_fault_dampening: float = 0.25`

#### [NEW] @[backend_v2/models/dtos/causal_discovery.py]
- Määritellään ja created tyypitetyt DTO-mallit, jotka tukevat sekä itsenäistä että fuusioitua ajoa:
  - `CausalNodeDTO(BaseModel)`: created malli kentillä `node_id: str`, `claim: str`, `source_quote: str | None`, `paragraph_ref: str | None`, `status: ExecutionStatus`, `blame_parent_ids: list[str]`, `dependent_child_ids: list[str]`, `tda_score: float | None = None`, `tda_level_key: str | None = None`, `tda_color: str | None = None`. (TDA-kentät ovat oletuksena `None` itsenäisessä tilassa).
  - `CausalEdgeDTO(BaseModel)`: created malli kentillä `source_id: str`, `target_id: str`, `reasoning: str`.
  - `CausalGraphPayloadDTO(BaseModel)`: created itsenäinen tuloskuorma kentillä `nodes: list[CausalNodeDTO]`, `edges: list[CausalEdgeDTO]`, `root_cause_node_ids: list[str]`, `cycle_detected: bool`, `isolated_node_ids: list[str]`.
  - `CausalRootCauseDiagnosisDTO(BaseModel)`: defining malli juurisyyattribuutiolle (Hyöty 1) kentillä `failing_node_id: str`, `root_cause_parent_id: str`, `paragraph_ref: str`, `explanation: str`, `penalty_points: float`.
  - `AntiFluffAuditDTO(BaseModel)`: defining malli avainsanahötön tunnistukselle (Hyöty 2) kentillä `isolated_concept_count: int`, `cycle_detected: bool`, `unsupported_claims_count: int`, `logical_cohesion_score: float`, `detected_hollow_terms: list[str]`.
  - `PrescriptiveRemediationDTO(BaseModel)`: defining malli täsmäkorjaukselle (Hyöty 3) kentillä `target_node_id: str`, `required_action: str`, `unlocks_node_ids: list[str]`, `potential_score_impact: float`.
  - `FairScoringBreakdownDTO(BaseModel)`: defining malli oikeudenmukaiselle osapisteytykselle (Hyöty 5) kentillä `independent_error_count: int`, `cascading_fault_count: int`, `raw_penalty_points: float`, `deduplicated_penalty_points: float`, `dampened_savings_points: float`.
  - `CausalTdaFusionResultDTO(BaseModel)`: defining kokoomamalli valinnaiselle fuusiotilalle kentillä `graph: CausalGraphPayloadDTO`, `root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO]`, `anti_fluff_audit: AntiFluffAuditDTO`, `prescriptive_remediations: list[PrescriptiveRemediationDTO]`, `fair_scoring: FairScoringBreakdownDTO`.

---

### Phase 2: Engine Implementation & Orchestrator Wiring (Standalone & Optional Fusion)

#### [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- Toteutetaan `CausalDiscoveryEngine(ExecutionEngine)`:
  - Konstruktorissa injektoidaan `prompt_compiler: PromptCompiler`.
  - Moottori on täysin itsenäinen ja decoupled: se ei importoi `TDAEngine`a eikä vaadi arviointimatriisia toimiakseen.
  - `execute(request: EngineExecutionRequest) -> EngineExecutionResult`:
    1. **Pre-flight Ingress & Hydration**: Alustaa `AliasEngine`, numeroi kappaleet (`[B0]...[Bn]`).
    2. **Phase 0 (Global Ontology)**: Kutsuu `TwoPassAtomizer.execute_phase_0` rakentaen `GlobalOntologyMap` -olion.
    3. **Phase 1 (Chunked Claim Extraction)**: Kutsuu `TwoPassAtomizer.execute_phase_1` muodostaen itsenäiset `ExtractedAtom`-oliot anaforat korvattuna.
    4. **Sliding Window Linking**: Kutsuu `SlidingWindowLinker.link_graph` kytkien atomit suunnatuksi `LinkedAtomGraph`-verkoksi (`CausalEdge`).
    5. **Topological Wave Execution**: Ajaa verkon `EnrichedDagExecutor`/`TopologicalEvaluator`-läpi short-circuit -kaskadeineen ja blame-attribuutioineen.
    6. **Standalone Result Projection**: Projisoi itsenäisen kausaaliverkon tilat `ResultProjector.project()`:lla palauttaen `EngineExecutionResult`:n, joka sisältää itsenäisen argumenttikartan ja syyllisyysattribuution.

#### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py]
- Lisätään `_resolve_execution_engine`:n reititykseen tuki `step_def.model_strategy == "causal_discovery"`:
  - Injektoi puhtaasti `CausalDiscoveryEngine(self.deps.prompt_compiler)`.
  - Mahdollistaa askeleen suorittamisen joko **täysin itsenäisenä (Standalone)** tai osana ketjutettua työnkulkua.
- **Valinnainen ketjutus (Vaihe 1A $\rightarrow$ Vaihe 1B):**
  - Jos työnkulku määrittelee vaiheen 1A (`causal_discovery`) ja vaiheen 1B (`tda`), vaiheen 1A tuottamat solmut välitetään tyypitettyinä atomeina vaiheen 1B syötteeksi.
  - Jos työnkulku sisältää vain askeleen `causal_discovery`, se suoritetaan itsenäisenä maaliin asti tuottaen oman raporttinsa ilman TDA-vaihetta.
- **Viiden hyödyn laskentalogiikka putkessa:**
  - **Hyöty 1 (Root Cause Attribution):** Kartoittaa `blame_parent_ids`-polun ja muodostaa `CausalRootCauseDiagnosisDTO`-tietueet.
  - **Hyöty 2 (Anti-Fluff Shield):** Havaitsee orvot solmut ilman premissiyhteyttä tai kehämäiset riippuvuudet (`cycle_detected`) ja muodostaa `AntiFluffAuditDTO`-raportin.
  - **Hyöty 3 (Prescriptive Feedback):** Etsii solmut, joiden korjaaminen vapauttaa useita lapsisolmuja (`unlocks_node_ids`) ja generoi `PrescriptiveRemediationDTO`-suositukset.
  - **Hyöty 5 (Fair & Deduplicated Scoring):** Erottelee toisistaan riippumattomat juurisyyvirheet ja alisteiset kaskadivirheet, soveltaen kaskadivirheisiin vaimennettua sakotusta (`causal_secondary_fault_dampening`) ja muodostaen `FairScoringBreakdownDTO`-erittelyn.

---

### Phase 3: SDUI Presentation & Client Visualization (Standalone & Semantic Overlay)

#### [MODIFY] @[backend_v2/models/view/sdui.py]
- Lisätään `SduiCausalGraphBlock(SduiBlockBase)` polymorfiseen SDUI-blokkijoukkoon `AnySduiBlock`.
- Sisältää interaktiivisen graafin renderöintitiedot:
  - `nodes: list[CausalNodeDTO]`
  - `edges: list[CausalEdgeDTO]`
  - `root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO]`
  - `anti_fluff_audit: AntiFluffAuditDTO`
  - `prescriptive_remediations: list[PrescriptiveRemediationDTO]`
  - `fair_scoring: FairScoringBreakdownDTO | None = None`
  - `summary: I18nText`
- Tukee sekä itsenäistä renderöintiä että semanttista päällekkäisasettelua (Visual XAI):
  - Itsenäisessä tilassa solmujen värit kuvaavat argumenttien validiteettia ja topologista tilaa.
  - Fuusiotilassa solmujen värit heijastavat TDA-matriisin arviointia.

#### [NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
- Toteutetaan adapteri, joka muuntaa `EngineExecutionResult`:n `SduiCausalGraphBlock`-lohkoiksi raportointinäkymään:
  - Osaa renderöidä graafin itsenäisenä ilman TDA-kenttiä.
  - Osaa yhdistää TDA-matriisin tiedot semanttiseksi päällekkäisasetteluksi, jos fuusio on ajettu.

#### [NEW] @[client_app_v2/lib/features/execution/presentation/causal_graph_view.dart]
- Toteutetaan Flutter-komponentti interaktiivisen suunnatun graafin visualisointiin (Visual XAI):
  - Toimii täysin itsenäisenä argumenttikarttana ja tukee myös semanttista päällekkäisasettelua.
  - Suunnatut kaaret näyttävät argumenttien loogisen etenemisen.
  - Solmun väri ilmaisee tilan (itsenäisessä tilassa validiteetti, fuusiotilassa TDA-kriteeri).
  - Solmua klikkaamalla esitetään suora leksikaalinen sitaatti tekstistä, juurisyydiagnoosi, anti-fluff -huomautus ja preskriptiivinen täsmäkorjaus.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="SETTINGS_AND_DTO_FOUNDATION">
    <action>Add causal discovery configuration parameters to `settings.py` including `causal_secondary_fault_dampening`.</action>
    <action>Create strictly typed immutable DTOs in `models/dtos/causal_discovery.py` supporting standalone execution and optional fusion (CausalNodeDTO, CausalEdgeDTO, CausalGraphPayloadDTO, CausalRootCauseDiagnosisDTO, AntiFluffAuditDTO, PrescriptiveRemediationDTO, FairScoringBreakdownDTO, and CausalTdaFusionResultDTO).</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce ConfigDict(strict=True, extra='forbid', frozen=True) on all DTOs with zero naked dicts.</constraint>
    <constraint invariant="dry_composition_mandate">Reuse existing CausalEdge and ExtractedAtom types rather than inventing duplicate models.</constraint>
  </step>

  <step id="2" name="STANDALONE_ENGINE_IMPLEMENTATION">
    <action>Implement `CausalDiscoveryEngine` in `services/orchestrator/engines/causal_discovery_engine.py` as a standalone engine without any TDAEngine dependencies.</action>
    <action>Wire `TwoPassAtomizer` (Phase 0 and Phase 1) and `SlidingWindowLinker` sequentially with progress reporting callbacks.</action>
    <action>Pass generated LinkedAtomGraph to `EnrichedDagExecutor` for wave-based topological evaluation, blame cascading, and anti-fluff checks.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Keep CausalDiscoveryEngine completely separate from TDAEngine with zero shared fallback branches.</constraint>
    <constraint invariant="anti_god_file_dumping">Isolate engine logic strictly in its own file under 200 lines.</constraint>
  </step>

  <step id="3" name="DAG_ROUTER_AND_OPTIONAL_FUSION">
    <action>Mount `CausalDiscoveryEngine` in `dag_executor.py` under `step_def.model_strategy == "causal_discovery"` supporting standalone execution.</action>
    <action>Wire optional sequential DAG chaining allowing Step 1A (CausalDiscoveryEngine) outputs to feed directly into Step 1B (TDAEngine) shuffled_atoms input when configured.</action>
    <action>Implement five stakeholder benefit pipelines: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI data projection, and Fair Scoring Deduplication.</action>
    <constraint invariant="engine_override_ban">Ensure routing resolves dynamically and deterministically from step blueprint model_strategy without hardcoded override flags.</constraint>
  </step>

  <step id="4" name="SDUI_MODEL_AND_ADAPTER">
    <action>Add `SduiCausalGraphBlock` to `models/view/sdui.py` supporting both standalone presentation and Semantic Overlay.</action>
    <action>Implement `CausalGraphAdapter` in `services/sdui/adapters/causal_graph_adapter.py`.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Ensure 100% semantic parity between Python SDUI model and Flutter Freezed representation.</constraint>
  </step>

  <step id="5" name="CLIENT_APP_VISUALIZATION">
    <action>Implement interactive Flutter DAG visualizer widget in `client_app_v2` with standalone argument graph view, semantic overlay, and lexical quote inspection.</action>
    <constraint invariant="flutter_audit_execution">Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build` to compile Freezed models.</constraint>
  </step>

  <step id="6" name="UNIT_TESTING_AND_VERIFICATION">
    <action>Create comprehensive ISTQB unit tests in `test_causal_discovery_engine.py` covering standalone execution (Happy Path, Cyclic graph handling, Data starvation, and Blame cascading).</action>
    <action>Create integration test `test_causal_tda_fusion.py` verifying optional sequential pipeline chaining and the five stakeholder benefits.</action>
    <constraint invariant="backend_audit_execution">Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py --test`.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Standalone Engine Unit & Equivalence Tests**:
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py --test`
   - Testaa vapaamuotoisen tekstin itsenäisen 2-vaiheisen uuton ja linkityksen ilman matriiseja tai TDAEngineä.
   - Testaa itsenäisen syyllisyysattribuution ja short-circuit -kaskadin toiminnan.
   - Testaa kehäriippuvuuksien eristyksen (`CYCLIC_DEPENDENCY_DETECTED`) ja orpojen käsitteiden tunnistuksen (`AntiFluffAuditDTO`).
2. **Optional Chained Fusion Integration Tests**:
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py --test`
   - Testaa kahden erillisen moottorin valinnaisen ketjutuksen (Vaihe 1A $\rightarrow$ Vaihe 1B).
   - Testaa Hyöty 1: Juurisyyattribuutio (`blame_parent_ids`) osoittaa oikean kausaalisen polun.
   - Testaa Hyöty 2: Anti-Fluff Shield havaitsee orvot käsitteet ja kehäpäätelmät.
   - Testaa Hyöty 3: Prescriptive Feedback generoi toiminnalliset täsmäkorjaukset vapautettavine solmuineen.
   - Testaa Hyöty 4: Visual XAI projisoi graafin ja leksikaaliset sitaatit `SduiCausalGraphBlock`-malliin.
   - Testaa Hyöty 5: Fair Scoring erottaa yhden juurisyyn kaskadivirheineen monesta itsenäisestä virheestä ja vaimentaa sekundäärisen sakon.
3. **Frontend UI Parity Gate**:
   - `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`
   - Varmistaa Freezed-mallien ja SDUI-lohkojen 1:1 vastaavuuden sekä itsenäisessä että fuusiotilassa.
4. **Markdown Boundary Audit**:
   - `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Engine.md`

### Manual Verification
1. Aja `CausalDiscoveryEngine` täysin itsenäisenä työnkulkuna vapaalle tekstille ilman matriiseja: tarkista, että itsenäinen argumenttikartta visualisoituu ilman virheitä.
2. Aja ketjutettu työnkulku (Vaihe 1A $\rightarrow$ Vaihe 1B): tarkista, että TDA-semanttinen päällekkäisasettelu (Semantic Overlay) ja juurisyydiagnoosi rikastavat saman graafin.
3. Klikkaa solmuja molemmissa tiloissa ja varmista leksikaalisten sitaattien moitteeton esitys.
