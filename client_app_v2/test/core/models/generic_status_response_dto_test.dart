import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('GenericStatusResponseDto', () {
    test('deserializes valid JSON with status and message', () {
      final json = {'status': 'ok', 'message': 'Operation successful'};

      final dto = GenericStatusResponseDto.fromJson(json);
      expect(dto.status, equals('ok'));
      expect(dto.message, equals('Operation successful'));
    });

    test('serializes to valid JSON matching backend contract', () {
      const dto = GenericStatusResponseDto(
        status: 'ok',
        message: 'Saved successfully',
      );

      final json = dto.toJson();
      expect(json['status'], equals('ok'));
      expect(json['message'], equals('Saved successfully'));
    });

    test(
      'Negative Test 1: throws exception on unrecognized keys due to disallowUnrecognizedKeys',
      () {
        final invalidJson = {
          'status': 'ok',
          'message': 'Saved successfully',
          'unexpected_extra_key': 'banned payload',
        };

        expect(
          () => GenericStatusResponseDto.fromJson(invalidJson),
          throwsA(anything),
        );
      },
    );

    test(
      'Negative Test 2: throws exception when required message field is missing',
      () {
        final missingFieldJson = {'status': 'ok'};

        expect(
          () => GenericStatusResponseDto.fromJson(missingFieldJson),
          throwsA(anything),
        );
      },
    );
  });
}
