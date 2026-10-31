import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/execution/models/synthesis_config_dto.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('SynthesisConfigDto Tests', () {
    test(
      'Positive: deserializes valid JSON payload with 32-hex UUIDv7 IDs and roundtrips cleanly',
      () {
        final synthId = generateOpaqueUuid7('blk');
        final rowExpId = generateOpaqueUuid7('blk');
        final fullJson = <String, dynamic>{
          'system_prompt': 'Synthesize findings strictly from evidence.',
          'synthesis_block_id': synthId,
          'row_explanations_block_id': rowExpId,
          'length_constraint': 500,
          'preamble_text': <String, dynamic>{
            'translations': <String, String>{
              'en': 'Executive Preamble',
              'fi': 'Johdon esipuhe',
            },
          },
          'tone_instruction': <String, dynamic>{
            'translations': <String, String>{
              'en': 'Analytical and concise',
              'fi': 'Analyyttinen ja tiivis',
            },
          },
        };

        final dto = SynthesisConfigDto.fromJson(fullJson);
        expect(
          dto.systemPrompt,
          equals('Synthesize findings strictly from evidence.'),
        );
        expect(dto.synthesisBlockId, equals(synthId));
        expect(dto.rowExplanationsBlockId, equals(rowExpId));
        expect(dto.lengthConstraint, equals(500));
        expect(dto.preambleText?.get('en'), equals('Executive Preamble'));
        expect(
          dto.toneInstruction?.get('fi'),
          equals('Analyyttinen ja tiivis'),
        );
        expect(dto.toJson(), equals(fullJson));

        final emptyJson = <String, dynamic>{};
        final emptyDto = SynthesisConfigDto.fromJson(emptyJson);
        expect(emptyDto.systemPrompt, isNull);
        expect(emptyDto.synthesisBlockId, isNull);
        expect(emptyDto.rowExplanationsBlockId, isNull);
        expect(emptyDto.lengthConstraint, isNull);
        expect(emptyDto.preambleText, isNull);
        expect(emptyDto.toneInstruction, isNull);
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, dynamic>{
          'system_prompt': 'Valid prompt',
          'unexpected_field': 'forbidden',
        };

        expect(
          () => SynthesisConfigDto.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: rejects malformed Opaque Stripe IDs (16-hex legacy or invalid prefix) and invalid field types',
      () {
        final legacy16HexId = <String, dynamic>{
          'synthesis_block_id': 'blk_0123456789abcdef',
        };
        expect(
          () => SynthesisConfigDto.fromJson(legacy16HexId),
          throwsA(
            isA<CheckedFromJsonException>().having(
              (e) => e.innerError,
              'innerError',
              isA<AppException>(),
            ),
          ),
        );

        final invalidRowBlockId = <String, dynamic>{
          'row_explanations_block_id': 'invalid_id_format',
        };
        expect(
          () => SynthesisConfigDto.fromJson(invalidRowBlockId),
          throwsA(
            isA<CheckedFromJsonException>().having(
              (e) => e.innerError,
              'innerError',
              isA<AppException>(),
            ),
          ),
        );

        final invalidLengthType = <String, dynamic>{
          'length_constraint': 'five-hundred',
        };
        expect(
          () => SynthesisConfigDto.fromJson(invalidLengthType),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
