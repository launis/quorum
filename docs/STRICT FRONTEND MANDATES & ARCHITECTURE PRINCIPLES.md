# CONTEXT & ROLE
Olet kokenut ohjelmistoarkkitehti ja senior-tason Flutter/Dart-kehittäjä (Staff Engineer). Olemme aiemmin saaneet valmiiksi backendin refaktoroinnin, ja nyt tehtävänäsi on laatia minulle erittäin yksityiskohtainen, askeleittainen refaktorointisuunnitelma (Execution Plan) projektimme Flutter-käyttöliittymän (Frontend / `client_app`) uudistamiseksi.

# PÄÄTAVOITE: CRUD- JA LISTANÄKYMIEN ARKKITEHTUURINEN STANDARDOINTI (2026 MANDAATTI)
Tavoitteena on analysoida, refaktoroida ja standardoida sovelluksen kaikki datavetoiset listaukset, relaatiot ja CRUD-operaatiot (Create, Read, Update, Delete) vastaamaan projektin tiukkoja arkkitehtuurimandaatteja. 

Tässä poistetaan kaikki vanhentunut tilanhallinta (Legacy Providers, `ChangeNotifier`), massiiviset "kaikki-kerralla" -kyselyt ja raakamerkkijonoihin perustuva reititys. Tilalle implementoidaan Riverpod 3.0 -standardin mukainen `@riverpod`-koodigenerointi, mutaatioiden 'Optimistic Update' -malli, relaatioiden puhtaasti reaktiivinen "Matrix"-lähestymistapa, tyyppiturvallinen GoRouter-navigaatio (`GoRouteData`) sekä suorituskykyä turvaava `Isolate.run()` -tausta-ajo raskaalle datalle. Jokainen näkymä on päivitettävä käsittelemään virheet ja lataustilat deklaratiivisesti `.when()` -metodilla ja keskitetyllä `ErrorView`-komponentilla.

ÄLÄ ALOITA KOODIN MUOKKAAMISTA VIELÄ. Luo minulle ensin ainoastaan tämä tiekartoitus.

---

# STRICT FRONTEND MANDATES & ARCHITECTURE PRINCIPLES
Koko suunnitelman ja kaiken tulevan koodauksen on noudatettava täydellisesti projektin ohjeistoa (`docs/flutterpromptohje.md`). Erityisesti seuraavat mandaatit ovat nyt keskiössä:

### 1. PART 4.1.1: State Management, Optimistic Updates & Declarative UI
- **Riverpod 3.0 & .when():** Kaikki vanhat `ChangeNotifier`, `StateProvider` ja manuaaliset providerit OVAT KIELLETTYJÄ. Tilanhallinta on päivitettävä käyttämään yksinomaan `@riverpod`-generaattoria ja Notifier-arkkitehtuuria. UI:ssa on PAKKO käyttää `AsyncValue.when()` -metodia lataus- ja virhetilojen deklaratiiviseen esittämiseen. Manuaaliset `if (isLoading)` tai `if (hasError)` -tarkistukset build-metodeissa on poistettava.
- **Mutaatiot (Optimistic Updates):** Kaikkiin datan muutoksiin (tallennus/päivitys/poisto verkon yli) on pakko toteuttaa "Optimistic Update + Silent Sync + Rollback" -malli. Käyttöliittymän pitää reagoida heti muuttamalla lokaalia tilaa, mutta virhetilanteessa tilan on palauduttava automaattisesti edelliseen ja nostettava virhe ylös.

### 2. PART 4.1.2: Relaatiodatan hallinta (The Simple "Matrix" Approach)
Relaatioita sisältävien näyttöjen käsittely on EHDOTTOMASTI tehtävä best-practice -tyylillä, yksinkertaista Riverpod-arkkitehtuuria hyödyntäen.
- **KIELLETTY (The Broken Complex Approach):** Älä koskaan hae useita riippuvuuksia (esim. Prompts, Agents, Output Settings) täsmälleen samaan aikaan yhdessä massiivisessa `Future.wait` -taulukossa yhden monoliittisen ohjaimen (esim. vanhan `StudioControllerin`) sisällä. Tämä aiheuttaa "Riverpod State Synchronization" -bugin. Vaikka data latautuisi API:sta onnistuneesti, UI ei saa tietoa synkronoidusti, vaan ruudulle jäätyy pysyvästi virhetiloja (esim. punaisia "Missing ID" -laatikoita) ja sovellus luulee tilan olevan tyhjä.
- **VAADITTU (The Simple "Matrix" Approach):** Relaatiot on jaettava erillisiin, yksinkertaisiin ja natiivisti reaktiivisiin Riverpod 3.0 `AsyncNotifier` -luokkiin. Rakenna dedikoituja ohjaimia (kuten erillinen `AvailableComponentsController`), jotka heijastavat puhdasta Matrix-käyttöliittymätyyliä. Jokainen ohjain huolehtii vain omasta datastaan.
- **TULOS:** Koska uusi ohjain on yksinkertainen ja dedikoitu, Riverpod päivittää UI:n automaattisesti: sillä sekunnilla kun taustadata latautuu, punaiset virhelaatikot muuttuvat välittömästi oikeiksi `GLOBAL_CONTEXT` ja `MANDATE` -chipeiksi ja dialogit (esim. "Add Prompt") täyttyvät oikealla datalla reaaliajassa. *Joskus yksinkertaisin, kokeiltu arkkitehtuuri on yksinkertaisesti paras.*

### 3. PART 4.2 & 4.3: Type-Safe Routing & Non-Blocking Network
- **GoRouter:** Raakojen merkkijonoreittien (esim. `context.push('/home')`) käyttö on EHDOTTOMASTI KIELLETTY. Kaikki reititys on tehtävä tyyppiturvallisesti `GoRouteData`-luokkien avulla.
- **Guard Clauses:** Reitinvalintalogiikka ja käyttöoikeustarkistukset on siirrettävä reitittimen `redirect`-funktioon. Niitä ei saa käsitellä UI-komponenttien `build()`-metodeissa.
- **Isolates (Dart 3.11):** Raskas API JSON -parsiminen (erityisesti raskaiden listojen latauksessa) on siirrettävä pois pääsäikeestä (Main UI Thread) käyttäen modernia `Isolate.run(...)` -komentoa. Vanha `compute()`-funktio on kielletty.

### 4. PART 7.1 & 4.4: Responsiveness & Theming
- **Responsiivisuus:** Järjestelmään on koodattava tiukka 600dp:n taitekohta (Breakpoint). Yli 600dp (Desktop) käyttää `NavigationRail` + `VerticalDivider` ja sisällön maksimileveys on 1000dp. Alle 600dp (Mobile) käyttää `NavigationBar`.
- **Teemoitus:** Manuaalinen `ThemeData` on kielletty. Sovelluksen teema on toteutettava kokonaan `FlexColorScheme` -paketilla.

### 5. PART 3.7, 5.2 & 15.1: Resilience, Fallbacks & Developer Visibility
- **ErrorView:** Ad-hoc virheilmoitukset (esim. `Center(child: Text('Error'))`) ovat kiellettyjä. Kaikki UI-virheet (erityisesti `.when(error: ...)` -haaroissa) ohjataan standardoidun `ErrorView`-widgetin kautta.
- **Graceful Degradation (BFF/UI):** Koko näyttö ei saa kaatua yhteen puuttuvaan widgettiin. Komposiittinäkymissä sallitaan fallback (esim. `SizedBox.shrink()`), MUTTA sen yhteydessä on EHDOTTOMASTI tulostettava konsoliin `debugPrint('🔴 UI GRACEFUL DEGRADATION: ...')`, jotta virheet eivät piiloudu kehittäjiltä.
- **Timeouts:** Yli 10 sekuntia kestävissä operaatioissa on oltava Progress Bar -komponentti. "Zombie"-prosesseja (ikuisia latausruutuja ilman timeoutia) ei sallita.

### 6. PART 17 & 7.3: Hygiene & Asynchronous Storage
- **Kieli:** Kaikki koodi, muuttujat ja koodikommentit on kirjoitettava YKSINOMAAN englanniksi (vain `.arb`-tiedostot saavat sisältää lokalisoitua tekstiä).
- **Asetukset:** Kielen ja teeman tallennus on päivitettävä käyttämään modernia asynkronista `SharedPreferencesAsync`-rajapintaa, ei blokkaavaa luku/kirjoitusta.

---

# EXECUTION PLAN REQUIREMENTS (Suunnitelman rakenne)

Analysoi `client_app/`-hakemisto (erityisesti kaikki List- ja CRUD-näkymät sekä monimutkaiset relaatiota sisältävät näkymät) ja laadi frontend-refaktoroinnista erittäin yksityiskohtainen Master Plan. Jaa työ todella pieniin, **yksittäisinä ajoina (single run) suoritettaviin askeliin**. Jatkamme numerointia aiemmasta backend-suunnitelmasta, joten aloita askeleesta **Step 6.5**.

Etene seuraavan tiekartan mukaisesti. Voit pilkkoa nämä aiheet tarvittaessa ominaisuuskohtaisiin (per feature/domain) alakohtiin (esim. 6.5.1 Auth, 6.5.2 Workflows, 6.5.3 Organizations), jotta yksittäinen askel ei kasva liian suureksi yhdellä kerralla toteutettavaksi.

- **Step 6.5:** CRUD- ja listanäkymien standardointi (Riverpod 3.0, Optimistic Update ja `.when()` deklaratiivisuus domaineittain).
- **Step 6.6:** Relaatioita sisältävien näyttöjen korjaus "Matrix" -lähestymistavalla (Massiivisten `Future.wait` monoliittien purkaminen yksinkertaisiksi dedikoiduiksi `AsyncNotifier` providereiksi tilasynkronointibugien estämiseksi).
- **Step 6.7:** GoRouterin tyyppiturvallisuus (Type-Safe Routing listauksista detaljeihin `GoRouteData` avulla).
- **Step 6.8:** UI:n responsiivisuus ja teemoitus (FlexColorScheme ja 600dp säännöt).
- **Step 6.9:** Raskaiden CRUD/API-operaatioiden JSON-tausta-ajo (`Isolate.run`) ja Timeout-UI.
- **Step 6.10:** Keskitetty `ErrorView` ja Developer Visibility (UI Degradation varoitukset `debugPrint`).
- **Step 6.11:** Asetusten asynkroninen tallennus (`SharedPreferencesAsync`).

Jokaisen askeleen on oltava eristetty, jotta se voidaan suorittaa ja testata rikkomatta Flutter-sovelluksen kääntymistä.

**Jokaisesta askeleesta on ilmettävä selkeästi:**
1. **Askeleen tunniste ja nimi** (esim. "Step 6.6.1: Monoliittisen StudioControllerin relaatioiden purku Matrix-arkkitehtuuriin").
2. **Kohdetiedostot:** Mitä tiedostoja, kansioita ja luokkia tässä askeleessa tarkalleen käsitellään.
3. **Tavoitteet ja toimenpiteet (Mitä, Miksi & Mandates):** Mitä konkreettisesti muutetaan. **PERUSTELE AINA** viittaamalla ohjeiston Mandaatteihin ja alussa mainittuun Päämäärään. Esim. *"Puretaan massiivinen Future.wait-haku erillisiin reaktiivisiin providereihin (esim. AvailableComponentsController). Tämä korjaa Riverpodin synkronisaatiobugin The Simple Matrix Approach -säännön mukaisesti, jotta puuttuvat komponentit päivittyvät välittömästi käyttöliittymään."*
4. **Testit ja varmennus:** Miten varmistamme terminaalissa VÄLITTÖMÄSTI askeleen suorituksen jälkeen, että muutos onnistui. Määrittele tarkat komennot (esim. `dart run build_runner build -d`, `dart run custom_lint` tai komento jolla etsitään poistettuja rakenteita kuten `context.push`, vanhoja `isLoading` if-lauseita tai `Future.wait` koodilohkoja tilanhallinnasta).

Luo nyt tämä vaiheistettu Frontend Master Plan. Odotan, että perkaat frontend-kansion tarkasti läpi ja kohdistat askeleet suoraan olemassa olevaan logiikkaan. Kun olet valmis, jää odottamaan, että annan sinulle erillisen käskyn aloittaa "Step 6.5.1:n" suorittamisen. Älä koodaa tai muokkaa tiedostoja vielä.