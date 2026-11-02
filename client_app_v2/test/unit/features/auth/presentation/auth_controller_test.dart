import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_user_provider.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _MockFirebaseAuth extends Mock implements firebase.FirebaseAuth {}

class _MockFirebaseUser extends Mock implements firebase.User {}

class _MockUserCredential extends Mock implements firebase.UserCredential {}

class _MockMultiFactor extends Mock implements firebase.MultiFactor {}

class _MockMultiFactorInfo extends Mock implements firebase.MultiFactorInfo {}

class _MockMultiFactorResolver extends Mock
    implements firebase.MultiFactorResolver {}

class _MockFirebaseAuthMultiFactorException extends Mock
    implements firebase.FirebaseAuthMultiFactorException {}

class _MockDio extends Mock implements Dio {}

class _MockLoggerService extends Mock implements LoggerService {}

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
  late _MockFirebaseAuth mockFirebaseAuth;
  late _MockDio mockDio;
  late _MockLoggerService mockLoggerService;
  late _FakeSharedPreferencesAsync fakePrefs;

  final validUserId = generateOpaqueUuid7('usr');
  final orgIdAlpha = generateOpaqueUuid7('org');
  final orgIdBeta = generateOpaqueUuid7('org');

  Map<String, Object?> buildExchangePayload({
    String? userId,
    String? organizationId,
    String accessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.quorum_jwt_01',
    String language = 'en',
    String themeMode = 'dark',
  }) => <String, Object?>{
    'access_token': accessToken,
    'token_type': 'bearer',
    'expires_in_seconds': 900,
    'user': <String, Object?>{
      'id': userId ?? validUserId,
      'firebase_uid': null,
      'email': 'coach@quorum.ai',
      'name': 'Executive Coach',
      'role': 'ADMIN',
      'organization_id': organizationId ?? orgIdAlpha,
      'language': language,
      'theme_mode': themeMode,
      'is_active': true,
      'deleted_at': null,
    },
  };

  setUp(() {
    mockFirebaseAuth = _MockFirebaseAuth();
    mockDio = _MockDio();
    mockLoggerService = _MockLoggerService();
    fakePrefs = _FakeSharedPreferencesAsync();

    when(
      () => mockFirebaseAuth.authStateChanges(),
    ).thenAnswer((_) => Stream<firebase.User?>.value(null));
    when(() => mockFirebaseAuth.currentUser).thenReturn(null);
    when(() => mockFirebaseAuth.signOut()).thenAnswer((_) async {});
  });

  ProviderContainer createContainer({
    AuthRepository? customAuthRepository,
    UserRepository? customUserRepository,
  }) {
    final container = ProviderContainer(
      retry: (retryCount, error) => null,
      overrides: [
        firebaseAuthInstanceProvider.overrideWithValue(mockFirebaseAuth),
        apiClientProvider.overrideWithValue(mockDio),
        loggerServiceProvider.overrideWithValue(mockLoggerService),
        settingsControllerProvider.overrideWith(
          () => SettingsController(prefs: fakePrefs),
        ),
        if (customAuthRepository != null)
          authRepositoryProvider.overrideWithValue(customAuthRepository),
        if (customUserRepository != null)
          userRepositoryProvider.overrideWithValue(customUserRepository),
      ],
    );
    addTearDown(container.dispose);
    return container;
  }

  group('AuthController & MfaSessionController Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: build() hydrates from mockUser or Firebase currentUser via UserRepository, and signIn exchanges credentials, syncs settings, and schedules silent refresh',
      () async {
        // 1. Hydrate build() when Firebase user is active and /iam/auth/me returns User
        final mockFbUser = _MockFirebaseUser();
        when(
          () => mockFirebaseAuth.authStateChanges(),
        ).thenAnswer((_) => Stream<firebase.User?>.value(mockFbUser));
        when(
          () => mockDio.get<Map<String, Object?>>('/iam/auth/me'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/me'),
            statusCode: 200,
            data:
                buildExchangePayload(organizationId: orgIdAlpha)['user']
                    as Map<String, Object?>,
          ),
        );

        final container = createContainer();
        await container.read(settingsControllerProvider.future);

        final initialUser = await container.read(authControllerProvider.future);
        expect(initialUser, isNotNull);
        expect(initialUser!.id, equals(validUserId));
        expect(initialUser.organizationId, equals(orgIdAlpha));

        // 2. Full signIn with enrolled factor -> exchanges token, syncs settings, starts timer
        final mockCredential = _MockUserCredential();
        final mockMultiFactor = _MockMultiFactor();
        final mockFactorInfo = _MockMultiFactorInfo();

        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'coach@quorum.ai',
            password: 'ValidPassword123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(() => mockCredential.user).thenReturn(mockFbUser);
        when(() => mockFbUser.multiFactor).thenReturn(mockMultiFactor);
        when(
          () => mockMultiFactor.getEnrolledFactors(),
        ).thenAnswer((_) async => <firebase.MultiFactorInfo>[mockFactorInfo]);
        when(
          () => mockFbUser.getIdToken(any()),
        ).thenAnswer((_) async => 'firebase_id_token_xyz');

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            statusCode: 200,
            data: buildExchangePayload(
              organizationId: orgIdAlpha,
              language: 'en',
              themeMode: 'dark',
            ),
          ),
        );

        final notifier = container.read(authControllerProvider.notifier);
        await notifier.signIn('coach@quorum.ai', 'ValidPassword123!');

        expect(
          container.read(mockTokenProvider),
          equals('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.quorum_jwt_01'),
        );
        expect(container.read(mockUserProvider)?.id, equals(validUserId));
        expect(notifier.hasActiveRefreshTimer, isTrue);

        final syncedSettings = container.read(settingsControllerProvider).value;
        expect(syncedSettings?.locale, equals(const Locale('en')));
        expect(syncedSettings?.themeMode, equals(ThemeMode.dark));
      },
    );

    test(
      'Positive 2: tenant data isolation invalidates masterDataProvider on organization switch across performSilentRefresh, setOptimisticUser, applyTokenExchangeResponse, and signOut',
      () async {
        final container = createContainer();
        await container.read(settingsControllerProvider.future);

        int masterDataBuildCount = 0;
        container.listen<AsyncValue<void>>(masterDataProvider, (_, next) {
          if (next is AsyncData<void> && !next.isLoading) {
            masterDataBuildCount++;
          }
        }, fireImmediately: true);
        await container.read(masterDataProvider.future);
        expect(masterDataBuildCount, equals(1));

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            statusCode: 200,
            data: buildExchangePayload(
              organizationId: orgIdAlpha,
              accessToken: 'jwt_org_alpha',
            ),
          ),
        );

        final notifier = container.read(authControllerProvider.notifier);
        await notifier.debugMockLogin(validUserId);
        expect(
          container.read(authControllerProvider).value?.organizationId,
          equals(orgIdAlpha),
        );

        // Silent refresh switching organization from orgIdAlpha -> orgIdBeta invalidates masterDataProvider
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            statusCode: 200,
            data: buildExchangePayload(
              organizationId: orgIdBeta,
              accessToken: 'jwt_org_beta',
            ),
          ),
        );

        await notifier.performSilentRefresh();
        await container.read(masterDataProvider.future);
        expect(masterDataBuildCount, equals(2));
        expect(container.read(mockTokenProvider), equals('jwt_org_beta'));
        expect(
          container.read(authControllerProvider).value?.organizationId,
          equals(orgIdBeta),
        );

        // Optimistic user update switching back to orgIdAlpha invalidates masterDataProvider
        final currentUser = container.read(authControllerProvider).value!;
        notifier.setOptimisticUser(
          currentUser.copyWith(organizationId: orgIdAlpha),
        );
        await container.read(masterDataProvider.future);
        expect(masterDataBuildCount, equals(3));

        // applyTokenExchangeResponse switching to orgIdBeta invalidates masterDataProvider
        final dtoBeta = TokenExchangeResponseDto.fromJson(
          buildExchangePayload(
            organizationId: orgIdBeta,
            accessToken: 'jwt_direct_apply',
          ),
        );
        await notifier.applyTokenExchangeResponse(dtoBeta);
        await container.read(masterDataProvider.future);
        expect(masterDataBuildCount, equals(4));

        // 5-Step signOut revokes server session, clears tokens/user/MFA, and invalidates masterDataProvider
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/logout'),
            statusCode: 200,
            data: const <String, Object?>{
              'status': 'logged_out',
              'revoked_jti': 'jti_0195f3a0000070008000000000000001',
              'all_sessions_revoked': true,
            },
          ),
        );

        await notifier.signOut(revokeAllSessions: true);
        await container.read(masterDataProvider.future);
        expect(masterDataBuildCount, equals(5));
        expect(notifier.hasActiveRefreshTimer, isFalse);
        expect(container.read(mockTokenProvider), isNull);
        expect(container.read(mockUserProvider), isNull);
        expect(container.read(authControllerProvider).value, isNull);
      },
    );

    test(
      'Negative 1 (MFA Challenge & Enrollment Interception): signIn intercepts MFA_CHALLENGE_REQUIRED and MFA_REQUIRED without authenticating until second factor succeeds or is cancelled',
      () async {
        final container = createContainer();
        await container.read(settingsControllerProvider.future);

        final mockResolver = _MockMultiFactorResolver();
        final mockHint = _MockMultiFactorInfo();
        when(() => mockHint.uid).thenReturn('factor_uid_01');
        when(
          () => mockResolver.hints,
        ).thenReturn(<firebase.MultiFactorInfo>[mockHint]);

        final mockMfaException = _MockFirebaseAuthMultiFactorException();
        when(() => mockMfaException.resolver).thenReturn(mockResolver);

        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'challenge@quorum.ai',
            password: 'Password123!',
          ),
        ).thenThrow(mockMfaException);

        final notifier = container.read(authControllerProvider.notifier);

        // Should NOT throw on MFA_CHALLENGE_REQUIRED; keeps state AsyncData(null) and populates MfaSessionController
        await notifier.signIn('challenge@quorum.ai', 'Password123!');
        expect(container.read(authControllerProvider).value, isNull);
        expect(container.read(authControllerProvider).hasError, isFalse);

        final pendingMfa = container.read(mfaSessionControllerProvider);
        expect(pendingMfa.isChallenge, isTrue);
        expect(pendingMfa.email, equals('challenge@quorum.ai'));
        expect(pendingMfa.enrollmentId, equals('factor_uid_01'));

        // Cancelling MFA flow clears repository and controller state
        await notifier.cancelMfaFlow();
        expect(
          container.read(mfaSessionControllerProvider).type,
          equals(MfaRequirementType.none),
        );
        expect(container.read(authRepositoryProvider).pendingMfaState, isNull);
        expect(container.read(authControllerProvider).value, isNull);
      },
    );

    test(
      'Negative 2 (ISTQB BVA & Error Propagation): rejects invalid TOTP lengths (5 digits min-1, 7 digits max+1), surfaces non-MFA signIn / debugMockLogin errors, and degrades gracefully on signOut / performSilentRefresh failures',
      () async {
        final container = createContainer();
        await container.read(settingsControllerProvider.future);
        final notifier = container.read(authControllerProvider.notifier);

        // 1. Non-MFA signIn failure sets AsyncError and rethrows AppException
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'bad@quorum.ai',
            password: 'wrong',
          ),
        ).thenThrow(firebase.FirebaseAuthException(code: 'invalid-credential'));

        await expectLater(
          notifier.signIn('bad@quorum.ai', 'wrong'),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('AUTHENTICATION_FAILED'),
            ),
          ),
        );
        expect(container.read(authControllerProvider).hasError, isTrue);

        // 2. ISTQB BVA on verifyMfaChallenge and completeMfaEnrollment: 0 chars, 5 chars (min-1), 7 chars (max+1)
        for (final invalidCode in ['', '12345', '1234567']) {
          await expectLater(
            notifier.verifyMfaChallenge(invalidCode),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
          await expectLater(
            notifier.completeMfaEnrollment(invalidCode),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
        }

        // 3. ISTQB BVA on debugMockLogin with empty/whitespace ID -> sets AsyncError and throws VALIDATION_FAILED
        await expectLater(
          notifier.debugMockLogin('   '),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
        expect(container.read(authControllerProvider).hasError, isTrue);

        // 4. performSilentRefresh logs warning when unauthenticated without crashing state
        await notifier.performSilentRefresh();
        verify(
          () => mockLoggerService.warning(
            'AuthController',
            any(that: contains('Silent token refresh failed')),
          ),
        ).called(1);

        // 5. signOut handles unexpected non-DioException on revokeServerSession and Firebase signOut failure gracefully
        container.read(mockTokenProvider.notifier).setToken('active_jwt');
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: any(named: 'data'),
          ),
        ).thenThrow(StateError('Unexpected transport failure'));
        when(
          () => mockFirebaseAuth.signOut(),
        ).thenThrow(Exception('Firebase local cache locked'));

        await notifier.signOut();
        verify(
          () => mockLoggerService.warning(
            'AuthController',
            any(that: contains('Unexpected error during server logout')),
          ),
        ).called(1);
        verify(
          () => mockLoggerService.warning(
            'AuthController',
            any(that: contains('Firebase signOut warning')),
          ),
        ).called(1);
        expect(container.read(mockTokenProvider), isNull);
        expect(container.read(authControllerProvider).value, isNull);

        // 6. UserRepository.fetchCurrentUser translates Dio 401/404 responses on /iam/auth/me to Left(AppException)
        final userRepo = container.read(userRepositoryProvider);
        when(() => mockDio.get<Map<String, Object?>>('/iam/auth/me')).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/me'),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(path: '/iam/auth/me'),
              statusCode: 401,
            ),
            type: DioExceptionType.badResponse,
          ),
        );
        final unauthorizedResult = await userRepo.fetchCurrentUser();
        expect(unauthorizedResult.isLeft(), isTrue);

        when(() => mockDio.get<Map<String, Object?>>('/iam/auth/me')).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/me'),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(path: '/iam/auth/me'),
              statusCode: 404,
            ),
            type: DioExceptionType.badResponse,
          ),
        );
        final notFoundResult = await userRepo.fetchCurrentUser();
        expect(notFoundResult.isLeft(), isTrue);
      },
    );
  });
}
