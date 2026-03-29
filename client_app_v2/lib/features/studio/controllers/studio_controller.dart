import 'dart:async';
import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'studio_controller.g.dart';

// --- Providers ---

/// Fetches a single Workflow natively by ID
@riverpod
Future<Map<String, dynamic>> workflowById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return client.getWorkflow(id);
}

/// Fetches a single Step natively by ID
@riverpod
Future<Map<String, dynamic>> stepById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return client.getStep(id);
}

// --- Form State (Flat MVC) ---

@riverpod
class WorkflowForm extends _$WorkflowForm {
  @override
  FutureOr<Map<String, dynamic>> build(String configId) async {
    if (configId == 'new') {
      return Isolate.run(
        () => {
          'id': '',
          'slug': '',
          'expected_inputs': [],
          'steps': [],
          'output_profiles': <String, dynamic>{},
        },
      );
    }

    final rawData = await ref.watch(workflowByIdProvider(configId).future);
    final str = jsonEncode(rawData);
    var copy = await Isolate.run(() => jsonDecode(str) as Map<String, dynamic>);

    if (!copy.containsKey('expected_inputs')) copy['expected_inputs'] = [];
    if (!copy.containsKey('steps')) copy['steps'] = [];
    // Legacy keys cleaned if present
    copy.remove('render_blueprints');
    copy.remove('render_blueprint');
    copy.remove('output_mapping');

    if (!copy.containsKey('output_profiles')) {
      copy['output_profiles'] = <String, dynamic>{};
    }

    return copy;
  }

  void forceRebuild() {
    final payload = state.value;
    if (payload != null) {
      state = AsyncData(Map<String, dynamic>.from(payload));
    }
  }

  Future<void> submit(Map<String, dynamic> updatedData) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final idToSave = updatedData['id'] as String? ?? configId;
      if (idToSave.isEmpty || idToSave == 'new')
        throw AppException.validation("Workflow ID is required");

      await ref
          .read(workflowsControllerProvider.notifier)
          .saveWorkflow(idToSave, updatedData);
      return updatedData;
    });
  }
}

@riverpod
class StepForm extends _$StepForm {
  @override
  FutureOr<Map<String, dynamic>> build(String configId) async {
    if (configId == 'new') {
      return Isolate.run(
        () => {
          'id': '',
          'slug': '',
          'label': {'fi': 'Uusi Steppi', 'en': 'New Step'},
          'agent_type': 'general_executive',
          'prompt_blocks': [],
          'enabled': true,
        },
      );
    }

    final rawData = await ref.watch(stepByIdProvider(configId).future);
    final str = jsonEncode(rawData);
    return Isolate.run(() => jsonDecode(str) as Map<String, dynamic>);
  }

  void forceRebuild() {
    final payload = state.value;
    if (payload != null) {
      state = AsyncData(Map<String, dynamic>.from(payload));
    }
  }

  Future<void> submit(Map<String, dynamic> updatedData) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final idToSave = updatedData['id'] as String? ?? configId;
      if (idToSave.isEmpty || idToSave == 'new')
        throw AppException.validation("Step ID is required");

      await ref
          .read(stepsControllerProvider.notifier)
          .saveStep(idToSave, updatedData);
      return updatedData;
    });
  }
}

// --- Controllers ---

/// Controller managing Studio Workflows (DAGs) strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
@riverpod
class WorkflowsController extends _$WorkflowsController {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchWorkflows();
  }

  Future<List<Map<String, dynamic>>> _fetchWorkflows() async {
    final client = ref.read(studioClientProvider);
    return client.getWorkflows();
  }

  /// Refreshes the workflow list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newWorkflows = await _fetchWorkflows();
      state = AsyncValue.data(newWorkflows);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('WorkflowsController', 'Refresh failed', e, st);
      state = AsyncValue.error(e, st);
    }
  }

  /// Saves a workflow utilizing Optimistic Updates.
  Future<Map<String, dynamic>> saveWorkflow(
    String id,
    Map<String, dynamic> payload,
  ) async {
    final previousState = state;

    // Pluck orphaned questionnaire definitions to satisfy Pydantic Strict Fail-Fast
    if (payload['expected_inputs'] is List) {
      for (var inputDef in payload['expected_inputs']) {
        if (inputDef is Map) {
          final modes = inputDef['input_modes'] ?? [];
          if (modes is List && !modes.contains('questionnaire')) {
            inputDef.remove('questionnaire_definition');
          }
        }
      }
    }

    Map<String, dynamic> returnData = {...payload, 'id': id};

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((w) => w['id'] == id);

      final updatedWorkflow = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedWorkflow;
      } else {
        currentList.add(updatedWorkflow);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final verifiedWorkflow = await client.saveWorkflow(id, payload);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((w) => w['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedWorkflow;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedWorkflow;
      }
      return returnData;
    } catch (e, st) {
      // 4. Rollback on Failure
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('WorkflowsController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes a workflow. Throwing AppException on orphan rejection (RESOURCE_IN_USE)
  Future<void> deleteWorkflow(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteWorkflow(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.removeWhere((w) => w['id'] == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('WorkflowsController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones a workflow using the backend's Shallow-Deep Copy constraint.
  Future<Map<String, dynamic>> cloneWorkflow(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      final clonedWorkflow = await client.cloneWorkflow(id);

      // Append cloned workflow to local state instantly
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.insert(0, clonedWorkflow);
        state = AsyncValue.data(currentList);
      }
      return clonedWorkflow;
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('WorkflowsController', 'Clone failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Simulates a workflow on the backend without saving it.
  Future<Map<String, dynamic>> simulateWorkflow(
    Map<String, dynamic> payload,
  ) async {
    try {
      final client = ref.read(studioClientProvider);
      return await client.simulateWorkflow(payload);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('WorkflowsController', 'Simulate failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }
}

/// Controller managing Studio Steps strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
@riverpod
class StepsController extends _$StepsController {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchSteps();
  }

  Future<List<Map<String, dynamic>>> _fetchSteps() async {
    final client = ref.read(studioClientProvider);
    return client.getSteps();
  }

  /// Refreshes the steps list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newSteps = await _fetchSteps();
      state = AsyncValue.data(newSteps);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('StepsController', 'Refresh failed', e, st);
      state = AsyncValue.error(e, st);
    }
  }

  /// Saves a step utilizing Optimistic Updates.
  Future<Map<String, dynamic>> saveStep(
    String id,
    Map<String, dynamic> payload,
  ) async {
    final previousState = state;
    Map<String, dynamic> returnData = {...payload, 'id': id};

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedStep = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedStep;
      } else {
        currentList.add(updatedStep);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call (Append-Only)
      final client = ref.read(studioClientProvider);
      final verifiedStep = await client.saveStep(id, payload);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedStep;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedStep;
      }
      return returnData;
    } catch (e, st) {
      // 4. Rollback on Failure
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('StepsController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes a step. Throwing AppException on orphan rejection
  Future<void> deleteStep(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteStep(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.removeWhere((m) => m['id'] == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('StepsController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones a step utilizing Optimistic UI.
  Future<Map<String, dynamic>> cloneStep(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final clonedStep = await client.cloneStep(id);

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.add(clonedStep);
        state = AsyncValue.data(currentList);
      }
      return clonedStep;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('StepsController', 'Clone failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Simulates a step on the backend without saving it.
  Future<Map<String, dynamic>> simulateStep(
    Map<String, dynamic> payload,
  ) async {
    try {
      final client = ref.read(studioClientProvider);
      return await client.simulateStep(payload);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('StepsController', 'Simulate failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }
}
