import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/performative_lexicon.dart';

void main() {
  group('SystemConfigPerformativeLexicons deserialization', () {
    test('deserializes successfully when slug is null', () {
      final payload = {
        'id': 'sys_e0b2a3c4d5e6f7a8',
        'type': 'performative_lexicons',
        'slug': null,
        'lexicon_configs': <String, dynamic>{},
      };

      final config = SystemConfigPerformativeLexicons.fromJson(payload);

      expect(config.id, 'sys_e0b2a3c4d5e6f7a8');
      expect(config.type, 'performative_lexicons');
      expect(config.slug, isNull);
      expect(config.lexiconConfigs, isEmpty);
    });

    test('deserializes successfully when slug is omitted', () {
      final payload = {
        'id': 'sys_e0b2a3c4d5e6f7a8',
        'type': 'performative_lexicons',
        'lexicon_configs': <String, dynamic>{},
      };

      final config = SystemConfigPerformativeLexicons.fromJson(payload);

      expect(config.id, 'sys_e0b2a3c4d5e6f7a8');
      expect(config.slug, isNull);
    });

    test('deserializes successfully when slug is a valid string', () {
      final payload = {
        'id': 'sys_e0b2a3c4d5e6f7a8',
        'type': 'performative_lexicons',
        'slug': 'performative_lexicons',
        'lexicon_configs': {
          'en': {
            'language_code': 'en',
            'language_name': 'English',
            'fuzz_threshold': 90,
            'words': ['delve into'],
          },
        },
      };

      final config = SystemConfigPerformativeLexicons.fromJson(payload);

      expect(config.id, 'sys_e0b2a3c4d5e6f7a8');
      expect(config.slug, 'performative_lexicons');
      expect(config.lexiconConfigs.containsKey('en'), isTrue);
      expect(config.lexiconConfigs['en']!.words, contains('delve into'));
    });
  });
}
