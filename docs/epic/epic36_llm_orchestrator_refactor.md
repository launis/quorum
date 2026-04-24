# Epic 36: LLM Orchestrator Structural Refactoring (Facade Pattern)

## Objective
Purkaa ~500-rivinen `LLMNodeStrategy.execute()` ("God Method") selkeiksi, yhden vastuun luokiksi (Single Responsibility Principle) uuteen alihakemistoon, jättäen alkuperäisen luokan ohueksi työnjohtajaksi (Coordinator).

Mitään liiketoimintalogiikkaa tai tietovirtaa ei muuteta; kaikki olemassa olevat Epic 35:n ja Epic 32:n säännöt (Feature Sovereignty, Duct-Tape Ban) säilyvät 100% muuttumattomina.

## Phase 1: Context Builder & Prompt Factory
Luodaan ensimmäiset apuluokat, jotka irrottavat datan valmistelun varsinaisesta LLM-suorituksesta.

- **[NEW] `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`**: 
  Vastaa `input_mappings` -sanakirjan purkamisesta, `resolve_dot_notation` -kutsuista, ContextRouterin integroinnista ja Token-rajoitusten (100k) valvonnasta. Tuottaa valmiin `llm_context_data` -sanakirjan tekoälylle.
  
- **[NEW] `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`**: 
  Kutsuu olemassa olevaa `PromptCompileria`. Rakentaa `dynamic_schema`, `xml_ctx` (dokumentit), staattiset ohjeet sekä Blind Evaluation -säännöt. Tuottaa paketin (PromptPayload), joka sisältää valmiin järjestelmäpromptin ja Pydantic-skeeman LLM:ää varten.

## Phase 2: Chunk Worker (Map-Reduce Engine)
Siirretään raskain logiikka – asynkroninen palojen prosessointi – omaan tiedostoonsa.

- **[NEW] `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`**: 
  Korvaa `llm.py`:n sisällä olleen massiivisen `process_chunk` -alifunktion.
  - Hakee Semantic Cachesta mahdollisen osuman.
  - Kokoaa lopulliset viestit (System Prompt + User Data).
  - Tekee fyysisen `litellm.acompletion` -kutsun.
  - Rakentaa MCP Audit Trace -raportit ja purkaa JSON-vastauksen Pydanticilla.
  - Palauttaa tuple-muodossa `(c_final, c_usage, c_traces)`.

## Phase 3: The Facade (Koordinaattorin kasaus)
Siivotaan alkuperäinen tiedosto käyttämään luotuja apuluokkia.

- **[MODIFY] `backend_v2/services/orchestrator/strategies/llm.py`**:
  - Poistetaan yli 300 riviä sisäkkäistä koodia (indentation hell).
  - Muutetaan `execute`-metodi puhtaaksi koordinaattoriksi. Seuraa logiikkaa: Rakenna Konteksti -> Chunkkaa -> Rinnakkaisajo (TaskGroup + ChunkWorker) -> Yhdistä (ChunkAccumulator) -> Post-Hooks.
