# Arkkitehtuurin ja Tietomallien Parannuskohteet

Tähän dokumenttiin on koottu järjestelmän koodikannassa, tietomalleissa ja laatuporteissa **avoinna ja toteuttamatta olevat** arkkitehtuuriset parannuskohteet, karkaisuaallot ja skeeman yhtenäistykset. Dokumentti noudattaa *The e.g. Ban* -sääntöä (`anti_ambiguity_mandate`), *No Hidden Scope* -periaatetta sekä Quorumin *Zero-Tolerance* -laatuvaatimusta ilman siirtymäajan purkkaratkaisuja.

*(Huomautus: Aiemmin tässä dokumentissa olleet matriisiskaalauksen keskitys `computed_min`/`computed_max`, `theory_grounding` vs. `ai_description` -eriyttäminen, `I18nText.default_locale`-poisto, `MatrixClaim.ai_description` -> `TDAAssertion.concept_description` -keskitys, `OutputProfile.matrix_synthesis_groups` & L10n-siivous sekä Karkaisuaalto 1 ja Karkaisuaallon 2 ensimmäiset 21 tiedostoa on toteutettu ja poistettu tästä työlistasta.)*

---

## Luku 1: Backend-koodikannan Jäljellä Oleva Karkaisujärjestys (Aallot 2–4: 76 Tiedostoa)
> **STATUS: KÄYNNISSÄ (Aalto 1 [36/36] ja Aalto 2:n alkuosa [21/36] valmiit; 76 karkaistavaa tiedostoa jäljellä)**
> *Selite: Synkronoitu päätoteutussuunnitelman `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]` (Askeleet 3.2b – 3.2d) kanssa.*

### 1.1 Koko `backend_v2/`-Tuotantokoodikannan Tilannekuva (403 `.py`-tiedostoa)

Koko `backend_v2/`-hakemiston (pl. `tests/`) 403 tuotantotiedoston tilannekuva:

| Kategoria | Tiedostomäärä | Tila ja seurantadokumentti |
| :--- | :--- | :--- |
| **1. Valmiiksi karkaistut ja lukitut tuotantotiedostot** | `315` kpl | Sisältää `__init__.py`-fasaadit (`47` kpl), aiemmissa puruissa karkaistut moduulit (`162` kpl), entuudestaan 100 % puhtaat tiedostot (`49` kpl), valmistuneen Karkaisuaallon 1 (`36` kpl) sekä Karkaisuaallon 2 valmistuneet tiedostot (`21` kpl). |
| **2. Karkaisuaalto 2 — Jäljellä olevat (LLM Adapters & Studio/Execution Services)** | `15` kpl | `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]` (tiedostot 22–36) |
| **3. Karkaisuaalto 3 — Repositories, Orchestrator & Routers** | `27` kpl | `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]` |
| **4. Karkaisuaalto 4 — Domain Models & DTO Schemas** | `34` kpl | `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]` |
| **5. Tulevat arkkitehtuurivaiheet (IAM & Storage)** | `12` kpl | Eristetty vaiheisiin `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` (9 tiedostoa) ja `@[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]` (3 tiedostoa). |
| **YHTEENSÄ** | **403 kpl** | **315 / 403 valmiina, 76 kpl karkaisuaalloissa 2–4, 12 kpl IAM/Storage-vaiheissa** |

---

### 1.2 Jäljellä Olevien Karkaisuaaltojen Etenemisjärjestys (Bottom-Up Dependency Order)

#### Aalto 2: Jäljellä olevat 15 tiedostoa — `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`
*(Paketit 1 ja 2 [18 tiedostoa] sekä Paketin 3 tiedostot `directives.py`, `prompt_builder.py` ja `deepseek_adapter.py` [3 tiedostoa] ovat valmiit ja commitoitu.)*

* **Paketti 3 — LLM Provider Adapters (jäljellä 5 tiedostoa):**
  1. `@[backend_v2/llm/adapters/mock_adapter.py]`
  2. `@[backend_v2/llm/adapters/adapter_factory.py]`
  3. `@[backend_v2/llm/adapters/anthropic_adapter.py]`
  4. `@[backend_v2/llm/adapters/openai_adapter.py]`
  5. `@[backend_v2/llm/adapters/ai_studio_adapter.py]`
* **Paketti 4 — Studio, Ingress & Execution Services (10 tiedostoa):**
  1. `@[backend_v2/services/web_fetcher.py]`
  2. `@[backend_v2/services/ingress/multi_channel_ingress_service.py]`
  3. `@[backend_v2/services/source_verification_service.py]`
  4. `@[backend_v2/services/factories/output_profile_factory.py]`
  5. `@[backend_v2/services/studio/auth_validator.py]`
  6. `@[backend_v2/services/studio/prompt_block_service.py]`
  7. `@[backend_v2/services/studio/output_profile_service.py]`
  8. `@[backend_v2/services/execution/context_service.py]`
  9. `@[backend_v2/services/execution/resumption_service.py]`
  10. `@[backend_v2/services/execution/override_service.py]`
* **Suorituskomento (jatkaa automaattisesti tiedostosta `mock_adapter.py`):**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md --gate backend --model gemini-4-argon-medium --continue-on-failure
  ```

#### Aalto 3 (27 tiedostoa) — `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`
* **Paketti 1 — Repository & Persistence Layer (11 tiedostoa):**
  1. `@[backend_v2/database/repository.py]`
  2. `@[backend_v2/database/repositories/component.py]`
  3. `@[backend_v2/database/repositories/report_artifact.py]`
  4. `@[backend_v2/database/repositories/components/agent.py]`
  5. `@[backend_v2/database/repositories/components/execution_persona.py]`
  6. `@[backend_v2/database/repositories/components/extraction_protocol.py]`
  7. `@[backend_v2/database/repositories/components/matrix.py]`
  8. `@[backend_v2/database/repositories/components/output_profile.py]`
  9. `@[backend_v2/database/repositories/components/prompt_block.py]`
  10. `@[backend_v2/database/repositories/components/role.py]`
  11. `@[backend_v2/database/repositories/components/task_blueprint.py]`
* **Paketti 2 — Orchestrator & Schema Services (6 tiedostoa):**
  1. `@[backend_v2/services/orchestrator/schema_factory.py]`
  2. `@[backend_v2/services/orchestrator/chunking_service.py]`
  3. `@[backend_v2/services/orchestrator/atomizer.py]`
  4. `@[backend_v2/services/orchestrator/dag_compiler.py]`
  5. `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`
  6. `@[backend_v2/services/orchestrator/enriched_dag_executor.py]`
* **Paketti 3 — FastAPI Routers: System, Studio & Execution (10 tiedostoa):**
  1. `@[backend_v2/api/routers/system/health.py]`
  2. `@[backend_v2/api/routers/system/telemetry.py]`
  3. `@[backend_v2/api/routers/system/configs.py]`
  4. `@[backend_v2/api/routers/output_profiles.py]`
  5. `@[backend_v2/api/routers/studio/model_registry.py]`
  6. `@[backend_v2/api/routers/studio/prompt_blocks.py]`
  7. `@[backend_v2/api/routers/studio/system_configs.py]`
  8. `@[backend_v2/api/routers/studio/workflows.py]`
  9. `@[backend_v2/api/routers/execution/workflows.py]`
  10. `@[backend_v2/api/routers/execution/reports.py]`
* **Suorituskomento:**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md --gate backend --model gemini-4-argon-medium --continue-on-failure
  ```

#### Aalto 4 (34 tiedostoa) — `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`
* **Paketti 1 — Domain Models (`backend_v2/models/domain/`) (23 tiedostoa):**
  1. `@[backend_v2/models/domain/base.py]`
  2. `@[backend_v2/models/domain/metadata.py]`
  3. `@[backend_v2/models/domain/usage.py]`
  4. `@[backend_v2/models/domain/references.py]`
  5. `@[backend_v2/models/domain/retrieval.py]`
  6. `@[backend_v2/models/domain/hydration.py]`
  7. `@[backend_v2/models/domain/interaction.py]`
  8. `@[backend_v2/models/domain/integrity.py]`
  9. `@[backend_v2/models/domain/archivist.py]`
  10. `@[backend_v2/models/domain/causal.py]`
  11. `@[backend_v2/models/domain/coach.py]`
  12. `@[backend_v2/models/domain/evaluation.py]`
  13. `@[backend_v2/models/domain/falsifier.py]`
  14. `@[backend_v2/models/domain/judge.py]`
  15. `@[backend_v2/models/domain/knowledge.py]`
  16. `@[backend_v2/models/domain/logician.py]`
  17. `@[backend_v2/models/domain/overseer.py]`
  18. `@[backend_v2/models/domain/performativity.py]`
  19. `@[backend_v2/models/domain/profiler.py]`
  20. `@[backend_v2/models/domain/scoring.py]`
  21. `@[backend_v2/models/domain/source_verification.py]`
  22. `@[backend_v2/models/domain/synthesis.py]`
  23. `@[backend_v2/models/domain/workflow.py]`
* **Paketti 2 — DTO Schemas & Prompt Models (`backend_v2/models/dtos/` + `models/prompt.py`) (11 tiedostoa):**
  1. `@[backend_v2/models/prompt.py]`
  2. `@[backend_v2/models/dtos/system.py]`
  3. `@[backend_v2/models/dtos/inputs.py]`
  4. `@[backend_v2/models/dtos/prompt.py]`
  5. `@[backend_v2/models/dtos/prompt_context.py]`
  6. `@[backend_v2/models/dtos/retrieval.py]`
  7. `@[backend_v2/models/dtos/evaluation_steps.py]`
  8. `@[backend_v2/models/dtos/schema_manifest.py]`
  9. `@[backend_v2/models/dtos/state.py]`
  10. `@[backend_v2/models/dtos/variance.py]`
  11. `@[backend_v2/models/dtos/workflow_schema.py]`
* **Suorituskomento:**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md --gate backend --model gemini-4-argon-medium --continue-on-failure
  ```

---

## Luku 2: Yhtenäinen `PrefixedUUID7`-tunnistearkkitehtuuri ja Natiivi PostgreSQL 19 `UUIDv7` (Malli A)
> **STATUS: SUUNNITELTU ARKKITEHTUURIN YHTENÄISTYS (Tuleva Cutover)**
> *Selite: Poistaa 16-merkkisen `UUIDv4`-katkaisun ja `TEXT PRIMARY KEY` -hybridijaon yhdistämällä Opaque Stripe ID -etuliitteet ja PostgreSQL 19:n natiivin 16-tavuisen RFC 9562 `UUIDv7` -tietotyypin yhdeksi poikkeuksettomaksi standardiksi.*

### 2.1 Nykytilanne ja kahden rinnakkaisen ID-putken ongelma (Hybrid Split)

Nykyisessä toteutuksessa (`@[backend_v2/models/core_base.py]`, `@[backend_v2/models/enums.py]`, `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` ja `@[backend_v2/database/postgres/entity_adapter.py]`) järjestelmän entiteettitunnisteet on jaettu kahteen erilliseen generointi- ja tallennusmekanismiin:

1. **Aikasarja- ja graafientiteetit (4 etuliitettä, 5 taulua):**
   * Joukko `_UUID7_DELEGATED_PREFIXES` (nimenomaan ja tyhjentävästi: `exe`, `rep`, `nod`, `edg`) generoi 32 heksamerkin pituisen monotonisen RFC 9562 `UUIDv7` -tunnisteen muodossa `{prefix}_{32_hex_uuidv7}`.
   * Nämä tallennetaan PostgreSQL 19 -tietokantaan natiivina 16-tavuisena binäärisenä `UUID PRIMARY KEY DEFAULT uuidv7()` -sarakkeena 5 tauluun (nimenomaan ja tyhjentävästi: `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes`, `quorum_edges`), joita vartioi tietokantatason rajoite `CHECK (uuid_extract_version(id) = 7)`.

2. **Konfiguraatio-, hallinta- ja rakenne-entiteetit (9 etuliitettä + asteikot, 7 taulua):**
   * Kaikki muut `EntityPrefix`-luokan etuliitteet (nimenomaan ja tyhjentävästi: `wf`, `stp`, `sr`, `prf`, `blk`, `sys`, `usr`, `org`, `tda`) sekä `@[backend_v2/seed/seed_data.json]`-tiedoston matriisiasteikkojen `sc`-tunnisteet ja työnkulkujen `wor`-tunnisteet käyttävät 16 heksamerkin pituista `uuid.uuid4().hex[:16]`-katkaisua muodossa `{prefix}_{16_hex}`.
   * Koska 16 heksamerkkiä on vain 64 bittiä (8 tavua), näitä tunnisteita ei voida tallentaa PostgreSQL:n natiiviin 128-bittiseen (16-tavuiseen) `UUID`-sarakkeeseen. Sen vuoksi 7 taulua (nimenomaan ja tyhjentävästi: `organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) käyttää `TEXT PRIMARY KEY` -merkkijonoavaimia.

**Hybridijaon aiheuttamat arkkitehtuuriset haitat:**
* **Säännöllisen lausekkeen väljyys:** `OPAQUE_STRIPE_ID_REGEX` (`r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"`) joutuu sallimaan vaihtelevan heksapituuden välillä 16–32 merkkiä.
* **Ehdollinen haaroitus generoinnissa ja adaptereissa:** `generate_opaque_id()` joutuu tarkistamaan `if prefix_str in _UUID7_DELEGATED_PREFIXES`, ja `@[backend_v2/database/postgres/entity_adapter.py]` käsittelee osan tauluista `$1::uuid`-parametreilla (`parse_prefixed_uuid7` / `format_prefixed_uuid7`) ja osan raakoina `TEXT`-merkkijonoina.
* **Menetetyt natiivit `UUID`-viiteavaimet (`FOREIGN KEY`):** Taulujen `executions` ja `report_artifacts` viiteavaimet konfiguraatiotauluihin (nimenomaan ja tyhjentävästi: `workflow_id`, `active_profile_id`, `output_profile_id`, `profile_id`, `organization_id`) ovat pakotettuja `TEXT`-tyyppiin, koska kohdetaulujen pääavaimet ovat `TEXT`-muotoisia.

---

### 2.2 Tavoitearkkitehtuuri: Malli A (Universal `PrefixedUUID7`)

Kun vanhoja suoritusajoja (`executions`) ei tarvitse säilyttää ja ainoastaan pohjadata `@[backend_v2/seed/seed_data.json]` migroidaan deterministisesti, ID-käsittely yhtenäistetään **Malli A:n** mukaisesti yhdeksi poikkeuksettomaksi putkeksi (`single_pipeline_invariant_mandate`):

```
+-----------------------------------------------------------------------------------+
| 1. SOVELLUS-, DTO-, JSON-, SEED- JA FLUTTER-KERROS (Domain Prefix Safety)         |
|    - Kaikki ID:t ovat poikkeuksetta muotoa: {prefix}_{32_hex_uuidv7}              |
|    - OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"                   |
|    - generate_opaque_id(prefix) -> kutsuu aina generate_uuid7_opaque_id(prefix)   |
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

#### Malli A:n neljä arkkitehtuurista perussääntöä:
1. **Kiinteämittainen 32 heksamerkin RFC 9562 `UUIDv7` kaikkialla:**
   * Jokainen järjestelmän entiteettitunniste koostuu kanonisesta `EntityPrefix`-etuliitteestä, alaviivasta ja tasan 32 pienestä heksamerkistä, jotka edustavat validia 128-bittistä RFC 9562 version 7 UUID-arvoa (`r"^([a-z]{2,5})_[a-f0-9]{32}$"`).
   * Vakio `_UUID7_DELEGATED_PREFIXES`, `length`-parametri sekä `uuid.uuid4().hex[:16]`-haara poistetaan kokonaan tiedostosta `@[backend_v2/models/core_base.py]`.
2. **Etuliitteiden yhtenäistäminen (`EntityPrefix` SSOT):**
   * Työnkulkujen (`workflows`) ja matriisiasteikkojen (`scales`) etuliitteet yhdenmukaistetaan `@[backend_v2/models/enums.py]:EntityPrefix`-luokan ja `@[backend_v2/seed/seed_data.json]`-tiedoston välillä siten, että jokaisella persistoidulla ja sisäkkäisellä entiteetillä on yksikäsitteinen `EntityPrefix`-jäsen (nimenomaan ja tyhjentävästi: `org`, `usr`, `sys`, `blk`, `stp`, `sr`, `wf`, `prf`, `exe`, `rep`, `nod`, `edg`, `tda`, `sc`).
3. **100 % Natiivi `UUID`-skeema kaikissa 12 PostgreSQL 19 -taulussa:**
   * Tiedostossa `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` kaikkien 12 taulun (nimenomaan ja tyhjentävästi: `organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes`, `quorum_edges`) pääavaimet ja keskinäiset relaatioviiteavaimet määritellään tyyppiin `UUID` varustettuna `CHECK (uuid_extract_version(<column>) = 7)` -tarkistuksella.
4. **Symmetrinen muunnos vain tietokanta-adapterin rajalla:**
   * `@[backend_v2/database/postgres/entity_adapter.py]` ja `@[backend_v2/database/postgres/graph_adapter.py]` suorittavat muunnoksen `{prefix}_{32_hex}` <-> `uuid.UUID` (16 tavua) käyttäen funktioita `parse_prefixed_uuid7()` ja `format_prefixed_uuid7()`.
   * JSONB-rakenteiden sisäiset ID-listat (nimenomaan ja tyhjentävästi: `steps.criteria_block_ids`, `workflows.steps`, `output_profiles.target_block_order`, `output_profiles.matrix_synthesis_groups`, `prompt_blocks.scales`, `prompt_blocks.rows`, `prompt_blocks.columns`) säilyvät suoraan `{prefix}_{32_hex}`-muodossa ilman erillistä JSON-puun läpikäyntiä luku- ja kirjoitushetkellä.

---

### 2.3 Miksi Malli A on Best Practice -ratkaisu?

Kun historiallisia suoritusajoja ei tarvitse säilyttää ja pohjadata `@[backend_v2/seed/seed_data.json]` päivitetään puhtaalta pöydältä, Malli A yhdistää kaksi alan parasta käytäntöä ilman ainuttakaan kompromissia:

1. **Stripe-tyylinen tyyppiturvallisuus sovelluskerroksessa (Zero Cross-Entity ID Confusion):**
   * Jos sovelluskerroksessa käytettäisiin pelkkiä raakoja UUID-merkkijonoja (`0195f3a0-...`), kehittäjä tai kutsuva koodi voisi vahingossa välittää `step_id`-parametrin `workflow_id`-kenttään tai `prompt_block_id`-kenttään ilman, että tyyppijärjestelmä huomaa virhettä.
   * Malli A:ssa `parse_prefixed_uuid7(val, EntityPrefix.WORKFLOW)` pysäyttää väärän entiteettityypin välittömästi (`Fail-Fast AppException`), koska etuliite on lukittu osaksi ulkoista tunnisteformaattia.
2. **PostgreSQL 19:n 16-tavuinen binäärinen suorituskyky ja muistitehokkuus:**
   * `TEXT`-muotoinen tunniste vie PostgreSQL:ssä 21–37 tavua per rivi ja indeksiavain, kun taas natiivi `UUID` vie aina tasan **16 tavua**.
   * RFC 9562 `UUIDv7` sisältää 48-bittisen Unix-millisekuntiaikaleiman korkeimmissa biteissään sekä 12-bittisen monotonisen alilaskurin (`_MonotonicUuid7State`), jolloin uudet rivit sijoittuvat B-Tree-indeksin oikeaan reunaan peräkkäisesti ilman satunnaisia sivuhajoamisia (*random I/O page splits*).
3. **Täydellinen relaatioeheys (`FOREIGN KEY`) kaikkien 12 taulun välillä:**
   * Kun myös `organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows` ja `output_profiles` käyttävät `UUID PRIMARY KEY` -avainta, kaikki taulujen väliset viiteavaimet (nimenomaan ja tyhjentävästi: `users.organization_id`, `prompt_blocks.organization_id`, `steps.organization_id`, `steps.role_block_id`, `steps.extraction_protocol_block_id`, `steps.execution_persona_block_id`, `workflows.organization_id`, `workflows.default_profile_id`, `workflows.mcp_gateway_id`, `workflows.model_registry_id`, `output_profiles.workflow_id`, `output_profiles.organization_id`, `executions.workflow_id`, `executions.active_profile_id`, `executions.output_profile_id`, `executions.organization_id`, `report_artifacts.execution_id`, `report_artifacts.workflow_id`, `report_artifacts.profile_id`) voidaan sitoa aidoiksi 16-tavuisiksi `UUID REFERENCES ...` -viiteavaimiksi.
4. **Nolla erikoistapausta koodikannassa (Single Pipeline):**
   * Sekä Python-backendissä (`generate_opaque_id`) että Flutter-asiakassovelluksessa ja Polyfactory-testitehtaissa on vain yksi ID-formaatti, yksi säännöllinen lauseke ja yksi validointisääntö.

---

### 2.4 Toteutusaskeleet (`@[backend_v2/seed/seed_data.json]` ja Koodikannan Atomaarinen Cutover)

Malli A toteutetaan viisivaiheisena atomaarisena leikkauksena `@[.agents/rules/03_seed_vault.md]`-säännön (`<vault_mutation_protocol>`) mukaisesti:

1. **Vaihe 1 — Core ID SSOT & Regex-lukitus (`@[backend_v2/models/core_base.py]` & `@[backend_v2/models/enums.py]`):**
   * Päivitetään `OPAQUE_STRIPE_ID_REGEX` muotoon `r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`.
   * Poistetaan `_UUID7_DELEGATED_PREFIXES` ja muutetaan `generate_opaque_id(prefix)` delegoimaan kaikki kutsut suoraan funktiolle `generate_uuid7_opaque_id(prefix)`.
   * Päivitetään `SystemConfigID.MCP_GATEWAYS` vakioarvo 32-merkkiseksi RFC 9562 `UUIDv7` -tunnisteeksi.
2. **Vaihe 2 — `@[backend_v2/seed/seed_data.json]` Deterministinen `UUIDv7`-migraatio ja `@[scripts/sanitize_seed_vault.py]` Automaattinen ID-generointi:**
   * Ajetaan deterministinen migraatioskripti, joka luo jokaiselle `@[backend_v2/seed/seed_data.json]`-tiedostossa esiintyvälle 16-merkkiselle `{prefix}_{16_hex}`-tunnisteelle (sekä `wor_`-työnkulut että `sc_`-asteikot) yksikäsitteisen 32-merkkisen RFC 9562 `UUIDv7` -vastineen (`{prefix}_{32_hex_uuidv7}`).
   * Korvataan samalla kerralla kaikki kyseisiin tunnisteisiin osoittavat viiteavaimet koko `@[backend_v2/seed/seed_data.json]`-tiedostossa ja tarkistetaan referenssieheys komennolla `uv run python backend_v2/seed/run_seed.py local --dry-run`.
   * Lisäksi `@[scripts/sanitize_seed_vault.py]`-työkaluun lisätään automaattinen tarkistus: jos `@[backend_v2/seed/seed_data.json]`-tiedostoon lisätään uusi rivi tai atomiväite ilman kanonista `UUIDv7`-tunnistetta, työkalu generoi sille kanonisen `UUIDv7`-tunnisteen `generate_uuid7_opaque_id()`-funktiolla ja kirjoittaa sen suoraan `@[backend_v2/seed/seed_data.json]`-tiedostoon ennen `@[backend_v2/seed/run_seed.py]`-ajoa.
3. **Vaihe 3 — PostgreSQL 19 Skeeman ja Adapterin Yhtenäistäminen:**
   * Päivitetään `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` muuttamalla taulujen 1–7 pääavaimet (`id UUID PRIMARY KEY DEFAULT uuidv7()`) ja kaikki taulujen 1–10 relaatioviiteavaimet `UUID`-tyyppisiksi `CHECK (uuid_extract_version(...) = 7)` -rajoitteilla.
   * Päivitetään `@[backend_v2/database/postgres/entity_adapter.py]` käyttämään `parse_prefixed_uuid7()`- ja `format_prefixed_uuid7()`-funktioita kaikkien 10 entiteetti- ja binääritaulun tallennus- ja lukukyselyissä (`$1::uuid`).
4. **Vaihe 4 — Kovakoodattujen Oletus-ID-ankkureiden Poisto, Kausaalisen Koheesiomatriisin Sidonta ja `@[docs/tiede.md]`-graafimatematiikan 100 % Synkronointi (Luku 2.5):**
   * Poistetaan kovakoodatut 16-heksaiset oletus-ID:t Studio-luonnosten luonnista (`@[backend_v2/services/studio/workflow_service.py]` ja `@[backend_v2/models/domain/workflow.py]`), kytketään kausaalinen koheesiomatriisi suoraan `StepType.CAUSAL_DISCOVERY`-stepin `criteria_block_ids`-listaan ja täydennetään 0-tokenin topologiset graafimetriikat (`r_LCC`, `r_conv`, $\kappa_{\text{steer}}$ ja `simulate_counterfactual_retraction`) tiedostoihin `@[backend_v2/models/dtos/causal_discovery.py]`, `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]`, `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`, `@[backend_v2/settings.py]` ja `@[client_app_v2/lib/features/execution/models/causal_discovery_models.dart]` alla olevan Luvun 2.5 mukaisesti.
5. **Vaihe 5 — Flutter-mallien ja Testifikstuurien Synkronointi:**
   * Päivitetään kovakoodatut 16-merkkiset testitunnisteet (`backend_v2/tests/` ja `client_app_v2/test/`) kanonisiksi 32-merkkisiksi `UUIDv7`-tunnisteiksi.
6. **Vaihe 6 — Laatuportit ja Uudelleensiemennys:**
   * Ajetaan `uv run python backend_v2/seed/run_seed.py postgres --dry-run`, `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` ja `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.

---

### 2.5 Kovakoodattujen Oletus-ID-ankkureiden Poisto, Kausaalisen Koheesiomatriisin Sidonta ja `@[docs/tiede.md]`-graafimatematiikan 100 % Synkronointi

Varsinainen DAG-ajomoottori (`DAGExecutor`, `NodeExecutor`, `TDAEngine`, `SynthesisOrchestrator`) on vapaa kovakoodatuista steppi- ja matriisi-ID:istä, mutta koodipohjassa on kaksi oletusankkuria sekä neljä `@[docs/tiede.md]`-dokumentin Luvun 4.2 topologista 0-tokenin graafimittaria, jotka toteutetaan yhtenä kokonaisuutena samalla kun 32-heksainen `PrefixedUUID7` otetaan käyttöön:

#### 1. Studion "Luo uusi luonnos" (`create_step_draft`, `create_workflow_draft` & `Workflow.mcp_gateway_id`)
* **Ongelma:**
  * Tiedostossa `@[backend_v2/services/studio/workflow_service.py]` metodi `StudioWorkflowService.create_step_draft` (rivi 720) asettaa uuden stepin luonnokselle kovakoodatun 16-heksaisen oletusmatriisin `criteria_block_ids=["blk_440a5fef9331451b"]`, vaikka riveillä 690–695 sama metodi hakee jo kaikki lohkot tietokannasta (`all_blocks = await self.prompt_block_repo.get_all_prompt_blocks()`) etsiessään ensimmäisen `PromptBlockCategory.PROTOCOL`-lohkon.
  * Samassa tiedostossa `StudioWorkflowService.create_workflow_draft` (rivi 386) asettaa `default_profile_id="prf_0000000000000000"`, vaikka uudella tyhjällä työnkulkuluonnoksella (`steps=[]`) ei ole vielä yhtäkään steppiä eikä tulosprofiilia ja `@[backend_v2/models/domain/workflow.py]:Workflow.default_profile_id` sallii arvon `None`.
  * Lisäksi `@[backend_v2/models/domain/workflow.py]:Workflow.mcp_gateway_id` (rivit 42–46) sisältää kovakoodatun 16-heksaisen oletusarvon `default="sys_8172bda70c8641c5"`.
* **Arkkitehtoninen ratkaisu:**
  1. **`create_step_draft` (`@[backend_v2/services/studio/workflow_service.py]`):** Poimitaan `all_blocks`-silmukassa dynaamisesti sekä ensimmäinen `PromptBlockCategory.PROTOCOL`-lohko (`protocol_block_id`) että ensimmäinen matriisi-/kriteerilohko (`b.category_id in (PromptBlockCategory.MATRIX, PromptBlockCategory.CRITERIA)` -> `default_criteria_id`). Jos kumpikaan ei löydy tietokannasta, nostetaan `AppException(ErrorCodes.STATE_INTEGRITY_ERROR)`. Kovakoodattu `"blk_440a5fef9331451b"` poistetaan.
  2. **`create_workflow_draft` (`@[backend_v2/services/studio/workflow_service.py]`) & `Workflow.mcp_gateway_id` (`@[backend_v2/models/domain/workflow.py]`):** Asetetaan uudelle työnkulkuluonnokselle `default_profile_id=None`, muutetaan `Workflow.mcp_gateway_id`-kentän skeemaoletukseksi `default=None` ja haetaan aktiivinen MCP-gateway-konfiguraatio dynaamisesti `self.system_repo`-repositoriosta samalla tavalla kuin `chosen_registry_id`.

#### 2. Kausaalisen koheesion matriisi (`settings.causal_cohesion_matrix_block_id` & `CausalCohesionEvaluator`)
* **Ongelma:**
  * Kausaalinen koheesio ohittaa normaalin `Step.criteria_block_ids`-sopimuksen kolmessa paikassa:
    1. `@[backend_v2/settings.py]` (rivit 426–428) määrittelee kovakoodatun asetuksen `causal_cohesion_matrix_block_id = "blk_c0a1e50000000001"`.
    2. `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` (rivit 35–49) kovakoodaa 5 atomi-ID:tä (`CAUSAL_COHESION_TDA_IDS`) ja niiden väitetekstit (`CAUSAL_COHESION_CLAIMS`) suoraan Python-tupleiksi.
    3. `@[backend_v2/models/domain/workflow.py]:Workflow.get_allowed_layout_targets` (rivit 194–217) sisältää erillisen `causal_cohesion_block_id: str | None = None` -sivukanavaparametrin, koska `StepType.CAUSAL_DISCOVERY` -steppi ei ilmoita koheesiomatriisiaan omassa `criteria_block_ids`-listassaan.
* **Arkkitehtoninen ratkaisu:**
  1. **Kytketään koheesiomatriisi suoraan `CAUSAL_DISCOVERY`-stepin `criteria_block_ids`-kenttään (`@[backend_v2/models/domain/step.py]` & `@[backend_v2/seed/seed_data.json]`):**
     * Vaaditaan `Step.validate_step_consistency`-validaattorissa, että myös `StepType.CAUSAL_DISCOVERY` -stepillä on `criteria_block_ids`-kentässä sen käyttämä BARS-koheesiomatriisi (`MatrixPromptBlock`).
     * Poistetaan `causal_cohesion_block_id`-sivukanavaparametri metodista `@[backend_v2/models/domain/workflow.py]:Workflow.get_allowed_layout_targets`, koska `get_allowed_prompt_block_targets` löytää koheesiomatriisin nyt automaattisesti `step.criteria_block_ids`-listasta.
  2. **Luetaan matriisi-ID ja sen 5 BARS-atomia suoraan stepin matriisista ajon aikana (`@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` & `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`):**
     * Haetaan `_append_causal_fusion_and_cohesion_events`-funktiossa kausaalistepin (`src_step_id`) `Step`-määrityksestä `cohesion_matrix_id = src_step_def.criteria_block_ids[0]` sekä kyseisen `MatrixPromptBlock`-matriisin 5 BARS-rivin `TDAAssertion`-oliot (`id` ja `claim`) ja välitetään ne suoraan `CausalCohesionEvaluator.evaluate_causal_cohesion`-metodille.
     * Poistetaan `causal_cohesion_matrix_block_id` tiedostosta `@[backend_v2/settings.py]` sekä kovakoodatut `CAUSAL_COHESION_TDA_IDS`- ja `CAUSAL_COHESION_CLAIMS`-vakiot tiedostosta `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`.

#### 3. `@[docs/tiede.md]`-graafimatematiikan 100 % Synkronointi (`r_LCC`, `r_conv`, $\kappa_{\text{steer}}$ ja `simulate_counterfactual_retraction`)
* **Ongelma:**
  * Nykyinen `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]:compute_causal_tda_fusion_result` tarkistaa vain yksittäiset täysin eristyneet solmut (`isolated_concept_count`), jolloin toisistaan irrallisista kahden solmun väitepareista ($A \to B$, $C \to D$) tai kahden lauseen tynkäteksteistä koostuva tuotos voi läpäistä kaikki 5 BARS-tasoa (`l1_passed`..`l5_passed = True`) tiedostossa `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`.
  * Lisäksi `@[docs/tiede.md]`-dokumentin Luvun 4.2 mukaiset nollan LLM-tokenin topologiset mittarit (`largest_component_ratio` $r_{\text{LCC}}$, `branch_convergence_ratio` $r_{\text{conv}}$, `steering_coupling_ratio` $\kappa_{\text{steer}}$) sekä kontrafaktuaalinen haavoittuvuussimulaatio (`simulate_counterfactual_retraction`, Algoritmi 1) puuttuvat `AntiFluffAuditDTO`- ja `CausalCohesionEvaluator`-luokista.
* **Arkkitehtoninen ratkaisu (0 lisätokenia, $< 1\text{ ms}$ suoritusaika):**
  1. **DTO-sopimus ja Full-Duplex Pariteetti (`@[backend_v2/models/dtos/causal_discovery.py]` & `@[client_app_v2/lib/features/execution/models/causal_discovery_models.dart]`):**
     * Lisätään `AntiFluffAuditDTO`-luokkaan (ja vastaavaan Flutterin Freezed-malliin) kolme kenttää: `largest_component_ratio: float` ($r_{\text{LCC}} \in [0.0, 1.0]$), `branch_convergence_ratio: float` ($r_{\text{conv}} \in [0.0, 1.0]$) ja `steering_coupling_ratio: float` ($\kappa_{\text{steer}} \in [0.0, 1.0]$).
     * Lisätään `CounterfactualSimulationResultDTO` (kentät nimenomaan ja tyhjentävästi: `retracted_root_id`, `collapsed_node_ids`, `surviving_node_ids`, `collapse_ratio`, `max_cascade_depth`) kontrafaktuaalisen stressitestin paluuarvoksi.
  2. **Topologisten mittareiden laskenta (`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]:compute_causal_tda_fusion_result`):**
     * Lasketaan `deliverable_nodes`-joukolle samassa silmukassa suurimman yhtenäisen komponentin suhteellinen koko $r_{\text{LCC}} = |\mathcal{V}_{\text{LCC}}| / |\mathcal{V}_{\text{deliv}}|$ (Dyad Fragmentation Defense), monipremissisten synteesisolmujen osuus $r_{\text{conv}} = |\{v \in \mathcal{V}_{\text{deliv}} : \text{InDegree}(v) \ge 2\}| / |\mathcal{V}_{\text{deliv}}|$ sekä ihmisen keskusteluohjaukseen kytkeytyvien juurisolmujen osuus $\kappa_{\text{steer}}$.
  3. **Guttman-porttien ja kontrafaktuaalisen simulaation toteutus (`@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` & `@[backend_v2/settings.py]`):**
     * Lisätään `@[backend_v2/settings.py]`-tiedostoon konfiguraatioarvot (nimenomaan ja tyhjentävästi: `causal_cohesion_l2_min_nodes = 2`, `causal_cohesion_l3_min_nodes = 5`, `causal_cohesion_l4_min_nodes = 10`, `causal_cohesion_l5_min_nodes = 15`, `causal_cohesion_l2_lcc_min = 0.35`, `causal_cohesion_l3_lcc_min = 0.50`, `causal_cohesion_l4_lcc_min = 0.70`, `causal_cohesion_l5_lcc_min = 0.85` ja `causal_cohesion_l4_convergence_min = 0.05`).
     * Päivitetään `CausalCohesionEvaluator.evaluate_causal_cohesion` tarkistamaan `total_nodes`, `largest_component_ratio` ja `branch_convergence_ratio` 1:1 `@[docs/tiede.md]`-dokumentin Kaavan (13) mukaisesti.
     * Toteutetaan `CausalCohesionEvaluator.simulate_counterfactual_retraction(graph, retracted_node_id, conjunctive)` `@[docs/tiede.md]`-dokumentin Algoritmin 1 mukaisena BFS-etenemisenä ($\bigwedge$ konjunktiivinen ja $\bigvee$ disjunktiivinen tila).

---

## Luku 3: AST- ja Laatuporttilaajennukset (`QGR031`, `scripts/*.py` & `QGR032`)
> **STATUS: TUNNISTETUT JATKOHANKKEET (Tuleva Roadmap)**
> *Selite: `@[scripts/_ast_guardrails.py]` kattaa tällä hetkellä säännöt `QGR000`–`QGR030`. Alla olevat kolme tarkistusta ovat vielä toteuttamatta.*

1. **`QGR031` (Kyselysuodattimien staattinen validointi):** Estää virheelliset operaattorit (`"eq"`, `"LIKE"`, `"="`), tyhjät kentät sekä `"in"`-operaattorin vahingolliset merkkijonoliteraalit staattisesti AST-tasolla.
2. **`scripts/`-hakemiston dynaaminen automaattiskannaus:** Korvaa kovakoodatut skriptilistat dynaamisella `scripts/*.py` -globilla, estäen varjoskriptien ja vanhentuneiden aputyökalujen syntymisen laatuporttien ulkopuolelle.
3. **Polyfactory-mallitehtaiden invarianttivartija (`QGR032` & metatestit):** Varmistaa, että testitehtaat käyttävät heksadesimaalisia Opaque ID -generaattoreita ja että jokainen tehdas palauttaa aina oletusarvoilla `.build()` validoituvan Pydantic V2 -mallin.
