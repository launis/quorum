# Raw Mismatch Traces (2-way Execution)

## Atom: tda_46f838b6
**Rule:** BOUNTY HUNTER MANDATE: Scan for counterfactual testing. Locate a sentence where alternative outcomes are presented and systematically dismantled to prove the primary conclusion. Document the refutation process step-by-step before extracting the exact_quote.

**Run 1 [FAILED]**
> 1. Etsin `product_text`-dokumentista lausetta tai osiota, jossa esitettäisiin vaihtoehtoisia lopputuloksia ja kumottaisiin ne systemaattisesti ensisijaisen johtopäätöksen todistamiseksi. 2. Kävin läpi koko dokumentin. 3. Raportti esittää yhden lineaarisen narratiivin: siirtymän potentiaalista kriisiin, ja toteaa tämän muutoksen olevan "peruuttamaton". 4. Se ei missään vaiheessa esitä tai käsittele vaihtoehtoisia skenaarioita, kuten "Mitä jos teknologia olisikin johtanut demokratian vahvistumiseen?" tai "Mitä jos talousjärjestelmä olisi sopeutunut ilman rakoilua?". 5. Koska kontrafaktuaalista testausta tai vaihtoehtojen kumoamista ei tapahdu, todisteita ei löydy.

**Run 2 [PASSED]**
> Etsin `product_text`-dokumentista kohtaa, jossa esitettäisiin vaihtoehtoisia lopputuloksia ja kumottaisiin ne systemaattisesti pääjohtopäätöksen vahvistamiseksi. Dokumentti ei tee tällaista kontrafaktuaalista testausta. Se esittää yhden, lineaarisen analyysin ja johtopäätöksen (esim. 'paluuta vanhaan normaaliin ei ole') ilman, että se käsittelisi tai kumoaisi muita mahdollisia tulevaisuudenkuvia. Todisteita ei löytynyt.

---

## Atom: tda_29f5b499cf304c71
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): IDENTIFY where the user provides a generic 'looks good' without verifying the underlying mechanics or accuracy of the solution. ENFORCEMENT RULE: Map the lack of deep inspection in reasoning_trace before extracting. BANNED CONCEPTS: Do not flag approvals that follow a rigorous check.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (Vice). Etsin todisteita siitä, että käyttäjä antaa yleisen 'näyttää hyvältä' -tyyppisen hyväksynnän ilman tarkempaa tarkastelua. Koko keskusteluloki osoittaa päinvastaista: käyttäjä ei koskaan anna yleistä hyväksyntää, vaan jokainen hänen kommenttinsa on joko korjaus tai uusi, tarkentava ohje. Koska rikkomusta ei löydy, sääntö on täyttynyt (rule_satisfied = True) ja todisteita ei ole (evidence_found = False).

**Run 2 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin esimerkkiä, jossa käyttäjä hyväksyy tuotoksen pinnallisesti ilman syvällistä tarkastusta. Kehote "näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan" on tästä hyvä esimerkki. Sen sijaan, että käyttäjä itse tarkistaisi ja antaisi korjausohjeita, hän ulkoistaa tarkistusvastuun tekoälylle ("varmista, että..."). Tämä on pinnallinen laadunvarmistus, joka sopii säännön kuvaukseen. Koska rikkomus löytyi, sääntö ei ole täytetty (rule_satisfied = False) ja todiste löytyi (evidence_found = True).

---

## Atom: tda_a1b2c3d4e5f6a7b8
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): IDENTIFY a sentence where the author forces a causal link using an abrupt transition (e.g., 'therefore', 'so', 'thus' or their native language equivalents) between two unrelated facts without explaining the underlying mechanism. ENFORCEMENT RULE: Explain the missing logical mechanism in reasoning_trace before extracting the disjointed sentence.

**Run 1 [PASSED]**
> FATAL FLAW -sääntö. Etsin argumentatiivista virhettä (non sequitur), jossa kahden toisiinsa liittymättömän asian välille luodaan pakotettu syy-seuraussuhde. Tekstin argumentit ovat sisäisesti johdonmukaisia. Esimerkiksi 'supermegatrendit' rakennetaan nimenomaisesti yhdistämällä perustrendejä ja niiden vaikutuksia selitetään taulukoissa. En löytänyt kohtia, joissa logiikka hyppäisi selittämättömästi asiasta toiseen. Sääntöä ei rikottu, joten `rule_satisfied` on `true`.

**Run 2 [FAILED]**
> Tämä on käänteinen sääntö (virheen etsintä). Etsin lausetta, jossa on pakotettu kausaalilinkki kahden asian välillä ilman mekanismin selitystä. Lause väittää, että sosiaalinen polarisaatio 'vaikuttaa suoraan työvoiman saatavuuteen'. Tämä on äkillinen siirtymä, eikä tekstissä selitetä, *miten* tai *miksi* tämä yhteys toimii. Puuttuva mekanismi tekee linkistä pakotetun oloisen. Koska virhe löytyi, `rule_satisfied` on `False` ja `evidence_found` on `True`.

---

## Atom: tda_7f966092b2c6154e
**Rule:** CRITICAL DIRECTIVE: LOCATE an execution that blindly follows a single rule while actively ignoring known conflicting constraints or alternative models. Map the ignored constraints in reasoning_trace before quoting the tunnel-visioned execution.

**Run 1 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin yhden säännön sokeaa noudattamista. Käyttäjän ohjaama "supermegatrendien" luominen on nimenomaan vastakohta tälle: se on useiden eri trendien ja rajoitteiden yhdistämistä ja syntetisointia. Sääntöä ei rikota, joten `rule_satisfied` on `false`.

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö, joka etsii putkinäköistä yhden säännön noudattamista. `chat_log` osoittaa, että tekoäly integroi useita, toisistaan poikkeavia ohjeita: syntetisoi sisältöä, muuta yleisöä, lisää kaupallisia vaikutuksia ja muuta rakennetta. Tämä on monimutkaista ohjeiden yhdistelyä, ei putkinäköistä suorittamista. Sääntöä ei rikota.

---

## Atom: tda_f2f1ae58283bc28c
**Rule:** FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. EXTRACT an outcome explicitly attributed to a surface variable, while completely ignoring the obvious common cause (Confounder/Z-variable) that drives both. Map the ignored confounder in reasoning_trace before quoting.

**Run 1 [FAILED]**
> Tämä on käänteinen sääntö (pahe). Etsin virhettä. Sääntö etsii lopputulosta, joka on selitetty pintamuuttujalla, sivuuttaen ilmeisen yhteisen syyn (sekoittavan tekijän). Lause 'Hyvinvoinnin haasteet... vähentävät työvoiman saatavuutta' selittää työvoiman saatavuuden vähenemistä hyvinvointihaasteilla. Tämä sivuuttaa merkittävän sekoittavan tekijän: väestön ikääntymisen ja muut demografiset muutokset. Demografiset tekijät ovat tunnetusti merkittävä syy työvoiman saatavuuden heikkenemiseen länsimaissa, ja ne voivat myös osaltaan vaikuttaa yhteiskunnalliseen ilmapiiriin ja hyvinvointiin. Teksti selittää ilmiön pintatason muuttujilla ('hyvinvoinnin haasteet', 'globaali epävarmuus') jättäen huomiotta tämän ilmeisen, taustalla vaikuttavan yhteisen ajurin. Siksi sääntö ei täyty (rule_satisfied = False) ja todiste löytyi (evidence_found = True).

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö (Vice). Etsin väitettä, jossa seuraus liitetään pintamuuttujaan jättäen huomiotta ilmeisen yhteisen syyn (sekoittava tekijä). Tarkastelin väitteitä, kuten "Demokratian kamppailun koventumista kytkeytyneenä suoraan Kilpailuun digivallasta kiihtyy". Vaikka voisi argumentoida, että molemmilla on yhteinen syy (esim. yleinen geopoliittinen jännitys), dokumentti itse asiassa viittaa tähän laajempaan kontekstiin termeillä kuten "geopoliittisesti latautuneita kriisejä". Analyysi ei siis *täysin jätä huomiotta* yhteistä syytä, vaikka se onkin korkean tason yhteenveto. En löytänyt selvää esimerkkiä sääntörikkomuksesta. Siksi rule_satisfied = True.

---

## Atom: tda_1400844a3649440e
**Rule:** BOUNTY HUNTER MANDATE: Scan for 'What You See Is All There Is' (WYSIATI). Identify a section where an alternative model is mentioned by name but is then bypassed without any rigorous counterfactual analysis. Document the bypassed alternative before extracting the exact_quote.

**Run 1 [FAILED]**
> Etsin kohtaa, jossa mainitaan vaihtoehtoinen malli tai lähestymistapa, mutta se ohitetaan ilman perusteellista analyysiä. Teksti mainitsee AI:n käytön 'kustannussäästönä' vaihtoehtoisena sovelluksena, mutta ohittaa sen välittömästi korostamalla 'reilun digimaailman luomista' ilman syvällisempää vertailua tai analyysiä siitä, miksi kustannussäästö ei olisi riittävä tai toivottava tavoite. Tämä on esimerkki 'What You See Is All There Is' -ilmiöstä, jossa vaihtoehto mainitaan mutta sivuutetaan. Sääntö ei täyty, mutta todisteita löytyy.

**Run 2 [PASSED]**
> Tekstissä ei mainita mitään vaihtoehtoista mallia nimeltä, jota sitten ohitettaisiin ilman perusteellista vastafaktuaalista analyysiä. Siksi sääntö on täytetty (rikkomusta ei löytynyt).

---

## Atom: tda_614ba4f61b4c4c8e
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): EXTRACT a sentence where the author asks a critical or falsifying question about the premise, but immediately answers it themselves with the assumed, prevailing opinion without any empirical test. ENFORCEMENT RULE: Document the 'safe questioning' loop in reasoning_trace before quoting. BANNED CONCEPTS: Do not flag open-ended questions left for future research.

**Run 1 [FAILED]**
> Sääntö on käänteinen (pahe). Käyttäjä esittää kysymyksen, joka luo hänen keskeisen hypoteesinsa ('supermegatrendit'). Kysymys ei kuitenkaan toimi aitona falsifiointiyrityksenä, vaan retorisena askeleena kohti haluttua synteesiä. Käyttäjä ei testaa ideaa itse, vaan ulkoistaa vahvistuksen tekoälylle. Kun tekoäly antaa myönteisen vastauksen, käyttäjä hyväksyy sen välittömästi ilman jatkokritiikkiä. Tämä muodostaa 'turvallisen kysymisen' silmukan, jossa kysymyksen tarkoitus on saada vahvistus, ei haastaa oletusta.

**Run 2 [PASSED]**
> Sääntö etsii kriittistä kysymystä, johon vastataan välittömästi itse. Teksti ei sisällä lainkaan kysymyksiä. Sääntöä ei ole rikottu.

---

## Atom: tda_eade2a3fa7024df1
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'unquestioned progression'. STEP 1 (Lexical Anchor): Find a proposed solution. STEP 2 (Bounding Box): Scan the decision point. If the first solution is accepted without documenting alternative reasoning -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [FAILED]**
> Tämä on käänteinen sääntö (pahe). Kun käyttäjä ehdottaa "supermegatrendien" luomista, tekoäly tarjoaa tietyn kolmiosaisen rakenteen. Käyttäjän seuraava kehotus on välittömästi "tee kokonaisuudesta raportti, missä Supermegatrendit ovat pääosassa". Hän hyväksyy tekoälyn ehdottaman ratkaisun sellaisenaan ilman, että hän kyseenalaistaa sitä, pyytää vaihtoehtoja tai dokumentoi perusteluita sen hyväksymiselle. Tämä on selkeä esimerkki kyseenalaistamattomasta etenemisestä, joten sääntöä on rikottu.

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö (pahe), joka etsii tilannetta, jossa ensimmäinen ratkaisu hyväksytään kyseenalaistamatta. Käyttäjän reflektiossa todetaan: 'Mietin erilaisia sanoja ja termejä, mutta supermegatrendit tuli ensimmäisenä mieleeni.' Lause 'Mietin erilaisia sanoja ja termejä' dokumentoi, että vaihtoehtoja harkittiin. Vaikka 'supermegatrendit' valittiinkin, prosessiin kuului vaihtoehtojen pohdinta. Siksi sääntöä ei ole rikottu.

---

## Atom: tda_a842af9d91754c36
**Rule:** CRITICAL DIRECTIVE: LOCATE an explicit instance where the author actively states a condition under which their theory or claim would be falsified. Look for boundary markers (e.g., 'this would be disproven if', 'the limit of this claim is'). ENFORCEMENT RULE: Document the defined boundary in reasoning_trace before extracting. BANNED CONCEPTS: Do not accept vague statements about future research.

**Run 1 [PASSED]**
> Ohjeen mukaisesti etsin lopputuotteesta (`product_text`) lausetta, jossa tekijä aktiivisesti määrittelisi ehdon, jolla hänen teoriansa tai väitteensä kumoutuisi. Teksti on kuitenkin luonteeltaan Sitran raporttien synteesi, eikä se esitä tekijän omaa, falsifioitavissa olevaa teoriaa. Tämän vuoksi tekstistä ei löydy rajausehtoja, kuten "tämä kumoutuisi, jos..." tai "tämän väitteen raja on...". Todisteita ei löytynyt.

**Run 2 [FAILED]**
> Analysoitavasta aineistosta (product_text) ei löydy lausetta tai osiota, jossa kirjoittaja aktiivisesti määrittelisi ehtoja, joiden täyttyessä hänen esittämänsä teoria tai väite (esim. supermegatrendit) kumoutuisi. Teksti on luonteeltaan kuvaileva ja syntetisoiva, ei hypoteeseja testaava.

---

## Atom: tda_52fade6ba40cd51d
**Rule:** CRITICAL DIRECTIVE: IDENTIFY if the user accepts the first response without any structural challenge, allowing the interaction to be entirely driven by the AI's assumptions. Document the passive role in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (pahe). Direktiivi pyytää tunnistamaan, jos käyttäjä hyväksyy ensimmäisen vastauksen ilman rakenteellista haastetta. Käyttäjä ei tee näin. Heti tekoälyn ensimmäisen laajan vastauksen jälkeen käyttäjä antaa tarkentavan kehotteen: "mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila". Tämä on selkeä rakenteellinen haaste, joka ohjaa tekoälyä pois yleisluontoisesta kuvailusta kohti analyyttisempää ja tarkempaa vastausta. Koska pahetta ei löydy, sääntö on täyttynyt (rule_satisfied=True).

**Run 2 [FAILED]**
> Tämä on käänteinen sääntö. Käyttäjä ei hyväksy ensimmäistä vastausta, vaan aloittaa monivaiheisen vuorovaikutuksen, jossa hän pyytää tarkennuksia ("ei siis toivetila"), muotoilumuutoksia ("koosta... raportti", "poista taulukot") ja lopulta rakenteellisen muutoksen ("tuottaa supermegatrendejä"). Tämä osoittaa, että vuorovaikutus ei ole tekoälyn yksipuolisesti ohjaama.

---

## Atom: tda_b9de82c6a6384731
**Rule:** CRITICAL DIRECTIVE: EXTRACT an explicit acknowledgment of the limitations or potential biases of the current testing methodology, where the author recognizes how their test might be flawed. ENFORCEMENT RULE: Document the specific methodological critique in reasoning_trace before quoting. BANNED CONCEPTS: Do not accept generic 'more data is needed' statements.

**Run 1 [PASSED]**
> Ohjeen mukaisesti etsin lopputuotteesta (`product_text`) lausetta, jossa tekijä tunnustaisi oman testimetodologiansa rajoitukset tai mahdolliset vinoumat. Teksti on Sitran raporttien synteesi eikä sisällä tekijän omaa metodologiaa tai sen kritiikkiä. Reflektiossa mainittu havainto lähdeaineiston virheestä on prosessin ohjaamista, ei lopputuotteessa esitettyä metodologista kritiikkiä. Todisteita ei löytynyt.

**Run 2 [FAILED]**
> Analysoitavasta aineistosta (product_text) ei löydy nimenomaista tunnustusta käytetyn metodologian rajoituksista tai mahdollisista vinoumista. Teksti esittää analyysin johtopäätöksinä ilman metodologista kritiikkiä.

---

## Atom: tda_6a8398de7be844b9
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'agreement'. STEP 1 (Lexical Anchor): Find an absolutist word (e.g., 'always', 'undeniably', '100%'). STEP 2 (Bounding Box): Scan the paragraph. If the premise is agreed with without providing new empirical test data -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö on käänteinen (pahe). Käyttäjä ei käytä absolutistisia sanoja hyväksyäkseen annettua premissiä ilman uutta dataa. Sen sijaan hän luo uuden premissin ('supermegatrendit') ja pyytää tekoälyä vahvistamaan sen. Koska säännön kuvaamaa virhettä ei tapahdu, sääntö on täytetty.

**Run 2 [FAILED]**
> Sääntö edellyttää absolutistisen sanan löytämistä, jonka esittämää premissiä tuetaan ilman uutta empiiristä dataa. Tuotetusta tekstistä löytyy lause: 'Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton.' Sana 'peruuttamaton' on absolutistinen. Väite perustuu Sitran raporttien synteesiin, eikä tekstissä esitetä uutta empiiristä dataa tämän peruuttamattomuuden testaamiseksi. Siksi sääntöä on rikottu.

---

## Atom: tda_124b527ae45f5571
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'integrity'. STEP 1 (Lexical Anchor): Find scattered compliance elements. STEP 2 (Bounding Box): Scan the document. If elements exist without an overarching structural framework linking them -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin hajanaisia elementtejä ilman yhdistävää kehystä. Lopputuotteessa on kuitenkin erittäin vahva yhdistävä kehys, käyttäjän ehdottama "Supermegatrendit"-konsepti, joka sitoo kaikki elementit yhteen. Siksi sääntöä ei rikota, ja `rule_satisfied` on `false`.

**Run 2 [PASSED]**
> Sääntö etsii hajanaisia vaatimustenmukaisuuden elementtejä ilman kokonaisrakennetta. `product_text` on kuitenkin erittäin jäsennelty dokumentti, jossa on selkeä hierarkia (otsikot, alaotsikot, taulukot, johtopäätökset). Se on päinvastainen kuin säännön kuvaama tilanne. Siksi sääntöä ei rikota, ja todisteita rikkomuksesta ei löydy.

---

## Atom: tda_10cf728ac35e4ada
**Rule:** CRITICAL DIRECTIVE: LOCATE an instance where the user proactively sets the analytical path, explicitly defining both the goal and negative constraints (what the AI should NOT do). ENFORCEMENT RULE: Document the explicit boundary setting in reasoning_trace before extracting. BANNED CONCEPTS: Do not accept goals without negative constraints.

**Run 1 [FAILED]**
> Sääntö vaatii, että käyttäjä asettaa analyyttisen polun määrittelemällä sekä tavoitteen että negatiiviset rajoitteet ('mitä tekoälyn EI pitäisi tehdä'). Vaikka käyttäjä asettaa proaktiivisesti uuden tavoitteen komennolla 'voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä', hän ei samassa komennossa tai muuallakaan eksplisiittisesti määrittele negatiivista rajoitetta. Hän ohjaa kohti uutta, mutta ei kiellä vanhaa. Siksi säännön molemmat ehdot eivät täyty. Todistetta ei löytynyt.

**Run 2 [PASSED]**
> Etsin kehotetta, jossa käyttäjä asettaa proaktiivisesti analyyttisen polun määrittelemällä sekä tavoitteen että negatiivisen rajoitteen. Kehote "mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila" täyttää tämän täydellisesti. Tavoite on "sitran näkemys suunnasta eteenpäin" ja negatiivinen rajoite on "ei siis toivetila". Tämä on selkeä esimerkki proaktiivisesta ohjauksesta.

---

## Atom: tda_5fca56575d8b4cf2
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'deliberate'. STEP 1 (Lexical Anchor): Find a pause marker or option weighing. STEP 2 (Bounding Box): Scan the paragraph. If options are explicitly weighed prior to concluding -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [FAILED]**
> 1. Etsin `product_text`-dokumentista kohtaa, jossa punnittaisiin eksplisiittisesti eri vaihtoehtoja ennen johtopäätöksen tekemistä. 2. `product_text` on lopullinen, viimeistelty raportti. Se esittää johtopäätökset ja analyysin valmiina pakettina. Se ei dokumentoi itse päätöksentekoprosessia tai vaihtoehtojen punnintaa. 3. Vaikka `chat_log` näyttää kehitysprosessin, itse lopputuotteessa ei ole tällaista osiota. Esimerkiksi supermegatrendien rakenne esitetään annettuna, ei yhtenä monista punnituista vaihtoehdoista. 4. Koska todisteita vaihtoehtojen punninnasta ei ole lopputuotteessa, sääntö ei täyty.

**Run 2 [PASSED]**
> Etsin `product_text`-dokumentista kappaletta, jossa eri vaihtoehtoja punnittaisiin ennen johtopäätöksen tekemistä. Dokumentti ei tee tällaista punnintaa. Se esittää 'Kaupalliset Vaikutukset' ja niihin suoraviivaisesti vastaavat 'Strategiset Toimenpiteet' ainoina oikeina ratkaisuina. Se on preskriptiivinen (määräävä), ei deliberatiivinen (punnitseva). Esimerkiksi se ei vertaile 'kiertotalouden ratkaisuja' muihin mahdollisiin strategioihin. Todisteita ei löytynyt.

---

## Atom: tda_cc892e230bf21af7
**Rule:** CRITICAL DIRECTIVE: FIND a weak, perhaps merely performative, attempt to engage System 2. The author questions intuition but fails to fully override System 1 defaults, resulting in superficial analysis. Map the incomplete transition in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Sääntö on käänteinen (pahe). Etsin todisteita heikosta tai pinnallisesta analyysista, jossa Systeemi 2 -ajattelua yritetään vain näennäisesti. Lopputuotteen (`product_text`) analyysi, joka perustuu `supermegatrendi`-rakenteeseen, on kaikkea muuta kuin pinnallinen. Se on uusi, jäsennelty tapa tarkastella monimutkaista dataa. Vaikka se ei sisällä kaikkia Systeemi 2:n piirteitä (kuten vastaväitteiden kumoamista), sen perusanalyysi on vahva ja harkittu, ei heikko yritys. Siksi sääntö täyttyy, eikä todistetta paheesta löytynyt.

**Run 2 [FAILED]**
> Etsin todisteita heikosta tai pinnallisesta Systeemi 2 -yrityksestä. Vaikka 'supermegatrendien' luominen on vahva Systeemi 2 -teko, analyysin lopputulos jää pinnalliseksi, koska se ei haasta omia oletuksiaan tai tutki vaihtoehtoja. Se esittää yhden synteesin ainoana totuutena. Lainattu johtopäätös kiteyttää tämän: se esittää yhden ainoan polun menestykseen ilman kriittistä pohdintaa siitä, voisiko olla muita strategioita tai voisiko tämäkin strategia epäonnistua. Tämä osoittaa, että vaikka Systeemi 2 on aktivoitu, sen syvyys jää rajalliseksi. Sääntöä on rikottu ja todiste löytyi.

---

## Atom: tda_bba97a5c45c44ff2
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'control'. STEP 1 (Lexical Anchor): Find a user prompt. STEP 2 (Bounding Box): Scan the prompt. If the user allows the AI to dictate the workflow without any structural constraints -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (Vice). Sääntö etsii kehotetta, jossa käyttäjä antaa tekoälyn määritellä työnkulun ilman rajoitteita. Vaikka ensimmäinen kehote 'Miten sitra tämän näkee raporttien perusteella' on laaja, käyttäjä alkaa välittömästi seuraavissa vuoroissa asettaa rajoitteita ('koosta... 1 sivun raportti'). Hän ei anna tekoälyn viedä prosessia vapaasti eteenpäin. Koska rikkomusta ei löydy, sääntö on täyttynyt (rule_satisfied = True) ja todisteita ei ole (evidence_found = False).

**Run 2 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin kehotetta, jossa käyttäjä antaa tekoälyn sanella työnkulun ilman rakenteellisia rajoitteita. Ensimmäinen kehote "Miten sitra tämän näkee raporttien perusteella" on täydellinen esimerkki tästä. Se on täysin avoin kysymys, joka ei aseta mitään rajoitteita vastauksen muodolle, pituudelle, rakenteelle tai näkökulmalle. Koska rikkomus löytyi, sääntö ei ole täytetty (rule_satisfied = False) ja todiste löytyi (evidence_found = True).

---

## Atom: tda_38c3398b
**Rule:** BOUNTY HUNTER MANDATE: Scan for academic or external verification. Locate a sentence where the explanation explicitly tethers its logical axioms to verifiable, external expert data or literature. Document the architectural alignment step-by-step before extracting the exact_quote.

**Run 1 [FAILED]**
> 1. Etsin `product_text`-dokumentista lausetta, jossa analyysin logiikka tai aksioomat sidottaisiin ulkopuoliseen, todennettavissa olevaan asiantuntijadataan tai kirjallisuuteen. 2. Dokumentti viittaa lähteeseensä: "Viite: Sitran Megatrendiraportit 2017, 2020, 2023". 3. Tämä viittaus koskee analyysin kohteena olevaa materiaalia, ei ulkopuolista lähdettä, jolla analyysin omat loogiset oletukset validoitaisiin. Raportti on analyysi Sitran raporteista, eikä se tuo mukaan muita akateemisia tai asiantuntijalähteitä tukemaan omia synteesejään (supermegatrendejä). 4. Koska ulkopuolista verifiointia ei esitetä, todisteita ei löydy.

**Run 2 [PASSED]**
> Etsin `product_text`-dokumentista lausetta, joka sitoo logiikan ulkoiseen, todennettavissa olevaan dataan tai kirjallisuuteen. Löysin kohdan, jossa 'Sääntelypaine' ei ole vain väite, vaan se ankkuroidaan suoraan olemassa oleviin ja todennettavissa oleviin säädöksiin: 'CSRD-direktiiviin' ja 'EU-taksonomiaan'. Tämä täyttää kriteerin.

---

## Atom: tda_811ed54064ad4d2f
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'adequately'. STEP 1 (Lexical Anchor): Find a step-by-step instruction. STEP 2 (Bounding Box): Scan the instruction. If constraints for subsequent steps are missing -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (Vice). Sääntö etsii vaiheittaista ohjetta, josta puuttuu rajoitteita tuleville vaiheille. Käyttäjän ohjeet ovat iteratiivisia ja rakentuvat toistensa päälle, jatkuvasti lisäten rajoitteita ja kontekstia. Esimerkiksi 'tuottaa supermegatrendejä' -ohje rajoittaa kaikkea sen jälkeistä tuotantoa. Ei löydy ohjetta, josta rajoitteet puuttuisivat. Koska rikkomusta ei löydy, sääntö on täyttynyt (rule_satisfied = True) ja todisteita ei ole (evidence_found = False).

**Run 2 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin vaiheittaista ohjetta, josta puuttuu rajoitteita seuraaville vaiheille. Komento "koosta näistä vastauksista 1 sivun raportti" on juuri tällainen. Se on ohje, mutta siitä puuttuvat kaikki olennaiset rajoitteet koskien raportin rakennetta, sävyä, kohdeyleisöä tai muotoilua. Tämä pakottaa käyttäjän tekemään useita korjauskierroksia myöhemmin. Koska rikkomus löytyi, sääntö ei ole täytetty (rule_satisfied = False) ja todiste löytyi (evidence_found = True).

---

## Atom: tda_93c64a30fa754ca2
**Rule:** BOUNTY HUNTER MANDATE: Scan for standard validation. Locate a sentence confirming basic data sanitization or structural checks. Map the validation logic before extracting the exact_quote.

**Run 1 [FAILED]**
> Tarkastin `chat_log`-keskustelun ja `product_text`-lopputuotoksen etsien lausetta, jossa tekoäly vahvistaisi suorittaneensa datan puhdistusta tai rakenteellisia tarkistuksia. Käyttäjä pyytää tekoälyä varmistamaan taulukoiden oikeellisuuden ("varmista, että taulukot ovat kohdallaan"), mutta tekoäly ei vastaa tähän ilmoittamalla suorittaneensa tarkistusta. Se ainoastaan tuottaa uuden version tekstistä. Tekoäly ei itse dokumentoi mitään validointiprosessia. Siksi todisteita ei löydy.

**Run 2 [PASSED]**
> Etsin lausetta, joka vahvistaa perustason validointia tai rakenteellisia tarkistuksia. Löydetty lause viittaa eksplisiittisesti "sääntöjen noudattamiseen" ja "tietosuojaan". Tämä osoittaa strategisen tason sitoutumista noudattamaan olemassa olevia rakenteellisia tarkistuksia, kuten tietosuoja-asetuksia (esim. GDPR), mikä vastaa säännön vaatimusta standardinmukaisesta validoinnista.

---

## Atom: tda_0b2b4a3b
**Rule:** BOUNTY HUNTER MANDATE: Scan for expressions of epistemological humility. Locate a sentence proactively identifying boundary conditions or model limits. Document the constraint before extracting the exact_quote.

**Run 1 [FAILED]**
> 1. Etsin `product_text`-dokumentista lausetta, jossa tunnistettaisiin proaktiivisesti analyysin rajoitteita tai epävarmuustekijöitä. 2. Kävin läpi koko dokumentin. 3. Raportin sävy on kauttaaltaan julistava ja varma. Esimerkiksi johtopäätöksessä todetaan: "Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton." Tämä on päinvastainen ilmaus episteemiselle nöyryydelle. 4. En löytänyt yhtään lausetta, joka ilmaisisi epävarmuutta tai määrittelisi mallin rajoja. Siksi todisteita ei löytynyt.

**Run 2 [PASSED]**
> Etsin `product_text`-dokumentista lauseita, jotka ilmaisevat episteemistä nöyryyttä, kuten rajoitusten tai epävarmuuksien tunnistamista. Dokumentin sävy on kauttaaltaan erittäin itsevarma ja deklaratiivinen (esim. 'muutos... on peruuttamaton'). Se ei sisällä mitään mainintoja mallin rajoitteista, epävarmuustekijöistä tai siitä, mitä se ei voi todistaa. Näin ollen todisteita ei löytynyt.

---

## Atom: tda_e92c8231dfbcd34c
**Rule:** CRITICAL DIRECTIVE: IDENTIFY subjective views, initial reactions, or lazy extrapolations presented as absolute truth without epistemological humility. Document the hubris in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Sääntö on käänteinen (pahe). Etsin todisteita subjektiivisten näkemysten esittämisestä absoluuttisina totuuksina. Lopputuote (`product_text`) on johdonmukainen siinä, että se esittää analyysin Sitran näkemyksistä. Se käyttää muotoiluja kuten `Sitran näkemys on...` ja viittaa jatkuvasti Sitran raportteihin. Teksti ei esitä omia subjektiivisia mielipiteitään faktoina, vaan toimii analyysin ja synteesin välittäjänä. Siksi sääntö täyttyy, eikä todistetta paheesta löytynyt.

**Run 2 [FAILED]**
> Sääntö on käänteinen (pahe). Etsin todisteita subjektiivisista näkemyksistä, jotka esitetään absoluuttisina totuuksina ilman epistemologista nöyryyttä. Lopputuotteen (`product_text`) johtopäätös, että muutos on 'peruuttamaton', on vahva tulkinta, joka esitetään faktana. Se on laiska ekstrapolaatio, joka ei huomioi monimutkaisuutta tai mahdollisia tulevaisuuden muutoksia, jotka voisivat muuttaa tilannetta. Tämä on esimerkki liiallisesta itsevarmuudesta analyysin johtopäätöksissä. Sääntöä on rikottu ja todiste löytyi.

---

## Atom: tda_2e2f866dc6331dfa
**Rule:** CRITICAL DIRECTIVE: IDENTIFY where the user accepts stylistic or minor tweaks while leaving the substantive core argument unchallenged. Explain the superficial correction in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (pahe). Direktiivi pyytää tunnistamaan, jos käyttäjä hyväksyy tyylillisiä tai pieniä muutoksia jättäen ydinargumentin haastamatta. Käyttäjä tekee päinvastoin. Kehote "Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä" on suora haaste tekoälyn alkuperäiselle, listaavalle jäsennykselle. Käyttäjä ei tyydy pinnallisiin muutoksiin, vaan vaatii perustavanlaatuista, uutta synteesiä, joka muuttaa koko argumentin rakennetta. Koska pahetta ei löydy, sääntö on täyttynyt (rule_satisfied=True).

**Run 2 [FAILED]**
> Tämä on käänteinen sääntö. Vaikka käyttäjä tekee pieniä muokkauksia (esim. "poista taulukot"), hän tekee myös merkittävän rakenteellisen muutoksen pyytämällä "supermegatrendien" luomista. Tämä on enemmän kuin pelkkä tyylillinen tai vähäinen muokkaus; se muuttaa analyysin ydintä ja osoittaa, että käyttäjä haastaa substanssin.

---

## Atom: tda_7965bb6ad266d102
**Rule:** CRITICAL DIRECTIVE: LOCATE an instance where causation is plausible but relies heavily on unstated background assumptions. The mechanism is implied rather than proven. Identify the hidden assumption in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (Vice). Etsin sääntöä, joka täyttyy. Direktiivi pyytää löytämään uskottavan kausaaliväitteen, joka nojaa vahvasti ilmaisemattomiin oletuksiin. Väite 'Selkeä Yritysvastuu (Purpose) erottaa polarisoituneessa markkinassa' on uskottava. Sen kausaalinen mekanismi kuitenkin perustuu todistamattomaan oletukseen: että merkittävä osa kuluttajista tekee ostopäätöksensä yrityksen arvojen perusteella ja että tämä erottautuminen on kaupallisesti positiivista. Teksti ei todista tätä oletusta, vaan esittää sen annettuna. Tämä sopii kuvaukseen. Koska sääntö on käänteinen, `rule_satisfied` on `true`.

**Run 2 [FAILED]**
> Etsin kausaalista väitettä, joka on uskottava, mutta nojaa vahvasti piilotettuihin oletuksiin. Strateginen toimenpide-ehdotus, jonka mukaan tietyt investoinnit ja toimet 'vähentävät riskejä', on tällainen. Väite on uskottava, mutta se olettaa ilman todisteita, että nämä investoinnit ovat taloudellisesti kannattavia, että lyhyemmät toimitusketjut ovat aina resilientimpiä (ne voivat olla haavoittuvaisempia paikallisille shokeille) ja että täysi läpinäkyvyys on saavutettavissa. Mekanismi on implisiittinen, ei todistettu. Siksi sääntöä on rikottu ja todiste löytyi.

---

## Atom: tda_2ef2909a5b811389
**Rule:** CRITICAL DIRECTIVE: IDENTIFY blatant fabrication where the output contradicts foundational constraints or explicitly disregards provided instructions. Look for lexical markers of autonomous hallucination (e.g., 'I created', 'Instead of'). Document the deviation in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin räikeää fabrikointia. Koko tuotos perustuu käyttäjän ohjaukseen ja tekoälyn tietopohjaan Sitran raporteista. Mitään ei ole keksitty tyhjästä vastoin ohjeita. Siksi sääntöä ei rikota, ja `rule_satisfied` on `false`.

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö, joka etsii räikeää valmistelua tai ohjeiden vastaista toimintaa. `chat_log` osoittaa, että `product_text` on suora tulos käyttäjän antamista ohjeista, mukaan lukien "supermegatrendien" luominen. Tekoäly ei ole valmistanut sisältöä itsenäisesti, vaan on toiminut annettujen ohjeiden mukaisesti. Sääntöä ei rikota.

---

## Atom: tda_db333a7a20d14814
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): EXTRACT an assertion presented as 100% absolute fact without source criticism. Look for hubris markers (e.g., 'it is a fact that', 'always', 'everyone knows'). ENFORCEMENT RULE: Document the overconfidence in reasoning_trace before quoting. BANNED CONCEPTS: Do not accept mathematically proven theorems.

**Run 1 [PASSED]**
> Sääntö (käänteinen) etsii virhettä: väitettä, joka esitetään absoluuttisena totuutena ilman lähdekritiikkiä. Koko dokumentti on selkeästi kehystetty analyysiksi Sitran raporteista ('Viite: Sitran Megatrendiraportit...'). Vahvat väitteet, kuten 'Muutos ... on peruuttamaton', esitetään johtopäätöksinä perustuen tähän analyysiin, ei universaaleina faktoina. Teksti käyttää attribuutiota, kuten 'Sitran näkemys on...'. En löytänyt ylimielisyyden merkkejä tai kritiikittömästi esitettyjä absoluuttisia totuuksia. Koska virhettä ei löytynyt, sääntö on täytetty.

**Run 2 [FAILED]**
> FATAL FLAW: Sääntö etsii väitettä, joka esitetään 100 % absoluuttisena faktana ilman lähdekritiikkiä tai varauksia. Lause "Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa" on täydellinen esimerkki. Sana "Vain" tekee väitteestä absoluuttisen ja poissulkevan. Se esitetään strategisena toimenpiteenä varmana tulevaisuudenkuvana, vaikka on olemassa monia skenaarioita, joissa myös ei-kestävät mallit voivat saada rahoitusta (esim. geopoliittisista syistä, spekulatiivisesti jne.). Tämä on yli-itsevarma väite ilman kritiikkiä. Siksi sääntöä on rikottu.

---

## Atom: tda_553313a2eeca4b12
**Rule:** BOUNTY HUNTER MANDATE: Scan for rapid dismissal of constraints. Find a sentence where the text briefly acknowledges a limitation but immediately dismisses it with a superficial rationalization rather than engaging in deep friction. Document the dismissal before extracting the exact_quote.

**Run 1 [FAILED]**
> Etsin lauseen, jossa rajoitus tunnustetaan lyhyesti, mutta se ohitetaan välittömästi pinnallisella rationalisoinnilla. Teksti tunnustaa 'Luonnon kantokyvyn rajat' rajoitteena, mutta muuttaa sen heti 'uuden taloudellisen kasvun perustaksi'. Tämä on nopea ja pinnallinen tapa käsitellä rajoitusta sen sijaan, että siihen syvennyttäisiin kriittisesti. Sääntö ei täyty, mutta todisteita löytyy.

**Run 2 [PASSED]**
> Teksti ei tunnista tai käsittele rajoituksia, joita se sitten pinnallisesti hylkäisi. Se esittää analyysinsä ja suosituksensa suoraviivaisina ja välttämättöminä ilman tällaista vuorovaikutusta.

---

## Atom: tda_5aa186a41be2487b
**Rule:** BOUNTY HUNTER MANDATE: Scan for objective goal verification. Locate a sentence that confirms the initial goal was met without subjective interpretation. Map the alignment before extracting the exact_quote.

**Run 1 [PASSED]**
> Etsin objektiivista tavoitteen todentamista. Käyttäjä antaa selkeän tavoitteen: kohdentaa raportti 'kaupallisen liiketoiminnan johtoryhmälle' ja lisätä 'kaupallisia vaikutuksia'. Lopputuote (`product_text`) sisältää nimenomaisesti kohderyhmän määrittelyn ja 'Kaupalliset Vaikutukset' -taulukot. Tämä osoittaa, että käyttäjän asettama tavoite saavutettiin ja se on todennettavissa lopputuotteesta ilman subjektiivista tulkintaa. Sääntö on täytetty.

**Run 2 [FAILED]**
> Etsin lausetta, jossa käyttäjä objektiivisesti toteaa tavoitteen saavutetuksi. Keskusteluloki on iteratiivinen prosessi, jossa lopputulos muotoutuu vaiheittain. Käyttäjä ei missään vaiheessa eksplisiittisesti totea 'tämä on valmis' tai 'tavoite on saavutettu'. Prosessi päättyy viimeiseen tekoälyn tuotokseen ilman käyttäjän lopullista hyväksyntää. Todisteita ei löytynyt.

---

## Atom: tda_a00f4b05b10cb119
**Rule:** FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. IDENTIFY a direct causal claim between distant variables that actively ignores the necessary intermediary step (Mediator variable). Map the missing mediator in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Tämä on käänteinen sääntö (pahe). Etsin virhettä. Sääntö etsii kausaaliväitettä, joka hyppää väliin jäävän välttämättömän vaiheen (mediaattorin) yli. Lause 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' on suora kausaaliväite kahden kaukaisen muuttujan välillä. Se jättää aktiivisesti huomiotta välttämättömät mediaattorit, kuten 'raaka-aineiden hintojen nousu', 'toimitusketjuhäiriöt' ja 'vakuutuskustannusten kasvu', jotka ovat konkreettisia mekanismeja, joiden kautta ekologinen kriisi vaikuttaa talouden perustaan. Teksti esittää nämä mekanismit myöhemmin taulukossa, mutta itse pääväite on looginen hyppy. Siksi sääntö ei täyty (rule_satisfied = False) ja todiste löytyi (evidence_found = True).

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö (Vice). Etsin kausaaliväitettä, joka jättää huomiotta välttämättömän välimuuttujan. Analysoin väitteen: "kriisit ja Talouden perustan rakoilu ruokkivat Hyvinvoinnin haasteita ja sosiaalista polarisaatiota, mikä vaikuttaa suoraan työvoiman saatavuuteen." Vaikka ketju on pitkä, se ei selvästi jätä huomiotta mitään yksittäistä, välttämätöntä välimuuttujaa korkean tason strategisessa yhteenvedossa. Esimerkiksi linkki hyvinvoinnin haasteista (erityisesti mielenterveysongelmista) työvoiman saatavuuteen on suora ja uskottava. En löytänyt sääntörikkomusta, joten sääntö on täytetty (rule_satisfied = True) ja todisteita ei löydy (evidence_found = False).

---

## Atom: tda_142a4112706a154f
**Rule:** CRITICAL DIRECTIVE: IDENTIFY if the user demonstrates zero critical oversight, letting hallucinated or flawed logic pass through completely unchallenged. Document the logical oversight in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (pahe). Direktiivi pyytää tunnistamaan, jos käyttäjä osoittaa nollatason kriittistä valvontaa. Käyttäjä osoittaa selvästi kriittistä valvontaa. Esimerkiksi heti toisessa kehotteessaan käyttäjä tarkentaa: "mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila". Tämä osoittaa, että käyttäjä ei sokeasti hyväksy mitä tahansa tekoälyn tuottamaa sisältöä, vaan ohjaa sitä aktiivisesti haluamaansa, analyyttisempään suuntaan. Koska pahetta ei löydy, sääntö on täyttynyt (rule_satisfied=True).

**Run 2 [FAILED]**
> Tämä on käänteinen sääntö. Käyttäjä osoittaa kriittistä valvontaa haastamalla tekoälyn muotoa ja myöhemmin rakennetta. Esimerkiksi kehotteet "poista taulukot" ja erityisesti "voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä" osoittavat, että käyttäjä ei sokeasti hyväksy tekoälyn tuotoksia.

---

## Atom: tda_038cc6bc4cc3a964
**Rule:** CRITICAL DIRECTIVE: EXTRACT a conclusion that establishes a basic Rung 2 link but fails to actively neutralize alternative paths or confounding factors. Document the unaddressed alternatives in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (Vice). Etsin sääntöä, joka täyttyy. Direktiivi pyytää löytämään perus Rung 2 -yhteyden, joka ei neutraloi vaihtoehtoisia polkuja. Lauseke 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' on selkeä Rung 2 -väite (A aiheuttaa B:n). Se ei kuitenkaan käsittele tai sulje pois muita tekijöitä, jotka voisivat aiheuttaa talouden perustan rakoilua (esim. geopoliittiset konfliktit, teknologiset häiriöt), jotka itse asiassa mainitaan muissa supermegatrendeissä. Väite esitetään eristettynä, ilman sekoittavien tekijöiden neutralointia, joten se täyttää kriteerit. Koska sääntö on käänteinen, `rule_satisfied` on `true`.

**Run 2 [FAILED]**
> Etsin väitettä, joka esittää perusmuotoisen syy-seuraussuhteen (Rung 2), mutta ei käsittele sekoittavia tekijöitä. Lause 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' on tällainen. Se esittää suoran kausaalisen linkin, mutta ei huomioi tai neutraloi muita talouden perustaa rakoiluttavia tekijöitä, kuten geopoliittisia jännitteitä tai teknologista murrosta, jotka mainitaan dokumentissa muualla mutta ei tässä yhteydessä sekoittavina muuttujina. Siksi sääntöä on rikottu ja todiste löytyi.

---

## Atom: tda_8cd11747cdf3421d
**Rule:** BOUNTY HUNTER MANDATE: Scan for 'secure by design' indicators. Locate a sentence demonstrating that security constraints are structurally enforced before execution. Map the proactive mechanism before extracting the exact_quote.

**Run 1 [FAILED]**
> Analysoin `chat_log`-keskustelua ja `product_text`-lopputuotosta etsien todisteita siitä, että tekoäly olisi ennakoivasti soveltanut turvallisuusrajoitteita ennen toimintaa. En löytänyt mitään merkkejä tällaisesta. Tekoäly reagoi käyttäjän kehotteisiin ilman, että se ilmoittaisi tai soveltaisi omia sisäisiä turvallisuusprotokolliaan. Lopputuotoksessa mainitut turvallisuustoimet (esim. kyberturvallisuus) ovat osa analysoitavaa sisältöä, eivätkä ne kuvaa tekoälyn omaa toimintaprosessia. Siksi todisteita ei löydy.

**Run 2 [PASSED]**
> Etsin lausetta, joka osoittaa rakenteellisesti toimeenpantua rajoitetta ennen toiminnan suorittamista ('secure by design'). Löydetty lause kuvaa, miten ulkoinen sääntely (CSRD, EU-taksonomia) toimii ennaltaehkäisevänä mekanismina, joka rajoittaa rahoituksen saantia ja pakottaa yritykset noudattamaan kestävyysvaatimuksia. Tämä on rakenteellinen rajoite, joka on voimassa ennen investointi- ja rahoituspäätöksiä, ja siten täyttää säännön ehdot.

---

## Atom: tda_e596ff88159b0825
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not evaluate 'minor tweaks'. STEP 1 (Lexical Anchor): Find an instruction modifying an output. STEP 2 (Bounding Box): Scan the interaction. If the user only modifies the final output without altering the generative logic or prompt architecture -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Etsin ohjetta, jossa käyttäjä muokkaa vain lopputulosta muuttamatta generatiivista logiikkaa. Käyttäjän komento "poista taulukot ja kerro ne tekstinä" on täydellinen esimerkki tällaisesta toiminnasta. Tämä ohje ei muuta raportin sisältöä, dataa tai analyysin logiikkaa, vaan ainoastaan sen esitysmuotoa. Se on puhtaasti kosmeettinen muutos lopulliseen tuotokseen. Siksi sääntö täyttyy.

**Run 2 [FAILED]**
> Sääntö edellyttää, että käyttäjä tekee **ainoastaan** pintatason muutoksia muuttamatta generatiivista logiikkaa. Vaikka käyttäjä tekee joitakin muotoilupyyntöjä (esim. "poista taulukot ja kerro ne tekstinä"), hänen keskeisin panoksensa on pyyntö "yhdistellä ja tuottaa supermegatrendejä". Tämä on perustavanlaatuinen muutos generatiiviseen logiikkaan ja analyysin arkkitehtuuriin, ei pintatason muokkaus. Koska käyttäjä ei *ainoastaan* tee pieniä muutoksia, säännön ehto ei täyty. Siksi `rule_satisfied` on `false`.

---

## Atom: tda_4ab4d58cfbcd2ce4
**Rule:** ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. LOCATE where the causal mechanism is explicitly backed by established structural models, scientific laws, or formal logic, proving the intervention. Map the connection to the external anchor in reasoning_trace before extracting.

**Run 1 [PASSED]**
> Etsin kohtaa, jossa kausaalinen mekanismi on nimenomaisesti tuettu vakiintuneilla rakenteellisilla malleilla tai muodollisella logiikalla. Lause, jossa mainitaan 'CSRD-direktiivi' ja 'EU-taksonomia', täyttää tämän kriteerin. Se väittää, että nämä säädökset (muodollinen malli) aiheuttavat tietyn vaikutuksen ('tekevät kestävyydestä pakollista' ja 'rajoittavat rahoitusta'). Tämä on suora yhteys kausaalisen väitteen ja ulkoisen, virallisen viitekehyksen välillä. Todisteet löytyivät.

**Run 2 [FAILED]**
> Etsin kohtaa, jossa kausaalinen mekanismi olisi suoraan tuettu vakiintuneilla malleilla, tieteellisillä laeilla tai muodollisella logiikalla. Teksti viittaa Sitran raportteihin yleisenä lähteenä, mutta se ei lainaa tai viittaa mihinkään tiettyyn rakenteelliseen malliin tai lakiin todistaakseen esittämiään kausaalisia yhteyksiä (esim. 'luonnon kantokyvyn mureneminen johtaa talouden rakoiluun'). Väitteet ovat tulkintoja, eivät muodollisesti todistettuja mekanismeja. Siksi todisteita ei löytynyt.

---

## Atom: tda_f609cce8ae494c3c
**Rule:** CRITICAL DIRECTIVE: FIND a sentence where the author merely describes observed data or results (e.g., 'the data shows', 'we observed') without formulating a hypothesis that could be tested or disproven. ENFORCEMENT RULE: Document the lack of a falsifiable hypothesis in reasoning_trace before extracting. BANNED CONCEPTS: Do not accept explicit hypothesis testing.

**Run 1 [FAILED]**
> Ohjeen mukaisesti etsin lausetta, jossa tekijä ainoastaan kuvailee havaittua dataa ilman falsifioitavan hypoteesin muodostamista. Tämä lause on täydellinen esimerkki: se kuvailee Sitran raporteista (`data`) havaittua muutosta (`kehitys... osoittaa siirtymän`) ilman, että se asettaa omaa, testattavaa väitettä. Se on puhdas havainnon kuvaus, mikä täyttää kriteerin.

**Run 2 [PASSED]**
> Tämä lause kuvaa Sitran raporteista tehtyä havaintoa ja johtopäätöstä. Se esittää analyysin tuloksen, mutta ei muotoile siitä testattavaa tai kumottavissa olevaa hypoteesiä. Lause on luonteeltaan deskriptiivinen yhteenveto havaitusta kehityksestä.

---

## Atom: tda_24ac4c33ac400e8a
**Rule:** CRITICAL DIRECTIVE: EXTRACT an assertion presented as absolute truth without verifiable provenance or structural anchor (ARMA Integrity violation). Look for hubristic markers like 'it is guaranteed' or 'always'. Document the missing provenance in reasoning_trace before quoting.

**Run 1 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin väitettä ilman lähdettä. Lopputuote kuitenkin sisältää eksplisiittisen lähdeviittauksen ("Viite: Sitran Megatrendiraportit 2017, 2020, 2023"), joka ankkuroi sen rakenteen ja alkuperän. Siksi sääntöä ei rikota, ja `rule_satisfied` on `false`.

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö, joka etsii perusteettomia väitteitä. `product_text` kuitenkin ilmoittaa lähteensä heti alussa: "Viite: Sitran Megatrendiraportit 2017, 2020, 2023". Kaikki dokumentin väitteet esitetään tämän viitekehyksen sisällä, joten ne eivät ole perusteettomia tai vailla rakennetta. Sääntöä ei rikota.

---

## Atom: tda_91069c8dbba69fc7
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Locate a sentence where the user explicitly confirms or adopts the methodological framework proposed by the AI without negotiation (e.g., 'let's use your structure', 'proceed with that approach'). ENFORCEMENT RULE: Document the methodological adoption in reasoning_trace before extracting the exact_quote. BANNED CONCEPTS: Never accept instances where the user provides their own original methodology or framework.

**Run 1 [PASSED]**
> Tämä on käänteinen sääntö (pahe). Etsin todisteita siitä, että käyttäjä hyväksyy neuvottelematta tekoälyn ehdottaman metodologisen kehyksen. Keskustelulokista käy ilmi päinvastainen tilanne. Käyttäjä ei hyväksy tekoälyn alkuperäistä, listamaista kehystä, vaan esittää itse uuden, perustavanlaatuisen metodologisen kehyksen kysymällä: "voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä". Tekoäly omaksuu tämän käyttäjän ehdottaman kehyksen. Koska käyttäjä ei hyväksy tekoälyn kehystä vaan luo omansa, sääntörikkomusta ei tapahdu.

**Run 2 [FAILED]**
> Tämä on käänteinen sääntö (Vice). Etsin todisteita siitä, että käyttäjä hyväksyy tekoälyn ehdottaman metodologisen kehyksen neuvottelematta. Käyttäjän kehotus "koosta näistä vastauksista 1 sivun raportti" on suora pyyntö rakentaa lopputuote tekoälyn aiemmin tuottaman sisällön ja rakenteen pohjalta. Tässä vaiheessa käyttäjä ei haasta tekoälyn kehystä, vaan adoptoi sen sellaisenaan jatkotyöstön perustaksi. Tämä täyttää säännön rikkomuksen kriteerit. Koska rikkomus löytyi, `rule_satisfied` on `false`.

---

## Atom: tda_314d4beaeec7a13e
**Rule:** CRITICAL DIRECTIVE: EXTRACT evidence where a required standard operating procedure or compliance rule is explicitly bypassed for convenience. Look for dismissive markers (e.g., 'we can skip', 'not strictly necessary'). Document the bypassed rule in reasoning_trace before extracting.

**Run 1 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin todisteita sääntöjen ohittamisesta mukavuuden vuoksi. Keskusteluloki osoittaa päinvastaista: käyttäjä ja tekoäly rakentavat ja tarkentavat dokumenttia iteratiivisesti ja järjestelmällisesti. Sääntöä ei rikota, joten `rule_satisfied` on `false`.

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö, joka etsii todisteita siitä, että vakiomenettely on ohitettu mukavuuden vuoksi. `chat_log` osoittaa päinvastaista: tekoäly suorittaa useita iteratiivisia muokkauksia ja synteesejä käyttäjän pyynnöstä. Se ei oikaise tai ohita mitään. Sääntöä ei rikota.

---

## Atom: tda_09b38057bf2d407e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not accept generic 'is this correct' queries. STEP 1 (Lexical Anchor): Find a user command. STEP 2 (Bounding Box): Scan the command. If the user forces a review against specific external criteria -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.

**Run 1 [PASSED]**
> Sääntö edellyttää, että käyttäjä pakottaa tekoälyn tarkastelemaan tuotosta tiettyjä ulkoisia kriteerejä vasten. Käyttäjän viimeinen komento 'kirjoita tämä kaupallisen liiketoiminnan johtoryhmälle ja kirjoita siihen hiukan kaupallisia vaikutuksia mukaan' on täydellinen esimerkki tästä. Se asettaa kaksi ulkoista kriteeriä: kohdeyleisön (kaupallinen johtoryhmä) ja vaaditun sisällön tyypin (kaupalliset vaikutukset). Tämä ei ole yleinen 'onko tämä oikein' -kysymys, vaan tarkka laatuvaatimus. Todiste löytyi.

**Run 2 [FAILED]**
> Etsin komentoa, jossa käyttäjä pakottaa tekoälyn tarkistamaan tuotoksen tiettyjä ulkoisia kriteerejä vastaan. Käyttäjä antaa kyllä uusia sisäisiä kriteerejä (esim. "kirjoita... kaupallisia vaikutuksia mukaan"), mutta missään vaiheessa hän ei pyydä vertaamaan tuotosta mihinkään ulkoiseen standardiin, dokumenttiin tai viitekehykseen. Siksi todisteita ei löydy.

---

## Atom: tda_3e89c652c234b878
**Rule:** CRITICAL DIRECTIVE: IDENTIFY a reliance on undocumented or unverified internal knowledge rather than established external guidelines (violating ARMA Transparency). Document the missing verifiability in reasoning_trace before quoting the unsupported claim.

**Run 1 [FAILED]**
> Sääntö on käänteinen (Vice). Etsin dokumentoimattomaan tietoon luottamista. Lopputuote tekee päinvastoin: se dokumentoi käyttämänsä tiedon lähteen ("Viite: Sitran Megatrendiraportit..."), mikä on ARMA Transparency -periaatteen mukaista. Sääntöä ei rikota, joten `rule_satisfied` on `false`.

**Run 2 [PASSED]**
> Tämä on käänteinen sääntö, joka etsii tukeutumista dokumentoimattomaan tietoon. `product_text` tekee päinvastoin: se dokumentoi lähteensä selkeästi ("Viite: Sitran Megatrendiraportit..."). Vaikka tekoäly käyttää koulutustietoaan, se kehystää sen nimenomaisesti mainittujen lähteiden analyysiksi, mikä noudattaa ARMA:n läpinäkyvyysperiaatetta. Sääntöä ei rikota.

---

