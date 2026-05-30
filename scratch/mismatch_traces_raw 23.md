# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 94.62 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.8922
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.8922
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.0538
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 10 kpl
- **PASSED -> FAILED:** 7
- **FAILED -> PASSED:** 3
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_aa54c6b40e9c4160` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph containing statistical or factual reporting. STEP 2: Count the first-person pronouns ('I', 'we') or explicit self-reflective verbs ('assume', 'interpret'). EXTRACTION CONDITION: the count is exactly 0. NEGATIVE CONDITION (RETURN NULL IF MET): greater than 0. <ambiguity_protocol>ABSOLUTE ZERO ENFORCEMENT: The count of first-person references must be EXACTLY zero. You are strictly forbidden from ignoring possessive suffixes, bound morphemes, verb inflections, or clitics that grammatically denote a first-person perspective in the source document's target language (e.g., the Finnish suffix '-mme' in 'yrityksemme' or verb inflection '-n' in 'oletan'). If any such morpho-syntactic marker is found, the count is greater than zero, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [TRUE]:**
  > *This paragraph presents factual reporting based on the analysis of Sitra's reports. A scan of this specific paragraph shows that the count of first-person pronouns, self-reflective verbs, or possessive suffixes (like -ni, -mme) is exactly zero.*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [FALSE]:**
  > *The rule requires a count of exactly 0 for first-person references in a factual paragraph, with a strict negative condition for any count greater than 0. The concluding paragraph contains the word 'Yrityksemme' ('Our company'). The suffix '-mme' is a first-person plural possessive marker. As per the ambiguity protocol, this counts as a first-person reference, making the count greater than zero and triggering the negative condition.*

---

### Atom-ID: `tda_a383d38d1f47ce65` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EXTRACTION CONDITION: role prefixes exist, focus on the 'ai:' block. BANNED LOGIC: Do not evaluate 'opaque' subjectively. STEP 1 (Syntactic Anchor): Find a definitive conclusion or final answer (e.g. 'Therefore', 'The result is', 'In conclusion'). STEP 2 (Bounding Box): Scan the preceding text. NEGATIVE CONDITION (RETURN NULL IF MET): the conclusion is presented WITHOUT any preceding step-by-step mathematical, logical, or variable-level decomposition. If steps exist.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [TRUE]:**
  > *Presence detected: Parsing Log: 1. Syntactic anchor is a definitive conclusion marker like 'In conclusion'. 2. Localized anchor 'Johtopäätös' is found. 3. The rule requires the conclusion to be preceded by a step-by-step logical decomposition. 4. The text preceding the conclusion details three 'Supermegatrendit' with tables and three numbered points under 'Sitran Strateginen Suunta'. This constitutes a clear, multi-step logical decomposition leading to the conclusion. 5. Concluded with CONDITION MET.. Exceptions audit: Tämä on käänteinen sääntö, joka etsii puutetta. Sääntö ei täyty, koska `chat_log`-lähdettä tarkasteltaessa tekoälyn vastaukset rakentuvat vaiheittain. Esimerkiksi ensimmäinen vastaus erittelee megatrendit viiteen kohtaan, ja myöhemmät raporttiluonnokset perustuvat tähän erittelyyn. En löydä esimerkkiä, jossa johtopäätös esitettäisiin ilman edeltävää loogista erittelyä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii virhettä. Vaikka tekstissä on selkeä johtopäätös, se ei ole esitetty ilman edeltävää loogista purkua. Koko dokumentti rakentaa argumentaatiota vaiheittain (esim. supermegatrendien määrittely, niiden vaikutusten erittely taulukoissa, strategisen suunnan esittely), joka tukee lopullista johtopäätöstä. Koska perustelut ovat olemassa, säännön negatiivinen ehto täyttyy, eikä virhettä löydy.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_513d51a119ef4fd6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [FALSE]:**
  > *No presence of target concept detected: The text synthesizes Sitra's reports and presents causal links derived from them. It does not appear to make conclusions based on limited visible evidence while actively ignoring unknowns; rather, it operates entirely within the framework provided by its sources.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [TRUE]:**
  > *Presence detected: The text synthesizes Sitra's reports and presents causal links derived from them. It does not appear to make conclusions based on limited visible evidence while actively ignoring unknowns; rather, it operates entirely within the framework provided by its sources.. Exceptions audit: Sääntö etsii kausaalisia harppauksia tai päätelmiä, jotka perustuvat vain rajalliseen näkyvään todistusaineistoon (WYSIATI). Arvioitava teksti on synteesi ja analyysi nimetyistä ulkoisista lähteistä (Sitran raporteista), eikä se tee säännön kuvaamia perusteettomia loogisia hyppyjä. Ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b00e1f77f38317e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept post-decision doubt. STEP 1 (Syntactic Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the alternatives are explicitly compared and evaluated BEFORE the final decision is stated. NEGATIVE CONDITION (RETURN NULL IF MET): evaluated after.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [TRUE]:**
  > *Presence detected: Sääntö edellyttää, että vaihtoehtoja punnitaan eksplisiittisesti ennen lopullisen päätöksen tekemistä. Lähdeteksti ei esitä tällaista päätöksentekoprosessia. Se kuvaa historiallista kehitystä (2017 vs. 2023) ja esittää strategiset toimenpiteet välttämättöminä seurauksina, ei valintoina eri vaihtoehtojen välillä. Koska vaihtoehtojen punnintaa ennen päätöstä ei löydy, negatiivinen ehto täyttyy.. Exceptions audit: Sääntö vaatii, että vaihtoehtoja punnitaan ennen päätöksen tekemistä. Lähdeteksti on luonteeltaan analyyttinen yhteenveto, joka esittää johtopäätöksiä ja strategisia suuntia ilman, että se dokumentoi prosessia, jossa eri vaihtoehtoja olisi punnittu toisiaan vastaan.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että vaihtoehtoja punnitaan eksplisiittisesti ennen lopullisen päätöksen tekemistä. Lähdeteksti ei esitä tällaista päätöksentekoprosessia. Se kuvaa historiallista kehitystä (2017 vs. 2023) ja esittää strategiset toimenpiteet välttämättöminä seurauksina, ei valintoina eri vaihtoehtojen välillä. Koska vaihtoehtojen punnintaa ennen päätöstä ei löydy, negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6bf0433f60924302` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. Vague filler words.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [TRUE]:**
  > *Presence detected: The text does not use conditional qualifiers to define specific boundaries or probabilities for its claims. The arguments are presented in absolute and general terms rather than with specified conditions.. Exceptions audit: Tekstistä ei löydy ehdollisia määreitä, jotka asettaisivat rajoja tai todennäköisyyksiä esitetyille väitteille. Kielenkäyttö on pääosin absoluuttista ja varmaa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löydy ehdollistavia määreitä, kuten "näissä tietyissä olosuhteissa" tai "pääasiassa kun", jotka määrittelisivät väitteelle tarkkoja rajoja tai todennäköisyyksiä. Ehtoa ei täytetty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_3da456b757644c46` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept vague assertions like 'it is secure'. STEP 1 (Syntactic Anchor): Find explicit physical validation actions (e.g. 'validated', 'filtered', 'sanitized', 'checked against'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it describes a concrete data validation rule being applied to input or output.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä konkreettisia validointitoimia kuvaavia verbejä, kuten 'validoitu' tai 'suodatettu', eikä se kuvaa datan validointisääntöjen soveltamista. CONDITION NOT MET.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [TRUE]:**
  > *Presence detected: Sääntö etsii konkreettisia datan validointitoimia kuvaavia ilmauksia. Lähdeaineistosta ei löytynyt suoria semanttisia vastineita ankkureille, kuten 'validoitu' tai 'suodatettu', jotka kuvaisivat teknistä validointisääntöä.. Exceptions audit: The rule requires finding explicit physical validation actions like 'validated' or 'sanitized'. I scanned all source texts for such markers. The user's command 'varmista' in the chat log is a request for validation, not a description of a validation rule being applied. No description of a concrete data validation rule was found. CONDITION NOT MET.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b7ce46fc627dbc7e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find demands for epistemological humility (e.g., 'tell me what you do not know', 'what are the limitations of this analysis'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly commands the AI to state its uncertainties or missing data. Demands for absolute certainty.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [TRUE]:**
  > *Presence detected: The user never asks the AI to state its uncertainties, limitations, or what it does not know. All prompts are focused on generating, structuring, or refining content based on the provided context.. Exceptions audit: Sääntö etsii episteemisen nöyryyden vaatimuksia. Yksikään käyttäjän kehotus ei sisällä pyyntöä tekoälylle kertoa rajoituksistaan, epävarmuuksistaan tai siitä, mitä se ei tiedä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [FALSE]:**
  > *No presence of target concept detected: The user prompts in the chat log do not contain any explicit commands for the AI to state its uncertainties, limitations, or what it does not know. The user asks clarifying questions like "mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila" but does not probe for epistemic humility.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b7712f8a6c4619b4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept general 'secure' statements. STEP 1 (Syntactic Anchor): Find zero-trust markers (e.g. 'zero implicit trust', 'independent verification', 'cryptographic', 'strict boundary'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the processing demonstrates explicit zero-trust architecture where every input/output is treated as potentially hostile.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [FALSE]:**
  > *No presence of target concept detected: The text discusses security at a strategic level (e.g., 'kyberturvallisuus', 'tietosuoja') but does not contain the specific syntactic markers of a zero-trust architecture, such as 'zero implicit trust' or 'independent verification', as required by the rule.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [TRUE]:**
  > *Mitigating exception found: The text discusses trust from a social and brand perspective ('Luotamuskriisi') but does not contain any specific markers for a zero-trust security architecture, such as 'nollaluottamus' or 'riippumaton varmennus'. The security measures mentioned, like 'kyberturvallisuus', are too general to meet the condition.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_25973a87867690b7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find single-path commands (e.g., 'just write the final version', 'skip the analysis'). STEP 2 (Bounding Box): Scan the user prompt. EXTRACTION CONDITION: the user actively refuses to explore counter-arguments or alternative models. Do not accept if the user asks for pros and cons.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [TRUE]:**
  > *Mitigating exception found: Tämä on käänteinen sääntö. Ehto ei täyty, koska käyttäjä ei kieltäydy tutkimasta vaihtoehtoja. Päinvastoin, käyttäjä aktiivisesti ehdottaa uutta analyysimallia kysymällä "voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä", mikä on vastakohta yhden polun vaatimiselle. EHTO EI TÄYTTYNYT.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että käyttäjä aktiivisesti kieltäytyy tutkimasta vastaväitteitä tai vaihtoehtoisia malleja. Käyttäjä ei tee näin; päinvastoin, hän ehdottaa uutta vaihtoehtoista mallia ('supermegatrendit'), mikä on tutkimista, ei siitä kieltäytymistä. EHTO EI TÄYTY.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_03419e9a41f304ce` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_c33ae3606bc04a11a0666dc5c707c29f) - [TRUE]:**
  > *The text makes an absolute claim that the change is "peruuttamaton" (irreversible), which dismisses any alternative possibilities. The paragraph does not provide an external verifiable source or empirical data to support this absolute dismissal.*
- **Run 2 (exe_6ed75c9a3e164e3f8efbcba00a16530a) - [FALSE]:**
  > *This is an inverse rule. The rule requires finding dismissive markers towards alternatives. I scanned the text for Finnish equivalents of 'obviously false', 'nonsense', or 'irrelevant'. No such direct dismissive markers were found in the text. The text presents its conclusions assertively but does not explicitly name and then dismiss alternatives with the specified markers.*

---

