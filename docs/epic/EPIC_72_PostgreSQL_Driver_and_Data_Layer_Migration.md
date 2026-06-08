# Epic 72: PostgreSQL Driver ja Datakerroksen Migraatio

> [!IMPORTANT]
> **DATAKERRROKSEN SUVERENITEETTI**: Tämä Epic korvaa Firestore-pohjaisen tuotantoarkkitehtuurin (Epic 22) PostgreSQL + JSONB -ratkaisulla. Firestore-driver säilyy historiallisena referenssinä mutta ei ole enää tuotantopolku. TinyDB pysyy lokaali-/testitarkoituksessa.

---

## 1. Yhteenveto ja Tavoite (Objective)

Tämän Epicin tavoitteena on toteuttaa `PostgreSQLDriver` — uusi `IRepository`-abstraktiota noudattava tietokanta-ajuri, joka korvaa Firestoren tuotantokäytössä ja ratkaisee seuraavat nykyiset rajoitteet:

### Tunnistetut Nykytilan Haasteet

| Ongelma | TinyDB | Firestore | PostgreSQL (ratkaisu) |
|---|---|---|---|
| **Dokumenttikoko** | Rajoittamaton (mutta koko DB muistissa) | ⛔ 1 MB/dokumentti | ✅ Käytännössä rajaton |
| **Rinnakkaiskirjoitus** | ⛔ Tiedostolukko (globaali) | ⚠️ Optimistic locking | ✅ MVCC — rinnakkaiset rivitason kirjoitukset |
| **Trace append** | ⛔ Koko blob uusiksi per checkpoint | ⛔ Koko dokumentti uusiksi | ✅ INSERT rivejä — O(1) |
| **Indeksit ja kyselyt** | ⛔ Full scan | ⚠️ Composite-rajoitukset | ✅ B-tree + GIN (JSONB) |
| **Transaktiot** | ⛔ Ei | ⚠️ Rajoitetut | ✅ Täydet ACID-transaktiot |
| **Async Python** | ✅ (sync, mutta nopea) | ⚠️ SDK ei natiivisti async | ✅ `asyncpg` — nopein |
| **Kustannus** | Ilmainen | ⚠️ Per read/write ops | ✅ Ennustettava (CPU/RAM) |

### Arkkitehtoninen Ratkaisu

```
backend_v2/database/
├── drivers/
│   ├── tinydb_driver.py          (nykyinen — pysyy dev/testissä)
│   ├── firestore_driver.py       (nykyinen — arkistoitu, ei tuotantopolku)
│   └── postgresql_driver.py      ← UUSI (asyncpg + JSONB)
├── migrations/
│   ├── alembic.ini               ← UUSI (Alembic-konfiguraatio)
│   ├── env.py                    ← UUSI (migraatiomoottori)
│   └── versions/
│       └── 001_initial_schema.py ← UUSI (alkuskeema)
├── factory.py                    (päivitetään: QUORUM_DB_DRIVER=postgresql)
└── interfaces.py                 (EI MUUTU — abstraktio pysyy)
```

---

## 2. Arkkitehtuuristen Sääntöjen Huomiointi (Compliance)

### 2.1. Ydinjärjestelmä (00-antigravity-core.md)

* **the_zero_compromise_pledge**: PostgreSQL-driver toteuttaa saman `IRepository`-rajapinnan — ei fallback-logiikkaa, ei duck-typingiä.
* **universal_fail_fast**: Kaikki SQL-virheet kääritään `AppException`-poikkeuksiksi RFC 7807 -standardin mukaisesti.
* **atomic_checkpoint_mandate**: Jokainen vaihe commitoidaan erikseen Gitiin.

### 2.2. Backend-arkkitehtuuri (01-python-backend.md)

* **strict_pydantic_v2_rust**: Kaikki data validoidaan `.model_validate()` rajalla — PostgreSQL palauttaa raakadictejä, jotka hydratoidaan Pydantic-malleiksi.
* **no_naked_dicts_in_state**: `model_validate(row).model_dump(mode='json')` -ketju kaikissa rajapinnoissa.
* **no_inline_imports**: `asyncpg` importoidaan globaalisti driver-tiedostossa (ei ML-kirjasto).

---

## 3. Tietokantaskeema (Database Schema)

### 3.1. Relaatiotaulut (rakenne) + JSONB (joustavuus)

```sql
-- Core execution tracking
CREATE TABLE executions (
    id              TEXT PRIMARY KEY,
    workflow_id     TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    error           TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}',
    raw_inputs      JSONB NOT NULL DEFAULT '{}',
    frozen_context  JSONB,
    step_states     JSONB NOT NULL DEFAULT '{}',
    profile_syntheses JSONB,
    output_profile_id TEXT,
    pdf_report_path TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    duration_ms     INTEGER,
    models_used     JSONB DEFAULT '{}'
);

-- Append-only event sourcing (EI koskaan UPDATE)
CREATE TABLE trace_events (
    id          BIGSERIAL PRIMARY KEY,
    exec_id     TEXT NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    seq         INTEGER NOT NULL,
    step_name   TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    content     JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(exec_id, seq)
);

-- Workflow configurations
CREATE TABLE workflows (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    slug        TEXT NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'draft',
    version     INTEGER NOT NULL DEFAULT 1,
    config      JSONB NOT NULL,  -- steps, expected_inputs, scoring etc.
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ
);

-- Prompt blocks (evaluation criteria)
CREATE TABLE prompt_blocks (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    config      JSONB NOT NULL,  -- scales, atoms, rules etc.
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ
);

-- Steps (task blueprints)
CREATE TABLE steps (
    id          TEXT PRIMARY KEY,
    slug        TEXT NOT NULL,
    type        TEXT NOT NULL,
    config      JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Output profiles
CREATE TABLE output_profiles (
    id                TEXT PRIMARY KEY,
    workflow_id       TEXT NOT NULL,
    name              TEXT NOT NULL,
    config            JSONB NOT NULL,
    strictness_level  INTEGER,
    scoring_strategy  TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Organizations (IAM)
CREATE TABLE organizations (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    config      JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Users (IAM integration)
CREATE TABLE users (
    id              TEXT PRIMARY KEY, -- Firebase UID
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    role            TEXT NOT NULL,
    deleted_at      TIMESTAMPTZ, -- Soft delete for GDPR
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(organization_id, id)
);

-- Invitations (IAM integration)
CREATE TABLE invitations (
    id              TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    email           TEXT NOT NULL,
    role            TEXT NOT NULL,
    invite_token    TEXT NOT NULL UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audit log (append-only, tamper-proof)
CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    exec_id     TEXT,
    org_id      TEXT,
    action      TEXT NOT NULL,
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Performance indexes
CREATE INDEX idx_executions_workflow ON executions(workflow_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_trace_events_exec ON trace_events(exec_id, seq);
CREATE INDEX idx_workflows_slug ON workflows(slug);
CREATE INDEX idx_audit_log_exec ON audit_log(exec_id);
CREATE INDEX idx_executions_metadata ON executions USING GIN(metadata);
CREATE INDEX idx_users_org ON users(organization_id);
```

### 3.2. Trace Events: Append-Only -arkkitehtuuri

Kriittinen ero nykytilanteeseen:

```
Nyt (TinyDB/Firestore):
  checkpoint → koko execution_trace-blob kirjoitetaan uusiksi
  7 rinnakkaista agenttia → 7 × 500 KB = 3.5 MB levykirjoituksia

PostgreSQL:
  checkpoint → INSERT INTO trace_events (exec_id, seq, content)
  7 rinnakkaista agenttia → 7 × INSERT (1-5 KB) = ~35 KB
  → 100× vähemmän I/O, rinnakkain, ilman lukkoja
```

Trace-tapahtumat rekonstruoidaan lukuhetkellä:
```python
async def get_execution(self, exec_id: str) -> dict[str, Any] | None:
    row = await self.pool.fetchrow("SELECT * FROM executions WHERE id = $1", exec_id)
    if not row:
        return None
    result = dict(row)
    # Reconstruct trace from append-only events
    trace_rows = await self.pool.fetch(
        "SELECT * FROM trace_events WHERE exec_id = $1 ORDER BY seq", exec_id
    )
    result["execution_trace"] = [dict(r) for r in trace_rows]
    return result
```

### 3.3. Row-Level Security (RLS) ja Tenant-eristys (IAM-tuki)

Tietokantakerros tulee tukemaan **B2B SaaS IAM -arkkitehtuurin (Epic IAM-003)** vaatimaa loogista eristystä Row-Level Securityn (RLS) avulla.
* Kun `PostgreSQLDriver` ottaa yhteyden altaasta (connection pool) ja API-reitin kontekstissa on organisaatio, yhteys injektoi lokaalin session muuttujan: `SET LOCAL quorum.current_org = '<org_id>'`.
* Tämä estää inhimilliset virheet (ORM Data Leakage) pysäyttämällä ristiinluvut suoraan kanta-tasolla.

---

## 4. Toteutussuunnitelma (Implementation Phases)

### Phase 1: PostgreSQL-driver (2 sessiota)

| Tehtävä | Tiedostot | Huomiot |
|---|---|---|
| 1.1 Alembic-setup | `migrations/alembic.ini`, `env.py` | Alembic versionoi skeeman |
| 1.2 Initial schema | `migrations/versions/001_initial_schema.py` | Yllä oleva SQL |
| 1.3 `PostgreSQLDriver` | `drivers/postgresql_driver.py` | `asyncpg` + connection pool |
| 1.4 `factory.py` päivitys | `database/factory.py` | `QUORUM_DB_DRIVER=postgresql` |
| 1.5 `settings.py` päivitys | `settings.py` | `database_url: str` kenttä |

### Phase 2: Contract-testit (1 sessio)

| Tehtävä | Kuvaus |
|---|---|
| 2.1 `testcontainers` setup | `pytest-testcontainers` + `PostgresContainer` |
| 2.2 Parametrisoitu fixture | Sama `IRepository`-suite ajetaan TinyDB + PG vasten |
| 2.3 Rinnakkaisuustesti | 7 rinnakkaista INSERT → ei lukko-ongelmia |
| 2.4 Trace append -testi | Append-only INSERT vs blob-rewrite pariteetti |

### Phase 3: Seed-migraatio (1 sessio)

| Tehtävä | Kuvaus |
|---|---|
| 3.1 `run_seed.py` PG-tuki | Seed-skripti kirjoittaa PostgreSQL:ään |
| 3.2 `docker-compose.yml` | Lokaali PG 16 + Redis kehitysympäristöön |
| 3.3 Full-run validointi | Kokonainen workflow-suoritus PG-driverilla |

---

## 5. Docker-compose (Lokaali kehitysympäristö)

```yaml
# docker-compose.dev.yml
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: quorum_dev
      POSTGRES_USER: quorum
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

---

## 6. Verifiointisuunnitelma (Verification)

| Tarkistus | Menetelmä | Hyväksymiskriteeri |
|---|---|---|
| Skeeman validointi | `alembic upgrade head` | Ei virheitä |
| Contract-testit | `pytest --pg` (TinyDB + PG pariteetti) | 100% vihreä |
| Rinnakkaisuus | 7 samanaikaista INSERT-operaatiota | Ei deadlockeja |
| Full workflow | Lokaali suoritus PG-driverilla | Sama tulos kuin TinyDB |
| Quality Gate | `backend_audit_loop.py postgresql_driver.py --test` | Ruff + MyPy + 30% coverage |

---

## 7. Riippuvuudet ja Rajaukset

* **Ei riko mitään**: `IRepository`-rajapinta pysyy — logiikkakerros ei muutu
* **TinyDB pysyy**: Lokaali dev ja yksikkötestit käyttävät edelleen TinyDB:tä
* **Firestore arkistoidaan**: Driver säilyy mutta ei ole aktiivisessa käytössä
* **Ei hosting-muutoksia**: Tämä Epic käsittelee VAIN datakerrosta
* **Riippuvuudet**: `asyncpg`, `alembic`, `testcontainers[postgres]`
