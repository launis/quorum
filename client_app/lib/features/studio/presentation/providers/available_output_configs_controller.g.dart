// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'available_output_configs_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(AvailableOutputConfigsController)
final availableOutputConfigsControllerProvider =
    AvailableOutputConfigsControllerProvider._();

final class AvailableOutputConfigsControllerProvider
    extends
        $AsyncNotifierProvider<
          AvailableOutputConfigsController,
          List<StudioComponentDef>
        > {
  AvailableOutputConfigsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableOutputConfigsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableOutputConfigsControllerHash();

  @$internal
  @override
  AvailableOutputConfigsController create() =>
      AvailableOutputConfigsController();
}

String _$availableOutputConfigsControllerHash() =>
    r'a1722a8f8b875400c12a73fb577eb9ebff6a7569';

abstract class _$AvailableOutputConfigsController
    extends $AsyncNotifier<List<StudioComponentDef>> {
  FutureOr<List<StudioComponentDef>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<StudioComponentDef>>,
              List<StudioComponentDef>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<StudioComponentDef>>,
                List<StudioComponentDef>
              >,
              AsyncValue<List<StudioComponentDef>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
