import 'dart:ui';

import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/network/interceptors/locale_interceptor.dart';
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockRequestInterceptorHandler extends Mock
    implements RequestInterceptorHandler {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() {
    registerFallbackValue(RequestOptions(path: '/fallback'));
    registerFallbackValue(
      DioException(requestOptions: RequestOptions(path: '/fallback')),
    );
  });

  group('TargetLocaleInterceptor Unit & ISTQB Boundary Tests', () {
    late _MockRequestInterceptorHandler mockRequestHandler;

    setUp(() {
      dotenv.loadFromString(
        envString: 'API_URL=https://api.quorum.test\nENVIRONMENT=production',
      );
      mockRequestHandler = _MockRequestInterceptorHandler();
    });

    tearDown(() {
      dotenv.clean();
    });

    TargetLocaleInterceptor resolveFromApiClient() {
      final container = ProviderContainer();
      addTearDown(container.dispose);
      final dio = container.read(apiClientProvider);
      return dio.interceptors.whereType<TargetLocaleInterceptor>().single;
    }

    test(
      'Positive 1: attaches Accept-Language and X-Target-Locale headers from PlatformDispatcher via apiClientProvider and advances handler',
      () {
        final interceptor = resolveFromApiClient();
        final options = RequestOptions(
          path: '/studio/workflows',
          method: 'GET',
        );

        interceptor.onRequest(options, mockRequestHandler);

        final expectedLanguage =
            PlatformDispatcher.instance.locale.languageCode;
        expect(options.headers['Accept-Language'], equals(expectedLanguage));
        expect(options.headers['X-Target-Locale'], equals(expectedLanguage));
        verify(() => mockRequestHandler.next(options)).called(1);
        verifyNever(() => mockRequestHandler.reject(any(), any()));
      },
    );

    test(
      'Positive 2: dynamically reflects updated active locale across consecutive requests while preserving unrelated headers',
      () {
        Locale currentLocale = const Locale('fi', 'FI');
        final interceptor = TargetLocaleInterceptor(
          localeResolver: () => currentLocale,
        );

        final firstOptions = RequestOptions(
          path: '/execution/run',
          method: 'POST',
          headers: <String, Object?>{'Authorization': 'Bearer token_123'},
        );

        interceptor.onRequest(firstOptions, mockRequestHandler);
        expect(firstOptions.headers['Accept-Language'], equals('fi'));
        expect(firstOptions.headers['X-Target-Locale'], equals('fi'));
        expect(
          firstOptions.headers['Authorization'],
          equals('Bearer token_123'),
        );

        reset(mockRequestHandler);
        currentLocale = const Locale('sv', 'SE');
        final secondOptions = RequestOptions(
          path: '/reports/export',
          method: 'GET',
        );

        interceptor.onRequest(secondOptions, mockRequestHandler);
        expect(secondOptions.headers['Accept-Language'], equals('sv'));
        expect(secondOptions.headers['X-Target-Locale'], equals('sv'));
        verify(() => mockRequestHandler.next(secondOptions)).called(1);
      },
    );

    test(
      'Negative 1 (Stale Header Override Enforcement): overwrites pre-existing or conflicting Accept-Language and X-Target-Locale headers with authoritative locale',
      () {
        final interceptor = TargetLocaleInterceptor(
          localeResolver: () => const Locale('fi', 'FI'),
        );
        final options = RequestOptions(
          path: '/studio/prompt-blocks',
          method: 'PUT',
          headers: <String, Object?>{
            'Accept-Language': 'de-DE,de;q=0.9',
            'X-Target-Locale': 'fr',
            'X-Custom-Trace': 'trc_0195f3a0000070008000000000000001',
          },
        );

        interceptor.onRequest(options, mockRequestHandler);

        expect(options.headers['Accept-Language'], equals('fi'));
        expect(options.headers['X-Target-Locale'], equals('fi'));
        expect(
          options.headers['X-Custom-Trace'],
          equals('trc_0195f3a0000070008000000000000001'),
        );
        verify(() => mockRequestHandler.next(options)).called(1);
      },
    );

    test(
      'Negative 2 (ISTQB Boundary Value Analysis - Undefined/Minimal Locale Subtags): handles 3-char ISO-639-2 and multi-subtag locales deterministically',
      () {
        Locale activeLocale = const Locale('und');
        final interceptor = TargetLocaleInterceptor(
          localeResolver: () => activeLocale,
        );

        // Boundary A: 3-letter ISO 639-2 language code ('und' - undetermined) with no country code
        final undOptions = RequestOptions(path: '/health', method: 'GET');

        interceptor.onRequest(undOptions, mockRequestHandler);
        expect(undOptions.headers['Accept-Language'], equals('und'));
        expect(undOptions.headers['X-Target-Locale'], equals('und'));
        verify(() => mockRequestHandler.next(undOptions)).called(1);

        // Boundary B: Explicit scriptCode + countryCode subtags strips down strictly to primary languageCode
        reset(mockRequestHandler);
        activeLocale = const Locale.fromSubtags(
          languageCode: 'zh',
          scriptCode: 'Hans',
          countryCode: 'CN',
        );
        final subtagOptions = RequestOptions(path: '/health', method: 'GET');

        interceptor.onRequest(subtagOptions, mockRequestHandler);
        expect(subtagOptions.headers['Accept-Language'], equals('zh'));
        expect(subtagOptions.headers['X-Target-Locale'], equals('zh'));
        verify(() => mockRequestHandler.next(subtagOptions)).called(1);
      },
    );
  });
}
