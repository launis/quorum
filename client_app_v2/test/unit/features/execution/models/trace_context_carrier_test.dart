import 'package:client_app/features/execution/models/trace_context_carrier.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('TraceContextCarrier Tests', () {
    const validTraceparent =
        '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01';

    test(
      'Positive: deserializes valid W3C trace context payload with and without tracestate and roundtrips cleanly',
      () {
        final fullJson = <String, Object?>{
          'traceparent': validTraceparent,
          'tracestate': 'congo=t61rcWkgMzE,rojo=00f067aa0ba902b7',
        };

        final carrier = TraceContextCarrier.fromJson(fullJson);
        expect(carrier.traceparent, equals(validTraceparent));
        expect(
          carrier.tracestate,
          equals('congo=t61rcWkgMzE,rojo=00f067aa0ba902b7'),
        );
        expect(carrier.toJson(), equals(fullJson));

        final minimalJson = <String, Object?>{
          'traceparent': validTraceparent,
        };
        final minimalCarrier = TraceContextCarrier.fromJson(minimalJson);
        expect(minimalCarrier.traceparent, equals(validTraceparent));
        expect(minimalCarrier.tracestate, isNull);
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'traceparent': validTraceparent,
          'tracestate': 'rojo=00f067aa0ba902b7',
          'unexpected_field': 'forbidden',
        };

        expect(
          () => TraceContextCarrier.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when required traceparent is missing or has invalid type',
      () {
        final missingRequired = <String, Object?>{
          'tracestate': 'congo=t61rcWkgMzE',
        };
        expect(
          () => TraceContextCarrier.fromJson(missingRequired),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final invalidType = <String, Object?>{
          'traceparent': 12345,
          'tracestate': 'congo=t61rcWkgMzE',
        };
        expect(
          () => TraceContextCarrier.fromJson(invalidType),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
