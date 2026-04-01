---
description: Tier 2 (Frontend Hardening) - Step-by-step auditing loop for Flutter frontend directories against Phase 9 standards.
---

### 🟢 TIER 2: FLUTTER FRONTEND HARDENING LOOP

Lue ensin uusi Antigravity-säännöstö `.agents/rules/02_flutter_desktop.md`: UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (PHASE 9 HARDENING & DESKTOP UI). Noudata näitä ohjeita ehdottomasti.

**STEP 1: Kartoitus ja Suunnitelma (Mapping)**
Ensimmäisenä tehtävänäsi on käyttää työkaluja (esim. kansioiden listaus) ja hahmottaa hakemiston rakenteen syvyys.
* Jos käyttäjä antaa komennossaan tarkan alipolun (esim. `client_app_v2/lib/features/studio`), kartoita RAKENNE VAIN TÄSTÄ POLUSTA alaspäin. Jos alipolkua ei erikseen määritetä, kartoita koko `client_app_v2/lib`.
* **EHDOTON KIELTO (Sivuutettavat tiedostot):** Sivuuta analyysissä täysin kaikki koodigeneraattoreiden luomat tiedostot (päättyvät `.g.dart` tai `.freezed.dart`). Sivuuta myös `build/` ja `.dart_tool/` -kansiot. Älä lue, auditoi tai yritä muokata niitä säästääksesi resursseja ja estääksesi vääriä korjausehdotuksia.
* **SÄÄNTÖ:** Rakenna havainnoistasi chattiin tulostettava virtuaalinen Markdown-tarkistuslista (`task_front.md`). Jaa lista niin hienojakoiseksi, että **JOKAINEN alin alihakemisto (leaf directory) on oma erillinen kohtansa listalla**. Hakemistoja ei saa niputtaa.
* **KIELTO:** ÄLÄ tee koodimuutoksia tässä vaiheessa. Päätä vastauksesi aina sanoihin: *"Lista valmis. Odotan PROCEED-komentoa."*

**STEP 2: Systemaattinen Auditointi (One Subdirectory At A Time)**
Kun annan luvan edetä ("PROCEED"), aloitamme virtuaalisen listan purkamisen:
1. Valitse listan ENSIMMÄINEN tekemätön alihakemisto.
2. Vastaa aina ensin tällä tarkistuslistalla ennen analyysin tulostamista tai koodin lukemista. Konkreettiset ohjeet, kiellot ja soveltamistavat jokaiselle teemalle löytyvät sähkeestä `02_flutter_desktop.md`. Etsi ja auditoi koodista nämä teemat:

> **AUDITOINTIMANDAATIT VAHVISTETTU (Ks. `02_flutter_desktop.md`):**
> [ ] Vain YKSI alin alihakemisto valittu analyysiin.
> [ ] Generoidut tiedostot (`.g.dart`, `.freezed.dart`) ohitettu onnistuneesti.
> [ ] Fail-Fast Client Firewall (Strict JSON, ei oletusarvoja/fallbackeja).
> [ ] Riverpod Code Gen Mandate (Vain `@riverpod` sallittu, ei manuaalisia providereita).
> [ ] State Management & Loading Flags (Optimistic updates, ei raskaiden latausten vilkuttamista UI:ssa).
> [ ] The Three Riverpod Boundaries (Säännöt Widgettien, Notifierien ja Repo-rajapintojen välillä, ei "Jumala-widgettejä").
> [ ] Frontend Zero Leaks (Riverpod tilojen invalidointi suojauksena).
> [ ] Error Handling & Unwrapping (RFC 7807, AppErrorBoundary, ei tyhjiä catch-lohkoja, InnerError esiin).
> [ ] Concurrency & Isolate Mandate (Raskaat JSON-purut turvakaranteeniin).
> [ ] Strict Freezed & Dart 3 Pattern Matching (Natiivi switch, map/when kiellot, O(1) listat).
> [ ] Strongly Typed Routing & $extra Ban (Vain URL-pohjainen Opaque ID-reititys, ei objektien siirtoa reitittimen avulla).
> [ ] Zero-Hardcoding & 5-Layer I18N (Backend Enums, ei UI-merkkijonoja liiketoimintalogiikassa ehtolauseina).

3. Lue KAIKKI kyseisen alihakemiston `.dart`-tiedostot (pl. sivuutettavat). Työskentele yllä olevan tarkistuslistan avulla peilaten löydöksiä `02_flutter_desktop.md` mukaisiksi. Raportoi löydökset kansion sisältä. Jos alihakemisto on puhdas, kerro se. Pysähdy odottamaan komentoa "FIX" (jos virheitä löytyi) tai "NEXT" (jos kansio oli puhdas).

# 🛑 EHDOTON TOIMINTAOHJE: KORJAUSVAIHE (STEP 3 - REMEDIATION) 🛑

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
uv run python docs\koodit\flutter_audit_loop.py client_app_v2/lib/polku/kansioon/tarkka_tiedosto.dart --build
```
