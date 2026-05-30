# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 185
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 96.22 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.9239
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.9239
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.0378
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 7 kpl
- **PASSED -> FAILED:** 4
- **FAILED -> PASSED:** 3
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_0d8c983364b914ba` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate internal mental states. STEP 1 (Syntactic Anchor): Find epistemic boundary markers (e.g. 'may be inaccurate', 'verify independently', 'limitations', 'hallucination'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: there is a physical, explicit statement acknowledging the AI's limitations or a disclaimer.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b666529910ea404295aa6f8c8958260d) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii episteemisiä rajausmerkintöjä, jotka tunnustavat tekoälyn rajoitukset. Mistään lähdeaineiston osasta ei löytynyt vastuuvapauslausekkeita tai mainintoja mahdollisista epätarkkuuksista tai hallusinaatioista.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_15c6c7ce95044ec293f482a88afb11ae) - [FALSE]:**
  > *No presence of target concept detected: The source texts do not contain any explicit epistemic boundary markers, disclaimers, or acknowledgements of the AI's limitations, such as 'may be inaccurate' or 'verify independently'.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0f4ab5b3344ef1a8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'proactivity' subjectively. STEP 1 (Syntactic Anchor): Find temporal reactive markers (e.g. 'after the failure', 'once identified', 'we fixed'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: security measures are ONLY described as post-incident responses without any pre-incident checks.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b666529910ea404295aa6f8c8958260d) - [TRUE]:**
  > *Presence detected: This is a vice rule. The texts do not describe any security measures, so the condition that they are ONLY described as post-incident responses cannot be met. The user's content correction is not a security measure.. Exceptions audit: Sääntö etsii kuvauksia reaktiivisista turvatoimista, jotka tehdään vasta virheen jälkeen. Aineiston konteksti on liiketoimintastrategia ja megatrendit, eikä se käsittele tietoturvapoikkeamia tai niihin reagoimista.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_15c6c7ce95044ec293f482a88afb11ae) - [FALSE]:**
  > *No presence of target concept detected: This is a vice rule. The texts do not describe any security measures, so the condition that they are ONLY described as post-incident responses cannot be met. The user's content correction is not a security measure.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_50d614006cd53384` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit absolute status declarations (e.g., 'perfectly secure', 'no issues found', 'fully compliant'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute declaration BUT does NOT contain risk or mitigation vocabulary (e.g., 'risk', 'trade-off', 'vulnerability', 'however') -> ACCEPT. If it contains risk vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'sweeping nature', or subjective 'flawlessness'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b666529910ea404295aa6f8c8958260d) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä absoluuttisia tilannekuvauksia (kuten 'täysin vaatimustenmukainen') ilman riskisanastoa. Koko dokumentin sävy on riskeihin ja kriiseihin keskittyvä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_15c6c7ce95044ec293f482a88afb11ae) - [TRUE]:**
  > *Presence detected: Sääntö on pahesääntö, joka etsii absoluuttisia tilan julistuksia kappaleista, joista puuttuu riskienhallinnan sanastoa. Lause "Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton" on absoluuttinen julistus. Sitä ympäröivässä kappaleessa ei ole riskienhallintaan tai lieventämiseen viittaavia sanoja, joten säännön ehto täyttyy.. Exceptions audit: Sääntö etsii absoluuttisia tilailmoituksia ilman riskien mainintaa. Lähdeteksti on luonteeltaan päinvastainen; se keskittyy kriiseihin, haasteisiin ja riskeihin, eikä sisällä vaadittuja absoluuttisia väitteitä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_513d51a119ef4fd6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b666529910ea404295aa6f8c8958260d) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löydy selkeää esimerkkiä, jossa tehtäisiin johtopäätös perustuen vain rajoitettuun näkyvään todistusaineistoon samalla aktiivisesti sivuuttaen tuntemattomia tekijöitä. Esitetyt kausaaliketjut ovat analyysin ytimessä ja perustuvat annettuihin Sitran raportteihin, eivätkä ne vaikuta perusteettomilta loogisilta harppauksilta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_15c6c7ce95044ec293f482a88afb11ae) - [TRUE]:**
  > *Presence detected: The text presents a direct causal leap, stating that crises and a cracking economy feed well-being challenges, which in turn *directly affects* labor availability. This conclusion is based solely on the visible connection between these trends, ignoring other complex socio-economic factors and unknowns that influence the labor market.. Exceptions audit: Sääntö etsii johtopäätöstä, joka perustuu vain rajalliseen näkyvään todistusaineistoon ja jättää tuntemattomat seikat huomiotta. Teksti on analyysi Sitran raporteista, ja sen johtopäätökset perustuvat tähän annettuun aineistoon. Tekstissä ei ole kohtaa, jossa aktiivisesti sivuutettaisiin tunnettuja epävarmuustekijöitä virheellisen johtopäätöksen tekemiseksi. Ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b7ce46fc627dbc7e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find demands for epistemological humility (e.g., 'tell me what you do not know', 'what are the limitations of this analysis'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly commands the AI to state its uncertainties or missing data. Demands for absolute certainty.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b666529910ea404295aa6f8c8958260d) - [FALSE]:**
  > *No presence of target concept detected: I scanned all user prompts in the chat log. None of them contain a command for the AI to state its uncertainties, limitations, or what it does not know. The phrase 'ei siis toivetila' (so not a wishful state) is a constraint on the source information, not a demand for the AI's self-reflection.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_15c6c7ce95044ec293f482a88afb11ae) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kehotuksia, joissa tekoälyä pyydetään ilmaisemaan epävarmuutensa. Käyttäjä ei esitä tällaisia suoria pyyntöjä. Kehotus 'ei siis toivetila' tarkentaa halutun tiedon tyyppiä, mutta ei ole suora komento tekoälylle eritellä tietämyksensä rajoja.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6bf0433f60924302` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. Vague filler words.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b666529910ea404295aa6f8c8958260d) - [TRUE]:**
  > *Presence detected: Lauseessa käytetään ehdollista määritettä ('Kriisien keskellä'), joka rajaa eksplisiittisesti olosuhteet, joissa väite ('on tehtävä tietoisia valintoja') pätee. Tämä täyttää poiminnan ehdon.. Exceptions audit: Tekstistä ei löytynyt ehdollistavia kvalifiointi-ilmaisuja, kuten 'pääasiassa kun' tai 'näissä olosuhteissa'. Väitteet esitetään yleispätevinä ilman niiden soveltamisalan tai todennäköisyyksien rajaamista.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_15c6c7ce95044ec293f482a88afb11ae) - [FALSE]:**
  > *No presence of target concept detected: The text does not contain conditional qualifiers that define specific boundaries or probabilities for its claims. The tone is generally absolute and declarative rather than conditional.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6758e0a8f1b3aaf8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find conflict resolution markers (e.g., 'while X requires Y, we must also ensure Z by'). STEP 2 (Bounding Box): Scan the paragraph. If two conflicting operational constraints (e.g., Retention vs Disposition) are mentioned and a specific action is taken to resolve the tension. Do not accept rhetorical mentions of conflict without a resolution action.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_b666529910ea404295aa6f8c8958260d) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kahden ristiriitaisen toiminnallisen rajoitteen mainintaa ja niiden ratkaisutoimenpidettä. Teksti kuvaa laajoja yhteiskunnallisia jännitteitä, mutta ei esitä säännön tarkoittamaa spesifistä operationaalista konfliktinratkaisua.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_15c6c7ce95044ec293f482a88afb11ae) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii kohtia, joissa kaksi ristiriitaista toiminnallista rajoitetta mainitaan ja niiden välinen jännite ratkaistaan tietyllä toimenpiteellä. Vaikka teksti kuvaa yleisellä tasolla jännitteitä, kuten selviytymisen ja uudistumisen välillä, se ei sisällä säännön vaatimaa syntaktista rakennetta, jossa kaksi nimettyä rajoitetta asetetaan vastakkain ja ratkaistaan nimenomaisella toimenpiteellä.  [5. VALIDATION DECISION: FAIL]*

---

