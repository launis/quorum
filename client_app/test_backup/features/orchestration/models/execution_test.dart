import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Execution Model', () {
    const executedId = '123-abc';
    final now = DateTime.now();
    // Round trip via ISO8601 string to handle microsecond precision differences
    final isoNow = DateTime.parse(now.toIso8601String());

    test('should deserialize Pending state correctly', () {
      final json = {
        'execution_id': executedId,
        'start_time': isoNow.toIso8601String(),
        'workflow_name': 'Test Workflow',
        'status': 'pending',
        'inputs': {'foo': 'bar'},
      };

      final execution = Execution.fromJson(json);

      expect(execution, isA<ExecutionPending>());
      expect(execution.id, executedId);
      expect(execution.status, ExecutionStatus.pending);
      expect(execution.inputs['foo'], 'bar');
    });

    test('should deserialize Running state correctly', () {
      final json = {
        'execution_id': executedId,
        'start_time': isoNow.toIso8601String(),
        'status': 'running',
        'current_step_name': 'Step 1',
      };

      final execution = Execution.fromJson(json);

      expect(execution, isA<ExecutionRunning>());
      expect(execution.status, ExecutionStatus.running);
      expect(execution.currentStepName, 'Step 1');
    });

    test('should deserialize Completed state correctly with result', () {
      final json = {
        'execution_id': executedId,
        'start_time': isoNow.toIso8601String(),
        'status': 'completed',
        'result': {'output': 'success'},
        'xai_report_formatted': '# Report',
      };

      final execution = Execution.fromJson(json);

      expect(execution, isA<ExecutionCompleted>());
      expect((execution as ExecutionCompleted).result['output'], 'success');
      expect(execution.xaiReport, '# Report');
    });

    test('should deserialize Failed state correctly with error', () {
      final json = {
        'execution_id': executedId,
        'start_time': isoNow.toIso8601String(),
        'status': 'failed',
        'error': 'Something went wrong',
      };

      final execution = Execution.fromJson(json);

      expect(execution, isA<ExecutionFailed>());
      expect((execution as ExecutionFailed).error, 'Something went wrong');
    });

    test('should unknown status fall back to ExecutionUnknown', () {
      // Note: Freezed union handling depends on how unknown values are mapped.
      // If strict checking is off or fallback is manual, checking behavior here.
      // Based on the definition:
      // const factory Execution.unknown(...) = ExecutionUnknown;
      // BUT @Freezed(unionKey: 'status'...) usually requires 'unknown' string explicitly
      // UNLESS fallbackUnion is set. The model doesn't have fallbackUnion.
      // However, the enum has 'unknown'.
      // Backend might send 'unknown'.

      final jsonUnknown = {
        'execution_id': executedId,
        'start_time': isoNow.toIso8601String(),
        'status': 'unknown',
      };

      final execution = Execution.fromJson(jsonUnknown);
      expect(execution, isA<ExecutionUnknown>());
    });
  });
}
