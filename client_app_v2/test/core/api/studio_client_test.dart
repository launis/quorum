import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late StudioClient client;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    client = StudioClient(mockDio);
  });

  group('StudioClient', () {
    test('test_studio_client_get_prompt_blocks_returns_typed_list', () async {
      // Arrange: HTTP 200 with raw JSON list of prompt blocks
      final mockData = [
        {
          'category_id': 'system_rule',
          'id': 'blk_1234567812345678',
          'slug': 'test_rule',
          'label': {
            'translations': {'en': 'Test Rule'},
          },
          'description': {
            'translations': {'en': 'Test Description'},
          },
          'is_evaluative': false,
          'type': 'instruction',
          'allow_decimals': false,
          'output_extensions': <String>[],
          'is_lightweight_protocol': false,
          'instruction_text': 'Follow rule',
        },
      ];

      when(() => mockDio.get('studio/prompt-blocks')).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: 'studio/prompt-blocks'),
          data: mockData,
          statusCode: 200,
        ),
      );

      // Act
      final result = await client.getPromptBlocks();

      // Assert
      expect(result, isA<List<PromptBlock>>());
      expect(result.length, 1);
      expect(result.first.id, 'blk_1234567812345678');
      expect(result.first, isA<SystemRulePromptBlock>());
      verify(() => mockDio.get('studio/prompt-blocks')).called(1);
    });

    test(
      'test_studio_client_get_prompt_blocks_unknown_keys_fails_fast',
      () async {
        // Arrange: HTTP 200 with JSON containing unknown key 'legacy_field'
        final invalidBlockJson = {
          'category_id': 'system_rule',
          'id': 'blk_1234567812345678',
          'slug': 'test_rule',
          'label': {
            'translations': {'en': 'Test Rule'},
          },
          'description': {
            'translations': {'en': 'Test Desc'},
          },
          'is_evaluative': false,
          'type': 'instruction',
          'allow_decimals': false,
          'output_extensions': <String>[],
          'is_lightweight_protocol': false,
          'instruction_text': 'Follow rule',
          'legacy_field': 'forbidden_value',
        };

        when(() => mockDio.get('studio/prompt-blocks')).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: 'studio/prompt-blocks'),
            data: [invalidBlockJson],
            statusCode: 200,
          ),
        );

        // Act & Assert
        expect(
          () => client.getPromptBlocks(),
          throwsA(
            anyOf(isA<FormatException>(), isA<CheckedFromJsonException>()),
          ),
        );
      },
    );

    test(
      'test_studio_client_simulate_prompt_block_empty_request_fails_fast',
      () async {
        // Arrange: PromptBlockSimulationRequest with empty block ID
        const emptyBlock = PromptBlock.systemRule(
          id: '',
          slug: 'empty_test',
          label: I18nText(translations: {'en': 'Empty'}),
          description: I18nText(translations: {'en': 'Empty'}),
        );
        const request = PromptBlockSimulationRequest(block: emptyBlock);

        // Act & Assert: Throws validation AppException before network dispatch
        expect(
          () => client.simulatePromptBlock(request),
          throwsA(isA<AppException>()),
        );
        verifyNever(() => mockDio.post(any(), data: any(named: 'data')));
      },
    );

    test(
      'test_studio_client_simulate_prompt_block_serializes_non_null_defaults',
      () async {
        // Arrange: PromptBlockSimulationRequest omitting optional contextText and targetLocale
        const block = PromptBlock.systemRule(
          id: 'blk_1234567812345678',
          slug: 'test_rule',
          label: I18nText(translations: {'en': 'Test Rule'}),
          description: I18nText(translations: {'en': 'Test Description'}),
        );
        const request = PromptBlockSimulationRequest(block: block);

        final returnedData = {
          'valid': true,
          'rendered_prompt': 'Rendered test prompt',
          'errors': <String>[],
          'prompt_context': null,
        };

        when(
          () => mockDio.post(
            'studio/prompt-blocks/simulate',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: 'studio/prompt-blocks/simulate',
            ),
            data: returnedData,
            statusCode: 200,
          ),
        );

        // Act
        final result = await client.simulatePromptBlock(request);

        // Assert
        expect(result.valid, isTrue);
        final captured =
            verify(
                  () => mockDio.post(
                    'studio/prompt-blocks/simulate',
                    data: captureAny(named: 'data'),
                  ),
                ).captured.single
                as Map<String, dynamic>;

        expect(captured['target_locale'], equals('en'));
        expect(
          captured['context_text'],
          equals('[SIMULATED CONTEXT DOCUMENT]'),
        );
        expect(captured['context_text'], isNotNull);
        expect(captured['target_locale'], isNotNull);
      },
    );

    test(
      'savePromptBlock calls correct endpoint and returns updated data',
      () async {
        // Arrange
        const blockToSave = PromptBlock.systemRule(
          id: 'blk_1234567812345678',
          slug: 'test_rule',
          label: I18nText(translations: {'en': 'Test Rule'}),
          description: I18nText(translations: {'en': 'Test Description'}),
        );

        final returnedData = {
          'category_id': 'system_rule',
          'id': 'blk_1234567812345678',
          'slug': 'test_rule',
          'label': {
            'translations': {'en': 'Test Rule'},
          },
          'description': {
            'translations': {'en': 'Test Description'},
          },
          'is_evaluative': false,
          'type': 'instruction',
          'allow_decimals': false,
          'output_extensions': <String>[],
          'is_lightweight_protocol': false,
          'instruction_text': null,
        };

        when(
          () => mockDio.put(
            'studio/prompt-blocks/blk_1234567812345678',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: 'studio/prompt-blocks/blk_1234567812345678',
            ),
            data: returnedData,
            statusCode: 200,
          ),
        );

        // Act
        final result = await client.savePromptBlock(
          'blk_1234567812345678',
          blockToSave,
        );

        // Assert
        expect(result.id, equals('blk_1234567812345678'));
        expect(result, isA<SystemRulePromptBlock>());
        verify(
          () => mockDio.put(
            'studio/prompt-blocks/blk_1234567812345678',
            data: any(named: 'data'),
          ),
        ).called(1);
      },
    );
  });
}
