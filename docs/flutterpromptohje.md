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

### 1.1 Baseline Dependencies & Tooling (2026 Standard)
Täyttä tukea 2026-arkkitehtuurille ei saavuteta legacy-kirjastoilla tai vanhoilla pakettimanagereilla.
* **Paketinhallinta:** Järjestelmä käyttää yksinomaan salamannopeaa **`uv`**-työkalua (Rust-pohjainen). Kaikki skriptit ja linterit ajetaan komennolla `uv run`. `pip`, `poetry` tai `pipenv` ovat kiellettyjä.
* **Backend (Python 3.14.2+, FastAPI 0.128+)**: `pydantic 2.12.5+`, `litellm 1.81.3+`, `tenacity 9.1.2+`.
* **Frontend (Dart 3.11, Flutter)**: `flutter_riverpod ^3.1.0`, `go_router ^17.0.1+`, `freezed ^3.2.3`.

### 1.2 Banned Patterns (Language & State)
| Area | Modern Requirement (MANDATORY) | Banned Pattern |
| :--- | :--- | :--- |
| **Python Typing** | `str \| None`, `list[int]`, `dict[str, Any]` | `Optional[str]`, `Union[...]`, `typing.List`, `typing.Dict` |
| **Python Generics** | PEP 695: `type Alias = ...`, `def func[T](x: T):` | `TypeVar('T')` (Legacy generics), `TypeAlias` |
| **Python Async** | `asyncio.TaskGroup()` (Structured Concurrency) | Bare `asyncio.create_task()`, raw `asyncio.gather()` |
| **Python Logging** | Structured Logs: `logger.error("fail", extra={"id": 1})` | F-strings in logs: `logger.error(f"fail {id}")` |
| **Inheritance** | PEP 698: Use `@override` from `typing` | Silently overriding interface methods |
| **State (Flutter)** | Use `@riverpod` (Generator) + `ref.watch()` | `ChangeNotifier`, `StateProvider`, manual `Provider` |
| **Routing (Flutter)**| Use strongly typed `GoRouteData` classes | Raw strings: `context.push('/home')` |
| **API** | Use `Annotated[Dep, Depends()]` | `params: Dep = Depends()` (Old syntax) |

### 1.3 Routine Quality Gates (Verifications)
Älä koskaan merkitse työtä valmiiksi tarkistamatta sitä manuaalisesti laadunvarmistustyökaluilla:
* **Backend**: `cd backend_v2 && uv run ruff format . && uv run ruff check . --fix && uv run mypy . --strict` (Ruff hoitaa muotoilun ja linttauksen, Mypy tarkistaa koko syvän juuressaan välttääkseen tuonti-sokeutumisen).
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

### 2.3 Strict Typing & Banned Fallbacks (No Defaults)
* Domain-malleissa ja UI-tiloissa **EI SAA OLLA** implisiittisiä oletusarvoja pakollisille kentille. Alkuarvojen asettaminen (esim. `score: float = 0.0` tai `String text = ""`) puuttuvan serveridatan paikkaamiseksi on ankarasti KIELLETTY.
* **DTO Schema Parity (Backend-Frontend Match):** Vaikka ylläoleva sääntö kieltää paikkailun, **TARKISTA AINA Backendin Pydantic-malli** ennen `fromJson` koodin kiristämistä. Jos backendin palauttama malli (esim. vakio `User`) oikeasti jättää tietyn tilastokentän (esim. `execution_count`) rakenteellisesti pois, vastaavan Flutter-kentän TYPPI PITÄÄ OLLA nullable (`int?`). Älä koskaan syötä sokeasti `as int` -castausta dataan, jota backend ei edes suunnitellut lähettävänsä. Jos payloadit eroavat merkittävästi eri rooleilla/näkymillä, luo Flutteriin erilliset mallit (esim. `User` vs `UserAdmin`).
* **Kielletty:** Null-coalescing -operaattoreiden (`data ?? defaultData`) käyttö käyttöliittymäkomponenteissa tai backend-logiikassa datan selviytymiseksi on täysin BANNATTU.
* Pydantic V2 on käytössä tilassa `ConfigDict(strict=True)`. Tyyppipakotuksia ei tehdä lennosta (esim. ei merkkijonoa `"1"` numerokenttään `1`).
* **Strict Pydantic 2026 Mandate (Rust-Core & Anti-Hallucination):**
  1. **Instantiation:** NEVER use dictionary unpacking (`MyModel(**data)`). ALWAYS use `MyModel.model_validate(data)` to force the Fail-Fast validation pipeline.
  2. **Rust-Speed JSON Parsing:** When parsing raw JSON strings (e.g., from Arq/Redis or LLM output), NEVER use Python's `json.loads()`. You MUST use `MyModel.model_validate_json(json_str)` to bypass Python and parse directly in Rust.
  3. **Serialization Ban:** Legacy V1 methods `.dict()`, `.json()`, and `parse_obj()` are BANNED. Use `.model_dump()` and `.model_dump_json()`. Nested `class Config:` is banned; use `model_config = ConfigDict(...)`.
  4. **V1 Validator Ban:** Legacy `@validator` and `@root_validator` are BANNED. Use V2 `@field_validator` and `@model_validator(mode='after')`.
  5. **Anti-Hallucination:** All models parsing external or LLM payloads MUST use `model_config = ConfigDict(extra='forbid', strict=True)`. If an LLM hallucinates undocumented keys, the model MUST crash immediately (Fail-Fast). Silently dropping extra data is banned.
  6. **Immutability (Frozen State):** All Event Sourcing models (`TraceEvent`), DTOs, and DAG nodes MUST be immutable using `model_config = ConfigDict(frozen=True)`. In-place mutation (`event.status = 'done'`) is BANNED. Spawn new states using `event.model_copy(update={'status': 'done'})`.
  7. **Polymorphism (O(1) Routing):** When defining complex DAG nodes or TraceEvents, implicit Unions are BANNED. You MUST use Discriminated Unions (`Field(discriminator='type')`) to ensure O(1) parsing speed and prevent unsafe duck-typing.
  8. **Annotated Validators (PEP 593):** NEVER mix validation with default values (e.g., `age: int = Field(gt=0)`). ALWAYS use `Annotated` to keep type hints pure for `mypy` (e.g., `age: Annotated[int, Field(gt=0)]`).

### 2.4 Deterministic Execution Mandate (Python Authority)
* LLM (Tekoäly) on probabilistinen; Python on deterministinen. 
* Jos loogisen operaation (Matematiikka, lajittelu, deduplikointi, tunnisteiden luonti) voi tehdä deterministisesti Pythonissa (`BaseAgent.post_process()`), sitä **EI KOSKAAN** delegoida tekoälylle promptiin.

### 2.5 Zero-Hardcoded Styling (Design Tokens)
* **NO HARDCODED STYLING:** NEVER use magic numbers for padding/sizing (e.g., 16.0) or hardcoded raw colors (e.g., Colors.blue). ALWAYS use `Theme.of(context)` and the app's centralized design tokens. The UI must flawlessly support dynamic Dark Mode and density scaling.

---

## 💾 3. ARCHITECTURE & DATA LIFECYCLE

### 3.1 Single Source of Truth (SSOT) & Domain Service Layer (MANDATORY)
* **Firebase CQRS (Read/Write Separation):** Frontend (Flutter) on Firebase-tietokannan suhteen **EHDOTTOMAN READ-ONLY**. Frontend käyttää Firebase SDK:ta AINOASTAAN reaaliaikaisten datastriimien (`snapshots()`) kuuntelemiseen nollaviiveen illuusion luomiseksi. Frontend EI SAA KOSKAAN kirjoittaa, päivittää tai poistaa dataa suoraan Firestoresta. Kaikki mutaatiot ON lähetettävä Python FastAPI -backendille, joka validoi payloadit Pydanticilla ja päivittää tietokannan turvallisesti Admin SDK:n kautta.
* **API Routers MUST be "Anemic":** FastAPI reitittimet (esim. `users.py`, `studio.py`) saavat sisältää vain HTTP-pyynnön parsinnan (Pydantic). 
* **NO RAW CRUD IN ROUTERS:** Reititin ei koskaan saa kutsua suoraan `repository.create()` tai `repository.get()`, eikä se saa sisältää käyttöoikeuslogiikkaa (esim. `if current_user.role == "ROOT"`). Kaikki tietokanta- ja liiketoimintalogiikka (etenkin Tenant Isolation, RBAC ja Last Admin Guard) **ON PAKKO** reitittää aina kerroksen 2 (Domain Service Layer, esim. `AuthServiceDep`, `StudioServiceDep`, `ExecutionServiceDep`) kautta.
* **Miksi?** Järjestelmää ajetaan myös ohjelmallisesti tausta-ajoilla (esim. `worker.py`), jotka eivät reitity API:n kautta. Service Layer on backendin ainoa Single Source of Truth luvitukselle ja datan eheyksille.

### 3.2 Unified Storage Driver (V3 Muutos)
* Tietokantaa koskevat CRUD-muutokset tehdään vain kerran `UnifiedWorkflowRepository` -luokkaan. Vanha `firestore_repo.py` on poistettu, ja uudet StorageDriverit hoitavat pilvi/lokaali -peilauksen automaattisesti taustalla.

### 3.3 Event Sourcing & Rehydration (⚠️ V3 BIG BANG MIGRATION IN PROGRESS)
* **HUOM:** Moottorin V3-refaktorointi on kesken! Osa rajapinnoista palauttaa toistaiseksi vanhaa `ExecutionRecord.results` sanakirjaa. Kun migraatio on valmis, Frontend lukee askeleet ainoastaan `execution_trace` (TraceEvent) -lokista.
* Tapahtumaloki (`TraceEvent`) tulee olemaan ydinmoottorin AINOA totuuden lähde (SSOT). Vanha, lennosta editoitava `results` blackboard poistuu historiidatasta lopullisesti. 
* **Rehydration:** Käyttöliittymä tulee tukemaan katkenneen ajon saumatonta jatkamista (Rehydration). Jos ajo päätyy `failed` -tilaan, sitä ei hylätä korruptoituneena. Käyttäjä voi lähettää virhetilassa olevan ajon ID:n takaisin moottorille, joka kelustelee tapahtumanauhan (*fold_trace*) takaisin katkeamispisteeseen ja jatkaa suoritusta ilman toistettuja LLM-kutsuja.

### 3.4 Reliability Strategy (Timeout)
* Kaikilla ulospäin lähtevillä verkkopyynnöillä on pakotettu aikakatkaisu (Timeout). Järjestelmä ei saa hirttää kiinni (Zombie).
* Uudelleenyritys (Retry) hallitaan infrastruktuurissa asynkronisilla kirjastoilla (kuten `Tenacity`), ei etupäässä käyttäjän toimesta.
* **Background Workers (Arq 2026 Mandate):** Pitkäkestoiset tekoälygeneroinnit tai raskaat DAG-suoritukset EIVÄT SAA KOSKAAN blokata FastAPI:n HTTP-pyyntösykliä. Ne on siirrettävä asynkroniseen taustatyöjonoon (Arq / Redis). API-reitittimen on palautettava `202 Accepted` -status ja TaskID välittömästi. Frontend kuuntelee valmistumista Firebase-striimien (tai SSE) kautta.

### 3.5 Seed Data Protocol (Tietokannan hallinta)
**ERITTÄIN TÄRKEÄ SÄÄNTÖ:** Tietokantaa (TinyDB) ei koskaan muokata lennosta tai ohittaen Seed-prosessia kehityksessä. 
Aina kun tietokannan asetuksia, prompti-lohkoja tai askeleita muutetaan:
1. **Opaque ID -Sääntö:** Kaikkien uusien tunnisteiden on noudatettava Stripe Patternia (ei ihmisluettavia sanoja). Katso luontiohjeet: `Arkkitehtuuristandardi_Tietokannan_Tunnisteet.md`.
2. **Muokkaa alkuperäistä JSONia:** Tee rakenteellinen muutos ensin tiedostoon `backend_v2/seed/seed_data.json`.
3. **Kopio (Backup):** Aina ennen isoja muutoksia on varmistettava, että kopiota pidetään `backend_v2/seed/backups/` -hakemistossa turvassa vääristymiseltä.
4. **Siemennys (Re-Seed):** Vasta tämän jälkeen varsinainen paikallisen kannan päivitys ja synkronointi suoritetaan ajamalla käsky: `python backend_v2/seed/run_seed.py local`.
Tämän ohjeen kiertäminen ja kannan (`db_v2.json`) sorkkiminen lennossa korruptoi järjestelmän ID:t korjauskelvottomiksi.

---

## 🐍 4. PYTHON BACKEND MANDATES (3.14+ STRICT STANDARDS)

### 4.1 Framework Features & FastAPI Lifespan
* **DI (Dependency Injection)**: Pakotettu `Annotated[Type, Depends()]` -syntaksi. Suojaa tyypit ja poistaa "Any" -vuodot reiteistä. Vanha `param: Type = Depends()` on legacyä.
* **FastAPI Lifespan**: Vanhat `@app.on_event("startup")` dekoraattorit ovat poistuneet (deprecated). Kaikki tietokanta- ja worker-alustukset tehdään puhtaalla `@asynccontextmanager` (Lifespan) -rakenteella `main.py`:ssä.
* **FastAPI Async/Sync Rule**: Jos reitti lukee vain TinyDB:tä (joka on lukittu blocking-ajuri), reitin määritys tulee olla puhdas `def`. Jos reitti kutsuu LLM:iä, Firebasea tai Arq-jonoa, sen ON OLTAVA `async def`. FastAPI optimoi nämä omiin lankapoolihinsa.

### 4.2 Modern Syntax & Typing Strictness (PEP 695, PEP 604, PEP 698)
Python 3.14 -ympäristössä koodin on oltava sataprosenttisesti modernia syntaksia. "Legacy"-tyypityksen käyttö hylätään linterissä (Mypy Strict).
* **Kielletyt**: `typing.Union`, `typing.Optional`, `typing.List`, `typing.Dict`, `TypeAlias`, `TypeVar`.
* **Vaaditut**: Käytä or-operaattoria (`str | None`), natiivikokoelmia (`list[MyModel]`) sekä uutta tyyppiparametrisyntaksia (esim. `type StripeId = str` ja `class Service[T]:`).
* **Perintä (`@override`)**: Kun implementoit Service-kerroksessa tai Repositoryssa perusluokan/interfacen metodia, sinun **ON PAKKO** käyttää `typing.override` -dekoraattoria. Se katkaisee ohjelman (Fail-Fast) heti `mypy`:ssä, jos rajapinnan muoto on muuttunut, suojellen koodikantaa hiljaisilta virheiltä.

### 4.3 Structured Concurrency & TaskGroups (Ei Orpoja Säikeitä)
Rinnakkaiset LLM-pyynnöt ja asynkronisten I/O-tehtävien hallinta (esim. rinnakkaiset reititykset tai MCP-haut) **ei saa koskaan** käyttää vanhaa `asyncio.gather()` tai vapaata `asyncio.create_task()` -metodia, koska ne voivat jättää taustalle zombiprosesseja yhden kaatuessa.
* **Mandaatti:** Kaikki uusi asynkroninen rinnakkaisuus kääritään Python 3.11+ **`asyncio.TaskGroup()`** -kontekstiin.
* **Miksi?** Jos DAG-verkossa yksi LLM-agentti nostaa virheen tai aikakatkeaa (Fail-Fast), `TaskGroup` peruuttaa automaattisesti (Graceful Cancellation) kaikki muut käynnissä olevat rinnakkaiset LLM-kyselyt. Tämä säästää välittömästi Token-kustannuksia, estää muistivuodot ja poistaa orpojen säikeiden riskin. Rinnakkaiset virheet napataan kiinni `ExceptionGroup` -oliosta uudella `except*` -syntaksilla.

### 4.4 API Boundary, Schema-First & Event Sourcing
* JSON-datansiirtoon on kiellettyä käyttää `dict` tai tyypittämätöntä datakenttää HTTP-rajapinnassa. Request/Response -kappaleet ovat aina vahvasti rajattuja Pydantic-malleja (`response_model`).
* **The Three Pydantic Boundaries (API, Service, Middleware)**: 
  1. **API Ingestion (Generic IN -> Strict OUT)**: Reitittimien ON PAKOTETTAVA data heti tiukkaan Pydantic DTO -malliin. Service-kerros ei ota vastaan tyhmiä sanakirjoja.
  2. **Service Layer (Strict IN -> Strict OUT)**: Liiketoimintalogiikka on ehdoton portinvartija. Se ottaa API:lta ja Tietokannasta vastaan vain puhdasta, validoitua Pydanticia (`Model.model_validate(data)`).
  3. **Middleware / Event Sourcing (V3)**: DAG-putkisto ja tallennuslokit (`TraceEvent`) on käsiteltävä tyyppiturvallisesti. Reititä uudet tapahtumat (esim. Event Reducers) käyttämällä Pythonin **Pattern Matchingia (`match / case`)**. Pitkät `if isinstance()` -ketjut ovat kiellettyjä solmujen tyyppien arvioinnissa, sillä `match/case` on tyyppiturvallisempi, nopeampi ja pakottaa käsittelemään kaikki vaihtoehdot. Ohjelman sisäiset riippuvuudet pakastetaan tiukasti tyypitettyyn `HookExecutionContext` -objektiin Fail-Fast injektion takaamiseksi.
* **No-ORM**: Ei SQLAlchemyä. Pydantic kuvaa suoraan tietokannan dokumenttirakenteen (NoSQL) 1:1.

### 4.5 Null-Safety & Date Handling (Temporal Standard)
* API-rajapinta ei halua palauttaa asiakkaalle tyhjän listan tilalla `null`. Käytä listoille Pydanticissä automaattisesti reagoivaa syntaksia: `Field(default_factory=list)`.
* Kentät, jotka voivat olla tyhjiä, määritellään aina muodossa `field_name: str | None = None`. Implisiittinen arvon arvaaminen on kielletty.
* **Aikaleimat:** Talletus aina formatoituna aikaleimana UTC-ajassa käyttäen modernia Python-singletonia: `datetime.now(datetime.UTC)`. Hitaampi `timezone.utc` on legacyä. API:ssa muunnetaan muotoon `isoformat()` automaattisesti. Älä ikinä käytä aikaleimoja ilman aikavyöhykettä (naive datetime).

---

## 💙 5. FLUTTER CLIENT MANDATES (DESKTOP-FIRST & PRO-TOOL)

### 5.1 Desktop-First, PC Breakpoints & Information Density
Quorum ei ole kuluttajille suunnattu mobiilisovellus, vaan **ammattilaisten IDE-työkalu (Pro Tool)**. Käyttöliittymä ja komponentit suunnitellaan aina työpöytä (Desktop) edellä:
* **PC-luokan Breakpointit:** Näyttötila jaetaan kolmeen tiukkaan murtumispisteeseen:
  1. **PC / Ultrawide (>1200dp):** Vaatii **Three-Pane Layoutin** (Sivupalkki -> Master-lista -> Työtila/Canvas). Sarakkeiden välillä käytetään hiirellä säädettäviä jakajia (Resizable Splitters).
  2. **Tabletti / Kannettava (600dp - 1199dp):** Vaatii **TwoPane (Split-Screen)** -asettelun rinnakkain.
  3. **Mobiili (<600dp):** Degradoituu alalaidan `NavigationBar`-komponenttiin ja koko ruudun peittäväksi pino-navigaatioksi (Stack Navigation).
* **Information Density (Datan tiheys):** Isoilla näytöillä tyhjän tilan ("white space") tuhlaus on kielletty. Yli 600dp näytöillä Flutterin teema pakotetaan tilaan `VisualDensity.compact`, mikä maksimoi kerralla näkyvän informaation. Pitkissä luetteloissa suositaan tiheitä DataGrid-taulukoita löyhien listojen sijaan.
* **Power-User Modalities (Hiiri ja Näppäimistö):** Järjestelmän on tuettava natiivisti tehokäyttöä: Context Menus (hiiren oikea painike), Hover-työkaluvihjeet (esim. XAI-rajoitteet), pikanäppäimet (`Ctrl+S`, `Del`) ja Shift/Ctrl -monivalinnat. Kaikille monimutkaisille hiirieleille (kuten Drag & Drop) on tarjottava kosketusnäytöllä toimiva saavutettava varamekanismi (esim. Ylös/Alas -painikkeet) virhepainallusten ("Fat Finger") estämiseksi.

### 5.2 GoRouter, Deep Linking & Moniajo (Multi-Tab)
* Sovelluksen sisälle navigoiminen tapahtuu luokkapohjaisesti `GoRouteData`. Raakamuotoisten `/` ja `/login` reittien kirjoittelu UI:n sekaan on bugi.
* **Deep Linking ja Moniajo (PC):** PC-käyttäjät avaavat näkymiä säännöllisesti uusiin selaimen välilehtiin (Multi-Tab). Vahvasti tyypitetty reititys (jossa "Opaque Stripe ID" kulkee validina parametrina tyyliin `/workflows/wf_xyz`) on elinehto, jotta syvälinkit toimivat saumattomasti ja yksittäisiä työnkulkuja voidaan jakaa URL-osoitteena tiimin kesken ilman tilan korruptoitumista.
* **Hybrid URL Pattern (Opaque ID + Slug):** Jos halutaan SEO:n tai ihmisluettavuuden takia näyttää entiteetin nimi URL:ssa (esim. `/workflows/wf_xyz/my-workflow`), reititin ja Backend poimivat hakuihin AINA vain muuttumattoman Opaque ID:n (`wf_xyz`). Slug on järjestelmälle pelkkää merkityksetöntä kosmetiikkaa. Näin taataan, että nimien muuttaminen ei koskaan riko vanhoja linkkejä (Link Rot) tai tietokantakytköksiä.
* **Guard Clauses:** Reitinvalintalogiikka keskitetään yksinomaan reitittimen `redirect`-funktioon, ei manuaalisesti widgetien `build()`-luokkiin.
* **GoRouter $extra Ban (Strict ID-Only Routing):** Älä koskaan yritä ruokkia State/Form -tiloja injektoimalla domain-dataa (`initialData: $extra`) reitittimen läpi. Se rikkoo Riverpod-eristyksen (ja mahdollisesti moniajonsyvälinkityksen PC-ympäristössä, kun sivu päivitetään). Reititin (GoRouter) saa välittää AINOASTAAN puhtaita tunnisteita (Opaque IDs tai Slugs) uusille näkymille. Näkymän oma `@riverpod` AsyncNotifier on yksin vastuussa datan hakemisesta ja formatoinnista täsmällisen ID:n perusteella.
* **Stateful Nested Navigation (Desktop):** Koska Admin Studio on PC-työkalu, käyttäjien työnkulut (esim. puoliksi täytetyt lomakkeet) EIVÄT SAA tuhoutua sivupalkin välilehtiä vaihdettaessa. Päätason navigaatiossa ON KÄYTETTÄVÄ GoRouterin `StatefulShellRoute` (tai `StatefulShellBranch`) -rakennetta tavallisen `ShellRoute`:n sijaan.

### 5.3 Concurrency, Performance & Zero-Latency Illusion (Isolate Mandate)
* Raskaat Backendistä tuodut ylisuuret JSON-rakenteet tai datan transformoinnit **SIIRRETÄÄN VÄKISTEN** erilliseen säikeeseen: `Isolate.run(...)`. Vanha Flutterin `compute` -funktio on poistettu näistä tehtävistä käytöstä.
* **The "Dumb UI" & Isolate Leaking:** `Isolate.run()` kuuluu yksinomaan Riverpod-providerin (esim. `AsyncNotifier` `build`-metodin) sisälle. Älä koskaan kutsu `Isolate.run()` suoraan Widgetin `build`-syklissä tai `useEffect`-hookissa, sillä se vuotaa asynkronista liiketoimintalogiikkaa UI-kerrokseen.
* **Main Thread Jank -suojaus (PC-näytöt):** Erityisesti PC-työpöytänäkymissä massiivisten DAG-puiden (satoja solmuja) ja Pydantic DTO -rakenteiden deserialisointi välimuistiin on pakko eristää päälangoista. Vain näin taataan "Zero-Latency Illusion", eli hiiren kursori ja raskaiden 2D-kankaiden zoomaus pysyvät täydellisen sulavina huippunäytöillä (120Hz/144Hz).

### 5.4 Riverpod 3.0 State, Optimistic Updates & Mutaatiot
* Luovu "Odotan vastausta 2 sekuntia - spinneri pyörii" UX-suunnittelusta. **Koko ruudun latausanimaatiot (Loading Spinners) ovat IDE-työkalussa ankarasti kiellettyjä.** PC-käytön illuusio nollaviiveestä säilytetään **Optimistisilla päivityksillä** (Tila paikallisesti = Päivitetty jono $\rightarrow$ Lähetä serverille $\rightarrow$ Jos ei onnistunut, peruuta näyttö tilaan x).
* Kaikki **sivuvaikutukset (Side Effects)** – tallennukset, poistot – on ohjelmistossa **PAKOTETUSTI** hallittava kokeellisen (mutta stabiilin) Riverpod 3.0 `Mutation<T>` objektin kautta. Älä tee enää manuaalisia state-lippuja kuten `bool _isLoading`.
* **Lataustilojen (Loading Flags) kielto:** Manuaaliset latausliput hookeilla (esim. `final isSaving = useState(false);`) ovat UI:ssa ankarasti kiellettyjä. Kaikki sivuvaikutukset ja lataustilat hoidetaan Notifierissa (joka asettaa itsensä `AsyncLoading`-tilaan). UI lukee pelkästään providerin sisäänrakennettua `.isLoading` -tilaa eikä ylläpidä omaa lokaalia lippuaan.

### 5.5 Riverpod Hybrid Caching Strategy (SWR & TTL)
* Järjestelmän listat ja lomakkeet EIVÄT käytä pelkkää aggressiivista `autoDispose`:a.
  1. **Lukunäkymät (Luku-Listat, Dashboard):** Käytetään SWR (Stale-While-Revalidate) -mallia. Riverpod-provider pidetään elossa (`ref.keepAlive()`), jolloin PC:llä paluunavigointi on välitöntä nollaviiveellä. Tiedot päivittyvät taustalla huomaamattomasti.
  2. **Syöttönäkymät (Forms, Uudet Analyysit):** Käytetään TTL (Time-To-Live) välimuistia. Keskeneräiset lomakkeet säilytetään aktiivisina vain lyhyen turva-ajan (esim. 3 minuuttia) poistumisen jälkeen vahinkonavigaation varalta.

### 5.6 The Flat MVC List Architecture (Master-Detail Mandate)
* **Kielletyt rakenteet:** Älä koskaan lataa dynaamisia tietokantakokoelmia (kuten koko Model Registryä tai Prompteja) valtavaksi `AsyncNotifier<Map<String, dynamic>>` -monoliitiksi, mistä UI yrittää onkia yksittäisiä objekteja.
* **The Flat MVC List:** Kaikki Master-näkymän listat mallinnetaan litteänä taulukkona: `AsyncNotifier<List<Map<String, dynamic>>>`. 
* **Detail-haku:** Kun käyttäjä siirtyy Detail-muokkausnäkymään Reitittimen ("Hybrid URL") kautta, yksittäinen objekti noudetaan erillisellä "IdProviderilla" (esim. `modelRegistryByIdProvider(id)`), ei suodattamalla ylätason Master-listaa. Tämä takaa saumattoman Syvälinkityksen (Deep Linking) vaikka Master-listaa ei oltaisi edes vierailtu.

### 5.7 2026 "Gold Standard" -malli lomakkeille
Frontend on yksinomaan 'tyhmä' renderöintimoottori.
1. **Lokaali Lomakkeen Tila (Notifier):** Puhtaaseen `@riverpod` Notifieriin / AsyncNotifieriin eriytetty logiikka hakee raw-datan, suorittaa `Isolate.run()`-purun ja hoitaa `submit()`-mutaatiot `AsyncLoading`-tilan kanssa. Tämä takaa 100% yksikkötestattavuuden ilman Flutter-riippuvuuksia.
2. **Tyhmä Käyttöliittymä (HookConsumerWidget):** Hookeja (`flutter_hooks`) saa ja pitää käyttää UI-komponenttien rakentamiseen, mutta **AINOASTAAN** puhtaiden ohimenevien UI-kontrollerien (kuten `useTextEditingController` tai `useAnimationController`) hallintaan. Kaikki asymptoottinen data ja tila luetaan ohjelmallisesti Riverpodista (`ref.watch(provider).when()`). Näin UI-kerros pysyy täysin eristettynä liiketoimintalogiikasta.
3. **Transient Form State:** Keystrokes and local UI inputs MUST remain locally inside Hooks (`useTextEditingController`). DO NOT dispatch every onChange event to a Riverpod Notifier, as this causes severe Main Thread Jank and unnecessary rebuilds. Only send the final assembled payload to the Riverpod Mutation upon `submit()`.

### 5.8 Dart 3 Pattern Matching & BFF Data Destructuring
* When destructing raw `Map<String, dynamic>` BFF payloads, you **MUST** use Dart 3 Pattern Matching (e.g., `final {'id': String id} = payload;`). 
* This provides compiler-backed type safety and instantly enforces the Fail-Fast boundary by throwing a `StateError` if the JSON schema is malformed. 
* **NEVER** use legacy, unsafe manual casting (e.g., `payload['id'] as String`).

### 5.9 Keyboard Focus Management (Strict Focus)
* Pro-tools require flawless Tab key navigation. 
* **Keyboard Focus Management:** Complex layouts **MUST** use `FocusTraversalGroup` and `FocusNode` to isolate and define logical keyboard navigation flow within specific panes.

---

## ⚠️ 6. ERROR HANDLING CONTRACT (GLOBAL ERROR HANDLING V3 / RFC 7807)

**SINGLE SOURCE OF TRUTH**: `backend/exceptions.py` & `client_app/lib/core/error/app_exception.dart`

### 6.1 Strict RFC 7807 Pattern & The "No Pass" Rule
Backendissä ei saa enää ikinä esiintyä paljaita (`ValueError` / `HTTPException`) nostoja rajapinnoilla. Kaikki poikkeukset tulee heittää paketoituna `AppException` tai sen semanttisilla aliluokilla. Frontend parsii ne 1:1 Freezed-malliin.

**THE "NO PASS" RULE (Silent failure is banned):**
Poikkeusten hiljainen nieleminen eli koodin yskiminen rikkinäisenä eteenpäin on EHDOTTOMASTI KIELLETTY.
* **Python:** `try: ... except Exception: pass` on **anasti kielletty**.
* **Dart/Flutter:** Tyhjät catch-lohkot `try { ... } catch (e) {}` ovat **täysin kiellettyjä**.
* **Ratkaisu:** Virheet on AINA joko käsiteltävä näyttämällä `ErrorView`, lokitettava rakenteellisesti (Dual-Reporting) tai heitettävä eteenpäin (`rethrow` / `raise`). Älä koskaan peitä järjestelmän kaatumista.

### 6.2 THE ZERO-HARDCODING MANDATE (Kovakoodaus kielletty)
Kaikki koodatut "oikotiet" ovat EHDOTTOMASTI KIELLETTYJÄ koko järjestelmässä.
* **Ei kovakoodattuja avaimia:** Älä keksi dart-koodissa sanakirja-avaimia (kuten `'criteria'`), jotka on julistettu kuolleiksi backendin Pydantic-malleissa. Pydantic on _Single Source of Truth_.
* **Ei kovakoodattuja tilaratkaisuja:** UI ei saa asettaa tila-logiikkaa manuaalisesti (esim. ohjelmoidut vakio ID:t kentissä). Kaiken on joustettava ja luettava suoraan backendin tarjoamasta skeemasta ja rajapinnoilta.
* **Ei ID-kenttien kysymistä käyttäjältä (Opaque ID Ban):** Luonti- ja muokkauslomakkeissa (Forms) ei saa IKINÄ olla näkyvissä "ID" tekstikenttää, jota käyttäjä tai pääkäyttäjä täyttäisi käsin. Kaikki Stripe Pattern ID:t (esim. `blk_abc123`) generoidaan järjestelmän toimesta aina taustalla The Cascading Clone tai luontiprosessien aikana. Käyttäjä syöttää ainoastaan `slug`, `label` yms.
* **Kieliperusteinen Relaationpurku (Nomenclature Resolution):** Kun relaatioita tai JSON-puuta täytetään (esim. liitetään askeleita työnkulkuun pudotusvalikosta), käyttöliittymän on EHDOTTOMASTI esitettävä elementit inhimillisesti luettavilla Nimi-arvoilla (esim. `label.translations[locale]`). Nämä arvot on haettava dynaamisesti ID:n perusteella käyttäjän valitsemalla kielellä. Käyttäjä näkee nimen, järjestelmä tallentaa taustalla ID:n. Pelkkien ID-koodien näyttäminen valikoissa on kielletty.
* **Virheiden piilotus Default-arvoilla:** (esim. `score=0.0` tai `name="Nimetön"`) on rinnastettavissa kovakoodaukseen ja tiedon väärentämiseen. Se on kielletty.

### 6.3 Dual-Reporting & Telemetry Mandate
Ainoa sallittu tapa ottaa virhe kiinni ja heittää se ylemmäs on **Kaksinkertainen Raportointi** (Dual-Reporting).
**Backendissä:** Ensin rakenteellinen printti serverille (`logger.error(..., exc_info=True)`), sitten nosto `AppException(error_code=...)`.
**Frontendissä:** HTTP-verkkovirheet kirjataan Riverpod-LoggerServiceen, joka välittää ne Backendin etätelemetria-päätepisteeseen.

```python
# Backend Esimerkki (Python 2026 / Logfire Standard)
try:
    result = some_operation()
except Exception as e:
    # 1. SERVER LOKI: Yksityiskohtainen ja tekninen (Vain koodareille/Logfireen).
    # EI f-stringiä viestissä! logger.error(f"Error: {e}") on KIELLETTY.
    logger.error(
        "Validation failed during execute_node for block_id xyz",
        extra={
            "error_code": ErrorCodes.VALIDATION_FAILED.name,
            "detail": str(e)
        },
        exc_info=True
    )
    # 2. ASIAKAS/API-VIESTI: Geneerinen ja turvallinen. (Menee HTTP-verkon yli Flutterille)
    # HUOM: ÄLÄ KOSKAAN yhdistä Server-lokiviestiä ja API-viestiä samaan muuttujaan
    # Tietoturvan (Information Leakage) ja eriytyksen takia!
    raise AppException(
        message="Invalid data structure.",
        error_code=ErrorCodes.VALIDATION_FAILED
    ) from e
```

### 6.3 Absolute Death & Diagnostic Node (Ei "Graceful Degradationia")
Käyttöliittymäkomponentit EIVÄT SAA ikinä jatkaa toimintaansa ("Graceful Degradation", `SizedBox.shrink()`), jos ne vastaanottavat viallista dataa.
* **Absolute Death:** Jos komponentti saa invalidia dataa, sen ON KUOLTAVA heti poikkeukseen (throw Exception tai palauta AsyncError).
* **Diagnostic Node:** Ylemmän tason **`AppErrorBoundary`** (tai Riverpodin `.when(error: ...)`) nappaa kaatumisen ja tulostaa komponentin tilalle lokaalin ja selkeän "Error Boxin" (esim. punainen katkoviiva, virheikoni ja spesifi `ErrorCode`), jotta data-korruptio on pro-työkalussa välittömästi havaittavissa, eikä piiloudu näkymättömiin.

### 6.4 Mapping Exceptions to the UI (Actionable Hints)
Backend-virheet käännetään UI:ssa lokalisoiduiksi **Actionable Hinteiksi** (esim. "Ikuinen silmukka havaittu. [Poista kytkös]"). PC-näkymässä nämä esitetään tyylikkäinä leijuvina Toast- tai Snackbar-komponentteina työtilan alakulmassa, ei koko ruutua blokkaavina modaaleina.

---

## 🖥️ 7. HYBRID BFF & OMNI-CHANNEL RENDERING

### 7.1 Zero-Deploy BFF & ViewModel Nodes (Backend-for-Frontend)
Kaikki kognitiivinen liiketoimintalogiikka ja käyttöliittymän piirtosäännöt konfiguroidaan tietokannassa. Frontend on "tyhmä" renderöintimoottori, joka kääntää isot epäsäännölliset rakenteet nautittavaan dynaamiseen perusformaattiin. 

### 7.2 Omni-Channel Data Feed
Tässä kerroksessa isot domain mallit tarjoillaan Pydantic DTO:ina ja liitetään jäädytettyyn `ui_hints_snapshot` -sääntöjoukkoon. Backend ei enää sisällä kovakoodattuja UI-reittejä (BFF).

### 7.3 Specialist Nested Output Data
Kaikki erikoisagenttien (kuten Logician tai Archivist) tuottamat erikoistulokset pakataan omaksi avaimekseen rakenteen sisään. Datan luvaton "flättäys" (yhdistäminen root-tasolle) romuttaa BFF:n dynamiikan.

### 7.4 The "Zero-Math UI" & Database Purity Mandate (MANDATORY)
* **Tietokannan Puhtaus (`ExecutionRecord`)**: V2-tietokanta on puhdas logi! Se ei koskaan saa sisältää esitysmuuttujia.
* **Laskentavastuu (`/render` API)**: Kaikki visuaalinen matematiikka ja näyttöarvojen formatointi on keskitetty Python-backendin `BlueprintTransformer`-palveluun!
* **Zero-Math UI (Frontend)**: Flutterin widgetit (kuten `gauge_1d_widget.dart` tai Simulaattori) MÄÄRÄTÄÄN nollamatematiikka-sääntöön. Ne EIVÄT SAA ikinä suorittaa algoritmeja (esim. Kahnin algoritmi) lokaalisti prosessorilla. Kaikki on ohjattava Backend-mutaatioiden (esim. `/simulate`) kautta, joiden palauttaman "UI Hintin" mukaan Frontend vain värittää solmut.

### 7.5 The Infinite Canvas & Inspector Mandate (DAG & Workflows)
Isolla PC-näytöllä monimutkaisia työnkulkuja (Workflows) ja riippuvuusverkkoja (DAG) **ei koskaan** piirretä staattisina pystysuuntaisina listanäkyminä tai yksinkertaisina pudotusvalikkoina. 
* Ne toteutetaan Flutterin `InteractiveViewer` -komponentilla varustettuna **2D-kankaana (Infinite Canvas)**, jota voi zoomata hiiren rullalla ja panoroida vapaasti.
* Kun kankaalla klikataan yksittäistä solmua, sen dynaamiset asetukset avautuvat erilliseen oikean reunan sivupaneeliin (**The Inspector**). Näin itse graafin visuaalinen kokonaisuus pysyy aina käyttäjän näkyvillä ja muokattavissa.

---

## 🌍 8. INTERNATIONALIZATION (I18N) POLICY

**"The No-String Mandate" & Kognitiivinen Monikielisyys (The 5-Layer Strategy)**

### 8.1 The 5-Layer Strategy
1. **Compile-Time l10n:** Staattiset käyttöliittymäkomponentit (`.arb`).
2. **Runtime Payload:** Dynaamiset säännöt tallennetaan `translations: {"fi": "...", "en": "..."}`.
3. **The Deep Engine:** Tekoälyn järjestelmäohjeet pakotetaan englanniksi laadun maksimoimiseksi.
4. **Temporal Standard:** Numerot ja ajat käsitellään UTC ISO 8601 -muodossa ja formatoidaan Dartin ICU:lla.
5. **Translation Boundary:** Backend ratkaisee käännökset vasta myöhäisellä sidonnalla. UI:lle toimitetaan aina Enum-koodeja (`AUTH_ORGANIC`).

### 8.2 Computed Enum Fields (The Safety Check)
LLM:n datakenttä-valinnat (`"RISK_LOW"`) ajetaan Pydanticin `@computed_field`in läpi `Enum`-mallina.

### 8.3 Studio/Builder Safety ("Edit values, never keys")
Admin Studion raakadatan avaimia (kuten `History Text`) ei saa kääntää suomeksi. Ne ovat lokalisaatioavaimia. Muokkaa arvoja, älä avaimia.

---

## 📝 9. DOCUMENTATION & HYGIENE

### 9.1 English-Only Policy
Järjestelmän lähdekoodi (muuttujat, funktiokutsut, luokat, SQL) on nimettävä täysin englanniksi.

### 9.2 Imperative Mood Docstrings
Julkiset funktiot alkavat imperatiivissa (käskymuodossa): "Calculate the matrix score..."

### 9.3 The "Why" Mandate for Inline Comments
Älä kommentoi MITÄ koodi tekee. Kommentoi MIKSI se on tehty (esim. `NOTE (Architecture): ...`).

### 9.4 Code Ownership (No Zombies)
Poiskommentoidut zombie-koodiblokit ja orvot TODO:t on poistettava säälimättä.

---

## 🔐 10. IAM & KÄYTTÄJÄN NÄKYMÄT (2026)

### 10.1 Zero-Latency IAM UI (Käyttäjäasetukset)
* **TwoPane IDE Layout:** Käyttäjän asetusnäkymä rakennetaan Desktop-First -periaatteella hyödyntäen TwoPane-näyttöä ja `FocusTraversalGroup` -rakennetta näppäimistönavigaatiolle. Käyttäjää ei koskaan viedä täysin "ulos" nykyisestä työtilasta.
* **SWR (Stale-While-Revalidate):** UI-tila (teema, kieli) päivitetään Riverpodilla välittömästi (Optimistic Update) lukemalla lokaalia välimuistia (`userPreferencesProvider`). Koko ruudun Loading-spinnerit on asetusmuutoksissa ehdottomasti KIELLETTY. Riverpod `Mutation` lähettää pyynnön API:lle täysin taustalla.

### 10.2 Passkey-First & Auth Interceptors (Riverpod)
* **Re-Auth Guard (Zero-Trust):** Backend hylkää arkaluonteiset mutaatiot (esim. salasanan vaihto) yli 5 min vanhalla tokenilla (`REAUTH_REQUIRED`). Riverpod-interceptor **ei koskaan navigoi täysruudun login-sivulle**, vaan ampuu päälle lokaalin dialogin, pyytää välittömän tunnistautumisen (Sormenjälki/Passkey), ja toistaa pyynnön taustalla saumattomasti.
* **Step-Up MFA:** Jos API palauttaa 403 `MFA_REQUIRED` (sillä JWT Custom Claims / AMR-leima puuttui tokenista), UI esittää Firebasen natiivin MFA-haasteikkunan paikallaan Actionable Hint -käyttökokemuksella varustettuna.

### 10.3 Bulk Data (The Isolate Mandate)
* Admin Studion listakutsut tai tuhansien rivien Excel/CSV massatuonnit (Massakutsulogiikka) **EIVÄT SAA KOSKAAN** blokata UI-säiettä edes sekunnin kymmenystä. Dataparsoinnit siirretään poikkeuksetta erilliseen säikeeseen: `final payload = await Isolate.run(() => parseAndValidateCsv(bytes));`. 

### 10.4 Flat Claims & Graceful Degradation (O(1) Authorization)
* Koko valtuutuslogiikka lepää Riverpodin muistissa dekoodatun JWT Tokenin Custom Claimseissa (`org_xyz: MEMBER`). Koska tieto on 0ms:n viiveellä Flutterin tiedossa, käyttöliittymä reagoi aktiivisesti piilottamalla elementtejä ohjelmallisesti (esim. "Tallenna" -nappi korvataan `SizedBox.shrink()` jos käyttäjä on Views-roolissa).
* Riverpod ei kysele käyttäjäoikeuksia serveriltä jatkuvasti, vaan reititys turvataan lokaaleilla Guardeilla. API hylkää yritykset lopullisesti 403:lla backendissä, jos UI vahingossa vuoti läpi kielletyn toiminnon.

## 📱 11. ADAPTIVE UI & NAVIGATION ARCHITECTURE
Käyttöliittymän globaalia navigaatiota, rakenteen litteyttä (Flat Hierarchy) ja "Omni-Navigation" sääntöjä ohjaa nyt oma, erillinen arkkitehtuuridokumenttinsa.
**Jokaisen Flutter-kehittäjän ja AI-agentin on ehdottomasti noudatettava sitä navigaatiota rakennettaessa.**

👉 **Lue täysi säännöstö:** `docs/AdminStudio_V2_UI_Architecture.md`