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
* **Työnkulku:** 
  1. **Uusi Konteksti:** Ihminen avaa puhtaan chatin ja sanoo "Jatka" (tai antaa tietyn matriisin ID:n, esim. `blk_440a5fef9331451b`).
  2. **Valinta:** AI lukee `epic51_matrix_tracker.md` -tiedoston ja poimii listalta seuraavan `[NOK]`-tilassa olevan matriisin.
  3. **Teorian Purku (Tiedonhaku ja Ankkurointi):** AI hakee matriisin sisällön `seed_data.json` -tiedostosta. AI on **pakotettu** tekemään `search_web` -haun etsiäkseen aidon tieteellisen lähteen tai metodologisen viitekehyksen (esim. argumentaatioteoria, kognitiiviset vinoumat). Samalla se etsii oikean maailman esimerkkejä (Anti-Patterns) ja tunnistaa oikeat leksikaaliset siirtymäsanat.
  4. **Generointi (XML & TDA):** AI rakentaa `05_llm_architecture.md` -sääntöjen mukaisen Native English XML-ohjeen (`ai_description`), johon se sisällyttää `<epistemic_anchor>` -viitteen. Se kääntää teorian 2-5:ksi toisensa poissulkevaksi mikrosäännöksi. **Sääntöihin injektoidaan aina negatiivinen "Few-Shot" -esimerkki, jos `inverse_evidence: true`**. Jokaiselle uudelle TDA-säännölle on generoitava täysin uusi ja ainutkertainen "Opaque Stripe ID" (esim. `tda_` + 16-32 merkin satunnainen hex-arvo Pydantic-standardin mukaisesti). **KRIITTINEN PYDANTIC-SÄÄNTÖ:** Jos `inverse_evidence` on `true`, `aggregation_mode` on EHDOTTOMASTI oltava `"EXISTS"` (muuten Pydantic V2 kaatuu `validate_math_logic` -validaattoriin). Jos `inverse_evidence` on `false`, se voi olla `"ALL_MUST_COMPLY"`.
  5. **Auditointi:** AI ehdottaa säännöt ihmiselle esittäen selkeästi löytämänsä akateemisen ankkurin ja leksikaaliset indikaattorit. Kun ihminen hyväksyy, AI tallentaa ne `seed_data.json` -tiedostoon.
  6. **Tilan tallennus:** AI päivittää seurantatiedostoon tilaksi `[OK]` ja ohjeistaa ihmistä: *"Matriisi valmis. Avaa uusi puhdas chat ja sano Jatka."*

### Phase 3: "Raskaan Kognition" -matriisien refaktorointi
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
* **Tehtävä:** Kun koko `seed_data.json` on käyty läpi, järjestelmä nollataan ja uusi data injektoidaan.
* **Komennot:**
  * `uv run python backend_v2/seed/run_seed.py local`
  * Ajetaan `backend_audit_loop.py` varmistamaan, että mikään uusi sääntö ei rikkonut Pydantic V2 -skeemoja (`extra='forbid'`).
  * Ajetaan uusi asynkroninen arviointiajo jollain testidokumentilla ja seurataan, kuinka RapidFuzz ja Fail-Fast hoitavat uudet moniosaiset TDA-väitteet.

## 4. Definition of Done (DoD)
- Koko `seed_data.json` -tiedoston `ai_description` ja `tda_assertions` -kentät on kirjoitettu uudelleen Epic 48:n V2-standardeilla.
- Yksikään `ai_description` ei ole litteää tekstiä, vaan käyttää `<system_directive>` XML-rakennetta.
- Jokaisessa monimutkaisessa solussa on vähintään 2-3 EHDOTONTA `TDAAssertion` -sääntöä.
- Uusi data on ajettu menestyksekkäästi paikalliseen tietokantaan (`run_seed.py`).
- Yksikään Pydantic-validointi ei kaadu, ja järjestelmä läpäisee Universal Quality Gaten (Tier 2).
