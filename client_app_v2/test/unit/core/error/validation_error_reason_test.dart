import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/validation_error_reason.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ValidationErrorReason Hardening & ISTQB Boundary Tests (Profile A)', () {
    test(
      'Positive 1: exposes canonical snake_case backendValue wire identifiers across all 10 enum members',
      () {
        final expectedWireMap = <ValidationErrorReason, String>{
          ValidationErrorReason.required: 'required',
          ValidationErrorReason.minItems: 'min_items',
          ValidationErrorReason.maxItems: 'max_items',
          ValidationErrorReason.pattern: 'pattern',
          ValidationErrorReason.format: 'format',
          ValidationErrorReason.minLength: 'min_length',
          ValidationErrorReason.maxLength: 'max_length',
          ValidationErrorReason.minimum: 'minimum',
          ValidationErrorReason.maximum: 'maximum',
          ValidationErrorReason.unknown: 'unknown',
        };

        expect(
          ValidationErrorReason.values.length,
          equals(expectedWireMap.length),
        );

        for (final entry in expectedWireMap.entries) {
          expect(entry.key.backendValue, equals(entry.value));
        }

        expect(
          ValidationErrorReason.unknown.toString(),
          equals('ValidationErrorReason.unknown'),
        );
      },
    );

    test(
      'Positive 2: parseStrict resolves all members deterministically from snake_case backendValue and camelCase name',
      () {
        for (final reason in ValidationErrorReason.values) {
          expect(
            ValidationErrorReason.parseStrict(reason.backendValue),
            same(reason),
          );
          expect(ValidationErrorReason.parseStrict(reason.name), same(reason));
          expect(
            ValidationErrorReason.parseStrict('  ${reason.backendValue}  '),
            same(reason),
          );
        }
      },
    );

    test(
      'Negative 1: parseStrict throws AppException (VALIDATION_FAILED) on unrecognized or case-mismatched reason codes',
      () {
        for (final invalidInput in <String>[
          'unrecognized_constraint',
          'REQUIRED',
          'MIN_ITEMS',
          'null',
        ]) {
          expect(
            () => ValidationErrorReason.parseStrict(invalidInput),
            throwsA(
              isA<AppException>()
                  .having((e) => e.status, 'status', equals(400))
                  .having(
                    (e) => e.errorCode,
                    'errorCode',
                    equals('VALIDATION_FAILED'),
                  ),
            ),
            reason: 'Expected Fail-Fast AppException for input "$invalidInput"',
          );
        }
      },
    );

    test(
      'Negative 2 (ISTQB Boundary Value Analysis): parseStrict throws AppException on empty, whitespace-only, and off-by-one boundary strings',
      () {
        for (final boundaryInput in <String>[
          '',
          '   ',
          '\t\n',
          'require',
          'required_',
          'min_item',
          'min_items_extra',
        ]) {
          expect(
            () => ValidationErrorReason.parseStrict(boundaryInput),
            throwsA(
              isA<AppException>()
                  .having((e) => e.status, 'status', equals(400))
                  .having(
                    (e) => e.errorCode,
                    'errorCode',
                    equals('VALIDATION_FAILED'),
                  ),
            ),
            reason:
                'Expected Fail-Fast AppException for boundary input "$boundaryInput"',
          );
        }
      },
    );
  });
}
