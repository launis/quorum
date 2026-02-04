// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'system_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(systemRepository)
final systemRepositoryProvider = SystemRepositoryProvider._();

final class SystemRepositoryProvider
    extends
        $FunctionalProvider<
          SystemRepository,
          SystemRepository,
          SystemRepository
        >
    with $Provider<SystemRepository> {
  SystemRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'systemRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$systemRepositoryHash();

  @$internal
  @override
  $ProviderElement<SystemRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  SystemRepository create(Ref ref) {
    return systemRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SystemRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SystemRepository>(value),
    );
  }
}

String _$systemRepositoryHash() => r'afe1bb6578ebed42fb645fd98e2f9b8f6cf8d64a';
