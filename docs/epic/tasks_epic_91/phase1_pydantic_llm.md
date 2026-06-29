# Phase 1: LLM Prompt & Pydantic-skeeman uudistus

**Source:** Epic 91, Task 1.1 - 1.4
**Context Rules Injected:** 01-python-backend.md (Zero-Compromise Pydantic V2), 00-antigravity-core.md (No-String Mandate, Primitive Obsession)
**Hardening Rules:** Enforce strict Pydantic V2 definitions. No loose dictionaries.

## TARGET (Modify)
- `backend_v2/models/prompts/field_prompts.py`
- `backend_v2/models/dtos/lightweight_matrix.py`
- `backend_v2/models/v2_core.py`
- `backend_v2/models/dtos/evaluation_steps.py`

## CONTEXT (Read-Only)
- None

## Technical Requirements & Milestones

### 1. Uudet Pydantic-mallit (Domain Isolation)
*   Luo `backend_v2/models/v2_core.py` (varmista sijainti, jotta vältetään circular imports):
    ```python
    class LLMExtractedQuote(BaseModel):
        source_alias: str = Field(description="Lyhyt lähde-alias, esim. DOC-1")
        text: str = Field(description="Tarkka lainaus tekstistä")
        model_config = ConfigDict(extra="ignore")
        
    class QuoteEvidenceDTO(V2CoreBase):
        quote_text: str
        source_id: str | None = None
    ```

### 2. Prompt-uudelleenkirjoitus (`field_prompts.py`)
*   Etsi `DESC_EXACT_QUOTES`.
*   Poista kaikki viittaukset `<<QRM-SRC-...>>` -syntaksiin.
*   Päivitä kuvaus ohjeistamaan tekoälyä palauttamaan JSON-objektilista `[{"source_alias": "DOC-X", "text": "..."}]`.

### 3. Neljän LLM-skeeman migraatio
*   Muuta `exact_quotes: list[str]` -> `exact_quotes: list[LLMExtractedQuote]` seuraavissa malleissa:
    *   `LightweightExtractionAtom` (`dtos/lightweight_matrix.py`)
    *   `AtomEvaluationItemDTO` (`dtos/lightweight_matrix.py`)
    *   `BaseTDAExtraction` (`v2_core.py`)
    *   `StepDTOStrict` / `StepDTOSemantic` (`dtos/evaluation_steps.py`)

### 4. Listojen Uudelleennimeäminen Aliaksiksi
*   Vaihda `used_evidence_ids` -> `used_source_aliases: list[str]` (`AtomEvaluationItemDTO`, `LightweightExtractionAtom`, `StepDTOStrict`).
*   Vaihda `source_document_ids` -> `source_document_aliases: list[str]` (`StepDTOStrict`).
*   Päivitä vastaavat promptit (`field_prompts.py`), jotta LLM tietää palauttavansa lyhyitä aliaksia.

## Dokumentaatiopäivitys
- Lisää `docs/architecture/` -kansioon tarvittaessa maininta uudesta LLM-rajapinnan erottelusta (Domain Isolation).

## Testing & Quality Gate Plan
1.  **Unit Tests:** Kirjoita Pydantic-yksikkötestit (`tests/unit/test_quote_evidence.py`), jotka varmistavat, että `LLMExtractedQuote` ei kaadu, vaikka JSONissa olisi ylimääräisiä avaimia (`extra="ignore"`), ja että pakolliset kentät parsitaan oikein.
2.  **Universal Quality Gate:** Aja `uv run python scripts/backend_audit_loop.py backend_v2/models --test`

---
**Session Handover:**
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_91_tracker.md`
