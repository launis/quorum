// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'mock_user_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(MockUser)
final mockUserProvider = MockUserProvider._();

final class MockUserProvider extends $NotifierProvider<MockUser, User?> {
  MockUserProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'mockUserProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$mockUserHash();

  @$internal
  @override
  MockUser create() => MockUser();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(User? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<User?>(value),
    );
  }
}

String _$mockUserHash() => r'253018bf44199d649eeea77b5faa2c67a312d176';

abstract class _$MockUser extends $Notifier<User?> {
  User? build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<User?, User?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<User?, User?>,
              User?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
