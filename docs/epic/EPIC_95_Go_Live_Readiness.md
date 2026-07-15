# Epic 95: Quorum V2 Go-Live Readiness & Production Migration

> [!NOTE]
> **Architectural Milestone Reached:** The Quorum V2 Core architecture is officially stable. Epic 91.5 (Universal DTO Bridge), Epic 92 (DAG Engine), Epic 93 (SDUI Unification), and Epic 94 (Frontend Synchronization) have been successfully implemented. The system operates on the unified `ReportDataDTO` SSOT model and a flat topological graph, entirely free of Pipeline B legacy code. Backend test coverage has reached 80%+.

## 1. Objective
With the architectural foundation solid and the backend rigorously hardened, the goal of Epic 95 is to transition Quorum V2 from a stable local environment to **Production Go-Live Readiness**. This involves completing the Testing Pyramid on the Flutter client, establishing CI/CD automation, and executing the Data Migration strategy from V1 to V2.

## 2. Core Principles & Architectural Safeguards
- **Zero-Regression Assurance:** CI/CD pipelines will mathematically prove that the Fail-Fast architecture remains intact before any merge.
- **Tenant Data Isolation:** As we prepare for production data, the Riverpod state invalidation boundary (cross-tenant leakage prevention) must be rigorously tested.
- **Single Source of Truth Preservation:** The database migration from V1 to V2 must cleanly map to the `seed_data.json` schema without introducing legacy "duct-tape" or `extra='ignore'` hacks into the V2 models.

## 3. Implementation Phases

### Phase 1: Frontend Testing Pyramid (Flutter)
While the Python backend is hardened, the Flutter UI requires equal rigor to ensure Server-Driven UI (SDUI) stability.
- **Riverpod Provider Tests:** Verify that O(1) state management correctly handles rapid node mutations and Optimistic UI updates without Memory Leaks (`autoDispose`).
- **Golden Tests (UI Parity):** Implement Golden Master snapshot tests for core SDUI components (`N_A_CARD`, Matrix Blocks) to ensure 100% pixel-perfect rendering of the backend Markdown/ICU parity.
- **Error Boundary Verification:** Test that network failures gracefully degrade without crashing the UI (Graceful Network Degradation), while JSON schema errors successfully trigger the `AppErrorBoundary` (Fail-Fast).

### Phase 2: CI/CD Pipeline Automation
- **Unified Quality Gate:** Integrate `scripts/backend_audit_loop.py` and `scripts/flutter_audit_loop.py` into a strict CI/CD pipeline (e.g., GitHub Actions).
- **Contract Enforcement:** Automate `test_contract_parity.py` to block any PR where Python Pydantic models drift from Flutter Freezed models.

### Phase 3: V1 to V2 Database Migration (The Big Bang)
- **Migration Script Generation:** Create a one-off transformation script (`migration_v1_to_v2.py`) that reads the old relational database and maps the nested legacy structures into the new flat topological DAG structure (`seed_data.json`).
- **Data Sanitization:** The migration script must drop all deprecated fields. V2 Pydantic models will run with `strict=True, extra='forbid'` during the migration load to guarantee zero legacy pollution.

### Phase 4: Production Telemetry & Security Audit
- **Logfire & Arq Telemetry:** Verify that all background tasks report trace IDs correctly to Logfire without leaking PII or HTTP secrets.
- **Tenant Isolation Audit:** Prove that the FastAPI `response_model` strictly strips hidden database fields, preventing Cross-Tenant Trace Leaks.

## 4. Next Steps for Execution
To begin execution, the user should run the Tier 1 Planner on this Epic to break down Phase 1 into actionable implementation plans:
`/tier1-planner --target="docs/epic/EPIC_95_Go_Live_Readiness.md"`
