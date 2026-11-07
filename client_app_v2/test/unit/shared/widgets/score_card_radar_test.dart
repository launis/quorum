import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/score_card_radar.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:dio/dio.dart';
import 'package:fl_chart/fl_chart.dart';
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
    required ScoreCardRadarData cardData,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double width = 600,
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
            child: SizedBox(
              width: width,
              child: ScoreCardRadar(cardData: cardData),
            ),
          ),
        ),
      ),
    );
  }

  group('ScoreCardRadar Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders header, score badge, RadarChart with ExcludeSemantics, and detailed breakdown list for >= 3 dimensions',
      (WidgetTester tester) async {
        const cardData = ScoreCardRadarData(
          agentName: 'Logician Specialist',
          verdict: 'Strong dialectical rigor verified across dimensions.',
          totalScore: 4.3,
          minScore: 1,
          maxScore: 5,
          dimensions: <ScoreCardDimensionData>[
            ScoreCardDimensionData(
              dimensionLabel: 'lblFidelity',
              score: 4.5,
              reasoning: 'Havainto: Strict adherence to premises.',
            ),
            ScoreCardDimensionData(
              dimensionLabel: 'lblStrategicDepth',
              score: 4.0,
              reasoning: 'Long-term second-order consequences modeled.',
            ),
            ScoreCardDimensionData(
              dimensionLabel: 'lblCredibility',
              score: 4.4,
              reasoning: 'All citations anchored to verified sources.',
            ),
          ],
        );

        await tester.pumpWidget(buildTestHarness(cardData: cardData));
        await tester.pumpAndSettle();

        expect(find.text('Logician Specialist'), findsOneWidget);
        expect(
          find.text('Strong dialectical rigor verified across dimensions.'),
          findsOneWidget,
        );
        expect(find.text('4.3'), findsOneWidget);
        expect(find.text('(Scale: 1-5)'), findsOneWidget);

        expect(find.byType(RadarChart), findsOneWidget);
        expect(
          find.ancestor(
            of: find.byType(RadarChart),
            matching: find.byType(ExcludeSemantics),
          ),
          findsWidgets,
        );

        final radarChart = tester.widget<RadarChart>(find.byType(RadarChart));
        final entries = radarChart.data.dataSets.single.dataEntries;
        expect(entries.length, equals(3));
        expect(entries[0].value, closeTo(4.5, 1e-6));
        expect(entries[1].value, closeTo(4.0, 1e-6));
        expect(entries[2].value, closeTo(4.4, 1e-6));

        expect(
          radarChart.data.getTitle!(0, 0.0).text,
          equals('Reasoning Fidelity'),
        );
        expect(find.text('Detailed Breakdown'), findsOneWidget);
        expect(find.text('Reasoning Fidelity'), findsOneWidget);
        expect(find.text('Strategic Depth'), findsOneWidget);
        expect(find.text('Credibility'), findsOneWidget);
        expect(find.text('Strict adherence to premises.'), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 1: empty dimensions list and null totalScore renders localized placeholders without RadarChart or breakdown list',
      (WidgetTester tester) async {
        const cardData = ScoreCardRadarData(
          dimensions: <ScoreCardDimensionData>[],
          totalScore: null,
        );

        await tester.pumpWidget(buildTestHarness(cardData: cardData));
        await tester.pumpAndSettle();

        expect(find.text('Unknown Agent'), findsOneWidget);
        expect(find.text('Data unavailable'), findsOneWidget);
        expect(
          find.text('No detailed observation data available.'),
          findsOneWidget,
        );
        expect(find.byType(RadarChart), findsNothing);
        expect(find.text('Detailed Breakdown'), findsNothing);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 2: 2 dimensions (< 3) in narrow 240px viewport with dark theme and Finnish locale renders breakdown list without RadarChart or overflow',
      (WidgetTester tester) async {
        const cardData = ScoreCardRadarData(
          agentName:
              'ErittäinPitkäAsiantuntijaAgentinNimiIlmanVälilyöntejäKapeassaNäkymässä',
          verdict:
              'ErittäinPitkäTuomioTekstiJokaTestaaRivitystäJaEllipsisKatkaisuaKapeassaTilassa',
          totalScore: 3.8,
          minScore: 1,
          maxScore: 6,
          dimensions: <ScoreCardDimensionData>[
            ScoreCardDimensionData(
              dimensionLabel: 'lblBloomScore',
              score: 4.0,
              reasoning: 'Korkean tason synteesi.',
            ),
            ScoreCardDimensionData(
              dimensionLabel: 'CustomUnmappedDimensionKeyWithoutSpaces',
              score: 3.5,
              reasoning: 'Toinen perustelu.',
            ),
          ],
        );

        await tester.pumpWidget(
          buildTestHarness(
            cardData: cardData,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(RadarChart), findsNothing);
        expect(find.text('3.8'), findsOneWidget);
        expect(find.text('Bloom-pisteet'), findsOneWidget);
        expect(
          find.text('CustomUnmappedDimensionKeyWithoutSpaces'),
          findsOneWidget,
        );
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Negative 1: corrupted dimensions or malformed dimension entry logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            cardData: const ScoreCardRadarData(
              agentName: 'Broken Agent',
              isCorrupted: true,
            ),
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[ScoreCardRadar] VALIDATION_FAILED: Failed to render ScoreCardRadar',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: invalid scale bounds (maxScore <= minScore) or null dimension score logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            cardData: const ScoreCardRadarData(
              agentName: 'Invalid Bounds Agent',
              minScore: 5,
              maxScore: 5,
              dimensions: <ScoreCardDimensionData>[
                ScoreCardDimensionData(
                  dimensionLabel: 'lblFidelity',
                  score: null,
                ),
              ],
            ),
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(Card), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[ScoreCardRadar] VALIDATION_FAILED: Failed to render ScoreCardRadar',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
