# Phase 5: Architecture Documentation Update

## Objective
Update the core architecture documentation (`docs/architecture/`) to reflect the new state of the backend after successfully implementing Structured State Envelopes and API Boundary Sovereignty. The documentation must act as the Single Source of Truth (SSOT) for developers, explaining the paradigm shift away from "loose dictionaries".

## Execution Steps

1. **Target (Modify): `c:\src\quorum\docs\architecture\01_backend_api_and_core.md`**
   - Update the descriptions around API layer to explicitly state that the system employs `BaseResponseDTO` to strip hidden database variables and ensure multi-tenant isolation. Mention that routers no longer handle `exclude=True` locally.

2. **Target (Modify): `c:\src\quorum\docs\architecture\02_domain_models.md`**
   - Add a new section or update existing definitions to document `StepOutputDTO`.
   - Explain that execution traces are projected strictly as `List[StepOutputDTO]` instead of flat dictionaries, establishing the **Structured State Envelopes** principle.
   - Document `BaseResponseDTO` and its role in enforcing the "API Boundary Leakage Trap" prevention.

## Verification & Quality Gate Plan
- Manually review the updated markdown documents to ensure the architectural narrative is clear and correctly instructs future AI agents and human developers on the new baseline.
