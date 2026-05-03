# Epic 44: Virtuaaliset System-Askeleet (Näkyvyys Tausta-ajoihin)

## 1. Yhteenveto (Executive Summary)
Tavoitteena on tuoda näkyväksi pitkään kestävät tausta-ajot (kuten PDF-raporttien koonti ja LLM-synteesi) käyttöliittymän työnkulkunäkymään. Tämä tehdään "Virtuaalisten System-Askelien" (Virtual System Steps) avulla ilman, että rikotaan GraphEnginen tiukkaa DAG-moottorin SSOT-historiaa.

**Liiketoiminta-arvo:** Parantaa järjestelmän UX:ää ja läpinäkyvyyttä. Käyttäjä ei enää koe järjestelmän "jumittavan" työnkulun päätyttyä, vaan näkee selkeästi "Raportin koonti" -askeleen. Tämä mahdollistaa myös on-demand tulosteiden (eri tulostemallien) uudelleenluonnin visualisoinnin täysin samalla komponentilla.

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

## 4. Tekniset Vaatimukset (Frontend)
- Frontend (Flutter) lukee jo valmiiksi kaikki askeleet `ExecutionRecord.steps` -sanakirjasta.
- Koska virtuaalinen askel on tietorakenteeltaan täysin validi `StepRecord` (sisältää tilan ja nimen), sen pitäisi automaattisesti piirtyä UI-komponenttina (`StepCard` tms.) oikein ilman suuria koodimuutoksia.
- **Testaus:** Varmistettava, että käyttöliittymän "Kokonaisedistyminen" (Progress Bar) ymmärtää, että askeleita on tullut yksi lisää lennosta, eikä se sekoa 100% laskennassa.

## 5. Taaksepäin Yhteensopivuus ja Zero-Trust
- Arkkitehtuuri noudattaa "Fail-Fast" ja "Zero-Trust" -periaatteita: emme muuta aiempia Pydantic-validaatioita tai DAG-moottorin ydintä.
- Uudet virtuaaliset askeleet tunnistetaan selkeästi `sys_` -etuliitteellä (esim. `sys_render`), jotta ne voidaan tarvittaessa erottaa analytiikassa aidoista AI-arviointiasteleista.
- SSOT (Single Source of Truth) säilyy tietokannassa.

## 6. Toteutuksen Karkaisu (Tier 2 Hardening)
- Kaikkien päivitysten on tapahduttava keskitetysti `repository.update_execution()` -metodin kautta atomisesti, jotta Redis Pub/Sub ja SSE-stream pysyvät täydellisesti synkronissa tietokannan tilan kanssa.
