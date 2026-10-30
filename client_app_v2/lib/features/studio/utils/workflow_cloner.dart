import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/utils/json_converters.dart';

/// **WorkflowCloner (The Routing Logic Engine)**
///
/// Handles the complex deep-cloning of a Workflow DAG.
/// Enforces 100% Freezed model domain cloning (`cloneWorkflow`) and strict
/// Fail-Fast validation (Zero-Fallback, 32-hex RFC 9562 UUIDv7 IDs via
/// `generateOpaqueUuid7`, and DAG dependency / causal source verification).
class WorkflowCloner {
  /// Clones a strongly-typed [Workflow] domain model with newly generated
  /// 32-hex RFC 9562 UUIDv7 identifiers (`wf_`, `sr_`, `op_`) and remapped
  /// DAG dependency, input mapping, causal source, and output profile references.
  ///
  /// Throws [AppException] if any dependency or `causalSourceStepId` points to
  /// a missing or unmapped step.
  static Workflow cloneWorkflow(Workflow original) {
    final newWorkflowId = generateOpaqueUuid7('wf');
    final newSlug = original.slug.isNotEmpty
        ? '${original.slug}_copy'
        : newWorkflowId;

    // 1. Build 1:1 StepRule ID mapping using 32-hex RFC 9562 UUIDv7 ('sr_')
    final idMap = <String, String>{};
    for (final step in original.steps) {
      if (step.id.isEmpty) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Step ID cannot be empty during workflow clone.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }
      idMap[step.id] = generateOpaqueUuid7('sr');
    }

    final validNewIds = idMap.values.toSet();

    // 2. Remap StepRule instances and enforce Fail-Fast topological invariants
    final clonedSteps = <StepRule>[];
    for (final step in original.steps) {
      final newStepId = idMap[step.id]!;

      final newDependsOn = <String>[];
      for (final oldDep in step.dependsOn) {
        final mappedDep = idMap[oldDep];
        if (mappedDep == null || !validNewIds.contains(mappedDep)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail: 'Dependency points to a missing/invalid step.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        newDependsOn.add(mappedDep);
      }

      final newMappings = <String, String>{};
      for (final entry in step.inputMappings.entries) {
        newMappings[entry.key] = _remapStepBindingString(entry.value, idMap);
      }

      String? newCausalSource;
      final oldCausalSource = step.causalSourceStepId;
      if (oldCausalSource != null && oldCausalSource.isNotEmpty) {
        final mappedCausal = idMap[oldCausalSource];
        if (mappedCausal == null || !validNewIds.contains(mappedCausal)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail: 'Causal source step ID could not be remapped.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        if (!newDependsOn.contains(mappedCausal)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail:
                'Causal source step ID must exist in valid new steps and depends_on.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        newCausalSource = mappedCausal;
      }

      clonedSteps.add(
        step.copyWith(
          id: newStepId,
          dependsOn: newDependsOn,
          inputMappings: newMappings,
          causalSourceStepId: newCausalSource,
        ),
      );
    }

    // 3. Remap attached OutputProfiles and their content block bindings
    final profileIdMap = <String, String>{};
    final clonedProfiles = <String, OutputProfile>{};
    for (final entry in original.outputProfiles.entries) {
      final oldProfile = entry.value;
      final newProfileId = generateOpaqueUuid7('op');
      profileIdMap[entry.key] = newProfileId;
      profileIdMap[oldProfile.id] = newProfileId;

      final remappedBlocks = oldProfile.contentBlocks
          .map((block) => _remapSduiBlock(block, idMap))
          .toList(growable: false);

      clonedProfiles[newProfileId] = oldProfile.copyWith(
        id: newProfileId,
        workflowId: newWorkflowId,
        contentBlocks: remappedBlocks,
      );
    }

    final newDefaultProfileId =
        profileIdMap[original.defaultProfileId] ?? original.defaultProfileId;

    return original.copyWith(
      id: newWorkflowId,
      slug: newSlug,
      version: 1,
      steps: clonedSteps,
      outputProfiles: clonedProfiles,
      defaultProfileId: newDefaultProfileId,
    );
  }

  /// Creates a completely standalone copy of a raw workflow map payload.
  /// Generates new 32-hex RFC 9562 UUIDv7 Opaque IDs (`wf_`, `sr_`) and
  /// structurally updates all internal semantic routing references
  /// (`depends_on`, `input_mappings`, `causal_source_step_id`, `output_profiles`).
  ///
  /// Throws [AppException] if the original workflow contains broken references
  /// or malformed step structures.
  static Map<String, Object?> cloneDeep(Map<String, Object?> original) {
    final cloned = _deepCopyMap(original);

    final rawId = cloned['id'];
    if (rawId is String && rawId.isNotEmpty) {
      cloned['id'] = generateOpaqueUuid7('wf');
    } else {
      cloned.remove('id');
    }

    final rawSlug = cloned['slug'];
    if (rawSlug is String && rawSlug.isNotEmpty) {
      cloned['slug'] = '${rawSlug}_copy';
    } else {
      cloned.remove('slug');
    }

    cloned.remove('version');
    cloned.remove('created_at');
    cloned.remove('updated_at');

    final stepsRaw = cloned['steps'];
    if (stepsRaw != null && stepsRaw is! List) {
      throw const AppException(
        type: 'https://api.quorum.fi/errors/workflow-clone-failed',
        title: 'Clone Failed',
        status: 400,
        detail: 'Invalid workflow steps collection: expected a List.',
        extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
      );
    }
    final steps = stepsRaw is List ? List<Object?>.from(stepsRaw) : <Object?>[];

    // --- Phase A: ID Mapping ---
    final Map<String, String> idMap = {};
    for (int i = 0; i < steps.length; i++) {
      final rawStep = steps[i];
      if (rawStep is! Map<String, Object?>) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Invalid step item in workflow steps: expected a Map.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }

      final step = rawStep;
      final idCandidate = step.containsKey('id') ? step['id'] : step['step_id'];
      if (idCandidate is! String || idCandidate.isEmpty) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Step ID is missing or empty.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }

      final newId = generateOpaqueUuid7('sr');
      idMap[idCandidate] = newId;

      step['id'] = newId;
      step.remove('step_id');
      steps[i] = step;
    }

    final Set<String> validNewIds = idMap.values.toSet();

    // --- Phase B: Re-routing & Fail-Fast Verification ---
    for (int i = 0; i < steps.length; i++) {
      final step = steps[i] as Map<String, Object?>;

      // 1. Re-route `depends_on`
      final dependsOnRaw = step['depends_on'];
      if (dependsOnRaw != null && dependsOnRaw is! List) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Step depends_on must be a List.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }
      final dependsOn = dependsOnRaw is List ? dependsOnRaw : const <Object?>[];
      final newDependsOn = <String>[];
      for (final dep in dependsOn) {
        final String oldDep = dep.toString();
        final mappedDep = idMap[oldDep];
        if (mappedDep == null || !validNewIds.contains(mappedDep)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail: 'Dependency points to a missing/invalid step.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        newDependsOn.add(mappedDep);
      }
      step['depends_on'] = newDependsOn;

      // 2. Re-route `input_mappings`
      final mappingsRaw = step['input_mappings'];
      if (mappingsRaw != null && mappingsRaw is! Map) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Step input_mappings must be a Map.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }
      final mappings = mappingsRaw is Map
          ? mappingsRaw
          : const <String, Object?>{};
      final newMappings = <String, Object?>{};
      for (final entry in mappings.entries) {
        final sourceValue = _remapStepBindingString(
          entry.value.toString(),
          idMap,
        );
        newMappings[entry.key.toString()] = sourceValue;
      }
      step['input_mappings'] = newMappings;

      // 3. Re-route `causal_source_step_id`
      final rawCausalSource = step['causal_source_step_id'];
      if (rawCausalSource is String && rawCausalSource.isNotEmpty) {
        final newCausalSource = idMap[rawCausalSource];
        if (newCausalSource == null || !validNewIds.contains(newCausalSource)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail: 'Causal source step ID could not be remapped.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        if (!newDependsOn.contains(newCausalSource)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail:
                'Causal source step ID must exist in valid new steps and depends_on.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        step['causal_source_step_id'] = newCausalSource;
      }

      steps[i] = step;
    }

    // 4. Re-route bindings in `output_profiles`
    if (cloned.containsKey('output_profiles')) {
      final blueprintsRaw = cloned['output_profiles'];
      if (blueprintsRaw != null && blueprintsRaw is! Map) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Workflow output_profiles must be a Map.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }
      final blueprints = blueprintsRaw is Map
          ? blueprintsRaw
          : const <String, Object?>{};
      final updatedBlueprints = <String, Object?>{};

      for (final entry in blueprints.entries) {
        final entryVal = entry.value;
        if (entryVal is! Map<String, Object?>) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail: 'Output profile entry must be a Map.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        updatedBlueprints[entry.key.toString()] = _reRouteNode(entryVal, idMap);
      }
      cloned['output_profiles'] = updatedBlueprints;
    }

    cloned['steps'] = steps;
    return cloned;
  }

  static SduiBlockDTO _remapSduiBlock(
    SduiBlockDTO block,
    Map<String, String> idMap,
  ) {
    final serialized = _deepCopyMap(block.toJson());
    final remapped = _reRouteNode(serialized, idMap) as Map<String, Object?>;
    return SduiBlockDTO.fromJson(remapped);
  }

  static String _remapStepBindingString(
    String value,
    Map<String, String> idMap,
  ) {
    String updated = value;
    for (final entry in idMap.entries) {
      final oldId = entry.key;
      final newId = entry.value;

      final stepsPrefix = '\$steps.$oldId.';
      if (updated.contains(stepsPrefix)) {
        updated = updated.replaceFirst(stepsPrefix, '\$steps.$newId.');
      }

      final resultsPrefix = '\$results.$oldId.';
      if (updated.contains(resultsPrefix)) {
        updated = updated.replaceFirst(resultsPrefix, '\$results.$newId.');
      }
    }
    return updated;
  }

  /// Recursively walks a JSON tree and replaces step ID references.
  static Object? _reRouteNode(Object? node, Map<String, String> idMap) {
    if (node is Map<String, Object?>) {
      final newMap = <String, Object?>{};
      for (final entry in node.entries) {
        newMap[entry.key] = _reRouteNode(entry.value, idMap);
      }
      return newMap;
    } else if (node is List) {
      return node.map((e) => _reRouteNode(e, idMap)).toList();
    } else if (node is String) {
      return _remapStepBindingString(node, idMap);
    }
    return node;
  }

  /// Creates a deep copy of a JSON map.
  static Map<String, Object?> _deepCopyMap(Map<String, Object?> original) {
    final copy = <String, Object?>{};
    for (final entry in original.entries) {
      copy[entry.key] = _deepCopyObject(entry.value);
    }
    return copy;
  }

  static Object? _deepCopyObject(Object? value) {
    if (value is Map<String, Object?>) {
      return _deepCopyMap(value);
    } else if (value is Map) {
      final stringMap = <String, Object?>{};
      for (final key in value.keys) {
        stringMap[key.toString()] = value[key];
      }
      return _deepCopyMap(stringMap);
    } else if (value is List) {
      return value.map(_deepCopyObject).toList();
    }
    return value;
  }
}
