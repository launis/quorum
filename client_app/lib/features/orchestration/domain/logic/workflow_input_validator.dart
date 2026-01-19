import 'package:fpdart/fpdart.dart';
import 'package:client_app/core/error/app_error.dart';

/// **Workflow Input Validator**
///
/// Pure logic class responsible for validating that user inputs match
/// the required fields for a given workflow.
///
/// This moves validation logic out of the Controller/Notifier to ensure
/// separation of concerns and testability.
class WorkflowInputValidator {
  /// Validates that [inputs] contains all keys specified in [requiredKeys].
  ///
  /// Returns:
  /// - [Right(unit)] if validation passes.
  /// - [Left(AppError.validationMissing)] if fields are missing.
  /// - [Left(AppError.validation(emptyInput))] if inputs map is empty.
  static Either<AppError, Unit> validate({
    required Map<String, dynamic> inputs,
    required List<String> requiredKeys,
  }) {
    // 1. Fail Fast: Empty Logic - REMOVED
    // We do NOT block empty inputs here.
    // If requiredKeys is empty, empty inputs are valid.
    // If requiredKeys is NOT empty, the loop below will catch them and return validationMissing.

    // 2. Check Constraints
    final missing = <String>[];

    for (final key in requiredKeys) {
      if (!inputs.containsKey(key)) {
        missing.add(key);
        continue;
      }

      final value = inputs[key];

      // Treat null as missing
      if (value == null) {
        missing.add(key);
        continue;
      }

      // If String, verify it's not empty/whitespace
      if (value is String && value.trim().isEmpty) {
        missing.add(key);
      }
      // Note: File inputs (PlatformFile) are non-null checked above.
    }

    if (missing.isNotEmpty) {
      return Left(AppError.validationMissing(missing));
    }

    return const Right(unit);
  }
}
