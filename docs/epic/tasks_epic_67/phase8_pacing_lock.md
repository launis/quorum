# Epic: Provider-Scoped LLM Pacing (Rate Limit Hardening)

Tämä Epic korjaa Quorumin asynkronisen LLM-kutsulogiikan sokean pisteen koskien palveluntarjoajakohtaisia RPM (Requests Per Minute) -rajoja. Vaikka nykyinen `SystemConcurrency.MAX_CONCURRENT_LLM_STEPS = 2` estää samanaikaiset piikit, se ei estä salamannopeiden kutsujen pinoitumista. Googlen 5 RPM -raja kaataa järjestelmän alle 10 sekunnissa raskailla kuormilla.

Ratkaisuna rakennamme **Provider-Scoped Redis Pacing Lockin**, joka pakottaa mallikohtaiset turvavälit (esim. 12 sekuntia Vertex AI:lle, 0 sekuntia OpenAI/Mock -malleille) ennen API-kutsua. Tämä mekanismi hajautetaan turvallisesti Adapter-kerrokseen.

## User Review Required

> [!WARNING]
> **Arkkitehtuurinen Sijoituspaikka**
> Suunnitelmassa ehdotetaan uuden `acquire_pacing_lock()` -funktion injektointia `BaseLLMAdapter`-luokkaan (tai `provider.py` -tasolle juuri ennen adapterin kutsua). Onko tämä hyväksyttävä kerros asynkronisen Wait & Poll -silmukan sijoittamiselle, jotta DAG-moottori itse pysyy LLM-agnostisena?

## Open Questions

> [!IMPORTANT]
> **Odotusajan Maksimikatto (Timeout)**
> Jos Vertex AI:lle ammutaan 10 pyyntöä, joilla kaikilla on pakotettu 12 sekunnin jono, kymmenes pyyntö joutuu odottamaan yli 2 minuuttia saadakseen lukon. Tuleeko `SystemConcurrency.LLM_DEFAULT_TIMEOUT_SECONDS` -arvoa kasvattaa varmuuden vuoksi, vai riittääkö nykyinen 600 sekunnin (10 min) timeout?

## Proposed Changes

---

### Enums & Konfiguraatiot

Lisätään mallikohtaiset tahtisäätimet (Pacing) suoraan `SystemConcurrency` -kokonaisuuteen.

#### [MODIFY] `backend_v2/models/enums.py`
- **Uudet arvot `SystemConcurrency` -enumiin:**
  - `PACING_DELAY_VERTEX_SECONDS = 12` (Takaa maks. 5 RPM ja estää 429-väsymyksen Googlen rajapinnassa).
  - `PACING_DELAY_OPENAI_SECONDS = 0` (OpenAI:n korkeat limiitit sallivat vapaan tulituksen).
  - `PACING_DELAY_MOCK_SECONDS = 0` (Yksikkötestien viiveet pidetään nollassa).

---

### Backend: Pacing-logiikan toteutus (Redis)

Kierrätetään ja laajennetaan nykyistä Thundering Herd -lukon logiikkaa luomalla mallikohtainen tahdistin.

#### [NEW / MODIFY] `backend_v2/llm/adapters/base_adapter.py` (tai vastaava apukirjasto)
- **Uusi funktio: `apply_provider_pacing(provider_name: str)`**
  - Hakee `provider_name`:n perusteella `SystemConcurrency`:stä oikean viiveen (esim. Vertex = 12s).
  - Jos viive on 0, palauttaa välittömästi (Fast-Path).
  - Jos viive > 0, siirtyy Redis-lukon hankintaan:
    1. Yrittää luoda avaimen `lock:pacer:{provider_name}` komennolla `SETNX`, ja asettaa TTL:ksi (Expiration) kyseisen viiveen (12s).
    2. Jos asetus onnistuu (`lock_acquired == True`), asynkroninen funktio päästää prosessin jatkamaan API-kutsun tekoon. **HUOM:** Lukkoa *ei* poisteta API-kutsun jälkeen.
    3. Jos asetus epäonnistuu, worker siirtyy Wait & Poll -silmukkaan, yrittäen napata lukon uudelleen puolen sekunnin välein, kunnes vanha lukko raukeaa.

#### [MODIFY] `backend_v2/llm/provider.py`
- **Injektio:** Ennen kuin varsinainen LiteLLM-kysely suoritetaan reitittimessä, suoritetaan `await apply_provider_pacing(provider_name)`.
- Tämä pakottaa DAG-moottorin odottamaan kiltisti vuoroaan ennen kuin fyysinen API-kutsu poistuu palvelimelta, maksimoiden nopeuden rikkomatta RPM-rajaa.

---

## Verification Plan

### Automated Tests
- Päivitetään `test_system_concurrency_compliance.py` sisältämään `PACING_DELAY_*` -arvojen eheyden tarkistus (Mock ja OpenAI oltava 0).
- Luodaan yksikkötesti `apply_provider_pacing` -funktiolle FakeRedis-altaalla, joka simuloi 3 rinnakkaista Vertex-kutsua ja varmistaa, että niiden suoritusajat porrastuvat asetetun viiveen mukaisesti.

### Manual Verification
- Aseta `PACING_DELAY_VERTEX_SECONDS` arvoon 5 sekuntia paikallisessa ympäristössä.
- Aja suuri Sitra-testikeissi `run_local.bat` -komennolla.
- Seuraa `backend_debug.log` -tiedostoa: sinun pitäisi nähdä "Wait-and-Poll: Pacing lock active for vertex_ai..." -ilmoituksia, ja onnistuneiden LLM-kutsujen tulisi tapahtua säännöllisesti 5 sekunnin välein ilman ainoatakaan 429 Exponential Backoff -virhettä.
