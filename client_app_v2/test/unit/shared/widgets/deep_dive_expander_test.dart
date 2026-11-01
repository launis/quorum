import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';
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
    required Widget child,
    IconData icon = Icons.analytics_outlined,
    bool initiallyExpanded = false,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final expander = DeepDiveExpander(
      title: title,
      icon: icon,
      initiallyExpanded: initiallyExpanded,
      child: child,
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
                ? SizedBox(width: width, child: expander)
                : expander,
          ),
        ),
      ),
    );
  }

  group('DeepDiveExpander Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders Theme-sovereign card, leading icon, collapsed state by default, and reveals child when tapped',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'Analytical Deep Dive',
            icon: Icons.terminal,
            child: const Text('Expanded Payload Content'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Analytical Deep Dive'), findsOneWidget);
        expect(find.byIcon(Icons.terminal), findsOneWidget);
        expect(find.text('Expanded Payload Content'), findsNothing);

        final iconWidget = tester.widget<Icon>(find.byIcon(Icons.terminal));
        expect(iconWidget.color, equals(AppTheme.light.colorScheme.primary));

        final tile = tester.widget<ExpansionTile>(find.byType(ExpansionTile));
        expect(tile.childrenPadding, equals(AppSpacing.p16));

        await tester.tap(find.text('Analytical Deep Dive'));
        await tester.pumpAndSettle();

        expect(find.text('Expanded Payload Content'), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 1: initiallyExpanded=true renders child immediately on mount',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'Pre-Expanded Section',
            initiallyExpanded: true,
            child: const Text('Immediate Child Widget'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Pre-Expanded Section'), findsOneWidget);
        expect(find.text('Immediate Child Widget'), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: narrow 280px viewport in dark mode truncates long title with ellipsis without RenderFlex overflow',
      (WidgetTester tester) async {
        const longTitle =
            'ExtraordinarilyLongEnterpriseDeepDiveSectionHeaderWithoutBreaksOrSpaces';

        await tester.pumpWidget(
          buildTestHarness(
            title: longTitle,
            initiallyExpanded: true,
            theme: AppTheme.dark,
            width: 280,
            child: const Text('Dark Mode Narrow Child'),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        final titleText = tester.widget<Text>(find.text(longTitle));
        expect(titleText.overflow, equals(TextOverflow.ellipsis));
        expect(titleText.maxLines, equals(1));
      },
    );

    testWidgets(
      'Negative 1: empty string title logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: '',
            logger: logger,
            child: const Text('Unreachable Child'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.text('Unreachable Child'), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render deep dive expander',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: whitespace-only title logs error via LoggerService and renders compact ErrorView without silent fallback',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: '   \t\n  ',
            logger: logger,
            child: const Text('Unreachable Child'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.text('Unreachable Child'), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render deep dive expander',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
