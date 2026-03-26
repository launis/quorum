// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'app_exception.freezed.dart';
part 'app_exception.g.dart';

/// RFC 7807 Problem Details response model and Dart Exception.
///
/// This is the standardized error format returned by the backend API.
/// All API and frontend errors conform to this structure.
@freezed
abstract class AppException with _$AppException implements Exception {
  const AppException._();

  const factory AppException({
    @Default('about:blank') String type,
    @Default('Error') String title,
    @Default(500) int status,
    @Default('Unknown error') String detail,
    String? instance,
    @JsonKey(name: 'request_id') String? requestId,
    @Default(<String, dynamic>{}) Map<String, dynamic> extensions,
  }) = _AppException;

  factory AppException.fromJson(Map<String, Object?> json) =>
      _$AppExceptionFromJson(json);

  /// Extracts error code from type URI or extensions for localization lookup.
  ///
  /// Converts: `https://api.quorum.fi/errors/execution-not-found`
  /// To: `EXECUTION_NOT_FOUND`
  String get errorCode {
    if (extensions.containsKey('error_code')) {
      return extensions['error_code'].toString();
    }
    final slug = type.split('/').last;
    if (slug.isEmpty || slug == 'about:blank') return 'UNKNOWN_ERROR';
    return slug.replaceAll('-', '_').toUpperCase();
  }

  // --- Helper constructors for frontend-generated fallbacks ---

  factory AppException.network([Object? error]) => AppException(
    type: 'https://api.quorum.fi/errors/network-fatal',
    title: 'Network Error',
    status: 0,
    detail: error?.toString() ?? 'Network connection failed.',
    extensions: const {'error_code': 'NETWORK_FATAL'},
  );

  factory AppException.unknown([Object? error]) => AppException(
    type: 'https://api.quorum.fi/errors/unknown-error',
    title: 'Unknown Error',
    status: 500,
    detail: error?.toString() ?? 'An unknown error occurred.',
    extensions: const {'error_code': 'UNKNOWN_ERROR'},
  );

  factory AppException.unauthorized() => const AppException(
    type: 'https://api.quorum.fi/errors/authentication-failed',
    title: 'Unauthorized',
    status: 401,
    detail: 'Authentication is required.',
    extensions: const {'error_code': 'AUTHENTICATION_FAILED'},
  );

  factory AppException.notFound(String message) => AppException(
    type: 'https://api.quorum.fi/errors/resource-not-found',
    title: 'Not Found',
    status: 404,
    detail: message,
    extensions: const {'error_code': 'RESOURCE_NOT_FOUND'},
  );

  factory AppException.cancelled() => const AppException(
    type: 'https://api.quorum.fi/errors/cancelled',
    title: 'Cancelled',
    status: 499,
    detail: 'The request was cancelled.',
    extensions: const {'error_code': 'CANCELLED'},
  );

  factory AppException.validation(String message) => AppException(
    type: 'https://api.quorum.fi/errors/validation-failed',
    title: 'Validation Error',
    status: 400,
    detail: message,
    extensions: const {'error_code': 'VALIDATION_FAILED'},
  );
}
