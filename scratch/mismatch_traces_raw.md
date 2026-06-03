# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 185
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 87.03 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.7192
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.7195
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1297
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 24 kpl
- **PASSED -> FAILED:** 9
- **FAILED -> PASSED:** 15
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_9ab273ce743ac29e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph evaluating a successful outcome or positive achievement. STEP 2: Verify if the paragraph or immediate surrounding section completely omits any epistemic boundary or uncertainty markers. <ambiguity_protocol>ABSOLUTE ABSENCE ENFORCEMENT: You must prove that epistemic boundary markers are COMPLETELY absent from the surrounding section. Epistemic boundary markers include words/phrases like 'however', 'limitations', 'failed to', 'uncertainty', 'but', 'silti', 'kuitenkin', 'rajoitus', 'epävarmuus'. If you locate even a single such marker in the section, the absence is falsified, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Presence detected: Positiivista saavutusta tai tulevaisuuden suuntaa käsittelevässä osiossa ('Sitran Strateginen Suunta: Tulevaisuusresilienssi') löytyi episteeeminen rajausmerkki 'rajoite'. Tämä rikkoo ehdon, jonka mukaan osion tulisi täysin jättää pois tällaiset merkit.. Exceptions audit: Tuotetekstin kappaleessa, joka alkaa 'Sitran megatrendien kehitys vuosien 2017 ja 2023 välillä osoittaa...' ja päättyy '...panostettava **tulevaisuusresilienssiin**.', kuvataan polkua menestykseen. Tässä kappaleessa ei ole yhtään epistemiologista raja- tai epävarmuusmerkkiä ('kuitenkin', 'rajoitus', 'epävarmuus', 'silti', 'mutta', 'ei onnistunut', 'rajallisuus'). Koska tällaisia merkkejä ei löytynyt, negatiivinen ehto (merkintöjen puuttuminen) täyttyi, mikä tarkoittaa, että sääntöä ei rikottu. Siksi `exact_quote` on tyhjä merkkijono.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Vaikka tekstissä on osioita, jotka käsittelevät tulevaa menestystä ja strategista suuntaa ('Sitran Strateginen Suunta: Tulevaisuusresilienssi'), tämä osio sisältää sanan 'rajoite', joka on episteeeminen rajausmerkki. Säännön mukaan, jos yksikin tällainen merkki löytyy, ehdon täydellisestä puuttumisesta ei täyty, ja siksi palautetaan null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_79f305842b933ea5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find explicit dialectical reasoning ('we evaluated option A, but chose B because'). STEP 2 (Bounding Box): Scan the paragraph. If the author explicitly documents a rejected compliance alternative and provides data-driven reasoning for the final choice. Do not accept simple lists of options without rejection reasoning.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Presence detected: Kappaleessa esitetään dialektinen päättely, jossa hylätään vaihtoehto ('ei vain kustannussäästönä') ja perustellaan valittu lähestymistapa ('välineenä reilun digimaailman luomiseen').. Exceptions audit: Etsin eksplisiittistä dialektista päättelyä, jossa dokumentoidaan hylätty vaatimustenmukaisuusvaihtoehto ja annetaan datalähtöinen perustelu lopulliselle valinnalle. Tekstistä ei löytynyt tällaista päättelyä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää eksplisiittisen dialektisen päättelyn (esim. 'arvioimme vaihtoehdon A, mutta valitsimme B:n, koska') löytämistä 'ai:'-lohkosta, jossa kirjoittaja dokumentoi hylätyn vaatimustenmukaisuusvaihtoehdon ja antaa dataan perustuvan perustelun lopulliselle valinnalle. Läpikäynnissä ei löytynyt yhtään tällaista suomenkielistä vastinetta 'ai:'-lohkoista.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_7284133a24e27b16` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find explicit methodology links (e.g., 'in accordance with', 'following the protocol defined by'). STEP 2 (Bounding Box): Scan the sentence. If an action is explicitly linked to a named guideline or procedure (ARMA Compliance). Do not evaluate the 'quality' of the methodology.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Mitigating exception found: Etsin eksplisiittisiä metodologialinkkejä, joissa toiminto linkitetään nimettyyn ohjeistukseen tai menettelyyn. Lause 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset tekevät kestävyydestä pakollista (compliance)' linkittää kestävyyden pakollisuuden (toiminto) nimettyihin säädöksiin (ohjeistus/menettely).  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää eksplisiittisten metodologialinkkien (esim. 'mukaisesti', 'noudattaen protokollaa, jonka on määritellyt') löytämistä 'ai:'-lohkosta, jossa toiminto on eksplisiittisesti linkitetty nimettyyn ohjeeseen tai menettelyyn. Läpikäynnissä ei löytynyt yhtään tällaista suomenkielistä vastinetta 'ai:'-lohkoista.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6bf0433f60924302` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. Vague filler words.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt syntaktisia ankkureita, kuten 'näissä erityisissä olosuhteissa' tai 'ensisijaisesti kun', jotka määrittelisivät eksplisiittisesti väitteen rajat tai todennäköisyydet. Teksti käyttää vahvaa ja määrätietoista kieltä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Sana 'Vain' (only) toimii ehdollisena tarkentimena, joka määrittelee eksplisiittisesti rajat sille, mitkä liiketoimintamallit saavat pääomaa tulevaisuudessa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_dfa97bbeeb1dafc5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find criteria anchoring markers (e.g., 'measured against', 'based on the standard of', 'criteria'). STEP 2: EXTRACTION CONDITION: an evaluation explicitly links its judgment to a stated benchmark or metric. Do not accept floating evaluations with unstated goalposts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Etsin arviointia, joka on nimenomaisesti sidottu mainittuun vertailukohtaan tai mittariin. Tekstissä mainitaan säädöksiä kuten 'CSRD-direktiivi ja EU-taksonomia', mutta niitä ei käytetä minkään arviointiin tekstin sisällä, vaan niiden vaikutuksia kuvataan. Muut arviot ovat yleisiä havaintoja tai strategisia suosituksia, eivätkä ne linkity selkeästi nimettyihin kriteereihin tai standardeihin.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Presence detected: Teksti linkittää eksplisiittisesti arvion ('tekevät kestävyydestä pakollista') mainittuihin vertailukohtiin ('CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset').. Exceptions audit: Skannasin 'product_text'-tekstin kriteereitä ankkuroivien markkereiden (esim. 'mitattuna', 'perustuen standardiin', 'kriteerit') varalta. Teksti esittää havaintoja ja strategisia suosituksia, mutta ei eksplisiittisesti linkitä arviointiaan johonkin nimettyyn vertailukohtaan tai mittariin käyttäen näitä markkereita. Siksi ehto ei täyttynyt.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d5d27ea4cfe44c44` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate engagement quality. STEP 1 (Syntactic Anchor): Find an explicit counter-argument or risk raised in the text (e.g., 'Despite the risk', 'Opponents argue', 'Vaikka'). STEP 2 (Bounding Box): Scan the subsequent sentences. EXTRACTION CONDITION: the counter-argument is stated but not logically dismantled with data. NEGATIVE CONDITION (RETURN NULL IF MET): it is dismantled step-by-step.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Etsin eksplisiittistä vastaväitettä tai riskiä, joka esitetään, mutta jota ei pureta loogisesti datan avulla. Teksti ei sisällä selkeää vastaväitettä tai riskiä, joka olisi esitetty ja jätetty purkamatta datan avulla. Se keskittyy enemmän nykytilanteen kuvaukseen ja strategisiin toimenpiteisiin.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Lause 'Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta**' esittää 'rajoite'-sanan riskinä tai vastaväitteenä. Tämä vastaväite kuitenkin uudelleenkehystetään välittömästi 'kasvun perustaksi' ilman, että sitä loogisesti purettaisiin datalla, mikä täyttää ehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_8f668ea29869ba8b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Etsin lopputuloksen arviointia ja tarkistin, onko rajoituksia käsitelty samassa osiossa. `chat_log`-osiossa, tekoälyn vastauksessa "poista taulukot ja kerro ne tekstinä", kohdassa "III. Ennusteiden Osuvuus (Jälkeenpäin Katsoen)" mainitaan "Monimutkainen/Aliarvioitu", joka on selkeä rajoituksen tai aliarvioinnin käsittely. Koska rajoituksia käsiteltiin, negatiivinen ehto täyttyi.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Presence detected: AI antaa positiivisen arvion mahdollisuudesta yhdistellä megatrendejä. Tässä osiossa ei mainita rajoituksia tai epäonnistumisia.. Exceptions audit: Etsin lopputuloksen arviointia ('menestys') ja tarkistin, jättääkö teksti kokonaan pois maininnat poikkeustapauksista, epäonnistumisista tai rajoituksista. Tuoteteksti käsittelee laajasti kriisejä, haasteita ja rajoituksia ('Ekologinen Resilienssikriisi', 'Markkinoiden Fragmentaatio', 'Työvoimapula'), joten rajoituksia käsiteltiin. Negatiivinen ehto täyttyi.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_a9bbdcc4d1bfc915` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit optimization commands for proxy metrics (e.g., 'maximize the score', 'increase the word count', 'make it sound professional'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user demands optimization of a surface metric without linking it to a qualitative real-world outcome. Do not accept if the metric is explicitly tied back to a measure of effectiveness.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän syötteistä ei löytynyt eksplisiittisiä komentoja proxy-mittareiden optimointiin, kuten sanamäärän lisäämiseen tai ammattimaisemman sävyn pyytämiseen ilman laadullista kytkentää. Käyttäjän pyynnöt olivat joko rakenteellisia tai sisällöllisiä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää '1 sivun raportti', mikä on pinnallinen mittari (sivumäärä) ilman eksplisiittistä linkitystä laadulliseen lopputulokseen. Tämä täyttää ehdon 'demands optimization of a surface metric without linking it to a qualitative real-world outcome'.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_61c1b43bc6f5406f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EXTRACTION CONDITION: role prefixes exist, focus on 'ai:' output compared to 'user:' input. BANNED LOGIC: Do not evaluate 'coincidence' abstractly. STEP 1 (Syntactic Anchor): Identify a novel concept, specific methodology, or data point introduced by the AI. STEP 2 (Bounding Box): Scan the preceding 'user:' prompt. NEGATIVE CONDITION (RETURN NULL IF MET): the user prompt did NOT explicitly request this concept or methodology. If the user requested it.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Mitigating exception found: Tekoäly esitteli käsitteen "Ekologinen Resilienssikriisi" sen jälkeen, kun käyttäjä kysyi yleisesti "supermegatrendeistä", mutta ei pyytänyt tätä nimenomaista käsitettä. Negatiivinen ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Vaikka AI esitteli 'tulevaisuusresilienssiin'-käsitteen lopullisessa tuotoksessa, käyttäjän edeltävä kehotus ei nimenomaisesti pyytänyt tätä käsitettä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5f71c2e291f1ae4e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept 'fully justified' without a traced reasoning path. STEP 1 (Syntactic Anchor): Find causal justification markers (e.g. 'because of risk X', 'to prevent Y', 'therefore blocked'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a security action is paired with an explicit, documented risk assessment.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Syntaktisia ankkureita, jotka yhdistäisivät turvatoimenpiteen riskinarviointiin kausaalisilla perusteluilla (esim. 'koska', 'siksi'), ei löytynyt lähdetekstistä. Teksti kuvaa vaikutuksia ja strategisia toimenpiteitä, mutta ei niiden eksplisiittistä kausaalista perustelua.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Turvallisuustoimenpide ('Toimitusketjun lyhentäminen ja läpinäkyvyys') on yhdistetty riskinarviointiin ('vähentävät riskejä'), mikä täyttää ehdon syy-seuraussuhteen perustelusta. Tämä on rikkomus käänteisessä säännössä, koska perustelu on läsnä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6be555cac0b9115b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Mitigating exception found: Etsin menettelyllisiä järjestysmarkkereita, jotka eivät sisällä eksplisiittisiä synteesi- tai päättelyverbejä. Löysin kohdan, jossa luetellaan kolme kohtaa 'Johtoryhmälle tämä tarkoittaa:', ja nämä kohdat sisältävät järjestysnumerot (1., 2., 3.) ilman synteesi- tai päättelyverbejä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää menettelyllisten sekvenssimerkkien (esim. 'ensimmäiseksi', 'toiseksi', 'sitten') löytämistä 'ai:'-lohkosta. Jos kappale sisältää menettelyllisiä merkkejä, mutta EI sisällä eksplisiittisiä synteesi- tai päättelyverbejä (esim. 'analysoitu', 'päätelty', 'syntetisoitu', 'siksi'), se hyväksytään. Useat 'ai:'-lohkot sisältävät numeroituja listoja (esim. '1. Luonto ja Kestävyys', '1. Ekologisen Kriisin Edellyttämä Sopeutuminen'), jotka ovat menettelyllisiä merkkejä. Kuitenkin kaikki nämä kappaleet sisältävät myös synteesi- tai päättelyverbejä tai -lausekkeita (esim. 'Sitra korostaa', 'on ratkaiseva', 'Tämä tarkoittaa', 'Ydin:', 'Sitran Suunta:'), mikä estää hyväksymisen negatiivisen ehdon mukaisesti.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_513d51a119ef4fd6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Etsin kausaalisia hyppyjä tai johtopäätöksiä, jotka perustuvat vain näkyvään todisteeseen ja jättävät huomiotta tuntemattomat tekijät. Teksti ei kuitenkaan sisällä selkeää esimerkkiä tällaisesta päättelystä, jossa tuntemattomat tekijät jätettäisiin aktiivisesti huomiotta samalla kun tehdään lopullinen johtopäätös.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Lause 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' esittää suoran kausaalisen yhteyden kahden ilmiön välillä. Tämä on määrittelevä johtopäätös, joka perustuu havaittuun ilmiöön ilman, että monimutkaisia välivaiheita tai muita vaikuttavia tekijöitä eritellään tai tuntemattomia tekijöitä kartoitetaan eksplisiittisesti.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_4fa47fd622e62e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision. Do not accept generic references to 'standards' without naming them.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Presence detected: Lauseessa mainitaan nimenomaisesti ulkoiset viitekehykset 'CSRD-direktiivin' ja 'EU-taksonomian' ja linkitetään niihin toiminto ('tekevät kestävyydestä pakollista (compliance)').. Exceptions audit: Etsin muodollisia viittausmarkkereita, jotka nimeävät ulkoisen viitekehyksen ja siihen liittyvän alaperiaatteen tai lausekkeen. Tekstissä mainitaan 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset', jotka tekevät kestävyydestä pakollista. Vaikka nämä ovat nimettyjä säädöksiä, ne eivät viittaa spesifiseen alaperiaatteeseen tai lausekkeeseen ARMA- tai ISO-kontekstissa, vaan yleisemmin sääntelyyn.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää muodollisten viittausmerkkien (esim. 'ARMA-periaatteen mukaan', 'ISO-standardi') löytämistä 'ai:'-lohkosta, jossa nimetty ulkoinen viitekehys ja spesifinen ala-periaate tai lauseke mainitaan päätöksen perusteluna. Läpikäynnissä ei löytynyt yhtään tällaista suomenkielistä vastinetta 'ai:'-lohkoista.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_f142c3fa1d08cc2d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: EXTRACTION CONDITION: the user explicitly restricts the AI to the provided data and demands exact evidence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Mitigating exception found: Lause 'raporttien perusteella' rajoittaa tekoälyn vastaamaan ainoastaan annettujen raporttien pohjalta, mikä vastaa 'perustuen vain' -ankkuria ja vaatimusta tarkasta näytöstä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: The user prompts were scanned for extraction anchors such as 'poimi suoraan', 'tarkka lainaus', 'älä keksi itse', or 'perustuen vain'. No such anchors were found in any of the user's inputs.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2303fd9ca0b0fa67` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept generic terms like 'safe'. STEP 1 (Syntactic Anchor): Find explicit references to standard security protocols (e.g. 'policy', 'standard', 'guideline', 'OWASP'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text physically demonstrates adherence to a named standard.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Fyysisiä ankkureita, jotka viittaavat nimenomaisiin standarditurvaprotokolliin, kuten 'politiikka', 'standardi', 'ohjeistus' tai 'OWASP', ei löytynyt lähdetekstistä. Mainitut säädökset (CSRD, EU-taksonomia) eivät ole vaadittuja turvaprotokollia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Presence detected: Teksti viittaa eksplisiittisesti 'CSRD-direktiivin ja EU-taksonomian kaltaisiin säädöksiin' ja mainitsee 'compliance', mikä osoittaa noudattamista nimetyille standardeille/säädöksille.. Exceptions audit: Teksti ei fyysisesti osoita noudattavansa nimettyä turvallisuusstandardia. Vaikka 'CSRD-direktiivi' ja 'EU-taksonomia' ovat säädöksiä, ne liittyvät kestävyyteen, eivät suoraan turvallisuusprotokolliin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_f48b82675bb04c12` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'mastery'. STEP 1 (Syntactic Anchor): Find structural breakdown markers (e.g., 'firstly', 'component A', 'broken down into', 'ensimmäiseksi'). STEP 2: EXTRACTION CONDITION: the text physically separates a complex problem into at least three distinct, testable sub-components. NEGATIVE CONDITION (RETURN NULL IF MET): it remains a single monolithic block.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Mitigating exception found: Teksti jakaa monimutkaisen ongelman 'Supermegatrendit' kolmeen erilliseen ja nimettyyn alakomponenttiin ('Ekologinen Resilienssikriisi', 'Geoteknologinen Valtaistelu', 'Epävarmuuden Sosiaalinen Polarisointi'), jotka on esitetty selkeästi numeroituina otsikoina. Tämä täyttää ehdon ongelman pilkkomisesta vähintään kolmeen osaan.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Teksti erittelee kompleksisen ongelman ('Supermegatrendit ja Liiketoimintavaikutukset') kolmeen erilliseen supermegatrendiin. Vaikka erittely on selkeä, näitä osia ei voida poimia yhtenäisenä, fyysisesti jatkuvana lainauksena, koska niiden välissä on muuta tekstiä ja taulukoita.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0eb49f05fdd6deb9` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept generic errors; must be an absolute fabrication (LLM09 Overreliance). STEP 1 (Syntactic Anchor): Find a factual claim (dates, names, specific data points). STEP 2 (Search Verification): Verify the claim's logic. EXTRACTION CONDITION: the claim is demonstrably false or fabricated but presented with absolute certainty.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [TRUE]:**
  > *Presence detected: Tekoälyn tuottamassa raportissa mainitaan 'Sitran Megatrendiraportit 2023' faktapohjaisena väitteenä. Käyttäjän reflektio kuitenkin osoittaa, että 'tehtävän vaatimaa viimeistä raporttia ei ollut annettu', mikä tarkoittaa, että tämä väite on tekaistu.. Exceptions audit: No factual claim in the AI's output was found to be demonstrably false or fabricated and presented with absolute certainty. The user's reflection points to an issue with the input data, not a fabrication by the AI.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei ole faktaväitteitä, jotka olisivat todistettavasti virheellisiä tai keksittyjä ja esitetty ehdottomalla varmuudella. Mainitut päivämäärät ovat raportin oma päivämäärä tai viittauksia olemassa oleviin dokumentteihin/ilmiöihin.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_92af590371ba4f3d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'thoughtfulness'. STEP 1 (Syntactic Anchor): Find dialectical markers (e.g., 'While X is true, Y proves', 'Reconciling these', 'Toisaalta'). STEP 2: EXTRACTION CONDITION: the text explicitly introduces two opposing variables and generates a third, novel conclusion (synthesis) rather than just picking one.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Etsin dialektisia merkkejä, jotka esittävät kaksi vastakkaista muuttujaa ja luovat kolmannen, uuden johtopäätöksen (synteesin). Teksti kuvaa megatrendien kietoutumista ja niiden vaikutuksia, mutta ei eksplisiittisesti esitä kahta vastakkaista muuttujaa ja niistä syntyvää uutta synteesiä 'Toisaalta'-tyyppisellä rakenteella.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Presence detected: Teksti esittelee kaksi vastakkaista näkökulmaa ('rajoite' vs. 'kasvun perusta') ja luo niistä kolmannen, uuden johtopäätöksen (synteesin), mikä täyttää dialektisen synteesin ehdon.. Exceptions audit: Tekstistä ei löytynyt eksplisiittisiä dialektisiä merkkejä ('Toisaalta', 'While X is true, Y proves', 'Reconciling these'), jotka esittelisivät kaksi vastakkaista muuttujaa ja tuottaisivat kolmannen, uuden synteesin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2dabbdba90a549ae` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find formal citations ('according to the methodology of', 'based on the study by'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the logical rule is explicitly backed by a verifiable external methodology or study. NEGATIVE CONDITION (RETURN NULL IF MET): it's a vague reference ('research shows'). Vague references to 'studies' or 'science'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt syntaktisia ankkureita, kuten 'metodologian mukaan' tai 'perustuen tutkimukseen', jotka viittaisivat muodolliseen viittaukseen loogisen säännön tueksi. Yleinen viite Sitran raportteihin ei täytä tätä ehtoa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Presence detected: Lauseessa viitataan muodollisiin säädöksiin ('CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset'), jotka tukevat loogista sääntöä kestävyyden pakollisuudesta. Tämä ei ole epämääräinen viittaus, joten negatiivinen ehto ei täyty ja poimintaehto täyttyy.. Exceptions audit: Tekstistä ei löytynyt muodollisia viittauksia ('menetelmän mukaan', 'tutkimuksen perusteella'), jotka tukisivat eksplisiittisesti loogista sääntöä. Yleinen viite Sitran raportteihin ei täytä tätä ehtoa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b65277ca32d4c0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'depth' subjectively. STEP 1 (Syntactic Anchor): Find absolute conclusion words (e.g., 'clearly', 'obviously', 'must be', 'selvästi'). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: the conclusion is presented without a multi-step logical deduction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Etsin absoluuttisia johtopäätössanoja, kuten 'selvästi', jotka esitetään ilman monivaiheista loogista päättelyä. Tekstissä ei ole tällaista absoluuttista johtopäätöstä, joka olisi esitetty ilman edeltävää tai seuraavaa monivaiheista loogista päättelyä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Lause 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' sisältää absoluuttisen johtopäätöksen ('ainoa tapa'), joka esitetään ilman monivaiheista loogista päättelyä tai yksityiskohtaista perustelua sen ainutlaatuisuudesta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_4956abf072945f43` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Syntactic Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context. NEGATIVE CONDITION (RETURN NULL IF MET): the alternative is dismissed without evidence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Etsin viittausta vaihtoehtoiseen malliin ja sen kumoamista todisteilla. Löysin 'ai:'-vastauksesta ilmaisun "pelkkä toivetila" vaihtoehtona Sitran näkemykselle. Tämä vaihtoehto kumottiin laadullisesti ("korostaa samanaikaista sopeutumista ja uudistumista") ilman konkreettisia datapisteitä tai loogisia ristiriitoja. Koska vaihtoehto hylättiin ilman todisteita, negatiivinen ehto täy (vaihtoehto hylättiin ilman todisteita) täyttyi.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Etsin viittausta vaihtoehtoiseen malliin ja tarkistin, puretaanko se todisteiden avulla. Teksti esittää 'rajoite'-käsitteen ja kumoaa sen 'uuden taloudellisen kasvun perusta' -väitteellä, mikä on looginen ristiriita. Koska vaihtoehtoa ei hylätty ilman todisteita, negatiivinen ehto ei täyttynyt ja rike löytyi.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_247927c98b0c46f8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. Rebuttals that provide counter-data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt syntaktisia ankkureita, kuten 'vaikka X on totta, sillä ei ole väliä' tai 'riippumatta', jotka osoittaisivat vasta-argumentin ohittamisen ilman vasta-dataa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Teksti mainitsee vasta-argumentin ('rajoite'), mutta ohittaa sen retorisesti uudelleenkehystämällä sen 'uuden taloudellisen kasvun perustaksi' esittämättä vastadataa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_1532d756b11a4259` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find breakdown condition markers (e.g., 'breaks down when', 'does not apply if', 'fails beyond', 'invalidated when'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the breakdown marker AND ALSO contains explicit numerical limits or physical threshold vocabulary (e.g., 'exceeds', '<', '>', 'limit of', 'threshold') -> ACCEPT. If it lacks explicit measurement limits -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'deep humility' or whether the claim is logically 'voided'. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Syntaktisia ankkureita (hajoamiseen tai soveltumattomuuteen viittaavia markkereita) ei löytynyt 'ai:'-lohkoista. Siksi ehdot eivät täyttyneet.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Mitigating exception found: Ankkuri 'murentuessa' (breakdown condition) ja kynnyssanasto 'maapallon rajoihin' (physical threshold) löytyivät samasta lauseesta `ai:`-lohkosta. Lause kuvaa järjestelmän hajoamista, kun rajat saavutetaan.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_55dfd9cb0adec620` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb follows to mitigate it. <ambiguity_protocol>ABSOLUTE MITIGATION ENFORCEMENT: You must strictly scan the paragraph containing the risk identification marker. If the paragraph contains a physical action verb that describes a technical, administrative, or physical mitigation or control (e.g., 'encrypted', 'blocked', 'sanitized', 'implemented', 'configured', 'restricted', 'validated', or Finnish equivalents like 'salataan', 'estetään', 'tarkistetaan', 'validoidaan'), the absence of mitigation is falsified, the risk is mitigated, and you MUST conclude 'CONDITION NOT MET' and return JSON null. Proposing future plans to mitigate or dismissing the risk as 'low priority' without physical control verbs DOES NOT satisfy the mitigation requirement and the rule remains satisfied.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1b0c6ec14c244061a98fdf1c4d7d6932) - [FALSE]:**
  > *No presence of target concept detected: Vaikka riskin tunnistavia markkereita, kuten 'riskejä' ja 'maineriskin', löytyi, jokaista tunnistettua riskiä seurasi välittömästi samassa kappaleessa fyysinen toimintaverbi, joka kuvasi lieventävää toimenpidettä (esim. 'Investoinnit', 'lyhentäminen', 'vähentävät', 'Panostus', 'Kehitetään ja käytetään'). Siksi poimintaehto (riski tunnistettu ilman lievennystä) ei täyttynyt.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_29c9ff4011f24f958fc841d645d01a53) - [TRUE]:**
  > *Presence detected: Riski 'Sääntelypaine' tunnistetaan, mutta sitä ei seuraa fyysinen toimintaverbi sen lieventämiseksi samassa kappaleessa. 'Pakollinen' on adjektiivi ja 'saavat' kuvaa seurausta, ei aktiivista lievennystoimenpidettä.. Exceptions audit: Kaikki tunnistetut riskit (esim. 'Kustannus- ja Toimitusketjuhäiriöt', 'Sääntelypaine', 'Markkinoiden Fragmentaatio', 'Luotamuskriisi', 'Työvoimapula ja Tuotavuus', 'Kysynnän Volatiliteeti') seurasivat fyysistä toimintaverbiä, joka kuvasi niiden lieventämistä (esim. 'vähentävät riskejä', 'pakollinen kilpailuvalti', 'Panostus kyberturvallisuuteen', 'Kehitetään ja käytetään teknologiaa', 'investoinnit', 'hallitsemiseksi'). Siksi ehdon negatiivinen ehto ei täyttynyt.  [5. VALIDATION DECISION: PASS]*

---

