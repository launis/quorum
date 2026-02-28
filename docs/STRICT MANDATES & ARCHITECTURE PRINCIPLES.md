# STRICT MANDATES & ARCHITECTURE PRINCIPLES (BACKEND)

Tämä dokumentti määrittelee Cognitive Quorum -järjestelmän palvelinpään (Backend) ja arkkitehtuurin ehdottomat säännöt. Näistä säännöistä ei jousteta missään tilanteessa.

## 1. THE ZERO-COMPROMISE PLEDGE (Quality Standard)
- **Laadusta ei jousteta:** Ei "quick hackeja", ei teknistä velkaa, ei defensiivistä koodausta.
- **Fail-Fast Boundary:** Ydinlogiikassa (Core Engine, Database, Domain) järjestelmän ON KAADUTTAVA VÄLITTÖMÄSTI virheellisen tilan tai puuttuvan datan kohdalla. `try-except pass` ja hiljainen tyhjän (`None`, `[]` tai `{}`) palauttaminen dataa odotettaessa ovat EHDOTTOMASTI KIELLETTYJÄ, koska ne piilottavat upstream-virheet.
- **Juussyiden korjaaminen (Root Cause Mandate):** Oireita ei paikata pintapuolisesti (esim. `if x is None: return` tai `.get('field', default)`), vaan virheellisen datan alkulähde etsitään ja korjataan.
- **Strict Typing & No Defaults:** Domain-malleissa ei saa olla implisiittisiä oletusarvoja pakollisille kentille (esim. `score: float = 0.0` on sallittu vain jos se on loogisesti oikea oletus).
- **Python Authority (Determinism):** Deterministinen logiikka (matematiikka, lajittelu, deduplikointi, ID:n luonti) tehdään aina Pythonissa (`BaseAgent.post_process()`). Tekoälylle ei delegoida järjestelmäkriittistä determinististä logiikkaa.

## 2. DOCUMENTATION & HYGIENE
- **English Only -sääntö (Koodi):** Koko koodipohja (muuttujat, funktiot, luokat, docstringit ja kommentit) on yksinomaan englanniksi. Suomenkieliset termit koodissa on siivottu paikalleen ainoastaan lokalisaatiotiedostoihin (`app_fi.arb`, `fi.json`).
- **Tyyppivihjeet:** Täydellinen `mypy --strict` -tason tyypitys Pythonissa. Kaikki tietorakenteet on tyypitetty tarkasti.
- **Docstringit (Imperative Mood):** Kaikilla julkisilla funktioilla, luokilla ja moduuleilla on selkeät docstringit (Google-style Pythonissa), kirjoitettu imperatiivissa (esim. "Calculate risk score").
- **Koodikommentit (The "Why" Mandate):** Sisäiset kommentit saavat kertoa vain "miksi" (liiketoimintalogiikka, erikoistapaukset) jotain tehdään, ei selittää koodin mekaanista "mitä" tekoa.

## 3. DATAN EHEYS JA KESKITETYT LIIKETOIMINTASÄÄNNÖT (Relational Integrity)
- **Service-kerros portinvartijana:** Liiketoiminta- ja eheyssääntöjä ei ole sijoitettu HTTP API -reitittimiin, vaan keskitettyyn Service-kerrokseen. Repository tekee vain raa'an tallennuksen, ja Service-kerros tarkistaa relaatiot.
- **Kriittiset eheyssäännöt:**
  - Järjestelmässä ei saa olla "orpoja" käyttäjiä tai dataa.
  - Vahva poistosuoja (esim. `root`-käyttäjää tai järjestelmän elintärkeitä ydinasetuksia ei saa voida poistaa mistään kautta).
  - Vahva relaatiosuoja: Komponentteja tai Steppejä, jotka ovat käytössä (Workfloweissa tms.), ei voi poistaa. Service-kerros nostaa `AppException`in jos sääntöä rikotaan.

## 4. PYTHON BACKEND MANDATES & SISÄINEN CRUD API (SSOT)
- **Database SSOT & Seed Data:** `backend/seed/seed_data.json` toimii Single Source of Truthinä (SSOT) alkuperäiselle konfiguraatiolle, steppeille ja workfloweille. Konfiguraatioita ei kovakoodata Python-luokkiin.
- **Sisäinen CRUD API (Service & Repository):** Järjestelmän ytimessä on vahva Service- ja Repository-kerros, joka on AINOA paikka, josta otetaan yhteys tietokanta-ajureihin. Ulkoinen HTTP API, asynkroniset Workerit ja Agentit käyttävät yksinomaan näitä Service/Repository CRUD -metodeja.
- **Pydantic V2 (No-ORM):** Ainoa totuuden lähde datalle API-rajoilla ja logiikassa. Kaikki datansiirto käyttää tiukkoja Pydantic-malleja (`ConfigDict(strict=True, extra="ignore")`). Säännöttömien `dict`-objektien siirtely ydinlogiikassa on kielletty.
- **Dependency Injection (DI):** Riippuvuudet välitetään `Annotated[Type, Depends()]` -syntaksilla FastAPI-rajapinnoissa ja kytketyissä palveluissa.

## 5. ERROR HANDLING CONTRACT (RFC 7807 & Fail Fast)
- **Strukturoitu AppException:** Kaikki liiketoiminta- ja data-auktorisoinnin virheet on kääritty keskitettyyn `AppException`-malliin, johon liittyy yksiselitteinen `ErrorCodes`-enum. Ei paljaita `ValueError` poikkeuksia ydinviestinnässä.
- **Dual-Reporting & Boilerplate:** Exception-kiinniotossa noudatetaan sääntöä: Ota kiinni -> Logita strukturoidusti (`logger.error(exc_info=True)`) -> Nosta explicit `AppException`.
- **RFC 7807 Problem Details:** Backendin globaali Exception Handler palauttaa kaikki virheet standardoidussa RFC 7807 -muodossa. 
- **Actionable Hints (Frontend):** Backend ei palauta lokalisoituja virheviestejä (`"Tapahtui virhe"`), vaan se palauttaa vain `ErrorCodes`-vakioita, jotka Frontend kääntää käyttäjälle ymmärrettäviksi `.arb`-käännöstiedostojen avulla.

## 6. INTERNATIONALIZATION (I18N) STANDARDS
- **The "No-String" API Policy:** Backend toimittaa DATAA (avaimia, Enumeita, koodeja, tiloja). Front-end toimittaa ESITYKSEN (käännökset). Backend ei koskaan palauta hardkodattuja lokalisoituja UI-merkkijonoja API:n yli (Poikkeuksena LLM:n natiivisti generoima dynaaminen vapaa teksti).
- **Backend I18N Rajoitus:** Backendin omaa lokalisointia (`backend/l10n/`) käytetään VAIN palvelinpään renderöintiin (esim. luotaessa PDF-dokumentteja dynaamisesti).

## 7. SERVER-DRIVEN UI (SDUI) & "DUMB" FRONTEND
- **SDUI & BFF Resilience:** Frontend delegointi on pidetty kevyenä. Backend Backend-for-Frontend (BFF) -muuntajat (esim. `domain/profiling.py`, `domain/logic.py`) kokoavat ja mappaavat laajat Domain-mallit tarkoiksi, tyyppiturvallisiksi View-malleiksi (esim. `DriverProfileDisplay`).
- **UI Graceful Degradation:** Jos komponentin data on viallista, se hylätään mieluummin rakenteellisesti (Fail Fast Backendissä) tai pehmennetään paikalliseen "Error Componenttiin" Frontendissä. UI ei kaada koko näkymää yhden widgetin virheeseen.