# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ympäristö ja Konteksti (Execution State)
- **Git / Epic -tila:** Branch: night-shift-2026-06-05-1458 | Commit: e16e3bc9 - feat: implement LLMTaskExecutor with self-healing, fail-fast validation, and supporting orchestration hooks. (Fri Jun 12 21:36:02 2026 +0300)
- **Kriittiset järjestelmäarvot (Enums):**
  - **EvaluationRunCount**: ENSEMBLE = 3, STANDARD = 1
  - **VerificationResult**: VERIFIED = RESULT_VERIFIED, DEBUNKED = RESULT_DEBUNKED
  - **SystemConcurrency**:
    - MAX_CONCURRENT_WORKFLOWS = 10
    - MAX_CONCURRENT_LLM_STEPS = 2
    - LLM_MAX_RETRIES = 2
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
    - PACING_DELAY_VERTEX_SECONDS = 12
    - PACING_DELAY_OPENAI_SECONDS = 0
    - PACING_DELAY_MOCK_SECONDS = 0
    - REDIS_CONNECTION_TIMEOUT_SECONDS = 10
- **Vertailtavat ajot (R1, R2...):**
  - **R1:** `exe_90b176274d4e456bae89d3f503f19658`
  - **R2:** `exe_accb763bf6024c94bb5cb3135bb87536`
- **Aktiiviset Säännöt ja Asetukset (Frozen Context):**
  - **Vastuullisuus (Turvallisuus- ja Etiikkasuodatin)** (`blk_80732a33fe1947ee`) - [R1: 0P/15F] [R2: 1P/14F]
  - **Oman tiedon rajat (Episteeminen Nöyryys)** (`blk_22e3598e06414409`) - [R1: 7P/8F] [R2: 7P/8F]
  - **Harkintakyky (Kahnemanin Kaksoisprosessiteoria)** (`blk_109dab5b6b3f403a`) - [R1: 7P/2F] [R2: 7P/2F]
  - **Päättelyn rehellisyys (Kausaalinen ja Abduktiivinen Integriteetti)** (`blk_c3bc5f3eb8e74110`) - [R1: 6P/9F] [R2: 8P/6F]
  - **Väitteiden perustelu (Toulminin Argumentaatiomalli)** (`blk_440a5fef9331451b`) - [R1: 9P/6F] [R2: 5P/10F]
  - **Itsensä haastaminen (Falsifioinnin Auditointi)** (`blk_b476f89fb732448c`) - [R1: 0P/15F] [R2: 1P/14F]
  - **Syy-seuraussuhteet (Kausaalisuuden Analyysi)** (`blk_c5804a9143c34cb1`) - [R1: 5P/10F] [R2: 7P/8F]
  - **Ohjeiden noudattaminen (Arkistointistandardien Auditointi)** (`blk_fb15f8dcf23f4865`) - [R1: 0P/15F] [R2: 2P/12F]
  - **Avoimuus (Selitettävyys ja Läpinäkyvyys)** (`blk_f6e286f050c94d60`) - [R1: 7P/8F] [R2: 5P/10F]
  - **Luovuus ja syvyys (Bloomin Taksonomia)** (`blk_f921c7c0989b47e8`) - [R1: 8P/10F] [R2: 11P/7F]
  - **Prosessiomistajuus (Ylituomari)** (`blk_ff72c2d79edb4ebf`) - [R1: 5P/9F] [R2: 6P/9F]
  - **Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)** (`blk_53f32679aa514fcb`) - [R1: 3P/12F] [R2: 4P/11F]
  - **Luottamusarvio (XAI-Raportoija)** (`blk_6b8c766185294f7e`) - [R1: 2P/7F] [R2: 1P/8F]

## Ajojen Lähdetiedostot ja Syötteet
- **Run 1:** `exe_90b176274d4e456bae89d3f503f19658` (Lähde: [data/files/executions/exe_90b176274d4e456bae89d3f503f19658\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_90b176274d4e456bae89d3f503f19658/execution_trace.json))
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_90b176274d4e456bae89d3f503f19658/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_90b176274d4e456bae89d3f503f19658/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_90b176274d4e456bae89d3f503f19658/inputs/input_reflection_text.md)
- **Run 2:** `exe_accb763bf6024c94bb5cb3135bb87536` (Lähde: [data/files/executions/exe_accb763bf6024c94bb5cb3135bb87536\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_accb763bf6024c94bb5cb3135bb87536/execution_trace.json))
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_accb763bf6024c94bb5cb3135bb87536/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_accb763bf6024c94bb5cb3135bb87536/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_accb763bf6024c94bb5cb3135bb87536/inputs/input_reflection_text.md)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 183
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 81.42 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.5853
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.5858
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1858
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 34 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 2 / 34
- **PASSED -> FAILED:** 14
- **FAILED -> PASSED:** 20
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_5257ba1edae34afe8b837c8c238cf743` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE] **[CONTEXTUAL OVERRIDE]**:**
  > *Teksti esittelee kolme supermegatrendiä, jotka vaikuttavat talousjärjestelmän vakauteen, mutta nämä kolme komponenttia eivät esiinny fyysisesti yhtenäisenä, peräkkäisenä lainauksena lähdetekstissä. Konsepti on läsnä, mutta ei yhtenäisenä lainauksena.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_01edff70b75047ec9f6df0c49745f46e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Sääntö etsii kausaaliväitettä, joka on johdettu rajallisesta kontekstista ja jota sovelletaan universaalisti ilman rajojen tunnustamista. Tekstissä esiintyvät väitteet, kuten 'menestyäkseen yritysten on panostettava tulevaisuusresilienssiin', on rajattu 'yritysten' ja 'Kaupallinen Johtoryhmä' -kontekstiin, mikä estää absoluuttisen yleistyksen. Siksi ehto ei täyty, ja palautetaan null.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Lause 'ainoa tapa' esittää universaalin kausaalisen väitteen 'pitkän aikavälin vakaudesta' ilman, että lauseessa tai välittömässä kontekstissa mainitaan eksplisiittisiä rajauksia tai rajoituksia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_71e60846894545b2bc43a3361b7a5a9c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Käyttäjän kehotteista ei löytynyt sokraattisia käsitteellisiä kysymyksiä, jotka aktiivisesti tutkisivat perustavanlaatuista päättelyä tai pakottaisivat tekoälyn puolustamaan logiikkaansa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjä esittää käsitteellisen kysymyksen, joka pakottaa tekoälyn tarkentamaan vastaustaan ja erottamaan faktuaalisen näkemyksen toiveajattelusta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_bd90e5a66c5d433a9ed650f295132625` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lainauksessa 'kriisit ja Talouden perustan rakoilu ruokkivat Hyvinvoinnin haasteita ja sosiaalista polarisaatiota' 'ruokkivat' on kausaalinen sana. Väite perustuu tilastolliseen korrelaatioon tai samanaikaiseen esiintymiseen ilman eksplisiittistä fyysistä mekanismia, joka selittäisi, miten talouden rakoilu fyysisesti 'ruokkii' hyvinvoinnin haasteita tai sosiaalista polarisaatiota. Tämä sopii sään ehtoon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Tekstissä ei ole kausaalisia väitteitä, jotka perustuisivat *ainoastaan* tilastolliseen korrelaatioon tai samanaikaiseen esiintymiseen ilman minkäänlaista fyysistä mekanismia. Kausaaliset väitteet sisältävät implisiittisiä mekanismeja (esim. 'aja suoraan siihen, että', 'ruokkivat').  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_dff85ed8a43a4ca99c34873b2fe44d89` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lauseessa 'Luonnon kantokyky murenee' on empiirinen data, 'Talouden perusta rakoilee' on väite, ja 'mikä ajaa suoraan siihen, että' on tarkka kausaalinen mekanismi, joka yhdistää nämä kaksi. Kaikki kolme komponenttia ovat läsnä ja eksplisiittisiä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_86ccd40936bb4dfc9a6d1f532568c05c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Tekstistä ei löytynyt eksplisiittistä monivaiheista kausaalista ketjua, jossa olisi vähintään kolme erillistä peräkkäistä toimintoa, joista jokainen riippuu täysin edellisestä. Esimerkiksi 'Ekologinen Resilienssikriisi: Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' on vain kaksivaiheinen ketju.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjän kehotteet muodostavat kolmen peräkkäisen ja toisistaan riippuvaisen toiminnon ketjun: 1) 'koosta näistä vastauksista 1 sivun raportti', 2) 'näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan', 3) 'poista taulukot ja kerro ne tekstinä'. Jokainen toiminto riippuu edellisestä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b7e1fb5427384bb6866e224a0013ed2d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Tekstissä ei ole proseduraalisia sääntöjä, joita perusteltaisiin yksinomaan sisäisellä perinteellä ilman ulkoista todennettavissa olevaa standardia.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjän perustelu sisällön muuttamiselle ('koska näin alkupeäisen tarpeettomana') on puhtaasti sisäinen, subjektiivinen arvio, eikä se viittaa mihinkään ulkoiseen, todennettavissa olevaan standardiin tai ohjeeseen. Tämä on selkeä esimerkki sisäiseen auktoriteettiin perustuvasta perustelusta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_eec00de564394e9dbcc5744ca77f8e60` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Lause 'Vain<br>kestävät liiketoimintamallit saavat<br>tulevaisuudessa pääomaa.' sisältää poissulkevan sanan 'Vain' (only), joka esittää yhden menetelmän (kestävät liiketoimintamallit) ainoana tapana saada pääomaa, mainitsematta tai kumoamatta muita vaihtoehtoja. Tämä täyttää poissulkevan ratkaisumerkin ehdot.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d262dd4421bd4af68191eb1f4d0faf26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Käyttäjä kysyi 'Miten sitra tämän näkee raporttien perusteella'. AI esitteli vastauksessaan käsitteen 'postnormaalina aikana', jota käyttäjä ei ollut eksplisiittisesti pyytänyt. Tämä on AI:n esittelemä uusi käsite.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_7d0ef5f0be004974801b53d2af317bbe` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Lähdetekstissä ei ole eksplisiittisiä hylkäämismarkkereita, joissa kirjoittaja ilmoittaisi luovansa uuden säännön, joka on ristiriidassa annettujen ohjeiden kanssa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjä ilmoittaa nimenomaisesti muuttaneensa ja poistaneensa sisältöä ('Korjasin taulukosta Eurooppaan liittyvän asian, koska näin alkupeäisen tarpeettomana') oman harkintansa perusteella, mikä on ristiriidassa pyydettyjen ohjeiden kanssa, jotka edellyttävät AI:n tuottaman sisällön käyttöä tai tiettyä rakennetta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_47bade191cf346ec818757f081f6aef3` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lauseessa käytetään kontrastimerkitsijöitä ('eivät ole vain... vaan') ja vastaväite ('rajoite') käsitellään retorisesti uudelleenkehystämällä se 'uuden taloudellisen kasvun perustaksi' ilman empiiristä vastadataa. Tämä täyttää ehdon, jossa vastaväite ohitetaan retorisesti ilman dataa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Tekstissä ei esitetä spesifisiä vasta-argumentteja, joita käsiteltäisiin empiirisellä vastadatalla. Raportti keskittyy Sitran näkemyksen esittämiseen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_65c125a7c28b4f8e9c33c8987ff52931` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Tekstistä ei löytynyt absoluuttisia kvantifioijia tai varmuuden ilmauksia, jotka eivät sisältäisi empiirisiä mittaustermejä. Käyttäjän lausunnot ovat prosessikuvauksia tai subjektiivisia arvioita.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Lause sisältää absoluuttisen kvantifioijan 'peruuttamaton', eikä siinä ole empiirisiä mittaustokeneita, jotka voisivat kumota tai tarkentaa tätä absoluuttista väitettä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_ca74247488fe49d49c70e96cf74a31a7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Säännön 'EXTRACTION CONDITION: terms like, or are completely missing' määritelmä on puutteellinen, koska se ei määrittele, mitä termejä tulisi etsiä puuttuvina. 'ANTI-SEMANTIC-STRETCHING' -säännön mukaisesti en voi päätellä puuttuvia termejä, joten ehtoa ei voida täyttää.*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Otsikkokappale sisältää viittauksen 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023'. Tässä kappaleessa puuttuvat kokonaan termit kuten 'tutkimus', 'analyysi', 'data' tai 'tilasto'.*

---

### Atom-ID: `tda_1473cecaeb4c495c9bd0d28710e602b4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Käyttäjä antoi ohjeen 'koosta näistä vastauksista 1 sivun raportti', jossa on kaksi rajoitetta ('1 sivun', 'raportti'). Seuraava käyttäjän vastaus ('näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan') ei kuitenkaan sisällä eksplisiittistä vahvistusta näiden kahden rajoitteen täyttymisestä. Se on uusi ohje, ei vahvistus.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjä antoi ohjeen, jossa oli kaksi spesifistä rajoitetta ('näytä raportti uudestaan' ja 'varmista, että taulukot ovat kohdallaan'), mutta seuraava käyttäjän vastaus ('poista taulukot ja kerro ne tekstinä') ei sisältänyt eksplisiittistä vahvistusta näiden rajoitteiden täyttymisestä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_eb266643b83b48bbab94a041b6d12f6d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Tämän atom-ID:n kysymys oli tyhjä, joten palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjä antaa laajan yhteenvetokäskyn ('koosta... raportti'), joka antaa tekoälylle vapauden päättää, mitä sisällyttää, lukuun ottamatta sivumäärärajoitetta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_7e0d493a62234375b180d942cb6e0bcd` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Lause 'menestyäkseen' (saavuttaakseen menestyksen) on odotettu lopputulos, ja 'panostettava tulevaisuusresilienssiin' (on panostettava tulevaisuusresilienssiin) on toimintaan suuntautuva interventio, joka johtaa tähän lopputulokseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_5198e13cde3447fe9d0737a80abe458c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Lainaus linkittää arvion ('tekevät kestävyydestä pakollista') eksplisiittisesti mainittuihin kriteereihin ('CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset'), mikä täyttää kriteerien ankkuroinnin ehdot.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fda64d221181411fa70843a88689b27b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Tekstistä ei löytynyt sanoja, jotka viittaisivat vaihtoehtoihin, eikä se nimeä eksplisiittisesti potentiaalista kolmatta muuttujaa, joka voisi selittää lopputuloksen. Siksi ehto ei täyty, ja palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Lause esittää 'reilun digimaailman luomisen' vaihtoehtoisena tarkoituksena teknologiselle murrokselle, vastakohtana 'vain kustannussäästönä', mikä nimeää potentiaalisen kolmannen muuttujan tai vaihtoehtoisen selityksen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6e3e3aa6b9134a01838c3b70a35b4f32` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lauseessa käytetään heikkoa assosiatiivista kieltä ('kietoutuvat toisiinsa', 'sanelevat'), joka yhdistää datan (megatrendit) väitteeseen (sanelevat markkinaolosuhteet) määrittelemättä tarkkaa kausaalista mekanismia, miten tämä tapahtuu.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Tekstissä käytetään johdonmukaisesti tarkkaa kausaalista kieltä (esim. "syntyy siitä, että", "aja suoraan siihen, että", "ruokkivat", "vaikuttaa suoraan"), eikä heikkoa assosiatiivista kieltä ilman tarkkaa kausaalimekanismia. Siksi ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_a946688e5f5549e8ac30584d1a02ad26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Johtopäätös-kappaleessa on ensimmäisen persoonan monikon possessiivimuoto 'Yrityksemme'. Koska ensimmäisen persoonan merkintöjen määrä ei ole tasan nolla, ehto ei täyty.*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Otsikkokappale sisältää tilastollista/faktuaalista raportointia (kohderyhmä, päivämäärä, viite) ja siinä on tasan nolla ensimmäisen persoonan merkkiä (esim. 'minä', 'me', '-mme', '-ni').*

---

### Atom-ID: `tda_b899e72085ea4d488a6e6c22a34e2d75` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Tekstissä ei kuvata minkäänlaisia varmistusprosesseja, olivatpa ne manuaalisia tai systeemisiä. Siksi ehto ei täyty.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjän reflektiotekstissä mainitaan 'mielestäni' ja 'koska näin alkupeäisen tarpeettomana', mikä osoittaa, että varmistus ja päätöksenteko perustuivat käyttäjän omaan intuitioon ja subjektiiviseen arvioon, ei systeemiseen protokollaan. Tämä täyttää ehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_45885ef98e7d481084b4378d5b3f2f3f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lainaus on heuristinen tai ohittava ilmaus, jota käytetään päätöksen perustelemiseen ilman spesifistä dataa, numeerista painoarvoa tai todennettavissa olevaa sääntöä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Teksti viittaa 'Sitran Megatrendiraportteihin' ja 'Sitran näkemykseen', jotka ovat spesifisiä lähteitä ja attribuutioita, eivätkä yleisiä heuristisia tai vähätteleviä fraaseja ilman viittausta dataan tai sääntöön.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_e407bc0297324a5da95c9091d08b88bc` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Käyttäjä asetti mitattavissa olevan tavoitteen ('1 sivun raportti'). Vaikka AI tuotti raportin, se ei vahvistanut tätä tavoitetta fyysisellä mittauksella tai laskennalla (esim. 'Raportti on tasan 1 sivu pitkä'). Vahvistus oli implisiittinen, ei eksplisiittinen ja mitattavissa oleva.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjä asetti mitattavissa olevan tavoitteen ('1 sivun raportti'), mutta myöhemmässä vuorovaikutuksessa ei ole fyysistä mittausta tai laskentaa, joka vahvistaisi tämän tavoitteen täyttymisen. Vahvistus on puhtaasti kvalitatiivinen tai puuttuu kokonaan.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_1361cf5ec5b5420c905cd2a1f80893a7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Vaikka `reflection_text`-osiossa on retrospektiivisiä väitteitä aikomuksesta (esim. 'Annoin rajoituksia sekä roolin liiketoiminnalle'), `ANTI_PATTERNS`-sääntö edellyttää, että edeltävä teksti (`chat_log`) EI SAA sisältää väitettyjä parametreja. Tässä tapauksessa käyttäjä pyysi myöhemmin 'kaupallisen liiketoiminnan johtoryhmälle' ja 'kaupallisia vaikutuksia', mikä tarkoittaa, että parametrit olivat läsnä ennen lopullista tuotosta. Siksi retrospektiivinen väite ei täytä ehtoa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjän reflektiossa on eksplisiittinen retrospektiivinen väite aikomuksesta ('Annoin rajoituksia sekä roolin liiketoiminnalle'), jonka parametreja ei fyysisesti esiintynyt käyttäjän aiemmissa kehotteissa chat-lokissa ennen AI:n vastausta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_45b5e5067e2743dbbc275ac472e4cc06` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Tekstistä ei löytynyt käyttäjän esittämää falsifikaatiomarkkeria tai aktiivista stressitestiä, jossa käyttäjä olisi tarkoituksellisesti luonut skenaarion oman hypoteesinsa epäonnistumiseksi. `reflection_text`-osiossa mainittu 'Ennakoin, että alkuun en saa hyvää tulosta' on yleinen odotus, ei aktiivinen stressitesti.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Käyttäjän kehotteissa ei ole fyysisesti läsnä mitään falsifiointimerkkiä tai aktiivista stressitestiä, jossa käyttäjä yrittäisi kumota omaa hypoteesiaan. Tämä täyttää ehdon 'If no active stress-test is present'.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_25f0540101174b66a09fe7770a28d110` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lauseessa mainitaan vastaväite ('rajoite'), mutta se ohitetaan retorisesti uudelleenkehystämällä ('uuden taloudellisen kasvun perusta') esittämättä empiiristä vastadataa. Tämä täyttää ehdon, jossa vastaväite ohitetaan ilman vastadataa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Tekstissä ei mainita vasta-argumentteja, joita sitten sivuutettaisiin esittämättä vastadataa. Raportti esittää Sitran analyysin ilman tällaista retorista ohitusta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_41c6b31cee074d05b3024bb3437bedc1` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lainaus on perustelu, joka ei sisällä spesifisiä toimialamuuttujia, numeroita tai tarkkoja lainauksia syötteestä, vaan luottaa yleiseen malliin.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Justifikaatio sisältää spesifisiä toimialamuuttujia, kuten 'Korjaavaan ja uusintavaan talouteen siirtyminen' ja 'pitkän aikavälin vakaus'. Siksi ehdon (justifikaatio EI sisällä spesifisiä muuttujia) ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_569a2c551bae4301b1217c8a7107cc2c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lainaus sisältää eksplisiittisen kausaalisen väitteen ('osoittaa fundamentaalisen siirtymän'). Kappale ei sisällä empiiristä datasanastoa (esim. tilastollisia mittauksia tai data-analyysiä), vaan kuvaa kehitystä ja siirtymää vuosien välillä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Käyttäjän kehotteissa ei ole yhtään eksplisiittistä kausaalista väitettä, joka ei sisältäisi empiiristä datasanastoa. Käyttäjä esittää kysymyksiä ja ohjeita, ei kausaalisia väitteitä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_5f0355b329a24860b62b2118e24aab69` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *Kysymys oli tyhjä, joten vastausta ei voitu muodostaa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE] **[CONTEXTUAL OVERRIDE]**:**
  > *Kysymys on tyhjä, joten fyysistä merkkiä ei voida etsiä tai löytää. Palautetaan null.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_84b7784951c84e948c131c189261f564` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lauseessa 'rajoite' on rajoitusmerkintä, jota seuraa välittömästi 'vaan' (mutta/sen sijaan), joka toimii vähättelevänä siirtymäsanana ja rationalisoi rajoituksen pois esittämällä sen kasvun perustana.*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Tekstistä ei löytynyt rajoitusmerkkiä, jota olisi seurannut vähättelevä siirtymäsana, joka rationalisoisi rajoituksen pois. Rajoituksia seurasi yleensä strateginen vastaus tai selitys, ei vähättely.*

---

### Atom-ID: `tda_00245380f839424abfe3d923c1ae322f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lauseessa 'Sitran näkemys on, että' toimii performatiivisena varauksena (hedging marker), jota seuraa välittömästi absoluuttiset varmuusmerkinnät 'ei ole' ja 'on panostettava', jotka palauttavat väitteen absoluuttiseen varmuuteen.*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Tekstistä ei löytynyt performatiivista suojausmerkkiä, jota olisi välittömästi seurannut absoluuttisen varmuuden merkki seuraavassa lauseessa. Esimerkiksi 'voi olla' -tyyppisiä ilmaisuja ei seurannut 'on aina' -tyyppinen ilmaisu.*

---

### Atom-ID: `tda_4ba32055738247d28e00a597f505ce9e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [TRUE]:**
  > *Lause käyttää binääristä reduktiomerkkiä 'ainoa tapa' ('the only way'), joka pakottaa monimutkaisen tilanteen yhteen absoluuttiseen vaihtoehtoon. Tämä on rikkomus säännön mukaan, joten lainaus poimitaan.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d467244b1f5f412f92d3200691028bc0` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lainaus sisältää absoluuttisen johtopäätöksen ('paluuta vanhaan normaaliin ei ole'). Kappale ei sisällä kontrafaktuaalisia markkereita (esim. 'jos', 'ellei').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Käyttäjän kehotteissa ei ole yhtään absoluuttista johtopäätöstä tai päätöstä, jonka kappale ei sisältäisi kontrafaktuaalisen sanaston leksikaalisia merkkejä. Käyttäjä esittää kysymyksiä ja ohjeita.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_353aa6c896db47fb9d29b06a69bf77d4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_90b176274d4e456bae89d3f503f19658) - [TRUE]:**
  > *Lause esittää yhden toimintatavan 'ainoa tapa' -muodossa, mikä implisiittisesti hylkää kaikki muut vaihtoehtoiset tavat ilman eksplisiittistä empiiristä todistetta niiden tehottomuudesta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_accb763bf6024c94bb5cb3135bb87536) - [FALSE]:**
  > *Lähdetekstissä ei ole havaittavissa dismissiivisiä markkereita, jotka hylkäisivät vaihtoehtoisia hypoteeseja ilman empiiristä näyttöä. Siksi sääntö on tyydytetty (ei rikkomusta).  [5. VALIDATION DECISION: PASS]*

---

