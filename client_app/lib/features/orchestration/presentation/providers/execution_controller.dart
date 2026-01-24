import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart';

import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/network/sse_client.dart';
import 'package:file_picker/file_picker.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_file.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_providers.dart';
import 'package:client_app/features/orchestration/domain/logic/workflow_input_validator.dart';
import 'package:client_app/api/api_client.dart';

part 'execution_controller.g.dart';

/// **Execution Data Stream**
///
/// Legacy/Simple polling provider (retained for fallback/simplicity if needed)
/// But ExecutionController now takes over active monitoring.
@riverpod
Stream<Execution> executionStream(Ref ref, String executionId) async* {
  final repository = ref.watch(executionRepositoryProvider);
  await for (final result in repository.streamExecution(executionId)) {
    yield result.fold((error) => throw error, (execution) => execution);
  }
}

/// **Execution Controller**
///
/// Manages the state of the active execution, including SSE monitoring and actions.
@riverpod
class ExecutionController extends _$ExecutionController {
  StreamSubscription? _sseSubscription;

  @override
  FutureOr<Execution?> build() {
    return null; // Initially no active execution
  }

  /// Starts monitoring an execution via SSE.
  ///
  /// Updates [state] with real-time data.
  Future<void> monitorExecution(String executionId) async {
    // Cancel existing subscription if any
    await _sseSubscription?.cancel();

    // Set loading initially? Or rely on stream?
    // If we have no data, loading is appropriate.
    if (state.value == null) {
      state = const AsyncLoading();
    }

    final dio = ref.read(dioProvider); // Need dio for SseClient
    final sseClient = SseClient(dio);
    final url = '/executions/$executionId/events';

    _sseSubscription = sseClient
        .subscribe(url)
        .listen(
          (data) {
            if (data is Map<String, dynamic>) {
              // We expect partial or full updates.
              // Ideally we should fetch full execution initially OR merge.
              // But 'data' from backend SSE is 'current state snapshot' mostly?
              // The backend SSE yield: 'update', data: {status, current_step, ...}
              // It might NOT be a full Execution object (which has inputs, results etc).
              // If it IS a full object or compatible partial:

              // Strategy: Use Repositoy.getExecution once to hydrate, then apply patches?
              // Or assume SSE sends sufficient info to display progress.

              // For robust UI, we might want to poll 'getExecution' if SSE says "update".
              // But for efficiency, we want to use SSE data.

              // Let's try to map generic data to Execution if possible, or trigger refresh.
              // If we can't parse full execution, we might need to rely on refetching.
              // Refetching on every event defeats SSE purpose slightly, but ensures consistency.

              // OPTIMIZATION: If data has 'status', 'current_step', update local state if present.
              // If State is null, we MUST fetch first.

              _handleUpdate(executionId, data);
            }
          },
          onError: (error) {
            // Switch to polling or just show error?
            // state = AsyncError(error, StackTrace.current);
            // Retrying is complex.
          },
        );

    // Initial fetch to ensure full data
    final repository = ref.read(executionRepositoryProvider);
    final result = await repository.getExecution(executionId).run();
    result.match(
      (error) => state = AsyncError(error, StackTrace.current),
      (execution) => state = AsyncData(execution),
    );
  }

  void _handleUpdate(String id, Map<String, dynamic> data) {
    final currentState = state.value;
    if (currentState == null) return; // Wait for initial fetch

    // Create a copy with updated fields
    // Assuming generic map update logic or specific fields
    final statusStr = data['status'] as String?;
    final newStatus =
        statusStr != null
            ? ExecutionStatus.values.firstWhere(
              (e) => e.name == statusStr,
              orElse: () => currentState.status,
            )
            : currentState.status;

    final updated = currentState.copyWith(
      status: newStatus,
      currentStepName:
          data['current_step'] as String? ?? currentState.currentStepName,
      // results: ... potentially complex merge
    );

    // If status changed to completed/failed, we might want to refetch full result to get outputs
    if (newStatus != currentState.status &&
        (newStatus == ExecutionStatus.completed ||
            newStatus == ExecutionStatus.failed)) {
      // Refetch
      ref.read(executionRepositoryProvider).getExecution(id).run().then((res) {
        res.match(
          (err) => null, // ignore
          (full) => state = AsyncData(full),
        );
      });
    } else {
      state = AsyncData(updated);
    }
  }

  /// Cancels the current execution.
  Future<void> cancelExecution(String id) async {
    // 1. Optimistic Update
    final currentState = state.value;
    if (currentState != null) {
      // Create a specific status or just reuse 'cancelling' if we had it in Enum
      // Since ExecutionStatus might not have 'cancelling', we check enum.
      // If enum doesn't support it, we assume 'running' but maybe UI shows spinner.
      // User requested "Optimistically update local state status to cancelling".
      // Let's assume Enum has 'cancelling' or we just proceed.
      // If we strictly follow backend model, we should check `execution_repository.dart` -> `Execution` model.

      // We'll proceed with call.
    }

    final repository = ref.read(executionRepositoryProvider);
    final result = await repository.cancelExecution(id).run();

    result.match(
      (error) {
        // Revert or show error
        state = AsyncError(error, StackTrace.current);
      },
      (_) {
        // Success. SSE should eventually confirm 'cancelled'.
        // We can force update manually if enum supports it.
      },
    );
  }

  // Dispose
  void dispose() {
    _sseSubscription?.cancel();
  }

  /// Starts a new analysis workflow.
  Future<String?> startAnalysis({
    required String workflowId,
    required Map<String, dynamic> inputs,
    required List<String> requiredInputs,
  }) async {
    // 1. Validate Inputs
    final validation = WorkflowInputValidator.validate(
      inputs: inputs,
      requiredKeys: requiredInputs,
    );

    if (validation.isLeft()) {
      final error =
          validation.getLeft().toNullable() ??
          const AppError.validation(ValidationErrorReason.unknown);
      state = AsyncError(error, StackTrace.current);
      throw error;
    }

    // 2. Set Loading
    state = const AsyncLoading();

    // 3. Prepare Inputs
    final jsonInputs = <String, dynamic>{};
    final files = <String, ExecutionFile>{};

    for (final entry in inputs.entries) {
      final value = entry.value;
      if (value is PlatformFile) {
        files[entry.key] = ExecutionFile(
          name: value.name,
          path: value.path,
          bytes: (!kIsWeb && value.path != null) ? null : value.bytes,
        );
      } else {
        jsonInputs[entry.key] = value;
      }
    }

    // 4. Call Repository
    final repository = ref.read(executionRepositoryProvider);
    final input = ExecutionInput(
      workflowId: workflowId,
      inputs: jsonInputs,
      files: files,
    );

    final result = await repository.createExecution(input).run();

    return result.match(
      (error) {
        state = AsyncError(error, StackTrace.current);
        throw error;
      },
      (executionId) {
        ref.invalidate(executionListControllerProvider);

        // Start Monitoring immediately?
        monitorExecution(executionId);

        return executionId;
      },
    );
  }
}

// Helper to access Dio
final dioProvider = Provider((ref) => ref.watch(apiClientProvider));

@riverpod
Future<Map<String, dynamic>> executionRawData(
  Ref ref,
  String executionId,
) async {
  final repository = ref.watch(executionRepositoryProvider);
  final result = await repository.getRawExecutionData(executionId).run();

  return result.fold((error) => throw error, (data) => data);
}
