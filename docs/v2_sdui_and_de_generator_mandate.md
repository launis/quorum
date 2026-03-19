# V2 Frontend Architecture: SDUI & De-Generator Mandate

This document outlines the authoritative standards for the V2 Flutter client, emphasizing dynamic orchestration and strict rejection of generated domain models.

## 1. Zero-Deploy SDUI (Server-Driven UI) & The "Zero-Math" Mandate

The V2 architecture enforces a strict tripartite boundary between Data, Computation, and Presentation. The V2 frontend acts exclusively as a "Dumb Rendering Engine".

- **Database Purity (`ExecutionRecord`)**: The database MUST serve as the Single Source of Truth for raw data only. It must NEVER store ephemeral display variables (e.g., `visual_pct`, `display_value_only`, CSS coordinates). Storing rendering math in the DB corrupts the schema and breaks migration safety.
- **Backend Computation (`/render` API)**: All business logic, mathematical layout calculations (percentages, max scales), and string formatting (localization, decimals) MUST occur lennosta (on-the-fly) within the Python `BlueprintTransformer`.
- **Zero-Math UI (Frontend)**: The Flutter frontend MUST NOT perform any mathematical calculations, string formatting (e.g., `.toStringAsFixed(1)`), or fallback assignments. It blindly binds to the pre-calculated aesthetic string/float properties provided by the `/render` API.
- **Render Delegation**: The legacy `SDUIWidgetFactory` and direct database-to-UI rendering debug loops are strictly banned to prevent schema contamination. All widgets must compose via the standardized `SduiRenderer`.

## 2. The No-CodeGen Mandate (V2 Domain Data)

To maintain maximum flexibility and avoid "Drift" between backend and frontend schemas, **V2 domain data MUST NOT use code generators.**

- **Banned**: `freezed`, `json_serializable`, `riverpod_generator` for API models.
- **Requirement**: Use pure `Map<String, dynamic>` for domain objects fetched from the V2 API.
- **Fail-Fast Typing**: While model classes are banned, variables MUST be typed where possible (e.g., `final int strictness = SafeCast.safeInt(data['strictness'])`).

### 2.1 Recursive Deep Copy for Nested States
When managing complex configurations (like the Model Registry) as a `Map<String, dynamic>`, Riverpod states MUST be treated as immutable.
- **Problem**: Standard `Map.from(oldMap)` only performs a shallow copy. Modifying nested maps (e.g., `editableState['models']['google']['temperature'] = 0.5`) silently mutates the provider's original state, leading to unpredictable UI behavior and cache corruption.
- **Mandate**: Every view implementing an edit form for a nested configuration MUST utilize a recursive deep copy utility (`SafeCast.safeDeepCopyMap`) to create its working state.

## 3. SafeCast & Defensive Parsing

Since static type safety is relaxed at the serialized boundary (Map-access), the frontend must implement a rigorous **SafeCast Layer**.

- **Pattern**: Every key lookup must pass through a utility (e.g., `SafeCast.safeDouble(map['val'])`, `SafeCast.safeString(map['label'])`).
- **Graceful Degradation**: If a non-critical field is missing or malformed, the SafeCast utility returns a clean default (e.g., `0.0`) and logs a warning.
- **Fail-Fast (Critical)**: For mandatory identifiers (like workflow ID), the lookup must throw an exception or return an error state from the controller to prevent a partial/ghost UI state.

## 4. Live Rendering (SSE + StreamNotifier)

In Phase 3, the execution monitoring transitioned from polling to **Server-Sent Events (SSE)**.

- **SSE Client**: Uses `Dio`'s byte stream processing to parse fragmented JSON event objects.
- **StreamNotifier**: Riverpod's `StreamNotifier` is used to maintain a persistent connection. The `build()` method yields `async*` data as events arrive.
- **Blind SDUI Rendering**: The `ExecutionReportView` uses `SliverGrid` to iterate through the ephemeral layout JSON provided by the `/render` API. It delegates rendering to `SduiRenderer` without knowing the specific contents, while the raw `ExecutionView` debugger is prohibited from constructing visual blocks.
- **Audit Drift Check**: The view compares the `version_id` of the live execution with the current system's active version. If they differ, a "Audit Drift" banner is displayed.

## 5. Admin Studio V2: Dynamic CRUD Patterns

Phase 4 introduced the "Studio Dashboard" for managing V2 configurations.

- **I18n Dynamic Input**: The `I18nTextField` manages a map of `default_locale` and `translations`. This allows administrators to provide multilingual content for any field in a matrix or workflow.
- **Universal Matrix Builder**: A high-density interface for creating evaluation rubrics.
    - **Calibration**: Includes a global "Strictness/Kireys" slider (0-100).
    - **XAI Grounding**: Each criterion can specify a theory URL and citation reference.
- **Workflow DAG Builder**: Defines the execution graph.
    - **Semantic Routing**: Admins use `$inputs.key` or `$steps.step_id.results` to map data flow between asynchronous agent steps.
    - **Depends On**: Explicit graph edges (`depends_on: [step_A]`) allow the backend `dag_executor` to parallelize independent tasks.

## 6. The Map Iteration Type-Safety Hazard

When building dynamic UIs from flexible JSON objects (e.g., the Model Registry), a critical runtime hazard exists when iterating over map values if the schema is polymorphic or contains literal mappings.

- **The Symptom**: A red "Screen of Death" or `type 'String' is not a subtype of type 'Map<String, dynamic>' in type cast`.
- **The Cause**: The code assumes all children in a nested map are of the same structure (e.g., `google.values.map((v) => v as Map<String, dynamic>)`), but the backend may include literal role mappings (e.g., `"AnalystAgent": "fast"`) alongside full strategy objects.
- **The Mandate**: UI components MUST perform type-checking during iteration. If a value is a `String`, it should be rendered as a simple `ListTile` or mapping link; only `Map` values should trigger full strategy/config forms. 
