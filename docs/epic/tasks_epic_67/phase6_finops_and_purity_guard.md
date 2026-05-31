# Implementation Plan: Phase 6 - Moniulotteinen FinOps-seuranta, ROI-laskenta ja Purity-valvonta

Tämä yksityiskohtainen toteutussuunnitelma kattaa Epic 67:n alavaiheet **Phase 9** ja **Phase 10**. Se päivittää Pydantic V2 -tietomallit moniulotteiseen seurantamuotoon, laajentaa `UsageService`-palvelua tarkan ROI-hinnoittelumatematiikan laskemiseksi ja ottaa käyttöön ajonaikaisen asynkronisen `Purity Scanner` -valvonnan sekä `PROMPT_CACHING_DRIFT_ALERT`-hälytyksen.

---

## 1. Yleiset arkkitehtoniset määräykset (General Mandates)

Toteutuksessa on noudatettava tiukasti seuraavia `c:\src\quorum\.agents\rules\` -sääntöjä ja yleisiä määräyksiä:

1. **the_zero_compromise_pledge** (`00-antigravity-core.md`): Taaksepäinyhteensopivuus, fallback-ketjut ("jos A puuttuu, kokeile B"), oikotiet ja ohjelmointikielen oletusarvot (esim. `v.get('kenttä', '')`) ovat ankarasti kiellettyjä. Jos odotettu avain tai tieto puuttuu (kuten Micro-CoT -jälki), järjestelmän on kaaduttava kuuluvasti (`AppException` tai `RuntimeError`). `hasattr()`, `isinstance(dict)` tai rekursiiviset dict-silmukat datan etsimiseen ovat kiellettyjä.
2. **universal_fail_fast** (`00-antigravity-core.md`): Jos data ei täsmää Pydantic V2 -skeemaan tai Dart Freezed -skeemaan, järjestelmän on kaaduttava heti ja annettava poikkeus.
3. **atomic_checkpoint_mandate** (`00-antigravity-core.md`): Jokaisen onnistuneen askeleen jälkeen käyttäjää pyydetään tekemään atominen `git commit` suhteellisilla tiedostopoluilla (NEVER `git add .`) ja englanninkielisellä commit-viestillä.
4. **tdd_mandate** (`00-antigravity-core.md`): Virhettä tai ominaisuutta ei saa koodata ennen kuin sille on kirjoitettu epäonnistuva testi (`failing test`), joka toistaa tilanteen.
5. **mocking_mandate_for_llm** (`00-antigravity-core.md`): Testeissä ei saa tehdä suoria HTTP-kutsuja LLM-tarjoajille. On käytettävä `backend_v2/llm/mock.py`- ja `mock_data.py`-infrastruktuuria. Live LLM -kutsut ovat ankarasti kiellettyjä nopeuden ja FinOps-kustannusten vuoksi.
6. **circuit_breaker_protocol** (`00-antigravity-core.md`): Jos testi tai suoritus epäonnistuu 3 kertaa peräkkäin, AI:n on pysähdyttävä, tulostettava `<circuit_breaker_tripped>` and odotettava ohjeita.
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
| **[enums.py](file:///c:/src/quorum/backend_v2/models/enums.py)** | **[MODIFY]** Uusien caching-enumien lisäykset | Ei riippuvuuksia |
| **[usage.py](file:///c:/src/quorum/backend_v2/models/domain/usage.py)** | **[MODIFY]** Moniulotteinen `TokenUsage` -tietomalli | Ei riippuvuuksia |
| **[usage_service.py](file:///c:/src/quorum/backend_v2/services/usage_service.py)** | **[MODIFY]** ROI-matematiikka ja `Drift Alert` -kytkentä | `usage.py`, `adapter_factory.py` |
| **[test_finops_telemetry.py](file:///c:/src/quorum/backend_v2/tests/unit/test_finops_telemetry.py)** | **[NEW]** Yksikkötestit ja purity/drift-todisteet | `usage_service.py`, `usage.py` |
| **[EPIC_67_caching_architecture.md](file:///c:/src/quorum/docs/architecture/EPIC_67_caching_architecture.md)** | **[NEW]** Arkkitehtoniset välimuistitiedot ja kaavat | Ei riippuvuuksia |

---

## 3. Yksityiskohtaiset suoritukset ja virstanpylväät (Milestones)

### Milestone 6.1: `enums.py` -päivitys
- **Source**: *Epic Section 2.3, strict_enum_mandate_for_critical_values*
- **Sijainti**: `backend_v2/models/enums.py`
- **Sisältö**:
  Määritellään ja lisätään uudet tyypitetyt välimuistienumit ilman raakoja merkkijonoliteraaleja (No-String Mandate):
  - `LLMCachingStrategy(str, Enum)`: `"prompt_caching"`, `"ephemeral"`, `"anthropic_ephemeral"`, `"gemini_native"`, `"none"`
  - `LLMProviderName(str, Enum)`: `"vertex_ai"`, `"anthropic"`, `"openai"`, `"deepseek"`
  - `PromptCacheStatus(str, Enum)`: `"CREATING"`, `"CREATED"`, `"FAILED"`
  - Lisätään `SystemConcurrency`-enumille uudet välimuistiparametrit:
    * `CONTEXT_CACHE_LOCK_TTL_SECONDS = 300`
    * `CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS = 500`
    * `CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS = 20`
    * `CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600`

### Milestone 6.2: Moniulotteinen `TokenUsage` -tietomalli
- **Source**: *Epic Section 3.7.1*
- **Sijainti**: `backend_v2/models/domain/usage.py`
- **Sisältö**:
  Uudistetaan `TokenUsage`-tietomalli ottamaan huomioon välimuistin moniulotteisuus (strict, extra='forbid'):
  ```python
  class TokenUsage(BaseModel):
      prompt_tokens: int = Field(default=0)  # Input-tokenit
      completion_tokens: int = Field(default=0)  # Output-tokenit
      cached_tokens: int = Field(default=0)  # Välimuistista luetut tokenit (Read / Hit / Cached)
      cache_creation_input_tokens: int = Field(default=0)  # Välimuistiin kirjoitetut tokenit (Cache Write / Miss)
      cost_usd: float = Field(default=0.0)  # Toteutunut kokonaiskustannus (USD)
      estimated_savings_usd: float = Field(default=0.0)  # Säästetty rahasumma (ROI)
      reasoning_tokens: int = Field(default=0)  # Mallin omat ajattelutokenit
  ```

### Milestone 6.3: `UsageService` hinnanlaskennan abstrahointi ja `Drift Alert` -kuluhälytys
- **Source**: *Epic Section 3.2.2 & 3.6.3*
- **Sijainti**: `backend_v2/services/usage_service.py`
- **Sisältö**:
  1. **Hinnoitteludelegointi**: Kutsuttaessa `track_usage` otetaan vastaan uudet kentät `cache_creation_input_tokens` ja `estimated_savings_usd`. Lasketaan hinta sokeasti oikealle adapterille:
     ```python
     adapter = LLMCacheAdapterFactory.get_adapter(provider_name)
     final_usage = adapter.calculate_cost(usage, model_pricing_config)
     ```
  2. **PROMPT_CACHING_DRIFT_ALERT**:
     Toteutetaan osumatarkkuuden alittumisen tarkistus. Mikäli suoritusympäristössä on käytössä `"prompt_caching"`, mutta viiden viimeisimmän suorituksen keskimääräinen välimuistiin osumisaste (Cache Hit Rate: `cached_tokens` / `total_tokens`) tippuu **alle 80 %**, järjestelmä lokittaa kriittisen virheen:
     `logger.error("PROMPT_CACHING_DRIFT_ALERT: Cache hit rate has degraded to X% for workflow Y. Investigate prompt mutations immediately.")`

### Milestone 6.4: Ajonaikainen `Purity Scanner` järjestelmädirektiiveille
- **Source**: *Epic Section 3.6.1*
- **Sijainti**: `backend_v2/llm/caching_service.py` / `prepare_caching_payload`
- **Sisältö**:
  Toteutetaan kevyt asynkroninen regex-skannaus **ainoastaan järjestelmäviesteille** (`role == "system"`).
  - **Sääntö**: Laajoja massadokumentteja (`role == "user" / <source_data>`) ei koskaan skannata event loopin lukkiutumisen (Event Loop blocking) ja väärien hälytysten välttämiseksi.
  - Skanneri etsii dynaamisia UUID/Timestamp-kuvioita ja jos ne löytyvät, se lokittaa varoituksen:
    `logger.warning("PROMPT_CACHING_PURITY_VIOLATION: Dynamic trace/timestamp pattern detected in static system instruction block. Cache hit rate will drop to 0%!")`
  - Skanneri toimii ainoastaan passiivisena valvontana (observability) eikä koskaan estä tai kaada suoritusta (Fail-Soft).

### Milestone 6.5: FinOps- ja Purity-testit
- **Source**: *Epic Phase 9 & 10*
- **Sijainti**: `backend_v2/tests/unit/test_finops_telemetry.py`
- **Sisältö**:
  Kirjoitetaan yksikkötestit:
  1. Testataan `TokenUsage` V2 strict -toteutuksen ja matemaattisen `__add__`-operaattorin oikeellisuus uusilla seurantakentillä.
  2. Testataan `UsageService` delegoivan hintalaskennan ja ROI:n oikein `MockCacheAdapter`-luokalle.
  3. Testataan ajonaikainen `Purity Scanner` injektoimalla dynaamisia UUID/Timestamp-kuvioita lyhyeen järjestelmäviestiin (role == "system") ja todennetaan `PROMPT_CACHING_PURITY_VIOLATION` -varoituslokin syntyminen.
  4. Testataan `PROMPT_CACHING_DRIFT_ALERT`-kuluhälytyksen laukeaminen, kun osumatarkkuus laskee 5 peräkkäisessä kutsussa alle 80 % kynnyksen.

---

## 4. Quality Gate & Verification Plan

### Automated Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/models/domain/usage.py backend_v2/services/usage_service.py tests/unit/test_finops_telemetry.py --test
```

### Database Reset & Re-seeding
Koska legacymallien taaksepäinyhteensopivuus katkaistaan arkkitehtuurin puhtauden vuoksi (Clean-Slate), alustetaan tietokanta ja seedataan dynaamisen mallirekisterin caching-parametrit:
```powershell
uv run python scripts/run_seed.py
```

---

## 5. Session Handover
Tämä päättää viimeisen vaiheen. Tee atominen git-commit suhteellisilla tiedostopoluilla:
```powershell
git add backend_v2/models/enums.py backend_v2/models/domain/usage.py backend_v2/services/usage_service.py tests/unit/test_finops_telemetry.py docs/architecture/EPIC_67_caching_architecture.md
git commit -m "feat: implement multi-dimensional FinOps tracking, adapter-based ROI calculations, runtime purity guards, and cache drift alerts"
```
Jatka suoritusta lataamalla seuraava vaihe: `/tier5-resume --target docs/epic/EPIC_67_tracker.md`
