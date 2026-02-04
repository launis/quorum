// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(modelRegistryRepository)
final modelRegistryRepositoryProvider = ModelRegistryRepositoryProvider._();

final class ModelRegistryRepositoryProvider
    extends
        $FunctionalProvider<
          ModelRegistryRepository,
          ModelRegistryRepository,
          ModelRegistryRepository
        >
    with $Provider<ModelRegistryRepository> {
  ModelRegistryRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'modelRegistryRepositoryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$modelRegistryRepositoryHash();

  @$internal
  @override
  $ProviderElement<ModelRegistryRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  ModelRegistryRepository create(Ref ref) {
    return modelRegistryRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ModelRegistryRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ModelRegistryRepository>(value),
    );
  }
}

String _$modelRegistryRepositoryHash() =>
    r'4eaa521bce22a3fe6385746206a68e766bd9834d';
