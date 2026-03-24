# End-to-End Output Generation Pipeline (Quorum V2 BFF Architecture)

## 0. Tavoite (System Objective)
Tämän järjestelmän päätavoite on rakentaa tyylikäs, murtumaton ja joustava tulostusarkkitehtuuri (**Backend-For-Frontend, Zero-Math Frontend**). 

Tämä saavutetaan erottamalla tekoälyn "kognitiivinen aivotyö" (tiedon louhinta ja pisteytys) täydellisesti sen "graafisesta esittämisestä". Tavoitteena on kyetä tulostamaan yksi massiivinen tekoälyraportti dynaamisesti eritasoisina näkyminä – Johdon Tiivistelmänä tai Raakana Excel-vientinä – vailla riviäkään uutta käyttöliittymäkoodia.

---

## 1. The Foundation: Database & Event Log

### The Database (Service / Repository Layer)
* **Role**: The **Immutable Ledger**.
* **Function**: Persists the event log (`ExecutionRecord`) täysin irrallaan ulkoasusta.

### The Software (GraphEngine / DAGExecutor)
* **Role**: The **Deterministic Processor**.
* **Standardization**: `PromptCompiler` rakentaa Pydantic V2 Domains (`Step_{id}_Response`) lennosta `PromptBlock` sääntöjen pohjalta. Jos LLM hallusinoi ohitse säännön, kentät hylätään (`extra="ignore"`), taaten puhtaan datan.
* **Persistence Boundary**: Moottori tallentaa tulokset `ExecutionRecord.results` sanakirjaan. Tänne ei enää koskaan tallenneta tulostusohjeita, käännöksiä tai esitysmuotoja (The DB Purity Mandate).

---

## 2. Phase I: Tulostusprofiilien Domain (The Blueprint Master)

Toisin kuin legacy-(SDUI)-arkkitehtuurissa, tulostusprofiilit (Output Profiles) on nostettu työnkuluista riippumattomiksi Domain-tason entiteeteiksi (`/api/v2/output-profiles/`).

### Strict UI/UX CRUD
Admin-studio ei salli enää vapaamuotoisten raakojen ID-merkkijonojen naputtelua (`blk_...`), vaan asettelu (`OutputProfileLayout`) luodaan tiukalla CRUD-näytöllä:
*   Käyttäjä valitsee tyypiksi esim. *1D Laatikko, 2D Matriisi tai Excel Riviluettelo*.
*   Käyttäjä linkittää akselit valitsemalla olemassa olevan solmun (komponentin) alasvetovalikosta.
*   Pydantic torjuu heti kättelyssä (HTTP 422), jos samaan matriisiin yritetään syöttää ristiriitaista kenttää, tai jos englanninkielinen `I18nText` käännösavain uupuu.

---

## 3. Phase II: State Presentation & Rendering (Omni-Channel BFF)

Koska `ExecutionRecord` sisältää raakaa dataa, se yhdistetään pyydettyyn Tulostusprofiiliin *Vasta luku- / tulostushetkellä*. 

### 3.1 Dynaaminen Valinta (1:N Suhde)
Yksittäinen ajo ei ole lukittu yhteen oikeaan muotoon. Käyttöliittymä tai API kutsuu reititintä:  `GET /api/v2/executions/{id}/report?profile_id={haluttu_profiili}`. 
Sama ajo voidaan välittömästi uuttaa Johdon Tiivistelmäksi (Profile A) tai DataGrid/Excel Excel -vienniksi (Profile B).

### 3.2 Kääntäjä (The BFF Compiler) & Collision Avoidance
Sielu lepää `blueprint.py` Kääntäjässä. Tämä rajapinta purkaa pyydetyn profiilin, etsii vastaavuudet ajon tulosdatasta ja laskee näytön/PDF:n tarvitseman ViewModel-rakenteen lennosta.
1. **Zero-Math:** Flutter ja PDF eivät laske enää mitään (`1D vs 2D`). Python kääntäjä muodostaa valmiin ViewModel Noden (esim: `{"type": "matrix_2d", "x_label": "Riski", "x_value": 4.0}`).
2. **Kenttien Automaatio (Excel):** Riviluetteloita (DataGrid/Excel) rakennettaessa kääntäjä päättelee sarakeotsikot suoraan työnkulun natiivin solmun nimestä estäen kirjoitusvirheet.
3. **Collision Avoidance Hierarchy:** Jos tulosteeseen on osumassa kaksi saman nimistä komponenttia (esim. kaksi "Riskiä"), kääntäjä kiipeää automaattisesti isä-puulistan (DAG) ylemmille tasoille eriyttääkseen nimen turvalliseksi (esim. "Myynti - Riski" vs "Hallinto - Riski"), taaten 100% uniikit Excel-sarakeotsikot ilman asiantuntijoiden asettamia rajoitteita.
4. **Resilienssi Datan Muuttuessa:** Jos ajaudutaan tilanteeseen, jossa tulostin odottaa `2D Matriisia`, mutta ajo sisälsikin muuttuneen työnkulun ja ohitettujen askeleiden takia vain 1 matriisiakselin, Kääntäjä ei lähetä rikkinäistä 2D-koodia eteenpäin. Se suorittaa automaattisen geometrisen degradaation, lakkauttaen paketin "1D Info Box" muotoon, suojaten Frontendin kaatumisilta täysin näkymättömästi.

---

## 4. Phase III: Rendering Environments (The Dumb Client)

Tavoitteena on sataprosenttinen pariteetti Flutterin (Näyttö) ja PDF:n (Tuloste) välillä tukeutuen samaan BFF ViewModel -listaan. Koska laskentataakka on siirretty Backendiin (Python), Renderöintimoottorit ovat tyhjiä iterointisilmukoita.

**A. Flutter UI (Reaaliaikainen Näyttötulostus)**
* Flutter tekee kutsun (`/report?profile_id=...`). 
* Vastaanottaa Backend-For-Frontend ViewModel listan.
* `report_renderer_widget.dart` for-looppaa (silmukoi) pelkän koodityypin läpi ja liittää valmiiksi käännetyt arvot yksinkertaisiin tyhmiin UI-kortteihin (`info_box` -> HTML paneeli, `matrix_2d` -> FlChart). Se on sokea puskutraktori.

**B. Palvelimen Asynkroninen PDF-Worker (Staattinen Tulostus Taskina)**
* Käyttäjä pyytää PDF-tulosteen (`POST /executions/{id}/render_pdf?profile_id=...`).
* Palvelimen taustaprosessi kutsuu tismalleen samaa `blueprint.py` Kääntäjää (The Shared Core). Se saa saman lasketun Node-listan.
* Jinja2 HTML/CSS moottori iteroi muuttujat PDF-rakenteeseen 1-suhde-1. Matematiikasta vapautettuna Jinja tekee asettelun täydellisesti ja WeasyPrint muuntaa sen dokumentiksi luotettavasti.

---

## 5. Menneisyyden Haarniskan Purku (Legacy Removal Notice)
V2 BFF Arkkitehtuuri julistaa ohjelmistosta vanhentuneeksi lukuisia aiempia (Phase V1 ja V6) kerroksia:
* 🚫 **Flutter SDUI Logic:** Älä kirjoita Flutteriin ehtolausekoodia näyttämään "yksinkertaista" tai "laajennettua" kuvaajaa. Anna Backendin päättää laatikon tyyppi.
* 🚫 **Tietokannan Käännökset:** Tulostukseen tai näyttöön liittyviä käännösavaimia tai tekstejä ei koskaan säilötä `ExecutionRecord` lokiin. 
* 🚫 **Raaka Blueprint Editor:** JSON-muotoista koodia ei editoida enää selaimen UI:n kautta, vain selkeitä alasvetovalikko-Formeja sallitaan.
