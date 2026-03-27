INSTRUCTIONS (TIER 2 EXECUTION):

**STEP 1: Kartoitus ja Suunnitelma (Mapping)**
Ensimmäisenä tehtävänäsi on käyttää työkaluja (esim. bash `find client_app_v2/lib -type d`) ja hahmottaa `client_app_v2/lib` rakenteen syvyys. Rakenna tämän pohjalta `task.md` -tiedostoon Markdown-tarkistuslista. 

SÄÄNTÖ: Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) on oma erillinen kohtansa listalla** (esim. pelkkä `features/studio` ei riitä, vaan listalla on oltava erikseen `features/studio/controllers`, `features/studio/views`, `features/studio/views/widgets` jne.). Mitään hakemistoja ei saa niputtaa. ÄLÄ tee koodimuutoksia tässä vaiheessa. Pyydä minulta "PROCEED" kun lista on valmis.

**STEP 2: Systemaattinen Auditointi (One Subdirectory At A Time)**
Kun annan luvan edetä, aloitamme listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto.
2. Lue KAIKKI kyseisen alihakemiston .dart-tiedostot.
3. Peilaa koodia TARKASTI sääntöihin:
   - Onko tyhjiä `catch (e) {}` lohkoja joissa ei ole logger-kutsua tai virheen heittoa? (Fail-Fast rikkomus)
   - Onko käytössä Freezed API-vastauksissa? (De-Generator rikkomus)
   - Heitetäänkö raakoja `Exception` -luokkia `AppException`in sijaan?
   - Onko raskaita JSON-purkuja tehty ilman `Isolate.run` -kutsua? (Riverpod-puhtaus)
   - Onko UI-tekstejä kovakoodattu ilman `.arb` l10n käännösavaimia? (No-strings)
   - Onko Riverpodin vanhoja `final fooProvider = Provider(...)` rakenteita koodigeneroinnin (`@riverpod`) sijaan?
4. Raportoi löydökset kansion sisältä minulle viestillä. Jos alihakemisto on puhdas, kerro se. Pysähdy odottamaan komentoa "FIX" (jos virheitä löytyi) tai komentoa "NEXT..." (jos kansio oli puhdas).

**STEP 3: Korjaus ja Quality Loop (Remediation)**
Kun vastaan "FIX", korjaa äsken listaamasi kyseisen kansion virheet. 
Aja korjauksen jälkeen kohdekansioonsa `dart format` ja `dart analyze` (esim. `cd client_app_v2 && dart analyze lib/polku/kansioon`).
Merkitse sen jälkeen itemi `task.md` listasta tehdyksi [x].
Ilmoita minulle: "Valmis. Odotan NEXT-komentoa."

**STEP 4: Kontekstin nollaus ja siirtyminen (The NEXT command)**
Kun kansion auditointi oli puhdas tai korjaukset on tehty, annan sinulle aina tällaisen komennon:

> "NEXT. Muista yhä docs/flutterpromptohje.md säännöt ja docs/antigravity_prompting.md:#L133-189 UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.2 - PHASE 9 HARDENING & DESKTOP UI) pakolliset mandaatit ja rajoitukset kuten esimerkiksi Fail-Fast sääntö ja no-strings mandaatti (ei kovakoodattuja UI tekstejä, vaan .arb) samoin kuin Riverpod-puhtaus (Isolate.run). Lue ohjetiedostot nyt uudestaan."

Kun saat yllä olevan komennon, sinun on **EHDOTTOMASTI luettava työkalullasi (esim. bash `cat` / python) mainitut dokumentit ja niissä määritellyt rivit uudelleen** aktiiviseen muistiisi (context driftin estämiseksi). Vasta luettuasi ohjetiedostot uudelleen, siirry `task.md` listan seuraavaan tekemättömään alihakemistoon ja aloita STEP 2 alusta.

Huom: Työskentelemme EHDOTTOMASTI vain yksi alihakemisto kerrallaan. Älä koskaan yritä auditoida tai korjata useampaa kansiota tai koko projektia yhdellä työkalukutsulla.