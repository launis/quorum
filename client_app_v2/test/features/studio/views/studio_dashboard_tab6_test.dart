import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/studio_dashboard_view.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

class MockModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  final List<ModelConfig> _initialData;
  MockModelRegistryController([this._initialData = const []]);

  @override
  FutureOr<List<ModelConfig>> build() async => _initialData;

  @override
  Future<ModelConfig> saveConfig(String id, ModelConfig config) async => config;

  @override
  Future<ModelConfig> createSystemConfigDraft() async => const ModelConfig(
    id: 'sys_draft12345678',
    slug: 'draft',
    type: 'model_registry',
  );

  @override
  Future<ModelConfig> cloneConfig(String id) async => const ModelConfig(
    id: 'sys_cloned123456',
    slug: 'cloned',
    type: 'model_registry',
  );

  @override
  Future<void> deleteConfig(String id) async {}

  @override
  Future<void> refresh() async {}
}

class MockWorkflowsController extends WorkflowsController {
  @override
  FutureOr<List<Workflow>> build() async => [];
}

class MockStepsController extends StepsController {
  @override
  FutureOr<List<NodeStrategy>> build() async => [];
}

class MockPromptBlocksController extends PromptBlocksController {
  @override
  FutureOr<List<PromptBlock>> build() async => [];
}

void main() {
  group('StudioDashboardView Tab 6 Model Registry Tests', () {
    late MockStudioClient mockClient;
    late MockLoggerService mockLogger;

    setUp(() {
      mockClient = MockStudioClient();
      mockLogger = MockLoggerService();

      when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
      when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
      when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);
      when(() => mockClient.getWorkflows()).thenAnswer((_) async => []);
      when(() => mockClient.getOutputProfiles()).thenAnswer((_) async => []);
      when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
    });

    Widget createWidgetUnderTest(List<ModelConfig> configs) {
      return ProviderScope(
        overrides: [
          studioClientProvider.overrideWithValue(mockClient),
          loggerServiceProvider.overrideWithValue(mockLogger),
          modelRegistryControllerProvider.overrideWith(() {
            return MockModelRegistryController(configs);
          }),
          promptBlocksControllerProvider.overrideWith(() {
            return MockPromptBlocksController();
          }),
          workflowsControllerProvider.overrideWith(() {
            return MockWorkflowsController();
          }),
          stepsControllerProvider.overrideWith(() {
            return MockStepsController();
          }),
        ],
        child: const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: StudioDashboardView(),
        ),
      );
    }

    testWidgets(
      'Renders Tab 6 with Model Registry items and tier count badge',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final mockConfigs = [
          const ModelConfig(
            id: 'sys_e26807f3bfa3454d',
            name: 'Google Gemini Sovereign Stack',
            slug: 'gemini-stack',
            type: 'model_registry',
            defaultProvider: 'google',
            tierDefinitions: {
              'fast': LlmModelConfig(
                provider: 'google',
                modelName: 'gemini-3.8-flash',
              ),
              'balanced': LlmModelConfig(
                provider: 'google',
                modelName: 'gemini-3.8-flash',
              ),
              'deep': LlmModelConfig(
                provider: 'google',
                modelName: 'gemini-3.8-pro',
              ),
              'reasoning': LlmModelConfig(
                provider: 'google',
                modelName: 'gemini-3.8-pro',
              ),
            },
          ),
          const ModelConfig(
            id: 'sys_6f8b1c4a2e0d49f1',
            name: 'OpenAI O-Series Stack',
            slug: 'openai-stack',
            type: 'model_registry',
            defaultProvider: 'openai',
            tierDefinitions: {
              'fast': LlmModelConfig(provider: 'openai', modelName: 'gpt-5.1'),
            },
          ),
        ];

        await tester.pumpWidget(createWidgetUnderTest(mockConfigs));
        await tester.pumpAndSettle();

        // Switch to Tab 6 (Model Registry Tab)
        await tester.tap(find.byIcon(Icons.settings));
        await tester.pumpAndSettle();

        // Verify header and count chip
        expect(find.text('Google Gemini Sovereign Stack'), findsOneWidget);
        expect(find.text('OpenAI O-Series Stack'), findsOneWidget);
        expect(find.text('2 / 2'), findsOneWidget);
      },
    );

    testWidgets(
      'Filtering search query updates active count and hides non-matching stacks',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final mockConfigs = [
          const ModelConfig(
            id: 'sys_e26807f3bfa3454d',
            name: 'Google Gemini Sovereign Stack',
            defaultProvider: 'google',
          ),
          const ModelConfig(
            id: 'sys_6f8b1c4a2e0d49f1',
            name: 'OpenAI O-Series Stack',
            defaultProvider: 'openai',
          ),
        ];

        await tester.pumpWidget(createWidgetUnderTest(mockConfigs));
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.settings));
        await tester.pumpAndSettle();

        // Enter search query
        final searchField = find.byType(TextField);
        expect(searchField, findsOneWidget);

        await tester.enterText(searchField, 'gemini');
        await tester.pumpAndSettle();

        // Gemini is visible, OpenAI is filtered out
        expect(find.text('Google Gemini Sovereign Stack'), findsOneWidget);
        expect(find.text('OpenAI O-Series Stack'), findsNothing);
        expect(find.text('1 / 2'), findsOneWidget);
      },
    );

    testWidgets('Empty search match displays empty state placeholder', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1400, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final mockConfigs = [
        const ModelConfig(
          id: 'sys_e26807f3bfa3454d',
          name: 'Google Gemini Sovereign Stack',
        ),
      ];

      await tester.pumpWidget(createWidgetUnderTest(mockConfigs));
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      final searchField = find.byType(TextField);
      await tester.enterText(searchField, 'non_existent_query_xyz');
      await tester.pumpAndSettle();

      expect(find.text('0 / 1'), findsOneWidget);
      expect(find.text('No System Configs defined.'), findsOneWidget);
    });
  });
}
