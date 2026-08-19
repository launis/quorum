# Phase 5: Quality Gates & Anti-Happy-Path Falsification (DEFERRED)

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 5 "Quality Gates & Anti-Happy-Path Falsification" (L640-L698) and 6-Step Pipeline Step 6 (L265-L270)
**Status:** PLACEHOLDER — Detailed plan will be generated after Phase 4 is complete.

**Overview:** Final quality gate sweep with negative/boundary tests, anti-happy-path falsification, cross-platform parity verification, and Final Live E2E REST API Verification.

**Estimated Sub-Plans:**
- 22_p5_backend_negative_tests.md — Backend Pydantic boundary tests (ge/le violations, extra keys, invalid enums)
- 23_p5_frontend_negative_tests.md — Frontend CheckedFromJsonException tests
- 24_p5_live_e2e_verification.md — Final E2E REST API integration test

**Key Verification Commands:**
- Backend: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
- Frontend: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
- Full regression: `uv run python scripts/backend_audit_loop.py backend_v2 --test`

**Prerequisites:** Phase 4 (Plans 20-21) must be complete.
