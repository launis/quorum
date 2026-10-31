import 'package:client_app/features/studio/models/gcp_location.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('GcpLocation Tests', () {
    test(
      'Positive: deserializes valid JSON payload, supports copyWith, and roundtrips cleanly',
      () {
        final validJson = <String, Object?>{
          'id': 'europe-north1',
          'label': 'Finland (europe-north1)',
          'description': 'Low-latency Nordic Vertex AI region',
        };

        final location = GcpLocation.fromJson(validJson);
        expect(location.id, equals('europe-north1'));
        expect(location.label, equals('Finland (europe-north1)'));
        expect(
          location.description,
          equals('Low-latency Nordic Vertex AI region'),
        );
        expect(location.toJson(), equals(validJson));

        final updated = location.copyWith(label: 'Europe North 1');
        expect(updated.id, equals('europe-north1'));
        expect(updated.label, equals('Europe North 1'));
        expect(
          updated.description,
          equals('Low-latency Nordic Vertex AI region'),
        );
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'id': 'europe-west1',
          'label': 'Belgium (europe-west1)',
          'description': 'Western Europe Vertex AI region',
          'unexpected_field': 'forbidden',
        };

        expect(
          () => GcpLocation.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when required fields are missing or have invalid types',
      () {
        final missingRequiredField = <String, Object?>{
          'id': 'us-central1',
          'label': 'Iowa (us-central1)',
        };
        expect(
          () => GcpLocation.fromJson(missingRequiredField),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final invalidFieldType = <String, Object?>{
          'id': 'us-central1',
          'label': 12345,
          'description': 'Invalid label type',
        };
        expect(
          () => GcpLocation.fromJson(invalidFieldType),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
