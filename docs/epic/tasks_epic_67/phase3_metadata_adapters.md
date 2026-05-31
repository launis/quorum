# Implementation Plan: Phase 3 - Anthropic Claude ja OpenAI/DeepSeek -sovittimet (Metadata Caching)

Tämä yksityiskohtainen toteutussuunnitelma kattaa Epic 67:n alavaiheen **Phase 4**. Se toteuttaa metadata-pohjaiset välimuistisovittimet `AnthropicCacheAdapter` ja `OpenAICacheAdapter` ja eristää tarjoajakohtaisen viestimuotoilu- ja ROI-hinnoittelulogiikan ydinkoodista.

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
| **[anthropic_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/anthropic_adapter.py)** | **[NEW]** Caching-sovitin Anthropic-malleille | `base_adapter.py` |
| **[openai_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/openai_adapter.py)** | **[NEW]** Caching-sovitin OpenAI/DeepSeek-malleille | `base_adapter.py` |
| **[test_metadata_adapters.py](file:///c:/src/quorum/backend_v2/tests/unit/test_metadata_adapters.py)** | **[NEW]** Yksikkötestit ja hintalaskelmien tarkkuustodisteet | `anthropic_adapter.py`, `openai_adapter.py` |

---

## 3. Yksityiskohtaiset suoritukset ja virstanpylväät (Milestones)

### Milestone 3.1: `AnthropicCacheAdapter` toteutus
- **Source**: *Epic Section 3.2.1, Step 3 (Anthropic)*
- **Sijainti**: `backend_v2/llm/adapters/anthropic_adapter.py`
- **Sisältö**:
  Toteutetaan Anthropic-sovitin, joka noudattaa tarkasti seuraavia sääntöjä:
  1. **Tägien sijainti ja alternoivien roolien säilyminen**:
     - Anthropic ei tue `cache_control`-tägiä viestiobjektin juuressa. Sisältö lohkoina: `{"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}}`.
     - Jotta API-rakenne pysyy ehjänä ja roolit (user/assistant) vaihtuvat oikein, adapteri ryhmittelee viestit:
       * Kaikki `role == "system"` yhdistetään yhdeksi system-lohkojoukoksi, jonka loppuun asetetaan ensimmäinen `cache_control` -tägi.
       * Kaikki `role == "user" / "assistant"` few-shot esimerkit ja conversation säilytetään omissa alternoivissa viesteissään. Toinen `cache_control` -tägi sijoitetaan **ainoastaan staattisen viestilistan absoluuttisen viimeisen viestin viimeiseen lohkoon**. Tämä poistaa fragmentoitumisen, varmistaa 100 % prefix-osumisen ja estää skeemavirheet.
  2. **Kynnysarvo**: Välimuistisovitin aktivoidaan vain, jos staattisten viestien merkkimäärä on >= 4 000 merkkiä (vastaa 1024 tokenia). Jos pituus alittuu, palautetaan viestit sellaisenaan ilman tägejä.
  3. **Aktiivinen siivous (Teardown)**: No-Op (`pass`).
  4. **FinOps Cost & ROI-laskenta**:
     - Clauden kirjoitus (Cache Write) maksaa **+25 %** normaalia input-hintaa enemmän.
     - Clauden luku (Cache Read / Hit) on **-90 %** halvempaa.
     - Toteutetaan matemaattinen kaava dynaamisten pricing kertoimien kanssa:
       $$\text{Cost} = (\text{input\_tokens} \times P_{\text{in}}) + (\text{cache\_creation\_input\_tokens} \times P_{\text{in}} \times 1.25) + (\text{cached\_tokens} \times P_{\text{in}} \times 0.10) + (\text{output\_tokens} \times P_{\text{out}})$$
       $$\text{Savings} = (\text{cached\_tokens} \times P_{\text{in}} \times 0.90) - (\text{cache\_creation\_input\_tokens} \times P_{\text{in}} \times 0.25)$$

### Milestone 3.2: `OpenAICacheAdapter` toteutus
- **Source**: *Epic Section 3.2.1, Step 3 (OpenAI)*
- **Sijainti**: `backend_v2/llm/adapters/openai_adapter.py`
- **Sisältö**:
  Toteutetaan OpenAI/DeepSeek-sovitin:
  1. **prepare_caching_payload**: OpenAI ja DeepSeek tunnistavat välimuistin automaattisesti etuliitteestä. Palautetaan litteät viestit (`CompiledPrompt.to_flat_messages()`) ja tyhjät `extra_kwargs`.
  2. **Aktiivinen siivous (Teardown)**: No-Op (`pass`).
  3. **FinOps Cost & ROI-laskenta**:
     - OpenAI lukualennus (Cache Read / Hit) on **-50 %**. DeepSeek lukualennus on **-90 %** (tunnistetaan mallinimestä).
     - Toteutetaan kaava (OpenAI):
       $$\text{Cost} = (\text{input\_tokens} \times P_{\text{in}}) + (\text{cached\_tokens} \times P_{\text{in}} \times 0.50) + (\text{output\_tokens} \times P_{\text{out}})$$
       $$\text{Savings} = \text{cached\_tokens} \times P_{\text{in}} \times 0.50$$

### Milestone 3.3: Hintamatematiikan ja tägien tarkkuustesti
- **Source**: *Epic Phase 4, Step 2*
- **Sijainti**: `backend_v2/tests/unit/test_metadata_adapters.py`
- **Sisältö**:
  Kirjoitetaan kattavat yksikkötestit:
  1. Varmistetaan `AnthropicCacheAdapter` tuottavan tasan 2 `cache_control` -tägiä ja sijoittavan ne oikeisiin paikkoihin (system ja viimeisen staattisen viestin loppuun).
  2. Varmistetaan, ettei tyhjiä tai liian pieniä syötteitä (< 4000 merkkiä) tägätä.
  3. **Laskentatarkkuustodiste**: Testataan hintamatematiikka ja ROI-laskelma kymmenellä eri token- ja hintaskenaariolla (mukaan lukien erittäin suuret syötteet ja vaihtelevat hintakertoimet), todentaen, että hinta täsmää pilkulleen matemaattisiin kaavoihin ja säästö lasketaan oikein.

---

## 4. Quality Gate & Verification Plan

### Automated Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/anthropic_adapter.py backend_v2/llm/adapters/openai_adapter.py tests/unit/test_metadata_adapters.py --test
```

---

## 5. Session Handover
Tämä päättää kolmannen vaiheen. Tee atominen git-commit suhteellisilla tiedostopoluilla:
```powershell
git add backend_v2/llm/adapters/anthropic_adapter.py backend_v2/llm/adapters/openai_adapter.py tests/unit/test_metadata_adapters.py
git commit -m "feat: implement Anthropic Claude and OpenAI adapters with structural block mapping, ephemeral cache control tagging, and exact FinOps ROI calculations"
```
Jatka suoritusta lataamalla seuraava vaihe: `/tier5-resume --target docs/epic/tasks_epic_67/phase4_vertex_adapter.md`
