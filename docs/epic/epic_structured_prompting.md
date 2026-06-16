# Epic: Schema-Driven Cognitive Control & SDUI (Structured Prompting)

## 1. Tavoite

Tavoitteena on siirtyä f-string -pohjaisista prompteista ja vapaamuotoisesta Markdown-jäsennöinnistä tiukkoihin Pydantic-pohjaisiin JSON-skeemoihin. LLM:n kognitiivinen ohjaus keskitetään lennosta rakennettaviin Pydantic-malleihin (SchemaFactory). Tämä mahdollistaa automaattisen determinismin ja poistaa raskaan Python-tason portinvartijalogiikan (Track B).

> [!IMPORTANT]
> **Hardening Rule #28 (`llm_structured_execution_mandate`)**:
> "Direct instantiation or calling of the `LLMClient` SDK is prohibited. All LLM inferences MUST be centralized and routed exclusively via `LLMTaskExecutor.execute_structured_task()`."

> [!IMPORTANT]
> **Hardening Rule #20 (`the_self_healing_ban`)**:
> "Attempting to dynamically patch AI-generated quotes or JSON formatting errors on-the-fly using Regex is STRICTLY PROHIBITED. Data validation belongs 100% to Pydantic."

> [!IMPORTANT]
> **Hardening Rule #14 (`frozen_state_mutability`)**:
> "`HookState` and other domain models are permanently frozen. You MUST NOT mutate state in-place (e.g., `state.inputs = X`). Hooks MUST purely return `HookResult(state_delta={...})`."

> [!IMPORTANT]
> **Hardening Rule #51 (`hybrid_prompting_mandate`)**:
> "System prompts MUST use a hybrid of XML for structural control and Markdown for nested content formatting."

> [!IMPORTANT]
> **Hardening Rule #84 (`pydantic_schema_freeze_mandate`)**:
> "Pydantic Schema Freeze Mandate: NEVER autonomously tighten or alter the structural types, `Optional` bounds (`| None`), or field signatures of any Pydantic models. [...] Hyväksytty poikkeus tässä Epicissä: `PromptBlock`-malliin lisätään `allows_semantic_override`."

> [!IMPORTANT]
> **Hardening Rule #37 (`pydantic_namespace_collisions`)**:
> "Inline schemas within router definitions are prohibited. All Pydantic schema definitions MUST reside exclusively in the `models/` directory."

> [!IMPORTANT]
> **Hardening Rule #65 (`pep750_t_strings_only`)**:
> "Construct dynamic LLM prompts and SQL statements exclusively utilizing Python 3.14 t-strings (Template Strings - PEP 750). The use of standard f-strings within critical data ingestion pathways is categorically forbidden due to inherent injection vulnerability vectors."

---

## 2. Tekniset Reunaehdot ja Vaatimukset

Seuraavat kriittiset arkkitehtuurivaatimukset on huomioitava toteutuksessa:

1. **`evaluate_extraction()` ja Track A**: Track A (fyysinen lainausten todentaminen `AnchorValidationService`:n kautta) säilyy ennallaan. Vain Track B:n porttifunktio (`if strictness_level >= 100: status = "FAIL"`) korvataan Pydantic-tason pakotuksella.
2. **`scoring.py` Override-hierarkia**: Kolmitasoinen override-hierarkia (Workflow × TDA) säilytetään Defense-in-Depth -mekanismina. Se ei ole korvattavissa pelkällä skeemapäivityksellä.
3. **`chunk_worker.py:383` In-place mutaatio**: Mutaatio `strictness_level = max(strictness_level, 100)` (Fast-Model Compensator) on Rule 14 rikkomus ja se poistetaan kokonaan. Zero-Trust pakotus delegoidaan SchemaFactorylle.
4. **Vertex AI ja `Literal[False]`**: Vertex AI ignoroi `"const": false` -rajoitteen JSON Schemassa. Tämä on korjattava muuntamalla `"const": <val>` muotoon `"enum": [<val>]` tiedostossa `client.py:305`.
5. **Zero-Trust Security Violation & AND-Logiikka**: Semanttinen ohitus sallitaan kenttäkohtaisesti vain, jos *sekä* protokolla *että* yksittäinen TDA-sääntö sen sallivat (AND-logiikka). Jos LLM palauttaa luvattoman `contextual_override=True`, askeleesta on nostettava kova `SecurityViolationError`.
6. **SchemaFactory Suorituskyky**: `build_dynamic_schema()`-funktion serialisointi-overhead on minimoitava luomalla välimuistiavain lajitelluista `block_id`-arvoista kokonaisen JSON-dumpin sijaan. Lisäksi kaksoiskutsu `llm.py`:ssä on poistettava.

---

## 3. Toteutusvaiheet (Implementation Plan)

### Vaihe 0: Esivaatimukset (Kriittinen Core-valmistelu)
- [x] **Rule 14 -korjaus (`chunk_worker.py`)**: Poista `chunk_worker.py:383` in-place mutaatio ja koko "Fast-Model Compensator" -logiikka. -> Track B poistettu kokonaan, ja testit vihertävät.
- [x] **Seed Data -puhdistus**: (PERUUTETTU) `concept_description` palautettiin TDA-refaktoroinnissa pakolliseksi Pydantic-kentäksi (säilytettävä `""` arvona, jos tyhjä). BANNED LOGIC on jo suojattu onnistuneesti.
- [x] **Contextual Override -laajennus**: (SUORITETTU TDA-refaktoroinnissa) `allow_contextual_override` lisättiin `TdaAssertion`-malliin (korvasi alkuperäisen `PromptBlock` tason suunnitelman).
- [x] **`const` → `enum` -muunnos (`client.py:305`)**: Laajenna `strip_unsupported_constraints()` muuntamaan `"const": <value>` muotoon `"enum": [<value>]` rekursiivisesti. (Kriittinen esivaatimus Vertex AI:lle).

### Vaihe A: Infrastruktuuri ja Syötteiden Formatointi
- [x] **XML-muunnin**: (SUORITETTU TDA-refaktoroinnissa) Kääntäjä generoi nyt puhdasta `<tda_validation>` XML-koodia erillisillä kentillä suoraan `localization_compiler.py`:ssä.
- [x] **XML-kääntäjän korjaus (`concept_description`)**: Päivitä `localization_compiler.py` lisäämällä `<concept_description>` -tagi tulosteeseen, jos se ei ole tyhjä. Tällä hetkellä kääntäjä hukkaa koko kentän eikä ohjaa LLM:ää konseptin kuvauksella.
- [x] **Globaali Ohjelmallinen Kielikonteksti (Universal Linguistic Context)**
**Tiedosto:** `chunk_worker.py` ja `synthesis.py` (ja prompt-templaten päivitys)
- [x] Olet havainnut, että jos kieltä ei lukita joka kerta lennosta, malli "driftaa" kielestä toiseen. Kielen on tultava tietokannasta (käyttäjän tai organisaation asettama kieli) aina ohjelmallisesti.
- [x] **Toteutus:** Rakenna kaikkiin prompteihin standardoitu XML-lohko `<linguistic_context>`, joka injektoidaan _jokaisen_ API-kutsun alussa ohjelmallisesti Pythonilla.
```xml
<linguistic_context>
  <source_data_language>{db.source_language}</source_data_language>
  <required_output_language>{db.user_language}</required_output_language>
  <required_reasoning_language>English</required_reasoning_language>
</linguistic_context>
```
- [x] **Kriittinen lisäys (Kielellisen Kontekstivuodon / Semantic Bleed esto):** Kun mallia pyydetään päättelemään englanniksi mutta poimimaan lainaus suomeksi, vaarana on kielivuoto (malli kääntää `exact_quote`:n englanniksi). Lisää promptin sääntöihin (ja Pydanticin `Field` -kuvauksiin) ehdoton mandaatti: *"CRITICAL: The `exact_quote` MUST ALWAYS be extracted in the exact original language of the source text. NEVER translate the quote, even if your reasoning is in another language."*
- [x] Tämä kokonaisuus estää satunnaiset kielen vaihtumiset kesken suorituksen (Semantic Loss) ja varmistaa, ettei kielellinen vuoto tuhoa Track A:n Verbatim-poimintaa.
- [x] **SchemaFactory Optimointi ja Dynaamisuus (Zero-Overfit)**: 
  1. Muuta välimuistiavain (`schema_factory.py`) hyödyntämään ID-jono-konkatenointia `json.dumps`:n sijaan.
  2. Poista tarpeeton `global_schema`-kutsu `llm.py`:stä ja populoikaa XAI-tallennus `ChunkWorker.process_chunk`-paluuarvosta.
  3. **Agnostinen Kohdedokumentti ja Rust-vuodon esto (Schema Freeze)**: Kohdedokumenttien valintaa (`target_document`) **EI SAA** toteuttaa lennosta rakennettavana dynaamisena Enumina, koska Pydantic V2:n Rust-ydin (pydantic-core) vuotaa muistia ja ylikuormittuu jatkuvista lennosta käännöksistä (Hardening Rule #84). Pydantic-mallin on oltava pysyvästi jäädytetty ja käytettävä staattista `target_document: str` -kenttää. Oikean dokumentin valinta ohjataan injektoimalla promptin tekstiin tietokannasta haettu lista sallituista dokumenteista ja niiden `ai_description` -metatiedoista (esim. `seed_data.json`). Jos LLM palauttaa kenttään tunnistamattoman avaimen, `chunk_worker.py` hylkää sen Python-tasolla (`SecurityViolationError`). Tämä estää samalla Cache Poisoning -virheet välimuistissa, koska skeema pysyy muuttumattomana.

### Vaihe B: Pydantic Prompt -mallien määrittely
- [x] **Mallien luonti**: Luo hakemistoon `backend_v2/models/prompts/` omat Pydantic-mallit promptien rakenteille (esim. `TdaValidationPrompt`). Tyhjät kentät pudotetaan (`exclude_none=True`).

### Vaihe C: Turvallisuus (PEP 750 t-strings & TemplateProcessor)
**Tiedosto:** `backend_v2/core/template_processor.py` (Uusi tiedosto)
- [x] **`TemplateProcessor`-luokka**: Luo uusi luokka korvaamaan nykyiset Python f-stringit promptien rakentamisessa (Hardening Rule #65).
- [x] **Prompt Injektion Esto (CDATA Encapsulation + Breakout Shield)**: Korvataan raskaampi HTML-sanitointi huomattavasti elegantimmalla ja natiivimmalla ratkaisulla. Käyttäjän syötteet kääritään promptissa aina XML:n `<![CDATA[ ... ]]>` -lohkoon. Nykyaikaiset kielimallit ymmärtävät CDATA-semantiikan ja tietävät automaattisesti, että lohkon sisällä olevia (esim. käyttäjän injektoimia `<rule>`) tageja EI saa noudattaa ohjeina, vaan ne ovat puhtaasti raakadataa.
- [x] **Toteutus (TemplateProcessor):** `TemplateProcessor.safe_interpolate` käärii syötteet automaattisesti CDATA-lohkoon. Ainoa tarvittava sanitointi on **CDATA Breakoutin esto**: Käyttäjän syötteestä on etsittävä merkkijono `]]>` (joka sulkisi lohkon ennenaikaisesti) ja korvattava se turvalliseen muotoon (esim. standardilla `]]]]><![CDATA[>`). Tämä on täydellinen "Zero-Touch" -ratkaisu: alkuperäisiä `<` ja `>` -merkkejä ei tarvitse sanitoida, joten Track A:n Verbatim-poiminta ja regex-haku toimivat täydellisesti sellaisenaan ilman backendin purku- tai rehydraatiokikkoja.
- [x] **f-string -migraatio**: Korvaa nykyiset f-string -rakenteet dynaamisilla PEP 750 t-stringeillä ja ohjaa ne rakennetun `TemplateProcessor`in läpi välttääksesi `TypeError`-kaatumiset.

### Vaihe D: Seed Data ja Kognitiiviset Protokollat
- [x] **Kognitiivisen Skitsofrenian Esto (Seed Data Migraatio)**: Etsi `seed_data.json` -tiedostosta kaikista TDA-säännöistä kovakoodatut vanhat käskyt (esim. *"TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log"*). Korvaa nämä eksplisiittisellä kehotuksella: *"TRACE REQUIREMENT: Follow the explicit step-by-step cognitive sequence defined in the provided JSON schema."* Tämä poistaa ristiriidan ja delegoi rakenteellisen ohjauksen 100 % Pydantic-skeemalle.
- [x] **Protokollien lisäys**: Luo `seed_data.json`:iin uudet protokollat `blk_8b4c2e1f9a0d3765` (Guided Semantic) ja `blk_f23a9b1c7d4e5082` (Freeform Semantic), joissa `allows_semantic_override: true`.
- [x] **Tiukkuus-säätö**: Päivitä `prompt_compiler.py` `calibrate_strictness()` käyttämään formaattia `"SCORING_STRICTNESS: {val}/100"`.
- [x] **Kovakoodauksen poisto**: Päivitä `studio.py` hakemaan ensimmäinen `category_id == "protocol"` -block dynaamisesti.
- [x] **Testien päivitys**: Päivitä hajonneet testit (~15 tiedostoa) vastaamaan uutta `allows_semantic_override` -kenttää.

### Vaihe E: Schema-Driven Override ja Determinismi
- [x] **Mallien päivitys ja Kognitiivinen Työjärjestys**: Korvaa `SchemaFactory`ssä olevat nykyiset `str`-kentät (esim. `reasoning_trace`) sisäkkäisillä Pydantic-malleilla (esim. `ParsingLogSteps`). **Kriittinen järjestys:** Pydantic-mallissa `reasoning_steps` -kentän on oltava määritelty **ennen** `decision: bool` ja `contextual_override: bool` kenttiä, jotta LLM pakotetaan ajattelemaan ennen lukitusta (kognitiivinen puskurointi).
- [x] **Agnostinen Askel-malli (Scope Drift -esto)**: `ParsingLogSteps` -mallin on oltava täysin universaali lista (esim. `list[StepDTO]`, jossa `step_goal` ja `extracted_evidence`). Älä kovakoodaa laajuuksia (esim. "sentence" tai "holistic") Enum-arvoihin, jotta arkkitehtuuri kestää muuttuvat TDA-säännöt yli-sovittamatta (Zero-Overfit).
- [x] **Skeema-vuodon Esto (Dual Static Schemas):** Jos `strictness=100` (Zero-Trust), `contextual_override` -kenttää **ei saa** näyttää kielimallille ollenkaan. Jos kenttä on olemassa edes pelkkänä `bool`-tyyppinä, LLM saattaa hallusinoida sen `True`:ksi, tuhlata tokeneita selittelyyn ja aiheuttaa koko suorituksen kaatumisen validointivirheeseen. Koska emme voi luoda skeemoja lennosta (Rust-muistivuodon takia), luo kaksi täysin staattista mallia:
  1. `StepDTOStrict`: Ei sisällä kenttiä `contextual_override` tai `override_reason`.
  2. `StepDTOSemantic`: Sisältää ohituskentät.
- [x] **Ennakoiva Reititys (Proactive Control):** Poistetaan aiemmin kaavailtu reaktiivinen Python-tason `AND`-logiikka. Sen sijaan `chunk_worker.py` tarkistaa ennen LLM-kutsua, salliiko protokolla ja `strictness`-arvo ohituksen. Jos ei, Vertex AI:lle annetaan suoraan `StepDTOStrict` -skeema. Tällöin LLM on fyysisesti estetty tekemästä ohituksia, token-vuoto tukitaan, ja koodi toimii O(1) staattisilla malleilla ilman muistivuotoja.
- [x] **Track B Pelkistys**: Poista `chunk_worker.py`:n `evaluate_extraction()`:n Track B:n porttifunktio.
- [x] **XAI-Rajapinta**: Laajenna arviointi-endpoint palauttamaan `PromptContextDTO`.

---

## 4. Tietoisesti rajattu pois (Out of Scope)
- **Synthesis SDUI (Phase 2):** `SynthesisOutputDTO.synthesized_markdown` -kentän korvaaminen Pydantic-rakenteella rajataan pois. Tämä tehdään omana Epicinään (`epic_sdui_synthesis.md`).
- **Vertex AI `strict=False` -migraatio:** Tehdään erillisenä konfiguraatiomuutoksena.

---

## 5. Menestyskriteerit (Definition of Done)
- [x] Yhtään tyhjää XML-tagia (kuten `<tag></tag>`) ei lähetetä LLM:lle.
- [x] LLM palauttaa 100 % tyyppiturvallisia JSON-objekteja ilman formaattivaihteluita.
- [x] `chunk_worker.py`:n Track B:n porttifunktio on korvattu tarkalla Python-tasoisella AND-logiikan pakotuksella (`SecurityViolationError`), samalla kun Pydantic hoitaa vain tyyppiturvallisuuden (`bool`).
- [x] `scoring.py`:n kolmitasoinen override-hierarkia on yksinkertaistettu mutta säilytetty (Defense-in-Depth).
- [x] `evaluate_extraction()`:n Track A (fyysinen lainausvalidointi) toimii muuttumattomana.
- [x] `chunk_worker.py:383`:n in-place mutaatio on poistettu.
- [x] Arkkitehtuuri noudattaa kaikkia listattuja Hardening Rule -sääntöjä.

---

## 6. Päätös / Yhteenveto (16. Kesäkuuta 2026)
Epic on täysin suoritettu. Structured Prompting ja SDUI Validation toimivat nyt 100% Pydanticin ja SchemaFactoryn varassa täysin deterministisesti. Lainaukset haetaan virheettömästi Spatial Anchoring -logiikalla, ja käyttöliittymä renderöidään UI-blokkeina. Kielellinen drift on korjattu ja `ROLE_ARCHITECT` on lokalisoitu onnistuneesti ohjelmallisesti (Translation Leakage korjattu). Koko suoritusputki selvisi End-to-End testistä.
