import 'dart:async';

import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflow_execution_provider.g.dart';

/// Manages the state of the active workflow execution.
@riverpod
class WorkflowExecution extends _$WorkflowExecution {
  @override
  AsyncValue<Execution?> build() {
    return const AsyncValue.data(null);
  }

  /// Starts a new execution and begins polling for updates.
  Future<void> startExecution(ExecutionInput input) async {
    state = const AsyncValue.loading();

    // 1. Create Execution
    final createResult =
        await ref
            .read(executionRepositoryProvider)
            .createExecution(input)
            .run();

    createResult.fold(
      (error) {
        state = AsyncValue.error(error, StackTrace.current);
      },
      (executionId) {
        // 2. Start Polling
        // We set the state to "loading" (or specialized status) with the ID if we had the object,
        // but getting the full object requires a fetch.
        // Let's immediately poll/stream.
        _streamUpdates(executionId);
      },
    );
  }

  /// Polls the execution status until terminal.
  void _streamUpdates(String executionId) {
    // Listen to the stream from repository
    final stream = ref
        .read(executionRepositoryProvider)
        .streamExecution(executionId);

    // Cancel any previous subscription if we were managing one manually,
    // but here we just update state on each event.
    // Note: This subscription will technically run "outside" the build lifecycle
    // unless we bind it.
    // Valid Pattern: Use `await for` inside a method if we want to block,
    // or listen and update state.

    // Better pattern for AsyncNotifier:
    // Simply update state as data arrives.

    // ignore: avoid_types_on_closure_parameters
    final subscription = stream.listen(
      (execution) {
        state = AsyncValue.data(execution);
      },
      onError: (Object error, StackTrace stackTrace) {
        state = AsyncValue.error(error, stackTrace);
      },
    );

    // Ensure subscription is cancelled if the provider is disposed or rebuilt
    ref.onDispose(() {
      subscription.cancel();
    });
  }

  /// Resets the state to initial (null).
  void reset() {
    state = const AsyncValue.data(null);
  }
}
