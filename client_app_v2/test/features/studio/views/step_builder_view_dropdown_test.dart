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
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';
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
        name: const I18nText(translations: {'en': 'Test'}),
        criteriaBlockIds: const ['block_a'],
      );

      final List<PromptBlock> mockPromptBlocks = [
        const PromptBlock.systemRule(
          id: 'block_a',
          slug: 'block_a',
          label: I18nText(translations: {'en': 'Block A'}),
          description: I18nText(translations: {'en': 'Desc A'}),
        ),
        const PromptBlock.systemRule(
          id: 'block_b',
          slug: 'block_b',
          label: I18nText(translations: {'en': 'Block B'}),
          description: I18nText(translations: {'en': 'Desc B'}),
        ),
      ];

      final mockClient = MockStudioClient();
      when(
        () => mockClient.getPromptBlocks(),
      ).thenAnswer((_) async => mockPromptBlocks);
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

      expect(find.text('Prompt Block'), findsOneWidget);
      expect(find.text('Block A (block_a)'), findsWidgets);

      final dropdownFinder = find.byType(DropdownButtonFormField<String>).last;
      await tester.ensureVisible(dropdownFinder);
      await tester.pumpAndSettle();
      await tester.tap(dropdownFinder);
      await tester.pumpAndSettle();

      expect(find.text('Block B (block_b)').last, findsOneWidget);

      ErrorWidget.builder = originalErrorBuilder;
    });

    testWidgets(
      'handles non-existent or filtered-out criteria block ID without assertion crash',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;
        bool hasAssertError = false;

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
          name: const I18nText(translations: {'en': 'Test'}),
          criteriaBlockIds: const ['block_c'],
        );

        final List<PromptBlock> mockPromptBlocks = [
          const PromptBlock.systemRule(
            id: 'block_a',
            slug: 'block_a',
            label: I18nText(translations: {'en': 'Block A'}),
            description: I18nText(translations: {'en': 'Desc A'}),
          ),
          const PromptBlock.runtimeVariables(
            id: 'block_c',
            slug: 'block_c',
            label: I18nText(translations: {'en': 'Block C'}),
            description: I18nText(translations: {'en': 'Desc C'}),
          ),
        ];

        final mockClient = MockStudioClient();
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => mockPromptBlocks);
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

        expect(hasAssertError, isFalse);
      },
    );

    testWidgets(
      'renders vendor-neutral cognitive tier dropdown with zero physical model suffixes',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          id: 'test_step_1',
          slug: 'test_slug',
          name: const I18nText(translations: {'en': 'Test Step'}),
          cognitiveTier: CognitiveTier.fast,
        );

        final mockClient = MockStudioClient();
        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
        when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
        when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

        final mockLogger = MockLoggerService();
        when(
          () => mockLogger.error(any(), any(), any(), any()),
        ).thenReturn(null);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              studioClientProvider.overrideWithValue(mockClient),
              loggerServiceProvider.overrideWithValue(mockLogger),
              promptBlocksControllerProvider.overrideWith(() {
                return MockPromptBlocksController([]);
              }),
              modelRegistryControllerProvider.overrideWith(() {
                return MockPopulatedModelRegistryController();
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

        final tierDropdownFinder = find.byType(
          DropdownButtonFormField<CognitiveTier>,
        );
        expect(tierDropdownFinder, findsOneWidget);

        await tester.ensureVisible(tierDropdownFinder);
        await tester.pumpAndSettle();
        await tester.tap(tierDropdownFinder);
        await tester.pumpAndSettle();

        expect(
          find.text('Fast (Zero-Thinking, Low-Latency)').last,
          findsOneWidget,
        );
        expect(
          find.text('Balanced (Light Reasoning, Standard Synthesis)').last,
          findsOneWidget,
        );
        expect(
          find.text('Deep (Heavy Reasoning, Complex Analysis)').last,
          findsOneWidget,
        );
        expect(
          find.text('Reasoning (Maximal Thinking, Scientific Rigor)').last,
          findsOneWidget,
        );

        expect(find.textContaining('['), findsNothing);
        expect(find.textContaining('gemini'), findsNothing);
        expect(find.textContaining('gpt-'), findsNothing);
        expect(find.byIcon(Icons.psychology), findsNothing);

        ErrorWidget.builder = originalErrorBuilder;
      },
    );

    testWidgets(
      'triggers AppErrorBoundary diagnostic node when preHooks contains unsupported legacy hook',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          id: 'test_step_1',
          slug: 'test_slug',
          name: const I18nText(translations: {'en': 'Test Step'}),
          preHooks: const ['legacy_unknown_hook'],
        );

        final mockClient = MockStudioClient();
        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
        when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
        when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

        final mockLogger = MockLoggerService();
        when(
          () => mockLogger.error(any(), any(), any(), any()),
        ).thenReturn(null);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              studioClientProvider.overrideWithValue(mockClient),
              loggerServiceProvider.overrideWithValue(mockLogger),
              promptBlocksControllerProvider.overrideWith(() {
                return MockPromptBlocksController([]);
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

        expect(tester.takeException(), isNotNull);
        expect(find.byIcon(Icons.report_problem), findsWidgets);
        expect(find.textContaining('legacy_unknown_hook'), findsWidgets);

        ErrorWidget.builder = originalErrorBuilder;
      },
    );

    testWidgets(
      'triggers AppErrorBoundary when PromptBlock lacks required locale and en fallback translation',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          id: 'test_step_1',
          slug: 'test_slug',
          name: const I18nText(translations: {'en': 'Test Step'}),
          criteriaBlockIds: const ['block_missing_i18n'],
        );

        final List<PromptBlock> mockPromptBlocks = [
          const PromptBlock.systemRule(
            id: 'block_missing_i18n',
            slug: 'block_missing_i18n',
            label: I18nText(translations: {}),
            description: I18nText(translations: {'en': 'Desc'}),
          ),
        ];

        final mockClient = MockStudioClient();
        when(
          () => mockClient.getPromptBlocks(),
        ).thenAnswer((_) async => mockPromptBlocks);
        when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
        when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

        final mockLogger = MockLoggerService();
        when(
          () => mockLogger.error(any(), any(), any(), any()),
        ).thenReturn(null);

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

        expect(tester.takeException(), isNotNull);
        expect(find.byIcon(Icons.report_problem), findsWidgets);
        expect(find.textContaining('block_missing_i18n'), findsWidgets);

        ErrorWidget.builder = originalErrorBuilder;
      },
    );

    testWidgets(
      'does not inject hardcoded fallback description when step description is null',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          id: 'test_step_1',
          slug: 'test_slug',
          name: const I18nText(translations: {'en': 'Actual Step Name'}),
          description: null,
        );

        final mockClient = MockStudioClient();
        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
        when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
        when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

        final mockLogger = MockLoggerService();
        when(
          () => mockLogger.error(any(), any(), any(), any()),
        ).thenReturn(null);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              studioClientProvider.overrideWithValue(mockClient),
              loggerServiceProvider.overrideWithValue(mockLogger),
              promptBlocksControllerProvider.overrideWith(() {
                return MockPromptBlocksController([]);
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

        expect(find.text('Test'), findsNothing);

        ErrorWidget.builder = originalErrorBuilder;
      },
    );
  });
}

class MockPopulatedModelRegistryController
    extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  @override
  FutureOr<List<ModelConfig>> build() async {
    return [
      const ModelConfig(
        id: 'sys_e26807f3bfa3454d',
        slug: 'default',
        type: 'model_registry',
        defaultProvider: 'google',
        tierDefinitions: {
          'fast': LlmModelConfig(
            provider: 'google',
            modelName: 'gemini/gemini-3.8-flash',
          ),
        },
      ),
    ];
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
    tierDefinitions: {},
  );
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
  Future<PromptBlockSimulationResponse> simulatePromptBlock(
    PromptBlock payload,
    Map<String, Object?> mockInputs, {
    int? targetScaleScore,
    String? targetLocale,
    String? contextText,
  }) async {
    return const PromptBlockSimulationResponse(
      renderedPrompt: 'MOCK',
      valid: true,
    );
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
    tierDefinitions: {},
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
