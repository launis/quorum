# EPIC: ChunkWorker Refactoring - God Method Decomposition

## Tausta ja Konteksti
`ChunkWorker`-luokka ja sen ydinmetodi `process_chunk` vastaavat järjestelmän kriittisimmästä osasta: LLM-kutsujen,MCP-työkalujen, determinististen sensorien (Pre-flight) ja Map-Merge-orkestroinnin suorittamisesta.
Tällä hetkellä `process_chunk` on kasvanut massiiviseksi "God Methodiksi" (> 500 riviä), jolla on yli 20 parametria. Tämä rikkoo The Universal Quality Gaten periaatteita vaikeuttamalla testausta (Mocking Hell) ja koodin luettavuutta.

**Juurisyy-analyysi (Kesäkuu 2026 Double Negation -bugi):**
Tämä vastuiden sekoittuminen johti konkreettiseen katastrofaaliseen virheeseen, jossa koodi käänsi "FAIL" -tulokset "PASS" -tuloksiksi. Syynä oli se, että sama tiedosto yritti sekä louhia dataa (fyysiset lainaukset) että tulkita monimutkaista liiketoimintalogiikkaa (käänteissäännöt, inverse_evidence). Tämän vuoksi SRP:n noudattaminen on nyt kriittistä.

## Tavoite
Purkaa `process_chunk` selkeisiin, yksittäisen vastuun (Single Responsibility Principle) komponentteihin käyttäen Parameter Object ja Pipeline -suunnittelumalleja. `ChunkWorker` muunnetaan puhtaaksi Pipeline-orkestraattoriksi, joka delegoi raskaat työvaiheet erikoistuneille apuluokille.

## Suunnitellut Arkkitehtuurimuutokset
Kaikki uudet komponentit sijoitetaan hakemistoon: `backend_v2/services/orchestrator/strategies/llm_execution/`

### 1. Tilanhallinnan keskittäminen (`chunk_dto.py`)
- **Ongelma:** `process_chunk` vastaanottaa nykyisin jopa 20 erillistä parametria.
- **Ratkaisu:** Luodaan `ChunkExecutionContext(BaseModel)` Pydantic-tietomalli, johon koko orkestroinnin tila (chunk, criteria_blocks, user_payload jne.) pakataan.
- **Mukana siirrettävät rakenteet:** Pienemmät apurakenteet kuten `AtomIdentifier`, `ConsensusVotePayload` ja `SduiResponseList`.

### 2. Pre-flight ja Chunk-suodatus (`chunk_pre_flight.py`)
- **Ongelma:** Deterministisen sensorin (ExtractiveSensorService) ja atomeiden suodatuksen logiikka on upotettu pääfunktion alkuun.
- **Ratkaisu:** Eristetään `extract_and_filter_atoms` -funktio, joka ottaa vastaan `ChunkExecutionContext`-olion ja palauttaa suodatetun chunkin, ennalta ratkaistut `pre_flight_results`-tiedot sekä Pydanticin validoimat `atoms_xml` -määrittelyt.

### 3. LLM TaskGroup Moniajo (`chunk_executor.py`)
- **Ongelma:** Pääfunktiossa pyöritetään massiivista `asyncio.TaskGroup` -häkkiä ja otetaan kiinni `ExceptionGroup` -poikkeuksia.
- **Ratkaisu:** Eristetään moniajo ja säikeiden tilanhallinta (`AgentExecutionError`/`ExceptionGroup`) omaan `chunk_executor.py` -luokkaansa, joka vastaanottaa dynaamisen skeiman ja promptin ja palauttaa pelkät LLM-raakatulokset.

### 4. Map-Merge ja Sääntömoottori (`chunk_map_merge.py` & `chunk_rules.py`)
- **Ongelma:** LLM-tuloksien evaluointi (`evaluate_extraction`, `resolve_majority_vote`) sekä determinististen `pre_flight_results` -tuloksien "injektointi" takaisin sanakirjoihin muodostavat vaikeasti testattavan kokonaisuuden. Liiketoimintasääntöjen (kuten käänteisten sääntöjen) tulkinta on ollut vaarallisesti sekoittuneena tiedonlouhintaan (Double Negation -bugi).
- **Ratkaisu:** Eristetään puhdas matemaattinen sääntömoottori (`RuleEvaluator` / `ConsensusEngine`), joka käsittelee liiketoimintalogiikan (esim. `inverse_evidence = True`) täysin erillään tekoälyn toiminnasta. Tämän lisäksi eristetään `ExtractionValidator` -turvaportti ja `merge_hybrid_results` -funktio, joka osaa suoraan yhdistää eri lähteistä tulevan Pydantic-datan tehden niille loppuvalidoinnin dynaamista skeemaa vasten, palauttaen turvallisen JSON/Pydantic-tuloksen.

### 5. Pipeline-orkestraattori (`chunk_worker.py`)
- **Ongelma:** Vaikeasti luettava logiikkaviidakko.
- **Ratkaisu:** Muutetaan `ChunkWorker` tiiviiksi Pipeline-ohjaimeksi, joka näyttää suunnilleen tältä:
  1. `context = ChunkExecutionContext(...)`
  2. `pf_chunk, pf_results, atoms = pre_flight.filter(context)`
  3. `schema, prompt = compiler.compile(context, pf_chunk)`
  4. `llm_raw_results = await executor.run_ensemble(context, prompt, schema)`
  5. `final_output = map_merge.merge(llm_raw_results, pf_results, schema)`

## Hyväksymiskriteerit
1. `chunk_worker.py`:n `process_chunk` -metodi on kutistettu alle 50 riviin pelkkää pipeline-ohjausta.
2. Kaikki alkuperäiset integraatio- ja yksikkötestit (`test_worker_dlq.py`, `test_chunk_worker_validation.py`) menevät läpi.
3. Koko projektin laatuportti (`backend_audit_loop.py`) näyttää vihreää (Pydantic-malleja ja tyyppivihjeitä noudatettu).
