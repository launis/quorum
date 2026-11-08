import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow_simulation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('WorkflowSimulationResponse Contract Tests', () {
    test('test_workflow_simulation_response_deserialization_success', () {
      final emptyResponse = WorkflowSimulationResponse.fromJson(
        <String, Object?>{},
      );
      expect(emptyResponse.valid, isTrue);
      expect(emptyResponse.errors, isEmpty);
      expect(emptyResponse.stepStatus, isEmpty);
      expect(emptyResponse.executionOrder, isEmpty);
      expect(emptyResponse.trace.executionTimeMs, equals(0.0));
      expect(emptyResponse.trace.estimatedTokens, equals(0));

      final validResponseJson = <String, Object?>{
        'valid': true,
        'errors': <String>[],
        'step_status': <String, Object?>{'step_1': 'ready', 'step_2': 'ready'},
        'execution_order': <Object?>['step_1', 'step_2'],
        'trace': <String, Object?>{
          'execution_time_ms': 12.5,
          'estimated_tokens': 2,
        },
      };

      final response = WorkflowSimulationResponse.fromJson(validResponseJson);

      expect(response.valid, isTrue);
      expect(response.errors, isEmpty);
      expect(response.stepStatus['step_1'], 'ready');
      expect(response.executionOrder, ['step_1', 'step_2']);
      expect(response.trace.executionTimeMs, 12.5);
      expect(response.trace.estimatedTokens, 2);
      expect(response.toJson(), equals(validResponseJson));

      final updated = response.copyWith(
        valid: false,
        errors: const <String>['DAG validation error'],
        trace: const StepSimulationTraceDto(
          executionTimeMs: 20.0,
          estimatedTokens: 10,
        ),
      );
      expect(updated.valid, isFalse);
      expect(updated.errors, equals(<String>['DAG validation error']));
      expect(updated.trace.estimatedTokens, equals(10));
    });

    test('test_workflow_simulation_response_hallucinated_fields_fail_fast', () {
      final hallucinatedJson = <String, Object?>{
        'valid': true,
        'errors': <String>[],
        'step_status': <String, Object?>{},
        'execution_order': <Object?>[],
        'trace': <String, Object?>{},
        'hallucinated_key': 'fail',
      };

      expect(
        () => WorkflowSimulationResponse.fromJson(hallucinatedJson),
        throwsA(isA<CheckedFromJsonException>()),
      );

      final nestedHallucinatedJson = <String, Object?>{
        'valid': true,
        'trace': <String, Object?>{
          'execution_time_ms': 1.0,
          'estimated_tokens': 5,
          'extra_trace_key': 'forbidden',
        },
      };

      expect(
        () => WorkflowSimulationResponse.fromJson(nestedHallucinatedJson),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_workflow_simulation_response_invalid_type_fail_fast', () {
      final invalidTypeJson = <String, Object?>{
        'valid': 'not_a_bool',
        'errors': <Object?>[],
        'step_status': <String, Object?>{},
        'execution_order': <Object?>[],
        'trace': <String, Object?>{},
      };

      expect(
        () => WorkflowSimulationResponse.fromJson(invalidTypeJson),
        throwsA(isA<CheckedFromJsonException>()),
      );

      expect(
        () => WorkflowSimulationResponse.fromJson(<String, Object?>{
          'step_status': <String, Object?>{'step_1': 42},
        }),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });
}
