import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/domain/logic/workflow_input_validator.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';

void main() {
  group('WorkflowInputValidator', () {
    test('should allow empty inputs when requiredKeys is empty', () {
      final result = WorkflowInputValidator.validate(
        inputs: {},
        requiredKeys: [],
      );

      expect(result.isRight(), true);
    });

    test('should return validationMissing when inputs are empty but keys are required', () {
      final result = WorkflowInputValidator.validate(
        inputs: {},
        requiredKeys: ['required_field'],
      );

      expect(result.isLeft(), true);
      result.fold(
        (error) {
           error.maybeWhen(
            validationMissing: (fields) {
              expect(fields.length, 1);
              expect(fields.first, 'required_field');
            },
            orElse: () => fail('Wrong error type: $error'),
          );
        },
        (_) => fail('Should have failed'),
      );
    });

    test('should return validationMissing for empty string values', () {
      final result = WorkflowInputValidator.validate(
        inputs: {'required_field': '   '},
        requiredKeys: ['required_field'],
      );

      expect(result.isLeft(), true);
      result.fold(
        (error) {
           error.maybeWhen(
            validationMissing: (fields) {
              expect(fields.contains('required_field'), true);
            },
            orElse: () => fail('Wrong error type: $error'),
          );
        },
        (_) => fail('Should have failed'),
      );
    });

    test('should pass valid input', () {
      final result = WorkflowInputValidator.validate(
        inputs: {'required_field': 'valid'},
        requiredKeys: ['required_field'],
      );

      expect(result.isRight(), true);
    });
  });
}
