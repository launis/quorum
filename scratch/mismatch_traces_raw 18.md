# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 91.40 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.8280
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.8280
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.0860
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 16 kpl
- **PASSED -> FAILED:** 9
- **FAILED -> PASSED:** 7
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_3d3f1162d2ff1558` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** <syntactic_constraint> <anchors> <anchor>a limitation is</anchor> <anchor>rajoituksena on</anchor> <anchor>puutteena on</anchor> <anchor>heikkoutena on</anchor> </anchors> <transitions> <transition>however</transition> <transition>regardless</transition> <transition>kuitenkin</transition> <transition>silti</transition> </transitions> <extraction_condition> Verify if a limitation acknowledgment from the <anchors> block is immediately followed (within two sentences) by a dismissive logical transition word from the <transitions> block that rationalizes away the limitation. </extraction_condition> <ambiguity_protocol> If the limitation anchor from <anchors> is absent, or if the dismissive marker from <transitions> is missing, or if new empirical data is cited to solve the limitation, you MUST return JSON null. Do not rationalize or excuse missing evidence. </ambiguity_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Sääntö on käänteinen (vice rule). Teksti sisältää lauseen, jossa sana "rajoite" esiintyy. Välittömästi sen jälkeen rajoituksen merkitys kumotaan ja käännetään positiiviseksi käyttämällä sanaa "vaan", joka toimii tässä yhteydessä säännön määrittelemänä vähättelevänä siirtymänä. Tämä vastaa säännön ehtoja rikkomuksen löytymisestä.*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *Tämä on käänteinen sääntö (vice rule). Tekstistä ei löytynyt säännön määrittelemää syntaktista ketjua, jossa rajoituksen ankkurisanaa (esim. 'rajoituksena on') seuraisi välittömästi vähättelevä siirtymäsana (esim. 'kuitenkin'). Lause "Luonnon kantokyvyn rajat eivät ole vain rajoite, vaan uuden taloudellisen kasvun perusta" käyttää sanaa 'rajoite', mutta uudelleenkehystää sen 'vaan'-sanalla, mikä ei ole säännön määrittelemä vähättelevä siirtymä.*

---

### Atom-ID: `tda_09d4ef9d436a49e3` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept implicit modesty. STEP 1 (Syntactic Anchor): Find an explicit epistemic boundary marker (e.g. 'may not apply', 'exception', 'edge case', 'out of scope'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the text physically identifies a scenario where the model or logic fails or is limited. NEGATIVE CONDITION (RETURN NULL IF MET): absent.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää eksplisiittisen episteemisen rajan ilmaisua. Lähdeteksti ei sisällä mitään lauseita, jotka määrittelisivät skenaarion, jossa malli tai logiikka epäonnistuu tai on rajoittunut.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [TRUE]:**
  > *Mitigating exception found: Säännön edellyttämiä eksplisiittisiä episteemisiä rajausmerkkejä, kuten 'poikkeus' tai 'reunatapaus', ei esiinny lähdetekstissä. Lopputuotos esitetään lopullisena analyysinä ilman mainittuja rajoituksia tai skenaarioita, joissa logiikka ei pätisi.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_247927c98b0c46f8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. Rebuttals that provide counter-data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii retorisia ohituksia, joissa vastaväite mainitaan mutta sivuutetaan ilman dataa. Tekstistä ei löytynyt lauserakenteita, kuten 'vaikka X on totta, sillä ei ole väliä', jotka täyttäisivät tämän ehdon.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [TRUE]:**
  > *Mitigating exception found: Teksti ei sisällä retorisia ohituksia, joissa mainittu vastaväite sivuutettaisiin ilman vasta-argumentointia tai dataa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_32ee0cac79ad098e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Mitigating exception found: Tämä on pahe-sääntö (vice rule). Sääntö etsii universaaleja termejä, kuten 'aina' tai 'joka tapauksessa', joilla yleistetään kausaaliväite. Lähdeteksti ei sisällä näitä spesifejä syntaktisia ankkureita.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö. Sääntö etsii universaaleja termejä, kuten 'aina', jotka yleistävät kausaaliväitteen. Kohdeteksti ei sisällä tällaisia termejä, joten sääntöä ei rikota.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_93568eab47234542` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept mathematical axioms. STEP 1 (Syntactic Anchor): Find dogmatic certainty markers (e.g., 'is self-evident', 'needs no proof', 'as we all know', 'beyond question'). STEP 2 (Bounding Box): Scan the sentence. If it explicitly blocks further empirical testing or questioning. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Presence detected: The phrase "ainoa tapa" (the only way) is a dogmatic certainty marker. It presents a single solution as absolute, implicitly blocking further questioning or empirical testing of alternative strategies.. Exceptions audit: Tekstistä ei löytynyt dogmaattisen varmuuden ilmauksia, kuten 'on itsestään selvää' tai 'ei kaipaa todisteita', jotka estäisivät empiirisen testaamisen.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt dogmaattisia varmuuden ilmauksia, kuten 'on itsestään selvää' tai 'ei kaipaa todisteita', jotka eksplisiittisesti estäisivät jatkotutkimuksen tai kyseenalaistamisen. Vaikka tekstissä on vahvoja johtopäätöksiä, ne eivät täytä säännön vaatimaa ehtoa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_7cdd3652e248e6a9` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find tension markers between metrics and goals (e.g., 'this metric is flawed because', 'we need to ensure this actually works'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly questions the reliability of a proxy metric in relation to the ultimate qualitative goal. Do not accept simple metric tracking.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei missään vaiheessa kyseenalaista Sitran megatrendien luotettavuutta tai sitä, ovatko ne hyviä mittareita tulevaisuuden tavoitteille. Sen sijaan käyttäjä hyväksyy ne annettuina ja työskentelee niiden pohjalta, jopa rakentaen niiden päälle uuden 'supermegatrendit'-käsitteen.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [TRUE]:**
  > *Mitigating exception found: A scan of the user's prompts in the chat log shows no instances where the user questions the reliability of a proxy metric or highlights a tension between a metric and a qualitative goal. The user's focus is on synthesis and structuring of information, not on critiquing its validity.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_82e8242331deddab` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a factual claim. STEP 2: Check for qualifying terms (e.g., 'indicates', 'suggests', 'is correlated'). EXTRACTION CONDITION: present AND absolute markers (e.g., 'proves', 'always') are strictly absent in the same sentence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Lause "Sitran megatrendien kehitys ... osoittaa fundamentaalisen siirtymän" sisältää kvalifioivan termin 'osoittaa' (indicates/shows). Lauseessa ei ole samanaikaisesti absoluuttisia merkkejä, kuten 'todistaa' tai 'aina', joten se täyttää säännön ehdot.*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *Säännön ehto ei täyty. Teksti on sävyltään pääosin absoluuttinen. Vaikka lause "Sitran megatrendien kehitys... osoittaa fundamentaalisen siirtymän" sisältää potentiaalisesti kvalifioivan termin 'osoittaa', lauseen konteksti ja koko tekstin vakuuttava sävy eivät tee siitä varauksellista. Tekstistä ei löydy lausetta, joka olisi selkeästi varauksellinen ja samalla vapaa absoluuttisista ilmauksista.*

---

### Atom-ID: `tda_ade6cbd3f956fa67` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. Do not evaluate 'collaboration' or 'politeness'. STEP 1 (Syntactic Anchor): Find delegation verbs ('päätä', 'valitse', 'kumpi', 'decide', 'choose'). STEP 2 (Bounding Box): Scan the prompt. EXTRACTION CONDITION: the user explicitly asks the AI to make a final subjective choice or decision on their behalf.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Presence detected: Sääntö ei täyty, koska käyttäjä ei missään vaiheessa delegoi subjektiivista päätöksentekoa tekoälylle. Käyttäjä pyytää koostamaan ja muotoilemaan tietoa, mutta ei pyydä tekoälyä valitsemaan tai päättämään puolestaan.. Exceptions audit: The user never delegates a subjective choice or decision to the AI using verbs like 'päätä' or 'valitse'. The user maintains decision-making authority throughout the process.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii delegointiverbejä ('päätä', 'valitse'). Käyttäjän kehotteista ei löydy yhtäkään komentoa, jossa päätösvalta siirrettäisiin subjektiivisesti tekoälylle. Käyttäjä antaa selkeitä ohjeita.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b8c1d460ccfd9ae4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find listing conjunctions (e.g., 'and', 'also', 'in addition'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: two major domain concepts are placed side-by-side without a relational verb connecting them. Do not accept sentences that explicitly define the relationship between the concepts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen (vice rule), joka etsii virhettä. Tekstistä ei löytynyt kohtia, joissa kaksi merkittävää käsitettä olisi vain listattu rinnakkain ilman, että niiden välistä suhdetta olisi määritelty. Esimerkiksi lauseessa "...nähdä kestävyys ja autonomia uusina kilpailutekijöinä" verbi "nähdä" määrittelee käsitteiden välisen suhteen. Koska rikkomusta ei löytynyt, sääntö on täytetty.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [TRUE]:**
  > *Presence detected: Teksti listaa rinnakkain kaksi käsitettä, "kriisejä" ja "systeemisiä murtumia", ilman että niiden välistä suhdetta määritellään relaatioverbillä, mikä vastaa säännön ehtoja virheen löytymisestä.. Exceptions audit: Sääntö etsii lauseita, joissa kaksi käsitettä on lueteltu ilman niitä yhdistävää relaatiota. Lähdetekstissä kaikki 'ja'-konjunktiolla yhdistetyt käsitteet ovat osa lauserakennetta, jossa verbi tai muu määre (esim. 'kaltaiset säädökset', 'panostus') selkeästi määrittelee niiden välisen suhteen. Virhettä ei siis esiinny.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_55dfd9cb0adec620` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [FALSE]:**
  > *No presence of target concept detected: Tämä on pahesääntö, joka etsii tunnistettuja riskejä, joille ei esitetä lievennystoimia. Lopullisessa tuotoksessa (`product_text`) käytetty taulukkorakenne esittää systemaattisesti jokaiselle tunnistetulle kaupalliselle vaikutukselle (riski) vastaavan strategisen toimenpiteen (lievennys). Esimerkiksi "maineriskin" vastatoimena on "Kehitetään ja käytetään teknologiaa eetisesti ja läpinäkyvästi". Pahetta ei esiinny.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [TRUE]:**
  > *Presence detected: Tämä on pahesääntö. Lopputuotteessa tunnistetut riskit (esim. "Luotamuskriisi", "maineriski") on kaikki yhdistetty strategisiin toimenpiteisiin niiden lieventämiseksi. Ei löydy tunnistettua riskiä ilman vastaavaa toimenpide-ehdotusta.. Exceptions audit: This is a vice rule. The product text consistently identifies risks ('Kaupalliset Vaikutukset') and then provides corresponding mitigation actions ('Strategiset Toimenpiteet'). No identified risk is left without a proposed mitigation.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_8b65277ca32d4c0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'depth' subjectively. STEP 1 (Syntactic Anchor): Find absolute conclusion words (e.g., 'clearly', 'obviously', 'must be', 'selvästi'). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: the conclusion is presented without a multi-step logical deduction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Mitigating exception found: Sääntö on käänteinen (vice rule). Lause esittää absoluuttisen johtopäätöksen ("Vain kestävät liiketoimintamallit saavat... pääomaa") ilman, että sitä edeltävässä kappaleessa olisi esitetty riittävän kattavaa ja aukotonta loogista päättelyketjua. Vaikka sääntelypainetta käsitellään, hyppäys "vain"-sanan käyttöön on perustelematon oikaisu.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *No presence of target concept detected: This is an inverse rule. The document's conclusions, such as 'Muutos... on peruuttamaton', are presented at the end of a logical chain of reasoning that starts with Sitra's reports, synthesizes them into supermegatrends, and details their impacts. The conclusions are not presented as leaps of faith but as summaries of the preceding analysis.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0eb49f05fdd6deb9` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept generic errors; must be an absolute fabrication (LLM09 Overreliance). STEP 1 (Syntactic Anchor): Find a factual claim (dates, names, specific data points). STEP 2 (Search Verification): Verify the claim's logic. EXTRACTION CONDITION: the claim is demonstrably false or fabricated but presented with absolute certainty.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [FALSE]:**
  > *No presence of target concept detected: Tämä on pahesääntö, joka etsii todisteita tekoälyn tuottamien väärien tietojen hyväksymisestä. Lähdeaineisto ei sisällä tällaisia tapauksia. Käyttäjä päinvastoin tunnistaa virheen lähtöaineistossa ("yksi raportti oli annettu kahteen kertaan") ja korjaa aktiivisesti tekoälyn tuotoksia, mikä osoittaa, ettei hän luota sokeasti annettuihin tietoihin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [TRUE]:**
  > *Presence detected: Tämä on pahe-sääntö (vice rule). Vaikka käyttäjä mainitsee reflektiossa virheen lähtötiedoissa, tekoälyn tuottamassa sisällössä ei ole havaittavissa tai todistettavissa olevaa absoluuttista, keksittyä väitettä annettujen lähteiden perusteella. Ilman ulkoista tietoa Sitran raporteista, fabriikointia ei voida todentaa.. Exceptions audit: This is a vice rule. I cannot find any claims in the provided texts that are demonstrably false or fabricated. The user's reflection mentions an error in the initial source data provided to them, not a fabrication by the AI.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_4fa47fd622e62e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision. Do not accept generic references to 'standards' without naming them.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Mitigating exception found: Teksti viittaa ulkoisiin kehyksiin (CSRD, EU-taksonomia), mutta se ei viittaa tiettyyn alaperiaatteeseen tai lausekkeeseen perustellakseen päätöstä säännön vaatimalla tavalla.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää viittausta tiettyyn ulkoiseen viitekehykseen ja sen ala-periaatteeseen. Lähdeteksti (chat-lokin 'ai:'-osiot) ei sisällä mitään viittauksia ARMA- tai ISO-standardeihin tai niiden osiin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_aa54c6b40e9c4160` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph containing statistical or factual reporting. STEP 2: Count the first-person pronouns ('I', 'we') or explicit self-reflective verbs ('assume', 'interpret'). EXTRACTION CONDITION: the count is exactly 0. NEGATIVE CONDITION (RETURN NULL IF MET): greater than 0.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Tekstin kappaleet on kirjoitettu persoonattomalla ja faktapohjaiselta vaikuttavalla tyylillä. Esimerkiksi ensimmäinen kappale "Evoluutio Konfliktiin" -otsikon alla kuvaa kehityskulkua ilman ensimmäisen persoonan pronomineja ('minä', 'me') tai itsetutkiskelevia verbejä ('oletan', 'tulkitsen'), mikä täyttää säännön ehdon.*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *Säännön poimintaehto (ensimmäisen persoonan pronominien määrä on tasan 0) ei täyty. Tekstin lopussa esiintyy sana "Yrityksemme", joka on omistusmuoto pronominista 'me'. Koska pronominien määrä on suurempi kuin 0, negatiivinen ehto täyttyy ja poimintaa ei tehdä.*

---

### Atom-ID: `tda_f142c3fa1d08cc2d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: EXTRACTION CONDITION: the user explicitly restricts the AI to the provided data and demands exact evidence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [TRUE]:**
  > *Mitigating exception found: The user prompts do not contain any explicit commands to extract verbatim quotes or to strictly limit the output to the source text without synthesis or invention. The condition is not met.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteista ei löytynyt yhtään säännössä määriteltyä ankkuria ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain'). Käyttäjä ei rajoita tekoälyä eksplisiittisesti vain annettuun dataan tai vaadi tarkkoja lainauksia.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_31ae4494272845fe` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. Do not evaluate the quality of the bridging rule.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77c3cb441dd6474abc3422f3a64c89f7) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii lauseita, joissa datan ja väitteen välinen siltasääntö (warrant) on eksplisiittisesti ilmaistu yleisenä periaatteena. Tekstistä ei löytynyt tällaisia yleisiä periaatteita ilmaisevia rakenteita.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_a68fc75f7d3b457782a1fa435ee8b725) - [TRUE]:**
  > *Mitigating exception found: Teksti ei sisällä lauseita, joissa datan ja väitteen välinen siltaussääntö (warrant) olisi eksplisiittisesti muotoiltu yleiseksi periaatteeksi. Yhteydet esitetään suorina seurauksina.  [5. VALIDATION DECISION: PASS]*

---

