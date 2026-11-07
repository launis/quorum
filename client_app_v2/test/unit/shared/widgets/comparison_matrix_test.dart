import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/comparison_matrix.dart';
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
  Widget buildTestHarness(
    ComparisonMatrixData comparisonData, {
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final child = ComparisonMatrix(comparisonData: comparisonData);
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
            child: width != null ? SizedBox(width: width, child: child) : child,
          ),
        ),
      ),
    );
  }

  group('ComparisonMatrix Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders localized headers, positive/negative/zero deltas, and expands reasoning blocks',
      (WidgetTester tester) async {
        const data = ComparisonMatrixData(
          leftLabel: 'Evaluator Alpha',
          rightLabel: 'Evaluator Beta',
          rows: <ComparisonRowData>[
            ComparisonRowData(
              observation: 'Fidelity',
              left: ComparisonSideScore(
                score: 4.5,
                reasoning: 'Strong premise alignment.',
              ),
              right: ComparisonSideScore(
                score: 3.0,
                reasoning: 'Minor inferential leap detected.',
              ),
              delta: 1.5,
            ),
            ComparisonRowData(
              observation: 'Cohesion',
              left: ComparisonSideScore(score: 2.0),
              right: ComparisonSideScore(score: 3.5),
              delta: -1.5,
            ),
            ComparisonRowData(
              observation: 'Grounding',
              left: ComparisonSideScore(score: 4.0),
              right: ComparisonSideScore(score: 4.0),
              delta: 0.0,
            ),
          ],
        );

        await tester.pumpWidget(buildTestHarness(data));
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.text(l10n.sharedComparativeEvaluation), findsOneWidget);
        expect(find.text(l10n.lblObservation), findsOneWidget);
        expect(find.text('Evaluator Alpha'), findsOneWidget);
        expect(find.text('Evaluator Beta'), findsOneWidget);
        expect(find.text(l10n.sharedDeltaColumnHeader), findsOneWidget);

        expect(find.text('FIDELITY'), findsOneWidget);
        expect(find.text('COHESION'), findsOneWidget);
        expect(find.text('GROUNDING'), findsOneWidget);
        expect(find.byIcon(Icons.arrow_upward), findsOneWidget);
        expect(find.byIcon(Icons.arrow_downward), findsOneWidget);
        expect(find.text('='), findsOneWidget);

        await tester.tap(find.text('FIDELITY'));
        await tester.pumpAndSettle();

        expect(find.text('Evaluator Alpha:'), findsOneWidget);
        expect(find.text('Strong premise alignment.'), findsOneWidget);
        expect(find.text('Evaluator Beta:'), findsOneWidget);
        expect(find.text('Minor inferential leap detected.'), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 1: empty data or empty rows list renders localized empty state card',
      (WidgetTester tester) async {
        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        await tester.pumpWidget(buildTestHarness(const ComparisonMatrixData()));
        await tester.pumpAndSettle();
        expect(find.text(l10n.sharedNoComparisonData), findsOneWidget);

        await tester.pumpWidget(
          buildTestHarness(
            const ComparisonMatrixData(rows: <ComparisonRowData>[]),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.text(l10n.sharedNoComparisonData), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: narrow 280px viewport in dark mode with Finnish locale contains long labels without overflow',
      (WidgetTester tester) async {
        const data = ComparisonMatrixData(
          leftLabel: 'ErittäinPitkäEnsimmäisenArvioijanNimi',
          rightLabel: 'ErittäinPitkäToisenArvioijanNimi',
          rows: <ComparisonRowData>[
            ComparisonRowData(
              observation:
                  'PoikkeuksellisenPitkäHavaintokriteerinTunnisteIlmanVälilyöntejä',
              left: ComparisonSideScore(
                score: 99.9,
                reasoning: 'Pitkä perusteluteksti ensimmäiselle arviolle.',
              ),
              right: ComparisonSideScore(
                score: 10.1,
                reasoning: 'Pitkä perusteluteksti toiselle arviolle.',
              ),
              delta: 89.8,
            ),
          ],
        );

        await tester.pumpWidget(
          buildTestHarness(
            data,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 280,
          ),
        );
        await tester.pumpAndSettle();

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.sharedComparativeEvaluation), findsOneWidget);
        expect(find.text(l10nFi.sharedDeltaColumnHeader), findsOneWidget);
        expect(tester.takeException(), isNull);
      },
    );

    testWidgets(
      'Negative 1: corrupted rows payload logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        const corruptedData = ComparisonMatrixData(
          leftLabel: 'Judge A',
          rightLabel: 'Judge B',
          isCorrupted: true,
        );

        await tester.pumpWidget(
          buildTestHarness(corruptedData, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render comparison matrix',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: missing required labels or row fields logs error and renders ErrorView without silent fallback',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        const incompleteData = ComparisonMatrixData(
          leftLabel: 'Judge A',
          rightLabel: 'Judge B',
          rows: <ComparisonRowData>[
            ComparisonRowData(
              observation: 'Logic',
              left: ComparisonSideScore(score: null),
              right: ComparisonSideScore(score: 3),
              delta: 1.0,
            ),
          ],
        );

        await tester.pumpWidget(
          buildTestHarness(incompleteData, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render comparison matrix',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
