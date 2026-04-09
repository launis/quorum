import 'dart:async';
import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/models/workflow.dart';

import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';

part 'studio_controller.g.dart';

// --- Providers ---

/// Fetches a single Workflow natively by ID
@riverpod
Future<Workflow> workflowById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  final rawData = await client.getWorkflow(id);
  final str = jsonEncode(rawData);
  return Workflow.parseInBackground(str);
}

/// Fetches a single Step natively by ID
@riverpod
Future<NodeStrategy> stepById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  final rawData = await client.getStep(id);
  final str = jsonEncode(rawData);
  return Isolate.run(
    () => NodeStrategy.fromJson(jsonDecode(str) as Map<String, dynamic>),
  );
}

// --- Form State (Flat MVC) ---

@riverpod
class WorkflowForm extends _$WorkflowForm {
  @override
  FutureOr<Workflow> build(String configId) async {
    final block = await ref.watch(workflowByIdProvider(configId).future);
    return block.copyWith();
  }

  void forceRebuild(Workflow block) {
    state = AsyncData(block);
  }

  Future<void> submit(Workflow block) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final idToSave = block.id.isEmpty ? configId : block.id;
      if (idToSave.isEmpty || idToSave == 'new') {
        throw AppException.validation("Workflow ID is required");
      }

      await ref
          .read(workflowsControllerProvider.notifier)
          .saveWorkflow(idToSave, block);
      return block;
    });
  }
}

@riverpod
class StepForm extends _$StepForm {
  @override
  FutureOr<NodeStrategy> build(String configId) async {
    final block = await ref.watch(stepByIdProvider(configId).future);

    // Strict Dart 3 exhaustive matching - Freezed maps are BANNED
    switch (block) {
      case NodeStrategyLlm l:
        return l.copyWith();
      case NodeStrategyLogic l:
        return l.copyWith();
    }
  }

  void forceRebuild(NodeStrategy block) {
    state = AsyncData(block);
  }

  Future<void> submit(NodeStrategy block) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final idToSave = block.id.isEmpty ? configId : block.id;
      if (idToSave.isEmpty || idToSave == 'new') {
        throw AppException.validation("Step ID is required");
      }

      await ref
          .read(stepsControllerProvider.notifier)
          .saveStep(idToSave, block);
      return block;
    });
  }
}

// --- Controllers ---

/// Controller managing Studio Workflows (DAGs) strictly using `Workflow` mapped domain model.
/// Implements Optimistic UI principles where possible.
@riverpod
class WorkflowsController extends _$WorkflowsController {
  @override
  FutureOr<List<Workflow>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchWorkflows();
  }

  Future<List<Workflow>> _fetchWorkflows() async {
    final client = ref.read(studioClientProvider);
    final rawData = await client.getWorkflows();
    return Workflow.parseListInBackground(rawData);
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
  Future<Workflow> saveWorkflow(String id, Workflow payload) async {
    final previousState = state;
    Workflow returnData = payload.copyWith(id: id);

    // 1. Optimistic Update (0ms Illusion)
    if (state.hasValue && state.value != null) {
      final currentList = List<Workflow>.from(state.value!);
      final index = currentList.indexWhere((w) => w.id == id);

      if (index >= 0) {
        currentList[index] = returnData;
      } else {
        currentList.add(returnData);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.saveWorkflow(id, returnData.toJson());
      final str = jsonEncode(rawResponse);
      final verifiedWorkflow = await Workflow.parseInBackground(str);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Workflow>.from(state.value!);
        final index = currentList.indexWhere((w) => w.id == id);
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
        final currentList = List<Workflow>.from(state.value!);
        currentList.removeWhere((w) => w.id == id);
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
  Future<Workflow> cloneWorkflow(String id) async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.cloneWorkflow(id);
      final str = jsonEncode(rawResponse);
      final clonedWorkflow = await Workflow.parseInBackground(str);

      // Append cloned workflow to local state instantly
      if (state.hasValue && state.value != null) {
        final currentList = List<Workflow>.from(state.value!);
        currentList.insert(0, clonedWorkflow);
        state = AsyncValue.data(currentList);
      }

      // Proactively refresh output profiles since cloning a workflow also clones its bound output profiles!
      ref.read(outputProfilesControllerProvider.notifier).refresh();

      return clonedWorkflow;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('WorkflowsController', 'Clone failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Creates a draft workflow via the backend SSoT.
  Future<Workflow> createWorkflowDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.createWorkflowDraft();
      final str = jsonEncode(rawResponse);
      final draftWorkflow = await Workflow.parseInBackground(str);

      if (state.hasValue && state.value != null) {
        final currentList = List<Workflow>.from(state.value!);
        currentList.insert(0, draftWorkflow);
        state = AsyncValue.data(currentList);
      }
      return draftWorkflow;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('WorkflowsController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) throw e.error!;
      throw AppException.unknown(e);
    }
  }

  /// Simulates a workflow on the backend without saving it.
  Future<Map<String, dynamic>> simulateWorkflow(Workflow payload) async {
    try {
      final client = ref.read(studioClientProvider);
      return await client.simulateWorkflow(payload.toJson());
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

/// Controller managing Studio Steps strictly using `NodeStrategy` mapping.
/// Implements Optimistic UI principles where possible.
@riverpod
class StepsController extends _$StepsController {
  @override
  FutureOr<List<NodeStrategy>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchSteps();
  }

  Future<List<NodeStrategy>> _fetchSteps() async {
    final client = ref.read(studioClientProvider);
    final rawData = await client.getSteps();
    // Isolate Mandate: Zero-Latency
    return Isolate.run(() {
      return rawData.map((e) => NodeStrategy.fromJson(e)).toList();
    });
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
  Future<NodeStrategy> saveStep(String id, NodeStrategy payload) async {
    final previousState = state;
    NodeStrategy returnData = payload;

    // Strict pattern matching to achieve copyWith injected parameter
    switch (payload) {
      case NodeStrategyLlm l:
        returnData = l.copyWith(id: id);
        break;
      case NodeStrategyLogic l:
        returnData = l.copyWith(id: id);
        break;
    }

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<NodeStrategy>.from(state.value!);
      final index = currentList.indexWhere((m) {
        if (m is NodeStrategyLlm) return m.id == id;
        if (m is NodeStrategyLogic) return m.id == id;
        return false;
      });

      if (index >= 0) {
        currentList[index] = returnData;
      } else {
        currentList.add(returnData);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call (Append-Only)
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.saveStep(id, returnData.toJson());
      final str = jsonEncode(rawResponse);
      final verifiedStep = await Isolate.run(
        () => NodeStrategy.fromJson(jsonDecode(str) as Map<String, dynamic>),
      );

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<NodeStrategy>.from(state.value!);
        final index = currentList.indexWhere((m) {
          if (m is NodeStrategyLlm) return m.id == id;
          if (m is NodeStrategyLogic) return m.id == id;
          return false;
        });

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
        final currentList = List<NodeStrategy>.from(state.value!);
        currentList.removeWhere((m) {
          if (m is NodeStrategyLlm) return m.id == id;
          if (m is NodeStrategyLogic) return m.id == id;
          return false;
        });
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
  Future<NodeStrategy> cloneStep(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.cloneStep(id);
      final str = jsonEncode(rawResponse);
      final clonedStep = await Isolate.run(
        () => NodeStrategy.fromJson(jsonDecode(str) as Map<String, dynamic>),
      );

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<NodeStrategy>.from(state.value!);
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

  /// Creates a draft step via the backend SSoT.
  Future<NodeStrategy> createStepDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.createStepDraft();

      // Isolate Mandate: Zero-Latency
      final draftStep = await Isolate.run(() {
        return NodeStrategy.fromJson(rawResponse);
      });

      if (state.hasValue && state.value != null) {
        final currentList = List<NodeStrategy>.from(state.value!);
        currentList.insert(0, draftStep);
        state = AsyncValue.data(currentList);
      }
      return draftStep;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('StepsController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) throw e.error!;
      throw AppException.unknown(e);
    }
  }

  /// Simulates a step on the backend without saving it.
  Future<Map<String, dynamic>> simulateStep(NodeStrategy payload) async {
    try {
      final client = ref.read(studioClientProvider);
      return await client.simulateStep(payload.toJson());
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
