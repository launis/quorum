# Epic 12: Frontend Domain Model Freezed Migration (Strict Nirvana Validation)

## Tilannekatsaus (Background)
Cognitive Quorum V2 käyttää Flutter-frontendissä tiukkaa "De-Generator Mandate" -arkkitehtuuria. Tämä tarkoittaa, että luokkien serialisointi (`fromJson`, `toJson`), kopiointi (`copyWith`) ja identiteettivertailut (`==`) on ohjeistettu tehtäväksi tiukasti käsin koodattuna puhtaan Tyyppiturvallisuuden (Pydantic V2 -pariteetti) ja välittömän virheiden kiinnioton (Fail-Fast) saavuttamiseksi.

Käsin koodatun mallin (esim. 300-rivinen `PromptBlock`) ylläpidettävyys, skaalautuvuus ja virhealttius uusien kenttien lisäämisessä ovat kuitenkin osoittautuneet merkittäväksi pullonkaulaksi. Kehittäjäkokemus ja koodin puhtaus kärsivät. 

## Tavoite (Objective)
Siirrytään käyttämään Flutterin teollisuusstandardia, **Freezed** ja **JSON Serializable** -koodingenerointia, kaikkien laitteen (Frontend) Domain-mallien (`PromptBlock`, `Workflow`, `ExecutionRecord`) ylläpidossa. 

**Kriittinen edellytys:** Muutos **EI SAA** heikentää "Strict Nirvana" tai "Fail-Fast" -periaatteita. Emme luota `json_serializable`:n oletusarvoiseen parsintaan sokeasti. Sen sijaan koodiin integroidaan kustomoidut `@JsonConverter`-luokat, jotkat käärivät nykyisen `SafeCast`-logiikkamme sisäänsä. Näin saamme koodingeneroinnin tuoman valtavan boilerplaten poiston (hyöty), mutta säilytämme täydellisen poikkeustenhallinnan tietoturvan ja tyyppien eheyden (Fail-Fast).

---

## Toteutussuunnitelma (Tier-1 Milestones)

### Milestone 0: Arkkitehtuuridokumentaation päivitys (Phase 9 Hardening)
Ennen varsinaista koodimuutosta päivitetään projektin ydindokumentaatio vastaamaan uutta teollisuusstandardia (Freezed + Custom Converters Riverpod-sovelluksissa). Tämä kumoaa aiemman laajan "De-generator" (manuaalinen `Map<String, dynamic>`) mandaatin.

**Tärkeimmät uudet arkkitehtuurisäännöt, jotka on päivitettävä ohjeisiin:**
1. **CQRS-Polymorfia:** Ohjeistetaan, että `StrictDateTimeConverter` (ja vastaavat) on osattava purkaa Data dynaamisesti (API:n `String` vs. Firestoren `Timestamp`), jotta luetut mallit toimivat molemmissa tietolähteissä.
2. **Deep Equalityn rajoittaminen (RAG):** Kielletään raskaiden historiataulukoiden (esim. `TraceEvent`) syvävertailu (`@Freezed(equal: false)`) ja siirretään ne `fast_immutable_collections` (`IList`) -muotoon Riverpod-säikeiden jäätymisen estämiseksi.
3. **DAG-reitityksen Discriminator-pariteetti:** Pakotetaan `@Freezed(unionKey: 'type')` polymorfisiin malleihin (esim. Node-strategiat) Exhaustive Pattern Matchingin (`.when()`) varmistamiseksi UI-kerroksessa.
4. **Telemetria ja Dual-Reporting:** Määritellään, että kun `CheckedFromJsonException` napataan, järjestelmä poimii alkuperäisen viitteen (Opaque ID) ja lähettää asynkronisen telemetrian Backendin Logfire-järjestelmään pelkän nätin UI-virheen lisäksi.
5. **Nimistön Opaque ID Mandaatti:** Hylätään sana "Safe" nimistössä (implying defensiivinen nielaisu) -> Käytetään muotoa "Strict". Luodaan `StrictOpaqueIdConverter`, joka kaataa purun heti RegEx-tasolla vääränlaisesta ID:stä.
6. **DX-Optimointi:** Määritellään, että LLM-agenttien nopeuttamiseksi Windows-ympäristössä `build.yaml` pakotetaan rajoittamaan generointi vain malleihin (`generate_for`).

*   Päivitettävät tiedostot: `docs/flutterpromptohje.md`, `docs/hardeningfront.md`, `docs/hardeningback.md`, `docs/antigravity_prompting.md`, `docs/Arkkitehtuurimäärittely_ AI-orkestraattori V2.md`. Näihin sisällytetään yllä mainitut 6 uutta arkkitehtuuriperiaatetta.

### Milestone 1: Infrastruktuuri & Kustomoidut Konvertterit (Pydantic Parity)
*   Asennetaan `freezed`, `freezed_annotation`, `json_annotation` dev-riippuvuuksina yhdessä `build_runner`:in kanssa.
*   **build.yaml -tiukkuus & DX-Optimointi:** Luodaan projektin juureen `build.yaml`, joka pakottaa koodigeneroinnin globaalisti "Strict"-tilaan vastaten Pydantic V2:n sääntöjä, ja nopeuttaa analysointia Windows-agenttia varten:
    ```yaml
    targets:
      $default:
        builders:
          source_gen|combining_builder:
            generate_for:
              - lib/**/models/**.dart # Pakottaa kääntäjän ohittamaan raskaat UI-tiedostot, säästäen LLM:n timeoutteja
          json_serializable:
            options:
              disallow_unrecognized_keys: true # Pydantic extra="forbid"
              any_map: false # Estää JSON-sanakirjojen villin muuntumisen
              checked: true # Pakottaa heittämään CheckedFromJsonException puuttuvista
              explicit_to_json: true
    ```
*   **Standardoitujen Konverttereiden Luominen (`lib/utils/json_converters.dart`):**
    *   `StrictDateTimeConverter`: CQRS Polymorfinen muunnos, joka osaa dynaamisesti käsitellä API:n `Stringit` ja Firestoren `Timestampit` turvallisesti lokalisoituun UTC ISO-8601 DateTime -olioon.
    *   `StrictEnumConverter`: Heittää välittömästi AppExceptionin (eikä hiljaista TypeErroria), jos API palauttaa odottamattoman Enum-arvon.
    *   `StrictOpaqueIdConverter`: Varmistaa heti RegEx-tasolla JSON-purussa, että tietokannan viite-ID (esim. `blk_`, `org_`) on aito ja turvallinen Fail-Fast periaatteen mukaisesti.
    *   Universaalit Strict-kääreet: `StrictStringConverter`, `StrictIntConverter`, `StrictListConverter` (jotka pakottavat epäselvätkin tyypit vanhan rakenteellisen Fail-Fast-logiikkamme läpi turvautumatta "Safe" nielaisuun).
*   **RFC 7807 Verkkovirheiden Käsittely (`api_client.dart`):** Lisätään verkko- ja JSON-purkukerrokseen globaali kaappari `CheckedFromJsonException`-virheille. Järjestelmä paketoi virheen nättiin `AppException.validation` viestiin UI:n puolelle, **MUTTA poimii virheestä viallisen avaimen ja Opaque ID:n lähetettäväksi taustalla Backendin Logfire-telemetriaan (Dual-Reporting)**.

### Hallittu Siirtymästrategia (Migration Strategy)
Älä yritä migroida kaikkea kerralla (esim. korvaamalla kaikki projektin mallit yhdellä isolla komennolla). Tämä rikkoisi sovelluksen Riverpod-kerrokset ristiin tuottaen satoja ratkeamattomia Type-virheitä "Generation Hell" -tyylillä.

Migraatio suoritetaan tiukasti Domain-alue (skooppi) kerrallaan. Jokaisen askeleen jälkeen ajetaan `flutter test` ja `dart run build_runner build -d`, sekä testataan API-pariteetti:

#### Vaihe 2.A: Autentikaatio & Globaalit Enumit
*   Refaktoroidaan triviaalit ja riippumattomat objektit (esim. `I18nText`, Auth-mallit, `BlockDataType` ja `PromptBlockCategory`).
*   Varmistetaan Enumien `@JsonValue` -pariteetti backendin kanssa.

#### Vaihe 2.B: Workflow & PromptBlock -mallit (Polymorphic Pattern Matching)
*   Uudelleenkirjoitetaan nykyinen käsin koodattu `PromptBlock` tiiviiksi Freezed-malliksi.
*   Korvataan Pydantic-tason DAG Discriminatorit hyödyntämällä Freezedin Sealed Classes / Union Typeseja (`@Freezed(unionKey: 'type')`), jolla kääntäjä pakotetaan vaatimaan `.when()`-tarkistukset koko UI-kerrokseen.
*   Sovelletaan standardoituja Konverttereita (`StrictEnumConverter`, `StrictDateTimeConverter`) turvaamaan Matrix-säännöstöjen eheys.

#### Vaihe 2.C: UI-kerroksen ja Formien Siivous
*   Poistetaan väliaikaiset "De-Generator / Map" -hakkerit käyttöliittymästä (`PromptBlockBuilderView`, jne.)
*   Varmistetaan Riverpod 3.0:n Optimistic UI toimii luontevasti Freezedin syväkopioinnin (`deepCopy`) ja tuodun `Equatable`-luokan tuottaman Deep Equality (`==`) kera.

#### Vaihe 2.D: ExecutionEngine & Raskaat RAG-mallit (O(1) Rajoitteet)
*   Skaalataan arkkitehtuuri ajonaikaisiin entiteetteihin (`ExecutionRecord`, `TraceEvent`). Varmistetaan The Isolate Mandate -purkunopeudet.
*   **Deep Equalityn Ohitus:** Otetaan tässä mittakaavassa `.==` automaatiot pois päältä raskaista listoista (`@Freezed(equal: false)`). Riverpodin suorituskyvyn takaamiseksi valtavissa RAG-lokeissa pakotetaan Listat käyttämään `fast_immutable_collections` (`IList`) -rakennetta, turvaten käyttöliittymän 144Hz renderoinnin.

---

## Määritelmä Valmiille (Definition of Done)
1. **Zero-Map Tavoite:** `lib/models/` hakemiston alla olevista domain-malleista on kokonaan hävitetty manuaaliset `Map<String, dynamic>` iteraatiot ja manuaalilogiikat.
2. **Kääntäjäystävällisyys:** `dart run build_runner build --delete-conflicting-outputs` menee läpi puhtaasti ilman Type Cast -varoituksia.
3. **Fail-Fast Pariteetti:** Viallinen database-siemen synnyttää täsmälleen saman virheviestin ("Missing Field X in JSON") kuin ennenkin, kiitos kustomoitujen kääntäjien (`@JsonConverter`).
4. **Dev-kokemus (DX):** Koodin laatu ja ylläpidettävyys ovat harpanneet eteenpäin poistaen 'Generation Hell' -riskit jättäen sen pelkäksi tehokkaaksi työkaluksi täyden kontrollin alla.
5. **Arkkitehtuuriset Rajat (Boundaries) vahvistettu:** Freezed on otettu 100% käyttöön DTO-malleissa ja monimutkaisissa Riverpod-tiloissa (State Unions), mutta sen käyttö on **ehdottomasti kielletty** logiikkaa sisältävissä luokissa (kuten `*Service`, `*Repository`, `*Client` tai Riverpod `@riverpod class` Notifierit itse).
    *   **Perustelu (Miksi?):** Freezed on suunniteltu *immutaabelin muodon* (Data Classes) turvaamiseen, syvävertailuun (Deep Equality) ja vaivattomaan kopiointiin `.copyWith`. Riverpod Notifierit ja Servicet sen sijaan ohjaavat *käyttäytymistä* asynkronisten metodien kautta ja pitävät sisällään elinkaaren (`build()`, `dispose()`). Freezedin pakottaminen logiikkaluokkiin rikkoisi "Data vs. Behavior" -periaatteen synnyttäen jättiluokkia (God-Classes) ja valtavasti tarpeetonta boilerplatea kahden singletonin täysin tarpeettomia vertailuja varten.

---
**HUOMIO OS-YMPÄRISTÖSTÄ (Windows 11):**
Kaikki automatiikan suorittamat `dart run` askeleet tulee listata ohjeena dokumentteihin eksplisiittisesti puolipisteellä eroteltuna tai manuaalisesti ajettaviksi, koska Antigravity 1.21.6 agentti ei voi käynnistää powershell-makroja suoraan käyttöjärjestelmärajoitteiden vuoksi.
