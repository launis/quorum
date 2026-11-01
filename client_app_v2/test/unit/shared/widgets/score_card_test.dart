import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/score_card.dart';
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
    required String label,
    required double? value,
    double? maxValue,
    String? description,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final card = ScoreCard(
      label: label,
      value: value,
      maxValue: maxValue,
      description: description,
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
            child: width != null ? SizedBox(width: width, child: card) : card,
          ),
        ),
      ),
    );
  }

  group('ScoreCard Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive 1: renders label, description, and formatted score interpolating to AppSemanticColors.success at max value',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            label: 'Toulmin Argumentation',
            value: 5.0,
            maxValue: 5.0,
            description: 'Evaluates claim-warrant-backing coherence.',
            theme: AppTheme.light,
            locale: const Locale('en'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Toulmin Argumentation'), findsOneWidget);
        expect(
          find.text('Evaluates claim-warrant-backing coherence.'),
          findsOneWidget,
        );
        expect(find.text('5'), findsOneWidget);
        expect(find.byType(Card), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);

        final scoreText = tester.widget<Text>(find.text('5'));
        expect(scoreText.style?.color, equals(AppSemanticColors.light.success));
      },
    );

    testWidgets(
      'Positive 2: formats decimal score according to active locale and renders localized dataUnavailable when value is null',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            label: 'Strategic Depth',
            value: null,
            description: 'Missing sensor evaluation.',
            locale: const Locale('fi'),
          ),
        );
        await tester.pumpAndSettle();

        final fiL10n = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text('Strategic Depth'), findsOneWidget);
        expect(find.text('Missing sensor evaluation.'), findsOneWidget);
        expect(find.text(fiL10n.dataUnavailable), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Strategic Depth',
            value: 3.5,
            maxValue: 5.0,
            locale: const Locale('en'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('3.5'), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 1: exact lower bound (0.0) resolves to colorScheme.error and exact upper bound (maxValue) resolves to semanticColors.success in dark mode',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            label: 'Boundary Zero',
            value: 0.0,
            maxValue: 10.0,
            theme: AppTheme.dark,
          ),
        );
        await tester.pumpAndSettle();

        final zeroText = tester.widget<Text>(find.text('0'));
        expect(zeroText.style?.color, equals(AppTheme.dark.colorScheme.error));

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Boundary Max',
            value: 10.0,
            maxValue: 10.0,
            theme: AppTheme.dark,
          ),
        );
        await tester.pumpAndSettle();

        final maxText = tester.widget<Text>(find.text('10'));
        expect(maxText.style?.color, equals(AppSemanticColors.dark.success));
      },
    );

    testWidgets(
      'Boundary 2: narrow 200px viewport with long unbreakable label and description renders without RenderFlex overflow',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            label:
                'ExtraordinarilyLongEnterpriseScoreCardLabelWithoutSpacesOrBreaksForOverflowTesting',
            value: 4.2,
            maxValue: 5.0,
            description:
                'ExtraordinarilyLongEnterpriseScoreCardDescriptionWithoutAnySpacesOrBreaksForOverflowVerification' *
                2,
            theme: AppTheme.dark,
            width: 200,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(Card), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Negative 1: empty or whitespace label logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(label: '   ', value: 3.0, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('VALIDATION_FAILED: Failed to render ScoreCard'),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: out-of-bounds value (< 0 or > maxValue) or non-positive maxValue logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Invalid High Score',
            value: 5.1,
            maxValue: 5.0,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(logger.loggedErrors, isNotEmpty);

        logger.loggedErrors.clear();

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Negative Score',
            value: -0.1,
            maxValue: 5.0,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(logger.loggedErrors, isNotEmpty);

        logger.loggedErrors.clear();

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Invalid Max Value',
            value: 1.0,
            maxValue: 0.0,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(logger.loggedErrors, isNotEmpty);
      },
    );
  });
}
