# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 186
- Total mismatching atoms: 14
- Variance percentage: 7.5 %
- PASSED -> FAILED (Run 1 -> Run 2): 7
- FAILED -> PASSED (Run 1 -> Run 2): 7
- Other state changes: 0

## Atom: tda_9ab273ce743ac29e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess intent. STEP 1 (Syntactic Anchor): Find an evaluation of success or a positive outcome. STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text details the positive outcome but COMPLETELY OMITs any epistemic boundary markers (e.g. 'however', 'limitations', 'failed to', 'uncertainty'). NEGATIVE CONDITION (RETURN NULL IF MET): limitations are explicitly stated. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.'] | [2. SYNTACTIC ANCHOR: 'on ainoa tapa'] | [3. TARGET NODE: 'however/limitations/uncertainty'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: '...kriisejä ja systeemisiä murtumia...Epävarmuuden Sosiaalinen Polarisointi...'] | [2. SYNTACTIC ANCHOR: 'kriisejä/murtumia/epävarmuuden'] | [3. TARGET NODE: 'however/limitations/failed to/uncertainty'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_61c1b43bc6f5406f
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. EXTRACTION CONDITION: role prefixes exist, focus on 'ai:' output compared to 'user:' input. BANNED LOGIC: Do not evaluate 'coincidence' abstractly. STEP 1 (Syntactic Anchor): Identify a novel concept, specific methodology, or data point introduced by the AI. STEP 2 (Bounding Box): Scan the preceding 'user:' prompt. NEGATIVE CONDITION (RETURN NULL IF MET): the user prompt did NOT explicitly request this concept or methodology. If the user requested it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Sitra näkee tulevaisuuden "postnormaalina aikana", joka on täynnä yllätyksiä, ristiriitaisuuksia ja konflikteja.'] | [2. SYNTACTIC ANCHOR: 'postnormaalina aikana'] | [3. TARGET NODE: 'Miten sitra tämän näkee raporttien perusteella'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'ai: Kyllä, Sitran megatrendien pohjalta voi ehdottomasti yhdistelemällä tuottaa niin kutsuttuja supermegatrendejä... user: Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'] | [2. SYNTACTIC ANCHOR: 'supermegatrendejä'] | [3. TARGET NODE: 'supermegatrendejä'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_247927c98b0c46f8
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rebuttals that provide counter-data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023)...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta** .'] | [2. SYNTACTIC ANCHOR: 'eivät ole vain'] | [3. TARGET NODE: 'rajoite'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_25973a87867690b7
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find single-path commands (e.g., 'just write the final version', 'skip the analysis'). STEP 2 (Bounding Box): Scan the user prompt. EXTRACTION CONDITION: the user actively refuses to explore counter-arguments or alternative models. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user asks for pros and cons. TRACE REQUIREMENT: Explain the missing alternatives in `mechanical_trace`. ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES.

**Run 1 [true]**
> Etsin käyttäjän kehotteista komentoja, jotka ohjaavat tekoälyä tuottamaan lopullisen version ilman vaihtoehtojen tutkimista. Käyttäjän kehotus 'tee kokonaisuudesta raportti, missä Supermegatrendit ovat pääosassa' on suora komento luoda lopullinen tuotos perustuen yhteen valittuun polkuun (supermegatrendit) ilman, että pyydetään vastaväitteitä tai vaihtoehtoisia malleja. Tämä täyttää ehdon kirjaimellisesti.

**Run 2 [false]**
> Mekaaninen tarkistus: Etsin kohdedatasta (chat_log) komentoja, jotka vastaavat 'single-path' -ehtoa, kuten 'kirjoita vain lopullinen versio'. Käyttäjän prosessi on iteratiivinen ja sisältää useita vaiheita, eikä hän aktiivisesti kieltäydy vaihtoehdoista. Päinvastoin, käyttäjä luo uuden vaihtoehdon ('supermegatrendit'). Koska ehto ei täyty, palautan null-arvon direktiivin mukaisesti.

---

## Atom: tda_d335b4457e3e4ac7
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find thought-terminating clichés ('it is simply a matter of', 'there is no alternative', 'period'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: complexity or opposing views are dismissed without data. NEGATIVE CONDITION (RETURN NULL IF MET): data is provided. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Data-driven rebuttals. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.'] | [2. SYNTACTIC ANCHOR: 'ainoa tapa'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.'] | [2. SYNTACTIC ANCHOR: 'ainoa tapa'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_2590fb7ecb6379e7
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate nuance. STEP 1 (Lexical Anchor): Find absolute causal words ('only reason', 'entirely due to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text attributes a highly complex outcome to a single cause without acknowledging any other potential factors. TRACE REQUIREMENT: Document `mechanical_trace`. ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES.

**Run 1 [false]**
> Vaihe 1: Etsin kohdekielisiä (suomi) absoluuttisia kausaalisanoja, kuten 'ainoa syy' tai 'täysin johtuen'. Vaihe 2: Skannasin `Product_Text`-dokumentin. Vaihe 3: En löytänyt lauseita, joissa monimutkainen seuraus olisi redusoitu yhteen ainoaan syyhyn käyttämällä absoluuttisia ilmauksia. Teksti esittää useita toisiinsa kietoutuvia supermegatrendejä, mikä implisiittisesti välttää yhden syyn harhan. Koska kyseessä on käänteinen sääntö (etsitään virhettä) ja virhettä ei löydy, `evidence_found` on `False` ja palautan tyhjän merkkijonon.

**Run 2 [true]**
> Tämä on käänteinen sääntö (Vice). Vaihe 1: Etsin kohdetekstistä (product_text) absoluuttisia kausaalisanoja, kuten 'ainoa syy' tai 'täysin johtuen'. Löysin ilmaisun 'ainoa tapa'. Vaihe 2: Poimintaehto on, että teksti attribuoi monimutkaisen lopputuloksen (pitkän aikavälin vakaus) yhteen ainoaan syyhyn (korjaavaan ja uusintavaan talouteen siirtyminen) tunnustamatta muita tekijöitä. Lause täyttää tämän ehdon kirjaimellisesti. Vaihe 3: Koska sääntörikkomus löytyi, `evidence_found` on `True` ja poimin tarkan lainauksen.

---

## Atom: tda_c45a513f2e724e06
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Koko dokumentti'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton.'] | [2. SYNTACTIC ANCHOR: 'peruuttamaton'] | [3. TARGET NODE: 'Muutos'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_5f71c2e291f1ae4e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept 'fully justified' without a traced reasoning path. STEP 1 (Lexical Anchor): Find causal justification markers (e.g. 'because of risk X', 'to prevent Y', 'therefore blocked'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a security action is paired with an explicit, documented risk assessment. TRACE REQUIREMENT: Document the exact risk assessment linkage in `mechanical_trace`. ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES.

**Run 1 [true]**
> Vaihe 1: Etsin kausaalisia perustelumarkkereita, kuten 'riskin X vuoksi', 'estääkseen Y'. Vaihe 2: Skannasin `product_text` -kohdetta. Vaihe 3: Löysin lauseen "Eetisesti kyseenalaiset AI-ratkaisut aiheutavat maineriskin", joka yhdistää suoraan riskin ("maineriski") sen syyhyn ("Eetisesti kyseenalaiset AI-ratkaisut"). Vastaava toimenpide "Kehitetään ja käytetään teknologiaa eetisesti ja läpinäkyvästi" on esitetty heti perään. Tämä täyttää ehdon, jossa turvallisuustoimi on yhdistetty dokumentoituun riskinarviointiin. Siksi poimin lauseen.

**Run 2 [false]**
> Vaihe 1: Etsin kohdetekstistä ('product_text') kausaalisia perustelumarkkereita, kuten 'koska riski X' tai 'estääkseen Y', jotka yhdistävät turvatoimenpiteen ja riskianalyysin. Vaihe 2: Teksti sisältää liiketoimintastrategisia suosituksia vastauksena tunnistettuihin riskeihin (esim. 'Toimitusketjun lyhentäminen ja läpinäkyvyys vähentävät riskejä'). Nämä eivät kuitenkaan ole säännön vaatimia teknisiä turvatoimenpiteitä (kuten 'salattu', 'estetty'). Vaihe 3: Koska tiukka ehto (tekninen turvatoimi + riskianalyysi) ei täyty, todisteita ei löydy.

---

## Atom: tda_b7ce46fc627dbc7e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find demands for epistemological humility (e.g., 'tell me what you do not know', 'what are the limitations of this analysis'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly commands the AI to state its uncertainties or missing data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Demands for absolute certainty. TRACE REQUIREMENT: Document the logical step-by-step evaluation in `mechanical_trace`. ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES.

**Run 1 [false]**
> Tarkastin `chat_log`-aineiston etsien käyttäjän vaatimuksia episteemisestä nöyryydestä, kuten 'kerro, mitä et tiedä'. Käyttäjän kehotus 'mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila' on pyyntö rajata vastaus realistiseen näkemykseen idealistisen sijaan. Tämä on eräänlainen reunaehdon asettaminen, mutta se ei ole säännön vaatima eksplisiittinen komento, jossa tekoälyä pyydettäisiin ilmaisemaan epävarmuutensa tai tietämyksensä rajat. Käyttäjä ei kysy 'mitkä ovat tämän analyysin rajoitukset', vaan ohjaa tekoälyä tuottamaan tietyntyyppistä sisältöä. Siksi tämä ei täytä säännön tiukkaa ehtoa. Todisteita ei löydy.

**Run 2 [true]**
> Etsin käyttäjän kehotteista vaatimuksia episteemisestä nöyryydestä tai analyysin rajoitusten tunnustamisesta. Leksikaaliset ankkurit kuten 'kerro mitä et tiedä' tai 'mitkä ovat tämän analyysin rajoitukset' ovat ohjeellisia. Käyttäjän kehote 'mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila' vastaa säännön henkeä. Se pakottaa tekoälyn erottamaan spekulatiivisen tai toiveikkaan tulevaisuudenkuvan ('toivetila') siitä, mikä on raportteihin perustuva, maadoitettu näkemys. Tämä on selkeä komento asettaa rajoituksia tuotettavan tiedon luonteelle ja tunnustaa eri tietotyyppien välinen ero. Siksi ehto täyttyy ja sitaatti poimitaan.

---

## Atom: tda_569f87a921a2fb69
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find user instructions that modify an output (e.g., 'change this paragraph to'). STEP 2 (Bounding Box): Scan the interaction. EXTRACTION CONDITION: the user modifies the final output but leaves the original AI system prompt or generative logic exactly the same. NEGATIVE CONDITION (RETURN NULL IF MET): the user alters the underlying instructions/logic. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Deep structural refactoring. TRACE REQUIREMENT: Document the logical step-by-step evaluation in `mechanical_trace`. ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES.

**Run 1 [true]**
> Etsin käyttäjän komentoja, jotka muokkaavat tuotosta muuttamatta taustalla olevaa logiikkaa. Kehote 'poista taulukot ja kerro ne tekstinä' on suora komento muuttaa esitysmuotoa (taulukosta tekstiksi). Tämä ei muuta alkuperäisen tiedon sisältöä tai tekoälyn logiikkaa tiedon generoimiseksi, ainoastaan sen lopullista ulkoasua. Tämä täyttää ehdon täydellisesti.

**Run 2 [false]**
> Mekaaninen tarkistus: Etsin kohdedatasta (chat_log) tilannetta, jossa käyttäjä muokkaa tuotosta, mutta jättää alkuperäisen logiikan ennalleen. Käyttäjä muokkaa tuotosta, mutta hän myös muuttaa perustavanlaatuisesti sen logiikkaa esittelemällä 'supermegatrendit'-käsitteen ja kohdeyleisön. Tämä on 'deep structural refactoring', joka on direktiivissä määritelty negatiivinen ehto. Koska negatiivinen ehto täyttyy, palautan null-arvon.

---

## Atom: tda_31ae4494272845fe
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate the quality of the bridging rule. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023)...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tämä syntyy siitä, että **Luonnon kantokyky murenee**, mikä ajaa suoraan siihen, että **Talouden perusta rakoilee** .'] | [2. SYNTACTIC ANCHOR: 'mikä ajaa suoraan siihen, että'] | [3. TARGET NODE: 'Luonnon kantokyky murenee'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_a2d1fa749b77d3de
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find boundary conditions (e.g., 'assuming that', 'only if', 'the exception is'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly forces the AI to acknowledge a specific edge case or foundational premise. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Broad, unconditional statements. TRACE REQUIREMENT: Map this explicit logic in `mechanical_trace`. ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES.

**Run 1 [true]**
> Etsin käyttäjän kehotteista rajausehtoja (esim. 'olettaen että', 'vain jos'). Kehote 'mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila' asettaa selkeän rajauksen. Se pakottaa tekoälyn erottamaan spekulatiivisen 'toivetilan' ja faktapohjaisen 'näkemyksen suunnasta eteenpäin'. Tämä on eksplisiittinen rajausehto, joka ohjaa tekoälyn tuotosta. Tämä täyttää ehdon.

**Run 2 [false]**
> Mekaaninen tarkistus: Etsin kohdedatasta (chat_log) rajaehtoja, kuten 'olettaen että' tai 'vain jos'. Käyttäjän kehotteet ovat suoria komentoja eivätkä sisällä tällaisia loogisia rajaehtoja. Ehto ei täyty. Palautan null-arvon.

---

## Atom: tda_2dabbdba90a549ae
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find formal citations ('according to the methodology of', 'based on the study by'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the logical rule is explicitly backed by a verifiable external methodology or study. NEGATIVE CONDITION (RETURN NULL IF MET): it's a vague reference ('research shows'). BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Vague references to 'studies' or 'science'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023)...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Sitran näkemys on, että paluuta vanhaan normaaliin ei ole, ja menestyäkseen yritysten on panostettava **tulevaisuusresilienssiin** .'] | [2. SYNTACTIC ANCHOR: 'Sitran näkemys on'] | [3. TARGET NODE: 'Sitran'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c6bcce2b818718a1
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unbounded absolute rules. TRACE REQUIREMENT: Document the boundary condition in `mechanical_trace`. ENFORCEMENT MANDATE: You are a blind extraction engine, NOT a judge. Step 1: Translate Lexical Anchors to the target language (e.g., Finnish) and locate potential text. Step 2: IF AND ONLY IF the EXTRACTION CONDITION is physically explicit in the text, extract the exact_quote. STRICT FIT RULE: Matches must be explicit and literal. Do not stretch definitions, infer implicit meanings, or rationalize away physical matches. If it requires debate, return null. Step 3: IF NOT MET, OR IF A NEGATIVE CONDITION IS PRESENT, RETURN NULL. DO NOT EXPLAIN AWAY FAILURES.

**Run 1 [false]**
> Ohjeen mukaisia rajanvetoa ilmaisevia ankkureita (esim. 'tämä koskee vain', 'soveltamisalan sisällä') ei löytynyt tekoälyn vastauksista (`ai:`-lohkoista) tavalla, joka määrittelisi operatiivisen säännön rajoja. Keskustelun sisältö keskittyy informaation syntetisointiin, ei operatiivisten prosessien tai sääntöjen määrittelyyn.

**Run 2 [true]**
> Suoritin mekaanisen haun `ai:`-lohkoista `chat_log`-aineistossa. Etsin suomenkielisiä vastineita rajanmäärittelyä osoittaville leksikaalisille ankkureille, kuten 'tämä koskee vain' tai 'soveltamisalan sisällä'. Viimeisessä tekoälyn vastauksessa, joka vastaa käyttäjän pyyntöön luoda raportti tietylle yleisölle, tekoäly määrittelee eksplisiittisesti dokumentin soveltamisalan lauseella "Kohderyhmä: Kaupallinen Johtoryhmä". Tämä on suora vastaus käyttäjän asettamaan sääntöön/rajoitteeseen ja määrittelee selvästi operationaalisen rajan (kenelle dokumentti on tarkoitettu). Tämä täyttää ehdon, jossa operationaalisen säännön rajat on eksplisiittisesti määritelty. Siksi poimin tämän sitaatin.

---

