INSTRUCTIONS (TIER 2 EXECUTION - PYTHON BACKEND):

**STEP 1: Kartoitus ja Suunnitelma (Mapping)**
Ensimmäisenä tehtävänäsi on käyttää työkaluja (esim. kansioiden listaus) ja hahmottaa hakemiston rakenteen syvyys. Huomioi: Jos käyttäjä antaa komennossaan tarkan alipolun (esim. `backend_v2/api/routers/studio`), kartoita RAKENNE VAIN TÄSTÄ POLUSTA alaspäin, ja jätä muu projekti rauhaan. Jos alipolkua ei erikseen määritetä, kartoita koko `backend_v2`. Rakenna tämän pohjalta `task_backend.md` -tiedostoon Markdown-tarkistuslista.

SÄÄNTÖ: Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) on oma erillinen kohtansa listalla** (esim. pelkkä `backend_v2/api/routers` ei riitä, vaan listalla on oltava erikseen `backend_v2/api/routers/studio`, `backend_v2/api/routers/execution` jne.). Mitään hakemistoja ei saa niputtaa. ÄLÄ tee koodimuutoksia tässä vaiheessa. Pyydä minulta "PROCEED" kun lista on valmis.

**STEP 2: Systemaattinen Auditointi (One Subdirectory At A Time)**
Kun annan luvan edetä, aloitamme listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto.
2. Lue KAIKKI kyseisen alihakemiston .py-tiedostot.
3. Peilaa koodia TARKASTI 2026-arkkitehtuurisääntöihin:
   - **Fail-Fast & Dual-Reporting:** Onko koodissa nieltyjä virheitä (`try: ... except Exception: pass`) tai palautetaanko virhetilanteessa hiljaa `None`, `{}` tai `[]`? Puuttuuko catch-lohkoista rakenteellinen lokitus (`logger.error(..., exc_info=True)`) tai onko lokeissa kiellettyjä f-stringejä (`extra={}` sijaan)?
   - **AppException (RFC 7807):** Heitetäänkö API- tai Service-kerroksessa raakoja `HTTPException` tai `ValueError` -luokkia oman RFC 7807 -standardoidun `AppException`in sijaan?
   - **Strict Pydantic V2 DTOs (2026 SOTA):** Käyttääkö koodi V1-legacy-metodeja (.dict(), .parse_obj(), @validator, class Config:) modernien V2-metodien sijaan? Onko malleissa käytössä `model_config = ConfigDict(strict=True, frozen=True, extra='forbid')` LLM-hallusinaatioiden ja tilamutaatioiden estämiseksi? Puretaanko raaka JSON suoraan Rust-ytimessä (`model_validate_json`) hitaan `json.loads()` + `**kwargs` -purun sijaan? Onko polymorfinen data reititetty O(1) nopeudella Discriminated Unioneilla (`Field(discriminator=...)`)? Erotellaanko tyyppirajoitteet selkeästi `Annotated`-syntaksilla (PEP 593)?
   - **Anemic Routers (SSOT):** Ovatko FastAPI-reitittimet "aneemisia"? Onko reitittimiin (`api/routers/`) vuotanut suoraa tietokanta-CRUDia, RBAC-tarkistuksia tai muuta liiketoimintalogiikkaa, joka kuuluisi ehdottomasti Service-kerrokseen?
   - **Structured Concurrency (2026):** Käytetäänkö asynkronisessa rinnakkaisuudessa orpoja säikeitä jättäviä `asyncio.gather()` tai `asyncio.create_task()` -kutsuja modernin ja turvallisen `asyncio.TaskGroup()` -kontekstin sijaan?
   - **Modern Typing & DI (Python 3.14+):** Käytetäänkö FastAPI:n injektioissa vanhaa `param: Type = Depends()` -syntaksia uuden `Annotated[Type, Depends()]` -syntaksin sijaan? Onko käytössä legacy-tyyppejä (`Optional`, `Union`, `List`, `Dict`) modernien natiivityyppien (`X | None`, `list`, `dict`) sijaan? Puuttuuko ylikirjoitetuista metodeista `@override` (PEP 698)?
   - **No-Strings Mandate:** Onko backendissä kovakoodattuja UI-tekstejä (esim. suomeksi/englanniksi) dynaamisten Enum-avainten (esim. `AUTH_ORGANIC`) sijaan?
4. Raportoi löydökset kansion sisältä minulle viestillä. Jos alihakemisto on puhdas, kerro se. Pysähdy odottamaan komentoa "FIX" (jos virheitä löytyi) tai komentoa "NEXT..." (jos kansio oli puhdas).

**STEP 3: Korjaus ja Quality Loop (Remediation)**
Kun vastaan "FIX", korjaa äsken listaamasi kyseisen kansion virheet 2026-mandaatin mukaisesti. 
Käytä AINA `uv`-pakettimanageria koodin tarkistamiseen. Aja korjauksen jälkeen kohdekansioonsa terminaalissa:
`cd backend_v2 && uv run ruff format polku/kansioon && uv run ruff check polku/kansioon --fix && uv run mypy polku/kansioon --strict`
Merkitse sen jälkeen itemi `task_backend.md` listasta tehdyksi [x].
Ilmoita minulle: "Valmis. Odotan NEXT-komentoa."

**STEP 4: Kontekstin nollaus ja siirtyminen (The NEXT command)**
Kun kansion auditointi oli puhdas tai korjaukset on tehty, annan sinulle aina tällaisen komennon:

> "NEXT. Muista yhä docs/Arkkitehtuurimäärittely_ AI-orkestraattori V2.md säännöt ja docs/antigravity_prompting.md:#L133-206 UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.2 - PHASE 9 HARDENING). Pakolliset mandaatit backendille: Strict Pydantic V2 (Rust-parsing, frozen, forbid extra, Annotated), Fail-Fast sääntö (ei try-except pass), AppException (RFC 7807) & Dual-Reporting (rakenteellinen lokitus, ei f-stringejä), Aneemiset Reitittimet (SSOT Serviceihin), asyncio.TaskGroup (ei orpoja säikeitä), Annotated Dependency Injection ja PEP 695/698 tyypitykset. Lue ohjetiedostot nyt uudestaan."

Kun saat yllä olevan komennon, sinun on **EHDOTTOMASTI luettava työkalullasi (esim. bash `cat` / python) mainitut dokumentit ja niissä määritellyt rivit uudelleen** aktiiviseen muistiisi (context driftin estämiseksi). Vasta luettuasi ohjetiedostot uudelleen, siirry `task_backend.md` listan seuraavaan tekemättömään alihakemistoon ja aloita STEP 2 alusta.

Huom: Työskentelemme EHDOTTOMASTI vain yksi alihakemisto kerrallaan. Älä koskaan yritä auditoida tai korjata useampaa kansiota tai koko projektia yhdellä työkalukutsulla.