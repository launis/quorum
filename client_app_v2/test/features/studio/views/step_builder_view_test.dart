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
  group('StepBuilderView Widget Tests', () {
    testWidgets(
      'positive: renders LLM step configuration and cognitive tier dropdown',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'stp_0195f000000070008000000000000001',
          slug: 'test_slug',
          name: const I18nText(translations: {'en': 'Test Step'}),
          cognitiveTier: CognitiveTier.balanced,
          criteriaBlockIds: const ['blk_0195f000000070008000000000000001'],
        );

        final List<PromptBlock> mockPromptBlocks = [
          const PromptBlock.systemRule(
            organizationId: 'org_0195f3a0000070008000000000000001',
            id: 'blk_0195f000000070008000000000000001',
            slug: 'block_a',
            label: I18nText(translations: {'en': 'Block A'}),
            description: I18nText(translations: {'en': 'Desc A'}),
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
                return _TestPromptBlocksController(mockPromptBlocks);
              }),
              modelRegistryControllerProvider.overrideWith(() {
                return _TestModelRegistryController();
              }),
              stepFormProvider(mockStep.id).overrideWith(() {
                return _TestStepForm(mockStep);
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

        expect(
          find.byType(DropdownButtonFormField<CognitiveTier>),
          findsOneWidget,
        );
        expect(
          find.text('Block A (blk_0195f000000070008000000000000001)'),
          findsWidgets,
        );

        ErrorWidget.builder = originalErrorBuilder;
      },
    );

    testWidgets(
      'negative: triggers AppErrorBoundary when preHooks contains unsupported hook identifier',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'stp_0195f000000070008000000000000002',
          slug: 'test_slug',
          name: const I18nText(translations: {'en': 'Test Step'}),
          preHooks: const ['unsupported_hook_name'],
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
                return _TestPromptBlocksController([]);
              }),
              modelRegistryControllerProvider.overrideWith(() {
                return _TestModelRegistryController();
              }),
              stepFormProvider(mockStep.id).overrideWith(() {
                return _TestStepForm(mockStep);
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
        expect(find.textContaining('unsupported_hook_name'), findsWidgets);

        ErrorWidget.builder = originalErrorBuilder;
      },
    );

    testWidgets(
      'negative: blocks save and shows validation error when specialist LLM step lacks role, persona, and criteria blocks',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'stp_0195f000000070008000000000000003',
          slug: 'specialist_slug',
          name: const I18nText(translations: {'en': 'Specialist Step'}),
          isSystemCore: false,
          roleBlockId: null,
          executionPersonaBlockId: null,
          criteriaBlockIds: const [],
        );

        final mockClient = MockStudioClient();
        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
        when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
        when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

        final mockLogger = MockLoggerService();
        when(
          () => mockLogger.error(any(), any(), any(), any()),
        ).thenReturn(null);

        final stepForm = _TestStepForm(mockStep);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              studioClientProvider.overrideWithValue(mockClient),
              loggerServiceProvider.overrideWithValue(mockLogger),
              promptBlocksControllerProvider.overrideWith(() {
                return _TestPromptBlocksController([]);
              }),
              modelRegistryControllerProvider.overrideWith(() {
                return _TestModelRegistryController();
              }),
              stepFormProvider(mockStep.id).overrideWith(() => stepForm),
            ],
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: StepBuilderView(stepId: mockStep.id),
            ),
          ),
        );

        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.save));
        await tester.pumpAndSettle();

        expect(stepForm.submitCalled, isFalse);
        expect(find.byType(SnackBar), findsOneWidget);

        ErrorWidget.builder = originalErrorBuilder;
      },
    );

    testWidgets(
      'negative: displays localized hint via AppExceptionX.extractLocalizedHint when save submit throws error',
      (WidgetTester tester) async {
        final originalErrorBuilder = ErrorWidget.builder;

        final mockStep = NodeStrategy.llm(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'stp_0195f000000070008000000000000004',
          slug: 'save_error_slug',
          name: const I18nText(translations: {'en': 'Error Step'}),
          isSystemCore: true,
        );

        final mockClient = MockStudioClient();
        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
        when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
        when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);

        final mockLogger = MockLoggerService();
        when(
          () => mockLogger.error(any(), any(), any(), any()),
        ).thenReturn(null);

        final stepForm = _TestStepForm(
          mockStep,
          submitError: StateError('RAW_INTERNAL_CRASH_STRING'),
        );

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              studioClientProvider.overrideWithValue(mockClient),
              loggerServiceProvider.overrideWithValue(mockLogger),
              promptBlocksControllerProvider.overrideWith(() {
                return _TestPromptBlocksController([]);
              }),
              modelRegistryControllerProvider.overrideWith(() {
                return _TestModelRegistryController();
              }),
              stepFormProvider(mockStep.id).overrideWith(() => stepForm),
            ],
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: StepBuilderView(stepId: mockStep.id),
            ),
          ),
        );

        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.save));
        await tester.pumpAndSettle();

        expect(stepForm.submitCalled, isTrue);
        expect(find.byType(SnackBar), findsOneWidget);
        expect(find.textContaining('RAW_INTERNAL_CRASH_STRING'), findsNothing);

        ErrorWidget.builder = originalErrorBuilder;
      },
    );
  });
}

class _TestPromptBlocksController extends PromptBlocksController {
  final List<PromptBlock> initialData;
  _TestPromptBlocksController(this.initialData);

  @override
  FutureOr<List<PromptBlock>> build() async => initialData;

  @override
  Future<void> refresh() async {}

  @override
  Future<PromptBlock> savePromptBlock(String id, PromptBlock payload) async =>
      payload;

  @override
  Future<void> deletePromptBlock(String id) async {}

  @override
  Future<PromptBlock> clonePromptBlock(String id) async => initialData.first;

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

class _TestModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  @override
  FutureOr<List<ModelConfig>> build() async => [];

  @override
  Future<void> refresh() async {}

  @override
  Future<ModelConfig> saveConfig(String id, ModelConfig config) async => config;

  @override
  Future<void> deleteConfig(String id) async {}

  @override
  Future<ModelConfig> createSystemConfigDraft() async => const ModelConfig(
    id: 'mrg_0195f000000070008000000000000001',
    slug: 'mock_draft_slug',
  );

  @override
  Future<ModelConfig> cloneConfig(String id) async => const ModelConfig(
    id: 'mrg_0195f000000070008000000000000002',
    slug: 'cloned_slug',
    tierDefinitions: {},
  );
}

class _TestStepForm extends StepForm {
  final NodeStrategy initialData;
  final Object? submitError;
  bool submitCalled = false;
  _TestStepForm(this.initialData, {this.submitError});

  @override
  FutureOr<NodeStrategy> build(String arg) async => initialData;

  @override
  void forceRebuild(NodeStrategy payload) {
    state = AsyncValue.data(payload);
  }

  @override
  Future<void> submit(NodeStrategy payload) async {
    submitCalled = true;
    if (submitError != null) {
      throw submitError!;
    }
  }
}
