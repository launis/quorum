# Admin Studio V2 & Client: Adaptive UI & Architecture Manifesto

**PROJECT**: Cognitive Quorum V2 Platform
**STATUS**: Mandatory Architecture Law for Web/Desktop/Mobile clients
**REFERENCE**: Based on Flutter `Adaptive-Responsive` best practices & The De-Generator Mandate.

---

## 1. THE DE-GENERATOR MANDATE & FLAT MVC
Quorum käyttöliittymä ei rakenna graafisia käyttöliittymäpuita dynaamisesti (ei SDUI:ta). Arkkitehtuuri on tiukka Flat MVC, jossa data ja esitys on erotettu täysin toisistaan:

* **Backend (Model/Controller)**: Palauttaa litteän graafisen mallin (`ReportDataDTO` ja `OutputProfile`), joka sisältää vain puhtaan datan ja asettelutyypin (esim. 1D Metrics, 2D Matrix, 3D Complex).
* **Frontend (View / De-Generator)**: Flutter-asiakasovellus lukee litteän datan ja "generoi" itse tyylitellyt natiivikomponentit nollamatematiikka-säännöllä (Zero-Math UI).

Työnkulut (Workflows) ja Rakennuspalikat (PromptBlocks) hallitaan ja tallennetaan puhtaasti datavetoisesti.

---

## 2. THE OMNI-NAVIGATION MANDATE (FLAT HIERARCHY)
Päänavigaatio ei saa koskaan jakautua useaan paikkaan (Sekä AppBar/TabBar että Sidebar). Kaikki järjestelmän ylätason moduulit on pakotettu **yhdelle tasaiselle hierarkiatasolle (Flat Hierarchy)**.

* **BANNED**: Yläpalkin välilehdet (`TabBar` tai `AppBar` title-menut) **globaalissa navigaatiossa**.
* **MANDATORY**: Koko sovellusta ohjaa tasan yksi käyttöliittymäkomponentti, joka mukautuu näytön kokoon (Omni-Navigation).

### 2.1 Päänavigaatiorakenne (V3 Flat Routing)
Navigaatiopalkin elementit Admin Studiossa on lukittu seuraavaan muotoon:
1. **Hallintapaneeli** (Suoritukset ja Yleiskatsaus)
2. **Työnkulut** (Workflow DAG -hallinta ja orkestrointi)
3. **PromptBlockit** (Tekoälyn rakennuspalikat The PromptBlock Strategy -mallin mukaan)
4. **Mallirekisteri** (Konfiguraatiot ja LLM-mallit)
5. **Organisaatiot** (Käyttäjien, roolien ja lisensoinnin hallinta)
6. **Asetukset** (Sovellustason globaalit järjestelmäkonfiguraatiot)

---

## 3. ADAPTIVE BREAKPOINTS & ROUTING RULES
Noudatamme täsmällisiä Flutter-suosituksia näytön fyysisen leveyden suhteen (`LayoutBuilder`, `MediaQuery`):

* **< 600dp (Mobile View):** 
  * Käytetään yksinomaan `NavigationBar` (Bottom nav). 
  * Yläpalkissa (`AppBar`) on vain nykyisen näkymän tekstiotsikko ja spesifisesti kyseisen näkymän konteksti-toiminnot (esim. Tallenna/Julkaise -napit).
* **>= 600dp (Tablet/Desktop View):** 
  * Käytetään yksinomaan `NavigationRail` (Left nav). 
  * Näytön ollessa erittäin leveä (>1200dp), Rail voi vaihtua `extended = true` tilaan, jolloin ikonien vieressä näkyvät tekstit.

**Routing Mandaatti (`StatefulShellRoute`):**
GoRouter käyttää tilaan perustuvaa `StatefulShellRoute` reititystä. Tämä säilyttää jokaisen välilehden oman navigointipinon ja ramin (Scroll position, syötetyt lomakekentät), estäen keskeneräisen datan katoamisen päävälilehtiä vaihdettaessa.

---

## 4. THE WORKSPACE CONTEXT (ORGANISAATIOT)
Kaikki datamallit (Työnkulut, PromptBlockit) on luvitettu (`tenant_id`). Käyttäjän on aina nähtävä selkeästi, missä työtilassa ollaan.

* **Sijainti:** Vasemman `NavigationRail`:n ehdottomassa huipussa tai ylänavigaatiossa tulee olla koko ajan näkyvä **Workspace Switcher** (esim. "Aktiivinen: Sitra").
* **Mutaatio:** Kun Workspacea vaihdetaan pudotusvalikosta, kyseinen toimenpide päivittää globaalin Riverpod-tilan (`selectedOrganizationProvider`), joka **automaattisesti invalidoi** (`ref.invalidate()`) asynkronisesti kaikki tilatut listaukset. Järjestelmä hakee uuden organisaation sisällön lennosta muistiin eristäen tenant-tiedot turvallisesti.

---

## 5. TABBAR SALLITUT KÄYTTÖTAPAUKSET
Vaikka `TabBar` on kielletty globaalilla tasolla, sitä **käytetään yksittäisten entiteettien sisäisessä asioinnissa**.

**Esimerkki sallitusta käytöstä:**
Käyttäjä avaa Työnkulun "Riskianalyysi V2" luodakseen uuden logiikan. Koko ruudun editorissa on loogista käyttää `TabBar`:
* Välilehti 1: Yleiset asetukset (Metadata, Nimi)
* Välilehti 2: DAG-solmut (Säännöt ja Riippuvuudet)
* Välilehti 3: Output Profile (Litteän raportin asettelu)

Nämä välilehdet kuuluvat täysin "Riskianalyysin" kontekstiin eivätkä navigoi pois kyseisestä entiteetistä muihin järjestelmän pääosiin.

---

## 6. RELATIONAL INTEGRITY (NO FREE-TEXT KEYS)
Kaikki käyttöliittymän syötteet (Inputs), jotka määrittelevät **relaation, riippuvuuden tai järjestelmätason tunnisteen** kahden entiteetin välillä, on ehdottomasti toteutettava pudotusvalikoilla (Dropdown/Select, Autocomplete tai Checkbox). Vapaa tekstinsyöttö (TextField) on näissä kielletty datan pirstaloitumisen ja inhimillisten kirjoitusvirheiden estämiseksi.

* **BANNED:** Käyttäjä kirjoittaa tekstikenttään vapaasti `data_path` säännön omien muistikuvien mukaan.
* **MANDATORY:** Tekstikentän sijaan käytetään pudotusvalikkoa (Controlled Vocabulary), josta käyttäjä ainoastaan **valitsee** sallitun PromptBlockin tai järjestelmän tarjoaman avaimen. Backend sanelee sallitut avaimet.

---

## 7. MUTAATIOT JA CATCH ("THE RIVERPOD 3.0 LAW")
Admin Studion verkkopyynnöt ja tallennukset on hallittava modernisti Riverpod 3.0 arkkitehtuurilla.

* Keskustele vaativista asioinneista (mutations) `Mutation<void>` -objektilla. Unohda asynkroninen manuaalinen tilanhallinta (esim. `bool _isLoading = true`).
* Vältä blokkaavia latausanimaatioita luku-listoissa tekemällä silent Stale-While-Revalidate (SWR) taustapäivityksiä tai Optimistic Updates -päivityksiä lomakkeissa.
* Älä sokaise Frontendiä `try/catch` lohkoilla, jotka piilottavat ja hukkaavat verkkovirheet. Ohjaa kaikki fataalit epäonnistumiset The Translation Boundaryn ja The Dual-Reporting Mandaatin mukaisesti `AppException`in kautta Actionable Hinteiksi, jotka näytetään `GlobalErrorView` (tai Layer-kohtaisen ErrorView) -komponentin kautta rakenteellisesti asiakkaalle.

---

## 8. WORKFLOW SOLMUJEN KONFIGUROINTI (MCP & SAFETY)
**V3 Core Engine Big Bang** -päivitys (P6) tuhosi kokonaan vanhan tavan kytkeä Python-tason kovakoodattuja hookkeja (kuten `search.py`) suoraan työnkulkuihin. Kaikki integraatiot on nyt harmonisoitu asynkroniseen Model Context Protocol (MCP) -arkkitehtuuriin. Tällä on suora vaikutus Admin Studioon, kun käyttäjä rakentaa graafista DAG-työnkulkua:

### 8.1 The Safety Slider (Fail-Fast Kuori)
Jokaisella Työnkulun askeleella (`Step`) on pakollinen turvallisuustaso the Fail-Fast mallin mukaisesti. Se sanelee, saako kyseisen solmun sisältämä tekoäly-agentti ajaa työkaluja ilman ihmisen valvontaa (Autonomous Loop).
* **MANDATORY UX:** Admin Studion Step-editorin on tarjottava pakollinen Dropdown/Slider Enum-valinta kentälle `safety` (Vaihtoehdot lukuhetkellä: `safe`, `moderate`, `unsafe`). Se ei saa olla vapaasti kirjoitettava teksti.

### 8.2 The MCP Tool Checklist (Ulkoiset Työkalut)
Nykyinen V3 Backend ei enää aja sokeasti "kaikkia tuettuja työkaluja". Se antaa agentille tasan ne kyvykkyydet, jotka Admin Studion kautta on askeleeseen salittu the Principle of Least Privilege -säännöllä.
* **MANDATORY UX:** Työnkulun askeleiden hallinnassa (DAG Builder) on oltava visuaalinen valikko Backendin ilmoittamista The Tool Registryn MCP-työkaluista (esim. `["google-search", "fetch-url"]`). Käyttäjä raksii `allowed_mcp_tools` -listaan mitkä työkalut tällä kyseisellä solmulla on valtuutettu ajaa LLM:n kontekstissa. Vapaateksti on tässäkin Relational Integrity -mandaatin nojalla täydellisesti kielletty.
