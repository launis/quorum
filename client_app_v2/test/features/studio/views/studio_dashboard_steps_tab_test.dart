import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/studio_dashboard_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  setUpAll(() {
    registerFallbackValue(StepFilterScope.specialists);
  });

  group('StudioDashboardView Steps Tab Scope Filtering & Hardening Tests', () {
    late MockStudioClient mockClient;
    late MockLoggerService mockLogger;

    final specialistStep = NodeStrategyLogic(
      id: 'sp_01965b80000070008000000000000001',
      slug: 'specialist_step',
      name: const I18nText(translations: {'en': 'Specialist Step'}),
      description: const I18nText(translations: {'en': 'Specialist Desc'}),
      isSystemCore: false,
      hook: 'test_hook',
    );

    final systemCoreStep = NodeStrategyCausalDiscovery(
      id: 'sp_01965b80000070008000000000000002',
      slug: 'step_causal_discovery',
      name: const I18nText(translations: {'en': 'Causal Discovery'}),
      description: const I18nText(translations: {'en': 'Causal Desc'}),
      isSystemCore: true,
      expectedInputs: const ['product_text', 'chat_log', 'reflection_text'],
      engineType: EngineType.causalDiscovery,
      extractionProtocolBlockId: 'blk_01965b80000070008000000000000001',
    );

    setUp(() {
      mockClient = MockStudioClient();
      mockLogger = MockLoggerService();

      when(() => mockLogger.error(any(), any())).thenReturn(null);
      when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
      when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
      when(() => mockLogger.info(any(), any())).thenReturn(null);

      when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
      when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
      when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);
      when(() => mockClient.getWorkflows()).thenAnswer((_) async => []);
      when(() => mockClient.getOutputProfiles()).thenAnswer((_) async => []);
    });

    Widget createWidgetUnderTest() {
      return ProviderScope(
        overrides: [
          studioClientProvider.overrideWithValue(mockClient),
          loggerServiceProvider.overrideWithValue(mockLogger),
        ],
        child: const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: StudioDashboardView(),
        ),
      );
    }

    testWidgets(
      'Default filter renders specialist blueprints returned by backend',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        when(() => mockClient.getSteps(scope: any(named: 'scope'))).thenAnswer((
          invocation,
        ) async {
          final scope = invocation.namedArguments[#scope] as StepFilterScope;
          switch (scope) {
            case StepFilterScope.specialists:
              return [specialistStep];
            case StepFilterScope.systemCore:
              return [systemCoreStep];
            case StepFilterScope.all:
              return [specialistStep, systemCoreStep];
          }
        });

        await tester.pumpWidget(createWidgetUnderTest());
        await tester.pumpAndSettle();

        // Switch to Steps Tab (index 3)
        await tester.tap(find.byIcon(Icons.extension));
        await tester.pumpAndSettle();

        // Verify SegmentedButton exists and specialists item is shown
        expect(find.byType(SegmentedButton<StepFilterScope>), findsOneWidget);
        expect(find.text('Specialist Step'), findsOneWidget);
        expect(find.text('Causal Discovery'), findsNothing);
        verify(
          () => mockClient.getSteps(scope: StepFilterScope.specialists),
        ).called(1);
      },
    );

    testWidgets(
      'Selecting systemCore calls setScope and displays returned items',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        when(() => mockClient.getSteps(scope: any(named: 'scope'))).thenAnswer((
          invocation,
        ) async {
          final scope = invocation.namedArguments[#scope] as StepFilterScope;
          switch (scope) {
            case StepFilterScope.specialists:
              return [specialistStep];
            case StepFilterScope.systemCore:
              return [systemCoreStep];
            case StepFilterScope.all:
              return [specialistStep, systemCoreStep];
          }
        });

        await tester.pumpWidget(createWidgetUnderTest());
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.extension));
        await tester.pumpAndSettle();

        // Tap System Core segment
        await tester.tap(find.text('System Core'));
        await tester.pumpAndSettle();

        expect(find.text('Causal Discovery'), findsOneWidget);
        expect(find.text('Specialist Step'), findsNothing);
        verify(
          () => mockClient.getSteps(scope: StepFilterScope.systemCore),
        ).called(1);
      },
    );

    testWidgets(
      'Selecting all calls setScope and displays complete union of items',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        when(() => mockClient.getSteps(scope: any(named: 'scope'))).thenAnswer((
          invocation,
        ) async {
          final scope = invocation.namedArguments[#scope] as StepFilterScope;
          switch (scope) {
            case StepFilterScope.specialists:
              return [specialistStep];
            case StepFilterScope.systemCore:
              return [systemCoreStep];
            case StepFilterScope.all:
              return [specialistStep, systemCoreStep];
          }
        });

        await tester.pumpWidget(createWidgetUnderTest());
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.extension));
        await tester.pumpAndSettle();

        // Tap All segment
        await tester.tap(find.text('All'));
        await tester.pumpAndSettle();

        expect(find.text('Specialist Step'), findsOneWidget);
        expect(find.text('Causal Discovery'), findsOneWidget);
        verify(() => mockClient.getSteps(scope: StepFilterScope.all)).called(1);
      },
    );

    testWidgets('Empty state rendered when backend returns an empty list', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1400, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      when(
        () => mockClient.getSteps(scope: any(named: 'scope')),
      ).thenAnswer((_) async => []);

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.extension));
      await tester.pumpAndSettle();

      expect(find.text('No Steps defined.'), findsOneWidget);
    });

    testWidgets(
      'Negative Case 1: Corrupted step with empty ID or missing translation renders compact ErrorView and logs error',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final corruptedEmptyIdStep = NodeStrategyLogic(
          id: '',
          slug: 'corrupted_step',
          name: const I18nText(translations: {'en': 'Corrupted Step'}),
          isSystemCore: false,
          hook: 'test_hook',
        );

        final corruptedMissingTranslationStep = NodeStrategyLogic(
          id: 'sp_01965b80000070008000000000000003',
          slug: 'untranslated_step',
          name: const I18nText(translations: {}),
          isSystemCore: false,
          hook: 'test_hook',
        );

        when(() => mockClient.getSteps(scope: any(named: 'scope'))).thenAnswer(
          (_) async => [corruptedEmptyIdStep, corruptedMissingTranslationStep],
        );

        await tester.pumpWidget(createWidgetUnderTest());
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.extension));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsNWidgets(2));
        verify(() => mockLogger.error('Studio', any(), any(), any())).called(2);
      },
    );

    testWidgets(
      'Negative Case 2: Corrupted PromptBlock (empty ID or empty slug) in Regular Blocks and Matrices tabs renders ErrorView',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final corruptedRegularBlock = PromptBlock.systemRule(
          id: '',
          slug: 'missing_id_rule',
          label: const I18nText(translations: {'en': 'Broken Rule'}),
          description: const I18nText(translations: {'en': 'Desc'}),
        );

        final corruptedMatrixBlock = PromptBlock.matrix(
          id: 'blk_01965b80000070008000000000000002',
          slug: '',
          label: const I18nText(translations: {'en': 'Broken Matrix'}),
          description: const I18nText(translations: {'en': 'Desc'}),
          scales: const [],
        );

        when(() => mockClient.getPromptBlocks()).thenAnswer(
          (_) async => [corruptedRegularBlock, corruptedMatrixBlock],
        );
        when(
          () => mockClient.getSteps(scope: any(named: 'scope')),
        ).thenAnswer((_) async => []);

        await tester.pumpWidget(createWidgetUnderTest());
        await tester.pumpAndSettle();

        // Switch to Regular Prompt Blocks Tab (index 1)
        await tester.tap(find.byIcon(Icons.chat));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);

        // Switch to Matrices Tab (index 2)
        await tester.tap(find.byIcon(Icons.dataset));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary & Negative Case 3: Model Registry tab search filtering, boundary empty match, and corrupted config ID ErrorView',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        const validConfig = ModelConfig(
          id: 'cfg_01965b80000070008000000000000001',
          name: 'Enterprise Vertex Stack',
          defaultProvider: 'vertex_ai',
        );
        const corruptedConfig = ModelConfig(
          id: '',
          name: 'Broken Stack',
          defaultProvider: 'openai',
        );

        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig, corruptedConfig]);
        when(
          () => mockClient.getSteps(scope: any(named: 'scope')),
        ).thenAnswer((_) async => []);

        await tester.pumpWidget(createWidgetUnderTest());
        await tester.pumpAndSettle();

        // Switch to Model Registry Tab (index 5)
        await tester.tap(find.byIcon(Icons.settings));
        await tester.pumpAndSettle();

        // Valid config renders, corrupted config renders ErrorView
        expect(find.text('Enterprise Vertex Stack'), findsOneWidget);
        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.text('2 / 2'), findsOneWidget);

        // Filter to valid config only
        await tester.enterText(find.byType(TextField), 'Vertex');
        await tester.pumpAndSettle();

        expect(find.text('Enterprise Vertex Stack'), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
        expect(find.text('1 / 2'), findsOneWidget);

        // Boundary: search query with 0 matches renders empty state
        await tester.enterText(find.byType(TextField), 'non_existent_xyz_999');
        await tester.pumpAndSettle();

        expect(find.text('0 / 2'), findsOneWidget);
        expect(find.text('No System Configs defined.'), findsOneWidget);

        // Clear search button resets query
        await tester.tap(find.byIcon(Icons.clear));
        await tester.pumpAndSettle();

        expect(find.text('2 / 2'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative Case 4: Backend network failure on Steps and PromptBlocks tabs renders ErrorView with working Retry',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        var failSteps = true;
        when(() => mockClient.getSteps(scope: any(named: 'scope'))).thenAnswer((
          _,
        ) async {
          if (failSteps) {
            throw AppException.server('Backend unavailable');
          }
          return [specialistStep];
        });

        await tester.pumpWidget(createWidgetUnderTest());
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.extension));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);

        // Recover on retry
        failSteps = false;
        await tester.tap(find.text('Retry'));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsNothing);
        expect(find.text('Specialist Step'), findsOneWidget);
      },
    );
  });
}
