import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/orchestration/domain/models/xai_report.dart';
import 'package:client_app/features/orchestration/domain/models/evaluation_result.dart';

void main() {
  group('XAIReport Serialization', () {
    test('Should deserialize ScoreCardItem correctly', () {
      final json = {
        'agent_name': 'Judge (cognitive_matrix)',
        'total_score': 4.2,
        'max_score': 5,
        'verdict': 'Solid performance',
        'dimensions': [
          {'dimension_id': 'logic', 'score': 4.0, 'reasoning': 'Good'}
        ]
      };

      final item = ScoreCardItem.fromJson(json);

      expect(item.agentName, 'Judge (cognitive_matrix)');
      expect(item.totalScore, 4.2);
      expect(item.maxScore, 5);
      expect(item.verdict, 'Solid performance');
      expect(item.dimensions.length, 1);
      expect(item.dimensions.first.dimensionId, 'logic');
    });

    test('Should deserialize XAIReport with ScoreCards correctly', () {
      final json = {
        'metadata': {},
        'metodologinen_loki': 'Log data',
        'edellisen_vaiheen_validointi': 'Valid',
        'semanttinen_tarkistussumma': 'Hash123',
        'executive_summary': 'Report Summary',
        'analysis_strengths': 'Strengths',
        'analysis_weaknesses': 'Weaknesses',
        'analysis_opportunities': 'Opportunities',
        'analysis_recommendations': 'Recommendations',
        'final_verdict': 'Verdict',
        'confidence_score': 0.95,
        'score_cards': [
          {
            'agent_name': 'Judge 1',
            'total_score': 5.0,
            'max_score': 5,
            'verdict': 'Perfect',
            'dimensions': []
          },
          {
            'agent_name': 'Judge 2',
            'total_score': 3.0,
            'max_score': 5,
            'verdict': 'Okay',
            'dimensions': []
          }
        ]
      };

      final report = XAIReport.fromJson(json);

      expect(report.executiveSummary, 'Report Summary');
      expect(report.scoreCards.length, 2);
      expect(report.scoreCards.first.agentName, 'Judge 1');
      expect(report.scoreCards[1].totalScore, 3.0);
    });
  });
}
