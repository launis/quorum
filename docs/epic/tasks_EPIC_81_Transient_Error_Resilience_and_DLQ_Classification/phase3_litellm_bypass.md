# EPIC 81 - Phase 3: LiteLLM Health Check Bypass

## Source Material Traceability
- **Source**: Epic Phase 3, Step 1 & 2
- **Epic Requirements**: Disable LiteLLM's internal Health Check entirely via `enable_pre_call_checks=False` or equivalent configuration in `client.py`'s Router initialization.

## Architectural Invariants & Hardening Mandates
- **Invariant (01-python-backend.md, Rule 27 - deferred_ai_initialization)**: LiteLLM SDKs must be lazily imported. Ensure we don't break existing import boundaries.
- **Invariant (01-python-backend.md, Rule 28 - llm_structured_execution_mandate)**: Do not bypass our own Quorum Pacing Lock for LLMs. The built-in pacing provides domain-aware resilience.
- **Hardening Rule 17 (the_duct_tape_ban)**: The hardcoded LiteLLM "EUR to USD" health check query with a malformed `role: tool` message causes crashes. Removing it is an architectural fix, not duct-tape.

## TARGET (Modify)
- `backend_v2/llm/client.py` (or `backend_v2/llm/provider.py` where the actual LiteLLM Router is initialized. Note: check `provider.py` if `client.py` delegates router initialization.)

## CONTEXT (Read-Only)
- `backend_v2/llm/provider.py` (To trace exactly where the LiteLLM Router is instantiated)

## Sequence Milestones

### Milestone 1: Locate LiteLLM Router Initialization
- **Target**: `backend_v2/llm/provider.py` (or `client.py`, dependent on where `litellm.Router()` or `litellm.completion` is called).
- **Requirement**: Identify where LiteLLM is executing its requests. If using a Router, inject the bypass argument.
- **Implementation Spec**:
  ```python
  # Inject into the router creation configuration
  router_kwargs = {
      "model_list": model_list,
      "enable_pre_call_checks": False, # Disable LiteLLM's buggy health checks
      "retry_after": 0,                # Delegate to Quorum's own retry loops
      # ... existing args
  }
  ```
  *(Note: If `LLMFactory` in `provider.py` uses `litellm.completion` natively instead of a router, we must set `litellm.health_check_interval = 0` or simply configure the router properly if it's utilized).*

### Milestone 2: Update Architecture Documentation
- **Target**: `docs/architecture/execution_orchestration.md`
- **Requirement**: Document the deliberate disabling of third-party LiteLLM health checks in favor of Quorum's native resilient transient loops.

## Testing Strategy & Verification Plan
1. **Manual/Integration Verification**:
   - Because disabling a third party library feature is hard to unit test natively, verify via live execution that no spurious "missing corresponding tool call" errors fire in `backend_debug.log`.
2. **Quality Gate Command**:
   ```bash
   uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py backend_v2/llm/client.py --test
   ```

---

## Session Handover

<session_handover>
This phase is ready for execution.
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_81_Transient_Error_Resilience_and_DLQ_Classification_tracker.md`
</session_handover>
