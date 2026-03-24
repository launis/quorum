# EPIC: V3 Flutter Frontend Adaptation (Post-MVC & Event Sourcing)

## 1. Yhteenveto (Summary)
V3-moottorin siirtyessä keskitettyyn Event Sourcing ja "The Flush Strategy" (Checkpointing) -arkkitehtuuriin, Frontend menettää aiemman jatkuvasti yli-kirjoitetun `ExecutionRecord.results` sanakirjatilan. Samalla hiljattainen P1.8 MVC-refaktorointi tuhosi kaiken SDUI (Server-Driven UI) -logiikan.

Tämä Epic määrittelee Mandaattien (The Zero-Compromise Pledge) mukaisen polun, jolla Flutter-asiakassovellus elää tässä uudessa maailmassa. Se mukautetaan lukemaan The De-Generator Mandaatin mukaisesti puhdasta `ReportDataDTO` litteää mallia BFF-kerrokseelta, säilyttäen optimointinsa, tiukan reitityksen (GoRouter) sekä Riverpod 3.0 mutaatio-reaktiivisuutensa.

---

## 2. Taustakonteksti: V3 Big Bangin Opetukset
Moottori koki giganttisen päivityksen. Tämä on Flutter-tiimin "Need-To-Know":
* **SDUI. On. Kuollut:** Backend ei enää koskaan lähetä `render_blueprint` komponenttipuita. Frontend on vastuussa UI-komponenttien piirtämisestä. Backend lähettää vain `ReportDataDTO` (Metadata, Layout asettelut: 1D/2D/3D) ja tiukasti tyypitetyt `ReportAxisDTO` solut.
* **Event Sourcing (Mutaation kuolema):** Backend tallentaa kognitiivisen ajon puhtaana append-only -lokina (TraceEvents). Koko `TraceEvent` on 100% Python-backendin salaisuus. Flutter ei KOSKAAN lue raakoja tapahtumia, vaan se kutsuu BFF-rajapintoja (esim. `/render`), jotka "taittavat" lokin JSON DTO -muotoon.
* **Fail-Fast & Rehydration:** Backend katkaisee ajon heti virheeseen ja heittää tyyppiturvallisen poikkeuksen (RFC 7807). Ajo jää odottamaan `REHYDRATING` tilaan. Käyttäjä voi lähettää jatkopyynnön (Rehydration), jolloin backend kelustelee moottorin takaisin samaan tilaan ja jatkaa salamana eteenpäin ilman redundantteja API-kutsuja LLM:lle.

---

## 3. Tavoitteet (Objectives)
- **Zero-Math UI Säilytys:** Frontend ei ryhdy itse raskaaseen Event-Sourcing datan REDUCE-murskaukseen, eikä se laske itse prosentteja. UI nojaa täysin Backendin `/render` API:n generoimaan Pydantic `ReportDataDTO` -pakettiin valitulla `OutputProfile`lla.
- **Saumaton Rehydration (Ajosta Toipuminen):** Kaatuneesta (Fail-Fast) tilasta palauttaminen käyttöliittymässä ei merkitse ajon nollausta. Käyttäjälle tarjotaan Actionable Hint -painike "Jatka ajoa", joka ohjaa ID:n suoraan moottorin rehydrationiin.
- **Timeline API (Signal & Fetch):** Vanha `DatabaseProgressTracker` kuolee. Statuspäivitykset hoituvat ohuilla SSE-pingeillä (deltas), kun taas massiivinen kymmenien/satojen kilotavujen raportti (Lukumalli) noudetaan erillisellä HTTP GET Fetchillä.

---

## 4. Vaiheet (Execution Plan)

### Vaihe 1: Datan Luku ja Litteä MVC-Arkkitehtuuri (ReportDataDTO)
* **Toimenpide:** Refaktoroidaan Flutterin `ExecutionRecord` mallit. Dart lakkaa odottamasta dynaamista `results` sanakirjaa jolta se kyselee ominaisuuksia. Se siirtyy The De-Generator Mandaattiin: Lukemaan litteää, ennustettavaa asettelua (`preset_view: 1d_metrics`, `axes: [...]`).
* **Isolate Parsing:** Jotta Appi ei jäädy (Main Thread Jank) raskaiden satojen kilotavujen RAG-tulosten (eval_notes, justification) JSON-purussa, `jsonDecode` ja DTO-kuorinta siirretään ehdottomasti Dartin **Isolate.run()** taustasäikeeseen.

### Vaihe 2: Rehydration UX ja Riverpod 3.0 Mutaatiot
* **Toimenpide:** Lisätään navigaation tuki infrastuktuurivirheiden (`FAILED`) varalle.
* **Mutaatio Law:** Luodaan Controlleriin `final resumeExecutionMutation = Mutation<void>();`. Tämä takaa Optimistic Updaten (UI siirtyy Loading Stateen viiveettömästi) noudattaen uutta The Riverpod 3.0 Law:ta vaativien asiointien osalta. `bool _isLoading` liput ovat kiellettyjä.

### Vaihe 3: Delta Signal & Heavy Fetch (SSE Optimointi)
* **Toimenpide:** Siirrytään hitaasta pollausmallista turvalliseen The Payload Trap -vapaaseen SSE-virtaukseen.
* **Toteutus:** SSE-putki välittää vain *tilan muutoksia, lokeja ja askelmuutoksia* (Delta Signal) sisältäen `trace_version`. Itse giganttista Pydantic `ReportDataDTO` lukumallia ei KOSKAAN työnnetä asynkronisen SSE:n läpi verkkokaistan säästämiseksi. Lukumalli (Heavy Fetch) ladataan perinteisellä HTTP GET:llä vain kun käyttäjä selaa raporttia tai kun olennaisia blokkeja on syntetisoitu.
* **Catch-up Fetch:** Mobiiliverkkojen (hissi, metro) katkokset paikataan taustakutsulla yhteyden palatessa, estäen UI:n jäätymistä PING-signaalien hävitessä tyhjyyteen.

### Vaihe 4: RFC 7807 ja Actionable Hints (Global Error Handling V3)
* **Toimenpide:** Varmistetaan manifestin mukainen virheenhallinta V3-putkessa. Kun Frontendin BFF Fetch palauttaa HTTP 400/500 `AppException`in, Frontendin Dart-parseri ei kaadu, vaan paketoi sen.
* **Toteutus:** Raw Error Name (esim. `TOOL_EXECUTION_FAILED`) ei PÄÄDY ruudulle. Aina kun vikatila ilmenee, sivu ohjaa sen `GlobalErrorView V3` -komponenttiin, joka purkaa Pydantic-virheen paikallisen `.arb` -tiedoston avulla aidoksi **Actionable Hintiksi**: *"Asiantuntija-agentti ei saanut yhteyttä rekisteriin. [Yritä jatkaa ajoa (Päivitä)]"*.

---

## 5. Konkreettiset Vaikutukset Koodiin (Top Targets)

1. **`client_app_v2/lib/features/execution/views/execution_view.dart`**
   Komponentti koodataan täysin uusiksi pudottamalla `SDUI`/`Blueprint` UIX builderit. Tilalle koodataan 1D/2D/3D komponenttirenderöijät jotka iteroivat turvallisesti backendin asettamien The De-Generator sääntöjen ympärillä. `FAILED`-tila laukaisee Actionable Hint paneelin.

2. **`client_app_v2/lib/features/execution/controllers/execution_controller.dart`**
   Controlleri (joka käyttää jo `sseClient.subscribeToExecution`) siivotaan. Sen sisään istutetaan `Mutation<void>` rutiinit rehydration-logiikalle.

3. **`ExecutionRecord` jne. Domain Models (Frontend Dart)**
   `Map<String, dynamic>? results` heitetään roskiin. Dart Modelien on mallinnettava litteä `ReportDataDTO` yhdessä `OutputProfile` ja `ReportLayoutDTO` taulukoiden kanssa. Tyyppiturvallinen, ei dynaaminen.

4. **Graceful Degradation (The Omni-Channel Guarantee)**
   Koska Flat MVC on silti armoton data-anomalioille, Frontendin "tyhmät" piirturit (esim. 1D_Gauge tai Matrix) on peitettävä Dartin *SafeCast* purkuun ja `SizedBox.shrink()` turvatulppaan vääristyneiden kenttien varalta. Vika ei koskaan saa aiheuttaa punaista Exception Screeniä (Red Screen of Death). Frontend raportoi mykän ohitetun virheen LoggerServicellä pilvitelemetriaan (Dual-Reporting).

---

## 6. Uusi V3 QA & Testausstrategia (The Final Gauntlet)

1. **The Database Wipe:** 
   Koska Backendin V3 Big Bang tuhosi vanhan `results` muotoilun, myös UI devaajat poistavat TinyDB:n datan armottomalla viillolla, estäen vanhojen korruptoituneiden UI-mallien kummittelemisen. App lähtee liikkeelle puhtaalta pöydältä.

2. **Isolate Parse Test (Jank-Killer):** 
   Ladataan giganttinen gigatavun RAG-analyysi (tai 10,000 sanan esseerapsa) ruudulle. Flutter Performace DevTools ei saa näyttää yhdenkään frame:n putoavan punaiselle (Lopeta Main Thread Jank JSON-deserialisaatiossa).

3. **Graceful Degradation Pitfall:** 
   Injektoidaan HTTP Mockilla osittain korruptoitunut `ReportDataDTO` (esim. `ReportAxisDTO.value` on tuntematon olio vahingossa). UI Renderöijän on reagoitava ohittamalla tämä graafi jättäen sen tilalle tyhjää, ja muun näkymän on reagoitava vahvasti ilman jäätymistä. Konsoliin on tulostuttava tästä hiljainen the Dual-Reporting vikaloki.

4. **Rehydration UX Test:**
   Laukaistaan Failed-tila työnkulussa manuaalisesti. `GlobalErrorView` aukeaa, Actionable Hint nappi näkyy, klikkaus asettaa sivun viiveettä `Loading` -tilaan optimisesti (Riverpod Mutation), ja Backend ottaa herätyksen vastaan (Rehydrating...). Valmis tuotantoon.
