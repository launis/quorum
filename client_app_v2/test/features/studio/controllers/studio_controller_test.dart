import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
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

  final validWorkflow = Workflow(
    id: 'wf_0123456789abcdef',
    slug: 'test-wf',
    name: const I18nText(translations: {'en': 'Test'}),
    description: const I18nText(translations: {'en': 'Test Desc'}),
    modelRegistryId: 'reg_default',
    outputProfiles: {},
  );

  final validBlock = PromptBlock.systemRule(
    id: 'blk_0123456789abcdef',
    slug: 'test-block',
    label: const I18nText(translations: {'en': 'Test Block'}),
    description: const I18nText(translations: {'en': 'Test Desc'}),
    instructionText: 'Test Instruction',
  );

  final validConfig = const ModelConfig(
    id: 'cfg_0123456789abcdef',
    name: 'Test Registry',
    slug: 'test-registry',
    type: 'model_registry',
    defaultProvider: 'ai_studio',
  );

  setUpAll(() {
    registerFallbackValue(validWorkflow);
    registerFallbackValue(validBlock);
    registerFallbackValue(validConfig);
    registerFallbackValue(StackTrace.current);
  });

  setUp(() {
    mockClient = MockStudioClient();
    mockLogger = MockLoggerService();

    // Add default mock behavior for logger
    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
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

  group('PromptBlocksController Operations & Exception Handling', () {
    final validBlock = PromptBlock.systemRule(
      id: 'blk_0123456789abcdef',
      slug: 'test-block',
      label: const I18nText(translations: {'en': 'Test Block'}),
      description: const I18nText(translations: {'en': 'Test Desc'}),
      instructionText: 'Test Instruction',
    );

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

    test('Positive: savePromptBlock saves typed PromptBlock model', () async {
      when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
      when(
        () => mockClient.savePromptBlock(any(), any()),
      ).thenAnswer((_) async => validBlock);

      final controller = container.read(
        promptBlocksControllerProvider.notifier,
      );
      final result = await controller.savePromptBlock(
        'blk_0123456789abcdef',
        validBlock,
      );

      expect(result.id, 'blk_0123456789abcdef');
      verify(
        () => mockClient.savePromptBlock(
          'blk_0123456789abcdef',
          any(that: isA<PromptBlock>()),
        ),
      ).called(1);
    });

    test(
      'Negative 1: savePromptBlock rolls back and throws on server error',
      () async {
        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
        when(() => mockClient.savePromptBlock(any(), any())).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/studio/prompt-blocks/save'),
            type: DioExceptionType.badResponse,
          ),
        );

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );
        expect(
          () => controller.savePromptBlock('blk_0123456789abcdef', validBlock),
          throwsA(isA<AppException>()),
        );
      },
    );

    test('Negative 2: PromptBlockForm submit throws on empty ID', () async {
      final form = container.read(promptBlockFormProvider('new').notifier);
      final emptyBlock = validBlock.copyWith(id: '');

      await form.submit(emptyBlock);

      final state = container.read(promptBlockFormProvider('new'));
      expect(state.hasError, isTrue);
      expect(
        state.error,
        isA<AppException>().having(
          (e) => e.detail,
          'detail',
          contains('Block ID is required'),
        ),
      );
    });
  });

  group('WorkflowsController Form & Serialization (Bug Fix 422)', () {
    test(
      'Positive: saveWorkflow sends typed Workflow payload and updates state',
      () async {
        when(() => mockClient.getWorkflows()).thenAnswer((_) async => []);
        when(
          () => mockClient.saveWorkflow(any(), any()),
        ).thenAnswer((_) async => validWorkflow);

        final controller = container.read(workflowsControllerProvider.notifier);
        await controller.saveWorkflow('wf_0123456789abcdef', validWorkflow);

        final captured = verify(
          () => mockClient.saveWorkflow('wf_0123456789abcdef', captureAny()),
        ).captured;

        final payload = captured.first as Workflow;
        expect(payload.id, 'wf_0123456789abcdef');
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
            requestOptions: RequestOptions(
              path: '/studio/workflows/wf_0123456789abcdef',
            ),
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

  group('ModelRegistryController Operations & Exception Handling', () {
    test('Positive: saveConfig saves typed ModelConfig and updates state', () async {
      when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);
      when(
        () => mockClient.saveSystemConfig(any(), any()),
      ).thenAnswer((_) async => validConfig);

      final controller = container.read(modelRegistryControllerProvider.notifier);
      final result = await controller.saveConfig('cfg_0123456789abcdef', validConfig);

      expect(result.id, 'cfg_0123456789abcdef');
      verify(
        () => mockClient.saveSystemConfig(
          'cfg_0123456789abcdef',
          any(that: isA<ModelConfig>()),
        ),
      ).called(1);
    });

    test('Negative 1: saveConfig rolls back and throws on server error', () async {
      when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);
      when(
        () => mockClient.saveSystemConfig(any(), any()),
      ).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/studio/system-configs/cfg_0123456789abcdef'),
          type: DioExceptionType.badResponse,
        ),
      );

      final controller = container.read(modelRegistryControllerProvider.notifier);
      expect(
        () => controller.saveConfig('cfg_0123456789abcdef', validConfig),
        throwsA(isA<AppException>()),
      );
    });

    test('Negative 2: deleteConfig throws AppException on orphan rejection', () async {
      final appError = AppException(
        extensions: const {'error_code': 'RESOURCE_IN_USE'},
        detail: 'Cannot delete system config in use by workflow',
        status: 400,
      );

      when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);
      when(() => mockClient.deleteSystemConfig('cfg_0123456789abcdef')).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/studio/system-configs/cfg_0123456789abcdef'),
          error: appError,
        ),
      );

      final controller = container.read(modelRegistryControllerProvider.notifier);
      expect(
        () => controller.deleteConfig('cfg_0123456789abcdef'),
        throwsA(
          isA<AppException>()
              .having((e) => e.errorCode, 'errorCode', 'RESOURCE_IN_USE')
              .having((e) => e.status, 'status', 400),
        ),
      );
    });
  });
}
