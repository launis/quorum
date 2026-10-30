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
> **STATUS: SEURAAVANA JONOSSA — 1. PRIORITEETTI (`@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]`, `@[docs/epic/EPIC_161_audit_report.md]`, `@[docs/epic/EPIC_161_tracker.md]` & `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_161/04_phase4_plan.md]`)**
> *Selite: Ajetaan nyt välittömästi ennen Vaihetta 2g (`Askel 3.5`). Ratkaisee ongelman, jossa Vaiheen 1 rikastetun DAG-suorituksen topologiset estoketjut (`short_circuit_reason_tda_ids`), kausaaliset riippuvuudet (`depends_on_tda_ids`), käänteiset myrkkyosumat (`is_inverse_evidence`), PostgreSQL 19 3-suuntaiset Toulmin-falsifikaatiot (`find_falsified_claims`) ja kontrastiiviset kehitysraja-ankkurit (`ContrastivePairDTO`) litistyvät ennen synteesiä ja SDUI-raporttia — ylittämättä `300 000` merkin (`~75 000` tokenin) kontekstikattoa.*

### 5.1 Tunnistetut 6 rakenteellista litistymiskohtaa (Breakpoints 1–6)

Syväauditoinnissa (`@[docs/epic/EPIC_161_audit_report.md]`) todennettiin kuusi tarkkaa kohtaa, joissa Vaiheen 1 rikas topologinen ja kausaalinen älykkyys katoaa matkalla Vaiheen 2 synteesiin ja lopulliseen SDUI/PDF-raporttiin:

1. **Katkos 1 — Episteemisten todisteiden leikkautuminen, tyhjän sitaatin pudotus & skeema-amputaatio luokassa `DistilledEvaluation` (`@[backend_v2/models/domain/synthesis.py#L131-L155]`, `@[backend_v2/models/dtos/atom_evaluation.py#L21-L40]`, `@[backend_v2/settings.py]` & `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393]`):**
   * `SynthesisPayloadCompressor._clean_and_distill_payload` (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393]`, rivit `268–270` ja `340–342`) leikkaa `semantic_reasoning`-perustelun ensimmäiseen `300` merkkiin (`settings.max_synthesis_reasoning_length`), mikä katkaisee `ReasoningStepDTO`:n (`@[backend_v2/models/dtos/atom_evaluation.py#L21-L40]`) tärkeimmät kentät `step_3_evaluate_anti_patterns` ja `step_4_final_conclusion`.
   * Samassa metodissa rivit `265–266` ja `336–338` pudottavat arvioinnit, kun `valid_quotes` on tyhjä ja `semantic_reasoning` puuttuu, mikä hävittää oikosuljetut `ExecutionStatus.N_A`-atomit (`evaluation_reasoning = None`), ja `DistilledEvaluation` (`@[backend_v2/models/domain/synthesis.py#L131-L155]`) pudottaa kentät `depends_on_tda_ids`, `short_circuit_reason_tda_ids` ja `is_inverse_evidence`.
2. **Katkos 2 — Matemaattisesti degeneroitunut defisiittien järjestäminen (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140]`):**
   * Metodi `_prune_and_stratify_evaluations` (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179]`) järjestää sekä vahvuudet että puutteet (`deficits`) avaimella `sort_key` (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140]`: `(-len(e.exact_quotes), e.atom_id)`). Koska `@[backend_v2/models/dtos/atom_result.py#L139-L172]` pakottaa `source_quotes = None` kaikille `FAILED`- ja `N_A`-atomeille, `-len(e.exact_quotes)` on aina `0` ja puutteet leikkautuvat mielivaltaisessa `atom_id`-aakkosjärjestyksessä topologisen vaikuttavuuden sijaan.
3. **Katkos 3 — Affirmatiivinen vinouma, linkittämättömät `N_A`-oikosulut & kontrastiivinen sokeus luokassa `MatrixExplanationService` (`@[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311]`):**
   * Kun `hit_status == ExecutionStatus.FAILED` (rivit `243–252`), `assemble_matrices_to_explain` lisää listaan pelkän väitteen otsikon ja hylkää `evaluation_reasoning`-perustelun, `ContrastivePairDTO(acceptable, rejected)`-esimerkit (`@[backend_v2/models/domain/matrix.py#L94-L129]`), `anti_patterns`-listan (`@[backend_v2/models/domain/matrix.py#L66-L77]`) sekä `is_inverse_evidence`-tiedon.
   * Lisäksi `ExecutionStatus.N_A`-atomit ohitetaan kokonaan, eikä niitä sidota `short_circuit_reason_tda_ids`-ketjun (`@[backend_v2/services/orchestrator/topological_evaluator.py#L56-L175]`, rivit `156–162`) kautta estäneen yläsolmun väitteeseen ja yläsolmun `evaluation_reasoning`-perusteluun.
4. **Katkos 4 — Vaiheen 1 `SynthesisEngine` ohittaa pelkistetyt `ReducedAtomDTO`-arvot (`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301]` & `@[backend_v2/models/dtos/atom_evaluation.py#L43-L67]`):**
   * `SynthesisEngine.execute()` kutsuu `MatrixReducer.reduce_matrix()`-metodia (`@[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239]`), mutta ei koskaan injektoi `matrix_reducer_output.reduced_atoms`-tuloksia (`ReducedAtomDTO`) `user_message_parts`-promptiin (rivit `170–188`).
5. **Katkos 5 — Kausaaligraafin ja Toulmin-falsifikaatioiden eristyneisyys (`@[backend_v2/workers/synthesis_worker.py#L92-L664]` & `@[backend_v2/database/postgres/graph_adapter.py#L347-L431]`):**
   * `SynthesisWorker` (rivit `394–433` tiedostossa `@[backend_v2/workers/synthesis_worker.py#L92-L664]`) muotoilee `CausalTdaFusionResultDTO`:sta (`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465]`) pelkkiä raakoja solmu-ID:itä ilman ihmisluettavia `PropositionNode.claim`-väitteitä ja välittää ne vain `create_executive_summary_task`-tehtävälle, jättäen `create_matrix_sections_tasks`-, `create_xai_highlights_task`- ja `create_row_explanations_task`-tehtävät (`@[backend_v2/workers/synthesis_tasks.py#L140-L241]`, `@[backend_v2/workers/synthesis_tasks.py#L244-L333]`, `@[backend_v2/workers/synthesis_tasks.py#L336-L427]`) kokonaan ilman kausaali- ja Toulmin-falsifikaatiokontekstia (`FalsifiedClaimMatch` luokasta `@[backend_v2/models/domain/proposition_graph.py#L343-L391]`).
6. **Katkos 6 — Siiloutuneet SDUI-adapterit & irtonaiset `SduiNACard`-kortit (`@[backend_v2/services/blueprint.py#L127-L698]` & `@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]`):**
   * `SduiMapperService.map_report_to_sdui` (rivit `146–160` tiedostossa `@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]`) sijoittaa `SduiNACard`-kortit raportin loppuun irralleen matriisitaulusta (`SduiMatrixSummaryTableBlock`) ja kausaaligraafista (`SduiCausalGraphBlock`), ja `@[backend_v2/services/blueprint.py#L127-L698]` sisältää riveillä `584–592` raa'an `if type(content) is dict:` -tarkistuksen.

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
|  4. Frontier (S + 1) [NEW] MatrixFailureDeficitDTO: ContrastivePairDTO + anti_patterns (max 3/r). |
|  5. [NEW] CausalSynthesisBriefDTO: Kausaalipolut + FalsifiedClaimMatch kaikille 4 synteesille.    |
+---------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
| VAIHE 2: SYNTEESI & FULL-DUPLEX SDUI / JINJA2 PDF / FLUTTER FREEZED -PARITEETTI                   |
|  - SduiMatrixSummaryTableBlock & SduiCausalGraphBlock: short_circuited_by_claims & falsified      |
+---------------------------------------------------------------------------------------------------+
```

#### Token-budjetin matemaattinen yläraja (20 matriisiriviä):
* `max_synthesis_prompt_chars = 300 000` merkkiä (`~75 000` tokenia tiedostossa `@[backend_v2/services/orchestrator/synthesis_distiller.py#L43-L115]`).
* **Matriisirivikohtainen kehitysrajakuorma ($S + 1$):** enintään `MAX_CONTRASTIVE_DEFICITS_PER_ROW = 3` epäonnistunutta kehitysraja-atomia $\times$ (`600` merkkiä 4-vaiheinen Micro-CoT `evaluation_reasoning` + `260` merkkiä `ContrastivePairDTO` ja `anti_patterns` + `140` merkkiä transitiivinen riippuvuusketju) $\approx 3\,000$ merkkiä ($\approx 750$ tokenia) per rivi.
* **Kokonaiskuorma 20 matriisirivillä:** $20 \times 3\,000 = 60\,000$ merkkiä ($\approx 15\,000$ tokenia), eli tasan **`20,0 %`** `300 000` merkin synteesibudjetista samalla kun 100 % episteemisestä virhesignaalista säilyy.

---

### 5.3 Vaiheistus (`Phase 1` – `Phase 4`), Kohdetiedostot (`24` Backend + `4` Flutter) ja Suorituskomento

Eepos `@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]` on jaettu neljään peräkkäiseen toteutussuunnitelmaan hakemistossa `@[docs/epic/tasks_EPIC_161/]` ja kytketty seurantatiedostoon `@[docs/epic/EPIC_161_tracker.md]`:

1. **Vaihe 1 — `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]` (*Pre-Implementation Technical Debt Cleanups & Typed Topological Envelope Foundation*, `9` tiedostoa):**
   * Poistaa `if type(content) is dict:` -tarkistuksen tiedostosta `@[backend_v2/services/blueprint.py#L127-L698]`, kytkee PostgreSQL 19 3-suuntaisen Toulmin-kyselyn `@[backend_v2/database/postgres/graph_adapter.py#L347-L431]` (`CteReasoningStrategy.find_falsified_claims` -> `FalsifiedClaimMatch` luokasta `@[backend_v2/models/domain/proposition_graph.py#L343-L391]`) osaksi `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465]`- ja `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py#L211-L363]`-putkea, nostaa `max_synthesis_reasoning_length = 1500` tiedostossa `@[backend_v2/settings.py]` sekä rikastaa `DistilledEvaluation`-, `ReducedAtomDTO`- ja `CausalRootCauseDiagnosisDTO`-mallit ja topologisen defisiittijärjestyksen tiedostossa `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179]`.
2. **Vaihe 2 — `@[docs/epic/tasks_EPIC_161/02_phase2_plan.md]` (*Orchestration, Frontier Contrastive Deficit Injection & Synthesis Convergence*, `11` tiedostoa):**
   * Luo `[NEW]` `MatrixFailureDeficitDTO`- ja `[NEW]` `CausalSynthesisBriefDTO`-skeemat tiedostoon `@[backend_v2/models/dtos/synthesis.py]`, toteuttaa kehitysrajan ($S + 1$) kontrastiivisen rikastuksen ja transitiivisen `N_A`-oikosulkujen periytymisen luokassa `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311]`, injektoi `matrix_reducer_output.reduced_atoms` Vaiheen 1 `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301]`-moottoriin sekä hajauttaa `[NEW]` `CausalSynthesisBriefDTO`-tiivistelmän kaikille 4 synteesitehtävälle tiedostoissa `@[backend_v2/workers/synthesis_worker.py#L92-L664]`, `@[backend_v2/workers/synthesis_tasks.py#L61-L137]` ja `@[backend_v2/models/prompts/synthesis/synthesis_directives.py]`.
3. **Vaihe 3 — `@[docs/epic/tasks_EPIC_161/03_phase3_plan.md]` (*Frontend Flutter UI, Jinja PDF & Freezed SDUI DTO Synchronization*, `7` tiedostoa):**
   * Synkronoi `short_circuited_by_claims`- ja `falsified_warrant_claims`-ketjut tiedostoihin `@[backend_v2/models/dtos/report_data.py]`, `@[backend_v2/models/view/sdui.py]`, `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`, `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py#L32-L185]`, `@[backend_v2/services/sdui/sdui_mapper_service.py#L91-L167]` ja `@[backend_v2/services/pdf_generator.py]` sekä Flutter Freezed -malleihin ja näkymiin (`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]`, `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`).
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
