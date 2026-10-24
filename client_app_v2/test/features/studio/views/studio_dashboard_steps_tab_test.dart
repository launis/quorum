import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
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

  group('StudioDashboardView Steps Tab Scope Filtering Tests', () {
    late MockStudioClient mockClient;
    late MockLoggerService mockLogger;

    final specialistStep = NodeStrategyLogic(
      id: 'sp_spec00000000001',
      slug: 'specialist_step',
      name: const I18nText(translations: {'en': 'Specialist Step'}),
      description: const I18nText(translations: {'en': 'Specialist Desc'}),
      isSystemCore: false,
      hook: 'test_hook',
    );

    final systemCoreStep = NodeStrategyCausalDiscovery(
      id: 'sp_c4a5a1d15c00438a',
      slug: 'step_causal_discovery',
      name: const I18nText(translations: {'en': 'Causal Discovery'}),
      description: const I18nText(translations: {'en': 'Causal Desc'}),
      isSystemCore: true,
      expectedInputs: const ['product_text', 'chat_log', 'reflection_text'],
      engineType: EngineType.causalDiscovery,
      extractionProtocolBlockId: 'blk_proto00000001',
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
  });
}
