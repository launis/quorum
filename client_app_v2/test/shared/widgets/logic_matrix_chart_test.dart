import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/widgets/logic_matrix_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const xAxis = MatrixScorecardRowDto(
    blockId: 'axis_x',
    labelI18n: I18nText(translations: {'en': 'Axis X', 'fi': 'Akseli X'}),
    name: 'Axis X',
    score: 2.0,
    scaleMin: 0.0,
    scaleMax: 4.0,
    uiPlotRatio: 0.5,
  );

  const yAxis = MatrixScorecardRowDto(
    blockId: 'axis_y',
    labelI18n: I18nText(translations: {'en': 'Axis Y', 'fi': 'Akseli Y'}),
    name: 'Axis Y',
    score: 1.0,
    scaleMin: 0.0,
    scaleMax: 2.0,
    uiPlotRatio: 0.5,
  );

  Widget createChartWidget() {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: const Locale('en'),
      home: const Scaffold(
        body: Center(
          child: SizedBox(
            width: 500,
            height: 300,
            child: LogicMatrixChart(
              xAxis: xAxis,
              yAxis: yAxis,
            ),
          ),
        ),
      ),
    );
  }

  testWidgets(
    'LogicMatrixChart renders standard 2D Cartesian chart without quadrants',
    (tester) async {
      await tester.pumpWidget(createChartWidget());
      await tester.pumpAndSettle();

      // Axis labels must be visible
      expect(find.textContaining('Axis X'), findsOneWidget);
      expect(find.textContaining('Axis Y'), findsOneWidget);

      // Quadrant labels must NOT be present in pure Cartesian scatter chart
      expect(find.text('Flattery & Filler Phrases'), findsNothing);
      expect(find.text('Fluent Mastery'), findsNothing);
      expect(find.text('Novice / Routine'), findsNothing);
      expect(find.text('Organic Insight'), findsNothing);
    },
  );
}
