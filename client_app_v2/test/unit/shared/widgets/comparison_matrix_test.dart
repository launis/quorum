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
    Map<String, Object?> comparisonData, {
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
        final data = <String, Object?>{
          'left_label': 'Evaluator Alpha',
          'right_label': 'Evaluator Beta',
          'rows': <Object?>[
            <String, Object?>{
              'observation': 'Fidelity',
              'left': <String, Object?>{
                'score': 4.5,
                'reasoning': 'Strong premise alignment.',
              },
              'right': <String, Object?>{
                'score': 3.0,
                'reasoning': 'Minor inferential leap detected.',
              },
              'delta': 1.5,
            },
            <String, Object?>{
              'observation': 'Cohesion',
              'left': <String, Object?>{'score': 2.0},
              'right': <String, Object?>{'score': 3.5},
              'delta': -1.5,
            },
            <String, Object?>{
              'observation': 'Grounding',
              'left': <String, Object?>{'score': 4.0},
              'right': <String, Object?>{'score': 4.0},
              'delta': 0.0,
            },
          ],
        };

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
      'Boundary 1: empty data map or empty rows list renders localized empty state card',
      (WidgetTester tester) async {
        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        await tester.pumpWidget(buildTestHarness(const {}));
        await tester.pumpAndSettle();
        expect(find.text(l10n.sharedNoComparisonData), findsOneWidget);

        await tester.pumpWidget(
          buildTestHarness(const {'rows': <Object?>[]}),
        );
        await tester.pumpAndSettle();
        expect(find.text(l10n.sharedNoComparisonData), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: narrow 280px viewport in dark mode with Finnish locale contains long labels without overflow',
      (WidgetTester tester) async {
        final data = <String, Object?>{
          'left_label': 'ErittäinPitkäEnsimmäisenArvioijanNimi',
          'right_label': 'ErittäinPitkäToisenArvioijanNimi',
          'rows': <Object?>[
            <String, Object?>{
              'observation':
                  'PoikkeuksellisenPitkäHavaintokriteerinTunnisteIlmanVälilyöntejä',
              'left': <String, Object?>{
                'score': 99.9,
                'reasoning': 'Pitkä perusteluteksti ensimmäiselle arviolle.',
              },
              'right': <String, Object?>{
                'score': 10.1,
                'reasoning': 'Pitkä perusteluteksti toiselle arviolle.',
              },
              'delta': 89.8,
            },
          ],
        };

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
      'Negative 1: malformed rows type logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final corruptedData = <String, Object?>{
          'left_label': 'Judge A',
          'right_label': 'Judge B',
          'rows': 'invalid_non_list_payload',
        };

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
        final incompleteData = <String, Object?>{
          'left_label': 'Judge A',
          'right_label': 'Judge B',
          'rows': <Object?>[
            <String, Object?>{
              'observation': 'Logic',
              'left': <String, Object?>{'score': 'not_a_number'},
              'right': <String, Object?>{'score': 3},
              'delta': 1.0,
            },
          ],
        };

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
