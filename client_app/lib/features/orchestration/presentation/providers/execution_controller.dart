import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter/foundation.dart';

import 'package:client_app/core/error/app_error.dart';
import 'package:file_picker/file_picker.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_file.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_providers.dart';
import 'package:client_app/features/orchestration/domain/logic/workflow_input_validator.dart';

part 'execution_controller.g.dart';

/// **Execution Data Stream**
///
/// Provides real-time updates for a specific execution ID.
/// Automatically handles polling and lifecycle via [ExecutionRepository.streamExecution].
@riverpod
Stream<Execution> executionStream(Ref ref, String executionId) async* {
  final repository = ref.watch(executionRepositoryProvider);

  // Subscribe to the repository stream that returns Either<AppError, Execution>
  // We unwrap the Either to throw errors so Riverpod handles them as AsyncError
  await for (final result in repository.streamExecution(executionId)) {
    yield result.fold((error) => throw error, (execution) => execution);
  }
}

/// **Execution Controller (Actions)**
///
/// Manages actions like `startAnalysis`.
/// DOES NOT manage the state of the active execution (use [executionStreamProvider]).
@riverpod
class ExecutionController extends _$ExecutionController {
  @override
  FutureOr<void> build() {
    // Stateless controller pattern (initially idle)
  }

  /// Starts a new analysis workflow.
  ///
  /// **Validation Logic**:
  /// Checks for presence of required text fields.
  /// Starts a new analysis workflow.
  ///
  /// **Validation Logic**:
  /// Validates [inputs] against the provided [requiredInputs] keys using [WorkflowInputValidator].
  Future<String?> startAnalysis({
    required String workflowId,
    required Map<String, dynamic> inputs,
    required List<String> requiredInputs,
  }) async {
    // 1. Validate Inputs (Client-side fail-fast)
    final validation = WorkflowInputValidator.validate(
      inputs: inputs,
      requiredKeys: requiredInputs,
    );

    if (validation.isLeft()) {
      // Extract the specific AppError
      final error =
          validation.getLeft().toNullable() ??
          const AppError.validation(ValidationErrorReason.unknown);

      // Update state and throw so UI can show it
      state = AsyncError(error, StackTrace.current);
      throw error;
    }

    // 2. Set Loading
    state = const AsyncLoading();

    // 3. Prepare Inputs & Files
    final jsonInputs = <String, dynamic>{};
    final files = <String, ExecutionFile>{};

    for (final entry in inputs.entries) {
      final value = entry.value;
      if (value is PlatformFile) {
        // Efficient File Handling (OOM Prevention):
        // On IO (Mobile/Desktop), we prefer 'path' and avoid loading 'bytes'.
        // On Web, 'path' is useless (or causes crash if used in MultipartFile.fromFile), so we MUST use 'bytes'.
        files[entry.key] = ExecutionFile(
          name: value.name,
          path: value.path,
          // Only clear bytes if we are NOT on web AND we have a path.
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

    // 5. Handle Result
    return result.match(
      (error) {
        state = AsyncError(error, StackTrace.current);
        throw error;
      },
      (executionId) {
        // Invalidate the list so the dashboard updates
        ref.invalidate(executionListControllerProvider);

        // Reset state to success (void)
        state = const AsyncData(null);

        return executionId;
      },
    );
  }
}

/// **Execution Raw Data Provider**
///
/// Fetches complete raw execution data from the /raw API endpoint.
/// This includes all agent outputs, hook outputs, and timing information.
@riverpod
Future<Map<String, dynamic>> executionRawData(Ref ref, String executionId) async {
  final repository = ref.watch(executionRepositoryProvider);
  final result = await repository.getRawExecutionData(executionId).run();
  
  return result.fold(
    (error) => throw error,
    (data) => data,
  );
}
