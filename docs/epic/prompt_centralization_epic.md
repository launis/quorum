# EPIC: Global Prompt Centralization (The "Enum" Pattern)

## 1. Tausta ja Ongelma
Tällä hetkellä järjestelmän ydinlogiikkaan (`backend_v2/services/...` ja `backend_v2/hooks/...`) on ripoteltu kovakoodattuna satoja rivejä englanninkielistä proosaa ja LLM-ohjeistuksia. 

Koodista löytyy muun muassa seuraavia upotuksia (Grep-analyysin tulos 18.6.2026):
* `backend_v2/hooks/synthesis.py` (Koko loppuraportin satojen rivien massiivinen prompti)
* `backend_v2/services/orchestrator/localization_compiler.py` ("CRITICAL ARCHITECTURAL RULE: You are a blind micro-evaluator...")
* `backend_v2/services/orchestrator/prompt_compiler.py` ("You are processing map-reduce chunk...")
* `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py` ("You are a highly accurate, structured evaluation assistant.")
* `backend_v2/services/chat_parser.py` ("You are a data-mining expert...")
* `backend_v2/hooks/translation_hook.py` ("ROLE: You are an automatic JSON translator.")

**Miksi tämä on syntiä:** Python-lähdekoodin joukossa asuva proosateksti vaikeuttaa koodin lukemista valtavasti. Kun tekoälyn ohjeistusta (promptia) halutaan "tuunata", kehittäjä joutuu vahingossa koskemaan kriittisten palveluiden suorittavaan koodiin, mikä voi rikkoa järjestelmän. 

## 2. Tavoite
Luoda keskitetty, "Enum-tyyppinen" teksti-vakioiden kirjasto (`backend_v2/llm/prompts/`), jonne **kaikki** koko backendin LLM-ohjetekstit siirretään. Jatkossa yksikään `.py`-tiedosto palvelukerroksessa (services/hooks) ei sisällä englanninkielisiä proosalauseita.

## 3. Suunniteltu Arkkitehtuuri

### A. Tekstivakioiden hakemisto: `backend_v2/llm/prompts/`
Tämä hakemisto toimii järjestelmän ainoana "sanakirjana" tekoälyohjeille. Sieltä löytyy esimerkiksi:
* `synthesis_prompts.py`
* `evaluator_prompts.py`
* `parser_prompts.py`
* `translation_prompts.py`

Näiden tiedostojen sisällä tekstit määritellään puhtaina vakioina (käytännössä kuten Enum, mutta monirivisinä merkkijonoina):

```python
# backend_v2/llm/prompts/evaluator_prompts.py
BLIND_EVALUATOR_SYSTEM_PROMPT = (
    "CRITICAL ARCHITECTURAL RULE: You are a blind micro-evaluator. "
    "You MUST NEVER declare a final score..."
)
```

### B. Miten koodi käyttää näitä
Suorittava koodi (esim. `localization_compiler.py`) muuttuu näin puhtaaksi:
```python
from backend_v2.llm.prompts.evaluator_prompts import BLIND_EVALUATOR_SYSTEM_PROMPT

def build_prompt():
    messages.append({"role": "system", "content": BLIND_EVALUATOR_SYSTEM_PROMPT})
```

## 4. Toteutuksen Askelmerkit (Phased Approach)

Kuten muissakin refaktoroinneissa, tämä toteutetaan askel kerrallaan tiukasti The Universal Quality Gaten alaisuudessa:

1. **Vaihe 1: Infra ja Synthesis**
   * Luodaan `backend_v2/llm/prompts/` -hakemisto.
   * Puretaan `synthesis.py`:n valtava tekstimassa omaan `synthesis_prompts.py` -tiedostoonsa. Varmistetaan `backend_audit_loop.py`:lla, että raporttien laatu ei muuttunut.

2. **Vaihe 2: Orchestrator ja Compilerit**
   * Siivotaan `localization_compiler.py`, `prompt_compiler.py` ja `prompt_factory.py`. Nämä asettuvat esimerkiksi tiedostoon `orchestrator_prompts.py`.

3. **Vaihe 3: Pienet koukut ja parserit**
   * Siirretään `translation_hook.py` ja `chat_parser.py` omiin vakiotiedostoihinsa.

4. **Vaihe 4: Nimeämiskäytännön vahvistaminen**
   * Lopuksi uudelleennimetään `backend_v2/models/prompts/` muotoon `backend_v2/models/llm_schemas/` (tai vastaava), jotta "Prompt" -sana tarkoittaa projektissa enää vain ja ainoastaan raakoja teksti-vakioita.

Tämän Epicin toteuduttua järjestelmän kielimallien ohjaus on täysin eristetty järjestelmän toiminnallisesta logiikasta. Ohjeiden viilaaminen (Prompt Engineering) muuttuu turvalliseksi ja helpoksi asetusarvojen säätämiseksi.
