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
    extends
        $AsyncNotifierProvider<ModelRegistryController, ModelRegistryState> {
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
}

String _$modelRegistryControllerHash() =>
    r'e6b2b516deca074aa2f248f822fbb341d9d3137c';

abstract class _$ModelRegistryController
    extends $AsyncNotifier<ModelRegistryState> {
  FutureOr<ModelRegistryState> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<ModelRegistryState>, ModelRegistryState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ModelRegistryState>, ModelRegistryState>,
              AsyncValue<ModelRegistryState>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
