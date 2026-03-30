# Epic 12: Frontend Domain Model Freezed Migration (Strict Nirvana Validation)

## Tilannekatsaus (Background)
Cognitive Quorum V2 käyttää Flutter-frontendissä tiukkaa "De-Generator Mandate" -arkkitehtuuria. Tämä tarkoittaa, että luokkien serialisointi (`fromJson`, `toJson`), kopiointi (`copyWith`) ja identiteettivertailut (`==`) on ohjeistettu tehtäväksi tiukasti käsin koodattuna puhtaan Tyyppiturvallisuuden (Pydantic V2 -pariteetti) ja välittömän virheiden kiinnioton (Fail-Fast) saavuttamiseksi.

Käsin koodatun mallin (esim. 300-rivinen `PromptBlock`) ylläpidettävyys, skaalautuvuus ja virhealttius uusien kenttien lisäämisessä ovat kuitenkin osoittautuneet merkittäväksi pullonkaulaksi. Kehittäjäkokemus ja koodin puhtaus kärsivät. 

## Tavoite (Objective)
Siirrytään käyttämään Flutterin teollisuusstandardia, **Freezed** ja **JSON Serializable** -koodingenerointia, kaikkien laitteen (Frontend) Domain-mallien (`PromptBlock`, `Workflow`, `ExecutionRecord`) ylläpidossa. 

**Kriittinen edellytys:** Muutos **EI SAA** heikentää "Strict Nirvana" tai "Fail-Fast" -periaatteita. Emme luota `json_serializable`:n oletusarvoiseen parsintaan sokeasti. Sen sijaan koodiin integroidaan kustomoidut `@JsonConverter`-luokat, jotkat käärivät nykyisen `SafeCast`-logiikkamme sisäänsä. Näin saamme koodingeneroinnin tuoman valtavan boilerplaten poiston (hyöty), mutta säilytämme täydellisen poikkeustenhallinnan tietoturvan ja tyyppien eheyden (Fail-Fast).

### Tulevaisuusvisio (Future Outlook 2026+)
Dart-tiimin virallisen päätöksen myötä natiivit makrot (Dart Macros, ml. `@JsonCodable`) on hyllytetty suorituskykyongelmien (Hot Reload / Analyzer latency) vuoksi. Tämä tekee tästä Epic-suunnitelmasta absoluuttisen ja pitkäaikaisen teollisuusstandardin:

*   **1. `build_runner` on pysyvä standardi:** Koska makroja ei tule, `freezed` ja `json_serializable` tulevat olemaan Dart-ekosysteemin serialisoinnin selkäranka pitkälle tulevaisuuteen. Tästä syystä Milestone 1:ssä määritelty tiukka `build.yaml` -optimointi (`generate_for` skooppaus rajoittamaan kääntöaikaa) on pitkäikäisen arkkitehtuurin elinehto.
*   **2. Augmentation-Ready Arkkitehtuuri:** Vaikka makrot peruttiin, Dart-tiimi tuo kieleen koodingenerointia suoraviivaistavat *Augmentations*-ominaisuudet. Pakottamalla koodimme nyt tiukkaan Freezed-muottiin, varmistamme, että tulevaisuudessa `.g.dart` ja `.freezed.dart` -tiedostot sulautuvat saumattomammin osaksi alkuperäistä tiedostoa pelkällä `pubspec.yaml`-päivityksellä ilman massiivista arkkitehtuuriremonttia.
*   **3. Natiivit Data Classet:** Pitkän aikavälin tavoitteena Dart-tiimi tutkii metaprogrammoinnin sijaan natiiveja `data class` -rakenteita. Koska koodaamme mallit tiukasti Freezedillä simuloiden data-luokkia jo nyt, koodikanta on valmiiksi täydellisessä paradigmaattisessa muodossa mahdollista kielen tason tuettua siirtymää varten.

---

## Toteutussuunnitelma (Tier-1 Milestones)

### Milestone 0: Arkkitehtuuridokumentaation päivitys (Phase 9 Hardening)
Ennen varsinaista koodimuutosta päivitetään projektin ydindokumentaatio vastaamaan uutta teollisuusstandardia (Freezed + Custom Converters Riverpod-sovelluksissa). Tämä kumoaa aiemman laajan "De-generator" (manuaalinen `Map<String, dynamic>`) mandaatin.

**Tärkeimmät uudet arkkitehtuurisäännöt, jotka on päivitettävä ohjeisiin:**

1.  **Dart 3 Sealed Classes & Natiivi Pattern Matching (DAG & Polymorfia):**
    *   Käyttöliittymäkerroksessa (UI) ja Riverpod-logiikassa on ehdottomasti kiellettyä käyttää Freezedin generoimia `.when()`, `.maybeWhen()` tai `.map()` -metodeja. Ne ovat hitaampia legacy-jäänteitä.
    *   Kaikki polymorfiset mallit (esim. Node-strategiat, DAG-askeleet) on määriteltävä Dart 3:n `sealed class` -avainsanalla yhdistettynä `@Freezed(unionKey: 'type')` -annotaatioon.
    *   Tämä siirtää Exhaustive Pattern Matchingin Dartin kääntäjän vastuulle. Tilojen purkuun on käytettävä natiivia `switch (state)` -lauseketta. **Ei varatyylejä (Fallbacks):** UnknownStrategy-tyyppisiä "catch-all" -pakoreittejä ei sallita. Tuntematon JSON-avain kaataa puun heti (Fail-Fast).
2.  **The Isolate Mandate -suojaus (Säikeistyksen säilyttäminen):**
    *   Vaikka Freezed generoi `fromJson` -tehtaat automaattisesti, alkuperäiset `parseInBackground` ja `parseListInBackground` -staattiset metodit ON SÄILYTETTÄVÄ malleissa.
    *   Koodigeneraattori ei poista velvollisuuttamme suojella PC-näkymien "Zero-Latency Illusionia". Freezedin generoima purkulogiikka on edelleen käärittävä `Isolate.run()` -lohkon sisään raskaissa DTO-malleissa (kuten `ExecutionRecord` tai massiiviset RAG-lokit) Main Thread Jankin estämiseksi.
    *   *Isolate Exception Safety:* Kaikkien `AppException.validation` -luokkien tulee olla rakenteeltaan täysin Isolate-siirrettäviä (Sendable), jotta tarkka virhekoodi saadaan kiinni Main Threadin telemetriassa ilman Isolate-kaatumisia.
3.  **Kustomoitujen Konverttereiden Strict-Pariteetti & Exception Unwrapping (RFC 7807):**
    *   Emme luota `json_serializable`:n oletusparsintaan sokeasti. Kaikki kriittiset datatyypit kääritään Strict-konverttereihin (esim. `StrictEnumConverter`, `StrictIListConverter`).
    *   **The No Pass Rule:** Kaikkien kustomoitujen `@JsonConverter`-luokkien heittämien poikkeuksien on oltava täsmälleen muotoa `AppException.validation`.
    *   **Poikkeuksen purku (Unwrap):** Globaalin Error Boundaryn on kaivettava automaattisesti generoidun `CheckedFromJsonException` -virheen sisältä sen `.innerError` esiin, jotta Logfire-telemetria saa oikean RFC 7807 -koodin generoidun virheen sijaan.
4.  **Zero Backward Compatibility & Arkkitehtuurinen Totuus (`seed_data.json`):**
    *   Frontend ei harrasta taaksepäinyhteensopivuutta ("Graceful Degradation"). Tuntemattomien kenttien nielaisu on kielletty (`disallow_unrecognized_keys: true`).
    *   Järjestelmän The Single Source of Truth on lokaali `backend_v2/seed/seed_data.json`. Jos Flutter-malli joutuu ristiriitaan, siemendata tai malli päivitetään vastaamaan toisiaan 100%. Emme piilota virheitä oletusarvoilla.
5.  **Zero-Touch Riippuvuudet (Infrastruktuurin lukitus):**
    *   Projektin `pubspec.yaml` on jäädytetty. Oletamme teollisuusstandardin mukaisten pakettien (`freezed`, `json_serializable`) olevan jo oikeissa versioissaan. Agentit eivät saa koskea asennuksiin versioristiriitojen välttämiseksi.
6.  **Deep Equality -rajoitteet (O(1) RAG-suorituskyky):**
    *   Raskaiden historiataulukoiden (esim. `TraceEvent`) syvävertailu listojen tasolla ohitetaan (`@Freezed(equal: false)`). Riverpodin suorituskyvyn takaamiseksi valtavissa lokeissa vältetään O(N)-tason syvävertailut. Noudattaaksemme Zero-Touch riippuvuussääntöä, emme asenna ulkoista `fast_immutable_collections`-kirjastoa, vaan käytämme natiivia Dart `List<T>` -rakennetta ohitetulla `.==` operaattorilla.

**Päivitettävät tiedostot:** Nämä 6 peruspilaria on ensin päivitettävä tiedostoihin `docs/flutterpromptohje.md` (eritoten lukuihin 2.3 Strict Typing ja 5.8 Dart 3 Pattern Matching), `docs/hardeningfront.md` ja `docs/Arkkitehtuurimäärittely_ AI-orkestraattori V2.md` ennen kooditason refaktoroinnin aloittamista.

### Milestone 1: Infrastruktuuri & Kustomoidut Konvertterit (Zero-Touch & Pydantic Parity)
**Zero-Touch Riippuvuudet:** Projektin `pubspec.yaml` on lukittu. Oletamme teollisuusstandardin mukaisten pakettien (`freezed: ^3.2.3`, `json_serializable: ^6.11.2`) olevan asennettuna. Agentit EIVÄT SAA ajaa asennuskomentoja versioristiriitojen välttämiseksi.

**build.yaml -tiukkuus & DX-Optimointi:** Luodaan/päivitetään projektin juureen `build.yaml`, joka pakottaa koodigeneroinnin globaalisti "Strict"-tilaan vastaten Pydantic V2:n sääntöjä, ja nopeuttaa analysointia Windows-agenttia varten:

```yaml
targets:
  $default:
    builders:
      freezed:
        generate_for:
          - lib/**/models/**.dart
      json_serializable:
        generate_for:
          - lib/**/models/**.dart
        options:
          field_rename: snake # Pydantic pariteetti (esim. org_id -> orgId) ilman boilerplatea
          disallow_unrecognized_keys: true # Pydantic extra="forbid". Backward compatibility on kielletty. Ainoa totuus on seed_data.json.
          any_map: false # Estää JSON-sanakirjojen villin muuntumisen
          checked: true # Fail-fast puuttuville TAI väärän tyyppisille kentille!
          explicit_to_json: true
```

**Standardoitujen Konverttereiden Luominen (`lib/utils/json_converters.dart`):**

*Huom (The No Pass Rule):* Kaikkien näiden luokkien on kaatuessaan heitettävä ehdottomasti `AppException.validation(message: '...', errorCode: 'VALIDATION_FAILED')`. Muut virhetyypit ovat kiellettyjä.

*   `StrictIListConverter<T>`: (Hylätty) Koska noudatamme Zero-Touch riippuvuuksia, käytämme normaaleja `List<T>` rakenteita ryyditettynä `@Freezed(equal: false)` annotaatioilla massiivisissa datajoukoissa estääksemme Riverpod-syvävertailun aiheuttaman hitauden.
*   `StrictDateTimeConverter`: Osattava käsitellä API:n `Stringit` ja Firestoren `Timestampit` turvallisesti lokalisoituun UTC ISO-8601 DateTime -olioon.
*   `StrictEnumConverter`: Heittää välittömästi `AppExceptionin` (eikä hiljaista TypeErroria tai kartoitusta `Enum.unknown` tilaan), jos API/seed data palauttaa odottamattoman Enum-arvon. Zero Backward Compatibility. Oikea korjaustapa on päivittää sovelluksen koodi tai `seed_data.json` vastaamaan toisiaan.
*   `StrictOpaqueIdConverter`: Varmistaa heti RegEx-tasolla JSON-purussa, että viite-ID (esim. `blk_`, `org_`) on aito ja Fail-Fast periaatteen mukainen.

**Poikkeuksien purkaminen (Exception Unwrapping & RFC 7807):**
*   API-kerroksen Error Boundaryn (esim. `lib/core/error/app_error_ext.dart`) pitää napata json_serializablen heittämä `CheckedFromJsonException` ja kaivaa sen `.innerError` -kentästä alkuperäinen `AppException` esiin, jotta Logfire-telemetriaan lähtee oikea RFC 7807 -standardin mukainen virhekoodi pelkän generoidun poikkeuksen sijaan.

### Milestone 1.B: Backendin Siemendatan (Seeder) Tiukennukset
Koska koko arkkitehtuurin **ainoa hyväksytty totuus** on jatkossa `backend_v2/seed/seed_data.json` sekä sen ajuriskripti `run_seed.py`, myös backend-pään validoinnin on vastattava Frontendin "Strict Nirvana" -linjausta.

1.  **Backend vs Frontend Joustavuus (`strict=False` poikkeus):** Vaikka koko arkkitehtuuri pyrkii Pydantic Pariteettiin, backend-mallien oletetaan (käytännön historiadatan pohjalta) olevan joustavampia kuin frontendin. Esim. `V2CoreBase` Enumien Pydantic tyypityksessä sallitaan `strict=False`, jotta TinyDB:n palauttamat raa'at Stringit kääntyvät Enumiksi kaatamatta palvelinta. Frontend (Flutter) on kuitenkin säälimätön Fail-Fast tason tarkistaja Pydantic-tason mukaisesti, eikä anna armoa (`disallow_unrecognized_keys: true`).
2.  **`run_seed.py` Optimointi (validate_python):** Nykyisessä skriptissä purku tehdään raskaasti JSON-käännöksen kautta: `validated = pyd_adapter.validate_json(json.dumps(item))`. Se tulee muuttaa muotoon `validated = pyd_adapter.validate_python(item, strict=True)`. Tämä ei ainoastaan estä turhaa sarjallistamista, vaan `strict=True` pakottaa Pydanticin hylkäämään epäsuorat tyyppimuunnokset (esim. numero `1` ohitetaan jos kenttä vaatii `"1"`), peilaten Dartin tiukkuutta.
3.  **V2 `seed_data.json` Puhdistus:** Kaikki vanhat jäänteet, oletusarvot ja varatyypit (esim. legacy `input_variables`) poistetaan lokaalista `seed_data.json`:sta. Olemassaolevien tyyppien on täsmättävä uusiin dart-konverttereihin. Viallinen data kaataa `run_seed.py` skriptin estäen huonolaatuisen datan päätymisen kantaan (`db_v2.json`).

### Hallittu Siirtymästrategia (Migration Strategy)
Älä yritä migroida kaikkea kerralla (esim. korvaamalla kaikki projektin mallit yhdellä isolla komennolla). Tämä rikkoisi sovelluksen Riverpod-kerrokset ristiin tuottaen satoja ratkeamattomia Type-virheitä "Generation Hell" -tyylillä.

Migraatio suoritetaan tiukasti Domain-alue (skooppi) kerrallaan. Jokaisen askeleen jälkeen ajetaan `flutter test` ja `dart run build_runner build -d`, sekä testataan API-pariteetti:

#### Vaihe 2.A: Autentikaatio & Globaalit Enumit
*   Refaktoroidaan triviaalit ja riippumattomat objektit (esim. `I18nText`, Auth-mallit, `BlockDataType` ja `PromptBlockCategory`).
*   Varmistetaan Enumien `@JsonValue` -pariteetti backendin kanssa.

#### Vaihe 2.B: Workflow & PromptBlock -mallit (Dart 3 Native Pattern Matching)
Uudelleenkirjoitetaan nykyinen käsin koodattu PromptBlock tiiviiksi Freezed-malliksi.

**Sealed Classes Mandate:** Korvataan Pydantic-tason DAG Discriminatorit hyödyntämällä Freezedin ja Dart 3:n hybridimallia (`@Freezed(unionKey: 'type') sealed class NodeStrategy`). Polymorfisille luokille **ei sallita** `Unknown/Fallback` -tyyppejä. Tuntematon JSON-avain kaataa purkamisen välittömästi (Fail-Fast), ja korjaus tehdään aina päivittämällä asiat synkroniin (`seed_data.json` vs. Dart-mallit). Oikopolkuja tai oletusarvoja tuntemattomille tyypeille ei tueta.

Varmistetaan, että UI-kerroksessa **ei käytetä** Freezedin generoimaa `.when()`-metodia, vaan pakotetaan kaikki koodi käyttämään natiivia Dart 3 `switch (state)` -lauseketta Exhaustive Pattern Matchingin varmistamiseksi.

Sovelletaan standardoituja Konverttereita (`StrictEnumConverter`, `StrictDateTimeConverter`) turvaamaan Matrix-säännöstöjen eheys.

#### Vaihe 2.C: UI-kerroksen ja Formien Siivous
*   Poistetaan väliaikaiset "De-Generator / Map" -hakkerit käyttöliittymästä (`PromptBlockBuilderView`, jne.)
*   **Teknisen velan tuhoaminen:** Vanha `client_app_v2/lib/utils/safe_cast.dart` merkitään `@deprecated`-annotaatiolla. Kun kaikki parse-kutsut on asennettu käyttämään uusia Strict-konverttereita, asiantila varmistetaan poistamalla legacy-käsittelijä lopulta koodikannasta kokonaan ohitusten estämiseksi.
*   Varmistetaan Riverpod 3.0:n Optimistic UI toimii luontevasti Freezedin syväkopioinnin (`deepCopy`) ja tuodun `Equatable`-luokan tuottaman Deep Equality (`==`) kera.

#### Vaihe 2.D: ExecutionEngine & Raskaat RAG-mallit (Isolate Mandate & O(1) Rajoitteet)
Skaalataan arkkitehtuuri ajonaikaisiin entiteetteihin (`ExecutionRecord`, `TraceEvent`).

**The Isolate Mandate -suojaus:** Vaikka mallit muutetaan Freezed-pohjaisiksi, niiden vanhat staattiset `parseInBackground` ja `parseListInBackground` -metodit on pakko säilyttää. Nämä käärivät Freezedin purkuoperaation `Isolate.run()` -säikeeseen taaten nollaviiveen illuusion (Zero-Latency Illusion) raskaissa lokeissa.

**Deep Equalityn Ohitus (Natiivi List & Zero-Touch):** Kunnioitamme tiukasti "Zero-Touch" -sääntöä (`pubspec.yaml` riippuvuuksiin ei kosketa), joten emme asenna `fast_immutable_collections`-pakettia. Sen sijaan otamme valtavien natiivien luettelojen `.==` -automaation pois päältä raskaissa malleissa (`@Freezed(equal: false)`). Tämä ohittaa Riverpodin hitaan O(N) iteraation RAG-lokeissa suorituskyvyn pelastamiseksi.

---

## Määritelmä Valmiille (Definition of Done)
1. **Zero-Map Tavoite:** `lib/models/` hakemiston alla olevista domain-malleista on kokonaan hävitetty manuaaliset `Map<String, dynamic>` iteraatiot ja manuaalilogiikat.
2. **Kääntäjäystävällisyys:** `dart run build_runner build --delete-conflicting-outputs` menee läpi puhtaasti ilman Type Cast -varoituksia.
3. **Fail-Fast Pariteetti (`seed_data.json`):** Emme tue taaksepäinyhteensopivuutta (ei `Enum.unknown` -fallbackeja tai tuntemattomien kenttien nielaisuja). Ainoa hyväksyttävä totuus on `backend_v2/seed/seed_data.json` ja lokaalin tietokannan initialisointi (`run_seed.py local`). Viallinen tietu synnyttää täsmälleen saman virheviestin ("Missing Field X in JSON") kuin ennenkin, kiitos kustomoitujen kääntäjien (`@JsonConverter`). Tarvittaessa `seed_data.json` päivitetään vastaamaan uusia tiukkoja malleja.
4. **Dev-kokemus (DX):** Koodin laatu ja ylläpidettävyys ovat harpanneet eteenpäin poistaen 'Generation Hell' -riskit jättäen sen pelkäksi tehokkaaksi työkaluksi täyden kontrollin alla.
5. **Arkkitehtuuriset Rajat (Boundaries) vahvistettu:** Freezed on otettu 100% käyttöön DTO-malleissa ja monimutkaisissa Riverpod-tiloissa (State Unions), mutta sen käyttö on **ehdottomasti kielletty** logiikkaa sisältävissä luokissa (kuten `*Service`, `*Repository`, `*Client` tai Riverpod `@riverpod class` Notifierit itse).
    *   **Perustelu (Miksi?):** Freezed on suunniteltu *immutaabelin muodon* (Data Classes) turvaamiseen, syvävertailuun (Deep Equality) ja vaivattomaan kopiointiin `.copyWith`. Riverpod Notifierit ja Servicet sen sijaan ohjaavat *käyttäytymistä* asynkronisten metodien kautta ja pitävät sisällään elinkaaren (`build()`, `dispose()`). Freezedin pakottaminen logiikkaluokkiin rikkoisi "Data vs. Behavior" -periaatteen synnyttäen jättiluokkia (God-Classes) ja valtavasti tarpeetonta boilerplatea kahden singletonin täysin tarpeettomia vertailuja varten.

---
**HUOMIO OS-YMPÄRISTÖSTÄ (Windows 11):**
Kaikki automatiikan suorittamat `dart run` askeleet tulee listata ohjeena dokumentteihin eksplisiittisesti puolipisteellä eroteltuna tai manuaalisesti ajettaviksi, koska Antigravity 1.21.6 agentti ei voi käynnistää powershell-makroja suoraan käyttöjärjestelmärajoitteiden vuoksi.
