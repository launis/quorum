// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller managing the Model Registry strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

@ProviderFor(ModelRegistryController)
final modelRegistryControllerProvider = ModelRegistryControllerProvider._();

/// Controller managing the Model Registry strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
final class ModelRegistryControllerProvider
    extends
        $AsyncNotifierProvider<
          ModelRegistryController,
          List<Map<String, dynamic>>
        > {
  /// Controller managing the Model Registry strictly using `Map<String, dynamic>`.
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
    r'7c331a49b019070cb79d79c2863ca6de7f536e13';

/// Controller managing the Model Registry strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

abstract class _$ModelRegistryController
    extends $AsyncNotifier<List<Map<String, dynamic>>> {
  FutureOr<List<Map<String, dynamic>>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<Map<String, dynamic>>>,
              List<Map<String, dynamic>>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<Map<String, dynamic>>>,
                List<Map<String, dynamic>>
              >,
              AsyncValue<List<Map<String, dynamic>>>,
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
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>
        >
    with
        $FutureModifier<Map<String, dynamic>>,
        $FutureProvider<Map<String, dynamic>> {
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
  $FutureProviderElement<Map<String, dynamic>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Map<String, dynamic>> create(Ref ref) {
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

String _$modelRegistryByIdHash() => r'a74d2a8788fc9962a43a0f856e1cf8f32cc15d90';

/// Fetches a single System Config natively by ID

final class ModelRegistryByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Map<String, dynamic>>, String> {
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
    extends $AsyncNotifierProvider<ModelRegistryForm, Map<String, dynamic>> {
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

String _$modelRegistryFormHash() => r'f92d73bea7c4a6fdadd3c4e7abf473706a2dfafb';

final class ModelRegistryFormFamily extends $Family
    with
        $ClassFamilyOverride<
          ModelRegistryForm,
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>,
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

abstract class _$ModelRegistryForm
    extends $AsyncNotifier<Map<String, dynamic>> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<Map<String, dynamic>> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<Map<String, dynamic>>, Map<String, dynamic>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Map<String, dynamic>>,
                Map<String, dynamic>
              >,
              AsyncValue<Map<String, dynamic>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
