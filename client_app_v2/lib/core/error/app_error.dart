import 'package:client_app/core/error/problem_detail.dart';

/// Base class for all application-specific errors.
///
/// Uses [Freezed] to create a union of all possible error types,
/// enabling exhaustive pattern matching in UI code.
///
/// **RFC 7807 Integration:**
/// Use [AppError.fromProblemDetail] to convert backend errors to typed AppError.
sealed class AppError implements Exception {
  const AppError();

  const factory AppError.unknown([Object? error, StackTrace? stackTrace]) =
      UnknownAppError;
  const factory AppError.network([Object? error]) = NetworkAppError;
  const factory AppError.server(String? message, [int? code]) = ServerAppError;
  const factory AppError.unauthorized() = UnauthorizedAppError;
  const factory AppError.notFound(String message) = NotFoundAppError;
  const factory AppError.validation(ValidationErrorReason reason) =
      ValidationAppError;
  const factory AppError.validationMissing(List<String> fields) =
      ValidationMissingAppError;
  const factory AppError.serverParsingError(String message) =
      ServerParsingAppError;
  const factory AppError.networkError(String message) = NetworkErrorAppError;
  const factory AppError.cancelled() = CancelledAppError;
  const factory AppError.api({
    required String errorCode,
    required String detail,
    required int status,
    String? instance,
  }) = ApiAppError;

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
        print(
          '[ErrorInterceptor] 404 Not Found: ${problem.detail} at ${problem.instance ?? "unknown path"}',
        );
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

class UnknownAppError extends AppError {
  final Object? error;
  final StackTrace? stackTrace;
  const UnknownAppError([this.error, this.stackTrace]);
}

class NetworkAppError extends AppError {
  final Object? error;
  const NetworkAppError([this.error]);
}

class ServerAppError extends AppError {
  final String? message;
  final int? code;
  const ServerAppError(this.message, [this.code]);
}

class UnauthorizedAppError extends AppError {
  const UnauthorizedAppError();
}

class NotFoundAppError extends AppError {
  final String message;
  const NotFoundAppError(this.message);
}

class ValidationAppError extends AppError {
  final ValidationErrorReason reason;
  const ValidationAppError(this.reason);
}

class ServerParsingAppError extends AppError {
  final String message;
  const ServerParsingAppError(this.message);
}

class NetworkErrorAppError extends AppError {
  final String message;
  const NetworkErrorAppError(this.message);
}

class ValidationMissingAppError extends AppError {
  final List<String> fields;
  const ValidationMissingAppError(this.fields);
}

class CancelledAppError extends AppError {
  const CancelledAppError();
}

class ApiAppError extends AppError {
  final String errorCode;
  final String detail;
  final int status;
  final String? instance;
  const ApiAppError({
    required this.errorCode,
    required this.detail,
    required this.status,
    this.instance,
  });
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
