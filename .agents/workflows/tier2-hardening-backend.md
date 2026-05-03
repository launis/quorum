---
description: Tier 2 (Backend Hardening) - Step-by-step auditing loop for Python backend directories against Phase 9 standards.
---

### 🟢 TIER 2: PYTHON BACKEND HARDENING LOOP

```xml
<system_prompt>
  <objective>Tier 2: Python Backend Hardening Loop</objective>
  <context_rules>Lue ensin uusi Antigravity-säännöstö `.agents/rules/01-python-backend.md` ja `.agents/rules/00-antigravity-core.md`: UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.2 - PHASE 9 HARDENING). Noudata näitä ohjeita ehdottomasti. Lue säännöstö `.agents/rules/04_directory_reference.md` hakemistorakenteen ymmärtämiseksi tarvittaessa.</context_rules>
  <phases>
    <phase id="1" name="Mapping (Kartoitus ja Suunnitelma)">
Ensimmäisenä tehtävänäsi on käyttää työkaluja (esim. kansioiden listaus) ja hahmottaa hakemiston rakenteen syvyys.
* Jos käyttäjä antaa komennossaan tarkan alipolun (esim. `backend_v2/api/routers/studio`), kartoita RAKENNE VAIN TÄSTÄ POLUSTA alaspäin. Jos alipolkua ei erikseen määritetä, kartoita koko `backend_v2`.
* **ERIKOISSÄÄNTÖ YKSITTÄISILLE TIEDOSTOILLE:** Jos käyttäjä antaa komennossaan tarkan tiedoston tai tiedostoja (esim. `backend_v2/services/execution.py`), kartoita lista **Vain näistä yksittäisistä tiedostoista**. Älä laajenna auditointia koko hakemistoon.
* **EHDOTON KIELTO (Sivuutettavat tiedostot):** Sivuuta analyysissä täysin `__pycache__` -kansiot, virtuaaliympäristöt (`venv`, `.venv`), alembic-migraatioiden versiotiedostot (`alembic/versions`) ja täysin tyhjät `__init__.py` -tiedostot. Älä lue, auditoi tai yritä muokata niitä säästääksesi resursseja ja kontekstia.
* **SÄÄNTÖ:** Rakenna havainnoistasi chattiin tulostettava virtuaalinen Markdown-tarkistuslista (`task_backend.md`). Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) TAI annettujen yksittäisten tiedostojen tapauksessa JOKAINEN yksittäinen tiedosto on oma erillinen kohtansa listalla**. Hakemistoja ei saa niputtaa.
* **STATE PERSISTENCE & CONTEXT RENEWAL:** Jos käyttäjän komennossa on `--resume` tai tiedosto `c:\src\quorum\tmp\hardening_state.json` on olemassa, lue se. Jätä listalta pois kaikki hakemistot, jotka on siellä merkitty tilaan "DONE". Tuo lista vain tekemättömistä hakemistoista. Aseta samalla lokaali tavoite: "Käsittelen maksimissaan 10 tiedostoa tässä sessiossa estääkseni kontekstin hajoamisen."
* **KIELTO:** ÄLÄ tee koodimuutoksia tässä vaiheessa. Päätä vastauksesi aina sanoihin: *"Lista valmis. Odotan PROCEED-komentoa."*
    </phase>
    <phase id="2" name="Auditing (Systemaattinen Auditointi, One Subdirectory At A Time)">
Kun annan luvan edetä ("PROCEED"), aloitamme virtuaalisen listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto TAI yksittäinen tiedosto.
2. Lue tiukasti kyseisen kohteen `.py`-tiedostot (tai vain se yksittäinen annettu tiedosto) huomioiden sivuutettavat kansiot. Määrittele auditointitaulukko koskemaan Vain valittua laajuutta.
3. **MANDATOITU TRACEABILITY MATRIX**: Sinun on **EHDOTTOMASTI** raportoitava havaintosi tulostamalla chattiin tarkka Markdown-taulukko ("Audit Matrix"). Taulukon on **PAKKO** sisältää oma erillinen rivinsä jokaiselle Phase 9 -säännölle (24+ kpl), ja jokainen on arvioitava (Pass/Fail/NA):
   - **`the_zero_compromise_pledge`**: Ei `.get("default")` fallbackeja. Pydantic-validointi pakollinen.
   - **`the_duct_tape_ban` / `silent_failures`**: Ei "God Blockeja" (`except Exception: pass`). Virheet on lokitettava ja heitettävä.
   - **`no_naked_dicts_in_state`**: Ei raakoja sanakirjoja (dict) tilanhallinnassa. Pydantic-mallit pakollisia.
   - **`structured_state_envelopes_mandate`**: Tilaprojektiot ainoastaan `StepOutputDTO` listana, ei `dict` palautuksia. Ei merkkijonojen arvaamista (`.endswith()`) tilojen purussa.
   - **`strict_pydantic_v2_rust`**: `.model_validate()`, ei vanhaa `parse_obj()`. `extra='forbid'` käytössä.
   - **`fail_fast_hydration_mandate`**: Kaikki dict-muodossa kulkeva epävarma data (kuten komponentit/matriisit tietokannasta tai webhookista) on "hydratoitava" `.model_validate()` -metodilla VÄLITTÖMÄSTI ennen käsittelyä. Arvojen onkiminen `data.get("avain")` tyylillä on ehdottomasti kielletty logiikkakerroksessa.
   - **`opaque_stripe_id_mandate`**: Vain `usr_123` jne. Ei kokonaisluku-ID:itä (IDOR) tai slugeja relaatioissa.
   - **`python_314_modern_syntax`**: PEP 695 generics, modernit unionit (`| None`), ei `Optional[X]`.
   - **`zero_legacy_fallback_hacks`**: Vanhoja asioita ei saa tukea! Tämä koskee KAIKKIA fallback-asioita (ei "or" ketjuja, ei `.get(key, default)`, ei puuttuvien arvojen paikkaamista tyhjillä). Ei `@model_validator` -purkkakorjauksia vanhan V1 datan hyväksymiseksi. Vanhat kentät ja oletusarvot pitää poistaa armotta. **(Tämä on auditoitava erillisenä Pass/Fail -rivinä taulukossa!)**
   - **`frozen_state_mutability`**: Domain-mallit muuttumattomia (`ConfigDict(frozen=True)`).
   - **`pydantic_native_field_priority`**: Suosi Pydanticin natiivia `Field(ge=0)` validaatiota manuaalisen field_validatorin sijaan.
   - **`zero_type_ignore_shortcuts`**: Ei `# type: ignore` merkintöjä ilman tarkkaa error codea ja perustelua.
   - **`anemic_routers`**: Reitittimissä vain HTTP-käsittely. Ei business-logiikkaa.
   - **`blocking_the_fastapi_thread`**: Raskaat ajot on siirrettävä asynkroniseen Arq-työjonoon.
   - **`pydantic_namespace_collisions`**: Ei inline-skeemoja reitittimissä. Kaikki skeemat `models/` -kansiossa.
   - **`security_logging_ban`**: Lokeihin ei saa printata käyttäjien prompteja (PII) tai API-avaimia.
   - **`polymorphic_routing_o1`**: Käytä Discriminated Unioneita ja natiivia `match/case` syntaksia.
   - **`no_string_l10n`**: Ei kovakoodattuja näyttötekstejä. Enum-avaimet rajapintojen yli.
   - **`data_leak_prevention_firewall`**: `response_model` (periytyen `BaseResponseDTO`:sta) on PAKOLLINEN jokaiseen reittiin tietovuotojen estämiseksi.
   - **`llm_structured_execution_mandate`**: LLM-kutsut vain `LLMTaskExecutor.execute_structured_task()` tai `execute_chat_task()` kautta (ei suoraa LLMClient-käyttöä).
   - **`ui_driven_synthesis_boundary`**: AI-raportointi suodatettava tiukasti UI-profiilin mukaan (ei token-räjähdyksiä).
   - **`tripartite_rendering_boundary`**: Ei kovakoodattuja markdown-taulukoita (esim. matriisiyhteenvedot) backendissä. Backend palauttaa vain DTO-dataa, ja UI (Flutter) + PDF (Jinja) vastaavat natiivista renderöinnistä.
   - **`high_fidelity_prompting`**: Kaikki promptien dynaamiset parametrit on eristetty `<execution_parameters>`-tagiin promptin alkuun. Prompti ei sisällä f-stringejä loogisten sääntöjen rakentamisessa.
   - **`strict_math_display_isolation`**: Pisteiden laskenta `computed_min` perusteella. UI `scale_min` on vain näytölle.
   - **`zero_orm_bleed`**: Tietokantakerros palauttaa vain puhtaita Pydantic-malleja, ei raakoja sanakirjoja.
   - **`strict_dependency_injection`**: Palvelut ladataan FastAPI:ssa `Depends()` kautta. Ei manuaalisia instansseja.
   - **`global_settings_import`**: `get_settings` tuotava tiedoston alussa.
   - **`no_inline_imports`**: Ei inline importteja (esim. funktioiden sisällä). Kaikki importit tiedoston alussa.
   - **`cross_language_enum_parity`**: Pydantic Enum/Literal muuttujat täytyy olla pariteetissa Flutterin kanssa.
   - **`schema_driven_routing`**: Ei "Duck Typingiä" (sokeaa sanakirjojen muodon availua). Reititys aina tietokannasta tulevan schema_map:in perusteella.
   - **`prompt_compiler_immutability`**: Älä muokkaa `prompt_compiler.py` -tiedostoa.
   - **`Synthesis.py Standard`**: Funktiot "Pure Functions" muodossa. Sisäkkäisten looppien tilalla O(1) haut.
   - Käytä sarakkeita: `| Rule Block ID / Sääntö | Tila (Pass / Fail) | Löydökset & Perustelu |`.
   - Varmista, että todella käyt läpi koodista säännösten <banned_pattern> ja <mandatory_pattern> asiat kohta kohdalta. Tämä poistaa hallusinaatiot ja ohitukset.
4. Pysähdy taulukon tulostamisen jälkeen. Odotan sen näkemistä. Jää odottamaan komentoa "FIX" (jos asioita on korjattavana / Fail) tai komentoa "NEXT" (jos kaikki säännöt olivat puhtaasti Pass).
5. **STATE PERSISTENCE (TALLENNUS):** Kun kansio on valmis (eli sait komennon korjata ja korjasit, TAI se oli heti puhdas), päivitä VÄLITTÖMÄSTI `c:\src\quorum\tmp\hardening_state.json` ja merkkaa tämä alihakemisto tilaan "DONE". Pidä lukua tässä sessiossa auditoimiesi tiedostojen yhteismäärästä.
6. **SESSION LIMIT**: Jos olet käsitellyt (auditoinut) yhteensä 10 tiedostoa TÄSSÄ sessiossa, LOPETA välittömästi kansion valmistuttua. Älä siirry seuraavaan. Tulosta käyttäjälle: *"Sessioraja (10 tiedostoa) saavutettu. Avaa uusi chat-ikkuna ja anna komento `/tier2-hardening-backend --resume` jatkaaksesi laatuporttia turvallisesti."*  
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
uv run python scripts/backend_audit_loop.py backend_v2/polku/kansioon/tarkka_tiedosto.py --openapi --test
```
    </critical_remediation_protocol>
  </phases>
</system_prompt>
```
