# EPIC: LLM Rate Limiting & Concurrency Safety

## 1. Yhteenveto (Summary)
Työnkulkumoottori (`DAGExecutor`) käynnistää askeleet rinnakkain `asyncio.gather`-kutsulla. Jos 10 askeleen LLM-solmua aktivoidaan samanaikaisesti ja ne vaativat raskasta mallia (esim. Gemini Pro), ne iskevät API-rajapintaan täsmälleen samalla millisekunnilla. Koska `system_config` määrittelee raskaiden mallien kapasiteetiksi esim. `rpm_limit: 2` (Requests Per Minute), API hylkää 8 pyyntöä asettamalla niille `429 Too Many Requests` tai `Quota Exceeded` -virheen. Tästä seuraa Fail-Fast -mandaatin mukaisesti koko työnkulun kaatuminen.

## 2. Tavoitteet (Objectives)
- **Token Bucket Rate Limiter:** Toteuttaa `LLMClient`-tasolla asynkroninen jonotusmekanismi, joka rajoittaa tietyn strategian (`strategy`) pyyntötiheyden `rpm_limit` ja `tpm_limit` -arvojen ramin puitteisiin.
- **429 Backoff Self-Healing:** Lisätä LLMClienttiin kyky tunnistaa ohimenevä 429-virhe ja kokeilla pyyntöä uudelleen viiveellä (Exponential Backoff), ennen kuin virhe eskaloidaan DAG-tasolle.

## 3. Vaiheet (Execution Plan)

### Vaihe 1: Global Limiter Registry
- **Toimenpide:** Luodaan uusi `backend_v2/llm/rate_limit.py`, johon ohjelmoidaan Singleton-pohjainen `TokenBucketLimiter` tai hyödynnetään `aiolimiter`-kirjastoa. Sen pitää säilyttää tila globaalisti muistissa per strategia (esim. `"strict": AsyncLimiter(2, 60)`).

### Vaihe 2: LLMClient.from_strategy päivitys
- **Toimenpide:** Vaiheessa, missä Pydantic-konfiguraatio ladatun `rpm_limit` arvon parsaa (esim. 2 tai 15), se injektoidaan heti globaaliin Limiter-rekisteriin suojaksi.

### Vaihe 3: Provider Generate Wrap (Jonotus)
- **Toimenpide:** Muutetaan `run_structured_task` ja `run_chat` -funktioita siten, että `provider.generate()` -verkkokutsu on kääritty `async with limiter:` -blokin sisään. Tämä muuttaa 10 yhtäaikaista pyyntöä kiltiksi jonoksi.

### Vaihe 4: Resilienssin parannus (Exponential Backoff)
- **Toimenpide:** Lisätään `run_structured_task` -looppiin `except Exception as e:` -kohtaan tunnistus 429-statukselle (Too Many Requests / Quota). Tällöin koodi tekee `await asyncio.sleep(10)` ja yrittää uudelleen, säästäen järjestelmän kaatumiselta.

---
*Integroituu täydellisesti V2.9 LLMClient ja Fail-Fast arkkitehtuurien väliin varmistamassa toimintavarmuutta raskaassa kuormassa.*
