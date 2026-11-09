import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Normalizes Dio HTTP and transport failures into typed [AppException] instances.
class ErrorInterceptor extends Interceptor {
  final Ref ref;

  ErrorInterceptor(this.ref);

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final logger = ref.read(loggerServiceProvider);
    final path = err.requestOptions.path;
    final method = err.requestOptions.method;

    // Downgrade 404 responses to warning to avoid false-positive error telemetry on probe lookups.
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

    // Preserve raw response payload in logs to diagnose 422/500 schema mismatches.
    if (err.response?.data != null) {
      logger.error('HTTP', 'Response Body: ${err.response?.data}');
    }

    // Parse structured RFC 7807 Problem Details or FastAPI 422 validation payloads first
    // so HTTP 403 SECURITY_VIOLATION / PERMISSION_DENIED payloads are preserved before the bare 401/403 fallback.
    if (err.response?.data != null &&
        err.response!.data is Map<String, Object?>) {
      final data = err.response!.data as Map<String, Object?>;

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
        } catch (e, stack) {
          logger.error(
            'HTTP',
            'Failed to parse RFC 7807 AppException payload',
            e,
            stack,
          );
        }
      } else if (err.response?.statusCode == 422 &&
          data.containsKey('detail')) {
        // Translate raw FastAPI 422 validation payloads into AppException.validation.
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

    // Intercept non-RFC 401/403 gateway responses because upstream proxies may omit RFC 7807 bodies.
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

    // Map transport-level timeouts and socket failures to AppException.network for graceful UI degradation.
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

    // Normalize non-RFC 7807 proxy/gateway failures (502, 503, 504) to network errors for graceful degradation.
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
