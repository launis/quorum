// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'available_components_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Available Components Controller**
///
/// Manages the list of available text components (Prompts) using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).

@ProviderFor(AvailableComponentsController)
final availableComponentsControllerProvider =
    AvailableComponentsControllerProvider._();

/// **Available Components Controller**
///
/// Manages the list of available text components (Prompts) using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).
final class AvailableComponentsControllerProvider
    extends
        $AsyncNotifierProvider<
          AvailableComponentsController,
          List<StudioComponentDef>
        > {
  /// **Available Components Controller**
  ///
  /// Manages the list of available text components (Prompts) using the modern
  /// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).
  AvailableComponentsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableComponentsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableComponentsControllerHash();

  @$internal
  @override
  AvailableComponentsController create() => AvailableComponentsController();
}

String _$availableComponentsControllerHash() =>
    r'e5526331520bc1fd4b3d2b4313fa0a64a9a90b0d';

/// **Available Components Controller**
///
/// Manages the list of available text components (Prompts) using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).

abstract class _$AvailableComponentsController
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
