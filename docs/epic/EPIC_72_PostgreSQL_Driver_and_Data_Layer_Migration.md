<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
</required_context_rules>

# Epic 72: PostgreSQL Driver ja Datakerroksen Migraatio

> [!IMPORTANT]
> **DATAKERROKSEN SUVERENITEETTI JA TINYDB:N TÄYDELLINEN POISTO**: Tämä Epic korvaa tiedostopohjaisen TinyDB-kehityskannan (`db_v2.json`) ja arkistoidun Firestore-ajurin modernilla, suorituskykyisellä PostgreSQL + JSONB -arkkitehtuurilla (`asyncpg`). TinyDB poistetaan kokonaisuudessaan koodikannasta ja riippuvuuksista ilman pysyviä fallback-ketjuja. Kognitiivisen atomiverkon (`atoms`, `atom_links`) graafikyselyt ankkuroidaan puhtaasti jälkikäteiseen XAI-auditointiin ja raportointiin rikkomatta suorituksen aikaisen Tripartite-arkkitehtuurin in-memory-reduktioita (`MatrixReducer`).

---

## 1. Yhteenveto ja Tavoite (Objective)

Tämän Epicin tavoitteena on toteuttaa `PostgreSQLDriver` — `StorageDriver`- ja `IUnifiedWorkflowRepository`-sopimuksia noudattava asynkroninen tietokanta-ajuri, joka siirtää Quorumin täyteen ACID-transaktiotukeen, MVCC-rinnakkaisuuteen ja skaalautuvaan data-arkkitehtuuriin:

### Tunnistetut Nykytilan Haasteet

| Ominaisuus / Haaste | TinyDB (Decommissionoitava) | Firestore (Arkistoitu) | PostgreSQL 16+ (Uusi Standardi) |
|---|---|---|---|
| **Dokumenttikoko** | Rajoittamaton (mutta koko taulu RAM-muistissa) | ⛔ 1 MB / dokumentti | ✅ Käytännössä rajaton (JSONB + TOAST) |
| **Rinnakkaiskirjoitus** | ⛔ Tiedostolukko (`msvcrt`/`fcntl` OS-lukitus) | ⚠️ Optimistic locking | ✅ MVCC — rinnakkaiset rivitason transaktiot |
| **Trace append** | ⛔ Koko `execution_trace` uusiksi per tapahtuma | ⛔ Koko dokumentti uusiksi | ✅ Append-only `INSERT INTO trace_events` — O(1) |
| **Indeksit ja haut** | ⛔ Full scan muistissa | ⚠️ Rajoitetut yhdistelmäindeksit | ✅ B-tree + GIN (JSONBPath-haut) |
| **Transaktiot** | ⛔ Ei transaktioita | ⚠️ Rajoitetut transaktiot | ✅ Täydet ACID-transaktiot ja SAVEPOINTit |
| **Async Python** | ⛔ Synkroninen levytiedosto | ⚠️ SDK ei natiivisti async | ✅ `asyncpg` — korkean suorituskyvyn yhteyspooli |
| **Graafirakenteet** | ⛔ Manuaalinen Python-silmukointi | ⛔ Ei graafitukea | ✅ Relaatiograafi (`atoms`, `atom_links`) + CTE / SQL-PGQ valmius |
| **Kustannus ja hallinta** | Paikallinen kehitysteline | ⚠️ Kallis pilvikustannus per I/O | ✅ Ennustettava, kontitettavissa (`docker-compose`) |

### Arkkitehtoninen Hakemistorakenne

```
backend_v2/database/
├── drivers/
│   ├── firestore_driver.py       (arkistoitu referenssi)
│   └── postgresql_driver.py      ← UUSI (asyncpg + yhteyspooli + JSONB)
├── migrations/
│   ├── alembic.ini               ← UUSI (Alembic-konfiguraatio)
│   ├── env.py                    ← UUSI (Alembic-ajoympäristö)
│   └── versions/
│       └── 001_initial_schema.py ← UUSI (reprodusoitava DDL-skeema)
├── factory.py                    (päivitetään: palauttaa puhtaasti PostgreSQLDriverin)
├── interfaces.py                 (EI MUUTU — IUnifiedWorkflowRepository SSOT pysyy)
└── repository.py                 (UnifiedWorkflowRepository toimii PostgreSQLDriverin kanssa)
```

> [!NOTE]
> Tiedostot `backend_v2/database/tinydb_driver.py` ja `backend_v2/database/wrapper.py` (sisältäen OS-tiedostolukitukset `msvcrt`/`fcntl`) poistetaan kokonaan Phase 5:ssä.

---

## 2. Arkkitehtuuristen Sääntöjen Huomiointi (Compliance)

### 2.1. Ydinjärjestelmä (@[.agents/rules/00-antigravity-core.md])

* **the_zero_compromise_pledge**: `PostgreSQLDriver` noudattaa tiukasti `StorageDriver`- ja repository-rajapintoja ilman fallback-silmukoita tai duck-typingiä (`isinstance(dict)`).
* **universal_fail_fast**: Kaikki tietokantavirheet ja yhteyskatkot kääritään välittömästi tyypitetyiksi `AppException`-poikkeuksiksi RFC 7807 -muodossa (`ErrorCodes.STORAGE_ACCESS_FAILED`).
* **atomic_checkpoint_mandate**: Jokainen toteutusvaihe auditoidaan `backend_audit_loop.py` -skriptillä ja commitoidaan itsenäisenä atomisena kokonaisuutena.

### 2.2. Backend-arkkitehtuuri (@[.agents/rules/01-python-backend.md])

* **strict_pydantic_v2_rust**: Tietokannasta luku käyttää `.model_validate(row_dict, strict=False)` -muunnosta (sallii `asyncpg`:n natiivit `datetime`- ja `UUID`-tyypit), ja DTO-palautukset sekä tallennukset noudattavat `strict=True` / `.model_dump(mode='json')`.
* **no_naked_dicts_in_state**: Ei raakasanakirjojen välitystä sovelluslogiikassa; kaikki tietokantataulujen rivit hydratoidaan välittömästi Pydantic V2 -malleiksi repository-rajalla.
* **no_inline_imports**: `asyncpg` ja `alembic` tuodaan tiedoston ylätasolla globaalisti.

### 2.3. Tripartite- ja Kognitioarkkitehtuuri (@[ki_tripartite_pipeline_architecture.md])

* **tripartite_phase_isolation**: Heavy LLM Execution (Vaihe 1) tuottaa atomit ja kausaalilinkit muistiin Pydantic-malleina (`ExtractedAtom`, `LinkedAtomGraph`).
* **MatrixReducer Sovereignty**: `MatrixReducer` suorittaa kolmitilalogiikan (`reduce_exists`, `reduce_all_must_comply`, `reduce_matrix`) **puhtaasti in-memory -tilassa `ExecutionRecord.step_states` -datasta**. Kognition runtime-logiikkaan ei vuodeta tietokantakyselyitä.
* **Graph Querying Boundary**: `atoms`- ja `atom_links`-tauluja käytetään suorituksen jälkeiseen säilytykseen, XAI-jäljitettävyyteen, visualisointiin ja EU AI Act -auditointeihin (Vaihe 2/3), ei reaaliaikaisen DAG-tokenreduktion estäjänä.

---

## 3. Tietokantaskeema (Database Schema)

### 3.1. Relaatiotaulut ja JSONB-sarakkeet

```sql
-- Core execution tracking
CREATE TABLE executions (
    id                          TEXT PRIMARY KEY,
    workflow_id                 TEXT NOT NULL,
    workflow_version            INTEGER NOT NULL DEFAULT 1,
    status                      TEXT NOT NULL DEFAULT 'pending',
    error                       TEXT,
    target_locale               TEXT NOT NULL,
    active_profile_id           TEXT,
    output_profile_id           TEXT NOT NULL,
    pdf_report_path             TEXT,
    is_resumable                BOOLEAN NOT NULL DEFAULT FALSE,
    prompt_tokens               INTEGER NOT NULL DEFAULT 0,
    completion_tokens           INTEGER NOT NULL DEFAULT 0,
    cached_tokens               INTEGER NOT NULL DEFAULT 0,
    reasoning_tokens            INTEGER NOT NULL DEFAULT 0,
    cumulative_synthesis_tokens INTEGER NOT NULL DEFAULT 0,
    dag_cost_usd                DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    cumulative_synthesis_cost   DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    cost_estimate               DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    duration_ms                 INTEGER NOT NULL DEFAULT 0,
    metadata                    JSONB,
    raw_inputs                  JSONB NOT NULL DEFAULT '{}',
    frozen_context              JSONB,
    frozen_context_storage_path TEXT,
    execution_trace_storage_path TEXT,
    context_variables_storage_path TEXT,
    step_states                 JSONB NOT NULL DEFAULT '{}',
    steps                       JSONB NOT NULL DEFAULT '[]',
    profile_syntheses           JSONB NOT NULL DEFAULT '{}',
    source_identity_manifest    JSONB NOT NULL DEFAULT '{}',
    models_used                 JSONB NOT NULL DEFAULT '{}',
    execution_summary           JSONB,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at                TIMESTAMPTZ
);

-- Append-only event sourcing for trace events (O(1) write performance)
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

-- Workflows
CREATE TABLE workflows (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    slug        TEXT NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'draft',
    version     INTEGER NOT NULL DEFAULT 1,
    config      JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ
);

-- Steps (Task Blueprints)
CREATE TABLE steps (
    id          TEXT PRIMARY KEY,
    slug        TEXT NOT NULL,
    type        TEXT NOT NULL,
    config      JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ
);

-- Prompt Blocks (Evaluation Criteria, Matrices, Personas)
CREATE TABLE prompt_blocks (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    category_id TEXT NOT NULL,
    type        TEXT NOT NULL,
    config      JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ
);

-- Output Profiles (Presentation & SDUI Blueprints)
CREATE TABLE output_profiles (
    id                TEXT PRIMARY KEY,
    workflow_id       TEXT NOT NULL,
    name              TEXT NOT NULL,
    config            JSONB NOT NULL,
    strictness_level  INTEGER,
    scoring_strategy  TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ
);

-- Enriched Atom Graph: Nodes (Vertices)
CREATE TABLE atoms (
    id                    TEXT PRIMARY KEY,
    execution_id          TEXT NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    step_id               TEXT NOT NULL,
    claim_text            TEXT NOT NULL,
    atom_type             TEXT NOT NULL,
    status                TEXT NOT NULL,
    source_quote          TEXT,
    source_id             TEXT,
    reasoning             TEXT,
    extracted_facts       JSONB DEFAULT '{}',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enriched Atom Graph: Edges
CREATE TABLE atom_links (
    id              TEXT PRIMARY KEY,
    execution_id    TEXT NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    source_id       TEXT NOT NULL REFERENCES atoms(id) ON DELETE CASCADE,
    target_id       TEXT NOT NULL REFERENCES atoms(id) ON DELETE CASCADE,
    relation_type   TEXT NOT NULL,
    edge_reasoning  TEXT,
    weight          DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- System Configurations (Model Registry, MCP Gateways)
CREATE TABLE system_config (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,
    config      JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ
);

-- Organizations (IAM)
CREATE TABLE organizations (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    config      JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Users (IAM)
CREATE TABLE users (
    id              TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    email           TEXT NOT NULL,
    role            TEXT NOT NULL,
    deleted_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Invitations (IAM)
CREATE TABLE invitations (
    id              TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    email           TEXT NOT NULL,
    role            TEXT NOT NULL,
    invite_token    TEXT NOT NULL UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audit Log (Append-only)
CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    exec_id     TEXT,
    org_id      TEXT,
    action      TEXT NOT NULL,
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Performance Indexes
CREATE INDEX idx_executions_workflow ON executions(workflow_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_metadata ON executions USING GIN(metadata);
CREATE INDEX idx_trace_events_exec ON trace_events(exec_id, seq);
CREATE INDEX idx_workflows_slug ON workflows(slug);
CREATE INDEX idx_prompt_blocks_category ON prompt_blocks(category_id);
CREATE INDEX idx_atoms_execution ON atoms(execution_id);
CREATE INDEX idx_atoms_step ON atoms(step_id);
CREATE INDEX idx_atom_links_execution ON atom_links(execution_id);
CREATE INDEX idx_atom_links_source_target ON atom_links(source_id, target_id);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_audit_log_exec ON audit_log(exec_id);
```

### 3.2. Trace Events: Append-Only Tapahtumavirta

* **Kirjoitustehokkuus (O(1))**: Jokainen agentin tilasiirtymä tai lokitapahtuma lisää rivin `trace_events`-tauluun. 7 rinnakkaista taustatyöntekijää ei lukitse päätaulua `executions`.
* **Lukuhetken rekonstruointi**: `get_execution()` lukee päätietueen ja koostaa täyden trace-historian järjestyksessä `seq`:
  ```python
  async def get_execution(self, exec_id: str) -> ExecutionRecord | None:
      row = await self.pool.fetchrow("SELECT * FROM executions WHERE id = $1", exec_id)
      if not row:
          return None
      row_dict = dict(row)
      trace_rows = await self.pool.fetch(
          "SELECT content FROM trace_events WHERE exec_id = $1 ORDER BY seq ASC", exec_id
      )
      row_dict["execution_trace"] = [json.loads(r["content"]) if isinstance(r["content"], str) else r["content"] for r in trace_rows]
      return ExecutionRecord.model_validate(row_dict, strict=False)
  ```

### 3.3. Tenant-eristys ja Row-Level Security (RLS)

* **Istuntokohtainen transaktioeristys**: Transaktion avauksen yhteydessä ajuri asettaa lokaalin organisaatiomuuttujan:
  ```sql
  SET LOCAL quorum.current_org = '<org_id>';
  ```
* **Vuotosuoja**: Avainsana `LOCAL` nollaa organisaatiotunnisteen transaktion päättyessä (`COMMIT`/`ROLLBACK`), mikä estää yhteyksien jakamisesta johtuvat tietovuodot.

---

## 4. Toteutussuunnitelma (Implementation Phases)

### Phase 1: PostgreSQL-infrastruktuuri ja Alembic-skeema
* **Tehtävä 1.1**: Lisää `asyncpg>=0.30.0` ja `alembic>=1.14.0` `pyproject.toml`-riippuvuuksiin.
* **Tehtävä 1.2**: Konfiguroi `docker-compose.dev.yml` ja `docker-compose.yml` (`postgres:16-alpine`, portti 5432, voluumi `pgdata`).
* **Tehtävä 1.3**: Alusta `migrations/alembic.ini`, `migrations/env.py` ja luo migraatiotiedosto `migrations/versions/001_initial_schema.py`.
* **Tehtävä 1.4**: Päivitä `backend_v2/settings.py` lisäämällä `database_url: str`, `postgres_pool_min_size: int = 5` ja `postgres_pool_max_size: int = 20`.

### Phase 2: PostgreSQLDriver ja Yhteyspooli
* **Tehtävä 2.1**: Toteuta `backend_v2/database/drivers/postgresql_driver.py` (`asyncpg.Pool`, transaktionhallinta, query/get/upsert/delete -toteutukset).
* **Tehtävä 2.2**: Päivitä `backend_v2/database/factory.py` palauttamaan puhtaasti `PostgreSQLDriver` asynkronisesti.
* **Tehtävä 2.3**: Varmista Pydantic V2 -hydraatiorajat (`strict=False` tietokantahaussa, `strict=True` DTO-rajalla).

### Phase 3: Seeder- ja Datamigraatio
* **Tehtävä 3.1**: Päivitä `backend_v2/seed/run_seed.py` tukemaan PostgreSQL-kantaa: Two-Phase Seeder validoi in-memory `STANDARD_REGISTRY`:n ja ajaa atomic transaktion PostgreSQL:ään.
* **Tehtävä 3.2**: Päivitä `backend_v2/seed/seed_registry.py` varmistamaan 1:1 vastaavuus taulujen ja Pydantic-mallien välillä.
* **Tehtävä 3.3**: Suorita testiseedaus ja varmista `audit_database_atoms.py --strict` -tarkastuksen läpimeno.

### Phase 4: Contract- ja Rinnakkaisuustestit
* **Tehtävä 4.1**: Luo `backend_v2/tests/integration/test_postgresql_driver.py` käyttäen Testcontainers-konttia (`pytest-testcontainers` / `PostgresContainer`).
* **Tehtävä 4.2**: Testaa 7 samanaikaisen worker-tehtävän rinnakkaista `trace_events`-kirjoitusta ilman lukkiutumisia.
* **Tehtävä 4.3**: Varmista, että yksikkötestit jatkavat luotettavien `backend_v2/tests/fakes/in_memory_repositories.py` -feikkien käyttöä (QGR014-sääntö).

### Phase 5: TinyDB:n ja Legacy-wrapperien Täydellinen Decommissionointi
* **Tehtävä 5.1**: Poista `tinydb` tiedostoista `pyproject.toml`, `requirements.txt` ja `uv.lock`.
* **Tehtävä 5.2**: Poista fyysisesti `backend_v2/database/tinydb_driver.py`, `backend_v2/database/wrapper.py`, `data/db_v2.json` ja `.lock`-tiedostot.
* **Tehtävä 5.3**: Siivoa `backend_v2/database/repositories/workflow.py` poistamalla levyfallbackit (`data/workflows/{id}.json`).
* **Tehtävä 5.4**: Päivitä `scripts/_ast_guardrails.py` estämään TinyDB-importit ja varmista täysi laatuportti `backend_audit_loop.py`.

---

## 5. Docker-Compose (Lokaali Kehitysympäristö)

```yaml
# docker-compose.dev.yml
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    container_name: quorum-postgres-dev
    environment:
      POSTGRES_DB: quorum_dev
      POSTGRES_USER: quorum
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quorum -d quorum_dev"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: quorum-redis-dev
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

---

## 6. Verifiointisuunnitelma (Verification Plan)

| Tarkistus | Menetelmä / Komento | Hyväksymiskriteeri |
|---|---|---|
| **Skeeman migraatiot** | `uv run alembic upgrade head` | DDL-taulut ja indeksit luodaan ilman virheitä |
| **Seeder-integraatio** | `uv run python backend_v2/seed/run_seed.py local` | Kaikki kokoelmat seedataan PostgreSQL:ään ja auditointi läpäistään |
| **Rinnakkaistestaus** | `uv run pytest backend_v2/tests/integration/test_postgresql_driver.py` | 7 rinnakkaista append-only kirjoitusta ilman lukkiutumista |
| **AST Guardrail Gate** | `uv run python scripts/_ast_guardrails.py` | 0 FATAL-rikkomusta; TinyDB-importit estetty |
| **Täysi laatuportti** | `uv run python scripts/backend_audit_loop.py backend_v2 --test` | Ruff, MyPy ja testit 100% vihreänä |

---

## 7. Riippuvuudet ja Rajaukset

* **Ei suoranaisia frontend-muutoksia**: `client_app_v2` kuluttaa samoja REST/SSE-rajapintoja ja DTO-sopimuksia.
* **TinyDB poistetaan kokonaan**: Ei rinnakkaiskantoja tai lokaaleja JSON-tiedostokantoja tuotannossa eikä dev-tilassa.
* **Yksikkötestit**: Yksikkötestit käyttävät `backend_v2/tests/fakes/in_memory_repositories.py` -feikkejä ilman tietokantariippuvuutta.
* **Riippuvuudet**: `asyncpg>=0.30.0`, `alembic>=1.14.0`, `testcontainers[postgres]>=4.9.0`.
