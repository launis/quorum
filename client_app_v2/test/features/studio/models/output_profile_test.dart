import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';

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
}
