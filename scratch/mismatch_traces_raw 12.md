# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 185
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 88.11 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.7553
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.1189
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 22 kpl
- **PASSED -> FAILED:** 6
- **FAILED -> PASSED:** 16
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_a383d38d1f47ce65` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. EXTRACTION CONDITION: role prefixes exist, focus on the 'ai:' block. BANNED LOGIC: Do not evaluate 'opaque' subjectively. STEP 1 (Syntactic Anchor): Find a definitive conclusion or final answer (e.g. 'Therefore', 'The result is', 'In conclusion'). STEP 2 (Bounding Box): Scan the preceding text. NEGATIVE CONDITION (RETURN NULL IF MET): the conclusion is presented WITHOUT any preceding step-by-step mathematical, logical, or variable-level decomposition. If steps exist. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [TRUE]:**
  > *Mitigating exception found: Malli esittää 'Lopullinen arvio' -taulukossa johtopäätöksiä (arvioita), mutta ei tarjoa edeltävässä tekstissä askel-askeleelta etenevää logiikkaa tai muuttujia, joilla näihin arvioihin on päädytty. Tämä tekee johtopäätöksestä läpinäkymättömän.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö. Tekoäly esittää johdonmukaisesti johtopäätöksensä (esim. "Lyhyt vastaus:", "Johtopäätös") ja tarjoaa niille välittömästi perusteellisen, vaiheittaisen loogisen tai rakenteellisen erittelyn. Koska johtopäätöksiä ei esitetä ilman edeltävää tai seuraavaa päättelyketjua, sääntöä ei rikota.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8af3c72c0b5d4bfe` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find implicit authority markers (e.g., 'it is common knowledge', 'we always do it this way', 'internally known'). STEP 2 (Bounding Box): Scan the sentence. If a procedural rule is justified solely by internal tradition without citing an external verifiable standard (ARMA Transparency violation). BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept explicit external citations. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt kohtaa, jossa proseduraalista sääntöä olisi perusteltu ainoastaan sisäisellä perinteellä tai implisiittisellä auktoriteetilla. Malli pyrkii perustelemaan väitteensä joko logiikalla tai ulkoisilla lähteillä, eikä vetoa vakiintuneisiin, perustelemattomiin käytäntöihin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Lainaus rikkoo sääntöä, koska siinä menettelyllinen toimi (prosenttilukujen käyttö) oikeutetaan vetoamalla 'kokemusperäisiin arvioihin' ja 'kouluttajien käytännön havaintoihin'. Tämä on sisäiseen perinteeseen tai vahvistamattomaan tietoon perustuva perustelu ilman viittausta ulkoiseen, todennettavissa olevaan standardiin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fbd90f9c0f2247ed` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit counterargument markers (e.g., 'critics argue', 'opposing view', 'counterargument', 'on the other hand'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the counterargument marker AND ALSO contains physical citation markers (e.g., 'et al', '[1]', '(', 'published in') AND empirical measurement vocabulary (e.g., 'data', 'showed', 'measured') -> ACCEPT. If it lacks citations or measurement tokens -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'strength', 'steel-manning', or whether the argument is successfully 'dismantled'. Evaluate only physical token presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt kohtaa, jossa olisi samanaikaisesti esitetty vastaväite-ankkuri (kuten "kriitikot väittävät"), fyysinen lähdeviite ja empiirinen mittaustermi (kuten "osoitti"). Vaikka tekoäly viittaa tutkimuksiin, se ei tee sitä esitelläkseen ja kumotakseen vahvasti perusteltua vastaväitettä säännön edellyttämällä tavalla.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii lähdeviitattua vasta-argumenttia. Tekoäly esittelee tutkimuslähteen ('Tecnológico de Monterrey Observatory') ja käyttää sitä tuodakseen esiin riskejä ('kriittisen ajattelun heikkeneminen'), jotka toimivat vasta-argumenttina tekoälyn hyödyille. Tämä kappale sisältää sekä vasta-argumentin (riskit), lähdeviitteen että viittauksen empiiriseen havaintoon ('Nostaa esiin'), joten se täyttää säännön ehdot.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_58b71c9945482385` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the user prompts (prefixes like 'user:'). BANNED SOURCES: Never read AI outputs. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not look for absence of critique. STEP 1 (Syntactic Anchor): Find active acceptance words ('täydellinen', 'näin', 'jatketaan', 'hyvä', 'perfect', 'looks good'). STEP 2 (Bounding Box): Scan the user prompt. EXTRACTION CONDITION: the user accepts the AI output fully in one sentence WITHOUT any modifications or follow-up tasks in the same prompt. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Yksikään käyttäjän kehotteista ei täytä ehtoa. Vaikka käyttäjä käyttää hyväksyviä sanoja, kuten "Hienoa" ja "Hyvä", ne on aina yhdistetty samaan kehotteeseen kuuluvaan uuteen tehtävään, mikä rikkoo sääntöä, jonka mukaan hyväksynnän tulee tapahtua ilman seurantatehtäviä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Presence detected: Käyttäjä ilmaisee hyväksyntänsä sanoin 'Hyvä kiitos' ja siirtyy välittömästi seuraavaan aiheeseen ilman mitään muokkauksia, tarkennuksia tai jatkotehtäviä samassa kehotteessa. Tämä on selkeä esimerkki sokeasta hyväksynnästä, jossa edellinen tuotos kuitataan valmiiksi ja siirrytään eteenpäin.. Exceptions audit: No instances were found where the user passively accepts the AI's output without immediately providing a new task, modification, or question in the same prompt. All positive acknowledgements are coupled with further instructions.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b26497410d7b422b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find generic consensus markers ('as everyone knows', 'it is widely accepted', 'obviously'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: consensus is the ONLY backing for a logical rule. NEGATIVE CONDITION (RETURN NULL IF MET): an empirical source is cited. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Verifiable empirical sources. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [TRUE]:**
  > *Presence detected: Lause käyttää vetoamista jaettuun historiaan/yleiseen tietoon ('Sama pelko on ollut') ainoana perusteena argumentille, että nykyinen pelko on vain vanha ilmiö uudessa muodossa. Empiiristä lähdettä tämän historiallisen rinnastuksen tueksi ei esitetä.. Exceptions audit: The text does not use generic consensus markers like 'as everyone knows' or 'it is widely accepted' as the sole backing for a logical rule. The arguments are backed by internal logic or provided sources.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt säännön määrittelemiä yleiseen konsensukseen vetoavia fraaseja, joita olisi käytetty väitteen ainoana perusteluna. Argumentit perustuvat logiikkaan tai viitattuihin lähteisiin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_713c6cd20146d1c2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Ignore system instructions. STEP 1 (Syntactic Anchor): Find a falsification marker (e.g. 'Let\'s try to break this', 'What EXTRACTION CONDITION: the opposite is true', 'Counter-argument'). STEP 2 (Bounding Box): Scan the paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): the user explicitly introduces a scenario designed to make their own hypothesis fail. If no active stress-test is present. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei missään vaiheessa yritä aktiivisesti kumota omia oletuksiaan tai esitä skenaariota, joka pyrkisi osoittamaan oman hypoteesinsa vääräksi.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä on ensin omaksunut hypoteesin ohjaavasta ja sparraavasta roolista. Tämän jälkeen hän pyytää tekoälyä analysoimaan tätä mallia opiskelijan näkökulmasta. Tämä on aktiivinen yritys testata ja mahdollisesti falsifioida omaa omaksuttua hypoteesia etsimällä siitä heikkouksia tai haasteita toisesta perspektiivistä katsottuna.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_cee9db6717cdafb7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Locate a risk assessment or 'pre-mortem' structure. STEP 2: Find explicit dismantling of a risk using a verifiable external citation or empirical data. EXTRACTION CONDITION: both the risk and the empirical counter-data are found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [TRUE]:**
  > *Teksti sisältää riskinarviointirakenteen (otsikko 'Riski: ajattelun heikkeneminen ja riippuvuus') ja purkaa tai kontekstualisoi riskin käyttämällä ulkoista viitettä ('Tecnológico de Monterrey Observatory'). Molemmat ehdot täyttyvät.*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [FALSE]:**
  > *fi: Tekstiä analysoitaessa ei löytynyt kohtaa, jossa riskiarvio olisi purettu suoraan ulkoiseen, todennettavissa olevaan viittaukseen tai empiiriseen dataan vedoten. Tekoäly tunnistaa riskejä ja käyttää ulkoisia lähteitä niiden ymmärtämiseen ja vahvistamiseen, mutta se ei käytä dataa riskin kumoamiseen tai purkamiseen säännön edellyttämällä tavalla.*

---

### Atom-ID: `tda_073aecbc29db5fc9` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in a 'user:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'ai:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find a structural blueprint or architectural parameter list (e.g., 'must contain', 'requirements are', 'architecture must'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the blueprint AND ALSO contains conflict or constraint vocabulary (e.g., 'conflict', 'hard part', 'trade-off', 'issue', 'balance', 'problem') -> ACCEPT. If it lacks constraint vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, psychological 'cognitive friction', or 'pre-meditated' status. Evaluate only physical token presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt käyttäjän kehotetta, joka sisältäisi samanaikaisesti sekä rakenteellisia vaatimuksia että kuvauksen ongelmasta tai ristiriidasta.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Presence detected: Sääntö edellyttää rakenteellisen suunnitelman ('blueprint') ja rajoitteen ('constraint') löytymistä samasta käyttäjän viestistä. Ensimmäinen käyttäjän viesti sisältää molemmat: rajoitteen ('Esihenkilöni on huolissaan tekoälyn tuottamista haasteita') ja suunnitelman ('Tehtävänä on nyt kertoa esihenkilölleni...'). Nämä elementit löytyvät samasta kappaleesta, joten säännön ehdot täyttyvät.. Exceptions audit: Sääntö edellyttää, että käyttäjän kehotteesta löytyy sekä rakenteellinen ohjeistus että samanaikainen viittaus konfliktiin tai rajoitteeseen. Lähdetekstin käyttäjän kehotteet sisältävät kyllä ohjeita (esim. 'Tee tekstit kahteen Powerpoint diaan'), mutta niissä ei samassa yhteydessä artikuloida ongelmaa tai kompromissia, jota ohjeistus yrittäisi ratkaista. Siksi säännön molemmat ehdot eivät täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_653b3f5497b9147e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find explicit external anchoring for uncertainty (e.g., 'due to X, as noted by [Source]'). STEP 2: Map the cognitive friction. EXTRACTION CONDITION: an external citation is used specifically to justify why a variable remains unknown. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *Sääntö etsii ulkoista lähdettä, jota käytetään perustelemaan, miksi jokin muuttuja on tuntematon. Tekoäly käyttää lähteitä tukeakseen väitteitään (esim. opiskelijat käyttävät tekoälyä), mutta se ei käytä lähdettä selittämään epävarmuutta. Kun tekoäly myöntää epävarmuuden prosenttiluvuistaan, se perustelee sen tutkimuksen puutteella ("eivät perustu yksittäiseen tutkimukseen"), ei viittaamalla tutkimukseen, joka vahvistaisi epävarmuuden syyn. Ehto ei täyty.*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Tekoäly perustelee, miksi sen aiemmin esittämät prosenttiluvut ovat epävarmoja (eivät perustu tutkimukseen vaan ovat heuristiikkaa). Se ankkuroi tämän epävarmuuden ja käyttämänsä jaottelun ulkoiseen, nimettyyn malliin, Everett Rogersin 'Diffusion of Innovations' -teoriaan.*

---

### Atom-ID: `tda_5d6ad535f76d0d14` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Syntactic Anchor): Find declarations of completeness (e.g., 'exhaustive', 'covers everything', 'the only possible'). STEP 2: Document the reasoning. STEP 3: EXTRACTION CONDITION: the text explicitly claims that there are zero unknown variables remaining. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [TRUE]:**
  > *Sääntö etsii täydellisyyttä tai kaikenkattavuutta ilmaisevia väitteitä. Vastauksessaan opiskelijan oppimisen tukemisesta tekoäly listaa palautteen laadun ja toteaa sen jälkeen: "Tämä ratkaisee kaiken.". Tämä on absoluuttinen ja kaikenkattava väite, joka esittää yhden tekijän ainoana ratkaisevana muuttujana, mikä vastaa säännön ehtoa.*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [FALSE]:**
  > *Tekoäly käyttää superlatiiveja kuten 'suurin riski' ja 'tärkein osa', mutta se ei missään vaiheessa eksplisiittisesti väitä, että sen antama tieto olisi täydellistä tai että tuntemattomia muuttujia ei olisi. Itse asiassa, kun sitä haastetaan, se myöntää tietojensa rajoitteet.*

---

### Atom-ID: `tda_c8a12182ecbc4c9f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find precise causal language ('which directly causes', 'the mechanism behind this is'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: a Claim is supported by empirical Data AND the exact mechanism is defined. NEGATIVE CONDITION (RETURN NULL IF MET): any of the three (Claim, Data, Warrant) is missing from the explicit text. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Implicit connections. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt lauseita, joissa olisi käytetty tarkkaa kausaalista kieltä, kuten 'tämän takana oleva mekanismi on'. Vaikka kausaalisia yhteyksiä esitetään, tarkkaa mekanismia ei määritellä säännön vaatimalla tavalla.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Lauseessa esitetään väite (Claim: oppimiseen vaikutus riippuu ohjauksesta), joka tuetaan empiirisellä datalla (Data: "Tutkimusten mukaan") ja mekanismi (Warrant: ohjauksen olemassaolo) on määritelty. Tämä täyttää säännön kaikki ehdot.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_55dfd9cb0adec620` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii rikkomusta. Se etsii riskien tunnistamista ilman lievennystoimia. Tekoäly tunnistaa useita pedagogisia riskejä, mutta ehdottaa systemaattisesti niihin myös ratkaisuja ja lievennyskeinoja. Rikkomusta ei tapahdu.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Presence detected: Tekoäly tunnistaa irtisanomisiin liittyvän riskin ("Riski on olemassa"), mutta ei ehdota siihen mitään konkreettista lieventävää toimenpidettä. Sen sijaan se ainoastaan rajaa riskin koskemaan tiettyjä opetuksen muotoja, jättäen riskin itsessään käsittelemättä.. Exceptions audit: Tämä on käänteinen sääntö. Tekoäly tunnistaa johdonmukaisesti pedagogisia riskejä (esim. "Näennäinen osaaminen lisääntyy", "'Heitetään syvään päähän' -riski"), mutta se myös ehdottaa niihin aina konkreettisia lievennystoimia (esim. tehtävien uudistaminen, selkeä rakenne, riittävä tuki). Yhtään riskiä ei jätetä käsittelemättä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_9a0fa3967ebb2497` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate creativity. STEP 1 (Syntactic Anchor): Find counterfactual markers ('EXTRACTION CONDITION: X had not', 'would have been'). STEP 2: NEGATIVE CONDITION (RETURN NULL IF MET): the text actively simulates an alternate timeline (Pearl's Rung 3) to explicitly prove necessary causation. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Teksti käyttää tulevaisuuteen suuntautuvia ehtolauseita riskien ja mahdollisuuksien pohtimiseen, mutta se ei käytä menneitä tapahtumia koskevaa kontrafaktuaalista päättelyä välttämättömän syy-seuraussuhteen todistamiseksi.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Presence detected: Sääntö etsii kontrafaktuaalista päättelyä, jossa simuloidaan vaihtoehtoista aikajanaa. Lause "Jos opetus ei muutu, opiskelijat ohittavat opettajan" on selkeä esimerkki tällaisesta päättelystä. Se simuloi tulevaisuutta, jossa muutosta ei tapahdu, todistaakseen muutoksen välttämättömyyden. Tämä vastaa Pearlin kausaalisuustikkaiden kolmatta tasoa.. Exceptions audit: Sääntö etsii kontrafaktuaalisen päättelyn puutetta. Teksti sisältää tulevaisuuteen suuntautuvia konditionaaleja (esim. 'Mitä tapahtuu, jos ei tehdä muutosta'), mutta ei selkeitä menneisyyttä simuloivia kontrafaktuaaleja (esim. 'olisi ollut'). Säännön negatiivinen ehto (kontrafaktuaalin löytyminen) ei täyty, mutta koska selkeää positiivista löydöstäkään ei ole, tulos on null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_50d614006cd53384` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit absolute status declarations (e.g., 'perfectly secure', 'no issues found', 'fully compliant'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute declaration BUT does NOT contain risk or mitigation vocabulary (e.g., 'risk', 'trade-off', 'vulnerability', 'however') -> ACCEPT. If it contains risk vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'sweeping nature', or subjective 'flawlessness'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt kappaletta, jossa esitettäisiin absoluuttinen tilannekuvaus (esim. 'täysin valmis', 'ei ongelmia') ilman, että samassa asiayhteydessä (kappaleessa tai siihen sidotussa listassa) mainittaisiin myös riskejä tai lieventäviä tekijöitä. Malli sisällyttää tyypillisesti riski-analyysin osaksi vastauksiaan.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Lainaus on absoluuttinen väite ('tehokkaamman kuin koskaan'). Sitä ympäröivä kappale kuvaa ainoastaan positiivisia seurauksia eikä sisällä säännössä mainittuja riskeihin tai lievennyksiin viittaavia sanoja, kuten 'riski', 'mutta' tai 'kuitenkin'.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_21d7952c2bf6393c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'watertightness'. STEP 1: Find mathematical or structural causal terms ('do-calculus', 'directed acyclic graph', 'structural equation', 'formal model'). STEP 2: EXTRACTION CONDITION: the text explicitly uses a formal model or strict structural logic to map the causality. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei käytetä formaalin kausaalimallinnuksen termejä. Päättely perustuu laadullisiin argumentteihin ja heuristiikkaan, ei rakenteellisiin yhtälöihin tai graafeihin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Presence detected: Sääntö etsii matemaattisia tai rakenteellisia kausaalisia termejä, kuten 'formaali malli'. Tekoäly viittaa eksplisiittisesti tunnettuun teoreettiseen malliin, 'Diffusion of Innovations (Everett Rogers)', selittäessään teknologian omaksumisen dynamiikkaa. Tämä täyttää säännön ehdon.. Exceptions audit: Teksti ei sisällä viittauksia muodollisiin kausaalimalleihin tai niiden termeihin, kuten 'do-calculus' tai 'rakenneyhtälömalli'. Lähimmäksi pääsee viittaus 'UTAUT-mallit', mutta sitä ei käytetä kausaalisuuden todistamiseen keskustelussa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_f1f6335cf78ee3d1` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'deliberation' without a physical pause. STEP 1 (Syntactic Anchor): Find friction markers (e.g. 'requires confirmation', 'are you sure', 'second approval'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: an explicit multi-step confirmation or manual override is required before a risky execution. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Sääntö ei täyty, koska tekoäly ei käytä tai ehdota mitään monivaiheisia vahvistusmekanismeja tai kitkaa lisääviä elementtejä ennen toimintojen suorittamista. Keskustelu etenee normaalina pyyntö-vastaus-mallina ilman erillisiä turvavahvistuksia.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Sääntö täyttyy, koska tekoäly lisää prosessiin kitkaa pyytämällä käyttäjältä vahvistuksen ennen seuraavan, työläämmän toimenpiteen (PowerPoint-diojen luomisen) suorittamista. Tämä on selkeä monivaiheinen prosessi, joka vaatii manuaalisen hyväksynnän.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c6bcce2b818718a1` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unbounded absolute rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Vaikka tekoäly rajaa vastauksiaan (esim. "Erityisesti yrittäjyyden ja markkinoinnin opetuksessa"), se ei määrittele formaalin vaatimustenmukaisuussäännön (kuten ARMA) toiminnallisia rajoja. Konteksti on neuvonanto, ei sääntöjen määrittely.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Lainaus sisältää ankkurin 'erityisesti', jolla rajataan säännön soveltamisalaa ammatilliseen koulutukseen. Tämä täyttää säännön vaatimuksen operationaalisten rajojen nimenomaisesta määrittelystä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2d670bf31419dd73` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept qualitative confidence (e.g. 'very sure'). STEP 1 (Syntactic Anchor): Find a quantitative confidence metric or strict certainty boundary (e.g. 'Confidence level', 'Margin of error', 'p-value', '95%'). STEP 2 (Bounding Box): Scan the logic block. EXTRACTION CONDITION: the text rigorously defines the EXACT quantitative or structural boundary of its own certainty. NEGATIVE CONDITION (RETURN NULL IF MET): missing quantitative boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [TRUE]:**
  > *Mitigating exception found: Malli käyttää kvantitatiivisia prosenttilukuja viitatusta ulkoisesta mallista ('Diffusion of Innovations') rakentaakseen ja jäsentääkseen argumenttiaan opiskelijoiden jakautumisesta eri ryhmiin. Tämä määrittelee rakenteellisen rajan mallin omalle päättelylle.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii kvantitatiivista varmuusmittaria (esim. '95%', 'p-arvo'). Vaikka tekstissä esiintyy prosenttilukuja, ne ovat joko ulkoisista tutkimuksista lainattuja tai malli itse kumoaa niiden dataperusteisuuden toteamalla: "Antamani prosenttiluvut...eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan. Ne ovat kokemusperäisiä arvioita (heuristiikka)". Näin ollen malli ei määrittele oman logiikkansa varmuutta kvantitatiivisesti.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_25973a87867690b7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find single-path commands (e.g., 'just write the final version', 'skip the analysis'). STEP 2 (Bounding Box): Scan the user prompt. EXTRACTION CONDITION: the user actively refuses to explore counter-arguments or alternative models. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user asks for pros and cons. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii komentoja, joissa käyttäjä kieltäytyy tutkimasta vaihtoehtoja. Käyttäjä kuitenkin jatkuvasti pyytää analyysejä, tarkennuksia ja kritiikkiä omista tuotoksistaan (esim. 'Analysoi vielä diat...'). Käyttäjä ei missään vaiheessa kieltäydy vaihtoehtojen tutkimisesta, vaan päinvastoin pyrkii laajentamaan ja syventämään keskustelua. Säännön ehto ei täyty.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että käyttäjä aktiivisesti kieltäytyy vaihtoehtojen tutkimisesta. Lähdeaineistossa käyttäjä tekee päinvastoin: hän pyytää jatkuvasti lisäanalyysejä ja uusia näkökulmia.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c59639ea92894862` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find anecdotal markers ('I once saw', 'in my experience', 'some people say'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: an anecdote is used to justify a systemic rule or broad policy. NEGATIVE CONDITION (RETURN NULL IF MET): it's just a personal story without broad policy claims. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not flag rigorous case studies. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt määriteltyjä anekdoottisia ankkureita. Tekoäly perustelee väitteensä yleisillä periaatteilla tai analyysillä, ei henkilökohtaisilla tarinoilla.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Presence detected: Lähdetekstistä ei löytynyt kohtia, joissa anekdoottia olisi käytetty järjestelmällisen säännön tai laajan politiikan perusteluna. Tekoäly viittaa siihen, mitä 'tarinat kuulostavat', mutta tekee sen kumotakseen ne, ei käyttääkseen niitä todisteina.. Exceptions audit: Lähdetekstistä ei löytynyt säännön mukaisia anekdoottisia ilmauksia, joita olisi käytetty laajan systeemitason säännön tai politiikan perustelemiseen. Tekoäly mainitsee termin 'kokemusperäisiä arvioita', mutta selittää sen olevan heuristiikkaa eikä käytä sitä anekdoottina politiikkaväitteen tukena.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_72d84ac4a1f440d5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not flag caveats that result in a mathematically or conceptually altered conclusion. STEP 1 (Syntactic Anchor): Find concessive conjunctions (e.g., 'while it is true that', 'although X fails'). STEP 2 (Bounding Box): Scan the sentence. If the concession is immediately followed by a return to the original unmodified premise (e.g., '..ultimately it holds'). Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: The AI makes concessions (e.g., 'osittain totta, mutta...'), but it uses them to qualify or modify its premise, not to dismiss the concession and return to the original unmodified premise. The specific flawed reasoning pattern is not found.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Tekoäly myöntää väitteen ("tarina on osittain totta"), mutta kumoaa sen merkityksen välittömästi esittämällä ratkaisun, mikä palauttaa keskustelun alkuperäiseen, hallittavissa olevaan kehykseen. Tämä on myönnytyksen jälkeinen paluu alkuperäiseen oletukseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_3da456b757644c46` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept vague assertions like 'it is secure'. STEP 1 (Syntactic Anchor): Find explicit physical validation actions (e.g. 'validated', 'filtered', 'sanitized', 'checked against'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it describes a concrete data validation rule being applied to input or output. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_8f7d6c3cd807442782ec7ac94820cad1) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii konkreettisia datan validointitoimia kuvaavia termejä. Tekoäly ei kuvaa omia sisäisiä prosessejaan, vaan keskittyy pedagogiikkaan. Ankkureita ei löydy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_c2a300ee973d471d99472029cfba1700) - [TRUE]:**
  > *Mitigating exception found: Kun käyttäjä kyseenalaistaa tekoälyn antamien prosenttilukujen alkuperän, tekoäly validoi tai maadoittaa oman heuristiikkansa viittaamalla tunnettuun teoreettiseen malliin. Tämä on konkreettinen validointitoimi, jossa oma väite tarkistetaan ulkoista mallia vasten.  [5. VALIDATION DECISION: PASS]*

---

