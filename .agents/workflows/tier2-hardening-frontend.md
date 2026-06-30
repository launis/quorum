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
* **ERIKOISSÄÄNTÖ YKSITTÄISILLE TIEDOSTOILLE:** Jos käyttäjä antaa komennossaan tarkan tiedoston tai tiedostoja (esim. `client_app_v2/lib/main.dart`), kartoita lista **Vain näistä yksittäisistä tiedostoista**. Älä laajenna auditointia koko hakemistoon.
* **EHDOTON KIELTO (Sivuutettavat tiedostot):** Sivuuta analyysissä täysin kaikki koodigeneraattoreiden luomat tiedostot (päättyvät `.g.dart` tai `.freezed.dart`). Sivuuta myös `build/` ja `.dart_tool/` -kansiot. Älä lue, auditoi tai yritä muokata niitä säästääksesi resursseja ja estääksesi vääriä korjausehdotuksia.
* **SÄÄNTÖ:** Rakenna havainnoistasi chattiin tulostettava virtuaalinen Markdown-tarkistuslista (`task_front.md`). Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) TAI annettujen yksittäisten tiedostojen tapauksessa JOKAINEN yksittäinen tiedosto on oma erillinen kohtansa listalla**. Hakemistoja ei saa niputtaa.
* **STATE PERSISTENCE & CONTEXT RENEWAL:** Jos käyttäjän komennossa on `--resume` tai tiedosto `c:\src\quorum\tmp\hardening_state.json` on olemassa, lue se. Jätä listalta pois kaikki hakemistot, jotka on siellä merkitty tilaan "DONE". Tuo lista vain tekemättömistä hakemistoista. Aseta samalla lokaali tavoite: "Käsittelen maksimissaan 10 tiedostoa tässä sessiossa estääkseni kontekstin hajoamisen."
* **KIELTO:** ÄLÄ tee koodimuutoksia tässä vaiheessa. Päätä vastauksesi aina sanoihin: *"Lista valmis. Odotan PROCEED-komentoa."*
    </phase>
    <phase id="2" name="Auditing (Systemaattinen Auditointi, One Subdirectory At A Time)">
Kun annan luvan edetä ("PROCEED"), aloitamme virtuaalisen listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto TAI yksittäinen tiedosto.
2. Lue tiukasti kyseisen kohteen `.dart`-tiedostot (tai vain se yksittäinen annettu tiedosto) huomioiden sivuutettavat kansiot/tiedostot. Määrittele auditointitaulukko koskemaan Vain valittua laajuutta.
3. **MANDATOITU TRACEABILITY MATRIX**: Sinun on **EHDOTTOMASTI** raportoitava havaintosi tulostamalla chattiin tarkka Markdown-taulukko ("Audit Matrix"). Sinun on **PAKKO** jäsentää `c:\src\quorum\.agents\rules\00-antigravity-core.md` ja `c:\src\quorum\.agents\rules\02_flutter_desktop.md` -tiedostojen sisältö mielessäsi ja luotava matriisiin oma rivi **jokaista tiedostoissa esiintyvää `<rule_block>` -kohtaa kohden**.
   **Erityishuomio 1:** Varmista ettet päästä "the_zero_compromise_pledge"-tarkistuksesta läpi yhtäkään Dartin null-coalescing (`?? 'default'`) oikotietä tai `.maybeWhen` fallbackia, jotka piilottavat rakenteellisia virheitä. Vanhoja asioita ei saa tukea! Tämä koskee KAIKKIA fallback-asioita (ei "or" ketjuja, ei `.maybeWhen` tai oletusarvojen ruokkimista puuttuvalla datalla). Legacy koodia ja purkkapaikkauksia ei suvaita. **Erityishuomio 2:** `frontend_zero_db_hardcoding_mandate` vaatii tarkistamaan, ettei mikään UI-komponentti tai kontrolleri oleta koodissa tiettyjen tietokantataulujen ID-tunnisteita, nimiä tai indeksijärjestyksiä. **Erityishuomio 3:** `dropdown_database_alignment` vaatii varmistamaan, että kaikki pudotusvalikoiden (Dropdowns) kategoria- ja suodatusehdot ovat täysin synkronissa tietokannan ja `enums.dart`-määritelmien kanssa (käyttäen `PromptBlockCategoryGroups`-ryhmiä) ilman purkkaratkaisuja tai UI-tason ohituksia.
   - Käytä sarakkeita: `| Nro | Sääntö ID | Tila (Pass / Fail) | Löydökset & Perustelu |`.
   - Varmista, että todella käyt läpi koodista säännösten <banned_pattern> ja <mandatory_pattern> asiat kohta kohdalta. Tämä poistaa hallusinaatiot ja ohitukset.

    <critical_anti_laziness_mandate>
      KIELTO: Audit Matrixin tiivistäminen, rivien yhdistäminen tai sääntöjen pois jättäminen on ANKARASTI KIELLETTY (Anti-Laziness Mandate). 
      Sinun on PAKKO tulostaa taulukkoon rivi JOKAISElle `02_flutter_desktop.md` (ja ytimen) tiedostossa olevalle `<rule_block>`:lle, vaikka se olisi "Pass" tai "NA". 
      Jos jokin sääntö uupuu taulukosta, rikot suoraan järjestelmän pääarkkitehtuurin sääntöjä. Jokainen Phase 9 -sääntö on käytävä läpi eksplisiittisesti, jotta pakotat oman huomiomekanismisi (attention mechanism) tarkistamaan koodin tuon säännön osalta.
    </critical_anti_laziness_mandate>

4. Pysähdy taulukon tulostamisen jälkeen. Odotan sen näkemistä. Jää odottamaan komentoa "FIX" (jos asioita on korjattavana / Fail) tai komentoa "NEXT" (jos kaikki säännöt olivat puhtaasti Pass).
5. **STATE PERSISTENCE (TALLENNUS):** Kun kansio on valmis (eli sait komennon korjata ja korjasit, TAI se oli heti puhdas), päivitä VÄLITTÖMÄSTI `c:\src\quorum\tmp\hardening_state.json` ja merkkaa tämä alihakemisto tilaan "DONE". Pidä lukua tässä sessiossa auditoimiesi tiedostojen yhteismäärästä.
6. **SESSION LIMIT**: Jos olet käsitellyt (auditoinut) yhteensä 10 tiedostoa TÄSSÄ sessiossa, LOPETA välittömästi kansion valmistuttua. Älä siirry seuraavaan. Tulosta käyttäjälle: *"Sessioraja (10 tiedostoa) saavutettu. Avaa uusi chat-ikkuna ja anna komento `/tier2-hardening-frontend --resume` jatkaaksesi laatuporttia turvallisesti."* 
    </phase>
    <critical_remediation_protocol name="STEP 3 - FIX (Korjausvaihe)">
Tämä on kriittinen suoritusprotokolla. Kun annan komennon **"FIX"**, sinun on välittömästi korjattava listaamasi kansion virheet 2026-mandaatin tiukkojen sääntöjen mukaisesti. Sinun on noudatettava alla olevia rajoitteita poikkeuksetta:

### 1. KIELTO: OMATOIMINEN KOMENTOJEN AJO (POIKKEUKSET)
**ÄLÄ KOSKAAN** yritä ajaa satunnaisia komentoja itse `run_command`-työkalulla. Sandbox on rajattu (esim. `flutter gen-l10n` tai `flutter pub run` epäonnistuvat/ovat kiellettyjä). 
**EHDOTON POIKKEUS:** Sinun on **PAKKO** suorittaa laadunvarmistustestaus suoraan itse ajamalla: `uv run python scripts/flutter_audit_loop.py client_app_v2/[polku]`.

### 2. KOODIN TOIMITUSTAPA (SUORA LEVYKIRJOITUS)
* Käytä AINA suoraan omia rakenteellisia muokkaustyökalujasi (kuten `replace_file_content` tai `multi_replace_file_content`) koodin korjaamiseen asynkronisen prosessin nopeuttamiseksi.
* Älä tulosta ratkaisuja pelkkänä koodiblokkina chattiin ja odota käyttäjän kopiointia. Minulla on agentti, joka osaa kirjoittaa tiedostoihin sisäisillä työkaluillaan.
* Kun olet tallentanut muutokset levylle, **AJA AUDIT LOOP** varmistaaksesi muutokset.

### 3. TARKKA KOODIBLOKKI (EI VILLEJÄ KORTTEJA)
Anna minulle kopioitavaksi TARKKA koodibloki testikomentoja varten, EHKÄ mikäli oma testisi kaatuu. Villien korttien (kuten `*.dart`) käyttö on ankarasti kielletty. Kirjoita jokainen tiedostopolku eksplisiittisesti ja täydellisesti. *(Käytä `--build` lippua vain, jos `@riverpod` tai `@freezed` malleja muutettiin).*

**Vaadittu formaatti:**
```bash
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/polku/kansioon/tarkka_tiedosto.dart --build
```
    </critical_remediation_protocol>
  </phases>
</system_prompt>
```
