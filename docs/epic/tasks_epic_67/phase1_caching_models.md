# Implementation Plan: Phase 1 - Tyyppimääritelmät (`CompiledPrompt`) ja Kääntäjän Adapteri (`PromptCompilerAdapter`)

Tämä yksityiskohtainen toteutussuunnitelma kattaa Epic 67:n alavaiheet **Phase 1** ja **Phase 2**. Se määrittelee staattisesti erotellun viestitietorakenteen `CompiledPrompt` sekä siihen liittyvän kääntäjän sovittimen `PromptCompilerAdapter`, joka pitää ydinjärjestelmän `prompt_compiler.py` tiedoston 100 % jäädytettynä ja koskemattomana.

---

## 1. Yleiset arkkitehtoniset määräykset (General Mandates)

Toteutuksessa on noudatettava tiukasti seuraavia `c:\src\quorum\.agents\rules\` -sääntöjä ja yleisiä määräyksiä:

1. **the_zero_compromise_pledge** (`00-antigravity-core.md`): Taaksepäinyhteensopivuus, fallback-ketjut ("jos A puuttuu, kokeile B"), oikotiet ja ohjelmointikielen oletusarvot (esim. `v.get('kenttä', '')`) ovat ankarasti kiellettyjä. Jos odotettu avain tai tieto puuttuu (kuten Micro-CoT -jälki), järjestelmän on kaaduttava kuuluvasti (`AppException` tai `RuntimeError`). `hasattr()`, `isinstance(dict)` tai rekursiiviset dict-silmukat datan etsimiseen ovat kiellettyjä.
2. **universal_fail_fast** (`00-antigravity-core.md`): Jos data ei täsmää Pydantic V2 -skeemaan tai Dart Freezed -skeemaan, järjestelmän on kaaduttava heti ja annettava poikkeus.
3. **atomic_checkpoint_mandate** (`00-antigravity-core.md`): Jokaisen onnistuneen askeleen jälkeen käyttäjää pyydetään tekemään atominen `git commit` suhteellisilla tiedostopoluilla (NEVER `git add .`) ja englanninkielisellä commit-viestillä.
4. **tdd_mandate** (`00-antigravity-core.md`): Virhettä tai ominaisuutta ei saa koodata ennen kuin sille on kirjoitettu epäonnistuva testi (`failing test`), joka toistaa tilanteen.
5. **mocking_mandate_for_llm** (`00-antigravity-core.md`): Testeissä ei saa tehdä suoria HTTP-kutsuja LLM-tarjoajille. On käytettävä `backend_v2/llm/mock.py`- ja `mock_data.py`-infrastruktuuria.
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
| **[prompt.py](file:///c:/src/quorum/backend_v2/models/prompt.py)** | **[NEW]** Tietomalli segmentoidulle promptille | Ei riippuvuuksia |
| **[prompt_compiler_adapter.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler_adapter.py)** | **[NEW]** Adapteri litteiden viestien pilkkomiseen | `prompt_compiler.py` (Read-only) |
| **[test_prompt_caching_models.py](file:///c:/src/quorum/backend_v2/tests/unit/test_prompt_caching_models.py)** | **[NEW]** Yksikkötestit ja deterministisyystodisteet | `prompt.py`, `prompt_compiler_adapter.py` |

---

## 3. Yksityiskohtaiset suoritukset ja virstanpylväät (Milestones)

### Milestone 1.1: `CompiledPrompt` -tietomallin luonti
- **Source**: *Epic Phase 1, Step 1*
- **Sijainti**: `backend_v2/models/prompt.py`
- **Sisältö**:
  Toteutetaan Pydantic V2 -malli, joka erottaa täysin staattisen ja dynaamisen osion.
  ```python
  from typing import Any
  from pydantic import BaseModel, ConfigDict, Field

  class CompiledPrompt(BaseModel):
      """Strictly typed representation of compiled LLM prompt parts to support Context Caching."""

      static_messages: list[dict[str, Any]] = Field(
          ...,
          description="100% static system instructions, static few-shot examples, and unchanging schemas."
      )
      dynamic_messages: list[dict[str, Any]] = Field(
          ...,
          description="Dynamic execution parameters, Trace IDs, and user/assistant dynamic tail conversation."
      )

      model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

      def to_flat_messages(self) -> list[dict[str, Any]]:
          """Flattens both parts into a single list of messages for backward-compatibility with LiteLLM."""
          return self.static_messages + self.dynamic_messages
  ```

### Milestone 1.2: `PromptCompilerAdapter` -luokan luonti
- **Source**: *Epic Phase 1, Step 2 & Phase 2, Step 1*
- **Sijainti**: `backend_v2/services/orchestrator/prompt_compiler_adapter.py`
- **Sisältö**:
  Luodaan adapteriluokka, joka käärii alkuperäisen `PromptCompiler` kutsut.
  - Alkuperäinen `prompt_compiler.py` tuodaan laiskasti metodin sisällä tai alustetaan.
  - Metodi `compile_prompt` ottaa vastaan litteän viestijonon tai kriteerit ja erottaa viestit kahteen segmenttiin:
    1. **`static_messages`**: Viestit, joissa `role == "system"` tai few-shot esimerkit, jotka eivät sisällä muuttuvaa ajonaikaista dataa (kuten aikaleimoja tai Trace ID:tä). Staattinen aineisto ladataan viestiketjun **alkuun**.
    2. **`dynamic_messages`**: Viestit, jotka sisältävät dynaamista suoritusaikaista dataa (esim. `dynamic_instructions`, trace ID:t, aikaleimat). Kaikki dynaamiset parametrit ohjataan XML-tagiin `<execution_parameters>` tämän listan loppuun.
  - Adapteri varmistaa, että kaikki dynamic parametrit, trace ID:t ja aikarajat on sijoitettu tiukasti listan loppuun (Static First, Dynamic Last).

### Milestone 1.3: Kryptografinen deterministisyystesti
- **Source**: *Epic Phase 2, Step 2*
- **Sijainti**: `backend_v2/tests/unit/test_prompt_caching_models.py`
- **Sisältö**:
  Kirjoitetaan kattavat yksikkötestit varmistamaan:
  1. `CompiledPrompt` pystyy luomaan molemmat segmentit ja `.to_flat_messages()` yhdistää ne deterministisesti.
  2. `PromptCompilerAdapter` erottelee staattisen ja dynaamisen osan aukottomasti.
  3. **Deterministisyystodiste**: Testataan, että kun dynaamisia muuttujia (kuten trace_id, timestamp, execution_time) muutetaan 10 eri skenaariossa, `static_messages`-lohkon SHA-256 -kryptografinen tiiviste pysyy 100 % identtisenä!
     ```python
     import hashlib
     import json
     # Varmistetaan lajittelu
     static_hash_1 = hashlib.sha256(json.dumps(prompt1.static_messages, sort_keys=True).encode()).hexdigest()
     static_hash_2 = hashlib.sha256(json.dumps(prompt2.static_messages, sort_keys=True).encode()).hexdigest()
     assert static_hash_1 == static_hash_2
     ```

---

## 4. Quality Gate & Verification Plan

### Automated Tests
Suoritetaan backend-auditointi ja testit:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/prompt.py backend_v2/services/orchestrator/prompt_compiler_adapter.py tests/unit/test_prompt_caching_models.py --test
```

### Manual Verification
- Varmistetaan, ettei `prompt_compiler.py`-tiedostoon ole koskettu.

---

## 5. Session Handover
Tämä päättää ensimmäisen vaiheen. Tee atominen git-commit suhteellisilla tiedostopoluilla:
```powershell
git add backend_v2/models/prompt.py backend_v2/services/orchestrator/prompt_compiler_adapter.py tests/unit/test_prompt_caching_models.py
git commit -m "feat: implement CompiledPrompt models and PromptCompilerAdapter for strict static-dynamic prompt segregation"
```
Jatka suoritusta lataamalla seuraava vaihe: `/tier5-resume --target docs/epic/tasks_epic_67/phase2_adapter_factory.md`
