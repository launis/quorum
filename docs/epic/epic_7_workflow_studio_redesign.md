# Epic 7: Workflow Studio V3 Redesign (Admin App)

**RIIPPUVUUS:** Tämä Epic käynnistetään vasta **[EPIC_v3_flutter_frontend_adaptation.md]** -suorituksen jälkeen. Ennen tätä Epiciä Flutter-arkkitehtuurin perusta (Riverpod 3.0 Mutaatiot, Isolate-parsinta, SSE State ja `AppException` tason Actionable Hint -virheenhallinta) on oltava valmiina tuotantokäyttöön.

## 📌 Context
Käyttäjäpalaute osoitti, että nykyinen "Työnkulun Asetukset" (Workflow Settings) -näkymä on sekava. Se suoltaa kaiken informaation yhdelle sivulle ja sallii heikosta typologiasta johtuvia rikkoutumia (vapaatekstisyötteitä ja suttuisia hook-valikoita).

Tässä Epicissä Admin Studion työnkulunrakentaja rakennetaan täysin uusiksi tiukkojen `AdminStudio_V2_UI_Architecture.md` The Flat MVC ja Omni-Navigation -sääntöjen mukaiseksi. Keskiössä on loogisuus, V3-moottorin työkalutuet (MCP) ja tekoälyn turvallisuusrajoitteet (Safety).

## 🎯 Objectives
1. **Litteä Navigaatio (Master-Detail):** Luodaan Listausnäkymä (`WorkflowListView`) SWR (Stale-while-revalidate) välimuistilla riemuitsemaan välittömän 0-viiveen paluunavigoinnin.
2. **Jakaa Editori Loogisiin Välilehtiin (Tabs):** Yksittäisen työnkulun muokkaus jaetaan neljään sallittuun `TabBar`-välilehteen (Kontekstin sisällä sallittu navigaatio).
3. **Poistaa Vapaatekstiavaimet (Relational Integrity):** Kielletään kaikkien riippuvuuksien ja viitteiden kirjoittaminen käsin TextFieldillä. Kaikki avaimet valitaan Dropdown/Checkbox-valikoista.

---

## 🏗️ Milestones & Implementation Tasks

### Milestone 1: Työnkulkujen Hakemisto (List View)
Työnkulkujen hallinnan "Etusivu".
- **Ominaisuudet:** Lista, Työnkulun kloonaus (Copy), Haku.
- **Teknologia:** Riverpod `keepAlive()` mahdollistaa nollaviiveen selailussa. Tallennukset operoivat `Mutation<void>` optimistisina päivityksinä.

### Milestone 2: App Shell & Meta/Syötteet (Tabs A & B)
- **Tab A: Yleiset (General):** Nimi, Slug ja metadata. Käyttää `I18nTextField` -komponenttia Pydantic I18nText mallin luontiin.
- **Tab B: Odotetut Syötteet (Expected Inputs):** Tässä määritellään globaalit syöteroolit (esim. `doc_pdf`). Relational Integrity -säännön mukaisesti uudet syöteroolit rekisteröidään keskitettyyn sanastoon, josta niitä valitaan putosiin. Tämä suojaa backendin $inputs -reititystä.

### Milestone 3: Työnkulun Rakentaja & Node Inspector (Tab C)
Graafinen verkkoeditori (DAG Builder) askeleille ja riippuvuuksille (`depends_on`). Kun askel (Node) klikataan, aukeaa Property Drawer -paneeli, johon V3-innovaatiot purkautuvat:
- **Strategiat:** `model_strategy` pudotusvalikko (Controlled Vocabulary Pydantic-skemoista).
- **Turvallisuustaso (Safety Slider):** Pakollinen valinta (`safe`, `moderate`, `unsafe`), määrittää Agentin autonomian rajoitteen Fail-Fast -putkessa.
- **MCP Työkalut (Ulkoiset Integraatiot):** Vanhat `pre_hooks` / `search.py` -kovakoodaukset ovat poissa. Studion UI kysyy Backendin uudesta Tool Keystoresta sallitut The Model Context Protocol (MCP) -työkalut (kuten `google-search`, `fetch-url`). Käyttäjä raksii `allowed_mcp_tools` taulukkoon ne työkalut, joita askeleella on valtuus käyttää (Principle of Least Privilege).
- **Datan reititys (Semantic Data Flow):** Älykäs Pydantic mapping UI. Dropdown-valikoita, jotka pakottavat askeleiden syötteet joko olemassa olevaan `$inputs` tai edellisen `$steps.x` datarajapintaan.

### Milestone 4: Flat MVC Layout Roolituksen Luonti (Tab D)
- **Tab D: Raportit (Output Profiles):** Kytketään taustajärjestelmän askeleet 1D/2D/3D asetteluihin. 
- Mandaatti MVC refaktoroinnille (SDUI:n kuolema) tarkoittaa, ettei täällä rakenneta UI-puita. Käyttäjä ainoastaan ryhmittelee `ReportDataDTO` sääntöjä The De-Generator mallille: *"Nämä 3 askelta sijoitetaan 2D-Matriisiin "*.

### Milestone 5: Pre-Flight Validointi (Dry Run) & Rollback
Lisätään Editorin App Bariin pysyvä "Validoi" (Dry Run) -painike:
- Frontend validoi riippuvuudet jo visuaalisella tasolla (esim. poistaa Dropdownista solmut jotka johtaisivat Infinite Loop -kehäviitteeseen).
- Painike lähettää draftin serverille Topological Sort -algoritmille (Kahnin Algoritmi). Estetään katkenneet datareitit.
- Jos API palauttaa virheen `RFC 7807` muodossa, UI ei kaadu tai lukitu, vaan hyödyntää `GlobalErrorView V3` lokalisointia tuottaen ohjeen: *"Viittaus puuttuvaan askeleeseen x. [Sulje]"*. Optimistinen mutaatio rullataan sivistyneesti takaisin (Rollback) muistissa.

---

## 🛡️ Next Steps
Kun `EPIC_v3_flutter_frontend_adaptation.md` perusputkisto on asennettu uuteen konteksti-ikkunaan (uusi chatti) ja integroitu onnistuneesti API / SSE tasolla, edetään tämän Epic 7 kimppuun `implementation_plan.md` luomisella ja Studio GUI:n lopullisella viimestellisyydellä.
