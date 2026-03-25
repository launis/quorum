# Epic 9: The Zero-Compromise Fail-Fast Remediation (Phase 9 Hardening)

**Status:** Proposed (Tier 3B Target)
**Context:** Quorum V2/V3 Backend & Frontend
**Author:** AI Orchestrator / Principal Solutions Architect
**Reference:** `docs/flutterpromptohje.md`, `docs/antigravity_prompting.md`
**Date:** March 25, 2026

## 1. Problem Statement
Vuoden 2026 Phase 9 Hardening -vaiheessa järjestelmä siirtyy ehdottomaan "Zero-Compromise Pledge" ja "Fail-Fast" -arkkitehtuuriin. Ydinlogiikassa (Core Engine, Database, Domain) ohjelman on kaaduttava välittömästi (`raise AppException`) virheellisen tilan kohdalla. 

Koodikannan auditointi V5.2-mandaatin mukaisesti paljasti **14 tiedostoa**, joissa käytetään arkkitehtuurin ankarasti kieltämää anti-patternia: `try-except pass` tai tyhjiä `catch(e) {}` -lohkoja. Nämä lohkot nielevät virheet hiljaisesti, estävät Root Cause -analyysin, tuhoavat Logfiren telemetrian ja rikkovat Epic 8:n Dual-Reporting -säännöt.

## 2. The Remediation Targets (The "Niellyt Virheet" List)

Tämä Epic vaatii jokaisen seuraavan tiedoston refaktorointia "Tier 3B: Bug Hunting" sääntöjen mukaisesti.
**Tavoite:** Poista `try-except pass` kokonaan TAI korvaa se strukturoidulla lokituksella (`logger.error(..., exc_info=True)`) ja RFC 7807 `AppException` -nostamisella.

### 🐍 Python Backend (13 tiedostoa)
1. `backend_v2/exceptions.py`
2. `backend_v2/logging_config.py`
3. `backend_v2/main.py`
4. `backend_v2/run_worker.py`
5. `backend_v2/hooks/scoring.py`
6. `backend_v2/models/auth.py`
7. `backend_v2/models/v2_core.py`
8. `backend_v2/models/domain/falsifier.py`
9. `backend_v2/models/domain/guard.py`
10. `backend_v2/models/domain/output_profile.py`
11. `backend_v2/models/domain/performativity.py`
12. `backend_v2/services/execution.py`
13. `backend_v2/services/orchestrator/dag_executor.py` *(⚠️ V3 Event Sourcing sijaitsee täällä. Erityisen kriittinen.)*

### 💙 Flutter Client (1 tiedosto)
14. `client_app_v2/lib/features/execution/views/dashboard_view.dart`

## 3. Implementation Rules (Tier 3B Mandate)
1. **Kielletty ratkaisu:** Älä korvaa `pass` -sanaa returnaamalla tyhjää objektia `{}` tai `[]` tai asettamalla hiljainen `None` oireen piilottamiseksi. 
2. **Sallittu ratkaisu (Fail-Fast & Dual-Reporting):** Ota kiinni rajattu, tarkka poikkeus (esim. `except KeyError:`), logita se varjoisasti ja yksityiskohtaisesti palvelimelle (`logger.error("Detailed server trace..", exc_info=True)`). Sitten, jos koodin on pakko pysähtyä, heitä ulkopuoliselle asiakkaalle turvallinen, geneerinen `raise AppException(message="Invalid data structure.", error_code=ErrorCodes.XYZ)`. 
   * **TIETOTURVASÄÄNTÖ (Information Leakage):** Palvelinlokia (`logger.error`) ja ulos lähtevää API-viestiä (`AppException.message`) **EI KOSKAAN** saa yhdistää samaan muuttujaan. Server-loki saa sisältää tarkat ID:t ja koodipolut. Frontendille lähetettävä API-viesti ei koskaan. 
3. **Poikkeus (Graceful Degradation):** Omni-Channel Rendering / BFF -kerroksessa yksittäisen komponentin puuttuminen ei saa kaataa koko sovellusta. Silloin logita varoitus (`logger.warning`) ja palauta ohjelmallinen Fallback, mutta dokumentoi kommentteihin *MIKSI* näin tehdään.

## 4. Execution Plan
1. Kehittäjä valitsee tiedoston tai listan osion tältä sivulta.
2. Syötetään valinta Antigravity-agentille käyttäen **`3B. BUG HUNTING & ROOT CAUSE ANALYSIS`** -protokollaa chattiin (kts. `antigravity_prompting.md`).
3. Agentti fixa tiedoston atomaarisesti Strict Pydantic V2 säännöillä.
4. Ajetaan laadunvarmistus: Python-moduuleille `uv run ruff check . --fix` ja `uv run mypy .` (Strict). Dart-viesteille `dart run custom_lint`.
5. Siirrytään seuraavaan tiedostoon, kunnes tämä Epic on tyhjennetty.
