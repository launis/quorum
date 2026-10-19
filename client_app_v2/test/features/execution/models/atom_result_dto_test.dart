import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';

void main() {
  group('AtomResultDTO Contract Tests', () {
    test('test_atom_result_dto_serialization_success', () {
      const dto = AtomResultDTO(
        tdaId: 'tda_123',
        matrixId: 'mat_456',
        status: ExecutionStatus.passed,
        sourceQuotes: ['Quote A', 'Quote B'],
        contextualOverride: false,
        isInverseEvidence: false,
        evaluationReasoning: 'Satisfies criteria',
        dependsOnTdaIds: ['tda_dep'],
        shortCircuitReasonTdaIds: [],
      );

      final json = dto.toJson();
      expect(json['tda_id'], 'tda_123');
      expect(json['matrix_id'], 'mat_456');
      expect(json['status'], 'PASSED');
      expect(json['source_quotes'], ['Quote A', 'Quote B']);
      expect(json['contextual_override'], isFalse);
      expect(json['is_inverse_evidence'], isFalse);
      expect(json['evaluation_reasoning'], 'Satisfies criteria');
      expect(json['depends_on_tda_ids'], ['tda_dep']);
    });

    test('test_atom_result_dto_deserialization_success', () {
      final json = {
        'tda_id': 'tda_789',
        'matrix_id': null,
        'status': 'FAILED',
        'extracted_data': {'value': 42, 'unit': 'ms'},
        'source_quotes': ['Failed evidence citation'],
        'contextual_override': true,
        'is_inverse_evidence': true,
        'evaluation_reasoning': 'Refuted by source',
        'error_details': {
          'error_code': 'SEMANTIC_ERROR',
          'message': 'Assertion failed',
        },
        'extensions': {'meta_k': 'meta_v'},
        'depends_on_tda_ids': [],
        'short_circuit_reason_tda_ids': ['tda_blocker'],
      };

      final dto = AtomResultDTO.fromJson(json);
      expect(dto.tdaId, 'tda_789');
      expect(dto.status, ExecutionStatus.failed);
      expect(dto.extractedData?.value, 42);
      expect(dto.extractedData?.unit, 'ms');
      expect(dto.sourceQuotes, ['Failed evidence citation']);
      expect(dto.contextualOverride, isTrue);
      expect(dto.isInverseEvidence, isTrue);
      expect(dto.errorDetails?.errorCode, 'SEMANTIC_ERROR');
      expect(dto.errorDetails?.message, 'Assertion failed');
      expect(dto.shortCircuitReasonTdaIds, ['tda_blocker']);
    });

    test('test_atom_result_dto_hallucinated_fields_fail_fast', () {
      final hallucinatedJson = {
        'tda_id': 'tda_999',
        'status': 'PASSED',
        'hallucinated_field': 'illegal_payload',
      };

      expect(
        () => AtomResultDTO.fromJson(hallucinatedJson),
        throwsA(
          anyOf(
            isA<FormatException>(),
            isA<TypeError>(),
            isA<CheckedFromJsonException>(),
          ),
        ),
      );
    });

    test('test_atom_result_dto_invalid_enum_throws', () {
      final invalidEnumJson = {
        'tda_id': 'tda_000',
        'status': 'NOT_A_REAL_STATUS',
      };

      expect(
        () => AtomResultDTO.fromJson(invalidEnumJson),
        throwsA(anything),
      );
    });
  });
}
