# **ADMIN STUDIO V2/V3 UI ARCHITECTURE & OMNI-NAVIGATION**

**Google Antigravity / Quorum Project**
**Status:** Valmis tuotantoon (2026 Mandaatti)

Tämä dokumentti on yksinoikeutettu arkkitehtuurikuvaus Quorum Admin Studion (V2/V3) käyttöliittymärakenteesta. Koska Quorum on ammattilaisille suunnattu tehokäyttäjän kehitysympäristö (IDE / Pro-Tool), sen navigaatio poikkeaa täysin perinteisen kuluttajamobiilisovelluksen kaavoista.

---

## 1. 🖥️ The Desktop-First Breakpoints (Omni-Navigation)

Käyttöliittymä on välttämätöntä suunnitella "Työpöytä Edellä" (Desktop-First). Tieto esitetään tiheänä, hiiriohjatusti ja reaaliaikaisena. 

Näyttö asettuu automaattisesti kolmeen tiukkaan Omni-Navigation-porrasteeseen (Breakpoint):

1. **PC / Ultrawide (>1200dp): The Three-Pane Layout**
   * **Pane 1 (Left):** Kaventuva `NavigationRail` pääkategorioille (esim. Workflows, Steps). Ei koskaan koko ruutua peittävä Drawer.
   * **Pane 2 (Middle):** Tiivis SWR-välimuistilla toimiva Master-lista valitun kategorian elementeistä (lukunäkymä).
   * **Pane 3 (Right):** Massiivinen työtila (Workspace / Editor / Canvas), johon listalta klikatut objektit avautuvat (Detail View).
   * **UX:** Sarakkeiden välillä käytetään hiirellä säädettäviä jakajia (Resizable Splitters). Modaalit (Pop-up dialogit) ovat kiellettyjä raskaiden editointien osalta; käytä aina Pane 3:a.
2. **Tabletti / Kannettava (600dp - 1199dp): Split-Screen**
   * **Pane 1 (Left):** Master-lista (joka voi väliaikaisesti liittää NavigationRail-ikonit listaansa säästääkseen tilaa).
   * **Pane 2 (Right):** Editori (Detail View).
3. **Mobiili (<600dp): Stack Navigation**
   * Navigaatio romahtaa laitteen täysin klassiseen alasivupinoon (`NavigationBar` pohjalla, josta aukeaa pinottavia Stack Push/Pop -sivuja koko ruudulle). Master-listaa ja Editoria ei koskaan yritetä sovittaa mobiilissa rinnakkain.

---

## 2. 🗄️ The Master-Detail V2 Hierarchy (SWR)

Studio jakaa tietokantansa ja navigaationsa globaalisti viiteen pääkategoriaan. Käyttäjä ei navigoi sekalaisten asetusvalikoiden kautta, vaan jokainen kategoria on suora lista kohteita "Master-Detail" -paradigman mukaisesti:

1. **Työnkulut (Workflows)**
2. **Työvaiheet (Steps)**
3. **Kognitio (Prompt Blocks & BARS)**
4. **Esityskerros (Layouts)**
5. **Järjestelmä (System Config: Model Registry & MCP Gateways)**

**Riverpod 3.0 SWR-mandaatti:** Koko Master-listojen navigaation arkkitehtoninen kulmakivi on Stale-While-Revalidate (SWR) yhdistettynä Riverpodin `ref.keepAlive()` komentoihin. Kun PC-käyttäjä vaihtaa Pane 3 työtilasta uuteen sub-näkymään ja palaa takaisin Master-listalle, listan latauksessa on ehdottoman pakollista olla **0-viive**. Lista päivittyy vain taustalla hiljaisesti, hyläten "Odotan vastausta - Spinneri" UI-suunnittelun kokonaan.

---

## 3. 🕸️ The Infinite Canvas & Inspector (DAG Builder)

Aikaisemmissa V1/V2 -malleissa monimutkaisia työnkulkuja piirrettiin pudotusvalikoilla. Tämä on ohjelmallisesti hylätty yli 600dp laitteilla.

* **2D Kangas (InteractiveViewer):** Työnkulku (Workflow) on ohjattu verkko (DAG = Directed Acyclic Graph). Rakennus suoritetaan laajaan, zoomattavaan kangastilaan (Infinite Canvas). Käyttäjä vetää ja pudottaa askelsolmuja listastaan kankaalle, yhdistäen solmujen I/O-riippuvuudet (`$inputs`, `$steps.node...`) visuaalisesti.
* **The Inspector (Property Drawer):** Koska kankaalle ei mahdu tekstiä, kankaan aktiivisen solmun klikkaaminen avaa pysyvän litteän liukuvalikon oikeaan laitaan (The Inspector). Inside Inspector: 
  * "Cascading Dropdowns" varmistaa Pydantic/Stripe ID referenssien virheettömän sitomisen (Käyttäjä valitsee aiemmin laitetun solmun pudotusvalikosta ihmisluettavalla "Nomenclature" nimellä, ja UI kääntää valinnan V3-tietokantamuotoon kuten `$steps.steprule_XYZ.output`).

---

## 4. 🪟 Moniajo ja Deep Linking (System URL Router)

Koska Admin Studio tukee power-user ominaisuuksia, työnkulkujen ylläpitäjät pitävät sovellusta jatkuvasti auki selaimessa monessa eri välilehdessä (Multi-Tab), tai asennettuna Desktop-ajona useassa rinnakkaisessa moniajoikkunassa (Multi-Window Windows 11 / macOS).

* Koskaan UI ei saa ohjelmallisesti hylätä reitin selkokielistä tilaa muistiin (Esimerkiksi piilottaa sivun ID lokaaliin Riverpod tilaan). Koko navigaation absoluuttisen sijainnin on nojattava GoRouterin Type-Safe reitityksiin asynkronisesti (esim. `WorkflowDetailRoute(id: 'wf_xyz').go(context)`). 
* Joka ainut selaus ja työkalusivu on oltava saavutettavissa kopioidulla Hyperlinkillä (Deep Link). Jos käyttäjä liittää selaimen linkkikenttään solmun editorin URL:n ja painaa Enter, sen on avattava tismalleen se kyseinen saraketila ja aseteltava navigaatio senympärille virheettömästi puhtaalta pöydältä (Tab Restoration).

### 4.1 The Hybrid URL Pattern (Opaque ID + Slug)
* **SEO & Ihmisluettavuus:** Kun resursseja jaetaan linkkeinä, käytetään modernia Hybrid-mallia. URL-reitti sisältää aina muuttumattoman Stripe Pattern ID:n ja perässä luettavan aliaksen (slug): esim. `/workflows/wf_92jKs3P/uusi-riskianalyysi-2026`.
* **Tyhmä Reititin:** GoRouter ja Backend poimivat URL:sta **ainoastaan** Opaque ID:n (`wf_92jKs3P`) tietokantahakuihin. Slug-osuus on vain kosmetiikkaa (Vanity URL). Jos työnkulun nimi (ja siten slug) muuttuu, vanhat linkit eivät hajoa (Link Rot), koska haussa käytetty ID ei muutu koskaan. Tämä ehkäisee järjestelmän korruptioita syvälinkityksessä.

---

## 5. ⚡ Mutaatiot ja Toiminnallisuus (Power-User Modality)

1. **Jank-Free Rendering (Isolate):** Massiivisten DAG-puiden graafinen laskenta ja lajittelu (Topological Sort Canvasille) siirretään rutiinilla `Isolate.run()` -taustasäikeeseen. Pääthread pyhitetään vain kankaan 120Hz/144Hz -renderöinnille.
2. **Optimistic Mutations:** Työnkulkujen rakenteen päivittäminen kankaalla (esim. poistot tai relaatiot) pakotetaan tyyppiturvallisen Riverpod `Mutation` -objektin läpi. Muutos toteutuu UI:n Canvasilla nanosekunnissa optimistisena päivityksenä, ja peruutetaan Rollbackillä vain silloin, jos BFF-palvelimen Pydantic Fail-Fast verifiointi palauttaa 4xx/5xx virheen.
3. **Ohjelmallinen tiheys (Information Density):** V3 hylkää avarat listat teemoituksella `VisualDensity.compact` yli 600dp resoluutioilla.
7. **Hiiri:** Ylläpitotasolla oletetaan järjestelmällisesti mahdollisuus Hover-työkaluvihjeisiin, Context-Menuihin (Oikea ja painallus hiirissä luo uuden askeleen graafiin) ja Pikanäppäimiin (Ctrl+S, Delete node). Kosketustuen ollessa rajoittuneempi alaspäin degradoidaan nämä napit kankaan kelluvaksi Toolbariksi mobiili/tablettilaitteilla.
8. **The Gold Standard Form Model (Dumb UI):** Frontend on täysin 'tyhmä' renderöintimoottori. Hookeja (`flutter_hooks`) saa käyttää vain visuaalisiin ohjaimiin (`useTextEditingController`). Kaikki asynkroninen datan purku (`Isolate.run`), lomakkeiden tallennuslogiikka ja lataustilat **SIIRRETÄÄN EHDOTTOMASTI** puhtaisiin `@riverpod` Notifier-luokkiin. UI ei koskaan ylläpidä omia asynkronisen datan `useEffect`-kopioita tai `useState`-latauslippuja (Loading Flags).

---

## 6. 🛑 The Absolute Death & Diagnostic Node (Fallbacks Banned)

Quorum Admin Studio on ehdoton Fail-Fast -ympäristö. Hiljainen datan selviytyminen (Graceful Degradation) on BANNATTU.

1. **Ei paikkausarvoja (No Fallbacks / Initial Values):** Käyttöliittymä ei saa koskaan asettaa implisiittisiä oletusarvoja puuttuvalle backend-datalle (esim. `?? "Fallback"` tai `score: 0.0`).
2. **Absolute Death:** Jos yksittäinen UX-solmu (esim. kankaan DAG-nodi tai lista-elementti) vastaanottaa invalidia tai epätäydellistä dataa Pydantic-rajapinnasta, sen **ON KUOLTAVA** (heitettävä Exception tai palautettava `AsyncError`). Se ei saa yrittää pelastautua palauttamalla tyhjää komponenttia (`SizedBox.shrink()`).
3. **Diagnostic Node:** Kun solmu kuolee, sen ylempi suojakerros (`AppErrorBoundary`) aktivoituu ja asettaa solmun tilalle lokaalin ja räikeästi erottuvan "Error Boxin" (esim. punaisella katkoviivalla ja ErrorCode:lla varustettu laatikko). Näin järjestelmänvalvoja näkee välittömästi, mikä tietty datakomponentti on korruptoitunut kankaalla. Viat eivät enää piiloudu.
