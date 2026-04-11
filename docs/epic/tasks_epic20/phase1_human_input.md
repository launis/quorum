# Phase 1: Pääkäyttäjän syöte (Human Input)

## Objective
Luodaan käyttöliittymään ja pohjamalleihin mekanismi, jolla pääkäyttäjä voi rakentaa yksinkertaisen 5-portaisen BARS-matriisin (1-2 lausetta per taso) V2 arkkitehtuurissa huolehtimatta tekoälyn suoritusrajoitteista.

## TARGET (Modify)
- `backend_v2/models/v2_core.py` (Mahdolliset lisäykset PromptBlockin taustarakenteisiin, jos atomisaation varastointi vaatii uusia kenttiä)
- `client_app_v2/lib/features/studio/domain/models/` (Freezed-mallit Matrixille)
- `client_app_v2/lib/features/studio/presentation/components/` (Matrix Builder UI -komponentit työpöydälle)

## CONTEXT (Read-Only)
- `client_app_v2/lib/core/models/enums.dart`
- `backend_v2/seed/seed_data.json`

## Architectural Constraints (V2 Sequence)
1. **Dependencies:** Varmistetaan, ettei käyttöliittymä ota ratkaistakseen "O(N^2) list" ongelmia dynaamisen Canvaksen ulkopuolella. 
2. **Pydantic Models -> L10n:** Määritellään yksinkertainen syöte. Kaikki uudet tekstikentät UI:ssa tulee käyttää `AppLocalizations` .arb-käännöksiä (No-String Mandate).
3. **Frontend Controller -> UI:** Vältetään `SizedBox.shrink()` UI:n renderöinnissä ja hyödynnetään `AppErrorBoundary`. Desktop-First Flexbox/Expanded säännöt estämässä ylivuotoja matriisin sarakkeissa.

## Design / Implementation specifics
* "Macro-Breakpoint" -sääntö mukaisesti kehitetään matriisille "Three-Pane" asettelu isoilla ruuduilla ja Split-Screen kapeammilla, jotta asiantuntija voi helposti arvioida ja luoda arvosanakriteerit (1-5 tasot).
* Optimoitu `InteractiveViewer` hyödyntää nollalatenssin SWR:ää Riverpod 3.0:ssa kun syötteitä (claims) päivitetään.

## Verification & Quality Gate Plan
* Kirjoitetaan yksikkötestit UI:n matriisilaajennuksille (Flutter widget testing).
* Validointi: `uv run python scripts/flutter_audit_loop.py client_app_v2` ja tarvittaessa koodin generointi tiedostojen muutoksille `flutter gen-l10n` sekä `dart run build_runner build -d`.
