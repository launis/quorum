// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'api_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
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

@ProviderFor(apiClient)
final apiClientProvider = ApiClientProvider._();

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

final class ApiClientProvider extends $FunctionalProvider<Dio, Dio, Dio>
    with $Provider<Dio> {
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
  ApiClientProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'apiClientProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$apiClientHash();

  @$internal
  @override
  $ProviderElement<Dio> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  Dio create(Ref ref) {
    return apiClient(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Dio value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Dio>(value),
    );
  }
}

String _$apiClientHash() => r'2e460c65fb6709295d2e2dfa5f2e93be0a776ad8';
