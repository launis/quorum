import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **Authentication Interceptor**
///
/// Attaches the active 15-minute `Quorum Local JWT` (cached via `/iam/auth/exchange`
/// in `mockTokenProvider`) or falls back to the Firebase ID token when no local
/// session JWT has been cached yet.
class AuthInterceptor extends Interceptor {
  final Ref _ref;

  AuthInterceptor(this._ref);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Phase 6, Step 6.1: Attach exchanged Quorum Local JWT from session token store.
    final isExchangeRoute = options.path.endsWith('/iam/auth/exchange');
    final sessionJwt = _ref.read(mockTokenProvider);

    if (sessionJwt != null && sessionJwt.trim().isNotEmpty) {
      if (!isExchangeRoute) {
        options.headers['Authorization'] = 'Bearer ${sessionJwt.trim()}';
      }
      super.onRequest(options, handler);
      return;
    }

    final auth = _ref.read(firebaseAuthInstanceProvider);
    final user = auth.currentUser;

    if (user != null && !isExchangeRoute) {
      try {
        final token = await user.getIdToken();
        if (token == null || token.trim().isEmpty) {
          throw StateError('Firebase ID token resolved to null or empty.');
        }
        options.headers['Authorization'] = 'Bearer $token';
      } catch (e, stack) {
        // Token refresh failed - Fail-Fast, NEVER swallow silently
        final logger = _ref.read(loggerServiceProvider);
        logger.error('AUTH', 'Firebase token refresh failed', e, stack);

        handler.reject(
          DioException(
            requestOptions: options,
            type: DioExceptionType.cancel,
            error: AppException.unknown('Local authentication failed: $e'),
          ),
          true,
        );
        return;
      }
    }

    super.onRequest(options, handler);
  }
}
