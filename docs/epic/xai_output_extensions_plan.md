# Epic: XAI Output Extensions \-määrittelyjen reititys Tulostusprofiileihin

## Tavoite ja Ongelman Kuvaus

Tällä hetkellä `PromptBlock` (esim. `blk_440a5fef9331451b`) määrittelee staattisesti `output_extensions` \-kentässä, mitä XAI-laajennuksia se tukee (esim. `citation`, `justification`, `falsification`, `theory_link`). Tämä kertoo järjestelmälle, **mitä tietoa tekoäly tuottaa**, mutta `OutputProfile` (Tulostusprofiili) ja sen sisäiset raporttiosiot (`layouts` / `ReportLayoutModel`) eivät ota tällä hetkellä kantaa siihen, **mitkä näistä laajennuksista tulisi renderöidä lopulliselle lukijalle asetetussa raportissa**.

Ongelmana on "Sokea Tuutista Ulostulo" – on tarve kyetä valitsemaan tulostemäärittelyssä (Output Profile), mitkä datassa esiintyvät XAI-laajennukset esitetään loppukäyttäjälle. Lisäksi tavoitteena on uudistaa esitystapa siten, että valitut laajennukset irrotetaan alkuperäisten datalohkojen (Target Blocks) seasta ja kootaan ryhmiteltynä tulosteen loppuun (esim. kaikki `citation`-kentät omaan listäänsä, kaikki `risk_flag`-kentät omaansa). Tavoitteena on laatia "Fail-Fast" periaatetta ja Pydantic V2 Strict -mandaattia kunnioittava arkkitehtuuri tämän ongelman ja uuden keskitetyn esitystavan ratkaisemiseksi.

---

## Arkkitehtuurivaihtoehdot (Architectural Options)

### Vaihtoehto 1: Osion tason lista (`OutputProfileLayout.visible_extensions`)

Jokaiseen raportin osioon (Layout-objektiin) lisätään uusi taulukkokenttä `visible_extensions`.

**JSON Esimerkki (`seed_data.json` hahmotelma):**

{

  "preset\_view": "3d\_complex",

  "title": { "default\_locale": "fi", "translations": {"fi": "Globaali Johdon Yhteenveto"} },

  "show\_text": false,

  "target\_blocks": \[

    "blk\_440a5fef9331451b",

    "blk\_b476f89fb732448c"

  \],

  "visible\_extensions": \[

    "justification",

    "citation",

    "risk\_flag"

  \]

}

* **Hyödyt (Pros):** Ohjaa kaikkia kyseisen osion sisään sijoitettuja solmuja samoilla esityssäännöillä. Mahdollistaa kätevästi sen, että kaikki kyseisen osion alueelta kerätyt laajennukset voidaan koostaa siististi osion (tai koko tulosteen) loppuun ryhmiteltynä laajennustyypeittäin. Pydantic-mallit ovat täysin taaksepäin yhteensopivia `Field(default_factory=list)` myötä. UI:n (Admin Studio) puolelle helppo toteuttaa yhtenä Checkbox-listana "Raporttipohjan Osion" asetuksiin. BlueprintTransformer pystyy toteuttamaan leikkausoperaation, poimimaan halutun datan lohkoista ja hoitamaan keskitetyn ryhmittelyn dokumentin/osion loppuun.  
* **Haitat (Cons):** Samassa Layout-osiossa ei voida hienojakoisesti määrittää, että vain solmu A jättää viitteet raportin loppuun mutta B ei. Koska visio on muutenkin koota samat laajennukset keskitetysti yhteen listaan tulosteen loppuun erilleen leipätekstistä, tämä haitta on lähinnä teoreettinen ja osiokohtainen globaali sääntö on jopa toivottava.

### Vaihtoehto 2: Globaali konfiguraatio (`OutputProfile.visible_extensions`) \- 🌟 SUOSITELTU

Laajennukset määritellään kerran koko `OutputProfile` \-juuritasolla, jolloin sama asetus koskee kaikkia raportin prompt-lähteitä ja graafisia layoutteja yhdessä.

**JSON Esimerkki:**

"display\_scale": "original",

"visible\_metadata": \["date", "organization"\],

"visible\_extensions": \["justification", "citation"\],

"layouts": \[ ... \]

* **Hyödyt (Pros):** Asiakkaan toivoma "One source of truth" -raporttitason asetus. UI:ssa riittää, että tulostemäärittelyssä (Output Profile) näytetään yksi lista mahdollisista laajennuksista ja rastitetaan halutut, riippumatta siitä miltä yksittäiseltä lohkolta tuloste tulee. Valitut laajennukset kootaan keskitetysti raportin loppuun kukin omana kokonaisuutenaan.
* **Haitat (Cons):** Menettää layout/solmustason hienosäädön mahdollisuuden, mutta koska keskitetty yhdistely ja ryhmittely (kaikki saman tyyppiset tulosteen lopussa) on nimenomainen tavoite, tämä ei ole haitta vaan täsmällinen ratkaisu ongelmaan.

### Vaihtoehto 3: Kohdelohkotason Mapping (`TargetBlockConfig`)

Muutetaan nykyinen osion sääntö `target_blocks: list[str]` kompleksisemmaksi objektilistaksi: `list[TargetBlockConfig]`.

**JSON Esimerkki:**

"target\_blocks": \[

  {

    "id": "blk\_440a5fef9331451b",

    "visible\_extensions": \["justification"\]

  },

  {

    "id": "blk\_b476f89fb732448c",

    "visible\_extensions": \["citation", "risk\_flag"\]

  }

\]

* **Hyödyt (Pros):** Äärimmäinen, mikrotason kontrolli.  
* **Haitat (Cons):** Rikkoo välittömästi koodipariteetin `list[str]` olemuksesta, mikä aiheuttaa rankan taannehtivan migraation (Break-Change Pydantic V2 Strict \-tilan vuoksi) kaikkiin vanhoihin asiantuntijoihin ja tietokantoihin. Graafinen Flutter-studio muuttuisi UX-painajaiseksi, jos loppukäyttäjän pitäisi ruksia satoja asetuksia lohkokohtaisesti auki sen sijaan, että määrittäisi säännön kerralla raportin osiolle.

---

## Suositeltu valinta: Vaihtoehto 2 (Globaali lista ryhmiteltynä loppuun)

Suunnitelmana on kerätä profiilin kaikki mahdolliset laajennukset **raporttitason tulostusmäärittelyyn**, jossa näytetään yksi yhteinen lista. Käyttäjä ohjauspaneelissa voi ruksia, mitkä laajennukset otetaan tulosteeseen – riippumatta siitä tuleeko niitä yhdestä vai jokaisesta promptista (esim. Checkbox-lista Output Profilen asetuksiin). Renderöintimoottori kunnioittaa tätä globaalia valintaa, kerää kaikkien target blockien palauttamat vastaukset ja **eristää niistä vain valitut laajennukset**. Lopulta laajennukset rullataan tyypeittäin yhteen ja **tulostetaan jokainen valittu laajennus omana itsenäisenä kokonaisuutenaan koko tulosteen perään**.

---

## Toimenpiteet jatkoa varten (The Execution Plan)

Jos "PERMISSION GRANTED" annetaan ajolle, toteutus jakautuu seuraaviin järjestelmällisiin vaiheisiin (Milestones):

### Milestone 1: Backend Domain & Data Migration
1. **Python Pydantic V2 Domain (Strict Enum):**  
   * Luodaan uusi vahvasti tyypitetty Python `Enum` (esim. `XaiExtensionType`), joka sisältää sallitut laajennukset (citation, justification, falsification, jne.).
   * Lisätään `backend_v2/models/.../output_profile.py` kenttä `visible_extensions: list[XaiExtensionType] = Field(default_factory=list)` **OutputProfile -loogisen pääluokan tasolle** (Globaali ydin). Tämä aito Enum-tyypitys vaaditaan ehdottomasti, jotta Pydantic V2 Rust-ydin hylkää tuntemattomat laajennukset välittömästi Fail-Fast -periaatteen mukaisesti ja takaa turvallisen UI-koodigeneroinnin.
2. **Seed Data Vault Päivitys (Strict Migration):**  
   * Luodaan `backend_v2/seed/backups/xxx` varmuuskopio.
   * Suoritetaan turvallinen migraatio ohjelmallisesti **`c:\src\quorum\tmp\modify_seed.py`** -skriptillä (Arkkitehtuurisääntö `temporary_workspace_sandbox` - kaikki ad-hoc skriptit vain `tmp/` kansioon). Migraatio lisää kaikille olemassa oleville `OutputProfile`-entiteeteille `visible_extensions = []`.
   * Ajetaan komento `uv run python backend_v2/seed/run_seed.py local` varmistamaan JSON-rakenteen Pydantic-eheys.
   * Suoritetaan Audit: `uv run python scripts/backend_audit_loop.py backend_v2/seed --test`.

### Milestone 2: Backend Rendering & Grouping Logic
3. **Blueprint BFF (Backend For Frontend) & Ryhmittelylogiikka:**  
   * **DTO Päivitys (`backend_v2/models/xai.py`):** Lisätään `XAIOutputDTO`-luokkaan nimenomainen kenttä ryhmitellyille laajennuksille varmistamaan tyyppiturvallinen DTO-vienti eteenpäin:
     ```python
     grouped_extensions: dict[str, list[Any]] | None = Field(
         default_factory=dict,
         description="Keskitetysti ryhmitellyt XAI-laajennukset (esim. 'citation': [...])"
     )
     ```
   * **Koostaminen ja Ryhmittely (UUSI):** Renderöintimoottori (BFF) toteuttaa tiedon kokoamisen. Kaikki `Target Block` -olioista kerätyt tällä tasolla sallitut laajennukset irrotetaan lohkon sisältä ja ryhmitellään tulostus-DTO:n rakenteessa omiin kokonaisuuksiinsa (esim. kaikki `citation` -oliot yhteen taulukkoon, kaikki `risk_flag` -oliot toiseen). Tämä mahdollistaa laajennusten näyttämisen erikseen varsinaisen leipätekstin ulkopuolella tulosteen lopussa, samat extensiot tyypeittäin yhdistettynä.  
   * **Karsiminen (Strict Validation & Immutability):** Päivitetään renderöintilogiikkaa hylkäämään sellaiset datakentät, joita EI ole erikseen pyydetty profiilin `visible_extensions`-listassa. Datamuutokset on tehtävä alkuperäiseen sanakirjaan (dict) ennen Pydantic V2 `model_validate()` -kutsua, tai jos käsitellään jo instanssia, hyödynnetään `.model_copy(update={...})` -metodia. Valmista, "Frozen" Pydantic -oliota ei saa mutatoida suoraan (Sääntö: `frozen_state_mutability`). 
   * **Audit Loop:** Koodimuutosten jälkeen on ajettava `uv run python scripts/backend_audit_loop.py backend_v2/...`

### Milestone 3: Client Foundations & UI Generators
4. **Flutter Client (Strict Parity & No Fallbacks):**  
   * Päivitetään `client_app_v2/.../models/` Freezed-malli vastaamaan backendin skeemaa muodossa `required List<XaiExtensionType> visibleExtensions`. Aidon Enumin käyttö varmistaa vahvan tyyppiturvallisuuden Dartin puolella, mikä tekee UI:n Checkbox-listan rakentamisesta kestävämpää. 
   * **HUOM:** Arkkitehtuurisäännön `silent_json_fallbacks` mukaan emme saa käyttää `@JsonKey(defaultValue: [])` -virheiden piilotusta! Koska tietokannat on migroitu backendissä Vaiheessa 2, datan pitää olla täydellistä. Jätämme tiukan `disallow_unrecognized_keys: true` -säännön päälle varmistaaksemme aito Fail-Fast -kaatuminen, jos data jostain syystä puuttuu.
   * Ajetaan koodigenerointi ja audit: `cd client_app_v2 && dart run build_runner build -d && cd .. && uv run python scripts/flutter_audit_loop.py client_app_v2/...`  
5. **Flutter UI Generaattori (Optimistic UI Mutation):**  
   * Lisätään "Raporttipohjat"-osioon kootusti laajennusten Checkbox-lista, jossa käyttäjä merkitsee aktiiviset laajennukset.
   * Muokkaus tehdään Riverpod `Mutation<T>` -paradigman mukaisesti **Optimistisena Päivityksenä** (Sääntö: `mutation_optimistic_ui`). UI päivittyy heti lokaalisti, ja virhetilanteessa (`onError`) toteutetaan "Rollback" `ref.invalidate()` -komennolla, jottei käyttäjälle jää valheellista onnistumisen tunnetta.  

### Milestone 4: Client Display Components
6. **Flutter UI Komponentti (Tyhjien tilojen käsittely):**
   * Uutta renderöintilaatikkoa (esim. `XAIExtensionsBox`) rakennettaessa on otettava huomioon tekoälyn datan puuttuminen.
   * Jos käyttäjä on vaatinut profiilista laajennuksen näkyviin, mutta tekoäly ei ole tuottanut dataa (lista on tyhjä), UI välttää tyhjän otsikon haamurenderöinnin palaamalla puhtaasti: `if (extensions.isEmpty) { hyödynnä LoggerServiceProvider(logger.error); return const SizedBox.shrink(); }`. HUOM: Säännön `sized_box_shrink_ban` puitteissa sallimme tämän nimenomaan *datan liiketoimintalogiikan osalta* (tekoälyllä ei oikeasti ollut viitteitä), emmekä koodin kaatumisen piilottamiseksi, minkä takia tiedon puuttuminen yhä *logitetaan* seurantaa varten.

### Milestone 5: Output Verification
7. **Hard Artifact Testing Protocol (Visuaalinen Regressio):**  
   * Arkkitehtuurisäännön 08 mukaisesti, tekoälyn on päivitettävä tai luotava E2E-testitiedosto (esim. `test_e2e_reporting_outputs.py`). Testin tulee injektoida renderöintimoottorille mockattu `ExecutionRecord` ja sen on pakollista tuottaa fyysinen `test_report.pdf` \-tiedosto levylle. Testin pitää assertioilla ja/tai deterministisesti todentaa, että karsitut XAI-laajennukset on onnistuneesti piilotettu lopullisesta renderöidystä asiakirjasta ilman rikkinäisiä laatikkoja.

