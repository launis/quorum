import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/api/auth_interceptor.dart';
import 'package:client_app/api/error_interceptor.dart';
import 'package:client_app/api/dio_logger_interceptor.dart';
import 'package:client_app/core/environment/env.dart';
import 'package:client_app/features/settings/locale_provider.dart';
import 'package:client_app/api/locale_interceptor.dart';

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

  final dio = Dio(
    BaseOptions(
      baseUrl: Env.apiUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 60),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, application/problem+json',
      },
    ),
  );

  // Add Auth Interceptor (must be first to add token)
  dio.interceptors.add(AuthInterceptor(ref));
  
  // Add Locale Interceptor (Dynamic Accept-Language)
  dio.interceptors.add(LocaleInterceptor(ref));
  
  // Add Logger (before ErrorInterceptor to capture raw requests)
  dio.interceptors.add(DioLoggerInterceptor(ref));

  // Add Error Interceptor (parses RFC 7807 errors to AppError)
  dio.interceptors.add(ErrorInterceptor(ref));

  return dio;
}
