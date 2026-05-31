# Implementation Plan: Phase 2 - Rajapinta, Tehdas ja Mock-infrastruktuuri (Core & Mock Adapter)

Tämä yksityiskohtainen toteutussuunnitelma kattaa Epic 67:n alavaiheen **Phase 3**. Se määrittelee tarjoajariippumattoman välimuistisovittimen abstraktin kantaluokan `BaseLLMAdapter`, sovittimen latauksesta vastaavan tehdasluokan `LLMCacheAdapterFactory` sekä verkkokutsuvapaan testauksen mahdollistavan `MockCacheAdapter`-luokan.

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
| **[base_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/base_adapter.py)** | **[NEW]** Abstrakti kantaluokka adapterille | `prompt.py`, `usage.py` (Read-only) |
| **[adapter_factory.py](file:///c:/src/quorum/backend_v2/llm/adapters/adapter_factory.py)** | **[NEW]** Sovitinlataaja tehdasluokkana | `base_adapter.py` |
| **[mock_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/mock_adapter.py)** | **[NEW]** Verkkokutsuvapaa testaussovitin | `base_adapter.py` |
| **[test_cache_adapter_factory.py](file:///c:/src/quorum/backend_v2/tests/unit/test_cache_adapter_factory.py)** | **[NEW]** Yksikkötestit ja laiskuustodisteet | `adapter_factory.py`, `mock_adapter.py` |

---

## 3. Yksityiskohtaiset suoritukset ja virstanpylväät (Milestones)

### Milestone 2.1: Abstraktin `BaseLLMAdapter` luonti
- **Source**: *Epic Phase 3, Step 1*
- **Sijainti**: `backend_v2/llm/adapters/base_adapter.py`
- **Sisältö**:
  Määritellään abstrakti kantaluokka (`BaseLLMAdapter`), joka asettaa tiukan, yhteisen ja tarjoajariippumattoman rajapinnan kaikille välimuisti- ja hinnoittelusovittimille.
  ```python
  from abc import ABC, abstractmethod
  from typing import Any
  from backend_v2.models.prompt import CompiledPrompt
  from backend_v2.models.domain.usage import TokenUsage

  class BaseLLMAdapter(ABC):
      """Abstract base class defining the strict interface for caching and pricing adapters."""

      @abstractmethod
      async def prepare_caching_payload(
          self, 
          compiled_prompt: CompiledPrompt,
          model_name: str
      ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
          """Palauttaa muokatut viestit ja tarjoajakohtaiset lisäparametrit."""
          pass

      @abstractmethod
      async def teardown_cache(self, workflow_run_id: str) -> None:
          """Purkaa luodut tilalliset resurssit (Vertex) tai suorittaa No-Op (Anthropic/OpenAI) Option B mukaisesti."""
          pass

      @abstractmethod
      def calculate_cost(
          self, 
          usage: TokenUsage,
          pricing_config: dict[str, Any]
      ) -> TokenUsage:
          """Laskee tarkan hinnan ja ROI:n tarjoajan omilla matemaattisilla kertoimilla."""
          pass
  ```

### Milestone 2.2: Tehdasluokan `LLMCacheAdapterFactory` toteutus
- **Source**: *Epic Phase 3, Step 2*
- **Sijainti**: `backend_v2/llm/adapters/adapter_factory.py`
- **Sisältö**:
  Toteutetaan tehdasluokka, joka palauttaa dynaamisesti oikean sovittimen perustuen mallirekisterin tarjoajanimeen (`provider_name`).
  - **Laiskan latauksen mandaatti (Lazy Loading)**: Raskaat ML-kirjastotuonnit (kuten `vertexai` tai `anthropic`) on sijoitettava *ainoastaan* asynkronisten metodien sisään (Lazy Loading) testien ja boot-vaiheen PyO3-monialustaturvallisuuden vuoksi.
  - Tehdas tukee arvoja: `"vertex_ai"`, `"anthropic"`, `"openai"`, `"deepseek"` ja `"mock_llm_99"`.

### Milestone 2.3: `MockCacheAdapter` luonti testejä varten
- **Source**: *Epic Phase 3, Step 3*
- **Sijainti**: `backend_v2/llm/adapters/mock_adapter.py`
- **Sisältö**:
  Luodaan mockattava adapteri yksikkö- ja integraatiotestausta varten:
  - `prepare_caching_payload` palauttaa viestit sellaisenaan ja asettaa `extra_kwargs` kenttään `"mock_cache_active": True`.
  - `teardown_cache` suorittaa No-Op (`pass`).
  - `calculate_cost` palauttaa TokenUsage-olion sellaisenaan ja asettaa säästöksi (`estimated_savings_usd`) kiinteän 0.05 USD laskentatestien varmentamiseksi.

### Milestone 2.4: Laiskuuden ja eheyden yksikkötestit
- **Source**: *Epic Phase 3, Step 4*
- **Sijainti**: `backend_v2/tests/unit/test_cache_adapter_factory.py`
- **Sisältö**:
  Kirjoitetaan yksikkötestit:
  1. Varmistetaan, että tehdas palauttaa oikean sovittimen ja heittää poikkeuksen tuntemattomalla toimijalla.
  2. **Lazy Import -todiste**: Testataan, ettei yhtäkään raskasta ML-kirjastoa (kuten `google-genai` tai `litellm` tai `anthropic`) ladata Pythonin muistiin (`sys.modules`) pelkän adapteritehtaan tai `MockCacheAdapter`-luokan suorassa tuonnissa.
  3. Varmistetaan `MockCacheAdapter`-matematiikan ja ROI-laskennan 100 % oikeellisuus.

---

## 4. Quality Gate & Verification Plan

### Automated Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/base_adapter.py backend_v2/llm/adapters/adapter_factory.py backend_v2/llm/adapters/mock_adapter.py tests/unit/test_cache_adapter_factory.py --test
```

---

## 5. Session Handover
Tämä päättää toisen vaiheen. Tee atominen git-commit suhteellisilla tiedostopoluilla:
```powershell
git add backend_v2/llm/adapters/base_adapter.py backend_v2/llm/adapters/adapter_factory.py backend_v2/llm/adapters/mock_adapter.py tests/unit/test_cache_adapter_factory.py
git commit -m "feat: implement abstract BaseLLMAdapter, LLMCacheAdapterFactory, and MockCacheAdapter for robust provider-agnostic caching decoupling"
```
Jatka suoritusta lataamalla seuraava vaihe: `/tier5-resume --target docs/epic/tasks_epic_67/phase3_metadata_adapters.md`
