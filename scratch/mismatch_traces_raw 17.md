# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 91.94 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.8305
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.0806
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 15 kpl
- **PASSED -> FAILED:** 8
- **FAILED -> PASSED:** 7
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_8d049ce6e39a465c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data.
<syntactic_constraint>
  <anchors>
    <anchor>however</anchor>
    <anchor>might seem</anchor>
    <anchor>initially</anchor>
    <anchor>kuitenkin</anchor>
    <anchor>aluksi</anchor>
    <anchor>vaikuttaisi</anchor>
  </anchors>
  <extraction_condition>
    Check if transitional doubt from one of the words in the <anchors> block is immediately dismissed (within the same paragraph) to reaffirm the initial automatic conclusion without introducing any new empirical proof, metrics, or citations.
  </extraction_condition>
  <ambiguity_protocol>
    If the doubt anchors from <anchors> are absent, or if the doubt leads to a new productive hypothesis, or if it is supported by new empirical evidence, you MUST return JSON null.
  </ambiguity_protocol>
</syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen virhesääntö. Teksti ei riko sääntöä. En löytänyt tekstistä kohtaa, jossa esitetty epäilys (esim. ankkurisanalla 'kuitenkin' tai 'vaikuttaisi') olisi välittömästi kumottu ilman uutta todistusaineistoa alkuperäisen johtopäätöksen vahvistamiseksi. Tekoäly käyttää vastaväitteitä rakentavasti.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [TRUE]:**
  > *Mitigating exception found: Teksti myöntää riskin olemassaolon, mutta välittömästi sen jälkeen kumoaa sen merkityksen käyttäjän kontekstissa ilman uutta empiiristä todistusaineistoa. Tämä vahvistaa alkuperäistä johtopäätöstä sivuuttamalla esitetyn epäilyksen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b8c1d460ccfd9ae4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find listing conjunctions (e.g., 'and', 'also', 'in addition'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: two major domain concepts are placed side-by-side without a relational verb connecting them. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept sentences that explicitly define the relationship between the concepts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Presence detected: This is a vice rule. A violation was found. The AI lists several major domain concepts ('Keskustelut', 'ryhmätyöt', 'konfliktit', 'sosiaalinen oppiminen') side-by-side under a heading without using any relational verbs to connect them or explain their relationship to one another. This fits the extraction condition of placing concepts together without a defined relationship.. Exceptions audit: Tämä on käänteinen sääntö (virheen etsintä). Tekstiä analysoitaessa ei löytynyt kohtia, joissa kaksi merkittävää käsitettä olisi asetettu rinnakkain ilman niitä yhdistävää relaatiota tai verbiä. Tekoäly yhdistää käsitteet, kuten 'yrittäjyys ja markkinointi', johdonmukaisesti lauseyhteyteen, joka määrittelee niiden suhteen (esim. 'opetat yrittäjyyttä ja markkinointia'). Virhettä ei siis esiinny.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen (vice rule). Tekstistä ei löytynyt esimerkkiä, jossa kaksi merkittävää käsitettä olisi yhdistetty konjunktiolla ilman, että niiden välistä suhdetta määriteltäisiin selkeästi joko verbillä tai lauserakenteella. Tekoäly on tässä suhteessa kielellisesti tarkka.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_58cbd7271f491351` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing absolute declarations (e.g., 'proves unequivocally', 'the model dictates', 'undeniable', 'certainty') into List A. Extract exact quotes containing mitigating words or constraints (e.g., 'however', 'potential limit', 'constraint', 'lens', 'maybe') into List B.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Mitigating exception found: Tämä on käänteinen sääntö (vice rule). Tekoäly esittää absoluuttisen, kannustavan arvion käyttäjän asemasta ('sinä olet oikeasti etulyöntiasemassa') ilman, että samassa kappaleessa on tasapainottavia tai lieventäviä ilmauksia. Vaikka lause on positiivinen, se täyttää säännön määritelmän tasapainottamattomasta arviosta ja on siten sääntörikkomus.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö. Teksti ei sisällä absoluuttisia, ehdottomia julistuksia. Sen sijaan se käyttää jatkuvasti lieventäviä ja rajoittavia sanoja, kuten "mutta", "voi" ja "osittain", osoittaen, että esitettyjä malleja ja väitteitä tarkastellaan kriittisesti ja niiden rajoitteet tunnistetaan. Virhettä ei siis tapahdu.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_cee9db6717cdafb7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Locate a risk assessment or 'pre-mortem' structure. STEP 2: Find explicit dismantling of a risk using a verifiable external citation or empirical data. EXTRACTION CONDITION: both the risk and the empirical counter-data are found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [FALSE]:**
  > *The text identifies risks, for instance under the heading 'Riski: ajattelun heikkeneminen ja riippuvuus', and cites an external source ('Tecnológico de Monterrey Observatory'). However, the citation is used to confirm and detail the risk, not to dismantle it with counter-data. The dismantling of the risk's implications is done through subsequent logical argumentation by the AI, not by the citation itself.*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [TRUE]:**
  > *Sääntö täyttyy. Teksti sisältää riskinarvioinnin, jossa riski ('ajattelun heikkeneminen ja riippuvuus') puretaan käyttämällä ulkoista viitettä ('Tecnológico de Monterrey Observatory') ja kontekstualisoimalla riski ('riski syntyy ilman ohjausta ei tekoälystä itsestään').*

---

### Atom-ID: `tda_9a0fa3967ebb2497` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate creativity. STEP 1 (Syntactic Anchor): Find counterfactual markers ('EXTRACTION CONDITION: X had not', 'would have been'). STEP 2: NEGATIVE CONDITION (RETURN NULL IF MET): the text actively simulates an alternate timeline (Pearl's Rung 3) to explicitly prove necessary causation. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Mitigating exception found: Teksti ei sisällä säännön määrittelemää kontrafaktuaalista päättelyä, jossa simuloidaan mennyttä vaihtoehtoista aikajanaa. Se käyttää tulevaisuuteen suuntautuvia konditionaaleja.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä kontrafaktuaalista päättelyä menneisyydestä säännön määrittelemällä tavalla (esim. "jos X ei olisi tapahtunut, Y olisi ollut tulos"). Se käyttää ehtolauseita tulevaisuuden skenaarioiden pohtimiseen, mutta ei simuloi vaihtoehtoisia menneisyyksiä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_f142c3fa1d08cc2d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: EXTRACTION CONDITION: the user explicitly restricts the AI to the provided data and demands exact evidence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää tekoälyä perustelemaan väitteitään ja etsimään tutkimusviitteitä, mikä on semanttisesti linjassa säännön kanssa. Kuitenkaan yksikään vaadituista syntaktisista ankkureista ('poimi suoraan', 'tarkka lainaus', 'perustuen vain') ei esiinny käyttäjän kehotteissa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä pyytää tekoälyä etsimään tutkimusviitteitä, mutta ei käytä mitään säännön määrittelemistä ankkureista, jotka rajoittaisivat tekoälyn toimintaa vain tiettyyn dataan tai vaatisivat tarkkoja lainauksia.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b65277ca32d4c0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'depth' subjectively. STEP 1 (Syntactic Anchor): Find absolute conclusion words (e.g., 'clearly', 'obviously', 'must be', 'selvästi'). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: the conclusion is presented without a multi-step logical deduction. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen virhesääntö. Teksti ei riko sääntöä. Vaikka tekoäly käyttää vahvoja väittämiä, se tyypillisesti tarjoaa niille loogisen perustelun tai purkaa ne osiin (esim. "Tämä tarkoittaa:", "Todellisuus:"). En löytänyt selvää esimerkkiä absoluuttisesta johtopäätöksestä ilman monivaiheista loogista päättelyä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [TRUE]:**
  > *Mitigating exception found: Teksti esittää absoluuttisen johtopäätöksen esihenkilön ajatuksista ilman minkäänlaista vaiheittaista loogista päättelyä tai todisteita. Väite perustuu pelkkään stereotypiaan roolista, ei esitettyyn dataan.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2590fb7ecb6379e7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate nuance. STEP 1 (Syntactic Anchor): Find absolute causal words ('only reason', 'entirely due to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text attributes a highly complex outcome to a single cause without acknowledging any other potential factors. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [FALSE]:**
  > *No presence of target concept detected: Tämä on pahesääntö. Teksti ei riko sääntöä, koska se ei käytä absoluuttisia kausaalisia termejä tai selitä monimutkaisia ilmiöitä yhdellä ainoalla syyllä. Päinvastoin, se erittelee useita vaikuttavia tekijöitä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [TRUE]:**
  > *Presence detected: Tämä on pahesääntö. Teksti ei riko sääntöä, koska se ei käytä absoluuttisia kausaalisia termejä tai selitä monimutkaisia ilmiöitä yhdellä ainoalla syyllä. Päinvastoin, se erittelee useita vaikuttavia tekijöitä.. Exceptions audit: Tekstissä ei esiinny pahetta. Monimutkaisia ilmiöitä ei selitetä yhdellä ainoalla syyllä käyttäen absoluuttisia ilmaisuja, kuten 'ainoa syy' tai 'johtuu täysin'.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d5d27ea4cfe44c44` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate engagement quality. STEP 1 (Syntactic Anchor): Find an explicit counter-argument or risk raised in the text (e.g., 'Despite the risk', 'Opponents argue', 'Vaikka'). STEP 2 (Bounding Box): Scan the subsequent sentences. EXTRACTION CONDITION: the counter-argument is stated but not logically dismantled with data. NEGATIVE CONDITION (RETURN NULL IF MET): it is dismantled step-by-step. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen virhesääntö. Teksti ei riko sääntöä. Tekoäly nimenomaisesti listaa vastaväitteitä (esim. "huolestuttavia tarinoita") ja purkaa ne systemaattisesti osiin sen sijaan, että vain toteaisi ja sivuuttaisi ne. Negatiivinen ehto (vastaväitteen purkaminen askel askeleelta) täyttyy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [TRUE]:**
  > *Mitigating exception found: Teksti käsittelee vastaväitettä opettajan arvon laskusta, mutta sen purkaminen ei perustu dataan. Sen sijaan se torjutaan esittämällä affirmaatioita, jotka toistavat keskustelun pääteesiä, mikä ei ole looginen, dataan perustuva kumoaminen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0b0cc9976fb0d7d6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'superficial' subjectively. STEP 1 (Syntactic Anchor): Find terms indicating a manual or ad-hoc check (e.g. 'glanced at', 'looks okay', 'basic check'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the verification relies entirely on human intuition rather than a systemic protocol (like OWASP). TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Mitigating exception found: Tämä on pahesääntö. Tekoäly ei kuvaa omaa tarkistusprosessiaan ylimalkaiseksi tai intuitioon perustuvaksi. Vaikka se käyttää ilmaisua 'näyttää hyvältä', se tekee sen kontekstissa, jossa opettajan tulee erottaa aito osaaminen pinnallisesta tuotoksesta, ei kuvatakseen omaa toimintaansa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei ole viitteitä siitä, että tekoäly itse suorittaisi ad-hoc-tarkistuksia. Vaikka se käyttää ilmaisua "miltä näyttää hyvältä", se liittyy opettajan roolin kuvailuun, ei järjestelmän omaan toimintaan.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fbd90f9c0f2247ed` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit counterargument markers (e.g., 'critics argue', 'opposing view', 'counterargument', 'on the other hand'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the counterargument marker AND ALSO contains physical citation markers (e.g., 'et al', '[1]', '(', 'published in') AND empirical measurement vocabulary (e.g., 'data', 'showed', 'measured') -> ACCEPT. If it lacks citations or measurement tokens -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'strength', 'steel-manning', or whether the argument is successfully 'dismantled'. Evaluate only physical token presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt kohtaa, joka täyttäisi kaikki säännön ehdot samanaikaisesti. Vaikka tekoäly esittää tutkimusviitteitä, se ei tee sitä eksplisiittisen vasta-argumentin (esim. 'kriitikot väittävät') yhteydessä, joka sisältäisi myös empiirisen mittaamisen sanastoa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [TRUE]:**
  > *Presence detected: The AI presents a risk ('kriittisen ajattelun heikkeneminen'), which acts as a counterargument to a purely positive view of AI. This point is explicitly supported by a citation ('Tecnológico de Monterrey Observatory'), fulfilling the rule's conditions.. Exceptions audit: Vaikka tekoäly esittää tutkimusviitteitä, se ei tee sitä säännön vaatimassa kontekstissa, jossa esiteltäisiin vastustajan argumentti lähteineen. Sen sijaan tekoäly käyttää tutkimuksia oman, aiemmin esitetyn ja vivahteikkaan näkemyksensä tukemiseen ja tarkentamiseen. Säännön vaatimaa rakennetta (vasta-argumentin esittely + lähde + empiirinen data samassa kappaleessa) ei löydy.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_21d7952c2bf6393c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'watertightness'. STEP 1: Find mathematical or structural causal terms ('do-calculus', 'directed acyclic graph', 'structural equation', 'formal model'). STEP 2: EXTRACTION CONDITION: the text explicitly uses a formal model or strict structural logic to map the causality. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Mitigating exception found: Tekstistä ei löydy formaaleihin kausaalimalleihin viittaavia termejä, kuten 'rakenneyhtälömalli' tai 'suunnattu syklinen graafi'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: The text does not contain any terms related to formal causal modeling such as 'do-calculus', 'structural equation model', or their Finnish equivalents. The reasoning is based on argumentation, not formal models.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_44fd8d7101a84a48` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate completeness. STEP 1 (Syntactic Anchor): Find a primary proposal or argument. STEP 2 (Bounding Box): Scan the entire document. EXTRACTION CONDITION: alternative hypotheses or competing theories are completely absent from the text. NEGATIVE CONDITION (RETURN NULL IF MET): at least one competing alternative is analyzed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen virhesääntö. Teksti ei riko sääntöä. Tekoäly esittää jatkuvasti vastakkaisia hypoteeseja (esim. "huolestuttavia tarinoita") ja analysoi niitä sen sijaan, että sivuuttaisi ne. Negatiivinen ehto (vähintään yhden kilpailevan vaihtoehdon analysointi) täyttyy selvästi.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [TRUE]:**
  > *Mitigating exception found: Teksti esittää yhden vahvan, pääasiallisen narratiivin opettajan roolin muutoksesta, ja kaikki esitetyt riskit tai huolet käsitellään tämän pääargumentin vahvistamisen kautta, ei aitoina kilpailevina hypoteeseina.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d8bdf091d22d4412` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE: IDENTIFY the baseline presence of explicit partial consensus among agents. Look for lexical markers like 'mostly agree', 'general consensus', or 'aligns' in the native language. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Mitigating exception found: The rule looks for markers of partial consensus or alignment. In the context of discussing research findings, the AI states that a finding 'Täsmälleen tukee sinun ajatusta...' ('Exactly supports your idea...'). The word 'tukee' (supports) is a strong semantic equivalent for 'aligns' in this context, indicating that an external source (research) and an agent's (user's) idea are in consensus.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt kielellisiä markkereita, jotka viittaisivat osittaiseen konsensukseen (esim. 'pääosin samaa mieltä', 'yleinen konsensus'). Tekoäly esittää näkemyksensä asiantuntijan auktoriteetilla, ei ryhmän yhteisenä kantana.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_eb46c2f21b7f4c66` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): LOCATE a single instance where the synthesis includes actively contradictory statements that are left completely unresolved. Look for lexical markers of conflict (e.g., 'however', 'contradicts') in the native language. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_7bf3ddc4ad2043918f087e2d67019602) - [TRUE]:**
  > *Mitigating exception found: This is a vice rule looking for unresolved contradictions. A clear contradiction was found. The AI first states its percentage figures are not based on data ('eivät perustu... tarkkaan dataan'). Later, it presents a list of fabricated 'reliable studies' with very specific data (e.g., '88 %'). This later action directly contradicts the initial claim of not having precise data, and the contradiction is left unresolved. The extracted quote is the first part of this contradiction.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_0dfb0101e4714c58bb0d4b430b4b81e3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä etsittiin ratkaisemattomia ristiriitoja. Vaikka tekoäly käyttää vastakkainasettelua ilmaisevia sanoja kuten 'mutta', se tekee niin johdonmukaisesti esitelläkseen vastakkaisen näkökulman, rajoituksen tai ehdon, jonka se välittömästi selittää ja ratkaisee. Aktiivisia, ratkaisemattomia ristiriitoja ei löytynyt.  [5. VALIDATION DECISION: PASS]*

---

