# **SYSTEM ARCHITECTURE MANIFESTO (2026 Edition)**

**PROJECT**: Google Antigravity (Monorepo: Python Backend + Flutter Client)
**STATUS**: Phase 9 (Hardening & Standardization)

> [!CAUTION]
> **SUPREME ARCHITECTURE LAW (V2)**
> Tämän dokumentin yläpuolella on yksi ylin, ohittamaton auktoriteetti: **`docs/Flutter Frontend V2 Suunnitelma.md`**.
> Mahdollisissa ristiriitatilanteissa tämän manifestin, ohjeistuksien (KI) tai minkä tahansa muun dokumentin ja **V2 Suunnitelman** välillä, **V2 Suunnitelma määrää aina absoluuttisesti järjestelmän suunnan ja säännöt.**

> [!IMPORTANT]
> Tämä dokumentti on koko ohjelmistoprojektin perustuslaki (V2 Suunnitelman alaisuudessa). Kaikki tekoälyagentit (kuten Antigravity Assistant) ja ihmiskehittäjät on sidottu näihin absoluuttisiin sääntöihin.

---

## 🛑 1. PRE-FLIGHT CHECKLIST & TOOLING (MANDATORY)

### 1.1 Baseline Dependencies (Latest Stable Mandate)
Täyttä tukea 2026-arkkitehtuurille ei saavuteta legacy-kirjastoilla. Pysy näissä tai uudemmissa:
* **Backend (Python 3.14.2+, FastAPI 0.128+)**: `pydantic 2.12.5+`, `litellm 1.81.3+`, `tenacity 9.1.2+`.
* **Frontend (Dart 3.11, Flutter)**: `flutter_riverpod ^3.1.0`, `go_router ^17.0.1+`, `freezed ^3.2.3`.

### 1.2 Banned Patterns
| Area | Modern Requirement (MANDATORY) | Banned Pattern |
| :--- | :--- | :--- |
| **State** | Use `@riverpod` (Generator) + `ref.watch()` | `ChangeNotifier`, `StateProvider`, manual `Provider` |
| **Routing** | Use `GoRouteData` (Type-safe classes) | Raw strings: `context.push('/home')` |
| **API** | Use `Annotated[Dep, Depends()]` | `params: Dep = Depends()` (Old syntax) |
| **Models (Backend)** | Use `model_validate`, `model_dump` | `.parse_obj()`, `.dict()` |
| **Domain Data (Frontend)** | `Freezed` for Local UI State (User, Settings). Raw `Map<String, dynamic>` for Dynamic API Payloads (De-Generator Policy). | Pure `Map<String, dynamic>` for Local State (Too slow to type and parse) / Freezed for BFF ViewModels (Breaks Zero-Deploy). |

### 1.3 Routine Quality Gates (Verifications)
Älä koskaan merkitse työtä valmiiksi tarkistamatta sitä manuaalisesti laadunvarmistustyökaluilla:
* **Backend**: `ruff check . --fix` AND `mypy .` (Strict typing).
* **Frontend**: `dart run custom_lint` AND `dart run build_runner build -d`.

### 1.4 Environment Constraints
* **Windows 11**: Koodia ajetaan PowerShellissä. Määritä Pythonissa aina `encoding="utf-8"`.
* **Debugging**: Ohjelmaloki ja virheet kulkevat `backend_debug.log` ja `client_debug.log` tiedostoihin. Kun etsit virhettä, lue nämä tiedostot ensin.

---

## 🏛️ 2. THE ZERO-COMPROMISE PLEDGE (System Core Principles)

**"Production Quality, Day One."** Laadusta, turvallisuudesta tai eheyden tarkistuksista ei jousteta missään tilanteessa.

### 2.1 The Fail-Fast Boundary
* Ydinlogiikassa (Core Engine, Database, Domain) järjestelmän **ON KAASTUTTAVA VÄLITTÖMÄSTI** (raise Exception) virheellisen tilan tai puuttuvan datan kohdalla.
* **BANNED**: `try-except pass` ja tyhjän datan (`None`, `[]`, `{}`) hiljainen palauttaminen piilottavat upstream-virheet ja estävät debuggaamisen.

### 2.2 Root Cause Mandate (Ei oireiden paikkausta)
* Oireita ei paikata pintapuolisesti `if x is None: return` -tarkistuksilla tai `.get('field', default)` defensiivisillä oletuksilla.
* Etsi ja korjaa datan alkuperä. Miksi data on viallinen? Korjaa lukija tai generoija, älä laita putkeen purkkaa.

### 2.3 Strict Typing & No Defaults
* Domain-malleissa ei saa olla implisiittisiä oletusarvoja pakollisille kentille (esim. `score: float = 0.0` on kielletty, ellet ole matemaattisesti aivan varma oletuksen alkuperästä).
* Pydantic V2 on käytössä tilassa `ConfigDict(strict=True)`. Tyyppipakotuksia ei tehdä lennosta (esim. ei merkkijonoa `"1"` numerokenttään `1`).

### 2.4 Deterministic Execution Mandate (Python Authority)
* LLM (Tekoäly) on probabilistinen; Python on deterministinen. 
* Jos loogisen operaation (Matematiikka, lajittelu, deduplikointi, tunnisteiden luonti) voi tehdä deterministisesti Pythonissa (`BaseAgent.post_process()`), sitä **EI KOSKAAN** delegoida tekoälylle promptiin.

---

## 💾 3. ARCHITECTURE & DATA LIFECYCLE

### 3.1 Single Source of Truth (SSOT) & Domain Service Layer (MANDATORY)
* **API Routers MUST be "Anemic":** FastAPI reitittimet (esim. `users.py`, `studio.py`) saavat sisältää vain HTTP-pyynnön parsinnan (Pydantic). 
* **NO RAW CRUD IN ROUTERS:** Reititin ei koskaan saa kutsua suoraan `repository.create()` tai `repository.get()`, eikä se saa sisältää käyttöoikeuslogiikkaa (esim. `if current_user.role == "ROOT"`). Kaikki tietokanta- ja liiketoimintalogiikka (etenkin Tenant Isolation, RBAC ja Last Admin Guard) **ON PAKKO** reitittää aina kerroksen 2 (Domain Service Layer, esim. `AuthServiceDep`, `StudioServiceDep`, `ExecutionServiceDep`) kautta.
* **Miksi?** Järjestelmää ajetaan myös ohjelmallisesti tausta-ajoilla (esim. `worker.py`), jotka eivät reitity API:n kautta. Service Layer on backendin ainoa Single Source of Truth luvitukselle ja datan eheyksille.

### 3.2 Dual Backend Parity
* Kaikki tietokantaa koskevat CRUD-muutokset on peilattava ja päivitettävä säännönmukaisesti kumpaankin ajuriin: `repository.py` (TinyDB) ja `firestore_repo.py` (Cloud).

### 3.3 Hybrid State Architecture
* Tapahtumaloki (`TraceEvent`) on totuuden lähde (Immutable).
* Työtila (`ExecutionRecord.results` / Blackboard) on nopea ja editoitava hetkittäinen tilanne. Molempia täytyy ylläpitää, kun agentti tekee siirron.

### 3.4 Reliability Strategy (Timeout)
* Kaikilla ulospäin lähtevillä verkkopyynnöillä on pakotettu aikakatkaisu (Timeout). Järjestelmä ei saa hirttää kiinni (Zombie).
* Uudelleenyritys (Retry) hallitaan infrastruktuurissa asynkronisilla kirjastoilla (kuten `Tenacity`), ei etupäässä käyttäjän toimesta.

### 3.5 Seed Data Protocol (Tietokannan hallinta)
**ERITTÄIN TÄRKEÄ SÄÄNTÖ:** Tietokantaa (TinyDB) ei koskaan muokata lennosta tai ohittaen Seed-prosessia kehityksessä. 
Aina kun tietokannan asetuksia, prompti-lohkoja tai askeleita muutetaan:
1. **Muokkaa alkuperäistä JSONia:** Tee rakenteellinen muutos ensin tiedostoon `backend_v2/seed/seed_data.json`.
2. **Kopio (Backup):** Aina ennen isoja muutoksia on varmistettava, että kopiota pidetään `backend_v2/seed/backups/` -hakemistossa turvassa vääristymiseltä.
3. **Siemennys (Re-Seed):** Vasta tämän jälkeen varsinainen paikallisen kannan päivitys ja synkronointi suoritetaan ajamalla käsky: `python backend_v2/seed/run_seed.py local`.
Tämän ohjeen kiertäminen ja kannan (`db_v2.json`) sorkkiminen lennossa korruptoi järjestelmän ID:t korjauskelvottomiksi.

---

## 🐍 4. PYTHON BACKEND MANDATES

### 4.1 Framework Features
* **DI (Dependency Injection)**: Pakotettu `Annotated[Type, Depends()]` -syntaksi. Suojaa tyypit ja poistaa "Any" -vuodot reiteistä.
* **Asynk/Synk Rajoite**: Jos reitti lukee vain TinyDB:tä (joka on luksattu blocking-ajuri), reitin määritys tulee olla puhdas `def`. Jos tiedonlähde on Cloud (Firebase), käytä asynkronista `async def`. FastAPI optimoi nämä omiin lankapoolihinsa.

### 4.2 API Boundary & Schema-First (No-ORM)
* JSON-datansiirtoon on kiellettyä käyttää `dict` tai tyypittämätöntä datakenttää HTTP-rajapinnassa. Request/Response -kappaleet ovat aina vahvasti rajattuja Pydantic-malleja (`response_model`).
* **The Three Pydantic Boundaries (API, Service, Middleware)**: 
  1. **API Ingestion (Generic IN -> Strict OUT)**: Kun data saapuu ulkomaailmasta (Web/Flutter) sisään Backendin API-reitittimiin (`backend_v2/api/`), se ON PAKOTETTAVA välittömästi tiukkaan Pydantic DTO -malliin ennen kuin sitä saa siirtää Service-kerrokselle. Service-kerros ei ota vastaan tyhmiä sanakirjoja.
  2. **Service Layer (Strict IN -> Strict OUT)**: Liiketoimintalogiikka (`backend_v2/services/`) on järjestelmän ehdoton portinvartija. Se ottaa API:lta vastaan vain puhdasta Pydanticia. Kaikki tietokannasta (`repository`) haettava data on myös VÄLITTÖMÄSTI hydratoitava Pydantic-malleihin (`Model.model_validate(data)`) ennen kuin logiikkaa suoritetaan.
  3. **Middleware (Strict Context -> Generic Data OUT)**: Koko post-hook arkkitehtuuri (`backend_v2/hooks/`), DAG-putkisto ja tallennuslokit toimivat päinvastoin datan suhteen: ne ovat 100% litetyssä Sanakirja-maailmassa. Middlewaren sisään EI SAA kirjoittaa Pydantic-fallbackeja kognitiiviseen dataan (esim. `hasattr(item, "model_dump")`). Agentit pakottavat Pydanticin luontihetkellä (Fail-Fast), mutta DAG takaa, että eteenpäin hookeille siirrettävä tulosdata on aina turvallisesti riisuttua `.model_dump(mode="json")` muotoa. **KUITENKIN: Ohjelman sisäiset riippuvuudet ja kontrollimuuttujat (esim. `_sys_repository`, `execution_id`) EIVÄT OLE sanakirjadataa, vaan ne on pakastettava tiukasti tyypitettyyn `HookExecutionContext` -objektiin Fail-Fast injektion ja tyyppiturvallisuuden takaamiseksi.**
* **No-ORM**: Ei SQLAlchemyä. Pydantic kuvaa suoraan tietokannan dokumenttirakenteen (NoSQL) 1:1.

### 4.3 Null-Safety v2.12
* API-rajapinta ei halua palauttaa asiakkaalle tyhjän listan tilalla `null`. Käytä listoille Pydanticissä automaattisesti reagoivaa syntaksia: `Field(default_factory=list)`.

### 4.4 Date Handling (Temporal Standard)
* Talletus aina formatoituna aikaleimana UTC-ajassa (`datetime.now(timezone.utc)`). API:ssa muunnetaan muotoon `isoformat()` automaattisesti.

---

## 💙 5. FLUTTER CLIENT MANDATES

### 5.1 Riverpod 3.0 State & Optimistic Updates
* Luovu "Odotan vastausta 2 sekuntia - spinneri pyörii" UX-suunnittelusta.
* Kaikkiin tilamuutoksiin käytetään **Optimistista Päivitystä** (Tila paikallisesti = Päivitetty jono $\rightarrow$ Lähetä serverille $\rightarrow$ Jos ei onnistunut, peruuta näyttö tilaan x). Muuten käyttöliittymä reagoi liian viiveellä (Network latency hit).

### 5.2 GoRouter & Declarative UI
* Sovelluksen sisälle navigoiminen tapahtuu luokkapohjaisesti `GoRouteData`. Raakamuotoisten `/` ja `/login` reittien kirjoittelu UI:n sekaan on bugi.
* **Guard Clauses:** Reitinvalintalogiikka (kuka saa mennä minnekin ja tila) keskitetään yksinomaan reitittimen `redirect`-funktioon, ei manuaalisesti widgetien `build()`-luokkiin.
* Unohda `if(isLoading) return Spinner()`. Tieto tulee syleillä muodossa `ref.watch(provider).when(data: ..., loading: ..., error: ...)`.
* **Relaatiodatan Hallinta:** Vältä massiivisia `Future.wait` monoliitiveja asynk-tarpeissa. "Yhden providerin tulisi ladata yksi asia." litteästi ja natiivisti erillään muista.

### 5.3 Concurrency & Performance (Dart 3.11)
* Raskaat Backendistä tuodut ylisuuret JSON-rakenteet tai datan transformoinnit **SIIRRETÄÄN VÄKISTEN** erilliseen säikeeseen: `Isolate.run(...)`. Vanha Flutterin `compute` -funktio on poistettu näistä tehtävistä käytöstä.
* **Tausta-Tallennus:** Sovelluksen asetusten (Theme, Kieli) lukeminen hyödyntää `SharedPreferencesAsync`-rajapintaa, joka estää päälangan (UI Thread) hidastumisen I/O-operaatioiden aikana.

### 5.4 UI/UX Responsiveness & Theming
* **Responsiveness Breakpoint:** Järjestelmä asettaa ehdottoman rajan `600dp` pöytäkone-/tablettikokoonpanon (`NavigationRail`) ja mobiilin (`NavigationBar`) välille.
* **Teemoitus:** App-teema käyttää yksinomaan dynaamista, automaattisesti generoituvaa `FlexColorScheme` -kirjastoa. Manuaalinen värien ja elementtien hardkoodaus suoraan `ThemeDataan` on kielletty, ellei sitä ole otettu suoraan kontekstista `Theme.of(context)`.

### 5.5 Riverpod Hybrid Caching Strategy (SWR & TTL)
* Järjestelmän listat ja lomakkeet EIVÄT käytä pelkkää aggressiivista `autoDispose`:a (mikä aiheuttaa hidasta navigointia), vaan tilaa hallitaan älykkäästi kahdella mallilla:
  1. **Lukunäkymät (Luku-Listat, Dashboard):** Käytetään SWR (Stale-While-Revalidate) -mallia. Riverpod-provider pidetään elossa (`ref.keepAlive()`), jolloin paluunavigointi on välitöntä nollaviiveellä. Tiedot päivittyvät taustalla huomaamattomasti (Silent Background Fetch) ilman blokkaavia latausanimaatioita.
  2. **Syöttönäkymät (Forms, Uudet Analyysit):** Käytetään TTL (Time-To-Live) välimuistia. Keskeneräiset lomakkeet säilytetään aktiivisina ram-muistissa vain lyhyen turva-ajan (esim. 3 minuuttia) poistumisen jälkeen (`ref.onDispose` Timerilla), jolloin vahinkonavigointi ei hukkaa työtä. Jos käyttäjä palaa myöhemmin uudestaan, lomake on nollautunut automaattisesti roskista tyhjältä pöydältä aloittamista varten. Lomakkeille tarjotaan aina myös manuaalinen Nollaa/Tyhjennä -painike.

### 5.6 UI Mutations Mandate (Mandaatti: Riverpod 3.0 Mutations)
* Kaikki **sivuvaikutukset (Side Effects)** – asiat kuten painikkeiden painallukset, lomakkeiden tallennukset (POST), tietuieden poistamiset – ovat ohjelmistossa **PAKOTETUSTI** hallittava kokeellisen (mutta stabiilin) Riverpod 3.0 `Mutation<T>` objektin kautta.
* **Käytäntö:** ÄLÄ tee enää manuaalisia state-lippuja kuten `bool _isLoading` tai hyödynnä sokeasti `AsyncLoading()` Notifiereissa tallennustoimenpiteitä varten. Määrittele sen sijaan napille tai lomakkeelle dedikoitu `final executeXMutation = Mutation<void>();`
  * UI voi lukea dynaamisesti ja turvallisesti lomakkeen tilan: `MutationIdle`, `MutationPending` (Näytä spinneri), `MutationSuccess` (Näytä Toast ja onnistuminen) tai `MutationError` (Error hint).
  * Painikkeet laukaisevat suorituksen tyyppiturvallisesti: `mutation.run(ref, (tsx) async { await tsx.get(provider.notifier).saveAction(); });` 

---

## ⚠️ 6. ERROR HANDLING CONTRACT (GLOBAL ERROR HANDLING V3 / RFC 7807)

**SINGLE SOURCE OF TRUTH**: `backend/exceptions.py` & `client_app/lib/core/error/app_exception.dart`

### 6.1 Strict RFC 7807 Pattern (AppException)
Backendissä ei saa enää ikinä esiintyä paljaita (`ValueError` / `HTTPException`) nostoja rajapinnoilla. Kaikki poikkeukset tulee heittää paketoituna `AppException` tai sen semanttisilla aliluokilla.
**Frontend V3 Mandaatti:** Flutter-asiakas on velvoitettu mallintamaan nämä virheet 1:1 `AppException` Freezed-luokkana. Kun HTTP-virhe (Dio) saapuu, ErrorInterceptor **PURSII** RFC 7807 "Problem Details" payloadin tiukasti tähän Freezed-malliin, joka sisältää resoluutiotasot (`errorCode`, `status`, `detail`). Paljaita DioException tai String-virheitä ei saa päätyä käyttöliittymäkerrokselle asti.

### 6.2 Dual-Reporting & Telemetry Mandate
Ainoa sallittu tapa ottaa virhe kiinni ja heittää se ylemmäs on **Kaksinkertainen Raportointi** (Dual-Reporting).

**Backendissä:** Ensin rakenteellinen printti serverille (`logger.error(..., exc_info=True)`), sitten tyyppiturvallisen poikkeuksen nosto `AppException(error_code=...)`.
**Frontendissä:**
1. Kaikki kiinniotetut HTTP-verkkovirheet, mutaatio-epäonnistumiset ja `ErrorBoundary`-poikkeukset on **kirjattava Riverpod-LoggerServiceen**.
2. LoggerService välittää kriittiset virheet asynkronisesti Backendin etätelemetria-päätepisteeseen (Logfire/Sentry -injektio), kantaen mukanaan asiakkaan asiointikielen ja session ID:n.

```python
# Backend Esimerkki
try:
    result = some_operation()
except Exception as e:
    logger.error(f"[Component] {ErrorCodes.VALIDATION_FAILED.name}: Error: {e}", exc_info=True)
    raise AppException(message=..., error_code=ErrorCodes.VALIDATION_FAILED, ...) from e
```

### 6.3 Non-Fatal Errors (Sallitut läpimenot / Graceful Degradation)
Myös silloin, kun virheen tai tietyn poikkeuksen annetaan mennä läpi ilman koko sovelluksen kaatumista (esim. poikkeuksen nappaaminen SDUI-renderöijässä, jotta yksi viallinen JSON-noodi ei kaada koko näkymää), **käytetään lähes täsmälleen samaa rakenteellista virheenhallintaa ja lokitusta** kuin fataaleissa tilanteissa. Pelkkää hiljaista ohittamista (`catch: return fallback()`) ei hyväksytä koskaan vikatilanteissa. 

Tyypillinen esimerkki tästä on Frontendin BFF-widget (Backend-For-Frontend): jos backendistä tullut payload on osittain korruptoitunut ja yksittäisen komponentin rakentaminen failaa, näytämme näkymässä `SizedBox.shrink()` (Graceful Degradation). VAIKKA sovellus ei kaadu, komponentin on pakko ampua vahva virheloki osoittamaan, että fail-fast periaate toteutui osittain ja data oli viallista.

**Käännösvirheet (TRANSLATION_FAILED):** 
Uusi The Translation Boundary Hook nojaa LLM:ään kääntääkseen dynaamisia tekstejä (kuten `scratchpad`) asiointikielelle lennosta. Jos käännöspalvelu kaatuu tai timeouttaa, sovellus suorittaa Graceful Degradationin: se logittaa rakenteellisen `TRANSLATION_FAILED` -virheen, mutta tulostaa UI:hin datan sen **alkuperäisellä kielellä** (englanniksi) suojellakseen käyttäjäkokemusta ja sallien arvioinnin jatkumisen. Sovelluskokemus ei koskaan saa kaatua rikkoutuneeseen kääntäjään.

**Esimerkki (Dart / Flutter):**
```dart
try {
  return buildDynamicWidget(jsonData);
} catch (e, st) {
  // 1. Log with STRUCTURED FORMAT (esim. VALIDATION_FAILED tai TRANSLATION_FAILED) vaikka tilanteen annetaankin mennä läpi
  logger.error('[BFF Builder] ${ErrorCodes.VALIDATION_FAILED}: Widget render error: $e', e, st);
  // 2. Fallback UI, mutta vain koska backendin dataongelma ei saa rikkoa koko puhelinta
  return const SizedBox.shrink(); // Tai käännösvirheessä: palauta alkuperäinen englanninkielinen teksti
}
```
### 6.4 Mapping Exceptions to the UI (Actionable Hints & GlobalErrorView)
* Backendin virhedata (`AppException`) tuodaan sellaisenaan koodina UI:hin (`"VALIDATION_FAILED"`), ilman käännöstä.
* UI lokalisoi viestin asiakkaalle `AppExceptionX` laajennuksessa (`app_error_ext.dart`). Sanomaan kirjataan **miksi kävi näin ja mitä käyttäjän pitäisi yrittää seuraavaksi (Actionable Hint).** Ei kuitteja mallia "Tapahtui virhe" tai "Tuntematon virhe". *Kaikki* backend-virheet kuvataan asiakkaalle Actionable Hinteiksi `.arb` -tiedostoissa.
* **Standardisoitu UI-Komponentti (GlobalErrorView V3):** Kaikki virheet (`.when(error: ...)` ja GoRouter `errorBuilder`) ohjataan **standardoidun** `GlobalErrorView` (asiakkaassa `ErrorView`) komponentin kautta. Se osaa purkaa `AppException`in lokalisoiduksi toimintakehotteeksi. **Ainoastaan kehitystilassa (Debug Mode)** ErrorView paljastaa laajennettavan `Technical Details` -paneelin, joka näyttää koko stack tracen ja raa'an poikkeusdatan. Tuotannossa asiakas näkee vain tyylikkään ja ystävällisen kehotteen.

### 6.5 Separation of Concerns: Framework vs. Domain Errors (Päällekkäisen työn estäminen)
Päällekkäinen lokalisointityö vältetään ymmärtämällä selkeä rajanveto **Framework-virheiden** ja **Domain-virheiden** välillä:
* **Framework-tason l10n (Automaattinen):** Flutterin omat SDK-paketit ja natiivikomponentit hoitavat OS-tason virheiden ja ilmoitusten lokalisoinnin. Näitä *ei koskaan* yritetä kääntää uudelleen omilla `.arb` tiedostoilla.
* **Domain-tason l10n (Global Error Handling V3):** Tämä kokonaisuus (`AppException` ja backendin `exceptions.py`) on varattu **puhtaasti liiketoimintalogiikan** räätälöidyille virheille (esim. `WORKFLOW_EXECUTION_FAILED`). Me kartoitamme ja käännämme ainoastaan nämä omat Enum-koodimme Actionable Hinteiksi.

---

## 🖥️ 7. HYBRID BFF & OMNI-CHANNEL RENDERING

### 7.1 Zero-Deploy BFF & ViewModel Nodes (Backend-for-Frontend)
Kaikki kognitiivinen liiketoimintalogiikka ja käyttöliittymän piirtosäännöt konfiguroidaan tietokannassa. Frontend on "tyhmä" renderöintimoottori, joka kääntää isot epäsäännölliset rakenteet nautittavaan dynaamiseen perusformaattiin. 
Käyttöliittymä piirtää UI-vihjeiden (esim. `slider`) pohjalta dynaamisia yhdistelmäkomponentteja (Compound Widgets), jotka näyttävät LLM:n teoriaperustelun ja virallisen lähdeviitteen automaattisesti laajennettavissa Markdown-laatikoissa.

### 7.2 Omni-Channel Data Feed
Tässä kerroksessa isot domain mallit tarjoillaan Pydantic DTO:ina ja liitetään jäädytettyyn `ui_hints_snapshot` -sääntöjoukkoon. Backend ei enää sisällä kovakoodattuja UI-reittejä (BFF).

### 7.3 Graceful Degradation Protocol (The Only Exception to Fail-Fast)
Rajapinta on ohjelmiston **AINOA PAIKKA**, jossa Fail-Fast ei ole ehdoton standardi.
* Jos Agentti tuottaa laajan monihierarkisen raportin, ja yhdestä sen palasesta rikkoutuu yksi solu, emme kaada koko näkymää. 
* Ominaisuus hoituu nykyään automaattisesti `ui_hints_snapshot` -mekanismin ja Dartin `SafeCast` -defensiivisen parsinnan yhteistyönä. Frontend on suunniteltu ohittamaan tyhjät (`{}`) tai tuntemattomat blokit nostamatta Punaista Ruutua (Red Screen of Death) `SizedBox.shrink()` avulla.

### 7.4 Specialist Nested Output Data
Kaikki erikoisagenttien (kuten Logician tai Archivist) tuottamat erikoistulokset pakataan omaksi avaimekseen rakenteen sisään (Strict Nesting -> `{"logician_data": {"score": ...}}`). Datan luvaton "flättäys" (yhdistäminen root-tasolle) romuttaa BFF:n dynamiikan.

### 7.5 The "Zero-Math UI" & Database Purity Mandate (MANDATORY)
* **Tietokannan Puhtaus (`ExecutionRecord`)**: V2-tietokanta on puhdas logi! Se ei koskaan saa sisältää esitysmuuttujia (kuten renderöintiprosentteja `visual_pct` tai käännettyjä CSS-mittoja). Tietokanta sisältää vain arkkitehtuurin raakadatan.
* **Laskentavastuu (`/render` API)**: Kaikki visuaalinen matematiikka ja näyttöarvojen formatointi (esim. `12.3 / 100`) on keskitetty Python-backendin `BlueprintTransformer`-palveluun, joka injektoidaan lennosta vain lukuhetkellä!
* **Zero-Math UI (Frontend)**: Flutterin widgetit (kuten `gauge_1d_widget.dart` tai `scatter_3d_widget.dart`) MÄÄRÄTÄÄN nollamatematiikka-sääntöön. Ne EIVÄT SAA ikinä sisältää `.toStringAsFixed(1)` muotoiluja tai prosenttilaskuja. UI-näkymien ja Debuggerin (esim. `ExecutionView`) on täysin kiellettyä yrittää piirtää käyttöliittymää suoraan raa'asta DB-objektista ilman `/render` -päätepisteen esilaskentaa.

---

## 🌍 8. INTERNATIONALIZATION (I18N) POLICY

**"The No-String Mandate" & Kognitiivinen Monikielisyys (The 5-Layer Strategy)**

Quorum V2:n työnkulut irrottavat tekoälyn "kognitiivisen" päättelymekanismin (aina englanniksi laadun maksimoimiseksi) loppukäyttäjän "esitys- ja asiointikielestä" (esim. suomi) hyödyntäen Holistic Localization Strategy -mallia.

### 8.1 Kerros 1: Staattinen Käyttöliittymä (Compile-Time l10n)
Flutterin luontaiset `.arb`-tiedostot (esim. `app_fi.arb`) on varattu **ainoastaan** käyttöliittymän kiinteille komponenteille (napit, navigaatio, staattiset otsakkeet). Virheenhallinnassa (RFC 7807) käytetään `AppErrorExt` reititintä, joka muuntaa backendin Enum-tunnisteet yhdistetyksi *Actionable Hintiksi* omalla kielellä.

### 8.2 Kerros 2: BFF-Tietokanta & Dynaamiset Säännöt (Runtime Payload)
Kun järjestelmään lisätään matriiseja tai säännöstöjä, Pydantic DTO tallentaa ne kantaan muodossa `translations: {"fi": "Syyttäjä...", "en": "Prosecutor..."}`. Flutter lukee aina oman lokaalinsa mukaisen käännöksen dynaamisesti Backendin The Translation Schema Doctrine mukaisesti (SafeCast/BlueprintTransformer).

### 8.3 Kerros 3: Kognitiivinen Moottori & English-Only Mandate (The Deep Engine)
Tekoälymalli on huomattavasti kyvykkäämpi englanninkielisenä. Asiantuntija-agenttien metatiedot ja PromptBlockien järjestelmätason ohjeet on **pakko kirjoittaa englanniksi** (`translations["en"]`). Malli pakotetaan ajattelemaan (JSON `reasoning_trace`) englanniksi, mutta se on velvoitettu poimimaan käyttäjän alkuperäiset lainaukset täysin koskemattomina alkukielellä.

### 8.4 Kerros 4: Numeerinen ja Temporaalinen Standardi (Dates, Numbers)
Numeroita, päivämääriä, kellonaikoja ja valuuttoja ei koskaan lokalisoida backendissä. Kaikki aika kulkee ISO 8601 UTC -muodossa (`"2026-03-14T15:30:00Z"`) ja numerot primitiiveinä (esim. `5.0`). Flutter vastaa formatointilogiikasta käyttäjän laitteen paikalleen Dartin `intl`-kirjaston avulla (ICU).

### 8.5 Kerros 5: The Translation Boundary & Loppusynteesi (Late-Binding)
Backend **EI KOSKAAN** palauta API:ssa ohjelmallisesti yhdisteltyjä UI-merkkijonoja. Lopullinen muoto (Flutter BFF, taitettu Jinja2 PDF) purkautuu vasta aivan prosessin lopussa myöhäisellä sidonnalla (Late-Binding). Tarvittaessa backend käyttää erillistä luonnollisen kielen LLM-käntäjää (Translation Hook) asiakkaan kielelle kääntämiseen ennen payloadin siirtoa eteenpäin dokumenteigenerointiin tai web-käyttöliittymään. Koska UI saa valita kielen, backendin status-kentät tulevat tiukkoina Enum-koodeina (esim. `AUTH_ORGANIC`) Fronttiin tai BFF-kerrokseen.

### 8.6 Frontend ICU Formatting (Ei string-katenointia)
Manuaalinen ohjelmallinen sanaliitto (`"Score: " + val.toString()`) on ehdottoman **KIELLETTYÄ**. 
Jos sanoilla tai sanamuodoilla joudutaan pelaamaan (monikko, sanajärjestys, viivaukset), kaikki logiikka siirretään kielen omistavaan `.arb`-tiedostoon käyttäen tehokasta ICU-syntaksia:
`"scoreVal": "Pisteesi on {val}"`. UI saa välittää lauseeseen ainoastaan muuttujan.

### 8.7 Computed Enum Fields (The Safety Check)
Kun LLM antaa datakenttään valinnan, kuten `"RISK_LOW"`, tämä ei korreloidu kovakoodattuna numerona koodin seassa. Se ajetaan Pydantic V2 `@computed_field`in läpi `Enum`-mallina varmistaen datan eheyden juuri ennen arvon (`1.0`) lukitsemista.

### 8.8 Studio/Builder Safety ("Edit values, never keys")
* Cognitive Studion "Raw Mode" koskee suoraan kantoihin/siemendataan (`seed_data.json`). Kun editoit ominaisuuksia muista: Et ole Excelissä kirjoittamassa sarakeotsikoita!
* Kirjaamasi `History Text` on **lokalisointiavain** (Translation Key), ei en-käyttäjän otsikko. Jos käännät sen täällä muotoon `Historiateksti`, särjet englannin käännöksen ja hajotat järjestelmän globaalin lokalisaation. Muokkaa arvoja, älä avaimia sorkkiessasi "SSOT"-rekistereitä.

---

## 📝 9. DOCUMENTATION & HYGIENE

### 9.1 English-Only Policy
Järjestelmän lähdekoodi (muuttujat, funktiokutsut, luokat, SQL) sekä sen mukana liikkuvat dokumentit (`task_key`) on nimettävä täysin globaalilla englannilla (US English). Poikkeuksia suomen käytöstä koodin sisällä ei tunneta.

### 9.2 Imperative Mood Docstrings
Julkiset funktiot (sekä Dart `///` että Python `"""`) alkavat käskymuodossa, komentaen lukijaa.
* ❌ Kertova/Kuvaileva (Banned): "Returns the calculated score from the matrix."
* ✅ Imperatiivi (Mandatory): "Calculate the matrix score and return the numeric equivalent."

### 9.3 The "Why" Mandate for Inline Comments
Ohjelmoijat (ja Tekoälyagentit) lukevat koodia erittäin hyvin. Kukaan ei tarvitse selitystä siihen **Mitä (What)** mekaanisesti tehtiin (esim `# Yhdistä taulukot`).
Sisäisten rivikommenttien ainoa tehtävä arkkitehtuurissa on avata poikkeuksia, tai avata **Miksi (Why)** koodi käyttäytyy kyseisellä tavalla (esim. liikesalaisuudet, oudot matemaattiset ratkaisut, arkkitehtuuricorner-caset). Jos käytät yllättävää rakennusratkaisua reunaehdon voittamiseksi, aloita docstring lauseella: `NOTE (Architecture): ...`. Tämä estää seuraavaa devaajaa vahingossa "korjaamasta" tuikitärkeää hackiasi olettaen sitä virheeksi.

### 9.4 Code Ownership (No Zombies)
* Zombie koodia, eli passivoituja koodiblokkeja (`// class OldSettings()...`) ei pidetä kiusaamassa lintereitä ja versionhallintaa. Ne deletoidaan ronskisti, git historia muistaa hävikkisi.
* Orphaned (Orvot) TODO:t ovat kiellettyjä. Merkintä vaatii kontekstin ratkaisulle: `TODO(risto) [2026-03] Remove after api-V2 rolls out.`

---

## 📱 10. ADAPTIVE UI & NAVIGATION ARCHITECTURE
Käyttöliittymän globaalia navigaatiota, rakenteen litteyttä (Flat Hierarchy) ja "Omni-Navigation" sääntöjä ohjaa nyt oma, erillinen arkkitehtuuridokumenttinsa.
**Jokaisen Flutter-kehittäjän ja AI-agentin on ehdottomasti noudatettava sitä navigaatiota rakennettaessa.**

👉 **Lue täysi säännöstö:** `docs/AdminStudio_V2_UI_Architecture.md`