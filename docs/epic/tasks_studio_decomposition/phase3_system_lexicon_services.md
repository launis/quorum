# Phase 3: System Configs & Lexicons Extraction

## 1. Goal
Extract `StudioSystemConfigService` and `StudioLexiconService`. These services govern global platform behavior and AI performative filtering.

## 2. Architectural Invariants
- **Tripartite Configuration Architecture (01-python-backend.md)**: Ensure global limits and configuration remain strictly segregated.
- **Fail-Fast**: Ensure root access validation logic is strictly enforced using `auth_validator.py`.

## 3. Destructive Operation Inventory
Move from `StudioService`:
- `get_available_models` -> `StudioSystemConfigService`
- `get_all_system_configs` -> `StudioSystemConfigService`
- `get_system_config` -> `StudioSystemConfigService`
- `save_system_config` -> `StudioSystemConfigService`
- `delete_system_config` -> `StudioSystemConfigService`
- `create_model_registry_draft` -> `StudioSystemConfigService`
- `clone_system_config` -> `StudioSystemConfigService`
- `list_mcp_gateways` -> `StudioSystemConfigService`
- `get_mcp_gateways` -> `StudioSystemConfigService`
- `save_mcp_gateways` -> `StudioSystemConfigService`
- `create_mcp_gateway_draft` -> `StudioSystemConfigService`
- `clone_mcp_gateways` -> `StudioSystemConfigService`
- `list_system_configs` -> `StudioSystemConfigService`
- `get_performative_lexicons_config` -> `StudioLexiconService`
- `save_performative_lexicons_config` -> `StudioLexiconService`
- `discover_new_performative_phrases` -> `StudioLexiconService`
- `translate_performative_phrases` -> `StudioLexiconService`

## 4. Proposed Changes

### [NEW] `backend_v2/services/studio/system_config_service.py`
- Create `StudioSystemConfigService`.

### [NEW] `backend_v2/services/studio/lexicon_service.py`
- Create `StudioLexiconService`.

### [MODIFY] `backend_v2/services/studio/__init__.py`
- Export the new services.

### [MODIFY] `backend_v2/api/dependencies.py`
- Add `StudioSystemConfigServiceDep` and `StudioLexiconServiceDep`.

### [MODIFY] `backend_v2/api/routers/studio/system_configs.py`
- Inject `StudioSystemConfigServiceDep`.

### [MODIFY] `backend_v2/api/routers/studio/model_registry.py`
- Inject `StudioSystemConfigServiceDep`.

### [MODIFY] `backend_v2/api/routers/studio/mcp_gateways.py`
- Inject `StudioSystemConfigServiceDep`.

### [MODIFY] `backend_v2/api/routers/studio/lexicons.py`
- Inject `StudioLexiconServiceDep`.

## 5. Testing Strategy & Quality Gate
1. `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/ --test`
2. `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/studio/ --test`

---
### Session Handover
```bash
/tier5-resume --target="docs/epic/studio_decomposition_tracker.md" --workflow="/tier2-execute" --achieved="Phase 3 Planned" --learned="System configs extracted" --remaining="Execute Phase 3."
```
