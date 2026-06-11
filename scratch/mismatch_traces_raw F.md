# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ajo-tiedot (Runs)
- **Run 1:** `exe_3a489bfb44cd498a950b5dadfc7f89ed` (Lähde: [data/files/executions\exe_3a489bfb44cd498a950b5dadfc7f89ed\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_3a489bfb44cd498a950b5dadfc7f89ed/execution_trace.json))
- **Run 2:** `exe_3f5380c3fdbb4a42b7dcfb21ed9664bb` (Lähde: [data/files/executions\exe_3f5380c3fdbb4a42b7dcfb21ed9664bb\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_3f5380c3fdbb4a42b7dcfb21ed9664bb/execution_trace.json))

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 182
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 80.77 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.4872
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.4979
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1923
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 35 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 0 / 35
- **PASSED -> FAILED:** 6
- **FAILED -> PASSED:** 29
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_10f455c36f754d33a3a551e9e7b61da4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find structural breakdown verbs (e.g., 'consists of', 'divided into', 'components', 'elements'). STEP 2: EXTRACTION CONDITION: a single overarching concept is explicitly split into at least two named sub-components. Do not accept simple bullet-point lists of unrelated features.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause 'Talousjärjestelmän vakauteen vaikuttavat kolme pääasiallista, toisiaan vahvistavaa supermegatrendiä:' jakaa selkeästi yhden yläkäsitteen (supermegatrendit) kolmeen nimettyyn alakomponenttiin, jotka esitetään välittömästi tämän jälkeen luettelomuodossa. Tämä vastaa säännön vaatimusta rakenteellisesta jaottelusta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_a935aa7d237849259142a2a8936bdec0` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EXTRACTION CONDITION: role prefixes exist, focus on the 'ai:' block. BANNED LOGIC: Do not evaluate 'opaque' subjectively. STEP 1 (Syntactic Anchor): Find a definitive conclusion or final answer (e.g. 'Therefore', 'The result is', 'In conclusion'). STEP 2 (Bounding Box): Scan the preceding text. NEGATIVE CONDITION (RETURN NULL IF MET): the conclusion is presented WITHOUT any preceding step-by-step mathematical, logical, or variable-level decomposition. If steps exist.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *AI:n vastauksessa 'Tiivistelmä'-osiossa esitetään johtopäätös ilman edeltävää vaiheittaista matemaattista, loogista tai muuttujatason hajotusta kyseisen tiivistelmälohkon sisällä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_bfbe65b639b54106913902d5bd0ae6ab` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find revelation markers (e.g., 'underlying this', 'the root cause is', 'fundamentally'). STEP 2: EXTRACTION CONDITION: the text identifies a mechanism or assumption that is not immediately visible on the surface. Do not accept superficial observations of visible symptoms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lähdetekstistä löytyi sana 'fundamentaalisen', joka vastaa englanninkielistä ankkuria 'fundamentally'. Lause kuvaa perustavanlaatuista siirtymää, joka on pinnan alla oleva mekanismi eikä pelkkä pinnallinen havainto.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6a779cd5e9714994b83168dd0fef0ef7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find application markers (e.g., 'in practice', 'applied to', 'for example', 'implemented'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: an abstract framework or rule is explicitly linked to a physical, real-world noun (e.g., a specific project, person, or physical action). Do not accept purely theoretical analogies without actionable context.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lauseessa 'Investoinnit kiertotalouden ratkaisuihin' sana 'Investoinnit' toimii sovellusmerkkinä, joka linkittää abstraktin käsitteen (kiertotalous) konkreettiseen, fyysiseen toimenpiteeseen (investoinnit ratkaisuihin). Tämä on ensimmäinen tällainen esiintymä `Product_Text`-osiossa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ac3b078498e048889ad3bc46b634c2ee` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find an academic citation, mathematical theorem, or academic framework. If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the sentence IF AND ONLY IF the logic is explicitly tethered to this source (e.g., actively applying a rule from the source).</step3_extraction_condition> <step4_fail_fast_protocol>If the source is just named or referenced passively without actively applying its logic, you MUST return JSON null.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lähdetekstissä on akateeminen viittaus 'Sitran Megatrendiraportit 2017, 2020, 2023'. Koko dokumentti on analyysi, joka perustuu ja viittaa aktiivisesti Sitran näkemyksiin ja raportteihin, mikä osoittaa logiikan olevan sidottu tähän lähteeseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_64cce5cf564a497dbbc2341248cea637` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find external citation markers (e.g., 'according to', 'study shows', 'metric [X]', 'perustuen'). STEP 2: EXTRACTION CONDITION: the logical deduction is strictly tied to a specific named methodology, framework, or external dataset. NEGATIVE CONDITION (RETURN NULL IF MET): it relies purely on internal logic.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Looginen päättely (koko raportin sisältö) on sidottu eksplisiittisesti nimettyyn ulkoiseen tietojoukkoon ('Sitran Megatrendiraportit') 'Viite'-merkinnällä, mikä täyttää ehdon.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_23df983a5c6e4eb9b8a28f2287267bd8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find explicit methodology links (e.g., 'in accordance with', 'following the protocol defined by'). STEP 2 (Bounding Box): Scan the sentence. If an action is explicitly linked to a named guideline or procedure (ARMA Compliance). Do not evaluate the 'quality' of the methodology. <disambiguation>
  Regulatory framework references count as formal citations ONLY if a 
  specific sub-article, clause, or numbered principle is cited (e.g., 
  "Article 29b(2)", "ISO 27001 §6.1.2"). Generic regulatory mentions 
  without sub-clause specificity DO NOT satisfy methodology link, benchmark, 
  formal citation, or security standard extraction conditions.
</disambiguation> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lähdetekstissä mainitaan 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset', jotka tekevät kestävyydestä pakollista. Tämä linkittää toiminnan (kestävyydestä pakollista) nimettyihin ohjeisiin/menettelyihin. Vaikka spesifistä artiklaa ei mainita, 'direktiivi' ja 'taksonomia' ovat nimettyjä ohjeita, jotka täyttävät ehdon 'named guideline or procedure'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_7d0ef5f0be004974801b53d2af317bbe` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find explicit rejection markers (e.g., 'Instead of following', 'I will create my own', 'I ignored'). STEP 2 (Bounding Box): Scan the sentence containing the marker. If the author explicitly states they are creating a new rule that contradicts the requested instructions. Do not evaluate 'quality' or if the new rule is better.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Käyttäjä ilmoittaa 'reflection_text'-osiossa korjanneensa taulukosta Eurooppaan liittyvän asian, koska näki sen tarpeettomana. Tämä on eksplisiittinen ilmoitus siitä, että käyttäjä on muuttanut tai jättänyt huomiotta alkuperäisen sisällön oman harkintansa perusteella, mikä täyttää 'explicit rejection markers' -ehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_654d4f29e9a045a0ad58566e3fc5f942` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate engagement quality. STEP 1 (Syntactic Anchor): Find an explicit counter-argument or risk raised in the text (e.g., 'Despite the risk', 'Opponents argue', 'Vaikka'). STEP 2 (Bounding Box): Scan the subsequent sentences. EXTRACTION CONDITION: the counter-argument is stated but not logically dismantled with data. NEGATIVE CONDITION (RETURN NULL IF MET): it is dismantled step-by-step. <disambiguation>
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
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Tekstissä esitetään eksplisiittinen riski ('vaikka haasteet ovat suuria'), mutta sitä ei pureta loogisesti datalla tai vaiheittaisella perustelulla. Sen sijaan esitetään mahdollisuus ('toisenlainen, reilu ja kestävä tulevaisuus on mahdollinen'), mikä täyttää ehdon, että vasta-argumentti esitetään mutta sitä ei pureta datalla.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b3c69e002634430ca9f2e2a33f7b280e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find synthesis verbs (e.g., 'design', 'formulate', 'invent', 'combining X and Y creates'). STEP 2: EXTRACTION CONDITION: the text explicitly merges at least two disparate elements into a completely new, named framework or solution. Do not accept mere combinations of existing ideas without a novel theoretical leap.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Teksti yhdistää eksplisiittisesti 'yksittäiset megatrendit' (erilliset elementit) 'kolmeksi keskeiseksi Supermegatrendiksi' (uusi, nimetty viitekehys), mikä täyttää synteesin ehdot ja edustaa teoreettista harppausta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0b7512034e6f40db9b4ea46b64af4e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Focus on 'user:' blocks EXTRACTION CONDITION: prefixes exist. Do not judge 'vagueness' subjectively. STEP 1 (Syntactic Anchor): Find a directive verb (e.g. 'Make', 'Improve', 'Change'). STEP 2 (Bounding Box): Scan the sentence containing the verb. NEGATIVE CONDITION (RETURN NULL IF MET): the sentence DOES NOT contain a measurable threshold, a specific framework name, or a quantifiable metric. If specific metrics exist.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Käyttäjän syötteestä 'user: näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan' löytyy direktiiviverbit 'näytä' ja 'varmista'. Lause ei sisällä mitattavaa kynnystä, spesifistä viitekehystä tai kvantifioitavaa mittaria. 'Taulukot ovat kohdallaan' on kvalitatiivinen ohje, joka täyttää ehdon 'DOES NOT contain a measurable threshold, a specific framework name, or a quantifiable metric'.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_90549a60a8dd4d029e6b6d23196ddf2f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE: EXTRACT a section where the final synthesis is explicitly tethered to verifiable references or source data, ensuring zero-trust compliance. Look for explicit citation markers like 'according to', 'as seen in', or 'referenced in' in the native language.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Teksti sisältää nimenomaisen viittauksen lähdetietoihin 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023', mikä sitoo synteesin todennettaviin lähteisiin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b03e802130ef46c781ff49c6a71d6ada` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find thought-terminating clichés ('it is simply a matter of', 'there is no alternative', 'period'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: complexity or opposing views are dismissed without data. NEGATIVE CONDITION (RETURN NULL IF MET): data is provided. Data-driven rebuttals.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' sisältää ilmaisun 'ainoa tapa', joka on ajatuksen päättävä klisee. Se esittää väitteen ainoasta vaihtoehdosta ilman, että samassa kontekstissa esitetään dataa tai dataan perustuvaa vastinetta muiden vaihtoehtojen kumoamiseksi. Tämä täyttää poimintaehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b36d3ec7b1f94fe9ad4b45795a8a104b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find a declarative verb (e.g., 'is', 'has', 'consists of'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the sentence states a standalone fact without explanatory conjunctions (e.g., 'because', 'therefore'). Do not accept sentences that attempt to explain the 'why' or 'how'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause sisältää deklaratiivisen verbin 'osoittaa' (shows/indicates), joka esittää itsenäisen tosiasian Sitran megatrendien kehityksestä. Lauseessa ei ole selittäviä konjunktioita (esim. 'koska', 'siksi'), jotka selittäisivät 'miksi' tai 'miten'.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_01edff70b75047ec9f6df0c49745f46e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries. <ambiguity_protocol>ABSOLUTE BOUNDARY ENFORCEMENT: You must check if the causal claim is bounded. If the sentence or immediate context contains explicit boundary-setting vocabulary, limitations, or environmental constraints (e.g., 'only under', 'in this scenario', 'limited to', 'primarily when', 'but may fail if', or Finnish equivalents like 'ainoastaan', 'rajattu', 'vain silloin kun'), the absolute overgeneralization is falsified, the boundary is acknowledged, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Teksti sisältää universaalin termin 'ainoa tapa', joka esittää kausaalisen väitteen ('taata pitkän aikavälin vakaus') ilman eksplisiittisiä rajauksia tai rajoituksia, mikä täyttää säännön rikkomuksen ehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_44793a48813843f0b48364e890eeba1e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept vague lists. STEP 1 (Syntactic Anchor): Find an explicit listing of factors or variables (e.g. 'Based on the following factors:', 'Variables considered:'). STEP 2 (Bounding Box): Scan the list. EXTRACTION CONDITION: at least two distinct variables or weights are physically defined in the text. NEGATIVE CONDITION (RETURN NULL IF MET): fewer than two are defined.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Tekstissä on eksplisiittinen listaus tekijöistä ('kolmeksi keskeiseksi Supermegatrendiksi'), ja sitä seuraa vähintään kaksi erillistä muuttujaa (Ekologinen Resilienssikriisi, Geoteknologinen Valtaistelu, Epävarmuuden Sosiaalinen Polarisointi), mikä täyttää ehdon 'at least two distinct variables or weights are physically defined in the text'.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c2968c987f1a4ac5824f15653df3dc8f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Tekstistä ei löytynyt vähätteleviä merkkejä vaihtoehtoja kohtaan (esim. 'ilmeisen väärä', 'hölynpölyä'), joita olisi käytetty ilman ulkoista lähdettä tai empiiristä dataa.*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.' sisältää vaihtoehtoja vähättelevän ilmauksen 'ainoa tapa'. Samassa kappaleessa ei ole esitetty ulkoista todennettavissa olevaa lähdettä tai empiiristä tietoa tämän absoluuttisen väitteen tueksi, mikä täyttää sääntörikkomuksen ehdon.*

---

### Atom-ID: `tda_5568f81c93bc4d1fb524fbfc1d9f0e04` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a proposal, claim, or argument. STEP 2: Check if the author actively refuses to consider alternative perspectives, or dogmatically declares their view as the single exclusive truth (e.g., using physical syntactic markers like 'there is no alternative', 'only option', 'is the only', 'ainoastaan', 'ainoa oikea', or explicit dismissal/exclusion of alternative options). EXTRACTION CONDITION: present. NEGATIVE CONDITION (RETURN NULL IF MET): absent. <ambiguity_protocol>ABSOLUTE EXCLUSION ENFORCEMENT: You must actively locate a sentence where the author explicitly dismisses alternative perspectives or dogmatically asserts exclusive truth. General one-sided arguments that merely lack alternatives DO NOT trigger this rule; there MUST be a physical marker of active refusal, dogmatic exclusivity, or explicit dismissal. If such a marker is absent, you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Teksti sisältää fyysisen syntaktisen merkin 'ainoa tapa', joka dogmaattisesti julistaa yhden näkemyksen ainoaksi totuudeksi ja poissulkee muut vaihtoehdot pitkän aikavälin vakauden takaamiseksi. Tämä vastaa täysin säännön vaatimusta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_4ba32055738247d28e00a597f505ce9e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find binary reduction markers (such as equivalents of 'either', 'or', 'simply boils down to', 'only way' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the quote IF the text uses these markers to force a complex situation into exactly one or two absolute options.</step3_extraction_condition> <step4_fail_fast_protocol>If the text acknowledges alternative paths, middle grounds, or nuance, you MUST return JSON null.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lauseessa käytetään ilmaisua 'ainoa tapa' pakottaen monimutkaisen tilanteen (taloudellinen vakaus) yhteen absoluuttiseen vaihtoehtoon (siirtyminen korjaavaan ja uusintavaan talouteen) ilman, että tunnustetaan vaihtoehtoisia polkuja tai vivahteita.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2d12f15e1c2d4488b7c2ef32d0ccfa26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause 'paluuta vanhaan normaaliin ei ole' ilmaisee absoluuttista varmuutta ('ei ole') ilman empiiristä dataa tai episteemisiä kvalifikaattoreita. Tämä on ensimmäinen kronologinen esiintymä absoluuttisen varmuuden merkistä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bd85f009b0fb4f7899b40ff0e763dee7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find tension markers between metrics and goals (such as equivalents of 'this metric is flawed because', 'the metric versus the actual goal' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the quote IF the user explicitly questions the reliability of a proxy metric in relation to the true qualitative goal.</step3_extraction_condition> <step4_fail_fast_protocol>If the text merely tracks a metric without questioning its validity, you MUST return JSON null.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Käyttäjä erottaa 'toivetilan' (mittari) 'suunnasta eteenpäin' (todellinen tavoite), kyseenalaistaen 'toivetilan' luotettavuuden todellisena ohjaavana tekijänä. Tämä ilmaisee jännitteen mittarin ja tavoitteen välillä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_1361cf5ec5b5420c905cd2a1f80893a7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find explicit retrospective claims of intent (such as equivalents of 'that is what I meant', 'I intended', 'my original goal was' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Target ONLY 'user:' blocks. Read the preceding instructions.</step2_bounding_box> <step3_extraction_condition>Extract the retrospective claim IF AND ONLY IF the preceding text DOES NOT physically contain the parameters being claimed.</step3_extraction_condition> <step4_fail_fast_protocol>If the prior text ALREADY contains the requested parameters (i.e. the user did actually ask for it earlier), you MUST return JSON null. We only extract false post-hoc rationalizations.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Käyttäjä esittää retrospektiivisen väitteen aikomuksestaan ('muuttelin yksityiskohtia', 'otin mielestäni asioita pois'), jota ei ole eksplisiittisesti pyydetty edeltävissä 'user:'-kehotteissa. Tämä täyttää ehdon 'false post-hoc rationalization' poiminnalle.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_4a8347422e464965a6e9206dcc240c26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. Vague filler words. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lauseessa 'menestyäkseen yritysten on panostettava tulevaisuusresilienssiin' sana 'menestyäkseen' (in order to succeed) toimii ehdollisena määreenä, joka selkeästi määrittelee ehdon tai rajan väitteelle 'yritysten on panostettava tulevaisuusresilienssiin'. Tämä ei ole epämääräinen täytesana, vaan eksplisiittinen ehto.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b110906545324d1f80bf3ec3b81b2b05` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find boundary or limitation markers (e.g., 'only applies to', 'limited to', 'under these conditions', 'except when'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the boundary marker BUT does NOT contain universal absolutes (e.g., 'always', 'universal', 'everyone', 'everywhere') -> ACCEPT. If it contains universal absolutes that contradict the boundary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'validity', or excuse missing context. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause sisältää rajamerkinnät 'rajat' ja 'rajoite'. Välittömässä kontekstissa ei ole universaaleja absoluutteja, jotka olisivat ristiriidassa tämän rajauksen kanssa. Siksi ehto täyttyy ja lause poimitaan.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_9fd2fff3ab4a46d29b5df31488561dd4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find demands for external grounding (e.g., 'cite a specific source', 'base this strictly on the provided document', 'give me the exact quote'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly restricts the AI to an external, objective anchor. Acceptance of unsourced hallucinated facts. NEGATIVE BOUNDARY: General questions or requests for explanation DO NOT count as external grounding unless they explicitly demand a citation or source material restriction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lause 'raporttien perusteella' on eksplisiittinen vaatimus ulkoiselle perustelulle, joka rajoittaa AI:n vastausta annettuihin lähteisiin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_216cc3fd45284deb8d51ea4cf2b2fd93` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find absolute words (e.g., 'always', 'never', 'everyone knows', 'fact'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the absolute claim is presented without any citations or stated limitations. Do not accept absolute statements that are mathematically proven or properly cited.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lähdetekstistä löytyi absoluuttinen ilmaisu 'ainoa tapa' ilman siihen liittyviä viittauksia tai rajoituksia, mikä täyttää säännön ehdot absoluuttisen väitteen osalta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_10dd47750c9244139c394ca875f160e6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. Do not evaluate the quality of the bridging rule.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lauseessa käytetään absoluuttista ilmaisua 'on ainoa tapa', joka toimii syntaktisena ankkurina. Se esittää yleisen säännön tai periaatteen (warrantin) siitä, miten pitkän aikavälin vakaus taataan, yhdistäen sen 'korjaavaan ja uusintavaan talouteen siirtymiseen'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b7dfe23403db4db5b92a29a8bda9957c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find generic listing conjunctions (e.g., 'and', 'also', 'in addition'). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the immediate sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the exact quote IF AND ONLY IF two nouns or noun phrases are joined by the conjunction WITHOUT any relational verb describing their interaction in the same sentence.</step3_extraction_condition> <step4_fail_fast_protocol>If ANY verb exists in the sentence that defines a causal or operational relationship between the two nouns, you MUST return JSON null. Verify only syntax, do not judge 'importance'.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Konjunktio 'ja' yhdistää kaksi substantiivilauseketta ('potentiaaleista' ja 'kehityskuluista') ilman, että samassa lauseessa on niiden välistä suhdetta kuvaavaa verbiä. Lauseen pääverbi 'osoittaa' viittaa laajempaan siirtymään, ei näiden kahden substantiivin väliseen suhteeseen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_686aaacdd96a4a5aa61634fc248527ef` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing absolute declarations (e.g., 'proves unequivocally', 'the model dictates', 'undeniable', 'certainty') into List A. Extract exact quotes containing mitigating words or constraints (e.g., 'however', 'potential limit', 'constraint', 'lens', 'maybe') into List B.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lauseessa 'Sitran näkemys on, että paluuta vanhaan normaaliin ei ole' esiintyy absoluuttinen ilmaus 'ei ole', joka vastaa englanninkielistä 'is not' tai 'there is no'. Tämä on ensimmäinen absoluuttinen ilmaus `Product_Text`-osiossa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0f797e820117411d9934418a1d5d0a82` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing user instructions to modify the final output (e.g., 'change this paragraph to') into List A. Extract exact quotes containing alterations to the underlying instructions or logic into List B. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Käyttäjä antaa suoran ohjeen muuttaa tulosteen muotoa ('poista taulukot ja kerro ne tekstinä'), mikä vastaa kriteeriä 'instructions to modify the final output'.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_65c125a7c28b4f8e9c33c8987ff52931` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find an absolute quantifier or declaration of certainty (e.g., 'always', 'undeniably', 'proven', 'fact', '100%'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute quantifier BUT does NOT contain empirical measurement tokens (e.g., 'data', 'measurement', 'study', 'statistics', 'survey') -> ACCEPT. If it contains empirical measurement tokens -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'agreement' or whether an assumption is being confirmed. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Löydettiin absoluuttinen varmuuden ilmaus 'paluuta vanhaan normaaliin ei ole' 'ai:'-lohkosta. Kappale ei sisältänyt empiirisiä mittaustermejä, joten ehdot täyttyivät.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_131403148eab4c739149e6bd29164ce2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find reformulation markers (e.g., 'in other words', 'this means', 'essentially'). STEP 2: EXTRACTION CONDITION: found, the author is paraphrasing. Do not accept verbatim copy-pasting of definitions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause 'Johtoryhmälle tämä tarkoittaa:' sisältää täsmällisen uudelleenmuotoilun merkin 'tämä tarkoittaa', joka selittää edellisen lauseen 'tulevaisuusresilienssin rakentamiseen' merkityksen kohderyhmälle. Tämä on suora osoitus parafrasoinnista.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_3b951170f9f54f649b7da95fb9f121e6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept explicit hypothesis testing. STEP 1 (Syntactic Anchor): Find descriptive reporting verbs (e.g., 'the data shows', 'we observed', 'indicates'). STEP 2 (Bounding Box): Scan the paragraph. If the observation lacks a formulated hypothesis that could be tested or disproven (e.g. no 'if X then Y' structure). Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lause sisältää kuvailevan raportointiverbin 'näkee' ja kuvaa tulevaisuuden tilaa ilman testattavaa hypoteesia, mikä täyttää ehdot.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_83c3a1f41fb94c8d802a60e00ad2550f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'proactivity' subjectively. STEP 1 (Syntactic Anchor): Find temporal reactive markers (e.g. 'after the failure', 'once identified', 'we fixed'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: security measures are ONLY described as post-incident responses without any pre-incident checks.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lauseessa kuvataan virheen havaitsemista ('Huomasin myös, että lähtötilanteessaa oli virhe') ja sen korjaamista ('Korjasin taulukosta Eurooppaan liittyvän asian'), mikä on reaktiivinen toimenpide. Tekstissä ei mainita ennakoivia tarkistuksia, jotka olisivat estäneet virheen alun perin, täyttäen ehdon, että turvatoimet kuvataan vain jälkikäteen tapahtuvina vastauksina.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bd90e5a66c5d433a9ed650f295132625` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'spurious'. STEP 1 (Syntactic Anchor): Find causal words (e.g. 'causes', 'because'). STEP 2 (Bounding Box): Scan the same sentence. EXTRACTION CONDITION: the causal claim is backed ONLY by a statistical correlation or simultaneous occurrence without any physical mechanism.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3f5380c3fdbb4a42b7dcfb21ed9664bb) - [TRUE]:**
  > *Lauseessa "mielenterveysongelmat lisääntyvät epävarmuuden keskellä" esitetään kausaaliväittämä (lisääntyvät), joka perustuu samanaikaiseen esiintymiseen ("epävarmuuden keskellä") ilman eksplisiittistä fyysistä mekanismia siitä, miten epävarmuus konkreettisesti aiheuttaa mielenterveysongelmien lisääntymisen. Tämä täyttää ehdon, että kausaaliväittämä perustuu *vain* tilastolliseen korrelaatioon tai samanaikaiseen esiintymiseen ilman fyysistä mekanismia.  [5. VALIDATION DECISION: FAIL]*

---

