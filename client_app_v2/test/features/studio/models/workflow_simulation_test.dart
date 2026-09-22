import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/studio/models/workflow_simulation.dart';

void main() {
  group('WorkflowSimulationResponse Contract Tests', () {
    test('test_workflow_simulation_response_deserialization_success', () {
      final validResponseJson = {
        'valid': true,
        'errors': <String>[],
        'step_status': {'step_1': 'ready', 'step_2': 'ready'},
        'execution_order': ['step_1', 'step_2'],
        'trace': {'simulated_nodes': 2},
      };

      final response = WorkflowSimulationResponse.fromJson(validResponseJson);

      expect(response.valid, isTrue);
      expect(response.errors, isEmpty);
      expect(response.stepStatus['step_1'], 'ready');
      expect(response.executionOrder, ['step_1', 'step_2']);
      expect(response.trace['simulated_nodes'], 2);
    });

    test('test_workflow_simulation_response_hallucinated_fields_fail_fast', () {
      final hallucinatedJson = {
        'valid': true,
        'errors': <String>[],
        'step_status': {},
        'execution_order': [],
        'trace': {},
        'hallucinated_key': 'fail',
      };

      expect(
        () => WorkflowSimulationResponse.fromJson(hallucinatedJson),
        throwsA(
          anyOf(
            isA<FormatException>(),
            isA<TypeError>(),
            isA<CheckedFromJsonException>(),
          ),
        ),
      );
    });

    test('test_workflow_simulation_response_invalid_type_fail_fast', () {
      final invalidTypeJson = {
        'valid': 'not_a_bool',
        'errors': [],
        'step_status': {},
        'execution_order': [],
        'trace': {},
      };

      expect(
        () => WorkflowSimulationResponse.fromJson(invalidTypeJson),
        throwsA(
          anyOf(
            isA<FormatException>(),
            isA<TypeError>(),
            isA<CheckedFromJsonException>(),
          ),
        ),
      );
    });
  });
}
