# Arkkitehtuurisuunnitelma: Flutter MVC DTO Refaktorointi (Phase 9)

**PROJEKTI:** Quorum V2 Client & Admin Studio
**TEEMA:** Siirtymä Server-Driven UI (SDUI) dynaamisuudesta vahvasti tyypitettyyn MVC / DTO arkkitehtuuriin.
**LUKIJALLE (TEKOÄLYAGENTTI):** Tämä dokumentti on suunniteltu ohjeistamaan itsenäistä agenttia Flutter-pään refaktoroinnissa nollakontekstista. Noudata Quorumin tiukkoja `flutterpromptohje.md` arkkitehtuurisääntöjä (Fail-Fast, kielletyt 패턴it, Riverpod-suositukset).

---

## 1. Lähtötilanne ja Tavoite

Quorum V2 -backend on onnistuneesti refaktoroitu poistamaan monimutkainen Server-Driven UI (SDUI) -kerros. Backend ei enää renderöi eikä palauta `render_blueprints` JSON-puita dynaamisine komponenttityyppeineen. Sen sijaan backend toimii nyt puhtaana ohjaimena (Controller) ja palauttaa aina yhden yksiselitteisen ja kiinteän mallin: **ReportDataDTO**.

**Flutter-pään ensisijainen tavoite:**
1. Poistaa tuhansia rivejä vanhaa SDUI `WidgetFactory` / dynaamista renderöintikoodia.
2. Siirtyä tyhmempään Presenter-kerrokseen, joka lukee puhdasta `ReportDataDTO` dataa ja luo siitä ennalta kovakoodatun näkymän (esim. 1D lista, 2D vertailu tai 3D matriisi).
3. Yksinkertaistaa Admin Studio täysin: visuaalisesta layout-editorista luovutaan, tilalle tulee globaali Dropdown-valikko (`preset_view` asetus).

### Target DTO (Backendiltä tuleva uusi JSON)
```json
{
  "workflow_id": "string",
  "preset_view": "1d_metrics", 
  "axes": [
    {
      "name": "Loogisuus",
      "score": 88.0,
      "justification": "Analyysi perustelu..."
    }
  ],
  "synthesis": "Kokonaisarvio..."
}
```

---

## 2. Refaktoroinnin Vaiheet (Milestones)

Lähde purkamaan refaktorointia puhtaalla pöydällä, noudattaen "Fail-Fast" periaatetta. Älä jätä vanhaa koodia pyörimään. Käsittele yksi vaihe kerrallaan.

### Milestone 1: Datamallien Standardisointi (Domain)
* **Tiedostot:** `lib/features/execution/domain/models/...`
* **Tehtävä:**
  1. Poista täysin vanhat `BlueprintComponentBase`, `RenderBlueprint`, ja niihin liittyvät luokat.
  2. Luo uudet tiukasti tyypitetyt luokat `ReportAxisDTO` ja `ReportDataDTO`. Muista Flutter-ohjeen Banned Patterns: *Älä generoi automaattisia Pydantic/Freezed-malleja API-rajapintaan, jos sääntö kieltää sen, salli vain manuaalinen ja defensiivinen fromJson-parsinta "SafeCast"-tyylillä*.
* **QA / Testaus:** 
  - Kirjoita yksikkötesti (`test_report_dto_parsing.dart`), joka syöttää yllä olevan mock-JSONin mallille, ja toistaa Fail-Fast -räjähdyksen (heittää Exceptionin) jos `axes` puuttuu.

### Milestone 2: API ja Repository-tason Siivous (Data)
* **Tiedostot:** `lib/features/execution/data/repositories/...`
* **Tehtävä:**
  1. Refaktoroi `/render` -päätepistettä kutsuvat metodit. Paluuarvo ei ole enää dynaaminen komponenttipuu, vaan puhdas `ReportDataDTO`.
  2. Varmista, että Dio/Http-kutsut on kääritty vakiintuneeseen `AppException`-virheenkäsittelyyn.
* **QA / Testaus:**
  - Aja Riverpod/Repository-testit simuloimalla 200 OK vastaus DTO:n perusrakenteella ja 400 Bad Request vastaus virhetilanteessa.

### Milestone 3: Client App Käyttöliittymän Uusinta (Presentation)
* **Tiedostot:** `lib/features/execution/presentation/widgets/blueprint_renderer.dart` jne.
* **Tehtävä:**
  1. Poista koko `WidgetFactory` ja dynaamiseen rekursioon perustuva piirtologiikka.
  2. Luo `ReportRendererWidget`. Widget tutkii DTO:n `preset_view` kentän arvon (esim. ohjaus switch-casella uusiin staattisiin widgetteihin `Metrics1DView`, `Compare2DView`, `Complex3DView`).
  3. Kukin View vastaa itse UI:sta `axes`-listan iteroinnin kautta. Data ja logiikka ovat irrallaan muodosta.
* **QA / Testaus:**
  - Widget-testi: Lataa `ReportRendererWidget` syöttämällä sille yksi "Score 100" akseli, ja tarkista `expect(find.text('100'), findsOneWidget)`. Listan renderöinnissä ei saa olla minkäänlaista "kokeillaan piirtää tämä komponentti"-purkkaa.

### Milestone 4: Admin Studion Yksinkertaistaminen (Admin / Studio)
* **Tiedostot:** `lib/features/admin/presentation/...` tai missä ikinä Työnkulun luominen (Workflow editor) sijaitsee.
* **Tehtävä:**
  1. SDUI:n myötä monimutkaiselle graafiselle näkymän rakentajalle ei ole enää tarvetta. Poista se.
  2. Työnkulun luontinäytölle (Workflow Config) lisätään yksinkertainen kenttä: **Tulosteen Visuaalinen Teema (`output_mapping.preset_view`)**.
  3. Vaihtoehdot ladataan alasvetovalikkoon: "1D Metrics", "2D Compare", "3D Complex".
  4. Varmista, että Admin Studion tallennus lähettää Backendille Pydanticin V2-yhteensopivan rakenteen `{"output_mapping": {"preset_view": "X"}}`.
* **QA / Testaus:**
  - Tarkista Riverpod Notifierin tila Admin Studiossa ennen tallennusta: varmista, että JSON-rakenne on täsmälleen haluttu uusi standardi poissiivotuin vanhoin kilkkein.

### Milestone 5: Fail-Fast Doctrinen Tarkastus (System)
* **Tiedostot:** Globaali virheenkäsittely.
* **Tehtävä:**
  1. Poista koodikannasta kaikki sellaiset `try-catch` tai `if (component == null) return const SizedBox();` rakenteet, jotka on luotu SDUI:n dynaamisuuden takia.
  2. Jos DTO on rikki, tai preset_view tuntematon, UI:n kuuluu heittää The Red Error Screen, eli siirtää vika asiallisesti `AppErrorBoundary`:n näytettäväksi. Ohita tyhjien ruutujen silent failyre -haamut.
* **QA / Testaus:**
  - Tee E2E tai integraatiotesti syöttämällä viallinen Data Transfer Object. Validoi, että UI herjaa korruptoituneesta datasta välittömästi ilman hiljaista nielaisua.

---

## Ennen aloittamista (Agentille)
Lue nämä dokumentit ennen yhdenkään koodirivin luomista:
1. `docs\flutterpromptohje.md` - Erityisesti kielletyt patternit, Fail-Fast säännöt, ja lokituksen vaatimukset.
2. `docs\Arkkitehtuurimäärittely_ AI-orkestraattori V2.md` - Saat kuvan siitä miten Event-Sourcing ja V2 Core toimivat isossa kuvassa.

*"Se on nyt niin, että DTO tekee työt, ja ruudulle piirto on niin tyhmiä kuin mahdollista."*
