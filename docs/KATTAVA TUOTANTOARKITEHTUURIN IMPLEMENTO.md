# KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTOINTISUUNNITELMA (2026)
## GCP Cloud Run, PostgreSQL 19 Zero-ORM, B2B SaaS IAM & Cloud Storage

> [!NOTE]
> **Arkkitehtuurin tila ja Single Source of Truth (SSOT)**
> Tämä asiakirja kokoaa yhteen Cognitive Quorumin tuotantopystytyksen kokonaiskuvan Google Cloud Platformilla (`europe-north1` / Hamina, Suomi). Se korvaa vanhentuneet SQLAlchemy 2.0-, Alembic- ja TinyDB-luonnokset ja nojaa suoraan Quorumin virallisiin 2026-arkkitehtuuristandardeihin:
> 1. **PostgreSQL 19 Zero-ORM & Cutover** (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`, vaatimukset: `@[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]`)
> 2. **Kohdennettu Tausta- ja Apukerroksen Karkaisu** (Workers, SDUI Adapters, Utilities)
> 3. **B2B SaaS IAM, Token Exchange & Enterprise Hardening** (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`)
> 4. **Firebase Storage & Direct-to-Cloud Signed URLs** (`[NEW] @[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]`)
> 5. **Frontend & Studio UI Hardening** (Flutter Web & Desktop: Error Boundaries & Dumb Painter)
> 6. **GCP Production Deployment, Cloud Security & FinOps Hardening** (`@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`, tracker: `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`)

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

### 0.4 Verkkotunnukset, Reititys ja `quorum.ai` -varaus
Tuotannon verkkoinfrastruktuuri ja kuormantasaus konfiguroidaan tukemaan kansainvälistä pääverkkotunnusta **`quorum.ai`** (rinnalla toissijainen `quorum.fi`):
* **1. Verkkotunnuksen saatavuuden tarkistus ja hankinta (`quorum.ai` & `quorum.fi`):**
  * Ennen kuormantasaajan ja SSL-varmenteen pystytystä tarkistetaan `quorum.ai`- ja `quorum.fi`-verkkotunnusten saatavuus Google Cloud Domainsilla (`gcloud domains registrations search-domains quorum.ai`) tai valtuutetulla verkkotunnusvälittäjällä (Cloudflare Registrar `.ai`-tunnuksille ja Traficom-välittäjä `.fi`-tunnuksille).
  * **Mikäli `quorum.ai` on vapaana:** Rekisteröidään `quorum.ai` ensisijaiseksi globaaliksi verkkotunnukseksi ja `quorum.fi` rinnakkaiseksi kotimaiseksi verkkotunnukseksi sekä ohjataan nimipalvelimet (`NS`-tietueet) Google Cloud DNS -vyöhykkeeseen.
  * **Toimintamalli, mikäli `quorum.ai` on jo varattu kolmannelle osapuolelle:** Rekisteröidään vapaana oleva ensisijainen verkkotunnus (`cognitivequorum.ai` tai `quorum.fi`) ja asetetaan se Cloud Run -ympäristömuuttujiin (`PRIMARY_DOMAIN`, `JWT_ISSUER`, `JWT_AUDIENCE`, `CORS_ORIGINS`). Koska `@[backend_v2/settings.py#L54-L1053]` lukee kaikki domain- ja JWT-väitteet dynaamisesti ympäristömuuttujista (`AliasChoices`), Python- tai Flutter-lähdekoodiin ei tarvita yhtäkään koodimuutosta.
* **2. Domain-jako ja reititys (Cloud Load Balancer & Cloud DNS):**
  * `api.quorum.ai` $\rightarrow$ Cloud Run API (`quorum-api`) REST/SSE-rajapinnat.
  * `app.quorum.ai` / `studio.quorum.ai` $\rightarrow$ Flutter Web & Studio -käyttöliittymä.
  * `quorum.ai` $\rightarrow$ Yrityksen pääsivusto / landing page ja ohjaus sovellukseen.
  * `api.quorum.fi` & `app.quorum.fi` $\rightarrow$ Rinnakkaiset toissijaiset osoitteet automaattisella 301-ohjauksella tai rinnakkaistuella.
* **3. Google-Managed SSL/TLS -monivarmenne (SAN Certs):**
  * Luodaan Google-Managed SSL-sertifikaatti (`quorum-san-cert`), joka kattaa kaikki alidomainit (`quorum.ai`, `api.quorum.ai`, `app.quorum.ai`, `studio.quorum.ai`, `quorum.fi`, `api.quorum.fi`, `app.quorum.fi`) yhdellä globaalilla Anycast IP -osoitteella (`quorum-global-ip`).
* **4. Cloud DNS & SAN SSL -provisiointikomennot (PowerShell):**
  ```powershell
  gcloud domains registrations search-domains quorum.ai
  gcloud compute addresses create quorum-global-ip --global --ip-version IPV4
  gcloud dns managed-zones create quorum-ai-zone --dns-name="quorum.ai." --description="Cognitive Quorum Primary Production DNS Zone" --visibility=public
  gcloud dns record-sets create quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud dns record-sets create api.quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud dns record-sets create app.quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud dns record-sets create studio.quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
  gcloud compute ssl-certificates create quorum-san-cert --domains="quorum.ai,api.quorum.ai,app.quorum.ai,studio.quorum.ai,quorum.fi,api.quorum.fi,app.quorum.fi" --global
  ```
* **5. CORS & Origin Security (`@[backend_v2/settings.py#L54-L1053]`):**
  * API-ingress sallii nimenomaisesti tuotanto-originit: `https://quorum.ai`, `https://app.quorum.ai`, `https://studio.quorum.ai`, `https://quorum.fi`, `https://app.quorum.fi`.
* **6. Firebase Auth & OAuth Redirect URIs:**
  * Lisätään Firebase Authenticationin *Authorized Domains* -listalle: `quorum.ai`, `app.quorum.ai`, `api.quorum.ai`, `quorum.fi`, `app.quorum.fi`.
* **7. JWT Issuer & Audience SSOT:**
  * Quorum Local JWT:n token-väitteet: `iss = "https://api.quorum.ai"`, `aud = "https://quorum.ai"`.

---

## Luku 1: Zero-ORM Työkalupakki ja Ajonaikaiset Kirjastot

Tuotantoarkkitehtuurissa poistetaan kaikki demotason tiedostokannat (TinyDB) sekä raskaat välikädet (SQLAlchemy, Alembic, hashids).

### 1.1 Poistettavat legacy-riippuvuudet
* `tinydb` (tiedostopohjainen demotietokanta).
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

## Luku 2: Tietokantamallit ja Natiivi UUIDv7 (Zero-ORM SSOT)

PostgreSQL 19 on Single Source of Truth (SSOT) kaikelle sovellusdatalle. Tiedostojen binäärejä ei säilytetä relaatiokannassa, vaan kanta hallinnoi ainoastaan metadataa.

### 2.1 Pääavaimet ja RFC 9562 `PrefixedUUID7`
* Kaikki SQL-taulut käyttävät primääriavaimena PostgreSQL 19:n natiivia `uuidv7()`-arvoa (`UUID PRIMARY KEY DEFAULT uuidv7()`).
* Python- ja Flutter-rajapintakerroksessa avaimet sillataan tyyppiturvalliseen **`PrefixedUUID7`** -muotoon (`OPAQUE_STRIPE_ID_REGEX`):
  * Käyttäjät: `usr_<hex32>` (esim. `usr_01950000000070008000000000000001`)
  * Organisaatiot: `org_<hex32>`
  * Kutsut: `inv_<hex32>`
  * Salaisuudet (BYOK): `sec_<hex32>`
  * Graafisolmut: `nod_<hex32>`, Kaaret: `edg_<hex32>`, Suoritukset: `exe_<hex32>`

### 2.2 SQL DDL -skeema (`001_pg19_uuidv7_schema.sql`)
Kanta alustetaan ilman Alembicia suoralla, idempotentilla SQL DDL -tiedostolla:

```sql
-- PostgreSQL 19 Natiivi Skeema (Ote: users, organizations, file_metadata)

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

### 2.3 Pydantic V2 Domain-malli (`backend_v2/models/auth.py`)
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
* Avaimet puretaan EPIC 160:ssä luotavassa (created) `SecretService`-palvelussa pyyntökohtaisesti `pydantic.SecretStr`-muotoon ja injektoidaan LLM- ja MCP-kutsuille ilman lokivuotoja.

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

Tietokannan alustus ja testidata hoidetaan täysin ilman vanhoja JSON-tiedostoja:
* **DDL-migraatio:** `001_pg19_uuidv7_schema.sql` luo taulut idempotentisti (`CREATE TABLE IF NOT EXISTS`).
* **Seeding-skripti (`backend_v2/seed/run_seed.py`):**
  * Lukee järjestelmän pakolliset perustiedot (järjestelmäorganisaatio `ROOT_SYSTEM = "org_01950000000070008000000000000000"`, oletustyönkulut, prompt-lohkot).
  * Tarkistaa rivit Natural Key -kenttien perusteella, eikä luo tuplia toistuvissakaan CI/CD-ajoissa.

---

## Luku 6: Toteutustiekartta ja Riippuvuudet (The Master Waves)

Toteutus etenee vaiheittain ja matalariskisesti. Kaikki tekninen tekeminen kytkeytyy suoraan virallisiin Epiceihin ja hyväksyttyihin toteutussuunnitelmiin. Järjestys perustuu `@[docs/koodikannan_purku_ja_migraatiojarjestys.md]` -analyysiin, jolla eliminoidaan kaksoistyö ja estetään purettujen moduulien desynkronoituminen:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1A. LLM Strategy Monolithin purku (SUORITETTU & LUKITTU - EPIC 157)   │
│     llm.py (1 090 LOC) -> llm_strategy/ (4 erillistä vaihetta)         │
│     Plan: docs/epic/tasks_llm/ | Tracker: llm_decomposition_tracker.md │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 1B. LLM Provider -purku (SUORITETTU & LUKITTU - Vaihe 1B)              │
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
│ 2. PostgreSQL 19 Zero-ORM & dag_executor.py -purku (EPIC 151)          │
│    - asyncpg-allas, PrefixedUUID7, 12 taulua, Zero-ORM (ei SQLAlchemy) │
│    - TinyDB-lukkojen poisto & dag_executor.py (1 640 LOC) purku        │
│      tapahtumapohjaiseen trace_events-malliin (wave_scheduler jne.)    │
│    Plan: docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 3. B2B SaaS IAM & Hardening (EPIC 160)                                 │
│    Token Exchange (RAM <0,1 ms), Redis Kill-Switch, BYOK SecretService │
│    Epic: docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 4. Storage & Tiedostopalvelut (Tämä suunnitelma, Luku 4)               │
│    Firebase Storage Signed URLs, FileMetadata, orposiivous             │
│    Plan: docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────────────┐
│ 5. GCP Tuotantopystytys & quorum.ai Domain (EPIC 74 & Pilvi-infra)                  │
│    Cloud SQL PG19, Cloud Run API & Worker, Memorystore, Secret Manager              │
│    Google-Managed SSL (api.quorum.ai, app.quorum.ai, quorum.fi)                    │
│    Epic: docs/epic/EPIC_74_Production_Deployment_GCP.md                             │
│    Plan: docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md │
│    Tracker: docs/implementationplans/TRACKER_GCP_Production_Deployment.md          │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Luku 7: Monoliittien ja "God Code" -arkkitehtuurin Purkukartta (Master SSOT)

Jotta tuotantokoodi on testattavaa, helposti ylläpidettävää ja skaalautuvaa, Quorumin arkkitehtuurisäännöt (`@[ki_god_code_prevention.md]`) vaativat kaikkien historiallisten monoliittien purkamisen pieniin, yhden vastuun luokkiin ja palveluihin (Single Responsibility Principle & Hexagonal CQRS).

Koodikannassa on kartoitettu ja aikataulutettu kaikki 12 kriittistä monoliittialuetta. Jokaisella on oma virallinen eepoksensa tai toteutussuunnitelmansa, ja niiden purku on sidottu tarkasti oikeisiin aaltoihin:

| Monoliitti / God Code -alue | Alkuperäinen koko & riski | Purkutoimenpide & tavoitearkkitehtuuri | Virallinen Epic / Toteutussuunnitelma | Suoritusvaihe & Tila |
| :--- | :--- | :--- | :--- | :--- |
| **1. DAG Workflow Executor** | `backend_v2/services/orchestrator/dag_executor.py`<br>**1 640 LOC** (koko järjestelmän suurin tiedosto, `execute_workflow` 1 118 LOC). Raskas TinyDB-lukitus (`_update_lock`), tilablobien uudelleenkirjoitus. | Puretaan 4 itsenäiseen moduuliin:<br>1. `wave_scheduler.py` (Kahnin aallot)<br>2. `state_machine.py` (`trace_events` append-only)<br>3. `cancellation_manager.py` (DLQ/TaskGroup)<br>4. `telemetry_broadcaster.py` (SSE/WS) | **PostgreSQL 19 & Event Sourcing**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`<br>`@[docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md]` | **Vaihe 2**<br>Puretaan PostgreSQL-migraation yhteydessä (ks. perustelu alla) |
| **2. LLM Provider Core & Engine** | `backend_v2/llm/provider.py`<br>**1 846 LOC**. Yhdisti semaforit, dynaamisen nopeusrajoituksen, LiteLLM-kutsut, hinnoittelun ja transienttien virheiden luokittelun. | Purettu 7 modulaariseen alitiedostoon paketissa `backend_v2/llm/provider/`: `env_and_schema_utils.py`, `transient_retry_policy.py`, `base_and_mock_provider.py`, `provider_factory.py`, `litellm_response_stage.py`, `litellm_provider.py` ja 93 LOC fasaadi `__init__.py`. Monoliitti poistettu ja lukittu AST-säännöllä `QGR017`. | **Provider Decomposition Plan**<br>`@[docs/epic/provider_decomposition_tracker.md]`<br>`@[docs/epic/tasks_provider/]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017`, 52 yksikkötestiä läpäisty (99 % kattavuus), 0 sanakirjarikkomusta, Tier 8 Red-Team auditoitu |
| **3. LLM Strategy & Orchestrator** | `backend_v2/services/orchestrator/strategies/llm.py`<br>**1 090 LOC**. Vastasi yhtä aikaa prompteista, skeemoista, työkaluista, LLM-kutsusta ja telemetriasta. | 4-vaiheinen Strangler Fig -pilkonta pakettiin `llm_strategy/`: `blueprint_and_metadata_stage`, `prompt_and_schema_stage`, `engine_retry_stage`, `trace_event_stage` ja fasaadi `__init__.py` (< 200 LOC). Monoliitti tuhotaan. | **EPIC 157**<br>`@[docs/epic/llm_decomposition_tracker.md]`<br>`@[docs/epic/tasks_llm/]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` (hashit `b9d66471a`, `3f04a6e2f`) |
| **4. Tietokantaydin & Tallennus** | `tinydb_driver.py`, `firestore_driver.py` ja `db_v2.json.lock`. Keräsivät sanakirjoja (`dict[str, Any]`), estivät rinnakkaisuuden ja lukitsivat levyn. | Korvataan puhtaalla Zero-ORM -arkkitehtuurilla: heksagonaaliset CQRS-portit (`GraphMutationPort`, `EntityPersistencePort`), `PostgresPoolManager` (`asyncpg`) ja binääriset `pydantic_core` Rust-koodekit. | **PostgreSQL 19 Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` | **Vaihe 2**<br>Valmis suunnitelma, alkaa heti LLM-purkujen jälkeen |
| **5. Taustatyöntekijät (Workers)** | `backend_v2/worker.py`<br>**2 000+ LOC**. Sekoitti Arq-daemonin käynnistyksen, raskaat DAG-analyysit ja raporttien generoinnin yhteen sekamelskaan. | Pilkottu kolmeen: `worker.py` on pelkkä ohut daemon-käynnistys; raskas laskenta on `backend_v2/workers/execution_worker.py` ja raporttien renderöinti `backend_v2/workers/report_worker.py`. | **Worker Decoupling Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Tripartite_Pipeline_Isolation_and_Worker_Decoupling.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` |
| **6. Raportointipalvelu** | `backend_v2/services/report_service.py`<br>**749 LOC**. Käsitteli raporttien elinkaarta, Markdown/PDF-kasausta ja tiedostolukua. | Purettu pakettiin `backend_v2/services/report/`: `lifecycle_service.py`, `compilation_service.py`, `format_reader_service.py`. | **Report Service Decomposition**<br>`@[docs/koodikannan_purku_ja_migraatiojarjestys.md]` | **SUORITETTU & LUKITTU**<br>Vanha tiedosto poistettu |
| **7. Raporttiviennin Flattenerit** | `backend_v2/services/export_service.py` (**1 123 LOC**) & aiemmin määritelty (defined) `FlatFileService`. Keräsivät sanakirjamutaatioita ja konvertoivat graafeja löyhästi yhden rivin konevektoreiksi. | Monoliittinen flattener tuhottu; korvattu tyypitetyillä Pydantic V2 DTO-virroilla (`ExportMatrixSummaryRowDTO`, `ExportForensicAtomDTO`, `ExportPayloadDTO`) ja modulaarisella `backend_v2/services/export/` -paketilla. | **Export Tables SSOT Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md]` | **SUORITETTU & LUKITTU**<br>`ki_god_code_prevention.md` |
| **8. Matriisidomainin Jäsennin** | `backend_v2/services/matrix_domain_parser.py`<br>**732 LOC**. Sekoitti asteikot, atomien jäsennyksen, jakaumamuotoilun ja rivien rakentamisen. | Purettu pakettiin `backend_v2/services/matrix_parser/`: `scale_and_atom_stage.py`, `row_builder_stage.py`, `distribution_formatter.py`. | **Matrix Parser Decomposition**<br>`@[docs/epic/matrix_domain_parser_decomposition_tracker.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` |
| **9. Sitaattien Lexical Verifier** | `backend_v2/services/orchestrator/anchor_validation_service.py`<br>**855 LOC**. Hoiti yhtä aikaa tekstin normalisoinnin, fuzzy-tarkistuksen, morfologian ja tilasiirtymät. | Pilkottu modulaariseksi paketiksi `backend_v2/services/orchestrator/anchor_validation/`: `lexical_normalizer.py`, `lexical_matcher.py`, `evidence_validator.py`, `atom_evaluation_processor.py`. | **Anchor Validation Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Multilingual_Rule_Based_Stemming_in_Anchor_Validation.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` |
| **10. Keskustelun PDF-ingressi** | `backend_v2/services/ingress/pdf_chat_extractor.py`<br>**682 LOC**. Sekoitti Skia-vektoripiirron, taulukoiden rekonstruoinnin ja puheenvuorojen segmentoinnin. | Pilkottu 3-vaiheiseksi liukuhihnaksi `backend_v2/services/ingress/pdf_extractor/`: `bubble_geometry.py`, `table_and_card_stage.py`, `turn_assembly_stage.py` ja fasaadiksi `pdf_extractor/__init__.py`. | **Chat Ingress SSOT**<br>`@[ki_chat_ingress_and_provenance_architecture.md]` | **SUORITETTU & LUKITTU**<br>Kovennettu AST-säännöllä `QGR017` |
| **11. SDUI UI-Mäppääjä** | `backend_v2/services/sdui_mapper_service.py` (juurimonoliitti). Yhdisti laskentalogiikan ja Dumb Painter -renderöinnin. | Juurimonoliitti tuhottu ja siirretty kanoniseen paikkaan `backend_v2/services/sdui/sdui_mapper_service.py`. | **SDUI Dumb Painter Plan**<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md]` | **SUORITETTU & LUKITTU**<br>Juurimonoliitti poistettu |
| **12. Dynaaminen MCP & Työkalukutsu** | `backend_v2/services/mcp/mcp_tool_loop.py` (**651 LOC**) ja Flutterin `StepBuilderView` (lomakemonoliitti). Kovakoodatut työkalut ja kytkökset. | Staattiset työkalut poistettu; korvattu protokolla-agnostisella `GenericMCPClient`:llä, `SchemaFactory`:lla ja JIT-syntetisoijalla. Flutterissa eristetty `McpToolParamsPanel`. | **EPIC 159 (Dynamic MCP)**<br>`@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]`<br>`@[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]` | **SUORITETTU & KOVENNETTU**<br>`GenericMCPClient` tuotannossa |

---

### Kriittiset arkkitehtoniset säännöt purkujen ajoitukselle:

#### Miksi `dag_executor.py` puretaan nimenomaan PostgreSQL-migraatiossa (Vaihe 2)?
* **Syy:** `dag_executor.py`:n 1 640 rivistä yli 70 % liittyy nykyiseen **TinyDB-tiedostolukitukseen** (`_update_lock`, `msvcrt/fcntl`) ja monen megatavun `execution_trace`-blobin toistuvaan sarjallistamiseen levylle.
* Jos `dag_executor.py` yritettäisiin pilkkoa ennen PostgreSQL-vaihetta, jouduttaisiin rakentamaan monimutkaisia väliaikaisia lukitus- ja tilanhallintamoduuleita tiedostokannalle — ja heittämään ne heti perään roskiin tietokantamigraatiossa.
* PostgreSQL 19:ssä siirrytään **append-only `trace_events` -tapahtumavirtaan** (`asyncpg`), jolloin koko tiedostolukitus poistuu luonnostaan. `dag_executor.py` puretaan suoraan neljään puhtaaseen tapahtumamoduuliin (`wave_scheduler.py`, `state_machine.py`, `cancellation_manager.py`, `telemetry_broadcaster.py`) ilman väliaikaista koodijätettä.

#### Miksi `provider.py` ja LLM-ydin purettiin heti LLM Strategian jälkeen (Vaihe 1B)?
* **Syy:** EPIC 159 (Dynamic MCP) oli jo poistanut vanhat staattiset työkalut (`tavily.py`, `wikipedia.py`, `models/domain/tools.py`) ja stabiloinut `GenericMCPClient`:in ja `ToolDispatcher`:in.
* Kun `strategies/llm.py` valmistui (Vaihe 1A), koko LLM-infrastruktuuri oli puhdas vanhoista MCP-riippuvuuksista. Tällöin `provider.py` voitiin pilkkoa puhtaaksi paketiksi `backend_v2/llm/provider/` ennen tietokantamigraatiota, jolloin PostgreSQL- ja `dag_executor.py` -vaiheeseen siirrytään täysin modernisoidulla LLM-infrastruktuurilla.

---

## Luku 8: Ihmisen Ohjauskeskus ja Työjärjestys (Human Executive Playbook)

> [!IMPORTANT]
> **Kaikki tekeminen tapahtuu suunnitelmien ja epicien kautta**
> Kehittäjän tai tekoälyn ei tule koskaan ryhtyä kirjoittamaan suoraa koodia tai muuttamaan arkkitehtuuria ilman hyväksyttyä toteutussuunnitelmaa (`IMPLEMENTATION_PLAN_*.md`) ja seurantatiedostoa (`TRACKER_*.md`). Tämä takaa, että jokainen muutos testataan automaattisissa laatuporteissa (`universal_quality_gates`).

Alla on ihmiselle tarkoitettu selkeä, komentotasoinen etenemispolku askel askeleelta:

### Askel 1: Saata maaliin LLM Strategy -purku (Vaihe 1A) — [SUORITETTU & LUKITTU]
* **Tavoite:** Viimeistele `backend_v2/services/orchestrator/strategies/llm.py`:n poisto ja paketin `llm_strategy/__init__.py` käyttöönotto.
* **Seurantatiedosto:** `@[docs/epic/llm_decomposition_tracker.md]`
* **Tila:** Suoritettu ja kovennettu (hash `b9d66471a`, Tier 2 Hardening `3f04a6e2f`). Monoliitti poistettu ja korvattu 199-rivisellä fasaadilla `llm_strategy/__init__.py`.
* **Laatuvarmennus:** 10/10 laatuporttia läpäisty (`58 passed, 99.53%` kattavuus).

---

### Askel 2: Suorita LLM Provider & Client Engine -purku (Vaihe 1B) — [SUORITETTU & LUKITTU]
* **Tavoite:** Pura `backend_v2/llm/provider.py` (1 846 LOC) modulaariseksi paketiksi `backend_v2/llm/provider/`, eristä fasaadi `__init__.py` (< 100 LOC), poista monoliitti ja lukitse se AST-säännöllä `QGR017`.
* **Seurantatiedosto:** `@[docs/epic/provider_decomposition_tracker.md]`
* **Tila:** Suoritettu, kovennettu ja auditoitu (10/10 Epoch 2 -karkaisukohdetta läpäisty, Tier 7 As-Built dokumentaatiosynkronointi ja Tier 8 System 2 Red-Team Audit suoritettu). Monoliitti tuhottu ja korvattu 93-rivisellä fasaadilla `backend_v2/llm/provider/__init__.py`.
* **Laatuvarmennus:** 10/10 backend-laatuporttia läpäisty, 52 yksikkötestiä läpäisty (99 % testikattavuus), 0 sanakirjarikkomusta (`audit_dict_eradication.py`), 395/395 puhdasta tuontimoduulia (`audit_clean_imports.py`), `QGR017` aktiivisena.

---

### Välivaiheen Todentaminen: Päästä päähän (E2E) -suoritusajon Varmennus Ennen PostgreSQL-toteutusta — [SUORITETTU & VERIFIOITU]
> [!IMPORTANT]
> **Toimintakunnon peruskivi ennen tietokantavaihetta (PostgreSQL 19 Zero-ORM)**
> Ennen tietokantakerroksen ja `dag_executor.py`:n purkamista varmistettiin ja auditoitiin koko järjestelmän virheetön toimintakunto ajamalla täydellinen monivaiheinen tuotantoajo paikallisessa ajoympäristössä (`run_local.bat` + `/tier6-execution-monitor`). Ajo todisti, että puretut LLM Strategy- ja LLM Provider -moduulit toimivat saumattomasti osana koko elinkaarta.
> 
> * **Suoritus-ID:** `exe_2af2f7665e7c477b` (Työnkulku: `wf_a8f1d71000000001`, Raportti: `rep_210bacbab69246c4`)
> * **Ajankohta & Kesto:** 27.10.2026 klo 09:42:10 – 09:47:45 UTC+02:00 (5 min 35 s)
> * **Tila & Git Commit:** 🟢 **PASSED & FINALIZED (100 % E2E Pariteetti)** — Commit `3f3f3d941` (*docs(architecture): record verified e2e execution exe_2af2f7665e7c477b prior to postgresql*)
> * **Forensiikkaraportti:** `@[data/files/executions/exe_2af2f7665e7c477b/forensic_summary.md]`
> * **Tallennetut fyysiset artefaktit:**
>   * `report.pdf` (185.9 KB, 9-sivuinen WeasyPrint-johdon raportti)
>   * `report.sdui.json` (361.8 KB, SDUI-lohkot Flutter- ja Web-esitykselle)
>   * `report.xlsx` (13.9 KB, Excel-matriisivienti)
>   * `report.csv` (18.1 KB, litteä forensiikkavienti)
>   * `execution_trace.json` (375.8 KB) & `context_variables.json` (405.5 KB)
> * **Todennettu ketju askel askeleelta:**
>   1. **Vaihe 1 (DAG Heavy LLM Execution):** Ingressi ja RAG-esilento purkivat 3 binaarista PDF:ää (`lopputuote.pdf`, `keskusteluhistoria.pdf`, `reflektiodokumentti.pdf`) sekä dynaamisen luontipäivämäärän (`2026-06-25T07:38:55+03:00`). Arvioitiin 4 matriisilohkoa (`blk_f921c7c0989b47e8`, `blk_f6e286f050c94d60`, `blk_440a5fef9331451b`, `blk_7d8e9f0a1b2c3d4e`), dynaaminen kausaalilinkitys (16 atomia supistettu 4:ään `MatrixReducer`:illa), ja suoritettiin pisteiden normalisointi (keskiarvo 5.7, 0 sakkoa). Tila: **PASSED**.
>   2. **Vaihe 2 (Asynkroninen synteesi & varianssianalyysi):** Tuotettiin rinnakkain johdon tiivistelmä, matriisiosioiden synteesit ja XAI-nostot. Mekaanis-kognitiivinen varianssianalyysi laski varianssin (3.6675, `MISALIGNED`) ja loi sanallisen selityksen.
>   3. **Vaihe 3 (Monikanavainen raporttikoonti & vienti):** Koottiin 9-sivuinen WeasyPrint PDF, SDUI-renderöintipuu, Excel ja CSV.
>   4. **Vaihe 4 (Flutter Desktop -asiakasohjelman pariteetti):** Flutter Desktop -asiakas nouti raportin ja SDUI-lohkot onnistuneesti (`/reports/rep_210bacbab69246c4/sdui` ja `/rows` HTTP 200 OK) ilman yhtäkään deserialisointi- tai käyttöliittymävirhettä.
>   5. **FinOps & Telemetria (`finops_trace_analyzer.py`):** 0 itseparannustoistoa (`healing_cost_events = 0`), 0 transienttia HTTP 429 -virhettä, provider pacing (0.3s–1.0s) toimi virheettömästi.

---

### Askel 3: Suorita PostgreSQL 19 Zero-ORM & `dag_executor.py` -purku (Vaihe 2)
* **Lähtötilanteen varmennus:** Ennen tämän askeleen aloitusta koko järjestelmän suorituskyky ja elinkaari on todennettu onnistuneella tuotantoajolla `exe_2af2f7665e7c477b` ja lukittu commitiin `3f3f3d941` (ks. yllä oleva Välivaiheen Todentaminen ja `@[data/files/executions/exe_2af2f7665e7c477b/forensic_summary.md]`).
* **Tavoite:** Korvaa TinyDB ja JSON-levylukot PostgreSQL 19:llä, `asyncpg`:llä ja `trace_events` append-only -tapahtumavirralla. Pura samalla `dag_executor.py` (1 640 LOC) neljään suoritusmoduuliin.
* **Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` (EPIC 151)
* **1. Luo seurantatiedosto:**
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]"
  ```
* **2. Käynnistä automaattinen vaiheittainen toteutus:**
  ```powershell
  uv run python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_PostgreSQL.md --model gemini-4-argon-high
  ```
  tai suoraan itsenäisessä CLI-sessiossa:
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[docs/implementationplans/TRACKER_PostgreSQL.md] --full-auto. PERMISSION GRANTED for continuous full-auto execution across all steps. Proceed autonomously through all steps without intermediate confirmations."
  ```
* **Laatuvarmennus:**
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/database/ --test --ast-strict
  uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/execution/ --test --ast-strict
  ```

---

### Askel 3.1: PostgreSQL 19 Lopullinen Cutover, TinyDB:n Poisto & Täysi Live E2E -Testiajo (Vaihe 2b)
* **Siirtymä ja Lähtötilanteen Vaikutusanalyysi:**
  Kun PostgreSQL 19 -perusinfrastruktuuri ja sen tiedostokohtainen hardening (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` ja `@[docs/implementationplans/TRACKER_PostgreSQL.md]`) saavuttavat 100 % hyväksynnän, toteutetaan **Lopullinen Cutover (TinyDB Eradication)** vaatimusmäärittelyn `@[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]` mukaisesti ennen siirtymistä B2B SaaS IAM -vaiheeseen (Askel 4).
  * **Vaikutus ja saavutettu pohja:** `IMPLEMENTATION_PLAN_PostgreSQL.md`:n ja `TRACKER_PostgreSQL.md`:n valmistuttua DDL-skeema (`001_pg19_uuidv7_schema.sql`), `PostgresPoolManager`, `PostgresEntityAdapter`, `PostgresGraphAdapter` ja `PostgresUnitOfWork` ovat jo valmiina, karkaistuina ja 100 % Zero-ORM AST -valvottuina.
  * **Cutoverin täsmällinen fokus:** Cutoverissa keskitytään puhtaasti TinyDB:n ja tiedostolukitusten fyysiseen poistamiseen, `run_seed.py`:n uudelleenohjaukseen PostgreSQL 19:ään, `run_local.bat`:n pysyvään siirtämiseen `STORAGE_BACKEND=POSTGRES` -tilaan, `tinydb`-paketin poistoon `pyproject.toml`:sta sekä `QGR017`-AST-laatuportin lukitsemiseen.
* **Toteutus Quorumin Normaalilla Projektitavalla:**
  1. **Tier 0 Tutkimus ja Vaikutusanalyysi:**
     ```powershell
     agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier0-research-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]"
     ```
  2. **Tier 1 Suunnittelu ja Seuranta:**
     Luodaan `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]` ja `@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`:
     ```powershell
     agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]"
     ```
  3. **Tier 2 Autonominen Suoritus:**
     ```powershell
     uv run python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md --model gemini-4-argon-high
     ```
  4. **Tier 2 Autonominen Hardening (Tiedostokohtainen Laatuportti):**
     ```powershell
     uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate backend --model gemini-4-argon-medium --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
     ```
  5. **Täysi Live E2E -Testiajo (Gate 8 Pariteetti- ja Toimintavarmennus):**
     Käynnistetään järjestelmä `run_local.bat`-skriptillä PostgreSQL 19 -kontin kanssa ja ajetaan täydellinen monivaiheinen E2E-ajo (`run_workflow_simulation.py` tai `/tier6-execution-monitor`), joka verifioi:
     * **Vaihe 1 (DAG Heavy LLM Execution):** Tilasiirtymät ja Kahn-aallot tallentuvat suoraan PostgreSQL:n `executions`- ja `trace_events`-tauluihin ilman tiedostolukituksia.
     * **Vaihe 2 (Asynkroninen synteesi):** Varianssianalyysi ja synteesit tuotetaan rinnakkain.
     * **Vaihe 3 (Monikanavainen vienti):** Koostetaan ja tallennetaan `report.pdf`, `report.sdui.json`, `report.xlsx` ja `report.csv`.
     * **Vaihe 4 (Frontend-pariteetti):** Flutter Desktop ja Web noutavat raportin ja SDUI-lohkot virheettömästi (HTTP 200).
     * **FinOps & Observability:** 0 itseparannustoistoa (`healing_cost_events = 0`), täysi pariteetti aiempaan `exe_2af2f7665e7c477b`-ajoon.
  6. **Tier 7 Dokumentointi & Tier 8 Auditointi:**
     ```powershell
     agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier7-describe-architecture @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]"
     agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]"
     ```

---

### Askel 3.2: Kohdennettu Aluekohtainen Karkaisu (Targeted Hardening: Workers, SDUI & Utilities) (Vaihe 2c)
* **Tavoite ja Arkkitehtoninen Rooli:**
  Ennen siirtymistä laajaan B2B SaaS IAM -vaiheeseen (Askel 4) karkaistaan Quorumin kolme keskeisintä asynkronista ja esityskerroksen apualuetta. Nämä muodostavat järjestelmän "selkärangan" (asynkroniset Arq-taustatyöntekijät) ja "hermoston" (SDUI-muuntimet ja matemaattiset aputyökalut). Karkaisu suoritetaan omina itsenäisinä ja hallittuina paketteinaan (`auto_hardening_runner.py` käyttäen mallia `gemini-4-argon-medium` ja alikomentoa `/tier2-hardening-backend`).

#### Paketti 1: Asynkroniset Taustatyöntekijät (`backend_v2/workers/`)
* **Laajuus & Kesto:** 6 tiedostoa, kestoarvio **~40 min**.
* **Tavoite:** Taustajonojen täysi vikaturvallisuus, nolla "jumiin jäänyttä" työnkulkua, deterministinen DLQ-luokittelu, `exc_info=True` ja oikeat `ErrorCodes`.
* **Kohdetiedostot:**
  1. `@[backend_v2/workers/execution_worker.py]`
  2. `@[backend_v2/workers/report_worker.py]`
  3. `@[backend_v2/workers/synthesis_reducers.py]`
  4. `@[backend_v2/workers/synthesis_tasks.py]`
  5. `@[backend_v2/workers/synthesis_worker.py]`
  6. `@[backend_v2/workers/variance_synthesis.py]`
* **Suorituskomento:**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Workers_Hardening.md]" --gate backend --model gemini-4-argon-medium --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
  ```

#### Paketti 2: SDUI-adapterit & Vientimuuntimet (`backend_v2/services/sdui/adapters/`)
* **Laajuus & Kesto:** 15 tiedostoa, kestoarvio **~1,5 h**.
* **Tavoite:** Nolla Flutter- tai PDF-kaatumista puuttuvien tai ääriarvoisten metriikoiden takia, 100 % Dumb Painter -yhteensopivuus, ISTQB-rajatestit ääritilanteille.
* **Kohdetiedostot:**
  1. `@[backend_v2/services/sdui/sdui_mapper_service.py]`
  2. `@[backend_v2/services/sdui/adapters/base_adapter.py]`
  3. `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`
  4. `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`
  5. `@[backend_v2/services/sdui/adapters/global_score_adapter.py]`
  6. `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]`
  7. `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`
  8. `@[backend_v2/services/sdui/adapters/mcp_audit_adapter.py]`
  9. `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`
  10. `@[backend_v2/services/sdui/adapters/penalties_adapter.py]`
  11. `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
  12. `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]`
  13. `@[backend_v2/services/sdui/adapters/variance_adapter.py]`
  14. `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]`
  15. `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`
* **Suorituskomento:**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_SDUI_Hardening.md]" --gate backend --model gemini-4-argon-medium --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
  ```

#### Paketti 3: Utilities & Apupalvelut (`backend_v2/utils/` + `services/`)
* **Laajuus & Kesto:** 15 tiedostoa, kestoarvio **~1,5 – 2 h**.
* **Tavoite:** Tiukat tyypit, nolla `typing.Any`, hiljaisten virhenielujen poisto, `exc_info=True`, suorat Pydantic V2 DTO -validointisäännöt.
* **Kohdetiedostot:**
  1. `@[backend_v2/utils/math_utils.py]`
  2. `@[backend_v2/utils/alias_engine.py]`
  3. `@[backend_v2/utils/normalization.py]`
  4. `@[backend_v2/utils/paths.py]`
  5. `@[backend_v2/utils/pydantic_utils.py]`
  6. `@[backend_v2/utils/ranked_round_robin.py]`
  7. `@[backend_v2/utils/redis_patcher.py]`
  8. `@[backend_v2/utils/static_charts.py]`
  9. `@[backend_v2/utils/finops_trace_analyzer.py]`
  10. `@[backend_v2/services/translation_service.py]`
  11. `@[backend_v2/services/caching_service.py]`
  12. `@[backend_v2/services/llm_task_executor.py]`
  13. `@[backend_v2/services/state_sanitizer_service.py]`
  14. `@[backend_v2/services/mcp/presentation_sanitizer.py]`
  15. `@[backend_v2/services/orchestrator/localization_compiler.py]`
* **Suorituskomento:**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Utility_Hardening.md]" --gate backend --model gemini-4-argon-medium --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
  ```

#### Laatuvarmennus:
Jokaisen karkaisupaketin jälkeen ajetaan koko backendin kattava laatuportti:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
```

---

### Askel 4: Suorita B2B SaaS IAM & Hardening (Vaihe 3)
* **Tavoite:** Ota käyttöön RFC 8693 Token Exchange, 0,1 ms in-RAM JWT -validointi, Redis Fail-Closed Kill-Switch, moniroolivaltuutus ja luotava (create) [NEW] `SecretService`.
* **Virallinen Eepos:** `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`
* **1. Generoi vaihekohtaiset suunnitelmat ja tracker:**
  ```powershell
  agy -i "/tier1-planner @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]"
  ```
* **2. Suorita vaiheet multi-phase runnerilla:**
  ```powershell
  uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_160_tracker.md
  ```

---

### Askel 5: Suorita Firebase Storage Direct-to-Cloud Signed URLs (Vaihe 4)
* **Tavoite:** Toteuta frontendin suoralataus Firebase Storageen (15 min PUT Signed URLs), tiedostometadatan rekisteröinti ja orposiivous-taustatyö.
* **Toteutussuunnitelma:** `[NEW] @[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]`
* **Suoritus:**
  ```powershell
  agy -i "/tier2-execute --full-auto [NEW] @[docs/implementationplans/IMPLEMENTATION_PLAN_Storage_Signed_URLs.md]"
  ```

---

### Askel 5.1: Frontend & Studio UI Hardening (Flutter Web & Desktop) (Vaihe 4b)
* **Tavoite ja Arkkitehtoninen Rooli:**
  Ennen pilvituotannon käyttöönottoa karkaistaan Flutter Web- ja Desktop -käyttöliittymä (`client_app_v2`), Riverpod-tilanhallinta, SDUI Dumb Painter -renderöinti ja virherajat (`AppErrorBoundary`). Tämä takaa, ettei mikään verkko- tai deserialisointivirhe kaada sovellusta punaiseen virheruutuun (Red Screen of Death), vaan käyttöliittymä toipuu siististi.
* **Laajuus & Kesto:** ~12–15 tiedostoa (`client_app_v2/lib/features/`, `client_app_v2/lib/shared/`), kestoarvio **~1,5 h**.
* **Kohdetiedostot:**
  1. `@[client_app_v2/lib/features/studio/presentation/views/studio_dashboard_view.dart]`
  2. `@[client_app_v2/lib/features/studio/presentation/widgets/workflow_step_card.dart]`
  3. `@[client_app_v2/lib/features/studio/presentation/widgets/workflow_steps_tab.dart]`
  4. `@[client_app_v2/lib/features/reports/presentation/views/report_view.dart]`
  5. `@[client_app_v2/lib/features/reports/presentation/widgets/sdui_block_renderer.dart]`
  6. `@[client_app_v2/lib/shared/widgets/app_error_boundary.dart]`
  7. `@[client_app_v2/lib/core/network/api_client.dart]`
  8. `@[client_app_v2/lib/core/auth/auth_controller.dart]`
* **Suorituskomento:**
  ```powershell
  uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Hardening.md]" --gate frontend --model gemini-4-argon-medium --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"
  ```
* **Laatuvarmennus:**
  ```powershell
  uv run python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

### Askel 6: Suorita GCP-tuotantopystytys & `quorum.ai` Domain (Vaihe 5)
* **Tavoite:** Provisioi GCP europe-north1 -resurssit (Cloud SQL PG19, Cloud Run API & Worker, Memorystore Redis, Secret Manager, Cloud Armor, Cloud Load Balancer) ja kytke Google-Managed SAN SSL `api.quorum.ai`-, `app.quorum.ai`- ja `quorum.fi`-osoitteille.
* **Virallinen Eepos:** `@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`
* **Toteutussuunnitelma:** `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`
* **Seurantadokumentti (Tracker):** `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`
* **1. Luo seurantatiedosto (mikäli ei vielä luotu):**
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]"
  ```
* **2. Käynnistä automaattinen suoritus:**
  ```powershell
  uv run python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_GCP_Production_Deployment.md --model gemini-4-argon-high
  ```
  tai suoraan itsenäisessä CLI-sessiossa:
  ```powershell
  agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md] --full-auto. PERMISSION GRANTED for continuous full-auto execution across all steps. Proceed autonomously through all steps without intermediate confirmations."
  ```

---

### Askel 6.1: Cloud Security & FinOps Infrastructure Hardening (GCP europe-north1) (Vaihe 5b)
* **Tavoite ja Arkkitehtoninen Rooli:**
  Ennen julkisen verkkoliikenteen avaamista `quorum.ai`-osoitteelle karkaistaan GCP europe-north1 -tuotantoympäristön verkkoturvallisuus, WAF-säännöt, pienimmät riittävät käyttöoikeudet (Least Privilege IAM), VPC-eristys ja kustannuskatot (FinOps Circuit Breakers).
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
* **Todennuskomento:**
  ```powershell
  gcloud compute security-policies describe quorum-armor-policy --project=quorum-prod
  gcloud sql instances describe quorum-pg19 --format="value(ipAddresses)"
  uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  ```