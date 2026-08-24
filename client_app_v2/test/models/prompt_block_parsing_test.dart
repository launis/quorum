import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';

void main() {
  group('PromptBlock JSON Parsing', () {
    test('Parses PromptBlock with allow_contextual_override', () {
      final json = {
        'id': 'pb_1234567890abcdef',
        'slug': 'test-slug',
        'label': {
          'default_locale': 'en',
          'translations': {'en': 'Test Label', 'fi': 'Testi'},
        },
        'description': {
          'default_locale': 'en',
          'translations': {'en': 'Test Desc', 'fi': 'Testi'},
        },
        'category_id': 'matrix',
        'allow_contextual_override': true,
        'scales': [],
      };

      // We expect it to parse successfully because allow_contextual_override is now in PromptBlock
      final block = PromptBlock.fromJson(json);

      expect(block.id, 'pb_1234567890abcdef');
    });
  });
}
