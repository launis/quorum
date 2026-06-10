# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ajo-tiedot (Runs)
- **Run 1:** `exe_67ebf9ea0446459f93a7f35cad392404` (Lähde: [data\files\executions\exe_67ebf9ea0446459f93a7f35cad392404\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_67ebf9ea0446459f93a7f35cad392404/execution_trace.json))
- **Run 2:** `exe_1227ec0b70dc4763ac021da9f33f5f7d` (Lähde: [data\files\executions\exe_1227ec0b70dc4763ac021da9f33f5f7d\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_1227ec0b70dc4763ac021da9f33f5f7d/execution_trace.json))

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 185
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 77.84 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.5120
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.5133
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.2216
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 41 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 0 / 41
- **PASSED -> FAILED:** 16
- **FAILED -> PASSED:** 25
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_3a362e01de66444c813e5b79adec27bf` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'depth' subjectively. STEP 1 (Syntactic Anchor): Find absolute conclusion words (e.g., 'clearly', 'obviously', 'must be', 'selvästi'). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: the conclusion is presented without a multi-step logical deduction. <disambiguation>
  REFRAMING EXCLUSION: Rhetorical reframing patterns where a concept is 
  repositioned from negative to positive framing ('not just X, but Y') are 
  STYLISTIC DEVICES, not argumentative structures. Do NOT extract them as:
  - counter-arguments (they do not argue AGAINST anything)
  - dialectical syntheses (they do not reconcile two opposing theses)
  - alternative model dismantling (they do not present a separate model)
  - absolute conclusions (they are framing choices, not logical claims)
  If a reframing pattern is the ONLY candidate match, return JSON null.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstissä ei ole absoluuttisia johtopäätöksiä (esim. 'selvästi', 'täytyy olla'), jotka esitettäisiin ilman monivaiheista loogista päättelyä. Ehdotukset ja niiden perustelut ovat jäsenneltyjä ja sisältävät implisiittisen tai eksplisiittisen päättelyn.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Lause 'Tämä on varma tapa myrkyttää työilmapiiri' esittää absoluuttisen johtopäätöksen ('varma tapa') ilman monivaiheista loogista päättelyä tai perusteluja välittömässä yhteydessä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_69cc84e0b0c44996a8a95e09b356c692` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find abrupt transition markers ('therefore', 'thus', 'so'). STEP 2 (Bounding Box): Scan the sentence containing the transition. EXTRACTION CONDITION: it connects two facts but lacks any explanatory mechanism ('because mechanism X'). NEGATIVE CONDITION (RETURN NULL IF MET): a mechanism is described. Do not accept explicit causal mechanisms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstistä ei löytynyt äkillisiä siirtymämerkkejä ('siksi', 'näin ollen', 'joten'), jotka yhdistäisivät kaksi tosiasiaa ilman selittävää mekanismia. Kaikki löydetyt siirtymät sisälsivät selittävän mekanismin tai olivat johtopäätöksiä, eivätkä täyttäneet negatiivista ehtoa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin äkillisiä siirtymämerkkejä ('siksi', 'näin ollen', 'siispä'), jotka yhdistävät kaksi faktaa ilman selittävää mekanismia. Lause 'Ratkaisu ei siis ole paluu vanhaan, muttei myöskään sataprosenttinen etätyö. Voittajayritykset luovat toimivan hybridimallin.' sisältää siirtymämerkin 'siis'. Se yhdistää kaksi faktaa (ei vanhaan, ei täysin etänä; voittajayritykset luovat hybridimallin), mutta ei eksplisiittisesti kuvaa mekanismia, miksi voittajayritykset tekevät niin, vaan jättää sen implisiittiseksi. Negatiivinen ehto (mekanismi on kuvattu) ei täyty, koska mekanismia ei ole eksplisiittisesti kuvattu lauseen sisällä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2d12f15e1c2d4488b7c2ef32d0ccfa26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstissä ei ole absoluuttisen varmuuden markkereita (esim. 'täysin', '100%') ilman empiiristä dataa tai epistemologisia kvalifikaattoreita. Esitetyt väitteet ovat ehdotuksia, tavoitteita tai odotettuja seurauksia, eivät absoluuttisia totuuksia.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Lauseessa käytetään ilmaisua 'varma tapa', joka viittaa absoluuttiseen varmuuteen ilman empiiristä dataa tai episteemisiä tarkennuksia kyseisessä kontekstissa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bd90e5a66c5d433a9ed650f295132625` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'spurious'. STEP 1 (Syntactic Anchor): Find causal words (e.g. 'causes', 'because'). STEP 2 (Bounding Box): Scan the same sentence. EXTRACTION CONDITION: the causal claim is backed ONLY by a statistical correlation or simultaneous occurrence without any physical mechanism.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstistä ei löytynyt yhtään kausaalista väitettä, joka perustuisi pelkästään tilastolliseen korrelaatioon tai samanaikaiseen esiintymiseen ilman minkäänlaista fyysistä mekanismia. Kaikissa kausaalisissa väitteissä oli joko eksplisiittinen tai implisiittinen mekanismi kuvattuna.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Lauseessa esitetään kausaalinen väite ('Jos yhteisöllisyys katoaa, yrityskulttuuri kuolee'), jossa seuraus esitetään suorana ilman eksplisiittistä fyysistä mekanismia tai välivaiheita, mikä täyttää säännön ehdon korrelaatiosta ilman mekanismia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fda64d221181411fa70843a88689b27b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate completeness. STEP 1 (Syntactic Anchor): Find words indicating alternatives ('however', 'other factors', 'confounder'). STEP 2: EXTRACTION CONDITION: the text explicitly names a potential third variable that could also explain the outcome. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Teksti nimeää eksplisiittisesti 'pakotettu läsnäolo' (forced presence) potentiaaliseksi kolmanneksi muuttujaksi, joka selittää motivaation heikkenemisen, käyttäen ankkuria 'Toisaalta' (on the other hand).  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Tekstistä ei löytynyt kohtaa, jossa nimenomaisesti nimettäisiin potentiaalinen kolmas muuttuja, joka voisi selittää lopputuloksen. 'Kuitenkin' ja 'mutta' -sanat esittelivät vastaväitteitä tai haasteita, eivät vaihtoehtoisia selittäviä muuttujia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_db48d54b7f704f65a361a113611c3b53` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find breakdown condition markers (e.g., 'breaks down when', 'does not apply if', 'fails beyond', 'invalidated when'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the breakdown marker AND ALSO contains explicit numerical limits or physical threshold vocabulary (e.g., 'exceeds', '<', '>', 'limit of', 'threshold') -> ACCEPT. If it lacks explicit measurement limits -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'deep humility' or whether the claim is logically 'voided'. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Etsin 'ai:'-lohkoista hajoamisolosuhteiden merkkejä (esim. 'breaks down when', 'does not apply if') ja lisäksi eksplisiittisiä numeerisia rajoja tai fyysisiä kynnysarvoja. Lause 'Unohdetaan jäykkä 'klo 17 suljetaan laitteet' -sääntö, joka ei sovi iltaopetukseen.' sisältää 'joka ei sovi' (semanttisesti 'does not apply') ja 'klo 17' (numeerinen raja), mikä täyttää molemmat ehdot.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Etsin 'ai:'-lohkoista hajoamisen ehtoja kuvaavia merkitsijöitä (esim. 'breaks down when', 'does not apply if') ja tarkistin, sisältävätkö ne eksplisiittisiä numeerisia rajoja tai fyysisiä kynnysarvoja. Vaikka teksti sisältää kritiikkiä ja ennusteita ongelmista, se ei käytä täsmällisiä hajoamisen ehtoja kuvaavia merkitsijöitä yhdistettynä numeerisiin rajoihin tai kynnysarvoihin.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fcdde66df02c4edb9e090172c3e2b956` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not synthesize steps yourself. STEP 1 (Syntactic Anchor): Find sequential logic markers (e.g. 'First', 'Second', 'Finally', 'Step 1'). STEP 2 (Bounding Box): Scan the block. EXTRACTION CONDITION: a continuous, unbroken chain of at least three explicit logical steps is documented. NEGATIVE CONDITION (RETURN NULL IF MET): fewer than three steps. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin vähintään kolmen peräkkäisen, eksplisiittisen loogisen vaiheen ketjua, jotka on numeroitu. Ensimmäinen tällainen esiintymä löytyi toisesta 'ai:'-vastauksesta, jossa oli kolme numeroitua kohtaa sisältöineen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fba3218b2c5443d89ad105d945f71255` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Locate a risk assessment or 'pre-mortem' structure. STEP 2: Find explicit dismantling of a risk using a verifiable external citation or empirical data. EXTRACTION CONDITION: both the risk and the empirical counter-data are found.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Etsin riskinarviointia tai 'pre-mortem' -rakennetta, jossa riski puretaan eksplisiittisesti todennettavalla ulkoisella viittauksella tai empiirisellä tiedolla. Vaikka teksti mainitsee ongelmia ('siiloutumiseen, epävarmuuteen tavoitettavuudesta sekä kokemuksiin epäoikeudenmukaisuudesta') ja ehdottaa ratkaisuja, se ei sisällä nimenomaista rakennetta, jossa yksittäinen riski esitetään ja sitten puretaan välittömästi empiirisellä tiedolla tai ulkoisella viittauksella samassa kontekstissa. Ehdotuksen perustelu tutkimustietoon on yleinen, ei spesifien riskien purkamista.*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Johdanto-kappaleessa tunnistetaan riskit ('työyhteisön siiloutumiseen, epävarmuuteen tavoitettavuudesta sekä kokemuksiin epäoikeudenmukaisuudesta'). Välittömästi tämän jälkeen ehdotus esitetään perustuen 'Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon', mikä on ulkoinen, todennettavissa oleva empiirinen tieto, jolla riskejä pyritään purkamaan. Molemmat ehdot täyttyvät samassa kappaleessa.*

---

### Atom-ID: `tda_c607024dbf524f7a9d68af443901c40e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find an explicit causal claim (e.g., 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the causal claim AND ALSO contains intermediary sequential tokens (e.g., 'which in turn', 'leading to', 'via', 'through the process of', 'first... then') -> ACCEPT. If it lacks intermediary step tokens (meaning it only states A causes C directly) -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, logical 'robustness', or whether the mechanism is 'functional'. Evaluate only token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Löysin kausaalisen väitteen, joka sisälsi eksplisiittisiä välivaiheen sekvenssitokeneita ('Tämä luo riskin', 'mikä voi johtaa'), jotka yhdistävät syyn ja seurauksen useamman vaiheen kautta.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Tekstistä ei löytynyt eksplisiittisiä kausaaliväitteitä, jotka sisältäisivät välivaiheita kuvaavia sekventiaalitunnuksia (esim. 'which in turn', 'leading to', 'via', 'through the process of', 'first... then'). Kaikki kausaaliväitteet olivat suoria A -> C -tyyppisiä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_1336f92df9fd474cb4929d8796c86da7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find a final absolute verdict sentence (e.g., 'is a complete failure', 'is perfect', 'is completely useless'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the verdict. If the paragraph contains the verdict BUT does NOT contain comparative or weighing vocabulary (e.g., 'however', 'although', 'despite', 'on the other hand') -> ACCEPT. If it contains weighing vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'praise', or 'condemnation' subjectively. Do not evaluate if the verdict is balanced or not.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Etsin 'ai:'-lohkoista lopullisia, absoluuttisia tuomiosanoja (esim. 'on täydellinen epäonnistuminen', 'on täydellinen', 'on täysin hyödytön'). 'Paholaisen asianajaja' -osiossa lause 'Johtopäätös: Ehdotus on kaunis kompromissi, joka yrittää miellyttää kaikkia, mutta vaarantaa loppujen lopuksi sekä operatiivisen toiminnan, tilatehokkuuden että työrauhan.' sisältää absoluuttisen tuomion ('vaarantaa'), mutta myös vertailevaa tai punnitsevaa sanastoa ('mutta'), mikä hylkää sen säännön mukaisesti. Muita absoluuttisia tuomioita ilman punnitsevaa sanastoa ei löytynyt.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Sääntö edellyttää lopullisen absoluuttisen tuomion sisältävän lauseen löytämistä 'ai:'-lohkosta, kunhan kyseinen kappale ei sisällä vertailevaa tai punnitsevaa sanastoa (esim. 'kuitenkin', 'vaikka', 'huolimatta', 'toisaalta'). Lause 'Tämä on suorastaan loukkaavaa heitä kohtaan.' on selkeä absoluuttinen tuomio. Sen sisältävä kappale ei sisällä kiellettyä vertailevaa sanastoa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_9a08254fb47a46fdb8a78030ed68f853` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dialectical reasoning markers ('One might argue that X, but testing showed Y because'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the author explicitly attempts to falsify their own Claim with a test/data before accepting it. NEGATIVE CONDITION (RETURN NULL IF MET): it is just a pros/cons list. Simple pros/cons lists.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Etsin dialektisen päättelyn merkkejä, joissa kirjoittaja yrittää nimenomaisesti falsifioida omaa väitettään testin/datan avulla ennen sen hyväksymistä. AI:n vastaus käyttäjän 'paholaisen asianajajana' -pyyntöön sisältää juuri tämän. AI kritisoi omaa aiempaa ehdotustaan ja toteaa sen olleen 'teoreettisen kaunis, mutta käytännössä se olisi johtanut kaaokseen'. Tämä on selkeä yritys falsifioida aiempi väite kritiikin (testin/datan) perusteella, mikä johtaa uuteen, korjattuun ehdotukseen. Tämä ei ole pelkkä plussat/miinukset-lista, vaan aiemman väitteen aktiivista kumoamista.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Etsin dialektisen päättelyn merkkejä, joissa kirjoittaja yrittää nimenomaisesti falsifioida omaa väitettään testin/datan avulla ennen sen hyväksymistä. 'product_text' on muistio, joka esittää ehdotuksen ja sen perustelut, eikä se sisällä tällaista itse-falsifioinnin rakennetta. Vaikka 'chat_log' sisälsi 'paholaisen asianajaja' -osion, se oli kritiikkiä aiemmalle ehdotukselle, ei lopullisen 'product_text'-dokumentin sisäistä dialektista päättelyä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bd85f009b0fb4f7899b40ff0e763dee7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find tension markers between metrics and goals (such as equivalents of 'this metric is flawed because', 'the metric versus the actual goal' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the quote IF the user explicitly questions the reliability of a proxy metric in relation to the true qualitative goal.</step3_extraction_condition> <step4_fail_fast_protocol>If the text merely tracks a metric without questioning its validity, you MUST return JSON null.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Käyttäjä kyseenalaistaa opettajan 'tuloksen' mittaamisen etäpäivänä ja esittää esimerkin (kurssimateriaalin valmius), joka ei välttämättä korreloi todellisen työmäärän kanssa ('Siihen voi mennä kaksi tuntia tai kaksi päivää'). Tämä osoittaa jännitteen välitysmittarin ja todellisen laadullisen tavoitteen välillä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bfbe65b639b54106913902d5bd0ae6ab` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find revelation markers (e.g., 'underlying this', 'the root cause is', 'fundamentally'). STEP 2: EXTRACTION CONDITION: the text identifies a mechanism or assumption that is not immediately visible on the surface. Do not accept superficial observations of visible symptoms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Syntaktinen ankkuri 'Fakta taustalla' löytyi 'ai:'-lohkon sisältä. Lause identifioi mekanismin ('hallitsematon tai liiallinen etätyö ei vähennä vain yhteisöllisyyttä, vaan myös työntekijän tarvetta kuulua työyhteisöön. Tämä luo riskin "etätyöhön katoamisesta", mikä voi johtaa uupumukseen ja elämänhallinnan vaikeuksiin'), joka ei ole välittömästi näkyvä oire, vaan syvempi mekanismi.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Lähdetekstistä ei löytynyt fyysisiä paljastusmerkkejä (esim. 'tämän taustalla', 'perimmäinen syy on', 'pohjimmiltaan') tai niiden suomenkielisiä vastineita, jotka tunnistaisivat pinnan alla olevan mekanismin tai oletuksen. Teksti kuvaa oireita, tavoitteita tai sääntöjä, mutta ei paljasta piileviä syitä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_ce2566987e8f44819102d6eb1d28857d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not flag open-ended questions explicitly left for future research. STEP 1 (Syntactic Anchor): Find a question mark '?' used by the author to question their own premise. STEP 2 (Bounding Box): Scan the following 2 sentences. If the author answers their own question confirming the premise without citing new data. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Etsin 'ai:'-lohkoista kysymysmerkkiä '?', jota kirjoittaja käyttää kyseenalaistaakseen oman premissinsä, ja sen jälkeen kahta lausetta, joissa kirjoittaja vastaa kysymykseen vahvistaen premissin ilman uutta tietoa. Löysin kysymyksiä, joissa AI kyseenalaistaa aiemman ehdotuksensa (paholaisen asianajaja -roolissa) tai kysyy lähteistä, mutta näissä tapauksissa joko kyseenalaistus johti premissin muuttamiseen tai vastaus sisälsi uutta tietoa (lähteet). Sääntöä vastaavaa tapausta ei löytynyt.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin 'ai:'-lohkoista kysymysmerkkiä '?' ja tarkistin, vastaako kirjoittaja omaan kysymykseensä vahvistaen premissin ilman uutta dataa seuraavien kahden lauseen sisällä. Löysin kohdan, jossa kysymys esitetään ja siihen vastataan välittömästi vahvistaen kaaoksen premissin.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_216cc3fd45284deb8d51ea4cf2b2fd93` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find absolute words (e.g., 'always', 'never', 'everyone knows', 'fact'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the absolute claim is presented without any citations or stated limitations. Do not accept absolute statements that are mathematically proven or properly cited.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstistä ei löytynyt absoluuttisia väitteitä (esim. 'aina', 'ei koskaan', 'tosiasia'), joita ei olisi rajoitettu tai joihin ei olisi viitattu. Sääntö on inverse-sääntö, ja koska rikkomusta ei löytynyt, palautetaan tyhjä merkkijono.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin absoluuttisia sanoja (esim. 'aina', 'ei koskaan') 'ai:'-lohkoista ja 'product_text'-osiosta. Löysin 'aina'-sanan lauseesta, joka esittää säännön ilman viittausta tai rajoitusta, mikä täyttää ehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_10dd47750c9244139c394ca875f160e6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. Do not evaluate the quality of the bridging rule.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Etsin lauseita, jotka sisältävät eksplisiittisen sillan datan ja väitteen välillä, kuten 'periaatteen mukaan' tai 'tämä osoittaa mekanismin'. Tekstissä esiintyy 'koska' ja 'kun' -rakenteita, jotka ilmaisevat suoria kausaalisuhteita, mutta ei yleistä, eksplisiittisesti muotoiltua periaatetta tai mekanismia, joka toimisi Toulminin mallin mukaisena warranttina.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Lauseessa 'sillä ne toimivat huonosti videolla' esitetään eksplisiittinen mekanismi (bridging rule) sille, miksi toimistopäivien tulee olla tarkoituksellisia tiettyjen toimintojen osalta. Tämä vastaa kriteeriä, jossa Data ja Claim yhdistetään eksplisiittisellä säännöllä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ac3b078498e048889ad3bc46b634c2ee` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find an academic citation, mathematical theorem, or academic framework. If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the sentence IF AND ONLY IF the logic is explicitly tethered to this source (e.g., actively applying a rule from the source).</step3_extraction_condition> <step4_fail_fast_protocol>If the source is just named or referenced passively without actively applying its logic, you MUST return JSON null.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin lauseita, joissa logiikka tai suositus sidottiin nimenomaisesti akateemiseen lähteeseen. Ensimmäinen tällainen esiintymä löytyi 'ai:'-vastauksesta, jossa suositus perustuu suoraan Stanfordin yliopiston dataan.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c2968c987f1a4ac5824f15653df3dc8f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Tekstissä hylätään 'ankkuripäivä'-konsepti ('Koko oppilaitoksen yhteisestä 'ankkuripäivästä' luovutaan') ilman, että samassa kappaleessa esitetään ulkoista todennettavissa olevaa lähdettä tai empiiristä dataa tämän hylkäämisen tueksi. Perustelu on sisäinen looginen argumentti ('jotta kampus ei ruuhkautuisi yhtenä päivänä ja autioituisi muina'), ei ulkoinen lähde.*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Tekstissä ei ole vähätteleviä ilmaisuja vaihtoehtoja kohtaan ilman, että niille esitetään perusteluja tai viitataan käytännön syihin. Esimerkiksi 'ankkuripäivästä luopuminen' perustellaan kampuksen ruuhkautumisen estämisellä.*

---

### Atom-ID: `tda_6ecd649b48c24e68824e27e30ed8a63e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. Do not accept generic requests ('analysoi hyvin'). STEP 1 (Syntactic Anchor): Find methodology anchors ('käytä menetelmää', 'mallin mukaisesti', 'viitekehys', 'SWOT', 'PESTEL', 'teoria', 'framework'). STEP 2: EXTRACTION CONDITION: the user explicitly names a method or analytical framework the AI MUST follow.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Käyttäjän kehotteista ei löytynyt yhtään syntaktista ankkuria, joka viittaisi metodologian tai analyyttisen viitekehyksen nimeämiseen, kuten 'käytä menetelmää' tai 'viitekehys'.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Käyttäjä pyytää tekoälyä toimimaan kolmesta eri näkökulmasta (talousasiantuntija, HR-johtaja, strategi), mikä on selkeä metodologinen kehys dialogin rakentamiselle.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0da1a4b2bca64e62ad3225857e780004` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'thoughtfulness'. STEP 1 (Syntactic Anchor): Find dialectical markers (e.g., 'While X is true, Y proves', 'Reconciling these', 'Toisaalta'). STEP 2: EXTRACTION CONDITION: the text explicitly introduces two opposing variables and generates a third, novel conclusion (synthesis) rather than just picking one. <disambiguation>
  REFRAMING EXCLUSION: Rhetorical reframing patterns where a concept is 
  repositioned from negative to positive framing ('not just X, but Y') are 
  STYLISTIC DEVICES, not argumentative structures. Do NOT extract them as:
  - counter-arguments (they do not argue AGAINST anything)
  - dialectical syntheses (they do not reconcile two opposing theses)
  - alternative model dismantling (they do not present a separate model)
  - absolute conclusions (they are framing choices, not logical claims)
  If a reframing pattern is the ONLY candidate match, return JSON null.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Teksti ei esitä kahta vastakkaista muuttujaa ja luo niistä kolmatta, uutta synteesiä. Se esittelee ongelmia ja ehdottaa ratkaisua, mutta ei käytä dialektisia markkereita synteesin luomiseen.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Teksti esittelee ensin etätyön myönteiset ja kielteiset vaikutukset (kaksi vastakkaista muuttujaa) ja luo sitten uuden johtopäätöksen (tasapaino ja pelisäännöt) synteesinä, mikä vastaa dialektisen synteesin määritelmää.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_09a80d0f657a4a449417bdbc82059578` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. Do not accept unbounded absolute rules. NEGATIVE BOUNDARY: General statements about megatrends, future directions, or abstract concepts DO NOT count as operational limits. This rule ONLY applies to strict operational/compliance boundaries.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Lause määrittää etätyöoikeuden operatiiviset rajat tehtävän vaatimusten perusteella, mikä vastaa rajauksen määrittelyn ankkuria.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Tekstistä ei löytynyt eksplisiittisiä rajausehtoja, jotka määrittelisivät vaatimustenmukaisuussäännön toiminnallisia rajoja käyttäen säännössä mainittuja syntaktisia ankkureita (esim. 'koskee vain', 'pois lukien'). Vaikka joitakin rajoituksia tai ehtoja mainittiin, ne eivät olleet muotoiltu säännön edellyttämällä tavalla compliance-säännön operatiivisena rajauksena.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d9cb646741ba4750ab561bf766c94f03` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 100% certainty markers ('guaranteed', 'undoubtedly', 'always'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the sentence makes a future prediction or subjective assessment using these markers. NEGATIVE CONDITION (RETURN NULL IF MET): it states a mathematical/historical fact. Mathematical facts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Etsin 100 % varmuutta ilmaisevia markkereita ('taattu', 'epäilemättä', 'aina') ja tarkistin, tekeekö lause tulevaisuuden ennusteen tai subjektiivisen arvion. Ensimmäinen tällainen osuma löytyi 'väistämättä'-sanasta, joka on vahva varmuusmarkkeri ja liittyy ennusteeseen siitä, miten työpäivä täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Tekstistä ei löytynyt yhtään 100 % varmuutta ilmaisevaa merkitsijää (kuten 'taattu', 'epäilemättä', 'aina'), jotka liittyisivät tulevaisuuden ennustukseen tai subjektiiviseen arvioon. Siksi negatiivinen ehto täyttyy ja palautetaan null.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_3eed2113bd9842f3b8fd050046505e4d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find causal claims relying on metaphysical or subjective vocabulary (e.g., 'universal energy', 'destiny', 'pure willpower', 'manifested', 'vibes'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the metaphysical anchor BUT does NOT contain empirical intermediary vocabulary (e.g., 'mechanism', 'measured', 'calculated', 'process', 'data') -> ACCEPT. If it contains mechanism vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'science', or subjective 'measurability'. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstistä ei löytynyt kausaaliväitteitä, jotka perustuisivat metafyysiseen tai subjektiiviseen sanastoon (esim. 'kohtalo', 'puhdas tahdonvoima') ilman empiiristä välitystä. Termejä kuten 'mututuntuma' käytettiin nimenomaan negatiivisessa mielessä, eli niitä ei käytetty kausaalisten väitteiden perustana.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Lause sisältää subjektiivisen termin 'tunnelma' ('aistitaan tunnelmaa'), eikä samassa lauseessa tai välittömässä kontekstissa ole empiiristä välittävää sanastoa (kuten 'mekanismi', 'mitattu', 'laskettu', 'prosessi', 'data'), joka selittäisi kausaalisen mekanismin empiirisesti.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_10f455c36f754d33a3a551e9e7b61da4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find structural breakdown verbs (e.g., 'consists of', 'divided into', 'components', 'elements'). STEP 2: EXTRACTION CONDITION: a single overarching concept is explicitly split into at least two named sub-components. Do not accept simple bullet-point lists of unrelated features.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Sääntö edellyttää rakenteellista jaotteluverbiä (esim. 'koostuu', 'jakautuu'), joka jakaa yläkäsitteen vähintään kahteen nimettyyn alakomponenttiin. Vaikka 'Ehdotus: Toimintalähtöinen hybridityömalli (2+3 -malli)' -otsikon alla on numeroitu lista alakomponenteista, tekstissä ei ole yhtään lausetta, joka sisältäisi eksplisiittistä jaotteluverbiä, joka yhdistäisi yläkäsitteen ja alakomponentit.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Sääntö edellyttää rakenteellisten jaottelua ilmaisevien verbien löytämistä, jotka jakavat yhden yläkäsitteen vähintään kahteen nimettyyn alakomponenttiin. Tekstissä 'Ehdotus: Toimintalähtöinen hybridityömalli (2+3 -malli)' on yläkäsite, joka jaetaan selkeästi neljään numeroituun alakomponenttiin ('1. Tehtäväkohtaiset linjaukset...', '2. Kulttuurin ja innovoinnin turvaaminen...', '3. Tavoitettavuus ja johtaminen...', '4. Talous ja tilatehokkuus'). Tämä täyttää ehdon, että yläkäsite on jaettu vähintään kahteen nimettyyn alakomponenttiin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_a9c96a0c55fe4ac884795440c722eb5d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find superficial correction commands by the user (e.g., 'fix the typo', 'make it shorter', 'bold the headers'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user ONLY requests formatting or minor lexical changes without challenging the logic. NEGATIVE CONDITION (RETURN NULL IF MET): logical changes are requested. Do not accept if the user challenges the underlying reasoning.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Käyttäjä pyysi useita kertoja muotoiluun ja tyyliin liittyviä muutoksia, kuten 'selvällä kielellä (ei jargonia)', 'yhden sivun yhteenveto' ja 'muistio, jonka voin antaa johtoryhmälle. Ota huomioon tekstin muodossa sopiva kieli. Yksi sivu riittää. Tee lyhyt johdanto selvityksellesi'. Nämä ovat pinnallisia korjauksia, jotka eivät haasta tekoälyn logiikkaa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ae5dd6ac930544f4abd77d3438c59ddd` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept post-decision doubt. STEP 1 (Syntactic Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the alternatives are explicitly compared and evaluated BEFORE the final decision is stated. NEGATIVE CONDITION (RETURN NULL IF MET): evaluated after.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin kohtaa, jossa vaihtoehtoja vertaillaan ja arvioidaan ennen lopullisen päätöksen ilmoittamista. Ensimmäinen tällainen esiintymä löytyi 'ai:'-vastauksesta, jossa kaksi vaihtoehtoa hylätään ja kolmas esitetään ratkaisuna.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0f797e820117411d9934418a1d5d0a82` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing user instructions to modify the final output (e.g., 'change this paragraph to') into List A. Extract exact quotes containing alterations to the underlying instructions or logic into List B. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Käyttäjä antoi ohjeen muuttaa taustalla olevia ohjeita/logiikkaa pyytämällä tekoälyä huomioimaan aiemmin antamansa kritiikin ja tekemään ehdotuksen uudelleen. Tämä on ensimmäinen tällainen ohje kronologisessa järjestyksessä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_76df73280fc943cc9434d44efc8116e8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept 'fully justified' without a traced reasoning path. STEP 1 (Syntactic Anchor): Find causal justification markers (e.g. 'because of risk X', 'to prevent Y', 'therefore blocked'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a security action is paired with an explicit, documented risk assessment.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Lauseessa kuvataan turvallisuustoimi (omat/jaetut työhuoneet) ja perustellaan se nimenomaisella riskinarvioinnilla (luottamuksellisen tiedon käsittely). Tämä vastaa säännön ehtoa, jossa turvallisuustoimi yhdistetään dokumentoituun riskinarviointiin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_34259a6c02b74917b12f74b5f3839a66` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers ('is the best', 'must be done', 'is the only way'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. EXTRACTION CONDITION: no empirical data or external reference exists in the same paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): data exists.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Etsin dogmaattisia absoluuttisia markkereita, kuten 'on paras', 'on pakko tehdä' tai 'on ainoa tapa'. Vaikka tekstissä on vahvoja suosituksia ja velvoitteita (esim. 'velvoitetaan'), ne eivät ole dogmaattisia väitteitä siitä, että jokin olisi 'ainoa' tai 'paras' tapa ilman perusteluja. 'Parhaalla mahdollisella ergonomialla' viittaa laadun maksimointiin, ei dogmiin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Lause sisältää dogmaattisen absoluuttisen merkitsijän 'paras kompromissi'. Samassa kappaleessa ei ole empiiristä dataa tai ulkoista viittausta, joka tukisi tätä väitettä suoraan, mikä täyttää poimintaehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5b0573225735409b8ef3d3eac041236d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers (e.g., 'always', '100% guaranteed', 'it is a fact that'). STEP 2 (Bounding Box): Scan the same paragraph. If the absolute claim is made regarding a compliance or archival rule BUT no external framework (ARMA, ISO, law) is cited in that paragraph. Do not accept absolute claims that are mathematically verifiable. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstistä ei löytynyt dogmaattisia absoluuttisia merkintöjä compliance- tai arkistointisäännöistä, jotka eivät olisi sisältäneet ulkoisen viitekehyksen mainintaa. Kaikki vahvat väitteet joko viittasivat ulkoisiin lähteisiin tai eivät koskeneet compliance- tai arkistointisääntöjä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Toinen 'ai:'-lohko sisältää absoluuttisen markkerin 'aina' lauseessa 'Yhteiset pedagogiset kehityspäivät tehdään aina kampuksella.' Tämä on operatiivinen sääntö, eikä samassa kappaleessa viitata ulkoiseen viitekehykseen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0ab09c0daa9f4aeaad264c00944c5332` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find integration markers (e.g., 'simultaneously achieving', 'balances X and Y through'). STEP 2 (Bounding Box): Scan the paragraph. If a specific mechanism is described that actively satisfies two typically opposing ARMA principles (e.g., Protection vs Availability). Do not accept claims of balance without describing the physical mechanism. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Lause kuvaa mekanismin ('limitoidaan päivät'), joka samanaikaisesti saavuttaa useita etuja (estää siiloutumisen, mahdollistaa mentoroinnin, pitää käyttöasteen tasaisena), mikä vastaa integraatioankkuria.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Tekstistä ei löytynyt integraatiomerkintöjä, jotka kuvaisivat spesifistä mekanismia, joka aktiivisesti tyydyttäisi kahta tyypillisesti vastakkaista ARMA-periaatetta. Vaikka tekstissä mainittiin tavoitteita kuten 'taloudellisia säästöjä' ja 'organisaation sosiaalista liimaa', näitä ei eksplisiittisesti linkitetty ARMA-periaatteisiin, eikä kuvattu mekanismia niiden tasapainottamiseksi säännön edellyttämällä tavalla.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_453ddf8b14a442e988836098e3c7b55c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb follows to mitigate it. <ambiguity_protocol>ABSOLUTE MITIGATION ENFORCEMENT: You must strictly scan the paragraph containing the risk identification marker. If the paragraph contains a physical action verb that describes a technical, administrative, or physical mitigation or control (e.g., 'encrypted', 'blocked', 'sanitized', 'implemented', 'configured', 'restricted', 'validated', or Finnish equivalents like 'salataan', 'estetään', 'tarkistetaan', 'validoidaan'), the absence of mitigation is falsified, the risk is mitigated, and you MUST conclude 'CONDITION NOT MET' and return JSON null. Proposing future plans to mitigate or dismissing the risk as 'low priority' without physical control verbs DOES NOT satisfy the mitigation requirement and the rule remains satisfied.</ambiguity_protocol> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Ensimmäisessä kappaleessa tunnistetaan useita riskejä ('siiloutumiseen', 'epävarmuuteen tavoitettavuudesta', 'kokemuksiin epäoikeudenmukaisuudesta'), mutta samassa kappaleessa ei ole fyysistä toimintaverbiä, joka kuvaisi teknistä, hallinnollista tai fyysistä lievennystä näille nimenomaisille riskeille. 'Korvata malli' on liian yleinen eikä täytä lievennyksen ehtoa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_44793a48813843f0b48364e890eeba1e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept vague lists. STEP 1 (Syntactic Anchor): Find an explicit listing of factors or variables (e.g. 'Based on the following factors:', 'Variables considered:'). STEP 2 (Bounding Box): Scan the list. EXTRACTION CONDITION: at least two distinct variables or weights are physically defined in the text. NEGATIVE CONDITION (RETURN NULL IF MET): fewer than two are defined.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Etsin eksplisiittisiä luetteloita tekijöistä tai muuttujista. Ensimmäinen löydetty luettelo 'Kampussidonnaiset (Opintosihteerit, IT-lähituki, kiinteistö):' sisältää kolme erillistä kohdetta, mikä on enemmän kuin kaksi. Negatiivinen ehto (alle kaksi määriteltyä) ei täyty, joten lainaus poimitaan.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Sääntö edellyttää, että listassa on vähintään kaksi erillistä muuttujaa. Kaikki tunnistetut listaukset sisälsivät vähintään kaksi erillistä muuttujaa, joten negatiivinen ehto ei täyttynyt.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_40c435f393cb4357b31cf835ca601a54` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find hypothesis generation markers (e.g., 'propose', 'hypothesize', 'we can infer'). STEP 2: EXTRACTION CONDITION: the text generates a new hypothesis and explicitly documents the step-by-step logical friction or trade-offs in its creation. Do not accept hypotheses presented as sudden epiphanies without documented reasoning.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstistä ei löytynyt eksplisiittisiä hypoteesin muodostamisen merkkejä, jotka olisivat dokumentoineet vaiheittain loogista kitkaa tai kompromisseja sen luomisessa. 'Ehdotus' viittaa yleiseen ehdotukseen tai toimintaehdotukseen, ei uuteen hypoteesiin, jonka luomisprosessia olisi kuvattu.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin hypoteesin luomiseen viittaavia merkkejä ja dokumentoitua kitkaa tai kompromisseja sen luomisessa. 'Paholaisen asianajajan' kritiikin jälkeinen 'ai:'-lohko kuvaa alkuperäisen ehdotuksen (hypoteesin) uudelleenmuotoilua kritiikin (kitkan) perusteella, mikä täyttää ehdon.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_45885ef98e7d481084b4378d5b3f2f3f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept appeals to authority. STEP 1 (Syntactic Anchor): Find heuristic or dismissive phrases (e.g. 'typically', 'usually', 'it is known', 'obviously'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the phrase is used to justify a decision WITHOUT citing a specific dataset, numerical weight, or verifiable rule. NEGATIVE CONDITION (RETURN NULL IF MET): a specific source is cited.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Etsin heuristisia tai vähätteleviä fraaseja, joita käytetään päätöksen perusteluun ilman spesifistä lähdettä. Tekstistä ei löytynyt yhtään tällaista fraasia, joka täyttäisi poimintaehdon. Esimerkiksi 'luonnollinen osa' tai 'suosituksena on malli' eivät ole päätöstä perustelevia heuristisia fraaseja tässä kontekstissa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Ensimmäinen heuristinen tai vähättelevä ilmaus, joka ei viittaa spesifiseen tietojoukkoon, numeeriseen painoarvoon tai todennettavissa olevaan sääntöön, löytyi lauseesta 'Oppilaitoksenne kokoiselle organisaatiolle (200 hlö) paras kompromissi on usein 2 päivää kampuksella, 3 päivää etätyömahdollisuutta'. Ilmaus 'paras kompromissi on usein' on heuristinen eikä sitä perustella spesifillä lähteellä tai säännöllä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fa4667af98f84790af9b9a12cd9d7bd0` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Syntactic Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: EXTRACTION CONDITION: the command lacks any specific constraints and allows the AI to freely decide what is important.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Vaikka käyttäjä pyytää 'yhteenvetoa' ja 'muistiota', näihin pyyntöihin liittyy aina useita spesifejä rajoituksia (esim. 'yhden sivun', 'ei jargonia', 'suosituksesi (juuri opetusalalle)', 'sopiva kieli', 'lyhyt johdanto'). Nämä rajoitukset estävät tekoälyä päättämästä vapaasti, mikä on tärkeää, joten komento ei ole 'laaja yhteenvetopyyntö'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Käyttäjä antoi laajan yhteenvetokomennon ('Tee yhden sivun yhteenveto'), joka sisälsi pituusrajoituksen ('yhden sivun') mutta ei sisältöön liittyviä rajoituksia, jolloin tekoäly sai vapaasti päättää, mikä on tärkeää sisällyttää yhteenvetoon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_aa0b85a7febe4a3d9f580223c36a1646` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit absolute status declarations (e.g., 'perfectly secure', 'no issues found', 'fully compliant'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute declaration BUT does NOT contain risk or mitigation vocabulary (e.g., 'risk', 'trade-off', 'vulnerability', 'however') -> ACCEPT. If it contains risk vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'sweeping nature', or subjective 'flawlessness'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Lause sisältää absoluuttisen tilajulistuksen 'vastaa täysin' ('fully compliant') ja kyseinen kappale ei sisällä riskisanastoa, mikä täyttää säännön ehdot.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Tekstistä ei löytynyt eksplisiittisiä absoluuttisia tilajulistuksia (esim. 'täysin turvallinen', 'ei ongelmia', 'täysin yhteensopiva'), jotka eivät sisältäisi riski- tai lievennyssanastoa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_9fd2fff3ab4a46d29b5df31488561dd4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find demands for external grounding (e.g., 'cite a specific source', 'base this strictly on the provided document', 'give me the exact quote'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly restricts the AI to an external, objective anchor. Acceptance of unsourced hallucinated facts. NEGATIVE BOUNDARY: General questions or requests for explanation DO NOT count as external grounding unless they explicitly demand a citation or source material restriction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Käyttäjä kysyy eksplisiittisesti, mihin faktoihin ja taustamateriaaleihin selvitys perustuu, ja pyytää lähteiden listaamista. Tämä on suora vaatimus ulkoiselle perustelulle ja lähteiden luotettavuuden arvioinnille.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_3b951170f9f54f649b7da95fb9f121e6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept explicit hypothesis testing. STEP 1 (Syntactic Anchor): Find descriptive reporting verbs (e.g., 'the data shows', 'we observed', 'indicates'). STEP 2 (Bounding Box): Scan the paragraph. If the observation lacks a formulated hypothesis that could be tested or disproven (e.g. no 'if X then Y' structure). Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Sääntö etsii kuvailevia raportointiverbejä, joita seuraa havainto ilman testattavissa olevaa hypoteesia. Tekstissä käytetään raportointiverbejä (esim. 'osoittavat'), mutta ne viittaavat aina ulkoisiin tutkimustuloksiin (Työterveyslaitos, Stanfordin yliopisto), jotka oletettavasti perustuvat hypoteeseihin. Tekoäly ei esitä omia havaintojaan ilman hypoteesia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Lauseessa käytetään kuvailevaa raportointiverbiä 'osoittavat', ja se esittää havainnon ilman eksplisiittisesti muotoiltua 'jos X niin Y' -tyyppistä hypoteesia, joka voitaisiin testata tai kumota tekstin sisällä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_47bade191cf346ec818757f081f6aef3` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find contrast markers ('however, data shows that', 'despite X, metric Y'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a specific counter-argument is addressed using empirical counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): it's dismissed rhetorically. Rhetorical dismissals without data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [FALSE]:**
  > *Tekstistä ei löytynyt kontrastimerkkejä, jotka esittäisivät vastaväitteen ja kumoaisivat sen empiirisellä vastadatalla. Vaikka 'paholaisen asianajaja' -osuudessa esitetään kritiikkiä, se ei kumoa vastaväitteitä empiirisellä datalla, vaan esittää uusia argumentteja ja ongelmia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [TRUE]:**
  > *Etsin kontrastimerkkejä, joita seuraa empiirinen vastadata. Lause 'Mutta nyt näemme kolikon kääntöpuolen: työn ja vapaa-ajan rajat hämärtyvät. Tutkimukset (kuten Työterveyslaitoksen raportit) osoittavat, että etätyöläiset tekevät huomaamattaan pidempää päivää ja kärsivät "digiähkystä".' sisältää kontrastimerkin ('Mutta nyt näemme kolikon kääntöpuolen') ja viittauksen empiiriseen dataan ('Tutkimukset (kuten Työterveyslaitoksen raportit) osoittavat'). Negatiivinen ehto (retorinen sivuuttaminen) ei täyty, koska empiiristä dataa esitetään.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_20e76f768d24458fb2cc131b2bde4e04` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find blind procedural markers (e.g., 'must follow', 'the checklist requires', 'according to protocol'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a rule is enforced explicitly despite stated contextual evidence that it might be suboptimal. Do not accept justifiable adherence to safety or compliance protocols where no counter-evidence is presented.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_67ebf9ea0446459f93a7f35cad392404) - [TRUE]:**
  > *Sääntö edellyttää sokeiden menettelytapamerkintöjen löytämistä, joissa sääntöä noudatetaan huolimatta siitä, että kontekstuaalinen näyttö viittaa sen olevan suboptimaalinen. 'ai:'-lohko ennen 'paholaisen asianajaja' -osiota esittää säännön 'Otetaan käyttöön sääntö: 'Oikeus olla tavoittamattomissa'. Teams-viesteihin ja sähköposteihin ei odoteta vastausta klo 17:00 jälkeen.'. 'Paholaisen asianajaja' -osiossa tätä sääntöä kritisoidaan suoraan: 'Tämä sääntö osoittaa, että politiikka on tehty perinteisen virka-aikatyön ehdoilla, eikä se ymmärnä aikuiskoulutuksen todellista rytmiä. Se joko pakottaa opettajat joustamaan salaa (mikä lisää stressiä) tai halvaannuttaa iltaopiskelijoiden tukipalvelut.' Tämä täyttää ehdon, jossa sääntöä noudatetaan (tai ehdotetaan noudatettavaksi) huolimatta sen suboptimaalisuudesta kontekstissa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1227ec0b70dc4763ac021da9f33f5f7d) - [FALSE]:**
  > *Sääntö edellyttää sokeiden menettelytapamerkkien (esim. 'on noudatettava', 'tarkistuslista vaatii', 'protokollan mukaan') löytämistä, joissa sääntöä noudatetaan nimenomaisesti huolimatta siitä, että kontekstuaalinen näyttö viittaa sen mahdolliseen epäoptimaalisuuteen. Lähdetekstissä ei ole tapausta, jossa sääntöä noudatettaisiin nimenomaisesti, vaikka sen tiedettäisiin olevan epäoptimaalinen. Sen sijaan teksti joko ehdottaa uusia, optimoituja sääntöjä tai kritisoi vanhoja epäoptimaalisia käytäntöjä.  [5. VALIDATION DECISION: PASS]*

---

