import 'package:client_app/features/execution/models/execution_metrics_dto.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionMetricsDTO Tests', () {
    test(
      'Positive: deserializes valid JSON payload, applies duration_ms default, and roundtrips cleanly',
      () {
        final fullJson = <String, dynamic>{
          'total_atoms': 42,
          'evaluated': 35,
          'short_circuited_na': 7,
          'duration_ms': 1250,
        };

        final dto = ExecutionMetricsDTO.fromJson(fullJson);
        expect(dto.totalAtoms, equals(42));
        expect(dto.evaluated, equals(35));
        expect(dto.shortCircuitedNa, equals(7));
        expect(dto.durationMs, equals(1250));
        expect(dto.toJson(), equals(fullJson));

        final defaultDurationJson = <String, dynamic>{
          'total_atoms': 10,
          'evaluated': 8,
          'short_circuited_na': 2,
        };
        final dtoWithDefault = ExecutionMetricsDTO.fromJson(
          defaultDurationJson,
        );
        expect(dtoWithDefault.durationMs, equals(0));
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, dynamic>{
          'total_atoms': 10,
          'evaluated': 8,
          'short_circuited_na': 2,
          'duration_ms': 500,
          'unexpected_field': 'forbidden',
        };

        expect(
          () => ExecutionMetricsDTO.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when required fields are missing or have invalid types',
      () {
        final missingRequired = <String, dynamic>{
          'evaluated': 8,
          'short_circuited_na': 2,
        };
        expect(
          () => ExecutionMetricsDTO.fromJson(missingRequired),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final invalidType = <String, dynamic>{
          'total_atoms': 'forty-two',
          'evaluated': 35,
          'short_circuited_na': 7,
        };
        expect(
          () => ExecutionMetricsDTO.fromJson(invalidType),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
