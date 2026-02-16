// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ingestion_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(IngestionController)
final ingestionControllerProvider = IngestionControllerProvider._();

final class IngestionControllerProvider
    extends
        $NotifierProvider<IngestionController, AsyncValue<IngestionStatus?>> {
  IngestionControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'ingestionControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$ingestionControllerHash();

  @$internal
  @override
  IngestionController create() => IngestionController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AsyncValue<IngestionStatus?> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AsyncValue<IngestionStatus?>>(value),
    );
  }
}

String _$ingestionControllerHash() =>
    r'910491d0c00d4ace00e743043ef7a8a6d80d5659';

abstract class _$IngestionController
    extends $Notifier<AsyncValue<IngestionStatus?>> {
  AsyncValue<IngestionStatus?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<IngestionStatus?>, AsyncValue<IngestionStatus?>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<IngestionStatus?>,
                AsyncValue<IngestionStatus?>
              >,
              AsyncValue<IngestionStatus?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

@ProviderFor(knowledgeStrategies)
final knowledgeStrategiesProvider = KnowledgeStrategiesProvider._();

final class KnowledgeStrategiesProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<KnowledgeModelStrategy>>,
          List<KnowledgeModelStrategy>,
          FutureOr<List<KnowledgeModelStrategy>>
        >
    with
        $FutureModifier<List<KnowledgeModelStrategy>>,
        $FutureProvider<List<KnowledgeModelStrategy>> {
  KnowledgeStrategiesProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'knowledgeStrategiesProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$knowledgeStrategiesHash();

  @$internal
  @override
  $FutureProviderElement<List<KnowledgeModelStrategy>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<KnowledgeModelStrategy>> create(Ref ref) {
    return knowledgeStrategies(ref);
  }
}

String _$knowledgeStrategiesHash() =>
    r'e61550585da078b55a64f4c747a402cc9f66f95a';
