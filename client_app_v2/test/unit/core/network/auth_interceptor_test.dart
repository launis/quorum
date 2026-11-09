import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/network/interceptors/auth_interceptor.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_user_provider.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:client_app/router/router.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _MockFirebaseAuth extends Mock implements firebase.FirebaseAuth {}

class _MockFirebaseUser extends Mock implements firebase.User {}

class _MockUserCredential extends Mock implements firebase.UserCredential {}

class _MockDio extends Mock implements Dio {}

class _MockLoggerService extends Mock implements LoggerService {}

class _MockRequestInterceptorHandler extends Mock
    implements RequestInterceptorHandler {}

class _FakeSharedPreferencesAsync implements SharedPreferencesAsync {
  final Map<String, String> store = <String, String>{};

  @override
  Future<String?> getString(String key) async => store[key];

  @override
  Future<void> setString(String key, String value) async {
    store[key] = value;
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  setUpAll(() {
    registerFallbackValue(RequestOptions(path: '/test'));
  });

  group('Phase 6 Step 6.1: AuthInterceptor, Token Exchange & 5-Step Logout', () {
    late _MockFirebaseAuth mockFirebaseAuth;
    late _MockDio mockDio;
    late _MockLoggerService mockLoggerService;
    late _MockRequestInterceptorHandler mockHandler;
    late _FakeSharedPreferencesAsync fakePrefs;

    const testUserId = 'usr_0195f3a00000700a83fd6b3d77c748f4';
    const testOrgId = 'org_0195f3a0000070008000000000000001';

    final exchangeResponsePayload = <String, Object?>{
      'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.local_jwt_15min',
      'token_type': 'bearer',
      'expires_in_seconds': 900,
      'user': <String, Object?>{
        'id': testUserId,
        'email': 'admin@quorum.ai',
        'name': 'Root Admin',
        'role': 'ADMIN',
        'organization_id': testOrgId,
        'language': 'en',
        'theme_mode': 'dark',
        'is_active': true,
      },
    };

    setUp(() {
      dotenv.loadFromString(
        envString: 'API_URL=https://api.quorum.test\nENVIRONMENT=development',
      );
      mockFirebaseAuth = _MockFirebaseAuth();
      mockDio = _MockDio();
      mockLoggerService = _MockLoggerService();
      mockHandler = _MockRequestInterceptorHandler();
      fakePrefs = _FakeSharedPreferencesAsync();

      when(
        () => mockFirebaseAuth.authStateChanges(),
      ).thenAnswer((_) => Stream<firebase.User?>.value(null));
      when(() => mockFirebaseAuth.currentUser).thenReturn(null);
      when(() => mockFirebaseAuth.signOut()).thenAnswer((_) async {});
      when(() => mockDio.interceptors).thenReturn(Interceptors());
    });

    tearDown(() {
      dotenv.clean();
    });

    ProviderContainer createContainer() {
      final container = ProviderContainer(
        overrides: [
          firebaseAuthInstanceProvider.overrideWithValue(mockFirebaseAuth),
          apiClientProvider.overrideWithValue(mockDio),
          loggerServiceProvider.overrideWithValue(mockLoggerService),
          settingsControllerProvider.overrideWith(
            () => SettingsController(prefs: fakePrefs),
          ),
        ],
      );
      addTearDown(container.dispose);
      return container;
    }

    test(
      'test_auth_interceptor_token_exchange_and_5_step_logout_positive',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            statusCode: 200,
            data: exchangeResponsePayload,
          ),
        );

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/logout'),
            statusCode: 200,
            data: <String, Object?>{
              'status': 'revoked',
              'revoked_jti': 'jti_0195f3a0000070008000000000000099',
              'all_sessions_revoked': true,
            },
          ),
        );

        final mockFbUser = _MockFirebaseUser();
        final mockCredential = _MockUserCredential();
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'admin@quorum.ai',
            password: 'SecretPassword123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(() => mockCredential.user).thenReturn(mockFbUser);
        when(
          () => mockFbUser.getIdToken(any()),
        ).thenAnswer((_) async => 'firebase_id_token_01');

        final container = createContainer();
        await container.read(settingsControllerProvider.future);
        final authNotifier = container.read(authControllerProvider.notifier);

        // 1. Exchange Firebase ID token via POST /iam/auth/exchange
        await authNotifier.signIn('admin@quorum.ai', 'SecretPassword123!');

        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: const TokenExchangeRequestDto(
              firebaseToken: 'firebase_id_token_01',
            ).toJson(),
          ),
        ).called(1);

        final cachedJwt = container.read(mockTokenProvider);
        expect(
          cachedJwt,
          equals('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.local_jwt_15min'),
        );
        expect(authNotifier.hasActiveRefreshTimer, isTrue);

        // Verify SettingsController synced user.language ('en') and user.themeMode ('dark')
        final settingsState = container.read(settingsControllerProvider).value;
        expect(settingsState?.locale, equals(const Locale('en')));
        expect(settingsState?.themeMode, equals(ThemeMode.dark));

        // 2. Verify AuthInterceptor attaches cached Quorum Local JWT (never raw mock-token:)
        late AuthInterceptor interceptor;
        final interceptorProvider = Provider<AuthInterceptor>(
          (ref) => AuthInterceptor(ref),
        );
        interceptor = container.read(interceptorProvider);
        final protectedOptions = RequestOptions(path: '/studio/workflows');
        await interceptor.onRequest(protectedOptions, mockHandler);

        expect(
          protectedOptions.headers['Authorization'],
          equals('Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.local_jwt_15min'),
        );
        verify(() => mockHandler.next(protectedOptions)).called(1);

        // 3. Execute 5-Step Logout Pipeline with revokeAllSessions: true
        await authNotifier.signOut(revokeAllSessions: true);

        expect(authNotifier.hasActiveRefreshTimer, isFalse);
        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: const LogoutRequestDto(revokeAllSessions: true).toJson(),
          ),
        ).called(1);
        verify(() => mockFirebaseAuth.signOut()).called(1);

        expect(container.read(mockTokenProvider), isNull);
        expect(container.read(mockUserProvider), isNull);

        final postLogoutAuthState = container.read(authControllerProvider);
        expect(postLogoutAuthState.value, isNull);
        expect(
          resolveAuthRedirect(
            authState: postLogoutAuthState,
            location: '/dashboard',
          ),
          equals('/login'),
        );
      },
    );

    test(
      'test_auth_controller_sign_out_offline_graceful_degradation_error_path',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            statusCode: 200,
            data: exchangeResponsePayload,
          ),
        );

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/logout'),
            type: DioExceptionType.connectionError,
            message: 'Offline or token already expired',
          ),
        );

        final mockFbUser = _MockFirebaseUser();
        final mockCredential = _MockUserCredential();
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'admin@quorum.ai',
            password: 'SecretPassword123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(() => mockCredential.user).thenReturn(mockFbUser);
        when(
          () => mockFbUser.getIdToken(any()),
        ).thenAnswer((_) async => 'firebase_id_token_02');

        final container = createContainer();
        final authNotifier = container.read(authControllerProvider.notifier);

        await authNotifier.signIn('admin@quorum.ai', 'SecretPassword123!');
        expect(container.read(mockTokenProvider), isNotNull);
        expect(authNotifier.hasActiveRefreshTimer, isTrue);

        // Sign out while offline / server unreachable -> must degrade gracefully inside finally
        await authNotifier.signOut(revokeAllSessions: false);

        expect(authNotifier.hasActiveRefreshTimer, isFalse);
        verify(
          () => mockLoggerService.warning(
            'AuthController',
            any(that: contains('Server logout request failed')),
          ),
        ).called(1);
        verify(() => mockFirebaseAuth.signOut()).called(1);
        expect(container.read(mockTokenProvider), isNull);
        expect(container.read(mockUserProvider), isNull);
        expect(container.read(authControllerProvider).value, isNull);
        expect(
          resolveAuthRedirect(
            authState: container.read(authControllerProvider),
            location: '/admin',
          ),
          equals('/login'),
        );
      },
    );

    test(
      'Negative & Boundary (ISTQB BVA): rejects empty Firebase ID token and validates 6-digit TOTP code boundaries (5, 6, 7 chars)',
      () async {
        final container = createContainer();
        final repo = container.read(authRepositoryProvider);

        final emptyResult = await repo.exchangeToken('   ');
        expect(emptyResult.isLeft(), isTrue);
        emptyResult.fold(
          (err) => expect(err.errorCode, equals('AUTHENTICATION_FAILED')),
          (_) => fail('Expected Left(AppException.unauthorized)'),
        );

        // Boundary 5 chars (min - 1) and 7 chars (max + 1) on TOTP verification
        final shortChallenge = await repo.resolveMfaChallenge('12345');
        expect(shortChallenge.isLeft(), isTrue);
        shortChallenge.fold(
          (err) => expect(err.errorCode, equals('VALIDATION_FAILED')),
          (_) => fail('Expected validation error for 5-digit TOTP'),
        );

        final longEnrollment = await repo.completeTotpEnrollment('1234567');
        expect(longEnrollment.isLeft(), isTrue);
        longEnrollment.fold(
          (err) => expect(err.errorCode, equals('VALIDATION_FAILED')),
          (_) => fail('Expected validation error for 7-digit TOTP'),
        );

        // 6 chars without active pending MFA state -> unauthorized (401)
        final uninitializedChallenge = await repo.resolveMfaChallenge('123456');
        expect(uninitializedChallenge.isLeft(), isTrue);
        uninitializedChallenge.fold(
          (err) => expect(err.errorCode, equals('AUTHENTICATION_FAILED')),
          (_) => fail('Expected unauthorized when no pending MFA state'),
        );
      },
    );
  });
}
