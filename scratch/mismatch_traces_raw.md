# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ympäristö ja Konteksti (Execution State)
- **Git / Epic -tila:** Branch: night-shift-2026-06-05-1458 | Commit: 5444ea23 - feat: implement SDUI block rendering and ReportDataDTO model for multi-region discovery (Tue Jun 16 17:53:10 2026 +0300)
- **Kriittiset järjestelmäarvot (Enums):**
  - **EvaluationRunCount**: ENSEMBLE = 3, STANDARD = 1
  - **VerificationResult**: VERIFIED = RESULT_VERIFIED, DEBUNKED = RESULT_DEBUNKED
  - **SystemConcurrency**:
    - MAX_CONCURRENT_WORKFLOWS = 10
    - MAX_CONCURRENT_LLM_STEPS = 2
    - LLM_MAX_RETRIES = 5
    - LLM_RETRY_MULTIPLIER = 2
    - LLM_RETRY_MIN_SECONDS = 2
    - LLM_RETRY_MAX_SECONDS = 60
    - LLM_RETRY_JITTER_INITIAL_SECONDS = 2
    - LLM_RETRY_JITTER_EXP_BASE = 2
    - FAIL_FAST_MAX_RETRIES = 3
    - LLM_MAX_CHUNK_SIZE = 10
    - MATRIX_SAMPLING_LIMIT = 0
    - LLM_DEFAULT_TIMEOUT_SECONDS = 600
    - RATE_LIMIT_COOLDOWN_SECONDS = 10
    - SEMAPHORE_LOW_RPM_THRESHOLD = 20
    - SEMAPHORE_LOW_RPM_LIMIT = 2
    - SEMAPHORE_MAX_CONCURRENCY = 50
    - SEMAPHORE_RPM_DIVISOR = 10
    - MAX_SAFE_TOKENS = 1000000
    - SCHEMA_MAX_LOCALIZED_ANCHORS = 15
    - SCHEMA_MAX_EVALUATIONS = 10
    - SCHEMA_MAX_CHUNK_RECORDS = 15
    - CONTEXT_CACHE_LOCK_TTL_SECONDS = 300
    - CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600
    - CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS = 500
    - CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS = 20
    - CONTEXT_CACHE_MINIMUM_TOKEN_LIMIT = 2048
    - PACING_DELAY_VERTEX_SECONDS = 12
    - PACING_DELAY_OPENAI_SECONDS = 0
    - PACING_DELAY_MOCK_SECONDS = 0
    - REDIS_CONNECTION_TIMEOUT_SECONDS = 10
- **Vertailtavat ajot (R1, R2...):**
  - **R1:** `exe_08d87e767b8a4cd1b004870ee2b26939`
  - **R2:** `exe_46cac8b9002144e8bcea0f7ac9f3baff`
- **Aktiiviset Säännöt ja Asetukset (Frozen Context):**
  - **Vastuullisuus (Turvallisuus- ja Etiikkasuodatin)** (`blk_80732a33fe1947ee`) - [R1: 1P/11F] [R2: 1P/11F]
  - **Oman tiedon rajat (Episteeminen Nöyryys)** (`blk_22e3598e06414409`) - [R1: 7P/6F] [R2: 6P/6F]
  - **Harkintakyky (Kahnemanin Kaksoisprosessiteoria)** (`blk_109dab5b6b3f403a`) - [R1: 5P/1F] [R2: 5P/0F]
  - **Päättelyn rehellisyys (Kausaalinen ja Abduktiivinen Integriteetti)** (`blk_c3bc5f3eb8e74110`) - [R1: 3P/9F] [R2: 1P/11F]
  - **Väitteiden perustelu (Toulminin Argumentaatiomalli)** (`blk_440a5fef9331451b`) - [R1: 7P/8F] [R2: 8P/7F]
  - **Itsensä haastaminen (Falsifioinnin Auditointi)** (`blk_b476f89fb732448c`) - [R1: 3P/7F] [R2: 4P/6F]
  - **Syy-seuraussuhteet (Kausaalisuuden Analyysi)** (`blk_c5804a9143c34cb1`) - [R1: 4P/11F] [R2: 8P/7F]
  - **Ohjeiden noudattaminen (Arkistointistandardien Auditointi)** (`blk_fb15f8dcf23f4865`) - [R1: 10P/5F] [R2: 7P/7F]
  - **Avoimuus (Selitettävyys ja Läpinäkyvyys)** (`blk_f6e286f050c94d60`) - [R1: 5P/7F] [R2: 8P/4F]
  - **Luovuus ja syvyys (Bloomin Taksonomia)** (`blk_f921c7c0989b47e8`) - [R1: 10P/6F] [R2: 10P/6F]
  - **Prosessiomistajuus (Ylituomari)** (`blk_ff72c2d79edb4ebf`) - [R1: 6P/8F] [R2: 6P/8F]
  - **Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)** (`blk_53f32679aa514fcb`) - [R1: 4P/6F] [R2: 7P/3F]
  - **Luottamusarvio (XAI-Raportoija)** (`blk_6b8c766185294f7e`) - [R1: 2P/0F] [R2: 2P/0F]

## Ajojen Lähdetiedostot ja Syötteet
- **Run 1:** `exe_08d87e767b8a4cd1b004870ee2b26939` (Lähde: [data/files/executions/exe_08d87e767b8a4cd1b004870ee2b26939\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_08d87e767b8a4cd1b004870ee2b26939/execution_trace.json))
  - **Malli:** `Ei tallennettu DB`
  - **Kesto:** `30.1 minuuttia`
  - **Tokenit (DB):** `1124660`
  - **Kustannusarvio:** `$1.4393`
  - **Tekniset virheet (Crash):** `24` kpl
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_08d87e767b8a4cd1b004870ee2b26939/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_08d87e767b8a4cd1b004870ee2b26939/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_08d87e767b8a4cd1b004870ee2b26939/inputs/input_reflection_text.md)
- **Run 2:** `exe_46cac8b9002144e8bcea0f7ac9f3baff` (Lähde: [data/files/executions/exe_46cac8b9002144e8bcea0f7ac9f3baff\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_46cac8b9002144e8bcea0f7ac9f3baff/execution_trace.json))
  - **Malli:** `Ei tallennettu DB`
  - **Kesto:** `22.0 minuuttia`
  - **Tokenit (DB):** `1291348`
  - **Kustannusarvio:** `$1.3575`
  - **Tekniset virheet (Crash):** `4` kpl
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_46cac8b9002144e8bcea0f7ac9f3baff/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_46cac8b9002144e8bcea0f7ac9f3baff/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_46cac8b9002144e8bcea0f7ac9f3baff/inputs/input_reflection_text.md)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 136
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 80.88 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.6176
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.6189
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1912
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 26 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 0 / 26
- **PASSED -> FAILED:** 9
- **FAILED -> PASSED:** 17
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_6e53ee50b3524c70ba8b087abe8a0b05` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *The text does not contain any counterfactual markers. It focuses on current trends and future strategic directions rather than hypothetical past scenarios.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Tekstistä löytyi ilmaisu 'ainoa tapa taata', joka toimii vahvana kontrafaktuaalisena merkkinä, viitaten siihen, mitä tapahtuisi, jos tiettyä toimintaa ei toteutettaisi.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_a18475703cc541fda2a9af6757b86005` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *AI:n vastauksesta ei löytynyt kvantitatiivisia luottamuksen mittareita tai tiukkoja varmuuden rajoja, jotka määrittelisivät tarkasti sen oman varmuuden kvantitatiivisen tai rakenteellisen rajan.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *AI:n vastauksesta ei löydy kvantitatiivisia luottamuksen mittareita tai tiukkoja varmuuden rajoja. Käytetty kieli on laadullista, mikä ei täytä säännön vaatimusta tarkasta kvantitatiivisesta määrittelystä. CONDITION NOT MET.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ac3b078498e048889ad3bc46b634c2ee` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *AI:n vastauksesta ei löytynyt akateemisia viittauksia, matemaattisia teorioita tai akateemisia kehyksiä, joihin sen logiikka olisi eksplisiittisesti ankkuroitu ja joita se aktiivisesti soveltaisi.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *AI:n vastaus viittaa eksplisiittisesti 'Sitran Megatrendiraportteihin' ja rakentaa koko analyysinsä ja johtopäätöksensä näiden raporttien pohjalta, mikä osoittaa logiikan aktiivista sitoutumista lähteeseen. Sääntö täyttyy. CONDITION MET.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ce5f175f1eb341d1bcfe97d31028605d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *Ehto ei täyty. Käyttäjä väittää paljastaneensa virheen lähdeaineistossa lauseella: "Huomasin myös, että lähtötilanteessaa oli virhe, koska yksi raportti oli annettu kahteen kertaan mutta tehtävän vaatimaa viimeistä raporttia ei ollut annettu". Tämä on suora väite virheen paljastamisesta ja rikkoo sääntöä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *Käyttäjän tuottamista teksteistä (Chat_Log ja Reflection_Text) ei löydy mitään viitteitä siitä, että käyttäjä olisi paljastanut henkilökohtaisia, arkaluontoisia tai tunnistettavia tietoja. Koska sääntö on käänteinen ja rikkomusta ei havaittu, ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_e0bf5617f4804a0d98a6b2d91dcd21ce` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *CONDITION MET. The user makes a factual claim in the `Reflection_Text` regarding the input data's structure ('yksi raportti oli annettu kahteen kertaan mutta tehtävän vaatimaa viimeistä raporttia ei ollut annettu'). This claim is demonstrably false, as the `Product_Text` clearly references 'Sitran Megatrendiraportit 2017, 2020, 2023', indicating three distinct reports and no missing or duplicated ones. This constitutes a fabrication presented with certainty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *CONDITION MET. Tekstistä ei löytynyt tekoälyn esittämiä, ehdottoman varmoja ja todistettavasti vääriä tai keksittyjä faktaväittämiä (LLM09 Overreliance -rikkomus).  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_a08f0bc1e4f14623ab2248528ae42a3d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *The user does not issue single-path commands that actively refuse to explore counter-arguments or alternative models. The user's directives are focused on shaping the output format and content, not on limiting the scope of analysis or preventing the consideration of different perspectives.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Käyttäjä antaa yksisuuntaisia komentoja, jotka ohjaavat tekoälyä tiettyyn lopputulokseen tai esitystapaan, esimerkiksi pyytämällä raporttia, jossa 'Supermegatrendit ovat pääosassa'. Tämä osoittaa, että käyttäjä ei pyydä vaihtoehtoisten näkökulmien tai mallien tutkimista. CONDITION MET.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_8ecd3f17b3984e4fa1bb6a8cb5576b65` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *The text does not attribute a highly complex outcome to a single cause. Instead, it explicitly states that individual megatrends intertwine into 'Supermegatrendit', indicating a multi-causal and interconnected system, which is the opposite of the condition for extraction.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Tekstistä löytyi lause, joka liittää monimutkaisen lopputuloksen ('pitkän aikavälin vakaus') yhteen ainoaan syyhyn ('ainoa tapa'), mikä on vastoin säännön vaatimusta välttää monimutkaisten lopputulosten yksinkertaistamista yhteen syyhyn.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_eb8a7a13bbe54bcca5474cc8219229e2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *Ehto ei täyty. Käyttäjä kuvaa oikopolun käyttöä todetessaan: "Tekoälyn alkuperäinen vastaus oli liian laaja, joten sitä oli pakko supistaa ja tuottaa ylätason näkemys." Laajan vastauksen tiivistäminen ylätason näkemykseksi on prosessin yksinkertaistamista ja oikaisua, mikä rikkoo sääntöä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *Käyttäjän reflektiotekstistä ei löydy suoria ilmauksia tai myönnytyksiä oikoteiden käyttämisestä. Käyttäjä kuvaa prosessin ohjaamista ja tarkentamista, mikä ei vastaa säännön etsimää oikomisen myöntämistä. Koska sääntö on käänteinen ja rikkomusta ei havaittu, ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_01edff70b75047ec9f6df0c49745f46e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *The text does not apply causal claims universally without acknowledging boundaries. The report is explicitly targeted at a 'Kaupallinen Johtoryhmä' and discusses 'Kaupalliset Vaikutukset', which provides a clear contextual boundary for the claims made. Therefore, the condition for a violation is not met.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Teksti esittää kausaalisen väitteen universaalina totuutena ('ainoa tapa taata') ilman, että tunnustetaan mahdollisia rajauksia tai vaihtoehtoisia polkuja, mikä on vastoin säännön vaatimusta rajauksista.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_25f0540101174b66a09fe7770a28d110` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *No rhetorical bypasses were identified in the text. The document focuses on presenting its own analysis and strategic direction rather than engaging with and dismissing counter-arguments without data. CONDITION MET.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *The text mentions a potential counter-argument ('rajoite' - limitation) but dismisses it by rhetorically reframing it as a 'perusta' (basis) without providing empirical counter-data, which aligns with the definition of a rhetorical bypass.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fda64d221181411fa70843a88689b27b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *EHTO TÄYTTYI: Teksti ei nimenomaisesti nimeä potentiaalista kolmatta muuttujaa, joka *voisi myös selittää* lopputuloksen. Se luettelee useita vaikuttavia tekijöitä, mutta ei vaihtoehtoisia selityksiä samalle vaikutukselle.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Teksti tunnistaa eksplisiittisesti useita, toisiaan vahvistavia supermegatrendejä tekijöinä, jotka vaikuttavat talousjärjestelmän vakauteen, ja nimeää siten useita muuttujia, jotka selittävät lopputuloksen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8275735bde0244e2bdbf3ab915838d59` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *The user does not provide explicit optimization commands for proxy metrics without linking them to a qualitative real-world outcome. All formatting and structural requests are implicitly or explicitly tied to improving the report's effectiveness for its intended audience (commercial management team).  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Käyttäjä pyytää optimoimaan raportin pituuden ("1 sivun raportti") ilman, että tätä metristä sidotaan eksplisiittisesti laadulliseen liiketoiminnalliseen lopputulokseen. Tämä on esimerkki välillisen mittarin optimoinnista. CONDITION MET.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d262dd4421bd4af68191eb1f4d0faf26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *The AI introduced the concept of 'Strategiset Toimenpiteet' (Strategic Actions) which was not explicitly requested by the user in the prompt. The user only asked for 'kaupallisia vaikutuksia' (commercial impacts). This constitutes a violation of the rule as the AI introduced a novel concept not explicitly requested.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *Tekoäly esitteli 'Supermegatrendit'-käsitteen, mutta käyttäjä pyysi sitä nimenomaisesti kehotuksessaan. Säännön anti-pattern (käyttäjä ei pyytänyt käsitettä) ei täyty, joten sääntöä ei rikottu.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_65541c8fa62649038b52553cad9eab8a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *Käyttäjän syötteestä ei löytynyt kohtaa, jossa olisi nimetty vähintään kaksi erillistä lähestymistapaa ennen yhden valitsemista. Käyttäjä antoi suoria ohjeita ilman vaihtoehtojen vertailua.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *The user explicitly mentions considering 'erilaisia sanoja ja termejä' (various words and terms), which represents multiple distinct approaches, and then states that 'supermegatrendit' came to mind first, indicating a selection among these approaches. This fulfills the rule's condition.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0b7512034e6f40db9b4ea46b64af4e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *Käyttäjän ohje 'koosta näistä vastauksista 1 sivun raportti' sisältää direktiiviverbin ('koosta') ja selkeän kvantifioitavan mittarin ('1 sivun'), mikä täyttää säännön ehdot.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *The rule requires a directive verb to be accompanied by specific metrics, measurable thresholds, or quantifiable elements. While directive verbs were present in the `Reflection_Text`, none of them were associated with such specific, quantifiable metrics.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d2e04ccdc7df428380b667e21217224a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *Käyttäjän kehotteista ei löytynyt yhtään tapausta, jossa hän olisi eksplisiittisesti pyytänyt tekoälyä tekemään lopullisen subjektiivisen valinnan tai päätöksen hänen puolestaan. Käyttäjä ohjaa sisällön tuottamista ja muotoilua, mutta ei delegoi päätöksentekoa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Käyttäjä delegoi tekoälylle subjektiivisen harkinnan siitä, mikä on 'järkevää' sisällyttää raporttiin, mikä on lopullinen subjektiivinen valinta käyttäjän puolesta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_a946688e5f5549e8ac30584d1a02ad26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *Sääntö edellyttää, että faktapohjaisessa raportoinnissa ei ole yhtään ensimmäisen persoonan ilmaisua. Tekstin viimeisessä kappaleessa käytetään sanaa "Yrityksemme", joka sisältää ensimmäisen persoonan omistusliitteen "-mme". Koska ensimmäisen persoonan ilmaisujen määrä ei ole nolla, säännön ehto ei täyty.*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Säännön ehto täyttyy. Tekstistä löytyi faktapohjaista raportointia sisältävä kappale, jossa ensimmäisen persoonan merkkien määrä on nolla.*

---

### Atom-ID: `tda_cb7637a8eae04303ae9a3e8085b075b4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *Ehto täyttyi, koska dokumentista löytyi faktaväite, joka esitetään ilman eksplisiittisiä absoluuttisia ilmauksia (kuten 'aina' tai 'ainoastaan') samassa lauseessa.*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *Ehto ei täyty. Teksti esittää faktaväittämiä, mutta ne ovat luonteeltaan absoluuttisia. Esimerkiksi väite "Supermegatrendeistä" esitetään tosiasiana ilman mitään varaumia tai pehmentäviä ilmauksia, jotka osoittaisivat sen olevan tulkinta.*

---

### Atom-ID: `tda_52ffb15768ba4a62ac3a8be5824a8aa6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *The text does not define any specific, measurable boundary conditions that would falsify its claims regarding the megatrends or supermegatrends. The claims are presented as descriptive of current and future states requiring adaptation.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *CONDITION MET. The text defines conditions for successful responses to megatrends but does not define specific measurable conditions that would falsify the underlying claims about the megatrends themselves.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_45885ef98e7d481084b4378d5b3f2f3f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *AI:n vastauksesta ei löytynyt vetoamisia auktoriteettiin, jotka eivät olisi perustuneet spesifisiin lähdetietoihin tai todennettavissa oleviin sääntöihin. Kaikki väitteet on ankkuroitu Sitran raportteihin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *AI vetoaa toistuvasti 'Sitran näkemykseen' ja 'Sitran megatrendiraportteihin' perustellessaan väitteitään. Vaikka nämä ovat spesifisiä lähteitä, säännön anti-pattern tulkitsee spesifiseen lähteeseen vetoamisen auktoriteettiin vetoamiseksi tässä kontekstissa. CONDITION NOT MET.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_dff85ed8a43a4ca99c34873b2fe44d89` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *Lauseessa esitetään väite ('Talouden perusta rakoilee'), sitä tukeva data ('Luonnon kantokyky murenee') ja tarkka mekanismi ('syntyy siitä, että', 'mikä ajaa suoraan siihen, että'), joka yhdistää nämä kaksi. Kaikki kolme komponenttia ovat selkeästi läsnä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *Tekstissä on esitetty väitteitä ja niitä tukevia tietoja sekä perustason syy-seuraussuhteita. Kuitenkaan ei ole määritelty tarkkaa mekanismia, joka selittäisi, miten data johtaa väitteeseen empiirisesti ja yksityiskohtaisesti. Esimerkiksi 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' kuvaa yhteyden, mutta ei sen tarkkaa toimintamekanismia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c17684acfcbe4a918e5ae0705b452b06` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *The user does not provide commands focused solely on tone or style while ignoring substantive factual gaps. The request to tailor the report for a 'kaupallisen liiketoiminnan johtoryhmälle' also includes a substantive request for 'kaupallisia vaikutuksia', indicating a focus on content as well as presentation.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Käyttäjä keskittyy tekoälyn vastauksen sävyyn ja tyyliin, pyytämällä sitä kirjoittamaan raportin 'kaupallisen liiketoiminnan johtoryhmälle' ja sisällyttämään siihen 'kaupallisia vaikutuksia'. Tämä on performatiivisuuteen keskittyvä komento, joka ohjaa esitystapaa tietylle yleisölle. CONDITION MET.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5257ba1edae34afe8b837c8c238cf743` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *Teksti erottaa monimutkaisen ongelman (supermegatrendien vaikutukset) vähintään kolmeen erilliseen, testattavaan osakomponenttiin ('Ekologinen Resilienssikriisi', 'Geoteknologinen Valtaistelu', 'Epävarmuuden Sosiaalinen Polarisointi').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *Teksti jakaa monimutkaisen ongelman (supermegatrendit) selkeästi kolmeen erilliseen osakomponenttiin, ja tämä jaottelu on merkitty eksplisiittisesti, mikä osoittaa rakenteellisen jaottelun läsnäolon.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_69cc84e0b0c44996a8a95e09b356c692` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [FALSE]:**
  > *No abrupt transition markers were found. The text consistently provides explicit causal mechanisms when connecting different facts or phenomena, thus avoiding abrupt transitions without explanation. CONDITION MET.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [TRUE]:**
  > *The text connects extreme weather and resource scarcity to rising raw material prices and supply chain disruptions. While a causal relationship is evident, the precise explanatory mechanism for this connection is not detailed within the quoted string, making it an abrupt transition.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_680dc2c703b3425fa0b0d943dbd5af16` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *Käyttäjän ohje 'koosta näistä vastauksista 1 sivun raportti' sisältää sekä rakenteellisen suunnitelman ('raportti') että rajoitesanaston ('1 sivun') samassa lauseessa, mikä täyttää säännön ehdot.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *No structural blueprint for the AI's output was found within the `Reflection_Text` that also contained constraint vocabulary in the same paragraph. The structure described pertains to the reflection document itself, not the generated content.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_3a65513aa717469a8d2c3b821a69c4ab` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_08d87e767b8a4cd1b004870ee2b26939) - [TRUE]:**
  > *Käyttäjä hylkää tekoälyn päättelyn ja lisää oman loogisen korjauksensa ilmaisulla 'ei siis toivetila', ohjaten tekoälyä pois toiveajattelusta.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_46cac8b9002144e8bcea0f7ac9f3baff) - [FALSE]:**
  > *Käyttäjä ei hylkää tekoälyn päättelyä ja esitä omaa, parempaa loogista tai empiiristä korjausta.  [5. VALIDATION DECISION: FAIL]*

---

