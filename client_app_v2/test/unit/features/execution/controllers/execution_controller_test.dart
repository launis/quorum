import 'dart:async';
import 'dart:io';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

const String _validExecId = 'exe_0195f2c4e8a97d3b9a1c2e3f4a5b6c7d';
const String _validWfId = 'wfl_0195f2c4e8a97d3b9a1c2e3f4a5b6c7d';

class MockExecutionClient implements ExecutionClient {
  final bool shouldFailStart;
  final bool shouldFailResume;

  MockExecutionClient({
    this.shouldFailStart = false,
    this.shouldFailResume = false,
  });

  @override
  Future<ExecutionRecord> startExecution({
    required ExecutionCreateRequestDto request,
  }) async {
    if (shouldFailStart) {
      throw AppException.server('Start execution failed', statusCode: 500);
    }
    return ExecutionRecord(
      id: _validExecId,
      workflowId: request.workflowId,
      targetLocale: request.targetLocale,
      status: 'RUNNING',
    );
  }

  @override
  Future<ExecutionRecord> resumeExecution(String executionId) async {
    if (shouldFailResume) {
      throw AppException.server('Resume execution failed', statusCode: 500);
    }
    return ExecutionRecord(
      id: executionId,
      workflowId: _validWfId,
      targetLocale: 'fi',
      status: 'RUNNING',
    );
  }

  @override
  Future<ExecutionRecord> getExecutionStatus(String executionId) async {
    return ExecutionRecord(
      id: executionId,
      workflowId: _validWfId,
      targetLocale: 'fi',
      status: 'PASSED',
    );
  }

  @override
  Future<GenericStatusResponseDto> overrideAtom({
    required String executionId,
    required String atomId,
    required HumanOverrideRequestDto payload,
  }) async {
    return const GenericStatusResponseDto(message: 'ok');
  }
}

class MockSseClient implements SseClient {
  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    yield {
      'id': executionId,
      'workflow_id': _validWfId,
      'target_locale': 'fi',
      'status': 'passed',
    };
  }
}

class MockErrorSseClient implements SseClient {
  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    yield {
      'id': executionId,
      'workflow_id': _validWfId,
      'target_locale': 'fi',
      'status': 'running',
    };
    yield {
      'error':
          "SSE Stream Interrupted: execution with ID '$executionId' not found",
    };
  }
}

class MockExplicitErrorCodeSseClient implements SseClient {
  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    yield {
      'error_code': 'QUOTA_EXCEEDED',
      'message': 'Token quota limit reached',
    };
  }
}

class MockMalformedPayloadSseClient implements SseClient {
  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    yield {'id': executionId, 'unrecognized_illegal_field': 'boom'};
  }
}

class MockSseClientWithErrorNull implements SseClient {
  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    yield {
      'id': executionId,
      'workflow_id': _validWfId,
      'target_locale': 'fi',
      'status': 'passed',
      'error': null,
    };
  }
}

class MockSseClientWithFailedExecutionRecord implements SseClient {
  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    yield {
      'id': executionId,
      'workflow_id': _validWfId,
      'target_locale': 'fi',
      'status': 'failed',
      'error': 'Step computation failed',
    };
  }
}

class MockAbruptDropTerminalSseClient implements SseClient {
  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    throw Exception('Socket closed abruptly');
  }
}

class MockLoggerService implements LoggerService {
  final List<String> errors = [];
  final List<String> warnings = [];

  @override
  Future<void> init({File? logFile}) async {}
  @override
  void debug(String context, String message) {}
  @override
  void info(String context, String message) {}
  @override
  void warning(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    warnings.add('$context: $message');
  }

  @override
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    errors.add('$context: $message');
  }
}

class _StubDioAdapter implements HttpClientAdapter {
  final List<Object?>? responseData;

  _StubDioAdapter(this.responseData);

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    return ResponseBody.fromString(
      '[]',
      200,
      headers: {
        Headers.contentTypeHeader: [Headers.jsonContentType],
      },
    );
  }

  @override
  void close({bool force = false}) {}
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
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution(_validWfId, {});
      await Future<void>.delayed(const Duration(milliseconds: 50));

      final state = container.read(executionControllerProvider);
      expect(state.hasValue, isTrue);
      expect(state.value?.id, _validExecId);
      expect(state.value?.status, 'PASSED');
    },
  );

  test(
    'ExecutionController handles SSE error update gracefully without CheckedFromJsonException',
    () async {
      final logger = MockLoggerService();
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(MockExecutionClient()),
          sseClientProvider.overrideWithValue(MockErrorSseClient()),
          loggerServiceProvider.overrideWithValue(logger),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution(_validWfId, {});
      await Future<void>.delayed(const Duration(milliseconds: 50));

      final state = container.read(executionControllerProvider);
      expect(state.hasError, isTrue);
      expect(
        state.error.toString().contains('CheckedFromJsonException'),
        isFalse,
      );
      expect(logger.errors, isNotEmpty);
    },
  );

  test(
    'ExecutionController handles explicit error_code SSE payload as AppException',
    () async {
      final logger = MockLoggerService();
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(MockExecutionClient()),
          sseClientProvider.overrideWithValue(MockExplicitErrorCodeSseClient()),
          loggerServiceProvider.overrideWithValue(logger),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution(_validWfId, {});
      await Future<void>.delayed(const Duration(milliseconds: 50));

      final state = container.read(executionControllerProvider);
      expect(state.hasError, isTrue);
      expect(state.error, isA<AppException>());
      final appErr = state.error as AppException;
      expect(appErr.extensions['error_code'], 'QUOTA_EXCEEDED');
    },
  );

  test(
    'ExecutionController fails fast on malformed SSE payload with SSE_DESERIALIZATION_FAILED',
    () async {
      final logger = MockLoggerService();
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(MockExecutionClient()),
          sseClientProvider.overrideWithValue(MockMalformedPayloadSseClient()),
          loggerServiceProvider.overrideWithValue(logger),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution(_validWfId, {});
      await Future<void>.delayed(const Duration(milliseconds: 50));

      final state = container.read(executionControllerProvider);
      expect(state.hasError, isTrue);
      expect(state.error, isA<AppException>());
      final appErr = state.error as AppException;
      expect(appErr.extensions['error_code'], 'SSE_DESERIALIZATION_FAILED');
    },
  );

  test(
    'ExecutionController transitions to error state when startExecution fails',
    () async {
      final logger = MockLoggerService();
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(
            MockExecutionClient(shouldFailStart: true),
          ),
          sseClientProvider.overrideWithValue(MockSseClient()),
          loggerServiceProvider.overrideWithValue(logger),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution(_validWfId, {});

      final state = container.read(executionControllerProvider);
      expect(state.hasError, isTrue);
      expect(logger.errors, isNotEmpty);
    },
  );

  test(
    'ExecutionController submitRehydration rethrows error and logs on failure',
    () async {
      final logger = MockLoggerService();
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(
            MockExecutionClient(shouldFailResume: true),
          ),
          sseClientProvider.overrideWithValue(MockSseClient()),
          loggerServiceProvider.overrideWithValue(logger),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await expectLater(
        () => controller.submitRehydration(_validExecId),
        throwsA(isA<AppException>()),
      );
      expect(container.read(executionControllerProvider).hasError, isTrue);
      expect(logger.errors, isNotEmpty);
    },
  );

  test(
    'ExecutionController handles SSE update containing error: null without misclassifying as stream error',
    () async {
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(MockExecutionClient()),
          sseClientProvider.overrideWithValue(MockSseClientWithErrorNull()),
          loggerServiceProvider.overrideWithValue(MockLoggerService()),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution(_validWfId, {});
      await Future<void>.delayed(const Duration(milliseconds: 50));

      final state = container.read(executionControllerProvider);
      expect(state.hasError, isFalse);
      expect(state.hasValue, isTrue);
      expect(state.value?.id, _validExecId);
      expect(state.value?.status, 'PASSED');
    },
  );

  test(
    'ExecutionController handles failed ExecutionRecord containing domain error without misclassifying as stream error',
    () async {
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(MockExecutionClient()),
          sseClientProvider.overrideWithValue(
            MockSseClientWithFailedExecutionRecord(),
          ),
          loggerServiceProvider.overrideWithValue(MockLoggerService()),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);

      await controller.startExecution(_validWfId, {});
      await Future<void>.delayed(const Duration(milliseconds: 50));

      final state = container.read(executionControllerProvider);
      expect(state.hasError, isFalse);
      expect(state.hasValue, isTrue);
      expect(state.value?.id, _validExecId);
      expect(state.value?.status, 'FAILED');
      expect(state.value?.error, 'Step computation failed');
    },
  );

  test(
    'ExecutionController resumeExecution with abrupt stream error sets SSE_CONNECTION_ABORTED when state is null',
    () async {
      final logger = MockLoggerService();
      final container = ProviderContainer(
        overrides: [
          executionClientProvider.overrideWithValue(MockExecutionClient()),
          sseClientProvider.overrideWithValue(
            MockAbruptDropTerminalSseClient(),
          ),
          loggerServiceProvider.overrideWithValue(logger),
        ],
      );
      addTearDown(container.dispose);

      final sub = container.listen(executionControllerProvider, (_, _) {});
      addTearDown(sub.close);

      final controller = container.read(executionControllerProvider.notifier);
      await controller.resumeExecution(_validExecId);
      await Future<void>.delayed(const Duration(milliseconds: 50));

      final state = container.read(executionControllerProvider);
      expect(state.hasError, isTrue);
      final appErr = state.error as AppException;
      expect(appErr.extensions['error_code'], 'SSE_CONNECTION_ABORTED');
    },
  );

  test('executionListProvider parses empty list cleanly', () async {
    final dio = Dio();
    dio.httpClientAdapter = _StubDioAdapter(const []);

    final container = ProviderContainer(
      overrides: [
        apiClientProvider.overrideWithValue(dio),
        loggerServiceProvider.overrideWithValue(MockLoggerService()),
      ],
    );
    addTearDown(container.dispose);

    final list = await container.read(executionListProvider.future);
    expect(list, isEmpty);
  });
}
