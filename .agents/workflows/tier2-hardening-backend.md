---
description: Tier 2 (Backend Hardening) - Step-by-step auditing loop for Python backend directories against Phase 9 standards.
---

### 🟢 TIER 2: PYTHON BACKEND HARDENING LOOP

Lue ensin uusi Antigravity-säännöstö `.agents/rules/01-python-backend.md` ja `.agents/rules/00-antigravity-core.md`: UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.2 - PHASE 9 HARDENING). Noudata näitä ohjeita ehdottomasti.

**STEP 1: Kartoitus ja Suunnitelma (Mapping)**
Ensimmäisenä tehtävänäsi on käyttää työkaluja (esim. kansioiden listaus) ja hahmottaa hakemiston rakenteen syvyys.
* Jos käyttäjä antaa komennossaan tarkan alipolun (esim. `backend_v2/api/routers/studio`), kartoita RAKENNE VAIN TÄSTÄ POLUSTA alaspäin. Jos alipolkua ei erikseen määritetä, kartoita koko `backend_v2`.
* **EHDOTON KIELTO (Sivuutettavat tiedostot):** Sivuuta analyysissä täysin `__pycache__` -kansiot, virtuaaliympäristöt (`venv`, `.venv`), alembic-migraatioiden versiotiedostot (`alembic/versions`) ja täysin tyhjät `__init__.py` -tiedostot. Älä lue, auditoi tai yritä muokata niitä säästääksesi resursseja ja kontekstia.
* **SÄÄNTÖ:** Rakenna havainnoistasi chattiin tulostettava virtuaalinen Markdown-tarkistuslista (`task_backend.md`). Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) on oma erillinen kohtansa listalla** (esim. pelkkä `backend_v2/api/routers` ei riitä, vaan listalla on oltava erikseen `backend_v2/api/routers/studio` jne.). Hakemistoja ei saa niputtaa.
* **KIELTO:** ÄLÄ tee koodimuutoksia tässä vaiheessa. Päätä vastauksesi aina sanoihin: *"Lista valmis. Odotan PROCEED-komentoa."*

**STEP 2: Systemaattinen Auditointi (One Subdirectory At A Time)**
Kun annan luvan edetä ("PROCEED"), aloitamme virtuaalisen listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto.
2. Lue KAIKKI kyseisen alihakemiston `.py`-tiedostot (huomioiden sivuutettavat kansiot).
3. Peilaa koodia TARKASTI 2026-arkkitehtuurisääntöihin:
   - **Fail-Fast & Dual-Reporting:** Onko koodissa nieltyjä virheitä (`try: ... except Exception: pass`) tai palautetaanko virhetilanteessa hiljaa `None`, `{}` tai `[]`? Puuttuuko catch-lohkoista rakenteellinen lokitus (`logger.error(..., exc_info=True)`) tai onko lokeissa kiellettyjä f-stringejä (`extra={}` sijaan)?
   - **AppException (RFC 7807):** Heitetäänkö API- tai Service-kerroksessa raakoja `HTTPException` tai `ValueError` -luokkia oman RFC 7807 -standardoidun `AppException`in sijaan?
   - **Strict Pydantic V2 & No Naked Dicts (2026 SOTA):** 
     - **DTO Mandate:** Etsi ja poista `dict`- ja `**kwargs`-rakenteet tiedonsiirrosta kerrosten välillä. Kaikki säännönmukainen data on korvattava tyypitetyillä Pydantic V2 -malleilla. `dict` on sallittu vain apufunktioiden tuntemattomissa metadatakentissä.
     - **V1 -> V2 Migraatio:** Varmista, ettei koodissa ole V1-jäänteitä. Korvaa `.dict()` -> `.model_dump()`, `.parse_obj()` -> `.model_validate()`, `class Config:` -> `model_config = ConfigDict(...)` ja `@validator` -> `@field_validator`.
     - **Strict Pydantic & Zero Backward Compatibility:** Kaikkiin paluuarvo- ja siirtomalleihin on lisättävä `model_config = ConfigDict(strict=True, frozen=True, extra='forbid')`. Ei fallbackeja. Mutaatiot kielletty: jos tilaa pitää vaihtaa, käytä `.model_copy(update={...})`. Poikkeus: Backend-mallien (esim. `V2CoreBase`) lokaaleille Enum-kentille sallitaan `strict=False` tietokannasta luvun turvaamiseksi.
     - **Rust-Parsing:** Käytä aina suoraan `Model.model_validate_json(data)` -metodia, älä hidasta `json.loads(data)` -purkua.
     - **O(1) Polymorfismi:** Union-rakenteissa (`A | B`) vaadi aina Discriminated Unions -määritys (`Field(discriminator='type')`).
     - **Annotated (PEP 593):** Erota tyyppirajoitteet: `id: Annotated[int, Field(...)]`.
   - **Anemic Routers (SSOT):** Ovatko FastAPI-reitittimet "aneemisia"? Onko reitittimiin (`api/routers/`) vuotanut suoraa tietokanta-CRUDia, RBAC-tarkistuksia tai muuta liiketoimintalogiikkaa, joka kuuluisi ehdottomasti Service-kerrokseen?
   - **Structured Concurrency (2026):** Käytetäänkö asynkronisessa rinnakkaisuudessa orpoja säikeitä jättäviä `asyncio.gather()` tai `asyncio.create_task()` -kutsuja modernin ja turvallisen `asyncio.TaskGroup()` -kontekstin sijaan?
   - **Modern Typing & DI (Python 3.14+):** Käytetäänkö FastAPI:n injektioissa uutta `Annotated[Type, Depends()]` -syntaksia? Onko käytössä legacy-tyyppejä (`Optional`, `Union`, `List`, `Dict`) modernien natiivityyppien sijaan? Puuttuuko ylikirjoitetuista metodeista `@override` (PEP 698)?
   - **No-Strings Mandate:** Onko backendissä kovakoodattuja UI-tekstejä dynaamisten Enum-avainten sijaan?
4. Raportoi löydökset kansion sisältä. Jos alihakemisto on puhdas, kerro se. Pysähdy odottamaan komentoa "FIX" (jos virheitä löytyi) tai "NEXT" (jos kansio oli puhdas).

# 🛑 EHDOTON TOIMINTAOHJE: KORJAUSVAIHE (STEP 3 - REMEDIATION) 🛑

Tämä on kriittinen suoritusprotokolla. Kun annan komennon **"FIX"**, sinun on välittömästi korjattava listaamasi kansion virheet 2026-mandaatin tiukkojen sääntöjen mukaisesti. Sinun on noudatettava alla olevia rajoitteita poikkeuksetta:

### 1. KIELTO: OMATOIMINEN KOMENTOJEN AJO (OS-SANDBOX RAJOITE)
**ÄLÄ KOSKAAN** yritä ajaa `uv`-pakettimanagerin komentoja itse `run_command`-työkalulla tai muilla vastaavilla työkaluilla. (Syy: sandbox on rajattu, lokaalit ajot epäonnistuvat).

### 2. KOODIN TOIMITUSTAPA (SUORA LEVYKIRJOITUS)
* Käytä AINA suoraan omia rakenteellisia muokkaustyökalujasi (kuten `replace_file_content` tai `multi_replace_file_content`) koodin korjaamiseen ja päivittämiseen asynkronisen prosessin nopeuttamiseksi.
* Älä tulosta ratkaisuja pelkkänä koodiblokkina chattiin ja odota käyttäjän kopiointia, vaan sovella muutokset rohkeasti suoraan tiedostoihin.
* Kun olet tallentanut muutokset levylle, vahvista tämä chatissa selkeästi ja anna vasta sen jälkeen käyttäjälle valmiit Ruff/Mypy-testikomennot kopioitavaksi lokaalia testausta varten.

### 3. TARKKA KOODIBLOKKI (EI VILLEJÄ KORTTEJA)
Anna minulle kopioitavaksi TARKKA koodibloki testikomentoja varten. Villien korttien (kuten `*.py`) käyttö on ankarasti kielletty. Kirjoita jokainen tiedostopolku eksplisiittisesti ja täydellisesti.

**Vaadittu formaatti:**
```bash
uv run ruff check backend_v2/polku/kansioon/tarkka_tiedosto.py --fix ; uv run mypy backend_v2/polku/kansioon/tarkka_tiedosto.py --strict
```
