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
*   **Varmistus:** Varmistetaan, ettei yksikään LLM-prompti enää yritä laskea osumaprosentteja tai tuottaa JSON-kenttiä matemaattisille raaka-arvoille.

### 1.2 Matrix Output Extensions -sukupolvi
*   LLM generoi asiantuntijamatriiseille ("category_id": "matrix") sanalliset arviot suoraan konfiguroituihin `output_extensions` -kenttiin (esim. `justification`, `falsification`, `coaching`).
*   Nämä generoidaan Matrix-vaiheessa, ja ne ohitetaan FinOps-kompressiossa (jo korjattu `ContextBuilder`:ssa), joten ne kulkeutuvat muuttumattomina loppuraporttiin.

---

## Vaihe 2: FinOps ja Kontekstin Kompressio (Data Minimization Strategy)

Kaikkien atomisoitujen väitteiden käyttöönotto (`MATRIX_SAMPLING_LIMIT = 0`) luo massiivisen uhan järjestelmän vakaudelle, mikäli dataa ei hallita tiukasti. Työnkulun kaatuminen (`TokenLimitExceededError (239704 > 100000)`) oli suora seuraus siitä, että sokean arvioinnin raaka data pääsi vuotamaan raportoivalle LLM:lle asti.

### 2.1 Kontekstin Säälimätön Karsiminen (Ruthless Pruning via ContextBuilder)
*   **Ongelma:** `ChunkWorker`-solmut tuottavat jokaiselle yksittäiselle atomille monisanaisen perustelun (`reasoning`). Sadan atomin arvioinnissa pelkkä perustelu-dump paisuu välittömästi satoihin tuhansiin merkkeihin.
*   **Best Practice -Ratkaisu:** `ContextBuilder` puuttuu väliin juuri ennen kuin `$global_context_vars` (tai muu tila) injektoidaan LLM:n kontekstiin (esim. XAI Reporter -vaiheessa). Se etsii massiiviset `evaluations`-taulukot ja "puristaa" ne säälimättä puhtaaksi totuusarvolistaksi (`evaluations_bool_only: [True, False, True...]`).
*   **Skaalautuvuus (Scale):** Pelkkä totuusarvolista kuluttaa vain kourallisen tokeneita (esim. 100 atomia = ~150 tokenia). Tämän myötä 100 000 tokenin kontekstiraja ei tule enää vastaan, vaikka matriisi arvioisi 10 000 atomia. Token-räjähdys on estetty arkkitehtuurin juuritasolla.

### 2.2 LLM-Payloadin Minimointi vs. Pythonin Maksimointi
*   **LLM saa MINIMI-datan:** XAI Reporter tai Executive Coach -LLM saa nähtäväkseen ainoastaan matriisien tuottamat korkean tason aggregaatit: `normalized_score` sekä matriisin tuottamat asiantuntijasynteesit (`output_extensions`). Sille *ei* koskaan syötetä yksittäisiä atomeja, koska sen tehtävä on ainoastaan laatia makrotason "Johdon yhteenveto".
*   **Python hoitaa MAKSIMI-datan:** Kaikki raskaat tietorakenteet, kuten atomien luupit, alkuperäiset tekstit ja mikrotason osumat (`true_atoms`, `false_atoms`) elävät yksinomaan Pythonin RAM-muistissa ja tietokannassa. Python suorittaa kaiken DINA-laskennan omalla prosessoritehollaan, mikä pitää API-kustannukset nollassa ja LLM:n prosessointinopeuden salamannopeana.

---

## Vaihe 3: Tulostusprofiilien ja Raporttipohjien Dynaaminen Injektio

Käyttöliittymä antaa dynaamisia prompteja ("Senior Executive Coach" ja "Visual Analyst"). Nämä on kytkettävä `XAI Reporter` -solmun ytimeen.

### 3.1 Johdon Yhteenvedon (Executive Summary) Generointi
*   **Mekanismi:** Kun `XAI Reporter` aloittaa, se hakee tietokannasta suoritukseen sidotun tulostusprofiilin (`OutputProfile`).
*   **Promptin Injektio:** Se lukee profiilista *Synteesi- ja vientiasetukset* -lohkon system_directive -promptin. Tämä prompti asetetaan suoraan LLM:n järjestelmäohjeeksi (System Message).
*   **Konteksti:** Sisään syötetään kompressoitu `matrix_data` (josta atomit on piilotettu, mutta `output_extensions` on mukana).

### 3.2 Dynaamiset Raporttipohjat (Report Templates 1-n)
*   **Mekanismi:** `OutputProfile` voi sisältää listan erillisiä raporttipohjia (esim. "3D Matrix: Toulmin - Goodhart - Kahneman").
*   **Iteratiivinen Suoritus:** `XAI Reporter` käy läpi kaikki 1-n raporttipohjaa.
*   **Kohdekomponenttien (Axis X, Y, Z) Suodatus:** Reporter etsii globaalista kontekstista tarkalleen ne matriisit, jotka on kytketty käyttöliittymän pudotusvalikoista komponentteihin 1, 2 ja 3.
*   **Raporttipohjan Promptaus:** Reporter lähettää tekoälylle erillisen kyselyn (jossa on kyseisen raporttipohjan prompti, esim. "Visual Analyst") ja syöttää kontekstiksi *vain* X, Y ja Z akselien matriisien DTO-tulokset ja raw-arvosanat.
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

## Vaihe 5: Läpinäkyvyyden ja Observabiliteetin Tuominen Käyttöliittymään (`lue_tulokset.py`)

Komentorivityökalu `lue_tulokset.py` tarjosi erinomaisen läpinäkyvyyden siihen, miten asiantuntijamatriisin tulos on muodostunut. Tämä on tuotava saumattomasti Flutter UI:hin.

### 5.1 Backend-Tuen Varmistus
*   `ScoringHook` (Epic 24 & 34 myötä) jo laskee ja injektoi matriisien tuloksiin kentät: `level_breakdown`, `true_atoms`, `false_atoms`, `total_atoms` ja `waterfall_calculation_log`.
*   Varmistetaan, että `LightweightMatrixOutput` DTO ja `ReportSynthesisDTO` todella säilyttävät nämä kentät rajapintavastaukseen asti.

### 5.2 Flutter-Puolen Observabiliteetti-Komponentti
*   **Matrix Observability Accordion:** Jokaiseen näytöllä esitettävään matriisikorttiin lisätään avattava "Näytä Laskenta (Show Calculation)" -haitari.
*   **Datavisualisointi:** Tämä haitari renderöi:
    1.  Tason Onnistumiset: "Taso 1: 5/10 (50%) - Flow: Optimaalinen"
    2.  Osumasuhteet: Vihreä/Punainen palkki (`true_atoms` vs `false_atoms`).
    3.  Lopullinen CDM (Cognitive Diagnostic Model) raw-arvosana.
*   Koska tämä on täysin determinististä matematiikkaa (Backendin Python-tuottamaa), se vahvistaa valtavasti järjestelmän "Zero-Math UI" -luotettavuutta.

---

## Vaihe 6: Arkkitehtuurin Invariantit ja Sääntöjen Noudattaminen (Tier 2 Hardening Compliance)

Tämän Epicin toteutuksessa on ehdottomasti noudatettava seuraavia sääntöjä (`c:\src\quorum\.agents\rules`), jotta Tier 2 hardening -työnkulut menevät virheettömästi läpi:

### 6.1 Python Backend (`01-python-backend.md`)
*   **`strict_pydantic_v2_rust` & `no_naked_dicts_in_state`:** Raportoinnin ja synteesin rajapinnat (esim. `ReportSynthesisDTO`) on oltava täydellisesti tyypitettyjä. `ConfigDict(strict=True, extra='forbid')` on pakollinen.
*   **`polymorphic_routing_o1`:** Jos XAI-raporteilla tai graafeilla on erilaisia rakenteita, ne on hoidettava Discriminated Unioneilla, ei `isinstance()` -hakkeroinnilla.
*   **`ui_driven_synthesis_boundary`:** Backendin `generate_report_hook.py` EI SAA syöttää koko raakaa suoritustilaa LLM:lle (mikä aiheuttaisi TokenLimit-virheitä). Data on suodatettava tiukasti UI-tulostusprofiilin `target_blocks` -määrittelyjen mukaisesti.
*   **`strict_math_display_isolation`:** Matematiikka (raw_score) lasketaan ainoastaan `scales` taulukon absoluuttisista arvoista (`math_min`, `math_max`), ei esitystason konfiguraatioista.
*   **`no_string_l10n`:** Kaikki UI:ta ohjaavat avaimet (esim. XAI-extensioiden nimet) on välitettävä Enum-avaimina, ei raakateksteinä.

### 6.2 Flutter Frontend (`02_flutter_desktop.md`)
*   **`silent_json_fallbacks` & `no_raw_string_enum_mappings`:** Kaikkien backendiltä tulevien XAI-laajennusten nimien on mätsättävä täydellisesti `@JsonEnum()` määrittelyihin `enums.dart` tiedostossa. Tuntemattomat kentät ohjataan `Fallback`-näkymään (Graceful Degradation), niitä ei saa niellä hiljaisesti.
*   **`sized_box_shrink_ban` & `the_no_pass_rule`:** Jos XAI-raportti on virheellinen, UI:n on kaaduttava siististi `AppErrorBoundary` -komponenttiin tai näytettävä hallittu virhekortti, `SizedBox.shrink()` ei saa käyttää virheiden piilottamiseen.
*   **`o1_lists`:** Pitkät `lue_tulokset.py` -tyyliset listat atomitason erittelyistä on toteutettava puhtailla `List<T>` rakenteilla ja `@Freezed(equal: false)` estämään O(N^2) renderöintijumiutumiset, kun laatikostoja on paljon.

---

## Yhteenveto ja Toimenpiteet (Action Items)

1.  [ ] **[Backend]** Varmistetaan, että `XAI Reporter` (`generate_report_hook.py`) hakee `OutputProfile` -taulusta dynaamiset promptit (Executive Summary + Report Templates).
2.  [ ] **[Backend]** Refaktoroidaan `generate_report_hook.py` tukemaan "kohdekomponenttien" (X, Y, Z -akselien matriisien) injektiota suoraan template-pohjaisille prompteille.
3.  [ ] **[Frontend]** Vahvistetaan Flutter-puolen Fallback-komponentti (Graceful Degradation) puuttuvien XAI-extensioiden varalle.
4.  [ ] **[Frontend]** Rakennetaan `MatrixObservabilityAccordion` Flutteriin, joka esittää `true_atoms`/`false_atoms` suhteet `lue_tulokset.py` -tyylisesti suoraan API:n palauttamasta DTO:sta.
