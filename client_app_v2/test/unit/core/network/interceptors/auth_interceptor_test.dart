import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/network/interceptors/auth_interceptor.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockFirebaseAuth extends Mock implements FirebaseAuth {}

class _MockUser extends Mock implements User {}

class _MockLoggerService extends Mock implements LoggerService {}

class _MockRequestInterceptorHandler extends Mock
    implements RequestInterceptorHandler {}

void main() {
  setUpAll(() {
    registerFallbackValue(RequestOptions(path: '/test'));
    registerFallbackValue(
      DioException(requestOptions: RequestOptions(path: '/test')),
    );
    registerFallbackValue(StackTrace.empty);
  });

  group('AuthInterceptor Unit & ISTQB Boundary Tests', () {
    late _MockFirebaseAuth mockFirebaseAuth;
    late _MockUser mockUser;
    late _MockLoggerService mockLoggerService;
    late _MockRequestInterceptorHandler mockHandler;

    setUp(() {
      dotenv.loadFromString(
        envString: 'API_URL=https://api.quorum.test\nENVIRONMENT=production',
      );
      mockFirebaseAuth = _MockFirebaseAuth();
      mockUser = _MockUser();
      mockLoggerService = _MockLoggerService();
      mockHandler = _MockRequestInterceptorHandler();
    });

    tearDown(() {
      dotenv.clean();
    });

    ProviderContainer createContainer() {
      final container = ProviderContainer(
        overrides: [
          firebaseAuthInstanceProvider.overrideWithValue(mockFirebaseAuth),
          loggerServiceProvider.overrideWithValue(mockLoggerService),
        ],
      );
      addTearDown(container.dispose);
      return container;
    }

    AuthInterceptor resolveInterceptor(ProviderContainer container) {
      final dio = container.read(apiClientProvider);
      return dio.interceptors.whereType<AuthInterceptor>().single;
    }

    test(
      'Positive 1: attaches Firebase Bearer token and advances handler when currentUser is authenticated',
      () async {
        when(() => mockFirebaseAuth.currentUser).thenReturn(mockUser);
        when(
          () => mockUser.getIdToken(),
        ).thenAnswer((_) async => 'firebase_jwt_token_123');

        final container = createContainer();
        final interceptor = resolveInterceptor(container);
        final options = RequestOptions(path: '/workflows');

        await interceptor.onRequest(options, mockHandler);

        expect(
          options.headers['Authorization'],
          equals('Bearer firebase_jwt_token_123'),
        );
        verify(() => mockHandler.next(options)).called(1);
        verifyNever(() => mockHandler.reject(any(), any()));
      },
    );

    test(
      'Positive 2: falls back to mockTokenProvider when Firebase currentUser is null',
      () async {
        when(() => mockFirebaseAuth.currentUser).thenReturn(null);

        final container = createContainer();
        container
            .read(mockTokenProvider.notifier)
            .setToken('dev_mock_token_456');
        final interceptor = resolveInterceptor(container);
        final options = RequestOptions(path: '/workflows');

        await interceptor.onRequest(options, mockHandler);

        expect(
          options.headers['Authorization'],
          equals('Bearer dev_mock_token_456'),
        );
        verify(() => mockHandler.next(options)).called(1);
        verifyNever(() => mockHandler.reject(any(), any()));
      },
    );

    test(
      'Negative 1 (Fail-Fast Token Refresh Failure): logs RFC 7807 error and rejects request when getIdToken throws',
      () async {
        final authError = Exception('Firebase network unreachable');
        when(() => mockFirebaseAuth.currentUser).thenReturn(mockUser);
        when(() => mockUser.getIdToken()).thenThrow(authError);

        final container = createContainer();
        final interceptor = resolveInterceptor(container);
        final options = RequestOptions(path: '/workflows');

        await interceptor.onRequest(options, mockHandler);

        expect(options.headers.containsKey('Authorization'), isFalse);
        verify(
          () => mockLoggerService.error(
            'AUTH',
            'Firebase token refresh failed',
            authError,
            any(),
          ),
        ).called(1);

        final captured = verify(
          () => mockHandler.reject(captureAny(), true),
        ).captured;
        expect(captured, hasLength(1));
        final dioError = captured.single as DioException;
        expect(dioError.type, equals(DioExceptionType.cancel));
        expect(dioError.error, isA<AppException>());
        final appException = dioError.error as AppException;
        expect(appException.errorCode, equals('UNKNOWN_ERROR'));
        expect(
          appException.detail,
          contains('Local authentication failed: Exception: Firebase network'),
        );
        verifyNever(() => mockHandler.next(any()));
      },
    );

    test(
      'Negative 2 (Boundary Value Analysis - Null/Empty Tokens): rejects null or empty Firebase token and omits blank mockToken',
      () async {
        when(() => mockFirebaseAuth.currentUser).thenReturn(mockUser);
        when(() => mockUser.getIdToken()).thenAnswer((_) async => '   ');

        final container = createContainer();
        final interceptor = resolveInterceptor(container);
        final options = RequestOptions(path: '/workflows');

        await interceptor.onRequest(options, mockHandler);

        expect(options.headers.containsKey('Authorization'), isFalse);
        verify(
          () => mockLoggerService.error(
            'AUTH',
            'Firebase token refresh failed',
            any(that: isA<StateError>()),
            any(),
          ),
        ).called(1);
        verify(() => mockHandler.reject(any(), true)).called(1);
        verifyNever(() => mockHandler.next(any()));

        // Boundary sub-case: currentUser is null and mockToken is whitespace-only
        reset(mockHandler);
        when(() => mockFirebaseAuth.currentUser).thenReturn(null);
        container.read(mockTokenProvider.notifier).setToken('   ');
        final unauthOptions = RequestOptions(path: '/public');

        await interceptor.onRequest(unauthOptions, mockHandler);

        expect(unauthOptions.headers.containsKey('Authorization'), isFalse);
        verify(() => mockHandler.next(unauthOptions)).called(1);
        verifyNever(() => mockHandler.reject(any(), any()));
      },
    );
  });
}
