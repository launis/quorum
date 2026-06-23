# EPIC 83: LLM Schema Validation Healing & Reasoning Trace Simplification

## 1. Tausta ja Ongelman Kuvaus
Järjestelmän monitoroinnin (Tier 6) aikana havaittiin toistuvia `LLMSchemaValidationError` -poikkeuksia erityisesti `gemini-2.5-flash` ja `gemini-2.5-pro` -mallien rinnakkaissuorituksissa. 
Lokien perusteella virheet ilmenevät muotoilulla:
`Invalid JSON: invalid escape at line 3 column 0`

**Juuri-syy (Root Cause):**
Virhe johtuu Pydantic-skeeman kentästä `reasoning_trace` (tai vastaavasta CoT-kentästä, esim. `reasoning_steps`), jonka on määritelty olevan tyyppiä `str`. Promptin ohjeistus kuitenkin kannustaa mallia generoimaan "askeleittaisen" rakenteen. Gemini yrittää täyttää kentän **stringifioidulla JSON-taulukolla** (esim. `"[\n  {\n    \"step\": 1..."`), ja tuottaa vahingossa "literal newline" (`\n`) -merkkejä JSON-merkkijonon sisään. 
Koska raaka JSON ei salli rivinvaihtoja merkkijonon sisällä ilman asianmukaista eskapointia (`\\n`), Pydanticin `model_validate_json` kaatuu välittömästi.

Tämä pakottaa `ChunkWorker`:in kuluttamaan sallitut uudelleenyritykset (Retry), johtaen lopulta `Max schema retries exceeded` -virheeseen ja Graceful Degradation -hylkäykseen (DLQ:hun siirtoon).

## 2. Vaikutukset nykytilassa
- **Suorituskyky ja hinta:** Jokainen virheellinen haku laukaisee uudelleenyrityksen. Esimerkiksi Pro-mallin kohdalla tämä aktivoi 12 sekunnin Pacing-lukon (Wait-and-Poll), mikä pidentää ajon kestoa tarpeettomasti.
- **Käyttöliittymä (SDUI):** XAI Highlights joutuu pahimmillaan käsittelemään ja renderöimään loppukäyttäjälle hankalasti luettavaa raakaa JSON-koodia vapaan selittävän tekstin sijaan.
- **Vakaus:** Vaikka arkkitehtuurin Graceful Degradation estää koko järjestelmän kaatumisen, yksittäisten arviointien hylkääminen laskee kattavuutta.

## 3. Ratkaisuvaihtoehdot ja Suunnitelma

Olemme tunnistaneet kolme mahdollista tasoa ongelman korjaamiseksi:

### Vaihtoehto 1: Pydanticin dynaaminen Pre-Validator (@model_validator)
Jos haluamme jatkaa askeleittaisen JSON-pohdinnan (`[{"step": 1, ...}]`) pyytämistä, voimme lisätä Pydantic-malliin `@model_validator(mode='before')` -korjaajan.
- **Miten se toimii:** Ennen varsinaista validointia Python ottaa merkkijonon kiinni, puhdistaa siitä laittomat `\n` -merkit Regexillä, ja ajaa sille `json.loads()`, muuntaen sen oikeaksi Python-listaksi (tai korjaa merkkijonon muuten kelvolliseksi JSON-arvoksi).
- **Hyödyt:** Pydantic parantaa datan "lennosta" ennen kuin validointi ehtii kaatua. Ei tarvita uudelleenyrityksiä.

### Vaihtoehto 2: Pre-Parsing JSON Sanitizer (Raakatekstin siivous)
Ennen kuin raaka LLM-vastaus annetaan Pydanticin `.model_validate_json()` -funktiolle (tiedostossa `client.py`), raakateksti ajetaan erillisen siivoojan läpi.
- **Toteutus:** Python skannaa merkkijonon (`raw_payload`), etsii lainausmerkkien sisällä olevat kirjaimelliset rivinvaihdot ja korvaa ne eskapoidulla muodolla (`\\n`) ennen JSON-validointia.
- **Hyödyt:** Suojelee kaikkia Pydantic-malleja globaalisti LLM:n tyypillisimmältä JSON-koodausvirheeltä.

### Vaihtoehto 3: Vapaan tekstin salliminen (Schema Simplification) - SUOSITELTU ARKKITEHTUURIVALINTA
Koska nykyisissä Pydantic-malleissa (esim. `StepDTOStrict`) kenttä `reasoning_steps` / `reasoning_trace` on jo määritelty tyypiksi `str`, voimme yksinkertaisesti **poistaa tekoälyltä pakotuksen** käyttää sisäkkäistä JSON-rakennetta sen sisällä.
- **Toteutus:** Päivitetään promptit (esim. `seed_data.json` tai Prompt Compiler) ohjeistamaan: *"Write your reasoning step-by-step as plain free text paragraphs. Do not use JSON arrays for reasoning."*
- **Hyödyt:** Poistaa JSON-escaping -virheet täysin, säilyttää Chain-of-Thought (CoT) kognition hyödyt, ja parantaa frontendin luettavuutta huomattavasti, kun XAI Highlights saa puhdasta tekstiä ruman JSON:in sijaan. Suositeltuin ratkaisu.

## 4. Toimenpiteet (Execution Steps)
1. Päivitetään Tier 1/2 mukaisesti `backend_v2/models/prompts/` tai `seed_data.json` poistamaan JSON-pakotukset CoT-kentistä.
2. (Valinnainen) Implementoidaan kevyt regex-puhdistaja `LLMClient`-luokkaan varasuojaksi.
3. Ajetaan `pytest` ja varmistetaan, ettei `evaluations` putoa.
4. Varmistetaan SDUI-renderöinnin muutos, kun data muuttuu JSON:ista raakatekstiksi.

*(Tätä Epiciä päivitetään, jos käynnissä olevan ajon seurannassa paljastuu uusia variaatioita näistä schema-virheistä).*
