import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';

part 'execution_details_provider.g.dart';

@riverpod
Future<Execution> executionDetails(Ref ref, String executionId) async {
  final repository = ref.watch(executionRepositoryProvider);

  // Set up auto-refresh timer if we are in a polling state?
  // Riverpod 2/3 approach: use a Timer to invalidate self.
  // But strictly, we only want to poll if status is running/pending.
  // We can check the result and schedule a refresh.

  final result = await repository.getExecution(executionId).run();

  return result.fold((error) => throw error, (execution) {
    // Polling Logic: If running or pending, refresh after 3 seconds.
    // This creates a recursive loop of "live" updates.
    if (execution.status == ExecutionStatus.running ||
        execution.status == ExecutionStatus.pending ||
        execution.status == ExecutionStatus.started) {
      final timer = Timer(const Duration(seconds: 3), () {
        // We invalidate the provider to force a re-fetch
        ref.invalidateSelf();
      });

      // Ensure timer is cancelled if provider is disposed
      ref.onDispose(timer.cancel);
    }
    return execution;
  });
}
