# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 89.25 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.7745
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.7745
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1075
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 20 kpl
- **PASSED -> FAILED:** 9
- **FAILED -> PASSED:** 11
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_72d84ac4a1f440d5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not flag caveats that result in a mathematically or conceptually altered conclusion. STEP 1 (Syntactic Anchor): Find concessive conjunctions (e.g., 'while it is true that', 'although X fails'). STEP 2 (Bounding Box): Scan the sentence. If the concession is immediately followed by a return to the original unmodified premise (e.g., '..ultimately it holds'). Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii myönnytystä, jota seuraa välitön paluu alkuperäiseen väitteeseen. Tekoäly myöntää riskin olemassaolon ('Riski on olemassa'), mutta välittömästi rajaa sen koskemaan muita kuin käyttäjän tilannetta ('mutta: koskee eniten: massaluentoja...'), mikä palauttaa keskustelun alkuperäiseen, muokkaamattomaan premissiin, jonka mukaan uhka ei ole merkittävä käyttäjälle.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö. Tekstistä ei löytynyt selkeää esimerkkiä, jossa myönnytyksen jälkeen palattaisiin täysin muuttumattomaan alkuperäiseen oletukseen. Tekoäly tyypillisesti käyttää myönnytyksiä tarkentamaan tai kvalifioimaan väitettään, ei kumoamaan niitä ja palaamaan alkuperäiseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_545bffdc85a31f0e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Reject superficial mentions of frameworks. STEP 1 (Syntactic Anchor): Find exact framework citations (e.g. 'OWASP LLM01', 'NIST', 'ISO 27001'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the specific framework clause is directly linked to the physical security action taken.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Mitigating exception found: Säännön syntaktisia ankkureita (esim. 'OWASP LLM01', 'NIST', 'ISO 27001') ei löytynyt lähdetekstistä. Keskustelussa ei viitata mihinkään tietoturvakehykseen.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii tarkkoja viittauksia tietoturvakehyksiin (esim. OWASP LLM01). Vaikka tekoäly viittaa akateemisiin malleihin, se ei viittaa mihinkään tietoturvastandardiin tai sen spesifiin lausekkeeseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_da500772aaf386b2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept simple disagreements. STEP 1 (Syntactic Anchor): Find override phrases ('olet väärässä', 'tämä logiikka ontuu', 'faktojen vastainen', 'kumottu', 'incorrect', 'you are wrong'). STEP 2 (Bounding Box): Scan the sequence. EXTRACTION CONDITION: the user rejects the AI's reasoning and injects their own superior logical or empirical correction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: I scanned all user prompts for phrases that would indicate a direct override of the AI's logic, such as 'olet väärässä' or 'tämä logiikka ontuu'. The user's interaction style is collaborative and refining; they do not reject the AI's reasoning but rather ask for it to be deepened or viewed from another angle. No direct logical override was found.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä haastaa suoraan tekoälyn esittämien väitteiden (prosenttiluvut) empiirisen perustan. Kysymys "Mihin tietoon perustuvat nämä prosenttiluvut?" toimii loogisena korjauksena, joka kumoaa perustelemattoman tiedon ja vaatii todisteita.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fbd90f9c0f2247ed` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit counterargument markers (e.g., 'critics argue', 'opposing view', 'counterargument', 'on the other hand'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the counterargument marker AND ALSO contains physical citation markers (e.g., 'et al', '[1]', '(', 'published in') AND empirical measurement vocabulary (e.g., 'data', 'showed', 'measured') -> ACCEPT. If it lacks citations or measurement tokens -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'strength', 'steel-manning', or whether the argument is successfully 'dismantled'. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt vasta-argumenttia, joka täyttäisi samanaikaisesti kaikki säännön tiukat ehdot: vasta-argumentin esittämisen, fyysisen viittausmerkin (kuten sulkeet tai linkin) ja empiirisen mittaussanaston (kuten 'data', 'näytti', 'mitattiin'). Vaikka tekoäly esittää riskejä ja viittaa lähteisiin, nämä kohdat eivät täytä kaikkia ehtoja samassa kappaleessa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii vasta-argumenttia, joka sisältää viittausmerkkejä ja empiiristä sanastoa. Tekstissä esitetään "Riski: ajattelun heikkeneminen ja riippuvuus", joka toimii vastakkaisena näkemyksenä. Tämä riski perustellaan viittauksella "Tecnológico de Monterrey Observatory". Vaikka tarkkoja mittaussanoja kuten 'osoitti' ei käytetä, lähteen mainitseminen vastakkaisen näkemyksen tukena täyttää säännön ehdot.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_aa3c4095c3a3fe82` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find exclusionary solution markers (e.g., 'the only solution', 'there is no other way'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a single method is pushed without mentioning any alternatives. Do not accept solutions that have explicitly evaluated and dismissed alternatives with data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Presence detected: Sääntö ei täyty (virhe löydetty). Lause esittää yhden polun (tekoälyn käyttö) ainoana tapana välttää korvatuksi tuleminen, mainitsematta tai arvioimatta vaihtoehtoja dataan perustuen. Tämä on poissulkeva ratkaisuehdotus.. Exceptions audit: Sääntö on käänteinen virhesääntö. Tekstissä ei esitetä yksittäistä ratkaisua ainoana vaihtoehtona. Sen sijaan tekoäly tarjoaa suosituksia ja erilaisia näkökulmia, eikä käytä poissulkevaa kieltä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löydy poissulkevia ratkaisumarkkereita, kuten 'ainoa ratkaisu'. Tekoäly esittää suosituksia ja tarjoaa käyttäjälle usein vaihtoehtoja, joten virhesäännön ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c59639ea92894862` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find anecdotal markers ('I once saw', 'in my experience', 'some people say'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: an anecdote is used to justify a systemic rule or broad policy. NEGATIVE CONDITION (RETURN NULL IF MET): it's just a personal story without broad policy claims. Do not flag rigorous case studies.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: The text does not contain anecdotal markers used to justify a systemic rule or broad policy. The AI's language is consistently analytical and does not rely on personal stories as evidence.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Teksti käyttää henkilökohtaista kokemusta ('Omassa opetuksessa') yleisen säännön tai mallin ('opiskelijat jakautuvat tyypillisesti kolmeen ryhmään') perustelemiseen. Tämä vastaa säännön ehtoa anekdootin käytöstä laajemman politiikan tai säännön oikeuttamiseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_58cbd7271f491351` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing absolute declarations (e.g., 'proves unequivocally', 'the model dictates', 'undeniable', 'certainty') into List A. Extract exact quotes containing mitigating words or constraints (e.g., 'however', 'potential limit', 'constraint', 'lens', 'maybe') into List B.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Presence detected: Sääntö ei täyty (virhe löydetty). Teksti esittää absoluuttisen tuomion ('Tekoäly ei ole uhka opetukselle. Se on stressitesti opetuksen laadulle.') ilman, että samassa kappaleessa olisi tasapainottavaa tai lieventävää sanastoa (kuten 'kuitenkin', 'vaikka').. Exceptions audit: Sääntö on käänteinen virhesääntö. Teksti sisältää runsaasti tasapainottavia ja lieventäviä ilmauksia ('mutta', 'osittain totta', 'riski on olemassa') eikä nojaa pelkkiin absoluuttisiin julistuksiin. Tämän vuoksi virhettä ei esiinny.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei esiinny rajoittamattomia absoluuttisia väittämiä. Tekoäly käyttää johdonmukaisesti lieventäviä ja ehdollisia ilmauksia ('mutta', 'osittain', 'jos') ja myöntää avoimesti väitteidensä rajat, joten virhesäännön ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b1bcf8b0c203b736` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user commands focused on tone (e.g., 'make it sound more persuasive', 'make it more academic'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user focuses solely on the performativity (tone/style) while ignoring substantive factual gaps. Revisions containing factual additions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei keskity ainoastaan tyyliin. Kun hän pyytää muutoksia, ne liittyvät sisältöön ja strategiaan ("Tee strategisempi, vältä geneerisyyttä ja lisää konkretiaa"), eivät pelkkään performatiivisuuteen.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä ei keskity pelkästään performatiivisuuteen. Kehote 'Tee strategisempi' on yhdistetty substanssia koskeviin pyyntöihin ('vältä geneerisyyttä ja lisää konkretiaa'), joten sääntö, joka edellyttää *yksinomaan* tyyliin keskittymistä, ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_55dfd9cb0adec620` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Mitigating exception found: Tämä on käänteinen sääntö. Tekstissä tunnistetaan riskejä, mutta niihin myös ehdotetaan aina pedagogisia ratkaisuja, joten riskejä ei jätetä ilman toimenpiteitä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö (vice rule). Vaikka tekoäly tunnistaa useita riskejä (esim. 'kriittisen ajattelun heikkeneminen', 'näennäinen osaaminen lisääntyy'), se ehdottaa johdonmukaisesti konkreettisia lievennyskeinoja jokaiseen. Esimerkiksi se ehdottaa tehtävien ja arvioinnin muuttamista. Yhtään riskiä ei tunnisteta ilman, että siihen tarjotaan ratkaisua.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_32ee0cac79ad098e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei esitä universaaleja kausaalisia väitteitä. Kun universaaleja termejä käytetään (esim. 'Kaikki opetus siirtyy tekoälylle'), ne esitetään osana tarinoita tai myyttejä, jotka tekoäly sitten analysoi ja purkaa osiin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Presence detected: Teksti tekee universaalin väitteen ("kaikki näyttää samalta") suorana seurauksena tekoälyn käytöstä markkinointisisällön tuottamisessa, soveltaen tiettyä havaintoa yleisesti ilman poikkeusten tunnustamista.. Exceptions audit: Teksti ei sisällä universaaleja kausaalisia väittämiä, jotka yleistäisivät rajoitetusta kontekstista peräisin olevan havainnon. Päinvastoin, se usein rajaa väitteensä tiettyihin konteksteihin, kuten yrittäjyyden opetukseen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d8bdf091d22d4412` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE: IDENTIFY the baseline presence of explicit partial consensus among agents. Look for lexical markers like 'mostly agree', 'general consensus', or 'aligns' in the native language.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Mitigating exception found: Ilmaus "osittain totta" on suora semanttinen vastine osittaiselle konsensukselle, jossa myönnetään yhden näkökulman (tarinan) osittainen validiteetti, mutta ei täyttä hyväksyntää.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii merkkejä osittaisesta konsensuksesta agenttien välillä. Koska lähdeteksti on dialogi yhden käyttäjän ja yhden tekoälyagentin välillä, useiden agenttien välistä konsensusta ei voi muodostua. Tekstistä ei löydy vaadittuja kielellisiä ankkureita.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_50d614006cd53384` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit absolute status declarations (e.g., 'perfectly secure', 'no issues found', 'fully compliant'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute declaration BUT does NOT contain risk or mitigation vocabulary (e.g., 'risk', 'trade-off', 'vulnerability', 'however') -> ACCEPT. If it contains risk vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'sweeping nature', or subjective 'flawlessness'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii absoluuttisia tilannekuvauksia (esim. 'täysin vaatimustenmukainen') ilman riskejä tai lieventäviä tekijöitä samassa kappaleessa. Lähdeteksti ei sisällä tällaisia kvalifioimattomia, absoluuttisia väitteitä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Presence detected: Sääntö etsii absoluuttisia tilaväittämiä (esim. 'täysin valmis') kappaleista, joista puuttuu riskitermistöä. Vaikka tekstissä on ilmauksia kuten 'valmis sisältö', ne eivät ole säännön tarkoittamia absoluuttisia tilan julistuksia vaatimustenmukaisuudesta tai turvallisuudesta. Lisäksi tekoälyn vastausten yleinen sävy on vivahteikas ja sisältää jatkuvasti pohdintaa riskeistä ja mahdollisuuksista, joten negatiivinen ehto (riskisanojen puuttuminen) ei täyty.. Exceptions audit: Tekstistä ei löydy kappaletta, jossa esitettäisiin absoluuttinen tilannearvio (esim. 'täysin vaatimustenmukainen') ilman, että samassa kappaleessa olisi myös riskeihin tai lieventäviin tekijöihin viittaavaa sanastoa (esim. 'mutta', 'riski'). Tekoälyn vastaustyyli on kauttaaltaan tasapainotteleva ja vivahteikas.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2ca8b77ba2dd43ad` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept explicit hypothesis testing. STEP 1 (Syntactic Anchor): Find descriptive reporting verbs (e.g., 'the data shows', 'we observed', 'indicates'). STEP 2 (Bounding Box): Scan the paragraph. If the observation lacks a formulated hypothesis that could be tested or disproven (e.g. no 'if X then Y' structure). Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kuvailevaa havaintoa, josta puuttuu testattava hypoteesi. Tekoäly esittää tutkimuslöydöksen ('Keskeinen löydös: 88 % opiskelijoista käyttää tekoälyä...'), mutta ei muotoile tästä havainnosta uutta, testattavaa 'jos X niin Y' -tyyppistä hypoteesia, vaan käyttää sitä tukemaan olemassa olevaa argumenttiaan.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Vaikka tekoäly viittaa tutkimuksiin ja niiden löydöksiin (esim. 'Keskeinen löydös: 88 % opiskelijoista käyttää...'), se raportoi muiden tekemiä havaintoja. Se ei itse esitä havaintoa muodossa 'minä havaitsin' tai 'data osoittaa' omasta analyysistään, jolta puuttuisi hypoteesi. Siksi sääntö ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8af3c72c0b5d4bfe` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find implicit authority markers (e.g., 'it is common knowledge', 'we always do it this way', 'internally known'). STEP 2 (Bounding Box): Scan the sentence. If a procedural rule is justified solely by internal tradition without citing an external verifiable standard (ARMA Transparency violation). Do not accept explicit external citations.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Presence detected: Sääntö on käänteinen (pahe). Etsin sääntöjä, jotka perustellaan sisäisellä perinteellä ('teemme aina näin'). Tekoäly toimii ulkoisena asiantuntijana ja perustelee väitteensä ulkoisilla periaatteilla, ei sisäisillä tavoilla.. Exceptions audit: Sääntö on käänteinen sääntö, joka etsii menettelytapasääntöä, joka perustellaan ainoastaan sisäisellä perinteellä tai implisiittisellä auktoriteetilla (esim. 'on yleisesti tiedossa') ilman ulkoista viittausta. Lähdetekstissä tekoäly toimii ulkoisena asiantuntijana ja perustelee väitteensä logiikalla tai myöhemmin ulkoisilla malleilla ja tutkimuksilla. Tekstistä ei löydy sääntöjä, jotka perusteltaisiin vetoamalla perinteeseen tai 'yleiseen tietoon'.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii perusteluja, jotka nojaavat implisiittiseen auktoriteettiin tai perinteeseen ilman ulkoista viitettä. Tekoäly ei käytä tällaisia perusteluja, vaan pyrkii loogiseen argumentaatioon tai viittaa ulkoisiin malleihin ja tutkimuksiin. Se jopa selventää, että sen antamat prosenttiluvut ovat 'kokemusperäisiä arvioita', mikä on päinvastaista kuin vedota implisiittiseen auktoriteettiin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b9199261d997ad2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find a counterfactual scenario (e.g. 'What if', 'Alternatively', 'Had we used'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the scenario is systematically dismantled with specific data points or mathematical proofs to validate the primary conclusion. NEGATIVE CONDITION (RETURN NULL IF MET): it is merely mentioned without data-driven refutation.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt yhtään kontrafaktuaalista skenaariota (esim. 'Mitä jos...'), jota olisi systemaattisesti analysoitu tai kumottu datalla tai matemaattisilla todisteilla. Tekstissä käsitellään riskejä ja tulevaisuudenkuvia, mutta ei säännön edellyttämällä tavalla.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Presence detected: Sääntö etsii kontrafaktuaalista skenaariota, joka kumotaan systemaattisesti datalla. Tekoäly esittää oman aiemman ajattelunsa ('Aiempi ajatus (ennen tutkimuksia)') kontrafaktuaalina ja kumoaa sen viittaamalla aiemmin esittämiinsä tutkimuksiin ('Tutkimusten jälkeen (tarkennettu näkemys)'), jotka toimivat dataperusteisena todisteena.. Exceptions audit: Lähdetekstissä on vastaehdollisia skenaarioita, kuten "Mitä tapahtuu, jos ei tehdä muutosta". Näitä skenaarioita ei kuitenkaan pureta systemaattisesti datalla tai matemaattisilla todisteilla, vaan niihin vastataan laadullisilla seurauksilla. Siksi sääntö ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_86bd73202db64e04` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept legitimate, statistically proven outlier exclusions (e.g., p-value tests). STEP 1 (Syntactic Anchor): Find dismissal markers (e.g., 'doesn\'t really count', 'is an anomaly', 'was an exception', 'however, generally'). STEP 2 (Bounding Box): Scan the paragraph. If these markers are used to protect the original premise from contradictory data without changing the premise. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii hylkääviä markkereita, joilla suojellaan väitettä vasta-argumenteilta. Tekoäly myöntää riskin olemassaolon, mutta käyttää 'mutta'-sanaa ja rajaa riskin koskemaan vain tiettyjä opetuksen muotoja. Tämä toimii retorisena keinona, jolla väitteen vastainen data (opettajia voidaan vähentää) sivuutetaan epärelevanttina käyttäjän kontekstissa, suojellen näin alkuperäistä väitettä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö. Tekstistä ei löytynyt säännön määrittelemiä ankkureita, joilla olisi hylätty vasta-argumentti alkuperäisen premissin suojelemiseksi. Tekoäly pyrkii ennemmin kontekstualisoimaan ja selittämään poikkeamia tai riskejä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_a9bbdcc4d1bfc915` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit optimization commands for proxy metrics (e.g., 'maximize the score', 'increase the word count', 'make it sound professional'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user demands optimization of a surface metric without linking it to a qualitative real-world outcome. Do not accept if the metric is explicitly tied back to a measure of effectiveness.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei pyydä pintapuolisten mittareiden optimointia. Päinvastoin, hän pyytää lisää syvyyttä ja konkretiaa ("Tee strategisempi, vältä geneerisyyttä ja lisää konkretiaa"), mikä on vastakohta säännön kuvaamalle haitalliselle käytökselle.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjän pyynnöt optimoida tuotosta (esim. "Tee strategisempi, vältä geneerisyyttä ja lisää konkretiaa") ovat suoraan sidoksissa edellisessä vaiheessa tunnistettuun laadulliseen tavoitteeseen: vakuuttaa esihenkilö. Koska pyyntö on sidottu laadulliseen lopputulokseen, se ei täytä säännön ehtoa, jonka mukaan linkitystä ei saa olla.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_4956abf072945f43` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Syntactic Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context. NEGATIVE CONDITION (RETURN NULL IF MET): the alternative is dismissed without evidence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstissä viitataan akateemisiin malleihin (esim. 'Diffusion of Innovations', 'UTAUT-mallit'). Näitä malleja ei kuitenkaan pureta tai kumota datalla tai logiikalla, vaan niitä käytetään tukemaan tekoälyn omaa argumentaatiota.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kohtaa, jossa vakiintunut vaihtoehtoinen malli puretaan datan tai loogisten ristiriitojen avulla. Tekoälyn toisessa vastauksessa esitellään yleinen pelko tai 'tarina' vaihtoehtoisena mallina: 'Tekoäly korvaa opettajat kokonaan'. Tämän jälkeen 'Todellisuus:'-osiossa tekoäly kumoaa tämän mallin loogisella ristiriidalla todeten, että tekoäly voi jakaa tietoa, mutta se ei pysty suorittamaan keskeisiä inhimillisiä opettajan tehtäviä, kuten johtamaan oppimista tai rakentamaan motivaatiota. Tämä täyttää säännön ehdot.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_44fd8d7101a84a48` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate completeness. STEP 1 (Syntactic Anchor): Find a primary proposal or argument. STEP 2 (Bounding Box): Scan the entire document. EXTRACTION CONDITION: alternative hypotheses or competing theories are completely absent from the text. NEGATIVE CONDITION (RETURN NULL IF MET): at least one competing alternative is analyzed.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen (vice rule). Teksti ei sisällä vaihtoehtoisten hypoteesien puuttumista. Päinvastoin, koko keskustelu rakentuu ensisijaisen ehdotuksen (opettajan rooli muuttuu) ja vaihtoehtoisen hypoteesin (tekoäly korvaa opettajat) väliselle vertailulle. Tekoäly analysoi useita "huolestuttavia tarinoita", jotka ovat kilpailevia teorioita, ja kumoaa ne järjestelmällisesti. Tämä täyttää negatiivisen ehdon, joten virhettä ei löydy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Tämä on pahe-sääntö. Teksti esittää yhden pääasiallisen argumentin – että tekoäly muuttaa opettajan roolia, ei korvaa sitä – ja käsittelee vastakkaisia näkemyksiä ainoastaan kumotakseen ne. Se ei analysoi vakavasti kilpailevia hypoteeseja (esim. skenaariota, jossa tekoäly korvaakin opettajat tietyillä aloilla), mikä täyttää säännön ehdon.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d335b4457e3e4ac7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find thought-terminating clichés ('it is simply a matter of', 'there is no alternative', 'period'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: complexity or opposing views are dismissed without data. NEGATIVE CONDITION (RETURN NULL IF MET): data is provided. Data-driven rebuttals.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4c88fc6a6243409db2c4f53fe02711ed) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä ajatuksia päättäviä kliseitä, joilla sivuutettaisiin monimutkaisuus tai vastakkaiset näkemykset ilman perusteluja. Vaikka tekoäly käyttää vahvoja ja tiivistettyjä lauseita, ne toimivat johtopäätöksinä aiemmin esitetylle analyysille, eivätkä ne ole perusteettomia väitteitä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_d3bbd15db5a649aaacccb9753c2fd8d5) - [TRUE]:**
  > *Mitigating exception found: Tekstistä ei löytynyt paikannettuja ankkureita vastaavia ajatuksen pysäyttäviä kliseitä. Tekoälyn argumentaatio pyrkii avaamaan monimutkaisuutta ja esittämään eri näkökulmia sen sijaan, että se sulkisi keskustelun.  [5. VALIDATION DECISION: PASS]*

---

