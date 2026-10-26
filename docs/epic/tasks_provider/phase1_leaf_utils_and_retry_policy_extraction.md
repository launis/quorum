<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 1: Leaf Environment/Schema Utilities & Transient Retry Policy Extraction (`phase1_leaf_utils_and_retry_policy_extraction.md`)

## 1. Objective
Execute Phase 1 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/llm/provider.py]`:
1. Create the test package marker `[NEW] @[backend_v2/tests/unit/llm/provider/__init__.py]` (`strangler_fig_mandate` rule 2: test subpackages require `__init__.py` from Step 1 to prevent Pytest flat-namespace collisions, while the source domain sub-directory `backend_v2/llm/provider/` MUST NOT contain `__init__.py` while `backend_v2/llm/provider.py` exists).
2. Extract depth-0 leaf static reflection helpers (`_safe_static_getattr` `@[backend_v2/llm/provider.py#L64-L83]`, `_safe_static_hasattr` `@[backend_v2/llm/provider.py#L86-L99]`), `_INTERNAL_NON_API_KEYS` (`#L101-L105`), `resolve_env_variables` (`@[backend_v2/llm/provider.py#L108-L132]`), `_normalize_mcp_tool_schema_for_llm` (`@[backend_v2/llm/provider.py#L135-L159]`), and `_sync_diagnostic_dump` (`@[backend_v2/llm/provider.py#L162-L179]`) into `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` (`< 200` lines).
3. Extract depth-1 transient error detection and adaptive Tenacity `Retry-After` policy (`_is_transient_llm_error` `@[backend_v2/llm/provider.py#L182-L320]`, `_RETRY_AFTER_REGEX` `#L322-L323`, `_extract_retry_after_seconds` `@[backend_v2/llm/provider.py#L326-L398]`, `_AdaptiveWaitWithRetryAfter` `@[backend_v2/llm/provider.py#L401-L444]`, and `_format_attempt_error` `@[backend_v2/llm/provider.py#L447-L453]`) into `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` (`< 310` lines).
4. Update `is_boundary_exempt` (`@[scripts/_ast_guardrails.py#L98-L107]`) so sub-modules inside `backend_v2/llm/provider/` inherit the boundary exemption of `backend_v2/llm/provider.py` during Epoch 1 pure structural lift-and-shift, wire explicit redundant re-exports in `@[backend_v2/llm/provider.py]`, and create dedicated unit tests in `[NEW] @[backend_v2/tests/unit/llm/provider/test_env_and_schema_utils.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_transient_retry_policy.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` | Leaf static reflection (`_safe_static_getattr`, `_safe_static_hasattr`), `_INTERNAL_NON_API_KEYS`, `resolve_env_variables`, `_normalize_mcp_tool_schema_for_llm`, and `_sync_diagnostic_dump` (`< 200` lines, without `__init__.py` in `backend_v2/llm/provider/`) |
| `[NEW]` | `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` | Transient LLM error classifier (`_is_transient_llm_error`), `_RETRY_AFTER_REGEX`, `_extract_retry_after_seconds`, `_AdaptiveWaitWithRetryAfter`, and `_format_attempt_error` (`< 310` lines) |
| `[MODIFY]` | `@[backend_v2/llm/provider.py]` | Replace leaf helpers (`@[backend_v2/llm/provider.py#L64-L83]` through `@[backend_v2/llm/provider.py#L447-L453]`) with explicit redundant re-exports (`Symbol as Symbol`) from `env_and_schema_utils.py` and `transient_retry_policy.py` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L98-L107]` | Extend `is_boundary_exempt` so files under `backend_v2/llm/provider/` inherit boundary exemption during Epoch 1 lift-and-shift |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/__init__.py]` | Mandatory Pytest test package marker |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/test_env_and_schema_utils.py]` | Unit tests for `_safe_static_getattr`, `_safe_static_hasattr`, `resolve_env_variables`, `_normalize_mcp_tool_schema_for_llm`, and `_sync_diagnostic_dump` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/test_transient_retry_policy.py]` | Unit tests for `_is_transient_llm_error`, `_extract_retry_after_seconds`, `_AdaptiveWaitWithRetryAfter`, and `_format_attempt_error` |

### Multi-Phase Decomposition Context (Epoch 1 Surviving Targets)
Across Phases 1–4 of the `provider.py` decomposition, the complete set of surviving production `.py` files (`[NEW]` sub-modules, package facade, and `[MODIFY]` 1-hop production callers) registered for Epoch 2 Tier 2 Hardening is:
- `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` (Phase 1)
- `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` (Phase 1)
- `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` (Phase 2)
- `[NEW] @[backend_v2/llm/provider/provider_factory.py]` (Phase 2)
- `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` (Phase 3)
- `[NEW] @[backend_v2/llm/provider/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/llm/client.py#L46-L58]` (Phase 4)
- `[MODIFY] @[backend_v2/llm/handler.py#L878-L1057]` (Phase 4)
- `[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]` (Phase 4)

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Test Package Marker, Extend Boundary Exemption, and Extract Leaf Modules">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/llm/provider/__init__.py during Phase 1 while backend_v2/llm/provider.py exists on disk. Create backend_v2/tests/unit/llm/provider/__init__.py immediately.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither env_and_schema_utils.py nor transient_retry_policy.py may import from backend_v2.llm.provider, and both MUST remain under 350 lines with all lines <= 120 characters.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/tests/unit/llm/provider/__init__.py]` containing a module docstring.
      2. Update `is_boundary_exempt` (`@[scripts/_ast_guardrails.py#L98-L107]`) so `rel_posix in BOUNDARY_EXEMPTION_FILES or rel_posix.startswith("backend_v2/llm/provider/")` (and `"backend_v2/llm/provider/" in posix_str` in the fallback branch) returns `True`, granting sub-modules under `backend_v2/llm/provider/` the exact same boundary exemption as `backend_v2/llm/provider.py`.
      3. Create `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` (`< 200` lines, all lines `<= 120` chars) with `__all__ = ["_INTERNAL_NON_API_KEYS", "_normalize_mcp_tool_schema_for_llm", "_safe_static_getattr", "_safe_static_hasattr", "_sync_diagnostic_dump", "resolve_env_variables"]`:
         - Relocate `_safe_static_getattr` verbatim from `@[backend_v2/llm/provider.py#L64-L83]`.
         - Relocate `_safe_static_hasattr` verbatim from `@[backend_v2/llm/provider.py#L86-L99]`.
         - Relocate `_INTERNAL_NON_API_KEYS` (`#L101-L105`), `resolve_env_variables` (`@[backend_v2/llm/provider.py#L108-L132]`), `_normalize_mcp_tool_schema_for_llm` (`@[backend_v2/llm/provider.py#L135-L159]`), and `_sync_diagnostic_dump` (`@[backend_v2/llm/provider.py#L162-L179]`).
      4. Create `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` (`< 310` lines, all lines `<= 120` chars) with `__all__ = ["_AdaptiveWaitWithRetryAfter", "_RETRY_AFTER_REGEX", "_extract_retry_after_seconds", "_format_attempt_error", "_is_transient_llm_error"]`:
         - Import `_safe_static_getattr` from `backend_v2.llm.provider.env_and_schema_utils`.
         - Relocate `_is_transient_llm_error` verbatim from `@[backend_v2/llm/provider.py#L182-L320]`.
         - Relocate `_RETRY_AFTER_REGEX` (`#L322-L323`), `_extract_retry_after_seconds` (`@[backend_v2/llm/provider.py#L326-L398]`), `_AdaptiveWaitWithRetryAfter` (`@[backend_v2/llm/provider.py#L401-L444]`), and `_format_attempt_error` (`@[backend_v2/llm/provider.py#L447-L453]`).
    </action>
  </step>

  <step id="2" name="Rewire Re-Exports in provider.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/llm/provider.py.</constraint>
    <action>
      1. Update `@[backend_v2/llm/provider.py]` (`@[backend_v2/llm/provider.py#L64-L83]` through `@[backend_v2/llm/provider.py#L447-L453]`) to replace the extracted leaf functions, constants, and `_AdaptiveWaitWithRetryAfter` class with explicit redundant re-exports from `backend_v2.llm.provider.env_and_schema_utils` and `backend_v2.llm.provider.transient_retry_policy`.
      2. Create `[NEW] @[backend_v2/tests/unit/llm/provider/test_env_and_schema_utils.py]` testing `_safe_static_getattr`, `_safe_static_hasattr`, `resolve_env_variables` (env substitution, missing env error, passthrough non-strings), `_normalize_mcp_tool_schema_for_llm`, and `_sync_diagnostic_dump`.
      3. Create `[NEW] @[backend_v2/tests/unit/llm/provider/test_transient_retry_policy.py]` testing `_is_transient_llm_error` (429/502/503/504, `InstructorRetryException` cause traversal, `ValidationError` rejection, quota exhaustion vs rate limit), `_extract_retry_after_seconds`, `_AdaptiveWaitWithRetryAfter`, and `_format_attempt_error`.
    </action>
  </step>

  <step id="3" name="Run Phase 1 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules, scripts/_ast_guardrails.py, and backend_v2/llm/provider.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/env_and_schema_utils.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/transient_retry_policy.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test --ast-strict` to verify all 34 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_resolve_env_variables_and_mcp_schema_normalization">
      Verifies that resolve_env_variables expands env:VAR strings and _normalize_mcp_tool_schema_for_llm normalizes MCP tool parameters identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_extract_retry_after_and_adaptive_wait_clamping">
      Verifies that _extract_retry_after_seconds parses Retry-After headers and _AdaptiveWaitWithRetryAfter clamps wait durations to max_seconds.
    </contract>
    <contract type="negative" name="test_resolve_env_variables_missing_var_raises_configuration_error">
      Verifies that resolve_env_variables raises ConfigurationError when a referenced environment variable is missing or empty.
    </contract>
  </test_contracts>
</execution_protocol>
```
