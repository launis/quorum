# Phase 6: Valmentava Synteesi (XAI & MCP Shift)

## Objective
Kytketään lopullisen tuomion jälkeinen valmentava Synteesi-AI. Se ottaa sisään Pythonin tuottamat kylmät faktat (Score ja puuttuviksi jääneet Atomit) sekä alkuperäisen rubriikin, hakee tarvittaessa MCP-hauilla (Tavily tms) selventävää pedagogista taustaa verkosta ja tuottaa Rubric-aligned CoT menetelmällä asiantuntijamaisen loppuarvioinnin.

## TARGET (Modify)
- `backend_v2/hooks/synthesis.py` tai `text_consolidation_hook` (Laajennetaan Scaffolded CoT ja MCP käsittelyyn)
- `backend_v2/services/blueprint.py` (Varmistetaan Zero-Math konfluenssi raporttiedostoon saakka)

## CONTEXT (Read-Only)
- `backend_v2/models/v2_core.py` 
- `backend_v2/llm/client.py`
- `backend_v2/services/orchestrator/dag_executor.py`

## Architectural Constraints (V2 Sequence)
1. **Dependencies:** Käytetään Arq/Background Worker prosessia (`render_profile_job`), sillä synteesin rakentaminen on asynkroninen prosessi. API-päässä ylläpidetään 202 Accepted.
2. **Native English Generation Mandate:** Synteesi ja laaja kognitio tuotetaan englanniksi, minkä jälkeen se voidaan tarvittaessa kääntää `translation_hook.py` avulla suomeksi vasta lopuksi, välttäen "Intelligence Dropping".

## Design / Implementation specifics
* Järjestetään `input_mappings` tälle Hook-kutsulle toimittamaan alkuperäisen matriisin (Rubric), vesiputouksen loppuscoren, sekä tarkasti listatut hylätyt atomit.
* Promptilla T=0.3 - 0.5 mahdollistaen selityksen luovuuden mutta estäen harhautumisen. 
* Lupa MCP-työkalujen käyttöön (grounding) tilanne-ohjeistuksella.
* Generatiivinen palaute kirjataan Pydantic-mallien PII-maskattuun (`enable_pii_masking=True`) rakenteeseen, taaten "Zero-Math UI" suorituskyky Frontendissä.

## Verification & Quality Gate Plan
* Kirjoitetaan testit varmistaaksemme, että synteesiprompti noudattaa englanninkielistä pakotusta ennen kääntäjää (Native English Mandate).
* Komento: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/synthesis.py --test`
