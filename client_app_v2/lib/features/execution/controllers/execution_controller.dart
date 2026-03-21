import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/features/execution/views/dashboard_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_controller.g.dart';

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses raw `Map<String, dynamic>` strictly adhering to the De-Generator Policy.
@riverpod
class ExecutionController extends _$ExecutionController {
  StreamSubscription? _sseSubscription;

  @override
  Stream<Map<String, dynamic>?> build() async* {
    // Initial state is idle (null)
    ref.onDispose(() {
      _sseSubscription?.cancel();
    });
    yield null;
  }

  /// Starts an execution, sets the state to loading, and connects to SSE.
  Future<void> startExecution(
    String workflowId,
    Map<String, dynamic> inputs,
  ) async {
    state = const AsyncValue.loading();
    await _sseSubscription?.cancel();

    try {
      final client = ref.read(executionClientProvider);
      final initialRecord = await client.startExecution(
        workflowId: workflowId,
        rawInputs: inputs,
      );

      final executionId = initialRecord['id'] as String;

      // Update with initial record before stream connects
      state = AsyncValue.data(initialRecord);

      // Connect to SSE stream
      _connectToStream(executionId);
    } catch (e, stack) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ExecutionController',
            'START_EXECUTION_FAILED: Failed to start DAG',
            e,
            stack,
          );
      // Automatic RFC 7807 AppException catch
      state = AsyncValue.error(e, stack);
    }
  }

  /// Reconnects to an existing execution stream by ID
  Future<void> resumeExecution(String executionId) async {
    state = const AsyncValue.loading();
    await _sseSubscription?.cancel();
    _connectToStream(executionId);
  }

  /// Manually refreshes the current status by reconnecting the stream
  void refreshStatus() {
    if (state.hasValue && state.value != null) {
      final id = state.value!['id'] as String?;
      if (id != null) {
        resumeExecution(id);
      }
    }
  }

  void _connectToStream(String executionId) {
    final sseClient = ref.read(sseClientProvider);

    _sseSubscription = sseClient
        .subscribeToExecution(executionId)
        .listen(
          (update) {
            state = AsyncValue.data(update);

            final status = (update['status'] as String?)?.toLowerCase();
            if (status == 'completed' || status == 'failed') {
              ref.invalidate(executionListProvider);
              _sseSubscription?.cancel();
            }
          },
          onError: (e, stack) {
            state = AsyncValue.error(e, stack);
          },
          onDone: () {
            // Stream closed naturally
          },
        );
  }
}
