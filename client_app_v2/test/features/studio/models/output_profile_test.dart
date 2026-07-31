import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';

void main() {
  group('OutputLayoutBlock JSON Parsing', () {
    test('Should parse OutputLayoutBlock with synthesis_blocks', () {
      final jsonPayload = {
        'preset_view': 'default',
        'title': {
          'default_locale': 'en',
          'translations': {'fi': 'Otsikko', 'en': 'Title'},
        },
        'text_delivery_mode': 'full',
        'synthesis_blocks': [
          {'block_type': 'hero_insight', 'text': 'Some insight'},
        ],
      };

      final block = OutputLayoutBlock.fromJson(jsonPayload);

      expect(block, isNotNull);
      expect(block.synthesisBlocks.length, 1);
      expect(block.synthesisBlocks.first, isA<SduiHeroInsightBlock>());
      expect(
        (block.synthesisBlocks.first as SduiHeroInsightBlock).text,
        'Some insight',
      );
    });

    test('Should parse empty JSON and default maps to {}', () {
      final jsonPayload = <String, dynamic>{};

      final block = OutputLayoutBlock.fromJson(jsonPayload);

      expect(block, isNotNull);
      expect(block.matrixColumnLabels, isEmpty);
    });
  });

  group('OutputProfile Additional JSON Parsing', () {
    test('Should parse OutputProfile with language and content_blocks', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'language': 'fi',
        'content_blocks': [
          {'id': 'blk_123', 'block_type': 'markdown', 'text': 'test'},
        ],
      };

      final profile = OutputProfile.fromJson(jsonPayload);

      expect(profile, isNotNull);
      expect(profile.language, 'fi');
    });
  });

  group('OutputProfile JSON Parsing', () {
    test('Should parse strict Stripe ID for system workflows', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'content_blocks': [
          {'id': 'blk_123', 'block_type': 'markdown', 'text': 'test'},
        ],
      };

      final profile = OutputProfile.fromJson(jsonPayload);
      expect(profile.workflowId, 'wf_9d68c573802341db');
    });

    test('Should parse OutputProfile with synthesis object', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'synthesis': {
          'historical_context_mode': 'DISABLED',
          'enable_pii_masking': false,
          'allowed_exports': ['pdf', 'raw_json'],
          'omit_empty_sections': true,
          'allowed_mcp_tools': [],
          'synthesis_block_id': 'blk_1a2b3c4d5e6f7a8b',
          'row_explanations_block_id': 'blk_row_explanation_rules',
        },
      };

      final profile = OutputProfile.fromJson(jsonPayload);
      expect(profile.synthesis, isNotNull);
      expect(profile.synthesis?.synthesisBlockId, 'blk_1a2b3c4d5e6f7a8b');
      expect(
        profile.synthesis?.rowExplanationsBlockId,
        'blk_row_explanation_rules',
      );
    });
  });

  group('SynthesisConfigDTO JSON Parsing', () {
    test('Should parse SynthesisConfigDTO with synthesis_block_id', () {
      final jsonPayload = {
        'historical_context_mode': 'DISABLED',
        'enable_pii_masking': false,
        'allowed_exports': ['pdf'],
        'omit_empty_sections': true,
        'allowed_mcp_tools': [],
        'synthesis_block_id': 'blk_8f7e6d5c4b3a2019',
      };

      final dto = SynthesisConfigDTO.fromJson(jsonPayload);
      expect(dto.synthesisBlockId, 'blk_8f7e6d5c4b3a2019');
    });
  });
}
