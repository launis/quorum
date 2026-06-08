# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 185
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 83.24 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.6484
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.6487
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1676
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 31 kpl
- **PASSED -> FAILED:** 18
- **FAILED -> PASSED:** 13
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_9da28945325e4486a8b4941c561299fa` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find formal citations ('according to the methodology of', 'based on the study by'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the logical rule is explicitly backed by a verifiable external methodology or study. NEGATIVE CONDITION (RETURN NULL IF MET): it's a vague reference ('research shows'). Vague references to 'studies' or 'science'. <disambiguation>
  Regulatory framework references count as formal citations ONLY if a 
  specific sub-article, clause, or numbered principle is cited (e.g., 
  "Article 29b(2)", "ISO 27001 §6.1.2"). Generic regulatory mentions 
  without sub-clause specificity DO NOT satisfy methodology link, benchmark, 
  formal citation, or security standard extraction conditions.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Presence detected: Lauseessa 'Ehdotus perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon' käytetään 'perustuu' (based on) -ankkuria, joka linkittää ehdotuksen selkeästi ulkoiseen, todennettavissa olevaan tutkimustietoon (Työterveyslaitos ja Stanfordin yliopisto). Tämä täyttää muodollisen viittauksen ehdon.. Exceptions audit: Sääntö edellyttää muodollista viittausta, joka sisältää metodologian tai tutkimuksen yksityiskohdat. Tekstissä mainitaan 'Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon', mikä on liian yleinen viittaus eikä täytä 'vague reference' -negatiivista ehtoa. Se ei sisällä metodologian tai tutkimuksen yksityiskohtia, kuten sääntö vaatii.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Sääntö vaatii, että looginen sääntö on nimenomaisesti tuettu todennettavissa olevalla ulkoisella metodologialla tai tutkimuksella. Vaikka 'perustuu' on syntaktinen ankkuri, 'Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon' on liian yleinen viittaus, eikä se täytä 'verifiable external methodology or study' -ehtoa. Negatiivinen ehto ('vague reference') täyttyy, joten palautetaan null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bd90e5a66c5d433a9ed650f295132625` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'spurious'. STEP 1 (Syntactic Anchor): Find causal words (e.g. 'causes', 'because'). STEP 2 (Bounding Box): Scan the same sentence. EXTRACTION CONDITION: the causal claim is backed ONLY by a statistical correlation or simultaneous occurrence without any physical mechanism.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt kausaalisia väitteitä, jotka perustuisivat *ainoastaan* tilastolliseen korrelaatioon tai samanaikaiseen esiintymiseen ilman fyysistä mekanismia. Esimerkiksi 'Kun siirryimme laajaan etätyöhön, toimitilakulumme putosivat 30 prosenttia' sisältää implisiittisen mekanismin (vähemmän ihmisiä toimistolla = vähemmän tilantarvetta).  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Mitigating exception found: Lauseessa esitetään kausaalinen väite ('johtaneet'), mutta fyysistä mekanismia, jolla 'epäviralliset käytännöt' johtavat mainittuihin seurauksiin, ei kuvata. Tämä on rikkomus, koska väite perustuu vain korrelaatioon tai samanaikaiseen esiintymiseen ilman mekanismia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b7dfe23403db4db5b92a29a8bda9957c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find listing conjunctions (e.g., 'and', 'also', 'in addition'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: two major domain concepts are placed side-by-side without a relational verb connecting them. Do not accept sentences that explicitly define the relationship between the concepts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Presence detected: Lauseessa 'Selvitys' ja 'ehdotus' ovat kaksi merkittävää toimialakonseptia, jotka on asetettu rinnakkain 'ja'-konjunktiolla ilman niitä yhdistävää relationaalista verbiä, mikä on säännön rikkomus.. Exceptions audit: Tekstistä ei löytynyt kahta merkittävää toimialakonseptia, jotka olisi asetettu rinnakkain ilman niitä yhdistävää relationaalista verbiä. Kaikki listaukset ovat joko osia suuremmasta kokonaisuudesta tai niillä on selkeä relationaalinen verbi.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei ole lauseita, jotka asettaisivat kaksi suurta toimialakäsitettä rinnakkain ilman niitä yhdistävää relationaalista verbiä. Kaikki mainitut käsitteet on liitetty toisiinsa selkeillä suhdeverbeillä tai kontekstilla.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_8275735bde0244e2bdbf3ab915838d59` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit optimization commands for proxy metrics (e.g., 'maximize the score', 'increase the word count', 'make it sound professional'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user demands optimization of a surface metric without linking it to a qualitative real-world outcome. Do not accept if the metric is explicitly tied back to a measure of effectiveness.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä antaa eksplisiittisen optimointikäskyn pintamittarille ('Yksi sivu riittää.') ilman, että sitä linkitetään laadulliseen reaalimaailman lopputulokseen. Vaikka se voi implikoida tiiviyttä, sääntö edellyttää nimenomaan linkityksen puuttumista.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä pyytää 'yhden sivun yhteenvetoa' ja 'yksi sivu riittää', jotka ovat pinnallisia mittareita. Kuitenkin nämä pyynnöt on linkitetty laadullisiin tavoitteisiin, kuten 'maksimoida työhyvinvointi, kulttuurin ylläpito, innovointi ja talous' tai muistion tapauksessa implisiittisesti johtoryhmälle sopivaan tiiviyteen. Siksi ne eivät täytä ehtoa, jonka mukaan optimointi olisi 'ilman linkitystä laadulliseen todelliseen lopputulokseen'.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_83c3a1f41fb94c8d802a60e00ad2550f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'proactivity' subjectively. STEP 1 (Syntactic Anchor): Find temporal reactive markers (e.g. 'after the failure', 'once identified', 'we fixed'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: security measures are ONLY described as post-incident responses without any pre-incident checks.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: En löytänyt tekstistä turvatoimia, jotka olisi kuvattu *ainoastaan* reaktiivisina toimenpiteinä (esim. 'epäonnistumisen jälkeen'). Ehdotukset ovat luonteeltaan ennakoivia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Presence detected: Tekoäly kuvaa, kuinka sen aiempi ehdotus oli puutteellinen ja se on nyt 'korjattu' kritiikin perusteella. Tämä osoittaa, että toimenpiteet ovat reaktiivisia aiemmin tunnistettuihin ongelmiin, eivät ennakoivia turvatoimia.. Exceptions audit: Tekstissä ei kuvata turvatoimenpiteitä ainoastaan jälkikäteen reagoivina toimenpiteinä. Kyseessä on politiikkaehdotus, joka on luonteeltaan ennakoiva.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6ecd649b48c24e68824e27e30ed8a63e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. Do not accept generic requests ('analysoi hyvin'). STEP 1 (Syntactic Anchor): Find methodology anchors ('käytä menetelmää', 'mallin mukaisesti', 'viitekehys', 'SWOT', 'PESTEL', 'teoria', 'framework'). STEP 2: EXTRACTION CONDITION: the user explicitly names a method or analytical framework the AI MUST follow.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteista ei löytynyt nimenomaisia mainintoja menetelmistä tai analyyttisistä viitekehyksistä, joita tekoälyn tulisi noudattaa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Presence detected: Käyttäjä nimeää eksplisiittisesti metodin ('käyt dialogia itsesi kanssa kolmesta eri näkökulmasta käsin'), jota tekoälyn tulee noudattaa.. Exceptions audit: Käyttäjän kehotteista ei löytynyt fyysisiä ankkureita, jotka nimeäisivät eksplisiittisesti tietyn menetelmän tai analyyttisen viitekehyksen, jota tekoälyn tulisi noudattaa ('käytä menetelmää', 'mallin mukaisesti', 'SWOT').  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_45885ef98e7d481084b4378d5b3f2f3f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept appeals to authority. STEP 1 (Syntactic Anchor): Find heuristic or dismissive phrases (e.g. 'typically', 'usually', 'it is known', 'obviously'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the phrase is used to justify a decision WITHOUT citing a specific dataset, numerical weight, or verifiable rule. NEGATIVE CONDITION (RETURN NULL IF MET): a specific source is cited.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Lauseessa käytetään heuristista ilmausta 'Suosituksena on malli' perustelemaan päätöstä ilman, että siinä tai sen välittömässä kontekstissa viitataan spesifiseen data-aineistoon, numeeriseen painoarvoon tai todennettavissa olevaan sääntöön. Yleinen viittaus tutkimustietoon ei ole riittävän spesifinen.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt heuristisia tai vähätteleviä fraaseja, joita olisi käytetty päätöksen perustelemiseen ilman spesifistä datajoukkoa, numeerista painoarvoa tai todennettavissa olevaa sääntöä.  [5. VALIDATION DECISION: FAIL]*

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
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Teksti esittelee kaksi vastakkaista näkökulmaa: etätyön luonnollisuuden ja sen nykyisten käytäntöjen aiheuttamat ongelmat. Ehdotettu hybridityöpolitiikka toimii näiden kahden vastakkaisen tilan synteesinä, pyrkien ratkaisemaan ongelmat ja maksimoimaan hyödyt.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: [SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b899e72085ea4d488a6e6c22a34e2d75` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'superficial' subjectively. STEP 1 (Syntactic Anchor): Find terms indicating a manual or ad-hoc check (e.g. 'glanced at', 'looks okay', 'basic check'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the verification relies entirely on human intuition rather than a systemic protocol (like OWASP). NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei kuvata tarkistusta, joka perustuisi kokonaan inhimilliseen intuitioon ('vilkaisi', 'näyttää hyvältä'). Päinvastoin, ehdotuksessa siirrytään 'tulosten johtamiseen' ja 'selkeisiin tavoitemittareihin'.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Presence detected: Tekoäly nimenomaisesti kiistää luottavansa 'mututuntumaan' (intuitioon) ja väittää perustavansa suositukset laajaan tutkimustietoon, mikä falsifioi ehdon, että tarkistus perustuisi pelkästään intuitioon.. Exceptions audit: Tekstissä ei kuvata tarkistusprosesseja, jotka perustuisivat kokonaan inhimilliseen intuitioon tai ad hoc -tarkistuksiin. Sen sijaan mainitaan 'selkeät tavoitemittarit' ja 'tulosten johtaminen', mikä viittaa systemaattiseen lähestymistapaan.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ae5dd6ac930544f4abd77d3438c59ddd` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept post-decision doubt. STEP 1 (Syntactic Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the alternatives are explicitly compared and evaluated BEFORE the final decision is stated. NEGATIVE CONDITION (RETURN NULL IF MET): evaluated after.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä kysyy vaihtoehdoista ('yksi läsnäolopäivä' vs. 'kaksi tai useampi'). Teksti vertailee näitä vaihtoehtoja ja perustelee kahden päivän mallia ennen kuin lopullinen päätös (2+3-malli) esitetään muistiossa. Tämä osoittaa vaihtoehtojen vertailun ja arvioinnin ennen päätöstä. Siksi EXTRACTION CONDITION täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä kysyy vaihtoehdoista ('yksi läsnäolopäivä' vs. 'kaksi tai useampi'), ja AI vertailee näitä vaihtoehtoja ennen kuin esittää lopullisen suosituksen ('2+3 -malli'). Vertailu tapahtuu ennen päätöstä, joten negatiivinen ehto (arvioitu päätöksen jälkeen) ei täyty. Siksi exact_quote on tyhjä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_34259a6c02b74917b12f74b5f3839a66` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers ('is the best', 'must be done', 'is the only way'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. EXTRACTION CONDITION: no empirical data or external reference exists in the same paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): data exists.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt dogmaattisia absoluuttisia merkkejä ('on paras', 'on pakko tehdä', 'on ainoa tapa'), joiden yhteydessä ei olisi ollut empiiristä dataa tai ulkoista viittausta samassa kappaleessa. Ehdotus perustuu 'tutkimustietoon' ja esittää 'suosituksia', ei ehdottomia totuuksia ilman perusteluja.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'reiluus korvataan laajennetulla työaikajoustolla (pankitusjärjestelmä vapaapäiviä varten) sekä kampustyöpisteiden parhaalla mahdollisella ergonomialla ja varustelulla.' käytetään dogmaattista absoluuttista merkitsijää 'parhaalla mahdollisella'. Samassa kappaleessa ei ole empiiristä dataa tai ulkoista viittausta, joka tukisi tätä väitettä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_43516f120e4a415bb0ee3a878a53a5bc` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept generic 'more data is needed' statements. STEP 1 (Syntactic Anchor): Find methodological critique markers (e.g., 'our measurement of X may overrepresent', 'the bias in our sample'). STEP 2 (Bounding Box): Scan the paragraph. If a specific structural flaw in the methodology is explicitly identified. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Presence detected: Kappaleessa tunnistetaan metodologinen puute (KPI-mittareiden puute asiantuntijatyölle), joka johtaa johtamisen muuttumiseen "mututuntumaksi". Tämä on spesifi rakenteellinen virhe metodologiassa.. Exceptions audit: Tekstissä esitettiin kritiikkiä ehdotuksen käytännön toteutuksesta ja oletuksista, mutta ei tunnistettu nimenomaisesti metodologista rakennevirhettä (esim. tiedonkeruussa tai analyysissä).  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt metodologisen kritiikin merkkejä, jotka tunnistaisivat nimenomaisesti rakenteellisen virheen metodologiassa. Paholaisen asianajajan osuus kritisoi ehdotusta, ei sen taustalla olevaa metodologiaa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_69cc84e0b0c44996a8a95e09b356c692` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find abrupt transition markers ('therefore', 'thus', 'so'). STEP 2 (Bounding Box): Scan the sentence containing the transition. EXTRACTION CONDITION: it connects two facts but lacks any explanatory mechanism ('because mechanism X'). NEGATIVE CONDITION (RETURN NULL IF MET): a mechanism is described. Do not accept explicit causal mechanisms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt äkillisiä siirtymämerkkejä ('siksi', 'näin ollen', 'joten'), jotka olisivat yhdistäneet kaksi faktaa ilman selittävää mekanismia. Kaikissa löydetyissä kausaalisissa yhteyksissä mekanismi oli kuvattu (esim. 'jotta kampus ei ruuhkautuisi', 'Tämä estää siiloutumisen', 'Tämä säästää kiinteistökuluja').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Mitigating exception found: Lause 'Ratkaisu ei siis ole paluu vanhaan, muttei myöskään sataprosenttinen etätyö.' sisältää äkillisen siirtymän merkitsijän 'siis'. Se yhdistää kaksi tosiasiaa (ei vanhaan, ei 100 % etätyöhön) ilman eksplisiittistä selittävää mekanismia ('koska mekanismi X') itse lauseessa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c17684acfcbe4a918e5ae0705b452b06` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user commands focused on tone (e.g., 'make it sound more persuasive', 'make it more academic'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user focuses solely on the performativity (tone/style) while ignoring substantive factual gaps. Revisions containing factual additions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä pyytää 'sopivaa kieltä', mikä on sävyyn/tyyliin liittyvä pyyntö. Kuitenkin tämä pyyntö on osa laajempaa ohjetta, joka sisältää myös rakenteellisia elementtejä ('Tee tästä muistio', 'Yksi sivu riittää', 'Tee lyhyt johdanto selvityksellesi'). Siksi käyttäjä ei keskity *ainoastaan* performatiivisuuteen, eikä poimintaehto täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää kyllä tyyliin ja sävyyn liittyviä muutoksia (esim. 'selvällä kielellä (ei jargonia)', 'tekstin muodossa sopiva kieli'), mutta nämä pyynnöt eivät ole *ainoastaan* performatiivisia. Ne ovat aina yhdistettynä muihin rakenteellisiin tai sisällöllisiin vaatimuksiin, kuten dialogimuotoon, muistion luomiseen tai johdannon lisäämiseen. Ehto 'user focuses solely on the performativity' ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fda64d221181411fa70843a88689b27b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate completeness. STEP 1 (Syntactic Anchor): Find words indicating alternatives ('however', 'other factors', 'confounder'). STEP 2: EXTRACTION CONDITION: the text explicitly names a potential third variable that could also explain the outcome. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Timo esittää 'kulut ja juridiikka' potentiaalisina kolmansina muuttujina, jotka voivat selittää tai vaikuttaa globaalin rekrytoinnin lopputulokseen, vastaten Sarin aiempaan väitteeseen sen hyödyistä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt eksplisiittistä mainintaa potentiaalisesta kolmannesta muuttujasta, joka voisi selittää lopputuloksen (eli sekoittavasta tekijästä). Vaikka vaihtoehtoisia näkökulmia tai haasteita esitettiin, ne eivät olleet kolmansia muuttujia, jotka selittäisivät aiemmin esitettyä lopputulosta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5257ba1edae34afe8b837c8c238cf743` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'mastery'. STEP 1 (Syntactic Anchor): Find structural breakdown markers (e.g., 'firstly', 'component A', 'broken down into', 'ensimmäiseksi'). STEP 2: EXTRACTION CONDITION: the text physically separates a complex problem into at least three distinct, testable sub-components. NEGATIVE CONDITION (RETURN NULL IF MET): it remains a single monolithic block.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Teksti jakaa hybridityömallin neljään selkeästi erilliseen ja testattavissa olevaan osaan käyttäen numeroituja otsikoita. Ensimmäinen numeroitu otsikko toimii fyysisenä merkkinä rakenteellisesta jaottelusta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: [SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_ce2566987e8f44819102d6eb1d28857d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not flag open-ended questions explicitly left for future research. STEP 1 (Syntactic Anchor): Find a question mark '?' used by the author to question their own premise. STEP 2 (Bounding Box): Scan the following 2 sentences. If the author answers their own question confirming the premise without citing new data. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää kysymysmerkkiä, jota kirjoittaja käyttää kyseenalaistamaan omaa premissiään, ja että kirjoittaja vastaa kysymykseen vahvistaen premissin ilman uutta dataa. Vaikka kysymysmerkkejä löytyy, niitä ei käytetä kyseenalaistamaan omaa premissiä tällä tavalla, eikä niitä seuraa premissin vahvistus ilman uutta dataa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Mitigating exception found: Tekstistä löytyi `ai:`-lohkon sisältä kysymysmerkki, jota kirjoittaja (AI) käytti kyseenalaistamaan omaa oletustaan ('Miksi kaksi päivää?'). Välittömästi seuraava lause vastasi kysymykseen vahvistaen oletuksen ('Toinen läsnäolopäivä jättää tilaa aikatauluttomalle ajalle') ilman uuden datan esittämistä kyseisessä vastauksessa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5b0573225735409b8ef3d3eac041236d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers (e.g., 'always', '100% guaranteed', 'it is a fact that'). STEP 2 (Bounding Box): Scan the same paragraph. If the absolute claim is made regarding a compliance or archival rule BUT no external framework (ARMA, ISO, law) is cited in that paragraph. Do not accept absolute claims that are mathematically verifiable. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei ole dogmaattisia absoluuttisia väitteitä, jotka koskisivat vaatimustenmukaisuutta tai arkistointisääntöjä ilman ulkoisen viitekehyksen mainintaa. Vahvat ilmaisut ovat joko ennusteita tai yleisiä toteamuksia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Mitigating exception found: Lauseessa käytetään absoluuttista merkitsijää 'väistämättä' kuvaamaan seurauksia, jos työntekijä on kampuksella vain yhtenä päivänä viikossa. Tässä yhteydessä ei viitata ulkoiseen viitekehykseen (ARMA, ISO, laki).  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_82698279c7bd44b9a763f56423b86bda` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find physical actions of organizing or saving data (e.g., 'stored in', 'saved as', 'archived'). STEP 2 (Bounding Box): Scan the sentence. If an action is taken to store data. Do not evaluate if the storage method is 'good' or 'bad'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Lauseet kuvaavat fyysisiä toimia tietojen järjestämiseksi tai tallentamiseksi (työhuoneiden säilyttäminen luottamuksellista tietoa käsitteleville) ja tilankäytön tiivistämiseksi (siirtyminen yhteiskäyttöisiin tiloihin), mikä vastaa fyysisen tallennustoiminnan ankkuria.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei ole fyysisiä toimintoja, jotka kuvaavat tiedon järjestämistä tai tallentamista (esim. 'stored in', 'saved as', 'archived').  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_728cd0dff7384300bc55622fa7dfffc0` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate accuracy. STEP 1: Find a claim connecting two variables. STEP 2: EXTRACTION CONDITION: the text explicitly states the direction of influence (which variable affects which). NEGATIVE CONDITION (RETURN NULL IF MET): the direction is ambiguous or bi-directional without explanation.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Teksti yhdistää kaksi muuttujaa ('laajaan etätyöhön' ja 'toimitilakulumme putosivat') ja ilmoittaa eksplisiittisesti vaikutussuunnan (etätyö johti kustannusten laskuun).  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Etsin kausaaliväitteitä ja tarkistin, onko vaikutussuunta eksplisiittisesti ilmoitettu eikä epäselvä tai selittämättä kaksisuuntainen. Kaikissa löydetyissä kausaaliväitteissä vaikutussuunta oli selkeästi ilmaistu (esim. 'käytännöt ovat johtaneet siiloutumiseen', 'malli maksimoi työhyvinvoinnin'). Negatiivinen ehto ei täyttynyt, joten rikettä ei löytynyt.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_569a2c551bae4301b1217c8a7107cc2c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find an explicit causal claim (e.g., 'Because of X', 'Led to Y', 'Caused', 'Resulted in'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the causal claim BUT does NOT contain empirical data vocabulary (e.g., numbers, percentages, 'log', 'quote', 'measured', 'statistically') -> ACCEPT. If it contains empirical measurement vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, subjective 'unproven' nature, or 'truth'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Lause 'Jos yhteisöllisyys katoaa, yrityskulttuuri kuolee.' on eksplisiittinen kausaaliväite. Kappale, jossa se esiintyy, ei sisällä empiiristä datasanastoa, mikä täyttää ehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Vaikka kausaalinen väite on olemassa ('Kun siirryimme... putosivat'), se sisältää empiiristä dataa ('30 prosenttia'), joten negatiivinen ehto täyttyy ja poimintaa ei tehdä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_3b951170f9f54f649b7da95fb9f121e6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept explicit hypothesis testing. STEP 1 (Syntactic Anchor): Find descriptive reporting verbs (e.g., 'the data shows', 'we observed', 'indicates'). STEP 2 (Bounding Box): Scan the paragraph. If the observation lacks a formulated hypothesis that could be tested or disproven (e.g. no 'if X then Y' structure). Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Presence detected: Lauseessa "Kun siirryimme laajaan etätyöhön, toimitilakulumme putosivat 30 prosenttia" esiintyy kuvaileva raportointiverbi "putosivat". Tämä on havainto menneestä tapahtumasta, eikä sille ole esitetty muotoiltua hypoteesia.. Exceptions audit: Vaikka tekstissä oli kuvailevia raportointiverbejä (esim. 'osoittavat'), ne viittasivat ulkoisiin tutkimuksiin, joilla oletetaan olevan jo muotoiltu hypoteesi. AI ei tehnyt omia havaintoja ilman hypoteesia.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Vaikka tekstissä on kuvailevia raportointiverbejä, ne liittyvät tutkimustuloksiin, jotka oletettavasti perustuvat formuloituihin hypoteeseihin. Siksi ehto 'havainnosta puuttuu formuloitu hypoteesi' ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6e3e3aa6b9134a01838c3b70a35b4f32` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find weak associative language ('relates to', 'is associated with', 'impacts'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it connects Data to a Claim without defining the exact causal mechanism. NEGATIVE CONDITION (RETURN NULL IF MET): it uses precise causal mechanism ('which directly causes'). Precise causal mechanisms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt heikkoa assosiatiivista kieltä ('liittyy', 'yhdistetään', 'vaikuttaa'), joka yhdistäisi datan väitteeseen määrittelemättä tarkkaa kausaalista mekanismia. Käytetyt verbit (esim. 'johtaneet', 'maksimoida', 'suojella', 'tukea', 'saavuttaa', 'estää', 'mahdollistaa', 'pitää', 'säästää', 'vapauttaa') kuvaavat tarkkoja kausaalisia suhteita.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'Tavoitettavuus sidotaan opetuksen rytmiin.' 'sidotaan' (is tied to) on heikko assosiatiivinen kieli. Se yhdistää datan (opetuksen rytmi) väitteeseen (tavoitettavuus) määrittelemättä tarkkaa kausaalista mekanismia ('joka suoraan aiheuttaa').  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fcdde66df02c4edb9e090172c3e2b956` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not synthesize steps yourself. STEP 1 (Syntactic Anchor): Find sequential logic markers (e.g. 'First', 'Second', 'Finally', 'Step 1'). STEP 2 (Bounding Box): Scan the block. EXTRACTION CONDITION: a continuous, unbroken chain of at least three explicit logical steps is documented. NEGATIVE CONDITION (RETURN NULL IF MET): fewer than three steps. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Presence detected: Lopullinen muistio sisältää neljä selkeästi numeroitua kohtaa, jotka muodostavat jatkuvan ja katkeamattoman loogisen vaiheketjun ehdotetun hybridityömallin esittelyssä.. Exceptions audit: Muistiossa on neljä selkeästi numeroitua ja otsikoitua osiota, jotka esittävät ehdotuksen loogiset vaiheet. Nämä osiot eivät kuitenkaan ole fyysisesti yhtenäinen, katkeamaton tekstilohko, vaan niiden välissä on muita kappaleita. Koska exact_quote-vaatimus edellyttää fyysisesti yhtenäistä lainausta, en voi poimia näitä otsikoita yhtenä lainauksena. Siksi exact_quote on null.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Vaikka tekstissä on neljä numeroitua loogista vaihetta, jotka täyttävät vähintään kolmen vaiheen vaatimuksen, ne eivät ole fyysisesti jatkuva merkkijono lähdetekstissä. Ne ovat erillisten kappaleiden otsikoita, joiden välissä on muuta tekstiä. Siksi 'PHANTOM EXTRACTION BAN' -säännön mukaisesti exact_quote on null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_45b5e5067e2743dbbc275ac472e4cc06` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find a falsification marker (e.g. 'Let\'s try to break this', 'What EXTRACTION CONDITION: the opposite is true', 'Counter-argument'). STEP 2 (Bounding Box): Scan the paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): the user explicitly introduces a scenario designed to make their own hypothesis fail. If no active stress-test is present.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei eksplisiittisesti esitä skenaariota, joka olisi suunniteltu saamaan hänen oma hypoteesinsa epäonnistumaan. Vaikka AI:ta pyydetään toimimaan 'paholaisen asianajajana', tämä ei ole käyttäjän omaan hypoteesiin kohdistuva stressitesti, joten negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Presence detected: Käyttäjä pyytää tekoälyä toimimaan 'paholaisen asianajajana' ja antamaan 'säälimätöntä kritiikkiä' omalle ehdotukselleen, mikä on selkeä falsifiointimerkki ja stressitesti.. Exceptions audit: Käyttäjä pyytää AI:ta toimimaan 'paholaisen asianajajana' ja kritisoimaan AI:n omaa ehdotusta, ei käyttäjän omaa hypoteesia. Sääntö edellyttää, että käyttäjä esittelee skenaarion, joka on suunniteltu saamaan *hänen oman hypoteesinsa* epäonnistumaan.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_131403148eab4c739149e6bd29164ce2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find reformulation markers (e.g., 'in other words', 'this means', 'essentially'). STEP 2: EXTRACTION CONDITION: found, the author is paraphrasing. Do not accept verbatim copy-pasting of definitions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt eksplisiittisiä uudelleenmuotoilun merkkejä (esim. 'toisin sanoen', 'tämä tarkoittaa', 'pohjimmiltaan'), jotka esittäisivät käsitteen uudelleenmuotoiltuna versiona.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Presence detected: Tekstissä käytetään sanaa 'eli' selittämään tai uudelleenmuotoilemaan edellistä käsitettä 'ilmeisimmästä' käsitteeksi 'rahasta'.. Exceptions audit: Tekstistä ei löytynyt suomenkielisiä vastineita uudelleenmuotoilun markkereille (esim. 'toisin sanoen', 'tämä tarkoittaa', 'pohjimmiltaan').  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_7b88a578c3824b31b83a5154f7d3667a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Presence detected: Teksti esittää useita positiivisia lopputuloksia ('estää siiloutumisen, mahdollistaa... ja pitää...') suorina seurauksina ehdotetusta mallista. Nämä johtopäätökset esitetään varmoina ilman, että tunnustetaan mahdollisia tuntemattomia tekijöitä tai muuttujia, jotka voisivat vaikuttaa näihin lopputuloksiin, perustuen näin rajoitettuun näkyvään näyttöön (mallin rakenteeseen).. Exceptions audit: Tekstissä ei ole havaittavissa kausaalisia harppauksia tai johtopäätöksiä, jotka perustuisivat pelkästään rajalliseen näkyvään todisteeseen jättäen tuntemattomat tekijät huomiotta. Johtopäätökset ovat joko suoria seurauksia tai perustuvat mainittuun tutkimustietoon.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: [SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2d59c195d8324fc0a22838ef53417686` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph evaluating a successful outcome or positive achievement. STEP 2: Verify if the paragraph or immediate surrounding section completely omits any epistemic boundary or uncertainty markers. <ambiguity_protocol>ABSOLUTE ABSENCE ENFORCEMENT: You must prove that epistemic boundary markers are COMPLETELY absent from the surrounding section. Epistemic boundary markers include words/phrases like 'however', 'limitations', 'failed to', 'uncertainty', 'but', 'silti', 'kuitenkin', 'rajoitus', 'epävarmuus'. If you locate even a single such marker in the section, the absence is falsified, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Kappale "Tämän selvityksen tavoitteena on korvata nykyinen malli tavoitteellisella ja toimintalähtöisellä hybridityöpolitikaalla. Ehdotus perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon. Mallin tavoitteena on maksimoida työhyvinvointi, suojella organisaatiokulttuuria, tukea pedagogista innovointia ja saavuttaa toimitilasäästöjä – reiluutta unohtamatta." kuvaa positiivisia saavutuksia/tavoitteita, eikä siinä ole yhtään episteeemistä rajaus- tai epävarmuusmerkkiä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Vaikka toinen kappale kuvaa positiivisia tavoitteita, sitä edeltävä kappale sisältää epistemologisia rajausmerkkejä ('kuitenkin', 'epävarmuuteen'), mikä falsifioi ehdon, että ympäröivä osa jättää TÄYSIN pois kaikki tällaiset merkit.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_e407bc0297324a5da95c9091d08b88bc` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not use subjective words like 'good'. STEP 1 (Syntactic Anchor): Find a stated objective containing a measurable goal (e.g. 'Reduce word count', 'Include 3 examples'). STEP 2 (Bounding Box): Scan the result evaluation. EXTRACTION CONDITION: the text quotes the exact measurable goal and confirms it with a physical measurement or count. NEGATIVE CONDITION (RETURN NULL IF MET): the confirmation is purely qualitative.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Presence detected: Käyttäjä kysyi 'Riittääkö yksi läsnäolopäivä? Mikä puoltaisi esim. kahta tai useampaa läsnäolopäivää?'. Tekoäly ehdotti '2 päivää kampuksella, 3 päivää etätyömahdollisuutta' ja vahvisti tämän mitattavalla luvulla 'koska 60 % ajasta ollaan etänä'. Tämä on fyysinen mittaus/laskenta, joka vahvistaa mitattavan tavoitteen.. Exceptions audit: Käyttäjä asetti mitattavan tavoitteen ('yhden sivun yhteenveto'), mutta tekoäly ei vahvistanut tätä tavoitetta fyysisellä mittauksella tai laskennalla. Vahvistus oli puhtaasti kvalitatiivinen (tuottamalla tekstin), joten negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä mainitaan tavoitteita kuten 'maksimoida työhyvinvointi' ja 'saavuttaa toimitilasäästöjä'. Nämä ovat laadullisia tavoitteita, eikä niitä vahvisteta fyysisellä mittauksella tai lukumäärällä 'product_text'-dokumentissa. Siksi negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_64cce5cf564a497dbbc2341248cea637` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find external citation markers (e.g., 'according to', 'study shows', 'metric [X]', 'perustuen'). STEP 2: EXTRACTION CONDITION: the logical deduction is strictly tied to a specific named methodology, framework, or external dataset. NEGATIVE CONDITION (RETURN NULL IF MET): it relies purely on internal logic.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [TRUE]:**
  > *Mitigating exception found: Ehdotuksen looginen päättely on sidottu eksplisiittisesti ulkoisiin lähteisiin, Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [FALSE]:**
  > *No presence of target concept detected: [SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0af46ca3de69431e8a3eea89df104507` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not flag dialectical synthesis that mathematically resolves the conflict. STEP 1 (Syntactic Anchor): Find conflict identification markers (e.g., 'contradictory results', 'on the one hand'). STEP 2 (Bounding Box): Scan the paragraph. If the conflict is left unresolved using passive synthesis (e.g., 'both sides have valid points', 'it is a complex issue') without falsifying one. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fcf075277344441fa67e60634b1c548b) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt konfliktin tunnistusmerkkejä, joita olisi seurannut passiivinen synteesi ilman toisen osapuolen falsifiointia. Kaikki tunnistetut ristiriidat joko ratkaistiin tai esitettiin suorana kritiikkinä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d4ea135591c94d798d49d844d0d75a90) - [TRUE]:**
  > *Presence detected: Lauseessa on vastaväiteindikaattori 'Toisaalta', fyysinen lähdeviittaus 'Lähde: Työterveyslaitos (2025)' ja empiiristä mittausvokabulaaria 'TTL:n tutkimukset osoittavat' ja 'rekisteri- ja kyselyaineistoihin'. Kaikki ehdot täyttyvät.. Exceptions audit: En löytänyt tekstistä ristiriitojen tunnistusmerkkejä, joita olisi passiivisesti syntetisoitu ratkaisematta niitä tai falsifioimatta toista osapuolta. Teksti joko esittää ongelmia ja ratkaisuja tai kritisoi aiempaa ehdotusta aktiivisesti.  [5. VALIDATION DECISION: PASS]*

---

