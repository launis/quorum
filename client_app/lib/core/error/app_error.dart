import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/error/problem_detail.dart';

part 'app_error.freezed.dart';

/// Base class for all application-specific errors.
///
/// Uses [Freezed] to create a union of all possible error types,
/// enabling exhaustive pattern matching in UI code.
///
/// **RFC 7807 Integration:**
/// Use [AppError.fromProblemDetail] to convert backend errors to typed AppError.
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

  /// API error with error_code for localization lookup.
  ///
  /// This is the primary factory for RFC 7807 errors from backend.
  const factory AppError.api({
    required String errorCode,
    required String detail,
    required int status,
    String? instance,
  }) = _Api;

  /// Creates an [AppError] from RFC 7807 [ProblemDetail].
  ///
  /// Maps common status codes to typed errors, falls back to [AppError.api]
  /// for specific error_code based handling.
  ///
  /// Example:
  /// ```dart
  /// on DioException catch (e) {
  ///   final problem = ProblemDetail.fromJson(e.response?.data);
  ///   throw AppError.fromProblemDetail(problem);
  /// }
  /// ```
  static AppError fromProblemDetail(ProblemDetail problem) {
    // Map common status codes to typed errors
    switch (problem.status) {
      case 401:
        return const AppError.unauthorized();
      case 404:
        print('[ErrorInterceptor] 404 Not Found: ${problem.detail} at ${problem.instance ?? "unknown path"}');
        return AppError.notFound(problem.detail);
      case >= 500:
        return AppError.server(problem.detail, problem.status);
      default:
        // Use generic api error with errorCode for localization
        return AppError.api(
          errorCode: problem.errorCode,
          detail: problem.detail,
          status: problem.status,
          instance: problem.instance,
        );
    }
  }
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
