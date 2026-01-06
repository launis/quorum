import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';

part 'execution_providers.g.dart';

/// Controller for the Orchestration Dashboard.
///
/// Manages the state of the execution list.
/// Uses strict Riverpod 3.0 AsyncNotifier pattern.
@riverpod
class DashboardController extends _$DashboardController {
  @override
  Future<List<Execution>> build() async {
    final repository = ref.watch(executionRepositoryProvider);

    // Fetch data using fpdart TaskEither
    final result = await repository.fetchExecutions().run();

    // specific strict logic: Unfold Either to standard Dart Control Flow for AsyncValue compatibility
    return result.fold(
      (error) =>
          throw error, // AsyncValue will catch this and become AsyncError
      (executions) => executions, // AsyncValue will become AsyncData
    );
  }

  /// Forces a refresh of the dashboard list.
  void refreshList() {
    ref.invalidateSelf();
  }
}
