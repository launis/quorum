// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller managing the Model Registry strictly using strict representations.
/// Implements Optimistic UI principles where possible.

@ProviderFor(ModelRegistryController)
final modelRegistryControllerProvider = ModelRegistryControllerProvider._();

/// Controller managing the Model Registry strictly using strict representations.
/// Implements Optimistic UI principles where possible.
final class ModelRegistryControllerProvider
    extends $AsyncNotifierProvider<ModelRegistryController, List<ModelConfig>> {
  /// Controller managing the Model Registry strictly using strict representations.
  /// Implements Optimistic UI principles where possible.
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
    r'1014a3fde13a32bfc279f4686b9d54a57499b600';

/// Controller managing the Model Registry strictly using strict representations.
/// Implements Optimistic UI principles where possible.

abstract class _$ModelRegistryController
    extends $AsyncNotifier<List<ModelConfig>> {
  FutureOr<List<ModelConfig>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<ModelConfig>>, List<ModelConfig>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<ModelConfig>>, List<ModelConfig>>,
              AsyncValue<List<ModelConfig>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Fetches a single System Config natively by ID

@ProviderFor(modelRegistryById)
final modelRegistryByIdProvider = ModelRegistryByIdFamily._();

/// Fetches a single System Config natively by ID

final class ModelRegistryByIdProvider
    extends
        $FunctionalProvider<
          AsyncValue<ModelConfig>,
          ModelConfig,
          FutureOr<ModelConfig>
        >
    with $FutureModifier<ModelConfig>, $FutureProvider<ModelConfig> {
  /// Fetches a single System Config natively by ID
  ModelRegistryByIdProvider._({
    required ModelRegistryByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'modelRegistryByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$modelRegistryByIdHash();

  @override
  String toString() {
    return r'modelRegistryByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<ModelConfig> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ModelConfig> create(Ref ref) {
    final argument = this.argument as String;
    return modelRegistryById(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ModelRegistryByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$modelRegistryByIdHash() => r'067d118916579f82d8d390703c42ed6ad8bdd552';

/// Fetches a single System Config natively by ID

final class ModelRegistryByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<ModelConfig>, String> {
  ModelRegistryByIdFamily._()
    : super(
        retry: null,
        name: r'modelRegistryByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches a single System Config natively by ID

  ModelRegistryByIdProvider call(String id) =>
      ModelRegistryByIdProvider._(argument: id, from: this);

  @override
  String toString() => r'modelRegistryByIdProvider';
}

/// Fetches the list of available models from the backend.

@ProviderFor(availableModels)
final availableModelsProvider = AvailableModelsProvider._();

/// Fetches the list of available models from the backend.

final class AvailableModelsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<String>>,
          List<String>,
          FutureOr<List<String>>
        >
    with $FutureModifier<List<String>>, $FutureProvider<List<String>> {
  /// Fetches the list of available models from the backend.
  AvailableModelsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableModelsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableModelsHash();

  @$internal
  @override
  $FutureProviderElement<List<String>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<String>> create(Ref ref) {
    return availableModels(ref);
  }
}

String _$availableModelsHash() => r'956bc100e67bb3b7af43cd19d9b02b5c3ad1dd2d';

@ProviderFor(ModelRegistryForm)
final modelRegistryFormProvider = ModelRegistryFormFamily._();

final class ModelRegistryFormProvider
    extends $AsyncNotifierProvider<ModelRegistryForm, ModelConfig> {
  ModelRegistryFormProvider._({
    required ModelRegistryFormFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'modelRegistryFormProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$modelRegistryFormHash();

  @override
  String toString() {
    return r'modelRegistryFormProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  ModelRegistryForm create() => ModelRegistryForm();

  @override
  bool operator ==(Object other) {
    return other is ModelRegistryFormProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$modelRegistryFormHash() => r'1e207c022b3287898931f91e8c30ed6c961da8b6';

final class ModelRegistryFormFamily extends $Family
    with
        $ClassFamilyOverride<
          ModelRegistryForm,
          AsyncValue<ModelConfig>,
          ModelConfig,
          FutureOr<ModelConfig>,
          String
        > {
  ModelRegistryFormFamily._()
    : super(
        retry: null,
        name: r'modelRegistryFormProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  ModelRegistryFormProvider call(String configId) =>
      ModelRegistryFormProvider._(argument: configId, from: this);

  @override
  String toString() => r'modelRegistryFormProvider';
}

abstract class _$ModelRegistryForm extends $AsyncNotifier<ModelConfig> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<ModelConfig> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<ModelConfig>, ModelConfig>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ModelConfig>, ModelConfig>,
              AsyncValue<ModelConfig>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
