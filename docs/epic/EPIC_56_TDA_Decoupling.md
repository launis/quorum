# EPIC 56: Decoupled TDA Architecture (Zero-Variance Protocol)

> [!IMPORTANT]
> **THE CLEAN SLATE MANDATE (`the_duct_tape_ban` & `the_no_legacy_mandate`)**: Toteutamme tämän puhtaalta pöydältä (Clean Slate). Emme huomioi vanhoja ajoja tai historiallisia tietokantarakenteita. Kaikki "fallback"-ominaisuudet (esim. `obj.get('old_field')`), purkkakoodi (duct tape) ja kovakoodaus ovat ANKARASTI KIELLETTYJÄ. Jos data puuttuu, järjestelmän tulee kaatua välittömästi (Fail-Fast). Rakennamme puhdasta arkkitehtuuria ilman kompromisseja.
## 1. Tausta ja Oppimiset Ajoista (org.md -> org9.md)

Historiallisten analyysiajojen sarja (`org.md` – `org9.md`) paljasti syvällisiä arkkitehtuurisia kipupisteitä LLM:n toiminnassa ja todisti tarpeen purkaa TDA-putken (Target Data Analysis) nykyinen rakenne.

### Mitä ajoista opittiin?
1. **Varhainen Oskillaatio (org.md, 19.6 % varianssi):** 
   Ensimmäiset ajot näyttivät rajua lähes 20 % varianssia. Tämä johtui siitä, että kielimalli käytti vapaata Chain-of-Thought -päättelyä subjektiivisiin päätöksiin. Pehmeä rajanveto (esim. "onko tämä vähättelyä?") flippasi herkästi puolelta toiselle täysin samalla tekstillä API-kutsujen mikrotason kohinan vuoksi.
2. **Determinismin Illuusio ja Pydantic-vuoto (org8.md, 3.0 % varianssi):**
   Vaikutti siltä, että varianssi katosi lähes nollaan. Todellisuudessa `diff_executions.py` -skriptissä oli bugi, joka yhdisti "löydetyt lainaukset", "JSON nullit" ja LLM:n hallusinoimat haamu-nullit (esim. merkkijono `"none"`) samaan laariin (`"true"`). LLM ei siis tullut deterministisemmäksi; virheiden mittaus vain sokeutui niille.
3. **Puhdas Kognitiivinen Varianssi (org9.md, 15.6 % varianssi):**
   Kun Pydantic-skeemat tiukennettiin (Epic 55 / Haamu-nullien esto `@model_validator`:lla) ja vertailuskripti korjattiin, todellinen historiallinen varianssi paljastui. 15.6 % atomeista koki aitoa kognitiivista oskillaatiota: LLM löysi molemmilla kerroilla tismalleen saman ankkurin, mutta päätti itse logiikkavaiheessaan (`[5. VALIDATION DECISION]`) antaa toisella kerralla tuloksen `Pass` ja toisella `Fail`.
4. **The Reversal Curse (Käänteinen Logiikka):**
   Lokit todistivat kiistattomasti, että LLM kaatuu useimmiten ns. "Proof by Contradiction" -sääntöihin (esim. *"Jos väitteelle ON todisteita, palauta null"*). LLM on autoregressiivinen moottori; se on erinomainen löytämään asioita, mutta surkea päättelemään negatiivisia ehtoja tai hiljaisuutta.

## 2. Arkkitehtuurinen Ratkaisu: Decoupled TDA

Näiden oppien perusteella nykyinen arkkitehtuuri, jossa LLM sekä **etsii (Extract)** että **tuomitsee (Evaluate)**, hylätään. TDA-putki jaetaan tiukasti kahteen toisistaan eristettyyn vastuualueeseen.

### A. Semantic Extractor (Dynaaminen N-Dimensional Extraction)
LLM pelkistetään sokeaksi, mutta semanttisesti älykkääksi poimijaksi. Siltä evätään oikeus tuottaa `[5. VALIDATION DECISION]` lokiinsa. Se ei ota kantaa siihen, meneekö sääntö läpi.
Hylkäämme jäykän kaksiulotteisen (Primary/Mitigating) dikotomian. Myös staattinen `Dict`-määrittely hylätään serialisointiongelmien (Arq/Redis) vuoksi.
Sen sijaan käytämme **Dynaamista Pydantic-mallien Tehdasta (Factory)**. Pythonin `pydantic.create_model` -funktio rakentaa sisäkkäisen (nested) Pydantic-luokan dynaamisesti suorituksen hetkellä workerissa juuri ennen LLM-kutsua.
Tietokantaohjattu sääntö (`seed_data.json`) määrittää tarvittavat lokerot (esim. `facts_to_find: ["vaatimus_A", "poikkeus_B"]`). Nämä injektoidaan erilliseen sisäkkäiseen `extracted_facts` DTO-malliin propertyinä (esim. `vaatimus_A: str | None`). Tämä rakenne pelastaa AnchorValidationService:n fuzzerin sokealta kaatumiselta, koska fuzzer voi iteroida eksaktisti vain louhittavien faktojen yli, eikä yritä sokeasti fuzzata koko vastausmallia. Näin LLM saa eksaktin JSON-skeeman ja Pydanticin `extra='forbid'` toimii natiivisti ilman kontekstin siirtämistä asynkronisen jonon yli. LLM on sokea imuri, joka täyttää dynaamisesti luodun luokan `extracted_facts`-alakentät tekstistä löytyvillä lainauksilla (tai `null`).

### B. Deterministic Evaluator ja AST-Logiikka (Map-Merge-Evaluate)
Kaikkea maailman yrityslogiikkaa ei voida pelkistää yhteen Enumiin. Jotta emme menetä ilmaisuvoimaa (Expressiveness), TDA-atomin lopullinen Pass/Fail -tuomio siirretään 100 % deterministiseen Python-koodiin (`scoring.py`), joka käyttää **AST-Logiikkaa (Abstract Syntax Tree)**.

Koska dokumentit on pilkottu asynkronisiin Chunkkeihin, AST-logiikkaa **EI SAA** evaluoida Chunk-tasolla (tämä rikkoisi `not`-operaattorien globaalin totuuden). TDA-putki siirtyy **Map-Merge-Evaluate** -malliin:
1. **Map:** Jokainen Chunk-worker palauttaa sokeasti dynaamisen Pydantic-mallin (esim. `vaatimus_A` löytyi, `poikkeus_B` `null`).
2. **Merge:** Backend yhdistää kaikkien chunkkien faktat yhdeksi globaaliksi `merged_facts` -sanakirjaksi. Fakta katsotaan löytyneeksi, jos se palautuu mistä tahansa chunkista. Jos useampi chunk löytää saman faktan (esim. kaksi eri lainausta), Merge-vaihe on ratkaistava deterministisesti ("First-Wins" -strategia): tallenna **ensimmäisen** osuman tarjonneen chunkin fyysinen lainaus (kronologisesti pienin `chunk_index`). Tämä takaa, että XAI esittää käyttäjälle aina saman johdonmukaisen fyysisen lainauksen, eikä lainaus oskilloi ajokertojen välillä.
3. **Evaluate:** AST-logiikka (esim. `vaatimus_A and not poikkeus_B`) ajetaan vain kerran tälle globaalille `merged_facts` -sanakirjalle (boolean / 3-state -arviona).
Tämä poistaa 15.6 % varianssin kerralla ja mahdollistaa äärettömän monimutkaisen yrityslogiikan suorittamisen deterministisesti ilman kognitiivista epävarmuutta.

### C. Arkkitehtuurikritiikki: Päättelyvarianssi vs. Louhintavarianssi
Kuten havaittua, kognitiivisen tuomiovallan poistaminen LLM:ltä ei itsessään hävitä subjektiivisuutta; **se siirtää päättelyvarianssin (Reasoning Variance) louhintavarianssiksi (Extraction Variance)**. Jos jokin `facts_to_find` -ehto on tulkinnanvarainen, LLM oskilloi edelleen siinä, täyttääkö se kyseisen lokeron vai ei. Jos AST-logiikka sitten tuomitsee tämän sokeasti, varianssi näyttäytyy edelleen tuloksissa.

Tämä on kuitenkin tietoinen ja vahvasti perusteltu arkkitehtuurinen kompromissi:
1. **Kognitiivisen kuorman pieneneminen:** LLM:t ovat luontaisesti vahvempia hahmontunnistuksessa ja entiteettien louhinnassa (NER) kuin monimutkaisessa AST-päättelyssä ja negatiivisissa ehdoissa. Loogisten ehtojen poistaminen itse promptista vapauttaa LLM:n "Attention"-mekanismin pelkkään tekstin semantiikkaan.
2. **Few-Shot -opetuksen voima:** Louhintavarianssi voidaan tappaa lähes kokonaan antamalla konkreettisia esimerkkipareja siitä, milloin tietty fakta poimitaan. Tämä pakottaa LLM:n Pattern Matching -tilaan.
3. **Fyysisen todistusaineiston syntyminen (XAI):** Aiemmin `Fail`-päätöksen syy katosi bittiavaruuteen. Nyt, AST-puun jokaisella solmulla (faktalla) on taustallaan fyysinen lause (`extracted_facts[key]`), jonka perusteella Python-tuomio tehtiin.
4. **RapidFuzz-portinvartija:** Koska LLM palauttaa pelkkiä tekstilainauksia sanakirjassa, voimme ajaa kaikki poimitut arvot tiukan leksikaalisen tarkistuksen läpi (AnchorValidationService).

### D. Anti-Sycophancy Arkkitehtuuri (Miellyttämisenhalun tuhoaminen)
LLM:ien tunnetuin haaste on "Sycophancy" (miellyttämisenhalu / Confirmation Bias). Jos prompti käskee "Etsi vastatodiste", malli saattaa epätoivoissaan venyttää määritelmiä ja pakottaa jonkin löyhästi liittyvän lauseen kenttään vain miellyttääkseen käyttäjää. Tämä aiheuttaisi "False Negative" -räjähdyksen (atomeja hylätään Python-logiikassa turhaan).

Tämä estetään rakenteellisesti kolmella tavalla:
1. **Palkitse Poissaolo (Few-Shot as a Sycophancy Breaker):** Few-Shot -esimerkeissä annetaan ylivalta sille, että kumoava kenttä on `null`. Tämä opettaa mallin huomiomekanismille, että `null` ei tarkoita epäonnistumista, vaan se on "turvallinen" ja haluttu tila.
2. **Neutraali Muotoilu:** Prompteihin ei koskaan kirjoiteta "Etsi vastaväite", vaan neutraalimmin "Tarkista, sisältääkö kappale empiiristä dataa. Jos ei sisällä, sinun TÄYTYY palauttaa null."
3. **Nimeämisen Psykologia (Token-tason bias):** Pydantic-skeemassa vältetään adversariaalisia termejä kuten `counter_evidence` tai `nullifier`. Sen sijaan käytetään kliinisiä data-analyysin termejä kuten `empirical_modifier` tai `mitigating_context`, jotka ohjaavat mallin sisäisen roolin väittelijästä datan kerääjäksi.

### E. Kaksikanavainen Sääntöontologia (Dual-Track TDA)
Alkuperäinen arkkitehtuuriluonnos pyrki tappamaan tietoisesti LLM:n kyvyn arvioida yksittäisiä sääntöjä holistisesti. Tämä ylioptimointi "nollavarianssin" saavuttamiseksi osoittautui kuitenkin hauraaksi, koska kaikkea yrityslogiikkaa ei voida puristaa sokean sensorin muottiin menettämättä semanttista syvyyttä.

Tämän vuoksi TDA-arkkitehtuuri jaetaan **Kaksikanavaiseen Sääntöontologiaan (Dual-Track TDA)**. Kaikkia sääntöjä ei saa pakottaa sokean sensorin muottiin, vaan säännön tyyppi valitaan dynaamisesti:

1. **EXTRACTIVE_SENSOR (Sokea tiedonkerääjä):**
   - Käytetään koviin, objektiivisiin sääntöihin (esim. "Löytyykö ISO-sertifikaatti?", "Mainitaanko liikevaihto?").
   - LLM:ltä on riisuttu kaikki tuomiovalta. Se toimii vain datan poimijana (N-Dimensional Extraction).
   - Python tekee 100 % sokean, matemaattisen Pass/Fail -päätöksen AST-logiikan avulla (esim. `vaatimus_A and not poikkeus_B`).
   - Tavoitevarianssi: 0 %.

2. **COGNITIVE_JUDGEMENT (Holistinen tuomari):**
   - Käytetään subjektiivisiin ja nyansseja vaativiin sääntöihin (esim. "Onko johdon katsauksen sävy proaktiivinen?").
   - Tässä tilassa LLM ei ole vain sensori. Se tekee Pydantic-mallissa `validation_decision` (boolean) -tuomion täysin itsenäisesti.
   - **Pythonin Rooli (Auditoija):** Python ei ohita mallin päätöstä, vaan toimii riippumattomana auditoijana. Se lukee LLM:n antaman `validation_decision` -arvon, mutta ajaa RapidFuzzilla leksikaalisen tarkistuksen varmistaakseen, että LLM:n päätöksensä tueksi tarjoama fyysinen lainaus (`primary_quote`) on aidosti olemassa lähdetekstissä.
   - Tämä sallii kognitiivisen joustavuuden (Vibes-arvioinnin), mutta pakottaa sen maadoittumaan todellisuuteen (Grounded Synthesis).

### F. Lexical Fuzzing ja Event Loop Starvation -riskin hallinta
Käytämme `AnchorValidationService`:ssä `RapidFuzz`-kirjastoa (C++-pohjainen). `RapidFuzz` on aikakompleksisuudeltaan $O(N)$ verrattuna natiivin `difflib`:n hitaampaan $O(N^2)$ -kompleksisuuteen. Tästä syystä välitön "Event Loop Starvation" -riski on minimaalinen tavanomaisilla tekstichunkeilla.

Varotoimena äärimmäisiä tapauksia varten (erittäin suuret chunkit, >100k merkkiä), taklaamme kooditason riskit seuraavasti:
1. **Pakotettu Säikeistys (Thread Offloading):** `RapidFuzz`-leksikaaliset validaatiot voidaan tarvittaessa siirtää pois pääsäikeestä äärimmäisissä tapauksissa. `AnchorValidationService` käyttää `asyncio.to_thread()` -rakennetta offloadatakseen raskaat vertailut, varmistaen ettei FastAPI/Arq Event Loop pysähdy suurillakaan aineistoilla.
2. **Yhdistetty Self-Healing:** Järjestelmä ei saa suorittaa erillisiä korjausluuppeja N-Dimensional -faktakentille. Jos yksikin kenttä epäonnistuu leksikaalisessa varmennuksessa, `AnchorValidationService` nostaa yhden keskitetyn virheen, ja LLM korjaa atomin samassa ainoassa Self-Healing -kutsussa.
3. **Kognitiivisen kuorman lasku vähentää luuppeja:** Vaikka valvottavia kenttiä on useita, mallin kognitiivinen kuorma on radikaalisti pienempi. LLM:t kopioivat tekstiä huomattavasti tarkemmin silloin, kun niiden "Attention"-mekanismia ei rasiteta AST-säännöillä itse promptissa.

### G. Sokea Panikointi ja Kirurginen Virheenkäsittely
Kun malli menettää kykynsä tehdä kokonaispäätelmiä, piilee vaara ns. "Sokeassa Panikoinnissa" (Blind Panic). Jos järjestelmä palauttaa mallille geneerisen leksikaalisen virheen (*"Lainausta ei löytynyt"*), malli ei tiedä kumpi kenttä epäonnistui. Se saattaa epätoivoissaan alkaa muuttaa täydellisesti osunutta `primary_quote` -kenttää, vaikka todellinen ongelma oli hallusinoitu sana `mitigating_context` -kentässä.

Tämä neutralisoidaan "Kirurgisella Virheenkäsittelyllä" (Surgical Error Targeting):
1. Pydantic-validoinnissa (`AnchorValidationService`) kentät tarkistetaan eristetysti.
2. Jos jompikumpi kenttä epäonnistuu, luotu `SemanticEvidenceError` ei ole geneerinen, vaan se on osoitettu nimenomaiselle Pydantic-avaimelle (esim. *"Kenttä 'mitigating_context' epäonnistui, tekstiä X ei löytynyt. Kenttä 'primary_quote' oli pätevä. Korjaa ainoastaan 'mitigating_context'."*).
3. Tämä ohjaa LLM:n "Attention"-mekanismin suoraan vialliseen tokeniin ja suojaa validit kentät turhalta silpomiselta Self-Healing -luupissa.
4. **Kumulatiivisen virheen esto (Non-Accumulating Retry):** `LLMTaskExecutor` ei saa lisätä uusia `<PREVIOUS_SCHEMA_ERROR>` -blokkeja toistensa perään (kumulaatio), sillä N-ulotteisessa arvioinnissa pitkä virheloki tuhoaa Prompt Cachingin ja hukuttaa mallin. Aiempi virheblokki on korvattava uudella, ja sen maksimipituus on rajattu 500 merkkiin.

### H. Salliva Identiteetti ja Kontekstilippu (Soft Overlap & Lazy Dumping Ban)
Sokea tiedonkerääjä on riskialtis "imuri" (Vacuum Cleaner). Se saattaa kopioida tismalleen saman lauseen molempiin kenttiin oikotienä (100 % Overlap) tai dumpata kokonaisen kappaleen kenttiin (Information Dumping). 

Ehdoton lainausten päällekkäisyyden kielto (Identity Ban) kaataisi atomin tiiviissä yritysteksteissä, joissa ehto ja väite ovat fyysisesti täysin sama virke (esim. *"Toteutamme investoinnin Q3:lla, ellei korko nouse"*). Jos Python-moottorin logiikka on "hyväksy jos primary löytyy, mutta counter ei", ja malli palauttaa saman lauseen molempiin, Python-koodi osaa itse matemaattisesti hylätä tämän. Meidän ei tarvitse rangaista mallia asiasta, jonka koodi osaa ratkaista.

Arkkitehtuurinen ratkaisu on **Salliva Identiteetti yhdistettynä Laiskuuden Torjuntaan**:
1. **Salliva Identiteetti (Identity Allowance):** Pydanticin `@model_validator` sallii, että useampi `extracted_facts` -sanakirjan arvo voi olla 100 % identtinen. Pythonin AST-moottori pitää huolen siitä, että matemaattisesti tällainen tilanne johtaa oikeaan lopputulokseen, ilman että mallia rangaistaan "väärästä" kopioinnista.
2. **Pehmeä Overlap-validaattori:** Osittainen päällekkäisyys on aina sallittua (esim. yksi fakta on alimerkkijono toisesta faktasta).
3. **Laiskuuden Torjunta (Lazy Dumping Ban):** Jotta malli ei ala laiskuuttaan dumppaamaan kokonaisia tekstikappaleita kaikkiin kenttiin välttääkseen ajattelua, Pydantic-validaattoriin lisätään dynaaminen rajoite: **Laiskuus mitataan vertaamalla lainauksen kokoa koko chunkin kokoon**. Jos LLM yrittää dumpata laiskasti >80 % koko chunkin tekstistä useaan kenttään kerralla, järjestelmä kaatuu ja laukaisee Self-Healing -rangaistuksen. Yksi 300 merkin spesifi lause ei siis laukaise rangaistusta, jos se on vain murto-osa chunkista.

### I. Turvallinen Poissaolon Todistaminen (Safe Absence & Inverse Routing)
Mekaaninen sensori ei voi louhia jotain, mitä tekstissä ei ole. Aiemmin LLM:ää on yritetty ohjeistaa kognitiivisesti vaativilla säännöillä kuten "varmista, ettei X:ää ole", mikä johtaa epävarmoihin tuloksiin.

Arkkitehtuurinen ratkaisu on **AST-ohjattu Käänteinen Python-reititys yhdistettynä Turvalliseen Poissaoloon (Safe Absence)**:
LLM:ää ei koskaan ohjeisteta säännöllä "varmista, ettei X:ää ole". Malli pidetään 100 % ajasta samassa sokeassa "etsi kohteita" -moodissa. Jos AST-lauseke sisältää negatiivisen ehdon (esim. `not poikkeus_B`), LLM ei tiedä tästä negatiivisesta logiikasta mitään. Se yrittää vain löytää faktan `poikkeus_B`.

**Turvallinen Poissaolon Todistaminen (Safe Absence):** 
Kun AST-logiikka vaatii jonkin faktan poissaoloa (eli malli palauttaa kyseiselle avaimelle `null`), pelkkä `null` ei saa koskaan riittää Pythonille `Pass`-tulokseen. Tämä sallisi mallin kaatuvan "laiskuuteen". Alun perin tähän ehdotettiin pakollista `search_context_anchor` -kenttää, mutta se todettiin heikoksi (LLM voi laiskasti kopioida ensimmäisen virkkeen; lyhyillä chunkeilla triviaali). 

Sen sijaan käytämme **Chunk ID ja Trace -analyysiä**: LLM palauttaa mallissa yksinkertaisen `chunk_index` -arvon ja dokumentoi "lukemisensa" pakolliseen `context_scan_trace` -kenttään asiakirjan kielellä. `search_context_anchor` säilytetään vain *optionaalisena* (`str | None`) lisätodisteena äärimmäisiä tapauksia varten, mutta ensisijainen "lukemisen" todistus tulee siitä, että mallin purkautumiskanava (`context_scan_trace`) heijastelee kyseistä chunkkia.

**Granulaarinen DLQ-Propagointi (3-State Logic) & Käänteisen todistelun Toleranssi:** Aiempi "DLQ Strict Mode" oli matemaattisesti virheellinen ja liian aggressiivinen. Tämän vuoksi AST-moottori käyttää 3-tilaista logiikkaa (`TRUE`, `FALSE`, `DLQ`). Matemaattinen tuntemattomuus (DLQ) propagoituu AST-puussa solmu kerrallaan: `FALSE and DLQ = FALSE` (Short-circuit). Kuitenkin puhtaassa käänteisessä logiikassa (`not DLQ`) piilee vaara "DLQ Amplification" -efektistä: jos yksi epäonnistunut chunk kaataa koko 100-sivuisen asiakirjan poissaolon todistuksen. Tämän estämiseksi AST-evaluaattorin on käytettävä **DLQ Tolerance** -heuristiikkaa käänteisissä säännöissä:

*DLQ Tolerance -sääntö Inverse Routingissa:* Jos käänteistä faktaa ei löydy muista chunkeista, mutta osa chunkeista on DLQ-tilassa, `not` operaattori ei automaattisesti palauta `DLQ`:ta. Jos DLQ-tilassa olevien chunkkien osuus on pieni (esim. < 5 %) verrattuna koko asiakirjaan (>95 % puhdasta dataa), poissaolo katsotaan tilastollisesti todistetuksi ja sääntö palauttaa `TRUE`.

### J. Kultaisten Esimerkkien Tasapainotus ja Prompt Caching
Kun mallilta viedään oma järjenkäyttö tuomaroinnissa, koko TDA-putken onnistuminen kulminoituu Few-Shot -esimerkkeihin. Jos lisäisimme esimerkit jokaiseen sääntöön erikseen tietokannassa, tuhoaisimme järjestelmän Prompt Caching -hyödyt ja räjäyttäisimme API-kustannukset.

**MANDATE: 100 % Staattinen System Prompt & Prefix Caching Topologia**
Jotta maksimoimme Prompt Caching -hyödyt, `System Message` ei saa lähtökohtaisesti muuttua atomin tai ajon välillä *yhdenkään merkin* vertaa. Kaikki dynaaminen sisältö on EHDOTTOMASTI injektoitava siten, että Prefix Caching säilyy. **EHDOTON TOPOLOGIA-SÄÄNTÖ:** Valtava `document_chunk` on pakotettava heti `User Message`:n (tai `System Message`:n dynaamisen osan) AIVAN ALKUUN `<source_data>` -tägeihin. Kaikki atomin vaihtelevat, dynaamiset säännöt (kuten N-Dimensional `facts_to_find` ja natiivikieli) sijoitetaan TÄMÄN TAAKSE `<execution_parameters>` -tägiin. Jos dynaaminen sääntö laitetaan alkuun, jokainen eri atomi rikkoo välimuistin etuliitteen (Prefix) ja koko satojen kilotavujen dokumentti luetaan kalliisti uudestaan joka kerta. Tällä käännetyllä topologialla malli voi ratsastaa massiivisen dokumentin välimuistilla kaikkien sääntöjen yli.

Ratkaisu: Kultaisten esimerkkien joukko sijoitetaan yhtenä staattisena XML-blokkina (`<universal_extraction_rules>`) ylätason `System Messageen` (`PromptCompiler`). Tämän staattisen säännöstön ehdoton prioriteetti on opettaa mallille **objektiivisuutta ja sitkeyttä ilman laiskuutta**:
1. **Tasapainotettu Suhdeluku (50/50 tai max 60/40 osumien eduksi):** Esimerkkien suhdeluku ei saa tukea mallin laiskuutta. Liiallinen `null`-arvojen painotus esimerkeissä opettaa mallin luovuttamaan liian helposti. Tämän vuoksi valtaosa esimerkeistä opettaa mallin *löytämään* tiedon, mutta jättää tilaa myös perustelluille hylkäyksille.
2. **Sycophancy-ansat:** Esimerkit sisältävät ansoja (esim. tekstissä lukee epämääräisesti "toivottavasti pian", kun etsitään eksaktia rajaehtoa). Malli opetetaan hylkäämään nämä "vibat" ja palauttamaan perustellusti `null`.
3. **Edge Case -sitkeys:** Lisätään esimerkkejä, joissa malli nimenomaan palkitaan siitä, että se jaksaa kaivaa oikean tiedon monimutkaisen rakenteen, taulukoiden tai epäsuoran kielen keskeltä, sen sijaan että se valitsisi helpoimman reitin (`null`).
Näin malli ohjelmoidaan analyyttisen työkoneen rooliin, jota ei voi huijata "rivien välistä" lukemisella, mutta joka ei myöskään luovuta helposti. Koska koko System Message on 100 % staattinen, se välimuistitetaan ilmaiseksi kaikkiin ajoihin.

Satojen atomien manuaalinen refaktorointi vältetään ajamalla tietokannan läpi LLM-pohjainen migraatioskripti, joka muotoilee vanhat litaniat puhtaaseen Target/Context -rakenteeseen sekunneissa.

### K. Gaslighting-efektin Eliminointi ja Synteesin Kapinaoikeus (Right to Dissent)
Kun atomitaso tyhmennetään 1/0-sensoreiksi, koko järjestelmän inhimillinen älykkyys ja arvo siirtyvät ylätason `evaluation_notes` -synteesiin. Jos tätä ei hallita oikein, syntyy ns. **"Gaslighting-efekti"**: Synteesi saattaa holistisesti kehua raporttia upeaksi, mutta vieressä oleva Python-ohjattu matriisi hylkäsi puolet säännöistä sokeiden sensorien vuoksi. Käyttäjän luottamus romahtaa ristiriitaiseen UX:ään.

Arkkitehtuurinen ratkaisu on **Matriisikahlittu Synteesi (Matrix-Driven Judge Node) yhdistettynä Kapinaoikeuteen (Anomaly Flagging)**:
Synteesiä ei saa koskaan tuottaa samassa rinnakkaisajossa atomien poiminnan kanssa. Arkkitehtuuri pakottaa tarkan sekventiaalisen tietovirran (DAG):
1. **Extraction:** LLM-sensorit louhivat datan (rinnakkain).
2. **Evaluation:** Python laskee matriisin tulokset deterministisesti (Pass/Fail).
3. **Synthesis:** Vasta nyt herätetään Synteesi-LLM (Judge Node).

Tälle Judge-LLM:lle syötetään kontekstina (Prompt-injektio) Pythonin valmiiksi lukitsema matriisi, esim. `{'Sääntö 1 (Visio)': 'FAIL', 'Sääntö 2 (Data)': 'PASS'}`. Aiempi arkkitehtuuri pakotti Judge-Noden alistumaan täysin sokean matriisin orjaksi (pakotettu valehtelu). Nyt järjestelmään palautetaan kognitiivinen vapaus: Judge-Node saa liputtaa mekaanisen matriisin sokeat pisteet.

**Uusi Direktiivi (Englanniksi Quorum-sääntöjen mukaisesti):**
> *"You are an objective expert. Here are the Pass/Fail results from the mechanical Python matrix. Synthesize the results. HOWEVER, if you notice that the mechanical matrix has rejected/accepted a rule due to a blind keyword search that clearly contradicts the deeper nuance or conditionality of the document, you MUST flag this using the tag [CONTEXTUAL OVERRIDE] and explain to the user why the mechanical rule made an error in this context."*

Tämä tekee tekoälystä älykkään analytiikan kumppanin (Senior Analyytikko valvoo Juniorin Exceliä), ei sääntökoneen orjan. Se estää Gaslighting-efektin, mutta ei pakota mallia suostumaan sokean algoritmin tekemiin semanttisiin virheisiin.

### L. Lokiteatterin Tuhoaminen ja Kognitiivinen Pakottaminen (Micro-CoT)
Lokit osoittavat ns. "Chatter Leakage" -ilmiötä (mallin pakottava tarve selitellä) sekä "Lokiteatteria" (putkilokin syntaksin matkimista ilman oikeaa logiikkaa). Mallit oppivat myös tilastollisen oikotien: ne palauttavat `null`-arvoja heti kun vastatodisteen etsiminen tuntuu vaivalloiselta.

Ratkaisu on poistaa promptista kokonaan vaatimus tulostaa vapaamuotoinen 5-vaiheinen loki ja siirtyä puhtaaseen **Structured Outputs** -pakotukseen, jossa "purkautumiskaista" ohjataan fyysisesti oikeaan paikkaan Pydantic DTO:ssa (`prompt_compiler.py`):
1. **Kognitiivisesti Laajennettu Micro-CoT (context_scan_trace):** Asetetaan `AtomResponse` -mallin **ensimmäiseksi** kentäksi `context_scan_trace` (300–400 merkkiä). Tämä ei ole enää pelkkä ylivuotokanava, vaan todellinen *Structured Reasoning* (Chain-of-Thought) -askel.
2. **Pakotettu Relaatioanalyysi (Attention-mekanismin ohjaus):** Koska LLM tuottaa JSON-vastauksen ylhäältä alas, sen on pakko kirjoittaa tämä kenttä ensin. Malli velvoitetaan *aktiivisesti suhteuttamaan* kappaleen väitteet ja vastaväitteet toisiinsa tässä kentässä, ennen kuin se eristää ne fyysisiin quote-kenttiin. Louhintavarianssi pienenee luonnollisesti, kun malli saa luvan reflektoida löydöksiään ääneen.
3. **Haamu-nullien Äänetön Tuhoaminen (Silent Mutation):** Jos malli yrittää palauttaa tyhjää, mutta kirjoittaa vahingossa stringin "none", "N/A" tai "", emme rankaise sitä raskaalla Self-Healing -luupilla. Pydantic-validaattori muuttaa nämä kosmeettiset virheet äänettömästi oikeaksi `None`-tyypiksi. Tämä säästää tuhansia API-sekunteja tuotannossa.

### M. Semantic Normalization ja Kontekstisidonnainen Fuzzaus (Ei-tuhoava Korjaus)
Kun fuzzaus ajetaan N-lukumäärälle kenttiä, riski leksikaaliselle epäonnistumiselle moninkertaistuu. LLM:t korjaavat usein alitajuisesti typoja, tuplavälilyöntejä tai lainausmerkkien tyyppejä (" vs. ”). Raskaiden Self-Healing -luuppien estämiseksi tarvitaan "Soft Match" -mekanismi, mutta sokea Auto-Accept on vaarallinen oikotie (Spatiaalisen korruption riski), joka tuhoaisi XAI:n ylikirjoittamalla tekstiä vääristä lokaatioista.

Tämä taklataan kooditasolla tiukalla "Kontekstisidonnainen Fuzzaus ja Ei-tuhoava Korjaus" -arkkitehtuurilla:
1. **Determininen Pre-Normalisaatio:** Ennen kuin `AnchorValidationService` syöttää kentät fuzzaajalle, tekstit siivotaan deterministisesti puhtaaksi ytimeksi (pienkirjaimet, ei välimerkkejä, yhtenäiset välilyönnit).
2. **Spatiaalinen Lukitus (Spatial Bounding):** Leksikaalista vertailua ei koskaan suoriteta vapaasti koko dokumenttiin. Se rajataan tiukasti vain siihen tekstikappaleeseen (Chunk), jota LLM oli sillä hetkellä prosessoimassa. Tämä estää sen, että esimerkiksi sivun 85 virhe ylikirjoitettaisiin sokeasti sivun 2 täydellisellä osumalla.
3. **Törmäyksenesto (Collision Detection):** Ennen Auto-Acceptia järjestelmän on tarkistettava mahdolliset "kilpailevat osumat" kappaleen sisältä. Jos samankaltaisia lauseita on useita (esim. taulukon rivit, toistuvat disclaimerit), Soft Match kytkeytyy heti pois päältä. Atomi kaadetaan leksikaaliseen virheeseen ja LLM pakotetaan korjaamaan osuma itse, koska väärän arvauksen riski on liian suuri.
4. **Turvallinen Ylikirjoitus:** Vain jos spatiaalinen lukitus pätee eikä kilpailevia osumia ole (yksiselitteinen Soft Match >85 %), Python ylikirjoittaa LLM:n otteen alkuperäisen lähdetekstin absoluuttisella osumalla.
5. **Semanttinen Hätäuloskäynti (Semantic Escape Hatch):** Jos Self-Healing epäonnistuu leksikaalisessa tarkistuksessa kaksi kertaa peräkkäin (esim. erittäin likaisen PDF-OCR:n takia), kolmannella yrityksellä järjestelmä kytkee "Strict Fuzzing" pois päältä. Järjestelmä siirtyy "LLM-as-a-Judge" -varmennukseen, jossa mallia pyydetään katsomaan alkuperäistä chunkia ja vahvistamaan erikseen, onko tuotetun lainauksen merkitys 100 % sama leksikaalisista eroista huolimatta. Tämä pelastaa atomin `<PREVIOUS_SCHEMA_ERROR>` -kuolemanloukusta.

### N. Asiakirjakohtainen Kognitiivinen Silta ja Monikielisyys (Bilingual Decoupling)
Koska Quorum-arkkitehtuuri pakottaa System Promptit englanniksi mallin älykkyyden maksimoimiseksi, mutta käsiteltävät dokumentit voivat olla millä tahansa kielellä, syntyy ns. "Cross-Lingual Attention Tax". Malli joutuu kuluttamaan työmuistiaan englanninkielisten konseptien reaaliaikaiseen kääntämiseen dokumentin kielelle. Riskinä on "Translation Leakage" (malli kääntää vahingossa poimitun lainauksen englanniksi kaataen fuzzerin) tai kognitiivinen jäätyminen (malli palauttaa `null` koska kääntäminen ja poiminta samanaikaisesti on liian raskasta).

Tämä ratkaistaan "Asiakirjakohtaisella Kognitiivisella Sillalla" (Harmonized Task Language):
1. **Harmonisoitu Työkieli:** Vaikka JSON-skeemojen avaimet (`extracted_facts`, jne.) ja työkalujen tekniset kuvaukset pidetään englanniksi, **itse kognitiivinen tehtävänanto sallitaan kohdekielellä**.
2. **Kielisilta Micro-CoT:ssa:** `context_scan_trace` -kenttä (purkautumiskanava) ohjeistetaan täytettäväksi asiakirjan alkuperäisellä kielellä (esim. suomeksi). Tämä asettaa mallin "Attention"-mekanismin täydelliseen linjaan lähdetekstin kanssa.
3. **Uusi Direktiivi:** *"Lue dokumentti ja kirjaa havaintosi context_scan_trace-kenttään dokumentin ALKUPERÄISELLÄ kielellä. Tämän jälkeen poimi sanatarkat lainaukset vastaaviin kenttiin. ÄLÄ KÄÄNNÄ."*

Vaikutus: Kun malli saa jäsentää ajatuksensa samalla kielellä kuin lähdeteksti, sen neuraaliverkon "Attention"-kielikeskus kohdistuu täydellisesti oikeisiin sanoihin. Käännöshallusinaatioiden riski poistuu, koska mallin ei tarvitse hyppiä englannin ja suomen välillä juuri kriittisimmällä eristämishetkellä.

### O. Arkkitehtuurifilosofia: RAG vs. Auditointi (Evidence vs. Answer)
Alan standardit (kuten Ragas, DSPy ja yleiset RAG-sovellukset) nojaavat semanttiseen Embedding-validointiin (Cosine Similarity) puhtaan leksikaalisen fuzzauksen sijaan. Syy on ilmeinen: Embeddings on sietää typoja, piilomerkkejä ja synonyymejä, mikä säästää LLM:n raskailta Self-Healing -luupeilta ja antaa sen generoida luonnollisemmin.

**Miksi Quorum ei hylkää leksikaalista sokeaa imuria?**
Quorum ei ole RAG-järjestelmä, vaan *Auditointijärjestelmä*.
* RAG:n tavoite on antaa oikea **vastaus**.
* Auditoinnin tavoite on esittää **todiste**.

Jos käytämme vektorivalidointia, tuhoamme XAI:n (Explainable AI) ytimen eli **"Ctrl+F -Säännön"**. Jos LLM generoi "Myynti nousi 15 %" mutta alkuperäinen teksti oli "Liikevaihto kasvoi 15 %", Embedding hyväksyy tämän. Käyttäjä painaa PDF:ssä Ctrl+F eikä löydä mitään, jolloin luottamus järjestelmään romahtaa. Threshold Drift (kynnysarvon heilahtelu) muuttaisi deterministisen sääntömoottorin läpinäkymättömäksi mustaksi laatikoksi.

**Synteesi: Parhaiden puolien yhdistäminen**
Epic 56 ratkaisee tämän ristiriidan yhdistämällä mallien parhaat puolet:
1. **Ensisijainen Vaatimus (Lexical Reality):** Sokea imuri ja `RapidFuzz` pakottavat LLM:n poimimaan tekstin 100 % sanatarkasti. Jos tämä onnistuu, XAI on täydellinen.
2. **LLM-as-a-Judge -Hätäuloskäynti (Semanttinen Varmistus):** Vain jos leksikaalinen reitti on fyysisesti mahdoton (esim. korruptoitunut PDF-OCR tai vesileimat hajottavat merkit), aktivoimme Luvussa M määritellyn hätäuloskäynnin. LLM saa arvioida semanttisen samankaltaisuuden, mutta se on merkittävä eksplisiittisesti `[SEMANTIC_MATCH]` -etuliitteellä, jotta käyttäjä tietää, miksi Ctrl+F ei välttämättä toimi. 

Näin säilytämme matemaattisen audit-trailin, mutta emme kaadu likaisen reaalimaailman datan edessä.

---

## 3. Toteutussuunnitelma (Backend Engine & UI)
*Tämä Epic on 100 % itsenäinen ja sisältää sekä TDA-moottorin että siihen liittyvän Admin Studion (Frontend) käyttöliittymän päivityksen.*

### Vaihe 1: Pydantic-skeemojen rakenteellinen uudistus (Data Mappays)
- **Kohde:** Uusi tiedosto `extraction_schema_factory.py` (SRP) sekä kevyt integraatio `prompt_compiler.py`:hyn.
- **MANDATE (`prompt_compiler_immutability`):** `prompt_compiler.py` on jäädytetty arkkitehtuurin ydin ja se käyttää haurasta `lru_cache`-mekanismia. Dynaamista skeematehdasta **EI SAA** toteuttaa suoraan 994-rivisen `prompt_compiler.py`:n sisään. Kaikki logiikka on eriytettävä uuteen `extraction_schema_factory.py` -tiedostoon SRP:n mukaisesti. Koodaajan on **AINA** pyydettävä erillinen USER CONFIRMATION ennen `prompt_compiler.py`:n tuomista integraatiota varten!
- **MANDATE (`strict_pydantic_v2_rust` & `the_zero_compromise_pledge`):** Enforce strict Pydantic V2 schemas (`ConfigDict(extra='forbid', strict=True)`). Käytä natiiveja Rust-pohjaisia rakenteita (`@model_validator`). If parsing fails, DO NOT use fallbacks. Raise an explicit error and CRASH.
- **MANDATE (`deterministic_schema_generation`):** `create_model`-kutsussa kenttäjärjestys on AINA `sorted(facts_to_find)` ja factory-funktio on puhdas funktio (deterministinen tulo → tulo). Kirjoita yksikkötesti, joka varmistaa skeeman JSON-schema-hashien identtisyyden. Tämä on elintärkeää Prompt Caching -hyötyjen säilymiseksi, kun schema siirtyy Arq/Redis-jonon yli ja rekonstruoidaan workereissa.
- **MANDATE (`arq_validation_context_isolation`):** Pydantic V2:n `ValidationInfo.context` ei serialisoidu JSON:ksi Arq-jonon yli. Ota huomioon `worker.py`:n erillinen prosessi: `source_text` ja `chunk_text` on injektoitava LLM:n palauttamaan dataan vasta lokaalissa workerissa. Suorita tämä injektio Pydantic-mallille koodilla `model_validate(data, context={'source_text': chunk_text})`.
- **Toimenpiteet:**
  - Hylkää staattinen `AtomResponse` -luokka. Tee uuteen tiedostoon funktio `create_extraction_model(facts: List[str], track: Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"] = "EXTRACTIVE_SENSOR") -> Type[BaseModel]`, joka palauttaa dynaamisesti (`pydantic.create_model`) rakennetun sisäkkäisen skeeman. Rakenteen tulee noudattaa seuraavaa muotoa:
    1. Luo dynaaminen malli `ExtractedFactsDTO`, johon lisätään kaikki säännön `facts_to_find` -avaimet aakkosjärjestyksessä (`sorted()`) yksittäisinä propertyinä (`str | None`).
    2. Luo juurimalli `DynamicExtractionResponse`, jonka kenttäjärjestys on aina: **1.** `chunk_index` (int) -> **2.** `context_scan_trace` (max 400 merkkiä) -> **3.** `search_context_anchor` (str | None, optionaalinen) -> (COGNITIVE_JUDGEMENT -reitillä: **4.** `validation_decision` (bool)) -> **Viimeisenä:** `extracted_facts` (Tyyppiä `ExtractedFactsDTO`).
    
    *Arkkitehtuurinen vaatimus (Pydantic extra='forbid' -vuodon esto):*
    ```python
    def create_extraction_model(facts: list[str], track: Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"]) -> Type[BaseModel]:
        fields = {
            "chunk_index": (int, ...),
            "context_scan_trace": (str, ...),
            "search_context_anchor": (str | None, None),
        }
        if track == "COGNITIVE_JUDGEMENT":
            fields["validation_decision"] = (bool, ...)
        
        # ... luo ExtractedFactsDTO dynaamisesti facts-listan pohjalta ...
        # fields["extracted_facts"] = (ExtractedFactsDTO, ...)
        
        return create_model("DynamicResponse", **fields, __config__=ConfigDict(extra='forbid'))
    ```
  - Tuhoa promptista (`prompt_compiler.py`) täysin vaatimus tuottaa vanha 5-vaiheinen vapaa tekstiloki (`mechanical_trace`). Siirry 100 % Structured Outputs -arkkitehtuuriin eksaktilla JSON-skeemalla.
  - Kirjoita dynaamisen luokan rakentajaan (factory) mukaan dynaaminen `@model_validator` estämään "haamu-nullit".
  - Laajenna `@model_validator` sallimaan kenttien 100 % identtisyys (Identity Allowance), mutta lisää "Lazy Dumping Ban" -rajoite, joka hylkää kopioinnin vain, jos kopioitu teksti kattaa >80 % koko chunkin pituudesta. Älä käytä kiinteää merkkimäärää.

### Vaihe 2: Data Contract Migration (Downstream-komponenttien uudelleenjohdotus)
- **Kohde:** `chunk_accumulator.py`, `lightweight_matrix.py`, `scoring.py`, ja `MatrixReducer`
- **MANDATE (`fail_fast_contract_update`):** AtomResponse-luokan poistaminen rikkoo kaikki myöhemmät vaiheet, jotka odottavat `exact_quote`-, `mechanical_trace`- ja `pre_quote_anchor` -kenttiä. Olemassa olevaa purkkakoodia ei saa kirjoittaa, vaan DTO-contractit on päivitettävä eksplisiittisesti.
- **MANDATE (`no_naked_dicts_in_state`):** Merge-vaihe ei saa tuottaa paljasta ("naked") Python-sanakirjaa. Globaali aggregaatiotila on mallinnettava `MergedFactsDTO` Pydantic-mallina (perii `V2CoreBase`), joka käyttää `ConfigDict(extra='allow')` dynaamisten kenttien tallentamiseen.
- **Toimenpiteet:**
  - **MergedFactsDTO (Merge-tilan vakiointi):** Luo uusi DTO aggregoidulle tilalle. Esimerkki:
    ```python
    class MergedFactsDTO(V2CoreBase):
        """Global aggregation of all chunk extraction results."""
        model_config = ConfigDict(extra='allow', frozen=True)
        
        search_context_anchors: dict[str, str] = Field(default_factory=dict)
        dlq_chunk_indices: list[int] = Field(default_factory=list)
        
        def get_fact_state(self, key: str) -> Literal["TRUE", "FALSE", "DLQ"]:
            ...
    ```
    Määrittele kuinka Chunkkien palauttamat dynaamiset mallit yhdistetään tähän DTO:hon.
  - **ChunkAccumulator päivitys:** Refaktoroi `ChunkAccumulator` poistamalla odotus `exact_quote` -kentästä. Accumulator **ei saa yhdistää dataa asynkronisesti pala kerrallaan** "in-flight", jotta vältetään samanaikaiset tietokantakirjoitukset ja `frozen_state_mutability`-mandaatin rikkoutuminen. Kaikki chunk-workerien palauttamat Pydantic-objektit työnnetään listaan, ja Map-Reduce -arviointi suoritetaan yhdellä deterministisellä Reducer-operaatiolla vasta kun kaikki workerit ovat palauttaneet tuloksensa.
    
    *Arkkitehtuurinen vaatimus (Race Condition -esto):*
    ```python
    def reduce_extracted_facts(chunk_responses: list[DynamicExtractionResponse]) -> MergedFactsDTO:
        # Deterministic sort ensures perfect XAI parity regardless of execution speed
        sorted_responses = sorted(chunk_responses, key=lambda x: x.chunk_index)
        merged = {}
        for response in sorted_responses:
            for fact_key, quote in response.extracted_facts.model_dump().items():
                if fact_key not in merged and quote is not None:
                    merged[fact_key] = quote # First-Wins guaranteed by sorting
        return MergedFactsDTO(facts=merged)
    ```
  - **AtomEvaluationItemDTO päivitys:** Päivitä `AtomEvaluationItemDTO` (`lightweight_matrix.py`) hylkäämällä vanhat yksittäiset quote-kentät ja ottamalla käyttöön `extracted_facts: dict[str, str | None]` -kenttä.
  - **Scoring.py uudelleenjohdotus:** Refaktoroi `scoring.py`-hookin evaluaatioluuppi (rivit 560-706) lukemaan arviot uudesta `merged_facts` -rakenteesta vanhan staattisen DTO:n sijaan, jotta AST-moottori saa tarvitsemansa syötteen.

### Vaihe 3: Deterministinen AST-Arviointimoottori (Scoring ja Data-Driven OCP)
- **Kohde:** `seed_data.json` & `scoring.py` (Poista `EvaluationStrategy` Enum kokonaan säännöistä).
- **MANDATE (`zero_db_hardcoding_mandate`):** Arviointilogiikka ei saa koskaan nojata kovakoodattuihin tietokanta-ID:hin. Reitityksen on oltava 100 % polymorfista AST-logiikan pohjalta.
- **MANDATE (`the_no_legacy_mandate`):** Obsolete code, ALL fallback chains, and legacy test fixtures MUST be ruthlessly deleted.
- **MANDATE (`ast_security_protocol`):** Vältä EHDOTTOMASTI `eval()`-funktion käyttöä `logical_expression`-merkkijonon evaluoinnissa. Se on luokiteltava epäluotettavaksi (user input) koska admin voi muokata sitä UI:n kautta (Prompt Injection Pythonissa). AST-parseri on rajattava tiukalla Whitelist-filtterillä ainoastaan yksinkertaisiin Bool/Unary-operaatioihin (`ast.And`, `ast.Or`, `ast.Not`, `ast.Name`, `ast.BoolOp`, `ast.UnaryOp`, `ast.Expression`).
- **MANDATE (`matrix_scoring_dlq_math`):** Matriisitason luottamuspisteiden (`system_confidence`) laskenta on määriteltävä eksplisiittisesti. **EHDOTON KIELTO:** DLQ-sääntöjä EI SAA poistaa nimittäjästä (ei optimistista `effective_total`-laskentaa). DLQ-tilaan päätynyt sääntö pisteytetään matemaattisesti nollana (0/1), jolloin matriisin tulos pysyy pessimistisenä ja luotettavana. Tällaiselle matriisille asetetaan käyttöliittymää varten erillinen "Data Quality Flag" (esim. Keltainen "Puutteellinen data" -merkintä). Aseta lisäksi kova kipuraja: jos `dlq_count / total > 0.10`, koko matriisi on asetettava suoraan tilaan `INDETERMINATE` laadun takaamiseksi.
- **MANDATE (`ast_evaluator_srp_mandate`):** AST-evaluaattori on puhtaasti matemaattinen funktio ilman sivuvaikutuksia. Sitä **EI SAA** toteuttaa sisäkkäin `scoring.py`:n raskaaseen I/O-logiikkaan. Eriytä se omaan testattavaan moduuliinsa (esim. `ast_evaluator.py`), jossa on eksplisiittiset `validate_expression` ja `evaluate` -metodit. Tämä takaa 100 % yksikkötestattavuuden ilman mockeja.
- **MANDATE (`dlq_guard_hook_mandate`):** DLQ-tilojen tarkistukset ja kipurajan laskenta (`dlq_count / total > 0.10`) on itsenäinen liiketoimintasääntö. Sitä **EI SAA** upottaa `scoring.py`:n sisään. Toteuta DLQ-logiikka erillisenä Pre-Scoring Hookina (`dlq_guard.py`) SRP-periaatteen ja testattavuuden varmistamiseksi.
- **Toimenpiteet:**
  - **Turvallinen 3-State AST-evaluaattori (`ast_evaluator.py`):** Toteuta whitelistattu turvaportti ja granulaarinen DLQ-propagointi lausekkeen suorittamiseksi. Käänteistä todistelua varten on integroitava DLQ Tolerance -mekanismi "DLQ Amplification" -efektin estämiseksi. Pseudokoodiesimerkki:
    ```python
    ALLOWED_OPS = {ast.And, ast.Or, ast.Not, ast.Name, ast.BoolOp, ast.UnaryOp}
    
    # Instead of pure boolean algebra, use a heuristic threshold for missing data
    def calculate_inverse_dlq_tolerance(total_chunks: int, dlq_chunks: int, found_state: bool) -> Literal["TRUE", "FALSE", "DLQ"]:
        if found_state is True:
            return "FALSE" # The exception was found, automatically invalidates the rule
        if (dlq_chunks / total_chunks) > 0.05:
            return "DLQ" # Too much data is missing to safely assume absence
        return "TRUE" # 95%+ of the document is clean, absence is statistically proven

    def eval_ast(node, merged_facts: dict[str, Literal["TRUE","FALSE","DLQ"]], total_chunks: int, dlq_chunks: int):
        match node:
            case ast.Name(id=name):
                return merged_facts.get(name, "DLQ")
            case ast.UnaryOp(op=ast.Not(), operand=inner):
                inner_val = eval_ast(inner, merged_facts, total_chunks, dlq_chunks)
                # Apply DLQ Tolerance instead of blind 'not DLQ = DLQ'
                return calculate_inverse_dlq_tolerance(
                    total_chunks=total_chunks, 
                    dlq_chunks=dlq_chunks, 
                    found_state=(inner_val == "TRUE")
                )
            case ast.BoolOp(op=ast.And(), values=vals):
                results = [eval_ast(v, merged_facts, total_chunks, dlq_chunks) for v in vals]
                if "FALSE" in results: return "FALSE"  # Short-circuit
                if "DLQ" in results: return "DLQ"
                return "TRUE"
    ```
  - **Map-Merge-Evaluate (Python):** Toteuta `scoring.py`:hyn uusi AST Evaluator. Koodaa ensin **Merge**-vaihe, joka yhdistää asynkronisten Chunkkien palauttamat dynaamiset Pydantic-tulokset yhdeksi globaaliksi `merged_facts` -sanakirjaksi (`TRUE`, `FALSE`, `DLQ`).
  - **DLQ Strict Mode Guard (Pre-Hook):** Erota DLQ-tilojen kipuraja- ja validointilogiikka omaan rekisteröitävään hookkiinsa (`backend_v2/hooks/dlq_guard.py`), joka ajetaan juuri ennen varsinaista `scoring.py`-ajokertaa.
    ```python
    @hook_registry.register(name="dlq_strict_mode_guard")
    def dlq_strict_mode_guard(state: HookState, deps: HookDependencies) -> HookResult:
        """Pre-hook: Evaluates DLQ thresholds and logic before main scoring."""
        ...
    ```
  - **Ohjauspyörä (Dual-Track Routing & UI/Tietokanta):** Päivitä `TDAAssertion` (esim. `v2_core.py`) ja `seed_data.json` sisältämään uudet ohjauskentät:
    ```python
    class TDAAssertion(V2CoreBase):
        evaluation_track: Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"] = "EXTRACTIVE_SENSOR"
        facts_to_find: list[str] = Field(default_factory=list)
        logical_expression: str | None = None
    ```
    `evaluation_track` reitittää atomin joko sokeaan mekaaniseen putkeen tai harvinaisissa poikkeustapauksissa inhimillisen tason kognitiiviseen päättelyyn.
  - **Reititin:** Refaktoroi `calculate_rule_satisfied` -metodi parsimaan `logical_expression` turvallisesti whitelistin läpi ja evaluoimaan se AST-puuna vasten globaalia `merged_facts` -sanakirjaa.
  - Varmista, että Python-koodi palauttaa puhtaan `True/False` booleanin (tai `INDETERMINATE`). COGNITIVE_JUDGEMENT -tyyppiset säännöt voidaan evaluoida `validation_decision == True` AST-lausekkeella.

### Vaihe 4: Promptien ja Seed Datan siivous (HITL-Migraatio)
- **Kohde:** `backend_v2/seed/seed_data.json` ja tietokantamigraatio
- **Toimenpiteet:**
  - **Sääntöjen Aivopesu (Radical Rule Stripping):** Siivoa tietokannasta (Seed Data) säälimättä pois kaikki loogiset säännöt, kiellot ja ehtolauseet (esim. *"EXTRACTION CONDITION", "BANNED SOURCES", "NEGATIVE CONDITION"*).
  - **Semantic Signature -migraatio (Bilingual Decoupling):** Rakenna säännöt LLM-migraatioskriptillä puhtaaksi "Etsintäkuulutukseksi" (Semantic Signature). Target on pelkkä lause, jossa monimutkainen ilmiö on pelkistetty binääriseksi valinnaksi. **HUOM:** Vaikka system prompt on englanniksi, Semantic Signaturet on käännettävä/rakennettava kohdedokumentin **käyttäjän natiivikielelle**, jotta vältetään Cross-Lingual Attention Tax.
  - **Tiedonhävikin esto (Legacy-kenttä):** Tallenna vanha monimutkainen sääntökuvaus uuteen `legacy_description` -tietokantakenttään turvaamaan historiaa.
  - **Inverse Routing -täydennys:** Varmista skriptissä, että jos alkuperäinen sääntö kielsi jotain, uuden atomin `evaluation_strategy` arvoksi asetetaan `REQUIRE_ABSENCE`.
  - **Human-in-the-Loop (HITL):** Skripti generoi ensin Review-tiedoston (esim. CSV) manuaaliseen tarkistukseen.
  - **MANDATE (`high_fidelity_prompting_and_caching` & `hybrid_prompting_mandate`):** Kaikkien promptien on oltava "Hybrid Prompteja" (XML-tagit markdownin sisällä). Lisää "Golden Few-Shot" -esimerkit täysin staattiseen `<universal_extraction_rules>` XML-blokkiin. Tämä on kriittistä Prompt Caching -finopsille.
  - **MANDATE (`native_language_system_prompts` & `native_english_generation_mandate` Poikkeus):** System promptin rakenteet (XML-tägit, JSON-avaimet) pidetään englanniksi, mutta **Asiakirjakohtaisen Kognitiivisen Sillan** vuoksi `context_scan_trace` ja sääntöjen semanttinen sisältö sallitaan/pakotetaan asiakirjan natiivikielelle (esim. suomeksi).

### Vaihe 5: Tilan muistava Leksikaalinen Validointi (AnchorValidationService)
- **Kohde:** `AnchorValidationService.py` ja `llm_task_executor.py`
- **MANDATE (`infinite_retry_loops` & `llm_structured_execution_mandate`):** Luota ainoastaan `LLMTaskExecutor.execute_structured_task()` -luuppiin Pydantic-korjauksissa. Varmista, että `SystemConcurrency.LLM_MAX_RETRIES` on tiukasti 2.
- **MANDATE (`non_accumulating_error_mandate`):** Refaktoroi `LLMTaskExecutor` siten, että uusi `<PREVIOUS_SCHEMA_ERROR>` -blokki **korvaa** vanhan blokin User Messagessa, eikä appendata (lisätä) sen perään. Virheviestin kokonaispituus on rajattava tiukasti (esim. 500 merkkiin), jotta vältetään Prompt Caching -hyötyjen menettäminen.
- **Toimenpiteet:**
  - Poista "Trace Contradiction Ban" (koska LLM ei enää tuota tuomiota).
  - **MANDATE (`event_loop_protection`):** Aja `RapidFuzz`-tarkistus (Lexical Reality) `asyncio.to_thread()`:in läpi suurille chunteille (>100k merkkiä) estääksesi workerin jäätymisen.
  - **Pre-Fuzzing Normalization:** Muuta sekä lähdeteksti että LLM:n palauttamat otteet puhtaiksi ytimiksi (pienkirjaimet, ei erikoismerkkejä, ei tuplavälejä) ennen `RapidFuzz`-vertailua.
  - **Spatiaalinen Lukitus (Spatial Bounding):** Rajaa fuzzaus-haku pelkästään aktiiviseen tekstikappaleeseen (Chunk). Älä etsi osumia globaalisti koko dokumentista.
  - **Törmäyksenesto (Collision Detection):** Jos fuzzer löytää yli yhden kilpailevan osuman (esim. >85 % samankaltaisuudella), hylkää Auto-Accept välittömästi ja laukaise poikkeus pakottaaksesi LLM:n korjaamaan otteen itse.
  - **Turvallinen Ylikirjoitus:** Säädä `score_cutoff` 85.0:aan. Vain yksiselitteisen osuman kohdalla päivitä (override) LLM:n palauttama teksti alkuperäisestä lähdetekstistä kaivetulla täydellisellä osumalla.
  - **Lokaali Semanttinen Silta (TF-IDF / Embedding):** Optimoi "Self-Healing" -kustannukset vähentämällä raskaita API-kutsuja. Jos `RapidFuzz` palauttaa osuman harmaalla alueella (75.0 % - 84.9 %), aja välitön, lokaali semanttinen vertailu (esim. nopea TF-IDF tai lokaali Word2Vec/SBERT) alkuperäisen lähdetekstin ehdokkaan ja LLM:n palauttaman lainauksen välillä. Jos lokaali vertailu vahvistaa semanttisen vastaavuuden, hyväksy osuma välittömästi ilman uutta LLM-kutsua.
  - **Viimeinen Semanttinen Hätäuloskäynti (LLM-as-a-Judge):** Toteuta laskuri `locked_state`:n yhteyteen. Vasta kun osuma jää alle 75 % (tai lokaali silta epäonnistuu) ja sama avain epäonnistuu leksikaalisesti kaksi kertaa peräkkäin, palauta Pydantic-virheen mukana hätäkehotus LLM:lle: *"Text not found exactly. As a judge, confirm if the semantic meaning is 100% identical. If yes, return the text with [SEMANTIC_MATCH] prefix."* Jos prefix löytyy, bypassaa `RapidFuzz`.
  - **Tilan muistava lukitus (Stateful Locking):** Estä "Whack-a-Mole" -korjausluupit ylläpitämällä `locked_state` -sanakirjaa. **MANDATE (`frozen_state_mutability`):** DTO:ita ei saa mutatoida in-place (esim. `obj.quote = "X"` on kielletty, koska `frozen=True`). Käytä AINA `obj.model_copy(update={'quote': "X"})` palauttaaksesi lukitun tilan!
  - **Kirurginen Virheviesti:** Nosta poikkeus (`SemanticEvidenceError`), joka palauttaa `locked_state`:n orchestratorille ja ohjeistaa LLM:ää promptissa. **MANDATE (`native_language_system_prompts`):** Virheviesti (Prompt) on kirjoitettava **ENGLANNIKSI** (esim. *"Field Y was PERFECT. DO NOT CHANGE IT. Only fix field X."*). Suomenkieliset virheviestit LLM:lle ovat ankarasti kiellettyjä.

### Vaihe 6: Universal Quality Gate & Testaus (TDD Mandate)
- **Kohde:** `backend_audit_loop.py` & Test Suite
- **MANDATE (`mocking_mandate_for_llm`):** Live LLM calls during tests are strictly forbidden. You MUST ABSOLUTELY use mocked JSON fixtures via `backend_v2/llm/mock.py` and `polyfactory`.
- **MANDATE (`deterministic_testing_delegation`):** You are the worker, Python is the judge. The `backend_audit_loop.py` enforces >90% coverage. Code is not complete until it passes the CI script locally.
- **MANDATE (`documentation_parity`):** Koodin ja arkkitehtuurin muuttuessa `docs/architecture/` -hakemiston dokumentit sekä `.agents/rules/04_directory_reference.md` on EHDOTTOMASTI päivitettävä. Hakemistoviittaukset (Hakemistokartta) eivät saa vanhentua uuden rakenteen myötä.

### Vaihe 7: Frontend (Admin Studio UI) Päivitys
- **Kohde:** `client_app_v2/lib/features/studio/`
- **Toimenpiteet:**
  - Päivitetään Atomin (`TDAAssertion`) muokkausnäkymä. 
  - Poistetaan vanha `ai_rule_description` -megakenttä. 
  - Tilalle rakennetaan uudet Data-Driven -komponentit:
    1. `TARGET` -tekstikenttä
    2. `CONTEXT` -tekstikenttä
    3. `FACTS TO FIND` -lista (N-Dimensional faktat)
    4. `LOGICAL EXPRESSION` -kenttä (AST-logiikan syöttämiseen).
  - Tämä vaihe voidaan toteuttaa täysin itsenäisesti riippumatta muista Epiceistä.
