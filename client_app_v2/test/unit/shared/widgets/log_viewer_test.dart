import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/log_viewer.dart';
import 'package:client_app/theme/app_colors.dart';
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
    required List<String> logs,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double height = 240,
    LoggerService? logger,
  }) {
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
          body: SizedBox(
            height: height,
            child: LogViewer(logs: logs),
          ),
        ),
      ),
    );
  }

  group('LogViewer Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders log lines using semanticColors.success and monospace typography',
      (WidgetTester tester) async {
        const logEntries = [
          '[INFO] Step stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c71 initialized',
          '[PASS] Evidence verified in 140ms',
        ];

        await tester.pumpWidget(
          buildTestHarness(logs: logEntries, theme: AppTheme.dark),
        );
        await tester.pumpAndSettle();

        expect(find.text(logEntries[0]), findsOneWidget);
        expect(find.text(logEntries[1]), findsOneWidget);
        expect(find.byType(ListView), findsOneWidget);

        final firstText = tester.widget<Text>(find.text(logEntries[0]));
        expect(firstText.style?.color, equals(AppSemanticColors.dark.success));
        expect(firstText.style?.fontFamily, equals('monospace'));
      },
    );

    testWidgets(
      'Boundary 1: empty logs list renders localized sharedNoLogsAvailable in English and Finnish',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(logs: const [], locale: const Locale('en')),
        );
        await tester.pumpAndSettle();

        final enL10n = await AppLocalizations.delegate.load(const Locale('en'));
        expect(find.text(enL10n.sharedNoLogsAvailable), findsOneWidget);
        expect(find.byType(ListView), findsNothing);
        expect(find.byType(ErrorView), findsNothing);

        await tester.pumpWidget(
          buildTestHarness(logs: const [], locale: const Locale('fi')),
        );
        await tester.pumpAndSettle();

        final fiL10n = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(fiL10n.sharedNoLogsAvailable), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: single-character log line and long log entry render without layout overflow',
      (WidgetTester tester) async {
        final logs = ['A', 'B' * 500];

        await tester.pumpWidget(buildTestHarness(logs: logs));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('A'), findsOneWidget);
        expect(find.text('B' * 500), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty string log entry logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(logs: const [''], logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(ListView), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[LogViewer] VALIDATION_FAILED: Failed to render log entries',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: whitespace-only log entry amidst valid logs triggers Fail-Fast ErrorView and LoggerService',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            logs: const ['[INFO] Valid line', '   \t\n  '],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.text('[INFO] Valid line'), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[LogViewer] VALIDATION_FAILED: Failed to render log entries',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
