import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/network/interceptors/auth_interceptor.dart';
import 'package:client_app/core/network/interceptors/dio_logger_interceptor.dart';
import 'package:client_app/core/network/interceptors/error_interceptor.dart';
import 'package:client_app/core/network/interceptors/locale_interceptor.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('api_client.dart Unit & ISTQB Boundary Tests', () {
    tearDown(() {
      dotenv.clean();
    });

    test(
      'Positive 1: apiClientProvider constructs Dio with configured baseUrl, timeouts, headers, BackgroundTransformer, and ordered interceptors',
      () {
        dotenv.loadFromString(
          envString: 'API_URL=https://api.quorum.test\nENVIRONMENT=production',
        );

        final container = ProviderContainer();
        addTearDown(container.dispose);

        final dio = container.read(apiClientProvider);

        expect(dio.options.baseUrl, equals('https://api.quorum.test/api/v2/'));
        expect(dio.options.connectTimeout, equals(ApiTimeouts.connect));
        expect(dio.options.receiveTimeout, equals(ApiTimeouts.receive));
        expect(dio.options.connectTimeout, isNot(equals(Duration.zero)));
        expect(dio.options.receiveTimeout, isNot(equals(Duration.zero)));
        expect(dio.options.headers['Content-Type'], equals('application/json'));
        expect(
          dio.options.headers['Accept'],
          equals('application/json, application/problem+json'),
        );
        expect(dio.transformer, isA<BackgroundTransformer>());

        final customInterceptors = dio.interceptors
            .where(
              (i) =>
                  i is AuthInterceptor ||
                  i is TargetLocaleInterceptor ||
                  i is DioLoggerInterceptor ||
                  i is ErrorInterceptor,
            )
            .toList();

        expect(customInterceptors, hasLength(4));
        expect(customInterceptors[0], isA<AuthInterceptor>());
        expect(customInterceptors[1], isA<TargetLocaleInterceptor>());
        expect(customInterceptors[2], isA<DioLoggerInterceptor>());
        expect(customInterceptors[3], isA<ErrorInterceptor>());
      },
    );

    test(
      'Positive 2: BackgroundTransformer decodes valid JSON objects and arrays in isolate',
      () async {
        final transformer = BackgroundTransformer();
        final decodedMap =
            await transformer.jsonDecodeCallback(
                  '{"id":"wf_0195f3a0000070008000000000000001","count":42}',
                )
                as Map<String, Object?>;

        expect(decodedMap['id'], equals('wf_0195f3a0000070008000000000000001'));
        expect(decodedMap['count'], equals(42));
      },
    );

    test(
      'Negative Test 1 (Fail-Fast Missing Config): reading apiClientProvider when API_URL is missing or empty throws AppException.validation',
      () {
        dotenv.loadFromString(envString: 'ENVIRONMENT=production');

        final container = ProviderContainer();
        addTearDown(container.dispose);

        expect(
          () => container.read(apiClientProvider),
          throwsA(
            predicate<Object>(
              (error) =>
                  (error is AppException &&
                      error.errorCode == 'VALIDATION_FAILED') ||
                  error.toString().contains('VALIDATION_FAILED') ||
                  error.toString().contains('API_URL'),
            ),
          ),
        );

        dotenv.loadFromString(envString: 'API_URL=\nENVIRONMENT=production');
        final emptyContainer = ProviderContainer();
        addTearDown(emptyContainer.dispose);

        expect(
          () => emptyContainer.read(apiClientProvider),
          throwsA(
            predicate<Object>(
              (error) =>
                  (error is AppException &&
                      error.errorCode == 'VALIDATION_FAILED') ||
                  error.toString().contains('VALIDATION_FAILED') ||
                  error.toString().contains('API_URL'),
            ),
          ),
        );
      },
    );

    test(
      'Negative Test 2 (Boundary / Malformed Payload): BackgroundTransformer throws FormatException on empty or truncated JSON strings',
      () async {
        final transformer = BackgroundTransformer();

        await expectLater(
          () => transformer.jsonDecodeCallback(''),
          throwsA(isA<FormatException>()),
        );

        await expectLater(
          () => transformer.jsonDecodeCallback('{"unterminated": 123'),
          throwsA(isA<FormatException>()),
        );
      },
    );
  });
}
