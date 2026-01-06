import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';

/// **Authentication Interceptor**
///
/// This interceptor acts as the security bridge between the Flutter Client and the Python Backend.
/// It ensures that every outgoing HTTP request is authenticated with the current user's identity.
///
/// **Business Logic**:
/// 1.  Checks if a Firebase User is currently signed in.
/// 2.  Fetches a fresh **ID Token** (JWT) from Firebase Auth.
/// 3.  Injects this token into the `Authorization` header as a Bearer token.
///
/// **Failure Strategy**:
/// If token fetching fails, the request proceeds *without* the header. This allows public endpoints
/// to function, while protected endpoints will return `401 Unauthorized`.
///
/// **Usage**:
/// Automatically added to the [ApiClient] Dio instance.
class AuthInterceptor extends Interceptor {
  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      try {
        // Force refresh if needed to ensure we don't send expired tokens
        final token = await user.getIdToken();
        options.headers['Authorization'] = 'Bearer $token';
      } catch (e) {
        // Log locally or handle specific auth errors if needed.
        // Proceeding without header allows the backend to decide if 401 is needed.
      }
    }
    super.onRequest(options, handler);
  }
}
