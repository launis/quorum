# Epic: TDA-putken Kognitiivinen ja Rakenteellinen Uudistus (Bilingual Schema & Zero-Reasoning Refactor)

## Tiivistelmä (Executive Summary)

### Miksi (Syyt ja ongelman kuvaus)
* Kustannus- ja tehokkuusvuoto: Jopa 60 % monimutkaisten työnkulkujen LLM-kustannuksista kuluu tarpeettomiin "reasoning-tokeneihin" (Chain-of-Thought) rutiinipoiminnoissa, mikä hidastaa ajoja ja maksaa liikaa.
* Järjestelmän TDA-putkessa on havaittu varianssikriisi (Entropia 1.0) raskaiden analyysimatriisien osalta.
* Kielellinen ristiriita tuhoaa arvioinnin tarkkuuden: vanhat säännöt ovat yhtenäisiä englanninkielisiä merkkijonoja, mikä pakottaa kielimallin kääntämään sääntöjä semanttisesti lennosta suomenkielisiä tekstejä analysoidessaan.
* Rajatapauksissa (Boundary Cases), kuten argumenteissa joita erehdytään pitämään retorisina tehokeinoina, kielimalli joutuu arpomaan tuloksia, koska siltä puuttuvat yksiselitteiset hylkäyskriteerit.
* Kielimallit kärsivät miellyttämishalusta ja vahvistusvinoumasta, minkä vuoksi ne yrittävät väkisin löytää osumia tyhjästä lisäten analyysin satunnaisuutta.

### Mitä (Tavoitteet ja tuotokset)
* Nostaa mittauksen luotettavuus (Cohen's κ ≥ 0.85) eliminoimalla systemaattiset tulkintaepäselvyydet, hyödyntäen EPIC 71:n löydöksiä juurisyistä.
* Nostaa järjestelmän parittainen konsistenssi (Self-Consistency) yli 98 %:iin siirtymällä kalliista Pro-mallin kognitiivisesta päättelystä Best-of-Three (2/3) rinnakkaisajoon ja enemmistöäänestykseen mekaanisissa rutiinipoiminnoissa (EPIC 77 integraatio).
* Litteistä `string`-tyyppisistä säännöistä siirrytään rakenteelliseen ja tyyppiturvalliseen `I18nText` Pydantic BaseModel -ratkaisuun.
* Rutiinitehtävien kustannusten ja suoritusajan leikkaaminen "Zero-Reasoning Mandate" -säännöllä, joka eliminoi tarpeettoman ääneen ajattelun mekaanisissa uutoissa.
* Järjestelmään lisätään tiukat negatiiviset poikkeussäännöt (Boundary Disambiguation), jotka pakottavat mallin palauttamaan deterministisesti `null`-arvon rajatapauksissa ilman luovaa arvailua.
* Oletustilaksi pakotetaan nollahypoteesi: malli ei palauta osumaa, ellei se pysty poimimaan tekstistä tarkkaa lainausta, joka vastaa vaadittuja ankkurisanoja.
* Sääntöjen osat (kuten ohjeteksti, ankkurisanat ja poissulkusäännöt) eristetään arkkitehtuurisesti toisistaan, jotta ankkurit voidaan syöttää mallille erillisenä kohdekielisenä sanalistana (Zero Semantic Drift).

### Miten (Toteutuksen vaiheet: Expand & Contract)
Tämä Epic on jaettu peräkkäisiin, rinnakkaisiin ja taaksepäin yhteensopiviin vaiheisiin (**Expand & Contract** -malli), jotta vältetään valtavien "God Commit" -muutosten aiheuttamat koodin rikkoutumiset. Järjestelmä pidetään koko ajan 100% suoritettavana.

**Expand & Contract -vaiheet:**
* **Vaihe 1 (God Object Refactor):** Ennakko-siivous. Pilkotaan PromptCompiler pienempiin SRP-moduuleihin ilman rakenteellisia skeemamuutoksia.
* **Vaihe 2 (Schema Expand):** Pydantic-skeemoihin ja Flutter-malleihin LISÄTÄÄN uudet rakenteelliset kentät (`concept_description`, `acceptance_criteria`, jne.) alkuun `Optional` tai sallivina arvoina. **Vanhaa litteää `ai_rule_description` -kenttää EI POISTETA vielä**. Tämä takaa, että vanha koodi ja UI toimivat yhä (Expand). Lisätään myös uusi "Kevyt JSON-uutto" -protokolla rutiiniaskeleille.
* **Vaihe 3 (Online Database Migration):** Rakennetaan taustaskripti (ETL), joka lukee tietokannasta (`seed_data.json`) vanhan `ai_rule_description`-kentän, luo LLM:n avulla sen pohjalta uudet rakenteelliset kentät ja tallentaa NE MOLEMMAT tietokantaan. Järjestelmää voidaan ajaa koko ajan.
* **Vaihe 4 (Frontend Sync & Routing):** Frontendin DTO:t synkronoidaan uusiin kenttiin ja Admin Studio V2 -UI päivitetään tukemaan uusia kenttiä rinnakkain vanhojen kanssa. Rakennetaan uusi Best-of-3 Flash reitityslogiikka.
* **Vaihe 5 (Schema Contract):** Vasta kun kaikki koodi osaa lukea ja kirjoittaa uusia rakenteellisia kenttiä, **poistetaan vanha `ai_rule_description` kokonaan** Backendin Pydantic-malleista, Frontendin DTO:ista ja tietokannasta. Pakotetaan uudet kentät pakollisiksi (Contract).

*(Huom: Kielellinen siivous ja rajatapausten määrittely on eriytetty omaksi jälkikokonaisuudekseen, jotta ydin-Epicin laajuus pysyy hallittavana ja Regressio-riskit minimoituvat.)*

## Tausta ja Ongelma (The Variance Crisis)
Analysoimme järjestelmän varianssia (Entropia 1.0) TDA-putkessa raskaiden matriisien osalta. Löysimme kolme kriittistä varianssilähdettä:
1. **Kielellinen ristiriita:** Nykyisessä tietokannassa (`seed_data.json`) tekoälyn PromptBlock-säännöt (`ai_rule_description`) on kirjoitettu yhtenä string-tekstinä, ja ne sisältävät fyysisiä ankkurisanoja englanniksi (esim. *"Find abrupt transition markers (e.g., 'therefore', 'thus')."*). Koska arvioimme suomenkielisiä tekstejä, kielimalli joutuu tekemään lennosta semanttista kääntämistä, mikä tuhoaa osumatarkkuuden erityisesti nopeilla ja halvoilla malleilla (Gemini 2.5 Flash), joita käytämme testeissä.
2. **Rajatapaukset (Boundary Cases) ja Systemaattiset Klusterit:** Empiirinen analyysi (EPIC 71) kahden identtisen ajon vertailussa paljasti Cohen's κ = 0.72 ("Substantial Agreement"), mutta myös 24 epävakaata atomia (13 % varianssi). Suurin osa näistä eroista syntyy rajatapauksissa, joille ei ole yksiselitteisiä hylkäyskriteereitä. Nämä jakautuvat systemaattisiin juurisyyluokkiin:
   - **Klusteri A (Sääntely-viittausten Domain-Scope):** Samat sääntely-viittaukset flippaavat eri konseptien välillä (esim. methodology link vs. formal citation), koska tarkkuustasoa (kuten sub-artiklojen vaatimista) ei ole määritelty.
   - **Klusteri B (Retorinen Reframing-Pattern):** Tekstien uudelleenkehystykset (esim. "not just X, but Y") tunnistetaan virheellisesti vasta-argumenteiksi tai synteeseiksi, vaikka kyseessä on pelkkä stilistinen tehokeino.
   - Kun tällaisille rajatapauksille ei ole määritelty eksplisiittisiä poissulkusääntöjä, LLM arpoo lopputuloksen kahden vaiheilla.
3. **Miellyttämishalu ja vahvistusvinouma (Confirmation Bias):** Kielimalleilla on luontainen "miellyttämishalu". Ne yrittävät etsiä osumia säännöille silloinkin, kun näitä ei ole, mikä lisää satunnaisuutta ja heikentää konsistenssia.

## Tavoite
1. Siirretään järjestelmä pois litteistä `string`-säännöistä ja otetaan säännöissä (`ai_rule_description`) käyttöön olemassa oleva globaali `I18nText` Pydantic BaseModel -rakenne. (HUOM: Pelkkä dynaaminen `dict`-alias ei ole sallittu, sillä se sallisi laittomat `.get()`-fallbackit ja ohittaisi rajapinnan Fail-Fast -validoinnin. Täysi luokka takaa tyyppiturvallisuuden ja pariteetin Flutterin Freezed-mallien kanssa).
2. **Tiukat negatiiviset poikkeukset (Boundary Disambiguation):** Määritetään säännöille tiukat negatiiviset poikkeukset (kuten Toulminin matriisissa: *REFRAMING EXCLUSION: ... If a reframing pattern is the only candidate, return JSON null*). Kun rajatapauksille annetaan eksplisiittinen sääntö poissulkemiseen, mallin ei tarvitse arpoa epäselvissä tilanteissa, vaan se palauttaa deterministisesti `null`.
3. **Nollahypoteesin pakottaminen (Null Hypothesis Priority):** Pakotetaan promptissa oletukseksi nollatila: *"Assume by default that no evidence exists. Return null unless you can extract a verbatim quote that strictly complies with the anchors."* Tämän ansiosta negatiiviset havainnot (jotka muodostavat suuren osan datasta) muuttuvat 100 % stabiileiksi, koska malli ei yritä väkisin luoda osumaa tyhjästä.
4. **Arkkitehtuurinen erottelu:** Erotetaan ohjeteksti, ankkurisanat, disambiguation-rajaukset ja nollahypoteesisäännöt toisistaan. `prompt_compiler.py` kokoaa ankkurit mekaanisina Pydantic-rajoitteina (Zero Semantic Drift) ja pakottaa poissulkusäännöt sekä nollahypoteesin LLM-promptiin, jotta malli ei ala tulkita rajatapauksia luovasti. Tämän avulla voimme tarjota säännöille täydelliset kohdekielen ankkurisanat erillisenä listana (esim. `syntactic_anchors: {"fi": ["siksi", "joten"]}`).

<!-- Phase 0 siirretty itsenäisiin työkokonaisuuksiin asiakirjan loppuun -->

## Phase 2: Schema Expand (Strukturoitu malli rinnalle)
> **Kriittinen Käsitteellinen Rajoitus (`ai_rule_description` vs `ai_description`):** Tämä refaktorointi koskee AINOASTAAN `TDAAssertion`-mallin `ai_rule_description`-kenttää. `PromptBlock`- ja `MatrixClaim`-mallien englanninkieliset `ai_description`-kentät pysyvät litteinä merkkijonoina, koska ne toimivat LLM:n ylätason ohjeina, eivätkä ne tarvitse rakenteellista jakoa. Älä muuta `ai_description`-kenttiä.
1. **Pydantic V2 Expand -muutokset:** LISÄTÄÄN tiedoston `backend_v2/models/v2_core.py` skeemaan `TDAAssertion` uudet rakenteelliset kentät **ilman, että poistetaan vanhaa `ai_rule_description`-kenttää vielä**. Kaikki uudet kentät asetetaan alkuun muotoon `Optional[...] = Field(default=None)`, jotta tietokannan luku ei kaadu. Uudet kentät ovat:
   - `concept_description: I18nText | None` (Mitä tekoäly etsii?)
   - `acceptance_criteria: I18nText | None` (Hyväksymiskynnys / Standard of Proof)
   - `anti_patterns: I18nText | None` (Hylkäyskriteerit / poikkeussäännöt)
   
   > **KRIITTINEN SÄÄNTÖ (NO BACKWARDS COMPATIBILITY FOR EXECUTIONS):** 
   > Taaksepäin yhteensopivuus koskee AINOASTAAN `seed_data.json`-määrityksiä koodin suoritettavuuden takaamiseksi siirtymän aikana. **Historiallisiin ajoihin (executions / historical runs) EI SAA OLLA taaksepäin yhteensopivuutta.** Pydantic-malleihin on ehdottomasti KIELLETTYÄ kirjoittaa `obj.get("ai_rule_description")` -tyyppisiä fallback-purkkapatentteja vanhojen ajojen tukemiseksi. Paikallinen ajotietokanta (TinyDB/Firestore) tyhjennetään kylmästi, ja vanhat ajot saavat (ja niiden pitää) kaatua Fail-Fast -virheeseen.

   > **Arkkitehtuurisääntö (hardening.xml):**
   > - Rule 1 (the_zero_compromise_pledge): No `.get("default")` fallbacks permitted in business logic. Strict Pydantic validation is absolutely mandatory.
   > - Rule 2 (strict_pydantic_v2_rust): Enforce `.model_validate()`, NEVER use the legacy `parse_obj()`. All NEW classes MUST define `model_config = ConfigDict(strict=True, extra="forbid")`.
   > - Rule 3 (fail_fast_hydration_mandate): All uncertain data flowing as dictionaries MUST be hydrated via `.model_validate()` IMMEDIATELY before processing.
   > - Rule 10 (pydantic_pure_hydration_boundary): Enforce `.model_validate(data, strict=False)` at the Database boundary, but strictly `ConfigDict(strict=True)` at the API boundary.
   > - Rule 22 (zero_legacy_fallback_hacks): Legacy fallback hacks are entirely unsupported. If requisite data is absent, the execution MUST trigger a Fail-Fast crash immediately.
   > - Rule 77 (zero_field_renaming_mandate): NEVER autonomously rename existing Pydantic model fields (esim. ai_rule_description -> concept_description). Renaming fields breaks database schema mappings and causes Fail-Fast validation errors downstream.
   > - Rule 84 (pydantic_schema_freeze_mandate): NEVER autonomously tighten or alter the structural types, `Optional` bounds (`| None`), or field signatures of any Pydantic models.
   > - Rules 54-58 (PEP 257 Google Style): Every module, class, and function MUST possess a PEP 257 compliant Google-style docstring. Function docstrings MUST specify Args:, Returns:, and Raises: blocks.
   > 
   > *System 2 Synkronisaatio-ohje:* Säännöt 77 ja 84 kieltävät tekoälyagenttia tekemästä **autonomisia** (itsenäisesti lennossa tapahtuvia) kenttien uudelleennimeämisiä tai rakennemuutoksia. Tämä Epic *ohittaa* kyseisen "autonomous"-rajoituksen, koska kyseessä on ihmisen hyväksymä, keskitetty arkkitehtuuritason Pydantic-muutos ja tietokantamigraatio. Agentin on kuitenkin noudatettava sääntöjä 1 ja 22 ehdottomasti: uusiin rakenteisiin siirryttäessä vanhan kentän taaksepäin yhteensopivuutta EI saa ylläpitää fallback-koodeilla.
   
   > **Huom:** Olemassa oleva `I18nText.validate_i18n()` -model_validator takaa, että `en`-käännös on aina olemassa (Fail-Fast ValueError). Prompt Compiler voi luottaa tähän eikä tarvitse omaa Fail-Fast -tarkistusta `en`-käännöksen olemassaololle. Lisäksi `backend_v2/hooks/atom_flattening.py` on lisättävä muokattavien listalle, sillä se käyttää `tda.ai_rule_description` kenttää tällä hetkellä; korvaa se `tda.concept_description.resolve("en")` ja `generate_atom_hash` korvataan `tda.tda_id`:llä.
2. **Syntactic Anchors & Pre-flight flags:** 
   - Lisää uusi kenttä `syntactic_anchors: dict[str, list[str]] | None = Field(default=None)` vastaaviin Pydantic-skeemoihin. Tämä pitää säännöt puhtaina ja sallii sanalistojen mekaanisen validoinnin.
   - Lisää uusi kenttä `enforce_pre_flight: bool = Field(default=False)` TDAAssertion-luokkaan.
   - Lisää uusi kenttä `is_lightweight_protocol: bool = Field(default=False)` `PromptBlock`-luokkaan, jotta kevyiden ja raskaiden analyysien reititys voidaan tehdä turvallisesti.
3. **Pre-Flight Fail-Fast -tarkistus (Kooditason Nollahypoteesi):** Ennen kalliin LLM-kutsun tekemistä ohjelma voi ajaa kohdetekstin kevyen säännöllisen lausekkeen läpi, joka tarkistaa `syntactic_anchors` -sanalistan esiintyvyyden.
   * **Enforce Pre-flight -kytkin (Opt-in):** Tämä tarkistus on ajettava **vain jos** `enforce_pre_flight` on asetettu arvoon `True`. Koska suomen kieli on erittäin rikas ja agglutinatiivinen, kova kooditason (regex) filtteri väistämättä hylkäisi taivutusmuotoja ja romahduttaisi osumatarkkuuden (recall collapse). Siksi oletusarvoisesti `enforce_pre_flight = False`, jolloin ankkurit syötetään vain LLM:lle osaksi system promptin sääntöjä, ja LLM (joka hallitsee suomen morfologian) tekee semanttis-syntaktisen ankkuritarkistuksen ilman kooditason short-circuitia.
   * Jos `enforce_pre_flight` on `True` ja ankkurit on määritelty, mutta yksikään ei esiinny tekstissä, palautetaan suoraan deterministinen `null` eikä LLM:ää kutsuta.
   * Raskaiden ulkoisten kirjastojen (kuten Voikko tai UralicNLP) käyttö backend-koodissa lemmatisaatioon on kielletty Windows-asennushazardien (windows_build_hazards) välttämiseksi.
   > **Arkkitehtuurisääntö (hardening.xml):**
   > - Rule 17 (the_duct_tape_ban): All file handles, network sessions, and external resources MUST be initialized via context managers. Banned: `except Exception: pass` and bare `try-except` blocks. Pre-Flight logiikan virheenkäsittely on suunniteltava tämän mukaan.
   > - Rule 18 (rfc7807_dual_reporting_strict): Within the `backend_v2/` directory scope, code MUST NOT raise raw `ValueError`, `HTTPException`, or standard `Exception` instances. All exceptions MUST be translated into Quorum's `AppException` schema (RFC 7807). Mandatory signature: `AppException(error_code=ErrorCodes.XYZ, message="...", status_code=...)`. DO NOT nest the error_code inside a `details` dict. Explicitly call `logger.error(..., exc_info=True)` prior to raising.
   > - Rule 89 (fail_fast_payload_length_mandate): Always enforce a strict minimum character length on extracted user text payloads BEFORE passing them to an LLM context window. Reject suspiciously short payloads (< 10 chars) via an explicit `AppException` to prevent the LLM from hallucinating answers over empty inputs.
4. **Prompt Compiler (Arkkitehtuurinen Kielen Eristäminen & Structured Prompt):** Päivitä `backend_v2/services/orchestrator/prompt_compiler.py`.
   > **Kriittinen System 2 Arkkitehtuurivaroitus (Cognitive Language Leak):**
   > LLM:n kognitiivinen päättelykyky on vahvimmillaan englanniksi (Rule 36). Jos Prompt Compiler syöttäisi LLM:lle `concept_description` tai `anti_patterns` -kentät käännettynä kohdekielelle (esim. suomeksi), mallin "älykkyys" romahtaisi (Intelligence Dropping). Siksi mallin ohjauslogiikka on AINA englanniksi, ja vain analysoitava data ja ankkurit ovat kohdekielellä.
    - **Kognitiivisen logiikan injektio (AINA ENGLANNIKSI) & Kielen pakotus:** Kääntäjän on purettava `concept_description`, `acceptance_criteria` ja `anti_patterns` -kentistä **ehdottomasti englanninkielinen (`"en"`) versio** (Fail-Fast, jos "en" puuttuu). Näistä muodostetaan LLM:n ohje: *"Goal: {concept_en}. Requirement: {criteria_en}. Warning: {anti_patterns_en}."*
      * **English Leakage -suojaus:** LLM-ohjeeseen on lisättävä tiukka kielellinen ohjeistus, jotta malli kirjoittaa `reasoning_trace`- ja `semantic_reasoning`-kentät täysin pyydetyllä kohdekielellä (esim. suomeksi) eikä ala vuotaa englantia vastauksissaan, mikä rikkoisi backendin kielellisen auditoinnin.
     > **Arkkitehtuurisääntö (hardening.xml):**
     > - Rule 29 (high_fidelity_prompting): Prompt core instructions MUST remain completely static to enable Prompt Caching. Dynamic execution variables MUST be isolated within an `<execution_parameters>` tag at the tail of the message. Avoid f-strings when formatting foundational core rules.
     > - Rule 36 (native_english_generation): Cognitive reasoning is formulated natively in English; UI localization is handled strictly in a downstream translation phase.
     > - Rule 51 (hybrid_prompting_mandate): System prompts MUST use a hybrid of XML for structural control and Markdown for nested content formatting.
     > - Rule 52 (ephemeral_caching_topology): System Prompts must remain 100% static to maximize ephemeral prompt caching hit rates on external LLM provider APIs.
     > - Rule 53 (role_segregation_and_fencing): Always fence untrusted user payloads with clear XML tags (e.g. `<user_input>...</user_input>`) to prevent prompt injection attacks during role segregation.
   - **Kohdekielen Ankkurien pakottaminen (Hard Constraints):** Ainoastaan `syntactic_anchors` -sanalista haetaan aktiivisen kohdekielen (`state.inputs.get("language")`, esim. "fi") perusteella. Kääntäjä injektoi kohdekieliset ankkurit englanninkielisen säännön lomaan: *"CRITICAL: The analyzed text is in {language}. You MUST find a match for at least one of these exact localized anchors: {anchors_fi}. If missing, return null."* **Jos vaadittua kohdekielen ankkurilistaa ei löydy `syntactic_anchors` -sanakirjasta, ajo on kaadettava välittömästi (Exception)**.
   - **Disambiguation-sääntöjen käsittely (Rajatapaukset):** Kääntäjän on poimittava `<disambiguation>`- tai `NEGATIVE BOUNDARY` -lohkot (jotka sisältyvät `anti_patterns` -kenttään) ja sisällytettävä ne oikeassa kieliversiossa LLM-prompissa. Nämä sisältävät tiukat poissulkusäännöt (kuten *REFRAMING EXCLUSION*), jotka ohjaavat mallin palauttamaan deterministisesti `null` epäselvissä rajatapauksissa ilman luovaa arvailua.
   - **Nollahypoteesin pakottaminen (Null Hypothesis Priority):** Kääntäjän tulee injektoida promptirakenteeseen ohjeistus siitä, että oletusarvona on nollahypoteesi (palautetaan `null`), ellei ankkurit täyttävää verbatim-lainausta löydy.
   - **Determinismin varmistaminen:** Asetetaan mallien kutsuparametrit (mukaan lukien Gemini 2.5 Flash) tiukasti deterministisiksi (`temperature = 0.0`, `top_k = 1`, `top_p = 0.0`).
   - **Rakenteinen dekoodaus (Structured Outputs API):** Pelkkä tekstuaalinen kehotemuotoilu ei estä stokastisuutta. Dynaamisesti generoitu Pydantic-skeema on injektoitava suoraan mallin API-kutsun `response_schema` -parametriin. Tämä kahlitsee mallin dekooderin matemaattisesti (Logit-tason maskaus) ja takaa, että vastauksen tietorakenne on 100 % validi eikä sisällä hallusinoituja kenttiä.
     > **Arkkitehtuurisääntö (hardening.xml):**
     > - Rule 28 (llm_structured_execution_mandate): Direct instantiation or calling of the `LLMClient` SDK is prohibited. All LLM inferences MUST be centralized and routed exclusively via `LLMTaskExecutor.execute_structured_task()`.
   - **Globaali Zero-Reasoning Mandate:** Injektoi uusi tiukka XML-sääntö, joka kieltää `<thought>`-lohkot ja askeleittaisen päättelyn mekaanisissa rutiinihauissa kokonaan. Zero-Reasoning Mandate -sääntö tulee injektoida suoraan `PromptCompiler`-luokkaan uutena staattisena XML-lohkona `compile_static_instructions`-metodiin tai erillisen `PromptBlock`-tietueen kautta tietokannasta.
   - **Dynamic Schema Pruning (LightweightExtractionAtom):** Jotta mallia ei tarvitse erikseen ohjeistaa jättämään raskaiden skeemojen (kuten `semantic_reasoning`) kenttiä tyhjäksi (mikä on virhealtista), otetaan laajemmin käyttöön jo olemassa oleva karsittu Pydantic-skeema `LightweightExtractionAtom` (tiedostossa `backend_v2/models/dtos/lightweight_matrix.py`). Siitä on poistettu "ajattelukentät", jolloin dekooderin kognitiivinen kuorma minimoituu.
5. **Prompt Factory Hash-päivitys & tda_id -pariteetti:** Päivitä `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`. Koska `ai_rule_description` poistetaan:
    - Varmistetaan, että järjestelmä käyttää aina ensisijaisesti staattista ja pysyvää `tda.tda_id` -tunnistetta (Opaque Stripe ID).
    - Poista `generate_atom_hash` kokonaan ja kiellä luonnollisiin avaimiin (kuten ihmisen kirjoittamaan tekstiin) perustuva fallback-hash-logiikka. Järjestelmän tunnisteiden (`tda_id`) on poikkeuksetta oltava UUID4-muotoisia (Opaque Stripe ID). Jos tunnistetta ei ole, sitä ei koskaan luoda tiivisteenä `concept_description`-kentästä (Surrogate Key Mandate).
   > **Arkkitehtuurisääntö (hardening.xml):**
   > - Rule 25 (opaque_stripe_id_mandate): Relational models MUST use opaque identifiers (e.g., `tda_123`). Raw sequential integers or predictable slugs are categorically forbidden.
   > - Rule 26 (md5_hashery_ban): hashlib.md5 and hashlib.sha1 are STRICTLY PROHIBITED for dynamic ID generation. Utilize `uuid.uuid4().hex`.
6. **Blacklist-sanakirjojen synkronointi ja RapidFuzz-toleranssi (Lightweight Matrix):** Päivitä `backend_v2/models/dtos/lightweight_matrix.py`. Varmista, että mahdolliset `evidence_found`-metodin käyttämät negatiiviset blacklist-sanastot synkronoidaan dynaamisesti `anti_patterns` tai `syntactic_anchors` -kenttien logiikan kanssa haamuhavaintojen estämiseksi. **TAVOITE:** Laske `fuzz.partial_ratio` -kynnysarvo nykyisestä 95.0 prosentista 85.0 prosenttiin. Tämä arkkitehtuuripoikkeus sallii suomen kielen runsaat taivutusmuodot (esim. "megatrendien kehityskulku" vs "megatrendit kehittyvät") menettämättä kuitenkaan nollahypoteesin edellyttämää fyysistä ankkuria, nostaen validien osumien määrää (recall). **SSOT Refaktorointi:** Koska arvo on nykyään kovakoodattu kahteen eri paikkaan (`lightweight_matrix.py` ja globaali pre-flight `integrity.py` -hookki), tämä kovakoodaus rikkoo Single Source of Truth -periaatetta. Uusi tavoitearvo on määriteltävä yhteisenä Enum-muuttujana (esim. `QuorumLexicalConfig.FUZZ_THRESHOLD_BILINGUAL = 85.0`), jota molemmat tiedostot käyttävät.
7. **Skeemojen dynaaminen injektointi (Zero-Bilingual Leak):** Vaikka koko `I18nText`-rakenne (kaikki kielet) palautetaan UI/Frontend -kerrokselle esitettäväksi asiantuntijoille, Prompt Compiler eristää kielet täydellisesti LLM:ltä. LLM:n konteksti-ikkunaan (ja Structured Outputs JSON-skeemaan) injektoidaan vain yksinkertainen englanninkielinen ohjenauha ja kohdekielinen ankkurilista. Malli ei koskaan näe koko monimutkaista kielirakennetta, jolloin promptin resoluutio ja Prompt Caching pysyvät täydellisinä.

## Phase 3: Online Tietokantamigraatio (Structured Seed Data Migration)

> **Expand & Contract Online Migration:**
> Koska vanha kenttä on yhä olemassa koodissa (Expand-vaihe), Pydantic ei kaadu lukiessaan vanhaa dataa. Siksi voimme ajaa datamigraation asynkronisena online-tilassa (tai tallentavana skriptinä) rikomatta koodikantaa. Uusi generoitu `seed_data.json` sisältää sekä vanhan `ai_rule_description` -kentän että uudet rakenteelliset kentät.

1. Koodaa Python-skripti (ETL), joka käy läpi koko olemassa olevan `backend_v2/seed/seed_data.json` -tiedoston. Skriptin on osattava navigoida syvälle oikeaan JSON-polkuun: `prompt_blocks` -> `scales` -> `claims` -> `tda_assertions` löytääkseen muokattavat kohteet. Skriptin tulee asettaa myös uuden `enforce_pre_flight` kentän oletusarvoksi `false`.
   > **Arkkitehtuurisääntö (hardening.xml):**
   > - Rule 59 (free_threading_concurrency): Utilizing the `multiprocessing` module is EXPLICITLY FORBIDDEN. Employ lightweight threads or `asyncio`.
   > - Rule 61 (taskgroup_exceptiongroup_mandate): In concurrent async execution, `asyncio.gather` is FORBIDDEN. Background routines MUST ALWAYS be orchestrated utilizing the `asyncio.TaskGroup` context.
   > - Rule 65 (pep750_t_strings_only): Construct dynamic LLM prompts exclusively utilizing Python 3.14 t-strings (Template Strings - PEP 750). Standard f-strings within data ingestion pathways are forbidden.
2. **Kattava 186 säännön konversio:** Tietokannassa (`seed_data.json`) on tarkalleen 186 kappaletta litteitä `ai_rule_description`-kenttiä. Skriptin tulee lukea jokainen `TDAAssertion`-objekti ja muuttaa se uuden strukturoidun mallin mukaiseksi:
   - **LLM-avustettu ETL (Extract, Transform, Load):** Vapaamuotoisen tekstin purkaminen rakenteelliseksi dataksi säännöllisillä lausekkeilla (Regex) on liian haurasta. Skriptin tulee käyttää Quorumin virallista LLM-rajapintaa (`LLMTaskExecutor.execute_structured_task()`), suorat `google-genai`-kutsut on kielletty (Sääntö 28). Jos käytetään rinnakkaisuutta API-kutsujen nopeuttamiseksi, skriptin on käytettävä `asyncio.TaskGroup` -rakennetta säännön 61 mukaisesti, multiprocessing on kielletty (Sääntö 59). Skripti syöttää vanhan `ai_rule_description` -tekstin LLM:lle, joka palauttaa suoraan uuden Pydantic-skeeman mukaisen JSON-objektin:
     - `concept_description`: Mitä sääntö etsii (esim. dogmaattisia väitteitä).
     - `acceptance_criteria`: Hyväksymiskynnys / milloin sääntö laukeaa. **SALLIVUUSTAVOITE (Tiered Permissiveness):** Monimutkaisille säännöille (esim. synteesit) ETL-skriptin tulee injektoida ehto: *"SALLITTU POIKKEUS: Jos konsepti on selvästi läsnä yli lauserajojen, saat käyttää contextual_override=true -lippua ilman tarkkaa sanasta sanaan -lainausta."* Tämä leipoo joustavuuden suoraan dataan rikkomatta koodin eheyttä.
     - `anti_patterns`: Negatiiviset poikkeukset ja rajatapaukset (esim. `NEGATIVE CONDITION` ja `<disambiguation>`-lohkot). **EHDOLLISET HYLKÄYKSET:** Älä muunna sääntöjä "välittömiksi hylkäyksiksi" jos ei ole pakko. Salli rajatapaukset (esim. vaillinaiset viitekehykset tai retoriset reframing-kuviot) sillä ehdolla, että malli kytkee `contextual_override` -lipun päälle ja pystyy perustelemaan laajemmasta kontekstista, miksi tapaus on validi.
     - `syntactic_anchors`: Säännön sisältämät merkkijonoankkurit listoina (esim. `{"en": ["is the best", ...], "fi": ["on paras", ...]}`). **KATTAVUUSTAVOITE:** Näistä ankkurilistoista on tehtävä äärimmäisen kattavia. ETL-skriptin/LLM:n on generoitava alkuperäisen ankkurisanaston lisäksi laaja joukko synonyymejä, tyypillisiä taivutusmuotoja ja kiertoilmauksia kummallakin kielellä. Koska järjestelmä käyttää nollahypoteesia (kaikki hylätään ilman fyysistä ankkuria), osumien määrän (recall) maksimointi edellyttää mahdollisimman rikasta `syntactic_anchors` -sanakirjaa.
     - **Surrogate Key Mandate (Opaque Stripe ID):** Skriptin on samalla tarkistettava `tda_id`. Jos vanha `tda_id` perustuu tekstin tiivisteeseen (hash) tai puuttuu, skriptin on korvattava se puhtaalla standardilla UUID4-tunnisteella. Luonnollisten avaimien käyttö on ehdottomasti kielletty.
   - **Ihmisvalidointi (Human-in-the-loop):** Koska LLM-migraatio saattaa hukata vivahteita, skriptin tulee tallentaa uusi tietokanta tilapäistiedostoon (esim. `seed_data_v2_draft.json`) ja pakottaa asiantuntija tekemään `diff` -tarkistus ja manuaalinen korjauskierros ennen sen siirtämistä tuotantoon.
   - Luo kullekin kentälle `LocalizedText` -rakenne, joka sisältää sekä englanninkielisen että suomenkielisen version käännettynä (esim. Toulminin ja Bloomin matriisien säännöille).
3. Aja skripti ja testaa `backend_audit_loop.py` -työkalulla, että seed data on validia uusilla Pydantic-säännöillä.
   > **Arkkitehtuurisääntö (hardening.xml):**
   > - Rule 35 (single_source_of_truth_mandate): Ruthlessly purge deprecated V1-era fallback hacks, `.get()` coalescing chains, and `@model_validator` retrofits handling legacy data payloads. The execution environment MUST trust V2 schemas implicitly (100%).
   > - Rule 74 (polymorphic_parsing_mandate): All Data Access Layer (Repository) methods MUST return raw `dict[str, Any]` to embrace NoSQL polymorphism. DO NOT enforce or return strict Pydantic DTOs at the database repository boundary. When external database clients (like Firestore or TinyDB) return `Any`, you MUST explicitly wrap the return value with `typing.cast(dict[str, Any], result)` to satisfy MyPy strict mode.
   > - Rule 76 (strict_attribute_integrity): Strict Attribute Integrity & Anti-Defensive Guardrail: NEVER alter existing string prefixes (e.g. changing `prov_` to `provider_`), as they are often tied to strict regex validations. NEVER convert strict dot-notation attribute access (e.g. `model.model_name`) into dynamic `getattr(model, "model", "")` fallbacks. Embracing the Fail-Fast protocol requires relying on Pydantic's static structure; defensive programming that subverts static typing is strictly FORBIDDEN.
   > - Rule 79 (pydantic_validation_bypass_ban): Pydantic Validation Bypass Ban: NEVER use `dict(model)` or list comprehensions that cast Pydantic objects into raw dictionaries (e.g., `[dict(m) for m in models]`) when rebuilding collections. ALWAYS use `model.model_copy()` or instantiate the target DTO explicitly. Bypassing strict validation by injecting raw dictionaries into Pydantic models via `.model_copy(update=...)` is STRICTLY FORBIDDEN as it causes runtime AttributeErrors during downstream attribute access.
   > - Rule 80 (setdefault_hydration_mandate): Dictionary Hydration Mandate: When safely injecting fallback or configuration values into a dictionary (such as `**kwargs`), you MUST utilize Python's native `dict.setdefault("key", value)` method. Constructing complex conditional logic (e.g., `if "key" not in kwargs: kwargs["key"] = value`) is strictly PROHIBITED as it violates the anti-defensive guardrail philosophy.
4. **Kevyen poimintaprotokollan luonti (`blk_lightweight_extract_01`):** Tietokantaan luodaan uusi PromptBlock, joka kieltää 5-vaiheisen lokituksen ja vaatii vain mekaanisen uuton ("Kevyt JSON-uutto"). Samaan lohkoon pakotetaan yksi validi JSON-esimerkki (Few-Shot), jotta halvat mallit (esim. Gemini 2.5 Flash) noudattavat muotoa täydellisesti. Tämän jälkeen päivitetään rutiiniaskeleet (kuten `step_input_processing` `extraction_protocol_block_id`) osoittamaan tähän uuteen lohkoon vanhan raskaamman Zero-Trust -lohkon sijaan.
   > **Tietokannan päivityskohde:** Lisää `seed_data.json` -tiedoston `prompt_blocks` -taulukkoon uusi lohko:
   > ```json
   > {
   >   "id": "blk_[uuid4_hex]",
   >   "slug": "lightweight_extract_protocol",
   >   "label": {"default_locale": "fi", "translations": {"fi": "Kevyt JSON-uutto", "en": "Lightweight JSON Extraction"}},
   >   "description": {"default_locale": "fi", "translations": {"fi": "Kevyt nollahypoteesi-uutto", "en": "Lightweight null hypothesis extraction"}},
   >   "ai_description": "ZERO-REASONING MANDATE: Extract data mechanically without step-by-step reasoning...",
   >   "category_id": "execution_persona",
   >   "type": "instruction",
   >   "is_lightweight_protocol": true
   > }
   > ```
5. **Kriittinen korjaus (Matrix Type Sync Validation):** Aiempi oletus, että matrix-lohkojen `type` olisi virheellisesti `"instruction"`, on tarkistettu dataa vasten ja havaittu vääräksi. Matrix-lohkot (`category_id == "matrix"`) palauttavat numeerisia arvosanoja (esim. 1-5, `allow_decimals: true`), joten niiden `type` on jo tällä hetkellä oikein `"float"`. Skriptin ei pidä mennä muuttamaan näitä `"string"` tai `"instruction"` tyyppisiksi, jotta numeerinen validointi ei rikkoudu. Varmista vain, että `execution_persona` -tyyppiset lohkot säilyttävät `type: "instruction"`.
6. **Testien ja Mock-datan päivittäminen:** Koska fallback-logiikka ei ole sallittua (Hardening Rule 22), kaikki yksikkö- ja integraatiotestit, jotka pohjautuvat vanhaan `ai_rule_description` -kenttään, rikkoutuvat välittömästi. Etsi kaikki testitiedostot ja fixturet, ja refaktoroi testien käyttämä Mock-data vastaamaan uutta Pydantic-skeemaa (LocalizedText-kentät). Tämä on kriittinen askel ennen testiluuppien (`backend_audit_loop.py`) ajamista.
   - **Kriittinen Testi-Gap:** Päivitettävät kohteet: `backend_v2/llm/mock_data.py` (Rivi 360 rakentaa litteän TDA-diktiä, tämä on rakennettava täydeksi lokalisaatiorakenteeksi, muuten `backend_audit_loop.py` kaatuu), `backend_v2/tests/unit/test_hashing.py` (POISTETTAVA KOKONAAN), `backend_v2/tests/unit/hooks/test_scoring.py` (Korvaa kaikki 13 `generate_atom_hash` -kutsua staattisilla `tda_123` UUID-tunnisteilla, hashien käyttö luonnollisille avaimille on arkkitehtuurisesti kielletty), ja itse `backend_v2/utils/hashing.py` (POISTETTAVA KOKONAAN).

## Phase 4: Frontend Sync & Routing

> **Expand & Contract UI Sync:**
> Koska koodikanta ei ole rikki, voimme lisätä Flutterin puolelle uudet kentät rinnakkaisena päivityksenä. Kun UI pystyy tallentamaan ja lukemaan kumpaakin formaattia, UI voidaan kytkeä uusiin rakenteellisiin kenttiin.

1. Päivitä Flutter-client (`client_app_v2`): Välitön Dart/Freezed DTO -mallien Expand-päivitys.
   - **Säilytä** `aiRuleDescription` Flutterin `TDAAssertion` -Freezed-mallissa väliaikaisesti. LISÄÄ uudet `I18nText` ja `syntacticAnchors` -kentät `Optional` muodossa (`?`) vastaamaan Backendin Pydantic Expand-muutoksia.
   - **Kriittinen Pariteettikorjaus:** Lisää Flutterin `PromptBlock` -Freezed-malliin kenttä `isLightweightProtocol` vastaamaan Backendin luomaa reitityslippua.
   - **Pariteettivian korjaus:** Huomaa, että Flutterin `TDAAssertion.evaluationTrack` oletusarvo on tällä hetkellä `EvaluationTrack.extractiveSensor`, mutta Backendin oletusarvo on `COGNITIVE_JUDGEMENT`. Korjaa tämä pariteettivika synkronoimalla oletusarvo.
   - Aja `dart run build_runner build -d` ennen minkään UI-muutoksen koodaamista, jotta verkkokerroksen deserialisointi saadaan stabiiliksi.
2. Etsi UI-komponentit, joissa hallinnoidaan PromptBlockien arviointisääntöjä (entinen `ai_rule_description`). Näihin kuuluvat erityisesti `client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart` ja `client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart`.
3. Korvataan vanha singular-tekstikenttä kokonaan **Structured Prompt Editor** -rakenteella:
   > **Arkkitehtuurisääntö (hardening.xml):**
   > - Rule 40 (no_string_l10n): Hardcoded display strings within the backend are strictly prohibited. Always reference designated Enum keys for UI text.
   > - Rule 44 (cross_language_enum_parity): Pydantic `Enum` and `Literal` definitions MUST maintain absolute strict parity with their Flutter client counterparts.
   - Luodaan erilliset `LocalizedTextInputWidget` -syöttökentät kullekin osiolle: Concept Description, Acceptance Criteria, Anti-patterns ja Contrastive Example.
   - Luodaan oma tagi-syöttökenttä tai lista-editori `syntactic_anchors` -ankkurisanoille.
4. Varmista, että De-Generator -arkkitehtuuri ja Red Screen Mitigation -säännöt pätevät (esim. Map.from() käyttö käännöksien iteronnissa).

## Itsenäiset Työkokonaisuudet (Irrotetut Epic-osuudet)

Seuraavat kokonaisuudet on eristetty ydin-Epicistä (Phase 1-3) Regression Parityn suojelemiseksi ja Blast Radiuksen pienentämiseksi. Nämä voidaan ja pitää suorittaa ominaan irrallaan tietokanta/Flutter-rajapinnan God Commitista.

### Ennakko-Epic A: God Object -purku (Entinen Phase 0)
**Suoritettava ENNEN Pydantic-skeemamuutoksia (Phase 1-3).**
Ennen uusien kieli- ja ankkuriominaisuuksien lisäämistä `backend_v2/services/orchestrator/prompt_compiler.py` (joka on paisunut lähes 900 rivin kokoiseksi) on pilkottava pienempiin, loogisiin vastuualueisiin Single Responsibility -periaatteen mukaisesti. Täysin nykyisillä Pydantic-malleilla (ai_rule_description pysyy toistaiseksi stringinä).

> **Arkkitehtuurisääntö (hardening.xml):**
> - Rules 54-58 (PEP 257 Google Style): Every module, class, and function MUST possess a PEP 257 compliant Google-style docstring. Function docstrings MUST specify Args:, Returns:, and Raises: blocks.
1. **Schema Factory:** Erota Pydantic-skeemojen dynaaminen rakentaminen omaan moduuliinsa (esim. `schema_factory.py`).
2. **Localization & Anchor Utils:** Luo erillinen palvelu (esim. `localization_compiler.py` tai funktioita uuteen tiedostoon) pelkästään käännösten purkamiselle, litteiden stringien injektoinnille ja tulevien listojen validoinnille.
3. **Pääkompilaattorin rakenteellinen uudelleenkirjoitus (Zero-Bilingual Leak):** Jätä `PromptCompiler` puhtaasti ylätason orkestroijaksi, joka vain delegoi käännöstyöt ja skeemojen generoinnin alimoduuleilleen. **Kriittinen System 2 Gap-korjaus:** Vanha `compile_xml_rubrics` ei voi enää yhdistää sääntöjä litteäksi tekstiksi. Metodi on koodattava täysin uusiksi siten, että se injektoi englanninkieliset kognitiiviset ohjeet (`concept_description.resolve("en")`) ja kohdekieliset ankkurit täysin erillisiin XML-tageihin, jotta kielimalli ei koskaan näe rakenteellista "Semantic Driftiä".
4. **Spatial Slicing & Chronology:** Refaktoroitava `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py` tiedoston `apply_spatial_slicing` -metodi joustavammaksi.

> **Arkkitehtuurisääntö (hardening.xml):**
> - Rule 88 (srp_god_method_mandate): Break down massive God Methods. Extract distinct logical blocks into isolated private helper methods to uphold the Single Responsibility Principle and allow modular testing.
> - Rule 47 (prompt_compiler_immutability): The core logic within `prompt_compiler.py` is locked and static. DO NOT mutate it with ad-hoc patches.
> - Rule 75 (zero_truncation_pledge): NEVER truncate existing methods, classes, or complex implementations into `pass` stubs.
> - Rule 81 (data_parsing_preservation_mandate): NEVER modify existing data extraction, dictionary traversal, or string concatenation algorithms. Do not attempt to "simplify" working data parsing loops.
> 
> *Refaktorointiohje & System 2 Synkronisaatio:* Rule 88 vaatii God Objectin pilkkomista, mutta Rule 47, 75 ja 81 kieltävät alkuperäisen logiikan ad-hoc muuttamisen ja yksinkertaistamisen. Pilkkominen on toteutettava siten, että **siirretään olemassa oleva koodi sellaisenaan** (data_parsing_preservation) uusiin moduuleihin (SRP), ja ylläpidetään 100 % toiminnallinen ja tuloksellinen vastaavuus (regression parity). Muutokset on vahvistettava vertaamalla tuotettuja promptirakenteita ennen ja jälkeen pilkkomisen.
>
> **Tier 1 Planner -ohje:** Tämä Epic ohittaa Rule 47 (prompt_compiler_immutability) tältä osin, koska kyseessä on SRP-pilkkominen (Rule 88), jossa olemassa oleva logiikka siirretään sellaisenaan uusiin tiedostoihin ilman algoritmista muutosta. Agentti EI saa tulkita tätä Rule 47 -rikkomuksena. Käyttäjä on hyväksynyt tämän muutoksen etukäteen.

### Jälki-Epic B: Kielellinen siivous & Rajatapaukset (Entinen Phase 4)
**Suoritettava KUN Phase 1-3 on vakaasti tuotannossa.**
1. Kun arkkitehtuuri on tuotannossa, käydään läpi kaikki raskaiden matriisien säännöt.
2. Hienosäädetään suomen- ja englanninkieliset strukturoidut kentät ja poistetaan kaikki semanttisesti epämääräiset ilmaukset. Varmistetaan, että suomenkielisen säännön ankkurit vastaavat täsmällisesti suomenkielisissä teksteissä käytettäviä ilmauksia (Zero Semantic Drift).
3. **Poissulkusääntöjen (Disambiguation) implementointi (EPIC 71 Integraatio):** Viedään tunnistetut systemaattiset korjaukset suoraan uuteen strukturoituun `anti_patterns` -kenttään:
   - **Klusteri A (Sääntely-scope):** Määritetään sääntö, jonka mukaan *"Regulatory framework references count as formal citations ONLY if a specific sub-article, clause, or numbered principle is cited. Generic mentions DO NOT satisfy conditions."*
   - **Klusteri B (Reframing Exclusion):** Määritetään sääntö, jonka mukaan *"Rhetorical reframing patterns (e.g., 'not just X, but Y') are STYLISTIC DEVICES, not argumentative structures. Do NOT extract them as counter-arguments or dialectical syntheses."*
   - Kun rajatapauksille (kuten yllä mainitut) annetaan eksplisiittiset ja lokalisoidut hylkäyskriteerit `anti_patterns` -kentässä, malli ei arvo kahden vaiheilla, vaan palauttaa stabiilisti `null` kaikilla ajokerroilla. Tavoitteena on nostaa luotettavuus (Cohen's κ) yli 0.85 tason.

## Phase 5: Schema Contract & Best-of-Three Routing

**Suoritetaan vasta kun Phase 1-4 ovat ajossa ja luotettavia.**
Tämä vaihe siivoaa "Expand" jäänteet ja poistaa litteän merkkijonon. Lisäksi reitityslogiikka viimeistellään kokonaisuudessaan.

### Contract (Cleanup)
1. **Pydantic Hardening:** Poistetaan `ai_rule_description` TDAAssertion Pydantic -mallista. Muutetaan uudet strukturoidut kentät pakollisiksi (`Optional` -> vaadittu) niiltä osin kuin se on liiketoimintalogiikassa tarpeen.
2. **Tietokannan siivous:** Siivotaan `seed_data.json` poistamalla vanhat litteät kentät.
3. **Flutter Hardening:** Poistetaan `aiRuleDescription` Freezed-malleista.

### Kognitio-Reititys ja Best-of-Three Flash
1. **Reitityslogiikka:** Järjestelmän tulee ohjelmallisesti suojella syväanalyysien laatua estämällä kevyen protokollan käyttö väärissä paikoissa:
   - *Mekaaninen tiedonhaku:* Käytetään uutta Kevyttä protokollaa + nopeaa Flash-mallia + `LightweightExtractionAtom` -skeemaa (säästää rahaa ja aikaa poistamalla reasoning-tokenit).
   - *Syväanalyysi (esim. Kahneman, Bloom jne.):* Kielletään Kevyt protokolla. Pakotetaan "Globaali Zero-Trust" (5-vaiheinen lokitus on sallittu/pakotettu) ja reititetään raskaammalle Pro-mallille + alkuperäiselle isolle skeemalle, sillä näissä tehtävissä kognitiivisia "reasoning"-tokeneita on pakko käyttää oikeellisuuden saavuttamiseksi.
2. **Best-of-Three Rinnakkaisajo (TaskGroup) ja High_Entropy-karsinta (EPIC 77 Integraatio):** Koska rutiinipoiminnoissa siirrytään Gemini 2.5 Flash -malliin, sen matalampaa älykkyyttä kompensoidaan arkkitehtuuritasolla siirtymällä **Best-of-Three (2/3) -rinnakkaisajoon**. **KRIITTINEN KORJAUS:** Aiemmin ensemble laukesi `chunk_worker.py`:ssä vain atomeille, joiden `high_entropy` oli True. Koska `TDAAssertion`-mallissa ei tällaista kenttää ole, ensemble ei koskaan lauennut. Poista tämä `high_entropy`-gateway kokonaan koodista. Kunkin lightweight-suorituslohkon rutiiniarviointi käynnistää AINA 3 rinnakkaista Flash-kutsua asynkronisesti `asyncio.TaskGroup` -rakenteella, rajoitettuna globaalilla `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)` -semaforilla API-rajojen suojelemiseksi (Sääntö 32). Tämä eliminoi yksittäisen API-aikakatkaisun (1/3) aiheuttaman koko askeleen kaatumisen.
3. **Leksikaalinen auditointi, Enemmistöpäätös ja Minority Veto:** 
   - Jokaisen ajon palauttama sitaatti (`exact_quote`) auditoidaan fyysisesti kohdetekstiä vasten käyttämällä sumeaa hakua (`RapidFuzz`) normalisoiduista teksteistä, jotta sallitaan pienet poikkeamat. Säännön 20 (`the_self_healing_ban`) mukaisesti dynaaminen säännöllisillä lausekkeilla (Regex) korjailu on kielletty, mutta leksikaalinen joustavuus (esim. `fuzz.partial_ratio`) Pydantic-validointirajapinnassa on sallittua ja suositeltavaa. Hallusinoidut sitaatit hylätään heti (`FAIL`).
   - Järjestelmä laskee konsensuksen: Jos vähintään 2/3 ajoa palauttaa `PASS` ja validin sitaatin, lopputulos on `PASS`. Muuten `FAIL` (tai `DLQ` jos 2/3 päätyy Contextual Overrideen). Laske samalla `confidence`-arvo mallin epävarmuuden mittaamiseksi (3/3 = 1.0, 2/3 = 0.67, 1/3 tai DLQ = 0.33) ja tallenna se `LightweightExtractionAtom`-tulokseen.
   - **Minority Veto (KRIITTINEN LISÄYS):** Jos yksikin ajoista palauttaa `FAIL` ja sen `semantic_reasoning` viittaa eksplisiittiseen `anti_pattern` -rikkomukseen, tämä `FAIL` kumoaa muiden ajojen `PASS`-tuloksen ja voittaa aina. Tämä mekanismi estää systemaattisen vahvistusvinouman (Confirmation Bias) monistumisen enemmistöpäätöksessä.
4. **Prompt Caching -hyödyt:** Vaikka kutsuja on kolme, Vertex AI:n Prompt Caching -mekanismin ansiosta identtisen syötteen kustannus putoaa toisessa ja kolmannessa ajossa merkittävästi. Tällä taataan **98 % konsistenssi** halvalla hinnalla.

## System 2 Kooditason ja Hardening-sääntöjen Synkronoinnin Analyysi (Audit)
Tämä analyysi on suoritettu peilaamalla Epic-dokumenttia puhtaasti `c:\src\quorum\scripts\hardening.xml` -säännöstöön ja olemassa olevaan koodipohjaan (`v2_core.py`, `prompt_compiler.py`, `lightweight_matrix.py`).

**1. Ovatko hardening ohjeet upotettu aidosti kokonaan?**
Alkuperäinen Epic huomioi Fail-Fast (Rule 1, 3, 22), Strict Pydantic (Rule 2) ja Native English (Rule 36) -säännöt hyvin. Kuitenkin arkkitehtuurin pilkkomiseen (SRP), sumeaan hakuun ja rinnakkaisajojen rajoitteisiin liittyvä kehys vaati korjauksia. Epicciin on nyt upotettu:
* **Sääntö 88 (SRP God Method) vs Säännöt 47, 75, 81:** `prompt_compiler.py` -tiedoston (1019 riviä) pilkkominen on paitsi sallittua, myös *pakollista* säännön 88 mukaan, mutta se täytyy tehdä noudattaen sääntöjä 47 ja 81 (Zero-Truncation ja Data Parsing Preservation), mikä tarkoittaa olemassa olevan koodin mekaanista siirtämistä uusiin tiedostoihin ilman algoritmista "parantelua".
* **Sääntö 20 (The Self Healing Ban):** Dynaaminen korjailu säännöllisillä lausekkeilla on kielletty, mutta RapidFuzz-kirjaston käyttö leksikaalisessa auditoinnissa on vahvistettu sallituksi arkkitehtuuripoikkeukseksi Pydantic-rajapinnassa, jotta vältetään turhat hylkäykset morfologisten erojen takia.
* **Säännöt 32 ja 28 (System Concurrency & LLM Structured Mandate):** Rinnakkaisajojen rajoittamiseen on pakko käyttää `SystemConcurrency.MAX_CONCURRENT_LLM_STEPS` -semaforia. Lisäksi ETL-skriptien on käytettävä `LLMTaskExecutor.execute_structured_task()` -rajapintaa; suorat `google-genai` -kutsut on kielletty.
* **Säännöt 77 ja 84 (Zero Field Renaming & Schema Freeze):** Säännöt kieltävät kenttien omatoimisen uudelleennimeämisen (esim. `ai_rule_description` poistaminen). Tähän on luotu System 2 -tason oikeutus: säännöt kieltävät *autonomisen* sooloilun, mutta tämä Epic edustaa virallista, etukäteen hyväksyttyä tietokanta- ja skeemamigraatiota (Atomic Commit), joten arkkitehtuurimuutos on sääntöjen mukainen, kunhan taaksepäin yhteensopivia purkkaratkaisuja ei jätetä (Sääntö 22).

**2. Ovatko ohjeet noudatettavissa ja kohdistuvatko ne oikeisiin paikkoihin?**
Kyllä. Koodianalyysi vahvistaa, että:
* `backend_v2/models/v2_core.py` sisältää `TDAAssertion` -luokan, jolla todella on `ai_rule_description` kenttä (löytyy rivin 191 tuntumasta).
* `LightweightExtractionAtom` todella on olemassa tiedostossa `backend_v2/models/dtos/lightweight_matrix.py` (rivillä 102), ja se on rakenteeltaan karsittu (Zero-Reasoning Mandate -yhteensopiva).
* Ristiriita `category_id == "matrix"` lohkojen osalta on todennettu: Pydanticissa tyyppi on `LaxBlockDataType` (float/int/string), joten matriisien numeerinen arvo säilyy `float`:na ja Epicin varoitus pitää paikkansa.
* `prompt_compiler.py` tekee massiivista iterointia (`compile_xml_rubrics` yms.), jonka siirto erilliseen `localization_compiler.py` -moduuliin osuu suoraan God Object -ongelman ytimeen.

**3. Onko koodi muutettavissa hardening ohjeiden mukaan ja mikä on vaikutus?**
Koodi on täysin muutettavissa turvallisesti **Expand & Contract** -mallin ansiosta. Koska `ai_rule_description` pidetään mukana, koodi ja testit säilyvät "100% executable" koko migraation ajan.
* "God Commit" vältetään pilkkomalla muutos rinnakkaisiin askeliin, jotka eivät riko tuotantoa.
* Vaikutus ulottuu välittömästi Flutter-sovelluksen Freezed DTO -malleihin, mutta taaksepäin yhteensopivuus takaa (Expand-vaiheessa), että deserialisointi ei kaadu.

## Huomioita Tier 1 Plannerille
- Tämä Epic leikkaa Frontendin, Backendin ja Data-kerroksen välistä rajapintaa massiivisesti.
- **Arkkitehtuurinen suojelu:** Suojele Pydantic V2 sääntöjä (Rule 1, Rule 2) ehdottomasti. Älä anna agenttien generoida `.get()`-ketjuja siirtymäkauden helpottamiseksi.
- Kaikki testit (`backend_audit_loop.py` ja `flutter_audit_loop.py`) on läpäistävä täysin nollavirheellä arkkitehtuuri-inkongruenssien estämiseksi. Varmista, että unit-testien käyttämät mock-datat päivitetään samalla.
- Mallin itse-konsistenssia ja Zero-Reasoning Mandaten toimivuutta (kustannussäästö ja token-vähennys) voidaan arvioida olemassa olevalla [`scratch/diff_executions.py`](file:///c:/src/quorum/scratch/diff_executions.py) -työkalulla suorittamalla rinnakkaisia evaluointeja.

## Liite A: Vaiheen 1 Jälkeinen Varianssianalyysi ja Mittausraportti (11.6.2026)

**Mittauksen tulokset:**
Suoritetun `diff_executions.py` -ajon tulokset kahden identtisen syötteen välillä (exe_3a489bf... vs exe_3f5380c...) vahvistivat kriittisen varianssin olemassaolon.
- **Varianssi:** 19.2 %
- **Cohen's Kappa:** 0.4979 (Vastaa arviota "Moderate/Weak Agreement", lähes satunnainen huojunta)
- **Osumien suunta:** 29 atomia flippasi FAILED -> PASSED, kun taas vain 6 flippasi PASSED -> FAILED.

**Miksi näin isot erot?**
Vaihe 1 (God Object Refactor) pilkkoi ainoastaan Python-koodin luokkia (SRP-refaktorointi). Järjestelmä käyttää edelleen vanhaa tietokantaa ja litteitä englanninkielisiä merkkijonosääntöjä (`ai_rule_description`). Kun LLM joutuu lennosta tulkitsemaan englanninkielisiä sääntöjä (esim. *"Find absolute words (e.g., 'always', 'never')"*) suomenkieliseen kohdetekstiin, se joutuu arpomaan semanttisia vastineita. Tämä yhdistettynä LLM:n luontaiseen miellyttämishaluun (Confirmation Bias) saa mallin "hallusinoimaan" osumia epäselvissä rajatapauksissa.

**Saadaanko Epicin loppuunsuorituksen jälkeen enemmän atomeita PASS-tilaan?**
**Ei.** Todennäköisesti PASS-tilojen määrä *laskee*, mutta jäljelle jäävät osumat muuttuvat 98 % vakaiksi. Nykyinen 29 FAILED->PASSED -hyppy paljastaa, että LLM yrittää epätoivoisesti löytää osumia pakottamalla rajatapaukset läpi. Kun Epicin uusi Pydantic-arkkitehtuuri, *Nollahypoteesin pakottaminen* (Null Hypothesis Priority) ja kohdekieliset ankkurilistat (`syntactic_anchors: {"fi": [...]}`) astuvat voimaan, järjestelmä hylkää säälimättä kaikki tapaukset, joista puuttuu fyysinen ankkuri. Tavoitteena ei ole maksimoida osumia, vaan eliminoida kaikki "väärät positiiviset" ja saavuttaa deterministinen luotettavuus (Cohen's Kappa > 0.85).

**Muutosehdotukset Epiciin:**
Mittausdata tukee sataprosenttisesti Epicin alkuperäistä hypoteesia (The Variance Crisis). Itse arkkitehtuurisuunnitelmaan ei tarvitse tehdä muutoksia. Epicin tavoitteet ja "Expand & Contract" -migraatiovaiheet (Vaiheet 2-6) ovat juuri se lääke, joka korjaa tämän havaitun 19.2 % varianssin. 
Ainoa toimenpide on jatkaa välittömästi Vaiheen 2 (Kognitio-Reititys ja Best-of-Three Flash) toteutukseen, joka tuo mukanaan rinnakkaisauditoinnin ja enemmistöpäätöksen hylkäämään nämä FAILED->PASSED -hallusinaatiot.
