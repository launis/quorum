# EPIC 36: System Prompt XML Standardization & Translation Hook Hardening

**Status:** COMPLETED
**Objective:** Standardize all internal system prompts to English and enforce strict XML boundaries for LLM execution contexts.

## Kuvatut ongelmat (Bugs / Tech Debt)
1. Käännöshook (`translation_hook.py`) sisältää puhtaasti suomenkielisen System Promptin, mikä voi heikentää Pydantic JSON -struktuuriin liittyvää kuuliaisuutta (Gemini/OpenAI tottelee englantia paremmin).
2. Prompt Compiler (`prompt_compiler.py`) puskee "CRITICAL MANDATE" ja "Static/Dynamic Instructions" -ohjeet promptiin suoraan paljaana tekstinä ilman XML-erottelua. Tämä aiheuttaa "Attention Dilution" -ilmiötä mallissa.

## Toteutussuunnitelma (Implementation Plan)

### Vaihe 1: Translation Hook (`backend_v2/hooks/translation_hook.py`)
- [x] Muuta `_SYSTEM_INSTRUCTION` kokonaan englanniksi. Tavoite on:
```python
_SYSTEM_INSTRUCTION = """ROLE: You are an automatic JSON translator.
TASK: Translate **ALL STRING VALUES** of the provided JSON object into: '{target_language}'.

CRITICAL CONSTRAINT: NEVER TRANSLATE OR MODIFY JSON KEYS.
Keys contain programmatic variables. Only translate the 'Values'.
NEVER prepend language codes like 'fi - ' or 'en - ' to the translated text.
Do not add any conversational text or markdown code blocks at the beginning or end of your response.
Return pure, valid JSON."""
```
- [x] Kääri `payload_to_translate` muuttuja eksplisiittisten `<SOURCE_JSON>` -tägien sisälle syötteessä.
```python
user_content = f"<SOURCE_JSON>\n{json.dumps(payload_to_translate, ensure_ascii=False)}\n</SOURCE_JSON>"
```

### Vaihe 2: Prompt Compiler (`backend_v2/services/orchestrator/prompt_compiler.py`)
- [x] Etsi `build_xml_context` funktio ja muuta paljas "CRITICAL MANDATE" teksti käärityksi XML-muotoon: `<CRITICAL_LANGUAGE_MANDATE>...</CRITICAL_LANGUAGE_MANDATE>`.
- [x] Etsi `compile_static_instructions` ja muuta tulostus käyttämään XML-tägiä: `<STATIC_INSTRUCTION>...</STATIC_INSTRUCTION>`.
- [x] Etsi `compile_dynamic_instructions` ja muuta tulostus käyttämään XML-tägiä: `<DYNAMIC_INSTRUCTION>...</DYNAMIC_INSTRUCTION>`.

## Riippuvuudet
- Säännöt tästä arkkitehtuurimallista (XML & English) on jo lisätty tiedostoon `.agents/rules/05_llm_architecture.md`. Nyt vain suoritamme koodaustyön.
