import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/validation_timeline_widget.dart';
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
    required List<dynamic> events,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final widget = ValidationTimelineWidget(title: title, events: events);
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
                ? SizedBox(width: width, child: widget)
                : widget,
          ),
        ),
      ),
    );
  }

  group('ValidationTimelineWidget Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders timeline events with formatted HH:mm timestamps, content, and alert color styling',
      (WidgetTester tester) async {
        final events = <Object?>[
          <String, Object?>{
            'timestamp': '2026-11-01T08:15:30Z',
            'label': 'Schema Preflight Verified',
            'content': 'All 12 tables validated cleanly.',
            'is_alert': false,
          },
          <String, Object?>{
            'timestamp': '2026-11-01T08:16:04Z',
            'label': 'Anchor Contiguity Check',
            'content': 'Threshold violation detected in segment 2.',
            'is_alert': true,
          },
        ];

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Validation Audit Timeline',
            events: events,
            theme: AppTheme.light,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Validation Audit Timeline'), findsOneWidget);
        expect(find.text('08:15'), findsOneWidget);
        expect(find.text('08:16'), findsOneWidget);
        expect(find.text('Schema Preflight Verified'), findsOneWidget);
        expect(find.text('All 12 tables validated cleanly.'), findsOneWidget);
        expect(find.text('Anchor Contiguity Check'), findsOneWidget);
        expect(
          find.text('Threshold violation detected in segment 2.'),
          findsOneWidget,
        );

        final alertLabel = tester.widget<Text>(
          find.text('Anchor Contiguity Check'),
        );
        expect(
          alertLabel.style?.color,
          equals(AppTheme.light.colorScheme.error),
        );

        final normalLabel = tester.widget<Text>(
          find.text('Schema Preflight Verified'),
        );
        expect(
          normalLabel.style?.color,
          equals(AppTheme.light.colorScheme.onSurface),
        );
      },
    );

    testWidgets(
      'Boundary 1: empty events list renders localized sharedNoTimelineData in English and Finnish without ErrorView',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'Empty Validation Timeline',
            events: const <dynamic>[],
            locale: const Locale('en'),
          ),
        );
        await tester.pumpAndSettle();

        final enL10n = await AppLocalizations.delegate.load(const Locale('en'));
        expect(find.text(enL10n.sharedNoTimelineData), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Tyhjä Aikajana',
            events: const <dynamic>[],
            locale: const Locale('fi'),
          ),
        );
        await tester.pumpAndSettle();

        final fiL10n = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(fiL10n.sharedNoTimelineData), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: single event with non-ISO timestamp and long unbroken label on narrow 280px dark mode viewport renders without overflow',
      (WidgetTester tester) async {
        final events = <Object?>[
          <String, Object?>{
            'timestamp': 'T+00:42s',
            'label':
                'ExtraordinarilyLongValidationTimelineEventLabelWithoutSpacesOrBreaks',
          },
        ];

        await tester.pumpWidget(
          buildTestHarness(
            title:
                'ExtraordinarilyLongValidationTimelineHeaderTitleWithoutBreaks',
            events: events,
            theme: AppTheme.dark,
            width: 280,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('T+00:42s'), findsOneWidget);
        expect(
          find.text(
            'ExtraordinarilyLongValidationTimelineEventLabelWithoutSpacesOrBreaks',
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Negative 1: empty or whitespace-only title logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: '   ',
            events: const <dynamic>[],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[ValidationTimelineWidget] VALIDATION_FAILED: Failed to render validation timeline',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: malformed event item (non-Map or missing label) logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Malformed Events Timeline',
            events: <Object?>[
              <String, Object?>{
                'timestamp': '2026-11-01T09:00:00Z',
                'label': '',
              },
            ],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[ValidationTimelineWidget] VALIDATION_FAILED: Failed to render validation timeline',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
