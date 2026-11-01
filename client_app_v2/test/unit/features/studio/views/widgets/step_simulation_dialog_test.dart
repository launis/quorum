import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/step_simulation_dialog.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations_en.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockStudioClient extends Mock implements StudioClient {}

class _MockLoggerService extends Mock implements LoggerService {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  final l10n = AppLocalizationsEn();
  late _MockStudioClient mockStudioClient;
  late _MockLoggerService mockLogger;

  const stepWithInputs = NodeStrategy.llm(
    id: 'sp_01965b80000070008000000000000010',
    slug: 'step_sim_test',
    name: I18nText(translations: {'en': 'Simulation Step'}),
    expectedInputs: ['source_doc', 'user_goal'],
  );

  const stepWithoutInputs = NodeStrategy.llm(
    id: 'sp_01965b80000070008000000000000011',
    slug: 'step_no_inputs',
    name: I18nText(translations: {'en': 'No Inputs Step'}),
    expectedInputs: [],
  );

  setUpAll(() {
    registerFallbackValue(const StepSimulationRequest(step: stepWithInputs));
  });

  setUp(() {
    mockStudioClient = _MockStudioClient();
    mockLogger = _MockLoggerService();

    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
    when(() => mockLogger.info(any(), any())).thenReturn(null);
  });

  Widget buildTestApp(Widget child) {
    return ProviderScope(
      overrides: [
        studioClientProvider.overrideWithValue(mockStudioClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('fi')],
        home: Scaffold(body: child),
      ),
    );
  }

  group('StepSimulationDialog', () {
    testWidgets(
      'positive: wide layout renders expected inputs, executes simulation, and switches preview tabs',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        StepSimulationRequest? capturedRequest;
        when(() => mockStudioClient.simulateStep(any())).thenAnswer((
          invocation,
        ) async {
          capturedRequest =
              invocation.positionalArguments.first as StepSimulationRequest;
          return const StepSimulationResponse(
            valid: true,
            errors: [],
            renderedPrompt: '{"type": "object", "title": "SimulatedSchema"}',
            trace: StepSimulationTraceDto(
              executionTimeMs: 42.5,
              estimatedTokens: 310,
            ),
            promptContext: PromptContextDto(
              staticMessages: [
                LlmMessageDto(role: 'system', content: 'STATIC_BLOCK_TEXT'),
              ],
              dynamicMessages: [
                LlmMessageDto(role: 'user', content: 'DYNAMIC_CONTEXT_TEXT'),
              ],
            ),
          );
        });

        await tester.pumpWidget(
          buildTestApp(const StepSimulationDialog(step: stepWithInputs)),
        );
        await tester.pumpAndSettle();

        expect(find.text(l10n.stepSimulationTitle), findsOneWidget);
        expect(find.text('source_doc'), findsOneWidget);
        expect(find.text('user_goal'), findsOneWidget);

        // Switch locale from 'en' to 'fi'
        await tester.tap(find.byType(DropdownButton<String>));
        await tester.pumpAndSettle();
        await tester.tap(find.text(l10n.profileLanguageFi).last);
        await tester.pumpAndSettle();

        // Enter values into expected inputs
        await tester.enterText(
          find.widgetWithText(TextFormField, 'source_doc'),
          'Doc payload A',
        );
        await tester.enterText(
          find.widgetWithText(TextFormField, 'user_goal'),
          'Goal payload B',
        );

        // Run simulation
        await tester.tap(
          find.widgetWithText(FilledButton, l10n.runSimulationBtn),
        );
        await tester.pumpAndSettle();

        expect(capturedRequest, isNotNull);
        expect(capturedRequest!.targetLocale, 'fi');
        expect(capturedRequest!.mockInputs['source_doc'], 'Doc payload A');
        expect(capturedRequest!.mockInputs['user_goal'], 'Goal payload B');

        // Verify trace metrics and tabs
        expect(
          find.text('${l10n.stepSimulationExecutionTime}: 42.5 ms'),
          findsOneWidget,
        );
        expect(
          find.text('${l10n.stepSimulationEstimatedTokens}: ~310'),
          findsOneWidget,
        );
        expect(find.textContaining('STATIC_BLOCK_TEXT'), findsOneWidget);

        // Switch to Dynamic tab
        await tester.tap(find.text(l10n.previewPromptDynamicTab));
        await tester.pumpAndSettle();
        expect(find.textContaining('DYNAMIC_CONTEXT_TEXT'), findsOneWidget);

        // Switch to Schema tab
        await tester.tap(find.text(l10n.previewPromptSchemaTab));
        await tester.pumpAndSettle();
        expect(find.textContaining('SimulatedSchema'), findsOneWidget);
      },
    );

    testWidgets(
      'negative: displays error banner when simulateStep throws and dismisses banner on close icon tap',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        when(
          () => mockStudioClient.simulateStep(any()),
        ).thenThrow(AppException.validation('Step simulation backend failure'));

        await tester.pumpWidget(
          buildTestApp(const StepSimulationDialog(step: stepWithInputs)),
        );
        await tester.pumpAndSettle();

        await tester.tap(
          find.widgetWithText(FilledButton, l10n.runSimulationBtn),
        );
        await tester.pumpAndSettle();

        expect(
          find.textContaining('Step simulation backend failure'),
          findsOneWidget,
        );
        expect(find.byIcon(Icons.error_outline), findsOneWidget);

        // Dismiss the inline error banner (second close icon after AppBar leading close button)
        final closeButtons = find.byIcon(Icons.close);
        expect(closeButtons, findsNWidgets(2));
        await tester.tap(closeButtons.last);
        await tester.pumpAndSettle();

        expect(
          find.textContaining('Step simulation backend failure'),
          findsNothing,
        );
      },
    );

    testWidgets(
      'negative & boundary: narrow layout with empty expectedInputs and invalid response errors',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(700, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        StepSimulationRequest? capturedRequest;
        when(() => mockStudioClient.simulateStep(any())).thenAnswer((
          invocation,
        ) async {
          capturedRequest =
              invocation.positionalArguments.first as StepSimulationRequest;
          return const StepSimulationResponse(
            valid: false,
            errors: ['Missing extraction protocol block', 'Unbound input key'],
            renderedPrompt: '',
            promptContext: null,
          );
        });

        await tester.pumpWidget(
          buildTestApp(const StepSimulationDialog(step: stepWithoutInputs)),
        );
        await tester.pumpAndSettle();

        // Empty expectedInputs notice is visible
        expect(find.text(l10n.noExpectedInputsNotice), findsOneWidget);

        // Clear context field to test fallback to '[SIMULATED CONTEXT DOCUMENT]'
        await tester.enterText(find.byType(TextFormField).first, '   ');

        // Run simulation
        await tester.tap(
          find.widgetWithText(FilledButton, l10n.runSimulationBtn),
        );
        await tester.pumpAndSettle();

        expect(capturedRequest, isNotNull);
        expect(capturedRequest!.contextText, '[SIMULATED CONTEXT DOCUMENT]');

        // Switch to Preview tab in narrow layout
        await tester.tap(find.text(l10n.previewPromptTitle));
        await tester.pumpAndSettle();

        expect(
          find.text('• Missing extraction protocol block'),
          findsOneWidget,
        );
        expect(find.text('• Unbound input key'), findsOneWidget);
        expect(find.text('---'), findsOneWidget);
      },
    );

    testWidgets(
      'boundary: dirty state guard prompts confirmation before closing when inputs are modified',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        await tester.pumpWidget(
          buildTestApp(
            Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog<void>(
                    context: context,
                    builder: (_) =>
                        const StepSimulationDialog(step: stepWithInputs),
                  );
                },
                child: const Text('Open Dialog'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();
        expect(find.byType(StepSimulationDialog), findsOneWidget);

        // Clean state: tapping close immediately pops the dialog
        await tester.tap(find.byIcon(Icons.close));
        await tester.pumpAndSettle();
        expect(find.byType(StepSimulationDialog), findsNothing);

        // Re-open and dirty the form
        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();
        await tester.enterText(
          find.widgetWithText(TextFormField, 'source_doc'),
          'Modified input',
        );

        await tester.tap(find.byIcon(Icons.close));
        await tester.pumpAndSettle();

        // Confirmation dialog appears
        expect(find.text(l10n.discardChangesConfirmTitle), findsOneWidget);

        // Keep editing keeps StepSimulationDialog open
        await tester.tap(find.text(l10n.keepEditingButtonLabel));
        await tester.pumpAndSettle();
        expect(find.byType(StepSimulationDialog), findsOneWidget);

        // Tap close again and confirm discard
        await tester.tap(find.byIcon(Icons.close));
        await tester.pumpAndSettle();
        await tester.tap(find.text(l10n.discardButtonLabel));
        await tester.pumpAndSettle();
        expect(find.byType(StepSimulationDialog), findsNothing);
      },
    );
  });
}
