# Phase 4: Verification, Quality Gate and Architecture Hardening

## 1. Yhteenveto
Tässä vaiheessa suoritetaan täydellinen arkkitehtuurin kovettaminen (Hardening) ja verifiointi. Varmistetaan, että kaikki yksikkö- ja integraatiotestit menevät läpi, OpenAPI-speksi generoidaan virheettömästi ja arkkitehtuuridokumentaatio päivitetään vastaamaan uutta väitetasoista ohitusventtiiliä.

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [technical_architecture_summary.md](file:///c:/src/quorum/docs/architecture/technical_architecture_summary.md) - Päivitetään arkkitehtuuridokumentaatio.

### B. Lukuoikeus (Context - Read-Only)
* [00-antigravity-core.md](file:///c:/src/quorum/.agents/rules/00-antigravity-core.md) - Yleiset arkkitehtuurilait.
* [01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md) - Taustajärjestelmän säännöt.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: Integraatiotason verifiointi
* **Tehtävä**: Suoritetaan testiajo, joka tarkastaa koko TDA- ja pisteytysketjun toimivuuden:
  ```powershell
  uv run pytest backend_v2/tests/unit/services/orchestrator/test_atomizer.py -v
  uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -v
  ```
* **Source**: Epic 59, Section 6.

### Milestone 2: Staattinen laatuportti (Ruff / Mypy / OpenAPI)
* **Tehtävä**: Ajetaan staattisen laadun tarkastukset koko muuttuneelle koodille:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi
  uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py
  uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py
  ```
* **Source**: Epic 59, Section 6 & rule_block id="pydantic_namespace_collisions".

### Milestone 3: Arkkitehtuuridokumentaation päivitys
* **Tiedosto**: `docs/architecture/technical_architecture_summary.md` (tai vastaava)
* **Tehtävä**: Lisää lyhyt kuvaus Claim-Level Contextual Override -arkkitehtuurista ja sen suojamuureista kognitiivisen arviointimoottorin osioon.
* **Source**: Epic 59, Section 6.

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattinen loppuauditointi
Varmista, ettei taustajärjestelmä heitä yhtäkään `DeprecationWarning`- tai tyyppivirhettä:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py
```

---

## 5. Istunnon Handover (Session Handover)

> [!NOTE]
> Kun tämä vaihe on valmis ja testit menevät läpi, päivitä tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` asettamalla tämä vaihe tilaan `[x]`.

Tämä Epic on nyt valmis ja täydellisesti verifioitu!
Koska kaikki vaiheet on suoritettu, voit päättää continuous loopin ja raportoida onnistumisesta käyttäjälle.
