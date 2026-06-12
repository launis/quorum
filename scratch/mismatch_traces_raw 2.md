# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ympäristö ja Konteksti (Execution State)
- **Git / Epic -tila:** Branch: night-shift-2026-06-05-1458 | Commit: 04ed7f17 - feat: implement best-of-three LLM execution strategy with minority veto and enhanced unit test coverage (Thu Jun 11 15:13:00 2026 +0300)
- **Kriittiset järjestelmäarvot (Enums):**
  - **EvaluationRunCount**: ENSEMBLE = 3, STANDARD = 1
  - **VerificationResult**: VERIFIED = RESULT_VERIFIED, DEBUNKED = RESULT_DEBUNKED
  - **SystemConcurrency**:
    - MAX_CONCURRENT_WORKFLOWS = 10
    - MAX_CONCURRENT_LLM_STEPS = 15
    - LLM_MAX_RETRIES = 4
    - LLM_RETRY_MULTIPLIER = 2
    - LLM_RETRY_MIN_SECONDS = 1
    - LLM_RETRY_MAX_SECONDS = 30
    - LLM_RETRY_JITTER_INITIAL_SECONDS = 1
    - LLM_RETRY_JITTER_EXP_BASE = 2
    - FAIL_FAST_MAX_RETRIES = 1
    - LLM_MAX_CHUNK_SIZE = 15
    - MATRIX_SAMPLING_LIMIT = 0
    - LLM_DEFAULT_TIMEOUT_SECONDS = 600
    - RATE_LIMIT_COOLDOWN_SECONDS = 10
    - SEMAPHORE_LOW_RPM_THRESHOLD = 20
    - SEMAPHORE_LOW_RPM_LIMIT = 2
    - SEMAPHORE_MAX_CONCURRENCY = 50
    - SEMAPHORE_RPM_DIVISOR = 10
    - MAX_SAFE_TOKENS = 1000000
    - SCHEMA_MAX_LOCALIZED_ANCHORS = 15
    - SCHEMA_MAX_EVALUATIONS = 15
    - SCHEMA_MAX_CHUNK_RECORDS = 15
    - CONTEXT_CACHE_LOCK_TTL_SECONDS = 300
    - CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600
    - CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS = 500
    - CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS = 20
    - CONTEXT_CACHE_MINIMUM_TOKEN_LIMIT = 2048
    - PACING_DELAY_VERTEX_SECONDS = 0
    - PACING_DELAY_OPENAI_SECONDS = 0
    - PACING_DELAY_MOCK_SECONDS = 0
    - REDIS_CONNECTION_TIMEOUT_SECONDS = 10
- **Vertailtavat ajot (R1, R2...):**
  - **R1:** `exe_b4cd9c3dd4ae401e86fe56f3c3ddf982`
  - **R2:** `exe_4babefe56f334cb093d2e9e7a9ff2187`
- **Aktiiviset Säännöt ja Asetukset (Frozen Context):**
  - **Vastuullisuus (Turvallisuus- ja Etiikkasuodatin)** (`blk_80732a33fe1947ee`) - [R1: 0P/15F] [R2: 0P/14F]
  - **Oman tiedon rajat (Episteeminen Nöyryys)** (`blk_22e3598e06414409`) - [R1: 2P/13F] [R2: 5P/9F]
  - **Harkintakyky (Kahnemanin Kaksoisprosessiteoria)** (`blk_109dab5b6b3f403a`) - [R1: 4P/5F] [R2: 6P/3F]
  - **Päättelyn rehellisyys (Kausaalinen ja Abduktiivinen Integriteetti)** (`blk_c3bc5f3eb8e74110`) - [R1: 3P/12F] [R2: 5P/10F]
  - **Väitteiden perustelu (Toulminin Argumentaatiomalli)** (`blk_440a5fef9331451b`) - [R1: 4P/11F] [R2: 7P/8F]
  - **Itsensä haastaminen (Falsifioinnin Auditointi)** (`blk_b476f89fb732448c`) - [R1: 2P/13F] [R2: 2P/13F]
  - **Syy-seuraussuhteet (Kausaalisuuden Analyysi)** (`blk_c5804a9143c34cb1`) - [R1: 0P/15F] [R2: 2P/13F]
  - **Ohjeiden noudattaminen (Arkistointistandardien Auditointi)** (`blk_fb15f8dcf23f4865`) - [R1: 1P/14F] [R2: 1P/14F]
  - **Avoimuus (Selitettävyys ja Läpinäkyvyys)** (`blk_f6e286f050c94d60`) - [R1: 2P/13F] [R2: 3P/12F]
  - **Luovuus ja syvyys (Bloomin Taksonomia)** (`blk_f921c7c0989b47e8`) - [R1: 1P/17F] [R2: 1P/17F]
  - **Prosessiomistajuus (Ylituomari)** (`blk_ff72c2d79edb4ebf`) - [R1: 4P/11F] [R2: 4P/11F]
  - **Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)** (`blk_53f32679aa514fcb`) - [R1: 2P/12F] [R2: 3P/12F]
  - **Luottamusarvio (XAI-Raportoija)** (`blk_6b8c766185294f7e`) - [R1: 2P/7F] [R2: 2P/7F]

## Ajojen Lähdetiedostot ja Syötteet
- **Run 1:** `exe_b4cd9c3dd4ae401e86fe56f3c3ddf982` (Lähde: [data/files/executions\exe_b4cd9c3dd4ae401e86fe56f3c3ddf982\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_b4cd9c3dd4ae401e86fe56f3c3ddf982/execution_trace.json))
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_b4cd9c3dd4ae401e86fe56f3c3ddf982/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_b4cd9c3dd4ae401e86fe56f3c3ddf982/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_b4cd9c3dd4ae401e86fe56f3c3ddf982/inputs/input_reflection_text.md)
- **Run 2:** `exe_4babefe56f334cb093d2e9e7a9ff2187` (Lähde: [data/files/executions\exe_4babefe56f334cb093d2e9e7a9ff2187\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_4babefe56f334cb093d2e9e7a9ff2187/execution_trace.json))
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_4babefe56f334cb093d2e9e7a9ff2187/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_4babefe56f334cb093d2e9e7a9ff2187/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_4babefe56f334cb093d2e9e7a9ff2187/inputs/input_reflection_text.md)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 183
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 89.07 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.6388
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.6422
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1093
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 20 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 0 / 20
- **PASSED -> FAILED:** 3
- **FAILED -> PASSED:** 17
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_dff85ed8a43a4ca99c34873b2fe44d89` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt syntaktisia ankkureita, kuten 'mikä suoraan aiheuttaa' tai 'tämän mekanismi on', jotka määrittelisivät eksplisiittisesti tarkan kausaalimekanismin datan ja väitteen välillä. Vaikka kausaalisuhteita kuvataan, ne eivät sisällä yksityiskohtaista mekanismin kuvausta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa 'mikä ajaa suoraan siihen, että' on tarkka kausaalinen kieli. Väite ('Tämä syntyy') on tuettu empiirisellä datalla ('Luonnon kantokyky murenee'), ja tarkka mekanismi ('aja suoraan siihen, että Talouden perusta rakoilee') on määritelty. Kaikki kolme elementtiä (väite, data, mekanismi) ovat eksplisiittisesti läsnä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_18fd37ad3f1f4903a812c12346d0ca8e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Lähdetekstissä on useita kausaalisia lauseita, kuten 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.' Näissä lauseissa syy ja seuraus on nimetty eksplisiittisesti (esim. 'Luonnon kantokyky murenee' ja 'Talouden perusta rakoilee'), eikä yhteys ole vain implisiittinen. Siksi negatiivinen ehto täyttyy, ja palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa on suora kausaalinen yhteys ('syntyy siitä, että', 'mikä ajaa suoraan siihen, että'), jossa syy ('Luonnon kantokyky murenee') ja seuraus ('Talouden perusta rakoilee') on nimetty eksplisiittisesti. Yhteys ei ole vain implisiittinen, joten negatiivinen ehto ei täyty ja poiminta tehdään.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ca74247488fe49d49c70e96cf74a31a7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt viittausta tai tietolähteen esittelyä (esim. 'mukaan', 'tiedot osoittavat'), jonka yhteydessä termit kuten 'harha', 'virhemarginaali' tai 'rajoitus' olisivat täysin puuttuneet samasta kappaleesta.*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Viittaus 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023' löytyy otsikko-osiosta. Tässä kappaleessa ei ole mainintoja termeistä 'harha', 'virhemarginaali' tai 'rajoitus'.*

---

### Atom-ID: `tda_71e60846894545b2bc43a3361b7a5a9c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Käyttäjän syötteistä ei löytynyt socratic-tyyppisiä käsitteellisiä kysymyksiä, kuten 'mihin oletukseen' tai 'miksi päädyit', jotka aktiivisesti tutkisivat AI:n perusteluja tai pakottaisivat sen puolustamaan logiikkaansa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Käyttäjä esitti sokraattisen käsitteellisen kysymyksen, joka aktiivisesti tutkii taustalla olevaa päättelyä ja pyytää tekoälyä harkitsemaan uusien luokittelumallien mahdollisuutta ('supermegatrendejä').  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_3a362e01de66444c813e5b79adec27bf` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt absoluuttisia johtopäätössanoja (esim. 'selvästi', 'on oltava'), jotka esitettäisiin ilman monivaiheista loogista päättelyä. Johtopäätökset ovat yleensä edeltävän tekstin tukemia, eikä yksittäistä irrotettua, perusteetonta absoluuttista johtopäätöstä löytynyt.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa käytetään absoluuttista johtopäätössanaa 'osoittaa' ('shows/indicates'), ja johtopäätös esitetään ilman monivaiheista loogista päättelyä välittömässä kontekstissa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_cb7637a8eae04303ae9a3e8085b075b4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt faktuaalista väitettä, jossa olisi ollut kvalifioivia termejä (esim. 'osoittaa', 'viittaa', 'korreloi') ja samalla absoluuttiset markkerit (esim. 'todistaa', 'aina') olisivat puuttuneet samasta lauseesta.*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lause sisältää kvalifioivan termin 'osoittaa' ('indicates/shows'), eikä siinä ole samassa lauseessa absoluuttisia merkintöjä kuten 'todistaa' tai 'aina'.*

---

### Atom-ID: `tda_8ecd3f17b3984e4fa1bb6a8cb5576b65` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' käytetään absoluuttista kausaalisanaa 'ainoa tapa' ja se liittää monimutkaisen lopputuloksen ('pitkän aikavälin vakaus') yhteen ainoaan syyhyn ('Korjaavaan ja uusintavaan talouteen siirtyminen'). Teksti ei tunnista useita tekijöitä tai vivahteita tässä kohtaa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0b7512034e6f40db9b4ea46b64af4e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Käyttäjän kehotteessa 'koosta näistä vastauksista 1 sivun raportti' on direktiiviverbi 'koosta' ja mitattavissa oleva kynnys '1 sivun'. Koska mitattavissa oleva kynnys on läsnä, negatiivinen ehto täyttyy, ja siksi palautetaan null.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Käyttäjä antaa direktiivin 'varmista', mutta ei määrittele mitattavaa kynnystä, spesifistä viitekehystä tai kvantifioitavaa mittaria sille, mitä 'kohdallaan' tarkoittaa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_7e0d493a62234375b180d942cb6e0bcd` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' löytyy intervention merkki ('mikä ajaa suoraan siihen, että') ja odotettu lopputulos ('Talouden perusta rakoilee').  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ac3b078498e048889ad3bc46b634c2ee` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Lause 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023' on akateeminen viittaus. Vaikka koko dokumentin logiikka perustuu näihin raportteihin, tämä spesifinen lause on vain passiivinen viittaus eikä aktiivisesti sovella lähdemateriaalin sääntöä tai kehystä. Siksi negatiivinen ehto täyttyy, ja palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Teksti viittaa eksplisiittisesti 'Sitran Megatrendiraportit 2017, 2020, 2023' -lähteeseen. Lause 'Sitran megatrendien kehitys vuosien 2017 ja 2023 välillä osoittaa fundamentaalisen siirtymän...' sitoo analyysin suoraan näihin raportteihin ja niiden sisältöön, osoittaen logiikan olevan eksplisiittisesti sidottu lähteeseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6e3e3aa6b9134a01838c3b70a35b4f32` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt syntaktisia ankkureita, kuten 'liittyy', 'yhdistetään' tai 'vaikuttaa', jotka yhdistäisivät dataa väitteeseen ilman tarkan kausaalimekanismin määrittelyä. Tekstissä esiintyvät yhteydet ovat usein kuvattuja kausaalisina tai selittävinä, eivät pelkästään heikkoina assosiaatioina.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa 'vaikuttavat' (impacts/affect) on heikko assosiatiivinen kieli, joka yhdistää datan (supermegatrendit) väitteeseen (talousjärjestelmän vakaus) määrittelemättä tarkkaa kausaalista mekanismia. Vaikka yhteys on mainittu, mekanismia ei ole kuvattu.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_69cc84e0b0c44996a8a95e09b356c692` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt syntaktisia ankkureita, kuten 'siksi', 'näin ollen' tai 'joten', jotka yhdistäisivät kaksi faktaa ilman selittävää mekanismia. Tekstissä esiintyvät kausaalisuhteet sisältävät yleensä jonkinlaisen selityksen tai kontekstin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa 'mikä ajaa suoraan siihen, että' toimii äkillisenä siirtymämerkkinä, joka yhdistää kaksi tosiasiaa ('Luonnon kantokyky murenee' ja 'Talouden perusta rakoilee') ilman, että selittävää mekanismia kuvataan eksplisiittisesti. Se ilmaisee suoran seurauksen, mutta ei mekanismin yksityiskohtia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_569a2c551bae4301b1217c8a7107cc2c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *AI-vastauksessa 'Sitran megatrendiraporttien perusteella näkymä tulevaisuuteen on siirtynyt potentiaalista ja nousevista ilmiöistä (2017) kohti kasautuvia, geopoliittisesti latautuneita kriisejä ja systeemisiä murtumia (2023).' on kausaalinen väite ('on siirtynyt'). Lause sisältää numeerista tietoa ('2017', '2023'), joka täyttää 'empiirisen datan sanaston' ehdon. Koska empiiristä dataa sisältävää sanastoa löytyi, negatiivinen ehto täyttyy, ja siksi palautetaan null.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa esitetään kausaalinen väite ('Evoluutio on...'), mutta se ei sisällä empiiristä dataa (esim. lukuja, prosentteja, mittauksia) väitteen tueksi.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_003f932abb9642fc8c3147b04fac95c5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt absoluuttisia täydellisyyden markkereita (esim. 'tyhjentävä', 'kattaa kaiken', 'ainoa mahdollinen', 'ainoa tapa'), jotka väittäisivät nollaa tuntematonta muuttujaa tai vaihtoehtoa.*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lause sisältää absoluuttisen täydellisyyden merkinnän 'ainoa tapa', joka väittää, ettei muita vaihtoehtoja ole pitkän aikavälin vakauden takaamiseksi.*

---

### Atom-ID: `tda_a946688e5f5549e8ac30584d1a02ad26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [TRUE]:**
  > *Ensimmäisessä kappaleessa, joka sisältää faktuaalista raportointia, ei ole ensimmäisen persoonan markkereita (esim. 'minä', 'me', '-mme', '-ni', '-n').*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [FALSE]:**
  > *Tekstin johtopäätöksessä esiintyy ensimmäisen persoonan monikon possessiivi 'Yrityksemme', mikä tarkoittaa, että ensimmäisen persoonan merkintöjen määrä ei ole tasan nolla.*

---

### Atom-ID: `tda_2d59c195d8324fc0a22838ef53417686` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [TRUE]:**
  > *Kappale 'Johtopäätös' sisältää lauseen, joka arvioi positiivista lopputulosta ('Yrityksemme menestys riippuu...'). Tässä kappaleessa tai sen välittömässä läheisyydessä ei ole episteeemisiä raja- tai epävarmuusmerkkejä (kuten 'kuitenkin', 'rajoitus', 'epävarmuus'). Siksi poimintaehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [FALSE]:**
  > *Vaikka 'Sitran Strateginen Suunta' -osiossa kuvataan positiivisia saavutuksia, lause 'Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta**' sisältää episteeemisen raja-arvon ('rajoite'). Tämän vuoksi täydellisen poissaolon ehto ei täyty, ja palautetaan null.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_65541c8fa62649038b52553cad9eab8a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [TRUE]:**
  > *Teksti sisältää vertailevan merkin 'sen sijaan että'. Se nimeää eksplisiittisesti kaksi erillistä lähestymistapaa ('Sitran näkemys suunnasta eteenpäin' ja 'pelkkä toivetila') ennen kuin valitsee toisen ja kuvaa sitä tarkemmin. Tämä vastaa säännön ehtoja.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [FALSE]:**
  > *Tekstistä ei löytynyt tapausta, jossa vertailevaa merkkiä olisi käytetty, mutta vain yksi lähestymistapa olisi käsitelty. Kaikki löydetyt tapaukset vertailivat eksplisiittisesti kahta erillistä lähestymistapaa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_92680081ffb244d8abbdc99120a3291f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt absoluuttisia varmuusmarkkereita (esim. 'kiistatta', '100%', 'todistettu fakta'), joita ei olisi perusteltu empiirisellä tiedolla samassa kappaleessa.*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lause sisältää absoluuttisen varmuuden merkinnän 'ei ole' ('there is not'), eikä kyseisessä kappaleessa esitetä empiiristä tietoa tämän väitteen perustelemiseksi.*

---

### Atom-ID: `tda_7b88a578c3824b31b83a5154f7d3667a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Tekstistä ei löytynyt kausaalisia harppauksia, jotka yhdistäisivät toisiinsa liittymättömiä piirteitä tai priorisoisivat vain näkyvää todistusaineistoa tehden lopullisen johtopäätöksen rajoitetun tiedon perusteella ja jättäen huomiotta tuntemattomat tekijät. Kausaalisuhteet esitetään osana Sitran megatrendien kehystä, ei puutteellisena päättelynä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Teksti vetää suoran kausaalisen johtopäätöksen ('syntyy siitä, että', 'mikä ajaa suoraan siihen, että') kahden ilmiön välille perustuen esitettyyn näyttöön, mutta ei aktiivisesti tunnista tai käsittele tuntemattomia tekijöitä tai muita mahdollisia syy-seuraussuhteita.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c512ea7305614bfabf468fe838420dda` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b4cd9c3dd4ae401e86fe56f3c3ddf982) - [FALSE]:**
  > *Käyttäjän 'reflection_text'-osiossa arvioidaan lopputulosta. Siinä mainitaan 'muuttelin yksityiskohtia', 'otin mielestäni asioita pois', 'muutin myös tulosta' ja 'Korjasin taulukosta Eurooppaan liittyvän asian'. Nämä osoittavat, että alkuperäisessä tuloksessa oli puutteita tai rajoituksia, jotka vaativat korjausta. Koska rajoituksia käsitellään, negatiivinen ehto täyttyy, ja siksi palautetaan null.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_4babefe56f334cb093d2e9e7a9ff2187) - [TRUE]:**
  > *Lauseessa esitetään positiivinen arvio lopputuloksesta ('onnistuivat tunnistamaan'), mutta samassa kappaleessa ei mainita lainkaan rajoituksia, epäonnistumisia tai reunatapauksia.  [5. VALIDATION DECISION: FAIL]*

---

