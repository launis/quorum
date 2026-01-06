import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **Authentication Interceptor**
///
/// This interceptor acts as the security bridge between the Flutter Client and the Python Backend.
/// It ensures that every outgoing HTTP request is authenticated with the current user's identity.
class AuthInterceptor extends Interceptor {
  final Ref _ref;

  AuthInterceptor(this._ref);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final user = FirebaseAuth.instance.currentUser;

    // 1. Try Firebase Auth
    if (user != null) {
      try {
        final token = await user.getIdToken();
        options.headers['Authorization'] = 'Bearer $token';
      } catch (e) {
        // Fallback or ignore
      }
    } else {
      // 2. Try Mock Token (Hybrid/Dev Mode)
      final mockToken = _ref.read(mockTokenProvider);
      if (mockToken != null) {
        options.headers['Authorization'] = 'Bearer $mockToken';
      }
    }

    super.onRequest(options, handler);
  }
}
