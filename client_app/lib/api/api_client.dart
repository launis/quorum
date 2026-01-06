import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/api/auth_interceptor.dart';
import 'package:client_app/core/environment/env.dart';

part 'api_client.g.dart';

/// **API Client Provider**
///
/// Configures and exposes the [Dio] HTTP client used for all backend communications.
///
/// **Architecture Role**:
/// This is the central point for HTTP configuration. All Repositories MUST use this client
/// instead of creating their own Dio instances.
///
/// **Configuration**:
/// - **Base URL**: Sourced from [Env.apiUrl].
/// - **Headers**: Default content-type is `application/json`.
/// - **Security**: Automatically attaches [AuthInterceptor] to sign requests.
///
/// **Returns**:
/// A fully configured [Dio] instance ready for network requests.
@riverpod
Dio apiClient(Ref ref) {
  // Watch envProvider to rebuild client if config changes (unlikely in runtime, but good practice)
  ref.watch(envProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl:
          Env.apiUrl, // Accessing static getter directly as Env is a utility class
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  // Add Auth Interceptor
  dio.interceptors.add(AuthInterceptor(ref));

  return dio;
}
