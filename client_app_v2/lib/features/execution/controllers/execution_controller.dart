import 'dart:async';
import 'dart:convert';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/core/error/app_exception.dart';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_controller.g.dart';

/// Centralized execution logic settings
class ExecutionSettings {
  const ExecutionSettings._();

  /// The duration to yield before reconnecting to a rehydrated SSE stream.
  static const Duration rehydrationDelay = Duration(milliseconds: 500);
}

/// Centralized settings for the Execution Dashboard
class DashboardSettings {
  const DashboardSettings._();

  /// Auto-refresh interval for the continuous background polling
  static const Duration refreshRate = Duration(seconds: 10);
}

/// Provider to fetch executions using native casting (No Freezed API DTOs)
@riverpod
Future<List<Map<String, dynamic>>> executionList(Ref ref) async {
  // 1. Riverpod Polling (Auto-Refresh)
  // Poll backend every 10 seconds to keep the Execution Dashboard alive and fresh,
  // bypassing the StatefulShellRoute cache stagnation issue.
  final timer = Timer(DashboardSettings.refreshRate, () {
    ref.invalidateSelf();
  });
  ref.onDispose(timer.cancel);

  final dio = ref.watch(apiClientProvider);
  final response = await dio.get('/execution/executions');

  final List<dynamic> data = response.data is List ? response.data as List : [];
  return data
      .map((e) => e is Map ? e as Map<String, dynamic> : <String, dynamic>{})
      .toList();
}

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses raw `Map<String, dynamic>` strictly adhering to the De-Generator Policy.
@riverpod
class ExecutionController extends _$ExecutionController {
  StreamSubscription? _sseSubscription;
  int _retryCount = 0;

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
    Map<String, dynamic> inputs, {
    int strictnessLevel = 50,
    String scoringStrategy = 'WATERFALL',
  }) async {
    state = const AsyncValue.loading();
    await _sseSubscription?.cancel();
    _retryCount = 0;

    try {
      final client = ref.read(executionClientProvider);
      final initialRecord = await client.startExecution(
        workflowId: workflowId,
        rawInputs: inputs,
        strictnessLevel: strictnessLevel,
        scoringStrategy: scoringStrategy,
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
    state = const AsyncValue<Map<String, dynamic>?>.loading();
    await _sseSubscription?.cancel();
    _retryCount = 0;

    _connectToStream(executionId);
  }

  /// Submits a Rehydration request to the backend for an interrupted/FAILED execution.
  /// This adheres to the Riverpod 3.0 Mutation pattern by optimistically updating the state.
  Future<void> submitRehydration(String executionId) async {
    // Preserve existing state while loading to prevent UI flicker
    state = const AsyncValue<Map<String, dynamic>?>.loading();
    await _sseSubscription?.cancel();
    _retryCount = 0;
    try {
      final client = ref.read(executionClientProvider);
      final resumedRecord = await client.resumeExecution(executionId);

      // Immediately hydrate with the backend's verified resumed state
      state = AsyncValue.data(resumedRecord);

      // Wait a tiny bit for the backend to transition state before we hook SSE again
      await Future.delayed(ExecutionSettings.rehydrationDelay);
      _connectToStream(executionId);
    } catch (e, stack) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ExecutionController',
            'REHYDRATION_FAILED: Failed to resume execution',
            e,
            stack,
          );
      state = AsyncValue.error(e, stack);
      // Let the mutation Hook catch the exception
      rethrow;
    }
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

  /// Extracts the heavy blueprint JSON and deserializes it off-thread.
  Future<void> _performHeavyFetch(String executionId) async {
    try {
      final client = ref.read(executionClientProvider);
      final renderData = await client.renderExecution(executionId);

      // Guard: Provider may have been disposed during the network call
      if (!ref.mounted) return;

      // Epic 14: Guard against 202 Accepted pending synthesis poll
      if (renderData.containsKey('status') &&
          renderData['status'] == 'pending') {
        return; // Synthesis is still running, abort parsing
      }

      // We parse it in Isolate to guarantee no Jank.
      final reportData = await ReportDataDTO.parseInBackground(
        jsonEncode(renderData),
      );

      // Guard: Provider may have been disposed during isolate parsing
      if (!ref.mounted) return;

      if (state.hasValue && state.value != null) {
        // Merge the heavy DTO back into the raw Map state for backward compatibility
        // with the temporary ExecutionView payload before Milestone 4 applies Flat MVC.
        final Map<String, dynamic> merged = Map<String, dynamic>.from(
          state.value!,
        );
        merged['report_data'] = reportData;
        merged['results'] = renderData; // Temporary legacy support

        // DEFENSIVE MERGE (Tier 4 Bugfix): If we successfully downloaded and parsed
        // the final Heavy payload, the execution is mathematically guaranteed to be
        // completed (otherwise /render would have returned 202 Pending or 400).
        // This prevents asynchronous Race Conditions where state.value was momentarily stale.
        final currentStatus = merged['status']?.toString().toLowerCase();
        if (currentStatus != 'failed') {
          merged['status'] = 'completed';
        }

        state = AsyncValue.data(merged);
      }
    } catch (e, stack) {
      // Guard: Don't try to log via ref if provider is disposed
      if (!ref.mounted) return;
      ref
          .read(loggerServiceProvider)
          .warning(
            'ExecutionController',
            'HEAVY_FETCH_FAILED: Failed to download heavy payload',
            e,
            stack,
          );
      state = AsyncValue.error(e, stack);
    }
  }

  void _connectToStream(String executionId) {
    final sseClient = ref.read(sseClientProvider);

    _sseSubscription = sseClient
        .subscribeToExecution(executionId)
        .listen(
          (update) {
            _retryCount = 0;
            final currentState = state.value;
            bool needsHeavyFetch = false;

            if (currentState != null) {
              // Preserve heavy fetched properties that SSE payload dropped
              if (currentState.containsKey('report_data')) {
                update['report_data'] = currentState['report_data'];
              }
              if (currentState.containsKey('results')) {
                update['results'] = currentState['results'];
              }

              // Detect Trace Version change
              final oldVersion = currentState['trace_version']?.toString();
              final newVersion = update['trace_version']?.toString();

              if (newVersion != null && newVersion != oldVersion) {
                needsHeavyFetch = true;
              }

              // Detect completion
              final oldStatus = (currentState['status'] as String?)
                  ?.toLowerCase();
              final newStatus = (update['status'] as String?)?.toLowerCase();
              if ((newStatus == 'passed' || newStatus == 'completed') &&
                  (oldStatus != 'passed' && oldStatus != 'completed')) {
                needsHeavyFetch = true;
              }
            } else {
              // Bootstrapping initial stream state
              final newStatus = (update['status'] as String?)?.toLowerCase();
              if (update['trace_version'] != null ||
                  newStatus == 'passed' ||
                  newStatus == 'completed') {
                needsHeavyFetch = true;
              }
            }

            state = AsyncValue.data(update);

            if (needsHeavyFetch) {
              _performHeavyFetch(executionId);
            }

            final status = (update['status'] as String?)?.toLowerCase();
            if (status == 'passed' ||
                status == 'completed' ||
                status == 'failed') {
              ref.invalidate(executionListProvider);
              _sseSubscription?.cancel();
            }
          },
          onError: (e, stack) {
            final currentState = state.value;
            final status = (currentState?['status'] as String?)?.toLowerCase();
            final isTerminal =
                status == 'passed' ||
                status == 'completed' ||
                status == 'failed';

            if (currentState != null && !isTerminal && _retryCount < 5) {
              _retryCount++;
              ref
                  .read(loggerServiceProvider)
                  .warning(
                    'ExecutionController',
                    'SSE connection lost abruptly for execution $executionId. Reconnecting (attempt $_retryCount/5)... Error: $e',
                  );
              _sseSubscription?.cancel();
              Future.delayed(const Duration(seconds: 2), () {
                if (!ref.mounted) return;
                final currentId = state.value?['id'] as String?;
                if (currentId == executionId) {
                  _connectToStream(executionId);
                }
              });
              return;
            }

            ref
                .read(loggerServiceProvider)
                .error(
                  'ExecutionController',
                  'SSE_STREAM_ERROR: Connection failed abruptly',
                  e,
                  stack,
                );

            // V2 UX: Translate raw socket/stream errors into a human-readable graceful degradation message
            // Uses No-String Mandate by passing error_code to the localization pipeline.
            final explicitError =
                AppException.network(
                  'Connection dropped unexpectedly.',
                ).copyWith(
                  extensions: const {'error_code': 'SSE_CONNECTION_ABORTED'},
                );
            state = AsyncValue.error(explicitError, stack);
          },
          onDone: () {
            // Stream closed naturally
          },
        );
  }
}
