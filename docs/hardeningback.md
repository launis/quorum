INSTRUCTIONS (TIER 2 EXECUTION - PYTHON BACKEND):

Lue ensinja docs/Arkkitehtuurimäärittely_AI-orkestraattori V2.md ja docs\antigravity_prompting.md: UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.2 - PHASE 9 HARDENING & DESKTOP UI). Noudata näitä ohjeita tarkasti.

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
   - **Strict Pydantic V2 & No Naked Dicts (2026 SOTA):** 
     - **DTO Mandate:** Etsi ja poista `dict`- ja `**kwargs`-rakenteet tiedonsiirrosta kerrosten välillä. Kaikki säännönmukainen data on korvattava tyypitetyillä Pydantic V2 -malleilla. `dict` on sallittu vain apufunktioiden tuntemattomissa metadatakentissä.
     - **V1 -> V2 Migraatio:** Varmista, ettei koodissa ole V1-jäänteitä. Korvaa `.dict()` -> `.model_dump()`, `.parse_obj()` -> `.model_validate()`, `class Config:` -> `model_config = ConfigDict(...)` ja `@validator` -> `@field_validator`.
     - **Strict Pydantic & Zero Backward Compatibility:** Kaikkiin paluuarvo- ja siirtomalleihin on lisättävä `model_config = ConfigDict(strict=True, frozen=True, extra='forbid')`. Ei fallbackeja, ei taaksepäinyhteensopivuuden siltoja. Järjestelmän ainoa totuus on `seed_data.json`. Jos data muuttuu, kaadutaan Fail-Fast, jotta virhe paljastuu. Mutaatiot kielletty: jos tilaa pitää vaihtaa, käytä `.model_copy(update={...})`. Poikkeuksena: Backend-mallien (esim. `V2CoreBase`) lokaaleille Enum-kentille sallitaan joustavuussyistä `strict=False`, jotta TinyDB:stä luettavat merkkijonot kääntyvät turvallisesti Enumeiksi kaatamatta palvelinta.
     - **Rust-Parsing:** Älä käytä hidasta `json.loads(data)` -purkua. Käytä aina suoraan `Model.model_validate_json(data)` -metodia.
     - **O(1) Polymorfismi:** Union-tyyppisissä rakenteissa (`A | B`) vaadi aina Discriminated Unions -määritys (`Field(discriminator='type')`), jottei Pydantic fallbackkaa hitaaseen iterointiin.
     - **Annotated (PEP 593):** Älä sekoita oletusarvoja ja rajoitteita (esim. `id: int = Field(...)`). Erota tyyppirajoitteet puhtaasti MyPy-yhteensopivalla syntaksilla: `id: Annotated[int, Field(...)]`.
   - **Anemic Routers (SSOT):** Ovatko FastAPI-reitittimet "aneemisia"? Onko reitittimiin (`api/routers/`) vuotanut suoraa tietokanta-CRUDia, RBAC-tarkistuksia tai muuta liiketoimintalogiikkaa, joka kuuluisi ehdottomasti Service-kerrokseen?
   - **Structured Concurrency (2026):** Käytetäänkö asynkronisessa rinnakkaisuudessa orpoja säikeitä jättäviä `asyncio.gather()` tai `asyncio.create_task()` -kutsuja modernin ja turvallisen `asyncio.TaskGroup()` -kontekstin sijaan?
   - **Modern Typing & DI (Python 3.14+):** Käytetäänkö FastAPI:n injektioissa vanhaa `param: Type = Depends()` -syntaksia uuden `Annotated[Type, Depends()]` -syntaksin sijaan? Onko käytössä legacy-tyyppejä (`Optional`, `Union`, `List`, `Dict`) modernien natiivityyppien (`X | None`, `list`, `dict`) sijaan? Puuttuuko ylikirjoitetuista metodeista `@override` (PEP 698)?
   - **No-Strings Mandate:** Onko backendissä kovakoodattuja UI-tekstejä (esim. suomeksi/englanniksi) dynaamisten Enum-avainten (esim. `AUTH_ORGANIC`) sijaan?
4. Raportoi löydökset kansion sisältä minulle viestillä. Jos alihakemisto on puhdas, kerro se. Pysähdy odottamaan komentoa "FIX" (jos virheitä löytyi) tai komentoa "NEXT..." (jos kansio oli puhdas).

**STEP 3: Korjaus ja Quality Loop (Remediation)**
# 🛑 EHDOTON TOIMINTAOHJE: KORJAUSVAIHE (STEP 3 - REMEDIATION) 🛑

Tämä on kriittinen suoritusprotokolla. Kun annan komennon **"FIX"**, sinun on välittömästi korjattava listaamasi kansion virheet 2026-mandaatin tiukkojen sääntöjen mukaisesti. Sinun on noudatettava alla olevia rajoitteita poikkeuksetta:

### 1. KIELTO: OMATOIMINEN KOMENTOJEN AJO (OS-SANDBOX RAJOITE)
**ÄLÄ KOSKAAN** yritä ajaa `uv`-pakettimanagerin komentoja itse `run_command`-työkalulla tai muilla vastaavilla työkaluilla. (Syy: sandboxing is not supported on Windows). 

### 2. TARKKA KOODIBLOKKI (EI VILLEJÄ KORTTEJA)
Sinun tehtäväsi on tuottaa minulle tarkka, kopioitava Markdown-koodibloki komentoja varten. 
* **EHDOTON SÄÄNTÖ:** Villien korttien (kuten `*.py`) käyttö on ankarasti kielletty.
* Kirjoita jokainen tiedostopolku eksplisiittisesti ja täydellisesti.

**Vaadittu formaatti:**
```bash
uv run ruff check backend_v2/polku/kansioon/tarkka_tiedosto.py --fix ; uv run mypy backend_v2/polku/kansioon/tarkka_tiedosto.py --strict
3. TEHTÄVÄN SEURANTA (task_backend.md)
Kun olet antanut korjatut koodit ja yllä olevan tarkistuskomennon minulle kopioitavaksi, sinun on päivitettävä virtuaalinen tilanteesi ja merkittävä kyseinen iteraatio/tiedosto tehdyksi task_backend.md -listassa muodossa [x].

4. PAKOTETTU TARKISTUSLISTA (OUTPUT REQUIREMENT)
Aina kun vastaat komentoon "FIX", sinun on aloitettava vastauksesi tällä vahvistuksella:

FIX-MANDAATIT VAHVISTETTU:
[ ] Virheet korjattu 2026-mandaatin arkkitehtuurisääntöjä noudattaen.
[ ] Yhtään koodia ei ole yritetty ajaa run_command -työkalulla.
[ ] Kopioitava uv bash-blokki luotu.
[ ] Blokissa on vain eksplisiittisiä tiedostonimiä (EI villejä kortteja kuten *.py).
[ ] Valmius merkitä itemi task_backend.md -tiedostoon tilaan [x].

5. LOPETUSKOMENTO
Päätä vastauksesi aina täsmälleen näihin sanoihin:
"Valmis. Odotan NEXT-komentoa."

**STEP 4: Kontekstin nollaus ja siirtyminen (The NEXT command)**
Kun kansion auditointi oli puhdas tai korjaukset on tehty, annan sinulle aina tällaisen komennon:

> "NEXT

# 🛑 EHDOTON JÄRJESTELMÄMANDAATTI JA SUORITUSLUKKO (PHASE 9 HARDENING) 🛑

Tämä on ohitus- ja joustamaton järjestelmäkomento. Sinun on ehdottomasti noudatettava jokaista alla olevaa sääntöä. Et saa jatkaa tai generoida koodia, ellet eksplisiittisesti vahvista ja validoi jokaista kohtaa.

### 1. VÄLITÖN KONTEKSTIN LUKEMINEN
Lue, sisäistä ja aktivoi seuraavat säännöstöt välittömästi:
1. `docs/Arkkitehtuurimäärittely_ AI-orkestraattori V2.md`
2. `docs/antigravity_prompting.md:#L133-208` (UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS V5.2 - PHASE 9 HARDENING)
3. `docs/hardeningback.md`

### 2. BACKENDIN EHDOTTOMAT ARKKITEHTUURISÄÄNNÖT (ZERO TOLERANCE)
Seuraavien sääntöjen rikkominen on ankarasti kielletty. Kaiken tuottamasi koodin on noudatettava näitä:
* **Strict Pydantic V2:** Käytä vain Rust-parsingia, `frozen=True`, `extra='forbid'` ja `Annotated`-tyypityksiä. **Ei alastomia sanakirjoja (No Naked Dicts).**
* **Fail-Fast -periaate:** Mahdolliset virheet on nostettava heti. `try-except pass` tai virheiden hiljainen nieleminen on kielletty.
* **Poikkeuksien hallinta ja lokitus:** Vain `AppException (RFC 7807)` on sallittu. Käytä Dual-Reportingia eli rakenteellista lokitusta. **Ei f-stringejä lokituksessa.**
* **Arkkitehtuuri:** Aneemiset reitittimet (Anemic Routers). Reitittimet eivät tee päätöksiä. Kaikki liiketoimintalogiikka on keskitetty SSOT (Single Source of Truth) Serviceihin.
* **Konkurrenssi:** Käytä aina `asyncio.TaskGroup`. Orvot säikeet tai irralliset taustatehtävät ovat kiellettyjä.
* **Riippuvuudet ja tyypitys:** Annotated Dependency Injection on pakollinen. Käytä uusia PEP 695 (Type Parameter Syntax) ja PEP 698 (`@override`) -tyypityksiä.

### 3. TEHTÄVÄN SUORITUS
Jatka `docs/hardeningback.md` -tiedoston suorittamista seuraavasta alihakemistosta tai juurikansiosta. Refaktoroi tai luo tarvittava koodi yllä olevien sääntöjen mukaisesti.

### 4. PAKOTETTU TARKISTUSLISTA (OUTPUT REQUIREMENT)
**ENNEN KUIN TULOSTAT RIVIÄKÄÄN KOODIA**, sinun on tulostettava alla oleva tarkistuslista osana vastaustasi ja merkittävä JOKAINEN kohta suoritetuksi rastilla [X]. Jos et pysty laittamaan ruksia johonkin kohtaan, sinun on hylättävä oma koodisi ja korjattava se, kunnes vaatimus täyttyy.

Tulosta tämä vastaustesi alkuun:
> **VAHVISTETUT MANDAATIT:**
> [ ] Asiakirjat (Arkkitehtuuri V2, antigravity L133-208, hardeningback.md) luettu ja sisäistetty.
> [ ] Strict Pydantic V2 (Rust, frozen, forbid extra, Annotated, No Naked Dicts) toteutettu.
> [ ] Järjestelmän SSoT pariteetti `seed_data.json` huomioitu (Zero Backward Compatibility).
> [ ] Fail-Fast -sääntö aktiivinen (ei try-except pass, ei default-fallbackeja).
> [ ] AppException (RFC 7807) heitetään ja lokitetaan ennen `raise` kutsua.
Kun saat yllä olevan komennon, sinun on **EHDOTTOMASTI luettava työkalullasi (esim. bash `cat` / python) mainitut dokumentit ja niissä määritellyt rivit uudelleen** aktiiviseen muistiisi (context driftin estämiseksi). Vasta luettuasi ohjetiedostot uudelleen, siirry `task_backend.md` listan seuraavaan tekemättömään alihakemistoon ja aloita STEP 2 alusta.

Huom: Työskentelemme EHDOTTOMASTI vain yksi alihakemisto kerrallaan. Älä koskaan yritä auditoida tai korjata useampaa kansiota tai koko projektia yhdellä työkalukutsulla.