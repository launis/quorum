# EPIC 83: LLM Schema Validation Healing & Reasoning Trace Simplification

## 1. Tausta ja Ongelman Kuvaus

Järjestelmän monitoroinnin (Tier 6) aikana havaittiin toistuvia `LLMSchemaValidationError` -poikkeuksia `gemini-2.5-flash` ja `gemini-2.5-pro` -mallien rinnakkaissuorituksissa. Lokien perusteella virheet ilmenevät muotoilulla:

```
Invalid JSON: invalid escape at line 3 column 0
```

### Juurisyy (Root Cause)

Virhe johtuu kentistä `reasoning_steps` ([StepDTOStrict](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py#L24), [StepDTOSemantic](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py#L49)) ja `thought_process` ([ReasoningTraceDTO](file:///c:/src/quorum/backend_v2/models/domain/base.py#L136)), jotka on Pydanticissa määritelty tyypiksi `str`.

Vaikka Pydantic odottaa pelkkää merkkijonoa, promptin ohjeistus ("Step by step cognitive breakdown") kannustaa mallia generoimaan askeleittaisen rakenteen. Gemini yrittää täyttää kentän **stringifioidulla JSON-taulukolla** (esim. `"[\\n  {\\n    \\"step\\": 1..."`), ja tuottaa vahingossa `literal newline` (`\n`) -merkkejä JSON-merkkijonon sisään.

Koska raaka JSON ei salli rivinvaihtoja merkkijonon sisällä ilman asianmukaista eskapointia (`\\n`), Pydanticin `model_validate_json` kaatuu välittömästi, ja [LLMTaskExecutor](file:///c:/src/quorum/backend_v2/services/llm_task_executor.py#L319) kirjaa `LLM Schema Validation Failed`.

### Empiirinen havainto (Tier 6 Monitorointi, 23.6.2026)

Yksittäisen ajon (`exe_c7f3b69b...`) aikana havaittiin:
- **Vähintään 6 erillistä** `LLM Schema Validation Failed` -virhettä.
- Jokainen virhe laukaisi uudelleenyrityssyklin ([Self-Healing](file:///c:/src/quorum/backend_v2/services/llm_task_executor.py#L311-L315)), kuluttaen 10–60 sekuntia ylimääräistä aikaa (erityisesti Pro-mallin 12 sekunnin Pacing-lukon takia).
- Kaikki virheet itseparantuivat (Self-Healing successful), joten yksikään arviointi ei pudonnut DLQ:hun.
- **Mutta:** Jokainen turha uudelleenyritys maksoi sekä aikaa (latenssi) että rahaa (Vertex AI tokenit).

## 2. Vaikutukset Nykytilassa

| Alue | Vaikutus |
|------|----------|
| **Suorituskyky** | Jokainen virheellinen kutsu laukaisee uudelleenyrityksen. Pro-mallin kohdalla tämä aktivoi 12 sekunnin Pacing-lukon (`Wait-and-Poll`), pidentäen ajon kestoa tarpeettomasti. |
| **Kustannukset** | Uudelleenyritykset kuluttavat ylimääräisiä Vertex AI tokeneita. Flash-mallilla kustannukset ovat pieniä, mutta Pro-mallilla merkittäviä. |
| **Vakaus** | Vaikka Self-Healing estää kaatumisen, `max_schema_retries` (oletus 2) -rajan ylittäminen johtaa `AgentExecutionError` -poikkeukseen ja Graceful Degradation -tilaan. |
| **Käyttöliittymä (SDUI)** | XAI Highlights ja Reasoning Trace -näkymät joutuvat pahimmillaan renderöimään ruman stringified-JSON:in vapaan selittävän tekstin sijaan. |

## 3. Ratkaisu: Vapaan Tekstin Salliminen (Schema Simplification)

> [!NOTE]
> Alkuperäisessä Epicissä esitettiin kolme vaihtoehtoa (1: Pydantic Pre-Validator, 2: Pre-Parsing Sanitizer, 3: Schema Simplification). Analyysin perusteella **vaihtoehdot 1 ja 2 on hylätty** alla perustelluista syistä, ja toteutetaan vain vaihtoehto 3.

### Miksi vaihtoehdot 1 ja 2 hylättiin?

**Vaihtoehto 1 (Pydantic `@model_validator`):**
- Hoitaisi vain yhden oireen (laiton `\n`), mutta ei juuria.
- `reasoning_steps` on jo tyyppiä `str`. Validaattorin lisääminen siihen, jotta se osaisi parsia JSON-taulukkoa merkkijonosta, loukkaisi Pydanticin Fail-Fast -periaatetta: mallin pitäisi validoida dataa, ei muuttaa sen tyyppiä lennossa.
- Koodi monimutkaistuisi (uusi `@model_validator` jokaiseen DTO:hon), vaikka ongelma on oikeastaan promptin ohjeistuksessa.

**Vaihtoehto 2 (Pre-Parsing JSON Sanitizer):**
- Globaali regex-siivous `client.py`:ssä on vaarallinen: se voisi vahingossa muokata kenttiä, joissa rivinvaihdot ovat tarkoituksellisia (esim. `exact_quotes` -sitaatit, jotka sisältävät laillisia rivinvaihtoja lähdetekstistä).
- Luo väärän turvallisuuden tunteen: kehittäjät alkaisivat luottaa siihen, että sanitizer korjaa kaiken, sen sijaan että promptit ohjeistettaisiin oikein alusta asti.

### Vaihtoehto 3: Vapaan Tekstin Salliminen (VALITTU)

Koska Pydantic-malleissa kentät `reasoning_steps` ja `thought_process` ovat jo tyyppiä `str`, ongelma on yksinomaan siinä, että promptit kannustavat mallia tuottamaan sisäkkäistä JSON-rakennetta merkkijonon sisään.

**Ratkaisu:** Poistetaan JSON-pakotus, mutta **korvataan se tiukalla Markdown-templatella**. Näin vältämme JSON-escaping -virheet (Pydantic ei kaadu), mutta estämme myös vapaan tekstin tuoman rakenteellisen varianssin eri ajojen välillä. Malli ohjeistetaan täyttämään askeleet selkokielisenä "lomakkeena".

**Toteutus:**
1. Päivitetään promptit (`seed_data.json` tai Prompt Compiler) ohjeistamaan:
   *"Write your reasoning STRICTLY using the following plain text format. Do NOT use JSON arrays.
   Step 1 (Observation): [Extract your finding]
   Step 2 (Comparison): [Compare to rule]
   Step 3 (Conclusion): [State the outcome]"*
2. Päivitetään kenttien `description` -kuvaukset DTO-malleissa tukemaan tätä (esim. `"Cognitive breakdown strictly formatted as Step 1, Step 2, Step 3 text. Do NOT use JSON arrays."`).

**Hyödyt:**
- Poistaa JSON-escaping -virheet kokonaan kyseisten kenttien osalta.
- Säilyttää Chain-of-Thought (CoT) kognition hyödyt (malli ajattelee edelleen askeleittain, mutta kirjoittaa sen vapaana tekstinä).
- Parantaa SDUI-käyttöliittymän luettavuutta, kun XAI Highlights saa puhdasta tekstiä ruman stringified-JSON:in sijaan.
- Vähentää tokenikulutusta, koska vapaa teksti on tiiviimpää kuin JSON-syntaksi (`{"step": 1, "reasoning": "..."}`).

## 4. Toteutettavat Tiedostot

### Vaihe 1: DTO-kenttien Description-päivitys

#### [MODIFY] [evaluation_steps.py](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py)
- Päivitetään `reasoning_steps` -kentän `description` molemmissa DTO:issa (`StepDTOStrict` rivi 24, `StepDTOSemantic` rivi 49).
- Uusi kuvaus ohjaa mallia tuottamaan vapaamuotoista tekstiä JSON-rakenteen sijaan.

#### [MODIFY] [base.py](file:///c:/src/quorum/backend_v2/models/domain/base.py)
- Päivitetään `thought_process` -kentän `description` (`ReasoningTraceDTO` rivi 136).

### Vaihe 2: Prompt-ohjeistuksen päivitys

#### [MODIFY] Prompt Compiler / `seed_data.json`
- Lisätään eksplisiittinen ohje: *"Write your reasoning as plain free text paragraphs. Do NOT output JSON arrays, numbered JSON objects, or structured notation inside string fields."*
- Tämä ohje lisätään kaikkiin promptteihin, jotka viittaavat `reasoning_steps` tai `thought_process` -kenttiin.

### Vaihe 3: Self-Healing -telemetrian parannus

#### [MODIFY] [llm_task_executor.py](file:///c:/src/quorum/backend_v2/services/llm_task_executor.py)
- Lisätään `LLMSchemaValidationError` -käsittelijään (rivi 362) strukturoidumpaa telemetriaa:
  - Kirjataan, mikä kenttä aiheutti virheen (jos saatavilla Pydanticin virheviestistä).
  - Kirjataan, onko kyseessä toistuva virhe samassa kentässä (Stuck Loop Detection hyödyntää tätä jo, mutta telemetriaa voi rikastaa).
- **Perustelu:** Tällä hetkellä lokiin kirjataan vain geneerinen `"LLM Schema Validation Failed"`. Rikastettu telemetria mahdollistaa tulevaisuudessa datapohjaisen analyysin siitä, mitkä kentät ja mitkä mallit tuottavat eniten virheitä.

## 5. Varmennussuunnitelma (Verification Plan)

1. Ajetaan `uv run pytest` ja varmistetaan, ettei yksikään testi hajoa Description-muutosten jälkeen.
2. Ajetaan `uv run python scripts/backend_audit_loop.py . --test` arkkitehtuurivaatimusten varmistamiseksi.
3. Suoritetaan pieni testiaineiston ajo ja monitoroidaan `backend_debug.log`:sta, ettei `LLM Schema Validation Failed` -virhettä enää esiinny `reasoning_steps`/`thought_process` -kenttien osalta.
4. Varmistetaan SDUI-renderöinti: XAI Highlights ja Reasoning Trace -näkymät näyttävät vapaamuotoista tekstiä eikä JSON-koodia.

---
**Tila:** Ready for Execution (Tier 2)
