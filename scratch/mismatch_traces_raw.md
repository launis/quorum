# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 182
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 92.86 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.8450
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.0714
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 13 kpl
- **PASSED -> FAILED:** 2
- **FAILED -> PASSED:** 11
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_d204baf0bdf74ff7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find explicit boundary setting markers (e.g., 'this does not apply to', 'a key constraint is'). STEP 2: Document the constraint before extracting the exact_quote. EXTRACTION CONDITION: found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *Tekstistä ei löydy eksplisiittisiä, analyysin soveltamisalaa rajoittavia ilmauksia, kuten 'tämä ei koske' tai 'keskeinen rajoite on'. Vaikka kohderyhmä on määritelty, analyysi itse esitetään yleispätevänä.*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Teksti käyttää sanaa 'rajoite' viitatessaan luonnon kantokyvyn rajoihin. Vaikka se heti perään uudelleenmuotoilee rajoitteen mahdollisuudeksi, se ensin nimeää ja asettaa kyseisen rajan.*

---

### Atom-ID: `tda_d335b4457e3e4ac7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find thought-terminating clichés ('it is simply a matter of', 'there is no alternative', 'period'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: complexity or opposing views are dismissed without data. NEGATIVE CONDITION (RETURN NULL IF MET): data is provided. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Data-driven rebuttals. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *The text makes strong, conclusive statements, but these are presented as the outcome of the analysis of Sitra's reports. It does not use thought-terminating clichés to dismiss complexity without providing data.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *The text uses the phrase "paluuta vanhaan normaaliin ei ole" (there is no return to the old normal), which functions as a thought-terminating cliché, dismissing complexity and alternative views without presenting data in the same sentence.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_569f87a921a2fb69` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user instructions that modify an output (e.g., 'change this paragraph to'). STEP 2 (Bounding Box): Scan the interaction. EXTRACTION CONDITION: the user modifies the final output but leaves the original AI system prompt or generative logic exactly the same. NEGATIVE CONDITION (RETURN NULL IF MET): the user alters the underlying instructions/logic. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Deep structural refactoring. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *Negatiivinen ehto täyttyy, koska käyttäjä muuttaa perustavanlaatuisesti taustalla olevaa logiikkaa. Hän ei ainoastaan muokkaa tuotosta, vaan esittelee uuden käsitteellisen kehyksen ('supermegatrendejä').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Käyttäjä antaa selkeän komennon muuttaa tulosteen muotoa ('poista taulukot ja kerro ne tekstinä') muuttamatta alkuperäistä pyyntöä tai logiikkaa. Tämä on suora muokkaus olemassa olevaan tulosteeseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_32ee0cac79ad098e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *Teksti ei käytä universaaleja kvantifioijia, kuten 'aina' tai 'joka tapauksessa', soveltaakseen rajoitetusta kontekstista peräisin olevaa kausaaliväitettä yleismaailmallisesti. Siten säännössä kuvattua virhepäätelmää ei esiinny.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Tämä on käänteinen sääntö. Teksti tekee universaalin kausaaliväittämän, jonka mukaan tietty toiminto on 'ainoa tapa' saavuttaa haluttu lopputulos, mikä on säännön vastainen ylilyönti. Koska rikkomus löytyi, sääntöä ei ole noudatettu.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_823c84f71d94ce84` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept post-generation complaints. STEP 1 (Syntactic Anchor): Find a friction marker prior to an action (e.g. 'This is difficult because', 'The risk here is', 'We must balance'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the conflict or trade-off is articulated BEFORE the final output is generated. NEGATIVE CONDITION (RETURN NULL IF MET): the friction is only discussed afterwards. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [TRUE]:**
  > *The rule requires finding a friction marker articulated before an action. The reflection text contains the statement 'Ennakoin, että alkuun en saa hyvää tulosta' (I anticipated that I wouldn't get a good result at first), which clearly articulates anticipated difficulty before the main process, fulfilling the rule's condition.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [FALSE]:**
  > *Sääntö edellyttää, että konflikti tai kompromissi artikuloidaan ennen toimintaa. Käyttäjän kehotteet ovat suoria käskyjä, eikä keskustelulokissa ole näyttöä siitä, että käyttäjä olisi pohtinut tai ilmaissut mahdollisia vaikeuksia tai riskejä etukäteen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c74c4367acc028cf` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user phrases adopting AI methodology blindly (e.g., 'let us use your structure', 'proceed with that approach', 'do what you suggested'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly adopts the AI's proposed framework without adding their own constraints. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user modifies the AI's framework. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *Käyttäjä ei omaksu sokeasti tekoälyn metodologiaa. Päinvastoin, hän hylkää tekoälyn alkuperäisen rakenteen ja esittää oman, uuden kehyksensä ('supermegatrendit').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Kun tekoäly ehdottaa supermegatrendien käsitettä, käyttäjä omaksuu tämän viitekehyksen suoraan ja käskee tekoälyä tuottamaan raportin sen pohjalta. Tämä on selkeä esimerkki tekoälyn ehdottaman metodologian omaksumisesta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8f668ea29869ba8b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *This is an inverse rule that triggers if an evaluation of an outcome omits any mention of failures or limitations. The reflection text explicitly mentions limitations and corrections made ('Korjasin taulukosta Eurooppaan liittyvän asian...'). Since limitations are discussed, the condition for finding a violation is not met.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Sääntö on käänteinen ja etsii yksipuolista arviota onnistumisesta. Reflektiossa käyttäjä toteaa: 'Pyysin supermegatrendejä – tämä oli iso oivallus.' Tämä on selkeä arvio oman toiminnan onnistumisesta. Ympäröivä teksti ei mainitse mitään rajoituksia tai negatiivisia puolia tälle oivallukselle, joten arvio on yksipuolinen ja sääntöä on rikottu.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_5c82ad4f766b762e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find superficial correction commands by the user (e.g., 'fix the typo', 'make it shorter', 'bold the headers'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user ONLY requests formatting or minor lexical changes without challenging the logic. NEGATIVE CONDITION (RETURN NULL IF MET): logical changes are requested. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user challenges the underlying reasoning. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *Negatiivinen ehto täyttyy, koska käyttäjä ei *ainoastaan* pyydä pinnallisia korjauksia. Hän tekee myös merkittäviä loogisia ja rakenteellisia muutoksia, kuten uuden 'supermegatrendit'-käsitteen käyttöönoton.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Käyttäjä pyytää tekoälyä tarkistamaan muotoilun ('varmista, että taulukot ovat kohdallaan') ilman, että hän haastaa sisältöä tai logiikkaa. Tämä on puhtaasti pinnallinen korjauspyyntö.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_be74d9af83716dcc` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in a 'user:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'ai:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit retrospective claims of intent (e.g., 'That is what I meant', 'I intended', 'As expected'). STEP 2 (Bounding Box & Negative Condition): Scan the text preceding this claim (the original instruction). If the preceding text DOES NOT physically contain the exact parameters now being claimed -> ACCEPT. If the preceding text physically contains the parameters -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'sincerity' or 'post-hoc rationalization'. Evaluate only the physical presence or absence of the claimed parameters in the prior text. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *This is an inverse rule that looks for post-hoc rationalization. The user reflects on their insight to ask for 'supermegatrendejä'. The chat log confirms the user did introduce this term in their prompt. According to the rule, if the preceding text contains the claimed parameter, the condition for a violation is not met ('REJECT'). Therefore, no violation is found.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Sääntö on käänteinen ja etsii jälkikäteistä rationalisointia. Reflektiossa käyttäjä väittää: 'Annoin rajoituksia sekä roolin liiketoiminnalle koska kyse oli johtoryhmän tehtävästä' heti alussa. Keskusteluloki kuitenkin osoittaa, että ensimmäinen kehotus oli yleinen, ja rooli sekä kaupallinen näkökulma lisättiin vasta viimeisessä kehotteessa. Tämä on selvä tapaus, jossa alkuperäinen tarkoitus esitetään takautuvasti erilaiseksi kuin se oli, joten sääntöä on rikottu.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b1717b2ca9f25e2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Syntactic Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: EXTRACTION CONDITION: the command lacks any specific constraints and allows the AI to freely decide what is important. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *The user does not use broad, unconstrained summary commands like 'tiivistä' or 'tee yhteenveto'. The command 'koosta' is used, but it is accompanied by a specific constraint ("1 sivun").  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *The user's initial prompt is a very broad request for synthesis ('Miten sitra tämän näkee'), lacking any specific constraints on length, format, or focus, thus allowing the AI to freely decide what is important.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2590fb7ecb6379e7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate nuance. STEP 1 (Syntactic Anchor): Find absolute causal words ('only reason', 'entirely due to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text attributes a highly complex outcome to a single cause without acknowledging any other potential factors. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [TRUE]:**
  > *Teksti sisältää absoluuttisen kausaaliväittämän, jossa monimutkainen lopputulos ('pitkän aikavälin vakaus') johdetaan yhdestä ainoasta syystä ('Korjaavaan ja uusintavaan talouteen siirtyminen'). Tämä vastaa säännön ehtoa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [FALSE]:**
  > *Tämä on käänteinen sääntö. Teksti ei syyllisty yksinkertaistavaan yhden syyn selitykseen, vaan korostaa megatrendien kietoutumista toisiinsa. Koska rikkomusta ei löydy, sääntö on täytetty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_58cbd7271f491351` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find framework absolutism words (e.g., 'proves unequivocally', 'the model dictates', 'undeniable', 'certainty'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolutism anchor BUT does NOT contain mitigating vocabulary (e.g., 'however', 'potential limit', 'constraint', 'lens', 'maybe') -> ACCEPT. If it contains mitigating vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'infallible truth', or epistemological humility subjectively. Do not accept mathematical proofs. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *Sääntöä ei rikottu. Teksti ei käytä absoluuttisia ankkurisanoja, kuten 'todistaa kiistatta' tai 'kiistaton'. Sen sijaan se attribuoi näkemykset selkeästi Sitralle ('Sitran näkemys on...'), mikä toimii lieventävänä tekijänä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Sääntö etsii virhettä, jossa viitekehyksestä johdettu väite esitetään absoluuttisena totuutena ilman lieventävää sanastoa. Johtopäätöksessä väite 'Muutos... on peruuttamaton' on absoluuttinen ja lopullinen. Kappaleessa ei ole mukana mitään epävarmuutta tai rajoituksia ilmentäviä sanoja (kuten 'kuitenkin', 'mahdollisesti'), joten se rikkoo sääntöä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_9ab273ce743ac29e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess intent. STEP 1 (Syntactic Anchor): Find an evaluation of success or a positive outcome. STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text details the positive outcome but COMPLETELY OMITs any epistemic boundary markers (e.g. 'however', 'limitations', 'failed to', 'uncertainty'). NEGATIVE CONDITION (RETURN NULL IF MET): limitations are explicitly stated. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3fd8226676154108a50a644f621ad7fe) - [FALSE]:**
  > *Sääntö on käänteinen (pahe), joka etsii rajojen poisjättämistä. Lähdeteksti on kuitenkin täynnä rajoituksia ja epävarmuuksia kuvaavia termejä ('ennakoimatomia katkoja', 'maineriskin', 'luottamuksen rapautuminen', 'kysynnän epävarmuutta'). Koska rajoitukset on eksplisiittisesti mainittu, säännön negatiivinen ehto täyttyy, eikä rikkomusta löydy. Siksi sääntö on täytetty (rule_satisfied = True).  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_50cc66ec4ee84fd38398d71170dc3fe0) - [TRUE]:**
  > *Tämä on käänteinen sääntö, joka etsii positiivisen lopputuloksen kuvausta, josta puuttuvat kaikki episteemiset rajamarkkerit. Teksti esittää väitteen "Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus" absoluuttisena totuutena ilman mitään rajoituksia tai epävarmuuden tunnustamista. Tämä on säännön rikkomus.  [5. VALIDATION DECISION: PASS]*

---

