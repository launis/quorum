import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/validation_error_reason.dart';
import 'package:fpdart/fpdart.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    ref.watch(firebaseAuthInstanceProvider),
    ref.watch(apiClientProvider),
  );
});

class AuthRepository {
  final firebase.FirebaseAuth? _firebaseAuth;
  final Dio _client;

  AuthRepository(this._firebaseAuth, this._client);

  Stream<firebase.User?> authStateChanges() {
    return _firebaseAuth?.authStateChanges() ?? Stream.value(null);
  }

  Future<Either<AppException, User>> signInWithEmailAndPassword(
    String email,
    String password,
  ) async {
    try {
      if (_firebaseAuth == null) {
        return Left(AppException.unknown());
      }
      // 1. Authenticate with Firebase
      final userCredential = await _firebaseAuth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      final firebaseUser = userCredential.user;
      if (firebaseUser == null) {
        return Left(AppException.unknown());
      }

      // 2. Get Token
      final token = await firebaseUser.getIdToken();

      // 3. Verify with Backend to get full profile (Role, OrgID)
      final response = await _client.post<Map<String, dynamic>>(
        '/iam/auth/verify',
        data: {'token': token},
      );

      if (response.data == null || response.data!['user'] == null) {
        return Left(AppException(detail: ''));
      }

      // 4. Return Hydrated User
      return Right(
        User.fromJson(response.data!['user'] as Map<String, dynamic>),
      );
    } on firebase.FirebaseAuthException catch (e) {
      if (e.code == 'user-not-found' || e.code == 'wrong-password') {
        return Left(AppException.unauthorized());
      }
      // Strict Localization: Map generic Auth failure to unknown validation error
      return Left(
        AppException.validation(ValidationErrorReason.unknown.toString()),
      );
    } on DioException catch (e) {
      if (e.response != null && e.response!.data != null) {
        final data = e.response!.data;
        if (data is Map<String, dynamic> && data.containsKey('error_code')) {
          final code = data['error_code'] as String?;

          // Strict Mapping of Backend Error Codes
          if (code == 'HTTP_401' || code == 'AUTH_FAILED') {
            return Left(AppException.unauthorized());
          }
          if (code == 'HTTP_404') {
            return Left(AppException.notFound(''));
          }
          // Default to generic server error without dynamic message
          return const Left(AppException(detail: ''));
        }
      }

      if (e.response?.statusCode == 404) {
        return Left(AppException.notFound(''));
      }
      if (e.response?.statusCode == 401) {
        return Left(AppException.unauthorized());
      }

      return Left(AppException(detail: ''));
    } catch (e) {
      return Left(AppException.unknown());
    }
  }

  /// **Debug Only**: Bypasses Firebase and authenticates directly with Backend Mock Token.
  /// **Debug Only**: Bypasses Firebase and authenticates directly with Backend Mock Token.
  Future<Either<AppException, User>> debugSignInWithMockToken(String id) async {
    try {
      // 1. Verify with Backend (using special mock-token prefix logic)
      final response = await _client.post<Map<String, dynamic>>(
        '/iam/auth/verify',
        data: {'token': 'mock-token:$id'},
      );

      if (response.data == null || response.data!['user'] == null) {
        return Left(AppException(detail: ''));
      }

      // 2. Return Hydrated User
      // Note: We don't have a Firebase User, so the calls to `authStateChanges` stream
      // won't fire. The Controller must handle this manually or we create a fake internal session.
      // For Phase 2, we will just return the User and let the Controller manage state.
      return Right(
        User.fromJson(response.data!['user'] as Map<String, dynamic>),
      );
    } catch (e) {
      // DEBUG: Return raw error to UI
      return Left(AppException(detail: "Debug Login Failed: $e"));
    }
  }

  Future<void> signOut() async {
    await _firebaseAuth?.signOut();
  }
}
