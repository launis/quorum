// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(usageRepository)
final usageRepositoryProvider = UsageRepositoryProvider._();

final class UsageRepositoryProvider
    extends
        $FunctionalProvider<UsageRepository, UsageRepository, UsageRepository>
    with $Provider<UsageRepository> {
  UsageRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'usageRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$usageRepositoryHash();

  @$internal
  @override
  $ProviderElement<UsageRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  UsageRepository create(Ref ref) {
    return usageRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(UsageRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<UsageRepository>(value),
    );
  }
}

String _$usageRepositoryHash() => r'1f7b1764712d6280c545057350e565cf5b98d003';
