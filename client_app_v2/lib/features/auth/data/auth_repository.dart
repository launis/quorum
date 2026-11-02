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

// Phase 6, Step 6.1: @Riverpod(keepAlive: true) AuthRepository, 2FA Enrollment/Challenge, and Token Exchange.

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
  MfaPendingState? _pendingMfaState;

  AuthRepository(this._firebaseAuth, this._client);

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
        await _prepareEnrollmentForCurrentUser(
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

      // Mandatory First-Time 2FA Enrollment check when user has zero enrolled second factors.
      final enrolledFactors = await firebaseUser.multiFactor
          .getEnrolledFactors();
      if (enrolledFactors.isEmpty) {
        await _prepareEnrollmentForUser(firebaseUser, fallbackEmail: email);
        return const Left(
          AppException(
            status: 403,
            title: 'MFA Enrollment Required',
            detail: 'Mandatory TOTP 2FA enrollment is required.',
            extensions: {'error_code': 'MFA_REQUIRED'},
          ),
        );
      }

      final idToken = await firebaseUser.getIdToken();
      if (idToken == null || idToken.trim().isEmpty) {
        return Left(AppException.unauthorized());
      }

      return await exchangeToken(idToken);
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

  /// Completes a 2FA TOTP challenge using the captured [firebase.MultiFactorResolver] and exchanges the token.
  Future<Either<AppException, TokenExchangeResponseDto>> resolveMfaChallenge(
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
      final assertion =
          await firebase.TotpMultiFactorGenerator.getAssertionForSignIn(
            factorUid,
            trimmedCode,
          );
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
      return await exchangeToken(idToken);
    } on firebase.FirebaseAuthException {
      return Left(AppException.unauthorized());
    } on DioException catch (e) {
      return Left(_mapDioException(e));
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Completes mandatory first-time TOTP 2FA enrollment and exchanges the upgraded token.
  Future<Either<AppException, TokenExchangeResponseDto>> completeTotpEnrollment(
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
        final assertion =
            await firebase.TotpMultiFactorGenerator.getAssertionForEnrollment(
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
        return await exchangeToken(idToken);
      }
      return Left(AppException.unauthorized());
    } on firebase.FirebaseAuthException {
      return Left(AppException.unauthorized());
    } on DioException catch (e) {
      return Left(_mapDioException(e));
    } catch (e) {
      return Left(AppException.unknown(e));
    }
  }

  /// Exchanges a developer `target_user_id` at `POST /api/v2/iam/auth/exchange` for a signed Quorum Local JWT.
  Future<Either<AppException, TokenExchangeResponseDto>>
  debugSignInWithMockToken(String targetUserId) async {
    final trimmedId = targetUserId.trim();
    if (trimmedId.isEmpty) {
      return Left(
        AppException.validation('Target User ID is required for debug login.'),
      );
    }
    return exchangeWithPayload(
      TokenExchangeRequestDto(targetUserId: trimmedId),
    );
  }

  /// Performs a silent background token exchange using the current Firebase session or debug `targetUserId`.
  Future<Either<AppException, TokenExchangeResponseDto>> refreshSession({
    String? debugTargetUserId,
  }) async {
    if (debugTargetUserId != null && debugTargetUserId.trim().isNotEmpty) {
      return debugSignInWithMockToken(debugTargetUserId.trim());
    }
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

  Future<void> _prepareEnrollmentForCurrentUser({
    required String fallbackEmail,
  }) async {
    final firebaseUser = _firebaseAuth?.currentUser;
    if (firebaseUser != null) {
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
