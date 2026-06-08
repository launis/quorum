# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 185
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 90.81 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.7991
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.7994
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.0919
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 17 kpl
- **PASSED -> FAILED:** 5
- **FAILED -> PASSED:** 12
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_b7dfe23403db4db5b92a29a8bda9957c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find listing conjunctions (e.g., 'and', 'also', 'in addition'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: two major domain concepts are placed side-by-side without a relational verb connecting them. Do not accept sentences that explicitly define the relationship between the concepts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on inverse-sääntö. Tekstistä ei löytynyt yhtään tapausta, jossa kaksi merkittävää toimialakonseptia olisi asetettu rinnakkain 'ja'-konjunktiolla ilman niitä yhdistävää relationaalista verbiä tai lauseketta. Kaikissa 'ja'-konjunktiota sisältävissä lauseissa oli selkeä relationaalinen verbi tai määrite, joka kuvasi käsitteiden välistä suhdetta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'Kustannus- ja Toimitusketjuhäiriöt:' kaksi merkittävää toimialakonseptia ('Kustannus' ja 'Toimitusketjuhäiriöt') on asetettu vierekkäin 'ja'-konjunktiolla ilman niitä yhdistävää relationaalista verbiä. Vaikka ne muodostavat yhdistelmänimen, niiden välistä suhdetta ei määritellä verbin avulla tässä lauseessa, mikä rikkoo säännön ehtoja.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_eb266643b83b48bbab94a041b6d12f6d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: EXTRACTION CONDITION: the user explicitly restricts the AI to the provided data and demands exact evidence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä rajoitti tekoälyn vastausta nimenomaisesti annettuihin raportteihin käyttämällä fraasia 'raporttien perusteella', mikä vastaa säännön ehtoa 'perustuen vain'.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteissa ei ollut yhtään syntaktista ankkuria ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain'), jotka rajoittaisivat tekoälyn tuotoksen tarkkaan todisteeseen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_1473cecaeb4c495c9bd0d28710e602b4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Focus on 'user:' to 'ai:' interaction. BANNED LOGIC: Do not accept vague requests. STEP 1 (Syntactic Anchor): Find an explicit user instruction containing at least two specific constraints (e.g. format, tone, length). STEP 2 (Bounding Box): Scan the subsequent user response. EXTRACTION CONDITION: the user explicitly verifies those exact constraints (e.g. 'Constraint A met, Constraint B failed'). NEGATIVE CONDITION (RETURN NULL IF MET): verification is absent or generic.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että käyttäjä antaa vähintään kaksi spesifistä rajoitusta ja sitten eksplisiittisesti vahvistaa NÄMÄ TARKAT rajoitukset myöhemmässä vastauksessa. Esimerkiksi 'koosta näistä vastauksista 1 sivun raportti' sisältää kaksi rajoitusta ('1 sivun', 'raportti'), mutta seuraava käyttäjän vastaus ('näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan') ei eksplisiittisesti vahvista edellisiä rajoituksia. Viimeisessä käyttäjän ohjeessa ('kirjoita tämä kaupallisen liiketoiminnan johtoryhmälle ja kirjoita siihen hiukan kaupallisia vaikutuksia mukaan') ei ole lainkaan myöhempää vahvistusta. Koska vahvistus puuttuu tai on liian yleinen, negatiivinen ehto täyttyy, ja palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Mitigating exception found: Käyttäjän ohjeessa "poista taulukot ja kerro ne tekstinä" oli kaksi spesifistä rajoitetta. Seuraavassa käyttäjän vastauksessa ("Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä") ei kuitenkaan ole eksplisiittistä vahvistusta näiden rajoitteiden täyttymisestä, mikä täyttää ehdon, että vahvistus puuttuu tai on yleistä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_049eb80a94164c519d5a322d55499707` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept post-generation complaints. STEP 1 (Syntactic Anchor): Find a friction marker prior to an action (e.g. 'This is difficult because', 'The risk here is', 'We must balance'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the conflict or trade-off is articulated BEFORE the final output is generated. NEGATIVE CONDITION (RETURN NULL IF MET): the friction is only discussed afterwards.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää kitkan tai ristiriidan ilmaisemista ENNEN toimintoa. Käyttäjän reflektiotekstissä mainitut kitkat ('Mietin erilaisia sanoja ja termejä', 'Huomasin myös, että lähtötilanteessaa oli virhe') ovat post-hoc-analyysiä, eivätkä ne ole ilmaistuina ennen tekoälyn tuottamaa lopputulosta tai edes ennen seuraavaa käyttäjän ohjetta chat-lokissa. Siksi negatiivinen ehto täyttyy, ja palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Mitigating exception found: Kitkaa ilmaiseva merkki ("Ennakoin, että alkuun en saa hyvää tulosta") esiintyy käyttäjän jälkikäteisessä reflektiossa (`Reflection_Text`), eikä ennen toimintoa `Chat_Logissa`. Tämä täyttää ehdon, että kitka on mainittu vasta jälkikäteen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_84b7784951c84e948c131c189261f564` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** <syntactic_constraint> <anchors> <anchor>a limitation is</anchor> <anchor>rajoituksena on</anchor> <anchor>puutteena on</anchor> <anchor>heikkoutena on</anchor> </anchors> <transitions> <transition>however</transition> <transition>regardless</transition> <transition>kuitenkin</transition> <transition>silti</transition> </transitions> <extraction_condition> Verify if a limitation acknowledgment from the <anchors> block is immediately followed (within two sentences) by a dismissive logical transition word from the <transitions> block that rationalizes away the limitation. </extraction_condition> <ambiguity_protocol> If the limitation anchor from <anchors> is absent, or if the dismissive marker from <transitions> is missing, or if new empirical data is cited to solve the limitation, you MUST return JSON null. Do not rationalize or excuse missing evidence. </ambiguity_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *Tekstistä ei löytynyt ankkurisanoja, jotka tunnustaisivat rajoituksen, kuten 'rajoituksena on', 'puutteena on' tai 'heikkoutena on'. Tämän vuoksi ei ollut mahdollista tarkistaa, seurasiko niitä vähättelevä siirtymäsana.*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Teksti tunnistaa 'rajoite'-sanan (limitation) ja seuraavassa lauseessa käyttää 'vaan' (but/rather) -sanaa siirtyäkseen suoraan rationalisoimaan rajoituksen pois esittämällä sen 'uuden taloudellisen kasvun perustana'. Tämä täyttää ehdon rajoituksen tunnustamisesta, jota seuraa välittömästi sen vähättely tai rationalisointi.*

---

### Atom-ID: `tda_19e1957773db4cfd820cb167ae1d8ec3` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept implicit modesty. STEP 1 (Syntactic Anchor): Find an explicit epistemic boundary marker (e.g. 'may not apply', 'exception', 'edge case', 'out of scope'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the text physically identifies a scenario where the model or logic fails or is limited. NEGATIVE CONDITION (RETURN NULL IF MET): absent.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt eksplisiittisiä epistemologisia raja-arvoja tai vaatimattomuuden merkkejä, jotka tunnistaisivat skenaarion, jossa esitetty malli tai logiikka epäonnistuu tai on rajoitettu. Teksti kuvaa ulkoisia kriisejä, mutta ei analyysin omia rajoituksia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Mitigating exception found: Tekstissä mainitaan eksplisiittisesti 'rajoite' (limitation), joka on episteeeminen raja-arvomerkki ja osoittaa skenaarion, jossa malli tai logiikka on rajallinen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_a946688e5f5549e8ac30584d1a02ad26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph containing statistical or factual reporting. STEP 2: Count the first-person pronouns ('I', 'we') or explicit self-reflective verbs ('assume', 'interpret'). EXTRACTION CONDITION: the count is exactly 0. NEGATIVE CONDITION (RETURN NULL IF MET): greater than 0. <ambiguity_protocol>ABSOLUTE ZERO ENFORCEMENT: The count of first-person references must be EXACTLY zero. You are strictly forbidden from ignoring possessive suffixes, bound morphemes, verb inflections, or clitics that grammatically denote a first-person perspective in the source document's target language (e.g., the Finnish suffix '-mme' in 'yrityksemme' or verb inflection '-n' in 'oletan'). If any such morpho-syntactic marker is found, the count is greater than zero, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *Tekstissä esiintyy sana 'yrityksemme', joka sisältää ensimmäisen persoonan monikon possessiivisuffiksin '-mme'. Tämä tarkoittaa, että ensimmäisen persoonan viittauksia on enemmän kuin nolla, joten ehdon 'count is exactly 0' negatiivinen ehto täyttyy.*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Tekstistä löytyi ensimmäisen persoonan monikon possessiivisuffiksi '-mme' sanoista 'yrityksemme' ja 'kyvystämme' kappaleessa 'Johtopäätös'. Koska ensimmäisen persoonan viittauksia löytyi, laskenta ei ole tasan 0, ja negatiivinen ehto täyttyy.*

---

### Atom-ID: `tda_680dc2c703b3425fa0b0d943dbd5af16` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in a 'user:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'ai:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find a structural blueprint or architectural parameter list (e.g., 'must contain', 'requirements are', 'architecture must'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the blueprint AND ALSO contains conflict or constraint vocabulary (e.g., 'conflict', 'hard part', 'trade-off', 'issue', 'balance', 'problem') -> ACCEPT. If it lacks constraint vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, psychological 'cognitive friction', or 'pre-meditated' status. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän syötteistä ei löytynyt yhtään kappaletta, joka olisi sisältänyt sekä rakenteellisen suunnitelman tai parametriluettelon että konfliktia tai rajoituksia kuvaavaa sanastoa. Esimerkiksi 'tee kokonaisuudesta raportti, missä Supermegatrendit ovat pääosassa' sisältää rakenteellisen vaatimuksen, mutta ei konfliktisanastoa samassa kappaleessa. Negatiivinen ehto täyttyi, joten palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Presence detected: Käyttäjän syötteestä löytyi rakenteellinen suunnitelma ('Megatrendien Kooste ja Evoluutio Tekstinä') ja siihen liittyvä rajoitesanasto ('aina kun on järkevää'). 'Aina kun on järkevää' toimii ehtona tai rajoitteena viestien sisällyttämiselle, mikä täyttää molemmat ehdot.. Exceptions audit: Käyttäjän syötteestä ei löytynyt kappaletta, joka olisi sisältänyt sekä rakenteellisen suunnitelman tai parametriluettelon että konfliktia tai rajoitusta kuvaavaa sanastoa. Negatiivinen ehto täyttyi.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_003f932abb9642fc8c3147b04fac95c5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find declarations of completeness (e.g., 'exhaustive', 'covers everything', 'the only possible'). STEP 2: Document the reasoning. STEP 3: EXTRACTION CONDITION: the text explicitly claims that there are zero unknown variables remaining. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *Tekstistä ei löytynyt täydellisyyttä julistavia ilmaisuja, kuten 'kaikenkattava', 'kattaa kaiken' tai 'ainoa mahdollinen', eikä myöskään väitteitä tuntemattomien muuttujien puuttumisesta. Teksti keskittyy 'kolmeen keskeiseen Supermegatrendiin', mikä viittaa valikoituun, ei tyhjentävään, analyysiin.*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Teksti sisältää suoran väitteen 'ainoa tapa', joka implikoi täydellisen ratkaisun ilman tuntemattomia muuttujia pitkän aikavälin vakauden takaamiseksi. Tämä on julistus täydellisyydestä ilman, että tuntemattomia muuttujia tunnustetaan.*

---

### Atom-ID: `tda_24bdc98709e84de984aabd67b597239b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Etsin 'ai:'-lohkoista menettelyllisiä sekvenssimarkkereita, kuten numeroituja luetteloita. Löysin kohdan, jossa käytettiin '1.', '2.' ja '3.' markkereita. Tämän jälkeen tarkistin, sisältääkö sama kappale synteesi- tai päättelyverbejä. Kappaleessa esiintyi verbi 'tarkoittaa', joka tulkitaan päättelyverbiksi ('this means/implies'). Koska sääntö edellyttää, ettei kappale sisällä tällaisia verbejä, negatiivinen ehto ei täyttynyt, ja siksi palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Presence detected: Etsin `ai:`-lohkoista proseduurisia sekventiaalisia markkereita. Löysin numeroidut kohdat 1, 2 ja 3 `ai:`-vastauksesta, joka alkaa "Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 → 2023) Supermegatrendit Postnormaalissa Ajassa". Tarkistin, ettei näitä kohtia sisältävä kappale sisältänyt eksplisiittisiä synteesi- tai deduktiiverbejä ('analysoitu', 'päätelty', 'syntetisoitu', 'siksi'). Kappaleen teksti kuvaa ja selittää, mutta ei käytä näitä kiellettyjä verbejä.. Exceptions audit: Sääntö etsii proseduraalisia sekventiaalimerkkejä ('1.', '2.', '3.', jne.) `ai:`-lohkoista, mutta hylkää osuman, jos kappale sisältää synteesiä tai päättelyä ilmaisevia verbejä. Ensimmäinen `ai:`-lohko sisältää numeroituja listoja (proseduraalisia merkkejä), mutta myös synteesiä ja päättelyä ilmaisevia lauseita, kuten 'Sitran keskeinen viesti on' ja 'Tämä edellyttää'. Siksi negatiivinen ehto ei täyty, ja osumaa ei hyväksytä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_4ba32055738247d28e00a597f505ce9e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** <syntactic_constraint> <anchors> <anchor>either</anchor> <anchor>or</anchor> <anchor>simply boils down to</anchor> <anchor>joko</anchor> <anchor>tai</anchor> <anchor>pelkistyy</anchor> </anchors> <extraction_condition> Verify if the text explicitly frames a multi-dimensional system or complex strategic situation into exactly two opposing options using one of the binary reduction anchors from the <anchors> block, without acknowledging any middle ground or other alternatives. </extraction_condition> <ambiguity_protocol> If the binary reduction anchors from <anchors> are absent, or if there is any nuance or mention of alternative paths in the paragraph, you MUST return JSON null. Speculation is strictly banned. </ambiguity_protocol> </syntactic_constraint> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Etsin binäärisen pelkistyksen ankkureita ('joko', 'tai', 'pelkistyy'). Teksti ei kehystä moniulotteista järjestelmää tai monimutkaista strategista tilannetta täsmälleen kahdeksi vastakkaiseksi vaihtoehdoksi käyttäen näitä ankkureita ilman, että tunnustettaisiin mitään välimaastoa tai muita vaihtoehtoja. Teksti kuvaa usein toisiinsa liittyviä tekijöitä ja monipuolisia lähestymistapoja, ei tiukkaa binääristä valintaa. Koska sääntö on käänteinen ja rikkomusta ei löytynyt, palautetaan tyhjä merkkijono.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Presence detected: Teksti esittää moniulotteisen tilanteen (pitkän aikavälin vakauden takaaminen) ja pelkistää sen yhteen ainoaan vaihtoehtoon ('ainoa tapa') ilman, että muita vaihtoehtoja tai välivaiheita tunnustetaan. Vaikka 'joko' tai 'tai' ei esiinny, 'ainoa tapa' toimii vastaavana binäärisenä pelkistyksenä.. Exceptions audit: Tekstistä löytyi ankkuri 'pelkistyy', mutta sitä ei käytetty moniulotteisen järjestelmän tai monimutkaisen strategisen tilanteen rajaamiseen kahteen vastakkaiseen vaihtoehtoon ilman, että muita vaihtoehtoja tai välimaastoja olisi tunnustettu. Sen sijaan se esiintyi osana laajempaa selitystä, joka ei pelkistänyt tilannetta binäärisesti.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8ecd3f17b3984e4fa1bb6a8cb5576b65` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate nuance. STEP 1 (Syntactic Anchor): Find absolute causal words ('only reason', 'entirely due to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text attributes a highly complex outcome to a single cause without acknowledging any other potential factors.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt absoluuttisia kausaalisanoja ('ainoa syy', 'kokonaan johtuen', 'täysin johtuen'), jotka liittäisivät monimutkaisen lopputuloksen yhteen ainoaan syyhyn.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Mitigating exception found: Teksti käyttää absoluuttista kausaalista ilmaisua 'ainoa tapa' (the only way) ja liittää monimutkaisen lopputuloksen ('pitkän aikavälin vakaus') yhteen ainoaan syyhyn ('Korjaavaan ja uusintavaan talouteen siirtyminen') tunnustamatta muita mahdollisia tekijöitä, mikä rikkoo säännön.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_715eb98a6f4a4a1e944db99f5eaaded9` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate internal mental states. STEP 1 (Syntactic Anchor): Find epistemic boundary markers (e.g. 'may be inaccurate', 'verify independently', 'limitations', 'hallucination'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: there is a physical, explicit statement acknowledging the AI's limitations or a disclaimer.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [TRUE]:**
  > *Mitigating exception found: Käyttäjän reflektioteksti sisältää useita lauseita, jotka eksplisiittisesti tunnustavat tekoälyn tuotoksen rajoitukset ja virheet, kuten 'liian laaja', 'virhe' ja 'korjasin'. Nämä osoittavat tekoälyn rajoitusten tiedostamisen ja tarpeen ihmisen puuttumiselle.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää fyysistä, eksplisiittistä lausuntoa tekoälyn rajoitusten tunnustamisesta tai vastuuvapauslauseketta. Lähdetekstissä ei ole tällaista lausuntoa tekoälyn omasta toimesta. Käyttäjän reflektioissa mainitaan tekoälyn vastauksen laajuus tai syöttödatan virhe, mutta ei tekoälyn itsensä esittämää rajoitusta tai vastuuvapauslauseketta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_f29c602444b446a3a6973aa9953a0b01` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find contextual qualifiers (e.g., 'in this specific context', 'under these conditions'). STEP 2: Extract the exact_quote containing the qualifier. EXTRACTION CONDITION: found.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [TRUE]:**
  > *Lause 'Johtoryhmälle tämä tarkoittaa:' toimii selkeänä kontekstuaalisena kvalifioijana, joka rajaa seuraavan tiedon koskemaan nimenomaan johtoryhmää.*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [FALSE]:**
  > *Tekstistä ei löytynyt eksplisiittisiä kontekstuaalisia kvalifioijia, kuten 'tässä spesifissä kontekstissa' tai 'näissä olosuhteissa', jotka rajoittaisivat väitteen soveltamisalaa. Vaikka teksti kuvaa yleisiä olosuhteita (esim. 'Postnormaalissa Ajassa', 'Kriisien keskellä'), se ei käytä niitä faktuaalisen väitteen kontekstuaalisena rajoittimena vaaditulla tavalla.*

---

### Atom-ID: `tda_1361cf5ec5b5420c905cd2a1f80893a7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in a 'user:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'ai:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit retrospective claims of intent (e.g., 'That is what I meant', 'I intended', 'As expected'). STEP 2 (Bounding Box & Negative Condition): Scan the text preceding this claim (the original instruction). If the preceding text DOES NOT physically contain the exact parameters now being claimed -> ACCEPT. If the preceding text physically contains the parameters -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'sincerity' or 'post-hoc rationalization'. Evaluate only the physical presence or absence of the claimed parameters in the prior text.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että käyttäjän takautuva aikomusväite (reflektiotekstistä) EI OLE ollut fyysisesti läsnä alkuperäisessä ohjeessa (chat-lokissa). Kaikissa käyttäjän reflektiotekstissä esittämissä aikomusväitteissä ('Pyysin supermegatrendejä', 'Aloitin kyselemään yleisesti, mitä ovat megatrendit', 'Annoin rajoituksia sekä roolin liiketoiminnalle') vastaavat parametrit löytyvät eksplisiittisesti aiemmista chat-lokien käyttäjäohjeista. Koska alkuperäinen teksti SISÄLTÄÄ väitetyt parametrit, negatiivinen ehto täyttyy (eli 'REJECT'), ja palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä väittää jälkikäteen antaneensa rajoituksia ja roolin liiketoiminnalle. Viimeinen käyttäjän ohje ("kirjoita tämä kaupallisen liiketoiminnan johtoryhmälle ja kirjoita siihen hiukan kaupallisia vaikutuksia mukaan") sisältää "kaupallisen liiketoiminnan johtoryhmälle" ja "kaupallisia vaikutuksia", jotka vastaavat tätä väitettä. Koska edeltävä teksti *sisältää* väitetyt parametrit, tämä ei ole post-hoc rationalisointi säännön määritelmän mukaan (sääntö etsii tapauksia, joissa parametreja *ei* ollut).  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bd85f009b0fb4f7899b40ff0e763dee7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find tension markers between metrics and goals (e.g., 'this metric is flawed because', 'we need to ensure this actually works'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly questions the reliability of a proxy metric in relation to the ultimate qualitative goal. Do not accept simple metric tracking.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [TRUE]:**
  > *Presence detected: Käyttäjä erottaa 'Sitran näkemyksen' 'toivetilasta', mikä kyseenalaistaa 'toivetilan' luotettavuuden tai pätevyyden ohjaavana tekijänä 'suunnasta eteenpäin'. Tämä on jännitemarkkeri mittarin (toivetila) ja laadullisen tavoitteen (suunta eteenpäin) välillä.. Exceptions audit: Käyttäjän syötteistä ei löydy lauseita, jotka ilmaisivat jännitteitä mittareiden ja tavoitteiden välillä tai kyseenalaistaisivat välitysmittarin luotettavuutta suhteessa lopulliseen laadulliseen tavoitteeseen.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteista ei löytynyt syntaktisia ankkureita, jotka viittaisivat jännitemerkkeihin mittareiden ja tavoitteiden välillä, kuten 'tämä mittari on virheellinen, koska' tai 'meidän on varmistettava, että tämä todella toimii'. Käyttäjä ei kyseenalaistanut välitysmittarin luotettavuutta suhteessa lopulliseen laadulliseen tavoitteeseen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_ac3b078498e048889ad3bc46b634c2ee` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find an external citation, mathematical theorem, or recognized academic framework. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the explanation explicitly tethers its logic to this external, verifiable source (e.g. applying a specific rule from the source). NEGATIVE CONDITION (RETURN NULL IF MET): the source is merely named without application.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d1ee66b472d846d589730b3ab617fa8e) - [TRUE]:**
  > *Mitigating exception found: Teksti viittaa eksplisiittisesti Sitran megatrendiraportteihin ja käyttää niitä perustana analyysilleen, osoittaen logiikan kytkemisen ulkoiseen lähteeseen eikä pelkkää nimeämistä. Esimerkiksi megatrendien kehitystä kuvataan suoraan raporttien perusteella.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_f9f6450275b640f5ab1db2b3c2aa56fd) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että ulkoinen lähde on nimenomaisesti sidottu logiikkaan, ei vain nimetty. Sekä tuotetekstissä että chat-lokissa Sitran raportteja käytetään aktiivisesti analyysin perustana ja kehityskulkujen selittämiseen, mikä täyttää soveltamisen ehdon. Negatiivinen ehto (pelkkä nimeäminen ilman soveltamista) ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

