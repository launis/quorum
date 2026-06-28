import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';

void main() {
  group('ReportAxisDTO XAI Extensions', () {
    test('fromJson parses all valid XAI extensions correctly (Happy Path)', () {
      final json = {
        'block_id': 'blk_123',
        'label_i18n': {
          'default_locale': 'en',
          'translations': {'en': 'Matrix Risk', 'fi': 'Matriisi Riski'},
        },
        'name': 'Matrix Risk',
        'row_explanation': 'Valid logic structure.',
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
      expect(dto.labelI18n.get('en'), 'Matrix Risk');
      expect(dto.name, 'Matrix Risk');
      expect(dto.score, 4.5);
      expect(dto.rowExplanation, 'Valid logic structure.');
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
          'label_i18n': {
            'default_locale': 'en',
            'translations': {'en': 'Matrix Logic', 'fi': 'Matriisi Logiikka'},
          },
          'name': 'Matrix Logic',
          'row_explanation': 'Basic',
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
        expect(dto.rowExplanation, 'Basic');
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

    test(
      'TDD REPRO: fromJson parses label_i18n from backend without crashing',
      () {
        final json = {
          'block_id': 'blk_123',
          'name': 'Matrix Risk',
          'label_i18n': {
            'default_locale': 'en',
            'translations': {'fi': 'Matriisi Riski', 'en': 'Matrix Risk'},
          },
          'row_explanation': 'Valid logic structure.',
          'is_evaluative': true,
        };

        // This should now successfully parse without crashing!
        final dto = MatrixScorecardRowDto.fromJson(json);

        expect(dto.blockId, 'blk_123');
      },
    );

    test(
      'TDD REPRO: fromJson throws when backend sends quotes_list and row_forensics',
      () {
        final json = {
          'block_id': 'blk_123',
          'name': 'Matrix Risk',
          'label_i18n': {
            'default_locale': 'en',
            'translations': {'fi': 'Matriisi Riski'},
          },
          'row_explanation': 'Valid logic structure.',
          'is_evaluative': true,
          // Unrecognized keys sent by the backend:
          'quotes_list': ['quote 1'],
          'row_forensics': {'level_quotes': [], 'all_evidence_rejected': false},
        };

        // This will throw CheckedFromJsonException because of unrecognized keys
        MatrixScorecardRowDto.fromJson(json);
      },
    );

    test(
      'TDD REPRO: MCPToolAuditDTO throws on knowledge_gap and search_rationale',
      () {
        final json = {
          'tool_id': 'search_web',
          'step_name': 'Fact Check',
          'query': 'what is the capital of Finland',
          'knowledge_gap': 'Need to confirm capital',
          'search_rationale': 'Checking official sources',
        };

        // This will throw CheckedFromJsonException because of unrecognized keys
        MCPToolAuditDTO.fromJson(json);
      },
    );
  });
}
