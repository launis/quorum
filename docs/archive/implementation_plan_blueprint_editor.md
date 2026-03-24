# Epic: Admin GUI Drag-and-Drop Editor (V6.0 Render Blueprint Builder)

Tämä dokumentti on "The Goal & Steps" -toimeenpanosuunnitelma **Cognitive Studion (client_app_v2)** uuden Blueprinting-editorin rakentamiselle. Tämä vaihe sulkee arkkitehtuurikehän ja mahdollistaa todellisen *Zero-Deploy UI* -hallinnan.

## 0. Tavoite (System Objective)
Tavoitteena on luoda Quorumin ylläpitäjille visuaalinen "Drag-and-Drop" -editori uuteen Admin Studioon (client_app_v2). Editorilla rakennetaan dynaamisia renderöintiohjeita (Blueprintejä) tietylle työnkulun (Workflow) variaatiolle ilman ohjelmointiosaamista.

Editorin ainoa kova tekninen tavoite on tuottaa visuaalisesta asettelusta 100-prosenttisesti asetteluohje, joka menee läpi Backendin `v2_core.py` tiedoston `RenderBlueprint` Pydantic-validoinnista. Tämä takaa sen, että mitä tahansa editorilla luodaan, se piirtyy täydellisesti Flutter-mobiilissa ja PDF-tulosteessa olemassa olevan arkkitehtuurin (BlueprintTransformer) läpi.

---

## 1. Tausta ja Arkkitehtuurin Vaatimukset

Suunnitelma pohjautuu V6.0 Output Generation Pipelinesta tuttuihin ohjenuoriin (`docs\output_generation_pipeline.md` ja `docs\implementation_plan_output_generation.md`):

1. **Ei Teemoitusta (Styling Independence):** Editorissa EI valita värejä, fontteja tai marginaaleja. Se on puhtaasti **sisällön asettelueditori** (Mikä graafi, mikä data ja mikä sääntö).
2. **Kieliagnostisuus (Translation Doctrine):** Editorissa kytketään vain kieliavaimia tai tietokannan käännösnodejen viitteitä (esim. `matriisi_4_tila_2`), itse tekstiä ei koskaan kovakoodata.
3. **Graceful Fail-Fast:** Valmiin Blueprint JSON:n on oltava teknisesti validi laajoine datareitityksineen (esim. polku `$steps.analyst.score`).

---

## 2. Toteutuksen Vaiheet (Implementation Milestones)

Tämä toteutus tehdään vaiheittain Flutter-sovellukseen (`client_app_v2`), painottaen Riverpod -tilan hallintaa modulaarisesti rakentuvien asettelu-objektien ympärille.

### Milestone 1: Blueprint Builder Context & State Management
Rakennetaan editorin "aivot" Flutterin puolelle, joka pitelee muistissa kasattavaa Blueprint -JSONia livenä.
1. **Model:** Määritä Flutteriin tarkat Dart-mallit, jotka peilaavat `RenderBlueprint` ja sen kaikkia komponentteja (`1d_gauge`, `2d_matrix`, jne.).
2. **State (Riverpod):** Luo `BlueprintEditorNotifier`, jolla voidaan lisätä (`addComponent`), poistaa (`removeComponent`) ja muuttaa järjestystä (`reorderComponents`).
3. **Data Routing Service:** Rakenna editorille valitsin, joka lukee The Model Registryn/Workflow'n solmut (DAG) antaen käyttäjän poimia suoraan polkuja dropdown-valikosta (esim. poimi `$steps.logician.hypothesis_1` datapoluksi matriisiin).

### Milestone 2: Drag-and-Drop UI (The Canvas)
Toteutetaan reaktiivinen visuaalinen piirtoalue (Canvas).
1. Luo `client_app_v2/lib/features/studio/views/blueprint_editor_screen.dart`.
2. Ota käyttöön Flutterin natiivi `ReorderableListView` (tai edistyneempi Drag-and-Drop Reorderable paketti) Canvas-alueelle.
3. Rakenna sivupalkki (Component Palette), josta käyttäjä voi raahata tyhjiä komponentteja (Komponenttityypit: Otsikko, 1D-mittari, 2D-matriisi, jne.) Canvakselle.

### Milestone 3: Component Settings Panels
Jokaiselle raahatulle komponentille tarvitaan oma asetusnäkymä, jolla sen ominaisuudet konfiguroidaan täyttämään Pydantic-vaatimukset.
1. Laajenna Canvas-elementit klikattaviksi, jolloin sivupaneeli (tai dialogi) aukeaa.
2. Rakenna spesifiset asetuslomakkeet (Settings Pages) kullekin tyypille:
   - **Header/Footer:** Tekstiavaimien syöttö.
   - **1D Gauge:** `data_path` valinta ja min/max asetukset.
   - **2D/3D Matrix:** X, Y (ja Z) akselien datareititykset, sekä optionaaliset "Evaluation Notes" -polkujen kytkennät.
3. Kaikki tallennukset päivittävät heti Riverpodin `BlueprintEditorNotifier` tilaa reaaliajassa.

### Milestone 4: Serialization, Pydantic Testing & Save
Tehdään varmistus ja tallennus tietokantaan.
1. **JSON Serialization:** Lisää Dartin `toJson()` logiikka, joka kääntää muistissa olevan Drag-and-Drop tilan tasan V6 Blueprint -määritysten mukaiseksi abstraktiksi JSON:iksi.
2. **Local Validation:** Rakenna kevyt esivalidointi tyhjiä pintoja (missing paths) vastaan ennen lähettämistä.
3. **Save to Network API:** Päivitä `studio`-ruuterit (`EXECUTION` tallennus backendissä) säästämään tämä JSON työnkulkuun / seed dataan.
4. Kun tallennettu, käytä olemassa olevaa Python `RenderBlueprint.model_validate` moottoria varmistamaan, että tuotos kelpasi palvelimelle.

### Milestone 5: The "Live Render Preview" (Optional but Recommended)
Koska olemme jo tehneet upean V6.0 SDUI rendering enginen (`client_app_v2/lib/features/reports/presentation/sdui/widget_factory.dart`), hyödynnämme sitä tässä!
1. Rakenna Editorin Canvaksen viereen "Live Preview" -painike.
2. Tähän painettaessa editori syöttää muistissa leijuvan keskeneräisen JSON-Blueprintin suoraan olemassa olevaan `WidgetFactory` tulostajaan varustettuna keksityllä "Dummy Data" -$results tiedolla.
3. Ylläpitäjä näkee *suoraan täydellisen pikseliresoluution livenäkymän* olemassa olevasta raportin osasta ennen julkaisua ilman, että Backendia koodattiin riviäkään.

---

## 3. Käyttöoikeudet / Luvat
Editori on keskitason yläpuolinen ylläpitäjän/kehittäjän (Studio Configurator) työkalu. Se tulee elämään tiukasti suojatussa `studio/` reititinavaruudessa, ei loppukäyttäjien käyttöliittymissä.

### User Review
> Hyväksytkö yllä olevat viisi virstanpylvästä askeleiksi tämän Blueprint Editorin toteutukselle Flutteriin? Kuvastaako The Canvas ja The Settings Panel-rakenne odotuksiasi vaivattomasta ylläpitoliittymästä?
