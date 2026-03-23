# EPIC: V3 Flutter Frontend Adaptation (The Event Sourcing Gap)

## 1. Yhteenveto (Summary)
V3-moottorin siirtyessä keskitettyyn Event Sourcing ja "The Flush Strategy" (Checkpointing) -arkkitehtuuriin, Frontend menettää aiemman jatkuvasti yli-kirjoitetun `ExecutionRecord.results` sanakirjatilan sekä vanhan pollausmallin. Tämä Epic määrittelee Mandaattien (The Zero-Compromise Pledge) mukaisen polun, jolla Flutter-asiakassovellus sopeutetaan uuteen `TraceEvent` -lokiin säilyttäen optimointinsa, tiukan reitityksen (GoRouter) sekä UI-reaktiivisuutensa (Riverpod 3.0).

## 2. Taustakonteksti: Mikä ihmeen V3 Big Bang? (Frontendin "Need-To-Know")
Koska tämä Epic on täysin itsenäinen The Zero-Compromise Pledgen manifesti, tässä on tiivistelmä siitä, miksi backend ylipäätään uudistettiin ja miksi Flutter-tiimi joutuu sopeutumaan:
* **Event Sourcing (Mutaation kuolema):** V3 Backend ei enää ylikirjoita tietokannan rivejä askeleiden välillä (se hylkää vanhat mutatoituvat `results` ja `progress` sanakirjat). Sen sijaan moottori tallentaa ajon puhtaana append-only -lokina. Ajon tilana on lopulta satoja/tuhansia rivejä pitkä lista `TraceEvent` -objekteja.
* **The Flush Strategy (I/O-Tukoksen Esto):** Koska tietokannat (Firestore 1 write/sec ruuhka) kaatuisivat massiivisista mikrotallennuksista askeleiden aikana, backend puskuroi ne lokaaliin muistiin. Vasta kun looginen työnkulun solmu päättyy (tai laukeaa virheeseen), backend "flushaa" event-muistipuskurin yhtenä isona taulukkona kantaan (Checkpointing). Iso tiedosto (yli 100KB raja) offloadataan automaattisesti Blob-storageen (Cloud Storage). 
* **Rehydration (Fail-Fast Toipuminen):** Jos GPT/Claude putoaa timeouteihin tai validointiin pamahtaa Pydantic-virhe, backend katkaisee ajon välittömästi the Fail-Fast mallin mukaisesti tallentaen virheen ja keskenjääneen statuksen suoraan append-only lokiin. Työnkulkua *ei menetetä*. Frontend voi milloin tahansa kutsua `resume` / Rehydration-rajapintaa pelkällä id:llä, jolloin backend lukee massiivisen lokinsa, "taittaa" tilan takaisin (fold_trace) ja jatkaa ajon salamana eteenpäin ilman redundantteja API-kutsuja LLM:lle.

## 3. Tavoitteet (Objectives)
- **Zero-Math UI Säilytys:** Frontend ei ryhdy itse raskaaseen Event-Sourcing datan REDUCE-murskaukseen (fold_trace), vaan säilyttää "Tyhmän ja Laiskan" luonteensa. UI nojaa Backendin tarjoamaan The Translation Schema Doctrineen (BFF).
- **Saumaton Rehydration (Ajosta Toipuminen):** Kaatuneesta (Fail-Fast) tilasta palauttaminen käyttöliittymässä ei enää merkitse ajon nollausta. Käyttäjälle tarjotaan Actionable Hint -painike "Jatka ajoa", joka ohjaa ID:n suoraan moottorin rehydrationiin.
- **Timeline Streaming (Optimointi):** Vanha `DatabaseProgressTracker` -pollaus kuolee. UI:n on päivitettävä visuaalista edistystään puhtaaseen Event-Append -virtaukseen nojaten (striimaus/täsmävedot).

## 4. Vaiheet (Execution Plan)

### Vaihe 1: Datan Luku ja BFF (Backend-For-Frontend) Yhteentoimivuus
*   **Toimenpide:** Refaktoroidaan Flutterin data-adapterit (DTO:t). Frontend lakkaa katsomasta `results` -sanakirjaa. Se mukautetaan kuluttamaan dynaamisesti taitettua (folded) lukumallia esikäsiteltyjen rajapintojen kautta. Jotta UI ei jäädy raskaiden RAG-kontekstien JSON-purussa (Main Thread Jank), JSON-deserialisointi siirretään Dartin **Isolate** -taustasäikeisiin. Suuren kuormituksen (esim. jatkuva vuoto) aikana käytetään **Isolate Pool / Worker Thread** -arkkitehtuuria jatkuvan luomisen/tuhoamisen ja roskienkeruun (GC) välttämiseksi.
*   **Rationale:** V3 Mandaatin `Zero-Math UI` kieltää Frontendin yrittävän manipuloida isoa logia. Koko `TraceEvent` -käsite pidetään yksinomaan Python-backendin salaisuutena.

### Vaihe 2: Rehydration UX ja Human-in-the-Loop Mutaatiot
*   **Toimenpide:** Navigaatiossa tunnistetaan infrastruktuurivirheiden (`FAILED` -> `REHYDRATING`) lisäksi valinnainen **`SUSPENDED_FOR_INPUT`** (Human-in-the-Loop) -tila, jos siemenkannan arkkitehti on näin määritellyt. Rehydration palvelee siis sekä virheistä toipumista "Jatka"-napilla että tarkoituksellista pysäytystä käyttäjän syötettä odotettaessa. Oletuksena HITL on disabloitu työnkuluissa.
*   **Toteutus:** Luodaan Riverpodiin `resumeExecutionMutation` (virheestä toipuminen) sekä tarvittaessa `resumeWithInputMutation` (jatkaminen syötteellä). Molemmat hyödyntävät Optimistic Updatea siirtäen UI:n välittömästi "Running/Rehydrating" -tilaan.

### Vaihe 3: Event-Virtauksen Seuranta (Signal & Fetch)
*   **Toimenpide:** Siirrytään raskaasta tietokannan pollausmallista kevyempään ja turvallisempaan **Server-Sent Events (SSE)** -virtaukseen hyödyntäen tarkennettua **Delta Signal & Heavy Fetch** -arkkitehtuuria Live UI:n mahdollistamiseksi.
*   **Toteutus:** Ristiriita ratkaistu: SSE-putki *välittää Live-päivitykset (esim. tekstistriimauksen tai askeleen nimen muutoksen)* ohuina Delta DTO -paketteina (jotka sisältävät `trace_version` -leiman Eventual Consistency -suojaukseen). Massiivista yli 100KB historiallista Lukumallia ei koskaan työnnetä SSE:n läpi (The Payload Trap). Pääasiallinen massiivinen Lukumalli noudetaan HTTP GET -kutsulla ("Fetch") vasta kriittisissä taitekohdissa, välttäen kisaustilat `?min_version=X` -suojalla varustetun BFF-kutsun ja Long Pollingin avulla.
*   **Mobiiliverkon Katkokset:** Kun (esim. hississä) mobiililuuri hukkaa verkon ja SSE-yhteys katkeaa (ja palaa vähän ajan päästä takaisin), mobiilisovellus lähettää automaattisesti **"Catch-up Fetch"** täyden HTTP GET -kutsun välittömästi yhteyden palautuessa estääkseen UI:n jäätymisen ikuiseen pimentoon niiden PING-signaalien osalta, jotka katosivat kyberavaruuteen kätkon aikana.

### Vaihe 4: RFC 7807 ja Actionable Hints (Global Error Handling V3)
*   **Toimenpide:** Varmistetaan manifestin (Sääntö 6) mukainen virheenhallinta V3-putkessa. Kun Frontendin BFF Fetch palauttaa `TimelineDTO` -lukumallin, jossa askeleen tila on FAILED (Backend on tuottanut `ErrorTraceEvent`in), Frontendin Dart-parseri purkaa sen suoraan tyyppiturvalliseksi `AppException` -Freezed-luokaksi sivuuttamatta rajapintasopimusta.
*   **Toteutus:** Backendin tiukka virhekoodi (esim. `error_code: "TOOL_EXECUTION_FAILED"`) ei koskaan tuota asiakkaalle raakaa punaista kooditekstiä. Sivun `GlobalErrorView V3` ottaa kopin ja kääntää virheen paikallisesta `.arb` -tiedostostaan suoraan asiakkaalle ymmärrettäväksi **Actionable Hintiksi** (esim. *"Asiantuntija-agentti ei saanut yhteyttä palvelimeen. [Yritä jatkaa ajoa (Resume)]"*).

## 5. Konkreettiset Vaikutukset Koodiin (Fyysisesti vahvistetut tiedostot)

Koska Frontend käyttää jo The De-Generator Mandaattia (lukee suoraan SSE-striimin `Map<String, dynamic>` dataa ilman DTO-generointia), muutos iskee lokaalisti näihin olemassa oleviin tiedostoihin:

**1. `client_app_v2/lib/features/execution/views/execution_view.dart` (Live UI)**
*   **Mitä:** Riveillä 71-75 koodi yrittää lukea `record['results']` ja `record['step_states']` avaimia piirtääkseen ruudun. Nämä avaimet häviävät tietokannasta Event Sourcingin myötä.
*   **Miten:** Komponentti koodataan uusiksi lukemaan append-only `execution_trace` taulukkovirtaa (tai BFF:n taittamaa näkymää). Samaan moduuliin lisätään Failed-tilaan visuaalinen "Jatka ajoa" (Rehydration) liipaisin.

**2. `client_app_v2/lib/features/execution/controllers/execution_controller.dart`**
*   **Mitä:** Koodikanta on jo valmiiksi Event Sourcing -yhteensopiva! Riveillä 86 alkaen Controller tilaa jo SSE-striimin (`sseClient.subscribeToExecution`). Se osaa ottaa live-päivitykset täydellisesti vastaan raskaiden pollausluuppien sijaan.
*   **Miten:** Controlleriin lisätään Riverpodin mukainen `Mutation<void>` uutta `resumeExecution` Rehydration-kutsua varten säilyttäen Optimistic Update viiveettömyys.

**3. `ExecutionRecord` Model (Frontend Dart)**
*   Dartin arkkitehtuuriluokista pudotetaan `Map<String, dynamic>? results` kokonaan pois, **eikä tilalle tuoda koskaan litanniaa raaoista `TraceEvent` -objekteista**. Zero-Math UI -mandaatin mukaisesti Frontend saa vain tyyppiturvallisen, palvelimen esitaittaman Lukumallin (Read Model / DTO). Frontendin Omni-channel renderöinti (Defensiivinen SafeCast) varmistaa yhä `SizedBox.shrink()` avulla, ettei yksittäisen avaimen puuttuminen kaada näkymää.

**4. `client_app_v2/lib/shared/widgets/execution_timeline.dart`**
*   **Mitä:** Nykypäivänä odottaa vanhan V2-moottorin `step_statesList` rakennetta litteänä. Se uusitaan sietämään Backendin (BFF) valmiiksi taittamaa litteää **TimelineDTO** -lukumallia. Ristiriita korjattu: Frontend ei ota koskaan vastaan raakoja `TraceEvent` -merkintöjä aikajanalleen, vaan täysin "Zero-Math" -valmiin abstraktion askeleiden kulusta.

**5. Graceful Degradation (The Omni-Channel Guarantee)**
*   Koska Event Sourcing sallii massiivisen lokin kasvun, Frontend ohittaa vioittuneet yhden askeleen "Sudenkuoppa"-eventit `SizedBox.shrink()` turvatulpan avulla silloinkin, kun backend BFF:n `fold_trace` parsinnassa tapahtuu odottamaton häiriö. Red Screen of Death on yhä ehdottomasti kielletty. 
*   **Dual-Reporting V3:** Niin ikään säännön 6 mukaisesti: vaikka Frontend väistää osittaisen data-korruption hiljaisesti (`SizedBox.shrink()`), sen on pakko käydä kiinni lokiin taustalla. Frontendin on nostettava rakenteellinen virhe (esim. `TRANSLATION_FAILED`) etätelemetriaan (Riverpod Logger -> Logfire/Sentry) mykkänä tapahtumana, jotta vika voidaan jäljittää backend-BFF -rajapintaan.

## 6. Tuhoava Päivitys ja Laadunvarmistus (QA)

**Tietokannan Tyhjennys (Database Wipe):**
Aivan kuten Backendissä, tämä päivitys on tuhoava vanhalle datalle. Vanhat lokaalit ajot, jotka luottivat ylikirjoitettaviin `results` ja `progress` sanakirjoihin, **tuhotaan puhtaasti viiltämällä Firestoresta ja TinyDB:stä** siirtymän yhteydessä, jottei Frontendin uusi `TimelineDTO`-logiikka törmää rikkinäiseen ja tuntemattomaan legacy-dataan. Frontend alkaa puhtaalta pöydältä.

**Frontendin QA ja Testausstrategia:**
1. **Isolate Parse Test (Jank-Killer):** Syötetään tahallisesti giganttinen gigatavun kokoluokkaa oleva JSON-lukumalli sovellukselle painikkeen takaa. Varmistetaan Flutter Performace DevTools -profiililla, ettei UI-thread (Main loop) tiputa yhtäkään 60fps/120fps framea JSON-purkamisen aikana (tämän kokeen onnistuminen todistaa onnistuneen purun taustasäikeessä `Isolate.run` tai `compute` -funktioiden kautta).
2. **Graceful Degradation Test ("Sudenkuoppa"):** Syötetään tahallisesti Frontendiin HTTP GET -väärennöksellä BFF-lukumalli (`TimelineDTO`), josta on poistettu täysin kriittisiä kenttiä tai jonka sisällä on odottamaton tuntematon tietotyyppi täysin väärässä paikassa. Varmistetaan, että Omni-Channel SafeCast ei aiheuta Red Screen of Death -kaatumista, vaan palauttaa vioittuneen näyttäsolun kohdalle vain turvallisen `SizedBox.shrink()` -tyhjyyden kirjoittaen samalla konsoliin asiallisen `logger.error` viestin. Sovelluksen muun osan on pysyttävä täysin reaktiivisena.
3. **Rehydration UX Test ("Kaadu ja Herää"):** Simuloidaan Backendiltä tuleva valmiiksi `FAILED` -tilassa oleva ajo. Testataan visuaalisesti, että ajo ei renderöidy sovelluksessa pelkkänä pelottavana punaiseena Error-lauluna. Sen sijaan on löydyttävä selkeä "Yritä jatkaa ajoa" -toimintapainike (Rehydration Hint). Painalluksen on välittömästi mutatoitava lokaali Riverpod-tila viiveettömästi `Loading/Running` -asentoon (Optimistic Update) ilman verkkoviiveen odottelua, samalla kun varsinainen herätyspyyntö lähtee taustalla.
