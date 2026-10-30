import 'dart:convert';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

void main() {
  group('PromptBlock & Sub-Models Unit & ISTQB Boundary Tests', () {
    const validPbId = 'pb_0195f3a0000070008000000000000001';
    const validTdaId = 'tda_0195f3a0000070008000000000000002';
    const sampleLabel = I18nText(
      translations: {'en': 'English Label', 'fi': 'Suomenkielinen otsikko'},
    );
    const sampleDesc = I18nText(
      translations: {'en': 'English Description', 'fi': 'Kuvaus'},
    );

    test(
      'Positive: Deserializes all 7 PromptBlock discriminated union variants and resolves getters',
      () {
        final matrixJson = {
          'id': validPbId,
          'slug': 'test-matrix',
          'organization_id': 'org_0195f3a0000070008000000000000099',
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'category_id': 'matrix',
          'type': 'float',
          'allow_contextual_override': true,
          'computed_min': 1,
          'computed_max': 5,
          'target_input_key': 'chat_log',
          'scales': [
            {
              'score': 1,
              'ai_label': 'POOR',
              'claims': [
                {
                  'label': {
                    'translations': {'en': 'Claim 1'},
                  },
                  'tda_assertions': [
                    {
                      'tda_id': validTdaId,
                      'concept_description': 'Valid concept description string',
                      'inverse_evidence': false,
                      'aggregation_mode': 'EXISTS',
                      'depends_on': [
                        {
                          'edge_reasoning': 'Prerequisite check',
                          'tda_id': validTdaId,
                          'source_id': 'chunk_1',
                          'expected_status': 'PASSED',
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
          'rows': [
            {
              'label': {
                'translations': {'en': 'Row 1'},
              },
              'ai_description': 'Row instruction',
            },
          ],
        };

        final matrixBlock = PromptBlock.fromJson(matrixJson);
        expect(matrixBlock, isA<MatrixPromptBlock>());
        expect(matrixBlock.categoryId, 'matrix');
        expect(matrixBlock.computedMin, 1);
        expect(matrixBlock.computedMax, 5);
        expect(matrixBlock.allowContextualOverride, isTrue);
        expect(matrixBlock.scales, hasLength(1));
        expect(matrixBlock.rows, hasLength(1));

        for (final category in [
          'system_rule',
          'execution_persona',
          'agent_role',
          'protocol',
          'runtime_variables',
          'task_definition',
        ]) {
          final block = PromptBlock.fromJson({
            'id': validPbId,
            'slug': 'test-$category',
            'label': sampleLabel.toJson(),
            'description': sampleDesc.toJson(),
            'category_id': category,
          });
          expect(block.categoryId, category);
          expect(block.computedMin, isNull);
          expect(block.computedMax, isNull);
          expect(block.scales, isNull);
          expect(block.rows, isNull);
          expect(block.columns, isNull);
          expect(block.allowContextualOverride, isFalse);
        }
      },
    );

    test(
      'Positive: TDAAssertion.create generates canonical 32-hex tda_ UUIDv7 and parseInBackground works',
      () async {
        final tda = TDAAssertion.create(
          conceptDescription: 'Valid concept description for TDA assertion',
          inverseEvidence: true,
          aggregationMode: AggregationMode.exists,
        );
        expect(RegExp(r'^tda_[a-f0-9]{32}$').hasMatch(tda.tdaId), isTrue);

        const ruleBlock = PromptBlock.systemRule(
          id: validPbId,
          slug: 'test-rule',
          label: sampleLabel,
          description: sampleDesc,
        );
        const protocolBlock = PromptBlock.protocol(
          id: validPbId,
          slug: 'test-protocol',
          label: sampleLabel,
          description: sampleDesc,
        );

        final rawJson = jsonEncode(ruleBlock.toJson());
        final parsedSingle = await PromptBlock.parseInBackground(rawJson);
        expect(parsedSingle.id, validPbId);
        expect(parsedSingle.categoryId, 'system_rule');

        final parsedList = await PromptBlock.parseListInBackground([
          protocolBlock.toJson(),
          ruleBlock.toJson(),
        ]);
        expect(parsedList, hasLength(2));
        expect(parsedList.first.categoryId, 'protocol');
        expect(parsedList.last.categoryId, 'system_rule');
      },
    );

    test(
      'Negative Partition 1 (BVA): StrictOpaqueIdConverter rejects 31-hex (min-1) and 33-hex (max+1) IDs on PromptBlock and TDAAssertion',
      () {
        // 31 hex chars (min - 1)
        final shortIdJson = {
          'id': 'pb_0195f3a000007000800000000000001',
          'slug': 'short-id',
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'category_id': 'system_rule',
        };
        expect(
          () => PromptBlock.fromJson(shortIdJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // 33 hex chars (max + 1)
        final longIdJson = {
          'id': 'pb_0195f3a0000070008000000000000001a',
          'slug': 'long-id',
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'category_id': 'system_rule',
        };
        expect(
          () => PromptBlock.fromJson(longIdJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // Invalid 16-hex truncated tda_id on TDAAssertion
        final truncatedTdaJson = {
          'tda_id': 'tda_0195f3a000007000',
          'concept_description': 'Valid concept description',
          'inverse_evidence': false,
          'aggregation_mode': 'EXISTS',
        };
        expect(
          () => TDAAssertion.fromJson(truncatedTdaJson),
          throwsA(
            isA<CheckedFromJsonException>().having(
              (e) => e.innerError,
              'innerError',
              isA<AppException>(),
            ),
          ),
        );
      },
    );

    test(
      'Negative Partition 2: disallowUnrecognizedKeys rejects unknown properties across PromptBlock and sub-DTOs',
      () {
        final pollutedBlockJson = {
          'id': validPbId,
          'slug': 'polluted-protocol',
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'category_id': 'protocol',
          'legacy_unrecognized_field': 'must_crash',
        };
        expect(
          () => PromptBlock.fromJson(pollutedBlockJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final pollutedEdgeJson = {
          'edge_reasoning': 'Valid reasoning',
          'tda_id': validTdaId,
          'source_id': 'src_1',
          'unexpected_key': 123,
        };
        expect(
          () => CausalEdgeDTO.fromJson(pollutedEdgeJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative Partition 3: BlockDataType.fromString throws FormatException on unknown value',
      () {
        expect(BlockDataType.fromString('FLOAT'), BlockDataType.floatType);
        expect(
          () => BlockDataType.fromString('invalid_type'),
          throwsA(isA<FormatException>()),
        );
      },
    );
  });
}
