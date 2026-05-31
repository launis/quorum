# Implementation Plan: Phase 5 - LiteLLMProvider, Caching Service ja Task Executor -integraatio

Tämä yksityiskohtainen toteutussuunnitelma kattaa Epic 67:n alavaiheet **Phase 7** ja **Phase 8**. Se integroi sovittimet osaksi ydinjärjestelmän asynkronista suoritusputkea ottamalla käyttöön julkisivupohjaisen `LLMCachingService`-palvelun ja yhdistämällä sen `LiteLLMProvider`- ja `LLMTaskExecutor`-luokkiin.

---

## 1. Yleiset arkkitehtoniset määräykset (General Mandates)

Toteutuksessa on noudatettava tiukasti seuraavia `c:\src\quorum\.agents\rules\` -sääntöjä ja yleisiä määräyksiä:

1. **the_zero_compromise_pledge** (`00-antigravity-core.md`): Taaksepäinyhteensopivuus, fallback-ketjut ("jos A puuttuu, kokeile B"), oikotiet ja ohjelmointikielen oletusarvot (esim. `v.get('kenttä', '')`) ovat ankarasti kiellettyjä. Jos odotettu avain tai tieto puuttuu (kuten Micro-CoT -jälki), järjestelmän on kaaduttava kuuluvasti (`AppException` tai `RuntimeError`). `hasattr()`, `isinstance(dict)` tai rekursiiviset dict-silmukat datan etsimiseen ovat kiellettyjä.
2. **universal_fail_fast** (`00-antigravity-core.md`): Jos data ei täsmää Pydantic V2 -skeemaan tai Dart Freezed -skeemaan, järjestelmän on kaaduttava heti ja annettava poikkeus.
3. **atomic_checkpoint_mandate** (`00-antigravity-core.md`): Jokaisen onnistuneen askeleen jälkeen käyttäjää pyydetään tekemään atominen `git commit` suhteellisilla tiedostopoluilla (NEVER `git add .`) ja englanninkielisellä commit-viestillä.
4. **tdd_mandate** (`00-antigravity-core.md`): Virhettä tai ominaisuutta ei saa koodata ennen kuin sille on kirjoitettu epäonnistuva testi (`failing test`), joka toistaa tilanteen.
5. **mocking_mandate_for_llm** (`00-antigravity-core.md`): Testeissä ei saa tehdä suoria HTTP-kutsuja LLM-tarjoajille. On käytettävä `backend_v2/llm/mock.py`- ja `mock_data.py`-infrastruktuuria. Live LLM -kutsut ovat ankarasti kiellettyjä nopeuden ja FinOps-kustannusten vuoksi.
6. **circuit_breaker_protocol** (`00-antigravity-core.md`): Jos testi tai suoritus epäonnistuu 3 kertaa peräkkäin, AI:n on pysähdyttävä, tulostettava `<circuit_breaker_tripped>` ja odotettava ohjeita.
7. **silent_failures** (`01-python-backend.md`): Poikkeuksia ei saa koskaan niellä hiljaa (`except: pass`). Ne on ALWAYS logitettava (`logger.error`) ja heitettävä edelleen tai käsiteltävä asiallisesti `AppException`-oliona (RFC 7807).
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
| **[caching_service.py](file:///c:/src/quorum/backend_v2/llm/caching_service.py)** | **[NEW]** Tarjoaja-agnostinen Facade caching-ydintoiminnoille | `adapter_factory.py`, `prompt.py` |
| **[provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py)** | **[MODIFY]** LiteLLMProvider-sovitus completion-kutsuihin | `caching_service.py` |
| **[llm_task_executor.py](file:///c:/src/quorum/backend_v2/services/llm_task_executor.py)** | **[MODIFY]** Task Executorin kytkentä ja Self-Healing eheyttäminen | `prompt_compiler_adapter.py`, `caching_service.py` |
| **[test_caching_integration.py](file:///c:/src/quorum/backend_v2/tests/integration/test_caching_integration.py)** | **[NEW]** Integraatiotestaussarja suorituspoluille | `llm_task_executor.py`, `caching_service.py` |

---

## 3. Yksityiskohtaiset suoritukset ja virstanpylväät (Milestones)

### Milestone 5.1: `LLMCachingService`-julkisivun luonti
- **Source**: *Epic Section 3.2.2*
- **Sijainti**: `backend_v2/llm/caching_service.py`
- **Sisältö**:
  Toteutetaan tarjoaja-agnostinen julkisivupalvelu (Facade), joka ei sisällä lainkaan tarjoajakohtaisia `if-else` -laustehimmeleitä (Zero If-Statement Principle).
  - Se delegoi pyynnöt dynaamisesti ja sokeasti oikealle adapterille tehdasluokan `LLMCacheAdapterFactory` kautta.
  - Sisältää asynkroniset metodit:
    * `prepare_caching_payload`: Hakee sovittimen, valmistelee pyyntökuorman ja palauttaa muokatut viestit ja `extra_kwargs`.
    * `teardown_workflow_caches`: Suorittaa asynkronisen roskienkeruun delegoidusti (Vertexille ja Anthropicille/OpenAI:lle No-Op `pass`).

### Milestone 5.2: `LiteLLMProvider` -päivitys
- **Source**: *Epic Phase 7, Step 1*
- **Sijainti**: `backend_v2/llm/provider.py`
- **Sisältö**:
  Päivitetään `LiteLLMProvider` asettamaan adapterin palauttamat parametrit completion-kutsuun:
  - `generate`-metodi ottaa vastaan asynkronisesti valmistellun välimuistipyyntökuorman (`messages` ja `extra_kwargs`).
  - Jos `extra_kwargs` sisältää `cached_content` (Gemini), se siirretään suoraan `litellm.completion`-kutsulle osana `extra_headers` tai mallikohtaisia lisäparametreja.
  - Jos kyseessä on Anthropic, `cache_control` -tägit on jo valmiiksi sijoitettu `messages` -lohkoihin, ja ne välittyvät automaattisesti.

### Milestone 5.3: `LLMTaskExecutor` refaktorointi ja itseparannuksen eheyttäminen
- **Source**: *Epic Section 2.4, Contradiction 2*
- **Sijainti**: `backend_v2/services/llm_task_executor.py`
- **Sisältö**:
  Refaktoroidaan `execute_structured_task` käsittelemään `CompiledPrompt`-malleja ja kytketään se `PromptCompilerAdapter` -luokkaan.
  - **Itseparannuksen (Self-Healing) eheyttäminen**: Mikäli syntyy `LLMSchemaValidationError` tai `LogicalValidationError`, korjaava virhe-prompti injektoidaan **ainoastaan `CompiledPrompt.dynamic_messages`-segmentin absoluuttiseen loppuun**. Tämä pitää `static_messages` (ja sen SHA-256 -hasheksen) 100 % puhtaana, jolloin välimuistin osumatarkkuus ei nollaudu itseparannusyrityksillä!
  - Suorituksen päätteeksi kutsutaan asynkronista caching facade siivousta turvallisessa `finally`-lohkossa.

### Milestone 5.4: Integraatiotestaussarja
- **Source**: *Epic Phase 8, Step 2*
- **Sijainti**: `backend_v2/tests/integration/test_caching_integration.py`
- **Sisältö**:
  Kirjoitetaan integraatiotestit:
  1. `LLMTaskExecutor` suorittaa strukturoidun kutsun onnistuneesti `MockCacheAdapter`-sovittimen kanssa.
  2. Varmistetaan, että itseparannuskierroksilla (Self-Healing) virheellisen tuloksen injektio ei muuta promptin staattisen osan SHA-256-tiivistettä.
  3. **Fail-Soft integraatiotodiste**: Testataan vikaeheyttäminen: kun `VertexCacheAdapter` epäonnistuu mockatussa verkkokutsussa, järjestelmä suorittaa askeleen onnistuneesti loppuun tekemällä perinteisen ei-välimuistitetun API-kutsun.

---

## 4. Quality Gate & Verification Plan

### Automated Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/llm/caching_service.py backend_v2/llm/provider.py backend_v2/services/llm_task_executor.py tests/integration/test_caching_integration.py --test
```

---

## 5. Session Handover
Tämä päättää viidennen vaiheen. Tee atominen git-commit suhteellisilla tiedostopoluilla:
```powershell
git add backend_v2/llm/caching_service.py backend_v2/llm/provider.py backend_v2/services/llm_task_executor.py tests/integration/test_caching_integration.py
git commit -m "feat: integrate caching service and compiler adapter into task executor with strict self-healing static-purity preservation"
```
Jatka suoritusta lataamalla seuraava vaihe: `/tier5-resume --target docs/epic/tasks_epic_67/phase6_finops_and_purity_guard.md`
