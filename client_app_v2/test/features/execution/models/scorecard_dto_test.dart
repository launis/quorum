import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

void main() {
  group('EvidenceQuoteDto', () {
    test('fromJson throws when backend sends used_evidence_ids (Epic 88)', () {
      final json = {
        'id': 'evq_123',
        'text': 'Test quote',
        'source_reference': 'page 1',
        'user_rejected': false,
        'rejection_reason': null,
        'is_mcp_verified': true,
        'used_evidence_ids': [
          'abc',
          'def',
        ], // <--- THIS is what the backend sends now
      };

      // Test that the new field is parsed correctly without crashing
      final dto = EvidenceQuoteDto.fromJson(json);
      expect(dto.usedEvidenceIds, ['abc', 'def']);
    });
  });
}
