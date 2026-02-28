import 'package:client_app/core/logging/logger_service.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DioLoggerInterceptor extends Interceptor {
  final Ref ref;

  DioLoggerInterceptor(this.ref);

  LoggerService get logger => ref.read(loggerServiceProvider);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    logger.info('HTTP', 'REQ: ${options.method} ${options.path}');
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    logger.info(
      'HTTP',
      'RES: ${response.statusCode} ${response.requestOptions.path}',
    );
    handler.next(response);
  }

  // onError is handled by ErrorInterceptor (to avoid double logging or specific handling)
  // But if we want raw logging even of handled errors?
  // ErrorInterceptor rejects with new error.
  // If we place this interceptor BEFORE ErrorInterceptor?
  // Request -> DioLogger -> ErrorInterceptor -> Network
  // Response <- DioLogger <- ErrorInterceptor <- Network
  // If ErrorInterceptor catches, does it propagate to DioLogger?
  // Rejection propagates to onError.

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // We let ErrorInterceptor handle the DETAILED logging of the error (with stack trace etc)
    // Here we just log the event if not handled?
    // Actually, ErrorInterceptor logs "Request Failed".
    // So we don't need to log here to avoid duplicates.
    handler.next(err);
  }
}
