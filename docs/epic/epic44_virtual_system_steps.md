# Epic 44: Virtuaaliset System-Askeleet (Näkyvyys Tausta-ajoihin)

## 1. Yhteenveto (Executive Summary)
Tavoitteena on luoda **yleinen Arq-työnkulkujen (tausta-ajojen) hallinta- ja visualisointimenetelmä**. Pitkään kestävät tausta-ajot, kuten dynaaminen tulostemallikohtainen pisteiden laskenta (Scoring), LLM-synteesi ja PDF-raporttien koonti, tuodaan näkyväksi täsmälleen samaan käyttöliittymän työnkulkunäkymään kuin perinteiset AI-askeleet. Tämä tehdään "Virtuaalisten System-Askelien" (Virtual System Steps) avulla ilman, että rikotaan GraphEnginen tiukkaa DAG-moottorin SSOT-historiaa.

**Liiketoiminta-arvo:** Parantaa järjestelmän UX:ää ja läpinäkyvyyttä. Käyttäjä ei enää koe järjestelmän "jumittavan" työnkulun päätyttyä, vaan näkee selkeästi visualisoituna, miten "Pisteiden laskenta" tai "Raportin koonti" etenee muiden työvaiheiden jonossa. Tämä menetelmä kattaa saumattomasti sekä automaattisen päätyönkulun loppuajot että yksittäisten, on-demand -tulosteiden (esim. tulostemallin vaihdon tai erillisen PDF-luonnin) visualisoinnin.

## 2. Arkkitehtoniset Taustat ja Haasteet
- **Nykytilanne:** Kun työnkulku (DAG) valmistuu, `worker.py` asettaa `ExecutionRecord`-tilan välittömästi `COMPLETED`-tilaan ja lähettää synteesin (`render_profile_job`) erillisenä taustatyönä Redis-jonoon. Käyttöliittymä näyttää "Completed" heti, eikä kerro synteesin tai PDF-generoinnin edistymisestä mitään.
- **Miksi aito DAG-solmu (Option B) hylättiin:** Jos synteesistä tehtäisiin aito GraphEnginen solmu (`PromptBlock`), sen uudelleenajaminen (esim. kun käyttäjä haluaa vaihtaa raporttipohjaa on-demand) vaatisi valmiin työnkulun tilan ja historian rikkomista tai rinnakkaisen, kokonaan piilossa olevan suorituspolun rakentamista uudelleenluonneille.
- **Ratkaisu (Virtuaalinen Askel):** Irrotamme "tilaseurannan" ja "DAG-suorituksen" toisistaan. Injektoimme manuaalisesti `ExecutionRecord.steps` -sanakirjaan uuden askeleen (esim. `sys_render_default`), jota Arq Worker ja API-endpointit hallitsevat manuaalisesti ohi DAG-moottorin.

## 3. Tekniset Vaatimukset (Backend)

### 3.1. Automaattinen ajo (Ensimmäinen kerta)
- Tiedosto: `backend_v2/worker.py`
- Kun `execute_workflow` on suoritettu, Arq Workerin tulee päivittää `ExecutionRecord`-dokumenttiin uusi askel ennen tilan vaihtamista `COMPLETED`-tilaan:
  ```json
  "steps": {
    ...
    "sys_render_default": {
      "status": "running",
      "name": "Raportin koonti ja tulostuksen valmistelu",
      "updated_at": "..."
    }
  }
  ```
- Koko työnkulku (`execution.status`) pidetään `RUNNING` -tilassa, kunnes synteesi on valmis, jotta käyttöliittymä ymmärtää prosessin jatkuvan.

### 3.2. On-Demand Uudelleenluonti (Tulostemallin vaihto)
- Tiedosto: `backend_v2/api/routers/execution/executions.py`
- Rajapinta `POST /{execution_id}/render_pdf` (ja mahdollisesti `GET /render`) päivittää vanhan, jo valmiin `ExecutionRecordin` tilaa:
  - Injektoi uuden askeleen (esim. `sys_render_X`), jos sitä ei ole.
  - Asettaa askeleen tilaan `RUNNING`.
- Järjestelmän tulee lähettää SSE-päivitys välittömästi, jotta käyttöliittymään aukeaa lataus-spinner.

### 3.3. Askeleen Valmistuminen (Taustatyöt)
- Tiedosto: `backend_v2/worker.py`
- Arq-työt `generate_pdf_job` ja `render_profile_job` ottavat vastuun `sys_render_<profile>` -askeleen tilapäivityksestä:
  - Onnistuessa: `status="completed"`.
  - Epäonnistuessa: `status="failed"`.
  - Molemmissa tapauksissa myös itse työnkulun (`ExecutionRecord`) tila on päivitettävä takaisin `COMPLETED`-tilaan, jos se jätettiin aiemmin `RUNNING`-tilaan.

### 3.4. Dynaaminen Tulostemallikohtainen Pisteiden Laskenta (Profile Scoring)
- Osana Epic 46:tta arviointimoottorin matematiikka (Strictness & Scoring Strategy) sidotaan tulostemalliin. Tämän dynaamisen laskennan on **ehdottomasti** tapahduttava Arq-taustatyönkulun (`render_profile_job`) sisällä.
- Laskentaa ei saa suorittaa synkronisesti API-reitittimessä, jotta vältetään FastAPI-säikeen tukkiminen (Blocking the Event Loop -mandaatin rikkominen).
- Arq-workerin vastuu: Lataa `Frozen Contextin` raakadata (atomit), ajaa pyydetyn Output Profilen mukaisen matematiikkamoottorin, syöttää lasketut pisteet LLM-synteesille, tallentaa `ReportDataDTO`:n välimuistiin ja päivittää lopuksi virtuaalisen askeleen (`sys_render...`) tilan valmiiksi.

### 3.5. Yleinen Arq-työnkulkujen Hallintamenetelmä (General Arq Workflow Management)
- Tämä mekanismi ei rajoitu vain yhteen `sys_render` -askeleeseen, vaan luo standardoidun, yleisen tavan käsitellä mitä tahansa Arq-tausta-ajoa (esim. `sys_scoring`, `sys_pdf_gen`).
- Kun mikä tahansa raskas taustatyö käynnistetään (joko osana päätyönkulkua tai on-demand -pyyntönä), backend:
  1. Injektoi virtuaalisen askeleen `ExecutionRecord.steps` -sanakirjaan tilalla `RUNNING`.
  2. Pakottaa koko työnkulun päätilan takaisin `RUNNING`-tilaan, jos se oli jo valmis (esim. jälkikäteen tehty PDF-pyyntö).
  3. Lähettää SSE-tapahtuman (Server-Sent Event), jotta UI päivittyy välittömästi reaktiivisesti.
  4. Arq-työn päättyessä kuittaa virtuaalisen askeleen (`COMPLETED` tai `FAILED`) ja palauttaa työnkulun päätilan ennalleen.

## 4. Tekniset Vaatimukset (Frontend)
- Frontendin (Flutter) on hyödynnettävä **täsmälleen samaa käyttöliittymäkomponenttia** (askeleiden listanäkymä ikoneineen ja lataus-spinnereineen) virtuaalisten askeleiden esittämiseen kuin mitä se käyttää aitojen LLM-askeleiden (kuten "Faktantarkistaja", "Analyst") esittämiseen.
- Käyttäjän ei pidä visuaalisesti erottaa, onko kyseessä tekoälyn suorittama solmu vai Arq-taustatyö (kuten "Scoring Engine" tai "PDF Generointi"). Kaikki askeleet näkyvät yhtenäisenä, alaspäin rakentuvana listana.
- **Yksittäiset tulostukset (On-Demand):** Kun käyttäjä painaa UI:ssa myöhemmin "Luo uusi raportti" tai vaihtaa tulostemallia jo valmiissa ajossa, olemassa olevaan askeleiden listaan on ilmestyttävä lennosta uusi virtuaalinen askel pyörivällä spinnerillä.
- **Testaus:** Varmistettava, että käyttöliittymän "Kokonaisedistyminen" (Progress Bar) ymmärtää lennosta dynaamisesti kasvavan askelmäärän (Total Steps = AI-askeleet + Virtuaaliaskeleet) eikä sekoa prosenttilaskennassaan.

## 5. Taaksepäin Yhteensopivuus ja Zero-Trust
- Arkkitehtuuri noudattaa "Fail-Fast" ja "Zero-Trust" -periaatteita: emme muuta aiempia Pydantic-validaatioita tai DAG-moottorin ydintä.
- Uudet virtuaaliset askeleet tunnistetaan selkeästi `sys_` -etuliitteellä (esim. `sys_render`), jotta ne voidaan tarvittaessa erottaa analytiikassa aidoista AI-arviointiasteleista.
- SSOT (Single Source of Truth) säilyy tietokannassa.

## 6. Toteutuksen Karkaisu (Tier 2 Hardening)
- Kaikkien päivitysten on tapahduttava keskitetysti `repository.update_execution()` -metodin kautta atomisesti, jotta Redis Pub/Sub ja SSE-stream pysyvät täydellisesti synkronissa tietokannan tilan kanssa.
