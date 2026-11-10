import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockFirebaseAuth extends Mock implements firebase.FirebaseAuth {}

class MockUserCredential extends Mock implements firebase.UserCredential {}

class MockFirebaseUser extends Mock implements firebase.User {}

class MockMultiFactor extends Mock implements firebase.MultiFactor {}

class MockMultiFactorInfo extends Mock implements firebase.MultiFactorInfo {}

class MockMultiFactorResolver extends Mock
    implements firebase.MultiFactorResolver {}

class MockFirebaseAuthMultiFactorException extends Mock
    implements firebase.FirebaseAuthMultiFactorException {}

class MockMultiFactorSession extends Mock
    implements firebase.MultiFactorSession {}

class MockMultiFactorAssertion extends Mock
    implements firebase.MultiFactorAssertion {}

class MockTotpSecret extends Mock implements firebase.TotpSecret {}

void main() {
  late MockDio mockDio;
  late MockFirebaseAuth mockFirebaseAuth;
  late AuthRepository repository;

  final validUserId = generateOpaqueUuid7('usr');
  final validOrgId = generateOpaqueUuid7('org');

  Map<String, Object?> buildExchangePayload({String? userId}) =>
      <String, Object?>{
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.quorum_jwt',
        'token_type': 'bearer',
        'expires_in_seconds': 900,
        'user': <String, Object?>{
          'id': userId ?? validUserId,
          'email': 'coach@quorum.ai',
          'role': 'ADMIN',
          'organization_id': validOrgId,
          'is_active': true,
        },
      };

  setUp(() {
    mockDio = MockDio();
    mockFirebaseAuth = MockFirebaseAuth();
    repository = AuthRepository(mockFirebaseAuth, mockDio);
  });

  group('AuthRepository Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: exchangeToken and revokeServerSession execute strict DTO roundtrips',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            data: buildExchangePayload(),
            statusCode: 200,
          ),
        );

        final tokenResult = await repository.exchangeToken('  fb_id_token  ');
        expect(tokenResult.isRight(), isTrue);
        final dto = tokenResult.getRight().toNullable()!;
        expect(dto.user.id, equals(validUserId));
        expect(dto.user.role, equals(UserRole.admin));
        expect(dto.expiresInSeconds, equals(900));

        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: <String, Object?>{'firebase_token': 'fb_id_token'},
          ),
        ).called(1);

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/logout'),
            data: const <String, Object?>{
              'status': 'revoked',
              'revoked_jti': 'jti_0195f3a0000070008000000000000001',
              'all_sessions_revoked': true,
            },
            statusCode: 200,
          ),
        );

        final logoutDto = await repository.revokeServerSession(
          revokeAllSessions: true,
        );
        expect(logoutDto.status, equals('revoked'));
        expect(logoutDto.allSessionsRevoked, isTrue);
        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: const <String, Object?>{'revoke_all_sessions': true},
          ),
        ).called(1);
      },
    );

    test(
      'test_sign_in_with_email_and_password_succeeds_when_backend_require_mfa_false',
      () async {
        final mockCredential = MockUserCredential();
        final mockUser = MockFirebaseUser();
        final mockMultiFactor = MockMultiFactor();

        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'coach@quorum.ai',
            password: 'SecretPassword123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(() => mockCredential.user).thenReturn(mockUser);
        when(() => mockUser.multiFactor).thenReturn(mockMultiFactor);
        when(
          () => mockUser.getIdToken(any()),
        ).thenAnswer((_) async => 'fresh_firebase_jwt');

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            data: buildExchangePayload(),
            statusCode: 200,
          ),
        );

        final signInResult = await repository.signInWithEmailAndPassword(
          'coach@quorum.ai',
          'SecretPassword123!',
        );
        expect(signInResult.isRight(), isTrue);
        expect(repository.pendingMfaState, isNull);
        verifyNever(() => mockMultiFactor.getEnrolledFactors());
        verifyNever(() => mockMultiFactor.getSession());

        // Refresh session via active Firebase user
        when(() => mockFirebaseAuth.currentUser).thenReturn(mockUser);
        final refreshResult = await repository.refreshSession();
        expect(refreshResult.isRight(), isTrue);

        // Auth state stream & signOut clear pending MFA state
        when(
          () => mockFirebaseAuth.authStateChanges(),
        ).thenAnswer((_) => Stream<firebase.User?>.value(mockUser));
        expect(await repository.authStateChanges().first, equals(mockUser));

        repository.setPendingMfaState(
          const MfaPendingState(
            type: MfaRequirementType.challenge,
            email: 'coach@quorum.ai',
          ),
        );
        expect(repository.pendingMfaState?.isChallenge, isTrue);
        expect(repository.pendingMfaState?.isEnrollment, isFalse);

        when(() => mockFirebaseAuth.signOut()).thenAnswer((_) async {});
        await repository.signOut();
        expect(repository.pendingMfaState, isNull);
        verify(() => mockFirebaseAuth.signOut()).called(1);
      },
    );

    test(
      'test_sign_in_with_email_and_password_prepares_totp_enrollment_on_backend_mfa_required',
      () async {
        final mockCredential = MockUserCredential();
        final mockUser = MockFirebaseUser();
        final mockMultiFactor = MockMultiFactor();

        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'newuser@quorum.ai',
            password: 'Password123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(() => mockCredential.user).thenReturn(mockUser);
        when(() => mockUser.email).thenReturn('newuser@quorum.ai');
        when(() => mockUser.multiFactor).thenReturn(mockMultiFactor);
        when(
          () => mockUser.getIdToken(any()),
        ).thenAnswer((_) async => 'single_factor_firebase_jwt');
        when(
          () => mockMultiFactor.getSession(),
        ).thenThrow(Exception('Platform TOTP session fallback'));

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(path: '/iam/auth/exchange'),
              statusCode: 403,
              data: const <String, Object?>{
                'error_code': 'MFA_REQUIRED',
                'title': 'MFA Enrollment Required',
                'detail': 'Mandatory TOTP 2FA enrollment is required.',
              },
            ),
          ),
        );

        final enrollResult = await repository.signInWithEmailAndPassword(
          'newuser@quorum.ai',
          'Password123!',
        );
        expect(enrollResult.isLeft(), isTrue);
        final enrollError = enrollResult.getLeft().toNullable()!;
        expect(enrollError.status, equals(403));
        expect(enrollError.errorCode, equals('MFA_REQUIRED'));
        expect(repository.pendingMfaState, isNotNull);
        expect(repository.pendingMfaState!.isEnrollment, isTrue);
        expect(repository.pendingMfaState!.email, equals('newuser@quorum.ai'));
        expect(
          repository.pendingMfaState!.secretKey,
          equals('QUORUM-TOTP-SETUP'),
        );

        repository.clearPendingMfaState();
        expect(repository.pendingMfaState, isNull);

        // Second-factor challenge flow via FirebaseAuthMultiFactorException
        final mockResolver = MockMultiFactorResolver();
        final mockHint = MockMultiFactorInfo();
        when(() => mockHint.uid).thenReturn('factor_uid_01');
        when(
          () => mockResolver.hints,
        ).thenReturn(<firebase.MultiFactorInfo>[mockHint]);

        final mockMfaException = MockFirebaseAuthMultiFactorException();
        when(() => mockMfaException.resolver).thenReturn(mockResolver);

        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'enrolled@quorum.ai',
            password: 'Password123!',
          ),
        ).thenThrow(mockMfaException);

        final challengeResult = await repository.signInWithEmailAndPassword(
          'enrolled@quorum.ai',
          'Password123!',
        );
        expect(challengeResult.isLeft(), isTrue);
        final challengeError = challengeResult.getLeft().toNullable()!;
        expect(challengeError.status, equals(403));
        expect(challengeError.errorCode, equals('MFA_CHALLENGE_REQUIRED'));
        expect(repository.pendingMfaState?.isChallenge, isTrue);
        expect(
          repository.pendingMfaState?.enrollmentId,
          equals('factor_uid_01'),
        );
      },
    );

    test(
      'Negative 1 (ISTQB BVA): rejects empty tokens and non-6-digit TOTP codes (5 digits min-1, 7 digits max+1)',
      () async {
        // Empty and whitespace firebaseIdToken
        for (final invalidToken in ['', '   ']) {
          final res = await repository.exchangeToken(invalidToken);
          expect(res.isLeft(), isTrue);
          expect(
            res.getLeft().toNullable()!.errorCode,
            equals('AUTHENTICATION_FAILED'),
          );
        }

        // BVA on TOTP 6-digit code length: 0 chars, 5 chars (min-1), 7 chars (max+1)
        for (final invalidTotp in ['', '12345', '1234567', '  12345  ']) {
          final challengeRes = await repository.resolveMfaChallenge(
            invalidTotp,
          );
          expect(challengeRes.isLeft(), isTrue);
          expect(
            challengeRes.getLeft().toNullable()!.errorCode,
            equals('VALIDATION_FAILED'),
          );

          final enrollRes = await repository.completeTotpEnrollment(
            invalidTotp,
          );
          expect(enrollRes.isLeft(), isTrue);
          expect(
            enrollRes.getLeft().toNullable()!.errorCode,
            equals('VALIDATION_FAILED'),
          );
        }

        // Valid 6-digit TOTP when no pending MFA state exists -> unauthorized
        final noPendingChallenge = await repository.resolveMfaChallenge(
          '123456',
        );
        expect(noPendingChallenge.isLeft(), isTrue);
        expect(
          noPendingChallenge.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        final noPendingEnroll = await repository.completeTotpEnrollment(
          '123456',
        );
        expect(noPendingEnroll.isLeft(), isTrue);
        expect(
          noPendingEnroll.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        verifyNever(
          () => mockDio.post<Map<String, Object?>>(
            any(),
            data: any(named: 'data'),
          ),
        );
      },
    );

    test(
      'Negative 2: maps DioException (RFC 7807, MFA_REQUIRED, 404, 401/403), FirebaseAuthException, null payloads, and schema violations',
      () async {
        // 1. Null FirebaseAuth instance fallback
        final nullAuthRepo = AuthRepository(null, mockDio);
        expect(await nullAuthRepo.authStateChanges().first, isNull);
        final nullSignIn = await nullAuthRepo.signInWithEmailAndPassword(
          'a@b.com',
          'pw',
        );
        expect(nullSignIn.isLeft(), isTrue);
        expect(
          nullSignIn.getLeft().toNullable()!.errorCode,
          equals('UNKNOWN_ERROR'),
        );

        final nullRefresh = await nullAuthRepo.refreshSession();
        expect(nullRefresh.isLeft(), isTrue);
        expect(
          nullRefresh.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        // 2. FirebaseAuthException credential errors -> 401 AUTHENTICATION_FAILED
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: any(named: 'email'),
            password: any(named: 'password'),
          ),
        ).thenThrow(firebase.FirebaseAuthException(code: 'invalid-credential'));

        final badCreds = await repository.signInWithEmailAndPassword(
          'coach@quorum.ai',
          'wrong',
        );
        expect(badCreds.isLeft(), isTrue);
        expect(
          badCreds.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        // 3. DioException with MFA_REQUIRED prepares enrollment state
        when(() => mockFirebaseAuth.currentUser).thenReturn(null);
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(path: '/iam/auth/exchange'),
              statusCode: 403,
              data: const <String, Object?>{
                'error_code': 'MFA_REQUIRED',
                'title': '2FA Required',
                'detail': 'Enroll TOTP first.',
              },
            ),
          ),
        );

        final mfaDioResult = await repository.exchangeToken('valid_token');
        expect(mfaDioResult.isLeft(), isTrue);
        expect(
          mfaDioResult.getLeft().toNullable()!.errorCode,
          equals('MFA_REQUIRED'),
        );
        expect(repository.pendingMfaState?.isEnrollment, isTrue);

        // 4. DioException with RFC 7807 AppException payload
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(path: '/iam/auth/exchange'),
              statusCode: 403,
              data: const <String, Object?>{
                'type': 'https://api.quorum.fi/errors/tenant-suspended',
                'title': 'Tenant Suspended',
                'status': 403,
                'detail': 'Organization subscription is suspended.',
                'extensions': <String, Object?>{
                  'error_code': 'TENANT_SUSPENDED',
                },
              },
            ),
          ),
        );

        final rfcResult = await repository.exchangeToken('valid_token');
        expect(rfcResult.isLeft(), isTrue);
        expect(
          rfcResult.getLeft().toNullable()!.errorCode,
          equals('TENANT_SUSPENDED'),
        );

        // 5. revokeServerSession throws AppException.server on null payload
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/logout',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/logout'),
            data: null,
            statusCode: 200,
          ),
        );

        expect(
          () => repository.revokeServerSession(),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('SERVER_ERROR'),
            ),
          ),
        );

        // 6. Strict schema rejection when server returns non-32-hex user ID
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            data: buildExchangePayload(userId: 'usr_legacy16hex0000'),
            statusCode: 200,
          ),
        );

        final malformedResult = await repository.exchangeToken('valid_token');
        expect(malformedResult.isLeft(), isTrue);
        expect(
          malformedResult.getLeft().toNullable()!.errorCode,
          equals('UNKNOWN_ERROR'),
        );

        // Direct DTO deserialization throws CheckedFromJsonException on unrecognized keys
        expect(
          () => LogoutResponseDto.fromJson(const <String, Object?>{
            'status': 'revoked',
            'revoked_jti': 'jti_1',
            'all_sessions_revoked': false,
            'unexpected_field': true,
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'Positive 2 & Negative 3: authenticateForTaskOnboarding handles sign-in, user-not-found/invalid-credential sign-up, TOTP challenge/enrollment, and BVA',
      () async {
        final mockCredential = MockUserCredential();
        final mockUser = MockFirebaseUser();
        final mockMultiFactor = MockMultiFactor();
        final mockAssertion = MockMultiFactorAssertion();
        final mockSecret = MockTotpSecret();

        final customRepo = AuthRepository(
          mockFirebaseAuth,
          mockDio,
          signInAssertionBuilder: (enrollmentId, code) async => mockAssertion,
          enrollmentAssertionBuilder: (secret, code) async => mockAssertion,
        );

        // 1. Negative BVA: empty email or password < 6 chars returns VALIDATION_FAILED
        for (final badCase in <({String email, String password})>[
          (email: '', password: 'Password123!'),
          (email: '   ', password: 'Password123!'),
          (email: 'user@alpha.fi', password: ''),
          (email: 'user@alpha.fi', password: '12345'),
        ]) {
          final invalidRes = await customRepo.authenticateForTaskOnboarding(
            email: badCase.email,
            password: badCase.password,
          );
          expect(invalidRes.isLeft(), isTrue);
          expect(
            invalidRes.getLeft().toNullable()!.errorCode,
            equals('VALIDATION_FAILED'),
          );
        }

        // 2. Negative: null FirebaseAuth returns AUTHENTICATION_FAILED
        final nullAuthRepo = AuthRepository(null, mockDio);
        final nullRes = await nullAuthRepo.authenticateForTaskOnboarding(
          email: 'user@alpha.fi',
          password: 'Password123!',
        );
        expect(nullRes.isLeft(), isTrue);
        expect(
          nullRes.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        // 3. Positive: direct signInWithEmailAndPassword returns fresh ID token
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'existing@alpha.fi',
            password: 'Password123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(() => mockCredential.user).thenReturn(mockUser);
        when(
          () => mockUser.getIdToken(true),
        ).thenAnswer((_) async => 'signed_in_id_token');

        final signInRes = await customRepo.authenticateForTaskOnboarding(
          email: '  existing@alpha.fi  ',
          password: 'Password123!',
        );
        expect(signInRes.isRight(), isTrue);
        expect(signInRes.getRight().toNullable(), equals('signed_in_id_token'));

        // 4. Positive: 'invalid-credential' (enumeration protection) falls back to createUserWithEmailAndPassword
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'newbie@alpha.fi',
            password: 'Password123!',
          ),
        ).thenThrow(firebase.FirebaseAuthException(code: 'invalid-credential'));
        when(
          () => mockFirebaseAuth.createUserWithEmailAndPassword(
            email: 'newbie@alpha.fi',
            password: 'Password123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(
          () => mockUser.getIdToken(true),
        ).thenAnswer((_) async => 'created_user_id_token');

        final signUpRes = await customRepo.authenticateForTaskOnboarding(
          email: 'newbie@alpha.fi',
          password: 'Password123!',
        );
        expect(signUpRes.isRight(), isTrue);
        expect(
          signUpRes.getRight().toNullable(),
          equals('created_user_id_token'),
        );

        // 5. Negative: 'email-already-in-use' during fallback sign-up maps to AUTHENTICATION_FAILED
        when(
          () => mockFirebaseAuth.createUserWithEmailAndPassword(
            email: 'newbie@alpha.fi',
            password: 'WrongPassword!',
          ),
        ).thenThrow(
          firebase.FirebaseAuthException(code: 'email-already-in-use'),
        );
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'newbie@alpha.fi',
            password: 'WrongPassword!',
          ),
        ).thenThrow(firebase.FirebaseAuthException(code: 'invalid-credential'));

        final wrongPassRes = await customRepo.authenticateForTaskOnboarding(
          email: 'newbie@alpha.fi',
          password: 'WrongPassword!',
        );
        expect(wrongPassRes.isLeft(), isTrue);
        expect(
          wrongPassRes.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        // 6. Positive: prepareEnrollmentForCurrentUser(reloadUser: true) + enrollTotpAndGetIdToken
        when(() => mockFirebaseAuth.currentUser).thenReturn(mockUser);
        when(() => mockUser.reload()).thenAnswer((_) async {});
        when(() => mockUser.email).thenReturn('newbie@alpha.fi');
        when(() => mockUser.multiFactor).thenReturn(mockMultiFactor);
        when(
          () => mockMultiFactor.getSession(),
        ).thenThrow(Exception('Use fallback secret'));

        final prepRes = await customRepo.prepareEnrollmentForCurrentUser(
          fallbackEmail: 'newbie@alpha.fi',
          reloadUser: true,
        );
        expect(prepRes.isRight(), isTrue);
        verify(() => mockUser.reload()).called(1);

        // Bind a mock TotpSecret and complete enrollment via authenticateForTaskOnboarding
        customRepo.setPendingMfaState(
          MfaPendingState(
            type: MfaRequirementType.enrollment,
            email: 'newbie@alpha.fi',
            totpSecret: mockSecret,
            secretKey: 'BASE32SECRET',
          ),
        );
        when(
          () => mockMultiFactor.enroll(
            mockAssertion,
            displayName: any(named: 'displayName'),
          ),
        ).thenAnswer((_) async {});
        when(
          () => mockUser.getIdToken(true),
        ).thenAnswer((_) async => 'mfa_enrolled_id_token');

        final enrolledTokenRes = await customRepo.authenticateForTaskOnboarding(
          email: 'newbie@alpha.fi',
          password: 'Password123!',
          totpCode: '654321',
        );
        expect(enrolledTokenRes.isRight(), isTrue);
        expect(
          enrolledTokenRes.getRight().toNullable(),
          equals('mfa_enrolled_id_token'),
        );
        expect(customRepo.pendingMfaState, isNull);

        // 7. Positive: FirebaseAuthMultiFactorException challenge resolved with 6-digit totpCode
        final mockResolver = MockMultiFactorResolver();
        final mockHint = MockMultiFactorInfo();
        when(() => mockHint.uid).thenReturn('factor_uid_99');
        when(
          () => mockResolver.hints,
        ).thenReturn(<firebase.MultiFactorInfo>[mockHint]);
        when(
          () => mockResolver.resolveSignIn(mockAssertion),
        ).thenAnswer((_) async => mockCredential);
        when(
          () => mockUser.getIdToken(true),
        ).thenAnswer((_) async => 'mfa_challenged_id_token');

        final mockMfaException = MockFirebaseAuthMultiFactorException();
        when(() => mockMfaException.resolver).thenReturn(mockResolver);
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'mfa.user@alpha.fi',
            password: 'Password123!',
          ),
        ).thenThrow(mockMfaException);

        // Without totpCode -> returns MFA_CHALLENGE_REQUIRED
        final challengeNeeded = await customRepo.authenticateForTaskOnboarding(
          email: 'mfa.user@alpha.fi',
          password: 'Password123!',
        );
        expect(challengeNeeded.isLeft(), isTrue);
        expect(
          challengeNeeded.getLeft().toNullable()!.errorCode,
          equals('MFA_CHALLENGE_REQUIRED'),
        );

        // Subsequent call with 6-digit totpCode resolves challenge
        final challengeResolved = await customRepo
            .authenticateForTaskOnboarding(
              email: 'mfa.user@alpha.fi',
              password: 'Password123!',
              totpCode: '123456',
            );
        expect(challengeResolved.isRight(), isTrue);
        expect(
          challengeResolved.getRight().toNullable(),
          equals('mfa_challenged_id_token'),
        );

        // 8. Positive: resolveMfaChallenge and completeTotpEnrollment exchange upgraded tokens
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            data: buildExchangePayload(),
            statusCode: 200,
          ),
        );

        customRepo.setPendingMfaState(
          MfaPendingState(
            type: MfaRequirementType.challenge,
            email: 'mfa.user@alpha.fi',
            resolver: mockResolver,
            enrollmentId: 'factor_uid_99',
          ),
        );
        final resolvedDto = await customRepo.resolveMfaChallenge('123456');
        expect(resolvedDto.isRight(), isTrue);

        customRepo.setPendingMfaState(
          MfaPendingState(
            type: MfaRequirementType.enrollment,
            email: 'mfa.user@alpha.fi',
            totpSecret: mockSecret,
            secretKey: 'BASE32SECRET',
          ),
        );
        final completedDto = await customRepo.completeTotpEnrollment('654321');
        expect(completedDto.isRight(), isTrue);

        // 9. Negative: _mapDioException branches (404, 401, embedded AppException, null exchange payload)
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            data: null,
            statusCode: 200,
          ),
        );
        final nullPayloadRes = await customRepo.exchangeToken('tok');
        expect(
          nullPayloadRes.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        for (final status in <int>[404, 401, 500]) {
          when(
            () => mockDio.post<Map<String, Object?>>(
              '/iam/auth/exchange',
              data: any(named: 'data'),
            ),
          ).thenThrow(
            DioException(
              requestOptions: RequestOptions(path: '/iam/auth/exchange'),
              response: Response<Map<String, Object?>>(
                requestOptions: RequestOptions(path: '/iam/auth/exchange'),
                statusCode: status,
              ),
            ),
          );
          final statusRes = await customRepo.exchangeToken('tok');
          expect(statusRes.isLeft(), isTrue);
        }

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/auth/exchange',
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/exchange'),
            error: const AppException(
              status: 403,
              title: 'Forbidden',
              detail: 'Custom forbidden',
            ),
          ),
        );
        final embeddedRes = await customRepo.exchangeToken('tok');
        expect(embeddedRes.getLeft().toNullable()!.status, equals(403));

        // 10. Negative: authenticateForTaskOnboarding wrong-password & generic FirebaseAuthException
        for (final code in <String>['wrong-password', 'too-many-requests']) {
          when(
            () => mockFirebaseAuth.signInWithEmailAndPassword(
              email: 'err@alpha.fi',
              password: 'Password123!',
            ),
          ).thenThrow(firebase.FirebaseAuthException(code: code));
          final errRes = await customRepo.authenticateForTaskOnboarding(
            email: 'err@alpha.fi',
            password: 'Password123!',
          );
          expect(errRes.isLeft(), isTrue);
        }

        // 11. Provider instantiation and defensive guard branches across MFA/Session methods
        final container = ProviderContainer(
          overrides: [
            firebaseAuthInstanceProvider.overrideWithValue(mockFirebaseAuth),
            apiClientProvider.overrideWithValue(mockDio),
          ],
        );
        addTearDown(container.dispose);
        expect(container.read(authRepositoryProvider), isA<AuthRepository>());

        // signInWithEmailAndPassword: null user, null token, non-auth FirebaseAuthException, generic Exception
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'guard@alpha.fi',
            password: 'Password123!',
          ),
        ).thenAnswer((_) async => mockCredential);
        when(() => mockCredential.user).thenReturn(null);
        expect(
          (await customRepo.signInWithEmailAndPassword(
            'guard@alpha.fi',
            'Password123!',
          )).isLeft(),
          isTrue,
        );

        when(() => mockCredential.user).thenReturn(mockUser);
        when(() => mockUser.getIdToken(any())).thenAnswer((_) async => '');
        expect(
          (await customRepo.signInWithEmailAndPassword(
            'guard@alpha.fi',
            'Password123!',
          )).isLeft(),
          isTrue,
        );

        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'guard@alpha.fi',
            password: 'Password123!',
          ),
        ).thenThrow(firebase.FirebaseAuthException(code: 'too-many-requests'));
        expect(
          (await customRepo.signInWithEmailAndPassword(
            'guard@alpha.fi',
            'Password123!',
          )).isLeft(),
          isTrue,
        );

        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'guard@alpha.fi',
            password: 'Password123!',
          ),
        ).thenThrow(StateError('unexpected'));
        expect(
          (await customRepo.signInWithEmailAndPassword(
            'guard@alpha.fi',
            'Password123!',
          )).isLeft(),
          isTrue,
        );

        // resolveChallengeAndGetIdToken: null enrollmentId fallback, null user, empty token, exceptions
        customRepo.setPendingMfaState(
          MfaPendingState(
            type: MfaRequirementType.challenge,
            email: 'mfa.user@alpha.fi',
            resolver: mockResolver,
          ),
        );
        when(() => mockCredential.user).thenReturn(null);
        expect(
          (await customRepo.resolveChallengeAndGetIdToken('123456')).isLeft(),
          isTrue,
        );

        when(() => mockCredential.user).thenReturn(mockUser);
        when(() => mockUser.getIdToken(true)).thenAnswer((_) async => '');
        expect(
          (await customRepo.resolveChallengeAndGetIdToken('123456')).isLeft(),
          isTrue,
        );

        when(
          () => mockResolver.resolveSignIn(mockAssertion),
        ).thenThrow(firebase.FirebaseAuthException(code: 'invalid-verification-code'));
        expect(
          (await customRepo.resolveChallengeAndGetIdToken('123456')).isLeft(),
          isTrue,
        );

        when(
          () => mockResolver.resolveSignIn(mockAssertion),
        ).thenThrow(StateError('resolver failure'));
        expect(
          (await customRepo.resolveChallengeAndGetIdToken('123456')).isLeft(),
          isTrue,
        );

        // enrollTotpAndGetIdToken: empty token, null currentUser, FirebaseAuthException, generic Exception
        customRepo.setPendingMfaState(
          MfaPendingState(
            type: MfaRequirementType.enrollment,
            email: 'newbie@alpha.fi',
            totpSecret: mockSecret,
          ),
        );
        when(() => mockFirebaseAuth.currentUser).thenReturn(mockUser);
        when(() => mockUser.getIdToken(true)).thenAnswer((_) async => '');
        expect(
          (await customRepo.enrollTotpAndGetIdToken('654321')).isLeft(),
          isTrue,
        );

        when(() => mockFirebaseAuth.currentUser).thenReturn(null);
        expect(
          (await customRepo.enrollTotpAndGetIdToken('654321')).isLeft(),
          isTrue,
        );

        when(() => mockFirebaseAuth.currentUser).thenReturn(mockUser);
        when(
          () => mockMultiFactor.enroll(
            mockAssertion,
            displayName: any(named: 'displayName'),
          ),
        ).thenThrow(firebase.FirebaseAuthException(code: 'invalid-verification-code'));
        expect(
          (await customRepo.enrollTotpAndGetIdToken('654321')).isLeft(),
          isTrue,
        );

        when(
          () => mockMultiFactor.enroll(
            mockAssertion,
            displayName: any(named: 'displayName'),
          ),
        ).thenThrow(StateError('enroll crash'));
        expect(
          (await customRepo.enrollTotpAndGetIdToken('654321')).isLeft(),
          isTrue,
        );

        // authenticateForTaskOnboarding: immediate challenge resolution & refreshSession error branches
        customRepo.clearPendingMfaState();
        when(
          () => mockResolver.resolveSignIn(mockAssertion),
        ).thenAnswer((_) async => mockCredential);
        when(
          () => mockUser.getIdToken(true),
        ).thenAnswer((_) async => 'immediate_mfa_token');
        when(
          () => mockFirebaseAuth.signInWithEmailAndPassword(
            email: 'mfa.user@alpha.fi',
            password: 'Password123!',
          ),
        ).thenThrow(mockMfaException);

        final immediateRes = await customRepo.authenticateForTaskOnboarding(
          email: 'mfa.user@alpha.fi',
          password: 'Password123!',
          totpCode: '123456',
        );
        expect(immediateRes.getRight().toNullable(), equals('immediate_mfa_token'));

        when(() => mockUser.getIdToken(true)).thenAnswer((_) async => '');
        expect((await customRepo.refreshSession()).isLeft(), isTrue);
        when(() => mockUser.getIdToken(true)).thenThrow(StateError('token err'));
        expect((await customRepo.refreshSession()).isLeft(), isTrue);
      },
    );
  });
}
