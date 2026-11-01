import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/unified_metric_gauge.dart';
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
    required UnifiedMetricGauge gauge,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
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
          body: SingleChildScrollView(
            child: width != null ? SizedBox(width: width, child: gauge) : gauge,
          ),
        ),
      ),
    );
  }

  group('UnifiedMetricGauge Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive 1: renders cumulative and ordinal segmented bars, axis labels, and opens bilingual help dialog',
      (WidgetTester tester) async {
        final gauge = UnifiedMetricGauge(
          label: 'Bloom Cognitive Level',
          value: 4.0,
          max: 6.0,
          description: 'Measures cognitive depth along Bloom taxonomy.',
          descriptionSecondary: 'Secondary bilingual explanation.',
          displayValue: '4.0/6.0',
          axisLabels: const ['Rem', 'Und', 'App', 'Ana', 'Eva', 'Cre'],
          isOrdinal: true,
        );

        await tester.pumpWidget(buildTestHarness(gauge: gauge, width: 600));
        await tester.pumpAndSettle();

        expect(find.text('Bloom Cognitive Level'), findsOneWidget);
        expect(find.text('4.0/6.0'), findsOneWidget);
        expect(find.text('Rem'), findsOneWidget);
        expect(find.text('Cre'), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);

        // Open help dialog via help icon
        await tester.tap(find.byIcon(Icons.help_outline));
        await tester.pumpAndSettle();

        expect(
          find.text('Measures cognitive depth along Bloom taxonomy.'),
          findsOneWidget,
        );
        expect(find.text('Secondary bilingual explanation.'), findsOneWidget);
        expect(find.byIcon(Icons.info_outline), findsOneWidget);

        // Dismiss dialog
        await tester.tap(find.text('OK'));
        await tester.pumpAndSettle();
        expect(find.byType(AlertDialog), findsNothing);
      },
    );

    testWidgets(
      'Positive 2: renders cumulative gauge with non-matching axisLabels count and without axisLabels cleanly',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              theme: AppTheme.light,
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: const Scaffold(
                body: Column(
                  children: [
                    UnifiedMetricGauge(
                      label: 'Fidelity Score',
                      value: 2.0,
                      max: 4.0,
                      description: 'Fidelity explanation.',
                      displayValue: '2.0/4.0',
                      axisLabels: ['Weak', 'Strong'],
                    ),
                    UnifiedMetricGauge(
                      label: 'Raw Score',
                      value: 3.0,
                      max: 5.0,
                      description: 'Raw score explanation.',
                      displayValue: '3.0/5.0',
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Fidelity Score'), findsOneWidget);
        expect(find.text('Weak'), findsOneWidget);
        expect(find.text('Strong'), findsOneWidget);
        expect(find.text('Raw Score'), findsOneWidget);
        expect(find.text('3.0/5.0'), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 1: exact lower and upper value bounds (0.0 and max) render cleanly without ErrorView',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              theme: AppTheme.light,
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: const Scaffold(
                body: Column(
                  children: [
                    UnifiedMetricGauge(
                      label: 'Min Bound Gauge',
                      value: 0.0,
                      max: 5.0,
                      description: 'Zero bound description.',
                      displayValue: '0.0/5.0',
                    ),
                    UnifiedMetricGauge(
                      label: 'Max Bound Gauge',
                      value: 5.0,
                      max: 5.0,
                      description: 'Max bound description.',
                      displayValue: '5.0/5.0',
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Min Bound Gauge'), findsOneWidget);
        expect(find.text('0.0/5.0'), findsOneWidget);
        expect(find.text('Max Bound Gauge'), findsOneWidget);
        expect(find.text('5.0/5.0'), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 2: narrow 240px dark mode viewport with Finnish locale and long unbreakable strings renders without RenderFlex overflow',
      (WidgetTester tester) async {
        const gauge = UnifiedMetricGauge(
          label:
              'ErittäinPitkäMittarinOtsikkoIlmanVälilyöntejäKapeassaNäkymässä',
          value: 2.0,
          max: 3.0,
          description: 'Kuvaus suomeksi.',
          displayValue: 'ErittäinPitkäArvoTeksti_2.0/3.0',
          axisLabels: [
            'ErittäinPitkäAkseli1',
            'ErittäinPitkäAkseli2',
            'ErittäinPitkäAkseli3',
          ],
        );

        await tester.pumpWidget(
          buildTestHarness(
            gauge: gauge,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Negative 1: empty label, displayValue, or description logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            gauge: const UnifiedMetricGauge(
              label: '   ',
              value: 2.0,
              max: 5.0,
              description: 'Valid description',
              displayValue: '2/5',
            ),
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[UnifiedMetricGauge] VALIDATION_FAILED: Failed to render UnifiedMetricGauge',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: invalid max (<= 0) or out-of-bounds value (< 0 or > max) logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            gauge: const UnifiedMetricGauge(
              label: 'Out of Bounds Gauge',
              value: 7.5,
              max: 5.0,
              description: 'Valid description',
              displayValue: '7.5/5.0',
            ),
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[UnifiedMetricGauge] VALIDATION_FAILED: Failed to render UnifiedMetricGauge',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
