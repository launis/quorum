import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/step_builder_view.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  group('StepBuilderView Dropdown Tests', () {
    testWidgets('renders prompt_blocks dropdown with correct options', (
      WidgetTester tester,
    ) async {
      final originalErrorBuilder = ErrorWidget.builder;

      final mockStep = NodeStrategy.llm(
        id: 'test_step_1',
        slug: 'test_slug',
        name: I18nText(defaultLocale: 'en', translations: {'en': 'Test'}),
        criteriaBlockIds: ['block_a'],
      );

      final List<PromptBlock> mockPromptBlocks = [
        const PromptBlock(
          id: 'block_a',
          slug: 'block_a',
          categoryId: 'criteria',
          label: I18nText(defaultLocale: 'en', translations: {'en': 'Block A'}),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Desc A'},
          ),
        ),
        const PromptBlock(
          id: 'block_b',
          slug: 'block_b',
          categoryId: 'criteria',
          label: I18nText(defaultLocale: 'en', translations: {'en': 'Block B'}),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Desc B'},
          ),
        ),
      ];

      final mockClient = MockStudioClient();
      when(() => mockClient.getPromptBlocks()).thenAnswer(
        (_) async => mockPromptBlocks.map((e) => e.toJson()).toList(),
      );
      when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
      when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

      final mockLogger = MockLoggerService();
      when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            studioClientProvider.overrideWithValue(mockClient),
            loggerServiceProvider.overrideWithValue(mockLogger),
            promptBlocksControllerProvider.overrideWith(() {
              return MockPromptBlocksController(mockPromptBlocks);
            }),
            modelRegistryControllerProvider.overrideWith(() {
              return MockModelRegistryController();
            }),
            stepFormProvider('test_step_1').overrideWith(() {
              return MockStepForm(mockStep);
            }),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: StepBuilderView(stepId: mockStep.id),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Check for the rendered Dropdown
      // The dropdown label is "Prompt Block"
      expect(find.text('Prompt Block'), findsOneWidget);

      // Verify that 'Block A (block_a)' is selected initial value
      expect(find.text('Block A (block_a)'), findsWidgets);

      // Open the dropdown
      final dropdownFinder = find.byType(DropdownButtonFormField<String>).last;
      await tester.ensureVisible(dropdownFinder);
      await tester.pumpAndSettle();
      await tester.tap(dropdownFinder);
      await tester.pumpAndSettle();

      // Verify dropdown items exist
      expect(find.text('Block B (block_b)').last, findsOneWidget);

      // Restore error widget builder at the very end
      ErrorWidget.builder = originalErrorBuilder;
    });

    testWidgets(
      'handles non-existent or filtered-out criteria block ID without assertion crash',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;
        bool hasAssertError = false;

        // Mock Flutter's FlutterError.onError to detect assertions
        final originalOnError = FlutterError.onError;
        FlutterError.onError = (FlutterErrorDetails details) {
          if (details.exception.toString().contains('Failed assertion:')) {
            hasAssertError = true;
          }
          originalOnError?.call(details);
        };

        final mockStep = NodeStrategy.llm(
          id: 'test_step_1',
          slug: 'test_slug',
          name: I18nText(defaultLocale: 'en', translations: {'en': 'Test'}),
          criteriaBlockIds: ['block_c'], // block_c is filtered out!
        );

        final List<PromptBlock> mockPromptBlocks = [
          const PromptBlock(
            id: 'block_a',
            slug: 'block_a',
            categoryId: 'criteria',
            label: I18nText(
              defaultLocale: 'en',
              translations: {'en': 'Block A'},
            ),
            description: I18nText(
              defaultLocale: 'en',
              translations: {'en': 'Desc A'},
            ),
          ),
          const PromptBlock(
            id: 'block_c',
            slug: 'block_c',
            categoryId:
                'context', // Context blocks are filtered out of criteria dropdown items
            label: I18nText(
              defaultLocale: 'en',
              translations: {'en': 'Block C'},
            ),
            description: I18nText(
              defaultLocale: 'en',
              translations: {'en': 'Desc C'},
            ),
          ),
        ];

        final mockClient = MockStudioClient();
        when(() => mockClient.getPromptBlocks()).thenAnswer(
          (_) async => mockPromptBlocks.map((e) => e.toJson()).toList(),
        );
        when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
        when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

        final mockLogger = MockLoggerService();
        when(
          () => mockLogger.error(any(), any(), any(), any()),
        ).thenReturn(null);

        try {
          await tester.pumpWidget(
            ProviderScope(
              overrides: [
                studioClientProvider.overrideWithValue(mockClient),
                loggerServiceProvider.overrideWithValue(mockLogger),
                promptBlocksControllerProvider.overrideWith(() {
                  return MockPromptBlocksController(mockPromptBlocks);
                }),
                modelRegistryControllerProvider.overrideWith(() {
                  return MockModelRegistryController();
                }),
                stepFormProvider('test_step_1').overrideWith(() {
                  return MockStepForm(mockStep);
                }),
              ],
              child: MaterialApp(
                localizationsDelegates: AppLocalizations.localizationsDelegates,
                supportedLocales: AppLocalizations.supportedLocales,
                home: StepBuilderView(stepId: mockStep.id),
              ),
            ),
          );
          await tester.pumpAndSettle();
        } catch (e) {
          if (e.toString().contains('Failed assertion:')) {
            hasAssertError = true;
          }
        } finally {
          FlutterError.onError = originalOnError;
          ErrorWidget.builder = originalErrorBuilder;
        }

        // If we haven't fixed the bug, hasAssertError will be true (meaning it threw the assertion).
        // If we fixed the bug, it should NOT throw any assertion error (hasAssertError is false).
        expect(hasAssertError, isFalse);
      },
    );
  });
}

class MockPromptBlocksController extends PromptBlocksController {
  final List<PromptBlock> initialData;
  MockPromptBlocksController(this.initialData);

  @override
  FutureOr<List<PromptBlock>> build() async {
    return initialData;
  }

  @override
  Future<void> refresh() async {}

  @override
  Future<PromptBlock> savePromptBlock(String id, PromptBlock payload) async {
    return payload;
  }

  @override
  Future<void> deletePromptBlock(String id) async {}

  @override
  Future<PromptBlock> clonePromptBlock(String id) async {
    return initialData.first;
  }

  @override
  Future<Map<String, dynamic>> simulatePromptBlock(
    PromptBlock payload,
    Map<String, dynamic> mockInputs,
  ) async {
    return {'rendered_prompt': 'MOCK', 'valid': true};
  }
}

class MockModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  @override
  FutureOr<List<ModelConfig>> build() async {
    return [];
  }

  @override
  Future<void> refresh() async {}
  @override
  Future<ModelConfig> saveConfig(String id, ModelConfig config) async => config;
  @override
  Future<void> deleteConfig(String id) async {}
  @override
  Future<ModelConfig> createSystemConfigDraft() async => const ModelConfig(
    id: 'mock_draft',
    slug: 'mock_draft_slug',
    type: 'model_registry',
  );
  @override
  Future<ModelConfig> cloneConfig(String id) async => const ModelConfig(
    id: 'cloned',
    slug: 'cloned_slug',
    type: 'model_registry',
    models: {},
  );
}

class MockStepForm extends StepForm {
  final NodeStrategy initialData;
  MockStepForm(this.initialData);

  @override
  FutureOr<NodeStrategy> build(String arg) async {
    return initialData;
  }

  @override
  void forceRebuild(NodeStrategy payload) {
    state = AsyncValue.data(payload);
  }

  @override
  Future<void> submit(NodeStrategy payload) async {}
}
