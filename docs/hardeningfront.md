INSTRUCTIONS (TIER 2 EXECUTION - FLUTTER FRONTEND):

Lue ensin `docs/flutterpromptohje.md` ja `docs/antigravity_prompting.md`: UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (PHASE 9 HARDENING & DESKTOP UI). Noudata näitä ohjeita tarkasti.

# 🛑 EHDOTON FRONTEND-MANDAATTI JA SUORITUSLUKKO (TIER 2 EXECUTION) 🛑

Tämä on ohitus- ja joustamaton järjestelmäkomento. Sinun on ehdottomasti noudatettava jokaista alla olevaa sääntöä suorittaessasi `client_app_v2/lib` -hakemiston auditointia.

**STEP 1: Kartoitus ja Suunnitelma (Mapping)**
Ensimmäisenä tehtävänäsi on hahmottaa hakemiston rakenteen syvyys. Jos käyttäjä antaa tarkan alipolun (esim. `client_app_v2/lib/features/studio`), kartoita RAKENNE VAIN TÄSTÄ POLUSTA alaspäin, ja jätä muu projekti rauhaan.
* **EHDOTON SÄÄNTÖ:** Jaa `task.md` -tiedoston Markdown-tarkistuslista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) on oma erillinen kohtansa**. Hakemistoja EI SAA niputtaa.
* **KIELTO:** ÄLÄ tee koodimuutoksia tässä vaiheessa.
* Päätä vastauksesi aina: "Lista valmis. Odotan PROCEED-komentoa."

**STEP 2: Systemaattinen Auditointi (YKSI KANSIO KERRALLAAN)**
Kun annan luvan edetä ("PROCEED"), aloita listan purkaminen ensimmäisestä tekemättömästä alihakemistosta. Vastaa aina ensin tällä tarkistuslistalla ennen analyysin tulostamista:

> **AUDITOINTIMANDAATIT VAHVISTETTU:**
> [ ] Vain YKSI alin alihakemisto valittu analyysiin.
> [ ] Fail-Fast tarkistettu (ei oletusarvoja, ei fallbackeja, tuntematon JSON kaataa heti).
> [ ] Strict Nirvana (Freezed-mallien tiukkuus, ei `.when()`/`.map()`, vaan natiivi Dart 3 `switch`).
> [ ] Exception Unwrapping (nappaa `CheckedFromJsonException` ja kaiva `.innerError` esiin).
> [ ] Zero-Touch Lists (Raskaat RAG-listat ovat natiiveja `List<T>` muodossa `@Freezed(equal: false)` kera, fast_immutable_collections-pakettia ei käytetä).
> [ ] Isolate Mandate (kaikki raskaat JSON-purut pidetään `Isolate.run`-sisällä Freezedistä huolimatta).
> [ ] The Single Source of Truth tsekattu (mallit noudattavat `seed_data.json` rakennetta).
> [ ] No-strings mandaatti tarkistettu (ei kovakoodattuja UI-tekstejä, käytössä `.arb`).
> [ ] Vanhat Providerit tarkistettu (pakotettu `@riverpod` koodigenerointi).
> [ ] "Mock Login" poikkeukset huomioitu (kovakoodaukset sallittu täällä).

Raportoi löydökset listan tulostamisen jälkeen havaitsemistasi tiedostoista yksityiskohtaisesti. Pysähdy odottamaan komentoa "FIX" tai "NEXT...".

**STEP 3: Korjaus ja Quality Loop (Remediation)**
Kun vastaan "FIX", korjaa listaamasi kansion virheet noudattaen 2026-mandaatin arkkitehtuurisääntöjä.
* **EHDOTON KIELTO:** ÄLÄ KOSKAAN yritä ajaa komentoja itse `run_command` -työkalulla. OS-sandbox rajoitteiden vuoksi suoritus on kielletty.
* Anna minulle kopioitavaksi TARKKA koodibloki ilman villejä kortteja:

```bash
uv run python docs\koodit\flutter_audit_loop.py lib/polku/kansioon/tarkka_tiedosto.dart --build
```
*(Käytä `--build` lippua vain jos `@riverpod` tai `@freezed` malleja muutettiin).*

Aina kun vastaat komentoon "FIX", sinun on aloitettava vastauksesi tällä listalla:

> **FIX-MANDAATIT VAHVISTETTU:**
> [ ] Virheet korjattu sääntöjen mukaisesti.
> [ ] Kopioitava skriptikomento luotu ekspliittisillä tiedostopoluilla (ei villejä kortteja kuten `*.dart`).
> [ ] Komentoa EI ole yritetty ajaa työkalulla OS-sandbox rajoitteiden vuoksi.
> [ ] Itemi merkitty `task.md` listaan tehdyksi [x].

Päätä vastauksesi aina täsmälleen sanoihin: "Valmis. Odotan NEXT-komentoa."

**STEP 4: Kontekstin nollaus ja siirtyminen (The NEXT command)**
Kun annan "NEXT..." komennon, jossa pyydän lukemaan `docs/flutterpromptohje.md` ja `docs/antigravity_prompting.md` uudelleen:
* **EHDOTON SÄÄNTÖ:** Sinun on oikeasti luettava työkalullasi kyseiset dokumentit uudelleen aktiiviseen muistiin context driftin estämiseksi.

Vastaa lukemisen jälkeen tällä listalla:

> **KONTEKSTI PALAUTETTU:**
> [ ] Määritellyt dokumentit luettu uudelleen aktiiviseen muistiin työkalun avulla.
> [ ] Säännöt (Fail-Fast, no-strings, Isolate.run) sisäistetty ja varmennettu.
> [ ] Siirrytään seuraavaan tekemättömään alihakemistoon (STEP 2 alkaa alusta).

Huom: Työskentelemme EHDOTTOMASTI vain yksi alihakemisto kerrallaan. Älä koskaan yritä auditoida tai korjata useampaa kansiota tai koko projektia yhdellä työkalukutsulla. Tämän rikkominen johtaa prosessin välittömään epäonnistumiseen.