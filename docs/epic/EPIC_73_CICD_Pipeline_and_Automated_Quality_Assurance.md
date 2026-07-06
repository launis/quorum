# Epic 73: CI/CD Pipeline ja Automaattinen Laadunvarmistus

> [!IMPORTANT]
> **AUTOMAATION SUVERENITEETTI**: Tämä Epic toteuttaa GitHub Actions -pohjaisen CI/CD-putken, joka ajaa laadunvarmistuksen (Quality Gate), integraatiotestit (`testcontainers`) ja tuotantoon deployauksen automaattisesti. Tavoitteena on siirtää manuaalinen `backend_audit_loop.py`-ajo ja Docker-buildi koneelliseksi prosessiksi.

---

## 1. Yhteenveto ja Tavoite (Objective)

Tämän Epicin tavoitteena on rakentaa luotettava, vaiheittainen CI/CD-putki, joka:

1. **Estää regressiot automaattisesti** — jokainen push tarkistetaan Quality Gatella
2. **Validoi tietokantapariteetti** — TinyDB ja PostgreSQL ajetaan samoja testejä vasten
3. **Rakentaa tuotantokelpoisen Docker-imagen** — ilman manuaalisia vaiheita
4. **Deployaa staging-ympäristöön automaattisesti** — `main`-branchista

### Tunnistetut Nykytilan Haasteet

| Ongelma | Nykytila | CI/CD-ratkaisu |
|---|---|---|
| **Manuaalinen QG** | Käyttäjä ajaa `backend_audit_loop.py` käsin | GitHub Actions ajaa automaattisesti per push |
| **Ei integraatiotestejä** | Vain yksikkötestit TinyDB:llä | `testcontainers` pyörittää PG + Redis |
| **Ei Docker-buildia** | Ei Dockerfileä | Multi-stage build + vulnerability scan |
| **Ei staging-deployta** | Manuaalinen Cloud Run deploy | Automaattinen `main`-branchista |

---

## 2. Arkkitehtuuristen Sääntöjen Huomiointi (Compliance)

### 2.1. Ydinjärjestelmä (00-antigravity-core.md)

* **tdd_mandate**: CI/CD-putki ajaa testit automaattisesti — regressiot eivät pääse tuotantoon.
* **atomic_checkpoint_mandate**: Jokainen CI-vaihe on itsenäinen — epäonnistuminen pysäyttää putken.
* **mocking_mandate_for_llm**: CI-ympäristössä ei koskaan tehdä live-LLM-kutsuja — MockLLM ja JSON-fixturet.

### 2.2. Backend-arkkitehtuuri (01-python-backend.md)

* **eager_llm_dependency_loading**: Docker-image ei sisällä turhia ML-riippuvuuksia testitasossa.
* **security_logging_ban**: CI-lokit eivät paljasta API-avaimia tai PII-dataa — Secret Manager.

---

## 3. Pipeline-arkkitehtuuri

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                       │
├─────────────┬──────────────┬──────────────┬─────────────────────┤
│  quality    │  unit-tests  │  integration │  deploy-staging     │
│  gate       │              │  tests       │                     │
├─────────────┼──────────────┼──────────────┼─────────────────────┤
│ Ruff check  │ pytest       │ testcontainers│ Docker build       │
│ Ruff format │ TinyDB       │ PostgreSQL 16 │ Push to GCR        │
│ MyPy strict │ MockLLM      │ Redis 7       │ Cloud Run deploy   │
│             │ Coverage 30% │ Contract tests│ Smoke test         │
├─────────────┼──────────────┼──────────────┼─────────────────────┤
│ ~10s        │ ~15s         │ ~45s         │ ~2min               │
│ Kaikki PR   │ Kaikki PR    │ Kaikki PR    │ Vain main           │
└─────────────┴──────────────┴──────────────┴─────────────────────┘
```

---

## 4. Toteutussuunnitelma (Implementation Phases)

### Phase 1: GitHub Actions Workflow (1 sessio)

#### 4.1.1. Quality Gate Job

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - run: uv sync --frozen
      - name: Ruff Check
        run: uv run ruff check backend_v2/
      - name: Ruff Format
        run: uv run ruff format --check backend_v2/
      - name: MyPy Strict
        run: uv run mypy --strict backend_v2/
```

#### 4.1.2. Unit Tests Job

```yaml
  unit-tests:
    needs: quality-gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --frozen
      - name: Run Tests with Coverage
        run: |
          uv run pytest backend_v2/tests/unit/ \
            -v --tb=short \
            --cov=backend_v2 \
            --cov-fail-under=30 \
            --cov-report=xml
      - uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

#### 4.1.3. Integration Tests Job

```yaml
  integration-tests:
    needs: quality-gate
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: quorum_test
          POSTGRES_USER: quorum
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --frozen
      - name: Run Integration Tests
        env:
          QUORUM_DB_DRIVER: postgresql
          DATABASE_URL: postgresql://quorum:test_password@localhost:5432/quorum_test
          REDIS_HOST: localhost
          REDIS_PORT: 6379
        run: |
          uv run alembic upgrade head
          uv run pytest backend_v2/tests/integration/ \
            -v --tb=short \
            -m "integration"
```

### Phase 2: Docker Build (1 sessio)

#### 4.2.1. Multi-stage Dockerfile

```dockerfile
# Dockerfile
FROM python:3.14-slim AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.14-slim AS runtime

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY backend_v2/ backend_v2/
COPY migrations/ migrations/
COPY alembic.ini .

ENV PATH="/app/.venv/bin:$PATH"
ENV QUORUM_DB_DRIVER=postgresql

# Health check
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "backend_v2.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4.2.2. Worker Dockerfile

```dockerfile
# Dockerfile.worker
FROM python:3.14-slim AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.14-slim AS runtime

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY backend_v2/ backend_v2/
COPY migrations/ migrations/

ENV PATH="/app/.venv/bin:$PATH"
ENV QUORUM_DB_DRIVER=postgresql

CMD ["python", "-m", "arq", "backend_v2.worker.WorkerSettings"]
```

#### 4.2.3. Deploy Job (vain main)

```yaml
  deploy-staging:
    needs: [unit-tests, integration-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - uses: google-github-actions/setup-gcloud@v2
      - name: Build and Push
        run: |
          gcloud builds submit \
            --tag gcr.io/${{ secrets.GCP_PROJECT }}/quorum-api:${{ github.sha }}
          gcloud builds submit \
            -f Dockerfile.worker \
            --tag gcr.io/${{ secrets.GCP_PROJECT }}/quorum-worker:${{ github.sha }}
      - name: Deploy API
        run: |
          gcloud run deploy quorum-api-staging \
            --image gcr.io/${{ secrets.GCP_PROJECT }}/quorum-api:${{ github.sha }} \
            --region europe-north1 \
            --platform managed \
            --allow-unauthenticated=false \
            --set-env-vars "QUORUM_DB_DRIVER=postgresql"
      - name: Deploy Worker
        run: |
          gcloud run deploy quorum-worker-staging \
            --image gcr.io/${{ secrets.GCP_PROJECT }}/quorum-worker:${{ github.sha }} \
            --region europe-north1 \
            --platform managed \
            --no-allow-unauthenticated \
            --min-instances 1
      - name: Smoke Test
        run: |
          curl -f https://quorum-api-staging-*.run.app/health || exit 1
```

---

## 5. Contract-testit (TinyDB ↔ PostgreSQL pariteetti)

### 5.1. Parametrisoitu Repository Fixture

```python
# backend_v2/tests/conftest.py

import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(params=["tinydb", "postgresql"])
async def repository(request, tmp_path):
    """Sama IRepository-sopimus testataan molemmilla drivereilla."""
    if request.param == "tinydb":
        from backend_v2.database.drivers.tinydb_driver import TinyDBDriver
        driver = TinyDBDriver(str(tmp_path / "test.json"))
        yield driver
    else:
        with PostgresContainer("postgres:16-alpine") as pg:
            from backend_v2.database.drivers.postgresql_driver import PostgreSQLDriver
            driver = await PostgreSQLDriver.create(pg.get_connection_url())
            yield driver
            await driver.close()
```

### 5.2. Contract-testiesimerkki

```python
# backend_v2/tests/contract/test_repository_contract.py

@pytest.mark.asyncio
async def test_execution_create_and_read(repository):
    """Varmistaa, että molemmat driverit tuottavat identtisen tuloksen."""
    exec_data = {
        "id": "exe_test123",
        "workflow_id": "wf_test456",
        "status": "running",
        "metadata": {"org_id": "org_1"},
        "execution_trace": [],
        "step_states": {},
    }
    await repository.create_execution(exec_data)
    result = await repository.get_execution("exe_test123")
    assert result is not None
    assert result["status"] == "running"
    assert result["workflow_id"] == "wf_test456"

@pytest.mark.asyncio
async def test_trace_append_and_reconstruct(repository):
    """Varmistaa append-only trace-pariteetti."""
    await repository.create_execution({"id": "exe_trace1", ...})
    await repository.append_trace_event("exe_trace1", {
        "step_name": "sr_step1",
        "event_type": "output",
        "content": {"score": 85},
    })
    result = await repository.get_execution("exe_trace1")
    assert len(result["execution_trace"]) == 1
    assert result["execution_trace"][0]["step_name"] == "sr_step1"
```

---

## 6. Tiedostorakenne (uudet tiedostot)

```
.github/
└── workflows/
    └── ci.yml                              ← GitHub Actions pipeline

Dockerfile                                  ← API multi-stage build
Dockerfile.worker                           ← Worker multi-stage build
docker-compose.dev.yml                      ← Lokaali PG + Redis

backend_v2/tests/
├── contract/
│   └── test_repository_contract.py         ← TinyDB ↔ PG pariteetti
└── integration/
    ├── conftest.py                         ← testcontainers fixtures
    └── test_concurrent_execution.py        ← Rinnakkaisuustesti
```

---

## 7. Verifiointisuunnitelma (Verification)

| Tarkistus | Menetelmä | Hyväksymiskriteeri |
|---|---|---|
| Quality Gate CI | Push → GitHub Actions | Ruff + MyPy + Format vihreä |
| Unit Tests CI | GitHub Actions `unit-tests` job | 30%+ coverage, 0 failures |
| Integration Tests | GitHub Actions `integration-tests` job | PG + Redis testit vihreä |
| Contract Tests | Parametrisoitu TinyDB/PG suite | 100% identtinen käyttäytyminen |
| Docker Build | `docker build -t quorum-api .` | Build onnistuu, health check OK |
| Staging Deploy | `main`-push → Cloud Run | Smoke test palauttaa 200 OK |

---

## 8. Riippuvuudet ja Rajaukset

* **Vaatii Epic 72**: PostgreSQL-driver on oltava valmis ennen integraatiotestejä
* **Ei vaadi Epic 74**: CI/CD voidaan rakentaa ilman tuotantoinfraa
* **GitHub Secrets**: `GCP_SA_KEY`, `GCP_PROJECT` konfiguroitava
* **Kustannus**: GitHub Actions ilmainen public-repoille, private: 2000 min/kk ilmaiseksi
* **Riippuvuudet**: `testcontainers[postgres]`, `pytest-cov`, `codecov`
