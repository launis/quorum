import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/generic_grid.dart';
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
    required String title,
    required Map<String, Object?> data,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final grid = GenericGrid(title: title, data: data);

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
            child: width != null ? SizedBox(width: width, child: grid) : grid,
          ),
        ),
      ),
    );
  }

  group('GenericGrid Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders title and standard + highlighted metric items using Theme tokens',
      (WidgetTester tester) async {
        final data = <String, Object?>{
          'items': <Object?>[
            <String, Object?>{
              'label': 'Total Tokens',
              'value': '14,250',
              'highlight': false,
            },
            <String, Object?>{
              'label': 'Cohesion Score',
              'value': '94.2%',
              'highlight': true,
            },
            <String, Object?>{'label': 'Latency', 'value': '420 ms'},
          ],
        };

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Execution Telemetry Metrics',
            data: data,
            width: 600,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Execution Telemetry Metrics'), findsOneWidget);
        expect(find.text('Total Tokens'), findsOneWidget);
        expect(find.text('14,250'), findsOneWidget);
        expect(find.text('Cohesion Score'), findsOneWidget);
        expect(find.text('94.2%'), findsOneWidget);
        expect(find.text('Latency'), findsOneWidget);
        expect(find.text('420 ms'), findsOneWidget);
        expect(find.byType(Card), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 1: empty items list renders Card header cleanly without ErrorView',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'Empty Metrics Section',
            data: const <String, Object?>{'items': <Object?>[]},
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Empty Metrics Section'), findsOneWidget);
        expect(find.byType(Card), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 2: narrow 240px dark mode viewport with long unbreakable strings renders single-column with ellipsis without overflow',
      (WidgetTester tester) async {
        final data = <String, Object?>{
          'items': <Object?>[
            <String, Object?>{
              'label':
                  'ExtraordinarilyLongEnterpriseTelemetryMetricLabelWithoutBreaksOrSpaces',
              'value':
                  'ExtraordinarilyLongEnterpriseTelemetryMetricValueWithoutBreaksOrSpaces_999999999',
              'highlight': true,
            },
          ],
        };

        await tester.pumpWidget(
          buildTestHarness(
            title:
                'ExtraordinarilyLongEnterpriseGridSectionHeaderWithoutAnySpacesOrBreaks',
            data: data,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(Card), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Negative 1: empty or whitespace title logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: '   ',
            data: const <String, Object?>{'items': <Object?>[]},
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('VALIDATION_FAILED: Failed to render GenericGrid'),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: malformed items payload or missing item label/value logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Valid Title',
            data: const <String, Object?>{
              'items': <Object?>[
                <String, Object?>{'label': 'Valid Label', 'value': '   '},
              ],
            },
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('VALIDATION_FAILED: Failed to render GenericGrid'),
          ),
          isTrue,
        );
      },
    );
  });
}
