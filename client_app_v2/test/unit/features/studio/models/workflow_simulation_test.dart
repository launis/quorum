import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow_simulation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('WorkflowSimulationResponse Contract Tests', () {
    test(
      'Positive: deserializes valid JSON payload, applies defaults, and roundtrips cleanly via toJson',
      () {
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
          'errors': <Object?>[],
          'step_status': <String, Object?>{
            'stp_0195f3a00000700080008172bda70c86': 'ready',
            'stp_0195f3a00000700080008172bda70c87': 'ready',
          },
          'execution_order': <Object?>[
            'stp_0195f3a00000700080008172bda70c86',
            'stp_0195f3a00000700080008172bda70c87',
          ],
          'trace': <String, Object?>{
            'execution_time_ms': 18.5,
            'estimated_tokens': 420,
          },
        };

        final response = WorkflowSimulationResponse.fromJson(validResponseJson);

        expect(response.valid, isTrue);
        expect(response.errors, isEmpty);
        expect(
          response.stepStatus['stp_0195f3a00000700080008172bda70c86'],
          equals('ready'),
        );
        expect(
          response.executionOrder,
          equals(<String>[
            'stp_0195f3a00000700080008172bda70c86',
            'stp_0195f3a00000700080008172bda70c87',
          ]),
        );
        expect(response.trace.executionTimeMs, equals(18.5));
        expect(response.trace.estimatedTokens, equals(420));
        expect(response.toJson(), equals(validResponseJson));

        final updated = response.copyWith(
          valid: false,
          errors: const <String>['Cycle detected in DAG'],
          trace: const StepSimulationTraceDto(
            executionTimeMs: 25.0,
            estimatedTokens: 512,
          ),
        );
        expect(updated.valid, isFalse);
        expect(updated.errors, equals(<String>['Cycle detected in DAG']));
        expect(updated.trace.estimatedTokens, equals(512));
      },
    );

    test(
      'Negative 1: rejects unrecognized keys at root and nested trace levels (disallowUnrecognizedKeys)',
      () {
        final rootHallucinatedJson = <String, Object?>{
          'valid': true,
          'errors': <String>[],
          'step_status': <String, Object?>{},
          'execution_order': <Object?>[],
          'trace': <String, Object?>{},
          'hallucinated_key': 'fail',
        };

        expect(
          () => WorkflowSimulationResponse.fromJson(rootHallucinatedJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final nestedTraceHallucinatedJson = <String, Object?>{
          'valid': true,
          'trace': <String, Object?>{
            'execution_time_ms': 12.0,
            'estimated_tokens': 100,
            'unrecognized_trace_field': true,
          },
        };

        expect(
          () =>
              WorkflowSimulationResponse.fromJson(nestedTraceHallucinatedJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when field or collection element types are invalid',
      () {
        expect(
          () => WorkflowSimulationResponse.fromJson(<String, Object?>{
            'valid': 'not_a_bool',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => WorkflowSimulationResponse.fromJson(<String, Object?>{
            'step_status': <String, Object?>{'step_1': 12345},
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => WorkflowSimulationResponse.fromJson(<String, Object?>{
            'execution_order': <Object?>[999],
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
