import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/network/interceptors/dio_logger_interceptor.dart';
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockLoggerService extends Mock implements LoggerService {}

class _MockRequestInterceptorHandler extends Mock
    implements RequestInterceptorHandler {}

class _MockResponseInterceptorHandler extends Mock
    implements ResponseInterceptorHandler {}

class _MockErrorInterceptorHandler extends Mock
    implements ErrorInterceptorHandler {}

void main() {
  group('DioLoggerInterceptor Unit & ISTQB Boundary Tests', () {
    late _MockLoggerService mockLogger;
    late _MockRequestInterceptorHandler mockRequestHandler;
    late _MockResponseInterceptorHandler mockResponseHandler;
    late _MockErrorInterceptorHandler mockErrorHandler;

    setUp(() {
      dotenv.loadFromString(
        envString: 'API_URL=https://api.quorum.test\nENVIRONMENT=production',
      );
      mockLogger = _MockLoggerService();
      mockRequestHandler = _MockRequestInterceptorHandler();
      mockResponseHandler = _MockResponseInterceptorHandler();
      mockErrorHandler = _MockErrorInterceptorHandler();
    });

    tearDown(() {
      dotenv.clean();
    });

    DioLoggerInterceptor resolveInterceptor() {
      final container = ProviderContainer(
        overrides: [loggerServiceProvider.overrideWithValue(mockLogger)],
      );
      addTearDown(container.dispose);
      final dio = container.read(apiClientProvider);
      return dio.interceptors.whereType<DioLoggerInterceptor>().single;
    }

    test(
      'Positive 1: onRequest logs HTTP method and path and forwards RequestOptions to handler.next',
      () {
        final interceptor = resolveInterceptor();
        final options = RequestOptions(
          path: '/execution/executions/exe_0195f3a0000070008000000000000001',
          method: 'POST',
        );

        interceptor.onRequest(options, mockRequestHandler);

        verify(
          () => mockLogger.info(
            'HTTP',
            'REQ: POST /execution/executions/exe_0195f3a0000070008000000000000001',
          ),
        ).called(1);
        verify(() => mockRequestHandler.next(options)).called(1);
      },
    );

    test(
      'Positive 2: onResponse logs HTTP status code and request path and forwards Response<Object?> to handler.next',
      () {
        final interceptor = resolveInterceptor();
        final requestOptions = RequestOptions(
          path: '/studio/workflows/',
          method: 'GET',
        );
        final response = Response<Object?>(
          requestOptions: requestOptions,
          statusCode: 200,
          data: <String, Object?>{'status': 'ok'},
        );

        interceptor.onResponse(response, mockResponseHandler);

        verify(
          () => mockLogger.info('HTTP', 'RES: 200 /studio/workflows/'),
        ).called(1);
        verify(() => mockResponseHandler.next(response)).called(1);
      },
    );

    test(
      'Negative Test 1: onError forwards DioException to handler.next without duplicate logging',
      () {
        final interceptor = resolveInterceptor();
        final requestOptions = RequestOptions(
          path: '/execution/executions/exe_0195f3a0000070008000000000000001',
          method: 'GET',
        );
        final dioError = DioException(
          requestOptions: requestOptions,
          type: DioExceptionType.connectionTimeout,
          message: 'Connection timed out',
        );

        interceptor.onError(dioError, mockErrorHandler);

        verify(() => mockErrorHandler.next(dioError)).called(1);
        verifyZeroInteractions(mockLogger);
      },
    );

    test(
      'Negative Test 2 (Boundary Value Analysis): onResponse handles null statusCode and empty path boundary without crashing',
      () {
        final interceptor = resolveInterceptor();
        final requestOptions = RequestOptions(path: '', method: 'HEAD');
        final response = Response<Object?>(
          requestOptions: requestOptions,
          statusCode: null,
          data: null,
        );

        interceptor.onResponse(response, mockResponseHandler);

        verify(() => mockLogger.info('HTTP', 'RES: null ')).called(1);
        verify(() => mockResponseHandler.next(response)).called(1);
      },
    );
  });
}
