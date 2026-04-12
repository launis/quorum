---
description: Tier 2 (Frontend Hardening) - Step-by-step auditing loop for Flutter frontend directories against Phase 9 standards.
---

### 🟢 TIER 2: FLUTTER FRONTEND HARDENING LOOP

```xml
<system_prompt>
  <objective>Tier 2: Flutter Frontend Hardening Loop</objective>
  <context_rules>Lue ensin uusi Antigravity-säännöstö `.agents/rules/00-antigravity-core.md` ja `.agents/rules/02_flutter_desktop.md`: UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (PHASE 9 HARDENING & DESKTOP UI). Noudata näitä ohjeita ehdottomasti. Lue säännöstö `.agents/rules/04_directory_reference.md` hakemistorakenteen ymmärtämiseksi tarvittaessa.</context_rules>
  <phases>
    <phase id="1" name="Mapping (Kartoitus ja Suunnitelma)">
Ensimmäisenä tehtävänäsi on käyttää työkaluja (esim. kansioiden listaus) ja hahmottaa hakemiston rakenteen syvyys.
* Jos käyttäjä antaa komennossaan tarkan alipolun (esim. `client_app_v2/lib/features/studio`), kartoita RAKENNE VAIN TÄSTÄ POLUSTA alaspäin. Jos alipolkua ei erikseen määritetä, kartoita koko `client_app_v2/lib`.
* **EHDOTON KIELTO (Sivuutettavat tiedostot):** Sivuuta analyysissä täysin kaikki koodigeneraattoreiden luomat tiedostot (päättyvät `.g.dart` tai `.freezed.dart`). Sivuuta myös `build/` ja `.dart_tool/` -kansiot. Älä lue, auditoi tai yritä muokata niitä säästääksesi resursseja ja estääksesi vääriä korjausehdotuksia.
* **SÄÄNTÖ:** Rakenna havainnoistasi chattiin tulostettava virtuaalinen Markdown-tarkistuslista (`task_front.md`). Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) on oma erillinen kohtansa listalla**. Hakemistoja ei saa niputtaa.
* **STATE PERSISTENCE & CONTEXT RENEWAL:** Jos käyttäjän komennossa on `--resume` tai tiedosto `c:\src\quorum\tmp\hardening_state.json` on olemassa, lue se. Jätä listalta pois kaikki hakemistot, jotka on siellä merkitty tilaan "DONE". Tuo lista vain tekemättömistä hakemistoista. Aseta samalla lokaali tavoite: "Käsittelen maksimissaan 5 kansiota tässä sessiossa estääkseni kontekstin hajoamisen."
* **KIELTO:** ÄLÄ tee koodimuutoksia tässä vaiheessa. Päätä vastauksesi aina sanoihin: *"Lista valmis. Odotan PROCEED-komentoa."*
    </phase>
    <phase id="2" name="Auditing (Systemaattinen Auditointi, One Subdirectory At A Time)">
Kun annan luvan edetä ("PROCEED"), aloitamme virtuaalisen listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto.
2. Lue ensin tiukasti KAIKKI kyseisen alihakemiston `.dart`-tiedostot (pl. sivuutettavat kansiot/tiedostot).
3. **MANDATOITU TRACEABILITY MATRIX**: Sinun on **EHDOTTOMASTI** raportoitava havaintosi tulostamalla chattiin tarkka Markdown-taulukko ("Audit Matrix"). Sinun on kirjoitettava tähän taulukkoon rivi *jokaiselle* `00-antigravity-core.md` ja `02_flutter_desktop.md` -tiedostoissa mainitulle säännölle (esim. `riverpod_code_gen_mandate`, `opaque_stripe_id_mandate`, `frontend_zero_leaks`, `strongly_typed_routing` jne).
   - Käytä sarakkeita: `| Rule Block ID / Sääntö | Tila (Pass / Fail) | Löydökset & Perustelu |`.
   - Varmista, että todella käyt läpi koodista säännösten <banned_pattern> ja <mandatory_pattern> asiat kohta kohdalta. Tämä poistaa hallusinaatiot ja ohitukset.
4. Pysähdy taulukon tulostamisen jälkeen. Odotan sen näkemistä. Jää odottamaan komentoa "FIX" (jos asioita on korjattavana / Fail) tai komentoa "NEXT" (jos kaikki säännöt olivat puhtaasti Pass).
5. **STATE PERSISTENCE (TALLENNUS):** Kun kansio on valmis (eli sait komennon korjata ja korjasit, TAI se oli heti puhdas), päivitä VÄLITTÖMÄSTI `c:\src\quorum\tmp\hardening_state.json` ja merkkaa tämä alihakemisto tilaan "DONE".
5. **SESSION LIMIT**: Jos olet käsitellyt 5 kansiota TÄSSÄ sessiossa, LOPETA välittömästi. Älä siirry seuraavaan. Tulosta käyttäjälle: *"Sessioraja (5 kansiota) saavutettu. Avaa uusi chat-ikkuna ja anna komento `/tier2-hardening-frontend --resume` jatkaaksesi laatuporttia turvallisesti."* 
    </phase>
    <critical_remediation_protocol name="STEP 3 - FIX (Korjausvaihe)">
Tämä on kriittinen suoritusprotokolla. Kun annan komennon **"FIX"**, sinun on välittömästi korjattava listaamasi kansion virheet 2026-mandaatin tiukkojen sääntöjen mukaisesti. Sinun on noudatettava alla olevia rajoitteita poikkeuksetta:

### 1. KIELTO: OMATOIMINEN KOMENTOJEN AJO (OS-SANDBOX RAJOITE)
**ÄLÄ KOSKAAN** yritä ajaa komentoja itse `run_command`-työkalulla tai muilla vastaavilla työkaluilla. (Syy: sandbox on rajattu, lokaalit flutter-ajot epäonnistuvat).

### 2. KOODIN TOIMITUSTAPA (SUORA LEVYKIRJOITUS)
* Käytä AINA suoraan omia rakenteellisia muokkaustyökalujasi (kuten `replace_file_content` tai `multi_replace_file_content`) koodin korjaamiseen asynkronisen prosessin nopeuttamiseksi.
* Älä tulosta ratkaisuja pelkkänä koodiblokkina chattiin ja odota käyttäjän kopiointia. Minulla on agentti, joka osaa kirjoittaa tiedostoihin sisäisillä työkaluillaan.
* Kun olet tallentanut muutokset levylle, vahvista tämä chatissa selkeästi ja anna vasta sen jälkeen käyttäjälle valmiit lint-komennot kopioitavaksi lokaalia testausta varten.

### 3. TARKKA KOODIBLOKKI (EI VILLEJÄ KORTTEJA)
Anna minulle kopioitavaksi TARKKA koodibloki testikomentoja varten. Villien korttien (kuten `*.dart`) käyttö on ankarasti kielletty. Kirjoita jokainen tiedostopolku eksplisiittisesti ja täydellisesti. *(Käytä `--build` lippua vain, jos `@riverpod` tai `@freezed` malleja muutettiin).*

**Vaadittu formaatti:**
```bash
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/polku/kansioon/tarkka_tiedosto.dart --build
```
    </critical_remediation_protocol>
  </phases>
</system_prompt>
```
