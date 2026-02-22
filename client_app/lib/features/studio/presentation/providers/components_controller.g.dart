// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'components_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ComponentsController)
final componentsControllerProvider = ComponentsControllerProvider._();

final class ComponentsControllerProvider
    extends
        $AsyncNotifierProvider<ComponentsController, List<StudioComponentDef>> {
  ComponentsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'componentsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$componentsControllerHash();

  @$internal
  @override
  ComponentsController create() => ComponentsController();
}

String _$componentsControllerHash() =>
    r'b230ff3eaf943b277502813b77f64322717e2040';

abstract class _$ComponentsController
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
