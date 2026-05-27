# Phase 2: Dynamic Env Resolver & Provider Decoupling (Backend Layer)

This sub-plan covers implementing the dynamic environment variable resolver and provider decoupling.

## Architectural Invariants (From Rules)
1. **Rule 1: The Zero-Compromise Pledge** - Taaksepäinyhteensopivuus, fallback-ketjut tai ohjelmointikielen oletusarvot (esim. `v.get('kenttä', '')`) ovat ankarasti kiellettyjä. Puuttuva ympäristömuuttuja laukaisee `ConfigurationError`-virheen.
2. **Rule 2: No Inline Imports** - Kaikki importit on ilmoitettava globaalisti tiedoston yläosassa pytest-yhteensopivuuden ja koodin selkeyden takaamiseksi.

## Proposed Changes

### Target Files (Modify)
- [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py)
- [client.py](file:///c:/src/quorum/backend_v2/llm/client.py)

### Context Files (Read-Only)
- [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)

---

## Milestones

### Milestone 1: Implement Dynamic Env Resolver in provider.py
* **Source**: Epic Phase 2, Step 1
* **Files**: [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py)
* **Instructions**: Add a global helper function `resolve_env_variables` at the top level of `provider.py` (after imports):
```python
def resolve_env_variables(params: dict[str, Any]) -> dict[str, Any]:
    """Korvaa parametrien ${ENV_VAR} -viitteet todellisilla ympäristömuuttujilla."""
    resolved = {}
    for k, v in params.items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_key = v[2:-1]
            resolved_value = os.getenv(env_key)
            if not resolved_value:
                raise ConfigurationError(
                    f"Strict Mode: Vaadittua ympäristömuuttujaa '{env_key}' ei löydy "
                    f"järjestelmästä parametrille '{k}'."
                )
            resolved[k] = resolved_value
        else:
            resolved[k] = v
    return resolved
```

### Milestone 2: Decouple LiteLLMProvider.generate from Hardcoded Vertex Checking
* **Source**: Epic Phase 2, Step 2
* **Files**: [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py)
* **Instructions**:
  1. Remove the hardcoded `vertex_location` checking code and `v_loc` resolution from lines 318-338 of `LiteLLMProvider.generate`.
  2. Dynamically resolve and unpack `self._config.additional_params` into `call_kwargs`:
```python
if self._config and self._config.additional_params:
    resolved_additional = resolve_env_variables(self._config.additional_params)
    call_kwargs.update(resolved_additional)
```

### Milestone 3: Pass additional_params in LLMClient
* **Source**: Epic Phase 2, Step 3
* **Files**: [client.py](file:///c:/src/quorum/backend_v2/llm/client.py)
* **Instructions**: Locate `LLMClient.from_strategy()` and update `LLMProviderConfig` instantiation to pass `additional_params`:
```python
        provider_config = LLMProviderConfig(
            id=f"prv_{uuid.uuid4().hex}",
            provider=target_provider,
            model_name=target_strategy.model_name,
            api_key=target_strategy.api_key,
            temperature=target_strategy.temperature,
            top_p=target_strategy.top_p,
            top_k=target_strategy.top_k,
            tpm_limit=target_strategy.tpm_limit,
            rpm_limit=target_strategy.rpm_limit,
            default_max_tokens=target_strategy.max_tokens,
            supports_grounding=target_strategy.supports_grounding,
            parsing_mode=target_strategy.parsing_mode,
            caching_strategy=target_strategy.caching_strategy,
            additional_params=target_strategy.additional_params,
        )
```

---

## Testing & Quality Gate Plan

### Automated Tests
1. Run LLM Client and Provider unit tests:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/llm/ --test
   ```
2. Verify all tests pass and coverage is >90%.

---

## Session Handover
To proceed, start a new session and invoke the next step via the Master Tracker:
```powershell
To execute this Epic iteratively, start a NEW chat session and run: /tier5-resume --target docs/epic/EPIC_62_tracker.md
```
