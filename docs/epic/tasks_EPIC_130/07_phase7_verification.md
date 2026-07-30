# Phase 7: Verification & E2E Integration Gate

Objective: Run full backend and frontend audit loops, and execute the E2E variance script to guarantee SDUI parity between Flutter and PDF rendering.

Source: @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L141-L146]

Expected Actions:
1. Run backend tests: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
2. Run frontend compilation: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
3. Execute parity check: `uv run python scripts/run_e2e_variance_test.py`
