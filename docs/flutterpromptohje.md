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

### 1.2 Banned Legacy Patterns
| Area | Modern Requirement (MANDATORY) | Legacy Pattern (BANNED) |
| :--- | :--- | :--- |
| **State** | Use `@riverpod` (Generator) + `ref.watch()` | `ChangeNotifier`, `StateProvider`, manual `Provider` |
| **Routing** | Use `GoRouteData` (Type-safe classes) | Raw strings: `context.push('/home')` |
| **API** | Use `Annotated[Dep, Depends()]` | `params: Dep = Depends()` (Old syntax) |
| **Models (Backend)** | Use `model_validate`, `model_dump` | `.parse_obj()`, `.dict()` |
| **Domain Data (Frontend)** | `Freezed` for Local UI State (User, Settings). Raw `Map<String, dynamic>` for Dynamic API Payloads (De-Generator Policy). | Pure `Map<String, dynamic>` for Local State (Too slow to type and parse) / Freezed for SDUI (Breaks Zero-Deploy). |

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
* Työtila (`WorkflowState.context_variables` / Blackboard) on nopea ja editoitava hetkittäinen tilanne. Molempia täytyy ylläpitää, kun agentti tekee siirron.

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

---

## ⚠️ 6. ERROR HANDLING CONTRACT (RFC 7807)

**SINGLE SOURCE OF TRUTH**: `backend/exceptions.py`

### 6.1 Strict RFC 7807 Pattern (AppException)
Backendissä ei saa enää ikinä esiintyä paljaita (`ValueError` / `HTTPException`) nostoja rajapinnoilla tai patchejä. Kaikki poikkeukset tulee heittää paketoituna `AppException` tai sen semanttisilla aliluokilla (kuten `ConfigurationError`, `AgentExecutionError`).

### 6.2 Dual-Reporting Mandate
Ainoa sallittu tapa ottaa virhe kiinni ja heittää se ylemmäs on **Kaksinkertainen Raportointi** (Dual-Reporting).
Ensin rakenteellinen printti serverille, sitten tyyppiturvallisen poikkeuksen nosto. Siihen syötetään virheen syyn erottava Enum-vakio `ErrorCodes`.

```python
try:
    result = some_operation()
except Exception as e:
    # 1. Log with STRUCTURED FORMAT  
    logger.error(f"[Component] {ErrorCodes.VALIDATION_FAILED.name}: Error: {e}", exc_info=True)
    # 2. Raise explicit AppException wrapping the original error
    raise AppException(message=..., error_code=ErrorCodes.VALIDATION_FAILED, ...) from e
```

### 6.3 Mapping Exceptions to the UI (Actionable Hints & ErrorView)
* Backendin virhedata (`AppException`) tuodaan sellaisenaan koodina UI:hin (`"VALIDATION_FAILED"`), ilman käännöstä.
* UI lokalisoi viestin asiakkaalle (`client_app/lib/core/error/app_error_ext.dart`). Sanomaan kirjataan **miksi kävi näin ja mitä käyttäjän pitäisi yrittää seuraavaksi (Actionable Hint).** Ei kuitteja mallia "Tapahtui virhe".
* **Standardisoitu UI-Komponentti:** Kaikki virheet (`.when(error: ...)`) ohjataan standardoidun kokonäytön tai osittaisen näytön `ErrorView`-widgetin kautta, joka osaa näyttää poikkeuksen vikakoodit siististi ja nätisti. Omia `Text('Error')` vökerryksiä ei tueta.

---

## 🖥️ 7. HYBRID SDUI & BFF (Backend-for-Frontend)

### 7.1 Zero-Deploy SDUI & Compound Widgets (Server-Driven UI)
Kaikki kognitiivinen liiketoimintalogiikka ja käyttöliittymän piirtosäännöt konfiguroidaan tietokannassa. Frontend on "tyhmä" renderöintimoottori, joka kääntää isot epäsäännölliset rakenteet nautittavaan dynaamiseen perusformaattiin. 
Käyttöliittymä piirtää UI-vihjeiden (esim. `slider`) pohjalta dynaamisia yhdistelmäkomponentteja (Compound Widgets), jotka näyttävät LLM:n teoriaperustelun ja virallisen lähdeviitteen automaattisesti laajennettavissa Markdown-laatikoissa.

### 7.2 The BFF Mapping layer
Tässä kerroksessa isot domain mallit pienennetään spesifeihin View-malleihin (esimerkiksi `DriverProfileDisplay`).

### 7.3 Graceful Degradation Protocol (The Only Exception to Fail-Fast)
Rajapinta on ohjelmiston **AINOA PAIKKA**, jossa Fail-Fast ei ole ehdoton standardi.
* Jos Agentti tuottaa laajan monihierarkisen raportin, ja yhdestä sen palasesta rikkoutuu yksi solu, emme kaada koko näkymää. 
* Frontendille toimitetaan tällöin muunnoksena kyseiselle osiolle tyhjä data `{}` tai `SizedBox.shrink()`.
* **Kriittinen lisäehto:** Fallback (pehmennys) on merkittävä logeihin erittäin näkyvästi (`logger.warning("BFF Graceful degradation applied to specialist_data")` / Flutter `debugPrint("🔴 UI GRACFEFUL DEGRADATION...")`), jotta se ei huku hiljaisiksi aavebugeiksi!

### 7.4 Specialist Nested Output Data
Kaikki erikoisagenttien (kuten Logician tai Archivist) tuottamat erikoistulokset pakataan omaksi avaimekseen rakenteen sisään (Strict Nesting -> `{"logician_data": {"score": ...}}`). Datan luvaton "flättäys" (yhdistäminen root-tasolle) romuttaa SDUI:n dynamiikan.

---

## 🌍 8. INTERNATIONALIZATION (I18N) POLICY

**"The No-String Mandate"**

### 8.1 Late-Binding Omni-Channel (Backend Supplies Data)
Backend **EI KOSKAAN** palauta API:ssa lokalisointia tai yhdisteltyjä UI-merkkijonoja. Kaikki status- ja tyyppikentät esitetään yksinomaisin ja muuttumattomin Enum-koodein (`"status": "AUTH_ORGANIC"`). Tulosteiden lopullinen muoto (Flutter SDUI, taitettu Jinja2 PDF, litteä CSV/Flat-File export) purkautuu vasta aivan prosessin lopussa myöhäisellä sidonnalla (Late-Binding). Lokalisaatio ja esitysasu ratkaistaan aina kanavakohtaisesti.

### 8.2 Frontend ICU Formatting (Ei string-katenointia)
Manuaalinen ohjelmallinen sanaliitto (`"Score: " + val.toString()`) on ehdottoman **KIELLETTYÄ**. Piste. 
Jos sanoilla tai sanamuodoilla joudutaan pelaamaan (monikko, sanajärjestys, viivaukset), kaikki logiikka siirretään kielen omistavaan `.arb`-tiedostoon käyttäen tehokasta ICU-syntaksia:
`"scoreVal": "Pisteesi on {val}"`. UI saa välittää lauseeseen ainoastaan muuttujan.

### 8.3 Computed Enum Fields (The Safety Check)
Kun LLM antaa datakenttään valinnan, kuten `"RISK_LOW"`, tämä ei korreloidu kovakoodattuna numerona koodin seassa. Se ajetaan Pydantic V2 `@computed_field`in läpi `Enum`-mallina varmistaen datan eheyden juuri ennen arvon (`1.0`) lukitsemista.

### 8.4 Studio/Builder Safety ("Edit values, never keys")
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

## 🗺️ 10. KNOWLEDGE BASE MAP (DEEP DIVES)

Lisätietoja tarkemmista osa-alueista löydät järjestelmän ylläpitämästä sisäisestä tiedosta (Knowledge Items). Arkkitehtuurilinjaukset syvennetään näissä:

1. **Backend & AI Engine**:
   - `knowledge/backend_system_architecture/`
   - `knowledge/workflow_orchestration_and_reliability/`
   - `knowledge/seeding_and_data_lifecycle/`
2. **Frontend & UX**:
   - `knowledge/client_application_development/`
   - `knowledge/hybrid_sdui_strategy/`
   - `knowledge/identity_and_access_management/`
3. **Environment Protocols**:
   - `knowledge/development_environment_modernization/`