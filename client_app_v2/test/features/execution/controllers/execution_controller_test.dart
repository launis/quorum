import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/core/logging/logger_service.dart';

class MockExecutionClient implements ExecutionClient {
  @override
  Future<Map<String, dynamic>> startExecution({
    required String workflowId,
    required Map<String, dynamic> rawInputs,
    int? strictnessLevel,
    String? scoringStrategy,
  }) async {
    return {'id': 'test_exec', 'workflow_id': 'test_wf', 'status': 'running'};
  }

  @override
  Future<Map<String, dynamic>> resumeExecution(String executionId) async {
    return {'id': executionId, 'workflow_id': 'test_wf', 'status': 'running'};
  }

  Future<Map<String, dynamic>> renderExecution(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) async {
    return {
      'execution_id': executionId,
      'workflow_id': 'test_wf',
      'global_metrics': {
        'total_atoms': 5,
        'evaluated': 5,
        'short_circuited_na': 0,
        'duration_ms': 100,
      },
      'results': [],
      'hydrated_references': {},
    };
  }

  @override
  Future<Map<String, dynamic>> getExecutionStatus(String executionId) async {
    return {'id': executionId, 'workflow_id': 'test_wf', 'status': 'passed'};
  }

  Future<Map<String, dynamic>> getScorecard(String executionId) async {
    return {};
  }

  @override
  Future<Map<String, dynamic>> overrideAtom({
    required String executionId,
    required String atomId,
    required Map<String, dynamic> payload,
  }) async {
    return {};
  }
}

class MockSseClient implements SseClient {
  @override
  Stream<Map<String, dynamic>> subscribeToExecution(String executionId) async* {
    yield {
      'id': executionId,
      'workflow_id': 'test_wf',
      'status': 'passed',
      'trace_version': '1.0',
    };
  }
}

class MockLoggerService implements LoggerService {
  @override
  Future<void> init() async {}
  @override
  void debug(
    String module,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {}
  @override
  void info(
    String module,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {}
  @override
  void warning(
    String module,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {}
  @override
  void error(
    String module,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {}
}

void main() {
  test(
    'ExecutionController initializes state and handles SSE updates successfully',
    () async {
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(MockExecutionClient()),
          sseClientProvider.overrideWithValue(MockSseClient()),
          loggerServiceProvider.overrideWithValue(MockLoggerService()),
        ],
      );

      final sub = container.listen(executionControllerProvider, (_, __) {});

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution('test_wf', {});

      // Wait for the stream update and heavy fetch
      await Future.delayed(const Duration(milliseconds: 200));

      final state = container.read(executionControllerProvider);
      expect(state.hasValue, true);
      // Wait, state.value is an ExecutionRecord.
      expect(state.value?.id, 'test_exec');
      expect(state.value?.status, 'PASSED');
      expect(state.value?.reportData != null, true);

      sub.close();
    },
  );
}
