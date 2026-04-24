# Epic 39: Dynaamisen Raportoinnin ja SDUI-arkkitehtuurin Täydellistäminen (Dynamic Reporting & SDUI Zero-Compromise)

## 1. Johdanto ja Tavoitteet
Tämän Epicin tavoitteena on saattaa loppuun kognitiivisen arviointimoottorin ja käyttöliittymän välinen tulostus- ja raportointilogiikka. Ohjelmistossa on jo valmiudet dynaamisten tulostusprofiilien hallintaan, matriisien arviointiin ja XAI-laajennusten integrointiin, mutta data-vuon (data pipeline) synkronointi asiantuntijamatriisien ja lopullisen Executive-tason raportoinnin välillä vaatii systemaattista rakenteellista eheyttämistä.

Päätavoitteet:
1. **Matemaattisen vastuun eristäminen (De-Generator Mandate):** LLM tuottaa jatkossa yksinomaan sokeiden atomien totuusarvot (`[True, False]`) sekä asiantuntijamatriisien sanalliset laajennukset (`output_extensions`). Kaikki numeerinen laskenta (raw_score, true/false suhteet) tapahtuu eksklusiivisesti Pythonilla.
2. **Dynaaminen Synteesi ja Raporttipohjat (1-n):** Käyttöliittymästä asetetut dynaamiset promptit (kuten *Senior Executive Coach*) kytketään XAI Reporter -solmun automaattiseksi ohjaukseksi.
3. **XAI-laajennusten Ristiriitojen Ratkaisu (Mismatch Resolution):** Määritellään arkkitehtuuritason ratkaisu tilanteeseen, jossa Output Profile vaatii näytettäväksi XAI-laajennuksia, joita ei ole alkuperäisissä matriiseissa generoitu.
4. **Observabiliteetin tuominen UI:hin:** Luodaan käyttöliittymään läpinäkyvä näkymä arvosanojen muodostumisesta (`lue_tulokset.py` -hengessä).

---

## Vaihe 1: Matemaattisen Vastuun Eristäminen (The Math Boundary)

Nykytilanteessa tekoäly ja Python tekevät jossain määrin päällekkäistä työtä tulosten koosteessa. Tämä vaihe karsii tekoälyltä turhan matemaattisen painolastin.

### 1.1 Atomisoinnin ja Tulosten Vastuunjako
*   **LLM:n ainoa tehtävä:** Palauttaa `ChunkWorker`-vaiheessa sokeiden atomien totuusarvojen lista (boolean).
*   **Pythonin tehtävä (`ScoringHook`):** Laskee `true_atoms`, `false_atoms`, `total_atoms` ja lopullisen Raw-arvosanan `level_breakdown` -rakenteeseen DINA-mallilla. Tämä on jo pitkälti tehty.
*   **Matematiikan Eristäminen (`strict_math_display_isolation`):** Raw-arvosanan laskenta on sidottava yksinomaan Pydanticin `scales`-taulukosta johdettuihin `math_min` ja `math_max` absoluuttisiin arvoihin. Tietokannan `scale_min` ja `scale_max` ovat puhtaasti käyttöliittymän esitystason (esim. 4-10 skaalaus) muuttujia, eikä niitä saa koskaan käyttää sisäisen matematiikan rajoina.
*   **Nollatilan Suojaus (`safe_math_zero_division`):** Python-tason DINA-laskennassa on EHDOTTOMASTI oltava absoluuttinen nollatilan suojaus. Jos validien atomien määrä on nolla (esim. sokea suodatus hylkäsi kaikki hypoteesit), järjestelmä ei saa koskaan kaatua `ZeroDivisionError` -poikkeukseen (HTTP 500). Tällöin raw-arvosanaksi asetetaan turvallisesti alin sallittu arvo ja prosessia jatketaan.
*   **Varmistus:** Varmistetaan, ettei yksikään LLM-prompti enää yritä laskea osumaprosentteja tai tuottaa JSON-kenttiä matemaattisille raaka-arvoille.

### 1.2 Matrix Output Extensions -sukupolvi
*   LLM generoi asiantuntijamatriiseille ("category_id": "matrix") sanalliset arviot suoraan konfiguroituihin `output_extensions` -kenttiin (esim. `justification`, `falsification`, `coaching`).
*   **XAI Domain -mallinnus (Strict-pakotus):** Kaikki dynaamiset `output_extensions` -kentät on EHDOTTOMASTI mallinnettava tiedostossa `backend_v2/models/domain/xai.py`. Ne on toteutettava polymorfisella Discriminated Union -rakenteella (esim. `Field(discriminator='extension_type')`), eikä niissä saa koskaan käyttää turvatonta `dict[str, Any]` -tyyppiä.
*   Nämä generoidaan Matrix-vaiheessa, ja ne ohitetaan FinOps-kompressiossa (jo korjattu `ContextBuilder`:ssa), joten ne kulkeutuvat muuttumattomina loppuraporttiin.

---

## Vaihe 2: FinOps ja Kontekstin Kompressio (Data Minimization Strategy)

Kaikkien atomisoitujen väitteiden käyttöönotto (`MATRIX_SAMPLING_LIMIT = 0`) luo massiivisen uhan järjestelmän vakaudelle, mikäli dataa ei hallita tiukasti. Työnkulun kaatuminen (`TokenLimitExceededError (239704 > 100000)`) oli suora seuraus siitä, että sokean arvioinnin raaka data pääsi vuotamaan raportoivalle LLM:lle asti.

### 2.1 Kontekstin Säälimätön Karsiminen (Ruthless Pruning via ContextBuilder)
*   **Ongelma:** `ChunkWorker`-solmut tuottavat jokaiselle yksittäiselle atomille monisanaisen perustelun (`reasoning`). Sadan atomin arvioinnissa pelkkä perustelu-dump paisuu välittömästi satoihin tuhansiin merkkeihin.
*   **Best Practice -Ratkaisu:** `ContextBuilder` puuttuu väliin juuri ennen kuin `$global_context_vars` (tai muu tila) injektoidaan LLM:n kontekstiin (esim. XAI Reporter -vaiheessa). Se etsii massiiviset `evaluations`-taulukot ja "puristaa" ne säälimättä puhtaaksi totuusarvolistaksi (`evaluations_bool_only: [True, False, True...]`).
*   **Amnesia Protocol (Puhdas Funktio):** Quorumin arkkitehtuurissa HookState ja DTO:t ovat ehdottoman pakastettuja (`frozen=True`). `ContextBuilder` **ei saa koskaan** yrittää muokata alkuperäistä tilaa in-place (ei `.pop()`, ei `del`, eikä edes raskasta `.model_copy()`-kloonausta koko massiivisesta tilasta). Sen sijaan on toteutettava puhdas, sivuvaikutukseton funktio (esim. `_prune_context_for_llm`), joka ottaa sisään raakadatan ja palauttaa täysin uuden, kevennetyn sanakirjan (delta) yksinomaan LLM-konteksti-injektiota varten. Alkuperäinen `HookState` säilyttää historiallisen totuuden muuttumattomana.
*   **Skaalautuvuus (Scale):** Pelkkä totuusarvolista kuluttaa vain kourallisen tokeneita (esim. 100 atomia = ~150 tokenia). Tämän myötä 100 000 tokenin kontekstiraja ei tule enää vastaan, vaikka matriisi arvioisi 10 000 atomia. Token-räjähdys on estetty arkkitehtuurin juuritasolla.

### 2.2 LLM-Payloadin Minimointi vs. Pythonin Maksimointi
*   **LLM saa MINIMI-datan:** XAI Reporter tai Executive Coach -LLM saa nähtäväkseen ainoastaan matriisien tuottamat korkean tason aggregaatit: `normalized_score` sekä matriisin tuottamat asiantuntijasynteesit (`output_extensions`). Sille *ei* koskaan syötetä yksittäisiä atomeja, koska sen tehtävä on ainoastaan laatia makrotason "Johdon yhteenveto".
*   **Python hoitaa MAKSIMI-datan:** Kaikki raskaat tietorakenteet, kuten atomien luupit, alkuperäiset tekstit ja mikrotason osumat (`true_atoms`, `false_atoms`) elävät yksinomaan Pythonin RAM-muistissa ja tietokannassa. Python suorittaa kaiken DINA-laskennan omalla prosessoritehollaan, mikä pitää API-kustannukset nollassa ja LLM:n prosessointinopeuden salamannopeana.

---

## Vaihe 3: Tulostusprofiilien ja Raporttipohjien Dynaaminen Injektio

Käyttöliittymä antaa dynaamisia prompteja ("Senior Executive Coach" ja "Visual Analyst"). Nämä on kytkettävä `generate_report_hook.py` -solmun ytimeen. **Kriittistä on noudattaa `ui_driven_synthesis_boundary` sääntöä:** LLM:lle syötettävää kontekstia ei saa enää vain sokeasti dumppaa (kuten vanhassa koodissa, joka puski Judge, Overseer yms. sumeilematta `ReportSynthesisDTO`:hon). Konteksti on aktiivisesti suodatettava.

### 3.1 Johdon Yhteenvedon (Executive Summary) Generointi
*   **Mekanismi:** Kun `generate_report_hook.py` aloittaa, se lukee suoritukseen sidotun tulostusprofiilin (`OutputProfile`). **Clean Architecture -huomio:** Hook ei saa koskaan tehdä suoraa tietokantahakua (esim. `db.client`), vaan `OutputProfile` on joko luettava Orchestratorin/Service-kerroksen sille valmiiksi välittämästä `global_context_vars` -tilasta tai noudettava tiukasti injektoidun `UnifiedWorkflowRepository` -kerroksen kautta.
*   **Aktiivinen Suodatus:** Globaalista kontekstista karsitaan kaikki tarpeeton (esim. WebSearch/PDF-raakatekstit, Logician-raakajäljet). Yhteenveto saa nähtäväkseen **vain** matriisitason (`category_id: matrix`) lopulliset suodatetut tulokset (`normalized_score`, `output_extensions`). Tämä *parantaa* LLM-tulosteen laatua, koska LLM:n huomiokyky (attention mechanism) ei harhaudu "context stuffing" -ilmiön myötä irrelevantteihin raakateksteihin.
*   **Promptin Injektio:** Se lukee profiilista *Synteesi- ja vientiasetukset* -lohkon system_directive -promptin. Tämä prompti asetetaan suoraan LLM:n järjestelmäohjeeksi (System Message).
*   **Konteksti:** Sisään syötetään kompressoitu ja aktiivisesti suodatettu `matrix_data`.

### 3.2 Dynaamiset Raporttipohjat (Report Templates 1-n) & Osiokohtainen Synteesi
*   **Mekanismi:** `OutputProfile` voi sisältää listan erillisiä raporttipohjia (esim. "3D Matrix: Toulmin - Goodhart - Kahneman").
*   **Iteratiivinen Suoritus:** `XAI Reporter` käy läpi kaikki 1-n raporttipohjaa.
*   **Kohdekomponenttien (Axis X, Y, Z) Suodatus:** Reporter etsii globaalista kontekstista tarkalleen ne matriisit, jotka on kytketty käyttöliittymän pudotusvalikoista komponentteihin 1, 2 ja 3 (esim. "Kausaalisuuden Analyysi", "Falsifioinnin Auditointi"). LLM saa nähtäväkseen VAIN näiden tarkasti valittujen matriisien data-aggregaatit.
*   **Osiokohtainen Synteesi & Näkymämallit:** Jos raporttipohjassa on kytketty päälle "Käytä osiokohtaista synteesiä", Reporter ylikirjoittaa globaalin promptin ja injektoi tekoälylle osion *oman* järjestelmäkehotteen (esim. "Senior Strategic Risk Analyst & Visual Guide"). Lisäksi tekoälylle välitetään metadatana tieto valitusta **Näkymämallista** (esim. `3D: Matrix`), jotta se ymmärtää analysoida komponenttien moniulotteisia suhteita ja tuottaa valittua asettelua tukevaa tekstiä.
*   **Tallennus:** Generoidut raporttipohjien tulosteet tallennetaan `ReportSynthesisDTO` -rakenteen alle erilliseksi listaksi (esim. `report_sections`).

---

## Vaihe 4: SDUI-käyttöliittymän XAI-ruudukko ja Ristiriitojen Ratkaisu

Käyttöliittymän "Visible XAI Extensions" -valinta määrittää, mitä laatikostoja näytölle piirretään.

### 4.1 Dynaaminen Laatikosto (Dynamic UI Grid)
*   Flutter-sovellus lukee suorituksen tuloksista `matrix_output` -rakenteen ja sen `extensions` -kartan.
*   Käyttöliittymä piirtää dynaamisen Gridin tai Card-listan ainoastaan niille extensioille, jotka on aktivoitu Tulostusprofiilissa.

### 4.2 Puuttuvien Extensioiden Ristiriidan Ratkaisu (Mismatch Protocol)
**Ongelma:** Mitä tapahtuu, jos UI-tulostusprofiilissa on rastitettu "RiskFlag", mutta yksikään matriisi koko suorituksessa ei ollut konfiguroitu tuottamaan "RiskFlag" -extensiota (LLM ei siis ole kirjoittanut sitä)?
**Ratkaisu (Graceful Degradation):**
1.  **Strict Fallback (Ensisijainen):** Backend palauttaa `extensions`-kartassa vain ne arvot, jotka oikeasti generoitiin. Jos UI yrittää etsiä "RiskFlag":ia eikä löydä sitä, se renderöi paikalle tyylikkään SDUI-virhekortin / placeholderin: *"Ei arvioitu tässä suorituksessa (Not evaluated in this workflow)"*. Tämä opettaa käyttäjää konfiguroimaan PromptBlockit oikein.
2.  **Kielletään "Post-Hoc Hallusinaatio":** Backend ei saa koskaan yrittää "keksiä" tai generoida jälkikäteen (post-hoc) puuttuvia extensioita pelkän UI-valinnan vuoksi. Se tuhoaisi XAI-jäljitettävyyden luotettavuuden. Matriisin arviointihetki on ainoa hetki, jolloin luotettavaa dataa syntyy.

---

## Vaihe 5: Läpinäkyvyyden ja Observabiliteetin Tuominen Käyttöliittymään

Komentorivityökalu `lue_tulokset.py` tarjosi aiemmin loistavan visuaalisen esimerkin siitä, miten asiantuntijamatriisin tulos ja true/false -suhteet voidaan havainnollistaa. **Huomio:** `lue_tulokset.py` on tässä Epicissä yksinomaan *käsitteellinen esikuva* tavoitellulle läpinäkyvyydelle. Se ei toimi raportointilogiikan koodipohjana uudessa järjestelmässä, vaan järjestelmällä on jo oma olemassa oleva raportointilogiikkansa. Tämä visuaalinen konsepti on nyt tuotava saumattomasti natiiviin Flutter UI:hin.

### 5.1 Backend-Tuen Varmistus ja HTTP-Payloadin Minimointi
*   `ScoringHook` (Epic 24 & 34 myötä) jo laskee matriisien tuloksiin kentät: `level_breakdown`, `true_atoms`, `false_atoms`, `total_atoms` ja `waterfall_calculation_log`.
*   **Payload-räjähdyksen esto (API Contract):** Varmistetaan, että API-rajapinnasta ulos lähtevä vastaus sisältää observabiliteettidatan välitystä varten erillisen, täysin uuden `MatrixObservabilityDTO`:n. Emme saa koskaan lähettää Flutterille `true_atoms` tai `false_atoms` -raakalistoja (jotka sisältävät raskaat `reasoning`-tekstit). `MatrixObservabilityDTO` sisältää tiukasti ainoastaan aggregaatit: `true_atoms_count: int` ja `false_atoms_count: int` (Zero-Math UI -periaatteen mahdollistamiseksi).

### 5.2 Flutter-Puolen Observabiliteetti-Komponentti
*   **Matrix Observability Accordion:** Jokaiseen näytöllä esitettävään matriisikorttiin lisätään avattava "Näytä Laskenta (Show Calculation)" -haitari.
*   **Datavisualisointi:** Tämä haitari renderöi (hyödyntäen tiukasti vain `MatrixObservabilityDTO`:n kevyttä dataa):
    1.  Tason Onnistumiset: "Taso 1: 5/10 (50%) - Flow: Optimaalinen"
    2.  Osumasuhteet: Vihreä/Punainen palkki puhtaiden lukumäärien perusteella (`true_atoms_count` vs `false_atoms_count`).
    3.  Lopullinen CDM (Cognitive Diagnostic Model) raw-arvosana.
*   Koska tämä on täysin determinististä matematiikkaa (Backendin Python-tuottamaa), se vahvistaa valtavasti järjestelmän "Zero-Math UI" -luotettavuutta.

---

## Vaihe 6: Arkkitehtuurin Invariantit ja Sääntöjen Noudattaminen (Tier 2 Hardening Compliance)

Tämän Epicin toteutuksessa on ehdottomasti noudatettava seuraavia sääntöjä (`c:\src\quorum\.agents\rules`), jotta Tier 2 hardening -työnkulut menevät virheettömästi läpi:

### 6.1 Python Backend (`01-python-backend.md`)
*   **`single_source_of_truth` (Ei Zombikoodia):** Suurin osa tarvittavasta koodista (kuten logiikka `generate_report_hook.py`:ssä ja jo olemassa olevat omat raportointilogiikat) on jo olemassa. Uutta rinnakkaista koodia tai duplikaatteja EI SAA luoda. Jos vanha koodi (esim. vanha dict-pohjainen parsinta) ei täytä Epicin uusia tiukkoja vaatimuksia, se refaktoroidaan in-place tai poistetaan kokonaan. Järjestelmään ei saa jäädä rinnakkaisia toteutuksia samasta asiasta. Vain yksi totuus.
*   **`de_generator_mandate` (Ehdottoman Dynaamisuus):** Quorumin UI (Admin Studio V2) on ylin auktoriteetti. Tekoäly ei saa KOSKAAN kovakoodata Pythoniin järjestelmäkehotteita (System Directives), tulostusrakennetta, BARS-skaaloja tai Hook-ketjuja. Kaikki nämä konfiguraatiot (kuten Admin Studion `OutputProfile` ja `PromptBlock` -näytöissä määritellyt tiedot) on luettava dynaamisesti tietokannasta. Kovakoodaus on sallittu ainoastaan hätätilan Fallback-arvoiksi (Graceful Degradation), ja silloinkin vain jos UI:sta tai kannasta ei tule mitään dataa. Kovakoodaus ei IKINÄ saa ohittaa näytöillä määriteltyjä asioita.
*   **`ANTI-TDD TRAP MANDATE` (ÄLÄ PELASTA VANHOJA TESTEJÄ):** Olemassa olevat yksikkötestit EIVÄT SAA sanella arkkitehtuuria. Tekoäly ei saa jättää koodiin kovakoodattuja merkkijonoja (kuten `"Verkkohaku"`, `"Not Assessed"`), vanhoja dict-läpikäyntejä (`isinstance(v, dict)`) tai Epic 6 jäänteitä vain siksi, että vanha Pytest-testi menisi vihreäksi. Revi vanha "frankenstein"-koodi ja laittomat LLM-mallien kovakoodaukset (esim. `gpt-4o`) säälimättä irti juurineen, ja **korjaa testit** vastaamaan uutta puhdasta Pydantic-arkkitehtuuria.
*   **`no_naked_dicts_in_state` (Ei Pydanticin ohituksia):** Koodissa ei saa olla `isinstance(existing_val, dict)` -tarkastuksia tilanhallinnassa. Kaikki validoidaan Pydantic-malleilla (esim. `GlobalContextVarsDTO`).
*   **`frozen_state_mutability`:** Kaikki DTO:t ja tila-objektit (esim. `HookState`) ovat `frozen=True`. Niitä ei saa koskaan muokata in-place (esim. `state.vars = new` tai `del dict["key"]`). Datan suodatus tai karsinta LLM:lle on tehtävä luomalla uusia kopioita (esim. `.model_copy()`).
*   **`clean_architecture_isolation`:** Hook-tiedostoilla (kuten `generate_report_hook.py`) ei saa koskaan olla suoria riippuvuuksia tietokanta-ajureihin (esim. `db.client` tai TinyDB/Firestore suorat tuonnit). Kaikki tietokantatoiminnot on hoidettava Service-kerroksen injektoiman tilan tai virallisen `UnifiedWorkflowRepository` -rajapinnan kautta.
*   **`safe_math_zero_division`:** Kaikessa Pythonilla suoritettavassa matematiikassa (erityisesti DINA-mallin osumasuhteissa ja keskiarvoissa) on taattava nollatilan suojaus. Ennen jakolaskuja on aina tarkistettava nollatila (esim. `if total_atoms > 0:`). Järjestelmä ei saa kaatua `ZeroDivisionError` -poikkeukseen, vaikka ulkoinen data olisi täysin tyhjää.
*   **`strict_pydantic_v2_rust` & `no_naked_dicts_in_state`:** Raportoinnin ja synteesin rajapinnat (esim. `ReportSynthesisDTO` ja `GlobalContextVarsDTO` tiedostossa `report.py`) on refaktoroitava täysin tyypitetyiksi. Nykytilan turvareikä `extra="ignore"` on ehdottomasti korvattava `ConfigDict(strict=True, extra='forbid')` määrittelyllä. **KRIITTISTÄ: `dict[str, Any]` tai `Any` -tyyppien käyttö on EHDOTTOMASTI KIELLETTY.** "Laiska" Any-tyypitys tuhoaa Fail-Fast -konseptin ja päästää LLM:n hallusinoimat rakenteet läpi Dart-koodigeneraattorille asti. Kaikki dynaaminen data (erityisesti `output_extensions`) on mallinnettava tiedostossa `backend_v2/models/domain/xai.py` tiukoilla polymorfisilla Discriminated Union -rakenteilla (esim. `Field(discriminator='extension_type')`).
*   **`polymorphic_routing_o1`:** Jos XAI-raporteilla tai graafeilla on erilaisia rakenteita, ne on hoidettava Discriminated Unioneilla, ei `isinstance()` -hakkeroinnilla.
*   **`ui_driven_synthesis_boundary`:** Backendin `generate_report_hook.py` EI SAA syöttää koko raakaa suoritustilaa LLM:lle (mikä aiheuttaisi TokenLimit-virheitä). Data on suodatettava tiukasti UI-tulostusprofiilin `target_blocks` -määrittelyjen mukaisesti.
*   **`strict_math_display_isolation`:** Matematiikka (raw_score) lasketaan ainoastaan `scales` taulukon absoluuttisista arvoista (`math_min`, `math_max`), ei esitystason konfiguraatioista.
*   **`no_string_l10n`:** Kaikki UI:ta ohjaavat avaimet (esim. XAI-extensioiden nimet) on välitettävä Enum-avaimina, ei raakateksteinä.

### 6.2 Flutter Frontend (`02_flutter_desktop.md`)
*   **`silent_json_fallbacks` & `no_raw_string_enum_mappings`:** Kaikkien backendiltä tulevien XAI-laajennusten nimien on mätsättävä täydellisesti `@JsonEnum()` määrittelyihin `enums.dart` tiedostossa. Tuntemattomat kentät ohjataan `Fallback`-näkymään (Graceful Degradation), niitä ei saa niellä hiljaisesti.
*   **`sized_box_shrink_ban` & `the_no_pass_rule`:** Jos XAI-raportti on virheellinen, UI:n on kaaduttava siististi `AppErrorBoundary` -komponenttiin tai näytettävä hallittu virhekortti, `SizedBox.shrink()` ei saa käyttää virheiden piilottamiseen.
*   **`o1_lists`:** Pitkät `lue_tulokset.py` -tyyliset listat atomitason erittelyistä on toteutettava puhtailla `List<T>` rakenteilla ja `@Freezed(equal: false)` estämään O(N^2) renderöintijumiutumiset, kun laatikostoja on paljon.

---

## 7. Toteutuksen Vaiheistus (Domain -> API -> UI)

Jotta tekoälyn konteksti-ikkuna (Context Window) ei ylikuormitu ja koodin laatu säilyy "Zero-Compromise" -tasolla, toteutus EHDOTTOMASTI pilkotaan tiukkaan kerrosarkkitehtuuriin.

**TIER 1 PLANNER -OHJE:** Kun purat tätä Epiciä (`/tier1-planner`), sinun ON PAKKO luoda täsmälleen kolme (3) erillistä `implementation_plan.md` -tiedostoa (esim. `phase1_domain_api.md`, `phase2_business_logic.md`, `phase3_frontend.md`). Älä koskaan yritä yhdistää näitä yhteen massiiviseen suunnitelmaan. Jokaista suunnitelmaa tullaan ajamaan itsenäisesti erillisessä Tier 2 -sessiossa.

**HUOMIO - Vain Yksi Totuus:** Suurin osa järjestelmän koodista on jo olemassa. Älä tee uusia rinnakkaisia tiedostoja (esim. `generate_report_v2.py`) tai funktioita olemassa olevien rinnalle. Uusiokäytä nykyinen koodi refaktoroimalla se in-place täyttämään Epicin säännöt. Jos vanha koodi ei ole pelastettavissa, poista se armotta. Järjestelmässä saa olla vain yksi totuus.

### Vaihe 7.1: Domain & API Layer (Backend DTOs & Enums)
Tässä vaiheessa rakennetaan datan ja rajapintojen perusta. Ei kosketa liiketoimintalogiikkaan.
1.  [ ] **[DTO Hardening & API Contract]** Refaktoroidaan `backend_v2/models/dtos/report.py` (`GlobalContextVarsDTO`, `ReportSynthesisDTO`). Luodaan uusi `MatrixObservabilityDTO` observabiliteettidatalle (joka sallii vain `true_atoms_count: int` ja `false_atoms_count: int`). Asetetaan kaikkiin `ConfigDict(extra="forbid", strict=True)`.
2.  [ ] **[Discriminated Unions]** Poistetaan kaikki `dict[str, Any]` ja `Any` -viittaukset. Dynaamiset XAI-rakenteet (`output_extensions`) on mallinnettava tiedostossa `backend_v2/models/domain/xai.py` polymorfisella Discriminated Union -rakenteella (käyttäen `Field(discriminator='extension_type')`).
3.  [ ] **[L10N Enums]** Poistetaan suomenkieliset hardkoodaukset ("Verkkohaku", "Organisaation Linjaus" yms.) ja luodaan vastaavat `ReferenceTitle` enumit `no_string_l10n` -säännön mukaisesti.

### Vaihe 7.2: Business Logic Layer (Backend Hooks)
Tässä vaiheessa koodataan itse tiedonkäsittely. Ei kosketa UI:hin.
4.  [ ] **[Clean Architecture & De-Generator]** Refaktoroidaan `generate_report_hook.py` lukemaan dynaamiset tulostusprofiilit (System Directive, näkymämallit) tiukasti joko `global_context_vars` -tilasta tai injektoidun `UnifiedWorkflowRepository` -kerroksen kautta. Varmistetaan ehdoton dynaamisuus: koodiin ei kovakoodata prompteja, vaan se kunnioittaa 100% UI:sta (Admin Studio) tulevaa dataa.
5.  [ ] **[Data Minimization & UI Boundary]** Rakennetaan hookiin aktiivinen suodatus, joka karsii Judge, Overseer yms. raakadatan ja injektoi LLM:lle EHDOTTOMASTI VAIN `target_blocks` -konfiguraation vaatimat asiantuntijamatriisit.
6.  [ ] **[Safe Math & Payload Protection]** Varmistetaan, että kaikki matematiikka (ScoringHook/DINA) sisältää absoluuttisen nollatilan suojan (`ZeroDivisionError`) ja rajapinnan (API) payload siivoaa raa'at atomitaulukot pelkiksi `true_atoms_count` / `false_atoms_count` -aggregaateiksi.

### Vaihe 7.3: Frontend & SDUI Layer (Flutter Client)
Tässä vaiheessa rakennetaan käyttöliittymä hyödyntäen uutta tiukkaa rajapintasopimusta.
7.  [ ] **[Graceful Degradation]** Toteutetaan Dart-puolen Fallback-komponentti, joka ottaa kiinni puuttuvat tai generoimattomat XAI-extensiot tyylikkäästi kaatamatta näkymää.
8.  [ ] **[MatrixObservabilityAccordion]** Rakennetaan UI-haitari arvosanojen observabiliteettiin (esikuvana `lue_tulokset.py` -konsepti, mutta täysin puhtaana Flutter-rakenteena), käyttäen VAIN rajapinnan tarjoamia aggregaatteja (`true_atoms_count`), jotta Dartin JSON Isolate ei tukehtuisi raakadataan.
