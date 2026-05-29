# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 96.24 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.9247
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.9247
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.0376
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 7 kpl
- **PASSED -> FAILED:** 3
- **FAILED -> PASSED:** 4
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_c1a05b0ce5f88033` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a named alternative model or theory. STEP 2 (Bounding Box): Scan the same paragraph. EXTRACTION CONDITION: the alternative is mentioned but the paragraph contains exactly 0 counter-arguments or comparative data points. Do not evaluate 'depth', simply count the data points.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_04f8b6bec55d4c78b60c9ba2b921e0a9) - [FALSE]:**
  > *Sääntö edellyttää nimetyn vaihtoehtoisen mallin tai teorian mainitsemista. Skannasin koko asiakirjan, eikä se mainitse mitään Sitran megatrendianalyysille vaihtoehtoista nimettyä mallia tai teoriaa. EHTO EI TÄYTY.*
- **Run 2 (exe_248d846b198f4c2683878c1d4573b5cd) - [TRUE]:**
  > *Sääntö etsii nimettyä vaihtoehtoista mallia, joka mainitaan ilman vasta-argumentteja tai vertailevaa dataa. Tekstissä todetaan: "Sitran näkemys on, että paluuta vanhaan normaaliin ei ole...". Tässä "vanha normaali" on vaihtoehtoinen malli tai tila. Kappaleessa ei esitetä mitään dataa tai argumentteja tämän väitteen tueksi, vaan se vain todetaan. Tämä täyttää säännön ehdon.*

---

### Atom-ID: `tda_93568eab47234542` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept mathematical axioms. STEP 1 (Syntactic Anchor): Find dogmatic certainty markers (e.g., 'is self-evident', 'needs no proof', 'as we all know', 'beyond question'). STEP 2 (Bounding Box): Scan the sentence. If it explicitly blocks further empirical testing or questioning. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_04f8b6bec55d4c78b60c9ba2b921e0a9) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää dogmaattisen varmuuden ilmaisua (esim. 'on itsestään selvää', 'kiistaton'), joka nimenomaisesti estää empiirisen testauksen tai kyseenalaistamisen. Lähdeteksteistä ei löytynyt tällaisia ilmauksia. Vaikka tekstissä on vahvoja väitteitä, kuten 'on peruuttamaton', ne eivät täytä säännön toista ehtoa eli aktiivista jatkokyselyjen estämistä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_248d846b198f4c2683878c1d4573b5cd) - [TRUE]:**
  > *Presence detected: Säännön vaatimia dogmaattisen varmuuden merkkejä (esim. 'on itsestään selvää', 'ei kaipaa todisteita') tai ilmauksia, jotka nimenomaisesti estävät empiirisen testauksen, ei löytynyt lähdetekstistä.. Exceptions audit: Lähdeteksti ei sisällä dogmaattisia varmuuden ilmauksia, kuten 'on itsestään selvää' tai 'kiistaton', jotka nimenomaisesti estäisivät empiirisen testaamisen tai kyseenalaistamisen. Siksi säännön ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_3da456b757644c46` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept vague assertions like 'it is secure'. STEP 1 (Syntactic Anchor): Find explicit physical validation actions (e.g. 'validated', 'filtered', 'sanitized', 'checked against'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it describes a concrete data validation rule being applied to input or output.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_04f8b6bec55d4c78b60c9ba2b921e0a9) - [FALSE]:**
  > *No presence of target concept detected: The rule requires finding an explicit physical validation action describing a concrete data validation rule. I scanned all texts for Finnish equivalents of 'validated', 'filtered', 'sanitized'. No such technical data validation rules were described. The actions mentioned are either high-level strategic goals ('Panostus kyberturvallisuuteen') or manual content corrections ('Korjasin taulukosta').  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_248d846b198f4c2683878c1d4573b5cd) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii konkreettisia validointitoimia. Reflektiotekstissä käyttäjä kuvaa, kuinka hän sovelsi tuotokseen konkreettista validointisääntöä: "Korjasin taulukosta Eurooppaan liittyvän asian, koska näin alkupeäisen tarpeettomana." Tämä osoittaa, että tarpeettomaksi katsottu sisältö poistettiin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6be555cac0b9115b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_04f8b6bec55d4c78b60c9ba2b921e0a9) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii proseduraalisia merkkejä (kuten numerolistoja) kappaleesta, jossa EI ole synteesi- tai päättelyverbejä. Tekstissä on numerolistoja, mutta ne ovat osa analyyttistä ja deduktiivista kontekstia (esim. johdantona 'Johtoryhmälle tämä tarkoittaa:'). Negatiivinen ehto (päättelyverbien puuttuminen) ei täyty. EHTO EI TÄYTY.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_248d846b198f4c2683878c1d4573b5cd) - [TRUE]:**
  > *Mitigating exception found: Teksti sisältää numeroidun listan, joka toimii menettelyllis-järjestyksellisenä ankkurina. Listausta edeltävä kappale ei sisällä säännössä kiellettyjä synteesi- tai päättelyverbejä (kuten 'analysoitu', 'päätelty'). Siksi ehdot täyttyvät.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c6bcce2b818718a1` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. Do not accept unbounded absolute rules.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_04f8b6bec55d4c78b60c9ba2b921e0a9) - [TRUE]:**
  > *Presence detected: Sääntö etsii operatiivisten rajojen määrittelyä. Lähdeteksti on strateginen analyysi eikä sisällä lauseita, joissa määriteltäisiin sääntöjen soveltamisalan rajoja ankkureilla, kuten 'tämä koskee vain' tai 'pois lukien'.. Exceptions audit: Sääntö etsii rajojen määrittelyä koskevia merkkejä, kuten 'this applies only to'. Lähdetekstin `ai:`-lohkoissa ei ole lauseita, joissa tekoäly määrittelisi toiminnallisia rajoja millekään säännölle tai prosessille. CONDITION NOT MET.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_248d846b198f4c2683878c1d4573b5cd) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii operatiivisten rajojen määrittelyä. Lähdeteksti on strateginen analyysi eikä sisällä lauseita, joissa määriteltäisiin sääntöjen soveltamisalan rajoja ankkureilla, kuten 'tämä koskee vain' tai 'pois lukien'.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_247927c98b0c46f8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. Rebuttals that provide counter-data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_04f8b6bec55d4c78b60c9ba2b921e0a9) - [TRUE]:**
  > *Mitigating exception found: HAVAINTOPROSESSI: 1. Etsittiin retorisia ohituksia, kuten 'vaikka X on totta, sillä ei ole väliä'. | 2. Skannattiin koko `Product_Text`. | 3. Tekstistä ei löydy lauseita, joissa mainittaisiin vastaväite ja se sitten ohitettaisiin retorisesti. | 4. Ankkureita ei löytynyt. | 5. EHTO EI TÄYTY.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_248d846b198f4c2683878c1d4573b5cd) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii retorisia ohituksia, joissa vastaväite mainitaan mutta sivuutetaan ilman dataa. Lähdeteksti ei esitä vastaväitteitä ja siten ei myöskään sivuuta niitä. EHTO EI TÄYTTYNYT.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_bdbdc546677cc222` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find a formal citation, academic framework, or recognized methodology (e.g. 'Pearl\'s do-calculus', 'Bayesian updating'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the causal reasoning is explicitly justified by applying the rules of this named external framework. NEGATIVE CONDITION (RETURN NULL IF MET): the framework is merely name-dropped without applying its rules.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_04f8b6bec55d4c78b60c9ba2b921e0a9) - [TRUE]:**
  > *Presence detected: The text repeatedly cites a recognized methodology ('Sitran Megatrendiraportit'). The reasoning is explicitly justified by applying the content of this framework, for instance, by tracing the evolution of a concept from one report to another. The negative condition (framework is merely name-dropped) is not met.. Exceptions audit: Sääntö vaatii, että kausaalinen päättely perustellaan nimenomaisesti soveltamalla nimetyn viitekehyksen sääntöjä. Vaikka tekstissä mainitaan viitekehyksiä (Sitran raportit, CSRD, EU-taksonomia), niitä käytetään joko tiedon lähteenä tai niiden korkean tason vaikutus tiivistetään. Teksti ei sovella näiden kehysten erityisiä sääntöjä tai artikloita yksityiskohtaisen kausaalisen argumentin rakentamiseen. Negatiivinen ehto 'viitekehys on vain mainittu soveltamatta sen sääntöjä' täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_248d846b198f4c2683878c1d4573b5cd) - [FALSE]:**
  > *No presence of target concept detected: The text mentions formal sources and frameworks like 'Sitran Megatrendiraportit' and 'CSRD-direktiivin'. However, the reasoning is not justified by applying the specific rules of these frameworks. They are referenced as the source of information or as market pressures, rather than a formal methodology whose rules are used to structure the argument.  [5. VALIDATION DECISION: PASS]*

---

