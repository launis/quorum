// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'mock_auth_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Mock Token Provider**
///
/// Stores the 'fake' JWT token when running in Debug/Mock mode without Firebase.
/// This allows the [AuthInterceptor] to sign requests with `mock-token:uid`.

@ProviderFor(MockToken)
final mockTokenProvider = MockTokenProvider._();

/// **Mock Token Provider**
///
/// Stores the 'fake' JWT token when running in Debug/Mock mode without Firebase.
/// This allows the [AuthInterceptor] to sign requests with `mock-token:uid`.
final class MockTokenProvider extends $NotifierProvider<MockToken, String?> {
  /// **Mock Token Provider**
  ///
  /// Stores the 'fake' JWT token when running in Debug/Mock mode without Firebase.
  /// This allows the [AuthInterceptor] to sign requests with `mock-token:uid`.
  MockTokenProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'mockTokenProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$mockTokenHash();

  @$internal
  @override
  MockToken create() => MockToken();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(String? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<String?>(value),
    );
  }
}

String _$mockTokenHash() => r'fec63cc7ce6a9b0d175e1b59384af303dbf42ad8';

/// **Mock Token Provider**
///
/// Stores the 'fake' JWT token when running in Debug/Mock mode without Firebase.
/// This allows the [AuthInterceptor] to sign requests with `mock-token:uid`.

abstract class _$MockToken extends $Notifier<String?> {
  String? build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<String?, String?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<String?, String?>,
              String?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
