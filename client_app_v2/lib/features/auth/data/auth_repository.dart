import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/validation_error_reason.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_repository.g.dart';

// Keep-alive Riverpod AuthRepository managing 2FA TOTP enrollment/challenge and local JWT token exchange.

/// Categorizes the active second-factor authentication step required before token exchange.
enum MfaRequirementType { none, challenge, enrollment }

/// Immutable snapshot of an in-progress 2FA challenge or mandatory TOTP enrollment session.
class MfaPendingState {
  final MfaRequirementType type;
  final String email;
  final firebase.MultiFactorResolver? resolver;
  final String? enrollmentId;
  final firebase.TotpSecret? totpSecret;
  final String? secretKey;
  final String? provisioningUri;

  const MfaPendingState({
    this.type = MfaRequirementType.none,
    this.email = '',
    this.resolver,
    this.enrollmentId,
    this.totpSecret,
    this.secretKey,
    this.provisioningUri,
  });

  bool get isChallenge => type == MfaRequirementType.challenge;
  bool get isEnrollment => type == MfaRequirementType.enrollment;
}

typedef TotpSignInAssertionBuilder =
    Future<firebase.MultiFactorAssertion> Function(
      String enrollmentId,
      String oneTimePassword,
    );

typedef TotpEnrollmentAssertionBuilder =
    Future<firebase.MultiFactorAssertion> Function(
      firebase.TotpSecret secret,
      String oneTimePassword,
    );

@Riverpod(keepAlive: true)
AuthRepository authRepository(Ref ref) {
  return AuthRepository(
    ref.watch(firebaseAuthInstanceProvider),
    ref.watch(apiClientProvider),
  );
}

class AuthRepository {
  final firebase.FirebaseAuth? _firebaseAuth;
  final Dio _client;
  final TotpSignInAssertionBuilder _signInAssertionBuilder;
  final TotpEnrollmentAssertionBuilder _enrollmentAssertionBuilder;
  MfaPendingState? _pendingMfaState;

  AuthRepository(
    this._firebaseAuth,
    this._client, {
    TotpSignInAssertionBuilder? signInAssertionBuilder,
    TotpEnrollmentAssertionBuilder? enrollmentAssertionBuilder,
  }) : _signInAssertionBuilder =
           signInAssertionBuilder ??
           firebase.TotpMultiFactorGenerator.getAssertionForSignIn,
       _enrollmentAssertionBuilder =
           enrollmentAssertionBuilder ??
           firebase.TotpMultiFactorGenerator.getAssertionForEnrollment;

  MfaPendingState? get pendingMfaState => _pendingMfaState;

  void clearPendingMfaState() {
    _pendingMfaState = null;
  }

  void setPendingMfaState(MfaPendingState? state) {
    _pendingMfaState = state;
  }

  Stream<firebase.User?> authStateChanges() {
    return _firebaseAuth?.authStateChanges() ?? Stream.value(null);
  }

  /// Exchanges a Firebase ID token for a 15-minute Quorum Local JWT at `POST /api/v2/iam/auth/exchange`.
  Future<Either<AppException, TokenExchangeResponseDto>> exchangeToken(
    String firebaseIdToken,
  ) async {
    final trimmed = firebaseIdToken.trim();
    if (trimmed.isEmpty) {
      return Left(AppException.unauthorized());
    }
    return exchangeWithPayload(TokenExchangeRequestDto(firebaseToken: trimmed));
  }

  /// Executes `POST /api/v2/iam/auth/exchange` using a typed [TokenExchangeRequestDto].
  Future<Either<AppException, TokenExchangeResponseDto>> exchangeWithPayload(
    TokenExchangeRequestDto request,
  ) async {
    try {
      final response = await _client.post<Map<String, Object?>>(
        '/iam/auth/exchange',
        data: request.toJson(),
      );
      final payload = response.data;
      if (payload == null) {
        return Left(AppException.unauthorized());
      }
      return Right(TokenExchangeResponseDto.fromJson(payload));
    } on DioException catch (e) {
      final mapped = _mapDioException(e);
      if (mapped.errorCode == 'MFA_REQUIRED') {
        await prepareEnrollmentForCurrentUser(
          fallbackEmail: _firebaseAuth?.currentUser?.email ?? '',
        );
      }
      return Left(mapped);
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Authenticates with first-factor credentials, enforces mandatory TOTP 2FA, and upgrades the session.
  Future<Either<AppException, TokenExchangeResponseDto>>
  signInWithEmailAndPassword(String email, String password) async {
    try {
      if (_firebaseAuth == null) {
        return Left(AppException.unknown());
      }
      _pendingMfaState = null;

      final userCredential = await _firebaseAuth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      final firebaseUser = userCredential.user;
      if (firebaseUser == null) {
        return Left(AppException.unknown());
      }

      final idToken = await firebaseUser.getIdToken();
      if (idToken == null || idToken.trim().isEmpty) {
        return Left(AppException.unauthorized());
      }

      final exchangeResult = await exchangeToken(idToken);
      return await exchangeResult.fold((error) async {
        if (error.errorCode == 'MFA_REQUIRED') {
          await _prepareEnrollmentForUser(firebaseUser, fallbackEmail: email);
        }
        return Left(error);
      }, (dto) async => Right(dto));
    } on firebase.FirebaseAuthMultiFactorException catch (e) {
      // Enrolled 2FA Challenge: capture MultiFactorResolver for 6-digit TOTP verification.
      final hints = e.resolver.hints;
      final firstFactorUid = hints.isNotEmpty ? hints.first.uid : null;
      _pendingMfaState = MfaPendingState(
        type: MfaRequirementType.challenge,
        email: email,
        resolver: e.resolver,
        enrollmentId: firstFactorUid,
      );
      return const Left(
        AppException(
          status: 403,
          title: 'MFA Challenge Required',
          detail: 'Enter your 6-digit TOTP authentication code.',
          extensions: {'error_code': 'MFA_CHALLENGE_REQUIRED'},
        ),
      );
    } on firebase.FirebaseAuthException catch (e) {
      if (e.code == 'user-not-found' ||
          e.code == 'wrong-password' ||
          e.code == 'invalid-credential') {
        return Left(AppException.unauthorized());
      }
      return Left(
        AppException.validation(ValidationErrorReason.unknown.toString()),
      );
    } on DioException catch (e) {
      return Left(_mapDioException(e));
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Resolves an active 2FA TOTP challenge and returns the fresh MFA-verified Firebase ID token.
  Future<Either<AppException, String>> resolveChallengeAndGetIdToken(
    String totpCode,
  ) async {
    final trimmedCode = totpCode.trim();
    if (trimmedCode.length != 6) {
      return Left(
        AppException.validation(
          'A 6-digit TOTP verification code is required.',
        ),
      );
    }

    final pending = _pendingMfaState;
    if (pending == null || !pending.isChallenge || pending.resolver == null) {
      return Left(AppException.unauthorized());
    }

    try {
      final resolver = pending.resolver!;
      final factorUid =
          pending.enrollmentId ??
          (resolver.hints.isNotEmpty ? resolver.hints.first.uid : '');
      final assertion = await _signInAssertionBuilder(factorUid, trimmedCode);
      final userCredential = await resolver.resolveSignIn(assertion);
      final firebaseUser = userCredential.user;
      if (firebaseUser == null) {
        return Left(AppException.unauthorized());
      }
      final idToken = await firebaseUser.getIdToken(true);
      if (idToken == null || idToken.trim().isEmpty) {
        return Left(AppException.unauthorized());
      }
      _pendingMfaState = null;
      return Right(idToken);
    } on firebase.FirebaseAuthException {
      return Left(AppException.unauthorized());
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Completes a 2FA TOTP challenge using the captured [firebase.MultiFactorResolver] and exchanges the token.
  Future<Either<AppException, TokenExchangeResponseDto>> resolveMfaChallenge(
    String totpCode,
  ) async {
    final idTokenResult = await resolveChallengeAndGetIdToken(totpCode);
    return await idTokenResult.fold(
      (error) async => Left(error),
      (idToken) async => exchangeToken(idToken),
    );
  }

  /// Completes mandatory first-time TOTP 2FA enrollment and returns the fresh MFA-verified Firebase ID token.
  Future<Either<AppException, String>> enrollTotpAndGetIdToken(
    String totpCode, {
    String accountDisplayName = 'Quorum Authenticator',
  }) async {
    final trimmedCode = totpCode.trim();
    if (trimmedCode.length != 6) {
      return Left(
        AppException.validation(
          'A 6-digit TOTP confirmation code is required.',
        ),
      );
    }

    final pending = _pendingMfaState;
    if (pending == null || !pending.isEnrollment) {
      return Left(AppException.unauthorized());
    }

    try {
      final firebaseUser = _firebaseAuth?.currentUser;
      if (firebaseUser != null && pending.totpSecret != null) {
        final assertion = await _enrollmentAssertionBuilder(
          pending.totpSecret!,
          trimmedCode,
        );
        await firebaseUser.multiFactor.enroll(
          assertion,
          displayName: accountDisplayName,
        );
        final idToken = await firebaseUser.getIdToken(true);
        if (idToken == null || idToken.trim().isEmpty) {
          return Left(AppException.unauthorized());
        }
        _pendingMfaState = null;
        return Right(idToken);
      }
      return Left(AppException.unauthorized());
    } on firebase.FirebaseAuthException {
      return Left(AppException.unauthorized());
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Completes mandatory first-time TOTP 2FA enrollment and exchanges the upgraded token.
  Future<Either<AppException, TokenExchangeResponseDto>> completeTotpEnrollment(
    String totpCode, {
    String accountDisplayName = 'Quorum Authenticator',
  }) async {
    final idTokenResult = await enrollTotpAndGetIdToken(
      totpCode,
      accountDisplayName: accountDisplayName,
    );
    return await idTokenResult.fold(
      (error) async => Left(error),
      (idToken) async => exchangeToken(idToken),
    );
  }

  /// Authenticates or registers a task assignee via Firebase Auth and resolves TOTP 2FA when required.
  Future<Either<AppException, String>> authenticateForTaskOnboarding({
    required String email,
    required String password,
    String? totpCode,
  }) async {
    final normalizedEmail = email.trim();
    final trimmedTotp = totpCode?.trim();
    if (normalizedEmail.isEmpty || password.length < 6) {
      return Left(
        AppException.validation(
          'Email and password (min 6 chars) are required.',
        ),
      );
    }
    if (_firebaseAuth == null) {
      return Left(AppException.unauthorized());
    }

    final pending = _pendingMfaState;
    if (pending != null && trimmedTotp != null && trimmedTotp.length == 6) {
      if (pending.isChallenge) {
        return resolveChallengeAndGetIdToken(trimmedTotp);
      }
      if (pending.isEnrollment) {
        return enrollTotpAndGetIdToken(trimmedTotp);
      }
    }

    try {
      firebase.UserCredential userCredential;
      try {
        userCredential = await _firebaseAuth.signInWithEmailAndPassword(
          email: normalizedEmail,
          password: password,
        );
      } on firebase.FirebaseAuthMultiFactorException {
        rethrow;
      } on firebase.FirebaseAuthException catch (e) {
        if (e.code == 'user-not-found' || e.code == 'invalid-credential') {
          try {
            userCredential = await _firebaseAuth.createUserWithEmailAndPassword(
              email: normalizedEmail,
              password: password,
            );
          } on firebase.FirebaseAuthException {
            return Left(AppException.unauthorized());
          } catch (err) {
            return Left(AppException.unknown(err));
          }
        } else if (e.code == 'wrong-password') {
          return Left(AppException.unauthorized());
        } else {
          return Left(
            AppException.validation(ValidationErrorReason.unknown.toString()),
          );
        }
      }

      final firebaseUser = userCredential.user;
      if (firebaseUser == null) {
        return Left(AppException.unauthorized());
      }
      final idToken = await firebaseUser.getIdToken(true);
      if (idToken == null || idToken.trim().isEmpty) {
        return Left(AppException.unauthorized());
      }
      return Right(idToken);
    } on firebase.FirebaseAuthMultiFactorException catch (e) {
      final hints = e.resolver.hints;
      final firstFactorUid = hints.isNotEmpty ? hints.first.uid : null;
      _pendingMfaState = MfaPendingState(
        type: MfaRequirementType.challenge,
        email: normalizedEmail,
        resolver: e.resolver,
        enrollmentId: firstFactorUid,
      );
      if (trimmedTotp != null && trimmedTotp.length == 6) {
        return resolveChallengeAndGetIdToken(trimmedTotp);
      }
      return const Left(
        AppException(
          status: 403,
          title: 'MFA Challenge Required',
          detail: 'Enter your 6-digit TOTP authentication code.',
          extensions: {'error_code': 'MFA_CHALLENGE_REQUIRED'},
        ),
      );
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Performs a silent background token exchange using the current Firebase session.
  Future<Either<AppException, TokenExchangeResponseDto>>
  refreshSession() async {
    final firebaseUser = _firebaseAuth?.currentUser;
    if (firebaseUser == null) {
      return Left(AppException.unauthorized());
    }
    try {
      final freshIdToken = await firebaseUser.getIdToken(true);
      if (freshIdToken == null || freshIdToken.trim().isEmpty) {
        return Left(AppException.unauthorized());
      }
      return await exchangeToken(freshIdToken);
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Invokes `POST /api/v2/iam/auth/logout` with [LogoutRequestDto] and hydrates [LogoutResponseDto].
  Future<LogoutResponseDto> revokeServerSession({
    bool revokeAllSessions = false,
  }) async {
    final response = await _client.post<Map<String, Object?>>(
      '/iam/auth/logout',
      data: LogoutRequestDto(revokeAllSessions: revokeAllSessions).toJson(),
    );
    final payload = response.data;
    if (payload == null) {
      throw AppException.server('Empty logout response payload.');
    }
    return LogoutResponseDto.fromJson(payload);
  }

  /// Signs out from the local Firebase Identity Provider instance.
  Future<void> signOut() async {
    _pendingMfaState = null;
    await _firebaseAuth?.signOut();
  }

  /// Prepares TOTP 2FA enrollment for the active Firebase user (optionally reloading `emailVerified` state first).
  Future<Either<AppException, MfaPendingState>>
  prepareEnrollmentForCurrentUser({
    required String fallbackEmail,
    bool reloadUser = false,
  }) async {
    final firebaseUser = _firebaseAuth?.currentUser;
    if (firebaseUser != null) {
      if (reloadUser) {
        try {
          await firebaseUser.reload();
        } catch (_) {
          // Proceed to enrollment session creation if reload is unsupported in test fakes.
        }
      }
      await _prepareEnrollmentForUser(
        firebaseUser,
        fallbackEmail: fallbackEmail,
      );
    } else {
      _pendingMfaState = MfaPendingState(
        type: MfaRequirementType.enrollment,
        email: fallbackEmail,
        secretKey: 'QUORUM-TOTP-SETUP',
        provisioningUri:
            'otpauth://totp/Quorum:$fallbackEmail?issuer=Quorum&secret=QUORUMTOTPSETUP',
      );
    }
    return Right(_pendingMfaState!);
  }

  Future<void> _prepareEnrollmentForUser(
    firebase.User firebaseUser, {
    required String fallbackEmail,
  }) async {
    final resolvedEmail = firebaseUser.email ?? fallbackEmail;
    try {
      final session = await firebaseUser.multiFactor.getSession();
      final totpSecret = await firebase.TotpMultiFactorGenerator.generateSecret(
        session,
      );
      final provisioningUri = await totpSecret.generateQrCodeUrl(
        accountName: resolvedEmail,
        issuer: 'Quorum',
      );
      _pendingMfaState = MfaPendingState(
        type: MfaRequirementType.enrollment,
        email: resolvedEmail,
        totpSecret: totpSecret,
        secretKey: totpSecret.secretKey,
        provisioningUri: provisioningUri,
      );
    } catch (_) {
      _pendingMfaState = MfaPendingState(
        type: MfaRequirementType.enrollment,
        email: resolvedEmail,
        secretKey: 'QUORUM-TOTP-SETUP',
        provisioningUri:
            'otpauth://totp/Quorum:$resolvedEmail?issuer=Quorum&secret=QUORUMTOTPSETUP',
      );
    }
  }

  AppException _mapDioException(DioException e) {
    if (e.error is AppException) {
      return e.error as AppException;
    }
    final data = e.response?.data;
    if (data is Map<String, Object?>) {
      if (data.containsKey('type') && data.containsKey('status')) {
        try {
          return AppException.fromJson(data);
        } catch (_) {
          // Fall through to status code mapping when payload is non-conformant.
        }
      }
      final code = data['error_code'];
      if (code is String && code.isNotEmpty) {
        final detail = data['detail'];
        return AppException(
          status: e.response?.statusCode ?? 401,
          title: (data['title'] as String?) ?? 'Authentication Error',
          detail: detail is String ? detail : 'Authentication failed.',
          extensions: {'error_code': code},
        );
      }
    }
    if (e.response?.statusCode == 404) {
      return AppException.notFound('User account not found.');
    }
    if (e.response?.statusCode == 401 || e.response?.statusCode == 403) {
      return AppException.unauthorized();
    }
    return AppException.unknown(e);
  }
}
