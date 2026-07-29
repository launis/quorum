import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';

void main() {
  group('SduiBlockDTO strict deserialization', () {
    test('parses paragraph block correctly', () {
      final json = {
        'block_type': 'paragraph',
        'text': 'Hello world',
        'citations': [1, 2],
        'exact_quotes': ['Hello'],
      };

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiParagraphBlock>());
      if (block is SduiParagraphBlock) {
        expect(block.text, 'Hello world');
        expect(block.citations, [1, 2]);
        expect(block.exactQuotes, ['Hello']);
      }
    });

    test('parses bullet_list block correctly', () {
      final json = {
        'block_type': 'bullet_list',
        'items': [
          {
            'text': 'Item 1',
            'citations': [1],
            'exact_quotes': [],
          },
        ],
      };

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiBulletListBlock>());
      if (block is SduiBulletListBlock) {
        expect(block.items.length, 1);
        expect(block.items.first.text, 'Item 1');
      }
    });

    test('parses alert_box block correctly', () {
      final json = {
        'block_type': 'alert_box',
        'text': 'Warning',
        'severity': 'high',
      };

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiAlertBoxBlock>());
      if (block is SduiAlertBoxBlock) {
        expect(block.text, 'Warning');
        expect(block.severity, 'high');
      }
    });

    test('parses hero_insight block correctly', () {
      final json = {'block_type': 'hero_insight', 'text': 'Insightful'};

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiHeroInsightBlock>());
      if (block is SduiHeroInsightBlock) {
        expect(block.text, 'Insightful');
      }
    });

    test('parses markdown block correctly', () {
      final json = {'block_type': 'markdown', 'text': '# Heading'};

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiMarkdownBlock>());
      if (block is SduiMarkdownBlock) {
        expect(block.text, '# Heading');
      }
    });

    test('parses quote_card block correctly', () {
      final json = {
        'block_type': 'quote_card',
        'quote': 'To be or not to be',
        'source_aliases': ['Shakespeare'],
        'citations': [1],
      };

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiQuoteCardBlock>());
      if (block is SduiQuoteCardBlock) {
        expect(block.quote, 'To be or not to be');
        expect(block.sourceAliases, ['Shakespeare']);
        expect(block.citations, [1]);
      }
    });

    test('parses warning_card block correctly', () {
      final json = {
        'block_type': 'warning_card',
        'message': 'Be careful',
        'quote_text': 'Caution',
      };

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiWarningCardBlock>());
      if (block is SduiWarningCardBlock) {
        expect(block.message, 'Be careful');
        expect(block.quoteText, 'Caution');
      }
    });

    test('parses n_a_card block correctly', () {
      final json = {
        'block_type': 'n_a_card',
        'short_circuit_reason_tda_ids': ['id123'],
        'message': 'Not applicable',
      };

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiNACardBlock>());
      if (block is SduiNACardBlock) {
        expect(block.shortCircuitReasonTdaIds, ['id123']);
        expect(block.message, 'Not applicable');
      }
    });

    test('parses grid block correctly', () {
      final json = {
        'block_type': 'grid',
        'items': ['foo'],
      };

      final block = SduiBlockDTO.fromJson(json);

      expect(block, isA<SduiGridBlock>());
      if (block is SduiGridBlock) {
        expect(block.items.length, 1);
        expect(block.items.first, 'foo');
      }
    });

    test('throws exception on unknown block type', () {
      final json = {'block_type': 'unknown_type', 'text': 'Should fail'};

      expect(() => SduiBlockDTO.fromJson(json), throwsException);
    });

    test('throws exception on missing required field', () {
      final json = {
        'block_type': 'paragraph',
        // missing 'text'
      };

      expect(() => SduiBlockDTO.fromJson(json), throwsException);
    });

    test('throws exception on unrecognized key (strict mode)', () {
      final json = {
        'block_type': 'paragraph',
        'text': 'Hello',
        'extra_field_not_in_schema': 'This should crash',
      };

      expect(() => SduiBlockDTO.fromJson(json), throwsException);
    });

    test('reproduces bug: successfully parses id key when present', () {
      final json = {
        'block_type': 'paragraph',
        'id': 'blk_123',
        'text': 'Hello',
      };

      final block = SduiBlockDTO.fromJson(json);
      expect(block, isA<SduiParagraphBlock>());
    });
  });
}
