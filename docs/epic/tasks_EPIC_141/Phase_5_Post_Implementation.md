# Phase 5: Post-Implementation Final Gates

## 1. Pre-Delete Audit
- **Action:** Verify no orphaned dependencies or unused imports remain in the domains modified during this Epic.
- **Command:** `uv run ruff check backend_v2/`

## 2. Semantic Coverage & Zero-Loss Audit
- **Action:** Mathematically verify line coverage >90% for the surviving business logic (specifically the newly created/refactored files).
- **Command:** `uv run pytest backend_v2/ --cov=backend_v2/services/orchestrator/ --cov-report=term-missing`

## 3. Final E2E REST API Verification Gate
- **Action:** Execute the mandatory full-stack LLM integration test to prove the synthesis pipeline and SDUI matrix mappings function correctly against live models.
- **Command:** `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

## 4. Knowledge Item (KI) Creation
- **Action:** Identify new Single Sources of Truth (SSOTs) created during this Epic (specifically `SynthesisPayloadCompressor` and `ExtractiveSensorService`).
- **Action:** If these introduce new architectural rules, draft the corresponding `.md` artifacts or update current artifacts in the Knowledge Base (`<appDataDir>/knowledge/`).

## 5. Next Steps Post-Execution
Once these steps pass, the Epic is functionally complete and you MUST run the automated documentation syncs:
1. `/tier7-describe-architecture`
2. `/tier8-audit-epic @[docs\epic\EPIC_141_Holistic_Executive_Synthesis.md]`
