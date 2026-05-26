# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 184
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 90.76 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.8123
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.0924
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 17 kpl
- **PASSED -> FAILED:** 7
- **FAILED -> PASSED:** 10
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_bce60530213249dd` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'spurious'. STEP 1 (Syntactic Anchor): Find causal words (e.g. 'causes', 'because'). STEP 2 (Bounding Box): Scan the same sentence. EXTRACTION CONDITION: the causal claim is backed ONLY by a statistical correlation or simultaneous occurrence without any physical mechanism. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [TRUE]:**
  > *Mitigating exception found: The text makes a causal claim that the crumbling of nature's carrying capacity directly drives the cracking of the economy's foundation. However, it does not provide an explicit intermediary mechanism, presenting the relationship as a direct consequence, which resembles a claim based on high-level correlation rather than a detailed causal process.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä kausaalisia väitteitä, jotka perustuisivat ainoastaan korrelaatioon ilman taustalla olevaa mekanismia. Kausaaliväittämät sisältävät johdonmukaisesti vähintään ylätason mekanismin tai loogisen yhdistäjän (esim. 'ajaa suoraan siihen, että', 'ruokkivat', 'vaikuttavat').  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_545bffdc85a31f0e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Reject superficial mentions of frameworks. STEP 1 (Syntactic Anchor): Find exact framework citations (e.g. 'OWASP LLM01', 'NIST', 'ISO 27001'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the specific framework clause is directly linked to the physical security action taken. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: The text does not contain any exact citations of security frameworks like 'OWASP LLM01', 'NIST', or 'ISO 27001'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Mitigating exception found: Teksti sisältää tarkan viittauksen olemassa olevaan säädökseen ('EU:n tietosuojasäädökset') ja yhdistää sen strategiseen toimenpiteeseen (markkinoiden fragmentaatio ja data-autonomia).  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_f142c3fa1d08cc2d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: EXTRACTION CONDITION: the user explicitly restricts the AI to the provided data and demands exact evidence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: No user prompt contains any of the specified syntactic anchors for demanding exact evidence, such as 'poimi suoraan' or 'perustuen vain'. Therefore, no extraction is possible.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Presence detected: Käyttäjä rajoittaa tekoälyn vastauksen perustumaan vain annettuihin raportteihin. Lauseke "raporttien perusteella" toimii ankkurina, joka vaatii uskollisuutta lähdeaineistolle.. Exceptions audit: Lähdeaineiston käyttäjäkehotteista ei löydy yhtään säännön määrittelemää syntaktista ankkuria ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain') tai niiden semanttista vastinetta. Käyttäjä ei missään vaiheessa rajoita tekoälyä eksplisiittisesti vain annettuun dataan tai vaadi tarkkoja lainauksia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_247927c98b0c46f8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rebuttals that provide counter-data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [TRUE]:**
  > *Presence detected: The text uses a rhetorical bypass by stating that nature's limits are "not just a limitation, but" a new foundation. This dismisses the negative framing without providing data to counter it.. Exceptions audit: The text does not contain rhetorical bypasses like 'although X is true' to dismiss a counter-argument without data. It presents its analysis without engaging potential opposition.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii retorisia ohituksia, joissa vastaväite mainitaan mutta sivuutetaan ilman dataa. Lähdetekstissä ei esiinny tällaisia rakenteita.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_bdbdc546677cc222` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Do not accept generic AI knowledge. STEP 1 (Syntactic Anchor): Find a formal citation, academic framework, or recognized methodology (e.g. 'Pearl\'s do-calculus', 'Bayesian updating'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the causal reasoning is explicitly justified by applying the rules of this named external framework. NEGATIVE CONDITION (RETURN NULL IF MET): the framework is merely name-dropped without applying its rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [TRUE]:**
  > *Presence detected: Käyttäjä viittaa nimenomaisesti lähdemateriaaliin ('Sitran megatrendit') ja ehdottaa uutta synteesiä kysymällä, voiko niitä "yhdistellä ja tuottaa supermegatrendejä". Tämä on suoraa nimetyn ulkoisen viitekehyksen (raporttien trendit) sääntöjen (yhdistely) soveltamista uuden, korkeamman tason kausaalirakenteen luomiseksi.. Exceptions audit: The source text mentions 'Sitran Megatrendiraportit' as a source and regulations like 'CSRD-direktiivin ja EU-taksonomian'. However, it does not cite or apply any formal academic framework or recognized methodology (like Pearl's do-calculus or Bayesian updating) to justify its causal reasoning. The reasoning is presented without grounding in a formal external model.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [FALSE]:**
  > *No presence of target concept detected: The text mentions sources and regulations like 'Sitran Megatrendiraportit', 'CSRD-direktiivi', and 'EU-taksonomia'. However, these are not formal academic frameworks or methodologies for causal reasoning in the sense of the rule's examples (e.g., 'Pearl's do-calculus'). They are cited as sources of information, not as a logical framework to structure the reasoning itself. The user's invention of 'supermegatrendit' is a structural concept for this task, not an external recognized methodology.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_55dfd9cb0adec620` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: The text identifies several business and brand risks (e.g., 'maineriskin') but pairs each one with a corresponding strategic mitigation action (e.g., 'Kehitetään ja käytetään teknologiaa eetisesti'). No risk is left unaddressed.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Mitigating exception found: Teksti tunnistaa eettisiin AI-ratkaisuihin liittyvän maineriskin, mutta ehdotettu toimenpide on yleinen periaate eikä säännön esimerkkien kaltainen konkreettinen tekninen toimenpide.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2303fd9ca0b0fa67` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prompts alone. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept generic terms like 'safe'. STEP 1 (Syntactic Anchor): Find explicit references to standard security protocols (e.g. 'policy', 'standard', 'guideline', 'OWASP'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text physically demonstrates adherence to a named standard. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: The text mentions the 'CSRD-direktiivi' and 'EU-taksonomia', but these are sustainability reporting regulations, not security protocols as intended by the rule's context (e.g., OWASP).  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Mitigating exception found: Teksti viittaa eksplisiittisesti olemassa oleviin säädöksiin (CSRD, EU-taksonomia) ja toteaa niiden tekevän kestävyydestä pakollista, mikä osoittaa standardien tunnistamista ja noudattamista.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b1717b2ca9f25e2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Syntactic Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: EXTRACTION CONDITION: the command lacks any specific constraints and allows the AI to freely decide what is important. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: The user prompts do not contain a broad summary command that lacks specific constraints. The prompt 'koosta näistä vastauksista 1 sivun raportti' includes a constraint ('1 sivun'), so it does not meet the rule's condition.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Mitigating exception found: The user issues a command to 'koosta' (compile/summarize) a report from the previous answers. While it includes a page constraint, the core request allows the AI to decide which information is most important to include in the summary.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c74c4367acc028cf` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user phrases adopting AI methodology blindly (e.g., 'let us use your structure', 'proceed with that approach', 'do what you suggested'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly adopts the AI's proposed framework without adding their own constraints. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user modifies the AI's framework. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä ei omaksu sokeasti tekoälyn ehdottamaa viitekehystä. Päinvastoin, käyttäjä itse esittelee keskeisen käsitteen 'supermegatrendit' ja ohjaa tekoälyä rakentamaan raportin sen ympärille.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii todisteita siitä, että käyttäjä omaksuu sokeasti tekoälyn ehdottaman toimintatavan. Käyttäjä tekee päinvastoin: hän introduceeraa oman analyyttisen viitekehyksensä ('supermegatrendit') ja ohjaa tekoälyä toimimaan sen puitteissa. Tämä on aktiivista ohjausta, ei sokeaa omaksumista.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8f668ea29869ba8b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [TRUE]:**
  > *Mitigating exception found: The rule looks for an evaluation of an outcome that omits any mention of limitations. In the reflection text, the user states, 'Pyysin supermegatrendejä – tämä oli iso oivallus.' (I asked for super megatrends - this was a big insight.). This is a clear, positive evaluation of an action's outcome. The surrounding text does not mention any downsides, edge cases, or limitations of this 'super megatrends' approach, thus fitting the rule's criteria for one-sided evaluation.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii vahvistusharhaa, jossa onnistumista arvioidaan, mutta kaikki rajoitukset tai epäonnistumiset jätetään mainitsematta. Lähdeaineistossa, kuten tekoälyn vastauksessa kohdassa 'Ennusteiden Osuvuus', mainitaan sekä onnistumiset ('Osuva') että rajoitukset ('Monimutkainen/Aliarvioitu'). Myös käyttäjän reflektiossa mainitaan sekä oivallus ('iso oivallus') että ongelma ('vastaus oli liian laaja'). Aineisto ei siis osoita säännön kuvaamaa yksipuolista arviointia.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_9ab273ce743ac29e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess intent. STEP 1 (Syntactic Anchor): Find an evaluation of success or a positive outcome. STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text details the positive outcome but COMPLETELY OMITs any epistemic boundary markers (e.g. 'however', 'limitations', 'failed to', 'uncertainty'). NEGATIVE CONDITION (RETURN NULL IF MET): limitations are explicitly stated. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: This is an inverse rule. The rule is satisfied (no violation found) because the text does not omit limitations or uncertainties. It explicitly mentions multiple risks and challenges, such as 'kysynnän epävarmuuta' and 'ennakoimatomia katkoja'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Presence detected: This is a vice rule. The text makes a definitive, positive-framed strategic conclusion but completely omits any epistemic boundary markers like 'however', 'limitations', or 'uncertainty', presenting the path to success as absolute.. Exceptions audit: Sääntö edellyttää positiivisen lopputuloksen löytämistä, josta on jätetty kokonaan pois rajoituksia kuvaavat ilmaisut. Tekstissä kuitenkin mainitaan riskejä ja epävarmuuksia (esim. 'riskejä', 'maineriskin', 'epävarmuus'), joten säännön negatiivinen ehto täyttyy eikä rikkomusta löydy.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_8c7b6a9f0d8e411b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find examples or model structures provided by the user (e.g., 'Esimerkki:', 'Kuten tässä:', 'esimerkiksi'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: The user provides a concrete linguistic model or structurally detailed template to direct the AI. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei tarjoa valmista esimerkkiä tai yksityiskohtaista mallipohjaa (kuten 'Esimerkki: ...'). Sen sijaan käyttäjä esittää uuden käsitteen ('supermegatrendit') ja pyytää tekoälyä rakentamaan analyysin sen ympärille. Tämä on korkeamman tason ohjausta kuin esimerkin antaminen, eikä se vastaa säännön kirjaimellista määritelmää.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Presence detected: Sääntö etsii tilanteita, joissa käyttäjä antaa konkreettisen esimerkin tai rakenteellisen mallin. Käyttäjä ei anna valmista esimerkkiä. Sen sijaan hän ohjaa tekoälyä luomaan uuden rakenteen ('supermegatrendit') kysymyksellä. Myös käyttäjän reflektiossa todetaan: 'Esimerkkejä en antanut'. Ehto ei täyty.. Exceptions audit: Käyttäjä ei anna konkreettista esimerkkiä tai rakenteellista mallia tekoälyn seurattavaksi. Sen sijaan käyttäjä esittää käsitteellisiä kysymyksiä ja komentoja, kuten pyynnön luoda "supermegatrendejä", mutta jättää toteutuksen tekoälyn tehtäväksi antamatta mallia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c6bcce2b818718a1` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unbounded absolute rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [TRUE]:**
  > *Mitigating exception found: The text explicitly defines the target audience for the report. This acts as a boundary definition marker, limiting the scope of the document's application.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [FALSE]:**
  > *No presence of target concept detected: Tekoäly ei määrittele toiminnallisia rajoja vaatimustenmukaisuussäännölle. Vaikka se määrittelee raportin kohdeyleisön ja viitteet, tämä rajaa dokumentin soveltamisalaa, ei toiminnallisen vaatimustenmukaisuussäännön rajoja atomin määritelmän mukaisesti.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ade6cbd3f956fa67` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'collaboration' or 'politeness'. STEP 1 (Syntactic Anchor): Find delegation verbs ('päätä', 'valitse', 'kumpi', 'decide', 'choose'). STEP 2 (Bounding Box): Scan the prompt. EXTRACTION CONDITION: the user explicitly asks the AI to make a final subjective choice or decision on their behalf. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: The user prompts do not contain any of the specified syntactic anchors for delegation, such as 'päätä' or 'valitse'. The user maintains decision-making authority throughout the process.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Presence detected: The user's instruction 'ota näissä väleissä aina kun on järkevää' explicitly delegates the subjective decision of what is 'järkevää' (makes sense) to the AI. This is a clear instance of offloading a subjective choice.. Exceptions audit: The user does not delegate any subjective choices or final decisions to the AI. The user maintains control and provides explicit instructions on what to do next.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_32ee0cac79ad098e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä säännön määrittelemiä universaaleja ankkurisanoja, kuten 'aina' tai 'joka tapauksessa'. Vaikka tekstin sävy on yleistävä, se ei täytä säännön tiukkaa syntaktista vaatimusta.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Presence detected: Väite, että "Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa", on universaali ja ehdoton yleistys. Se soveltaa tietystä kontekstista (kestävyyden kasvava merkitys) johdettua trendiä kaikkiin tilanteisiin ilman rajauksia tai poikkeuksia.. Exceptions audit: Sääntö etsii universaaleja kausaaliväittämiä, kuten 'aina' tai 'joka tapauksessa'. Kohdeteksti ei sisällä tällaisia absoluuttisia yleistyksiä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6bf0433f60924302` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Vague filler words. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [FALSE]:**
  > *No presence of target concept detected: The text does not use conditional qualifiers to define boundaries or probabilities for its claims. The statements are generally presented as absolute rather than conditional.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [TRUE]:**
  > *Presence detected: Sääntö etsii kvalifioijia, jotka määrittelevät väitteelle rajoja. Lause 'Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa' käyttää sanaa 'Vain' asettaakseen selkeän ja ehdottoman ehdon (kestävät liiketoimintamallit) väitteen toteutumiselle.. Exceptions audit: Teksti ei käytä ehdollisia määreitä rajatakseen väitteidensä pätevyyttä tai todennäköisyyksiä. Kielenkäyttö on pääosin julistavaa ja absoluuttista.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_80c038ed35173cb4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not assume connections. STEP 1 (Syntactic Anchor): Find a multi-step sequence marker (e.g. 'Step 1.. Step 2.. Step 3', 'First.. Then.. Finally'). STEP 2 (Bounding Box): Scan the entire causal chain. EXTRACTION CONDITION: the text explicitly links at least three distinct sequential actions where each depends entirely on the previous one. NEGATIVE CONDITION (RETURN NULL IF MET): the chain is less than three steps or broken. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_31d496205d1a4f14ae9c582298daa9b4) - [TRUE]:**
  > *Presence detected: The rule requires a sequence of at least three dependent steps. The AI's explanation of the 'Talous' trend's evolution presents a clear three-step chronological sequence (2017 -> 2020 -> 2023), where each stage is described as an evolution from the previous one, fulfilling the rule's conditions.. Exceptions audit: Sääntö edellyttää vähintään kolmivaiheista, toisistaan riippuvaista kausaaliketjua, joka on kuvattu eksplisiittisesti. Vaikka lopputuotteessa ja keskustelussa on numeroituja listoja (esim. kolme supermegatrendiä tai kolme strategista suuntaa), ne ovat rinnakkaisia elementtejä, eivät peräkkäisiä, toisistaan riippuvaisia vaiheita. Aineistosta ei löydy vaaditun kaltaista ketjua.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_41da959333254701a834e7bca70b3d24) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii vähintään kolmivaiheista, eksplisiittisillä sekvenssimarkkereilla (esim. 'Ensin.. Sitten..') merkittyä kausaaliketjua, jossa jokainen vaihe riippuu edellisestä. Vaikka lopputuotteessa ja chat-lokeissa on luetteloita (esim. kolme supermegatrendiä, kolme strategista suuntaa), ne esitetään rinnakkaisina elementteinä, ei toisistaan riippuvana vaiheittaisena ketjuna. Säännön vaatimaa rakennetta ei löydy.  [5. VALIDATION DECISION: PASS]*

---

