# CONTEXT & ROLE
Olet kokenut ohjelmistoarkkitehti ja senior-tason ohjelmistokehittäjä (Staff Engineer). Tehtävänäsi on laatia minulle erittäin yksityiskohtainen ja hienojakoinen, askeleittainen refaktorointisuunnitelma (Execution Plan) laajan FastAPI/Python- ja Flutter/Dart-projektin uudistamiseksi.

Tavoitteena on muuttaa koodi suoraviivaiseksi, ylläpidettäväksi ja testattavaksi "best practice" -ohjelmistoksi, joka rakentuu ehdottoman Single Source of Truth (SSOT) -arkkitehtuurin varaan.

ÄLÄ ALOITA KOODIN MUOKKAAMISTA VIELÄ. Luo minulle ensin ainoastaan tämä tiekartoitus.

---

# STRICT MANDATES & ARCHITECTURE PRINCIPLES
Koko suunnitelman ja kaiken tulevan koodauksen on noudatettava täydellisesti projektin ohjeistoa (`docs/flutterpromptohje.md`), erityisesti seuraavia ydinsääntöjä. Nämä mandaatit on otettava huomioon ja niihin on viitattava toimintaperiaatteina läpi koko suunnitelman:

### 1. PART 18: THE ZERO-COMPROMISE PLEDGE (Quality Standard)
- **Laadusta ei jousteta:** Ei "quick hackeja", ei teknistä velkaa, ei defensiivistä koodausta.
- **Fail-Fast Boundary:** Ydinlogiikassa (Core Engine, Database, Domain) järjestelmän ON KAADUTTAVA VÄLITTÖMÄSTI virheellisen tilan tai puuttuvan datan kohdalla. `try-except pass` ja hiljainen tyhjän (`None`, `[]` tai `{}`) palauttaminen dataa odotettaessa ovat EHDOTTOMASTI KIELLETTYJÄ, koska ne piilottavat upstream-virheet.
- **Juussyiden korjaaminen (Root Cause Mandate):** Oireita ei paikata pintapuolisesti (esim. `if x is None: return` tai `.get('field', default)`), vaan virheellisen datan alkulähde etsitään ja korjataan.
- **Strict Typing & No Defaults:** Domain-malleissa ei saa olla implisiittisiä oletusarvoja pakollisille kentille (esim. `score: float = 0.0` on kielletty).
- **Python Authority (Determinism):** Deterministinen logiikka (matematiikka, lajittelu, deduplikointi, ID:n luonti) tehdään aina Pythonissa (`BaseAgent.post_process()`). Tekoälyyn ei luoteta näissä asioissa.

### 2. PART 17: DOCUMENTATION & HYGIENE (Strict Mandate)
- **ENGLISH ONLY -SÄÄNTÖ:** Kaikki koodi, muuttujien nimet, funktioiden nimet, luokat ja lähdekoodin sisäiset kommentit/docstringit ON KIRJOITETTAVA YKSINOMAAN ENGLANNIKSI. Suomenkieliset termit koodissa on siivottava käännöksellä. (Poikkeuksena vain lokalisaatiotiedostot `app_fi.arb` ja `fi.json`).
- **Hygienia:** Kaikki kuollut koodi, turhat printit ja orvot `TODO`:t (ilman vastuuhenkilöä/päivämäärää) on poistettava refaktoroinnin yhteydessä. Jokainen poisto pitää erikseen perustella ja minulta vahvistaa.
- **Tyyppivihjeet:** Täydellinen `mypy --strict` -tason tyypitys Pythonissa ja tiukka tyypitys Dartissa. Ei `Any` tai `dynamic` -tyyppejä.
- **Docstringit (Imperative Mood):** Kaikilla julkisilla funktioilla, luokilla ja moduuleilla on oltava selkeät docstringit (Google-style Pythonissa, kolmoisslash `///` Dartissa), jotka on kirjoitettu imperatiivissa (esim. "Calculate risk score", ei "Calculates...").
- **Koodikommentit (The "Why" Mandate):** Sisäiset kommentit saavat kertoa vain "miksi" (liiketoimintalogiikka, erikoistapaukset) jotain tehdään, ei "mitä" tehdään.

### 3. DATAN EHEYS JA KESKITETYT LIIKETOIMINTASÄÄNNÖT (Relational Integrity)
- **Ongelma:** Nyt liiketoiminta- ja eheyssäännöt (esim. voiko jonkin poistaa) on ripoteltu HTTP API -reitittimiin (`api/routes/`). Tämä on väärin, koska kantaa voidaan muokata myös Workereiden ja skriptien kautta.
- **Ratkaisu (Keskitetty mekanismi):** Sinun on suunniteltava Service-kerros, joka toimii portinvartijana kaikille CRUD-operaatioille. Repository tekee vain raa'an tallennuksen, mutta **Service-kerros** tarkistaa relaatiot ja liiketoimintasäännöt.
- **Kriittiset säännöt, jotka Service-kerroksen on taattava:**
  - Järjestelmässä ei saa olla "orpoja" käyttäjiä tai dataa.
  - Vahva poistosuoja (Root-suoja): `root`-käyttäjää tai järjestelmän elintärkeitä ydinasetuksia ei saa voida poistaa mistään kautta.
  - Vahva relaatiosuoja: **Komponentteja**, jotka ovat käytössä Stepeissä, EI saa poistaa. **Steppejä**, jotka ovat käytössä Workfloweissa, EI saa poistaa. Service-kerroksen on validoitava nämä riippuvuudet ennen poistoa ja nostettava esim. `ConflictError`.

### 4. PART 2: PYTHON BACKEND MANDATES & SISÄINEN CRUD API (SSOT)
- **Database SSOT & Seed Data:** `backend/seed/seed_data.json` is the Single Source of Truth for models, config, and workflows. Do not hardcode configurations in Python classes.
- **Repository on SSOT:** Järjestelmän ytimeen rakennetaan vahva Service- ja Repository-kerros. Tämä on ohjelmiston "Sisäinen CRUD API" ja AINOA paikka, josta otetaan yhteys tietokanta-ajureihin (Firestore/TinyDB).
- **Yksi yhteinen rajapinta kaikille:** Ulkoinen HTTP API (FastAPI-reitittimet), asynkroniset Workerit (`worker.py`, `engine.py`), Agenttien Hookit (`hooks/`) ja siemennysskriptit (`seed/run_seed.py`) **EIVÄT SAA** tehdä suoria tietokanta-ajurikutsuja. Ne kaikki käyttävät täsmälleen samaa Sisäistä CRUD APIa.
- **Puuttuvien rajapintojen sääntö:** Jos jokin sisäinen prosessi tarvitsee kantaoperaatiota, jota ei vielä ole, sitä ei koskaan kovakoodata lokaaliksi erikoiskyselyksi. Puuttuva ominaisuus toteutetaan ensin standardina CRUD-metodina Repository/Service-kerrokseen.
- **Pydantic V2 (No-ORM):** Ainoa totuuden lähde datalle. Kaikki sisäinen datansiirto (Services, Hooks, Agents) pakotetaan tiukkojen Pydantic-mallien läpi (`ConfigDict(strict=True)`). Ei perinteisiä ORM-kirjastoja. `dict`-objektien siirtely ydinlogiikassa on kielletty.
- **Dependency Injection (DI):** Riippuvuudet ruiskutetaan aina modernilla `Annotated[Type, Depends()]` -syntaksilla.

### 5. PART 3: ERROR HANDLING CONTRACT (RFC 7807 & Fail Fast)
- **The Zero-Laziness Mandate:** Kaikki vanhat paljaat `ValueError`, `raise Exception` tai karsitut `HTTPExceptionit` on pakko korvata strukturoidulla `AppException`-mallilla.
- **Standardisoitu AppException:** Kaikki virheet on käärittävä projektin omaan `AppException`-luokkaan (tai sen semanttisiin perillisiin), joilla on yksiselitteinen `ErrorCodes`-enum.
- **Dual-Reporting & Boilerplate:** Poikkeusten kiinniotossa noudatetaan sääntöä: 1. Tarkista data-eheys, 2. Yritä (try), 3. Ota kiinni (except), 4. Logita strukturoidusti (`logger.error(..., exc_info=True)`), 5. Nosta explicit AppException (`raise ... from e`). Pelkkä `raise e` on kielletty.
- **Keskitetty virheenkäsittely:** Backendissä on YKSI globaali Exception Handler, joka palauttaa virheet standardoidussa RFC 7807 (Problem Details) -muodossa. Ripotellut `try/exceptit` poistetaan liiketoimintalogiikasta ja annetaan virheiden nousta ylös asti.
- **Actionable Hints (Frontend):** Frontend nappaa virheet `ErrorInterceptorissa` ja kääntää virhekoodit käyttäjälle merkityksellisiksi ohjeiksi `.arb`-tiedostojen kautta. Älä näytä teknisiä serverivirheitä loppukäyttäjälle.

### 6. PART 10: INTERNATIONALIZATION (I18N) STANDARDS
- **The "No-String" API Policy:** Backend toimittaa DATAA (avaimia, Enumeita, koodeja). Frontend toimittaa ESITYKSEN (käännökset `.arb`-tiedostoista). Backend **EI KOSKAAN** palauta lokalisoituja UI-merkkijonoja API:n yli (Poikkeuksena LLM:n natiivisti generoima dynaaminen vapaa teksti).
- **Backend I18N Rajoitus:** Backendin lokalisointipalvelua (`backend/l10n/`) saa käyttää AINOASTAAN palvelinpään renderöintiin (Server-Side Rendering, esim. PDF-dokumenttien luontiin).
- **Dual Sovereign Locations:** Frontendin käännökset ovat `.arb`-tiedostoissa, Backendin `.json`-tiedostoissa. Kieli tunnistetaan `Accept-Language` -otsakkeesta ContextVarin avulla, sitä ei välitetä muuttujana.
- **ICU Formatting & No Hacks:** Merkkijonojen yhdistely koodissa (esim. `"Welcome " + name`) ja manuaaliset if/else-monikot (esim. `if count == 1`) ovat EHDOTTOMASTI KIELLETTYJÄ. Kaikki muuttujat ja monikot käsitellään pelkästään `.arb`-tiedoston ICU-syntaksilla. Backend lähettää muuttujat vain raakana JSON-datana.
- **Semantic Markup (Markdown):** Käyttöliittymän muotoiluja (esim. `<b>`, `TextStyle`) ei leivota Dart-koodiin osittaisten käännösten ympärille. Käännöksissä käytetään kevyttä Markdownia (esim. `"pressButton": "Paina **Tallenna**-nappia"`).
- **Keys Are Sacred (Studio & Builder Safety):** Dynaamisissa työkaluissa (esim. Cognitive Studio) käyttäjä saa muokata vain Arvoja. Järjestelmäavaimia (Translation Keys, esim. `history_text`) EI SAA koskaan kääntää tai muuttaa käyttöliittymän kautta.

### 7. LISÄVAATIMUKSET: DRY AI-AGENTS & "DUMB" FRONTEND (SDUI)
- **Agenttien abstraktio:** Agenttien toistuva logiikka (LLM API-kutsut, parsinta) siirretään yhteiseen abstraktiin `BaseAgent`-luokkaan.
- **Frontendin SSOT:** Flutter-malleja tai API-clientia EI koodata käsin. Ne generoidaan suoraan backendin OpenAPI-skeemasta.
- **Server-Driven UI (SDUI) & BFF Resilience:** Frontend on tyhmä ja ainoastaan renderöi backendin lähettämän JSON-tilan. Ainoastaan BFF-kerros (Backend-for-Frontend) saa tehdä "Graceful Degradation" -komposiittipudotuksia UI-kaatumisten estämiseksi.

---

# EXECUTION PLAN REQUIREMENTS (Suunnitelman rakenne)

Analysoi ohjelmisto ja laadi koko refaktoroinnista erittäin yksityiskohtainen ja hienojakoinen Master Plan. Jaa koko ohjelmiston läpikäynti todella pieniin, **yksittäisinä ajoina (single run) suoritettaviin askeliin** (esim. Step 1.1, Step 1.2, Step 2.1...). Käsittele ne kohdat, missä suunnitellaan koodin poistoa huolellisesti ja pyydä minulta erikseen lupa ennen kuin poistat mitään.

Etene arkkitehtuurin pohjalta kohti käyttöliittymää seuraavan tiekartan mukaisesti:

**Vaihe 1: Turvaverkko, Kieli, Pydantic-mallit ja Virheenkäsittely (Part 3, 17, 18)**
- Lintereiden puhtaus, "English Only" -koodisäännön varmistus & dead coden poisto.
- Pydantic DTO -mallien putsaus (Edge Validation, no dicts, no implicit defaults).
- Keskitetyn RFC 7807 -virheenkäsittelyn (AppException) ja strukturoidun logituksen (Dual-Reporting) käyttöönotto. Paljaiden poikkeuksien refaktorointi.

**Vaihe 2: Sisäinen CRUD API & Kanta-abstraktio (Part 2)**
- Kanta-ajurien (Firestore/TinyDB) täysi kapselointi Repository-luokkiin.
- Modernin Dependency Injectionin (`Annotated[Type, Depends()]`) käyttöönotto.

**Vaihe 3: Keskitetty Datan Eheys ja Relaatiotarkistukset (Domain Constraints & Integrity)**
- Suunnittele ja toteuta mekanismi (ehdota tätä suunnitelmassasi), jolla estetään luvattomat poistot ja orvot tietueet (root-käyttäjä, aktiiviset komponentit, stepit ja workflowt) SERVICE-kerroksessa.
- Siirretään nämä tarkistukset API-reitittimistä tähän keskitettyyn mekanismiin (Fail-Fast).

**Vaihe 4: Sisäisten asiakkaiden kytkentä (Zero-Compromise, Part 18)**
- `worker.py` ja `engine.py` siirretään käyttämään yksinomaan Repository/Service-kerrosta (suorat ajurikutsut pois, Fail-Fast).
- Agenttien `hooks/` refaktoroidaan käyttämään CRUD APIa.
- `seed/run_seed.py` muutetaan käyttämään Service/Repository -kerroksen CRUD-metodeja (Pydantic-validoinnilla ja constraint-tarkistuksilla).

**Vaihe 5: Ulkoinen API, Agentit ja I18N (Clean Architecture, Part 10, 18)**
- Kaikki tietokanta- ja liiketoimintalogiikka (MUKAAN LUKIEN EHEYSTARKISTUKSET) poistetaan FastAPI-reitittimistä (`api/routes/`). Reitittimet ohjaavat pyynnöt vain Service-kerrokseen.
- Varmistetaan **No-String Policy**: Reitittimet palauttavat UI-tekstien sijaan vain Enumeita ja avaimia (Part 10).
- `BaseAgent`-abstraktion luominen ja agenttien siivous (Python Authority -säännön varmistaminen).

**Vaihe 6: Frontend SSOT, I18N ja SDUI (Part 10, 17)**
- Manuaalisten Dart DTO -mallien poisto ja OpenAPI -> Dart -generoinnin täysi käyttöönotto.
- Frontendin Error Interceptorin kytkentä ja Actionable Hinttien luonti `.arb`-tiedostoihin.
- UI-lokalisaation täysi korjaus: Dart-koodin kieli englanniksi, ICU-monikot/muuttujat kuntoon, Markdown-käännökset käyttöön ja Dartin `switch`-lausekkeiden rakentaminen Backendiltä tuleville Enum-avaimille (Part 10). Varmistetaan myös "Keys Are Sacred" -sääntö.

Jokaisen askeleen on oltava riittävän eristetty, jotta se voidaan suorittaa ja testata rikkomatta koko järjestelmää kerralla.

**Jokaisesta askeleesta on ilmettävä selkeästi:**
1. **Askeleen tunniste ja nimi** (esim. "Step 6.2: Frontendin ICU-lokalisoinnin ja Enum-käsittelyn korjaus").
2. **Kohdetiedostot:** Mitä tiedostoja, kansioita ja luokkia tässä askeleessa tarkalleen käsitellään.
3. **Tavoitteet ja toimenpiteet (Mitä, Miksi & Mandates):** Mitä konkreettisesti muutetaan. Miten ehdotettu ratkaisu toimii. **PERUSTELE AINA** viittaamalla ohjeiston Mandaatteihin. (Esim. *"Poistetaan Dart-koodista if/else-monikot ja korvataan ICU-formatoinnilla .arb-tiedostoihin. Tämä toteuttaa Part 10: Interpolation Security & Pluralization -säännön. Kaikki Dartin funktioiden nimet ja kommentit muutetaan englanniksi (Part 17)."*).
4. **Testit ja varmennus:** Miten varmistamme terminaalissa VÄLITTÖMÄSTI askeleen suorituksen jälkeen, että muutos onnistui ja ohjelmisto toimii. Määrittele tarkat komennot (esim. linter-ajot `ruff check .` & `mypy --strict`, tietyt `pytest`-komennot, `dart run build_runner build`, `dart run custom_lint` tai seed-skriptin turvallinen testiajo). Ennen kuin siirrät logiikkaa reitittimistä Service-kerrokseen, varmista että kyseiselle CRUD-operaatiolle on olemassa yksikkötesti (pytest) (backend/tests/), tai kirjoita testi ensin (Test-Driven Development)

Luo nyt tämä vaiheistettu Master Plan. Odotan, että suunnittelet arkkitehtuurin ja erittelyt huolella. Kun olet valmis, jää odottamaan, että annan sinulle erillisen käskyn aloittaa "Step 1.1:n" suorittamisen. Älä koodaa tai muokkaa tiedostoja vielä.