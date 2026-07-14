import 'dart:async';
import 'dart:convert';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/execution_record.dart';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_controller.g.dart';

// Settings moved to SystemConcurrency per centralized enums rule.

/// Provider to fetch executions strictly adhering to Freezed DTOs
@riverpod
Future<List<ExecutionRecord>> executionList(Ref ref) async {
  // 1. Riverpod Polling (Auto-Refresh)
  // Poll backend every 10 seconds to keep the Execution Dashboard alive and fresh,
  // bypassing the StatefulShellRoute cache stagnation issue.
  final timer = Timer(
    Duration(seconds: SystemConcurrency.dashboardRefreshRateSeconds.value),
    () {
      ref.invalidateSelf();
    },
  );
  ref.onDispose(timer.cancel);

  final dio = ref.watch(apiClientProvider);
  final response = await dio.get('/execution/executions');

  final List<dynamic> data = response.data as List;
  
  // Phase 9 Strictness: The backend returns full database models but ExecutionRecord
  // uses disallowUnrecognizedKeys: true. We must strip unrecognized keys.
  const allowedKeys = {
    'id', 'workflow_id', 'status', 'trace_version', 'strictness_level',
    'created_at', 'cost_estimate', 'metadata', 'error', 'is_resumable',
    'frozen_context', 'step_states', 'results', 'report_data'
  };

  return data.map((e) {
    final map = Map<String, dynamic>.from(e as Map<String, dynamic>);
    map.removeWhere((key, value) => !allowedKeys.contains(key));
    return ExecutionRecord.fromJson(map);
  }).toList();
}

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses `ExecutionRecord` strictly adhering to the De-Generator Policy.
@riverpod
class ExecutionController extends _$ExecutionController {
  StreamSubscription? _sseSubscription;
  int _retryCount = 0;

  @override
  Stream<ExecutionRecord?> build() async* {
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
      state = AsyncValue.data(ExecutionRecord.fromJson(initialRecord));

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
    state = const AsyncValue<ExecutionRecord?>.loading();
    await _sseSubscription?.cancel();
    _retryCount = 0;

    _connectToStream(executionId);
  }

  /// Submits a Rehydration request to the backend for an interrupted/FAILED execution.
  /// This adheres to the Riverpod 3.0 Mutation pattern by optimistically updating the state.
  Future<void> submitRehydration(String executionId) async {
    // Preserve existing state while loading to prevent UI flicker
    state = const AsyncValue<ExecutionRecord?>.loading();
    await _sseSubscription?.cancel();
    _retryCount = 0;
    try {
      final client = ref.read(executionClientProvider);
      final resumedRecord = await client.resumeExecution(executionId);

      // Immediately hydrate with the backend's verified resumed state
      state = AsyncValue.data(ExecutionRecord.fromJson(resumedRecord));

      // Wait a tiny bit for the backend to transition state before we hook SSE again
      await Future.delayed(
        Duration(milliseconds: SystemConcurrency.rehydrationDelayMs.value),
      );
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
      final id = state.value!.id;
      resumeExecution(id);
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
          renderData['status'].toString().toLowerCase() == 'pending') {
        return; // Synthesis is still running, abort parsing
      }

      // We parse it in Isolate to guarantee no Jank.
      final reportData = await ReportDataDto.parseInBackground(
        jsonEncode(renderData),
      );

      // Guard: Provider may have been disposed during isolate parsing
      if (!ref.mounted) return;

      if (state.hasValue && state.value != null) {
        ExecutionRecord merged = state.value!.copyWith(reportData: reportData);

        // DEFENSIVE MERGE (Tier 4 Bugfix): If we successfully downloaded and parsed
        // the final Heavy payload, the execution is mathematically guaranteed to be
        // passed (otherwise /render would have returned 202 Pending or 400).
        if (merged.status.toLowerCase() !=
            ExecutionStatus.failed.name.toLowerCase()) {
          merged = merged.copyWith(
            status: ExecutionStatus.passed.name.toUpperCase(),
          );
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
              if (!update.containsKey('workflow_id')) {
                update['workflow_id'] = currentState.workflowId;
              }
            }

            ExecutionRecord newRecord;
            try {
              newRecord = ExecutionRecord.fromJson(update);
            } catch (e) {
              ref
                  .read(loggerServiceProvider)
                  .warning(
                    'ExecutionController',
                    'Failed to parse SSE update',
                    e,
                  );
              return;
            }

            if (currentState != null) {
              // Preserve heavy fetched properties that SSE payload dropped
              if (currentState.reportData != null &&
                  newRecord.reportData == null) {
                newRecord = newRecord.copyWith(
                  reportData: currentState.reportData,
                );
              }

              // Detect Trace Version change
              final oldVersion = currentState.traceVersion;
              final newVersion = newRecord.traceVersion;

              if (newVersion != null && newVersion != oldVersion) {
                needsHeavyFetch = true;
              }

              // Detect completion
              final oldStatus = currentState.status.toLowerCase();
              final newStatus = newRecord.status.toLowerCase();
              if (newStatus == ExecutionStatus.passed.name.toLowerCase() &&
                  oldStatus != ExecutionStatus.passed.name.toLowerCase()) {
                needsHeavyFetch = true;
              }
            } else {
              // Bootstrapping initial stream state
              final newStatus = newRecord.status.toLowerCase();
              if (newRecord.traceVersion != null ||
                  newStatus == ExecutionStatus.passed.name.toLowerCase()) {
                needsHeavyFetch = true;
              }
            }

            state = AsyncValue.data(newRecord);

            if (needsHeavyFetch) {
              _performHeavyFetch(executionId);
            }

            final status = newRecord.status.toLowerCase();
            if (status == ExecutionStatus.passed.name.toLowerCase() ||
                status == ExecutionStatus.failed.name.toLowerCase()) {
              ref.invalidate(executionListProvider);
              _sseSubscription?.cancel();
            }
          },
          onError: (e, stack) {
            final currentState = state.value;
            final status = currentState?.status.toLowerCase();
            final isTerminal =
                status == ExecutionStatus.passed.name.toLowerCase() ||
                status == ExecutionStatus.failed.name.toLowerCase();

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
                final currentId = state.value?.id;
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
