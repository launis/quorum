import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/api/auth_interceptor.dart';
import 'package:client_app/api/error_interceptor.dart';
import 'package:client_app/core/environment/env.dart';
import 'package:client_app/features/settings/locale_provider.dart';

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
/// - **Accept**: Includes `application/problem+json` for RFC 7807 errors.
/// - **Security**: Automatically attaches [AuthInterceptor] to sign requests.
/// - **Error Handling**: [ErrorInterceptor] parses RFC 7807 responses to [AppError].
///
/// **Returns**:
/// A fully configured [Dio] instance ready for network requests.
@Riverpod(keepAlive: true)
Dio apiClient(Ref ref) {
  // Watch envProvider to rebuild client if config changes
  ref.watch(envProvider);

  // Watch localeProvider to inject correct Accept-Language header
  final locale = ref.watch(localeProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl: Env.apiUrl,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, application/problem+json',
        'Accept-Language': locale.languageCode,
      },
    ),
  );

  // Add Auth Interceptor (must be first to add token)
  dio.interceptors.add(AuthInterceptor(ref));

  // Add Error Interceptor (parses RFC 7807 errors to AppError)
  dio.interceptors.add(ErrorInterceptor());

  return dio;
}
