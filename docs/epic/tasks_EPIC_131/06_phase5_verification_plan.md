<execution_protocol>
## Core Directives
1. **Verification Gate**: Enforce full E2E execution safely.

## Implementation Plan

### Step 5.1: Database Re-Seed
**Action**: Run `uv run python backend_v2/seed/run_seed.py local`

### Step 5.2: Backend Audit Loop (Full)
**Action**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test`

### Step 5.3: Flutter Audit Loop (Full)
**Action**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Step 5.4: Contract Parity Test
**Target**: `@[c:\src\quorum\backend_v2\tests\unit\models\test_contract_parity.py]`
- Confirm Python ↔ Flutter DTO field-level parity.
- **Action**: Surgically remove the temporary Phase 3 `'layouts'` ignore logic (`missing_in_python.remove("layouts")`) and the associated `layouts` heuristic regex parser from `test_contract_parity.py`.

### Step 5.5: SDUI Semantic Parity Test
**Target**: `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]`
- Confirm flat block pipeline produces identical visual semantics.

### Step 5.6: MANDATORY Final E2E REST API Verification Gate
**Action**: Run `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
*(Note: If this fails with API key errors, ensure your terminal has valid LLM provider credentials configured).*

### Step 5.7: Manual Verification (UI & PDF)
**Action**: Perform the following manual checks as mandated by the Epic DoD:
1. Start the Flutter desktop app and verify all 4 visualization types (`3d_matrix`, `2d_compare`, `matrix_summary`, `1d_metrics`) render correctly.
2. Export a PDF and verify visual parity with the Flutter rendering.
3. Verify the Admin Studio layout editor successfully creates and saves layout blocks with the new type selector.

### Step 5.8: Epic Conclusion & Tracker Update
**Target**: `@[c:\src\quorum\docs\epic\EPIC_131_tracker.md]`
**Action**: Update the tracker to mark Phase 5 as `[x] (completed)`. Add a final summary of the Epic's success. Instruct the user that the Epic is fully complete.
</execution_protocol>
