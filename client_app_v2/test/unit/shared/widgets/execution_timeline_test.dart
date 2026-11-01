import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/execution_timeline.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _RecordingLoggerService extends LoggerService {
  final List<String> loggedErrors = [];

  _RecordingLoggerService()
    : super(
        telemetryDio: Dio(BaseOptions(baseUrl: 'https://test.invalid'))
          ..interceptors.add(
            InterceptorsWrapper(
              onRequest: (options, handler) => handler.resolve(
                Response(requestOptions: options, statusCode: 200),
              ),
            ),
          ),
      );

  @override
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    loggedErrors.add('[$context] $message');
  }
}

void main() {
  Widget buildTestHarness({
    required List<ExecutionStep> steps,
    bool compact = false,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final timeline = ExecutionTimeline(steps: steps, compact: compact);
    return ProviderScope(
      overrides: [
        if (logger != null) loggerServiceProvider.overrideWithValue(logger),
      ],
      child: MaterialApp(
        theme: theme ?? AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: width != null
                ? SizedBox(width: width, child: timeline)
                : timeline,
          ),
        ),
      ),
    );
  }

  group('ExecutionTimeline Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders steps with labels, icons, progress bar, and localized anomaly retry message',
      (WidgetTester tester) async {
        final steps = [
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c71',
            label: 'Step Ingestion',
            status: 'passed',
            durationMs: 1200,
            progress: 100,
          ),
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c72',
            label: 'Step Analysis',
            status: 'running',
            progress: 45,
            messageCode: 'event_llm_anomaly_retry',
          ),
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c73',
            label: 'Step Synthesis',
            status: 'failed',
            lastError: 'Quota exceeded',
            hasWarning: true,
          ),
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c74',
            label: 'Step Queued',
            status: 'queued',
          ),
        ];

        await tester.pumpWidget(buildTestHarness(steps: steps));
        await tester.pump();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.text('Step Ingestion'), findsOneWidget);
        expect(find.text('Step Analysis'), findsOneWidget);
        expect(find.text('Step Synthesis'), findsOneWidget);
        expect(find.text('Step Queued'), findsOneWidget);
        expect(find.text('45%'), findsOneWidget);
        expect(find.text('Quota exceeded'), findsOneWidget);
        expect(find.text(l10n.eventLlmAnomalyRetry), findsOneWidget);
        expect(find.byType(LinearProgressIndicator), findsOneWidget);
        expect(find.byIcon(Icons.check_circle), findsOneWidget);
        expect(find.byIcon(Icons.play_circle_fill), findsOneWidget);
        expect(find.byIcon(Icons.error), findsOneWidget);
        expect(find.byIcon(Icons.hourglass_empty), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 1: empty steps list renders empty SizedBox without Card or ErrorView',
      (WidgetTester tester) async {
        await tester.pumpWidget(buildTestHarness(steps: const []));
        await tester.pumpAndSettle();

        expect(find.byType(Card), findsNothing);
        expect(find.byType(ErrorView), findsNothing);
        expect(find.byType(SizedBox), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: progress at exact bounds (0 and 100) and narrow 280px dark mode viewport render without RenderFlex overflow',
      (WidgetTester tester) async {
        final steps = [
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c75',
            label:
                'ExtraordinarilyLongEnterpriseExecutionStepLabelWithoutBreaksOrSpaces',
            status: 'running',
            progress: 0,
          ),
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c76',
            label: 'Completed Boundary Step',
            status: 'running',
            progress: 100,
            hasWarning: true,
          ),
        ];

        await tester.pumpWidget(
          buildTestHarness(
            steps: steps,
            compact: true,
            theme: AppTheme.dark,
            width: 280,
          ),
        );
        await tester.pump();

        expect(tester.takeException(), isNull);
        expect(find.text('0%'), findsOneWidget);
        expect(find.text('100%'), findsOneWidget);
        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty step label or id logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final invalidSteps = [
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c77',
            label: '   ',
            status: 'running',
          ),
        ];

        await tester.pumpWidget(
          buildTestHarness(steps: invalidSteps, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render execution timeline',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: out-of-bounds progress (< 0 or > 100) logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final outOfBoundsSteps = [
          const ExecutionStep(
            id: 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c78',
            label: 'Invalid Progress Step',
            status: 'running',
            progress: 105,
          ),
        ];

        await tester.pumpWidget(
          buildTestHarness(steps: outOfBoundsSteps, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render execution timeline',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
