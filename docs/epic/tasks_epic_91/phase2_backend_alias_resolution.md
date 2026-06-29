# Phase 2: Alias-resoluutio ja 2-Stage Translation

**Source:** Epic 91, Task 1.5 - 1.6, Task 3.4
**Context Rules Injected:** 01-python-backend.md (Graceful Degradation, Zero-Compromise Traceability)
**Hardening Rules:** Tripartite Calculation Boundary. Never mix LLM invocation and deterministic math.

## TARGET (Modify)
- `backend_v2/services/mcp/alias_registry.py`
- `backend_v2/hooks/scoring.py`

## CONTEXT (Read-Only)
- `backend_v2/models/v2_core.py` (For QuoteEvidenceDTO structure)

## Technical Requirements & Milestones

### 1. Graceful Degradation (`alias_registry.py`)
*   Nykyinen `resolve()` heittää virheen, jos aliasta ei löydy. Tämä rikkoo Sääntöä 100.
*   Luo `resolve_graceful(alias)` -metodi. Jos aliasta ei ole rekisterissä, logita `logger.warning` ja palauta `None`.

### 2. 2-Stage Translation Pipeline (`scoring.py`)
*   Poista kaikki purkkaviritys-regexit (`<<QRM-SRC...>>` -splitit) ja aliasten generointi "lennosta" `scoring.py`:stä.
*   Lisää post-prosessointivaihe LLM-ajon perään:
    *   Iteroi LLM:n palauttamat `exact_quotes: list[LLMExtractedQuote]`.
    *   Muunna ne `QuoteEvidenceDTO` -objekteiksi. Käytä `AliasRegistry.resolve_graceful(alias)` selvittääksesi aidon Opaque ID:n. Jos resolve palauttaa `None`, aseta `source_id = None`.
    *   Muunna LLM:n listat: `used_source_aliases` -> `used_evidence_ids` ja `source_document_aliases` -> `source_document_ids`. Jälleen käytä `resolve_graceful` ja pudota tuntemattomat aliakset.

### 3. Matemaattisen Aggregaation Irrotus (Extraction)
*   **Source:** Epic 91, Task 3.4
*   Tällä hetkellä matriisien pisteiden laskenta ("Hybrid Calculation") on upotettu suoraan `scoring.py`:n suoritusputkeen (n. L930 alkaen).
*   Irrota tämä logiikka omaksi riippumattomaksi puhtaaksi funktiokseen: `def recalculate(execution_state: ExecutionRecord, profile_id: str) -> None`. 
*   Päivitä normaali LLM-suoritusputki kutsumaan tätä uutta eristettyä `recalculate()`-funktiota kääntämisvaiheen (Translation) jälkeen.
*   **Effective Status:** Varmista, että uusi `recalculate()`-funktio lukee atomin tilaa prioriteetilla: `effective_status = atom.human_override.new_status if atom.human_override else atom.status`.

## Testing & Quality Gate Plan
1.  **Unit Tests:** Kirjoita yksikkötestit `AliasRegistry.resolve_graceful` toimivuudelle ja varmista, että tuntematon alias palauttaa todella `None` eikä kaada prosessia.
2.  **Integration Tests:** Testaa `scoring_engine.recalculate` eristettynä. Varmista, että `human_override`-status jyrää alkuperäisen statuksen matematiikassa.
3.  **Universal Quality Gate:** Aja `uv run python scripts/backend_audit_loop.py backend_v2/hooks --test`

---
**Session Handover:**
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_91_tracker.md`
