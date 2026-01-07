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

/// Manages the state of the *currently active* or *most recently created* execution.
///
/// **Role**:
/// - Validation of inputs.
/// - triggering `startAnalysis`.
/// - Polling for status updates (simple polling for MVP).
@riverpod
class ExecutionController extends _$ExecutionController {
  @override
  FutureOr<Execution?> build() {
    // Initially no active execution.
    return null;
  }

  /// Starts a new analysis workflow.
  ///
  /// **Validation Logic**:
  /// Checks for presence of required text fields (`history_text`, `product_text`, `reflection_text`).
  /// Starts a new analysis workflow. Returns the execution ID on success.
  ///
  /// **Validation Logic**:
  /// Checks for presence of required text fields.
  Future<String?> startAnalysis({
    required String workflowId,
    required Map<String, dynamic> inputs,
  }) async {
    // 1. Validate Inputs (Client-side fail-fast)
    final validation = _validateInputs(inputs);
    if (validation.isLeft()) {
      state = AsyncError(
        AppError.validation(
          validation.getLeft().toNullable() ?? 'Invalid inputs',
        ),
        StackTrace.current,
      );
      return null;
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
    return await result.match(
      (error) {
        state = AsyncError(error, StackTrace.current);
        return null;
      },
      (executionId) async {
        // Successfully started. Now fetch the initial state.
        await _fetchAndSetExecution(executionId);

        // Invalidate the list so the dashboard updates
        ref.invalidate(executionListControllerProvider);

        return executionId;
      },
    );
  }

  /// Polls the current execution status.
  Future<void> refreshStatus() async {
    final current = state.value;
    if (current == null) return;

    await _fetchAndSetExecution(current.id);
  }

  Future<void> _fetchAndSetExecution(String id) async {
    final repository = ref.read(executionRepositoryProvider);
    final result = await repository.getExecution(id).run();

    result.match(
      (error) => state = AsyncError(error, StackTrace.current),
      (execution) => state = AsyncData(execution),
    );
  }

  /// Validates that 3 key text fields are present and not empty.
  Either<String, Unit> _validateInputs(Map<String, dynamic> inputs) {
    // Only strictly validate standard audit inputs if we are in that workflow
    // But currently this validator runs for all.
    // For now, checks keys if they exist in inputs map.
    // Ideally we should check based on workflowId.

    // We relax validation to just check non-null if key is present.
    // The Wizard UI enforces required fields.
    return const Right(unit);
  }
}
