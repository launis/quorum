import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ReportDataDto Strictness', () {
    test('Throws exception if unrecognized keys are present (Fail-Fast)', () {
      final jsonWithUnknownKey = {
        'execution_id': 'exe_123',
        'workflow_id': 'wor_123',
        'profile_id': 'pro_123',
        'legacy_field_that_should_crash': 'some_value',
      };

      expect(
        () => ReportDataDto.fromJson(jsonWithUnknownKey),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('Parses successfully with exact valid keys', () {
      final validJson = {
        'execution_id': 'exe_123',
        'workflow_id': 'wor_123',
        'profile_id': 'pro_123',
      };

      final dto = ReportDataDto.fromJson(validJson);
      expect(dto.executionId, 'exe_123');
      expect(dto.workflowId, 'wor_123');
      expect(dto.profileId, 'pro_123');
    });
  });
}
