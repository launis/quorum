import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/widgets/logic_radar_chart.dart';
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
  String name = 'Strategic Depth',
  Map<String, String> translations = const {
    'en': 'Strategic Depth',
    'fi': 'Strateginen Syvyys',
  },
  double? score = 4.5,
  String? scoreDisplayLabel = '4.5 / 5.0',
  double? scaleMin = 1.0,
  double? scaleMax = 5.0,
  double? uiPlotRatio = 0.875,
}) {
  return MatrixScorecardRowDto(
    blockId: blockId,
    name: name,
    labelI18n: I18nText(translations: translations),
    score: score,
    scoreDisplayLabel: scoreDisplayLabel,
    scaleMin: scaleMin,
    scaleMax: scaleMax,
    uiPlotRatio: uiPlotRatio,
  );
}

void main() {
  Widget buildTestHarness({
    required List<MatrixScorecardRowDto> axes,
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
              child: LogicRadarChart(axes: axes),
            ),
          ),
        ),
      ),
    );
  }

  group('LogicRadarChart Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders 3D polygon radar chart with localized titles, pre-computed uiPlotRatio entries, and ExcludeSemantics sandboxing',
      (WidgetTester tester) async {
        final axes = [
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c71',
            name: 'Toulmin Rigor',
            translations: const {
              'en': 'Toulmin Rigor',
              'fi': 'Toulmin-tarkkuus',
            },
            score: 4.5,
            scoreDisplayLabel: '4.5 / 6.0',
            scaleMin: 1.0,
            scaleMax: 6.0,
            uiPlotRatio: 0.7,
          ),
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c72',
            name: 'Bloom Taxonomy',
            translations: const {
              'en': 'Bloom Taxonomy',
              'fi': 'Bloomin taksonomia',
            },
            score: 5.0,
            scoreDisplayLabel: '5.0 / 6.0',
            scaleMin: 1.0,
            scaleMax: 6.0,
            uiPlotRatio: 0.8,
          ),
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c73',
            name: 'Strategic Depth',
            translations: const {
              'en': 'Strategic Depth',
              'fi': 'Strateginen syvyys',
            },
            score: 3.5,
            scoreDisplayLabel: null,
            scaleMin: 1.0,
            scaleMax: 4.0,
            uiPlotRatio: 0.5,
          ),
        ];

        await tester.pumpWidget(buildTestHarness(axes: axes));
        await tester.pumpAndSettle();

        expect(find.byType(RadarChart), findsOneWidget);
        expect(
          find.ancestor(
            of: find.byType(RadarChart),
            matching: find.byType(ExcludeSemantics),
          ),
          findsWidgets,
        );

        final radarChart = tester.widget<RadarChart>(find.byType(RadarChart));
        final data = radarChart.data;
        expect(data.tickCount, equals(6));
        expect(data.radarShape, equals(RadarShape.polygon));

        final entries = data.dataSets.single.dataEntries;
        expect(entries.length, equals(3));
        expect(entries[0].value, closeTo(0.7, 1e-6));
        expect(entries[1].value, closeTo(0.8, 1e-6));
        expect(entries[2].value, closeTo(0.5, 1e-6));

        final title0 = data.getTitle!(0, 0.0);
        final title2 = data.getTitle!(2, 0.0);
        expect(title0.text, equals('Toulmin\nRigor\n(4.5 / 6.0)'));
        expect(title2.text, equals('Strategic\nDepth\n(3.5)'));
      },
    );

    testWidgets(
      'Boundary 1: exact 3-axis minimum with 0.0 and 1.0 extrema and score-based normalization renders cleanly',
      (WidgetTester tester) async {
        final axes = [
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c74',
            name: 'Min Axis',
            translations: const {'en': 'Min Axis'},
            score: null,
            scoreDisplayLabel: '0.0 / 5.0',
            scaleMin: null,
            scaleMax: null,
            uiPlotRatio: 0.0,
          ),
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c75',
            name: 'Max Axis',
            translations: const {'en': 'Max Axis'},
            score: null,
            scoreDisplayLabel: '5.0 / 5.0',
            scaleMin: null,
            scaleMax: null,
            uiPlotRatio: 1.0,
          ),
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c76',
            name: 'Score Only Axis',
            translations: const {'en': 'Score Only Axis'},
            score: 3.0,
            scoreDisplayLabel: null,
            scaleMin: 1.0,
            scaleMax: 5.0,
            uiPlotRatio: null,
          ),
        ];

        await tester.pumpWidget(buildTestHarness(axes: axes));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(RadarChart), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);

        final radarChart = tester.widget<RadarChart>(find.byType(RadarChart));
        final entries = radarChart.data.dataSets.single.dataEntries;
        expect(entries[0].value, closeTo(0.0, 1e-6));
        expect(entries[1].value, closeTo(1.0, 1e-6));
        expect(entries[2].value, closeTo(0.5, 1e-6));
      },
    );

    testWidgets(
      'Boundary 2: 5-axis polygon in narrow 220px viewport with dark theme and Finnish locale renders without overflow',
      (WidgetTester tester) async {
        final axes = List.generate(
          5,
          (i) => _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c8$i',
            name: 'Dimension $i',
            translations: {
              'en': 'Dimension $i',
              'fi': 'Strateginen Ulottuvuus $i',
            },
            score: 4.0,
            scoreDisplayLabel: '4.0 / 5.0',
            scaleMin: 1.0,
            scaleMax: 5.0,
            uiPlotRatio: 0.75,
          ),
        );

        await tester.pumpWidget(
          buildTestHarness(
            axes: axes,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 220,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(RadarChart), findsOneWidget);
        final radarChart = tester.widget<RadarChart>(find.byType(RadarChart));
        expect(
          radarChart.data.getTitle!(0, 0.0).text,
          equals('Strateginen\nUlottuvuus\n0\n(4.0 / 5.0)'),
        );
      },
    );

    testWidgets(
      'Negative 1: fewer than 3 axes (< 3) logs error via LoggerService and renders compact ErrorView without SizedBox.shrink',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final twoAxes = [
          _buildAxis(blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c71'),
          _buildAxis(blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c72'),
        ];

        await tester.pumpWidget(
          buildTestHarness(axes: twoAxes, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(RadarChart), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[LogicRadarChart] VALIDATION_FAILED: Failed to render logic radar chart',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: out-of-bounds uiPlotRatio (> 1.0), invalid scale bounds (scaleMax <= scaleMin), or missing translation triggers Fail-Fast ErrorView and LoggerService',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final invalidAxes = [
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c71',
            uiPlotRatio: 1.5,
          ),
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c72',
            scaleMin: 5.0,
            scaleMax: 5.0,
          ),
          _buildAxis(
            blockId: 'blk_0195f2c4e8a97d3b9a1c2e3f4a5b6c73',
            translations: const {},
          ),
        ];

        await tester.pumpWidget(
          buildTestHarness(axes: invalidAxes, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(RadarChart), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[LogicRadarChart] VALIDATION_FAILED: Failed to render logic radar chart',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
