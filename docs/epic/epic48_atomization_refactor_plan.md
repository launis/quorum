# Epic 48: Atomisaation Purku ja Teoreettinen Ankkurointi (Implementation Plan)

Tämä suunnitelma kuvaa vaiheittaisen prosessin, jolla siirrymme V1-aikakauden epätarkasta "Deep Atomization" (15 satunnaista lausetta) -mallista kohti 100 % determinististä ja akateemisesti ankkuroitua **"Single Source of Truth" -mallia**.

## Vaihe 1: Arkkitehtuurin Siivous (Dead Code Removal)

Tehdään koodikannasta deterministinen poistamalla tekoälyn pakotettu hallusinointi käynnistyksen (seeding) yhteydessä.

1.  **`atomization_cache.json` tuhoaminen:**
    *   Tiedosto `backend_v2/seed/atomization_cache.json` poistetaan kokonaan repositoryn historiasta.
2.  **`PromptAtomizer`-luokan poisto tai muokkaus:**
    *   Tiedosto `backend_v2/services/orchestrator/atomizer.py` muutetaan siten, että se ei tee API-kutsua LLM:lle.
    *   Logiikka korvataan puhtaalla Pythonilla: Jos matriisin `micro_atoms` puuttuu, koodi yksinkertaisesti asettaa `micro_atoms = [claim.ai_description]`. Vaihtoehtoisesti koodi voi pilkkoa rivinvaihdoilla, jos niitä on (moniehtoiset säännöt).
3.  **Pydantic-skeemojen rajoitteiden purku:**
    *   Etsitään `micro_atoms` Pydantic-määrittely (`min_length=15`, `max_length=15`) tiedostosta `backend_v2/services/orchestrator/atomizer.py` tai mallistosta ja poistetaan se. Sallitaan jatkossa dynaaminen määrä atomeja (esim. 1–3).
4.  **`run_seed.py` kevennys:**
    *   Poistetaan LLM-clientin ja välimuistin alustukset Seederistä. Jatkossa tietokannan pystytys vie vain sekunteja ilman verkkokutsuja.
5.  **`enums.py` optimointi:**
    *   Päivitetään `SystemConcurrency` arvot (esim. `MAX_CONCURRENT_LLM_STEPS = 5`, `LLM_MAX_RETRIES = 3`, `LLM_DEFAULT_TIMEOUT_SECONDS = 180`) aiemman keskustelun mukaisesti.

---

## Vaihe 2: Database Schema & Roolien Täydellinen Erottelu (Separation of Concerns)

Poistamme järjestelmästä `micro_atoms` -kentän täysin ja muutamme `ai_description` -kenttien käyttötarkoituksen Pydantic V2 "Zero-Legacy" -sääntöjen ja `05_llm_architecture.md` -sääntöjen mukaisiksi.

1.  **Pydantic-mallin tyyppimuutos (`Claim.ai_description` $\rightarrow$ `list[str]`):**
    *   Yksittäisen väitteen (Claim) kohdalla `ai_description` ei ole enää merkkijono, vaan se muutetaan Pydantic-mallissa muotoon `ai_description: list[str] = Field(min_length=1)`.
    *   Tämä korvaa aiemman `micro_atoms` -keksintämekanismin. Ihminen syöttää jatkossa TDA-väitteet suoraan tähän listaan tietokannassa.
    *   **Arkkitehtuurisääntö (`strict_pydantic_v2_rust` & `zero_legacy_fallback_hacks`):** Pydantic-mallissa on pakotettava `model_config = ConfigDict(extra='forbid', strict=True)`. Legacy V1-fallbackeja tai löysiä dict-tyyppejä ei sallita; jos rakenne poikkeaa, se kaatuu Fail-Fast-periaatteen mukaisesti.
2.  **Matriisitason `PromptBlock.ai_description` (System Prompt & Persona):**
    *   Matriisin päätason `ai_description` säilyy normaalina merkkijonona (`str`), mutta sen rooli muuttuu pelkäksi **Agentin Persoonaksi ja Sääntömoottoriksi**.
    *   **Arkkitehtuurisäännöt (`native_language_system_prompts`, `hybrid_prompting_mandate`, `high_fidelity_prompting_and_caching`):** 
        *   Promptin on oltava **yksinomaan englanniksi**, jotta vältetään monimutkaisten sääntöjen kielellinen rapautuminen (suomenkieliset ohjeet kielletty systeemitason säännöissä).
        *   Promptin on käytettävä **Hybrid Promptingia** (Markdownia XML-tagien sisällä).
        *   Promptin on oltava täysin staattinen. Kaikki dynaamiset parametrit injektoidaan erillisen `<execution_parameters>`-tagin sisään käyttäjän pyyntöön, jotta 100 % "Prompt Caching" toteutuu kustannussäästöjen maksimoimiseksi.
    *   *Esimerkki:*
      ```xml
      <system_directive>
        <role>You are a highly critical, zero-trust academic auditor evaluating text according to the Toulmin model.</role>
        <rules>
          <rule>If you evaluate an assertion as TRUE, you MUST provide the exact, character-for-character quote from the text that proves it.</rule>
          <rule>If the text uses vague language (e.g. 'probably', 'might') when evidence is required, mark the assertion as FALSE.</rule>
        </rules>
      </system_directive>
      ```
3.  **Positivity Mandate (Kaikki väitteet ovat hyveitä):**
    *   **Kriittinen sääntö:** Kaikki listan TDA-väitteet on muotoiltava positiivisiksi onnistumisiksi. Matematiikkamoottorit (DINA/Guttman) laskevat tulosta ylöspäin (`hit_rate = sum(True) / total`). Negatiivisten sääntöjen ("Data puuttuu") sekoittaminen rikkoo kumulatiivisen matematiikan.
    *   *Esimerkki ennen (Negatiivinen):* "Teksti esittää subjektiivisia olettamuksia faktoina."
    *   *Esimerkki jälkeen (Positiivinen TDA):* "Teksti erottaa eksplisiittisesti subjektiiviset olettamukset objektiivisista faktoista." (Jos tekstissä on vikaa, arvio on False, hit rate jää nollaan ja rangaistus laukeaa).
4.  **Metatekstin poisto:**
    *   Kaikki vanha metateksti, kuten `"CRITICAL EVALUATION DIRECTIVE:"` siivotaan pois väiteriveiltä ja siirretään puhtaana XML-sääntönä matriisin päätason ohjeistukseen (Kohta 2).

---

## Vaihe 3: Teoreettinen Ankkurointi ja Database Schema -muutos (SSOT)

Tämä on kriittisin laadullinen vaihe. Ennen kuin luomme yhtäkään uutta Test-Driven Assertion -väitettä, varmistamme alkuperäislähteistä, mitä olemme todella mitanneet. Vasta tämän jälkeen rakennamme uuden Pydantic-tietokantaskeeman.

**Toteutusjärjestys ja Database Schema -muutos:**

1.  **Lähteiden analyysi (Ensimmäinen askel):**
    *   Käytämme LLM:n agenttityökaluja (Web Search / MCP) lukemaan `seed_data.json`:n `theory_grounding.source_url` -linkit tai niiden tiivistelmät (esim. Toulminin 2003 tai Bloomin 2001 alkuperäisteokset).
2.  **Akateemisten määritelmien purku LLM:llä:**
    *   Emme anna LLM:n keksiä kriteerejä vapaasti. Luomme uuden apuscriptin (esim. `scripts/theory_grounding_extractor.py`), joka lukee `theory_grounding` -lähteen ja purkaa sen Pydantic-listaksi.
    *   **Arkkitehtuurisääntö (`llm_structured_execution_mandate`):** Älä koskaan käytä `run_chat()`-metodia tai regex-parsimista tällaiseen strukturoituun generointiin. Suoritus on aina tehtävä API:n natiivin strukturoidun rajoitteen ja keskitetyn Pydantic-korjauksen kautta metodilla `LLMTaskExecutor.execute_structured_task()`.
    *   **Prompt-arkkitehtuuri:** Täysin staattinen, puhtaasti englanninkielinen System Prompt XML-tageilla. Kohdeteksti injektoidaan User-viestiin.
3.  **Database Schema -muutos (String $\rightarrow$ Pydantic List):**
    *   Koska luovumme `atomizer.py`:n ajonaikaisesta parsimisesta, muutamme tietokantaskeemaa (`models/v2_core.py` ja `seed_data.json`).
    *   Poistamme `micro_atoms` kentän täysin ja muutamme yhtenäiseksi totuudenlähteeksi `ai_description: list[str]`. 
    *   Tämä tekee koodista **Single Source of Truth (SSOT)**: Emme enää koskaan splitata merkkijonoja rivinvaihdoilla ajonaikaisesti, vaan Pydantic valvoo jo rajapinnassa, että kriteerit ovat valmis JSON-lista.
4.  **Väitteiden (Claims) purku listaksi (Compound $\rightarrow$ Atomic):**
    *   Peilaamme akateemiset määritelmät tähän uuteen listarakenteeseen.
    *   Nykyiset yhdistelmäsäännöt (esim. "Data on kiistatonta ja relevanttia") pakotetaan pilkkomaan erillisiksi atomeiksi uuteen JSON-listaan:
        *   `"Esitetty data on kiistatonta."`
        *   `"Esitetty data on erittäin relevanttia."`

---

## Vaihe 4: Hallusinaatiosuoja, Kestävyys ja Tunnisteet (Industrial Grade Resilience)

Kun väitteet on tiukennettu yksittäisiksi ja deterministisiksi (`list[str]`), asynkronisen ajon on oltava matemaattisesti idioottivarma ja kestettävä tekoälyn hallusinaatiot kaatamatta koko järjestelmää.

1.  **Ephemeral Runtime IDs (MD5-Hashien tuhoaminen):**
    *   Historiallinen asynkroninen arkkitehtuuri, joka laski kysymyksille raskaat MD5-tiivisteet, on ankarasti kielletty (Hash Collision -haavoittuvuus).
    *   Koska TDA:t asuvat nyt Pydantic-listassa, `atom_flattening.py` (tai vastaava logiikka) generoi jokaiselle väitteelle puhtaasti ajonaikaisen ja tilapäisen sekvenssitunnisteen (esim. `tda_0`, `tda_1`). Tämä ID lähetetään LLM:lle, ja tulokset mapataan takaisin listaan O(1) -muistimäppäyksen avulla ilman tietokantataakkaa.
2.  **DTO-rakenteiden päivitys (Chain of Custody, XAI & Extensions):**
    *   Lisätään tulos-DTO:ihin pakolliset kentät `evidence_quotes: list[str]` ja `reasoning_trace: str`.
    *   **XAI-Perustelu (`reasoning_trace`):** Ennen kuin LLM päättää `is_true` -arvon, sen on **aina** kirjoitettava lyhyt perustelu tähän kenttään. Tämä on erityisen kriittistä, kun tulos on `False` (ja lainaus on tyhjä).
    *   **Dynaamiset Output Extensions (seed_data.json):** Emme kovakoodaa valmennusohjeita. DTO-mallin on kunnioitettava `PromptBlock` -määrittelyssä olevia dynaamisia laajennuksia (esim. `output_extensions: ["coaching", "falsification"]`). `schema_builder.py` / `prompt_compiler.py` injektoi nämä lennosta `AtomResponse`-luokkaan (esim. `extension_coaching: str`), jolloin LLM palauttaa matriisikohtaisesti vaaditut XAI-tiedot `False`-skenaarioissa rakentavaa palautetta varten.
    *   **Nollasääntö (Zero-Length Quote):** Oletuksena `is_true == True` vaatii aina suoran lainauksen (`len(quotes) > 0`), ja `is_true == False` pakotetaan tyhjäksi listaksi `[]` (sillä puutetta ei voi lainata).
    *   **Natiivisti Negatiiviset Säännöt (`inverse_evidence`):** Kaikkien teorioiden hyveitä ei voi lainata fyysisesti (esim. "Tekstissä ei ole syrjiviä ilmaisuja"). Pydantic-malliin lisätään `inverse_evidence: bool = False` konfiguraatiolippu. Kun tämä lippu on päällä, Nollasääntö kääntyy päinvastaiseksi:
        *   `is_true == True` (Onnistuminen: ei löytynyt syrjintää) $\rightarrow$ Lainaus **pakotetaan** tyhjäksi `[]`.
        *   `is_true == False` (Epäonnistuminen: löytyi syrjintää) $\rightarrow$ Lainaus on **pakollinen** `len(quotes) > 0`. Tällöin teksti falsifioidaan ja rangaistus todistetaan RapidFuzz-kestävällä lainauksella. Tällä saavutamme Positivity Mandaten ilman "todista olemattomuus" -paradoksia.
3.  **RapidFuzz Python-validointi (Fail-Fast & Cheat Code Prevention):**
    *   Pydantic `@model_validator` lukee LLM:n palauttaman `evidence_quotes` -listan ja ajaa sen `RapidFuzz` -kirjaston läpi.
    *   **Kontekstin Injektio:** Jotta Pydantic-validaattori ylipäätään tietää, mistä tekstistä vertailu tehdään, alkuperäinen puhdistettu teksti on injektoitava Pydanticin `ValidationInfo.context` -parametrin kautta LLM-paluukutsun parsimisvaiheessa.
    *   **Kadonnut Konteksti (Fail-Fast Assertio):** Asynkronisissa Arq-työnkuluissa konteksti saattaa hukkua. Validaattoriin on koodattava ehdoton assertio heti ensimmäiselle riville: `if not info.context or 'source_text' not in info.context: raise ValueError("CRITICAL: source_text context missing")`.
    *   **Ohjelmallinen Normalisointi & Kynnysarvo:** PDF-dokumenttien näkymättömien rivinvaihtojen ja OCR-artefaktien takia molemmat merkkijonot (lähdeteksti ja tekoälyn lainaus) on **aina normalisoitava** lokaalisti ennen RapidFuzzia: `.strip().replace('\n', ' ').lower()`. Kynnysarvoksi asetetaan tiukka, mutta pragmaattinen `fuzz.partial_ratio > 95.0`. Täydellistä (100 %) osumaa ei saa vaatia PDF-tiedostojen kohdalla.
    *   **Tekoälyn Huijauksen Esto (Max Length Rule):** LLM saattaa yrittää varmistaa osuman palauttamalla koko sivun sisällön lainauksena. Tämä estetään asettamalla validaattoriin ehdoton pituusrajoite (esim. max 40 sanaa per lainaus): `if len(quote.split()) > 40: raise ValueError(...)`.
4.  **Dynaaminen Virhepalaute (`<PREVIOUS_SCHEMA_ERROR>`):**
    *   Jos `RapidFuzz` ei löydä lainausta tekstistä, Python laukaisee välittömästi `ValueError`-virheen osana Pydantic-mallia.
    *   Arq-worker injektoi seuraavaan yritykseen dynaamisen `<PREVIOUS_SCHEMA_ERROR>` -XML-lohkon: *"Error: Lainauksesi 'X' ei löydy tekstistä. Etsi alkuperäinen lainaus tai aseta väite muotoon False."*
    *   **Arkkitehtuurisäännöt (`infinite_retry_loops`, `silent_failures`):** Arq-workerin automaattinen uudelleenyritys ei saa muodostaa ääretöntä luuppia. Uudelleenyritysten lukumäärän on oltava tiukasti sidottu `SystemConcurrency.LLM_MAX_RETRIES`-vakioon. Validointivirheitä ei koskaan saa nielaista hiljaa (`try: ... except: pass`), vaan ne on logattava eksplisiittisesti (`logger.error`).
5.  **Dead Letter Queue & Matemaattinen Puhtaus (N/A, ei 0):**
    *   Jos tekoäly epäonnistuu toistamiseen, pysyvästi korruptoitunut TDA-väite siirretään **Dead Letter Queue (DLQ)** -jonoon.
    *   **Matemaattinen Suoja:** DLQ-väitteelle **ei** anneta 0 pistettä. Jos asiakkaan dokumentti on täydellinen, mutta LLM kaatuu, asiakasta ei rangaista. DLQ:hun joutunut väite poistetaan kokonaan nimittäjästä: `hit_rate = sum(True) / (total_atoms - dlq_count)`. Raportissa DLQ-kohta merkitään "N/A". Takaamme auditoitavuuden kaatamatta järjestelmää tai vääristämättä matematiikkaa.
    *   **Nollalla Jakamisen Esto (Death by DLQ):** Jos *kaikki* väitteet joutuvat DLQ:hun (esim. teksti on lukukelvotonta OCR-siansaksaa), nimittäjä menee nollaan. Pisteytysmoottoriin (`scoring.py`) on lisättävä ehdoton tarkistus: `if valid_denominator == 0: return ScoringResult(score=None, status="FAILED_UNSCORABLE")`. Tämä estää koko Python-taustaprosessin kaatumisen `ZeroDivisionError` -virheeseen.

---

## Analyysi ja havaittujen epäloogisuuksien korjaukset (Analysis & Corrections)

Suunnitelman läpikäynnin yhteydessä huomattiin kolme arkkitehtuurillista ristiriitaa, jotka korjataan seuraavasti ennen koodin toteuttamista:

1. **Ristiriita 1: `micro_atoms` vs `ai_description` nimeämiskäytäntö (Vaihe 2 ja 3)**
   * **Ongelma:** Suunnitelma ohjeisti muuttamaan `Claim.ai_description` listaksi, mutta puhui myöhemmin `micro_atoms` (tai `tda_assertions`) kentästä listana.
   * **Ratkaisu (Backend & UI Parity):** Päätetään yksi totuudenlähde. Muutetaan olemassa oleva `ai_description` kenttä tyypiksi `list[str]` yksittäisille väitteille (Claim). Vanha `micro_atoms` poistetaan kokonaan. TDA-väitteet syötetään jatkossa suoraan `ai_description`-listaan.
   * **Käyttöliittymän (UI) vaatimus:** Kun `Claim.ai_description` muutetaan listaksi (`list[str]`), Flutter-sovelluksen (Admin Studio) matriisieditori on ehdottomasti päivitettävä tukemaan tätä. Käyttöliittymän on lähetettävä API:lle oikein muotoiltu JSON-lista (esim. `["väite 1", "väite 2"]`), jotta se läpäisee Pydanticin `extra='forbid'` -validoinnin tallennettaessa. Frontendin DTO:t (`MatrixClaim`) on päivitettävä heijastamaan tätä `List<String>` -muutosta.

2. **Ristiriita 2: Pydantic ja `AppException` (Vaihe 4.4)**
   * **Ongelma:** Suunnitelma käskee nostamaan `@model_validator`in sisällä välittömästi `AppException`-virheen, jos RapidFuzz ei löydä osumaa. Pydantic-validaattoreissa on pakko nostaa `ValueError` (tai `AssertionError`), muuten Pydanticin sisäinen validointiputki rikkoutuu.
   * **Ratkaisu:** Validaattorissa nostetaan normaali `ValueError`. `LLMTaskExecutor` ottaa kopin Pydanticin tuottamasta `ValidationError`:ista ja injektoi sen `<PREVIOUS_SCHEMA_ERROR>` -blokkiin Arq-workeria varten.

3. **Ristiriita 3: Vaihe 1:n purkkapaikka vs. Vaihe 2:n rakennemuutos**
   * **Ongelma:** Vaihe 1 ohjeisti laittamaan `atomizer.py`:ssä "purkkapaikan" `micro_atoms = [claim.ai_description]`. Heti Vaihe 2 kuitenkin muuttaa koko tietokantaskeemaa siten, että teksti poistuu ja tilalle tulee oikea TDA-lista.
   * **Ratkaisu:** Koodimuutokset tehdään yhtenä "Zero-Legacy" -atomisena committina: poistetaan `atomizer.py`:n LLM-logiikka täysin samaan aikaan kun vaihdetaan Pydantic-mallit (`v2_core.py`), jolloin vältetään turhat väliaikaiset listakäärinnät.

**Toteutettavuus (Feasibility Check):**
* Kooditason tarkastelu varmistaa, että Pydanticin `ValidationInfo.context` tukee alkuperäisen tekstin injektointia RapidFuzzia varten.
* Pisteytysmoottorin suojaukset (`ZeroDivisionError` -esto `valid_denominator == 0` checkillä ja DLQ-vähennyksillä) ovat kriittisiä järjestelmän vakaudelle asynkronisissa Arq-ajoissa ja täysin toteutettavissa.

---

## Laatuporttien Vaatimukset (Tier 2 Hardening Compatibility)

Kun suunnitelma toteutetaan, koodin on läpäistävä backend- ja frontend-laatuporttien tarkistukset ilman virheitä (100 % Pass). Tämä edellyttää seuraavien kriittisten sääntöjen EHDOTONTA noudattamista toteutuksen aikana:

**Python Backend (Tier 2):**
* **Kielletyt oikotiet (the_zero_compromise_pledge & fail_fast_hydration_mandate):** Älä koskaan käytä Pythonin oletusarvon noutoa vanhojen rakenteiden kiertämiseksi (esim. `data.get("ai_description", [])`). Kaikki saapuva tietokanta/JSON-data on hydratoitava VÄLITTÖMÄSTI Pydanticin `.model_validate()` -komennolla (`extra='forbid'`).
* **Ei purkkapaikkauksia (zero_legacy_fallback_hacks):** Pydantic-malleihin (kuten `v2_core.py`) ei saa lisätä `@model_validator(mode="before")` -funktioita, `| None` tyyppejä tai or-ketjuja pelkästään vanhan V1-datan sovittamiseksi. Esimerkiksi uusi `ai_description` on *pakollinen* lista. Jos tietokanta sisältää vanhaa muotoa, tietokannan sisältö on päivitettävä (SSOT), ohjelmistoa ei saa "löysentää".
* **ID:iden kovakoodaus (zero_db_hardcoding_mandate):** Tietokannan ID-tunnisteita (esim. magic strings) ei saa esiintyä kovakoodattuna Pythonin logiikassa.

**Flutter Frontend (Tier 2):**
* **Null-Coalescing kielto (the_zero_compromise_pledge):** Et saa käyttää Dartissa null-fallbackeja piilottamaan rakenteellisia virheitä (esim. `aiDescription ?? []` tai arvojen arvailua `.maybeWhen()` -metodilla). Legacy-koodia ei tueta. Jos backend lähettää viallista dataa, Freezed-mallin TÄYTYY kaatua äänekkäästi ja välittömästi.
* **Kovakoodaus kielto (frontend_zero_db_hardcoding_mandate):** UI-komponentit eivät saa olettaa taulukoiden tiettyjä ID-arvoja, nimiä tai indeksijärjestyksiä näkymien rakentamisessa.

---

## Seuraavat askeleet (Execution)

Kun tämä suunnitelma hyväksytään (korjauksilla), etenemme seuraavasti:
1. Käynnistetään **Vaihe 1**: Tiedostojen poistot, `run_seed.py` puhdistus ja `enums.py` optimointi.
2. Ajetaan **Vaihe 3 & 2**: Etsitään teorian lähteet LLM-työkaluilla ja refaktoroidaan `seed_data.json`:n kentät Test-Driven Assertion -muotoon.
3. Toteutetaan **Vaihe 4**: Päivitetään arviointi-DTO:t ja lisätään RapidFuzz-koodivalidaattori backendin ytimeen.
4. **Validointi (Tier 2):** Varmistetaan muutosten kestävyys ajamalla tiukat Tier 2 -laatuportit sekä backendille että frontendille.
