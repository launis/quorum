import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/score_card_radar.dart';
import 'package:client_app/features/orchestration/domain/models/xai_report.dart';
import 'package:client_app/features/orchestration/domain/models/evaluation_result.dart';
import 'package:fl_chart/fl_chart.dart';

void main() {
  testWidgets('ScoreCardRadar renders without crash with < 3 dimensions', (WidgetTester tester) async {
    final card = ScoreCardItem(
      agentName: 'TestAgent',
      totalScore: 4.5,
      verdict: 'Good',
      dimensions: [
        DimensionResultItem(dimensionId: 'dim1', score: 4.0, reasoning: 'Reason 1'),
        DimensionResultItem(dimensionId: 'dim2', score: 3.5, reasoning: 'Reason 2'),
      ],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ScoreCardRadar(card: card),
        ),
      ),
    );

    expect(find.byType(RadarChart), findsNothing);
    expect(find.text('TestAgent'), findsOneWidget);
    expect(find.text('Good'), findsOneWidget);
    // Chips should still be visible
    expect(find.text('dim1: 4.0'), findsOneWidget); 
    expect(find.text('dim2: 3.5'), findsOneWidget);
  });

  testWidgets('ScoreCardRadar renders RadarChart with >= 3 dimensions', (WidgetTester tester) async {
    final card = ScoreCardItem(
      agentName: 'TestAgent',
      totalScore: 4.5,
      verdict: 'Good',
      dimensions: [
        DimensionResultItem(dimensionId: 'dim1', score: 4.0, reasoning: ''),
        DimensionResultItem(dimensionId: 'dim2', score: 4.0, reasoning: ''),
        DimensionResultItem(dimensionId: 'dim3', score: 4.0, reasoning: ''),
      ],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ScoreCardRadar(card: card),
        ),
      ),
    );

    expect(find.byType(RadarChart), findsOneWidget);
  });
}
