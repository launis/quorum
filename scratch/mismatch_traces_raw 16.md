# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 90.32 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.7998
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.0968
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 18 kpl
- **PASSED -> FAILED:** 7
- **FAILED -> PASSED:** 11
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_7cd559fd662724f5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: AI responses. STEP 1 (Syntactic Anchor): Find user requests for absolute truth without external verification (e.g., 'give me the absolute fact', 'what is the exact truth'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user asks the AI to act as an infallible oracle without providing an external source or document to ground it. NEGATIVE CONDITION (RETURN NULL IF MET): a document or source is provided. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Requests grounded in explicitly provided documents. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Sääntöä ei rikottu. Käyttäjä ei missään vaiheessa pyydä tekoälyltä absoluuttista totuutta. Päinvastoin, käyttäjä haastaa tekoälyn väitteitä ja pyytää ulkoisia lähteitä, mikä on säännön vastakohta.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä ei pyydä tekoälyltä absoluuttista totuutta. Päinvastoin, hän haastaa tekoälyn väitteitä ja pyytää lähteitä, mikä osoittaa kriittistä lähestymistapaa eikä sokeaa luottamusta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0f4ab5b3344ef1a8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not evaluate 'proactivity' subjectively. STEP 1 (Syntactic Anchor): Find temporal reactive markers (e.g. 'after the failure', 'once identified', 'we fixed'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: security measures are ONLY described as post-incident responses without any pre-incident checks. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei kuvaa turvatoimia reaktiivisina tai ainoastaan epäonnistumisen jälkeen tehtyinä. Koko keskustelun sävy on proaktiivinen ja pyrkii ennakoimaan muutoksia.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Mitigating exception found: Tekoäly muuttaa ja tarkentaa aiempaa neuvoaan vasta sen jälkeen, kun se on käynyt läpi (itse tuottamansa) tutkimusviitteet. Tämä on reaktiivinen korjausliike, joka tehdään tietyn tapahtuman jälkeen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_4fb15d2eff06dbb4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not judge 'vagueness' subjectively. STEP 1 (Syntactic Anchor): Find a justification sentence (e.g. 'This is because', 'Due to'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the justification DOES NOT contain any specific domain variables, numbers, or exact verbatim quotes from the input data (relying only on generic templates). NEGATIVE CONDITION (RETURN NULL IF MET): specific variables are present. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii perustelua, joka ei sisällä tiettyjä muuttujia, numeroita tai lainauksia. Lause "Todella hyvä jatkokysymys – koska usein huoli ei synny faktoista, vaan tarinoista ja tulkinnoista" käyttää perusteluna yleistä psykologista havaintoa, joka ei ole ankkuroitu mihinkään spesifiin dataan tai muuttujaan keskustelussa. Se on geneerinen kehystys, joten se täyttää säännön poimintaehdon.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [FALSE]:**
  > *No presence of target concept detected: This is a vice rule. The model consistently provides specific justifications for its claims, often using detailed lists or direct examples from the user's context (e.g., 'Sinun arvo kasvaa, koska: Osaat nähdä bullshitin läpi...'). I could not find an instance of a justification that relied only on generic templates without specific variables.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b65277ca32d4c0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'depth' subjectively. STEP 1 (Syntactic Anchor): Find absolute conclusion words (e.g., 'clearly', 'obviously', 'must be', 'selvästi'). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: the conclusion is presented without a multi-step logical deduction. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [TRUE]:**
  > *Presence detected: The AI's very first response begins with a major, absolute conclusion. The multi-step logical deduction to support this conclusion only follows afterward, it does not precede it.. Exceptions audit: Sääntö etsii johtopäätöksiä, jotka esitetään ilman loogista päättelyketjua. Tekoälyn vastausten rakenne on kuitenkin johdonmukaisesti sellainen, että se esittää väitteen ja perustelee sen välittömästi seuraavissa kappaleissa tai luetelmakohdissa. Säännön kuvaamaa virhettä ei löytynyt.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii absoluuttisia johtopäätöksiä ilman loogista päättelyketjua. Tekoäly käyttää vahvoja johtopäätöksiä, mutta sen rakenne on johdonmukaisesti sellainen, että se esittää ensin johtopäätöksen (esim. otsikkona) ja sitten erittelee sen perustelut vaiheittain (esim. listoilla ja alaotsikoilla). Vaikka perustelut itsessään voivat olla pelkkiä väitteitä, rakenne itsessään muodostaa loogisen päättelyketjun, joten säännön ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0b0cc9976fb0d7d6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'superficial' subjectively. STEP 1 (Syntactic Anchor): Find terms indicating a manual or ad-hoc check (e.g. 'glanced at', 'looks okay', 'basic check'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the verification relies entirely on human intuition rather than a systemic protocol (like OWASP). TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt ankkureita, jotka viittaisivat pinnalliseen, intuitioon perustuvaan tarkistukseen. Tekoälyn analyysit ovat perusteltuja, eivät hätäisiä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Mitigating exception found: Lähdeteksti ei sisällä ilmaisuja, jotka viittaisivat ad-hoc-tarkistuksiin tai intuitioon perustuvaan turvallisuusvarmennukseen. Tekoälyn suorittama diojen analyysi on sisällöllinen, ei tekninen tai turvallisuuteen liittyvä tarkistus.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_653b3f5497b9147e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find explicit external anchoring for uncertainty (e.g., 'due to X, as noted by [Source]'). STEP 2: Map the cognitive friction. EXTRACTION CONDITION: an external citation is used specifically to justify why a variable remains unknown. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [TRUE]:**
  > *Tekoäly käyttää ulkoista lähdettä (Nature, 2025) perustellakseen, miksi opiskelijoiden valmiudet vaihtelevat. Tämä selittää epävarmuutta siitä, miten opiskelijat omaksuvat tekoälyn, ankkuroimalla sen ulkoisen lähteen mainitsemiin muuttujiin (valmius, osaaminen, eettinen ymmärrys).*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [FALSE]:**
  > *Sääntö etsii kohtaa, jossa ulkoista lähdettä käytetään perustelemaan, miksi jokin asia on epävarma tai tuntematon. Tekoäly käyttää lähteitä perustellakseen väitteitään (esim. tekoälyn käytön laajuus), mutta ei nimenomaisesti perustellakseen epävarmuutta. Esimerkiksi, kun se myöntää epävarmuuden prosenttiluvuista, se viittaa tutkimuksen puutteeseen, ei tutkimukseen, joka todistaisi epävarmuuden. Säännön ehto ei täyty.*

---

### Atom-ID: `tda_3da456b757644c46` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept vague assertions like 'it is secure'. STEP 1 (Syntactic Anchor): Find explicit physical validation actions (e.g. 'validated', 'filtered', 'sanitized', 'checked against'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it describes a concrete data validation rule being applied to input or output. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei kuvaa konkreettisia teknisiä datan validointisääntöjä. Keskustelu liikkuu pedagogisella tasolla, ei teknisen järjestelmän kuvauksessa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Mitigating exception found: Tekoäly kuvaa suorittavansa analyysin (validointitoimenpide), jossa se tarkistaa tuottamiaan dioja vasten esihenkilön oletettuja kriteerejä. Tämä on konkreettinen validointisäännön soveltaminen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_25973a87867690b7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find single-path commands (e.g., 'just write the final version', 'skip the analysis'). STEP 2 (Bounding Box): Scan the user prompt. EXTRACTION CONDITION: the user actively refuses to explore counter-arguments or alternative models. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user asks for pros and cons. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Sääntöä ei rikottu. Käyttäjä ei missään vaiheessa aktiivisesti kieltäydy analyysista tai vaihtoehtojen tutkimisesta. Päinvastoin, käyttäjä pyytää jatkuvasti lisää analyysia eri näkökulmista.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää tekoälyä tuottamaan yhteenvedon ilman, että samassa kehotteessa pyydetään vaihtoehtoja tai vasta-argumentteja. Tämä tapahtuu kuitenkin laajan analyysin jälkeen, joten se on osa tuottavaa työnkulkua eikä niinkään analyysin välttelyä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2aec15ab07984f4d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs or system prompts. STEP 1 (Syntactic Anchor): Find 100% certainty markers ('guaranteed', 'undoubtedly', 'always'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the sentence makes a future prediction or subjective assessment using these markers. NEGATIVE CONDITION (RETURN NULL IF MET): it states a mathematical/historical fact. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Mathematical facts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt säännössä määriteltyjä 100 % varmuutta ilmaisevia ankkurisanoja (esim. 'taatusti', 'epäilemättä', 'aina') tai niiden suoria semanttisia vastineita. Vaikka tekoälyn sävy on itsevarma, se ei käytä näitä nimenomaisia leksikaalisia merkitsimiä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Presence detected: Lause on subjektiivinen arvio, joka esitetään absoluuttisella varmuudella ("ratkaisee kaiken"). Se ei ole matemaattinen tai historiallinen fakta, vaan tulevaisuutta koskeva ennustus palautteen laadun tärkeydestä.. Exceptions audit: Sääntö etsii 100% varmuutta ilmaisevia markkereita (esim. 'taatusti', 'epäilemättä', 'aina') subjektiivisen tai tulevaisuutta ennustavan väitteen yhteydessä. Lähdetekstissä ei esiinny näitä spesifejä syntaktisia ankkureita, vaikka yleinen sävy onkin itsevarma.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_e7f3eec588424a86` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'triviality'. STEP 1 (Syntactic Anchor): Find a counter-argument transition (e.g., 'Critics might say', 'Some argue'). STEP 2 (Bounding Box): Scan the paragraph. If the presented counter-argument lacks specific citations, named sources, or numerical data, AND is immediately dismissed. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt säännön määrittelemiä vasta-argumentin siirtymiä, kuten 'kriitikot saattaisivat sanoa'. Tekoäly esitti 'huolestuttavia tarinoita' vastauksena käyttäjän suoraan pyyntöön, ei spontaanina olkinukke-argumenttina.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Presence detected: Tekoäly esittelee vasta-argumentin tai yleisen huolenaiheen "tarinana" ("Tekoäly korvaa opettajat kokonaan"). Se esittää tämän näkemyksen ilman lähteitä tai dataa ja kumoaa sen välittömästi omalla vastaväitteellään, leimaten sen "liioitelluksi + yksinkertaistetuksi". Tämä vastaa säännön kuvausta olkinukke-argumentista.. Exceptions audit: Tekstistä ei löytynyt säännön määrittelemiä syntaktisia ankkureita vasta-argumentin esittämiseen (esim. 'Kriitikot saattavat sanoa'). Vaikka tekoäly käsittelee mahdollisia huolia ('tarinoita'), se tekee sen vastauksena suoraan käyttäjän kysymykseen, eikä rakenna olkinukke-argumentteja omasta aloitteestaan.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_55dfd9cb0adec620` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Kaikkiin tekoälyn tunnistamiin riskeihin (esim. pinnallinen oppiminen) liitetään keskustelussa konkreettisia pedagogisia ratkaisuehdotuksia. Yhtään riskiä ei jätetä käsittelemättä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Presence detected: Tämä on käänteinen sääntö. Tekoäly tunnistaa useita riskejä, mutta ehdottaa johdonmukaisesti niihin pedagogisia ratkaisuja tai lievennyskeinoja. Yhtään riskiä ei jätetä käsittelemättä.. Exceptions audit: Tekoäly tunnistaa pedagogisia riskejä, mutta ne eivät ole järjestelmän teknisiä haavoittuvuuksia, jotka vaatisivat välittömiä teknisiä torjuntatoimia. Ehdotetut toimenpiteet ovat pedagogisia, mikä on kontekstissa asianmukaista.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d204baf0bdf74ff7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit boundary setting markers or key constraint phrases (must be one of: 'this does not apply to', 'a key constraint is', 'our analysis is limited to', 'rajoituksena on'). STEP 2 (Extraction Condition): Extract the exact quote containing the physical anchor. AMBIGUITY PROTOCOL: If the physical anchors are absent or vague, you MUST return JSON null. Speculation is strictly banned.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [TRUE]:**
  > *Teksti sisältää eksplisiittisen rajoituksen asettamisen, kun tekoäly toteaa, että sen aiemmin esittämät prosenttiluvut 'eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan'. Tämä lause toimii selkeänä rajoituksena ja asettaa rajan esitetyn tiedon luonteelle ja luotettavuudelle, mikä vastaa säännön vaatimusta.*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [FALSE]:**
  > *Tekstistä ei löydy säännön vaatimia tarkkoja syntaktisia ankkureita, kuten "rajoituksena on". Lähimpänä oleva kohta, jossa myönnetään prosenttilukujen olevan arvioita, ei käytä vaadittua sanamuotoa.*

---

### Atom-ID: `tda_9ab273ce743ac29e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess intent. STEP 1 (Syntactic Anchor): Find an evaluation of success or a positive outcome. STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text details the positive outcome but COMPLETELY OMITs any epistemic boundary markers (e.g. 'however', 'limitations', 'failed to', 'uncertainty'). NEGATIVE CONDITION (RETURN NULL IF MET): limitations are explicitly stated. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [TRUE]:**
  > *Presence detected: This is an inverse rule. A violation was found. The text makes a very strong positive claim, 'Tekoäly tekee opettajasta tehokkaamman kuin koskaan' (AI makes the teacher more effective than ever). While the overall response structure includes a separate section for risks, this specific section detailing the 'biggest opportunity' presents the positive outcome without any internal epistemic boundary markers like 'however' or 'limitations', thus fulfilling the violation condition.. Exceptions audit: Tekoäly ei esitä positiivisia tuloksia ilman rajoituksia. Se käyttää jatkuvasti rakenteita kuten "mutta", "riski on" tai esittää myönteiset asiat vastapainona kielteisille, mikä osoittaa episteemisten rajojen ymmärrystä. Siksi sääntöä ei rikota.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [FALSE]:**
  > *No presence of target concept detected: This is an inverse rule. The text does not violate the rule because it consistently includes epistemic boundary markers like 'mutta', 'riski on olemassa', and 'osittain totta', and does not present positive outcomes without limitations.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_32ee0cac79ad098e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: Tämä on pahesääntö. Tekstistä ei löytynyt kohtia, joissa olisi käytetty universaaleja termejä ('aina', 'joka tapauksessa') soveltamaan rajoitetusta kontekstista johdettua kausaaliväitettä kaikkiin tilanteisiin. Tekoäly käyttää usein rajaavia ilmauksia, kuten 'erityisesti', 'usein' ja 'tyypillisesti'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Mitigating exception found: Tämä on pahesääntö. Lause "Tieto on jatkuvasti saatavilla → luennointi vähenee" esittää universaalin kausaaliväitteen, joka on johdettu rajatusta kontekstista (tiedon saatavuus) ilman, että lauseessa itsessään tunnustetaan poikkeuksia tai rajoituksia.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c6f705f7a5f94f53` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find an absolute quantifier or declaration of certainty (e.g., 'always', 'undeniably', 'proven', 'fact', '100%'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute quantifier BUT does NOT contain empirical measurement tokens (e.g., 'data', 'measurement', 'study', 'statistics', 'survey') -> ACCEPT. If it contains empirical measurement tokens -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'agreement' or whether an assumption is being confirmed. Evaluate only physical token presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [TRUE]:**
  > *Mitigating exception found: Tämä lause on selkeä varmuuden ilmaus. Kappale, jossa se esiintyy, ei sisällä mitään empiirisiä mittareita, kuten 'data', 'tutkimus' tai 'tilasto', jotka tukisivat väitettä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt absoluuttisia kvantifioijia tai varmuuden ilmauksia (esim. 'aina', 'fakta', '100%'), jotka esiintyisivät ilman empiiriseen mittaamiseen viittaavia sanoja samassa kappaleessa. Kun tekoäly esittää numeerisia väitteitä (esim. prosenttiluvut), se joko myöntää niiden olevan heuristiikkaa tai sitoo ne suoraan tutkimusviitteisiin, mikä rikkoo säännön negatiivisen ehdon.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c1a05b0ce5f88033` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a named alternative model or theory. STEP 2 (Bounding Box): Scan the same paragraph. EXTRACTION CONDITION: the alternative is mentioned but the paragraph contains exactly 0 counter-arguments or comparative data points. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'depth', simply count the data points. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *Tämä on käänteinen sääntö. Sääntöä ei ole rikottu. Tekoäly mainitsee nimetyt mallit ('Diffusion of Innovations (Everett Rogers)' ja 'UTAUT-mallit'), mutta se ei sivuuta niitä. Sen sijaan se käyttää niitä aktiivisesti oman argumenttinsa tukena ja selittää, miten sen oma yksinkertaistettu malli suhteutuu niihin. Näin ollen säännön ehto (mainitseminen ilman vasta-argumentteja) ei täyty.*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Teksti nimeää teorian ("Diffusion of Innovations (Everett Rogers)"), mutta ei esitä sitä vastaan vasta-argumentteja tai vertailevaa dataa. Se ainoastaan selittää, kuinka mallia on sovellettu, mikä on säännön vastainen laiminlyönti.*

---

### Atom-ID: `tda_b8c1d460ccfd9ae4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find listing conjunctions (e.g., 'and', 'also', 'in addition'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: two major domain concepts are placed side-by-side without a relational verb connecting them. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept sentences that explicitly define the relationship between the concepts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [TRUE]:**
  > *Mitigating exception found: The text contains a parenthetical list of major domain concepts `(yrittäjyys + markkinointi + aikuisopetus)`. The '+' symbol acts as a listing conjunction ('and'), and the concepts are presented side-by-side without a relational verb connecting them, which matches the fatal flaw criteria.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [FALSE]:**
  > *No presence of target concept detected: This is an inverse rule. The flaw described (listing major concepts with a conjunction but without a relational verb) was not found in the text. The AI consistently connects concepts with relational verbs or uses structured lists where the relationship is implied by the context, thus avoiding this specific logical flaw.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8d049ce6e39a465c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit transitional doubt words (must be one of: 'however', 'might seem', 'initially', 'kuitenkin', 'aluksi', 'vaikuttaisi'). STEP 2 (Syntactic Chain): Check if this doubt is immediately dismissed (within the same paragraph) to reaffirm the initial automatic conclusion without introducing any new empirical proof, metrics, or citations. AMBIGUITY PROTOCOL: If the doubt anchors are absent, or if the doubt leads to a new productive hypothesis, or if it is supported by new empirical evidence, you MUST return JSON null.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_d8e0475360864e069bc8516c099cd81c) - [FALSE]:**
  > *No presence of target concept detected: The text does not contain an instance where doubt is introduced and then immediately dismissed without new evidence. When the AI uses words like 'mutta' to introduce a counterpoint, it leads to a productive analysis or a more nuanced conclusion, rather than a simple reaffirmation of the initial stance.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_551e0e59a6bc480da2a30f2d4ef0f20b) - [TRUE]:**
  > *Presence detected: Sääntö etsii tilannetta, jossa epäilys tai vasta-argumentti kumotaan välittömästi ilman uutta dataa. Tekoäly esittää huolen "Opiskelijat eivät enää opi mitään itse" ja myöntää sen olevan "osittain totta". Kuitenkin se kumoaa huolen välittömästi väittämällä, että ongelma on "ratkaistavissa pedagogiikalla". Tämä on uusi väite, ei empiirinen todiste, ja se palauttaa keskustelun takaisin alkuperäiseen väitteeseen ilman, että esitettyä epäilystä aidosti käsitellään datalla.. Exceptions audit: Sääntö etsii tilannetta, jossa epäilys hylätään ilman uutta näyttöä. Tekstistä ei löydy sellaista kohtaa. Kun tekoäly käyttää epäilyä ilmaisevia rakenteita (esim. "mutta"), se johtaa uuteen, tuottavaan hypoteesiin, joka perustuu uuteen tietoon (käyttäjän kysymykset, tutkimusviitteet).  [5. VALIDATION DECISION: FAIL]*

---

