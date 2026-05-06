# Epic 47 - Phase 3: Frontend UI, Enums & Exhaustive Switches

## Objective
Implement Dart 3 exhaustive switches for Soft Scoring engines, expose new Profile Editor dropdowns, handle SSE events for anomaly retries, and render Arq Virtual Steps seamlessly in the UI.

## TARGET (Modify)
- `client_app_v2/lib/features/execution/views/dynamic_start_screen.dart`
- `client_app_v2/lib/core/models/` (various DTO files)
- `client_app_v2/lib/features/execution/`
- `client_app_v2/lib/l10n/app_fi.arb`
- `client_app_v2/lib/features/studio/views/output_profile_editor.dart`
- `client_app_v2/lib/features/execution/views/dashboard.dart`
- `client_app_v2/lib/features/execution/widgets/step_card.dart`

## Architectural Invariants (From .agents/rules/)
- **Rule 1: Exhaustive Switches:** Enforce Dart 3 exhaustive `switch` expressions for enums. No `default:` branch. Do not use `.maybeWhen()` or `??` for unions.
- **Rule 2: Zero DB Hardcoding:** Frontend logic must NEVER hardcode UI texts, magic strings, or database IDs.
- **Rule 3: No-String L10n:** UI strings must reside purely in `.arb` files. Fallbacks must not guess IDs.
- **Rule 4: State Mutations:** Ensure optimistic updates and safe Riverpod `ref.invalidate()` when modifying Output Profiles.
- **Rule 5: Macro-Breakpoints:** Layout must remain flex-responsive, no unbounded text in Rows.

## [x] Task 7 (Frontend): UX/XAI - Asynkroninen UX-palaute (SSE)
Target file: `client_app_v2/lib/features/execution/views/dynamic_start_screen.dart`

Intercept SSE for LLM anomaly retries.

New logic requirements:
1. Intercept the SSE message (`{"status": "processing", "message_code": "event_llm_anomaly_retry"}`) in the execution loading state listener.
2. Frontend UI: Dynamically update the loading spinner text to use an i18n translation key mapping to a string like: "Quality Assurance: The AI detected an inconsistency and is verifying its reasoning (Attempt 2)...".

## [x] Task 11: Frontend Hardening - Tyhjentävä käsittely (Dart 3 Exhaustive Switches)
Target files: `client_app_v2/lib/core/models/`, `client_app_v2/lib/features/execution/`, `client_app_v2/lib/l10n/app_fi.arb`

Enforce 'Zero DB Hardcoding' and Exhaustive Handling for Strictness and Engine Selection.

New logic requirements:
1. Replace backend/frontend enums to match the new plain-language taxonomy: "Koearvostelu", "Syväarvostelu", "Lineaarinen Keskiarvo", "Painotettu Keskiarvo".
2. Backend API must return strictness configurations as structured DTOs (e.g., `{"level": 15, "localization_key": "strictness_lenient"}`).
3. Frontend must map the `localization_key` to `AppLocalizations` to eliminate duplicate UI texts (e.g., fixing `Salliva (15) (15)` to just `Salliva (15)`).
4. Enforce Dart 3 EXHAUSTIVE switch expressions for enums (NO `default:` branch allowed).
5. For Freezed unions, strictly use `.map()` or `.when()`. Do not use `.maybeWhen()` or `??` fallbacks.
6. Instruct the AI to run `dart run build_runner build --delete-conflicting-outputs` after updating frontend DTOs.
7. **Agent Rule Compliance**: Enforce `c:\src\quorum\.agents\rules\02_flutter_desktop.md` (Zero-Compromise UI & Zero DB Hardcoding Mandate). No UI component may assume specific database IDs or magic strings.

## [x] Task 12: Tulostemallikohtaiset Kontrollit (UI)
Target file: `client_app_v2/lib/features/studio/views/output_profile_editor.dart`

Expose the new Dynamic Profile Scoring controls in the Flutter UI.

New logic requirements:
1. Profile Editor: Add "Arvostelumoottori" (Scoring Strategy) and "Ankaruustaso" (Strictness Level) dropdowns to the "Muokkaa tulostusprofiilia" view. Ensure these bind to the updated OutputProfile DTOs.
2. **Agent Rule Compliance**: Follow `c:\src\quorum\.agents\rules\02_flutter_desktop.md` for Strongly Typed State. The UI layer must use Riverpod generators and strictly typed DTO models without dynamic `Map` recycling.

## [x] Task 13: Yhtenäinen Askel-UI (Virtual Steps Visualization)
Target files: `client_app_v2/lib/features/execution/views/dashboard.dart`, `client_app_v2/lib/features/execution/widgets/step_card.dart`

New logic requirements:
1. Frontend (Flutter) lukee jo valmiiksi kaikki askeleet `ExecutionRecord.steps` -sanakirjasta. Koska virtuaalinen askel on tietorakenteeltaan täysin validi `StepRecord` (sisältää tilan ja nimen), sen pitäisi automaattisesti piirtyä UI-komponenttina (`StepCard` tms.) oikein ilman suuria koodimuutoksia.
2. Frontendin on hyödynnettävä täsmälleen samaa käyttöliittymäkomponenttia (askeleiden listanäkymä ikoneineen ja lataus-spinnereineen) virtuaalisten askeleiden esittämiseen kuin mitä se käyttää aitojen LLM-askeleiden (kuten "Faktantarkistaja", "Analyst") esittämiseen.
3. Käyttäjän ei pidä visuaalisesti erottaa, onko kyseessä tekoälyn suorittama solmu vai Arq-taustatyö (kuten "Scoring Engine" tai "PDF Generointi"). Kaikki askeleet näkyvät yhtenäisenä, alaspäin rakentuvana listana.
4. Yksittäiset tulostukset (On-Demand): Kun käyttäjä painaa UI:ssa myöhemmin "Luo uusi raportti" tai vaihtaa tulostemallia jo valmiissa ajossa (Execution Dashboardin "Valitse tulostemalli" popup), olemassa olevaan askeleiden listaan on ilmestyttävä lennosta uusi virtuaalinen askel pyörivällä spinnerillä ja backendin uusi laskenta käynnistyy.
5. Testaus: Varmistettava, että käyttöliittymän "Kokonaisedistyminen" (Progress Bar) ymmärtää lennosta dynaamisesti kasvavan askelmäärän (Total Steps = AI-askeleet + Virtuaaliaskeleet) eikä sekoa prosenttilaskennassaan 100 % yli.
6. **Hardening Verification**: The implementing agent MUST execute the `[/tier2-hardening-frontend]` workflow rules upon completion. Explicitly run `dart format .`, `flutter analyze`, and `flutter test` to ensure zero errors. If the analyzer or tests fail, fix them immediately before concluding the task.

## [x] Documentation Update
Update `c:\src\quorum\docs\architecture\` frontend documentation to document Virtual System Steps tracking in the UI.
Täydennä myös `c:\src\quorum\.agents\rules\04_directory_reference.md` tiedostoa tehtyjen muutosten osalta.

## Testing & Quality Gate Plan
1. **UNIT/WIDGET TESTS**: Add/update tests in `client_app_v2` for the `StepCard` and `dashboard.dart` to verify that injecting a virtual step updates the UI gracefully and doesn't exceed 100% progress.
2. Ensure strict adherence by running `uv run python scripts/flutter_audit_loop.py client_app_v2`.
3. If Freezed models change, generate with `dart run build_runner build --delete-conflicting-outputs`.
4. Validate with `flutter analyze` and `flutter test`.
