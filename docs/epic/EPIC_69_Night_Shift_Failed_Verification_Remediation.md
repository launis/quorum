# EPIC 69: Night Shift FAILED_VERIFICATION Remediation (Vaiheistettu Priorisoitu Ajo)

## 1. Background & Motivation

Night Shift Hardener (`scripts/night_shift_hardener.py`) suoritettiin 2.6.2026 yöajona koko `backend_v2/` -koodikannalle. Noin 60 tiedostoa läpäisi kaikkien kolmen Pass-vaiheen (1–3) Quality Gate -tarkistukset ja merkittiin `DONE`-tilaan. Kuitenkin **41 tiedostoa** epäonnistui verifiointivaiheessa ja tallennettiin `FAILED_VERIFICATION` -tilaan `tmp/night_shift_state.json` -tiedostoon.

Jokaiselle epäonnistuneelle tiedostolle hardener tallensi osittain korjatun version `*_needs_review.py` -nimellä alkuperäisen tiedoston viereen. Nämä ovat LLM:n tuottamia refaktorointeja, jotka eivät läpäisseet MyPy/Ruff/Bandit/TDD-porttia kaikissa yrityksissä (max 5 yritystä per Pass).

**Juurisyy**: Ajon aikana `hardening.xml` Rule 47 (`zero_db_hardcoding_mandate`) aiheutti regressioita poistamalla loogisesti välttämättömiä ehtolauseita. Tämä korjattiin istunnon aikana lisäämällä Rule 47:ään `dynamic_translation_mandate`, joka pakottaa hardenerin kääntämään kovakoodaukset dynaamisiksi lausekkeiksi sen sijaan, että ne poistetaan sokeasti. Korjattu `hardening.xml` on nyt voimassa.

## 2. Architectural Objectives

1. **Systemaattinen korjaus**: Käydä läpi kaikki 41 epäonnistunutta tiedostoa hallitusti, priorisoiden riskiprofiilin mukaan.
2. **Regressioturvallisuus**: Jokaisen tason jälkeen varmistetaan arkkitehtuurin eheys (`pytest --collect-only`) ja ajettavat yksikkötestit.
3. **Päivitetty sääntökanta**: Käytetään korjattua `hardening.xml`:ää (Rule 47 + Rule 86 päivitykset), joka estää aikaisemman regression toistumisen.
4. **Atomic Rollback**: Git stash -pohjainen backup ennen jokaista vaihetta.

## 3. Tilannekatsaus

| Mittari | Arvo |
|---|---|
| DONE (onnistuneet) | ~60 tiedostoa |
| FAILED_VERIFICATION | 41 tiedostoa |
| `_needs_review.py` levyllä | 41 kpl |
| Audit-raportit (`tmp/audit_reports/`) | 61 raporttia |
| Korjattu `hardening.xml` | ✅ Rule 47 + Rule 86 päivitetty |

## 4. Backup-protokolla

Ennen jokaisen vaiheen aloittamista:

```powershell
git add -A
git stash push -m "pre-epic69-phase-N-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
```

Palautus tarvittaessa:

```powershell
git stash pop
```

## 5. Implementation Phases

### Phase 1: Domain Models (matalin riski, 13 tiedostoa)

Pydantic-mallit, joissa tyypillinen virhesyy on MyPy-tyyppiannotaatio, puuttuva docstring tai `Optional[X]` → `X | None` -modernisointi.

**Kohdetiedostot:**

| # | Tiedosto | Alkuperäinen | Review-tiedosto |
|---|---|---|---|
| 1 | `models/domain/analyst.py` | `backend_v2/models/domain/analyst.py` | `analyst_needs_review.py` |
| 2 | `models/domain/base.py` | `backend_v2/models/domain/base.py` | `base_needs_review.py` |
| 3 | `models/domain/causal.py` | `backend_v2/models/domain/causal.py` | `causal_needs_review.py` |
| 4 | `models/domain/evaluation.py` | `backend_v2/models/domain/evaluation.py` | `evaluation_needs_review.py` |
| 5 | `models/domain/guard.py` | `backend_v2/models/domain/guard.py` | `guard_needs_review.py` |
| 6 | `models/domain/mcp.py` | `backend_v2/models/domain/mcp.py` | `mcp_needs_review.py` |
| 7 | `models/domain/overseer.py` | `backend_v2/models/domain/overseer.py` | `overseer_needs_review.py` |
| 8 | `models/domain/references.py` | `backend_v2/models/domain/references.py` | `references_needs_review.py` |
| 9 | `models/domain/retrieval.py` | `backend_v2/models/domain/retrieval.py` | `retrieval_needs_review.py` |
| 10 | `models/domain/security.py` | `backend_v2/models/domain/security.py` | `security_needs_review.py` |
| 11 | `models/domain/validation.py` | `backend_v2/models/domain/validation.py` | `validation_needs_review.py` |
| 12 | `models/dtos/output_profile.py` | `backend_v2/models/dtos/output_profile.py` | `output_profile_needs_review.py` |
| 13 | `models/dtos/lightweight_matrix.py` | `backend_v2/models/dtos/lightweight_matrix.py` | `lightweight_matrix_needs_review.py` |

**Suorituskomento:**

```powershell
# Vaihtoehto A: Resume (vain Pass 3, nopeampi)
uv run python scripts/night_shift_hardener.py --resume-failed

# Vaihtoehto B: Uudelleenajo alkuperäisestä (kaikki 3 passia, perusteellisempi)
uv run python scripts/night_shift_hardener.py backend_v2/models/domain
uv run python scripts/night_shift_hardener.py backend_v2/models/dtos
```

**Verifiointitarkistus Phase 1:n jälkeen:**

```powershell
# 1. Arkkitehtuurin eheys
uv run pytest backend_v2 --collect-only

# 2. Yksikkötestit
uv run pytest backend_v2/tests -q

# 3. Tilan tarkistus
uv run python -c "import json; d=json.load(open('tmp/night_shift_state.json')); print(f'DONE: {list(d.values()).count(\"DONE\")}, FAILED: {list(d.values()).count(\"FAILED_VERIFICATION\")}')"
```

---

### Phase 2: Core & Infrastructure (keskitason riski, 14 tiedostoa)

Infrastruktuurikomponentit: auth, database-repositories, LLM-client, rate limiting, logging. Virhe voi liittyä monimutkaisempiin importteihin tai palveluriippuvuuksiin.

**Kohdetiedostot:**

| # | Tiedosto |
|---|---|
| 1 | `models/auth.py` |
| 2 | `models/state.py` |
| 3 | `logging_config.py` |
| 4 | `extraction_schema_factory.py` |
| 5 | `core/hook_registry.py` |
| 6 | `core/rate_limit.py` |
| 7 | `database/repository.py` |
| 8 | `database/repositories/component.py` |
| 9 | `database/repositories/workflow.py` |
| 10 | `llm/client.py` |
| 11 | `llm/provider.py` |
| 12 | `seed/run_seed.py` |
| 13 | `utils/math_utils.py` |
| 14 | `utils/scoring/dampening_engine.py` |

**Suorituskomennot (hakemistoittain):**

```powershell
uv run python scripts/night_shift_hardener.py backend_v2/core
uv run python scripts/night_shift_hardener.py backend_v2/database
uv run python scripts/night_shift_hardener.py backend_v2/llm
uv run python scripts/night_shift_hardener.py backend_v2/utils
uv run python scripts/night_shift_hardener.py backend_v2/models/auth.py
uv run python scripts/night_shift_hardener.py backend_v2/models/state.py
uv run python scripts/night_shift_hardener.py backend_v2/logging_config.py
uv run python scripts/night_shift_hardener.py backend_v2/extraction_schema_factory.py
uv run python scripts/night_shift_hardener.py backend_v2/seed/run_seed.py
```

**Verifiointitarkistus Phase 2:n jälkeen:** Sama kuin Phase 1.

---

### Phase 3: Services & Hooks (korkein riski, 14 tiedostoa)

Palvelulogiikka ja workflow-hookit — monimutkaisin logiikka, suurin regressioriski. Näissä `hardening.xml` Rule 47 -korjaus on erityisen kriittinen.

**Kohdetiedostot:**

| # | Tiedosto |
|---|---|
| 1 | `hooks/atom_flattening.py` |
| 2 | `hooks/input_processing.py` |
| 3 | `hooks/translation_hook.py` |
| 4 | `worker.py` |
| 5 | `services/execution.py` |
| 6 | `services/flattener.py` |
| 7 | `services/llm_task_executor.py` |
| 8 | `services/usage_service.py` |
| 9 | `services/mcp/mcp_tool_loop.py` |
| 10 | `services/orchestrator/anchor_validation_service.py` |
| 11 | `services/orchestrator/extraction_schema_factory.py` |
| 12 | `services/orchestrator/strategies/logic.py` |
| 13 | `services/orchestrator/strategies/llm_execution/chunk_worker.py` |
| 14 | `api/routers/iam/organizations.py` |

**Suorituskomennot:**

```powershell
uv run python scripts/night_shift_hardener.py backend_v2/hooks
uv run python scripts/night_shift_hardener.py backend_v2/services
uv run python scripts/night_shift_hardener.py backend_v2/worker.py
uv run python scripts/night_shift_hardener.py backend_v2/api/routers/iam/organizations.py
```

**Verifiointitarkistus Phase 3:n jälkeen:** Sama kuin Phase 1 + täysi regressiotestaus.

---

### Phase 4: Lopputarkastus & Siivous

1. Varmista, ettei yhtään `_needs_review.py` -tiedostoa ole jäljellä:
   ```powershell
   Get-ChildItem -Path backend_v2 -Recurse -Filter "*_needs_review.py"
   ```

2. Tarkista `tmp/night_shift_state.json` — kaikki 41 tiedostoa → `DONE`:
   ```powershell
   uv run python -c "import json; d=json.load(open('tmp/night_shift_state.json')); failed=[k for k,v in d.items() if v!='DONE']; print(f'Remaining failures: {len(failed)}'); [print(f'  - {f}') for f in failed]"
   ```

3. Täysi regressiotestaus:
   ```powershell
   uv run pytest backend_v2/tests -v --tb=short
   ```

4. Git diff -laajuuden tarkistus ja commit:
   ```powershell
   git diff --stat
   git add -A
   git commit -m "EPIC-69: Night Shift FAILED_VERIFICATION remediation complete (41 files)"
   ```

## 6. Suoritusmoodi-viite

| Lippu | Toiminta | Passit | Kohdistus |
|---|---|---|---|
| `--resume-failed` | Lukee `_needs_review.py`, mikrokorjaa | Vain Pass 3 | Kaikki review-tiedostot |
| `--force` | Ajaa alkuperäisestä koodista, ohittaa DONE-tilan | Pass 1, 2, 3 | Kohteen kaikki `.py` |
| *(ei lippua)* | Inkrementaalinen, ohittaa DONE-tiedostot | Pass 1, 2, 3 | FAILED-tilaiset |
| `--git` | Vain git-muuttuneet tiedostot | Pass 1, 2, 3 | `git diff` + `git status` |

> **Suositus**: Aja hakemistokohtaisesti **ilman** `--force` -lippua. Tällöin hardener lukee alkuperäiset `.py`-tiedostot (ei review-versioita), ajaa kaikki 3 passia, mutta ohittaa automaattisesti jo `DONE`-tilaiset tiedostot.

## 7. Zero-Compromise Pledges

- **Atomic Rollback**: Git stash ennen jokaista vaihetta. Mikään muutos ei ole peruuttamaton.
- **Fail-Fast**: Jokainen tiedosto käy läpi AST Parity Check, Schema Freeze Guard, Adversarial Judge ja Quality Gate (MyPy+Ruff+Bandit+pytest).
- **Päivitetty Rule 47**: `dynamic_translation_mandate` estää sokeaa ehtolauseiden poistamista, vaatien dynaamisen käännöksen.
- **Ei manuaalisia korjauksia**: Kaikki muutokset tulevat automatiikan kautta. Manuaalinen interventio vain jos hardener tuottaa toistuvasti `FAILED_VERIFICATION`.
