// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ModelRegistryController)
final modelRegistryControllerProvider = ModelRegistryControllerProvider._();

final class ModelRegistryControllerProvider
    extends $NotifierProvider<ModelRegistryController, ModelRegistryState> {
  ModelRegistryControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'modelRegistryControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$modelRegistryControllerHash();

  @$internal
  @override
  ModelRegistryController create() => ModelRegistryController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ModelRegistryState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ModelRegistryState>(value),
    );
  }
}

String _$modelRegistryControllerHash() =>
    r'c4a41e9a69a0638f2fd10fa8b3deb407df08dbf0';

abstract class _$ModelRegistryController extends $Notifier<ModelRegistryState> {
  ModelRegistryState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ModelRegistryState, ModelRegistryState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ModelRegistryState, ModelRegistryState>,
              ModelRegistryState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
