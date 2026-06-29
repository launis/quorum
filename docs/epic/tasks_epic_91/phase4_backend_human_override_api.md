# Phase 4: Human Override API & SSOT Mutaatio

**Source:** Epic 91, Task 3.1 & 3.4
**Context Rules Injected:** 01-python-backend.md (Fail-Fast Pydantic API, RESTful conventions)
**Hardening Rules:** Tripartite Calculation Boundary. Override updates state -> forces pure recalculate -> outputs new state. No code duplication.

## TARGET (Modify)
- `backend_v2/models/v2_core.py`
- `backend_v2/api/routers/execution/executions.py`

## CONTEXT (Read-Only)
- `backend_v2/hooks/scoring.py` (For the `recalculate` function)
- `backend_v2/services/execution.py`

## Technical Requirements & Milestones

### 1. HumanOverrideDTO
*   Lisää `backend_v2/models/v2_core.py` tiedostoon:
    ```python
    class HumanOverrideDTO(BaseModel):
        new_status: str
        reason: str
        evidence_quotes: list[QuoteEvidenceDTO]
        overridden_by: str
        overridden_at: datetime
    ```
*   Päivitä `ScorecardAtomDTO`:hon kenttä `human_override: HumanOverrideDTO | None = None`.

### 2. Override REST API Reitti
*   Luo `backend_v2/api/routers/execution/executions.py` tiedostoon uusi endpoint: `PATCH /api/v2/executions/{id}/atoms/{atom_id}/override`.
*   Tämä reitti ottaa vastaan Payloadin, joka vastaa ihmisen yliohjausta.
*   Se validoi Payloadin Pydanticilla, etsii oikean ajon (`ExecutionRecord`) ja oikean atomin (`step_states[...].scorecard_atoms`).
*   Se asettaa atomin `human_override` -kentän.

### 3. Pakotettu Uudelleenlaskenta & Tulostus (Re-render)
*   Kun API on asettanut `human_override` -tilan, se kutsuu `scoring_engine.recalculate(execution)`. (Rakennettu vaiheessa 2).
*   Se tallentaa päivitetyn ajon takaisin tietokantaan SSOT:nä.
*   Tämän jälkeen API ohjaa joko palauttamaan JSON:n olemassa olevaa `blueprint.py` -reititystä hyödyntäen tai kutsumalla vanhaa, toimivaa asynkronista PDF-generointia (`enqueue_pdf_generation()`), jos raportti pitää päivittää.

## Testing & Quality Gate Plan
1.  **Unit Tests:** Testaa `PATCH` endpoint mockatulla tietokannalla. Varmista, että validointivirheet (esim. liian lyhyt perustelu) kaatuvat oikein RFC 7807 Fail-Fast -mallin mukaisesti.
2.  **Integration Tests:** Lähetä override API-pyyntö e2e-tyyppisesti. Varmista, että ajo hakeutuu uudelleenlaskentaan ja uudet aggregaatiot näkyvät lopputuloksessa tekoäly-arvosanojen sijaan.
3.  **Universal Quality Gate:** Aja `uv run python scripts/backend_audit_loop.py backend_v2/api --test`

---
**Session Handover:**
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_91_tracker.md`
