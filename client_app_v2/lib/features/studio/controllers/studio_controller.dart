import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';

// --- Providers ---

/// Manages the state of all Studio PromptBlocks.
final promptBlocksControllerProvider =
    AsyncNotifierProvider<PromptBlocksController, List<Map<String, dynamic>>>(
      PromptBlocksController.new,
    );

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

// --- Controllers ---

/// Controller managing Studio PromptBlocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class PromptBlocksController extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    // SWR Strategy for List Views: Keep alive so navigation back is instant.
    // If it gets disposed intentionally or app memory is low, 
    // it will be cached for 3 minutes before total garbage collection.
    ref.cacheFor(const Duration(minutes: 3));
    return _fetchPromptBlocks();
  }

  Future<List<Map<String, dynamic>>> _fetchPromptBlocks() async {
    final client = ref.read(studioClientProvider);
    return client.getPromptBlocks();
  }

  /// Refreshes the prompt blocks list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newPromptBlocks = await _fetchPromptBlocks();
      state = AsyncValue.data(newPromptBlocks);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Saves a prompt block utilizing Optimistic Updates.
  Future<Map<String, dynamic>> savePromptBlock(String id, Map<String, dynamic> payload) async {
    final previousState = state;
    Map<String, dynamic> returnData = {...payload, 'id': id};

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedPromptBlock = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedPromptBlock;
      } else {
        currentList.add(updatedPromptBlock);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call (Append-Only)
      final client = ref.read(studioClientProvider);
      final verifiedPromptBlock = await client.savePromptBlock(id, payload);

      // 3. Confirm with Actual Data (in case backend added fields like `version_id`)
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedPromptBlock;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedPromptBlock;
      }
      return returnData;
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      // Re-throw to allow view layer to show snackbar
      throw Exception('Failed to save prompt block: $e');
    }
  }

  /// Deletes a prompt block. Throwing AppException on orphan rejection (RESOURCE_IN_USE)
  Future<void> deletePromptBlock(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deletePromptBlock(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.removeWhere((m) => m['id'] == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to delete prompt block: $e');
    }
  }
}

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
  Future<Map<String, dynamic>> saveWorkflow(String id, Map<String, dynamic> payload) async {
    final previousState = state;
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
  Future<Map<String, dynamic>> saveStep(String id, Map<String, dynamic> payload) async {
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
}
