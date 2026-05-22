# Phase 2: Prompt Compiler and Scoring Pipeline Integration

## 1. Yhteenveto
Tässä vaiheessa integroidaan uusi `allow_contextual_override` -kenttä osaksi promptigeneraattoria (Prompt Compiler), jotta LLM ymmärtää säännöt joissa ohitus on sallittu, sekä päivitetään pisteytyskoukku (Scoring Hook) lukemaan ja välittämään tämän tiedon deterministiselle sääntömoottorille.

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py) - Päivitetään LLM-ohjeistuksen rakentaja.
* [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py) - Päivitetään `atom_mapping` ja evaluation-looppi.

### B. Lukuoikeus (Context - Read-Only)
* [01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md) - Taustajärjestelmän arkkitehtuurisäännöt.
* [05_llm_architecture.md](file:///c:/src/quorum/.agents/rules/05_llm_architecture.md) - Prompt-invarianteet ja caching-strategia.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: Prompt Compilerin ohjeistuksen laajennus
* **Tiedosto**: `backend_v2/services/orchestrator/prompt_compiler.py`
* **Tehtävä**: Muokkaa XML-rubriikkien rakentajaa siten, että jos `assertion.allow_contextual_override` on `True`, lisätään säännön perään LLM-ohjeistus:
  `[CONTEXTUAL OVERRIDE ALLOWED] If the assertion's criteria are satisfied semantically or contextually across the text but no single exact verbatim quote can be isolated, you MUST: 1) Set contextual_override = true. 2) Provide a detailed explanation in semantic_reasoning. 3) You may return null or an empty string for exact_quote. Do NOT hallucinate a quote. Only use this override if a direct literal quote is physically absent.`
* **Arkkitehtuurisääntö**: Prompt-rakenteen tulee pysyä 100-prosenttisesti staattisena suhteessa samoihin syötteisiin, jotta promptin välimuisti (caching) toimii optimaalisesti ja säästää kustannuksia.
* **Source**: Epic 59, Section 4.B.

### Milestone 2: Pisteytyskoukun (Scoring Hook) kartoituksen laajennus
* **Tiedosto**: `backend_v2/hooks/scoring.py`
* **Tehtävä**: Päivitä `atom_mapping`-sanasto ottamaan kuudentena kenttänä mukaan `tda.allow_contextual_override` -arvo.
* **Arkkitehtuurisääntö**: Ei naked dicts -rakenteita tai implicit duck typingia. Kaikki arvot kartoitetaan suoraan skeemasta.
* **Source**: Epic 59, Section 4.C.

### Milestone 3: Sääntöjen deterministinen evaluointi
* **Tiedosto**: `backend_v2/hooks/scoring.py`
* **Tehtävä**: Puretaan evaluation-loopissa `allow_override` -kenttä ja välitetään se parametrina `calculate_rule_satisfied` -kutsulle.
* **Source**: Epic 59, Section 4.C.

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattiset testit (Pytest)
Aja prompt compilerin ja pisteytyskoukun testit varmistaaksesi ettei mikään nykyinen arviointi rikkoudu:
```powershell
uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py -v
uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -v
```

### B. Staattinen analyysi ja laatuportit (Quality Gates)
Varmista, ettei tyypitys rikkoudu ja koodi noudattaa Phase 9 Ruff-standardeja:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py
uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py
```

---

## 5. Istunnon Handover (Session Handover)

> [!NOTE]
> Kun tämä vaihe on valmis ja testit menevät läpi, päivitä tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` asettamalla tämä vaihe tilaan `[x]`.

Aloita seuraava vaihe ajamalla:
```powershell
/tier5-resume --target docs/epic/tasks_EPIC_59/phase3_seed_migration.md
```
