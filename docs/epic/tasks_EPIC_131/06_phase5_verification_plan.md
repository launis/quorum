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

### Step 5.5: SDUI Semantic Parity Test
**Target**: `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]`
- Confirm flat block pipeline produces identical visual semantics.

### Step 5.6: MANDATORY Final E2E REST API Verification Gate
**Action**: Run `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
</execution_protocol>
