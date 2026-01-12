import 'package:freezed_annotation/freezed_annotation.dart';

part 'app_error.freezed.dart';

/// Base class for all application-specific errors.
///
/// Uses [Freezed] to create a union of all possible error types,
/// enabling exhaustive pattern matching in UI code.
@freezed
sealed class AppError with _$AppError implements Exception {
  /// Unknown or unexpected error.
  const factory AppError.unknown([Object? error, StackTrace? stackTrace]) =
      _Unknown;

  /// Network connectivity issues (e.g., offline, timeout).
  const factory AppError.network([Object? error]) = _Network;

  /// Server returned a 5xx error.
  const factory AppError.server(String? message, [int? code]) = _Server;

  /// Authentication failed (401).
  const factory AppError.unauthorized() = _Unauthorized;

  /// Resource not found (404).
  const factory AppError.notFound(String message) = _NotFound;

  /// Validation or Bad Request (400/422).
  ///
  /// Forces localization by using an enum instead of raw strings.
  const factory AppError.validation(ValidationErrorReason reason) = _Validation;

  /// Specific validation error for missing fields.
  const factory AppError.validationMissing(List<String> fields) =
      _ValidationMissing;

  /// Operation cancelled by user.
  const factory AppError.cancelled() = _Cancelled;
}

/// Enumeration of strict validation reasons for localization.
enum ValidationErrorReason {
  emptyInput,
  invalidEmail,
  passwordTooWeak,
  invalidDate,
  demoteLastAdmin,
  unknown,
}
