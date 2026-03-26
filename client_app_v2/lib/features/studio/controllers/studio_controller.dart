import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';

// --- Providers ---

/// Manages the state of all Studio Workflows (DAGs).
final workflowsControllerProvider =
    AsyncNotifierProvider<WorkflowsController, List<Map<String, dynamic>>>(
      WorkflowsController.new,
    );

/// Manages the state of all Studio Steps.
final stepsControllerProvider =
    AsyncNotifierProvider<StepsController, List<Map<String, dynamic>>>(
      StepsController.new,
    );

/// Fetches a single Workflow natively by ID
final workflowByIdProvider = FutureProvider.autoDispose
    .family<Map<String, dynamic>, String>((ref, id) async {
      final client = ref.watch(studioClientProvider);
      return client.getWorkflow(id);
    });

// --- Controllers ---

/// Controller managing Studio Workflows (DAGs) strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class WorkflowsController extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    ref.cacheFor(const Duration(minutes: 3));
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
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
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
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to save workflow: $e');
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
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to delete workflow: $e');
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
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to clone workflow: $e');
    }
  }

  /// Simulates a workflow on the backend without saving it.
  Future<Map<String, dynamic>> simulateWorkflow(
    Map<String, dynamic> payload,
  ) async {
    try {
      final client = ref.read(studioClientProvider);
      return await client.simulateWorkflow(payload);
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to simulate workflow: $e');
    }
  }
}

/// Controller managing Studio Steps strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class StepsController extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    ref.cacheFor(const Duration(minutes: 3));
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
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
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
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to save step: $e');
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
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to delete step: $e');
    }
  }

  /// Simulates a step on the backend without saving it.
  Future<Map<String, dynamic>> simulateStep(
    Map<String, dynamic> payload,
  ) async {
    try {
      final client = ref.read(studioClientProvider);
      return await client.simulateStep(payload);
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to simulate step: $e');
    }
  }
}
