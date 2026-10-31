# Arkkitehtuurin ja Tietomallien Parannuskohteet

Tähän dokumenttiin on koottu järjestelmän koodikannassa, tietomalleissa ja laatuporteissa **avoinna ja toteuttamatta olevat** arkkitehtuuriset parannuskohteet sekä jo suoritettujen ja lukittujen arkkitehtuurikokonaisuuksien tilannekuva. Dokumentti noudattaa `anti_ambiguity_mandate`-sääntöä, *No Hidden Scope* -periaatetta sekä Quorumin *Zero-Tolerance* -laatuvaatimusta ilman siirtymäajan purkkaratkaisuja.

*(Huomautus: Aiemmin tässä dokumentissa olleet matriisiskaalauksen keskitys `computed_min`/`computed_max`, `theory_grounding` vs. `ai_description` -eriyttäminen, `I18nText.default_locale`-poisto, `MatrixClaim.ai_description` -> `TDAAssertion.concept_description` -keskitys, `OutputProfile.matrix_synthesis_groups` & L10n-siivous, Karkaisuaallot 1 [36/36], 2 [36/36], 3 [27/27] ja 4 [34/34] = 133/133 tiedostoa, Luvun 2 Malli A:n yhtenäinen 32-hex `PrefixedUUID7`-arkkitehtuuri ja legacy `UUIDv4`-generaattoreiden poisto [`15/15` & `31/31` karkaistu], Luvun 3 AST-laatuportit `QGR020`/`QGR031`–`QGR033` ja SHA-256-karkaisuvälimuisti sekä Luvun 4 FastAPI-reitittimien SSOT-konsolidointi [`22/22` karkaistu] on toteutettu, karkaistu, auditoitu ja lukittu.)*

---

## Luku 1: Backend-koodikannan Karkaisuaallot 1–4 (133/133 Tiedostoa Suoritettu)
> **STATUS: SUORITETTU & LUKITTU (Aallot 1 [36/36], 2 [36/36], 3 [27/27] ja 4 [34/34] = 133/133 valmiit; 391/403 backend-tiedostoa = 97,0 % lukittu)**
> *Selite: Synkronoitu päätoteutussuunnitelman `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]` (Askeleet 3.2 – 3.2d) kanssa.*

### 1.1 Koko `backend_v2/`-Tuotantokoodikannan Tilannekuva (403 `.py`-tiedostoa)

Koko `backend_v2/`-hakemiston (pl. `tests/`) 403 tuotantotiedoston tilannekuva:

| Kategoria | Tiedostomäärä | Tila ja seurantadokumentti |
| :--- | :--- | :--- |
| **1. Valmiiksi karkaistut ja lukitut tuotantotiedostot** | `391` kpl | Sisältää `__init__.py`-fasaadit (`47` kpl), aiemmissa puruissa karkaistut moduulit (`162` kpl), entuudestaan 100 % puhtaat tiedostot (`49` kpl) sekä valmistuneet Karkaisuaallot 1 (`36/36`), 2 (`36/36`), 3 (`27/27`) ja 4 (`34/34`). |
| **2. Tulevat arkkitehtuurivaiheet (IAM & Storage)** | `12` kpl | Eristetty vaiheisiin `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` (9 tiedostoa) ja `[NEW]` `@[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]` (3 tiedostoa). |
| **YHTEENSÄ** | **403 kpl** | **391 / 403 valmiina (97,0 %), 12 kpl IAM/Storage-vaiheissa (Askeleet 4 & 5)** |

---

### 1.2 Valmistuneet Karkaisuaallot 1–4 (`133/133`) ja Jäljellä Olevat 12 Kohdetiedostoa

Kaikki neljä kohdennettua backend-karkaisuaaltoa sekä jokaisen aallon *Final Macro-Audit Completion Gate* on suoritettu, auditoitu ja lukittu:
* **Aalto 1 (`36/36` valmis):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]` — Workers, SDUI Adapters & Shared Utilities.
* **Aalto 2 (`36/36` valmis):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]` — Core, Observability, Deterministic Hooks, LLM Provider Adapters & Studio/Execution Services.
* **Aalto 3 (`27/27` valmis):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]` — Repositories, Orchestrator Services & non-IAM FastAPI Routers.
* **Aalto 4 (`34/34` valmis, commit `1af36b166`):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]` — Domain Models (`23` tiedostoa) & DTO/Prompt Schemas (`11` tiedostoa).

Jäljellä olevat **12 avointa tuotantotiedostoa** (`3,0 %` koko `backend_v2/`-koodikannasta) karkaistaan ja lukitaan osana omia tulevia arkkitehtuurivaiheitaan:
* **Askel 4 — `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` (9 tiedostoa, nimenomaan ja tyhjentävästi):**
  1. `@[backend_v2/models/auth.py]`
  2. `@[backend_v2/services/auth/constants.py]`
  3. `@[backend_v2/services/auth/repositories.py]`
  4. `@[backend_v2/services/auth/token_service.py]`
  5. `@[backend_v2/services/auth/organization_service.py]`
  6. `@[backend_v2/services/auth/user_service.py]`
  7. `@[backend_v2/api/routers/iam/auth.py]`
  8. `@[backend_v2/api/routers/iam/organizations.py]`
  9. `@[backend_v2/api/routers/iam/users.py]`
* **Askel 5 — `[NEW]` `@[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]` (3 tiedostoa, nimenomaan ja tyhjentävästi):**
  1. `@[backend_v2/services/file_driver.py]`
  2. `@[backend_v2/services/drivers/local_file_driver.py]`
  3. `@[backend_v2/services/storage.py]`

---

## Luku 2: Yhtenäinen `PrefixedUUID7`-tunnistearkkitehtuuri, Natiivi PostgreSQL 19 `UUIDv7` ja Legacy `UUIDv4`-generaattoreiden Poisto (Malli A)
> **STATUS: SUORITETTU, KOVENNETTU & LUKITTU (`@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` [15/15 karkaistu] & `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` [31/31 karkaistu])**
> *Selite: Poisti vanhan 16-merkkisen `UUIDv4`-katkaisun, `TEXT PRIMARY KEY` -hybridijaon sekä kaikki jäljellä olleet `uuid.uuid4()`- ja `Uuid().v4()`-generaattorit koko Python-backendistä ja Flutter-asiakassovelluksesta. Yhdistää Opaque Stripe ID -etuliitteet ja PostgreSQL 19:n natiivin 16-tavuisen RFC 9562 `UUIDv7` -tietotyypin yhdeksi poikkeuksettomaksi standardiksi.*

### 2.1 Ratkaistu ongelma ja kahden peräkkäisen toteutussuunnitelman kokonaisuus

Ennen Askeleen 3.3 toteutusta järjestelmän entiteettitunnisteet olivat jakautuneet kahteen rinnakkaiseen tallennus- ja generointimekanismiin (5 `UUID`-taulua 32-heksalla vs. 7 `TEXT`-taulua 16-heksalla). Lisäksi kun ensimmäinen cutover-suunnitelma (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]`) oli suoritettu ja järjestelmää testattiin käyttöliittymässä sekä yksikkö- ja integraatiotesteissä, havaittiin, että osa sisäisistä apu- ja asiakaspuolen generaattoreista kutsui yhä vanhaa `uuid.uuid4()`- tai `Uuid().v4()`-funktiota ja katkaisi tunnisteita 8 tai 16 heksamerkkiin.

Tämän vuoksi Luvun 2 kokonaisuus toteutettiin, dokumentoitiin (`/tier7-describe-architecture`), auditoitiin (`/tier8-audit-plan`) ja karkaistiin (`Tier 2 Hardening` via `@[scripts/auto_hardening_runner.py]`) kahdella toisiaan täydentävällä toteutussuunnitelmalla ja seurantadokumentilla:
1. **Osa 3.3a — `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]` & `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` (Steps 1–5 valmiit; `Tier 2 Hardening`: `14/14` Backend + `1/1` Frontend = `15/15` karkaistu ja lukittu):**
   * Kaikkien 12 PostgreSQL 19 -taulun natiivi `UUIDv7` DDL-skeema (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`), symmetrinen adapterisilta (`@[backend_v2/database/postgres/entity_adapter.py]`), `OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"` (`@[backend_v2/models/core_base.py]`), koko `@[backend_v2/seed/seed_data.json]`-tiedoston deterministinen 32-hex `UUIDv7` -migraatio, `@[scripts/sanitize_seed_vault.py]`-automaatio, Studio-oletusankkureiden poisto, kausaalisen koheesiomatriisin suora sidonta sekä `@[docs/tiede.md]`-graafimatematiikan synkronointi.
2. **Osa 3.3b — `@[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` & `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` (Steps 1–5 valmiit; `Tier 2 Hardening`: `24/24` Backend + `7/7` Frontend = `31/31` karkaistu ja lukittu):**
   * Kaikkien jäljellä olleiden `uuid.uuid4()`- ja `Uuid().v4()`-kutsujen sekä `.hex[:8]`-, `.hex[:16]`-, `.substring(0, 16)`- ja `.take(16)`-katkaisujen täydellinen hävittäminen koko Python-backendistä (`@[backend_v2/models/core_base.py]:generate_uuid7`) ja Flutter-asiakassovelluksesta (`@[client_app_v2/lib/utils/json_converters.dart]:generateOpaqueUuid7` ja 32-hex `StrictOpaqueIdConverter`), lukittuna pysyvillä staattisilla laatuporteilla `QGR030` (`@[scripts/_ast_guardrails.py]`) ja `DGR008` (`@[scripts/_dart_guardrails.py]`).

---

### 2.2 Toteutettu arkkitehtuuri: Malli A (Universal 32-Hex `PrefixedUUID7`)

ID-käsittely toimii koko järjestelmässä yhtenä poikkeuksettomana putkena (`single_pipeline_invariant_mandate`):

```
+-----------------------------------------------------------------------------------+
| 1. SOVELLUS-, DTO-, JSON-, SEED- JA FLUTTER-KERROS (Domain Prefix Safety)         |
|    - Kaikki etuliitteelliset ID:t ovat muotoa: {prefix}_{32_hex_uuidv7}           |
|    - OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"                   |
|    - Backend: generate_opaque_id(prefix) & generate_uuid7()                       |
|    - Flutter: StrictOpaqueIdConverter (32-hex) & generateOpaqueUuid7(prefix)      |
|    - Staattiset vartijat: QGR030 (Python AST) & DGR008 (Dart Guardrail)           |
+-----------------------------------------------------------------------------------+
                                          |
                 Kirjoitus: parse_prefixed_uuid7(id, EntityPrefix.<TYPE>)
                 Luku:      format_prefixed_uuid7(row["id"], EntityPrefix.<TYPE>)
                                          v
+-----------------------------------------------------------------------------------+
| 2. POSTGRESQL 19 TIETOKANTAKERROS (100 % Natiivi 16-tavuinen Binäärinen UUIDv7)   |
|    - Kaikki 12 taulua: id UUID PRIMARY KEY DEFAULT uuidv7()                       |
|    - Kaikki relaatioviiteavaimet (FOREIGN KEY): natiivi UUID-sarake               |
|    - Tietokantatason invariantti: CHECK (uuid_extract_version(id) = 7)            |
+-----------------------------------------------------------------------------------+
```

#### Malli A:n toteutetut ja lukitut invariantit:
1. **Kiinteämittainen 32 heksamerkin RFC 9562 `UUIDv7` kaikkialla:**
   * Jokainen järjestelmän entiteettitunniste koostuu kanonisesta `EntityPrefix`-etuliitteestä, alaviivasta ja tasan 32 pienestä heksamerkistä, jotka edustavat validia 128-bittistä RFC 9562 version 7 UUID-arvoa (`r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`).
   * Vakio `_UUID7_DELEGATED_PREFIXES`, `length`-parametri sekä kaikki `uuid.uuid4()`- ja `Uuid().v4()`-kutsut on poistettu kokonaan koodikannasta.
2. **Etuliitteiden yhtenäistäminen (`EntityPrefix` SSOT):**
   * Jokaisella persistoidulla ja sisäkkäisellä entiteetillä on yksikäsitteinen `@[backend_v2/models/enums.py]:EntityPrefix`-jäsen (nimenomaan ja tyhjentävästi: `org`, `usr`, `sys`, `blk`, `stp`, `sr`, `wf`, `prf`, `exe`, `rep`, `nod`, `edg`, `tda`, `sc`).
   * `@[scripts/sanitize_seed_vault.py]` generoi automaattisesti `generate_uuid7_opaque_id()`-funktiolla kanonisen 32-heksaisen `UUIDv7`-tunnisteen jokaiselle `@[backend_v2/seed/seed_data.json]`-tiedostoon lisätylle uudelle riville, asteikolle (`sc_`) tai `TDAAssertion`-väitteelle (`tda_`), jolta puuttuu validi tunniste.
3. **100 % Natiivi `UUID`-skeema kaikissa 12 PostgreSQL 19 -taulussa:**
   * Tiedostossa `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` kaikkien 12 taulun (nimenomaan ja tyhjentävästi: `organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes`, `quorum_edges`) pääavaimet ja keskinäiset relaatioviiteavaimet ovat tyyppiä `UUID` varustettuna `CHECK (uuid_extract_version(<column>) = 7)` -rajoitteella ja virtuaalisella `uuid_extract_timestamp(id)`-aikaleimalla.
4. **Symmetrinen muunnos tietokanta-adapterin rajalla:**
   * `@[backend_v2/database/postgres/entity_adapter.py]` ja `@[backend_v2/database/postgres/graph_adapter.py]` suorittavat muunnoksen `{prefix}_{32_hex}` <-> `uuid.UUID` (16 tavua) funktioilla `parse_prefixed_uuid7()` ja `format_prefixed_uuid7()`, mitä valvoo `@[scripts/audit_zero_orm_strictness.py]`.

---

### 2.3 Toteutetut Studio-ankkureiden poistot, Kausaalisen koheesiomatriisin sidonta ja `@[docs/tiede.md]`-graafimatematiikan synkronointi

Osana Askeleen 3.3 toteutusta (`@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]`) poistettiin myös kovakoodatut oletus-ID-ankkurit ja synkronoitiin `@[docs/tiede.md]`-dokumentin Luvun 4.2 mukaiset 0-tokenin topologiset graafimittarit:

1. **Studion luonnosten dynaaminen haku (`@[backend_v2/services/studio/workflow_service.py]` & `@[backend_v2/models/domain/workflow.py]`):**
   * `StudioWorkflowService.create_step_draft` hakee sekä oletusprotokollan (`PromptBlockCategory.PROTOCOL`) että ensimmäisen matriisi-/kriteerilohkon (`PromptBlockCategory.MATRIX` tai `PromptBlockCategory.CRITERIA`) dynaamisesti tietokannasta ja nostaa `AppException(ErrorCodes.STATE_INTEGRITY_ERROR)`-poikkeuksen, jos lohkoja ei löydy.
   * `StudioWorkflowService.create_workflow_draft` asettaa `default_profile_id=None` ja hakee `mcp_gateway_id`- ja `model_registry_id`-viitteet (`r"^sys_[a-fA-F0-9]{32}$"`) dynaamisesti `self.system_repo`-repositoriosta.
2. **Kausaalisen koheesion matriisin suora sidonta (`@[backend_v2/models/domain/step.py]`, `@[backend_v2/models/domain/workflow.py]`, `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` & `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`):**
   * BARS-koheesiomatriisi on sidottu suoraan `StepType.CAUSAL_DISCOVERY`-stepin `criteria_block_ids`-listaan.
   * `_append_causal_fusion_and_cohesion_events` lukee matriisi-ID:n ja sen 5 BARS-atomia (`TDAAssertion`) suoraan stepin hydratoidusta matriisista ajon aikana, ja vanhat kovakoodaukset (`causal_cohesion_matrix_block_id`, `CAUSAL_COHESION_TDA_IDS`, `CAUSAL_COHESION_CLAIMS`) on poistettu.
3. **`@[docs/tiede.md]`-graafimatematiikan 100 % synkronointi (`r_LCC`, `r_conv`, $\kappa_{\text{steer}}$ ja `simulate_counterfactual_retraction`):**
   * `AntiFluffAuditDTO` (`@[backend_v2/models/dtos/causal_discovery.py]`) ja Flutterin `AntiFluffAuditDto` (`@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`) sisältävät 0 LLM-tokenin topologiset suhdeluvut `largest_component_ratio` ($r_{\text{LCC}} \in [0.0, 1.0]$), `branch_convergence_ratio` ($r_{\text{conv}} \in [0.0, 1.0]$) ja `steering_coupling_ratio` ($\kappa_{\text{steer}} \in [0.0, 1.0]$), jotka lasketaan funktiossa `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]:compute_causal_tda_fusion_result`.
   * `CausalCohesionEvaluator.evaluate_causal_cohesion` (`@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`) valvoo `@[docs/tiede.md]`-dokumentin Kaavan (13) Guttman-kynnyksiä (`causal_cohesion_l2_min_nodes` – `causal_cohesion_l4_convergence_min` tiedostossa `@[backend_v2/settings.py]`), ja `CausalCohesionEvaluator.simulate_counterfactual_retraction` toteuttaa Algoritmin 1 mukaisen $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ kontrafaktuaalisen haavoittuvuussimulaation (`CounterfactualSimulationResultDTO` / `CounterfactualSimulationResultDto`).

---

## Luku 3: AST- ja Laatuporttilaajennukset (`QGR020`, `QGR031`–`QGR033`, `scripts/*.py`) & `auto_hardening_runner.py` SHA-256 -välimuisti
> **STATUS: SUORITETTU, KOVENNETTU & LUKITTU (Askel 3.4: `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` & `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` — commitit `034c56fd6`, `df0518f8c`, `267312915`)**
> *Selite: `@[scripts/_ast_guardrails.py]` valvoo sääntöjä `QGR000`–`QGR033`, `@[scripts/_dart_guardrails.py]` sääntöjä `DGR001`–`DGR008` ja `@[scripts/auto_hardening_runner.py]` käyttää sisältöosoitteista SHA-256-välimuistia (`data/hardening_cache.json`).*

1. **`QGR031` (Kyselysuodattimien staattinen validointi):** Estää virheelliset operaattorit (`"eq"`, `"LIKE"`, `"="`), tyhjät kentät sekä `"in"`-operaattorin vahingolliset merkkijonoliteraalit staattisesti AST-tasolla.
2. **`scripts/`-hakemiston dynaaminen automaattiskannaus:** Korvaa kovakoodatut skriptilistat dynaamisella `scripts/*.py` -globilla (`Path("scripts").glob("*.py")`), estäen varjoskriptien ja vanhentuneiden aputyökalujen syntymisen laatuporttien ulkopuolelle.
3. **Polyfactory-mallitehtaiden invarianttivartija (`QGR032` & metatestit):** Varmistaa, että testitehtaat käyttävät 32-heksaisia RFC 9562 `UUIDv7` Opaque ID -generaattoreita (`generate_opaque_id`) ja että jokainen tehdas palauttaa aina oletusarvoilla `.build()` validoituvan Pydantic V2 -mallin (`@[backend_v2/tests/factories/test_model_factories.py]`).
4. **PEP 593 `Annotated[..., Field(...)]` (`QGR020` Check 20B) sekä PEP 257 / `Raises: None` / RFC 7807 `logger.error` (`QGR033`) staattiset AST-säännöt:** Siirtää yleisimmät LLM-hardening-säännöt suoraan `@[scripts/_ast_guardrails.py]`-tarkistukseen, jolloin virheet jäävät kiinni välittömästi `/tier2-execute`-vaiheessa yhdellä kertaa.
5. **Sisältöosoitteinen SHA-256-karkaisuvälimuisti (`@[scripts/auto_hardening_runner.py]`):** Laskee kohdetiedoston, sen yksikkötestien ja `.agents/rules/*.md`-tiedostojen yhdistetyn SHA-256-tiivisteen ja esitäyttää välimuistin valmistuneista Karkaisuaaltojen 1–4 ja UUIDv7-trackereista (`179` kohdetta), kuitaten muuttumattomat tiedostot `- [x]`-tilaan 0 sekunnissa (`⚡ CACHE HIT`) ilman LLM-aliagenttia.

---

## Luku 4: FastAPI Reitittimien SSOT-konsolidointi (`reports.py`, `workflows.py`, `system_configs.py`) & Universaalin `CRUD + Clone` -elinkaaren Lukitus (Askel 3.4b)
> **STATUS: SUORITETTU, KOVENNETTU & LUKITTU (Askel 3.4b: `@[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]` & `@[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]` [`16/16` Backend + `6/6` Frontend = `22/22` karkaistu] — commitit `b62b65d47`, `ee38118ed`)**
> *Selite: Varmisti 100 % **1 Entiteetti = 1 Reititin SSOT** -kurinalaisuuden kaikissa ei-IAM-reitittimissä sekä lukitsi universaalin `CRUD + Draft + Clone` (`POST /{id}/clone`) -elinkaaren ja 3-tason poistosuojan (`3-Layer Delete Protection`).*

1. **Kuolleen tyhjän reitittimen poisto (`system_configs.py`) & `/system/hooks`-prefiksikorjaus (`system/health.py`):** Poistettiin tyhjä varjoreititin `backend_v2/api/routers/studio/system_configs.py` ja sen vanhentunut testi `backend_v2/tests/unit/api/routers/studio/test_system_configs.py`, siivottiin `@[backend_v2/api/routers/studio/__init__.py]` sekä poistettiin päällekkäinen `prefix="/system"` tiedostosta `@[backend_v2/api/routers/system/health.py]` (`/api/v2/system/system/hooks` -> `/api/v2/system/hooks`).
2. **`Workflow`-reitittimen SSOT-konsolidointi (`studio/workflows.py`), 3-tason poistosuoja & kaikkien 5 vanhan Studio-reitittimen yhdenmukaistaminen `output_profiles.py`-standardiin:** Siirrettiin `GET /{id}/ui_schema` (`response_model=WorkflowSchemaResponseDTO`) poistetusta tiedostosta `backend_v2/api/routers/execution/workflows.py` osaksi ainoaa virallista `Workflow`-reititintä `@[backend_v2/api/routers/studio/workflows.py]` (`/api/v2/studio/workflows/{id}/ui_schema`), päivitettiin Flutterin `@[client_app_v2/lib/core/api/workflow_client.dart]` ja `@[client_app_v2/lib/core/api/studio_client.dart]`, lukittiin 3-tason poistosuoja (`@[backend_v2/database/repositories/components/prompt_block.py]`, `@[backend_v2/services/studio/prompt_block_service.py]`, `@[backend_v2/services/studio/workflow_service.py]`, `@[backend_v2/services/studio/output_profile_service.py]`, `@[backend_v2/services/studio/system_config_service.py]`) ja päivitettiin kaikki 5 vanhempaa Studio-reititintä (`@[backend_v2/api/routers/studio/workflows.py]`, `@[backend_v2/api/routers/studio/steps.py]`, `@[backend_v2/api/routers/studio/prompt_blocks.py]`, `@[backend_v2/api/routers/studio/model_registry.py]`, `@[backend_v2/api/routers/studio/mcp_gateways.py]`) tarkistamaan polkuparametreista `Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)]` sekä `PUT /{id}`-kutsuista Fail-Fast `ErrorCodes.ID_MISMATCH` täsmälleen `@[backend_v2/api/routers/output_profiles.py]`-mallin mukaisesti.
3. **`ReportArtifact`-reitittimen täysi 1-Router SSOT-konsolidointi (`execution/reports.py` & `main.py`):** Yhdistettiin `external_router` (`GET /external/reports/{report_id}`) suoraan `@[backend_v2/api/routers/execution/reports.py]`:n ainoaan `router`-instanssiin, poistettiin `execution_reports_subrouter`, `external_router`, kaksoiskoristellut `include_in_schema=False` `/execution/...`-varjopolut, tuplakiinnitys `@[backend_v2/api/routers/execution/__init__.py]`-tiedostosta sekä vanhentuneet `external_reports_router`-kiinnitykset (`/api/v1` ja `/api/v2`) `@[backend_v2/main.py]`-tiedostosta; korjattiin samalla `@[client_app_v2/lib/core/api/reports_client.dart]`-tiedoston `DGR008` `.substring()`-tekninen velka ja `@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]`-tiedoston `DGR009`-virheraja.
4. **Universaali `CRUD + Clone` (`POST /{id}/clone`) & `OPAQUE_STRIPE_ID_REGEX` OpenAPI-laatuportti (`@[backend_v2/tests/unit/api/test_router_ssot_guardrails.py]`):** Lukittiin automaattinen testi, joka tarkistaa `app.routes`- ja `app.openapi()["paths"]`-rakenteista, ettei yksikään reitti ala `/api/v1`-, `/api/v2/system/system`- tai `/api/v2/execution/reports`-etuliitteellä ja että kaikki 6 konfiguroitavaa Studio/Ontologia-entiteettiä (`workflows`, `steps`, `prompt-blocks`, `output-profiles`, `model-registry`, `mcp-gateways`) toteuttavat täyden `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}` ja `POST /{id}/clone` -pinnan `OPAQUE_STRIPE_ID_REGEX`-polkuvalidoinnilla.

---

## Luku 5: Topologisen Älykkyyden Säilyttäminen Tislauksessa, Synteesissä & SDUI-raportoinnissa (Askel 3.4c — EPIC 161)
> **STATUS: VAIHEET 1–4, LIVE E2E & BACKEND HARDENING 31/31 SUORITETTU (`@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]`, `@[docs/epic/EPIC_161_audit_report.md]`, `@[docs/epic/EPIC_161_tracker.md]` & `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_161/04_phase4_plan.md]` — commitit `32e3ccf3d`, `566aa2773`, `bc78c2c80`, `78273ed8c`, `6409a3953`, `204c4e529`, `8f838d834`; 5 Flutter SDUI -kohdetta karkaistaan Karkaisuaalloissa F1–F3)**
> *Selite: Ratkaisee ongelman, jossa Vaiheen 1 rikastetun DAG-suorituksen topologiset estoketjut (`short_circuit_reason_tda_ids`), kausaaliset riippuvuudet (`depends_on_tda_ids`), käänteiset myrkkyosumat (`is_inverse_evidence`), PostgreSQL 19 3-suuntaiset Toulmin-falsifikaatiot (`find_falsified_claims`) ja kontrastiiviset kehitysraja-ankkurit (`ContrastivePairDTO`) litistyvät ennen synteesiä ja SDUI-raporttia — ylittämättä `300 000` merkin (`~75 000` tokenin) kontekstikattoa.*

### 5.1 Tunnistetut 6 rakenteellista litistymiskohtaa (Breakpoints 1–6)

Syväauditoinnissa (`@[docs/epic/EPIC_161_audit_report.md]`) todennettiin kuusi tarkkaa kohtaa, joissa Vaiheen 1 rikas topologinen ja kausaalinen älykkyys katoaa matkalla Vaiheen 2 synteesiin ja lopulliseen SDUI/PDF-raporttiin:

1. **Katkos 1 — Episteemisten todisteiden leikkautuminen, tyhjän sitaatin pudotus & skeema-amputaatio luokassa `DistilledEvaluation` (`@[backend_v2/models/domain/synthesis.py]`, `@[backend_v2/models/dtos/atom_evaluation.py]`, `@[backend_v2/settings.py]` & `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`):**
   * `SynthesisPayloadCompressor._clean_and_distill_payload` (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`, rivit `268–270` ja `340–342`) leikkaa `semantic_reasoning`-perustelun ensimmäiseen `300` merkkiin (`settings.max_synthesis_reasoning_length`), mikä katkaisee `ReasoningStepDTO`:n (`@[backend_v2/models/dtos/atom_evaluation.py]`) tärkeimmät kentät `step_3_evaluate_anti_patterns` ja `step_4_final_conclusion`.
   * Samassa metodissa rivit `265–266` ja `336–338` pudottavat arvioinnit, kun `valid_quotes` on tyhjä ja `semantic_reasoning` puuttuu, mikä hävittää oikosuljetut `ExecutionStatus.N_A`-atomit (`evaluation_reasoning = None`), ja `DistilledEvaluation` (`@[backend_v2/models/domain/synthesis.py]`) pudottaa kentät `depends_on_tda_ids`, `short_circuit_reason_tda_ids` ja `is_inverse_evidence`.
2. **Katkos 2 — Matemaattisesti degeneroitunut defisiittien järjestäminen (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`):**
   * Metodi `_prune_and_stratify_evaluations` (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`) järjestää sekä vahvuudet että puutteet (`deficits`) avaimella `sort_key` (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`: `(-len(e.exact_quotes), e.atom_id)`). Koska `@[backend_v2/models/dtos/atom_result.py]` pakottaa `source_quotes = None` kaikille `FAILED`- ja `N_A`-atomeille, `-len(e.exact_quotes)` on aina `0` ja puutteet leikkautuvat mielivaltaisessa `atom_id`-aakkosjärjestyksessä topologisen vaikuttavuuden sijaan.
3. **Katkos 3 — Affirmatiivinen vinouma, linkittämättömät `N_A`-oikosulut & kontrastiivinen sokeus luokassa `MatrixExplanationService` (`@[backend_v2/services/orchestrator/matrix_explanation_service.py]`):**
   * Kun `hit_status == ExecutionStatus.FAILED` (rivit `243–252`), `assemble_matrices_to_explain` lisää listaan pelkän väitteen otsikon ja hylkää `evaluation_reasoning`-perustelun, `ContrastivePairDTO(acceptable, rejected)`-esimerkit (`@[backend_v2/models/domain/matrix.py]`), `anti_patterns`-listan (`@[backend_v2/models/domain/matrix.py]`) sekä `is_inverse_evidence`-tiedon.
   * Lisäksi `ExecutionStatus.N_A`-atomit ohitetaan kokonaan, eikä niitä sidota `short_circuit_reason_tda_ids`-ketjun (`@[backend_v2/services/orchestrator/topological_evaluator.py]`, rivit `156–162`) kautta estäneen yläsolmun väitteeseen ja yläsolmun `evaluation_reasoning`-perusteluun.
4. **Katkos 4 — Vaiheen 1 `SynthesisEngine` ohittaa pelkistetyt `ReducedAtomDTO`-arvot (`@[backend_v2/services/orchestrator/engines/synthesis_engine.py]` & `@[backend_v2/models/dtos/atom_evaluation.py]`):**
   * `SynthesisEngine.execute()` kutsuu `MatrixReducer.reduce_matrix()`-metodia (`@[backend_v2/services/orchestrator/matrix_reducer.py]`), mutta ei koskaan injektoi `matrix_reducer_output.reduced_atoms`-tuloksia (`ReducedAtomDTO`) `user_message_parts`-promptiin (rivit `170–188`).
5. **Katkos 5 — Kausaaligraafin ja Toulmin-falsifikaatioiden eristyneisyys (`@[backend_v2/workers/synthesis_worker.py]` & `@[backend_v2/database/postgres/graph_adapter.py]`):**
   * `SynthesisWorker` (rivit `394–433` tiedostossa `@[backend_v2/workers/synthesis_worker.py]`) muotoilee `CausalTdaFusionResultDTO`:sta (`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]`) pelkkiä raakoja solmu-ID:itä ilman ihmisluettavia `PropositionNode.claim`-väitteitä ja välittää ne vain `create_executive_summary_task`-tehtävälle, jättäen `create_matrix_sections_tasks`-, `create_xai_highlights_task`- ja `create_row_explanations_task`-tehtävät (`@[backend_v2/workers/synthesis_tasks.py]`, `@[backend_v2/workers/synthesis_tasks.py]`, `@[backend_v2/workers/synthesis_tasks.py]`) kokonaan ilman kausaali- ja Toulmin-falsifikaatiokontekstia (`FalsifiedClaimMatch` luokasta `@[backend_v2/models/domain/proposition_graph.py]`).
6. **Katkos 6 — Siiloutuneet SDUI-adapterit & irtonaiset `SduiNACard`-kortit (`@[backend_v2/services/blueprint.py]` & `@[backend_v2/services/sdui/sdui_mapper_service.py]`):**
   * `SduiMapperService.map_report_to_sdui` (rivit `146–160` tiedostossa `@[backend_v2/services/sdui/sdui_mapper_service.py]`) sijoittaa `SduiNACard`-kortit raportin loppuun irralleen matriisitaulusta (`SduiMatrixSummaryTableBlock`) ja kausaaligraafista (`SduiCausalGraphBlock`), ja `@[backend_v2/services/blueprint.py]` sisältää riveillä `584–592` raa'an `if type(content) is dict:` -tarkistuksen.

---

### 5.2 Viiden pilarin epäsymmetrinen tislausarkkitehtuuri & Token-budjetin matemaattinen todistus

Ratkaisu estää kontekstin paisumisen (`Context Bloat`) soveltamalla **epäsymmetristä episteemistä tislausta**, jossa saavutetut `PASSED`-tasot tiivistetään ja vain kehitysrajan ($S + 1$) puutteet rikastetaan:

```
+---------------------------------------------------------------------------------------------------+
| VAIHE 1: RIKASTETTU DAG-SUORITUS (MATRIX_EVALUATION + CAUSAL_DISCOVERY + BARS_SYNTHESIS)          |
|  - TopologicalEvaluator -> ReducedAtomDTO (status, is_inverse_evidence, short_circuit_ids)        |
|  - compute_causal_tda_fusion_result + CteReasoningStrategy.find_falsified_claims()                |
+---------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
| EPÄSYMMETRINEN TISLAUS & KEHITYSRAJAN (S + 1) RIKASTUS (<= 60 000 merkkiä / 20.0 % budjetista)    |
|  1. PASSED-atomit: Tiivistetään korkeimpaan saavutettuun tasoon S (max 300 merkin sitaatit).      |
|  2. FAILED & N_A -atomit: 100 % säilytys + topologinen järjestys (-inverse, -out_degree, ...).    |
|  3. Transitiivinen N_A-periytyminen: Yläsolmun väite + evaluation_reasoning sidotaan lapsiin.     |
|  4. Frontier (S + 1) MatrixFailureDeficitDTO: ContrastivePairDTO + anti_patterns (max 3/r). |
|  5. CausalSynthesisBriefDTO: Kausaalipolut + FalsifiedClaimMatch kaikille 4 synteesille.    |
+---------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
| VAIHE 2: SYNTEESI & FULL-DUPLEX SDUI / JINJA2 PDF / FLUTTER FREEZED -PARITEETTI                   |
|  - SduiMatrixSummaryTableBlock & SduiCausalGraphBlock: short_circuited_by_claims & falsified      |
+---------------------------------------------------------------------------------------------------+
```

#### Token-budjetin matemaattinen yläraja (20 matriisiriviä):
* `max_synthesis_prompt_chars = 300 000` merkkiä (`~75 000` tokenia tiedostossa `@[backend_v2/services/orchestrator/synthesis_distiller.py]`).
* **Matriisirivikohtainen kehitysrajakuorma ($S + 1$):** enintään `MAX_CONTRASTIVE_DEFICITS_PER_ROW = 3` epäonnistunutta kehitysraja-atomia $\times$ (`600` merkkiä 4-vaiheinen Micro-CoT `evaluation_reasoning` + `260` merkkiä `ContrastivePairDTO` ja `anti_patterns` + `140` merkkiä transitiivinen riippuvuusketju) $\approx 3\,000$ merkkiä ($\approx 750$ tokenia) per rivi.
* **Kokonaiskuorma 20 matriisirivillä:** $20 \times 3\,000 = 60\,000$ merkkiä ($\approx 15\,000$ tokenia), eli tasan **`20,0 %`** `300 000` merkin synteesibudjetista samalla kun 100 % episteemisestä virhesignaalista säilyy.

---

### 5.3 Vaiheistus (`Phase 1` – `Phase 4`), Kohdetiedostot (`24` Backend + `4` Flutter) ja Suorituskomento

Eepos `@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]` on jaettu neljään peräkkäiseen toteutussuunnitelmaan hakemistossa `@[docs/epic/tasks_EPIC_161/]` ja kytketty seurantatiedostoon `@[docs/epic/EPIC_161_tracker.md]`:

1. **Vaihe 1 — `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]` (*Pre-Implementation Technical Debt Cleanups & Typed Topological Envelope Foundation*, `9` tiedostoa):**
   * Poistaa `if type(content) is dict:` -tarkistuksen tiedostosta `@[backend_v2/services/blueprint.py]`, kytkee PostgreSQL 19 3-suuntaisen Toulmin-kyselyn `@[backend_v2/database/postgres/graph_adapter.py]` (`CteReasoningStrategy.find_falsified_claims` -> `FalsifiedClaimMatch` luokasta `@[backend_v2/models/domain/proposition_graph.py]`) osaksi `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]`- ja `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]`-putkea, nostaa `max_synthesis_reasoning_length = 1500` tiedostossa `@[backend_v2/settings.py]` sekä rikastaa `DistilledEvaluation`-, `ReducedAtomDTO`- ja `CausalRootCauseDiagnosisDTO`-mallit ja topologisen defisiittijärjestyksen tiedostossa `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`.
2. **Vaihe 2 — `@[docs/epic/tasks_EPIC_161/02_phase2_plan.md]` (*Orchestration, Frontier Contrastive Deficit Injection & Synthesis Convergence*, `11` tiedostoa):**
   * Luo `MatrixFailureDeficitDTO`- ja `CausalSynthesisBriefDTO`-skeemat tiedostoon `@[backend_v2/models/dtos/synthesis.py]`, toteuttaa kehitysrajan ($S + 1$) kontrastiivisen rikastuksen ja transitiivisen `N_A`-oikosulkujen periytymisen luokassa `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`, injektoi `matrix_reducer_output.reduced_atoms` Vaiheen 1 `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`-moottoriin sekä hajauttaa `CausalSynthesisBriefDTO`-tiivistelmän kaikille 4 synteesitehtävälle tiedostoissa `@[backend_v2/workers/synthesis_worker.py]`, `@[backend_v2/workers/synthesis_tasks.py]` ja `@[backend_v2/models/prompts/synthesis/synthesis_directives.py]`.
3. **Vaihe 3 — `@[docs/epic/tasks_EPIC_161/03_phase3_plan.md]` (*Frontend Flutter UI, Jinja PDF & Freezed SDUI DTO Synchronization*, `7` tiedostoa):**
   * Synkronoi `short_circuited_by_claims`- ja `falsified_warrant_claims`-ketjut tiedostoihin `@[backend_v2/models/dtos/report_data.py]`, `@[backend_v2/models/view/sdui.py]`, `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`, `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`, `@[backend_v2/services/sdui/sdui_mapper_service.py]` ja `@[backend_v2/services/pdf_generator.py]` sekä Flutter Freezed -malleihin ja näkymiin (`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]`, `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`).
4. **Vaihe 4 — `@[docs/epic/tasks_EPIC_161/04_phase4_plan.md]` (*Verification & E2E Integration Gate*, `12` testitiedostoa):**
   * Lukitsee kaikki 4 ISTQB-ekvivalenssipartitiota ja 2 negatiivista raja-arvotestiä jokaista positiivista testiä kohden sekä varmistaa 100 % Cross-Domain SDUI -pariteetin (`@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`).

#### Suoritus- ja karkaisukomennot (Seuraavana vuorossa):
```powershell
# 1. Vaiheen 1 syväanalyysi (valinnainen ennen ajoa):
/tier0-research-plan @[docs/epic/tasks_EPIC_161/01_phase1_plan.md] @[docs/epic/EPIC_161_tracker.md]

# 2. Kaikkien 4 vaiheen automaattinen suoritus:
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_161_tracker.md --model gemini-4-argon-high

# 3. 28 kohdetiedoston automaattinen Tier 2 Hardening:
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_161_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"
```

---

## Luku 6: Studio-käyttöliittymän ja `OutputProfile`-profiilin vanhentuneiden matriisiviittausten (`target_blocks`) synkronointi steppiä poistettaessa
> **STATUS: AVOIN PARANNUSKOHDE (Studio UI & Backend `OutputProfile` / `Workflow` -synkronointi)**
> *Selite: Estää näkymättömän "haamuvalinnan" (`ghost ID`) jäämisen `OutputProfile`-profiilin `matrix_synthesis_groups[*].target_blocks`-, `variance_target_block`- ja `user_role_target_block`-kenttiin silloin, kun työnkulusta (`Workflow`) irrotetaan steppi ja siihen kytketty matriisi.*

### 6.1 Tunnistettu ongelma ja nykytilan käyttäytyminen

1. **Työnkulun sisäinen steppisiivous toimii oikein (`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]`):**
   * Kun käyttäjä poistaa stepin työnkulusta metodissa `WorkflowStepsTab._deleteStep`, käyttöliittymä siivoaa automaattisesti muiden steppien `dependsOn`-riippuvuudet, `$steps.<deletedId>`-syötekartoitukset (`inputMappings`) sekä `causalSourceStepId`-viittaukset.
2. **Työnkulun tallennus ei synkronoi kytkettyä `OutputProfile`-profiilia (`@[backend_v2/services/studio/workflow_service.py]`):**
   * Kun päivitetty työnkulku tallennetaan metodilla `StudioWorkflowService.save_workflow`, tietokantaan jäävät ennalleen työnkulkuun liitetyn `OutputProfile`-profiilin vanhat matriisiviittaukset (nimenomaan ja tyhjentävästi: `matrix_synthesis_groups[*].target_blocks`, `variance_target_block` ja `user_role_target_block`), vaikka kyseinen matriisi (`blk_...`) ei enää kuulu mihinkään työnkulun steppiin.
3. **Näkymätön haamuvalinta käyttöliittymässä ja `400 VALIDATION_FAILED` tallennettaessa (`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]` & `@[backend_v2/services/studio/output_profile_service.py]`):**
   * `ProfileSectionConfigTab` muodostaa `allowedBlockIds`-joukon työnkulun nykyisten steppien `criteriaBlockIds`-listoista, ja `MatrixGraphItemEditor` suodattaa näkyvät `FilterChip`-valintanapit ehdolla `allowedBlockIds.contains(b.id)`.
   * Koska poistetun stepin matriisi-ID (`blk_...`) ei ole enää `allowedBlockIds`-joukossa, sen `FilterChip`-siru piilotetaan käyttöliittymästä, mutta vanha ID jää silti `group.targetBlocks`-listan sisään.
   * Kun käyttäjä yrittää myöhemmin muokata ja tallentaa `OutputProfile`-profiilia, `StudioOutputProfileService.save_output_profile` hylkää tallennuksen virheellä `400 VALIDATION_FAILED: Target Component 'blk_...' does not exist in the context of Workflow 'wor_...'`, eikä käyttäjä pysty ruksimaan piilotettua valintaa suoraan pois poistamatta koko kuvaajaryhmää tai vaihtamatta `PresetView`-tyyppiä.

### 6.2 Toteutettava ratkaisu

Parannus on yksinkertainen toteuttaa joko automaattisena siivouksena tai visuaalisena virhesiruna (tai molempien yhdistelmänä):
1. **Vaihtoehto A — Automaattinen synkronointi tallennuksessa ja UI:ssa (`@[backend_v2/services/studio/workflow_service.py]` & `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]`):**
   * `StudioWorkflowService.save_workflow` (ja/tai UI:n tallennuspolku) siivoaa `allowed_blocks`- / `allowedBlockIds`-joukon ulkopuoliset vanhentuneet matriisi-ID:t automaattisesti pois työnkulkuun kytkettyjen `OutputProfile`-profiilien `target_blocks`-listoista sekä `variance_target_block`- ja `user_role_target_block`-kentistä.
2. **Vaihtoehto B — Näkyvä punainen poistettava `FilterChip`-siru (`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`):**
   * `MatrixGraphItemEditor` renderöi `group.targetBlocks`-listassa olevat `allowedBlockIds`-joukon ulkopuoliset vanhentuneet ID:t punaisena, varoitusmerkillä varustettuna `FilterChip`-siruna, josta käyttäjä näkee välittömästi vanhentuneen viittauksen ja voi poistaa sen yhdellä klikkauksella.

---

## Luku 7: `CognitiveTier`-enumin 100 % Pakottaminen, Merkkijonopohjaisten `LLMClient.from_strategy`-siltojen Poisto & KI-/Sääntöohjeistuksen Synkronointi
> **STATUS: AVOIN PARANNUSKOHDE (`No-String Mandate` & `zero_backward_compatibility_planning_ban` -yhdenmukaistaminen; KI- ja sääntötiedostot synkronoitu)**
> *Selite: Muuttaa kaikki jäljellä olevat merkkijonopohjaiset `LLMClient.from_strategy("fast", ...)` -kutsut ja `PipelineConfig.default_strategy: str | None` -määritykset käyttämään suoraan vahvasti tyypitettyä `CognitiveTier`-enumia (`CognitiveTier.FAST`, `CognitiveTier.BALANCED`, `CognitiveTier.DEEP`, `CognitiveTier.REASONING`) sekä metodia `LLMClient.from_tier(...)`, ja poistaa vanhentuneen `LLMClient.from_strategy`-yhteensopivuussillan.*

### 7.1 Tunnistetut kohteet, joissa käytetään raakaa `"fast"`-merkkijonoa tai `str`-tyyppiä `CognitiveTier`-enumin sijaan

Vaikka Vaiheen 1 DAG-vaiheet (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, rivit `452–469`), RAG Preflight (`@[backend_v2/services/orchestrator/rag_preflight_service.py]`, rivit `211–217`), MCP-työkalusilmukka (`@[backend_v2/services/mcp/mcp_tool_loop.py]`, rivit `163–188`) ja Vaiheen 2 synteesityöntekijät (`@[backend_v2/workers/synthesis_worker.py]`, rivit `328–333` ja `@[backend_v2/workers/variance_synthesis.py]`, rivit `395–400`) käyttävät jo `LLMClient.from_tier(CognitiveTier.<TIER>, ...)`-kutsua, koodikannassa on yhä seuraavat merkkijonopohjaiset kutsut ja tyypitykset:

1. **`ChatParserService.parse_pasted_chat` (`@[backend_v2/services/chat_parser.py]`, rivit `178–190`):**
   * Kutsuu `await LLMClient.from_strategy("fast", repository=system_repo, pipeline_name="chat_parser", ...)` raa'alla `"fast"`-merkkijonolla `await LLMClient.from_tier(CognitiveTier.FAST, repository=system_repo, pipeline_name="chat_parser", ...)` sijaan.
2. **`analyze_interaction_role` (`@[backend_v2/hooks/interaction_hook.py]`, rivit `109–121`):**
   * Kutsuu `await LLMClient.from_strategy("fast", repository=system_repo, pipeline_name="interaction_hook", ...)` raa'alla `"fast"`-merkkijonolla `await LLMClient.from_tier(CognitiveTier.FAST, repository=system_repo, pipeline_name="interaction_hook", ...)` sijaan.
3. **`PipelineConfig` & `PIPELINE_REGISTRY` (`@[backend_v2/models/enums.py]`, rivit `1052–1074`):**
   * `PipelineConfig.default_strategy` on tyypitetty `str | None = None` (eikä `CognitiveTier | None = None`), ja `PIPELINE_REGISTRY`-sanakirjassa riveillä `1067`, `1070` ja `1071` (`"chat_parser"`, `"studio_generation"`, `"interaction_hook"`) on kovakoodattu merkkijono `default_strategy="fast"` `default_strategy=CognitiveTier.FAST` sijaan.
4. **Muut samassa yhteydessä siivottavat `LLMClient.from_strategy`-jäänteet (`No Hidden Scope`):**
   * `@[backend_v2/hooks/linguistics.py]` (rivit `157–169`): kutsuu `await LLMClient.from_strategy("fast", repository=deps.system_repo, pipeline_name="linguistics_hook", ...)` -> vaihdetaan muotoon `await LLMClient.from_tier(CognitiveTier.FAST, ...)`.
   * `@[backend_v2/hooks/source_verification_hook.py]` (rivit `230–242`): kutsuu `await LLMClient.from_strategy("fast", repository=deps.system_repo, pipeline_name="source_verification", ...)` -> vaihdetaan muotoon `await LLMClient.from_tier(CognitiveTier.FAST, ...)`.
   * `@[scripts/ablation_live_executor.py]` (rivit `680–681`): kutsuu `await LLMClient.from_strategy(strat_1, repository=repo)` -> vaihdetaan muotoon `await LLMClient.from_tier(CognitiveTier(strat_1), repository=repo)`.
   * `@[backend_v2/llm/client.py]`: kun kaikki kutsujat on siirretty `LLMClient.from_tier`-metodiin, vanha merkkijonopohjainen yhteensopivuussilta `LLMClient.from_strategy` poistetaan kokonaan (`the_no_legacy_mandate` & `zero_backward_compatibility_planning_ban`) ja vastaavat yksikkötestit (`@[backend_v2/tests/unit/services/test_chat_parser.py]`, `@[backend_v2/tests/unit/hooks/test_interaction_hook.py]`, `@[backend_v2/tests/unit/hooks/test_linguistics.py]`, `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/models/test_enums.py]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`) päivitetään kohdistumaan suoraan `LLMClient.from_tier`-metodiin ja `CognitiveTier`-enumiin.

### 7.2 Toteutettava ratkaisu ja KI-/Sääntöohjeistuksen lukitus

1. **Koodikannan migraatio (`CognitiveTier` SSOT):**
   * Vaihdetaan `PipelineConfig.default_strategy: CognitiveTier | None = None` tiedostossa `@[backend_v2/models/enums.py]` (rivit `1052–1074`) ja asetetaan `default_strategy=CognitiveTier.FAST`.
   * Korvataan kaikki `LLMClient.from_strategy("fast", ...)` -kutsut tiedostoissa `@[backend_v2/services/chat_parser.py]`, `@[backend_v2/hooks/interaction_hook.py]`, `@[backend_v2/hooks/linguistics.py]` ja `@[backend_v2/hooks/source_verification_hook.py]` kutsulla `LLMClient.from_tier(CognitiveTier.FAST, ...)`.
   * Poistetaan `LLMClient.from_strategy`-silta tiedostosta `@[backend_v2/llm/client.py]` ja lisätään staattinen AST-vartija (`@[scripts/_ast_guardrails.py]`), joka estää `LLMClient.from_strategy`-kutsut sekä raa'at merkkijonoliteraalit `LLMClient.from_tier`-kutsuissa.
2. **KI- ja Sääntöohjeistuksen synkronointi (SUORITETTU):**
   * Päivitetty `@[.agents/rules/05_llm_architecture.md]` (`direct_sdk_calls` & `internal_utility_llm_execution`), `@[.agents/rules/01-python-backend.md]` (`llm_structured_execution_mandate`), `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` sekä Knowledge Itemit `@[knowledge/unified_model_multiplexing/artifacts/ki_unified_model_multiplexing.md]`, `@[knowledge/cartesian_variance_and_authenticity/artifacts/ki_cartesian_variance_and_authenticity.md]` ja `@[knowledge/execution_engine_protocol/artifacts/ki_execution_engine_protocol.md]` ohjaamaan poikkeuksetta muotoon `await LLMClient.from_tier(CognitiveTier.<TIER>, repository=repo)` ja kieltämään merkkijonopohjaisen `from_strategy`-kutsun.

---

## Luku 8: DAG-suorituksen Resilienssi, Prosessienvälinen Optimistinen Lukitus (OCC) ja Solmutason Merkle-syötetiiviste (`input_merkle_hash`)
> **STATUS: AVOIN PARANNUSKOHDE (`/tier8-audit-feature` -arvioinnin perusteella valitut 3 korkean hyöty–panos-suhteen karkaisukohdetta)**
> *Selite: Täydentää Quorumin nykyistä DAG-orkestrointia kolmella kohdennetulla parannuksella: (1) Vaiheen 3 (`execute_engine_retry_stage`) semanttinen oskillaatiotunnistin ja ajokohtainen `ExecutionBudget`-kustannuskatto, (2) prosessienvälinen optimistinen lukitus (`state_version` OCC) `executions`-taulun päivityksissä ja (3) solmutason `input_merkle_hash`-tiiviste `ExecutionStep`-malliin yhdessä MCP-hakutulosten XML-ohjaustagien suodatuksen kanssa.*

### 8.1 Vaiheen 3 (`execute_engine_retry_stage`) semanttinen oskillaatiotunnistin ja ajokohtainen `ExecutionBudget`-katto

1. **Nykytilan aukko (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, rivit `493–574` & `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, rivit `320–343`):**
   * Matalan tason `LLMTaskExecutor.execute_structured_task` (`@[backend_v2/services/llm_task_executor.py]`, rivit `429–490`) sisältää jo jumiutuneen silmukan tunnistimen (`Stuck Loop Detected`), joka katkaisee suorituksen heti (`ErrorCodes.AI_EXECUTION_FAILED`), jos kaksi peräkkäistä yritystä tuottavat identtisen Pydantic-skeemavirheen tai raakavastauksen.
   * Sen sijaan korkeamman tason Vaiheen 3 `execute_engine_retry_stage` (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, rivit `552–573`) ajaa koko moottorin ja post-hookit uudelleen `llm_max_retries` kertaa, kun post-hook asettaa `llm_anomaly_retry_requested = True`, tarkistamatta tuottiko moottori täsmälleen saman kanonisen tulostiivisteen kuin edellisellä kierroksella.
   * Lisäksi `UsageService.check_quota` (`@[backend_v2/services/usage_service.py]`, rivit `47–95`) valvoo organisaatiotason kiintiötä, mutta yksittäisellä DAG-ajolla ei ole omaa ajonaikaista token- tai kustannuskattoa aaltojen välissä tiedostossa `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` (rivit `320–343`).
2. **Toteutettava ratkaisu:**
   * Lisätään `execute_engine_retry_stage`-silmukkaan (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, rivit `552–573`) edellisen kierroksen tuloksen kanoninen SHA-256-tiivistevertailu (`hashlib.sha256`): jos uudelleenyritys tuottaa identtisen tulostiivisteen ja laukaisee saman `llm_anomaly_retry_requested`-lipun, silmukka katkaistaan välittömästi ilman uutta LLM-kutsua.
   * Lisätään tiedostoon `@[backend_v2/settings.py]` (rivit `204–237`) ajokohtaiset budjettirajat (`max_tokens_per_run`, `max_cost_usd_per_run`, `max_total_steps_per_run`), joita `wave_orchestrator_stage.py` (`@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, rivit `320–343`) tarkistaa jokaisen DAG-aallon välissä suoraan `state.execution_record.metrics`-kertymästä (`TokenUsage`). Rajan ylittyessä ajo keskeytetään hallitusti `AppException(ErrorCodes.QUOTA_EXCEEDED)`-virheellä.

### 8.2 Prosessienvälinen optimistinen lukitus (`state_version` OCC) `executions`-taulussa

1. **Nykytilan aukko (`@[backend_v2/database/postgres/entity_adapter.py]`, rivit `1150–1218` & `@[backend_v2/services/execution/override_service.py]`, rivit `307–382`):**
   * Yksittäisen Arq-työläisen sisällä rinnakkaiset solmut ovat suojattuja muistitason lukolla (`async with state.update_lock:` tiedostossa `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, rivit `149–197`).
   * Kahden eri prosessin välillä voi kuitenkin syntyä päivitystörmäys (`Lost Update`), kun käyttäjä tallentaa manuaalisen tuomion ylikirjoituksen (`ExecutionOverrideService.override_atom` tiedostossa `@[backend_v2/services/execution/override_service.py]`, rivit `307–382`) tai synteesin esilämmitys päivittää `ExecutionRecord`-oliota samanaikaisesti, kun Arq-työläinen tallentaa tilannevedosta (`ExecutionCommitter.commit_trace` tiedostossa `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py]`, rivit `43–108`). `PostgresEntityAdapter.update_execution` (`@[backend_v2/database/postgres/entity_adapter.py]`, rivit `1185–1218`) suorittaa tällä hetkellä ehdottoman `UPDATE executions SET ... WHERE id = $1` -lauseen, jolloin jälkimmäinen kirjoittaja ylikirjoittaa `step_states`- ja `context_variables`-JSONB-sarakkeet.
2. **Toteutettava ratkaisu:**
   * Lisätään `ExecutionRecord`-malliin (`@[backend_v2/models/domain/execution.py]`, rivit `175–280`) ja PostgreSQL:n `executions`-tauluun (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, rivit `136–157`) kokonaislukukenttä `state_version: Annotated[int, Field(ge=1)] = 1`.
   * Päivitetään `PostgresEntityAdapter.update_execution` (`@[backend_v2/database/postgres/entity_adapter.py]`, rivit `1185–1218`) käyttämään atomista ehtoa `WHERE id = $1 AND state_version = $11` ja kasvattamaan versiota (`state_version = state_version + 1`). Jos `asyncpg` ei päivitä riviä, nostetaan RFC 7807 -yhteensopiva `AppException(ErrorCodes.CONFLICT, status_code=409)`, jolloin kutsuva palvelu hakee tuoreen `ExecutionRecord`-tilan ja yhdistää muutoksensa hävittämättä rinnakkaisen prosessin päivitystä.

### 8.3 Solmutason `input_merkle_hash` `ExecutionStep`-malliin ja MCP-hakutulosten XML-tagisiivous

1. **Nykytilan aukko (`@[backend_v2/models/domain/execution.py]`, rivit `135–173`, `@[backend_v2/services/execution/resumption_service.py]`, rivit `91–127` & `@[backend_v2/services/mcp/mcp_tool_loop.py]`, rivit `412–449`):**
   * `ExecutionResumptionService.resume_execution` (`@[backend_v2/services/execution/resumption_service.py]`, rivit `91–127`) vertaa koko työnkulun versiota (`workflow.version != orig_version`) ja ohittaa ainoastaan `ExecutionStatus.PASSED`-tilassa olevat solmut (`@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, rivi `321`), mutta yksittäiselle solmulle ei tallenneta determinististä syötetiivistettä.
   * Lisäksi `mcp_tool_loop.py` (`@[backend_v2/services/mcp/mcp_tool_loop.py]`, rivit `412–449`) katkaisee ulkoisten MCP-työkalujen vastaukset merkkirajaan `max_tool_output_chars`, mutta ei poista ulkoisesta tekstistä varattuja XML-ohjaustageja ennen vastauksen liittämistä keskusteluhistoriaan.
2. **Toteutettava ratkaisu:**
   * Lisätään `ExecutionStep`-malliin (`@[backend_v2/models/domain/execution.py]`, rivit `135–173`) kenttä `input_merkle_hash: Annotated[str | None, Field(default=None)] = None`, joka lasketaan kanonisella SHA-256-tiivisteellä (`hashlib.sha256` + `json.dumps(..., sort_keys=True)`) solmun kartoitetusta syötteestä (`ContextRouter.extract_mapped_context`), solmun `PromptBlock`-sisällöistä ja `CognitiveTier`-malliparametreista.
   * Hyödynnetään `input_merkle_hash`-tiivistettä `ExecutionResumptionService.resume_execution`-metodissa (`@[backend_v2/services/execution/resumption_service.py]`, rivit `91–127`) siten, että osittaisessa uudelleenajossa alkupään solmut, joiden syötetiiviste on muuttumaton, voidaan säilyttää ilman uusia LLM-kutsuja.
   * Lisätään `mcp_tool_loop.py`-tiedostoon (`@[backend_v2/services/mcp/mcp_tool_loop.py]`, rivit `412–449`) deterministinen XML-ohjaustagien suodatus (nimenomaan ja tyhjentävästi: `</source_data>`, `<source_data>`, `</user_payload>`, `<user_payload>`, `<system_directive>` ja `</system_directive>`) ennen kuin ulkoisen MCP-työkalun palauttama teksti liitetään `ToolMessage`-viestinä LLM-keskusteluhistoriaan.

### 8.4 Arkkitehtoniset rajaukset (Mitä EI toteuteta)

1. **Ei uusia SQL-tauluja (`node_executions` / `node_events`):** Kaikki solmutason tilat ja `input_merkle_hash`-tiivisteet tallennetaan olemassa olevaan `executions.step_states`-JSONB-rakenteeseen (`universal_ssot_and_normalization_mandate`).
2. **Ei päällekkäistä `InputContract`-kerrosta:** Solmujen kontekstieristys hoidetaan jo olemassa olevilla luokilla `SourceDocumentPacker` (`ContextTargetFilterDTO` tiedostossa `@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]`, rivit `24–139`), `ContextRouter` (`@[backend_v2/services/orchestrator/context_router.py]`, rivit `50–196`) ja `ContextBuilder` (`@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`, rivit `236–471`).
3. **Ei `FallbackErrorBlock`-komponenttia tai `@FreezedUnionValue('unknown')`-haaraa:** Rikkinäisten SDUI-lohkojen muuntaminen hiljaiseksi varakomponentiksi rikkoisi Quorumin `universal_fail_fast`- ja `the_zero_compromise_pledge`-sääntöjä sekä `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`-sopimustestiä.
4. **Ei jaettua globaalia `asyncio.Semaphore`-lukkoa tietokanta- ja LLM-kutsujen välille:** Tietokanta- ja LLM-rinnakkaisuus pidetään erillisinä (`system_concurrency_ssot`), jotta sisäkkäiset `asyncio.TaskGroup`-haarat eivät lukkiudu (`deadlock`).



