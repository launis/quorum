# EPIC 79: Multi-Region Model Discovery & SDUI Integration

## Context & Motivation
Following the transition to Google GenAI V2 (Epic 65), the system successfully decoupled model fetching using the `get_available_models` endpoint. However, the current implementation defaults to `europe-north1` (Hamina) for model discovery, leaving the system vulnerable to transient Vertex AI RPM/TPM throughput limits in that specific datacenter. 

While the system is strictly bound to EU datacenters, the UI currently lacks the capability to switch regions dynamically when encountering congestion.

## Goal
Implement a Datacenter Region multiplexer directly in the Admin Studio (Model Registry), allowing users to switch between regions (e.g., `europe-north1`, `europe-west4`) from the UI. This must trigger an immediate re-fetch of available models for the newly selected region.

## Architectural Mandates
1. **Single Source of Truth**: The region preference must be saved directly to the database via `SystemConfigModelRegistry` under the model's `additionalParams` block (`vertex_location`). No fallback hardcoding.
2. **De-Generator Alignment**: The endpoint `/available-models` must become context-aware without breaking the frontend's strict `Map<String, dynamic>` representations.

## Phased Implementation Plan

### Phase 1: Backend Support for Location-Based Discovery
- **`backend_v2/api/routers/studio/model_registry.py`**: Update `@router.get("/available-models")` to accept an optional query parameter `location: str | None = None`.
- **`backend_v2/services/studio.py`**: Modify `get_available_models(self, initiator, llm_handler, location)` to pass the location argument to `llm_handler.fetch_all_available_models(location=location)`.

### Phase 2: Frontend Data Layer
- **`client_app_v2/lib/core/api/studio_client.dart`**: Update `getAvailableModels({@Query('location') String? location})` to pass the query parameter cleanly.
- **`client_app_v2/lib/features/studio/controllers/model_registry_controller.dart`**: Change `@riverpod Future<List<String>> availableModels` to a family provider or add a location parameter: `availableModels(Ref ref, {String? location})`.

### Phase 3: Frontend UI Layer (Model Registry View)
- **`client_app_v2/lib/features/studio/views/model_registry_view.dart`**:
  - Extract the individual model strategy editor into a sub-widget (e.g., `_ModelStrategyEditor`) to isolate `ref.watch` triggers.
  - Add a Datacenter Region `DropdownButtonFormField` listing EU options (e.g., `europe-north1`, `europe-west4`, `europe-west1`, `europe-west3`).
  - Read/Write the region value directly to `cfg.additionalParams['vertex_location']`.
  - Invalidate and watch the `availableModelsProvider(location: currentRegion)` when the region changes.

## Verification
- Flutter Tier 2 Audit (`uv run python scripts/flutter_audit_loop.py client_app_v2`).
- Python Tier 2 Audit (`uv run python scripts/backend_audit_loop.py . --test`).
