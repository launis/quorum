import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';
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

  const validBlock = PromptBlock.systemRule(
    id: 'blk_01965b80000070008000000000000001',
    slug: 'system-rule-default',
    label: I18nText(translations: {'en': 'System Rule'}),
    description: I18nText(translations: {'en': 'System Rule Description'}),
    instructionText: 'Follow strict deterministic constraints.',
  );

  const validSimulationRequest = PromptBlockSimulationRequest(
    block: validBlock,
  );

  setUpAll(() {
    registerFallbackValue(validBlock);
    registerFallbackValue(validSimulationRequest);
    registerFallbackValue(StackTrace.current);
  });

  setUp(() {
    mockClient = MockStudioClient();
    mockLogger = MockLoggerService();

    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);

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

  group('PromptBlocksController', () {
    test('build fetches prompt blocks from StudioClient', () async {
      when(
        () => mockClient.getPromptBlocks(),
      ).thenAnswer((_) async => [validBlock]);

      container.read(promptBlocksControllerProvider.notifier);
      final result = await container.read(
        promptBlocksControllerProvider.future,
      );

      expect(result.length, 1);
      expect(result.first.id, 'blk_01965b80000070008000000000000001');
      verify(() => mockClient.getPromptBlocks()).called(1);
    });

    test('refresh updates state on success and logs on failure', () async {
      when(
        () => mockClient.getPromptBlocks(),
      ).thenAnswer((_) async => [validBlock]);

      final controller = container.read(
        promptBlocksControllerProvider.notifier,
      );
      await container.read(promptBlocksControllerProvider.future);

      final updatedBlock = validBlock.copyWith(slug: 'updated-slug');
      when(
        () => mockClient.getPromptBlocks(),
      ).thenAnswer((_) async => [updatedBlock]);

      await controller.refresh();
      expect(
        container.read(promptBlocksControllerProvider).value?.first.slug,
        'updated-slug',
      );

      // Negative: refresh failure sets AsyncError and logs
      when(
        () => mockClient.getPromptBlocks(),
      ).thenThrow(Exception('Network timeout'));
      await controller.refresh();

      expect(container.read(promptBlocksControllerProvider).hasError, isTrue);
      verify(
        () => mockLogger.error(
          'PromptBlocksController',
          'Refresh failed',
          any(),
          any(),
        ),
      ).called(1);
    });

    test(
      'savePromptBlock performs optimistic update, confirms with backend data, and invalidates promptBlockByIdProvider',
      () async {
        const blockId = 'blk_01965b80000070008000000000000001';
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => [validBlock]);
        when(
          () => mockClient.getPromptBlock(blockId),
        ).thenAnswer((_) async => validBlock);

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );
        await container.read(promptBlocksControllerProvider.future);
        await container.read(promptBlockByIdProvider(blockId).future);

        final modifiedBlock = validBlock.copyWith(slug: 'saved-slug');
        when(
          () => mockClient.savePromptBlock(blockId, any()),
        ).thenAnswer((_) async => modifiedBlock);
        when(
          () => mockClient.getPromptBlock(blockId),
        ).thenAnswer((_) async => modifiedBlock);

        final result = await controller.savePromptBlock(blockId, modifiedBlock);

        expect(result.slug, 'saved-slug');
        expect(
          container.read(promptBlocksControllerProvider).value?.first.slug,
          'saved-slug',
        );
        final refreshedById = await container.read(
          promptBlockByIdProvider(blockId).future,
        );
        expect(refreshedById.slug, 'saved-slug');
        verify(() => mockClient.savePromptBlock(blockId, any())).called(1);
      },
    );

    test(
      'savePromptBlock appends new block when id is not yet in state and rolls back on failure',
      () async {
        const existingId = 'blk_01965b80000070008000000000000001';
        const newId = 'blk_01965b80000070008000000000000002';
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => [validBlock]);

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );
        await container.read(promptBlocksControllerProvider.future);

        final newBlock = validBlock.copyWith(id: newId, slug: 'new-block');
        when(
          () => mockClient.savePromptBlock(newId, any()),
        ).thenAnswer((_) async => newBlock);

        final saved = await controller.savePromptBlock(newId, newBlock);
        expect(saved.id, newId);
        expect(container.read(promptBlocksControllerProvider).value?.length, 2);

        // Negative 1: DioException with AppException rolls back and rethrows AppException
        final dioError = DioException(
          requestOptions: RequestOptions(
            path: '/api/studio/prompt-blocks/$existingId',
          ),
          error: AppException.network('Backend save failed'),
        );
        when(
          () => mockClient.savePromptBlock(existingId, any()),
        ).thenThrow(dioError);

        await expectLater(
          () => controller.savePromptBlock(
            existingId,
            validBlock.copyWith(slug: 'failing-slug'),
          ),
          throwsA(isA<AppException>()),
        );
        expect(
          container.read(promptBlocksControllerProvider).value?.first.slug,
          'system-rule-default',
        );

        // Negative 2: Direct AppException rethrows without wrapping as unknown
        when(
          () => mockClient.savePromptBlock(existingId, any()),
        ).thenThrow(AppException.validation('Invalid schema'));
        await expectLater(
          () => controller.savePromptBlock(existingId, validBlock),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Invalid schema'),
            ),
          ),
        );
      },
    );

    test(
      'clonePromptBlock prepends cloned block and rolls back on failure',
      () async {
        const blockId = 'blk_01965b80000070008000000000000001';
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => [validBlock]);

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );
        await container.read(promptBlocksControllerProvider.future);

        const clonedBlock = PromptBlock.systemRule(
          id: 'blk_01965b80000070008000000000000003',
          slug: 'system-rule-default-copy',
          label: I18nText(translations: {'en': 'System Rule (Copy)'}),
          description: I18nText(translations: {'en': 'Desc'}),
        );

        when(
          () => mockClient.clonePromptBlock(blockId),
        ).thenAnswer((_) async => clonedBlock);

        final result = await controller.clonePromptBlock(blockId);
        expect(result.id, 'blk_01965b80000070008000000000000003');
        expect(
          container.read(promptBlocksControllerProvider).value?.first.id,
          'blk_01965b80000070008000000000000003',
        );

        // Negative 1: DioException with AppException rolls back and rethrows
        final dioError = DioException(
          requestOptions: RequestOptions(
            path: '/api/studio/prompt-blocks/$blockId/clone',
          ),
          error: AppException.network('Clone endpoint failed'),
        );
        when(() => mockClient.clonePromptBlock(blockId)).thenThrow(dioError);
        await expectLater(
          () => controller.clonePromptBlock(blockId),
          throwsA(isA<AppException>()),
        );

        // Negative 2: Generic exception wraps in AppException
        when(
          () => mockClient.clonePromptBlock('bad_id'),
        ).thenThrow(Exception('Unexpected error'));
        await expectLater(
          () => controller.clonePromptBlock('bad_id'),
          throwsA(isA<AppException>()),
        );
        verify(
          () => mockLogger.error(
            'PromptBlocksController',
            'Clone failed',
            any(),
            any(),
          ),
        ).called(2);
      },
    );

    test(
      'createPromptBlockDraft prepends draft block and rolls back on failure',
      () async {
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => [validBlock]);

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );
        await container.read(promptBlocksControllerProvider.future);

        const draftBlock = PromptBlock.matrix(
          id: 'blk_01965b80000070008000000000000004',
          slug: 'draft-matrix',
          label: I18nText(translations: {'en': 'Draft Matrix'}),
          description: I18nText(translations: {'en': 'Draft'}),
          scales: [],
        );

        when(
          () => mockClient.createPromptBlockDraft(categoryId: 'matrix'),
        ).thenAnswer((_) async => draftBlock);

        final result = await controller.createPromptBlockDraft(
          categoryId: 'matrix',
        );
        expect(result.id, 'blk_01965b80000070008000000000000004');
        expect(
          container.read(promptBlocksControllerProvider).value?.first.id,
          'blk_01965b80000070008000000000000004',
        );

        // Negative 1: DioException with AppException rolls back and rethrows
        final dioError = DioException(
          requestOptions: RequestOptions(path: '/api/studio/prompt-blocks/'),
          error: AppException.validation('Invalid category'),
        );
        when(
          () => mockClient.createPromptBlockDraft(categoryId: 'invalid'),
        ).thenThrow(dioError);
        await expectLater(
          () => controller.createPromptBlockDraft(categoryId: 'invalid'),
          throwsA(isA<AppException>()),
        );

        // Negative 2: Generic exception wraps in AppException
        when(
          () => mockClient.createPromptBlockDraft(),
        ).thenThrow(Exception('Server error'));
        await expectLater(
          () => controller.createPromptBlockDraft(),
          throwsA(isA<AppException>()),
        );
        verify(
          () => mockLogger.error(
            'PromptBlocksController',
            'Create draft failed',
            any(),
            any(),
          ),
        ).called(2);
      },
    );

    test(
      'deletePromptBlock removes block from state, invalidates provider, and propagates errors',
      () async {
        const blockId = 'blk_01965b80000070008000000000000001';
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => [validBlock]);
        when(
          () => mockClient.deletePromptBlock(blockId),
        ).thenAnswer((_) async {});

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );
        await container.read(promptBlocksControllerProvider.future);

        await controller.deletePromptBlock(blockId);
        expect(container.read(promptBlocksControllerProvider).value, isEmpty);

        // Negative 1: DioException with AppException propagates
        final dioError = DioException(
          requestOptions: RequestOptions(
            path: '/api/studio/prompt-blocks/$blockId',
          ),
          error: AppException.validation('Block in use'),
        );
        when(() => mockClient.deletePromptBlock(blockId)).thenThrow(dioError);
        await expectLater(
          () => controller.deletePromptBlock(blockId),
          throwsA(isA<AppException>()),
        );

        // Negative 2: Generic exception wraps in AppException
        when(
          () => mockClient.deletePromptBlock('other_id'),
        ).thenThrow(Exception('Timeout'));
        await expectLater(
          () => controller.deletePromptBlock('other_id'),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'simulatePromptBlock normalizes blank locale/context defaults and propagates errors',
      () async {
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => [validBlock]);
        when(() => mockClient.simulatePromptBlock(any())).thenAnswer(
          (_) async => const PromptBlockSimulationResponse(
            valid: true,
            renderedPrompt: '<system_rule>Rendered</system_rule>',
          ),
        );

        final controller = container.read(
          promptBlocksControllerProvider.notifier,
        );

        // Boundary 1: Blank targetLocale and contextText resolve to 'en' and '[SIMULATED CONTEXT DOCUMENT]'
        final response = await controller.simulatePromptBlock(
          validBlock,
          const {'input_key': 'val'},
          targetScaleScore: 3,
          targetLocale: '   ',
          contextText: '',
        );
        expect(response.renderedPrompt, '<system_rule>Rendered</system_rule>');

        final captured =
            verify(
                  () => mockClient.simulatePromptBlock(captureAny()),
                ).captured.single
                as PromptBlockSimulationRequest;
        expect(captured.targetLocale, 'en');
        expect(captured.contextText, '[SIMULATED CONTEXT DOCUMENT]');
        expect(captured.targetScaleScore, 3);

        // Boundary 2: Explicit targetLocale and contextText are trimmed and preserved
        await controller.simulatePromptBlock(
          validBlock,
          const {},
          targetLocale: ' fi ',
          contextText: ' Custom context ',
        );
        final capturedCustom =
            verify(
                  () => mockClient.simulatePromptBlock(captureAny()),
                ).captured.single
                as PromptBlockSimulationRequest;
        expect(capturedCustom.targetLocale, 'fi');
        expect(capturedCustom.contextText, 'Custom context');

        // Negative 1: Direct AppException from StudioClient rethrows preserving validation details
        when(
          () => mockClient.simulatePromptBlock(any()),
        ).thenThrow(AppException.validation('PromptBlock ID is required'));
        await expectLater(
          () => controller.simulatePromptBlock(
            validBlock.copyWith(id: ''),
            const {},
          ),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('PromptBlock ID is required'),
            ),
          ),
        );

        // Negative 2: DioException with AppException rethrows AppException
        final dioError = DioException(
          requestOptions: RequestOptions(
            path: '/api/studio/prompt-blocks/simulate',
          ),
          error: AppException.network('Simulation timeout'),
        );
        when(() => mockClient.simulatePromptBlock(any())).thenThrow(dioError);
        await expectLater(
          () => controller.simulatePromptBlock(validBlock, const {}),
          throwsA(isA<AppException>()),
        );
      },
    );
  });

  group('PromptBlockForm', () {
    test(
      'build, forceRebuild, and submit handle positive and negative partitions',
      () async {
        const blockId = 'blk_01965b80000070008000000000000001';
        when(
          () => mockClient.getPromptBlock(blockId),
        ).thenAnswer((_) async => validBlock);
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => [validBlock]);

        final formNotifier = container.read(
          promptBlockFormProvider(blockId).notifier,
        );
        final loaded = await container.read(
          promptBlockFormProvider(blockId).future,
        );
        expect(loaded.id, blockId);

        // forceRebuild updates state immediately
        final rebuilt = validBlock.copyWith(slug: 'rebuilt-slug');
        formNotifier.forceRebuild(rebuilt);
        expect(
          container.read(promptBlockFormProvider(blockId)).value?.slug,
          'rebuilt-slug',
        );

        // Positive submit saves and updates form state with backend-verified block
        final backendVerified = rebuilt.copyWith(slug: 'verified-by-backend');
        when(
          () => mockClient.savePromptBlock(blockId, any()),
        ).thenAnswer((_) async => backendVerified);

        await formNotifier.submit(rebuilt);
        expect(
          container.read(promptBlockFormProvider(blockId)).value?.slug,
          'verified-by-backend',
        );

        // Negative 1: Save failure retains unsaved form edits in state.value while exposing error
        final dioSaveErr = DioException(
          requestOptions: RequestOptions(
            path: '/api/studio/prompt-blocks/$blockId',
          ),
          error: AppException.network('Save failed'),
        );
        when(
          () => mockClient.savePromptBlock(blockId, any()),
        ).thenThrow(dioSaveErr);

        final unsavedEdit = validBlock.copyWith(slug: 'unsaved-edit');
        await expectLater(
          () => formNotifier.submit(unsavedEdit),
          throwsA(isA<AppException>()),
        );
        final errState = container.read(promptBlockFormProvider(blockId));
        expect(errState.hasError, isTrue);
        expect(errState.hasValue, isTrue);
        expect(errState.value?.slug, 'unsaved-edit');

        // Negative 2: Empty ID and 'new' configId throw validation AppException
        final newFormNotifier = container.read(
          promptBlockFormProvider('new').notifier,
        );
        await expectLater(
          () => newFormNotifier.submit(validBlock.copyWith(id: '')),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Block ID is required'),
            ),
          ),
        );
      },
    );
  });
}
