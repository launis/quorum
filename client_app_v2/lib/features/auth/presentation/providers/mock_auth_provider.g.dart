// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'mock_auth_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(MockToken)
final mockTokenProvider = MockTokenProvider._();

final class MockTokenProvider extends $NotifierProvider<MockToken, String?> {
  MockTokenProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'mockTokenProvider',
        isAutoDispose: false,
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

String _$mockTokenHash() => r'5fe51b63ec6731376a488629e6e09dde3c60be10';

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
