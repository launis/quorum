# EPIC: Step Template vs Workflow StepRule — Single Source of Truth Refactoring

**STATUS:** Draft / Planning Phase  
**TIER:** Tier 1 (Epic Planner)  
**CONTEXT:** Quorum V3 Architecture (Python Backend V2 + Flutter Client V2)  
**LAST UPDATED:** 2026-03-25

---

## 📌 1. Objective

Step Template (`Step`) ja Workflow StepRule (`StepRule`) jakavat kolme kenttää: `pre_hooks`, `post_hooks` ja `allowed_mcp_tools`. Nämä päällekkäisyydet rikkovat Single Source of Truth (SSoT) -periaatetta ja luovat piilotettuja merge-sääntöjä jotka ovat epäintuitiivisia, testaamattomia ja vaikeasti debugattavia.

**Tavoite:** Poistaa päällekkäisyydet kokonaan ja luoda selkeä, yksiselitteinen vastuujako:

- **Step Template = "Kuka tämä agentti ON"** (identiteetti, kyvykkyys, käyttäytyminen)
- **Workflow StepRule = "Miten tämä agentti SIJOITTUU DAG:iin"** (topologia, datavirta, resurssi)

---

## 🔬 2. Nykytila-analyysi

### 2.1. Pydantic-mallit

**Step Template** ([v2_core.py:348-378](file:///c:/src/quorum/backend_v2/models/v2_core.py#L348-L378)):

| Kenttä | Tyyppi | Tarkoitus |
|--------|--------|-----------|
| `id`, `slug`, `name`, `description` | Identiteetti | Agentin nimi ja kuvaus |
| `type` | `"llm"` / `"logic"` | Suoritustapa |
| `hook` | `str?` | Logic-stepin Python-funktio |
| `prompt_blocks` | `list[str]` | LLM-promptin rakennuspalikat |
| **`pre_hooks`** | `list[str]` | ⚠️ DUPLIKAATTI |
| **`post_hooks`** | `list[str]` | ⚠️ DUPLIKAATTI |
| `safety` | `"safe"` / `"unsafe"` | MCP-turvaluokitus |
| **`allowed_mcp_tools`** | `list[str]` | ⚠️ DUPLIKAATTI |

**StepRule** ([v2_core.py:402-429](file:///c:/src/quorum/backend_v2/models/v2_core.py#L402-L429)):

| Kenttä | Tyyppi | Tarkoitus |
|--------|--------|-----------|
| `id` | Identiteetti | DAG-noden tunniste |
| `task_blueprint` | `str` | Viittaus Step Template:iin |
| `depends_on` | `list[str]` | DAG-riippuvuudet |
| `input_mappings` | `dict` | Semanttinen reititys |
| `model_strategy` | `str?` | LLM-mallistrategia (fast/deep) |
| **`pre_hooks`** | `list[str]` | ⚠️ DUPLIKAATTI |
| **`post_hooks`** | `list[str]` | ⚠️ DUPLIKAATTI |
| **`allowed_mcp_tools`** | `list[str]` | ⚠️ DUPLIKAATTI |

### 2.2. Merge-logiikka DAG executorissa

Kolme duplikaattikenttää resoloidaan **eri tavalla** — tämä on suurin ongelma:

**Hookit** ([dag_executor.py:184](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py#L184)):
```python
combined_pre_hooks = list(dict.fromkeys(step_obj.pre_hooks + step.pre_hooks))
```
→ **Additiivinen merge**: molemmat yhdistetään, duplikaatit poistetaan. Template ensin, steprule lisää perään.

**MCP Tools** ([dag_executor.py:257](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py#L257)):
```python
effective_mcp_tools = step.allowed_mcp_tools or step_obj.allowed_mcp_tools
```
→ **Or-fallback**: steprule voittaa jos ei-tyhjä, muuten template. **Ei voi deaktivoida** template:n MCP:tä (tyhjä lista on falsy → putoaa template:iin).

### 2.3. Ristiriidat

| Skenaario | Hookit | MCP |
|-----------|--------|-----|
| Template `[A]`, Steprule `[B]` | `[A, B]` (yhdistys) | `[B]` (steprule voittaa) |
| Template `[A]`, Steprule `[]` | `[A]` (template jää) | `[A]` (template fallback) |
| Template `[]`, Steprule `[B]` | `[B]` (steprule lisää) | `[B]` (steprule voittaa) |
| Template `[A]`, Halutaan deaktivoida | ❌ Ei mahdollista | ❌ Ei mahdollista |

> [!WARNING]
> Kaksi eri merge-strategiaa samoille kentätyypeille samassa executorissa on arkkitehtuurivelkaa joka tuottaa ennakoimattomia bugiluokkia.

### 2.4. Admin Studio -UI ongelma

- MCP toggle on **workflow builder** -näytössä ([workflow_builder_view.dart:947-963](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/workflow_builder_view.dart#L947-L963))
- Se muokkaa **StepRule:a** (DAG-node), **ei** Step Template:a
- Tallennus menee workflown kautta → step template:n `allowed_mcp_tools` ei päivity
- Tänään (2026-03-24) todistettiin: toggle oli ON mutta `db_v2.json` steps-taulussa arvo oli `[]`

---

## 🎯 3. Tavoitearkkitehtuuri

### 3.1. Selkeä vastuujako

```
┌─────────────────────────────────────────┐
│         Step Template (steps-taulu)     │
│  "KUKA tämä agentti ON"                │
│                                         │
│  ▸ identiteetti  (id, name, slug, desc) │
│  ▸ tyyppi        (llm / logic)          │
│  ▸ kyvykkyys     (prompt_blocks)        │
│  ▸ käyttäytyminen(pre_hooks, post_hooks)│
│  ▸ turvallisuus  (safety)               │
│  ▸ työkalut      (allowed_mcp_tools)    │
└────────────┬────────────────────────────┘
             │ task_blueprint viittaus
             ▼
┌─────────────────────────────────────────┐
│      Workflow StepRule (workflow DAG)    │
│  "MITEN agentti SIJOITTUU tähän DAG:iin"│
│                                         │
│  ▸ topologia     (depends_on)           │
│  ▸ datavirta     (input_mappings)       │
│  ▸ resurssi      (model_strategy)       │
│  ▸ [EI hookeja, EI MCP:tä]             │
└─────────────────────────────────────────┘
```

### 3.2. Puhdas StepRule

```python
class StepRule(V2CoreBase):
    id: str
    task_blueprint: str         # → Step Template
    depends_on: list[str]       # DAG topologia
    input_mappings: dict        # Semanttinen reititys
    model_strategy: str | None  # LLM-mallistrategia
    # EI MUUTA. Kaikki käyttäytyminen tulee Step Templatesta.
```

### 3.3. DAG Executor — Ei merge-logiikkaa

```python
# ENNEN (epäselvä merge):
combined_pre_hooks = list(dict.fromkeys(step_obj.pre_hooks + step.pre_hooks))
effective_mcp_tools = step.allowed_mcp_tools or step_obj.allowed_mcp_tools

# JÄLKEEN (yksi lähde):
pre_hooks = step_obj.pre_hooks     # Vain Step Template
mcp_tools = step_obj.allowed_mcp_tools  # Vain Step Template
```

---

## 🏗️ 4. Execution Milestones

### Phase 1: Analyysi ja vaikutusarviointi
- [ ] Kartoita jokainen `seed_data.json` step + steprule jossa hookit/MCP ovat steprulessa
- [ ] Listaa kaikki backend-koodipaikat jotka lukevat `step.pre_hooks` / `step.post_hooks` / `step.allowed_mcp_tools` (StepRule:sta)
- [ ] Tarkista onko yhtään workflowia jossa steprule lisää hookeja joita template:ssa ei ole

### Phase 2: Backend-mallit ja executor
- [ ] Poista `pre_hooks`, `post_hooks`, `allowed_mcp_tools` `StepRule`:sta (`v2_core.py`)
- [ ] Päivitä DAG executor: poista merge-logiikka, lue hookit ja MCP vain `step_obj`:stä (Step Template)
- [ ] Päivitä DAG compiler / validator

### Phase 3: Seed Data
- [ ] Siirrä kaikki steprule-tason hookit step templateihin (jos niitä on)
- [ ] Poista `pre_hooks`, `post_hooks`, `allowed_mcp_tools` kaikista stepruleista `seed_data.json`:ssa
- [ ] Aja seed + parity check

### Phase 4: Frontend (Admin Studio)
- [ ] Siirrä MCP toggle workflow builderista → Step editor -näyttöön
- [ ] Poista `allowed_mcp_tools` workflown steprule JSON payloadista
- [ ] Varmista, että Step Template PUT tallentaa `allowed_mcp_tools` oikein kantaan

### Phase 5: Testit ja validointi
- [ ] Päivitä `test_blueprint_transformer.py` ja DAG-testit
- [ ] End-to-end: aja workflow MCP:n kanssa → varmista Fact Checker käyttää Tavilyä
- [ ] End-to-end: aja workflow ilman MCP:tä → varmista step ilman MCP:tä toimii normaalisti

---

## 🚨 5. Banned Patterns

- **Ei merge-logiikkaa:** Kenttä tulee YHDESTÄ paikasta. Ei `or`, ei `+`, ei `dict.fromkeys`.
- **Ei hiljaista fallbackia:** Jos Step Template:ssa ei ole hookia, sitä EI ajeta. Ei haeta "varalle" muualta.
- **Ei duplikaattikenttiä:** Sama konsepti saa esiintyä vain yhdessä mallissa.
- **Workflow ei voi muuttaa agentin luonnetta:** StepRule ei voi lisätä tai poistaa kyvykkyyksiä (hooks/MCP). Se voi vain valita minkä mallin käyttää ja mistä data tulee.

---

## 📊 6. Riskianalyysi

| Riski | Todennäköisyys | Vaikutus | Mitigaatio |
|-------|:---:|:---:|---|
| Jokin steprule lisää kriittisen hookin jota template:ssa ei ole | Matala | Korkea | Phase 1 kartoitus paljastaa |
| Frontend ei tallenna Step Template:n MCP:tä oikein | Kohtalainen | Korkea | Phase 4 testaa PUT-endpointin |
| Kolmannen osapuolen workflow rikkoutuu | Ei sovellettavissa | - | Yksi workflow, yksi admin |

---

## 💡 7. Tulevaisuuden joustavuus

Jos joskus tarvitaan per-workflow override (esim. "tässä workflowssa Fact Checker EI käytä hakua"), se toteutetaan **eksplisiittisenä feature flagilla**, ei piilotettuna merge-logiikkana:

```python
class StepRule(V2CoreBase):
    ...
    overrides: StepOverrides | None = None  # Eksplisiittinen, ei hiljainen

class StepOverrides(V2CoreBase):
    disable_mcp: bool = False
    disable_hooks: list[str] = []  # Nimetty deaktivointi
```

Tämä on selkeästi "tietoinen poikkeus", ei "ohjelmoijan huolimattomuus".
