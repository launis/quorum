# Hooks System Documentation

## Yleiskatsaus (Overview)

**Hookit** ovat deterministisiä Python-funktioita, jotka suoritetaan workflow-agenttien yhteydessä. Ne mahdollistavat:

1. **Syötteiden esikäsittelyn** (Pre-hooks) - Ennen agentin LLM-kutsua
2. **Tulosten jälkikäsittelyn** (Post-hooks) - Agentin suorituksen jälkeen
3. **Deterministisen logiikan** - Ei satunnaisuutta, toistettavat tulokset
4. **Ulkoisten palveluiden integraation** - Google Search, tietokannat, jne.

```
┌─────────────┐    ┌────────────┐    ┌─────────────┐    ┌─────────────┐
│  Pre-Hooks  │ -> │   Agent    │ -> │  Post-Hooks │ -> │   Output    │
│ (sanitize,  │    │  (LLM)     │    │  (scoring,  │    │   (state)   │
│  metrics)   │    │            │    │   report)   │    │             │
└─────────────┘    └────────────┘    └─────────────┘    └─────────────┘
```

> [!IMPORTANT]
> **Yksi mekanismi (Jan 2026)**: Hookit suoritetaan **ainoastaan** HOOK_MAPPING:n kautta.
> Vanha mekanismi (agenttiluokkien metodit) on poistettu. 
> Kaikki hookit määritellään `seed_data.json`:ssa ja resolvoidaan `runner.py`:n `_execute_hook()`-metodissa.

---

## Arkkitehtuuri

### Hook-rekisteri (HOOK_MAPPING)

Kaikki hookit on rekisteröity keskitetysti tiedostossa `backend/core/registry.py`:

```python
HOOK_MAPPING = {
    "generate_report": ("backend.hooks.reporting", "generate_report"),
    "verify_structure": ("backend.hooks.validation", "verify_structure"),
    "execute_google_search": ("backend.hooks.search", "execute_google_search"),
    "sanitize_text": ("backend.hooks.security", "sanitize_text_hook"),
    "check_banned_phrases": ("backend.hooks.security", "check_banned_phrases_hook"),
    "calculate_text_metrics": ("backend.hooks.metrics", "calculate_text_metrics_hook"),
    "calculate_control_ratio": ("backend.hooks.metrics", "calculate_control_ratio_hook"),
    "detect_performative_patterns": ("backend.hooks.linguistics", "detect_performative_patterns"),
    "apply_scoring_logic": ("backend.hooks.scoring", "apply_scoring_logic"),
    "retrieve_precedent": ("backend.hooks.archival", "retrieve_precedent"),
    "generate_bibliography": ("backend.hooks.references", "generate_bibliography_hook"),
}
```

### Konfigurointi (seed_data.json)

Hookit aktivoidaan workflow-stepeille `config`-kentässä:

```json
{
    "id": "step_judge",
    "task_key": "judge",
    "config": {
        "pre_hooks": [],
        "post_hooks": ["apply_scoring_logic"]
    }
}
```

---

## Hookit yksityiskohtaisesti

### 1. Turvallisuus (Security)

#### `sanitize_text` / `sanitize_text_hook`
**Tiedosto:** `backend/hooks/security.py`  
**Tyyppi:** Pre-hook  
**Agentti:** Guard

**Toiminta:**
- Tunnistaa ja poistaa PII-tiedot (Personal Identifiable Information)
- Regex-pohjaiset tunnistimet:
  - Sähköpostit
  - Suomalaiset puhelinnumerot
  - HETU (henkilötunnus)
  - Luottokorttinumerot
  - IP-osoitteet

**Tallentaa:**
- `aux_data["sanitized_inputs"]` - Puhdistetut tekstit
- `aux_data["pii_threats_detected"]` - Lista havaituista uhista

---

#### `check_banned_phrases` / `check_banned_phrases_hook`
**Tiedosto:** `backend/hooks/security.py`  
**Tyyppi:** Pre-hook  
**Agentti:** Guard

**Toiminta:**
- Skannaa syötteet kiellettyjen fraasien varalta
- Oletuslista sisältää jailbreak-yritysten tunnistamisen:
  - "jailbreak", "ignore instructions", "pretend you are", jne.

**Tallentaa:**
- `aux_data["banned_phrases_detected"]` - Lista havaituista fraseista
- `aux_data["security_threat"]` - Boolean lippu

---

### 2. Metriikka (Metrics)

#### `calculate_text_metrics` / `calculate_text_metrics_hook`
**Tiedosto:** `backend/hooks/metrics.py`  
**Tyyppi:** Pre-hook  
**Agentti:** Profiler

**Toiminta:**
- Laskee objektiiviset tekstimetriikkat:
  - `word_count` - Sanojen määrä
  - `sentence_count` - Lauseiden määrä
  - `avg_sentence_length` - Keskimääräinen lausepituus
  - `lexical_diversity` - Sanaston rikkaus (0-1)
  - `capitalization_ratio` - Isojen kirjainten osuus

**Tallentaa:**
- `aux_data["profiler_metrics"]` - Metriikkaobjekti

---

#### `calculate_control_ratio` / `calculate_control_ratio_hook`
**Tiedosto:** `backend/hooks/metrics.py`  
**Tyyppi:** Pre-hook  
**Agentti:** Interaction

**Toiminta:**
- Analysoi keskusteluhistorian käyttäjän vs. AI:n osuudet
- Tunnistaa headerit: "User:", "AI:", "Human:", jne.
- Laskee käyttäjän merkkien osuuden kokonaismäärästä

**Tallentaa:**
- `aux_data["input_control_ratio"]` - Float (0.0 = puhdas AI, 1.0 = puhdas käyttäjä)

**Käyttö raportissa:**
- Näytetään käyttäjän aktiivisuusaste prosentteina
- Luokitellaan: Matkustaja (<30%), Kuski (>70%), Tasainen (30-70%)

---

### 3. Validointi (Validation)

#### `verify_structure`
**Tiedosto:** `backend/hooks/validation.py`  
**Tyyppi:** Pre-hook  
**Agentti:** Analyst

**Toiminta:**
- Tarkistaa syötteiden minimipituudet (100 merkkiä)
- Generoi varoitukset liian lyhyistä syötteistä

**Tallentaa:**
- `aux_data["structural_warnings"]` - Lista varoituksista

**Käyttö raportissa:**
- Näytetään **"Rakenteelliset Varoitukset"** -osiossa (osio 6)

---

### 4. Kielianalyysi (Linguistics)

#### `detect_performative_patterns`
**Tiedosto:** `backend/hooks/linguistics.py`  
**Tyyppi:** Pre-hook  
**Agentti:** Detector (Performativity)

**Toiminta:**
- Havaitsee AI-generoidulle tekstille tyypillisiä kliseitä:
  - "delve into", "tapestry", "comprehensive overview"
  - "testament to", "pivotal role", "landscape of", jne.

**Tallentaa:**
- `aux_data["performative_patterns_detected"]` - JSON-lista havainnoista

**Käyttö raportissa:**
- Näytetään "Pre-Mortem Signals" osiossa

---

### 5. Haku (Search)

#### `execute_google_search`
**Tiedosto:** `backend/hooks/search.py`  
**Tyyppi:** Pre-hook  
**Agentti:** Overseer

**Toiminta:**
- Suorittaa Google Custom Search API -hakuja
- Hakukyselyt tulevat Analyst-agentin hypoteeseista (`hakusana_ehdotus`)
- Maksimissaan 3 hakua, 3 tulosta per haku

**Vaatii:**
- `GOOGLE_SEARCH_API_KEY` ympäristömuuttuja
- `GOOGLE_SEARCH_CX` ympäristömuuttuja

**Tallentaa:**
- `aux_data["google_search_results"]` - JSON hakutuloksista

**Käyttö raportissa:**
- Näytetään **"Faktantarkistuksen Lähteet"** -osiossa (osio 8)

---

### 6. Arkistointi (Archival)

#### `retrieve_precedent`
**Tiedosto:** `backend/hooks/archival.py`  
**Tyyppi:** Pre-hook (async)  
**Agentti:** Archivist

**Toiminta:**
- Hakee aiempien suoritusten tuloksia tietokannasta
- Muodostaa "ennakkotapaukset" (case law) -kontekstin
- Käyttää viimeisiä 3-5 valmistunutta suoritusta

**Tallentaa:**
- `aux_data["archivist_precedents"]` - Tekstiyhteenveto aiemmista tapauksista

**Käyttö raportissa:**
- Näytetään **"Historiallinen Konteksti (Ennakkotapaukset)"** -osiossa (osio 7)

---

### 7. Pisteytys (Scoring)

#### `apply_scoring_logic`
**Tiedosto:** `backend/hooks/scoring.py`  
**Tyyppi:** Post-hook  
**Agentti:** Judge

**Toiminta:**
- Soveltaa deterministisiä rangaistuksia:
  1. **Turvallisuusuhka** → Kaikki pisteet = 1
  2. **Post-hoc rationalisointi** → Maksimipisteet = 2
- Laskee keskiarvon kaikista arviointikategorioista

**Tallentaa:**
- `aux_data["score_summary"]` - Yhteenvetoteksti
- `aux_data["calculated_average"]` - Keskiarvo (float)
- `aux_data["penalties_applied"]` - Lista rangaistuksista

**Käyttö raportissa:**
- Näytetään "Rangaistukset" -osiossa
- Keskiarvo näkyy pisteytystaulukossa

---

### 8. Viitteet (References)

#### `generate_bibliography` / `generate_bibliography_hook`
**Tiedosto:** `backend/hooks/references.py`  
**Tyyppi:** Post-hook  
**Agentti:** Coach

**Toiminta:**
- Skannaa tekstistä viittauksia tieteellisiin lähteisiin
- Käyttää `ReferenceManager`-palvelua
- Generoi lähdeluettelon

**Tallentaa:**
- `aux_data["bibliography"]` - Lista viitteistä

---

### 9. Raportointi (Reporting)

#### `generate_report`
**Tiedosto:** `backend/hooks/reporting.py`  
**Tyyppi:** Post-hook  
**Agentti:** XAI Reporter

**Toiminta:**
- Kokoaa kaikki workflow-tulokset yhteen
- Renderöi Jinja2-mallipohjan (`report_template.jinja2`)
- Tuottaa lopullisen XAI-raportin Markdown-muodossa

**Kokoaa tiedot:**
- Pisteet kaikilta arviointikategorioilta
- Eettiset havainnot (Overseer)
- Valmennussuunnitelma (Coach)
- Performatiivisuussignaalit (Detector)
- Rangaistukset (Scoring hook)
- Vuorovaikutusanalyysi (Interaction hook)

**Tallentaa:**
- `state.xai_report_formatted` - Valmis Markdown-raportti

---

## Hook-taulukko

| Hook | Tiedosto | Pre/Post | Agentti | Tallentaa |
|------|----------|----------|---------|-----------|
| `sanitize_text` | security.py | Pre | Guard | `sanitized_inputs`, `pii_threats_detected` |
| `check_banned_phrases` | security.py | Pre | Guard | `banned_phrases_detected`, `security_threat` |
| `calculate_text_metrics` | metrics.py | Pre | Profiler | `profiler_metrics` |
| `calculate_control_ratio` | metrics.py | Pre | Interaction | `input_control_ratio` |
| `verify_structure` | validation.py | Pre | Analyst | `structural_warnings` |
| `detect_performative_patterns` | linguistics.py | Pre | Detector | `performative_patterns_detected` |
| `execute_google_search` | search.py | Pre | Overseer | `google_search_results` |
| `retrieve_precedent` | archival.py | Pre | Archivist | `archivist_precedents` |
| `apply_scoring_logic` | scoring.py | Post | Judge | `score_summary`, `calculated_average`, `penalties_applied` |
| `generate_bibliography` | references.py | Post | Coach | `bibliography` |
| `generate_report` | reporting.py | Post | XAI | `xai_report_formatted` |

---

## Oman hookin luominen

### 1. Luo hook-funktio

```python
# backend/hooks/my_hook.py
from backend.models.state import WorkflowState

def my_custom_hook(state: WorkflowState) -> WorkflowState:
    """Esimerkki hookista."""
    # Lue syötteet
    text = state.inputs.history_text or ""
    
    # Tee jotain deterministä
    result = len(text.split())
    
    # Tallenna tulokset
    state.aux_data["my_hook_result"] = result
    
    return state
```

### 2. Rekisteröi HOOK_MAPPING:iin

```python
# backend/core/registry.py
HOOK_MAPPING = {
    # ... muut hookit ...
    "my_custom_hook": ("backend.hooks.my_hook", "my_custom_hook"),
}
```

### 3. Aktivoi seed_data.json:ssa

```json
{
    "id": "step_my_agent",
    "config": {
        "pre_hooks": ["my_custom_hook"],
        "post_hooks": []
    }
}
```

---

## Testaus

Hookien testit löytyvät tiedostosta `tests/test_hooks_comprehensive.py`. Testit kattavat:

1. **Signatuurit** - Kaikki wrapper-funktiot ovat käytettävissä
2. **Validit syötteet** - Normaalit käyttötapaukset
3. **Reunatapaukset** - Tyhjät syötteet, puuttuvat kentät
4. **Virheenkäsittely** - None-tilanteet, puuttuvat attribuutit
5. **Integraatio** - HOOK_MAPPING sisältää kaikki hookit

Testien ajo:
```bash
python -m pytest tests/test_hooks_comprehensive.py -v
```
