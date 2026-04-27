import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

void main() {
  group('ReportAxisDTO XAI Extensions', () {
    test('fromJson parses all valid XAI extensions correctly (Happy Path)', () {
      final json = {
        'block_id': 'blk_123',
        'label_en': 'Matrix Risk',
        'label_fi': 'Matriisi Riski',
        'name': 'Matrix Risk',
        'justification': 'Valid logic structure.',
        'is_evaluative': true,
        'scale_min': 0.0,
        'scale_max': 5.0,
        'score': 4.5,
        'coaching': 'Try alternative phrasing.',
        'confidence': 95.5,
        'falsification': 'Unless the edge case is impossible.',
        'missing_context': 'Background dependencies not mentioned.',
        'risk_flag': true,
        'remediation_steps': 'Step 1\nStep 2',
        'emotional_sentiment': 'Positive and encouraging',
        'theory_link': 'Constructivist learning theory',
      };

      final dto = MatrixScorecardRowDto.fromJson(json);

      expect(dto.blockId, 'blk_123');
      expect(dto.labelEn, 'Matrix Risk');
      expect(dto.name, 'Matrix Risk');
      expect(dto.score, 4.5);
      expect(dto.justification, 'Valid logic structure.');
      expect(dto.coaching, 'Try alternative phrasing.');
      expect(dto.confidence, 95.5);
      expect(dto.falsification, 'Unless the edge case is impossible.');
      expect(dto.missingContext, 'Background dependencies not mentioned.');
      expect(dto.riskFlag, true);
      expect(dto.remediationSteps, 'Step 1\nStep 2');
      expect(dto.emotionalSentiment, 'Positive and encouraging');
      expect(dto.theoryLink, 'Constructivist learning theory');
    });

    test(
      'fromJson handles missing or null extensions smoothly (Fail-Fast Compliant)',
      () {
        final json = {
          'block_id': 'blk_123',
          'label_en': 'Matrix Logic',
          'label_fi': 'Matriisi Logiikka',
          'name': 'Matrix Logic',
          'justification': 'Basic',
          'is_evaluative': true,
          'scale_min': null,
          'score': 0.0,
          'confidence': null,
          'risk_flag': false,
          'remediation_steps': null,
          'coaching': null,
        };

        final dto = MatrixScorecardRowDto.fromJson(json);

        expect(dto.name, 'Matrix Logic');
        expect(dto.justification, 'Basic');
        expect(dto.score, 0.0);
        expect(dto.scaleMin, null);
        expect(dto.scaleMax, null);

        expect(dto.coaching, null);
        expect(dto.confidence, null);
        expect(dto.falsification, null);

        expect(dto.riskFlag, false);
        expect(dto.remediationSteps, null);
      },
    );
  });
}
