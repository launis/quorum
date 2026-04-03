---
description: Tier 2 (Backend Hardening) - Step-by-step auditing loop for Python backend directories against Phase 9 standards.
---

### 🟢 TIER 2: PYTHON BACKEND HARDENING LOOP

```xml
<system_prompt>
  <objective>Tier 2: Python Backend Hardening Loop</objective>
  <context_rules>Lue ensin uusi Antigravity-säännöstö `.agents/rules/01-python-backend.md` ja `.agents/rules/00-antigravity-core.md`: UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.2 - PHASE 9 HARDENING). Noudata näitä ohjeita ehdottomasti.</context_rules>
  <phases>
    <phase id="1" name="Mapping (Kartoitus ja Suunnitelma)">
Ensimmäisenä tehtävänäsi on käyttää työkaluja (esim. kansioiden listaus) ja hahmottaa hakemiston rakenteen syvyys.
* Jos käyttäjä antaa komennossaan tarkan alipolun (esim. `backend_v2/api/routers/studio`), kartoita RAKENNE VAIN TÄSTÄ POLUSTA alaspäin. Jos alipolkua ei erikseen määritetä, kartoita koko `backend_v2`.
* **EHDOTON KIELTO (Sivuutettavat tiedostot):** Sivuuta analyysissä täysin `__pycache__` -kansiot, virtuaaliympäristöt (`venv`, `.venv`), alembic-migraatioiden versiotiedostot (`alembic/versions`) ja täysin tyhjät `__init__.py` -tiedostot. Älä lue, auditoi tai yritä muokata niitä säästääksesi resursseja ja kontekstia.
* **SÄÄNTÖ:** Rakenna havainnoistasi chattiin tulostettava virtuaalinen Markdown-tarkistuslista (`task_backend.md`). Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) on oma erillinen kohtansa listalla** (esim. pelkkä `backend_v2/api/routers` ei riitä, vaan listalla on oltava erikseen `backend_v2/api/routers/studio` jne.). Hakemistoja ei saa niputtaa.
* **KIELTO:** ÄLÄ tee koodimuutoksia tässä vaiheessa. Päätä vastauksesi aina sanoihin: *"Lista valmis. Odotan PROCEED-komentoa."*
    </phase>
    <phase id="2" name="Auditing (Systemaattinen Auditointi, One Subdirectory At A Time)">
Kun annan luvan edetä ("PROCEED"), aloitamme virtuaalisen listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto.
2. Vastaa aina ensin tällä tarkistuslistalla ennen analyysin tulostamista tai koodin lukemista. Konkreettiset ohjeet, kiellot ja soveltamistavat jokaiselle teemalle löytyvät sähkeestä `01-python-backend.md`. Etsi ja auditoi koodista nämä teemat:

<audit_mandates>
  <rule>Fail-Fast & Dual-Reporting</rule>
  <rule>AppException (RFC 7807)</rule>
  <rule>Strict Pydantic V2 & No Naked Dicts</rule>
  <rule>Native Pydantic Field() Priority over @field_validator</rule>
  <rule>Data Leak Prevention & SRP</rule>
  <rule>Modern Typing & No-Strings Mandate</rule>
</audit_mandates>

3. Lue KAIKKI kyseisen alihakemiston `.py`-tiedostot (huomioiden sivuutettavat kansiot). Työskentele yllä olevan tarkistuslistan avulla peilaten löydöksiä `01-python-backend.md` mukaisiksi. Raportoi löydökset kansion sisältä. Jos alihakemisto on puhdas, kerro se. Pysähdy odottamaan komentoa "FIX" (jos virheitä löytyi) tai "NEXT" (jos kansio oli puhdas).
    </phase>
    <critical_remediation_protocol name="STEP 3 - FIX (Korjausvaihe)">
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
uv run python scripts/backend_audit_loop.py backend_v2/polku/kansioon/tarkka_tiedosto.py --openapi
```
    </critical_remediation_protocol>
  </phases>
</system_prompt>
```
