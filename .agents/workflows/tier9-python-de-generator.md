---
description: Tier 9 (Python De-Generator) - Systematically converts legacy XML-based prompts inside Python files into Markdown and fixes corresponding unit tests.
---

### 🟢 TIER 9: PYTHON DE-GENERATOR FORMATTER & ANTI-TDD TRAP
*Usage: Use this workflow to systematically audit and refactor existing Python files that improperly use XML tags for prompts or instructions. This workflow explicitly mandates fixing corresponding unit tests to avoid the Anti-TDD trap.*

# SYSTEM DIRECTIVE

## OBJECTIVE
[MÄÄRITÄ KOHDE TÄHÄN. Esim: "Konvertoi backend_v2/models/prompts/linguistic_directives.py Markdown-muotoon"]

## ROLE
Lead Python Architect & Strict Compliance Enforcer

## CONTEXT RULES
1. **The De-Generator Mandate:** Kaikki tekoälyn ja agenttien ohjaus (myös Pythonin koodin sisään rakennetut f-stringit ja promptit) on pakko kirjoittaa natiivilla Markdown-hierarkialla. XML-tagien käyttö on **EHDOTTOMASTI KIELLETTY**.
2. **Anti-TDD Trap:** Tiedät, että jos muutat Python-tiedoston XML-tulostetta, yksikkötestit *tulevat räjähtämään*. Sinun on siis **aina** korjattava kohdetiedosto JA sitä vastaava `test_*.py` -tiedosto samassa sessiossa.

## EXECUTION PROTOCOL

### Phase 1: File Analysis & Dependency Tracking (Kartoitus)
- Lue komennossa annettu kohdetiedosto (esim. `backend_v2/services/chat_parser.py`).
- Etsi koodista XML-kääreet (esim. `<source_data>`).
- **DEPENDENCY MANDATE:** Et saa olettaa, että testit löytyvät vain yhdestä tiedostosta (esim. `test_chat_parser.py`). Sinun on **EHDOTTOMASTI** käytettävä `grep_search` -työkalua etsiäksesi kaikki tiedostot (koodi ja testit), jotka viittaavat tähän XML-tagiin, sen tuottamaan muuttujaan tai funktioon.
- Esimerkiksi: Jos muutat muuttujaa `LANGUAGE_MANDATE`, etsi mihin kaikkeen se vaikuttaa koko `backend_v2` -kansiossa.
- Suunnittele muutokset (XML -> Markdown) kohdetiedostoon, sen riippuvuuksiin JA kaikkiin löytämiisi testitiedostoihin.
- Päätä vastauksesi: *"Analyysi valmis. Odotan PROCEED-komentoa."*

### Phase 2: Refactoring Code, Docs & Tests (Muunnos)
Kun saat "PROCEED" -komennon:
1. Muuta kohdetiedoston f-stringit ja vakiot puhtaiksi Markdown-otsikoiksi:
   - Esim. `f"<source_data>\n{data}\n</source_data>"` -> `f"## SOURCE DATA\n{data}\n"`
2. **DOCSTRING MANDATE:** Siivoa välittömästi myös tiedoston sisäiset docstringit (dokumentaatio). Poista kaikki viittaukset XML:ään ja korvaa ne termeillä 'Markdown', 'Markdown header' tms.
3. Varmista, ettei koodin varsinainen logiikka tai muuttujien nimet muutu.
4. Siirry kaikkiin löytämiisi olemassa oleviin testitiedostoihin ja päivitä `assert "<xml>"` -väittämät `assert "## MARKDOWN"` -muotoon.
5. **EXACT TEST FILE MANDATE:** Jotta `backend_audit_loop.py` ei kaadu tiedostokohtaisessa ajossa, varmista, että kohteella on **täsmälleen samanniminen testitiedosto** olemassa (esim. jos kohde on `backend_v2/foo/bar.py`, pitää olla olemassa `backend_v2/tests/unit/foo/test_bar.py`). Jos tätä tiedostoa ei ole, **luo se** ja tee siihen vähintään perustesti, jotta laatuportti menee läpi.
6. Tallenna kaikki muutokset.

### Phase 3: The Universal Quality Gate (Testaa ja Varmista)
1. Aja järjestelmän pakollinen laatuportti korjatulle hakemistolle tai tiedostoille `run_command` -työkalulla:
   - `uv run python scripts/backend_audit_loop.py backend_v2/[alipolku_jota_muokkasit] --test`
2. Jos testit epäonnistuvat (esim. unohdit jonkin toisen testitiedoston, joka käytti samaa koodia), korjaa ne välittömästi.
3. Kun The Universal Quality Gate menee puhtaasti (100% Pass) läpi, ilmoita:
   *"Tier 9 Formatter on suorittanut työnsä. Python-tiedosto ja sen testit ovat nyt täysin De-Generator Mandaten mukaisia ja vihreitä."*
