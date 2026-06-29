# Phase 5: Flutter UI ja Dumb Frontend Renderöinti

**Source:** Epic 91, Task 2.3 & 3.2 - 3.3
**Context Rules Injected:** 02_flutter_desktop.md (De-Generator, No-String Mandate, Dumb Frontend)
**Hardening Rules:** Remove all parsing logic from widgets.

## TARGET (Modify)
- `client_app_v2/lib/features/execution/models/scorecard_dto.dart`
- `client_app_v2/lib/features/execution/widgets/atom_matrix_table_widget.dart`

## CONTEXT (Read-Only)
- None

## Technical Requirements & Milestones

### 1. Flutter DTO päivitys (`scorecard_dto.dart`)
*   Luo `QuoteEvidenceDto` (Freezed luokka), jolla kentät `sourceName` (aiemmin Opaque ID backendissä, nyt valmiiksi Snapshotista rikastettu) ja `quoteText`.
*   Luo `HumanOverrideDto`, jossa `newStatus`, `reason`, `evidenceQuotes` (lista `QuoteEvidenceDto`:ita), jne.
*   Päivitä `ScorecardAtomDto` sisältämään kentät `exactQuotes` (`List<QuoteEvidenceDto>`) ja `humanOverride` (`HumanOverrideDto?`).

### 2. Dumb UI (Regex:n kuolema) (`atom_matrix_table_widget.dart`)
*   Poista kaikki `.contains('|||')` ja vastaavat `split()` -hakkerointimetodit koodista.
*   **Logiikka (Dual-Evidence Pattern):**
    *   `if (atom.humanOverride != null)`: Piilota tekoälyn vastaukset haaleaksi. Piirrä matriisiin näyttävä "👨‍⚖️ Ihmisen päätös (EU AI Act)" laatikko, joka renderöi ihmisen oman `reason` kentän ja `humanOverride.evidenceQuotes`.
    *   `else`: Piirrä tavallinen tekoälyn `exactQuotes` -objektilista sellaisenaan.

### 3. Human Override Dialogi
*   Lisää "Yliohjaa päätös" (vasara/kynä -ikoni) painike atomin rivin oikeaan reunaan.
*   Tee `HumanOverrideDialog` modaali, jossa käyttäjä syöttää: Uusi arvosana (Dropdown: PASS/FAIL), Perustelu (TextField), ja Lainaukset.
*   Modaali kutsuu uutta Backend-reittiä (`PATCH /api/v2/executions/{id}/atoms/{atom_id}/override`).

## Testing & Quality Gate Plan
1.  **Unit Tests:** Kirjoita testi, joka antaa widgetille `ScorecardAtomDto`:n jossa on `humanOverride` ja varmistaa, että ihmisen laatikko piirretään tekoälyn sijaan.
2.  **Universal Quality Gate:** Aja `uv run python scripts/flutter_audit_loop.py client_app_v2`

---
**Session Handover:**
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_91_tracker.md`
