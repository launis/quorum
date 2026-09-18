import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/controllers/report_controller.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';

class MockExecutionClientPending implements ExecutionClient {
  int callCount = 0;

  @override
  Future<Map<String, dynamic>> renderExecution(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) async {
    callCount++;
    if (callCount == 1) {
      // First call returns pending with uppercase status
      return {'status': 'PENDING', 'message': 'Valmistellaan tulostusta...'};
    } else {
      // Second call returns actual data
      return {
        'execution_id': executionId,
        'workflow_id': 'wf_abc',
        'profile_id': 'prof_123',
        'global_metrics': {
          'total_atoms': 5,
          'evaluated': 5,
          'short_circuited_na': 0,
          'duration_ms': 100,
        },
        'results': <Map<String, dynamic>>[],
        'hydrated_references': <String, dynamic>{},
      };
    }
  }

  @override
  Future<ExecutionRecord> startExecution({
    required ExecutionCreateRequestDto request,
  }) async => const ExecutionRecord(
    id: 'test_exec',
    workflowId: 'test_wf',
    targetLocale: 'en',
    status: 'PASSED',
  );

  @override
  Future<ExecutionRecord> resumeExecution(String executionId) async =>
      const ExecutionRecord(
        id: 'test_exec',
        workflowId: 'test_wf',
        targetLocale: 'en',
        status: 'PASSED',
      );

  @override
  Future<ExecutionRecord> getExecutionStatus(String executionId) async =>
      const ExecutionRecord(
        id: 'test_exec',
        workflowId: 'test_wf',
        targetLocale: 'en',
        status: 'PASSED',
      );

  Future<Map<String, dynamic>> getScorecard(String executionId) async => {};

  @override
  Future<Map<String, dynamic>> overrideAtom({
    required String executionId,
    required String atomId,
    required Map<String, dynamic> payload,
  }) async => {};
}

void main() {
  group('ReportController', () {
    test('handles uppercase PENDING status without crashing', () async {
      final mockClient = MockExecutionClientPending();
      final container = ProviderContainer(
        overrides: [executionClientProvider.overrideWithValue(mockClient)],
      );

      final future = container.read(
        reportControllerProvider('test_exec').future,
      );

      // It should successfully return a ReportDataDto after 1 retry
      final result = await future;

      expect(result, isA<ReportDataDto>());
      expect(result.executionId, 'test_exec');
      expect(mockClient.callCount, 2);
    });
  });
}
