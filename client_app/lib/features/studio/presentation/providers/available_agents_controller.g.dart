// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'available_agents_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(AvailableAgentsController)
final availableAgentsControllerProvider = AvailableAgentsControllerProvider._();

final class AvailableAgentsControllerProvider
    extends
        $AsyncNotifierProvider<
          AvailableAgentsController,
          List<StudioComponentDef>
        > {
  AvailableAgentsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableAgentsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableAgentsControllerHash();

  @$internal
  @override
  AvailableAgentsController create() => AvailableAgentsController();
}

String _$availableAgentsControllerHash() =>
    r'6535a7c11b732d28c07d337e6b3214693482ec5a';

abstract class _$AvailableAgentsController
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
