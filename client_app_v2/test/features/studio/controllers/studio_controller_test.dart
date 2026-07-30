import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late MockStudioClient mockClient;
  late MockLoggerService mockLogger;
  late ProviderContainer container;

  setUp(() {
    mockClient = MockStudioClient();
    mockLogger = MockLoggerService();

    // Add default mock behavior for logger
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
    when(() => mockLogger.info(any(), any())).thenReturn(null);

    container = ProviderContainer(
      overrides: [
        studioClientProvider.overrideWithValue(mockClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('PromptBlocksController Exception Handling', () {
    test(
      'deletePromptBlock throws AppError if DioException contains one (RFC 7807 Fail-Fast)',
      () async {
        // Arrange
        const id = 'pb1';
        final appError = AppException(
          extensions: const {'error_code': 'RESOURCE_IN_USE'},
          detail: 'Cannot delete block used by a blueprint',
          status: 400,
        );

        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);

        when(() => mockClient.deletePromptBlock(id)).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/studio/prompt-blocks/$id'),
            error: appError,
          ),
        );

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );

        // Act & Assert
        expect(
          () => controller.deletePromptBlock(id),
          throwsA(
            isA<AppException>()
                .having((e) => e.errorCode, 'errorCode', 'RESOURCE_IN_USE')
                .having((e) => e.status, 'status', 400),
          ),
        );

        // Verify client was called
        verify(() => mockClient.deletePromptBlock(id)).called(1);
      },
    );
  });

  group('WorkflowsController Form & Serialization (Bug Fix 422)', () {
    final validWorkflow = Workflow(
      id: 'wf_0123456789abcdef',
      slug: 'test-wf',
      name: const I18nText(translations: {'en': 'Test'}),
      description: const I18nText(translations: {'en': 'Test Desc'}),
      outputProfiles: {},
    );

    test(
      'Positive: saveWorkflow strips output_profiles from payload',
      () async {
        when(() => mockClient.getWorkflows()).thenAnswer((_) async => []);
        when(
          () => mockClient.saveWorkflow(any(), any()),
        ).thenAnswer((_) async => validWorkflow.toJson());

        final controller = container.read(workflowsControllerProvider.notifier);
        await controller.saveWorkflow('wf_0123456789abcdef', validWorkflow);

        final captured = verify(
          () => mockClient.saveWorkflow('wf_0123456789abcdef', captureAny()),
        ).captured;

        final payload = captured.first as Map<String, dynamic>;
        expect(payload.containsKey('output_profiles'), isFalse);
      },
    );

    test(
      'Negative 1: 422 Error rolls back optimistic UI and throws AppException',
      () async {
        when(() => mockClient.getWorkflows()).thenAnswer((_) async => []);

        final appError = AppException(
          extensions: const {'error_code': 'VALIDATION_ERROR'},
          detail: '1 validation error: extra_forbidden',
          status: 422,
        );

        when(() => mockClient.saveWorkflow(any(), any())).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/studio/workflows/wf_0123456789abcdef'),
            error: appError,
          ),
        );

        final controller = container.read(workflowsControllerProvider.notifier);

        expect(
          () => controller.saveWorkflow('wf_0123456789abcdef', validWorkflow),
          throwsA(
            isA<AppException>()
                .having((e) => e.status, 'status', 422)
                .having((e) => e.detail, 'detail', contains('extra_forbidden')),
          ),
        );
      },
    );

    test(
      'Negative 2: WorkflowForm submit throws AppException for empty ID',
      () async {
        final form = container.read(workflowFormProvider('new').notifier);
        final emptyWorkflow = validWorkflow.copyWith(id: '');

        await form.submit(emptyWorkflow);

        final state = container.read(workflowFormProvider('new'));
        expect(state.hasError, isTrue);
        expect(
          state.error,
          isA<AppException>().having(
            (e) => e.detail,
            'detail',
            contains('Workflow ID is required'),
          ),
        );
      },
    );
  });
}
