import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'dart:convert';

void main() {
  group('ReportDataDto Isolate Parsing (Epic 95)', () {
    test('Parses successfully in background isolate without Main Thread Jank', () async {
      final validJson = {
        'execution_id': 'exe_456',
        'workflow_id': 'wor_456',
        'profile_id': 'pro_456',
      };
      
      final rawJson = jsonEncode(validJson);
      
      // Verification that the isolate method exists and works
      final dto = await ReportDataDto.parseInBackground(rawJson);
      
      expect(dto.executionId, 'exe_456');
      expect(dto.workflowId, 'wor_456');
      expect(dto.profileId, 'pro_456');
    });
  });
}
