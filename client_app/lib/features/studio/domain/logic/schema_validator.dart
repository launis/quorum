import 'package:client_app/features/studio/domain/models/json_schema.dart';

/// Domain logic for validating values against a JsonSchema.
class SchemaValidator {
  /// Validates a [value] against the provided [schema].
  ///
  /// Returns `null` if valid, or a localized error message string if invalid.
  static String? validate(JsonSchema schema, dynamic value) {
    // 1. Null handling
    // If value is null, we assume valid at this level.
    // "Required" checks are typically done at the parent object level or form submit level.
    if (value == null) {
      return null;
    }

    // 2. Type: String
    if (schema.type == 'string' && value is String) {
      if (schema.minLength != null && value.length < schema.minLength!) {
        return 'Min length is ${schema.minLength}';
      }
      if (schema.maxLength != null && value.length > schema.maxLength!) {
        return 'Max length is ${schema.maxLength}';
      }
      // Future: Pattern/Regex check could go here
    }

    // 3. Type: Number / Integer
    if ((schema.type == 'number' || schema.type == 'integer') && value is num) {
      if (schema.minimum != null && value < schema.minimum!) {
        return 'Minimum value is ${schema.minimum}';
      }
      if (schema.maximum != null && value > schema.maximum!) {
        return 'Maximum value is ${schema.maximum}';
      }
    }

    // 4. Enum validation
    if (schema.enumValues != null && schema.enumValues!.isNotEmpty) {
      if (!schema.enumValues!.contains(value)) {
        return 'Value must be one of: ${schema.enumValues!.join(", ")}';
      }
    }

    // 5. Future: Pattern regex
    /*
    if (value is String && schema.pattern != null) {
       final reg = RegExp(schema.pattern!);
       if (!reg.hasMatch(value)) return 'Invalid format';
    }
    */

    return null;
  }
}
