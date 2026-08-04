# EPIC 132: SDUI Pre-computation & Dynamic Workflow Extensions Decoupling

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> The integration of **Server-Driven UI (SDUI)** with **Command Query Responsibility Segregation (CQRS)** has emerged as a high-performance architectural pattern in 2025–2026. Industry best practices dictate that transforming raw domain data into UI instructions at request time is compute-heavy and anti-pattern. Instead, systems use **Pre-computation** to generate a "Materialized View" in the write-model phase. By shifting heavy computation (specifically variance mathematics) to the background execution pipeline (Pre-Synthesis Aggregation) rather than doing it at SDUI request time, the architecture remains scalable, perfectly decoupling business logic from the presentation layer (Dumb Painter).

## 1. Goal Description & Background (Objective & Problem Statement)

**Objective**: Eradicate all remaining business logic and ad-hoc mathematical calculations from the Server-Driven UI (SDUI) presentation layer (`blueprint.py`) by extracting dynamic workflow extensions (specifically `variance_validation` and `authenticity_evaluation`) into upstream Pre-Synthesis Aggregation steps and pure SDUI Adapters.

**Problem Statement**: 
During the execution of EPIC 130, all standard UI components were extracted into strict SDUI Adapters (`XaiHighlightsAdapter`, `PenaltiesAdapter`, etc.) utilizing a clean `AdapterContext`. However, dynamic workflow extensions specifically `variance_validation` were left hardcoded in `blueprint.py`. This was because calculating variance requires traversing the execution trace, fetching `step_detector` machine learning scores, and executing mathematical variance functions (`calculate_mechanical_cognitive_variance`). If we extracted this directly into an adapter, it would bloat the `AdapterContext` with heavy global state (`blocks_by_id`, `workflow_steps`, raw traces) and violate the Single Responsibility Principle. `blueprint.py` is acting as both a business logic calculator and a UI presentation layer, violating the "Dumb Painter" invariant.

**Strategic Scope**:
1. Introduce a **Pre-Synthesis Aggregation Step** inside the core execution pipeline (`worker.py` / `ExecutionEngine`) that calculates all workflow extension metrics *before* the UI is rendered.
2. Store the calculated results in a strictly typed `VarianceResultPayload` within the `ExecutionRecord`.
3. Create a clean `VarianceValidationAdapter` that only reads the pre-computed DTO from the `AdapterContext` and maps it to UI blocks (`SduiGridBlock`), preserving 100% Dumb Painter compliance.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- **[DELETE]** Inline `calculate_mechanical_cognitive_variance` calls from `backend_v2/services/blueprint.py`.
- **[DELETE]** Dynamic execution trace traversal loops for linguistic and authenticity checks from `blueprint.py`.
- **[DELETE]** Direct dependencies on `blocks_by_id` and `workflow_steps` for metric extrema boundary resolution inside the UI layer.

### Retained SSOT Invariants (`What We Will RETAIN`)
- **[RETAIN]** The `AdapterContext` schema remains lightweight and immutable.
- **[RETAIN]** The `SduiAdapterProtocol` requiring a single `@staticmethod build(context: AdapterContext) -> list[AnySduiBlock]`.

### Compliance & Modernity Gates
- **CQRS Read/Write Decoupling**: All heavy math and trace traversing (Write side / Aggregation) occurs in the Execution Pipeline. The SDUI generation (Read side) is purely O(1) mapping.
- **Pydantic Strictness**: The new `VarianceResultPayload` must enforce `ConfigDict(strict=True, extra="forbid")`.
- **Dumb Painter SDUI**: The `VarianceValidationAdapter` will contain absolutely zero fallback or mathematical logic.

### Producer-Consumer Integration Check
- **Producer**: `ExecutionEngine` (post-step aggregation) produces `VarianceResultPayload`.
- **Consumer**: `VarianceValidationAdapter` consumes `VarianceResultPayload` via `AdapterContext.execution`.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Data Model & Pre-Synthesis Aggregator
- Define `VarianceResultPayload` in `backend_v2/models/dtos/xai_metrics.py`.
- Update `ExecutionRecord` to store this payload safely (specifically inside a dedicated `synthesis_payload` field).
- Inject an Aggregation Step at the end of the DAG pipeline in `worker.py` / `topological_engine.py` that calculates the variance and commits it to the database before the run concludes.

### Phase 2: SDUI Adapter Extraction
- Create `backend_v2/services/sdui/adapters/variance_validation_adapter.py`.
- Migrate the UI mapping logic (building `SduiGridBlock` and `AlertBlock`) from `blueprint.py` to the new adapter.
- The adapter must fetch data natively via `context.execution.synthesis_payload.variance_result`.

### Phase 3: Blueprint Cleanup & Dispatch Integration
- Strip all `variance_validation` logic out of `backend_v2/services/blueprint.py`.
- Update the dispatch loop in `blueprint.py` to route the `variance_validation` workflow extension through `VarianceValidationAdapter.build(ctx)`.

### Phase 4: Verification & E2E Integration Gate
- Execute Backend Audit Loop.
- Execute Frontend Compilation Parity (Ensure no Unrecognized Keys in Flutter).
- Live API execution trace verification.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- `blueprint.py` contains exactly zero references to `calculate_mechanical_cognitive_variance`.
- `VarianceValidationAdapter` implements the strict `SduiAdapterProtocol`.
- `VarianceResultPayload` is stored persistently in the database during the execution phase, completely decoupling it from the presentation layer.

### Automated Unit Tests
- Run: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- Run: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

### Manual Verification Steps
- Re-seed local DB: `uv run python backend_v2/seed/run_seed.py local`
- View generated `raportti.pdf` to ensure the Variance Validation grid block and alert block render identically to the legacy implementation.

### MANDATORY Final E2E REST API Verification Gate
- Run: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
