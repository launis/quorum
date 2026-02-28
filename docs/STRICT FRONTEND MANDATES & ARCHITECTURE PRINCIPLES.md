# STRICT FRONTEND MANDATES & ARCHITECTURE PRINCIPLES (FLUTTER)

Tämä dokumentti määrittelee Cognitive Quorum -asiakassovelluksen (Flutter/Dart) ehdottomat arkkitehtuurisäännöt.

## 1. STATE MANAGEMENT & DECLARATIVE UI
- **Riverpod 3.0 & Immutability:** Tilanhallinta käyttää yksinomaan tuoretta `@riverpod`-koodigeneraattoria ja puhtaita `AsyncNotifier`-luokkia. `ChangeNotifier` ja lokaali tila laajalle levinneen datan hallintaan on ehdottomasti kielletty.
- **Deklaratiivinen käsittely (.when):** Kaikki asynkroninen tieto on piirrettävä käyttöliittymään noudattaen formaalia mallia: `ref.watch(provider).when(data: ..., loading: ..., error: ...)`. Manuaaliset `if (isLoading)` tai `if (hasError)` -tarkistukset vältetään.
- **Relaatiodatan hallinta (The Simple "Matrix" Approach):** Riippuvuuksia ei varastoida massiivisiin `Future.wait` monoliitteihin, jotka aiheuttavat tilasynkronisaatiobugeja (esim. StudioControllerin jäätyminen). Data jaetaan litteisiin, natiivisti reaktiivisiin providereihin. "Yhden providerin tulisi ladata yksi asia."

## 2. OPTIMISTIC UPDATES & BFF RESILIENCE
- **Mutaatiot (Optimistic Updates):** Datan luontiin, muokkaukseen tai poistoon liittyvissä operaatioissa välimuisti päivityksineen tehdään heti (optimistisesti) ennen verkkokutsua. Jos verkko-operaatio epäonnistuu, tila palautetaan (rollback) automaattisesti ja nostetaan virhe.
- **Graceful Degradation (BFF/UI):** Komposiittinäkymissä sallitaan "Fallback"-komponenttien käyttö (esim. tyhjän `SizedBox.shrink()` palauttaminen viallisen datan sijaan), EDELLYTTÄEN, että virhe ilmoitetaan konsoliin näkyvästi kehittäjille (`debugPrint('🔴 UI GRACEFUL DEGRADATION: ...')`). Koko näkymä ei saa koskaan kaatua yhden puuttuvan avaimen takia.
- **ErrorView:** Kaikki virheet (`.when(error: ...)`) ohjataan standardoidun kokonäytön tai osittaisen näytön `ErrorView`-widgetin kautta, joka osaa näyttää AppExceptionien vikakoodit ymmärrettävästi.

## 3. TYPE-SAFE ROUTING (GoRouteData)
- **Generointi:** Kaikki reitityssovelluksen URL-konfiguraatiot määritellään tyyppiturvallisesti `GoRouteData`-luokissa. Suora merkkijonopohjainen reititys (esim. `context.push('/home')`) on ehdottomasti kielletty.
- **Guard Clauses:** Reitinvalintalogiikka, tila- ja käyttöoikeustarkistukset keskitetään reitittimen `redirect`-funktioon, ei manuaalisiin `build()`-luokkiin.

## 4. INTERNATIONALIZATION (I18N) NO-STRING MANDATE
- **Frontendin yksinoikeus:** Vain ja ainoastaan Frontend (`lib/l10n/app_fi.arb`) sisältää UI:ssa näkyvän, lokalisoidun tekstin. Backend toimittaa pelkät avaimet.
- **ICU Formatting & No Hacks:** Datan ja käännösten yhdistäminen manuaalisesti koodissa (esim. `Text("Score: " + val.toString())`) on ankarasti KIELLETTY. Kaikki variaatiot hoidetaan käännöstiedoston ICU-syntaksilla (esim. `"scoreVal": "Score: {val}"`).
- **Muuttujat:** Monimutkaiset säännöt, kuten Plurals (Monikot), ovat ohjattavissa vain ja ainoastaan `.arb`-tiedoston avulla.

## 5. PERFORMANCE & RESPONSIVENESS
- **Asynchronous Storage:** Asetusten, kuten teeman ja kielen, lukeminen tai tallennus hyödyntää `SharedPreferencesAsync`-rajapintaa, joka estää päälangan hidastumisen IO-operaatioiden aikana.
- **Isolates (Tausta-ajot):** Yli 16 ms kestävät massiiviset JSON API -parsinnat (esim. valtavat listatut relaatiot) erotetaan käyttöliittymän säikeestä (UI Thread) modernilla `Isolate.run(...)` -komennolla.
- **Responsiveness Breakpoint:** Järjestelmä asettaa rajan `600dp` pöytäkone-/tablettikokoonpanon (`NavigationRail`) ja mobiilin (`NavigationBar`) välille.
- **Teemoitus:** App-teema käyttää yksinomaan dynaamista, automaattisesti generoituvaa `FlexColorScheme` -kirjastoa. Manuaalinen värien ja elementtien hardkoodaus `ThemeDataan` on kielletty, ellei sitä ole otettu suoraan teemasta `Theme.of(context)`.