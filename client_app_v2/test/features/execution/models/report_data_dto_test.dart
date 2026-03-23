import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';

void main() {
  group('ReportAxisDTO XAI Extensions', () {
    test('fromJson parses all valid XAI extensions correctly (Happy Path)', () {
      final json = {
        'name': 'Matrix Risk',
        'justification': 'Valid logic structure.',
        'scale_min': 0.0,
        'scale_max': 5.0,
        'score': 4.5,
        'coaching': 'Try alternative phrasing.',
        'confidence': 95.5,
        'falsification': 'Unless the edge case is impossible.',
        'missing_context': 'Background dependencies not mentioned.',
        'risk_flag': true,
        'remediation_steps': ['Step 1', 'Step 2'],
        'emotional_sentiment': 'Positive and encouraging',
        'theory_link': 'Constructivist learning theory',
      };

      final dto = ReportAxisDTO.fromJson(json);

      expect(dto.name, 'Matrix Risk');
      expect(dto.score, 4.5);
      expect(dto.justification, 'Valid logic structure.');
      expect(dto.coaching, 'Try alternative phrasing.');
      expect(dto.confidence, 95.5);
      expect(dto.falsification, 'Unless the edge case is impossible.');
      expect(dto.missingContext, 'Background dependencies not mentioned.');
      expect(dto.riskFlag, true);
      expect(dto.remediationSteps, ['Step 1', 'Step 2']);
      expect(dto.emotionalSentiment, 'Positive and encouraging');
      expect(dto.theoryLink, 'Constructivist learning theory');
    });

    test('fromJson handles missing, null, or incorrectly typed extensions gracefully (Defensive SafeCast)', () {
      final json = {
        'name': 'Matrix Logic',
        'justification': 'Basic',
        'scale_min': null,
        'scale_max': 'INVALID_MAX', // Should SafeCast to default
        'score': 'not a double', // Should SafeCast to 0.0 or null
        // Providing invalid types for extensions
        'confidence': 'HIGH STR', // Double parsing fails
        'risk_flag': 'yes', // Bool parsing fails or acts gracefully
        'remediation_steps': 'Just fix it', // List parsing fails
        'coaching': null,
      };

      final dto = ReportAxisDTO.fromJson(json);

      expect(dto.name, 'Matrix Logic');
      expect(dto.justification, 'Basic');
      // score: safeDouble usually returns 0.0 from invalid strings if defined, wait!
      // In ReportAxisDTO: json['score'] != null ? SafeCast.safeDouble(json['score']) : null
      // 'not a double' -> 0.0 (SafeCast.safeDouble defaults to 0.0 normally, and != null ensures it tries)
      expect(dto.score, 0.0);
      
      expect(dto.coaching, null);
      expect(dto.confidence, 0.0); // Assuming safeDouble('HIGH STR') -> 0.0
      expect(dto.falsification, null);
      
      expect(dto.riskFlag, false); // Assuming safeBool('yes') -> false based on strict frontend SafeCast
      // remediation_steps is safeList().map.
      // safeList('Just fix it') often returns [] for strings.
      expect(dto.remediationSteps, []);
    });
  });
}
