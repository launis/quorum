# Phase 4: Sokea Tiedonerottelu (Eristetty Runtime-AI)

## Objective
Suoritetaan täysin sokea asiantuntijasyötteen skannaus Runtimessä tekoälyllä, jolta on poistettu pääsy verkkoon ja jonka lämpötila on lukittu T=0.0. LLM joutuu vain prosessoimaan riisutun 75 satunnaisen väitteen listan mekaanisesti.

## TARGET (Modify)
- `backend_v2/seed/seed_data.json` (Luodaan uusi `model_strategy` Model Registryyn sokealla konfiguraatiolla, T=0.0)
- `backend_v2/services/orchestrator/prompt_compiler.py` (Sokean PromptBlock instruktion rakentaminen System-rooliin Micro-CoT ohjeilla ilman kontekstivihjeitä)

## CONTEXT (Read-Only)
- `backend_v2/models/v2_core.py` 
- `backend_v2/llm/client.py`
- `backend_v2/llm/schema_builder.py` 

## Architectural Constraints (V2 Sequence)
1. **Dependencies:** Promptit täytyy jakaa globaaleilla Two-Tier säännöillä. Asiantuntijasäännöt menossa User-rooliin ja koneellinen ohjeistus (Micro-CoT) System-rooliin.
2. **Zero-Math:** Tämä komponentti EI LISÄÄ pisteitä eikä tee arvioita osaamisesta. Se tuottaa pelkästään Boolen True/False osumat listattuna Array-rakenteeseen JSON Structured Outputs avulla.
3. **Pydantic V2:** Structured Output takaa, että LLM-vastaus on muotoa: `List[AtomResponse]` jossa `AtomResponse = BaseModel(quote: str, reasoning: str, boolean: bool)`.

## Design / Implementation specifics
* "No-MCP Mandate": Varmistetaan `Allowed_tools` tyhjäksi rekisterissä tälle työnkulun LLM-strategialle.
* Structured Output on pakko olla voimassa (`run_structured_task()`), regex/JSON.loads ei sallittu.
* "Duck-Typing Token Shield" käytössä, jottei koko taustateksti tukehduta tokenlimittejä, vaan syötetään vain aito arvioitava alkuperäisdokumentti.

## Verification & Quality Gate Plan
* Varmennus, että LLM Client generoi pyydetyn Strict JSON Output rakenteen ja hylkää MCP työkalupyynnöt. Pydantic Validator karsii virheet.
* Komento: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --openapi` ja `--test`.
