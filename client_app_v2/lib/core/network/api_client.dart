import 'package:dio/dio.dart';
import 'package:client_app/core/network/interceptors/auth_interceptor.dart';
import 'package:client_app/core/network/interceptors/error_interceptor.dart';
import 'package:client_app/core/network/interceptors/dio_logger_interceptor.dart';
import 'package:client_app/core/network/interceptors/locale_interceptor.dart';
import 'package:client_app/core/environment/env.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'dart:isolate';
import 'dart:convert';

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
/// - **Error Handling**: [ErrorInterceptor] parses RFC 7807 responses to [AppException].
///
/// **Returns**:
/// A fully configured [Dio] instance ready for network requests.

/// Parses JSON in a background isolate to prevent UI thread blocking
dynamic _parseAndDecode(String response) {
  return jsonDecode(response);
}

Future<dynamic> _parseJson(String text) {
  return Isolate.run(() => _parseAndDecode(text));
}

class BackgroundTransformer extends SyncTransformer {
  BackgroundTransformer() : super(jsonDecodeCallback: _parseJson);
}

/// Centralized Network Timeouts
class ApiTimeouts {
  const ApiTimeouts._();

  /// Max time to establish a TCP connection with the server
  static const Duration connect = Duration(seconds: 15);

  /// Max time to wait for a response after connection (High for AI execution)
  static const Duration receive = Duration(seconds: 300);
}

@Riverpod(keepAlive: true)
Dio apiClient(Ref ref) {
  // Watch envProvider to rebuild client if config changes
  ref.watch(envProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl: '${Env.apiUrl}/api/v2/',
      connectTimeout: ApiTimeouts.connect,
      receiveTimeout: ApiTimeouts.receive,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, application/problem+json',
      },
    ),
  );

  // Set BackgroundTransformer for Isolate JSON parsing
  dio.transformer = BackgroundTransformer();

  // Add Auth Interceptor (must be first to add token)
  dio.interceptors.add(AuthInterceptor(ref));

  // Add Target Locale Interceptor (I18n fallback)
  dio.interceptors.add(TargetLocaleInterceptor());

  // Add Logger (before ErrorInterceptor to capture raw requests)
  dio.interceptors.add(DioLoggerInterceptor(ref));

  // Add Error Interceptor (parses RFC 7807 errors to AppException)
  dio.interceptors.add(ErrorInterceptor(ref));

  return dio;
}
