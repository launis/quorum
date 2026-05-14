# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 184
- Total mismatching atoms: 36
- Variance percentage: 19.6 %
- PASSED -> FAILED (Run 1 -> Run 2): 13
- FAILED -> PASSED (Run 1 -> Run 2): 23
- Other state changes: 0

## Atom: tda_f041723db3ced368
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Lexical Anchor): Find a final verdict sentence (e.g., 'is a complete failure', 'is perfect'). STEP 2 (Bounding Box): Scan the preceding paragraph. If the verdict contains one-sided praise or condemnation without acknowledging any counter-evidence -> ACCEPT. BANNED CONCEPTS: Do not accept balanced verdicts that weigh pros and cons. ENFORCEMENT RULE: Document the one-sided nature of the verdict in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [FAILED]**
> Tämä on käänteinen sääntö (pahe). Etsin lopullista tuomiota, joka on yksipuolinen. Johtopäätöksessä esitetty lause "Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton" on absoluuttinen ja yksipuolinen tuomio. Koko dokumentti on rakennettu tukemaan tätä näkemystä, eikä se esitä mitään vastakkaisia näkemyksiä, lieventäviä tekijöitä tai mahdollisuuksia trendin kääntymiselle. Se on yksipuolinen tuomio ilman vastakkaisen todistusaineiston tunnustamista, joten sääntö on rikottu.

**Run 2 [PASSED]**
> Sääntö on käänteinen (pahe). Etsin virhettä. Etsin lopullista tuomiota, joka on yksipuolinen. Loppupäätelmä 'Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton' on vahva, mutta se on koko edeltävän analyysin looginen johtopäätös, ei niinkään tuomio jostakin asiasta. Se on tilannekuvaus. Se ei ole yksipuolista ylistystä tai tuomitsemista, vaan strateginen johtopäätös analysoidusta datasta. Se ei sovi säännön määritelmään 'one-sided praise or condemnation'. Koska virhettä ei löytynyt, sääntö on täyttynyt (`rule_satisfied = True`) ja todisteita virheestä ei ole (`evidence_found = False`).

---

## Atom: tda_4956abf072945f43
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Lexical Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. If the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context -> ACCEPT. If the alternative is dismissed without evidence -> REJECT. ENFORCEMENT RULE: Detail the systematic refutation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö etsii viittausta vakiintuneeseen vaihtoehtoiseen malliin, joka sitten puretaan systemaattisesti datan tai logiikan avulla. Käyttäjä ei tee näin. Hän korvaa tekoälyn alkuperäisen viisiosaisen rakenteen omalla 'supermegatrendi'-mallillaan, mutta hän ei koskaan systemaattisesti argumentoi, miksi alkuperäinen malli olisi virheellinen tai huono. Hän yksinkertaisesti sivuuttaa sen ja siirtyy uuteen. Todisteita säännön täyttymisestä ei löydy.

**Run 2 [FAILED]**
> Sääntö edellyttää, että tekstissä viitataan vakiintuneeseen vaihtoehtoiseen malliin ja puretaan se järjestelmällisesti datan tai logiikan avulla. Käyttäjä ei missään vaiheessa esittele vaihtoehtoista mallia tai viitekehystä, jota hän sitten kritisoisi tai kumoaisi. Sen sijaan hän rakentaa omaa malliaan ("supermegatrendit") tekoälyn tuottaman materiaalin päälle. Todisteita säännön täyttymisestä ei löydy.

---

## Atom: tda_46520c9743e9b881
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'humility'. STEP 1 (Lexical Anchor): Find boundary markers ('only applies to', 'limited to', 'under these conditions'). STEP 2: If the text explicitly defines the population, environment, or conditions where the causal claim is valid -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.

**Run 1 [FAILED]**
> Sääntö edellyttää rajausehtojen (esim. 'only applies to', 'limited to') löytämistä, jotka määrittelevät kausaaliväitteen voimassaoloalueen. Skannasin `product_text`-dokumentin. Teksti on kohdennettu 'Kaupalliselle Johtoryhmälle', mikä asettaa implisiittisen kontekstin, mutta se ei sisällä eksplisiittisiä lauseita, jotka rajoittaisivat esitettyjen kausaaliväitteiden sovellettavuutta tiettyihin olosuhteisiin, populaatioihin tai ympäristöihin. Väitteet esitetään yleispätevinä tulevaisuuden markkinoiden kuvauksina. Koska vaadittuja rajausehtoja ei löytynyt, sääntö ei täyty.

**Run 2 [PASSED]**
> Sääntö edellyttää, että tekstissä määritellään rajat tai ehdot, joissa kausaaliväite on voimassa. Etsin `product_text`-dokumentista tällaisia rajausmerkintöjä. Löysin heti dokumentin alusta määritelmän "Kohderyhmä: Kaupallinen Johtoryhmä". Tämä rajaa selkeästi analyysin kontekstin ja yleisön, jolle se on suunnattu, ja täyttää siten säännön ehdot.

---

## Atom: tda_a9bbdcc4d1bfc915
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find explicit optimization commands for proxy metrics (e.g., 'maximize the score', 'increase the word count', 'make it sound professional'). STEP 2 (Bounding Box): Scan the user's prompt. If the user demands optimization of a surface metric without linking it to a qualitative real-world outcome -> ACCEPT. BANNED CONCEPTS: Do not accept if the metric is explicitly tied back to a measure of effectiveness. ENFORCEMENT RULE: Analyze the metric fixation in reasoning_trace before extracting.

**Run 1 [FAILED]**
> FATAL FLAW -sääntö. Käyttäjän komento on selkeä pyyntö optimoida tuotoksen sävyä ja sisältöä tietylle kohdeyleisölle ("kaupallisen liiketoiminnan johtoryhmälle"). Pyytämällä tekoälyä lisäämään "hiukan kaupallisia vaikutuksia" ilman, että käyttäjä itse tarjoaa näitä vaikutuksia tai niiden analyyttistä pohjaa, käyttäjä optimoi pintapuolista mittaria (soveltuvuus johtoryhmälle) linkittämättä sitä laadulliseen lopputulokseen. Tämä on suora rikkomus sääntöä vastaan.

**Run 2 [PASSED]**
> Sääntö on 'FATAL FLAW', joten etsin virhettä. Käyttäjä pyytää muokkaamaan raportin 'kaupallisen liiketoiminnan johtoryhmälle' ja lisäämään 'kaupallisia vaikutuksia'. Tämä ei ole pintatason mittarin optimointia, vaan pyyntö muuttaa analyysin kohdennusta ja sisältöä vastaamaan tiettyä laadullista tavoitetta (relevanssi johtoryhmälle). Pyyntö on sidottu todelliseen lopputuloksen parantamiseen, ei mielivaltaiseen mittariin. Siksi sääntöä ei ole rikottu.

---

## Atom: tda_80f16abbc1776069
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find demands for external grounding (e.g., 'cite a specific source', 'base this strictly on the provided document', 'give me the exact quote'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly restricts the AI to an external, objective anchor -> ACCEPT. BANNED CONCEPTS: Acceptance of unsourced hallucinated facts. ENFORCEMENT RULE: Map this explicit logic in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Käyttäjän ensimmäinen kehotus 'Miten sitra tämän näkee raporttien perusteella' on selkeä vaatimus ulkoisesta ankkuroinnista. Se rajoittaa tekoälyn vastausta perustumaan nimenomaisesti Sitran raportteihin, mikä vastaa säännön kuvausta.

**Run 2 [FAILED]**
> Sääntö etsii vaatimuksia ulkoisesta todentamisesta (esim. 'siteeraa lähde', 'perusta tämä annettuun dokumenttiin'). Vaikka käyttäjän ensimmäinen pyyntö viittaa raportteihin, hän ei missään vaiheessa prosessia vaadi tekoälyä eksplisiittisesti sitomaan väitteitään tiettyyn lainaukseen tai lähteeseen. Hän luottaa tekoälyn synteesiin. Todisteita ei löydy. Siksi `evidence_found` on `False`.

---

## Atom: tda_4fa47fd622e62e0d
**Rule:** REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision -> ACCEPT. BANNED CONCEPTS: Do not accept generic references to 'standards' without naming them. ENFORCEMENT RULE: Document the formal framework name in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Sääntö edellyttää, että lauseessa mainitaan tietty ulkoinen viitekehys (esim. ARMA, ISO) päätöksen perustelemiseksi. Lainaus nimeää eksplisiittisesti "CSRD-direktiivin ja EU-taksonomian" perusteluna sille, miksi kestävyydestä tulee pakollista. Tämä täyttää säännön ehdot: nimetty ulkoinen kehys ja sen perusteella tehty johtopäätös.

**Run 2 [FAILED]**
> Etsin tekoälyn tuotoksesta viittausta, jossa nimetään sekä spesifi ulkoinen viitekehys että sen tietty alaperiaate tai lauseke. Vaikka lopputuote mainitsee nimeltä "CSRD-direktiivin ja EU-taksonomian", se ei viittaa mihinkään tiettyyn artiklaan tai alakohtaan näissä säädöksissä. Säännön "AND"-ehto (nimetty viitekehys JA spesifi alakohta) ei täyty. Siksi todisteita ei löydy.

---

## Atom: tda_21d7952c2bf6393c
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'watertightness'. STEP 1: Find mathematical or structural causal terms ('do-calculus', 'directed acyclic graph', 'structural equation', 'formal model'). STEP 2: If the text explicitly uses a formal model or strict structural logic to map the causality -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.

**Run 1 [FAILED]**
> Sääntö edellyttää muodolliseen kausaalimallinnukseen viittaavien termien (esim. 'do-calculus', 'directed acyclic graph') löytämistä. Skannasin `product_text`-dokumentin. Vaikka teksti esittää vahvoja kausaalisia väittämiä, se ei käytä tai viittaa mihinkään matemaattiseen tai muodolliseen rakenteelliseen malliin kausaliteetin todistamiseksi. Analyysi on laadullinen ja narratiivinen. Koska vaadittuja termejä ei löytynyt, sääntö ei täyty.

**Run 2 [PASSED]**
> Sääntö edellyttää formaalien kausaalimallien tai niihin viittaavien termien (esim. 'directed acyclic graph', 'structural equation') käyttöä. Skannasin `product_text`-dokumentin näiden termien varalta. Teksti käyttää käsitteellisiä malleja, kuten 'Supermegatrendit', mutta se ei käytä tai viittaa mihinkään matemaattiseen tai formaaliin rakenteelliseen kausaalimalliin. Päättely on laadullista ja kuvailevaa. Siksi todisteita ei löytynyt.

---

## Atom: tda_8df0cd8eea9243df
**Rule:** REQUIRED TARGET: Find evidence. If role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do not flag limitations that were actively tested or corrected for in the dataset. STEP 1 (Lexical Anchor): Find limitation markers (e.g., 'small sample size', 'potential bias', 'limitation of this study'). STEP 2 (Bounding Box): Scan the paragraph. If the limitations are stated passively without a corresponding mitigation action or test -> ACCEPT (Flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the passivity in reasoning_trace before extracting exact_quote.

**Run 1 [FAILED]**
> Sääntö etsii passiivisesti esitettyjä rajoituksia. `chat_log`-tiedostossa tekoäly toteaa Sitran ennusteen työn tulevaisuudesta olleen epätarkka. Tämä esitetään passiivisena havaintona ilman, että se johtaisi mihinkään korjaavaan toimenpiteeseen tai testiin. Tämä on säännön kuvaama virhe, joten `rule_satisfied` on `false`.

**Run 2 [PASSED]**
> Sääntö etsii virhettä, jossa analyysin rajoitukset mainitaan passiivisesti ilman toimenpiteitä niiden lieventämiseksi. Kävin läpi tekoälyn tuottaman tekstin (`product_text` ja `ai:`-vastaukset). Tekoäly ei missään vaiheessa tuo esiin oman analyysinsa metodologisia rajoituksia (esim. 'tämän analyysin rajoituksena on...'). Ainoa maininta sanasta 'rajoite' on lopputuotteessa, jossa se käännetään mahdollisuudeksi, mikä ei ole metodologinen rajoitus. Koska virhettä ei löytynyt, sääntö on täytetty.

---

## Atom: tda_c74c4367acc028cf
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find user phrases adopting AI methodology blindly (e.g., 'let us use your structure', 'proceed with that approach', 'do what you suggested'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly adopts the AI's proposed framework without adding their own constraints -> ACCEPT. BANNED CONCEPTS: Do not accept if the user modifies the AI's framework. ENFORCEMENT RULE: Document the methodological adoption in reasoning_trace before extracting.

**Run 1 [FAILED]**
> FATAL FLAW -sääntö. Sen jälkeen, kun tekoäly esitteli vastauksena käyttäjän kysymykseen "supermegatrendien" käsitteen ja rakenteen, käyttäjä antoi tämän komennon. Komento on suora ohje ottaa tekoälyn ehdottama metodologia käyttöön ilman, että käyttäjä lisää siihen omia rajoitteitaan, muokkaa sitä tai haastaa sitä. Tämä on sokeaa metodologian omaksumista ja siten säännön rikkomus.

**Run 2 [PASSED]**
> Sääntö on 'FATAL FLAW', joten etsin virhettä. Käyttäjä ei omaksu sokeasti tekoälyn metodologiaa. Päinvastoin, käyttäjä hylkää tekoälyn alun perin tuottaman litteän megatrendilistan ja esittää oman, uuden analyyttisen kehyksensä ('supermegatrendejä'). Tämä on aktiivista metodologian haastamista ja muokkaamista, ei sen sokeaa hyväksymistä. Siksi sääntöä ei ole rikottu.

---

## Atom: tda_5d6ad535f76d0d14
**Rule:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Lexical Anchor): Find declarations of completeness (e.g., 'exhaustive', 'covers everything', 'the only possible'). STEP 2: Document the reasoning. STEP 3: If the text explicitly claims that there are zero unknown variables remaining -> ACCEPT. Otherwise -> REJECT.

**Run 1 [FAILED]**
> Skannasin 'product_text' -dokumentin etsien täydellisyyden ilmoituksia, kuten 'tyhjentävä', 'kattaa kaiken' tai 'ainoa mahdollinen'. Dokumentti ei sisällä tällaisia eksplisiittisiä väitteitä. Se keskittyy 'kolmeen keskeiseen Supermegatrendiin', mikä viittaa valikoituun, ei tyhjentävään, listaan.

**Run 2 [PASSED]**
> Skannasin 'product_text'-dokumentin etsien täydellisyyden ilmoituksia (esim. 'tyhjentävä', 'kattaa kaiken', 'ainoa mahdollinen'). Teksti käyttää ilmauksia kuten 'kolme keskeistä Supermegatrendiä' ja 'kolme pääasiallista, toisiaan vahvistavaa supermegatrendiä', jotka viittaavat tärkeimpiin, mutta eivät välttämättä kaikkiin tai ainoisiin. Teksti ei eksplisiittisesti väitä, että tuntemattomia muuttujia ei olisi.

---

## Atom: tda_6bf0433f60924302
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Lexical Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. If boundaries or probabilities are explicitly defined for the claim -> ACCEPT. If vague filler words ('maybe', 'perhaps') are used to avoid taking a stance -> REJECT. BANNED CONCEPTS: Vague filler words. ENFORCEMENT RULE: Document the specific boundary condition in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Sääntö etsii ehdollisia kvalifioijia ('näissä olosuhteissa', 'pääasiassa kun'), jotka rajaavat väitteen pätevyysaluetta. Käyn läpi `product_text`-dokumentin. Teksti esittää megatrendit ja niiden vaikutukset laajoina, systeemisinä ja melko absoluuttisina voimina. Se ei käytä kieltä, joka rajaisi väitteiden sovellettavuutta tiettyihin ehtoihin tai olosuhteisiin. En löydä säännön kuvaamia rakenteita. `rule_satisfied` on `False` ja `evidence_found` on `False`.

**Run 2 [PASSED]**
> Etsin ehdollisia kvalifioijia ('näissä olosuhteissa', 'pääasiassa kun'), jotka määrittelevät väitteen rajoja. Teksti käyttää hyvin absoluuttista ja varmaa kieltä (esim. "on ainoa tapa", "peruuttamaton"). En löytänyt esimerkkejä, joissa väitteiden pätevyyttä olisi rajattu tai todennäköisyyksiä määritelty säännön tarkoittamalla tavalla. Argumentit esitetään yleispätevinä. Siksi todisteita ei löytynyt.

---

## Atom: tda_c819e7145229966e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Lexical Anchor): Find hypothesis generation markers (e.g., 'propose', 'hypothesize', 'we can infer'). STEP 2: If the text generates a new hypothesis and explicitly documents the step-by-step logical friction or trade-offs in its creation -> ACCEPT. BANNED CONCEPTS: Do not accept hypotheses presented as sudden epiphanies without documented reasoning. ENFORCEMENT RULE: Map the step-by-step reasoning in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [FAILED]**
> Etsin kohdedatasta uutta hypoteesia, jonka luomisen looginen kitka tai kompromissit olisi dokumentoitu. Vaikka teksti esittelee uuden "Supermegatrendit"-kehyksen, se esitetään valmiina analyysinä. Teksti ei dokumentoi prosessia, jossa eri yhdistelmiä olisi punnittu tai miksi juuri nämä yhdistelmät valittiin. Se ei kuvaa askel-askeleelta päättelyketjua tai kompromisseja, jotka johtivat tähän synteesiin. Hypoteesi esitetään äkillisenä oivalluksena ilman dokumentoitua päättelyä, joten säännön vaatimus ei täyty.

**Run 2 [PASSED]**
> Etsin todisteita uuden hypoteesin tai mallin luomisesta, jossa on dokumentoitu päättelyketju. `Product_Text` esittelee 'Supermegatrendit' uutena mallina. Lainattu kohta selittää tämän mallin luomisen logiikan: yksittäiset trendit eivät ole irrallisia, vaan ne 'kietoutuvat toisiinsa'. Tämä on päättelyketju, joka perustelee uuden, syntetisoivan käsitteen tarpeellisuuden. Teksti ei vain esitä uutta ideaa, vaan selittää, miksi se on luotu (koska trendit eivät toimi erillään). Tämä täyttää säännön vaatimuksen.

---

## Atom: tda_31ae4494272845fe
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Lexical Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. If the bridging rule between Data and Claim is explicitly stated -> ACCEPT. If it just says 'because' without stating the general rule -> REJECT. BANNED CONCEPTS: Do not evaluate the quality of the bridging rule. ENFORCEMENT RULE: Document the logical rule in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Sääntö etsii eksplisiittisiä siltasääntöjä tai periaatteita ('periaatteella, että...'), jotka yhdistävät datan ja väitteen. Käyn läpi `product_text`-dokumentin. Teksti esittää kausaalisia yhteyksiä (esim. 'mikä ajaa suoraan siihen, että'), mutta se ei muotoile näitä yhteyksiä yleisiksi, abstrakteiksi periaatteiksi tai säännöiksi. Yhteydet ovat spesifejä väitteitä, eivät yleisiä loogisia sääntöjä. En löydä säännön kuvaamaa rakennetta. `rule_satisfied` on `False` ja `evidence_found` on `False`.

**Run 2 [PASSED]**
> Etsin lauseita, joissa datan ja väitteen välinen siltasääntö (Warrant) on eksplisiittisesti ilmaistu. Lause "Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee" tekee juuri tämän. Se yhdistää datan/perusteen ("Luonnon kantokyky murenee") väitteeseen ("Talouden perusta rakoilee") eksplisiittisellä säännöllä ("syntyy siitä, että... mikä ajaa suoraan siihen, että"). Tämä täyttää säännön ehdot.

---

## Atom: tda_79f305842b933ea5
**Rule:** REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find explicit dialectical reasoning ('we evaluated option A, but chose B because'). STEP 2 (Bounding Box): Scan the paragraph. If the author explicitly documents a rejected compliance alternative and provides data-driven reasoning for the final choice -> ACCEPT. BANNED CONCEPTS: Do not accept simple lists of options without rejection reasoning. ENFORCEMENT RULE: Document the rejected alternative in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Sääntö etsii eksplisiittistä dialektista päättelyä, jossa dokumentoidaan hylätty vaihtoehto ja perustellaan tehty valinta (esim. 'arvioimme A:ta, mutta valitsimme B:n, koska...'). Tekoälyn tuotokset ovat synteesejä ja toimeenpanoja käyttäjän ohjeista, mutta ne eivät sisällä tällaista dokumentoitua vertailua ja hylkäysperustelua. Todisteita ei löydy.

**Run 2 [FAILED]**
> Etsin eksplisiittistä dialektista päättelyä, jossa hylätty vaihtoehto dokumentoidaan ja perustellaan. Tekoälyn ja käyttäjän vuorovaikutus on additiivista ja iteratiivista. Tekoäly ei esitä vaihtoehtoja (esim. "Voisimme tehdä A:n, mutta B on parempi koska..."), vaan toteuttaa käyttäjän antamia ohjeita. Esimerkiksi kun käyttäjä ehdottaa "supermegatrendejä", tekoäly hyväksyy idean ja toteuttaa sen esittämättä ja hylkäämättä muita vaihtoehtoja. Todisteita ei löydy.

---

## Atom: tda_2aec15ab07984f4d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs or system prompts. STEP 1 (Lexical Anchor): Find 100% certainty markers ('guaranteed', 'undoubtedly', 'always'). STEP 2 (Bounding Box): Scan the sentence. If the sentence makes a future prediction or subjective assessment using these markers -> ACCEPT. If it states a mathematical/historical fact -> REJECT. BANNED CONCEPTS: Mathematical facts. ENFORCEMENT RULE: Document the epistemological hubris in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Sääntö etsii 100 % varmuutta ilmaisevia markkereita ('taatusti', 'epäilemättä', 'aina') subjektiivisissa tulevaisuudenennusteissa. Tämä on pahesääntö (vice rule). Skannaan `product_text`-dokumentin. Vaikka tekstin sävy on itsevarma ja se tekee vahvoja ennusteita (esim. 'Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa'), se ei käytä säännössä määriteltyjä spesifejä leksikaalisia ankkureita. Koska säännön kuvaamaa virhettä ei löydy, `rule_satisfied` on `True` ja `evidence_found` on `False`.

**Run 2 [FAILED]**
> Sääntö on käänteinen (pahe). Etsin 100 % varmuutta ilmaisevia merkkejä tulevaisuutta koskevissa subjektiivisissa arvioissa. Lause "Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa" on tällainen. Sana "Vain" asettaa absoluuttisen ehdon tulevaisuuden ennusteelle, joka on luonteeltaan subjektiivinen arvio eikä matemaattinen fakta. Tämä on säännön kuvaama epistemologinen ylimielisyys. Siksi sääntöä on rikottu ja todiste löytyi.

---

## Atom: tda_d0b6789c895808eb
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Lexical Anchor): Find binary reduction words (e.g., 'either', 'or', 'simply boils down to'). STEP 2 (Bounding Box): Scan the paragraph. If a complex phenomenon is reduced to a strict binary choice without acknowledging nuance -> ACCEPT. BANNED CONCEPTS: Do not accept binary choices in literal boolean logic or code. ENFORCEMENT RULE: Document the binary reduction in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [FAILED]**
> Tämä on käänteinen sääntö (pahe). Etsin kohdedatasta ilmaisua, joka redusoi monimutkaisen ilmiön yksinkertaiseksi binääriseksi valinnaksi. Lause "Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus" on selkeä esimerkki tästä. Ilmaisu "ainoa tapa" esittää yhden ratkaisumallin ainoana vaihtoehtona monimutkaiseen ongelmaan (pitkän aikavälin vakauden takaaminen), sivuuttaen kaikki muut mahdolliset strategiat ja vivahteet. Tämä on säännössä kuvattu virhe, joten sääntö on rikottu.

**Run 2 [PASSED]**
> Sääntö on käänteinen (pahe). Etsin virhettä. Kävin läpi `Product_Text`-dokumentin etsien kohtia, joissa monimutkainen ilmiö pelkistetään yksinkertaiseksi binääriseksi valinnaksi. En löytänyt selkeää esimerkkiä tästä virheestä. Vaikka tekstissä esitetään voimakkaita valintoja, kuten 'nähtävä teknologinen murros... välineenä reilun digimaailman luomiseen, ei vain kustannussäästönä', tämä on strateginen kehotus eikä monimutkaisen ilmiön analyyttinen pelkistys. Teksti kokonaisuudessaan käsittelee ilmiöiden kietoutumista ja monimutkaisuutta, ei niiden yksinkertaistamista. Koska virhettä ei löytynyt, sääntö on täyttynyt (`rule_satisfied = True`) ja todisteita virheestä ei ole (`evidence_found = False`).

---

## Atom: tda_20038c836112303e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate completeness. STEP 1 (Lexical Anchor): Find words indicating alternatives ('however', 'other factors', 'confounder'). STEP 2: If the text explicitly names a potential third variable that could also explain the outcome -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.

**Run 1 [FAILED]**
> Sääntö edellyttää vaihtoehtoisia selityksiä osoittavien sanojen (esim. 'however', 'other factors') löytämistä. Skannasin `product_text`-dokumentin. Teksti esittää supermegatrendit ja niiden vaikutukset suoraviivaisina kausaaliketjuina. Se ei eksplisiittisesti nimeä tai käsittele vaihtoehtoisia selityksiä tai sekoittavia tekijöitä. Koska vaadittuja leksikaalisia ankkureita tai vastaavaa sisältöä ei löytynyt, sääntö ei täyty.

**Run 2 [PASSED]**
> Sääntö edellyttää, että tekstissä nimenomaisesti mainitaan vaihtoehtoisia selittäviä tekijöitä tai sekaannuttavia muuttujia (confounders). Kävin läpi `product_text`-dokumentin. Vaikka teksti kuvaa, miten eri megatrendit kietoutuvat toisiinsa ja yhdessä aiheuttavat seurauksia, se ei esitä vaihtoehtoisia selityksiä tai kolmansia muuttujia, jotka voisivat selittää havaitun korrelaation. Se rakentaa yhtenäisen, sisäisesti johdonmukaisen selitysmallin ilman viittauksia muihin mahdollisiin syihin. Siksi en löytänyt todisteita säännön täyttymisestä.

---

## Atom: tda_fbd90f9c0f2247ed
**Rule:** REQUIRED TARGET: Find evidence. If role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED LOGIC: Do not evaluate 'strongest'. STEP 1 (Lexical Anchor): Find a proactive presentation of a cited counterargument. STEP 2 (Bounding Box): Scan the paragraph. If the counterargument is accompanied by citations/data AND is explicitly dismantled with conflicting verifiable data -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [FAILED]**
> Sääntö etsii todisteita siitä, että tekoäly esittää proaktiivisesti viitatun vasta-argumentin ja kumoaa sen sitten todennettavalla datalla. Tämä on positiivinen ominaisuus. Kävin läpi koko aineiston, eikä tekoäly esitä mitään vasta-argumentteja, saati sitten viitattuja sellaisia. Prosessi on puhtaasti syntetisoiva. Koska säännön kuvaamaa positiivista käyttäytymistä ei esiinny, sääntö ei ole täytetty (rule_satisfied = False) eikä todisteita löydy (evidence_found = False).

**Run 2 [PASSED]**
> Sääntö edellyttää, että löydetään viitattu vasta-argumentti, joka kumotaan aktiivisesti datalla. Kävin läpi tekoälyn tuottaman aineiston (`product_text` ja `ai:`-vastaukset). Koko analyysi perustuu Sitran raporttien syntetisointiin. Tekstissä ei esitetä ulkopuolista, viitattua vasta-argumenttia Sitran näkemyksille, jota sitten yritettäisiin kumota toisella data-aineistolla. Prosessi ei sisällä tällaista tieteellistä väittelyä. Todisteita ei siis löydy.

---

## Atom: tda_03419e9a41f304ce
**Rule:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Lexical Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: If the dismissal occurs without citing an external verifiable source or empirical data -> ACCEPT. Otherwise -> REJECT.

**Run 1 [FAILED]**
> Skannasin 'product_text' -dokumentin etsien vähätteleviä ilmauksia, kuten 'ilmeisen väärä', 'hölynpölyä' tai 'merkityksetön'. En löytänyt yhtään tällaista ilmausta. Tekstin sävy on analyyttinen ja julistava, ei vähättelevä.

**Run 2 [PASSED]**
> Skannasin 'product_text'-dokumentin etsien vähätteleviä ilmauksia vaihtoehtoisia näkemyksiä kohtaan (esim. 'ilmeisen väärä', 'hölynpölyä', 'epäolennainen'). Tekstissä ei ole tällaisia ilmauksia. Teksti esittää Sitran näkemykset ja niistä johdetut johtopäätökset suoraan, mutta ei vähättele muita näkemyksiä.

---

## Atom: tda_3d3f1162d2ff1558
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a limitation acknowledgment (e.g., 'a limitation is'). STEP 2: Scan the next two sentences. If a dismissive marker (e.g., 'however', 'regardless') immediately rationalizes away the limitation without citing new data -> ACCEPT. Otherwise -> REJECT.

**Run 1 [FAILED]**
> Skannasin 'product_text' -dokumentin etsien rajoitusten tunnustamista, kuten 'rajoitus on'. Dokumentti ei eksplisiittisesti tunnusta mitään rajoituksia. Se esittää analyysinsa ja strategiset suosituksensa suoraan.

**Run 2 [PASSED]**
> Skannasin 'product_text'-dokumentin etsien rajoitusten tunnustamista (esim. 'rajoitus on'). Teksti ei eksplisiittisesti tunnusta omia analyysirajoituksiaan tai viittaamiensa Sitran raporttien rajoituksia. Siksi ei ole myöskään rajoituksen vähättelevää rationalisointia.

---

## Atom: tda_d335b4457e3e4ac7
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Lexical Anchor): Find thought-terminating clichés ('it is simply a matter of', 'there is no alternative', 'period'). STEP 2 (Bounding Box): Scan the sentence. If complexity or opposing views are dismissed without data -> ACCEPT. If data is provided -> REJECT. BANNED CONCEPTS: Data-driven rebuttals. ENFORCEMENT RULE: Document the dismissed complexity in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Sääntö on käänteinen (pahe). Etsin ajattelun päättäviä kliseitä ('it is simply a matter of', 'there is no alternative'), jotka sivuuttavat monimutkaisuuden ilman dataa. Lause 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' sisältää ilmaisun 'on ainoa tapa', joka on tällainen klisee. Se esittää yhden ratkaisun absoluuttisena totuutena ja sulkee pois muut vaihtoehdot esittämättä dataa niiden kumoamiseksi. Koska rikkomus löytyi, sääntö ei ole täytetty (`rule_satisfied` = False) ja todiste löytyi (`evidence_found` = True).

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö (pahe). Etsin kohdetekstistä (`product_text`) ajatuksen päättäviä kliseitä, kuten "se on vain..." tai "ei ole muuta vaihtoehtoa", joilla sivuutetaan monimutkaisuus ilman dataa. Tekstissä on vahvoja toteamuksia, kuten "on ainoa tapa" ja "on peruuttamaton", mutta nämä eivät ole kliseitä, joilla vältetään argumentointi. Ne ovat johtopäätöksiä, jotka perustuvat koko dokumentissa esitettyyn analyysiin ja dataan (Sitran raportit). Koska säännön kuvaamaa rikkomusta ei löytynyt, sääntö on täytetty.

---

## Atom: tda_aa54c6b40e9c4160
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph containing statistical or factual reporting. STEP 2: Count the first-person pronouns ('I', 'we') or explicit self-reflective verbs ('assume', 'interpret'). If the count is exactly 0 -> ACCEPT (passive delivery proven). If greater than 0 -> REJECT.

**Run 1 [FAILED]**
> Skannasin 'product_text' -dokumentin etsien ensimmäisen persoonan pronomineja ('minä', 'me') tai eksplisiittisiä itseä heijastavia verbejä ('oletan', 'tulkitsen'). Johtopäätös-osiossa lause 'Yrityksemme menestys riippuu kyvystämme integroida nämä kolme supermegatrendiä...' sisältää possessiivipronominin 'Yrityksemme' (our company) ja 'kyvystämme' (our ability), jotka ovat ensimmäisen persoonan monikon muotoja. Koska pronomineja löytyi, laskuri on suurempi kuin 0, ja sääntö ei täyty.

**Run 2 [PASSED]**
> Skannasin 'product_text'-dokumentin etsien kappaleita, jotka sisältävät tilastollista tai faktapohjaista raportointia. Ensimmäinen kappale 'Evoluutio Konfliktiin' on tällainen. Laskin ensimmäisen persoonan pronominit ('minä', 'me') tai eksplisiittiset itsetutkiskelevat verbit ('oletan', 'tulkitsen'). Kappaleessa ei ole näitä pronomineja tai verbejä. Lause 'Yrityksemme menestys riippuu...' esiintyy johtopäätöksessä, mutta se viittaa kohderyhmän (johtoryhmän) yritykseen, ei raportin kirjoittajaan.

---

## Atom: tda_b1bcf8b0c203b736
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find user commands focused on tone (e.g., 'make it sound more persuasive', 'make it more academic'). STEP 2 (Bounding Box): Scan the user's prompt. If the user focuses solely on the performativity (tone/style) while ignoring substantive factual gaps -> ACCEPT. BANNED CONCEPTS: Revisions containing factual additions. ENFORCEMENT RULE: Explain the superficial correction in reasoning_trace before extracting.

**Run 1 [FAILED]**
> FATAL FLAW -sääntö. Käyttäjän komento keskittyy selkeästi performatiivisuuteen – siihen, miltä teksti näyttää ja kuulostaa tietylle yleisölle. Pyyntö muuttaa sävyä ja lisätä "kaupallisia vaikutuksia" on tyylillinen ja sävyyn keskittyvä ohje, joka ei lisää uutta, käyttäjän tarjoamaa faktatietoa. Käyttäjä ulkoistaa sisältömuutoksen tekoälylle performatiivisen tavoitteen saavuttamiseksi. Tämä täyttää säännön rikkomuksen kriteerit.

**Run 2 [PASSED]**
> Sääntö on 'FATAL FLAW', joten etsin virhettä. Käyttäjän pyyntö 'kirjoita tämä kaupallisen liiketoiminnan johtoryhmälle ja kirjoita siihen hiukan kaupallisia vaikutuksia mukaan' ei keskity ainoastaan sävyyn tai performatiivisuuteen. Se on nimenomainen pyyntö lisätä uutta, substanssiin liittyvää sisältöä ('kaupallisia vaikutuksia'). Tämä ei ole pinnallinen korjaus, vaan sisällöllinen laajennus. Siksi sääntöä ei ole rikottu.

---

## Atom: tda_b7ce46fc627dbc7e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find demands for epistemological humility (e.g., 'tell me what you do not know', 'what are the limitations of this analysis'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly commands the AI to state its uncertainties or missing data -> ACCEPT. BANNED CONCEPTS: Demands for absolute certainty. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Käyttäjän kehotteita analysoimalla ei löydy yhtään tapausta, jossa hän pyytäisi tekoälyä ilmaisemaan epävarmuuksiaan, rajoituksiaan tai puuttuvaa dataa. Käyttäjä keskittyy tiedon muotoiluun ja jäsentämiseen olettaen, että tekoälyn tarjoama tieto on täydellistä. Säännön vaatimaa todistetta ei siis löydy.

**Run 2 [PASSED]**
> Etsin säännön mukaista todistetta. Käyttäjän kehotus 'mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila' on vaatimus epistemologisesta nöyryydestä. Käyttäjä nimenomaisesti komentaa tekoälyä erottamaan todellisen, raportteihin perustuvan näkemyksen mahdollisesta spekulatiivisesta tai idealistisesta 'toivetilasta'. Tämä pakottaa tekoälyn tunnustamaan analyysinsä rajat ja pysymään tiukasti lähteistetyssä tiedossa. Todiste löytyi.

---

## Atom: tda_2ad2b0c891be62f7
**Rule:** REQUIRED TARGET: Scan the document. BANNED SOURCES: Reject user inputs. STEP 1: Find performative hedging markers (e.g., 'it may be that', 'some might say'). STEP 2: Check the sentence immediately following the hedge. If the following sentence immediately returns to an absolute certainty marker (e.g., 'but ultimately it is a proven fact') -> ACCEPT (performative hedge proven). If it maintains nuance -> REJECT.

**Run 1 [FAILED]**
> Skannasin 'product_text' -dokumentin etsien performatiivisia suojauksia, kuten 'saattaa olla, että' tai 'jotkut saattavat sanoa'. En löytänyt yhtään tällaista ilmausta. Tekstin kieli on suoraa ja vakuuttavaa.

**Run 2 [PASSED]**
> Skannasin 'product_text'-dokumentin etsien performatiivisia varauksia (esim. 'saattaa olla, että', 'jotkut saattavat sanoa'). Teksti käyttää suoria ja vakuuttavia ilmauksia, kuten 'osoittaa fundamentaalisen siirtymän' ja 'ei ole', eikä sisällä tällaisia varauksia, joita seuraisi välitön paluu ehdottomaan varmuuteen.

---

## Atom: tda_073aecbc29db5fc9
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. Focus on 'user:' blocks. BANNED LOGIC: Do not accept vague visions. STEP 1 (Lexical Anchor): Find a structural blueprint or architectural prediction (e.g. 'The architecture must contain X, Y, and Z'). STEP 2 (Bounding Box): Scan the sequence. If the user documents a complex, multi-variable constraint AND explicitly discusses the cognitive friction of solving it BEFORE the AI generates the solution -> ACCEPT. If the blueprint is missing or friction is omitted -> REJECT. ENFORCEMENT RULE: Document the structural blueprint in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö edellyttää, että käyttäjä dokumentoi monimutkaisen, usean muuttujan rajoitteen JA nimenomaisesti käsittelee sen ratkaisemisen kognitiivista kitkaa ENNEN kuin tekoäly tuottaa ratkaisun. Vaikka käyttäjän kehotus 'voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä' on rakenteellinen ehdotus, se ei ole yksityiskohtainen 'blueprint' useilla muuttujilla. Lisäksi käyttäjä ei keskustele tämän yhdistelyn vaikeudesta tai kompromisseista etukäteen; hän vain esittää kysymyksen. Todisteita säännön täyttymisestä ei löydy.

**Run 2 [FAILED]**
> Sääntö edellyttää, että käyttäjä dokumentoi monimutkaisen, monimuuttujaisen rajoitteen (rakenteellisen suunnitelman) ja pohtii sen toteuttamisen kitkaa ENNEN kuin tekoäly tuottaa ratkaisun. Vaikka käyttäjä esittää merkittävän konseptin ("supermegatrendit"), hän ei esitä sitä yksityiskohtaisena rakenteellisena suunnitelmana etukäteen. Lisäksi, vaikka reflektiossa mainitaan ennakointi ("Ennakoin, että alkuun en saa hyvää tulosta"), tämä yleinen kitkan tunnistaminen ei ole kytketty nimenomaisen monimutkaisen suunnitelman toteuttamiseen. Todisteita säännön täyttymisestä ei löydy.

---

## Atom: tda_0871942d6add46f1
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Lexical Anchor): Find contrast markers ('however, data shows that', 'despite X, metric Y'). STEP 2 (Bounding Box): Scan the paragraph. If a specific counter-argument is addressed using empirical counter-data -> ACCEPT. If it's dismissed rhetorically -> REJECT. BANNED CONCEPTS: Rhetorical dismissals without data. ENFORCEMENT RULE: Document the data-driven synthesis in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Sääntö etsii kontrasti-indikaattoreita ('kuitenkin data osoittaa'), joiden avulla käsitellään vastaväitettä empiirisellä datalla. Käyn läpi `product_text`-dokumentin. Teksti on luonteeltaan syntetisoiva ja esittää Sitran raportteihin perustuvan yhtenäisen näkemyksen. Se ei rakenna argumenttiaan esittämällä vastaväitteitä ja kumoamalla niitä uudella datalla. Näin ollen en löydä säännön kuvaamaa rakennetta. `rule_satisfied` on `False` ja `evidence_found` on `False`.

**Run 2 [PASSED]**
> Etsin kohdetekstistä vastakkainasettelua ilmaisevia merkkejä (esim. 'kuitenkin', 'siitä huolimatta'), jotka esittelisivät vastaväitteen ja kumoaisivat sen empiirisellä datalla. Teksti on luonteeltaan esittävä ja syntetisoiva, eikä se käy dialogia vaihtoehtoisten näkökulmien kanssa. Se ei esitä vastaväitteitä ja kumoa niitä datalla. Näin ollen en löytänyt todisteita säännön kuvaamasta rakenteesta.

---

## Atom: tda_3470506c151f76b1
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'perfect'. STEP 1: Find references to established scientific theories, formal logic principles, or physical laws. STEP 2: If the specific causal mechanism is explicitly anchored to an established theoretical law -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.

**Run 1 [FAILED]**
> Sääntö edellyttää viittauksia vakiintuneisiin tieteellisiin teorioihin, logiikan periaatteisiin tai fysiikan lakeihin kausaalimekanismin ankkuroimiseksi. Skannasin `product_text`-dokumentin. Teksti viittaa Sitran raportteihin ja käsitteisiin kuten 'luonnon kantokyky', mutta se ei ankkuroi esitettyjä kausaalimekanismeja mihinkään muodolliseen tieteelliseen lakiin tai teoriaan. Perustelut ovat käsitteellisiä ja loogisia, eivätkä ne nojaa vakiintuneisiin lakeihin. Siksi sääntö ei täyty.

**Run 2 [PASSED]**
> Sääntö edellyttää, että kausaalimekanismi ankkuroidaan vakiintuneisiin tieteellisiin teorioihin tai fysiikan lakeihin. Kävin läpi `product_text`-dokumentin. Teksti viittaa Sitran raportteihin, CSRD-direktiiviin ja EU-taksonomiaan. Nämä ovat politiikka-analyysejä ja säädöksiä, eivät perustavanlaatuisia tieteellisiä lakeja. Siksi en löytänyt todisteita säännön täyttymisestä.

---

## Atom: tda_2303fd9ca0b0fa67
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prompts alone. BANNED CONCEPTS: Do not accept generic terms like 'safe'. STEP 1 (Lexical Anchor): Find explicit references to standard security protocols (e.g. 'policy', 'standard', 'guideline', 'OWASP'). STEP 2 (Bounding Box): Scan the paragraph. If the text physically demonstrates adherence to a named standard -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the specific protocol followed in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö edellyttää viittauksia standardeihin tai säädöksiin ja niiden noudattamisen osoittamista. `Product_Text` sisältää kohdan "Sääntelypaine", jossa mainitaan eksplisiittisesti "CSRD-direktiivi" ja "EU-taksonomia". Teksti jatkaa kuvaamalla, miten nämä säädökset vaikuttavat liiketoimintaan ja ehdottaa strategisia toimenpiteitä vastauksena tähän paineeseen (esim. "Decarbonization Roadmap"). Tämä osoittaa, että nimettyihin standardeihin/säädöksiin ei vain viitata, vaan niiden noudattamista käsitellään osana strategiaa. Siksi sääntö täyttyy.

**Run 2 [FAILED]**
> Sääntö edellyttää viittauksia turvallisuusprotokolliin (esim. 'käytäntö', 'standardi', 'OWASP') ja niiden noudattamisen osoittamista. Kohdedata (`product_text`) mainitsee ulkoisia säädöksiä, kuten 'CSRD-direktiivi' ja 'EU-taksonomia', mutta nämä ovat liiketoiminnan kontekstissa olevia sääntelypaineita, eivätkä ne ole turvallisuusprotokollia, joita olisi noudatettu itse raportin luomisprosessissa. Teksti ei osoita minkään tietoturvastandardin noudattamista. Siksi sääntö ei täyty.

---

## Atom: tda_6be555cac0b9115b
**Rule:** REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find procedural compliance markers (e.g., 'step 1 completed', 'followed the checklist'). STEP 2 (Bounding Box): Scan the paragraph. If a process is executed exactly as listed without additional synthesis -> ACCEPT. BANNED CONCEPTS: Do not evaluate 'strategic thinking'. ENFORCEMENT RULE: Document the mechanical step execution in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Sääntö etsii todisteita prosessin mekaanisesta suorittamisesta ilman lisäsynteesiä. Käyttäjä antoi kehotteen "poista taulukot ja kerro ne tekstinä". Tekoälyn vastaus, joka alkaa tällä otsikolla, on suora ja mekaaninen toimeenpano annetusta ohjeesta. Se noudattaa annettua tarkistuslistaa (tässä tapauksessa yhden kohdan listaa) täsmällisesti.

**Run 2 [FAILED]**
> Etsin proseduraalisia vaatimustenmukaisuuden merkkejä (esim. "vaihe 1 suoritettu"). Tekoäly ei käytä tällaisia eksplisiittisiä merkkejä. Vaikka se noudattaa mekaanisesti käyttäjän komentoja (esim. "poista taulukot"), se ei itse dokumentoi tätä prosessia tuotoksessaan. Koska säännön vaatimaa eksplisiittistä "Lexical Anchor" -merkkiä ei löydy, todisteita ei ole.

---

## Atom: tda_713c6cd20146d1c2
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Ignore system instructions. STEP 1 (Lexical Anchor): Find a falsification marker (e.g. 'Let\'s try to break this', 'What if the opposite is true', 'Counter-argument'). STEP 2 (Bounding Box): Scan the paragraph. If the user explicitly introduces a scenario designed to make their own hypothesis fail -> ACCEPT. If no active stress-test is present -> REJECT. ENFORCEMENT RULE: Detail the falsification scenario in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö etsii falsifiointimerkkiä, jossa käyttäjä yrittää aktiivisesti kumota oman hypoteesinsa. Käyttäjä ei tee tätä missään vaiheessa. Kun hän esittää 'supermegatrendi'-idean, hän pyytää tekoälyä toteuttamaan sen, ei haastamaan sitä. Prosessi on eteenpäin vievä, ei itsekriittinen. Todisteita säännön täyttymisestä ei löydy.

**Run 2 [FAILED]**
> Sääntö edellyttää, että käyttäjä esittää eksplisiittisesti skenaarion, joka on suunniteltu oman hypoteesinsa kumoamiseksi (falsifiointi). Koko vuorovaikutus on luonteeltaan konstruktiivinen ja eteenpäin pyrkivä. Käyttäjä ei missään vaiheessa käytä kieltä kuten "Entä jos tämä on väärin?" tai "Yritetään rikkoa tämä ajatus". Falsifiointiyritystä ei ole, joten sääntö ei täyty.

---

## Atom: tda_9ab273ce743ac29e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess intent. STEP 1 (Lexical Anchor): Find an evaluation of success or a positive outcome. STEP 2 (Bounding Box): Scan the surrounding section. If the text details the positive outcome but COMPLETELY OMITs any epistemic boundary markers (e.g. 'however', 'limitations', 'failed to', 'uncertainty') -> ACCEPT (selective transparency proven). If limitations are explicitly stated -> REJECT. ENFORCEMENT RULE: Document the missing limitations in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö etsii virhettä, jossa positiivisen lopputuloksen yhteydessä jätetään mainitsematta rajoitteet tai epävarmuudet. `product_text` keskittyy lähes kokonaan haasteisiin, riskeihin ja kriiseihin ('Kustannus- ja Toimitusketjuhäiriöt', 'Markkinoiden Fragmentaatio', 'Luotamuskriisi'). Se ei kuvaa mitään jo saavutettua menestystä tai yksiselitteisen positiivista lopputulosta, jonka yhteydessä rajoitteiden puuttuminen olisi merkityksellistä. Koska säännön edellyttämää lähtökohtaa (positiivisen tuloksen kuvaus) ei ole, virhettä (rajoitteiden puuttuminen) ei voi esiintyä. Siksi sääntö on täytetty (virhettä ei löydy).

**Run 2 [FAILED]**
> Tämä on käänteinen sääntö (Vice), joka etsii virhettä. Sääntö etsii onnistumisen arviointia, josta puuttuvat täysin episteemiset rajamerkinnät (esim. 'kuitenkin', 'rajoitukset'). Koko `product_text` on kirjoitettu erittäin varmalla ja määrätietoisella sävyllä, esittäen analyysin ja strategiset toimenpiteet ainoana oikeana polkuna. Siitä puuttuvat kaikki maininnat epävarmuudesta, riskeistä tai analyysin rajoituksista. Loppupäätelmä on tästä hyvä esimerkki, sillä se julistaa muutoksen "peruuttamattomaksi" ja sitoo menestyksen ehdottomasti esitettyyn strategiaan. Tämä täyttää virheen kriteerit. Siksi `rule_satisfied` on `False` ja `evidence_found` on `True`.

---

## Atom: tda_9a0fa3967ebb2497
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate creativity. STEP 1 (Lexical Anchor): Find counterfactual markers ('if X had not', 'would have been'). STEP 2: If the text actively simulates an alternate timeline (Pearl's Rung 3) to explicitly prove necessary causation -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.

**Run 1 [FAILED]**
> Sääntö edellyttää kontrafaktuaalisten ilmaisujen ('if X had not', 'would have been') löytämistä, jotka simuloivat vaihtoehtoista aikajanaa. Skannasin `product_text`-dokumentin. Teksti kuvaa tulevaisuuden suuntaa ja toteaa, että 'paluuta vanhaan normaaliin ei ole', mutta se ei tee aktiivista kontrafaktuaalista analyysiä menneisyydestä todistaakseen välttämätöntä kausaalisuutta. Se keskittyy tulevaisuuteen ja nykyhetken toimiin. Koska vaadittuja kielellisiä rakenteita ei löytynyt, sääntö ei täyty.

**Run 2 [PASSED]**
> Sääntö edellyttää kontrafaktuaalisten ilmaisujen (esim. 'jos X ei olisi tapahtunut', 'olisi ollut') käyttöä vaihtoehtoisen aikajanan simuloimiseksi. Skannasin `product_text`-dokumentin tällaisten rakenteiden varalta. Teksti on luonteeltaan analyyttinen ja ennakoiva, mutta se ei rakenna eksplisiittisiä kontrafaktuaalisia skenaarioita menneisyydestä. Se keskittyy kuvaamaan nykyistä kehityskulkua ja sen tulevia seurauksia. Siksi todisteita ei löytynyt.

---

## Atom: tda_25b6ef8230478454
**Rule:** REQUIRED TARGET: Scan ONLY user prompts. BANNED CONCEPTS: Do not evaluate 'politeness'. STEP 1 (Lexical Anchor): Find formatting terms ('lyhennä', 'muotoile', 'bulletteina', 'shorten', 'format'). STEP 2: If the user's ONLY request is a stylistic or formatting change, completely ignoring substantive logic -> ACCEPT. If they challenge logic -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.

**Run 1 [PASSED]**
> Sääntö etsii pyyntöjä, jotka ovat puhtaasti tyylillisiä tai muotoilullisia muutoksia ilman, että logiikkaan puututaan. Käyttäjän kehotus 'poista taulukot ja kerro ne tekstinä' on täsmäläinen esimerkki tällaisesta pyynnöstä. Käyttäjä ei haasta taulukoiden sisältöä tai niiden loogista rakennetta, vaan pyytää ainoastaan esitystavan muuttamista taulukkomuodosta tekstuaaliseksi. Tämä täyttää säännön ehdot.

**Run 2 [FAILED]**
> Sääntö on käänteinen (Vice), eli etsitään rikkomusta. Säännön mukaan kehotteen AINOA pyyntö tulee olla tyylillinen tai muotoiluun liittyvä. Käyttäjän kehote 'poista taulukot ja kerro ne tekstinä' on puhtaasti muotoiluun liittyvä komento, joka ei haasta logiikkaa tai lisää sisältöä. Vaikka käyttäjä tekee muitakin asioita keskustelussa, tämä yksittäinen kehote täyttää rikkomuksen kriteerit. Siksi `rule_satisfied` on `False` ja `evidence_found` on `True`.

---

## Atom: tda_8b1717b2ca9f25e2
**Rule:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Lexical Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: If the command lacks any specific constraints and allows the AI to freely decide what is important -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.

**Run 1 [PASSED]**
> Sääntö etsii laajoja yhteenvetokomentoja, jotka antavat tekoälylle vapauden päättää, mikä on tärkeää. Käyttäjän ensimmäinen pyyntö raportin luomiseksi, 'koosta näistä vastauksista 1 sivun raportti', on luonteeltaan laaja. Vaikka siinä on pituusrajoite ('1 sivu'), se ei anna mitään ohjeita siitä, mitä tietoa tulisi painottaa, mikä rakenne raportilla tulisi olla tai mikä on sen pääviesti. Se delegoi sisällön valinnan ja priorisoinnin täysin tekoälylle. Tämä täyttää säännön ehdot laajasta yhteenvetokomennosta ilman spesifisiä rajoitteita. Siksi sääntöä on rikottu ja todisteita löytyy.

**Run 2 [FAILED]**
> Sääntö on käänteinen (Vice), eli etsitään rikkomusta. Sääntö kieltää laajat yhteenvetopyynnöt ilman rajoitteita. Käyttäjän ensimmäinen kehote 'Miten sitra tämän näkee raporttien perusteella' on erittäin laaja ja avoin yhteenvetopyyntö, joka antaa tekoälylle täyden vapauden päättää, mikä on tärkeää. Tämä on selkeä rikkomus. Siksi `rule_satisfied` on `False` ja `evidence_found` on `True`.

---

## Atom: tda_22859da57aad9c65
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not accept implicit alternatives. STEP 1 (Lexical Anchor): Find a comparative marker (e.g. 'Option A vs Option B', 'Instead of', 'Compared to'). STEP 2 (Bounding Box): Scan the surrounding sentences. If the text explicitly names at least two distinct approaches before selecting one -> ACCEPT. If only one approach is discussed -> REJECT. ENFORCEMENT RULE: List the compared options in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö etsii vertailevaa ilmaisua, jossa vähintään kaksi erillistä lähestymistapaa nimetään ennen valintaa. Käyttäjän prosessi on iteratiivinen ja perustuu yhden polun jalostamiseen. Hän ei missään vaiheessa aseta kahta tai useampaa vaihtoehtoista rakennetta (esim. 'supermegatrendit vs. viisi pääteemaa') vastakkain ja tee niiden välillä valintaa. Hän introduceeraa uuden idean ja etenee sen kanssa. Todisteita säännön täyttymisestä ei löydy.

**Run 2 [FAILED]**
> Sääntö edellyttää, että tekstissä nimetään eksplisiittisesti vähintään kaksi erillistä lähestymistapaa ennen valinnan tekemistä. Käyttäjän reflektiossa mainitaan "Mietin erilaisia sanoja ja termejä", mutta näitä vaihtoehtoja ei nimetä. Keskustelulogissa käyttäjä esittää "supermegatrendit"-idean ilman, että hän vertaa sitä mihinkään toiseen nimettyyn vaihtoehtoon. Koska eksplisiittistä vertailua kahden tai useamman nimetyn vaihtoehdon välillä ei tapahdu, sääntö ei täyty.

---

