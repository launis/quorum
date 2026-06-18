# EPIC: Synthesis Hook Refactoring - Extracting Prompts and Separation of Concerns

## 1. Tausta ja Konteksti
`backend_v2/hooks/synthesis.py` (n. 40 KB) on tällä hetkellä Quorumin raskain kielimalli-integraatio. Se vastaa massiivisen loppuraportin (PDF/HTML) sisällön generoimisesta.

**Miksi se on God Object (Syntinen):**
1. **Hardcoded Prompts (Kovakoodatut ohjeet):** Tiedoston sisään on upotettu satoja rivejä raakaa englanninkielistä tekstiä, sääntöjä ja f-string -muotoiluja (esim. ohjeet siitä, miten tekoälyn pitää kirjoittaa). Tämä tekee koodista mahdottoman lukea.
2. **Datan siivooja:** Hook hakee raakaa dataa tietokannasta ja suorittaa itse massiivista Pydantic-objektien karsintaa ja "siivousta" (sanitization), jotta LLM:n konteksti-ikkuna ei räjähdä.
3. **XML-rakentaja:** Tiedosto kasaa käsin valtavia XML-puita lähetettäväksi tekoälylle.
4. **API-kutsuja:** Vastaa OpenAI:n kutsumisesta ja Token-kulujen reitittämisestä eteenpäin.

## 2. Tavoite ja Hakemistopohdinta
Purkaa `synthesis.py` siten, että raaka tekoälyn ohjeteksti (Promptit) eristetään täysin suorittavasta koodista, ja datan muokkaus eriytetään API-kutsusta.

### Käyttäjän ehdotus: `backend_v2/models/prompts/`
Tämä on osittain loistava suunta! Tarkennetaan arkkitehtuuria näin:

**A. `backend_v2/models/prompts/` (Skeemat ja Muuttujat)**
Kuten nykyinen `validation_prompts.py` todistaa, tämä kansio on täydellinen **Pydantic-malleille**, jotka määrittelevät *mitä* muuttujia promptiin syötetään (esim. `SynthesisPromptVariables(BaseModel)`). Näin saamme tiukan tyyppiturvan sille, ettei promptiin vahingossa injektoida "None"-arvoja.

**B. `backend_v2/llm/prompts/` (Varsinaiset tekstiohjeet)**
Itse 500-riviset englanninkieliset tekstiohjeet (esim. "You are an expert analyst...") siirretään tänne puhtaiksi teksti-vakioiksi (esim. `synthesis_system_prompt.py`). **Ehdottomana sääntönä:** Pythonin suorittavan koodin joukossa ei koskaan saa olla kappalekaupalla englanninkielistä proosaa. Näissä vakioissa lepää vain ja ainoastaan tekoälyn kielimalli-ohjeistus.

## 3. Suunnitellut Arkkitehtuurimuutokset (Uudet Komponentit)

### 1. `PromptHydrator` (Datan siivooja)
* **Vastuu:** Hakee raskaat tietokantaoliot (ExecutionRecord) ja karsii niistä kaiken LLM:lle turhan metadatan.
* **Palauttaa:** `backend_v2/models/prompts/synthesis_prompt.py` -tiedostossa määritellyn siistin Pydantic-olion, joka on valmis syötettäväksi prompt-moottorille.

### 2. `TemplateEngine` / `PromptBuilder`
* **Vastuu:** Ottaa vastaan yllä mainitun Pydantic-olion ja injektoi sen muuttujat puhtaisiin teksti-vakioihin (esim. Pythonin f-string tai `.format()`). Vastaa massiivisten XML-rakenteiden muotoilusta ilman, että itse prompt-tekstiä leivotaan koodiin.
* **Palauttaa:** Valmiin, puhtaan tekstistringin tai viestilistan OpenAI:lle lähetettäväksi.

### 3. Jäljelle jäävä `synthesis.py` (Orkestraattori)
Supistuu vain muutamaan kymmeneen riviin:
```python
variables = hydrator.extract_variables(state)
messages = prompt_builder.build_messages(variables, "synthesis_system_prompt.jinja2")
llm_result = await llm_executor.run(messages)
return HookResult(state_delta=llm_result)
```

## 4. Toteutuksen Askelmerkit
1. **Vaihe 1:** Irrotetaan nykyiset kovakoodatut englanninkieliset tekstiplokit sellaisenaan uuteen tiedostoon (esim. `backend_v2/llm/prompts/synthesis_prompts.py` vakiomuuttujiksi).
2. **Vaihe 2:** Luodaan `backend_v2/models/prompts/` -hakemistoon Pydantic-malli sille datalle, joka Synthesis-promptiin injektoidaan.
3. **Vaihe 3:** Eristetään datan siivous (XML-rakentelu) `PromptBuilder` -luokkaan.
4. **Laatuportti:** Tier 2 Python Audit Loop ajetaan jokaisen askeleen jälkeen. Tässä refaktoroinnissa on nollatoleranssi sille, että LLM:lle menevä lopullinen tekstimuoto muuttuisi tavuakaan alkuperäisestä. Se on vain tuotettava eri tiedostojen kautta.
