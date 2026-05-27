# Phase 4: Model Registry UI & Riverpod Integration (Frontend Layer)

This sub-plan covers exposing the new configuration options (`caching_strategy` and `additional_params` JSON) in the Flutter Admin Studio Model Registry UI.

## Architectural Invariants (From Rules)
1. **Rule 1: No-String Mandate (.arb Localization)** - Kaikki käyttöliittymän tekstit on ladattava `.arb` tiedostoista (`AppLocalizations`).
2. **Rule 2: Flat MVC State & Optimistic UI** - Riverpod Code Generation `@riverpod` on ehdottoman pakollinen kaikille tilan ylläpitäjille.
3. **Rule 3: Horizontal Overflow Prevention** - Kaikki tekstit ja pudotusvalikot Row-komponenteissa pitää suojata `Expanded` wrapperilla renderöintiongelmien estämiseksi.

## Proposed Changes

### Target Files (Modify)
- [model_config.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/model_config.dart)
- [app_en.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_en.arb)
- [app_fi.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb)
- [model_registry_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/model_registry_view.dart)

### Context Files (Read-Only)
- [enums.dart](file:///c:/src/quorum/client_app_v2/lib/core/models/enums.dart)

---

## Milestones

### Milestone 1: Add Fields to LlmModelConfig Dart Model
* **Source**: Epic Phase 4, Step 2
* **Files**: [model_config.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/model_config.dart)
* **Instructions**: Add `additionalParams` to `LlmModelConfig` matching the backend field:
```dart
  const factory LlmModelConfig({
    ...
    @JsonKey(name: 'caching_strategy') String? cachingStrategy,
    @JsonKey(name: 'additional_params') @Default({}) Map<String, dynamic> additionalParams,
  }) = _LlmModelConfig;
```

### Milestone 2: Add Translations to English and Finnish ARB Files
* **Source**: Epic Phase 4, Step 2
* **Files**: [app_en.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_en.arb), [app_fi.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb)
* **Instructions**:
  Add `cachingStrategyLabel` and `additionalParamsLabel` keys to both files in alphabetical order or matching adjacent settings keys:
  * English:
    ```json
    "cachingStrategyLabel": "Caching Strategy",
    "additionalParamsLabel": "Additional Parameters (JSON)",
    ```
  * Finnish:
    ```json
    "cachingStrategyLabel": "Välimuististrategia (Caching Strategy)",
    "additionalParamsLabel": "Lisäparametrit (Additional Parameters JSON)",
    ```

### Milestone 3: Expose Fields in model_registry_view.dart
* **Source**: Epic Phase 4, Step 2
* **Files**: [model_registry_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/model_registry_view.dart)
* **Instructions**:
  1. Add `_buildJsonField` helper widget in `ModelRegistryView` class:
     ```dart
     Widget _buildJsonField(
       Map<String, dynamic>? initialValue,
       String label,
       Function(Map<String, dynamic>) onSaved,
     ) {
       final initialText = initialValue != null && initialValue.isNotEmpty
           ? const JsonEncoder.withIndent('  ').convert(initialValue)
           : '{}';
       return Padding(
         padding: const EdgeInsets.only(bottom: 12.0),
         child: TextFormField(
           initialValue: initialText,
           maxLines: 4,
           decoration: InputDecoration(
             labelText: label,
             border: const OutlineInputBorder(),
           ),
           validator: (val) {
             if (val == null || val.trim().isEmpty) return null;
             try {
               final decoded = jsonDecode(val);
               if (decoded is! Map<String, dynamic>) {
                 return 'Must be a valid JSON object (e.g. {"key": "val"})';
               }
             } catch (e) {
               return 'Invalid JSON';
             }
             return null;
           },
           onSaved: (val) {
             if (val != null && val.trim().isNotEmpty) {
               try {
                 final decoded = jsonDecode(val);
                 if (decoded is Map<String, dynamic>) {
                   onSaved(decoded);
                 }
               } catch (_) {}
             } else {
               onSaved({});
             }
           },
         ),
       );
     }
     ```
  2. Under `_buildModelsSection`, render the two fields before `supportsGrounding`:
     ```dart
     _buildStringField(
       cfg.cachingStrategy,
       l10n.cachingStrategyLabel,
       (val) => updateModel(
         modelId,
         cfg.copyWith(cachingStrategy: val),
       ),
     ),
     _buildJsonField(
       cfg.additionalParams,
       l10n.additionalParamsLabel,
       (val) => updateModel(
         modelId,
         cfg.copyWith(additionalParams: val),
       ),
     ),
     ```
  3. In `saveRegistry()`, read the latest updated state from `ref.read(modelRegistryFormProvider(id)).value` to ensure `onSaved` updates are fully captured and persisted.

---

## Testing & Quality Gate Plan

### Automated Tests
1. Regenerate model serialization and localizations:
   * PowerShell command for l10n: `cd client_app_v2; flutter gen-l10n;`
   * PowerShell command for build_runner: `cd client_app_v2; dart run build_runner build -d;`
2. Run frontend audit loop to verify zero compiler warnings/errors:
   * Command: `uv run python scripts/flutter_audit_loop.py client_app_v2`

---

## Session Handover
To proceed, start a new session and invoke the next step via the Master Tracker:
```powershell
To execute this Epic iteratively, start a NEW chat session and run: /tier5-resume --target docs/epic/EPIC_62_tracker.md
```
