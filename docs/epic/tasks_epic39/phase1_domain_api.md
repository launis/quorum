# Epic 39: Phase 1 - Domain & API Layer (Backend DTOs & Enums)

## Goal
Implement the strict Domain and API foundations for Dynamic Reporting and SDUI. This phase focuses solely on data structures and API contracts, enforcing strict Pydantic V2 validation and polymorphic routing for XAI extensions.

## Target Files (Modify)
- `backend_v2/models/dtos/report.py`
- `backend_v2/models/domain/xai.py`
- `backend_v2/models/enums.py`

## Context Files (Read-Only)
- `backend_v2/models/dtos/output_profile.py`

## Architectural Invariants (MANDATORY)
1. **Strict Pydantic V2 Rust (`strict_pydantic_v2_rust`)**: Use `ConfigDict(strict=True, extra='forbid')` for all DTOs. The use of `dict[str, Any]` or `Any` is STRICTLY FORBIDDEN.
2. **Polymorphic Routing O(1) (`polymorphic_routing_o1`)**: All dynamic `output_extensions` MUST be modeled in `xai.py` using a polymorphic Discriminated Union (`Field(discriminator='extension_type')`).
3. **No String L10N (`no_string_l10n`)**: Replace any hardcoded Finnish strings (e.g., "Verkkohaku") with strict Enum keys (e.g., `ReferenceTitle`).
4. **Data Minimization (API Contract)**: Introduce `MatrixObservabilityDTO` to securely transmit only `true_atoms_count` and `false_atoms_count` to the frontend, preventing token explosions.
5. **The Anti-TDD Trap Mandate**: Do not preserve legacy code or tests that violate these invariants. Rewrite tests to support the new strict architecture.
6. **Zero Compromise Pledge (`the_zero_compromise_pledge`)**: No backwards compatibility. Legacy fallbacks or duck typing must be aggressively removed.
7. **No Fallbacks (`the_duct_tape_ban`)**: Do not provide "magic defaults" (`.get(key, default)`) if fields are missing.
8. **Universal Fail-Fast (`universal_fail_fast`)**: If incoming data violates the schema, the system MUST crash immediately with a ValidationError.

## Implementation Steps
1. Refactor `report.py` (`GlobalContextVarsDTO`, `ReportSynthesisDTO`).
2. Create `MatrixObservabilityDTO` restricting observability payloads.
3. Refactor `xai.py` to ensure all `output_extensions` utilize a strict Discriminated Union.
4. Refactor `enums.py` to provide the necessary Enums for UI strings (`ReferenceTitle`).

## Verification Plan & Quality Gate
Run the standard backend audit loop to ensure OpenAPI schema generation works and tests pass:
```bash
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/report.py backend_v2/models/domain/xai.py backend_v2/models/enums.py --openapi
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/report.py backend_v2/models/domain/xai.py backend_v2/models/enums.py --test
```
