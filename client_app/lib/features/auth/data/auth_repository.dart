import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase;
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_repository.g.dart';

@riverpod
AuthRepository authRepository(Ref ref) {
  return AuthRepository(
    firebase.FirebaseAuth.instance,
    ref.watch(apiClientProvider),
  );
}

class AuthRepository {
  final firebase.FirebaseAuth _firebaseAuth;
  final Dio _client;

  AuthRepository(this._firebaseAuth, this._client);

  Stream<firebase.User?> authStateChanges() => _firebaseAuth.authStateChanges();

  Future<User> signInWithEmailAndPassword(String email, String password) async {
    try {
      // 1. Authenticate with Firebase
      final userCredential = await _firebaseAuth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      final firebaseUser = userCredential.user;
      if (firebaseUser == null) {
        throw Exception('Firebase Sign-In failed: User is null');
      }

      // 2. Get Token
      final token = await firebaseUser.getIdToken();

      // 3. Verify with Backend to get full profile (Role, OrgID)
      final response = await _client.post<Map<String, dynamic>>(
        '/auth/verify',
        data: {'token': token},
      );

      if (response.data == null || response.data!['user'] == null) {
        throw Exception('Backend verification failed: No data');
      }

      // 4. Return Hydrated User
      return User.fromJson(response.data!['user'] as Map<String, dynamic>);
    } on firebase.FirebaseAuthException catch (e) {
      throw Exception('Login Failed: ${e.message}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw Exception('User account not found on backend. Contact Support.');
      }
      throw Exception('Server Error: ${e.message}');
    } catch (e) {
      throw Exception('Authentication Error: $e');
    }
  }

  /// **Debug Only**: Bypasses Firebase and authenticates directly with Backend Mock Token.
  Future<User> debugSignInWithMockToken(String uid) async {
    // 1. Verify with Backend (using special mock-token prefix logic)
    final response = await _client.post<Map<String, dynamic>>(
      '/auth/verify',
      data: {'token': 'mock-token:$uid'},
    );

    if (response.data == null || response.data!['user'] == null) {
      throw Exception('Mock Verification Failed');
    }

    // 2. Return Hydrated User
    // Note: We don't have a Firebase User, so the calls to `authStateChanges` stream
    // won't fire. The Controller must handle this manually or we create a fake internal session.
    // For Phase 2, we will just return the User and let the Controller manage state.
    return User.fromJson(response.data!['user'] as Map<String, dynamic>);
  }

  Future<void> signOut() async {
    await _firebaseAuth.signOut();
  }
}
