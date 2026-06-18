# EPIC: Worker Refactoring - Dismantling the Orchestration God Object

## 1. Tausta ja Konteksti
`backend_v2/worker.py` on paisunut yhdeksi koko backendin suurimmista "Jumal-luokista" (God Object). Se on tällä hetkellä lähes 50 kilotavua ja yli 1000 riviä pitkä monolyytti, joka vastaa käytännössä koko järjestelmän asynkronisesta ytimestä.

**Nykyiset vastuut, jotka on ahdettu yhteen tiedostoon:**
1. **Redis-työjonojen hallinta:** RQ-workerin asennus, jobien reititys ja jonotus (`execute_workflow_job`, `render_profile_job`).
2. **Liiketoiminta- ja USD-matematiikka:** Tokenien laskeminen yhteen, USD-hintojen accumulointi (jonka bugin korjasimme kesäkuussa 2026), sekä profiilien renderöinnin matematiikka.
3. **Tietokannan elinkaari:** `ExecutionRecord`in tilamuutokset (running -> completed -> failed), step-tulosten päivittäminen ja audit-lokien tallentaminen MongoDB/TinyDB-kantaan.
4. **Ulkoiset integraatiot:** Webhookien lähettäminen ja sähköpostiraporttien liipaiseminen ajon päätteeksi.
5. **Synteesin ja PDF:n orkestrointi:** `text_consolidation_hook`:in kutsuminen ja PDF/HTML-koodin luomisen käskytys.

Tämä rikkoo pahasti **Single Responsibility Principle (SRP)** -sääntöä. Jos esimerkiksi USD-kustannuslogiikkaan halutaan tehdä muutos, koodari joutuu kahlaamaan läpi satoja rivejä Redis-työjonologiikkaa ja Webhook-koodia. Tämä altistaa järjestelmän kriittisille bugeille (kuten kesäkuussa 2026 havaittu DAG-kulujen katoaminen).

## 2. Tavoite
Purkaa `worker.py` kolmeen selkeään, erikoistuneeseen komponenttiin. Varsinainen `worker.py` jää ainoastaan ohueksi reitittimeksi (Router), joka ottaa vastaan Redis-tehtävät ja delegoi ne eteenpäin oikeille asiantuntijaluokille.

## 3. Suunnitellut Arkkitehtuurimuutokset

### A. `JobQueueManager` (Redis-infrastruktuuri)
* **Vastuu:** Kuuntelee Redis-jonoa, ottaa vastaan jobit (`execute_workflow_job`, `render_profile_job`), purkaa parametrit ja delegoi työn.
* **Rajoitus:** Ei koske tietokantaan, ei tiedä mitään dollareista tai tokeneista. Hoitaa vain infran ja retry-mekanismit, jos työ epäonnistuu.

### B. `CostCalculator` (Puhdas Matematiikka)
* **Vastuu:** Puhdas matemaattinen moottori. Saa sisäänsä `TokenUsage`-olioita ja vanhan `ExecutionRecordin` metadatan, ja palauttaa uuden kumulatiivisen `total_cost_usd`-arvon ja token-summat.
* **Rajoitus:** Ei koskaan kutsu tietokantaa (repositorya). Se on 100 % deterministinen yksikkötestattava funktio.

### C. `ExecutionLifecycle` (Tilan ja Tietokannan hallinta)
* **Vastuu:** Vastaa `ExecutionRecord`:in koko elinkaaresta. Tämä luokka sisältää metodit kuten `mark_execution_running()`, `save_dag_results()`, `finalize_synthesis()` ja `fail_execution()`.
* **Hyöty:** Kun orkestraattori tarvitsee tallentaa tuloksia, se kutsuu vain `lifecycle.save_dag_results(exec_id, results, costs)`, ja tämä luokka hoitaa oikeat Pydantic-validoinnit ja tietokantakutsut. Tämä estää sen, että yksittäisiä tärkeitä kenttiä (kuten `cost_estimate`) unohdetaan vahingossa päivityksen ulkopuolelle.

### D. `WebhookNotifier` (Ulkoiset integraatiot)
* **Vastuu:** Eristetään raskaat verkko-operaatiot (Webhook-lähetykset, HTTP POST -kutsut asiakkaan järjestelmiin) omaan tiedostoonsa.

## 4. Toteutuksen Askelmerkit (Phased Approach)

Tämä on massiivinen leikkaus järjestelmän sydämeen. Se on tehtävä vaiheittain The Universal Quality Gaten alaisuudessa:

1. **Vaihe 1: Matemaattinen eristäminen (Pienin riski)**
   * Luodaan `CostCalculator`.
   * Siirretään rivit 840–880 (`worker.py`:n token- ja hintalaskenta) tänne.
   * Ajetaan testit.

2. **Vaihe 2: Webhookien siirto**
   * Siirretään `_send_webhook_if_configured` ja kaikki siihen liittyvä logiikka `WebhookNotifieriin`.

3. **Vaihe 3: Elinkaariluokan luominen**
   * Luodaan `ExecutionLifecycle`.
   * Siirretään suorat `repository.update_execution` -kutsut tähän luokkaan. Refaktoroidaan `worker.py` käyttämään uusia puhtaita metodeja.

4. **Vaihe 4: Siivous**
   * Jäljelle jäänyt `worker.py` on nyt pelkkä `JobQueueManager`.

## 5. Hyväksymiskriteerit ja Laatuportit
* **Riski:** Taustatyöt menevät jumiin Redis-jonoon tai ajojen tila jää "running"-tilaan, jos Lifecycle-luokka ei päivitä kantaa oikein.
* **Laatuportti:** Kaikki muutokset auditoidaan tiukasti `scripts/backend_audit_loop.py backend_v2 --test` -komennolla. Yhtäkään integraatiotestiä ei saa poistaa; niiden on mentävä läpi uutta arkkitehtuuria käyttäen. `worker.py`:n rivimäärä on laskenut alle 300:n.
