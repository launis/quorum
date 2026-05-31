# Implementation Plan: Phase 4 - Vertex AI -sovitin, Redis-lukitus ja Thundering Herd -ryntäyssuojaus

Tämä yksityiskohtainen toteutussuunnitelma kattaa Epic 67:n alavaiheet **Phase 5** ja **Phase 6**. Se toteuttaa eksplisiittisen pilvivälimuistin hallinnan Google Vertex AI:lle, kapseloi raskaat GCP-API-kutsut ja suojaa järjestelmän rinnakkaisten työnkulkujen ryntäysilmiöltä (Thundering Herd) hajautetulla Redis-lukituksella ja dynaamisella Wait & Poll -odotussilmukalla.

---

## 1. Yleiset arkkitehtoniset määräykset (General Mandates)

Toteutuksessa on noudatettava tiukasti seuraavia `c:\src\quorum\.agents\rules\` -sääntöjä ja yleisiä määräyksiä:

1. **the_zero_compromise_pledge** (`00-antigravity-core.md`): Taaksepäinyhteensopivuus, fallback-ketjut ("jos A puuttuu, kokeile B"), oikotiet ja ohjelmointikielen oletusarvot (esim. `v.get('kenttä', '')`) ovat ankarasti kiellettyjä. Jos odotettu avain tai tieto puuttuu (kuten Micro-CoT -jälki), järjestelmän on kaaduttava kuuluvasti (`AppException` tai `RuntimeError`). `hasattr()`, `isinstance(dict)` tai rekursiiviset dict-silmukat datan etsimiseen ovat kiellettyjä.
2. **universal_fail_fast** (`00-antigravity-core.md`): Jos data ei täsmää Pydantic V2 -skeemaan tai Dart Freezed -skeemaan, järjestelmän on kaaduttava heti ja annettava poikkeus.
3. **atomic_checkpoint_mandate** (`00-antigravity-core.md`): Jokaisen onnistuneen askeleen jälkeen käyttäjää pyydetään tekemään atominen `git commit` suhteellisilla tiedostopoluilla (NEVER `git add .`) ja englanninkielisellä commit-viestillä.
4. **tdd_mandate** (`00-antigravity-core.md`): Virhettä tai ominaisuutta ei saa koodata ennen kuin sille on kirjoitettu epäonnistuva testi (`failing test`), joka toistaa tilanteen.
5. **mocking_mandate_for_llm** (`00-antigravity-core.md`): Testeissä ei saa tehdä suoria HTTP-kutsuja LLM-tarjoajille. On käytettävä `backend_v2/llm/mock.py`- ja `mock_data.py`-infrastruktuuria. Live LLM -kutsut ovat ankarasti kiellettyjä nopeuden ja FinOps-kustannusten vuoksi.
6. **circuit_breaker_protocol** (`00-antigravity-core.md`): Jos testi tai suoritus epäonnistuu 3 kertaa peräkkäin, AI:n on pysähdyttävä, tulostettava `<circuit_breaker_tripped>` ja odotettava ohjeita.
7. **silent_failures** (`01-python-backend.md`): Poikkeuksia ei saa koskaan niellä hiljaa (`except: pass`). Ne on aina logitettava (`logger.error`) ja heitettävä edelleen tai käsiteltävä asiallisesti `AppException`-oliona (RFC 7807).
8. **blocking_the_fastapi_thread** (`01-python-backend.md`): Pitkäkestoiset AI-sukellukset tai DAG-ajot (>500ms) on ajettava asynkronisessa Arq-työjonossa, ja API:n on palautettava heti 202 Accepted TaskID:n kanssa.
9. **security_logging_ban** (`01-python-backend.md`): Lokitiedostoihin ei saa koskaan kirjoittaa PII-tietoja, asiakasprompteja tai salaisuuksia (API-avaimia, JWT). Vain matemaattinen/looginen syy ja Opaque ID (esim. req_abc123) lokitetaan.
10. **strict_pydantic_v2_rust** (`01-python-backend.md`): Pydantic-mallien luomiseen käytetään Rust-pohjaista `.model_validate()` tai `.model_validate_json()` -metodia. `model_config = ConfigDict(extra='forbid', strict=True)` on pakollinen ydinmalleilla.
11. **no_naked_dicts_in_state** (`01-python-backend.md`): Kaikki datavirrat on heti rajalla validoitava Pydantic-malliksi. Naked dicts -rakennetta ei saa käyttää tilansiirrossa.
12. **no_inline_imports** (`01-python-backend.md`): Kaikki normaalit tuonnit tehdään tiedoston alussa. Poikkeuksena raskaat ML-kirjastot (`litellm`, `vertexai`, `google-genai`, `tokenizers`), jotka on tuotava metodien sisällä (Lazy Loading) PyO3-virheiden ja kylmäkäynnistysviiveiden estämiseksi.
13. **prompt_compiler_immutability** (`01-python-backend.md`): Alkuperäinen `prompt_compiler.py` on arkkitehtonisesti pyhä eikä siihen saa koskea. Kaikki muutokset on toteutettava adapterilla.
14. **the_no_legacy_mandate** (`01-python-backend.md`): Vanhoja asioita ei saa tukea (Clean-Slate). Jos tietokantaschema muuttuu, kanta seedataan uudestaan (`run_seed.py`), eikä legacy-kenttien fallback-hakkauksia sallita.
15. **system_concurrency_ssot** (`05_llm_architecture.md`): Parallel limits ja aikarajat on haettava tiukasti `SystemConcurrency`-enumista.

---

## 2. Kohdetiedostot (Target Files)

| Tiedosto | Rooli | Riippuvuus |
| :--- | :--- | :--- |
| **[vertex_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/vertex_adapter.py)** | **[NEW]** Caching-sovitin Vertex AI:lle Redis-lukolla | `base_adapter.py`, `enums.py` (Read-only) |
| **[test_vertex_adapter.py](file:///c:/src/quorum/backend_v2/tests/unit/test_vertex_adapter.py)** | **[NEW]** Lukitus-, Thundering Herd - ja Fail-Soft -testit | `vertex_adapter.py` |

---

## 3. Yksityiskohtaiset suoritukset ja virstanpylväät (Milestones)

### Milestone 4.1: `VertexCacheAdapter` toteutus ja kynnystunnistus
- **Source**: *Epic Section 3.2.1, Step 3 (Vertex)*
- **Sijainti**: `backend_v2/llm/adapters/vertex_adapter.py`
- **Sisältö**:
  Toteutetaan Vertex AI Context Caching -sovitsin:
  - **Laiskat SDK-tuonnit**: `import google.cloud.aiplatform` ja muut GCP AI platform SDK -tuonnit on sijoitettava tiukasti metodien sisään (Lazy Loading).
  - **Kynnystunnistus**: Arvioidaan static messages -pituus nopealla $O(1)$-merkkipituustarkistuksella. Kynnysarvo on **130 000 merkkiä** (vastaa 32 768 tokenin minimikokoa pilvessä). Jos pituus on alle 130 000 merkkiä, välimuistia ei yritetä luoda (caching bypassed) ja suoritus ohjataan standardinaCompletion-kutsuna (tyhjät `extra_kwargs`), mikä estää Vertex AI API:n kovat `400 Bad Request` -rajarikko-virheet.

### Milestone 4.2: Redis-ryntäyssuojalukitus (Thundering Herd Protection)
- **Source**: *Epic Section 3.3.1*
- **Sijainti**: `backend_v2/llm/adapters/vertex_adapter.py`
- **Sisältö**:
  Toteutetaan ryntäyssuoja rinnakkaisille työkuluille:
  1. **Deterministinen avain**: Lasketaan `SHA-256` staattisista viesteistä (`CompiledPrompt.static_messages`) ja mallin nimestä (`model_name`) varmistaen case-sensitive mallieristys (estää tyyppivirheet Geminissä). Kaava: `hashlib.sha256(json.dumps(static_messages, sort_keys=True).encode()).hexdigest()`. Redis-avain on `vertex_cache:{model_name}:{static_hash}`.
  2. Tarkistetaan Redis-avain: Jos Cache Resource ID löytyy, palautetaan se.
  3. **Hajautetun lukon hankinta (`SETNX`)**:
     - Lukkoavain `lock:vertex_cache:{model_name}:{static_hash}` asetetaan atomisesti: `SET lock:vertex_cache:{model_name}:{static_hash} worker_id NX PX 300000` (lukko `SystemConcurrency.CONTEXT_CACHE_LOCK_TTL_SECONDS` sekunnin / 300s TTL:llä).
     - **Lukko saatu (1. worker)**:
       - Luodaan Vertex AI Context Cache GCP SDK -kutsulla. Passiivinen TTL asetetaan **60 minuuttiin** (`SystemConcurrency.CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600`).
       - **Zero-Compromise Fail-Soft -vikaeheyttäminen**: Kaikki GCP API Context Cache -luontivirheet kääritään `try-except Exception:` -lohkoon, nielaistaan (nolla vaikutusta ydinjärjestelmään), logitetaan lyhyt varoitus (`logger.warning`) ja kirjoitetaan Redisiin avaimelle arvo `"FAILED"` 5 minuutin (300s) TTL:llä (estää turhat uudet kalliit API-kutsut samalla aineistolla). Luodusta virheestä huolimatta adapteri palauttaa normaalincompletion-kutsun heti.
       - **Lukon vapautus (`finally`)**: Lukkoavain poistetaan Redistä aina `finally`-lohkossa.
     - **Lukkoa ei saatu (Muut workerit)**:
       - Siirrytään asynkroniseen **Wait & Poll** -odotussilmukkaan.
       - Kysellään Redisistä avainta `vertex_cache:{model_name}:{static_hash}` 500ms (`SystemConcurrency.CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS`) välein.
       - **Instant Exit**: Jos avaimesta löytyy arvo `"FAILED"`, säikeet poistuvat silmukasta heti ja jatkavat standardiincompletion-pyyntöön!
       - Odotetaan enintään 20 sekuntia (`SystemConcurrency.CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS`). Jos raja ylittyy tai Redis kaatuu, ohjataan pyyntö perinteisenä completion-kutsuna (Fail-Soft).

### Milestone 4.3: Option B mukainen passiivinen siivous (Teardown Bypass)
- **Source**: *Epic Section 3.4.1*
- **Sijainti**: `backend_v2/llm/adapters/vertex_adapter.py`
- **Sisältö**:
  **Option B - Pure Passive TTL Caching**: `teardown_cache`-metodi toteutetaan pelkkänä asynkronisena No-Op -lausekkeena (`pass`).
  - Mitään välimuistiresurssia ei koskaan tuhota aktiivisesti kesken muiden peräkkäisten tai rinnakkaisten ajojen, mikä eliminoi downstreameja kaatavat `404 Not Found` -kilpailutilanteet 100 % varmuudella.
  - Pilvisiivoamisesta vastaa Vertexin oma 60 minuutin passiivinen TTL, jota jokainen lukutapahtuma (Cache Hit) pidentää automaattisesti 60 minuutilla eteenpäin pilvessä.

### Milestone 4.4: Concurrency- ja Fail-Soft -yksikkötestit
- **Source**: *Epic Phase 6, Step 2*
- **Sijainti**: `backend_v2/tests/unit/test_vertex_adapter.py`
- **Sisältö**:
  Kirjoitetaan kattavat yksikkötestit:
  1. Testataan `VertexCacheAdapter` pituuskynnykset ja deterministiset SHA-256 avaimet.
  2. **Thundering Herd Testi**: Käynnistetään rinnakkain 5 mock-työntekijää, ja todennetaan, että vain 1 varaa lukon ja tekee API-luontikutsun, muiden siirtyessä odotussilmukkaan.
  3. **Instant Exit Testi**: Todennetaan odottavien säikeiden välitön poistuminen silmukasta, kun Redisiin palautuu `"FAILED"` arvo.
  4. Testataan vikasietoinen Fail-Soft -polku mockatuilla GCP-virheillä.
  5. Varmistetaan `teardown_cache` No-Op toiminta.

---

## 4. Quality Gate & Verification Plan

### Automated Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/vertex_adapter.py tests/unit/test_vertex_adapter.py --test
```

---

## 5. Session Handover
Tämä päättää neljännen vaiheen. Tee atominen git-commit suhteellisilla tiedostopoluilla:
```powershell
git add backend_v2/llm/adapters/vertex_adapter.py tests/unit/test_vertex_adapter.py
git commit -m "feat: implement Vertex AI caching adapter with distributed Redis locks, thundering herd protection, and option B passive teardown"
```
Jatka suoritusta lataamalla seuraava vaihe: `/tier5-resume --target docs/epic/tasks_epic_67/phase5_provider_executor_integration.md`
