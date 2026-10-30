# Arkkitehtuurin ja Tietomallien Parannuskohteet

Tähän dokumenttiin on koottu järjestelmän koodikannassa, tietomalleissa ja laatuporteissa **avoinna ja toteuttamatta olevat** arkkitehtuuriset parannuskohteet sekä jo suoritettujen ja lukittujen arkkitehtuurikokonaisuuksien tilannekuva. Dokumentti noudattaa `anti_ambiguity_mandate`-sääntöä, *No Hidden Scope* -periaatetta sekä Quorumin *Zero-Tolerance* -laatuvaatimusta ilman siirtymäajan purkkaratkaisuja.

*(Huomautus: Aiemmin tässä dokumentissa olleet matriisiskaalauksen keskitys `computed_min`/`computed_max`, `theory_grounding` vs. `ai_description` -eriyttäminen, `I18nText.default_locale`-poisto, `MatrixClaim.ai_description` -> `TDAAssertion.concept_description` -keskitys, `OutputProfile.matrix_synthesis_groups` & L10n-siivous, Karkaisuaallot 1 [36/36], 2 [36/36], 3 [27/27] ja 4 [34/34] = 133/133 tiedostoa sekä Luvun 2 Malli A:n yhtenäinen 32-hex `PrefixedUUID7`-arkkitehtuuri, legacy `UUIDv4`-generaattoreiden täydellinen poisto ja `@[docs/tiede.md]`-graafimatematiikan synkronointi on toteutettu, karkaistu, auditoitu ja lukittu.)*

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
> **STATUS: TOTEUTETTU & AUDITOITU — TIER 2 HARDENING (`auto_hardening_runner.py`) ODOTTAA AJOA (`@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` [0/15 karkaistu] & `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` [0/31 karkaistu])**
> *Selite: Poisti vanhan 16-merkkisen `UUIDv4`-katkaisun, `TEXT PRIMARY KEY` -hybridijaon sekä kaikki jäljellä olleet `uuid.uuid4()`- ja `Uuid().v4()`-generaattorit koko Python-backendistä ja Flutter-asiakassovelluksesta. Yhdistää Opaque Stripe ID -etuliitteet ja PostgreSQL 19:n natiivin 16-tavuisen RFC 9562 `UUIDv7` -tietotyypin yhdeksi poikkeuksettomaksi standardiksi.*

### 2.1 Ratkaistu ongelma ja kahden peräkkäisen toteutussuunnitelman kokonaisuus

Ennen Askeleen 3.3 toteutusta järjestelmän entiteettitunnisteet olivat jakautuneet kahteen rinnakkaiseen tallennus- ja generointimekanismiin (5 `UUID`-taulua 32-heksalla vs. 7 `TEXT`-taulua 16-heksalla). Lisäksi kun ensimmäinen cutover-suunnitelma (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]`) oli suoritettu ja järjestelmää testattiin käyttöliittymässä sekä yksikkö- ja integraatiotesteissä, havaittiin, että osa sisäisistä apu- ja asiakaspuolen generaattoreista kutsui yhä vanhaa `uuid.uuid4()`- tai `Uuid().v4()`-funktiota ja katkaisi tunnisteita 8 tai 16 heksamerkkiin.

Tämän vuoksi Luvun 2 kokonaisuus toteutettiin kahdella toisiaan täydentävällä toteutussuunnitelmalla ja seurantadokumentilla, joiden toteutusvaiheet (Steps 1–5), dokumentointi (`/tier7-describe-architecture`) ja suunnitelma-auditointi (`/tier8-audit-plan`) on suoritettu, ja joiden tiedostokohtainen 180 säännön AI-karkaisu (`Tier 2 Hardening` via `@[scripts/auto_hardening_runner.py]`) on seuraavana vuorossa:
1. **Osa 3.3a — `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]` & `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` (Steps 1–5 valmiit; `Tier 2 Hardening`: `0/14` Backend + `0/1` Frontend odottaa `auto_hardening_runner.py`-ajoa):**
   * Kaikkien 12 PostgreSQL 19 -taulun natiivi `UUIDv7` DDL-skeema (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`), symmetrinen adapterisilta (`@[backend_v2/database/postgres/entity_adapter.py]`), `OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"` (`@[backend_v2/models/core_base.py]`), koko `@[backend_v2/seed/seed_data.json]`-tiedoston deterministinen 32-hex `UUIDv7` -migraatio, `@[scripts/sanitize_seed_vault.py]`-automaatio, Studio-oletusankkureiden poisto, kausaalisen koheesiomatriisin suora sidonta sekä `@[docs/tiede.md]`-graafimatematiikan synkronointi.
2. **Osa 3.3b — `@[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` & `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` (Steps 1–5 valmiit; `Tier 2 Hardening`: `0/24` Backend + `0/7` Frontend odottaa `auto_hardening_runner.py`-ajoa):**
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
> **STATUS: SEURAAVANA JONOSSA (Askel 3.4: `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` & `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`)**
> *Selite: `@[scripts/_ast_guardrails.py]` kattaa tällä hetkellä säännöt `QGR000`–`QGR030` ja `@[scripts/_dart_guardrails.py]` säännöt `DGR001`–`DGR008`. Alla olevat viisi tarkistusta ja automaatiolaajennusta toteutetaan seuraavaksi Askeleessa 3.4.*

1. **`QGR031` (Kyselysuodattimien staattinen validointi):** Estää virheelliset operaattorit (`"eq"`, `"LIKE"`, `"="`), tyhjät kentät sekä `"in"`-operaattorin vahingolliset merkkijonoliteraalit staattisesti AST-tasolla.
2. **`scripts/`-hakemiston dynaaminen automaattiskannaus:** Korvaa kovakoodatut skriptilistat dynaamisella `scripts/*.py` -globilla, estäen varjoskriptien ja vanhentuneiden aputyökalujen syntymisen laatuporttien ulkopuolelle.
3. **Polyfactory-mallitehtaiden invarianttivartija (`QGR032` & metatestit):** Varmistaa, että testitehtaat käyttävät 32-heksaisia RFC 9562 `UUIDv7` Opaque ID -generaattoreita (`generate_opaque_id`) ja että jokainen tehdas palauttaa aina oletusarvoilla `.build()` validoituvan Pydantic V2 -mallin.
4. **PEP 593 `Annotated[..., Field(...)]` (`QGR020` Check 20B) sekä PEP 257 / `Raises: None` / RFC 7807 `logger.error` (`QGR033`) staattiset AST-säännöt:** Siirtää yleisimmät LLM-hardening-säännöt suoraan `@[scripts/_ast_guardrails.py]`-tarkistukseen, jolloin virheet jäävät kiinni välittömästi `/tier2-execute`-vaiheessa yhdellä kertaa.
5. **Sisältöosoitteinen SHA-256-karkaisuvälimuisti (`@[scripts/auto_hardening_runner.py]`):** Laskee kohdetiedoston, sen yksikkötestien ja `.agents/rules/*.md`-tiedostojen yhdistetyn SHA-256-tiivisteen ja esitäyttää välimuistin valmistuneista Karkaisuaaltojen 1–4 ja UUIDv7-trackereista (`179` kohdetta), kuitaten muuttumattomat tiedostot `- [x]`-tilaan 0 sekunnissa ilman LLM-aliagenttia.
