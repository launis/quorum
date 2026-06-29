# Phase 3: Display Blueprint & Immutability (O(1) Snapshot)

**Source:** Epic 91, Task 2.1 - 2.2
**Context Rules Injected:** 01-python-backend.md (Append-Only Repository Pattern, Immutability)
**Hardening Rules:** The backend MUST NEVER perform O(N) recursive traversal on the `inputs` tree during presentation rendering.

## TARGET (Modify)
- `backend_v2/models/v2_core.py`
- `backend_v2/services/execution.py` (tai missä `ExecutionRecord` luodaan aluksi)
- `backend_v2/services/blueprint.py`
- `backend_v2/hooks/synthesis.py`

## CONTEXT (Read-Only)
- None

## Technical Requirements & Milestones

### 1. O(1) Manifesti (`v2_core.py` & `execution.py`)
*   Lisää `ExecutionRecord`-malliin litteä sanakirja: `source_identity_manifest: dict[str, str] = Field(default_factory=dict)`.
*   Kun ajo (Execution) luodaan ja `inputs` injektoidaan tietokantaan, iteroi kerran input-puun yli ja poimi kaikki ladatut dokumentit (Opaque ID -> Display Name).
*   Tallenna tämä mäppäys litteänä (esim. `{"doc_123": "Sopimus.pdf"}`) ajon `source_identity_manifest` -kenttään. Tämä takaa Immutabiliteetin.

### 2. BFF Puhdistus (`blueprint.py`)
*   Poista `blueprint.py`:stä kokonaan `<<QRM-SRC...>>` -regex-parsinta.
*   Kun rakennat Flutterin payloadia (`ScorecardAtomDTO` -> UI JSON), älä tee kalliita rekursiivisia hakuja `raw_inputs`-puuhun.
*   Sen sijaan, käytä uutta manifestia: `display_name = execution.source_identity_manifest.get(quote.source_id, "Tuntematon lähde")`. Tämä on O(1).
*   Palauta Flutterille puhdas objekti (katso Epic, kohta 3).

### 3. Synthesis.py yhteensopivuus
*   Muuta `backend_v2/hooks/synthesis.py` (n. rivi L190-209). Se lukee tällä hetkellä `exact_quotes` -kenttää olettaen sen olevan merkkijonoja.
*   Muokkaa trunkauslogiikka lukemaan uusien `QuoteEvidenceDTO` -objektien `.quote_text` -kenttää.

## Testing & Quality Gate Plan
1.  **Unit Tests:** Kirjoita testi, joka varmistaa, että manifesti rakennetaan oikein kun ExecutionDTO luodaan.
2.  **Integration Tests:** Testaa `blueprint.py` ja varmista, että JSON payload on puhdas, Opaque ID on poistettu ja tilalla on oikea `sourceName` manifestista haettuna.
3.  **Universal Quality Gate:** Aja `uv run python scripts/backend_audit_loop.py backend_v2/services --test`

---
**Session Handover:**
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_91_tracker.md`
