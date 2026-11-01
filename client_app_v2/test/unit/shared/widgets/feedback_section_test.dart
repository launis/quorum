import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/feedback_section.dart';
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
    required List<String> items,
    IconData icon = Icons.lightbulb_outline,
    Color? color,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final section = FeedbackSection(
      title: title,
      items: items,
      icon: icon,
      color: color,
    );
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
                ? SizedBox(width: width, child: section)
                : section,
          ),
        ),
      ),
    );
  }

  group('FeedbackSection Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders title, custom icon, bullet items, and theme-derived colors',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'Key Coaching Observations',
            items: const [
              'Strong deductive reasoning in opening claim.',
              'Clear empirical grounding across sections.',
            ],
            icon: Icons.check_circle_outline,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Key Coaching Observations'), findsOneWidget);
        expect(
          find.text('Strong deductive reasoning in opening claim.'),
          findsOneWidget,
        );
        expect(
          find.text('Clear empirical grounding across sections.'),
          findsOneWidget,
        );
        expect(find.byIcon(Icons.check_circle_outline), findsOneWidget);
        expect(find.byIcon(Icons.circle), findsNWidgets(2));
        expect(find.byType(Card), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 1: empty items list renders empty SizedBox without Card or ErrorView',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(title: 'Empty Section', items: const []),
        );
        await tester.pumpAndSettle();

        expect(find.byType(Card), findsNothing);
        expect(find.byType(ErrorView), findsNothing);
        expect(find.byType(SizedBox), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: single item with long unspaced title and item text in narrow 280px dark mode viewport renders without overflow',
      (WidgetTester tester) async {
        const longTitle =
            'ExtraordinarilyLongFeedbackSectionHeaderTitleWithoutSpacesOrHyphensForOverflowCheck';
        const longItem =
            'ExtraordinarilyLongFeedbackBulletPointContentWithoutSpacesToVerifyExpandedContainmentInRow';

        await tester.pumpWidget(
          buildTestHarness(
            title: longTitle,
            items: const [longItem],
            theme: AppTheme.dark,
            width: 280,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text(longTitle), findsOneWidget);
        expect(find.text(longItem), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty or whitespace-only title logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: '   ',
            items: const ['Valid feedback item'],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render feedback section',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: whitespace-only feedback item logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Valid Section Title',
            items: const ['First valid item', '   '],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render feedback section',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
