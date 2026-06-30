# ** EPIC: Prompt Centralization & Hybrid Output Protocol (SDUI)**

## ** Tavoite**

Poistaa koodiin kovakoodatut LLM-kielisäännöt (directives.py, linguistic.py) ja siirtää LLM:n ohjaus täysin tietokantaan (OutputProfile). Otetaan käyttöön **Hybrid Output -protokolla**, jossa ohjausdata (enumit, labelit) tuotetaan JSON/Structured Outputs -muodossa ja pitkät vapaamuotoiset tekstit/lainaukset XML-tageissa syntaktisen haurauden (esim. karkaamattomat lainausmerkit) välttämiseksi. Tämä takaa Graceful Degradation -periaatteen säilymisen yhdistettynä Pydanticin Zero-Compromise -validointiin.

## ** ARKKITEHTONINEN VIITEKEHYS JA LAATUPERIAATTEET (Hardening-viitekehys)**

Tämän Epicin toteutuksessa noudatetaan Quorum V2:n tiukkaa laadunvarmistuksen ideologiaa. Kaikki tehtävät koodimuutokset suunnitellaan ja suoritetaan seuraavien periaatteiden mukaisesti:

### **Arkkitehtoninen Periaate: Episteemiset Rajat (Epistemic Boundaries)**
Järjestelmä on jaettu tiukasti kahteen osaan sen perusteella, mikä on todennäköisyyksiin perustuvaa (LLM) ja mikä on determinististä (koodi).
* **System 1 (Probabilistic LLM Inference - The Fuzzy Boundary):** Tekoälyn vastuulla on semanttinen päättely, oikeiden viitteiden uuttaminen kontekstista ja sävyn (tone of voice) säätely. Näitä ei voi taata matemaattisesti. Tästä syystä tekoäly tuottaa raskaan tekstin sille luontaisessa Markdown-muodossa, välttäen jäykän JSON-syntaksin globaalin haurauden.
* **System 2 (100% Deterministic Python Logic - The Hard Boundary):** Backendin "Ingestion Boundary" vastaa rakenteen pakottamisesta (Pydantic), viiteavaimien deterministisestä kääntämisestä (DOC-1 -> doc_xyz) tilakartan avulla ja virheiden hallitusta degradaatiosta. System 2 ei "arvaa" koskaan.

### **Suunnittelumalli: Tolerant-Read / Strict-Write Airlock Pipeline (Universal Ingress)**
Toteutamme Quorum V2:n datan vastaanoton, validoinnin ja vikasietoisuuden (Graceful Degradation) neljän ilmalukon (Airlock) mallilla:
1. **Airlock 1: The Universal Ingress Pipeline (Tolerant-Read & Syntax Healing):** Keskitetty, yleiskäyttöinen putki (esim. `ingress_pipeline.py`). Ennen `model_validate()`-kutsua raaka LLM-output (JSON ja/tai Markdown) kulkee esipuhdistajan läpi. Tämä korjaa lokaalit syntaksivirheet (puuttuvat sulkeet) ja hydratoi Token Compressionin vuoksi käytetyt **Positional Array Ingress** -tuplet (`["DOC-1", "..."]`) automaattisesti takaisin sanakirjoiksi. Se ei ota kantaa liiketoimintalogiikkaan.
2. **Airlock 2: Pydantic Shield & Semantic Paraphrase Prevention (Strict-Write):** Puhdistettu data hydratoidaan spesifiseen Pydantic-malliin (esim. `LLMExtractedQuote`). Tässä vaiheessa **Domain Sovereignty** säilyy: mallin omat `@model_validator`-metodit ajavat lainauksille `AnchorValidationService.calculate_fuzzy_score()` -tarkistuksen. Tämä estää tekoälyn semanttiset hallusinaatiot (kuten "shall" -> "must") ohittamasta tarkistuksia. Configin `extra='ignore'` leikkaa muun luvattoman datan.
3. **Airlock 3: The Translation Firewall:** Aliaksien deterministinen käännös (esim. `AliasRegistry`) lukitun tilakartan avulla. Luvalliset aliakset (DOC-1) muuttuvat oikeiksi viitteiksi (Opaque Stripe ID), virheelliset nollataan hiljaisesti (Degradation Logistics).
4. **Airlock 4: Human-in-the-Loop Shadowing:** Ihmisen tekemät muutokset (`HumanOverrideDTO`) on täysin eriytetty tekoälyn datasta (Forensic Sovereignty). Matematiikkamoottori on puhdas funktio, joka on irti kytketty (Event-Driven) raskaista UI-säikeistä.

1. **Zero-Compromise Pydantic-validointi:** 
   * Uudet DTO- ja domain-mallit (kuten `OutputProfile`) määritellään tiukoilla tyypityksillä (`model_config = ConfigDict(strict=True, extra="forbid")` API-rajoilla).
   * Kaikki saapuva ja epävarma data (mukaan lukien LLM:n tuotokset ja tietokantakyselyt) hydratoidaan välittömästi `.model_validate()` tai `.model_validate_json()` -metodeilla. 
   * Vältetään defensive programming -ansoja (kuten `.get("key", default)` tai `getattr()`-fallbackit liiketoimintalogiikassa). Virheellisen tai puuttuvan datan kohdalla järjestelmän on kaaduttava äänekkäästi ja välittömästi (Fail-Fast).

2. **Muuttumaton tilanhallinta ja puhtaat funktiot:**
   * Tila- ja DTO-olioita käsitellään pysyvästi jäädytettyinä (`frozen=True`).
   * Tilan muutoksia ei tehdä paikan päällä (in-place mutation), vaan luomalla uusia kopioita `.model_copy(update={...})` -metodilla, mikä estää sivuvaikutukset ja takaa forensisen jäljitettävyyden.

3. **Yhdenmukainen virheidenkäsittely (RFC 7807):**
   * Raakojen poikkeusten (kuten `ValueError`) sijaan kaikki poikkeukset käännetään ja lokitetaan `AppException`-rakenteeseen (määrittäen selkeät `ErrorCodes`).
   * Kaikki resurssit, kuten tiedostokäsittelyt, rajataan tiukasti context managereilla (`with` / `async with`) resurssivuotojen estämiseksi. Lokitukseen ei saa päätyä LLM:n raakaprompteja tai PII-dataa.

4. **Moderni Python-syntaksi (3.14+ ja PEP-standardit):**
   * Tyypityksessä hyödynnetään PEP 695 mukaisia geneerisiä parametreja (esim. `class Repository[T]`), moderneja tyyppiliittoja (`X | None`) sekä PEP 736 kwargs-shorthandia redundantin koodin vähentämiseksi.
   * Prompteissa käytetään t-stringejä (PEP 750) tai XML/Markdown-hybridiä parantamaan prompt caching -osumia ja estämään prompt-injektioita.

5. **Dokumentaatio ja itseselittävyys:**
   * Jokainen uusi moduuli, luokka ja funktio varustetaan PEP 257 -yhteensopivalla Google-tyylisellä docstringillä. Docstringeissä kuvataan selkeästi mahdolliset `Raises:` -osiot `AppException`-koodeilla ilman turhaa tyyppien toistoa.

*Huomautus:* Jotta tämä uudistus voidaan viedä läpi saumattomasti ja ilman purkkakorjauksia, aiemmat rajoitukset tiettyjen tiedostojen (kuten `prompt_compiler.py`) tai lukittujen koodilohkojen muokkaamisesta eivät ole tämän Epicin kohdalla voimassa. Tarvittavat muutokset tehdään suoraan arkkitehtuurin ytimeen, noudattaen edellä kuvattua tiukkaa laatuviitekehystä.

---

## ** VAIHE 1: Pydantic "Suojamuuri" ja DTO:n rakentaminen**

**Vastuualue:** Backend (Models)  
**Tavoite:** Luodaan rautaiset säännöt sille, mitä LLM saa palauttaa, ja leikataan liian pitkät tekstit kooditasolla, jotta UI-grafiikat (kuten tutkakartta) eivät koskaan hajoa.

* **Task 1.1: Määrittele Enum ja päivitä DTO (Hybrid Schema)**  
  * **Tiedosto:** `backend_v2/models/v2_core.py` (tai tiedosto, jossa `AtomEvaluationItemDTO` asuu).  
  * Määrittele sallitut tilat: `VisualIntent = Literal["success", "warning", "critical_override", "info"]`.  
  * Lisää kenttä: `chart_display_label: str`. Aseta Pydanticin `Field(description="...")` -parametriin tiukat ohjeet (JSON-schemaa varten).
  * Lisää kenttä: `visual_intent: VisualIntent` (JSON-schemaa varten).
  * Lisää kenttä: `semantic_reasoning: str`. (HUOM: Tätä ei pyydetä JSON:ssa syntaktisen haurauden vuoksi, vaan tämä parsitaan Markdown AST:n kautta tekstilohkoista).  
  * **Hardening-viitekehys (Säännöt 77 & 84 poikkeus, Sääntö 10):**  
    * *Clean Slate -lähestymistapa (Säännöt 77 & 84 poikkeus):* Koska tämä uudistus toteutetaan puhtaalta pöydältä ilman tarvetta tukea vanhoja tietokanta-ajoja tai ylläpitää taaksepäinyhteensopivuutta, voimme muokata olemassa olevien DTO-luokkien kenttiä vapaasti. Uudet kentät (`chart_display_label` ja `visual_intent`) määritellään **pakollisiksi** (ei oletusarvoja kuten `None` tai `""`). Tämä takaa, että tekoäly pakotetaan aina tuottamaan nämä arvot ilman mahdollisuutta tyhjiin tiloihin (Zero-Compromise).
    * *Sääntö 10 (Pydantic Pure Hydration Boundary):* API-rajan DTO-malleille varmistetaan tiukka tyyppiturvallisuus (`strict=True`).
* **Task 1.2: Rakenna @field_validator suojamuurit**  
  * Luo `chart_display_label`-kentälle validaattori (`mode="after"`). **Logiikka:** Jaa string sanoiksi (`v.split()`). Jos sanoja on yli 3, leikkaa ylimääräiset pois ja lisää perään "...". Leikkaa myös fyysisesti yli 25 merkin pituiset tekstirimpsut. *Tämä data on tarkoitettu vain esitykseen, joten UI:n turvaaminen leikkaamalla on sallittua.*  
  * **KIELLETTY (Sääntö 1 & 22):** Älä luo `visual_intent`-kentälle fallback-validaattoria tai hiljaisia oletusarvoja (kuten "info" palauttaminen, jos arvo on viallinen). Jos LLM palauttaa arvon, joka ei ole sallitulla listalla, Pydantic heittää `ValidationError`. Järjestelmän Fail-Fast -sääntö (Zero-Compromise Pledge) kieltää hiljaiset paikkaukset. Vanhoja ajoja ei tueta eikä paikkailla.
  * **Hardening-viitekehys (Sääntö 11):**  
    * *Sääntö 11 (Pydantic Native Field Priority):* Suosi natiiveja Pydantic-rajoitteita `Field`-tasolla (esim. `max_length=25`) `@field_validator`-logiikan sijaan, ellei Vertex AI:n float-ongelmat (Sääntö 5) vaadi toisin. Sanamäärän rajoittamiseen käytetään `@field_validator`-metodia.



---

## ** VAIHE 2: Output Profile -Tietokantamalli ja Seed-migraatio**

**Vastuualue:** Backend (Domain & Database)  
**Tavoite:** Siirtää LLM:n persoonallisuus ja kielelliset säännöt Python-koodista tietokantaan.

* **Task 2.1: Tietokantamallin luonti**  
  * **Tiedosto:** `backend_v2/models/domain/output_profile.py`  
  * Luo Pydantic-malli `OutputProfile`, joka perii `V2CoreBase` (tai vastaavan perusluokan).  
  * Kentät: `profile_id`, `name`, `language`, `tone_of_voice`, `formatting_directives`.  
  * **Hardening-viitekehys (Säännöt 2, 25):**  
    * *Sääntö 2 (Strict Pydantic V2 Rust):* Uudelle luokalle määritellään `model_config = ConfigDict(strict=True, extra="forbid")`.  
    * *Sääntö 25 (Opaque Stripe ID Mandate):* Avainkenttä `profile_id` on luotava noudattamaan tiukkaa Opaque Stripe ID -standardia (etuliite `prf_` ja satunnainen heksatunnus, esim. `prf_x8f9a2b1`). Semanttiset tunnisteet (kuten "default_fi") ovat kiellettyjä.
* **Task 2.2: Repository-tuki**  
  * **Tiedosto:** Luo uusi tiedosto `backend_v2/database/repositories/output_profile_repository.py`.  
  * Varmista, että tietokantakerroksessa on metodit profiilin hakemiseen (`get_profile`) ja tallentamiseen (`save_profile`).  
  * **Päätös & Hardening-viitekehys (Sääntö 74 poikkeus, Sääntö 10):**  
    * *Sääntö 74 poikkeus:* Koska `OutputProfile` ei ole polymorfinen rakenne (skeema on täysin staattinen kaikille profiileille), tehdään poikkeus sääntöön 74. `OutputProfileRepository`-metodit palauttavat raa'an sanakirjan sijaan suoraan tyypitetyn `OutputProfile`-mallin. Tämä parantaa tyyppiturvallisuutta ja poistaa turhaa validointi-boilerplatekoodia Service-kerroksesta.
    * *Sääntö 10 (Pydantic Pure Hydration Boundary):* Kyselyn tulos validoidaan tietokantarajalla löysästi `.model_validate(data, strict=False)` -metodilla, jotta tietokannan tyyppimuunnokset sallitaan, mutta palvelukerrokselle palautetaan heti täysin eheä ja tyyppitarkistettu olio.
* **Task 2.3: Seed-datan migraatio (Tärkeä!)**  
  * **Tiedosto:** `backend_v2/seed/seed_data.json`  
  * Kopioi nykyisistä `directives.py` ja `linguistic.py` -tiedostoista säännöt.  
  * Luo JSON-tiedostoon uusi juuritason kokoelma `"output_profiles": [...]` ja syötä säännöt sinne.  
  * **Hardening-viitekehys (Sääntö 25, 73):**  
    * Kaikki seed-profiilit saavat uniikit Opaque Stripe ID:t (esim. `prf_fi8x9y` ja `prf_en2b3c`). Monikielisyys toteutetaan profiilien kielikenttien (`language: "fi"`) ja l10n-järjestelmän kautta, ei kovakoodatuilla ID-merkkijonoilla.

---

## ** VAIHE 3: Studio API & DB Haku**

**Vastuualue:** Backend (API & Orchestrator)  
**Tavoite:** OutputProfile pitää pystyä hallitsemaan Studiosta ja hakemaan tehokkaasti LLM-ajon yhteydessä. Vältetään kuitenkin virheellistä `lru_cache`-logiikkaa, joka ei toimi hajautetussa järjestelmässä (FastAPI vs Arq Worker).

* **Task 3.1: Profiilin hallinta Studiossa**  
  * **Tiedosto:** `backend_v2/api/routers/studio/output_profiles.py`  
  * Luo CRUD-endpointit (erityisesti `PUT /studio/profiles/{profile_id}`).  
  * **Hardening-viitekehys (Säännöt 32, 33, 78):**  
    * *Sääntö 32 (Anemic Routers) & Sääntö 78 (API vs Service Layer Separation Mandate):* Reititin ei saa sisältää liiketoimintalogiikkaa eikä luoda uusia Opaque Stripe ID:itä. ID-generaatio ja entiteetin valmistelu kuuluvat yksinomaan Service-kerrokselle.  
    * *Sääntö 33 (Data Leak Prevention Firewall):* Endpoint-määritelmässä on pakotettava tiukka `response_model=...` estämään data-vuodot.
* **Task 3.2: Profiilin dynaaminen haku LLM-ajossa**  
  * Hae OutputProfile suoraan tietokannasta (Firestore/TinyDB) jokaisen LLM-työn (Arq Worker) alussa ohittamalla lokaalit välimuistit (kuten `lru_cache`). Tietokantahaku on riittävän nopea ja takaa Single Source of Truth -reaaliaikaisuuden aina.  
  * **Hardening-viitekehys (Säännöt 3, 23):**  
    * *Sääntö 3 (Fail-Fast Hydration Mandate) & Sääntö 23 (Zero Service Layer Fallbacks):* Älä käytä `.get(key, default)` tai anemic lookupia. Jos pyydettyä profiilia ei löydy, järjestelmän tulee heittää välittömästi `AppException`.

---

## ** VAIHE 4: LLM-moottorin purkaminen (The Dumb Pipe)**

**Vastuualue:** Backend (LLM/Orchestrator)  
**Tavoite:** Kytketään uusi arkkitehtuuri kiinni itse tekoälyyn ja poistetaan vanha koodi.

* **Task 4.1: LLM System Promptin dynaaminen rakennus**  
  * **Tiedosto:** `backend_v2/services/orchestrator/strategies/llm_execution.py` (tai vastaava LLM-ajon alustusreitti).  
  * Hae `OutputProfile` tietokannasta.  
  * **Hardening-viitekehys (Säännöt 29, 51, 52):**  
    * *Sääntö 29 (High Fidelity Prompting) & Sääntö 52 (Ephemeral Caching Topology):* Systeemipromptit pidetään 100% staattisina prompt caching -suorituskyvyn maksimoimiseksi. Dynaamiset esitysmuotoiluun ja kieleen liittyvät parametrit syötetään promptin loppuun erillisen `<execution_parameters>`-XML-tagin sisällä. Älä käytä f-stringejä promptien ytimen kasaamiseen.  
    * *Sääntö 51 (Hybrid Prompting Mandate):* Rakenna tekoälyn ohjeistus hyödyntäen XML-rakenteita ja Markdownia.
* **Task 4.2: Fast-Track XML Parsing & Hydration (Hybrid Protocol)**  
  * Ohjeista LLM palauttamaan data tiukan XML-rakenteen sisällä: pitkä teksti/päättely (esim. `semantic_reasoning` ja verbatim-lainaukset) menee `<reasoning>...[^DOC-1]</reasoning>` -tagien väliin luonnollisena Markdownina, ja koneellisesti luettava kontrollidata (esim. `visual_intent`, `chart_display_label`) menee `<json_payload>{...}</json_payload>` -tagien väliin.
  * **Tiedosto:** Luo `backend_v2/services/llm/ingress_pipeline.py`. **Kielletty (CPU Bloat):** Älä käytä raskasta Markdown AST -jäsennintä (kuten `markdown-it-py`), koska täyden abstraktisyntaksipuun rakentaminen synkronisessa Ingestion Boundaryssa estää Event Loopin ja tuhoaa suorituskyvyn (GIL bottleneck). Käytä sen sijaan kevyttä, salamannopeaa $O(1)$ regex-uuttoa XML-tagien erottamiseen ennen Pydantic-hydraatiota. Uutetusta JSONista ja tekstilohkoista muodostetaan yhdistetty sanakirja, joka syötetään DTO:lle (`Model.model_validate(combined_dict)`).
  * **Hardening-viitekehys (Sääntö 28 & Bifurcated Parsing):**  
    * *Sääntö 28 (LLM Structured Execution Mandate):* Suora anemic `LLMClient`-kutsu on kielletty. Fast-Track XML Parsing takaa kaksivaiheisen hydraation ilman CPU-tukoksia. Käyttämällä Markdownia raskaalle tekstille `<reasoning>`-tagissa vältämme JSON-syntaksin globaalin haurauden, ja Pydantic varmistaa tuloksen tyyppiturvallisuuden (Zero-Compromise).
* **Task 4.3: The Purge (Kovakoodauksen tuhoaminen)**  
  * **POISTA:** `backend_v2/llm/directives.py`  
  * **POISTA:** `backend_v2/llm/linguistic.py`  
  * Siivoa `prompt_builder.py` poistamalla sieltä kaikki luonnollisen kielen säännöt.  
  * **Hardening-viitekehys (Sääntö 50):**  
    * *Sääntö 50 (Feature Sovereignty Mandate):* Ennen tiedostojen poistoa varmistetaan, ettei niistä hävitetä mitään sellaista uniikkia liiketoimintalogiikkaa, jota ei ole siirretty tietokantapohjaisiin `OutputProfile`-profiileihin.

---

## ** VAIHE 5: Frontend & PDF Pariteetti (SDUI Renderöinti)**

**Vastuualue:** Frontend (Dart) & PDF Generator (Jinja2)  
**Tavoite:** Kytketään UI ja PDF reagoimaan sokeasti tekoälyn palauttamiin grafiikka- ja tilakenttiin (Server-Driven UI).

* **Task 5.1: Dart DTO ja Enum pariteetti**  
  * **Tiedostot:** `client_app_v2/lib/core/models/enums.dart` & `client_app_v2/lib/features/execution/models/scorecard_dto.dart`  
  * Luo uusi `@JsonEnum()` nimeltä `VisualIntent` ja määrittele sille täsmälleen samat Literal-arvot kuin Python-backendissa.  
  * Lisää Dart-malliin uudet kentät: `chartDisplayLabel` (String) ja `visualIntent` (VisualIntent). Aja build_runner.  
  * Päivitä backendin `test_enum_parity.py` tarkistamaan `VisualIntent`-pariteetti.  
  * **Hardening-viitekehys (Sääntö 44):**  
    * *Sääntö 44 (Cross Language Enum Parity):* Varmista absolute 1-to-1 enum-pariteetti backendin ja frontendin välillä. Tämän valvonta sidotaan automaattiseen testipatteristoon.
* **Task 5.2: Flutter Tutkakartta (Radar Chart)**  
  * Päivitä tutkakarttaa piirtävä widget.  
  * Vaihda akselien nimiksi atomin `chartDisplayLabel`. Poista Flutterista kaikki vanhat tekstien lyhennys- tai rivityslogiikat (Backend hoitaa nyt lyhentämisen). Nyt tutkakartta mahtuu ruudulle täydellisesti.
* **Task 5.3: Flutter Visuaalisen tilan (Intent) kytkentä**  
  * Toteuta värikarttaus laajentamalla olemassa olevaa teemaluokkaa (esim. `AppColors`), älä luo irrallisia apumetodeja widgetteihin. Mäppää `visualIntent`:n arvot teeman väreihin: esim. success -> Vihreä, critical_override -> Punainen/Huomio. Maalaa tuloskortit/rivien taustat näillä teemaväreillä.
* **Task 5.4: PDF Rendering Parity**  
  * **Tiedosto:** `backend_v2/templates/report_template.jinja2`  
  * Syötä PDF-kirjaston tutkakartta-komponentille täsmälleen samat `chart_display_label` -kentät.  
  * Luo Jinjaan dynaamiset CSS-luokat: `<div class="card intent-{{ atom.evaluation.visual_intent }}">`.  
  * Varmista CSS:ssä, että `.intent-critical_override` näyttää visuaalisesti samanlaiselta kuin Flutterin vastaava laatikko.  
  * **Hardening-viitekehys (Sääntö 30):**  
    * *Sääntö 30 (Tripartite Rendering Boundary):* Backend ei saa missään tilanteessa tuottaa valmiiksi muotoiltua Markdownia tai esityskerrosmerkkijonoja. Backend toimittaa puhtaan DTO-rakenteen, ja Jinja2 (PDF:lle) sekä Flutter (käyttöliittymälle) vastaavat esittämisestä itsenäisesti.

---

## ** Hyväksymiskriteerit (Definition of Done)**

1. Koodikannasta on pysyvästi poistettu `directives.py` ja `linguistic.py`.  
2. Kun Admin muokkaa Profiilia Studio API:n kautta, muutos astuu voimaan välittömästi *seuraavaan* generoituvaan raporttiin ilman backendin uudelleenkäynnistystä (haku suoraan tietokannasta ilman välimuistiongelmia).  
3. Tekoälyn tuottamat tutkakartan tekstit (`chart_display_label`) ovat aina max 3 sanaa. Vaikka LLM yrittäisi palauttaa liikaa tekstiä, Pydantic-suojamuuri leikkaa ne.  
4. UI ja PDF tulostavat värikoodauksen/ikonit täydellisessä synkassa `visual_intent` -enumia totellen.  
5. **Kaikki uudet ja muutetut Python-tiedostot läpäisevät `backend_audit_loop.py` -ajon** (PEP 257 docstring-hyväksyntä, tyypitykset, ei fallbackeja ja 100% testikattavuus tehdyille muutoksille ilman live-LLM-kutsuja).  
6. **Kaikki Flutter-muutokset läpäisevät `flutter_audit_loop.py` -ajon.**