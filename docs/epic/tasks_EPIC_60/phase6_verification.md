# Phase 6: Verification and Quality Gate Hardening (Laatuportti ja Varmistus)

This sub-plan addresses **Phase 6: Quality Gate Hardening & Verification** and the complete **Definition of Done (DoD)** from Epic 60. It establishes a multi-layered automated and manual auditing protocol to ensure zero-regression, flawless Dart/Python type parity, and verified prompt prefix caching gains.

## System Invariants & Rules
* **Rule 1: The Anti-TDD Trap Mandate (tier1-planner.md)**: Absolute architectural rules supersede old test structures. If legacy test fixtures assume old `prompt_blocks` lists or outdated dictionary-parsing patterns, do NOT preserve legacy hacks. Ruthlessly refactor both domain logic AND old test scripts.
* **Rule 2: Deterministic Testing & Coverage Gate (00-antigravity-core.md)**: Claims that tests are complete are void without execution metrics. The `backend_audit_loop.py` tool must verify >90% coverage on new and updated orchestrator/strategy modules.
* **Rule 3: Rule of Three Circuit Breaker (00-antigravity-core.md)**: If any Pytest or Flutter compilation error fails more than 3 times iteratively, execution must stop to prevent agentic logic thrashing.

---

## Proposed Changes

### [Component: Quality Gate]
We will create new unit and integration tests to verify the decoupled prompt compilation process and complete the final verification audit.

#### [NEW] [test_epic_60_decoupling.py](file:///c:/src/quorum/backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py)
* **Step 1 (Source: Epic DoD 4)**: Write isolated unit tests to assert correct decoupled Step parsing, compilation, and error handling.
  * Test 1: Verify that a Step object without criteria blocks or without an extraction protocol block fails validation at construction.
  * Test 2: Verify that `PromptFactory.build` properly integrates `role_block.ai_description` and `protocol_block.ai_description` into the `base_system_prompt` and segregates dynamic inputs within the `<execution_parameters>` tag.

---

## Testing & Quality Gate Plan

### Automated Verification
Perform the ultimate system audits to ensure zero warnings and maximum code coverage.

1. **Python Quality Gate Execution**:
   Run the centralized backend audit loop with coverage and OpenAPI checks:
   ```powershell
   # USER EXECUTION DELEGATION
   uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py backend_v2/services/orchestrator/strategies/llm.py --openapi --test
   ```
2. **Flutter Quality Gate Execution**:
   Verify frontend type alignment and widget compilability:
   ```powershell
   # USER EXECUTION DELEGATION
   uv run python scripts/flutter_audit_loop.py client_app_v2
   ```

---

## Session Handover
To proceed, start a new chat session and run the following command to load the tracking context:
```powershell
/tier5-resume --target="docs/epic/EPIC_60_tracker.md"
```
