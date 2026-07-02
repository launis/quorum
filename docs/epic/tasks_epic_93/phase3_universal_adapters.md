# EPIC 93 Phase 3: Universal Adapters and BFF Error Inversion

## Source: Epic 93, Sections 3.3, 3.4 (A & B), and OSA 2.2

### Objective
Implement the Backend-For-Frontend (BFF) translation layer mapping the unified, headless `ReportDataDto` to specific ports: the Flutter SDUI Router and the REST API. Critically implement RFC 7807 Dual-Reporting and explicit `SduiWarningCard` generation for hallucinated aliases.

### Target Files (Modify / Create)
- `backend_v2/models/view/sdui.py` (Add new SduiQuoteCard and SduiWarningCard)
- `backend_v2/services/sdui_mapper.py` (Create new BFF mapping service)
- `backend_v2/api/routers/execution/executions.py` (Expose new ports)

### Context Files (Read-Only)
- `backend_v2/models/view/sdui.py`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

### Architectural Mandates
- **graceful_degradation_over_fail_fast**: While core system is Fail-Fast, hallucinated individual fields from LLMs (e.g., broken alias) should be defensively scrubbed so the expensive run doesn't crash unnecessarily.
- **anemic_routers**: Routers MUST ONLY handle HTTP parsing and delegate to the Service layer.
- **security_logging_ban**: Log ONLY the mathematical/logical reason for the error.
- **Zero Legacy Support Mandate**: Mitään vanhoja rajapintoja, output-muotoja tai legacy-asiakkaita (kuten vanhoja QuoteEvidenceDTO-rakenteita) ei tarvitse eikä saa tukea. Yhteensopivuus vanhan järjestelmän kanssa rikotaan tietoisesti uuden, puhtaan arkkitehtuurin tieltä.

### Implementation Details

1.  **SDUI View Models (`backend_v2/models/view/sdui.py`)**:
    *   Luo `SduiQuoteCard` (SDUI-komponentti validille lainaukselle).
    *   Luo `SduiWarningCard` (SDUI-komponentti varoitusviestillä, jos lainauksen alias on hallusinoitu).
    *   Lisää nämä `AnySduiBlock` discriminated unioniin.

2.  **SDUI BFF Mapper (`backend_v2/services/sdui_mapper.py`)**:
    *   Luo uusi palvelu SDUI-mappaukselle.
    *   Toteuta `map_evidence_to_sdui(q: QuoteEvidenceDTO)`. Iteroi `q.source_alias`.
    *   **RFC 7807 Dual-Reporting**: Jos aliaksista löytyy `OpaqueID.UNVERIFIED`, logita `logger.error("Hallucinated alias detected during SDUI translation")` ja palauta `SduiWarningCard`. Muussa tapauksessa palauta `SduiQuoteCard`.

3.  **REST API Portti (`backend_v2/api/routers/execution/executions.py`)**:
    *   Lisää uusi reitti `GET /{execution_id}/report`, joka palauttaa puhtaan, ui-agnostisen `ReportDataDto`:n JSON-muodossa. Tämä on B2B kone-integraatioita varten (headless).

4.  **SDUI Portti (`backend_v2/api/routers/execution/executions.py`)**:
    *   Lisää reitti `GET /{execution_id}/sdui` (tai päivitä nykyinen `render` endpoint), joka palauttaa UI:lle SDUI-komponenttipuun hyödyntämällä `sdui_mapper.py`:tä.

### Destructive Operation Inventory
- None in this phase.

### Bidirectional Integration Check
- **Producer:** `QuoteEvidenceDTO` yielding `OpaqueID.UNVERIFIED`.
- **Consumer:** `sdui_mapper.py` catching it and returning `SduiWarningCard`.

### Testing & Quality Gate Plan
1.  **Unit Tests:** Unit test the SDUI mapping logic ensuring `OpaqueID.UNVERIFIED` yields exactly 1 Warning Card, regardless of valid sibling sources.
2.  **Integration Tests:** Verify the `/report` endpoint returns raw DTO without SDUI transformation.
3.  **Verification:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/ --test`.

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_93_tracker.md`
