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

    // Set loading if we have no data
    if (state.value == null) {
      state = const AsyncLoading();
    }

    // Initial fetch to ensure full data immediately (Fixes UI freeze)
    final repository = ref.read(executionRepositoryProvider);
    final result = await repository.getExecution(executionId).run();
    
    result.match(
      (error) => state = AsyncError(error, StackTrace.current),
      (execution) => state = AsyncData(execution),
    );

    final dio = ref.read(dioProvider);
    final url = '/executions/$executionId/events';

    try {
      final stream = SseClient.connect<Execution>(
        url: url,
        parser: (json) => Execution.fromJson(json),
        dio: dio,
      );

      _sseSubscription = stream.listen(
        (execution) {
          state = AsyncData(execution);
        },
        onError: (error) {
          // Determine if we should set error state or just log
          // If it's the only source of truth, error state is appropriate.
          state = AsyncError(error, StackTrace.current);
        },
      );
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }

  /// Cancels the current execution.
  Future<void> cancelExecution(String id) async {
    final repository = ref.read(executionRepositoryProvider);
    final result = await repository.cancelExecution(id).run();

    result.match(
      (error) {
        state = AsyncError(error, StackTrace.current);
      },
      (_) {
        // Success. SSE should eventually confirm 'cancelled'.
      },
    );
  }

  /// Deletes an execution permanently.
  Future<void> deleteExecution(String id) async {
    final repository = ref.read(executionRepositoryProvider);
    final result = await repository.deleteExecution(id).run();

    result.match(
      (error) => state = AsyncError(error, StackTrace.current),
      (_) {
        // Invalidate list to remove the item from grid
        ref.invalidate(executionListControllerProvider);
        
        // If we deleted the active one, clear state
        if (state.value?.id == id) {
          state = const AsyncData(null);
        }
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
      
      debugPrint('[ExecutionController] Validation failed: $error');
      
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

        // Start Monitoring immediately
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
