# Epic 51: TDA Knowledge Grounding & Seed Data Refactor

## 1. Yhteenveto ja Tavoite (Objective)
Tämän Epicin tavoitteena on suorittaa **"Kognitiivinen Siivous" (Cognitive Cleanup)** koko järjestelmän ytimeen. Vaikka Epic 48 rakensi taustalle täydellisen TDA-arkkitehtuurin (Test-Driven Assertion), nykyinen tietokantadata (`backend_v2/seed/seed_data.json`) on yhä jäänne V1-ajalta: se on 1:1 kopioitu yksinkertaisista lauseista.

Tässä Epicissä käymme järjestelmällisesti läpi koko `seed_data.json` -tiedoston (solu kerrallaan) käyttäen tekoälyn "Generator-Critic-Refiner" -loopia. Jokainen arviointikriteeri muutetaan huipputarkkaan XML-hybridimuotoon ja jaetaan 2-5 mikrotason matemaattisesti todennettavaan EHDOTTOMAAN TDA-väitteeseen.

## 2. Arkkitehtuuriset Mandaatit (The Rules of Engagement)

Jokainen matriisin `ai_description` ja `tda_assertions` -kenttä on tästä hetkestä lähtien muotoiltava seuraavien viiden ehdottoman säännön mukaisesti. Yksikin sääntörikkomus kaataa koko Pydantic-tason Fail-Fast -rutiinin tai tuhoaa arvioinnin validiteetin. Poikkeuksia ei sallita.

### 1. CHUNK-TURVALLINEN KÄÄNTEISLOGIIKKA (The Absence Paradox)
**Ongelma:** Asynkroninen worker näkee vain yhden irrallisen lohkon kerrallaan. Puutteen (omission) etsiminen aiheuttaa tekoälyssä joko hallusinaatioita tai massiivisen määrän vääriä negatiivisia tuloksia (False Negatives).
**Mandaatti:** Kun luot "Fatal Flaw" -kriteerejä (`inverse_evidence: true`), sääntö on EHDOTTOMASTI muotoiltava niin, että virhe **materialisoituu lokaalina lauseena** (commission). Pakota tekoäly poimimaan itse rikkova, virheellinen väite `exact_quote`-kenttään. Älä koskaan käske tekoälyä etsimään tyhjiötä.
* 🚫 **KIELLETTY (Omission):** *"Oikeutus puuttuu."* tai *"Kirjoittaja ei esitä dataa väitteensä tueksi."*
* ✅ **SALLITTU (Commission):** *"Etsi lause, jossa kirjoittaja esittää subjektiivisen olettamuksen 100% absoluuttisena faktana."*

### 2. LATTIALOGIIKAN MATEMATIIKKA (Floor vs. Ceiling Logic)
**Ongelma:** Z-tason Waterfall- ja DINA-kaskadimoottorit tuhoavat kokonaisarvosanan, jos alin taso reputetaan. Katto-logiikka alatasolla (esim. "teksti ainoastaan toistaa") reputtaa huipputekstit.
**Mandaatti:** Tasojen 1 ja 2 POSITIIVISET vaatimukset (`inverse_evidence: false`) on muotoiltava inklusiivisella "lattia-logiikalla" (Floor Logic). Säännön on kuvattava perusmekanismi, jonka myös nerokas teksti tekee automaattisesti sivutuotteenaan. Kieltosanojen (vain, ainoastaan, pelkästään) käyttö alatasojen positiivisissa kriteereissä on nollatoleranssissa.
* 🚫 **KIELLETTY (Ceiling Logic):** *"Teksti ainoastaan toistaa annettua tietoa."*
* ✅ **SALLITTU (Floor Logic):** *"Teksti sisältää alkuperäisen tiedon tunnistamista ja toistamista."*

### 3. LEKSIKAALISET INDIKAATTORIT (Lexical Proxies)
**Ongelma:** RapidFuzz ymmärtää vain fyysisiä merkkejä. Pelkät konseptuaaliset abstraktiot saavat LLM:n poimimaan epämääräisiä lauseita.
**Mandaatti:** Jokaiseen abstraktia konseptia mittaavaan TDA-väitteeseen on pakotettava konkreettiset kielelliset sormenjäljet eli **Leksikaaliset indikaattorit (Lexical Proxies)**. Anna tekoälylle täsmälliset englanninkieliset siirtymäsanat (esim. 'however', 'therefore') ja ohjeista se etsimään näiden vastineita dokumentin alkuperäiskielellä.
* 🚫 **KIELLETTY:** *"Find evidence of cognitive friction."*
* ✅ **SALLITTU:** *"Find evidence of cognitive friction. Look for lexical markers of contrast such as 'however', 'on the other hand', or 'therefore' (in the document's native language). Extract the sentence containing this structural opposition."*

### 4. CHAIN-OF-THOUGHT (CoT) PAKOTUS SÄÄNTÖTASOLLA
**Ongelma:** Jos LLM ohjeistetaan suoraan poimimaan lainaus, se kärsii kognitiivisesta laiskuudesta ja "jälkikäteisrationalisoi" lainaukset.
**Mandaatti:** LLM on pakotettava perustelemaan looginen ketjunsa **ennen** lainauksen poimimista (ohjaamalla se tuottamaan logiikka JSON:n `reasoning_trace`-kenttään ensin).
* 🚫 **KIELLETTY:** *"Poimi exact_quote, joka osoittaa kausaalisuuden."*
* ✅ **SALLITTU:** *"ENFORCEMENT RULE: Ennen exact_quote-lainauksen poimimista, dokumentoi syy-seurausmekanismi askeleittain. Vasta kun olet loogisesti perustellut päättelyn, poimi TÄSMÄLLINEN lainaus."*

### 5. ANTI-TOKEN BLOAT & XML-RAKENNE
**Ongelma:** Raskaat roolitukset ja XML-tagit mikrosäännöissä paisuttavat Map-Reduce -lohkojen promptit käyttökelvottomiksi.
**Mandaatti:** Eristä globaali konteksti ja XML-tagit puhtaasti ylätason `ai_description` -kenttään (Makrotaso, max 1-2 lausetta per tagi). Mikrotason `tda_assertions` (`ai_rule_description`) on oltava puhdasta, konemaista ja XML-vapaata imperatiivista tekstiä. Koodaa toimintaverbit isoin kirjaimin.
* 🚫 **KIELLETTY (Mikrotasolla XML-kohinaa):** `<rule>Etsi todiste...</rule> <cot>Perustele ensin...</cot>`
* ✅ **SALLITTU (Puhdas imperatiivi):** *"CRITICAL DIRECTIVE: Etsi tekstistä leksikaalinen indikaattori vastaväitteelle (esim. 'kuitenkin'). Pura logiikka askeleittain ennen exact_quote-poimintaa."*

### 6. UNIVERSAL LANGUAGE PROTOCOL (Native English Mandate)
* **Säännöt ovat 100% englantia:** Kaikki tekoälyn promptit (`ai_description`, `ai_rule_description`) kirjoitetaan tietokantaan yksinomaan englanniksi tekoälyn "Intelligence Dropping" -ilmiön välttämiseksi.
* **Dokumentti voi olla mitä tahansa kieltä:** Tekoälyä ohjeistetaan aina etsimään konseptit ja leksikaaliset indikaattorit kohdedokumentin omalla kielellä (esim. *"Look for 'therefore' or its equivalent in the document's native language"*). Suomenkieliset UI-tekstit pidetään täysin erillään taustalogiikasta.

### 7. TEOREETTINEN ANKKUROINTI (No Hollow Pydantic Structures)
**Ongelma:** Pelkkä XML-tägien ja Pydantic-rakenteen mekaaninen lisääminen ei paranna tekoälyn arviointikykyä, jos itse kriteeri on ontto tai jättää tulkinnanvaraa.
**Mandaatti:** Generaattori-Kriitikko-Jalostaja -työnkulussa **jokaisen TDA-väitteen on nojattava todelliseen teoriaan**, ei vain onttoon Pydantic-rakenteeseen. Jokaisen refaktoroidun blokin päätteeksi tekoälyn on raportoitava eksplisiittisesti, kuinka teoriainjektio (esim. uuden tutkimuksen käsitteet) integroitiin syvälle mikrosääntöihin asti.

### 8. PAKOLLINEN TIEDONHAKU (Mandatory Web Search & Grounding)
**Ongelma:** "Puhdas" AI käyttää vain sisäistä päättelyään (yleistä hallusinaatiota) täydentämään akateemisia viitteitä, jolloin syväkonteksti ohenee.
**Mandaatti:** Jos tekoäly on injektoimassa teoriaa, käsitteitä tai rakentamassa `epistemic_anchor` -viitettä, sen on EHDOTTOMASTI käytettävä `search_web` -työkalua hakeakseen täsmälliset teoriatermit (esim. Kahnemanin System 1/2 määritelmät tai Floridin "Human-in-the-loop"). Akateemisten käsitteiden arvailu on kielletty.

### 9. TURVALLINEN JSON-MANIPULAATIO (Python Scripts Only)
**Ongelma:** Massiivisen ja syvästi sisäkkäisen `seed_data.json` -tiedoston muokkaaminen merkkijonokorvauksilla rikkoo lähes aina JSON-skeeman (pilkkujen puuttuminen, sisennykset).
**Mandaatti:** AI on EHDOTTOMASTI KIELLETTY muokkaamasta `seed_data.json` -tiedostoa suoraan. Kaikki muutokset on tehtävä kirjoittamalla lokaali Python-skripti (esim. `scratch/refactor.py`), joka lataa JSONin tietorakenteena, tekee täsmällisen muokkauksen kohteena olevan blokin dataan (`data['prompt_blocks']`), ja tallentaa sen takaisin. Tämä takaa 100% syntaktisen eheyden.

### 10. IMPERATIIVINEN KÄSKYMUOTO (Actionable Directives)
**Ongelma:** Laiska AI kysyy arvioinnissa passiivisia kysymyksiä ("Onko tässä syy-seuraussuhde?").
**Mandaatti:** Mikrotason `ai_rule_description` ei saa KOSKAAN olla kysymys tai passiivinen toteamus. Sen on AINA alettava imperatiivisella toimintaverbillä (Etsi, Tunnista, Eristä / Identify, Locate, Find), joka pakottaa "työntekijä-tekoälyn" aktiivisesti haravoimaan näyttöä ja poimimaan `exact_quote` -todisteen.

### 11. 100% KATTAVUUSVAATIMUS (Comprehensive Traversal)
**Ongelma:** Laiska AI refaktoroi matriisista vain ylimmät pisteet (esim. score 1 ja 5) tai jättää osan väitteistä (claims) ennalleen, jolloin vanhaa V1-dataa jää kummittelemaan rakenteen sisään.
**Mandaatti:** AI on EHDOTTOMASTI pakotettu käymään läpi ja refaktoroimaan matriisin **jokainen pistetaso (score 1-5)** ja niiden sisällä oleva **jokainen yksittäinen väite (claim)**. Koko kohde-matriisin JSON-haara on käsiteltävä 100% kattavasti; oikominen, yhdistely tai osittainen suoritus on ehdottomasti kielletty.

### 12. EHDOTON TRACKER-SUVEREENIUS (Absolute Tracker Sovereignty)
**Ongelma:** Tietokannassa (`seed_data.json`) saattaa näkyä jäänteitä aiemmista epäonnistuneista tai osittaisista refaktoroinneista, jotka näyttävät tekoälylle siltä, että työ olisi jo tehty (esim. `tda_assertions` löytyy).
**Mandaatti:** `epic51_matrix_tracker.md` on AINOA lähde totuudelle. Osa refaktoroinnista on tietoista valittua uudelleenajoa. Jos matriisi on trackerissä tilassa `[NOK]`, se ON refaktoroitava uudelleen nollasta riippumatta siitä, mitä `seed_data.json` näyttää. Tietokannan tilalla ei ole mitään merkitystä, jos tracker sanoo `[NOK]`.

### 13. EKSPLISIITTISET POISSULKULISTAT (Banned Concepts & Anti-Proxies)
**Ongelma:** Tekoäly tulkitsee kielellisiä indikaattoreita ("kuten OWASP") ehdotuksina ja alittaa aidan matalimmasta kohdasta hyväksyen ylätason markkinointitermejä. Tämä altistaa arvioinnin "haamuvarianssille" huomion herpaantuessa.
**Mandaatti:** Jokaiseen käsitteelliseen TDA-väitteeseen on sisällytettävä EHDOTON KIELTO (Banned Concepts). Tekoälylle on kerrottava eksplisiittisesti, mitä se EI saa hyväksyä osumaksi.
* 🚫 **KIELLETTY (Valinnaisuus):** *"Etsi tietoturvakehyksiä, kuten OWASP tai vastaava."*
* ✅ **SALLITTU (Poissulkulista):** *"REQUIRED: Etsi OWASP, NIST. BANNED CONCEPTS: Älä koskaan hyväksy ylätason termejä kuten 'tietosuoja' tai 'kyberturvallisuus'."*

### 14. "PALKKIONMETSÄSTÄJÄ"-PARADIGMA (Fatal Flaw over Consistency)
**Ongelma:** "Johdonmukaisen välttelyn" etsiminen 32 000 merkin tekstistä ylittää tekoälyn Attention-mekanismin kyvyt (Lost in the Middle -ongelma). Tulos heiluilee satunnaisuuden mukaan.
**Mandaatti:** Kaikki säännöt, jotka vaativat "johdonmukaisuutta" tai "sävyn ylläpitämistä" koko tekstissä, on EHDOTTOMASTI käännettävä `inverse_evidence: true` -muotoon. Tekoäly ei todista viattomuutta, vaan se asetetaan "tuhoamismoodiin" etsimään yhtä ainoaa rikkomusta.
* 🚫 **KIELLETTY (Johdonmukaisuuden todistaminen):** *"Teksti välttelee absoluuttisia termejä johdonmukaisesti."*
* ✅ **SALLITTU (Bounty Hunter -moodi):** *"CRITICAL DIRECTIVE (FATAL FLAW): Etsi tekstistä YKSI KIN lause, jossa käytetään absoluuttista termiä (esim. 'ainoa tapa taata'). Jos löydät, poimi exact_quote."*

### 15. YKSINAPAINEN LOOGINEN PORTTI (Boolean Integrity)
**Ongelma:** Kaksoiskiellot ja monimutkaiset lauserakenteet ("Teksti on passiivinen EIKÄ sisällä itsetutkiskelua") aiheuttavat tekoälyn loogisessa portissa oikosulun, jolloin se saattaa kirjoittaa oikean perustelun mutta antaa käänteisen boolean-arvon (`FALSE`).
**Mandaatti:** TDA-väitteiden on oltava "yksinapaisia". Ei AND/OR -lausekkeita. Ei negatiivisia määreitä mittaamaan positiivista tulosta (ei "puuttuu" tai "ei sisällä"). Sääntö mittaa AINA vain ja ainoastaan etsittävän asian aktiivista läsnäoloa.
* 🚫 **KIELLETTY (Kaksoiskielto/Kompleksinen):** *"Teksti on passiivinen EIKÄ ota kantaa EIKÄ ehdota ratkaisuja."*
* ✅ **SALLITTU (Yksinapainen aktiivinen haku):** *"Etsi lause, jossa kirjoittaja aktiivisesti ulkoistaa päätöksenteon muille tahoille (delegaatio)."*

### 2.1 Epistemologiset ja Laadulliset Mandaatit (The Grounding Rules)
Tämä on vain kerta-ajo, joten data on ankkuroitava oikeaan maailmaan huolellisesti.
1. **Epistemic Anchoring:** Pelkkä tekoälyn "yleistieto" ei riitä. Jokaiseen `ai_description` -kenttään on injektoitava `<epistemic_anchor>` -tagi, joka sisältää verifioidun akateemisen tai rakenteellisen ankkurin (esim. suora viittaus Sitran megatrendi-metodologiaan tai Kahnemanin tiettyyn sivuun/käsitteeseen).
2. **Anti-Patternien Injektointi (Few-Shot):** Varsinkin `inverse_evidence: true` (Fatal Flaw) -säännöissä on pakko tarjota tekoälylle yksi mikroskooppinen reaalimaailman esimerkkilause siitä, miltä virhe näyttää käytännössä.
3. **Kontekstuaalinen Jargon:** Säännöissä on huomioitava toimialakohtainen kieli käyttämällä `search_web` -työkalua esimerkiksi hallintojargonin tai strategiaslangin tunnistamiseen.

## 3. Toteutuksen Vaiheet ja Automaattinen Työnkulku (State-Tracked Workflow)

### Phase 1: Seurannan alustus (Matrix Tracker)
* **Tehtävä:** Eristetään `seed_data.json` -tiedostosta kaikki matriisit (`category_id: "matrix"`) ja luodaan niille seurantatiedosto `epic51_matrix_tracker.md`.
* **Toteutus:** Kaikki matriisit merkitään alkutilaan `[NOK]`. Tämä tiedosto toimii koko työnkulun "Aivoina", jotta konteksti-ikkunat voidaan tyhjentää välissä tekoälyn suorituskyvyn takaamiseksi.

### Phase 2: "Raskas" Itseohjautuva Refaktorointilooppi
* **KRIITTINEN SÄÄNTÖ: YKSI MATRIISI PER CHAT.** AI:n kognitiivisen tason ylläpitämiseksi yhdessä konteksti-ikkunassa (chatissa) saa refaktoroida **vain ja ainoastaan yhden matriisin**. Kun matriisi on valmis, session on päätyttävä ja seuraava matriisi on aloitettava täysin uudessa puhtaassa ikkunassa.
* **SÄÄNTÖ 1:** Matriisin alkuperäistä skaalaa (esim. 1-5) ei saa koskaan muuttaa tai kaventaa.
* **SÄÄNTÖ 2:** Tekoäly EI saa pyytää käyttäjää sanomaan "Jatka". Työvaiheen päätteeksi tekoälyn on aina annettava vakiokomento `/tier5-resume --target docs/epic/epic51_matrix_tracker.md`. EHDOTON VAATIMUS: Seuraavaan matriisiin siirtyminen vaatii AINA puhtaan, uuden konteksti-ikkunan. Vanhaa ikkunaa ei saa käyttää kahden matriisin käsittelyyn.
* **SÄÄNTÖ 3:** `[NOK]`-merkittyjä matriiseja voi olla missä tahansa kohtaa `epic51_matrix_tracker.md` -listaa. Etsi aktiivisesti mikä tahansa jäljellä oleva `[NOK]` riippumatta sen sijainnista.
* **SÄÄNTÖ 4 (Execution Note):** Tässä silmukassa tai Epicin valmistuessa EI SAA koskaan ajaa komentoja `/tier2-execute` tai `/tier2-hardening-backend`. Muokkaamme ainoastaan JSON-muotoista seeder-dataa, emmekä tee rakenteellisia muutoksia Python- tai Flutter-ohjelmakoodiin.
* **Työnkulku:** 
  1. **Uusi Konteksti:** Ihminen avaa puhtaan chatin ja ajaa komennon: `/tier5-resume --target docs/epic/epic51_matrix_tracker.md`. Tekoäly ei saa ehdottaa toisen matriisin käsittelyä samassa istunnossa.
  2. **Teorian Purku (Tiedonhaku ja Ankkurointi):** AI hakee matriisin sisällön `seed_data.json` -tiedostosta. AI on **pakotettu** tekemään `search_web` -haun etsiäkseen aidon tieteellisen lähteen tai metodologisen viitekehyksen (esim. argumentaatioteoria, kognitiiviset vinoumat). Samalla se etsii oikean maailman esimerkkejä (Anti-Patterns) ja tunnistaa oikeat leksikaaliset siirtymäsanat.
  3. **Generointi (XML & TDA):** AI rakentaa `05_llm_architecture.md` -sääntöjen mukaisen Native English XML-ohjeen (`ai_description`), johon se sisällyttää `<epistemic_anchor>` -viitteen. Se kääntää teorian 2-5:ksi toisensa poissulkevaksi mikrosäännöksi. **Sääntöihin injektoidaan aina negatiivinen "Few-Shot" -esimerkki, jos `inverse_evidence: true`**. Jokaiselle uudelle TDA-säännölle on generoitava täysin uusi ja ainutkertainen "Opaque Stripe ID" (esim. `tda_` + 16-32 merkin satunnainen hex-arvo Pydantic-standardin mukaisesti). **KRIITTINEN PYDANTIC-SÄÄNTÖ:** Jos `inverse_evidence` on `true`, `aggregation_mode` on EHDOTTOMASTI oltava `"EXISTS"` (muuten Pydantic V2 kaatuu `validate_math_logic` -validaattoriin). Jos `inverse_evidence` on `false`, se voi olla `"ALL_MUST_COMPLY"`.
  4. **Auditointi & Pydantic-Verifikaatio:** AI ehdottaa säännöt ihmiselle esittäen selkeästi löytämänsä akateemisen ankkurin ja leksikaaliset indikaattorit. Kun ihminen hyväksyy, AI tallentaa ne `seed_data.json` -tiedostoon (skriptillä). **KRIITTINEN VERIFIKAATIO:** Välittömästi skriptin ajon jälkeen ihmistä ohjeistetaan AINA ajamaan seuraava komentosarja (joka sisältää MECE-tarkistuksen ja Pydantic-testit): `uv run python scratch/verify_claims.py; uv run pytest backend_v2/tests/unit/test_seed_architectural_guardrails.py backend_v2/tests/unit/test_matrix_data_integrity.py -v`. Tämä takaa Fail-Fast -rakenteen säilymisen jokaisen matriisin jälkeen.
  5. **Tilan tallennus ja Kattava Raportointi:** AI päivittää seurantatiedostoon tilaksi `[OK]`. **Pakollinen Mandaatti-Audit (Loppuraportti):** AI:n on raportoitava EHDOTTOMASTI ALLA OLEVAN EKSPLISIITTISEN TARKISTUSLISTAN AVULLA, miten se on täyttänyt arkkitehtuurimandaatit tässä refaktoroinnissa (jos yksikin näistä 6 kohdasta puuttuu, AI on epäonnistunut tehtävässään):
     - [ ] 1. **Teoriainjektio:** Mitä teoriaa haettiin (search_web) ja miten se injektoitiin väitteisiin.
     - [ ] 2. **Käänteis- ja Lattialogiikka:** Miten käänteislogiikka ja lattialogiikka toteutettiin (ei "puutetta" vaan aktiivinen komissio).
     - [ ] 3. **Leksikaaliset indikaattorit & Poissulkulistat:** Mitkä leksikaaliset indikaattorit pakotettiin ja **mitkä ylätason termit kiellettiin (Anti-Proxies)**.
     - [ ] 4. **Bounty Hunter -paradigma:** Vahvistus, että kaikki johdonmukaisuutta vaativat säännöt on käännetty `inverse_evidence: true` -tuhoamismoodiin.
     - [ ] 5. **Boolean Integrity:** Vahvistus, että säännöistä on siivottu kaikki kaksoiskiellot ja monimutkaiset AND/OR -portit.
     - [ ] 6. **CoT-perustelu:** Miten CoT-perustelu pakotettiin ennen `exact_quote`-poimintaa.
     - [ ] 7. **100% kattavuus:** Vahvistus 100% kattavuudesta JSONin Python-skriptauksella.
     - [ ] 8. **MECE-sääntö (Rule of 3):** Etsittiin kaikki refaktoroidut 'claims' `verify_claims.py` -skriptillä ja raportoitiin niiden lukumäärä vahvistuksena MECE-säännön (tasan 3 kpl/solu) toteutumisesta.
     
     Lopuksi AI ohjeistaa ihmistä aina ehdottomasti tällä vakiokomennolla: *"Matriisi valmis. Avaa uusi puhdas chat ja aja komento: `/tier5-resume --target docs/epic/epic51_matrix_tracker.md`"*

### Phase 2.5: "Haamuvarianssi" (Wobble) -matriisien V3-Kovetus
* **Tehtävä:** Aiempi analyysi paljasti, että kysymysten satunnaistaminen (Blind Shuffle) aiheuttaa 15 pisteen heittoja, koska 13 matriisin vanhat säännöt vuotavat (niissä on kaksoiskieltoja, liiaksi tulkinnanvaraa tai laajoja johdonmukaisuusvaatimuksia). Nämä 13 matriisia on refaktoroitava uudelleen "Hardened 2.0" -säännöillä (Säännöt 13, 14, 15).
* **Kohteet (13 matriisia):** `blk_53f3...`, `blk_6b8c...`, `blk_c3bc...`, `blk_f6e2...`, `blk_c580...`, `blk_8073...`, `blk_fb15...`, `blk_ff72...`, `blk_440a...`, `blk_f921...`, `blk_22e3...`, `blk_109d...`, `blk_b476...`.
* **Toteutus:** Nämä 13 matriisia on merkittävä trackerissä takaisin tilaan `[NOK]` (tai esim. `[NOK-V3]`), vaikka ne olisivat jo aiemmin saaneet `[OK]`. Ne käydään läpi yksi kerrallaan käyttäen nimenomaan yksinapaisia portteja, palkkionmetsästäjä-moodia ja poissulkulistoja.
* **Tehtävä:** Käydään läpi järjestelmän vaikeimmat matriisit.
* **Kohteet (esim.):**
  * *Catastrophic Failure / Hubris* (System 1 dominanssi)
  * *Lähdekritiikki ja Lähdehallusinaatiot*
  * *Performativiteetti ja Tyhjät Korusanat* (Sycophancy)

### Phase 3: "Rakenteellisten" -matriisien refaktorointi
* **Tehtävä:** Käydään läpi dokumentin muotoiluun, loogiseen järjestykseen ja työnkulkuun liittyvät solut.
* **Kohteet (esim.):**
  * *Looginen silta (Cohesion)*
  * *Johtopäätösten kestävyys*

### Phase 4: Tietokannan Nollaus ja Quality Gate
* **Tehtävä:** Tietokannan nollaus ja datan injektio. **KRIITTINEN SÄÄNTÖ:** Tätä vaihetta EI SAA SUORITTAA ennen kuin *jokainen* matriisi tiedostossa `epic51_matrix_tracker.md` on merkitty tilaan `[OK]`. Keskeneräisen datan ajaminen seederiin (`run_seed.py`) on ehdottomasti kielletty.
* **Komennot:**
  * `uv run python backend_v2/seed/run_seed.py local`
  * Ajetaan `backend_audit_loop.py` varmistamaan, että mikään uusi sääntö ei rikkonut Pydantic V2 -skeemoja (`extra='forbid'`).
  * Ajetaan uusi asynkroninen arviointiajo jollain testidokumentilla ja seurataan, kuinka RapidFuzz ja Fail-Fast hoitavat uudet moniosaiset TDA-väitteet.

## 4. Definition of Done (DoD)
- Koko `seed_data.json` -tiedoston `ai_description` ja `tda_assertions` -kentät on kirjoitettu uudelleen Epic 48:n V2-standardeilla.
- Yksikään `ai_description` ei ole litteää tekstiä, vaan käyttää `<system_directive>` XML-rakennetta.
- Jokaisessa solussa on TASAN 3 toisistaan riippumatonta (MECE-periaatteella trianguloitua) EHDOTONTA `TDAAssertion` -sääntöä, optimaalisen tilastollisen validiteetin ja kognitiivisen kuorman tasapainon takaamiseksi.
- Uusi data on ajettu menestyksekkäästi paikalliseen tietokantaan (`run_seed.py`).
- Yksikään Pydantic-validointi ei kaadu, ja järjestelmä läpäisee Universal Quality Gaten (Tier 2).
