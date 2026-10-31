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
  void onResponse(
    Response<Object?> response,
    ResponseInterceptorHandler handler,
  ) {
    logger.info(
      'HTTP',
      'RES: ${response.statusCode} ${response.requestOptions.path}',
    );
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Delegate error logging to ErrorInterceptor to avoid duplicate entries.
    handler.next(err);
  }
}
