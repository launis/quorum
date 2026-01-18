import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/error/problem_detail.dart';
import 'package:dio/dio.dart';

/// **RFC 7807 Error Interceptor**
///
/// Intercepts Dio errors and converts RFC 7807 Problem Details responses
/// to typed [AppError] instances.
///
/// **Architecture Role:**
/// This interceptor ensures all API errors are handled uniformly using
/// the RFC 7807 standard. It converts JSON error responses to [ProblemDetail]
/// and then to [AppError] for UI consumption.
///
/// **Error Flow:**
/// 1. Backend raises `AppException`
/// 2. Backend returns RFC 7807 JSON with `application/problem+json`
/// 3. This interceptor catches the error
/// 4. Parses to `ProblemDetail`
/// 5. Converts to `AppError` for UI localization
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Check if response contains RFC 7807 Problem Details
    if (err.response?.data != null && err.response!.data is Map<String, dynamic>) {
      final data = err.response!.data as Map<String, dynamic>;

      // RFC 7807 requires 'type' and 'status' fields
      if (data.containsKey('type') && data.containsKey('status')) {
        try {
          final problem = ProblemDetail.fromJson(data);
          final appError = AppError.fromProblemDetail(problem);

          // Create new DioException with AppError as error
          handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              response: err.response,
              type: err.type,
              error: appError,
            ),
          );
          return;
        } catch (_) {
          // Failed to parse, continue with original error
        }
      }
    }

    // Handle network errors without response
    if (err.type == DioExceptionType.connectionError ||
        err.type == DioExceptionType.connectionTimeout) {
      handler.reject(
        DioException(
          requestOptions: err.requestOptions,
          response: err.response,
          type: err.type,
          error: AppError.network(err),
        ),
      );
      return;
    }

    // Handle cancel
    if (err.type == DioExceptionType.cancel) {
      handler.reject(
        DioException(
          requestOptions: err.requestOptions,
          response: err.response,
          type: err.type,
          error: const AppError.cancelled(),
        ),
      );
      return;
    }

    // Fallback: wrap in unknown error
    handler.reject(
      DioException(
        requestOptions: err.requestOptions,
        response: err.response,
        type: err.type,
        error: AppError.unknown(err),
      ),
    );
  }
}
