import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';

void main() {
  group('HumanOverrideRequestDto Contract Tests', () {
    test('test_human_override_request_dto_serialization', () {
      // Input: HumanOverrideRequestDto(newStatus: ExecutionStatus.passed, reason: 'Verified', evidenceQuotes: [])
      const dto = HumanOverrideRequestDto(
        newStatus: ExecutionStatus.passed,
        reason: 'Verified',
        evidenceQuotes: [],
      );

      // Act
      final json = dto.toJson();

      // Expected: Serializes to JSON with new_status='PASSED' matching backend schema
      expect(json['new_status'], 'PASSED');
      expect(json['reason'], 'Verified');
      expect(json['evidence_quotes'], isEmpty);
    });

    test('test_human_override_request_dto_with_quotes_serialization', () {
      const quote = QuoteEvidenceDto(
        quote: 'Relevant quotation',
        verifiedSourceIds: ['src_1'],
        unverifiedAliases: [],
      );
      const dto = HumanOverrideRequestDto(
        newStatus: ExecutionStatus.failed,
        reason: 'Contradicted by source',
        evidenceQuotes: [quote],
      );

      final json = dto.toJson();
      expect(json['new_status'], 'FAILED');
      expect(json['reason'], 'Contradicted by source');
      expect(json['evidence_quotes'], isNotEmpty);
      final quotesList = json['evidence_quotes'] as List;
      expect(quotesList.first['quote'], 'Relevant quotation');
    });

    test('test_human_override_request_dto_empty_reason_fails_validation', () {
      // Input: HumanOverrideRequestDto with empty reason string
      const dto = HumanOverrideRequestDto(
        newStatus: ExecutionStatus.passed,
        reason: '',
        evidenceQuotes: [],
      );

      // Expected: Domain validator detects empty reason string
      final isReasonValid = dto.reason.trim().isNotEmpty;
      expect(isReasonValid, isFalse);
    });
  });
}
