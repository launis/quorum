# Phase 4: Frontend Freezed Models (Flutter-mallit ja Freezed)

This sub-plan addresses **Phase 4: Käyttöliittymä (Flutter Client & Admin Studio)** from Epic 60. It updates the Dart 3 dynamic workflow representation and serializable models to support the new segregated fields, matching the backend's Pydantic schema perfectly and generating type-safe model parsing rules.

## System Invariants & Rules
* **Rule 1: Sealed Classes Mandate (client_application_development.md)**: All polymorphic workflow strategies must utilize Dart 3 Sealed Classes mapped to `@Freezed(unionKey: 'type')` unions. Unknown or arbitrary fallback union cases are strictly banned.
* **Rule 2: Isolate JSON Parsing Mandate (client_application_development.md)**: Heavy JSON parsing must live inside background Dart Isolates (e.g. `Isolate.run()`) to ensure absolute "Zero-Latency Illusion" UI performance.
* **Rule 3: No-String Localisation Mandate (client_application_development.md)**: Raw hardcoded UI display strings are completely banned inside model properties or dart codes. Localization is deferred exclusively to `.arb` asset bundles.

---

## Proposed Changes

### [Component: Flutter Models]
We will replace the old `promptBlocks` list in `NodeStrategy` union models with strictly typed decoupled parameters.

#### [MODIFY] [workflow.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/workflow.dart)
* **Step 1 (Source: Epic Section 4.2)**: Update the serializable `NodeStrategy.llm` and `NodeStrategy.logic` freezed models:
  ```dart
  // Targets c:\src\quorum\client_app_v2\lib\features\studio\models\workflow.dart
  
  // Replace:
  // @Default([]) List<String> promptBlocks,
  //
  // With:
  @StrictOpaqueIdConverter() String? roleBlockId,
  @StrictOpaqueIdConverter() String? extractionProtocolBlockId,
  @Default([]) List<String> criteriaBlockIds,
  ```

---

## Testing & Quality Gate Plan

### Automated Verification
After making changes to standard freezed models, we must run code generation and verify syntax correctness:
1. **Code Generation & Diagnostics**:
   Rebuild serializable mapping definitions (`workflow.freezed.dart`, `workflow.g.dart`):
   ```powershell
   # USER EXECUTION DELEGATION
   uv run python scripts/flutter_audit_loop.py client_app_v2 --build
   ```
2. **Architecture and Compiler Audit**:
   Execute the Flutter audit loop tool to verify absolute zero warnings/errors compliance:
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2
   ```

---

## Session Handover
To proceed, start a new chat session and run the following command to load the tracking context:
```powershell
/tier5-resume --target="docs/epic/EPIC_60_tracker.md"
```
