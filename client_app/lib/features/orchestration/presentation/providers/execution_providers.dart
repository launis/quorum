import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';

part 'execution_providers.g.dart';

/// Controller for the Orchestration Dashboard.
///
/// Manages the state of the execution list.
/// Uses strict Riverpod 3.0 AsyncNotifier pattern.
@riverpod
class ExecutionListController extends _$ExecutionListController {
  @override
  Future<List<Execution>> build() async {
    final repository = ref.watch(executionRepositoryProvider);

    // Fetch data using fpdart TaskEither
    final result = await repository.fetchExecutions().run();

    // strict logic: Unfold Either to standard Dart Control Flow
    return result.fold((error) => throw error, (executions) {
      // "Smart Polling": If any execution is active, refresh list every 5s.
      final hasActive = executions.any(
        (e) =>
            e.status == ExecutionStatus.running ||
            e.status == ExecutionStatus.pending,
      );

      if (hasActive) {
        final timer = Timer(const Duration(seconds: 5), () {
          ref.invalidateSelf();
        });
        ref.onDispose(timer.cancel);
      }

      return executions;
    });
  }

  /// Forces a refresh of the dashboard list.
  void refreshList() {
    ref.invalidateSelf();
  }
}
