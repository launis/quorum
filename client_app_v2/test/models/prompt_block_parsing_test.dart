import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';

void main() {
  group('PromptBlock JSON Parsing', () {
    test('Parses PromptBlock with allow_contextual_override', () {
      final json = {
        'id': 'pb_0195f3a0000070008000000000000001',
        'slug': 'test-slug',
        'label': {
          'translations': {'en': 'Test Label', 'fi': 'Testi'},
        },
        'description': {
          'translations': {'en': 'Test Desc', 'fi': 'Testi'},
        },
        'category_id': 'matrix',
        'allow_contextual_override': true,
        'scales': [],
      };

      // We expect it to parse successfully because allow_contextual_override is now in PromptBlock
      final block = PromptBlock.fromJson(json);

      expect(block.id, 'pb_0195f3a0000070008000000000000001');
    });
  });
}
