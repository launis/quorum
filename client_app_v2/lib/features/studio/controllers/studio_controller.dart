import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/studio_client.dart';

// --- Providers ---

/// Manages the state of all Studio Matrices.
final matricesControllerProvider =
    AsyncNotifierProvider<MatricesController, List<Map<String, dynamic>>>(
      MatricesController.new,
    );

/// Manages the state of all Studio Workflows (DAGs).
final workflowsControllerProvider =
    AsyncNotifierProvider<WorkflowsController, List<Map<String, dynamic>>>(
      WorkflowsController.new,
    );

/// Manages the state of all Studio TaskBlueprints.
final taskBlueprintsControllerProvider =
    AsyncNotifierProvider<TaskBlueprintsController, List<Map<String, dynamic>>>(
      TaskBlueprintsController.new,
    );

// --- Controllers ---

/// Controller managing Studio Matrices strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class MatricesController extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    return _fetchMatrices();
  }

  Future<List<Map<String, dynamic>>> _fetchMatrices() async {
    final client = ref.read(studioClientProvider);
    return client.getMatrices();
  }

  /// Refreshes the matrix list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newMatrices = await _fetchMatrices();
      state = AsyncValue.data(newMatrices);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Saves a matrix utilizing Optimistic Updates.
  Future<void> saveMatrix(String id, Map<String, dynamic> payload) async {
    final previousState = state;

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedMatrix = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedMatrix;
      } else {
        currentList.add(updatedMatrix);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call (Append-Only)
      final client = ref.read(studioClientProvider);
      final verifiedMatrix = await client.saveMatrix(id, payload);

      // 3. Confirm with Actual Data (in case backend added fields like `version_id`)
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedMatrix;
          state = AsyncValue.data(currentList);
        }
      }
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      // Re-throw to allow view layer to show snackbar
      throw Exception('Failed to save matrix: $e');
    }
  }
}

/// Controller managing Studio Workflows (DAGs) strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class WorkflowsController extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
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
  Future<void> saveWorkflow(String id, Map<String, dynamic> payload) async {
    final previousState = state;

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
      }
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      throw Exception('Failed to save workflow: $e');
    }
  }
}

/// Controller managing Studio Task Blueprints strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class TaskBlueprintsController
    extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    return _fetchTaskBlueprints();
  }

  Future<List<Map<String, dynamic>>> _fetchTaskBlueprints() async {
    final client = ref.read(studioClientProvider);
    return client.getTaskBlueprints();
  }

  /// Refreshes the task blueprints list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newBlueprints = await _fetchTaskBlueprints();
      state = AsyncValue.data(newBlueprints);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Saves a task blueprint utilizing Optimistic Updates.
  Future<void> saveTaskBlueprint(
    String id,
    Map<String, dynamic> payload,
  ) async {
    final previousState = state;

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedBlueprint = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedBlueprint;
      } else {
        currentList.add(updatedBlueprint);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call (Append-Only)
      final client = ref.read(studioClientProvider);
      final verifiedBlueprint = await client.saveTaskBlueprint(id, payload);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedBlueprint;
          state = AsyncValue.data(currentList);
        }
      }
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      throw Exception('Failed to save task blueprint: $e');
    }
  }
}
