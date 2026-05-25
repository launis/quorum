# Phase 2: Context Slicing, Decoupled Falsification and Dynamic Routing

## 1. Yhteenveto
Tässä vaiheessa toteutetaan arviointimoottorin ydinintegraatio ja System 2 -tason ohjauslogiikat. Uudistetaan `prompt_compiler.py` pakottamaan tekoäly käyttämään Sentinel-arvoa `"[CONTEXTUAL_OVERRIDE_APPLIED]"` ohitustilanteessa. Toteutetaan `context_builder.py` tiedostoon Spatial Slicing estämään kronomnesia, rakennetaan kaksiportainen Map-Reduce -falsifiointiputki sekä dynaaminen Ensemble Voting korkean entropian sääntöajoryhmille.

---

## 2. Kohdetiedostot (Scope)

### A. Muokattavat tiedostot (Target - Modify)
* [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py) - XML-ohjeistuksen laajentaminen ja Sentinel-ankkurointipyynnön lisäys.
* [context_builder.py](file:///c:/src/quorum/backend_v2/services/orchestrator/context_builder.py) - Spatial Slicing (tekstin fyysinen leikkaus aikajanarajojen mukaan).
* [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py) - Decoupled Falsification (Map-Reduce) ja Ensemble Voting (3 rinnakkaisajoa ja enemmistöäänet) ohjaus.
* [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py) - `atom_mapping`-kartoitus ja työnkulun master-kytkimen (`workflow.enable_contextual_overrides`) laskenta evaluation-loopissa.

### B. Lukuoikeus (Context - Read-Only)
* [01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md) - Python-arkkitehtuurisäännöt.
* [05_llm_architecture.md](file:///c:/src/quorum/.agents/rules/05_llm_architecture.md) - Prompt caching ja LLM-invarianteet.

---

## 3. Toteutuksen Milestonet (Vaiheet)

### Milestone 1: Prompt Compilerin Sentinel-ohjeistus (`prompt_compiler.py`)
* **Tiedosto**: `backend_v2/services/orchestrator/prompt_compiler.py`
* **Tehtävä**: Muokkaa XML-rubriikkien rakentajaa siten, että jos `assertion.allow_contextual_override` on `True`, lisätään säännön perään LLM-ohjeistus, joka kieltää tyhjät/null sitaatit ja pakottaa Sentinel-arvon:
  `[CONTEXTUAL OVERRIDE ALLOWED] If the assertion's criteria are satisfied semantically or contextually across the text but no single exact verbatim quote can be isolated, you MUST: 1) Set contextual_override = true. 2) Provide a detailed explanation in semantic_reasoning with structural references. 3) Set exact_quote to exactly '[CONTEXTUAL_OVERRIDE_APPLIED]'. Do NOT hallucinate a quote. Only use this override if a direct literal quote is physically absent.`
* **Arkkitehtuurisääntö**: Promptin ydinosan on pysyttävä täysin staattisena, ja kaikki säännöt kirjoitetaan englanniksi (System Language).
* **Source**: Epic 59, Section 4.B.

### Milestone 2: Spatial Slicing aikajanan leikkaamiseksi (`context_builder.py`)
* **Tiedosto**: `backend_v2/services/orchestrator/context_builder.py`
* **Tehtävä**: Rakenna spatiaalinen leikkauslogiikka. Jos sääntö tai väite mittaa ajallista kronologiaa (esim. Toulmin-itsensähylkäys tietyssä vaiheessa), leikkaa dokumentin tekstistä asynkronisesti ja fyysisesti irti kaikki myöhempi keskustelu/vaihe ennen kuin se syötetään LLM:lle. Tämä poistaa kronomnesia-virheet (Blind Spot 3).
* **Source**: Epic 59, Section 4.A & B.

### Milestone 3: Decoupled Falsification Map-Reduce -putki (`dag_executor.py`)
* **Tiedosto**: `backend_v2/services/orchestrator/dag_executor.py`
* **Tehtävä**: Toteuta kaksiportainen Map-Reduce -logiikka negatiivisille säännöille (esim. *"X on jätetty pois"* tai *"mitään muuta Y ei muutettu"*). Erota kysely kahdeksi LLM-kutsuksi:
  1. Etsi kaikki positiiviset ilmentymät X (läsnäolo).
  2. Etsi kaikki poikkeukset tai rajoitukset (kielto).
  Suorita lopullinen päättely Boolean-tason Python-logiikalla LLM:n sijaan poistamaan negatiivisen tilan sokeus (Blind Spot 2).
* **Source**: Epic 59, Section 4.A.

### Milestone 4: Dynaaminen Ensemble Voting korkean entropian atomeille (`dag_executor.py`)
* **Tehtävä**: Tunnista suorituksen aikana korkean oskilloinnin atomit (historiallinen Shannonin entropia = 1.000). Jos atom_id kuuluu tähän joukkoon, pakota dynaaminen reititys Ensemble-tilaan: aja sääntö 3 kertaa rinnakkain `asyncio.TaskGroup`-tehtävinä ja tee lopputuomio enemmistöäänestyksen (Majority Vote) perusteella.
* **Source**: Epic 59, Section 4.A.

### Milestone 5: Scoring Hook & Kaksoislukitus (`scoring.py`)
* **Tiedosto**: `backend_v2/hooks/scoring.py`
* **Tehtävä**:
  1. Laajenna `atom_mapping`-sanakirjaa ottamaan mukaan `tda.allow_contextual_override`.
  2. Haetaan työnkulun (`workflow`) master-kytkin `workflow.enable_contextual_overrides` suoritusympäristöstä.
  3. Laske loopissa tehokas ohitusoikeus:
     `effective_allow_override = enable_contextual_overrides and allow_override`
     Välitä tämä arvo kutsulle `calculate_rule_satisfied(..., allow_contextual_override=effective_allow_override)`.
* **Source**: Epic 59, Section 4.C.

---

## 4. Testaus- ja Laatusuunnitelma (Verification Plan)

### A. Automaattiset integraatiotesti (Pytest)
```powershell
uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py -v
uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -v
```

### B. Staattiset laatuportit (Quality Gates)
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py
uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/context_builder.py
```

---

## 5. Istunnon Handover (Session Handover)

> [IMPORTANT]
> Aina onnistuneen työvaiheen ja auditointisilmukan jälkeen suorita kansion tarkka commit:
> `git add backend_v2/services/orchestrator/prompt_compiler.py backend_v2/services/orchestrator/context_builder.py backend_v2/services/orchestrator/dag_executor.py backend_v2/hooks/scoring.py`
> `git commit -m "feat(epic-59): implemented context slicing and decoupled falsification orchestrators"`

Kun tämä vaihe on täysin valmis ja laatuportit ovat vihreänä, merkitse tracker-tiedosto `docs/epic/EPIC_59_Claim_Level_Contextual_Override_Architecture_tracker.md` täytetyksi askeleeksi (`[x]`).

Siirry seuraavaan vaiheeseen ajamalla:
```powershell
/tier5-resume --target docs/epic/tasks_EPIC_59/phase3_seed_migration.md
```
