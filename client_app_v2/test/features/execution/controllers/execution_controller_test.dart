import 'dart:async';
import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:dio/dio.dart';

class MockExecutionClient implements ExecutionClient {
  @override
  Future<Map<String, dynamic>> startExecution({
    required String workflowId,
    required Map<String, dynamic> rawInputs,
  }) async {
    return {'id': 'test_exec', 'status': 'running'};
  }

  @override
  Future<Map<String, dynamic>> resumeExecution(String executionId) async {
    return {'id': executionId, 'status': 'running'};
  }

  @override
  Future<Map<String, dynamic>> renderExecution(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) async {
    return {
      'workflow_id': 'test_wf',
      'profile_id': 'default',
      'profile_name': {
        'default_locale': 'en',
        'translations': {'en': 'Default Profile'},
      },
      'available_profiles': {
        'default': {
          'default_locale': 'en',
          'translations': {'en': 'Default Profile'},
        }
      },
      'layouts': []
    };
  }

  @override
  Future<Map<String, dynamic>> getExecutionStatus(String executionId) async {
    return {'id': executionId, 'status': 'completed'};
  }
  
  @override
  Future<Map<String, dynamic>> getScorecard(String executionId) async {
    return {};
  }
}

class MockSseClient implements SseClient {
  @override
  Stream<Map<String, dynamic>> subscribeToExecution(String executionId) async* {
    yield {'id': executionId, 'status': 'completed', 'trace_version': '1.0'};
  }
}

class MockLoggerService implements LoggerService {
  @override
  Future<void> init() async {}
  @override
  void debug(String module, String message, [Object? error, StackTrace? stack]) {}
  @override
  void info(String module, String message, [Object? error, StackTrace? stack]) {}
  @override
  void warning(String module, String message, [Object? error, StackTrace? stack]) {}
  @override
  void error(String module, String message, [Object? error, StackTrace? stack]) {}
}

void main() {
  test('ExecutionController initializes state and handles SSE updates successfully', () async {
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
    expect(state.value?['id'], 'test_exec');
    expect(state.value?['status'], 'completed');
    expect(state.value?.containsKey('report_data'), true);

    sub.close();
  });
}
