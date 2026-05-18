# **EPIC 57: Zero-Variance Protocol v2 Implementation Plan**

**Status:** To Do
**Prioriteetti:** Kriittinen (P0)
**Tyyppi:** Arkkitehtuurinen refaktorointi
**Mandaatit:** Clean Slate, KISS, Fail-Fast, No-Legacy, SSOT

## **1. Tavoite ja Pääsäännöt**

Tavoitteena on implementoida Zero-Variance Protocol v2 puhtaasti sääntöohjattuna, deterministisenä järjestelmänä. Kaikki epämääräinen arvaaminen, aiemmat AST-parserit, while-retry -luupit ja "älykkäät" self-healing -yritykset on tuhottava koodikannasta. 

**Noudatettavat Tier 2 Backend Hardening -säännöt EHDOTTOMASTI:**
* **`the_zero_compromise_pledge`**: Ei `.get("default")` fallbackeja. Pydantic-validointi on pakollinen kaikelle tiedolle.
* **`the_duct_tape_ban` / `silent_failures`**: "God Blockeja" (`except Exception: pass`) ei hyväksytä. Virheet lokitetaan ja heitetään eteenpäin välittömästi. Älä korjaa puuttuvia arvoja tyhjillä listoilla (`[]`) tai sanakirjoilla (`{}`).
* **`strict_pydantic_v2_rust`**: Käytä `.model_validate()`, ei vanhaa `parse_obj()`. Pydantic V2 -skeemojen on oltava 100 % tiukkoja (`ConfigDict(strict=True, extra='forbid')`).
* **`fail_fast_hydration_mandate`**: Kaikki dict-muodossa kulkeva epävarma data (esim. ulkoiset pyynnöt ja rajapinnat) hydratoidaan `.model_validate()` -metodilla VÄLITTÖMÄSTI ennen käsittelyä. Ei arvojen onkimista `data.get("avain")` tyylillä logiikkakerroksessa.
* **`zero_legacy_fallback_hacks`**: Vanhaa arkkitehtuuria ei tueta. Ei `@model_validator` -purkkakorjauksia vanhan V1-datan hyväksymiseksi. Vanhat kentät ja oletusarvot poistetaan armotta. Ei "or"-ketjuja.
* **`llm_structured_execution_mandate`**: LLM-kutsuihin on EHDOTTOMASTI käytettävä arkkitehtuurin Model Registryä (`LLMClient.from_strategy()`) ja `LLMTaskExecutor.execute_structured_task()` tai `execute_chat_task()`. Kaikki LLM-kutsut on tehtävä natiivilla Structured Outputs -rajapinnalla (esim. välittämällä Pydantic-skeema suoraan `response_schema`-parametriksi). Syntaktiset self-healing -luupit poistetaan koodikannasta kokonaan, sillä API-tason constrained decoding takaa 100 % Pydantic-yhteensopivan JSONin ensimmäisellä kerralla. Suora LLMClient-käyttö ja omat Retry-luupit (esim. `while`-loop fuzzaus) ovat kiellettyjä. `SystemConcurrency.LLM_MAX_RETRIES` on maksimissaan 2.
* **`high_fidelity_prompting`**: Dynaamiset parametrit eristetään `<execution_parameters>` -tagiin promptin alkuun. Ei f-stringejä loogisten sääntöjen rakentamisessa.
* **`single_source_of_truth_mandate`**: Koodikannassa ei saa olla V1- ja V2-malleja sekaisin tai päällekkäistä hydrataatiologiikkaa (esim. vanha `WorkflowDefinition` vs uusi `Workflow`). Kaikki ohjataan yhteen keskitettyyn lähteeseen. Päällekkäisyydet on poistettava.
* **`annotated_hydration_mandate`**: Merkkijonojen ja Enumien välinen konversio tehdään Pydanticin natiivilla `Annotated[Enum, Field(strict=False)]` -mekanismilla. Manuaalisia `try-except` silmukoita ei sallita. Lax-aliakset on tuotava keskitetystä `enums.py` lähteestä.

---

## **2. Toteutusaskeleet (Implementation Steps)**

### **VAIHE 1: Polymorfinen Kognitiivinen Pakottaminen (Hybrid Schema & Micro-CoT)**
Korvaa nykyiset poimintamallit yhdellä vahvasti tyypitetyllä `BaseTDAExtraction` perusluokalla, joka pakottaa Micro-CoT -ajattelun JSON-avaimien järjestyksellä.

1. Implementoi seuraava luokka ja pakota se käyttöön:
```python
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Any

class BaseTDAExtraction(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra='forbid')
    
    # 1. Pakotettu ajattelu ensin kohdekielellä
    step_1_evidence_scan: str = Field(description="Listaa havainnot ja lainaukset, jotka tukevat säännön täyttymistä (dokumentin kielellä).")
    
    # 2. Vastatodisteiden etsintä (Anti-sycophancy)
    step_2_mitigating_context: str = Field(description="Listaa havainnot, jotka kumoavat säännön tai ovat poikkeuksia (dokumentin kielellä).")
    
    # 3. Synteesin kapinaoikeus (Right to Dissent)
    contextual_override: bool = Field(description="Aseta True VAIN, jos fyysistä sanatarkkaa lainausta ei ole olemassa, mutta asiayhteys absoluuttisesti todistaa säännön. Älä käytä laiskuuden takia.")
    
    # 4. Vasta analyysin jälkeen fyysinen eristys
    exact_quote: str | None = Field(max_length=1500, description="Sanatarkka lainaus alkuperäisestä tekstistä. Pakko olla Null, jos override on True.")
    
    # 5. Dynaaminen datakuorma
    extracted_data: Any = Field(description="Spesifit poimitut arvot (boolean, taulukko, päivämäärä).")

    @model_validator(mode='after')
    def validate_override_logic(self) -> 'BaseTDAExtraction':
        """Estää mallin laiskuuden: jos override on käytössä, fyysistä lainausta ei saa enää antaa."""
        if self.contextual_override and self.exact_quote is not None:
            raise ValueError("Cross-validation failed: exact_quote MUST be null if contextual_override is True.")
        return self
```
2. Ohjeista malli tuottamaan `step_1` ja `step_2` kohdedokumentin alkuperäisellä kielellä, vaikka JSON-avaimet ja System Prompt ovat englanniksi.

### **VAIHE 2: Deterministinen Leksikaalisuus & Sekventiaalinen Worker-Vuonti**
Refaktoroi TDA-atomin suoritus (`evaluate_tda_atom`) Arq-workerissa sekventiaaliseksi ja deterministiseksi.

1. **Poista Retry-luupit:** Tuhoa kaikki while-silmukat, jotka yrittävät kutsua LLM:ää uudelleen, jos vastaus on huono.
2. **Sekventiaalinen suoritus (Asynkronisessa kontekstissa):** LLM-verkkokutsu ja sitä välittömästi seuraava leksikaalinen validointi on suoritettava sekventiaalisesti samassa Arq-työssä (`await llm_call()` -> `lcs_validate()`). Älä pilko niitä erillisiksi jonotöiksi (Saga-pattern), mutta älä myöskään blokkaa Pythonin event-luuppia fyysisillä synkronisilla kutsuilla (säilytä täysi skaalautuvuus).
3. **Leksikaalinen Matematiikka & Indeksimäppäys:** Hylkää koneoppimispohjaiset vektorivalidoinnit (Cosine Similarity). Jos `contextual_override` on True, ohita leksikaalinen tarkistus kokonaan. Muussa tapauksessa käytä `AnchorValidationService.normalize_text` -metodia. **Huom!** Koska normalisointi tuhoaa välilyönnit, luo ensin yksinkertainen 1D-indeksimäppäys (esim. `index_map[norm_idx] = orig_idx`). Tämä on vain muutaman koodirivin (O(N)) nopea operaatio.
4. **XAI Override (Alignment):** Laske vastaavuus normalisoiduilla merkkijonoilla käyttäen RapidFuzzin `fuzz.partial_ratio_alignment` -funktiota, joka palauttaa tuloksen lisäksi osuman alku- ja loppuindeksit. Jos osuma on > 85%, hae indeksimäppäyksen avulla alkuperäiset indeksit ja ylikirjoita `exact_quote` -kenttä EHDOTTOMASTI alkuperäisestä tekstistä eristetyllä fyysisellä leikkeellä (sisältäen sen alkuperäiset välilyönnit ja rivinvaihdot). Tämä takaa UI:n XAI-korostuksen toiminnan ilman raskaita diff-kirjastoja.
5. **Fail-Fast & Arq Retry-Stormin esto:** Arq-kirjasto yrittää oletuksena ajaa kaatuneen taskin uudelleen (usein `max_tries=5`). Estä piilotettu infrastruktuuritason retry-myrsky asettamalla Arq-työn rekisteröinnissä `max_tries=1`.
6. **Graceful DLQ-reititys:** Jos LCS-vastaavuus jää alle kynnyksen tai API heittää virheen, ota virhe kiinni worker-tasolla. Kirjaa atomi välittömästi tietokantaan tilaan FAILED/DLQ (Dead Letter Queue) yhdessä matemaattisen syyn kanssa (`lcs_score=X, threshold=0.85`), ja **palauta työlle hiljainen success** (esim. `return`). Älä anna poikkeuksen nousta Arq-moottorille asti kaatamaan työtä.

### **VAIHE 3: Prompt Caching & "Lost in the Middle" -ankkurointi**
Refaktoroi `prompt_compiler.py` generoimaan promptit staattista välimuistia maksimoivassa järjestyksessä, mutta suojaa malli pitkien dokumenttien "Lost in the Middle" -ilmiöltä.

1. Promptin järjestys on oltava EHDOTTOMASTI seuraava:
   * **1. System Prompt & Few-Shot (Static Global):** Täysin staattinen järjestelmäohjeistus ja `<golden_examples>` aivan ensimmäisenä.
   * **2. Document (Static per Document):** Massiivinen lähdedokumentti käärittynä `<source_data>`-tägeihin.
   * **3. Execution Parameters & Attention Anchoring (Dynamic):** Itse atomin dynaaminen sääntö (`<execution_parameters>`) ja suoritettava tehtävä (`<task>`) asetetaan User Messagen LOPPUUN.
2. **Attention Anchoring:** Vaikka säännöt määritellään System-promptissa, toista aivan lopussa (`<task>`-osion yhteydessä) kriittisimmät uuttosäännöt lyhyesti. Varmista erityisesti, että olemassa olevaa `<CRITICAL_LANGUAGE_MANDATE>`-osiota EI poisteta `prompt_compiler.py`:stä. Se toimii elintärkeänä ankkurina, joka herättää LLM:n huomion juuri ennen generoinnin alkamista, estäen sääntöjen unohtumisen kymmenien tuhansien tokenien dokumentin jälkeen.
3. Älä injektoi dynaamisia sääntöjä promptin keskelle.

### **VAIHE 4: Taktiset Turvasäännöt**
1. **Spatiaalinen lukitus:** Leksikaalinen haku (`exact_quote`) tehdään VAIN sille Chunkille, jota malli käsitteli. Ei dokumentinlaajuista skannausta.
2. **Lazy Dumpingin estäminen (Kaksitasoinen turva):** 
   - **Verkkotason turva:** Aseta tiukka **`max_tokens` / `max_completion_tokens`** -katto suoraan `LLMTaskExecutor.execute_structured_task()` -kutsun parametreihin (esim. max 600 tokenia). Vain tämä katkaisee verkkotason generoinnin fyysisesti ja estää token-vuodon.
   - **Lokaali turva (API 400 Bad Request -pommi):** Pydantic-mallissa pidetään `max_length=1500` lokaalia fail-fast-validointia varten, MUTTA mandaatti devaajille: Rajapinnalle lähetettävästä JSON-skeemasta on riisuttava pituusrajoitteet lennosta adapterikerroksessa. Jos Pydantic-skeema lähetetään sellaisenaan, API kaatuu HTTP 400 -virheeseen (Native Structured Outputs ei tue pituusrajoitteita).
3. **Right to Dissent:** Malli saa käyttää asettamaamme `contextual_override` -boolean-kenttää ohittaakseen sokean leksikaalisen pakotuksen, mikäli asiayhteys vaatii sen. Tämä tuottaa eksplisiittisen, Pydantic-turvallisen rakenteen.

### **VAIHE 5: TDD-Mandaatit & QA (Automatisoidut Testit)**
Koodarien on EHDOTTOMASTI rakennettava seuraavat 100 % kattavuuden testitapaukset CI/CD-putkea varten:

1. **`test_native_schema_strips_unsupported_constraints` (Unit)**
   - **Mitä testataan:** API-rajapinnalle vietävän JSON Scheman validius.
   - **Assertio:** Generoi Pydantic-mallista API-kuorma (JSON Schema). Varmista assertiolla (`"maxLength" not in schema`), että pituusrajoitteet on riisuttu. Tämä varmistaa, ettei API kaadu 400 Bad Request -virheeseen.

2. **`test_pydantic_max_length_fail_fast_and_dlq_routing` (Integration)**
   - **Mitä testataan:** Pydanticin fail-fast -toiminta ja Arq-infrastruktuurin turvallinen toipuminen.
   - **Assertio:** Syötä pipelineen mockattu LLM-vastaus, jossa `exact_quote` on 1501 merkkiä. Assertoi, että `.model_validate_json()` nostaa välittömästi `ValidationError`-poikkeuksen, Arq-worker catchaa sen, atomin tila päivittyy kantaan muotoon FAILED/DLQ, ja mock-laskurit todistavat, ettei `llm_call`:ia kutsuttu kertaakaan uudelleen (ei retry-myrskyä).

3. **`test_lcs_normalization_retains_raw_pdf_mapping` (Unit)**
   - **Mitä testataan:** XAI-datan (indeksien) säilyminen rajussa normalisoinnissa.
   - **Assertio:** Syötä testi-chunk: `"Tämä  on\n\t tär\xadkeä \u00ADsopimus."` (sisältää soft hyphenejä, tabeja ja rivinvaihtoja). Syötä LLM:n uuttama puhdas `exact_quote`: `"Tämä on tärkeä sopimus."`. Assertoi, että LCS-pisteet ovat tasan 100.0 %, ja että validointikerros on indeksimäppäyksen avulla ylikirjoittanut atomin lopulliseksi uutoksi alkuperäisen ruman version `"Tämä  on\n\t tär\xadkeä \u00ADsopimus."`.

4. **`test_contextual_override_cross_validation` (Unit)**
   - **Mitä testataan:** Mallin laiskuuden estäminen Pydanticin puolella.
   - **Assertio:** Syötä JSON, jossa `contextual_override=True` ja `exact_quote="Löytyi lainaus"`. Pydanticin `@model_validator(mode='after')` on heitettävä `ValueError` (ristiinvalidointi epäonnistui).

---

## **3. Hyväksymiskriteerit (Definition of Done)**
* [ ] Koodikannassa ei ole yhtäkään viittausta vanhoihin AST-parsereihin tai omatekoisiin tekoälyn retry-luuppeihin.
* [ ] `BaseTDAExtraction` (Micro-CoT) on täysin käytössä koko putkessa.
* [ ] Arq-worker (`evaluate_tda_atom`) suorittaa LLM-haun ja LCS-validoinnin synkronisesti ja fail-fast tyylillä ilman yritysten toistamista.
* [ ] Prompt Compiler -topologia järjestää viestit 1. System (Static), 2. Source Data (Static), 3. Task (Dynamic).
* [ ] Kaikki Pydantic-mallit on lukittu `strict=True` ja `extra='forbid'`.
* [ ] Koodissa ei ole yhtäkään `except Exception: pass` tai `.get("key", default)` purkkaviritystä TDA-putkessa.