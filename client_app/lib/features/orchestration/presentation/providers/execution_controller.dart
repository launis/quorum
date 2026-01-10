import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:fpdart/fpdart.dart';

import 'package:client_app/core/error/app_error.dart';
import 'package:file_picker/file_picker.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_file.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_providers.dart';

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
  Future<String?> startAnalysis({
    required String workflowId,
    required Map<String, dynamic> inputs,
  }) async {
    // 1. Validate Inputs (Client-side fail-fast)
    final validation = _validateInputs(inputs, workflowId);
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
        files[entry.key] = ExecutionFile(
          name: value.name,
          path: value.path, // May be null on Web
          bytes: value.bytes, // May be null on IO (unless forced)
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

  /// Validates inputs.
  ///
  /// Mirrors Backend Logic (`GUARD 2` in `execution_router.py`):
  /// - If workflow ID contains "audit", requires specific evidence files/fields.
  /// - Checks that required fields are not empty or null.
  Either<AppError, Unit> _validateInputs(
    Map<String, dynamic> inputs,
    String workflowId,
  ) {
    // 1. Audit Workflow Specific Validation
    if (workflowId.toLowerCase().contains('audit')) {
      final requiredFields = [
        'history_text',
        'product_text',
        'reflection_text',
      ];
      final missing = <String>[];

      for (final field in requiredFields) {
        if (!inputs.containsKey(field)) {
          missing.add(field);
          continue;
        }

        final value = inputs[field];
        // If it's a file (PlatformFile), we assume it's valid if present.
        // If it's a string, it must not be empty.
        if (value is String && value.trim().isEmpty) {
          missing.add(field);
        } else if (value == null) {
          missing.add(field);
        }
      }

      if (missing.isNotEmpty) {
        // Return structured error
        return Left(AppError.validationMissing(missing));
      }
    }

    // 2. Generic Validation (if any)
    // Ensure no null keys or totally empty inputs if required by other workflows
    if (inputs.isEmpty) {
      return const Left(AppError.validation(ValidationErrorReason.emptyInput));
    }

    return const Right(unit);
  }
}
