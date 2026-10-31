import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/network/interceptors/error_interceptor.dart';
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockLoggerService extends Mock implements LoggerService {}

class _MockErrorInterceptorHandler extends Mock
    implements ErrorInterceptorHandler {}

void main() {
  setUpAll(() {
    registerFallbackValue(
      DioException(requestOptions: RequestOptions(path: '/fallback')),
    );
    registerFallbackValue(StackTrace.empty);
  });

  group('ErrorInterceptor Unit & ISTQB Boundary Tests', () {
    late _MockLoggerService mockLogger;
    late _MockErrorInterceptorHandler mockErrorHandler;

    setUp(() {
      dotenv.loadFromString(
        envString: 'API_URL=https://api.quorum.test\nENVIRONMENT=production',
      );
      mockLogger = _MockLoggerService();
      mockErrorHandler = _MockErrorInterceptorHandler();
    });

    tearDown(() {
      dotenv.clean();
    });

    ErrorInterceptor resolveInterceptor() {
      final container = ProviderContainer(
        overrides: [loggerServiceProvider.overrideWithValue(mockLogger)],
      );
      addTearDown(container.dispose);
      final dio = container.read(apiClientProvider);
      return dio.interceptors.whereType<ErrorInterceptor>().single;
    }

    AppException captureRejectedAppException() {
      final captured = verify(
        () => mockErrorHandler.reject(captureAny()),
      ).captured;
      expect(captured, hasLength(1));
      final rejectedDioErr = captured.single as DioException;
      expect(rejectedDioErr.error, isA<AppException>());
      return rejectedDioErr.error as AppException;
    }

    test(
      'Positive 1: parses RFC 7807 Problem Details payload into AppException and logs request and body',
      () {
        final interceptor = resolveInterceptor();
        final requestOptions = RequestOptions(
          path: '/studio/workflows/wf_0195f3a0000070008000000000000001',
          method: 'PUT',
        );
        final rfcPayload = <String, Object?>{
          'type': 'https://api.quorum.fi/errors/workflow-not-found',
          'title': 'Workflow Not Found',
          'status': 404,
          'detail': 'Target workflow does not exist.',
          'request_id': 'req_0195f3a0000070008000000000000099',
          'extensions': <String, Object?>{'error_code': 'WORKFLOW_NOT_FOUND'},
        };
        final dioError = DioException(
          requestOptions: requestOptions,
          type: DioExceptionType.badResponse,
          response: Response<Object?>(
            requestOptions: requestOptions,
            statusCode: 404,
            data: rfcPayload,
          ),
        );

        interceptor.onError(dioError, mockErrorHandler);

        verify(
          () => mockLogger.warning(
            'HTTP',
            '404 Not Found: PUT /studio/workflows/wf_0195f3a0000070008000000000000001',
          ),
        ).called(1);
        verify(
          () => mockLogger.error('HTTP', 'Response Body: $rfcPayload'),
        ).called(1);

        final appException = captureRejectedAppException();
        expect(appException.status, equals(404));
        expect(appException.title, equals('Workflow Not Found'));
        expect(appException.detail, equals('Target workflow does not exist.'));
        expect(
          appException.requestId,
          equals('req_0195f3a0000070008000000000000099'),
        );
        expect(appException.errorCode, equals('WORKFLOW_NOT_FOUND'));
      },
    );

    test(
      'Positive 2: translates FastAPI 422 validation payloads (List and String) and request cancellation into typed AppExceptions',
      () {
        final interceptor = resolveInterceptor();
        final requestOptions = RequestOptions(
          path: '/execution/run',
          method: 'POST',
        );

        // Case A: FastAPI 422 List detail
        final list422Error = DioException(
          requestOptions: requestOptions,
          type: DioExceptionType.badResponse,
          response: Response<Object?>(
            requestOptions: requestOptions,
            statusCode: 422,
            data: <String, Object?>{
              'detail': <Object?>['field_a is required', 'field_b is invalid'],
            },
          ),
        );

        interceptor.onError(list422Error, mockErrorHandler);
        final listException = captureRejectedAppException();
        expect(listException.errorCode, equals('VALIDATION_FAILED'));
        expect(
          listException.detail,
          equals('field_a is required\nfield_b is invalid'),
        );

        // Case B: FastAPI 422 String detail
        reset(mockErrorHandler);
        final string422Error = DioException(
          requestOptions: requestOptions,
          type: DioExceptionType.badResponse,
          response: Response<Object?>(
            requestOptions: requestOptions,
            statusCode: 422,
            data: <String, Object?>{'detail': 'Payload schema mismatch'},
          ),
        );

        interceptor.onError(string422Error, mockErrorHandler);
        final stringException = captureRejectedAppException();
        expect(stringException.errorCode, equals('VALIDATION_FAILED'));
        expect(stringException.detail, equals('Payload schema mismatch'));

        // Case C: Request cancellation
        reset(mockErrorHandler);
        final cancelError = DioException(
          requestOptions: requestOptions,
          type: DioExceptionType.cancel,
        );

        interceptor.onError(cancelError, mockErrorHandler);
        final cancelledException = captureRejectedAppException();
        expect(cancelledException.errorCode, equals('CANCELLED'));
        expect(cancelledException.status, equals(499));
      },
    );

    test(
      'Negative 1 (Network & Gateway Fault Isolation): maps transport timeouts, connection errors, and non-RFC 502/503/504 responses to AppException.network',
      () {
        final interceptor = resolveInterceptor();
        final requestOptions = RequestOptions(
          path: '/execution/stream',
          method: 'GET',
        );

        for (final netType in <DioExceptionType>[
          DioExceptionType.connectionError,
          DioExceptionType.connectionTimeout,
          DioExceptionType.receiveTimeout,
          DioExceptionType.sendTimeout,
        ]) {
          reset(mockErrorHandler);
          final err = DioException(
            requestOptions: requestOptions,
            type: netType,
            message: 'Transport failure: ${netType.name}',
          );

          interceptor.onError(err, mockErrorHandler);
          final appException = captureRejectedAppException();
          expect(appException.errorCode, equals('NETWORK_FATAL'));
          expect(appException.status, equals(0));
        }

        // Gateway status codes 502, 503, 504 with non-RFC body map to NETWORK_FATAL
        for (final gatewayStatus in <int>[502, 503, 504]) {
          reset(mockErrorHandler);
          final gatewayErr = DioException(
            requestOptions: requestOptions,
            type: DioExceptionType.badResponse,
            response: Response<Object?>(
              requestOptions: requestOptions,
              statusCode: gatewayStatus,
              data: 'Bad Gateway HTML',
            ),
          );

          interceptor.onError(gatewayErr, mockErrorHandler);
          final appException = captureRejectedAppException();
          expect(appException.errorCode, equals('NETWORK_FATAL'));
        }
      },
    );

    test(
      'Negative 2 (ISTQB Boundary Value Analysis & Malformed RFC 7807 Payload): enforces auth/gateway boundaries (400/401/402/403, 501/505) and logs error on malformed RFC 7807 data',
      () {
        final interceptor = resolveInterceptor();
        final requestOptions = RequestOptions(
          path: '/studio/prompt-blocks',
          method: 'GET',
        );

        // Auth boundaries: 401 and 403 -> AUTHENTICATION_FAILED; 400 and 402 -> UNKNOWN_ERROR (when non-RFC)
        final statusExpectations = <int, String>{
          400: 'UNKNOWN_ERROR',
          401: 'AUTHENTICATION_FAILED',
          402: 'UNKNOWN_ERROR',
          403: 'AUTHENTICATION_FAILED',
          501: 'UNKNOWN_ERROR',
          505: 'UNKNOWN_ERROR',
        };

        for (final entry in statusExpectations.entries) {
          reset(mockErrorHandler);
          final err = DioException(
            requestOptions: requestOptions,
            type: DioExceptionType.badResponse,
            response: Response<Object?>(
              requestOptions: requestOptions,
              statusCode: entry.key,
              data: 'plain error body',
            ),
          );

          interceptor.onError(err, mockErrorHandler);
          final appException = captureRejectedAppException();
          expect(
            appException.errorCode,
            equals(entry.value),
            reason: 'Status ${entry.key} should map to ${entry.value}',
          );
        }

        // Malformed RFC 7807 payload (status is String instead of int) triggers logger.error and falls back to UNKNOWN_ERROR
        reset(mockErrorHandler);
        reset(mockLogger);
        final malformedRfcError = DioException(
          requestOptions: requestOptions,
          type: DioExceptionType.badResponse,
          response: Response<Object?>(
            requestOptions: requestOptions,
            statusCode: 500,
            data: <String, Object?>{
              'type': 'https://api.quorum.fi/errors/corrupt',
              'status': 'invalid_int_type',
            },
          ),
        );

        interceptor.onError(malformedRfcError, mockErrorHandler);

        verify(
          () => mockLogger.error(
            'HTTP',
            'Failed to parse RFC 7807 AppException payload',
            any(),
            any(),
          ),
        ).called(1);

        final fallbackException = captureRejectedAppException();
        expect(fallbackException.errorCode, equals('UNKNOWN_ERROR'));
        expect(fallbackException.status, equals(500));
      },
    );
  });
}
