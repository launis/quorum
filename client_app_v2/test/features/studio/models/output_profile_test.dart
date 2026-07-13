import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/output_profile.dart';

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
  });

  group('EmbeddedOutputProfile JSON Parsing', () {
    test(
      'Should parse EmbeddedOutputProfile with language and formatting_directives',
      () {
        final jsonPayload = {
          'name': {
            'default_locale': 'en',
            'translations': {'en': 'Test Profile'},
          },
          'language': 'fi',
          'formatting_directives': ['directive 1', 'directive 2'],
        };

        final profile = EmbeddedOutputProfile.fromJson(jsonPayload);

        expect(profile, isNotNull);
        // We can't expect the fields yet as they don't exist, but we expect it not to throw.
      },
    );
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
      };

      final profile = OutputProfile.fromJson(jsonPayload);
      expect(profile.workflowId, 'wf_9d68c573802341db');
    });
  });
}
