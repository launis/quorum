# Epic 55: Prompt Directive SSOT (Persona Isolation Refactor)

> [!IMPORTANT]
> **THE CLEAN SLATE MANDATE (`the_duct_tape_ban` & `the_no_legacy_mandate`)**: Toteutamme tämän puhtaalta pöydältä (Clean Slate). Emme huomioi vanhoja ajoja tai historiallisia tietokantarakenteita. Kaikki "fallback"-ominaisuudet (esim. `obj.get('old_field')`), purkkakoodi (duct tape) ja kovakoodaus ovat ANKARASTI KIELLETTYJÄ. Jos data puuttuu, järjestelmän tulee kaatua välittömästi (Fail-Fast). Rakennamme puhdasta arkkitehtuuria ilman kompromisseja.
## 1. Yhteenveto ja Tavoite (Objective)
Tämän Epicin tavoitteena on poistaa kriittinen arkkitehtuurinen velka, jossa laajat järjestelmätason ohjeet (kuten `<global_framework>`, "Zero-Interpretation Doctrine" ja tarkan 5-vaiheisen `mechanical_trace`-lokin formaatti) on kopioitu kymmeniin eri `PromptBlock`-objekteihin tietokannassa.

Tämä "copy-paste" -malli rikkoo Single Source of Truth (SSOT) -periaatetta, paisuttaa tietokantaa, vaikeuttaa järjestelmän ohjeistuksien päivittämistä lennossa ja altistaa järjestelmän kriittisille regressioille, mikäli ihmiskäyttäjä vahingossa poistaa tai muokkaa turvamekanismeja Admin Studion käyttöliittymästä.

**Tavoite:** Erottaa "Asenne/Käyttäytyminen" (System Framework) puhtaasta "Substanssista" (Matrix Domain Logic).
* **Framework (Miten):** Siirretään ohjelmalliseksi Enum-reititetyksi vakioksi backendin ytimeen.
* **Substanssi (Mitä):** Jätetään `PromptBlockin` `ai_description`-kenttään vain ja ainoastaan kyseistä matriisia koskeva asiantuntijaohje.

---

## 2. Arkkitehtuurinen Linjaus: Enum & PromptCompiler Injection

Toteutamme turvallisen ohjelmallisen injektion (Kooditason SSOT), joka takaa absoluuttisen suojan (Fail-Safe) kriittisille säännöille:

1. **Backend Vakioistaminen:** Luodaan `ExecutionPersona` (tai `FrameworkDirective`) Enum. Backendin uuteen ytimeen (esim. `backend_v2/core/system_directives.py`) tallennetaan massiiviset prompt-osiot, kuten `DETERMINISTIC_PARSER_FRAMEWORK`.
2. **Dynaaminen Injektio:** `PromptCompiler` tarkistaa suoritettavan `PromptBlockin` Enum-arvon ja liittää sen vastaavan järjestelmäohjeen automaattisesti LLM:n system-promptiin.
3. **Käyttöliittymän Rajoitus:** Flutter Admin Studiossa käyttäjä ei näe enää koko jättimäistä sääntötekstiä, vaan pelkän pudotusvalikon: "Select Persona: Deterministic Parsing Engine".

---

## 3. Toteutuksen Vaiheet (Työnkulku)

### Phase 1: Backendin Core-Injektio (Arkkitehtuuri)
* **Toimenpide 1:** Luodaan `backend_v2/core/system_directives.py`, jonne tallennetaan `<global_framework>` muuttumattomana merkkijonovakiona (String Constant).
* **Toimenpide 2:** Luodaan `ExecutionPersona` Enum (esim. `DETERMINISTIC_PARSER`, `GENERATIVE_ASSISTANT`).
* **Toimenpide 3:** Päivitetään `v2_core.py` -> `PromptBlock`-malliin uusi kenttä `execution_persona: ExecutionPersona`.
* **Toimenpide 4:** Muokataan `PromptCompiler` (`compile_xml_rubrics` / context builder) lukemaan tämä kenttä ja liimaamaan `system_directives.py`:n sisältö promptin ylälaitaan.

### Phase 2: Datan Siivous ja Migraatio (Seed Data Mass Refactor)
* **Toimenpide 1:** Kirjoitetaan skripti (esim. `scratch/v5_1_prompt_slimming.py`), joka käy läpi `seed_data.json`-tiedoston kaikki `PromptBlockit`.
* **Toimenpide 2:** Skripti asettaa kaikkiin matriiseihin kentän `"execution_persona": "DETERMINISTIC_PARSER"`.
* **Toimenpide 3:** Skripti etsii ja poistaa `ai_description`-kentistä koko massiivisen `<global_framework>` -tekstin, jättäen jäljelle vain alkuperäisen matriisikohtaisen työnkuvauksen.
* **Toimenpide 4:** Ajetaan `run_seed.py local` ja varmistetaan unit-testien (`backend_audit_loop.py`) läpimeno.

### Phase 3: Frontend (Admin Studio UI) Päivitys
* **Toimenpide 1 (Ylätaso / Matrix):** Päivitetään `client_app_v2/lib/features/studio/models/prompt_block.dart` sisältämään uusi Enum-kenttä (`execution_persona`). 
* **Toimenpide 2:** Muokataan Admin Studion matriisin muokkausnäkymää: poistetaan raskaat sääntölaatikot ja lisätään pudotusvalikko `Execution Persona`.
* Tämän vaiheen myötä Ylätason (Matrix) Admin Studion LLM-hallinta siirtyy vapaamuotoisesta "prompt-koodailusta" tiukasti jäsenneltyyn, pudotusvalikko-ohjattuun Data-Driven -käyttöliittymään.

### Phase 4 (Tulevaisuuden Evoluutio): SystemConfigs Multiplexing
Tämä on tulevaisuuden tavoite, jota ei välttämättä toteuteta tässä Epicissä:
* Kun järjestelmä vakautuu, Pythonin sisään koodatut `system_directives.py` vakiot voidaan siirtää V7.5 arkkitehtuurin mukaisesti tietokantaan `SystemConfig`-dokumenteiksi ("Global Prompt Components").
* Tämä mahdollistaisi pääkäyttäjien muokata jopa `<global_framework>`-sääntöjä lennossa käyttöliittymän kautta ilman backend-päivityksiä.

---

## 4. Definition of Done (DoD)
1. **SSOT Toteutuu:** Tietokanta (`seed_data.json` tai `db_v2.json`) ei sisällä missään matriisissa laajoja "Zero-Interpretation", "Trace format" tai "Morpho-Syntactic" -sääntöjä, vaan ne ladataan yhdestä backendin tiedostosta lennossa.
2. **PromptCompiler Injektointi:** Pydantic / PromptCompiler kerää promptit oikein siten, että token-määrä ja ohjeistus OpenAI:lle/Anthropicille pysyy 100 % identtisenä vanhaan verrattuna (testataan vertailuajolla).
3. **Käyttöliittymä (Flutter):** Matriisin luonti sisältää Persona-Enumin, ja ohjaus on turvallisesti eristetty käyttöliittymästä koodin puolelle (Fail-Safe).
4. **Dokumentaatio:** `docs/architecture/` -hakemiston dokumentit ja `.agents/rules/04_directory_reference.md` on EHDOTTOMASTI päivitettävä vastaamaan uutta arkkitehtuuria (esim. kun `system_directives.py` ja muut uudet tiedostot on luotu).
