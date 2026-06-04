# Epic 74: Production Deployment — Google Cloud Platform

> [!IMPORTANT]
> **TUOTANTO-INFRASTRUKTUURI**: Tämä Epic toteuttaa Cognitive Quorumin tuotantoympäristön Google Cloud Platformilla. Se korvaa Epic 22:n Firestore-pohjaisen tuotantosuunnitelman PostgreSQL-pohjaisella arkkitehtuurilla (Epic 72) ja hyödyntää CI/CD-putkea (Epic 73).

> [!CAUTION]
> **RIIPPUVUUDET**: Tämä Epic vaatii Epic 72 (PostgreSQL Driver) ja Epic 73 (CI/CD Pipeline) olevan valmiit ja verifioituja ennen toteutuksen aloittamista.

---

## 1. Yhteenveto ja Tavoite (Objective)

Tämän Epicin tavoitteena on provisioida ja konfiguroida tuotantoinfrastruktuuri Google Cloud Platformille siten, että:

1. **FastAPI-backend** ja **Arq-worker** pyörivät Cloud Runissa
2. **PostgreSQL** toimii Cloud SQL -palvelussa (managed, PITR-backup)
3. **Redis** toimii Memorystoressa (managed, Private IP)
4. **Firebase Auth** pysyy identiteettipalveluna (ei muutoksia)
5. **Vertex AI** pysyy LLM-rajapintana (ei muutoksia)
6. **Tietokannan seeding** suoritetaan kerran tuotantokantaan

### Tuotantoarkkitehtuuri

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                        │
│                    (europe-north1 / Finland)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Cloud Run: API      │    │  Cloud Run: Worker   │          │
│  │  (quorum-api)        │    │  (quorum-worker)     │          │
│  │  min: 0, max: 10     │    │  min: 1, max: 5      │          │
│  │  2 vCPU / 2 GB       │    │  2 vCPU / 4 GB       │          │
│  │  Autoscale: requests │    │  Autoscale: CPU      │          │
│  └──────────┬───────────┘    └──────────┬───────────┘          │
│             │ SQL Proxy (Private IP)     │                      │
│             ▼                            ▼                      │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Cloud SQL           │    │  Memorystore         │          │
│  │  (PostgreSQL 16)     │    │  (Redis 7)           │          │
│  │  db-custom-2-8192    │    │  Standard 2 GB       │          │
│  │  Private IP          │    │  Private IP          │          │
│  │  PITR: 7 days        │    │  HA: cross-zone      │          │
│  └──────────────────────┘    └──────────────────────┘          │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Firebase Auth       │    │  Vertex AI           │          │
│  │  (identiteetti)      │    │  (LLM)               │          │
│  │  JWT verify          │    │  gemini-2.5-flash/pro │          │
│  │  Ilmainen ≤50k MAU   │    │  europe-north1       │          │
│  └──────────────────────┘    └──────────────────────┘          │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Cloud Storage       │    │  Secret Manager      │          │
│  │  (PDF, inputs)       │    │  (API keys, DB creds)│          │
│  │  europe-north1       │    │  Automaattinen       │          │
│  └──────────────────────┘    └──────────────────────┘          │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Cloud Load Balancer + Cloud Armor               │          │
│  │  HTTPS termination + DDoS protection             │          │
│  │  Custom domain: api.quorum.fi (esimerkki)        │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Arkkitehtuuristen Sääntöjen Huomiointi (Compliance)

### 2.1. Separation of State (Epic 22 periaate — päivitetty)

* **Tuotannossa** Cloud Run -kontit ovat **tilattomia** (stateless). Kaikki data elää Cloud SQL:ssä.
* **Lokaali `db_v2.json`** ei ole käytössä tuotannossa.
* **`seed_data.json`** on Build-Time Artifact — käytetään vain tietokannan alustuksessa.

### 2.2. Security (01-python-backend.md)

* **security_logging_ban**: API-avaimet Secret Managerissa — ei ympäristömuuttujissa.
* **Firebase Auth**: JWT-validointi pysyy ennallaan — vain backend-URL vaihtuu.
* **VPC**: Cloud SQL ja Memorystore eivät ole julkisessa verkossa.

---

## 3. Kustannusarvio (FinOps)

### 3.1. Staging-ympäristö

| Palvelu | Konfiguraatio | Arvioitu kustannus/kk |
|---|---|---|
| Cloud Run (API) | min 0, max 2, 1 vCPU / 512 MB | €3–5 |
| Cloud Run (Worker) | min 0, max 1, 1 vCPU / 1 GB | €3–5 |
| Cloud SQL | db-f1-micro (0.6 GB RAM) | €8 |
| Memorystore | Basic 1 GB | €5 |
| Cloud Storage | <1 GB | €0.02 |
| Firebase Auth | <100 MAU | €0 |
| Secret Manager | <10 secrets | €0 |
| **Yhteensä** | | **~€20–25/kk** |

### 3.2. Tuotantoympäristö

| Palvelu | Konfiguraatio | Arvioitu kustannus/kk |
|---|---|---|
| Cloud Run (API) | min 1, max 10, 2 vCPU / 2 GB | €15–40 |
| Cloud Run (Worker) | min 1, max 5, 2 vCPU / 4 GB | €20–50 |
| Cloud SQL | db-custom-2-8192, HA, PITR | €50–80 |
| Memorystore | Standard 2 GB, HA | €15–25 |
| Cloud Storage | <10 GB | €0.20 |
| Load Balancer + Armor | Standard tier | €18 |
| Firebase Auth | <1000 MAU | €0 |
| Vertex AI | Käytön mukaan | €20–200+ |
| **Yhteensä** | | **~€140–420/kk** |

> [!TIP]
> **FinOps-säästö**: Context Caching (Epic 67) vähentää Vertex AI -kustannuksia 50–90%, joten todellinen LLM-kustannus on huomattavasti pienempi kuin raaka per-token -hinnoittelu.

---

## 4. Toteutussuunnitelma (Implementation Phases)

### Phase 1: GCP-infrastruktuurin provisiointi (1 sessio)

| Tehtävä | Komento / Työkalu | Huomiot |
|---|---|---|
| 4.1.1 Projektin konfigurointi | `gcloud config set project cognitive-quorum` | Olemassa oleva projekti |
| 4.1.2 VPC-verkon luonti | `gcloud compute networks create quorum-vpc` | Private IP -verkko |
| 4.1.3 Cloud SQL provisiointi | `gcloud sql instances create` | PG 16, europe-north1, Private IP |
| 4.1.4 Alembic-migraatio | `alembic upgrade head` (Cloud SQL Proxylla) | Skeema tuotantokantaan |
| 4.1.5 Memorystore provisiointi | `gcloud redis instances create` | Redis 7, Private IP |
| 4.1.6 Secret Manager setup | `gcloud secrets create` | DATABASE_URL, API keys |
| 4.1.7 Cloud Storage bucket | `gcloud storage buckets create` | PDF-raportit, inputit |

#### Cloud SQL -provisiointi (esimerkki)

```bash
# Staging
gcloud sql instances create quorum-staging \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=europe-north1 \
  --network=quorum-vpc \
  --no-assign-ip \
  --enable-point-in-time-recovery \
  --backup-start-time=02:00

# Tuotanto
gcloud sql instances create quorum-production \
  --database-version=POSTGRES_16 \
  --tier=db-custom-2-8192 \
  --region=europe-north1 \
  --availability-type=REGIONAL \
  --network=quorum-vpc \
  --no-assign-ip \
  --enable-point-in-time-recovery \
  --backup-start-time=02:00 \
  --retained-backups-count=14
```

### Phase 2: Cloud Run Deploy (1 sessio)

| Tehtävä | Kuvaus | Huomiot |
|---|---|---|
| 4.2.1 Service Account | `gcloud iam service-accounts create quorum-api` | Minimal privileges |
| 4.2.2 IAM-oikeudet | Cloud SQL Client, Secret Accessor, Storage Admin | Per service |
| 4.2.3 API Deploy | `gcloud run deploy quorum-api` | Epic 73 Dockerfile |
| 4.2.4 Worker Deploy | `gcloud run deploy quorum-worker` | Epic 73 Dockerfile.worker |
| 4.2.5 Environment vars | Secret Manager → Cloud Run env bindings | DATABASE_URL, REDIS_HOST |
| 4.2.6 Custom domain | `gcloud beta run domain-mappings create` | DNS A/CNAME |

#### Cloud Run -konfiguraatio (esimerkki)

```bash
# API
gcloud run deploy quorum-api \
  --image gcr.io/cognitive-quorum/quorum-api:latest \
  --region europe-north1 \
  --platform managed \
  --vpc-connector quorum-connector \
  --set-env-vars "QUORUM_DB_DRIVER=postgresql,ENVIRONMENT=production" \
  --set-secrets "DATABASE_URL=quorum-db-url:latest" \
  --min-instances 1 \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --allow-unauthenticated

# Worker
gcloud run deploy quorum-worker \
  --image gcr.io/cognitive-quorum/quorum-worker:latest \
  --region europe-north1 \
  --platform managed \
  --vpc-connector quorum-connector \
  --set-env-vars "QUORUM_DB_DRIVER=postgresql,ENVIRONMENT=production" \
  --set-secrets "DATABASE_URL=quorum-db-url:latest" \
  --min-instances 1 \
  --max-instances 5 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 900 \
  --no-allow-unauthenticated
```

### Phase 3: Seeding ja Validointi (1 sessio)

| Tehtävä | Kuvaus | Huomiot |
|---|---|---|
| 4.3.1 Seed-skripti tuotantoon | `run_seed.py` Cloud SQL Proxylla | Kaikki seed_data → PostgreSQL |
| 4.3.2 Smoke test | `curl https://api.quorum.fi/health` | 200 OK |
| 4.3.3 E2E-suoritus | Yksi kokonainen workflow staging-ympäristössä | Kaikki askeleet vihreät |
| 4.3.4 PDF-generointi | Varmista PDF-tiedoston synty Cloud Storageen | Lataa ja tarkista |
| 4.3.5 Monitoring setup | Cloud Monitoring + alerting | Error rate, latency, CPU |

---

## 5. Ympäristömuuttujat (Environment Variables)

### 5.1. Tuotanto (Secret Managerissa)

| Muuttuja | Arvo | Lähde |
|---|---|---|
| `QUORUM_DB_DRIVER` | `postgresql` | Env var |
| `DATABASE_URL` | `postgresql://quorum:xxx@/quorum?host=/cloudsql/...` | Secret Manager |
| `REDIS_HOST` | `10.x.x.x` (Private IP) | Env var |
| `REDIS_PORT` | `6379` | Env var |
| `FIREBASE_PROJECT_ID` | `cognitive-quorum` | Env var |
| `GCP_PROJECT` | `cognitive-quorum` | Env var |
| `GCP_REGION` | `europe-north1` | Env var |
| `VERTEX_AI_LOCATION` | `europe-north1` | Env var |
| `STORAGE_BACKEND` | `gcs` | Env var |
| `GCS_BUCKET` | `quorum-production-files` | Env var |
| `ENVIRONMENT` | `production` | Env var |

### 5.2. Staging

Sama rakenne, mutta:
- `DATABASE_URL` → staging Cloud SQL instance
- `GCS_BUCKET` → `quorum-staging-files`
- `ENVIRONMENT` → `staging`

---

## 6. Turvallisuus (Security)

### 6.1. Verkkoarkkitehtuuri

```
Internet → Cloud Load Balancer (HTTPS)
           → Cloud Armor (DDoS, rate limiting)
           → Cloud Run API (VPC connector)
              → Cloud SQL (Private IP, ei julkinen)
              → Memorystore (Private IP, ei julkinen)
```

### 6.2. IAM-periaatteet

| Service Account | Oikeudet | Palvelu |
|---|---|---|
| `quorum-api@` | Cloud SQL Client, Secret Accessor, Storage Object Admin | Cloud Run API |
| `quorum-worker@` | Cloud SQL Client, Secret Accessor, Storage Object Admin, Vertex AI User | Cloud Run Worker |
| `quorum-deploy@` | Cloud Run Admin, Artifact Registry Writer | GitHub Actions CI/CD |

### 6.3. Tietoturvallisuusvaatimukset

* **Encryption at rest**: Cloud SQL automaattinen salaus (AES-256)
* **Encryption in transit**: TLS 1.3 kaikkialla
* **Backup**: PITR 7–14 päivää, automaattinen
* **Audit log**: Cloud Audit Logs kaikista admin-operaatioista
* **No PII in logs**: `security_logging_ban` pysyy voimassa

---

## 7. Monitoring ja Alerting

### 7.1. Cloud Monitoring -dashboardit

| Metriikka | Kynnys | Toimenpide |
|---|---|---|
| Error rate (5xx) | > 1% / 5 min | Email + Slack alert |
| P99 latency | > 5s | Warning alert |
| Cloud SQL CPU | > 80% / 10 min | Scale up alert |
| Cloud SQL storage | > 80% | Disk expand alert |
| Worker queue depth | > 50 jobs | Scale up alert |
| Memory usage | > 90% | OOM risk alert |

### 7.2. Health Check -endpoint

```python
# backend_v2/routers/health.py
@router.get("/health")
async def health_check():
    """Production health check for Cloud Run and Load Balancer."""
    return {"status": "ok", "version": "2.9", "db_driver": settings.db_driver}
```

---

## 8. Rollback-suunnitelma

| Tilanne | Toimenpide | Aikataulu |
|---|---|---|
| **API-regressio** | Cloud Run traffic split → edellinen revisio 100% | <1 min |
| **DB-migraatio epäonnistuu** | `alembic downgrade -1` | <5 min |
| **Kokonaisvika** | Palaa TinyDB-lokaaliin, pysäytä Cloud Run | <10 min |

---

## 9. Verifiointisuunnitelma (Verification)

| Tarkistus | Menetelmä | Hyväksymiskriteeri |
|---|---|---|
| Infra provisiointi | `gcloud sql instances describe` | PG 16 running, Private IP |
| DB-migraatio | `alembic upgrade head` | Kaikki taulut luotu |
| Seeding | `run_seed.py` + SQL count | Kaikki seed-data kannassa |
| API deploy | `curl /health` | 200 OK, version 2.9 |
| Worker deploy | Enqueue test job | Job completes successfully |
| E2E workflow | Kokonainen suoritus staging-ympäristössä | Kaikki askeleet + PDF vihreät |
| Firebase Auth | JWT-validointi staging API:sta | 401 ilman tokenia, 200 tokenilla |
| Monitoring | Trigger test alert | Alert saapuu Slackiin/emailiin |

---

## 10. Riippuvuudet ja Rajaukset

* **Vaatii Epic 72**: PostgreSQL-driver oltava valmis ja testattu
* **Vaatii Epic 73**: Docker build ja CI/CD-putki oltava toimiva
* **Ei muuta koodia**: Tämä Epic on 100% infraa — ei backend-koodimuutoksia
* **Firebase Auth pysyy**: JWT-validointi ei muutu — vain API-URL vaihtuu
* **Vertex AI pysyy**: LLM-kutsut eivät muutu — sama region (europe-north1)
* **GCP-projekti**: `cognitive-quorum` (olemassa oleva)
* **Budjetti**: Staging ~€25/kk, Production ~€140–420/kk (ilman LLM)
