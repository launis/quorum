# Phase 1: Pydantic Schema and Evaluation DTO Hardening

## 1. Yhteenveto
Tässä vaiheessa toteutetaan tarvittavat Pydantic-mallien ja DTO-luokkien rakennemuutokset, jotta väitetasoinen kontekstuaalinen ohitus (`allow_contextual_override`) saadaan tietokantatason ja tuomioistuimen sääntöarviointimoottorin käyttöön.

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py) - Lisätään `allow_contextual_override` Pydantic-säännölle.
* [lightweight_matrix.py](file:///c:/src/quorum/backend_v2/models/dtos/lightweight_matrix.py) - Päivitetään säännön arviointilogiikka (`AtomEvaluationItemDTO`).

### B. Lukuoikeus (Context - Read-Only)
* [01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md) - Taustajärjestelmän arkkitehtuurisäännöt.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: TDAAssertion-skeeman laajennus
* **Tiedosto**: `backend_v2/models/v2_core.py`
* **Tehtävä**: Lisää `allow_contextual_override: bool = Field(default=False, description="...")` `TDAAssertion`-luokkaan.
* **Arkkitehtuurisääntö**: Kaikki Pydantic-mallit ovat tiukasti tyypitettyjä eikä ylimääräisiä tyyppejä tai fallbackeja sallita (`ConfigDict(extra='forbid', strict=True)`).
* **Source**: Epic 59, Section 4.A.

### Milestone 2: Deterministisen sääntömoottorin päivitys
* **Tiedosto**: `backend_v2/models/dtos/lightweight_matrix.py`
* **Tehtävä**: Päivitä `calculate_rule_satisfied` ottamaan vastaan `allow_contextual_override` -lippu. Jos se on `True` ja LLM:n palauttama `contextual_override` on `True`, sääntö katsotaan täyttyneeksi ilman fyysistä sitaattia (`evidence_found` ohitetaan).
* **Source**: Epic 59, Section 4.A.

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattiset testit (Pytest)
Aja luotujen skeemojen ja luokkien yksikkötestit varmistaaksesi, ettei mikään nykyinen sääntö arvioidu väärin:
```powershell
uv run pytest backend_v2/tests/unit/services/orchestrator/test_atomizer.py -v
```

### B. Staattinen analyysi ja laatuportit (Quality Gates)
Varmista, ettei tyypitys rikkoudu ja koodi noudattaa Phase 9 Ruff-standardeja:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py
```

---

## 5. Istunnon Handover (Session Handover)

> [!NOTE]
> Kun tämä vaihe on valmis ja testit menevät läpi, päivitä tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` asettamalla tämä vaihe tilaan `[x]`.

Aloita seuraava vaihe ajamalla:
```powershell
/tier5-resume --target docs/epic/tasks_EPIC_59/phase2_prompt_compiler_and_scoring.md
```
