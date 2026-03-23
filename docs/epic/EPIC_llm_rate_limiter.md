# EPIC: LLM Rate Limiting & Concurrency Safety

## 1. Yhteenveto (Summary)
Työnkulkumoottori (`DAGExecutor`) käynnistää askeleet rinnakkain `asyncio.gather`-kutsulla. Jos 10 askeleen LLM-solmua aktivoidaan samanaikaisesti ja ne vaativat raskasta mallia (esim. Gemini Pro), ne iskevät API-rajapintaan täsmälleen samalla millisekunnilla. Koska `system_config` määrittelee raskaiden mallien kapasiteetiksi esim. `rpm_limit: 2` (Requests Per Minute), API hylkää 8 pyyntöä asettamalla niille `429 Too Many Requests` tai `Quota Exceeded` -virheen. Tästä seuraa Fail-Fast -mandaatin mukaisesti koko työnkulun kaatuminen.

## 2. Tavoitteet (Objectives)
- **Hajautettu Token Bucket Rate Limiter (Redis):** Toteuttaa `LLMClient`-tasolla asynkroninen jonotusmekanismi hyödyntäen hajautettua (distributed) välimuistia (Redis). Rajoitin kontrolloi tietyn strategian (`strategy`) pyyntötiheyttä `rpm_limit` ja dynaamisen `tpm_limit` -laskennan puitteissa tuotannollisessa moni-worker -ympäristössä.
- **429 Jitter Backoff & Self-Healing:** Lisätä LLMClienttiin kyky tunnistaa satunnainen 429-virhe ja kokeilla pyyntöä uudelleen satunnaistetulla viiveellä (Exponential Backoff + Jitter) ehkäisten samanaikaisia virtapiikkejä (Thundering Herd).

## 3. Vaiheet (Execution Plan)

### Vaihe 1: Hajautettu Limiter Registry (Redis)
- **Toimenpide:** Luodaan uusi `backend_v2/llm/rate_limit.py`, johon ohjelmoidaan Redis-pohjainen (esim. olemassa olevaa `redis_patcher.py` -infrastruktuuria hyödyntävä) Token Bucket. In-memory `aiolimiter` -kirjastoa ei käytetä, koska se ei skaalaudu horisontaalisesti usean workerin tai kontin (Cloud Run / GKE) varaan. Tila jaetaan kaikkien ajojen kesken per strategia (`strategy_name`).

### Vaihe 2: TPM- ja RPM-laskennan päivitys (`LLMClient`)
- **Toimenpide (RPM):** Pydantic-konfiguraation `rpm_limit` viedään suoraan Rediksen Token Bucketiin RPM-hallintaa varten.
- **Toimenpide (TPM):** Täsmennetään `tpm_limit` -logiikka: pyyntövaiheessa "ämpäristä" vähennetään karkea arvio tokeneista (esim. historiallinen keskiarvo pituuden pohjalta), ja varsinaisen LLM-vastauksen jälkeen token-ämpäriin palautetaan tai siitä poistetaan erotus tarkkojen toteutuneiden `usage`-tietojen perusteella.

### Vaihe 3: Aikakatkaisut (Timeouts) ja Provider Wrap
- **Toimenpide:** Muutetaan asynkronisia `run_structured_task` -kutsuja siten, että ne odottavat lukkoa (esim. `async with limiter:`).
- **Turvaverkko:** Jäätyneiden pyyntöjen ehkäisemiseksi jonottamiselle asetetaan ehdoton aikaraja (esim. `max_wait_time=60`). Jos pyyntö on jumissa yli tämän ajan, nostetaan `RateLimitTimeoutException` -virhe. Tämä estää koko API-kutsun jäätymisen jopa minuuteiksi ja 504 Gateway Timeout -verkkotilanteet.

### Vaihe 4: Resilienssin parannus (Exponential Backoff + Jitter)
- **Toimenpide:** Lisätään päälooppiin tunnistus 429-statukselle (Quota Exceeded). Tämä ei kaada suoritusta, vaan siirtää ohjelman odotustilaan.
- **Jitter-algoritmi:** Pelkän tasaisen odotuksen (`asyncio.sleep(10)`) sijaan koodiin lisätään "Jitter" eli pieni satunnaisviive (esim. `sleep(10 + random(0.0, 1.0))`). Tämä estää ns. Thundering Herd -ilmiön, jossa kaikki samaan aikaan 429-virheen saaneet solmut heräävät kokeilemaan uudelleen täsmälleen samalla millisekunnilla kaataen rajapinnan jälleen.

### Vaihe 5: Laadunvarmistus (QA), Kuormitustestaus ja Telemetria
- **Load Testing:** Rakennetaan simuloitu testi (Mock LLM), jolle asetetaan keinotekoinen 2 RPM katto. Ajetaan työnkulkua 20 rinnakkaisella askeleella ja todennetaan, että liikenne asettuu jonoon turvallisesti ja vain ylimenevät joutuvat Jitter Backoff -käsittelyyn kaatamatta koko DAGia.
- **Telemetria:** Konfiguroidaan `logger` kirjaamaan jonotusajat, `RateLimitTimeoutException` -katkaisut sekä 429-uudelleenyritykset suoraan `backend_debug.log` -tietueeseen helpottamaan tuotannollisen kapasiteetin monitorointia.

---
*Integroituu täydellisesti V2.9 LLMClient ja Fail-Fast arkkitehtuurien väliin varmistamassa toimintavarmuutta ja horisontaalista skaalautuvuutta raskaassa pilvikuormassa.*
