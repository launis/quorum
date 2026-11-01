import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/widgets/quadrant_matrix_chart.dart';
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

MatrixScorecardRowDto _buildAxis({
  String blockId = 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c71',
  String name = 'Cognitive Depth',
  Map<String, String> translations = const {
    'en': 'Cognitive Depth',
    'fi': 'Kognitiivinen syvyys',
  },
  double? score = 4.0,
  double? scaleMin = 1.0,
  double? scaleMax = 5.0,
  double? uiPlotRatio = 0.75,
}) {
  return MatrixScorecardRowDto(
    blockId: blockId,
    name: name,
    labelI18n: I18nText(translations: translations),
    score: score,
    scaleMin: scaleMin,
    scaleMax: scaleMax,
    uiPlotRatio: uiPlotRatio,
  );
}

void main() {
  Widget buildTestHarness({
    required MatrixScorecardRowDto xAxis,
    required MatrixScorecardRowDto yAxis,
    MatrixScorecardRowDto? zAxis,
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
              child: QuadrantMatrixChart(
                xAxis: xAxis,
                yAxis: yAxis,
                zAxis: zAxis,
              ),
            ),
          ),
        ),
      ),
    );
  }

  group('QuadrantMatrixChart Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders 4 localized diagnostic quadrants, 3D scatter chart, and ExcludeSemantics sandboxing',
      (WidgetTester tester) async {
        final xAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c71',
          name: 'Cognitive Depth',
          translations: const {
            'en': 'Cognitive Depth',
            'fi': 'Kognitiivinen syvyys',
          },
          score: 4.5,
          scaleMin: 1.0,
          scaleMax: 6.0,
          uiPlotRatio: 0.7,
        );
        final yAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c72',
          name: 'Formulaic Load',
          translations: const {
            'en': 'Formulaic Load',
            'fi': 'Kaavamainen kuorma',
          },
          score: 2.0,
          scaleMin: 1.0,
          scaleMax: 6.0,
          uiPlotRatio: 0.2,
        );
        final zAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c73',
          name: 'Variance Magnitude',
          translations: const {
            'en': 'Variance Magnitude',
            'fi': 'Varianssin voimakkuus',
          },
          score: 3.5,
          scaleMin: 1.0,
          scaleMax: 4.0,
          uiPlotRatio: 0.5,
        );

        await tester.pumpWidget(
          buildTestHarness(xAxis: xAxis, yAxis: yAxis, zAxis: zAxis),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ScatterChart), findsOneWidget);
        expect(
          find.ancestor(
            of: find.byType(ScatterChart),
            matching: find.byType(ExcludeSemantics),
          ),
          findsWidgets,
        );
        expect(find.text('Flattery & Filler Phrases'), findsOneWidget);
        expect(find.text('Fluent Mastery'), findsOneWidget);
        expect(find.text('Novice / Routine'), findsOneWidget);
        expect(find.text('Organic Insight'), findsOneWidget);
        expect(find.text('X: Cognitive Depth (4.5 / 6.0)'), findsOneWidget);
        expect(find.text('Y: Formulaic Load (2.0 / 6.0)'), findsOneWidget);
        expect(
          find.text('Z (Bubble Size): Variance Magnitude (3.5 / 4.0)'),
          findsOneWidget,
        );

        final scatterChart = tester.widget<ScatterChart>(
          find.byType(ScatterChart),
        );
        final spot = scatterChart.data.scatterSpots.single;
        expect(spot.x, closeTo(0.7, 1e-6));
        expect(spot.y, closeTo(0.2, 1e-6));
      },
    );

    testWidgets(
      'Boundary 1: exact uiPlotRatio extrema (0.0 and 1.0) without zAxis render cleanly',
      (WidgetTester tester) async {
        final xAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c74',
          name: 'Min Boundary Axis',
          translations: const {'en': 'Min Boundary Axis'},
          score: 0.0,
          scaleMin: 0.0,
          scaleMax: 100.0,
          uiPlotRatio: 0.0,
        );
        final yAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c75',
          name: 'Max Boundary Axis',
          translations: const {'en': 'Max Boundary Axis'},
          score: 100.0,
          scaleMin: 0.0,
          scaleMax: 100.0,
          uiPlotRatio: 1.0,
        );

        await tester.pumpWidget(buildTestHarness(xAxis: xAxis, yAxis: yAxis));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(ScatterChart), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
        expect(find.textContaining('Z (Bubble Size)'), findsNothing);
      },
    );

    testWidgets(
      'Boundary 2: narrow 240px viewport with long axis names in dark mode and Finnish locale renders without overflow',
      (WidgetTester tester) async {
        const longName =
            'ExtraordinarilyLongQuadrantAxisDimensionTitleForOverflowVerification';
        final xAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c76',
          name: longName,
          translations: const {'en': longName, 'fi': longName},
          score: 2.5,
          scaleMin: 1.0,
          scaleMax: 5.0,
          uiPlotRatio: 0.375,
        );
        final yAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c77',
          name: longName,
          translations: const {'en': longName, 'fi': longName},
          score: 4.0,
          scaleMin: 1.0,
          scaleMax: 5.0,
          uiPlotRatio: 0.75,
        );
        final zAxis = _buildAxis(
          blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c78',
          name: longName,
          translations: const {'en': longName, 'fi': longName},
          score: 5.0,
          scaleMin: 1.0,
          scaleMax: 5.0,
          uiPlotRatio: 1.0,
        );

        await tester.pumpWidget(
          buildTestHarness(
            xAxis: xAxis,
            yAxis: yAxis,
            zAxis: zAxis,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('Mielistely & Täytefraasit'), findsOneWidget);
        expect(find.text('Asiantunteva & Sujuva'), findsOneWidget);
        expect(find.text('Alkeellinen / Rutiini'), findsOneWidget);
        expect(find.text('Aito & Omaääninen'), findsOneWidget);
        expect(find.textContaining('Z (Pallon Koko):'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: null or out-of-bounds uiPlotRatio (< 0.0 or > 1.0) logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final invalidXAxis = _buildAxis(uiPlotRatio: -0.05);
        final validYAxis = _buildAxis(uiPlotRatio: 0.5);

        await tester.pumpWidget(
          buildTestHarness(
            xAxis: invalidXAxis,
            yAxis: validYAxis,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(ScatterChart), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[QuadrantMatrixChart] VALIDATION_FAILED: Failed to render quadrant matrix chart',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: invalid scale bounds (scaleMax <= scaleMin) or empty blockId triggers Fail-Fast ErrorView and LoggerService',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final validXAxis = _buildAxis();
        final invalidScaleYAxis = _buildAxis(scaleMin: 5.0, scaleMax: 5.0);

        await tester.pumpWidget(
          buildTestHarness(
            xAxis: validXAxis,
            yAxis: invalidScaleYAxis,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(ScatterChart), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[QuadrantMatrixChart] VALIDATION_FAILED: Failed to render quadrant matrix chart',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
