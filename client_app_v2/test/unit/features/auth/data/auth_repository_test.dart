import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
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
  });
}
