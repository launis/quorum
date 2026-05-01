# Cognitive Quorum - Client Application (Flutter V2.9)

Tämä on **Cognitive Quorum** -alustan uusi **Desktop-First** käyttöliittymä, joka on erikoistunut raskaaseen kognitiiviseen asiantuntijatyöhön (Thick Client). Se kommunikoi saumattoman asynkronisesti Backendin (`FastAPI`) API-rajapintojen ja taustatyöntekijöiden (`Arq / Redis`) kanssa ohitaen tyypillisen laiteviiveen (Main Thread Jank).

Laajemman ohjelmiston päälinjaukset, arkkitehtuurit ja Backendin teknologisen taustan voit lukea **[Juurihakemiston README:stä](../README.md)**. Yksityiskohtaisempi Frontendin tekninen erittely asuu puolestaan `docs/architecture/06_desktop_first_flutter_client.md` -hakemistossa.

## 🚀 Arkkitehtuurin Ydin (The Client Manifesto)

Flutter-sovellus ei ole vain visuaalinen kerros, vaan tiukka jatke järjestelmän **Fail-Fast** filosofialle:

*   **Zero-Math UI (BFF):** Käyttöliittymälaite (Flutter / CPU) *ei saa koskaan* laskea tekoälyn suorituskykypisteitä, x/y akseleiden matemaattisia keskiarvoja tai vertailla numeerisia värikynnyksiä tekoälyn datasta. Kaikki tämä monimutkaisuus tuodaan valmiiksipureskeltuna `ReportLayoutDTO` "Backend-for-Frontend" datana `BlueprintService`:stä. 
*   **AppErrorBoundary (RFC 7807):** Emme yritä epätoivoisesti piilottaa rikkinäistä arkkitehtuuria (`SizedBox.shrink()` on kielletty validointivirheiden laastaroinnissa). Jos taustajärjestelmä tarjoilee Freezed-mallin ulkopuolista tai puuttuvaa dataa, yksittäinen komponentti (esim tekoälyn solmu) "kaatuu sivistyneesti" punaiseen **Error Card** -laatikkoon. Koko muu graafinen IDE pyörii sulavana ja kehittäjä näkee vianlähteen (`Exception` / `CheckedFromJsonException`) ruudulla ilman mustaa laatikkoa. Opaque Stripe IDs -järjestelmä suojaa reitit linkkimädäntymiseltä.
*   **Riverpod 3.0 & SWR:** Koko ruuduttavat jäätävät latausanimaatiot (Full View Loading Spinners) on korvattu **Stale-While-Revalidate** (SWR) cache-arkkitehtuurilla. Tilamuutoksia nopeutetaan "Optimistic UI" mutaatioilla, jolloin ohjaus toimii sekunneissa viivelatenssin läpi.
*   **The De-Generator Mandate & Snapshot Revert:** Ylläpitopuolen Admin Studio on rakennettu sietämään massiivisia mutaatioita (työnkulkujen ja matriisien muokkaus) dynaamisilla "SafeCast" validointikerroksilla. Jos Pydantic V2 -taustajärjestelmä hylkää mutaation "Fail-Fast" -hengessä, **Snapshot Revert** -protokolla kumoaa välimuistimuutokset lennosta rikkomatta käyttäjäkokemusta.
*   **The Isolate Mandate:** (Main Thread Jank Prevention). Vaikka palvelin lähettäisi 10 MB JSON-raporttia täynnä monimutkaisia lainauksia kymmeniltä LLM-verkon osilta, valtavan datan purku eli Deserialisaatio lukitaan turvaan omalle Dart Isolate -prosessoriytimelleen garantöiden ehyen 60/120Hz sormiliu'un: `await Isolate.run(() => jsonDecode(chunk));`

## 🏗️ Teknologiapino

*   **UI Framework**: Flutter (3.27+) -> Optimoitu Desktop (Win/Mac) / Ultrawide reitityksiin (Three-Pane Layout).
*   **Tilanhallinta**: Riverpod 3.0+ (`@riverpod` koodigeneraatio ehdoton).
*   **Koodisturva**: Freezed (`disallow_unrecognized_keys: true` -> Strict mode Fail-Fast API:lle).
*   **Reititys**: GoRouter (Natiivit `GoRouteData` -luokat; string/path -reitit kielletty tyyppiturvallisuudessa).

## 📂 Hakemistorakenne

*   `lib/core/`: IDE-kuori (työtilat, AppErrorBoundary, navigointikerros) ja Dio / Riverpod verkkoinfrastruktuuri asynkronisilla SWR-tilauksilla.
*   `lib/features/`: Liiketoimintamoduulit ryhmiteltyinä. Pitää sisällään mm. `studio/` (Canvas-pohjainen DAG-editori), ja `execution/` asiantuntijajärjestelmän työnkulkumonitorin.
*   `lib/shared/` & `lib/models/`: Globaalit turvallisesti `@freezed`-generoidut Datamallit jotka synkronoivat 1:1 Backend Pydantic-rajapinnan.
*   `lib/l10n/`: **No-String Mandate!** Järjestelmän I18N lokaalistus hoidetaan täysin `.arb` tiedostojen kautta käyttöliittymän hard-koodauksen estämiseksi ja Enum-käytäntöjen turvin.

## 📦 Kehitysympäristö

Helpoin tapa ajaa koodia (FastAPI + Arq + Flutter) kerralla ja valmiina on käynnistää asiat projektin päätasolta asennettujen riippuvuuksien (Rediksen) kera `run_local.bat` scriptillä:
```bash
cd ..
./run_local.bat
```

Jos editoit Client-applikaatiota itsenäisesti (Backend on jo ylhäällä):
```bash
flutter pub get
# Generoi reitit ja mallit aina uudelleen!
dart run build_runner build -d
flutter run
```

---
*(Clientin oma tekninen arkkitehtuuri asuu kokonaisuudessaan osoitteessa `docs/architecture/06_desktop_first_flutter_client.md`)*
