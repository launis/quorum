# KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTOINTISUUNNITELMA (2026)
## GCP Cloud Run, PostgreSQL 19 Zero-ORM, B2B SaaS IAM, Cloud Storage & Full-Stack Hardening

> [!NOTE]
> **Arkkitehtuurin tila ja Single Source of Truth (SSOT)**
> Tämä asiakirja kokoaa yhteen Cognitive Quorumin tuotantopystytyksen kokonaiskuvan Google Cloud Platformilla (`europe-north1` / Hamina, Suomi). Se korvaa vanhentuneet SQLAlchemy 2.0-, Alembic- ja TinyDB-luonnokset ja nojaa suoraan Quorumin virallisiin 2026-arkkitehtuuristandardeihin sekä dokumentin `@[docs/arkkitehtuurin_parannuskohteet.md]` korjauksiin:
> 1. **PostgreSQL 19 Zero-ORM Perusta & Cutover — [SUORITETTU & LUKITTU]** (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]`)
> 1b. **Järjestelmällinen Ennaltaehkäisy, AST-vartija QGR030 & Testitehtaat — [SUORITETTU & AUDITOITU]** (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md]`, `@[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`)
> 2. **`dag_executor.py` God Code -purku modulaariseksi SRP-paketiksi — [SUORITETTU & KOVENNETTU]** (1 803 LOC -> 6 erillistä SRP-moduulia & ohut fasaadi, QGR017-lukittu) (`@[docs/epic/dag_executor_decomposition_tracker.md]`)
> 3. **Backend-koodikannan Karkaisuaallot 1–4, IAM-karkaisu & Tiedostoajurit (Aallot 1–4: 36 + 36 + 27 + 34 = 133/133 tiedostoa + Askel 4 `EPIC 160` IAM: 37/37 kohdetta + Tiedostoajurit `file_driver.py`, `local_file_driver.py`, `gcs_file_driver.py`: 3/3 karkaistu) — [SUORITETTU & LUKITTU]** (`@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`, `@[docs/epic/EPIC_160_tracker.md]`, `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 1)
> 3b. **Arkkitehtuurin Parannuskohteiden Toteutus, `entity_adapter.py`-purku & Jäännöspoikkeusten Hävitys (Askeleet 3.3–3.7)**:
>    * **Askel 3.3 (Malli A) — [SUORITETTU, KOVENNETTU & LUKITTU]:** Yhtenäinen 32-hex `PrefixedUUID7`-arkkitehtuuri, Natiivi PostgreSQL 19 `UUIDv7` kaikissa 12 taulussa, `@[backend_v2/seed/seed_data.json]` 32-hex Cutover, `@[scripts/sanitize_seed_vault.py]`-automaatio, `@[docs/tiede.md]`-graafimatematiikan synkronointi sekä kaikkien legacy `uuid.uuid4()`- ja `Uuid().v4()`-generaattoreiden poisto ja `QGR030`/`DGR008`-lukitus (`@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` [15/15], `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` [31/31], `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 2).
>    * **Askel 3.4 — [SUORITETTU, KOVENNETTU & LUKITTU]:** AST- ja Laatuporttilaajennukset (`QGR020` PEP 593 `Annotated`-pakko, `QGR031` `FilterOperator`-kurinalaisuus, `QGR032` Polyfactory 32-hex `UUIDv7` -invariantti, `QGR033` PEP 257 / `Raises: None` / RFC 7807 `logger.error` ennen `raise AppException`), dynaaminen `scripts/*.py`-skannaus sekä **`auto_hardening_runner.py` SHA-256 -välimuisti** (`target + unit_test + .agents/rules/` SHA-256, esitäytettynä Karkaisuaaltojen 1–4 ja UUIDv7-trackereiden 179 valmistuneesta kohteesta) (`@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]`, `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`, `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 3).
>    * **Askel 3.4b — [SUORITETTU, KOVENNETTU & LUKITTU]:** FastAPI Reitittimien SSOT-konsolidointi (`reports.py`, `workflows.py`, `system_configs.py`) & Universaalin `CRUD + Clone` (`POST /{id}/clone`) -elinkaaren ja 3-tason poistosuojan lukitus (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]`, `@[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]` [`22/22` karkaistu], `@[ki_router_ssot_and_crud_clone_lifecycle.md]`, `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 4).
>    * **Askel 3.4c (`EPIC 161`) — [100 % SUORITETTU, KOVENNETTU, SYNKRONOITU, AUDITOITU & LUKITTU]:** Topologisen Älykkyyden Säilyttäminen Tislauksessa, Synteesissä & SDUI-raportoinnissa (*5-Pillar Zero-Loss Epistemic Distillation Architecture*, `0 = rajoittamaton` oletusleikkuri `max_synthesis_*`-asetuksille, täysi 4-vaiheinen Micro-CoT- ja sitaattisäilytys, transitiivinen `N_A`-eston periytyminen, täysi kontrastiivinen ja antimallien ankkurointi `MatrixFailureDeficitDTO`-mallissa kaikille `FAILED`- ja `N_A`-defisiiteille, PostgreSQL 19 3-suuntainen Toulmin-falsifikaatio `find_falsified_claims`, 4-tehtävän `CausalSynthesisBriefDTO`-hajautus sekä kontekstuaalinen SDUI/Jinja2/Flutter-pariteetti; Vaiheet 1–4 & Live E2E `8f838d834`, Backend Hardening `31/31`, `/tier7-describe-architecture` `81853a38e`, `/tier8-audit-epic` `83f11d369`, 5 Frontend SDUI -tiedostoa delegoitu Karkaisuaaltoihin F1–F4) (`@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]`, `@[docs/epic/EPIC_161_audit_report.md]`, `@[docs/epic/EPIC_161_tracker.md]`, `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_161/04_phase4_plan.md]`, `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 5).
>    * **Askel 3.5 — [100 % SUORITETTU, KOVENNETTU 9/9, SYNKRONOITU, AUDITOITU & QGR017-LUKITTU]:** `PostgresEntityAdapter` (`[DELETE] backend_v2/database/postgres/entity_adapter.py`, `2 515` LOC, `48` AST-symbolia) Two-Epoch Strangler Fig God Code -purku 6-vaiheiseen Zero-ORM SRP-pakettiin `@[backend_v2/database/postgres/entity_adapter/]`: `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (`255` LOC), `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (`372` LOC), `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (`398` LOC), `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (`405` LOC), `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (`448` LOC), `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (`359` LOC) sekä ohut `242` LOC koordinaattorifasaadi `@[backend_v2/database/postgres/entity_adapter/__init__.py]` (`PostgresEntityAdapter`). Monoliitti on fyysisesti poistettu ja lukittu pysyvästi AST-säännöllä `QGR017` (`@[scripts/_ast_guardrails.py]`); `100 %` lausekattavuus (`730/730` lausetta, `33` modulaarista yksikkötestiä + `18` Golden Master -pariteettitestiä), Epoch 2 Backend Hardening `9/9` (`467885671`–`f32dfadf4`), `/tier7-describe-architecture` (`fb94d8dbe`) ja `/tier8-audit-plan` (`a7a5ac6c7`) läpäisty (`@[docs/epic/entity_adapter_decomposition_tracker.md]`, `@[docs/epic/tasks_entity_adapter/]`).
>    * **Askel 3.6 (`EPIC 162`) — [100 % SUORITETTU, KOVENNETTU 31/31, SYNKRONOITU, AUDITOITU, E2E-TODENNETTU & LUKITTU]:** Studio `OutputProfile` & `Workflow` `target_blocks` -synkronointi steppiä poistettaessa (`_sync_output_profiles_for_workflow` & poistettava virhetyylinen `FilterChip`), `CognitiveTier` SSOT & `LLMClient.from_strategy` -yhteensopivuussillan poisto (`QGR030` AST-vartija) sekä DAG-suorituksen resilienssi (semanttinen oskillaatiotunnistin `_compute_retry_output_digest` ja kumulatiivinen `usage_agg` `execute_engine_retry_stage`-vaiheessa, ajokohtainen `ExecutionBudget`-katto `_enforce_execution_budget` + `ErrorCodes.QUOTA_EXCEEDED`, solmutason `input_merkle_hash`, MCP XML -ohjaustagien suodatus `_sanitize_mcp_xml_control_tags` ja prosessienvälinen optimistinen lukitus `state_version` OCC PostgreSQL 19 `executions`-taulussa; `27/27` Backend + `4/4` Frontend = `31/31` karkaistu, `/tier7-describe-architecture` `9066bc8ab`, `/tier8-audit-epic` `@[docs/epic/EPIC_162_audit_report.md]` sekä E2E-todennettu ajolla `exe_01a19ad8c8807129955f7c2e90d12a52` / `rep_01a19adc9f7b71c3bc89b220140aced2`) (`@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]`, `@[docs/epic/EPIC_162_tracker.md]`, `@[docs/epic/tasks_EPIC_162/]`, `@[docs/arkkitehtuurin_parannuskohteet.md]` Luvut 6, 7 & 8).
>    * **Askel 3.7 (`EPIC 163`) — [100 % SUORITETTU, KOVENNETTU, SYNKRONOITU, AUDITOITU & LUKITTU]:** Kaikkien AST/Dart-laatuporttien jäännöspoikkeuslistojen (`RESIDUAL_*` ja `pyproject.toml` `per-file-ignores`) poisto, 100 % PEP 593 `Annotated`-tyypitys ja oletusarrokielto (`QGR020` Check 20B/20C), `JsonValue`- ja Open-JSON-rakenteiden hävitys (`QGR027` & `DGR005` rajattuna 9 kuljetusrajatiedostoon), muuttumattomat `ExecutionRecord`-tilasiirtymäapurit (`QGR028`: `with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`), `InMemoryUnitOfWork`-migraatio kaikille taustatyöntekijätesteille (`Census F = 0` tiedostossa `@[scripts/audit_warning_baseline.py]`) sekä `DGR013`/`DGR014`/`QGR013`/`QGR033` Check 33B -lukitus (`@[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]`, `@[docs/epic/EPIC_163_tracker.md]`, `@[docs/epic/EPIC_163_audit_report.md]`).
> 4. **B2B SaaS IAM, Token Exchange & Enterprise Hardening (`EPIC 160`) — [100 % SUORITETTU, KOVENNETTU 51/51, SYNKRONOITU (TIER 7), AUDITOITU (TIER 8) & LUKITTU]** (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`, `@[docs/epic/EPIC_160_tracker.md]`, `@[docs/epic/EPIC_160_audit_report.md]`, `@[docs/epic/tasks_EPIC_160/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_160/06_phase6_plan.md]`)
> 4b. **Post-EPIC 160 BYOK Tietokantapysyvyys, Ajonaikainen LLM/MCP-kytkentä, 100 % Tietokantapohjainen Secret SSOT (Nolla `.env`-varapolkua), JSONB/Wire DTO Bug-Hunting, Yhtenäinen Telemetria-/Firebase-salaisuusseedaus (`EPIC 164`), Tehtävänantojen & Suoran Tehtäväportaalin Karkaisu (Findings A–E) & E2E-todennus (Askeleet 4.1–4.6):**
>    * **Askel 4.1 — [100 % SUORITETTU, KOVENNETTU & AUDITOITU]:** `SecretService` PostgreSQL 19 `UnitOfWorkFactory`-kytkentä ja fyysinen poisto (`delete_collection_document("tenant_secrets", secret_id)`), muistivarapolkujen (`_local_secrets`, `_deleted_secret_ids`) hävitys, pakollinen `storage_mode` `TenantSecretCreateDTO`/`TenantSecretCreateDto`-malleissa, kanoninen `name TEXT NOT NULL` `SystemConfigMCPGateways`/`McpGateway`-malleissa sekä scope-tietoinen `org_secret_target_dropdown` (`sys_<hex32>` ja `LLMProvider`) (`@[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md]`, `@[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]`).
>    * **Askel 4.2 — [100 % SUORITETTU, KOVENNETTU & AUDITOITU]:** JSON Schema Draft 2020-12 MCP-työkalusanasto, `McpToolParamsPanel` `anyOf`/`oneOf`/`array`-komponentit ja 17-parametrin Tavily-skeema `@[backend_v2/seed/seed_data.json]`-tiedostossa (`@[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md]`, `@[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md]`), kanonisten `id`-relaatioiden, `slug`-kiellon ja oletusarvojen staattiset AST/DDL/Seed-laatuportit (`QGR016`, `QGR020`, `QGR030`, `QGR031`, `ZORM004`, `ZORM007`) (`@[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]`, `@[docs/implementationplans/TRACKER_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]`) sekä `system_configs` `NULL`-nimien preflight-skeemavalidointi ja live-seedaus (`@[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md]`, `@[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md]`).
>    * **Askel 4.3 — [100 % SUORITETTU, KOVENNETTU & AUDITOITU]:** `LLMClient.from_tier` kytketty suoraan `SecretService.resolve_llm_key`-hakuun (`ResolvedCredentialDTO` ja `SecretStr`-kapselointi) ja organisaatiokonteksti (`organization_id`) välitetty päästä päähän `ExecutionIngressService` (`GlobalContextVarsDTO`), Vaiheen 1 `execute_engine_retry_stage` (`LLMClient` + `ToolDispatcher`) ja Vaiheen 2 synteesityöntekijöiden (`synthesis_worker.py`, `variance_synthesis.py`) läpi (`@[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md]`, `@[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]`).
>    * **Askel 4.4 — [100 % SUORITETTU, KOVENNETTU, SYNKRONOITU, AUDITOITU & E2E-TODENNETTU]:** 100 % tietokantapohjainen LLM- ja MCP-salaisuuksien haku PostgreSQL 19 `tenant_secrets`-taulusta (`organization_id` $\rightarrow$ `ROOT_SYSTEM` luokassa `SystemOrganizations` $\rightarrow$ Fail-Fast `ConfigurationError`) ilman yhtäkään `.env`- tai `os.environ`-varapolkua (`_resolve_platform_llm_secret` ja `_resolve_platform_mcp_secret` poistettu fyysisesti, `"auth_env_var": null` tiedostossa `@[backend_v2/seed/seed_data.json]`), monirivisen Vertex AI Service Account JSON -avaimen syöttö (`org_secret_visibility_toggle_btn`) ja kontekstivälimuistien organisaatioeristys (`VertexCacheAdapter`, `GoogleAIStudioCacheAdapter`, `LLMCachingService`, `EnrichedDagExecutor`, `TwoPassAtomizer`, `RAGPreflightService`, `mcp_tool_loop`, hooks) sekä `GlobalContextVarsDTO.initiator_id` kanonisointi, PostgreSQL 19 binäärisen JSONB-koodekin esiserialisoitujen merkkijonojen purku (`encode_jsonb_binary` + `exclude_none=True`) ja Flutter `ExecutionRecord`/`ExecutionMetadata`/`ExecutionTraceItemDto`/`ProfileSynthesisEntryDto` 1:1 lankapariteetti (`91` malliparia `audit_dto_parity.py`:ssä, commitit `e0cc6cf79`–`b3980130d`) (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]`, `@[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]`), **sekä E2E-todennettu ajolla `exe_01a1c086576272b7a33c508d27277e94` / `rep_01a1c08a762d70b8b3b7c2fae8fcf6da`** (`PASSED & FINALIZED`, `healing_cost_events: 0`, ``data/files/executions/exe_01a1c086576272b7a33c508d27277e94/forensic_summary.md``).
>    * **Askel 4.5 (`EPIC 164`) — [100 % SUORITETTU, KOVENNETTU 17/17, SYNKRONOITU, AUDITOITU & LUKITTU]:** Yhtenäinen salaisuusseedaus `.env.secrets.local`-tiedostosta (`LocalSeedSecretsSettings` tiedostossa `@[backend_v2/seed/run_seed.py]`), `SecretScope.TELEMETRY` (`"telemetry"`, `ROOT`-rajattu RBAC organisaatiolle `ROOT_SYSTEM` luokassa `SystemOrganizations`), `"tenant_secrets"` mukana 11 taulun `CANONICAL_SEED_TABLES`-vakiossa, automaattinen `ROOT`-käyttäjän Firebase Auth -provisiointi (`_provision_root_firebase_user`), käynnistysaikainen tietokantapohjainen Logfire-tokenin (`resolve_startup_logfire_token` tiedostossa `@[backend_v2/core/telemetry.py]`) ja Firebase Admin SDK:n (`initialize_firebase_admin_from_secrets` tiedostossa `@[backend_v2/services/auth/token_service.py]`) alustus muistista (`main.py` & `worker.py`) sekä kaikkien fyysisten `service-account.json`-viittausten ja mock-kirjautumisten (`allow_mock_tokens`, `MockLoginPanel`, `debugMockLogin`) täydellinen poisto (`@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, `@[docs/epic/EPIC_164_tracker.md]`, `@[docs/epic/EPIC_164_audit_report.md]`).
>    * **Askel 4.6 — [100 % SUORITETTU, KOVENNETTU 14/14, SYNKRONOITU, AUDITOITU & LUKITTU]:** Tehtävänantojen, `TaskBrief` (`PromptBlockCategory.TASK_DEFINITION`) `CRUD + Clone` -elinkaaren ja suoran tehtäväportaalin (`/task/:token`) päästä päähän -karkaisu (Findings A–E): kanoninen Resend EU REST -runko (`from`, `to`, `subject`, `html`, `tags`), `html.escape(..., quote=True)`-suojattu `"Open Quorum Portal"` CTA-painike sekä `_redact_action_url`- ja `mask_email_address`-konsolisuojaukset palvelussa `@[backend_v2/services/auth/email_service.py]` (`QGR033`), normalisoitu vierasavain `execution_assignments.task_brief_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL` (`ZORM004`/`ZORM006`/`ZORM007`) ja `TaskAssignmentBriefDTO` $\leftrightarrow$ `TaskAssignmentBriefDto` 1:1 lankapariteetti (`92 / 92` jaettua DTO-paria `audit_dto_parity.py`:ssä), portaalin tiedostolatausten välitön `Base64Attachment`-purku (`ExecutionAssignmentService._normalize_assignee_ingress_inputs` sekä `/draft`- että `/submit`-poluilla), autenttinen Firebase Auth + pakollinen TOTP 2FA JIT -onboarding (`_verify_onboarding_firebase_token` merkitsee `email_verified=True` `IDENTITY_MISMATCH`-tarkistuksen jälkeen ennen `_enforce_firebase_mfa_claim`-vaatimusta; `AuthRepository.authenticateForTaskOnboarding` käsittelee Firebase Email Enumeration Protectionin `'invalid-credential'`-koodin ja portaalin sisäisen `MFA_REQUIRED` TOTP-aktivoinnin) sekä itsenäinen `TaskAssignmentConfigDialog` ja `ADMIN`/`ROOT`-käyttäjien `_TaskBriefsManagementCard` (`1 387` läpäistyä Flutter-testiä, commitit `f50520284`–`08385c09b`) (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]`, `@[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]`).
> 5. **Firebase Storage & Direct-to-Cloud Signed URLs (Valinnainen laajennus yli 32 MB suoralatauksille) — [NYKYISET TIEDOSTOAJURIT KARKAISTU 3/3; SUORALATAUSLAJENNUS SUUNNITELMAAVAIHEESSA]** (`@[backend_v2/services/file_driver.py]`, `@[backend_v2/services/drivers/local_file_driver.py]`, `@[backend_v2/services/drivers/gcs_file_driver.py]` karkaistu commiteissa `fa940a23f`–`85a7721ea`; Direct-to-Cloud Signed URLs `[NEW]` `@[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]`)
> 6. **Frontend & Studio UI Hardening (`client_app_v2` Karkaisuaallot F1–F4: 185/185 `.dart`-tiedostoa + Askel 4 `EPIC 160` IAM/Settings/Portal: 14/14 `.dart`-kohdetta = 100 % karkaistu) sekä Uusien Laatuporttien (`d44a5e77b`) Täyden Työtilan SHA-256 Uudelleenkarkaisu (`Yöajot 1–4`)** (`@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]` – `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]`, `@[docs/epic/EPIC_160_tracker.md]`, `@[data/hardening_cache.json]`)
> 7. **GCP Production Deployment (Kooditason Cloud Run -valmius — [100 % SUORITETTU, KOVENNETTU 5/5, SYNKRONOITU & AUDITOITU]) & Guided Cloud Cutover (`qrum.ai`) — [SEURAAVA TUOTANTOASKEL]** (`@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`, `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`, `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`, `[NEW] @[scripts/provision_gcp_cloud.py]`)

---

## Luku 0: Pilvi-infrastruktuuri ja Verkkoympäristö (GCP europe-north1)

> [!NOTE]
> **GCP-tuotantopystytyksen ja infrastruktuurin suunnitelma & tracker (EPIC 74)**
> Yksityiskohtainen arkkitehtoninen toteutussuunnitelma ja vaiheittainen seurantadokumentti:
> * **Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`
> * **Seurantadokumentti (Tracker):** `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`

Tuotantoympäristö provisioidaan Google Cloud Platformin Haminan datakeskukseen (`europe-north1`) samaan GCP-projektiin, jossa Firebase Auth ja Storage sijaitsevat:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                        │
│                    (europe-north1 / Finland)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Cloud Run: API      │    │  Cloud Run: Worker   │          │
│  │  (quorum-api)        │    │  (quorum-worker)     │          │
│  │  min: 1, max: 10     │    │  min: 1, max: 5      │          │
│  │  2 vCPU / 2 GB       │    │  2 vCPU / 4 GB       │          │
│  │  Tilaton (Stateless) │    │  Arq async daemon    │          │
│  └──────────┬───────────┘    └──────────┬───────────┘          │
│             │ VPC Connector (Private IP) │                      │
│             ▼                            ▼                      │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Cloud SQL           │    │  Memorystore         │          │
│  │  (PostgreSQL 19)     │    │  (Redis 7 / 8)       │          │
│  │  PgBouncer pooling   │    │  Kill-Switch &       │          │
│  │  Private IP (VPC)    │    │  FinOps Rate Limit   │          │
│  │  PITR: 7-14 päivää   │    │  Private IP (VPC)    │          │
│  └──────────────────────┘    └──────────────────────┘          │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Firebase Auth       │    │  Vertex AI & LiteLLM │          │
│  │  (IdP / SSO)         │    │  BYOK LLM Provider   │          │
│  │  Google / Email      │    │  Context Caching     │          │
│  └──────────────────────┘    └──────────────────────┘          │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Cloud Storage       │    │  Secret Manager      │          │
│  │  (Direct Signed URLs)│    │  (DATABASE_URL,      │          │
│  │  PDF & User Inputs   │    │   JWT Secret, KMS)   │          │
│  └──────────────────────┘    └──────────────────────┘          │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Cloud Load Balancer + Cloud Armor               │          │
│  │  HTTPS-terminointi, DDoS-suojaus, Custom Domain  │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 0.1 Cloud SQL for PostgreSQL 19
* **Versio:** PostgreSQL 19 (natiivi `uuidv7()`, `uuid_extract_timestamp() VIRTUAL`, `default_toast_compression = lz4`, `json_array()`).
* **Verkkoeristys (VPC):** Public IP on kytketty kokonaan pois. Kantaan pääsee ainoastaan sisäisen VPC-verkon (`quorum-vpc`) ja Serverless VPC Access Connectorin kautta.
* **Yhteysallas (PgBouncer):** Sisäänrakennettu PgBouncer (Transaction pooling mode). Estää asynkronisen Python-backendin yhteyksien loppumisen.
* **Varmuuskopiot:** Point-in-Time Recovery (PITR) 7–14 päivää automaattisella säilytyksellä.

### 0.2 Memorystore for Redis
* **Käyttötarkoitus:** 
  1. Istuntojen reaaliaikainen mitätöinti (**Fail-Closed Kill-Switch**, O(1) haku `revoked:usr:{id}`).
  2. Organisaatiokohtainen pyyntörajoitus (**AI FinOps TPM/RPM Rate Limiting**).
* **Verkkoeristys:** Private IP samassa VPC-verkossa Cloud Runin kanssa.

### 0.3 Salaisuuksien hallinta (Secret Manager)
* Nollatoleranssi `.env`-tiedostoille tai kovakoodatuille avaimille tuotannossa.
* Cloud Run lataa käynnistyessään salaisuudet (`DATABASE_URL`, `JWT_SECRET_KEY`, Cloud KMS -avaimet) suoraan GCP Secret Managerista ympäristöinjektiona.

### 0.4 Verkkotunnukset, Reititys ja `qrum.ai` -varaus
Tuotannon verkkoinfrastruktuuri ja kuormantasaus konfiguroidaan tukemaan virallisesti vapaaksi todennettua kansainvälistä pääverkkotunnusta **`qrum.ai`** (4-merkkinen ultra-lyhyt globaali verkkotunnus):
* **1. Verkkotunnuksen hankinta ja DNS-vyöhykkeen delegointi (`qrum.ai`):**
  * `whois.nic.ai` -rekisteritarkistus vahvistaa verkkotunnuksen `qrum.ai` olevan vapaana rekisteröitäväksi.
  * Rekisteröidään `qrum.ai` ensisijaiseksi globaaliksi verkkotunnukseksi valtuutetulla verkkotunnusvälittäjällä (nimenomaan ja tyhjentävästi: Cloudflare Registrar tai Google Cloud Domains) ja ohjataan nimipalvelimet (`NS`-tietueet) Google Cloud DNS -vyöhykkeeseen (`qrum-ai-zone`).
  * Asetetaan verkkotunnus Cloud Run -ympäristömuuttujiin (`PRIMARY_DOMAIN=qrum.ai`, `JWT_ISSUER=https://api.qrum.ai`, `JWT_AUDIENCE=https://qrum.ai`, `ENVIRONMENT=production`). `Settings._enforce_environment_limits` (`@[backend_v2/settings.py]`) johtaa tuotannon `cors_origins`-alkuperät (`https://qrum.ai`, `https://app.qrum.ai`, `https://studio.qrum.ai`) automaattisesti `PRIMARY_DOMAIN`-arvosta ilman manuaalista `CORS_ORIGINS`-ympäristömuuttujaa, eikä Python- tai Flutter-lähdekoodiin tarvita yhtäkään koodimuutosta.
* **2. Domain-jako ja reititys (Cloud Load Balancer & Cloud DNS):**
  * `api.qrum.ai` $\rightarrow$ Cloud Run API (`quorum-api`) REST/SSE-rajapinnat.
  * `app.qrum.ai` / `studio.qrum.ai` $\rightarrow$ Flutter Web & Studio -käyttöliittymä.
  * `qrum.ai` $\rightarrow$ Yrityksen pääsivusto / landing page ja ohjaus sovellukseen.
* **3. Google-Managed SSL/TLS -monivarmenne (SAN Certs):**
  * Luodaan Google-Managed SSL-sertifikaatti (`qrum-san-cert`), joka kattaa kaikki alidomainit (`qrum.ai`, `api.qrum.ai`, `app.qrum.ai`, `studio.qrum.ai`) yhdellä globaalilla Anycast IP -osoitteella (`qrum-global-ip`).
* **4. Cloud DNS & SAN SSL -provisiointikomennot (PowerShell):**
  ```powershell
  gcloud compute addresses create qrum-global-ip --global --ip-version IPV4
  gcloud dns managed-zones create qrum-ai-zone --dns-name="qrum.ai." --description="Quorum Primary Production DNS Zone" --visibility=public
  gcloud dns record-sets create qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud dns record-sets create api.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud dns record-sets create app.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud dns record-sets create studio.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud compute ssl-certificates create qrum-san-cert --domains="qrum.ai,api.qrum.ai,app.qrum.ai,studio.qrum.ai" --global
  ```
* **5. CORS & Origin Security (`@[backend_v2/settings.py]`):**
  * API-ingress sallii nimenomaisesti tuotanto-originit: `https://qrum.ai`, `https://app.qrum.ai`, `https://studio.qrum.ai`.
* **6. Firebase Auth & OAuth Redirect URIs:**
  * Lisätään Firebase Authenticationin *Authorized Domains* -listalle: `qrum.ai`, `app.qrum.ai`, `api.qrum.ai`.
* **7. JWT Issuer & Audience SSOT:**
  * Quorum Local JWT:n token-väitteet: `iss = "https://api.qrum.ai"`, `aud = "https://qrum.ai"`.

---

## Luku 1: Zero-ORM Työkalupakki ja Ajonaikaiset Kirjastot

Tuotantoarkkitehtuurissa poistetaan kaikki demotason tiedostokannat (TinyDB) sekä raskaat välikädet (SQLAlchemy, Alembic, hashids).

### 1.1 Poistettavat legacy-riippuvuudet
* `tinydb` (tiedostopohjainen demotietokanta — poistettu Askeleessa 3.1).
* `sqlalchemy` & `alembic` (korvattu puhtaalla Zero-ORM `asyncpg`:llä ja SQL DDL:llä).
* `hashids` (korvattu RFC 9562 `PrefixedUUID7` -standardilla).

### 1.2 Tuotantotason Python-ajoympäristö (`backend_v2`)
```toml
# Hallitaan uv-paketinhallinnalla (uv.lock SSOT)
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "asyncpg>=0.30.0",          # Natiivi asynkroninen PostgreSQL-ajuri
    "pydantic>=2.10.0",         # DTOt ja domain-validointi (pydantic_core Rust)
    "pydantic-settings>=2.6.0", # Tyypitetyt ympäristömuuttujat
    "redis>=5.3.1",             # Asynkroninen Redis Kill-Switchille ja Arqille
    "arq>=0.26.3",              # Asynkroninen taustatyöjono Cloud Run Workerille
    "firebase-admin>=6.6.0",    # Firebase ID Token validointi ja Signed URLs
    "google-cloud-storage>=2.19.0",
    "google-cloud-secret-manager>=2.21.0",
    "cryptography>=44.0.0",     # BYOK Envelope Encryption (AES-256-GCM)
    "logfire[fastapi,httpx,litellm,requests,system-metrics]>=4.37.0", # OpenTelemetry-observabiliteetti
]
```

---

## Luku 2: Tietokantamallit ja Yhtenäinen Natiivi UUIDv7 (Zero-ORM SSOT & Malli A)

PostgreSQL 19 on Single Source of Truth (SSOT) kaikelle sovellusdatalle. Tiedostojen binäärejä ei säilytetä relaatiokannassa, vaan kanta hallinnoi ainoastaan metadataa.

### 2.1 Pääavaimet ja Yhtenäinen RFC 9562 `PrefixedUUID7` (Malli A — `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 2)
* **Yksi yhtenäinen tunnistestandardi kaikissa 15 taulussa (Askel 3.3 & Askel 4 `EPIC 160`):** Kaikki 15 PostgreSQL 19 -taulua (nimenomaan ja tyhjentävästi: `organizations`, `users`, `invitations`, `tenant_secrets`, `execution_assignments`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes` ja `quorum_edges`) käyttävät primääriavaimena PostgreSQL 19:n natiivia 16-tavuista `UUID`-tyyppiä (`UUID PRIMARY KEY DEFAULT uuidv7()`).
* Python- ja Flutter-rajapintakerroksessa kaikki pää- ja viiteavaimet sillataan tyyppiturvalliseen 32-heksadesimaaliseen **`PrefixedUUID7`** -muotoon (`OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`):
  * Käyttäjät: `usr_<hex32>` (kanoninen muoto `usr_01950000000070008000000000000001`)
  * Organisaatiot: `org_<hex32>` (järjestelmän juuriorganisaatio `ROOT_SYSTEM` = `"org_0195f3a0000070008000000000000001"` luokassa `SystemOrganizations`)
  * Kutsut: `inv_<hex32>`, Salaisuudet (BYOK): `sec_<hex32>` ja Suorat tehtäväosoitukset (Assignments): `tsk_<hex32>`
  * Konfiguraatio- ja Studio-entiteetit: `cfg_<hex32>`, `blk_<hex32>`, `stp_<hex32>`, `wf_<hex32>`, `out_<hex32>`, `row_<hex32>`, `tda_<hex32>`, `var_<hex32>`, `scl_<hex32>`, `gate_<hex32>`
  * Suoritus- ja Graafientiteetit: `exe_<hex32>`, `rep_<hex32>`, `nod_<hex32>`, `edg_<hex32>`
* **Automaattinen Seed Vault -työkalu (`@[scripts/sanitize_seed_vault.py]`):** Kun kehittäjä lisää uuden entiteetin, matriisirivin tai väitteen `@[backend_v2/seed/seed_data.json]`-tiedostoon, `sanitize_seed_vault.py` generoi puuttuvan tai vanhan 16-heksaisen tunnisteen tilalle kanonisen 32-merkkisen `UUIDv7`-tunnisteen `generate_uuid7_opaque_id(prefix)`-funktiolla ja päivittää kaikki sisäiset viitteet atomisesti ennen `@[backend_v2/seed/run_seed.py]`-ajoa.

### 2.2 SQL DDL -skeema (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`)
Kanta alustetaan ilman Alembicia suoralla, idempotentilla SQL DDL -tiedostolla, jossa kaikki 15 taulua hyödyntävät natiivia `UUID PRIMARY KEY DEFAULT uuidv7()` -määrittelyä, `CHECK (uuid_extract_version(id) = 7)` -versiotarkistusta ja `uuid_extract_timestamp(id) VIRTUAL` -saraketta (mahdollinen yli 32 MB suoralatausten 16. `file_metadata`-lisätaulu on rajattu valinnaiseksi laajennukseksi Luvussa 4 / Askeleessa 5):

```sql
-- PostgreSQL 19 Natiivi Skeema (Ote tiedostosta 001_pg19_uuidv7_schema.sql: organizations & users)

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE,
    tier TEXT NOT NULL DEFAULT 'standard',
    subscription_status TEXT NOT NULL DEFAULT 'ACTIVE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    quota_limit NUMERIC(10, 2) NOT NULL DEFAULT 100.00,
    tpm_limit BIGINT NOT NULL DEFAULT 100000,
    rpm_limit INTEGER NOT NULL DEFAULT 60,
    allowed_email_domains JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_organizations_id_uuidv7 CHECK (uuid_extract_version(id) = 7)
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    firebase_uid TEXT UNIQUE,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_users_id_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT chk_users_org_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);

CREATE INDEX IF NOT EXISTS idx_users_org_active ON users(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid);
```

### 2.3 Pydantic V2 Domain-malli (`@[backend_v2/models/auth.py]`)
SQLAlchemy-luokkien sijaan backend käyttää muuttumattomia Pydantic V2 -malleja:
```python
class User(UserBase):
    """Immutable User Domain Entity (Zero-ORM SSOT)."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(pattern=r"^usr_[a-fA-F0-9]{32}$")]
    organization_id: Annotated[str, Field(pattern=r"^org_[a-fA-F0-9]{32}$")]
    firebase_uid: Annotated[str, Field(min_length=1, max_length=128)]
    email: Annotated[EmailStr, Field(description="User email address")]
    role: Annotated[UserRole, Field(description="System authorization role")]
    is_active: Annotated[bool, Field(default=True)]
    deleted_at: Annotated[datetime | None, Field(default=None)]
```

### 2.4 Zero-ORM Adapterikerros ja SRP-pakkausrakenne (`@[backend_v2/database/postgres/]`)

PostgreSQL 19 Zero-ORM -arkkitehtuuri nojaa suoraan `asyncpg`-ajuriin ja heksagonaalisiin portteihin (`GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`). Kanta-adaptereista muodostuu kolme ydinkomponenttia:

1. **`PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter/]`, 6 SRP-vaihemoduulia + `242` LOC fasaadi, lukittu AST-säännöllä `QGR017`):**
   * **Vastuu:** Kokoaa yhteen kaikkien 13 entiteettitaulun (`organizations`, `users`, `invitations`, `tenant_secrets`, `execution_assignments`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`) natiivit parametroidut SQL-kyselyt, `_to_pg_uuid` / `_from_pg_uuid` -siltauksen, JSONB-projektion ja eräseedauksen (sekä graafitaulut `quorum_nodes` ja `quorum_edges` `PostgresGraphAdapter`-adapterissa = yhteensä 15 PostgreSQL 19 -taulua, lukittu `@[scripts/audit_zero_orm_strictness.py]`-laatuportilla).
   * **Toteutettu ja kovennettu 6-vaiheinen pakettirakenne (Askel 3.5 / Luku 7 Kohta 13 — `@[docs/epic/entity_adapter_decomposition_tracker.md]`):** Alkuperäinen `2 515` LOC (`48` AST-symbolin) monoliitti `[DELETE] backend_v2/database/postgres/entity_adapter.py` on purettu Two-Epoch Strangler Fig -protokollalla pakettiin `@[backend_v2/database/postgres/entity_adapter/]` ja lukittu pysyvästi AST-säännöllä `QGR017`:
     * `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (`255` LOC — sarakelistat, `FilterOperator`-kuvaukset, `UUIDv7`-siltaus ja JSONB-koersioapurit)
     * `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (`organizations`, `users`, `invitations`, `tenant_secrets`, `execution_assignments`, `system_configs`)
     * `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (`398` LOC — `prompt_blocks`, `steps`)
     * `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (`405` LOC — `workflows`, `output_profiles`)
     * `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (`448` LOC — `executions`, `report_artifacts`, `report_binaries` ja kevyt `ExecutionSummarySnapshot`-projektio)
     * `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (`359` LOC — idempotentti `seed_validated_buffer` ja kokoelmatason reititys)
     * Ohut `242` LOC koordinaattorifasaadi `@[backend_v2/database/postgres/entity_adapter/__init__.py]` (`PostgresEntityAdapter`), jolla on `100 %` lausekattavuus (`730/730` lausetta).
2. **`PostgresGraphAdapter` (`@[backend_v2/database/postgres/graph_adapter.py]`, 669 LOC):**
   * **Vastuu:** Kausaalipäättelygraafin (`quorum_nodes` ja `quorum_edges`; domain-malleina `PropositionNode` ja `DependencyEdge`) Kahnin aallot, asyklisyyden varmennus (`detect_cycle`) ja falsifioitujen väitteiden suodatus.
3. **`PostgresPoolManager` (`@[backend_v2/database/postgres/pool.py]`, 534 LOC):**
   * **Vastuu:** `asyncpg`-yhteysaltaan elinkaari, transaktiorajat, binääriset `\x01` `pydantic_core` JSONB-koodekit ja DDL-migraatioiden suoritus ilman ulkoisia migraatiotyökaluja.

---

## Luku 3: B2B SaaS IAM, Token Exchange ja Turvallisuus

### 3.1 RFC 8693 Token Exchange & Session Upgrade
Tietokantaa ei koskaan kysellä jokaisella saapuvalla HTTP-pyynnöllä:
1. **Kirjautuminen / Vaihto:** Asiakassovellus kirjautuu Firebase Authiin ja lähettää lyhytikäisen Firebase ID Tokenin backendille: `POST /api/v2/iam/auth/exchange`.
2. **Kertatarkistus & pakollinen TOTP 2FA:** Backend (`@[backend_v2/services/auth/token_service.py]:TokenService.exchange_firebase_token`) tarkistaa Firebase-allekirjoituksen Firebase Admin SDK:lla, vaatii pakollisen `firebase.sign_in_second_factor`-väitteen, estää 1:1 `firebase_uid`-törmäykset (`ErrorCodes.CONFLICT`), hakee käyttäjän kannasta `firebase_uid`-kentällä ja varmistaa aktiivisuuden (`deleted_at IS NULL`).
3. **Quorum Local JWT:** Backend myöntää asiakkaalle 15 minuutin sisäisesti allekirjoitetun JWT-tokenin, joka sisältää valtuutustiedot:
   * `sub`: `usr_<hex32>`
   * `org`: `org_<hex32>`
   * `role`: `UserRole`
4. **0,1 ms API-validointi RAMissa:** Kaikki API-kutsut käyttävät Local JWT:tä. Sen validointi tapahtuu FastAPI:n `get_current_user_from_header` -riippuvuudessa suoraan muistissa ilman tietokantalatenssia.

### 3.2 Redis Fail-Closed Kill-Switch
Jos ylläpitäjä sulkee käyttäjätilin, muuttaa roolia tai käyttäjä poistetaan GDPR-pyynnöllä:
* Backend (`@[backend_v2/core/redis_security.py]:RevocationCache`) kirjoittaa välittömästi Redisiin käyttäjäkohtaisen avaimen `revoked:usr:{user.id}` tai istuntokohtaisen avaimen `revoked:jti:{jti}` (TTL = 900 s) ja tarkistaa jokaisella API-kutsulla atomisesti molemmat avaimet yhdellä `MGET revoked:usr:{user_id} revoked:jti:{jti}` -komennolla (sekä valvoo RPM/TPM-kiintiöitä `TenantRateLimitService`-palvelulla).
* Jokainen API-kutsu tarkistaa O(1) nopeudella Redisistä, ettei käyttäjä ole estolistalla.
* **Fail-Closed:** Jos Redis-yhteys katkeaa, järjestelmä palauttaa `503 Service Unavailable`, estäen oikeuksien vuotamisen.

### 3.3 Enterprise BYOK (Bring Your Own Key) ja 100 % Tietokantapohjainen Salaisuusarkkitehtuuri (`Askeleet 4.1–4.5`)
Quorum noudattaa kolmiportaista B2B SaaS -salaisuusarkkitehtuuria, jossa kaikki ajonaikaiset tekoäly- (`LLMProvider`) ja MCP-työkaluavaimet (`McpGateway.id`) ratkaistaan 100 % PostgreSQL 19 `tenant_secrets`-taulusta ilman `.env`- tai `os.environ`-varapolkuja:
* **Kolmiportainen salaisuushierarkia (3-Tier Secret Architecture):**
  1. **Taso 1 — Infrastruktuurin käynnistysavaimet (`Infrastructure Bootstrap Secrets`):** `.env`-tiedostossa ja Cloud Runin ympäristömuuttujissa (`@[backend_v2/settings.py]`: `Settings`) säilytetään nimenomaan ja tyhjentävästi alustan käynnistämiseen tarvittavat infrastruktuuri- ja kuljetusavaimet: `DATABASE_URL` (`postgres_dsn`), `JWT_SECRET_KEY` (ja valinnainen Cloud KMS -avainviite `KMS_MASTER_KEY_ID`), `SERVICE_AUTH_SECRET`, `REDIS_HOST` / `REDIS_PORT`, `STORAGE_BACKEND=POSTGRES`, `STORAGE_BUCKET_NAME`, `GCP_PROJECT`, `GCP_REGION`, `PRIMARY_DOMAIN`, `JWT_ISSUER`, `JWT_AUDIENCE`, `API_URL`, `FRONTEND_APP_BASE_URL`, `EMAIL_TRANSPORT_MODE`, `EMAIL_FROM_ADDRESS`, `EMAIL_API_ENDPOINT` ja `EMAIL_API_KEY`.
  2. **Taso 2 — Alustan oletusavaimet (`Platform Default / ROOT_SYSTEM Baseline Secrets`):** Järjestelmän oletus-LLM-avaimet (`openai`, `ai_studio`, `anthropic`, `vertex_ai` Service Account JSON joka alustaa käynnistyksessä muistipohjaisesti myös Firebase Admin SDK:n kutsulla `initialize_firebase_admin_from_secrets`), MCP-yhdyskäytäväavaimet (`sys_0195f3a00000700080008172bda70c86` Tavily MCP Gateway) sekä telemetriatokenit (`SecretScope.TELEMETRY`: `"logfire"` ja `"logfire_read"`, `resolve_startup_logfire_token`) tallennetaan salattuina PostgreSQL 19 `tenant_secrets`-tauluun järjestelmäorganisaatiolle `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`, luokka `SystemOrganizations`). Paikallisessa kehityksessä ja `quorum-seed`-ajossa nämä alustetaan tyypitetysti `LocalSeedSecretsSettings`-mallilla (`.env.secrets.local` tai `SECRET_*`-ympäristöinjektio seed-ajolle).
  3. **Taso 3 — Asiakasorganisaation BYOK-avaimet (`Customer Tenant BYOK Secrets`):** Asiakasorganisaation ylläpitäjä (`ADMIN` / `ROOT`) tallentaa organisaation omat LLM- ja MCP-avaimet näkymässä `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]` (`_ByokSecretsCard`) asiakkaan omalle `organization_id`-tunnisteelle.
* **100 % tietokantapohjainen ratkaisuketju ja Fail-Fast (`@[backend_v2/services/auth/secret_service.py]:SecretService`):**
  * Metodi `_resolve_scoped_secret` hakee avaimen PostgreSQL 19 `tenant_secrets`-taulusta `entity_adapter`- tai `uow_factory`-portin kautta järjestyksessä: 1) pyytävän organisaation `organization_id`, 2) järjestelmäorganisaatio `ROOT_SYSTEM` (`SystemOrganizations`). Jos avainta ei löydy kummaltakaan tasolta, palvelu kirjaa strukturoidun `logger.error`-lokin ja kaatuu välittömästi (`Fail-Fast`) poikkeukseen `ConfigurationError` (`ErrorCodes.SECRET_RESOLUTION_FAILED`). Kaikki `.env`-varapolut (`_resolve_platform_llm_secret`, `_resolve_platform_mcp_secret` ja `auth_env_var`) on poistettu pysyvästi.
  * Avaimet salataan `ENVELOPE_KMS`-tilassa (AES-256-GCM DEK + Cloud KMS KEK `kek_version`-tuella) tai tallennetaan `CLOUD_SECRET_MANAGER`-viitteinä (`SecretStorageMode`), ja poistetaan fyysisesti tietokannasta kutsulla `delete_collection_document("tenant_secrets", secret_id)`.
* **Kanoninen kohdevalinta ja monirivisten JSON-avainten tuki UI:ssa (`@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`):**
  * Kohdevalinta tapahtuu tyyppiturvallisella `DropdownButtonFormField<String>`-valitsimella (`org_secret_target_dropdown`), joka sitoo `MCP_GATEWAY`-laajuudessa kanonisen `McpGateway.id`-tunnisteen (`sys_<hex32>`, näyttäen ihmiselle luettavan nimen `Tavily MCP Gateway`) ja `LLM_PROVIDER`-laajuudessa `LLMProvider`-enum-arvon (hyläten epäkanoniset `slug`-merkkijonot virheellä `ErrorCodes.VALIDATION_FAILED`).
  * Salaisuuskenttä tukee sekä yksirivisiä API-avaimia että monirivisiä Google Cloud Vertex AI Service Account JSON -valtakirjoja (`org_secret_visibility_toggle_btn`).
* **Ajonaikainen `organization_id`- ja `ResolvedCredentialDTO`-injektio läpi koko suoritusputken:**
  * `ExecutionIngressService._persist_and_enqueue_execution` (`@[backend_v2/services/execution/ingress_service.py]`) tallentaa `GlobalContextVarsDTO(organization_id=initiator.organization_id, initiator_id=initiator.id, target_locale=payload.target_locale, profile_id=resolved_profile_id)` suorituksen metadataan.
  * `LLMClient.from_tier` (`@[backend_v2/llm/client.py]`) ratkaisee organisaatiokohtaisen avaimen `SecretService.resolve_llm_key`-kutsulla ja välittää `ResolvedCredentialDTO`-olion (`pydantic.SecretStr`) sekä `organization_id`-tunnisteen `LLMFactory.create_provider`-, `LiteLLMProvider`-, `VertexAIAdapter`- (`_parse_service_account_json`, `vertex_credentials`, `vertex_project`, `vertex_location`), `AIStudioAdapter`- ja `LLMCachingService`-komponenteille (jotka eristävät Redis-välimuistiavaimet organisaatiokohtaisesti muodossa `{model}:{org_scope}_{ttl}_...`) sekä `ToolDispatcher`- ja `GenericMCPClient`-työkalukutsuille ilman globaalia `os.environ`-mutaatiota tai lokivuotoja (`QGR033`).

### 3.4 B2B Kutsut, Normalisoitu Task Brief CRUD+Clone, 4-Tason RBAC ja Suora Tehtäväportaali (`EPIC 160` Vaiheet 5 & 6 + `Askel 4.6`)
* **Kryptografiset B2B-kutsut & Kanoninen Resend EU REST -lähetin (`@[backend_v2/services/auth/email_service.py]` & `@[backend_v2/services/auth/organization_service.py]`):** Yksittäis- ja eräkutsut (`InvitationBatchCreateDTO`) 256-bittisellä kertakäyttöisellä URL-tokenilla (`SHA-256` `token_hash` tietokannassa), 4-tason RBAC-hallintamatriisilla (`VIEWER`/`MEMBER`, `MANAGER`, `ADMIN`, `ROOT`) ja soft-delete-tietoisella `LAST_ADMIN_PROTECTION`-suojalla. `EmailService._send_single_http_item` muodostaa tarkan Resend EU REST -rungon (`from`, `to`, `subject`, `html`, `tags` ilman ei-tuettuja juurikenttiä) ja `EmailService._compose_transactional_html` upottaa `html.escape(raw_url, quote=True)`-suojatun `"Open Quorum Portal"` CTA-painikkeen sekä kopioitavan varalinkin samalla kun `_redact_action_url` ja `mask_email_address` suojaavat lokit raakatokeneilta ja vastaanottajaosoitteilta (`QGR033`).
* **Normalisoitu `TaskBrief` (`PromptBlockCategory.TASK_DEFINITION`) `CRUD + Clone` & Ensiluokkainen Vierasavain (`@[backend_v2/services/studio/prompt_block_service.py]`, `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` & `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`):** Uudelleenkäytettävät tehtävänannot / tapauskuvaukset tallennetaan `prompt_blocks`-tauluun (`PromptBlockCategory.TASK_DEFINITION`) ja kytketään tehtävänantoihin ensiluokkaisella vierasavaimella `execution_assignments.task_brief_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL` (`ZORM004`/`ZORM006`/`ZORM007`) saastuttamatta `locked_inputs.dynamic_inputs`-kenttiä tai `SmartIngressResolver`-paikkatunnistusta. `TaskAssignmentBriefDTO` $\leftrightarrow$ `TaskAssignmentBriefDto` ylläpitää 1:1 lankapariteettia (`92 / 92` jaettua DTO-paria), `_TaskBriefsManagementCard` tarjoaa `ADMIN`- ja `ROOT`-käyttäjille täyden 5-operaation `CRUD + Clone` -hallinnan (estäen asiakasorganisaation `ADMIN`-roolia muokkaamasta tai poistamasta `ROOT_SYSTEM`-lohkoja, mutta sallien kloonauksen), ja julkinen `TaskAssignmentConfigDialog` mahdollistaa tehtävänantojen luonnin ja kohortti-CSV-viennin suoraan sekä IAM-asetuksista että suoritusnäkymästä.
* **Suora tehtäväportaali, Autenttinen Firebase + TOTP 2FA JIT -onboarding & Välitön Tiedostopurku (`@[backend_v2/services/execution/assignment_service.py]`, `@[client_app_v2/lib/features/auth/data/auth_repository.dart]` & `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`):** SafeLinks-immuuni `GET .../preview`, autenttinen `AuthRepository.authenticateForTaskOnboarding` (yhteensopiva Firebase Email Enumeration Protectionin `'invalid-credential'`-vastauksen kanssa), esivaiheen `email_verified=True`-päivitys (`_verify_onboarding_firebase_token` varmistaa ensin `IDENTITY_MISMATCH`-ehdon ja päivittää `fb_auth.update_user(..., email_verified=True)` ennen `_enforce_firebase_mfa_claim`-tarkistusta, mahdollistaen portaalin sisäisen `MFA_REQUIRED` TOTP-aktivoinnin `task_portal_totp_secret_text`), tyypitetty `task_portal_task_brief_card`, välitön `Base64Attachment`-tiedostolatausten purku (`_normalize_assignee_ingress_inputs` `DocumentExtractionService`-palvelulla sekä `PUT .../draft`- että `POST .../submit`-reiteillä, `base64_amnesia_protocol`), eksplisiittinen `POST .../activate`, kaksikelloinen vanhentuminen (`access_expires_at` & `duration_minutes`) ja kertakäyttöinen `POST .../submit` (`AssignmentResultVisibility`).

---

## Luku 4: Firebase Storage ja Direct-to-Cloud Signed URLs

Raskaat binäärit (PDF-raportit, syötetiedostot) eivät saa koskaan kulkea Python-backendin RAM-muistin läpi.

### 4.1 Latausputki (Upload Flow)
1. **Pyyntö:** Frontend pyytää API:lta latauslupaa: `POST /api/v2/files/upload-request` (tiedoston nimi, koko, MIME-tyyppi).
2. **Rekisteröinti:** Backend luo tietokantaan `file_metadata`-rivin tilaan `pending`.
3. **Signed URL:** Backend luo Firebase Admin SDK:lla aikarajatun (15 min) PUT-osoitteen, johon sidotaan sallittu tiedostokoko ja MIME-tyyppi.
4. **Suoralataus:** Frontend lähettää binäärin suoraan Firebase Storageen.
5. **Vahvistus:** Frontend kutsuu `POST /api/v2/files/{id}/confirm`, jolloin backend varmistaa tiedoston olemassaolon pilvessä ja asettaa tilaksi `uploaded`.

### 4.2 Orpotiedostojen siivous (Orphan Cleanup CronJob)
Jos asiakkaan yhteys katkeaa kesken latauksen, pilveen ei jätetä roskatiedostoja:
* Arq-worker ajaa kerran vuorokaudessa taustatyön, joka etsii yli 24h vanhat `pending`-tilaiset tietokantarivit.
* Taustatyö tuhoaa tiedoston Storagesta ja poistaa metadatarivin tietokannasta.

### 4.3 GDPR-poistoketju (Split-Brain -suojaus)
Käyttäjätilin poistuessa suoritetaan tiukka poistojärjestys:
1. Poistetaan käyttäjän tiedostot Firebase Storagesta.
2. Poistetaan käyttäjätili Firebase Authista.
3. Merkitään PostgreSQL-tietokannassa `deleted_at = NOW()`, `is_active = FALSE` ja anonymisoidaan sähköposti (`deleted_usr_...@anonymized.quorum.local`), säilyttäen analyysien suoritushistoria eheänä.

---

## Luku 5: Idempotentti Seeding ja Skeemanhallinta

Tietokannan alustus ja peruskonfiguraatio hoidetaan deterministisesti `PrefixedUUID7`-avaimilla:
* **DDL-migraatio:** `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` luo kaikki 15 taulua idempotentisti (`CREATE TABLE IF NOT EXISTS`) natiiveilla `UUID PRIMARY KEY DEFAULT uuidv7()` -avaimilla.
* **Seed Vaultin sanitointi (`@[scripts/sanitize_seed_vault.py]`):** Varmistaa, että jokainen `@[backend_v2/seed/seed_data.json]`-tiedostoon lisätty uusi rivi, matriisiatomi tai konfiguraatio saa kanonisen 32-merkkisen `UUIDv7`-tunnisteen (`generate_uuid7_opaque_id()`) ennen tietokantaan latausta.
* **Seeding-skripti (`@[backend_v2/seed/run_seed.py]`):**
  * Lukee ja validoi `@[backend_v2/seed/seed_data.json]`-perustiedot `ValidatedSeedBufferDTO`-puskurin läpi (järjestelmäorganisaatio `ROOT_SYSTEM` = `"org_0195f3a0000070008000000000000001"` luokassa `SystemOrganizations`, oletustyönkulut, prompt-lohkot, matriisit ja tulosprofiilit).
  * Suorittaa atomisen `INSERT ... ON CONFLICT (id) DO UPDATE` -upsertin PostgreSQL 19 -kantaan `PostgresEntityAdapter`:in kautta, säilyttäen vakaat viiteavaimet CI/CD- ja kehitysajoissa.

---

## Luku 6: Toteutustiekartta ja Riippuvuudet (The Master Waves)

Toteutus etenee vaiheittain ja matalariskisesti. Kaikki tekninen tekeminen kytkeytyy suoraan virallisiin Epiceihin, hyväksyttyihin toteutussuunnitelmiin sekä dokumentin `@[docs/arkkitehtuurin_parannuskohteet.md]` korjauksiin:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1A. LLM Strategy Monolithin purku [SUORITETTU & LUKITTU - EPIC 157]    │
│     llm.py (1 090 LOC) -> llm_strategy/ (4 erillistä vaihetta)         │
│     Plan: docs/epic/tasks_llm/ | Tracker: llm_decomposition_tracker.md │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 1B. LLM Provider -purku [SUORITETTU & LUKITTU - Vaihe 1B]              │
│     provider.py (1 846 LOC) -> backend_v2/llm/provider/ (7 moduulia)   │
│     Plan: docs/epic/tasks_provider/ | Tracker: provider_decomposition  │
│     Lukittu AST-säännöllä QGR017 (52 testiä, 99 % kattavuus)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ [VARMISTETTU] E2E-tuotantoajojen toimivuus todennettu ennen PG-vaihetta│
│ Suoritus: exe_2af2f7665e7c477b (wf_a8f1d71000000001, rep_210bacba)     │
│ Vaiheet 1-3 + WeasyPrint 9s PDF + Flutter SDUI läpäisty 100 % puhtaasti│
│ Forensic Summary: data/files/executions/exe_2af2f7665e7c477b/          │
│ Git Commit: 3f3f3d941 (docs(architecture): record verified e2e...)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. PostgreSQL 19 Zero-ORM, Cutover, Karkaisuaallot & UUIDv7 Unification│
│    2A. PostgreSQL 19 Perusta [SUORITETTU & AUDITOITU - commit 4e56873c4]│
│    2B. PostgreSQL 19 Cutover [SUORITETTU & LUKITTU - TinyDB poistettu] │
│    2B-1. Järjestelmällinen Ennaltaehkäisy & QGR030 [18/18 karkaistu]   │
│    2B-2. dag_executor.py (1 803 LOC) purku [SUORITETTU & QGR017-LUKITTU]│
│    2C-1. Karkaisuaalto 1 (36 tiedostoa) [SUORITETTU & LUKITTU 36/36]   │
│    2C-2. Karkaisuaalto 2 (36 tiedostoa) [SUORITETTU & LUKITTU 36/36]   │
│    2C-3. Karkaisuaalto 3 (27 tiedostoa) [SUORITETTU & LUKITTU 27/27]   │
│    2C-4. Karkaisuaalto 4 (34 tiedostoa) [SUORITETTU & LUKITTU 34/34]   │
│    [VARMISTETTU] E2E-ajo Karkaisuaaltojen 1-4 jälkeen & ennen 2E:tä:   │
│        exe_01a188e876717069b74a7b3716a02489 (rep_01a188ec1f0a7037...)  │
│        DAG + Synteesi + 8s PDF + Flutter SDUI 100 % PASSED (d12ada5d1) │
│    2E. Malli A: 32-hex PrefixedUUID7, 12 taulun UUIDv7 & UUIDv4-poisto │
│        [SUORITETTU & LUKITTU: 15/15 + 31/31 kohdetta, QGR030 & DGR008] │
│    2F. AST & Laatuportit QGR031, scripts/*.py & QGR032 [SUORITETTU]    │
│        (Askel 3.4: QGR020, QGR031-033, cache, 3/3 karkaistu & lukittu) │
│    2F-2. Router SSOT Consolidation & CRUD+Clone Guard [SUORITETTU]     │
│        (IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md)              │
│    [VARMISTETTU] E2E-ajo Askeleiden 3.3, 3.4 & 3.4b jälkeen (f1a6818a8)│
│        exe_01a18ecef54372d39c31ef9fb1f12937 (rep_01a18ed15c5a7322...)  │
│        32-hex UUIDv7 DAG + Synteesi + 8s PDF + Flutter SDUI 100% PASS  │
│    2F-3. Topologinen Synteesikoheesio & 5-Pilarin Tislaus (EPIC 161)   │
│        [SUORITETTU, KOVENNETTU 31/31, SYNKRONOITU & AUDITOITU - 83f11d369]│
│        (docs/epic/EPIC_161_tracker.md | docs/epic/tasks_EPIC_161/)     │
│    2G. PostgresEntityAdapter (2 515 LOC) God Code -purku (Askel 3.5)   │
│        [SUORITETTU, KOVENNETTU 9/9, QGR017-LUKITTU & AUDITOITU]        │
│        (docs/epic/entity_adapter_decomposition_tracker.md)             │
│    2H. Studio Target Sync, CognitiveTier SSOT & DAG OCC Resilience     │
│        (Askel 3.6 - EPIC 162) [SUORITETTU, KOVENNETTU 31/31 & AUDITOITU]│
│        (docs/epic/EPIC_162_tracker.md | docs/epic/tasks_EPIC_162/)     │
│    [VARMISTETTU] E2E-ajo Askeleen 3.6 (EPIC 162) jälkeen (9066bc8ab)   │
│        exe_01a19ad8c8807129955f7c2e90d12a52 (rep_01a19adc9f7b71c3...)  │
│        DAG + Synteesi + 9s WeasyPrint PDF + Flutter SDUI 100% PASS     │
│        (docs/epic/EPIC_162_studio_target_sync_cognitive_tier_...)      │
│    2I. Jäännöspoikkeusten, JsonValuen & Mock-UoW:n poisto (EPIC 163)   │
│        (Askel 3.7) [SUORITETTU, KOVENNETTU, SYNKRONOITU & AUDITOITU]   │
│        (QGR020/027/028, DGR005/013/014, Census F=0, EPIC_163_tracker)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 3. B2B SaaS IAM, BYOK DB Persistence & Runtime SSOT (Askeleet 4 & 4.1-4.6)│
│    3A. EPIC 160 Vaiheet 1-6 + Hardening 51/51 + Tier 7/8 [SUORITETTU]  │
│        Token Exchange (<0,1 ms), 2FA, Redis Kill-Switch, Task Portal   │
│    3B. BYOK PostgreSQL 19 Persistence, MCP Schema & Target UI (4.1-4.2)│
│        [SUORITETTU & KOVENNETTU: SecretService UoW + Target Dropdown]  │
│    3C. LLM BYOK Runtime Wiring & 100 % DB-Only Secret SSOT (4.3-4.4)   │
│        [SUORITETTU & KOVENNETTU 19/19: 0 .env fallback, Vertex JSON]   │
│    3D. JSONB Codec Unwrapping & 91-Model Execution Wire DTO Parity     │
│        [SUORITETTU & LUKITTU: pool.py from_json + audit_dto_parity.py] │
│    [VARMISTETTU] E2E-ajo 100 % DB-pohjaisella LLM & Tavily BYOK        │
│        -konstellaatiolla (b3980130d): exe_01a1c086576272b7a33c508d27277e94│
│        DAG (7/7) + 5-Pilarin Synteesi + 9s PDF + Flutter SDUI 100% PASS│
│    3E. Yhtenäinen Salaisuusseedaus, DB Logfire/Firebase & 0 Mock Login │
│        (Askel 4.5 - EPIC 164) [SUORITETTU, KOVENNETTU 17/17 & AUDITOITU]│
│    3F. Task Assignment, Task Brief CRUD+Clone & Direct Portal Hardening │
│        (Askel 4.6) [SUORITETTU, KOVENNETTU 14/14 & AUDITOITU: 92 DTOs]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 4. Storage Signed URLs & Full-Workspace Hardening (Askeleet 5 & 5.1-5.5)│
│    4A. Tiedostoajurit karkaistu (3/3: file/local/gcs_file_driver.py);  │
│        Direct-to-Cloud Signed URLs (>32 MB suoralatauslaajennus)       │
│        Plan: docs/implementationplans/IMPLEMENTATION_PLAN_Storage_...  │
│    4B. Frontend & Studio UI Karkaisuaallot F1-F4 (185/185) [SUORITETTU]│
│        Aalto F1 (41), Aalto F2 (44), Aalto F3 (47), Aalto F4 (53)      │
│    4C. Yöajot 1-4: Uusien laatuporttien (d44a5e77b) koko työtilan      │
│        SHA-256 uudelleenkarkaisu (auto_hardening_runner.py)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────────────┐
│ 5. GCP Tuotantopystytys, qrum.ai Domain, CI/CD & E2E Go-Live (Askeleet 6, 6.1 & 6.2)│
│    5A. Kooditason Cloud Run -valmius (settings.py, /health, run_worker.py, Docker)  │
│        [SUORITETTU, KOVENNETTU 5/5, SYNKRONOITU & AUDITOITU - fa10bdb44]            │
│    5B. Ohjattu GCP-pilviinmeno (provision_gcp_cloud.py: Cloud SQL PG19, Memorystore,│
│        Artifact Registry, Cloud Run API/Worker, Firebase Web Hosting & SAN SSL)     │
│    5C. Cloud Armor WAF, Least Privilege IAM & FinOps Circuit Breakers (Askel 6.1)   │
│    5D. Lopullinen Full-Stack E2E Go-Live -Todennusportti (Askel 6.2)                │
│    Epic: docs/epic/EPIC_74_Production_Deployment_GCP.md                             │
│    Plan: docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md   │
│    Tracker: docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md            │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Luku 7: Monoliittien ja "God Code" -arkkitehtuurin Purkukartta (Master SSOT)

Jotta tuotantokoodi on testattavaa, helposti ylläpidettävää ja skaalautuvaa, Quorumin arkkitehtuurisäännöt (`@[ki_god_code_prevention.md]`) vaativat kaikkien historiallisten monoliittien purkamisen pieniin, yhden vastuun luokkiin ja palveluihin (Single Responsibility Principle & Hexagonal CQRS).

Koodikannassa on kartoitettu ja aikataulutettu kaikki 13 kriittistä monoliittialuetta. Jokaisella on oma virallinen eepoksensa tai toteutussuunnitelmansa, ja niiden purku on sidottu tarkasti oikeisiin aaltoihin:

| Monoliitti / God Code -alue | Alkuperäinen koko & riski | Purkutoimenpide & tavoitearkkitehtuuri | Virallinen Epic / Toteutussuunnitelma | Suoritusvaihe & Tila |
| :--- | :--- | :--- | :--- | :--- |
| **1. DAG Workflow Executor** | `backend_v2/services/orchestrator/dag_executor.py`<br>**1 803 LOC**. Raskas tilanhallinta, Kahnin aallot, TDA-fuusio ja askelsuoritus yhdessä tiedostossa. | Purettu 6 eristettyyn SRP-vaihemoduuliin paketissa `backend_v2/services/orchestrator/dag_executor/`: `causal_tda_fusion.py`, `execution_committer.py`, `node_executor.py`, `workflow_bootstrap_stage.py`, `step_execution_stage.py`, `wave_orchestrator_stage.py` ja 175 LOC fasaadi `__init__.py`. | **DAG Executor Decomposition**<br>`@[docs/epic/dag_executor_decomposition_tracker.md]`<br>`@[docs/epic/tasks_dag_executor/symbol_migration_map.md]` | **SUORITETTU & KOVENNETTU**<br>10/10 kohdetta karkaistu, 99.26 % kattavuus, lukittu AST-säännöllä `QGR017` |
| **2. LLM Provider Core & Engine** | `backend_v2/llm/provider.py`<br>**1 846 LOC**. Yhdisti semaforit, dynaamisen nopeusrajoituksen, LiteLLM-kutsut, hinnoittelun ja transienttien virheiden luokittelun. | Purettu 7 modulaariseen alitiedostoon paketissa `backend_v2/llm/provider/`: `env_and_schema_utils.py`, `transient_retry_policy.py`, `base_and_mock_provider.py`, `provider_factory.py`, `litellm_response_stage.py`, `litellm_provider.py` ja 93 LOC fasaadi `__init__.py`. Monoliitti poistettu ja lukittu AST-säännöllä `QGR017`. | **Provider Decomposition Plan**<br>`@[docs/epic/provider_decomposition_tracker.md]`<br>`@[docs/epic/tasks_provider/]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017`, 52 yksikkötestiä läpäisty (99 % kattavuus), 0 sanakirjarikkomusta, Tier 8 Red-Team auditoitu |
| **3. LLM Strategy & Orchestrator** | `backend_v2/services/orchestrator/strategies/llm.py`<br>**1 090 LOC**. Vastasi yhtä aikaa prompteista, skeemoista, työkaluista, LLM-kutsusta ja telemetriasta. | 4-vaiheinen Strangler Fig -pilkonta pakettiin `llm_strategy/`: `blueprint_and_metadata_stage`, `prompt_and_schema_stage`, `engine_retry_stage`, `trace_event_stage` ja fasaadi `__init__.py` (< 200 LOC). Monoliitti tuhotaan. | **EPIC 157**<br>`@[docs/epic/llm_decomposition_tracker.md]`<br>`@[docs/epic/tasks_llm/]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` (hashit `b9d66471a`, `3f04a6e2f`) |
| **4. Tietokantaydin & Tallennus** | `tinydb_driver.py`, `firestore_driver.py` ja `db_v2.json.lock`. Keräsivät sanakirjoja (`dict[str, Any]`), estivät rinnakkaisuuden ja lukitsivat levyn. | Korvattu puhtaalla Zero-ORM -arkkitehtuurilla: heksagonaaliset CQRS-portit (`GraphMutationPort`, `EntityPersistencePort`), `PostgresPoolManager` (`asyncpg`), binääriset `pydantic_core` Rust-koodekit ja AST-vartija `QGR030` (`FATAL`). TinyDB ja Firestore tuhottu kokonaan. | **PostgreSQL 19 Cutover & QGR030**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]`<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md]` | **SUORITETTU, KOVENNETTU & LUKITTU**<br>18/18 kohdetta karkaistu, Tier 7 synkronoitu, QGR030 aktiivisena |
| **5. Taustatyöntekijät (Workers)** | `backend_v2/worker.py`<br>**2 000+ LOC**. Sekoitti Arq-daemonin käynnistyksen, raskaat DAG-analyysit ja raporttien generoinnin yhteen sekamelskaan. | Pilkottu kolmeen: `worker.py` on pelkkä ohut daemon-käynnistys; raskas laskenta on `backend_v2/workers/execution_worker.py` ja raporttien renderöinti `backend_v2/workers/report_worker.py`. | **Worker Decoupling Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Tripartite_Pipeline_Isolation_and_Worker_Decoupling.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` + Aalto 1 (6/6 workeria karkaistu) |
| **6. Raportointipalvelu** | `backend_v2/services/report_service.py`<br>**749 LOC**. Käsitteli raporttien elinkaarta, Markdown/PDF-kasausta ja tiedostolukua. | Purettu pakettiin `backend_v2/services/report/`: `lifecycle_service.py`, `compilation_service.py`, `format_reader_service.py`. | **Report Service Decomposition**<br>`@[docs/epic/report_service_decomposition_tracker.md]` | **SUORITETTU & LUKITTU**<br>Vanha tiedosto poistettu |
| **7. Raporttiviennin Flattenerit** | `backend_v2/services/export_service.py` (**1 123 LOC**) & poistettu `[DELETE]` legacy-flattener. Keräsivät sanakirjamutaatioita ja konvertoivat graafeja löyhästi yhden rivin konevektoreiksi. | Monoliittinen flattener tuhottu; korvattu tyypitetyillä Pydantic V2 DTO-virroilla (`ExportMatrixSummaryRowDTO`, `ExportForensicAtomDTO`, `ExportPayloadDTO`) ja modulaarisella `backend_v2/services/export/` -paketilla. | **Export Tables SSOT Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md]` | **SUORITETTU & LUKITTU**<br>`ki_god_code_prevention.md` |
| **8. Matriisidomainin Jäsennin** | `backend_v2/services/matrix_domain_parser.py`<br>**732 LOC**. Sekoitti asteikot, atomien jäsennyksen, jakaumamuotoilun ja rivien rakentamisen. | Purettu pakettiin `backend_v2/services/matrix_parser/`: `scale_and_atom_stage.py`, `row_builder_stage.py`, `distribution_formatter.py`. | **Matrix Parser Decomposition**<br>`@[docs/epic/matrix_domain_parser_decomposition_tracker.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` |
| **9. Sitaattien Lexical Verifier** | `backend_v2/services/orchestrator/anchor_validation_service.py`<br>**855 LOC**. Hoiti yhtä aikaa tekstin normalisoinnin, fuzzy-tarkistuksen, morfologian ja tilasiirtymät. | Pilkottu modulaariseksi paketiksi `backend_v2/services/orchestrator/anchor_validation/`: `lexical_normalizer.py`, `lexical_matcher.py`, `evidence_validator.py`, `atom_evaluation_processor.py`. | **Anchor Validation Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` |
| **10. Keskustelun PDF-ingressi** | `backend_v2/services/ingress/pdf_chat_extractor.py`<br>**682 LOC**. Sekoitti Skia-vektoripiirron, taulukoiden rekonstruoinnin ja puheenvuorojen segmentoinnin. | Pilkottu 3-vaiheiseksi liukuhihnaksi `backend_v2/services/ingress/pdf_extractor/`: `bubble_geometry.py`, `table_and_card_stage.py`, `turn_assembly_stage.py` ja fasaadiksi `pdf_extractor/__init__.py`. | **Chat Ingress SSOT**<br>`@[ki_chat_ingress_and_provenance_architecture.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` |
| **11. SDUI UI-Mäppääjä** | `backend_v2/services/sdui_mapper_service.py` (juurimonoliitti). Yhdisti laskentalogiikan ja Dumb Painter -renderöinnin. | Juurimonoliitti tuhottu ja siirretty kanoniseen paikkaan `backend_v2/services/sdui/sdui_mapper_service.py` + 14 adapteria. | **SDUI Dumb Painter Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md]` | **SUORITETTU & LUKITTU**<br>Karkaistu Aallossa 1 (15/15 SDUI-tiedostoa) |
| **12. Dynaaminen MCP & Työkalukutsu** | `backend_v2/services/mcp/mcp_tool_loop.py` (**651 LOC**) ja Flutterin `StepBuilderView` (lomakemonoliitti). Kovakoodatut työkalut ja kytkökset. | Staattiset työkalut poistettu; korvattu protokolla-agnostisella `GenericMCPClient`:llä, `SchemaFactory`:lla ja JIT-syntetisoijalla. Flutterissa eristetty `McpToolParamsPanel`. | **EPIC 159 (Dynamic MCP)**<br>`@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]`<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]` | **SUORITETTU & KOVENNETTU**<br>`GenericMCPClient` tuotannossa |
| **13. PostgreSQL Zero-ORM Entity Adapter** | `[DELETE] backend_v2/database/postgres/entity_adapter.py`<br>**2 515 LOC (`48` AST-symbolia)**. Kokosi yhteen kaikkien 10 entiteettitaulun (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`) natiivit SQL-lauseet, hidraatiot, CRUD-operaatiot ja eräseedauksen. | Purettu Two-Epoch Strangler Fig -mallilla 6 SRP-vaihemoduuliin paketissa `@[backend_v2/database/postgres/entity_adapter/]`: `coercion_and_constants.py` (`255` LOC), `iam_and_system_stage.py` (`372` LOC), `prompt_block_and_step_stage.py` (`398` LOC), `workflow_and_profile_stage.py` (`405` LOC), `execution_and_report_stage.py` (`448` LOC), `seed_and_collection_stage.py` (`359` LOC) sekä `242` LOC koordinaattorifasaadi `__init__.py` (`PostgresEntityAdapter`). Monoliitti poistettu ja lukittu AST-säännöllä `QGR017`. | **Entity Adapter Decomposition Plan (Askel 3.5)**<br>`@[docs/epic/entity_adapter_decomposition_tracker.md]`<br>`@[docs/epic/tasks_entity_adapter/]` | **SUORITETTU, KOVENNETTU & LUKITTU**<br>9/9 kohdetta karkaistu, 100 % kattavuus (`730/730` lausetta), Tier 7 synkronoitu (`fb94d8dbe`), Tier 8 auditoitu (`a7a5ac6c7`), lukittu AST-säännöllä `QGR017` |

---

## Luku 8: Ihmisen Ohjauskeskus ja Työjärjestys (Human Executive Playbook)

> [!IMPORTANT]
> **Kaikki tekeminen tapahtuu suunnitelmien, seurantatiedostojen ja laatuporttien kautta**
> Kehittäjän tai tekoälyn ei tule koskaan ryhtyä kirjoittamaan suoraa koodia tai muuttamaan arkkitehtuuria ilman hyväksyttyä toteutussuunnitelmaa (`IMPLEMENTATION_PLAN_*.md`) ja seurantatiedostoa (`TRACKER_*.md`). Tämä takaa, että jokainen muutos testataan automaattisissa laatuporteissa (`universal_quality_gates`).

### 8.0 Suunnitelma- ja Tracker-tiedostojen Fyysinen Valmiusmatriisi Levyllä

Alla oleva taulukko näyttää yhdellä silmäyksellä, mitkä toteutussuunnitelmat ja seurantatiedostot ovat jo fyysisesti valmiina levyllä ja mitkä generoidaan kyseisen askeleen käynnistyskomennolla:

| Askel | Vaiheen sisältö | Fyysinen tila levyllä (`docs/implementationplans/` & `docs/epic/`) | Tarvittava esitoimenpide ennen ajoa |
| :--- | :--- | :--- | :--- |
| **Askel 1 – 3.2** | `llm_strategy/`, `llm/provider/`, E2E `exe_2af2f7665e7c477b`, PostgreSQL 19 Perusta & Cutover, `QGR030`, `dag_executor.py`-purku & **Karkaisuaalto 1 (36/36)** | 🟢 **100 % SUORITETTU & LUKITTU** | Valmis — ei toimenpiteitä. |
| **Askel 3.2b** | **Backend Karkaisuaalto 2** (`36/36` valmis: Core, Hooks, LLM Adapters & Services) | 🟢 **100 % SUORITETTU & LUKITTU:** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]` | Valmis — ei toimenpiteitä. |
| **Askel 3.2c** | **Backend Karkaisuaalto 3** (`27/27` valmis: Repositories, Orchestrator & Routers) | 🟢 **100 % SUORITETTU & LUKITTU:** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]` | Valmis — ei toimenpiteitä. |
| **Askel 3.2d** | **Backend Karkaisuaalto 4** (`34/34` valmis: Domain Models & DTO Schemas) | 🟢 **100 % SUORITETTU & LUKITTU:** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]` | Valmis — E2E-varmennusajo `exe_01a188e876717069b74a7b3716a02489` läpäisty (`d12ada5d1`). |
| **Askel 3.3** | **Malli A (`PrefixedUUID7` 12 taulussa + `seed_data.json` + `sanitize_seed_vault.py` + Legacy `UUIDv4`-poisto & `QGR030`/`DGR008`)** | 🟢 **100 % SUORITETTU, KOVENNETTU & LUKITTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]`, `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` (`15/15`), `@[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` & `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` (`31/31`) | Valmis — ei toimenpiteitä. |
| **Askel 3.4** | **AST- ja Laatuporttilaajennukset (`QGR020`, `QGR031`–`QGR033`, `scripts/*.py`) & `auto_hardening_runner.py` SHA-256 -välimuisti** | 🟢 **100 % SUORITETTU, KOVENNETTU & LUKITTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` & `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` | Valmis — toteutettu, karkaistu, KI- ja arkkitehtuurisynkronoitu sekä auditoitu (commit `df0518f8c`). |
| **Askel 3.4b** | **FastAPI Reitittimien SSOT-konsolidointi (`reports.py`, `workflows.py`, `system_configs.py`) & Universaali `CRUD + Clone` -lukitus** | 🟢 **100 % SUORITETTU, KOVENNETTU & LUKITTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]`, `@[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]` (`22/22` karkaistu) & `@[ki_router_ssot_and_crud_clone_lifecycle.md]` | Valmis — toteutettu, karkaistu (`16/16` Backend + `6/6` Frontend), KI- ja arkkitehtuurisynkronoitu, auditoitu (commitit `b62b65d47`, `ee38118ed`) sekä E2E-todennettu ajolla `exe_01a18ecef54372d39c31ef9fb1f12937` (GitHub-versio `f1a6818a8`, ``data/files/executions/exe_01a18ecef54372d39c31ef9fb1f12937/forensic_summary.md``). |
| **Askel 3.4c** | **Topologisen Älykkyyden Säilyttäminen Tislauksessa, Synteesissä & SDUI-raportoinnissa (`EPIC 161`: 5-Pilarin Nollahävikkinen Tislaus, Kontrastiivinen Ankkurointi, 3-Way Toulmin Falsifikaatio & SDUI/Jinja/Flutter-pariteetti)** | 🟢 **100 % SUORITETTU, KOVENNETTU, SYNKRONOITU, AUDITOITU & LUKITTU:** `@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]`, `@[docs/epic/EPIC_161_audit_report.md]`, `@[docs/epic/EPIC_161_tracker.md]` sekä `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_161/04_phase4_plan.md]` | Valmis — Vaiheet 1–4 & Live E2E (`8f838d834`), Backend Hardening (`31/31`), `/tier7-describe-architecture` (`81853a38e`) ja `/tier8-audit-epic` (`83f11d369`) suoritettu; 5 Frontend SDUI -tiedostoa delegoitu Karkaisuaaltoihin F1–F4. |
| **Askel 3.5** | **`PostgresEntityAdapter` (`[DELETE] entity_adapter.py`, 2 515 LOC) God Code -purku** (6 SRP-vaihemoduuliin + `242` LOC `__init__.py` fasaadi) | 🟢 **100 % SUORITETTU, KOVENNETTU (9/9), SYNKRONOITU (TIER 7), AUDITOITU (TIER 8) & QGR017-LUKITTU:** `@[docs/epic/entity_adapter_decomposition_tracker.md]` sekä `@[docs/epic/tasks_entity_adapter/phase1_leaf_constants_and_coercion_extraction.md]`–`@[docs/epic/tasks_entity_adapter/phase4_package_cutover_and_guardrails.md]` | Valmis — Vaiheet 1–4, Epoch 2 Backend Hardening (`9/9`, `100 %` kattavuus `730/730` lausetta), `/tier7-describe-architecture` (`fb94d8dbe`), `/tier8-audit-plan` (`a7a5ac6c7`) ja `QGR017`-lukitus suoritettu. |
| **Askel 3.6** | **Studio `OutputProfile` `target_blocks` -synkronointi, `CognitiveTier` SSOT & `LLMClient.from_strategy`-poisto sekä DAG Resilienssi, `ExecutionBudget`, `state_version` OCC & `input_merkle_hash` (`EPIC 162` — `@[docs/arkkitehtuurin_parannuskohteet.md]` Luvut 6, 7 & 8)** | 🟢 **100 % SUORITETTU, KOVENNETTU (31/31), SYNKRONOITU (TIER 7), AUDITOITU (TIER 8), E2E-TODENNETTU & LUKITTU:** `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]`, `@[docs/epic/EPIC_162_tracker.md]`, `@[docs/epic/EPIC_162_audit_report.md]` sekä `@[docs/epic/tasks_EPIC_162/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_162/04_phase4_plan.md]` | Valmis — Vaiheet 1–4, Tier 2 Hardening (`27/27` Backend + `4/4` Frontend = `31/31`), `/tier7-describe-architecture` (`9066bc8ab`), `/tier8-audit-epic` (`100 %` DoD) sekä E2E-varmennusajo `exe_01a19ad8c8807129955f7c2e90d12a52` (``data/files/executions/exe_01a19ad8c8807129955f7c2e90d12a52/forensic_summary.md``) suoritettu. |
| **Askel 3.7** | **Jäännöspoikkeuslistojen (`RESIDUAL_*`), `JsonValue` / Open-JSON -tyyppien ja Mock-UoW-testien poisto (`EPIC 163`: `QGR020` 20B/20C, `QGR027`, `QGR028`, `DGR005`, `DGR013`/`DGR014`, `Census F = 0`)** | 🟢 **100 % SUORITETTU, KOVENNETTU, SYNKRONOITU (TIER 7), AUDITOITU (TIER 8) & LUKITTU:** `@[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]`, `@[docs/epic/EPIC_163_tracker.md]`, `@[docs/epic/EPIC_163_audit_report.md]` sekä `@[docs/epic/tasks_EPIC_163/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_163/07_phase7_plan.md]` | Valmis — kaikki 7 vaihetta (`30aba5589`–`fbe6e1b33`), Tier 2 Hardening (`53/53`), `/tier7-describe-architecture` ja `/tier8-audit-epic` suoritettu. |
| **Askel 4** | **B2B SaaS IAM, 2FA, Token Exchange, Redis Kill-Switch, BYOK & Task Portal (`EPIC 160`)** (`37` backend + `14` frontend kohdetta = `51/51`) | 🟢 **100 % SUORITETTU, KOVENNETTU (51/51), SYNKRONOITU (TIER 7), AUDITOITU (TIER 8) & LUKITTU:** `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`, `@[docs/epic/EPIC_160_tracker.md]`, `@[docs/epic/EPIC_160_audit_report.md]` sekä `@[docs/epic/tasks_EPIC_160/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_160/06_phase6_plan.md]` | Valmis — Vaiheet 1–6, Tier 2 Hardening (`37/37` Backend + `14/14` Frontend = `51/51`), Tier 4 guardrailit (`ZORM007`, `DGR011`, `DGR012`), `/tier7-describe-architecture` (`3402d327b`) ja `/tier8-audit-epic` (`71b5247c6`) suoritettu. |
| **Askel 4.1** | **BYOK Salaisuuksien PostgreSQL 19 -pysyvyys (`UnitOfWorkFactory`), `system_configs.name` NOT NULL & Kanoninen Kohdevalikko (`org_secret_target_dropdown`)** | 🟢 **100 % SUORITETTU, KOVENNETTU (14/14) & LUKITTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md]` & `@[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]` | Valmis — `_local_secrets` poistettu, `uow_factory`-pysyvyys ja fyysinen poisto kytketty, `storage_mode` lisätty ja vapaa tekstikenttä korvattu kanonisella `DropdownButtonFormField<String>`-valitsimella (commitit `dc68c0aa2`–`c167b23d5`). |
| **Askel 4.2** | **MCP Draft 2020-12 Skeematuki, Kanoniset `id`-relaatiot (`slug`-hakukielto), Zero-Fallback AST Guardrailit & `system_configs` Fail-Fast -hidraatio** | 🟢 **100 % SUORITETTU, KOVENNETTU & LUKITTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]` & `@[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md]` | Valmis — 17-parametrinen Tavily-skeema, `anyOf`/`oneOf`-purku, `QGR016`/`QGR020`/`QGR030`/`QGR031`/`ZORM004`/`ZORM007`-laajennukset ja `hydrate_system_config_row` Fail-Fast toteutettu. |
| **Askel 4.3** | **LLM BYOK Ajonaikainen Kytkentä (`LLMClient.from_tier`, `ExecutionIngressService`, DAG-orkestraattori & Synteesityöntekijät)** | 🟢 **100 % SUORITETTU, KOVENNETTU & LUKITTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md]` & `@[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]` | Valmis — `SecretService.resolve_llm_key` ja `GlobalContextVarsDTO.organization_id` kytketty läpi Vaiheiden 1 ja 2 suoritusputken (commitit `c15bcdffa`–`fd433256b`). |
| **Askel 4.4** | **100 % DB-Only Secret SSOT (`0` `.env`-varapolkua), Vertex AI BYOK JSON + Express Mode, JSONB-koodekin purku & 91 DTO-parin lankapariteetti + E2E-todennus** | 🟢 **100 % SUORITETTU, KOVENNETTU (19/19), BUG-HUNTING-KORJATTU & E2E-TODENNETTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]` & `@[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]` | Valmis — `.env` LLM/MCP-varapolut poistettu, avaimet siirretty PostgreSQL 19 `tenant_secrets`-tauluun, JSONB-kaksoisserialisointi ja 91 DTO-parin pariteetti korjattu (`e0cc6cf79`–`b3980130d`), ja E2E-ajo `exe_01a1c086576272b7a33c508d27277e94` (`rep_01a1c08a762d70b8b3b7c2fae8fcf6da`) läpäisty 100 % tietokantapohjaisella LLM- ja Tavily-konstellaatiolla. |
| **Askel 4.5** | **Yhtenäinen Salaisuusseedaus (`.env.secrets.local`), `SecretScope.TELEMETRY`, Tietokantapohjainen Logfire & Firebase Admin -alustus sekä `service-account.json` & `MockLoginPanel` -poisto (`EPIC 164`)** | 🟢 **100 % SUORITETTU, KOVENNETTU (17/17), SYNKRONOITU (TIER 7), AUDITOITU (TIER 8) & LUKITTU:** `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, `@[docs/epic/EPIC_164_tracker.md]`, `@[docs/epic/EPIC_164_audit_report.md]` sekä `@[docs/epic/tasks_EPIC_164/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_164/04_phase4_plan.md]` | Valmis — Vaiheet 1–4 (`e31d46648`–`7df1c8daf`), Tier 2 Hardening (`11/11` Backend + `6/6` Frontend = `17/17`, commitit `011e39713`–`abc0328e1`), `/tier7-describe-architecture` ja `/tier8-audit-epic` (`80f1a3116`) suoritettu. |
| **Askel 4.6** | **Tehtävänantojen, `TaskBrief` (`PromptBlockCategory.TASK_DEFINITION`) `CRUD + Clone` -elinkaaren, Kanonisen Resend EU REST -lähettimen & Suoran Tehtäväportaalin (`/task/:token`) Päästä päähän -karkaisu (Findings A–E, `92/92` DTO-paria)** | 🟢 **100 % SUORITETTU, KOVENNETTU (14/14), SYNKRONOITU (TIER 7), AUDITOITU (TIER 8) & LUKITTU:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]` & `@[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]` | Valmis — Vaiheet 1–4 (`f50520284`, `e025b1e30`, `7bac2dc99`, `c21fca8d6`), Tier 2 Hardening (`9/9` Backend + `5/5` Frontend = `14/14`, commitit `a93056dea`–`08385c09b`), `/tier7-describe-architecture` ja `/tier8-audit-plan` suoritettu (`92/92` DTO-pariteetti, `1 387` läpäistyä Flutter-testiä). |
| **Askel 5** | **Firebase Storage Direct-to-Cloud Signed URLs** (Tiedostoajurit `file_driver.py`, `local_file_driver.py`, `gcs_file_driver.py` karkaistu `3/3`; Direct-to-Cloud PUT Signed URLs + `file_metadata` -taulu yli 32 MB suoralatauksille) | 🟢 Tiedostoajurit (`3/3`) karkaistu (`fa940a23f`–`85a7721ea`). 🟡 Direct-to-Cloud Signed URLs -arkkitehtuuri määritelty Luvussa 4 (valinnainen laajennus yli 32 MB suoralatauksille). | Jos tarvitaan yli 32 MB Direct-to-Cloud PUT Signed URL -latauksia, luo `IMPLEMENTATION_PLAN_Storage_Signed_URLs.md` ja `TRACKER_Storage_Signed_URLs.md` (`/tier0-create-plan` + `/tier1-plan-tracker-generator`). |
| **Askel 5.1 – 5.4** | **Frontend `client_app_v2/lib/` Karkaisuaallot F1–F4** (`41 + 44 + 47 + 53 = 185/185` `.dart`-tiedostoa + `14/14` IAM/Settings/Portal Askeleessa 4) | 🟢 **100 % SUORITETTU & LUKITTU:** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]` – `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]` & `@[docs/epic/EPIC_160_tracker.md]` | Valmis — kaikki 185 Karkaisuaaltojen F1–F4 tiedostoa sekä kaikki 14 `EPIC 160` Frontend-kohdetta karkaistu. |
| **Askel 5.5 (`Yöajot 1–4`)** | **Uusien Laatuporttien (`d44a5e77b`: Tenant RBAC, UoW Concurrency, Async Blocking & 1-Hop Parity) Täyden Työtilan SHA-256 Uudelleenkarkaisu (`auto_hardening_runner.py`)** | 🟡 **KÄYNNISSÄ (`data/hardening_cache.json`, `254` jäljellä):** Yöajo 1 (`191/201` välimuistissa, `10` jäljellä), Yöajo 2 (`72/190` välimuistissa, `118` jäljellä), Yöajo 3 (`114/201` välimuistissa, `87` jäljellä), Yöajo 4 (`--discover --gate all`, `39` jäljellä Yöajojen 1–3 jälkeen). | Suorita Yöajot 1–4 (ks. Askel 5.5 alla) tai aja suoraan ennen pilvikytkentää. |
| **Askel 6 (Koodivalmius)** | **Kooditason GCP Cloud Run -valmius (`settings.py`, `HealthCheckResponseDTO`, `GET /api/v2/system/health`, `run_worker.py` health probe & WeasyPrint `Dockerfile`)** | 🟢 **100 % SUORITETTU, KOVENNETTU (5/5), SYNKRONOITU (TIER 7) & AUDITOITU (TIER 8):** `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` & `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]` | Valmis — Vaiheet 1–4 (`15784637f`–`d732f4898`), Tier 2 Hardening (`5/5`), `/tier7-describe-architecture` (`0105e08d8`) ja `/tier8-audit-plan` (`fa10bdb44`) suoritettu. |
| **Askel 6.0b, 6.1 & 6.2** | **Ohjattu GCP-pilviinmeno (`TRACKER_GCP_Guided_Cloud_Cutover.md` & `[NEW] @[scripts/provision_gcp_cloud.py]`), `qrum.ai` SAN SSL, Resend EU (`HTTP_API`), Cloud Armor WAF, FinOps Circuit Breakers & E2E Go-Live** | 🟢 Suunnitelma `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]` ja tracker `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` ovat valmiina ja synkronoituna levyllä (Vaiheet 1–2 toteuttavat `[NEW] @[scripts/provision_gcp_cloud.py]`-orkestraattorin ja siivoavat `@[docker-compose.yml]`-tiedoston). | Aja `/tier2-execute --full-auto` tiedostolle `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`, suorita ohjattu GCP-pilviinmeno (`--stage all --check` / `--apply`) sekä Askeleet 6.1 ja 6.2. |

---

Alla on ihmiselle tarkoitettu selkeä, komentotasoinen etenemispolku askel askeleelta (mitä on jo tehty ja mitä tehdään seuraavaksi):

### Askel 1: Saata maaliin LLM Strategy -purku (Vaihe 1A) — [SUORITETTU & LUKITTU]
* **Tavoite:** Viimeistele `backend_v2/services/orchestrator/strategies/llm.py`:n poisto ja paketin `llm_strategy/__init__.py` käyttöönotto.
* **Seurantatiedosto:** `@[docs/epic/llm_decomposition_tracker.md]`
* **Tila:** 🟢 **100 % SUORITETTU & LUKITTU** (hash `b9d66471a`, Tier 2 Hardening `3f04a6e2f`). Monoliitti poistettu ja korvattu 199-rivisellä fasaadilla `llm_strategy/__init__.py`.
* **Laatuvarmennus:** 10/10 laatuporttia läpäisty (`58 passed, 99.53%` kattavuus).

---

### Askel 2: Suorita LLM Provider & Client Engine -purku (Vaihe 1B) — [SUORITETTU & LUKITTU]
* **Tavoite:** Pura `backend_v2/llm/provider.py` (1 846 LOC) modulaariseksi paketiksi `backend_v2/llm/provider/`, eristä fasaadi `__init__.py` (< 100 LOC), poista monoliitti ja lukitse se AST-säännöllä `QGR017`.
* **Seurantatiedosto:** `@[docs/epic/provider_decomposition_tracker.md]`
* **Tila:** 🟢 **100 % SUORITETTU, KOVENNETTU & AUDITOITU** (10/10 Epoch 2 -karkaisukohdetta läpäisty, Tier 7 As-Built dokumentaatiosynkronointi ja Tier 8 System 2 Red-Team Audit suoritettu). Monoliitti tuhottu ja korvattu 93-rivisellä fasaadilla `backend_v2/llm/provider/__init__.py`.
* **Laatuvarmennus:** 10/10 backend-laatuporttia läpäisty, 52 yksikkötestiä läpäisty (99 % testikattavuus), 0 sanakirjarikkomusta (`audit_dict_eradication.py`), 395/395 puhdasta tuontimoduulia (`audit_clean_imports.py`), `QGR017` aktiivisena.

---

### Välivaiheen Todentaminen: Päästä päähän (E2E) -suoritusajon Varmennus Ennen PostgreSQL-toteutusta — [SUORITETTU & VERIFIOITU]
> [!IMPORTANT]
> **Toimintakunnon peruskivi ennen tietokantavaihetta (PostgreSQL 19 Zero-ORM)**
> Ennen tietokantakerroksen ja `dag_executor.py`:n purkamista varmistettiin ja auditoitiin koko järjestelmän virheetön toimintakunto ajamalla täydellinen monivaiheinen tuotantoajo paikallisessa ajoympäristössä (`run_local.bat` + `/tier6-execution-monitor`).
> 
> * **Suoritus-ID:** `exe_2af2f7665e7c477b` (Työnkulku: `wf_a8f1d71000000001`, Raportti: `rep_210bacbab69246c4`)
> * **Ajankohta & Kesto:** 27.10.2026 klo 09:42:10 – 09:47:45 UTC+02:00 (5 min 35 s)
> * **Tila & Git Commit:** 🟢 **PASSED & FINALIZED (100 % E2E Pariteetti)** — Commit `3f3f3d941` (*docs(architecture): record verified e2e execution exe_2af2f7665e7c477b prior to postgresql*)
> * **Forensiikkaraportti:** `data/files/executions/exe_2af2f7665e7c477b/forensic_summary.md`

---

### Askel 3: PostgreSQL 19 Zero-ORM -perusinfrastruktuuri (Vaihe 2) — [SUORITETTU & LUKITTU]
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, KARKAISTU JA AUDITOITU** — Commit `4e56873c4`.
* **Saavutetut tulokset (REQ-001 – REQ-012):**
  1. PostgreSQL 19 DDL-skeema (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, 12 taulua, virtuaaliset aikaleimat, LZ4 TOAST).
  2. `PostgresPoolManager` (`asyncpg`), `PostgresEntityAdapter`, `PostgresGraphAdapter` ja `PostgresUnitOfWork` (repeatable read -eristys).
  3. Zero-ORM -arkkitehtuuri ja binääriset `pydantic_core` Rust-koodekit (`\x01`-etuliitteellä).
  4. Kaikki 12 kohdetiedostoa karkaistu, Tier 7 As-Built dokumentointi ja Tier 8 System 2 Red-Team Audit läpäisty 0 virheellä.
* **Toteutussuunnitelma & Seurantadokumentti:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`, `@[docs/implementationplans/TRACKER_PostgreSQL.md]`

---

### Askel 3.1: PostgreSQL 19 Lopullinen Cutover & TinyDB:n Poisto (Vaihe 2b) — [SUORITETTU & LUKITTU]
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, KOVENNETTU JA LUKITTU**
* **Saavutetut tulokset:**
  1. `tinydb_driver.py` ja vanhat tiedostokantariippuvuudet poistettu kokonaan koodipohjasta ja `@[pyproject.toml]`:sta.
  2. `run_local.bat` ja taustatyökalut siirretty pysyvästi `STORAGE_BACKEND=POSTGRES` -tilaan.
  3. Tietokantaseeding (`@[backend_v2/seed/run_seed.py]`) kytketty suoraan PostgreSQL 19:ään `ValidatedSeedBufferDTO`:n kautta.
* **Toteutussuunnitelma & Seurantadokumentti:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]`, `@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`

---

### Askel 3.1a: Järjestelmällinen Ennaltaehkäisy, AST-vartija QGR030 & Testitehtaat (Vaihe 2b-1) — [SUORITETTU & AUDITOITU]
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, 18/18 KOHDETTA KOVENNETTU JA AUDITOITU**
* **Saavutetut tulokset:**
  1. **Zero-Bifurcation Mandate & AST-vartija `QGR030` (`FATAL`):** Kieltää repo-laajuisesti kaikki viittaukset legacy-säilytysbackendeihin (`LOCAL`, `FIRESTORE`) ja pakottaa heksadesimaaliset Opaque Stripe ID:t.
  2. **Itsetarkistavat poikkeuslistat (Self-Verifying Exemption Lists):** AST-vartija validoi levyltä poikkeuslistojen (nimenomaan ja tyhjentävästi: `BOUNDARY_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_QGR028_FILES` ja `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`) olemassaolon.
  3. **Operatiiviset skriptit 1. luokan laatuportteihin:** `@[scripts/reconcile_storage.py]`, `@[scripts/run_e2e_variance_test.py]` ja `@[scripts/audit_zero_orm_strictness.py]` liitetty viralliseen `@[scripts/backend_audit_loop.py]` -ajoon.
  4. **Polyfactory-mallitehtaat (`@[backend_v2/tests/factories/model_factories.py]`):** Kaikki domain-entiteetit generoivat 100 % skeemavalideja Pydantic V2 -malleja ilman kovakoodattuja sanakirjamockeja.
* **Toteutussuunnitelma & Seurantadokumentti:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md]`, `@[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`

---

### Askel 3.1b: `dag_executor.py` God Code -purku modulaariseksi paketiksi (Vaihe 2b-2) — [SUORITETTU & KOVENNETTU]
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, 10/10 KOHDETTA KOVENNETTU, 10/10 LAATUPORTTIA JA AST-VARTIJA QGR017 LÄPÄISTY**
* **Saavutetut tulokset:**
  1. **Monoliitin täydellinen eliminointi:** 1 803 rivin monoliitti `dag_executor.py` on poistettu kokonaan levyltä ja korvattu eristetyllä SRP-alipaketilla `backend_v2/services/orchestrator/dag_executor/` (`causal_tda_fusion.py`, `execution_committer.py`, `node_executor.py`, `workflow_bootstrap_stage.py`, `step_execution_stage.py`, `wave_orchestrator_stage.py` ja 175 LOC `__init__.py` fasaadi).
  2. **AST Guardrail QGR017 (`FATAL`) -lukitus:** `@[scripts/_ast_guardrails.py]` estää pysyvästi monoliittisen `dag_executor.py` -tiedoston luomisen uudelleen.
* **Toteutussuunnitelmat & Seurantadokumentti:** `@[docs/epic/tasks_dag_executor/symbol_migration_map.md]`, `@[docs/epic/dag_executor_decomposition_tracker.md]`

---

### Askel 3.2: Karkaisuaalto 1 — Workers, SDUI & Utilities (Vaihe 2c-1) — [SUORITETTU & LUKITTU 36/36]
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, 36/36 TIEDOSTOA KARKAISTU JA LUKITTU** — Commit `63d2d37c5` (*chore(hardening): complete backend_v2/services/orchestrator/localization_compiler.py*).
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]`
* **Kokonaislaajuus:** Kaikki 36 tiedostoa karkaistu ja testattu 10/10 laatuportin läpi:
  * **Paketti 1 — Asynkroniset Taustatyöntekijät (`backend_v2/workers/`, 6/6 valmis):**
    1. `[x]` `@[backend_v2/workers/execution_worker.py]`
    2. `[x]` `@[backend_v2/workers/report_worker.py]`
    3. `[x]` `@[backend_v2/workers/synthesis_reducers.py]`
    4. `[x]` `@[backend_v2/workers/synthesis_tasks.py]`
    5. `[x]` `@[backend_v2/workers/synthesis_worker.py]`
    6. `[x]` `@[backend_v2/workers/variance_synthesis.py]`
  * **Paketti 2 — SDUI-adapterit & Vientimuuntimet (`backend_v2/services/sdui/`, 15/15 valmis):**
    1. `[x]` `@[backend_v2/services/sdui/sdui_mapper_service.py]`
    2. `[x]` `@[backend_v2/services/sdui/adapters/base_adapter.py]`
    3. `[x]` `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`
    4. `[x]` `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`
    5. `[x]` `@[backend_v2/services/sdui/adapters/global_score_adapter.py]`
    6. `[x]` `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]`
    7. `[x]` `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`
    8. `[x]` `@[backend_v2/services/sdui/adapters/mcp_audit_adapter.py]`
    9. `[x]` `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`
    10. `[x]` `@[backend_v2/services/sdui/adapters/penalties_adapter.py]`
    11. `[x]` `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
    12. `[x]` `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]`
    13. `[x]` `@[backend_v2/services/sdui/adapters/variance_adapter.py]`
    14. `[x]` `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]`
    15. `[x]` `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`
  * **Paketti 3 — Utilities & Apupalvelut (`backend_v2/utils/` + `services/`, 15/15 valmis):**
    1. `[x]` `@[backend_v2/utils/math_utils.py]`
    2. `[x]` `@[backend_v2/utils/alias_engine.py]`
    3. `[x]` `@[backend_v2/utils/normalization.py]`
    4. `[x]` `@[backend_v2/utils/paths.py]`
    5. `[x]` `@[backend_v2/utils/pydantic_utils.py]`
    6. `[x]` `@[backend_v2/utils/ranked_round_robin.py]`
    7. `[x]` `@[backend_v2/utils/redis_patcher.py]`
    8. `[x]` `@[backend_v2/utils/static_charts.py]`
    9. `[x]` `@[backend_v2/utils/finops_trace_analyzer.py]`
    10. `[x]` `@[backend_v2/services/translation_service.py]`
    11. `[x]` `@[backend_v2/llm/caching_service.py]`
    12. `[x]` `@[backend_v2/services/llm_task_executor.py]`
    13. `[x]` `@[backend_v2/services/chat_normalizer.py]`
    14. `[x]` `@[backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py]`
    15. `[x]` `@[backend_v2/services/orchestrator/localization_compiler.py]`

---

### Askel 3.2b–3.2d: Koko `backend_v2/`-Koodikannan Karkaisuaallot 2–4 (Bottom-Up Hardening Roadmap — `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 1)

Koko `backend_v2/`-tuotantokoodikannan **403 `.py`-tiedoston** kattava AST-, docstring-, yksikkötesti- ja poikkeuslista-auditointi jakaa koodikannan kahdeksaan tarkkaan kategoriaan:
1. **`47` tiedostoa — Valmis:** Pakettien `__init__.py`-fasaadit (valvottu suoraan `@[scripts/audit_clean_imports.py]`-laatuportilla).
2. **`162` tiedostoa — Valmis:** Jo aiemmissa monoliittipuruissa ja cutover-trackereissa (`llm_strategy/`, `llm/provider/`, `dag_executor/`, `postgres/`, `QGR030`, `export/`, `report/`, `matrix_parser/`, `anchor_validation/`, `pdf_extractor/`) 100 % karkaistut tiedostot.
3. **`49` tiedostoa — Valmis:** Jo entuudestaan 100 % puhtaat tiedostot (`__all__` määritelty, 0 AST-rikkomusta, 0 puuttuvaa docstringiä, 0 `.get()`-kutsua).
4. **`36` tiedostoa — Aalto 1 (Askel 3.2 / Vaihe 2c-1) — [SUORITETTU 36/36]:** Workers (6), SDUI-adapterit (15) ja Utilities (15) (`@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]`).
5. **`36` tiedostoa — Aalto 2 (Askel 3.2b / Vaihe 2c-2) — [SUORITETTU 36/36]:** Core, Observability, Deterministic Hooks, LLM Provider Adapters & Studio/Execution Services (`@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`).
6. **`27` tiedostoa — Aalto 3 (Askel 3.2c / Vaihe 2c-3) — [SUORITETTU 27/27]:** Repositories (11), Orchestrator Services (6) ja non-IAM FastAPI Routers (10) (`@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`).
7. **`34` tiedostoa — Aalto 4 (Askel 3.2d / Vaihe 2c-4) — [SUORITETTU 34/34]:** Domain Models (23) ja DTO Schemas (11) (`@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`).
8. **`12` tiedostoa — Eristetyt tulevat arkkitehtuurivaiheet (Askeleet 4 & 5):** B2B SaaS IAM (`backend_v2/api/routers/iam/*`, `backend_v2/services/auth/*`, `backend_v2/models/auth.py` — 9 tiedostoa) ja Firebase Storage Signed URLs (`file_driver.py`, `local_file_driver.py`, `storage.py` — 3 tiedostoa), jotka kirjoitetaan uusiksi ja karkaistaan omissa toteutustrackereissaan.

> [!IMPORTANT]
> **Karkaisuaaltojen 1–4 valmiustila (133/133 tiedostoa karkaistu; 391 / 403 backend-tiedostoa = 97,0 % lukittu):**
> 1. **Kaikki 4 kohdennettua backend-karkaisuaaltoa on suoritettu 100 % puhtaasti:** Aallot 1 (`36/36`), 2 (`36/36`), 3 (`27/27`) ja 4 (`34/34`) sekä jokaisen aallon *Final Macro-Audit Completion Gate* on läpäisty. Jäljellä olevat 12 tiedostoa kuuluvat eristettyihin tuleviin arkkitehtuurivaiheisiin: Askel 4 (`EPIC 160` IAM, 9 tiedostoa) ja Askel 5 (Firebase Storage Signed URLs, 3 tiedostoa).
> 2. **Täydellinen regressio- ja tyyppiturvaverkko Askeleille 3.3–3.5 (100 % suoritettu ja lukittu):** Koska kaikilla taustatyöntekijöillä, SDUI-adaptereilla, palvelukerroksilla, repositorioilla, reitittimillä, domain-malleilla ja DTO-skeemoilla on eksplisiittiset `__all__`-määrittelyt, PEP 257 -dokumentaatio, `ConfigDict(extra="forbid", strict=True)` -sopimukset ja kattavat yksikkötestit, Askeleen 3.3 `PrefixedUUID7`-yhtenäistys (Malli A), Askeleen 3.4 AST-laajennukset (`QGR031`/`QGR032`), Askeleen 3.4b Router SSOT, Askeleen 3.4c `EPIC 161` ja Askeleen 3.5 `entity_adapter/`-purku (`9/9` karkaistu, `QGR017`-lukittu) on ajettu läpi täydellisellä matemaattisella regressiosuojalla ennen Askeleen 4 (`EPIC 160` IAM) aloittamista.

---

### Askel 3.2b: Karkaisuaalto 2 — Core, Hooks, LLM Adapters & Studio/Execution Services (Vaihe 2c-2) — [SUORITETTU & LUKITTU 36/36]
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, 36/36 TIEDOSTOA KARKAISTU JA LUKITTU** — Commit `1f5da4a43` (*chore(hardening): audit and fix override_service.py*).

#### Paketti 1: Core, Observability & Shared Utilities (8/8 SUORITETTU)
1. `[x]` `@[backend_v2/context.py]`
2. `[x]` `backend_v2/core/rate_limit.py` (myöhemmin korvattu tiedostolla `@[backend_v2/core/redis_security.py]`)
3. `[x]` `@[backend_v2/core/template_processor.py]`
4. `[x]` `@[backend_v2/core/telemetry.py]`
5. `[x]` `@[backend_v2/utils/linguistics/stemmer.py]`
6. `[x]` `@[backend_v2/services/pii_analyzer.py]`
7. `[x]` `@[backend_v2/services/usage_service.py]`
8. `[x]` `@[backend_v2/services/progress.py]`

#### Paketti 2: Deterministic & Hybrid Pipeline Hooks + Scoring Base (10/10 SUORITETTU)
1. `[x]` `@[backend_v2/utils/scoring/base_engine.py]`
2. `[x]` `@[backend_v2/hooks/hydration.py]`
3. `[x]` `@[backend_v2/hooks/metadata.py]`
4. `[x]` `@[backend_v2/hooks/dlq_guard.py]`
5. `[x]` `@[backend_v2/hooks/context_mapper.py]`
6. `[x]` `@[backend_v2/hooks/references.py]`
7. `[x]` `@[backend_v2/hooks/interaction_hook.py]`
8. `[x]` `@[backend_v2/hooks/archival.py]`
9. `[x]` `@[backend_v2/hooks/metrics.py]`
10. `[x]` `@[backend_v2/hooks/input_processing.py]`

#### Paketti 3: LLM Provider Adapters & Prompt Utilities (8/8 SUORITETTU)
1. `[x]` `@[backend_v2/llm/directives.py]`
2. `[x]` `@[backend_v2/llm/prompt_builder.py]`
3. `[x]` `@[backend_v2/llm/adapters/deepseek_adapter.py]`
4. `[x]` `@[backend_v2/llm/adapters/mock_adapter.py]`
5. `[x]` `@[backend_v2/llm/adapters/adapter_factory.py]`
6. `[x]` `@[backend_v2/llm/adapters/anthropic_adapter.py]`
7. `[x]` `@[backend_v2/llm/adapters/openai_adapter.py]`
8. `[x]` `@[backend_v2/llm/adapters/ai_studio_adapter.py]`

#### Paketti 4: Studio, Ingress & Execution Services (10/10 SUORITETTU)
1. `[x]` `@[backend_v2/services/web_fetcher.py]`
2. `[x]` `@[backend_v2/services/ingress/multi_channel_ingress_service.py]`
3. `[x]` `@[backend_v2/services/source_verification_service.py]`
4. `[x]` `@[backend_v2/services/factories/output_profile_factory.py]`
5. `[x]` `@[backend_v2/services/studio/auth_validator.py]`
6. `[x]` `@[backend_v2/services/studio/prompt_block_service.py]`
7. `[x]` `@[backend_v2/services/studio/output_profile_service.py]`
8. `[x]` `@[backend_v2/services/execution/context_service.py]`
9. `[x]` `@[backend_v2/services/execution/resumption_service.py]`
10. `[x]` `@[backend_v2/services/execution/override_service.py]`

---

### Askel 3.2c: Karkaisuaalto 3 — Repositories, Orchestrator Services & FastAPI Routers (Vaihe 2c-3) — [SUORITETTU & LUKITTU 27/27]
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, 27/27 TIEDOSTOA KARKAISTU, MACRO-AUDIT COMPLETION GATE LÄPÄISTY JA LUKITTU** — Commit `248728871` (*refactor(hardening): tighten reports.py*).

#### Paketti 1: Repository & Persistence Layer (`backend_v2/database/`) (11/11 SUORITETTU)
1. `[x]` `@[backend_v2/database/repository.py]`
2. `[x]` `@[backend_v2/database/repositories/component.py]`
3. `[x]` `@[backend_v2/database/repositories/report_artifact.py]`
4. `[x]` `@[backend_v2/database/repositories/components/agent.py]`
5. `[x]` `@[backend_v2/database/repositories/components/execution_persona.py]`
6. `[x]` `@[backend_v2/database/repositories/components/extraction_protocol.py]`
7. `[x]` `@[backend_v2/database/repositories/components/matrix.py]`
8. `[x]` `@[backend_v2/database/repositories/components/output_profile.py]`
9. `[x]` `@[backend_v2/database/repositories/components/prompt_block.py]`
10. `[x]` `@[backend_v2/database/repositories/components/role.py]`
11. `[x]` `@[backend_v2/database/repositories/components/task_blueprint.py]`

#### Paketti 2: Orchestrator & Schema Services (`backend_v2/services/orchestrator/`) (6/6 SUORITETTU)
1. `[x]` `@[backend_v2/services/orchestrator/schema_factory.py]`
2. `[x]` `@[backend_v2/services/orchestrator/chunking_service.py]`
3. `[x]` `@[backend_v2/services/orchestrator/atomizer.py]`
4. `[x]` `@[backend_v2/services/orchestrator/dag_compiler.py]`
5. `[x]` `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`
6. `[x]` `@[backend_v2/services/orchestrator/enriched_dag_executor.py]`

#### Paketti 3: FastAPI Routers — System, Studio & Execution (`backend_v2/api/routers/`) (10/10 SUORITETTU)
1. `[x]` `@[backend_v2/api/routers/system/health.py]`
2. `[x]` `@[backend_v2/api/routers/system/telemetry.py]`
3. `[x]` `@[backend_v2/api/routers/system/configs.py]`
4. `[x]` `@[backend_v2/api/routers/output_profiles.py]`
5. `[x]` `@[backend_v2/api/routers/studio/model_registry.py]`
6. `[x]` `@[backend_v2/api/routers/studio/prompt_blocks.py]`
7. `[x]` `backend_v2/api/routers/studio/system_configs.py`
8. `[x]` `@[backend_v2/api/routers/studio/workflows.py]`
9. `[x]` `backend_v2/api/routers/execution/workflows.py`
10. `[x]` `@[backend_v2/api/routers/execution/reports.py]`

---

### Askel 3.2d: Karkaisuaalto 4 — Domain Models & DTO Schemas (Vaihe 2c-4) — [SUORITETTU & LUKITTU 34/34]
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, 34/34 TIEDOSTOA KARKAISTU, MACRO-AUDIT COMPLETION GATE LÄPÄISTY JA LUKITTU** — Commit `1af36b166` (*refactor(hardening): tighten workflow_schema.py*).

#### Paketti 1: Domain Models (`backend_v2/models/domain/`) (23/23 SUORITETTU)
1. `[x]` `@[backend_v2/models/domain/base.py]`
2. `[x]` `@[backend_v2/models/domain/metadata.py]`
3. `[x]` `@[backend_v2/models/domain/usage.py]`
4. `[x]` `@[backend_v2/models/domain/references.py]`
5. `[x]` `@[backend_v2/models/domain/retrieval.py]`
6. `[x]` `@[backend_v2/models/domain/hydration.py]`
7. `[x]` `@[backend_v2/models/domain/interaction.py]`
8. `[x]` `@[backend_v2/models/domain/integrity.py]`
9. `[x]` `@[backend_v2/models/domain/archivist.py]`
10. `[x]` `@[backend_v2/models/domain/causal.py]`
11. `[x]` `@[backend_v2/models/domain/coach.py]`
12. `[x]` `@[backend_v2/models/domain/evaluation.py]`
13. `[x]` `@[backend_v2/models/domain/falsifier.py]`
14. `[x]` `@[backend_v2/models/domain/judge.py]`
15. `[x]` `@[backend_v2/models/domain/knowledge.py]`
16. `[x]` `@[backend_v2/models/domain/logician.py]`
17. `[x]` `@[backend_v2/models/domain/overseer.py]`
18. `[x]` `@[backend_v2/models/domain/performativity.py]`
19. `[x]` `@[backend_v2/models/domain/profiler.py]`
20. `[x]` `@[backend_v2/models/domain/scoring.py]`
21. `[x]` `@[backend_v2/models/domain/source_verification.py]`
22. `[x]` `@[backend_v2/models/domain/synthesis.py]`
23. `[x]` `@[backend_v2/models/domain/workflow.py]`

#### Paketti 2: DTO Schemas & Prompt Models (`backend_v2/models/dtos/` + `models/prompt.py`) (11/11 SUORITETTU)
1. `[x]` `@[backend_v2/models/prompt.py]`
2. `[x]` `@[backend_v2/models/dtos/system.py]`
3. `[x]` `@[backend_v2/models/dtos/inputs.py]`
4. `[x]` `@[backend_v2/models/dtos/prompt.py]`
5. `[x]` `@[backend_v2/models/dtos/prompt_context.py]`
6. `[x]` `@[backend_v2/models/dtos/retrieval.py]`
7. `[x]` `@[backend_v2/models/dtos/evaluation_steps.py]`
8. `[x]` `@[backend_v2/models/dtos/schema_manifest.py]`
9. `[x]` `@[backend_v2/models/dtos/state.py]`
10. `[x]` `@[backend_v2/models/dtos/variance.py]`
11. `[x]` `@[backend_v2/models/dtos/workflow_schema.py]`

---

### Välivaiheen Todentaminen 2: Päästä päähän (E2E) -suoritusajon Varmennus Karkaisuaaltojen 1–4 Jälkeen ja Ennen Askeleen 3.3 `PrefixedUUID7`-cutoveria — [SUORITETTU & VERIFIOITU]
> [!IMPORTANT]
> **Toimintakunnon peruskivi Karkaisuaaltojen 1–4 (133/133 tiedostoa) jälkeen ja ennen `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]` -toteutusta**
> Ennen Askeleen 3.3 (Malli A: yhtenäinen 32-hex `PrefixedUUID7` kaikissa 12 PostgreSQL 19 -taulussa ja `@[backend_v2/seed/seed_data.json]` cutover) käynnistämistä varmistettiin ja auditoitiin koko karkaistun järjestelmän virheetön toimintakunto ajamalla täydellinen monivaiheinen tuotantoajo paikallisessa PostgreSQL 19 -ajoympäristössä (`/tier6-execution-monitor`).
>
> * **Suoritus-ID:** `exe_01a188e876717069b74a7b3716a02489` (Työnkulku: `wf_a8f1d71000000001`, Organisaatio: `org_system000000`, Käyttäjä: `usr_a3fd6b3d77c748f4`)
> * **Raportti-ID & Tulosprofiili:** `rep_01a188ec1f0a7037b9a6713071b72386` (Profiili: `prf_a8f1d71000000001`)
> * **Ajankohta & Kesto:** 29.10.2026 klo 20:25:05 – 20:30:22 UTC+02:00 (5 min 17 s)
> * **Tila & Git Commit:** 🟢 **PASSED & FINALIZED (100 % E2E Pariteetti, 0 virhettä, `healing_cost_events: 0`)** — Lähtötason commit `d12ada5d1` (*docs: add comprehensive production architecture implementation plan and implementation plans for AST guardrails and prefixed UUIDv7 cutover*)
> * **Forensiikkaraportti:** `data/files/executions/exe_01a188e876717069b74a7b3716a02489/forensic_summary.md`
> * **Todennettu ketju askel askeleelta:**
>   1. **Vaihe 1 (DAG Heavy LLM Execution — `PASSED` klo 20:28:54):** Kaikki DAG-askeleet (`sr_a8f1d71000000001` `MarkdownBlock`, `sr_a8f1d71000000002` Two-Pass Atomizer & Causal Discovery `LinkerResponseDTO`, 4 matriisiarviointiaskelta `sr_a8f1d71000000003`–`sr_a8f1d71000000006` sekä `sr_a8f1d71000000008` `SynthesisEngine`) suoritettiin 100 % puhtaasti (`Commensurate Base Average: 6.4, Final: 6.4, Penalties: 0`).
>   2. **Vaihe 2 (Asynkroninen tekstisynteesi & WeasyPrint PDF — `COMPLETED` klo 20:30:22):** `ExecutiveSummarySectionResult`, `XaiHighlightsResult`, `MatrixExplanationsResult`, `VarianceExplanationResult` (`variance=3.6675`, `verdict=MISALIGNED`) ja `MatrixSectionSynthesesResult` generoitiin ja 8-sivuinen PDF-raportti (`rep_01a188ec1f0a7037b9a6713071b72386`) koottiin virheettömästi.
>   3. **Vaihe 3 (Flutter Desktop SDUI & Rows -pariteetti):** Flutter-asiakasohjelma nouti ja renderöi raportin taulukkorivit (`GET /api/v2/reports/rep_01a188ec1f0a7037b9a6713071b72386/rows` `200 OK`) ja SDUI-näkymäpuun (`GET /api/v2/reports/rep_01a188ec1f0a7037b9a6713071b72386/sdui` `200 OK`) ilman yhtäkään deserialisointi- tai skeemavirhettä.

---

### Askel 3.3: Yhtenäinen `PrefixedUUID7`-arkkitehtuuri, Natiivi PostgreSQL 19 `UUIDv7` Kaikissa 12 Taulussa, Legacy `UUIDv4`-Poisto & `seed_data.json` Cutover (Vaihe 2e — `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 2) — [SUORITETTU, KOVENNETTU & LUKITTU]
* **Lähtötilanteen varmennus:** Ennen tämän askeleen aloitusta koko karkaistun järjestelmän (Karkaisuaallot 1–4, 133/133 tiedostoa) päästä päähän -toimivuus todennettiin tuotantoajolla `exe_01a188e876717069b74a7b3716a02489` / `rep_01a188ec1f0a7037b9a6713071b72386` (commit `d12ada5d1`, ks. yllä oleva *Välivaiheen Todentaminen 2*).
* **Toteutussuunnitelmat (Implementation Plans):**
  1. `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]`
  2. `@[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]`
* **Seurantadokumentit (SSOT Trackers):**
  1. `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` (Steps 1–5 valmiit, Tier 7 synkronoitu, Tier 8 auditoitu, `Tier 2 Hardening` `15/15` suoritettu ja lukittu)
  2. `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` (Steps 1–5 valmiit, Tier 7 synkronoitu, Tier 8 auditoitu, `Tier 2 Hardening` `31/31` suoritettu ja lukittu)
* **Tila:** 🟢 **100 % SUORITETTU, KOVENNETTU (`15/15` + `31/31` via `auto_hardening_runner.py`), SYNKRONOITU (TIER 7) & AUDITOITU (TIER 8)**
* **Miksi sijoitettu tähän kohtaan (heti Karkaisuaaltojen 2–4 jälkeen ja ENNEN Askelta 4 `EPIC 160` IAM):**
  `EPIC 160` (B2B SaaS IAM) perustuu siihen, että `organizations`- ja `users`-taulujen pääavaimet ovat natiiveja 16-tavuisia PostgreSQL 19 `UUIDv7`-arvoja (`usr_<hex32>` ja `org_<hex32>`). Toteuttamalla `@[docs/arkkitehtuurin_parannuskohteet.md]` Luvun 2 (**Malli A**) juuri ennen IAM-vaihetta poistettiin vanha kahtiajako (7 `TEXT`-taulua 16-heksalla vs. 5 `UUID`-taulua 32-heksalla) kerralla kaikista 12 taulusta sekä hävitettiin kaikki jäljellä olleet `uuid.uuid4()`- ja `Uuid().v4()`-generaattorit koko Python- ja Flutter-koodikannasta.
* **Toteutetut ja lukitut arkkitehtuurimuutokset (Malli A):**
  1. **PostgreSQL 19 DDL (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`):** Myös konfiguraatio- ja hallintataulut (nimenomaan ja tyhjentävästi: `organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows` ja `output_profiles`) käyttävät `id UUID PRIMARY KEY DEFAULT uuidv7()` -määrittelyä, `created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL` -saraketta ja `CHECK (uuid_extract_version(...) = 7)` -rajoitteita.
  2. **Zero-ORM Adapterisilta (`@[backend_v2/database/postgres/entity_adapter/]`):** Kaikki 12 taulua käyttävät symmetristä `parse_prefixed_uuid7()` / `format_prefixed_uuid7()` -muunnosta ilman taulukohtaisia poikkeuksia, varmennettuna `@[scripts/audit_zero_orm_strictness.py]`-laatuportilla.
  3. **Pydantic V2 `PrefixedUUID7` & `generate_uuid7()` SSOT (`@[backend_v2/models/core_base.py]`):** Lukittiin `OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`, reititettiin `generate_opaque_id(prefix)` suoraan `generate_uuid7_opaque_id(prefix)`-funktioon ja eriytettiin matalan tason `generate_uuid7()`-primitiivi.
  4. **`@[backend_v2/seed/seed_data.json]` 32-hex `UUIDv7` Cutover & `@[scripts/sanitize_seed_vault.py]` Automaatio:**
     * Kaikki `@[backend_v2/seed/seed_data.json]`-tiedoston ID-kentät ja sisäiset viitteet (`block_ids`, `step_id`, `workflow_id`, `output_profile_id`, `matrix_block_id`, `variance_target_block`, `matrix_synthesis_groups`, `sc_`-asteikot ja `wf_`-työnkulut) on konvertoitu deterministisiksi 32-merkkisiksi `UUIDv7`-tunnisteiksi (`{prefix}_{32_hex}`) ja paikallinen PostgreSQL 19 -kanta on siemennetty uudelleen.
     * `@[scripts/sanitize_seed_vault.py]`-työkalu generoi automaattisesti `generate_uuid7_opaque_id()`-funktiolla kanonisen 32-heksaisen `UUIDv7`-tunnisteen jokaiselle uudelle riville, asteikolle tai atomiväitteelle ilman tunnisteita ennen `@[backend_v2/seed/run_seed.py]`-ajoa.
  5. **Kovakoodattujen Oletus-ID-ankkureiden Poisto, Kausaalisen Koheesiomatriisin Sidonta ja `@[docs/tiede.md]`-graafimatematiikan 100 % Synkronointi:**
     * **Studio-luonnokset (`@[backend_v2/services/studio/workflow_service.py]` & `@[backend_v2/models/domain/workflow.py]`):** Korvattu `StudioWorkflowService.create_step_draft`- ja `create_workflow_draft`-metodien kovakoodatut oletus-ID:t dynaamisilla tietokantahauilla ja `None`-oletusarvoilla.
     * **Kausaalisen koheesion matriisi (`@[backend_v2/models/domain/step.py]`, `@[backend_v2/models/domain/workflow.py]`, `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` & `@[backend_v2/settings.py]`):** Kytketty BARS-koheesiomatriisi suoraan `StepType.CAUSAL_DISCOVERY`-stepin `criteria_block_ids`-kenttään ja poistettu vanhat kovakoodatut vakiot.
     * **`@[docs/tiede.md]`-graafimatematiikan 100 % Synkronointi (`r_LCC`, `r_conv`, $\kappa_{\text{steer}}$ ja `simulate_counterfactual_retraction`):** Toteutettu 0 LLM-tokenin topologiset graafimetriikat (`largest_component_ratio`, `branch_convergence_ratio`, `steering_coupling_ratio`), Kaavan (13) Guttman-kynnykset sekä Algoritmin 1 kontrafaktuaalinen haavoittuvuussimulaatio (`CounterfactualSimulationResultDTO` / `CounterfactualSimulationResultDto`) tiedostoihin `@[backend_v2/models/dtos/causal_discovery.py]`, `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`, `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]`, `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` ja `@[backend_v2/settings.py]`.
  6. **Legacy `UUIDv4`-generaattoreiden Täydellinen Poisto & Staattiset Vartijat (`QGR030` & `DGR008`):**
     * Hävitetty kaikki jäljellä olleet `uuid.uuid4()`- ja `Uuid().v4()`-kutsut sekä 8/16-heksan ID-katkaisut koko Python-backendistä ja Flutter-asiakassovelluksesta (`@[client_app_v2/lib/utils/json_converters.dart]:generateOpaqueUuid7` ja 32-hex `StrictOpaqueIdConverter`).
     * Lukittu pysyvillä staattisilla laatuporteilla `QGR030` (`@[scripts/_ast_guardrails.py]`) ja `DGR008` (`@[scripts/_dart_guardrails.py]`).

---

### Askel 3.4: AST- ja Laatuporttilaajennukset (`QGR020`, `QGR031`–`QGR033`), `scripts/*.py` Dynaaminen Skannaus & `auto_hardening_runner.py` SHA-256 -välimuisti (Vaihe 2f — `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 3) — [SUORITETTU, KOVENNETTU & LUKITTU]
* **Toteutussuunnitelma (Implementation Plan):** `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, KOVENNETTU & LUKITTU** — Commitit `034c56fd6` (toteutus), `df0518f8c` (Tier 7 & Tier 8 auditointi) ja `267312915` (Tier 2 karkaisu).
* **Tavoite:** Lukittiin Askeleen 3.2b–3.2d ja Askeleen 3.3 saavuttama arkkitehtuurinen puhtaus viidellä pysyvällä laatuportti- ja karkaisuautomaatiolaajennuksella (`@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 3):
  1. **AST-sääntö `QGR031` (`FilterOperator` & `QueryCondition` -kurinalaisuus):** Lisätään `@[scripts/_ast_guardrails.py]`-tiedostoon sääntö, joka valvoo kaikkia `Filter(...)`- ja `QueryCondition(...)`-kutsuja ja estää virheelliset operaattorit (`"="`, `"eq"`, `"LIKE"`), tyhjät kenttänimet sekä `"in"`-operaattorin merkkijonoliteraalit.
  2. **Dynaaminen `scripts/*.py` -skannaus laatuportissa:** Päivitetään `@[scripts/backend_audit_loop.py]` skannaamaan dynaamisesti kaikki `scripts/*.py`-tiedostot (`Path("scripts").glob("*.py")`) kovakoodatun skriptilistan sijaan.
  3. **AST-sääntö `QGR032` (Polyfactory 32-hex `UUIDv7` Invariant Guard):** Lisätään `@[scripts/_ast_guardrails.py]`-tiedostoon sääntö, joka varmistaa, että jokainen `@[backend_v2/tests/factories/model_factories.py]`-luokka reitittää ID-kenttänsä `Use(generate_opaque_id, ...)`-kutsun kautta ja tuottaa 100 % `OPAQUE_STRIPE_ID_REGEX`-yhteensopivia 32-heksaisia `UUIDv7`-arvoja, sekä lisätään dynaaminen `ModelFactory.__subclasses__()` -reflektiovarmennus tiedostoon `@[backend_v2/tests/factories/test_model_factories.py]`.
  4. **Yleisten PEP 593-, PEP 257- ja RFC 7807 -karkaisusääntöjen siirto suoraan staattiseen AST-vartijaan (`QGR020` Check 20B & `QGR033`):** Laajennetaan `@[scripts/_ast_guardrails.py]`-tiedostoa estämään paljaat `field: T = Field(...)` -määrittelyt ilman `Annotated[T, ...]`-käärettä (`QGR020`), `Raises: None` -docstringit (`QGR033`), puuttuvat moduuli- ja julkisten luokkien PEP 257 -docstringit (`QGR033`) sekä `raise AppException(...)` -kutsut ilman edeltävää `logger.error(...)`-kirjausta (`QGR033`), jolloin virheet jäävät kiinni välittömästi `/tier2-execute`-vaiheessa yhdellä kertaa.
  5. **Git Tree/Blob SHA-256 -välimuisti `@[scripts/auto_hardening_runner.py]`-skriptiin (`data/hardening_cache.json`):** Runner laskee kohdetiedoston + sen yksikkötestitiedostojen + `.agents/rules/*.md`-sääntötiedostojen yhdistetyn SHA-256-tiivisteen (`HardeningCacheEntryDTO` / `HardeningCacheManifestDTO`) ja esitäyttää välimuistin automaattisesti valmistuneista karkaisutrackereista (`@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`, `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` ja `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]`). Jos tiedostoa, yksikkötestiä tai sääntöjä ei ole muutettu edellisen onnistuneen hardening-commitin jälkeen, runner kuittaa kohteen `- [x]`-tilaan **0 sekunnissa** (`⚡ CACHE HIT`) käynnistämättä LLM-aliagenttia.
* **Suorituskomento:**
  ```powershell
  /tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]
  ```

---

### Askel 3.4b: FastAPI Reitittimien SSOT-konsolidointi (`reports.py`, `workflows.py`, `system_configs.py`) & Universaalin `CRUD + Clone` -elinkaaren lukitus (Vaihe 2f-2) — [100 % SUORITETTU, KOVENNETTU & LUKITTU]
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Router_SSOT_Consolidation.md]` (`16/16` Backend + `6/6` Frontend = `22/22` karkaistu, commitit `b62b65d47`, `ee38118ed`)
* **Toteutussuunnitelma (Implementation Plan):** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]`
* **Arkkitehtuurinen KI-standardi:** `@[ki_router_ssot_and_crud_clone_lifecycle.md]` (`single_router_ssot_mandate` & `crud_and_clone_lifecycle_standard_mandate`)
* **Tavoite (`@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 4):** Varmistetaan 100 % **1 Entiteetti = 1 Reititin SSOT** -kurinalaisuus kaikissa ei-IAM-reitittimissä ennen Askeleen 4 (`EPIC 160` IAM-reitittimien `auth.py`, `users.py`, `organizations.py` siivous) ja Askeleen 5.1 (Flutter API-asiakkaiden karkaisu) käynnistämistä sekä lukitaan universaali `CRUD + Draft + Clone` (`POST /{id}/clone`) -elinkaari automaattiseen laatuporttiin:
  1. **Kuolleen tyhjän reitittimen poisto (`system_configs.py`) & `/system/hooks`-prefiksikorjaus (`system/health.py`):** Poistetaan tyhjä varjoreititin `backend_v2/api/routers/studio/system_configs.py` ja sen testi `backend_v2/tests/unit/api/routers/studio/test_system_configs.py`, siivotaan `@[backend_v2/api/routers/studio/__init__.py]` sekä poistetaan päällekkäinen `prefix="/system"` tiedostosta `@[backend_v2/api/routers/system/health.py]` (`/api/v2/system/system/hooks` -> `/api/v2/system/hooks`).
  2. **`Workflow`-reitittimen SSOT-konsolidointi (`studio/workflows.py`) & kaikkien 5 vanhan Studio-reitittimen yhdenmukaistaminen `output_profiles.py`-standardiin:** Siirretään `GET /{id}/ui_schema` (`response_model=WorkflowSchemaResponseDTO`) tiedostosta `backend_v2/api/routers/execution/workflows.py` osaksi ainoaa virallista `Workflow`-reititintä `@[backend_v2/api/routers/studio/workflows.py]` (`/api/v2/studio/workflows/{id}/ui_schema`), poistetaan `execution/workflows.py`, päivitetään Flutterin `@[client_app_v2/lib/core/api/workflow_client.dart]` ja päivitetään kaikki 5 vanhempaa Studio-reititintä (`workflows.py`, `steps.py`, `prompt_blocks.py`, `model_registry.py`, `mcp_gateways.py`) tarkistamaan polkuparametreista `Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)]` sekä `PUT /{id}`-kutsuista Fail-Fast `ErrorCodes.ID_MISMATCH` täsmälleen `@[backend_v2/api/routers/output_profiles.py]`-mallin mukaisesti.
  3. **`ReportArtifact`-reitittimen täysi 1-Router SSOT-konsolidointi (`execution/reports.py` & `main.py`):** Yhdistetään `external_router` (`GET /external/reports/{report_id}`) suoraan `reports.py`:n ainoaan `router`-instanssiin, poistetaan `execution_reports_subrouter`, `external_router`, kaksoiskoristellut `include_in_schema=False` `/execution/...`-varjopolut, tuplakiinnitys `@[backend_v2/api/routers/execution/__init__.py]`-tiedostosta sekä vanhentuneet `external_reports_router`-kiinnitykset (`/api/v1` ja `/api/v2`) `@[backend_v2/main.py]`-tiedostosta; korjataan samalla `@[client_app_v2/lib/core/api/reports_client.dart]`-tiedoston `DGR008` `.substring()`-tekninen velka.
  4. **Universaali `CRUD + Clone` (`POST /{id}/clone`) & `OPAQUE_STRIPE_ID_REGEX` OpenAPI-laatuportti (`@[backend_v2/tests/unit/api/test_router_ssot_guardrails.py]`):** Lukitaan automaattinen testi, joka tarkistaa `app.routes`- ja `app.openapi()["paths"]`-rakenteista, ettei yksikään reitti ala `/api/v1`-, `/api/v2/system/system`- tai `/api/v2/execution/reports`-etuliitteellä ja että kaikki 6 konfiguroitavaa Studio/Ontologia-entiteettiä (`workflows`, `steps`, `prompt-blocks`, `output-profiles`, `model-registry`, `mcp-gateways`) toteuttavat täyden `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}` ja `POST /{id}/clone` -pinnan `OPAQUE_STRIPE_ID_REGEX`-polkuvalidoinnilla.
* **1. Generoi seurantatiedosto (valinnainen):**
  ```powershell
  /tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]
  ```
* **2. Suorituskomento:**
  ```powershell
  /tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Router_SSOT_Consolidation.md]
  ```

---

### Välivaiheen Todentaminen 3: Päästä päähän (E2E) -suoritusajon Varmennus 32-hex `PrefixedUUID7` Cutoverin (Askel 3.3), AST-laatuporttien (Askel 3.4) ja Router SSOT -konsolidoinnin (Askel 3.4b) Jälkeen Ennen `EPIC 161` -toteutusta — [SUORITETTU & VERIFIOITU]
> [!IMPORTANT]
> **Toimintakunnon ja 32-hex `UUIDv7` -pariteetin varmennus Askeleiden 3.3, 3.4 ja 3.4b jälkeen ennen `@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]` -toteutusta**
> Välittömästi Askeleen 3.3 (Malli A: 32-hex `PrefixedUUID7` 12 PostgreSQL 19 -taulussa, `@[backend_v2/seed/seed_data.json]` cutover ja `UUIDv4`-poisto), Askeleen 3.4 (`QGR020`, `QGR031`–`QGR033` ja SHA-256 hardening-välimuisti) sekä Askeleen 3.4b (`1 Entiteetti = 1 Reititin SSOT` ja `CRUD + Clone` -lukitus) valmistuttua varmennettiin koko järjestelmän päästä päähän -toimintakunto ajamalla täydellinen monivaiheinen tuotantoajo paikallisessa PostgreSQL 19 -ajoympäristössä (`/tier6-execution-monitor`).
>
> * **Suoritus-ID:** `exe_01a18ecef54372d39c31ef9fb1f12937` (Työnkulku: `wf_0195f3a00000700b89e2d71000000002` — *Tekoälyohjauksen ja Kognition Ydinauditointi*, Organisaatio: `org_system000000`, Käyttäjä: `usr_0195f3a00000700a83fd6b3d77c748f4`)
> * **Raportti-ID & Tulosprofiili:** `rep_01a18ed15c5a732288f2bb762c263440` (Profiili: `prf_0195f3a00000700b89e2d71000000002` — *Tekoälyohjauksen ja Kognition Ydinauditointi*)
> * **Ajankohta & Kesto:** 30.10.2026 klo 23:54:43 – 23:58:29 UTC+02:00 (3 min 46 s / 226 s)
> * **Tila & GitHub-versio:** 🟢 **PASSED & FINALIZED (100 % E2E Pariteetti, 0 virhettä, `healing_cost_events: 0`, `structural_warnings: 0`, `mcp_warnings: 0`)** — GitHub-versio `f1a6818a8` (`f1a6818a813efae79269481cd043c178c586c060`, *Merge branch 'main' of https://github.com/launis/quorum*; pohjalla commitit `3a914b43a` *feat: add EPIC-161 architectural planning and prompt blocks controller code generation* ja `ee38118ed` *docs(architecture): synchronize router ssot and crud+clone lifecycle*)
> * **Forensiikkaraportti:** ``data/files/executions/exe_01a18ecef54372d39c31ef9fb1f12937/forensic_summary.md``
> * **Todennettu ketju askel askeleelta:**
>   1. **Vaihe 1 (Ingress & DAG Heavy LLM Execution — `PASSED` klo 23:57:25, kesto 162 s):** Kolmen PDF-lähdedokumentin (`lopputuote.pdf`, `keskusteluhistoria.pdf`, `reflektiodokumentti.pdf`) purku ja kaikki 7 DAG-askelta kanonisilla 32-hex `UUIDv7`-tunnisteilla (`sr_0195f3a00000700b89e2d71000000001` `MarkdownBlock`, `sr_0195f3a00000700b89e2d71000000006` Two-Pass Atomizer `GlobalOntologyMap` / `LLMDraftAtomList` & `DynamicLinguisticsExtractorDTO`, 4 matriisiarviointiaskelta `sr_0195f3a00000700b89e2d71000000002` HACM [`7.90`, `3/25`], `sr_0195f3a00000700b89e2d71000000004` Toulmin [`5.45`, `5/25`], `sr_0195f3a00000700b89e2d71000000003` Bloom [`3.15`, `4/30`], `sr_0195f3a00000700b89e2d71000000005` Transparency [`0.00`, `0/25`] sekä `sr_0195f3a00000700b89e2d71000000007` `SynthesisEngine`) suoritettiin 100 % puhtaasti (`UNIFIED` Global Score `4.1 / 100.0`, `Penalties: 0`).
>   2. **Vaihe 2 (Asynkroninen profiilisynteesi — `PASSED` klo 23:57:52, kesto 24 s):** `ExecutiveSummarySectionResult`, `MatrixSectionSynthesesResult`, `XaiHighlightsResult`, `MatrixExplanationsResult` ja `VarianceExplanationResult` (`variance=3.6841`, `verdict=MISALIGNED`, `actual_Index=2.0`, `reflection_Index=1.0`, `prompt_Index=0.6316`) generoitiin virheettömästi.
>   3. **Vaihe 3 (WeasyPrint PDF & Flutter Desktop SDUI / Rows -pariteetti — `COMPLETED` klo 23:58:29, kesto 37 s):** 8-sivuinen PDF-raportti (`report.pdf`), `report.sdui.json`, `report.xlsx` ja `report.csv` koottiin virheettömästi (`rep_01a18ed15c5a732288f2bb762c263440`), ja Flutter Desktop -asiakasohjelma nouti sekä renderöi konsolidoidun reitittimen kautta raportin taulukkorivit (`GET /api/v2/reports/rep_01a18ed15c5a732288f2bb762c263440/rows` `200 OK`) ja SDUI-näkymäpuun (`GET /api/v2/reports/rep_01a18ed15c5a732288f2bb762c263440/sdui` `200 OK`) 32-hex `StrictOpaqueIdConverter`-validoinnilla ilman yhtäkään virhettä.

---

### Askel 3.4c: Topologisen Älykkyyden Säilyttäminen Tislauksessa, Synteesissä & SDUI-raportoinnissa (Vaihe 2f-3 — EPIC 161) — [100 % SUORITETTU, KOVENNETTU, SYNKRONOITU, AUDITOITU & LUKITTU]
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`31/31` Backend; `5/5` Frontend delegoitu Aaltoihin F1–F4), SYNKRONOITU (`/tier7-describe-architecture`, `81853a38e`), AUDITOITU (`/tier8-audit-epic`, `83f11d369`) & LUKITTU** — Vaiheiden 1–4 ja Live E2E -portin toteutus (`8f838d834`), `31/31` Backend Tier 2 Hardening (`auto_hardening_runner.py --gate backend`), As-Built dokumentaatiosynkronointi (`81853a38e`), System 2 Reverse Epic Audit (`83f11d369`, `@[docs/epic/EPIC_161_audit_report.md]`) sekä 5 Frontend SDUI -tiedoston (`/tier2-hardening-frontend`) delegointi kattaviin Flutter Karkaisuaaltoihin F1–F4 (Askeleet 5.1–5.4).
* **Lähtötilanteen E2E-varmennus:** Ennen `EPIC 161` -toteutuksen aloitusta koko 32-hex `PrefixedUUID7` -kannan, uusien AST-laatuporttien (`QGR020`, `QGR031`–`QGR033`) ja konsolidoitujen FastAPI-reitittimien päästä päähän -toimivuus on todennettu tuotantoajolla `exe_01a18ecef54372d39c31ef9fb1f12937` / `rep_01a18ed15c5a732288f2bb762c263440` GitHub-versiolla `f1a6818a8` (``data/files/executions/exe_01a18ecef54372d39c31ef9fb1f12937/forensic_summary.md``, ks. yllä oleva *Välivaiheen Todentaminen 3*).
* **Virallinen Eepos:** `@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]`
* **Red-Team Auditointiraportti (`0` virhettä):** `@[docs/epic/EPIC_161_audit_report.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/epic/EPIC_161_tracker.md]`
* **Vaihekohtaiset toteutussuunnitelmat (`docs/epic/tasks_EPIC_161/`):**
  1. **Vaihe 1:** `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]` — *Pre-Implementation Technical Debt Cleanups & Typed Topological Envelope Foundation*
  2. **Vaihe 2:** `@[docs/epic/tasks_EPIC_161/02_phase2_plan.md]` — *Orchestration, Frontier Contrastive Deficit Injection & Synthesis Convergence*
  3. **Vaihe 3:** `@[docs/epic/tasks_EPIC_161/03_phase3_plan.md]` — *Frontend Flutter UI, Jinja PDF & Freezed SDUI DTO Synchronization*
  4. **Vaihe 4:** `@[docs/epic/tasks_EPIC_161/04_phase4_plan.md]` — *Verification & E2E Integration Gate*
* **Tavoite (`5-Pillar Zero-Loss Epistemic Distillation Architecture`, `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 5 & `@[ki_sdui_matrix_synthesis.md]`):** Korjattiin ja lukittiin 6 rakenteellista litistymiskohtaa (Breakpoints 1–6), joissa Vaiheen 1 rikastetun DAG-suorituksen topologiset estoketjut (`short_circuit_reason_tda_ids`), kausaaliset riippuvuudet (`depends_on_tda_ids`), käänteiset myrkkyosumat (`is_inverse_evidence`), PostgreSQL 19 3-suuntaiset Toulmin-falsifikaatiot (`find_falsified_claims`) ja kontrastiiviset esimerkit (`ContrastivePairDTO`) kulkevat nyt nollahävikillä synteesiin ja SDUI-raportointiin:
  1. **Pilari 1 — Nollahävikkinen tislaus (`PASSED`-, `FAILED`-, `N_A`- ja `is_inverse_evidence`-säilytys):** Säilytetään kaikki `ExecutionStatus.PASSED`-, `ExecutionStatus.FAILED`-, `ExecutionStatus.N_A`- ja `is_inverse_evidence == True` -arvioinnit ilman tyhjän sitaatin pudotusta (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]` ja `@[backend_v2/services/orchestrator/matrix_reducer.py]`) ja järjestetään defisiitit topologisen vaikuttavuuden mukaan `(-int(item.is_inverse_evidence), -item.topological_out_degree, len(item.short_circuit_reason_tda_ids), atom_id)` silloin kun positiivinen leikkurikatto (`> 0`) on asetettu.
  2. **Pilari 2 — Rajoittamaton (`0`) synteesi- ja Micro-CoT-oletussäilytys (`step_1`–`step_4`):** Asetettiin `max_synthesis_evaluations = 0`, `max_synthesis_reasoning_length = 0`, `max_synthesis_quote_length = 0`, `max_synthesis_quotes_per_matrix = 0` ja `max_synthesis_unmet_criteria_per_matrix = 0` tiedostossa `@[backend_v2/settings.py]` (pitäen `Settings._enforce_environment_limits` 100 % koskemattomana), jotta `ReasoningStepDTO`:n (`@[backend_v2/models/dtos/atom_evaluation.py]`) kaikki 4 askelta ja suorat sitaatit säilyvät leikkautumatta.
  3. **Pilari 3 — Transitiivinen `N_A`-oikosulkujen periytyminen vanhemmalta lapselle:** Koska `@[backend_v2/services/orchestrator/topological_evaluator.py]` jättää `evaluation_reasoning = None` oikosuljetuille `N_A`-atomeille, `@[backend_v2/services/orchestrator/matrix_explanation_service.py]` sitoo jokaisen `N_A`-atomin `short_circuit_reason_tda_ids`-ketjun kautta suoraan sen kaataneen yläsolmun väitteeseen ja yläsolmun `evaluation_reasoning`-perusteluun.
  4. **Pilari 4 — Täysi kontrastiivinen ja antimallien ankkurointi (`MatrixFailureDeficitDTO`):** Luotiin `MatrixFailureDeficitDTO` tiedostoon `@[backend_v2/models/dtos/synthesis.py]`, joka injektoi `ContrastivePairDTO(rejected, acceptable)` (`@[backend_v2/models/domain/matrix.py]`) ja `anti_patterns` (`@[backend_v2/models/domain/matrix.py]`) kaikkiin `ExecutionStatus.FAILED`- ja `ExecutionStatus.N_A`-defisiitteihin.
  5. **Pilari 5 — Yhtenäinen `CausalSynthesisBriefDTO`, Toulmin-falsifikaatiot & SDUI/Jinja/Flutter-pariteetti:** Kytketään `@[backend_v2/database/postgres/graph_adapter.py]` (`CteReasoningStrategy.find_falsified_claims`) osaksi `CausalTdaFusionResultDTO`:ta (`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]`), injektoidaan `matrix_reducer_output.reduced_atoms` Vaiheen 1 `SynthesisEngine`:en (`@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`), hajautetaan `CausalSynthesisBriefDTO` kaikille neljälle synteesitehtävälle (`@[backend_v2/workers/synthesis_worker.py]`) ja sidotaan `short_circuited_by_claims` sekä `falsified_warrant_claims` kontekstuaalisesti matriisiriveihin ja kausaaligraafisolmuihin Pythonissa, Jinja2 PDF:ssä ja Flutter Freezed -komponenteissa.
* **1. Vaiheittainen suoritus (Aloita Vaiheen 1 syväanalyysillä):**
  ```powershell
  # Vaihe 1 Red-Team & syväanalyysi:
  /tier0-research-plan @[docs/epic/tasks_EPIC_161/01_phase1_plan.md] @[docs/epic/EPIC_161_tracker.md]
  ```
* **2. Automaattinen monivaihesuoritus & karkaisu (`auto_phase_runner.py` & `auto_hardening_runner.py`):**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_161_tracker.md --model gemini-4-argon-high
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_161_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"
  ```

---

### Askel 3.5: `PostgresEntityAdapter` (`[DELETE] entity_adapter.py`) God Code -purku (Vaihe 2g — Luku 7 Kohta 13) — [100 % SUORITETTU, KOVENNETTU 9/9, SYNKRONOITU, AUDITOITU & QGR017-LUKITTU]
* **Seurantadokumentti (SSOT Tracker):** `@[docs/epic/entity_adapter_decomposition_tracker.md]`
* **Vaihesuunnitelmat & Symbolikartta (`docs/epic/tasks_entity_adapter/`):**
  * `@[docs/epic/tasks_entity_adapter/symbol_migration_map.md]` (`48/48` AST-symbolia kartoitettu 1:1)
  * `@[docs/epic/tasks_entity_adapter/phase1_leaf_constants_and_coercion_extraction.md]` — *Phase 1: Package Scaffold, Coercion & Constants, and IAM & System Config Stage*
  * `@[docs/epic/tasks_entity_adapter/phase2_iam_and_studio_entities_extraction.md]` — *Phase 2: PromptBlock & Step Stage and Workflow & OutputProfile Stage*
  * `@[docs/epic/tasks_entity_adapter/phase3_execution_report_and_collection_extraction.md]` — *Phase 3: Execution & Report Stage and Seed & Collection Routing Stage*
  * `@[docs/epic/tasks_entity_adapter/phase4_package_cutover_and_guardrails.md]` — *Phase 4: Coordinator Facade Cutover, Monolith Deletion, and AST Guardrail Updates*
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`9/9` Backend via `auto_hardening_runner.py`), SYNKRONOITU (`/tier7-describe-architecture`, `fb94d8dbe`), AUDITOITU (`/tier8-audit-plan`, `a7a5ac6c7`) & QGR017-LUKITTU** — Epoch 1 (Vaiheet 1–4, commitit `bc3020d97`, `e6e94e4c7`), Epoch 2 (`9/9` kohdetta karkaistu, commitit `467885671`–`f32dfadf4`, `100 %` lausekattavuus `730/730` lausetta, `33` modulaarista yksikkötestiä + `18` Golden Master -pariteettitestiä), `/tier7-describe-architecture` (`fb94d8dbe`) ja `/tier8-audit-plan` (`a7a5ac6c7`).
* **Toteutettu ja lukittu 6-vaiheinen Zero-ORM SRP-pakettirakenne (`@[backend_v2/database/postgres/entity_adapter/]`):** Kun kaikki 12 taulua käyttävät yhtenäistä 16-tavuista `UUIDv7`-siltausta (Askel 3.3), `2 515` rivin (`48` AST-symbolin) `[DELETE] backend_v2/database/postgres/entity_adapter.py` purettiin Two-Epoch Strangler Fig -protokollalla kuuteen SRP-vaihemoduuliin ja ohueen koordinaattorifasaadiin ennen `EPIC 160` IAM-laajennuksia:
  1. `[x]` `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (`255` LOC — sarakelistat, `FilterOperator`-kuvaukset, `_to_pg_uuid` / `_from_pg_uuid` ja JSONB-koersioapurit)
  2. `[x]` `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (`372` LOC — `organizations`, `users`, `system_configs`)
  3. `[x]` `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (`398` LOC — `prompt_blocks`, `steps`)
  4. `[x]` `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (`405` LOC — `workflows`, `output_profiles`)
  5. `[x]` `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (`448` LOC — `executions`, `report_artifacts`, `report_binaries` ja kevyt `ExecutionSummarySnapshot`-projektio)
  6. `[x]` `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (`359` LOC — idempotentti `seed_validated_buffer` ja kokoelmatason reititys)
  7. `[x]` `@[backend_v2/database/postgres/entity_adapter/__init__.py]` (`242` LOC koordinaattorifasaadi `PostgresEntityAdapter`) + `[x]` `@[backend_v2/database/postgres/uow.py]` + `[x]` `@[backend_v2/database/postgres/storage_driver.py]` + `QGR017`-lukitus (`@[scripts/_ast_guardrails.py]`).
* **Laatuportti- ja karkaisukomento (Suoritettu 9/9):**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/entity_adapter_decomposition_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"
  ```

---

### Askel 3.6: Studio `OutputProfile` `target_blocks` -synkronointi, `CognitiveTier` SSOT & `LLMClient.from_strategy`-poisto sekä DAG Resilienssi, `ExecutionBudget`, `state_version` OCC & `input_merkle_hash` (Vaihe 2H — EPIC 162 / `arkkitehtuurin_parannuskohteet.md` Luvut 6, 7 & 8) — [SUORITETTU, KOVENNETTU 31/31, SYNKRONOITU, AUDITOITU & LUKITTU]
* **Seurantadokumentit, Vaihesuunnitelmat & Auditointiraportti:** `@[docs/epic/EPIC_162_tracker.md]`, `@[docs/epic/EPIC_162_audit_report.md]` sekä `@[docs/epic/tasks_EPIC_162/01_phase1_plan.md]`–`@[docs/epic/tasks_EPIC_162/04_phase4_plan.md]`
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`27/27` Backend + `4/4` Frontend = `31/31` via `auto_hardening_runner.py`), SYNKRONOITU (`/tier7-describe-architecture`, `9066bc8ab`), AUDITOITU (`/tier8-audit-epic`, `100 %` DoD) & LUKITTU** — Vaihe 1 (commitit `af3dafc5b`, `71ba73f8e`, `cc28095bc`), Vaihe 2 (commitit `9f32c34c6`, `c3c6ae39b`), Vaihe 3 (commitit `b0591fc62`, `47846b2d9`, `f9ae9d221`), Vaihe 4 (commitit `c8fe8abd5`, `2c0fa20de`, `a5b60d555`, `f48f98748`) ja `/tier7-describe-architecture` (`9066bc8ab`).
* **Tavoite:** Toteuta dokumentin `@[docs/arkkitehtuurin_parannuskohteet.md]` Luvut 6, 7 ja 8 4-vaiheisena eepoksena ennen Askelta 4 (`EPIC 160`):
  1. **Vaihe 1 (Luku 7 — `CognitiveTier` SSOT & `LLMClient.from_strategy` -poisto):** Korjaa kosketettujen tiedostojen teknisen velan varoitukset (`@[scripts/ablation_live_executor.py]` ja `@[backend_v2/tests/fakes/in_memory_uow.py]`), tyypitä `PipelineConfig.default_strategy: CognitiveTier | None = None` tiedostossa `@[backend_v2/models/enums.py]`, päivitä kaikki 5 tuotanto-/skriptikutsujaa (`@[backend_v2/services/chat_parser.py]`, `@[backend_v2/hooks/interaction_hook.py]`, `@[backend_v2/hooks/linguistics.py]`, `@[backend_v2/hooks/source_verification_hook.py]`, `@[scripts/ablation_live_executor.py]`) sekä 14 yksikkötestitiedostoa käyttämään `LLMClient.from_tier(CognitiveTier.<TIER>, ...)`-kutsua, poista `LLMClient.from_strategy` tiedostosta `@[backend_v2/llm/client.py]` ja lukitse kielto staattisella AST-vartijalla tiedostossa `@[scripts/_ast_guardrails.py]`.
  2. **Vaihe 2 (Luku 6 — Studio `Workflow` & `OutputProfile` `target_blocks` -synkronointi):** Lisää automaattinen vanhentuneiden matriisiviittausten (`matrix_synthesis_groups[*].target_blocks`, `variance_target_block`, `user_role_target_block`) siivous `StudioWorkflowService.save_workflow`-metodiin (`@[backend_v2/services/studio/workflow_service.py]`), täydennä `variance_target_block`- ja `user_role_target_block`-validointi `StudioOutputProfileService.save_output_profile`-metodissa (`@[backend_v2/services/studio/output_profile_service.py]`) ja renderöi mahdolliset tallentamattomat vanhentuneet lohko-ID:t poistettavina virhetyylisinä `FilterChip`-siruina `MatrixGraphItemEditor`-komponentissa (`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`).
  3. **Vaihe 3 (Luku 8.1 & 8.3 — Semanttinen oskillaatiotunnistin, `ExecutionBudget`, `input_merkle_hash` & MCP XML -siivous):** Korjaa kumulatiivinen `usage_agg`-laskenta ja lisää SHA-256-tulostiivisteeseen perustuva semanttinen oskillaatiotunnistin `execute_engine_retry_stage`-vaiheeseen (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`), lisää ajokohtaiset budjettirajat (`max_tokens_per_run`, `max_cost_usd_per_run`, `max_total_steps_per_run`) tiedostoon `@[backend_v2/settings.py]` ja pakota ne aaltojen välissä tiedostossa `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` (`ErrorCodes.QUOTA_EXCEEDED`), lisää solmutason `input_merkle_hash` `ExecutionStep`-malliin (`@[backend_v2/models/domain/execution.py]` & `@[client_app_v2/lib/features/execution/models/execution_step.dart]`) sekä osittaiseen uudelleenajoon (`@[backend_v2/services/execution/resumption_service.py]` & `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]`) ja siivoa varatut rakenteelliset XML-ohjaustagit ulkoisista MCP-tuloksista tiedostossa `@[backend_v2/services/mcp/mcp_tool_loop.py]`.
  4. **Vaihe 4 (Luku 8.2 — Prosessienvälinen optimistinen lukitus `state_version` OCC PostgreSQL 19 `executions`-taulussa):** Lisää `state_version: int = 1` `ExecutionRecord`-malliin (`@[backend_v2/models/domain/execution.py]`, `@[client_app_v2/lib/features/execution/models/execution_record.dart]`), `ExecutionUpdateDTO`- ja `NodeExecutionUpdateDTO`-malleihin (`@[backend_v2/models/dtos/trace.py]`, `@[backend_v2/models/dtos/node_execution.py]`), PostgreSQL 19 -skeemaan (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`) ja Zero-ORM-adapteriin (`@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]`, `@[backend_v2/database/postgres/storage_driver.py]`, `@[backend_v2/database/repositories/execution.py]`), ja kytke atomiset `expected_state_version`-tarkistukset (`ErrorCodes.CONFLICT`, HTTP 409) `ExecutionOverrideService`- ja `ExecutionCommitter`-palveluihin (`@[backend_v2/services/execution/override_service.py]`, `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py]`).
* **Virallinen Eepos:** `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]`
* **1. Suorita eepoksen System 2 Red-Team -analyysi ja generoi vaihesuunnitelmat + tracker:**
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier0-research-epic @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]"
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-planner @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]"
  ```
* **Laatuportti- ja karkaisukomento (Suoritettu 31/31):**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_162_tracker.md --model gemini-4-argon-high
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_162_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"
  ```

---

### Välivaiheen Todentaminen 4: Päästä päähän (E2E) -suoritusajon Varmennus Askeleen 3.6 (`EPIC 162`) Jälkeen ja Ennen Askeleen 4 (`EPIC 160` B2B SaaS IAM) Aloittamista — [SUORITETTU & VERIFIOITU]
> [!IMPORTANT]
> **Toimintakunnon peruskivi `EPIC 162` (`31/31` karkaistu) jälkeen ja ennen `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` -toteutusta**
> Heti kun Askeleet 3.4c (`EPIC 161`), 3.5 (`PostgresEntityAdapter`-purku `9/9`) ja 3.6 (`EPIC 162`: `CognitiveTier` SSOT, Studio `target_blocks` -synkronointi, `input_merkle_hash`, `ExecutionBudget` ja PostgreSQL 19 `state_version` OCC) oli toteutettu ja karkaistu, koko järjestelmän virheetön päästä päähän -toimintakunto todennettiin ajamalla täydellinen monivaiheinen tuotantoajo paikallisessa PostgreSQL 19 -ajoympäristössä (`/tier6-execution-monitor`).
>
> * **Suoritus-ID:** `exe_01a19ad8c8807129955f7c2e90d12a52` (Työnkulku: `wf_0195f3a00000700a88f1d71000000001`, Organisaatio: `org_system000000`, Käyttäjä: `usr_0195f3a00000700a83fd6b3d77c748f4`)
> * **Raportti-ID & Tulosprofiili:** `rep_01a19adc9f7b71c3bc89b220140aced2` (Profiili: `prf_0195f3a00000700a88f1d71000000001`)
> * **Ajankohta & Kesto:** 2.11.2026 klo 08:00:56 – 08:06:31 UTC+02:00 (5 min 35 s / `335 s`)
> * **Tila & Git Commit:** 🟢 **PASSED & FINALIZED (100 % E2E Pariteetti, 0 virhettä, `healing_cost_events: 0`, `structural_warnings: 0`, `mcp_warnings: 0`)** — Lähtötason commit `9066bc8ab`
> * **Forensiikkaraportti:** ``data/files/executions/exe_01a19ad8c8807129955f7c2e90d12a52/forensic_summary.md``
> * **Todennettu ketju askel askeleelta:**
>   1. **Vaihe 1 (DAG Heavy LLM Execution + `input_merkle_hash` + `state_version` OCC — `PASSED` klo 08:05:13):** Kaikki 7 DAG-solmua (`sr_0195f3a00000700a88f1d71000000001` `MarkdownBlock`, `sr_0195f3a00000700a88f1d71000000002` Two-Pass Atomizer & Causal Discovery `LinkerResponseDTO`, 4 matriisiarviointiaskelta `sr_0195f3a00000700a88f1d71000000003`–`sr_0195f3a00000700a88f1d71000000006` sekä `sr_0195f3a00000700a88f1d71000000008` `SynthesisEngine`) suoritettiin 100 % puhtaasti (`Global Score: 4.1, Penalties: 0`).
>   2. **Vaihe 2 (Asynkroninen 5-Pilarin Tekstisynteesi & WeasyPrint PDF — `COMPLETED` klo 08:06:31):** `ExecutiveSummarySectionResult`, `XaiHighlightsResult`, `MatrixExplanationsResult`, `VarianceExplanationResult` (`variance=3.93`, `verdict=MISALIGNED`) ja `MatrixSectionSynthesesResult` generoitiin ja 9-sivuinen PDF-raportti (`rep_01a19adc9f7b71c3bc89b220140aced2`) koottiin virheettömästi.
>   3. **Vaihe 3 (Flutter Desktop SDUI & Rows -pariteetti):** Flutter-asiakasohjelma nouti ja renderöi raportin SDUI-näkymäpuun (`GET /api/v2/reports/rep_01a19adc9f7b71c3bc89b220140aced2/sdui` `200 OK`) ja taulukkorivit (`GET /api/v2/reports/rep_01a19adc9f7b71c3bc89b220140aced2/rows` `200 OK`) ilman yhtäkään deserialisointi- tai skeemavirhettä.

---

### Askel 3.7: Jäännöspoikkeuslistojen (`RESIDUAL_*`), `JsonValue` / Open-JSON -Tyyppien ja Mock-UoW-Testien Poisto (Vaihe 2I — EPIC 163) — [100 % SUORITETTU, KOVENNETTU 53/53, SYNKRONOITU, AUDITOITU & LUKITTU]
* **Virallinen Eepos:** `@[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/epic/EPIC_163_tracker.md]`
* **Auditointiraportti (`Tier 8`):** `@[docs/epic/EPIC_163_audit_report.md]`
* **Vaihesuunnitelmat (`docs/epic/tasks_EPIC_163/`):** `@[docs/epic/tasks_EPIC_163/01_phase1_plan.md]` – `@[docs/epic/tasks_EPIC_163/07_phase7_plan.md]`
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`53/53` kohdetta), SYNKRONOITU (`/tier7-describe-architecture`) & AUDITOITU (`/tier8-audit-epic`)** — Vaihe 1 (`30aba5589`), Vaihe 2 (`596da6e53`), Vaihe 3 (`ab6ab3ec0`, `844c50644`), Vaihe 4 (`e1bd98004`), Vaihe 5 (`a3551fc01`), Vaihe 6 (`3ec37b5d4`) ja Vaihe 7 (`fbe6e1b33`).
* **Toteutetut kokonaisuudet (Vaiheet 1–7):**
  1. **Vaihe 1 (PEP 593 `Annotated` & Oletusarrokielto — `QGR020` Check 20B/20C):** Tyypitettiin kaikki domain- ja DTO-kentät PEP 593 `Annotated[..., Field(...)]`-muotoon, poistettiin hiljaiset oletusarvot identiteetti-, relaatio- ja näyttökentistä sekä tyhjennettiin `RESIDUAL_QGR020B_FILES` ja `RESIDUAL_QGR020C_FILES`.
  2. **Vaihe 2 & 3 (`JsonValue`-poisto — `QGR027`):** Korvattiin avoimet `JsonValue`-rakenteet tyypitetyillä Pydantic V2 DTO-unioneilla (`StepOutputValue`, `ContextVariableValue`, `TypedToolArgumentValue`) DTO-malleissa, `LLMClient`- ja `LiteLLMProvider`-kerroksissa sekä ingressi- ja orkestraattoripalveluissa, ja lukittiin `RESIDUAL_QGR027_FILES = frozenset()`.
  3. **Vaihe 4 (Muuttumattomat `ExecutionRecord`-tilasiirtymäapurit — `QGR028`):** Lisättiin domain-metodit `with_updated_step_state`, `with_updated_profile_synthesis` ja `with_cleared_profile_syntheses` luokkaan `ExecutionRecord` (`@[backend_v2/models/domain/execution.py]`), siirrettiin `worker.py`, `report_worker.py` ja `synthesis_worker.py` käyttämään niitä ja tyhjennettiin `RESIDUAL_QGR028_FILES`.
  4. **Vaihe 5 (Flutter Open-JSON -hävitys — `DGR005`):** Korvattiin avoimet `Map<String, dynamic>`- ja `dynamic`-kentät Freezed DTO -malleilla (`TypedContextValue`, `StepStatePayload`) ja kavennettiin `DGR005_EXEMPT_FILES` tasan 9 matalan tason HTTP/JSON-kuljetusrajatiedostoon (`@[scripts/_dart_guardrails.py]`).
  5. **Vaihe 6 (Worker-testien `InMemoryUnitOfWork`-migraatio — `Census F = 0`):** Korvattiin kaikki `MagicMock`/`AsyncMock` UnitOfWork -väärennökset tilallisella `InMemoryUnitOfWork`-toteutuksella (`@[backend_v2/tests/fakes/in_memory_uow.py]`) taustatyöntekijätesteissä (`test_worker.py`, `test_report_worker.py`, `test_synthesis_worker.py`, `test_variance_synthesis.py`, `test_synthesis_worker_deficits.py`), saavuttaen `Census F = 0` tiedostossa `@[scripts/audit_warning_baseline.py]`.
  6. **Vaihe 7 (Staattisten jäännöspoikkeusten ja `per-file-ignores`-listojen lopullinen sulku):** Poistettiin kaikki `RESIDUAL_*`-joukot tiedostosta `@[scripts/_ast_guardrails.py]` sekä `per-file-ignores`-poikkeukset tiedostosta `@[pyproject.toml]` ja lukittiin `DGR013`, `DGR014`, `QGR013` sekä `QGR033` Check 33B.

---

### Askel 4: B2B SaaS IAM, Token Exchange, 2FA, Redis Kill-Switch, BYOK & Direct Task Assignment Portal (Vaihe 3 — EPIC 160) — [100 % SUORITETTU, KOVENNETTU 51/51 (`37/37` BACKEND + `14/14` FRONTEND), SYNKRONOITU (TIER 7), AUDITOITU (TIER 8) & LUKITTU]
* **Auditointiraportti (`Tier 8`):** `@[docs/epic/EPIC_160_audit_report.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/epic/EPIC_160_tracker.md]`
* **Vaihesuunnitelmat (`docs/epic/tasks_EPIC_160/`):** `@[docs/epic/tasks_EPIC_160/01_phase1_plan.md]` – `@[docs/epic/tasks_EPIC_160/06_phase6_plan.md]`
* **Tila & Git Commitit:** 🟢 **VAIHEET 1–6 (`REQ-160-001`–`REQ-160-017`) & TIER 2 HARDENING (`37/37` Backend + `14/14` Frontend = `51/51`) SUORITETTU** — Vaihe 1 (Foundation & 15-table PostgreSQL 19 schema), Vaihe 2 (`f10dd15f6` — Token Exchange, TOTP 2FA & Router SSOT), Vaihe 3 (`792a2fe62` — `SecretService` BYOK KMS & Request-Scoped Injection), Vaihe 4 (`acb75b876` — `RevocationCache` Dual-Key Redis Kill-Switch, `TenantRateLimitService` & `UsageService` Quota Enforcement), Vaihe 5 (`4a17b7736` — `EmailService`, B2B Invitations, 4-Tier RBAC, GDPR Soft-Delete & `ExecutionAssignmentService`), Vaihe 6 (`21f866e09` — Flutter Auth, TOTP 2FA UI, `UserProfileSettingsView`, `OrganizationIamSettingsView` & `TaskAssignmentPortalView`) sekä Tier 2 Hardening (`37/37` Backend + `14/14` Frontend commitit `02d096a0f`–`998d8b4b1` ja makroportti `f9f9e6f53`, `1 353` läpäistyä Flutter-testiä, `0` `DGR`-virhettä).
* **Toteutetut ja karkaistut kokonaisuudet (Vaiheet 1–6):**
  1. **Vaihe 1 (Skeema, Enumit & 15 Taulun Zero-ORM Perusta):** Poistettu 4 vanhentunutta IAM-suunnitelmaluonnosta ja `backend_v2/services/auth/constants.py`, keskitetty 16 IAM/JWT/MFA/BYOK/Email/KMS-asetusta tiedostoon `@[backend_v2/settings.py]`, siirretty `UserRole` (`ROOT`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`) ja `SubscriptionStatus` tiedostoon `@[backend_v2/models/enums.py]`, lisätty `InvitationStatus`, `AssignmentStatus`, `AssignmentResultVisibility`, `EmailTransportMode`, `EmailDeliveryStatus`, `SecretScope`, `SecretStorageMode` ja `EntityPrefix` (`INVITATION = "inv"`, `TENANT_SECRET = "sec"`, `ASSIGNMENT = "tsk"`), päivitetty `ROOT_SYSTEM` = `"org_0195f3a0000070008000000000000001"` luokassa `SystemOrganizations` ja laajennettu `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[backend_v2/database/postgres/uow.py]` (`RESET quorum.current_org;`) sekä `@[scripts/audit_zero_orm_strictness.py]` kattamaan kaikki **15 PostgreSQL 19 -taulua** (`invitations`, `tenant_secrets`, `execution_assignments`).
  2. **Vaihe 2 (RFC 8693 Token Exchange, TOTP 2FA, 0,1 ms RAM JWT & IAM Router SSOT):** Toteutettu `TokenService.exchange_firebase_token` (pakollinen `firebase.sign_in_second_factor` 2FA-tarkistus, 1:1 `firebase_uid`-törmäyssuoja ja CLI `target_user_id` -vaihto), 0,1 ms RAM-validointi `TokenService.verify_token`, reitit `POST /api/v2/iam/auth/exchange`, `POST /api/v2/iam/auth/logout`, `POST /api/v2/iam/auth/impersonate` tiedostossa `@[backend_v2/api/routers/iam/auth.py]`, poistettu päällekkäiset `/auth/users*`-varjoreitit, päivitetty `require_role` tukemaan `Sequence[UserRole] | UserRole` -listoja tiedostossa `@[backend_v2/api/dependencies.py]` ja siirretty `@[scripts/run_e2e_variance_test.py]` käyttämään `_get_or_refresh_cli_session`-istuntoa (`CliSessionStateDTO`).
  3. **Vaihe 3 (`SecretService` Enterprise BYOK & Request-Scoped `SecretStr` Injection):** Toteutettu `@[backend_v2/services/auth/secret_service.py]` (`CLOUD_SECRET_MANAGER` ja `ENVELOPE_KMS` AES-256-GCM DEK + Cloud KMS KEK `kek_version`-tuella ja `ResolvedCredentialDTO`-palautuksella), pyyntökohtainen `pydantic.SecretStr`-injektio `LLMFactory`-, `LiteLLMProvider`-, `ToolDispatcher`- ja `GenericMCPClient`-kutsuihin ilman globaalia `os.environ`-mutaatiota, organisaation BYOK-päätepisteet (`GET`/`PUT`/`DELETE /api/v2/iam/organizations/{org_id}/secrets`) sekä DLP AST -sääntö `QGR033`.
  4. **Vaihe 4 (`RevocationCache` Dual-Key Redis Kill-Switch, `TenantRateLimitService` & FinOps Quota):** Toteutettu `@[backend_v2/core/redis_security.py]` (atominen O(1) `MGET revoked:usr:{user_id} revoked:jti:{jti}` Fail-Closed `503 Service Unavailable` -suojauksella sekä kiinteän aikaikkunan RPM/TPM-laskurit) ja kytketty `SubscriptionStatus`- sekä kuukausittainen USD `quota_limit` -tarkistus `UsageService.check_quota`-metodiin (`@[backend_v2/services/usage_service.py]`).
  5. **Vaihe 5 (`EmailService`, B2B Kutsut, 4-Tason RBAC, GDPR Soft-Delete & `ExecutionAssignmentService`):** Toteutettu `@[backend_v2/services/auth/email_service.py]`, yksittäis- ja eräkutsut (`InvitationBatchCreateDTO`) 256-bittisellä URL-tokenilla tiedostossa `@[backend_v2/services/auth/organization_service.py]`, 4-tason RBAC-hallintamatriisi, omat profiilipäivitykset (`PATCH /api/v2/iam/users/me/profile`), soft-delete-tietoinen `LAST_ADMIN_PROTECTION`, GDPR Soft-Delete -anonymisointi + `POST /api/v2/iam/auth/webhooks/firebase-user-deleted` sekä suora tehtäväportaali `@[backend_v2/services/execution/assignment_service.py]` (`/api/v2/execution/executions/assignments`: SafeLinks-immuuni `GET .../preview`, JIT-provisiointi + 2FA, `POST .../activate`, kaksikelloinen vanhentuminen ja kertakäyttöinen `POST .../submit`).
  6. **Vaihe 6 (Flutter Auth, TOTP 2FA UI, Eristetyt Asetusnäkymät & Tehtäväportaali):** Toteutettu `@Riverpod(keepAlive: true)` `AuthRepository`, pakollinen TOTP 2FA -rekisteröinti ja -haaste `AuthController`- ja `LoginScreen`-luokissa, `AuthInterceptor` single-flight `Completer<String>` -lukolla, 13 minuutin hiljainen token-virkistys, 5-vaiheinen `signOut`-putki sekä 4 uutta karkaistua Flutter-komponenttia (`@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`, `@[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]`, `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`) ja suora tehtäväosoituslomake `NewExecutionView`-näkymässä.
* **Karkaistut kohteet (`51/51` = `37/37` Backend + `14/14` Frontend `[OK]`):** Kaikki `@[docs/epic/EPIC_160_tracker.md]`-seurannan 37 backend-kohdetta ja 14 frontend-kohdetta on karkaistu, dokumentoitu (`@[docs/epic/EPIC_160_audit_report.md]`) ja lukittu (`data/hardening_cache.json`).
* **Tier 4 Guardrailit, Tier 7 Synkronointi & Tier 8 Loppusulku (`45c9cacda`, `02d2248f7`, `3402d327b`, `71b5247c6`):** Lukittu staattiset vartijat `ZORM007` (idempotentti `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` ja $O(1)$ `driver.get` PK-haku tiedostossa `@[backend_v2/database/repositories/identity.py]`), `DGR011` (`useContext()` post-`await` `if (!context.mounted)`-suoja tiedostossa `@[client_app_v2/lib/core/state/mutation.dart]`) ja `DGR012` (`GoRouter.refreshListenable` + `ValueNotifier` tiedostossa `@[client_app_v2/lib/router/router.dart]`), sekä suoritettu `/tier7-describe-architecture` (`3402d327b`) ja `/tier8-audit-epic` (`71b5247c6`, `@[docs/epic/EPIC_160_audit_report.md]`).
* **Virallinen Eepos:** `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`
  * **Backend (`backend_v2/`, 37 karkaistua kohdetta):** Kattaa kaikki 9 IAM-ydinmoduulia, 4 uutta turva-/palvelumoduulia (`@[backend_v2/services/auth/secret_service.py]`, `@[backend_v2/services/auth/email_service.py]`, `@[backend_v2/services/execution/assignment_service.py]`, `@[backend_v2/core/redis_security.py]`) sekä 24 integroitua tietokanta-, LLM-, MCP- ja reititinmoduulia (`@[docs/epic/EPIC_160_tracker.md]`).
  * **Frontend (`client_app_v2/lib/`, 14 karkaistua kohdetta):** `@[client_app_v2/lib/core/models/enums.dart]`, `@[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart]`, `@[client_app_v2/lib/features/auth/domain/models/user.dart]`, `@[client_app_v2/lib/features/auth/data/auth_repository.dart]`, `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]`, `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, `@[client_app_v2/lib/router/router.dart]`, `@[client_app_v2/lib/router/scaffold_with_nav.dart]`, `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`, `@[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`, `@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`, `@[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]`, `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`.

---

### Askel 4.1: BYOK Salaisuuksien PostgreSQL 19 -Pysyvyys (`UnitOfWorkFactory`), `system_configs.name` NOT NULL & Kanoninen Kohdevalitsin UI (`org_secret_target_dropdown`) — [100 % SUORITETTU, KOVENNETTU 14/14 & LUKITTU]
* **Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]`
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`10/10` Backend + `4/4` Frontend = `14/14`) & LUKITTU** (commitit `dc68c0aa2`, `b5e44d57c`, `0f975a9d7`, `b8a9c617a` sekä karkaisucommitit `284555e01`–`c167b23d5`).
* **Toteutetut korjaukset ja arkkitehtuurikovennukset (Vaiheet 1–4):**
  1. **Protokollatason `UnitOfWorkFactory`-rekisteröinti (`@[backend_v2/database/interfaces.py]` & `@[backend_v2/database/factory.py]`):** Lisätty `get_uow_factory() -> UnitOfWorkFactory | None` ja `set_uow_factory(factory: UnitOfWorkFactory) -> None` `IDatabaseDriver`-protokollaan, `PostgresDatabaseDriver`-ajuriin ja `MockDatabaseDriver`-testiajuriin sekä kytketty `driver.set_uow_factory(create_uow_factory())` tietokanta-ajurin alustukseen.
  2. **`SecretService`-muistivälimuistien poisto ja 100 % PostgreSQL 19 -pysyvyys (`@[backend_v2/services/auth/secret_service.py]`, `@[backend_v2/models/auth.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` & `@[backend_v2/database/postgres/uow.py]`):** Poistettu katoavat `_local_secrets`- ja `_deleted_secret_ids`-muistirakenteet, ohjattu kaikki `upsert_tenant_secret`-, `delete_tenant_secret`-, `_list_org_secret_records`- ja `_get_secret_record_by_id`-kutsut suoraan `entity_adapter`- / `uow_factory`-porttiin, vaihdettu poisto fyysiseksi tietokantarivin poistoksi (`delete_collection_document("tenant_secrets", secret_id)`) ja lisätty pakollinen `storage_mode: SecretStorageMode` -kenttä `TenantSecretCreateDTO`- ja `TenantSecretCreateDto`-malleihin (`@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`).
  3. **Kanoninen `system_configs.name` NOT NULL ja MCP-yhdyskäytävälistaus (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `@[backend_v2/models/domain/system_config.py]`, `@[backend_v2/seed/seed_data.json]` & `@[backend_v2/services/studio/system_config_service.py]`):** Muutettu `system_configs.name` pakolliseksi (`TEXT NOT NULL`), lisätty `"name": "Tavily MCP Gateway"` yhdyskäytävälle `sys_0195f3a00000700080008172bda70c86` tiedostossa `@[backend_v2/seed/seed_data.json]`, päivitetty `SystemConfigMCPGateways`- ja `McpGateway`-mallit (`@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`) ja avattu `GET /api/v2/studio/system-configs/mcp-gateways` rooleille `[UserRole.ROOT, UserRole.ADMIN]`.
  4. **Tyyppiturvallinen kohdevalikko Organisaation IAM- ja BYOK-näkymässä (`@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]` & `@[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`):** Korvattu vapaa tekstikenttä `DropdownButtonFormField<String>`-komponentilla (`ValueKey('org_secret_target_dropdown')`), joka sitoo `MCP_GATEWAY`-tilassa kanonisen `McpGateway.id`-tunnisteen (`sys_<hex32>`) ja näyttää ihmiselle luettavan `gateway.name`-otsikon (`Tavily MCP Gateway`), sekä `LLM_PROVIDER`-tilassa `LLMProvider`-arvon (`openai`, `ai_studio`, `vertex_ai`), hyläten informatiiviset `slug`-merkkijonot backendissä virheellä `ErrorCodes.VALIDATION_FAILED`.

---

### Askel 4.2: MCP JSON Schema Draft 2020-12, Kanoniset `id`-relaatiot (`slug`-hakukielto), Zero-Fallback AST Guardrailit & `system_configs` Fail-Fast -hidraatio — [100 % SUORITETTU, KOVENNETTU & LUKITTU]
* **Toteutussuunnitelmat:**
  * `@[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md]`
  * `@[docs/implementationplans/IMPLEMENTATION_PLAN_CANONICAL_ID_RELATIONS_AND_ZERO_FALLBACK_GUARDRAILS.md]`
  * `@[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md]`
* **Toteutetut kokonaisuudet:**
  1. **MCP JSON Schema Draft 2020-12 & 17-parametrinen Tavily-skeema (`@[backend_v2/models/dtos/mcp.py]`, `@[backend_v2/seed/seed_data.json]`, `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]` & `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]`):** Laajennettu `MCPToolSchemaPropertyDTO` ja `McpToolSchemaPropertyDto` tukemaan `anyOf`-, `oneOf`-, `items`-, `minimum`-, `maximum`- ja `additionalProperties`-kenttiä, toteutettu `anyOf`/`oneOf`-unionien purku ja `array`-syötekontrollit `McpToolParamsPanel`-näkymässä sekä päivitetty `tavily_search` (17 parametria) ja `tavily_extract` tiedostossa `@[backend_v2/seed/seed_data.json]`.
  2. **Kanoninen `id`-identiteetti, `slug`-hakukielto ja Zero-Fallback AST Guardrailit (`@[scripts/_ast_guardrails.py]`, `@[scripts/audit_zero_orm_strictness.py]` & `@[scripts/audit_database_atoms.py]`):** Lukittu säännöt `QGR016`, `QGR020` Check 20B, `QGR030` (32-hex `UUIDv7` ja `slug`-vertailukielto), `QGR031` (`FilterOperator`/`QueryCondition` ja `slug`-suodatuskielto), `ZORM004` ja `ZORM007` (kieltää `COALESCE`-oletukset pakollisille sarakkeille sekä pakottaa idempotentit `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` -evoluutiolauseet).
  3. **`system_configs` Fail-Fast -hidraatio ja PostgreSQL 19 -uudelleenseedaus (`@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[backend_v2/seed/run_seed.py]` & `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`):** Kytketty `hydrate_system_config_row` kääntämään `pydantic.ValidationError` strukturoiduksi RFC 7807 `AppException`-virheeksi (`ErrorCodes.DATABASE_ERROR`), laajennettu `verify_seed_table_counts_rows` validoimaan jokaisen `system_configs`-rivin hidraatio ja suoritettu tietokannan uudelleenseedaus (`run_seed.py`).

---

### Askel 4.3: LLM BYOK Ajonaikainen Kytkentä (`LLMClient.from_tier`, `ExecutionIngressService`, DAG-Orkestraattori & Synteesityöntekijät) — [100 % SUORITETTU, KOVENNETTU & LUKITTU]
* **Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]`
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU & LUKITTU** (commitit `c15bcdffa`, `28ebec232`, `c6e5274cf` ja karkaisucommit `fd433256b`).
* **Toteutetut kytkennät (Vaiheet 1–3):**
  1. **`LLMClient` & `LLMFactory` BYOK-avaimen ratkaisu (`@[backend_v2/llm/client.py]` & `@[backend_v2/llm/provider/provider_factory.py]`):** Laajennettu `LLMClient.__init__` ja `LLMClient.from_tier` vastaanottamaan `organization_id: str | None = None` ja `resolved_credential: ResolvedCredentialDTO | None = None`. Kun `LLMClient.from_tier` kutsutaan, se ratkaisee organisaatiokohtaisen avaimen `SecretService.resolve_llm_key(organization_id, resolved_provider_type)` -kutsulla, säilyttää `ResolvedCredentialDTO`-olion (`pydantic.SecretStr`) muistissa ja välittää sen `LLMFactory.create_provider`-kutsulle sekä `run_structured_task`- ja `run_chat`-suorituksille.
  2. **`GlobalContextVarsDTO.organization_id`-injektio suorituksen käynnistyksessä (`@[backend_v2/services/execution/ingress_service.py]`):** Päivitetty `ExecutionIngressService._persist_and_enqueue_execution` tallentamaan `GlobalContextVarsDTO(organization_id=initiator.organization_id, initiator_id=initiator.id, target_locale=payload.target_locale, profile_id=resolved_profile_id)` suoraan `ExecutionMetadata.global_context_vars`-kenttään ennen Arq-jonotusta.
  3. **Vaiheen 1 (DAG + MCP) ja Vaiheen 2 (Synteesi) organisaatiopropagaatio (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, `@[backend_v2/workers/synthesis_worker.py]` & `@[backend_v2/workers/variance_synthesis.py]`):** Päivitetty `execute_engine_with_retries` välittämään `effective_org_id` sekä `ToolDispatcher`-instanssille (MCP BYOK) että `LLMClient.from_tier`-kutsulle (LLM BYOK), ja päivitetty `SynthesisWorker.generate_all_explanations` sekä `execute_variance_explanation_task` välittämään `execution.organization_id` kaikille synteesin `LLMClient.from_tier`-kutsuille.

---

### Askel 4.4: 100 % DB-Only Secret SSOT (`0` `.env`-varapolkua), Vertex AI BYOK Service Account JSON + Express Mode, Kontekstivälimuistin Eristys sekä JSONB/Wire DTO -Lankapariteetti — [100 % SUORITETTU, KOVENNETTU 19/19 & BUG-HUNTING-LUKITTU]
* **Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]`
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`17/17` Backend + `2/2` Frontend = `19/19`) & BUG-HUNTING-LUKITTU** (suunnitelmacommitit `94a3ce478`, `d7821b08f`, `7ca49017f`, `9f18916d3`, karkaisucommitit `75655fca3`–`bdc0e447e` sekä JSONB/Wire DTO Bug-Hunting -commitit `e0cc6cf79`, `f225d1b55`, `a05973239`, `0e070d0d9`, `8b3b9404d`, `740660313`, `19777dacd` ja `b3980130d`).
* **Toteutetut kokonaisuudet:**
  1. **100 % tietokantapohjainen LLM- ja MCP-salaisuuksien ratkaisu ilman `.env`-varapolkuja (`@[backend_v2/services/auth/secret_service.py]`, `@[backend_v2/seed/seed_data.json]` & `@[backend_v2/services/studio/system_config_service.py]`):** Poistettu `_resolve_platform_llm_secret` ja `_resolve_platform_mcp_secret` kokonaan, yhdistetty `resolve_llm_key` ja `resolve_mcp_secret` käyttämään `_resolve_scoped_secret`-metodia (`organization_id` -> `ROOT_SYSTEM` luokassa `SystemOrganizations` taulussa `tenant_secrets` -> Fail-Fast `ConfigurationError` koodilla `ErrorCodes.SECRET_RESOLUTION_FAILED`), asetettu `"auth_env_var": null` Tavily-yhdyskäytävälle `sys_0195f3a00000700080008172bda70c86`, välitetty `organization_id` metodissa `StudioSystemConfigService.discover_mcp_gateway_tools` ja siirretty kaikki kehitysympäristön LLM- (`openai`, `ai_studio`, `vertex_ai`) ja MCP-avaimet (`sys_0195f3a00000700080008172bda70c86`) salattuina PostgreSQL 19 `tenant_secrets`-tauluun organisaatiolle `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`, luokka `SystemOrganizations`).
  2. **Vertex AI BYOK Service Account JSON + Express Mode, `vertex_location` DB SSOT ja organisaatioeristetty kontekstivälimuisti (`@[backend_v2/llm/adapters/vertex_adapter.py]`, `@[backend_v2/llm/adapters/ai_studio_adapter.py]` & `@[backend_v2/llm/caching_service.py]`):** Toteutettu `_parse_service_account_json` ja `build_provider_kwargs` tukemaan sekä monirivisiä Google Cloud Service Account JSON -valtakirjoja (`vertex_credentials`, `vertex_project`, `google.oauth2.service_account.Credentials`) että Express Mode API -avaimia ilman `GOOGLE_APPLICATION_CREDENTIALS`-ympäristömuuttujaa, sidottu `vertex_location` tietokannan `SystemConfigGeneral`-konfiguraatioon ja eristetty `LLMCachingService`-välimuistiavaimet organisaatiokohtaisesti (`{model}:{org_scope}_{ttl}_{expected_Dynamic_tokens}`).
  3. **Täydellinen `organization_id`-propagaatio kaikissa orkestraattori-, atomisoija-, RAG-, MCP- ja koukkupoluissa (`19/19` karkaistua kohdetta):** Kytketty `organization_id` tiedostoihin `@[backend_v2/services/orchestrator/enriched_dag_executor.py]`, `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`, `@[backend_v2/services/orchestrator/rag_preflight_service.py]`, `@[backend_v2/services/mcp/mcp_tool_loop.py]`, `@[backend_v2/hooks/interaction_hook.py]`, `@[backend_v2/hooks/linguistics.py]` ja `@[backend_v2/hooks/source_verification_hook.py]`, sekä lisätty monirivisen JSON-salaisuuden näkyvyyskytkin (`org_secret_visibility_toggle_btn`) näkymään `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`.
  4. **Post-BYOK JSONB-koodekin purku & 91 DTO-parin lankapariteetin Bug-Hunting (`e0cc6cf79`–`b3980130d`):**
     * Kanonisoitu `GlobalContextVarsDTO.initiator_id` tiedostoissa `@[backend_v2/models/dtos/global_context.py]` ja `@[backend_v2/services/execution/ingress_service.py]` (poistettu vanhentunut `alias="_sys_initiator_id"`).
     * Päivitetty `@[scripts/audit_dto_parity.py]` tarkistamaan `Field(alias=..., serialization_alias=...)` -määritykset sekä kaikki 91 Python- ja Flutter-DTO-paria (`[PASS] 91 model pairs verified, 0 mismatches found`).
     * Pakotettu `exclude_none=True` sarakkeiden `frozen_context`, `execution_summary` ja `metadata` serialisointiin metodissa `save_execution_row` (`@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]`).
     * Korjattu `encode_jsonb_binary` (`@[backend_v2/database/postgres/pool.py]`) purkamaan esiserialisoitu JSON-merkkijono `from_json`-kutsulla ennen `to_json`-binäärikoodausta (estäen PostgreSQL 19 `JSONB`-skalaarimerkkijonojen kaksoisserialisoinnin) ja lisätty idempotentti JSONB-skalaarien korjauslause tiedostoon `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`.
     * Synkronoitu Flutterin `ExecutionRecord`-, `ExecutionMetadata`-, `ExecutionTraceItemDto`- ja `ProfileSynthesisEntryDto`-mallit (`@[client_app_v2/lib/features/execution/models/execution_record.dart]` & `@[client_app_v2/lib/features/execution/models/execution_metadata.dart]`) 1:1 backendin lankamuodon kanssa (`disallowUnrecognizedKeys: true`).

---

### Välivaiheen Todentaminen 5: Päästä päähän (E2E) -suoritusajon Varmennus 100 % Tietokantapohjaisella LLM- ja Tavily MCP BYOK -konstellaatiolla — [SUORITETTU & VERIFIOITU]
> [!IMPORTANT]
> **Viides E2E-virstanpylvästodennus: 100 % Tietokantapohjainen LLM (`ai_studio`) & Tavily MCP (`sys_0195f3a00000700080008172bda70c86`) Salaisuusratkaisu + JSONB/Wire DTO -pariteetti varmennettu (9.11.2026)**
> Askeleiden 4 (`EPIC 160`) ja 4.1–4.4 jälkeen suoritettiin ja valvottiin `/tier6-execution-monitor`-protokollalla täysi tuotantotason E2E-ajo, joka todistaa, että koko kolmivaiheinen suoritusputki (DAG + Tavily MCP + 5-Pilarin Synteesi + WeasyPrint PDF + Flutter Desktop SDUI) toimii 100 % PostgreSQL 19 `tenant_secrets`-taulusta ratkaistuilla salaisuuksilla ilman yhtäkään `.env`-varapolkua tai DTO-deserialisointivirhettä:
> * **Suoritustunniste (`execution_id`):** `exe_01a1c086576272b7a33c508d27277e94` (`wf_0195f3a00000700a88f1d71000000001` — *Johtoryhmän kokous: Strategiasta toimeenpanoon*, profiili `prf_0195f3a00000700a88f1d71000000001`, organisaatio `org_0195f3a0000070008000000000000001`, käyttäjä `usr_0195f3a00000700a83fd6b3d77c748f4`)
> * **Raporttitunniste (`report_id`):** `rep_01a1c08a762d70b8b3b7c2fae8fcf6da`
> * **Git Commit -versio:** `b3980130d` (kaikki Askeleiden 4 ja 4.1–4.4 muutokset aktiivisina, kokonaiskesto `6 min 06 s` klo `15:36:25`–`15:42:31` UTC+02:00)
> * **Forensiikkaraportti:** ``data/files/executions/exe_01a1c086576272b7a33c508d27277e94/forensic_summary.md``
> * **Todennettu ketju askel askeleelta:**
>   1. **100 % Tietokantapohjainen LLM- ja Tavily MCP -salaisuusratkaisu (`tenant_secrets`):** Kaikki 16 LLM-kutsua (`gemini/gemini-3.8-flash`) ja molemmat kontekstivälimuistit (`gemini/gemini-3.8-flash:org_0195f3a0000070008000000000000001_4000000_200` ja `gemini/gemini-3.8-flash:org_0195f3a0000070008000000000000001_4000000_60`) ratkaisivat `ai_studio`-avaimen PostgreSQL 19 `tenant_secrets`-taulusta (`SecretService.resolve_llm_key`), ja molemmat faktantarkistuksen Tavily-verkkohaut (`sys_0195f3a00000700080008172bda70c86`, `backend_debug.log` rivit `434` ja `504`) ratkaisivat API-avaimen `tenant_secrets`-taulusta (`SecretService.resolve_mcp_secret`) ilman `.env`-varapolkua (`"auth_env_var": null`).
>   2. **Vaihe 1 (DAG Heavy LLM Execution + Tavily MCP Claim Verification — `PASSED` klo 15:40:57):** Kaikki 7 DAG-solmua (`sr_0195f3a00000700a88f1d71000000001` `MarkdownBlock`, `sr_0195f3a00000700a88f1d71000000002` Two-Pass Atomizer & Causal Discovery + 2 Tavily MCP -hakua, 4 matriisiarviointiaskelta `sr_0195f3a00000700a88f1d71000000003`–`sr_0195f3a00000700a88f1d71000000006` sekä `sr_0195f3a00000700a88f1d71000000008` `SynthesisEngine`) suoritettiin 100 % puhtaasti (`Base: 5.2`, `Final: 5.2`, `Penalties: 0.00`).
>   3. **Vaihe 2 (Asynkroninen 5-Pilarin Tekstisynteesi & WeasyPrint PDF — `COMPLETED` klo 15:42:28):** Kaikki 5 synteesikomponenttia (`ExecutiveSummarySectionResult`, `XaiHighlightsResult`, `MatrixExplanationsResult`, `VarianceExplanationResult` `variance=3.93` / `verdict=MISALIGNED` ja `MatrixSectionSynthesesResult`) generoitiin `37` sekunnissa organisaatiokohtaisella DB-avaimella ja 9-sivuinen PDF-raportti (`rep_01a1c08a762d70b8b3b7c2fae8fcf6da`) koottiin virheettömästi.
>   4. **Vaihe 3 (Flutter Desktop SDUI, Rows & Execution Polling -pariteetti klo 15:42:31):** Flutter-asiakasohjelma pollasia suoritustilan (`GET /api/v2/execution/executions/exe_01a1c086576272b7a33c508d27277e94` `200 OK`) ja renderöi raportin SDUI-näkymäpuun (`GET /api/v2/reports/rep_01a1c08a762d70b8b3b7c2fae8fcf6da/sdui` `200 OK`) sekä taulukkorivit (`GET /api/v2/reports/rep_01a1c08a762d70b8b3b7c2fae8fcf6da/rows` `200 OK`) nollalla virheellä (`healing_cost_events: 0`, `structural_warnings: []`, `hashing_warnings: []`).

---

### Askel 4.5: Yhtenäinen Salaisuusseedaus (`.env.secrets.local`), `SecretScope.TELEMETRY`, Tietokantapohjainen Logfire- & Firebase Admin -alustus sekä `service-account.json`- ja `MockLoginPanel`-poisto (Vaihe 3E — EPIC 164) — [100 % SUORITETTU, KOVENNETTU 17/17, SYNKRONOITU, AUDITOITU & LUKITTU]
* **Virallinen Eepos:** `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/epic/EPIC_164_tracker.md]`
* **Auditointiraportti (`Tier 8`):** `@[docs/epic/EPIC_164_audit_report.md]`
* **Vaihesuunnitelmat (`docs/epic/tasks_EPIC_164/`):** `@[docs/epic/tasks_EPIC_164/01_phase1_plan.md]` – `@[docs/epic/tasks_EPIC_164/04_phase4_plan.md]`
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`11/11` Backend + `6/6` Frontend = `17/17`), SYNKRONOITU (`/tier7-describe-architecture`) & AUDITOITU (`/tier8-audit-epic`, `80f1a3116`)** — Vaihe 1 (`e31d46648`), Vaihe 2 (`d2f9a87fb`), Vaihe 3 (`1012f18b9`), Vaihe 4 (`7df1c8daf`), Tier 2 Hardening (`011e39713`–`abc0328e1`) ja Tier 8 sulku (`80f1a3116`).
* **Toteutetut kokonaisuudet (Vaiheet 1–4):**
  1. **Vaihe 1 (`SecretScope.TELEMETRY`, RBAC & `.env.secrets.local`-seedaus):** Lisättiin `SecretScope.TELEMETRY = "telemetry"` tiedostoihin `@[backend_v2/models/enums.py]` ja `@[client_app_v2/lib/core/models/enums.dart]`, rajattiin telemetriasalaisuudet `UserRole.ROOT`-käyttäjille organisaatiossa `ROOT_SYSTEM` (`SystemOrganizations`), lisättiin `"tenant_secrets"` 11 taulun `CANONICAL_SEED_TABLES`-joukkoon, toteutettiin `LocalSeedSecretsSettings` ja `_seed_local_secrets_if_present` tiedostossa `@[backend_v2/seed/run_seed.py]` lukemaan `.env.secrets.local`-avaimet (`openai`, `ai_studio`, `vertex_ai`, `tavily`, `logfire`) ja provisioitiin automaattisesti `ROOT`-käyttäjän Firebase Auth -tili (`_provision_root_firebase_user`).
  2. **Vaihe 2 (Käynnistysaikainen tietokantapohjainen Logfire- ja Firebase Admin -alustus):** Toteutettiin `SecretService.resolve_telemetry_secret`, `resolve_startup_logfire_token` (`@[backend_v2/core/telemetry.py]`) sekä muistipohjainen `initialize_firebase_admin_from_secrets` (`@[backend_v2/services/auth/token_service.py]`) ja kytkettiin ne sekä API-palvelimen (`@[backend_v2/main.py]`) että taustatyöntekijän (`@[backend_v2/worker.py]`) käynnistykseen.
  3. **Vaihe 3 (`service-account.json`-tiedostoriippuvuuden ja mock-tokenien poisto):** Poistettiin kaikki fyysiset `service-account.json`-polut ja `allow_mock_tokens` / `mock_*_user_id` -kentät tiedostosta `@[backend_v2/settings.py]`, poistettiin `_verify_mock_token` tiedostosta `@[backend_v2/services/auth/token_service.py]` ja kytkettiin `@[scripts/run_e2e_variance_test.py]` autenttiseen Firebase Identity Toolkit REST API -kirjautumiseen (`_exchange_firebase_email_password`).
  4. **Vaihe 4 (Flutterin `MockLoginPanel`-ohitusten poisto & Telemetria-UI):** Poistettiin `MockLoginPanel` tiedostosta `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, poistettiin `debugMockLogin` ja `debugSignInWithMockToken` tiedostoista `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]` ja `@[client_app_v2/lib/features/auth/data/auth_repository.dart]` sekä lisättiin `SecretScope.telemetry` (`"logfire"`) `ROOT`-käyttäjän kohdevalikkoon näkymässä `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`.

---

### Askel 4.6: Tehtävänantojen, `TaskBrief` (`PromptBlockCategory.TASK_DEFINITION`) `CRUD + Clone` -elinkaaren ja Suoran Tehtäväportaalin Päästä päähän -karkaisu (Vaihe 3F — Findings A–E) — [100 % SUORITETTU, KOVENNETTU 14/14, SYNKRONOITU, AUDITOITU & LUKITTU]
* **Virallinen Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]`
* **Tila & Git Commitit:** 🟢 **100 % SUORITETTU, KOVENNETTU (`9/9` Backend + `5/5` Frontend = `14/14`), SYNKRONOITU (`/tier7-describe-architecture`) & AUDITOITU (`/tier8-audit-plan`, `100 %` pariteetti)** — Vaihe 1 (`f50520284`), Vaihe 2 (`e025b1e30`), Vaihe 3 (`7bac2dc99`), Vaihe 4 (`c21fca8d6`), Tier 2 Hardening (`a93056dea`–`a6bd5a7b5`) ja konsoli-PII-hygienia (`08385c09b`).
* **Toteutetut kokonaisuudet ja tuotanto-opit (Findings A–E):**
  1. **Finding C — Kanoninen Resend EU REST -skeema, HTML-suojattu CTA-painike & Konsolin PII-maskaus (`@[backend_v2/services/auth/email_service.py]`):** Toteutettiin `EmailService._compose_transactional_html(html_body: str, action_url: SecretStr) -> str`, joka suojaa taikalinkin `html.escape(raw_url, quote=True)`-kutsulla ja upottaa englanninkielisen `"Open Quorum Portal"` CTA-painikkeen sekä kopioitavan varalinkin sähköpostin runkoon (`_redact_action_url` ja `mask_email_address` suojaavat lokitulosteet, `QGR033`). Samalla `_send_single_http_item` kavennettiin tiukasti Resendin Zod-skeeman hyväksymiin 5 juurikenttään (`from`, `to`, `subject`, `html`, `tags`: `category`, `entity_id`, `locale`) poistamalla vanhentuneet ei-Resend-juuriavaimet (`html_body`, `action_url`, `recipient_name`), jotka aiheuttaisivat tuotannossa HTTP 400/422 -hylkäyksen.
  2. **Finding E — Normalisoitu `execution_assignments.task_brief_id` Vierasavain, `92/92` DTO-pariteetti & `TaskBrief` `CRUD + Clone`:** Lisättiin suljettuun 15 taulun skeemaan (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `ZORM004`, `ZORM006`, `ZORM007`) sarakkeeksi `task_brief_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL` (UUIDv7 `CHECK`-rajoitteella ja idempotentilla `ALTER TABLE`-lauseella), säilytettiin `PromptBlockCategory.TASK_DEFINITION` ja `RUNTIME_VARIABLES` metodissa `StudioPromptBlockService.create_prompt_block_draft`, ja synkronoitiin `TaskAssignmentBriefDTO` $\leftrightarrow$ `TaskAssignmentBriefDto` (`92 / 92` jaettua DTO-paria `audit_dto_parity.py`:ssä) saastuttamatta `locked_inputs.dynamic_inputs`-avaimia tai `SmartIngressResolver`-paikkatunnistusta. Näkymään `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]` toteutettiin `_TaskBriefsManagementCard` (`organizationTaskBriefsProvider` palauttaen `Future<List<PromptBlock>>` suodatettuna `.whereType<TaskDefinitionPromptBlock>()` `riverpod_generator ^4.0.0` Freezed-unionirajoitteen mukaisesti, tyhjien tekstien `null`-normalisoinnilla, `ROOT` org-vaihdon invalidaatiolla ja asiakasorganisaation `ADMIN`-roolin muokkaus-/poistosuojalla `ROOT_SYSTEM`-lohkoille).
  3. **Finding A — Autenttinen Firebase Auth + Pakollinen TOTP 2FA JIT -portaalionboarding (`@[backend_v2/services/execution/assignment_service.py]`, `@[client_app_v2/lib/features/auth/data/auth_repository.dart]` & `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`):** Palvelinpuolen `_verify_onboarding_firebase_token` varmistaa aina ensin `IDENTITY_MISMATCH`-ehdon (`token_email == expected_email.lower()`) ja kutsuu vasta täsmäävälle kutsutulle osoitteelle muistipohjaisen Firebase Admin SDK:n kautta `fb_auth.update_user(uid_str, email_verified=True)` ennen `_enforce_firebase_mfa_claim`-vaatimusta (edellyttäen pilvessä `roles/firebaseauth.admin`-oikeutta `vertex_ai` Service Accountille). Tämä avaa asiakaspuolen `multiFactor.getSession()`-istunnon ilman `unverified-email`-estettä. Asiakaspuolen `AuthRepository` eriytti jaetut MFA SSOT -apurit (`prepareEnrollmentForCurrentUser`, `resolveChallengeAndGetIdToken`, `enrollTotpAndGetIdToken`) ja toteutti `authenticateForTaskOnboarding`-metodin, joka käsittelee sekä `'user-not-found'`- että Firebase Email Enumeration Protectionin oletusarvoisen `'invalid-credential'`-paluukoodin siirtymällä hallitusti `createUserWithEmailAndPassword`-luontiin ja portaalin sisäiseen `MFA_REQUIRED` TOTP-aktivointiin (`task_portal_totp_secret_text`).
  4. **Finding B — Itsenäinen `TaskAssignmentConfigDialog` & Kohortti-CSV (`@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`):** Ylennettiin `TaskAssignmentConfigDialog` julkiseksi komponentiksi, joka sisältää itsenäiset `Workflow`-, `OutputProfile`- ja `TaskDefinitionPromptBlock` (`taskBriefId`) -valitsimet, lokalisoidut `ExpectedInput.label` `FilterChip`-syötelukitukset, todennetun lähetystilayhteenvedon (`assignedEmail`, `emailDeliveryStatus`, `id` ilman julkisen `tsk_<hex32>`-tunnisteen sekoittamista salattuun URL-tokeniin) ja kohortti-CSV-viennin.
  5. **Finding D — Portaalin Liitetiedostojen Välitön `Base64Attachment`-purku (`base64_amnesia_protocol`):** Laajennettiin `ExecutionAssignmentDraftDTO.draft_inputs` ja `ExecutionAssignmentSubmitDTO.submitted_inputs` muotoon `WorkflowInputsIngress | WorkflowInputs`, injektoitiin `DocumentExtractionServiceDep` myös `PUT .../draft`-reitille ja toteutettiin `ExecutionAssignmentService._normalize_assignee_ingress_inputs`, joka purkaa portaalista ladatut `.pdf`-, `.docx`- ja `.txt`-tiedostot (`FilePicker.platform.pickFiles` $\rightarrow$ `WorkflowInputValue.file`) välittömästi puhtaaksi tekstiksi muistissa ennen tietokantatallennusta tai `ExecutionCreate`-ajoa.

---

### Askel 5: Firebase Storage & Direct-to-Cloud Signed URLs (Vaihe 4 — Nykyinen As-Built vs. Suoralatauslaajennus)
* **Mitä koodikannassa on JO toteutettu ja karkaistu (`3/3` tiedostoajuria valmiina):**
  1. **Tiedostoajurit (`@[backend_v2/services/file_driver.py]`, `@[backend_v2/services/drivers/local_file_driver.py]`, `@[backend_v2/services/drivers/gcs_file_driver.py]` ja `@[backend_v2/services/storage.py]`):** Kaikki kolme ajuritiedostoa on toteutettu ja Tier 2 -karkaistu (commitit `fa940a23f`, `48d9ef2fe`, `85a7721ea`). Kun Cloud Runissa asetetaan `STORAGE_BUCKET_NAME`, `get_storage_driver()` valitsee automaattisesti `GCSFileDriver`-ajurin, joka lukee ja kirjoittaa generoidut raportit (`report.pdf`, `report.xlsx`, `report.csv`, `report.sdui.json`) Google Cloud Storageen (lisäksi raporttibinäärit tallennetaan PostgreSQL 19 `report_binaries`-tauluun).
  2. **Nykyinen syötetiedostojen käsittely (*Base64 Amnesia Eager Extraction* — sekä pääkäyttöliittymä että `/task/:token`-portaali):** Flutterin `FileInputField` (`@[client_app_v2/lib/shared/widgets/file_input_field.dart]`) sekä suoran tehtäväportaalin `TaskAssignmentPortalView` (`@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`, `FilePicker.platform.pickFiles` $\rightarrow$ `WorkflowInputValue.file`) lukevat valitun dokumentin (`.pdf`, `.docx`, `.txt`, `.md`) muistiin ja lähettävät sen joko suorituksen käynnistyspyynnössä (`POST /api/v2/execution/executions`) tai tehtäväportaalin tallennus-/palautuspyynnöissä (`PUT /api/v2/execution/assignments/{id}/draft` ja `POST /api/v2/execution/assignments/{id}/submit`). Backendin `ExecutionIngressService` (`@[backend_v2/services/execution/ingress_service.py]`), `ExecutionAssignmentService._normalize_assignee_ingress_inputs` (`@[backend_v2/services/execution/assignment_service.py]`) ja `DocumentExtractionService` purkavat binäärin **välittömästi ingressirajalla** puhtaaksi tekstiksi/markdowniksi ja hävittävät raakabinäärin muistista ennen tietokantatallennusta (`base64_amnesia_protocol`). Tämä toimii tilattomasti Cloud Runissa kaikille normaaleille dokumenteille (Cloud Runin HTTP/1.1-pyyntöraja on `32 MB`).
* **Mitä Askel 5 (`Direct-to-Cloud Signed URLs`, Luku 4) lisää (valinnainen tai >32 MB tiedostoille):**
  1. **Suoralataus ohi API-kontin (`POST /api/v2/files/upload-request` -> 15 min Signed PUT URL -> `POST /api/v2/files/{id}/confirm`):** Asiakasohjelma lataa isot binääritiedostot suoraan selaimesta/työpöydältä Google Cloud Storageen (`gs://...`) ilman että binääri kulkee `quorum-api`-kontin RAM-muistin tai Cloud Runin 32 MB HTTP-pyyntörajan läpi.
  2. **16. PostgreSQL 19 -taulu (`file_metadata`):** Kirjaa ladatun tiedoston elinkaaren (`pending` -> `uploaded` -> `verified`), `organization_id`-eristyksen, `size_bytes`-koon ja `storage_path`-polun.
  3. **Orpotiedostojen siivous (Arq CronJob) & GDPR Split-Brain -poistoketju:** Siivoaa yli 24 tuntia `pending`-tilassa olleet keskeytyneet lataukset ja poistaa käyttäjän GCS-tiedostot osana GDPR-poistoa.
* **Toteutussuunnitelma (`[NEW]`, kun suoralataus otetaan käyttöön):** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]`
* **Seurantadokumentti (`[NEW]` Tracker):** `@[docs/implementationplans/TRACKER_Storage_Signed_URLs.md]`
* **1. Luo suunnitelma ja seurantatiedosto:**
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier0-create-plan 'Firebase Storage Direct-to-Cloud Signed URLs, FileMetadata lifecycle, and orphan cleanup worker (Askel 5)'"
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-plan-tracker-generator docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md"
  ```
* **2. Suorita automaattisesti:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_Storage_Signed_URLs.md --model gemini-4-argon-high
  ```

---

### Askel 5.1–5.4: Koko `client_app_v2/lib/` Frontend- ja Studio UI -Koodikannan Karkaisuaallot F1–F4 (Bottom-Up Hardening Roadmap, Vaihe 4b) — [SUORITETTU & LUKITTU 185/185]

Vastaavasti kuin backendissä (`backend_v2/` 403 tiedostoa), myös koko Flutter Web- ja Desktop -asiakassovelluksen (`client_app_v2/lib/`) **194 ei-generoitua `.dart`-lähdetiedostoa** (pl. `*.freezed.dart`, `*.g.dart` ja `l10n/`) karkaistaan systemaattisesti alhaalta ylös (Bottom-Up) neljässä karkaisuaallossa (`Aallot F1–F4`) ennen pilvituotantoon julkaisua:

| Frontend-kategoria (`client_app_v2/lib/`) | Tiedostomäärä | Tila ja seurantadokumentti |
| :--- | :--- | :--- |
| **1. Karkaisuaalto F1 — Core, Network, API Clients, Error Boundaries, Theme, Shell & Shared Models** | `41 / 41` kpl | **[SUORITETTU & LUKITTU]** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]` (Askel 5.1) |
| **2. Karkaisuaalto F2 — Freezed Domain & DTO Models + Riverpod Controllers & Providers** | `44 / 44` kpl | **[SUORITETTU & LUKITTU]** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md]` (Askel 5.2) |
| **3. Karkaisuaalto F3 — Execution, Reports & Shared SDUI / Presentation Widgets** | `47 / 47` kpl | **[SUORITETTU & LUKITTU]** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md]` (Askel 5.3) |
| **4. Karkaisuaalto F4 — Quorum Studio Master Views, Profile Block Editors & Workflow Canvas Widgets** | `53 / 53` kpl | **[SUORITETTU & LUKITTU]** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]` (Askel 5.4) |
| **5. Eristetty B2B SaaS IAM, Asetusnäkymät & Tehtäväportaali (`EPIC 160`)** | `14 / 14` kpl | **[SUORITETTU & LUKITTU]** `@[docs/epic/EPIC_160_tracker.md]` (Askel 4, commit `f9f9e6f53`) |
| **YHTEENSÄ (`client_app_v2/lib/`)** | **199 kpl** | **185/185 tiedostoa Karkaisuaalloissa F1–F4 [SUORITETTU & LUKITTU] + 14/14 kohdetta Askeleessa 4 (`EPIC 160`) [SUORITETTU & LUKITTU] + jatkokarkaisut Askeleissa 4.5 & 4.6 = 100 % kattavuus (`0` `DGR`-virhettä, `0` `dart analyze` -huomautusta, `92/92` jaetun DTO-parin pariteetti ja `1 387` läpäistyä testiä koko `client_app_v2/`-koodikannassa)** |

> [!IMPORTANT]
> **Frontend-karkaisun laatuvaatimukset (`/tier2-hardening-frontend` & `@[.agents/rules/02_flutter_desktop.md]`):**
> 1. **100 % teemasuvereeni ulkoasu (`audit_flutter_theme_sovereignty.py`):** Nolla kovakoodattua `Color(0x...)`-arvoa tai `Colors.*`-vakiota widgeteissä; kaikki värit ja typografia haetaan `Theme.of(context).colorScheme`- ja `AppColors`-kokoelmista.
> 2. **100 % Dumb Painter & Freezed DTO -pariteetti (`audit_dto_parity.py`):** Kaikki DTO-mallit ovat muuttumattomia `@freezed`-luokkia, jotka vastaavat 1:1 backendin Pydantic V2 -malleja ja 32-heksaisia `PrefixedUUID7`-avaimia ilman `Map<String, dynamic>`-sanakirjakikkailua.
> 3. **Nolla Red Screen of Death -kaatumista (`AppErrorBoundary` & `AsyncValue.when`):** Jokainen Riverpod-näkymä käsittelee `loading`-, `error`- ja `data`-tilat eksplisiittisesti ilman `!`-pakotuksia (null-check bang operator) tai hiljaisia `SizedBox.shrink()`-virhenieluja.
> 4. **Widget- ja yksikkötestit (`client_app_v2/test/`):** Jokaiselle karkaistulle mallille, kontrollerille ja näkymälle varmistetaan sekä positiivinen että negatiivinen/rajatapaus-yksikkö- tai widget-testi.
> 5. **`EPIC 161` Frontend SDUI -kohteiden delegointi Karkaisuaaltoihin F1–F4:** Askeleen 3.4c (`EPIC 161`) Vaiheen 3 koskemat 5 Frontend SDUI -tiedostoa (`@[client_app_v2/lib/shared/models/sdui_block_dto.dart]` Aallossa F1, `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]` ja `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]` Aallossa F2 sekä `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]` ja `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` Aallossa F3) on delegoitu suoritettavaksi osana kattavia Flutter Karkaisuaaltoja F1–F4.

---

### Askel 5.1: Frontend Karkaisuaalto F1 — Core, Network, API Clients, Error Boundaries, Theme, Shell & Shared Models (41/41 tiedostoa) — [SUORITETTU & LUKITTU]
* **Seurantadokumentti:** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Root, Routing, Shell & Theme (11 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/main.dart]`
  2. `[x]` `@[client_app_v2/lib/app.dart]`
  3. `[x]` `@[client_app_v2/lib/app_config.dart]`
  4. `[x]` `@[client_app_v2/lib/firebase_options.dart]`
  5. `[x]` `@[client_app_v2/lib/router/router.dart]`
  6. `[x]` `@[client_app_v2/lib/router/scaffold_with_nav.dart]`
  7. `[x]` `@[client_app_v2/lib/features/shell/presentation/scaffold_with_nav.dart]`
  8. `[x]` `@[client_app_v2/lib/features/shell/presentation/widgets/admin_sidebar.dart]`
  9. `[x]` `@[client_app_v2/lib/theme/app_colors.dart]`
  10. `[x]` `@[client_app_v2/lib/theme/app_durations.dart]`
  11. `[x]` `@[client_app_v2/lib/theme/app_theme.dart]`
* **Paketti 2 — Core API Clients & Dio Network Interceptors (10 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/core/api/execution_client.dart]`
  2. `[x]` `@[client_app_v2/lib/core/api/reports_client.dart]`
  3. `[x]` `@[client_app_v2/lib/core/api/sse_client.dart]`
  4. `[x]` `@[client_app_v2/lib/core/api/studio_client.dart]`
  5. `[x]` `@[client_app_v2/lib/core/api/workflow_client.dart]`
  6. `[x]` `@[client_app_v2/lib/core/network/api_client.dart]`
  7. `[x]` `@[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart]`
  8. `[x]` `@[client_app_v2/lib/core/network/interceptors/dio_logger_interceptor.dart]`
  9. `[x]` `@[client_app_v2/lib/core/network/interceptors/error_interceptor.dart]`
  10. `[x]` `@[client_app_v2/lib/core/network/interceptors/locale_interceptor.dart]`
* **Paketti 3 — Core Error Boundaries, Logging, Models, Utils & Shared DTOs (20 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/core/environment/env.dart]`
  2. `[x]` `@[client_app_v2/lib/core/error/app_error_boundary.dart]`
  3. `[x]` `@[client_app_v2/lib/core/error/app_error_ext.dart]`
  4. `[x]` `@[client_app_v2/lib/core/error/app_exception.dart]`
  5. `[x]` `@[client_app_v2/lib/core/error/validation_error_reason.dart]`
  6. `[x]` `@[client_app_v2/lib/core/logging/app_logger_observer.dart]`
  7. `[x]` `@[client_app_v2/lib/core/logging/logger_service.dart]`
  8. `[x]` `@[client_app_v2/lib/core/models/enums.dart]`
  9. `[x]` `@[client_app_v2/lib/core/models/generic_status_response_dto.dart]`
  10. `[x]` `@[client_app_v2/lib/core/models/prompt_block_category.dart]`
  11. `[x]` `@[client_app_v2/lib/core/state/mutation.dart]`
  12. `[x]` `@[client_app_v2/lib/core/theme/app_spacing.dart]`
  13. `[x]` `@[client_app_v2/lib/core/ui/error_view.dart]`
  14. `[x]` `@[client_app_v2/lib/core/ui/splash_screen.dart]`
  15. `[x]` `@[client_app_v2/lib/core/utils/safe_isolate.dart]`
  16. `[x]` `@[client_app_v2/lib/utils/json_converters.dart]`
  17. `[x]` `@[client_app_v2/lib/utils/riverpod_extensions.dart]`
  18. `[x]` `@[client_app_v2/lib/shared/models/i18n_text.dart]`
  19. `[x]` `@[client_app_v2/lib/shared/models/sdui_block_dto.dart]`
  20. `[x]` `@[client_app_v2/lib/features/settings/domain/models/app_settings_state.dart]`

---

### Askel 5.2: Frontend Karkaisuaalto F2 — Freezed Domain & DTO Models + Riverpod Controllers & Providers (44/44 tiedostoa) — [SUORITETTU & LUKITTU]
* **Seurantadokumentti:** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Execution Freezed Models (18 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]`
  2. `[x]` `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`
  3. `[x]` `@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]`
  4. `[x]` `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]`
  5. `[x]` `@[client_app_v2/lib/features/execution/models/execution_metadata.dart]`
  6. `[x]` `@[client_app_v2/lib/features/execution/models/execution_metrics_dto.dart]`
  7. `[x]` `@[client_app_v2/lib/features/execution/models/execution_record.dart]`
  8. `[x]` `@[client_app_v2/lib/features/execution/models/execution_step.dart]`
  9. `[x]` `@[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart]`
  10. `[x]` `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]`
  11. `[x]` `@[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]`
  12. `[x]` `@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]`
  13. `[x]` `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`
  14. `[x]` `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]`
  15. `[x]` `@[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]`
  16. `[x]` `@[client_app_v2/lib/features/execution/models/tda_state.dart]`
  17. `[x]` `@[client_app_v2/lib/features/execution/models/trace_context_carrier.dart]`
  18. `[x]` `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]`
* **Paketti 2 — Studio & Reports Freezed Models + Cloner Utils (14 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/features/reports/models/report_artifact.dart]`
  2. `[x]` `@[client_app_v2/lib/features/studio/models/blueprint_config.dart]`
  3. `[x]` `@[client_app_v2/lib/features/studio/models/gcp_location.dart]`
  4. `[x]` `@[client_app_v2/lib/features/studio/models/llm_platform.dart]`
  5. `[x]` `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`
  6. `[x]` `@[client_app_v2/lib/features/studio/models/model_config.dart]`
  7. `[x]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]`
  8. `[x]` `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`
  9. `[x]` `@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`
  10. `[x]` `@[client_app_v2/lib/features/studio/models/step_simulation.dart]`
  11. `[x]` `@[client_app_v2/lib/features/studio/models/workflow.dart]`
  12. `[x]` `@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]`
  13. `[x]` `@[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart]`
  14. `[x]` `@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]`
* **Paketti 3 — Riverpod Controllers & State Providers (12 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`
  2. `[x]` `@[client_app_v2/lib/features/execution/providers/atom_result_provider.dart]`
  3. `[x]` `@[client_app_v2/lib/features/execution/providers/hydrated_reference_provider.dart]`
  4. `[x]` `@[client_app_v2/lib/features/execution/providers/report_data_v2_provider.dart]`
  5. `[x]` `@[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart]`
  6. `[x]` `@[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`
  7. `[x]` `@[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]`
  8. `[x]` `@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]`
  9. `[x]` `@[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart]`
  10. `[x]` `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]`
  11. `[x]` `@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]`
  12. `[x]` `@[client_app_v2/lib/features/studio/controllers/studio_controller.dart]`

---

### Askel 5.3: Frontend Karkaisuaalto F3 — Execution, Reports & Shared SDUI / Presentation Widgets (47/47 tiedostoa) — [SUORITETTU & LUKITTU]
* **Seurantadokumentti:** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Execution & Reports Views and SDUI Widgets (21 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`
  2. `[x]` `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`
  3. `[x]` `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]`
  4. `[x]` `@[client_app_v2/lib/features/execution/views/execution_view.dart]`
  5. `[x]` `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`
  6. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]`
  7. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/diagnostic_scorecard_widget.dart]`
  8. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]`
  9. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]`
  10. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart]`
  11. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_alert_box_widget.dart]`
  12. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]`
  13. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`
  14. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_grid_widget.dart]`
  15. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`
  16. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_node_renderer.dart]`
  17. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]`
  18. `[x]` `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]`
  19. `[x]` `@[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]`
  20. `[x]` `@[client_app_v2/lib/features/reports/views/execution_reports_view.dart]`
  21. `[x]` `@[client_app_v2/lib/features/reports/views/widgets/report_artifact_card.dart]`
* **Paketti 2 — Shared Cross-Domain Widgets (`client_app_v2/lib/shared/widgets/`, 26 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]`
  2. `[x]` `@[client_app_v2/lib/shared/widgets/comparison_matrix.dart]`
  3. `[x]` `@[client_app_v2/lib/shared/widgets/deep_dive_expander.dart]`
  4. `[x]` `@[client_app_v2/lib/shared/widgets/dynamic_form.dart]`
  5. `[x]` `@[client_app_v2/lib/shared/widgets/execution_timeline.dart]`
  6. `[x]` `@[client_app_v2/lib/shared/widgets/feedback_section.dart]`
  7. `[x]` `@[client_app_v2/lib/shared/widgets/file_input_field.dart]`
  8. `[x]` `@[client_app_v2/lib/shared/widgets/file_uploader.dart]`
  9. `[x]` `@[client_app_v2/lib/shared/widgets/generic_grid.dart]`
  10. `[x]` `@[client_app_v2/lib/shared/widgets/global_error_view.dart]`
  11. `[x]` `@[client_app_v2/lib/shared/widgets/log_viewer.dart]`
  12. `[x]` `@[client_app_v2/lib/shared/widgets/logic_matrix_chart.dart]`
  13. `[x]` `@[client_app_v2/lib/shared/widgets/logic_radar_chart.dart]`
  14. `[x]` `@[client_app_v2/lib/shared/widgets/omni_input_box.dart]`
  15. `[x]` `@[client_app_v2/lib/shared/widgets/output_renderer.dart]`
  16. `[x]` `@[client_app_v2/lib/shared/widgets/pdf_export_guide_dialog.dart]`
  17. `[x]` `@[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]`
  18. `[x]` `@[client_app_v2/lib/shared/widgets/quadrant_matrix_chart.dart]`
  19. `[x]` `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`
  20. `[x]` `@[client_app_v2/lib/shared/widgets/schema_mapper.dart]`
  21. `[x]` `@[client_app_v2/lib/shared/widgets/score_card.dart]`
  22. `[x]` `@[client_app_v2/lib/shared/widgets/score_card_radar.dart]`
  23. `[x]` `@[client_app_v2/lib/shared/widgets/specialist_section.dart]`
  24. `[x]` `@[client_app_v2/lib/shared/widgets/unified_metric_gauge.dart]`
  25. `[x]` `@[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]`
  26. `[x]` `@[client_app_v2/lib/shared/widgets/workflow_selector.dart]`

---

### Askel 5.4: Frontend Karkaisuaalto F4 — Quorum Studio Master Views, Profile Block Editors & Workflow Canvas Widgets (53/53 tiedostoa) — [SUORITETTU & LUKITTU]
* **Seurantadokumentti:** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Studio Master Views & Core Components (16 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]`
  2. `[x]` `@[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]`
  3. `[x]` `@[client_app_v2/lib/features/studio/views/components/clone_entity_button.dart]`
  4. `[x]` `@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]`
  5. `[x]` `@[client_app_v2/lib/features/studio/views/matrix_editor_view.dart]`
  6. `[x]` `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`
  7. `[x]` `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]`
  8. `[x]` `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`
  9. `[x]` `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`
  10. `[x]` `@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]`
  11. `[x]` `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]`
  12. `[x]` `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]`
  13. `[x]` `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]`
  14. `[x]` `@[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]`
  15. `[x]` `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`
  16. `[x]` `@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]`
* **Paketti 2 — Studio Widgets, Dialogs & Workflow Tabs (21 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/contrastive_pair_editor.dart]`
  2. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/dag_canvas_view.dart]`
  3. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/dynamic_item_list_editor.dart]`
  4. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/expected_input_editor_box.dart]`
  5. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]`
  6. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/inspector_pane.dart]`
  7. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/linguistic_shield_banner.dart]`
  8. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]`
  9. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/prompt_preview_dialog.dart]`
  10. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]`
  11. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`
  12. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]`
  13. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart]`
  14. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/tag_chip_input.dart]`
  15. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart]`
  16. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_inputs_tab.dart]`
  17. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]`
  18. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]`
  19. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]`
  20. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/xai/fallback_error_card.dart]`
  21. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/xai/matrix_observability_accordion.dart]`
* **Paketti 3 — Output Profile Block Cards & Tabs (16 tiedostoa):**
  1. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]`
  2. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]`
  3. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]`
  4. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart]`
  5. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`
  6. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]`
  7. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]`
  8. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]`
  9. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]`
  10. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/variance_block_card.dart]`
  11. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]`
  12. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]`
  13. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]`
  14. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]`
  15. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]`
  16. `[x]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart]`
* **Laatuvarmennus (Kaikki Frontend-aallot F1–F4):**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

### Askel 5.5: Uusien Laatuporttien (`d44a5e77b`) Täyden Työtilan SHA-256 Uudelleenkarkaisu (`Yöajot 1–4`)
* **Tavoite:** Commitissa `d44a5e77b` (*feat(governance): add tenant rbac, uow concurrency, async blocking, and 1-hop parity gates*) koodikantaan lisättiin uudet laatuportit (Tenant RBAC -eristys, `UnitOfWork`-rinnakkaisuussäännöt, asynkronisen tapahtumasilmukan blokkauksen esto sekä 1-Hop DTO-pariteetti), mikä päivitti `.agents/rules/`-tiivisteen tiedostossa `@[data/hardening_cache.json]`. Seuraavat 4 ajoa (`Yöajot 1–4`) päivittävät SHA-256-karkaisuvälimuistin koko työtilan osalta:
* **Yöajo 1 — Backend Services, LLM & Hooks (`201` kohdetta; `191/201` välimuistissa, `10` jäljellä):**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --targets backend_v2/services backend_v2/llm backend_v2/hooks --gate backend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Yöajo 2 — Backend Models, Routers, Database, Core & Utils (`190` kohdetta; `72/190` välimuistissa, `118` jäljellä):**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --targets backend_v2/models backend_v2/api backend_v2/database backend_v2/core backend_v2/utils --gate backend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Yöajo 3 — Frontend Flutter (`client_app_v2/lib`, `201` kohdetta; `114/201` välimuistissa, `87` jäljellä):**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --targets client_app_v2/lib --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Yöajo 4 — Loput työtilasta (`--discover`, kattaa `backend_v2/workers`, `backend_v2/seed`, juuren `backend_v2/*.py` sekä `scripts/*.py`, `39` jäljellä Yöajojen 1–3 jälkeen; koko työtilassa yhteensä `254` jäljellä):**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --discover --gate all --model gemini-4-argon-medium --continue-on-failure
  ```

---

### Askel 6: Kooditason GCP Cloud Run -valmius (`TRACKER_GCP_Production_Deployment.md` — [100 % SUORITETTU, KOVENNETTU 5/5 & AUDITOITU]) sekä Ohjattu GCP-pilviinmeno (`TRACKER_GCP_Guided_Cloud_Cutover.md`) (Vaihe 5)
* **Osa 1 — Kooditason GCP Cloud Run -valmius (`@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` & `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`) — 🟢 [100 % SUORITETTU, KOVENNETTU 5/5, SYNKRONOITU & AUDITOITU]:**
  * Toteutettu Vaiheet 1–4 (commitit `15784637f`, `64b1962e0`, `d0bb7722a`, `d732f4898`), karkaistu `5/5` kohdetta (`@[backend_v2/settings.py]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/api/routers/system/health.py]`, `@[backend_v2/main.py]`, `@[backend_v2/run_worker.py]`), synkronoitu arkkitehtuuridokumentaatioon (`/tier7-describe-architecture`, `0105e08d8`) ja auditoitu (`/tier8-audit-plan`, `fa10bdb44`):
    1. **`@[backend_v2/settings.py]`:** `strip_trailing_slash`-normalisointi, `app_version`, `port`, `worker_health_port`, `gcp_project_id`, `gcp_region`, `primary_domain = "qrum.ai"`, `jwt_issuer`, `jwt_audience` ja tuotannon `cors_origins`-lukitus.
    2. **`@[backend_v2/models/dtos/system.py]` & `@[backend_v2/api/routers/system/health.py]`:** `HealthCheckResponseDTO` ja `GET /api/v2/system/health` (asynkroninen PostgreSQL 19 `SELECT 1` + Redis `PING` < 10 ms).
    3. **`@[backend_v2/run_worker.py]` & `@[backend_v2/Dockerfile]`:** Taustatyöntekijän `_handle_health_probe` (`worker_health_port`) sekä monivaiheinen ei-root (`UID 10001`) `.venv`-tuotantokontti kaikilla WeasyPrintin Linux C -kirjastoilla ja fonteilla (`libpango-1.0-0`, `libharfbuzz0b`, `libpangoft2-1.0-0`, `libgdk-pixbuf-2.0-0`, `libcairo2`, `libffi-dev`, `shared-mime-info`, `fonts-liberation`, `fonts-noto-core`).
* **Osa 2 — Ohjattu GCP-pilviinmeno ja `qrum.ai` Cutover (`@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`, `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` & `[NEW] @[scripts/provision_gcp_cloud.py]`) — [SEURAAVA TUOTANTOASKEL]:**
  * Toteuta ensin Vaiheet 1–2 (`[NEW] @[scripts/provision_gcp_cloud.py]` ja `@[docker-compose.yml]`-siivous) komennolla `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`, ja provisioi sen jälkeen GCP `europe-north1` -resurssit (Cloud SQL PostgreSQL 19, Memorystore Redis, GCP Secret Manager, Artifact Registry, Cloud Run Job `quorum-seed` `SECRET_VERTEX_AI_SA_JSON`-alustuksella, Cloud Run `quorum-api` & `quorum-worker`, Resend EU `HTTP_API`, Firebase Auth TOTP + Web Hosting SPA-uudelleenohjaukset `/task/**` ja `/invite/**` sekä Google-Managed SAN SSL `qrum.ai` / `api.qrum.ai` / `app.qrum.ai` / `studio.qrum.ai`):
  ```powershell
  # Vaiheiden 1-6 ohjattu pilviprovisiointi (--check diagnostiikkatilassa tai --apply toteutustilassa):
  uv run python scripts/provision_gcp_cloud.py --project-id cognitive-quorum --region europe-north1 --stage all --check
  ```

---

### Askel 6.1: Cloud Security & FinOps Infrastructure Hardening (GCP europe-north1) (Vaihe 5b)
* **Tavoite ja Arkkitehtoninen Rooli:**
  Ennen julkisen verkkoliikenteen avaamista `qrum.ai`-osoitteelle karkaistaan GCP europe-north1 -tuotantoympäristön verkkoturvallisuus, WAF-säännöt, pienimmät riittävät käyttöoikeudet (Least Privilege IAM), VPC-eristys, hälytyskanavat ja kustannuskatot (FinOps Circuit Breakers).
* **Laajuus & Kesto:** Pilvi-infrastruktuurin auditointi ja verifiointi, kestoarvio **~1 h**.
* **Karkaisualueet:**
  1. **Cloud Armor WAF & Rate Limiting:** Konfiguroidaan DDoS-suojaus, HTTP Flood -rajoittimet ja SQLi/XSS-suodattimet kuormantasaajassa (`quorum-lb`).
  2. **Least Privilege IAM Audit:** Varmistetaan, että Cloud Run -palvelutilillä (`quorum-api-sa`) on ainoastaan:
     * `roles/secretmanager.secretAccessor` (vain vaadituille salaisuuksille)
     * `roles/cloudsql.client`
     * `roles/storage.objectAdmin` (vain `quorum-prod-uploads`- ja `quorum-prod-reports`-säilöille)
     * 0 kpl laajoja projektitason ylläpito-oikeuksia.
  3. **VPC Private IP Firewall -sulku:** Varmistetaan, että Cloud SQL PostgreSQL 19 ja Memorystore Redis eivät omaa julkista IP-osoitetta (`public_ip = false`) ja sallivat yhteydet ainoastaan sisäisen `quorum-vpc-connector`:in kautta.
  4. **FinOps Token & Cost Circuit Breakers:** Verifioidaan Redis-pohjaiset TPM/RPM-katot ja hälytysrajat GCP Billing Alertseissa estämään hallitsemattomat tekoälykulut.
  5. **Cloud Monitoring & Error Reporting -hälytyskanavat:** Konfiguroidaan reaaliaikaiset hälytykset kehitystiimin sähköpostiin/Slackiin odottamattomista HTTP 5xx -virhepiikeistä, Cloud SQL CPU/tallennustilahälytyksistä (>80%) sekä LLM-kiintiöiden lähestymisestä OpenTelemetry / Logfire -integraation rinnalle.
* **Todennuskomento:**
  ```powershell
  gcloud compute security-policies describe quorum-armor-policy --project=quorum-prod
  gcloud sql instances describe quorum-pg19 --format="value(ipAddresses)"
  uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  ```

---

### Askel 6.2: Lopullinen Full-Stack E2E Go-Live -Todennusportti (Pre-Launch Production Verification Gate) (Vaihe 5c)
* **Tavoite ja Arkkitehtoninen Rooli:**
  Aivan kuten ennen PostgreSQL-migraatiota suoritettiin täydellinen päästä päähän -todennusajo (`exe_2af2f7665e7c477b`), ennen tuotantoliikenteen avaamista ajetaan ja dokumentoidaan **koko uuden 2026 tuotantopinon kattava Full-Stack E2E Go-Live -todennusajo** (`/tier6-execution-monitor` + forensiikkaraportti).
* **Todennettavat 5 tuotantoketjun vaihetta (100 % E2E Pariteetti):**
  1. **Vaihe 1 — Pakollinen 2FA (TOTP), RFC 8693 Token Exchange (`EPIC 160`) & Suora `/task/:token` -Tehtäväportaali Resend EU:lla (`Askel 4.6`):**
     * Kirjaudutaan Flutter-asiakkaalla (`app.qrum.ai` / Desktop) sisään 2FA-vahvistuksella (`firebase.sign_in_second_factor`), vaihdetaan token `POST /api/v2/iam/auth/exchange`-rajapinnassa 15 minuutin `Quorum Local JWT`:ksi (`sub: usr_<hex32>`, `org: org_<hex32>`, `mfa: true`) ja varmistetaan `< 0,1 ms` RAM-validointi; luodaan lisäksi `TaskBrief` (`_TaskBriefsManagementCard`) ja lähetetään Resend EU (`HTTP_API`) -tehtävänanto (`Open Quorum Portal` CTA -> `https://app.qrum.ai/task/<raw_token>`), todennetaan ulkoisen osallistujan JIT-onboarding + portaalin sisäinen TOTP-aktivointi (`task_portal_totp_secret_text`), `task_portal_task_brief_card`-näkymä ja liitetiedoston välitön tekstipurku.
  2. **Vaihe 2 — Monikanavainen Ingressi & Cloud Storage (`GCSFileDriver` / Direct-to-Cloud Signed URLs):**
     * Ladataan syötetiedostot (`lopputuote.pdf`, `keskusteluhistoria.pdf`, `reflektiodokumentti.pdf`) joko suoraan Eager Extraction -ingressillä (< 32 MB) tai 15 minuutin Signed PUT URL -putkella (`POST /api/v2/files/upload-request` -> PUT -> `POST /api/v2/files/{id}/confirm`).
  3. **Vaihe 3 — DAG-suoritus, Kausaaligraafi & Asynkroninen Synteesi Natiivilla PostgreSQL 19 `UUIDv7` -kannalla (Askel 3.3):**
     * Suoritetaan koko moniaskeleinen työnkulku, jossa kaikki 15 taulua käyttävät natiivia 16-tavuista `UUIDv7`-avainta (`{prefix}_{32_hex}`), `execution_worker.py` ja `report_worker.py` kommunikoivat Redisin ja PostgreSQL 19:n kautta, ja BYOK `SecretService` injektoi avaimet pyyntökohtaisesti ilman lokivuotoja.
  4. **Vaihe 4 — Monikanavainen Raporttikoonti & Flutter SDUI Dumb Painter:**
     * Verifioidaan tuotetut artefaktit: 9-sivuinen WeasyPrint `report.pdf` (mukaan lukien ääkköset ja vektorikaaviot), `report.sdui.json`, `report.xlsx` ja `report.csv`, sekä tarkistetaan Flutter Web- ja Desktop -näkymissä `HTTP 200 OK` ilman yhtäkään deserialisointi- tai teemavirhettä.
  5. **Vaihe 5 — Turva- ja FinOps-katkaisijoiden (Kill-Switch & Quota) Koeponnistus:**
     * Todennetaan, että käyttäjän mitätöinti (`revoked:usr:<id>`) katkaisee pääsyn välittömästi (`401 Unauthorized` < 1 ms), ja että FinOps-kiintiön tai RPM/TPM-rajan ylitys palauttaa hallitun RFC 7807 -virheen (`429 Too Many Requests` / `QUOTA_EXHAUSTED`).
* **Todennus- ja lukituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

# Session Handover Context

## Achieved
* Completed **Targeted Backend Hardening Waves 1–4 (`133/133` targets)**, **Frontend Targeted Hardening Waves F1–F4 (`185/185` targets)**, and **Storage Driver Hardening (`3/3`: `file_driver.py`, `local_file_driver.py`, `gcs_file_driver.py` in commits `fa940a23f`–`85a7721ea`)**.
* Completed, hardened, synchronized (`/tier7-describe-architecture`), and audited (`/tier8-audit-plan` / `/tier8-audit-epic`) **Askeleet 3.3–3.7**:
  1. **Askel 3.3 (`PrefixedUUID7` & `UUIDv4` Eradication):** `15/15` + `31/31` targets hardened & locked (`QGR030` & `DGR008`).
  2. **Askel 3.4 (AST Guardrails `QGR020`/`QGR031`–`QGR033` & SHA-256 Hardening Cache):** Commit `df0518f8c`.
  3. **Askel 3.4b (Router SSOT Consolidation & Universal `CRUD + Clone` Lifecycle Guard):** `22/22` targets hardened (`b62b65d47`, `ee38118ed`), E2E verified in `exe_01a18ecef54372d39c31ef9fb1f12937`.
  4. **Askel 3.4c (`EPIC 161: Topological Intelligence Preservation Across Distillation, Synthesis & SDUI Reporting`):** `31/31` Backend + `5/5` Frontend targets hardened, Tier 7 (`81853a38e`) & Tier 8 (`83f11d369`).
  5. **Askel 3.5 (`PostgresEntityAdapter` 6-Stage Zero-ORM Package Decomposition):** `9/9` hardened, `100%` line coverage (`730/730` statements), `QGR017`-locked, Tier 7 (`fb94d8dbe`) & Tier 8 (`a7a5ac6c7`).
  6. **Askel 3.6 (`EPIC 162: Studio Target Sync, CognitiveTier SSOT & DAG OCC Resilience`):** `31/31` targets hardened, Tier 7 (`9066bc8ab`), Tier 8 audited, and E2E verified in `exe_01a19ad8c8807129955f7c2e90d12a52`.
  7. **Askel 3.7 (`EPIC 163: Residual Guardrail Exemption Eradication, JsonValue & Open-JSON Eradication, and InMemoryUnitOfWork Worker Test Migration`):** All 7 phases (`30aba5589`–`fbe6e1b33`), `53/53` targets hardened, `Census F = 0`, Tier 7 synced, and Tier 8 audited (`@[docs/epic/EPIC_163_audit_report.md]`).
* Completed, hardened, synchronized (`/tier7-describe-architecture`), and audited (`/tier8-audit-epic` / `/tier8-audit-plan`) **Askel 4 (`EPIC 160` `51/51`)** and **Askeleet 4.1–4.6**:
  1. **Askel 4 (`EPIC 160: B2B SaaS IAM, Token Exchange & Enterprise Hardening`):** `51/51` hardened (`f9f9e6f53`), Tier 7 (`3402d327b`) & Tier 8 (`71b5247c6`).
  2. **Askeleet 4.1–4.4 (`BYOK PostgreSQL 19 Persistence`, `MCP Draft 2020-12 Schema`, `LLM BYOK Runtime Wiring`, `100% DB-Only Secret SSOT & Vertex AI BYOK`):** `14/14` + `19/19` hardened, `91/91` DTO wire parity verified (`audit_dto_parity.py`), and E2E verified in `exe_01a1c086576272b7a33c508d27277e94` (`rep_01a1c08a762d70b8b3b7c2fae8fcf6da`).
  3. **Askel 4.5 (`EPIC 164: Unified Secret Seeding, SecretScope.TELEMETRY, Startup DB Logfire/Firebase Admin Initialization & Zero Mock Login`):** Phases 1–4 (`e31d46648`–`7df1c8daf`), `17/17` hardened (`011e39713`–`abc0328e1`), Tier 7 synced, and Tier 8 audited (`80f1a3116`, `@[docs/epic/EPIC_164_audit_report.md]`).
  4. **Askel 4.6 (`Task Assignment, Task Brief CRUD+Clone & Direct Portal End-to-End Hardening — Findings A–E`):** Phases 1–4 (`f50520284`, `e025b1e30`, `7bac2dc99`, `c21fca8d6`), `14/14` hardened (`9/9` Backend + `5/5` Frontend, `a93056dea`–`08385c09b`), `92/92` DTO parity (`audit_dto_parity.py`), `1,387` passing Flutter tests, Tier 7 synced, and Tier 8 audited (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]`, `@[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]`).
* Completed, hardened (`5/5`), synchronized (`0105e08d8`), and audited (`fa10bdb44`) **Askel 6 Code-Level GCP Cloud Run Readiness (`@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` & `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`)** and synchronized the Guided Cloud Cutover playbook (`@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`, `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`, `[NEW] @[scripts/provision_gcp_cloud.py]`) with `EPIC 164` and `Askel 4.6`.

## Learned
* Both `StrictOpaqueIdConverter` on the Flutter client and `OPAQUE_STRIPE_ID_REGEX` / `PostgresEntityAdapter` on the Python backend enforce 32-hex RFC 9562 `UUIDv7` identifiers (`^[a-z]{2,5}_[a-f0-9]{32}$` with version nibble `7`), guarded statically by `QGR030` (`@[scripts/_ast_guardrails.py]`) and `DGR008` (`@[scripts/_dart_guardrails.py]`).
* `EPIC 163` eradicated all `RESIDUAL_*` exemption sets in `@[scripts/_ast_guardrails.py]` and `per-file-ignores` in `@[pyproject.toml]`, locked `QGR020` Check 20B/20C, `QGR027`, `QGR028`, `DGR005`, `DGR013`, `DGR014`, and migrated all worker unit tests to stateful `InMemoryUnitOfWork` (`Census F = 0`).
* `EPIC 164` unified local and production secret seeding via `SecretScope.TELEMETRY`, `.env.secrets.local` (`LocalSeedSecretsSettings`), startup database resolution for Logfire (`resolve_startup_logfire_token`) and Firebase Admin SDK (`initialize_firebase_admin_from_secrets`), and 100% authentic Email/Password + backend MFA IAM parity with zero `service-account.json` files or mock login bypasses.
* `Askel 4.6` (`Task_Assignment_Portal_Hardening`) aligned `EmailService` strictly with Resend EU's canonical 5-key REST schema (`from`, `to`, `subject`, `html`, `tags`) with HTML-escaped `"Open Quorum Portal"` CTA links, normalized `execution_assignments.task_brief_id` (`ZORM004`/`ZORM006`/`ZORM007`) and `TaskAssignmentBriefDTO`/`TaskAssignmentBriefDto` (`92/92` DTO parity), enabled eager `Base64Attachment` portal file extraction on `/draft` and `/submit`, ordered `_verify_onboarding_firebase_token` so `IDENTITY_MISMATCH` runs before `fb_auth.update_user(..., email_verified=True)` and `_enforce_firebase_mfa_claim`, handled Firebase Email Enumeration Protection (`'invalid-credential'`) in `authenticateForTaskOnboarding`, and typed `organizationTaskBriefsProvider` as `Future<List<PromptBlock>>` (`.whereType<TaskDefinitionPromptBlock>()`) for `riverpod_generator ^4.0.0` Freezed union compatibility.
* Code-level Cloud Run readiness (`HealthCheckResponseDTO`, `GET /api/v2/system/health`, `run_worker.py` `_handle_health_probe`, and non-root `UID 10001` `.venv` `Dockerfile` with WeasyPrint C libraries) is 100% complete and audited (`fa10bdb44`).

## Resume Command
```text
/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]
```

## Remaining
### Hardening & Cutover State Snapshot
* **Full-Workspace Governance Re-Hardening (`Yöajot 1–4`, Askel 5.5):** Complete the remaining SHA-256 hardening cache updates triggered by the `d44a5e77b` governance rules (`254` files total: `10` files in Yöajo 1, `118` files in Yöajo 2, `87` files in Yöajo 3, and `39` files in Yöajo 4).
* **Optional Direct-to-Cloud Signed URLs (`Askel 5`):** Current file ingress (Base64 Amnesia Eager Extraction at ingress) and report artifact storage (`GCSFileDriver` / `LocalFileDriver` + `report_binaries`) are 100% implemented and hardened (`3/3`). Implement `IMPLEMENTATION_PLAN_Storage_Signed_URLs.md` if >32 MB direct browser-to-GCS PUT Signed URL uploads and the 16th `file_metadata` table are needed.
* **Immediate Next Production Task (`Askel 6.0b`):** Execute Steps 1–2 and the Guided Cloud Cutover (`@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` / `[NEW] @[scripts/provision_gcp_cloud.py]`), followed by Cloud Armor WAF & FinOps verification (**Askel 6.1**) and the Pre-Launch Full-Stack E2E Go-Live Gate (**Askel 6.2**).
