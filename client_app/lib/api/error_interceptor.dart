import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/error/problem_detail.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ErrorInterceptor extends Interceptor {
  final Ref ref;

  ErrorInterceptor(this.ref);

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Log failures
    final logger = ref.read(loggerServiceProvider);
    final path = err.requestOptions.path;
    final method = err.requestOptions.method;

    // Log the error
    if (err.response?.statusCode == 404) {
      logger.warning('HTTP', '404 Not Found: $method $path');
    } else {
      logger.error(
        'HTTP',
        'Request Failed: $method $path',
        err,
        err.stackTrace,
      );
    }

    // Log Response Body (Critical for Debugging 422 etc)
    if (err.response?.data != null) {
      logger.error('HTTP', 'Response Body: ${err.response?.data}');
    }

    // Check if response contains RFC 7807 Problem Details
    if (err.response?.data != null &&
        err.response!.data is Map<String, dynamic>) {
      final data = err.response!.data as Map<String, dynamic>;

      // RFC 7807 requires 'type' and 'status' fields
      if (data.containsKey('type') && data.containsKey('status')) {
        try {
          final problem = ProblemDetail.fromJson(data);
          final appError = AppError.fromProblemDetail(problem);

          handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              response: err.response,
              type: err.type,
              error: appError,
            ),
          );
          return;
        } catch (e) {
          logger.warning('HTTP', 'Failed to parse ProblemDetail: $e');
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
