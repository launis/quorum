import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/step_simulation_dialog.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

class FakeStepSimulationRequest extends Fake implements StepSimulationRequest {}

void main() {
  setUpAll(() {
    registerFallbackValue(FakeStepSimulationRequest());
  });

  Widget createTestWidget(Widget child, {List overrides = const []}) {
    final mockLogger = MockLoggerService();
    return ProviderScope(
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        ...overrides.cast(),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en')],
        home: Scaffold(body: child),
      ),
    );
  }

  NodeStrategy createSampleStep({
    List<String> expectedInputs = const ['product_text', 'prior_analysis'],
  }) {
    return NodeStrategy.llm(
      id: 'sp_1111222233334444',
      slug: 'sample_simulation_step',
      name: const I18nText(translations: {'en': 'Sample Simulation Step'}),
      expectedInputs: expectedInputs,
    );
  }

  group('StepSimulationDialog Desktop Tests', () {
    testWidgets(
      'renders dynamic input fields for each key in step.expectedInputs',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final step = createSampleStep(
          expectedInputs: ['user_query', 'system_context'],
        );

        await tester.pumpWidget(
          createTestWidget(StepSimulationDialog(step: step)),
        );
        await tester.pumpAndSettle();

        expect(find.text('user_query'), findsOneWidget);
        expect(find.text('system_context'), findsOneWidget);
        expect(find.text('[SIMULATED CONTEXT DOCUMENT]'), findsOneWidget);
        expect(find.text('English (en)'), findsOneWidget);
      },
    );

    testWidgets('renders notice when expectedInputs is empty', (tester) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final step = createSampleStep(expectedInputs: const []);

      await tester.pumpWidget(
        createTestWidget(StepSimulationDialog(step: step)),
      );
      await tester.pumpAndSettle();

      expect(
        find.text('No expected inputs declared for this step.'),
        findsOneWidget,
      );
    });

    testWidgets(
      'clicking Run Simulation executes simulation and renders preview tabs with trace telemetry',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final mockClient = MockStudioClient();
        when(() => mockClient.simulateStep(any())).thenAnswer(
          (_) async => const StepSimulationResponse(
            valid: true,
            errors: [],
            renderedPrompt: '<xml>Compiled Step Prompt Schema</xml>',
            trace: StepSimulationTraceDto(
              executionTimeMs: 15.4,
              estimatedTokens: 420,
            ),
            promptContext: PromptContextDto(
              staticMessages: [
                LlmMessageDto(
                  role: 'system',
                  content: 'Step Static System Message',
                ),
              ],
              dynamicMessages: [
                LlmMessageDto(
                  role: 'user',
                  content: 'Step Dynamic Execution Claim',
                ),
              ],
              metadata: {},
            ),
          ),
        );

        final step = createSampleStep(expectedInputs: ['input_one']);

        await tester.pumpWidget(
          createTestWidget(
            overrides: [studioClientProvider.overrideWithValue(mockClient)],
            StepSimulationDialog(step: step),
          ),
        );
        await tester.pumpAndSettle();

        // Tap Run Simulation
        final runBtn = find.widgetWithText(FilledButton, 'Run Simulation');
        expect(runBtn, findsOneWidget);
        await tester.tap(runBtn);
        await tester.pumpAndSettle();

        // Verify trace metrics displayed
        expect(find.textContaining('15.4 ms'), findsOneWidget);
        expect(find.textContaining('~420'), findsOneWidget);

        // Verify prompt context displayed in tabs
        expect(
          find.textContaining('Step Static System Message'),
          findsOneWidget,
        );

        // Switch to Dynamic tab
        await tester.tap(find.text('Claims & Rules (Payload)'));
        await tester.pumpAndSettle();
        expect(
          find.textContaining('Step Dynamic Execution Claim'),
          findsOneWidget,
        );

        // Switch to Schema tab
        final schemaTab = find.text('Compiled Prompt & Schema (Output)');
        await tester.ensureVisible(schemaTab);
        await tester.tap(schemaTab);
        await tester.pumpAndSettle();
        expect(
          find.textContaining('Compiled Step Prompt Schema'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'displays validation errors banner when simulation returns valid == false',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final mockClient = MockStudioClient();
        when(() => mockClient.simulateStep(any())).thenAnswer(
          (_) async => const StepSimulationResponse(
            valid: false,
            errors: [
              'Referenced criteria block blk_missing not found',
              'Context document payload empty',
            ],
            renderedPrompt: '',
            trace: StepSimulationTraceDto(
              executionTimeMs: 2.1,
              estimatedTokens: 0,
            ),
            promptContext: null,
          ),
        );

        final step = createSampleStep(expectedInputs: ['query']);

        await tester.pumpWidget(
          createTestWidget(
            overrides: [studioClientProvider.overrideWithValue(mockClient)],
            StepSimulationDialog(step: step),
          ),
        );
        await tester.pumpAndSettle();

        final runBtn = find.widgetWithText(FilledButton, 'Run Simulation');
        await tester.tap(runBtn);
        await tester.pumpAndSettle();

        expect(
          find.textContaining(
            'Referenced criteria block blk_missing not found',
          ),
          findsOneWidget,
        );
        expect(
          find.textContaining('Context document payload empty'),
          findsOneWidget,
        );
      },
    );

    testWidgets('adapts layout between wide (>= 900px) and compact (< 900px)', (
      tester,
    ) async {
      // 1. Wide Viewport: Two-Pane Row
      tester.view.physicalSize = const Size(1200, 800);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final step = createSampleStep();

      await tester.pumpWidget(
        createTestWidget(StepSimulationDialog(step: step)),
      );
      await tester.pumpAndSettle();

      expect(find.byType(Row), findsWidgets);
      expect(find.byType(VerticalDivider), findsOneWidget);

      // 2. Compact Viewport: TabBarView
      tester.view.physicalSize = const Size(800, 600);
      await tester.pumpWidget(
        createTestWidget(StepSimulationDialog(step: step)),
      );
      await tester.pumpAndSettle();

      expect(find.byType(TabBarView), findsWidgets);
    });

    testWidgets(
      'displays inline error banner (zero AlertDialog, zero SnackBar) when simulation call throws an exception',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final mockClient = MockStudioClient();
        when(
          () => mockClient.simulateStep(any()),
        ).thenThrow(Exception('Network connection drop during simulation'));

        final step = createSampleStep(expectedInputs: ['input_data']);

        await tester.pumpWidget(
          createTestWidget(
            overrides: [studioClientProvider.overrideWithValue(mockClient)],
            StepSimulationDialog(step: step),
          ),
        );
        await tester.pumpAndSettle();

        final runBtn = find.widgetWithText(FilledButton, 'Run Simulation');
        await tester.tap(runBtn);
        await tester.pumpAndSettle();

        expect(find.byType(AlertDialog), findsNothing);
        expect(find.byType(SnackBar), findsNothing);
        expect(
          find.textContaining('Network connection drop during simulation'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'PopScope intercepts dismissal with discard dialog when input controllers are dirty',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final step = createSampleStep(expectedInputs: ['query']);

        await tester.pumpWidget(
          createTestWidget(
            Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (ctx) => StepSimulationDialog(step: step),
                  );
                },
                child: const Text('Open Simulation'),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Open Simulation'));
        await tester.pumpAndSettle();

        expect(find.byType(StepSimulationDialog), findsOneWidget);

        // Enter text into expected input field to make it dirty
        final inputField = find.widgetWithText(TextFormField, 'query');
        await tester.enterText(inputField, 'dirty input value');
        await tester.pumpAndSettle();

        // Tap close icon in AppBar
        final closeBtn = find.byIcon(Icons.close);
        await tester.tap(closeBtn);
        await tester.pumpAndSettle();

        // Discard confirmation dialog must appear
        expect(find.byType(AlertDialog), findsOneWidget);
        expect(find.text('Discard changes?'), findsOneWidget);
        expect(find.text('Continue Editing'), findsOneWidget);
        expect(find.text('Discard Changes'), findsOneWidget);

        // Tapping 'Continue Editing' retains dialog
        await tester.tap(find.text('Continue Editing'));
        await tester.pumpAndSettle();
        expect(find.byType(StepSimulationDialog), findsOneWidget);

        // Tap close again and choose 'Discard Changes'
        await tester.tap(closeBtn);
        await tester.pumpAndSettle();
        await tester.tap(find.text('Discard Changes'));
        await tester.pumpAndSettle();

        expect(find.byType(StepSimulationDialog), findsNothing);
      },
    );

    testWidgets(
      'dismisses immediately without discard dialog when inputs are pristine',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final step = createSampleStep(expectedInputs: ['query']);

        await tester.pumpWidget(
          createTestWidget(
            Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (ctx) => StepSimulationDialog(step: step),
                  );
                },
                child: const Text('Open Simulation'),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Open Simulation'));
        await tester.pumpAndSettle();

        expect(find.byType(StepSimulationDialog), findsOneWidget);

        // Tap close icon without edits
        final closeBtn = find.byIcon(Icons.close);
        await tester.tap(closeBtn);
        await tester.pumpAndSettle();

        // Must pop cleanly without AlertDialog
        expect(find.byType(AlertDialog), findsNothing);
        expect(find.byType(StepSimulationDialog), findsNothing);
      },
    );
  });
}
