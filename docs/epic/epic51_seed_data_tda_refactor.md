# Epic 51: TDA Knowledge Grounding & Seed Data Refactor

## 1. Yhteenveto ja Tavoite (Objective)
Tämän Epicin tavoitteena on suorittaa **"Kognitiivinen Siivous" (Cognitive Cleanup)** koko järjestelmän ytimeen. Vaikka Epic 48 rakensi taustalle täydellisen TDA-arkkitehtuurin (Test-Driven Assertion), nykyinen tietokantadata (`backend_v2/seed/seed_data.json`) on yhä jäänne V1-ajalta: se on 1:1 kopioitu yksinkertaisista lauseista.

Tässä Epicissä käymme järjestelmällisesti läpi koko `seed_data.json` -tiedoston (solu kerrallaan) käyttäen tekoälyn "Generator-Critic-Refiner" -loopia. Jokainen arviointikriteeri muutetaan huipputarkkaan XML-hybridimuotoon ja jaetaan 2-5 mikrotason matemaattisesti todennettavaan EHDOTTOMAAN TDA-väitteeseen.

## 2. Arkkitehtuuriset Mandaatit (The Rules of Engagement)
Kaikki uudet säännöt (`ai_description` ja `ai_rule_description`) on luotava näiden viiden EHDOTTOMAN säännön puitteissa:

1. **Akateeminen ankkurointi (Ei AI-hallusinaatiota)**: Kriteerit perustuvat vahvasti tieteellisiin ja loogisiin teorioihin (esim. Kahnemanin System 1 / System 2, kognitiiviset vinoumat).
2. **Tiivis "Hybrid Prompting" (Anti-Token Bloat)**: Ylätason `ai_description` on aina formatoitava XML-tageilla (esim. `<system_directive><persona>...</persona></system_directive>`). Koska nämä injektoidaan usein Claim-tasolla, niiden on oltava äärimmäisen lyhyitä ja tiiviitä (max 1-2 lausetta), jotta vältetään LLM:n huomiokyvyn hukkuminen ja turhat API-kulut.
3. **Native English Mandate**: Jotta tekoälyn looginen päättelykyky ei romahda (Intelligence Dropping), kaikki säännöt ja promptit on kirjoitettava **100% englanniksi**. Suomenkieliset selitteet (translations) pidetään erillään UI-tarpeita varten.
4. **Mikro-TDA Fokus**: Säännön (`ai_rule_description`) on oltava yksi, yksiselitteinen väite, johon LLM voi vastata "Kyllä/Ei" ja osoittaa sen todeksi yhdellä tekstilainauksella (`exact_quote`). Sääntö ei saa sisältää liikaa "tai"-ehtoja, jotka hämärtävät arviointia.
5. **Käänteinen logiikka ja Negatiivisen lainauksen ongelma (`inverse_evidence`)**: Kun etsitään vikoja, säännössä on asetettava `"inverse_evidence": true`. **Kriittinen sääntö:** Koska tekoäly ei voi lainata (`exact_quote`) asiaa jota ei ole olemassa (esim. puuttuvaa dataa), käänteinen sääntö on kirjoitettava niin, että virhe materialisoituu. Esim: *"Kirjoittaja esittää vahvan väitteen, mutta ei tarjoa sille dataa"*. Tällöin tekoäly poimii lainaukseksi itse perusteettoman väitteen!
6. **Foundation vs Ceiling -logiikka (Vesiputousmatematiikka)**: Alimpien tasojen (esim. Taso 1 ja 2) TDA-väitteet on EHDOTTOMASTI kirjoitettava "Lattia-logiikalla" (asioita, jotka huonon tekstin lisäksi myös nerokas teksti tekee/tuntee). Ei saa kirjoittaa "Katto-logiikalla" (esim. "Teksti *ainoastaan* toistaa"), koska muuten nerokas teksti reputtaa Tason 1 ja Waterfall-moottori tuhoaa sen arvosanan nollaan.

## 3. Toteutuksen Vaiheet ja Automaattinen Työnkulku (State-Tracked Workflow)

### Phase 1: Seurannan alustus (Matrix Tracker)
* **Tehtävä:** Eristetään `seed_data.json` -tiedostosta kaikki matriisit (`category_id: "matrix"`) ja luodaan niille seurantatiedosto `epic51_matrix_tracker.md`.
* **Toteutus:** Kaikki matriisit merkitään alkutilaan `[NOK]`. Tämä tiedosto toimii koko työnkulun "Aivoina", jotta konteksti-ikkunat voidaan tyhjentää välissä tekoälyn suorituskyvyn takaamiseksi.

### Phase 2: "Raskas" Itseohjautuva Refaktorointilooppi
* **Työnkulku:** 
  1. **Uusi Konteksti:** Ihminen avaa puhtaan chatin ja sanoo "Jatka" (tai antaa tietyn matriisin ID:n, esim. `blk_440a5fef9331451b`).
  2. **Valinta:** AI lukee `epic51_matrix_tracker.md` -tiedoston ja poimii listalta seuraavan `[NOK]`-tilassa olevan matriisin.
  3. **Teorian Purku (Tiedonhaku):** AI hakee matriisin sisällön `seed_data.json` -tiedostosta. Jos matriisissa on `theory_grounding` (esim. Toulmin 2003), AI tekee aktiivisen `search_web` (Tavily AI) -haun teoriasta ja dekonstruktoi sen akateemisiin alkutekijöihinsä.
  4. **Generointi (XML & TDA):** AI rakentaa `05_llm_architecture.md` -sääntöjen mukaisen Native English XML-ohjeen (`ai_description`) ja kääntää teorian 2-5:ksi toisensa poissulkevaksi (MECE) mikrosäännöksi. Virheitä etsivät säännöt merkitään EHDOTTOMASTI `inverse_evidence: true`.
  5. **Auditointi:** AI ehdottaa säännöt ihmiselle. Kun ihminen hyväksyy (tai pyytää tarkennusta), AI tallentaa ne `seed_data.json` -tiedostoon.
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
