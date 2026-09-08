import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/widgets/quadrant_matrix_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const xAxis = MatrixScorecardRowDto(
    blockId: 'axis_x',
    labelI18n: I18nText(translations: {'en': 'Axis X', 'fi': 'Akseli X'}),
    name: 'Axis X',
    score: 2.0,
    scaleMin: 1.0,
    scaleMax: 3.0,
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

  Widget createChartWidget({Locale locale = const Locale('en')}) {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: locale,
      home: const Scaffold(
        body: Center(
          child: SizedBox(
            width: 500,
            height: 300,
            child: QuadrantMatrixChart(
              xAxis: xAxis,
              yAxis: yAxis,
            ),
          ),
        ),
      ),
    );
  }

  testWidgets(
    'QuadrantMatrixChart renders diagnostic quadrant watermarks in English',
    (tester) async {
      await tester.pumpWidget(createChartWidget(locale: const Locale('en')));
      await tester.pumpAndSettle();

      // Axis labels must be visible
      expect(find.textContaining('Axis X'), findsOneWidget);
      expect(find.textContaining('Axis Y'), findsOneWidget);

      // Quadrant labels MUST be rendered in English
      expect(find.text('Flattery & Filler Phrases'), findsOneWidget);
      expect(find.text('Fluent Mastery'), findsOneWidget);
      expect(find.text('Novice / Routine'), findsOneWidget);
      expect(find.text('Organic Insight'), findsOneWidget);
    },
  );

  testWidgets(
    'QuadrantMatrixChart renders diagnostic quadrant watermarks in Finnish',
    (tester) async {
      await tester.pumpWidget(createChartWidget(locale: const Locale('fi')));
      await tester.pumpAndSettle();

      // Axis labels must be visible
      expect(find.textContaining('Axis X'), findsOneWidget);
      expect(find.textContaining('Axis Y'), findsOneWidget);

      // Quadrant labels MUST be rendered in Finnish
      expect(find.text('Mielistely & Täytefraasit'), findsOneWidget);
      expect(find.text('Asiantunteva & Sujuva'), findsOneWidget);
      expect(find.text('Alkeellinen / Rutiini'), findsOneWidget);
      expect(find.text('Aito & Omaääninen'), findsOneWidget);
    },
  );
}
