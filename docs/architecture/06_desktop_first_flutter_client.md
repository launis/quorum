# 06: Esityskerros (Desktop-First Flutter) ja Kognitiivinen Monikielisyys

Järjestelmän käyttöliittymän (`client_app_v2`) arkkitehtuuri ei sisällä tekoälyn laskentareittejä (Zero-Math), vaan toimii näyttölasina (Backend-For-Frontend) täysin tyyppiturvallisessa (Type-Safe Freezed) muistissa. 

## Esityskerros (Adaptive BFF - Flutter & Riverpod)

Koko käyttöliittymä nojaa **Desktop-First** ja **IDE Pro-Tool** -filosofioihin. Käyttäjä on asiantuntija.
1. **Stateful Nested Navigation (GoRouter):** Työpöytänäkymän navigaatio nojautuu `StatefulShellRoute` -rakenteeseen. "InitialData" -syöttäminen (objektien puskeminen sivujen väliin) on sallittua vain lukkovaiheisilla Opaque Stripe ID:illä.
2. **Zero-Latency IAM UI (SWR):** Asetusikkunat hyödyntävät puhdasta Stale-While-Revalidate (Riverpod) -matriisia. Optimistiset päivitykset poistavat blokkaavat latausanimaatiot.
3. **The Isolate Mandate:** Järjestelmä siirtää monimutkaiset JSON-parsinnat asynkroniseen Dart Isolette -työkalulle ohi UI-säikeestä estämään PC-näyttöjen latenssivärinöitä.
4. **Zero-Math / Micro-CoT Flattening:** UI (Flutter) ei laske logiikkaa tai numeroita, vaan luottaa Backendiin Hookkien valmiiksi palauttamaan Pydantic valmiiseen Data-objektiin.

## Kognitiivinen Monikielisyys (The 5-Layer Strategy)
Järjestelmä viipaloi luonnollisen kielen kognitiivisen ytimen käännöksistä:
1. **Compile-Time L10n:** `.arb` kääntää natiivin valikon tai napit käskykirjastoilla ("Edit values, never keys").
2. **Runtime Payload:** Frontend ei tee tekoälyn datan kääntämistyötä, API generoi ja vastaa mallista saadut käännökset ajonaikaisella JSONilla.
3. **English-Only Mandate:** Tekoälyn The Deep Engine (The Blind Audit arviointi ja System Prompt) kirjoitetaan **vain** ja ainoastaan englanniksi parhaan laadun takeena.
4. **Temporal Standard:** Numerot/Aikaleimat välitetään ISO-8601 UTC ja palautetaan Dart ICU -muuttujin ruutuun.
5. **Translation Hooks:** Varmistaa, että malleja ei pakoteta purkamaan "Pydantic Field Names" suomennuksilla, aiheutusta rikkovat strict-schemat.

---

## The Map: Hakemistoryhmien kuvaus (Frontend Flutter)

Asiakassovelluksen The App Layer (Feature-First Architecture) peilaa ylläolevaa strategiaa Riverpod logiikoissa. Koko sovellus perustuu kansion sisäiseen jaotteluun:

### `client_app_v2/lib/` (The Cognitive Studio)
Asiakassovelluksen GoRouter ja Feature-kärjet sijaitsevat osioituna täällä.
- **`main.dart` & `app.dart`**: Ohjelman käynnistys ja App Shell. Tänne kuuluu The ErrorBoundary kääre (Red Screen of Death poistot).
- **`core/`**: Verkkoyhteys (Network client), `LoggerServiceProvider` (Riverpod loggeri) ja Error Exception Boundaries.
- **`features/`**: Feature-First jaottelu, jossa itsenäinen reitti ja state-layer elää samassa Feature-kansioissa logiikan ytimeen asettuen:
  - `auth/`: IAM Passkey ja Logiikka (Proaktiivinen MFA / Error Handling Zero-Latency asetuslasina).
  - `execution/`: DAG Ajojenseurantanäkymät. Riippuvaisia katsomiskulmasta. (SWR Optimistic state).
  - `bff/`: The Backend-For-Frontend -lukusolmut, jotka dynaamisessa muodossa luovat Widgetit lukemalla API:n antamia Opaque Stripe ID puitteita.
- **`l10n/`**: Lokalisointikansio (`app_en.arb`, `app_fi.arb`). Seuraa kovaa No-String ääriarvoista rajoitusta (UI ei sisällä kovakoodattuja jonoja widgeteissä).
- **`router/`**: Navigoinnin hermoverkko. Reitittimissä vain ID-välitunnuksia URL stression lieventämiseksi (Routing). Sisältää Guardit lennättämään ulos ei-tenant suojauksissa (`org_xyz: MEMBER`). 
- **`shared/`**: Modulaariset Widgetit, Model/Freezed -määritykset asynkroniselle JSON DTO:n pureukselle sekä "SafeCast" virheeneston työkalut.
- **`theme/`**: The Design System Material 3 värimaailmat. Ei tuplattuna Blueprinteihin tai Hookkeihin.
