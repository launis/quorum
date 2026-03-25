# Epic 7: Workflow Studio V3 Redesign (Admin App)

**RIIPPUVUUS:** Tämä Epic käynnistetään vasta **[EPIC_v3_flutter_frontend_adaptation.md]** -suorituksen jälkeen. Ennen tätä Epiciä Flutter-arkkitehtuurin perusta (Riverpod 3.0 Mutaatiot, Isolate-parsinta, SSE State ja `AppException` tason Actionable Hint -virheenhallinta) on oltava valmiina tuotantokäyttöön.

## 📌 Context
Käyttäjäpalaute osoitti, että nykyinen "Työnkulun Asetukset" (Workflow Settings) -näkymä on sekava. Se suoltaa kaiken informaation yhdelle sivulle ja sallii heikosta typologiasta johtuvia rikkoutumia (vapaatekstisyötteitä ja suttuisia hook-valikoita).

Tässä Epicissä Admin Studion työnkulunrakentaja rakennetaan täysin uusiksi tiukkojen `AdminStudio_V2_UI_Architecture.md` The Flat MVC ja Omni-Navigation -sääntöjen mukaiseksi. Keskiössä on loogisuus, V3-moottorin työkalutuet (MCP) ja tekoälyn turvallisuusrajoitteet (Safety).

**Arkkitehtuurin turvaaminen:** Studion on tuettava The Stripe Pattern -kryptografiaa (`wf_...`, `steprule_...`). Käyttöliittymän ainoa tehtävä on esittää nämä monimutkaiset viittaukset ihmisluettavina "Nomenclature" -käännöksinä litteiden Cascading Dropdowns -valikkojen kautta. Frontend ei koskaan generoi omia ID-tunnisteita, eikä tee mutaatioita ilman Pydantic V2 Fail-Fast -validointia.

## 🎯 Päävalikon Rakenne (Sivupalkki / Master Navigation)
Studio jaetaan viiteen selkeään pääkategoriaan, joilla jokaisella on oma listanäkymänsä (Master) ja muokkausnäkymänsä (Detail):

1. **Työnkulut (Workflows)**
2. **Työvaiheet (Steps)**
3. **Kognitio (Prompt Blocks & BARS)**
4. **Esityskerros (Layouts)**
5. **Järjestelmä (System Config)**

---

## 🏗️ Moduulien CRUD-prosessit ja Näkymät

*Yleinen sääntö päätauluille: Kaikille viidelle pääkategorialle CRUD-osuuksiin on toteutettava "Deep Copy" (kloonaus) -ominaisuus The Cascading Clone -arkkitehtuurin mukaisesti, ja tämä toteutetaan ehdottomasti vain Backend-API:na (UI vain esittää napin).*

### 1. Järjestelmä (System Config)
Tämä näkymä jaetaan kahteen selkeään välilehteen tai alivalikkoon, mikä erottaa LLM-mallit työkalujen reitityksestä:

- **SaaS / Tenant Eristys:** Järjestelmä erottaa globaalit (System) mallit ja paikalliset (Tenant) instanssit. Globaaleja objekteja ei voi muokata suoraan, vaan UI tarjoaa "Cascading Clone" -ominaisuuden, joka tekee syväkopion säännöistä asiakkaan omaan Tenant-kantaan (AI Act jäljitettävyyden takaamiseksi).
- **Model Registry (CRUD & Deep Copy):**
  - **Master:** Lista saatavilla olevista tekoälymalleista ja niiden rooleista (esim. `fast`, `deep`, `strict`).
  - **Detail:** Määritellään mallin fyysinen API-reitti (esim. `vertex_ai/gemini-2.5-pro`), token-rajat (`max_tokens`), lämpötila (`temperature`) ja älykkäät kuormanhallinnan rajat (`tpm_limit`, `rpm_limit`).
- **MCP Gateways (CRUD & Deep Copy):**
  - **Master:** Lista ulkoisista työkaluista ja agenteista (Model Context Protocol).
  - **Detail:** Konfiguroidaan reitit ulkoisiin SaaS-palveluihin (esim. Tavily Search) tai omiin sisäisiin Cloud Run -mikropalveluihin, joita tekoäly voi kutsua.

### 2. Kognitio (Prompt Blocks & BARS)
Koska asennepromptit ja arviointimatriisit ovat täysin erilaisia petoja, ne erotetaan käyttöliittymässä toisistaan, vaikka ne tallentuisivatkin samaan tietokantakokoelmaan.

- **The 5-Layer Language Strategy (I18n):** Kielipuskuri (UI): Otsikot, kuvaukset ja lokaalit käännökset syötetään uudella `i18n_text_field` -komponentilla (esim. tabit FI/EN).
- **English-Only Mandate:** Tekoälyn järjestelmäohjeet (system instructions) on rajoitettu käyttöliittymässä tiukasti vain englanninkielisiksi laadun maksimoimiseksi. Käyttöliittymän tulee pakottaa tämä visuaalisella varoituksella (esim. "AI Reasoning Mandate: System prompts must be in English").
- **Prompt Blocks (Ohjeistukset & Deep Copy):**
  - Tavallisten teksti- ja Markdown-pohjaisten systeemiohjeiden CRUD.
- **BARS-matriisit (Behaviorally Anchored Rating Scales & Deep Copy):**
  - UI suodattaa näkyviin vain ne, joissa `category_id: "matrix"`.
  - **Detail-näkymä:** Oma erikoistunut matriisieditori, jossa hallitaan arviointikriteerejä, numeerisia asteikkoja (esim. 1-5 tai 0-100) ja niihin sidottuja käyttäytymiskuvauksia.

### 3. Työvaiheet (Steps)
Tämä on työnkulkujen moottorin ydin. Askel on uudelleenkäytettävä palikka.

- **Master:** Lista kaikista saatavilla olevista työvaiheista (Task Blueprints). (Sisältää Deep Copy).
- **Detail (Muokkausnäkymä):**
  - **Hook-hallinta:** `pre_hooks` ja `post_hooks` esitetään monivalintapudotusvalikkoina (Multi-select dropdown). Nämä molemmat lukevat arvonsa samalta, backendin tarjoamalta dynaamiselta Enum-listalta (esim. `json_parser_hook`, `normalize_matrix_scores`). Koska näitä on yleensä vähemmän, valintaruudut tai "chips"-tyylinen käyttöliittymä on paras.
  - **Prompt Blocks -lista:** Järjestettävä lista (Drag & Drop -käyttöliittymä). Käyttäjä voi lisätä blokkeja kohdassa 2 luodusta listasta, poistaa niitä ja muuttaa niiden järjestystä vetämällä. Järjestys määrittää lopullisen kontekstin prioriteetin tekoälylle.

### 4. Esityskerros (Layouts)
Abstrakti `output_profiles` siirretään taka-alalle, ja käyttöliittymä keskittyy suoraan konkreettisiin asetteluihin (Layouts).

- **Master:** Lista saatavilla olevista asetteluista (esim. "Standardi auditointiraportti", "Tiivistelmäverkko"). (Sisältää Deep Copy).
- **Detail:** Visuaalinen tai rakenteellinen editori, johon lisätään suoraan arvoja (esim. näytetäänkö XAI-todistusaineistolaatikko, käytetäänkö DataGridiä vai 2D-matriisia). Koko renderöintisäännöstö (Flat DTO) konfiguroidaan täällä ilman välillisiä profiilikerroksia.

### 5. Työnkulut (Workflows)
Tämä on kokonaisuuden sitova, raskain näkymä.

- **Master:** Työnkulkujen (Workflows) päälista. (Sisältää Deep Copy).
- **Detail (DAG Builder):**
  - Sisältää useita erilaisia listoja.
  - **StepRules-lista:** Käyttäjä valitsee aiemmin luotuja "Steppejä" ja sitoo ne osaksi tätä työnkulkua. Tässä vaiheessa Stepeille voidaan antaa lokaaleja, työnkulkukohtaisia ylikirjoituksia tai datareitityksiä (`$inputs` ja aiemmat `$steps.x`).
  - **Syötteet (Expected Inputs):** Lista muuttujista, joita työnkulku vaatii käynnistyäkseen (määrittää dynaamiset lomakkeet loppukäyttäjälle).
  - **Riippuvuusverkko (DAG):** Käyttöliittymän on osattava hyödyntää litteitä pudotusvalikkoja (Cascading Dropdowns), jotta askeleet voidaan ketjuttaa turvallisesti toisiinsa ilman kirjoitusvirheitä.
  - **Reaaliaikainen riippuvuusvaroitus:** Jos askeleen nimi muuttuu tai se poistetaan, DAG-rakentajan `blueprint_editor_controller` invalidoidaan. Käyttöliittymä reagoi välittömästi muuttamalla kaikki orvoiksi jääneet viittaukset virhetilaan (Actionable Hint: "Tämä askel viittaa poistettuun lähteeseen").
  - **The Anti-Mirror Kytkennät:** Jos DAG-verkkoon kytketään LLM-as-a-Judge -solmuja (toinen AI arvioi toisen AI:n tuotosta `$steps` -viittauksella), käyttöliittymä merkitsee solmut selkeästi visuaalisella indikaattorilla (esim. kilpi tai varoitusväri) ja "Debate/Adversarial" -tagilla muistuttamaan Anti-Mirror protokollan poikkeuksesta.
  - **Dry-Run Visuaalinen Simulaattori (Testiajopainike):** Työnkulkueditoriin lisätään "Simulate / Dry Run" -painike. Ennen kuin työnkulku merkitään `status: active` -tilaan, admin voi painaa nappia, joka puskee kääntäjälle tyhjän syötteen ja varmistaa visuaalisesti vihreillä/punaisilla reunoilla, meneekö Kahnin algoritmin reititys läpi.

---

## 🛠️ Tekniset huomiot (Flutter / Riverpod 2026 Standardit & Desktop-Class UI)

Admin Studio on asiantuntijoiden Pro-työkalu (IDE). Jotta tämä päivitys vastaa Quorumin V3/2026-arkkitehtuurin "The Zero-Compromise Pledge" -laatustandardeja sekä Flutterin adaptiivisuusohjeita (laajentaen tuen massiivisille PC-näytöille ja moniajo-ikkunoihin), seuraavat säännöt ovat ehdottomia:

### 1. Maksimoitu Adaptiivinen Layout & Omni-Navigation (PC Breakpoints)
Käyttöliittymä on suunniteltava työpöytä (Desktop) edellä, josta se skaalautuu hallitusti alaspäin. Näyttötila jaetaan kolmeen tiukkaan murtumispisteeseen (Breakpoint):
* **PC / Ultrawide (>1200dp):** Käytetään **Three-Pane Layout (Kolmisarake)** -asettelua. Vasemmalla on kaventuva `NavigationRail`, keskellä tiivis Master-lista (SWR-välimuistilla), ja oikealla massiivinen työtila (Detail Editor / Canvas). Sarakkeiden välillä käytetään hiirellä säädettäviä jakajia (Resizable Splitters), jotta PC-käyttäjä voi muokata näkymää.
* **Tabletti / Kannettava (600dp - 1199dp):** Käytetään **TwoPane (Split-Screen)** -asettelua. Lista ja Editori ovat rinnakkain.
* **Mobiili (<600dp):** Navigaatio romahtaa alalaidan `NavigationBar`-komponentiksi ja asettelu muuttuu koko ruudun peittäväksi pino-navigaatioksi (Stack Navigation, Push/Pop).

### 2. Työnkulkujen 2D-Kangas ja Inspector (DAG Builder)
Isolla PC-näytöllä työnkulkujen (Workflows) rakentaminen irtautuu staattisista pystylistoista.
* **Infinite Canvas:** Keskelle aukeaa laaja, hiiren rullalla zoomattava ja keskipainikkeella panoroitava 2D-kangas (Flutter `InteractiveViewer`), johon Step-solmuja (Blueprintejä) tuodaan. Riippuvuudet (DAG) vedetään hiirellä visuaalisesti solmujen välille. Kankaan alakulmassa on Minimap.
* **The Inspector:** Kun kankaalta klikataan solmua (esim. AI Agentti), sen dynaamiset Pydantic-asetukset, "Cascading Dropdowns" -valikot ja lokaalit hookit aukeavat oikean reunan kiinteään sivupaneeliin (Inspector Pane) peittämättä itse graafia.

### 3. Desktop-Class Syöttötavat & Datan Tiheys (Power-User Modalities)
PC-hiirikäytössä mobiilisovellusten valtavat marginaalit ja tyhjät tilat ovat kiellettyjä.
* **Visual Density:** Yli 600dp näytöillä Flutterin teema pakotetaan `VisualDensity.compact` -tilaan, mikä maksimoi kerralla näkyvän informaation määrän (esim. BARS-matriisien tiheät DataGrid-taulukot).
* **Näppäimistö & Hiiri:** Järjestelmän on tuettava hiiren oikean napin kontekstivalikkoja (Context Menus: "Kopioi Omaksi", "Poista"), Hover-tiloja nopeaan XAI-rajoitteiden lukemiseen, sekä täyttä näppäimistönavigaatiota (`Ctrl+S` tallennus, `Delete` solmun poistaminen, `Shift+Click` monivalinnat).
* **Fallback:** Kosketusnäyttöjä ja esteettömyyttä varten kaikille Drag & Drop -toiminnoille on oltava aina "Ylös/Alas" -varapainikkeet ja litteät valikot kosketusnäyttöjen virhepainallusten (Fat Finger) estämiseksi.

### 4. The UI Mutations Mandate & Optimistinen UI
Kaikki sivuvaikutukset (Deep Copy, tallennukset, askeleiden poistot ja kytkökset) on pakotettu Riverpod 3.0:n kokeellisen `Mutation<void>` tai `Mutation<DTO>` -API:n taakse. Manuaaliset `_isLoading` -liput ja koko ruudun peittävät latausspinnerit ovat IDE-työkalussa ankarasti kiellettyjä. PC-käytön illuusio nollaviiveestä säilytetään **Optimistisilla päivityksillä** (Optimistic UI) – solmujen kytkökset ja tallennukset päivittyvät UI:hin heti, ja peruutus (Rollback) tapahtuu vain backendin antaessa Pydantic Fail-Fast -virheen.

### 5. Main Thread Jank -suojaus (Isolate-parsinta)
Koska raskaat PC-näkymät lataavat valtavia määriä dataa kerralla (esim. satojen solmujen DAG-puu ja matriisien Pydantic DTO -rakenteet välimuistiin), niiden deserialisointi Freezed-Dart-olioiksi on siirrettävä ehdottomasti **`Isolate.run()`** -taustasäikeeseen. Päälanka hoitaa vain 120fps/144fps piirtämisen huippunäytöillä, taaten ettei hiiren kursori tai kankaan zoomaus nyi koskaan.

### 6. Zero-Math UI & Dry-Run Simulaattori
Frontend ei laske KAHN-algoritmia lokaalisti edes tehokkaalla PC:llä. "Simulate / Dry Run" -painike (tai `F5` pikanäppäin) lähettää DAG-luonnoksen mutaationa BFF-rajapinnalle (`POST /api/v2/studio/workflows/simulate`). Backend suorittaa Pre-Flight -validoinnin, ja Flutter vain värittää palautetun litteän "UI Hint" -paketin ohjeistamana kankaalla olevat rikkinäiset solmut (esim. punaisella hehkulla ja Tooltip-varoitusviestillä).

### 7. Tyyppiturvallinen Reititys ja Deep Linking (Selain/Moniajo)
Raa'at merkkijono-URL:t (`context.push('/workflows/wf_xyz')`) ovat kiellettyjä. Kaikki reititys rakennetaan vahvasti tyypitetyillä `GoRouteData`-luokilla, missä **Hybrid URL Pattern** (Opaque ID + Slug) on täysin pakotettu (esim. `path: 'workflow/edit/:id/:slug'`). PC-käyttäjät avaavat usein työnkulkuja selaimen eri välilehtiin (Tabs) tai työpöydän moni-ikkuna-ajoon (Multi-window); tyypitetty Hybrid-reititys poimii URL:sta AINA vain absoluuttisen ID:n datakanta-vetoa varten, hyläten Slugin. Tämä takaa, että **syvälinkit (Deep Linking)** toimivat täydellisesti ja URL-osoitteita voidaan jakaa sellaisenaan muiden ylläpitäjien kesken täysin immuunina nimenmuutosten aiheuttamalle linkkien hajoamiselle (Link Rot).

### 8. Graceful Degradation & Global Error Handling (Epic 8 Integraatio)
**Riippuvuus Epic 8:aan:** Kaikki Workflow Studion mutaatiot, tallennukset ja simulaattorin verkkopyynnöt on alistettava **[EPIC_8_flutter_global_error_handling_v3.md]** määrittämään virheputkeen.
* **Dual-Reporting:** Kun DAG-simulaattori tai tallennus epäonnistuu, virhe ei jää vain UI-tilaan, vaan se kirjataan välittömästi `LoggerService.error()` -kutsulla paikalliseen `client_debug.log` -tiedostoon ja lähetetään taustalla Logfire-telemetriaan.
* **Tyyppiturvallinen RFC 7807:** Backendin palauttamat validointivirheet (esim. `DAG_CYCLE_DETECTED` Kahnin algoritmin törmätessä) otetaan kiinni `ErrorInterceptor`:ssa ja puretaan vahvasti tyypitetyn `AppExceptionX` -laajennuksen kautta `.arb` -kielitiedostoista Actionable Hinteiksi.
* **Non-Blocking UI (PC Toast):** Virheet reititetään `GlobalErrorView V3` -komponenttiin. PC-näkymässä tämä esitetään tyylikkäänä leijuvana Toast- tai Snackbar-komponenttina työtilan alakulmassa virheen kera, eikä se koskaan saa varastaa koko ruudun fokusta blokkaavana modaalina.
* **Solmutason Viansieto:** Jos kankaan (Canvas) yksittäinen solmu tai viittaus korruptoituu ohjelmallisen muistin varassa, koko PC-työtila ei saa kaatua ("Red Screen of Death"). Riski eristetään `SafeCast` ja `SizedBox.shrink()` -komponenteilla (Graceful Degradation), jättäen muun DAG-verkon toimiin.