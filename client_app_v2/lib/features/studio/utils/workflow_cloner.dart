import 'package:uuid/uuid.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_exception.dart';

/// **WorkflowCloner (The Routing Logic Engine)**
/// 
/// Handles the complex deep-cloning of a Workflow DAG.
/// Strict compliance with V2 Architecture `Arkkitehtuuristandardi_Tyonkulun_Kloonaus.md`:
/// 1. Operates entirely on raw `Map<String, dynamic>` payloads (Zero-Deploy SDUI Policy).
/// 2. Implements Fail-Fast security against broken dependencies.
/// 3. Re-routes explicit data paths instead of doing blind global string replaces.
class WorkflowCloner {
  static const Uuid _uuid = Uuid();

  /// Creates a completely standalone copy of the workflow.
  /// Generates new Opaque IDs for steps and structurally updates all internal
  /// semantic routing references (`depends_on`, `input_mappings`, `render_blueprints`).
  /// 
  /// Throws `AppException` if the original workflow contains broken references.
  static Map<String, dynamic> cloneDeep(Map<String, dynamic> original) {
    // 1. Initial deep copy to avoid mutating the original
    final cloned = _deepCopyMap(original);

    final oldId = SafeCast.safeString(cloned['id']);
    final oldSlug = SafeCast.safeString(cloned['slug']);
    
    if (oldId.isNotEmpty) {
      cloned['id'] = '${oldId}copy';
    } else {
      cloned.remove('id');
    }
    
    if (oldSlug.isNotEmpty) {
      cloned['slug'] = '${oldSlug}_copy';
    } else {
      cloned.remove('slug');
    }

    cloned.remove('version');
    cloned.remove('created_at');
    cloned.remove('updated_at');

    final steps = SafeCast.safeList(cloned['steps']);
    
    // --- Phase A: ID Mapping ---
    final Map<String, String> idMap = {};
    for (int i = 0; i < steps.length; i++) {
      final step = SafeCast.safeMap(steps[i]);
      final oldId = SafeCast.safeString(step['id'] ?? step['step_id']);
      if (oldId.isEmpty) continue;

      // Generate secure 128-bit Opaque ID
      final newId = 'steprule_${_uuid.v4().replaceAll('-', '')}';
      idMap[oldId] = newId;

      // Update the step itself
      step['id'] = newId;
      step.remove('step_id');
      steps[i] = step;
    }

    final Set<String> validNewIds = idMap.values.toSet();

    // --- Phase B: Re-routing ---
    for (int i = 0; i < steps.length; i++) {
      final step = SafeCast.safeMap(steps[i]);

      // 1. Re-route `depends_on`
      final dependsOn = SafeCast.safeList(step['depends_on']);
      final newDependsOn = <String>[];
      for (final dep in dependsOn) {
        final String oldDep = dep.toString();
        final mappedDep = idMap[oldDep] ?? oldDep; // Fallback to old if not in map (will trigger Riski 3 check later)
        newDependsOn.add(mappedDep);
      }
      step['depends_on'] = newDependsOn;

      // 2. Re-route `input_mappings`
      // e.g., "$steps.old_id.outputs" -> "$steps.new_id.outputs"
      final mappings = SafeCast.safeMap(step['input_mappings']);
      final newMappings = <String, dynamic>{};
      for (final entry in mappings.entries) {
        String sourceValue = entry.value.toString();
        
        // Structural check rather than global replace: Iterate through known mapped ids
        for (final oldId in idMap.keys) {
          final targetPrefix = '\$steps.$oldId.';
          if (sourceValue.contains(targetPrefix)) {
            final newPrefix = '\$steps.${idMap[oldId]}.';
            sourceValue = sourceValue.replaceFirst(targetPrefix, newPrefix);
            // Since it's specific per mapping, replaceFirst is sufficient and structural
          }
        }
        newMappings[entry.key] = sourceValue;
      }
      step['input_mappings'] = newMappings;
      
      steps[i] = step;
    }

    // 3. Re-route bindings in `render_blueprints`
    if (cloned.containsKey('render_blueprints')) {
      final blueprints = SafeCast.safeMap(cloned['render_blueprints']);
      final updatedBlueprints = <String, dynamic>{};
      
      for (final entry in blueprints.entries) {
        updatedBlueprints[entry.key] = _reRouteNode(SafeCast.safeMap(entry.value), idMap);
      }
      cloned['render_blueprints'] = updatedBlueprints;
    }

    // --- Phase C: Riski 3 - Fail Fast Validation ---
    for (final step in steps) {
      final stepMap = SafeCast.safeMap(step);
      final dependsOn = SafeCast.safeList(stepMap['depends_on']).map((e) => e.toString()).toList();
      
      for (final dep in dependsOn) {
        if (!validNewIds.contains(dep)) {
          // Validation failed: Dependency points to a missing/invalid step.
          throw AppException.validation(
            'workflowCloneErrorMissingDep',
          );
        }
      }
    }

    cloned['steps'] = steps;
    return cloned;
  }

  /// Recursively walks a JSON tree and replaces step ID references.
  static dynamic _reRouteNode(dynamic node, Map<String, String> idMap) {
    if (node is Map<String, dynamic>) {
      final newMap = <String, dynamic>{};
      for (final entry in node.entries) {
        newMap[entry.key] = _reRouteNode(entry.value, idMap);
      }
      return newMap;
    } else if (node is List) {
      return node.map((e) => _reRouteNode(e, idMap)).toList();
    } else if (node is String) {
      String strVal = node;
      // Replace data path bindings inside SDUI definition (e.g. $steps.old_id.results or $results.old_id.foo)
      for (final oldId in idMap.keys) {
         final stepsPrefix = '\$steps.$oldId.';
         if (strVal.contains(stepsPrefix)) {
            strVal = strVal.replaceFirst(stepsPrefix, '\$steps.${idMap[oldId]}.');
         }
         
         final resultsPrefix = '\$results.$oldId.';
         if (strVal.contains(resultsPrefix)) {
            strVal = strVal.replaceFirst(resultsPrefix, '\$results.${idMap[oldId]}.');
         }
      }
      return strVal;
    }
    return node;
  }

  /// Creates a deep copy of a JSON map.
  static Map<String, dynamic> _deepCopyMap(Map<String, dynamic> original) {
    final copy = <String, dynamic>{};
    for (final entry in original.entries) {
      copy[entry.key] = _deepCopyDynamic(entry.value);
    }
    return copy;
  }

  static dynamic _deepCopyDynamic(dynamic value) {
    if (value is Map<String, dynamic>) {
      return _deepCopyMap(value);
    } else if (value is Map) {
      final stringMap = <String, dynamic>{};
      for (final key in value.keys) {
        stringMap[key.toString()] = value[key];
      }
      return _deepCopyMap(stringMap);
    } else if (value is List) {
      return value.map(_deepCopyDynamic).toList();
    }
    return value; // Primitives are passed by value naturally
  }
}
