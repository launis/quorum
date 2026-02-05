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
/// Real-time monitoring of a specific execution via SSE.
/// Used by Detailed View.
@riverpod
Stream<Execution> executionStream(Ref ref, String executionId) {
  final repository = ref.watch(executionRepositoryProvider);
  return repository.streamExecution(executionId);
}

/// **Execution Actions Controller**
///
/// Manages actions like Start, Cancel, Delete.
/// Does NOT hold the active execution state (use [executionStream] for that).
@riverpod
class ExecutionController extends _$ExecutionController {
  
  @override
  FutureOr<void> build() {
    // Stateless controller for actions
    return null;
  }

  /// Cancels the current execution.
  Future<void> cancelExecution(String id) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(executionRepositoryProvider).cancelExecution(id).run();
    });
  }

  /// Deletes an execution permanently.
  Future<void> deleteExecution(String id) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final result = await ref.read(executionRepositoryProvider).deleteExecution(id).run();
      
      result.fold(
        (error) {
          // If 404, we consider it already deleted
          // However, AppError might need inspection. For now, strictly throw.
          // Ideally: if (error is NotFound) return;
          throw error;
        },
        (_) => null,
      );
      
      // Invalidate list to remove the item from grid
      ref.invalidate(executionListControllerProvider);
    });
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

    // 4. Call Repository via Guard
    final repository = ref.read(executionRepositoryProvider);
    final input = ExecutionInput(
      workflowId: workflowId,
      inputs: jsonInputs,
      files: files,
    );
    
    // We handle the result manually because we need to return the ID
    final result = await repository.createExecution(input).run();

    return result.match(
      (error) {
        state = AsyncError(error, StackTrace.current);
        throw error;
      },
      (executionId) {
        state = const AsyncData(null);
        ref.invalidate(executionListControllerProvider);
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
