import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:dio/dio.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';

/// **Authentication Interceptor**
///
/// This interceptor acts as the security bridge between the Flutter Client and the Python Backend.
/// It ensures that every outgoing HTTP request is authenticated with the current user's identity.
///
/// **NOTE**: Token availability is ensured by providers (e.g., workflowListProvider)
/// waiting for auth state before making API calls.
class AuthInterceptor extends Interceptor {
  final Ref _ref;

  AuthInterceptor(this._ref);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // 1. Try Firebase Auth (synchronous read - providers ensure auth is ready)
    final auth = _ref.read(firebaseAuthInstanceProvider);
    final user = auth?.currentUser;

    if (user != null) {
      try {
        final token = await user.getIdToken();
        options.headers['Authorization'] = 'Bearer $token';
      } catch (e) {
        // Token refresh failed - continue without auth
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
