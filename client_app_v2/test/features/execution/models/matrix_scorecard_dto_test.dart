import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  group('ScorecardAtomDto', () {
    test('fromJson strictly parses valid atom according to Phase 3 schema', () {
      final json = {
        'atom_id': 'atm_123',
        'level': 1,
        'level_name': 'T1',
        'claim_label': 'Test Claim',
        'extracted_facts': {'fact1': 'value'},
        'exact_quotes': [
          {'quote': 'quote 1'},
          {'quote': 'quote 2'},
        ],
        'internal_logic_en': {
          'step_1_identify_premise': 'p',
          'step_2_scan_source': 's',
          'step_3_evaluate_anti_patterns': 'e',
          'step_4_final_conclusion': 'c',
        },
        'status': 'PASSED',
        'semantic_reasoning': 'because',
        'contextual_override': false,
        'structural_location': null,
        'chart_display_label': 'Skipped',
        'visual_intent': 'NEUTRAL',
      };

      final dto = ScorecardAtomDto.fromJson(json);
      expect(dto.atomId, 'atm_123');
      expect(dto.status, ExecutionStatus.passed);
      expect(dto.exactQuotes.length, 2);
    });

    test(
      'test_matrix_scorecard_dto_deserialization: parses valid atom with ExecutionStatus.PASSED and visualIntent warning',
      () {
        final json = {
          'atom_id': 'atm_456',
          'level': 1,
          'level_name': 'T1',
          'claim_label': 'Test Claim',
          'extracted_facts': {},
          'exact_quotes': [],
          'internal_logic_en': {
            'step_1_identify_premise': 'p',
            'step_2_scan_source': 's',
            'step_3_evaluate_anti_patterns': 'e',
            'step_4_final_conclusion': 'c',
          },
          'status': 'PASSED',
          'semantic_reasoning': 'because',
          'contextual_override': true,
          'structural_location': null,
          'chart_display_label': 'OK',
          'visual_intent': 'warning',
        };

        final dto = ScorecardAtomDto.fromJson(json);
        expect(dto.status, ExecutionStatus.passed);
        expect(dto.visualIntent, VisualIntent.warning);
      },
    );

    test(
      'test_matrix_scorecard_dto_invalid_enum_throws: invalid status throws',
      () {
        final json = {
          'atom_id': 'atm_789',
          'level': 1,
          'level_name': 'T1',
          'claim_label': 'Test Claim',
          'extracted_facts': {},
          'exact_quotes': [],
          'internal_logic_en': {
            'step_1_identify_premise': 'p',
            'step_2_scan_source': 's',
            'step_3_evaluate_anti_patterns': 'e',
            'step_4_final_conclusion': 'c',
          },
          'status': 'INVALID_STATUS',
          'semantic_reasoning': 'because',
          'contextual_override': false,
          'structural_location': null,
          'chart_display_label': 'OK',
          'visual_intent': 'success',
        };

        expect(() => ScorecardAtomDto.fromJson(json), throwsA(anything));
      },
    );

    test(
      'test_human_override_dto_invalid_enum_throws: invalid new_status throws',
      () {
        final json = {
          'new_status': 'SUPER_PASS',
          'reason': 'Because',
          'evidence_quotes': [],
          'overridden_by': 'Test User',
          'overridden_at': '2023-01-01T00:00:00Z',
        };

        expect(() => HumanOverrideDto.fromJson(json), throwsA(anything));
      },
    );
  });

  group('MatrixScorecardRowDto', () {
    test('atomsByLevel correctly groups atoms by level', () {
      final json = {
        'block_id': 'blk_1',
        'name': 'test_matrix',
        'label_i18n': {
          'default_locale': 'en',
          'translations': {'en': 'Test', 'fi': 'Testi'},
        },
        'inner_sdui_blocks': [
          {'block_type': 'markdown', 'text': 'Matrix Markdown'},
        ],
        'evaluated_atoms': [
          {
            'atom_id': 'atm_1',
            'level': 1,
            'level_name': 'T1',
            'claim_label': 'A',
            'extracted_facts': {},
            'exact_quotes': [],
            'internal_logic_en': {
              'step_1_identify_premise': 'p',
              'step_2_scan_source': 's',
              'step_3_evaluate_anti_patterns': 'e',
              'step_4_final_conclusion': 'c',
            },
            'status': 'PASSED',
            'semantic_reasoning': 'r',
            'contextual_override': false,
            'structural_location': 'L',
            'chart_display_label': 'OK',
            'visual_intent': 'success',
          },
          {
            'atom_id': 'atm_2',
            'level': 1,
            'level_name': 'T1',
            'claim_label': 'B',
            'extracted_facts': {},
            'exact_quotes': [],
            'internal_logic_en': {
              'step_1_identify_premise': 'p',
              'step_2_scan_source': 's',
              'step_3_evaluate_anti_patterns': 'e',
              'step_4_final_conclusion': 'c',
            },
            'status': 'PASSED',
            'semantic_reasoning': 'r',
            'contextual_override': false,
            'structural_location': 'L',
            'chart_display_label': 'OK',
            'visual_intent': 'success',
          },
          {
            'atom_id': 'atm_3',
            'level': 2,
            'level_name': 'T2',
            'claim_label': 'C',
            'extracted_facts': {},
            'exact_quotes': [],
            'internal_logic_en': {
              'step_1_identify_premise': 'p',
              'step_2_scan_source': 's',
              'step_3_evaluate_anti_patterns': 'e',
              'step_4_final_conclusion': 'c',
            },
            'status': 'PASSED',
            'semantic_reasoning': 'r',
            'contextual_override': false,
            'structural_location': 'L',
            'chart_display_label': 'OK',
            'visual_intent': 'success',
          },
        ],
      };

      final dto = MatrixScorecardRowDto.fromJson(json);

      final grouped = dto.atomsByLevel;
      expect(grouped.length, 2);
      expect(grouped[1]?.length, 2);
      expect(grouped[2]?.length, 1);
    });
  });
}
