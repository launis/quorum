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

/// Fetches the list of available models from the backend filtered by platform and location.

@ProviderFor(availableModels)
final availableModelsProvider = AvailableModelsFamily._();

/// Fetches the list of available models from the backend filtered by platform and location.

final class AvailableModelsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<String>>,
          List<String>,
          FutureOr<List<String>>
        >
    with $FutureModifier<List<String>>, $FutureProvider<List<String>> {
  /// Fetches the list of available models from the backend filtered by platform and location.
  AvailableModelsProvider._({
    required AvailableModelsFamily super.from,
    required ({String? platform, String? location}) super.argument,
  }) : super(
         retry: null,
         name: r'availableModelsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$availableModelsHash();

  @override
  String toString() {
    return r'availableModelsProvider'
        ''
        '$argument';
  }

  @$internal
  @override
  $FutureProviderElement<List<String>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<String>> create(Ref ref) {
    final argument = this.argument as ({String? platform, String? location});
    return availableModels(
      ref,
      platform: argument.platform,
      location: argument.location,
    );
  }

  @override
  bool operator ==(Object other) {
    return other is AvailableModelsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$availableModelsHash() => r'1c7d3a1fe06a00cfa6d87c59dfcf5ec2d82aad99';

/// Fetches the list of available models from the backend filtered by platform and location.

final class AvailableModelsFamily extends $Family
    with
        $FunctionalFamilyOverride<
          FutureOr<List<String>>,
          ({String? platform, String? location})
        > {
  AvailableModelsFamily._()
    : super(
        retry: null,
        name: r'availableModelsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches the list of available models from the backend filtered by platform and location.

  AvailableModelsProvider call({String? platform, String? location}) =>
      AvailableModelsProvider._(
        argument: (platform: platform, location: location),
        from: this,
      );

  @override
  String toString() => r'availableModelsProvider';
}

/// Fetches supported GCP Vertex AI locations.

@ProviderFor(supportedLocations)
final supportedLocationsProvider = SupportedLocationsProvider._();

/// Fetches supported GCP Vertex AI locations.

final class SupportedLocationsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Map<String, dynamic>>>,
          List<Map<String, dynamic>>,
          FutureOr<List<Map<String, dynamic>>>
        >
    with
        $FutureModifier<List<Map<String, dynamic>>>,
        $FutureProvider<List<Map<String, dynamic>>> {
  /// Fetches supported GCP Vertex AI locations.
  SupportedLocationsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'supportedLocationsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$supportedLocationsHash();

  @$internal
  @override
  $FutureProviderElement<List<Map<String, dynamic>>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Map<String, dynamic>>> create(Ref ref) {
    return supportedLocations(ref);
  }
}

String _$supportedLocationsHash() =>
    r'75c69997bf538d1b4d8813bb1ef83c5d407d953f';

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
