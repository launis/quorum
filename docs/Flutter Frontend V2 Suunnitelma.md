# **TOTEUTUSSUUNNITELMA: Client App V2 (Dynaaminen SDUI)**

## **VAIHE 0: Infrastruktuurin Pelastus ja Generaattorien Tuho**

**Tavoite:** Alustaa client\_app\_v2 puhtaaksi SDUI-moottorin pohjaksi. Poistetaan V1:n staattinen data- ja API-kerros, mutta pelastetaan teemat, visuaaliset widgetit ja reitityksen perusrunko.

**Säilytettävä ja Kuorittava V1-koodi:**

* pubspec.yaml (Riippuvuudet siivotaan).  
* lib/theme/ ja lib/l10n/ (Värit, typografia, staattiset käännökset).  
* lib/core/ (Lukuun ottamatta vanhoja tyypitettyjä error-malleja).  
* lib/router/ (GoRouter-konfiguraatio tyhjennetään kovakoodatuista työnkulkureiteistä).  
* lib/features/auth/ ja lib/features/shell/ (Kirjautuminen ja navigointipalkit).  
* **Visuaaliset Helmet:** lib/features/orchestration/presentation/widgets/results/, sdui/ ja wizard/ \-kansioiden visuaaliset komponentit. Nämä siirretään uuteen lib/shared/widgets/ \-kansioon. Näistä **poistetaan kaikki viittaukset vanhoihin malleihin** (esim. ReportView, EvaluationResult) ja muutetaan parametrit natiiveiksi (Map, List, double, String).

**Tuhottava V1-koodi (Älä kopioi):**

* Koko packages/backend\_api/ \-hakemisto.  
* Kaikki domain/models/, domain/dtos/ ja data/repositories/ \-hakemistot.  
* Kaikki .freezed.dart ja .g.dart \-tiedostot.

**🤖 Antigravity-prompti 0 (Kopioi IDE:en):**

*"Olemme Vaiheessa 0\. Luo client\_app\_v2 kopioimalla V1:n client\_app-hakemisto, MUTTA tee heti seuraavat radikaalit siivoukset: 1\) Poista pubspec.yaml:sta paketit freezed, freezed\_annotation, json\_serializable, riverpod\_generator ja build\_runner sekä lokaali backend\_api. 2\) Poista koko packages/backend\_api/ \-kansio. 3\) Poista kaikki domain/models/, domain/dtos/ ja data/repositories/ kansiot. 4\) Poista kaikki .freezed.dart ja .g.dart tiedostot. 5\) Etsi V1:stä (features/orchestration/presentation/widgets/) visuaaliset widgetit (kuten score\_card\_radar.dart, logic\_matrix\_chart.dart, deep\_dive\_expander.dart, file\_input\_field.dart) ja siirrä ne uuteen lib/shared/widgets/ \-kansioon. Puhdista nämä widgetit: poista KAIKKI staattisten mallien importit. Niiden parametrien tulee olla vain Dartin perusmuuttujia (double, String, List, Map). Puhdista router siten, että sovellus kääntyy ilman build\_runneria ja avaa kirjautumisen / tyhjän etusivun."*

## ---

**VAIHE 1: Dynaaminen Verkkokerros, I18n ja Riverpod-perusta**

**Tavoite:** Rakentaa tuhotun V1-paketin tilalle kevyt, dynaaminen API-kerros. Valmistella turvallinen datan purkaminen ja SSE-striimaus.

**Tarkat Taskit:**

1. **API Client (api\_client.dart):** Yksinkertainen Dio-client, joka palauttaa Future\<Map\<String, dynamic\>\>. Lisää Dio-interceptor, joka lukee laitteen kielen ja lisää target\_locale \-tiedon (I18n Fallbackia varten).  
2. **SSE Client (sse\_client.dart):** Luokka, joka kuuntelee DAG-ajon (POST /api/v2/executions/run) Server-Sent Events \-striimiä ja tuottaa Stream\<Map\<String, dynamic\>\>.  
3. **SafeCast Util:** Koska luovumme tyyppiturvallisista malleista, tarvitsemme defensiiviset muuntimet. Erityisesti safeDouble on kriittinen, koska LLM voi palauttaa desimaalin "4.5" stringinä, inttinä tai floatina.  
4. **I18n Resolver (i18n\_utils.dart):** Apufunktio, joka purkaa backendin {"default\_locale": "fi", "translations": {...}} \-objektit UI:n kielelle.  
5. **Manuaalinen Riverpod:** Käytä modernia Notifier ja AsyncNotifier \-rajapintaa tilanhallinnan alustukseen ilman annotaatioita.

**🤖 Antigravity-prompti 1:**

*"Olemme Vaiheessa 1\. 1\) Rakenna lib/core/network/api\_client.dart käyttäen Dioa. Metodien tulee palauttaa raakaa Map\<String, dynamic\> \-dataa. Lisää Dio-interceptor, joka lukee sovelluksen kielen ja lähettää 'target\_locale' \-tiedon backendille. 2\) Rakenna sse\_client.dart lukemaan Server-Sent Events (SSE) \-striimiä. 3\) Luo lib/utils/safe\_cast.dart. Tee defensiiviset apufunktiot (erityisesti safeDouble), jotka estävät tyyppikaatumiset dynaamista JSONia luettaessa. 4\) Luo lib/utils/i18n\_resolver.dart I18n Fallback \-logiikan purkamiseen. 5\) Alusta Riverpod-tilanhallinta käyttäen manuaalisia Notifier ja AsyncNotifier \-luokkia ilman koodigenerointia."*

## ---

**VAIHE 2: Responsiivinen SDUI Widget Factory & XAI-Yhdistelmäkomponentit**

**Tavoite:** Tehdä V2:n renderöinnin sydän, joka kääntää backendin ui\_hints\_snapshot \-ohjeet lennosta V1-visuaaleiksi, liittäen niihin automaattisesti teoriaperustelut.

**Tarkat Taskit (lib/features/sdui/widget\_factory.dart):**

1. **Tehdasluokka:** SDUIWidgetFactory.buildWidget({Map hint, String slug, Map results, String locale}).  
2. **Mappaus:** Switch-case hint\['widget'\] \-arvon mukaan (esim. radar\_chart \-\> V1:n ScoreCardRadar). Arvot syötetään SafeCast:n läpi.  
3. **XAI Compound Widget (Teoriamaadoitus):**  
   * Tarkista dynaamisesti, löytyykö results-objektista avaimet ${slug}\_justification ja ${slug}\_citation.  
   * Jos löytyy, kääri V1-arviokomponentti responsiiviseen Column \-rakenteeseen. Piirrä sen alle V1:stä pelastettu deep\_dive\_expander.dart. Näytä tässä laatikossa tekoälyn perustelu ja klikattava lähdeviite (URL).  
4. **Responsiivisuus:** Kaikki komponentit asettuvat joustavasti LayoutBuilder tai Wrap \-elementtien sisään sopeutuakseen kaikille näyttökoille.

**🤖 Antigravity-prompti 2:**

*"Olemme Vaiheessa 2\. Rakenna SDUI Widget Factory (lib/features/sdui/widget\_factory.dart). Tee staattinen metodi buildWidget(hint, slug, results, locale). Mapita hint\['widget'\] (esim. 'radar\_chart', 'slider', 'gauge') Vaiheessa 0 pelastettuihin V1-widgetteihin käyttäen SafeCastia. TÄRKEÄÄ (XAI): Etsi results-mapista avaimia '${slug}\_justification' ja '${slug}\_citation'. Jos ne löytyvät, kääri alkuperäinen widget yhdistelmäkomponenttiin (Compound Widget), joka näyttää widgetin alapuolella V1:stä pelastetun deep\_dive\_expander-laatikon. Laita laatikkoon LLM:n antama lähdeperustelu ja virallinen lähdeviite. Varmista LayoutBuilderilla ja Wrapilla, että kaikki renderöityy täysin responsiivisesti eri laitteilla."*

## ---

**VAIHE 3: Dynaamiset End-User Näkymät (Semanttinen Reititys & Live SSE)**

**Tavoite:** Korvata V1:n kovakoodatut wizard-lomakkeet kahdella universaalilla näkymällä (Start ja Live Results), jotka rakentuvat täysin backendin ohjeista ja mukautuvat ruutukokoon.

**Tarkat Taskit (lib/features/execution/presentation/screens/):**

1. **DynamicStartScreen:**  
   * Hakee API:lta työnkulun expected\_inputs \-taulukon.  
   * Piirtää ListView/Wrap avulla dynaamisesti V1:n file\_input\_field tai tekstikentät iteroiden tätä taulukkoa. Syötteet kerätään semanttisiin rooleihin (Map\<String, dynamic\> inputs) backendille lähetystä varten.  
2. **LiveExecutionScreen (SSE):**  
   * Kuuntelee Riverpodin AsyncNotifierin kautta SSE-virtaa.  
   * **Renderöintiluuppi:** Iteroi *sokeasti* frozen\_context\['ui\_hints\_snapshot'\] \-objektia ja kutsuu Widget Factoryä. (Ei if-lauseita domain-avaimille\!).  
   * **Responsiivinen Layout:** Käytä SliverGrid \-rakennetta. Esimerkiksi puhelimella 1 sarake, tabletilla 2 saraketta, isolla työpöytänäytöllä 3-4 saraketta.  
3. **Version Drift \-varoitus:**  
   * Vertaa frozen\_contextin ID:tä (esim. matrix\_v1) kantaan. Jos matriisi (teoria tai kireys) on päivittynyt ajon jälkeen, näytä ylälaidassa V1:n system\_notification \-tyylinen varoitusbanneri.

**🤖 Antigravity-prompti 3:**

*"Olemme Vaiheessa 3\. Rakenna loppukäyttäjän näkymät lib/features/execution/ \-kansioon. Käytä Riverpodin AsyncNotifieria (ei codegenia). 1\) DynamicStartScreen: Hae työnkulun 'expected\_inputs' ja piirrä V1:n latauswidgeteillä dynaamisen lomakkeen for-silmukalla, keräten syötteet semanttisiin rooleihin. 2\) LiveExecutionScreen: Kuuntele SSE-striimiä. Näkymän TÄYTYY iteroida ainoastaan 'frozen\_context.ui\_hints\_snapshot' \-rakennetta ja piirtää elementit SDUIWidgetFactoryllä. Käytä SliverGridiä: tee layoutista täysin responsiivinen (mobiili 1 kolumni, työpöytä useita). 3\) Lisää Audit Drift \-varoitusbanneri, jos ajon 'frozen\_context' sisältää vanhemman versionimen (\_vX) kuin järjestelmän aktiivinen versio."*

## ---

**VAIHE 4: Admin Studio V2 (Kalibrointi, XAI & DAG)**

**Tavoite:** Uudistaa V1:n Studio tukemaan uutta "Kaikki on Matriiseja" \-arkkitehtuuria, teorian liittämistä, arvioinnin kireyden säätöä ja DAG-reititystä.

**Tarkat Taskit (lib/features/studio/presentation/):**

1. **Dynaaminen I18n-syöttö:** Rakenna komponentti (esim. I18nTextField), johon syötetään default\_locale ja voidaan lisätä käännöksiä kieli-avaimilla. Käytä tätä Sanakirjassa ja Säännöissä. Kaikki tallennus on Append-Only (PUT-kutsu palauttaa uuden versioidun ID:n).  
2. **Universaali Matriisirakentaja (UniversalMatrixBuilder):**  
   * Lomake kriteeririvien lisäykseen.  
   * **Uudet XAI-kentät:** Tietotyyppi (int/string/**float**). Checkboxit "Salli desimaalit" ja "Vaadi lähdeperustelu". Tekstikentät "Teorialähteen URL" ja "Lähdeviite".  
   * **KIREYS-KALIBROINTI:** Lisää liukusäädin 0–100 (strictness\_level), selitteillä 0=Maksimi armollisuus, 100=Maksimi kireys.  
3. **Workflow DAG Builder (Semanttinen reititys):**  
   * Lomake, jolla määritellään expected\_inputs (mitä syötteitä työnkulku vaatii).  
   * Askeleiden (Steps) luontiin uudet monivalinnat:  
     * depends\_on: Mitä muita askeleita tämän pitää odottaa (DAG-graafi).  
     * input\_mappings: Valikot, joista admin reitittää joko Globaalit Syötteet ($inputs.chat\_log) tai aiempien agenttien tulokset ($steps.step\_1.results) askeleen vaatimiin rooleihin.

**🤖 Antigravity-prompti 4:**

*"Olemme Vaiheessa 4, viimeinen vaihe. Rakenna lib/features/studio/ Admin-työkalut responsiivisesti käyttäen Riverpod Notifiereja. 1\) Tee CRUD-lomakkeet (Append-only tallennus). Luo I18nTextField \-komponentti monikielisten tekstien syöttöön. 2\) Rakenna UniversalMatrixBuilder. Kriteeririveille on lisättävä uudet kentät: tyyppi (float/int/string), Checkboxit 'Salli desimaalit' ja 'Vaadi lähdeperustelu', kentät Teorialähteelle (URL+viite), sekä Slider (0-100) arvioinnin kireyden (strictness\_level) asettamiseksi. 3\) Rakenna WorkflowDagBuilder, joka tukee semanttista datareititystä: lomakkeessa määritellään 'expected\_inputs' (roolit) sekä askeleiden 'depends\_on' (monivalinta) ja 'input\_mappings' ($inputs / $steps) DAG-rakennetta varten. Kaikki hallitaan dynaamisilla Mapeilla."*