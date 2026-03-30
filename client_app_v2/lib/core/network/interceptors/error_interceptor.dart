import 'package:client_app/core/error/app_exception.dart';
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

    // Handle Gateway/Auth errors (401, 403) eagerly, regardless of payload format
    if (err.response?.statusCode == 401 || err.response?.statusCode == 403) {
      handler.reject(
        DioException(
          requestOptions: err.requestOptions,
          response: err.response,
          type: err.type,
          error: AppException.unauthorized(),
        ),
      );
      return;
    }

    // Check if response contains RFC 7807 Problem Details or FastAPI standard responses
    if (err.response?.data != null &&
        err.response!.data is Map<String, dynamic>) {
      final data = err.response!.data as Map<String, dynamic>;

      // RFC 7807 requires 'type' and 'status' fields
      if (data.containsKey('type') && data.containsKey('status')) {
        try {
          final appException = AppException.fromJson(data);

          handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              response: err.response,
              type: err.type,
              error: appException,
            ),
          );
          return;
        } catch (e) {
          logger.warning('HTTP', 'Failed to parse AppException: $e');
        }
      } else if (err.response?.statusCode == 422 &&
          data.containsKey('detail')) {
        // Fallback for FastAPI standard Validation Errors (HTTP 422)
        final detail = data['detail'];
        String parsedDetail = 'Validation failed';
        if (detail is List) {
          parsedDetail = detail.map((e) => e.toString()).join('\n');
        } else if (detail is String) {
          parsedDetail = detail;
        }

        handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            response: err.response,
            type: err.type,
            error: AppException.validation(parsedDetail),
          ),
        );
        return;
      }
    }

    // Handle network errors without response
    if (err.type == DioExceptionType.connectionError ||
        err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.sendTimeout) {
      handler.reject(
        DioException(
          requestOptions: err.requestOptions,
          response: err.response,
          type: err.type,
          error: AppException.network(err),
        ),
      );
      return;
    }

    // Handle Proxy/Gateway failures (502, 503, 504) where payload is not RFC 7807
    if (err.response != null &&
        (err.response!.statusCode == 502 ||
            err.response!.statusCode == 503 ||
            err.response!.statusCode == 504)) {
      handler.reject(
        DioException(
          requestOptions: err.requestOptions,
          response: err.response,
          type: err.type,
          error: AppException.network(err),
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
          error: AppException.cancelled(),
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
        error: AppException.unknown(err),
      ),
    );
  }
}
