import 'package:client_app/core/error/app_exception.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

/// Canonical JSON Schema and RFC 7807 field validation failure reasons.
///
/// Enforces strict 1:1 snake_case serialization parity with backend validation
/// constraint identifiers and Fail-Fast parsing without silent fallbacks.
@JsonEnum(valueField: 'backendValue')
enum ValidationErrorReason {
  @JsonValue('required')
  required('required'),
  @JsonValue('min_items')
  minItems('min_items'),
  @JsonValue('max_items')
  maxItems('max_items'),
  @JsonValue('pattern')
  pattern('pattern'),
  @JsonValue('format')
  format('format'),
  @JsonValue('min_length')
  minLength('min_length'),
  @JsonValue('max_length')
  maxLength('max_length'),
  @JsonValue('minimum')
  minimum('minimum'),
  @JsonValue('maximum')
  maximum('maximum'),
  @JsonValue('unknown')
  unknown('unknown');

  const ValidationErrorReason(this.backendValue);

  /// Canonical snake_case wire identifier used in backend validation payloads.
  final String backendValue;

  /// Resolves a [ValidationErrorReason] from its canonical [backendValue] or Dart [name].
  ///
  /// Throws [AppException.validation] immediately if [rawReason] is empty, whitespace-only,
  /// or does not match a known validation constraint reason (Zero-Fallback mandate).
  static ValidationErrorReason parseStrict(String rawReason) {
    final normalized = rawReason.trim();
    if (normalized.isEmpty) {
      throw AppException.validation(
        'Fail-Fast: ValidationErrorReason cannot be empty.',
      );
    }

    for (final reason in ValidationErrorReason.values) {
      if (reason.backendValue == normalized || reason.name == normalized) {
        return reason;
      }
    }

    throw AppException.validation(
      'Fail-Fast: Unrecognized ValidationErrorReason "$rawReason".',
    );
  }
}
