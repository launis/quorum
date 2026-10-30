# KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTOINTISUUNNITELMA (2026)
## GCP Cloud Run, PostgreSQL 19 Zero-ORM, B2B SaaS IAM, Cloud Storage & Full-Stack Hardening

> [!NOTE]
> **Arkkitehtuurin tila ja Single Source of Truth (SSOT)**
> Tämä asiakirja kokoaa yhteen Cognitive Quorumin tuotantopystytyksen kokonaiskuvan Google Cloud Platformilla (`europe-north1` / Hamina, Suomi). Se korvaa vanhentuneet SQLAlchemy 2.0-, Alembic- ja TinyDB-luonnokset ja nojaa suoraan Quorumin virallisiin 2026-arkkitehtuuristandardeihin sekä dokumentin `@[docs/arkkitehtuurin_parannuskohteet.md]` korjauksiin:
> 1. **PostgreSQL 19 Zero-ORM Perusta & Cutover — [SUORITETTU & LUKITTU]** (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]`)
> 1b. **Järjestelmällinen Ennaltaehkäisy, AST-vartija QGR030 & Testitehtaat — [SUORITETTU & AUDITOITU]** (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md]`, `@[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`)
> 2. **`dag_executor.py` God Code -purku modulaariseksi SRP-paketiksi — [SUORITETTU & KOVENNETTU]** (1 803 LOC -> 6 erillistä SRP-moduulia & ohut fasaadi, QGR017-lukittu) (`@[docs/epic/dag_executor_decomposition_tracker.md]`)
> 3. **Backend-koodikannan Karkaisuaallot 1–4 (403 `.py`-tiedoston kokonaiskarkaisu; Aallot 1–4: 36 + 36 + 27 + 34 = 133/133 tiedostoa; 391/403 valmiina, 12 IAM/Storage-tiedostoa Askeleissa 4 & 5) — [SUORITETTU & LUKITTU 133/133]** (`@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`, `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 1)
> 3b. **Arkkitehtuurin Parannuskohteiden Toteutus & `entity_adapter.py`-purku (Askeleet 3.3–3.5)**:
>    * **Askel 3.3 (Malli A) — [SUORITETTU, KOVENNETTU & LUKITTU]:** Yhtenäinen 32-hex `PrefixedUUID7`-arkkitehtuuri, Natiivi PostgreSQL 19 `UUIDv7` kaikissa 12 taulussa, `@[backend_v2/seed/seed_data.json]` 32-hex Cutover, `@[scripts/sanitize_seed_vault.py]`-automaatio, `@[docs/tiede.md]`-graafimatematiikan synkronointi sekä kaikkien legacy `uuid.uuid4()`- ja `Uuid().v4()`-generaattoreiden poisto ja `QGR030`/`DGR008`-lukitus (`@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` [15/15], `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` [31/31], `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 2).
>    * **Askel 3.4 — [SEURAAVANA JONOSSA]:** AST- ja Laatuporttilaajennukset `QGR031` (`FilterOperator`-kurinalaisuus), dynaaminen `scripts/*.py`-skannaus & `QGR032` (Polyfactory 32-hex `UUIDv7` -invarianttivartija) (`@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 3).
>    * **Askel 3.5:** `PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter.py]`, 1 975 LOC) God Code -purku 4 SRP-moduuliin (`iam_adapter.py`, `studio_adapter.py`, `execution_adapter.py`, `seeding_adapter.py` + `<150 LOC` `__init__.py` fasaadi).
> 4. **B2B SaaS IAM, Token Exchange & Enterprise Hardening** (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`)
> 5. **Firebase Storage & Direct-to-Cloud Signed URLs** (`[NEW]` `@[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]`)
> 6. **Frontend & Studio UI Hardening (`client_app_v2` Karkaisuaallot F1–F4: 185 `.dart`-tiedostoa + 9 IAM-tiedostoa = 194 tiedostoa)** (`[NEW]` `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]` – `WaveF4.md`)
> 7. **GCP Production Deployment, Cloud Security & FinOps Hardening** (`@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`, tracker: `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`)

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
  * Asetetaan verkkotunnus Cloud Run -ympäristömuuttujiin (`PRIMARY_DOMAIN=qrum.ai`, `JWT_ISSUER=https://api.qrum.ai`, `JWT_AUDIENCE=https://qrum.ai`, `CORS_ORIGINS`). Koska `@[backend_v2/settings.py#L47-L1132]` lukee kaikki domain- ja JWT-väitteet dynaamisesti ympäristömuuttujista (`AliasChoices`), Python- tai Flutter-lähdekoodiin ei tarvita yhtäkään koodimuutosta.
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
* **5. CORS & Origin Security (`@[backend_v2/settings.py#L47-L1132]`):**
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
    "redis>=5.2.0",             # Asynkroninen Redis Kill-Switchille ja Arqille
    "arq>=0.26.0",              # Asynkroninen taustatyöjono Cloud Run Workerille
    "firebase-admin>=6.6.0",    # Firebase ID Token validointi ja Signed URLs
    "google-cloud-storage>=2.19.0",
    "google-cloud-secret-manager>=2.21.0",
    "cryptography>=44.0.0",     # BYOK Envelope Encryption (AES-256-GCM)
    "logfire>=2.10.0",          # Hajautettu OpenTelemetry-observabiliteetti
]
```

---

## Luku 2: Tietokantamallit ja Yhtenäinen Natiivi UUIDv7 (Zero-ORM SSOT & Malli A)

PostgreSQL 19 on Single Source of Truth (SSOT) kaikelle sovellusdatalle. Tiedostojen binäärejä ei säilytetä relaatiokannassa, vaan kanta hallinnoi ainoastaan metadataa.

### 2.1 Pääavaimet ja Yhtenäinen RFC 9562 `PrefixedUUID7` (Malli A — `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 2)
* **Yksi yhtenäinen tunnistestandardi kaikissa 12 taulussa (Askel 3.3):** Kaikki 12 PostgreSQL 19 -taulua (nimenomaan ja tyhjentävästi: `organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`, `proposition_nodes` ja `dependency_edges`) käyttävät primääriavaimena PostgreSQL 19:n natiivia 16-tavuista `UUID`-tyyppiä (`UUID PRIMARY KEY DEFAULT uuidv7()`).
* Python- ja Flutter-rajapintakerroksessa kaikki pää- ja viiteavaimet sillataan tyyppiturvalliseen 32-heksadesimaaliseen **`PrefixedUUID7`** -muotoon (`OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`):
  * Käyttäjät: `usr_<hex32>` (kanoninen muoto `usr_01950000000070008000000000000001`)
  * Organisaatiot: `org_<hex32>` (järjestelmän juuriorganisaatio `org_01950000000070008000000000000000`)
  * Kutsut: `inv_<hex32>` ja Salaisuudet (BYOK): `sec_<hex32>`
  * Konfiguraatio- ja Studio-entiteetit: `cfg_<hex32>`, `blk_<hex32>`, `stp_<hex32>`, `wf_<hex32>`, `out_<hex32>`, `row_<hex32>`, `tda_<hex32>`, `var_<hex32>`, `scl_<hex32>`, `gate_<hex32>`
  * Suoritus- ja Graafientiteetit: `exe_<hex32>`, `rep_<hex32>`, `nod_<hex32>`, `edg_<hex32>`
* **Automaattinen Seed Vault -työkalu (`@[scripts/sanitize_seed_vault.py]`):** Kun kehittäjä lisää uuden entiteetin, matriisirivin tai väitteen `@[backend_v2/seed/seed_data.json]`-tiedostoon, `sanitize_seed_vault.py` generoi puuttuvan tai vanhan 16-heksaisen tunnisteen tilalle kanonisen 32-merkkisen `UUIDv7`-tunnisteen `generate_uuid7_opaque_id(prefix)`-funktiolla ja päivittää kaikki sisäiset viitteet atomisesti ennen `@[backend_v2/seed/run_seed.py]`-ajoa.

### 2.2 SQL DDL -skeema (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`)
Kanta alustetaan ilman Alembicia suoralla, idempotentilla SQL DDL -tiedostolla, jossa kaikki 12 taulua hyödyntävät natiivia `UUID PRIMARY KEY DEFAULT uuidv7()` -määrittelyä ja `uuid_extract_timestamp(id) VIRTUAL` -saraketta:

```sql
-- PostgreSQL 19 Natiivi Skeema (Ote: organizations, users, file_metadata)

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(128) UNIQUE,
    tier VARCHAR(64) NOT NULL DEFAULT 'standard',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    quota_limit NUMERIC(10,2) NOT NULL DEFAULT 100.00,
    tpm_limit BIGINT NOT NULL DEFAULT 100000,
    rpm_limit INT NOT NULL DEFAULT 60,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(320) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'USER',
    name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ, -- GDPR Soft-Delete
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);

CREATE INDEX idx_users_org ON users(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);

CREATE TABLE file_metadata (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    size_bytes BIGINT NOT NULL,
    storage_path VARCHAR(1024) NOT NULL UNIQUE,
    mime_type VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending', -- pending -> uploaded -> verified
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);
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

### 2.4 Zero-ORM Adapterikerros ja Purkusuunnitelma (`@[backend_v2/database/postgres/]`)

PostgreSQL 19 Zero-ORM -arkkitehtuuri nojaa suoraan `asyncpg`-ajuriin ja heksagonaalisiin portteihin (`GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`). Kanta-adaptereista muodostuu kolme ydinkomponenttia:

1. **`PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter.py]`, 1 975 LOC):**
   * **Vastuu:** Kokoaa yhteen kaikkien 10 entiteettitaulun (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`) natiivit parametroidut SQL-kyselyt, `_to_pg_uuid` / `_from_pg_uuid` -siltauksen, JSONB-projektion ja eräseedauksen.
   * **Arkkitehtoninen tila ja Purku (Askel 3.5 / Luku 7 Kohta 13):** Heti kun Askel 3.3 (Malli A: yhtenäinen 16-tavuinen `UUIDv7` kaikissa 12 taulussa) on toteutettu, `entity_adapter.py` puretaan `/tier3-god-code-decomposition`-työnkululla alipakettiin `backend_v2/database/postgres/entity/`:
     * `iam_adapter.py` (`organizations`, `users`)
     * `studio_adapter.py` (`system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`)
     * `execution_adapter.py` (`executions`, `report_artifacts`, `report_binaries`)
     * `seeding_adapter.py` (idempotentit batch-tallennukset)
     * Ohut `<150 LOC` fasaadi `backend_v2/database/postgres/entity/__init__.py`.
2. **`PostgresGraphAdapter` (`@[backend_v2/database/postgres/graph_adapter.py]`, 669 LOC):**
   * **Vastuu:** Kausaalipäättelygraafin (`proposition_nodes`, `dependency_edges`) Kahnin aallot, asyklisyyden varmennus (`detect_cycle`) ja falsifioitujen väitteiden suodatus.
3. **`PostgresPoolManager` (`@[backend_v2/database/postgres/pool.py]`, 534 LOC):**
   * **Vastuu:** `asyncpg`-yhteysaltaan elinkaari, transaktiorajat, binääriset `\x01` `pydantic_core` JSONB-koodekit ja DDL-migraatioiden suoritus ilman ulkoisia migraatiotyökaluja.

---

## Luku 3: B2B SaaS IAM, Token Exchange ja Turvallisuus

### 3.1 RFC 8693 Token Exchange & Session Upgrade
Tietokantaa ei koskaan kysellä jokaisella saapuvalla HTTP-pyynnöllä:
1. **Kirjautuminen / Vaihto:** Asiakassovellus kirjautuu Firebase Authiin ja lähettää lyhytikäisen Firebase ID Tokenin backendille: `POST /api/v2/iam/auth/exchange`.
2. **Kertatarkistus:** Backend tarkistaa Firebase-allekirjoituksen Firebase Admin SDK:lla, hakee käyttäjän kannasta `firebase_uid`-kentällä ja varmistaa aktiivisuuden (`deleted_at IS NULL`).
3. **Quorum Local JWT:** Backend myöntää asiakkaalle 15 minuutin sisäisesti allekirjoitetun JWT-tokenin, joka sisältää valtuutustiedot:
   * `sub`: `usr_<hex32>`
   * `org`: `org_<hex32>`
   * `role`: `UserRole`
4. **0,1 ms API-validointi RAMissa:** Kaikki API-kutsut käyttävät Local JWT:tä. Sen validointi tapahtuu FastAPI:n `get_current_user_from_header` -riippuvuudessa suoraan muistissa ilman tietokantalatenssia.

### 3.2 Redis Fail-Closed Kill-Switch
Jos ylläpitäjä sulkee käyttäjätilin, muuttaa roolia tai käyttäjä poistetaan GDPR-pyynnöllä:
* Backend kirjoittaa välittömästi Redisiin avaimen `revoked:usr:{user.id}` (TTL = 900 s).
* Jokainen API-kutsu tarkistaa O(1) nopeudella Redisistä, ettei käyttäjä ole estolistalla.
* **Fail-Closed:** Jos Redis-yhteys katkeaa, järjestelmä palauttaa `503 Service Unavailable`, estäen oikeuksien vuotamisen.

### 3.3 Enterprise BYOK (Bring Your Own Key)
Organisaatiot voivat tuoda omat LLM- ja MCP-avaimensa:
* Avaimet salataan `Cloud KMS` Envelope Encryption -menetelmällä tai tallennetaan GCP Secret Manager -viitteinä.
* Avaimet puretaan EPIC 160:ssä luotavassa `[NEW]` `SecretService`-palvelussa pyyntökohtaisesti `pydantic.SecretStr`-muotoon ja injektoidaan LLM- ja MCP-kutsuille ilman lokivuotoja.

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
* **DDL-migraatio:** `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` luo kaikki 12 taulua idempotentisti (`CREATE TABLE IF NOT EXISTS`) natiiveilla `UUID PRIMARY KEY DEFAULT uuidv7()` -avaimilla.
* **Seed Vaultin sanitointi (`@[scripts/sanitize_seed_vault.py]`):** Varmistaa, että jokainen `@[backend_v2/seed/seed_data.json]`-tiedostoon lisätty uusi rivi, matriisiatomi tai konfiguraatio saa kanonisen 32-merkkisen `UUIDv7`-tunnisteen (`generate_uuid7_opaque_id()`) ennen tietokantaan latausta.
* **Seeding-skripti (`@[backend_v2/seed/run_seed.py]`):**
  * Lukee ja validoi `@[backend_v2/seed/seed_data.json]`-perustiedot `ValidatedSeedBufferDTO`-puskurin läpi (järjestelmäorganisaatio `ROOT_SYSTEM = "org_01950000000070008000000000000000"`, oletustyönkulut, prompt-lohkot, matriisit ja tulosprofiilit).
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
│    2F. AST & Laatuportit QGR031, scripts/*.py & QGR032 [SEURAAVA]      │
│        (Askel 3.4: arkkitehtuurin_parannuskohteet.md Luku 3)           │
│    2G. PostgresEntityAdapter (1 975 LOC) God Code -purku (Askel 3.5)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 3. B2B SaaS IAM & Hardening (Askel 4 - EPIC 160)                       │
│    Token Exchange (RAM <0,1 ms), Redis Kill-Switch, BYOK SecretService │
│    Kattaa 9 backend IAM-tiedostoa + 9 Flutter features/auth/ tiedostoa │
│    Epic: docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 4. Storage Signed URLs & Frontend Hardening (Askeleet 5 & 5.1-5.4)     │
│    4A. Firebase Storage Signed URLs, FileMetadata, orposiivous (3 kpl) │
│        Plan: docs/implementationplans/IMPLEMENTATION_PLAN_Storage_...  │
│    4B. Frontend & Studio UI Karkaisuaallot F1-F4 (185 .dart-tiedostoa) │
│        Aalto F1 (41), Aalto F2 (44), Aalto F3 (47), Aalto F4 (53)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────────────┐
│ 5. GCP Tuotantopystytys, qrum.ai Domain, CI/CD & E2E Go-Live (Askeleet 6, 6.1 & 6.2)│
│    5A. Cloud SQL PG19, Cloud Run API & Worker Pool (WeasyPrint C-libs), Memorystore │
│    5B. Flutter Web (app.qrum.ai, studio.qrum.ai) Release Build & Cloud CDN Hosting  │
│    5C. CI/CD Pipeline (Artifact Registry) & Cloud Run Job Seeding (run_seed.py)     │
│    5D. Cloud Armor WAF, Least Privilege IAM & FinOps Circuit Breakers (Askel 6.1)   │
│    5E. Lopullinen Full-Stack E2E Go-Live -Todennusportti (Askel 6.2)                │
│    Epic: docs/epic/EPIC_74_Production_Deployment_GCP.md                             │
│    Plan: docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md │
│    Tracker: docs/implementationplans/TRACKER_GCP_Production_Deployment.md          │
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
| **13. PostgreSQL Zero-ORM Entity Adapter** | `@[backend_v2/database/postgres/entity_adapter.py]`<br>**1 975 LOC**. Kokoaa yhteen kaikkien 10 entiteettitaulun (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`) natiivit SQL-lauseet, hidraatiot, CRUD-operaatiot ja eräseedauksen. | Puretaan Two-Epoch Strangler Fig -mallilla pakettiin `backend_v2/database/postgres/entity/`: `iam_adapter.py`, `studio_adapter.py`, `execution_adapter.py`, `seeding_adapter.py` ja alle 150 LOC fasaadi `__init__.py`. | **Entity Adapter Decomposition Plan (Askel 3.5)**<br>`/tier3-god-code-decomposition @[backend_v2/database/postgres/entity_adapter.py]` | **Askel 3.5 (Vaihe 2g)**<br>Suoritetaan välittömästi Askeleen 3.3 (`PrefixedUUID7` 12 taulun yhtenäistys) ja Askeleen 3.4 jälkeen ennen `EPIC 160` IAM-vaihetta |

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
| **Askel 3.4** | **AST- ja Laatuporttilaajennukset (`QGR031`, `scripts/*.py` & `QGR032`)** | 🟢 **SUUNNITELMA & TRACKER VALMIINA LEVYLLÄ:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` & `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` | Seuraava jonossa — valmis suoraan `/tier2-execute --full-auto` -suoritukseen. |
| **Askel 3.5** | **`PostgresEntityAdapter` (`entity_adapter.py`, 1 975 LOC) God Code -purku** (4 SRP-adapteriin) | 🟡 Määritelty Luvussa 2.4 ja Luvussa 7 (Kohta 13). | Generoi purkusuunnitelma ja tracker komennolla `/tier3-god-code-decomposition @[backend_v2/database/postgres/entity_adapter.py]`. |
| **Askel 4** | **B2B SaaS IAM, 2FA, Token Exchange, Redis Kill-Switch & BYOK (`EPIC 160`)** (`9` backend + `9` frontend tiedostoa) | 🟢 Eepos `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` on valmiina ja synkronoituna 32-hex `UUIDv7`:ään. | Generoi vaihesuunnitelmat ja `EPIC_160_tracker.md` komennolla `/tier1-planner @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`. |
| **Askel 5** | **Firebase Storage Direct-to-Cloud Signed URLs** (`3` tiedostopalvelutiedostoa) | 🟡 Arkkitehtuuri määritelty Luvussa 4. | Luo `IMPLEMENTATION_PLAN_Storage_Signed_URLs.md` ja `TRACKER_Storage_Signed_URLs.md` (`/tier0-create-plan` + `/tier1-plan-tracker-generator`). |
| **Askel 5.1 – 5.4** | **Frontend `client_app_v2/lib/` Karkaisuaallot F1–F4** (`41 + 44 + 47 + 53 = 185` `.dart`-tiedostoa) | 🟡 Kaikki 185 tiedostoa on listattu ja paketoitu Askeleissa 5.1–5.4. | Kirjoita 4 tracker-tiedostoa (`TRACKER_Frontend_Targeted_Hardening_WaveF1.md` – `WaveF4.md`) levylle ennen `auto_hardening_runner.py --gate frontend` -ajoa. |
| **Askel 6, 6.1 & 6.2** | **GCP Tuotantopystytys (`EPIC 74`), `qrum.ai` SAN SSL, Worker/WeasyPrint, Flutter Web Hosting, CI/CD & E2E Go-Live** | 🟢 Eepos `@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`, suunnitelma `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` ja `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]` ovat valmiina levyllä. | Päivitä Askeleen 6 suunnitelmaan kohdat 6A–6C (Worker/WeasyPrint, Flutter Web & CI/CD) ennen ajoa. |

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
> 2. **Täydellinen regressio- ja tyyppiturvaverkko Askeleille 3.3–3.5:** Koska kaikilla taustatyöntekijöillä, SDUI-adaptereilla, palvelukerroksilla, repositorioilla, reitittimillä, domain-malleilla ja DTO-skeemoilla on nyt eksplisiittiset `__all__`-määrittelyt, PEP 257 -dokumentaatio, `ConfigDict(extra="forbid", strict=True)` -sopimukset ja kattavat yksikkötestit, Askeleen 3.3 `PrefixedUUID7`-yhtenäistys (Malli A), Askeleen 3.4 AST-laajennukset (`QGR031`/`QGR032`) ja Askeleen 3.5 `entity_adapter.py`-purku voidaan ajaa läpi täydellisellä matemaattisella regressiosuojalla ennen Askeleen 4 (`EPIC 160` IAM) aloittamista.

---

### Askel 3.2b: Karkaisuaalto 2 — Core, Hooks, LLM Adapters & Studio/Execution Services (Vaihe 2c-2) — [SUORITETTU & LUKITTU 36/36]
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`
* **Tila & Git Commit:** 🟢 **100 % SUORITETTU, 36/36 TIEDOSTOA KARKAISTU JA LUKITTU** — Commit `1f5da4a43` (*chore(hardening): audit and fix override_service.py*).

#### Paketti 1: Core, Observability & Shared Utilities (8/8 SUORITETTU)
1. `[x]` `@[backend_v2/context.py]`
2. `[x]` `@[backend_v2/core/rate_limit.py]`
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
7. `[x]` `@[backend_v2/api/routers/studio/system_configs.py]`
8. `[x]` `@[backend_v2/api/routers/studio/workflows.py]`
9. `[x]` `@[backend_v2/api/routers/execution/workflows.py]`
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
  1. `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` (`15/15` kohdetta karkaistu, Tier 7 synkronoitu, Tier 8 auditoitu)
  2. `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` (`31/31` kohdetta karkaistu, Tier 7 synkronoitu, Tier 8 auditoitu)
* **Tila:** 🟢 **100 % SUORITETTU, KARKAISTU, AUDITOITU & LUKITTU**
* **Miksi sijoitettu tähän kohtaan (heti Karkaisuaaltojen 2–4 jälkeen ja ENNEN Askelta 4 `EPIC 160` IAM):**
  `EPIC 160` (B2B SaaS IAM) perustuu siihen, että `organizations`- ja `users`-taulujen pääavaimet ovat natiiveja 16-tavuisia PostgreSQL 19 `UUIDv7`-arvoja (`usr_<hex32>` ja `org_<hex32>`). Toteuttamalla `@[docs/arkkitehtuurin_parannuskohteet.md]` Luvun 2 (**Malli A**) juuri ennen IAM-vaihetta poistettiin vanha kahtiajako (7 `TEXT`-taulua 16-heksalla vs. 5 `UUID`-taulua 32-heksalla) kerralla kaikista 12 taulusta sekä hävitettiin kaikki jäljellä olleet `uuid.uuid4()`- ja `Uuid().v4()`-generaattorit koko Python- ja Flutter-koodikannasta.
* **Toteutetut ja lukitut arkkitehtuurimuutokset (Malli A):**
  1. **PostgreSQL 19 DDL (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`):** Myös konfiguraatio- ja hallintataulut (nimenomaan ja tyhjentävästi: `organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows` ja `output_profiles`) käyttävät `id UUID PRIMARY KEY DEFAULT uuidv7()` -määrittelyä, `created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL` -saraketta ja `CHECK (uuid_extract_version(...) = 7)` -rajoitteita.
  2. **Zero-ORM Adapterisilta (`@[backend_v2/database/postgres/entity_adapter.py]`):** Kaikki 12 taulua käyttävät symmetristä `parse_prefixed_uuid7()` / `format_prefixed_uuid7()` -muunnosta ilman taulukohtaisia poikkeuksia, varmennettuna `@[scripts/audit_zero_orm_strictness.py]`-laatuportilla.
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

### Askel 3.4: AST- ja Laatuporttilaajennukset `QGR031`, `scripts/*.py` Dynaaminen Skannaus & `QGR032` Polyfactory-invarianttivartija (Vaihe 2f — `@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 3) — [SUUNNITELMA & TRACKER VALMIINA — SEURAAVANA JONOSSA]
* **Toteutussuunnitelma (Implementation Plan):** `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]`
* **Seurantadokumentti (SSOT Tracker):** `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`
* **Tavoite:** Lukitaan Askeleen 3.2b–3.2d ja Askeleen 3.3 saavuttama arkkitehtuurinen puhtaus kolmella pysyvällä laatuporttilaajennuksella (`@[docs/arkkitehtuurin_parannuskohteet.md]` Luku 3):
  1. **AST-sääntö `QGR031` (`FilterOperator` & `QueryCondition` -kurinalaisuus):** Lisätään `@[scripts/_ast_guardrails.py]`-tiedostoon sääntö, joka valvoo kaikkia `Filter(...)`- ja `QueryCondition(...)`-kutsuja ja estää virheelliset operaattorit (`"="`, `"eq"`, `"LIKE"`), tyhjät kenttänimet sekä `"in"`-operaattorin merkkijonoliteraalit.
  2. **Dynaaminen `scripts/*.py` -skannaus laatuportissa:** Päivitetään `@[scripts/backend_audit_loop.py]` skannaamaan dynaamisesti kaikki `scripts/*.py`-tiedostot (`Path("scripts").glob("*.py")`) kovakoodatun skriptilistan sijaan.
  3. **AST-sääntö `QGR032` (Polyfactory 32-hex `UUIDv7` Invariant Guard):** Lisätään `@[scripts/_ast_guardrails.py]`-tiedostoon sääntö, joka varmistaa, että jokainen `@[backend_v2/tests/factories/model_factories.py]`-luokka reitittää ID-kenttänsä `Use(generate_opaque_id, ...)`-kutsun kautta ja tuottaa 100 % `OPAQUE_STRIPE_ID_REGEX`-yhteensopivia 32-heksaisia `UUIDv7`-arvoja.
* **Suorituskomento:**
  ```powershell
  /tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]
  ```

---

### Askel 3.5: `PostgresEntityAdapter` (`entity_adapter.py`) God Code -purku (Vaihe 2g — Luku 7 Kohta 13)
* **Tavoite:** Kun kaikki 12 taulua käyttävät yhtenäistä 16-tavuista `UUIDv7`-siltausta (Askel 3.3), puretaan 1 975 rivin `@[backend_v2/database/postgres/entity_adapter.py]` Strangler Fig -mallilla neljään SRP-moduuliin ennen kuin `EPIC 160` laajentaa IAM-tietokantakyselyitä:
  1. `backend_v2/database/postgres/entity/iam_adapter.py` (`organizations`, `users`)
  2. `backend_v2/database/postgres/entity/studio_adapter.py` (`system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`)
  3. `backend_v2/database/postgres/entity/execution_adapter.py` (`executions`, `report_artifacts`, `report_binaries`)
  4. `backend_v2/database/postgres/entity/seeding_adapter.py` (idempotentti batch-seeding)
  5. `backend_v2/database/postgres/entity/__init__.py` (`< 150 LOC` fasaadi) + `QGR017`-lukitus.
* **Suunnittelukomento:**
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier3-god-code-decomposition @[backend_v2/database/postgres/entity_adapter.py]"
  ```

---

### Askel 4: Suorita B2B SaaS IAM & Hardening (Vaihe 3 — EPIC 160)
* **Tavoite:** Ota käyttöön RFC 8693 Token Exchange, 0,1 ms in-RAM JWT -validointi, Redis Fail-Closed Kill-Switch, moniroolivaltuutus ja luotava `SecretService`.
* **Karkaistavat IAM-tiedostot (Backend 9 kpl + Frontend 9 kpl):**
  * **Backend (`backend_v2/`, 9 tiedostoa):** `@[backend_v2/models/auth.py]`, `@[backend_v2/services/auth/constants.py]`, `@[backend_v2/services/auth/repositories.py]`, `@[backend_v2/services/auth/token_service.py]`, `@[backend_v2/services/auth/organization_service.py]`, `@[backend_v2/services/auth/user_service.py]`, `@[backend_v2/api/routers/iam/auth.py]`, `@[backend_v2/api/routers/iam/organizations.py]`, `@[backend_v2/api/routers/iam/users.py]`.
  * **Frontend (`client_app_v2/lib/features/auth/`, 9 tiedostoa):** `@[client_app_v2/lib/features/auth/data/auth_repository.dart]`, `@[client_app_v2/lib/features/auth/data/repositories/user_repository.dart]`, `@[client_app_v2/lib/features/auth/domain/models/user.dart]`, `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]`, `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, `@[client_app_v2/lib/features/auth/presentation/providers/firebase_instance_provider.dart]`, `@[client_app_v2/lib/features/auth/presentation/providers/mock_auth_provider.dart]`, `@[client_app_v2/lib/features/auth/presentation/providers/mock_user_provider.dart]`, `@[client_app_v2/lib/features/auth/presentation/providers/user_role_provider.dart]`.
* **Virallinen Eepos:** `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`
* **1. Generoi vaihekohtaiset suunnitelmat ja tracker:**
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-planner @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]"
  ```
* **2. Suorita vaiheet multi-phase runnerilla:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_160_tracker.md --model gemini-4-argon-high
  ```

---

### Askel 5: Suorita Firebase Storage Direct-to-Cloud Signed URLs (Vaihe 4)
* **Tavoite:** Toteuta frontendin suoralataus Firebase Storageen (15 min PUT Signed URLs), tiedostometadatan rekisteröinti ja orposiivous-taustatyö (kattaen backendin 3 tiedostopalvelutiedostoa: `@[backend_v2/services/file_driver.py]`, `@[backend_v2/services/drivers/local_file_driver.py]` ja `@[backend_v2/services/storage.py]`).
* **Toteutussuunnitelma (`[NEW]`):** `@[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]`
* **Seurantadokumentti (`[NEW]` Tracker):** `@[docs/implementationplans/TRACKER_Storage_Signed_URLs.md]`
* **1. Luo seurantatiedosto:**
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-plan-tracker-generator docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md"
  ```
* **2. Suorita automaattisesti:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_Storage_Signed_URLs.md --model gemini-4-argon-high
  ```

---

### Askel 5.1–5.4: Koko `client_app_v2/lib/` Frontend- ja Studio UI -Koodikannan Karkaisuaallot F1–F4 (Bottom-Up Hardening Roadmap, Vaihe 4b)

Vastaavasti kuin backendissä (`backend_v2/` 403 tiedostoa), myös koko Flutter Web- ja Desktop -asiakassovelluksen (`client_app_v2/lib/`) **194 ei-generoitua `.dart`-lähdetiedostoa** (pl. `*.freezed.dart`, `*.g.dart` ja `l10n/`) karkaistaan systemaattisesti alhaalta ylös (Bottom-Up) neljässä karkaisuaallossa (`Aallot F1–F4`) ennen pilvituotantoon julkaisua:

| Frontend-kategoria (`client_app_v2/lib/`) | Tiedostomäärä | Tila ja seurantadokumentti |
| :--- | :--- | :--- |
| **1. Karkaisuaalto F1 — Core, Network, API Clients, Error Boundaries, Theme, Shell & Shared Models** | `41` kpl | `[NEW]` `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]` (Askel 5.1) |
| **2. Karkaisuaalto F2 — Freezed Domain & DTO Models + Riverpod Controllers & Providers** | `44` kpl | `[NEW]` `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md]` (Askel 5.2) |
| **3. Karkaisuaalto F3 — Execution, Reports & Shared SDUI / Presentation Widgets** | `47` kpl | `[NEW]` `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md]` (Askel 5.3) |
| **4. Karkaisuaalto F4 — Quorum Studio Master Views, Profile Block Editors & Workflow Canvas Widgets** | `53` kpl | `[NEW]` `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]` (Askel 5.4) |
| **5. Eristetty B2B SaaS IAM Auth -alue (`client_app_v2/lib/features/auth/`)** | `9` kpl | Toteutetaan ja karkaistaan Askeleessa 4 (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`) |
| **YHTEENSÄ (`client_app_v2/lib/`)** | **194 kpl** | **185 tiedostoa Karkaisuaalloissa F1–F4 + 9 tiedostoa Askeleessa 4 (`EPIC 160`) = 100 % kattavuus** |

> [!IMPORTANT]
> **Frontend-karkaisun laatuvaatimukset (`/tier2-hardening-frontend` & `@[.agents/rules/02_flutter_desktop.md]`):**
> 1. **100 % teemasuvereeni ulkoasu (`audit_flutter_theme_sovereignty.py`):** Nolla kovakoodattua `Color(0x...)`-arvoa tai `Colors.*`-vakiota widgeteissä; kaikki värit ja typografia haetaan `Theme.of(context).colorScheme`- ja `AppColors`-kokoelmista.
> 2. **100 % Dumb Painter & Freezed DTO -pariteetti (`audit_dto_parity.py`):** Kaikki DTO-mallit ovat muuttumattomia `@freezed`-luokkia, jotka vastaavat 1:1 backendin Pydantic V2 -malleja ja 32-heksaisia `PrefixedUUID7`-avaimia ilman `Map<String, dynamic>`-sanakirjakikkailua.
> 3. **Nolla Red Screen of Death -kaatumista (`AppErrorBoundary` & `AsyncValue.when`):** Jokainen Riverpod-näkymä käsittelee `loading`-, `error`- ja `data`-tilat eksplisiittisesti ilman `!`-pakotuksia (null-check bang operator) tai hiljaisia `SizedBox.shrink()`-virhenieluja.
> 4. **Widget- ja yksikkötestit (`client_app_v2/test/`):** Jokaiselle karkaistulle mallille, kontrollerille ja näkymälle varmistetaan sekä positiivinen että negatiivinen/rajatapaus-yksikkö- tai widget-testi.

---

### Askel 5.1: Frontend Karkaisuaalto F1 — Core, Network, API Clients, Error Boundaries, Theme, Shell & Shared Models (41 tiedostoa)
* **Seurantadokumentti (`[NEW]`):** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Root, Routing, Shell & Theme (11 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/main.dart]`
  2. `[ ]` `@[client_app_v2/lib/app.dart]`
  3. `[ ]` `@[client_app_v2/lib/app_config.dart]`
  4. `[ ]` `@[client_app_v2/lib/firebase_options.dart]`
  5. `[ ]` `@[client_app_v2/lib/router/router.dart]`
  6. `[ ]` `@[client_app_v2/lib/router/scaffold_with_nav.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/shell/presentation/scaffold_with_nav.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/shell/presentation/widgets/admin_sidebar.dart]`
  9. `[ ]` `@[client_app_v2/lib/theme/app_colors.dart]`
  10. `[ ]` `@[client_app_v2/lib/theme/app_durations.dart]`
  11. `[ ]` `@[client_app_v2/lib/theme/app_theme.dart]`
* **Paketti 2 — Core API Clients & Dio Network Interceptors (10 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/core/api/execution_client.dart]`
  2. `[ ]` `@[client_app_v2/lib/core/api/reports_client.dart]`
  3. `[ ]` `@[client_app_v2/lib/core/api/sse_client.dart]`
  4. `[ ]` `@[client_app_v2/lib/core/api/studio_client.dart]`
  5. `[ ]` `@[client_app_v2/lib/core/api/workflow_client.dart]`
  6. `[ ]` `@[client_app_v2/lib/core/network/api_client.dart]`
  7. `[ ]` `@[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart]`
  8. `[ ]` `@[client_app_v2/lib/core/network/interceptors/dio_logger_interceptor.dart]`
  9. `[ ]` `@[client_app_v2/lib/core/network/interceptors/error_interceptor.dart]`
  10. `[ ]` `@[client_app_v2/lib/core/network/interceptors/locale_interceptor.dart]`
* **Paketti 3 — Core Error Boundaries, Logging, Models, Utils & Shared DTOs (20 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/core/environment/env.dart]`
  2. `[ ]` `@[client_app_v2/lib/core/error/app_error_boundary.dart]`
  3. `[ ]` `@[client_app_v2/lib/core/error/app_error_ext.dart]`
  4. `[ ]` `@[client_app_v2/lib/core/error/app_exception.dart]`
  5. `[ ]` `@[client_app_v2/lib/core/error/validation_error_reason.dart]`
  6. `[ ]` `@[client_app_v2/lib/core/logging/app_logger_observer.dart]`
  7. `[ ]` `@[client_app_v2/lib/core/logging/logger_service.dart]`
  8. `[ ]` `@[client_app_v2/lib/core/models/enums.dart]`
  9. `[ ]` `@[client_app_v2/lib/core/models/generic_status_response_dto.dart]`
  10. `[ ]` `@[client_app_v2/lib/core/models/prompt_block_category.dart]`
  11. `[ ]` `@[client_app_v2/lib/core/state/mutation.dart]`
  12. `[ ]` `@[client_app_v2/lib/core/theme/app_spacing.dart]`
  13. `[ ]` `@[client_app_v2/lib/core/ui/error_view.dart]`
  14. `[ ]` `@[client_app_v2/lib/core/ui/splash_screen.dart]`
  15. `[ ]` `@[client_app_v2/lib/core/utils/safe_isolate.dart]`
  16. `[ ]` `@[client_app_v2/lib/utils/json_converters.dart]`
  17. `[ ]` `@[client_app_v2/lib/utils/riverpod_extensions.dart]`
  18. `[ ]` `@[client_app_v2/lib/shared/models/i18n_text.dart]`
  19. `[ ]` `@[client_app_v2/lib/shared/models/sdui_block_dto.dart]`
  20. `[ ]` `@[client_app_v2/lib/features/settings/domain/models/app_settings_state.dart]`

---

### Askel 5.2: Frontend Karkaisuaalto F2 — Freezed Domain & DTO Models + Riverpod Controllers & Providers (44 tiedostoa)
* **Seurantadokumentti (`[NEW]`):** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Execution Freezed Models (18 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]`
  2. `[ ]` `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`
  3. `[ ]` `@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]`
  4. `[ ]` `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]`
  5. `[ ]` `@[client_app_v2/lib/features/execution/models/execution_metadata.dart]`
  6. `[ ]` `@[client_app_v2/lib/features/execution/models/execution_metrics_dto.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/execution/models/execution_record.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/execution/models/execution_step.dart]`
  9. `[ ]` `@[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart]`
  10. `[ ]` `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]`
  11. `[ ]` `@[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]`
  12. `[ ]` `@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]`
  13. `[ ]` `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`
  14. `[ ]` `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]`
  15. `[ ]` `@[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]`
  16. `[ ]` `@[client_app_v2/lib/features/execution/models/tda_state.dart]`
  17. `[ ]` `@[client_app_v2/lib/features/execution/models/trace_context_carrier.dart]`
  18. `[ ]` `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]`
* **Paketti 2 — Studio & Reports Freezed Models + Cloner Utils (14 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/features/reports/models/report_artifact.dart]`
  2. `[ ]` `@[client_app_v2/lib/features/studio/models/blueprint_config.dart]`
  3. `[ ]` `@[client_app_v2/lib/features/studio/models/gcp_location.dart]`
  4. `[ ]` `@[client_app_v2/lib/features/studio/models/llm_platform.dart]`
  5. `[ ]` `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`
  6. `[ ]` `@[client_app_v2/lib/features/studio/models/model_config.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`
  9. `[ ]` `@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`
  10. `[ ]` `@[client_app_v2/lib/features/studio/models/step_simulation.dart]`
  11. `[ ]` `@[client_app_v2/lib/features/studio/models/workflow.dart]`
  12. `[ ]` `@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]`
  13. `[ ]` `@[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart]`
  14. `[ ]` `@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]`
* **Paketti 3 — Riverpod Controllers & State Providers (12 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`
  2. `[ ]` `@[client_app_v2/lib/features/execution/providers/atom_result_provider.dart]`
  3. `[ ]` `@[client_app_v2/lib/features/execution/providers/hydrated_reference_provider.dart]`
  4. `[ ]` `@[client_app_v2/lib/features/execution/providers/report_data_v2_provider.dart]`
  5. `[ ]` `@[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart]`
  6. `[ ]` `@[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]`
  9. `[ ]` `@[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart]`
  10. `[ ]` `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]`
  11. `[ ]` `@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]`
  12. `[ ]` `@[client_app_v2/lib/features/studio/controllers/studio_controller.dart]`

---

### Askel 5.3: Frontend Karkaisuaalto F3 — Execution, Reports & Shared SDUI / Presentation Widgets (47 tiedostoa)
* **Seurantadokumentti (`[NEW]`):** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Execution & Reports Views and SDUI Widgets (21 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`
  2. `[ ]` `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`
  3. `[ ]` `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]`
  4. `[ ]` `@[client_app_v2/lib/features/execution/views/execution_view.dart]`
  5. `[ ]` `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`
  6. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/diagnostic_scorecard_widget.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]`
  9. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]`
  10. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart]`
  11. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_alert_box_widget.dart]`
  12. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]`
  13. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`
  14. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_grid_widget.dart]`
  15. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`
  16. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/sdui_node_renderer.dart]`
  17. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]`
  18. `[ ]` `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]`
  19. `[ ]` `@[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]`
  20. `[ ]` `@[client_app_v2/lib/features/reports/views/execution_reports_view.dart]`
  21. `[ ]` `@[client_app_v2/lib/features/reports/views/widgets/report_artifact_card.dart]`
* **Paketti 2 — Shared Cross-Domain Widgets (`client_app_v2/lib/shared/widgets/`, 26 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]`
  2. `[ ]` `@[client_app_v2/lib/shared/widgets/comparison_matrix.dart]`
  3. `[ ]` `@[client_app_v2/lib/shared/widgets/deep_dive_expander.dart]`
  4. `[ ]` `@[client_app_v2/lib/shared/widgets/dynamic_form.dart]`
  5. `[ ]` `@[client_app_v2/lib/shared/widgets/execution_timeline.dart]`
  6. `[ ]` `@[client_app_v2/lib/shared/widgets/feedback_section.dart]`
  7. `[ ]` `@[client_app_v2/lib/shared/widgets/file_input_field.dart]`
  8. `[ ]` `@[client_app_v2/lib/shared/widgets/file_uploader.dart]`
  9. `[ ]` `@[client_app_v2/lib/shared/widgets/generic_grid.dart]`
  10. `[ ]` `@[client_app_v2/lib/shared/widgets/global_error_view.dart]`
  11. `[ ]` `@[client_app_v2/lib/shared/widgets/log_viewer.dart]`
  12. `[ ]` `@[client_app_v2/lib/shared/widgets/logic_matrix_chart.dart]`
  13. `[ ]` `@[client_app_v2/lib/shared/widgets/logic_radar_chart.dart]`
  14. `[ ]` `@[client_app_v2/lib/shared/widgets/omni_input_box.dart]`
  15. `[ ]` `@[client_app_v2/lib/shared/widgets/output_renderer.dart]`
  16. `[ ]` `@[client_app_v2/lib/shared/widgets/pdf_export_guide_dialog.dart]`
  17. `[ ]` `@[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]`
  18. `[ ]` `@[client_app_v2/lib/shared/widgets/quadrant_matrix_chart.dart]`
  19. `[ ]` `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`
  20. `[ ]` `@[client_app_v2/lib/shared/widgets/schema_mapper.dart]`
  21. `[ ]` `@[client_app_v2/lib/shared/widgets/score_card.dart]`
  22. `[ ]` `@[client_app_v2/lib/shared/widgets/score_card_radar.dart]`
  23. `[ ]` `@[client_app_v2/lib/shared/widgets/specialist_section.dart]`
  24. `[ ]` `@[client_app_v2/lib/shared/widgets/unified_metric_gauge.dart]`
  25. `[ ]` `@[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]`
  26. `[ ]` `@[client_app_v2/lib/shared/widgets/workflow_selector.dart]`

---

### Askel 5.4: Frontend Karkaisuaalto F4 — Quorum Studio Master Views, Profile Block Editors & Workflow Canvas Widgets (53 tiedostoa)
* **Seurantadokumentti (`[NEW]`):** `@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]`
* **Suorituskomento:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
  ```
* **Paketti 1 — Studio Master Views & Core Components (16 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]`
  2. `[ ]` `@[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]`
  3. `[ ]` `@[client_app_v2/lib/features/studio/views/components/clone_entity_button.dart]`
  4. `[ ]` `@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]`
  5. `[ ]` `@[client_app_v2/lib/features/studio/views/matrix_editor_view.dart]`
  6. `[ ]` `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`
  9. `[ ]` `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`
  10. `[ ]` `@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]`
  11. `[ ]` `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]`
  12. `[ ]` `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]`
  13. `[ ]` `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]`
  14. `[ ]` `@[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]`
  15. `[ ]` `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`
  16. `[ ]` `@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]`
* **Paketti 2 — Studio Widgets, Dialogs & Workflow Tabs (21 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/contrastive_pair_editor.dart]`
  2. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/dag_canvas_view.dart]`
  3. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/dynamic_item_list_editor.dart]`
  4. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/expected_input_editor_box.dart]`
  5. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]`
  6. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/inspector_pane.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/linguistic_shield_banner.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]`
  9. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/prompt_preview_dialog.dart]`
  10. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]`
  11. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`
  12. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]`
  13. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart]`
  14. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/tag_chip_input.dart]`
  15. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart]`
  16. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_inputs_tab.dart]`
  17. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]`
  18. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]`
  19. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]`
  20. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/xai/fallback_error_card.dart]`
  21. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/xai/matrix_observability_accordion.dart]`
* **Paketti 3 — Output Profile Block Cards & Tabs (16 tiedostoa):**
  1. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]`
  2. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]`
  3. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]`
  4. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart]`
  5. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`
  6. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]`
  7. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]`
  8. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]`
  9. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]`
  10. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/variance_block_card.dart]`
  11. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]`
  12. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]`
  13. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]`
  14. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]`
  15. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]`
  16. `[ ]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart]`
* **Laatuvarmennus (Kaikki Frontend-aallot F1–F4):**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

### Askel 6: Suorita GCP-tuotantopystytys, `qrum.ai` Domain, Worker/WeasyPrint-kontitus, Flutter Web Hosting & CI/CD (Vaihe 5)
* **Tavoite:** Provisioi GCP europe-north1 -resurssit (Cloud SQL PG19, Cloud Run API & Worker, Memorystore Redis, Secret Manager, Cloud Armor, Cloud Load Balancer), kytke Google-Managed SAN SSL `api.qrum.ai`-, `app.qrum.ai`- ja `studio.qrum.ai`-osoitteille sekä varmista konttien, taustatyöntekijän, Flutter Webin ja CI/CD-putken täysi tuotantovalmius.
* **Tuotantokriittiset Invariantit (Disaster Recovery, Container Sovereignty & Zero-Downtime):**
  1. **Cloud SQL PostgreSQL 19 PITR & Varmuuskopiot:** Automaattiset päivittäiset varmuuskopiot, transaktiologit (WAL) ja Point-in-Time Recovery (PITR) 14 päivän palautusikkunalla.
  2. **Nollakatkon Elossapito- ja Valmiustarkistukset (`/api/v2/system/health`, `/healthz` & `/ready`):** Cloud Run liveness probe (`/healthz`: Uvicorn elää) ja readiness probe (`/ready` / `/api/v2/system/health`: nopea <10 ms asynkroninen PostgreSQL- ja Redis-ping `[NEW]` `HealthCheckResponseDTO`-vasteella ennen liikenteen ohjausta konttiin) takaamaan virheettömät nollakatkon päivitykset (Zero-Downtime Rolling Deployments).
  3. **Idempotentti Tuotantomigraatio (Zero-Downtime Migration Runner):** Cloud Run -konttien käynnistyksessä ajettava automaattinen `run_migrations`-tarkistus (`@[backend_v2/database/postgres/pool.py]`), joka verifioi DDL-taulujen tilan ilman manuaalisia toimenpiteitä tai seisokkeja.
  4. **Osa 6A — Arq-taustatyöntekijän (`quorum-worker`) ja WeasyPrintin kontitus Cloud Runiin (`@[backend_v2/Dockerfile]` & `@[backend_v2/worker.py]`):**
     * **WeasyPrint Linux C -kirjastot ja UTF-8/Pohjoismaiset fontit:** Varmistetaan, että `@[backend_v2/Dockerfile]` asentaa tuotantokonttiin kaikki WeasyPrintin natiivikirjastot ja ääkköset (`ä, ö, å`) sisältävät fontit (nimenomaan ja tyhjentävästi: `libpango-1.0-0`, `libharfbuzz0b`, `libpangoft2-1.0-0`, `libgdk-pixbuf-2.0-0`, `libcairo2`, `libffi-dev`, `shared-mime-info`, `fonts-liberation` ja `fonts-noto-core`), jotta Vaiheen 3 PDF-raporttien generointi (`@[backend_v2/workers/report_worker.py]`) toimii Linux-kontissa ilman puuttuvia dynaamisia kirjastoja.
     * **Cloud Run Worker -prosessi (`quorum-worker`):** Koska Arq-worker (`arq backend_v2.worker.WorkerSettings`) on taustadaemon, `quorum-worker` ajetaan joko GCP:n **Cloud Run Worker Pool** -resurssina tai varustettuna `@[backend_v2/worker.py]`:n kevyellä asynkronisella `$PORT` HTTP health-check -kuuntelijalla, joka vastaa `200 OK` vain kun Arq Redis -yhteys on aktiivinen.
  5. **Osa 6B — Flutter Web (`app.qrum.ai` & `studio.qrum.ai`) Tuotantokäännös ja Cloud Hosting:**
     * Käännetään Flutter Web -tuotantopaketti ympäristömuuttujilla:
       ```powershell
       Set-Location client_app_v2; flutter build web --release --dart-define=API_BASE_URL=https://api.qrum.ai --dart-define=ENVIRONMENT=production
       ```
     * Julkaistaan staattinen `client_app_v2/build/web` -tuotantopaketti Firebase Hostingiin / Google Cloud Storage + Cloud CDN -taustapalveluun Cloud Load Balancerin (`qrum-lb`) taakse `app.qrum.ai`- ja `studio.qrum.ai`-verkkotunnuksille tiukoilla tietoturvaotsikoilla (`Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).
  6. **Osa 6C — CI/CD-julkaisuputki (Cloud Build / GitHub Actions) & Hallittu Cloud Run Job Seeding (`run_seed.py`):**
     * **Vaihe 1 (Laatuportit):** Jokainen tuotantojulkaisu ajaa pakollisena esiehtona `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` ja `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` sekä `uv run python scripts/sanitize_seed_vault.py --check`.
     * **Vaihe 2 (Artifact Registry):** Rakennetaan monivaiheinen (multi-stage) ei-root (`UID 10001`) Docker-image ja julkaistaan se Haminan GCP Artifact Registryyn (`europe-north1-docker.pkg.dev/quorum-prod/quorum-repo/quorum-api:$SHORT_SHA`).
     * **Vaihe 3 (Cloud Run Job — DDL & Seeding):** Ennen kuin uusi API- ja Worker-revisio saa liikennettä, suoritetaan eristetty **Cloud Run Job (`quorum-db-seed-job`)**, joka ajaa `001_pg19_uuidv7_schema.sql`-skeematarkistuksen ja idempotentin `uv run python backend_v2/seed/run_seed.py production` -upsertin Cloud SQL PostgreSQL 19 -kannalle.
* **Virallinen Eepos:** `@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`
* **Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`
* **Seurantadokumentti (Tracker):** `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`
* **1. Käynnistä automaattinen suoritus:**
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_GCP_Production_Deployment.md --model gemini-4-argon-high
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
  1. **Vaihe 1 — Pakollinen 2FA (TOTP) & RFC 8693 Token Exchange (`EPIC 160`):**
     * Kirjaudutaan Flutter-asiakkaalla (`app.qrum.ai` / Desktop) sisään 2FA-vahvistuksella (`firebase.sign_in_second_factor`), vaihdetaan token `POST /api/v2/iam/auth/exchange`-rajapinnassa 15 minuutin `Quorum Local JWT`:ksi (`sub: usr_<hex32>`, `org: org_<hex32>`, `mfa: true`) ja varmistetaan `< 0,1 ms` RAM-validointi.
  2. **Vaihe 2 — Direct-to-Cloud Signed URLs & Monikanavainen Ingressi (Luku 4):**
     * Ladataan syötetiedostot (`lopputuote.pdf`, `keskusteluhistoria.pdf`, `reflektiodokumentti.pdf`) suoraan pilvisäilöön 15 minuutin Signed PUT URL -putkella (`POST /api/v2/files/upload-request` -> PUT -> `POST /api/v2/files/{id}/confirm`) ilman että binäärit kuormittavat API-kontin RAM-muistia.
  3. **Vaihe 3 — DAG-suoritus, Kausaaligraafi & Asynkroninen Synteesi Natiivilla PostgreSQL 19 `UUIDv7` -kannalla (Askel 3.3):**
     * Suoritetaan koko moniaskeleinen työnkulku, jossa kaikki 12+2 taulua käyttävät natiivia 16-tavuista `UUIDv7`-avainta (`{prefix}_{32_hex}`), `execution_worker.py` ja `report_worker.py` kommunikoivat Redisin ja PostgreSQL 19:n kautta, ja BYOK `SecretService` injektoi avaimet pyyntökohtaisesti ilman lokivuotoja.
  4. **Vaihe 4 — Monikanavainen Raporttikoonti & Flutter SDUI Dumb Painter:**
     * Verifioidaan tuotetut artefaktit: 9-sivuinen WeasyPrint `report.pdf` (mukaan lukien ääkköset ja vektorikaaviot), `report.sdui.json`, `report.xlsx` ja `report.csv`, sekä tarkistetaan Flutter Web- ja Desktop -näkymissä ` HTTP 200 OK` ilman yhtäkään deserialisointi- tai teemavirhettä.
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
* Completed **Targeted Backend Hardening Wave 4 (`34/34` targets, Askel 3.2d)** across 23 Domain Models and 11 DTO/Prompt Schemas (commit `1af36b166`), bringing total backend hardening to `133/133` wave targets (`391/403` = `97.0%` of all `backend_v2/` production `.py` files locked).
* Executed and verified a full E2E baseline run (`exe_01a188e876717069b74a7b3716a02489`, report `rep_01a188ec1f0a7037b9a6713071b72386`) via `/tier6-execution-monitor` prior to starting **Askel 3.3** (`PASSED`, 8-page WeasyPrint PDF + Flutter Desktop `/rows` and `/sdui` `200 OK`, `healing_cost_events: 0`).
* Completed, hardened (`Tier 2 Hardening`), documented (`/tier7-describe-architecture`), and audited (`/tier8-audit-plan`) **Askel 3.3 (Malli A)** across both complementary implementation plans and trackers:
  1. `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]` & `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` (`15/15` targets hardened & locked: 12-table native PostgreSQL 19 `UUIDv7` schema, symmetric `PostgresEntityAdapter` UUID bridge, `seed_data.json` 32-hex `UUIDv7` cutover, `sanitize_seed_vault.py` auto-ID generator, Studio default anchor eradication, direct BARS causal cohesion matrix binding to `Step.criteria_block_ids`, and `@[docs/tiede.md]` zero-token topological ratios $r_{\text{LCC}}, r_{\text{conv}}, \kappa_{\text{steer}}$ + `simulate_counterfactual_retraction`).
  2. `@[docs/implementationplans/IMPLEMENTATION_PLAN_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` & `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]` (`31/31` targets hardened & locked: complete eradication of `uuid.uuid4()` and `Uuid().v4()` across Backend and Flutter, `generate_uuid7()` and `generateOpaqueUuid7(prefix)`, 32-hex `StrictOpaqueIdConverter`, and static guardrails `QGR030` and `DGR008`).

## Learned
* Both `StrictOpaqueIdConverter` on the Flutter client and `OPAQUE_STRIPE_ID_REGEX` / `PostgresEntityAdapter` on the Python backend enforce 32-hex RFC 9562 `UUIDv7` identifiers (`^[a-z]{2,5}_[a-f0-9]{32}$` with version nibble `7`), guarded statically by `QGR030` (`@[scripts/_ast_guardrails.py]`) and `DGR008` (`@[scripts/_dart_guardrails.py]`).
* `CausalCohesionEvaluator` enforces Equation (13) Guttman tier gates ($N_{\min}$, $r_{\text{LCC}}$, $r_{\text{conv}}$, $r_{\text{iso}}$, acyclicity) and executes deterministic $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ counterfactual retraction via `simulate_counterfactual_retraction` returning `CounterfactualSimulationResultDTO`.

## Resume Command
```text
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]
```

## Remaining
### Hardening State Snapshot
* **Backend Hardening Waves 1–4 + Askel 3.3 (`PrefixedUUID7` & `UUIDv4` Eradication):** `100% COMPLETED & LOCKED` (`391/403` = `97.0%` of `backend_v2/` hardened; `12` files remaining in Askel 4 IAM [`9` files] and Askel 5 Storage [`3` files]).
* **Immediate Next Task:** Execute **Askel 3.4** (`@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` and `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`), followed by **Askel 3.5** (`PostgresEntityAdapter` God Code decomposition).
