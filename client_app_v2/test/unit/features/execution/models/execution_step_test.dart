import 'dart:convert';

import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionStep Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: ExecutionStep deserializes full payload with FinOps metrics and scorecardAtoms and roundtrips cleanly',
      () {
        final stepId = generateOpaqueUuid7('stp');

        final rawPayload = <String, Object?>{
          'id': stepId,
          'label': 'Matrix Evaluation Step',
          'status': 'PASSED',
          'last_error': null,
          'message_code': 'STEP_COMPLETED',
          'model_strategy': 'reasoning',
          'physical_model': 'vertex_ai/gemini-2.5-pro',
          'system_fingerprint': 'fp_2026_v1',
          'prompt_tokens': 1450,
          'completion_tokens': 420,
          'cached_tokens': 800,
          'reasoning_tokens': 210,
          'cost_usd': 0.0185,
          'duration_ms': 2340,
          'chunk_count': 3,
          'progress': 100,
          'has_warning': true,
          'scorecard_atoms': <String, Object?>{
            'a0': <String, Object?>{
              'atom_id': 'a0',
              'level': 3,
              'level_name': 'Advanced',
              'claim_label': 'Explicit risk mitigation plan',
              'extracted_facts': <String, String?>{
                'fact_1': 'Documented fallback architecture',
              },
              'exact_quotes': <Map<String, Object?>>[
                <String, Object?>{
                  'source_quotes': <String>['Fallback architecture is active.'],
                  'verified_source_ids': <String>['src_1'],
                  'unverified_aliases': <String>[],
                  'is_verified': true,
                },
              ],
              'internal_logic_en': <String, Object?>{
                'step_1_identify_premise': 'Check risk mitigation',
                'step_2_scan_source': 'Found section 4',
                'step_3_evaluate_anti_patterns': 'None detected',
                'step_4_final_conclusion': 'Criterion satisfied',
              },
              'status': 'PASSED',
              'semantic_reasoning': 'Verified by explicit quote in section 4.',
              'contextual_override': false,
              'structural_location': 'Section 4.2',
              'human_override': null,
              'chart_display_label': 'Risk Mitigation',
              'visual_intent': 'success',
            },
          },
        };

        final step = ExecutionStep.fromJson(rawPayload);

        expect(step.id, equals(stepId));
        expect(step.label, equals('Matrix Evaluation Step'));
        expect(step.status, equals('PASSED'));
        expect(step.lastError, isNull);
        expect(step.messageCode, equals('STEP_COMPLETED'));
        expect(step.modelStrategy, equals('reasoning'));
        expect(step.physicalModel, equals('vertex_ai/gemini-2.5-pro'));
        expect(step.systemFingerprint, equals('fp_2026_v1'));
        expect(step.promptTokens, equals(1450));
        expect(step.completionTokens, equals(420));
        expect(step.cachedTokens, equals(800));
        expect(step.reasoningTokens, equals(210));
        expect(step.costUsd, equals(0.0185));
        expect(step.durationMs, equals(2340));
        expect(step.chunkCount, equals(3));
        expect(step.progress, equals(100));
        expect(step.hasWarning, isTrue);
        expect(step.scorecardAtoms, hasLength(1));
        expect(step.scorecardAtoms['a0'], isA<ScorecardAtomDto>());
        expect(
          step.scorecardAtoms['a0']?.visualIntent,
          equals(VisualIntent.success),
        );

        final roundtrippedMap =
            jsonDecode(jsonEncode(step.toJson())) as Map<String, Object?>;
        final roundtripped = ExecutionStep.fromJson(roundtrippedMap);

        expect(roundtripped.id, equals(stepId));
        expect(roundtripped.promptTokens, equals(1450));
        expect(roundtripped.chunkCount, equals(3));
        expect(roundtripped.hasWarning, isTrue);
        expect(
          roundtripped.scorecardAtoms['a0']?.claimLabel,
          equals('Explicit risk mitigation plan'),
        );
      },
    );

    test(
      'Positive 2 (Boundary & Defaults): applies deterministic defaults when optional FinOps and state fields are omitted',
      () {
        final stepId = generateOpaqueUuid7('stp');
        final minimalPayload = <String, Object?>{
          'id': stepId,
          'label': 'Pending Step',
          'status': 'PENDING',
        };

        final step = ExecutionStep.fromJson(minimalPayload);

        expect(step.id, equals(stepId));
        expect(step.label, equals('Pending Step'));
        expect(step.status, equals('PENDING'));
        expect(step.lastError, isNull);
        expect(step.messageCode, isNull);
        expect(step.modelStrategy, isNull);
        expect(step.physicalModel, isNull);
        expect(step.systemFingerprint, isNull);
        expect(step.promptTokens, equals(0));
        expect(step.completionTokens, equals(0));
        expect(step.cachedTokens, equals(0));
        expect(step.reasoningTokens, equals(0));
        expect(step.costUsd, equals(0.0));
        expect(step.durationMs, equals(0));
        expect(step.chunkCount, equals(1));
        expect(step.progress, isNull);
        expect(step.hasWarning, isFalse);
        expect(step.scorecardAtoms, isEmpty);
      },
    );

    test(
      'Negative 1: rejects unrecognized JSON keys under strict disallowUnrecognizedKeys configuration',
      () {
        final stepId = generateOpaqueUuid7('stp');
        final payloadWithExtraKey = <String, Object?>{
          'id': stepId,
          'label': 'Step',
          'status': 'RUNNING',
          'unrecognized_field': 'forbidden',
        };

        expect(
          () => ExecutionStep.fromJson(payloadWithExtraKey),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'Negative 2 (ISTQB BVA & Type Violations): rejects missing required fields and invalid field types',
      () {
        final stepId = generateOpaqueUuid7('stp');

        // Missing required 'label' and 'status'
        expect(
          () => ExecutionStep.fromJson(<String, Object?>{'id': stepId}),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // Invalid type for 'prompt_tokens' (String instead of int)
        expect(
          () => ExecutionStep.fromJson(<String, Object?>{
            'id': stepId,
            'label': 'Step',
            'status': 'RUNNING',
            'prompt_tokens': 'not_an_int',
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        // Invalid type for 'has_warning' (int instead of bool)
        expect(
          () => ExecutionStep.fromJson(<String, Object?>{
            'id': stepId,
            'label': 'Step',
            'status': 'RUNNING',
            'has_warning': 1,
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );
      },
    );
  });
}
