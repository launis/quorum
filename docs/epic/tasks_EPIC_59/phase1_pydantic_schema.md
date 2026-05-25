# Phase 1: Pydantic Schema, Micro-CoT Lists and Evaluation DTO Hardening

## 1. Yhteenveto
Tässä vaiheessa toteutetaan Pydantic-tason skeemamuutokset ja DTO-laajennukset kognitiivisen ohitusventtiilin sekä System 2 Zero-Variance -suojamuurien käyttönottoa varten. Korjataan dynaamisten skeemojen luonti (`extraction_schema_factory.py`) estämään `extra="forbid"`-kaatumiset, lisätään spatiaaliset ankkurointivaatimukset ja toteutetaan Unicode NFKC -normalisoitu fuzzy-validaattori sitaateille.

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [extraction_schema_factory.py](file:///c:/src/quorum/backend_v2/services/orchestrator/extraction_schema_factory.py) - Dynaamisen vastausskeeman laajentaminen (`contextual_override` ja `semantic_reasoning` -kenttien lisäys).
* [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py) - Mallien `TDAAssertion` ja `Workflow` laajennus.
* [lightweight_matrix.py](file:///c:/src/quorum/backend_v2/models/dtos/lightweight_matrix.py) - `AtomEvaluationItemDTO`-luokan sitaatti- ja anti-laziness -validaattoreiden toteutus.

### B. Lukuoikeus (Context - Read-Only)
* [00-antigravity-core.md](file:///c:/src/quorum/.agents/rules/00-antigravity-core.md) - Core arkkitehtuurisäännöt.
* [01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md) - Python-arkkitehtuurisäännöt.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: Purkuskeeman dynaaminen laajennus (`extraction_schema_factory.py`)
* **Tiedosto**: `backend_v2/services/orchestrator/extraction_schema_factory.py`
* **Tehtävä**: Muokkaa `create_extraction_model`-funktiota siten, että dynaamisesti luotavaan `DynamicExtractionResponse` -malliin lisätään aina `contextual_override` ja `semantic_reasoning` -kentät:
  ```python
  "contextual_override": (bool, Field(default=False, description="If True, contextual override is applied")),
  "semantic_reasoning": (str, Field(default="", description="Detailed semantic explanation")),
  ```
  Tämä estää Pydanticin `extra="forbid"` -konfiguraatiota kaatamasta LLM-kutsun vastausta, kun tekoäly palauttaa ohitustietoja.
* **Arkkitehtuurisääntö**: `ConfigDict(extra='forbid', strict=True)` on pidettävä sataprosenttisen puhtaana; kaikki rajapintakentät on deklaroitava eksplisiittisesti.
* **Source**: Epic 59, Section 4.A & B.

### Milestone 2: TDAAssertion & Workflow Schema -laajennus
* **Tiedosto**: `backend_v2/models/v2_core.py`
* **Tehtävä**:
  1. Lisää `TDAAssertion`-malliin kenttä:
     ```python
     allow_contextual_override: bool = Field(default=False, description="...")
     ```
  2. Lisää `Workflow`-malliin kenttä:
     ```python
     enable_contextual_overrides: bool = Field(default=False, description="...")
     ```
* **Arkkitehtuurisääntö**: Kaikki Pydantic-määritykset on tyypitettävä tiukasti ilman fallback-rakenteita.
* **Source**: Epic 59, Section 4.A.

### Milestone 3: Unicode NFKC Fuzzy-validaattori & Bypass (`lightweight_matrix.py`)
* **Tiedosto**: `backend_v2/models/dtos/lightweight_matrix.py`
* **Tehtävä**: Toteuta `AtomEvaluationItemDTO`-luokkaan `@model_validator(mode="after")` (`_enforce_zero_variance_protocols`), joka:
  1. Tarkistaa sitaatin eheyden: Jos `contextual_override` on `True`, ohita tarkistus kokonaan. Jos `contextual_override` on `False`, tarkista että `exact_quote` löytyy syötetekstistä.
  2. Jotta PDF/HTML-tekstinuuton ligatuurit ja rivinvaihdot eivät aiheuta vääriä hälytyksiä, **normalisoi sekä syöteteksti että `exact_quote` käyttäen `unicodedata.normalize('NFKC', ...)` -funktiota**, siivoa tyhjät välit (whitespace normalization) ja salli joustava Levenshtein-similarity osumatarkkuus (>95% osuma hyväksytään).
* **Source**: Epic 59, Section 4.A & B.

### Milestone 4: Spatiaalinen ankkurointi & Anti-Laziness -enforcement
* **Tiedosto**: `backend_v2/models/dtos/lightweight_matrix.py`
* **Tehtävä**: Laajenna `_enforce_zero_variance_protocols` -validaattoria siten, että jos `contextual_override` on asetettu arvoon `True`, Pydantic pakottaa laiskuudenestorajat:
  1. `len(semantic_reasoning)` on oltava **vähintään 50 merkkiä pitkä**.
  2. `semantic_reasoning` -perustelun on **sisällettävä spatiaalinen/rakenteellinen sijaintiviite** (esim. sivunumero, kappaleindeksi tai väliotsikko, kuten *"page"*, *"paragraph"*, *"section"* tai *"kappale"*).
  Jos ehdot eivät täyty, validaattorin on heitettävä `ValidationError` tai merkitsettävä status `DLQ`-tilaan.
* **Source**: Epic 59, Section 2.B & 4.A.

### Milestone 5: Telemetria ja ohjaus DTO Hardening
* **Tehtävä**: Päivitä `ValidationWarningDTO` tukemaan entropia- ja virhekooditelemetriaa ja luo `HardeningRetryDirectiveDTO` dynaamista orkestrointia varten.
* **Source**: Epic Phase 1.

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattiset yksikkötestit (Pytest)
Aja dynaamisten skeemojen ja arviointilogiikan testit:
```powershell
uv run pytest backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py -v
```

### B. Staattiset laatuportit (Quality Gates)
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extraction_schema_factory.py
```

---

## 5. Istunnon Handover (Session Handover)

> [IMPORTANT]
> Aina onnistuneen työvaiheen ja auditointisilmukan jälkeen suorita kansion tarkka commit:
> `git add backend_v2/services/orchestrator/extraction_schema_factory.py backend_v2/models/v2_core.py backend_v2/models/dtos/lightweight_matrix.py`
> `git commit -m "feat(epic-59): completed phase 1 schemas and fuzzy validators"`

Kun tämä vaihe on täysin valmis ja laatuportit ovat vihreänä, merkitse tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` täytetyksi askeleeksi (`[x]`).

Siirry seuraavaan vaiheeseen ajamalla:
```powershell
/tier5-resume --target docs/epic/tasks_EPIC_59/phase2_prompt_compiler_and_scoring.md
```
